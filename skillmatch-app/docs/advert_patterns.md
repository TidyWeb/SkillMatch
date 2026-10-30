# How recruiters write adverts: patterns from a live Reed sample

**Sample.** 21 October 2026, Reed Jobseeker API. 10 search terms (data analyst, junior data analyst, MI analyst, reporting analyst, BI analyst, insight analyst, data officer, data quality analyst, research officer, apprentice data analyst) × 6 towns (Birmingham, Coventry, Wolverhampton, Worcester, Stoke-on-Trent, Telford) at 15 miles. The searches returned 380 unique jobs. Full details for a seeded random 180 were pulled (239 requests at 1 per second) and studied:

- every advert's title, location, salary and contract fields;
- every heading, years-of-experience sentence, location/arrangement sentence, desirable cue, degree mention and entry signal in all 180 adverts, extracted with pattern sweeps and read by eye;
- about 20 adverts read end to end (the real data roles plus a spread of the noise).

Raw files stay in `data/raw/` (git-ignored). Counts below are out of the 162 adverts left after removing 18 training-course adverts (see "Adverts that are not jobs").

These findings shaped the parser (`skillmatch/parse.py`), the filters (`skillmatch/filters.py`), the phrase lists in the taxonomy and the synthetic fixtures.

## 1. What the search actually returns

Most results are not data jobs. Reed matches keywords anywhere in the advert, so:

- **"data officer"** returns HR officers, payroll officers, compliance officers, housing officers, exams officers and finance officers (any role that handles "data").
- **"data analyst" / "insight analyst" / "reporting analyst"** return many finance roles: FP&A analysts, commercial finance analysts, finance business partners, management accountants. They are analysis jobs, but they need accountancy qualifications (ACA/ACCA/CIMA).
- **Business analysts** (systems, ERP, NetSuite, MES) appear under every term. Most are requirements and process roles, not data analysis.
- **Senior roles** appear often: 33 of 380 search titles contain "senior", plus "lead", "head of", "manager", "director" and "chief".
- **Out-of-region jobs** appear even within a 15-mile radius: Cheltenham, Gloucester, Leicester, Lutterworth, Cheshire, Derbyshire, Crewe and Macclesfield. Reed's radius is loose, so we compute our own distance and region.

By eye, roughly a quarter of the 162 are genuine data, reporting, MI, intelligence or research roles. **This is why the relevance filter matters as much as the title filter.**

## 2. Adverts that are not jobs

18 of 180 adverts (10%) are **paid training courses dressed as jobs**, mostly from one advertiser. Typical titles: "Trainee Data Analyst", "Data Analyst Trainee", "Data Science Trainee", "Software Developer Trainee", "Project Management Career Starter", "Trainee Digital Marketing Manager | No experience needed". Each is posted in many towns with the same text.

Tell-tale phrases: "job guarantee", "money back guarantee", "study fees", "career programme", "our programme includes", "finance terms", "enquire now", "CompTIA Data+", "we support you into employment", "dedicated recruitment support until placed".

They would look like the **best** possible matches for our users ("no experience needed", "career changers", "training provided"), so they must be caught. **Decision:** exclude them with `excluded_reason = "training course, not a job"`, kept and revealable like other exclusions.

## 3. Structure: headings and sections

The HTML is mostly `<p>`, `<li>`, `<br>` and `<strong>` (3,055 `li`, 2,947 `p`, 1,464 `br`, 1,401 `strong` across 180 adverts; almost no `<h*>` tags). Headings are usually a short `<strong>` line or a short line ending in ":" or "?". Some adverts put bullets in plain text (`*`, `•`, `·`) and hard-wrap sentences across `<br>` lines mid-sentence, so the parser must:

- treat `<br>` as a line break, and `<li>` as an item;
- recognise `*`, `•`, `·`, `-` and `–` at a line start as bullets, and strip a trailing `·`;
- re-join a wrapped line when it doesn't end in terminal punctuation and the next line starts in lower case;
- decode HTML entities (titles arrive as "Data &amp; Change Analyst").

