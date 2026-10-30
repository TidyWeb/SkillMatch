"""Milestone 2: a small, throttled live pull from Reed for studying how adverts are written.

Saves search rows and full details to data/raw/reed_sample_<timestamp>.json (git-ignored).
Usage: uv run python scripts/reed_sample.py [--details 180]
"""

import argparse
import json
import random
from datetime import UTC, datetime

from skillmatch import config
from skillmatch.sources.http import PoliteClient
from skillmatch.sources.reed import ReedAdapter

TERMS = [
    "data analyst",
    "junior data analyst",
    "MI analyst",
    "reporting analyst",
    "BI analyst",
    "insight analyst",
    "data officer",
    "data quality analyst",
    "research officer",
    "apprentice data analyst",
]
TOWNS = ["Birmingham", "Coventry", "Wolverhampton", "Worcester", "Stoke-on-Trent", "Telford"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--details", type=int, default=180)
    args = ap.parse_args()
    config.load_env()
    client = PoliteClient(max_requests=400)
    reed = ReedAdapter(client=client, towns=TOWNS, terms=TERMS)
    if not reed.enabled:
        raise SystemExit("REED_API_KEY not set")
    found = reed.search()
    ids = sorted(found)
    random.Random(42).shuffle(ids)
    details = []
    for job_id in ids[: args.details]:
        d = reed._get(f"https://www.reed.co.uk/api/1.0/jobs/{job_id}")
        if d and d.get("jobId"):
            d["_matched_terms"] = found[job_id].get("_matched_terms", [])
            details.append(d)
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = config.RAW_DIR / f"reed_sample_{ts}.json"
    out.write_text(
        json.dumps(
            {
                "fetched_at": ts,
                "terms": TERMS,
                "towns": TOWNS,
                "search_rows": list(found.values()),
                "details": details,
                "requests_made": client.requests_made,
                "cache_hits": client.cache_hits,
            }
        )
    )
    print(
        f"{len(found)} unique jobs from search; {len(details)} details; "
        f"{client.requests_made} requests ({client.cache_hits} cache hits) -> {out}"
    )


if __name__ == "__main__":
    main()
