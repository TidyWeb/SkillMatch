from pathlib import Path

import pytest

from skillmatch.etl.export import ExportConflictError, UnsafeExportError, export_data


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _source(data_dir: Path) -> None:
    _write(data_dir / "snapshots" / "run-1" / "run.json", '{"run_id":"one"}\n')
    _write(data_dir / "snapshots" / "run-1" / "shown.csv", "id\n1\n")
    _write(data_dir / "snapshots" / "run-1" / "private.db", "not exported")
    _write(data_dir / "history" / "versions" / "v1" / "adverts_history.csv", "id\none\n")
    _write(data_dir / "history" / "adverts_history.csv", "id\ncurrent\n")
    _write(data_dir / "history" / "daily_changes.csv", "run\nfirst\n")
    _write(data_dir / "history" / "notes.md", "local history note")
    _write(data_dir / "raw" / "secret.csv", "never exported")
    _write(data_dir / ".env", "TOKEN=private")
    _write(data_dir / "cache" / "response.json", '{"private":true}')
    _write(data_dir / "processed" / "skillmatch.db", "database")


def test_export_copies_only_snapshots_and_history_allowlisted_files(tmp_path):
    data_dir, target = tmp_path / "data", tmp_path / "portable"
    _source(data_dir)

    result = export_data(data_dir, target)

    assert (target / "run-1" / "run.json").read_text() == '{"run_id":"one"}\n'
    assert (target / "run-1" / "shown.csv").exists()
    assert (data_dir / "history" / "versions" / "v1" / "adverts_history.csv").exists()
    assert not (target / "history" / "versions").exists()
    assert not (target / "history" / "notes.md").exists()
    assert (target / "history" / "adverts_history.csv").read_text() == "id\ncurrent\n"
    top_readme = (target / "README.md").read_text()
    assert top_readme.startswith("# SkillMatch job data")
    assert "Adverts collected" in top_readme and "data_dictionary.md" in top_readme
    assert '{"run_id"' not in top_readme
    assert (target / "data_dictionary.md").is_file()
    assert not (target / "run-1" / "private.db").exists()
    assert not (target / "history" / "raw").exists()
    assert not list(target.rglob(".env"))
    assert not list(target.rglob("*.db"))
    assert result["files_copied"] == 6
    assert result["total_bytes"] > 0
    assert result["report_paths"]


def test_export_is_idempotent_without_exporting_history_versions(tmp_path):
    data_dir, target = tmp_path / "data", tmp_path / "portable"
    _source(data_dir)

    first = export_data(data_dir, target)
    second = export_data(data_dir, target)

    assert first["files_copied"] == 6
    assert second["files_copied"] == 0
    assert second["items_skipped"] == 3
    assert second["total_bytes"] == 0
    assert not (target / "history" / "versions").exists()


def test_conflicting_snapshot_fails_without_overwriting(tmp_path):
    data_dir, target = tmp_path / "data", tmp_path / "portable"
    _source(data_dir)
    export_data(data_dir, target)
    destination = target / "run-1" / "shown.csv"
    destination.write_text("id\nchanged\n", encoding="utf-8")

    with pytest.raises(ExportConflictError, match="run-1"):
        export_data(data_dir, target)
    assert destination.read_text() == "id\nchanged\n"


def test_changed_history_current_is_backed_up_before_refresh(tmp_path):
    data_dir, target = tmp_path / "data", tmp_path / "portable"
    _source(data_dir)
    export_data(data_dir, target)
    _write(data_dir / "history" / "adverts_history.csv", "id\nupdated\n")

    result = export_data(data_dir, target)

    assert (target / "history" / "adverts_history.csv").read_text() == "id\nupdated\n"
    backups = list((data_dir / "history" / "versions").glob("export-current-*"))
    assert len(backups) == 1
    assert (backups[0] / "adverts_history.csv").read_text() == "id\ncurrent\n"
    assert (data_dir / "history" / "versions" / "v1" / "adverts_history.csv").exists()
    assert not (target / "history" / "versions").exists()
    assert result["files_copied"] == 1
    assert result["total_bytes"] == len("id\nupdated\n")


def test_existing_target_history_versions_fails_before_copying(tmp_path):
    data_dir, target = tmp_path / "data", tmp_path / "portable"
    _source(data_dir)
    legacy = target / "history" / "versions" / "legacy" / "adverts_history.csv"
    _write(legacy, "id\nlegacy\n")
    sentinel = target / "keep.txt"
    sentinel.write_text("leave unchanged", encoding="utf-8")

    with pytest.raises(ExportConflictError, match="history/versions already exists"):
        export_data(data_dir, target)

    assert legacy.read_text(encoding="utf-8") == "id\nlegacy\n"
    assert sentinel.read_text(encoding="utf-8") == "leave unchanged"
    assert not (target / "run-1").exists()
    assert not (target / "history" / "adverts_history.csv").exists()
    assert (data_dir / "history" / "versions" / "v1" / "adverts_history.csv").exists()


def test_export_refuses_symlinks_and_targets_inside_source(tmp_path):
    data_dir, target = tmp_path / "data", tmp_path / "portable"
    _source(data_dir)
    link = data_dir / "snapshots" / "run-1" / "linked.csv"
    link.symlink_to(data_dir / "snapshots" / "run-1" / "shown.csv")

    with pytest.raises(UnsafeExportError, match="symlink"):
        export_data(data_dir, target)

    clean_data = tmp_path / "clean-data"
    _source(clean_data)
    with pytest.raises(UnsafeExportError, match="outside"):
        export_data(clean_data, clean_data / "exported")
