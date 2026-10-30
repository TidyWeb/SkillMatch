"""Generate data/fixtures/vacancies.json: clearly synthetic adverts for offline use and tests.

Every employer is fictional and every record has source="fixture". The adverts copy the
*shapes* found in the live Reed sample (docs/advert_patterns.md), not any advert's text:
agency header blocks, "What will you need?" lists with plain-text bullets, council-style
essential/desirable criteria, heading-free prose with sentence cues, hard-wrapped lines,
benefits blocks and agency boilerplate.

Usage: uv run python scripts/make_fixtures.py
"""

from __future__ import annotations

import json
from html import escape

from skillmatch import config

AGENCY_FOOTER = (
    "{agency} acts as an employment agency for permanent recruitment and an employment business "
    "for the supply of temporary workers. We welcome applications from all candidates."
)
RIGHT_TO_WORK = "*Applicants must reside in the UK and have full right to work*"


def money(sal):
    if not sal:
        return "Competitive"
    lo, hi, period = sal
    unit = {"annum": "per annum", "day": "per day", "hour": "per hour"}[period]
    fmt = (lambda x: f"£{x:,.0f}") if period == "annum" else (lambda x: f"£{x:,.2f}")
    return f"{fmt(lo)} - {fmt(hi)} {unit}" if hi and hi != lo else f"{fmt(lo)} {unit}"


def ul(items):
    return "<ul>" + "".join(f"<li>{escape(i)}</li>" for i in items) + "</ul>"


def style_agency(a):
    """Agency style: header block, bold headings, <ul> lists, boilerplate."""
    parts = [
        f"<p><strong>{escape(a['title'])}</strong><br />Location: {escape(a['loc_line'])}"
        f"<br />Salary: {escape(money(a.get('salary')))}<br />Contract: {a.get('contract', 'Permanent')}</p>",
        f"<p>{escape(a['intro'])}</p>",
        "<p><strong>Key Responsibilities</strong></p>" + ul(a["duties"]),
        f"<p><strong>{a.get('req_heading', 'What we are looking for')}</strong></p>" + ul(a["ess"]),
    ]
    if a.get("des"):
        parts.append(f"<p><strong>{a.get('des_heading', 'Desirable')}</strong></p>" + ul(a["des"]))
    if a.get("extra"):
        parts.append(f"<p>{escape(a['extra'])}</p>")
    parts.append(
        "<p><strong>What's on offer</strong></p>"
        + ul(a.get("benefits", ["25 days holiday plus bank holidays", "Pension scheme"]))
    )
    parts.append(f"<p>{escape(AGENCY_FOOTER.format(agency=a.get('agency', a['employer'])))}</p>")
    return "".join(parts)


def style_specialist(a):
    """Specialist-recruiter style: short header, 'What will you need?' with '*' bullets in text."""
    t = escape(a["title"])
    lines = "<br />".join(f"* {escape(x)}" for x in a["duties"])
    needs = "<br />".join(f"* {escape(x)}" for x in a["ess"])
    out = (
        f"<p>{t}<br />{escape(a['loc_line'])}<br />{escape(money(a.get('salary')))}<br />"
        f"{a.get('contract', 'Permanent')}</p><p>{escape(a['intro'])}</p>"
        f"<p><strong>{t} - What will you be doing?</strong></p><p>{lines}</p>"
        f"<p><strong>{t} - What will you need?</strong></p><p>{needs}</p>"
    )
    if a.get("des"):
        out += (
            "<p><strong>Nice to have</strong></p><p>"
            + "<br />".join(f"* {escape(x)}" for x in a["des"])
            + "</p>"
        )
    if a.get("extra"):
        out += f"<p>{escape(a['extra'])}</p>"
    out += f"<p>{escape(RIGHT_TO_WORK)}</p>"
    out += f"<p>{escape(AGENCY_FOOTER.format(agency=a.get('agency', a['employer'])))}</p>"
    return out


def style_public(a):
    """Council, NHS-style and charity employers: role/team/offer, essential and desirable criteria."""
    out = (
        f"<p>Job title: {escape(a['title'])}<br />Location: {escape(a['loc_line'])}<br />"
        f"Contract: {a.get('contract', 'Permanent')}<br />Salary: {escape(money(a.get('salary')))}</p>"
        f"<p><strong>The role:</strong></p><p>{escape(a['intro'])}</p>"
        "<p><strong>Your responsibilities:</strong></p>" + ul(a["duties"])
    )
    out += "<p><strong>Our offer to you:</strong></p>" + ul(
        a.get(
            "benefits", ["Local Government Pension Scheme", "26 days' holiday rising with service"]
        )
    )
    out += "<p><strong>What we're looking for:</strong></p>"
    out += "<p>Essential criteria:</p>" + ul(a["ess"])
    if a.get("des"):
        out += "<p>Desirable criteria:</p>" + ul(a["des"])
    if a.get("extra"):
        out += f"<p>{escape(a['extra'])}</p>"
    out += (
        "<p>We value diversity and welcome applications from people of all backgrounds. "
        "Please ensure you have the right to work in the UK.</p>"
    )
    return out


def style_prose(a):
    """No headings at all: classification depends on sentence cues."""
    paras = [escape(a["intro"]), escape(a["loc_line"])]
    paras += [escape(x) for x in a["duties"]]
    paras += [escape(x) for x in a["ess"]]
    paras += [escape(x) for x in a.get("des", [])]
    if a.get("extra"):
        paras.append(escape(a["extra"]))
    paras.append(f"Salary: {escape(money(a.get('salary')))}.")
    return "".join(f"<p>{p}</p>" for p in paras)


def style_wrapped(a):
    """Hard-wrapped lines and '•' bullets inside one paragraph, as some agencies post."""

    def wrap(text, width=58):
        words, line, out = text.split(), "", []
        for w in words:
            if len(line) + len(w) + 1 > width and line:
                out.append(line)
                line = w
            else:
                line = f"{line} {w}".strip()
        out.append(line)
        return out

    lines = [
        f"Title: {a['title']}",
        f"Salary: {money(a.get('salary'))}",
        f"Location: {a['loc_line']}",
    ]
    lines += wrap(a["intro"])
    lines.append("Key Responsibilities")
    for d in a["duties"]:
        lines += wrap("• " + d)
    lines.append("What We're Looking For")
    for e in a["ess"]:
        lines += wrap("• " + e)
    for d in a.get("des", []):
        lines += wrap("• " + d)
    if a.get("extra"):
        lines += wrap(a["extra"])
    return "<p>" + "<br />".join(escape(x) for x in lines) + "</p>"


STYLES = {
    "agency": style_agency,
    "specialist": style_specialist,
    "public": style_public,
    "prose": style_prose,
    "wrapped": style_wrapped,
}

# ---------------------------------------------------------------------------------------------
# Blueprints. Every employer is fictional. "town" is where the job is; "loc_line" is how the
# advert itself describes location and arrangement (patterns from the live sample).
# ---------------------------------------------------------------------------------------------

