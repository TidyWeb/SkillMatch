"""Copy retained snapshots and history to a portable export directory."""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

from skillmatch import config

_EXTENSIONS = {".csv", ".json", ".md"}
_CURRENT_HISTORY_FILES = {"adverts_history.csv", "daily_changes.csv"}

DATA_DICTIONARY = """# Data dictionary

Use `vacancy_id` to count adverts. The same advert can appear in more than one row when it appears in several searches.

## shown.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `observation_id` | ID for this appearance in a search. |
| `vacancy_id` | Stable advert ID, made from the source and its ID. |
| `source` | Job site or advert source. |
| `source_id` | Advert ID used by the source. |
| `title` | Job title. |
| `employer` | Employer named in the advert. |
| `location_text` | Location as written by the source. |
| `postcode` | Postcode, when available. |
| `region` | Region assigned to the advert. |
| `is_remote` | Whether the advert says the job is remote. |
| `salary_min` | Lowest salary amount, when given. |
| `salary_max` | Highest salary amount, when given. |
| `salary_period` | Whether pay is yearly, monthly, daily, hourly or another period. |
| `salary_text` | Salary text as shown by the source. |
| `currency` | Currency used for the salary. |
| `posted_date` | Date the source says the advert was posted. |
| `posted_week` | Week the advert was posted. |
| `expiration_date` | Advert closing date, when available. |
| `description_coverage` | Whether the full advert, a short summary or no description was available. |
| `collected_at` | When SkillMatch collected this advert. |
| `link` | Link to the original advert. |
| `outcome` | Whether the advert was kept or why it was dropped. |
| `outcome_note` | Extra explanation when the outcome is `other`. |
| `eligibility_reason` | Another filter reason when the main outcome is a duplicate. |
| `duplicate_of` | ID of the advert kept instead of this duplicate. |
| `duplicate_source` | Source of the advert kept instead of this duplicate. |
| `search_term` | Search words that found this advert. |
| `search_location` | Place used in the search. |

## dropped.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `observation_id` | ID for this appearance in a search. |
| `vacancy_id` | Stable advert ID, made from the source and its ID. |
| `source` | Job site or advert source. |
| `source_id` | Advert ID used by the source. |
| `title` | Job title. |
| `employer` | Employer named in the advert. |
| `location_text` | Location as written by the source. |
| `postcode` | Postcode, when available. |
| `region` | Region assigned to the advert. |
| `is_remote` | Whether the advert says the job is remote. |
| `salary_min` | Lowest salary amount, when given. |
| `salary_max` | Highest salary amount, when given. |
| `salary_period` | Whether pay is yearly, monthly, daily, hourly or another period. |
| `salary_text` | Salary text as shown by the source. |
| `currency` | Currency used for the salary. |
| `posted_date` | Date the source says the advert was posted. |
| `posted_week` | Week the advert was posted. |
| `expiration_date` | Advert closing date, when available. |
| `description_coverage` | Whether the full advert, a short summary or no description was available. |
| `collected_at` | When SkillMatch collected this advert. |
| `link` | Link to the original advert. |
| `outcome` | Why the advert was dropped. |
| `outcome_note` | Extra explanation when the outcome is `other`. |
| `eligibility_reason` | Another filter reason when the main outcome is a duplicate. |
| `duplicate_of` | ID of the advert kept instead of this duplicate. |
| `duplicate_source` | Source of the advert kept instead of this duplicate. |
| `search_term` | Search words that found this advert. |
| `search_location` | Place used in the search. |

## skills.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `vacancy_id` | Advert this skill belongs to. |
| `skill` | Skill named in the advert. |
| `strength` | Whether the advert calls the skill essential, desirable or unclear. |
| `confidence` | How clearly the skill was stated. |
| `description_coverage` | Whether the full advert, a short summary or no description was available. |

## funnel.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `source` | Job site or advert source. |
| `collected` | Number of advert appearances recorded for this source. |
| `shown` | Appearances that passed the filters. |
| `outside area` | Appearances outside the search area. |
| `overseas-only remote` | Remote appearances that cannot be worked from the UK. |
| `senior` | Appearances for senior or lead roles. |
| `needs professional qualification` | Appearances that require a professional qualification. |
| `training or fake advert` | Appearances that are courses or misleading adverts. |
| `not a data role` | Appearances outside the data job scope. |
| `expired` | Appearances for adverts that had expired. |
| `duplicate of an advert from another source` | Appearances duplicated on another source. |
| `duplicate within the same source` | Repeated appearances from the same source. |
| `other` | Appearances dropped for another stated reason. |

## source_log.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `source` | Job site or advert source. |
| `source_id` | Advert ID, when the log entry relates to one advert. |
| `at` | When the source event was recorded. |
| `status` | Whether the source worked, partly worked or failed. |
| `error_type` | Short name for an error, if one happened. |
| `board` | Careers board involved, when available. |
| `note` | Short explanation of the source event. |
| `count` | Number of items covered by the event, when available. |
| `requests` | Number of recorded requests for the event. |

## search_terms_yield.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `search_term` | Words used to search. |
| `collected_observations` | Number of search appearances found by these words. |
| `first_attributed_new` | Distinct adverts first found by these words. |
| `matched_distinct` | Distinct adverts found by these words. |
| `shown_across_match` | Distinct adverts kept that matched these words. |

## history/adverts_history.csv

| Column | What it means |
|---|---|
| `vacancy_id` | Stable advert ID. |
| `first_seen` | First collection date when this advert appeared. |
| `last_seen` | Most recent collection date when it appeared. |
| `times_seen` | Number of collections that included this advert. |
| `latest_outcome` | Most recent keep or drop reason. |
| `sources_seen` | Sources where this advert or its duplicate appeared. |

## history/daily_changes.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `run_date` | Date of the collection. |
| `source` | Job site or advert source. |
| `new` | Distinct adverts not seen in the previous comparable collection. |
| `gone` | Distinct adverts missing from the previous comparable collection. |
| `still_live` | Distinct adverts seen in both comparable collections. |
| `completeness` | Whether the source collection was complete enough to compare. |
| `comparable` | Whether the two collections can be compared fairly. |
| `days_listed_gone_mean` | Average days listed for adverts that disappeared. |
| `days_listed_gone` | Days listed for each advert that disappeared. |

## run.json

| Field | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `started_at` | When the collection started. |
| `finished_at` | When collection finished. |
| `snapshot_date` | Date used to label this collection. |
| `data_mode` | Whether this was live, fixture, recovered or reprocessed data. |
| `sources` | Sources included in the run. |
| `source_status` | Whether each source worked, partly worked or failed. |
| `requests_made` | Recorded requests made during the run. |
| `reed_requests` | Recorded Reed requests. |
| `search_settings` | Search places, words, page limits and related settings. |
| `filter_version` | Version of the rules used to keep or drop adverts. |
| `taxonomy_version` | Version of the skill list used. |
| `code_commit` | App revision used for the run, when available. |
| `working_code_fingerprint` | Short check value for the working app code. |
| `code_has_uncommitted_changes` | Whether app files had unsaved Git changes. |
| `history_limitations` | Known limits when comparing this run with earlier runs. |
| `request_summary` | Notes about what the request totals include. |
| `original_collection_at` | Original start time for recovered or reprocessed data. |
| `original_collection_finished_at` | Original finish time, when known. |
| `processing_mode` | How the collected records were prepared. |
| `reprocessed_from` | Saved source used to rebuild an older collection. |
| `recovered_from` | Saved source used to recover an interrupted collection. |
| `prior_successful_reed_requests` | Successful Reed replies found in saved files. |
| `prior_request_count_basis` | Note explaining what the earlier Reed request count includes. |
| `collection_complete` | Whether all planned searches finished. |
| `raw_source_files` | Names of saved source files used for recovery. |
| `recovery_network_requests` | New requests made while recovering a run. |
| `collection_counts` | Summary counts for records and searches. |
| `processing_finished_at` | When record processing finished. |
| `agency_coverage` | Notes about agencies already covered by other sources. |

## Technical notes

`description_coverage` is `full`, `search excerpt only` or `unavailable`. A missing skill row does not mean the advert did not ask for that skill. Funnel counts are search appearances; one advert can appear more than once. Blank history comparisons mean there is not enough evidence to compare, not zero. “Gone” means missing from the next comparable collection, not confirmed filled. Dates only bound when SkillMatch saw an advert; they do not prove it was available every day between collections.

Run details include source settings and processing history. Fingerprints are short checks of the code and rule files used; they are not security signatures. Request totals can count saved successful responses or recorded attempts; use the request notes to see which. To export from the working app, run `make export-snapshot TARGET=your-folder`. The export adds new snapshot folders and refreshes the current history files.
"""


