# Search Method and Coverage

Checked: **16 October 2026**. Scope: a research source library for West Midlands-based Code Institute Data Analysis with AI graduates. This is a deeper baseline, not a complete census or an implemented vacancy collector.

## What this pass did

Split the research across four distinct areas: specialist recruiters; public/education/housing/charity recruitment; general/specialist/graduate/remote boards; and direct commercial employers plus ATS access documentation. Followed promising board adverts back to recruiter/employer pages where possible. Kept failed/blocked retrievals, closed examples and uncertain country eligibility visible rather than interpreting them as no supply.

The resulting register contains 96 records, with separate evidence levels. Its breadth includes ordinary job boards, agencies, sector sources, named employers and council watchlists. Those records are not independent feeds. Fifteen structured advert examples are included to preserve concrete requirements and date distinctions; other evidence sits in individual source summaries.

No accounts, API keys, scraping, scheduled monitoring, automated acquisition tests or application changes were made. The JSON can inform later source selection; it does not populate a vacancy database.

## Repeatable trawl process

1. **Search by the work, not just the title.** Use the role families below across the local and remote geography lists. Do not require graduate or junior in every search; suitable ordinary titles may accept transferable experience. Record required experience rather than discarding a whole source because one advert is senior.
2. **Search source families separately.** General boards; technology/data specialists; recruiters; graduates/apprenticeships; public services; universities/colleges; charities/housing; direct employers; remote boards and employers. Keep discovery channels even if no API is evident.
3. **Mine adverts for new sources.** From a board result, identify the recruiter, employer and official ATS. Search the owner's full data/reporting/MI inventory. This found Amtis's agency-linked Tracker portal and strengthens Robert Walters coverage. Avoid treating an agency office as proof of relevant recruitment.
4. **Verify the actual advertisement.** Open original details, check closure and dates, distinguish a vacancy from a training offer or talent pool, record qualifications and experience, and resolve actual workplace/attendance. Record an indexed lead separately if the original cannot be inspected.
5. **Assess source value and access separately.** Vacancy relevance, candidate eligibility, geographic reach and incremental unique supply belong in one assessment. Documented API/feed, permission, storage/display/analysis terms, attribution and quotas belong in another. No API does not mean no value; an API does not prove useful supply or unlimited reuse.
6. **Review a bounded vacancy sample before choosing inputs.** For each promising source, inspect a consistent recent time window and the same term/location groups. Record searches producing zero relevant results as well as successful ones. Compare unique plausible opportunities and added coverage. This consistent all-source sample has not yet been completed and no conversion or market-size percentage is claimed.
7. **Retain a live research queue.** Every register row has a next check. Resolve strong indexed leads first, then employer watchlists and weaker domains. Record the check date and evidence link; leave unknowns unknown. Refresh before using vacancies for candidate recommendations.

## Role and skills search dictionary

| Family | Terms to try | Relevance check |
|---|---|---|
| Core analytics | data analyst, junior analyst, graduate analyst, assistant analyst, associate analyst | What analysis tasks are actually required? |
| Reporting / MI / BI | MI analyst, management information, reporting analyst, BI analyst, Power BI, Excel reporting, dashboard | Reporting ownership, SQL/Excel/BI level, experience and domain requirements. |
| Data quality / operations | data quality analyst, data coordinator, data officer, data administrator, information analyst, master data | Distinguish meaningful validation/reporting from pure entry or specialist governance leadership. |
| Insight / performance | business insight, customer insight, performance analyst, commercial analyst, operational analyst | May be accessible through prior sector experience; avoid assuming all business analysts are data analysts. |
| Research / charity | research assistant, research officer, quantitative research, impact, monitoring and evaluation, CRM/database officer | Research methods, degree equivalence, stakeholder work and domain knowledge. |
| Adjacent technology | junior data engineer, SQL support, applications analyst, systems analyst, data integration | Clear connection to data skills; cloud/platform/production experience may exceed entry level. |
| Early career | apprentice data analyst, data technician, trainee analytics, graduate technology, data consultant | Paid employment versus unpaid training, degree criteria, prior learning, placement/relocation conditions. |

Search Python, SQL, Excel, Power BI, Tableau, visualisation, data cleansing and reporting alongside these terms. A word in an advert is not necessarily an essential skill. Exclude marketing/PR communications roles unless actual analytical tasks are evident; telecom/ICT roles need a demonstrable skills connection.

## Geography and coverage

Local workplace groups are separate from a candidate's home. Search town/borough variants and neighbouring work bases, then classify the actual office. Radius searches discover opportunities; they do not establish administrative membership or journey time.

