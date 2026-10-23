import pytest
from match_cases import ADVERTS, EXPECTED, EXPECTED_ANSWERS, PERSONAS

from skillmatch.match import GAP, MET, PARTLY, UNCLASSIFIED, data_gate, match_vacancy
from skillmatch.parse import parse_advert
from skillmatch.profile import Profile, personas, profile_from_dict


@pytest.fixture(scope="module")
def profiles():
    return {k: profile_from_dict(v) for k, v in personas().items()}


def build(title, html):
    p = parse_advert(html, title)
    vac = {
        "vacancy_id": title,
        "title": title,
        "data_years": p.data_years,
        "entry_signals": p.entry_signals,
        "degree": p.degree,
    }
    reqs = [
        {
            "req_id": f"r{r.n}",
            "n": r.n,
            "strength": r.strength,
            "confidence": r.confidence,
            "evidence_sentence": r.text,
            "tags": r.tags,
        }
        for r in p.requirements
    ]
    return vac, reqs


CASES = [(a, pid, EXPECTED[a][i]) for a in ADVERTS for i, pid in enumerate(PERSONAS)]


@pytest.mark.parametrize("advert, persona, tier", CASES)
def test_persona_tiers(profiles, advert, persona, tier):
    vac, reqs = build(*ADVERTS[advert])
    result = match_vacancy(profiles[persona], vac, reqs)
    assert result.tier == tier, result.reasons


@pytest.mark.parametrize("key, lines", list(EXPECTED_ANSWERS.items()))
def test_answers_this_lines(profiles, key, lines):
    advert, persona = key
    vac, reqs = build(*ADVERTS[advert])
    result = match_vacancy(profiles[persona], vac, reqs)
    answers = [a for c in result.coverage for a in c.answers]
    for line in lines:
        assert line in answers


def test_six_personas_present(profiles):
    assert set(profiles) == set(PERSONAS)
    for p in profiles.values():
        assert p.outcode and p.travel and p.roles and p.skills


def test_no_percentages_in_reasons(profiles):
    # Users' own evidence may contain "15%"; the app's own wording never shows a percentage.
    for advert in ADVERTS.values():
        vac, reqs = build(*advert)
        for p in profiles.values():
            r = match_vacancy(p, vac, reqs)
            assert not any("%" in x for x in r.reasons)


def test_met_partly_gap_rules():
    tax_profile = profile_from_dict(
        {
            "skills": {"power_bi": "project", "tableau": "course", "python": "course"},
            "roles": [
                {
                    "archetype": "retail_store_manager",
                    "seniority": "individual",
                    "competencies": {
                        "kpi_monitoring": "Tracked weekly sales KPIs",
                        "customer_insight": "",
                    },
                }
            ],
        }
    )
    vac, reqs = build(
        "Analyst",
        """<p><strong>Essential</strong></p><ul>
        <li>Power BI.</li><li>Tableau.</li><li>Looker Studio.</li><li>Qlik.</li><li>KPI monitoring.</li>
        <li>Customer insight.</li><li>Negotiation skills.</li><li>A full UK driving licence.</li></ul>""",
    )
    r = match_vacancy(tax_profile, vac, reqs)
    status = {c.sentence: c.status for c in r.coverage}
    assert status["Power BI."] == MET  # used in a project
    assert status["Tableau."] == PARTLY  # learned on the course
    assert status["Looker Studio."] == PARTLY  # related skill in the same family
    assert status["KPI monitoring."] == MET  # competency with evidence
    assert status["Customer insight."] == PARTLY  # ticked without evidence
    assert status["Negotiation skills."] == GAP
    assert status["A full UK driving licence."] == UNCLASSIFIED


