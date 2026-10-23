"""Match a profile against an advert: requirement-by-requirement coverage, then a tier.

Rules (thresholds live in skillmatch/config.py):

- Met: a skill rated "used in a project" or "confident", or a competency ticked with evidence.
- Partly met: a skill "learned on the course" only; a related skill in the same family; or a
  competency ticked without evidence.
- Gap: nothing in the profile answers it.
- A competency evidenced at manager level or above meets requirements about leadership, senior
  stakeholders or reporting to leadership.
- Unclassified requirements (no tags) are shown but don't count. Inferred requirements can raise
  a match but never sink one.
- Data-experience gate: only the advert's explicit data-experience demand is compared with the
  user's years in a data job.
- Tiers: Strong fit, Good fit, Stretch, Not yet. No percentages anywhere.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field

from skillmatch import config
from skillmatch.geo import haversine_miles
from skillmatch.phrasing import Phraser, join_items, years_text
from skillmatch.profile import Profile, Role
from skillmatch.taxonomy import SENIORITY, Taxonomy, get_taxonomy

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
HANDS_ON = re.compile(
    r"\b(proven|practical|hands-on|hands on|demonstrable|demonstrated|significant|extensive|"
    r"professional|commercial|track record|\d+\+?\s*years?|several years)\b[^.]{0,40}\bexperience\b|"
    r"\bexperience (managing|delivering|leading|running)\b",
    re.IGNORECASE,
)
INTEREST_ONLY = re.compile(r"\binterest in\b", re.IGNORECASE)
EXPERIENCE_WORDS = re.compile(
    r"\b(experience|knowledge|background|understanding|worked|working in)\b", re.IGNORECASE
)
MANAGER_RANK = SENIORITY.index("manager")


@dataclass
class TagResult:
    tag_type: str
    tag_id: str
    label: str
    status: str
    answer: str | None = None  # phrasing line when met or partly met
    gap: str | None = None  # advice when a gap
    evidence_role: str | None = None  # which previous role answered it


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
    data_gate: str  # ok | waived | small | stretch | not_yet
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


def _best_role(profile: Profile, competency: str) -> tuple[Role | None, str]:
    """The role that best evidences a competency: with evidence first, then most senior."""
    best, best_ev = None, ""
    for role in profile.roles:
        if competency not in role.competencies:
            continue
        ev = role.competencies[competency] or ""
        key = (bool(ev.strip()), role.rank, role.years)
        if best is None or key > (bool(best_ev.strip()), best.rank, best.years):
            best, best_ev = role, ev
    return best, best_ev


def _senior_role(profile: Profile) -> Role | None:
    roles = [r for r in profile.roles if r.rank >= MANAGER_RANK and r.competencies]
    return max(roles, key=lambda r: (r.rank, r.years)) if roles else None


def evaluate_tag(
    tag_type: str, tag_id: str, sentence: str, profile: Profile, tax: Taxonomy, phraser: Phraser
) -> TagResult:
    if tag_type == "skill":
        skill = tax.skills[tag_id]
        label = sentence_label(skill.label)
        level = profile.skills.get(tag_id)
        if level == "confident":
            return TagResult(
                tag_type,
                tag_id,
                label,
                MET,
                phraser.fill("answers", "skill_confident", skill=label),
            )
        if level == "project":
            if HANDS_ON.search(sentence):
                return TagResult(
                    tag_type,
                    tag_id,
                    label,
                    PARTLY,
                    phraser.fill("answers", "skill_project_needs_experience", skill=label),
                )
            return TagResult(
                tag_type, tag_id, label, MET, phraser.fill("answers", "skill_project", skill=label)
            )
        if level == "course":
            return TagResult(
                tag_type,
                tag_id,
                label,
                PARTLY,
                phraser.fill("answers", "skill_course_only", skill=label),
            )
        related = [r for r in tax.related_skills(tag_id) if r in profile.skills]
        if related:
            best = max(
                related, key=lambda r: ("course", "project", "confident").index(profile.skills[r])
            )
            return TagResult(
                tag_type,
                tag_id,
                label,
                PARTLY,
                phraser.fill(
                    "answers", "skill_related", skill=label, related=tax.skills[best].label
                ),
            )
        if skill.course_covered and skill.portfolio_idea:
            gap = phraser.fill(
                "gaps", "course_skill_not_ticked", skill=label, idea=skill.portfolio_idea
            )
        else:
            gap = phraser.fill("gaps", "skill", skill=label)
        return TagResult(tag_type, tag_id, label, GAP, gap=gap)

    comp = tax.competencies[tag_id]
    label = comp.label
    senior = _senior_role(profile)
    if tag_id in LEADERSHIP_COMPETENCIES and senior and LEADERSHIP_REQ.search(sentence):
        _, ev = _best_role(profile, tag_id)
        own_ev = senior.competencies.get(tag_id) or ev or ""
        return TagResult(
            tag_type,
            tag_id,
            label,
            MET,
            phraser.leadership(label, senior.title, senior.seniority, own_ev),
            evidence_role=senior.title,
        )
    role, ev = _best_role(profile, tag_id)
    if role and ev.strip():
        return TagResult(
            tag_type,
            tag_id,
            label,
            MET,
            phraser.competency(label, role.title, ev),
            evidence_role=role.title,
        )
    if role:
        return TagResult(
            tag_type,
            tag_id,
            label,
            PARTLY,
            phraser.fill(
                "answers",
                "competency_without_evidence",
                requirement=label,
                role=_role_with_article(role),
            ),
            evidence_role=role.title,
        )
    key = "sector" if comp.category == "sector" else "competency"
    return TagResult(tag_type, tag_id, label, GAP, gap=phraser.fill("gaps", key, requirement=label))


def _role_with_article(role: Role) -> str:
    from skillmatch.phrasing import role_phrase

    return role_phrase(role.title)


def _combine(sentence: str, results: list[TagResult]) -> str:
    statuses = [t.status for t in results]
    if DISJUNCTIVE.search(sentence):
        return max(statuses, key=lambda s: RANK[s])
    if all(s == MET for s in statuses):
        return MET
    if all(s == GAP for s in statuses):
        return GAP
    return PARTLY


def evaluate_requirement(req: dict, profile: Profile, tax: Taxonomy, phraser: Phraser) -> Coverage:
    sentence = req["evidence_sentence"]
    tags = list(dict.fromkeys(tuple(t) for t in req.get("tags", [])))
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
    if not tags:
        return cov
    cov.tags = [evaluate_tag(t, i, sentence, profile, tax, phraser) for t, i in tags]
    cov.status = _combine(sentence, cov.tags)
    return cov


def data_gate(vacancy: dict, profile: Profile) -> tuple[str, float]:
    """(gate, gap in years). Gate: ok | waived | small | stretch | not_yet."""
    demand = vacancy.get("data_years")
    if demand is None or (isinstance(demand, float) and math.isnan(demand)):
        return "ok", 0.0
    gap = float(demand) - float(profile.data_years or 0)
    if gap <= 0:
        return "ok", 0.0
    years = math.ceil(gap - 1e-9)
    if years <= config.DATA_GAP_SMALL:
        signals = vacancy.get("entry_signals") or []
        welcoming = bool(signals) or vacancy.get("degree") == "or_equivalent"
        return ("waived" if welcoming else "small"), gap
    if years <= config.DATA_GAP_STRETCH:
        return "stretch", gap
    return "not_yet", gap


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
    ]
    essentials = [c for c in coverage if c.strength == "essential" and c.counts]
    e_gaps = [c for c in essentials if c.status == GAP]
    e_partly = [c for c in essentials if c.status == PARTLY]
    desirable_met = sum(1 for c in coverage if c.strength == "desirable" and c.status == MET)
    # Inferred requirements can raise a match (never sink one): fully met ones count towards
    # the minimum number of essentials a Strong fit needs.
    inferred_met = sum(
        1
        for c in coverage
        if c.strength == "essential" and c.confidence == "inferred" and c.status == MET
    )

    gate, gap_years = data_gate(vacancy, profile)
    n_gaps = len(e_gaps) + (1 if gate == "small" else 0)

    if gate == "not_yet" or n_gaps >= config.NOT_YET_MIN_GAPS:
        tier = NOT_YET
    elif gate == "stretch" or n_gaps >= config.STRETCH_MIN_GAPS:
        tier = STRETCH
    elif n_gaps >= 1:
        tier = GOOD
    elif len(essentials) + inferred_met < config.STRONG_MIN_ESSENTIALS:
        tier = GOOD  # too little to check: never call it a strong fit
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
    if gate != "ok":
        key = {
            "waived": "data_years_waived",
            "small": "data_years_small_gap",
            "stretch": "data_years_stretch",
            "not_yet": "data_years_not_yet",
        }[gate]
        reasons.append(
            phraser.fill(
                "reasons",
                key,
                years=years_text(vacancy.get("data_years")),
                user_years=years_text(profile.data_years),
            )
        )
    if vacancy.get("degree") == "required" and not profile.has_degree:
        reasons.append(phraser.fill("reasons", "degree_warning"))
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
        data_gate=gate,
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
