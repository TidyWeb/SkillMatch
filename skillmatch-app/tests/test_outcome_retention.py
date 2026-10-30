from collections import Counter
from datetime import date

import pytest

from skillmatch.etl.outcomes import OUTCOMES, funnel_rows, observation_rows
from skillmatch.etl.pipeline import extract_reed_live, run


def test_each_collected_occurrence_has_exactly_one_outcome():
    records = [
        {"vacancy_id": v, "source": s}
        for v, s in [
            ("reed:1", "reed"),
            ("reed:1", "reed"),
            ("lever:2", "lever"),
            ("reed:3", "reed"),
        ]
    ]
    vacancies = [
        {"vacancy_id": "reed:1", "source": "reed", "excluded_reason": None, "is_primary": 0},
        {"vacancy_id": "lever:2", "source": "lever", "excluded_reason": None, "is_primary": 1},
        {"vacancy_id": "reed:3", "source": "reed", "excluded_reason": "expired", "is_primary": 1},
    ]
    obs = observation_rows(records, vacancies, [{"vacancy_id": "reed:1", "primary_id": "lever:2"}])
    assert Counter(r["outcome"] for r in obs) == {
        "shown": 1,
        "expired": 1,
        "duplicate within the same source": 1,
        "duplicate of an advert from another source": 1,
    }
    for row in funnel_rows(obs, "r1", "2026-10-27"):
        assert row["collected"] == sum(row[k] for k in OUTCOMES)
    assert obs[0]["duplicate_source"] == "lever"


def test_fixture_in_live_collection_fails_before_database(monkeypatch, tmp_path):
    from skillmatch import config
    from skillmatch.etl import pipeline

    monkeypatch.setattr(config, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(
        pipeline,
        "extract_live",
        lambda *args: (
            [{"source": "fixture", "source_id": "bad", "source_tier": "fixture"}],
            [],
            {},
        ),
    )
    with pytest.raises(ValueError, match="Fixture row"):
        run("live", db_path=tmp_path / "live.db", reports_dir=tmp_path, offline=True)
    assert not (tmp_path / "live.db").exists()


def test_blank_and_failed_details_remain_collected(monkeypatch):
    from skillmatch.etl import pipeline

    class Reed:
        enabled = True
        stats = {}
        search_observations = []

        def __init__(self, **kwargs):
            pass

        def search(self):
            return {
                n: {"jobId": n, "jobTitle": "Data Analyst", "locationName": "Birmingham"}
                for n in (1, 2)
            }

        def detail(self, n):
            if n == 1:
                return None
            raise TimeoutError()

    from skillmatch.sources.reed import ReedAdapter

    Reed.from_search_row = ReedAdapter.from_search_row
    monkeypatch.setattr(pipeline, "ReedAdapter", Reed)

    class Client:
        requests_made = 0

    out, rows, source_run = extract_reed_live("r", Client(), date(2026, 10, 27))
    assert len(out) == len(rows) == source_run["fetched"] == 2
    assert all("details unavailable" in r["pre_excluded_reason"] for r in out)
    assert len(source_run["_source_log"]) == 2
