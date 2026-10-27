# Data dictionary

Use `vacancy_id` to count adverts. The same advert can appear in more than one row when it appears in several searches.

## shown.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `observation_id` | ID for this appearance in a search. |
| `vacancy_id` | Stable advert ID, made from the source and its ID. |
| `source` | Job site or advert source. |
| `source_id` | Advert ID used by the source. |
| `title` | Job title. |
| `employer` | Employer named in the advert. |
| `location_text` | Location as written by the source. |
| `postcode` | Postcode, when available. |
| `region` | Region assigned to the advert. |
| `is_remote` | Whether the advert says the job is remote. |
| `salary_min` | Lowest salary amount, when given. |
| `salary_max` | Highest salary amount, when given. |
| `salary_period` | Whether pay is yearly, monthly, daily, hourly or another period. |
| `salary_text` | Salary text as shown by the source. |
| `currency` | Currency used for the salary. |
| `posted_date` | Date the source says the advert was posted. |
| `posted_week` | Week the advert was posted. |
| `expiration_date` | Advert closing date, when available. |
| `description_coverage` | Whether the full advert, a short summary or no description was available. |
| `collected_at` | When SkillMatch collected this advert. |
| `link` | Link to the original advert. |
| `outcome` | Whether the advert was kept or why it was dropped. |
| `outcome_note` | Extra explanation when the outcome is `other`. |
| `eligibility_reason` | Another filter reason when the main outcome is a duplicate. |
| `duplicate_of` | ID of the advert kept instead of this duplicate. |
| `duplicate_source` | Source of the advert kept instead of this duplicate. |
| `search_term` | Search words that found this advert. |
| `search_location` | Place used in the search. |

## dropped.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `observation_id` | ID for this appearance in a search. |
| `vacancy_id` | Stable advert ID, made from the source and its ID. |
| `source` | Job site or advert source. |
| `source_id` | Advert ID used by the source. |
| `title` | Job title. |
| `employer` | Employer named in the advert. |
| `location_text` | Location as written by the source. |
| `postcode` | Postcode, when available. |
| `region` | Region assigned to the advert. |
| `is_remote` | Whether the advert says the job is remote. |
| `salary_min` | Lowest salary amount, when given. |
| `salary_max` | Highest salary amount, when given. |
| `salary_period` | Whether pay is yearly, monthly, daily, hourly or another period. |
| `salary_text` | Salary text as shown by the source. |
| `currency` | Currency used for the salary. |
| `posted_date` | Date the source says the advert was posted. |
| `posted_week` | Week the advert was posted. |
| `expiration_date` | Advert closing date, when available. |
| `description_coverage` | Whether the full advert, a short summary or no description was available. |
| `collected_at` | When SkillMatch collected this advert. |
| `link` | Link to the original advert. |
| `outcome` | Why the advert was dropped. |
| `outcome_note` | Extra explanation when the outcome is `other`. |
| `eligibility_reason` | Another filter reason when the main outcome is a duplicate. |
| `duplicate_of` | ID of the advert kept instead of this duplicate. |
| `duplicate_source` | Source of the advert kept instead of this duplicate. |
| `search_term` | Search words that found this advert. |
| `search_location` | Place used in the search. |

## skills.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `vacancy_id` | Advert this skill belongs to. |
| `skill` | Skill named in the advert. |
| `strength` | Whether the advert calls the skill essential, desirable or unclear. |
| `confidence` | How clearly the skill was stated. |
| `description_coverage` | Whether the full advert, a short summary or no description was available. |

## funnel.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `source` | Job site or advert source. |
| `collected` | Number of advert appearances recorded for this source. |
| `shown` | Appearances that passed the filters. |
| `outside area` | Appearances outside the search area. |
| `overseas-only remote` | Remote appearances that cannot be worked from the UK. |
| `senior` | Appearances for senior or lead roles. |
| `needs professional qualification` | Appearances that require a professional qualification. |
| `training or fake advert` | Appearances that are courses or misleading adverts. |
| `not a data role` | Appearances outside the data job scope. |
| `expired` | Appearances for adverts that had expired. |
| `duplicate of an advert from another source` | Appearances duplicated on another source. |
| `duplicate within the same source` | Repeated appearances from the same source. |
| `other` | Appearances dropped for another stated reason. |

