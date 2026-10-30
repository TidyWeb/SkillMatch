"""The tier guard is a separate, read-only step after matching."""

import csv
import json
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from skillmatch.guards import GuardedMatch, apply_tier_guard
from skillmatch.match import match_vacancy
from skillmatch.profile import profile_from_dict
from skillmatch.repository import load
from skillmatch.results import Filters, build_shortlist
from skillmatch.taxonomy import get_taxonomy
from skillmatch.web import create_app


def requirement(text, n=3, strength="essential", confidence="inferred"):
    return {
        "req_id": str(n),
        "n": n,
        "strength": strength,
        "confidence": confidence,
        "evidence_sentence": text,
        "tags": [],
    }


def matched(text="SQL skills", strength="essential", confidence="inferred", skills=None):
    profile = profile_from_dict({"skills": skills or []})
    reqs = [
        requirement("Python", 1, confidence="stated"),
        requirement("Statistics", 2, confidence="stated"),
        requirement(text, strength=strength, confidence=confidence),
    ]
    result = match_vacancy(profile, {"vacancy_id": "test", "title": "Analyst"}, reqs)
    return result, profile


@pytest.mark.parametrize("confidence", ["stated", "inferred"])
def test_guard_caps_strong_regardless_of_requirement_confidence_without_mutation(confidence):
    # Inferred requirements make the matcher Strong. Force only the confidence field afterwards
    # so the guard is tested independently of the unchanged matcher's tier calculation.
    original, profile = matched()
    original.coverage[-1].confidence = confidence
    before = asdict(original)
    guarded = apply_tier_guard(original, profile)
    assert original.tier == "strong"
    assert asdict(original) == before
    assert isinstance(guarded, GuardedMatch)
    assert guarded.tier == "good" and guarded.tier_label == "Good match"
    assert "SQL" in guarded.guard_reason
    assert guarded.guard_findings[0].requirement_text == "SQL skills"
    assert apply_tier_guard(guarded, profile) is guarded


@pytest.mark.parametrize(
    "wording",
    [
        "SQL would be advantageous",
        "SQL is a plus",
        "Ideally SQL",
        "SQL would be beneficial",
        "SQL preferred",
        "SQL is desirable",
    ],
)
def test_desirable_wording_does_not_trigger(wording):
    result, profile = matched(wording)
    assert result.tier == "strong"
    guarded = apply_tier_guard(result, profile)
    assert guarded.tier == "strong" and guarded.guard_reason is None
    assert not guarded.guard_findings


def test_desirable_class_alone_does_not_trigger():
    result, profile = matched("SQL skills", strength="desirable")
    assert apply_tier_guard(result, profile).tier == "strong"


def test_optional_tool_in_distinct_clause_does_not_mask_required_missing_tool():
    result, profile = matched("SQL required; Azure would be beneficial")
    guard = apply_tier_guard(result, profile)
    assert guard.tier == "good" and "SQL" in guard.guard_reason
    assert "Azure" not in guard.guard_reason


def test_strong_with_no_missing_technical_skills_stays_strong():
    result, profile = matched(skills=["sql"])
    assert apply_tier_guard(result, profile).tier == "strong"


@pytest.mark.parametrize("tier", ["good", "stretch", "not_yet"])
def test_guard_never_raises_or_further_lowers_another_tier(tier):
    result, profile = matched()
    result = replace(result, tier=tier)
    guarded = apply_tier_guard(result, profile)
    assert guarded.tier == tier and guarded.guard_reason is None


def test_fabric_and_azure_are_named_and_repeated_requirements_deduplicate_reason():
    result, profile = matched("Azure or Microsoft Fabric")
    result.coverage.append(replace(result.coverage[-1], req_id="another"))
    guard = apply_tier_guard(result, profile)
    assert guard.guard_reason.count("Azure / Microsoft Fabric") == 1
    assert len(guard.guard_findings) == 2


@pytest.mark.parametrize("pid", ["chef_wolverhampton", "teacher_stoke", "nurse_worcester"])
def test_named_live_job_is_good_in_shared_shortlist_html_and_api(pid, monkeypatch):
    import skillmatch.web.routes as routes
    from scripts.ui_simplification_compare import convert_profile

    root = Path(__file__).parents[1]
    path = root / "reports/ui_simplification_baseline.json"
    if not path.exists():
        pytest.skip("Local comparison evidence is not present")
    baseline = json.loads(path.read_text())
    db = root / baseline["database"]
    if not db.exists():
        pytest.skip("Read-only live comparison snapshot is not available")
    raw, missing = convert_profile(baseline["profiles"][pid]["profile"], get_taxonomy())
    assert not missing
    profile = profile_from_dict(raw)
    snapshot = load(db)
    target = next(
        m for m in build_shortlist(profile, snapshot).results if m.vacancy_id == "reed:57451268"
    )
    assert target.tier == "good"
    assert "Azure" in target.guard_reason and "Microsoft Fabric" in target.guard_reason
    only_strong = build_shortlist(profile, snapshot, Filters(tiers={"strong"}))
    assert "reed:57451268" not in {m.vacancy_id for m in only_strong.results}
    seen = {}
    original_render = routes.render_template

    def capture(template, **context):
        if template == "partials/results_list.html":
            seen["cards"] = context["cards"]
        return original_render(template, **context)

    monkeypatch.setattr(routes, "render_template", capture)
    client = create_app({"TESTING": True, "DB_PATH": str(db)}).test_client()
    html = client.post("/results", data={"profile": json.dumps(raw)})
    response = client.get("/api/matches", headers={"X-SkillMatch-Profile": json.dumps(raw)})
    assert html.status_code == response.status_code == 200
    feed = response.get_json()
    assert feed["cards"] == seen["cards"]
    card = next(c for c in feed["cards"] if c["id"] == "reed:57451268")
    assert card["match_tier"] == "good" and card["guard_reason"] == target.guard_reason
    assert target.guard_reason in html.get_data(as_text=True)
    assert feed["counts"]["strong"] == len(only_strong.results)


def test_comparison_logs_each_trigger_and_keeps_earlier_logs(tmp_path, monkeypatch):
    from scripts.ui_simplification_compare import stage6_changes

    monkeypatch.chdir(tmp_path)
    (tmp_path / "reports").mkdir()
    result, profile = matched("Azure or Microsoft Fabric")
    guard = apply_tier_guard(result, profile)
    row = {
        "id": "test",
        "title": "Analyst",
        "tier": "good",
        "guard_reason": guard.guard_reason,
        "guard_findings": [asdict(f) for f in guard.guard_findings],
    }
    old = {"profiles": {"fictional": {"ranking": [dict(row, tier="strong")]}}}
    current = {"profiles": {"fictional": {"ranking": [row]}}}
    _, summary, name = stage6_changes(old, current)
    rows = list(csv.DictReader((tmp_path / "reports" / name).open()))
    assert summary["fictional"]["downgrades"] == 1
    assert rows[0]["vacancy_id"] == "test"
    assert rows[0]["missing_skills"] == "Azure / Microsoft Fabric"
    assert rows[0]["requirement_text"] == "Azure or Microsoft Fabric"
    _, _, second_name = stage6_changes(old, current)
    assert name != second_name and (tmp_path / "reports" / name).exists()
