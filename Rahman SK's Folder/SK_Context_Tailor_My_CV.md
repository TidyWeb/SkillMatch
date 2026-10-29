# Context: SkillMatch "Tailor my CV"

Load this into your AI assistant at the start of a session. It explains the project, the goal, how the pieces fit, and how SK and Phil work together. Use it to help SK build, review and give second opinions. Last updated 27 Oct 2026.

## How to use this context (for the AI)

- You are helping SK, one of two people building "Tailor my CV" (the other is Phil).
- Treat the decisions below as agreed. If you think one is wrong, say so plainly and explain why, but don't quietly design around it.
- When SK pastes in something Phil built, review it against this context: does it follow the rules, does it fit the structure, what would break?
- Keep answers short and plain. British English.
- Don't make up facts about Claude's apps or settings. If something needs checking (a menu name, a plan limit), say it needs testing.

## The project

**SkillMatch** is a free web app for Code Institute data analytics graduates in the West Midlands. Graduates enter where they live, how they travel, their skills and their previous working life. SkillMatch collects real job adverts every day, filters them for entry-level data roles, and shows matched vacancies as cards. Each card explains how the person's background answers the advert and which requirements they don't yet meet. Most users have no data experience but years in other careers, so transferable skills matter more than job titles.

It's a team project for a four-day Code Institute hackathon (team of five: Phil leads the app, SK works with Phil on Tailor my CV, John leads data analysis, Oana is project manager, Esmat leads interface ideas). **Deadline: Friday 30 Oct, midnight. Presentations: Monday 2 Nov.** The aim is a lasting service, not just a demo.

The app is a Python Flask app, to be hosted on Google Cloud Run. The team repo is https://github.com/TidyWeb/SkillMatch. There's also a static guides site in the repo (`site/`) with GitHub and LinkedIn profile guides for graduates.

## The goal of Tailor my CV

Help a graduate rewrite their CV for one specific SkillMatch vacancy, honestly, using their own words, with as little manual work as possible.

"CV Tweaker" was the working title. The name is now **Tailor my CV**.

## Ground rules (non-negotiable)

1. **SkillMatch never calls an AI and never stores anything about the user.** No accounts, no database of users, nothing logged.
2. **As little manual work for the user as possible.**
3. **Honesty:** the AI never invents experience. It only uses facts from the user's CV and biography.
4. **Never change the original CV.** Tailored copies are saved as `Employer_CV` (e.g. `Baines_and_Co_CV`).
5. **The user's own words are a feature.** Stories keep their exact quotes, so CVs don't read as machine-written.
6. **End users use the Claude desktop app** (free plan) with its filesystem extension. That's what lets Claude read and write their local files. (SK and Phil can use any AI to help build; this rule is about end users.)

## How it fits together

All the real work happens on the user's own computer, in their Claude desktop app, which can see a local folder called `SkillMatch`. The website only carries the job details and teaches the one-off setup.

```
SkillMatch app (Cloud Run)        Tailor my CV page (static site)       User's computer
──────────────────────────        ───────────────────────────────       ───────────────
Job page                                                                Claude desktop
  [Tailor my CV] ──link────────►  Reads the job brief from the link      + filesystem extension
  job brief packed in the           Shows it in plain English              pointed at SkillMatch/
  link after the #                [Copy for Claude] ── user pastes ───► + the SkillMatch skill
                                  Setup steps in expandable boxes        Reads cv.md + biography.md
                                                                         Saves Employer_CV (Word + PDF)
```

