"""ETL: extract -> clean -> parse -> geocode -> filter -> de-duplicate -> load SQLite -> report.

    python -m skillmatch.etl --mode fixtures|live

Fixtures mode needs no keys and no network. Live mode reads REED_API_KEY (and optionally
CVLIBRARY_FEED_URL) from the environment or .env.
"""

from __future__ import annotations

import csv
import html
import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd

from skillmatch import config
from skillmatch.etl.dedupe import group_duplicates
from skillmatch.etl.report import write_report
from skillmatch.etl.store import write_database
from skillmatch.filters import (
    NOT_A_DATA_ROLE,
    OUT_OF_REGION,
    TRAINING_COURSE,
    check_title,
    is_data_role,
    is_training_course,
)
from skillmatch.geo import WEST_MIDLANDS, Geocoder, is_remote_location, postcode_outside_region
from skillmatch.parse import parse_advert, parse_salary, uk_remote_eligibility
from skillmatch.sources.ats import ATSAdapter
from skillmatch.sources.curated import CuratedAdapter
from skillmatch.sources.cvlibrary import CVLibraryAdapter
from skillmatch.sources.http import PoliteClient, RequestCapReached
from skillmatch.sources.reed import ReedAdapter
from skillmatch.sources.registry import SOURCES, source_label
from skillmatch.sources.remote_boards import RemoteOKAdapter, WeWorkRemotelyAdapter
from skillmatch.taxonomy import get_taxonomy

log = logging.getLogger(__name__)

SENIOR_ROLE = "senior role"
NOT_UK = "remote role not open to UK applicants"
NO_DETAILS = "details not fetched (request cap reached)"
REMOTE_SOURCES = {"we_work_remotely", "remote_ok"}
NATIONAL = {"united kingdom", "uk", "england", "nationwide", "great britain"}


@dataclass
class RunResult:
    mode: str
    db_path: Path
    report_path: Path
    stage_counts: dict[str, int]
    source_runs: list[dict]
    shown: int
    excluded: Counter = field(default_factory=Counter)


def load_terms() -> list[str]:
    with (config.DATA_DIR / "search_terms.csv").open() as f:
        return [r["term"] for r in csv.DictReader(f)]


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------------------------
# Assessment shared by the Reed search stage and the main pipeline
# ---------------------------------------------------------------------------------------------


def remote_status(v: dict, arrangement: str) -> bool:
    loc = (v.get("location_text") or "").strip()
    if v["source"] in REMOTE_SOURCES or is_remote_location(loc) and loc.lower() not in NATIONAL:
        return True
    if loc.lower() in NATIONAL and arrangement == "remote":
        return True
    return v.get("remote_hint") == "remote" and loc in ("", "UK-remote")


def assess(title: str, text: str, place, is_remote: bool, uk_remote: str | None) -> tuple:
    """(excluded_reason or None, title exclude word, title boost words)."""
    verdict = check_title(title)
    reason = None
    if is_training_course(title, text):
        reason = TRAINING_COURSE
    elif is_remote and uk_remote == "no":
        reason = NOT_UK
    elif not is_remote and place is not None and place.region != WEST_MIDLANDS:
        reason = OUT_OF_REGION
    elif verdict.excluded_by:
        reason = SENIOR_ROLE
    elif not is_data_role(title, text):
        reason = NOT_A_DATA_ROLE
    return reason, verdict.excluded_by, verdict.boosted_by


# ---------------------------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------------------------


def _source_run(run_id, source_id, mode, started, fetched, kept, requests, status, message=""):
    return {
        "run_id": run_id,
        "source_id": source_id,
        "mode": mode,
        "started_at": started,
        "finished_at": _now(),
        "fetched": fetched,
        "kept": kept,
        "requests": requests,
        "status": status,
        "message": message,
    }


