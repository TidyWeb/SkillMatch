import csv
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import requests

from skillmatch.etl import recovery


def _write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _set_mtime(path: Path, value: float):
    import os

    os.utime(path, (value, value))


def test_load_recovery_replays_ordered_cache_observations_without_http(tmp_path, monkeypatch):
    run_id = "20261027T124644998193Z"
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    cache_dir = data_dir / "cache"
    data_dir.mkdir()
    with (data_dir / "search_terms.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["term"])
        writer.writeheader()
        writer.writerows([{"term": "data analyst"}, {"term": "data engineer"}])

    monkeypatch.setattr(recovery.config, "REED_GRID", ["Birmingham"])
    monkeypatch.setattr(recovery.config, "REED_BIRMINGHAM_PAGES", 2)
    monkeypatch.setattr(recovery.config, "REED_PAGES", 1)
    monkeypatch.setattr(recovery.config, "REED_DISTANCE_MILES", 27)

    raw = [
        {
            "jobId": 11,
            "jobTitle": "Data Analyst",
            "jobDescription": "Python SQL",
            "locationName": "Birmingham",
            "_matched_terms": ["data analyst", "data engineer"],
        },
        {
            "jobId": 12,
            "jobTitle": "Senior Data Analyst",
            "jobDescription": "Python SQL",
            "locationName": "Birmingham",
            "_matched_terms": ["data analyst"],
        },
    ]
    raw_path = raw_dir / f"reed_{run_id}.json"
    _write_json(raw_path, raw)
    full = {
        "source": "reed",
        "source_id": "11",
        "source_tier": "A",
        "title": "Data Analyst",
        "url": "https://www.reed.co.uk/jobs/11",
        "description_html": "<p>Full detail</p>",
        "description_text": "Full detail",
        "description_coverage": "full",
        "fetched_at": "2026-10-27T12:50:00+00:00",
        "extra": {},
    }
    _write_json(raw_dir / f"reed_details_{run_id}.json", [full])
    for source, rows in (("ats", []), ("we_work_remotely", []), ("remote_ok", []), ("curated", [])):
        _write_json(raw_dir / f"{source}_{run_id}.json", rows)

    requests_by_query = [
        ("data analyst", 0, [{"jobId": 11}, {"jobId": 12}]),
        ("data analyst", 100, []),
        ("data engineer", 0, [{"jobId": 11}]),
    ]
    when = datetime.strptime(run_id, "%Y%m%dT%H%M%S%fZ").replace(tzinfo=UTC).timestamp() + 2
    for term, skip, results in requests_by_query:
        query = (
            f"keywords={term.replace(' ', '+')}&locationName=Birmingham&distanceFromLocation=27"
            f"&resultsToTake=100&resultsToSkip={skip}"
        )
        path = cache_dir / f"cache-{term.split()[1]}-{skip}.json"
        _write_json(
            path,
            {"url": f"https://www.reed.co.uk/api/1.0/search?{query}", "body": {"results": results}},
        )
        _set_mtime(path, when)
    # Page two is cached but is not required after page one returns fewer than 100.
    raw_path.touch()
    _set_mtime(raw_path, when + 20)

    def fail_http(*args, **kwargs):
        raise AssertionError("recovery must not make HTTP requests")

    monkeypatch.setattr(requests, "get", fail_http)

    bundle = recovery.load_recovery(run_id, data_dir)

    assert len(bundle["records"]) == 3
    assert [r["extra"]["search_term"] for r in bundle["records"]] == [
        "data analyst",
        "data analyst",
        "data engineer",
    ]
    assert [r["extra"]["search_page"] for r in bundle["records"]] == [1, 1, 1]
    assert bundle["records"][0]["description_coverage"] == "full"
    assert bundle["records"][0]["fetched_at"] == "2026-10-27T12:50:00+00:00"
    assert bundle["records"][1]["pre_excluded_reason"] == "senior role"
    reed_run = bundle["source_runs"][0]
    assert reed_run["fetched"] == 3
    assert reed_run["kept"] == 1
    assert reed_run["status"] == "ok"
    assert bundle["metadata"]["collection_counts"]["search_queries_needed"] == 2
    assert bundle["metadata"]["collection_counts"]["search_queries_missing_needed_page"] == 0
    assert bundle["metadata"]["recovery_network_requests"] == 0
    assert bundle["metadata"]["collection_complete"] is True


def test_load_recovery_flags_a_missing_next_page_and_a_full_final_page(tmp_path, monkeypatch):
    run_id = "20261027T124644998193Z"
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    cache_dir = data_dir / "cache"
    data_dir.mkdir()
    with (data_dir / "search_terms.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["term"])
        writer.writeheader()
        writer.writerow({"term": "analyst"})
    monkeypatch.setattr(recovery.config, "REED_GRID", ["Birmingham"])
    monkeypatch.setattr(recovery.config, "REED_BIRMINGHAM_PAGES", 2)
    monkeypatch.setattr(recovery.config, "REED_PAGES", 1)
    monkeypatch.setattr(recovery.config, "REED_DISTANCE_MILES", 27)
    raw_path = raw_dir / f"reed_{run_id}.json"
    _write_json(raw_path, [])
    _write_json(raw_dir / f"reed_details_{run_id}.json", [])
    for source in ("ats", "we_work_remotely", "remote_ok", "curated"):
        _write_json(raw_dir / f"{source}_{run_id}.json", [])

    results = [
        {"jobId": i, "jobTitle": "Kitchen Assistant", "jobDescription": "Shift work"}
        for i in range(100)
    ]
    cache_path = cache_dir / "page-zero.json"
    _write_json(
        cache_path,
        {
            "url": "https://www.reed.co.uk/api/1.0/search?keywords=analyst&locationName=Birmingham&distanceFromLocation=27&resultsToTake=100&resultsToSkip=0",
            "body": {"results": results},
        },
    )
    when = datetime.strptime(run_id, "%Y%m%dT%H%M%S%fZ").replace(tzinfo=UTC).timestamp() + 2
    _set_mtime(cache_path, when)
    _set_mtime(raw_path, when + 20)

    missing_bundle = recovery.load_recovery(run_id, data_dir)
    missing_run = missing_bundle["source_runs"][0]
    assert missing_run["status"] == "partial"
    assert (
        missing_bundle["metadata"]["collection_counts"]["search_queries_missing_needed_page"] == 1
    )
    assert missing_run["_source_log"][0]["count"] == 1

    monkeypatch.setattr(recovery.config, "REED_BIRMINGHAM_PAGES", 1)
    truncated_bundle = recovery.load_recovery(run_id, data_dir)
    truncated_run = truncated_bundle["source_runs"][0]
    assert truncated_run["status"] == "partial"
    assert len(truncated_bundle["metadata"]["collection_counts"]["truncated_searches"]) == 1
    assert truncated_run["_source_log"][0]["count"] == 1


def test_load_back_snapshot_rebuilds_records_readonly_and_marks_limitations(tmp_path):
    data_dir = tmp_path / "data"
    raw_dir = data_dir / "raw"
    data_dir.mkdir()
    run_id = "20261021T203222Z"
    backup = tmp_path / "backup.db"
    connection = sqlite3.connect(backup)
    connection.executescript(
        """
        CREATE TABLE source_runs (
            run_id TEXT, source_id TEXT, mode TEXT, started_at TEXT, finished_at TEXT,
            fetched INTEGER, kept INTEGER, requests INTEGER, status TEXT, message TEXT
        );
        CREATE TABLE vacancies (
            vacancy_id TEXT, source TEXT, source_id TEXT, fetched_at TEXT, extra TEXT,
            description_html TEXT, description_text TEXT
        );
        INSERT INTO source_runs VALUES
            ('20261021T203222Z','reed','live','2026-10-21T20:32:22+00:00','2026-10-21T20:32:24+00:00',2,1,0,'ok','{}');
        INSERT INTO vacancies VALUES
            ('reed:1','reed','1','2026-10-21T20:32:22+00:00','{}',NULL,NULL),
            ('reed:2','reed','2','2026-10-21T20:32:22+00:00','{}',NULL,NULL),
            ('greenhouse:g1','greenhouse','g1','2026-10-21T20:32:22+00:00','{}',NULL,NULL),
            ('remote_ok:r1','remote_ok','r1','2026-10-21T20:32:22+00:00','{}',NULL,NULL);
        """
    )
    connection.commit()
    connection.close()
    _write_json(
        raw_dir / f"reed_{run_id}.json",
        [
            {"jobId": 1, "jobTitle": "Data Analyst", "jobDescription": "Python SQL"},
            {"jobId": 2, "jobTitle": "Data Analyst", "jobDescription": "SQL"},
        ],
    )
    _write_json(
        raw_dir / f"reed_details_{run_id}.json",
        [
            {
                "source": "reed",
                "source_id": "1",
                "source_tier": "A",
                "title": "Data Analyst",
                "url": "https://example.test/1",
                "description_html": "<p>Full</p>",
                "fetched_at": "2026-10-21T20:32:23+00:00",
            }
        ],
    )
    _write_json(
        raw_dir / f"ats_{run_id}.json",
        [
            {
                "source": "greenhouse",
                "source_id": "g1",
                "title": "Data Engineer",
                "description_html": "<p>Role</p>",
            }
        ],
    )
    _write_json(raw_dir / f"remote_ok_{run_id}.json", [])

    original_settings = {
        "run_id": run_id,
        "search_settings": {
            "centres": ["Birmingham", "Warwick"],
            "radius_miles": 15,
            "pages": 3,
            "birmingham_pages": 5,
            "request_cap": 1500,
            "terms": ["data analyst"],
        },
    }
    bundle = recovery.load_back_snapshot(backup, data_dir, original_settings)

    assert bundle["run_id"] == f"{run_id}_reprocessed"
    assert bundle["folder_name"] == "20261021_2033_reprocessed"
    assert len(bundle["records"]) == 4
    by_id = {row["source_id"]: row for row in bundle["records"]}
    assert by_id["1"]["description_coverage"] == "full"
    assert by_id["2"]["description_coverage"] == "search excerpt only"
    assert by_id["g1"]["description_coverage"] == "full"
    assert by_id["r1"]["description_coverage"] == "unavailable"
    assert all(row["fetched_at"] == "2026-10-21T20:32:22+00:00" for row in bundle["records"])
    assert bundle["metadata"]["collection_complete"] is False
    assert bundle["metadata"]["search_settings"] == original_settings["search_settings"]
    assert bundle["metadata"]["processed_classification_date"] == "2026-10-21"
    assert bundle["metadata"]["original_collection_finished_at"]
    # The database can still be reopened read-only after recovery.
    connection = sqlite3.connect(f"file:{backup}?mode=ro", uri=True)
    assert connection.execute("SELECT COUNT(*) FROM vacancies").fetchone()[0] == 4
    connection.close()
