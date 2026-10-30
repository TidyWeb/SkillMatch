"""Build data/discovery_links.csv (Tier C) from the team's source register.

Tier C collects no data: it builds links the user opens themselves. Where a source's own
example URL in the register shows how its search URL is built, we make a pre-filled template;
otherwise we link to its search page and say so. Templates use:
  {term} {term_slug} {town} {town_slug} {radius}

Usage: uv run python scripts/build_discovery_links.py [path/to/source_register.json]
"""

import csv
import json
import sys
from pathlib import Path

from skillmatch import config

DEFAULT_REGISTER = Path(
    "/home/Phil/C_C/Learn_Python_Data/Working Files/UNIT 4 - HACKATHON/Research/"
    "Vacancy_Sources/source_register.json"
)
# Sources we already collect automatically (Tier A) or exclude.
SKIP = {
    "reed": "Tier A: collected through the Reed API",
    "we-work-remotely": "Tier A: collected from the RSS feed",
    "remote-ok": "Tier A: collected from the JSON feed",
    "gymshark": "Tier A: collected from the Greenhouse board",
    "monzo": "Tier A: collected from the Greenhouse board",
    "kpler": "Tier A: collected from the Lever board",
    "biffa": "Tier A: collected from the Workable board",
    "adzuna": "Excluded: free key is evaluation-only",
    "jooble": "Aggregator API page, not a search page",
}
# (template, supports_radius, how the pattern was derived)
TEMPLATES = {
    "cv-library": (
        "https://www.cv-library.co.uk/{term_slug}-jobs-in-{town_slug}?distance={radius}",
        True,
        "Pattern from the register's example search URL; distance parameter assumed, check it.",
    ),
    "cwjobs": (
        "https://www.cwjobs.co.uk/jobs/{term_slug}/in-{town_slug}",
        False,
        "Pattern from the register's example search URL.",
    ),
    "totaljobs": (
        "https://www.totaljobs.com/jobs/{term_slug}/in-{town_slug}",
        False,
        "Pattern from the register's example search URL.",
    ),
    "jobsite": (
        "https://www.jobsite.co.uk/jobs/{term_slug}/in-{town_slug}",
        False,
        "Pattern from the register's example search URL.",
    ),
    "it-jobs-watch": (
        "https://www.itjobswatch.co.uk/find/{term_title_slug}-jobs-in-{town_title_slug}",
        False,
        "Pattern from the register's example search URL.",
    ),
    "technojobs": (
        "https://www.technojobs.co.uk/{term_slug}-jobs/{town_slug}",
        False,
        "Pattern from the register's example search URL.",
    ),
    "indeed": (
        "https://uk.indeed.com/jobs?q={term}&l={town}&radius={radius}",
        True,
        "Standard q/l/radius query parameters.",
    ),
    "linkedin-jobs": (
        "https://www.linkedin.com/jobs/search/?keywords={term}&location={town}",
        False,
        "Standard keywords/location query parameters.",
    ),
    "hays": (
        "https://www.hays.co.uk/job-search/{term_slug}-jobs-in-{town_slug}-uk",
        False,
        "Pattern from the register's example search URL.",
    ),
    "nhs-jobs": (
        "https://www.jobs.nhs.uk/candidate/search/results?keyword={term}&location={town}&language=en",
        False,
        "Keyword parameter from the register's example URL; location parameter assumed, check it.",
    ),
    "harnham": (
        "https://www.harnham.com/job-search/?_keyword={town}",
        False,
        "Pattern from the register's example search URL (town as keyword).",
    ),
    "bright-network": (
        "https://www.brightnetwork.co.uk/graduate-jobs/technology/in-{town_slug}/",
        False,
        "Pattern from the register's example search URL.",
    ),
    "halfords": (
        "https://careers.pageuppeople.com/806/cw/en/search/?search-keyword={term}",
        False,
        "Keyword parameter from the register's example URL.",
    ),
    "find-a-job-dwp-work-hub": (
        "https://findajob.dwp.gov.uk/search?q={term}&w={town}",
        False,
        "q parameter from the register's example URL; w (where) parameter assumed, check it.",
    ),
    "pertemps": (
        "https://www.pertemps.co.uk/jobs/{term_slug}-jobs",
        False,
        "Pattern from the register's example URL (no location).",
    ),
}


def main() -> None:
    register = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_REGISTER
    sources = json.loads(register.read_text())["sources"]
    rows = []
    for s in sources:
        sid = s["source_id"]
        if sid in SKIP:
            continue
        tmpl, radius, how = TEMPLATES.get(sid, (s["source_url"], False, None))
        notes = (
            how
            or "No safe pre-filled search link: this opens the source's search page; search for data roles near you."
        )
        rows.append(
            {
                "source_id": sid,
                "name": s["name"],
                "type": s["source_type"],
                "url_template": tmpl,
                "supports_radius": str(radius).lower(),
                "prefilled": str(sid in TEMPLATES).lower(),
                "notes": notes,
            }
        )
    out = config.DATA_DIR / "discovery_links.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            ["source_id", "name", "type", "url_template", "supports_radius", "prefilled", "notes"],
        )
        w.writeheader()
        w.writerows(rows)
    print(
        f"wrote {len(rows)} discovery links ({sum(r['prefilled'] == 'true' for r in rows)} pre-filled) to {out}"
    )


if __name__ == "__main__":
    main()
