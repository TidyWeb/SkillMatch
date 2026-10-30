import pytest

from skillmatch.geo import (
    Geocoder,
    haversine_miles,
    is_remote_location,
    normalise_postcode,
    outward_code,
    region_for_district,
)


@pytest.mark.parametrize(
    "a, b, miles",
    [
        ((51.5074, -0.1278), (48.8566, 2.3522), 213.5),  # London to Paris
        ((52.4797, -1.9027), (51.5074, -0.1278), 101.5),  # Birmingham to London
        ((52.4797, -1.9027), (52.4797, -1.9027), 0.0),
    ],
)
def test_haversine_known_distances(a, b, miles):
    assert haversine_miles(*a, *b) == pytest.approx(miles, abs=1.5)


@pytest.mark.parametrize(
    "raw, full, outward",
    [
        ("b913qs", "B91 3QS", "B91"),
        ("CV115AA", "CV11 5AA", "CV11"),
        ("WV1 1SH", "WV1 1SH", "WV1"),
        ("B91", None, "B91"),
        (" st1 ", None, "ST1"),
        ("not a postcode", None, None),
        ("", None, None),
    ],
)
def test_postcode_validation(raw, full, outward):
    assert normalise_postcode(raw) == full
    assert outward_code(raw) == outward


class FakeClient:
    """Stands in for postcodes.io. Records every URL so tests can check what was sent."""

    def __init__(self):
        self.urls = []

    def get(self, url, params=None):
        self.urls.append((url, params))
        if "/outcodes/" in url:
            return {"result": {"latitude": 52.41, "longitude": -1.78}}
        if "/postcodes/" in url:
            return {
                "result": {
                    "latitude": 52.48,
                    "longitude": -1.89,
                    "region": "West Midlands",
                    "admin_district": "Birmingham",
                }
            }
        if url.endswith("/places"):
            return {"result": []}
        raise AssertionError(url)


def test_user_home_sends_outward_code_only(monkeypatch):
    # Force the network path by hiding the offline table.
    monkeypatch.setattr("skillmatch.geo.outcode_table", lambda: {})
    client = FakeClient()
    place = Geocoder(client=client).locate_outcode("B91 3QS")
    assert place is not None
    sent = " ".join(f"{u} {p}" for u, p in client.urls)
    assert "/outcodes/B91" in sent
    assert "3QS" not in sent


def test_user_home_offline_table():
    place = Geocoder(offline=True).locate_outcode("cv1 2aa")
    assert place is not None and place.method == "outcode_table"


def test_job_postcode_uses_postcodes_api():
    client = FakeClient()
    place = Geocoder(client=client).locate_job("Birmingham", "B46AR")
    assert place.region == "West Midlands" and place.method == "postcode"


def test_job_town_offline_and_name_clash():
    g = Geocoder(offline=True)
    assert g.locate_job("Dudley").region == "West Midlands"
    assert g.locate_job("Solihull, England, United Kingdom").county == "Solihull"
    assert g.locate_job("Leicester").region == "East Midlands"
    assert g.locate_job("Warwickshire").approximate
    assert g.locate_job("Location TBC") is None
    assert "Location TBC" in g.failures


def test_remote_locations():
    assert is_remote_location("UK-remote")
    assert is_remote_location("Remote (UK)")
    assert not is_remote_location("Birmingham")


def test_region_for_district():
    assert region_for_district("Solihull") == "West Midlands"
    assert region_for_district("Powys") is None
