"""Post-matching tier guards. Pure evaluation: web requests write no profile or log files."""

from __future__ import annotations

import re
from dataclasses import dataclass, field, fields

from skillmatch.match import GOOD, STRONG, MatchResult
from skillmatch.phrasing import Phraser
from skillmatch.profile import Profile
from skillmatch.taxonomy import Taxonomy, get_taxonomy

OPTIONAL = re.compile(
    r"\b(advantageous|a plus|ideally|beneficial|prefer(?:red|able)|desirable|optional|"
    r"not required|not essential|not needed|nice[- ]to[- ]have|helpful)\b",
    re.I,
)


@dataclass(frozen=True)
class GuardFinding:
    req_id: str
    missing_skills: tuple[str, ...]
    requirement_text: str


@dataclass
class GuardedMatch(MatchResult):
    guard_reason: str | None = None
    guard_findings: list[GuardFinding] = field(default_factory=list)


def _label(skill, text: str) -> str:
    if skill.id == "azure" and re.search(r"\bfabric\b", text, re.I):
        return (
            "Azure / Microsoft Fabric"
            if re.search(r"\bazure\b", text, re.I)
            else "Microsoft Fabric"
        )
    return skill.label


@dataclass(frozen=True)
class _Mention:
    start: int
    end: int
    ids: tuple[str, ...]


_ALTERNATIVE = re.compile(
    r"\s*(?:(?:skills?|experience|knowledge|expertise|tools?)\s*)?"
    r"(?:or|and/or|/)\s*(?:(?:experience|knowledge|skills)\s+(?:with|of|using)\s*)?",
    re.I,
)
_GENERIC = re.compile(
    r"\s*(?:,\s*)?or\s+(?:(?:a|an)\s+)?(?:similar|equivalent|comparable|other)\b"
    r"(?:(?!,|;|[.!?]|\band\b|\balongside\b).)*",
    re.I,
)


def _mentions(text: str, tax: Taxonomy) -> list[_Mention]:
    spans = {}
    for skill in tax.skills.values():
        for pattern in skill.patterns:
            for hit in pattern.finditer(text):
                spans.setdefault(hit.span(), set()).add(skill.id)
    # A generic "database" inside "Oracle database" is not a separate alternative to Oracle.
    return [
        _Mention(start, end, tuple(sorted(ids)))
        for (start, end), ids in sorted(spans.items())
        if not any(a <= start and b >= end and (a, b) != (start, end) for a, b in spans)
    ]


def _missing_groups(text: str, selected: set[str], tax: Taxonomy) -> list[str]:
    mentions = _mentions(text, tax)
    if not mentions:
        return []
    # Only contiguous tool lists connected by OR become alternatives. AND and descriptive
    # text break a group, so "Fabric or Azure, alongside SQL and ETL" keeps separate asks.
    parent = list(range(len(mentions)))

    def root(index):
        while parent[index] != index:
            index = parent[index]
        return index

    def join(a, b):
        parent[root(b)] = root(a)

    for i in range(len(mentions) - 1):
        gap = text[mentions[i].end : mentions[i + 1].start]
        if _ALTERNATIVE.fullmatch(gap):
            join(i, i + 1)
            j = i - 1
            while j >= 0 and re.fullmatch(
                r"\s*,\s*", text[mentions[j].end : mentions[j + 1].start]
            ):
                join(j, i)
                j -= 1
    groups = {}
    for i, mention in enumerate(mentions):
        groups.setdefault(root(i), []).append(mention)
    missing = []
    descriptor_end = -1
    categories = {tax.skills[sid].category for sid in selected if sid in tax.skills}
    for group in sorted(groups.values(), key=lambda g: g[0].start):
        if group[0].start < descriptor_end:
            continue
        end = group[-1].end
        ids = set(sid for mention in group for sid in mention.ids)
        generic = _GENERIC.match(text, end)
        if generic:
            descriptor_end = generic.end()
        if ids & selected:
            continue
        group_text = text[group[0].start : end]
        labels = list(
            dict.fromkeys(
                _label(tax.skills[sid], group_text) for mention in group for sid in mention.ids
            )
        )
        if generic:
            kinds = {tax.skills[sid].category for sid in ids}
            if kinds & categories:
                continue
            category = " / ".join(sorted(kind.replace("_", " ") for kind in kinds))
            missing.append(f"a {category} skill ({' / '.join(labels)} or similar)")
        else:
            missing.append(" / ".join(labels))
    return missing


def apply_tier_guard(
    result: MatchResult, profile: Profile, tax: Taxonomy | None = None
) -> GuardedMatch:
    """Only cap Strong at Good when a non-desirable requirement names a missing tool.

    Confidence (stated/inferred) and the matcher's aggregate requirement status are irrelevant.
    Retain the original matcher result, including its coverage and reasons, without mutation.
    """
    if isinstance(result, GuardedMatch):
        return result
    guarded = GuardedMatch(
        **{item.name: getattr(result, item.name) for item in fields(MatchResult)}
    )
    if result.tier != STRONG:
        return guarded
    tax = tax or get_taxonomy()
    selected = set(profile.skills)
    for requirement in result.coverage:
        if requirement.strength == "desirable":
            continue
        missing = []
        # Distinct clauses may mark a different tool as optional. Comma-separated tool lists
        # stay together so a trailing "would be beneficial" applies to the whole list.
        for clause in re.split(r";|[.!?](?:\s|$)|\bbut\b", requirement.sentence, flags=re.I):
            if OPTIONAL.search(clause):
                continue
            missing.extend(_missing_groups(clause, selected, tax))
        if missing:
            guarded.guard_findings.append(
                GuardFinding(
                    requirement.req_id, tuple(dict.fromkeys(missing)), requirement.sentence
                )
            )
    if guarded.guard_findings:
        names = dict.fromkeys(
            name for finding in guarded.guard_findings for name in finding.missing_skills
        )
        guarded.tier = GOOD
        guarded.tier_label = Phraser(tax).tier_label(GOOD)
        guarded.guard_reason = "Capped at Good match: advert asks for " + ", ".join(names)
    return guarded
