from __future__ import annotations

import ast
from pathlib import Path

import pytest

from rie.application.visual_generation_provider import (
    VisualGenerationRequest,
    VisualGenerationResult,
)


MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "rie"
    / "application"
    / "visual_generation_provider.py"
)


def test_request_preserves_exact_grounded_prompt_and_reference_ids() -> None:
    request = VisualGenerationRequest(
        grounded_prompt="Grounded prompt\nwith exact spacing.",
        selected_reference_asset_ids=("asset-a", "asset-b"),
    )

    assert request.grounded_prompt == "Grounded prompt\nwith exact spacing."
    assert request.selected_reference_asset_ids == ("asset-a", "asset-b")


def test_request_fails_closed_for_blank_prompt_or_duplicate_reference_ids() -> None:
    with pytest.raises(ValueError, match="grounded_prompt"):
        VisualGenerationRequest(grounded_prompt="   ")

    with pytest.raises(ValueError, match="must not contain duplicates"):
        VisualGenerationRequest(
            grounded_prompt="prompt",
            selected_reference_asset_ids=("asset-a", "asset-a"),
        )


def test_result_preserves_only_provider_local_refs_and_message() -> None:
    result = VisualGenerationResult(
        provider_output_refs=("provider-output-1", "provider-output-2"),
        message="Provider completed the request.",
    )

    assert result.provider_output_refs == (
        "provider-output-1",
        "provider-output-2",
    )
    assert result.message == "Provider completed the request."


def test_provider_boundary_module_has_no_runtime_io_network_or_model_dependency() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))

    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= {"__future__", "dataclasses", "typing"}
