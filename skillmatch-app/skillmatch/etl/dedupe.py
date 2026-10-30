"""Group duplicate adverts while keeping every link.

1. Exact: the same normalised title, employer and town, even across sources.
2. Near: the same normalised title, and the first 600 characters of the description at least
   90% similar (rapidfuzz token_set_ratio), when the town matches OR the employer matches
   (agencies post one role in several towns; see DECISIONS.md).

Each group gets one primary record (shown as the card) and "also listed by" links.
"""

from __future__ import annotations

import html
import re
from collections import defaultdict

import pandas as pd
from rapidfuzz import fuzz

from skillmatch import config
from skillmatch.text import clean_text

TITLE_NOISE = re.compile(
    r"\b(hybrid|remote|ftc|fixed[- ]term|contract|permanent|temp|temporary|part[- ]time|full[- ]time|"
    r"inside ir35|outside ir35|x\d+|\d+[- ]month|urgent|immediate start|ref\b.*)",
    re.IGNORECASE,
)
EMPLOYER_NOISE = re.compile(r"\b(ltd|limited|plc|llp|uk|group|the)\b\.?", re.IGNORECASE)


def norm_title(title: str, towns: set[str] | None = None) -> str:
    t = html.unescape(clean_text(title)).lower()
    t = re.sub(r"\(.*?\)|\[.*?\]", " ", t)
    # Drop a trailing " - Birmingham" / " | Hybrid" style suffix.
    parts = re.split(r"\s+[-–|/]\s+|\s*,\s*", t)
    if len(parts) > 1 and towns:
        parts = [p for p in parts if p.strip() not in towns] or parts
    t = " ".join(parts)
    t = TITLE_NOISE.sub(" ", t)
    t = re.sub(r"[^a-z0-9& ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def norm_employer(employer: str | None) -> str:
    e = EMPLOYER_NOISE.sub(" ", html.unescape(clean_text(employer)).lower())
    return re.sub(r"[^a-z0-9]+", " ", e).strip()


def norm_town(location: str | None) -> str:
    return re.sub(r"[^a-z]+", " ", clean_text(location).lower()).strip()


class _UnionFind:
    def __init__(self, items):
        self.parent = {i: i for i in items}
        self.reason: dict = {}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b, reason):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra
            self.reason[b] = reason
            self.reason.setdefault(a, reason)


def group_duplicates(df: pd.DataFrame, towns: set[str] | None = None) -> pd.DataFrame:
    """Add duplicate_group and is_primary columns; return the duplicates table as a frame."""
    df["_title"] = [norm_title(t, towns) for t in df["title"]]
    df["_employer"] = [norm_employer(e) for e in df["employer"]]
    df["_town"] = [norm_town(x) for x in df["location_text"]]
    df["_head"] = [
        clean_text(t)[: config.NEAR_DUPLICATE_CHARS].lower() for t in df["description_text"]
    ]

    uf = _UnionFind(df.index)
    # Missing employer/location values are not evidence that same-title adverts match.
    # Keep exact-key matching only when all normalised key fields are present.
    exact_candidates = df[df["_title"].ne("") & df["_employer"].ne("") & df["_town"].ne("")]
    for _, idx in exact_candidates.groupby(["_title", "_employer", "_town"]).groups.items():
        idx = list(idx)
        for other in idx[1:]:
            uf.union(idx[0], other, "exact")

    buckets: dict[tuple, list] = defaultdict(list)
    for i, row in df.iterrows():
        if row["_title"] and row["_town"]:
            buckets[("town", row["_title"], row["_town"])].append(i)
        if row["_title"] and row["_employer"]:
            buckets[("employer", row["_title"], row["_employer"])].append(i)

        # A shared posting URL or substantial identical description can establish a match
        # when employer or location metadata is absent. Short/template descriptions are not
        # strong enough evidence on their own.
        url = str(row.get("url") or row.get("link") or "").strip().rstrip("/")
        if url:
            buckets[("url", url)].append(i)
        if row["_title"] and len(row["_head"].strip()) >= 80:
            buckets[("content", row["_title"], row["_head"])].append(i)
    for key, idx in buckets.items():
        if len(idx) < 2 or len(idx) > 200:
            continue
        for a_pos, a in enumerate(idx):
            for b in idx[a_pos + 1 :]:
                if uf.find(a) == uf.find(b):
                    continue
                if key[0] in {"url", "content"}:
                    uf.union(a, b, "exact")
                    continue
                ha, hb = df.at[a, "_head"], df.at[b, "_head"]
                if ha and hb and fuzz.token_set_ratio(ha, hb) >= config.NEAR_DUPLICATE_RATIO:
                    uf.union(a, b, "near")

    groups: dict = defaultdict(list)
    for i in df.index:
        groups[uf.find(i)].append(i)

    df["duplicate_group"] = None
    df["is_primary"] = 1
    rows = []
    for members in groups.values():
        if len(members) == 1:
            continue
        primary = max(members, key=lambda i: _primary_score(df.loc[i]))
        gid = "g-" + df.at[primary, "vacancy_id"].replace(":", "-")
        for i in members:
            df.at[i, "duplicate_group"] = gid
            df.at[i, "is_primary"] = int(i == primary)
            rows.append(
                {
                    "group_id": gid,
                    "vacancy_id": df.at[i, "vacancy_id"],
                    "primary_id": df.at[primary, "vacancy_id"],
                    "reason": uf.reason.get(i, "exact") if i != primary else "primary",
                }
            )
    df.drop(columns=["_title", "_employer", "_town", "_head"], inplace=True)
    return pd.DataFrame(rows, columns=["group_id", "vacancy_id", "primary_id", "reason"])


def _source_preference(row) -> int:
    """Lower is preferred: employer-hosted listings, Reed, boards, then agencies."""
    source = str(row.get("source", "")).lower()
    extra = row.get("extra")
    if isinstance(extra, str):
        try:
            import json

            extra = json.loads(extra)
        except (ValueError, TypeError):
            extra = {}
    extra = extra if isinstance(extra, dict) else {}
    platform = str(extra.get("platform", "")).lower()
    if source in {"greenhouse", "lever", "workable"} or platform in {
        "greenhouse",
        "lever",
        "workable",
    }:
        return 4
    if "reed" in source:
        return 3
    if source in {
        "we_work_remotely",
        "remote_ok",
        "cv_library",
        "cvlibrary",
        "totaljobs",
        "cwjobs",
        "jobsite",
        "wmjobs",
        "nhs_jobs",
        "jobs_ac_uk",
    } or platform in {"stepstone", "board"}:
        return 2
    # Explicitly scraped employer career sites are direct sources; other named adapters are
    # treated as agencies unless their metadata identifies a board.
    if extra.get("direct_source") or extra.get("source_kind") == "direct" or "direct" in source:
        return 4
    return 1


def _primary_score(row) -> tuple:
    excluded = row.get("excluded_reason")
    eligible = excluded is None or (isinstance(excluded, float) and pd.isna(excluded))
    fields = (
        "title",
        "employer",
        "location_text",
        "description_text",
        "link",
        "salary_min",
        "salary_max",
        "posted_date",
    )
    populated = sum(bool(row.get(name)) and not pd.isna(row.get(name)) for name in fields)
    description_length = len(str(row.get("description_text") or ""))
    return (
        eligible,
        _source_preference(row),
        populated,
        description_length,
        bool(row.get("salary_stated")),
        int(row.get("n_requirements") or 0),
        row.get("posted_date") or "",
        row["vacancy_id"],
    )