ADVERTS: list[dict] = [
    # ---------- genuine entry roles ----------
    dict(
        key="jr-da-bham",
        title="Junior Data Analyst",
        employer="Hollowmere Housing Group",
        town="Birmingham",
        loc_line="Birmingham city centre / Hybrid (2 days per week in the office)",
        salary=(27000, 30000, "annum"),
        style="agency",
        agency="Hollowmere Housing Group",
        intro="We are looking for a Junior Data Analyst to join our Performance and Insight team. This is an excellent opportunity for someone looking to take their first step into a data career, and full training will be provided.",
        duties=[
            "Produce weekly and monthly performance reports on repairs, rent collection and tenant satisfaction.",
            "Maintain Power BI dashboards used by housing managers.",
            "Carry out data quality checks on our housing management system and correct errors.",
            "Respond to ad hoc data requests from colleagues across the organisation.",
        ],
        ess=[
            "A good working knowledge of Excel, including pivot tables and lookups.",
            "Some experience of SQL or a willingness to learn it quickly.",
            "Excellent attention to detail and accuracy.",
            "The ability to explain findings clearly to non-technical colleagues.",
            "Good organisational skills and the ability to manage competing deadlines.",
        ],
        des=[
            "Experience using Power BI or a similar BI tool.",
            "Knowledge of the social housing sector would be advantageous.",
        ],
        extra="Career changers are welcome to apply; we value transferable skills from any background.",
    ),
    dict(
        key="data-officer-wolves",
        title="Data Officer",
        employer="Blackbrook Community Trust",
        town="Wolverhampton",
        loc_line="Wolverhampton (office based with occasional home working)",
        salary=(25500, 27000, "annum"),
        style="public",
        intro="The Data Officer will keep our supporter and service-user records accurate and produce the monitoring returns our funders rely on.",
        duties=[
            "Maintain accurate records on our CRM database.",
            "Produce quarterly monitoring and impact reports for funders and trustees.",
            "Carry out regular data cleansing and de-duplication.",
            "Support colleagues to record information consistently.",
        ],
        ess=[
            "Accurate data entry and record keeping.",
            "Good Excel skills.",
            "Ability to handle confidential information with discretion.",
            "Ability to work independently and prioritise a varied workload.",
            "Clear written and verbal communication skills.",
        ],
        des=[
            "Experience of a CRM system such as Salesforce or Raiser's Edge.",
            "Knowledge of the charity or voluntary sector.",
        ],
        extra="We welcome applicants who are new to data roles and will provide training.",
    ),
    dict(
        key="mi-analyst-coventry",
        title="MI Analyst",
        employer="Coppergate Insurance Services",
        town="Coventry",
        loc_line="Coventry / Hybrid (3 days office, 2 days home)",
        salary=(28000, 32000, "annum"),
        style="agency",
        agency="Sparrowhawk Recruitment",
        intro="Our client, a growing insurance services business in Coventry, is looking for an MI Analyst to produce management information for its claims and customer teams.",
        duties=[
            "Produce daily, weekly and monthly MI reports on claims volumes and service levels.",
            "Monitor KPIs and highlight trends to team managers.",
            "Automate existing Excel reports using Power Query and Power BI.",
            "Present findings to senior stakeholders in a clear and concise way.",
        ],
        ess=[
            "Strong Excel skills, including formulas and pivot tables.",
            "Experience producing reports or dashboards.",
            "Confidence presenting information to senior managers.",
            "A methodical approach and excellent attention to detail.",
        ],
        des=[
            "Experience with SQL would be advantageous.",
            "Knowledge of insurance or financial services is desirable but not essential.",
        ],
    ),
    dict(
        key="research-officer-coventry",
        title="Research Officer",
        employer="Arden Policy Institute",
        town="Coventry",
        loc_line="Coventry (hybrid, at least 1 day per week on site)",
        salary=(31000, 34500, "annum"),
        style="public",
        intro="The Research Officer will design and deliver mixed-methods research on regional skills and employment, and turn the results into reports for policy makers.",
        duties=[
            "Design surveys and interview schedules and manage fieldwork.",
            "Analyse quantitative data using Python, R or SPSS.",
            "Write reports and briefings for non-specialist audiences.",
            "Present findings to partners, including senior leaders in local government.",
        ],
        ess=[
            "A degree in a social science or quantitative subject, or equivalent experience.",
            "Experience of research design and quantitative research methods.",
            "Strong report-writing skills.",
            "Ability to communicate findings to non-technical audiences.",
            "Experience of statistical analysis.",
        ],
        des=[
            "Experience of qualitative analysis, for example using NVivo.",
            "A postgraduate research qualification.",
        ],
    ),
    dict(
        key="impact-officer-bham",
        title="Impact and Evaluation Officer",
        employer="Kingsbury Youth Foundation",
        town="Birmingham",
        loc_line="Birmingham (Digbeth) / Hybrid",
        salary=(29000, 31500, "annum"),
        style="public",
        intro="We are looking for an Impact and Evaluation Officer to help us understand and evidence the difference our youth programmes make.",
        duties=[
            "Develop our monitoring and evaluation framework with programme teams.",
            "Design surveys and analyse the results.",
            "Produce the annual impact report for trustees and funders.",
            "Train colleagues to collect data consistently.",
        ],
        ess=[
            "Experience of monitoring and evaluation or research methods.",
            "Confident using Excel to analyse data.",
            "Excellent written communication and report writing.",
            "Ability to build relationships with a wide range of stakeholders.",
        ],
        des=[
            "Experience of working in the charity sector.",
            "Familiarity with Power BI or Tableau would be a plus.",
        ],
        extra="We particularly welcome applications from people with lived experience or from career changers.",
    ),
    dict(
        key="dq-analyst-solihull",
        title="Data Quality Analyst",
        employer="Meriden Motor Group",
        town="Solihull",
        loc_line="Solihull / Hybrid (2 days on site)",
        salary=(30000, 34000, "annum"),
        style="specialist",
        agency="Tanworth Talent",
        intro="An exciting opportunity for a Data Quality Analyst to join a regional dealer group, keeping vehicle, customer and aftersales data accurate across 14 sites.",
        duties=[
            "Running data quality checks and reconciling data from multiple systems.",
            "Investigating and correcting errors with colleagues across sites.",
            "Building simple dashboards to track data quality KPIs.",
            "Documenting data standards and training branch staff.",
        ],
        ess=[
            "Strong Excel skills and experience reconciling data from different sources.",
            "Excellent attention to detail and accuracy.",
            "Ability to work with colleagues at all levels across multiple sites.",
            "Knowledge of SQL.",
        ],
        des=["Experience in the automotive industry.", "Power BI experience."],
    ),
    dict(
        key="crm-data-officer-worcester",
        title="CRM Data Officer",
        employer="Severn Vale Hospice",
        town="Worcester",
        loc_line="Worcester (hybrid working available)",
        salary=(24500, 26500, "annum"),
        style="prose",
        intro="Severn Vale Hospice is looking for a CRM Data Officer to look after our supporter database and help our fundraising team understand who gives and why.",
        duties=[
            "You will be responsible for processing donations and keeping supporter records accurate and up to date.",
            "Day to day you'll produce reports on fundraising income and campaign results.",
        ],
        ess=[
            "You will have strong attention to detail and experience of accurate data entry.",
            "You'll need good Excel skills and the confidence to learn new systems.",
            "You must be able to handle confidential and sensitive information with discretion.",
        ],
        des=[
            "Ideally you will have used a CRM database such as Raiser's Edge or Donorfy.",
            "Experience in a healthcare or charity setting would be advantageous.",
        ],
        extra="Training will be provided and we welcome applicants from all backgrounds.",
    ),
    dict(
        key="apprentice-da-oldbury",
        title="Apprentice Data Analyst",
        employer="Tamside Logistics",
        town="West Bromwich",
        loc_line="West Bromwich (office based)",
        salary=(21000, 21000, "annum"),
        style="agency",
        intro="Join our analytics team as an Apprentice Data Analyst and work towards a Level 4 Data Analyst apprenticeship while earning.",
        duties=[
            "Support the analyst team with daily and weekly operational reporting.",
            "Learn to use SQL, Python and Power BI on real business problems.",
            "Help monitor delivery performance against service levels.",
        ],
        ess=[
            "Minimum of 3 GCSEs at grade 4 or above including maths and English.",
            "A genuine interest in data and a willingness to learn.",
            "Good communication skills.",
            "Accuracy and attention to detail.",
        ],
        des=["Familiar with Excel or Google Sheets.", "An interest in logistics would be a plus."],
        req_heading="Knowledge, skills and abilities",
    ),
    dict(
        key="reporting-analyst-telford",
        title="Reporting Analyst",
        employer="Wrekin Retail Partners",
        town="Telford",
        loc_line="Telford / Hybrid (3 days per week onsite)",
        salary=(28000, 31000, "annum"),
        style="agency",
        agency="Ironbridge Recruitment",
        intro="Our client, a multi-site retail group head-quartered in Telford, needs a Reporting Analyst to own its weekly trading and stock reporting.",
        duties=[
            "Produce the weekly trading pack covering sales, margin and stock across 60 stores.",
            "Monitor store KPIs and flag issues to the regional managers.",
            "Build Power BI dashboards for the commercial team.",
            "Work with store and area managers to understand their reporting needs.",
        ],
        ess=[
            "Experience in a retail environment, either in store or at head office.",
            "Strong Excel skills.",
            "Understanding of KPIs such as sales, margin and stock turn.",
            "Ability to communicate clearly with store teams and senior managers.",
        ],
        des=["Experience with Power BI or SQL would be highly beneficial."],
        extra="This role would suit someone who has managed a store and wants to move into a data role.",
    ),
    dict(
        key="school-data-stoke",
        title="School Data and Exams Officer",
        employer="Potteries Learning Trust",
        town="Stoke-on-Trent",
        loc_line="Stoke-on-Trent (on site, term time plus two weeks)",
        salary=(24000, 26500, "annum"),
        style="public",
        intro="We are looking for a Data and Exams Officer to manage pupil data across our three secondary academies and support leaders to use it well.",
        duties=[
            "Maintain pupil records on the school information management system.",
            "Produce attainment and progress reports for heads of department and senior leaders.",
            "Manage exam entries and results and complete the school census.",
            "Train staff to use data systems.",
        ],
        ess=[
            "Experience of working in a school or education setting.",
            "Strong Excel skills.",
            "Excellent accuracy and attention to detail.",
            "Ability to explain data clearly to teachers and leaders.",
            "Ability to handle confidential information.",
        ],
        des=["Experience of SIMS or Arbor.", "Experience of exams administration."],
    ),
    dict(
        key="clinical-info-worcester",
        title="Information Analyst",
        employer="Three Counties Health Partnership",
        town="Worcester",
        loc_line="Worcester / Hybrid (2 days a week on site)",
        salary=(29000, 33000, "annum"),
        style="public",
        intro="The Information Analyst will produce reports on patient flow, waiting times and clinical quality for operational and clinical teams.",
        duties=[
            "Produce regular reports and dashboards on patient flow and waiting lists.",
            "Validate data from clinical systems and resolve data quality issues.",
            "Respond to information requests from clinicians and managers.",
            "Present findings to senior management meetings.",
        ],
        ess=[
            "Experience of working with healthcare or NHS data.",
            "Good Excel skills.",
            "Knowledge of SQL.",
            "Excellent attention to detail.",
            "Ability to communicate findings to clinical and non-technical audiences.",
        ],
        des=[
            "Experience with Power BI.",
            "Clinical experience or knowledge of patient pathways would be advantageous.",
        ],
    ),
    dict(
        key="bi-analyst-solihull",
        title="BI Analyst",
        employer="Blythe Valley Components",
        town="Solihull",
        loc_line="Solihull (hybrid)",
        salary=(36000, 42000, "annum"),
        style="specialist",
        agency="Tanworth Talent",
        intro="I am currently seeking a BI Analyst for a manufacturing business in Solihull. You'll turn commercial and operational data into insight for the board and senior leadership team.",
        duties=[
            "Building Power BI reports for the board and senior leadership team.",
            "Analysing sales, margin and cost data to support commercial decisions.",
            "Working with finance and operations to define KPIs.",
        ],
        ess=[
            "Strong Power BI skills.",
            "Proficiency in SQL.",
            "Commercial awareness and an understanding of profit and loss.",
            "Confidence presenting to senior stakeholders and the board.",
        ],
        des=["Experience of Python.", "Experience in a manufacturing environment."],
    ),
    dict(
        key="commercial-insight-bham",
        title="Commercial Insight Analyst",
        employer="Aston Cross Brewing Co",
        town="Birmingham",
        loc_line="Birmingham (Jewellery Quarter) / Hybrid (2 days per week in the office)",
        salary=(32000, 36000, "annum"),
        style="agency",
        intro="An opportunity for a Commercial Insight Analyst to help a growing drinks business understand its customers, pricing and margins.",
        duties=[
            "Analyse sales and margin by customer, product and channel.",
            "Produce monthly commercial performance reports for the leadership team.",
            "Support pricing and promotional decisions with analysis.",
            "Present insight to senior stakeholders and the board.",
        ],
        ess=[
            "Strong Excel skills.",
            "Commercial awareness.",
            "Experience presenting to senior stakeholders.",
            "Ability to translate data into actionable recommendations.",
        ],
        des=[
            "Experience with Power BI or Tableau.",
            "Experience in hospitality, retail or consumer goods.",
        ],
        des_heading="Desirable experience",
    ),
    dict(
        key="perf-analyst-dudley",
        title="Performance Analyst",
        employer="Black Country Bus Partnership",
        town="Dudley",
        loc_line="Dudley / Hybrid (3 days per week onsite)",
        salary=(30000, 33000, "annum"),
        style="public",
        intro="We need a Performance Analyst to monitor punctuality, reliability and customer satisfaction across our network.",
        duties=[
            "Produce monthly performance reports for the operations board.",
            "Monitor KPIs and identify trends and root causes.",
            "Build dashboards for depot managers.",
            "Support continuous improvement projects with analysis.",
        ],
        ess=[
            "Experience of KPI and performance monitoring.",
            "Strong Excel skills.",
            "Ability to present findings to senior managers.",
            "Problem-solving skills.",
        ],
        des=["Experience with SQL or Power BI.", "Knowledge of transport or logistics operations."],
    ),
    dict(
        key="supply-data-cannock",
        title="Supply Chain Data Analyst",
        employer="Chase Valley Foods",
        town="Cannock",
        loc_line="Cannock (site based, Monday to Friday)",
        salary=(29000, 32000, "annum"),
        style="wrapped",
        intro="A food manufacturer in Cannock is looking for a Supply Chain Data Analyst to improve stock accuracy, demand planning and waste reporting across its two sites.",
        duties=[
            "Produce daily stock, waste and service-level reports.",
            "Analyse demand and work with planners to improve forecasts.",
            "Reconcile stock data between the warehouse and finance systems.",
        ],
        ess=[
            "Experience of stock control, inventory or supply chain.",
            "Strong Excel skills including lookups and pivot tables.",
            "Ability to work under pressure in a fast-paced environment.",
            "Experience managing budgets or costs would be highly advantageous.",
        ],
        des=["SQL or Power BI experience is a bonus."],
        extra="We are open to candidates from operational backgrounds such as hospitality or warehouse management.",
    ),
    dict(
        key="data-coord-lichfield",
        title="Data Coordinator",
        employer="Lichfield Community Health Hub",
        town="Lichfield",
        loc_line="Lichfield (hybrid, 3 days in the office)",
        salary=None,
        style="prose",
        intro="We are looking for a Data Coordinator to keep our patient records system accurate and support our clinical teams with reporting.",
        duties=[
            "You will be responsible for maintaining patient records and producing weekly activity reports.",
            "Duties include auditing records for completeness and training staff on data standards.",
        ],
        ess=[
            "You must have excellent attention to detail and experience of accurate record keeping.",
            "You will have experience of working in a healthcare setting.",
            "Proven ability to handle confidential information.",
        ],
        des=["Knowledge of SystmOne or EMIS would be advantageous."],
        extra="This role would suit someone with a clinical or administrative background who wants to move into data.",
    ),
    dict(
        key="graduate-analyst-warwick",
        title="Graduate Analyst",
        employer="Avonside Mutual",
        town="Warwick",
        loc_line="Warwick / Hybrid (2 days per week in the office)",
        salary=(28000, 28000, "annum"),
        style="agency",
        intro="Our Graduate Analyst programme is open to graduates and career changers with strong analytical skills.",
        duties=[
            "Analyse customer and policy data to support pricing and product teams.",
            "Produce reports and present findings to managers.",
            "Rotate across teams to learn different analytical techniques.",
        ],
        ess=[
            "A degree, or equivalent experience.",
            "Strong numerical and analytical skills.",
            "Some experience of Python, R or SQL.",
            "Excellent communication skills.",
        ],
        des=["Experience of statistics or hypothesis testing."],
        req_heading="About you",
    ),
    dict(
        key="trainee-insight-leam",
        title="Trainee Insight Analyst",
        employer="Leam Valley Water",
        town="Leamington Spa",
        loc_line="Leamington Spa / Hybrid (1 day per week onsite)",
        salary=(26000, 26000, "annum"),
        style="agency",
        intro="A trainee role for someone with a recent data qualification who wants to learn how insight shapes customer service.",
        duties=[
            "Analyse customer contact and complaint data.",
            "Produce monthly customer insight reports.",
            "Support the customer experience team with surveys and analysis.",
        ],
        ess=[
            "A recent qualification in data analysis or a related field.",
            "Working knowledge of Excel and either Power BI or Tableau.",
            "Experience in a customer-facing role.",
            "Willingness to learn.",
        ],
        des=["Experience of survey design.", "Knowledge of SQL."],
    ),
    dict(
        key="evaluation-assistant-hereford",
        title="Research and Evaluation Assistant",
        employer="Marches Rural Action",
        town="Hereford",
        loc_line="Hereford (hybrid, with travel across Herefordshire)",
        salary=(23500, 25000, "annum"),
        style="public",
        intro="Help us measure the impact of our rural community programmes through surveys, interviews and data analysis.",
        duties=[
            "Collect and analyse survey and monitoring data.",
            "Write short evaluation reports for funders.",
            "Support programme staff to record outcomes consistently.",
        ],
        ess=[
            "Experience of research methods or evaluation.",
            "Good Excel skills.",
            "Clear written communication.",
            "Ability to work independently.",
        ],
        des=["A full UK driving licence.", "Experience in the voluntary sector."],
    ),
    dict(
        key="data-tech-shrewsbury",
        title="Data Technician",
        employer="Salop Utilities Services",
        town="Shrewsbury",
        loc_line="Shrewsbury (office based)",
        salary=(23000, 25000, "annum"),
        style="agency",
        intro="A Data Technician role processing and validating meter data for a regional utilities services firm. No previous industry experience is needed; training is provided.",
        duties=[
            "Process and validate meter readings and consumption data.",
            "Investigate discrepancies and escalate issues.",
            "Maintain accurate records and spreadsheets.",
        ],
        ess=[
            "Strong numerical skills and confidence working with spreadsheets.",
            "Excellent attention to detail.",
            "Ability to follow procedures accurately.",
        ],
        des=["Experience of data validation or reporting would be desirable."],
    ),
    dict(
        key="power-bi-dev-redditch",
        title="Power BI Developer",
        employer="Needlemakers Engineering",
        town="Redditch",
        loc_line="Redditch / Hybrid (2 days on site)",
        salary=(34000, 40000, "annum"),
        style="specialist",
        agency="Arrow Valley Search",
        intro="I am seeking a Power BI Developer for an engineering business in Redditch, building reporting for production and finance teams.",
        duties=[
            "Designing Power BI reports and data models.",
            "Writing DAX measures and SQL queries.",
            "Working with production managers to define KPIs.",
        ],
        ess=[
            "Strong Power BI skills, including DAX.",
            "Strong SQL.",
            "Proven experience in a BI role.",
        ],
        des=["Experience in manufacturing."],
    ),
    dict(
        key="insight-analyst-stratford",
        title="Customer Insight Analyst",
        employer="Avon Bard Hotels",
        town="Stratford-upon-Avon",
        loc_line="Stratford-upon-Avon / Hybrid",
        salary=(27000, 30000, "annum"),
        style="prose",
        intro="Our group of six hotels is looking for a Customer Insight Analyst to understand guest behaviour, reviews and booking patterns.",
        duties=[
            "You will be responsible for analysing booking, revenue and review data.",
            "Day to day you will produce dashboards for hotel general managers.",
        ],
        ess=[
            "You will have strong Excel skills and experience of building reports.",
            "You'll need an understanding of the hospitality industry.",
            "You must be able to present insight to non-technical colleagues.",
        ],
        des=[
            "Ideally you'll have used Power BI or Tableau.",
            "Experience of revenue management would be a plus.",
        ],
    ),
    dict(
        key="ops-data-tamworth",
        title="Operations Data Analyst",
        employer="Drayton Fulfilment",
        town="Tamworth",
        loc_line="Tamworth (site based with shift flexibility)",
        salary=(28000, 30000, "annum"),
        style="agency",
        intro="A busy fulfilment centre near Tamworth needs an Operations Data Analyst to support labour planning and productivity reporting.",
        duties=[
            "Produce productivity and labour planning reports for shift managers.",
            "Analyse throughput, picks per hour and service levels.",
            "Support rota planning with data on demand peaks.",
        ],
        ess=[
            "Experience of a warehouse, logistics or operations environment.",
            "Strong Excel skills.",
            "Experience of scheduling or rota planning.",
            "Ability to work under pressure.",
        ],
        des=["Knowledge of SQL or Power BI."],
    ),
    dict(
        key="data-analyst-nuneaton",
        title="Data Analyst",
        employer="Hinckley Road Distribution",
        town="Nuneaton",
        loc_line="Nuneaton / Hybrid (3 days office)",
        salary=(30000, 35000, "annum"),
        style="specialist",
        agency="Arbury Recruitment",
        intro="An opportunity for a Data Analyst to join a distribution business and improve how it reports on stock and deliveries.",
        duties=[
            "Building reports on stock, deliveries and customer service.",
            "Cleaning and reconciling data from the warehouse management system.",
        ],
        ess=[
            "Experience in SQL.",
            "Power BI or Tableau.",
            "Excellent attention to detail.",
            "Stakeholder management skills.",
        ],
        des=["Python."],
    ),
    dict(
        key="data-assistant-rugby",
        title="Data Assistant",
        employer="Dunsmore Housing",
        town="Rugby",
        loc_line="Rugby (hybrid)",
        salary=(22500, 24000, "annum"),
        style="public",
        intro="Support our housing teams by keeping tenancy and repairs data accurate and producing simple reports.",
        duties=[
            "Update tenancy and repairs records.",
            "Run weekly data checks and fix errors.",
            "Produce simple reports in Excel.",
        ],
        ess=[
            "Accurate data entry.",
            "Basic Excel.",
            "Good customer service skills.",
        ],
        des=["Experience in social housing."],
        extra="No previous data experience is necessary.",
    ),
    dict(
        key="mi-officer-kidderminster",
        title="Management Information Officer",
        employer="Wyre Forest Care Services",
        town="Kidderminster",
        loc_line="Kidderminster (office based)",
        salary=(25000, 27500, "annum"),
        style="public",
        intro="Produce management information on care visits, staffing and quality for our care services.",
        duties=[
            "Produce weekly management information reports for the senior management team.",
            "Monitor care visit times against contracted hours.",
            "Support CQC inspections with data.",
        ],
        ess=[
            "Experience of producing reports in Excel.",
            "Understanding of regulatory compliance.",
            "Ability to handle confidential data.",
        ],
        des=["Experience in health or social care."],
    ),
    dict(
        key="analyst-bromsgrove",
        title="Pricing Analyst",
        employer="Lickey Hills Insurance Brokers",
        town="Bromsgrove",
        loc_line="Bromsgrove / Hybrid (2 days a week in the office)",
        salary=(30000, 34000, "annum"),
        style="agency",
        intro="A broker in Bromsgrove is looking for a Pricing Analyst to monitor rates and margins.",
        duties=["Monitor pricing performance.", "Produce margin reports."],
        ess=[
            "Strong Excel skills.",
            "Experience of SQL.",
            "Statistical analysis skills.",
            "Commercial awareness.",
        ],
        des=["Insurance sector experience."],
    ),
    dict(
        key="data-officer-droitwich",
        title="Data and Systems Officer",
        employer="Salwarpe Valley Council Services",
        town="Droitwich",
        loc_line="Droitwich Spa (hybrid)",
        salary=(26500, 28500, "annum"),
        style="public",
        intro="Maintain our case management system and produce performance reports for council services.",
        duties=[
            "Administer the case management system.",
            "Produce monthly performance reports.",
            "Train users and write user guides.",
        ],
        ess=[
            "Experience of maintaining records on a database or case management system.",
            "Good Excel skills.",
            "Ability to train others.",
        ],
        des=["Experience of local government."],
    ),
    dict(
        key="data-analyst-stafford",
        title="Data Analyst",
        employer="Sow Valley County Services",
        town="Stafford",
        loc_line="Stafford (hybrid, at least 1 day per week)",
        salary=(31000, 34800, "annum"),
        style="public",
        intro="Join our corporate insight team analysing data on adult social care, children's services and highways.",
        duties=[
            "Analyse service data and produce reports for directors.",
            "Build dashboards in Power BI.",
            "Support statutory returns.",
        ],
        ess=[
            "Experience of data analysis.",
            "Knowledge of SQL and Power BI.",
            "Ability to communicate findings to non-technical audiences.",
            "Understanding of data protection and GDPR.",
        ],
        des=["Experience in the public sector."],
    ),
    dict(
        key="data-analyst-walsall",
        title="Data Analyst",
        employer="Walsall Metals Recycling",
        town="Walsall",
        loc_line="Walsall (office based)",
        salary=(28000, 32000, "annum"),
        style="wrapped",
        intro="A metals recycling business in Walsall needs a Data Analyst to report on tonnages, prices and site performance across four yards.",
        duties=[
            "Report on tonnages and margins by site.",
            "Track KPIs and present them to the directors.",
            "Improve reporting processes.",
        ],
        ess=[
            "Strong Excel skills.",
            "Experience of KPI reporting across multiple sites.",
            "Commercial awareness.",
        ],
        des=["Power BI would be a plus."],
    ),
    dict(
        key="data-analyst-sutton",
        title="Data Analyst",
        employer="Four Oaks Wealth",
        town="Sutton Coldfield",
        loc_line="Sutton Coldfield / Hybrid (2 days per week in the office)",
        salary=(32000, 36000, "annum"),
        style="agency",
        intro="A wealth management firm in Sutton Coldfield needs a Data Analyst to improve client and regulatory reporting.",
        duties=[
            "Build client and regulatory reports.",
            "Maintain data quality in the client database.",
        ],
        ess=[
            "Experience with SQL.",
            "Excellent attention to detail.",
            "Understanding of regulatory compliance.",
        ],
        des=["Financial services experience."],
    ),
    # ---------- "junior" titles demanding 2+ years in data ----------
    dict(
        key="jr-bi-2yrs-bham",
        title="Junior BI Analyst",
        employer="Selly Oak Software",
        town="Birmingham",
        loc_line="Birmingham / Hybrid (3 days per week onsite)",
        salary=(30000, 35000, "annum"),
        style="specialist",
        agency="Edgbaston Data Search",
        intro="A junior role in name, but you will need solid hands-on BI experience to hit the ground running.",
        duties=["Building and maintaining Power BI reports.", "Writing SQL to extract data."],
        ess=[
            "2+ years' experience as a data analyst or BI analyst.",
            "Advanced SQL.",
            "Strong Power BI skills including DAX.",
        ],
        des=["Azure Data Factory experience."],
    ),
    dict(
        key="jr-da-3yrs-coventry",
        title="Junior Data Analyst",
        employer="Canley Engineering Data",
        town="Coventry",
        loc_line="Coventry / Fully office based",
        salary=(28000, 32000, "annum"),
        style="agency",
        intro="We're looking for a Junior Data Analyst to join our engineering data team.",
        duties=["Analyse test data.", "Produce reports for engineers."],
        ess=[
            "A minimum of 3 years' experience in a data analyst role.",
            "Python and SQL.",
            "Experience in the automotive industry is essential.",
        ],
        des=["Tableau."],
    ),
    dict(
        key="jr-mi-2yrs-wolves",
        title="Junior MI Analyst",
        employer="Molineux Finance",
        town="Wolverhampton",
        loc_line="Wolverhampton / Hybrid (2 days in the office)",
        salary=(26000, 29000, "annum"),
        style="prose",
        intro="We're hiring a Junior MI Analyst for our collections team.",
        duties=["You will be responsible for daily collections MI and KPI reporting."],
        ess=[
            "You will have at least two years' experience in an MI or reporting role.",
            "You must have advanced Excel skills including VBA.",
            "Experience in financial services is essential.",
        ],
        des=["SQL would be advantageous."],
    ),
    dict(
        key="jr-da-1yr-equiv-telford",
        title="Junior Data Analyst",
        employer="Hadley Park Logistics",
        town="Telford",
        loc_line="Telford / Hybrid (2 days on site)",
        salary=(25000, 28000, "annum"),
        style="agency",
        intro="An entry-level opportunity in our planning team. Training provided.",
        duties=[
            "Support the planning team with daily reports.",
            "Maintain stock and delivery data.",
        ],
        ess=[
            "1 year of experience in a data or reporting role, or equivalent experience gained through study or projects.",
            "Good Excel skills.",
            "Attention to detail.",
        ],
        des=["Knowledge of SQL or Python."],
    ),
    dict(
        key="jr-analyst-2yrs-equiv-leam",
        title="Junior Analyst",
        employer="Warwick Lane Analytics",
        town="Leamington Spa",
        loc_line="Leamington Spa / Hybrid (3 days office, 2 days home)",
        salary=(27000, 30000, "annum"),
        style="specialist",
        agency="Royal Spa Recruitment",
        intro="A junior analyst role in a small consultancy working with public sector clients.",
        duties=["Analysing survey data.", "Writing client reports."],
        ess=[
            "Ideally 1-2 years' experience in an analytical role, or equivalent experience.",
            "Excel and either Python or R.",
            "Strong report writing.",
        ],
        des=["Experience of the public sector."],
    ),
    # ---------- roles asking for transferable experience ----------
    dict(
        key="ops-insight-wolves",
        title="Operations Insight Analyst",
        employer="Wulfrun Restaurants Group",
        town="Wolverhampton",
        loc_line="Wolverhampton / Hybrid (2 days per week at head office)",
        salary=(28000, 31000, "annum"),
        style="agency",
        intro="A restaurant group with 22 sites is looking for an Operations Insight Analyst. We are particularly interested in people who have run kitchens or restaurants and now have data skills.",
        duties=[
            "Produce weekly reports on sales, food cost, waste and labour cost by site.",
            "Monitor stock and margin KPIs and flag issues to area managers.",
            "Support rota planning with sales forecasts.",
            "Present findings to the operations director.",
        ],
        ess=[
            "Experience of stock control and food cost in a hospitality setting.",
            "Experience of managing budgets or margins.",
            "Good Excel skills.",
            "Ability to communicate with site managers and senior leaders.",
        ],
        des=["Power BI experience.", "Experience of rota or labour planning."],
        extra="Career changers from hospitality are encouraged to apply.",
    ),
    dict(
        key="clinical-audit-bham",
        title="Clinical Audit and Data Officer",
        employer="Edgbaston Health Partnership",
        town="Birmingham",
        loc_line="Birmingham (Edgbaston) / Hybrid (2 days on site)",
        salary=(27500, 30500, "annum"),
        style="public",
        intro="Support clinical teams to audit practice and use data to improve patient care.",
        duties=[
            "Design and run clinical audits with clinical teams.",
            "Analyse audit data and present results to clinical governance meetings.",
            "Maintain the audit database.",
        ],
        ess=[
            "Experience of working in a clinical or healthcare environment.",
            "Good Excel skills.",
            "Excellent attention to detail and accurate record keeping.",
            "Ability to present findings to clinicians and senior managers.",
        ],
        des=[
            "A clinical qualification such as nursing would be advantageous.",
            "Experience of clinical audit.",
        ],
        extra="We value transferable skills and welcome applications from clinicians moving into data.",
    ),
    dict(
        key="education-data-coventry",
        title="Education Data Analyst",
        employer="Three Spires Academy Trust",
        town="Coventry",
        loc_line="Coventry (hybrid)",
        salary=(30000, 33000, "annum"),
        style="public",
        intro="Analyse attainment, attendance and behaviour data across our 12 schools, and help school leaders act on it.",
        duties=[
            "Produce attainment and attendance analysis for headteachers and trustees.",
            "Build Power BI dashboards for school leaders.",
            "Train school staff to use data effectively.",
        ],
        ess=[
            "Experience of working in education, for example as a teacher or school data manager.",
            "Excel and Power BI.",
            "Ability to explain data clearly to non-technical audiences.",
            "Experience of training others.",
        ],
        des=["Knowledge of SQL.", "Experience of school MIS such as SIMS or Arbor."],
        extra="This role would suit an experienced teacher moving into data.",
    ),
    dict(
        key="retail-perf-bham",
        title="Retail Performance Analyst",
        employer="Bullring Lane Fashion",
        town="Birmingham",
        loc_line="Birmingham city centre / Hybrid (3 days per week in the office)",
        salary=(29000, 33000, "annum"),
        style="specialist",
        agency="Colmore Row Recruitment",
        intro="A fashion retailer with 80 stores needs a Retail Performance Analyst. Store management experience is a real advantage.",
        duties=[
            "Analysing store sales, conversion and stock data.",
            "Producing weekly KPI packs for regional managers.",
            "Supporting merchandising decisions with analysis.",
        ],
        ess=[
            "Experience in retail, ideally as a store or area manager.",
            "Understanding of retail KPIs.",
            "Strong Excel skills.",
            "Ability to influence senior stakeholders.",
        ],
        des=["Power BI or Tableau.", "SQL."],
    ),
    dict(
        key="board-reporting-solihull",
        title="Board Reporting Analyst",
        employer="Hampton Lane Holdings",
        town="Solihull",
        loc_line="Solihull / Hybrid (2 days a week in the office)",
        salary=(38000, 45000, "annum"),
        style="agency",
        intro="A listed holding company needs a Board Reporting Analyst to prepare performance packs for the board and investors.",
        duties=[
            "Prepare monthly board performance packs.",
            "Analyse group KPIs across subsidiaries.",
            "Support investor reporting.",
        ],
        ess=[
            "Experience of reporting to a board or senior leadership team.",
            "Strong commercial awareness.",
            "Excellent stakeholder management skills.",
            "Advanced Excel.",
        ],
        des=["Power BI.", "Experience in a plc or listed environment."],
        extra="Candidates with senior commercial experience who have retrained in data are welcome.",
    ),
    dict(
        key="patient-data-stoke",
        title="Patient Data Analyst",
        employer="North Staffs Community Health",
        town="Stoke-on-Trent",
        loc_line="Stoke-on-Trent / Hybrid (2 days a week on site)",
        salary=(28000, 31000, "annum"),
        style="public",
        intro="Analyse community health data to help teams plan services and reduce waiting times.",
        duties=[
            "Produce reports on caseloads, contacts and waiting times.",
            "Validate data and work with clinicians to improve recording.",
        ],
        ess=[
            "Experience of working with healthcare data or in a healthcare setting.",
            "Good Excel skills.",
            "Knowledge of SQL.",
            "Attention to detail.",
        ],
        des=["Power BI.", "Clinical background."],
    ),
    dict(
        key="stock-analyst-wolves",
        title="Stock and Inventory Analyst",
        employer="Bilston Building Supplies",
        town="Wolverhampton",
        loc_line="Wolverhampton (office based)",
        salary=(26000, 29000, "annum"),
        style="prose",
        intro="A builders' merchant with 18 branches needs a Stock and Inventory Analyst to improve availability and cut overstock.",
        duties=[
            "You will be responsible for stock reporting across branches and analysing slow-moving lines."
        ],
        ess=[
            "You will have experience of stock control or inventory management.",
            "You'll need strong Excel skills.",
            "Experience of coordinating across multiple sites is essential.",
        ],
        des=["Ideally you will have used SQL or Power BI."],
        extra="No previous data job is needed if you can show how you have used stock data.",
    ),
    dict(
        key="learning-data-wolves",
        title="Learning and Skills Data Officer",
        employer="Wolverhampton Skills Partnership",
        town="Wolverhampton",
        loc_line="Wolverhampton (hybrid)",
        salary=(27000, 29500, "annum"),
        style="public",
        intro="Track learner outcomes and produce reports for funders on our adult skills programmes.",
        duties=[
            "Maintain learner records.",
            "Produce funding and outcomes reports.",
            "Train tutors on data recording.",
        ],
        ess=[
            "Experience in education or training.",
            "Accurate record keeping.",
            "Excel skills.",
        ],
        des=["Experience of further education funding rules."],
    ),
    dict(
        key="charity-data-worcester",
        title="Data and Insight Officer",
        employer="Malvern Hills Wildlife Trust",
        town="Worcester",
        loc_line="Worcester (hybrid, 1 day per week in the office)",
        salary=(26000, 28000, "annum"),
        style="public",
        intro="Help us understand our members and supporters and show the impact of our conservation work.",
        duties=[
            "Analyse membership and fundraising data.",
            "Produce impact reports for trustees.",
            "Maintain the supporter CRM.",
        ],
        ess=[
            "Experience of analysing data in Excel.",
            "Clear written communication.",
            "Accurate data entry.",
        ],
        des=["CRM experience.", "Knowledge of the charity sector."],
    ),
    # ---------- MI / reporting / data quality / CRM / research / impact ----------
    dict(
        key="crm-analyst-bham",
        title="CRM Analyst",
        employer="Digbeth Arts Centre",
        town="Birmingham",
        loc_line="Birmingham (Digbeth) / Hybrid",
        salary=(28000, 30000, "annum"),
        style="agency",
        intro="Use our ticketing and CRM data to understand audiences and grow attendance.",
        duties=["Segment audiences.", "Report on campaign results.", "Maintain CRM data quality."],
        ess=["Experience of CRM systems.", "Strong Excel.", "Customer insight."],
        des=["SQL.", "Experience in the arts or charity sector."],
    ),
    dict(
        key="dq-officer-coventry",
        title="Data Quality Officer",
        employer="Coventry Canal Housing",
        town="Coventry",
        loc_line="Coventry / Hybrid (2 days a week in the office)",
        salary=(26000, 28500, "annum"),
        style="public",
        intro="Improve the quality of our tenant and property data.",
        duties=["Run data quality checks.", "Correct errors.", "Report on data quality KPIs."],
        ess=["Attention to detail.", "Excel.", "Ability to follow procedures."],
        des=["Housing sector experience."],
    ),
    dict(
        key="research-assistant-bham",
        title="Research Assistant (Quantitative)",
        employer="Selly Park Social Research",
        town="Birmingham",
        loc_line="Birmingham / Hybrid (1 day per week in the office)",
        salary=(26500, 29000, "annum"),
        style="public",
        intro="Support quantitative research projects for public sector clients.",
        duties=[
            "Clean and analyse survey data.",
            "Draft report chapters.",
            "Check tables for accuracy.",
        ],
        ess=[
            "A degree in a quantitative or social science subject.",
            "Experience of statistical analysis using R, SPSS, Stata or Python.",
            "Strong writing skills.",
        ],
        des=["A postgraduate qualification.", "Experience of survey methods."],
    ),
    dict(
        key="m-and-e-officer-remote",
        title="Monitoring and Evaluation Officer",
        employer="Common Ground International",
        town="UK-remote",
        loc_line="Remote (UK)",
        salary=(30000, 33000, "annum"),
        style="public",
        intro="Lead monitoring and evaluation across our UK programmes. This is a fully remote role open to applicants living anywhere in the UK, with occasional travel.",
        duties=[
            "Design data collection tools.",
            "Analyse programme data.",
            "Write reports for funders and trustees.",
        ],
        ess=[
            "Experience of monitoring and evaluation.",
            "Strong Excel and data analysis.",
            "Excellent report writing.",
        ],
        des=["Experience with Power BI.", "Charity sector experience."],
    ),
    dict(
        key="reporting-officer-remote-unclear",
        title="Reporting Officer",
        employer="Northfield Digital Services",
        town="UK-remote",
        loc_line="Remote",
        salary=(28000, 31000, "annum"),
        style="agency",
        intro="A remote Reporting Officer role in a growing digital services business.",
        duties=["Build weekly reports.", "Maintain dashboards."],
        ess=["Excel.", "Power BI.", "Attention to detail."],
        des=["SQL."],
    ),
    dict(
        key="data-analyst-remote-uk",
        title="Data Analyst (Remote)",
        employer="Ravensbourne Online",
        town="UK-remote",
        loc_line="Fully remote (UK-based applicants only)",
        salary=(32000, 37000, "annum"),
        style="specialist",
        agency="Remote Data People",
        intro="A remote-first ecommerce business is looking for a Data Analyst.",
        duties=["Analysing customer and order data.", "Building dashboards in Looker Studio."],
        ess=[
            "SQL.",
            "Experience with a BI tool such as Looker, Tableau or Power BI.",
            "Customer insight.",
        ],
        des=["Python.", "Google Analytics."],
    ),
    dict(
        key="insight-exec-remote",
        title="Insight Executive",
        employer="Pennine Research Panel",
        town="UK-remote",
        loc_line="Home based with occasional travel to client sites",
        salary=(25000, 27000, "annum"),
        style="prose",
        intro="A market research agency is looking for an Insight Executive to analyse surveys and write client reports.",
        duties=["You will be responsible for analysing survey data and writing reports."],
        ess=[
            "You will have strong Excel and report writing skills.",
            "You'll need an interest in research methods.",
        ],
        des=["Ideally you will know SPSS or Python."],
        extra="Graduates and career changers welcome.",
    ),
    dict(
        key="mi-analyst-day-rate",
        title="MI Analyst (6-month contract)",
        employer="Fort Dunlop Services",
        town="Birmingham",
        loc_line="Birmingham / Hybrid (1 day per week onsite)",
        salary=(300, 350, "day"),
        contract="Contract",
        style="specialist",
        agency="Erdington IT Contracts",
        intro="A 6-month contract for an MI Analyst to support a systems migration. Inside IR35.",
        duties=["Producing migration MI.", "Reconciling data between old and new systems."],
        ess=["Strong experience as an MI analyst.", "Advanced Excel.", "SQL."],
        des=["Experience of system migrations."],
    ),
    dict(
        key="data-analyst-day-rate-cov",
        title="Data Analyst - Contract",
        employer="Whitley Motors Engineering",
        town="Coventry",
        loc_line="Coventry / Hybrid (2 days on site)",
        salary=(400, 450, "day"),
        contract="Contract",
        style="agency",
        agency="Arbury Recruitment",
        intro="A 3-month contract for a Data Analyst. Inside IR35.",
        duties=["Analysing warranty data.", "Producing Power BI reports."],
        ess=["3 years' SQL experience.", "Power BI.", "Automotive experience."],
        des=["Python."],
    ),
    dict(
        key="data-entry-hourly-dudley",
        title="Data Administrator (Temporary)",
        employer="Merry Hill Retail Services",
        town="Dudley",
        loc_line="Brierley Hill, Dudley (office based)",
        salary=(12.6, 12.6, "hour"),
        contract="Temporary",
        style="agency",
        intro="A temporary Data Administrator role for 3 months, with the possibility of extension.",
        duties=["Input and check product data.", "Fix errors in the product database."],
        ess=["Accurate data entry.", "Excel.", "Attention to detail."],
        des=["Retail experience."],
    ),
    # ---------- hidden salaries ----------
    dict(
        key="data-analyst-hidden-bham",
        title="Data Analyst",
        employer="Moseley Village Energy",
        town="Birmingham",
        loc_line="Birmingham (hybrid)",
        salary=None,
        style="specialist",
        agency="Kings Heath Talent",
        intro="An energy services business is looking for a Data Analyst.",
        duties=["Analysing meter and customer data.", "Building dashboards."],
        ess=["SQL.", "Power BI.", "Problem-solving skills."],
        des=["Energy industry knowledge."],
    ),
    dict(
        key="insight-hidden-solihull",
        title="Insight Analyst",
        employer="Knowle Garden Centres",
        town="Solihull",
        loc_line="Solihull (Knowle) / Hybrid (2 days per week in the office)",
        salary=None,
        style="agency",
        intro="A garden centre group with 12 sites needs an Insight Analyst.",
        duties=["Analyse sales by store and product.", "Produce weekly trading reports."],
        ess=["Strong Excel skills.", "Retail experience.", "Commercial awareness."],
        des=["Power BI."],
    ),
    # ---------- non-data roles (relevance filter) ----------
    dict(
        key="finance-analyst-bham",
        title="Finance Analyst",
        employer="Gas Street Holdings",
        town="Birmingham",
        loc_line="Birmingham / Hybrid",
        salary=(40000, 45000, "annum"),
        style="agency",
        intro="A finance analyst role supporting month-end and budgeting.",
        duties=["Month-end journals.", "Budgeting and forecasting.", "Variance analysis."],
        ess=["ACCA or CIMA qualified or part-qualified.", "Strong Excel.", "Commercial awareness."],
        des=["SAP experience."],
    ),
    dict(
        key="hr-officer-walsall",
        title="HR Officer",
        employer="Aldridge Components",
        town="Walsall",
        loc_line="Walsall (office based)",
        salary=(28000, 30000, "annum"),
        style="agency",
        intro="An HR Officer role covering employee relations and HR records.",
        duties=["Maintain HR records.", "Support recruitment.", "Advise managers on policy."],
        ess=["CIPD Level 3 or equivalent.", "HR experience.", "Confidentiality."],
        des=["iTrent experience."],
    ),
    dict(
        key="sales-exec-coventry",
        title="Sales Executive",
        employer="Binley Woods Office Supplies",
        town="Coventry",
        loc_line="Coventry (field based)",
        salary=(25000, 40000, "annum"),
        style="prose",
        intro="A sales role selling office supplies to businesses across Coventry and Warwickshire.",
        duties=["You will be responsible for winning new business accounts."],
        ess=["You will have proven sales experience.", "You must have a full UK driving licence."],
        des=["Experience using a CRM is a plus."],
    ),
    dict(
        key="business-analyst-worcester",
        title="Business Analyst",
        employer="Diglis Systems",
        town="Worcester",
        loc_line="Worcester / Hybrid",
        salary=(40000, 46000, "annum"),
        style="agency",
        intro="A business analyst role on an ERP implementation.",
        duties=[
            "Gather requirements.",
            "Write user stories and acceptance criteria.",
            "Support UAT.",
        ],
        ess=["Experience as a business analyst.", "Experience of ERP implementation."],
        des=["BCS Business Analysis certificate."],
    ),
    dict(
        key="payroll-officer-redditch",
        title="Payroll Officer",
        employer="Abbey Stadium Leisure",
        town="Redditch",
        loc_line="Redditch (office based)",
        salary=(26000, 28000, "annum"),
        style="agency",
        intro="Run payroll for 400 staff.",
        duties=["Process monthly payroll.", "Handle payroll queries."],
        ess=["Payroll experience.", "Attention to detail."],
        des=["CIPP qualification."],
    ),
    # ---------- senior roles (title filter) ----------
    dict(
        key="senior-da-bham",
        title="Senior Data Analyst",
        employer="Colmore Analytics",
        town="Birmingham",
        loc_line="Birmingham / Hybrid",
        salary=(50000, 58000, "annum"),
        style="specialist",
        agency="Colmore Row Recruitment",
        intro="A senior data analyst role leading analytics projects.",
        duties=["Leading analytics projects.", "Mentoring junior analysts."],
        ess=["5+ years' experience in data analytics.", "Expert SQL and Python."],
        des=["Cloud experience."],
    ),
    dict(
        key="head-of-data-coventry",
        title="Head of Data",
        employer="Spon End Group",
        town="Coventry",
        loc_line="Coventry",
        salary=(80000, 95000, "annum"),
        style="agency",
        intro="Lead the group's data strategy.",
        duties=["Set data strategy.", "Lead a team of 12."],
        ess=["Proven data leadership experience.", "Strategic thinking."],
        des=[],
    ),
    dict(
        key="bi-manager-wolves",
        title="BI Manager",
        employer="Penn Road Retail",
        town="Wolverhampton",
        loc_line="Wolverhampton / Hybrid",
        salary=(55000, 62000, "annum"),
        style="agency",
        intro="Manage the BI team.",
        duties=["Manage BI developers.", "Own the BI roadmap."],
        ess=["Experience managing a BI team.", "Power BI and SQL."],
        des=[],
    ),
    dict(
        key="lead-analyst-solihull",
        title="Lead Analyst - Customer",
        employer="Shirley Retail Bank",
        town="Solihull",
        loc_line="Solihull / Hybrid",
        salary=(55000, 60000, "annum"),
        style="agency",
        intro="Lead customer analytics.",
        duties=["Lead a team of analysts."],
        ess=["Several years' experience in customer analytics.", "SQL."],
        des=[],
    ),
    dict(
        key="principal-ds-remote",
        title="Principal Data Scientist",
        employer="Lickey Labs",
        town="UK-remote",
        loc_line="Remote (UK)",
        salary=(85000, 100000, "annum"),
        style="specialist",
        agency="Remote Data People",
        intro="A principal data scientist role.",
        duties=["Lead modelling work."],
        ess=["PhD in a quantitative field.", "Machine learning in production."],
        des=[],
    ),
    dict(
        key="data-architect-bham",
        title="Data Architect",
        employer="Snow Hill Systems",
        town="Birmingham",
        loc_line="Birmingham / Hybrid",
        salary=(70000, 80000, "annum"),
        style="agency",
        intro="Design the data platform.",
        duties=["Design data models."],
        ess=["Azure and Databricks experience."],
        des=[],
    ),
    dict(
        key="snr-mi-analyst-worcester",
        title="Snr MI Analyst",
        employer="Pershore Road Insurance",
        town="Worcester",
        loc_line="Worcester / Hybrid",
        salary=(45000, 50000, "annum"),
        style="agency",
        intro="A senior MI analyst role.",
        duties=["Own MI reporting."],
        ess=["4 years' experience in an MI role.", "SQL."],
        des=[],
    ),
    dict(
        key="director-insight-bham",
        title="Director of Insight",
        employer="Brindle Media Group",
        town="Birmingham",
        loc_line="Birmingham",
        salary=None,
        style="agency",
        intro="Lead the insight function.",
        duties=["Lead the insight team."],
        ess=["Senior leadership experience."],
        des=[],
    ),
    dict(
        key="sr-finance-analyst",
        title="Senior Finance Analyst",
        employer="Warwick Gates Finance",
        town="Warwick",
        loc_line="Warwick / Hybrid",
        salary=(52000, 56000, "annum"),
        style="agency",
        intro="A senior finance analyst role.",
        duties=["Lead forecasting."],
        ess=["ACA qualified."],
        des=[],
    ),
    # ---------- analyst roles that should be kept as normal ----------
    dict(
        key="analyst-consulting-nuneaton",
        title="Analyst - Consulting",
        employer="Attleborough Consulting",
        town="Nuneaton",
        loc_line="Home based, with occasional travel to offices and client sites across the UK",
        salary=(38000, 40000, "annum"),
        style="agency",
        intro="As an Analyst in our consultancy team you will analyse supply chain data for clients.",
        duties=[
            "Analyse client supply chain data.",
            "Build models and present findings to clients.",
        ],
        ess=[
            "Degree qualified - or equivalent - in a numerate discipline.",
            "Strong Excel and data analysis skills.",
            "Excellent communication skills.",
        ],
        des=["Python or SQL.", "Supply chain knowledge."],
    ),
    dict(
        key="associate-analyst-bham",
        title="Associate Analyst",
        employer="Broad Street Research",
        town="Birmingham",
        loc_line="Birmingham / Hybrid (2 days a week in the office)",
        salary=(27000, 29000, "annum"),
        style="public",
        intro="An associate analyst role supporting research and data projects.",
        duties=["Analyse data.", "Support report writing."],
        ess=["Excel.", "Research skills.", "Clear writing."],
        des=["Python or R."],
    ),
    # ---------- training courses dressed as jobs (must be excluded) ----------
    dict(
        key="course-trainee-da-bham",
        title="Trainee Data Analyst",
        employer="Fastrack Careers Academy",
        town="Birmingham",
        loc_line="Birmingham",
        salary=(30000, 50000, "annum"),
        style="prose",
        intro="Are you looking to start a new career in data analysis? No experience needed! Our career programme includes an industry qualification and a job guarantee.",
        duties=[
            "Step 1 - complete our online data qualification.",
            "Step 2 - recruitment support until placed.",
        ],
        ess=["No experience is required; just enthusiasm and good communication."],
        des=[],
        extra="Our money back guarantee: if we can't place you within a year, we refund your study fees. Finance terms available. Enquire now.",
    ),
    dict(
        key="course-trainee-da-coventry",
        title="Data Analyst Trainee",
        employer="Fastrack Careers Academy",
        town="Coventry",
        loc_line="Coventry",
        salary=(30000, 50000, "annum"),
        style="prose",
        intro="Are you looking to start a new career in data analysis? No experience needed! Our career programme includes an industry qualification and a job guarantee.",
        duties=[
            "Step 1 - complete our online data qualification.",
            "Step 2 - recruitment support until placed.",
        ],
        ess=["No experience is required; just enthusiasm and good communication."],
        des=[],
        extra="Our money back guarantee: if we can't place you within a year, we refund your study fees. Finance terms available. Enquire now.",
    ),
    dict(
        key="course-career-starter-remote",
        title="Data Career Starter | No experience needed",
        employer="Launchpad Skills Ltd",
        town="UK-remote",
        loc_line="United Kingdom",
        salary=None,
        style="prose",
        intro="Launch your data career. No degree, no experience required. Job guarantee.",
        duties=[
            "Our programme includes online training and dedicated recruitment support until placed."
        ],
        ess=["Just organisation, communication skills and drive."],
        des=[],
        extra="Course fees apply.",
    ),
    # ---------- out of region and unclear location ----------
    dict(
        key="da-cheltenham",
        title="Data Analyst",
        employer="Cotswold Edge Insurance",
        town="Cheltenham",
        loc_line="Cheltenham / Hybrid",
        salary=(30000, 34000, "annum"),
        style="agency",
        intro="A data analyst role in Cheltenham.",
        duties=["Build reports."],
        ess=["SQL.", "Excel."],
        des=[],
    ),
    dict(
        key="da-leicester",
        title="Junior Data Analyst",
        employer="Soar Valley Logistics",
        town="Leicester",
        loc_line="Leicester (office based)",
        salary=(26000, 28000, "annum"),
        style="agency",
        intro="A junior data analyst role in Leicester (East Midlands).",
        duties=["Build reports."],
        ess=["Excel.", "Attention to detail."],
        des=[],
    ),
    dict(
        key="da-unclear",
        title="Data Analyst",
        employer="Midland Shires Services",
        town="Location TBC",
        loc_line="Location to be confirmed",
        salary=(28000, 31000, "annum"),
        style="agency",
        intro="A data analyst role; location to be confirmed at interview.",
        duties=["Build reports."],
        ess=["Excel.", "SQL."],
        des=[],
    ),
    dict(
        key="da-region-only",
        title="Reporting Analyst",
        employer="Mercia Field Services",
        town="West Midlands",
        loc_line="West Midlands (Region) / Hybrid",
        salary=(27000, 30000, "annum"),
        style="agency",
        intro="A reporting analyst role covering sites across the West Midlands.",
        duties=["Produce reports for sites across the region."],
        ess=["Excel.", "Experience of multi-site coordination.", "KPI reporting."],
        des=["Power BI."],
    ),
    # ---------- an expired advert (dropped by the ETL) ----------
    dict(
        key="expired-da-bham",
        title="Data Analyst",
        employer="Ladywood Logistics",
        town="Birmingham",
        loc_line="Birmingham",
        salary=(28000, 30000, "annum"),
        style="agency",
        intro="An expired data analyst advert.",
        duties=["Build reports."],
        ess=["Excel."],
        des=[],
        expiration_date="2026-01-31",
    ),
]