class ExportConflictError(RuntimeError):
    """Raised when an existing snapshot or destination layout conflicts with export."""


class UnsafeExportError(RuntimeError):
    """Raised when an export would follow a symlink or overlap its source tree."""


def _reject_symlink_components(path: Path) -> None:
    absolute = path.absolute()
    for item in (absolute, *absolute.parents):
        if item.is_symlink():
            raise UnsafeExportError(f"symlink path component is not allowed: {item}")


def _source_files(root: Path) -> dict[Path, Path]:
    """Return allowed files keyed by relative path, while rejecting any symlink."""
    if root.is_symlink():
        raise UnsafeExportError(f"symlink source is not allowed: {root}")
    if not root.exists():
        return {}
    if not root.is_dir():
        raise NotADirectoryError(root)
    files = {}
    for current, dirs, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in dirs:
            child = current_path / name
            if child.is_symlink():
                raise UnsafeExportError(f"symlink source is not allowed: {child}")
        for name in names:
            child = current_path / name
            if child.is_symlink():
                raise UnsafeExportError(f"symlink source is not allowed: {child}")
            if child.is_file() and child.suffix.lower() in _EXTENSIONS:
                files[child.relative_to(root)] = child
    return files


def _same_tree(source_files: dict[Path, Path], target_root: Path) -> bool:
    if target_root.is_symlink() or not target_root.is_dir():
        return False
    target_files = _source_files(target_root)
    # The destination must contain exactly the same eligible file set. Disallowed files
    # are also a conflict; they must not be silently mixed into a retained snapshot.
    all_target_files = {
        path.relative_to(target_root) for path in target_root.rglob("*") if path.is_file()
    }
    if all_target_files != set(target_files):
        return False
    if set(source_files) != set(target_files):
        return False
    return all(
        source_files[rel].read_bytes() == target_files[rel].read_bytes() for rel in source_files
    )


