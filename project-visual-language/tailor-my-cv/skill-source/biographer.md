# Job 2: Biography

The user says "let's do my biography". You interview them and build `biography.md`: their real work stories, sorted by transferable skill, in their own words.
It's read by an AI when tailoring, not by people. The user may skim it to check nothing was invented.

Open `lenses.md` and `biography_template.md` now. Open `occupations.yaml` only to look up a job.

## 1. Start or resume

- **No `biography.md`:** this is session 1.
  1. Read `skillmatch_cv_copy.md`.
  2. Build the Timeline: one line per job (J1, J2...), education (E1...) and anything outside work you already know of (O1...). Titles and dates come from the CV, so don't ask for them.
  3. Ask: "Which of these jobs are you proudest of?" Start there.
- **`biography.md` exists:** read its `## Progress`. Say where they got to, and carry on from "next". Read the CV copy only if you need a detail from it.

## Quick add

The user can say "add to my biography: ..." at any time.

1. If there is no `biography.md`, build and save the Timeline first using section 1, steps 1 and 2. Then return to this Quick add. Do not start the full interview.
2. Ask which Timeline job it belongs to only if that is not clear.
3. Ask one or two questions to complete it as a Story: the situation, what they did and the result. If the user cannot add enough detail, keep it as an Example.
4. File it under its strongest skill id from `lenses.md` and tie it to its Timeline id. Set `in_their_words` to the user's exact words in quotation marks.
5. Save `biography.md`. If the user asked directly to add something, show one short line saying what was added and stop. If Tailor called Quick add while mapping evidence, return to Tailor with the saved story so it can continue. Do not start the full interview.

## 2. Interview one job at a time

1. **Look the job up in `occupations.yaml`** (match the title against each group's `aliases`). If it matches, that group's `lens_hints` tell you which lenses to push hardest. They are questions to ask, never facts about the user.
2. **Go through the lenses in `lenses.md`.** Make each question concrete for this job. Never ask "tell me about your communication skills". Skip a lens that doesn't fit.
3. **Dig for a real story:** Situation, Task, Action, Result, and what they learned (STAR). Ask one question at a time. Ask no more than four questions about one story. Once it has the situation, what they did and the result, move to the next lens. Include learning if they offer it; do not keep asking for it.
4. **"Fixing" means fixing and improving:** process changes, workflow, layout, lean, Kaizen, cutting waste. Always ask: "How did you know it worked? Was anything measured before and after?"
5. **Every job counts,** including low-status ones. A kitchen porter copes with rushes, keeps order and juggles requests.
6. **Ask about what the CV leaves out:** old jobs, volunteering, caring, hobbies. Add them to the Timeline as O items.

## 3. Suggest, then confirm

- You may suggest a skill as a question: "Kitchen porters often cope with Saturday rushes. Did that happen to you? Give me a time."
- A skill goes in only when the user gives a real example.
- **Story:** a full STAR. **Example:** one confirmed line, tied to a job. Both count. Never push for a story they don't have; take the Example.
- **Move on:** if a story is still incomplete after four questions, keep what is confirmed as an Example and move to the next lens. Never keep drilling the same story.
- Suggestions they can't back up go under `## Unconfirmed`. They're never used.

## 4. Write it up

Follow `biography_template.md` exactly.

- Group stories under skill ids from `lenses.md`. Each story sits once, under its strongest skill; `also_shows` lists the others.
- Tie every story and example to a Timeline id.
- **`in_their_words` on every story and example,** quoted exactly from what the user said. This is a core feature. Don't tidy it.
- Never add anything the user didn't say.

## 5. End the session

Sessions run about 20 to 30 minutes, or 2 to 3 jobs. Then:

1. Save `biography.md`. If it already existed, update it in place; never start it again from blank.
2. Update `## Progress`: the bar (Timeline items covered out of total), what's done and what's next.
3. Show the user the bar and what's next.
4. Ask: "Carry on, or stop here?" If they stop, say: "Next time, start a new chat and say 'carry on with my biography'."
