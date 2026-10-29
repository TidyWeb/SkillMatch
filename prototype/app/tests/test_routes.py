import json
import os
import tempfile
import time
from pathlib import Path

import pytest

from skillmatch import config
from skillmatch.etl.pipeline import run
from skillmatch.profile import personas
from skillmatch.web import create_app


@pytest.fixture(scope="module")
def db(tmp_path_factory):
    d = tmp_path_factory.mktemp("web")
    run("fixtures", db_path=d / "web.db", reports_dir=d / "reports", offline=True)
    return d / "web.db"


@pytest.fixture
def client(db):
    return create_app({"TESTING": True, "DB_PATH": str(db)}).test_client()


def profile_json(pid="chef_wolverhampton", **extra):
    return json.dumps({**personas()[pid], **extra})


@pytest.mark.parametrize(
    "path",
    ["/", "/profile/skills", "/results", "/insights", "/sources", "/about", "/health", "/healthz"],
)
def test_get_pages(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert b"SkillMatch" in r.data or path in {"/health", "/healthz"}


@pytest.mark.parametrize("path", ["/health", "/healthz"])
def test_health_endpoints_return_identical_json(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert r.get_json() == {"ok": True, "mode": "fixtures"}


def test_footer_shows_data_mode(client):
    assert b"Fixtures" in client.get("/").data


def test_results_for_every_persona(client):
    seen = set()
    for pid in personas():
        r = client.post("/results", data={"profile": profile_json(pid)})
        assert r.status_code == 200
        html = r.data.decode()
        assert "SKILLMATCH JOB BRIEF" in html
        assert "requirements_met" not in html
        seen.add(html.split("tier-strong", 1)[-1][:2000])
    assert len(seen) == len(personas())  # different people get different lists


def test_results_without_profile(client):
    r = client.post("/results", data={})
    assert r.status_code == 200 and b"Start with your profile" in r.data


def test_reveal_senior_roles(client, monkeypatch):
    import skillmatch.web.routes as routes

    rendered = {}
    original = routes.render_template

    def capture(template, **context):
        if template == "partials/results_list.html":
            rendered["shortlist"] = context["sl"]
        return original(template, **context)

    monkeypatch.setattr(routes, "render_template", capture)
    r = client.post("/results", data={"profile": profile_json(), "reveal": "senior role"})
    assert r.status_code == 200
    assert rendered["shortlist"].revealed


def test_filters(client):
    r = client.post(
        "/results",
        data={
            "profile": profile_json(),
            "tier": "strong",
            "arrangement": "hybrid",
            "max_miles": "10",
        },
    )
    html = r.data.decode()
    assert r.status_code == 200
    assert 'Not yet</span> <span class="count">' not in html.split("Hidden from this list")[-1]


def test_job_pages(client, db):
    from skillmatch.repository import load

    snap = load(db)
    ids = [v["vacancy_id"] for v in snap.shown][:3]
    for job_id in ids:
        assert client.get(f"/job/{job_id}").status_code == 200
        r = client.post(f"/job/{job_id}", data={"profile": profile_json("teacher_stoke")})
        assert r.status_code == 200
        assert b"Requirement by requirement" in r.data
    assert client.get("/job/nope:1").status_code == 404


def test_insights_personal(client):
    r = client.post("/insights", data={"profile": profile_json("nurse_worcester")})
    assert r.status_code == 200


def test_profile_skills_api_uses_selected_levels_and_essential_counts(client):
    profile = json.loads(profile_json())
    profile["skills"] = list(profile["skills"]) + ["sql"]
    profile["skill_levels"] = {"sql": "project"}
    response = client.post("/api/profile/skills", data={"profile": json.dumps(profile)})

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    data = response.get_json()
    assert any("SQL" in group["skills"] for group in data["groups"] if group["level"] == "project")
    assert data["comparison"]["chart"]
    assert all(row["count"] > 0 for row in data["comparison"]["chart"])
    assert all(row["essential_count"] <= row["count"] for row in data["comparison"]["skills"])
    sql_row = next(row for row in data["comparison"]["chart"] if row["skill"] == "SQL")
    assert sql_row["profile_level"] == "Used in a project"


def test_profile_skills_api_validates_profile(client):
    assert client.post("/api/profile/skills", data={}).status_code == 400
    assert (
        client.post("/api/profile/skills", data={"profile": "not-json"}).status_code == 400
    )


def test_archetype_api(client):
    assert (
        client.get("/api/archetype?title=Head+Chef").get_json()["id"] == "kitchen_food_production"
    )
    assert client.get("/api/archetype?title=zzzz").get_json() == {}


def test_matches_api_requires_profile_header(client):
    assert client.get("/api/matches").status_code == 400
    assert (
        client.get("/api/matches", headers={"X-SkillMatch-Profile": "not-json"}).status_code == 400
    )
    too_large = " " * 8193
    assert (
        client.get("/api/matches", headers={"X-SkillMatch-Profile": too_large}).status_code == 400
    )


def test_matches_api_returns_ordered_card_feed(client):
    r = client.get("/api/matches", headers={"X-SkillMatch-Profile": profile_json()})
    assert r.status_code == 200
    assert r.headers["Cache-Control"] == "no-store"
    assert "X-SkillMatch-Profile" in r.headers["Vary"]
    data = r.get_json()
    assert data["cards"]
    assert set(data["counts"]) == {"strong", "good", "stretch", "not_yet"}
    tier_rank = {tier: rank for rank, tier in enumerate(("strong", "good", "stretch", "not_yet"))}
    ranks = [tier_rank[card["match_tier"]] for card in data["cards"]]
    assert ranks == sorted(ranks)
    card = data["cards"][0]
    assert {
        "id",
        "title",
        "company",
        "location",
        "salary_text",
        "match_level",
        "match_tier",
        "remote",
        "advert_url",
        "detail",
        "reasons",
        "job_brief",
        "tailor_url",
    } <= card.keys()
    assert {"requirements_met", "partly_met", "gaps", "duties"} <= card["detail"].keys()


def test_matches_api_returns_503_without_database(tmp_path):
    client = create_app({"TESTING": True, "DB_PATH": str(tmp_path / "missing.db")}).test_client()
    r = client.get("/api/matches", headers={"X-SkillMatch-Profile": profile_json()})
    assert r.status_code == 503


def test_html_and_api_use_same_card_data(client, monkeypatch):
    import skillmatch.web.routes as routes

    rendered = {}
    original = routes.render_template

    def capture(template, **context):
        if template == "partials/results_list.html":
            rendered["cards"] = context["cards"]
        return original(template, **context)

    monkeypatch.setattr(routes, "render_template", capture)
    client.post("/results", data={"profile": profile_json()})
    data = client.get("/api/matches", headers={"X-SkillMatch-Profile": profile_json()}).get_json()
    assert rendered["cards"] == data["cards"]


def test_profile_is_never_written_to_disk_or_cookies(client, db):
    """Post a profile with a unique marker; no file anywhere we can see may contain it afterwards."""
    marker = f"MARKER-{time.time_ns()}"
    prof = {**personas()["retail_telford"], "unrecognised_field": marker}
    start = time.time() - 1
    responses = [
        client.post("/results", data={"profile": json.dumps(prof)}),
        client.post("/insights", data={"profile": json.dumps(prof)}),
    ]
    from skillmatch.repository import load

    job_id = load(db).shown[0]["vacancy_id"]
    responses.append(client.post(f"/job/{job_id}", data={"profile": json.dumps(prof)}))
    for r in responses:
        assert r.status_code == 200
        assert "Set-Cookie" not in r.headers
    roots = [config.ROOT, Path(tempfile.gettempdir()), db.parent]
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [
                d for d in dirnames if d not in (".git", ".venv", "node_modules", "__pycache__")
            ]
            for name in filenames:
                p = Path(dirpath) / name
                try:
                    if p.stat().st_mtime < start or p.stat().st_size > 5_000_000:
                        continue
                    assert marker.encode() not in p.read_bytes(), f"profile data found in {p}"
                except (PermissionError, FileNotFoundError, OSError):
                    continue


def test_full_postcode_is_reduced_to_outward_code(client):
    r = client.post("/results", data={"profile": profile_json(postcode="WV1 1SH")})
    html = r.data.decode()
    assert r.status_code == 200 and "1SH" not in html
