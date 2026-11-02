# SK - Personal Project Development Diary: SkillMatch Hackathon

> Written with help from Microsoft 365 Copilot, from my own answers.

## Project Context

SkillMatch was a hackathon project developed by me and four other students as part of our 16-week Code Institute Data Analytics and AI course. My involvement started differently from the other members because I was initially part of another team. That team was later reshuffled and its members moved into different groups, which resulted in me joining the SkillMatch team after the project had already started.

When I joined, the project idea had already been established, a roadmap had been created, and the other team members had begun development. This meant that my first priority was not to start building immediately, but to understand what was already in place and identify where I could contribute effectively.

## Joining an Existing Project

On my first day with the SkillMatch team, I asked questions about the project's objective, what my role would be, how we could cooperate to achieve the objective, and who was responsible for the different areas of work. This helped me understand the existing project structure and how my contribution would fit alongside the work already underway.

I was designated to work on data architecture with Phil and to carry out biography/bio-match testing using scripts that had already been created. Joining at this stage challenged me to adapt quickly to an established project rather than being involved from the beginning.

## Biography and Bio-Match Testing

One of my main contributions was testing the biography-matching process. I downloaded and configured the free version of Claude on my local computer and tested the prompt that had been created for the SkillMatch project.

I approached the work using principles from software user acceptance and validation testing. I ran the process, observed its behaviour, documented my findings, and produced reports identifying areas that could be improved.

One of the first issues I identified was that the biography-matching process was asking too many questions. Although the questions were intended to gather information for the project, the process was longer than necessary for creating a useful persona. I documented this issue and reported it to the team. The process was subsequently revised so that the number of questions was limited while still collecting the information required for the persona.

## Testing Improvements and the Complete User Journey

My findings were documented in Markdown files and pushed to the GitHub repository. Phil addressed the reported issue with AI assistance and an updated version was produced.

I then tested the updated file using the same approach that I had used for my original testing and documented the new findings. This allowed the revised behaviour to be checked against the issue identified during the earlier test.

I also tested whether the SkillMatch application could complete a broader user journey. This included checking whether the application could produce a person's CV from biography information, use that information when matching the person against a job advertisement, and save the generated CV to the local computer. Following testing and iterative corrections, this test passed.

This experience helped me understand that testing is not simply about checking whether something runs. It also requires looking at the user's experience, identifying weaknesses, documenting evidence, making improvements, and then testing the revised version again.

## Technical Challenges

One challenge involved setting up Claude correctly on my local computer. The custom configuration required local computer access to be enabled. Identifying this requirement and completing the setup took longer than I initially expected because the instructions were not immediately clear to me. After several attempts and carefully observing what was happening, I resolved the setup issue and was able to continue testing.

Git and GitHub collaboration was another significant learning challenge. Initially, I found it difficult to create a separate branch for my work and understand the correct process for merging my contribution into the main branch after team approval. I also needed to become more confident using the VS Code terminal to obtain the latest team updates and correctly use the pull, push and merge workflow.

To improve my understanding, I followed guidance from Code Institute instructor Mr Vasi and used Microsoft Copilot for additional explanations. I practised the workflow several times and tested the process myself. Repetition helped me develop a clearer practical understanding of collaborative Git and GitHub workflows.

## Using AI Responsibly

AI was an important supporting tool during the project, but I did not treat AI output as automatically correct. I used AI advice as guidance and validated suggestions using my existing knowledge, my understanding of the project context, and the outcome I was trying to achieve. The main benefit was that AI helped speed up parts of my working process.

I used tools including Claude, Microsoft Copilot, Perplexity and other AI models during different activities. A recurring problem was that AI could move in a very generic direction rather than remaining aligned with the specific SkillMatch requirements. When this happened, I did not simply accept the response. I iterated on the instructions and revised my prompt engineering to provide clearer context and direction.

This taught me that effective use of AI still requires human judgement. AI could help me work faster and explore possible solutions, but I needed to understand the objective, evaluate the response and redirect the AI when its output did not match the project context.

## Remote Team Collaboration

The biggest learning outcome from the hackathon was learning how to collaborate with a team remotely. Because I joined after the project had already started, I also learned how to enter an existing team, understand work that was already underway, identify my responsibilities, and begin contributing without having participated in the project's initial planning.

The experience showed me the importance of communication, clearly defined responsibilities, shared documentation and version-control practices when several people are contributing to the same project from different locations.

## What I Would Do Differently

If I were starting another hackathon from the beginning, I would place more emphasis on creating a clear roadmap early. I would also make sure that roles and responsibilities were clearly defined and documented.

I would want the project idea to be developed through group discussion so that team members could contribute to the direction of the project and establish a shared understanding before development progressed. I would document those decisions so that new or existing team members could understand the project structure, responsibilities and direction more easily.

## Personal Reflection and Development

Although I contributed to specific sections of the SkillMatch project rather than developing the entire solution, the experience gave me a much better understanding of how different parts of a collaborative technical project fit together.

I developed practical experience in testing and validation, documenting findings, using AI critically, improving prompts, working with Git and GitHub, and collaborating with a remote team. Just as importantly, I experienced what it is like to join a project that is already underway and still find a way to contribute.

My most important personal outcome is that I now have a stronger understanding of the architectural thinking and working practices needed to reproduce a similar project structure from scratch. I can take the lessons from SkillMatch into future projects, especially around planning, architecture, team responsibilities, testing, documentation, version control and responsible use of AI.
