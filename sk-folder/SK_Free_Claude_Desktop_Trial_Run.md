# Free Claude desktop trial run

**Who:** Phil and SK. Both run it, on your own computers, and both post the report.

**What we're testing:** can a **free** Claude account, using the Claude desktop app, do everything Tailor my CV needs? That means reading and writing files in a folder, using our skill, handling Word files, and saving Word and PDF.

**Why it matters:** Tailor my CV depends on the answers. If yes, users only need the free app. If no, we change the plan.

**Time:** about 30 minutes. **You need:** a Windows 10+, Mac (macOS 11+) or Linux computer with the Claude desktop app, and a free Claude account. (Phil: Fedora, with the community build.)

**Files you need** (in the `CV_Tweaker` folder of the project): `SK_test_cv.docx` and `SK_skillmatch-trial.zip`. Phil sends them to SK.

Don't use your real CV. We use a made-up one below.

---

## Step 0: Use a FREE account

The test only counts on a free account.

1. If you pay for Claude (Pro or Max), log out and sign in with a free account on another email address. Make one if you need to.
2. If you've never used Claude, sign up free at https://claude.ai.

---

## Step 1: Do you have the Claude desktop app?

This is the app on your computer, not the website in your browser.

- **Windows:** press the Windows key, type `Claude`. Does an app called Claude appear?
- **Mac:** press Cmd + Space, type `Claude`. Does an app called Claude appear?
- **Linux:** look in your applications menu for Claude.

**Yes, it's there:** open it, sign in with the free account, then go to **Step 3**.

**No:** go to **Step 2**.

---

## Step 2: Install the Claude desktop app

1. Go to https://claude.ai/download
2. Click **Download** next to your system (Windows or macOS).
3. Open the downloaded file.
   - **Windows:** run the installer and follow the prompts.
   - **Mac:** drag Claude into your Applications folder.
4. Open Claude (Start menu on Windows, Applications on Mac).
5. Sign in with the **free** account.

---

## Step 3: Check you're on the free plan

1. In the app, click your name or initials (bottom left).
2. Open **Settings** and look for your plan.
3. It should say **Free**. If it says Pro or Max, go back to Step 0.

---

## Step 4: Make a test folder

1. Open your **Documents** folder.
2. Make a new folder called `SkillMatch_Test`.
3. Inside it, make a plain text file called `test_cv.txt`.
   - **Windows:** right-click > New > Text Document.
   - **Mac:** open TextEdit, choose Format > Make Plain Text, then save into the folder.
4. Paste this into it and save:

```
Alex Example
Kitchen porter, The Swan, 2004 to 2006
Head chef, The Old Mill, 2010 to 2018
Cut food waste by changing the Monday order.
```

5. Copy `SK_test_cv.docx` (from Phil) into the same folder. It's the same made-up CV as a Word file. You should now have two files: `test_cv.txt` and `SK_test_cv.docx`.

---

## Step 5: Add the file access extension

An extension is an add-on that lets Claude open files on your computer.

1. In the Claude app, go to **Settings > Extensions**.
2. Browse or search the list for a **filesystem** extension (it may be called "Filesystem").
3. Click **Install**.
4. If it asks which folders Claude may use, choose **only** `Documents/SkillMatch_Test`. Not your whole Documents folder.
5. If it asks you to restart Claude, do so.

**Write down exactly what you see.** If there's no Extensions option, if the filesystem extension isn't listed, or if it says you need a paid plan, take a screenshot. That *is* the result. Stop and go to Step 7.

---

## Step 6: Run four tests

Start a new chat in the app. Paste each line below, one at a time. If Claude asks permission to use a tool, click **Allow**.

1. **List:** `List the files in my SkillMatch_Test folder.`
   Pass if it names `test_cv.txt`.
2. **Read:** `Read test_cv.txt and tell me the two job titles.`
   Pass if it says kitchen porter and head chef.
3. **Write:** `Create a new file in SkillMatch_Test called biography.md containing the line: Test biography, created by Claude.`
   Pass if the file appears in the folder when you look.
4. **Leave the original alone:** `Make a tailored copy of test_cv.txt for a job at Baines and Co. Save it as Baines_and_Co_CV.txt. Do not change test_cv.txt.`
   Pass if the new file appears **and** `test_cv.txt` is unchanged.

