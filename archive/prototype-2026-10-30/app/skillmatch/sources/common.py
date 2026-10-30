"""Helpers shared by adapters."""

import re

from bs4 import BeautifulSoup

DATA_TITLE_HINT = re.compile(
    r"\b(data|analyst|analytics|insights?|bi|business intelligence|mi|reporting|sql|"
    r"power\s?bi|research|evaluation|statistic\w*|information)\b",
    re.IGNORECASE,
)
UK_HINT = re.compile(r"\b(united kingdom|uk|england|great britain|gb)\b", re.IGNORECASE)


def html_to_text(html: str | None) -> str:
    if not html:
        return ""
    return re.sub(r"\s+", " ", BeautifulSoup(html, "html.parser").get_text(" ")).strip()


def pick_location(locations: list[str], is_west_midlands) -> str | None:
    """From several location strings, prefer one in the West Midlands, else the first."""
    cleaned = [loc.strip() for loc in locations if loc and loc.strip()]
    for loc in cleaned:
        if is_west_midlands(loc):
            return loc
    return cleaned[0] if cleaned else None
