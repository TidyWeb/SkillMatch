"""The candidate profile: validated from the JSON the browser sends with each request.

The profile lives in the browser's sessionStorage. The server builds this object for one request
and forgets it. Nothing here is written to disk, logged or sent to analytics. The postcode is
reduced to its outward code ("B91") on arrival.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache

import yaml

from skillmatch import config
from skillmatch.geo import outward_code
from skillmatch.taxonomy import SENIORITY, Taxonomy, get_taxonomy

SKILL_LEVELS = ("course", "project", "confident")
TRAVEL = {
    "car": "Car",
    "motorbike": "Motorbike",
    "public_transport": "Public transport",
    "bike_walk": "Bike or walk",
}
DEGREES = {"none": "No degree", "bachelors": "Bachelor's", "masters": "Master's", "phd": "PhD"}
MAX_TEXT = 200
MAX_ROLES = 4


@dataclass
class Role:
    archetype: str | None
    title: str
    seniority: str = "individual"
    years: float = 0
    competencies: dict[str, str] = field(default_factory=dict)  # id -> evidence ("" = none)

    @property
    def rank(self) -> int:
        return SENIORITY.index(self.seniority)


@dataclass
class Profile:
    outcode: str | None = None
    travel: str | None = None
    max_miles: float | None = None
    include_remote: bool = True
    max_office_days: float = 5
    skills: dict[str, str] = field(default_factory=dict)  # id -> course | project | confident
    roles: list[Role] = field(default_factory=list)
    ci_diploma: bool = True
    degree: str = "none"
    other_qualifications: str = ""
    data_years: float = 0
    min_salary: float | None = None
    name: str | None = None  # demo personas only

    @property
    def has_degree(self) -> bool:
        return self.degree in ("bachelors", "masters", "phd")


def _text(value, limit: int = MAX_TEXT) -> str:
    return " ".join(str(value or "").split())[:limit]


def _number(value, lo: float, hi: float) -> float | None:
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return min(max(n, lo), hi)


def profile_from_dict(data: dict | None, tax: Taxonomy | None = None) -> Profile:
    """Build a Profile from untrusted input, keeping only known keys and values."""
    tax = tax or get_taxonomy()
    data = data if isinstance(data, dict) else {}
    p = Profile()
    p.outcode = outward_code(_text(data.get("postcode") or data.get("outcode"), 10))
    p.travel = data.get("travel") if data.get("travel") in TRAVEL else None
    p.max_miles = (
        _number(data.get("max_miles"), 1, 200) if data.get("max_miles") not in (None, "") else None
    )
    p.include_remote = data.get("include_remote") not in (False, "false", "no", "0", 0)
    days = _number(data.get("max_office_days"), 0, 5)
    p.max_office_days = 5 if days is None else days
    skills = data.get("skills") if isinstance(data.get("skills"), dict) else {}
    p.skills = {k: v for k, v in skills.items() if k in tax.skills and v in SKILL_LEVELS}
    roles = data.get("roles") if isinstance(data.get("roles"), list) else []
    for r in roles[:MAX_ROLES]:
        if not isinstance(r, dict):
            continue
        arch = r.get("archetype") if r.get("archetype") in tax.archetypes else None
        title = _text(r.get("title"), 80)
        if not arch and title:
            hit = tax.match_archetype(title)
            arch = hit[0] if hit else None
        if not arch and not title:
            continue
        comps = r.get("competencies") if isinstance(r.get("competencies"), dict) else {}
        p.roles.append(
            Role(
                archetype=arch,
                title=title or tax.archetypes[arch].label,
                seniority=r.get("seniority") if r.get("seniority") in SENIORITY else "individual",
                years=_number(r.get("years"), 0, 60) or 0,
                competencies={
                    c: _text(ev)
                    for c, ev in comps.items()
                    if c in tax.competencies and isinstance(ev, str | type(None))
                },
            )
        )
    quals = data.get("qualifications") if isinstance(data.get("qualifications"), dict) else {}
    p.ci_diploma = quals.get("ci_diploma", True) not in (False, "false", "no", 0)
    p.degree = quals.get("degree") if quals.get("degree") in DEGREES else "none"
    p.other_qualifications = _text(quals.get("other"))
    p.data_years = _number(data.get("data_years"), 0, 40) or 0
    p.min_salary = (
        _number(data.get("min_salary"), 0, 500000)
        if data.get("min_salary") not in (None, "")
        else None
    )
    p.name = _text(data.get("name"), 60) or None
    return p


def profile_from_json(text: str | None, tax: Taxonomy | None = None) -> Profile | None:
    if not text:
        return None
    try:
        data = json.loads(text)
    except (TypeError, ValueError):
        return None
    return profile_from_dict(data, tax) if isinstance(data, dict) else None


@lru_cache(maxsize=1)
def personas() -> dict[str, dict]:
    """Demo personas from data/personas.yaml, keyed by id, as profile dictionaries."""
    data = yaml.safe_load((config.DATA_DIR / "personas.yaml").read_text())
    return {p["id"]: p["profile"] for p in data["personas"]}


@lru_cache(maxsize=1)
def persona_cards() -> list[dict]:
    data = yaml.safe_load((config.DATA_DIR / "personas.yaml").read_text())
    return [{k: p[k] for k in ("id", "button", "summary")} for p in data["personas"]]