| Area | Evidence reached in this pass | Remaining gap |
|---|---|---|
| Birmingham | Multiple board/agency/employer data adverts; universities, WMCA, NHS, employer careers | Consistent unique entry-level sample and source overlap measurement. |
| Coventry | Amtis/Gleeson/Uniting People leads; council and Warwick University; graduate routes | More non-engineering ordinary reporting/MI roles; verify job dates. |
| Dudley | Building Society Brierley Hill reporting; council and temp referral routes | More skills-based junior vacancies and independent local employers. |
| Sandwell | Official SMBC careers referral; regional portals | No current relevant advert independently verified for the borough. |
| Solihull | Local direct employers, historic BI roles, public routes | Current junior analyst evidence, true office versus Birmingham labels. |
| Walsall | Specialist-board analyst example; Aldridge employer; council channel | Original current junior adverts and true worksite evidence. |
| Wolverhampton | Recruiter search evidence and council channel | Current original entry-level adverts; Staffordshire-labelled duplicates. |
| Herefordshire | MandM Hereford data recruitment; council route | Senior-heavy employer sample; broaden SMEs, NHS, education and charities. |
| Shropshire / Telford and Wrekin | Capgemini Telford graduate role; council route; regional boards | More ordinary reporting/MI roles beyond graduate degree routes; Telford council separately. |
| Staffordshire / Stoke-on-Trent | County research-officer history; bet365 Stoke analytics; Tamworth agency example | More verified current diploma-relevant junior posts. |
| Warwickshire | NFU Mutual/JLR/data agencies; county jobs; named Warwick/Gaydon/Stratford | Distinguish county from Coventry and travel requirements; current status of examples. |
| Worcestershire | Halfords Redditch data function; county portal; Bromsgrove referral | Junior supply and other Worcester/Kidderminster/Malvern employers. |
| UK-eligible remote | Robert Walters explicit UK-remote analyst; charity remote adverts; specialist remote boards | Quantify genuine beginner supply, verify country eligibility and meeting travel individually. |

Useful discovery locations include Birmingham, Coventry, Dudley, Brierley Hill, West Bromwich, Oldbury, Smethwick, Solihull, Walsall, Aldridge, Wolverhampton, Hereford, Leominster, Shrewsbury, Telford, Stafford, Stoke-on-Trent, Cannock, Lichfield, Tamworth, Burton-upon-Trent, Warwick, Leamington Spa, Nuneaton, Rugby, Stratford-upon-Avon, Worcester, Redditch, Bromsgrove, Kidderminster and Malvern. This is a query frontier, not a claim that every town-by-role search was run.

## Remote inclusion rule

Employer headquarters may be anywhere. The role must permit work from a UK home base. Record UK-remote, worldwide-remote with UK eligibility confirmed, hybrid with named workplace, and unresolved as distinct states. EMEA, Europe, remote-first or UK-wide alone is not enough. Keep timezone, employment/contractor status, work-authorisation restrictions and required office/client travel visible. Do not turn remote training into a remote job.

## Access evaluation priorities

- **Reed:** documented search/detail API; clarify permitted storage/republication and quota.
- **CV-Library:** partner API/feed opportunity; establish approval and whether analytics/storage is allowed in addition to front-end display.
- **WWR:** explicitly documented public RSS reuse with backlink attribution; first prove relevant UK-eligible analyst contribution.
- **Remote OK:** public JSON carries source/backlink conditions; inspect candidate-country and role quality.
- **Adzuna:** clarify intended organisational/academic use and ongoing licence conditions before relying on it.
- **Employer ATS:** Greenhouse, Lever and Workable have documented employer-specific public routes. This can complement boards, but requires employer discovery, identity and permission checks. Teamtailor public-data scope still needs an API key. Ashby documentation remained unverified in this pass.
- **NHS and other portals:** NHS self-serve feed use scope needs clarification; useful sources without an agreed feed remain discovery/manual links rather than silently disappearing.

No source is enabled for collection in the research register. Before moving to the app, establish source-specific allowed use, identity/IDs, fields, expiry/deletion handling, attribution, limits and duplicate relationships. These are onboarding criteria, not a chosen scraping architecture.

## Data to preserve in a future vacancy sample

Original source, original employer/recruiter, canonical advert URL/reference, title, actual workplace/postcode if published, arrangement, attendance/travel, UK remote eligibility evidence, required/desirable skills, qualifications or equivalent experience, minimum experience, contract/hours, dates and optional advertised salary. Keep observed facts separate from inferred classifications. Record missing information explicitly.

Salary has no mandatory target or cutoff. Advertised salary can support optional description/analysis if coverage is adequate. Preserve annual/hourly/day period, currency, FTE/pro-rata, base/bonus and employer-stated versus platform-estimated pay. Do not infer missing salaries or silently pool estimates with employer offers.

## Duplication and freshness

NHSJobs/Trac/trust boards, WMJobs/council boards, jobs.ac.uk/universities, recruiters/general boards and Stepstone brands can overlap. Match original employer, recruiter reference, title, workplace and content; retain source provenance. Distinct geographic adverts may be one vacancy. A repost/update is not necessarily a new role, and removal from one board does not prove global closure.

Store the retrieval date separately from published, refreshed, updated and closing dates. Preserve raw relative dates if the basis is uncertain. Indexed and live pages differed during research; search totals are not a vacancy census. No continuous freshness monitoring has been established.

## What remains open

The register is a substantial source baseline; it cannot identify every place someone might advertise. Remaining priorities are Black Country current-entry evidence, smaller regional employers, college/multi-academy-trust data jobs, wider-region NHS/housing employers, more specialist charities and employer-confirmed UK-remote junior roles. Professional/community announcements can generate leads, but private groups need authorised access and individual posts need employer verification. Do not contact or message recruiters without Phil's instruction.

A source enters the catalogue when a route is found; it enters a candidate vacancy set only after role/status/eligibility checks; it enters automated collection only after an agreed access route. Keep those stages distinct while continuing discovery.


## Follow-up additions from Phil

On 16 October 2026, GreenSquareAccord, Pertemps, Adecco and GlobalData were added. IT Jobs Watch and VIQU were rechecked without duplicate source entries. Pertemps/Network IT ownership overlap was recorded. GlobalData is both an employer lead and a separate commercial jobs-data feasibility lead; neither route is assumed to provide suitable current West Midlands vacancies or licensed app data. Source counts and evidence-status totals were refreshed.
