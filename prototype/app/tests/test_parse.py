"""Tricky advert snippets. Many are paraphrased from the live Reed sample (docs/advert_patterns.md)."""

import pytest

from skillmatch.filters import check_title, is_training_course
from skillmatch.parse import (
    DESIRABLE,
    DUTY,
    ESSENTIAL,
    OTHER,
    arrangement_of,
    html_to_lines,
    parse_advert,
    parse_salary,
)


def reqs(html, title="Data Analyst"):
    return {r.text: r for r in parse_advert(html, title).requirements}


def one(html, title="Data Analyst"):
    rs = [r for r in parse_advert(html, title).requirements if r.strength != OTHER]
    assert len(rs) == 1, [r.text for r in rs]
    return rs[0]


# ---------- essential vs desirable vs duty ----------


def test_1_mid_sentence_ideally_stays_essential():
    r = one(
        "<ul><li>Proven experience working in payroll, ideally managing payroll from start to finish.</li></ul>"
    )
    assert (r.strength, r.confidence) == (ESSENTIAL, "stated")


def test_2_desirable_tail_beats_about_you_heading():
    r = one(
        "<p><strong>About you</strong></p><ul><li>Experience within a commercial office environment, "
        "in particular a regulated one, would be desirable</li></ul>"
    )
    assert r.strength == DESIRABLE


def test_3_leading_ideally_is_desirable_and_never_gates():
    p = parse_advert(
        "<ul><li>Ideally 6 months - 2 years of experience in a data analyst role.</li></ul>"
    )
    assert p.requirements[0].strength == DESIRABLE
    assert p.data_years is None


def test_4_duty_cue_without_heading():
    assert (
        one(
            "<p>You will be responsible for producing weekly MI reports for the operations team.</p>"
        ).strength
        == DUTY
    )


def test_5_would_be_advantageous():
    assert one("<p>Experience with SQL would be advantageous.</p>").strength == DESIRABLE


def test_6_specialist_style_heading_and_star_bullets():
    html = "<p><strong>BI Analyst - What will you need?</strong></p><p>* Strong proficiency in SQL.<br />* Practical knowledge of Python</p>"
    rs = reqs(html)
    assert rs["Strong proficiency in SQL."].strength == ESSENTIAL
    assert ("skill", "sql") in rs["Strong proficiency in SQL."].tags
    assert rs["Practical knowledge of Python"].strength == ESSENTIAL


def test_7_duties_section_mentioning_senior_stakeholders():
    html = "<p><strong>Key responsibilities</strong></p><ul><li>Producing management information and performance reports for senior stakeholders.</li></ul>"
    r = one(html)
    assert r.strength == DUTY
    assert ("competency", "reporting_to_leadership") in r.tags


def test_8_senior_stakeholders_is_not_seniority():
    html = "<p><strong>Profile</strong></p><ul><li>Confidence working with cross-functional teams and senior stakeholders.</li></ul>"
    r = one(html, title="Data & Change Analyst")
    assert r.strength == ESSENTIAL
    assert ("competency", "team_leadership") not in r.tags
    assert check_title("Data & Change Analyst").excluded_by is None


# ---------- data-experience demands ----------


def test_9_two_plus_years_as_data_analyst():
    p = parse_advert(
        "<p><strong>Requirements</strong></p><ul><li>2+ years' experience as a data analyst.</li></ul>"
    )
    assert (p.data_years, p.data_years_implied) == (2, False)


def test_10_stakeholder_experience_is_not_data_years():
    p = parse_advert(
        "<p><strong>Requirements</strong></p><ul><li>Experience working with stakeholders across the business.</li>"
        "<li>Experience in a fast-paced environment.</li></ul>"
    )
    assert p.data_years is None


def test_11_number_as_word():
    p = parse_advert(
        "<ul><li>Three years experience as a reporting analyst / BI Developer</li></ul>"
    )
    assert p.data_years == 3


def test_12_five_plus_years_in_bi():
    p = parse_advert(
        "<ul><li>5+ years' experience in BI, Data Analytics, or BI Development.</li></ul>"
    )
    assert p.data_years == 5


