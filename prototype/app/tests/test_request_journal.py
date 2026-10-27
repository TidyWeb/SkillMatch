import json

import pytest
import requests

from skillmatch.etl.journal import RequestJournal, summarize_journal
from skillmatch.sources.http import PoliteClient, RequestCapReached


class Response:
    def __init__(self, status_code, body=None, headers=None):
        self.status_code = status_code
        self._body = body
        self.headers = headers or {}
        self.text = str(body)

    def json(self):
        return self._body

    def raise_for_status(self):
        raise requests.HTTPError(f"status {self.status_code}")


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.headers = {}
        self.calls = 0

    def get(self, *_args, **_kwargs):
        self.calls += 1
        result = next(self.responses)
        if isinstance(result, BaseException):
            raise result
        return result


def test_attempt_is_durable_before_session_call_even_if_process_stops(tmp_path):
    journal_path = tmp_path / "run.jsonl"
    session = Session([KeyboardInterrupt()])
    journal = RequestJournal(journal_path, "run-1")
    client = PoliteClient(
        cache_dir=tmp_path / "cache",
        min_interval=0,
        session=session,
        journal=journal,
        channel="reed",
    )

    with pytest.raises(KeyboardInterrupt):
        client.get("https://example.test/jobs?api_key=secret", auth=("user", "password"))

    persisted = [json.loads(line) for line in journal_path.read_text().splitlines()]
    assert [item["event"] for item in persisted] == ["request_attempt"]
    assert persisted[0]["at"].endswith("Z")
    assert summarize_journal(journal_path)["total_attempts"] == 1
    assert "secret" not in journal_path.read_text()
    assert "password" not in journal_path.read_text()


def test_retries_record_each_attempt_and_success(tmp_path, monkeypatch):
    monkeypatch.setattr("skillmatch.sources.http.time.sleep", lambda _seconds: None)
    journal_path = tmp_path / "run.jsonl"
    journal = RequestJournal(journal_path, "run-2")
    session = Session([Response(503), Response(200, {"ok": True})])
    client = PoliteClient(
        cache_dir=tmp_path / "cache",
        min_interval=0,
        max_retries=1,
        session=session,
        journal=journal,
        channel="feeds",
    )

    assert client.get("https://example.test/feed?token=private") == {"ok": True}
    assert session.calls == 2
    summary = summarize_journal(journal_path)
    assert summary["total_attempts"] == 2
    assert summary["successes"] == 1
    assert summary["failed_attempts"] == 1
    assert summary["per_channel"]["feeds"]["attempts"] == 2
    contents = journal_path.read_text()
    assert "private" not in contents and "example.test" not in contents


def test_cache_hit_is_journaled_without_network_request(tmp_path):
    journal_path = tmp_path / "run.jsonl"
    cache = tmp_path / "cache"
    cache.mkdir()
    journal = RequestJournal(journal_path, "run-3")
    session = Session([])
    client = PoliteClient(
        cache_dir=cache,
        min_interval=0,
        session=session,
        journal=journal,
        channel="geo",
    )
    url = "https://example.test/lookup?key=classified"
    path = client._cache_path(url)
    path.write_text(json.dumps({"url": url, "body": {"place": "Birmingham"}}))

    assert client.get(url) == {"place": "Birmingham"}
    assert session.calls == 0
    summary = summarize_journal(journal_path)
    assert summary["total_attempts"] == 0
    assert summary["cache_hits"] == 1
    assert "classified" not in journal_path.read_text()


def test_request_cap_is_a_separate_event(tmp_path):
    journal_path = tmp_path / "run.jsonl"
    journal = RequestJournal(journal_path, "run-4")
    client = PoliteClient(
        cache_dir=tmp_path / "cache",
        max_requests=0,
        session=Session([]),
        journal=journal,
        channel="reed",
    )

    with pytest.raises(RequestCapReached):
        client.get("https://example.test/jobs")

    summary = summarize_journal(journal_path)
    assert summary["total_attempts"] == 0
    assert summary["request_caps"] == 1


def test_journal_never_truncates_existing_file_and_rejects_unlisted_fields(tmp_path):
    path = tmp_path / "run.jsonl"
    journal = RequestJournal(path, "run-5")
    journal.close()
    original = path.read_bytes()

    with pytest.raises(FileExistsError):
        RequestJournal(path, "run-5")
    with path.open("a", encoding="utf-8") as output:
        output.write(" ")
    assert path.read_bytes().startswith(original)

    journal = RequestJournal(tmp_path / "another.jsonl", "run-6")
    with pytest.raises(ValueError):
        journal.record("request_result", channel="reed", url="https://secret.test/?token=x")
    journal.close()


def test_milestones_include_pipeline_commit_points_and_timestamp_is_internal(tmp_path):
    path = tmp_path / "run.jsonl"
    journal = RequestJournal(path, "run-7")
    journal.record("milestone", milestone="database_written")
    journal.record("milestone", milestone="snapshot_written")
    journal.record("milestone", milestone="run_completed")
    with pytest.raises(ValueError):
        journal.record("run_failed", at="2030-01-01T00:00:00Z")
    journal.close()

    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert [record["milestone"] for record in records] == [
        "database_written",
        "snapshot_written",
        "run_completed",
    ]
    assert all(record["at"].endswith("Z") for record in records)
