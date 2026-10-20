# Task E — integration, validation, and demo

## Purpose

This is likely to be the trickiest phase of the project: the source research, user journey, data, matching rules, analysis, and code must all work together. The purpose is to bring those pieces into one working app and analysis, test them against known cases, catch and record problems, and make sure the team can run the project and repeat the demo reliably. Start connecting and checking pieces while they are being built; do not leave integration, testing, and demo preparation until the final hours. The demo should show what works and be clear about the limits of the sample and the app.

**Owner:** __________  **Reviewer:** __________  **Rotating hat today:** __________

## During the build

- Keep a shared task board with owner, status, next action, and blocker. Use a short daily stand-up and end-of-day review.
- Keep the selected sample and its provenance in one known format; record any changed or removed row and why.
- Connect source evidence, fields, matching decisions, and screen labels. If a rule changes, update the example result and the acceptance checks.
- Ask each workstream owner to share a short handover: decision made, evidence, open issue, and what the builder needs next.
- Make Phil's coding/integration time visible if he is the main coder; teammates can actively reduce uncertainty, supply reviewed sample records, test flows, review rules, and prepare the analysis story.

## Core acceptance checks

| Area | Check | Pass evidence |
|---|---|---|
| Source traceability | Every displayed vacancy has source, link, and checked date | Open one or more results and trace each back to its evidence |
| Data handling | Missing values remain unknown; duplicates and stale/closed rows are labelled | Inspect the sample table and demonstrate a missing/duplicate case |
| Geography | West Midlands workplace and UK-remote evidence are handled separately | Show one local/hybrid and one remote or unresolved example |
| Early-career suitability | Classification follows advert requirements and carries a reason | Explain one plausible, one stretch, and one excluded/unresolved case |
| Skills | Required matches and gaps are distinguishable from desirable matches and course coverage | Use a known candidate and show the supporting advert wording |
| UX | A user can find a role and explain why it appeared | A teammate completes the agreed short task without coaching |
| Travel/privacy | No unsupported commute claim; no real personal data in the repo/demo | Check the app and repository contents used for the presentation |
| Analysis | One chart/count is reproducible and scoped to the reviewed sample | Recompute from the sample and display its denominator/limitations |
| Run/deployment | The chosen demo route starts from documented steps | A teammate follows the run instructions on the intended setup |

## Minimum scenario set

Use fictional candidate profiles and the reviewed/synthetic dataset approved for the demo.

1. Candidate has the required skills and meets stated location constraints: result explains why it appears.
2. Candidate has a required-skill gap but matches desirable skills: result distinguishes the two.
3. Vacancy title sounds junior but experience requirements do not: it is not silently labelled a clear entry role.
4. Hybrid job requires office attendance beyond the candidate's stated travel preference: the constraint is visible.
5. Remote advert has no proof of UK eligibility: it stays unresolved or out of the eligible shortlist.
6. Salary is missing or ambiguous: no value is estimated.
7. Duplicate, closed, or stale vacancy appears: it is handled visibly and does not inflate unique opportunities.
8. Candidate skips location/travel information: the app avoids a fabricated journey claim and shows what remains unknown.

Record **pass / fail / not tested**, the evidence, and any owner for a fix. A not-tested item is not a pass.

## Demo path

Prepare a short, repeatable path that works without improvising:

1. State who SkillMatch is for and the narrow sample being shown.
2. Enter or select the fictional candidate profile and preferences.
3. Open one plausible result and explain a match, a gap, and the role evidence.
4. Compare a stretch/unresolved case and show how uncertainty is handled.
5. Show one sample-level analysis finding and explain the denominator and coverage limits.
6. Show where source, checked date, and run instructions live; close with the next decision or limitation.

## Three-day versus four-day finish

- **Four days:** spend Day 3 on integration, usability feedback, and data-quality repairs; freeze new features late Day 3. Day 4 is for regression checks, documentation, and rehearsal.
- **Three days:** time-box the investigation to the morning of Day 1, complete a vertical slice on Day 2, then stop adding features by Day 3 morning. Reserve the rest of Day 3 for checks, README, and rehearsal.

## Final handover checklist

- [ ] Decision log reflects the choices actually used in the demo.
- [ ] Project README explains the app's purpose, how to run it, sample/source provenance, and limitations.
- [ ] The sample analysis does not claim to represent the whole job market.
- [ ] The demo uses no real candidate personal data or unapproved source content.
- [ ] One teammate other than the main coder can follow the run steps.
- [ ] Contributions and remaining questions are captured for the next team session.
