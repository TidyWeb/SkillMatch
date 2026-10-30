import csv
import json

from skillmatch.etl.snapshots import write_snapshot


def _inputs():
    observations = [
        {
            "observation_id": "o1",
            "vacancy_id": "reed:1",
            "source": "reed",
            "source_id": "1",
            "title": "Data Analyst",
            "url": "https://example.test/1",
            "posted_date": "2026-01-01",
            "fetched_at": "2026-10-27T10:00:00Z",
            "description_coverage": "search excerpt only",
            "outcome": "shown",
            "search_term": "data analyst",
            "description_html": "must not export",
            "extra": {"secret": "must not export"},
        },
        {
            "observation_id": "o2",
            "vacancy_id": "reed:1",
            "source": "reed",
            "source_id": "1",
            "title": "Data Analyst",
            "url": "https://example.test/1",
            "posted_date": "2026-01-01",
            "fetched_at": "2026-10-27T10:00:00Z",
            "description_coverage": "full",
            "outcome": "duplicate within the same source",
            "duplicate_of": "reed:1",
            "search_term": "reporting analyst",
        },
        {
            "observation_id": "o3",
            "vacancy_id": "ats:2",
            "source": "greenhouse",
            "source_id": "2",
            "title": "Sales Lead",
            "outcome": "not a data role",
            "search_term": "data analyst",
        },
    ]
    requirements = [
        {
            "req_id": "reed:1#1",
            "vacancy_id": "reed:1",
            "strength": "essential",
            "confidence": "high",
        },
        {
            "req_id": "reed:1#2",
            "vacancy_id": "reed:1",
            "strength": "desirable",
            "confidence": "medium",
        },
    ]
    tags = [
        {"req_id": "reed:1#1", "tag_type": "skill", "tag_id": "sql"},
        {"req_id": "reed:1#2", "tag_type": "skill", "tag_id": "sql"},
        {"req_id": "reed:1#2", "tag_type": "competency", "tag_id": "attention"},
    ]
    funnel = [
        {
            "run_id": "old",
            "source": "reed",
            "collected": 2,
            "shown": 1,
            "duplicate within the same source": 1,
        },
        {"run_id": "old", "source": "ALL", "collected": 3, "shown": 1},
    ]
    source_log = [
        {
            "source": "reed",
            "source_id": "22",
            "status": "partial",
            "error_type": "Timeout",
            "requests": 6,
        }
    ]
    metadata = {
        "started_at": "2026-10-27T10:00:00Z",
        "sources": ["reed"],
        "search_settings": {"pages": 3, "terms": ["data analyst", "zero yield"]},
        "api_key": "never-write-me",
        "source_status": {"reed": "ok"},
        "requests_made": 12,
        "reed_requests": 10,
        "data_mode": "reprocessed",
        "working_code_fingerprint": "abc123",
        "code_has_uncommitted_changes": True,
        "original_collection_at": "2026-10-21T20:33:00Z",
        "reprocessed_from": "21 Oct database",
        "history_limitations": "Older posting weeks undercount",
        "collection_complete": False,
        "agency_coverage": "Recomputed per run",
    }
    return observations, requirements, tags, funnel, source_log, metadata


def test_snapshot_has_required_schema_counts_skills_and_iso_week(tmp_path):
    inputs = _inputs()
    out = write_snapshot(
        data_dir=tmp_path,
        run_id="r1",
        observations=inputs[0],
        requirements=inputs[1],
        tags=inputs[2],
        funnel=inputs[3],
        source_log=inputs[4],
        metadata=inputs[5],
        folder_name="run",
    )
    with (out / "shown.csv").open() as f:
        shown = list(csv.DictReader(f))
    with (out / "dropped.csv").open() as f:
        dropped = list(csv.DictReader(f))
    assert len(shown) == 1 and len(dropped) == 2
    assert shown[0]["posted_week"] == "2026-W01"
    assert shown[0]["collected_at"] == "2026-10-27T10:00:00Z"
    assert shown[0]["link"] == "https://example.test/1"
    assert "description_html" not in shown[0] and "extra" not in shown[0]
    with (out / "skills.csv").open() as f:
        skills = list(csv.DictReader(f))
    assert skills == [
        {
            "run_id": "r1",
            "vacancy_id": "reed:1",
            "skill": "sql",
            "strength": "essential",
            "confidence": "high",
            "description_coverage": "full",
        }
    ]
    with (out / "funnel.csv").open() as f:
        funnel = list(csv.DictReader(f))
    assert len(funnel) == 1 and funnel[0]["source"] == "reed"
    assert funnel[0]["run_id"] == "r1" and funnel[0]["collected"] == "2"
    with (out / "source_log.csv").open() as f:
        source_events = list(csv.DictReader(f))
    assert source_events[0]["source_id"] == "22"
    run_data = json.loads((out / "run.json").read_text())
    assert run_data["run_id"] == "r1" and "api_key" not in run_data
    assert run_data["requests_made"] == 12 and run_data["data_mode"] == "reprocessed"
    assert run_data["working_code_fingerprint"] == "abc123"
    readme = (out / "README.md").read_text()
    assert readme.startswith("# Collection: 21 October 2026")
    assert "Adverts collected: 2" in readme
    assert "Adverts kept (in `shown.csv`): 1" in readme
    assert "Sources: Greenhouse and Reed" in readme
    assert "Older posting weeks undercount" not in readme
    assert '"observations":' not in readme
    assert "## The numbers" in readme and "## Notes on this run" in readme


