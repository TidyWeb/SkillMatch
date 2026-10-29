"""Prepare a validated profile's skills for a readable visual summary."""

from __future__ import annotations

import pandas as pd

from skillmatch.profile import SKILL_LEVELS, Profile
from skillmatch.retreve_vacancies_skillset import get_data_skills
from skillmatch.taxonomy import Taxonomy, get_taxonomy

LEVEL_LABELS = {
    "course": "Learned on the course",
    "project": "Used in a project",
    "confident": "Confident",
}
LEVEL_SCORES = {"course": 2, "project": 3, "confident": 4}
CHART_COLORS = {
    (True, "confident"): "#0B4F6C",
    (True, "project"): "#01BAEF",
    (True, "course"): "#89CFF0",
    (True, None): "#E0F2FE",
    (False, "confident"): "#A63A50",
    (False, "project"): "#D65A31",
    (False, "course"): "#E8A87C",
    (False, None): "#F4E0DB",
}


vacancy_skills = get_data_skills()


def skill_groups(profile: Profile, tax: Taxonomy | None = None) -> list[dict]:
    """Group selected profile skills by proficiency, using their taxonomy labels."""
    tax = tax or get_taxonomy()
    return [
        {
            "level": level,
            "label": LEVEL_LABELS[level],
            "skills": sorted(
                (
                    tax.skills[skill_id].label
                    for skill_id, value in profile.skills.items()
                    if value == level
                ),
                key=str.casefold,
            ),
        }
        for level in SKILL_LEVELS
    ]


def compare_vacancy_skills(profile: Profile, tax: Taxonomy | None = None) -> dict:
    """Prepare vacancy skill counts with course coverage and profile status."""
    tax = tax or get_taxonomy()
    required = {"skill", "count", "strength", "confidence", "course_covered"}
    missing = required - set(vacancy_skills.columns)
    if missing:
        raise ValueError(
            f"Vacancy skills data is missing columns: {', '.join(sorted(missing))}")

    rows = []
    chart_rows = []
    for row in vacancy_skills.to_dict("records"):
        skill_id = str(row["skill"]).strip()
        if not skill_id or skill_id.casefold() == "nan":
            continue
        skill = tax.skills.get(skill_id)
        raw_count = row["count"]
        count = int(raw_count) if not pd.isna(raw_count) else 0
        strength = str(row["strength"])
        confidence = str(row["confidence"])
        covered = row["course_covered"]
        course_covered = None if pd.isna(covered) else bool(covered)
        profile_level = profile.skills.get(skill_id)
        skill_name = skill.label if skill else skill_id
        profile_label = LEVEL_LABELS.get(profile_level)
        rows.append(
            {
                "skill": skill_name,
                "count": count,
                "strength": strength,
                "confidence": confidence,
                "sentence": (
                    f"{skill_name} is {confidence} as an {strength} requirement "
                    f"in {count} vacancies."
                ),
                "course_covered": course_covered,
                "profile_level": profile_label,
                "profile_has_skill": profile_level is not None,
            }
        )
        if strength.casefold() == "essential":
            chart_rows.append(
                {
                    "skill": skill_name,
                    "count": count,
                    "course_covered": course_covered,
                    "profile_level": profile_label or "Not selected",
                    "score": LEVEL_SCORES.get(profile_level, 1),
                    "bar_color": CHART_COLORS.get(
                        (course_covered, profile_level),
                        "#D8D2C4",
                    ),
                }
            )

    rows.sort(key=lambda row: (-row["count"], row["skill"].casefold()))
    chart_rows.sort(key=lambda row: (-row["count"], row["skill"].casefold()))
    counts = [row["count"] for row in chart_rows]
    min_count = min(counts, default=0)
    max_count = max(counts, default=0)
    for row in chart_rows:
        row["demand_score"] = (
            1 + 3 * (row["count"] - min_count) / (max_count - min_count)
            if max_count > min_count
            else 4 if max_count else 1
        )

    return {
        "skills": rows,
        "max_count": max((row["count"] for row in rows), default=0),
        "chart": chart_rows,
    }
