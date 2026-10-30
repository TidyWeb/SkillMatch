"""Compare the rebuilt matcher with the recorded original live-data baseline.

Run from the working project root. Does not collect data or modify the database.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from skillmatch.match import TIER_ORDER
from skillmatch.profile import areas_for_competencies, profile_from_dict
from skillmatch.repository import load
from skillmatch.results import build_shortlist
from skillmatch.taxonomy import get_taxonomy


def convert_profile(old, tax):
    """Preserve ticked skills; choose at most five areas to hold the same competencies."""
    wanted = {c for r in old.get("roles", []) for c in r.get("competencies", {})}
    areas, remaining = areas_for_competencies(wanted, tax)
    degree = old.get("qualifications", {}).get("degree", "none")
    profile = {
        k: old[k]
        for k in ["postcode", "travel", "max_miles", "max_office_days", "include_remote"]
        if k in old
    }
    profile.update(
        skills=list(old.get("skills", {})),
        areas=areas,
        highest_qualification={"none": 0, "bachelors": 6, "masters": 7, "phd": 8}[degree],
    )
    return profile, sorted(remaining)


def safe(value):
    return str(value).replace("|", "/").replace("\n", " ")


def stage5_changes(stage4, current):
    """Show this follow-up's changes separately from the original interface baseline."""
    lines = [
        "## Stage 5: changes since 4ab882f (before the tier guard)",
        "",
        "The Stage 4 JSON checkpoint preserves the pre-fix results. Both checkpoints use the unchanged database. Profiles preserve the same original ticks, now including the restored sector mappings.",
        "",
        "| Graduate | Strong | Good | Stretch | Not yet | Changed tiers |",
        "|---|---|---|---|---|---|",
    ]
    summaries = {}
    all_changes = []
    for pid, profile in current["profiles"].items():
        previous = {row["id"]: row for row in stage4["profiles"][pid]["ranking"]}
        after = {row["id"]: row for row in profile["ranking"]}
        before_counts = Counter(row["tier"] for row in previous.values())
        after_counts = Counter(row["tier"] for row in after.values())
        changed = sum(
            row["tier"] != previous[key]["tier"] for key, row in after.items() if key in previous
        )
        summaries[pid] = {
            "before": dict(before_counts),
            "after": dict(after_counts),
            "changed_tiers": changed,
        }
        label = pid.split("_")[0].capitalize()
        values = [f"{before_counts[t]} → {after_counts[t]}" for t in TIER_ORDER]
        lines.append("| " + " | ".join([label, *values, str(changed)]) + " |")
        for job_id, row in after.items():
            old = previous[job_id]
            if old["tier"] == row["tier"]:
                continue
            old_cov = {c["id"]: c for c in old["coverage"]}
            reasons = []
            for c in row["coverage"]:
                before = old_cov.get(c["id"])
                if before and before["status"] != c["status"]:
                    reasons.append(f"{c['sentence']}: {before['status']} → {c['status']}")
            all_changes.append(
                f"| {label} | {job_id} | {old['tier']} → {row['tier']} | {safe('; '.join(reasons) or 'Tag coverage changed; see the full requirement evidence in JSON.')} |"
            )
    lines += [
        "",
        "Requested advert checks:",
        "",
        "| Graduate | Vacancy | Stage 4 → Stage 5 tier | Relevant requirement |",
        "|---|---|---|---|",
    ]
    for pid, profile in current["profiles"].items():
        previous = {row["id"]: row for row in stage4["profiles"][pid]["ranking"]}
        for row in profile["ranking"]:
            if row["id"] not in {
                "reed:57451268",
                "reed:57450270",
                "reed:57479756",
                "reed:57382099",
                "reed:57486191",
            }:
                continue
            checks = [
                c for c in row["coverage"] if c["id"].endswith(("#6", "#26", "#22", "#10", "#23"))
            ]
            text = "; ".join(
                f"{c['sentence']}: {c['status']} ({', '.join(f'{tag[0]}={tag[1]}' for tag in c['tags'])})"
                for c in checks
            )
            lines.append(
                f"| {pid.split('_')[0].capitalize()} | {row['id']} | {previous[row['id']]['tier']} → {row['tier']} | {safe(text)} |"
            )
    lines += [
        "",
        "Before Stage 6, Reed 57451268 remains Strong for all three profiles. Requirement #6 is now partly met and explicitly names missing SQL, data modelling and Azure/Microsoft Fabric skills. The stored parser confidence for #6 is inferred, so it does not count against the tier. The stated Power BI requirement is met, and met inferred requirements supply the existing minimum of two checks for Strong. The existing allowance of one partly met stated essential is unchanged, but that allowance is not the main reason here: #6 is excluded from the negative tier calculation. Reclassifying that sentence as stated is a separate parser decision.",
        "",
        "Every tier change since Stage 4:",
        "",
        "| Graduate | Vacancy | Tier | Requirement changes |",
        "|---|---|---|---|",
        *all_changes,
        "",
    ]
    return lines, summaries


