"""Page routes. The server is stateless: the profile arrives with each request (POST field
`profile`, JSON from the browser's sessionStorage) and is forgotten when the response is sent.
Nothing from the profile is written to disk, logged or put in a cookie.
"""

from __future__ import annotations

import json

from flask import Blueprint, abort, current_app, jsonify, render_template, request

from skillmatch import repository
from skillmatch.insights import build_insights, personal_insights
from skillmatch.match import TIER_ORDER, match_vacancy
from skillmatch.phrasing import Phraser
from skillmatch.profile import (
    DEGREES,
    SKILL_LEVELS,
    TRAVEL,
    persona_cards,
    personas,
    profile_from_json,
)
from skillmatch.profile_visualization import compare_vacancy_skills, skill_groups
from skillmatch.results import (
    HIDDEN_LABELS,
    SOURCE_TIERS,
    Filters,
    build_discovery_links,
    build_shortlist,
    home_place,
)
from skillmatch.sources.cvlibrary import REGISTER_URL
from skillmatch.taxonomy import SENIORITY, get_taxonomy

bp = Blueprint("web", __name__)

TIER_DOTS = {"strong": 3, "good": 2, "stretch": 1, "not_yet": 0}


def snapshot():
    return repository.load(current_app.config["DB_PATH"])


def posted_profile():
    return profile_from_json(request.form.get("profile"))


@bp.app_context_processor
def inject_globals():
    snap = snapshot()
    return {
        "snap": snap,
        "data_mode": snap.mode if snap else None,
        "snapshot_date": snap.meta.get("snapshot_date") if snap else None,
        "tier_dots": TIER_DOTS,
    }


@bp.get("/")
def profile():
    tax = get_taxonomy()
    skills = sorted(tax.skills.values(), key=lambda s: (not s.course_covered, s.label.lower()))
    taxonomy_json = {
        "skills": {s.id: {"label": s.label, "course": s.course_covered} for s in skills},
        "competencies": {
            c.id: {"label": c.label, "description": c.description, "category": c.category}
            for c in sorted(tax.competencies.values(), key=lambda c: c.label)
        },
        "archetypes": {
            a.id: {
                "label": a.label,
                "competencies": list(a.competencies),
                "example": a.example_evidence,
            }
            for a in sorted(tax.archetypes.values(), key=lambda a: a.label)
        },
    }
    return render_template(
        "profile.html",
        course_skills=[s for s in skills if s.course_covered],
        other_skills=[s for s in skills if not s.course_covered],
        archetypes=sorted(tax.archetypes.values(), key=lambda a: a.label),
        seniority=SENIORITY,
        travel=TRAVEL,
        degrees=DEGREES,
        skill_levels=SKILL_LEVELS,
        persona_cards=persona_cards(),
        personas_json=personas(),
        taxonomy_json=taxonomy_json,
    )


@bp.get("/api/archetype")
def archetype_match():
    """Fuzzy-match a typed job title to an archetype. The title is not stored or logged."""
    hit = get_taxonomy().match_archetype(request.args.get("title", "")[:80])
    if not hit:
        return jsonify({})
    a = get_taxonomy().archetypes[hit[0]]
    return jsonify({"id": a.id, "label": a.label})


@bp.get("/results")
def results():
    return render_template("results.html", tiers=TIER_ORDER, source_tiers=SOURCE_TIERS)


@bp.post("/profile/skills")
def profile_skills():
    prof = posted_profile()
    if prof is None:
        return render_template("partials/no_profile.html", missing_data=False)
    return render_template(
        "profile_skills.html",
        groups=skill_groups(prof),
        comparison=compare_vacancy_skills(prof),
    )


def _filters_from_form() -> Filters:
    f = Filters()
    raw = request.form.get("max_miles", "").strip()
    try:
        f.max_miles = float(raw) if raw else None
    except ValueError:
        f.max_miles = None
    chosen = set(request.form.getlist("tier")) & set(TIER_ORDER)
    if chosen:
        f.tiers = chosen
    if request.form.get("arrangement") in ("onsite", "hybrid", "remote"):
        f.arrangement = request.form["arrangement"]
    f.salary_stated = request.form.get("salary_stated") == "on"
    if request.form.get("source_tier") in SOURCE_TIERS:
        f.source_tier = request.form["source_tier"]
    f.reveal = set(request.form.getlist("reveal"))
    return f


@bp.post("/results")
def results_list():
    snap = snapshot()
    prof = posted_profile()
    if snap is None or prof is None:
        return render_template("partials/no_profile.html", missing_data=snap is None)
    filters = _filters_from_form()
    shortlist = build_shortlist(prof, snap, filters)
    links = build_discovery_links(shortlist.town, filters.max_miles or prof.max_miles)
    return render_template(
        "partials/results_list.html",
        sl=shortlist,
        profile=prof,
        filters=filters,
        hidden_labels=HIDDEN_LABELS,
        tier_labels=Phraser().t["tiers"],
        links=links,
    )


def _vacancy_or_404(job_id: str):
    snap = snapshot()
    if snap is None or job_id not in snap.vacancies:
        abort(404)
    return snap, snap.vacancies[job_id]


@bp.get("/job/<path:job_id>")
def job(job_id: str):
    snap, v = _vacancy_or_404(job_id)
    reqs = snap.requirements.get(job_id, [])
    return render_template(
        "job.html",
        v=v,
        reqs=reqs,
        also=snap.also_listed(v),
        duties=[r for r in reqs if r["strength"] == "duty"],
    )


@bp.post("/job/<path:job_id>")
def job_coverage(job_id: str):
    snap, v = _vacancy_or_404(job_id)
    prof = posted_profile()
    if prof is None:
        return render_template("partials/no_profile.html", missing_data=False)
    place = home_place(prof)
    home = (place.lat, place.lon) if place else None
    m = match_vacancy(prof, v, snap.requirements.get(job_id, []), home)
    return render_template("partials/coverage.html", m=m, v=v, profile=prof)


@bp.get("/insights")
def insights():
    snap = snapshot()
    data = build_insights(snap) if snap else None
    return render_template(
        "insights.html", data=data, data_json=json.dumps(data) if data else "null"
    )


@bp.post("/insights")
def insights_personal():
    snap = snapshot()
    prof = posted_profile()
    if snap is None or prof is None:
        return render_template("partials/no_profile.html", missing_data=snap is None)
    data = personal_insights(prof, snap)
    return render_template("partials/insights_personal.html", data=data, data_json=json.dumps(data))


@bp.get("/sources")
def sources():
    snap = snapshot()
    groups = build_discovery_links(None, None)
    counts = {}
    if snap:
        for v in snap.vacancies.values():
            counts[v["source"]] = counts.get(v["source"], 0) + 1
    return render_template("sources.html", groups=groups, counts=counts, register_url=REGISTER_URL)


@bp.get("/about")
def about():
    return render_template("about.html")


@bp.get("/healthz")
def healthz():
    snap = snapshot()
    return jsonify({"ok": snap is not None, "mode": snap.mode if snap else None})
