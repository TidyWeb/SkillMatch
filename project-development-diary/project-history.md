# SkillMatch: project development history

This is a short history of how SkillMatch grew from a hackathon idea into a working app and a wider set of graduate support materials. Each milestone links to merged work or to the resulting project files. Planning images and board snapshots are labelled as records of what was proposed or visible at the time.

## Starting point

The four-day Code Institute hackathon set a data analytics challenge with AI. SkillMatch began with Oana's idea: help graduates find relevant first data jobs without having to sift through a blizzard of unsuitable adverts.

The first written plan, dated 16 October, proposed official job feeds, a Streamlit interface and local matching rules. A full early build on 21 October still used sample adverts while the team checked what real job sources allowed. These were starting choices, not the final architecture.

## Chronology

### 26 October — the project grows beyond a job finder

The team decided that a shortlist alone would not help graduates present themselves well or explain what the app found. The project widened to include analysis of vacancies and course coverage, guidance for GitHub and LinkedIn profiles, and a CV tailoring tool.

The matching idea also shifted towards transferable skills. A career changer might have years of useful experience without years in a data role, so a data-job title could not be the main test of fit.

### 28–29 October — clearer profiles and more careful matches

The profile form was simplified around skills and relevant experience. Match cards gained clearer tiers and a guard to check results after the first match pass. A separate relevance check stopped unrelated jobs from appearing as data-job matches.

Merged work: [PR #147](https://github.com/TidyWeb/SkillMatch/pull/147) and [PR #148](https://github.com/TidyWeb/SkillMatch/pull/148). The resulting app is documented in the [SkillMatch app README](https://github.com/TidyWeb/SkillMatch/blob/main/skillmatch-app/README.md).

### 29 October — the app moves towards reliable hosting

The team prepared the app for Google Cloud Run and added the health route needed by the host. This took SkillMatch from a local prototype towards a service that could be reached and checked online.

Merged work: [PR #149](https://github.com/TidyWeb/SkillMatch/pull/149) and [PR #151](https://github.com/TidyWeb/SkillMatch/pull/151).

### 29–30 October — one visual language and practical graduate guides

The team approved Navy A as the shared visual style. It was applied to the project visual-language area, the app and the graduate guides. The GitHub and LinkedIn guides turned profile advice into illustrated, step-by-step material.

The CV Tailor page and SkillMatch Skill added a way to use a vacancy's requirements alongside a person's CV. The later biography work was organised around transferable skills and examples from a person's working life.

Merged work: [PR #154](https://github.com/TidyWeb/SkillMatch/pull/154), [PR #155](https://github.com/TidyWeb/SkillMatch/pull/155), [PR #157](https://github.com/TidyWeb/SkillMatch/pull/157) and [PR #158](https://github.com/TidyWeb/SkillMatch/pull/158). See the [visual-language README](https://github.com/TidyWeb/SkillMatch/blob/main/project-visual-language/README.md), [LinkedIn guide](https://github.com/TidyWeb/SkillMatch/blob/main/project-visual-language/linkedin-profile-guide/index.html) and [CV Tailor page](https://github.com/TidyWeb/SkillMatch/blob/main/project-visual-language/tailor-my-cv/index.html).

### 30 October — team work and repository structure take shape

The project gained an overview page and a clearer home for team guides. Team contributions included a data analyst workbook, review-based improvements to the GitHub guide and organised folder guides.

The live app then moved into its own top-level folder, skillmatch-app, while the earlier prototype was archived. This made the working app and its history easier to distinguish.

Merged work: [PR #161](https://github.com/TidyWeb/SkillMatch/pull/161), [PR #163](https://github.com/TidyWeb/SkillMatch/pull/163), [PR #164](https://github.com/TidyWeb/SkillMatch/pull/164), [PR #165](https://github.com/TidyWeb/SkillMatch/pull/165) and [PR #167](https://github.com/TidyWeb/SkillMatch/pull/167).

### 31 October — the site brings the work together

The site gained a shared navigation, a CV Tailor section and an interactive data analysis section. Further updates connected the app back to the site, improved the CV Tailor journey and expanded the public project README with screenshots and an account of how the project was built.

Merged work: [PR #169](https://github.com/TidyWeb/SkillMatch/pull/169), [PR #170](https://github.com/TidyWeb/SkillMatch/pull/170), [PR #172](https://github.com/TidyWeb/SkillMatch/pull/172), [PR #173](https://github.com/TidyWeb/SkillMatch/pull/173), [PR #174](https://github.com/TidyWeb/SkillMatch/pull/174) and [PR #175](https://github.com/TidyWeb/SkillMatch/pull/175). The analysis is available in the [SkillMatch data analysis section](https://github.com/TidyWeb/SkillMatch/blob/main/project-visual-language/skillmatch-da/index.html).

### 31 October — the board becomes part of the project record

A review found that the project board had fallen behind work already merged. The team traced much of the gap to pull requests that did not use GitHub's issue-closing reference. The lesson was to make issue links part of the review and merge routine, and to give the project manager a clear role in board oversight.

The selected [board snapshots](board-snapshots/README.md) show several daily checkpoints. They record board state; they do not, on their own, prove that a task was completed.

### 1 November — the project diary opens to the team

The repository gained Phil's personal reflection and a shared method for other team members to write their own. The AI interviewer asks questions one at a time, draws out concrete examples, and produces a draft for the writer to review and edit.

Merged work: [PR #176](https://github.com/TidyWeb/SkillMatch/pull/176), [PR #177](https://github.com/TidyWeb/SkillMatch/pull/177) and [PR #178](https://github.com/TidyWeb/SkillMatch/pull/178). Read [Phil's diary](phil-diary.md) or the [diary instructions](README.md).

## Selected planning records

- [Team roadmap, 28 October](assets/roadmap/Roadmap_Team_20261028.png): a dated view of the intended route through the hackathon, not a claim that every planned date or task was met.
- [Role allocation proposal](assets/team-context/Team_Role_Allocation_Proposal.png): a proposal for dividing work, not a final record of each person's contribution.
- [GitHub collaboration guide shared through Discord](assets/team-context/SkillMatch_GitHub_Collaboration_Guide_Discord.png): a reference for branches, commits, pull requests and review. It records guidance, not proof that every step was followed from the start.
- [Journey colour options](assets/concept-planning/journey_colour_options_20261030.png): visual exploration dated 30 October.
- [Overview ochre pill mock-up](assets/concept-planning/overview_ochre_pill_mock_20261030.png): one concept for the project overview.
- [Overview pill colour tests](assets/concept-planning/overview_pill_colour_tests_20261030.png): a comparison of marker colours.
- [Overview layout faults](assets/concept-planning/overview_step2_faults_20261030.png): review notes from an intermediate layout.

## What was still ahead

The voice-based mock interviewer described in Phil's diary was a future idea, not a completed part of this project snapshot. Keeping that distinction makes the history useful as both a record of work done and a starting point for later work.

This page draws on the original hackathon brief, early planning, dated project records and merged pull requests. It summarises those sources rather than republishing the course handout or operational step-by-step prompts.
