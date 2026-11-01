# SkillMatch presentation: full script

Monday 2 November. About 19 minutes, then questions.

This is a guide, not a script. Each speaker uses their own words, and is free to add detail, examples and personal experience.

## Running order

| # | Who | Topic | Min |
|---|---|---|---|
| 1 | Oana | Introduction | 2 |
| 2 | Phil | The SkillMatch app | 5 |
| 3 | Phil | GitHub: how we worked | 2 |
| 4 | Esmat | LinkedIn guide | 2 |
| 5 | SK | Tailor my CV | 3 |
| 6 | John | Data analysis: what the search found | 3 |
| 7 | Oana | Data analysis: who advertises, pay, the test, what next | 2 |
| | | Total | 19 |

---

## 1. Oana: Introduction (2 min)

- SkillMatch was Oana's idea.
- The problem: a Code Institute graduate searching for a first data job gets a blizzard of adverts, most not meant for them.
- Most of us are career changers. We have years of skills, but no years in a data role.
- So SkillMatch matches on transferable skills, not job titles.
- Free, no login, West Midlands first.
- It started as a job finder and grew into five things: the app, a GitHub guide, a LinkedIn guide, Tailor my CV, and a data analysis.
- Five people, hackathon 26 to 30 October.
- Hand over: "Phil will show how the app works."

## 2. Phil: The SkillMatch app (5 min)

- Who it is for: graduates moving into data. The hosted app runs on Google Cloud Run.
- What you do (live or screenshots):
  - Say where you live and how you travel.
  - Pick up to 5 areas of expertise. These map to transferable skills. No job titles.
  - Code Institute skills are assumed for everyone. Extras are added from a dropdown.
- What you get: small cards. Open one for the detail.
  - Match level on each card.
  - Every requirement gap is flagged, so the match is explained, not a black box.
- How the matching works:
  - Plain local Python rules. No paid AI service writes the matches.
  - Senior roles and unrelated jobs are filtered out. A second check runs on the first pass's output.
- Where the adverts come from:
  - A daily collection on GitHub Actions from Reed's official API and documented feeds.
  - Each run adds a dated snapshot. History grows and is never overwritten.
  - CV-Library is switched off until we have access.
- Privacy:
  - No login. Your profile stays in your browser tab. Nothing is stored on the server.
- One style across everything: Navy A.
- The card's "Tailor my CV" button leads into the next sections.
- Be honest about limits: one captured sample, not the whole market. Reed's results were partial. Travel time between home and job is not built.
- Backup if the live app is slow: screenshots in `docs/screenshots/` in the repo.
- Hand over: "Now how we worked as a team on GitHub." (Phil continues.)

## 3. Phil: GitHub, how we worked (2 min)

- One repo, TidyWeb/SkillMatch: the app, the website, the guides, the team folders.
- Collected data sits on its own branch, data-snapshots, away from the code.
- A project board: chapters, MoSCoW priorities, user stories, cards linked to each other.
- Nothing goes into main without a pull request and a review. Main is protected: one approval, and Phil merges.
- Checks run on every pull request: code style, fictional test data, and the tests.
- The daily advert collection is automated on GitHub Actions.
- A shared work log records what each person or AI tool did.
- Lesson learned: the board drifted behind merged work. Fix: link every pull request to its issue with "Closes #number".
- AI use, stated plainly: Claude and Codex helped with planning, code, review and checks. The team chose the direction, reviewed and merged.
- One line on the GitHub profile guide: it helps graduates make their projects visible on GitHub.
- Hand over: "Esmat will take you through the LinkedIn guide."

## 4. Esmat: LinkedIn guide (2 min)

- Why: a career changer has to explain the move into data. A LinkedIn profile is where employers look first.
- What it is: a step-by-step guide with screenshots, written for someone who has never set up a profile properly.
- Key parts to mention (adjust to match what you wrote):
  - Section labels and the About section: how to tell the career-change story.
  - Featured: where to show your projects.
  - Your public profile URL.
