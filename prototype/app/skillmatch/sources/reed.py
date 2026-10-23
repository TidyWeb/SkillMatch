"""Reed Jobseeker API adapter (https://www.reed.co.uk/developers/jobseeker).

Basic auth with the API key as username and an empty password. Search returns at most 100
results per call; details return the full HTML description. We search a grid of West Midlands
towns, de-duplicate by Reed job id, let the caller filter on the search results, then fetch
details only for the survivors.
"""

from __future__ import annotations

import html
import logging
import os
import re
from collections.abc import Callable, Iterable
from datetime import date, datetime

from skillmatch.sources.base import Vacancy
from skillmatch.sources.http import PoliteClient, RequestCapReached

log = logging.getLogger(__name__)

API = "https://www.reed.co.uk/api/1.0"
ATTRIBUTION = "Jobs from Reed.co.uk"
POSTCODE = re.compile(r"^([A-Z]{1,2}\d[A-Z\d]?)\s*(\d[A-Z]{2})$")
PERIODS = {
    "per annum": "annum",
    "per day": "day",
    "per hour": "hour",
    "per week": "week",
    "per month": "month",
}


def _postcode(location: str | None) -> str | None:
    """Search rows often carry a full postcode without a space ("B46AR"); normalise it."""
    m = POSTCODE.match((location or "").strip().upper())
    return f"{m.group(1)} {m.group(2)}" if m else None


def _iso(d: str | None) -> str | None:
    """Reed dates are dd/mm/yyyy."""
    if not d:
        return None
    try:
        return datetime.strptime(d, "%d/%m/%Y").date().isoformat()
    except ValueError:
        return None


