# Task C — platform and architecture decision

## Purpose

Choose a build and demo route that the team can finish, explain, and safely show within three or four days. Resolve the existing disagreement between the written Streamlit plan and older visuals proposing a custom-coded web app.

The team also needs to decide how graduates will access and use SkillMatch. Possibilities include a hosted website that a user visits, with or without signing in; a Flask web application packaged in a container so it can run in different operating-system environments; or a hosted Streamlit app. Each route affects how easy the service is to reach, build, share, and keep available. Streamlit Community Cloud can hibernate inactive apps, so a visitor may first see a sleeping-app page and need to wake the app before using it. These delivery questions are supplementary to the core task, but matter if SkillMatch is to be useful to graduates beyond the hackathon.

**Owner:** __________  **Reviewer:** __________  **Rotating hat today:** __________

## Options to compare

| Option | What it can suit | Questions to prove before choosing |
|---|---|---|
| Local Python app (Streamlit is the current written proposal) | Fast data-to-interface prototype with a Python-focused build | Can the team make the interaction and responsive layout clear enough? Can the demo run reliably from the project setup? |
| Hosted Streamlit app | Shareable browser demo built from a repository and entry-point file | What repository/app access is required? Would the data or candidate inputs be public, stored, or exposed? Is hosting and setup achievable in the remaining time? |
| Flask with a custom frontend | More control over route, page, and interaction design; Python backend | Can the team build and maintain both backend and frontend in time? Which production host and WSGI setup would be used? How will input data be protected? |
| Static GitHub Pages | Project plan, instructions, and a static mock-up | It can publish static files but cannot run a Python backend. Could a static prototype meet the demo need, or is it only for project documentation? |
| Progressive web app or native mobile app | Potential later installable/mobile experience | Is this needed to prove the user need? What manifest, browser support, mobile packaging, and extra testing would add? Keep native mobile outside the hackathon MVP unless the team has a ready, proven path. |

## Short decision process

### 1. Agree the demo requirement

Write one sentence describing what must work on demo day: for example, “A user opens the app in a browser, chooses a small profile, and sees a traceable, explained shortlist from a reviewed sample.” Also say whether internet access is guaranteed and whether users must access the demo outside the team.

### 2. Compare the two most viable choices

Do not attempt a full implementation of every option. Score each 1–3 and add a short reason, using evidence from the current team and a small throwaway spike only if it answers a real uncertainty.

| Criterion | Weight or importance | Local Streamlit | Hosted Streamlit | Flask/custom | Static Pages |
|---|---|---:|---:|---:|---:|
| Can be built and debugged in remaining time |  |  |  |  |  |
| Fits the team's Python and frontend skills |  |  |  |  |  |
| Supports the UX the team agreed |  |  |  |  |  |
| Handles sample data and user inputs appropriately |  |  |  |  |  |
| Demo works reliably on the available network/devices |  |  |  |  |  |
| Can be shared with intended reviewers |  |  |  |  |  |
| Setup and handover are understandable |  |  |  |  |  |

### 3. Record the boundary between project site and app

The existing GitHub Pages site displays the static project plan. It does not run the future Python matching application. Keep the plan page and the application deployment as separate things in the architecture decision.

### 4. Decide what “mobile” means for this hackathon

Test the chosen browser flow at a narrow viewport. A responsive web page may be enough to demonstrate mobile usability. Treat PWA installation as a later option, and native mobile packaging as a separate project unless the team proves a very low-cost route.

## Evidence links for the comparison

- [GitHub Pages: creating a site](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [Streamlit Community Cloud: deploy an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app)
- [Streamlit Community Cloud: share an app](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app)
- [Streamlit Community Cloud: app hibernation and waking](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)
- [Flask: deploying to production](https://flask.palletsprojects.com/en/stable/deploying/)
- [MDN: making a PWA installable](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable)

Use these documents to confirm current requirements and limitations during the hackathon. Do not rely on a demo deployment with credentials or personal data in public code.

## Decision template

**Chosen route:**  
**Why it fits the user journey and remaining time:**  
**What the team tested or verified:**  
**How the app will be run/shared for the demo:**  
**What data and user inputs are used:**  
**What is deferred:**  
**Decision owner / date:**  

## Ready-to-close checklist

- [ ] Streamlit versus custom-web recommendations from the existing materials have been resolved in the decision log.
- [ ] The team has separated the static GitHub Pages project plan from the Python app hosting decision.
- [ ] Sharing, data exposure, and demo reliability have been considered, not just coding speed.
- [ ] A narrow-screen browser view has a clear purpose; native mobile is not assumed.
- [ ] The selected route has a short setup and run instruction for the next contributor.
