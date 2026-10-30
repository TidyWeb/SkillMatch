"""Milestone 7: calibrate the rules on a built database (live snapshot or fixtures).

For each demo persona: the tier spread over every shown advert. Across the snapshot: the share of
requirements left unclassified, what the title, relevance and other filters hid, and N random
persona-advert matches written out in full for a sceptical human read.

Usage: uv run python scripts/calibrate.py [--db data/processed/skillmatch.db] [--sample 20] [--seed 7]
Writes reports/calibration_<mode>_<timestamp>.md (git-ignored) and prints the summary.
"""

import argparse
import random
from collections import Counter
from datetime import UTC, datetime

from skillmatch import config
from skillmatch.match import TIER_ORDER
from skillmatch.profile import personas, profile_from_dict
from skillmatch.repository import load
from skillmatch.results import Filters, build_shortlist


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(config.DB_PATH))
    ap.add_argument("--sample", type=int, default=20)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    snap = load(args.db)
    if snap is None:
        raise SystemExit(f"no database at {args.db}")
    out = [f"# Calibration: {snap.mode} snapshot {snap.meta.get('snapshot_date')}", ""]

    shown = snap.shown
    out += [
        f"Adverts shown by default: {len(shown)} (of {len(snap.vacancies)} in the database).",
        "",
    ]

    # ---- tier spread per persona ----
    out += [
        "## Tier spread per persona (all shown adverts, persona's own remote/office/salary settings)",
        "",
    ]
    out += [
        "| persona | " + " | ".join(TIER_ORDER) + " | hidden by persona filters |",
        "|---" * 6 + "|",
    ]
    all_matches = []
    for pid, data in personas().items():
        profile = profile_from_dict(data)
        sl = build_shortlist(profile, snap, Filters())
        c = Counter(m.tier for m in sl.results)
        own_hidden = {
            k: v
            for k, v in sl.hidden.items()
            if k in ("remote", "too far", "office days", "salary")
        }
        out.append(
            f"| {pid} | " + " | ".join(str(c[t]) for t in TIER_ORDER) + f" | {own_hidden or ''} |"
        )
        all_matches += [(pid, m) for m in sl.results]
    out.append("")

    # ---- unclassified share ----
    counted = [
        r
        for v in shown
        for r in snap.requirements.get(v["vacancy_id"], [])
        if r["strength"] in ("essential", "desirable")
    ]
    untagged = [r for r in counted if not r["tags"]]
    inferred = [r for r in counted if r["confidence"] == "inferred"]
    no_ess = [
        v
        for v in shown
        if not any(
            r["strength"] == "essential" and r["tags"]
            for r in snap.requirements.get(v["vacancy_id"], [])
        )
    ]
    out += [
        "## Requirements",
        "",
        f"- Essential or desirable statements in shown adverts: {len(counted)}",
        f"- Unclassified (no tag): {len(untagged)} ({len(untagged) / max(1, len(counted)):.0%})",
        f"- Inferred: {len(inferred)} ({len(inferred) / max(1, len(counted)):.0%})",
        f"- Adverts with no tagged essential requirement: {len(no_ess)} of {len(shown)}",
        f"- Adverts with a data-experience demand: {sum(1 for v in shown if v['data_years'] is not None)}",
        "",
        "Most common unclassified statements:",
        "",
    ]
    for text, n in Counter(r["evidence_sentence"][:110] for r in untagged).most_common(25):
        out.append(f"- ({n}) {text}")
    out.append("")

    # ---- what the filters hid ----
    out += ["## What the filters hid", ""]
    by_reason: dict[str, list[dict]] = {}
    for v in snap.vacancies.values():
        if v["excluded_reason"] and v["is_primary"]:
            by_reason.setdefault(v["excluded_reason"], []).append(v)
    rnd = random.Random(args.seed)
    for reason, vs in sorted(by_reason.items(), key=lambda x: -len(x[1])):
        out += [f"### {reason} ({len(vs)})", ""]
        for v in rnd.sample(vs, min(15, len(vs))):
            word = f" [{v['title_excluded_word']}]" if v["title_excluded_word"] else ""
            out.append(f"- {v['title']}{word} — {v['employer']}, {v['location_text']}")
        out.append("")
    words = Counter(
        v["title_excluded_word"] for v in snap.vacancies.values() if v["title_excluded_word"]
    )
    out += ["Senior words: " + ", ".join(f"{w} {n}" for w, n in words.most_common()), ""]

    # ---- random matches, end to end ----
    out += [f"## {args.sample} random matches, read end to end", ""]
    for pid, m in rnd.sample(all_matches, min(args.sample, len(all_matches))):
        v = m.vacancy
        out += [
            f"### {pid} × {v['title']} — {v['employer']} ({v['location_text']})",
            "",
            f"**{m.tier_label}** · {m.distance_miles} miles · data gate: {m.data_gate} · {v['url']}",
            "",
            "Reasons: " + " / ".join(m.reasons),
            "",
        ]
        for c in m.coverage:
            tags = ", ".join(f"{t.label}={t.status}" for t in c.tags) or "—"
            out.append(
                f"- [{c.strength[:4]}/{c.confidence[:3]}] **{c.status}** {c.sentence[:150]}  _({tags})_"
            )
        out += ["", "Answers: " + " | ".join(m.top_answers), ""]

    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = config.REPORTS_DIR / f"calibration_{snap.mode}_{ts}.md"
    path.write_text("\n".join(out))
    summary_end = out.index("Most common unclassified statements:")
    print("\n".join(out[:summary_end]))
    print(f"full report: {path}")


if __name__ == "__main__":
    main()
