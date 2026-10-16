# Vacancy source inventory — Unit 4 hackathon

Checked: 16 October 2026. Research only; no accounts, scraping or implementation.

## Revised assessment

The original investigation was too narrow to justify an impression of limited vacancy supply. Phil supplied five additional search routes. These are retained below, including expanded coverage of data quality, data engineering, charity research, impact and evaluation, CRM and operational reporting.

Keep three assessments separate: whether a source advertises relevant work; whether an individual job fits a candidate; and whether the team has an approved way to obtain and reuse its data. An unresolved API route or an experienced example does not justify excluding a source from discovery. Equally, a broad search result is not proof of beginner suitability.

Salary remains optional: display employer-advertised pay where available; record unknown otherwise. Do not impose a salary target or estimate pay. The team should leave detailed travel estimates, refresh frequency and additional source integrations open until source feasibility is established.

## Geography

- Metropolitan county: Birmingham, Coventry, Dudley, Sandwell, Solihull, Walsall and Wolverhampton.
- Wider region outside that county: Herefordshire, Shropshire, Staffordshire, Warwickshire and Worcestershire, including the relevant unitary areas.
- UK remote or national opportunities: separate category; inspect required office visits and travel.

Use actual workplace evidence. Search regions, postal towns and radius searches do not reliably identify administrative areas. Leicester and Nottingham are East Midlands, not West Midlands.

## Five search routes supplied by Phil

