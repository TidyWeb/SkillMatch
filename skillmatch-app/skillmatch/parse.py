"""Parse an advert into requirement statements and facts, keeping the evidence sentence for each.

Rules, not models. The heading and phrase lists come from the live Reed sample studied in
docs/advert_patterns.md. Every classification records its confidence: "stated" when a heading or
cue word says so, "inferred" when we guessed from a skill mention.
"""

from __future__ import annotations

import html as htmllib
import re
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, NavigableString, Tag

from skillmatch.taxonomy import Taxonomy, get_taxonomy
from skillmatch.text import clean_text

# ---------------------------------------------------------------------------------------------
# 1. HTML -> lines
# ---------------------------------------------------------------------------------------------

BLOCK_TAGS = {"p", "div", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "table", "tr", "section"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
# Benefit/company/apply headings that some adverts run into the previous sentence.
GLUED_HEADS = r"(What['’]s On Offer\??|What We Offer|Why Join Us\??|The Benefits|Benefits:|About Us:?|How to Apply:?|What You['’]ll Get(?: In Return)?\??)"
GLUED_HEADING = re.compile(r"(?<=[a-z0-9.)])\s+(?=" + GLUED_HEADS + r"(?:\s|$))")
CONNECTOR_END = r"\b(and|or|of|to|the|a|an|in|for|with|using|by|from|across|within|into|on|at|as|including|such as|&)$|[,&-]$"
# Benefit/company/apply headings that some adverts run into the previous sentence.
GLUED_HEADS = r"(What['’]s On Offer\??|What We Offer|Why Join Us\??|The Benefits|Benefits:|About Us:?|How to Apply:?|What You['’]ll Get(?: In Return)?\??)"
GLUED_HEADING = re.compile(r"(?<=[a-z0-9.)])\s+(?=" + GLUED_HEADS + r"(?:\s|$))")
CONNECTOR_END = r"\b(and|or|of|to|the|a|an|in|for|with|using|by|from|across|within|into|on|at|as|including|such as|&)$|[,&-]$"
BULLET_RE = re.compile(r"^\s*(?:[*•·●▪◦‣–-]|\d+[.)])\s+")
TRAILING_BULLET_RE = re.compile(r"\s*[·•]\s*$")


@dataclass
class Line:
    text: str
    kind: str  # heading | item | para
    bold: bool = False


def _norm_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def html_to_lines(html: str | None) -> list[Line]:
    """Turn advert HTML into headings, list items and paragraphs.

    Treats <br> as a line break, <li> and text bullets (*, •, ·, -) as items, decodes double
    escaped HTML (Greenhouse), and re-joins sentences that agencies hard-wrap across lines.
    """
    html = clean_text(html)
    if not html:
        return []
    if "&lt;" in html and "<" not in html.replace("&lt;", ""):
        html = htmllib.unescape(html)
    soup = BeautifulSoup(html, "html.parser")
    raw: list[Line] = []
    buf: list[str] = []
    state = {"bold_only": True, "kind": "para"}

    def flush(kind: str):
        text = _norm_space("".join(buf))
        if text:
            raw.append(Line(text, kind, bold=state["bold_only"]))
        buf.clear()
        state["bold_only"] = True

    def walk(node: Tag, kind: str, bold: bool):
        for ch in node.children:
            if isinstance(ch, NavigableString):
                s = str(ch)
                if s.strip():
                    buf.append(s)
                    if not bold:
                        state["bold_only"] = False
                elif buf:
                    buf.append(" ")
                continue
            if not isinstance(ch, Tag):
                continue
            name = ch.name.lower()
            if name in ("script", "style"):
                continue
            if name == "br":
                flush(kind)
            elif name == "li":
                flush(kind)
                walk(ch, "item", bold)
                flush("item")
            elif name in HEADING_TAGS:
                flush(kind)
                walk(ch, "heading", True)
                flush("heading")
            elif name in BLOCK_TAGS:
                flush(kind)
                walk(ch, kind, bold)
                flush(kind)
            else:
                walk(ch, kind, bold or name in ("strong", "b"))

    walk(soup, "para", False)
    flush("para")

    expanded: list[Line] = []
    for ln in raw:
        m = GLUED_HEADING.search(ln.text)
        if m and ln.text[: m.start()].strip():
            # "…a specialist area What's On Offer?" -> the line, then a heading line.
            expanded.append(Line(ln.text[: m.start()].strip(), ln.kind, ln.bold))
            rest = ln.text[m.end() :].strip()
            head = re.match(GLUED_HEADS, rest).group(0)
            expanded.append(Line(head, "heading", True))
            if rest[len(head) :].strip():
                expanded.append(Line(rest[len(head) :].strip(), "para", False))
        else:
            expanded.append(ln)
    raw = expanded
    lines: list[Line] = []
    for ln in raw:
        text = TRAILING_BULLET_RE.sub("", ln.text)
        kind = ln.kind
        if BULLET_RE.match(text) and kind != "heading":
            text = BULLET_RE.sub("", text, count=1)
            kind = "item"
        text = text.strip(" ·•")
        if not text:
            continue
        prev = lines[-1] if lines else None
        # Re-join hard-wrapped lines: the previous line has no terminal punctuation and this
        # one starts in lower case, or the previous line ends mid-phrase ("using SQL, Power BI
        # and"), or it is a text-bullet item continued on a plain line.
        unfinished = prev is not None and not re.search(r"[.!?:;]$", prev.text)
        if (
            prev
            and unfinished
            and prev.kind != "heading"
            and kind not in ("heading", "item")
            and not _looks_like_heading(prev)
            and (
                re.match(r"^[a-z(&,]", text)
                or re.search(CONNECTOR_END, prev.text, re.I)
                or (
                    prev.kind == "item"
                    and kind == "para"
                    and ln.kind == "para"
                    and not ln.bold
                    and len(text.split()) <= 12
                    and not KNOWN_HEADING_WORDS.match(text.lower().strip(" :?"))
                )
            )
        ):
            prev.text = f"{prev.text} {text}"
            continue
        lines.append(Line(text, kind, ln.bold and kind != "item"))
    return lines


# ---------------------------------------------------------------------------------------------
# 2. Sections
# ---------------------------------------------------------------------------------------------

SECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "desirable",
        re.compile(
            r"(desirabl|nice to have|nice-to-have|bonus points|preferred (skills|experience|qualifications)|"
            r"\bideally\b|it would be (great|beneficial|nice|an advantage)|would also be advantageous|"
            r"advantageous|additional skills|would be a plus|plus points)"
        ),
    ),
    (
        "benefits",
        re.compile(
            r"(benefit|on offer|offer to you|in it for you|in return|why join|why work|perks|"
            r"^package|reward|what we offer|what they offer|job offer|our offer|salary|"
            r"what you('ll| will) get|why (apply|this role))"
        ),
    ),
    (
        "apply",
        re.compile(
            r"(how to apply|^apply|interested\b|next steps|what you need to do now|"
            r"recruitment process|interview|closing date|what now|your application)"
        ),
    ),
    (
        "essential",
        re.compile(
            r"(essential|requirement|about you|looking for|what you('ll| will) need|what will you need|"
            r"you('ll| will) (need|have|bring|possess)|what you('ll| will) bring|"
            r"skills (and|&) (experience|requirements|qualifications)|experience (and|&) (skills|qualifications)|"
            r"your (skills|experience|profile)|the person|person specification|ideal candidate|"
            r"candidate (profile|requirements)|to be successful|knowledge,? skills|key skills|"
            r"^qualifications|^profile$|mandatory|must have|who you are|what we need|"
            r"technical experience|skills required|successful candidate|competenc|^skills\b|got it|we want it|"
            r"\brequired\b|^experience\b|^knowledge\b|^qualifications\b|^key skills|"
            r"what you have|you have:|"
            r"^experience$|criteria)"
        ),
    ),
    (
        "duties",
        re.compile(
            r"(responsibilit|what you('ll| will) (be )?do|what will you be doing|the role|about the role|"
            r"role overview|job (description|overview|purpose|summary|introduction)|duties|"
            r"day[- ]to[- ]day|your (new )?role|main (purpose|tasks)|key tasks|the job|the position|"
            r"what the role involves|the opportunity|^description$|^summary$|^overview$|your day)"
        ),
    ),
    (
        "company",
        re.compile(
            r"(^about\b|the company|our client|client details|who we are|the team|our values|"
            r"working at|your new company|company description|our (story|mission|culture))"
        ),
    ),
]
KNOWN_HEADING_WORDS = re.compile(
    r"^(key responsibilities|responsibilities|the role|about the role|about you|requirements|"
    r"desirable|essential|benefits|duties|profile|description|the person|job offer|"
    r"what we're looking for|what we are looking for|what you'll do|skills|experience|"
    r"qualifications|the company|client details|summary|overview)$"
)


