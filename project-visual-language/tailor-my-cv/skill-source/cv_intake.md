# Job 1: Read my CV

Runs automatically in the shared start. Also runs when the user says "update my CV".
It turns the user's CV into `skillmatch_cv_copy.md`, the plain-text copy the other jobs read.

## 1. Find the CV

Look in the top level of the SkillMatch Folder only (not `Tailored CVs`).
A CV is any Word, PDF, text, OpenDocument, RTF or image file, except `skillmatch_cv_copy.md` and `biography.md`.

- **None:** say "I can't see a CV in your SkillMatch folder. Put it in (any format), or export your LinkedIn profile as a PDF and put that in." Stop.
- **One:** that's the CV.
- **More than one:** ask "I can see [list]. Which is your current CV?" Use that one. Suggest they move the others out of the folder. Never move them yourself.

## 2. Decide whether to read it

Read the first lines of `skillmatch_cv_copy.md`, if it exists. They say which file it came from and that file's last-modified date.

- **No copy yet:** read the CV.
- **Different file, or the CV's last-modified date is newer:** say "Your CV has changed since I last read it. Updating my copy." Then read it.
- **Same file, same date:** do nothing and say nothing. Go back to the shared start.
- **The user said "update my CV":** read it, whatever the dates say.

## 3. Read it

Open the CV with your file tools.
If they can't open it, ask the user to drag the file into this chat.

## 4. Convert, don't improve

Write `skillmatch_cv_copy.md` with the same content in the same words. Fix nothing. Add nothing.

```
source: <CV file name>
source_modified: <its last-modified date and time>
read_on: <today's date>

# <Name>
<contact details>

## Profile
## Experience
### <Role> | <Employer> | <dates>
- <bullet, as written>
## Education
## Skills
## Other
```

Keep any section the CV has that isn't listed above, under its own heading.
For scans or hard-to-read text, list anything you weren't sure of and ask the user.

## 5. Finish

Say: "CV read: [number] roles, [earliest year] to [latest year]." One line.
Then carry on with the job the user asked for. If they only asked to update the CV, stop there.
