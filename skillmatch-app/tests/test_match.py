import pytest

from skillmatch.match import GAP, MET, PARTLY, evaluate_requirement, match_vacancy
from skillmatch.phrasing import Phraser
from skillmatch.profile import MAX_AREAS, QUALIFICATIONS, Profile, profile_from_dict
from skillmatch.taxonomy import get_taxonomy


def req(sentence, tag_type, tag_id):
    return {
        "req_id": "r1",
        "n": 1,
        "strength": "essential",
        "confidence": "stated",
        "evidence_sentence": sentence,
        "tags": [(tag_type, tag_id)],
    }


def test_course_skills_are_default_and_user_skills_are_met():
    tax = get_taxonomy()
    p = profile_from_dict({"skills": ["sql", "not-a-skill"]}, tax)
    assert "python" in p.skills and "sql" in p.skills and "not-a-skill" not in p.skills
    c = evaluate_requirement(req("Experience with SQL", "skill", "sql"), p, tax, Phraser(tax))
    assert c.status == MET


def test_missing_requested_skill_is_gap_even_if_related_skill_selected():
    tax = get_taxonomy()
    p = profile_from_dict({"skills": ["python"]}, tax)
    c = evaluate_requirement(req("SQL", "skill", "sql"), p, tax, Phraser(tax))
    assert c.status == GAP


@pytest.mark.parametrize(
    "sentence, expected",
    [
        ("Commercial experience with SQL is required", PARTLY),
        ("2+ years of industry experience in SQL", PARTLY),
        ("2+ years in industry using SQL", PARTLY),
        ("Commercial experience with structured query language", PARTLY),
        ("Commercial experience with SQL Server (T-SQL)", PARTLY),
        ("Experience with SQL", MET),
        ("Knowledge of SQL", MET),
        ("Proven SQL skills", MET),
        ("Practical Python experience; commercial SQL experience", MET),
        ("Commercial SQL experience and knowledge of Python", MET),
        ("Professional communication and knowledge of SQL", MET),
        ("No commercial experience required with SQL", MET),
    ],
)
def test_only_explicit_skill_specific_professional_experience_is_partly(sentence, expected):
    tax = get_taxonomy()
    p = profile_from_dict({"skills": ["sql", "python"]}, tax)
    skill = "python" if "Python" in sentence else "sql"
    coverage = evaluate_requirement(req(sentence, "skill", skill), p, tax, Phraser(tax))
    assert next(tag for tag in coverage.tags if tag.tag_id == skill).status == expected


def test_commercial_experience_reason_names_skill():
    tax = get_taxonomy()
    p = profile_from_dict({"skills": ["sql"]}, tax)
    result = evaluate_requirement(
        req("Commercial experience with SQL", "skill", "sql"), p, tax, Phraser(tax)
    )
    assert "commercial experience" in result.tags[0].answer


def test_areas_defaults_explicit_empty_and_validation():
    tax = get_taxonomy()
    aid = next(iter(tax.archetypes))
    comps = list(tax.archetypes[aid].competencies)
    p = profile_from_dict(
        {"areas": [{"id": aid}, {"id": aid, "skills": []}, {"id": "unknown"}]}, tax
    )
    assert set(p.areas[0].skills) == set(comps)
    p = profile_from_dict({"areas": [{"id": aid, "skills": []}]}, tax)
    assert p.areas[0].skills == []


def test_area_limit_and_unique_ids():
    tax = get_taxonomy()
    ids = list(tax.archetypes)[:6]
    p = profile_from_dict({"areas": [{"id": x} for x in ids]}, tax)
    assert MAX_AREAS == 5 and len(p.areas) == 5 and len({a.id for a in p.areas}) == 5


def test_ticked_area_competency_is_met_and_unticked_is_gap():
    tax = get_taxonomy()
    area = next(a for a in tax.archetypes.values() if a.competencies)
    comp = area.competencies[0]
    p = profile_from_dict({"areas": [{"id": area.id, "skills": [comp]}]}, tax)
    assert (
        evaluate_requirement(req("Experience", "competency", comp), p, tax, Phraser(tax)).status
        == MET
    )
    empty = profile_from_dict({"areas": [{"id": area.id, "skills": []}]}, tax)
    assert (
        evaluate_requirement(req("Experience", "competency", comp), empty, tax, Phraser(tax)).status
        == GAP
    )


def test_invalid_untrusted_shapes_and_nonfinite_values_are_ignored():
    p = profile_from_dict(
        {
            "travel": [],
            "areas": [{"id": []}],
            "max_miles": float("inf"),
            "max_office_days": float("nan"),
            "highest_qualification": 7.9,
        }
    )
    assert p.travel == [] and p.areas == [] and p.max_miles is None
    assert p.max_office_days == 5 and p.highest_qualification == 0


def test_qualification_levels_and_invalid_input():
    assert set(QUALIFICATIONS) == {0, 2, 3, 5, 6, 7, 8}
    assert "python" in Profile().skills
    assert [
        profile_from_dict({"highest_qualification": v}).highest_qualification
        for v in [6, 7, 8, 4, "bad"]
    ] == [6, 7, 8, 0, 0]
    assert Profile(highest_qualification=6).has_degree
    assert not Profile(highest_qualification=5).has_degree


