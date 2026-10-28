"""Prepare a validated profile's skills for a readable visual summary."""

from __future__ import annotations

import re

import pandas as pd

from skillmatch.profile import SKILL_LEVELS, Profile
from skillmatch.taxonomy import Taxonomy, get_taxonomy

LEVEL_LABELS = {
    "course": "Learned on the course",
    "project": "Used in a project",
    "confident": "Confident",
}


vacancy_skills = pd.DataFrame(
    {
        "skill_name": [
            "Oracle (SQL)",
            "Overfitting management",
            "Pandas",
            "Pearson correlation",
            "Percentages",
            "Pivot tables",
            "Plotly",
            "Portfolio development",
            "PostgreSQL",
            "Power BI",
            "Power BI proficiency",
            "Presentation Skills",
            "Presentation Software",
            "Price Analysis",
            "Pricing Analysis",
            "Probability",
            "Problem Solving",
            "Problem Solving Skills",
            "Problem-solving",
            "Prophet forecasting",
            "P-value",
            "Python",
            "Python Development",
            "Python programming",
            "PyTorch",
            "Quantitative Analysis",
            "Quantitative and qualitative research methods",
        ]
    }
)


def _normalize_skill_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.casefold())


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
    """Compare selected profile skill labels with the curated vacancy skill list."""
    tax = tax or get_taxonomy()
    profile_labels = sorted(
        (tax.skills[skill_id].label for skill_id in profile.skills),
        key=str.casefold,
    )
    vacancy_labels = vacancy_skills["skill_name"].dropna().astype(str).tolist()

    profile_by_key = {_normalize_skill_name(label): label for label in profile_labels}
    vacancy_by_key = {
        _normalize_skill_name(label): label
        for label in vacancy_labels
        if _normalize_skill_name(label)
    }

    matched = sorted(
        (profile_by_key[key] for key in profile_by_key.keys() & vacancy_by_key.keys()),
        key=str.casefold,
    )
    profile_only = sorted(
        (profile_by_key[key] for key in profile_by_key.keys() - vacancy_by_key.keys()),
        key=str.casefold,
    )
    vacancy_only = sorted(
        (vacancy_by_key[key] for key in vacancy_by_key.keys() - profile_by_key.keys()),
        key=str.casefold,
    )
    chart = [
        {"label": "Profile skills found in vacancy list", "count": len(matched), "items": matched},
        {
            "label": "Profile skills not in vacancy list",
            "count": len(profile_only),
            "items": profile_only,
        },
        {
            "label": "Vacancy-list skills not in profile",
            "count": len(vacancy_only),
            "items": vacancy_only,
        },
    ]
    return {
        "chart": chart,
        "matched": matched,
        "profile_only": profile_only,
        "vacancy_only": vacancy_only,
    }
