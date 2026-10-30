"""Rebuild collection bundles from local cache and saved run data.

Recovery is deliberately read-only: it never creates a client or calls an adapter's
``fetch`` method. The returned bundle can be handed to the normal ETL pipeline.
"""

from __future__ import annotations

import csv
import html
import json
import sqlite3
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from skillmatch import config
from skillmatch.sources.reed import ReedAdapter

_RECOVERY_RUN_ID = "20261027T124644998193Z"
_BACK_RUN_ID = "20261021T203222Z"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _run_time(run_id: str) -> datetime:
    return datetime.strptime(run_id, "%Y%m%dT%H%M%S%fZ").replace(tzinfo=UTC)


def _source_run(
    run_id: str,
    source_id: str,
    started_at: str,
    fetched: int,
    kept: int,
    requests: int,
    status: str,
    message: str = "",
) -> dict:
    return {
        "run_id": run_id,
        "source_id": source_id,
        "mode": "live",
        "started_at": started_at,
        "finished_at": started_at,
        "fetched": fetched,
        "kept": kept,
        "requests": requests,
        "status": status,
        "message": message,
    }


def _cache_entries(cache_dir: Path, start: float, end: float) -> list[tuple[Path, dict]]:
    entries = []
    if not cache_dir.is_dir():
        return entries
    for path in cache_dir.glob("*.json"):
        try:
            if not start <= path.stat().st_mtime <= end:
                continue
            item = _json(path)
            if isinstance(item, dict) and isinstance(item.get("url"), str):
                entries.append((path, item))
        except (OSError, ValueError, TypeError):
            continue
    return entries


def _terms(data_dir: Path) -> list[str]:
    with (data_dir / "search_terms.csv").open(encoding="utf-8", newline="") as stream:
        return [row["term"] for row in csv.DictReader(stream)]


def _query_key(url: str) -> tuple[str, str, str, str] | None:
    parsed = urlparse(url)
    if not parsed.path.endswith("/api/1.0/search"):
        return None
    values = parse_qs(parsed.query)
    try:
        return (
            values["locationName"][0],
            values["keywords"][0],
            values["distanceFromLocation"][0],
            values["resultsToSkip"][0],
        )
    except (KeyError, IndexError):
        return None


def _replay_searches(
    cache_entries: list[tuple[Path, dict]], data_dir: Path
) -> tuple[list[dict], dict[int, dict], int, int, int, list[dict]]:
    """Return ordered (query, row) observations and the best row per Reed ID."""
    wanted: dict[tuple[str, str, str, str], tuple[str, int]] = {}
    for town in config.REED_GRID:
        pages = (
            config.REED_BIRMINGHAM_PAGES
            if town.strip().casefold() == "birmingham"
            else config.REED_PAGES
        )
        for term in _terms(data_dir):
            for page in range(pages):
                wanted[(town, term, str(config.REED_DISTANCE_MILES), str(page * 100))] = (
                    town,
                    page + 1,
                )

    cached: dict[tuple[str, str, str, str], tuple[float, dict]] = {}
    for path, item in cache_entries:
        key = _query_key(item["url"])
        if key not in wanted:
            continue
        # Discard cached responses made with a different page size or malformed body.
        parsed = parse_qs(urlparse(item["url"]).query)
        if parsed.get("resultsToTake") != ["100"]:
            continue
        body = item.get("body")
        if not isinstance(body, dict) or not isinstance(body.get("results"), list):
            continue
        mtime = path.stat().st_mtime
        if key not in cached or mtime > cached[key][0]:
            cached[key] = (mtime, body)

    observations: list[dict] = []
    unique: dict[int, dict] = {}
    needed_queries = recovered_queries = missing_needed_pages = 0
    truncated_searches = []
    stop_all_queries = False
    for town in config.REED_GRID:
        pages = (
            config.REED_BIRMINGHAM_PAGES
            if town.strip().casefold() == "birmingham"
            else config.REED_PAGES
        )
        for term in _terms(data_dir):
            for page in range(pages):
                key = (town, term, str(config.REED_DISTANCE_MILES), str(page * 100))
                needed_queries += 1
                saved = cached.get(key)
                if saved is None:
                    missing_needed_pages += 1
                    stop_all_queries = True
                    break
                recovered_queries += 1
                mtime, body = saved
                results = body["results"]
                for row in results:
                    if not isinstance(row, dict) or "jobId" not in row:
                        continue
                    job_id = int(row["jobId"])
                    unique.setdefault(job_id, row)
                    observations.append(
                        {
                            "job_id": job_id,
                            "row": row,
                            "search_term": term,
                            "search_location": town,
                            "search_page": page + 1,
                            "cache_mtime": mtime,
                        }
                    )
                if len(results) < 100:
                    break
                if page == pages - 1:
                    truncated_searches.append(
                        {"location": town, "term": term, "page": page + 1, "result_count": 100}
                    )
            if stop_all_queries:
                break
        if stop_all_queries:
            break
    return (
        observations,
        unique,
        needed_queries,
        recovered_queries,
        missing_needed_pages,
        truncated_searches,
    )


