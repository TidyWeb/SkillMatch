# Hackathon Diary: Project: SkillMatch

Written with help from ChatGPT, from my own answers.

# My AI Hackathon Diary

## 27 October–1 November 2026

## The team and project

Our team of five—Esmat, John, Oana, Phil, and SK—built SkillMatch, a website and job-matching app. I got on well with everyone in the team, and we worked together throughout the project.

## Working on the radar chart

I revisited my work several times because I did not initially understand some of the feedback. It was difficult to acknowledge that my first version was not quite right.

For example, the radar chart showed a value of 100% for an existing skill, while another plot showed the proportion of job vacancies requiring that skill. I was unsure how the user’s skill level could be represented as an absolute value of 0 or 1 while the other metric varied. This did not align with my understanding of radar charts. Phil’s feedback helped me identify and correct the issue, and I was ultimately able to complete the pull request.

## Working with the existing prototype

Working with the existing prototype was challenging. I found it difficult to rely on AI-generated research about how it worked. I tried a different AI agent, but it introduced its own assumptions and did not stay within the intended scope.

There was also a large amount of material to review, and the volume of text in some messages felt overwhelming.

## Learning from pull request #152

I found it particularly difficult to set aside pull request #152, **“Add the initial data analysis stage to insights html,”** because I had invested a lot of effort in it. However, the AI agent had changed 21 files, which I did not consider appropriate to merge into the main branch. I decided to redo that stage of the insights work in smaller pull requests.

After reconsidering my approach, I realised that the work I wanted to retain was in my notebook, while the AI agent’s other changes were not necessary for my submission. I reviewed the feedback carefully, identified the work I needed to keep, cloned the original repository again, and added only the notebook rather than the HTML insights page.

## What I learned about the data

I learned more about how the existing prototype worked and how the data it collected could help match a user’s profile with the skills required in the workplace.

As the project developed, I recognised the need to address the skills gap people may face after completing the course. Identifying those skills and measuring demand for them in job vacancies helped shape our data analysis. This gave us a way to address the issue and provide users with more useful information.

## What I would plan differently

If I were to do this project again, I would ask Phil, the key stakeholder, to provide a hypothesis for the data analysis. Having that direction from the outset would help me plan the work more effectively.

## How I used AI

I used Copilot Chat and GitHub Copilot for coding support, and Gemini 3.5 Flash and later Claude for discussion. As a team, we communicated with Phil, who used his own AI agents, “AI Kevin” and “AI Rory.” At times, they felt like the sixth and seventh members of the team.

Once I understood the requirements, Gemini 3.5 Flash helped me make the specific changes needed to use the radar chart effectively. GitHub Copilot was less helpful when it changed more than 20 files beyond the scope of my request.

## Skills I gained

I developed my ability to create pull requests in GitHub. I can now use them to contribute to larger team projects where members work on separate branches.

I also strengthened my communication skills. Oana, our project manager, helped ensure that communication remained central to the team’s work.

## Python, machine learning, and future ideas

I was comfortable with the fact that the project did not require Python or machine learning. I had already trained models with scikit-learn in my previous three projects, with mixed results. Since I understand the importance of having a sufficiently large dataset, I agree that waiting before introducing machine learning was the right decision.

Machine learning could be a useful future enhancement. For example, it might help forecast how demand for particular skills changes over time.