def section_of(heading: str) -> str:
    h = heading.lower().replace("&amp;", "&").strip(" :?-–")
    h = re.sub(r"^.{0,80}? [-–] (?=what )", "", h)  # "BI Analyst - What will you need?"
    for name, pat in SECTION_PATTERNS:
        if pat.search(h):
            return name
    return "other"


def _looks_like_heading(line: Line) -> bool:
    text = line.text.strip()
    words = text.split()
    if line.kind == "heading":
        return True
    if line.kind == "item" or not words or len(words) > 12:
        return False
    plain = text.lower().strip(" :?")
    if text.endswith(":") and len(words) <= 14:
        return True
    if text.endswith("?") and len(words) <= 10:
        return True
    if KNOWN_HEADING_WORDS.match(plain):
        return True
    return line.bold and len(words) <= 8 and not text.endswith(".")


# ---------------------------------------------------------------------------------------------
# 3. Statement classification
# ---------------------------------------------------------------------------------------------

DESIRABLE_TERMINAL = re.compile(
    r"(would be (a |an )?(real |big |huge |great |highly |very )?(advantage|advantageous|desirable|"
    r"beneficial|plus|bonus|helpful|useful|nice|welcome)|"
    r"\bis (highly |also )?(desirable|advantageous|preferred|preferable|beneficial|a plus|an advantage)|"
    r"\bhighly desirable|\bdesirable\b|\badvantageous\b|nice to have|\bpreferabl[ey]\b|"
    r"\bpreferred\b|\bis a (big |real )?plus|\b(is|be) a (real |big )?bonus|bonus points|^bonus\b|not essential|would be great)",
    re.IGNORECASE,
)
IDEALLY = re.compile(r"\b(ideally|preferably)\b", re.IGNORECASE)
ESSENTIAL_CUE = re.compile(
    r"\b(must|essential|required|you will have|you'll have|you will need|"
    r"you'll need|you need|you should have|proven|demonstrable|demonstrated|mandatory|"
    r"it is essential|need to have|we require|you will possess|you'll possess|you will bring|"
    r"you'll bring)\b",
    re.IGNORECASE,
)
DUTY_CUE = re.compile(
    r"\b(you will be responsible|you'll be responsible|responsible for|duties (include|will include)|"
    r"day[- ]to[- ]day|the role (involves|includes)|your role will|you will be (working|supporting|"
    r"producing|managing|leading|developing|delivering|building|maintaining|analysing|joining)|"
    r"you'll be (working|supporting|producing|managing|leading|developing|delivering|building|"
    r"maintaining|analysing|joining)|you will (support|produce|manage|lead|develop|deliver|build|"
    r"maintain|analyse|work|join|play|oversee|own|report)|you'll (support|produce|manage|lead|"
    r"develop|deliver|build|maintain|analyse|work|join|play|oversee|own|report))\b",
    re.IGNORECASE,
)
SKILL_ASK = re.compile(
    r"\b(experience (of|in|with|using|working)|knowledge of|proficien|familiar|understanding of|"
    r"skills in|skilled in|ability to|able to|competent|confident (in|with|using)|"
    r"working knowledge|good|strong|excellent|advanced|solid|expert)\b",
    re.IGNORECASE,
)
BOILERPLATE = re.compile(
    r"(employment (agency|business)|equal opportunit|right to work|privacy|reasonable adjustment|"
    r"disability confident|diversity|inclusive|welcome(s)? applications|apply (now|today)|"
    r"send (your|us your) cv|your cv|by applying|not hear back|unsuccessful on this occasion|"
    r"visa sponsorship|^keywords?\b|synonyms|you may have experience in the following|"
    r"if you('ve| have) also worked|click apply|recruitment business|we are committed to|"
    r"proud to (be|specialise)|registered (charity|in england)|values? (diversity|difference)|"
    r"encouraged to apply|(are |is )?welcome to apply|we encourage applications|"
    r"would suit someone|this role would suit|we('d| would) love to hear|preferred name|"
    r"use it to apply|an opportunity to build your|if you thrive|if you are passionate|benefits package|"
    r"competitive salary|salary range|base salary|we offer|company laptop|career development and progression)",
    re.IGNORECASE,
)

