"""Prepare a validated profile's skills for a readable visual summary."""

from __future__ import annotations

from skillmatch.profile import SKILL_LEVELS, Profile
from skillmatch.repository import Snapshot
from skillmatch.retreve_vacancies_skillset import get_data_skills
from skillmatch.taxonomy import Taxonomy, get_taxonomy

LEVEL_LABELS = {
    "course": "Learned on the course",
    "project": "Used in a project",
    "confident": "Confident",
}
LEVEL_SCORES = {"course": 2, "project": 3, "confident": 4}


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
                    for skill_id, value in profile.skill_levels.items()
                    if value == level
                ),
                key=str.casefold,
            ),
        }
        for level in SKILL_LEVELS
    ]


def compare_vacancy_skills(
    profile: Profile, tax: Taxonomy | None = None, *, snap: Snapshot | None = None
) -> dict:
    """Prepare snapshot-wide vacancy counts with course coverage and profile status."""
    tax = tax or get_taxonomy()
    vacancy_skills = get_data_skills(snap, tax)

    rows = []
    chart_rows = []
    for row in vacancy_skills:
        skill_id = str(row["skill"]).strip()
        if not skill_id or skill_id.casefold() == "nan":
            continue
        skill = tax.skills.get(skill_id)
        count = int(row["count"] or 0)
        strength = str(row["strength"])
        raw_essential_count = row.get(
            "essential_count", count if strength.casefold() == "essential" else 0
        )
        essential_count = int(raw_essential_count or 0)
        confidence = str(row["confidence"])
        covered = row["course_covered"]
        course_covered = None if covered is None else bool(covered)
        profile_level = profile.skill_levels.get(skill_id)
        skill_name = skill.label if skill else skill_id
        profile_label = LEVEL_LABELS.get(profile_level)
        rows.append(
            {
                "skill": skill_name,
                "count": count,
                "strength": strength,
                "confidence": confidence,
                "sentence": (
                    f"{skill_name} is {confidence} as a {strength} requirement "
                    f"in {count} vacancies."
                ),
                "essential_count": essential_count,
                "course_covered": course_covered,
                "profile_level": profile_label,
                "profile_has_skill": skill_id in profile.skills,
            }
        )
        if essential_count:
            chart_rows.append(
                {
                    "skill": skill_name,
                    "count": essential_count,
                    "course_covered": course_covered,
                    "profile_level": profile_label or "Not Ticked",
                    "score": LEVEL_SCORES.get(profile_level, 1),
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
