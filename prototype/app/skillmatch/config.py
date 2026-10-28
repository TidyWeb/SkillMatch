"""Paths and tunable thresholds. Everything a reviewer might want to change lives here."""

import os
from pathlib import Path

# The project root holds data/. Installed as a package (as in the container), set SKILLMATCH_ROOT.
ROOT = Path(os.environ.get("SKILLMATCH_ROOT") or Path(__file__).resolve().parent.parent)
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_PATH = PROCESSED_DIR / "skillmatch.db"
FIXTURES_PATH = DATA_DIR / "fixtures" / "vacancies.json"
TAXONOMY_DIR = DATA_DIR / "taxonomy"
REPORTS_DIR = ROOT / "reports"
CACHE_DIR = DATA_DIR / "cache"
TAILOR_PAGE_URL = os.environ.get("TAILOR_PAGE_URL", "").strip()


def load_env() -> None:
    """Load .env from the project root if present. Never logs values."""
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env", override=False)


# ----- Filters -----
# Minimum distinct non-generic technical skills that make an advert a data role when its
# title doesn't say so (relevance filter). Tuned during calibration; see DECISIONS.md.
RELEVANCE_MIN_SKILLS = 2

# ----- ETL -----
NEAR_DUPLICATE_CHARS = 600  # compare the first N characters of descriptions
NEAR_DUPLICATE_RATIO = 90  # rapidfuzz token_set_ratio threshold for near-duplicates
REED_DISTANCE_MILES = 27
REED_MAX_REQUESTS = 1500
# Grid of towns searched on Reed at REED_DISTANCE_MILES so the circles cover the region.
REED_GRID = ["Birmingham", "Shrewsbury", "Stoke-on-Trent", "Worcester", "Warwick"]
REED_BIRMINGHAM_PAGES = 5
REED_DETAIL_RESERVE = 500
# No numeric rate limit is published on Reed's Jobseeker API reference (checked 27 Oct 2026).
# Use at most one request per second and honour 429 retry/backoff responses.
REED_MIN_INTERVAL = 1.0
EVIDENCE_MAX_CHARS = 400  # longest advert sentence we store as evidence
REED_PAGES = 3  # follow up to this many pages of 100 when a search fills a page

# ----- Matching (see skillmatch/match.py) -----
STRONG_MAX_PARTLY = 1  # Strong match allows at most this many partly-met essentials
STRONG_MIN_ESSENTIALS = 2  # fewer clearly essential requirements than this: Good match at most
STRETCH_MIN_GAPS = 2  # essential gaps that make an advert a Stretch
NOT_YET_MIN_GAPS = 3  # essential gaps that make an advert Not yet
DATA_GAP_SMALL = 1  # data-years gap waived when the advert welcomes newcomers
DATA_GAP_STRETCH = 2  # gap up to this many years -> Stretch; more -> Not yet