YEARS_EXPERIENCE_CUE = re.compile(
    r"\b(\d+|one|two|three|four|five|six|several)\s*\+?\s*(?:(?:-|–|to)\s*\d+\s*)?years?['’]?\s+(?:of\s+)?(?:\w+\s+){0,2}experience",
    re.IGNORECASE,
)
ESSENTIAL, DESIRABLE, DUTY, OTHER = "essential", "desirable", "duty", "other"
STATED, INFERRED = "stated", "inferred"


def classify_statement(
    text: str, section: str, has_tags: bool, is_item: bool = True
) -> tuple[str, str]:
    """Return (strength, confidence) for one statement inside a section."""
    if BOILERPLATE.search(text) or section in ("benefits", "company", "apply"):
        return OTHER, STATED
    ess = ESSENTIAL_CUE.search(text) or YEARS_EXPERIENCE_CUE.search(text)
    ideal = IDEALLY.search(text)
    unbracketed = re.sub(r"\([^)]*\)", "", text)  # "(2:1 or above preferred)" qualifies a detail
    if DESIRABLE_TERMINAL.search(unbracketed) and not re.search(
        r"\bnot (desirable|preferred)", unbracketed, re.I
    ):
        return DESIRABLE, STATED
    if ideal and (not ess or ideal.start() < ess.start()):
        return DESIRABLE, STATED
    if section in ("essential", "desirable") and not is_item and not has_tags and not ess:
        # A closing paragraph after a list ("Career changers welcome…") is not a requirement.
        return OTHER, INFERRED
    if section == "desirable":
        return DESIRABLE, STATED
    if section == "essential":
        if DUTY_CUE.search(text) and not ess:
            return DUTY, STATED
        return ESSENTIAL, STATED
    if section == "duties":
        if ess and not DUTY_CUE.search(text):
            return ESSENTIAL, STATED
        return DUTY, STATED
    if section in ("benefits", "company", "apply"):
        return OTHER, STATED
    # No helpful heading: rely on the sentence itself.
    if ess or DEGREE_RE.search(text):
        return ESSENTIAL, STATED
    if DUTY_CUE.search(text):
        return DUTY, STATED
    if has_tags and SKILL_ASK.search(text):
        return ESSENTIAL, INFERRED
    return OTHER, INFERRED