def extract_fixtures(run_id: str, fixtures_path: Path) -> tuple[list[dict], list[dict]]:
    started = _now()
    records = json.loads(Path(fixtures_path).read_text())
    runs = [
        _source_run(run_id, "fixture", "fixtures", started, len(records), len(records), 0, "ok")
    ]
    return records, runs


def extract_reed_live(run_id, client, today) -> tuple[list[dict], dict, dict]:
    """Search the grid, filter on search rows, fetch details only for survivors."""
    started = _now()
    stats: dict[str, int] = {}
    reed = ReedAdapter(
        client=client,
        towns=config.REED_GRID,
        terms=load_terms(),
        distance_miles=config.REED_DISTANCE_MILES,
        pages_per_search=config.REED_PAGES,
    )
    if not reed.enabled:
        return (
            [],
            {},
            _source_run(
                run_id, "reed", "live", started, 0, 0, 0, "disabled", "REED_API_KEY not set"
            ),
        )
    before = client.requests_made
    offline_geo = Geocoder(offline=True)
    try:
        rows = reed.search()
    except RequestCapReached:
        rows = reed.search_results
    stats["search_unique"] = len(rows)
    out: list[dict] = []
    survivors = []
    expired = 0
    for row in rows.values():
        v = ReedAdapter.from_search_row(row).to_dict()
        if v["expiration_date"] and v["expiration_date"] < today.isoformat():
            expired += 1
            continue
        text = html.unescape(row.get("jobDescription") or "")
        # Offline tables only at this stage: no postcode lookups before we know we want the job.
        place = offline_geo.locate_job(v["location_text"], v["postcode"])
        is_remote = remote_status(v, "unknown")
        reason, _, _ = assess(v["title"], text, place, is_remote, None)
        if reason is None and place is None and postcode_outside_region(v["postcode"]):
            reason = OUT_OF_REGION
        if reason:
            v["pre_excluded_reason"] = reason
            out.append(v)
        else:
            survivors.append(row)
    stats["expired_in_search"] = expired
    stats["excluded_at_search"] = len(out)
    stats["survived_search"] = len(survivors)
    details = 0
    for i, row in enumerate(survivors):
        try:
            d = reed.detail(row["jobId"])
        except RequestCapReached:
            for rest in survivors[i:]:
                v = ReedAdapter.from_search_row(rest).to_dict()
                v["pre_excluded_reason"] = NO_DETAILS
                out.append(v)
            stats["stopped_at_cap"] = 1
            break
        except Exception as exc:  # one bad advert shouldn't stop the run
            log.warning("Reed detail %s failed: %s", row["jobId"], type(exc).__name__)
            continue
        if d is None:
            continue
        out.append(ReedAdapter.to_vacancy(d, row).to_dict())
        details += 1
    stats["details_fetched"] = details
    run = _source_run(
        run_id,
        "reed",
        "live",
        started,
        len(rows),
        details,
        client.requests_made - before,
        "ok",
        json.dumps(stats),
    )
    return out, rows, run


def extract_live(run_id, clients, today) -> tuple[list[dict], list[dict], dict[str, list]]:
    records: list[dict] = []
    runs: list[dict] = []
    raw: dict[str, list] = {}
    reed_records, reed_rows, reed_run = extract_reed_live(run_id, clients["reed"], today)
    records += reed_records
    runs.append(reed_run)
    raw["reed"] = list(reed_rows.values()) if reed_rows else []
    raw["reed_details"] = [r for r in reed_records if not r.get("pre_excluded_reason")]

    adapters = [
        ("ats", ATSAdapter(client=clients["feeds"])),
        ("we_work_remotely", WeWorkRemotelyAdapter(client=clients["feeds"])),
        ("remote_ok", RemoteOKAdapter(client=clients["feeds"])),
        ("cv_library", CVLibraryAdapter(client=clients["feeds"])),
        ("curated", CuratedAdapter()),
    ]
    for source_id, adapter in adapters:
        started = _now()
        before = clients["feeds"].requests_made
        if not getattr(adapter, "enabled", True):
            runs.append(
                _source_run(
                    run_id, source_id, "live", started, 0, 0, 0, "disabled", "not configured"
                )
            )
            continue
        try:
            got = [v.to_dict() for v in adapter.fetch()]
            status, message = "ok", json.dumps(getattr(adapter, "stats", {}))
        except Exception as exc:
            log.warning("%s failed: %s", source_id, exc)
            got, status, message = [], "error", f"{type(exc).__name__}: {exc}"[:300]
        records += got
        raw[source_id] = got
        runs.append(
            _source_run(
                run_id,
                source_id,
                "live",
                started,
                len(got),
                len(got),
                clients["feeds"].requests_made - before,
                status,
                message,
            )
        )
    return records, runs, raw


