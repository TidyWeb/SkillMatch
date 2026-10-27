import pandas as pd

from skillmatch.etl.dedupe import group_duplicates
from skillmatch.filters import is_training_course, required_professional_qualification


def test_required_qualification_excludes_essential_and_required_wording():
    assert required_professional_qualification(
        "Management Accountant", "You must hold ACCA or CIMA to be considered."
    ).startswith("Required professional qualification: ACCA")
    assert required_professional_qualification(
        "HR Manager", "CIPD Level 5 is essential for this role."
    ).startswith("Required professional qualification: CIPD")


def test_desirable_and_studying_towards_qualifications_are_retained():
    assert required_professional_qualification("Analyst", "ACCA is desirable.") is None
    assert (
        required_professional_qualification(
            "Analyst", "CIMA preferred; studying towards it is welcome."
        )
        is None
    )
    assert (
        required_professional_qualification(
            "HR Adviser", "CIPD required, or studying towards CIPD."
        )
        is None
    )


def test_qualification_headings_and_qualified_wording():
    assert required_professional_qualification(
        "Accountant", "Essential qualifications\nACCA or CIMA"
    )
    assert required_professional_qualification("Accountant", "ACCA qualified accountant")
    assert required_professional_qualification("Accountant", "Qualified ACCA accountant")
    assert (
        required_professional_qualification("Accountant", "Desirable qualifications\nACCA or CIMA")
        is None
    )


def test_explicitly_unrequired_qualification_is_not_excluded():
    assert required_professional_qualification("Analyst", "ACCA not required.") is None
    assert (
        required_professional_qualification("Analyst", "No ACCA qualification is required.") is None
    )
    assert (
        required_professional_qualification(
            "Analyst", "Essential qualifications\nACCA is not required"
        )
        is None
    )


def test_qualification_strength_is_scoped_to_each_credential_clause():
    assert required_professional_qualification(
        "Accountant", "ACCA required, with CIMA desirable."
    ).startswith("Required professional qualification: ACCA")
    assert (
        required_professional_qualification("Accountant", "ACCA essential or studying towards it.")
        is None
    )
    assert (
        required_professional_qualification("Accountant", "ACCA required, or studying towards.")
        is None
    )
    assert (
        required_professional_qualification(
            "Accountant", "ACCA, CIMA or studying towards either is essential."
        )
        is None
    )


def test_placement_training_detection_keeps_paid_apprenticeships():
    assert is_training_course(
        "Data Placement Programme",
        "Our programme includes training. Enquire now about the training package.",
    )
    assert not is_training_course(
        "Data Analyst Apprenticeship",
        "Paid employment with salary, structured on-the-job training and an apprenticeship qualification.",
    )


def _dupes(records):
    df = pd.DataFrame(records)
    table = group_duplicates(df)
    primary = df.loc[df.is_primary == 1, "vacancy_id"].item()
    return primary, table


def _record(vacancy_id, source, *, excluded_reason=None, extra=None, description="SQL reporting"):
    return {
        "vacancy_id": vacancy_id,
        "source": source,
        "source_tier": "A",
        "extra": extra or {},
        "title": "Data Analyst",
        "employer": "Example Ltd",
        "location_text": "Birmingham",
        "description_text": description,
        "link": f"https://example.test/{vacancy_id}",
        "salary_min": None,
        "salary_max": None,
        "salary_stated": False,
        "posted_date": "2026-10-01",
        "n_requirements": 2,
        "excluded_reason": excluded_reason,
    }


def test_duplicate_primary_prefers_eligible_then_direct_source_then_richer_record():
    primary, _ = _dupes(
        [
            _record("reed:1", "reed", description="An extensively detailed full advert " * 20),
            _record("agency:1", "agency", excluded_reason="outside the West Midlands"),
        ]
    )
    assert primary == "reed:1"

    primary, _ = _dupes(
        [
            _record("reed:2", "reed", description="A detailed advert " * 20),
            _record("ats:2", "employer_site", extra={"source_kind": "direct"}, description="Short"),
        ]
    )
    assert primary == "ats:2"

    primary, _ = _dupes(
        [
            _record("reed:3", "reed", description="Short"),
            _record("reed:4", "reed", description="A richer advert with details " * 20),
        ]
    )
    assert primary == "reed:4"
