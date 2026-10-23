"""Eight hand-written adverts and the tier each demo persona should get.

The expected tiers were worked out by hand from the matching rules before the matcher was run.
"""

ADVERTS = {
    "A_health_data_officer": (
        "Data Officer",
        """<p>Our community health service needs a Data Officer. Full training is provided.</p>
        <p><strong>Essential</strong></p>
        <ul><li>Experience of accurate data entry and record keeping.</li>
        <li>Good Excel skills.</li>
        <li>Ability to handle confidential information with discretion.</li>
        <li>Experience of working in a healthcare setting.</li>
        <li>Excellent attention to detail.</li></ul>
        <p><strong>Desirable</strong></p><ul><li>Experience of Power BI would be advantageous.</li></ul>""",
    ),
    "B_junior_bi_2yrs": (
        "Junior BI Analyst",
        """<p><strong>What you'll need</strong></p>
        <ul><li>2+ years' experience as a BI analyst or data analyst.</li>
        <li>Advanced SQL.</li>
        <li>Strong Power BI skills, including DAX.</li></ul>""",
    ),
    "C_analyst_3yrs": (
        "Data Analyst",
        """<p><strong>Requirements</strong></p>
        <ul><li>A minimum of 3 years' experience in a data analyst role.</li>
        <li>Strong SQL and Python.</li></ul>""",
    ),
    "D_ops_insight": (
        "Operations Insight Analyst",
        """<p>A restaurant and retail group needs an Operations Insight Analyst.</p>
        <p><strong>What we're looking for</strong></p>
        <ul><li>Experience of stock control or inventory management.</li>
        <li>Experience of managing budgets or margins.</li>
        <li>Experience monitoring KPIs and acting on them.</li>
        <li>Strong Excel skills.</li>
        <li>Ability to explain figures to site managers and senior leaders.</li></ul>
        <p><strong>Desirable</strong></p><ul><li>Experience of rota or labour planning would be a plus.</li></ul>""",
    ),
    "E_research_officer": (
        "Research Officer",
        """<p><strong>Essential criteria:</strong></p>
        <ul><li>Experience of research design and quantitative research methods.</li>
        <li>Experience of statistical analysis using Python, R or SPSS.</li>
        <li>Strong report-writing skills.</li>
        <li>Ability to communicate findings to non-technical audiences.</li>
        <li>A degree in a social science or related subject, or equivalent experience.</li></ul>
        <p><strong>Desirable criteria:</strong></p>
        <ul><li>Experience of qualitative analysis, for example using NVivo.</li></ul>""",
    ),
    "F_board_reporting": (
        "Board Reporting Analyst",
        """<p><strong>About you</strong></p>
        <ul><li>Experience of reporting to a board or senior leadership team.</li>
        <li>Strong commercial awareness.</li>
        <li>Excellent stakeholder management skills.</li>
        <li>Advanced Excel.</li></ul>
        <p><strong>Desirable</strong></p><ul><li>Power BI.</li></ul>""",
    ),
    "G_education_data": (
        "Education Data Analyst",
        """<p><strong>Essential</strong></p>
        <ul><li>Experience of working in education, for example as a teacher or school data manager.</li>
        <li>Excel and Power BI.</li>
        <li>Ability to explain data clearly to non-technical audiences.</li>
        <li>Experience of training others.</li></ul>
        <p><strong>Desirable</strong></p><ul><li>Knowledge of SQL.</li></ul>""",
    ),
    "H_junior_generic": (
        "Junior Data Analyst",
        """<p>We welcome career changers and provide full training.</p>
        <p><strong>About you</strong></p>
        <ul><li>Some experience of SQL or Python, from study or projects.</li>
        <li>Good Excel skills.</li>
        <li>Excellent attention to detail.</li>
        <li>Clear written and verbal communication.</li>
        <li>1 year of experience in a data or reporting role, or equivalent experience gained through study.</li></ul>""",
    ),
}

S, G, X, N = "strong", "good", "stretch", "not_yet"
PERSONAS = [
    "phd_coventry",
    "chef_wolverhampton",
    "director_solihull",
    "nurse_worcester",
    "retail_telford",
    "teacher_stoke",
]
EXPECTED = {
    # Calibration (milestone 7) enriched the personas with everyday competencies real people in
    # those careers evidence (communication, stakeholders, attention to detail...). Each tier
    # change below was re-derived by hand from the new evidence before updating:
    # A: attention to detail now evidenced -> 2 gaps (confidential data, health sector) = Stretch.
    # E: the nurse now evidences explaining findings to non-technical audiences -> 2 gaps.
    # F: stakeholder management now evidenced; the store manager's commercial awareness is
    #    ticked without evidence -> partly -> Strong.
    # G: the nurse explains data to non-specialists -> only the education-sector gap remains.
    # H: everyone now evidences attention to detail and clear communication -> Strong.
    #                         phd chef dir nurse retail teacher
    "A_health_data_officer": [X, X, X, S, X, X],
    "B_junior_bi_2yrs": [X, X, X, X, X, X],
    "C_analyst_3yrs": [N, N, N, N, N, N],
    "D_ops_insight": [N, S, G, N, S, X],
    "E_research_officer": [S, N, N, X, N, X],
    "F_board_reporting": [X, G, S, X, S, G],
    "G_education_data": [S, X, N, G, X, S],
    "H_junior_generic": [S, S, S, S, S, S],
}

# Lines the "How your background answers this advert" section must contain.
EXPECTED_ANSWERS = {
    ("D_ops_insight", "chef_wolverhampton"): [
        "Requirement: stock, inventory and supply. Your evidence: as a kitchen manager, you ran weekly stock and margin reports for a 40-cover restaurant and cut food waste by 15%.",
    ],
    ("D_ops_insight", "retail_telford"): [
        "Requirement: KPI and performance monitoring. Your evidence: as a store manager, you reviewed weekly sales, conversion, margin and shrinkage KPIs with my area manager.",
    ],
    ("A_health_data_officer", "nurse_worcester"): [
        "Requirement: health and care sector knowledge. Your evidence: as a ward sister, you worked in NHS acute medicine for twelve years.",
    ],
    ("E_research_officer", "phd_coventry"): [
        "Requirement: research design and methods. Your evidence: as a PhD researcher, you designed and ran a three-year mixed-methods study of 1,200 survey respondents and 40 interviews.",
    ],
    ("F_board_reporting", "director_solihull"): [
        "Requirement: reporting to senior leadership. Your evidence: as an operations director (plc board) at director level, you presented the monthly operations dashboard to the plc board and the audit committee.",
    ],
    ("G_education_data", "teacher_stoke"): [
        "Requirement: training and coaching others. Your evidence: as a head of maths, you trained the maths department to use our assessment tracker.",
    ],
    ("D_ops_insight", "director_solihull"): [
        "Requirement: budget and cost control. Your evidence: as an operations director (plc board), you set and held a £60m operating budget and explained variances to the board each month.",
    ],
    ("H_junior_generic", "chef_wolverhampton"): [
        "Requirement: Excel. Your evidence: you rate yourself confident in Excel.",
    ],
}
