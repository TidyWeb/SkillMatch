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

TITLE_NOISE = re.compile(
    r"\b(hybrid|remote|ftc|fixed[- ]term|contract|permanent|temp|temporary|part[- ]time|full[- ]time|"
    r"inside ir35|outside ir35|x\d+|\d+[- ]month|urgent|immediate start|ref\b.*)",
    re.IGNORECASE,
)
EMPLOYER_NOISE = re.compile(r"\b(ltd|limited|plc|llp|uk|group|the)\b\.?", re.IGNORECASE)


def norm_title(title: str, towns: set[str] | None = None) -> str:
    t = html.unescape(title or "").lower()
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
    e = EMPLOYER_NOISE.sub(" ", html.unescape(employer or "").lower())
    return re.sub(r"[^a-z0-9]+", " ", e).strip()


def norm_town(location: str | None) -> str:
    return re.sub(r"[^a-z]+", " ", (location or "").lower()).strip()


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
    df["_head"] = [(t or "")[: config.NEAR_DUPLICATE_CHARS].lower() for t in df["description_text"]]

    uf = _UnionFind(df.index)
    for _, idx in df.groupby(["_title", "_employer", "_town"]).groups.items():
        idx = list(idx)
        for other in idx[1:]:
            uf.union(idx[0], other, "exact")

    buckets: dict[tuple, list] = defaultdict(list)
    for i, row in df.iterrows():
        buckets[("town", row["_title"], row["_town"])].append(i)
        if row["_employer"]:
            buckets[("employer", row["_title"], row["_employer"])].append(i)
    for idx in buckets.values():
        if len(idx) < 2 or len(idx) > 200:
            continue
        for a_pos, a in enumerate(idx):
            for b in idx[a_pos + 1 :]:
                if uf.find(a) == uf.find(b):
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


def _primary_score(row) -> tuple:
    tier_rank = {"A": 3, "B": 2, "fixture": 1}.get(row["source_tier"], 0)
    return (
        row["excluded_reason"] is None or pd.isna(row["excluded_reason"]),
        tier_rank,
        bool(row.get("salary_stated")),
        int(row.get("n_requirements") or 0),
        row.get("posted_date") or "",
        row["vacancy_id"],
    )
