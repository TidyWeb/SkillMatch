"""Display helpers registered as Jinja filters. Every value shown says plainly when it's unknown."""

from __future__ import annotations

import re

PERIODS = {
    "annum": "a year",
    "day": "a day",
    "hour": "an hour",
    "week": "a week",
    "month": "a month",
}
ARRANGEMENTS = {
    "onsite": "On site",
    "hybrid": "Hybrid",
    "remote": "Remote",
    "unknown": "Not stated",
}
UK_REMOTE = {
    "yes": "open to UK applicants",
    "unclear": "UK eligibility unclear",
    "no": "not open to UK applicants",
}


def _amount(x: float, period: str | None, symbol: str) -> str:
    if period in ("annum", None) and x >= 1000:
        return f"{symbol}{x:,.0f}"
    return f"{symbol}{x:,.2f}".replace(".00", "")


def salary(v: dict) -> str:
    if v.get("source") == "cv_library" and v.get("salary_text"):
        return v["salary_text"]  # CV-Library fields are shown unaltered
    lo, hi = v.get("salary_min"), v.get("salary_max")
    if lo is None and hi is None:
        return "Not stated"
    symbol = "$" if v.get("currency") == "USD" else "£"
    period = v.get("salary_period")
    lo = lo if lo is not None else hi
    hi = hi if hi is not None else lo
    text = (
        _amount(lo, period, symbol)
        if lo == hi
        else f"{_amount(lo, period, symbol)} – {_amount(hi, period, symbol)}"
    )
    return f"{text} {PERIODS[period]}" if period in PERIODS else f"{text} (period not given)"


def _days(n: float) -> str:
    return f"{n:g}"


def arrangement(v: dict) -> str:
    a = v.get("arrangement") or "unknown"
    lo, hi = v.get("office_days_min"), v.get("office_days_max")
    if a == "hybrid":
        if lo is not None and hi is not None:
            days = _days(lo) if lo == hi else f"{_days(lo)}–{_days(hi)}"
            unit = "day" if hi == 1 else "days"
            return f"Hybrid · {days} {unit} a week in the office"
        return "Hybrid · office days not stated"
    if a == "remote":
        extra = " with occasional office visits" if hi else ""
        uk = UK_REMOTE.get(v.get("uk_remote") or "", "")
        return f"Remote{extra}" + (f" · {uk}" if uk else "")
    if a == "onsite":
        return "On site"
    return "Arrangement not stated"


def distance(m) -> str:
    v = m.vacancy
    if v.get("is_remote"):
        return "UK-remote"
    if m.distance_miles is not None:
        return f"{m.distance_miles:.1f} miles straight-line"
    if v.get("location_unclear"):
        return "Location unclear"
    return "Distance unknown (add your postcode)"


def place(v: dict) -> str:
    text = v.get("location_text") or "Location not given"
    if v.get("is_remote") and text in ("UK-remote", ""):
        return "UK-remote"
    if v.get("location_approximate"):
        return f"{text} (area only)"
    return text


def answer_body(line: str) -> str:
    """'Requirement: Excel. Your evidence: you…' -> 'Your evidence: you…' (the table names the tag)."""
    return re.sub(r"^Requirement: [^.]*\.\s*", "", line or "")


def capfirst(s: str) -> str:
    return s[:1].upper() + s[1:] if s else s


FILTERS = {
    "salary": salary,
    "arrangement": arrangement,
    "distance": distance,
    "place": place,
    "capfirst": capfirst,
    "answer_body": answer_body,
}
