"""Build notebooks/skillmatch_analysis.ipynb (and optionally run it).

Usage:
    uv sync --group notebook
    uv run python scripts/build_notebook.py            # write the notebook
    uv run python scripts/build_notebook.py --execute  # write it and run every cell

The notebook reads the SQLite build (data/processed/skillmatch.db, or $SKILLMATCH_DB).
Its outputs contain only counts and statistics, never advert text.
"""

import argparse

import nbformat as nbf

from skillmatch import config

CELLS = [
    (
        "md",
        """# SkillMatch: what entry-level data adverts in the West Midlands ask for

This notebook reads the SkillMatch database, the same SQLite file the web app serves, and tests two hypotheses about the adverts it holds. Every figure states its *n* and the data mode, because a nightly snapshot from a few sources is a **sample**, not the whole job market.

**Definitions**
- *Shown adverts*: data roles in the West Midlands or UK-remote, not senior by title, not a training course, de-duplicated.
- *Entry-plausible*: no explicit demand for experience in a data role, or at most a year while the advert welcomes newcomers (entry signals or "or equivalent experience").
- *Metropolitan county*: Birmingham, Coventry, Dudley, Sandwell, Solihull, Walsall and Wolverhampton. *Wider region*: Herefordshire, Shropshire, Staffordshire, Warwickshire and Worcestershire, including Telford and Wrekin and Stoke-on-Trent.""",
    ),
    (
        "code",
        """import os
import sqlite3
import json

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from skillmatch import config
from skillmatch.insights import entry_plausible

DB = os.environ.get("SKILLMATCH_DB", str(config.DB_PATH))
conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
meta = dict(conn.execute("select key, value from meta").fetchall())
MODE = "live snapshot " + meta["snapshot_date"] if meta["data_mode"] == "live" else "synthetic fixtures"
print(f"Database: {DB}")
print(f"Data mode: {MODE} (built {meta['built_at']})")""",
    ),
    (
        "code",
        """vac = pd.read_sql("select * from vacancies", conn)
req = pd.read_sql("select * from requirements", conn)
tags = pd.read_sql("select * from requirement_tags", conn)
vac["entry_signals"] = vac["entry_signals"].map(lambda s: json.loads(s or "[]"))

shown = vac[vac["excluded_reason"].isna() & (vac["is_primary"] == 1)].copy()
shown["entry_plausible"] = [entry_plausible(r) for r in shown.to_dict("records")]
print(f"All adverts held: {len(vac)} | primary (after de-duplication): {int((vac['is_primary'] == 1).sum())}")
print(f"Shown adverts: n = {len(shown)}; entry-plausible: {int(shown['entry_plausible'].sum())}")
print()
print("Why the rest are hidden (primary records):")
print(vac[vac["is_primary"] == 1]["excluded_reason"].value_counts().to_string())""",
    ),
    (
        "md",
        """## Hypothesis 1: is entry-level work more common in the metropolitan county?

- **H0:** the share of entry-plausible adverts is the same in the West Midlands metropolitan county as in the wider region.
- **H1:** the shares differ (two-sided).

Test: chi-square test of independence on the 2×2 table, or Fisher's exact test when any expected count is below 5. UK-remote adverts and adverts with no clear location are left out, because they belong to neither area.""",
    ),
    (
        "code",
        """METRO = ("birmingham", "coventry", "dudley", "sandwell", "solihull", "walsall", "wolverhampton")


def area(county):
    if not isinstance(county, str) or not county:
        return None
    c = county.lower()
    return "metropolitan county" if any(m in c for m in METRO) else "wider region"


def test_2x2(table):
    \"\"\"Chi-square when every expected count is at least 5, otherwise Fisher's exact.\"\"\"
    chi2, p_chi, dof, expected = stats.chi2_contingency(table, correction=True)
    if (expected < 5).any():
        odds, p = stats.fisher_exact(table)
        return "Fisher's exact test", p, odds, expected
    return f"chi-square (dof={dof}, statistic={chi2:.2f})", p_chi, None, expected


local = shown[(shown["is_remote"] == 0) & (shown["region"] == "West Midlands")].copy()
local["area"] = local["county"].map(area)
local = local[local["area"].notna()]
t1 = pd.crosstab(local["area"], local["entry_plausible"]).reindex(columns=[True, False], fill_value=0)
t1.columns = ["entry-plausible", "asks for more experience"]
print(f"n = {len(local)} located West Midlands adverts · {MODE}")
print(t1.to_string())
print()
print("Share entry-plausible:", (t1["entry-plausible"] / t1.sum(axis=1)).round(2).to_dict())
name, p, odds, expected = test_2x2(t1.values)
print(f"Test: {name}; p = {p:.3f}" + (f"; odds ratio = {odds:.2f}" if odds is not None else ""))
print("Expected counts under H0:", expected.round(1).tolist())""",
    ),
    (
        "md",
        """**Reading it.** With a p-value above 0.05 we cannot reject H0: this snapshot gives no evidence that entry-level work is more (or less) common in the metropolitan county than in the wider region. A small *n* gives the test little power, so "no evidence of a difference" is **not** evidence that there is no difference. Re-run the notebook on several nightly snapshots before drawing conclusions.""",
    ),
    (
        "md",
        """## Hypothesis 2: do "junior" titles ask for 2+ years in data as often as other adverts?

- **H0:** adverts with junior, graduate, entry-level, trainee, apprentice or assistant in the title ask for 2+ years' experience in a data role as often as other adverts.
- **H1:** the rates differ (two-sided).

"Asks for 2+ years" uses the parser's explicit data-experience demand (essential statements only, for example "2+ years as a data analyst", "3 years' SQL").""",
    ),
    (
        "code",
        """JUNIOR = r"\\b(?:junior|graduate|entry[\\s-]level|trainee|apprentice|assistant)\\b"
shown["junior_title"] = shown["title"].str.contains(JUNIOR, case=False, regex=True)
shown["asks_2plus"] = shown["data_years"].fillna(0) >= 2
t2 = pd.crosstab(shown["junior_title"], shown["asks_2plus"]).reindex(index=[True, False], columns=[True, False], fill_value=0)
t2.index = ["junior-type title", "other title"]
t2.columns = ["asks 2+ years in data", "doesn't"]
print(f"n = {len(shown)} shown adverts · {MODE}")
print(t2.to_string())
name, p, odds, expected = test_2x2(t2.values)
print(f"Test: {name}; p = {p:.3f}" + (f"; odds ratio = {odds:.2f}" if odds is not None else ""))""",
    ),
    (
        "md",
        """**Reading it.** Look at the counts before the p-value. On the live Reed sample we studied for the parser (October 2026), a "Junior Data Specialist" demanded industry experience and a "Junior Commercial Finance Analyst" wanted 1–2 years after graduating. The title is not the requirement, which is why SkillMatch checks every advert's requirements rather than trusting "junior". With few junior-titled adverts in one snapshot, the test has little power.""",
    ),
    (
        "md",
        """## Which transferable competencies do entry-plausible adverts ask for most?

Counted once per advert when any essential or desirable requirement signals the competency. This is the evidence for SkillMatch's core idea: these are the skills career-changers already have.""",
    ),
    (
        "code",
        """from skillmatch.taxonomy import get_taxonomy

tax = get_taxonomy()
entry_ids = set(shown.loc[shown["entry_plausible"], "vacancy_id"])
counted = req[req["strength"].isin(["essential", "desirable"]) & req["vacancy_id"].isin(entry_ids)]
t = tags.merge(counted[["req_id", "vacancy_id"]], on="req_id")
comp = (
    t[t["tag_type"] == "competency"].drop_duplicates(["vacancy_id", "tag_id"])["tag_id"].value_counts().head(12)
)
comp.index = [tax.competencies[i].label for i in comp.index]
n_entry = len(entry_ids)
print(f"n = {n_entry} entry-plausible adverts · {MODE}")
print(comp.to_string())

fig, ax = plt.subplots(figsize=(8, 5))
comp.sort_values().plot.barh(ax=ax, color="#1f4e8c")
ax.set_xlabel("Adverts asking for it")
ax.set_title(f"Competencies most asked for in entry-plausible adverts (n = {n_entry}; {MODE})", fontsize=10)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.show()""",
    ),
    (
        "code",
        """skills = t[t["tag_type"] == "skill"].drop_duplicates(["vacancy_id", "tag_id"])["tag_id"].value_counts().head(12)
skills.index = [tax.skills[i].label + (" (on the course)" if tax.skills[i].course_covered else "") for i in skills.index]
print(f"Technical skills most asked for · n = {n_entry} entry-plausible adverts · {MODE}")
print(skills.to_string())
unclassified = counted[~counted["req_id"].isin(tags["req_id"])]
print(f"\\nRequirements we could not classify: {len(unclassified)} of {len(counted)}")""",
    ),
    (
        "md",
        """## Limitations

- **Sample, not census.** One snapshot from the sources SkillMatch can read officially (Reed's API, three employer job boards, two remote boards). Councils, the NHS, charities and many recruiters are not collected (they appear only as links), so the counts can't describe the whole West Midlands market.
- **Rule-based reading.** Requirements are classified and tagged by rules over a draft vocabulary. Some are missed or misread (see the share left unclassified), and the vocabulary decides what counts as which competency.
- **Duplicates and agencies.** Agencies repost roles. De-duplication groups exact and near-identical adverts, but some duplicates will survive and some distinct roles may be merged.
- **Location.** Regions come from postcodes.io or our town table. County-only adverts are placed at a representative town and flagged as approximate.
- **Small n.** Both hypothesis tests have little statistical power on one night's data. Treat the p-values as a prompt to collect more snapshots, not as findings.
- **Selection by our own filters.** "Shown" adverts already passed our title and relevance filters, so these results describe SkillMatch's shortlist, not every advert collected.""",
    ),
    (
        "md",
        """## AI-assisted interpretation: what we checked, kept and rejected

*For the team to complete.* Record here:

- **What the AI assistant was asked to do** (for example: suggest a test for H1, draft the interpretation paragraphs, propose the limitations).
- **What we checked**, against the data and the statistics: did it pick the right test for the expected counts, are the counts it quotes the ones printed above, does the interpretation overclaim from a small *n*?
- **What we kept**, and why.
- **What we rejected or changed**, and why (for example, any wording that turned "no evidence of a difference" into "no difference").
- **Alternatives we considered**: a logistic regression of entry-plausibility on area and source, or pooling several nightly snapshots.""",
    ),
]


def build() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "name": "python3",
        "display_name": "Python 3",
        "language": "python",
    }
    for kind, text in CELLS:
        nb.cells.append(
            nbf.v4.new_markdown_cell(text) if kind == "md" else nbf.v4.new_code_cell(text)
        )
    return nb


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    args = ap.parse_args()
    nb = build()
    path = config.ROOT / "notebooks" / "skillmatch_analysis.ipynb"
    path.parent.mkdir(exist_ok=True)
    if args.execute:
        from nbconvert.preprocessors import ExecutePreprocessor

        ExecutePreprocessor(timeout=300, kernel_name="python3").preprocess(
            nb, {"metadata": {"path": str(config.ROOT)}}
        )
    nbf.write(nb, path)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