# ---------------------------------------------------------------------------------------------
# 4. Facts: data-experience demand, entry signals, degree, arrangement, salary
# ---------------------------------------------------------------------------------------------

NUM_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "a couple of": 2, "a few": 2, "several": 3, "a number of": 2,
}  # fmt: skip
NUM = r"(\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|nine|ten|a couple of|a few|several)"
YEARS_RE = re.compile(
    rf"(?:(?P<months>\d+)\s*months?\s*(?:-|–|to)\s*)?"
    rf"(?:at least|minimum of|a minimum of|min\.?|over|more than)?\s*"
    rf"(?P<n>{NUM})\s*\+?\s*(?:(?:-|–|to)\s*(?P<m>{NUM})\s*\+?\s*)?(?:years?|yrs?)['’]?",
    re.IGNORECASE,
)
DATA_ANCHOR = re.compile(
    r"\b(data|analyst|analytics|analytical|bi|business intelligence|mi|management information|"
    r"reporting|insight|sql|python|power ?bi|tableau|statistic\w*|dashboard\w*|etl)\b",
    re.IGNORECASE,
)
NOT_EXPERIENCE = re.compile(
    r"(service|established|founded|history|fixed[- ]term|contract|holiday|leave|old\b|ago\b|"
    r"for over|for more than \d+ years we|post[- ]qualifi)",
    re.IGNORECASE,
)
IMPLIED_ROLE = re.compile(
    r"\bexperience\s+(?:working\s+)?(?:as|in|within)\s+(?:a|an)?\s*(?:[\w/&-]+\s+){0,3}?"
    r"(?:data|bi|business intelligence|mi|reporting|insight|analytics|analyst)\b[\w/ -]{0,30}?"
    r"\b(analyst|role|position|developer|function|team|engineer|specialist|capacity)\b",
    re.IGNORECASE,
)

