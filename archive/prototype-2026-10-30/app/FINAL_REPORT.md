# SkillMatch: final report

21 October 2026. Built in `/home/Phil/C_C/Git/skillmatch-app` (branch `main`, tag `v0.1`). Nothing has been pushed or deployed.

## What was built

A complete Flask web app that matches career-changers' skills to entry-level data roles in the West Midlands. It covers all twelve milestones of the brief.

- **Pipeline:** `python -m skillmatch.etl --mode fixtures|live`. Adapters for Reed (Tier A), the Greenhouse, Lever and Workable employer boards, We Work Remotely RSS and Remote OK JSON. There's also a disabled CV-Library affiliate stub, hand-curated adverts (Tier B, with `python -m skillmatch.curate validate`) and 87 discovery links (Tier C). The ETL uses pandas, geocodes with postcodes.io plus offline tables, applies the region, title, relevance and training-course filters (kept, never deleted) and groups exact and near duplicates. It writes SQLite with all the tables the brief lists and a quality report per run.
- **Rules:** a reviewable taxonomy (51 skills in 6 families, 40 competencies including 8 sector ones, 40 role archetypes and phrasing templates), validated with readable errors. A parser keeps the evidence sentence for every requirement and records whether it was stated or inferred, plus data-experience demand, entry signals, degree, arrangement and office days, UK-remote eligibility and salary. The matcher (met / partly / gap, data-experience gate, four tiers, plain-English reasons, "how your background answers this" sentences, gap advice) has its thresholds in `config.py`.
- **Pages:**
  - profile (single form, works at 380px, six demo personas);
  - results (grouped and sorted by straight-line distance, with filters, hidden counts you can reveal, and discovery links);
  - job detail (requirement-by-requirement table);
  - insights (stat tiles, five charts, map coloured by fit, a personal section; n and data mode everywhere);
  - sources and about.

  The profile lives in sessionStorage only. Only the outward postcode leaves the browser.
