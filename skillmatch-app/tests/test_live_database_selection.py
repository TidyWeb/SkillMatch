from skillmatch import config, repository
from skillmatch.web import create_app


def test_default_web_app_defers_to_latest_live_database(monkeypatch, tmp_path):
    latest = tmp_path / "skillmatch_live_20261027.db"
    historical = tmp_path / "skillmatch_reprocessed_20261021.db"
    latest.write_bytes(b"test sentinel")
    historical.write_bytes(b"historical sentinel")
    selected = []

    monkeypatch.setattr(config, "PROCESSED_DIR", tmp_path)
    monkeypatch.setattr(repository, "_read", lambda path, mtime: selected.append(path) or None)
    app = create_app({"TESTING": True})
    with app.app_context():
        repository.load(app.config["DB_PATH"])
    assert selected == [latest]


def test_explicit_database_configuration_remains_available(tmp_path):
    explicit = tmp_path / "chosen.db"
    app = create_app({"TESTING": True, "DB_PATH": str(explicit)})
    assert app.config["DB_PATH"] == str(explicit)
