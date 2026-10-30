import json

import pytest

from skillmatch.etl import pipeline
from skillmatch.etl.journal import summarize_journal


def test_processing_crash_keeps_request_count_and_failure_event(monkeypatch, tmp_path):
    def fail_after_request(mode, **kwargs):
        journal = kwargs["_journal"]
        journal.record("request_attempt", channel="reed", attempt=1)
        journal.record(
            "request_result", channel="reed", attempt=1, outcome="success", status_code=200
        )
        journal.record("milestone", milestone="processing_started")
        raise AttributeError("simulated processing failure")

    monkeypatch.setattr(pipeline, "_run", fail_after_request)
    with pytest.raises(AttributeError):
        pipeline.run("live", db_path=tmp_path / "unused.db")
    journal_path = next((tmp_path / "run_logs").glob("*.jsonl"))
    assert summarize_journal(journal_path)["total_attempts"] == 1
    events = [json.loads(line) for line in journal_path.read_text().splitlines()]
    assert events[-1]["event"] == "run_failed"
    assert all(event["at"].endswith("Z") for event in events)
