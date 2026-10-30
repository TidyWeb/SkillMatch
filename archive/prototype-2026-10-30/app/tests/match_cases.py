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
    # Rebased for default course skills, selected areas as direct evidence, and no data-years gate.
    "A_health_data_officer": [X, X, X, S, X, X],
    "B_junior_bi_2yrs": [S, G, S, G, S, G],
    "C_analyst_3yrs": [G, G, G, G, G, G],
    "D_ops_insight": [N, S, G, N, S, X],
    "E_research_officer": [S, N, N, X, N, X],
    "F_board_reporting": [X, G, S, X, S, G],
    # Sector ticks restored to the lecturer and teacher archetypes now answer education-sector
    # experience directly, so both profiles cross the existing Strong threshold.
    "G_education_data": [S, X, N, G, X, S],
    "H_junior_generic": [S, S, S, S, S, S],
}