ENTRY_SIGNALS: list[tuple[str, re.Pattern]] = [
    ("junior", re.compile(r"\bjunior\b", re.I)),
    ("graduate", re.compile(r"\bgraduates?\b", re.I)),
    ("trainee", re.compile(r"\btrainee\b", re.I)),
    ("apprentice", re.compile(r"\bapprentice(ship)?\b", re.I)),
    ("assistant", re.compile(r"\bassistant\b", re.I)),
    ("entry level", re.compile(r"\bentry[- ]level\b", re.I)),
    ("associate", re.compile(r"\bassociate\b", re.I)),
    (
        "no experience necessary",
        re.compile(r"\bno (previous |prior )?(\w+ )?experience (is )?(necessary|needed|required)", re.I),
    ),
    ("training provided", re.compile(r"\b(full )?training (will be |is )?provided|we will train|full training\b", re.I)),
    ("career changers welcome", re.compile(r"\bcareer[- ]changers?\b", re.I)),
    ("transferable skills valued", re.compile(r"\btransferable (skills|experience)", re.I)),
    ("first step into a career", re.compile(r"\bfirst step\b", re.I)),
    ("or equivalent experience", re.compile(r"\bor equivalent (relevant |practical |commercial )?experience|or equivalent\b(?! qualification)", re.I)),
]  # fmt: skip

DEGREE_RE = re.compile(r"\b(degree|bsc|ba \(hons\)|undergraduate qualification)\b", re.I)
EQUIV_RE = re.compile(
    r"(or equivalent|or relevant experience|equivalent (relevant |practical |commercial )?experience|"
    r"or (similar|comparable) experience|or be operating at an equivalent)",
    re.I,
)