def stage6_changes(previous, current):
    """Log guard evidence once per triggering requirement, with per-profile vacancy counts."""
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    log_name = f"guard_log_{stamp}.csv"
    log_rows = []
    summary = {}
    lines = [
        "## Stage 6b: alternatives and database split",
        "",
        "The separate guard still only caps Strong at Good. An OR list is satisfied by any named alternative; a similar/equivalent/comparable/other tool is satisfied by any selected skill in that taxonomy category. Other requirements remain independent. Desirable wording remains exempt.",
        "",
        "Graduates know databases. Databases do not imply SQL. Schema design and warehousing are not course skills. Retired snapshot tags are reinterpreted in memory; stored evidence is unchanged. Parser classification and matcher tier rules are unchanged.",
        "",
        "Before/after counts below isolate this guard on the current taxonomy: before is the raw matcher tier, after is the guarded tier. The earlier Stage 6 checkpoint is retained separately. Basic database defaults can improve raw matcher tiers without satisfying SQL.",
        "",
        "| Profile | Downgraded vacancies | Strong before → after | Good before → after |",
        "|---|---|---|---|",
    ]
    details = []
    for pid, profile in current["profiles"].items():
        previous_counts = Counter(row["tier"] for row in previous["profiles"][pid]["ranking"])
        old_counts = Counter(
            "strong" if row.get("guard_reason") else row["tier"] for row in profile["ranking"]
        )
        new_counts = Counter(row["tier"] for row in profile["ranking"])
        downgrades = [row for row in profile["ranking"] if row.get("guard_reason")]
        summary[pid] = {
            "downgrades": len(downgrades),
            "previous_stage6": dict(previous_counts),
            "before": dict(old_counts),
            "after": dict(new_counts),
            "vacancies": [
                {"id": row["id"], "title": row["title"], "reason": row["guard_reason"]}
                for row in downgrades
            ],
        }
        lines.append(
            f"| {pid} | {len(downgrades)} | {old_counts['strong']} → {new_counts['strong']} | {old_counts['good']} → {new_counts['good']} |"
        )
        for row in downgrades:
            details.append(
                f"| {pid} | {row['id']} — {safe(row['title'])} | {safe(row['guard_reason'])} |"
            )
            for finding in row["guard_findings"]:
                log_rows.append(
                    {
                        "profile_id": pid,
                        "vacancy_id": row["id"],
                        "title": row["title"],
                        "missing_skills": "; ".join(finding["missing_skills"]),
                        "req_id": finding["req_id"],
                        "requirement_text": finding["requirement_text"],
                        "guard_reason": row["guard_reason"],
                        "original_tier": "strong",
                        "guarded_tier": "good",
                    }
                )
    fields = [
        "profile_id",
        "vacancy_id",
        "title",
        "missing_skills",
        "req_id",
        "requirement_text",
        "guard_reason",
        "original_tier",
        "guarded_tier",
    ]
    with Path("reports", log_name).open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(log_rows)
    lines += [
        "",
        "All downgraded vacancies:",
        "",
        "| Profile | Vacancy | Reason |",
        "|---|---|---|",
        *details,
        "",
        f"Guard evidence: [{log_name}]({log_name}). There is one row per triggering requirement; count distinct profile_id/vacancy_id pairs for vacancy totals. No web request writes this log.",
        "",
    ]
    return lines, summary, log_name