# ---------------------------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------------------------


def run(
    mode: str,
    db_path: Path | None = None,
    reports_dir: Path | None = None,
    fixtures_path: Path | None = None,
    offline: bool | None = None,
    today: date | None = None,
    client: PoliteClient | None = None,
) -> RunResult:
    if mode not in ("fixtures", "live"):
        raise ValueError("mode must be 'fixtures' or 'live'")
    config.load_env()
    tax = get_taxonomy()
    today = today or date.today()
    db_path = Path(db_path or config.DB_PATH)
    reports_dir = Path(reports_dir or config.REPORTS_DIR)
    offline = (mode == "fixtures") if offline is None else offline
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    # Separate request budgets: Reed's cap applies to Reed alone.
    clients = {
        "reed": client or PoliteClient(max_requests=config.REED_MAX_REQUESTS),
        "feeds": client or PoliteClient(max_requests=200),
        "geo": client or PoliteClient(min_interval=0.25, max_requests=5000),
    }
    geocoder = Geocoder(client=None if offline else clients["geo"], offline=offline)
    stages: dict[str, int] = {}

    # ---- extract ----
    if mode == "fixtures":
        records, runs = extract_fixtures(run_id, Path(fixtures_path or config.FIXTURES_PATH))
        curated = CuratedAdapter()
        got = [v.to_dict() for v in curated.fetch()]
        records += got
        runs.append(_source_run(run_id, "curated", mode, _now(), len(got), len(got), 0, "ok"))
    else:
        records, runs, raw = extract_live(run_id, clients, today)
        config.RAW_DIR.mkdir(parents=True, exist_ok=True)
        for source_id, items in raw.items():
            (config.RAW_DIR / f"{source_id}_{run_id}.json").write_text(json.dumps(items))
    for r in records:
        r.setdefault("vacancy_id", f"{r['source']}:{r['source_id']}")
    stages["extracted"] = len(records)

    df = pd.DataFrame(records)
    df = df.drop_duplicates("vacancy_id").reset_index(drop=True)
    # Sources disagree on which fields they send; pandas fills the gaps with NaN. Use None.
    df = df.astype(object).where(df.notna(), None)
    stages["unique ids"] = len(df)

    # ---- clean ----
    for col in ("title", "employer", "location_text"):
        df[col] = df[col].map(
            lambda s: " ".join(html.unescape(s).split()) if isinstance(s, str) else None
        )
    expired = df["expiration_date"].notna() & (
        df["expiration_date"].astype(str) < today.isoformat()
    )
    stages["dropped as expired"] = int(expired.sum())
    df = df[~expired].reset_index(drop=True)
    stages["after expiry"] = len(df)

    # ---- parse ----
    parsed = []
    requirements: list[dict] = []
    tags: list[dict] = []
    for _, row in df.iterrows():
        country = (
            (row.get("extra") or {}).get("country") if isinstance(row.get("extra"), dict) else None
        )
        p = parse_advert(row["description_html"], row["title"], tax, structured_country=country)
        parsed.append(p)
        for r in p.requirements:
            if r.strength == "other":
                continue
            req_id = f"{row['vacancy_id']}#{r.n}"
            requirements.append(
                {
                    "req_id": req_id,
                    "vacancy_id": row["vacancy_id"],
                    "n": r.n,
                    "text_ours": "; ".join(tax.label(t, i) for t, i in r.tags) or None,
                    "strength": r.strength,
                    "confidence": r.confidence,
                    "section": r.section,
                    "evidence_sentence": r.text[: config.EVIDENCE_MAX_CHARS],
                }
            )
            tags += [{"req_id": req_id, "tag_type": t, "tag_id": i} for t, i in r.tags]
    df["description_text"] = [p.description_text for p in parsed]
    df["n_requirements"] = [len(p.counted) for p in parsed]
    df["arrangement"] = [p.arrangement for p in parsed]
    df["office_days_min"] = [p.office_days_min for p in parsed]
    df["office_days_max"] = [p.office_days_max for p in parsed]
    df["arrangement_text"] = [p.arrangement_text for p in parsed]
    df["data_years"] = [p.data_years for p in parsed]
    df["data_years_text"] = [p.data_years_text for p in parsed]
    df["data_years_implied"] = [int(p.data_years_implied) for p in parsed]
    df["degree"] = [p.degree for p in parsed]
    df["degree_text"] = [p.degree_text for p in parsed]
    df["entry_signals"] = [json.dumps(p.entry_signals) for p in parsed]
    stages["parsed"] = len(df)

    # Salary: structured fields first; otherwise only what the text states.
    for i, row in df.iterrows():
        if (
            pd.isna(row.get("salary_min"))
            and pd.isna(row.get("salary_max"))
            and row["source"] != "remote_ok"
        ):
            s = parse_salary(row["description_text"])
            if s:
                for k, val in s.items():
                    df.at[i, k] = val
                df.at[i, "currency"] = "GBP"
    df["salary_stated"] = (df["salary_min"].notna() | df["salary_max"].notna()).astype(int)

    # ---- geocode ----
    geo_cols = {
        k: [] for k in ("lat", "lon", "region", "county", "geo_method", "location_approximate")
    }
    remote_flags, uk_flags, unclear = [], [], []
    places = []
    for (_, row), p in zip(df.iterrows(), parsed, strict=True):
        v = row.to_dict()
        is_remote = remote_status(v, p.arrangement)
        place = (
            None
            if is_remote and v["location_text"] in ("UK-remote", "")
            else geocoder.locate_job(v["location_text"], v.get("postcode"))
        )
        places.append(place)
        extra = v.get("extra") if isinstance(v.get("extra"), dict) else {}
        uk = None
        if is_remote or p.arrangement == "remote":
            uk = extra.get("uk_eligibility")
            if uk != "yes":
                uk = (
                    p.uk_remote
                    if p.uk_remote != "not_applicable"
                    else uk_remote_eligibility(p.description_text)
                )
        remote_flags.append(int(is_remote))
        uk_flags.append(uk)
        unclear.append(int(place is None and not is_remote))
        geo_cols["lat"].append(place.lat if place else None)
        geo_cols["lon"].append(place.lon if place else None)
        geo_cols["region"].append(place.region if place else None)
        geo_cols["county"].append(place.county if place else None)
        geo_cols["geo_method"].append(place.method if place else None)
        geo_cols["location_approximate"].append(int(bool(place and place.approximate)))
    for k, vals in geo_cols.items():
        df[k] = vals
    df["is_remote"] = remote_flags
    df["uk_remote"] = uk_flags
    df["location_unclear"] = unclear
    stages["geocoded"] = int((df["lat"].notna()).sum())
    stages["location unclear"] = int(df["location_unclear"].sum())

    # ---- filters ----
    reasons, words, boosts = [], [], []
    for (_, row), place in zip(df.iterrows(), places, strict=True):
        reason, word, boost = assess(
            row["title"], row["description_text"], place, bool(row["is_remote"]), row["uk_remote"]
        )
        pre = row.get("pre_excluded_reason")
        if reason is None and isinstance(pre, str):
            reason = pre
        reasons.append(reason)
        words.append(word)
        boosts.append(json.dumps(boost))
    df["excluded_reason"] = reasons
    df["title_excluded_word"] = words
    df["title_boost"] = boosts

    # ---- de-duplicate ----
    towns = {name for name in _known_towns()}
    dup_table = group_duplicates(df, towns)
    stages["duplicate records (not primary)"] = int((df["is_primary"] == 0).sum())

    shown = df[(df["excluded_reason"].isna()) & (df["is_primary"] == 1)]
    stages["shown by default (primary, not excluded)"] = len(shown)

    # ---- load ----
    df["listed_by"] = [
        (x or {}).get("listed_by") if isinstance(x, dict) else None
        for x in df.get("extra", [None] * len(df))
    ]
    df["source_label"] = [
        source_label(s, e, lb)
        for s, e, lb in zip(df["source"], df["employer"], df["listed_by"], strict=True)
    ]
    vac_cols = [
        "vacancy_id", "source", "source_id", "source_tier", "source_label", "listed_by", "title", "employer",
        "location_text", "postcode", "lat", "lon", "region", "county", "geo_method", "location_approximate",
        "location_unclear", "is_remote", "uk_remote", "url", "salary_min", "salary_max", "salary_period",
        "salary_text", "currency", "salary_stated", "contract_type", "job_type", "posted_date",
        "expiration_date", "arrangement", "office_days_min", "office_days_max", "arrangement_text",
        "data_years", "data_years_text", "data_years_implied", "degree", "degree_text", "entry_signals",
        "title_boost", "title_excluded_word", "excluded_reason", "duplicate_group", "is_primary",
        "attribution", "fetched_at", "extra",
    ]  # fmt: skip
    out = df.reindex(columns=vac_cols).copy()
    out["extra"] = [json.dumps(x) if isinstance(x, dict) else None for x in out["extra"]]
    out = out.astype(object).where(out.notna(), None)
    meta = {
        "data_mode": mode,
        "built_at": _now(),
        "snapshot_date": today.isoformat(),
        "run_id": run_id,
        "requests_made": str(
            0
            if offline and mode == "fixtures"
            else sum(c.requests_made for c in set(clients.values()))
        ),
        "reed_requests": str(clients["reed"].requests_made),
    }
    sources = [{**s, "enabled": int(_enabled(s["source_id"], mode, runs))} for s in SOURCES]
    place_rows = [
        {
            "key": k,
            "lat": p.lat if p else None,
            "lon": p.lon if p else None,
            "region": p.region if p else None,
            "county": p.county if p else None,
            "method": p.method if p else None,
            "approximate": int(bool(p and p.approximate)),
        }
        for k, p in geocoder.cache.items()
    ]
    write_database(
        db_path,
        {
            "vacancies": out.to_dict("records"),
            "requirements": requirements,
            "requirement_tags": tags,
            "sources": sources,
            "source_runs": runs,
            "duplicates": dup_table.to_dict("records"),
            "places": place_rows,
        },
        meta,
    )
    report_path = write_report(
        reports_dir, run_id, mode, df, stages, runs, requirements, tags, geocoder.failures, meta
    )
    return RunResult(
        mode=mode,
        db_path=db_path,
        report_path=report_path,
        stage_counts=stages,
        source_runs=runs,
        shown=len(shown),
        excluded=Counter(r for r in df["excluded_reason"] if isinstance(r, str)),
    )


def _enabled(source_id: str, mode: str, runs: list[dict]) -> bool:
    if source_id == "discovery":
        return True
    if source_id == "fixture":
        return mode == "fixtures"
    if source_id in ("greenhouse", "lever", "workable"):
        source_id = "ats"
    return any(r["source_id"] == source_id and r["status"] == "ok" for r in runs)


def _known_towns() -> set[str]:
    from skillmatch.geo import town_table

    return set(town_table().keys())
