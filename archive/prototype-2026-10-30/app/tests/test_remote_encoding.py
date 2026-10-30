import sqlite3

from skillmatch.etl.store import write_database
from skillmatch.repository import _read
from skillmatch.sources.http import PoliteClient
from skillmatch.sources.remote_boards import RemoteOKAdapter
from skillmatch.text import repair_mojibake


class Canned:
    def __init__(self, body):
        self.body = body

    def get(self, url, params=None, as_json=True, auth=None):
        return self.body


def test_remoteok_repairs_old_cache_text_and_preserves_unicode():
    body = [
        {
            "id": 1137572,
            "position": "Senior Software Engineer",
            "company": "Wagmo",
            "location": "Remote",
            "description": (
                "Youâ\x80\x99ve shipped an LLM-powered feature. "
                "Tessera Labs AI â\x80\x94 Logistics; café; 東京; you’ve"
            ),
        }
    ]

    vacancy = RemoteOKAdapter(client=Canned(body)).fetch()[0]

    assert vacancy.description_html == (
        "You’ve shipped an LLM-powered feature. Tessera Labs AI — Logistics; café; 東京; you’ve"
    )
    assert body[0]["description"].startswith("Youâ\x80\x99ve")  # input is not mutated


def test_remoteok_text_decoder_handles_only_valid_latin1_utf8_runs():
    assert repair_mojibake("Youâ\x80\x99ve café — you’ve") == "You’ve café — you’ve"
    assert repair_mojibake("café, naïve, ångström") == "café, naïve, ångström"


def test_polite_client_decodes_json_as_utf8_even_with_wrong_charset(tmp_path):
    class Response:
        status_code = 200
        headers = {}
        content = '{"title":"Café — 東京"}'.encode()

        def raise_for_status(self):
            raise AssertionError("successful response should not raise")

    class Session:
        def __init__(self):
            self.headers = {}

        def get(self, *args, **kwargs):
            return Response()

    client = PoliteClient(cache_dir=tmp_path, min_interval=0, session=Session())
    assert client.get("https://example.test/jobs") == {"title": "Café — 東京"}


def test_repository_repairs_remoteok_snapshot_without_writing_database(tmp_path):
    path = tmp_path / "live.db"
    vacancy = {
        "vacancy_id": "remote_ok:7",
        "source": "remote_ok",
        "source_id": "7",
        "source_tier": "A",
        "title": "Senior Analyst â\x80\x94 Café",
        "entry_signals": "[]",
        "title_boost": "[]",
        "extra": "{}",
    }
    requirement = {
        "req_id": "req-7",
        "vacancy_id": "remote_ok:7",
        "n": 1,
        "text_ours": "analysis",
        "strength": "essential",
        "confidence": "stated",
        "section": "essential",
        "evidence_sentence": "Youâ\x80\x99ve used SQL; café",
    }
    write_database(path, {"vacancies": [vacancy], "requirements": [requirement]}, {})
    before = (
        sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        .execute("select title from vacancies where vacancy_id = ?", ("remote_ok:7",))
        .fetchone()[0]
    )

    snapshot = _read(path, path.stat().st_mtime)

    assert snapshot.vacancies["remote_ok:7"]["title"] == "Senior Analyst — Café"
    assert snapshot.requirements["remote_ok:7"][0]["evidence_sentence"] == "You’ve used SQL; café"
    after = (
        sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        .execute("select title from vacancies where vacancy_id = ?", ("remote_ok:7",))
        .fetchone()[0]
    )
    assert after == before
