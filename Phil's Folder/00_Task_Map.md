# SkillMatch hackathon task map

**Purpose:** give every teammate a useful, evidence-based workstream while the project is still being shaped, then turn the findings into a small buildable scope.

## What we are trying to make

SkillMatch is intended to help Code Institute Data Analytics with AI graduates find first or early-career data and insight roles that are plausible for their skills and practical circumstances. The starting geography is the West Midlands, with UK remote roles included only when UK eligibility is clear. A useful result should explain why a role appears, what skills match or are missing, what experience it asks for, where the work happens, and which details remain unknown.

The working plan proposes local Python matching rules, candidate-confirmed skills, and no paid LLM service. Advertised salary should be shown as supplied; missing pay stays unknown. The route for travel-time estimates, exact salary handling, approved vacancy sources, and the deployed app format are still decisions.

## Current evidence and open decisions

- The vacancy library has 96 source records. They are research leads, not 96 independent feeds, a market census, or permission to collect data.
- The source research has not approved any source for automated collection. Publicly viewable adverts do not automatically permit copying, storing, analysing, or republishing their content.
- The written working plan proposes Streamlit. Older project-fit and team-allocation visuals describe a custom-coded web app and say not to use Streamlit. The team must choose after a short feasibility comparison.
- The current plan says early-career suitability must be judged from the actual requirements, not a title alone. It also says not to show an unexplained match percentage.
- A prior £30,000 salary ceiling conflicts with the newer source research, which recommends no mandatory salary cutoff. Leave the policy open until the team records a decision.
- Existing files: [working plan](../../Job_Search_App_Plan.md), [source inventory](../../Research/Vacancy_Source_Inventory.md), [search method](../../Research/Vacancy_Sources/Search_Method_and_Coverage.md), [hackathon brief](../../Hackathon%20Instructions.md), and [role handover](../../Hackathon%20Handover.md).

## Workstreams and required outputs

| ID | Workstream | Suggested lead | Output before coding expands | Complete when |
|---|---|---|---|---|
| A | Source identification and verification | Rotating Data Analyst or Data Architect | A small comparison of source value, a permitted-data route, and sample adverts with evidence | At least one source is cleared for the intended demo use, or the team records a safe fallback such as synthetic test records and linked discovery only |
| B | User experience and user flow | Rotating Data Analyst | One user journey, a rough wireframe, and short feedback notes | A graduate can complete the agreed task and understand the result, match reasons, gaps, location, and uncertainty |
| C | Platform and architecture | Rotating Data Architect | A decision note comparing the realistic build and hosting choices | One option is chosen against time, skills, privacy, demo reliability, and deployment evidence; conflicting old recommendations are reconciled |
| D | Data contract and matching rules | Data Architect with Analyst review | Vacancy/profile fields, classification rules, and edge-case decisions | The same sample advert and profile produce an explainable result that the team can check by hand |
| E | Integration, validation, and demo | Project Manager with all contributors | Test cases, a data-quality check, a demo path, and presentation notes | The app and analysis work from a known sample, limits are clear, and the team can reproduce and explain the result |

These are workstream owners, not permanent role assignments. Keep a named owner and reviewer for each output so handoffs do not reset when the formal roles rotate.

## Role rotation

Rotate four responsibilities daily so all four team members have a clear role: **Project Manager, Data Architect, Data Analyst, and Integration and Validation**. These are practical day-to-day responsibilities, not job titles or exclusive ownership of every related task. Workstream owners stay attached to their deliverables across days.

| Responsibility | What this person looks after | Likely task-pack work |
|---|---|---|
| **Project Manager** | Keeps the team moving together: confirms the day's goal, checks owners and reviewers, updates the task board, records decisions, raises blockers early, and keeps the final demo and handoffs on track. This person helps the team decide what to finish or defer; they do not have to manage every detail themselves. | Kickoff decision log and role/workstream coordination in this map; planning and demo coordination in [Task E — Integration, validation, and demo](05_Integration_Validation_and_Demo.md). |
| **Data Architect** | Makes the app's technical and data structure understandable: compares realistic platform choices, agrees how information moves through the app, defines vacancy and candidate fields, and helps make matching rules consistent and explainable. Checks that design choices fit the source evidence and the time available. | [Task C — Platform and architecture decision](03_Platform_and_Architecture_Decision.md) and [Task D — Data contract and matching rules](04_Data_Contract_and_Matching_Rules.md); consults [Task A](01_Source_Identification_and_Verification.md) about source constraints. |
| **Data Analyst** | Builds the evidence about the problem and the sample: checks what adverts actually say, records source and date evidence, helps shape and test the graduate's user journey, and prepares a modest finding from the reviewed data. Separates observed facts from the team's interpretation and explains sample limitations. | [Task A — Source identification and verification](01_Source_Identification_and_Verification.md), [Task B — UX and user flow](02_UX_and_User_Flow.md), and the sample-analysis work in [Task D](04_Data_Contract_and_Matching_Rules.md) and [Task E](05_Integration_Validation_and_Demo.md). |
| **Integration and Validation** | Connects handoffs and checks that the agreed pieces work together: tracks the sample's provenance, coordinates joining data, rules, and screens with whoever is building them, runs the acceptance scenarios, records pass/fail/blockers, and checks that another teammate can repeat the demo. This role coordinates checking; it does not make one person solely responsible for all coding or testing. | [Task E — Integration, validation, and demo](05_Integration_Validation_and_Demo.md), and checks the results from [Task A](01_Source_Identification_and_Verification.md), [Task B](02_UX_and_User_Flow.md), [Task C](03_Platform_and_Architecture_Decision.md), and [Task D](04_Data_Contract_and_Matching_Rules.md). |