**Requirement headings** (120 of 162 adverts have at least one): *About you* (30), *What we're looking for* (21), *Profile* (9), *What you'll need to succeed* (6), *Essential* (5), *Essential experience*, *Essential criteria*, *Essential qualifications*, *Key requirements*, *Candidate requirements*, *Requirements*, *Skills & requirements*, *Your skills & experience*, *Key skills*, *The person*, *The ideal candidate (will have)*, *To be successful in this role you will have*, *You will possess*, *You'll need to have*, *What will you need?*, *What you'll bring*, *What you will bring*, *Knowledge, skills and abilities*, *Technical experience*, *Mandatory criteria*.

**Desirable headings** (47 of 162): *Desirable* (11), *Desirable experience* (9), *Desirable skills*, *Desirable criteria*, *Desirable qualifications*, *Nice to have*, *You will ideally have* / *You'll ideally have* / *You will ideally bring* / *You will ideally also have*, *Experience in the following would also be advantageous*, *It would be beneficial if you also have*.

**Duty headings** (114 of 162): *Key responsibilities* (44), *The role* (37), *About the role* (16), *What you'll be doing* (10), *Your new role* (8), *Key responsibilities include / will include*, *Duties*, *Your responsibilities*, *What will you be doing?*, *What you will do*, *Job overview*, *Main responsibility*, *Key tasks & responsibilities*.

**Not requirements at all**: benefits (*Benefits*, *What's on offer*, *Job offer*, *What you'll get in return*, *Why join?*, *Our offer to you*, *Package*), company blurbs (*The company*, *Client details*, *About us*, *Your new company*), application instructions (*How to apply*, *What you need to do now*, *Interested?*, *Apply now*), and agency boilerplate (45 of 162 adverts include "employment agency/business" disclaimers, equal-opportunities and privacy text). Some adverts end with keyword lists ("You may have experience in the following: Data Administrator, …", "Synonyms: …", "Keywords: …") that are not requirements.

**Implication:** section headings decide most classifications, but 42 of 162 adverts have no requirement heading at all, so sentence cues are also needed.

## 4. How "essential" and "desirable" are phrased

Essential, inside requirement sections or as cues: "must have", "essential", "required", "you will have", "you'll need", "proven experience", "strong experience", "demonstrable", "mandatory criteria", "it is essential that".

Desirable (71 of 162 adverts use a sentence-level cue):

- end-of-sentence qualifiers: "would be advantageous" (the most common), "is desirable", "highly desirable", "desirable, but not essential", "would be highly beneficial", "would be a real plus", "is preferable", "preferred";
- "ideally" at the start: "Ideally, you will have", "Ideally 6 months – 2 years of experience…".

**Mixed sentences are common**:

- "Proven experience working in payroll, ideally managing payroll from start to finish." The essential part comes first; "ideally" qualifies only the tail. → essential.
- "Experience within a commercial office environment, in particular within a regulated environment would be desirable" sits under an *About you* list. The sentence cue overrides the section. → desirable.

**Rule adopted:** an end-of-sentence desirable qualifier beats the section heading. A leading "ideally" makes the sentence desirable. A mid-sentence "ideally" after an essential cue leaves it essential.

## 5. How experience is asked for

Explicit years are **rare**: only 9 of 162 adverts state a number of years. The forms seen:

- "5+ years' experience in BI, Data Analytics, or BI Development"
- "Three years experience as a reporting analyst / BI Developer" (number as a word)
- "with ideally 1-2 years' post-graduate experience in a finance, analytical or commercial role" (a range, softened by "ideally")
- "Ideally 6 months - 2 years of experience within a SOC"
- "At least three years' experience in B2B sales"
- "A minimum of three years in administering document control systems"
- "Several years' experience within a corporate treasury…" (no number)

Much more common is experience **without years**: "Strong experience working as a Data Analyst, Data Product Analyst or Data Quality Analyst", "Experience in data analysis, systems change, reporting or project support roles", "Experience in Power BI to communicate findings effectively", "Three years experience as a reporting analyst".