def test_unclassified_and_inferred_do_not_sink():
    p = Profile()
    vac = {"vacancy_id": "x", "data_years": None, "entry_signals": []}
    reqs = [
        {
            "req_id": "1",
            "n": 1,
            "strength": "essential",
            "confidence": "stated",
            "evidence_sentence": "A UK driving licence.",
            "tags": [],
        },
        {
            "req_id": "2",
            "n": 2,
            "strength": "essential",
            "confidence": "inferred",
            "evidence_sentence": "Experience with SQL.",
            "tags": [("skill", "sql")],
        },
        {
            "req_id": "3",
            "n": 3,
            "strength": "essential",
            "confidence": "stated",
            "evidence_sentence": "Accuracy.",
            "tags": [("competency", "attention_to_detail")],
        },
        {
            "req_id": "4",
            "n": 4,
            "strength": "essential",
            "confidence": "stated",
            "evidence_sentence": "Excel.",
            "tags": [("skill", "excel")],
        },
    ]
    nurse = {
        "skills": {"excel": "project"},
        "roles": [
            {"archetype": "nurse", "competencies": {"attention_to_detail": "Audited charts"}}
        ],
    }
    r = match_vacancy(profile_from_dict(nurse), vac, reqs)
    assert r.tier == "strong"  # the unclassified licence and the inferred SQL gap don't sink it
    r2 = match_vacancy(p, vac, reqs)
    assert r2.tier == "stretch"  # two stated gaps; the inferred SQL gap doesn't make it three


def test_strong_needs_two_clear_essentials():
    vac = {"vacancy_id": "x", "data_years": None, "entry_signals": []}
    reqs = [
        {
            "req_id": "1",
            "n": 1,
            "strength": "essential",
            "confidence": "stated",
            "evidence_sentence": "Excel.",
            "tags": [("skill", "excel")],
        }
    ]
    r = match_vacancy(profile_from_dict({"skills": {"excel": "confident"}}), vac, reqs)
    assert r.tier == "good" and any("only find 1" in x for x in r.reasons)


def test_leadership_rule_needs_manager_level():
    req = [
        {
            "req_id": "1",
            "n": 1,
            "strength": "essential",
            "confidence": "stated",
            "evidence_sentence": "Confidence presenting to senior stakeholders.",
            "tags": [("competency", "reporting_to_leadership")],
        }
    ]
    vac = {"vacancy_id": "x", "data_years": None, "entry_signals": []}
    manager = profile_from_dict(
        {
            "roles": [
                {
                    "archetype": "kitchen_manager",
                    "seniority": "manager",
                    "competencies": {"stock_inventory_supply": "Ran stock"},
                }
            ]
        }
    )
    assistant = profile_from_dict(
        {
            "roles": [
                {
                    "archetype": "retail_assistant",
                    "seniority": "individual",
                    "competencies": {"customer_service": "Served customers"},
                }
            ]
        }
    )
    assert match_vacancy(manager, vac, req).coverage[0].status == MET
    assert match_vacancy(assistant, vac, req).coverage[0].status == GAP


@pytest.mark.parametrize(
    "demand, user, signals, gate",
    [
        (None, 0, [], "ok"),
        (1, 0, ["junior"], "waived"),
        (1, 0, [], "small"),
        (2, 0, ["junior"], "stretch"),
        (3, 0, ["junior"], "not_yet"),
        (3, 2, [], "small"),
        (2, 3, [], "ok"),
    ],
)
def test_data_experience_gate(demand, user, signals, gate):
    p = Profile(data_years=user)
    assert data_gate({"data_years": demand, "entry_signals": signals}, p)[0] == gate


def test_degree_warning(profiles):
    vac, reqs = build(
        "Analyst",
        "<p><strong>Essential</strong></p><ul><li>A degree in mathematics is essential.</li><li>Excel.</li></ul>",
    )
    chef = match_vacancy(profiles["chef_wolverhampton"], {**vac}, reqs)
    assert any("degree" in r for r in chef.reasons)
    phd = match_vacancy(profiles["phd_coventry"], {**vac}, reqs)
    assert not any("degree" in r for r in phd.reasons)
