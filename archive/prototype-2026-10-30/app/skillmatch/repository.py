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
from skillmatch.filters import NOT_A_DATA_ROLE, is_data_role
from skillmatch.taxonomy import get_taxonomy
from skillmatch.text import repair_mojibake


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
            if v.get("source") == "remote_ok":
                # Older live databases contain source strings misread as Latin-1.
                # Repair only in this in-memory snapshot; the SQLite file stays read-only.
                v = repair_mojibake(v)
            v["entry_signals"] = json.loads(v["entry_signals"] or "[]")
            v["title_boost"] = json.loads(v["title_boost"] or "[]")
            v["extra"] = json.loads(v["extra"]) if v["extra"] else {}
            if v.get("source") == "remote_ok":
                v["entry_signals"] = repair_mojibake(v["entry_signals"])
                v["title_boost"] = repair_mojibake(v["title_boost"])
                v["extra"] = repair_mojibake(v["extra"])
            # Recheck relevance in memory with the current title-only rule, so databases built
            # before it (including the Codespaces live-data release) stop showing non-data jobs.
            # The SQLite file stays unchanged.
            if not v["excluded_reason"] and not is_data_role(v["title"]):
                v["excluded_reason"] = NOT_A_DATA_ROLE
            vacancies[v["vacancy_id"]] = v
        tags: dict[str, list[tuple[str, str]]] = {}
        for req_id, tag_type, tag_id in conn.execute(
            "select req_id, tag_type, tag_id from requirement_tags"
        ):
            tags.setdefault(req_id, []).append((tag_type, tag_id))
        requirements: dict[str, list[dict]] = {}
        tax = get_taxonomy()
        for row in conn.execute("select * from requirements order by vacancy_id, n"):
            r = dict(row)
            if (
                r["vacancy_id"] in vacancies
                and vacancies[r["vacancy_id"]].get("source") == "remote_ok"
            ):
                r = repair_mojibake(r)
            # Reinterpret old technical tags in memory, including split or retired IDs.
            # Keep the immutable source DB unchanged and give every reader current skill IDs.
            sentence = r["evidence_sentence"]
            current = [
                (kind, ident)
                for kind, ident in tags.get(r["req_id"], [])
                if kind != "skill"
                or (
                    ident in tax.skills
                    and any(pattern.search(sentence) for pattern in tax.skills[ident].patterns)
                )
            ]
            for ident in ("databases", "data_modelling", "data_warehousing"):
                skill = tax.skills[ident]
                tag = ("skill", ident)
                if tag not in current and any(
                    pattern.search(sentence) for pattern in skill.patterns
                ):
                    current.append(tag)
            r["tags"] = current
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