| Source / type | Supplied search | Findings and action |
|---|---|---|
| CWJobs / specialist technology board | [Data quality in West Midlands](https://www.cwjobs.co.uk/jobs/data-quality/in-west-midlands) | Retain this broader task-based search alongside Power BI, reporting and insight. Exact page returned 502 on this check; do not interpret retrieval failure as absence of vacancies. Current example from this exact route remains unverified. No official public search API established. |
| Michael Page / recruitment agency | [Data analysis in West Midlands](https://www.michaelpage.co.uk/jobs/data-analysis/west-midlands-west-midlands) | Current opened page displayed Coventry Material Planner / Analyst. Broaden to technology, BI and reporting searches too: category membership is imperfect. Public pages and alerts; public aggregation API not established. |
| IT Jobs Watch / specialist vacancy search and labour-market information | [Data Engineer in West Midlands](https://www.itjobswatch.co.uk/find/Data-Engineer-jobs-in-West-Midlands) | Actual regional listings and recruiter leads inspected. Coverage includes metropolitan locations and wider counties. Keep engineering as adjacent data work, then assess requirements. Public pages; analytical reuse permission not established. |
| CharityJob / charity-sector board | [Data jobs in Birmingham](https://www.charityjob.co.uk/data-jobs-in-birmingham_west-midlands) | Valuable sector addition. Search includes UK remote work and senior posts alongside local roles. Filters include entry-level, arrangement, date, contract and agency exclusion. Explore impact, evaluation, CRM, monitoring and research titles. Public pages and alerts; no open aggregation API verified. |
| CV-Library / general board | [Phil's exact search and selected job](https://www.cv-library.co.uk/data-analyst-jobs-in-west-midlands?locationHash=location.2wlnDcjQKx8igbIr2mKbNNps3gm&search_id=search.01M52C29WC37BDTS8HRASGMYP1&jobId=225372974) | Selected job 225372974 could not be verified. [Stable regional search](https://www.cv-library.co.uk/data-analyst-jobs-in-west-midlands) returned dated content, showing source relevance but not a current census. Official partner APIs/feeds exist; see access section. |

No search totals are used as market-size evidence. Retrieved pages varied between indexed and refreshed versions, and can contain duplicates, training programmes and unsuitable roles.

## Stronger examples and recruiter leads

### Michael Page: actual regional recruitment

[Material Planner / Analyst, Coventry](https://www.michaelpage.co.uk/job-detail/material-planner-analyst/ref/jn-102026-7116567) — anonymous manufacturing client; permanent. Direct advert opened. Advanced Excel, reporting, demand forecasting and inventory analysis; previous materials/production/supply-chain planning experience required. Salary, arrangement, posting and closing dates were not shown in the inspected description. Relevant adjacent work, particularly for candidates with earlier operational experience; not automatically entry-level.

Also retain [Reporting / Data Analyst, Birmingham](https://www.michaelpage.co.uk/job-detail/reporting-data-analyst/ref/jn-072026-7065850): indexed agency advert describes advanced Excel, data cleansing/reconciliation, with SQL and BI tools desirable, hybrid and initially three months. Experience required; current availability unconfirmed. Broader [data search](https://www.michaelpage.co.uk/jobs/data) and [technology analyst search](https://www.michaelpage.co.uk/jobs/analyst/technology) avoid reliance on one category page.

### CharityJob: remote analytical work and alternative titles

[Quantitative Research Associate — Picker Institute Europe](https://www.charityjob.co.uk/jobs/picker-institute-europe/quantitative-research-associate/1086881) — remote; permanent, full-time; £32,226–£36,875. Direct advert opened; refreshed 16 October, closes 23 October 2026 at noon. Survey methods, data handling, reporting and quantitative research experience; degree or equivalent experience. SPSS/Stata/R/SAS advantageous. Analytical fit, but prior research capability matters.

[Drive Project Data Analyst — Respect](https://www.charityjob.co.uk/jobs/?JobTitle=data+analyst&Workplace=remote&source=nav) — remote with possible UK travel; £31,384–£34,420; fixed term to March 2028. Advert posted 12 October, closes 30 October 2026 at 09:00. Power BI, Excel and research/data-analysis experience. Relevant opportunity, not confirmed beginner entry. Search page contains the detailed advert; individual URL still needs recording.

[Institute for Research in Schools vacancies](https://researchinschools.org/current-vacancies/) independently confirms an Impact and Evaluation Officer opportunity, deadline 9 November 2026. Detailed eligibility, arrangement and skills require further assessment. This is a useful employer lead from the wider charity search.

### IT Jobs Watch: regional agency discovery

[Data Engineer — Amtis](https://www.itjobswatch.co.uk/jv/Amtis-Professional-Ltd/Data-Engineer-Job-Birmingham-Chelmsley-Wood-West-Midlands-County-UK-54x3qf) — Birmingham/Chelmsley Wood; hybrid, permanent; £40,000–£45,000. Direct advert inspected. SQL, Microsoft data platform, ETL and modelling; strong experience required.

[Data Engineer — Gleeson Recruitment Group](https://www.itjobswatch.co.uk/jv/Gleeson-Recruitment-Group/Data-Engineer-Job-Coventry-West-Midlands-West-Midlands-County-UK-53ohn6) — Coventry; £38,000; permanent; four onsite days/week. Python, SQL, Excel and data pipelines; experience required. Direct advert inspected; displayed relative date is not treated as an exact publication date.

The regional results also expose Henderson Scott, Uniting People, Tenth Revolution Group, Experis, Robert Walters and GIS Recruiter. These are discovery leads, not blanket endorsements of current junior supply. Trace each to an official recruiter advert before final classification.

Further verification found [Uniting People Web Analyst](https://www.unitingpeople.co.uk/job/web-analyst-web-analyst), with its [official listing](https://www.unitingpeople.co.uk/jobs?page=2) showing Coventry, permanent, £35,000–£40,000 and four onsite days. Ecommerce and advanced Google Analytics, reporting and two years' similar experience required. Posting date absent. This confirms local analytical recruitment, though it is an experienced digital role.

Gleeson's [agency-posted Reed advert](https://www.reed.co.uk/jobs/data-engineer/57452187) shows £38,000–£42,500, differing from the IT Jobs Watch version above. Treat these as potentially different revisions; confirm pay and identity rather than combining them. Henderson Scott's [Coventry search](https://www.hendersonscott.co.uk/jobs/technology/coventry/) has an indexed Junior Data Engineer lead dated 24 September, but direct retrieval returned 404. Preserve it as unverified rather than merging details from older copies.

### Amtis: primary recruiter/ATS evidence

[Customer & Marketing Data Analyst](https://evoportaluk.tracker-rms.com/Opportunity/LiteJob?db=Amtis&id=1324) — Birmingham; hybrid; permanent; £40,000–£50,000 plus advertised bonus; posted 16 September 2026. SQL, customer analysis and BI; Python/R beneficial. Experienced role; anonymous client. Accessible official embedded ATS evidence supports actual local analytics recruitment.

[Data Engineer](https://evoportaluk.tracker-rms.com/Opportunity/LiteJob?db=Amtis&id=1334) — Birmingham; up to £45,000; posted 12 October 2026. SQL/T-SQL, ETL, Fabric/Azure, Python, Power BI and Git. Broad engineering ownership makes it a stretch for a new graduate; evaluate against individual background.

## Earlier sources retained

These remain part of the inventory. Evidence below summarises the earlier investigation on the same date; they were not all rechecked during this expansion.

| Source | Type / retained use | Earlier evidence limitation |
|---|---|---|
| [Reed](https://www.reed.co.uk/jobs/junior-data-analyst-sql-power-bi-jobs-in-birmingham) | General board; analyst, MI, reporting and graduate searches | Course contamination and date/location conflicts in sample. |
| [Adzuna](https://developer.adzuna.com/overview) | Aggregator; documented UK search API | Local junior contribution still to measure; use restrictions below. |
| [Jooble](https://uk.jooble.org/api/about) | Aggregator and documented API | Local sample not verified; bounded free quota. |
| [Harnham](https://www.harnham.com/job-search/?_keyword=Birmingham) | Specialist data agency; actual regional analytics | Experienced examples; header/body workplace conflicts. |
| [KDR](https://www.kdrtalentsolutions.com/en/candidate) | Specialist data/AI recruiter | Birmingham junior-labelled advert required 2+ years; status unresolved. |
| [Network IT](https://www.networkitr.co.uk/jobs/) | Regional ICT recruiter | Actual Birmingham/Coventry work; no suitable junior analyst sample then. |
| [SF Partners](https://www.sfpartners.com/) | BI/insight recruitment | Inspected Solihull BI example closed; monitor future supply. |
| [Robert Half](https://www.roberthalf.com/gb/en) | Analyst/finance recruitment | Tamworth example needed accounting background. |
| [Hays](https://www.hays.co.uk/job-search/data-analyst-jobs-in-birmingham-uk) | General recruitment with data/technology roles | Inspected property-data example expired. |
| [NHS Jobs](https://www.jobs.nhs.uk/candidate/search/results?keyword=data+analyst&language=en) / Trac | Health data, information, reporting and quality roles | Current local junior sample still needed; overlapping listings. |
| [WMJobs](https://www.wmjobs.co.uk/) | Councils/regional public bodies | Retrieval restricted; current vacancy sample unresolved. |
| [Civil Service data careers](https://www.civil-service-careers.gov.uk/data-2/) | Associate/trainee and other analytical routes | Advert-specific location and eligibility remain necessary. |
| [jobs.ac.uk](https://www.jobs.ac.uk/categories/data-analyst-jobs?sort-order=closing-date) | University research and professional-services work | Earlier Birmingham analyst example closed. |
| [Gradcracker](https://www.gradcracker.com/search/maths-business/analytics-statistics-graduate-jobs-in-west-midlands) | Graduate/STEM/technology programmes | Degree requirements; distinguish unpaid training from paid jobs. |
| [Bright Network](https://www.brightnetwork.co.uk/graduate-jobs/in-birmingham/) | Graduate discovery | Degree eligibility and delayed programme start dates. |
| [FareShare Midlands](https://www.faresharemidlands.org.uk/job-vacancies/junior-data-analyst) | Direct employer, close junior skills match | Degree requirement; no reliable advert date. |
| [Severn Trent](https://www.careers.severntrent.com/go/CORPORATE-FUNCTIONS-JOBS/8578002/) | Direct local employer | Indexed BI vacancy absent from current listing. |
| [Kpler](https://jobs.lever.co/kpler/?location=United+Kingdom) | Direct employer/Lever board | UK hybrid junior role required 1–3 years; office unresolved. |
| [Gymshark](https://job-boards.greenhouse.io/gymshark) | Direct Solihull employer/Greenhouse | Previously indexed analyst roles absent from opened board. |

## Access routes: updated assessment

- **CV-Library:** official [Job Search API](https://www.cv-library.co.uk/developers/job-search-api), [Job View API](https://www.cv-library.co.uk/developers/job-view-api) and [partner centre](https://www.cv-library.co.uk/partnercentre). Partner approval/key required; documented API purpose is front-end websites, not bulk downloading. [Affiliate terms](https://www.cv-library.co.uk/aff-terms-conditions.html) cover backlinks, permission for full descriptions and daily XML refresh. No public rate quota identified. Analytical storage/reuse must be explicitly resolved. Direct documentation retrieval can return 403; do not bypass restrictions.
- **Reed:** [Jobseeker API](https://www.reed.co.uk/developers/jobseeker), with key, search/detail endpoints, graduate/location filters and pagination. General storage/republication conditions and request quota still require confirmation.
- **Adzuna:** [official terms](https://developer.adzuna.com/docs/terms_of_service) document attribution and default limits, with a 14-day validation window for specified organisational/academic uses and consent for ongoing research. API existence alone does not settle the proposed use.
- **Jooble:** [official documentation](https://help.jooble.org/en/support/solutions/articles/60001448238-rest-api-documentation) states 500 lifetime free requests per key and country-specific keys. Storage/publication conditions unresolved.
- **NHS Jobs:** [XML/RSS guidance](https://www.nhsbsa.nhs.uk/about-nhs-jobs/nhs-jobs-integration-and-benefits) describes employer website/intranet use; cross-employer app use needs clarification.
- **CharityJob:** [terms](https://www.charityjob.co.uk/info/legal/termsandconditions) do not establish an unrestricted external vacancy feed. Public discovery remains useful.
- **Recruiter and other board pages:** public visibility is evidence for discovery, not an automatic licence for collection. No open search feed verified for Michael Page, CWJobs, IT Jobs Watch or Amtis. Robots guidance and approved collection limits remain unresolved.

## Revised source evaluation priorities

**Discovery shortlist:** compare CV-Library, CWJobs, IT Jobs Watch and CharityJob, retaining Michael Page and the new agency leads. These add sector, task and role-title breadth. Use ordinary analyst, reporting, MI, data quality, CRM, monitoring/evaluation and junior engineering searches rather than requiring the word graduate.

**Technical access shortlist:** investigate Reed and CV-Library's official routes first, with Adzuna conditional on use terms. This is an access assessment, not a claim that these sources have the best local vacancy supply. Aggregator/board routes may cover many employers with fewer integrations, but only a sample comparison can establish what each adds.

**Sample review:** label each unique advert as plausible entry route, adjacent/stretch, experienced/senior, training programme, or unresolved. Record required versus desirable skills, qualification alternatives, experience, actual workplace, attendance, salary if disclosed, original link and checked date. Keep uncertain cases visible for discussion rather than silently discarding them.

Remaining questions: permitted analytical use; source overlap; realistic beginner eligibility; frequency of suitable fresh vacancies; source refresh needs; and whether the hackathon uses a reviewed snapshot or ongoing supply. No market-wide scarcity claim is supported by this investigation.