## source_log.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `source` | Job site or advert source. |
| `source_id` | Advert ID, when the log entry relates to one advert. |
| `at` | When the source event was recorded. |
| `status` | Whether the source worked, partly worked or failed. |
| `error_type` | Short name for an error, if one happened. |
| `board` | Careers board involved, when available. |
| `note` | Short explanation of the source event. |
| `count` | Number of items covered by the event, when available. |
| `requests` | Number of recorded requests for the event. |

## search_terms_yield.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `search_term` | Words used to search. |
| `collected_observations` | Number of search appearances found by these words. |
| `first_attributed_new` | Distinct adverts first found by these words. |
| `matched_distinct` | Distinct adverts found by these words. |
| `shown_across_match` | Distinct adverts kept that matched these words. |

## history/adverts_history.csv

| Column | What it means |
|---|---|
| `vacancy_id` | Stable advert ID. |
| `first_seen` | First collection date when this advert appeared. |
| `last_seen` | Most recent collection date when it appeared. |
| `times_seen` | Number of collections that included this advert. |
| `latest_outcome` | Most recent keep or drop reason. |
| `sources_seen` | Sources where this advert or its duplicate appeared. |

## history/daily_changes.csv

| Column | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `run_date` | Date of the collection. |
| `source` | Job site or advert source. |
| `new` | Distinct adverts not seen in the previous comparable collection. |
| `gone` | Distinct adverts missing from the previous comparable collection. |
| `still_live` | Distinct adverts seen in both comparable collections. |
| `completeness` | Whether the source collection was complete enough to compare. |
| `comparable` | Whether the two collections can be compared fairly. |
| `days_listed_gone_mean` | Average days listed for adverts that disappeared. |
| `days_listed_gone` | Days listed for each advert that disappeared. |

## run.json

| Field | What it means |
|---|---|
| `run_id` | ID for this collection. |
| `started_at` | When the collection started. |
| `finished_at` | When collection finished. |
| `snapshot_date` | Date used to label this collection. |
| `data_mode` | Whether this was live, fixture, recovered or reprocessed data. |
| `sources` | Sources included in the run. |
| `source_status` | Whether each source worked, partly worked or failed. |
| `requests_made` | Recorded requests made during the run. |
| `reed_requests` | Recorded Reed requests. |
| `search_settings` | Search places, words, page limits and related settings. |
| `filter_version` | Version of the rules used to keep or drop adverts. |
| `taxonomy_version` | Version of the skill list used. |
| `code_commit` | App revision used for the run, when available. |
| `working_code_fingerprint` | Short check value for the working app code. |
| `code_has_uncommitted_changes` | Whether app files had unsaved Git changes. |
| `history_limitations` | Known limits when comparing this run with earlier runs. |
| `request_summary` | Notes about what the request totals include. |
| `original_collection_at` | Original start time for recovered or reprocessed data. |
| `original_collection_finished_at` | Original finish time, when known. |
| `processing_mode` | How the collected records were prepared. |
| `reprocessed_from` | Saved source used to rebuild an older collection. |
| `recovered_from` | Saved source used to recover an interrupted collection. |
| `prior_successful_reed_requests` | Successful Reed replies found in saved files. |
| `prior_request_count_basis` | Note explaining what the earlier Reed request count includes. |
| `collection_complete` | Whether all planned searches finished. |
| `raw_source_files` | Names of saved source files used for recovery. |
| `recovery_network_requests` | New requests made while recovering a run. |
| `collection_counts` | Summary counts for records and searches. |
| `processing_finished_at` | When record processing finished. |
| `agency_coverage` | Notes about agencies already covered by other sources. |

## Technical notes

`description_coverage` is `full`, `search excerpt only` or `unavailable`. A missing skill row does not mean the advert did not ask for that skill. Funnel counts are search appearances; one advert can appear more than once. Blank history comparisons mean there is not enough evidence to compare, not zero. “Gone” means missing from the next comparable collection, not confirmed filled. Dates only bound when SkillMatch saw an advert; they do not prove it was available every day between collections.

Run details include source settings and processing history. Fingerprints are short checks of the code and rule files used; they are not security signatures. Request totals can count saved successful responses or recorded attempts; use the request notes to see which. To export from the working app, run `make export-snapshot TARGET=your-folder`. The export adds new snapshot folders and refreshes the current history files.
