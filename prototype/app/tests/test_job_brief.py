from urllib.parse import unquote, urlsplit

from skillmatch.job_brief import build_job_brief
from skillmatch.web.cards import safe_http_url


def test_job_brief_uses_source_wording_and_optional_profile_hints():
    vacancy = {
        "title": "Junior Analyst",
        "employer": "Example Ltd",
        "location_text": "Birmingham",
        "salary_text": "£28,000",
        "expiration_date": "14 November 2026",
        "url": "https://example.test/job",
        "degree_text": "A degree in a numerical subject is essential.",
        "data_years_text": "At least one year of experience is preferred.",
    }
    requirements = [
        {"n": 1, "strength": "essential", "evidence_sentence": "Advanced Excel skills are essential."},
        {"n": 2, "strength": "desirable", "evidence_sentence": "Power BI experience is desirable."},
        {"n": 3, "strength": "duty", "evidence_sentence": "Prepare monthly reports."},
    ]
    brief = build_job_brief(vacancy, requirements)
    assert "Essential: Advanced Excel skills are essential." in brief
    assert "Desirable: Power BI experience is desirable." in brief
    assert "Duties: Prepare monthly reports." in brief
    assert "Degree: A degree in a numerical subject is essential." in brief
    assert "Experience: At least one year of experience is preferred." in brief
    assert "SKILLMATCH HINTS" not in brief


def test_job_brief_adds_only_match_status_hints():
    class Coverage:
        strength = "essential"
        status = "partly"
        sentence = "Excel experience is essential."

    class Match:
        coverage = [Coverage()]

    brief = build_job_brief({"title": "Analyst"}, [], Match())
    assert "Excel experience is essential.: partly" in brief
    assert "my profile" not in brief


def test_configured_tailor_url_encodes_entire_brief_in_fragment(client):
    client.application.config["TAILOR_PAGE_URL"] = "https://example.test/tailor?view=brief#old"
    from skillmatch.web.cards import _tailor_url

    with client.application.test_request_context():
        value = _tailor_url("SKILLMATCH JOB BRIEF\nJob: Analyst")
    parts = urlsplit(value)
    assert parts.scheme == "https"
    assert parts.query == "view=brief"
    assert unquote(parts.fragment) == "SKILLMATCH JOB BRIEF\nJob: Analyst"


def test_empty_or_unsafe_tailor_url_falls_back_to_no_link(client):
    from skillmatch.web.cards import _tailor_url

    with client.application.test_request_context():
        client.application.config["TAILOR_PAGE_URL"] = ""
        assert _tailor_url("brief") is None
        client.application.config["TAILOR_PAGE_URL"] = "javascript:alert(1)"
        assert _tailor_url("brief") is None
    assert safe_http_url("https://example.test/a") == "https://example.test/a"
    assert safe_http_url("javascript:alert(1)") is None


def test_card_template_escapes_advert_text(client):
    from flask import render_template_string

    card = {
        "title": "<script>alert(1)</script>",
        "company": "Example",
        "salary_text": "Not stated",
        "match_level": "Good match",
        "detail": {"requirements_met": [{"sentence": "<img src=x onerror=1>", "answers": [], "reasons": []}]},
        "advert_url": "https://example.test/job",
        "tailor_url": None,
        "job_brief": "brief",
    }
    with client.application.test_request_context():
        html = render_template_string(
            '{% from "partials/_match_card.html" import match_card %}{{ match_card(card, 1) }}',
            card=card,
        )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
    assert "<img src=x" not in html


def test_unclassified_essential_requirement_is_preserved(client):
    from types import SimpleNamespace

    from skillmatch.web.cards import build_card

    coverage = SimpleNamespace(
        status="unclassified",
        strength="essential",
        confidence="stated",
        sentence="Applications close on Friday.",
        answers=[],
        gaps=[],
    )
    vacancy = {
        "vacancy_id": "example:1",
        "title": "Analyst",
        "employer": "Example",
        "location_text": "Birmingham",
        "url": "https://example.test/job",
        "salary_min": None,
        "salary_max": None,
        "salary_period": None,
        "salary_text": None,
        "is_remote": False,
    }
    match = SimpleNamespace(
        vacancy=vacancy,
        vacancy_id="example:1",
        tier="strong",
        tier_label="Strong match",
        reasons=[],
        coverage=[coverage],
    )
    with client.application.test_request_context():
        card = build_card(match)
    item = card["detail"]["uncategorised"][0]
    assert item["sentence"] == "Applications close on Friday."
    assert item["strength"] == "essential"
    assert item["confidence"] == "stated"
