"""Aggregates for the insights page and the notebook. Every figure carries its n."""

from __future__ import annotations

import re
from collections import Counter

from skillmatch.match import TIER_ORDER
from skillmatch.profile import Profile
from skillmatch.repository import Snapshot
from skillmatch.results import Filters, build_shortlist
from skillmatch.taxonomy import get_taxonomy

JUNIOR_TITLE = re.compile(
    r"\b(junior|graduate|entry[\s-]level|trainee|apprentice|assistant)\b", re.I
)
SALARY_BANDS = [
    (0, 20000),
    (20000, 25000),
    (25000, 30000),
    (30000, 35000),
    (35000, 40000),
    (40000, 50000),
    (50000, 10**9),
]
DISTANCE_BANDS = [(0, 5), (5, 10), (10, 20), (20, 30), (30, 50), (50, 10**6)]


ARRANGEMENT_LABELS = {
    "onsite": "On site",
    "hybrid": "Hybrid",
    "remote": "Remote",
    "unknown": "Not stated",
}


def spread_points(points: list[dict]) -> list[dict]:
    """Nudge markers that share exact coordinates (a town centre) into a small ring so each can
    be seen and clicked. The offset is at most about 0.6 miles and is noted under the map."""
    import math
    from collections import defaultdict

    groups: dict = defaultdict(list)
    for p in points:
        groups[(round(p["lat"], 4), round(p["lon"], 4))].append(p)
    out = []
    for members in groups.values():
        n = len(members)
        for k, p in enumerate(members):
            if n == 1:
                out.append(p)
                continue
            angle = 2 * math.pi * k / n
            r = 0.004 + 0.0015 * (k // 12)
            out.append(
                {
                    **p,
                    "lat": p["lat"] + r * math.sin(angle),
                    "lon": p["lon"] + r * 1.6 * math.cos(angle),
                }
            )
    return out


def entry_plausible(v: dict) -> bool:
    """No data-experience demand, or at most a year with signs the advert welcomes newcomers."""
    years = v.get("data_years")
    if years is None or years != years:  # None or NaN (from pandas): no demand
        return True
    return years <= 1 and (bool(v.get("entry_signals")) or v.get("degree") == "or_equivalent")


def _band_label(lo: float, hi: float, money: bool) -> str:
    if money:
        if lo == 0:
            return f"under £{hi // 1000}k"
        if hi >= 10**9:
            return f"£{lo // 1000}k+"
        return f"£{lo // 1000}k–{hi // 1000}k"
    if hi >= 10**6:
        return f"{lo}+ miles"
    return f"{lo}–{hi} miles"


def build_insights(snap: Snapshot) -> dict:
    tax = get_taxonomy()
    shown = snap.shown
    entry = [v for v in shown if entry_plausible(v)]

    comp_counts: Counter = Counter()
    skill_counts: Counter = Counter()
    essential_skill_counts: Counter = Counter()
    for v in entry:
        seen = set()
        for r in snap.requirements.get(v["vacancy_id"], []):
            if r["strength"] not in ("essential", "desirable"):
                continue
            for t, i in r["tags"]:
                seen.add((t, i))
        for t, i in seen:
            (comp_counts if t == "competency" else skill_counts)[i] += 1

    for v in shown:
        essential_skills = {
            tag_id
            for requirement in snap.requirements.get(v["vacancy_id"], [])
            if requirement["strength"] == "essential"
            for tag_type, tag_id in requirement["tags"]
            if tag_type == "skill" and tag_id in tax.skills
        }
        essential_skill_counts.update(essential_skills)

    essential_skill_total = sum(essential_skill_counts.values())
    top_essential_skills = sorted(
        essential_skill_counts.items(),
        key=lambda item: (-item[1], tax.skills[item[0]].label.casefold()),
    )[:20]
    essential_skill_chart = [
        {
            "id": skill_id,
            "label": tax.skills[skill_id].label,
            "n": count,
            "share": round(100 * count / essential_skill_total, 2),
            "course_covered": tax.skills[skill_id].course_covered,
            "course_share": (
                round(100 * count / essential_skill_total, 2)
                if tax.skills[skill_id].course_covered
                else 0
            ),
        }
        for skill_id, count in top_essential_skills
    ]

    juniors = [v for v in shown if JUNIOR_TITLE.search(v["title"])]
    juniors_2plus = [v for v in juniors if (v.get("data_years") or 0) >= 2]
    others = [v for v in shown if not JUNIOR_TITLE.search(v["title"])]
    others_2plus = [v for v in others if (v.get("data_years") or 0) >= 2]

    primaries = [v for v in snap.vacancies.values() if v["is_primary"]]
    senior_words = Counter(
        v["title_excluded_word"] for v in primaries if v["excluded_reason"] == "senior role"
    )
    excluded = Counter(v["excluded_reason"] for v in primaries if v["excluded_reason"])

    annual = [
        (v["salary_min"] + v["salary_max"]) / 2
        for v in shown
        if v["salary_period"] == "annum"
        and v.get("currency") in (None, "GBP")
        and v["salary_min"]
        and v["salary_max"]
    ]
    salary_bands = [
        {"label": _band_label(lo, hi, True), "n": sum(1 for s in annual if lo <= s < hi)}
        for lo, hi in SALARY_BANDS
    ]
    arrangement = Counter(v["arrangement"] or "unknown" for v in shown)

    return {
        "mode": snap.mode,
        "snapshot_date": snap.meta.get("snapshot_date"),
        "n_shown": len(shown),
        "n_entry": len(entry),
        "n_total": len(snap.vacancies),
        "competencies": [
            {"id": i, "label": tax.competencies[i].label, "n": n}
            for i, n in comp_counts.most_common(15)
        ],
        "skills": [
            {"id": i, "label": tax.skills[i].label, "n": n} for i, n in skill_counts.most_common(15)
        ],
        "essential_skill_chart": essential_skill_chart,
        "essential_skill_total": essential_skill_total,
        "junior": {
            "n": len(juniors),
            "two_plus": len(juniors_2plus),
            "others_n": len(others),
            "others_two_plus": len(others_2plus),
            "examples": [
                {
                    "title": v["title"],
                    "employer": v["employer"],
                    "text": v["data_years_text"],
                    "id": v["vacancy_id"],
                }
                for v in juniors_2plus[:5]
            ],
        },
        "senior_words": [{"label": w, "n": n} for w, n in senior_words.most_common()],
        "n_senior": sum(senior_words.values()),
        "excluded": [{"label": r, "n": n} for r, n in excluded.most_common()],
        "salary": {
            "bands": salary_bands,
            "n": len(annual),
            "n_shown": len(shown),
            "min": min(annual) if annual else None,
            "max": max(annual) if annual else None,
            "median": sorted(annual)[len(annual) // 2] if annual else None,
        },
        "arrangement": [
            {"label": ARRANGEMENT_LABELS.get(k, k), "n": n} for k, n in arrangement.most_common()
        ],
        "points": spread_points(
            [
                {
                    "lat": v["lat"],
                    "lon": v["lon"],
                    "title": v["title"],
                    "employer": v["employer"] or "",
                    "id": v["vacancy_id"],
                }
                for v in shown
                if v["lat"] is not None
            ]
        ),
        "n_remote": sum(1 for v in shown if v["is_remote"]),
        "n_unclear": sum(1 for v in shown if v["lat"] is None and not v["is_remote"]),
    }


def personal_insights(profile: Profile, snap: Snapshot) -> dict:
    tax = get_taxonomy()
    sl = build_shortlist(profile, snap, Filters())
    points = spread_points(
        [
            {
                "lat": m.vacancy["lat"],
                "lon": m.vacancy["lon"],
                "tier": m.tier,
                "label": m.tier_label,
                "title": m.vacancy["title"],
                "employer": m.vacancy["employer"] or "",
                "id": m.vacancy["vacancy_id"],
                "approx": bool(m.vacancy["location_approximate"]),
            }
            for m in sl.results
            if m.vacancy["lat"] is not None
        ]
    )
    mine = {c for r in profile.roles for c in r.competencies}
    entry = [v for v in snap.shown if entry_plausible(v)]
    demand: Counter = Counter()
    for v in entry:
        seen = {
            i
            for r in snap.requirements.get(v["vacancy_id"], [])
            if r["strength"] in ("essential", "desirable")
            for t, i in r["tags"]
            if t == "competency" and i in mine
        }
        demand.update(seen)
    bands = []
    for lo, hi in DISTANCE_BANDS:
        bands.append(
            {
                "label": _band_label(lo, hi, False),
                "n": sum(
                    1
                    for m in sl.results
                    if m.distance_miles is not None and lo <= m.distance_miles < hi
                ),
            }
        )
    bands.append({"label": "UK-remote", "n": sum(1 for m in sl.results if m.vacancy["is_remote"])})
    bands.append(
        {
            "label": "location unclear",
            "n": sum(
                1 for m in sl.results if m.distance_miles is None and not m.vacancy["is_remote"]
            ),
        }
    )
    tiers = Counter(m.tier for m in sl.results)
    return {
        "mode": snap.mode,
        "home": list(sl.home) if sl.home else None,
        "outcode": profile.outcode,
        "points": points,
        "n_results": len(sl.results),
        "tiers": [{"id": t, "n": tiers[t]} for t in TIER_ORDER],
        "my_competencies": [
            {"label": tax.competencies[c].label, "n": demand[c]}
            for c in sorted(mine, key=lambda c: -demand[c])
        ],
        "n_entry": len(entry),
        "distance_bands": bands,
    }