def _copy_files_exclusive(files: dict[Path, Path], destination_root: Path) -> tuple[int, int]:
    count = total_bytes = 0
    destination_root.mkdir(parents=True, exist_ok=True)
    for relative, source in sorted(files.items(), key=lambda pair: str(pair[0])):
        destination = destination_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as input_file, destination.open("xb") as output_file:
            shutil.copyfileobj(input_file, output_file)
        count += 1
        total_bytes += source.stat().st_size
    return count, total_bytes


def _copy_immutable_tree(source: Path, destination: Path) -> tuple[int, int, bool]:
    files = _source_files(source)
    if destination.is_symlink():
        raise UnsafeExportError(f"symlink destination is not allowed: {destination}")
    if destination.exists():
        if _same_tree(files, destination):
            return 0, 0, True
        raise ExportConflictError(f"existing export differs from source: {destination}")
    count, total_bytes = _copy_files_exclusive(files, destination)
    return count, total_bytes, False


def _copy_history(data_history: Path, target_history: Path) -> dict:
    copied = skipped = total_bytes = 0
    report_paths: list[str] = []
    if data_history.is_symlink():
        raise UnsafeExportError(f"symlink source is not allowed: {data_history}")
    if not data_history.exists():
        return {"copied": copied, "skipped": skipped, "bytes": total_bytes, "paths": report_paths}
    if not data_history.is_dir():
        raise NotADirectoryError(data_history)
    if target_history.is_symlink():
        raise UnsafeExportError(f"symlink destination is not allowed: {target_history}")
    target_history.mkdir(parents=True, exist_ok=True)
    refresh: list[tuple[Path, Path]] = []
    for name in sorted(_CURRENT_HISTORY_FILES):
        source = data_history / name
        if source.is_symlink():
            raise UnsafeExportError(f"symlink source is not allowed: {source}")
        if not source.exists():
            continue
        if not source.is_file() or source.suffix.lower() not in _EXTENSIONS:
            raise ExportConflictError(f"history current export is not a regular file: {source}")
        destination = target_history / name
        if destination.is_symlink():
            raise UnsafeExportError(f"symlink destination is not allowed: {destination}")
        if destination.exists():
            if not destination.is_file():
                raise ExportConflictError(f"existing export is not a file: {destination}")
            if destination.read_bytes() == source.read_bytes():
                skipped += 1
            else:
                refresh.append((source, destination))
        else:
            _copy_one_immutable(source, destination)
            copied += 1
            total_bytes += source.stat().st_size
            report_paths.append(str(destination))

    if refresh:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        source_versions = data_history / "versions"
        if source_versions.is_symlink():
            raise UnsafeExportError(f"symlink backup directory is not allowed: {source_versions}")
        if source_versions.exists() and not source_versions.is_dir():
            raise ExportConflictError(f"backup destination is not a directory: {source_versions}")
        source_versions.mkdir(parents=True, exist_ok=True)
        backup = source_versions / f"export-current-{stamp}-{uuid.uuid4().hex[:8]}"
        backup.mkdir(parents=True, exist_ok=False)
        # Retain every current file that is about to be refreshed before changing any.
        for _source, destination in refresh:
            backup_file = backup / destination.name
            with destination.open("rb") as input_file, backup_file.open("xb") as output_file:
                shutil.copyfileobj(input_file, output_file)
        for source, destination in refresh:
            temporary = destination.parent / (destination.name + ".export-" + uuid.uuid4().hex)
            with source.open("rb") as input_file, temporary.open("xb") as output_file:
                shutil.copyfileobj(input_file, output_file)
            os.replace(temporary, destination)
            copied += 1
            total_bytes += source.stat().st_size
            report_paths.append(str(destination))

    return {"copied": copied, "skipped": skipped, "bytes": total_bytes, "paths": report_paths}


