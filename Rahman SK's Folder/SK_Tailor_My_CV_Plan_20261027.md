# Tailor my CV: plan overview

For Phil and SK, Wed 28 Oct 2026. Design agreed in the 27 Oct grilling sessions (decisions 1 to 33 in `Decisions.md`). Nothing here is built yet.

"CV Tweaker" was the working title. The name is now **Tailor my CV**.

## 1. What it's for

SkillMatch finds vacancies that suit a Code Institute graduate. Tailor my CV helps them rewrite their CV for one of those vacancies, honestly, using their own words.

Three rules shape everything:

- **SkillMatch never calls an AI and never stores anything about the user.**
- **As little manual work for the user as possible.**
- **The AI never invents experience.** It only uses facts from the user's CV and biography. It never changes the original CV.

## 2. The big idea

All the real work happens on the user's own computer, in their own Claude desktop app. Once Claude desktop can see a local folder called `SkillMatch`, most of the hard problems go away: Claude can read the CV, read the biography and save new files.

The website's only job is to **carry the job details** from the SkillMatch app to the user's Claude, and to **teach the one-off setup**.

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

Nothing about the user touches a server at any point.

## 3. The three pieces

### 3.1 The SkillMatch app: the "Tailor my CV" button

- Each job page (and later each card) gets a **Tailor my CV** button.
- The button links to the Tailor page with a **job brief** packed into the link, after a `#`. The part after `#` stays in the browser and is never sent to any server, so neither the app nor the static site sees it.
- **The job brief (decision 27):**
  - Always: title, employer, location, salary, closing date, advert link; every essential and desirable requirement in the advert's own words; duties; degree and data-years wording.
  - Only if the user has a SkillMatch profile in that browser: SkillMatch's met / partly / gap for each requirement, worded as **hints** for Claude to check against the biography, not as facts. The app's form is thin; the biography is rich.
- The app already holds all of this (`match.py`, `job.html`, `routes.py`). The work is one small link-building function and one button.

### 3.2 The Tailor my CV page: carrier and instructions

One page on the static guides site (`site/`), next to the GitHub and LinkedIn guides.

- **Top: this job.** JavaScript reads the brief from the link and shows it as a short, readable summary, so the user can see what's being passed on.
- **One big Copy for Claude button.** It copies a short message plus the brief, e.g. "Tailor my CV for this job using my SkillMatch folder." The page doesn't need to know where the folder is; Claude already does, from setup.
- **Below: setup and how-to in expandable boxes** (decision 31). Each box is one step and opens to show sub-steps. No long page of dense text. Where it differs by system, the box has Windows, Mac and Linux tabs.
- Opened without a job in the link, the page still works as the setup guide.
- **Look and feel waits for the unified visual style.** That style isn't designed yet and also covers the app's interface. On Wednesday the page is built for structure and function only (plain, mobile-first layout), then restyled once the style exists. The style should work on laptops and feel like a big mobile app, because a phone app serving SkillMatch cards is a possible later step.

### 3.3 The user's computer: Claude desktop and the SkillMatch skill

- **Claude desktop** (free plan), with the **filesystem extension** pointed at one flat folder called `SkillMatch` (decisions 17, 18).
- The folder holds: their original CV file(s), `cv.md`, `biography.md`, and tailored copies.
- **One skill, called SkillMatch, with three jobs inside it** (decision 33, section 5).

## 4. The user's journey

### Once only (setup)

1. Make a folder called `SkillMatch` somewhere memorable (Documents is suggested).
2. Install Claude desktop and sign in (free account is fine).
3. Add the filesystem extension and point it at the `SkillMatch` folder.
4. Turn on code execution and upload the SkillMatch skill (one zip).
5. Get your CV in: open a chat, say "update my CV", and drag in your CV in whatever format you have. Claude saves `cv.md`. No CV? Export your LinkedIn profile as a PDF and drag that in.
6. Build your biography: say "let's do my biography". Short sessions of 20 to 30 minutes; it picks up where you left off.

### Every job

