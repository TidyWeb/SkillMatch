# Progress

Source of truth for where the build is. Re-read this and DECISIONS.md after any interruption.

## Milestones

- [x] 1. Skeleton: repo, uv project, Flask app factory, Makefile, pytest and ruff running, empty pages render
- [x] 2. Live Reed sample and docs/advert_patterns.md (180 adverts studied, 21 Oct 2026)
- [x] 3. Taxonomy files and validation (51 skills, 40 competencies, 40 archetypes)
- [x] 4. Fixtures modelled on real patterns (120 synthetic adverts, scripts/make_fixtures.py)
- [x] 5. ETL pipeline (fixtures and live), SQLite, quality report (live: 2,790 adverts on 21 Oct 2026)
- [x] 6. Parsing and matching, with tests (206 tests passing)
- [x] 7. Calibration on live data (before/after numbers in DECISIONS.md)
- [x] 8. Web pages: profile, results, job detail (tag v0.1); checked in Chrome at 380px and 1280px with live data
- [x] 9. Insights, sources, about pages (charts checked at 380px and 1280px)
- [x] 10. Analysis notebook (scripts/build_notebook.py --execute; outputs are aggregate counts only)
- [x] 11. Docker image (151 MB, verified with Podman), GitHub Actions workflows, deployment docs
- [x] 12. README, remaining docs, self-check, final report (FINAL_REPORT.md)

## Now

All twelve milestones are complete (21 October 2026). See FINAL_REPORT.md.

## Next (for the team)

- Review the taxonomy (docs/taxonomy_review_guide.md, ten entries listed first).
- Fill the "AI-assisted interpretation" cell in the notebook.
- Ask Reed to confirm the API reuse; chase CV-Library for the feed URL.
- One-time Google Cloud setup (docs/deploy.md), then push from this staging repo when approved.
- Capture README screenshots from a fixtures build.

## Notes for resuming

- Live DB at data/processed/skillmatch.db (77 shown adverts, 21 Oct 2026). Re-runs use the 20-hour HTTP cache in data/cache/.
- The dev server caches templates unless started with `--debug`.
- Don't `pkill -f` with a pattern that appears in your own command line (it kills the shell); use a bracket trick such as `create_ap[p]`.
