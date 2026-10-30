"""One terminal outcome for each collected observation, independent of app presentation."""

from __future__ import annotations

from collections import Counter

OUTCOMES = (
    "shown",
    "outside area",
    "overseas-only remote",
    "senior",
    "needs professional qualification",
    "training or fake advert",
    "not a data role",
    "expired",
    "duplicate of an advert from another source",
    "duplicate within the same source",
    "other",
)

REASONS = {
    "outside the West Midlands": "outside area",
    "remote role not open to UK applicants": "overseas-only remote",
    "senior role": "senior",
    "training course, not a job": "training or fake advert",
}


def terminal_outcome(row: dict) -> tuple[str, str]:
    reason = row.get("excluded_reason")
    if isinstance(reason, str) and reason:
        mapped = REASONS.get(reason, reason)
        return (mapped, "") if mapped in OUTCOMES else ("other", reason)
    return "shown", ""


def observation_rows(
    records: list[dict], vacancies: list[dict], duplicates: list[dict]
) -> list[dict]:
    """Retain repeated source ids as observations without corrupting stable vacancy keys.

    Duplicate outcomes take precedence over eligibility exclusions. The representative's
    eligibility reason is retained separately, so counts are mutually exclusive.
    """
    by_id = {v["vacancy_id"]: v for v in vacancies}
    primary = {d["vacancy_id"]: d["primary_id"] for d in duplicates}
    seen = set()
    out = []
    for n, original in enumerate(records, 1):
        vid = original["vacancy_id"]
        row = {**by_id[vid]}
        row["observation_id"] = f"obs-{n:08d}"
        row["duplicate_of"] = ""
        row["duplicate_source"] = ""
        row["description_coverage"] = original.get("description_coverage") or "unavailable"
        row["fetched_at"] = original.get("fetched_at") or row.get("fetched_at")
        extra = original.get("extra") or {}
        row["search_term"] = extra.get("search_term", "") if isinstance(extra, dict) else ""
        row["search_location"] = extra.get("search_location", "") if isinstance(extra, dict) else ""
        outcome, note = terminal_outcome(row)
        row["eligibility_reason"] = row.get("excluded_reason") or ""
        if vid in seen:
            outcome = "duplicate within the same source"
            row["duplicate_of"] = vid
            row["duplicate_source"] = row["source"]
        elif not row.get("is_primary", 1):
            kept = primary.get(vid)
            if not kept or kept not in by_id:
                raise ValueError(f"Missing retained duplicate for {vid}")
            source = by_id[kept]["source"]
            outcome = (
                "duplicate within the same source"
                if source == row["source"]
                else "duplicate of an advert from another source"
            )
            row["duplicate_of"], row["duplicate_source"] = kept, source
        row["outcome"], row["outcome_note"] = outcome, note
        seen.add(vid)
        out.append(row)
    return out


def funnel_rows(observations: list[dict], run_id: str, run_date: str) -> list[dict]:
    result = []
    for source in sorted({r["source"] for r in observations} | {"ALL"}):
        subset = (
            observations if source == "ALL" else [r for r in observations if r["source"] == source]
        )
        totals = Counter(r["outcome"] for r in subset)
        if any(k not in OUTCOMES for k in totals):
            raise ValueError("Unrecognised outcome")
        result.append(
            {
                "run_id": run_id,
                "run_date": run_date,
                "source": source,
                "collected": len(subset),
                **{k: totals[k] for k in OUTCOMES},
            }
        )
        if len(subset) != sum(totals.values()):
            raise ValueError(f"Outcome accounting failed for {source}")
    return result
