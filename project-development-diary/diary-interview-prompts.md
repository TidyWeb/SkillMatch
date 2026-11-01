# Writing your project development diary with an AI interviewer

## Why we did it this way

Writing a reflection from a blank page is hard, and most of us write less honestly when we're trying to sound good. So instead of asking you to write from scratch, each team member used the same method we used for the CV Tailor biographer:

1. The AI asks one question at a time and waits for your answer.
2. It follows up when an answer is vague, and asks for one concrete example.
3. It gathers everything you say, in your words.
4. When it has enough, it sorts the wheat from the chaff and writes a draft in the first person, with a heading for each section.
5. You edit the draft, save it as a Markdown file, and push it to this folder through your own pull request.

The AI is there to draw the story out of you. The words, the judgement and the final edit are yours.

## How to use it

1. Copy the prompt for your name from the list below, and paste it into the AI you use (Claude, ChatGPT, Copilot, Gemini or similar).
2. Answer one question at a time. Be specific. Say where you disagree.
3. When it shows you a draft, change anything that isn't true or doesn't sound like you. Make sure the first line says which AI helped.
4. Save the result as `firstname-diary.md` (lower case, no spaces).
5. Add it to `project-development-diary/` through a pull request, as described in the README in this folder.

## Rules for the prompts

- Interview first, draft last. The AI should not write anything until the questions are done.
- No flattery, no polishing away frustration, no invented details.
- Each person's contribution lines are a starting point. If they're wrong, the person's version wins.

---

## Shared prompt structure

```
Interview me to write my project development diary. Ask ONE question at a time and wait for my answer. Use my words. Don't invent, don't flatter, don't polish away frustration.

Context: I'm [NAME]. In a 4-day Code Institute Data Analytics with AI hackathon (Oct 2026) our team of five (Esmat, John, Oana, Phil, SK) built SkillMatch: a website, a job-matching app, GitHub and LinkedIn guides, a CV Tailor and a data analysis section. Repo: https://github.com/TidyWeb/SkillMatch. Site: https://tidyweb.github.io/SkillMatch/
[MY PART]. If I correct any of this, use my version.

Cover, in this order, 2–4 questions each:
1. What I thought I was getting into, and how I felt at the start
2. What I actually did
3. What was hard, and how I got through it
4. How my ideas changed, and one thing I'd do differently
5. How I used AI, and where it helped or got in the way
6. What it's done for me: skills, confidence, what's next

Follow up when an answer is vague. Ask for one concrete example. After the last section, show me a draft as Markdown with a heading per section, written in first person in my voice, and ask what to change. The first line must say: "Written with help from <name of AI>, from my own answers." Final file name: [firstname]-diary.md
```

---

## Esmat

```
Interview me to write my project development diary. Ask ONE question at a time and wait for my answer. Use my words. Don't invent, don't flatter, don't polish away frustration.

Context: I'm Esmat. In a 4-day Code Institute Data Analytics with AI hackathon (Oct 2026) our team of five (Esmat, John, Oana, Phil, SK) built SkillMatch: a website, a job-matching app, GitHub and LinkedIn guides, a CV Tailor and a data analysis section. Repo: https://github.com/TidyWeb/SkillMatch. Site: https://tidyweb.github.io/SkillMatch/
My main part: the graduate guides. I designed the first LinkedIn guide and reviewed Phil's GitHub guide in depth; Phil reviewed my LinkedIn guide. Everyone also fed into the app, CV Tailor and data ideas. If I correct any of this, use my version.

Cover, in this order, 2–4 questions each:
1. What I thought I was getting into, and how I felt at the start
2. What I actually did, day by day, especially the guides and the reviewing
3. What was hard (technical, teamwork, GitHub, time) and how I got through it
4. How my ideas changed, and one decision I'd make differently
5. How I used AI, and where it helped or got in the way
6. What it's done for me: skills, confidence, what's next

Follow up when an answer is vague. Ask for one concrete example. After the last section, show me a draft as Markdown with a heading per section, written in first person in my voice, and ask what to change. The first line must say: "Written with help from <name of AI>, from my own answers." Final file name: esmat-diary.md
```

## John

```
Interview me to write my project development diary. Ask ONE question at a time and wait for my answer. Use my words. Don't invent, don't flatter, don't polish away frustration.

Context: I'm John. In a 4-day Code Institute Data Analytics with AI hackathon (Oct 2026) our team of five (Esmat, John, Oana, Phil, SK) built SkillMatch: a website, a job-matching app, GitHub and LinkedIn guides, a CV Tailor and a data analysis section. Repo: https://github.com/TidyWeb/SkillMatch. Site: https://tidyweb.github.io/SkillMatch/
My main part: the data analysis. My notebook and folder (course skills vs market demand, the radar chart) started it. Oana and I led the analysis; the team looked at my work, asked what the data was telling us, and built the Data analysis section from it. If I correct any of this, use my version.

Cover, in this order, 2–4 questions each:
1. What I thought I was getting into, and how I felt at the start
2. What I actually did: the notebook, the data, the charts, the reviews and PRs
3. What was hard (data, Python, GitHub, feedback, time) and how I got through it
4. How my question and ideas changed, and one thing I'd do differently
5. How I used AI, and where it helped or got in the way
6. What it's done for me: skills, confidence, what's next

Follow up when an answer is vague. Ask for one concrete example. After the last section, show me a draft as Markdown with a heading per section, written in first person in my voice, and ask what to change. The first line must say: "Written with help from <name of AI>, from my own answers." Final file name: john-diary.md
```

