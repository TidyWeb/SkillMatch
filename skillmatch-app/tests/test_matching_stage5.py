"""Stage 5 matching-policy regressions, including exact live advert wording."""

import json
from pathlib import Path

import pytest

from skillmatch.match import GAP, MET, PARTLY, evaluate_requirement, match_vacancy
from skillmatch.phrasing import Phraser
from skillmatch.profile import Profile, profile_from_dict
from skillmatch.taxonomy import get_taxonomy

FIXTURES = Path(__file__).parent / "fixtures" / "stage5_requirements.json"
ACTUAL_REQUIREMENTS = json.loads(FIXTURES.read_text(encoding="utf-8"))


@pytest.mark.parametrize("requirement", ACTUAL_REQUIREMENTS, ids=lambda req: req["req_id"])
def test_actual_report_experience_wording_marks_selected_skill_partly(requirement):
    tax = get_taxonomy()
    skill_id = next(tag[1] for tag in requirement["tags"] if tag[0] == "skill")
    profile = profile_from_dict({"skills": [skill_id]}, tax)
    coverage = evaluate_requirement(requirement, profile, tax, Phraser(tax))

    skill_result = next(tag for tag in coverage.tags if tag.tag_type == "skill")
    assert skill_result.status == PARTLY, requirement["req_id"]
    assert "Advert asks for" in skill_result.answer
    assert coverage.status == PARTLY
    if requirement["req_id"] == "reed:57479756#22":
        assert "corporate environment" in skill_result.answer
    elif requirement["req_id"] != "reed:57486191#23":
        assert "experience as" in skill_result.answer
    if requirement["req_id"] == "reed:57486191#23":
        area = next(
            area for area in tax.archetypes.values() if "training_others" in area.competencies
        )
        with_competency = profile_from_dict(
            {"skills": [skill_id], "areas": [{"id": area.id, "skills": ["training_others"]}]}, tax
        )
        checked = evaluate_requirement(requirement, with_competency, tax, Phraser(tax))
        assert next(tag for tag in checked.tags if tag.tag_type == "competency").status == MET
        assert checked.status == PARTLY


@pytest.mark.parametrize(
    "sentence,skill_id",
    [
        ("Experience using Power BI", "power_bi"),
        ("Experience using tools such as SQL", "sql"),
        ("Experience with SQL", "sql"),
        ("Knowledge of SQL", "sql"),
        ("Ability to use SQL", "sql"),
        ("Strong SQL skills", "sql"),
        ("Experience with Python would be a plus", "python"),
        ("Proven SQL experience would be considered a plus", "sql"),
        ("Prior machine learning experience is helpful but not required", "machine_learning"),
        ("Experience with Power BI is preferable", "power_bi"),
    ],
)
def test_plain_familiarity_and_optional_experience_remain_met(sentence, skill_id):
    tax = get_taxonomy()
    req = {
        "req_id": "plain",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": sentence,
        "tags": [["skill", skill_id]],
    }
    result = evaluate_requirement(
        req, profile_from_dict({"skills": [skill_id]}, tax), tax, Phraser(tax)
    )
    assert result.tags[0].status == MET


@pytest.mark.parametrize(
    "sentence,skill_id",
    [
        ("Proven experience using SQL", "sql"),
        ("Significant experience with Python", "python"),
        ("Extensive experience in Power BI", "power_bi"),
        ("5+ years' experience using Tableau", "tableau"),
        ("Experience with SQL in a professional setting", "sql"),
        ("Experience with Python in industry", "python"),
    ],
)
def test_explicit_work_experience_qualifiers_are_partly(sentence, skill_id):
    tax = get_taxonomy()
    req = {
        "req_id": "qualified",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": sentence,
        "tags": [["skill", skill_id]],
    }
    result = evaluate_requirement(
        req, profile_from_dict({"skills": [skill_id]}, tax), tax, Phraser(tax)
    )
    assert result.tags[0].status == PARTLY


def test_desirable_strength_never_downgrades_a_selected_skill():
    tax = get_taxonomy()
    req = {
        "req_id": "desirable",
        "n": 1,
        "strength": "desirable",
        "confidence": "stated",
        "evidence_sentence": "Significant experience as a Python developer would be useful.",
        "tags": [["skill", "python"]],
    }
    result = evaluate_requirement(
        req, profile_from_dict({"skills": ["python"]}, tax), tax, Phraser(tax)
    )
    assert result.status == MET


