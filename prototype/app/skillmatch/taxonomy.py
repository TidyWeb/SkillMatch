"""Load, validate and query the reviewable taxonomy in data/taxonomy/.

Validation runs on every load and reports every problem it finds at once, naming the file and
entry, so a non-technical reviewer can fix a YAML edit from the error message alone.

    python -m skillmatch.taxonomy validate
"""

from __future__ import annotations

import logging
import re
import string
import sys
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml
from rapidfuzz import fuzz, process

from skillmatch import config

HEADER = "# DRAFT: for team review"
LOG = logging.getLogger(__name__)
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
SKILL_CATEGORIES = {
    "programming",
    "database",
    "bi",
    "spreadsheet",
    "analysis",
    "data_engineering",
    "platform",
    "business_system",
    "ways_of_working",
    "governance",
}
COMPETENCY_CATEGORIES = {"core", "sector"}
SENIORITY = ["individual", "supervisor", "manager", "senior_manager", "director"]
PLACEHOLDERS = {
    "requirement",
    "role",
    "evidence",
    "quote",
    "seniority",
    "skill",
    "related",
    "idea",
    "years",
    "level",
    "user_years",
    "n",
    "items",
    "signals",
}
REQUIRED_PHRASING = {
    "answers": {
        "skill_confident",
        "skill_project",
        "skill_commercial_experience",
    },
    "gaps": {"skill", "competency", "sector"},
    "reasons": {
        "all_essentials_answered",
        "essential_gaps",
        "essential_partly",
        "no_essentials_found",
        "few_essentials_found",
        "entry_signals",
        "desirable_answered",
    },
    "tiers": {"strong", "good", "stretch", "not_yet"},
}


class TaxonomyError(ValueError):
    """Raised with a readable list of every problem found in the taxonomy files."""


@dataclass(frozen=True)
class Skill:
    id: str
    label: str
    category: str
    course_covered: bool
    patterns: tuple[re.Pattern, ...]
    portfolio_idea: str | None = None


@dataclass(frozen=True)
class Competency:
    id: str
    label: str
    category: str
    description: str
    patterns: tuple[re.Pattern, ...]
    not_patterns: tuple[re.Pattern, ...] = ()


@dataclass(frozen=True)
class Archetype:
    id: str
    label: str
    aliases: tuple[str, ...]
    competencies: tuple[str, ...]
    example_evidence: str


@dataclass
class Taxonomy:
    skills: dict[str, Skill]
    competencies: dict[str, Competency]
    archetypes: dict[str, Archetype]
    families: dict[str, tuple[str, ...]]
    phrasing: dict[str, dict[str, str]]
    _family_of: dict[str, set[str]] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        for members in self.families.values():
            for m in members:
                self._family_of.setdefault(m, set()).update(x for x in members if x != m)

    def related_skills(self, skill_id: str) -> set[str]:
        """Skills in the same family, which partly satisfy each other."""
        return self._family_of.get(skill_id, set())

    def tag(self, text: str) -> list[tuple[str, str]]:
        """Return (tag_type, tag_id) for every skill and competency the text signals."""
        tags: list[tuple[str, str]] = []
        for s in self.skills.values():
            if any(p.search(text) for p in s.patterns):
                tags.append(("skill", s.id))
        for c in self.competencies.values():
            if any(p.search(text) for p in c.patterns) and not any(
                p.search(text) for p in c.not_patterns
            ):
                tags.append(("competency", c.id))
        return tags

    def match_archetype(self, title: str, cutoff: float = 75) -> tuple[str, float] | None:
        """Fuzzy-match a typed job title to an archetype id."""
        title = (title or "").strip()
        if not title:
            return None
        choices = {}
        for a in self.archetypes.values():
            for name in (a.label, *a.aliases):
                choices[name.lower()] = a.id
        hit = process.extractOne(
            title.lower(), list(choices), scorer=fuzz.token_set_ratio, score_cutoff=cutoff
        )
        if not hit:
            return None
        return choices[hit[0]], hit[1]

    def label(self, tag_type: str, tag_id: str) -> str:
        table = self.skills if tag_type == "skill" else self.competencies
        return table[tag_id].label


# ---------- pattern compilation ----------


def compile_variant(text: str, case_sensitive: bool = False) -> re.Pattern:
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(r"(?<!\w)" + re.escape(text) + r"(?!\w)", flags)


def compile_phrase(phrase: str) -> re.Pattern:
    """Phrase mini-language: `*` lets a word continue; `...` allows up to four words between."""
    parts: list[str] = []
    gap_next = False
    for token in phrase.split():
        if token == "...":
            gap_next = True
            continue
        piece = re.escape(token[:-1]) + r"\w*" if token.endswith("*") else re.escape(token)
        if parts:
            parts.append(r"(?:\s+\S+){0,4}?\s+" if gap_next else r"[\s-]+")
        parts.append(piece)
        gap_next = False
    return re.compile(r"(?<!\w)" + "".join(parts) + r"(?!\w)", re.IGNORECASE)


