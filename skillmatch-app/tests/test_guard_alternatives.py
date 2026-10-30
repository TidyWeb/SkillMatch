"""Alternatives are choices; separate technical requirements remain independent."""

import json
from pathlib import Path

import pytest

from skillmatch.guards import _missing_groups, apply_tier_guard
from skillmatch.match import match_vacancy
from skillmatch.profile import profile_from_dict
from skillmatch.repository import load
from skillmatch.taxonomy import get_taxonomy


@pytest.mark.parametrize(
    "text,selected",
    [
        ("Python or R", {"python"}),
        ("Power BI, Tableau or Qlik", {"tableau"}),
        ("Power BI, Tableau or Qlik", {"power_bi"}),
        ("Power BI, Tableau or Qlik", {"qlik"}),
        ("Microsoft Fabric or Azure", {"azure"}),
        ("SQL and/or Python", {"python"}),
    ],
)
def test_any_named_alternative_satisfies_the_group(text, selected):
    assert _missing_groups(text, selected, get_taxonomy()) == []


def test_no_alternative_held_names_only_those_alternatives():
    missing = _missing_groups("Power BI, Tableau or Qlik", set(), get_taxonomy())
    assert missing == ["Power BI / Tableau / Qlik"]
    assert _missing_groups("Python or R", set(), get_taxonomy()) == ["Python / R"]


def test_or_does_not_swallow_other_required_tools():
    tax = get_taxonomy()
    assert _missing_groups("Python or R, alongside SQL and ETL", {"python", "etl"}, tax) == ["SQL"]
    assert _missing_groups("SQL and Python or R", {"python"}, tax) == ["SQL"]
    missing = _missing_groups("Fabric or Azure, alongside solid SQL and ETL", {"sql", "etl"}, tax)
    assert missing == ["Azure / Microsoft Fabric"]


@pytest.mark.parametrize(
    "suffix", ["or similar", "or equivalent", "or comparable", "or other cloud tools"]
)
def test_generic_alternative_uses_same_taxonomy_category(suffix):
    tax = get_taxonomy()
    text = "BigQuery " + suffix
    assert _missing_groups(text, {"azure"}, tax) == []
    missing = _missing_groups(text, {"python"}, tax)
    assert len(missing) == 1 and "a platform skill" in missing[0]
    assert _missing_groups(text, {"gcp"}, tax) == []


def test_other_tool_type_does_not_add_a_second_requirement():
    assert (
        _missing_groups("BigQuery or other data warehouse tools", {"azure"}, get_taxonomy()) == []
    )


def test_basic_database_category_can_satisfy_equivalent_database_tool():
    assert _missing_groups("SQL or equivalent", {"databases"}, get_taxonomy()) == []
    assert _missing_groups("SQL knowledge", {"databases"}, get_taxonomy()) == ["SQL"]


def test_nested_generic_database_word_does_not_mask_named_database_alternatives():
    tax = get_taxonomy()
    assert _missing_groups("Oracle database or PostgreSQL", {"databases"}, tax) == [
        "Oracle database / PostgreSQL"
    ]


def test_sql_added_chip_clears_all_sql_only_caps():
    tax = get_taxonomy()
    for text in [
        "SQL",
        "SQL skills",
        "Experience with SQL",
        "Knowledge of SQL",
        "SQL queries",
        "SQL essential",
    ]:
        original = profile_from_dict({})
        with_sql = profile_from_dict({"skills": ["sql"]})
        reqs = [
            {
                "req_id": str(i),
                "n": i,
                "strength": "essential",
                "confidence": confidence,
                "evidence_sentence": sentence,
                "tags": [],
            }
            for i, (sentence, confidence) in enumerate(
                [("Python", "stated"), ("Statistics", "stated"), (text, "inferred")]
            )
        ]
        matched = match_vacancy(original, {"vacancy_id": "sql-only"}, reqs)
        assert matched.tier == "strong"
        assert apply_tier_guard(matched, original, tax).tier == "good"
        assert apply_tier_guard(matched, with_sql, tax).tier == "strong"


def test_database_familiarity_does_not_create_sql_caps_but_schema_and_warehouses_do():
    tax = get_taxonomy()
    selected = set(profile_from_dict({}).skills)
    assert "databases" in selected and "sql" not in selected
    assert _missing_groups("Experience with databases", selected, tax) == []
    assert _missing_groups("Dimensional modelling and data warehouses", selected, tax) == [
        "Data modelling (schema design)",
        "Data warehousing",
    ]


@pytest.mark.parametrize("pid", ["chef_wolverhampton", "teacher_stoke", "nurse_worcester"])
def test_named_live_alternatives_for_each_baseline(pid):
    from scripts.ui_simplification_compare import convert_profile

    root = Path(__file__).parents[1]
    path = root / "reports/ui_simplification_baseline.json"
    if not path.exists():
        pytest.skip("Local comparison evidence is not present")
    baseline = json.loads(path.read_text())
    db = root / baseline["database"]
    if not db.exists():
        pytest.skip("Live comparison snapshot is not present")
    tax = get_taxonomy()
    raw, _ = convert_profile(baseline["profiles"][pid]["profile"], tax)
    profile = profile_from_dict(raw)
    snapshot = load(db)
    for job in ["remote_ok:1137531", "reed:57451268"]:
        reqs = snapshot.requirements[job]
        result = match_vacancy(profile, snapshot.vacancies[job], reqs, tax=tax)
        guarded = apply_tier_guard(result, profile, tax)
        if job.startswith("remote_ok"):
            python_r = next(r for r in reqs if "Python or R" in r["evidence_sentence"])
            assert not any(f.req_id == python_r["req_id"] for f in guarded.guard_findings)
            assert not any(name == "R" for f in guarded.guard_findings for name in f.missing_skills)
        else:
            assert guarded.tier == "good"
            assert "Azure / Microsoft Fabric" in guarded.guard_reason
    assert all(
        ident in tax.skills
        for reqs in snapshot.requirements.values()
        for req in reqs
        for kind, ident in req["tags"]
        if kind == "skill"
    )


@pytest.mark.parametrize("pid", ["chef_wolverhampton", "teacher_stoke", "nurse_worcester"])
def test_sql_chip_clears_every_sql_only_guard_cap_in_live_results(pid):
    from scripts.ui_simplification_compare import convert_profile
    from skillmatch.results import build_shortlist

    root = Path(__file__).parents[1]
    path = root / "reports/ui_simplification_baseline.json"
    if not path.exists():
        pytest.skip("Local comparison evidence is not present")
    baseline = json.loads(path.read_text())
    db = root / baseline["database"]
    if not db.exists():
        pytest.skip("Live comparison snapshot is not present")
    tax = get_taxonomy()
    raw, _ = convert_profile(baseline["profiles"][pid]["profile"], tax)
    snapshot = load(db)
    before = build_shortlist(profile_from_dict(raw), snapshot)
    sql_only = [
        m.vacancy_id
        for m in before.results
        if getattr(m, "guard_reason", None)
        and {name for f in m.guard_findings for name in f.missing_skills} == {"SQL"}
    ]
    if pid != "chef_wolverhampton":
        assert sql_only
    raw["skills"] = [*raw["skills"], "sql"]
    after = {m.vacancy_id: m for m in build_shortlist(profile_from_dict(raw), snapshot).results}
    assert all(after[job].guard_reason is None for job in sql_only)
