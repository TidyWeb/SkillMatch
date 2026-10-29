"""Regression checks for the public profile and shared match feed."""

from html.parser import HTMLParser
from pathlib import Path

import pytest

from skillmatch.match import GAP, MET, PARTLY, evaluate_requirement, match_vacancy
from skillmatch.phrasing import Phraser
from skillmatch.profile import profile_from_dict
from skillmatch.taxonomy import get_taxonomy
from skillmatch.web import create_app


class Controls(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_form = False
        self.controls = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "form" and values.get("id") == "profile-form":
            self.in_form = True
        if self.in_form and tag in {"input", "select", "button"}:
            self.controls.append(values)

    def handle_endtag(self, tag):
        if tag == "form":
            self.in_form = False


def test_profile_has_exactly_ten_base_controls(tmp_path):
    client = create_app({"TESTING": True, "DB_PATH": str(tmp_path / "absent.db")}).test_client()
    response = client.get("/")
    assert response.status_code == 200
    controls = Controls()
    controls.feed(response.get_data(as_text=True))
    assert len(controls.controls) == 10
    html = response.get_data(as_text=True)
    for old_control in ["min_salary", "data_years", "ci_diploma", "Try a demo profile"]:
        assert old_control not in html


@pytest.mark.parametrize(
    "sentence,skill,expected",
    [
        ("Commercial experience with SQL and Python", "sql", PARTLY),
        ("Commercial experience with SQL and Python", "python", PARTLY),
        ("SQL and Python experience in a professional setting", "sql", PARTLY),
        ("SQL and Python experience in a professional setting", "python", PARTLY),
        ("Commercial SQL experience and knowledge of Python", "python", MET),
        ("Knowledge of Python and commercial SQL experience", "python", MET),
        ("Knowledge of Python and commercial SQL experience", "sql", PARTLY),
        ("Professional SQL experience is not required", "sql", MET),
        ("Proven experience with SQL in a professional setting", "sql", PARTLY),
        ("Knowledge of SQL in the retail industry", "sql", MET),
        ("Professional communication and knowledge of SQL", "sql", MET),
        ("Experience with Python, commercial SQL experience", "python", MET),
    ],
)
def test_professional_experience_is_scoped_to_the_requested_skill(sentence, skill, expected):
    tax = get_taxonomy()
    profile = profile_from_dict({"skills": ["sql"]})
    req = {
        "req_id": "1",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": sentence,
        "tags": [("skill", skill)],
    }
    result = evaluate_requirement(req, profile, tax, Phraser(tax))
    assert next(tag for tag in result.tags if tag.tag_id == skill).status == expected


def test_commercial_skill_requirement_is_not_removed_as_generic_data_years():
    profile = profile_from_dict({"skills": ["sql"]})
    req = {
        "req_id": "1",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": "2 years commercial SQL experience in a data analyst role",
        "tags": [("skill", "sql")],
    }
    result = match_vacancy(profile, {"vacancy_id": "1"}, [req])
    assert len(result.coverage) == 1
    assert result.coverage[0].status == PARTLY


def test_absent_skill_is_gap_even_when_commercial_experience_is_requested():
    tax = get_taxonomy()
    req = {
        "req_id": "1",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": "Commercial SQL experience",
        "tags": [("skill", "sql")],
    }
    assert evaluate_requirement(req, profile_from_dict({}), tax, Phraser(tax)).status == GAP


def test_old_role_taxonomy_is_not_loaded(tmp_path):
    import shutil

    from skillmatch import config
    from skillmatch.taxonomy import load_taxonomy

    for source in config.TAXONOMY_DIR.glob("*.yaml"):
        shutil.copy2(source, tmp_path / source.name)
    (tmp_path / "role_archetypes.yaml").write_text("deliberately invalid: [")
    assert len(load_taxonomy(tmp_path).archetypes) == 31


def test_authored_templates_have_no_inline_styles_and_colours_live_in_tokens():
    import re

    root = Path(__file__).resolve().parents[1] / "skillmatch/web"
    for source in [
        *root.joinpath("templates").rglob("*.html"),
        *root.joinpath("static").glob("*.css"),
        *root.joinpath("static").glob("*.js"),
    ]:
        if source.name == "tokens.css":
            continue
        text = source.read_text()
        assert not re.search(r"\bstyle\s*=", text)
        assert not re.search(r"#[0-9a-fA-F]{3,8}\b|\brgba?\(", text)


@pytest.mark.parametrize("level,expected", [(0, GAP), (5, GAP), (6, MET), (7, MET), (8, MET)])
def test_degree_or_equivalent_requires_level_six_even_with_subject_skill_tags(level, expected):
    tax = get_taxonomy()
    req = {
        "req_id": "degree",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": "A degree in data analysis or equivalent",
        "tags": [("skill", "data_analysis")],
    }
    result = evaluate_requirement(
        req, profile_from_dict({"highest_qualification": level}), tax, Phraser(tax)
    )
    assert result.status == expected
    assert all(tag.tag_type == "qualification" for tag in result.tags)
