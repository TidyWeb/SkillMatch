import csv
import json
from pathlib import Path

from skillmatch.etl.history import rebuild_history


def _snapshot(
    root: Path,
    name: str,
    *,
    run_id: str,
    when: str,
    records: list[dict],
    status="ok",
    settings=None,
):
    folder = root / name
    folder.mkdir(parents=True)
    (folder / "run.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "started_at": when,
                "finished_at": when,
                "search_settings": settings or {"terms": ["data analyst"]},
                "sources": [{"source_id": "reed", "status": status}],
            }
        )
    )
    (folder / "source_log.csv").write_text(f"source_id,status\nreed,{status}\n")
    for filename in ("shown.csv", "dropped.csv"):
        rows = records if filename == "shown.csv" else []
        fields = [
            "vacancy_id",
            "source",
            "source_id",
            "collected_at",
            "posted_date",
            "expiration_date",
            "is_remote",
            "outcome",
            "duplicate_of",
        ]
        with (folder / filename).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    return folder


def _read(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _row(vacancy_id, when, outcome="shown"):
    return {
        "vacancy_id": vacancy_id,
        "source": "reed",
        "source_id": "reed",
        "collected_at": when,
        "posted_date": "2026-09-30",
        "expiration_date": "",
        "is_remote": "false",
        "outcome": outcome,
        "duplicate_of": "",
    }


def test_history_uses_distinct_runs_and_reports_first_last_new_gone(tmp_path):
    snapshots, history = tmp_path / "snapshots", tmp_path / "history"
    snapshots.mkdir()
    t1, t2 = "2026-10-01T10:00:00Z", "2026-10-02T10:00:00Z"
    _snapshot(
        snapshots,
        "20261001_1000",
        run_id="one",
        when=t1,
        records=[_row("reed:old", t1), _row("reed:old", t1)],
    )
    _snapshot(snapshots, "20261002_1000", run_id="two", when=t2, records=[_row("reed:new", t2)])

    result = rebuild_history(snapshots, history)
    rows = {row["vacancy_id"]: row for row in _read(history / "adverts_history.csv")}
    assert result["runs"] == 2
    assert rows["reed:old"]["first_seen"] == t1
    assert rows["reed:old"]["last_seen"] == t1
    assert rows["reed:old"]["times_seen"] == "1"
    changes = _read(history / "daily_changes.csv")
    assert [(row["new"], row["gone"], row["still_live"]) for row in changes] == [
        ("1", "0", "0"),
        ("1", "1", "0"),
    ]
    assert changes[1]["days_listed_gone"] == "1"


def test_incomplete_source_does_not_claim_gone_and_versions_are_retained(tmp_path):
    snapshots, history = tmp_path / "snapshots", tmp_path / "history"
    snapshots.mkdir()
    t1, t2 = "2026-10-01T10:00:00Z", "2026-10-02T10:00:00Z"
    _snapshot(snapshots, "20261001_1000", run_id="one", when=t1, records=[_row("reed:old", t1)])
    _snapshot(snapshots, "20261002_1000", run_id="two", when=t2, records=[], status="error")

    first = rebuild_history(snapshots, history)
    second = rebuild_history(snapshots, history)
    rows = _read(history / "daily_changes.csv")
    assert rows[1]["completeness"] == "incomplete"
    assert rows[1]["gone"] == ""
    assert rows[1]["comparable"] == "true"
    generations = list((history / "versions").iterdir())
    assert len(generations) == 3  # two generated versions and one retained prior-current pair
    assert Path(first["generation_dir"]).exists()
    assert Path(second["generation_dir"]).exists()


def test_settings_change_marks_run_not_comparable_and_duplicate_timestamp_is_ignored(tmp_path):
    snapshots, history = tmp_path / "snapshots", tmp_path / "history"
    snapshots.mkdir()
    when = "2026-10-01T10:00:00Z"
    _snapshot(snapshots, "20261001_1000", run_id="one", when=when, records=[_row("reed:old", when)])
    _snapshot(
        snapshots, "20261001_1000_copy", run_id="copy", when=when, records=[_row("reed:old", when)]
    )
    later = "2026-10-02T10:00:00Z"
    _snapshot(
        snapshots,
        "20261002_1000",
        run_id="two",
        when=later,
        records=[_row("reed:old", later)],
        settings={"terms": ["new terms"]},
    )

    result = rebuild_history(snapshots, history)
    assert result["runs"] == 2
    changes = _read(history / "daily_changes.csv")
    assert changes[1]["comparable"] == "false"
    assert changes[1]["new"] == changes[1]["gone"] == changes[1]["still_live"] == ""


def test_real_shown_record_wins_over_repeated_intra_source_duplicate_observation(tmp_path):
    snapshots, history = tmp_path / "snapshots", tmp_path / "history"
    snapshots.mkdir()
    when = "2026-10-01T10:00:00Z"
    folder = _snapshot(
        snapshots, "20261001_1000", run_id="one", when=when, records=[_row("reed:1", when, "shown")]
    )
    fields = [
        "vacancy_id",
        "source",
        "source_id",
        "collected_at",
        "posted_date",
        "expiration_date",
        "is_remote",
        "outcome",
        "duplicate_of",
    ]
    with (folder / "dropped.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerow(_row("reed:1", when, "duplicate within same source"))

    rebuild_history(snapshots, history)
    item = _read(history / "adverts_history.csv")[0]
    assert item["latest_outcome"] == "shown"
    assert item["times_seen"] == "1"


def test_source_status_uses_metadata_ats_fallback_and_worst_event(tmp_path):
    snapshots, history = tmp_path / "snapshots", tmp_path / "history"
    snapshots.mkdir()
    when = "2026-10-01T10:00:00Z"
    folder = _snapshot(snapshots, "20261001_1000", run_id="one", when=when, records=[])
    meta_path = folder / "run.json"
    meta = json.loads(meta_path.read_text())
    meta["sources"] = ["greenhouse", "lever", "ats"]
    meta["source_status"] = {"ats": "error", "greenhouse": "ok"}
    meta_path.write_text(json.dumps(meta))
    (folder / "source_log.csv").write_text(
        "source_id,status,message\nreed,,request error\nreed,ok,completed\n"
    )

    rebuild_history(snapshots, history)
    statuses = {row["source"]: row["completeness"] for row in _read(history / "daily_changes.csv")}
    assert statuses["reed"] == "incomplete"
    assert statuses["greenhouse"] == "complete"
    assert statuses["lever"] == "incomplete"
