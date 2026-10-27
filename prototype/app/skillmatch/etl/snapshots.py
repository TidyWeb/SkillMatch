"""Write append-only, privacy-limited CSV snapshots for collected vacancies."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, date, datetime
from pathlib import Path

from skillmatch.etl.outcomes import OUTCOMES

VACANCY_COLUMNS = (
    "run_id",
    "observation_id",
    "vacancy_id",
    "source",
    "source_id",
    "title",
    "employer",
    "location_text",
    "postcode",
    "region",
    "is_remote",
    "salary_min",
    "salary_max",
    "salary_period",
    "salary_text",
    "currency",
    "posted_date",
    "posted_week",
    "expiration_date",
    "description_coverage",
    "collected_at",
    "link",
    "outcome",
    "outcome_note",
    "eligibility_reason",
    "duplicate_of",
    "duplicate_source",
    "search_term",
    "search_location",
)
SKILL_COLUMNS = ("run_id", "vacancy_id", "skill", "strength", "confidence", "description_coverage")
FUNNEL_COLUMNS = ("run_id", "source", "collected", *OUTCOMES)
SOURCE_LOG_COLUMNS = (
    "run_id",
    "source",
    "source_id",
    "at",
    "status",
    "error_type",
    "board",
    "note",
    "count",
    "requests",
)
SEARCH_COLUMNS = (
    "run_id",
    "search_term",
    "collected_observations",
    "first_attributed_new",
    "matched_distinct",
    "shown_across_match",
)

_METADATA_KEYS = {
    "run_id",
    "started_at",
    "ended_at",
    "finished_at",
    "run_date",
    "mode",
    "sources",
    "search_settings",
    "filter_version",
    "filters_version",
    "taxonomy_version",
    "code_commit",
    "requests",
    "requests_used",
    "snapshot_date",
    "app_version",
    "source_status",
    "requests_made",
    "reed_requests",
    "data_mode",
    "working_code_fingerprint",
    "code_has_uncommitted_changes",
    "original_collection_at",
    "collection_at",
    "reprocessed_from",
    "recovered_from",
    "processing_mode",
    "processing_finished_at",
    "request_summary",
    "recovery_network_requests",
    "prior_successful_reed_requests",
    "prior_request_count_basis",
    "raw_sources",
    "original_run_id",
    "classification_date",
    "collection_limitations",
    "raw_source_files",
    "collection_counts",
    "original_collection_finished_at",
    "processing_started_at",
    "history_limitations",
    "collection_complete",
    "agency_coverage",
}
_SECRET_KEY = re.compile(r"(?:api.?key|secret|token|password|credential)", re.I)
_SECRET_VALUE = re.compile(r"(?i)\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]{20,})\b")


def _safe_metadata(metadata: dict, run_id: str) -> dict:
    def clean(value):
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items() if not _SECRET_KEY.search(str(k))}
        if isinstance(value, list):
            return [clean(v) for v in value]
        if isinstance(value, str) and _SECRET_VALUE.search(value):
            return "[redacted]"
        return value

    safe = {"run_id": run_id}
    for key, value in metadata.items():
        if key not in _METADATA_KEYS or _SECRET_KEY.search(key):
            continue
        safe[key] = clean(value)
    return safe


def _cell(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def _write_csv(path: Path, columns: Iterable[str], rows: Iterable[dict]) -> None:
    with path.open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(columns), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _cell(row.get(key)) for key in writer.fieldnames})


def _posted_week(value) -> str:
    if not value:
        return ""
    if isinstance(value, datetime):
        parsed = value.date()
    elif isinstance(value, date):
        parsed = value
    else:
        try:
            parsed = date.fromisoformat(str(value)[:10])
        except ValueError:
            return ""
    iso = parsed.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def _vacancy_row(row: dict, run_id: str) -> dict:
    out = {key: row.get(key) for key in VACANCY_COLUMNS}
    out["run_id"] = run_id
    out["collected_at"] = row.get("collected_at") or row.get("fetched_at") or ""
    out["link"] = row.get("link") or row.get("url") or ""
    out["posted_week"] = _posted_week(row.get("posted_date"))
    out["description_coverage"] = row.get("description_coverage") or "unavailable"
    return out


def _strength(value: str | None) -> str:
    if value in ("essential", "desirable"):
        return value
    return "unclear"


def _coverage_by_vacancy(observations: list[dict]) -> dict[str, str]:
    rank = {"unavailable": 0, "search excerpt only": 1, "full": 2}
    best: dict[str, str] = {}
    for row in observations:
        vid = row.get("vacancy_id")
        coverage = row.get("description_coverage") or "unavailable"
        if coverage not in rank:
            coverage = "unavailable"
        if vid and rank[coverage] > rank.get(best.get(vid, "unavailable"), 0):
            best[vid] = coverage
    return best


def _skill_rows(
    requirements: list[dict], tags: list[dict], coverage: dict[str, str], run_id: str
) -> list[dict]:
    tag_ids: dict[str, set[str]] = defaultdict(set)
    for tag in tags:
        if tag.get("tag_type") == "skill":
            tag_ids[str(tag.get("req_id"))].add(str(tag.get("tag_id")))
    strength_rank = {"unclear": 0, "desirable": 1, "essential": 2}
    confidence_rank = {"low": 0, "medium": 1, "high": 2}
    found: dict[tuple[str, str], dict] = {}
    for req in requirements:
        vid = req.get("vacancy_id")
        if not vid:
            continue
        strength = _strength(req.get("strength"))
        confidence = req.get("confidence") or ""
        for skill in tag_ids.get(str(req.get("req_id")), set()):
            key = (str(vid), skill)
            current = found.get(key)
            if current is None:
                found[key] = {"strength": strength, "confidence": confidence}
                continue
            if strength_rank[strength] > strength_rank[current["strength"]]:
                current["strength"] = strength
                current["confidence"] = confidence
            elif strength == current["strength"] and confidence_rank.get(
                str(confidence).lower(), -1
            ) > confidence_rank.get(str(current["confidence"]).lower(), -1):
                current["confidence"] = confidence
    return [
        {
            "run_id": run_id,
            "vacancy_id": vid,
            "skill": skill,
            "strength": v["strength"],
            "confidence": v["confidence"],
            "description_coverage": coverage.get(vid, "unavailable"),
        }
        for (vid, skill), v in sorted(found.items())
    ]


def _funnel_rows(rows: list[dict], run_id: str) -> list[dict]:
    result = []
    for source_row in rows:
        source = source_row.get("source") or source_row.get("source_id")
        if not source or source == "ALL":
            continue
        row = {"run_id": run_id, "source": source, "collected": source_row.get("collected", 0)}
        for outcome in OUTCOMES:
            row[outcome] = source_row.get(outcome, 0)
        result.append(row)
    return result


def _source_log_rows(rows: list[dict], run_id: str) -> list[dict]:
    result = []
    for original in rows:
        row = {key: original.get(key, "") for key in SOURCE_LOG_COLUMNS}
        row["run_id"] = run_id
        # Keep only safe categorical error details if callers supply a richer exception object.
        if not row["error_type"] and row.get("status") in ("error", "partial"):
            note = str(row.get("note") or "")
            row["error_type"] = note.split(":", 1)[0] if note else ""
        if isinstance(row.get("note"), str):
            row["note"] = _SECRET_VALUE.sub("[redacted]", row["note"])
            if _SECRET_KEY.search(row["note"]):
                row["note"] = "[redacted]"
        result.append(row)
    return result


def _search_rows(observations: list[dict], run_id: str, configured_terms=()) -> list[dict]:
    terms: dict[str, dict] = {}
    first_seen: set[str] = set()
    duplicate_parent = {
        str(row.get("vacancy_id")): str(row.get("duplicate_of"))
        for row in observations
        if row.get("vacancy_id")
        and row.get("duplicate_of")
        and str(row.get("vacancy_id")) != str(row.get("duplicate_of"))
        and row.get("outcome")
        in ("duplicate of an advert from another source", "duplicate within the same source")
    }

    def canonical_id(vacancy_id: str) -> str:
        path = set()
        current = vacancy_id
        while current in duplicate_parent and current not in path:
            path.add(current)
            parent = duplicate_parent[current]
            if parent == current:
                break
            current = parent
        return current

    globally_shown = {
        str(row.get("vacancy_id"))
        for row in observations
        if row.get("vacancy_id") and row.get("outcome") == "shown"
    }
    canonical_shown = {canonical_id(vacancy_id) for vacancy_id in globally_shown}
    for item in configured_terms or ():
        term = (
            str(item.get("term") or item.get("keywords") or "").strip()
            if isinstance(item, dict)
            else str(item).strip()
        )
        if term:
            terms.setdefault(
                term,
                {
                    "collected_observations": 0,
                    "first_attributed_new": 0,
                    "vacancies": set(),
                    "shown": set(),
                },
            )
    for row in observations:
        term = str(row.get("search_term") or "").strip()
        if not term:
            continue
        item = terms.setdefault(
            term,
            {
                "collected_observations": 0,
                "first_attributed_new": 0,
                "vacancies": set(),
                "shown": set(),
            },
        )
        item["collected_observations"] += 1
        vid = str(row.get("vacancy_id") or row.get("observation_id") or "")
        if vid:
            item["vacancies"].add(vid)
            if vid not in first_seen:
                item["first_attributed_new"] += 1
                first_seen.add(vid)
            canonical = canonical_id(vid)
            if canonical in canonical_shown:
                item["shown"].add(canonical)
    return [
        {
            "run_id": run_id,
            "search_term": term,
            "collected_observations": item["collected_observations"],
            "first_attributed_new": item["first_attributed_new"],
            "matched_distinct": len(item["vacancies"]),
            "shown_across_match": len(item["shown"]),
        }
        for term, item in sorted(terms.items())
    ]


def _plain_date(metadata: dict) -> str:
    for key in ("original_collection_at", "snapshot_date", "started_at"):
        value = metadata.get(key)
        if not value:
            continue
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            continue
        return f"{parsed.day} {parsed.strftime('%B %Y')}"
    return "date unavailable"


def _plain_source(source: str) -> str:
    names = {
        "reed": "Reed",
        "greenhouse": "Greenhouse",
        "lever": "Lever",
        "workable": "Workable",
        "remote_ok": "Remote OK",
        "we_work_remotely": "We Work Remotely",
        "curated": "curated adverts",
    }
    return names.get(source, source.replace("_", " ").title())


def _readme(metadata: dict | None = None, observations: list[dict] | None = None) -> str:
    metadata = metadata or {}
    observations = observations or []
    run_date = _plain_date(metadata)
    distinct_adverts = len(
        {str(row.get("vacancy_id")) for row in observations if row.get("vacancy_id")}
    )
    shown = len(
        {
            str(row.get("vacancy_id"))
            for row in observations
            if row.get("vacancy_id") and row.get("outcome") == "shown"
        }
    )
    sources = sorted(
        {_plain_source(str(row.get("source"))) for row in observations if row.get("source")}
    )
    source_list = ", ".join(sources[:-1]) + (f" and {sources[-1]}" if len(sources) > 1 else "")
    if not source_list:
        source_list = "not recorded"

    if metadata.get("reprocessed_from"):
        one_line = "This is a reprocessed copy of the 21 October collection. It is not a new collection."
        notes = (
            "- This is a reprocessed copy, not a new collection.\n"
            "- Some adverts were missing from the saved database.\n"
            "- Expiry was checked using the original collection date."
        )
    elif metadata.get("recovered_from"):
        one_line = "This recovers the live collection from 27 October using files already saved."
        notes = (
            "- No new job-site requests were made during recovery.\n"
            "- Some searches reached their last allowed page.\n"
            "- Older posting weeks may be incomplete."
        )
    else:
        one_line = f"This is a live collection of job adverts gathered on {run_date}."
        notes = (
            "- Some search pages may be incomplete.\n"
            "- Older posting weeks may be incomplete.\n"
            "- Check the original advert before applying."
        )

    return f"""# Collection: {run_date}