Rotate these responsibilities using the four-day pattern below. Each person takes each responsibility once. The daily role guides that person's focus; it does not stop teammates from helping with other workstreams or reviewing one another's work.

| Day | Person A | Person B | Person C | Person D |
|---|---|---|---|---|
| 1 | Project Manager | Data Architect | Data Analyst | Integration and Validation |
| 2 | Integration and Validation | Project Manager | Data Architect | Data Analyst |
| 3 | Data Analyst | Integration and Validation | Project Manager | Data Architect |
| 4 | Data Architect | Data Analyst | Integration and Validation | Project Manager |

Replace A/B/C/D with team members' names at kickoff. Across the four days, each person takes each responsibility once. Keep the workstream owner attached to their deliverable across days. If Phil is the main coder, record **implementation** as a continuing responsibility on the task board. The Integration and Validation role still rotates to coordinate checks and handoffs; teammates can also reduce uncertainty, supply reviewed sample records, test flows, review rules, and prepare the analysis story.

The hackathon brief's role descriptions put dashboard building with the Data Analyst, while parts of its daily schedule assign dashboard work to the Data Architect. Agree at kickoff who owns the data pipeline and who owns the user-facing analysis/dashboard, and capture that in the decision log.

## Four-day route

Use the official four-day brief as the baseline. It expects a cleaned dataset, ETL/data quality work, visual analysis, documentation, and a presentation. SkillMatch can add a working app, but should still produce a defensible data-analysis output from the sample.

| Day | Main purpose | End-of-day checkpoint |
|---|---|---|
| 1 | Parallel source, UX, platform, and matching-rule investigations; narrow the sample and scope | Record the key decisions by late afternoon: permitted data/fallback, target user flow, platform direction, and a small MVP |
| 2 | Build a vertical slice with a small, traceable dataset and transparent matching | One known candidate and a few known vacancies can run from input to explainable results; first basic chart/table works |
| 3 | Improve the flow, inspect data quality, and integrate team findings | Freeze new features late in the day; resolve high-impact errors and prepare the demo narrative |
| 4 | Test, document, rehearse, and present | Reproducible demo, README/project notes, limitations, and contribution summary are ready |

## Three-day compressed route

Keep the investigation time-boxed so it does not consume the build window.

| Day | Main purpose | End-of-day checkpoint |
|---|---|---|
| 1 | Morning investigations and decisions; afternoon data model, sample preparation, and one user-flow sketch | By lunch, decide the source route or safe fallback, platform, and MVP; by 5pm, a clean sample and a small build plan exist |
| 2 | Build the smallest end-to-end slice; teammates add reviewed records, test rules, and check the UX | Working journey from candidate inputs to explained vacancy results plus one honest sample insight |
| 3 | No new feature work after the morning; integration fixes, test, README, demo rehearsal, presentation | Demonstrate the working slice and state its evidence limits clearly |

## MVP boundary

**Aim to show:** a candidate can enter or select a small skills profile and practical preferences; see a small set of traceable vacancies; understand matches, gaps, experience/seniority judgement, workplace/arrangement, source, and missing facts; and explore one modest finding about the sample.

**Keep outside the first build unless the evidence and time make them straightforward:** broad scraping, a complete live-market feed, user accounts, CV upload, long-term storage of a real postcode, an opaque score, an unverified travel-cost estimate, or a native mobile app. Do not imply that a small convenience sample represents the whole regional job market.

## Kickoff decision log

Copy one row per decision and keep the evidence link or reason beside it.

| Decision | Options considered | Decision and reason | Evidence / owner | Date |
|---|---|---|---|---|
| First source or safe fallback |  |  |  |  |
| Data-use permission and attribution |  |  |  |  |
| Candidate flow and key screens |  |  |  |  |
| Local, hosted, or static delivery |  |  |  |  |
| Salary display/filter policy |  |  |  |  |
| Location and travel behaviour |  |  |  |  |
| Early-career classification |  |  |  |  |
| Dashboard / analysis owner |  |  |  |  |

## Task sheets

1. [Source identification and verification](01_Source_Identification_and_Verification.md)
2. [UX and user flow](02_UX_and_User_Flow.md)
3. [Platform and architecture decision](03_Platform_and_Architecture_Decision.md)
4. [Data contract and matching rules](04_Data_Contract_and_Matching_Rules.md)
5. [Integration, validation, and demo](05_Integration_Validation_and_Demo.md)
