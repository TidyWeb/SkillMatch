"""The normalised vacancy record every adapter returns, and the adapter interface."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from skillmatch.text import clean_text, normalize_record


@dataclass
class Vacancy:
    source: str  # adapter id, e.g. "reed", "greenhouse", "fixture"
    source_id: str  # the provider's own id for the advert
    source_tier: str  # "A" automated, "B" curated, "fixture"
    title: str
    url: str  # where the user goes to read and apply
    employer: str | None = None
    location_text: str | None = None
    description_html: str | None = None
    description_text: str | None = None
    description_coverage: str = "full"  # full | search excerpt only | unavailable
    salary_min: float | None = None
    salary_max: float | None = None
    salary_period: str | None = None  # annum | day | hour | week | month
    salary_text: str | None = None  # as stated by the source
    currency: str | None = None
    contract_type: str | None = None  # permanent | contract | temporary
    job_type: str | None = None  # full_time | part_time
    posted_date: str | None = None  # ISO date
    expiration_date: str | None = None  # ISO date
    postcode: str | None = None
    lat: float | None = None
    lon: float | None = None
    remote_hint: str | None = None  # what the source itself says about remote work
    attribution: str = ""
    fetched_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not (clean_text(self.description_html) or clean_text(self.description_text)):
            self.description_coverage = "unavailable"

    @property
    def vacancy_id(self) -> str:
        return f"{self.source}:{self.source_id}"

    def to_dict(self) -> dict:
        d = normalize_record(asdict(self))
        d["vacancy_id"] = self.vacancy_id
        return d


class SourceAdapter(Protocol):
    name: str
    tier: str
    enabled: bool

    def fetch(self) -> list[Vacancy]: ...
