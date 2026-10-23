"""The data-quality report written after every ETL run: reports/quality_<run>.md."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pandas as pd

FIELDS = [
    "title",
    "employer",
    "location_text",
    "lat",
    "region",
    "url",
    "salary_min",
    "salary_period",
    "contract_type",
    "posted_date",
    "expiration_date",
    "arrangement",
    "office_days_min",
    "data_years",
]


def _table(rows: list[tuple], headers: tuple[str, ...]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def write_report(
    reports_dir: Path,
    run_id: str,
    mode: str,
    df: pd.DataFrame,
    stages: dict[str, int],
    runs: list[dict],
    requirements: list[dict],
    tags: list[dict],
    geocode_failures: list[str],
    meta: dict,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"quality_{run_id}.md"
    n = len(df)
    lines = [
        f"# Data quality report: {run_id}",
        "",
        f"Mode: **{mode}**. Snapshot date: {meta['snapshot_date']}. Built at {meta['built_at']}. "
        f"HTTP requests made: {meta['requests_made']}.",
        "",
        "## Rows per stage",
        "",
        _table(list(stages.items()), ("stage", "rows")),
        "",
        "## Sources",
        "",
        _table(
            [
                (
                    r["source_id"],
                    r["status"],
                    r["fetched"],
                    r["kept"],
                    r["requests"],
                    (r["message"] or "")[:120],
                )
                for r in runs
            ],
            ("source", "status", "fetched", "kept", "requests", "notes"),
        ),
        "",
        "## Excluded (kept in the database, hidden by default)",
        "",
    ]
    reasons = Counter(r for r in df["excluded_reason"] if isinstance(r, str))
    lines += [_table(sorted(reasons.items(), key=lambda x: -x[1]), ("reason", "rows")), ""]
    words = Counter(w for w in df["title_excluded_word"] if isinstance(w, str))
    lines += [
        "### Senior roles excluded, by title word",
        "",
        _table(sorted(words.items(), key=lambda x: -x[1]), ("word", "rows")) if words else "None.",
        "",
        "## Missing values per field",
        "",
        _table(
            [
                (
                    f,
                    int(df[f].isna().sum()) if f in df else n,
                    f"{(df[f].isna().mean() * 100 if f in df and n else 0):.0f}%",
                )
                for f in FIELDS
            ],
            ("field", "missing", "share"),
        ),
        "",
        "## Duplicates",
        "",
        f"{int((df['is_primary'] == 0).sum())} records are duplicates of another advert "
        f"({df['duplicate_group'].nunique()} groups). They stay in the database as 'also listed by' links.",
        "",
        "## Geocoding",
        "",
        f"{int(df['lat'].notna().sum())} of {n} placed; {int(df['location_approximate'].sum())} approximate "
        f"(county or region only); {int(df['location_unclear'].sum())} location unclear; "
        f"{int(df['is_remote'].sum())} remote.",
        "",
    ]
    fails = Counter(f for f in geocode_failures if f)
    if fails:
        lines += ["Locations we could not place:", ""]
        lines += [f"- {loc} ({c})" for loc, c in fails.most_common(30)]
        lines.append("")
    req = pd.DataFrame(requirements)
    if len(req):
        counted = req[req["strength"].isin(["essential", "desirable"])]
        tagged = set(t["req_id"] for t in tags)
        untagged = counted[~counted["req_id"].isin(tagged)]
        lines += [
            "## Requirements",
            "",
            _table(
                [(s, int(c)) for s, c in req["strength"].value_counts().items()],
                ("strength", "statements"),
            ),
            "",
            f"Unclassified (no skill or competency tag): {len(untagged)} of {len(counted)} essential or "
            f"desirable statements ({(len(untagged) / max(1, len(counted)) * 100):.0f}%). They are shown on "
            "the job page but don't count towards tiers.",
            "",
            f"Inferred classifications: {int((counted['confidence'] == 'inferred').sum())} of {len(counted)}.",
            "",
        ]
    shown = df[df["excluded_reason"].isna() & (df["is_primary"] == 1)]
    sal = shown["salary_stated"].sum() if len(shown) else 0
    lines += [
        "## Salary coverage (adverts shown by default)",
        "",
        f"{int(sal)} of {len(shown)} state a salary ({(sal / max(1, len(shown)) * 100):.0f}%).",
        "",
        _table(
            [
                (p or "not stated", int(c))
                for p, c in shown["salary_period"].fillna("").value_counts().items()
            ],
            ("period", "adverts"),
        )
        if len(shown)
        else "",
        "",
        "## Data-experience demands (adverts shown by default)",
        "",
        f"{int(shown['data_years'].notna().sum())} of {len(shown)} ask for experience in a data role "
        f"({int(shown['data_years_implied'].sum())} implied without a number).",
        "",
        "## Entry signals (adverts shown by default)",
        "",
    ]
    sig = Counter(s for js in shown["entry_signals"] for s in json.loads(js or "[]"))
    lines += [_table(sig.most_common(), ("signal", "adverts")) if sig else "None.", ""]
    path.write_text("\n".join(lines))
    return path
