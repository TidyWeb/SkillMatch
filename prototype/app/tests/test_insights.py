from skillmatch.etl.pipeline import run
from skillmatch.insights import build_insights, entry_plausible, personal_insights
from skillmatch.profile import personas, profile_from_dict
from skillmatch.repository import load


def test_entry_plausible():
    assert entry_plausible({"data_years": None})
    assert entry_plausible({"data_years": float("nan")})  # as pandas reads a missing value
    assert entry_plausible({"data_years": 1, "entry_signals": ["junior"]})
    assert not entry_plausible({"data_years": 1, "entry_signals": []})
    assert not entry_plausible({"data_years": 2, "entry_signals": ["junior"]})


def test_insight_figures_carry_n(tmp_path):
    run("fixtures", db_path=tmp_path / "i.db", reports_dir=tmp_path, offline=True)
    snap = load(tmp_path / "i.db")
    d = build_insights(snap)
    assert d["mode"] == "fixtures"
    assert d["n_shown"] > 0 and d["n_entry"] <= d["n_shown"]
    assert d["competencies"] and d["skills"]
    assert 0 < len(d["essential_skill_chart"]) <= 20
    assert d["essential_skill_total"] >= sum(row["n"] for row in d["essential_skill_chart"])
    assert all(row["n"] > 0 for row in d["essential_skill_chart"])
    assert all(
        row["course_share"] == row["share"] if row["course_covered"] else row["course_share"] == 0
        for row in d["essential_skill_chart"]
    )
    assert d["junior"]["n"] >= d["junior"]["two_plus"] >= 1
    assert sum(b["n"] for b in d["salary"]["bands"]) == d["salary"]["n"]
    assert {w["label"] for w in d["senior_words"]} >= {"senior", "manager"}
    mine = personal_insights(profile_from_dict(personas()["teacher_stoke"]), snap)
    assert mine["points"] and mine["home"]
    assert sum(t["n"] for t in mine["tiers"]) == mine["n_results"]