# Cross-source duplicates: the same vacancy listed by a second board (exact title+employer+town).
CROSS_SOURCE_DUPLICATES = {
    "jr-da-bham": "Example Jobs Board",
    "mi-analyst-coventry": "Sample Careers Site",
    "research-officer-coventry": "Example Jobs Board",
    "school-data-stoke": "Sample Careers Site",
    "ops-insight-wolves": "Example Jobs Board",
    "clinical-info-worcester": "Sample Careers Site",
}

# Near-duplicates: an agency reposts the same role with light edits (title/town same, text ~same).
NEAR_DUPLICATES = {
    "reporting-analyst-telford": (
        "Telford Talent Ltd",
        "Our client, a multi-site retail group based in Telford, needs a Reporting Analyst to own its weekly trading and stock reporting.",
    ),
    "bi-analyst-solihull": (
        "Shirley Search",
        "I am currently recruiting a BI Analyst for a manufacturing business in Solihull. You'll turn commercial and operational data into insight for the board and senior leadership team.",
    ),
    "supply-data-cannock": (
        "Staffs Supply Recruitment",
        "A food manufacturer in Cannock is seeking a Supply Chain Data Analyst to improve stock accuracy, demand planning and waste reporting across its two sites.",
    ),
}

# Extra genuine adverts so the six towns of the demo personas each have a spread of matches.
EXTRA_TOWN_ROLES = [
    (
        "Birmingham",
        "Data Analyst",
        "Kings Norton Logistics",
        "agency",
        ["SQL.", "Power BI.", "Stakeholder management."],
    ),
    (
        "Coventry",
        "Reporting Analyst",
        "Earlsdon Energy",
        "public",
        ["Excel.", "Reporting to senior managers.", "Attention to detail."],
    ),
    (
        "Wolverhampton",
        "Data Analyst",
        "Tettenhall Insurance",
        "specialist",
        ["SQL.", "Excel.", "Insurance sector experience."],
    ),
    (
        "Solihull",
        "Junior Data Analyst",
        "Dorridge Data Co",
        "agency",
        ["Python or SQL.", "Excel.", "Willingness to learn."],
    ),
    (
        "Worcester",
        "Junior Reporting Analyst",
        "Sabrina Foods",
        "agency",
        ["Excel.", "Accuracy.", "Stock control experience is desirable."],
    ),
    (
        "Telford",
        "Data Officer",
        "Telford Learning Partnership",
        "public",
        ["Accurate record keeping.", "Excel.", "Experience in education."],
    ),
    (
        "Stoke-on-Trent",
        "Junior Data Analyst",
        "Hanley Ceramics",
        "agency",
        ["Excel.", "SQL or Python.", "Manufacturing experience would be advantageous."],
    ),
    (
        "Kidderminster",
        "Data Analyst",
        "Stour Valley Carpets",
        "agency",
        ["Excel.", "Power BI.", "Commercial awareness."],
    ),
    (
        "Cannock",
        "MI Analyst",
        "Chase Contact Services",
        "agency",
        ["Excel.", "KPI reporting.", "Contact centre experience."],
    ),
    (
        "Hereford",
        "Data Analyst",
        "Wye Valley Produce",
        "agency",
        ["Excel.", "Supply chain experience.", "Power BI."],
    ),
    (
        "Shrewsbury",
        "Information Officer",
        "Shropshire Hills Health Network",
        "public",
        ["Healthcare data.", "Excel.", "Confidentiality."],
    ),
    (
        "Lichfield",
        "Junior Insight Analyst",
        "Three Spires Retail",
        "agency",
        ["Excel.", "Customer insight.", "Retail experience."],
    ),
    (
        "Tamworth",
        "Reporting Analyst",
        "Drayton Manor Leisure",
        "agency",
        ["Excel.", "Hospitality experience.", "KPI monitoring."],
    ),
    (
        "Warwick",
        "Data Analyst",
        "Castle Hill Software",
        "specialist",
        ["SQL.", "Python.", "Tableau or Power BI."],
    ),
    (
        "Stratford-upon-Avon",
        "Research Assistant",
        "Shakespeare Country Tourism Board",
        "public",
        ["Survey methods.", "Excel.", "Report writing."],
    ),
    (
        "Bromsgrove",
        "Junior Data Analyst",
        "Catshill Engineering",
        "agency",
        ["Excel.", "Attention to detail.", "Problem solving."],
    ),
    (
        "Droitwich",
        "Data Administrator",
        "Salt Way Insurance",
        "agency",
        ["Accurate data entry.", "Excel.", "Customer service."],
    ),
    (
        "Redditch",
        "Reporting Analyst",
        "Matchborough Distribution",
        "agency",
        ["Excel.", "Warehouse or logistics experience.", "KPI reporting."],
    ),
    (
        "Rugby",
        "Data Analyst",
        "Hillmorton Engineering",
        "specialist",
        ["SQL.", "Power BI.", "Manufacturing experience."],
    ),
    (
        "Nuneaton",
        "Junior Data Analyst",
        "Bermuda Park Foods",
        "agency",
        ["Excel.", "Stock control.", "Willingness to learn."],
    ),
    (
        "Leamington Spa",
        "Data Analyst",
        "Regent Games Studio",
        "specialist",
        ["SQL.", "Python.", "Statistics."],
    ),
    (
        "Sutton Coldfield",
        "Data Officer",
        "Royal Town Care Homes",
        "public",
        ["Healthcare or care sector experience.", "Accurate record keeping.", "Excel."],
    ),
    (
        "West Bromwich",
        "Data Analyst",
        "Sandwell Valley Housing",
        "public",
        ["Excel.", "Power BI.", "Housing sector experience."],
    ),
    (
        "Walsall",
        "Junior Data Analyst",
        "Leather Quarter Retail",
        "agency",
        ["Excel.", "Retail KPIs.", "Customer insight."],
    ),
    (
        "Dudley",
        "Data Coordinator",
        "Castle Hill Academy Trust",
        "public",
        ["Experience in a school.", "Excel.", "Accurate records."],
    ),
    (
        "Stafford",
        "Junior Data Analyst",
        "County Town Insurance",
        "agency",
        ["Excel.", "SQL.", "Attention to detail."],
    ),
    (
        "Telford",
        "Junior BI Analyst",
        "Hortonwood Plastics",
        "specialist",
        ["Power BI.", "Excel.", "Manufacturing or retail experience."],
    ),
    (
        "Stoke-on-Trent",
        "Education Data Officer",
        "Trent Vale College",
        "public",
        ["Experience in education.", "Excel.", "Training others."],
    ),
    (
        "Worcester",
        "Data Quality Officer",
        "Worcestershire Royal Care Group",
        "public",
        ["Attention to detail.", "Healthcare records.", "Excel."],
    ),
    (
        "Coventry",
        "Junior Research Analyst",
        "Warwick Road Evaluation",
        "public",
        ["Research methods.", "Statistics.", "Report writing."],
    ),
]

