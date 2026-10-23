# SkillMatch backlog

Started 21 October 2026, after the first full build. Phil's notes and review findings.

## Team tasks (people, not code)

| Task | What to do | Owner | Status |
|---|---|---|---|
| Chase CV-Library | Phil emailed Matt Lees (Partner Manager) on 21 Oct asking for the XML jobs feed URL for affiliate ID 107834. If no reply by Fri 23 Oct, phone 01252 810995. Ask: feed URL, can it be filtered to data/IT roles in the West Midlands, fetch limits, can cached adverts feed anonymous skill counts. | Team | Waiting |
| Confirm Reed terms | Reed publishes no reuse, storage or attribution rules for API data, and its website terms forbid copying "for any commercial or business use". Email Reed and confirm that a non-commercial course project may cache API adverts for up to 24 hours, show them with links back, and publish anonymous counts. Get the answer in writing. | Team | To do |
| Review the taxonomy | Work through the ten entries in FINAL_REPORT.md using docs/taxonomy_review_guide.md. People from health, retail, hospitality and teaching check the role archetypes against what their old jobs really involved. | Team | To do |

## Filters

- **Loosen the relevance filter for analyst roles.** Finance-flavoured analyst jobs (Revenue Analyst, Junior Finance Analyst, Technical Support Analyst, supply chain and planning analysts) are being hidden as "not a data role". Career changers can apply for many of these. Keep them, possibly labelled "adjacent analyst role".
- **Bullshit filter: run an analysis daily.** A lot of recruitment adverts aren't real jobs: agencies fishing for CVs or clients, and training companies selling courses dressed up as vacancies. The current training-course filter caught 64. Each nightly snapshot should be kept (counts and IDs, not full text) so these signals can be measured over time:
  - the same job reposted again and again, or live for months;
  - near-identical adverts from several agencies;
  - vague employer ("our client", "a leading company");
  - very wide salary ranges (e.g. £30,000–£52,000) or salary "up to" only;
  - no specific town, or a whole county;
  - "send your CV for future opportunities", "talent pool", "register your interest";
  - fees, "course", "funded training", "guaranteed interview", "job guarantee" (training sellers);
  - agency adverts versus direct-employer adverts (Reed's postedByRecruitmentAgency / postedByDirectEmployer search parameters can label these).
  Turn the signals into a "suspect advert" score. Show suspect adverts in a hidden group like the senior ones, and report the share in the insights page and notebook.

## Unrecognised requirements (the 17%)

These are the advert lines the parser can't link to a skill or competency. Two kinds:

1. **Niche software and tools** (a particular ERP, CRM or industry package). Policy: ignore them. They don't count for or against a match. Entry-level candidates can't be expected to know every vendor's package.
2. **Professional qualifications** such as ACCA (Association of Chartered Certified Accountants, a multi-year accountancy qualification), CIMA, CIPD, PRINCE2. Decided 21 Oct: out of scope for a 16-week bootcamp graduate. If an advert **requires** one, hide the job (excluded_reason = "needs a professional qualification", kept and revealable like senior roles). If it's only desirable, ignore it.

## Matching problems found in review

- **Strong fits driven by soft skills alone.** "Business Intelligence Engineer" (Green Square) came out as a Strong fit for the ex-kitchen manager, despite the advert asking for an experienced BI professional, strong SQL, Azure Data Factory and data-warehouse modelling. Causes:
  - requirements without a cue word are "inferred" and never count as gaps, so technical demands slip through;
  - "experienced BI professional" isn't recognised as a data-experience demand.
  Fix: inferred technical requirements count as gaps; phrases like "experienced [data/BI/analytics] professional" count as data-experience demand.
- **"Factory" triggers manufacturing sector knowledge** ("Azure Data Factory"). Add to not_phrases.
- **"Engineer" titles** (BI engineer, data engineer) are usually not entry roles for this cohort. Consider excluding unless "junior" or "graduate" is in the title.
- **Good fit is too big** (32 to 42 of 77 for every persona). Tighten after the fixes above.

## Design

Phil's verdict: clean and functional, but generic. Needs its own design language before the team sees it. See the review notes in chat on 21 Oct for the proposed direction.

Ideas (thinking out loud, not decided):
- Most of the cohort use laptops. Replace the very long profile page with a single page in tabs or steps (where you live, skills, past roles, check and go), so nothing needs endless scrolling.
- Skills as clickable chips with a tap to change level, instead of 17 identical dropdowns.
- Results: fit badge, matched/missing skill chips, pay and distance up front; optional map.