def test_snapshot_name_collision_adds_suffix_without_overwrite(tmp_path):
    args = _inputs()
    first = write_snapshot(
        data_dir=tmp_path,
        run_id="r1",
        observations=args[0],
        requirements=args[1],
        tags=args[2],
        funnel=args[3],
        source_log=args[4],
        metadata=args[5],
        folder_name="same",
    )
    marker = first / "run.json"
    original = marker.read_text()
    second = write_snapshot(
        data_dir=tmp_path,
        run_id="r2",
        observations=[],
        requirements=[],
        tags=[],
        funnel=[],
        source_log=[],
        metadata={},
        folder_name="same",
    )
    assert first.name == "same" and second.name == "same_2"
    assert marker.read_text() == original


def test_search_term_yield_attributes_first_occurrence_only(tmp_path):
    args = _inputs()
    out = write_snapshot(
        data_dir=tmp_path,
        run_id="r",
        observations=args[0],
        requirements=[],
        tags=[],
        funnel=[],
        source_log=[],
        metadata=args[5],
        folder_name="yield",
    )
    with (out / "search_terms_yield.csv").open() as f:
        rows = {r["search_term"]: r for r in csv.DictReader(f)}
    assert rows["data analyst"]["collected_observations"] == "2"
    assert rows["data analyst"]["first_attributed_new"] == "2"
    assert rows["data analyst"]["matched_distinct"] == "2"
    assert rows["data analyst"]["shown_across_match"] == "1"
    assert rows["reporting analyst"]["first_attributed_new"] == "0"
    assert rows["reporting analyst"]["shown_across_match"] == "1"
    assert rows["zero yield"]["collected_observations"] == "0"
    assert rows["zero yield"]["matched_distinct"] == "0"


def test_skill_confidence_comes_from_strongest_strength_statement(tmp_path):
    observations, _, _, _, _, _ = _inputs()
    out = write_snapshot(
        data_dir=tmp_path,
        run_id="r",
        observations=observations,
        requirements=[
            {"req_id": "a", "vacancy_id": "reed:1", "strength": "essential", "confidence": "low"},
            {"req_id": "b", "vacancy_id": "reed:1", "strength": "desirable", "confidence": "high"},
        ],
        tags=[
            {"req_id": "a", "tag_type": "skill", "tag_id": "sql"},
            {"req_id": "b", "tag_type": "skill", "tag_id": "sql"},
        ],
        funnel=[],
        source_log=[],
        metadata={},
        folder_name="confidence",
    )
    with (out / "skills.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["strength"] == "essential"
    assert rows[0]["confidence"] == "low"


def test_shown_match_yield_maps_reed_duplicates_to_one_canonical_vacancy(tmp_path):
    observations = [
        {
            "observation_id": "o1",
            "vacancy_id": "reed:1",
            "source": "reed",
            "outcome": "duplicate of an advert from another source",
            "duplicate_of": "greenhouse:9",
            "search_term": "data analyst",
        },
        {
            "observation_id": "o2",
            "vacancy_id": "reed:2",
            "source": "reed",
            "outcome": "duplicate of an advert from another source",
            "duplicate_of": "greenhouse:9",
            "search_term": "data analyst",
        },
        {
            "observation_id": "o3",
            "vacancy_id": "greenhouse:9",
            "source": "greenhouse",
            "outcome": "shown",
        },
    ]
    out = write_snapshot(
        data_dir=tmp_path,
        run_id="r",
        observations=observations,
        requirements=[],
        tags=[],
        funnel=[],
        source_log=[],
        metadata={},
        folder_name="canonical-match",
    )
    with (out / "search_terms_yield.csv").open() as f:
        row = next(csv.DictReader(f))
    assert row["matched_distinct"] == "2"
    assert row["shown_across_match"] == "1"


def test_repeated_same_id_self_duplicate_does_not_hide_cross_source_primary(tmp_path):
    observations = [
        {
            "observation_id": "o1",
            "vacancy_id": "reed:1",
            "source": "reed",
            "outcome": "duplicate of an advert from another source",
            "duplicate_of": "greenhouse:9",
            "search_term": "data analyst",
        },
        {
            "observation_id": "o2",
            "vacancy_id": "reed:1",
            "source": "reed",
            "outcome": "duplicate within the same source",
            "duplicate_of": "reed:1",
            "search_term": "data analyst",
        },
        {
            "observation_id": "o3",
            "vacancy_id": "greenhouse:9",
            "source": "greenhouse",
            "outcome": "shown",
        },
    ]
    out = write_snapshot(
        data_dir=tmp_path,
        run_id="r",
        observations=observations,
        requirements=[],
        tags=[],
        funnel=[],
        source_log=[],
        metadata={},
        folder_name="repeated-self-edge",
    )
    with (out / "search_terms_yield.csv").open() as f:
        row = next(csv.DictReader(f))
    assert row["collected_observations"] == "2"
    assert row["matched_distinct"] == "1"
    assert row["shown_across_match"] == "1"
