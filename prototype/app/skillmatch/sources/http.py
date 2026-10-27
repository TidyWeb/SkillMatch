"""Polite HTTP client shared by every adapter.

- At most one request per `min_interval` seconds (default 1.0).
- Responses cached on disk keyed by URL (auth headers are never part of the key or the file).
- A hard cap on network requests per run.
- Exponential back-off on 429 and 5xx.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from contextlib import suppress
from pathlib import Path

import requests

from skillmatch import config
from skillmatch.etl.journal import RequestJournal

log = logging.getLogger(__name__)

USER_AGENT = "SkillMatch/0.1 (education project; West Midlands data-careers matcher)"


class RequestCapReached(RuntimeError):
    """Raised when a run would exceed its request budget."""


class PoliteClient:
    def __init__(
        self,
        cache_dir: Path | None = None,
        min_interval: float = 1.0,
        max_requests: int = 1500,
        max_retries: int = 4,
        cache_ttl_hours: float = 20.0,
        session: requests.Session | None = None,
        journal: RequestJournal | None = None,
        channel: str = "system",
    ):
        self.cache_dir = cache_dir or config.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_interval = min_interval
        self.max_requests = max_requests
        self.max_retries = max_retries
        self.cache_ttl = cache_ttl_hours * 3600
        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.journal = journal
        self.channel = channel
        self.requests_made = 0
        self.cache_hits = 0
        self._last = 0.0

    def _cache_path(self, url: str) -> Path:
        key = hashlib.sha256(url.encode()).hexdigest()[:32]
        candidates = list(self.cache_dir.glob(f"{key}*.json"))
        return (
            max(candidates, key=lambda p: p.stat().st_mtime)
            if candidates
            else self.cache_dir / (key + ".json")
        )

    def get(self, url: str, *, params: dict | None = None, auth=None, as_json: bool = True):
        full_url = requests.Request("GET", url, params=params).prepare().url
        path = self._cache_path(full_url)
        if path.exists() and time.time() - path.stat().st_mtime < self.cache_ttl:
            self.cache_hits += 1
            if self.journal is not None:
                self.journal.record("cache_hit", channel=self.channel)
            cached = json.loads(path.read_text())
            return cached["body"]

        for attempt in range(self.max_retries + 1):
            if self.requests_made >= self.max_requests:
                if self.journal is not None:
                    self.journal.record(
                        "request_cap", channel=self.channel, request_cap=self.max_requests
                    )
                raise RequestCapReached(f"request cap of {self.max_requests} reached")
            wait = self.min_interval - (time.monotonic() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.monotonic()
            self.requests_made += 1
            if self.journal is not None:
                self.journal.record("request_attempt", channel=self.channel, attempt=attempt + 1)
            try:
                resp = self.session.get(full_url, auth=auth, timeout=30)
            except requests.RequestException as exc:
                log.warning("network error on %s: %s", url, type(exc).__name__)
                if self.journal is not None:
                    self.journal.record(
                        "request_error",
                        channel=self.channel,
                        attempt=attempt + 1,
                        error_type="RequestException",
                    )
                resp = None
            status = resp.status_code if resp is not None else None
            outcome = (
                "network_error" if resp is None else ("success" if status < 400 else "http_error")
            )
            if self.journal is not None:
                result_fields = {"attempt": attempt + 1, "outcome": outcome}
                if status is not None:
                    result_fields["status_code"] = status
                self.journal.record("request_result", channel=self.channel, **result_fields)
            if resp is not None and resp.status_code < 400:
                body = resp.json() if as_json else resp.text
                # Expired responses are evidence of earlier collections; retain them.
                destination = path
                if destination.exists():
                    key = hashlib.sha256(full_url.encode()).hexdigest()[:32]
                    destination = self.cache_dir / f"{key}_{time.time_ns()}.json"
                with destination.open("x") as output:
                    json.dump({"url": full_url, "body": body}, output)
                return body
            if status is not None and status != 429 and status < 500:
                resp.raise_for_status()
            backoff = min(60, 2 ** (attempt + 1))
            if status == 429 and resp is not None:
                with suppress(TypeError, ValueError):
                    backoff = max(backoff, float(resp.headers.get("Retry-After", 0)))
            log.warning("status %s on %s; retrying in %ss", status, url, backoff)
            time.sleep(backoff)
        raise RuntimeError(f"gave up on {url} after {self.max_retries} retries")
