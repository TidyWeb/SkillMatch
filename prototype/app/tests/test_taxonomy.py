import shutil

import pytest

from skillmatch import config
from skillmatch.taxonomy import TaxonomyError, compile_phrase, get_taxonomy, load_taxonomy


@pytest.fixture
def tax():
    return get_taxonomy()


@pytest.fixture
def tax_copy(tmp_path):
    for f in config.TAXONOMY_DIR.glob("*.yaml"):
        shutil.copy(f, tmp_path / f.name)
    return tmp_path


def test_project_taxonomy_is_valid(tax):
    assert len(tax.skills) >= 45
    assert len(tax.competencies) >= 30
    assert len(tax.archetypes) >= 38


def test_required_competencies_present(tax):
    for cid in [
        "stakeholder_management",
        "communicating_non_technical",
        "reporting_to_leadership",
        "kpi_monitoring",
        "budget_cost_control",
        "stock_inventory_supply",
        "scheduling_rota_planning",
        "process_improvement",
        "project_management",
        "team_leadership",
        "training_others",
        "regulatory_compliance",
        "attention_to_detail",
        "problem_solving_pressure",
        "customer_insight",
        "research_methods",
        "technical_writing",
        "data_entry_records",
        "change_management",
        "commercial_awareness",
        "negotiation",
        "confidential_data",
        "independent_working",
        "multi_site_coordination",
    ]:
        assert cid in tax.competencies, cid


def test_course_covered_skills(tax):
    covered = {s.id for s in tax.skills.values() if s.course_covered}
    for sid in ["python", "pandas", "power_bi", "statistics", "git", "etl"]:
        assert sid in covered
    for sid in ["sql", "excel", "google_sheets", "r_language"]:
        assert not tax.skills[sid].course_covered


def test_families_are_symmetric(tax):
    assert "power_bi" in tax.related_skills("tableau")
    assert "tableau" in tax.related_skills("power_bi")
    assert "postgresql" in tax.related_skills("t_sql")
    assert "google_sheets" in tax.related_skills("excel")
    assert "python" in tax.related_skills("r_language")


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Strong Power BI skills including DAX", {"power_bi"}),
        ("Advanced proficiency in SQL.", {"sql"}),
        ("Experience with T-SQL and SSIS", {"t_sql"}),
        ("Knowledge of Python or R", {"python", "r_language"}),
        ("Experience in R&D environments", set()),
        ("You will excel in a fast-paced team", set()),
        ("Excellent Excel skills including pivot tables", {"excel"}),
    ],
)
def test_skill_tagging(tax, text, expected):
    got = {i for t, i in tax.tag(text) if t == "skill"}
    assert expected <= got
    if not expected:
        assert not got & {"r_language", "excel"}


@pytest.mark.parametrize(
    "text, competency",
    [
        ("Producing reports for senior stakeholders", "reporting_to_leadership"),
        (
            "Explain complex information clearly to non-technical stakeholders",
            "communicating_non_technical",
        ),
        ("Excellent attention to detail and data accuracy", "attention_to_detail"),
        ("Ability to manage competing priorities effectively", "organisation_prioritising"),
        ("Must have experience in the automotive industry", "sector_manufacturing_logistics"),
        ("Experience managing stock levels and suppliers", "stock_inventory_supply"),
    ],
)
def test_competency_tagging(tax, text, competency):
    assert ("competency", competency) in tax.tag(text)


def test_senior_stakeholders_is_not_a_seniority_tag(tax):
    tags = tax.tag("Confidence working with senior stakeholders")
    assert ("competency", "reporting_to_leadership") in tags
    assert ("competency", "team_leadership") not in tags


def test_phrase_language():
    assert compile_phrase("stakeholder*").search("Stakeholders across the business")
    assert compile_phrase("present* ... findings").search("presenting your key findings")
    assert not compile_phrase("present* ... findings").search(
        "present one two three four five six findings"
    )


def test_archetype_fuzzy_match(tax):
    assert tax.match_archetype("Head Chef")[0] == "kitchen_manager"
    assert tax.match_archetype("staff nurse (NHS)")[0] == "nurse"
    assert tax.match_archetype("Secondary school teacher")[0] == "teacher"
    assert tax.match_archetype("zzzz qqqq") is None


def test_archetypes_reference_existing_competencies(tax):
    for a in tax.archetypes.values():
        assert set(a.competencies) <= tax.competencies.keys()


def test_bad_competency_reference_is_reported(tax_copy):
    path = tax_copy / "role_archetypes.yaml"
    path.write_text(path.read_text().replace("research_methods,", "research_methodz,", 1))
    with pytest.raises(TaxonomyError) as exc:
        load_taxonomy(tax_copy)
    msg = str(exc.value)
    assert "role_archetypes.yaml" in msg and "research_methodz" in msg and "does not exist" in msg


def test_missing_header_and_bad_yaml_reported(tax_copy):
    (tax_copy / "phrasing.yaml").write_text("answers: [unclosed\n")
    with pytest.raises(TaxonomyError) as exc:
        load_taxonomy(tax_copy)
    msg = str(exc.value)
    assert "DRAFT: for team review" in msg
    assert "not valid YAML" in msg


def test_unknown_placeholder_and_duplicate_id_reported(tax_copy):
    p = tax_copy / "phrasing.yaml"
    p.write_text(p.read_text().replace("as {role}, {evidence}.", "as {role}, {evidense}.", 1))
    s = tax_copy / "technical_skills.yaml"
    s.write_text(s.read_text().replace("id: numpy", "id: pandas", 1))
    with pytest.raises(TaxonomyError) as exc:
        load_taxonomy(tax_copy)
    msg = str(exc.value)
    assert "unknown placeholder {evidense}" in msg
    assert "'pandas': id is used twice" in msg