1. **The app button.** Each job page gets a "Tailor my CV" button. It links to the Tailor page with a job brief packed into the link after `#`. Browsers never send the part after `#` to a server, so nothing is stored anywhere.
2. **The job brief.** Always: title, employer, location, salary, closing date, advert link, every essential and desirable requirement in the advert's own words, duties, degree and experience wording. If the user has a SkillMatch profile in that browser, it also carries SkillMatch's met / partly / gap verdict per requirement, but only as hints. The biography is richer than the app's form, so Claude checks for itself.
3. **The Tailor page.** One static HTML page. Top: the job brief from the link, shown in plain English. Then a big **Copy for Claude** button. Below: setup and how-to steps in expandable boxes (click to open the sub-steps), with Windows, Mac and Linux tabs where they differ. No long page of dense text. Without a job in the link, it still works as the setup guide. **Styling waits:** SkillMatch's unified visual style isn't designed yet (it also covers the app's interface, which should work on laptops and feel like a big mobile app). Build the page for structure and function first, plain and mobile-first, and restyle it when the style exists.
4. **The user's computer.** Claude desktop, the filesystem extension pointed at the `SkillMatch` folder, and one uploaded skill called **SkillMatch**.

## The user's journey

**Once (setup):** make a `SkillMatch` folder (Documents suggested); install Claude desktop; add the filesystem extension pointed at the folder; turn on code execution and upload the SkillMatch skill; say "update my CV" and drag in any CV file (no CV: export your LinkedIn profile as PDF); say "let's do my biography" and do short sessions of 20 to 30 minutes.

**Every job:** click Tailor my CV in SkillMatch, click Copy for Claude, paste into Claude desktop, check Claude's requirement map and add anything it missed, then get `Employer_CV` as Word and PDF plus a "what changed and why" list. When sending: if a portal has one upload slot, use the PDF unless it asks for Word; when emailing a recruiter, attach both.

**Linux:** Ubuntu and Debian have an official Claude desktop app (beta). Other distros (Fedora, Arch and so on) use community builds, which work; the page gives a copyable prompt asking Claude in the browser to find and install one.

## The SkillMatch skill

A Claude "skill" is a folder of instructions the user uploads to Claude once. Claude reads `SKILL.md`, and opens the other files only when it needs them. Ours is **one skill with three jobs**. Nothing is built yet.

```
skillmatch/
├── SKILL.md               Wed   when to use, the shared start, the shared rules, which job file to open
├── cv_intake.md           Wed   Job 1: turn any CV file into cv.md, check it's current
├── biographer.md          Wed   Job 2: the interview that builds biography.md
├── lenses.md              Wed   Biographer reference: 10 angles for asking about a job
├── occupations.yaml       Wed   Biographer reference: 31 occupation groups and their transferable skills
├── biography_template.md  Wed   Biographer reference: the layout of biography.md
└── tailor.md              Wed   Job 3: tailoring a CV to a job brief
```

Everything is built, tested and finalised on Wednesday 28 Oct.

| Job | User says | Result |
|---|---|---|
| Update my CV | "update my CV" and drags in a file | `cv.md`, a plain-text working copy of their CV, from any format (Word, PDF, scan) |
| Biography | "let's do my biography" | `biography.md`, built over short, resumable sessions |
| Tailor | pastes the brief from the Tailor page | `Employer_CV` (Word, PDF, Markdown) and `Employer_changes.md` |

**Shared start (every job):** find the SkillMatch folder; if there's no `cv.md`, make one first; if there is, ask "Is this still your current CV?"; then open the right job file.

**Why one skill, not three:** one upload for the user; the rules are written once, so they can't drift apart; users can't pick the wrong skill; files load only when needed. The cost is a bigger skill to write and test.

### The Biographer in brief

It interviews the user about their working life and saves `biography.md`, which is read by AI, not people. It starts from the CV, so it skips the chronological walk-through. It digs for real stories in STAR form (Situation, Task, Action, Result, plus what they learned). Every job counts, including low-status ones like kitchen porter. It asks about what the CV leaves out (volunteering, caring, hobbies). It may suggest a skill as a question ("Did that happen to you? Give me a time."), but a skill only goes in if the user confirms it with a real example. Stories are grouped by transferable skill, each keeps the user's exact words, and a text progress bar in the file shows how far they've got.

### The Tailor in brief

It reads the brief, `cv.md` and `biography.md`, then maps every requirement to its evidence (a CV line, a story, an example, or nothing). It shows the user that map first and asks what's missing. Then it rewrites: a tailored profile statement, the strongest evidence moved first, and new bullets built from stories in the user's words. It lists honest gaps and never fills them. Finally it saves the Markdown and changes list, then Word and PDF versions.

## Not yet known (needs testing)

SK's free-account test answers most of these. Until then, treat them as open.

1. Can a free Claude account use the filesystem extension to read and write the folder? (Everything depends on this.)
2. Can an uploaded skill use the filesystem extension?
3. Can Claude read a `.docx` straight from the folder, or must the user drag it into the chat?
4. Can Claude save Word and PDF files into the folder, or only offer them as downloads?
5. Does pasting a job brief reliably start the Tailor job?

## Still to decide

- **No biography yet:** tailor from the CV alone with a nudge towards the Biographer, or send the user to the Biographer first?
- **If free accounts can't use files:** fall back to uploading files into the chat and copying results out, or ask users to pay for Pro?

## Who does what (proposed, to agree on the Wed 28 Oct call)

All on Wednesday 28 Oct: built, tested and finalised the same day.

- **SK:** runs the free-account test (Windows) and reports back; owns the **Tailor page** (static HTML, expandable boxes, Copy for Claude button, reading the brief from the link; structure and function, not final styling), including its setup instructions; runs the Biographer on himself to test it; writes a hand-made job brief from a real vacancy to test the Tailor.
- **Phil:** builds the SkillMatch skill (shared start, CV intake, Biographer, Tailor); adds the button to the app last.
- **Both:** test each other's work, compare notes, fix. Biographies stay on our own computers; only a fictional mixed example goes in the repo.

Build order: skill first, test the Tailor by hand, then the page, then the app button. The skill and the page don't depend on each other, so they're built in parallel.

## Later, outside the hackathon (don't design for these now)

A phone app serving SkillMatch cards, and a standalone Flask version. Keep the Tailor page mobile-friendly so it fits later.

## Working together

- Share drafts both ways: paste a file into your AI with this context and ask for a review or a second opinion, then send the notes back.
- Useful review questions: Does it break a ground rule? Would a nervous first-time user follow it? Is anything vague enough that Claude might guess or invent? Is there a step we could cut?
- Keep the user's experience simple. If a design adds a click or a setting, ask whether it's worth it.

## Glossary

- **Job brief:** the job details the app passes to the Tailor page in the link.
- **`cv.md`:** the plain-text working copy of the user's CV, inside their SkillMatch folder.
- **`biography.md`:** the user's working life, organised by skill, built by the Biographer.
- **STAR:** Situation, Task, Action, Result (plus what was learned): the shape of each story.
- **Filesystem extension:** the Claude desktop add-on that lets Claude open and save files in chosen folders.
- **Skill:** a folder of instructions uploaded to Claude once, used when the user asks for that job.
- **Hint:** SkillMatch's met / partly / gap verdict, passed on for Claude to check rather than trust.