def _search_survivors(rows: dict[int, dict], collection_date: str) -> set[str]:
    """Reapply Reed's pre-detail filters to unique search rows for the completeness guard."""
    from skillmatch.etl.pipeline import OUT_OF_REGION, assess, remote_status
    from skillmatch.geo import Geocoder, postcode_outside_region

    geocoder = Geocoder(offline=True)
    survivors = set()
    for job_id, row in rows.items():
        record = ReedAdapter.from_search_row(row).to_dict()
        expires = record.get("expiration_date")
        if expires and expires < collection_date:
            continue
        place = geocoder.locate_job(record.get("location_text"), record.get("postcode"))
        reason, _, _ = assess(
            record.get("title") or "",
            html.unescape(row.get("jobDescription") or ""),
            place,
            remote_status(record, "unknown"),
            None,
        )
        if reason is None and place is None and postcode_outside_region(record.get("postcode")):
            reason = OUT_OF_REGION
        if reason is None:
            survivors.add(str(job_id))
    return survivors


def _description_present(record: dict) -> bool:
    return bool(
        (record.get("description_html") or "").strip()
        or (record.get("description_text") or "").strip()
    )


def _original_search_settings(settings: dict) -> dict:
    supplied = settings.get("search_settings") or settings
    aliases = {
        "centres": ("centres", "reed_grid", "towns"),
        "radius_miles": ("radius_miles", "distance_miles"),
        "pages": ("pages", "pages_per_search"),
        "birmingham_pages": ("birmingham_pages",),
        "request_cap": ("request_cap", "max_requests"),
        "terms": ("terms", "search_terms"),
    }
    result = {}
    for output_key, candidates in aliases.items():
        for key in candidates:
            if key in supplied:
                result[output_key] = supplied[key]
                break
    return result


def _cache_request_counts(entries: list[tuple[Path, dict]]) -> Counter:
    """Count successful cached responses by endpoint family (retry attempts unavailable)."""
    counts: Counter = Counter()
    for _, item in entries:
        parsed = urlparse(item["url"])
        host, path = parsed.netloc.casefold(), parsed.path.casefold()
        if "reed.co.uk" in host:
            counts["reed"] += 1
        elif "weworkremotely.com" in host:
            counts["we_work_remotely"] += 1
        elif "remoteok.com" in host:
            counts["remote_ok"] += 1
        elif any(domain in host for domain in ("greenhouse.io", "lever.co", "workable.com")):
            counts["ats"] += 1
        elif path in ("/", "") and host:
            counts["feeds"] += 1
    return counts


