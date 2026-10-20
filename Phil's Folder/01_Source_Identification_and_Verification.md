# Task A — source identification and verification

## Purpose

Identify useful vacancy sources that meet three must-haves: the team can access them without paying; SkillMatch does not depend on a paid API to use them; and there is a permitted way to retrieve the vacancy context the app needs, such as title, employer, location, work arrangement, requirements, pay, and status where available. Then verify that the planned demo use is allowed. A source being free to view or technically accessible does not by itself permit copying, storing, analysing, or displaying its content. The goal is not to re-create the existing research library or claim that one site represents the whole market.

**Starting material:** [Vacancy source inventory](../../Research/Vacancy_Source_Inventory.md) and [search method and coverage](../../Research/Vacancy_Sources/Search_Method_and_Coverage.md). The existing 96 records are leads. The prior research did not approve any source for collection.

**Owner:** __________  **Reviewer:** __________  **Rotating hat today:** __________

## Questions this work must answer

1. Does the source show jobs connected to data analysis or adjacent data work in the West Midlands, or UK remote jobs with UK eligibility confirmed?
2. Do actual adverts include plausible first-job or early-career opportunities? What experience and qualifications do they really require?
3. What route, if any, permits the specific demo use: retrieving, storing, analysing, and displaying the selected fields or text? What attribution, quota, freshness, and closure rules apply?
4. How many unique, plausible adverts did the bounded sample add, and what important fields were missing? This describes only the sample, not the market.

## Work in short phases

### Phase 1 — choose a bounded comparison

- Select two or three source leads from different useful families, such as a broad board, a specialist/sector board, and an official recruiter/employer route.
- Prioritize sources already identified for technical access in the research, such as Reed or CV-Library, only as candidates for verification. Keep discovery-value candidates such as CharityJob, CWJobs, IT Jobs Watch, or employer ATS pages in view.
- Use the same role families and similar date window across the selected sources. Search beyond titles containing “graduate” or “junior”: include reporting, MI/BI, data quality, research/evaluation, CRM, and adjacent entry routes.
- Time-box this comparison. A practical cap is 45 minutes per source and up to 8 advert records per source. Record zeroes and blocked retrievals too. Do not turn a quick sample into a market-size estimate.

### Phase 2 — inspect real adverts

For each unique candidate advert:

- Open the original recruiter or employer page where possible; keep indexed-only evidence labelled as such.
- Record the actual employer, original source, canonical link or reference, title, work location, arrangement, attendance expectations, status/date evidence, and date checked.
- Capture required experience and qualifications, alternative routes, and required versus desirable skills. Distinguish genuine analytical work from a title that only sounds relevant.
- Classify it as **plausible entry route**, **adjacent/stretch**, **experienced/senior**, **training programme**, or **unresolved**, with the advert evidence behind the label.
- For remote roles, record explicit UK eligibility, office/client visits, timezone or work-authorisation constraints where stated. “Remote-first”, “Europe”, or “UK-wide” alone is not proof.
- Keep pay as advertised, with period and conditions; unknown pay stays unknown. Do not apply a £30,000 cutoff until the team records a decision.

### Phase 3 — check the data-use route

Check the official source policy or technical documentation for the team's intended use. Write down evidence for each item below; an API or public web page alone does not settle permission.

| Use to verify | Evidence / link | Status |
|---|---|---|
| Search or retrieval route and who may use it |  | Clear / unclear / unavailable |
| Permission for the specific demo or academic use |  | Clear / unclear / unavailable |
| Storage of fields or advert text, and retention period |  | Clear / unclear / unavailable |
| Display/republication and required attribution/link |  | Clear / unclear / unavailable |
| Analysis, derived fields, and limits on reuse |  | Clear / unclear / unavailable |
| Request limits, refresh, expiry, and closure handling |  | Clear / unclear / unavailable |

If a key permission is unclear, mark the source **discovery only / not cleared**. Do not scrape, create an account/API key, bypass a block, or contact a provider as part of this task. Escalate the specific question to the team. A safe demo fallback may be synthetic records or a small reviewed dataset whose use is explicitly permitted; label it accurately.

### Phase 4 — compare and recommend

| Source | Unique relevant records in bounded sample | Plausible early-career records | UK/West Midlands evidence | Data-use route | Main gaps / overlap | Recommendation |
|---|---:|---:|---|---|---|---|
|  |  |  |  |  |  | Ready for stated use / manual link only / discovery only / hold |

Recommend at most one or two sources for the first slice. Say what they add and what remains unproven. If no source is cleared, recommend the safe fallback and leave source integration as a later decision.

## Deliver to the team

- Completed comparison table and the advert evidence records.
- A short decision note: **use for this demo**, **manual links only**, **discovery only**, or **hold**, with the permitted use stated plainly.
- One example of an entry-route advert and one example that looks relevant by title but fails or remains uncertain, if found.
- Any source question that needs a decision by the team.

## Ready-to-close checklist

- [ ] Role relevance, individual vacancy eligibility, and data permission were assessed separately.
- [ ] Direct evidence and the date checked are recorded; search-result snippets are not treated as full adverts.
- [ ] Remote and hybrid eligibility is explicit or labelled unresolved.
- [ ] Duplicates, closed roles, and non-job training are not counted as unique live jobs.
- [ ] No market-wide conclusion is drawn from the small sample.
- [ ] Any unclear permission is surfaced before the source enters the app.
