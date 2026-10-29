"""Filters that decide which adverts are shown by default. Nothing is ever deleted: an excluded
advert keeps an `excluded_reason` and can be revealed in the results.

- Title filter (data/title_rules.csv), applied to the TITLE only: senior words exclude, entry
  words boost. "Senior stakeholders" in a description never excludes anything.
- Relevance filter: is this actually a data job?
- Training-course filter: paid courses advertised as "Trainee Data Analyst" jobs.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from functools import lru_cache

from skillmatch import config
from skillmatch.taxonomy import Taxonomy, get_taxonomy
from skillmatch.text import clean_text

NOT_A_DATA_ROLE = "not a data role"
TRAINING_COURSE = "training course, not a job"
OUT_OF_REGION = "outside the West Midlands"
EXPIRED = "expired"

# Title words that make a job a data role on their own.
DATA_TITLE = re.compile(
    r"\b(data|databases?|insights?|bi|business intelligence|mi|management information|reporting|"
    r"information|research|evaluation|crm|analytics|intelligence|statistic(?:s|al|ian)?|"
    r"power\s?bi|sql|dashboards?)\b",
    re.IGNORECASE,
)
# Titles that are not data roles even with a data word in them (calibrated on the live sample:
# "Information Security Analyst", "Management Reporting Accountant", "BD Executive (Data)").
NOT_DATA_TITLE = re.compile(
    r"\b(security|cyber|accountant|accounting|solicitor|sales|business development|bd|"
    r"r\s*&\s*d|research\s*(?:&|and)\s*development|information assurance|recruit\w*)\b",
    re.IGNORECASE,
)
# "<something> Analyst" is a data role unless the something marks a different field.
ANALYST = re.compile(r"\b(analyst|analytics|analysis)\b", re.IGNORECASE)
NOT_DATA_ANALYST = re.compile(
    r"\b(financ\w*|fp\s*&\s*a|business|soc|security|cyber|support|service desk|it|systems?|network|"
    r"qc|tax|billing|accounts?|test\w*|infrastructure|application|actuarial|credit|treasury|"
    r"surveyor|technology operations|edi|payroll|hris|bom|feature configuration|revenue|sap|"
    r"integration|pmo|threat|detection|drilling)\b",
    re.IGNORECASE,
)
# Job families whose adverts mention data tools without being data jobs.
ENGINEERING_TITLE = re.compile(
    r"\b(engineer|developer|programmer|architect|designer|technician|merchandiser|buyer|"
    r"estimator|planner|administrator|assistant|consultant)\b",
    re.IGNORECASE,
)
# Skills too generic to make a role "data" by themselves (most office jobs mention them).
GENERIC_SKILLS = {"excel", "microsoft_office", "google_sheets", "erp_systems", "hr_systems"}

TRAINING_PATTERNS = re.compile(
    r"(job guarantee|money[- ]back guarantee|study fees|course fees|career programme|"
    r"career program\b|our programme includes|finance terms|recruitment support until placed|"
    r"we support you into employment|enquire now|training package|pay for (the|your) course)",
    re.IGNORECASE,
)

# Treat qualification names as entities, then look for a mandatory requirement in the same
# sentence. Acronyms alone are not enough: adverts commonly mention these in desirable lists.
PROFESSIONAL_QUALIFICATION = re.compile(
    r"\b(?:ACCA|CIMA|CIPD|ACA|ICAS|ICAEW|AAT|CFA|CII|CIPFA|CTA|ATT|CIIA|CIPHE)\b",
    re.IGNORECASE,
)
QUALIFICATION_REQUIRED = re.compile(
    r"\b(?:required|essential|must\s+(?:have|hold|be)|need(?:ed)?\s+to\s+have|"
    r"(?:fully\s+)?qualified\s+(?:by|with|as)|qualification\s+is\s+(?:required|essential)|"
    r"qualified)\b",
    re.IGNORECASE,
)
QUALIFICATION_EXEMPT = re.compile(
    r"\b(?:desirable|preferred|preferably|ideally|advantageous|a\s+plus|"
    r"studying\s+towards|working\s+towards|part[- ]qualified|student\s+member|"
    r"or\s+studying|study(?:ing)?\s+for)\b",
    re.IGNORECASE,
)
QUALIFICATION_NEGATED = re.compile(
    r"\b(?:not\s+(?:required|essential|a\s+requirement|needed)|no\s+(?:qualification\s+)?need|"
    r"does\s+not\s+need|isn't\s+required|is\s+not\s+necessary)\b",
    re.IGNORECASE,
)
QUALIFICATION_REQUIRED_HEADING = re.compile(
    r"\b(?:essential|required|mandatory|minimum)\b.*\bqualifications?\b|"
    r"\bqualifications?\b.*\b(?:essential|required|mandatory|minimum)\b",
    re.IGNORECASE,
)
QUALIFICATION_DESIRABLE_HEADING = re.compile(
    r"\b(?:desirable|preferred|nice\s+to\s+have|advantageous)\b.*\bqualifications?\b|"
    r"\bqualifications?\b.*\b(?:desirable|preferred|nice\s+to\s+have|advantageous)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TitleRule:
    word: str
    action: str  # exclude | boost
    pattern: re.Pattern


@lru_cache(maxsize=1)
def title_rules() -> tuple[TitleRule, ...]:
    with (config.DATA_DIR / "title_rules.csv").open() as f:
        return tuple(
            TitleRule(r["word"], r["action"], re.compile(r["pattern"], re.IGNORECASE))
            for r in csv.DictReader(f)
        )


@dataclass
class TitleVerdict:
    excluded_by: str | None = None  # the first exclude word found
    boosted_by: list[str] = field(default_factory=list)


def check_title(title: str) -> TitleVerdict:
    title = clean_text(title)
    v = TitleVerdict()
    for rule in title_rules():
        if rule.pattern.search(title or ""):
            if rule.action == "exclude" and v.excluded_by is None:
                v.excluded_by = rule.word
            elif rule.action == "boost":
                v.boosted_by.append(rule.word)
    return v


def is_data_title(title: str) -> bool:
    title = clean_text(title)
    return bool(DATA_TITLE.search(title or ""))


def technical_signals(text: str, tax: Taxonomy | None = None) -> list[str]:
    """Distinct non-generic technical skills a description mentions."""
    text = clean_text(text)
    tax = tax or get_taxonomy()
    found = []
    for s in tax.skills.values():
        if s.id in GENERIC_SKILLS:
            continue
        if any(p.search(text or "") for p in s.patterns):
            found.append(s.id)
    return found


def is_data_role(
    title: str, description_text: str | None = None, tax: Taxonomy | None = None
) -> bool:
    """Is this actually a data job? Judged on the TITLE only (see DECISIONS.md).

    1. A data word in the title (data, insight, BI, MI, reporting, research...) -> yes, unless
       the title also names a non-data field (security, accountant, sales...).
    2. "Analyst" in the title -> yes, unless qualified by a non-data field (finance, business,
       IT support...). Performance, commercial, pricing, planning and operations analysts stay.
    3. Anything else -> no.

    There used to be a third route: any title with 2+ technical skills in the description. On
    the 27 Oct 2026 live run it let in 98 adverts under 59 titles and none was an entry-level
    data job (Scrum Master, Video Editor, account executives). The skills it found were often
    in the employer's blurb, not the job: a database company's Video Editor mentions MySQL.
    `description_text` and `tax` are kept so existing callers don't change.
    """
    title = clean_text(title) or ""
    if NOT_DATA_TITLE.search(title):
        return False
    if is_data_title(title):
        return True
    if ANALYST.search(title):
        return not NOT_DATA_ANALYST.search(title)
    return False


def is_training_course(title: str, description_text: str) -> bool:
    # A named placement programme is usually a training product when the advert also uses
    # the course-sales language below. Paid employment apprenticeships remain eligible.
    title, description_text = clean_text(title), clean_text(description_text)
    hits = set(m.group(0).lower() for m in TRAINING_PATTERNS.finditer(description_text or ""))
    placement = bool(
        re.search(r"\bplacement\s+programme\b", f"{title or ''} {description_text or ''}", re.I)
    )
    return (
        len(hits) >= 2
        or ("no experience" in (title or "").lower() and bool(hits))
        or (placement and len(hits) >= 1)
    )


def required_professional_qualification(title: str, text: str) -> str | None:
    """Return evidence when an advert makes a professional qualification mandatory.

    Desired qualifications and studying-towards routes are deliberately retained. The check
    is sentence-based so a nearby mandatory phrase cannot turn a separate desirable mention
    into an exclusion.
    """
    title, text = clean_text(title), clean_text(text)
    combined = f"{title or ''}.\n{text or ''}"
    required_heading = False
    desirable_heading = False
    sentences = []
    for line in combined.splitlines():
        line = line.strip().lstrip("-•* ").strip()
        if not line:
            continue
        # Section headings carry their strength to the following lines until another
        # qualifications heading changes it. A heading itself is not qualification evidence.
        if QUALIFICATION_REQUIRED_HEADING.search(line) and len(line) < 100:
            required_heading, desirable_heading = True, False
            continue
        if QUALIFICATION_DESIRABLE_HEADING.search(line) and len(line) < 100:
            required_heading, desirable_heading = False, True
            continue
        for sentence in re.split(r"(?<=[.!?])\s+|[;•]+", line):
            if sentence.strip():
                sentences.append((sentence.strip(), required_heading, desirable_heading))
    for sentence, required_heading, desirable_heading in sentences:
        quals = list(PROFESSIONAL_QUALIFICATION.finditer(sentence))
        if not quals or desirable_heading:
            continue
        # Headings and explicit qualifying phrases both establish a requirement. A simple
        # "ACCA qualified" statement also counts, but negation and preference win.
        required = required_heading or bool(QUALIFICATION_REQUIRED.search(sentence))
        if not required:
            continue
        shared_study_route = len(quals) > 1 and bool(
            re.search(
                r"\b(?:or|alternatively)\s+(?:currently\s+)?(?:studying|working)\s+towards\s+(?:either|any|one|the\s+qualification|it)\b",
                sentence,
                re.IGNORECASE,
            )
        )
        # If the sentence qualifies the same qualification as desirable/studying, skip it.
        for index, match in enumerate(quals):
            # Qualification strength belongs to the local credential clause. Bound the
            # context by neighbouring qualification names so "CIMA desirable" cannot
            # soften a separate "ACCA required" clause earlier in the same sentence.
            left = quals[index - 1].end() if index else 0
            right = quals[index + 1].start() if index + 1 < len(quals) else len(sentence)
            context = sentence[left:right]
            if (
                shared_study_route
                or QUALIFICATION_EXEMPT.search(context)
                or QUALIFICATION_NEGATED.search(context)
            ):
                continue
            # A comma-separated continuation such as "ACCA required, or studying towards"
            # still states a permitted studying route for the preceding credential.
            if index + 1 == len(quals):
                trailing = sentence[match.end() :]
                if re.search(
                    r",\s*or\s+(?:currently\s+)?(?:studying|working)\s+towards\b", trailing, re.I
                ):
                    continue
            return f"Required professional qualification: {match.group(0).upper()} ({sentence.strip()})"
    return None