---

## Step 6b: Test a skill with file access

A skill is a set of instructions you upload to Claude once. We want to know if a skill can use the file access from Step 5. Use `SK_skillmatch-trial.zip`.

1. In Claude, go to **Settings > Capabilities** and turn on **Code execution and file creation** (it may be called **Create and edit files**).
2. Go to **Customize > Skills**. Click **+**, then **Create skill**, then **Upload a skill**.
3. Upload `SK_skillmatch-trial.zip`. Check it appears in your skills list and is switched on.
4. Start a new chat and type: `run the SkillMatch check`
5. **Test 5 passes** if Claude lists your test files **and** a new file `skill_test.md` appears in `SkillMatch_Test`.

If you can't find Capabilities or Skills, or the upload fails, screenshot it and note what happened.

---

## Step 6c: Three more tests (Word files and pasting)

These answer three questions the first five don't. Start a **new chat** for each one.

### Test 6: Can Claude read a Word file from the folder?

**Why:** most people's CVs are Word files. If Claude can read them straight from the folder, users skip a step.

1. Paste: `Read SK_test_cv.docx in my SkillMatch_Test folder and tell me the two job titles.`
2. **Pass** if it says kitchen porter and head chef.
3. **If it says it can't read it:** drag `SK_test_cv.docx` from the folder into the chat window and send `Tell me the two job titles in this file.` Write down whether that worked. (That's our backup plan, so it matters too.)

### Test 7: Can Claude save a Word file and a PDF into the folder?

**Why:** tailored CVs come out as Word and PDF. We need to know if Claude can put them straight into the folder, or only gives you a download button in the chat.

1. Make sure **Code execution and file creation** is still on (Step 6b).
2. Paste: `Make a tailored copy of test_cv.txt for a job at Baines and Co. Save it into my SkillMatch_Test folder twice: as Baines_and_Co_CV.docx and as Baines_and_Co_CV.pdf. Do not change test_cv.txt.`
3. Look in the folder.
4. **Pass** if both files are in the folder and both open.
5. **Partly** if Claude only shows download buttons in the chat. Click them, note where the files land, and write "downloads only".
6. **Fail** if you get no Word or PDF at all.

### Test 8: Does pasting a job brief start our skill?

**Why:** on the real Tailor page, users click Copy and paste into Claude. We need Claude to recognise that and use our skill without being told.

1. Copy everything in the box below and paste it into the chat as one message.

```
Tailor my CV for this job using my SkillMatch folder.

SKILLMATCH JOB BRIEF
Job: Junior Data Analyst
Employer: Baines and Co
Location: Birmingham
Essential: Experience working with stakeholders to gather requirements
Essential: Strong attention to detail
Desirable: Experience in a fast-paced environment
Advert: https://example.com/advert
```

2. **Pass** if Claude replies with `SkillMatch trial: job brief received` **and** a file `brief_received.md` appears in the folder. That means our skill picked it up.
3. **Fail** if Claude just starts chatting or writing a CV without saying that line. Then try once more in a new chat, with this as the very first line of the pasted message: `Use the SkillMatch skill.` Write down whether that version passed.

---

## Step 7: Report back

Copy this into Discord and fill it in. Attach screenshots of anything that failed.

```
Free Claude desktop trial run
Name: Phil / SK
Computer: Windows / Mac / Linux (version if you know it)
Had the desktop app already: yes / no
Plan shown in Settings: Free / other
Filesystem extension found and installed: yes / no (what happened)
Test 1 List: pass / fail
Test 2 Read: pass / fail
Test 3 Write: pass / fail
Test 4 Copy, original untouched: pass / fail
Test 5 Skill uses file access: pass / fail (what happened)
Test 6 Read Word from folder: pass / fail (did dragging it in work?)
Test 7 Save Word + PDF into folder: pass / downloads only / fail
Test 8 Pasted brief starts the skill: pass / fail (did "Use the SkillMatch skill." fix it?)
Anything odd:
```

---

## If something goes wrong

- Don't try workarounds or other add-ons. A failure is a useful answer.
- Note the exact wording of any message and take a screenshot.
- When finished, you can delete the `SkillMatch_Test` folder.
