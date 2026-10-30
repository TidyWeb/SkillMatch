import json
from collections import Counter

from skillmatch import config

TOWNS = [
    "Birmingham",
    "Solihull",
    "Coventry",
    "Wolverhampton",
    "Dudley",
    "Walsall",
    "West Bromwich",
    "Sutton Coldfield",
    "Worcester",
    "Redditch",
    "Bromsgrove",
    "Kidderminster",
    "Droitwich",
    "Telford",
    "Shrewsbury",
    "Stafford",
    "Lichfield",
    "Tamworth",
    "Cannock",
    "Warwick",
    "Leamington Spa",
    "Nuneaton",
    "Rugby",
    "Stratford-upon-Avon",
    "Hereford",
    "Stoke-on-Trent",
    "UK-remote",
]


def load():
    return json.loads(config.FIXTURES_PATH.read_text())


def test_fixture_volume_and_marking():
    recs = load()
    assert len(recs) >= 90
    assert all(r["source"] == "fixture" for r in recs)
    assert len({r["source_id"] for r in recs}) == len(recs)


def test_fixture_town_coverage():
    towns = {r["location_text"] for r in load()}
    assert set(TOWNS) <= towns


def test_fixture_mix():
    recs = load()
    titles = [r["title"].lower() for r in recs]
    assert (
        sum(
            t.startswith(("senior", "head of", "lead", "principal", "director", "snr"))
            for t in titles
        )
        >= 5
    )
    assert sum(r["salary_min"] is None for r in recs) >= 8
    assert any(r["salary_period"] == "day" for r in recs)
    assert any("Trainee" in r["title"] for r in recs)
    keys = Counter((r["title"], r["employer"], r["location_text"]) for r in recs)
    assert sum(1 for n in keys.values() if n > 1) >= 4  # cross-source duplicates
    assert any("days per week" in r["description_html"] for r in recs)
