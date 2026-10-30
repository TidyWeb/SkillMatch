import sqlite3

import pytest

from skillmatch.etl.pipeline import run


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    d = tmp_path_factory.mktemp("etl")
    result = run("fixtures", db_path=d / "test.db", reports_dir=d / "reports", offline=True)
    conn = sqlite3.connect(d / "test.db")
    yield result, conn
    conn.close()


def q(conn, sql):
    return conn.execute(sql).fetchall()


def test_all_tables_loaded(built):
    _, conn = built
    for table in [
        "vacancies",
        "requirements",
        "requirement_tags",
        "sources",
        "source_runs",
        "duplicates",
        "places",
        "meta",
    ]:
        assert q(conn, f"select count(*) from {table}")[0][0] > 0, table


def test_meta_records_mode(built):
    _, conn = built
    meta = dict(q(conn, "select key, value from meta"))
    assert meta["data_mode"] == "fixtures"
    assert meta["requests_made"] == "0"


def test_expired_dropped_and_excluded_kept(built):
    result, conn = built
    assert result.stage_counts["dropped as expired"] == 1
    reasons = dict(q(conn, "select excluded_reason, count(*) from vacancies group by 1"))
    assert reasons["senior role"] >= 8
    assert reasons["training course, not a job"] == 3
    assert reasons["outside the West Midlands"] == 2
    assert reasons["not a data role"] >= 4
    assert result.shown >= 80


def test_senior_words_recorded(built):
    _, conn = built
    words = {
        w
        for (w,) in q(
            conn, "select title_excluded_word from vacancies where title_excluded_word is not null"
        )
    }
    assert {"senior", "head of", "manager", "lead", "director"} <= words


def test_duplicates_grouped_with_one_primary(built):
    _, conn = built
    groups = q(
        conn,
        "select duplicate_group, sum(is_primary), count(*) from vacancies where duplicate_group is not null group by 1",
    )
    assert len(groups) >= 6
    assert all(primaries == 1 and n >= 2 for _, primaries, n in groups)
    reasons = {r for (r,) in q(conn, "select distinct reason from duplicates")}
    assert {"exact", "near", "primary"} <= reasons


def test_requirements_have_evidence_and_strength(built):
    _, conn = built
    rows = q(conn, "select strength, confidence, evidence_sentence from requirements")
    assert {s for s, _, _ in rows} <= {"essential", "desirable", "duty"}
    assert all(e for _, _, e in rows)
    assert {c for _, c, _ in rows} <= {"stated", "inferred"}


def test_location_flags(built):
    _, conn = built
    unclear = q(conn, "select title from vacancies where location_unclear = 1")
    assert ("Data Analyst",) in unclear
    remote = q(conn, "select count(*) from vacancies where is_remote = 1")[0][0]
    assert remote >= 5
    approx = q(conn, "select count(*) from vacancies where location_approximate = 1")[0][0]
    assert approx >= 1


def test_quality_report_written(built):
    result, _ = built
    text = result.report_path.read_text()
    for heading in [
        "Rows per stage",
        "Missing values per field",
        "Duplicates",
        "Geocoding",
        "Senior roles excluded",
        "Salary coverage",
        "Unclassified",
    ]:
        assert heading in text


def test_mixed_sources_with_missing_fields(tmp_path):
    """Records from different sources carry different fields (NaN in pandas); none may crash."""
    import json

    from skillmatch import config

    recs = json.loads(config.FIXTURES_PATH.read_text())[:5]
    recs[0]["postcode"] = "B4 6AR"
    recs[1]["remote_hint"] = "remote"
    recs[2]["extra"] = None
    path = tmp_path / "mixed.json"
    path.write_text(json.dumps(recs))
    result = run(
        "fixtures",
        db_path=tmp_path / "m.db",
        reports_dir=tmp_path,
        fixtures_path=path,
        offline=True,
    )
    assert result.stage_counts["parsed"] == 5