# ---------- loading and validation ----------


def _read(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        errors.append(f"{path.name}: file is missing")
        return {}
    text = path.read_text(encoding="utf-8")
    if path.name != "archetype_groups_v2.yaml" and not text.startswith(HEADER):
        errors.append(f'{path.name}: the first line must be "{HEADER}"')
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        where = f" near line {mark.line + 1}" if mark else ""
        errors.append(f"{path.name}: not valid YAML{where} ({getattr(exc, 'problem', exc)})")
        return {}
    if not isinstance(data, dict):
        errors.append(f"{path.name}: expected named sections at the top level")
        return {}
    return data


def _entries(
    data: dict, key: str, fname: str, errors: list[str], required: set, optional: set
) -> list[dict]:
    items = data.get(key)
    if not isinstance(items, list):
        errors.append(f"{fname}: missing the '{key}:' list")
        return []
    seen: set[str] = set()
    good = []
    for n, item in enumerate(items, 1):
        if not isinstance(item, dict):
            errors.append(f"{fname}: item {n} under '{key}' is not a set of fields")
            continue
        ident = item.get("id", f"item {n}")
        where = f"{fname}, entry '{ident}'"
        missing = required - item.keys()
        if missing:
            errors.append(f"{where}: missing field(s) {', '.join(sorted(missing))}")
        unknown = item.keys() - required - optional
        if unknown:
            errors.append(
                f"{where}: unknown field(s) {', '.join(sorted(unknown))} (check spelling)"
            )
        if not isinstance(ident, str) or not ID_RE.match(ident):
            errors.append(f"{where}: id must be lower_snake_case letters, digits and _")
        elif ident in seen:
            errors.append(f"{where}: id is used twice")
        seen.add(str(ident))
        if not missing:
            good.append(item)
    return good


def _str_list(value, where: str, field_name: str, errors: list[str]) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
        errors.append(f"{where}: '{field_name}' must be a list of non-empty text items")
        return []
    return value


def _load_skills(data: dict, errors: list[str]) -> tuple[dict, dict]:
    fname = "technical_skills.yaml"
    skills: dict[str, Skill] = {}
    for item in _entries(
        data,
        "skills",
        fname,
        errors,
        {"id", "label", "category", "course_covered"},
        {"variants", "variants_cs", "regex", "portfolio_idea"},
    ):
        where = f"{fname}, entry '{item['id']}'"
        if item["category"] not in SKILL_CATEGORIES:
            errors.append(
                f"{where}: category '{item['category']}' is not one of "
                f"{', '.join(sorted(SKILL_CATEGORIES))}"
            )
        if not isinstance(item["course_covered"], bool):
            errors.append(f"{where}: course_covered must be true or false")
        patterns = [
            compile_variant(v) for v in _str_list(item.get("variants"), where, "variants", errors)
        ]
        patterns += [
            compile_variant(v, case_sensitive=True)
            for v in _str_list(item.get("variants_cs"), where, "variants_cs", errors)
        ]
        for rx in _str_list(item.get("regex"), where, "regex", errors):
            try:
                patterns.append(re.compile(rx))
            except re.error as exc:
                errors.append(f"{where}: regex '{rx}' is invalid ({exc})")
        if not patterns:
            errors.append(f"{where}: needs at least one of variants, variants_cs or regex")
        if item["course_covered"] is True and not item.get("portfolio_idea"):
            errors.append(f"{where}: course-covered skills need a portfolio_idea")
        skills[item["id"]] = Skill(
            id=item["id"],
            label=str(item["label"]),
            category=item["category"],
            course_covered=bool(item["course_covered"]),
            patterns=tuple(patterns),
            portfolio_idea=item.get("portfolio_idea"),
        )
    families: dict[str, tuple[str, ...]] = {}
    for fam in _entries(data, "families", fname, errors, {"id", "label", "members"}, set()):
        where = f"{fname}, family '{fam['id']}'"
        members = _str_list(fam["members"], where, "members", errors)
        for m in members:
            if m not in skills:
                errors.append(f"{where}: member '{m}' is not a skill id")
        if len(members) < 2:
            errors.append(f"{where}: a family needs at least two members")
        families[fam["id"]] = tuple(members)
    return skills, families


def _load_competencies(data: dict, errors: list[str]) -> dict:
    fname = "competencies.yaml"
    out: dict[str, Competency] = {}
    for item in _entries(
        data,
        "competencies",
        fname,
        errors,
        {"id", "label", "category", "description", "phrases"},
        {"not_phrases"},
    ):
        where = f"{fname}, entry '{item['id']}'"
        if item["category"] not in COMPETENCY_CATEGORIES:
            errors.append(f"{where}: category must be core or sector")
        phrases = _str_list(item["phrases"], where, "phrases", errors)
        if not phrases:
            errors.append(f"{where}: needs at least one phrase")
        patterns = []
        for ph in phrases:
            if ph.strip().startswith("...") or ph.strip().endswith("..."):
                errors.append(f"{where}: phrase '{ph}' cannot start or end with ...")
                continue
            patterns.append(compile_phrase(ph))
        nots = [
            compile_phrase(ph)
            for ph in _str_list(item.get("not_phrases"), where, "not_phrases", errors)
        ]
        out[item["id"]] = Competency(
            id=item["id"],
            label=str(item["label"]),
            category=item["category"],
            description=str(item["description"]),
            patterns=tuple(patterns),
            not_patterns=tuple(nots),
        )
    return out


def _load_archetypes(data: dict, competencies: dict, errors: list[str]) -> dict:
    fname = "archetype_groups_v2.yaml"
    out: dict[str, Archetype] = {}
    for item in _entries(
        data,
        "groups",
        fname,
        errors,
        {"id", "label", "competencies", "example_evidence"},
        {"aliases", "lens_hints"},
    ):
        where = f"{fname}, entry '{item['id']}'"
        comps = _str_list(item["competencies"], where, "competencies", errors)
        known = []
        for c in comps:
            if c not in competencies:
                LOG.warning("%s: skipping unknown competency id '%s'", where, c)
            elif c not in known:
                known.append(c)
        if not known:
            errors.append(f"{where}: no known competencies")
        hints = item.get("lens_hints", {})
        if hints is not None and not isinstance(hints, dict):
            errors.append(f"{where}: 'lens_hints' must be a mapping")
        out[item["id"]] = Archetype(
            id=item["id"],
            label=str(item["label"]),
            aliases=tuple(_str_list(item.get("aliases"), where, "aliases", errors)),
            competencies=tuple(known),
            example_evidence=str(item["example_evidence"]),
        )
    return out


def _load_phrasing(data: dict, errors: list[str]) -> dict:
    fname = "phrasing.yaml"
    out: dict[str, dict[str, str]] = {}
    for section, keys in REQUIRED_PHRASING.items():
        block = data.get(section)
        if not isinstance(block, dict):
            errors.append(f"{fname}: missing the '{section}:' section")
            continue
        for k in sorted(keys - block.keys()):
            errors.append(f"{fname}: '{section}' is missing the template '{k}'")
        for k, tmpl in block.items():
            if not isinstance(tmpl, str):
                errors.append(f"{fname}, {section}.{k}: must be text")
                continue
            try:
                names = {f for _, f, _, _ in string.Formatter().parse(tmpl) if f}
            except ValueError as exc:
                errors.append(f"{fname}, {section}.{k}: braces don't match ({exc})")
                continue
            for name in sorted(names - PLACEHOLDERS):
                errors.append(f"{fname}, {section}.{k}: unknown placeholder {{{name}}}")
        out[section] = {k: v for k, v in block.items() if isinstance(v, str)}
    return out


def load_taxonomy(directory: Path | str | None = None) -> Taxonomy:
    directory = Path(directory or config.TAXONOMY_DIR)
    errors: list[str] = []
    skill_data = _read(directory / "technical_skills.yaml", errors)
    comp_data = _read(directory / "competencies.yaml", errors)
    arch_data = _read(directory / "archetype_groups_v2.yaml", errors)
    phrasing_data = _read(directory / "phrasing.yaml", errors)
    skills, families = _load_skills(skill_data, errors) if skill_data else ({}, {})
    competencies = _load_competencies(comp_data, errors) if comp_data else {}
    archetypes = _load_archetypes(arch_data, competencies, errors) if arch_data else {}
    phrasing = _load_phrasing(phrasing_data, errors) if phrasing_data else {}
    overlap = skills.keys() & competencies.keys()
    for ident in sorted(overlap):
        errors.append(f"'{ident}' is used as both a skill id and a competency id")
    if errors:
        raise TaxonomyError(
            "The taxonomy files have problems:\n" + "\n".join(f"  - {e}" for e in errors)
        )
    return Taxonomy(skills, competencies, archetypes, families, phrasing)


@lru_cache(maxsize=1)
def get_taxonomy() -> Taxonomy:
    """The project taxonomy, loaded once per process."""
    return load_taxonomy()


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] != ["validate"]:
        print("usage: python -m skillmatch.taxonomy validate [directory]")
        return 2
    try:
        tax = load_taxonomy(argv[1] if len(argv) > 1 else None)
    except TaxonomyError as exc:
        print(exc)
        return 1
    print(
        f"OK: {len(tax.skills)} skills in {len(tax.families)} families, "
        f"{len(tax.competencies)} competencies, {len(tax.archetypes)} areas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