def load_recovery(run_id: str, data_dir: Path = config.DATA_DIR) -> dict:
    """Build a replay bundle for the interrupted 27 October live collection.

    Only the named run is supported because its raw capture and cache window are the
    evidence used to reconstruct query observations. All reads stay under ``data_dir``.
    """
    if run_id != _RECOVERY_RUN_ID:
        raise ValueError(f"no local recovery evidence is configured for {run_id}")
    data_dir = Path(data_dir)
    raw_dir = data_dir / "raw"
    raw_path = raw_dir / f"reed_{run_id}.json"
    details_path = raw_dir / f"reed_details_{run_id}.json"
    raw_rows = _json(raw_path)
    details = _json(details_path)
    started_dt = _run_time(run_id)
    started_at = started_dt.isoformat(timespec="microseconds")
    end = raw_path.stat().st_mtime
    cache_entries = _cache_entries(data_dir / "cache", started_dt.timestamp(), end)
    (
        occurrences,
        cache_unique,
        needed_queries,
        recovered_queries,
        missing_needed_pages,
        truncated_searches,
    ) = _replay_searches(cache_entries, data_dir)

    raw_unique: dict[int, dict] = {}
    for row in raw_rows:
        if isinstance(row, dict) and "jobId" in row:
            raw_unique.setdefault(int(row["jobId"]), row)
    # The raw unique search rows are authoritative when available; cache rows supply
    # query order and per-occurrence attribution.
    for job_id, row in cache_unique.items():
        raw_unique.setdefault(job_id, row)

    full_by_id = {}
    for record in details:
        if record.get("description_coverage") == "full":
            full_by_id.setdefault(str(record.get("source_id")), dict(record))

    survivors = _search_survivors(raw_unique, started_dt.date().isoformat())
    missing_full = survivors - set(full_by_id)
    if missing_full:
        raise ValueError(
            f"recovery detail coverage incomplete: {len(missing_full)} of "
            f"{len(survivors)} Reed search-filter survivors lack a retained full description"
        )

    from skillmatch.etl.pipeline import OUT_OF_REGION, assess, remote_status
    from skillmatch.geo import Geocoder, postcode_outside_region

    geocoder = Geocoder(offline=True)
    records: list[dict] = []
    for occurrence in occurrences:
        job_id = occurrence["job_id"]
        row = raw_unique.get(job_id, occurrence["row"])
        record = full_by_id.get(str(job_id))
        if record is None:
            record = ReedAdapter.from_search_row(row).to_dict()
            # Recompute exactly the original pre-detail search screening decision.
            expires = record.get("expiration_date")
            if expires and expires < started_dt.date().isoformat():
                record["pre_excluded_reason"] = "expired"
            else:
                place = geocoder.locate_job(record.get("location_text"), record.get("postcode"))
                remote = remote_status(record, "unknown")
                reason, _, _ = assess(
                    record.get("title") or "",
                    html.unescape(row.get("jobDescription") or ""),
                    place,
                    remote,
                    None,
                )
                if (
                    reason is None
                    and place is None
                    and postcode_outside_region(record.get("postcode"))
                ):
                    reason = OUT_OF_REGION
                if reason:
                    record["pre_excluded_reason"] = reason
            record["fetched_at"] = datetime.fromtimestamp(occurrence["cache_mtime"], UTC).isoformat(
                timespec="seconds"
            )
        else:
            record = dict(record)
            if not record.get("fetched_at"):
                record["fetched_at"] = datetime.fromtimestamp(
                    occurrence["cache_mtime"], UTC
                ).isoformat(timespec="seconds")

        record["extra"] = {
            **(record.get("extra") or {}),
            "search_term": occurrence["search_term"],
            "search_location": occurrence["search_location"],
            "search_page": occurrence["search_page"],
            "matched_terms": row.get("_matched_terms", []),
        }
        records.append(record)

    other_sources = ("ats", "we_work_remotely", "remote_ok", "curated")
    source_counts = {}
    for source in other_sources:
        path = raw_dir / f"{source}_{run_id}.json"
        items = _json(path) if path.exists() else []
        records.extend(items)
        source_counts[source] = len(items)

    requests_by_source = _cache_request_counts(cache_entries)
    truncated = missing_needed_pages > 0 or bool(truncated_searches)
    reed_message = json.dumps(
        {
            "search_unique": len(raw_unique),
            "collected_observations": len(occurrences),
            "details_fetched": len(full_by_id),
            "search_queries_needed": needed_queries,
            "search_queries_recovered": recovered_queries,
            "search_queries_missing_needed_page": missing_needed_pages,
            "truncated_searches": truncated_searches,
            "request_count_basis": "successful responses reconstructed; original retry attempts unavailable",
        },
        sort_keys=True,
    )
    reed_run = _source_run(
        run_id,
        "reed",
        started_at,
        len(occurrences),
        len(full_by_id),
        requests_by_source["reed"],
        "partial" if truncated else "ok",
        reed_message,
    )
    if truncated:
        reed_run["_source_log"] = [
            {
                "source": "reed",
                "status": "partial",
                "note": json.dumps(
                    {
                        "missing_needed_pages": missing_needed_pages,
                        "full_final_pages": truncated_searches,
                        "queries_recovered": recovered_queries,
                    },
                    sort_keys=True,
                ),
                "count": missing_needed_pages + len(truncated_searches),
            }
        ]
    runs = [reed_run]
    for source in other_sources:
        count = source_counts[source]
        requests = requests_by_source[source]
        runs.append(
            _source_run(
                run_id,
                source,
                started_at,
                count,
                count,
                requests,
                "ok",
                "local raw capture replay; request count is successful cache responses only",
            )
        )

    metadata = {
        "run_id": run_id,
        "started_at": started_at,
        "original_collection_at": started_at,
        "data_mode": "live",
        "processing_mode": "recovery",
        "recovered_from": run_id,
        "original_collection_finished_at": datetime.fromtimestamp(end, UTC).isoformat(),
        "processed_classification_date": started_dt.date().isoformat(),
        "recovery_network_requests": 0,
        "prior_successful_reed_requests": requests_by_source["reed"],
        "prior_request_count_basis": "successful responses reconstructed; original retry attempts unavailable",
        "collection_complete": not truncated,
        "raw_source_files": [
            raw_path.name,
            details_path.name,
            *(f"{source}_{run_id}.json" for source in other_sources),
        ],
        "search_settings": {
            "centres": list(config.REED_GRID),
            "terms": _terms(data_dir),
            "radius_miles": config.REED_DISTANCE_MILES,
            "pages": config.REED_PAGES,
            "birmingham_pages": config.REED_BIRMINGHAM_PAGES,
            "request_cap": config.REED_MAX_REQUESTS,
        },
        "collection_counts": {
            "reed_observations": len(occurrences),
            "reed_search_unique": len(raw_unique),
            **source_counts,
            "total_collected": len(records),
            "search_queries_needed": needed_queries,
            "search_queries_recovered": recovered_queries,
            "search_queries_missing_needed_page": missing_needed_pages,
            "truncated_searches": truncated_searches,
        },
    }
    return {
        "records": records,
        "source_runs": runs,
        "run_id": run_id,
        "started_at": started_at,
        "folder_name": "20261027_1246_recovered",
        "metadata": metadata,
    }