WORD_DAYS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
D = r"(\d(?:\.\d)?|one|two|three|four|five)"
OFFICE_PLACE = r"(?:the\s+|our\s+|a\s+)?(?:[A-Z][\w-]+\s+)?(?:office|on[- ]?site|onsite|site|head office|hq|workplace)"
OFFICE_DAYS_PATTERNS = [
    re.compile(rf"\b{D}\s*(?:-|–|to|or)\s*{D}\s*(?:x\s*)?days?\s*(?:a|per|each)?\s*(?:week)?\s*(?:in|on|at)?\s*{OFFICE_PLACE}", re.I),
    re.compile(rf"\b{D}\s*(?:x\s*)?days?\s*(?:a|per|each)\s*week\s*(?:in|on|at)\s*{OFFICE_PLACE}", re.I),
    re.compile(rf"\b{D}\s*(?:x\s*)?days?\s*(?:in|on|at)\s*{OFFICE_PLACE}", re.I),
    re.compile(rf"\b{D}\s*(?:x\s*)?days?\s*(?:a|per|each)\s*week\s*(?:onsite|on[- ]site|office)", re.I),
    re.compile(rf"\b{D}\s*(?:x\s*)?days?\s*(?:office|on[- ]?site|onsite)\b", re.I),
    re.compile(rf"{OFFICE_PLACE}\s*(?:at least\s*)?{D}\s*days?\s*(?:a|per)\s*week", re.I),
    re.compile(rf"\bat least\s*{D}\s*days?\s*(?:a|per)\s*week", re.I),
]  # fmt: skip
OCCASIONAL_OFFICE = re.compile(
    r"(\d|one)\s*x?\s*days?\s*(?:a|per|each)\s*(month|quarter)|occasional (travel|visits?) to|"
    r"ad[- ]hoc (travel|visits?)",
    re.I,
)
PERCENT_HOME = re.compile(
    r"(\d{1,3})\s*%\s*(?:home ?working|homeworking|remote|from home|home)", re.I
)
REMOTE_CUE = re.compile(
    r"(fully remote|remote[- ]first|remote working|100% remote|home[- ]based|work from home|"
    r"working from home|remote role|remote basis|\(remote\)|^remote\b|remote \(uk\)|remote\s*[-–|/]\s*uk|"
    r"predominantly remote|remote position|remote,|\bremote\s*$|\|\s*remote\b|remote\s*\|)",
    re.I | re.M,
)
HYBRID_CUE = re.compile(
    r"\bhybrid\b(?!\s+(environment|methodolog|delivery|agile|waterfall|cloud|app))", re.I
)
ONSITE_CUE = re.compile(
    r"(fully (office|on-?site)[- ]?based|office[- ]based|on-?site role|fully on-?site|site[- ]based|"
    r"(5|five) days (on[- ]?site|in the office)|this is not a remote|not (a )?remote|"
    r"office based|based on site|monday to friday[^.]{0,30}on-?site)",
    re.I,
)
UK_ONLY = re.compile(
    r"(uk[- ]based|based in the uk|within the uk|anywhere in the uk|uk only|uk residents?|"
    r"reside in the uk|live in the uk|uk[- ]wide|remote \(uk\)|remote\s*[-–]\s*uk|uk remote|"
    r"across the uk|right to work in the uk|open to applicants living anywhere in the uk)",
    re.I,
)
NOT_UK = re.compile(
    r"(us only|usa only|must be (based|located) in the (us|usa|united states|eu)|eu only|"
    r"not open to (uk|applicants outside)|north america only|americas only|"
    r"must reside in (the )?(us|usa|united states|canada))",
    re.I,
)

SALARY_RE = re.compile(
    r"£\s?(?P<lo>\d[\d,]*(?:\.\d+)?)\s*(?P<lok>k)?\s*(?:(?:-|–|to)\s*£?\s?(?P<hi>\d[\d,]*(?:\.\d+)?)\s*(?P<hik>k)?)?"
    r"\s*(?P<period>per annum|p\.?a\.?|a year|per year|annually|per day|a day|p/?d|daily|per hour|an hour|p/?h|hourly)?",
    re.I,
)


@dataclass
class Requirement:
    n: int
    text: str
    section: str
    strength: str  # essential | desirable | duty | other
    confidence: str  # stated | inferred
    tags: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class ParsedAdvert:
    lines: list[Line]
    requirements: list[Requirement]
    description_text: str
    data_years: float | None = None
    data_years_text: str | None = None
    data_years_implied: bool = False
    entry_signals: list[str] = field(default_factory=list)
    degree: str = "not_mentioned"  # required | or_equivalent | desirable | not_mentioned
    degree_text: str | None = None
    arrangement: str = "unknown"  # onsite | hybrid | remote | unknown
    office_days_min: float | None = None
    office_days_max: float | None = None
    arrangement_text: str | None = None
    uk_remote: str = "not_applicable"  # yes | no | unclear | not_applicable

    @property
    def counted(self) -> list[Requirement]:
        return [r for r in self.requirements if r.strength in (ESSENTIAL, DESIRABLE)]


def _num(token: str | None) -> float | None:
    if not token:
        return None
    t = token.lower().strip()
    return float(NUM_WORDS[t]) if t in NUM_WORDS else float(t)


