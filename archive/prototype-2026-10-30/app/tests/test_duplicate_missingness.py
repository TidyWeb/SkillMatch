import pandas as pd

from skillmatch.etl.dedupe import group_duplicates


def _record(vacancy_id, *, employer=None, location=None, description="", url=None):
    return {
        "vacancy_id": vacancy_id,
        "source": "reed",
        "source_tier": "A",
        "title": "Data Analyst",
        "employer": employer,
        "location_text": location,
        "description_text": description,
        "url": url,
        "salary_min": None,
        "salary_max": None,
        "salary_stated": False,
        "posted_date": None,
        "n_requirements": 0,
        "excluded_reason": None,
    }


def _group(records):
    df = pd.DataFrame(records)
    duplicates = group_duplicates(df)
    return df, duplicates


def test_same_title_with_missing_employer_and_location_is_not_enough():
    df, duplicates = _group(
        [
            _record("reed:1", description="SQL and reporting responsibilities for a finance team."),
            _record("reed:2", description="Python and dashboard work for a health research team."),
        ]
    )

    assert duplicates.empty
    assert df["is_primary"].tolist() == [1, 1]
    assert df["duplicate_group"].isna().all()


def test_equal_complete_exact_keys_still_group():
    df, duplicates = _group(
        [
            _record("reed:1", employer="Example Ltd", location="Birmingham"),
            _record("reed:2", employer="Example Limited", location="Birmingham"),
        ]
    )

    assert len(duplicates) == 2
    assert df["is_primary"].sum() == 1
    assert df["duplicate_group"].notna().all()


def test_same_url_can_prove_match_without_employer_or_location():
    df, duplicates = _group(
        [
            _record("reed:1", url="https://jobs.example.test/123", description="Short excerpt one"),
            _record(
                "reed:2", url="https://jobs.example.test/123/", description="Short excerpt two"
            ),
        ]
    )

    assert len(duplicates) == 2
    assert df["is_primary"].sum() == 1


def test_same_substantial_content_can_prove_match_without_employer_or_location():
    description = (
        "The successful candidate will maintain scheduled reporting, validate incoming data, "
        "support colleagues with dashboard questions, document recurring processes, and work "
        "with SQL queries to improve the accuracy and usefulness of management information."
    )
    df, duplicates = _group(
        [
            _record("reed:1", description=description),
            _record("reed:2", description=description),
        ]
    )

    assert len(duplicates) == 2
    assert df["is_primary"].sum() == 1
