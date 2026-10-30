"""Build the shared, browser-ready job card feed for HTML and JSON routes."""

from __future__ import annotations

from urllib.parse import quote, urlsplit, urlunsplit

from flask import current_app

from skillmatch.job_brief import build_job_brief
from skillmatch.match import TIER_ORDER
from skillmatch.web.format import place, salary


def safe_http_url(value: str | None) -> str | None:
    """Keep links to explicitly configured or collected HTTP(S) destinations only."""
    value = (value or "").strip()
    if not value:
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
        return None
    return value


def _tailor_url(brief: str) -> str | None:
    destination = safe_http_url(current_app.config.get("TAILOR_PAGE_URL"))
    if not destination:
        return None
    parts = urlsplit(destination)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, quote(brief, safe="")))


def _requirement(cov) -> dict:
    return {
        "sentence": cov.sentence,
        "answers": list(cov.answers),
        "reasons": [tag.gap for tag in cov.gaps if tag.gap],
        "strength": cov.strength,
        "confidence": cov.confidence,
    }


def build_card(match, profile=None, requirements=None) -> dict:
    """Serialize one match without adding claims beyond stored advert/profile evidence."""
    vacancy = match.vacancy
    requirement_details = {
        "requirements_met": [],
        "partly_met": [],
        "gaps": [],
    }
    uncategorised = []
    for cov in match.coverage:
        if cov.status == "unclassified":
            uncategorised.append(_requirement(cov))
            continue
        if cov.strength not in ("essential", "desirable"):
            continue
        key = {"met": "requirements_met", "partly": "partly_met", "gap": "gaps"}.get(cov.status)
        if key:
            requirement_details[key].append(_requirement(cov))

    advert_requirements = requirements or []
    duties = [
        {"sentence": row["evidence_sentence"], "answers": [], "reasons": []}
        for row in advert_requirements
        if row.get("strength") == "duty"
    ]
    detail = {**requirement_details, "duties": duties}
    if uncategorised:
        detail["uncategorised"] = uncategorised

    advert_url = safe_http_url(vacancy.get("url"))
    brief = build_job_brief(vacancy, advert_requirements, match if profile is not None else None)
    card = {
        "id": match.vacancy_id,
        "title": vacancy.get("title") or "Job title not stated",
        "company": vacancy.get("employer") or "Employer not named",
        "location": place(vacancy),
        "salary_text": salary(vacancy),
        "match_level": match.tier_label,
        "match_tier": match.tier,
        "remote": bool(vacancy.get("is_remote")),
        "advert_url": advert_url,
        "detail": detail,
        "reasons": list(match.reasons),
        "guard_reason": getattr(match, "guard_reason", None),
        "job_brief": brief,
        "tailor_url": _tailor_url(brief),
    }
    if uncategorised:
        card["uncategorised"] = uncategorised
    return card


def build_cards(matches, profile=None, requirements=None) -> list[dict]:
    """Build cards by match tier, then distance, carrying snapshot duties along."""
    # Keep the dependency explicit to the request so a card can be built from the already-loaded
    # snapshot; never reload a database or persist profile data here.
    requirement_map = requirements or {}
    tier_rank = {tier: index for index, tier in enumerate(TIER_ORDER)}
    ordered = sorted(
        matches,
        key=lambda match: (
            tier_rank.get(match.tier, len(tier_rank)),
            match.distance_miles is None,
            match.distance_miles if match.distance_miles is not None else 0,
            match.vacancy.get("title") or "",
        ),
    )
    return [
        build_card(match, profile, requirement_map.get(match.vacancy_id, [])) for match in ordered
    ]
