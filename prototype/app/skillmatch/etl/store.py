"""SQLite schema and loading. The database is a read-only build artefact for the web app."""

from __future__ import annotations

import os
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);

CREATE TABLE vacancies (
    vacancy_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    source_tier TEXT NOT NULL,
    source_label TEXT,
    listed_by TEXT,
    title TEXT NOT NULL,
    employer TEXT,
    location_text TEXT,
    postcode TEXT,
    lat REAL,
    lon REAL,
    region TEXT,
    county TEXT,
    geo_method TEXT,
    location_approximate INTEGER DEFAULT 0,
    location_unclear INTEGER DEFAULT 0,
    is_remote INTEGER DEFAULT 0,
    uk_remote TEXT,
    url TEXT,
    salary_min REAL,
    salary_max REAL,
    salary_period TEXT,
    salary_text TEXT,
    currency TEXT,
    salary_stated INTEGER DEFAULT 0,
    contract_type TEXT,
    job_type TEXT,
    posted_date TEXT,
    expiration_date TEXT,
    arrangement TEXT,
    office_days_min REAL,
    office_days_max REAL,
    arrangement_text TEXT,
    data_years REAL,
    data_years_text TEXT,
    data_years_implied INTEGER DEFAULT 0,
    degree TEXT,
    degree_text TEXT,
    entry_signals TEXT,
    title_boost TEXT,
    title_excluded_word TEXT,
    excluded_reason TEXT,
    duplicate_group TEXT,
    is_primary INTEGER DEFAULT 1,
    attribution TEXT,
    fetched_at TEXT,
    extra TEXT
);
CREATE INDEX vacancies_excluded ON vacancies (excluded_reason);
CREATE INDEX vacancies_group ON vacancies (duplicate_group);

CREATE TABLE requirements (
    req_id TEXT PRIMARY KEY,
    vacancy_id TEXT NOT NULL REFERENCES vacancies (vacancy_id),
    n INTEGER NOT NULL,
    text_ours TEXT,
    strength TEXT NOT NULL,
    confidence TEXT NOT NULL,
    section TEXT,
    evidence_sentence TEXT NOT NULL
);
CREATE INDEX requirements_vacancy ON requirements (vacancy_id);

CREATE TABLE requirement_tags (
    req_id TEXT NOT NULL REFERENCES requirements (req_id),
    tag_type TEXT NOT NULL,
    tag_id TEXT NOT NULL
);
CREATE INDEX requirement_tags_req ON requirement_tags (req_id);

CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tier TEXT NOT NULL,
    kind TEXT,
    url TEXT,
    docs_url TEXT,
    attribution TEXT,
    enabled INTEGER,
    notes TEXT
);

CREATE TABLE source_runs (
    run_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    mode TEXT NOT NULL,
    started_at TEXT,
    finished_at TEXT,
    fetched INTEGER,
    kept INTEGER,
    requests INTEGER,
    status TEXT,
    message TEXT
);

CREATE TABLE duplicates (
    group_id TEXT NOT NULL,
    vacancy_id TEXT NOT NULL,
    primary_id TEXT NOT NULL,
    reason TEXT NOT NULL
);

CREATE TABLE places (
    key TEXT PRIMARY KEY,
    lat REAL,
    lon REAL,
    region TEXT,
    county TEXT,
    method TEXT,
    approximate INTEGER
);
"""


def write_database(path: Path, tables: dict[str, list[dict]], meta: dict[str, str]) -> None:
    """Write a fresh database to a temporary file, then move it into place atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.stem}-{os.getpid()}-{time.time_ns()}.db.tmp")
    conn = sqlite3.connect(tmp)
    try:
        conn.executescript(SCHEMA)
        conn.executemany("INSERT INTO meta VALUES (?, ?)", sorted(meta.items()))
        for table, rows in tables.items():
            if not rows:
                continue
            cols = list(rows[0].keys())
            sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})"
            conn.executemany(sql, [tuple(r.get(c) for c in cols) for r in rows])
        conn.commit()
    finally:
        conn.close()
    tmp.replace(path)


def connect_readonly(path: Path | str) -> sqlite3.Connection:
    """Open the built database read-only (the web app never writes)."""
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