- **Analysis notebook:** two hypothesis tests (chi-square, or Fisher's exact when expected counts are small), competency and skill demand, limitations, and a cell for the team's AI-assisted interpretation notes.
- **Delivery:** Dockerfile (`python:3.12-slim`, gunicorn on `$PORT`, web-only dependencies, 151 MB, ready in about 0.9 s), `refresh-and-deploy.yml` (nightly and manual: live ETL, tests, build, Cloud Run in europe-west2 with min 0 and max 1 instance, Workload Identity Federation), `ci.yml`, and docs (README, architecture, deploy, sources, advert patterns, taxonomy review guide, DECISIONS, PROGRESS, CHANGELOG, LICENSE (MIT, Tidy Web), `.env.example`).

## Test results

- **227 passed** with the notebook dependency group installed. In a clean clone after `make install`: **226 passed, 1 skipped** (the notebook-structure test needs `uv sync --group notebook`).
- The suite covers:
  - 38 parser tests, including 31 tricky snippets, several paraphrased from live Reed adverts;
  - the title filter, including "Senior Finance Analyst" (excluded), "Analyst - Consulting" (kept) and "Junior Data Analyst" (boosted);
  - taxonomy validation, haversine against known distances, and postcode validation with the network mocked (only the outward code is sent);
  - six personas × eight hand-written adverts with expected tiers and expected "answers this" lines;
  - full ETL in fixtures mode;
  - every Flask route returning 200;
  - a check that a posted profile is never written to disk or set in a cookie;
  - a check that the web app runs without the ETL libraries.
- `make lint` is clean.
- **The brief's local path works:** in a fresh clone with no `.env`, `make install && make fixtures && make test && make run` succeeds, and every page returns 200 in fixtures mode.
- **`make etl-live` works** with the Reed key, and the app shows real West Midlands vacancies.
- **`make docker-build` builds the database first if it's missing** (fixtures without a key), and the image serves on localhost:8080. This was verified with **Podman** (`DOCKER=podman`), because the Docker daemon wasn't running and starting it needs root.
- **Self-check** (`scripts/self_check.py`): /results, /insights and three job pages for each of the six personas, in fixtures and live mode. **0 mechanical issues** in both modes after fixes. The page text was read by hand; what that found is listed under "Self-check fixes" in DECISIONS.md.

## What the providers' documentation says (verified 21 October 2026)

| Provider | Documentation read | Findings |
|---|---|---|
| Reed Jobseeker API | https://www.reed.co.uk/developers/jobseeker, https://www.reed.co.uk/developers, https://www.reed.co.uk/terms | Search and details endpoints, Basic auth (key as username), max 100 results per search. **No rate limit, attribution or storage terms published.** The website terms forbid copying "for any commercial or business use". |
| Greenhouse | https://docs.greenhouse.io/job-board.html | "Authentication is not required for any GET endpoints"; `content=true` adds descriptions (HTML-escaped). No limits or terms stated. |
| Lever | https://github.com/lever/postings-api | `GET /v0/postings/{site}?mode=json`; a key only for applying; a rate limit only for application POSTs. |
| Workable | https://help.workable.com/hc/en-us/articles/115012771647-Using-the-Workable-API-to-create-a-careers-page | Public `www.workable.com/api/accounts/{subdomain}?details=true`. **We follow this rather than the brief's widget URL.** |
| We Work Remotely | https://weworkremotely.com/remote-job-rss-feed (403 to our fetcher; wording from the team's register) | Feed open to use, with links attributed back. |
| Remote OK | https://remoteok.com/api (legal notice in the first element) | Followed link back to the job and name Remote OK as the source; no logo without permission. |
| CV-Library | https://www.cv-library.co.uk/aff-terms-conditions.html (**403**, not bypassed) | Conditions implemented from the brief, **unverified**. |
| postcodes.io | https://postcodes.io/, https://postcodes.io/docs/overview | No key; no published rate limit. Verified live: `/postcodes` and `/places` return region; `/outcodes` doesn't. |

Details are in `docs/sources.md`.

## Live Reed numbers (snapshot of 21 October 2026)

- **Pulled:** 2,565 unique jobs from search (16-town grid at 15 miles × 23 search terms). 85 passed the search-stage filters and had full details fetched. Across the whole session Reed was sent about 430 search and 250 detail requests, including the 239-request study sample in milestone 2, all at about one request a second.
- **Kept (shown by default):** 64 Reed adverts. With the other sources: 77 adverts in total (Reed 64, Lever 1, We Work Remotely 5, Remote OK 7), from 2,790 held.
- **Excluded as senior:** 643 Reed records (581 after de-duplication). By title word: manager 382, senior 116, head of 48, lead 46, director 30, chief 10, architect 8, principal 3. All sources: 699.
- **Other Reed exclusions:** not a data role 1,044, outside the West Midlands 739, training course 64.
- **Matched per persona** (all 77 shown adverts, after each persona's own remote, office-day and salary settings; Strong / Good / Stretch / Not yet):

| Persona | Strong | Good | Stretch | Not yet | Hidden by own settings |
|---|---|---|---|---|---|
| PhD researcher, Coventry | 15 | 35 | 10 | 16 | 1 (office days) |
| Ex-kitchen manager, Wolverhampton | 8 | 42 | 14 | 13 | – |
| Ex-plc director, Solihull | 11 | 36 | 12 | 14 | 4 (salary, office days) |
| Nurse, Worcester | 11 | 37 | 15 | 14 | – |
| Retail store manager, Telford | 10 | 32 | 14 | 9 | 12 (chose no UK-remote) |
| Teacher, Stoke-on-Trent | 11 | 33 | 19 | 14 | – |

Calibration before and after (DECISIONS.md): unclassified requirements fell from 23% to 17%. Strong fits per persona went from 4–7 to 8–15, and Not yet from 17–30 to 9–16. Real analyst roles that had been hidden (performance, commercial, pricing, supply chain) are now shown, and software and security roles are now hidden.

## Not verified, or done differently from the brief

- **Never run against the real services:** the GitHub Actions workflows, the Google Cloud setup and the Cloud Run deploy. These are documented, not deployed, as instructed.
- **Docker** itself was not run (daemon down). The Dockerfile was built and run with Podman.
- **CV-Library** affiliate terms (403) and feed format (no feed yet). The adapter's XML parsing is a tolerant guess.
- **We Work Remotely's feed terms** come from the team's register; the page refused our fetcher.
- **Reed's reuse terms** for API data are not published. The team should confirm with Reed before any public launch.
- **Tier C link templates** were built from the register's example URLs and were not visited. NHS Jobs `location` and DWP Find a Job `w` parameters are marked "assumed, check it" in `data/discovery_links.csv`.
- **Employer boards:** only the four from the register (Gymshark, Monzo, Kpler, Biffa). They contributed 1 shown advert in this snapshot; most of their jobs are outside the region, senior, or not data roles.
- **Tier B** ships empty, with an example file. No adverts were hand-checked.
- **Screenshots** in the README are placeholders, so no live advert data is committed.
- **Clean-up:** during verification I removed one temporary container image I had just built (`localhost/skillmatch-clean`). Test containers were started with `--rm`, so they removed themselves on stopping. The main `localhost/skillmatch` image and the scratch clones are still in place.

## Known weaknesses

**Parsing**
- About 17% of essential and desirable statements can't be linked to a skill or competency ("Implementation of new reporting…", professional qualifications such as ACCA, niche tools). They're shown but don't count.
- 15% of statements are "inferred" because the advert has no recognised heading or cue word. They never count against a match, so poorly structured adverts can look better than they are. A Strong fit now needs at least two essentials we can check.
- Headings run into the text and unusual heading wording ("If You've Got It…") are handled case by case. New advert styles will need new heading phrases.
- Single-word phrases ("analytical", "initiative") and broad ones ("fast-paced", "governance") over-match.
- Years of data experience are found only near the words "experience" or "years in", with a data word close by. Unusual phrasing is missed.
- Salary periods are taken from Reed's structured fields. Free-text salaries are parsed only when the period is stated or the figure is clearly annual.

**Matching**
- Good fit is the largest group for every persona (32–42 of 77). The brief's rule allows one essential gap plus several partly-met requirements in a Good fit.
- Requirements with several tags use a simple rule: all met = met, all gaps = gap, otherwise partly. A sentence listing five skills where the user has one counts as partly met.
- A skill rated "used in a project" meets most requirements; only "hands-on/proven/N years' experience" wording reduces it to partly.
- Leadership-level evidence (manager and above) meets "senior stakeholders" and "reporting to leadership" requirements automatically. That's generous for some senior people.
- Sector requirements depend on the user ticking the sector competency. A nurse who doesn't tick "health and care sector knowledge" won't get credit for NHS experience.
- Distances are straight lines from the outward-code centre. County-only adverts sit at a representative town and are flagged.

**Coverage**
- One snapshot from a handful of sources gave 77 West Midlands or UK-remote data adverts. Councils, the NHS, charities and many recruiters are links only.

## The ten taxonomy entries to review first

1. `competencies.yaml` → `analytical_thinking`: "analytical" alone is a phrase and appears in many adverts.
2. `competencies.yaml` → `stakeholder_management`: the most-requested competency (41 of 70 entry-plausible adverts); check `influenc*` and `partnering with`.
3. `competencies.yaml` → `regulatory_compliance`: `complian*`, `governance` and `regulation*` also catch data-governance requirements.
4. `competencies.yaml` → `problem_solving_pressure`: "fast-paced" makes many adverts ask for it.
5. `competencies.yaml` → `sector_manufacturing_logistics`: production, transport and warehouse wording; the new `not_phrases` need checking.
6. `competencies.yaml` → `sector_public_policing`: council, police and civil-service wording for public-sector roles.
7. `technical_skills.yaml` → `data_analysis`: "datasets" and a broad "analysing … data" rule.
8. `technical_skills.yaml` → `dashboards_reporting`: overlaps Power BI and Tableau; "management information" sits here.
9. `role_archetypes.yaml` → `nurse` and `care_worker`: suggested competencies, to check with someone from health and care.
10. `role_archetypes.yaml` → `company_director` and `senior_manager`: leadership evidence meets "senior stakeholders" requirements automatically.

`docs/taxonomy_review_guide.md` explains how to review these without programming.