- It was checked against a real LinkedIn account, so the menu names match what you will see.
- Same look as the rest of the site.
- Your interface suggestions shaped the app: collapsible job cards, a simpler Sources page, and the map bug you found.
- Feel free to add your own experience: what was hardest, or what surprised you.
- Hand over: "SK will show how a job card becomes a tailored CV."

## 5. SK: Tailor my CV (3 min)

- Problem: one CV does not fit every advert, and a career changer's skills are buried in old job titles.
- How it works, in order:
  1. On a job card, press "Tailor my CV".
  2. The job brief is copied.
  3. Paste it into Claude desktop.
  4. Claude reads your CV and biography from your SkillMatch Folder.
  5. It saves a tailored CV, as Word and PDF, in a "Tailored CVs" subfolder.
- The SkillMatch Skill does three jobs: update my CV, build a biography, tailor.
- The biography is an interview. It digs out real stories (a problem, what you did, the result), organised by skill, in your own words.
- Setup: Claude desktop plus the Desktop Commander extension, then upload the SkillMatch Skill ZIP.
- One thing that trips people up: two Desktop Commander icons look alike. The black chip is the version that can read your local files. The `</>` icon (two chevrons with a slash, seen on Windows) is the other version. The page shows both.
- Privacy:
  - Your CV and biography never leave your computer.
  - Only public advert details travel, in the page address after a `#`. Our servers never store them.
- Limit: free Claude accounts have a usage limit. The page warns about it.
- Feel free to describe what you tested, what broke and how you fixed it.
- Hand over: "John will show what the data told us."

## 6. John: Data analysis, what the search found (3 min)

- The question: do the skills the course teaches match the skills employers ask for?
- Your radar chart was the first answer: employer demand against course coverage.
- One captured week, 30 October, West Midlands:
  - 24,656 search appearances (an advert can appear more than once).
  - 4,654 distinct adverts collected.
  - 1,988 data-role adverts.
  - 1,512 local ones, then 85 after the seniority filter.
  - 67 matched to a graduate.
- Adverts come and go fast: 148 new, 158 gone by the next collection. Median time seen: 3.25 days.
- Skills employers ask for: in adverts with full descriptions, SQL is essential in 60 and Excel in 42. Neither is marked as covered in the course.
- Tools: notebook in Google Colab, then exported summary data for the public analysis page.
- Hand over: "Oana will finish the analysis."

## 7. Oana: Data analysis, advertisers, pay, the test, what next (2 min)

- Who advertises: 45 of the 67 matched jobs come from agencies. None is confirmed direct.
- Pay: the middle half is £35,000 to £45,000. 20 of the 67 give no salary.
- AI: 10 of the 67 mention AI.
- Hypothesis tested: do matched and senior adverts list a different number of essential requirements?
  - Medians were 6 and 5.
  - Mann-Whitney U test, p = 0.062. Not significant at 0.05. This sample shows no clear difference.
- What to do next: the analysis page has a "What to do next" tab with learning resources. SQL and Excel come first, and the SQL and Excel mind maps help.
- Limits, said plainly: one sample, not the whole market. AI-assisted advertiser and sentence labels still await a human check.
- Close: SkillMatch is a working app, two guides, a CV tool and an analysis, built by five people in a week. Thank you. Questions?

---

## Questions to be ready for

- Where do the adverts come from? Reed's official API and documented feeds. Provider approval requests are still open (issues #7 and #115). CV-Library is off.
- Why no paid AI? Matching is local Python rules, so it is cheap and explainable. Tailor my CV uses the user's own Claude.
- Is it the whole market? No. One captured sample.
- What happens to my data? Nothing is stored. Profile stays in the tab, CV stays on your computer.
- What would you do next? Travel time between home and job, more regions, human check on AI labels, SQL and Excel learning route.
- Who did what? Oana idea and project management; Phil app and repo; Esmat guides; SK Tailor my CV; John and SK data analysis, with Esmat helping.
