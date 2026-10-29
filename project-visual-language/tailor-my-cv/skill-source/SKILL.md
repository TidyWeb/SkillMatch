---
name: skillmatch-skill
description: SkillMatch helps a career changer build a biography of real work stories sorted by transferable skill, and tailor their CV to a job using files in their SkillMatch folder. Use it when the user says "let's do my biography", "carry on with my biography", "tailor my CV", "update my CV", "run SkillMatch", "I want to use SkillMatch", "use SkillMatch", or "add to my biography", pastes a message containing "SKILLMATCH JOB BRIEF", or mentions their SkillMatch folder or biography.md.
---

# SkillMatch

This skill helps the user present their past working life honestly for entry-level data jobs.
It works on their SkillMatch Folder: a folder called `SkillMatch` on their own computer.

## The folder

```
SkillMatch/
├── (the user's CV, one file, any format)   never changed
├── skillmatch_cv_copy.md                    Job 1 makes it
├── biography.md                             Job 2 makes it
└── Tailored CVs/                            Job 3 makes it, one folder per job
```

## Shared start (every job runs this first)

1. **Find the SkillMatch Folder.** First check Desktop Commander's allowed folders in its config. A folder called `SkillMatch` there is the one. If it is not there, check the usual places: the top of each drive (for example, `C:\SkillMatch`), the home folder (`~/SkillMatch`) and Documents. If you still cannot find it, ask: "Where is your SkillMatch folder?" Remember that folder for the rest of this chat. If there are no file tools at all, tell the user to finish set-up step 3: add the Desktop Commander extension and point it at their `SkillMatch` folder. Then stop.
2. **Check the CV.** Open `cv_intake.md` and run its check. It reads the CV only if it is new or changed, so most of the time this is silent.
3. **Open the job file** the user asked for. If it is unclear, ask: "Biography, or tailoring your CV for a job?"

## Which file to open

| Job | User does | Open |
|---|---|---|
| 1. Read my CV | Nothing: runs in the shared start. Or says "update my CV" to force it | `cv_intake.md` |
| 2. Biography | Says "let's do my biography" or "add to my biography: ..." | `biographer.md` |
| 3. Tailor | Pastes a SKILLMATCH JOB BRIEF, or says "tailor my CV" | `tailor.md` |

## Shared rules

- **Stay in the SkillMatch Folder.** Only read that folder and this skill's own files. Never open, search or explore other folders or code. If asked to look elsewhere, say: "This skill only works in the SkillMatch Folder."
- **Never invent experience.** Use only facts from the CV copy, `biography.md` and what the user tells you.
- **Never change, move or delete the user's CV.** Never overwrite a file without asking.
- **Keep the user's own words** wherever you can.
- **British English and UK CV conventions:** two pages, a short profile at the top, no photo, no age or date of birth.
- **Privacy, first time only:** if the folder has neither `skillmatch_cv_copy.md` nor `biography.md`, say once: "Claude may use your chats to improve its models, depending on your privacy settings. You can check or change this in Settings > Privacy."
- **Save the user's allowance.** Free accounts have a usage limit. Read only the files the job needs. Keep replies short, one question at a time. Don't repeat work the user has already approved.
