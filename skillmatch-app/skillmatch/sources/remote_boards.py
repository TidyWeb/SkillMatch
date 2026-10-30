"""Remote job boards, data and analyst roles only.

- We Work Remotely RSS, https://weworkremotely.com/remote-job-rss-feed: the feed is open to use
  with links attributed back to We Work Remotely. https://weworkremotely.com/remote-jobs.rss
- Remote OK JSON, https://remoteok.com/api: the first element is a legal notice asking API users
  to link back (followed link, no nofollow) to the job's Remote OK URL and to mention Remote OK
  as the source. We do both and never use their logo.

UK eligibility is "unclear" unless the listing states the UK or worldwide eligibility.
"""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime

from skillmatch.sources.base import Vacancy
from skillmatch.sources.http import PoliteClient
from skillmatch.text import repair_mojibake

log = logging.getLogger(__name__)

WORLDWIDE = re.compile(r"\b(anywhere|worldwide|global|any country)\b", re.I)
UK = re.compile(r"\b(united kingdom|uk|great britain|england)\b", re.I)
OVERSEAS = re.compile(
    r"\b(us|usa|u\.s\.a\.|united states|canada|australia|new zealand|india|singapore|ireland|germany|france|netherlands|spain|poland|brazil|mexico|south africa|outside (?:the )?uk)\b",
    re.I,
)


def uk_eligibility(*texts: str | None) -> str:
    joined = " ".join(t for t in texts if t)
    if UK.search(joined) or WORLDWIDE.search(joined):
        return "yes"
    return "no" if OVERSEAS.search(joined) else "unclear"


class WeWorkRemotelyAdapter:
    name = "we_work_remotely"
    tier = "A"
    enabled = True
    FEED = "https://weworkremotely.com/remote-jobs.rss"

    def __init__(self, client: PoliteClient | None = None):
        self.client = client or PoliteClient()
        self.stats: dict[str, int] = {}
        self.source_log: list[dict] = []

    def fetch(self) -> list[Vacancy]:
        xml = self.client.get(self.FEED, as_json=False)
        root = ET.fromstring(xml)
        items = root.findall("./channel/item")
        out = []
        for it in items:
            raw_title = (it.findtext("title") or "").strip()
            company, _, title = raw_title.partition(": ")
            title = title or raw_title
            link = (it.findtext("link") or it.findtext("guid") or "").strip()
            region = it.findtext("region") or ""
            country = it.findtext("country") or ""
            pub = it.findtext("pubDate")
            try:
                posted = parsedate_to_datetime(pub).date().isoformat() if pub else None
            except (TypeError, ValueError):
                posted = None
            out.append(
                Vacancy(
                    source="we_work_remotely",
                    source_id=link.rstrip("/").rsplit("/", 1)[-1] or raw_title,
                    source_tier="A",
                    title=title,
                    url=link,
                    employer=company if title != raw_title else None,
                    location_text="UK-remote"
                    if uk_eligibility(region, country) == "yes"
                    else (f"Remote: {region}; {country}".strip("; ") or "Remote"),
                    description_html=it.findtext("description") or "",
                    posted_date=posted,
                    remote_hint=f"region: {region}; countries: {country}".strip(),
                    attribution="Job via We Work Remotely",
                    extra={"uk_eligibility": uk_eligibility(region, country), "region": region},
                )
            )
        self.stats = {"items": len(items), "kept": len(out)}
        return out


class RemoteOKAdapter:
    name = "remote_ok"
    tier = "A"
    enabled = True
    API = "https://remoteok.com/api"

    def __init__(self, client: PoliteClient | None = None):
        self.client = client or PoliteClient()
        self.stats: dict[str, int] = {}
        self.source_log: list[dict] = []

    def fetch(self) -> list[Vacancy]:
        body = self.client.get(self.API)
        # Also repairs old cache entries, which may already contain Latin-1-decoded UTF-8.
        body = repair_mojibake(body)
        jobs = [j for j in body if isinstance(j, dict) and j.get("id")]
        out = []
        for j in jobs:
            title = (j.get("position") or "").strip()
            tags = " ".join(j.get("tags") or [])
            location = j.get("location") or ""
            epoch = j.get("epoch")
            out.append(
                Vacancy(
                    source="remote_ok",
                    source_id=str(j["id"]),
                    source_tier="A",
                    title=title,
                    url=j.get("url") or f"https://remoteok.com/remote-jobs/{j['id']}",
                    employer=j.get("company"),
                    location_text="UK-remote"
                    if uk_eligibility(location) == "yes"
                    else (f"Remote: {location}" if location else "Remote"),
                    description_html=j.get("description") or "",
                    # Remote OK salary fields may be platform estimates, so we never show them.
                    posted_date=datetime.fromtimestamp(epoch, UTC).date().isoformat()
                    if epoch
                    else None,
                    remote_hint=f"location: {location}",
                    attribution="Job via Remote OK",
                    extra={"uk_eligibility": uk_eligibility(location), "tags": tags},
                )
            )
        self.stats = {"items": len(jobs), "kept": len(out)}
        return out
