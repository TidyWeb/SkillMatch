# SkillMatch

## [👉 OPEN THE TEAM HUB](https://tidyweb.github.io/SkillMatch/)

Guides, the project board, prototypes and plans, all as clickable web pages. Start there.

An early-career job-matching project for Code Institute Data Analytics with AI graduates.

- **Focus:** West Midlands vacancies and remote roles with confirmed UK eligibility.
- **Matching:** compare advert requirements with candidate-confirmed skills using local Python rules and supporting advert text; no paid LLM API.
- **Travel:** account for workplace, remote or hybrid arrangements, and candidate commute preferences.
- **Collection:** use APIs, feeds or other permitted source routes.

## Status

A working prototype exists: a Flask web app that compares a graduate's skills with West Midlands vacancies. Its code is in [`skillmatch-app/`](skillmatch-app/). **[Try it in your browser](https://codespaces.new/TidyWeb/SkillMatch)** with GitHub Codespaces: nothing to install. The prototype will eventually show live jobs. For now, Codespaces runs a saved copy of a live collection; if that copy is unavailable, it uses sample adverts. We are now designing the interface; the prototype designs will appear on the [team hub](https://tidyweb.github.io/SkillMatch/) as they are ready. Salary policy and the travel-routing provider remain open team decisions. Keep missing pay unknown and do not estimate it.

## Project documents

- [VIEW THE PROJECT PLAN AS A WEB PAGE](https://tidyweb.github.io/SkillMatch/Job_Search_App_Plan.html)
- [Code Institute Resources Visual Index](https://tidyweb.github.io/SkillMatch/Resources/Code_Institute_Resource_Index.html)
- [Code Institute resources — printable PDF index](Resources/Code_Institute_Resource_Index.pdf)
- [Open the Code Institute resources in the LMS (sign-in required)](https://lms.codeinstitute.net/learner_resources/list/125519#resource_4602588)
- [Project plan (Markdown)](Job_Search_App_Plan.md)
- [Vacancy source inventory](Research/Vacancy_Source_Inventory.md)
- [Source library](Research/Vacancy_Sources/Source_Library.html)
- [Search method and coverage](Research/Vacancy_Sources/Search_Method_and_Coverage.md)

## Viewing the Code Institute resource index

Open the [Code Institute Resources Visual Index](https://tidyweb.github.io/SkillMatch/Resources/Code_Institute_Resource_Index.html) to follow the links to the LMS. You need an internet connection and your own Code Institute sign-in. The PDF is a printable list of resource names and links; it does not contain the course materials.

## Viewing the HTML plan

From the repository page, find **Project documents** in this README and select **VIEW THE PROJECT PLAN AS A WEB PAGE**. This opens the rendered plan published with GitHub Pages.

If you open `Job_Search_App_Plan.html` from the repository's **Code** file list and see HTML tags, you are viewing the source file. Return to this README and use the webpage link to read the formatted plan.

GitHub Pages displays these static pages; it does not run the Flask application itself.

## Licence

The code and written material in this repo are released under the MIT licence. See [LICENSE](LICENSE).

- Anyone can use, copy and adapt it, as long as they keep the licence notice.
- Work contributed by team members is released under the same licence.
- The licence does not cover the job adverts collected on the `data-snapshots` branch. That content belongs to Reed and the employers who posted it.
