"""CV-Library affiliate XML jobs feed: a DISABLED stub until the feed URL arrives.

Affiliate ID 107834. The feed URL is pending from CV-Library's partner team and goes in the
CVLIBRARY_FEED_URL environment variable. The affiliate terms page
(https://www.cv-library.co.uk/aff-terms-conditions.html) returned 403 to our checks, so these
conditions come from the build brief and the team's research notes, not a reading of the terms:

- refresh the feed at least every 24 hours (the nightly workflow does);
- display CV-Library's title, salary, company and location unaltered. We keep them in
  `extra["cvlibrary_display"]` and show those, keeping our parsed fields separate;
- every click goes to the job on cv-library.co.uk;
- don't push the jobs to LinkedIn, Indeed, Google for Jobs or DWP. SkillMatch publishes no
  structured job markup and no outbound feed.

The feed schema is not yet known, so the parser below reads common element names tolerantly.
It is untested against a real feed.
"""

from __future__ import annotations

import logging
import os
import xml.etree.ElementTree as ET

from skillmatch.sources.base import Vacancy

log = logging.getLogger(__name__)
AFFILIATE_ID = "107834"
REGISTER_URL = f"https://www.cv-library.co.uk/register?id={AFFILIATE_ID}"


def _first(el: ET.Element, *names: str) -> str | None:
    for n in names:
        found = el.find(n)
        if found is not None and (found.text or "").strip():
            return found.text.strip()
    return None


class CVLibraryAdapter:
    name = "cv_library"
    tier = "A"

    def __init__(self, client=None, feed_url: str | None = None):
        self.feed_url = (
            feed_url if feed_url is not None else os.environ.get("CVLIBRARY_FEED_URL", "")
        )
        self.client = client
        self.stats: dict[str, int] = {}

    @property
    def enabled(self) -> bool:
        return bool(self.feed_url)

    def fetch(self) -> list[Vacancy]:
        if not self.enabled:
            log.info("CV-Library disabled: CVLIBRARY_FEED_URL not set")
            return []
        from skillmatch.sources.http import PoliteClient  # ETL-only dependency

        client = self.client or PoliteClient()
        root = ET.fromstring(client.get(self.feed_url, as_json=False))
        out = []
        for job in root.iter("job"):
            title = _first(job, "title", "jobtitle")
            url = _first(job, "url", "link", "joburl")
            if not title or not url:
                continue
            display = {
                "title": title,
                "salary": _first(job, "salary"),
                "company": _first(job, "company", "employer"),
                "location": _first(job, "location", "town"),
            }
            out.append(
                Vacancy(
                    source="cv_library",
                    source_id=_first(job, "id", "jobid", "reference") or url,
                    source_tier="A",
                    title=title,
                    url=url,
                    employer=display["company"],
                    location_text=display["location"],
                    description_html=_first(job, "description", "jobdescription"),
                    salary_text=display["salary"],
                    attribution="Job from CV-Library",
                    extra={"cvlibrary_display": display},
                )
            )
        self.stats = {"kept": len(out)}
        return out