def test_13_company_age_and_service_are_not_experience():
    p = parse_advert(
        "<p>For over 110 years we've put our customers at the heart of everything we do.</p>"
        "<p><strong>Benefits</strong></p><ul><li>28 days leave, rising to 30 days with 5 years' service</li></ul>"
        "<p><strong>Requirements</strong></p><ul><li>Strong Excel skills.</li></ul>"
    )
    assert p.data_years is None


def test_14_implied_role_experience():
    p = parse_advert(
        "<p><strong>Essential Experience</strong></p><ul><li>Strong experience working as a Data Analyst, "
        "Data Product Analyst or Data Quality Analyst</li></ul>"
    )
    assert (p.data_years, p.data_years_implied) == (1, True)


def test_15_years_with_a_named_tool():
    p = parse_advert("<p><strong>Essential</strong></p><ul><li>3 years' SQL experience.</li></ul>")
    assert p.data_years == 3


# ---------- degree and entry signals ----------


def test_16_degree_or_equivalent():
    p = parse_advert(
        "<ul><li>Degree qualified - or equivalent - in Supply Chain Management, Business Analytics or Engineering</li></ul>"
    )
    assert p.degree == "or_equivalent"
    assert "or equivalent experience" in p.entry_signals


def test_17_degree_required_despite_preferred_grade_in_brackets():
    p = parse_advert(
        "<p><strong>Requirements</strong></p><ul><li>A degree in Mathematics, Statistics or another numerical "
        "discipline (2:1 or above preferred).</li></ul>"
    )
    assert p.requirements[0].strength == ESSENTIAL
    assert p.degree == "required"


def test_18_entry_signals():
    p = parse_advert(
        "<p>This is an excellent opportunity for someone looking to take their first step into a data career. "
        "No previous experience is necessary and full training will be provided. Career changers welcome.</p>",
        title="Junior Data Officer",
    )
    for s in [
        "junior",
        "first step into a career",
        "no experience necessary",
        "training provided",
        "career changers welcome",
    ]:
        assert s in p.entry_signals


# ---------- salary ----------


def test_19_hidden_salary_is_not_estimated():
    assert parse_salary("Salary: Competitive, plus benefits") is None
    assert parse_salary("Up to 30 days holiday") is None


def test_20_day_rate():
    s = parse_salary("Rate: £450-£550 per day Inside IR35")
    assert (s["salary_min"], s["salary_max"], s["salary_period"]) == (450, 550, "day")


def test_21_hourly_and_k_notation():
    assert parse_salary("£28.53 per hour Umbrella")["salary_period"] == "hour"
    s = parse_salary("£30k - £35k + benefits")
    assert (s["salary_min"], s["salary_max"], s["salary_period"]) == (30000, 35000, "annum")


# ---------- arrangement and office days ----------


@pytest.mark.parametrize(
    "text, arrangement, lo, hi",
    [
        ("Location: Warwickshire / Hybrid (1 day per week onsite)", "hybrid", 1, 1),
        ("Hybrid working model (3 days office, 2 days home)", "hybrid", 3, 3),
        ("Hybrid role with 80% homeworking and 20% in Stratford-upon-Avon", "hybrid", 1, 1),
        (
            "Location: Hybrid working office based in Birmingham – typically 2 days in the office per week",
            "hybrid",
            2,
            2,
        ),
        ("2-3 Days in the office - Birmingham", "hybrid", 2, 3),
        (
            "Predominantly remote - 1x day per quarter in Birmingham or London office",
            "remote",
            0,
            0.25,
        ),
        ("Administration Manager | Birmingham - Fully Office Based | Full Time", "onsite", 5, 5),
        (
            "Comfortable working across initiatives within Agile or hybrid environments",
            "unknown",
            None,
            None,
        ),
    ],
)
def test_22_arrangements(text, arrangement, lo, hi):
    got = arrangement_of(text)
    assert got[:3] == (arrangement, lo, hi)


def test_23_remote_uk_eligibility_unclear():
    p = parse_advert("<p>Remote</p><p>A fully remote data analyst role.</p>")
    assert p.arrangement == "remote" and p.uk_remote == "unclear"


def test_24_remote_uk_only():
    p = parse_advert(
        "<p>Birmingham (remote)</p><p>*Applicants must reside in the UK &amp; have full right to work*</p>"
    )
    assert p.arrangement == "remote" and p.uk_remote == "yes"


