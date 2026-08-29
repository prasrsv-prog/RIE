from __future__ import annotations

import json
from pathlib import Path

import rie.ui.local_operator_settings as settings_module
from rie.ui.local_operator_settings import (
    default_settings_path,
    load_remembered_intake_root,
    save_remembered_intake_root,
)


def test_default_settings_path_prefers_localappdata(tmp_path: Path) -> None:
    local = tmp_path / "LocalAppData"
    actual = default_settings_path(
        environ={
            "LOCALAPPDATA": str(local),
            "USERPROFILE": str(tmp_path / "Profile"),
        }
    )
    assert actual == local / "RCIS" / "settings.json"


def test_missing_settings_returns_no_remembered_intake(tmp_path: Path) -> None:
    assert (
        load_remembered_intake_root(
            settings_path=tmp_path / "missing.json"
        )
        is None
    )


def test_valid_canonical_settings_loads_intake_root(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        '{"intake_root":"C:/Pilot/Intake","schema_version":1}\n',
        encoding="utf-8",
    )
    assert (
        load_remembered_intake_root(settings_path=path)
        == "C:/Pilot/Intake"
    )


def test_unsupported_schema_is_ignored_safely(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        '{"intake_root":"C:/Pilot/Intake","schema_version":2}\n',
        encoding="utf-8",
    )
    assert load_remembered_intake_root(settings_path=path) is None


def test_malformed_json_is_ignored_safely(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text("{not-json", encoding="utf-8")
    assert load_remembered_intake_root(settings_path=path) is None


def test_save_creates_canonical_schema_v1(tmp_path: Path) -> None:
    path = tmp_path / "RCIS" / "settings.json"
    saved = save_remembered_intake_root(
        "C:/Pilot/Intake",
        settings_path=path,
    )
    assert saved == path
    assert path.read_bytes() == (
        b'{"intake_root":"C:/Pilot/Intake","schema_version":1}\n'
    )
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "schema_version": 1,
        "intake_root": "C:/Pilot/Intake",
    }


def test_save_and_read_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    save_remembered_intake_root(
        r"C:\Users\Example\Downloads\RCIS-Intake",
        settings_path=path,
    )
    assert load_remembered_intake_root(settings_path=path) == (
        r"C:\Users\Example\Downloads\RCIS-Intake"
    )


def test_save_uses_atomic_sibling_replace(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "RCIS" / "settings.json"
    real_replace = settings_module.os.replace
    calls = []

    def recording_replace(source, destination):
        calls.append((Path(source), Path(destination)))
        return real_replace(source, destination)

    monkeypatch.setattr(
        settings_module.os,
        "replace",
        recording_replace,
    )

    save_remembered_intake_root(
        "C:/Pilot/Atomic",
        settings_path=path,
    )

    assert len(calls) == 1
    source, destination = calls[0]
    assert destination == path
    assert source.parent == path.parent
    assert source != path
    assert source.name.startswith(path.name + ".")
    assert not source.exists()
    assert path.is_file()
