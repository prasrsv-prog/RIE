"""Per-user local settings for the RCIS grounded-prompt desktop UI."""

from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path
import uuid


SETTINGS_SCHEMA_VERSION = 1
SETTINGS_DIRECTORY_NAME = "RCIS"
SETTINGS_FILENAME = "settings.json"


def default_settings_path(
    *,
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    values = os.environ if environ is None else environ
    local_app_data = str(values.get("LOCALAPPDATA", "")).strip()
    if local_app_data:
        base = Path(local_app_data)
    else:
        user_profile = str(values.get("USERPROFILE", "")).strip()
        if user_profile:
            base = Path(user_profile) / "AppData" / "Local"
        else:
            selected_home = Path.home() if home is None else Path(home)
            base = selected_home / "AppData" / "Local"
    return base / SETTINGS_DIRECTORY_NAME / SETTINGS_FILENAME


def load_remembered_intake_root(
    *,
    settings_path: str | os.PathLike[str] | None = None,
) -> str | None:
    path = (
        default_settings_path()
        if settings_path is None
        else Path(settings_path)
    )
    try:
        raw = path.read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None

    if not isinstance(value, dict):
        return None
    if set(value) != {"schema_version", "intake_root"}:
        return None
    if value.get("schema_version") != SETTINGS_SCHEMA_VERSION:
        return None

    intake_root = value.get("intake_root")
    if not isinstance(intake_root, str):
        return None
    intake_root = intake_root.strip()
    return intake_root or None


def save_remembered_intake_root(
    intake_root: str,
    *,
    settings_path: str | os.PathLike[str] | None = None,
) -> Path:
    if not isinstance(intake_root, str) or not intake_root.strip():
        raise ValueError("intake_root must be a non-empty string")

    path = (
        default_settings_path()
        if settings_path is None
        else Path(settings_path)
    )
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "schema_version": SETTINGS_SCHEMA_VERSION,
        "intake_root": intake_root.strip(),
    }
    raw = (
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        + "\n"
    ).encode("utf-8")

    temporary = path.with_name(
        path.name + "." + uuid.uuid4().hex + ".tmp"
    )
    try:
        with temporary.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass

    return path