1. In SkillMatch, open a job and click **Tailor my CV**.
2. On the Tailor page, click **Copy for Claude**.
3. Paste into Claude desktop and send.
4. Check Claude's requirement-by-requirement map, add anything it missed.
5. Get `Employer_CV` as Word and PDF, plus a list of what changed and why.

## 5. The SkillMatch skill

### What it does

| Job | User says | Result |
|---|---|---|
| Update my CV | "update my CV" (and drags in a file) | `cv.md`, the working text copy of the CV |
| Biography | "let's do my biography" | `biography.md`, built over short sessions |
| Tailor | pastes the brief from the Tailor page | `Employer_CV` (Word, PDF, Markdown) and `Employer_changes.md` |

### Layout

Nothing is built yet. The only skill so far is `CV_Tweaker/skillmatch-test/`, a tiny test for SK's Test 5. So this is one new skill built from scratch, not three old ones merged.

```
skillmatch/
├── SKILL.md               Wed   when to use, the shared start, the shared rules, which job file to open
├── cv_intake.md           Wed   Job 1: turn any CV file into cv.md, check it's current
│                                (built first: the Biographer starts from the CV, decision 1)
├── biographer.md          Wed   Job 2: the interview flow
├── lenses.md              Wed   Biographer reference (from Planning/CV_Tweaker/Lenses.md)
├── occupations.yaml       Wed   Biographer reference (copy of Research/Occupations/archetype_groups_v2.yaml)
├── biography_template.md  Wed   Biographer reference (from Biography_Skeleton.md)
└── tailor.md              Wed   Job 3: the tailoring flow
```

Everything is built, tested and finalised on Wed 28 Oct.

### What `SKILL.md` contains

1. **Frontmatter:** `name: skillmatch` and one description covering all three triggers: "let's do my biography", "update my CV", and a pasted SkillMatch job brief or "tailor my CV".
2. **What this is:** two lines.
3. **Shared start:** find the folder, check `cv.md` exists and is current, then pick the job.
4. **Which file to open** for each job.
5. **Shared rules:** honesty, never touch originals, keep their words, privacy line.

Claude only opens a file when it needs it, so someone tailoring never loads the interview material. `SKILL.md` stays short; the detail lives in the job files.

### The shared start (every job runs this first)

1. Find the `SkillMatch` folder through the filesystem extension.
2. Is there a `cv.md`? If not, run the CV intake first. If there is, ask "Is this still your current CV?" and refresh it if not.
3. Open the job file the user asked for.

### Shared rules (written once, in `SKILL.md`)

- Never invent experience. Use only facts from `cv.md` and `biography.md`.
- Never change or overwrite an original file. Tailored copies are saved as `Employer_CV`.
- Keep the user's own words (`in_their_words`) wherever possible.
- One privacy line: Claude free accounts use chats for training unless switched off in Settings.

### The Tailor job, step by step

1. Read the brief, `cv.md` and `biography.md`.
2. Map every requirement to its evidence: a CV line, a biography story, a biography example, or nothing. SkillMatch's hints are a starting point only.
3. Show the user the map first and ask what's missing. Short, not a new interview.
4. Rewrite: a tailored profile statement; experience reordered so the strongest evidence for this job comes first; new bullets built from STAR stories, keeping the user's words.
5. List honest gaps: requirements with no evidence. Never fill them.
6. Save `Employer_CV.md` and `Employer_changes.md` (what changed and why), then produce Word and PDF versions with code execution.
7. Tell the user what to send: portal with one upload slot, PDF unless it asks for Word; emailing a recruiter, attach both.

## 6. Why this path

