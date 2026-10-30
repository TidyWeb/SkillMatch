"""Rebuild append-only collection history from retained snapshot folders.

History CSVs are materialized views. Each rebuild first writes a retained generation, then
atomically refreshes the convenience copies at the history root. No prior generation is removed.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

ADVERT_COLUMNS = (
    "vacancy_id",
    "source",
    "source_id",
    "collected_at",
    "posted_date",
    "expiration_date",
    "outcome",
    "duplicate_of",
)
HISTORY_COLUMNS = (
    "vacancy_id",
    "first_seen",
    "last_seen",
    "times_seen",
    "latest_outcome",
    "sources_seen",
)
CHANGE_COLUMNS = (
    "run_id",
    "run_date",
    "source",
    "new",
    "gone",
    "still_live",
    "completeness",
    "comparable",
    "days_listed_gone_mean",
    "days_listed_gone",
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except (TypeError, ValueError):
        try:
            return datetime.combine(date.fromisoformat(str(value)[:10]), datetime.min.time(), UTC)
        except (TypeError, ValueError):
            return None


def _iso(value: datetime | None) -> str:
    return value.isoformat(timespec="seconds").replace("+00:00", "Z") if value else ""


def _run_time(meta: dict[str, Any], rows: list[dict[str, str]], folder: Path) -> datetime:
    for key in ("original_collection_at", "collection_at", "started_at", "start_time"):
        parsed = _parse_time(meta.get(key))
        if parsed:
            return parsed
    for row in rows:
        parsed = _parse_time(row.get("collected_at"))
        if parsed:
            return parsed
    for key in ("snapshot_date", "run_date"):
        parsed = _parse_time(meta.get(key))
        if parsed:
            return parsed
    # Snapshot folder names are commonly YYYYMMDD_HHMM, optionally with a suffix.
    stem = folder.name[:13]
    try:
        return datetime.strptime(stem, "%Y%m%d_%H%M").replace(tzinfo=UTC)
    except ValueError:
        return datetime.fromtimestamp(folder.stat().st_mtime, UTC)


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _load_runs(snapshots_dir: Path) -> list[dict[str, Any]]:
    candidates = []
    if not snapshots_dir.exists():
        return []
    for folder in sorted(p for p in snapshots_dir.iterdir() if p.is_dir()):
        meta = _read_json(folder / "run.json")
        rows = _read_csv(folder / "shown.csv") + _read_csv(folder / "dropped.csv")
        if not meta and not rows:
            continue
        when = _run_time(meta, rows, folder)
        run_id = str(meta.get("run_id") or meta.get("id") or folder.name)
        key = (run_id, when.isoformat())
        candidates.append(
            {
                "folder": folder,
                "meta": meta,
                "rows": rows,
                "when": when,
                "run_id": run_id,
                "dedupe_key": key,
            }
        )
    # Reprocessed/back snapshots sort by their original collection time. Exact duplicate
    # run IDs or collection timestamps count as one observation; path order breaks ties.
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    timestamps: set[str] = set()
    for run in sorted(candidates, key=lambda item: (item["when"], str(item["folder"]))):
        stamp = run["when"].isoformat()
        if run["dedupe_key"] in unique or stamp in timestamps:
            continue
        unique[run["dedupe_key"]] = run
        timestamps.add(stamp)
    return sorted(unique.values(), key=lambda item: (item["when"], item["run_id"]))


def _record_rows(run: dict[str, Any]) -> dict[str, dict[str, str]]:
    candidates: dict[str, list[tuple[tuple[bool, bool, bool], dict[str, str]]]] = {}
    for filename in ("shown.csv", "dropped.csv"):
        for row in _read_csv(run["folder"] / filename):
            vacancy_id = (row.get("vacancy_id") or "").strip()
            if not vacancy_id:
                continue
            normalized = {key: row.get(key, "") or "" for key in ADVERT_COLUMNS}
            normalized["source"] = normalized["source"] or normalized["source_id"]
            normalized["source_id"] = normalized["source_id"] or normalized["source"]
            normalized["collected_at"] = normalized["collected_at"] or _iso(run["when"])
            if filename == "shown.csv" and not normalized["outcome"]:
                normalized["outcome"] = "shown"
            outcome = normalized["outcome"].strip().lower()
            within_source_duplicate = "duplicate" in outcome and "same source" in outcome
            # A cross-source duplicate is a valid outcome for this advert and must not be
            # demoted. Prefer the substantive record when the same ID also appears as an
            # intra-source duplicate observation.
            rank = (
                not within_source_duplicate,
                bool(outcome),
                filename == "shown.csv" or outcome == "shown",
            )
            candidates.setdefault(vacancy_id, []).append((rank, normalized))
    records = {
        vacancy_id: max(rows, key=lambda pair: pair[0])[1]
        for vacancy_id, rows in candidates.items()
    }
    return records


def _source_statuses(run: dict[str, Any]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    severity = {
        "unknown": 0,
        "": 0,
        "ok": 1,
        "success": 1,
        "complete": 1,
        "completed": 1,
        "succeeded": 1,
        "disabled": 2,
        "partial": 3,
        "timeout": 4,
        "blocked": 4,
        "refused": 4,
        "error": 5,
        "failed": 5,
    }

    def record(source: str, status: str) -> None:
        status = status.strip().lower()
        old = statuses.get(source)
        if old is None or severity.get(status, 2) > severity.get(old, 2):
            statuses[source] = status or "unknown"

    rows = _read_csv(run["folder"] / "source_log.csv")
    for row in rows:
        source = (row.get("source_id") or row.get("source") or "").strip()
        if source:
            status = (row.get("status") or "").strip().lower()
            detail = " ".join(
                str(row.get(key) or "") for key in ("message", "error", "details")
            ).lower()
            if not status and any(
                term in detail for term in ("error", "failed", "timeout", "blocked", "refused")
            ):
                status = "partial"
            record(source, status or "unknown")

    metadata_status = run["meta"].get("source_status", {})
    if isinstance(metadata_status, dict):
        for source, value in metadata_status.items():
            if isinstance(value, dict):
                value = value.get("status", "unknown")
            record(str(source), str(value or "unknown"))
    sources = run["meta"].get("sources", [])
    if isinstance(sources, dict):
        sources = [
            dict(value, source_id=key)
            if isinstance(value, dict)
            else {"source_id": key, "status": value}
            for key, value in sources.items()
        ]
    if isinstance(sources, list):
        for item in sources:
            if isinstance(item, dict):
                source = str(
                    item.get("source_id") or item.get("source") or item.get("id") or ""
                ).strip()
                if source:
                    record(source, str(item.get("status") or "unknown"))
            elif item:
                record(str(item), "unknown")
    ats_status = statuses.get("ats")
    if ats_status:
        for source in ("greenhouse", "lever", "workable"):
            if source not in statuses or statuses[source] == "unknown":
                statuses[source] = ats_status
    for row in _record_rows(run).values():
        if row["source"]:
            statuses.setdefault(row["source"], "unknown")
    return statuses


def _is_complete(status: str) -> bool:
    return status in {"ok", "success", "complete", "completed", "succeeded"}


def _is_live(row: dict[str, str], when: datetime) -> bool:
    if row.get("outcome", "").strip().lower() == "expired":
        return False
    expiry = _parse_time(row.get("expiration_date"))
    return expiry is None or expiry.date() >= when.date()


def _source_from_id(value: str) -> str:
    value = (value or "").strip()
    return value.split(":", 1)[0] if ":" in value else value


def _build_history(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for run in runs:
        per_run = _record_rows(run)
        for vacancy_id, row in per_run.items():
            observed_at = _parse_time(row.get("collected_at")) or run["when"]
            item = by_id.setdefault(
                vacancy_id,
                {
                    "vacancy_id": vacancy_id,
                    "first": observed_at,
                    "last": observed_at,
                    "outcome": row.get("outcome", ""),
                    "runs": set(),
                    "sources": set(),
                },
            )
            if run["run_id"] in item["runs"]:
                continue
            item["runs"].add(run["run_id"])
            item["first"] = min(item["first"], observed_at)
            if observed_at >= item["last"]:
                item["last"] = observed_at
                item["outcome"] = row.get("outcome", "")
            if row.get("source"):
                item["sources"].add(row["source"])
            if row.get("duplicate_of"):
                linked = _source_from_id(row["duplicate_of"])
                if linked:
                    item["sources"].add(linked)
    result = []
    for item in by_id.values():
        result.append(
            {
                "vacancy_id": item["vacancy_id"],
                "first_seen": _iso(item["first"]),
                "last_seen": _iso(item["last"]),
                "times_seen": len(item["runs"]),
                "latest_outcome": item["outcome"],
                "sources_seen": ";".join(sorted(item["sources"])),
            }
        )
    return sorted(result, key=lambda row: row["vacancy_id"])


def _build_changes(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    previous_live: dict[str, set[str]] = {}
    previous_settings: str | None = None
    first_when: datetime | None = None
    first_records: dict[str, dict[str, str]] = {}
    first_sources: dict[str, str] = {}
    for run in runs:
        records = _record_rows(run)
        statuses = _source_statuses(run)
        settings_value = run["meta"].get("search_settings", run["meta"].get("settings", {}))
        settings = _canonical(settings_value)
        comparable = previous_settings is None or settings == previous_settings
        current_live: dict[str, set[str]] = {}
        for vacancy_id, row in records.items():
            source = row["source"]
            if source and _is_live(row, run["when"]):
                current_live.setdefault(source, set()).add(vacancy_id)
        source_names = sorted(set(statuses) | set(current_live) | set(previous_live))
        for source in source_names:
            status = statuses.get(source, "unknown")
            completeness = (
                "complete"
                if _is_complete(status)
                else (
                    "incomplete"
                    if status
                    in {"error", "partial", "disabled", "blocked", "refused", "timeout", "failed"}
                    else "unknown"
                )
            )
            current = current_live.get(source, set())
            previous = previous_live.get(source, set())
            if comparable:
                new_ids = current - previous
                still_ids = current & previous
                # A missing/failed/partial source cannot establish that old adverts vanished.
                gone_ids = (
                    previous - current
                    if _is_complete(status) and previous_settings is not None
                    else set()
                )
                gone_count: int | str = len(gone_ids) if completeness == "complete" else ""
                new_count: int | str = len(new_ids)
                still_count: int | str = len(still_ids)
                days = []
                for vacancy_id in sorted(gone_ids):
                    first_row = first_records.get(vacancy_id, {})
                    first_seen = (
                        _parse_time(first_row.get("collected_at")) or first_when or run["when"]
                    )
                    days.append(max(0, (run["when"].date() - first_seen.date()).days))
                mean_days: int | float | str = (
                    round(sum(days) / len(days), 2) if days else (0 if gone_count == 0 else "")
                )
                days_value = ";".join(str(value) for value in days)
            else:
                new_count = gone_count = still_count = mean_days = days_value = ""
            results.append(
                {
                    "run_id": run["run_id"],
                    "run_date": run["when"].date().isoformat(),
                    "source": source,
                    "new": new_count,
                    "gone": gone_count,
                    "still_live": still_count,
                    "completeness": completeness,
                    "comparable": str(comparable).lower(),
                    "days_listed_gone_mean": mean_days,
                    "days_listed_gone": days_value,
                }
            )
        if first_when is None:
            first_when = run["when"]
        for vacancy_id, row in records.items():
            first_records.setdefault(vacancy_id, row)
            if row["source"]:
                first_sources[vacancy_id] = row["source"]
        # A failed/partial/disabled source has no trustworthy current inventory. Keep its
        # last complete baseline so a later complete run can compare against it.
        retained_live = dict(current_live)
        for source, previous_ids in previous_live.items():
            if not _is_complete(statuses.get(source, "unknown")):
                retained_live[source] = previous_ids
        previous_live = retained_live
        previous_settings = settings
    return results


def _write_csv(path: Path, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def rebuild_history(snapshots_dir: Path, history_dir: Path) -> dict[str, Any]:
    """Rebuild history CSVs from all snapshots and return row counts and output paths."""
    snapshots_dir, history_dir = Path(snapshots_dir), Path(history_dir)
    runs = _load_runs(snapshots_dir)
    history_rows = _build_history(runs)
    change_rows = _build_changes(runs)

    versions = history_dir / "versions"
    versions.mkdir(parents=True, exist_ok=True)
    generation = versions / (
        datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:8]
    )
    generation.mkdir()
    version_history = generation / "adverts_history.csv"
    version_changes = generation / "daily_changes.csv"
    _write_csv(version_history, HISTORY_COLUMNS, history_rows)
    _write_csv(version_changes, CHANGE_COLUMNS, change_rows)

    # Preserve any previous current pair in a retained version before replacing either file.
    existing = [
        name
        for name in ("adverts_history.csv", "daily_changes.csv")
        if (history_dir / name).exists()
    ]
    if existing:
        prior = versions / (
            "previous-current-"
            + datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
            + "-"
            + uuid.uuid4().hex[:8]
        )
        prior.mkdir()
        for name in existing:
            shutil.copy2(history_dir / name, prior / name)

    # Atomic per-file refresh from the already retained generation.
    for name in ("adverts_history.csv", "daily_changes.csv"):
        target = history_dir / name
        temporary = history_dir / (name + ".tmp-" + uuid.uuid4().hex)
        shutil.copy2(generation / name, temporary)
        os.replace(temporary, target)

    return {
        "runs": len(runs),
        "adverts_history_rows": len(history_rows),
        "daily_changes_rows": len(change_rows),
        "generation_dir": str(generation),
        "adverts_history_path": str(history_dir / "adverts_history.csv"),
        "daily_changes_path": str(history_dir / "daily_changes.csv"),
    }
