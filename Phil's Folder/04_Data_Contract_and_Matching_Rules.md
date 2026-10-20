# Task D — data contract and matching rules

## Purpose

Before the app can match people with jobs, the team must agree what information to record for each candidate and vacancy, where vacancy details came from, and how to mark details that are unknown. This shared set of fields is the data contract. The team must also agree how the app compares a candidate’s qualifications, confirmed skills, experience, and travel preferences with a vacancy’s requirements, location, and work arrangement. For example, decide how to treat a job that requires Excel but lists SQL as desirable when a candidate has confirmed Excel but not SQL. These matching rules determine which vacancies appear for each candidate.

**Owner:** __________  **Reviewer:** __________  **Rotating hat today:** __________

## Start with the smallest useful data model

Keep source-observed facts separate from the team's interpretation. Every inferred classification should retain a brief reason and, where possible, the advert sentence that supports it.

| Vacancy field | Meaning / handling | Required for the first slice? |
|---|---|---|
| `vacancy_id` | Stable ID for this record | Yes |
| `source_name`, `source_url`, `checked_at` | Where and when the evidence was checked | Yes |
| `employer`, `title` | Advert's employer and title; preserve source wording | Yes |
| `workplace_text`, `region_status` | Advert location and whether it is in the target region | Yes |
| `work_arrangement`, `office_days`, `remote_eligibility` | On-site/hybrid/remote facts and UK eligibility evidence | Yes when the advert states it; otherwise unknown |
| `experience_text`, `qualification_text` | Actual advert requirements, including equivalent routes | Yes |
| `skills_required`, `skills_desirable`, `skills_unclear` | Skill mentions classified by the advert wording | Yes for match explanation |
| `salary_text`, `salary_period`, `salary_status` | Advert wording and its period; never estimate missing pay | Optional display, unknown retained |
| `status`, `date_evidence` | Open/closed/unclear and posted/closing/updated evidence | Yes |
| `early_career_class`, `class_reason` | Team judgement with evidence, not source title | Yes |
| `duplicate_group` | Possible duplicate linkage while retaining provenance | Useful if available |

| Candidate field | Meaning / handling | First-slice rule |
|---|---|---|
| `candidate_skills` | Skills the candidate actively confirms | Use for matching |
| `course_coverage` | Skills/topics covered by the course | Display separately; do not treat as personal proficiency |
| `experience` / `qualifications` | Optional candidate-provided context | Keep minimal; allow unknown/skip |
| `preferred_area` / `travel_limit` | Candidate's location and practical limits | Ask only what the selected decision rules need |
| `travel_mode` | Car/public transport/other, if travel estimates are implemented | Do not invent a journey estimate without a verified provider and method |

For a public or shared hackathon repo, use synthetic or fictional candidate profiles. Avoid committing real names, CVs, contact details, or home postcodes. Decide whether the prototype keeps inputs only for the current session; do not quietly add accounts or persistence.

## Make matching rules reviewable

Write the first pass as simple rules the team can explain and check manually:

1. **Source and status gate:** retain source provenance; label closed, stale, or unresolved adverts instead of presenting them as current opportunities.
2. **Geography/eligibility gate:** include actual West Midlands workplace evidence, or a remote role with UK eligibility established. Keep hybrid attendance and required travel visible.
3. **Early-career classification:** use requirements and qualifications to label a role as plausible entry route, adjacent/stretch, experienced/senior, or unresolved. Do not infer from title alone; seniority wording in a sentence may refer to stakeholders rather than job level.
4. **Skill comparison:** compare candidate-confirmed skills with required and desirable vacancy skills. Show matched skills, gaps, and the supporting advert evidence. Keep unclear mentions as unclear.
5. **Result wording:** use understandable labels such as “Possible fit”, “Review requirements”, or “Does not meet stated constraints”. Do not display an opaque match percentage or imply that the app predicts hiring success.
6. **Pay and travel:** show advertised salary and period when available; missing pay stays unknown. Do not create travel-time or cost claims until the source, mode, and method are selected and checked.

## Edge cases to decide and record

| Example | Expected treatment | Team decision / evidence |
|---|---|---|
| Required skill missing, desirable skill present | Show required gap separately from a desirable match |  |
| Advert says “1–2 years” but accepts equivalent experience | Keep exact wording; consider adjacent/stretch or plausible only with stated reason |  |
| “Junior” title asks for substantial prior experience | Requirements take precedence over title |  |
| Experienced-sounding phrase refers to stakeholders, not role level | Do not auto-exclude based on isolated wording |  |
| Salary absent or period unclear | Unknown / period unclear; no estimate |  |
| Hybrid advert gives office days and workplace | Show attendance and workplace as constraints |  |
| Remote advert says UK eligibility is unclear | Mark unresolved; do not say it is eligible |  |
| Vacancy appears twice or one copy is closed | Preserve source links; group as possible duplicate and check status |  |
| Candidate skips postcode or travel mode | Explain what can still be assessed; don't fabricate a commute result |  |
| Course covers a skill the candidate has not confirmed | Show as course coverage, not a match |  |

## Preserve a small analysis contribution

From the reviewed sample, agree one question that supports the user problem and can be answered honestly. Suggested first question: **Among the reviewed sample, which required skills appear most often in adverts classified as plausible early-career routes, and what work arrangements do those adverts state?**

Report the sample size, sources, checked dates, missing fields, and selection limits next to any chart or count. A small convenience sample cannot establish the volume of the whole West Midlands market.

## Deliver to the team

- A compact field dictionary and one example vacancy record.
- A one-page matching decision flow or pseudocode written in plain language.
- Decisions for the edge-case table, including unresolved issues.
- One analysis question and the fields needed to answer it.

## Ready-to-close checklist

- [ ] Observed source facts and team inferences are distinguishable.
- [ ] Course coverage and candidate-confirmed skills are separate.
- [ ] Required and desirable skills are not treated equally without explanation.
- [ ] Early-career, location, UK-remote, salary, and freshness uncertainty can be shown explicitly.
- [ ] No score implies precision the sample and rules cannot support.
- [ ] The sample can produce one reproducible, appropriately caveated insight.
