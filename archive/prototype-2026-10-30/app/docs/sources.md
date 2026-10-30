# Vacancy sources: what the providers' own documentation says

Each provider's official documentation and terms were read before its adapter was written. This file records the URL, the date it was read, limits, attribution and storage conditions. Where the documentation says nothing, we say so and explain the cautious choice we made instead. Where the documentation contradicts the build brief, we follow the documentation and note it.

## Tier A: automated, official and free

### Reed Jobseeker API

- **Docs:** https://www.reed.co.uk/developers/jobseeker (read 21 October 2026); index at https://www.reed.co.uk/developers.
- **Endpoints:** `GET https://www.reed.co.uk/api/1.0/search` and `GET https://www.reed.co.uk/api/1.0/jobs/{jobId}`.
- **Auth:** HTTP Basic, with the API key as the username and an empty password. The key is held in `.env` as `REED_API_KEY` and never logged.
- **Search parameters (documented):** `keywords`, `locationName`, `distanceFromLocation` (miles, default 10), `resultsToTake` (default and maximum 100), `resultsToSkip`, `employerId`, `employerProfileId`, `permanent`, `contract`, `temp`, `partTime`, `fullTime`, `graduate`, `postedByRecruitmentAgency`, `postedByDirectEmployer`, `minimumSalary`, `maximumSalary`.
- **Details fields (documented):** employer, title, HTML description, location, min/max salary, yearly min/max, currency, salary type (per hour/day/week/month/annum), contract type, job type, expiration date, external URL and the reed.co.uk URL. Hidden salaries come back empty, and an unknown id returns a blank job.
- **Observed, not documented:** search rows also carry `date`, `applications`, and a `locationName` that is often a full postcode without a space ("B46AR"). Detail rows carry `datePosted`, `salary` (display text), `partTime`/`fullTime`. Dates are `dd/mm/yyyy`.
- **Rate limits:** **none documented.** The developer page states no quota. We cap ourselves at about 1 request per second and 1,500 requests per run, back off exponentially on 429/5xx, and cache responses on disk by URL (`data/cache/`, git-ignored, 20-hour lifetime).
- **Attribution:** **none documented.** We credit every Reed job "Jobs from Reed.co.uk" and link each card to the job's reed.co.uk URL, where the user applies.
- **Storage and reuse:** **no API-specific terms found.** The developer pages link to no API terms. Reed's website terms (https://www.reed.co.uk/terms, read 21 October 2026) say material may be copied "for your own private or domestic purposes" and that "no copying for any commercial or business use is permitted". SkillMatch is a non-commercial education project. To stay well inside that:
  - vacancy data is never committed to git or published as a dataset. The SQLite file is a build artefact, rebuilt nightly and baked into the container;
  - the app shows Reed's own title, employer, location and salary. It shows only short evidence sentences from the description, each beside its requirement, never the full description, and always links back to Reed;
  - expired jobs are dropped on every refresh.
  - **Open question for the team:** ask Reed (via the developer page contact) whether this use is acceptable before any public launch.
- **Brief vs docs:** the brief's description of the endpoints, auth and limits matches the docs. The docs' own example URL has a typo ("loc ationName"); the live API accepts `locationName`, which we verified on 21 October 2026.

### Employer boards on Greenhouse

- **Docs:** https://docs.greenhouse.io/job-board.html (read 21 October 2026; the old developers.greenhouse.io URL redirects there).
- **Endpoint:** `GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true`. The docs say: "Job Board data is publicly available, so authentication is not required for any GET endpoints."
- **Fields:** `id`, `title`, `updated_at`, `location.name`, `absolute_url`, `metadata`; with `content=true` also `content` (HTML, entity-escaped, so we unescape it), `departments`, `offices`. Live responses also carried `first_published` and `company_name`.
- **Limits, attribution, storage:** none documented. We fetch each board once per run through the same polite client and link every card to the employer's own posting.
- **Employers:** Gymshark and Monzo, from the team's source register (`access_status: employer_ats_documented_public_route`). Both returned 200 on 21 October 2026 (`data/employer_boards.csv`, `confirmed = true`). We keep only UK postings; the ETL then keeps West Midlands and UK-remote ones.

### Employer boards on Lever

- **Docs:** https://github.com/lever/postings-api (read 21 October 2026).
- **Endpoint:** `GET https://api.lever.co/v0/postings/{site}?mode=json`, with an EU instance at `api.eu.lever.co`. An API key is documented only for posting applications, which we never do.
- **Fields:** `text` (title), `categories.location`/`allLocations`, `workplaceType` (on-site/remote/hybrid/unspecified), `country` (ISO code), `hostedUrl`, `description`, `lists` (requirement and benefit sections), `additional`, `createdAt`.
- **Limits:** only for application POSTs (2 per second). None documented for GET. **Terms:** the README notes published postings are public; it gives no reuse terms. We link to `hostedUrl`.
- **Employer:** Kpler (confirmed 200 on 21 October 2026). We keep `country = GB` only.

### Employer boards on Workable