def _plain_date(metadata: dict) -> str:
    value = (
        metadata.get("original_collection_at")
        or metadata.get("snapshot_date")
        or metadata.get("started_at")
    )
    if not value:
        return "date unavailable"
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return "date unavailable"
    return f"{parsed.day} {parsed.strftime('%B %Y')}"


def _snapshot_summary(folder: Path) -> dict:
    metadata_path = folder / "run.json"
    metadata = (
        json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
    )
    all_ids: set[str] = set()
    shown_ids: set[str] = set()
    sources: set[str] = set()
    for name in ("shown.csv", "dropped.csv"):
        path = folder / name
        if not path.is_file():
            continue
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                vacancy_id = str(row.get("vacancy_id") or "").strip()
                if vacancy_id:
                    all_ids.add(vacancy_id)
                    if name == "shown.csv":
                        shown_ids.add(vacancy_id)
                if row.get("source"):
                    sources.add(row["source"])
    if metadata.get("reprocessed_from"):
        description = "Reprocessed 21 October collection"
    elif metadata.get("recovered_from"):
        description = "Recovered 27 October live collection"
    else:
        description = f"Live collection from {_plain_date(metadata)}"
    return {
        "folder": folder.name,
        "description": description,
        "collected": len(all_ids),
        "shown": len(shown_ids),
        "sources": sorted(sources),
    }


def _top_readme(snapshots: list[dict]) -> str:
    rows = "\n".join(
        f"| `{item['folder']}/` | {item['description']} | {item['collected']:,} | {item['shown']:,} |"
        for item in snapshots
    )
    if not rows:
        rows = "| No snapshots yet | | 0 | 0 |"
    return f"""# SkillMatch job data

Real job adverts collected by SkillMatch, for the data team to analyse.

## Start here

1. Open the newest dated folder.
2. Open `shown.csv`. These are the adverts a graduate would see.
3. Then look at `dropped.csv` to see what was filtered out, and why.

## The folders

Each folder is one collection. The name is the date and time it ran.

| Folder | What it is | Adverts collected | Adverts kept |
|---|---|---:|---:|
{rows}

`history/` tracks every advert across all runs: when it was first seen, last seen, and how many times.

New runs add new folders. Nothing is ever overwritten.

## What's in each folder

| File | What it holds |
|---|---|
| `shown.csv` | Adverts that passed every filter |
| `dropped.csv` | Everything else, with the reason it was dropped |
| `skills.csv` | The skills each advert asks for: essential, desirable or unclear |
| `funnel.csv` | The counts at a glance |
| `search_terms_yield.csv` | Which search words found which adverts |
| `source_log.csv` | How each job site behaved during the run |
| `run.json` | The settings used for the run (technical) |

What every column means: [data_dictionary.md](data_dictionary.md)

## Why adverts get dropped

- Not a data job
- Senior role
- Outside the West Midlands
- Overseas-only remote job
- Needs a professional qualification (ACCA and similar)
- A training course dressed up as a job
- The same advert listed twice
- Expired
- Other (missing details; the note says what)

## Watch out for

- **Repeats in `dropped.csv`.** The same advert often turns up in several searches. Count adverts by `vacancy_id`, not by rows.
- **Short summaries.** Some adverts only had a short summary, not the full text. The `description_coverage` column shows which. If a skill is missing, the employer may still have asked for it.
- **Changed settings.** The first two runs used different search settings. Don't read the difference between them as the job market changing.
- **Older weeks look quieter.** Adverts that were filled before we started collecting are missing. See the limitations notes in the repo.
- **Salaries.** Some are yearly, some daily or hourly. Check `salary_period` before comparing.

## Where it comes from

Reed, the Gymshark, Monzo, Kpler and Biffa careers sites, We Work Remotely and Remote OK. Every row links back to the original advert. We keep a summary, not the advert text.
"""