@pytest.mark.parametrize(
    "sentence, level",
    [
        ("GCSE Level 2 qualification", 2),
        ("A level qualification", 3),
        ("HNC Level 5 qualification", 5),
        ("Foundation degree", 5),
        ("Level 6", 6),
        ("Level 7", 7),
        ("Level 8", 8),
        ("Degree or equivalent", 6),
        ("Master's degree", 7),
        ("PhD or doctorate", 8),
    ],
)
def test_qualification_requirement_compares_level_without_subject_match(sentence, level):
    tax = get_taxonomy()
    p = profile_from_dict({"highest_qualification": level})
    coverage = evaluate_requirement(
        {**req(sentence, "competency", "attention_to_detail"), "tags": []}, p, tax, Phraser(tax)
    )
    assert coverage.status == MET
    lower = profile_from_dict(
        {"highest_qualification": max((q for q in QUALIFICATIONS if q < level), default=0)}
    )
    missing = evaluate_requirement(
        {**req(sentence, "competency", "attention_to_detail"), "tags": []}, lower, tax, Phraser(tax)
    )
    assert missing.status == GAP


def test_six_persona_tier_matrix():
    from match_cases import ADVERTS, EXPECTED, PERSONAS

    from skillmatch.parse import parse_advert
    from skillmatch.profile import personas

    profiles = {key: profile_from_dict(value) for key, value in personas().items()}
    assert set(PERSONAS) <= set(profiles)
    for advert_id, (title, html) in ADVERTS.items():
        parsed = parse_advert(html, title)
        vacancy = {
            "vacancy_id": title,
            "title": title,
            "data_years": parsed.data_years,
            "entry_signals": parsed.entry_signals,
            "degree": parsed.degree,
        }
        requirements = [
            {
                "req_id": f"r{item.n}",
                "n": item.n,
                "strength": item.strength,
                "confidence": item.confidence,
                "evidence_sentence": item.text,
                "tags": item.tags,
            }
            for item in parsed.requirements
        ]
        actual = [match_vacancy(profiles[key], vacancy, requirements).tier for key in PERSONAS]
        assert actual == EXPECTED[advert_id]


def test_unclassified_requirements_do_not_count_and_inferred_met_can_support_strong():
    tax = get_taxonomy()
    area = next(
        area for area in tax.archetypes.values() if "attention_to_detail" in area.competencies
    )
    profile = profile_from_dict(
        {
            "skills": ["python"],
            "areas": [{"id": area.id, "skills": ["attention_to_detail"]}],
        },
        tax,
    )
    vacancy = {"vacancy_id": "x", "entry_signals": []}
    requirements = [
        {
            "req_id": "u",
            "n": 1,
            "strength": "essential",
            "confidence": "stated",
            "evidence_sentence": "A full UK driving licence.",
            "tags": [],
        },
        {
            "req_id": "i",
            "n": 2,
            "strength": "essential",
            "confidence": "inferred",
            "evidence_sentence": "Python.",
            "tags": [("skill", "python")],
        },
        {
            "req_id": "s",
            "n": 3,
            "strength": "essential",
            "confidence": "stated",
            "evidence_sentence": "Attention to detail.",
            "tags": [("competency", "attention_to_detail")],
        },
    ]
    result = match_vacancy(profile, vacancy, requirements, tax=tax)
    assert result.tier == "strong"
    assert result.coverage[0].status == "unclassified"


def test_one_clear_essential_cannot_be_strong():
    tax = get_taxonomy()
    result = match_vacancy(
        profile_from_dict({"skills": ["python"]}, tax),
        {"vacancy_id": "x", "entry_signals": []},
        [
            {
                "req_id": "1",
                "n": 1,
                "strength": "essential",
                "confidence": "stated",
                "evidence_sentence": "Python.",
                "tags": [("skill", "python")],
            }
        ],
        tax=tax,
    )
    assert result.tier == "good"


def test_data_role_years_sentence_is_removed_from_coverage():
    tax = get_taxonomy()
    result = match_vacancy(
        profile_from_dict({"skills": ["python"]}, tax),
        {"vacancy_id": "x", "entry_signals": [], "data_years": 25},
        [
            {
                "req_id": "1",
                "n": 1,
                "strength": "essential",
                "confidence": "stated",
                "evidence_sentence": "2+ years experience in a data analyst role.",
                "tags": [],
            },
            {
                "req_id": "2",
                "n": 2,
                "strength": "essential",
                "confidence": "stated",
                "evidence_sentence": "Python.",
                "tags": [("skill", "python")],
            },
        ],
        tax=tax,
    )
    assert [coverage.sentence for coverage in result.coverage] == ["Python."]


@pytest.mark.parametrize("sentence", ["No degree is required", "Degree not required"])
def test_nonrequired_degree_does_not_create_a_requirement(sentence):
    from skillmatch.match import qualification_level

    assert qualification_level(sentence) is None


@pytest.mark.parametrize(
    "value, expected",
    [
        (["car", "public_transport", "bike_walk"], ["car", "public_transport", "bike_walk"]),
        ("car", ["car"]),
        ([], []),
        (None, []),
        ("plane", []),
        ({"car": True}, []),
        (["car", "car", "plane", [], None, 1, "motorbike"], ["car", "motorbike"]),
    ],
)
def test_travel_accepts_choices_and_legacy_value_and_ignores_invalid(value, expected):
    assert profile_from_dict({"travel": value}).travel == expected


def test_profile_travel_defaults_are_independent():
    first, second = Profile(), Profile()
    first.travel.append("car")
    assert second.travel == []