- **Docs:** https://help.workable.com/hc/en-us/articles/115012771647-Using-the-Workable-API-to-create-a-careers-page (read 21 October 2026).
- **Endpoint:** the help article lists public endpoints `https://www.workable.com/api/accounts/{subdomain}?details=true` (descriptions included), `/locations` and `/departments`. The brief's `apply.workable.com/api/v1/widget/…` route appears only in third-party write-ups, so **we follow Workable's own documentation** and use `www.workable.com/api/accounts/{subdomain}`.
- **Fields (observed):** `title`, `shortcode`, `country`, `city`, `state`, `telecommuting`, `url`, `published_on`, `created_at`, `description`.
- **Limits, terms:** none stated for the public endpoint.
- **Employer:** Biffa (confirmed 200 on 21 October 2026).

### We Work Remotely

- **Docs:** https://weworkremotely.com/remote-job-rss-feed. The page returned 403 to our documentation fetcher on 21 October 2026. Its wording is recorded in the team's register (checked 16 October 2026): the feed is open to use, with links attributed back to We Work Remotely.
- **Feed:** `https://weworkremotely.com/remote-jobs.rss` (200 on 21 October 2026 with our honest User-Agent). The category feed URLs now redirect, so we use the all-jobs feed and keep data/analyst titles only.
- **Fields:** `title` ("Company: Role"), `link`, `region`, `country`, `category`, `type`, `description`, `pubDate`.
- **Attribution:** every card says "Job via We Work Remotely" and links to the job on weworkremotely.com.
- **UK eligibility:** "yes" when the item's region/country names the UK or says "Anywhere in the World"; otherwise "unclear".

### Remote OK

- **Docs/terms:** the first element of https://remoteok.com/api is its legal notice (read 21 October 2026): "Please link back (with follow, and without nofollow!) to the URL on Remote OK and mention Remote OK as a source, so we get traffic back from your site. If you do not we'll have to suspend API access." Its logo needs written permission; its name may be used.
- **What we do:** each card links to the job's remoteok.com URL as a normal followed link, says "Job via Remote OK" and never shows their logo.
- **Salary:** Remote OK's `salary_min`/`salary_max` may be platform estimates, so we never show them ("never estimate").
- **UK eligibility:** "yes" for UK/worldwide locations, "unclear" for "Europe", "EMEA" and the like (the team's research says these are not enough on their own).

### CV-Library (disabled)

- **Terms page:** https://www.cv-library.co.uk/aff-terms-conditions.html returned **403** to our documentation fetcher on 21 October 2026. We did not try to get round it. The conditions we implement come from the build brief and the team's research notes and are **unverified** against the page: refresh at least every 24 hours; show CV-Library's title, salary, company and location unaltered (kept separate from our parsed fields); every click goes to cv-library.co.uk; don't pass the jobs to LinkedIn, Indeed, Google for Jobs or DWP.
- **Status:** a disabled stub until the partner team supplies the feed URL (`CVLIBRARY_FEED_URL`). Affiliate ID 107834. The sources page shows "Register with CV-Library": https://www.cv-library.co.uk/register?id=107834.

## Geography: postcodes.io

- **Docs:** https://postcodes.io/ and https://postcodes.io/docs/overview (read 21 October 2026). "No authentication is required to use this API." No rate limit is documented. Data come from the ONS Postcode Directory and OS Open Names (Open Government Licence). We credit: *Contains OS data © Crown copyright and database right; contains Royal Mail data © Royal Mail copyright and database right; source: Office for National Statistics.*
- **Verified live on 21 October 2026:** `/postcodes/{postcode}` returns `region` ("West Midlands"). `/places?q=` **also returns `region`**, so reverse geocoding is only a fallback when it is missing. `/outcodes/{outcode}` returns coordinates and districts but **no region**.
- **Privacy:** a user's home is placed using the outward code only ("B91"). The profile form strips the inward part in the browser, so only the outward code reaches our server. The server sends only that to postcodes.io, or uses the offline table and sends nothing.
- **Offline fallbacks (committed):** `data/town_coords.csv` (72 places, built from `/places`) and `data/outcode_coords.csv` (230 West Midlands outward codes, built from `/outcodes`) by `scripts/build_geo_reference.py`. Names that clash ("Dudley" is also in North Tyneside) resolve to the West Midlands place.

## Tier B: hand-curated adverts

`data/curated/adverts.csv`, checked with `python -m skillmatch.curate validate`. It stores only the fields listed in the brief and a requirement list in our own words. It ships empty; `data/curated/adverts.example.csv` shows the format.

## Tier C: discovery links

`data/discovery_links.csv` (87 sources) is built from the team's source register by `scripts/build_discovery_links.py`. 15 have a pre-filled search link whose pattern comes from the register's own example URL or a standard query string. Parameters we could not confirm are marked "assumed, check it" in the notes column. The rest link to the source's search page and say so. No data is collected from any of them.

## Excluded

- **Adzuna:** the free key is evaluation-only; organisational use needs a licence.
- **Jooble, Indeed, LinkedIn and other boards:** no open API route for this use. Indeed and LinkedIn appear only as Tier C links.