# ---------- structure and noise ----------


def test_25_hard_wrapped_lines_are_rejoined():
    html = (
        "<p>What We're Looking For<br />• Strong SQL, Power BI and<br />Excel VBA skills.<br />"
        "• Experience working with large datasets and transforming<br />data into reports and dashboards.</p>"
    )
    texts = [ln.text for ln in html_to_lines(html)]
    assert "Strong SQL, Power BI and Excel VBA skills." in texts
    assert (
        "Experience working with large datasets and transforming data into reports and dashboards."
        in texts
    )


def test_26_mandatory_criteria_inline_heading():
    r = one(
        "<p>MANDATORY CRITERIA: Candidates must have experience working in the automotive industry</p>"
    )
    assert r.strength == ESSENTIAL
    assert ("competency", "sector_manufacturing_logistics") in r.tags


def test_27_benefits_and_boilerplate_are_not_requirements():
    html = (
        "<p><strong>Benefits</strong></p><ul><li>Private medical insurance</li><li>Annual bonus</li></ul>"
        "<p>Robert Walters Operations Limited is an employment business and employment agency and welcomes "
        "applications from all candidates</p>"
    )
    assert all(r.strength == OTHER for r in parse_advert(html).requirements)


def test_28_unclassified_requirement_is_kept():
    r = one("<p><strong>Essential</strong></p><ul><li>A full UK driving licence.</li></ul>")
    assert r.strength == ESSENTIAL and r.tags == []


def test_29_training_course_advert():
    text = (
        "Please note this career program is designed for entry level individuals. Step 1 - CompTIA Data+. "
        "Our money back guarantee: we will refund your study fees. Finance terms of up to 1 year. Enquire now."
    )
    assert is_training_course("Trainee Data Analyst", text)


def test_30_greenhouse_escaped_html():
    lines = html_to_lines(
        "&lt;p&gt;&lt;strong&gt;Requirements&lt;/strong&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;SQL&lt;/li&gt;&lt;/ul&gt;"
    )
    assert [(ln.kind, ln.text) for ln in lines] == [
        ("heading", "Requirements"),
        ("item", "SQL"),
    ] or lines[-1].text == "SQL"


def test_31_inferred_skill_sentence_without_cue():
    r = one("<p>Knowledge of Power BI and DAX.</p>")
    assert (r.strength, r.confidence) == (ESSENTIAL, "inferred")


# ---------- found during calibration on the live snapshot ----------


def test_32_heading_glued_to_previous_line():
    html = "<ul><li>A willingness to learn within a specialist area What's On Offer?</li><li>Salary of circa £32,000</li><li>Company laptop provided</li></ul>"
    p = parse_advert(html)
    by_text = {r.text: r.strength for r in p.requirements}
    assert "A willingness to learn within a specialist area" in by_text
    assert by_text.get("Salary of circa £32,000", OTHER) == OTHER
    assert by_text.get("Company laptop provided", OTHER) == OTHER


def test_33_years_in_a_field_without_the_word_experience():
    p = parse_advert(
        "<p><strong>If You've Got It - We Want It</strong></p><ul><li>8+ years in management consulting or business analytics</li></ul>"
    )
    assert p.data_years == 8


def test_34_repeated_requirements_are_kept_once():
    item = "<li>SQL query writing skills.</li>"
    p = parse_advert(
        f"<p><strong>Key Skills</strong></p><ul>{item}{item}</ul><p><strong>Key Skills</strong></p><ul>{item}</ul>"
    )
    assert sum(1 for r in p.requirements if r.text == "SQL query writing skills.") == 1


def test_36_experience_required_heading():
    r = one("<p>Experience required:</p><ul><li>Strong SQL and Power BI skills.</li></ul>")
    assert (r.strength, r.confidence) == (ESSENTIAL, "stated")


def test_35_data_warehousing_is_not_warehouse_work():
    r = one(
        "<p><strong>Requirements</strong></p><ul><li>Strong SQL and data warehousing skills.</li></ul>"
    )
    assert ("competency", "sector_manufacturing_logistics") not in r.tags
    assert ("skill", "data_warehousing") in r.tags
