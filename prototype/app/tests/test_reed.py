from datetime import date

from skillmatch.sources.reed import ReedAdapter, _postcode

DETAIL = {
    "jobId": 123,
    "employerName": "Acme &amp; Co",
    "jobTitle": "Data &amp; Insight Analyst",
    "locationName": "Birmingham",
    "minimumSalary": 450.0,
    "maximumSalary": 550.0,
    "salaryType": "per day",
    "salary": "£450.00 - £550.00 per day",
    "currency": "GBP",
    "datePosted": "01/10/2026",
    "expirationDate": "12/11/2026",
    "jobUrl": "https://www.reed.co.uk/jobs/x/123",
    "contractType": "Contract",
    "fullTime": True,
    "partTime": False,
    "jobDescription": "<p>Hello</p>",
}


def test_to_vacancy_normalises_fields():
    v = ReedAdapter.to_vacancy(DETAIL, {"locationName": "B46AR", "_matched_terms": ["bi analyst"]})
    assert v.vacancy_id == "reed:123"
    assert v.title == "Data & Insight Analyst"
    assert v.employer == "Acme & Co"
    assert v.salary_period == "day"
    assert (v.salary_min, v.salary_max) == (450.0, 550.0)
    assert v.posted_date == "2026-10-01"
    assert v.expiration_date == "2026-11-12"
    assert v.postcode == "B4 6AR"
    assert v.contract_type == "contract"
    assert v.job_type == "full_time"


def test_hidden_salary_stays_empty():
    d = dict(DETAIL, minimumSalary=None, maximumSalary=None, salaryType="per annum", salary="")
    v = ReedAdapter.to_vacancy(d)
    assert v.salary_min is None and v.salary_period is None and v.salary_text is None


def test_postcode_parsing():
    assert _postcode("CV115AA") == "CV11 5AA"
    assert _postcode("WR1 2EY") == "WR1 2EY"
    assert _postcode("Birmingham") is None


class FakeClient:
    def __init__(self, search, details):
        self.search, self.details, self.calls = search, details, []

    def get(self, url, params=None, auth=None):
        self.calls.append(url)
        if url.endswith("/search"):
            return {"results": self.search if params["resultsToSkip"] == 0 else []}
        return self.details[int(url.rsplit("/", 1)[1])]


def test_fetch_dedupes_filters_and_drops_expired():
    rows = [
        {"jobId": 1, "jobTitle": "Data Analyst", "expirationDate": "01/12/2026"},
        {"jobId": 2, "jobTitle": "Senior Data Analyst", "expirationDate": "01/12/2026"},
        {"jobId": 3, "jobTitle": "Old Analyst", "expirationDate": "01/01/2026"},
    ]
    details = {1: dict(DETAIL, jobId=1, jobTitle="Data Analyst")}
    client = FakeClient(rows, details)
    reed = ReedAdapter(
        client=client,
        api_key="k",
        towns=["Birmingham", "Coventry"],
        terms=["data analyst"],
        keep=lambda r: "Senior" not in r["jobTitle"],
        today=date(2026, 10, 21),
    )
    out = reed.fetch()
    assert [v.source_id for v in out] == ["1"]
    assert reed.stats["search_unique"] == 3
    assert reed.stats["expired_in_search"] == 1
    assert sum(1 for c in client.calls if "/jobs/" in c) == 1


def test_disabled_without_key():
    assert ReedAdapter(api_key="").fetch() == []
