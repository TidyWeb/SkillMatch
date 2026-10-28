import pytest

from skillmatch.match import GAP, MET, evaluate_requirement
from skillmatch.phrasing import Phraser
from skillmatch.profile import profile_from_dict
from skillmatch.taxonomy import get_taxonomy


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Relational databases with tables and keys", {"databases"}),
        ("Data modelling and dimensional modeling; star schema design", {"data_modelling"}),
        ("Data warehouses, lakehouse and data lake", {"data_warehousing"}),
        (
            "SQL, SQL Server, BigQuery, Snowflake and Azure Data Lake",
            {"sql", "t_sql", "gcp", "databricks", "azure"},
        ),
    ],
)
def test_database_taxonomy_split_and_unchanged_neighbouring_skills(text, expected):
    tax = get_taxonomy()
    assert expected <= {skill_id for tag_type, skill_id in tax.tag(text) if tag_type == "skill"}


def test_course_database_familiarity_is_met_without_inventing_sql_gap():
    tax = get_taxonomy()
    req = {
        "req_id": "legacy-database",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": "Familiarity with relational databases is required.",
        "tags": [["skill", "databases_general"]],
    }
    result = evaluate_requirement(
        req, profile_from_dict({"skills": ["databases"]}, tax), tax, Phraser(tax)
    )
    assert [(tag.tag_id, tag.status) for tag in result.tags] == [("databases", MET)]
    assert result.status == MET


def test_modelling_and_warehousing_are_distinct_gaps():
    tax = get_taxonomy()
    req = {
        "req_id": "split-database-requirements",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": "Experience with schema design and data warehouses.",
        "tags": [],
    }
    result = evaluate_requirement(
        req, profile_from_dict({"skills": ["databases"]}, tax), tax, Phraser(tax)
    )
    assert {tag.tag_id for tag in result.tags if tag.status == GAP} == {
        "data_modelling",
        "data_warehousing",
    }


def test_all_three_database_skills_can_be_selected():
    tax = get_taxonomy()
    profile = profile_from_dict(
        {"skills": ["databases", "data_modelling", "data_warehousing"]}, tax
    )
    assert {"databases", "data_modelling", "data_warehousing"} <= set(profile.skills)


def test_only_database_basics_are_course_covered():
    tax = get_taxonomy()
    assert tax.skills["databases"].course_covered is True
    assert tax.skills["data_modelling"].course_covered is False
    assert tax.skills["data_warehousing"].course_covered is False
    assert tax.skills["databases"].portfolio_idea


def test_stale_sql_tag_is_dropped_when_sentence_does_not_name_sql():
    tax = get_taxonomy()
    req = {
        "req_id": "stale-sql-tag",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": "Experience with a relational database.",
        "tags": [["skill", "sql"], ["skill", "databases_general"]],
    }
    result = evaluate_requirement(
        req, profile_from_dict({"skills": ["databases"]}, tax), tax, Phraser(tax)
    )
    assert [tag.tag_id for tag in result.tags] == ["databases"]
