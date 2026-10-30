from skillmatch.sources.reed import ReedAdapter


class FullPageClient:
    def __init__(self, max_requests=None):
        self.requests_made = 0
        self.max_requests = max_requests
        self.params = []

    def get(self, url, params=None, auth=None):
        self.requests_made += 1
        self.params.append(dict(params))
        skip = params["resultsToSkip"]
        return {
            "results": [{"jobId": skip + i + 1, "jobTitle": "Data Analyst"} for i in range(100)]
        }


def test_birmingham_uses_five_pages_and_other_searches_use_three():
    client = FullPageClient()
    adapter = ReedAdapter(
        client=client,
        api_key="test",
        towns=["Birmingham", "Coventry"],
        terms=["data analyst"],
        pages_per_search=3,
        birmingham_pages=5,
    )
    adapter.search()
    birmingham = [p for p in client.params if p["locationName"] == "Birmingham"]
    coventry = [p for p in client.params if p["locationName"] == "Coventry"]
    assert [p["resultsToSkip"] for p in birmingham] == [0, 100, 200, 300, 400]
    assert [p["resultsToSkip"] for p in coventry] == [0, 100, 200]
    assert adapter.stats["search_calls"] == 8


def test_search_reserve_stops_early_and_keeps_partial_results():
    client = FullPageClient(max_requests=4)
    adapter = ReedAdapter(
        client=client,
        api_key="test",
        towns=["Birmingham", "Coventry"],
        terms=["data analyst"],
        pages_per_search=3,
        birmingham_pages=5,
        detail_reserve=2,
    )
    results = adapter.search()
    assert client.requests_made == 2
    assert len(results) == 200
    assert len(adapter.search_results) == 200
    assert len(adapter.search_observations) == 200
    assert adapter.stats["search_reserve_reached"] == 1
    assert adapter.stats["unvisited_queries"] == 1
    assert adapter.search_events[-1]["status"] == "detail reserve reached"


def test_full_final_page_is_reported_as_truncated():
    client = FullPageClient()
    adapter = ReedAdapter(
        client=client,
        api_key="test",
        towns=["Worcester"],
        terms=["analyst"],
        pages_per_search=3,
    )
    adapter.search()
    assert adapter.stats["truncated_searches"] == [
        {"term": "analyst", "location": "Worcester", "pages": 3, "result_count": 100}
    ]