def compare():
    baseline = json.loads(Path("reports/ui_simplification_baseline.json").read_text())
    db = Path(baseline["database"])
    digest = hashlib.sha256(db.read_bytes()).hexdigest()
    if digest != baseline["sha256"]:
        raise RuntimeError("Baseline database changed; comparison refused")
    snap = load(db)
    tax = get_taxonomy()
    detail = {"database": baseline["database"], "sha256": digest, "profiles": {}}
    lines = [
        "# UI simplification: before and after",
        "",
        f"Database: `{baseline['database']}`",
        f"SHA256 unchanged: `{digest}`",
        "",
        "Same three fictional graduates, same database, same travel settings. Results retain the existing order: match tier, then distance and title.",
        "",
        "Conversion keeps each original ticked competency, using up to five areas to hold them. It adds no new expertise ticks. All course skills are now automatic; added technical skills keep their identity but lose their old levels. The retired minimum salary is ignored.",
        "",
        "Ranking changes come from the approved matching rules: ticks now meet requirements; missing skills are gaps without related-skill credit; explicit role, professional, commercial, proven, significant, extensive or years-based technical experience is partly met unless desirable; a missing technical skill prevents a requirement being met even in an alternatives list; the data-years gate is removed. Qualification levels are checked against the advert. A job can move because another job changes tier, even when its own coverage stays the same.",
        "",
        "Full original and new requirement statuses are retained in the companion JSON evidence files. The tables below account for every changed rank; direct changes identify the requirements responsible.",
        "",
    ]
    flags = [
        "The unchanged live snapshot includes a Video Editor vacancy (PlanetScale). Its data-job relevance remains a separate review item; this matching task does not change advert inclusion.",
        "The matcher tier rules are unchanged. Its Strong results are capped at Good by the separate guard when any non-desirable requirement names a missing technical skill, regardless of inferred/stated confidence. Desirable or non-technical gaps can still appear on Strong results.",
    ]
    for pid, before in baseline["profiles"].items():
        raw, lost = convert_profile(before["profile"], tax)
        if lost:
            flags.append(f"{pid}: unmapped competencies {lost}")
        sl = build_shortlist(profile_from_dict(raw), snap)
        ranked = [m for t in TIER_ORDER for m in sl.by_tier[t]]
        old = {r["id"]: (i, r) for i, r in enumerate(before["ranking"], 1)}
        new = {}
        for rank, match in enumerate(ranked, 1):
            coverage = [
                {
                    "id": c.req_id,
                    "sentence": c.sentence,
                    "status": c.status,
                    "strength": c.strength,
                    "tags": [(t.tag_id, t.status) for t in c.tags],
                }
                for c in match.coverage
            ]
            previous = old.get(match.vacancy_id)
            changes = []
            if previous:
                prior = {c["id"]: c for c in previous[1]["coverage"]}
                now = {c["id"]: c for c in coverage}
                for cid, row in now.items():
                    was = prior.get(cid)
                    if was and was["status"] != row["status"]:
                        changes.append(f"{row['sentence']}: {was['status']} → {row['status']}")
                    elif not was:
                        changes.append(f"Added check: {row['sentence']} ({row['status']})")
                for cid, row in prior.items():
                    if cid not in now:
                        changes.append(f"Removed data-job-years check: {row['sentence']}")
                old_reasons = previous[1]["reasons"]
                for reason in old_reasons:
                    if reason not in match.reasons and (
                        "data role" in reason or "years" in reason or "data job" in reason
                    ):
                        changes.append(f"Removed experience gate: {reason}")
            new[match.vacancy_id] = {
                "rank": rank,
                "id": match.vacancy_id,
                "title": match.vacancy["title"],
                "tier": match.tier,
                "distance": match.distance_miles,
                "coverage": coverage,
                "reasons": match.reasons,
                "guard_reason": getattr(match, "guard_reason", None),
                "guard_findings": [
                    asdict(finding) for finding in getattr(match, "guard_findings", [])
                ],
                "direct_changes": changes,
            }
        if set(old) != set(new):
            flags.append(
                f"{pid}: eligible set changed: removed {sorted(set(old) - set(new))}; added {sorted(set(new) - set(old))}"
            )
        detail["profiles"][pid] = {
            "profile": raw,
            "unmapped_competencies": lost,
            "ranking": list(new.values()),
        }
        moved = sum(old.get(k, (None,))[0] != v["rank"] for k, v in new.items())
        changed_tiers = sum(k in old and old[k][1]["tier"] != v["tier"] for k, v in new.items())
        lines += [
            f"## {pid}",
            "",
            f"{len(old)} → {len(new)} eligible results; {changed_tiers} tier changes; {moved} rank changes.",
            "",
            "Areas: " + ", ".join(tax.archetypes[a["id"]].label for a in raw["areas"]) + ".",
            "",
            "| New top 10 | Old rank | Vacancy | Title | Tier before → after |",
            "|---|---|---|---|---|",
        ]
        for row in list(new.values())[:10]:
            prev = old.get(row["id"])
            lines.append(
                f"| {row['rank']} | {prev[0] if prev else 'new'} | {row['id']} | {safe(row['title'])} | {prev[1]['tier'] if prev else '—'} → {row['tier']} |"
            )
        lines += [
            "",
            "All changed ranks or tiers:",
            "",
            "| Vacancy | Rank before → after | Tier before → after | Explanation |",
            "|---|---|---|---|",
        ]
        for key, row in new.items():
            prev = old.get(key)
            if prev and prev[0] == row["rank"] and prev[1]["tier"] == row["tier"]:
                continue
            explanation = (
                "; ".join(row["direct_changes"])
                or "Same coverage; moves as other jobs change tier. Distance/title ordering is unchanged."
            )
            if row.get("guard_reason"):
                explanation += "; " + row["guard_reason"]
            if prev and prev[1]["tier"] == row["tier"]:
                explanation = (
                    "Same tier; other jobs entering/leaving this tier shift the rank. "
                    + explanation
                )
            lines.append(
                f"| {key} | {prev[0] if prev else 'new'} → {row['rank']} | {prev[1]['tier'] if prev else '—'} → {row['tier']} | {safe(explanation)} |"
            )
        lines += [""]
    stage4 = json.loads(Path("reports/ui_simplification_stage4.json").read_text())
    stage5 = json.loads(Path("reports/ui_simplification_stage5.json").read_text())
    stage5_lines, stage5_summary = stage5_changes(stage4, stage5)
    lines += stage5_lines
    detail["stage5_summary"] = stage5_summary
    previous_stage6 = json.loads(Path("reports/ui_simplification_stage6.json").read_text())
    stage6_lines, stage6_summary, log_name = stage6_changes(previous_stage6, detail)
    lines += stage6_lines
    detail["stage6_summary"] = stage6_summary
    detail["guard_log"] = log_name
    lines += ["## Checks and concerns", ""]
    lines += (
        [f"- {f}" for f in flags]
        if flags
        else [
            "- No lost expertise ticks or changed eligible vacancy sets. All rank shifts follow tier changes; distance/title sorting stays the same."
        ]
    )
    lines += [
        "- These are matcher comparisons, not claims that an advert is still accepting applications. No new live collection was run."
    ]
    detail["flags"] = flags
    Path("reports/ui_simplification_after.json").write_text(json.dumps(detail, indent=2))
    Path("reports/ui_simplification_after.md").write_text("\n".join(lines) + "\n")
    print(
        json.dumps(
            {
                "flags": flags,
                "profiles": {pid: len(v["ranking"]) for pid, v in detail["profiles"].items()},
                "guard_downgrades": {
                    pid: info["downgrades"] for pid, info in stage6_summary.items()
                },
                "guard_log": log_name,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    compare()
