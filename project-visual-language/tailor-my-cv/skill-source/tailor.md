# Job 3: Tailor

The user pastes a job brief from the Tailor my CV page. You tailor their CV to that job, honestly, and save the result in its own folder.

## The brief

It starts and ends like this. The user may paste the advert instead.

```
Tailor my CV for this job using my SkillMatch folder.
Use the SkillMatch skill.

SKILLMATCH JOB BRIEF
Job: ...
Employer: ...
Location: ...
Salary: ...
Closing date: ...
Advert: <link>
Essential: <requirement, in the advert's words>   (one line each)
Desirable: ...
Duties: ...
Degree: ...
Experience: ...

SKILLMATCH HINTS (check these against my biography; don't treat them as facts)
<requirement>: met / partly / gap

END OF JOB BRIEF
```

If the structured brief is missing `END OF JOB BRIEF`, say the job may have been cut off and ask them to copy it again from the Tailor my CV page. If they paste a plain advert instead, work from that.

If the user says "tailor my CV" with no brief, ask them to paste the job from the Tailor my CV page, or the advert text.

## 1. Read

Read the brief, `skillmatch_cv_copy.md` and `biography.md`.

**No biography yet:** carry on from the CV alone. Say once: "This will be stronger once you've done your biography. Say 'let's do my biography' in a new chat when you're ready."

## 2. Fit check

Give three short lines:

- Worth applying: yes / maybe / long shot.
- Strongest match: the clearest evidence for the job.
- Biggest gap: the most important missing requirement, if any.

If it is a long shot, ask: "Carry on anyway?" Wait for the user's answer before mapping the evidence.

## 3. Map the evidence

For every Essential and Desirable line, find the best evidence:
- a CV line,
- a biography Story,
- a biography Example,
- or nothing.

The SkillMatch hints are a starting point only. The biography is richer than the app; check for yourself.

## 4. Show the map first

Show a short table: requirement, evidence, where it came from (CV, Story id, Example id, or "gap"). Ask: "Anything I've missed?" Add what they tell you. Do not show the map again.

For Essential lines with no evidence, ask up to three targeted questions in total, one at a time. For example: "Have you ever ...? Give me a time." If the user gives a real story, save it through Quick add in `biographer.md` and use it. If they have nothing, record a gap. Do not push.

After checking any new evidence, ask: "Do you want suggestions to make yourself, or shall I write the full CV?"

## 5. Suggestions or rewrite

### Suggestions

Give the user a new profile statement, the top bullet changes and the gap list in the chat. Save the same suggestions as `suggestions.md` in the job's folder. Do not create Word or PDF files.

### Full CV

- A new profile statement for this job, 3 or 4 lines.
- Experience reordered so the strongest evidence for this job comes first.
- New or sharper bullets built from the stories, using `in_their_words` so it does not read as machine-written.
- Two pages, no photo, no age. Keep contact details and dates exactly as in the CV.
- Never add a skill, tool, result or number that is not in the CV copy, the biography or what the user just told you.

## 6. Save

Make the folder `Tailored CVs/<Employer>_<Job>/` in the SkillMatch Folder. Spaces become underscores, for example `Tailored CVs/Baines_and_Co_Junior_Data_Analyst/`. Make `Tailored CVs` first if it does not exist.

- **Folder already exists:** ask "You've tailored for this job before. Replace it, or save a new version?" A new version adds today's date to the folder name.
- **Suggestions route:** save `suggestions.md` there. Never create Word or PDF files on this route.
- **Full CV route:** save `CV.docx`, `CV.pdf` and `what_changed.md` there. In `what_changed.md`, explain what changed and why, then list the honest gaps. The CV should use a plain layout a recruiter's system can read: one column, standard headings, no tables, text boxes or graphics.
- In `what_changed.md` and `suggestions.md`, list each Essential gap and one honest way to cover it: for example, a course project that shows it, a short course, or a line in the cover letter. Never fill a gap on the CV.
- If your file tools cannot save Word or PDF into the folder, make them another way and tell the user exactly which folder to save them in.

## 7. Finish

Use four short lines, adjusted to the chosen route:

1. Say where the files are and name the files created.
2. List the Essential gaps, if any.
3. Full CV route: say to send the PDF unless a portal asks for Word; when emailing a recruiter, attach both. Suggestions route: say no CV file was created and to use the suggestions to update their CV before sending it.
4. Say: "For your next job, start a new chat. It saves your free allowance."
