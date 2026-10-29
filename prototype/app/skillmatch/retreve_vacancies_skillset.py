"""Build a vacancy-skill summary from the local snapshot and taxonomy."""

from __future__ import annotations

from collections import defaultdict

from skillmatch.repository import Snapshot
from skillmatch.taxonomy import Taxonomy, get_taxonomy

STRENGTH_PRIORITY = {"essential": 3, "desirable": 2, "unclear": 1}


def get_data_skills(snap: Snapshot | None, tax: Taxonomy | None = None) -> list[dict]:
    """Count distinct shown vacancies asking for each skill, enriched with taxonomy coverage."""
    if snap is None:
        return []

    tax = tax or get_taxonomy()
    skill_vacancies: dict[str, set[str]] = defaultdict(set)
    essential_vacancies: dict[str, set[str]] = defaultdict(set)
    strength_vacancies: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    confidence_vacancies: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )

    for vacancy in snap.shown:
        vacancy_id = vacancy["vacancy_id"]
        for requirement in snap.requirements.get(vacancy_id, []):
            skills = {tag_id for tag_type,
                      tag_id in requirement["tags"] if tag_type == "skill"}
            for skill_id in skills:
                skill_vacancies[skill_id].add(vacancy_id)
                strength = requirement["strength"]
                strength_vacancies[skill_id][strength].add(vacancy_id)
                confidence_vacancies[skill_id][requirement["confidence"]].add(
                    vacancy_id)
                if strength == "essential":
                    essential_vacancies[skill_id].add(vacancy_id)

    rows = []
    for skill_id, vacancy_ids in skill_vacancies.items():
        strengths = strength_vacancies[skill_id]
        confidence_levels = confidence_vacancies[skill_id]
        strength = max(
            strengths,
            key=lambda value: (
                len(strengths[value]),
                STRENGTH_PRIORITY.get(value, 0),
                value,
            ),
        )
        confidence = max(
            confidence_levels,
            key=lambda value: (len(confidence_levels[value]), value),
        )
        skill = tax.skills.get(skill_id)
        rows.append(
            {
                "skill": skill_id,
                "count": len(vacancy_ids),
                "strength": strength,
                "confidence": confidence,
                "course_covered": skill.course_covered if skill else None,
                "essential_count": len(essential_vacancies[skill_id]),
            }
        )

    rows.sort(key=lambda row: (-row["count"], row["skill"]))
    return rows[:25]
