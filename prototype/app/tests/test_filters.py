import pytest

from skillmatch.filters import check_title, is_data_role, is_training_course


@pytest.mark.parametrize(
    "title, word",
    [
        ("Senior Finance Analyst", "senior"),
        ("Snr MI Analyst", "snr"),
        ("Sr. BI Developer", "sr"),
        ("Lead Data Analyst", "lead"),
        ("Principal Data Scientist", "principal"),
        ("Head of Data", "head of"),
        ("Director of Insight", "director"),
        ("Chief Data Officer", "chief"),
        ("BI Manager", "manager"),
        ("Data Architect", "architect"),
        ("Staff Data Engineer", "staff"),
    ],
)
def test_excluded_titles(title, word):
    assert check_title(title).excluded_by == word


@pytest.mark.parametrize(
    "title, boosts",
    [
        ("Junior Data Analyst", ["junior"]),
        ("Graduate Analyst", ["graduate"]),
        ("Trainee Insight Analyst", ["trainee"]),
        ("Apprentice Data Analyst", ["apprentice"]),
        ("Data Protection Assistant", ["assistant"]),
        ("Associate Analyst", ["associate"]),
        ("Entry Level Data Analyst", ["entry level"]),
        ("Data Analyst Intern", ["intern"]),
        ("Data Placement Student", ["placement"]),
    ],
)
def test_boosted_titles(title, boosts):
    v = check_title(title)
    assert v.excluded_by is None and v.boosted_by == boosts


@pytest.mark.parametrize(
    "title",
    [
        "Analyst - Consulting",
        "Data Analyst",
        "Consultant - Data",
        "Staff Nurse",
        "Reporting Analyst",
    ],
)
def test_neutral_titles_kept(title):
    v = check_title(title)
    assert v.excluded_by is None and v.boosted_by == []


def test_senior_stakeholders_in_title_text_only():
    # Seniority is judged on the title alone.
    assert check_title("Data Analyst").excluded_by is None


def test_relevance_filter():
    assert is_data_role("MI Analyst", "")
    assert is_data_role("Analyst - Consulting", "Strong SQL and Python; Tableau a plus.")
    assert not is_data_role("Finance Analyst", "Month-end journals, budgets and Excel.")
    assert not is_data_role("HR Officer", "HR records in Excel and Microsoft Office.")


@pytest.mark.parametrize(
    "title, description",
    [
        # Real adverts from the 27 Oct 2026 live run that the old skills-in-description route let in.
        ("Video Editor", "PlanetScale runs MySQL and PostgreSQL databases. Use AI tools to edit."),
        ("Scrum Master", "Agile ceremonies; GDPR awareness; data-driven teams."),
        ("Enterprise Account Executive", "Sell our ETL, dbt and database integration products."),
        ("Technical Customer Support", "Use dashboards and Git to resolve tickets."),
        ("DESARROLLADOR FULL STACK", "Python, SQL, GCP, Git and REST APIs."),
    ],
)
def test_skills_in_description_never_make_a_data_role(title, description):
    assert not is_data_role(title, description)


@pytest.mark.parametrize(
    "title",
    [
        "Junior Data Analyst",
        "Insights Partner",
        "Business Intelligence Engineer",
        "Commercial Analyst",
        "Supply Chain Analyst",
        "Reporting Officer",
        "Statistician",
    ],
)
def test_data_titles_still_count_without_a_description(title):
    assert is_data_role(title)


def test_training_course_detection():
    text = "No experience needed! Job guarantee. Our money back guarantee refunds your study fees."
    assert is_training_course("Trainee Data Analyst", text)
    assert not is_training_course("Junior Data Analyst", "Full training provided. Excel needed.")
