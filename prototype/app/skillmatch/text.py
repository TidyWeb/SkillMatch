"""Consistent handling of absent source text without a pandas runtime dependency."""

from __future__ import annotations

import html
import math
import re

TEXT_FIELDS = (
    "source",
    "source_tier",
    "title",
    "employer",
    "location_text",
    "postcode",
    "url",
    "salary_text",
    "salary_period",
    "currency",
    "contract_type",
    "job_type",
    "posted_date",
    "expiration_date",
    "fetched_at",
    "remote_hint",
    "attribution",
    "description_coverage",
    "pre_excluded_reason",
)

_LATIN1_BYTE_RUN = re.compile(r"[\u0080-\u00ff]+")


def repair_mojibake(value):
    """Repair UTF-8 bytes that were decoded as Latin-1, without guessing other text.

    Only contiguous Latin-1 byte runs that form valid UTF-8 are changed. Correct Unicode
    characters such as a standalone `é` or a curly apostrophe are left alone.
    """
    if isinstance(value, str):
        def decode_run(match: re.Match) -> str:
            run = match.group(0)
            try:
                decoded = run.encode("latin-1").decode("utf-8")
            except UnicodeError:
                return run
            # A one-character round-trip is generally an ordinary accented letter, not
            # mojibake. UTF-8 sequences collapse multiple byte characters into text.
            return decoded if len(decoded) < len(run) else run

        return _LATIN1_BYTE_RUN.sub(decode_run, value)
    if isinstance(value, list):
        return [repair_mojibake(item) for item in value]
    if isinstance(value, dict):
        return {key: repair_mojibake(item) for key, item in value.items()}
    return value


def clean_text(value, *, collapse: bool = False) -> str:
    """None, numeric NaN, pandas NA/NaT and blank/non-text scalars become empty text.

    Missing values must not turn into the literal strings 'nan' or '<NA>'. Paragraph
    breaks and HTML are preserved unless a caller explicitly requests a single line.
    """
    if not isinstance(value, str):
        return ""
    value = value.strip()
    if value.casefold() in {"", "nan", "none", "null", "nat", "<na>"}:
        return ""
    return " ".join(html.unescape(value).split()) if collapse else value


def clean_number(value) -> float | None:
    try:
        number = float(value)
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) else None


def normalize_record(record: dict) -> dict:
    """Normalise source-boundary text and numeric fields while retaining every advert."""
    row = dict(record)
    for key in TEXT_FIELDS:
        value = clean_text(row.get(key), collapse=True)
        row[key] = value if key in {"source", "source_tier", "title", "url"} else value or None
    for key in ("description_html", "description_text"):
        row[key] = clean_text(row.get(key)) or None
    for key in ("salary_min", "salary_max", "lat", "lon"):
        row[key] = clean_number(row.get(key))
    row["extra"] = dict(row["extra"]) if isinstance(row.get("extra"), dict) else {}
    for key in ("country", "uk_eligibility", "search_term", "search_location", "listed_by"):
        if key in row["extra"]:
            row["extra"][key] = clean_text(row["extra"][key], collapse=True) or None
    return row