class ReedAdapter:
    name = "reed"
    tier = "A"

    def __init__(
        self,
        client: PoliteClient | None = None,
        api_key: str | None = None,
        towns: Iterable[str] = (),
        terms: Iterable[str] = (),
        distance_miles: int = 15,
        pages_per_search: int = 1,
        keep: Callable[[dict], bool] | None = None,
        max_details: int | None = None,
        today: date | None = None,
    ):
        self.api_key = api_key if api_key is not None else os.environ.get("REED_API_KEY", "")
        self.client = client or PoliteClient()
        self.towns = list(towns)
        self.terms = list(terms)
        self.distance = distance_miles
        self.pages = pages_per_search
        self.keep = keep or (lambda _r: True)
        self.max_details = max_details
        self.today = today or date.today()
        self.stats: dict[str, int] = {}
        self.search_results: dict[int, dict] = {}

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _get(self, url: str, params: dict | None = None):
        return self.client.get(url, params=params, auth=(self.api_key, ""))

    def search(self) -> dict[int, dict]:
        """Run every term in every town. Returns search results keyed by Reed job id."""
        seen: dict[int, dict] = {}
        calls = 0
        for town in self.towns:
            for term in self.terms:
                for page in range(self.pages):
                    params = {
                        "keywords": term,
                        "locationName": town,
                        "distanceFromLocation": self.distance,
                        "resultsToTake": 100,
                        "resultsToSkip": page * 100,
                    }
                    body = self._get(f"{API}/search", params)
                    calls += 1
                    results = body.get("results", []) if isinstance(body, dict) else []
                    for r in results:
                        r.setdefault("_matched_terms", [])
                        prev = seen.setdefault(r["jobId"], r)
                        if term not in prev["_matched_terms"]:
                            prev["_matched_terms"].append(term)
                    if len(results) < 100:
                        break
        self.stats["search_calls"] = calls
        self.stats["search_unique"] = len(seen)
        self.search_results = seen
        return seen

    def detail(self, job_id: int | str) -> dict | None:
        """Full advert for one job id; None when Reed returns its blank job."""
        d = self._get(f"{API}/jobs/{job_id}")
        return d if d and d.get("jobId") else None

    @staticmethod
    def from_search_row(row: dict) -> Vacancy:
        """A Vacancy from a search row alone (short description, no details call)."""
        lo, hi = row.get("minimumSalary"), row.get("maximumSalary")
        return Vacancy(
            source="reed",
            source_id=str(row["jobId"]),
            source_tier="A",
            title=html.unescape(row.get("jobTitle") or "").strip(),
            url=row.get("jobUrl") or f"https://www.reed.co.uk/jobs/{row['jobId']}",
            employer=html.unescape(row.get("employerName") or "") or None,
            location_text=row.get("locationName"),
            description_html=html.escape(row.get("jobDescription") or ""),
            salary_min=float(lo) if lo else None,
            salary_max=float(hi) if hi else None,
            currency=row.get("currency") if (lo or hi) else None,
            posted_date=_iso(row.get("date")),
            expiration_date=_iso(row.get("expirationDate")),
            postcode=_postcode(row.get("locationName")),
            attribution=ATTRIBUTION,
            extra={"matched_terms": row.get("_matched_terms", []), "search_only": True},
        )

    def fetch(self) -> list[Vacancy]:
        if not self.enabled:
            log.info("Reed disabled: no REED_API_KEY")
            return []
        found = self.search()
        live = {k: r for k, r in found.items() if not self._expired(r.get("expirationDate"))}
        self.stats["expired_in_search"] = len(found) - len(live)
        survivors = [r for r in live.values() if self.keep(r)]
        self.stats["survived_search_filters"] = len(survivors)
        if self.max_details is not None:
            survivors = survivors[: self.max_details]
        out: list[Vacancy] = []
        for r in survivors:
            try:
                detail = self._get(f"{API}/jobs/{r['jobId']}")
            except RequestCapReached:
                log.warning("request cap reached after %d details", len(out))
                self.stats["stopped_at_cap"] = 1
                break
            if not detail or not detail.get("jobId"):
                continue  # Reed returns a blank job when the id no longer matches
            v = self.to_vacancy(detail, r)
            if self._expired(v.expiration_date, iso=True):
                continue
            out.append(v)
        self.stats["details_fetched"] = len(out)
        return out

    def _expired(self, d: str | None, iso: bool = False) -> bool:
        value = d if iso else _iso(d)
        return bool(value) and value < self.today.isoformat()

    @staticmethod
    def to_vacancy(detail: dict, search_row: dict | None = None) -> Vacancy:
        search_row = search_row or {}
        period = PERIODS.get((detail.get("salaryType") or "").lower())
        lo, hi = detail.get("minimumSalary"), detail.get("maximumSalary")
        contract = (detail.get("contractType") or "").lower() or None
        job_type = None
        if detail.get("partTime"):
            job_type = "part_time"
        elif detail.get("fullTime"):
            job_type = "full_time"
        return Vacancy(
            source="reed",
            source_id=str(detail["jobId"]),
            source_tier="A",
            title=html.unescape(detail.get("jobTitle") or "").strip(),
            url=detail.get("jobUrl") or f"https://www.reed.co.uk/jobs/{detail['jobId']}",
            employer=html.unescape(detail.get("employerName") or "") or None,
            location_text=detail.get("locationName"),
            description_html=detail.get("jobDescription"),
            salary_min=float(lo) if lo else None,
            salary_max=float(hi) if hi else None,
            salary_period=period if (lo or hi) else None,
            salary_text=detail.get("salary") if (lo or hi) else None,
            currency=detail.get("currency") if (lo or hi) else None,
            contract_type=contract,
            job_type=job_type,
            posted_date=_iso(detail.get("datePosted")),
            expiration_date=_iso(detail.get("expirationDate")),
            postcode=_postcode(search_row.get("locationName")),
            attribution=ATTRIBUTION,
            extra={
                "employer_id": detail.get("employerId"),
                "external_url": detail.get("externalUrl"),
                "matched_terms": search_row.get("_matched_terms", []),
                "application_count": search_row.get("applications"),
            },
        )
