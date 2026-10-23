"""Filters that decide which adverts are shown by default. Nothing is ever deleted: an excluded
advert keeps an `excluded_reason` and can be revealed in the results.

- Title filter (data/title_rules.csv), applied to the TITLE only: senior words exclude, entry
  words boost. "Senior stakeholders" in a description never excludes anything.
- Relevance filter: is this actually a data job?
- Training-course filter: paid courses advertised as "Trainee Data Analyst" jobs.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from functools import lru_cache

from skillmatch import config
from skillmatch.taxonomy import Taxonomy, get_taxonomy

NOT_A_DATA_ROLE = "not a data role"
TRAINING_COURSE = "training course, not a job"
OUT_OF_REGION = "outside the West Midlands"
EXPIRED = "expired"

# Title words that make a job a data role on their own.
DATA_TITLE = re.compile(
    r"\b(data|databases?|insights?|bi|business intelligence|mi|management information|reporting|"
    r"information|research|evaluation|crm|analytics|intelligence|statistic(?:s|al|ian)?|"
    r"power\s?bi|sql|dashboards?)\b",
    re.IGNORECASE,
)
# Titles that are not data roles even with a data word in them (calibrated on the live sample:
# "Information Security Analyst", "Management Reporting Accountant", "BD Executive (Data)").
NOT_DATA_TITLE = re.compile(
    r"\b(security|cyber|accountant|accounting|solicitor|sales|business development|bd|"
    r"r\s*&\s*d|research\s*(?:&|and)\s*development|information assurance|recruit\w*)\b",
    re.IGNORECASE,
)
# "<something> Analyst" is a data role unless the something marks a different field.
ANALYST = re.compile(r"\b(analyst|analytics|analysis)\b", re.IGNORECASE)
NOT_DATA_ANALYST = re.compile(
    r"\b(financ\w*|fp\s*&\s*a|business|soc|security|cyber|support|service desk|it|systems?|network|"
    r"qc|tax|billing|accounts?|test\w*|infrastructure|application|actuarial|credit|treasury|"
    r"surveyor|technology operations|edi|payroll|hris|bom|feature configuration|revenue|sap|"
    r"integration|pmo|threat|detection|drilling)\b",
    re.IGNORECASE,
)
# Job families whose adverts mention data tools without being data jobs.
ENGINEERING_TITLE = re.compile(
    r"\b(engineer|developer|programmer|architect|designer|technician|merchandiser|buyer|"
    r"estimator|planner|administrator|assistant|consultant)\b",
    re.IGNORECASE,
)
# Skills too generic to make a role "data" by themselves (most office jobs mention them).
GENERIC_SKILLS = {"excel", "microsoft_office", "google_sheets", "erp_systems", "hr_systems"}

TRAINING_PATTERNS = re.compile(
    r"(job guarantee|money[- ]back guarantee|study fees|course fees|career programme|"
    r"career program\b|our programme includes|finance terms|recruitment support until placed|"
    r"we support you into employment|enquire now|training package|pay for (the|your) course)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TitleRule:
    word: str
    action: str  # exclude | boost
    pattern: re.Pattern


@lru_cache(maxsize=1)
def title_rules() -> tuple[TitleRule, ...]:
    with (config.DATA_DIR / "title_rules.csv").open() as f:
        return tuple(
            TitleRule(r["word"], r["action"], re.compile(r["pattern"], re.IGNORECASE))
            for r in csv.DictReader(f)
        )


@dataclass
class TitleVerdict:
    excluded_by: str | None = None  # the first exclude word found
    boosted_by: list[str] = field(default_factory=list)


def check_title(title: str) -> TitleVerdict:
    v = TitleVerdict()
    for rule in title_rules():
        if rule.pattern.search(title or ""):
            if rule.action == "exclude" and v.excluded_by is None:
                v.excluded_by = rule.word
            elif rule.action == "boost":
                v.boosted_by.append(rule.word)
    return v


def is_data_title(title: str) -> bool:
    return bool(DATA_TITLE.search(title or ""))


def technical_signals(text: str, tax: Taxonomy | None = None) -> list[str]:
    """Distinct non-generic technical skills a description mentions."""
    tax = tax or get_taxonomy()
    found = []
    for s in tax.skills.values():
        if s.id in GENERIC_SKILLS:
            continue
        if any(p.search(text or "") for p in s.patterns):
            found.append(s.id)
    return found


def is_data_role(title: str, description_text: str, tax: Taxonomy | None = None) -> bool:
    """Is this actually a data job? (Calibrated rule; see DECISIONS.md.)

    1. A data word in the title (data, insight, BI, MI, reporting, research...) -> yes, unless
       the title also names a non-data field (security, accountant, sales...).
    2. "Analyst" in the title -> yes, unless qualified by a non-data field (finance, business,
       IT support...). Performance, commercial, pricing, planning and operations analysts stay.
    3. Otherwise yes only if the advert asks for at least two non-generic technical data skills
       and the title isn't an engineering, developer or similar job family.
    """
    title = title or ""
    if NOT_DATA_TITLE.search(title):
        return False
    if is_data_title(title):
        return True
    if ANALYST.search(title):
        return not NOT_DATA_ANALYST.search(title)
    if ENGINEERING_TITLE.search(title):
        return False
    return len(technical_signals(description_text, tax)) >= config.RELEVANCE_MIN_SKILLS


def is_training_course(title: str, description_text: str) -> bool:
    hits = set(m.group(0).lower() for m in TRAINING_PATTERNS.finditer(description_text or ""))
    return len(hits) >= 2 or ("no experience" in (title or "").lower() and bool(hits))
