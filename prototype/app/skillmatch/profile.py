"""Request-scoped, validated candidate profile."""

from __future__ import annotations

import json
import logging
import math
import re
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import combinations

import yaml

from skillmatch import config
from skillmatch.geo import outward_code
from skillmatch.taxonomy import Taxonomy, get_taxonomy

TRAVEL = {
    "car": "Car",
    "motorbike": "Motorbike",
    "public_transport": "Public transport",
    "bike_walk": "Bike or walk",
}
QUALIFICATIONS = {
    0: "No formal qualifications",
    2: "GCSE or O level – Level 2",
    3: "A level – Level 3",
    5: "HNC, HND or foundation degree – Level 4–5",
    6: "Bachelor's degree – Level 6",
    7: "Master's degree – Level 7",
    8: "PhD or doctorate – Level 8",
}
SKILL_LEVELS = ("course", "project", "confident")
MAX_AREAS = 5
MAX_TEXT = 200
LOG = logging.getLogger(__name__)


def _course_skills():
    return [s.id for s in get_taxonomy().skills.values() if s.course_covered]


@dataclass
class Area:
    id: str
    skills: list[str] = field(default_factory=list)


@dataclass
class Profile:
    outcode: str | None = None
    travel: str | None = None
    max_miles: float | None = None
    include_remote: bool = True
    max_office_days: float = 5
    skills: list[str] = field(default_factory=_course_skills)
    skill_levels: dict[str, str] = field(default_factory=dict)
    areas: list[Area] = field(default_factory=list)
    highest_qualification: int = 0

    @property
    def has_degree(self) -> bool:
        return self.highest_qualification >= 6


def _text(value, limit=MAX_TEXT):
    return " ".join(str(value or "").split())[:limit]


def _number(value, lo, hi):
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(n):
        return None
    return min(max(n, lo), hi)


def profile_from_dict(data: dict | None, tax: Taxonomy | None = None) -> Profile:
    tax = tax or get_taxonomy()
    data = data if isinstance(data, dict) else {}
    p = Profile()
    p.outcode = outward_code(_text(data.get("postcode") or data.get("outcode"), 10))
    travel = data.get("travel")
    p.travel = travel if isinstance(travel, str) and travel in TRAVEL else None
    p.max_miles = (
        _number(data.get("max_miles"), 1, 200) if data.get("max_miles") not in (None, "") else None
    )
    p.include_remote = data.get("include_remote") not in (False, "false", "no", "0", 0)
    days = _number(data.get("max_office_days"), 0, 5)
    p.max_office_days = 5 if days is None else days
    raw_skills = data.get("skills")
    course = [s.id for s in tax.skills.values() if s.course_covered]
    added = (
        [
            s
            for s in raw_skills
            if isinstance(s, str) and s in tax.skills and not tax.skills[s].course_covered
        ]
        if isinstance(raw_skills, list)
        else []
    )
    p.skills = list(dict.fromkeys(course + added))
    raw_levels = data.get("skill_levels")
    if isinstance(raw_levels, dict):
        p.skill_levels = {
            skill_id: level
            for skill_id in p.skills
            if (level := raw_levels.get(skill_id)) in SKILL_LEVELS
        }
    else:
        p.skill_levels = {
            skill_id: "course"
            for skill_id in p.skills
            if tax.skills[skill_id].course_covered
        }
    raw_areas = data.get("areas") if isinstance(data.get("areas"), list) else []
    seen = set()
    for raw in raw_areas:
        if not isinstance(raw, dict):
            continue
        area_id = raw.get("id")
        if not isinstance(area_id, str) or area_id not in tax.archetypes or area_id in seen:
            continue
        seen.add(area_id)
        valid = set(tax.archetypes[area_id].competencies)
        # Missing skills means preselect all area skills. An explicit [] means none.
        selected = raw.get("skills", list(valid))
        if not isinstance(selected, list):
            selected = []
        p.areas.append(
            Area(
                area_id,
                list(dict.fromkeys(s for s in selected if isinstance(s, str) and s in valid)),
            )
        )
        if len(p.areas) >= MAX_AREAS:
            break
    q = data.get("highest_qualification", 0)
    if isinstance(q, bool):
        q = 0
    elif isinstance(q, int):
        pass
    elif isinstance(q, str) and re.fullmatch(r"(?:0|2|3|5|6|7|8)", q.strip()):
        q = int(q.strip())
    else:
        q = 0
    p.highest_qualification = q if q in QUALIFICATIONS else 0
    return p


