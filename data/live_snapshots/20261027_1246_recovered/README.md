# Collection snapshot 20261027T124644998193Z

This recovers the interrupted 27 October 2026 live collection from saved raw records and cached search pages. Recovery made zero network requests. The original successful Reed response count is reconstructed from saved files; the original exact attempt/retry count was not persisted and is unavailable.

This folder is an append-only export for one collection run. No advert descriptions, requirement evidence, or serialized source extras are included. Every CSV includes `run_id`.

## Files and columns

- `shown.csv`: one row for each observation whose outcome is `shown`.
- `dropped.csv`: all other observations, including repeated search occurrences and duplicate listings. `duplicate_of` and `duplicate_source` identify the retained advert where known.
- Both vacancy files use: `run_id`, `observation_id`, stable `vacancy_id`, `source`, `source_id`, `title`, `employer`, `location_text`, `postcode`, `region`, `is_remote`, salary fields, `posted_date`, ISO `posted_week` (`YYYY-Www`), `expiration_date`, `description_coverage`, `collected_at`, `link`, `outcome`, `outcome_note`, `eligibility_reason`, `duplicate_of`, `duplicate_source`, `search_term`, and `search_location`. Empty values mean unavailable or not applicable. `vacancy_id` is the stable source plus source ID; `observation_id` identifies one occurrence in this run. Repeated observation rows are retained, so observation counts may exceed unique vacancy counts.
- `collected_at` is when SkillMatch observed the row; `posted_date` and `posted_week` come from the source and can be older. `is_remote` records whether the source/pipeline treated the role as remote. `salary_min` and `salary_max` are the source's stated numeric range in `currency` and `salary_period`; periods such as annum, day, hour, week, or month are not converted or compared. `outcome_note` explains an `other` outcome; duplicate outcomes use `duplicate_of` and `duplicate_source` to identify the retained listing.
- `skills.csv`: one row per unique vacancy and skill tag; columns are `run_id`, `vacancy_id`, `skill`, `strength`, `confidence`, and `description_coverage`. Strength is `essential`, `desirable`, or `unclear`. Coverage is `full`, `search excerpt only`, or `unavailable`, taken from the best observation for that vacancy. Missing skill rows do not mean the advert has no skills.
- `funnel.csv`: source-level `collected` and mutually exclusive counts for each outcome in the outcome list below. It omits the aggregate `ALL` row. A source failure is recorded in `source_log.csv`, never counted as a vacancy.
- `source_log.csv`: `run_id`, `source`, optional `source_id` (ties a detail failure to an advert), `at`, `status`, `error_type`, `board`, `note`, `count`, `requests`; errors and source events are not vacancies.
- `search_terms_yield.csv`: includes configured terms even when they return zero results. Per term, `collected_observations` counts search occurrences; `first_attributed_new` assigns each vacancy to only its first term in observation order; `matched_distinct` counts distinct vacancy IDs returned for that term; `shown_across_match` counts distinct IDs that were shown anywhere in the run and also matched that term, including when this term's occurrence was later classified as a duplicate.
- `run.json`: run identifier and allowlisted run metadata (source names, search settings, versions and timing where supplied).
- `README.md`: this file.

## Outcomes

shown, outside area, overseas-only remote, senior, needs professional qualification, training or fake advert, not a data role, expired, duplicate of an advert from another source, duplicate within the same source, other.

## Limitations

Older posting weeks undercount because collection began later. Search results may be partial when request limits or source failures interrupt a run. Missing skill rows do not establish that a skill is absent. `description_coverage` reports whether parsing had a full description, only a search excerpt, or no text; always follow the source link and read the advert before applying.

## Export counts

{"dropped": 24512, "observations": 24598, "shown": 86, "skills": 1538, "sources_logged": 6}
