# SkillMatch vacancy data for analysis

Read this data from branch **`data-snapshots`**, in **`data/live_snapshots/`**. The app code is maintained separately on the app development branch; this branch delivers analysis data.

Every collection adds a new snapshot folder. History is rebuilt from the retained snapshots. Earlier history versions stay in the working app and are never exported to this repository. A reprocessed historical collection is labelled explicitly and retains its original collection date. Scheduled daily collection is planned; it is not enabled in this first delivery.

## First delivery

| Folder | Collection | Observations | Distinct source IDs | Shown |
|---|---|---:|---:|---:|
| `20261027_1246_recovered/` | Live collection on 27 October, recovered from saved raw files and search pages | 24,598 | 5,554 | 86 |
| `20261021_2033_reprocessed/` | 21 October stored collection, reprocessed with current filters | 2,790 | 2,790 | 75 |

The 27 October collection contains 5,042 distinct Reed IDs from 24,070 search observations. Overlapping towns and terms return the same advert repeatedly; those observations remain in the data with a duplicate outcome. The other sources are Greenhouse, Lever, Workable, Remote OK and We Work Remotely.

## Files inside each snapshot

| File | Use |
|---|---|
| `shown.csv` | Adverts eligible to appear in the app before personal profile matching |
| `dropped.csv` | Every other collected observation, with one primary outcome, an optional note, and duplicate links |
| `skills.csv` | One vacancy–skill row; essential/desirable/unclear strength, extraction confidence and description coverage |
| `funnel.csv` | Per-source counts: collected equals the sum of all mutually exclusive outcomes |
| `source_log.csv` | Source status, request evidence and failures; these events are not vacancies |
| `search_terms_yield.csv` | Per-term observations, first-attributed distinct IDs, matched distinct IDs and shown canonical matches |
| `run.json` | Original collection timing, search settings, rule/taxonomy fingerprints, processing provenance and request counts |
| `README.md` | Column definitions and the limitations specific to that snapshot |

Use `vacancy_id` to join skills to vacancy rows. It is stable as `source:source_id`. Use `observation_id` to distinguish repeated query hits within a run. Use a distinct vacancy ID or the retained `duplicate_of` ID when counting adverts, rather than treating every query hit as a separate job. A duplicate may also fail an eligibility rule; `eligibility_reason` retains that information separately from its primary duplicate outcome.

## Primary outcomes

`shown`; `outside area`; `overseas-only remote`; `senior`; `needs professional qualification`; `training or fake advert`; `not a data role`; `expired`; `duplicate of an advert from another source`; `duplicate within the same source`; `other` (with a note).

Duplicate rows identify the retained source and vacancy ID. Source failures are logged separately and are never counted as collected vacancies. Unknown locations remain explicit rather than being assumed to be in the West Midlands. UK-remote adverts are retained; check their location and eligibility information in the app or original advert.

## Description coverage and skills

`description_coverage` is `full`, `search excerpt only`, or `unavailable`. Only 149 distinct Reed adverts passed the 27 October search filters; all 149 had full descriptions saved. The 21 October retained Reed data has 85 full descriptions and 2,480 search excerpts. Skills extracted from an excerpt are less complete than skills extracted from a full advert. A missing skill row does not mean that the employer did not ask for that skill. Extraction confidence is `stated` or `inferred`, not a model accuracy percentage.

The vacancy CSVs contain metadata and links back to the original adverts. They contain no full advert text, API credentials, database files or personal applicant profiles. Salary amounts have a currency and period where supplied; do not combine hourly, daily and annual amounts without an explicit conversion method.

## History

`history/adverts_history.csv` has one row per vacancy ID: `first_seen`, `last_seen`, distinct-run `times_seen`, `latest_outcome`, and `sources_seen` (including a linked duplicate winner's source where available). The first delivery contains 6,438 IDs; 1,906 were seen in both collections.

`history/daily_changes.csv` records each run's source-level new, gone and still-live counts, comparison completeness and observed days listed for missing adverts. Blank counts mean a comparison is not supported; they do not mean zero. “Gone” means absent from a comparable sample, not that a vacancy was filled. `first_seen` and `last_seen` bound observations, not continuous availability.

## Limitations and provenance

The full limitations and definitions live in each snapshot's `README.md` and `run.json`.

- There are only two collection dates in this delivery. The 21 October folder is a reprocessed retained subset, not a newly collected sample; the old database had already omitted some records.
- Search settings changed from 16 centres/15 miles/23 terms to five centres/27 miles/48 terms. The two collections cannot establish a market trend or an unbiased new/gone rate. Today's change comparison is therefore marked non-comparable.
- Sixteen 27 October searches filled their final permitted page. Search results are bounded samples, not a census of all vacancies or agency coverage.
- Older posting weeks undercount because collection began later. `posted_week` is the ISO week of the advert's posting date, not the week SkillMatch collected it.
- Recovery and historical reprocessing each used zero network requests. The original 27 October files evidence 376 successful Reed search responses and 149 detail responses (525). The exact original retry/attempt count was not persisted, so this is a successful-response count and lower bound, not an exact attempt total. Future live attempts are journalled durably before each request.
- Shown adverts are a candidate pool, not a guarantee that every graduate meets every requirement. The app explains personal skills and experience gaps.

## Producing later deliveries

From the working app, run `make export-snapshot TARGET=/path/to/export-folder` with your own destination. The exporter copies new snapshot folders and the two current history CSVs. It skips identical snapshots and refuses conflicting immutable files. Any backup made before refreshing a history CSV stays in the working app; `history/versions/` is never exported. Publication to this branch is a separate reviewed step.
