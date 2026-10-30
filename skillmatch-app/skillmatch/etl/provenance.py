"""Public, non-secret run provenance and reproducible rule fingerprints."""

from __future__ import annotations

import csv
import hashlib
import subprocess

from skillmatch import config


def fingerprint(paths) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def run_metadata(meta: dict, runs: list[dict]) -> dict:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=config.ROOT, text=True, capture_output=True, check=False
    )
    modules = [
        config.ROOT / "skillmatch" / name
        for name in (
            "filters.py",
            "parse.py",
            "etl/pipeline.py",
            "etl/dedupe.py",
            "etl/outcomes.py",
        )
    ]
    return {
        "run_id": meta["run_id"],
        "started_at": meta["started_at"],
        "finished_at": meta["built_at"],
        "snapshot_date": meta["snapshot_date"],
        "data_mode": meta["data_mode"],
        "sources": [r["source_id"] for r in runs],
        "source_status": {r["source_id"]: r["status"] for r in runs},
        "requests_made": int(meta["requests_made"]),
        "reed_requests": int(meta["reed_requests"]),
        "search_settings": {
            "centres": config.REED_GRID,
            "radius_miles": config.REED_DISTANCE_MILES,
            "pages": config.REED_PAGES,
            "birmingham_pages": getattr(config, "REED_BIRMINGHAM_PAGES", config.REED_PAGES),
            "request_cap": config.REED_MAX_REQUESTS,
            "terms": [
                r["term"] for r in csv.DictReader((config.DATA_DIR / "search_terms.csv").open())
            ],
        },
        "filter_version": fingerprint(modules),
        "taxonomy_version": fingerprint(config.TAXONOMY_DIR.rglob("*.yaml")),
        "code_commit": completed.stdout.strip() if completed.returncode == 0 else "unavailable",
        "working_code_fingerprint": fingerprint((config.ROOT / "skillmatch").rglob("*.py")),
        "code_has_uncommitted_changes": True,
        "history_limitations": "Absence from a bounded search is not proof that a vacancy was filled. "
        "Older posting weeks undercount. Sources, terms and page caps affect comparisons.",
    }