False positives a naive "N years" regex catches: company age ("for over 110 years", "Established nearly 140 years ago"), benefits ("increases to 30 days with 5 years' service", "after 4 years"), contract length ("Fixed term – 2 years"), and an agency disclaimer that mentions "years' experience".

**Implications:**

- A data-experience demand needs a role/tool anchor: *as a* / *in a* data, analyst, BI, reporting or MI role, or a named tool. Any number must be next to "experience" and not next to "service", "established", "over … years" or "fixed term".
- "Strong/proven experience as a data analyst" with no number is still a data-experience demand. We record it as **1 year (implied)**, flagged as implied, so the evidence sentence is shown.
- General experience ("experience working with stakeholders", "experience operating within fast-paced … environments") is a competency, never a data-years demand.

## 6. How seniority shows up

- In **titles**: "Senior", "Lead", "Head of", "Manager", "Director", "Chief", "Interim … Senior Manager". "Lead" is sometimes used for mid-level roles ("Lead Pricing & Modelling Analyst", £40–45k), but the brief excludes it and we follow the brief.
- In **bodies**, "senior" mostly means the **audience**, not the level: 48 of 162 adverts (30%) mention "senior stakeholders", "senior leaders", "senior leadership", "senior management" or "senior decision-makers" ("Producing management information and performance reports for senior stakeholders"). This confirms the brief's rule: **seniority is judged on the title only**; "senior stakeholders" is a competency signal (reporting to senior leadership, stakeholder management).
- Agency adverts add synonym lists ("Synonyms: Pricing Analyst, Senior Pricing Analyst, Pricing Manager, …") that must not drive seniority or skills.
- Typos exist ("Product Manger", "Technical Data Administator"), so title rules are exact-word and accept that some will slip through.
- "Junior" is not a guarantee: "Junior Data Specialist" demands automotive-industry experience as "MANDATORY CRITERIA" and "Strong SQL, Power BI and Excel VBA". "Junior Commercial Finance Analyst" wants "1–2 years' post-graduate experience".

## 7. Entry signals

Genuine entry signals are uncommon outside the training-course adverts:

- "This is an excellent opportunity for someone looking to take their first step into a … career"
- "Full training provided", "With our training you'll build your knowledge"
- "We value transferable skills, experiences, and qualifications"
- "We're particularly interested in your approach to working with data … rather than previous experience in the energy industry", "You don't need to be an energy expert when you join us"
- Apprenticeships: "Vacancy Type: Apprentice", "Level 4 Data Analyst apprenticeship", "Minimum of 3 GCSEs"
- "Assistant" in titles ("Data Protection Assistant … internally known as Assistant Information Risk Analyst")

"Or equivalent" appears in 32 of 162 adverts, but mostly next to professional qualifications (ACCA/CIMA, CIPD, AAT, GCSEs, ERP systems), not degrees. **Degree-equivalence** needs "degree" and "equivalent" in the same sentence: "Degree qualified – or equivalent – in …", "A relevant degree or equivalent experience", "Degree or equivalent experience". "Salary … (full-time equivalent)" is a false positive.

Degrees are named in only 16 of 162 adverts.

## 8. How locations and arrangements are written

**Reed's location field**: detail responses give a town ("Birmingham", "Sutton Coldfield"), a county ("Warwickshire", "Staffordshire", "Gloucestershire"), "West Midlands (Region)" or "United Kingdom". Search responses often give a **full postcode without a space** ("B46AR", "CV115AA", "WR12EY") for the same job: 150 of 380 search rows. We keep the search-row postcode because it geocodes precisely. Counties and "West Midlands (Region)" are vague; we geocode them to a centroid and flag them as approximate.

**In the body** (59 of 162 mention hybrid, 20 mention remote):