{one_line}

## The numbers

- Adverts collected: {distinct_adverts:,}
- Adverts kept (in `shown.csv`): {shown:,}
- Sources: {source_list}

## Start here

Open `shown.csv`. Then `dropped.csv` for what was filtered out and why.

## Files

| File | What it holds |
|---|---|
| `shown.csv` | Adverts that passed every filter |
| `dropped.csv` | Everything else, with the reason |
| `skills.csv` | Skills each advert asks for |
| `funnel.csv` | The counts at a glance |
| `search_terms_yield.csv` | Which search words found what |
| `source_log.csv` | How each job site behaved |
| `run.json` | Settings used (technical) |

What every column means: [../data_dictionary.md](../data_dictionary.md)

## Notes on this run

{notes}
"""


def write_snapshot(
    *,
    data_dir: Path,
    run_id: str,
    observations: list[dict],
    requirements: list[dict],
    tags: list[dict],
    funnel: list[dict],
    source_log: list[dict],
    metadata: dict,
    folder_name: str | None = None,
) -> Path:
    """Write one new run folder under ``data_dir/snapshots`` and return its path.

    Folder creation and every file open are exclusive. Existing snapshots are never replaced;
    a colliding requested name receives a numeric suffix.
    """
    data_dir = Path(data_dir)
    snapshots = data_dir / "snapshots"
    snapshots.mkdir(parents=True, exist_ok=True)
    base_name = folder_name or datetime.now(UTC).strftime("%Y%m%d_%H%M")
    if Path(base_name).name != base_name or base_name in (".", ".."):
        raise ValueError("folder_name must be one directory name")
    candidate = base_name
    suffix = 2
    while True:
        target = snapshots / candidate
        try:
            target.mkdir(exist_ok=False)
            break
        except FileExistsError:
            candidate = f"{base_name}_{suffix}"
            suffix += 1

    exported = [_vacancy_row(row, run_id) for row in observations]
    shown = [r for r in exported if r.get("outcome") == "shown"]
    dropped = [r for r in exported if r.get("outcome") != "shown"]
    coverage = _coverage_by_vacancy(observations)
    skills = _skill_rows(requirements, tags, coverage, run_id)
    funnel_export = _funnel_rows(funnel, run_id)
    log_export = _source_log_rows(source_log, run_id)
    settings = (metadata or {}).get("search_settings") or {}
    configured_terms = settings.get("terms", []) if isinstance(settings, dict) else []
    search_export = _search_rows(observations, run_id, configured_terms)
    _write_csv(target / "shown.csv", VACANCY_COLUMNS, shown)
    _write_csv(target / "dropped.csv", VACANCY_COLUMNS, dropped)
    _write_csv(target / "skills.csv", SKILL_COLUMNS, skills)
    _write_csv(target / "funnel.csv", FUNNEL_COLUMNS, funnel_export)
    _write_csv(target / "source_log.csv", SOURCE_LOG_COLUMNS, log_export)
    _write_csv(target / "search_terms_yield.csv", SEARCH_COLUMNS, search_export)
    run_data = _safe_metadata(metadata or {}, run_id)
    (target / "run.json").open("x", encoding="utf-8").write(
        json.dumps(run_data, ensure_ascii=False, indent=2) + "\n"
    )
    (target / "README.md").open("x", encoding="utf-8").write(_readme(run_data, observations))
    return target