def profile_from_json(text: str | None, tax: Taxonomy | None = None) -> Profile | None:
    if not text:
        return None
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return None
    return profile_from_dict(data, tax) if isinstance(data, dict) else None


def areas_for_competencies(competencies, tax: Taxonomy) -> tuple[list[dict], list[str]]:
    """Represent legacy ticks with at most five areas, preserving every possible tick.

    Greedy overlap can fill all five slots while missing a skill another combination covers.
    This bounded set-cover search is only used by fixture/report conversion, not web requests.
    """
    wanted = set(competencies) & tax.competencies.keys()
    ids = sorted(wanted)
    bits = {cid: 1 << i for i, cid in enumerate(ids)}
    candidates = [
        (a, sum(bits[c] for c in set(a.competencies) & wanted))
        for a in tax.archetypes.values()
        if set(a.competencies) & wanted
    ]
    candidates.sort(key=lambda item: (-item[1].bit_count(), item[0].id))
    full = (1 << len(ids)) - 1
    best, best_mask = (), 0
    for count in range(1, min(MAX_AREAS, len(candidates)) + 1):
        for chosen in combinations(candidates, count):
            mask = 0
            for _, value in chosen:
                mask |= value
            if mask.bit_count() > best_mask.bit_count():
                best, best_mask = chosen, mask
            if mask == full:
                best = chosen
                return (
                    [
                        {"id": a.id, "skills": [c for c in a.competencies if c in wanted]}
                        for a, _ in best
                    ],
                    [],
                )
    return (
        [{"id": a.id, "skills": [c for c in a.competencies if c in wanted]} for a, _ in best],
        [cid for cid in ids if not best_mask & bits[cid]],
    )


@lru_cache(maxsize=1)
def personas() -> dict[str, dict]:
    """Legacy fixtures converted in memory; public profile validation ignores roles."""
    data = yaml.safe_load((config.DATA_DIR / "personas.yaml").read_text())
    tax = get_taxonomy()
    out = {}
    for item in data["personas"]:
        old = item["profile"]
        skills = [
            k
            for k, v in old.get("skills", {}).items()
            if k in tax.skills and v in ("course", "project", "confident")
        ]
        comps = {
            c
            for role in old.get("roles", [])
            for c in role.get("competencies", {})
            if c in tax.competencies
        }
        areas, remaining = areas_for_competencies(comps, tax)
        if remaining:
            LOG.warning(
                "Legacy persona %s has competencies that have no v2 area mapping: %s",
                item["id"],
                sorted(remaining),
            )
        degree = {"none": 0, "bachelors": 6, "masters": 7, "phd": 8}.get(
            old.get("qualifications", {}).get("degree"), 0
        )
        out[item["id"]] = {
            **{
                k: old[k]
                for k in (
                    "postcode",
                    "outcode",
                    "travel",
                    "max_miles",
                    "include_remote",
                    "max_office_days",
                )
                if k in old
            },
            "skills": skills,
            "areas": areas,
            "highest_qualification": degree,
        }
    return out


@lru_cache(maxsize=1)
def persona_cards() -> list[dict]:
    data = yaml.safe_load((config.DATA_DIR / "personas.yaml").read_text())
    return [{k: p[k] for k in ("id", "button", "summary")} for p in data["personas"]]
