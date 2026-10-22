"""Local noncanonical operator workspace state for RCIS Phase J."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Mapping

SCHEMA_VERSION = 1
HISTORY_LIMIT = 20
PRESET_LIMIT = 20
PRODUCT_FAVORITE_LIMIT = 20
_REQUEST_FIELDS = (
    "product_id",
    "variant_id",
    "background",
    "camera_angle",
    "requested_output",
)


def empty_workspace() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "last_request": None,
        "recent_prompts": [],
        "presets": [],
        "product_favorites": [],
        "default_product_variant": None,
    }


def workspace_path(
    environ: Mapping[str, str] | None = None,
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
            base = Path.home() / "AppData" / "Local"
    return base / "RCIS" / "workspace.json"


def _request(value: object) -> dict:
    source = value if isinstance(value, dict) else {}
    return {
        field: str(source.get(field, ""))
        for field in _REQUEST_FIELDS
    }


def _recent_entry(value: object) -> dict | None:
    if not isinstance(value, dict):
        return None
    request = _request(value)
    entry = {
        **request,
        "prompt_text": str(value.get("prompt_text", "")),
        "favorite": bool(value.get("favorite", False)),
    }
    # Treat richer PySide context as opaque local annotation, never as rights.
    # Keep it through Tkinter clone/save cycles without making it authoritative.
    if isinstance(value.get("pyside_context"), dict):
        entry["pyside_context"] = copy.deepcopy(value["pyside_context"])
    return entry


def _preset_entry(value: object) -> dict | None:
    if not isinstance(value, dict):
        return None
    name = str(value.get("name", "")).strip()
    if not name:
        return None
    return {
        "name": name,
        **_request(value),
    }


def _product_favorite(value: object) -> dict | None:
    if not isinstance(value, dict):
        return None
    product_id = str(value.get("product_id", "")).strip()
    variant_id = str(value.get("variant_id", "")).strip()
    if not product_id or not variant_id:
        return None
    return {
        "product_id": product_id,
        "variant_id": variant_id,
    }


def _default_product_variant(value: object) -> dict | None:
    return _product_favorite(value)


def normalize_workspace(value: object) -> dict:
    if not isinstance(value, dict):
        return empty_workspace()
    if value.get("schema_version") != SCHEMA_VERSION:
        return empty_workspace()

    normalized = empty_workspace()

    last_request = value.get("last_request")
    if isinstance(last_request, dict):
        normalized["last_request"] = _request(last_request)

    recent = []
    for item in value.get("recent_prompts", []):
        normalized_item = _recent_entry(item)
        if normalized_item is not None:
            recent.append(normalized_item)
    normalized["recent_prompts"] = recent[:HISTORY_LIMIT]

    presets = []
    seen_names = set()
    for item in value.get("presets", []):
        normalized_item = _preset_entry(item)
        if normalized_item is None:
            continue
        name = normalized_item["name"]
        if name in seen_names:
            continue
        seen_names.add(name)
        presets.append(normalized_item)
    normalized["presets"] = presets[:PRESET_LIMIT]

    favorites = []
    seen_favorites = set()
    for item in value.get("product_favorites", []):
        normalized_item = _product_favorite(item)
        if normalized_item is None:
            continue
        key = (
            normalized_item["product_id"],
            normalized_item["variant_id"],
        )
        if key in seen_favorites:
            continue
        seen_favorites.add(key)
        favorites.append(normalized_item)
    normalized["product_favorites"] = favorites[
        :PRODUCT_FAVORITE_LIMIT
    ]

    normalized["default_product_variant"] = (
        _default_product_variant(
            value.get("default_product_variant")
        )
    )
    return normalized


def load_workspace(path: Path | str | None = None) -> dict:
    target = workspace_path() if path is None else Path(path)
    if not target.is_file():
        return empty_workspace()
    try:
        raw = target.read_bytes()
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return empty_workspace()
    return normalize_workspace(value)


def save_workspace(
    workspace: object,
    path: Path | str | None = None,
) -> Path:
    target = workspace_path() if path is None else Path(path)
    normalized = normalize_workspace(workspace)
    raw = (
        json.dumps(
            normalized,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(raw)
    os.replace(temporary, target)
    return target


def set_last_request(
    workspace: object,
    request: object,
) -> dict:
    updated = normalize_workspace(workspace)
    updated["last_request"] = _request(request)
    return updated


def record_recent_prompt(
    workspace: object,
    request: object,
    prompt_text: str,
    *,
    pyside_context: dict | None = None,
) -> dict:
    updated = normalize_workspace(workspace)
    entry = {
        **_request(request),
        "prompt_text": str(prompt_text),
        "favorite": False,
    }
    if pyside_context is not None:
        if not isinstance(pyside_context, dict) or pyside_context.get("schema_version") != 1:
            raise ValueError("unsupported PySide context")
        entry["pyside_context"] = copy.deepcopy(pyside_context)
    updated["recent_prompts"] = (
        [entry] + updated["recent_prompts"]
    )[:HISTORY_LIMIT]
    return updated


def append_pyside_history_prompt(
    request: dict,
    prompt_text: str,
    pyside_context: dict,
    *,
    path: Path | str | None = None,
) -> Path:
    """Explicit, guarded local save; never discard legacy/future workspace data.

    The existing v1 five-field request remains readable by Tkinter. Full
    PySide brief/reference IDs are an opaque annotation, not a rights grant.
    Unknown/malformed workspace data and a full history refuse mutation.
    """
    if not isinstance(prompt_text, str) or not prompt_text.strip():
        raise ValueError("empty prompt; workspace unchanged")
    if not isinstance(pyside_context, dict) or pyside_context.get("schema_version") != 1:
        raise ValueError("unsupported PySide context; workspace unchanged")
    if not isinstance(pyside_context.get("brief"), dict) or not isinstance(pyside_context.get("grounding"), dict):
        raise ValueError("incomplete PySide context; workspace unchanged")
    # Reject non-JSON payloads before touching any user file.
    json.dumps(pyside_context, ensure_ascii=True, allow_nan=False)
    target = workspace_path() if path is None else Path(path)
    if target.is_symlink() or (target.exists() and not target.is_file()):
        raise ValueError("unsafe workspace target")
    temp = target.with_name(target.name + ".tmp")
    if temp.exists() or temp.is_symlink():
        raise ValueError("workspace temporary file already exists")
    if target.exists():
        original = target.read_bytes()
        try:
            decoded = json.loads(original.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("unreadable workspace; unchanged") from exc
        if not isinstance(decoded, dict) or decoded.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("unsupported workspace; unchanged")
        state = normalize_workspace(decoded)
        if decoded != state:
            raise ValueError("noncanonical workspace; refuse lossy rewrite")
    else:
        original = None
        state = empty_workspace()
    if len(state["recent_prompts"]) >= HISTORY_LIMIT:
        raise ValueError("history at capacity; refuse eviction")
    updated = record_recent_prompt(
        state, request, prompt_text, pyside_context=pyside_context,
    )
    # Optimistic guard against another writer during validation.
    if original is None:
        if target.exists():
            raise ValueError("workspace created by another process")
    elif not target.exists() or target.read_bytes() != original:
        raise ValueError("workspace changed concurrently")
    return save_workspace(updated, target)


def toggle_recent_favorite(
    workspace: object,
    index: int,
) -> dict:
    updated = normalize_workspace(workspace)
    if index < 0 or index >= len(updated["recent_prompts"]):
        return updated
    updated["recent_prompts"][index]["favorite"] = not bool(
        updated["recent_prompts"][index]["favorite"]
    )
    return updated


def delete_recent_prompt(
    workspace: object,
    index: int,
) -> dict:
    updated = normalize_workspace(workspace)
    if index < 0 or index >= len(updated["recent_prompts"]):
        return updated
    del updated["recent_prompts"][index]
    return updated


def save_preset(
    workspace: object,
    name: str,
    request: object,
) -> dict:
    normalized_name = str(name).strip()
    if not normalized_name:
        raise ValueError("preset name must not be empty")
    updated = normalize_workspace(workspace)
    replacement = {
        "name": normalized_name,
        **_request(request),
    }
    remaining = [
        item
        for item in updated["presets"]
        if item["name"] != normalized_name
    ]
    updated["presets"] = (
        [replacement] + remaining
    )[:PRESET_LIMIT]
    return updated


def delete_preset(
    workspace: object,
    name: str,
) -> dict:
    normalized_name = str(name).strip()
    updated = normalize_workspace(workspace)
    updated["presets"] = [
        item
        for item in updated["presets"]
        if item["name"] != normalized_name
    ]
    return updated


def toggle_product_favorite(
    workspace: object,
    product_id: str,
    variant_id: str,
) -> dict:
    product = str(product_id).strip()
    variant = str(variant_id).strip()
    updated = normalize_workspace(workspace)
    if not product or not variant:
        return updated
    key = (product, variant)
    existing = [
        item
        for item in updated["product_favorites"]
        if (item["product_id"], item["variant_id"]) != key
    ]
    if len(existing) != len(updated["product_favorites"]):
        updated["product_favorites"] = existing
        return updated
    updated["product_favorites"] = (
        [{"product_id": product, "variant_id": variant}]
        + existing
    )[:PRODUCT_FAVORITE_LIMIT]
    return updated


def set_default_product_variant(
    workspace: object,
    product_id: str,
    variant_id: str,
) -> dict:
    product = str(product_id).strip()
    variant = str(variant_id).strip()
    if not product or not variant:
        raise ValueError(
            "default product_id and variant_id must not be empty"
        )
    updated = normalize_workspace(workspace)
    updated["default_product_variant"] = {
        "product_id": product,
        "variant_id": variant,
    }
    return updated


def clear_default_product_variant(workspace: object) -> dict:
    updated = normalize_workspace(workspace)
    updated["default_product_variant"] = None
    return updated


def clone_workspace(workspace: object) -> dict:
    return copy.deepcopy(normalize_workspace(workspace))