def data_years_demand(text: str, tags: list[tuple[str, str]]) -> tuple[float, bool] | None:
    """Years of data experience a statement demands: (years, implied) or None.

    Only experience in a data/analyst/BI/reporting role or with a named tool counts. General
    experience ("experience working with stakeholders") never does.
    """
    has_tool = any(t == "skill" for t, _ in tags)
    for m in YEARS_RE.finditer(text):
        after = text[m.end() : m.end() + 60].lower()
        before = text[max(0, m.start() - 40) : m.start()].lower()
        window = text[max(0, m.start() - 40) : m.end() + 80]
        in_field = re.match(r"\s*(in|of|as|within|working in)\b", text[m.end() :], re.I)
        if (
            "experience" not in after[:45]
            and "experience" not in before
            and "exp" not in after[:15]
            and not in_field
        ) and not (has_tool and re.match(r"\s*(of\s+)?[A-Z]", text[m.end() :])):
            continue
        if NOT_EXPERIENCE.search(after[:25]) or NOT_EXPERIENCE.search(before[-15:]):
            continue
        if not (DATA_ANCHOR.search(window) or has_tool):
            continue
        low = int(m.group("months")) / 12 if m.group("months") else _num(m.group("n"))
        if low is None:
            continue
        return low, False
    if IMPLIED_ROLE.search(text):
        return 1.0, True
    return None


def office_days(text: str) -> tuple[float | None, float | None, str | None]:
    """(min, max, phrase) for office days per week stated anywhere in the text."""
    for pat in OFFICE_DAYS_PATTERNS:
        m = pat.search(text)
        if m:
            nums = [g for g in m.groups() if g]
            vals = [float(WORD_DAYS.get(g.lower(), g)) for g in nums]
            vals = [v for v in vals if 0 < v <= 5]
            if vals:
                return min(vals), max(vals), m.group(0).strip()
    m = PERCENT_HOME.search(text)
    if m:
        home = int(m.group(1))
        if 0 <= home <= 100:
            days = round(5 * (100 - home) / 100, 1)
            return days, days, m.group(0)
    m = OCCASIONAL_OFFICE.search(text)
    if m:
        return 0.0, 0.25, m.group(0)
    return None, None, None


def arrangement_of(
    text: str, title: str = ""
) -> tuple[str, float | None, float | None, str | None]:
    lo, hi, phrase = office_days(text)
    whole = f"{title}\n{text}"
    remote = REMOTE_CUE.search(whole)
    hybrid = HYBRID_CUE.search(whole)
    onsite = ONSITE_CUE.search(text)
    if lo is not None:
        if lo >= 5:
            return "onsite", lo, hi, phrase
        if hi is not None and hi < 1:
            return "remote", lo, hi, phrase
        return "hybrid", lo, hi, phrase
    if hybrid:
        return "hybrid", None, None, _snippet(whole, hybrid)
    if remote:
        return "remote", None, None, _snippet(whole, remote)
    if onsite:
        return "onsite", 5.0, 5.0, _snippet(text, onsite)
    return "unknown", None, None, None


def _snippet(text: str, m: re.Match, width: int = 120) -> str:
    """The line containing the match, trimmed to `width` characters."""
    start = text.rfind("\n", 0, m.start()) + 1
    end = text.find("\n", m.end())
    line = _norm_space(text[start : end if end != -1 else len(text)])
    return line if len(line) <= width else line[: width - 1].rstrip() + "…"


def uk_remote_eligibility(text: str, structured_country: str | None = None) -> str:
    text = clean_text(text)
    structured_country = clean_text(structured_country)
    if NOT_UK.search(text):
        return "no"
    if UK_ONLY.search(text):
        return "yes"
    if structured_country and re.search(
        r"united kingdom|\buk\b|great britain", structured_country, re.I
    ):
        return "yes"
    return "unclear"


