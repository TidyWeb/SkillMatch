import json
import sqlite3

import pandas as pd
import pytest

from skillmatch import config
from skillmatch.etl.dedupe import norm_employer, norm_title, norm_town
from skillmatch.etl.pipeline import remote_status, run
from skillmatch.filters import check_title, is_data_role, is_training_course
from skillmatch.parse import html_to_lines, parse_advert, parse_salary
from skillmatch.sources.base import Vacancy
from skillmatch.text import clean_text


@pytest.mark.parametrize("value", [None, "", " \t\n ", float("nan"), pd.NA, pd.NaT, "NaN", "<NA>"])
def test_missing_text_is_safe_across_boundaries(value):
    assert clean_text(value) == ""
    assert norm_title(value) == norm_employer(value) == norm_town(value) == ""
    assert html_to_lines(value) == []
    assert parse_salary(value) is None
    assert parse_advert(value, value).description_text == ""
    assert check_title(value).excluded_by is None
    assert not is_data_role(value, value)
    assert not is_training_course(value, value)
    assert not remote_status({"source": "reed", "location_text": value}, "unknown")


def test_many_blank_fields_remain_collected_through_complete_pipeline(tmp_path):
    records = json.loads(config.FIXTURES_PATH.read_text())[:5]
    missing = [None, "", " \t", float("nan"), None]
    for n, (record, value) in enumerate(zip(records, missing, strict=True)):
        record.update(
            title=value,
            employer=value,
            location_text=value,
            salary_text=value,
            postcode=value,
            description_html=value,
            description_text=value,
            remote_hint=value,
            salary_period=value,
            expiration_date=value,
            posted_date=value,
            url=value,
            source_id=f"blank-{n}",
        )
    source = tmp_path / "blanks.json"
    source.write_text(json.dumps(records))
    result = run(
        "fixtures",
        db_path=tmp_path / "blanks.db",
        reports_dir=tmp_path / "reports",
        fixtures_path=source,
        offline=True,
    )
    assert result.stage_counts["extracted"] == 5
    assert len(result.observations) == 5
    assert result.shown == 0
    assert all(
        r["outcome"] == "other" and r["outcome_note"] == "title unavailable"
        for r in result.observations
    )
    conn = sqlite3.connect(result.db_path)
    values = conn.execute(
        "select title, employer, location_text, salary_text from vacancies"
    ).fetchall()
    assert all(row == ("", None, None, None) for row in values)
    conn.close()


def test_adapter_record_handles_pandas_nulls_before_serialization():
    vacancy = Vacancy(
        source="reed",
        source_id="x",
        source_tier="A",
        title=pd.NA,
        url="",
        employer=float("nan"),
        location_text=pd.NA,
        description_html=pd.NA,
        salary_text=pd.NaT,
    )
    row = vacancy.to_dict()
    assert row["title"] == ""
    assert row["location_text"] is None
    assert row["employer"] is None
    assert row["salary_text"] is None
    assert row["description_coverage"] == "unavailable"
