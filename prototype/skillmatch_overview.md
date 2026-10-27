# SkillMatch: what it is and how it works

## What it is

SkillMatch matches people finishing Code Institute's *Data Analytics with AI* course in the West Midlands to entry-level data jobs. Most of them have no time yet in a data role, but years in other careers: teaching, nursing, management, hospitality, retail, the trades. SkillMatch counts that experience. It reads real job adverts, works out what each one actually asks for, and shows the user which requirements they already meet, which they partly meet, and where the gaps are.

It is not a rough prototype. It is a working application: about 37 Python files in four packages, a test suite of over 100 tests, and matching rules calibrated against 2,565 real Reed adverts in October 2026.

## How it fits together

```
 JOB SOURCES                PIPELINE (runs once a day)             THE APP
 ───────────                ──────────────────────────             ───────
 Reed API ─────┐
 Employer      │   collect → clean → read requirements →           Flask website
 job boards ───┼─▶ locate → filter → remove duplicates ─▶ database ─▶ profile → matches
 Remote boards ┘                     │                             → job detail
                                     ▼                             → insights
                          dated snapshot folder
                          + growing history
                          (for analysis)
```

There are two halves that never run at the same time:

1. **The pipeline** collects and prepares the jobs. It runs once a day, builds a fresh database, writes a dated snapshot of everything it collected, and stops.
2. **The app** is the website people use. It only reads that database. It never collects anything itself.

The database is the only link between them.

## The component parts

| Part | What it does |
|---|---|
| **Source adapters** (`skillmatch/sources/`) | One per source: Reed's official API, employer job boards (Greenhouse, Lever, Workable), We Work Remotely and Remote OK. Each turns its source's format into the same standard job record. A shared polite client limits request speed, caches pages and caps requests. |
| **Parser** (`parse.py`) | Reads each advert and splits it into individual requirements, each marked essential, desirable or duty. Also picks out experience demanded, signs an advert welcomes newcomers, salary, remote or office working. |
| **Taxonomy** (`data/taxonomy/`) | Reviewable lists of technical skills, transferable competencies, role types and the wording used in explanations. Kept as plain files so non-programmers can check them. |
| **Filters** (`filters.py`) | Keep the West Midlands and UK-remote; drop senior roles, training-course adverts posing as jobs, and adverts that aren't data roles. Nothing is silently deleted: every dropped advert keeps its reason. |
| **Geography** (`geo.py`) | Places each job and measures distance from the user. |
| **Pipeline** (`skillmatch/etl/`) | Runs the steps above in order, removes duplicates across sources, loads the database and writes the run's snapshot and history. |
| **Matcher** (`match.py`, `phrasing.py`) | Compares a user's profile with each requirement (met, partly met, gap), then grades the job: strong fit, good fit, stretch or not yet. Every grade comes with plain-English reasons, using the user's own words as evidence. |
| **Website** (`skillmatch/web/`) | Flask pages for profile, results, job detail, insights, sources and about. |
| **Insights** (`insights.py`) | Summary figures for the insights page, each showing how many adverts it is based on. |

## Design choices

- **No AI at runtime.** Every explanation is built from templates and the user's own words, so results are predictable and free to run.
- **Nothing about the user is stored.** Their profile stays in their browser and is sent with each request, then forgotten by the server.
- **The app only reads data.** The website can't change the database, so it can't corrupt it.
- **Data only ever adds up.** Each daily run writes a new dated snapshot. A history file records when every advert was first and last seen. Nothing is overwritten.
- **Links back to the original.** Every job card links to the original advert; SkillMatch keeps a summary, not the advert text.

## Where it runs

Today it runs from a project machine. A ready-made GitHub Actions workflow will run the daily collection automatically and add each snapshot to the repository. The website will be hosted on Google Cloud Run once the prototype has been tested on live data.
