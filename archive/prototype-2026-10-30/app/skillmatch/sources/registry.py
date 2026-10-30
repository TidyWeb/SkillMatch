"""What the app says about each source: tier, links to the provider's docs, attribution.

Findings from reading each provider's documentation are in docs/sources.md.
"""

SOURCES = [
    {
        "source_id": "reed",
        "name": "Reed",
        "tier": "A",
        "kind": "Job board API",
        "url": "https://www.reed.co.uk/",
        "docs_url": "https://www.reed.co.uk/developers/jobseeker",
        "attribution": "Jobs from Reed.co.uk",
        "notes": "Official Jobseeker API with a free key. Searched across a grid of West Midlands "
        "towns; full details fetched only for jobs that pass our filters.",
    },
    {
        "source_id": "greenhouse",
        "name": "Employer boards on Greenhouse",
        "tier": "A",
        "kind": "Employer careers boards",
        "url": "https://www.greenhouse.com/",
        "docs_url": "https://docs.greenhouse.io/job-board.html",
        "attribution": "Posted on the employer's Greenhouse job board",
        "notes": "Public Job Board API for named employers (data/employer_boards.csv).",
    },
    {
        "source_id": "lever",
        "name": "Employer boards on Lever",
        "tier": "A",
        "kind": "Employer careers boards",
        "url": "https://www.lever.co/",
        "docs_url": "https://github.com/lever/postings-api",
        "attribution": "Posted on the employer's Lever job board",
        "notes": "Public Postings API for named employers.",
    },
    {
        "source_id": "workable",
        "name": "Employer boards on Workable",
        "tier": "A",
        "kind": "Employer careers boards",
        "url": "https://www.workable.com/",
        "docs_url": "https://help.workable.com/hc/en-us/articles/115012771647-Using-the-Workable-API-to-create-a-careers-page",
        "attribution": "Posted on the employer's Workable careers page",
        "notes": "Published-jobs account endpoint for named employers.",
    },
    {
        "source_id": "we_work_remotely",
        "name": "We Work Remotely",
        "tier": "A",
        "kind": "Remote job board (RSS)",
        "url": "https://weworkremotely.com/",
        "docs_url": "https://weworkremotely.com/remote-job-rss-feed",
        "attribution": "Job via We Work Remotely",
        "notes": "Public RSS feed; links go back to We Work Remotely. Data and analyst titles only.",
    },
    {
        "source_id": "remote_ok",
        "name": "Remote OK",
        "tier": "A",
        "kind": "Remote job board (JSON)",
        "url": "https://remoteok.com/",
        "docs_url": "https://remoteok.com/api",
        "attribution": "Job via Remote OK",
        "notes": "Public JSON feed; we link back to each job on Remote OK and name it as the "
        "source, as its API terms ask. Data and analyst titles only.",
    },
    {
        "source_id": "cv_library",
        "name": "CV-Library",
        "tier": "A",
        "kind": "Job board affiliate feed",
        "url": "https://www.cv-library.co.uk/",
        "docs_url": "https://www.cv-library.co.uk/aff-terms-conditions.html",
        "attribution": "Job from CV-Library",
        "notes": "Disabled until CV-Library's partner team supplies the affiliate feed URL "
        "(affiliate ID 107834).",
    },
    {
        "source_id": "curated",
        "name": "Adverts checked by hand",
        "tier": "B",
        "kind": "Human-curated list",
        "url": None,
        "docs_url": None,
        "attribution": "Checked by a team member",
        "notes": "Adverts from sources with no API, recorded in our own words "
        "(data/curated/adverts.csv). No advert text is copied.",
    },
    {
        "source_id": "discovery",
        "name": "Search links to other sources",
        "tier": "C",
        "kind": "Links only, no data collected",
        "url": None,
        "docs_url": None,
        "attribution": "",
        "notes": "Pre-filled searches on other boards, agencies and employers from the team's "
        "source register (data/discovery_links.csv).",
    },
    {
        "source_id": "fixture",
        "name": "SkillMatch fixtures",
        "tier": "fixture",
        "kind": "Synthetic test adverts",
        "url": None,
        "docs_url": None,
        "attribution": "Synthetic advert for testing (fictional employer)",
        "notes": "Clearly synthetic adverts used when no API keys are set.",
    },
]

LABELS = {
    "reed": "Reed",
    "greenhouse": "Greenhouse",
    "lever": "Lever",
    "workable": "Workable",
    "we_work_remotely": "We Work Remotely",
    "remote_ok": "Remote OK",
    "cv_library": "CV-Library",
}


def source_label(source: str, employer: str | None, listed_by: str | None) -> str:
    """How a card names where the advert came from."""
    if source in ("greenhouse", "lever", "workable"):
        return f"{employer} careers site ({LABELS[source]})"
    if source in ("curated", "fixture"):
        return listed_by or "SkillMatch fixtures"
    return LABELS.get(source, source)