def parse_salary(text: str) -> dict | None:
    """Salary as stated in free text. Never estimates; period only when stated or unambiguous."""
    for m in SALARY_RE.finditer(clean_text(text)):
        try:
            lo = float(m.group("lo").replace(",", "")) * (1000 if m.group("lok") else 1)
            hi = m.group("hi")
            hi = float(hi.replace(",", "")) * (1000 if m.group("hik") else 1) if hi else lo
        except ValueError:
            continue
        if m.group("lok") and not m.group("hik") and m.group("hi") and hi < 1000:
            hi *= 1000  # "£30k-35" style
        p = (m.group("period") or "").lower().replace(".", "")
        if p in ("per annum", "pa", "a year", "per year", "annually"):
            period = "annum"
        elif p in ("per day", "a day", "pd", "p/d", "daily"):
            period = "day"
        elif p in ("per hour", "an hour", "ph", "p/h", "hourly"):
            period = "hour"
        elif lo >= 10000:
            period = "annum"
        else:
            continue  # unclear period: don't guess
        if lo < 5:
            continue
        return {
            "salary_min": lo,
            "salary_max": max(lo, hi),
            "salary_period": period,
            "salary_text": _norm_space(m.group(0)),
        }
    return None


# ---------------------------------------------------------------------------------------------
# 5. Whole advert
# ---------------------------------------------------------------------------------------------

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(“\"'])")


def _statements(line: Line) -> list[str]:
    if line.kind == "item":
        return [line.text]
    parts = [p.strip() for p in SENTENCE_SPLIT.split(line.text) if p.strip()]
    return parts or [line.text]


def parse_advert(
    html: str | None,
    title: str = "",
    tax: Taxonomy | None = None,
    structured_country: str | None = None,
) -> ParsedAdvert:
    html, title = clean_text(html), clean_text(title)
    structured_country = clean_text(structured_country)
    tax = tax or get_taxonomy()
    lines = html_to_lines(html)
    reqs: list[Requirement] = []
    seen: set[str] = set()  # some adverts repeat their whole requirements list
    section = "intro"
    n = 0
    for line in lines:
        if _looks_like_heading(line):
            section = section_of(line.text)
            # "Essential criteria: SQL, Excel" style: keep any text after the colon as a statement.
            _, _, rest = line.text.partition(":")
            if not (rest.strip() and len(rest.split()) >= 3 and line.kind != "heading"):
                continue
            line = Line(rest.strip(), "para")
        for text in _statements(line):
            if len(text.split()) < 2 and (line.kind != "item" or len(text) < 2):
                continue  # one-word paragraphs are labels; one-word list items ("Python.") count
            key = re.sub(r"\W+", " ", text.lower()).strip()
            if key in seen:
                continue
            seen.add(key)
            tags = tax.tag(text)
            strength, confidence = classify_statement(
                text, section, bool(tags), is_item=line.kind == "item"
            )
            n += 1
            reqs.append(Requirement(n, text, section, strength, confidence, tags))

    full_text = "\n".join(ln.text for ln in lines)
    parsed = ParsedAdvert(lines=lines, requirements=reqs, description_text=full_text)

    # Data-experience demand: only from essential statements (desirable ones never gate).
    best = None
    for r in reqs:
        if r.strength != ESSENTIAL:
            continue
        d = data_years_demand(r.text, r.tags)
        if d and (
            best is None or d[0] > best[0][0] or (d[0] == best[0][0] and best[0][1] and not d[1])
        ):
            best = (d, r.text)
    if best:
        (parsed.data_years, parsed.data_years_implied), parsed.data_years_text = best

    signals = []
    title_and_text = f"{title}\n{full_text}"
    for label, pat in ENTRY_SIGNALS:
        if pat.search(title_and_text):
            signals.append(label)
    parsed.entry_signals = signals

    for r in reqs:
        if DEGREE_RE.search(r.text) and r.strength in (ESSENTIAL, DESIRABLE, OTHER):
            if r.strength == OTHER and not ESSENTIAL_CUE.search(r.text):
                continue
            if EQUIV_RE.search(r.text):
                parsed.degree = "or_equivalent"
            elif r.strength == DESIRABLE:
                parsed.degree = "desirable"
            else:
                parsed.degree = "required"
            parsed.degree_text = r.text
            if parsed.degree == "required":
                break

    arrangement, lo, hi, phrase = arrangement_of(full_text, title)
    parsed.arrangement, parsed.office_days_min, parsed.office_days_max = arrangement, lo, hi
    parsed.arrangement_text = phrase
    if arrangement == "remote":
        parsed.uk_remote = uk_remote_eligibility(full_text, structured_country)
    return parsed
