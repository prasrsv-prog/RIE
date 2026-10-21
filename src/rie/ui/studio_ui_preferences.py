"""Isolated local RCIS Creative Studio language preference (C20-H1).

The legacy RCIS/settings.json intake-root schema must remain UNCHANGED.
"""
from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path
import uuid

from rie.ui.studio_localization import DEFAULT_LOCALE, SUPPORTED_LOCALES

PREFERENCES_SCHEMA_VERSION = 1
PREFERENCES_FILENAME = "studio-ui.json"


def default_ui_preferences_path(*, environ: Mapping[str, str] | None = None,
                                home: Path | None = None) -> Path:
    env = os.environ if environ is None else environ
    local = str(env.get("LOCALAPPDATA", "")).strip()
    if local:
        base = Path(local)
    else:
        profile = str(env.get("USERPROFILE", "")).strip()
        base = Path(profile) / "AppData" / "Local" if profile else (home or Path.home()) / "AppData" / "Local"
    return base / "RCIS" / PREFERENCES_FILENAME


def load_preferred_locale(*, preferences_path: str | os.PathLike[str] | None = None) -> str:
    path = default_ui_preferences_path() if preferences_path is None else Path(preferences_path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return DEFAULT_LOCALE
    if (not isinstance(value, dict)
            or set(value) != {"schema_version", "locale"}
            or value.get("schema_version") != PREFERENCES_SCHEMA_VERSION
            or not isinstance(value.get("locale"), str)
            or value["locale"] not in SUPPORTED_LOCALES):
        return DEFAULT_LOCALE
    return value["locale"]


def save_preferred_locale(locale: str, *,
                          preferences_path: str | os.PathLike[str] | None = None) -> Path:
    if not isinstance(locale, str) or locale not in SUPPORTED_LOCALES:
        raise ValueError("unsupported UI locale")
    path = default_ui_preferences_path() if preferences_path is None else Path(preferences_path)
    if path.is_symlink():
        raise ValueError("UI preference path must not be a symlink")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps({"schema_version": PREFERENCES_SCHEMA_VERSION,
                       "locale": locale}, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":")) + "\n").encode("utf-8")
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
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