def _write_generated_file(path: Path, content: str) -> tuple[int, int, str | None]:
    if path.is_symlink():
        raise UnsafeExportError(f"symlink destination is not allowed: {path}")
    encoded = content.encode("utf-8")
    if path.is_file() and path.read_bytes() == encoded:
        return 0, 0, None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return 1, len(encoded), str(path)


def _write_export_readmes(data_dir: Path, target: Path) -> dict:
    snapshots_dir = data_dir / "snapshots"
    summaries = []
    if snapshots_dir.is_dir():
        summaries = [
            _snapshot_summary(folder)
            for folder in sorted(snapshots_dir.iterdir(), reverse=True)
            if folder.is_dir() and not folder.is_symlink()
        ]
    copied = total_bytes = 0
    report_paths = []
    for path, content in (
        (target / "README.md", _top_readme(summaries)),
        (target / "data_dictionary.md", DATA_DICTIONARY),
    ):
        count, size, report_path = _write_generated_file(path, content)
        copied += count
        total_bytes += size
        if report_path:
            report_paths.append(report_path)
    return {"copied": copied, "bytes": total_bytes, "paths": report_paths}


def _copy_one_immutable(source: Path, destination: Path) -> bool:
    if destination.is_symlink():
        raise UnsafeExportError(f"symlink destination is not allowed: {destination}")
    if destination.exists():
        if destination.is_file() and source.read_bytes() == destination.read_bytes():
            return False
        raise ExportConflictError(f"existing export differs from source: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as input_file, destination.open("xb") as output_file:
        shutil.copyfileobj(input_file, output_file)
    return True


def export_data(data_dir: Path, target: Path) -> dict:
    """Export retained snapshots and history without copying private or raw data.

    Identical immutable snapshots are skipped. A differing
    snapshot is a conflict. Only the current history CSVs are exported; changed target
    copies are backed up under the source data directory's ``history/versions``.
    """
    data_dir, target = Path(data_dir), Path(target)
    _reject_symlink_components(data_dir)
    _reject_symlink_components(target)
    source_root = data_dir.resolve()
    target_root = target.resolve()
    try:
        target_root.relative_to(source_root)
    except ValueError:
        pass
    else:
        raise UnsafeExportError("target must be outside the source data directory")
    if not data_dir.is_dir():
        raise NotADirectoryError(data_dir)

    target_history = target / "history"
    target_versions = target_history / "versions"
    if target_history.is_symlink():
        raise UnsafeExportError(f"symlink destination is not allowed: {target_history}")
    if target_versions.is_symlink() or target_versions.exists():
        raise ExportConflictError(
            "destination history/versions already exists; move it aside after separate confirmation"
        )

    target.mkdir(parents=True, exist_ok=True)
    snapshots = data_dir / "snapshots"
    copied = skipped = total_bytes = 0
    report_paths: list[str] = []
    if snapshots.exists():
        _source_files(snapshots)  # validates symlinks throughout the source tree
        for source in sorted(snapshots.iterdir()):
            if source.is_symlink():
                raise UnsafeExportError(f"symlink source is not allowed: {source}")
            if not source.is_dir():
                continue
            destination = target / source.name
            file_count, byte_count, was_skipped = _copy_immutable_tree(source, destination)
            copied += file_count
            total_bytes += byte_count
            skipped += int(was_skipped)
            if file_count:
                report_paths.append(str(destination))

    history_stats = _copy_history(data_dir / "history", target_history)
    copied += history_stats["copied"]
    skipped += history_stats["skipped"]
    total_bytes += history_stats["bytes"]
    report_paths.extend(history_stats["paths"])
    readme_stats = _write_export_readmes(data_dir, target)
    copied += readme_stats["copied"]
    total_bytes += readme_stats["bytes"]
    report_paths.extend(readme_stats["paths"])
    return {
        "files_copied": copied,
        "items_skipped": skipped,
        "total_bytes": total_bytes,
        "report_paths": report_paths,
        "target": str(target.resolve()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export SkillMatch snapshots and history")
    parser.add_argument("--target", required=True, type=Path, help="destination export directory")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=config.DATA_DIR,
        help="source data directory (defaults to the configured SkillMatch data directory)",
    )
    args = parser.parse_args(argv)
    result = export_data(args.data_dir, args.target)
    print(
        f"Exported {result['files_copied']} files ({result['total_bytes']} bytes); "
        f"skipped {result['items_skipped']} identical items to {result['target']}"
    )
    for path in result["report_paths"]:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
