# Collection: 27 October 2026

This recovers the live collection from 27 October using files already saved.

## The numbers

- Adverts collected: 5,554
- Adverts kept (in `shown.csv`): 86
- Sources: Greenhouse, Lever, Reed, Remote OK, We Work Remotely and Workable

## Start here

Open `shown.csv`. Then `dropped.csv` for what was filtered out and why.

## Files

| File | What it holds |
|---|---|
| `shown.csv` | Adverts that passed every filter |
| `dropped.csv` | Everything else, with the reason |
| `skills.csv` | Skills each advert asks for |
| `funnel.csv` | The counts at a glance |
| `search_terms_yield.csv` | Which search words found what |
| `source_log.csv` | How each job site behaved |
| `run.json` | Settings used (technical) |

What every column means: [../data_dictionary.md](../data_dictionary.md)

## Notes on this run

- No new job-site requests were made during recovery.
- Some searches reached their last allowed page.
- Older posting weeks may be incomplete.
