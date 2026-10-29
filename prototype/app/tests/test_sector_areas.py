from pathlib import Path

import pytest
import yaml

APP_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = APP_ROOT.parent
SOURCE_TAXONOMY = APP_ROOT / "data/taxonomy/archetype_groups_v2.yaml"
RESEARCH_TAXONOMY = PROJECT_ROOT / "Research/Occupations/archetype_groups_v2.yaml"
COMPETENCIES = APP_ROOT / "data/taxonomy/competencies.yaml"


EXPECTED_SECTOR_AREAS = {
    "sector_health_care": {
        "clinical_healthcare",
        "care_patient_support",
        "health_administration",
    },
    "sector_education": {"teaching_childcare_coaching"},
    "sector_finance_insurance": {
        "accounting_financial_records",
    },
    "sector_public_policing": {"public_administration", "public_safety_security"},
    "sector_retail_hospitality": {
        "kitchen_food_production",
        "customer_service",
        "sales_account_management",
    },
    "sector_manufacturing_logistics": {
        "skilled_trades_repair",
        "manufacturing_production",
        "warehouse_waste_materials",
        "goods_driving_delivery",
    },
    "sector_charity": {"charity_community_programmes"},
    "sector_energy_property": {
        "skilled_trades_repair",
    },
}


def _sector_areas(groups):
    result = {sector_id: set() for sector_id in EXPECTED_SECTOR_AREAS}
    for group in groups:
        for competency in group["competencies"]:
            if competency in result:
                result[competency].add(group["id"])
    return result


def test_every_sector_competency_maps_to_its_intended_existing_areas():
    groups = yaml.safe_load(SOURCE_TAXONOMY.read_text())["groups"]
    sector_ids = {
        competency["id"]
        for competency in yaml.safe_load(COMPETENCIES.read_text())["competencies"]
        if competency["category"] == "sector"
    }

    assert sector_ids == set(EXPECTED_SECTOR_AREAS)
    assert _sector_areas(groups) == EXPECTED_SECTOR_AREAS


def test_sector_mapping_preserves_the_31_existing_areas():
    groups = yaml.safe_load(SOURCE_TAXONOMY.read_text())["groups"]

    assert len(groups) == 31
    assert len({group["id"] for group in groups}) == 31


def test_research_taxonomy_is_an_exact_mirror_of_the_app_taxonomy():
    if not RESEARCH_TAXONOMY.exists():
        pytest.skip("The Research mirror belongs to the working project, outside the app repo")
    assert SOURCE_TAXONOMY.read_bytes() == RESEARCH_TAXONOMY.read_bytes()