def test_a_missing_technical_skill_caps_disjunction_at_partly():
    tax = get_taxonomy()
    req = {
        "req_id": "reed:57451268#6",
        "n": 6,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": (
            "The environment is centred around the Microsoft data stack, so we’re looking for "
            "someone with strong experience across either Microsoft Fabric or Azure data "
            "services, alongside solid SQL, data modelling and ETL capabilities."
        ),
        "tags": [["skill", "sql"], ["skill", "data_modelling"], ["skill", "etl"]],
    }
    profile = profile_from_dict({"skills": ["etl"]}, tax)
    coverage = evaluate_requirement(req, profile, tax, Phraser(tax))
    assert coverage.status == PARTLY
    assert {tag.tag_id for tag in coverage.tags if tag.status == GAP} >= {"azure", "sql"}
    assert next(tag for tag in coverage.tags if tag.tag_id == "etl").status == MET

    missing_all = evaluate_requirement(req, Profile(skills=[]), tax, Phraser(tax))
    assert missing_all.status == GAP


def test_partly_experienced_skill_is_not_masked_by_met_or_alternative():
    tax = get_taxonomy()
    req = {
        "req_id": "mixed-or",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": "SQL or proven experience with Python.",
        "tags": [["skill", "sql"], ["skill", "python"]],
    }
    result = evaluate_requirement(
        req, profile_from_dict({"skills": ["sql", "python"]}, tax), tax, Phraser(tax)
    )
    assert [tag.status for tag in result.tags] == [MET, PARTLY]
    assert result.status == PARTLY


@pytest.mark.parametrize("spelling", ["Microsoft Fabric", "Fabric", "Synapse Analytics"])
def test_new_azure_platform_spellings_are_retagged_without_database_changes(spelling):
    tax = get_taxonomy()
    req = {
        "req_id": "old-snapshot",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": f"Strong experience with {spelling}.",
        "tags": [],
    }
    coverage = evaluate_requirement(req, profile_from_dict({}), tax, Phraser(tax))
    assert [(tag.tag_type, tag.tag_id, tag.status) for tag in coverage.tags] == [
        ("skill", "azure", GAP)
    ]
    assert "Microsoft Azure data tools" in coverage.gaps[0].gap
    if "Fabric" in spelling:
        assert "This includes Microsoft Fabric." in coverage.gaps[0].gap


def test_named_reed_job_api_explains_missing_azure_tools():
    db = Path(__file__).parents[1] / "data/processed/skillmatch_live_20261027T124644998193Z.db"
    if not db.exists():
        pytest.skip("The read-only Stage 4 live snapshot is not present")
    from skillmatch.web import create_app

    client = create_app({"TESTING": True, "DB_PATH": str(db)}).test_client()
    profile = {"skills": ["etl", "data_analysis", "power_bi"]}
    response = client.post("/job/reed:57451268", data={"profile": json.dumps(profile)})
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Microsoft Azure data tools: not in your profile yet." in html


def test_named_data_engineer_keeps_strong_with_its_one_partly_requirement():
    db = Path(__file__).parents[1] / "data/processed/skillmatch_live_20261027T124644998193Z.db"
    baseline_path = Path(__file__).parents[1] / "reports/ui_simplification_baseline.json"
    if not db.exists() or not baseline_path.exists():
        pytest.skip("The read-only Stage 4 live snapshot and baseline are not present")

    from scripts.ui_simplification_compare import convert_profile
    from skillmatch.repository import load

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    snapshot = load(db)
    tax = get_taxonomy()
    vacancy_id = "reed:57451268"
    for profile_id, data in baseline["profiles"].items():
        converted, lost = convert_profile(data["profile"], tax)
        assert not lost, profile_id
        result = match_vacancy(
            profile_from_dict(converted, tax),
            snapshot.vacancies[vacancy_id],
            snapshot.requirements[vacancy_id],
            tax=tax,
        )
        partly = [
            coverage
            for coverage in result.coverage
            if coverage.strength == "essential" and coverage.status == PARTLY
        ]
        target = next(c for c in partly if c.req_id == "reed:57451268#6")
        assert result.tier == "strong", profile_id
        assert len(partly) == 1, profile_id
        assert target.confidence == "inferred"
        assert not target.counts
        assert {tag.tag_id for tag in target.gaps} >= {"azure", "sql"}


def test_all_named_missing_skills_are_found_even_when_snapshot_tags_are_stale():
    tax = get_taxonomy()
    req = {
        "req_id": "stale-sql",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": "Python or SQL skills",
        "tags": [["skill", "python"]],
    }
    cov = evaluate_requirement(req, profile_from_dict({}), tax, Phraser(tax))
    assert cov.status == PARTLY
    assert any(tag.tag_id == "sql" and tag.status == GAP for tag in cov.tags)