| Choice | Why | Downside we accept |
|---|---|---|
| Work happens in the user's Claude desktop | It can read and write their files, so no uploading every time; SkillMatch stays AI-free and stores nothing | Users must install an app and an extension once |
| Job brief carried in the link after `#` | No server, no database, no account; the brief never leaves the browser | Long links, but well within what browsers handle |
| Tailor page on the static site, not a panel in the app | One place for setup help and the carrier; shares a home with the GitHub and LinkedIn guides; works without the app | One extra click (button, then Copy) |
| Copy and paste into Claude | The only link a website can make with a desktop app; the user sees exactly what's sent | One paste per job |
| `cv.md` as the working copy | Any CV format comes in once; after that everything is plain text, which the extension handles well | User must refresh it when their real CV changes (the skill asks) |
| Word and PDF out | Adverts rarely say which; agencies like Word, portals like PDF | Claude's layout, not the user's own template (they can paste into their template instead) |
| One skill, three jobs | One upload; rules in one place so they can't drift; users can't pick the wrong skill; files load only when needed | A bigger skill to write and test; one description must cover three triggers |
| Expandable step boxes | Short page, users only open what they need | None worth noting |
| Linux: official app on Ubuntu and Debian; a copyable prompt for other distros | Community builds work (Phil runs Claude desktop on Fedora); the user's own Claude finds the current best build | We don't test every distro |

### Alternatives we turned down

- **Three separate skills.** Three uploads, rules copied three times, and users would have to remember which to run.
- **A separate "update my CV" skill.** Users wouldn't remember to run it. A check at the start of every job catches it instead.
- **Any AI (ChatGPT, Gemini and so on).** Replaced by Claude desktop only (decision 18): file access is what makes it low-effort.
- **A panel inside the app.** Saves a click, but splits setup help from the carrier and ties the Tailor to the app being up.

## 7. Things to test before we rely on them

The free Claude desktop trial run (`CV_Tweaker/SK_Free_Claude_Desktop_Trial_Run.md`, run by both Phil and SK) covers all of these except Linux beyond Phil's Fedora.

1. **Free account + filesystem extension:** does it install and read and write the `SkillMatch` folder? (Gate for everything.)
2. **Skill + extension (Test 5):** can an uploaded skill use the filesystem extension?
3. **Word in:** can Claude read a `.docx` straight from the folder, or must the user drag it into the chat? (The plan assumes dragging in, which works either way.)
4. **Word and PDF out:** can Claude save the `.docx` and `.pdf` into the folder, or only offer them as downloads in the chat? If downloads only, add "save both into your SkillMatch folder" to the instructions.
5. **Paste trigger:** does pasting the brief reliably start the Tailor job? If not, the copied text opens with "Use the SkillMatch skill to tailor my CV".
6. **Linux:** does the extension work on the Ubuntu/Debian beta and on a community build (Phil's Fedora)?

## 8. Still to decide

- **No biography yet:** tailor from the CV alone with a note suggesting the Biographer, or send the user to the Biographer first?
- **Q13** (parked until SK's test): if free accounts can't use the extension, fall back to upload-in and copy-out, or require Pro?
- **Test material:** a made-up vacancy and a dummy CV (board card 1.3.6).

## 9. Suggested build order

All on Wednesday 28 Oct: built, tested and finalised the same day.

1. **The skill**, starting with `SKILL.md`, the shared start and the Biographer (already planned for Wednesday), then `cv_intake.md`, then `tailor.md`.
2. **Test the Tailor by hand:** take a real job from `data-snapshots`, write the brief yourself, paste it in. If this works, the rest is delivery.
3. **The Tailor page:** static HTML; test it with a hand-made link. Structure and function only; styled later.
4. **The app button:** the link builder, last.

Steps 1 and 3 don't depend on each other, so they can run in parallel.

## 10. Knock-on changes

- Decision 25's layout (`skillmatch-biographer/`) becomes `skillmatch/` with three job files. The Biographer work plan for Wednesday needs that one change.
- Board cards 1.3.1 to 1.3.6 (issues #102 to #107): rename Tweaker to Tailor, and drop "works with any AI".
- The work plan's "Thursday" section is out of date: the Tailor is built on Wednesday too.

## 11. Later, outside the hackathon

- A phone app that serves SkillMatch cards from the hosted app.
- A standalone Flask version of SkillMatch.
- Note for the phone app: Tailor my CV needs Claude desktop, which is on a computer. A user browsing on a phone will need a way to send the job to their computer (for example, emailing themselves the Tailor link).
