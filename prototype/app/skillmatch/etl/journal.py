"""Append-only, secret-minimising journal for live collection runs."""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_CHANNELS = {"reed", "feeds", "geo", "system"}
_EVENTS = {
    "run_started",
    "milestone",
    "run_failed",
    "request_attempt",
    "request_result",
    "cache_hit",
    "request_cap",
    "request_error",
}
_STRING_FIELDS = {
    "channel",
    "event",
    "outcome",
    "error_type",
    "milestone",
}
_INT_FIELDS = {"attempt", "status_code", "request_cap", "retry_after_seconds", "backoff_seconds"}
_ALLOWED_VALUES = {
    "channel": _CHANNELS,
    "event": _EVENTS,
    "outcome": {"success", "http_error", "network_error"},
    "error_type": {
        "ConnectionError",
        "HTTPError",
        "Timeout",
        "TooManyRedirects",
        "RequestException",
        "RuntimeError",
        "ValueError",
        "OSError",
        "unknown",
    },
    "milestone": {
        "collection_started",
        "collection_completed",
        "report_written",
        "processing_started",
        "database_written",
        "snapshot_written",
        "run_completed",
    },
}


def _validate_fields(event: str, channel: str, fields: dict[str, Any]) -> dict[str, Any]:
    if event not in _EVENTS:
        raise ValueError(f"unsupported journal event: {event!r}")
    if channel not in _CHANNELS:
        raise ValueError(f"unsupported journal channel: {channel!r}")
    record: dict[str, Any] = {"event": event, "channel": channel}
    for key, value in fields.items():
        if key not in _STRING_FIELDS | _INT_FIELDS or key in {"event", "channel"}:
            raise ValueError(f"unsupported journal field: {key!r}")
        if key in _STRING_FIELDS:
            if not isinstance(value, str) or value not in _ALLOWED_VALUES[key]:
                raise ValueError(f"unsupported value for journal field {key!r}")
        elif isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"journal field {key!r} must be a non-negative integer")
        record[key] = value
    return record


class RequestJournal:
    """Durably append sanitized events to one run-specific JSONL file.

    The file is created exclusively. Reusing a path therefore fails instead of
    truncating or mixing two collection runs.
    """

    def __init__(self, path: Path, run_id: str):
        self.path = Path(path)
        if not run_id or Path(run_id).name != run_id or run_id in {".", ".."}:
            raise ValueError("run_id must be a non-empty path component")
        self.run_id = run_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("x", encoding="utf-8")

    def record(self, event: str, channel: str = "system", **safe_fields: Any) -> None:
        """Append one allowlisted event and force it to stable storage."""
        safe = _validate_fields(event, channel, safe_fields)
        safe["at"] = datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        safe["run_id"] = self.run_id
        self._file.write(json.dumps(safe, ensure_ascii=False, separators=(",", ":")) + "\n")
        self._file.flush()
        os.fsync(self._file.fileno())

    def summary(self) -> dict[str, Any]:
        return summarize_journal(self.path)

    def close(self) -> None:
        if not self._file.closed:
            self._file.close()

    def __enter__(self) -> RequestJournal:
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def summarize_journal(path: Path) -> dict[str, Any]:
    """Rebuild aggregate request counts from a journal, including after restart."""
    attempts: Counter[str] = Counter()
    successes: Counter[str] = Counter()
    failed: Counter[str] = Counter()
    cache_hits: Counter[str] = Counter()
    request_caps: Counter[str] = Counter()
    errors: Counter[str] = Counter()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        item = json.loads(line)
        channel = item["channel"]
        if item["event"] == "request_attempt":
            attempts[channel] += 1
        elif item["event"] == "request_result":
            if item.get("outcome") == "success":
                successes[channel] += 1
            else:
                failed[channel] += 1
        elif item["event"] == "cache_hit":
            cache_hits[channel] += 1
        elif item["event"] == "request_cap":
            request_caps[channel] += 1
        elif item["event"] == "request_error":
            errors[channel] += 1
    channels = sorted(
        set(attempts)
        | set(successes)
        | set(failed)
        | set(cache_hits)
        | set(request_caps)
        | set(errors)
    )
    per_channel = defaultdict(dict)
    for channel in channels:
        per_channel[channel] = {
            "attempts": attempts[channel],
            "successes": successes[channel],
            "failed_attempts": failed[channel],
            "cache_hits": cache_hits[channel],
            "request_caps": request_caps[channel],
            "errors": errors[channel],
        }
    return {
        "total_attempts": sum(attempts.values()),
        "successes": sum(successes.values()),
        "failed_attempts": sum(failed.values()),
        "cache_hits": sum(cache_hits.values()),
        "request_caps": sum(request_caps.values()),
        "errors": sum(errors.values()),
        "per_channel": dict(per_channel),
    }
