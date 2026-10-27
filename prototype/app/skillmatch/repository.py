"""Read-only access to the built SQLite database, cached in memory per database file version."""

from __future__ import annotations

import csv
import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path

from skillmatch import config
from skillmatch.etl.store import connect_readonly


@dataclass
class Snapshot:
    path: Path
    mtime: float
    meta: dict[str, str]
    vacancies: dict[str, dict]
    requirements: dict[str, list[dict]]
    sources: list[dict]
    source_runs: list[dict]
    duplicates: dict[str, list[dict]] = field(default_factory=dict)

    @property
    def mode(self) -> str:
        return self.meta.get("data_mode", "unknown")

    @property
    def shown(self) -> list[dict]:
        """Primary, non-excluded vacancies: what results show by default."""
        return [v for v in self.vacancies.values() if not v["excluded_reason"] and v["is_primary"]]

    def also_listed(self, vacancy: dict) -> list[dict]:
        group = vacancy.get("duplicate_group")
        if not group:
            return []
        return [
            self.vacancies[d["vacancy_id"]]
            for d in self.duplicates.get(group, [])
            if d["vacancy_id"] != vacancy["vacancy_id"] and d["vacancy_id"] in self.vacancies
        ]


_lock = threading.Lock()
_cache: dict[str, Snapshot] = {}


def load(path: Path | str | None = None) -> Snapshot | None:
    """The database as plain dictionaries. Reloaded only when the file changes."""
    if path is None:
        candidates = sorted(config.PROCESSED_DIR.glob("skillmatch_live_*.db"))
        path = candidates[-1] if candidates else config.DB_PATH
    path = Path(path)
    if not path.exists():
        return None
    mtime = os.path.getmtime(path)
    key = str(path)
    with _lock:
        snap = _cache.get(key)
        if snap and snap.mtime == mtime:
            return snap
        snap = _read(path, mtime)
        _cache[key] = snap
        return snap


def _read(path: Path, mtime: float) -> Snapshot:
    conn = connect_readonly(path)
    try:
        meta = dict(conn.execute("select key, value from meta").fetchall())
        vacancies = {}
        for row in conn.execute("select * from vacancies"):
            v = dict(row)
            v["entry_signals"] = json.loads(v["entry_signals"] or "[]")
            v["title_boost"] = json.loads(v["title_boost"] or "[]")
            v["extra"] = json.loads(v["extra"]) if v["extra"] else {}
            vacancies[v["vacancy_id"]] = v
        tags: dict[str, list[tuple[str, str]]] = {}
        for req_id, tag_type, tag_id in conn.execute(
            "select req_id, tag_type, tag_id from requirement_tags"
        ):
            tags.setdefault(req_id, []).append((tag_type, tag_id))
        requirements: dict[str, list[dict]] = {}
        for row in conn.execute("select * from requirements order by vacancy_id, n"):
            r = dict(row)
            r["tags"] = tags.get(r["req_id"], [])
            requirements.setdefault(r["vacancy_id"], []).append(r)
        sources = [dict(r) for r in conn.execute("select * from sources")]
        runs = [dict(r) for r in conn.execute("select * from source_runs")]
        dups: dict[str, list[dict]] = {}
        for row in conn.execute("select * from duplicates"):
            dups.setdefault(row["group_id"], []).append(dict(row))
    finally:
        conn.close()
    return Snapshot(path, mtime, meta, vacancies, requirements, sources, runs, dups)


def discovery_links() -> list[dict]:
    with (config.DATA_DIR / "discovery_links.csv").open() as f:
        return list(csv.DictReader(f))
