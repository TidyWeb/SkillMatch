# SkillMatch

Free job matching for Code Institute Data Analytics with AI graduates moving into data, starting in the West Midlands.

## [Open SkillMatch](https://tidyweb.github.io/SkillMatch/)

[Try the app](https://skillmatch-926015010605.europe-west2.run.app)

## What's in it

- **Website:** start here for the project and its public pages. [Open SkillMatch](https://tidyweb.github.io/SkillMatch/)
- **Job matches:** search vacancies in the [SkillMatch app](https://skillmatch-926015010605.europe-west2.run.app).
- **GitHub guide:** make your projects easier to see on [GitHub](https://tidyweb.github.io/SkillMatch/project-visual-language/github-profile-guide/).
- **LinkedIn guide:** explain your move into data with the [LinkedIn guide](https://tidyweb.github.io/SkillMatch/project-visual-language/linkedin-profile-guide/).
- **CV Tailor:** set it up in Claude desktop with Desktop Commander, then use the SkillMatch Skill; your files stay in your own folder. [Open CV Tailor](https://tidyweb.github.io/SkillMatch/project-visual-language/tailor-my-cv/).
- **Data analysis:** explore one captured West Midlands search and its limits. [Read the analysis](https://tidyweb.github.io/SkillMatch/project-visual-language/skillmatch-da/).

## How it works

1. Open the [SkillMatch website](https://tidyweb.github.io/SkillMatch/).
2. Use the GitHub and LinkedIn guides to prepare your profiles.
3. Add your skills in the [app](https://skillmatch-926015010605.europe-west2.run.app) and search for jobs.
4. Open a job card and choose **Tailor my CV**.
5. Copy the job brief into Claude desktop, where it can be used with your CV and biography in your own SkillMatch Folder.

The job brief is carried in the page address after a `#` fragment. The app and CV Tailor page do not store it on their servers.

## Privacy

- No account or login is needed.
- Your profile stays in the browser tab. The app sends it with each search and does not store it on the server.
- Your CV and biography stay in your SkillMatch Folder on your computer. The app cannot open that folder.
- The job brief contains public advert details and may include match hints based on your profile.

## How it's built

- The app uses Python and Flask and runs on Google Cloud Run.
- A daily process collects adverts from official APIs and documented feeds where collection is permitted.
- Local Python rules compare job requirements with candidate-confirmed skills. No paid AI service writes the matches.
- The static website is hosted on GitHub Pages and follows the Navy A style.
- The analysis notebook uses the local data build. Public analysis pages show summary counts; source rows stay local. See the [Jupyter notebook](skillmatch-app/notebooks/skillmatch_analysis.ipynb).

## Run it yourself

Open the project in [GitHub Codespaces](https://codespaces.new/TidyWeb/SkillMatch), then follow the setup instructions in [`skillmatch-app/README.md`](skillmatch-app/README.md).

## Project structure

| Folder | What it contains |
|---|---|
| `skillmatch-app/` | The Flask app, data collection and matching rules. |
| `project-visual-language/` | Public pages, guides and data analysis. |
| `team-guides/` | The team hub and working guides. |
| `Research/` | Vacancy source research and project resources. |
| `project-development-diary/` | Each team member's honest reflection on the project. |
| Team folders | `Phil's Folder/`, `John's Folder/`, `Rahman SK's Folder/`, `Esmat's Folder/` and `Oana's Folder/`. |

## Data and limits

The analysis uses a captured search. It shows collected adverts, not the whole job market. Reed's results were partial and some searches reached their result limit. [Read the 30 October 2026 snapshot](https://github.com/TidyWeb/SkillMatch/tree/data-snapshots/data/live_snapshots/20261030_1848) or see the [data analysis](https://tidyweb.github.io/SkillMatch/project-visual-language/skillmatch-da/).

Advertiser and sentence labels that use AI judgement are marked as awaiting a human check. The licence does not cover the job adverts collected on the `data-snapshots` branch. That content belongs to Reed and the employers who posted it.

## Team

Built during a four-day Code Institute Data Analytics with AI hackathon in October 2026 by Esmat, John, Oana, Phil and SK.

## For the team

Team members: open the [team hub](https://tidyweb.github.io/SkillMatch/team-guides/) for guides, the project board and working documents.

## Licence

The code and written material in this repo are released under the MIT licence. See [LICENSE](LICENSE).

- Anyone can use, copy and adapt it, as long as they keep the licence notice.
- Work contributed by team members is released under the same licence.
- The licence does not cover the job adverts collected on the `data-snapshots` branch. That content belongs to Reed and the employers who posted it.