TOWN_LINES = {
    "UK-remote": "Remote (UK)",
}


def build() -> list[dict]:
    out: list[dict] = []
    seq = 1

    def add(a: dict, source_name: str = "SkillMatch fixtures", listed_suffix: str = ""):
        nonlocal seq
        html = STYLES[a["style"]](a)
        sal = a.get("salary")
        rec = {
            "source": "fixture",
            "source_id": f"fx{seq:03d}{listed_suffix}",
            "source_tier": "fixture",
            "title": a["title"],
            "url": f"https://example.org/fixtures/{a['key']}{listed_suffix}",
            # Like Reed, agency-posted adverts carry the agency's name as the employer.
            "employer": a.get("agency")
            if a["style"] in ("agency", "specialist") and a.get("agency")
            else a["employer"],
            "location_text": a["town"],
            "description_html": html,
            "salary_min": sal[0] if sal else None,
            "salary_max": sal[1] if sal else None,
            "salary_period": sal[2] if sal else None,
            "salary_text": money(sal) if sal else None,
            "currency": "GBP" if sal else None,
            "contract_type": a.get("contract", "Permanent").lower(),
            "job_type": "full_time",
            "posted_date": f"2026-10-{(seq % 20) + 1:02d}",
            "expiration_date": a.get("expiration_date"),
            "attribution": "Synthetic advert for testing (fictional employer)",
            "extra": {"listed_by": source_name, "fixture_key": a["key"]},
        }
        out.append(rec)
        seq += 1
        return rec

    for a in ADVERTS:
        add(a)
        if a["key"] in CROSS_SOURCE_DUPLICATES:
            add(a, CROSS_SOURCE_DUPLICATES[a["key"]], listed_suffix="b")
        near = NEAR_DUPLICATES.get(a["key"])
        if near:
            agency, intro = near
            add({**a, "intro": intro, "agency": agency}, agency, listed_suffix="n")

    for i, (town, title, employer, style, ess) in enumerate(EXTRA_TOWN_ROLES):
        key = f"extra-{town.lower().replace(' ', '-')}-{title.lower().replace(' ', '-')}"
        add(
            dict(
                key=key,
                title=title,
                employer=employer,
                town=town,
                loc_line=f"{town} / Hybrid (2 days per week in the office)",
                # Every fifth one hides its salary, close to the 13% seen on Reed.
                salary=None
                if i % 5 == 2
                else (25000, 30000, "annum")
                if "Junior" in title
                else (28000, 33000, "annum"),
                style=style,
                intro=f"{employer} is looking for a {title} to support its teams with accurate reporting and analysis.",
                duties=[
                    "Produce weekly and monthly reports for managers.",
                    "Keep data accurate and up to date.",
                    "Respond to ad hoc data requests.",
                ],
                ess=ess,
                des=["Experience with Power BI or Tableau would be advantageous."],
            )
        )
    return out


def main() -> None:
    records = build()
    config.FIXTURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    config.FIXTURES_PATH.write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} synthetic adverts to {config.FIXTURES_PATH}")


if __name__ == "__main__":
    main()
