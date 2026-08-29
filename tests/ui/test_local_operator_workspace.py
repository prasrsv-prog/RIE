from __future__ import annotations

import inspect
import json
from pathlib import Path

import rie.ui.local_operator_workspace as workspace_module
from rie.ui.local_operator_workspace import (
    clear_default_product_variant,
    clone_workspace,
    delete_preset,
    empty_workspace,
    load_workspace,
    record_recent_prompt,
    save_preset,
    save_workspace,
    set_default_product_variant,
    set_last_request,
    toggle_product_favorite,
    toggle_recent_favorite,
    workspace_path,
)


def _request(index: int = 1) -> dict:
    return {
        "product_id": f"product-{index}",
        "variant_id": f"variant-{index}",
        "background": f"background-{index}",
        "camera_angle": f"angle-{index}",
        "requested_output": f"output-{index}",
    }


def test_workspace_path_uses_localappdata_and_userprofile_fallback() -> None:
    local = workspace_path(
        {
            "LOCALAPPDATA": r"C:\Local",
            "USERPROFILE": r"C:\User",
        }
    )
    assert local == Path(r"C:\Local") / "RCIS" / "workspace.json"

    fallback = workspace_path(
        {
            "LOCALAPPDATA": "",
            "USERPROFILE": r"C:\User",
        }
    )
    assert fallback == (
        Path(r"C:\User")
        / "AppData"
        / "Local"
        / "RCIS"
        / "workspace.json"
    )


def test_missing_workspace_yields_empty_schema_v1_state(tmp_path) -> None:
    missing = tmp_path / "workspace.json"
    assert load_workspace(missing) == empty_workspace()


def test_canonical_roundtrip_preserves_all_workspace_state(tmp_path) -> None:
    path = tmp_path / "workspace.json"
    state = set_last_request(empty_workspace(), _request(1))
    state = record_recent_prompt(state, _request(1), "prompt-1")
    state = toggle_recent_favorite(state, 0)
    state = save_preset(state, "Hero", _request(2))
    state = toggle_product_favorite(state, "product-2", "variant-2")
    state = set_default_product_variant(
        state,
        "product-3",
        "variant-3",
    )

    save_workspace(state, path)
    raw = path.read_bytes()
    decoded = json.loads(raw.decode("utf-8"))

    assert raw.endswith(b"\n")
    assert not raw.endswith(b"\n\n")
    assert raw == (
        json.dumps(
            decoded,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")
    assert load_workspace(path) == state


def test_invalid_json_fails_safe_without_rewrite(tmp_path) -> None:
    path = tmp_path / "workspace.json"
    original = b"{invalid-json\n"
    path.write_bytes(original)

    assert load_workspace(path) == empty_workspace()
    assert path.read_bytes() == original


def test_unknown_schema_fails_safe_without_rewrite(tmp_path) -> None:
    path = tmp_path / "workspace.json"
    original = b'{"schema_version":99}\n'
    path.write_bytes(original)

    assert load_workspace(path) == empty_workspace()
    assert path.read_bytes() == original


def test_atomic_save_uses_sibling_temp_os_replace_and_one_final_lf(
    tmp_path,
    monkeypatch,
) -> None:
    path = tmp_path / "workspace.json"
    calls = []
    real_replace = workspace_module.os.replace

    def tracked_replace(source, target):
        calls.append((Path(source), Path(target)))
        return real_replace(source, target)

    monkeypatch.setattr(
        workspace_module.os,
        "replace",
        tracked_replace,
    )
    save_workspace(empty_workspace(), path)

    assert calls == [
        (
            path.with_name(path.name + ".tmp"),
            path,
        )
    ]
    assert path.read_bytes().endswith(b"\n")
    assert not path.read_bytes().endswith(b"\n\n")
    assert not path.with_name(path.name + ".tmp").exists()


def test_recent_prompt_is_newest_first_and_bounded_to_twenty() -> None:
    state = empty_workspace()
    for index in range(25):
        state = record_recent_prompt(
            state,
            _request(index),
            f"prompt-{index}",
        )

    assert len(state["recent_prompts"]) == 20
    assert state["recent_prompts"][0]["prompt_text"] == "prompt-24"
    assert state["recent_prompts"][-1]["prompt_text"] == "prompt-5"


def test_last_request_replacement_is_data_only() -> None:
    state = set_last_request(empty_workspace(), _request(7))
    assert state["last_request"] == _request(7)
    assert "submit" not in inspect.getsource(set_last_request).lower()


def test_preset_save_replaces_name_and_is_bounded_then_delete_works() -> None:
    state = empty_workspace()
    state = save_preset(state, "Same", _request(1))
    state = save_preset(state, "Same", _request(2))
    assert len(state["presets"]) == 1
    assert state["presets"][0]["product_id"] == "product-2"

    for index in range(25):
        state = save_preset(
            state,
            f"Preset {index}",
            _request(index),
        )
    assert len(state["presets"]) == 20

    state = delete_preset(state, "Preset 24")
    assert all(
        item["name"] != "Preset 24"
        for item in state["presets"]
    )


def test_recent_and_product_favorite_toggles_are_local_only() -> None:
    state = record_recent_prompt(
        empty_workspace(),
        _request(1),
        "prompt",
    )
    state = toggle_recent_favorite(state, 0)
    assert state["recent_prompts"][0]["favorite"] is True

    state = toggle_product_favorite(
        state,
        "product-1",
        "variant-1",
    )
    assert state["product_favorites"] == [
        {
            "product_id": "product-1",
            "variant_id": "variant-1",
        }
    ]
    state = toggle_product_favorite(
        state,
        "product-1",
        "variant-1",
    )
    assert state["product_favorites"] == []


def test_explicit_default_can_be_set_and_cleared() -> None:
    state = set_default_product_variant(
        empty_workspace(),
        "alpha",
        "alpha-a",
    )
    assert state["default_product_variant"] == {
        "product_id": "alpha",
        "variant_id": "alpha-a",
    }
    state = clear_default_product_variant(state)
    assert state["default_product_variant"] is None


def test_workspace_module_has_no_frozen_runtime_database_or_service_imports() -> None:
    source = inspect.getsource(workspace_module)
    lowered = source.lower()
    assert "sqlite" not in lowered
    assert "rie.rsv_knowledge" not in source
    assert "evidence_repository" not in source
    assert "knowledge_repository" not in source
    assert "grounded_prompt_application_service" not in source
    assert "grounded_prompt_application_composition_root" not in source
    assert "grounded_prompt_application_foundation_provider" not in source
