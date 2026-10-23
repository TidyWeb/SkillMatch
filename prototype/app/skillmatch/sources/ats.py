"""Employer applicant-tracking-system boards: Greenhouse, Lever and Workable.

Each employer publishes its own board; there is no cross-employer search. Slugs live in
data/employer_boards.csv. We keep only postings in the UK (the ETL then keeps West Midlands
and UK-remote ones).

- Greenhouse Job Board API, https://docs.greenhouse.io/job-board.html: GET is public, no auth.
  GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true
- Lever Postings API, https://github.com/lever/postings-api: GET published postings.
  GET https://api.lever.co/v0/postings/{site}?mode=json
- Workable published jobs, https://help.workable.com/hc/en-us/articles/115012771647:
  GET https://www.workable.com/api/accounts/{subdomain}?details=true
"""

from __future__ import annotations

import csv
import html
import logging
from datetime import UTC, datetime

from skillmatch import config
from skillmatch.sources.base import Vacancy
from skillmatch.sources.common import UK_HINT, pick_location
from skillmatch.sources.http import PoliteClient

log = logging.getLogger(__name__)


def load_boards(path=None) -> list[dict]:
    path = path or config.DATA_DIR / "employer_boards.csv"
    with open(path) as f:
        return [r for r in csv.DictReader(f)]


def _is_wm(loc: str) -> bool:
    from skillmatch.geo import town_table

    first = loc.split(",")[0].strip().lower()
    place = town_table().get(first)
    return bool(place and place.region == "West Midlands")


def _remote_text(text: str) -> bool:
    return "remote" in (text or "").lower()


class ATSAdapter:
    tier = "A"
    enabled = True

    def __init__(self, client: PoliteClient | None = None, boards: list[dict] | None = None):
        self.client = client or PoliteClient()
        self.boards = boards if boards is not None else load_boards()
        self.stats: dict[str, int] = {}

    def fetch(self) -> list[Vacancy]:
        out: list[Vacancy] = []
        for b in self.boards:
            try:
                fetched = getattr(self, f"_{b['platform']}")(b)
            except Exception as exc:
                log.warning("%s board %s failed: %s", b["platform"], b["slug"], exc)
                self.stats[f"{b['slug']}_error"] = 1
                continue
            self.stats[b["slug"]] = len(fetched)
            out.extend(fetched)
        return out

    # ----- Greenhouse -----
    def _greenhouse(self, b: dict) -> list[Vacancy]:
        url = f"https://boards-api.greenhouse.io/v1/boards/{b['slug']}/jobs"
        body = self.client.get(url, params={"content": "true"})
        out = []
        for j in body.get("jobs", []):
            locs = [x.strip() for x in (j.get("location") or {}).get("name", "").split(";")]
            locs += [o.get("location") or "" for o in j.get("offices") or []]
            loc = pick_location(locs, _is_wm)
            if not loc or not (UK_HINT.search(" ".join(locs)) or _remote_text(" ".join(locs))):
                continue
            out.append(
                Vacancy(
                    source="greenhouse",
                    source_id=f"{b['slug']}-{j['id']}",
                    source_tier="A",
                    title=j.get("title", "").strip(),
                    url=j.get("absolute_url"),
                    employer=b["employer"],
                    location_text=loc,
                    description_html=html.unescape(j.get("content") or ""),
                    posted_date=(j.get("first_published") or j.get("updated_at") or "")[:10]
                    or None,
                    attribution=f"Posted on {b['employer']}'s Greenhouse job board",
                    extra={"board": b["slug"], "platform": "greenhouse"},
                )
            )
        return out

    # ----- Lever -----
    def _lever(self, b: dict) -> list[Vacancy]:
        body = self.client.get(
            f"https://api.lever.co/v0/postings/{b['slug']}", params={"mode": "json"}
        )
        out = []
        for j in body if isinstance(body, list) else []:
            cats = j.get("categories") or {}
            locs = cats.get("allLocations") or [cats.get("location") or ""]
            country = j.get("country")
            workplace = j.get("workplaceType")
            if country and country != "GB":
                continue
            if not country and not UK_HINT.search(" ".join(locs)):
                continue
            parts = [j.get("description") or ""]
            for lst in j.get("lists") or []:
                parts.append(
                    f"<h3>{html.escape(lst.get('text', ''))}</h3><ul>{lst.get('content', '')}</ul>"
                )
            parts.append(j.get("additional") or "")
            created = j.get("createdAt")
            loc = pick_location(locs, _is_wm)
            if workplace == "remote":
                loc = "UK-remote"
            out.append(
                Vacancy(
                    source="lever",
                    source_id=f"{b['slug']}-{j['id']}",
                    source_tier="A",
                    title=(j.get("text") or "").strip(),
                    url=j.get("hostedUrl"),
                    employer=b["employer"],
                    location_text=loc,
                    description_html="".join(parts),
                    posted_date=datetime.fromtimestamp(created / 1000, UTC).date().isoformat()
                    if created
                    else None,
                    remote_hint=workplace,
                    attribution=f"Posted on {b['employer']}'s Lever job board",
                    extra={"board": b["slug"], "platform": "lever", "country": country},
                )
            )
        return out

    # ----- Workable -----
    def _workable(self, b: dict) -> list[Vacancy]:
        body = self.client.get(
            f"https://www.workable.com/api/accounts/{b['slug']}", params={"details": "true"}
        )
        out = []
        for j in body.get("jobs", []):
            if (j.get("country") or "") not in ("United Kingdom", "UK", "GB"):
                continue
            loc = "UK-remote" if j.get("telecommuting") else (j.get("city") or j.get("state"))
            out.append(
                Vacancy(
                    source="workable",
                    source_id=f"{b['slug']}-{j.get('shortcode')}",
                    source_tier="A",
                    title=(j.get("title") or "").strip(),
                    url=j.get("url") or j.get("shortlink"),
                    employer=b["employer"],
                    location_text=loc,
                    description_html=j.get("description") or "",
                    posted_date=j.get("published_on") or j.get("created_at"),
                    remote_hint="remote" if j.get("telecommuting") else None,
                    attribution=f"Posted on {b['employer']}'s Workable careers page",
                    extra={"board": b["slug"], "platform": "workable"},
                )
            )
        return out