def _readonly_connection(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)


def load_back_snapshot(
    backup_path: Path,
    data_dir: Path = config.DATA_DIR,
    original_settings: dict | None = None,
) -> dict:
    """Rebuild the 21 October collection from its readonly SQLite backup and raw files."""
    backup_path = Path(backup_path)
    data_dir = Path(data_dir)
    settings = dict(original_settings or {})
    with _readonly_connection(backup_path) as connection:
        connection.row_factory = sqlite3.Row
        if "source_runs" not in {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }:
            raise ValueError("backup database does not contain source_runs")
        run_rows = connection.execute(
            "SELECT * FROM source_runs ORDER BY started_at, source_id"
        ).fetchall()
        original_run_id = settings.get("run_id") or (
            run_rows[-1]["run_id"] if run_rows else _BACK_RUN_ID
        )
        selected_runs = [row for row in run_rows if row["run_id"] == original_run_id]
        if not selected_runs:
            raise ValueError(f"backup has no source runs for {original_run_id}")
        started_at = selected_runs[0]["started_at"]
        vacancy_rows = connection.execute(
            "SELECT * FROM vacancies ORDER BY source, source_id"
        ).fetchall()
        existing = {row[0] for row in connection.execute("SELECT DISTINCT run_id FROM source_runs")}

        original_records = {}
        for row in vacancy_rows:
            record = dict(row)
            if record.get("extra"):
                try:
                    record["extra"] = json.loads(record["extra"])
                except (ValueError, TypeError):
                    record["extra"] = {}
            original_records[(record["source"], str(record["source_id"]))] = record

    replay_id = f"{original_run_id}_reprocessed"
    suffix = 2
    while replay_id in existing:
        replay_id = f"{original_run_id}_reprocessed_{suffix}"
        suffix += 1

    raw_dir = data_dir / "raw"
    reed_raw_path = raw_dir / f"reed_{original_run_id}.json"
    reed_details_path = raw_dir / f"reed_details_{original_run_id}.json"
    reed_rows = _json(reed_raw_path) if reed_raw_path.exists() else []
    detail_rows = _json(reed_details_path) if reed_details_path.exists() else []
    reed_search = {
        str(row["jobId"]): row for row in reed_rows if isinstance(row, dict) and "jobId" in row
    }
    reed_full = {
        str(row.get("source_id")): dict(row)
        for row in detail_rows
        if row.get("source_id") is not None and _description_present(row)
    }
    fallback_fetched_at = started_at
    records = []
    other_cache: dict[str, dict[str, dict]] = {}
    for key, db_record in original_records.items():
        source, source_id = key
        if source == "reed":
            record = reed_full.get(source_id)
            if record is None:
                search_row = reed_search.get(source_id)
                record = (
                    ReedAdapter.from_search_row(search_row).to_dict()
                    if search_row is not None
                    else dict(db_record)
                )
                reed_coverage = (
                    record.get("description_coverage") or "unavailable"
                    if search_row is not None
                    else "unavailable"
                )
            else:
                record = dict(record)
                reed_coverage = "full"
            record["description_coverage"] = reed_coverage or record.get(
                "description_coverage", "unavailable"
            )
        else:
            raw_source = "ats" if source in {"greenhouse", "lever", "workable"} else source
            source_file = raw_dir / f"{raw_source}_{original_run_id}.json"
            if source_file.exists() and raw_source not in other_cache:
                other_cache[raw_source] = {
                    str(item.get("source_id")): item
                    for item in _json(source_file)
                    if isinstance(item, dict)
                }
            record = dict(other_cache.get(raw_source, {}).get(source_id, db_record))
            if not record.get("description_coverage"):
                record["description_coverage"] = (
                    "full" if _description_present(record) else "unavailable"
                )
        record["fetched_at"] = (
            db_record.get("fetched_at") or record.get("fetched_at") or fallback_fetched_at
        )
        record["source"] = source
        record["source_id"] = source_id
        record["vacancy_id"] = db_record.get("vacancy_id") or f"{source}:{source_id}"
        records.append(record)

    if len(records) != len(original_records):
        raise ValueError(
            f"snapshot replay retained {len(records)} of {len(original_records)} stored vacancy IDs"
        )

    runs = []
    for old_run in selected_runs:
        run = dict(old_run)
        run["run_id"] = replay_id
        runs.append(run)
    raw_source_paths = sorted(raw_dir.glob(f"*_{original_run_id}.json"))
    raw_finished_at = max((path.stat().st_mtime for path in raw_source_paths), default=0)
    metadata = {
        "run_id": replay_id,
        "started_at": started_at,
        "original_collection_at": started_at,
        "original_collection_finished_at": (
            datetime.fromtimestamp(raw_finished_at, UTC).isoformat()
            if raw_finished_at
            else started_at
        ),
        "processed_classification_date": datetime.fromisoformat(started_at).date().isoformat(),
        "data_mode": "live",
        "processing_mode": "reprocessed_snapshot",
        "reprocessed_from": backup_path.name,
        "original_settings": settings,
        "search_settings": _original_search_settings(settings),
        "collection_complete": False,
        "history_limitations": "Reprocessed from the retained database snapshot and available raw source files; original collection completeness is not asserted.",
        "raw_source_files": [path.name for path in raw_source_paths],
        "recovery_network_requests": 0,
    }
    return {
        "records": records,
        "source_runs": runs,
        "run_id": replay_id,
        "started_at": started_at,
        "folder_name": "20261021_2033_reprocessed",
        "metadata": metadata,
    }
