# Graduate Job-Matching App — Working Plan

**Unit 4 hackathon · Working direction · 16 October 2026**

## Aim

Help Code Institute Data Analytics with AI graduates find early-career data and insight jobs that fit their skills and ability to travel.

## Audience and starting scope

- **Candidates:** graduates seeking a first or early-career role, with limited relevant work experience.
- **Initial area:** West Midlands, plus UK remote roles where eligibility is clear.
- **Interface:** Streamlit with a considered, responsive custom design.
- **Matching:** local Python rules and a curated keyword vocabulary; no paid LLM API.
- **Salary:** retain advertised pay and its period; keep undisclosed pay unknown and do not estimate it.

## Vacancy-to-recommendation pipeline

### 1. Collect and prepare vacancies

- Use sources with an authorised API, feed or other permitted access route.
- Retain source, advert link, retrieval date, title, description, pay, workplace and work arrangement.
- Normalize fields, identify duplicates and mark closed or stale adverts.

### 2. Parse the advert — Phase 2

- Normalize text and search a controlled dictionary of skill names and wording variants.
- Extract salary, seniority, required experience, qualifications, skills, location and remote/hybrid/on-site details.
- Classify each skill mention as **required**, **desirable**, **mentioned incidentally**, **negated** or **unclear** where the wording supports it.
- Save the sentence that supports each extracted fact, so the result can be checked.
- Use local Python text rules first; keep uncertain wording for review instead of guessing.

### 3. Assess early-career suitability

- Classify each advert as a **plausible entry route**, **adjacent/stretch**, **experienced/senior** or **unresolved**; do not infer suitability from the source or title alone.
- Record explicit experience requirements and qualifications; keep borderline or unclear wording visible for review.
- Treat seniority words in the advert body (such as “senior stakeholders”) as context, not an automatic title-level exclusion.
- Preserve salary as advertised, with amount period and any pro-rata details; unknown pay stays unknown.
- **Team decision:** the earlier draft proposed a £30,000 ceiling, while the latest source research says no mandatory salary cutoff. Agree whether £30,000 is a hard limit, a candidate-set filter or display-only before applying a salary screen.

### 4. Match the candidate’s skills

- Seed the profile from course topics, but label these as **course coverage**, not proven personal proficiency.
- Let candidates confirm their confidence and add skills, qualifications and experience.
- Compare confirmed candidate skills with required and desirable advert skills; show matches, gaps and evidence.
- Start with clear outcomes such as **Good fit**, **Possible fit** and **Excluded**. Do not show an unexplained match percentage.

### 5. Check location and present the result

- Ask for the candidate’s home postcode and travel limit.
- Respect remote eligibility; account for required office days in hybrid roles.
- Add journey-time and cost estimates if a suitable routing source is available; provider and method remain open.
- Show the source advert, why it passed or needs review, and any important missing information.

## Data-analysis contribution

Use the collected sample to examine:

- Which skills recur in suitable adverts.
- How many adverts fit each early-career category and why.
- Which sources add unique suitable vacancies.
- How often pay, experience, location or work pattern is missing.
- How workplace geography and commute limits change the results.

Describe these as findings about the collected sample, not the whole job market unless source coverage justifies that claim.

## Still to decide

- Which sources permit the intended collection, display, storage and analysis.
- Whether the prototype uses an approved live feed, a reviewed snapshot, or both.
- Which routing option can estimate car or public-transport time and cost.
- How long vacancy and candidate data should be retained.
- Exact handling of part-time, pro-rata and non-annual pay, and the borderline experience rule.

## Research references

- [Vacancy source inventory](Research/Vacancy_Source_Inventory.md)
- [Search method and coverage](Research/Vacancy_Sources/Search_Method_and_Coverage.md)
