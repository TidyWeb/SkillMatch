"""Create the source-backed handoff text for the Tailor my CV page."""

from __future__ import annotations

import re


def _text(value, fallback: str = "not mentioned") -> str:
    text = " ".join(str(value or "").split())
    return text or fallback


def build_job_brief(vacancy: dict, requirements: list[dict], match=None) -> str:
    """Use only fields captured from the advert, with optional match-status hints."""
    lines = [
        "Tailor my CV for this job using my SkillMatch folder.",
        "",
        "SKILLMATCH JOB BRIEF",
        f"Job: {_text(vacancy.get('title'), 'not stated')}",
        f"Employer: {_text(vacancy.get('employer'), 'not named')}",
        f"Location: {_text(vacancy.get('location_text'), 'not stated')}",
        f"Salary: {_text(vacancy.get('salary_text') or _salary(vacancy), 'not stated')}",
        f"Closing date: {_text(vacancy.get('expiration_date'), 'not stated')}",
        f"Advert: {_text(vacancy.get('url'), 'not available')}",
    ]
    for strength in ("essential", "desirable", "duty"):
        label = "Duties" if strength == "duty" else strength.capitalize()
        for row in sorted(requirements, key=lambda item: item.get("n", 0)):
            if row.get("strength") == strength:
                lines.append(f"{label}: {_text(row.get('evidence_sentence'))}")
    lines.extend(
        [
            f"Degree: {_text(vacancy.get('degree_text') or _source_line(requirements, r'\b(degree|qualification)\b'))}",
            f"Experience: {_text(vacancy.get('data_years_text') or _source_line(requirements, r'\b(experience|years?)\b'))}",
        ]
    )
    if match is not None:
        lines.extend(
            ["", "SKILLMATCH HINTS (check these against my biography; don't treat them as facts)"]
        )
        for cov in match.coverage:
            if cov.strength not in ("essential", "desirable"):
                continue
            if cov.status == "unclassified":
                continue
            status = {"met": "met", "partly": "partly", "gap": "gap"}.get(cov.status)
            if status:
                lines.append(f"{cov.sentence}: {status}")
    return "\n".join(lines)


def _source_line(requirements: list[dict], pattern: str) -> str | None:
    """Use the advert's own requirement sentence when its parsed fact text is absent."""
    expression = re.compile(pattern, re.IGNORECASE)
    return next(
        (
            str(row.get("evidence_sentence", "")).strip()
            for row in sorted(requirements, key=lambda item: item.get("n", 0))
            if expression.search(str(row.get("evidence_sentence", "")))
        ),
        None,
    )


def _salary(vacancy: dict) -> str:
    """Format the stored amount only; avoid importing the web presentation layer."""
    from skillmatch.web.format import salary

    rendered = salary(vacancy)
    return "not stated" if rendered == "Not stated" else rendered
