import json

from skillmatch.sources.ats import ATSAdapter
from skillmatch.sources.cvlibrary import CVLibraryAdapter
from skillmatch.sources.remote_boards import RemoteOKAdapter, WeWorkRemotelyAdapter, uk_eligibility


class Canned:
    def __init__(self, responses):
        self.responses = responses
        self.requests_made = 0

    def get(self, url, params=None, as_json=True, auth=None):
        self.requests_made += 1
        for key, body in self.responses.items():
            if key in url:
                return body
        raise AssertionError(url)


def test_greenhouse_keeps_uk_and_prefers_west_midlands():
    body = {
        "jobs": [
            {
                "id": 1,
                "title": "Data Analyst",
                "absolute_url": "https://boards.greenhouse.io/x/jobs/1",
                "location": {
                    "name": "London, England, United Kingdom; Solihull, England, United Kingdom"
                },
                "offices": [],
                "content": "&lt;p&gt;Hello&lt;/p&gt;",
                "first_published": "2026-10-01T09:00:00Z",
            },
            {
                "id": 2,
                "title": "Analyst",
                "location": {"name": "New York, United States"},
                "offices": [],
            },
        ]
    }
    a = ATSAdapter(
        client=Canned({"greenhouse": body}),
        boards=[{"platform": "greenhouse", "slug": "x", "employer": "X Ltd"}],
    )
    out = a.fetch()
    assert [v.location_text for v in out] == ["Solihull, England, United Kingdom"]
    assert out[0].description_html == "<p>Hello</p>"
    assert out[0].posted_date == "2026-10-01"


def test_lever_and_workable():
    lever = [
        {
            "id": "a",
            "text": "BI Analyst",
            "categories": {"location": "Birmingham", "allLocations": ["Birmingham"]},
            "country": "GB",
            "workplaceType": "hybrid",
            "hostedUrl": "https://jobs.lever.co/k/a",
            "lists": [{"text": "Requirements", "content": "<li>SQL</li>"}],
            "createdAt": 1760000000000,
        },
        {"id": "b", "text": "Analyst", "categories": {"location": "Detroit"}, "country": "US"},
    ]
    workable = {
        "jobs": [
            {
                "title": "Data Officer",
                "shortcode": "S1",
                "country": "United Kingdom",
                "city": "Walsall",
                "telecommuting": False,
                "url": "https://apply.workable.com/j/S1",
                "description": "<p>x</p>",
            }
        ]
    }
    a = ATSAdapter(
        client=Canned({"lever": lever, "workable": workable}),
        boards=[
            {"platform": "lever", "slug": "k", "employer": "K"},
            {"platform": "workable", "slug": "w", "employer": "W"},
        ],
    )
    out = {v.source: v for v in a.fetch()}
    assert (
        out["lever"].location_text == "Birmingham"
        and "<h3>Requirements</h3>" in out["lever"].description_html
    )
    assert out["workable"].location_text == "Walsall"


def test_remote_boards_keep_data_roles_only():
    rss = """<rss><channel>
      <item><title>Acme: Data Analyst</title><link>https://weworkremotely.com/remote-jobs/acme-data-analyst</link>
        <region>Anywhere in the World</region><country></country><description>&lt;p&gt;SQL&lt;/p&gt;</description>
        <pubDate>Tue, 20 Oct 2026 10:00:00 +0000</pubDate></item>
      <item><title>Acme: Sales Lead</title><link>https://weworkremotely.com/remote-jobs/acme-sales</link></item>
    </channel></rss>"""
    wwr = WeWorkRemotelyAdapter(client=Canned({"weworkremotely": rss})).fetch()
    assert [v.title for v in wwr] == ["Data Analyst"]
    assert wwr[0].employer == "Acme" and wwr[0].extra["uk_eligibility"] == "yes"
    rok = [
        {"legal": "notice"},
        {
            "id": 7,
            "position": "Data Analyst",
            "company": "B",
            "location": "Europe",
            "url": "https://remoteok.com/remote-jobs/7",
            "salary_min": 50000,
            "salary_max": 70000,
        },
    ]
    out = RemoteOKAdapter(client=Canned({"remoteok": rok})).fetch()
    assert out[0].url == "https://remoteok.com/remote-jobs/7"
    assert out[0].salary_min is None  # Remote OK salaries may be estimates: never shown
    assert out[0].extra["uk_eligibility"] == "unclear"


def test_uk_eligibility():
    assert uk_eligibility("UK only") == "yes"
    assert uk_eligibility("USA") == "unclear"


def test_cvlibrary_disabled_without_feed():
    a = CVLibraryAdapter(feed_url="")
    assert not a.enabled and a.fetch() == []


def test_cvlibrary_keeps_display_fields_unaltered():
    xml = "<jobs><job><id>9</id><title>Data Analyst</title><salary>£30k</salary><company>Acme</company><location>Coventry</location><url>https://www.cv-library.co.uk/job/9</url></job></jobs>"
    out = CVLibraryAdapter(
        client=Canned({"feed": xml}), feed_url="https://example.org/feed"
    ).fetch()
    assert out[0].extra["cvlibrary_display"] == {
        "title": "Data Analyst",
        "salary": "£30k",
        "company": "Acme",
        "location": "Coventry",
    }
    assert json.dumps(out[0].to_dict())
