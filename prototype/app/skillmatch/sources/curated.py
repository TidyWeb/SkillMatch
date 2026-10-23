"""Tier B: adverts a team member checked by hand on sources with no API.

data/curated/adverts.csv stores ONLY: source name, advert URL, checked date, title, employer,
town or postcode, arrangement, office days, salary as stated, closing date, and our own
requirement list in our own words. No advert text is copied.

`requirements` is a list separated by ";" where each item starts "E:" (essential) or
"D:" (desirable), e.g. "E: Good Excel skills; D: Power BI".
"""

from __future__ import annotations

import csv
import re
from datetime import date
from html import escape
from pathlib import Path

from skillmatch import config
from skillmatch.parse import parse_salary
from skillmatch.sources.base import Vacancy

CSV_PATH = config.DATA_DIR / "curated" / "adverts.csv"
COLUMNS = [
    "source_name",
    "advert_url",
    "checked_date",
    "title",
    "employer",
    "town_or_postcode",
    "arrangement",
    "office_days",
    "salary_as_stated",
    "closing_date",
    "requirements",
]
REQUIRED = {
    "source_name",
    "advert_url",
    "checked_date",
    "title",
    "employer",
    "town_or_postcode",
    "requirements",
}
ARRANGEMENTS = {"", "onsite", "hybrid", "remote"}
REQ_ITEM = re.compile(r"^\s*([ED])\s*:\s*(.+?)\s*$", re.I)


def _iso(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def validate(path: Path | str = CSV_PATH) -> list[str]:
    """Return a list of problems; an empty list means the file is valid."""
    path = Path(path)
    problems: list[str] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            return [f"{path.name}: columns must be exactly: {', '.join(COLUMNS)}"]
        seen = set()
        for n, row in enumerate(reader, start=2):
            where = f"{path.name} line {n}"
            for col in sorted(REQUIRED):
                if not (row.get(col) or "").strip():
                    problems.append(f"{where}: '{col}' is empty")
            url = row.get("advert_url", "")
            if url and not url.startswith(("http://", "https://")):
                problems.append(f"{where}: advert_url must start with http:// or https://")
            if url in seen:
                problems.append(f"{where}: advert_url appears twice")
            seen.add(url)
            for col in ("checked_date", "closing_date"):
                v = (row.get(col) or "").strip()
                if v and not _iso(v):
                    problems.append(f"{where}: '{col}' must be a date like 2026-10-21")
            if (row.get("arrangement") or "").strip().lower() not in ARRANGEMENTS:
                problems.append(f"{where}: arrangement must be onsite, hybrid, remote or blank")
            days = (row.get("office_days") or "").strip()
            if days:
                try:
                    if not 0 <= float(days) <= 5:
                        raise ValueError
                except ValueError:
                    problems.append(f"{where}: office_days must be a number from 0 to 5")
            items = [i for i in (row.get("requirements") or "").split(";") if i.strip()]
            for item in items:
                if not REQ_ITEM.match(item):
                    problems.append(
                        f"{where}: requirement '{item.strip()}' must start with E: or D:"
                    )
            for item in items:
                if len(item.split()) > 30:
                    problems.append(
                        f"{where}: requirement '{item.strip()[:40]}…' is too long; "
                        "use your own short words"
                    )
    return problems


def to_vacancy(row: dict, n: int) -> Vacancy:
    ess, des = [], []
    for item in (row["requirements"] or "").split(";"):
        m = REQ_ITEM.match(item)
        if m:
            (ess if m.group(1).upper() == "E" else des).append(m.group(2))
    arrangement = (row.get("arrangement") or "").strip().lower()
    days = (row.get("office_days") or "").strip()
    loc_line = row["town_or_postcode"]
    if arrangement == "hybrid" and days:
        loc_line += f" / Hybrid ({days} days per week in the office)"
    elif arrangement:
        loc_line += f" / {arrangement}"
    html = f"<p>Location: {escape(loc_line)}</p>"
    html += (
        "<p><strong>Essential</strong></p><ul>"
        + "".join(f"<li>{escape(x)}</li>" for x in ess)
        + "</ul>"
    )
    if des:
        html += (
            "<p><strong>Desirable</strong></p><ul>"
            + "".join(f"<li>{escape(x)}</li>" for x in des)
            + "</ul>"
        )
    sal = parse_salary(row.get("salary_as_stated") or "") or {}
    return Vacancy(
        source="curated",
        source_id=f"c{n:04d}",
        source_tier="B",
        title=row["title"].strip(),
        url=row["advert_url"].strip(),
        employer=row["employer"].strip(),
        location_text=row["town_or_postcode"].strip(),
        description_html=html,
        salary_min=sal.get("salary_min"),
        salary_max=sal.get("salary_max"),
        salary_period=sal.get("salary_period"),
        salary_text=(row.get("salary_as_stated") or "").strip() or None,
        currency="GBP" if sal else None,
        posted_date=row["checked_date"].strip() or None,
        expiration_date=(row.get("closing_date") or "").strip() or None,
        attribution=(
            f"Checked by hand on {row['source_name'].strip()} ({row['checked_date'].strip()})"
        ),
        extra={
            "listed_by": row["source_name"].strip(),
            "checked_date": row["checked_date"].strip(),
        },
    )


class CuratedAdapter:
    name = "curated"
    tier = "B"
    enabled = True

    def __init__(self, path: Path | str = CSV_PATH):
        self.path = Path(path)
        self.stats: dict[str, int] = {}

    def fetch(self) -> list[Vacancy]:
        if not self.path.exists():
            return []
        problems = validate(self.path)
        if problems:
            raise ValueError("curated adverts are invalid:\n" + "\n".join(problems))
        with self.path.open(newline="") as f:
            rows = list(csv.DictReader(f))
        out = [to_vacancy(r, n) for n, r in enumerate(rows, 1)]
        self.stats = {"rows": len(out)}
        return out
