"""Turn a profile and the database snapshot into a shortlist: matches, filters and hidden counts.

Shared by the web app, the calibration script and the analysis notebook.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from urllib.parse import quote, quote_plus

from skillmatch.geo import Geocoder, town_table
from skillmatch.match import TIER_ORDER, MatchResult, match_vacancy
from skillmatch.phrasing import Phraser
from skillmatch.profile import Profile
from skillmatch.repository import Snapshot, discovery_links
from skillmatch.taxonomy import get_taxonomy

SOURCE_TIERS = {"A": "Automated feeds", "B": "Checked by hand", "fixture": "Synthetic fixtures"}
HIDDEN_LABELS = {
    "senior role": "senior roles hidden",
    "not a data role": "non-data roles hidden",
    "training course, not a job": "training courses posing as jobs hidden",
    "outside the West Midlands": "jobs outside the West Midlands hidden",
    "remote role not open to UK applicants": "remote roles closed to UK applicants hidden",
    "details not fetched (request cap reached)": "adverts we couldn't read in full hidden",
    "too far": "beyond your maximum distance",
    "remote": "UK-remote roles hidden (you chose not to include them)",
    "office days": "need more office days than you want",
    "salary": "pay below your minimum salary",
}


@dataclass
class Filters:
    max_miles: float | None = None
    tiers: set[str] = field(default_factory=lambda: set(TIER_ORDER))
    arrangement: str = "any"  # any | onsite | hybrid | remote
    salary_stated: bool = False
    source_tier: str = "any"  # any | A | B | fixture
    reveal: set[str] = field(default_factory=set)  # excluded reasons the user chose to show


@dataclass
class Shortlist:
    results: list[MatchResult]
    by_tier: dict[str, list[MatchResult]]
    hidden: Counter
    revealed: list[MatchResult]
    home: tuple[float, float] | None
    town: str | None
    total_considered: int

    @property
    def count(self) -> int:
        return len(self.results)


def home_place(profile: Profile, geocoder: Geocoder | None = None):
    if not profile.outcode:
        return None
    return (geocoder or Geocoder(offline=True)).locate_outcode(profile.outcode)


def nearest_town(lat: float, lon: float) -> str | None:
    from skillmatch.geo import haversine_miles

    best, best_d = None, None
    for name, p in town_table().items():
        if p.approximate or p.region != "West Midlands" or "(" in name:
            continue
        d = haversine_miles(lat, lon, p.lat, p.lon)
        if best_d is None or d < best_d:
            best, best_d = name, d
    return town_names().get(best) if best else None


@lru_cache(maxsize=1)
def town_names() -> dict[str, str]:
    """Lower-case key -> the place name as written ("stoke-on-trent" -> "Stoke-on-Trent")."""
    import csv

    from skillmatch import config

    with (config.DATA_DIR / "town_coords.csv").open() as f:
        return {r["name"].lower(): r["name"] for r in csv.DictReader(f)}


def _salary_annual_max(v: dict) -> float | None:
    if v.get("salary_period") != "annum" or v.get("currency") not in (None, "GBP"):
        return None
    return v.get("salary_max") or v.get("salary_min")


def build_shortlist(
    profile: Profile,
    snap: Snapshot,
    filters: Filters | None = None,
    geocoder: Geocoder | None = None,
) -> Shortlist:
    filters = filters or Filters()
    tax = get_taxonomy()
    phraser = Phraser(tax)
    place = home_place(profile, geocoder)
    home = (place.lat, place.lon) if place else None
    town = nearest_town(*home) if home else None
    max_miles = filters.max_miles if filters.max_miles is not None else profile.max_miles

    hidden: Counter = Counter()
    results: list[MatchResult] = []
    revealed: list[MatchResult] = []
    considered = 0
    for v in snap.vacancies.values():
        if not v["is_primary"]:
            continue
        reason = v["excluded_reason"]
        if reason:
            hidden[reason] += 1
            if reason not in filters.reveal:
                continue
        considered += 1
        m = match_vacancy(
            profile, v, snap.requirements.get(v["vacancy_id"], []), home, tax, phraser
        )
        if v["is_remote"] and not profile.include_remote:
            hidden["remote"] += 1
            continue
        if max_miles is not None and m.distance_miles is not None and m.distance_miles > max_miles:
            hidden["too far"] += 1
            continue
        if (
            v["arrangement"] == "hybrid"
            and v["office_days_min"] is not None
            and v["office_days_min"] > profile.max_office_days
        ):
            hidden["office days"] += 1
            continue
        annual = _salary_annual_max(v)
        if profile.min_salary and annual is not None and annual < profile.min_salary:
            hidden["salary"] += 1
            continue
        if filters.arrangement != "any" and v["arrangement"] != filters.arrangement:
            continue
        if filters.salary_stated and not v["salary_stated"]:
            continue
        if filters.source_tier != "any" and v["source_tier"] != filters.source_tier:
            continue
        if m.tier not in filters.tiers:
            continue
        (revealed if reason else results).append(m)

    def sort_key(m: MatchResult):
        return (m.distance_miles is None, m.distance_miles or 0, m.vacancy["title"])

    results.sort(key=sort_key)
    revealed.sort(key=sort_key)
    by_tier = {t: [m for m in results if m.tier == t] for t in TIER_ORDER}
    return Shortlist(results, by_tier, hidden, revealed, home, town, considered)


# ---------- Tier C: discovery links ----------

TYPE_LABELS = {
    "ats_discovery": "Applicant tracking systems",
    "aggregator": "Aggregators",
    "charity_employer": "Charity employers",
    "council_watch": "Councils",
    "direct_employer": "Employers",
    "general_board": "General job boards",
    "graduate_board": "Graduate job boards",
    "housing_employer": "Housing associations",
    "public_employer": "Public employers",
    "public_portal": "Public job portals",
    "recruitment_agency": "Recruitment agencies",
    "remote_board": "Remote job boards",
    "remote_employer": "Remote-first employers",
    "sector_board": "Sector job boards",
    "specialist_board": "Specialist tech and data boards",
}


def _slug(text: str, title: bool = False) -> str:
    words = re.findall(r"[A-Za-z0-9]+", text)
    words = [w.capitalize() for w in words] if title else [w.lower() for w in words]
    return "-".join(words)


def build_discovery_links(
    town: str | None, radius: float | None, term: str = "data analyst"
) -> dict[str, list[dict]]:
    """Links grouped by source type, pre-filled with the user's town and a data search term."""
    town = town or "Birmingham"
    radius_value = int(radius) if radius else 15
    values = {
        "term": quote_plus(term),
        "term_slug": _slug(term),
        "term_title_slug": _slug(term, title=True),
        "town": quote_plus(town),
        "town_slug": _slug(town),
        "town_title_slug": _slug(town, title=True),
        "radius": str(radius_value),
    }
    groups: dict[str, list[dict]] = {}
    for row in discovery_links():
        url = row["url_template"]
        try:
            url = url.format(**values)
        except (KeyError, IndexError):
            url = row["url_template"]
        groups.setdefault(row["type"], []).append(
            {
                "name": row["name"],
                "url": quote(url, safe=":/?&=%+#,-_.~"),
                "prefilled": row["prefilled"] == "true",
                "notes": row["notes"],
            }
        )
    return {
        TYPE_LABELS.get(k, k.replace("_", " ").capitalize()): v for k, v in sorted(groups.items())
    }
