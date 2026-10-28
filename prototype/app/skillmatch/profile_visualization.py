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
        raise ValueError(f"Vacancy skills data is missing columns: {', '.join(sorted(missing))}")

    rows = []
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
                "profile_level": LEVEL_LABELS.get(profile_level),
                "profile_has_skill": profile_level is not None,
            }
        )

    rows.sort(key=lambda row: (-row["count"], row["skill"].casefold()))
    return {
        "skills": rows,
        "max_count": max((row["count"] for row in rows), default=0),
    }
