from skillmatch.sources.ats import ATSAdapter
from skillmatch.sources.http import RequestCapReached
from skillmatch.sources.reed import ReedAdapter
from skillmatch.sources.remote_boards import RemoteOKAdapter, WeWorkRemotelyAdapter


class Canned:
    def __init__(self, responses):
        self.responses = responses

    def get(self, url, params=None, as_json=True, auth=None):
        for key, response in self.responses.items():
            if key in url:
                if isinstance(response, Exception):
                    raise response
                return response
        raise AssertionError(url)


def test_ats_retains_overseas_items_and_records_safe_board_errors():
    adapter = ATSAdapter(
        client=Canned(
            {
                "greenhouse": {
                    "jobs": [
                        {
                            "id": 1,
                            "title": "Data Analyst",
                            "location": {"name": "New York, United States"},
                            "offices": [],
                        }
                    ]
                },
                "lever": RuntimeError("secret-containing error"),
            }
        ),
        boards=[
            {"platform": "greenhouse", "slug": "board", "employer": "Employer"},
            {"platform": "lever", "slug": "other", "employer": "Employer"},
        ],
    )
    records = adapter.fetch()
    assert len(records) == 1
    assert "New York" in records[0].location_text
    assert adapter.source_log == [
        {"source": "lever", "board": "other", "error_type": "RuntimeError"}
    ]
    assert "secret-containing" not in repr(adapter.source_log)


def test_remote_boards_retain_valid_items_without_data_title_prefilter():
    rss = """<rss><channel>
      <item><title>Acme: Sales Lead</title><link>https://weworkremotely.com/remote-jobs/1</link>
        <region>United States</region><country>USA</country><description>Sales work</description></item>
    </channel></rss>"""
    wwr = WeWorkRemotelyAdapter(client=Canned({"weworkremotely": rss})).fetch()
    assert len(wwr) == 1
    assert wwr[0].title == "Sales Lead"
    assert wwr[0].extra["uk_eligibility"] == "no"

    rok = RemoteOKAdapter(
        client=Canned({"remoteok": [{"id": 9, "position": "Sales Lead", "location": "USA"}]})
    ).fetch()
    assert len(rok) == 1
    assert rok[0].extra["uk_eligibility"] == "no"
    europe = RemoteOKAdapter(
        client=Canned({"remoteok": [{"id": 10, "position": "Analyst", "location": "Europe"}]})
    ).fetch()
    assert europe[0].extra["uk_eligibility"] == "unclear"


def test_reed_search_results_and_occurrences_survive_request_cap():
    class CappedSearch:
        def __init__(self):
            self.calls = 0

        def get(self, url, params=None, auth=None):
            self.calls += 1
            if self.calls == 1:
                return {
                    "results": [
                        {
                            "jobId": 42,
                            "jobTitle": "Data Assistant",
                            "jobDescription": "A short excerpt",
                        }
                    ]
                }
            raise RequestCapReached("cap")

    adapter = ReedAdapter(
        client=CappedSearch(),
        api_key="test",
        towns=["Birmingham", "Coventry"],
        terms=["data assistant"],
        pages_per_search=2,
    )
    result = adapter.search()
    assert list(result) == [42]
    assert adapter.search_results[42]["_matched_terms"] == ["data assistant"]
    assert adapter.search_observations == [
        {"job_id": 42, "matched_term": "data assistant", "location": "Birmingham", "page": 1}
    ]
    assert adapter.stats["stopped_at_cap"] == 1


def test_reed_coverage_marks_search_excerpt_and_missing_text_unavailable():
    excerpt = ReedAdapter.from_search_row({"jobId": 1, "jobDescription": "short"})
    blank = ReedAdapter.from_search_row({"jobId": 2})
    assert excerpt.description_coverage == "search excerpt only"
    assert blank.description_coverage == "unavailable"
