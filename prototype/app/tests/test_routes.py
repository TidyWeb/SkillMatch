import json
import os
import tempfile
import time
from pathlib import Path

import pandas as pd
import pytest

from skillmatch import config, profile_visualization
from skillmatch.etl.pipeline import run
from skillmatch.profile import Profile, personas
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


@pytest.mark.parametrize("path", ["/", "/results", "/insights", "/sources", "/about", "/healthz"])
def test_get_pages(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert b"SkillMatch" in r.data or path == "/healthz"
    if path != "/healthz":
        assert b">Your skills</a>" in r.data


def test_footer_shows_data_mode(client):
    assert b"Fixtures" in client.get("/").data


def test_results_for_every_persona(client):
    seen = set()
    for pid in personas():
        r = client.post("/results", data={"profile": profile_json(pid)})
        assert r.status_code == 200
        html = r.data.decode()
        assert "How your background answers this" in html
        assert "Also search these sources near you" in html
        assert "senior roles hidden" in html
        seen.add(html.split("tier-strong", 1)[-1][:2000])
    assert len(seen) == len(personas())  # different people get different lists


def test_results_without_profile(client):
    r = client.post("/results", data={})
    assert r.status_code == 200 and b"Start with your profile" in r.data


def test_profile_skills_visualization(client, monkeypatch):
    monkeypatch.setattr(
        profile_visualization,
        "vacancy_skills",
        pd.DataFrame(
            [
                {
                    "skill": "business_analysis",
                    "count": 12,
                    "strength": "essential",
                    "confidence": "stated",
                    "course_covered": True,
                },
                {
                    "skill": "sql",
                    "count": 7,
                    "strength": "desirable",
                    "confidence": "inferred",
                    "course_covered": False,
                },
            ]
        ),
    )
    profile = personas()["chef_wolverhampton"]
    response = client.post("/profile/skills", data={"profile": json.dumps(profile)})
    html = response.data.decode()
    assert response.status_code == 200
    assert "Your skill summary" in html
    assert "Learned on the course" in html
    assert "Confident" in html
    assert (
        "Business analysis and requirements is stated as an essential requirement in 12 vacancies."
        in html
    )
    assert "SQL is inferred as an desirable requirement in 7 vacancies." in html
    assert "Skills requested in vacancies" in html
    assert "Course covered: Yes" in html
    assert "Course covered: No" in html
    assert "Your skills and essential vacancy requirements" in html
    assert "Here’s how your skill selections relate to the essential requirements in current vacancies." in html
    assert "Skills requested in vacancies" in html
    assert 'href="/profile/skills" data-profile-navigation aria-current="page">Your skills</a>' in html


def test_profile_skills_get_redirects_to_profile(client):
    response = client.get("/profile/skills")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_profile_skills_visualization_without_profile(client):
    response = client.post("/profile/skills", data={})
    assert response.status_code == 200
    assert b"Start with your profile" in response.data


def test_vacancy_skill_comparison_includes_count_coverage_and_profile(monkeypatch):
    monkeypatch.setattr(
        profile_visualization,
        "vacancy_skills",
        pd.DataFrame(
            [
                {
                    "skill": "python",
                    "count": 12,
                    "strength": "essential",
                    "confidence": "stated",
                    "course_covered": False,
                },
                {
                    "skill": "sql",
                    "count": 7,
                    "strength": "desirable",
                    "confidence": "inferred",
                    "course_covered": True,
                },
            ]
        ),
    )
    comparison = profile_visualization.compare_vacancy_skills(
        Profile(skills={"python": "confident"})
    )

    assert comparison["max_count"] == 12
    assert comparison["skills"] == [
        {
            "skill": "Python",
            "count": 12,
            "strength": "essential",
            "confidence": "stated",
            "sentence": "Python is stated as an essential requirement in 12 vacancies.",
            "course_covered": False,
            "profile_level": "Confident",
            "profile_has_skill": True,
        },
        {
            "skill": "SQL",
            "count": 7,
            "strength": "desirable",
            "confidence": "inferred",
            "sentence": "SQL is inferred as an desirable requirement in 7 vacancies.",
            "course_covered": True,
            "profile_level": None,
            "profile_has_skill": False,
        },
    ]
    assert comparison["chart"] == [
        {
            "skill": "Python",
            "count": 12,
            "course_covered": False,
            "profile_level": "Confident",
            "score": 4,
            "bar_color": "#A63A50",
            "demand_score": 4.0,
        },
    ]


def test_reveal_senior_roles(client):
    r = client.post("/results", data={"profile": profile_json(), "reveal": "senior role"})
    assert b"Shown because you asked" in r.data
    assert b"Hidden by default: senior role" in r.data


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


def test_archetype_api(client):
    assert client.get("/api/archetype?title=Head+Chef").get_json()["id"] == "kitchen_manager"
    assert client.get("/api/archetype?title=zzzz").get_json() == {}


def test_profile_is_never_written_to_disk_or_cookies(client, db):
    """Post a profile with a unique marker; no file anywhere we can see may contain it afterwards."""
    marker = f"MARKER-{time.time_ns()}"
    prof = personas()["retail_telford"]
    prof = {**prof, "roles": [{**prof["roles"][0], "competencies": {"kpi_monitoring": marker}}]}
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
    assert "near WV1" in html and "1SH" not in html
