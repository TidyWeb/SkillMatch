import json
from pathlib import Path

import pytest

from skillmatch.profile import areas_for_competencies
from skillmatch.taxonomy import get_taxonomy


def test_baseline_ticks_all_fit_five_areas_with_restored_sectors():
    path = Path(__file__).parents[1] / "reports/ui_simplification_baseline.json"
    if not path.exists():
        pytest.skip("Local comparison evidence is not present")
    baseline = json.loads(path.read_text())
    tax = get_taxonomy()
    for fixture in baseline["profiles"].values():
        wanted = {c for role in fixture["profile"]["roles"] for c in role["competencies"]}
        areas, missing = areas_for_competencies(wanted, tax)
        assert not missing
        assert len(areas) <= 5
        assert {c for area in areas for c in area["skills"]} == wanted