## Oana

```
Interview me to write my project development diary. Ask ONE question at a time and wait for my answer. Use my words. Don't invent, don't flatter, don't polish away frustration.

Context: I'm Oana. In a 4-day Code Institute Data Analytics with AI hackathon (Oct 2026) our team of five (Esmat, John, Oana, Phil, SK) built SkillMatch: a website, a job-matching app, GitHub and LinkedIn guides, a CV Tailor and a data analysis section. Repo: https://github.com/TidyWeb/SkillMatch. Site: https://tidyweb.github.io/SkillMatch/
My main part: the app was my idea, shaped through group discussion. I took the project manager role, and with John I led the data analysis. If I correct any of this, use my version.

Cover, in this order, 2–4 questions each:
1. What I thought I was getting into, and how I felt at the start
2. What I actually did: the app idea, project management and the board, the data analysis
3. What was hard (coordination, GitHub, keeping the board current, time) and how I handled it
4. How my ideas changed, and one thing I'd do differently as PM
5. How I used AI, and where it helped or got in the way
6. What it's done for me: skills, confidence, what's next

Follow up when an answer is vague. Ask for one concrete example. After the last section, show me a draft as Markdown with a heading per section, written in first person in my voice, and ask what to change. The first line must say: "Written with help from <name of AI>, from my own answers." Final file name: oana-diary.md
```

## SK

```
Interview me to write my project development diary. Ask ONE question at a time and wait for my answer. Use my words. Don't invent, don't flatter, don't polish away frustration.

Context: I'm SK. In a 4-day Code Institute Data Analytics with AI hackathon (Oct 2026) our team of five (Esmat, John, Oana, Phil, SK) built SkillMatch: a website, a job-matching app, GitHub and LinkedIn guides, a CV Tailor and a data analysis section. Repo: https://github.com/TidyWeb/SkillMatch. Site: https://tidyweb.github.io/SkillMatch/
My main part: I joined the team late. I was vital to CV Tailor: the original installation, how it's applied, and reviewing it. I did the first full practice install and run-through with Phil, and a lot of quality testing on whether it was fit for purpose. If I correct any of this, use my version.

Cover, in this order, 2–4 questions each:
1. Joining late: what I expected, what I found, how I caught up
2. What I actually did: installing, testing, reviewing CV Tailor
3. What was hard (setup, instructions, tools, time) and how I got through it
4. What testing showed, how it changed the product, and one thing I'd do differently
5. How I used AI, and where it helped or got in the way
6. What it's done for me: skills, confidence, what's next

Follow up when an answer is vague. Ask for one concrete example. After the last section, show me a draft as Markdown with a heading per section, written in first person in my voice, and ask what to change. The first line must say: "Written with help from <name of AI>, from my own answers." Final file name: sk-diary.md
```

## Phil

```
Interview me to write my project development diary. Ask ONE question at a time and wait for my answer. Use my words. Don't invent, don't flatter, don't polish away frustration or arguments.

Context: I'm Phil. In a 4-day Code Institute Data Analytics with AI hackathon (Oct 2026) our team of five (Esmat, John, Oana, Phil, SK) built SkillMatch: a website, a job-matching app, GitHub and LinkedIn guides, a CV Tailor and a data analysis section. Repo: https://github.com/TidyWeb/SkillMatch. Site: https://tidyweb.github.io/SkillMatch/
My part: I took Data Architect but ended up doing most of the building: the app (Oana's idea), the GitHub guide, CV Tailor (a group idea), the site, the data pipeline and the repo, working through several AI agents. I reviewed Esmat's LinkedIn guide. If I correct anything, use my version.

Cover, in this order, 2–4 questions each:
1. What I thought I was getting into, and why I wanted Data Architect
2. What I actually did, and how the builder role grew
3. What was hard: the team, GitHub process, the board, AI agents, usage limits, time
4. How ideas changed, and what I'd do differently (board ownership, "Closes #", roles)
5. How I used AI: where it was brilliant, where it frustrated me
6. What it's done for me: strengths (ideas, iterating, spotting flaws), confidence, next steps

Follow up when an answer is vague. Ask for one concrete example. After the last section, show me a draft as Markdown with a heading per section, written in first person in my voice, and ask what to change. The first line must say: "Written with help from <name of AI>, from my own answers." Final file name: phil-diary.md
```
