# SkillMatch job data

Real job adverts collected by SkillMatch, for the data team to analyse.

## Start here

1. Open the newest dated folder.
2. Open `shown.csv`. These are the adverts a graduate would see.
3. Then look at `dropped.csv` to see what was filtered out, and why.

## The folders

Each folder is one collection. The name is the date and time it ran.

| Folder | What it is | Adverts collected | Adverts kept |
|---|---|---:|---:|
| `20261031_2309/` | Live collection from 31 October 2026 | 5,375 | 66 |
| `20261031_1301/` | Live collection from 31 October 2026 | 5,389 | 67 |
| `20261030_1848/` | Live collection from 30 October 2026 | 5,502 | 67 |
| `20261030_1324/` | Live collection from 30 October 2026 | 5,459 | 67 |
| `20261029_1350/` | Live collection from 29 October 2026 | 5,447 | 71 |
| `20261028_1651/` | Live collection from 28 October 2026 | 5,523 | 83 |
| `20261028_0856/` | Live collection from 28 October 2026 | 5,481 | 80 |
| `20261027_2232/` | Live collection from 27 October 2026 | 5,614 | 84 |
| `20261027_1701/` | Live collection from 27 October 2026 | 5,600 | 85 |
| `20261027_1246_recovered/` | Recovered 27 October live collection | 5,554 | 86 |
| `20261021_2033_reprocessed/` | Reprocessed 21 October collection | 2,790 | 75 |

`history/` tracks every advert across all runs: when it was first seen, last seen, and how many times.

New runs add new folders. Nothing is ever overwritten.

## What's in each folder

| File | What it holds |
|---|---|
| `shown.csv` | Adverts that passed every filter |
| `dropped.csv` | Everything else, with the reason it was dropped |
| `skills.csv` | The skills each advert asks for: essential, desirable or unclear |
| `funnel.csv` | The counts at a glance |
| `search_terms_yield.csv` | Which search words found which adverts |
| `source_log.csv` | How each job site behaved during the run |
| `run.json` | The settings used for the run (technical) |

What every column means: [data_dictionary.md](data_dictionary.md)

## Why adverts get dropped

- Not a data job
- Senior role
- Outside the West Midlands
- Overseas-only remote job
- Needs a professional qualification (ACCA and similar)
- A training course dressed up as a job
- The same advert listed twice
- Expired
- Other (missing details; the note says what)

## Watch out for

- **Repeats in `dropped.csv`.** The same advert often turns up in several searches. Count adverts by `vacancy_id`, not by rows.
- **Short summaries.** Some adverts only had a short summary, not the full text. The `description_coverage` column shows which. If a skill is missing, the employer may still have asked for it.
- **Changed settings.** The first two runs used different search settings. Don't read the difference between them as the job market changing.
- **Older weeks look quieter.** Adverts that were filled before we started collecting are missing. See the limitations notes in the repo.
- **Salaries.** Some are yearly, some daily or hourly. Check `salary_period` before comparing.

## Where it comes from

Reed, the Gymshark, Monzo, Kpler and Biffa careers sites, We Work Remotely and Remote OK. Every row links back to the original advert. We keep a summary, not the advert text.
