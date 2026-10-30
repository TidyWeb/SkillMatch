"""Match a profile against an advert: requirement-by-requirement coverage, then a tier.

Rules (thresholds live in skillmatch/config.py):

- Course skills, added technical skills and selected area competencies are met.
- A selected technical skill is partly met for explicit role, corporate, commercial, industry,
  professional, proven, significant, extensive or years-based experience requirements.
- Plain familiarity and desirable experience do not downgrade selected technical skills.
- A requested skill or competency absent from the profile is a gap.
- Unclassified requirements (no tags) are shown but don't count. Inferred requirements can raise
  a match but never sink one.
- Tiers: Strong match, Good match, Stretch, Not yet. No percentages anywhere.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from skillmatch import config
from skillmatch.geo import haversine_miles
from skillmatch.phrasing import Phraser, join_items
from skillmatch.profile import QUALIFICATIONS, Profile
from skillmatch.taxonomy import Taxonomy, get_taxonomy

MET, PARTLY, GAP, UNCLASSIFIED = "met", "partly", "gap", "unclassified"
STRONG, GOOD, STRETCH, NOT_YET = "strong", "good", "stretch", "not_yet"
TIER_ORDER = [STRONG, GOOD, STRETCH, NOT_YET]
RANK = {MET: 2, PARTLY: 1, GAP: 0}

LEADERSHIP_REQ = re.compile(
    r"\b(leadership|senior (stakeholders|leaders|management|managers|decision[- ]makers)|"
    r"board|directors|executive|trustees|lead(ing)? (a )?teams?|line manag\w*|"
    r"manag(e|ing) (a )?team|people management|report(ing)? to (senior|the board|directors))\b",
    re.IGNORECASE,
)
LEADERSHIP_COMPETENCIES = {"team_leadership", "reporting_to_leadership", "stakeholder_management"}
DISJUNCTIVE = re.compile(r"\b(or|either|such as|e\.g\.|for example|similar)\b", re.IGNORECASE)
# Statements that ask for work experience, not just familiarity: a course project is partly.
PROFESSIONAL_WORDS = re.compile(r"\b(commercial|professional|industry|corporate)\b", re.I)
YEARS_WORDS = re.compile(r"\b\d+\+?\s*years?\b", re.I)
NEGATED_EXPERIENCE = re.compile(r"\b(no|not|without|never)\b[^.!?]{0,35}\bexperience\b", re.I)
OPTIONAL_EXPERIENCE = re.compile(
    r"\b(not required|not essential|not needed|optional|would be (?:a )?plus|"
    r"is a plus|a plus|is helpful|is beneficial|would be advantageous|preferable|desirable)\b",
    re.I,
)
QUALIFIED_EXPERIENCE = re.compile(r"\b(proven|significant|extensive)\s+experience\b", re.I)
ROLE_EXPERIENCE = re.compile(
    r"\bexperience\s+(?:working\s+)?as\s+(?:an?\s+)?"
    r"[a-z][\w/&-]*(?:\s+[\w/&-]+){0,5}|"
    r"\bexperience\s+in\s+(?:an?\s+)?"
    r"[a-z][\w/&-]*(?:\s+[\w/&-]+){0,4}\s+role\b",
    re.I,
)


def _professional_experience_for_skill(sentence: str, skill, tax: Taxonomy) -> bool:
    """Recognise work-based experience asks while keeping them tied to the named skill."""
    boundaries = (
        r"[;.!?]|(?:,\s*|\s+(?:and|or|but|while)\s+)"
        r"(?=(?:knowledge|understanding|familiarity|familiar|experience|commercial|"
        r"professional|practical|proven|demonstrable|ability|confiden\w*)\b)"
    )
    for clause in re.split(boundaries, sentence, flags=re.I):
        if not any(pattern.search(clause) for pattern in skill.patterns):
            continue
        if NEGATED_EXPERIENCE.search(clause) or OPTIONAL_EXPERIENCE.search(clause):
            continue
        experience = re.search(r"\bexperience\b", clause, re.I)
        is_role_experience = ROLE_EXPERIENCE.search(clause)
        is_qualified_experience = QUALIFIED_EXPERIENCE.search(clause)
        years_experience = YEARS_WORDS.search(clause)
        professional_context = PROFESSIONAL_WORDS.search(clause)
        if (
            is_role_experience
            or is_qualified_experience
            or (years_experience and experience)
            or (experience and professional_context)
        ):
            return True
        # Some adverts say "2+ years in industry using SQL" without the word experience.
        if years_experience and re.search(r"\b(in|within)\s+(?:the\s+)?industry\b", clause, re.I):
            return True
    return False


def _experience_reason(sentence: str, skill_label: str) -> str:
    """Explain the actual experience signal that made a selected skill only partly met."""
    if re.search(r"\bcorporate\b", sentence, re.I):
        signal = "experience in a corporate environment"
    elif re.search(r"\bcommercial\b", sentence, re.I):
        signal = "commercial experience"
    elif re.search(r"\bindustry\b", sentence, re.I):
        signal = "industry experience"
    elif re.search(r"\bprofessional\b", sentence, re.I):
        signal = "professional experience"
    else:
        role = re.search(
            r"\bexperience\b[^.!?]{0,45}?\b(?:as|in)\s+((?:an?\s+)?"
            r"(?:data|bi|business intelligence|reporting|quality|scrum|agile|product|"
            r"research|pricing|statistical|analytics|analyst|engineer|developer|coach)"
            r"[^,;.!?]{0,32})",
            sentence,
            re.I,
        )
        if role:
            signal = f"experience as {role.group(1).strip()}"
        elif QUALIFIED_EXPERIENCE.search(sentence):
            signal = QUALIFIED_EXPERIENCE.search(sentence).group(1).lower() + " experience"
        elif YEARS_WORDS.search(sentence):
            signal = YEARS_WORDS.search(sentence).group(0) + " of experience"
        else:
            signal = "professional experience"
    return (
        f"Advert asks for {signal} related to {skill_label}. Partly met: {skill_label} is in "
        f"your profile, but this work experience is not recorded."
    )


INTEREST_ONLY = re.compile(r"\binterest in\b", re.IGNORECASE)
EXPERIENCE_WORDS = re.compile(
    r"\b(experience|knowledge|background|understanding|worked|working in)\b", re.IGNORECASE
)


@dataclass
class TagResult:
    tag_type: str
    tag_id: str
    label: str
    status: str
    answer: str | None = None  # phrasing line when met or partly met
    gap: str | None = None  # advice when a gap
    evidence_role: str | None = None


@dataclass
class Coverage:
    req_id: str
    n: int
    strength: str
    confidence: str
    sentence: str
    status: str
    tags: list[TagResult] = field(default_factory=list)

    @property
    def counts(self) -> bool:
        """Does this requirement count towards the tier?"""
        return self.status != UNCLASSIFIED and self.confidence == "stated"

    @property
    def answers(self) -> list[str]:
        return [t.answer for t in self.tags if t.status in (MET, PARTLY) and t.answer]

    @property
    def gaps(self) -> list[TagResult]:
        return [t for t in self.tags if t.status == GAP]


@dataclass
class MatchResult:
    vacancy: dict
    tier: str
    tier_label: str
    reasons: list[str]
    coverage: list[Coverage]
    distance_miles: float | None
    top_answers: list[str]
    essential_gaps: list[str]
    gap_advice: list[str]
    desirable_met: int

    @property
    def vacancy_id(self) -> str:
        return self.vacancy["vacancy_id"]


# ---------------------------------------------------------------------------------------------


# Skill labels that start with an ordinary word read better in lower case mid-sentence.
COMMON_FIRST_WORDS = {
    "data", "statistics", "building", "machine", "using", "survey", "qualitative", "business",
    "agile", "records", "programming", "cloud", "web",
}  # fmt: skip


def sentence_label(label: str) -> str:
    """'Data cleaning and validation' -> 'data cleaning and validation'; 'Power BI' unchanged."""
    if label.split()[0].lower() in COMMON_FIRST_WORDS:
        return label[0].lower() + label[1:]
    return label


def _area_for(profile: Profile, competency: str, tax: Taxonomy):
    for area in profile.areas:
        if competency in area.skills:
            return area, tax.archetypes[area.id].label
    return None, None


def evaluate_tag(
    tag_type: str,
    tag_id: str,
    sentence: str,
    profile: Profile,
    tax: Taxonomy,
    phraser: Phraser,
    experience_counts: bool = True,
) -> TagResult:
    if tag_type == "skill":
        skill = tax.skills[tag_id]
        label = sentence_label(skill.label)
        if (
            experience_counts
            and tag_id in profile.skills
            and _professional_experience_for_skill(sentence, skill, tax)
        ):
            return TagResult(
                tag_type,
                tag_id,
                label,
                PARTLY,
                _experience_reason(sentence, label),
            )
        if tag_id in profile.skills:
            return TagResult(
                tag_type,
                tag_id,
                label,
                MET,
                phraser.fill("answers", "skill_confident", skill=label),
            )
        gap = phraser.fill("gaps", "skill", skill=label)
        if tag_id == "azure" and re.search(r"\bfabric\b", sentence, re.I):
            gap += " This includes Microsoft Fabric."
        return TagResult(tag_type, tag_id, label, GAP, gap=gap)

    comp = tax.competencies[tag_id]
    label = comp.label
    area, area_label = _area_for(profile, tag_id, tax)
    if area:
        return TagResult(
            tag_type,
            tag_id,
            label,
            MET,
            f"Requirement: {label}. Your selected area of expertise is {area_label}.",
            evidence_role=area_label,
        )
    key = "sector" if comp.category == "sector" else "competency"
    return TagResult(tag_type, tag_id, label, GAP, gap=phraser.fill("gaps", key, requirement=label))


def _combine(sentence: str, results: list[TagResult]) -> str:
    statuses = [t.status for t in results]
    skill_partly = any(t.tag_type == "skill" and t.status == PARTLY for t in results)
    skill_gap = any(t.tag_type == "skill" and t.status == GAP for t in results)
    # A missing technical skill caps a mixed requirement at partly met, even when the sentence
    # uses OR or examples. It must never disappear behind a met alternative.
    if skill_partly:
        return PARTLY
    if skill_gap:
        return PARTLY if any(s == MET for s in statuses) else GAP
    if DISJUNCTIVE.search(sentence):
        return max(statuses, key=lambda s: RANK[s])
    if all(s == MET for s in statuses):
        return MET
    if all(s == GAP for s in statuses):
        return GAP
    return PARTLY


QUALIFICATION_LEVELS = (
    (8, re.compile(r"\b(phd|doctorate|level 8)\b", re.I)),
    (7, re.compile(r"\b(master'?s|postgraduate|level 7)\b", re.I)),
    (5, re.compile(r"\b(hnd|hnc|foundation degree|level 5)\b", re.I)),
    (6, re.compile(r"\b(bachelor'?s|degree|graduate qualification|level 6)\b", re.I)),
    (3, re.compile(r"\b(a[- ]levels?|level 3)\b", re.I)),
    (2, re.compile(r"\b(gcse|o[- ]levels?|level 2)\b", re.I)),
)
DEGREE_NOT_REQUIRED = re.compile(
    r"\b(degree|qualification)\b[^.!?]{0,25}\b(not required|not essential|unnecessary|not needed)\b|\b(no degree|degree not required)\b",
    re.I,
)


def qualification_level(sentence: str) -> int | None:
    """Qualification level explicitly requested in an advert requirement."""
    if DEGREE_NOT_REQUIRED.search(sentence):
        return None
    return next(
        (level for level, pattern in QUALIFICATION_LEVELS if pattern.search(sentence)), None
    )


DATA_ROLE_YEARS = re.compile(
    r"\b\d+\+?\s*years?\b[^.!?]{0,80}\b(data|bi|business intelligence|reporting|analyst)\s+(?:role|job|position|experience)?\b|"
    r"\b(?:data|bi|business intelligence|reporting)\s+(?:role|job|position)\b[^.!?]{0,80}\b\d+\+?\s*years?\b",
    re.I,
)


def evaluate_requirement(req: dict, profile: Profile, tax: Taxonomy, phraser: Phraser) -> Coverage:
    sentence = req["evidence_sentence"]
    tags = list(dict.fromkeys(tuple(t) for t in req.get("tags", [])))
    # Stored tags may come from a snapshot built with an older taxonomy. Keep technical tags only
    # when their current patterns still match the evidence sentence; this drops retired IDs and
    # stale false positives without changing the stored snapshot.
    tags = [
        (tag_type, tag_id)
        for tag_type, tag_id in tags
        if tag_type != "skill"
        or (
            tag_id in tax.skills
            and any(pattern.search(sentence) for pattern in tax.skills[tag_id].patterns)
        )
    ]
    # Recheck the sentence so newly known skill spellings are visible in old snapshots.
    for tag_type, tag_id in tax.tag(sentence):
        if tag_type == "skill" and (tag_type, tag_id) not in tags:
            tags.append((tag_type, tag_id))
    if INTEREST_ONLY.search(sentence) and not EXPERIENCE_WORDS.search(sentence):
        # "An interest in the automotive industry" is an attitude, not sector experience.
        tags = [
            t
            for t in tags
            if tax.competencies.get(t[1]) is None or tax.competencies[t[1]].category != "sector"
        ]
    cov = Coverage(
        req["req_id"], req["n"], req["strength"], req["confidence"], sentence, UNCLASSIFIED
    )
    cov.tags = [
        evaluate_tag(
            t,
            i,
            sentence,
            profile,
            tax,
            phraser,
            experience_counts=req["strength"] != "desirable",
        )
        for t, i in tags
    ]
    level = qualification_level(sentence)
    if level is not None:
        # Only the qualification level is recorded; subject words must not become extra skill
        # demands or let "degree in data analysis or equivalent" bypass the level check.
        cov.tags = []
        labels = {
            2: "Level 2 qualification",
            3: "Level 3 qualification",
            5: "Level 5 qualification",
            6: "degree or equivalent (Level 6)",
            7: "Master's degree (Level 7)",
            8: "PhD or doctorate (Level 8)",
        }
        label = labels[level]
        if profile.highest_qualification >= level:
            cov.tags.append(
                TagResult(
                    "qualification",
                    f"level_{level}",
                    label,
                    MET,
                    f"Requirement: {label}. Your highest qualification is {QUALIFICATIONS[profile.highest_qualification]}.",
                )
            )
        else:
            cov.tags.append(
                TagResult(
                    "qualification",
                    f"level_{level}",
                    label,
                    GAP,
                    gap=f"This advert asks for {label}; your highest qualification is {QUALIFICATIONS[profile.highest_qualification]}.",
                )
            )
    if not cov.tags:
        return cov
    cov.status = _combine(sentence, cov.tags)
    return cov


def _signals(vacancy: dict) -> list[str]:
    s = vacancy.get("entry_signals") or []
    if isinstance(s, str):
        try:
            s = json.loads(s)
        except ValueError:
            s = []
    return list(s)


def match_vacancy(
    profile: Profile,
    vacancy: dict,
    requirements: list[dict],
    home: tuple[float, float] | None = None,
    tax: Taxonomy | None = None,
    phraser: Phraser | None = None,
) -> MatchResult:
    tax = tax or get_taxonomy()
    phraser = phraser or Phraser(tax)
    vacancy = {**vacancy, "entry_signals": _signals(vacancy)}
    coverage = [
        evaluate_requirement(r, profile, tax, phraser)
        for r in sorted(requirements, key=lambda r: r["n"])
        if r["strength"] in ("essential", "desirable")
        and not (
            DATA_ROLE_YEARS.search(r["evidence_sentence"])
            and not any(t == "skill" for t, _ in r.get("tags", []))
        )
    ]
    essentials = [c for c in coverage if c.strength == "essential" and c.counts]
    e_gaps = [c for c in essentials if c.status == GAP]
    e_partly = [c for c in essentials if c.status == PARTLY]
    desirable_met = sum(1 for c in coverage if c.strength == "desirable" and c.status == MET)
    # Inferred requirements can raise a match (never sink one): fully met ones count towards
    # the minimum number of essentials a Strong match needs.
    inferred_met = sum(
        1
        for c in coverage
        if c.strength == "essential" and c.confidence == "inferred" and c.status == MET
    )

    n_gaps = len(e_gaps)

    if n_gaps >= config.NOT_YET_MIN_GAPS:
        tier = NOT_YET
    elif n_gaps >= config.STRETCH_MIN_GAPS:
        tier = STRETCH
    elif n_gaps >= 1:
        tier = GOOD
    elif len(essentials) + inferred_met < config.STRONG_MIN_ESSENTIALS:
        tier = GOOD  # too little to check: never call it a strong match
    elif len(e_partly) <= config.STRONG_MAX_PARTLY:
        tier = STRONG
    else:
        tier = GOOD

    reasons: list[str] = []
    gap_labels = [t.label for c in e_gaps for t in c.gaps]
    if not essentials:
        reasons.append(phraser.fill("reasons", "no_essentials_found"))
    elif (
        tier == GOOD
        and not e_gaps
        and len(essentials) + inferred_met < config.STRONG_MIN_ESSENTIALS
    ):
        reasons.append(phraser.fill("reasons", "few_essentials_found", n=len(essentials)))
    elif not e_gaps and not e_partly:
        reasons.append(phraser.fill("reasons", "all_essentials_answered"))
    if e_gaps:
        reasons.append(
            phraser.fill("reasons", "essential_gaps", n=len(e_gaps), items=join_items(gap_labels))
        )
    if e_partly:
        partly_labels = [t.label for c in e_partly for t in c.tags if t.status != MET]
        reasons.append(
            phraser.fill(
                "reasons", "essential_partly", n=len(e_partly), items=join_items(partly_labels)
            )
        )
    signals = vacancy["entry_signals"]
    if signals:
        reasons.append(
            phraser.fill("reasons", "entry_signals", signals=join_items(signals, limit=3))
        )
    if desirable_met:
        reasons.append(phraser.fill("reasons", "desirable_answered", n=desirable_met))

    distance = None
    if home and vacancy.get("lat") is not None and vacancy.get("lon") is not None:
        distance = round(haversine_miles(home[0], home[1], vacancy["lat"], vacancy["lon"]), 1)

    return MatchResult(
        vacancy=vacancy,
        tier=tier,
        tier_label=phraser.tier_label(tier),
        reasons=reasons,
        coverage=coverage,
        distance_miles=distance,
        top_answers=top_answers(coverage),
        essential_gaps=list(dict.fromkeys(gap_labels)),
        gap_advice=list(
            dict.fromkeys(
                t.gap for c in coverage for t in c.gaps if t.gap and c.strength == "essential"
            )
        ),
        desirable_met=desirable_met,
    )


def top_answers(coverage: list[Coverage], limit: int = 3) -> list[str]:
    """The lines for the card: career evidence first (that's the point), then skills."""
    seen_tags: set = set()
    picked: list[tuple[int, str]] = []
    for c in coverage:
        for t in c.tags:
            if t.status != MET or not t.answer or (t.tag_type, t.tag_id) in seen_tags:
                continue
            seen_tags.add((t.tag_type, t.tag_id))
            priority = (0 if t.tag_type == "competency" else 2) + (
                0 if c.strength == "essential" else 1
            )
            picked.append((priority, t.answer))
    picked.sort(key=lambda x: x[0])
    return [a for _, a in picked[:limit]]