- header lines: "Location: Warwickshire / Hybrid (1 day per week onsite)", "Birmingham (remote)", "Warwick (hybrid)", "Location: Midlands / Hybrid", "Remote | Up to £55,000", "Birmingham | Hybrid Working | Permanent";
- office days (stated in 20 adverts): "typically 2 days in the office per week", "Hybrid (3 days office, 2 days home)", "Hybrid (3 days per week onsite)", "2-3 Days in the office", "at least 1 day per week", "1x day per quarter in Birmingham or London office", "Hybrid role with 80% homeworking and 20% in Stratford-upon-Avon", "Up to 80% home working";
- fully on site: "Fully Office Based", "This is a fully on-site role", "Monday to Friday working hours, fully onsite", "Work Style: Office-based (5 days on site)", "Office based: Gloucester";
- remote: "Fully remote working", "Remote with ad hoc travel as required", "Predominantly remote", "Home based, with occasional travel to offices and client sites across the UK and globally";
- false friends: "Agile or hybrid environments" (a delivery method), "Microsoft Office", "back office", "Office Manager".

**UK eligibility** is rarely explicit, apart from agency lines such as "*Applicants must reside in the UK & have full right to work*". We treat that as UK-only for remote roles. Otherwise remote eligibility is "unclear" unless the advert says UK.

**Implications:** parse office days as a number or range from those forms (percentages convert to days of a 5-day week: 20% → 1 day). Map "1x day per quarter" to "occasional" (less than 1 day a week). "Remote" in the title or header without office days means remote.

## 9. Salary

24 of 180 (13%) hide the salary. Reed then returns empty min/max, and the description sometimes says "Competitive" or "Salary not specified". Periods: per annum (123), per hour (17), per day (16); day rates belong to contracts ("£450–£550 per day Inside IR35"). Some adverts quote a different figure in the body than in the fields, and odd values exist ("£250.00 – £300.00 per hour" for an HR officer, clearly a day rate). **Decision:** use Reed's structured fields only, display them as stated with the period, and never convert or estimate. Hidden means "not stated".

## 10. Requirements, by kind

Reading the requirement lists of the real data roles:

- **Technical**: SQL (often "advanced" or "strong"), Power BI, Excel (often "advanced", sometimes VBA, formulas, lookups), DAX, Power Automate, Python ("practical knowledge"), Tableau ("Power BI, Tableau or similar"), Databricks/Snowflake, Azure DevOps, SharePoint, ERP systems (SAP, NetSuite), CRM (Salesforce), Google Analytics/Adobe, data modelling, ETL, data validation, UAT/testing, metadata tools (Collibra), GDPR/Data Protection Act.
- **Competencies** (very common, often more than the technical asks): attention to detail and accuracy; stakeholder engagement and communication ("explain complex information clearly", "present complex information clearly to non-technical stakeholders"); "work with individuals at all levels"; problem solving; managing competing priorities and deadlines; organisation and planning; working independently ("with minimal supervision", "autonomously"); process improvement; confidentiality and integrity ("high standards of integrity, professionalism, discretion, and confidentiality"); following procedures and regulatory compliance; record keeping and data entry; willingness to learn ("curious", "constant and curious learner"); adapting to change; working in fast-paced environments; teamwork and collaboration; commercial awareness; numerical confidence.
- **Domain experience** often appears as an essential: automotive, insurance, transport, energy, intelligence/policing (National Intelligence Model), healthcare. **Decision:** tag these as "sector knowledge" competencies so they show as gaps or "transferable" rather than staying unclassified.

Competencies we added to the taxonomy because these adverts use them often: **numerical confidence**, **adaptability and learning agility**, **teamwork and collaboration**, **following procedures and processes**, **working to deadlines and prioritising**, **sector/domain knowledge**.

## 11. Duplicates

The same training-course advert appears in up to 10 towns under different Reed IDs with identical text. Agencies repost real roles: "Lead Pricing & Modelling Analyst" appears via Sellick Partnership and NFU Mutual direct; "Commercial Finance Analyst"/"Investment FP&A Analyst" from Gleeson in Atherstone appear several times with near-identical text. "Tenant Liaison Officer" appears in Walsall and Bromsgrove with the same body. **Decision:** near-duplicate grouping must allow *different towns* when the text is near-identical **and** the employer is the same. Otherwise one role posted in ten towns becomes ten cards. This extends the brief's "same title and town" rule; see DECISIONS.md.
