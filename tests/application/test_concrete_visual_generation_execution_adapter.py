from __future__ import annotations

import ast
from pathlib import Path

import pytest

from rie.application.concrete_visual_generation_execution_adapter import (
    ConcreteVisualGenerationExecutionAdapter,
    ProviderExecutionResponse,
    ResolvedVisualReference,
    VisualGenerationExecutionConfig,
)
from rie.application.visual_generation_provider import VisualGenerationRequest


class _Resolver:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def resolve(self, asset_id: str) -> ResolvedVisualReference:
        self.calls.append(asset_id)
        return ResolvedVisualReference(
            requested_asset_id=asset_id,
            resolved_asset_id=asset_id,
            provider_media_ref=f"media:{asset_id}",
            use_eligible=True,
        )


def test_exact_deterministic_request_translation_and_result_normalization() -> None:
    resolver = _Resolver()
    calls: list[object] = []

    def transport(payload):
        calls.append(payload)
        return ProviderExecutionResponse(
            execution_status="SUCCEEDED",
            provider_output_refs=("provider-output-1",),
            provider_execution_ref="exec-1",
            diagnostic_message="completed",
        )

    adapter = ConcreteVisualGenerationExecutionAdapter(
        config=VisualGenerationExecutionConfig(
            provider_id="explicit-provider",
            model_id="explicit-model",
        ),
        reference_resolver=resolver,
        transport=transport,
    )
    result = adapter.generate(
        VisualGenerationRequest(
            grounded_prompt="Exact grounded prompt.",
            selected_reference_asset_ids=("asset-a", "asset-b"),
        )
    )

    assert resolver.calls == ["asset-a", "asset-b"]
    assert calls == [{
        "provider_id": "explicit-provider",
        "model_id": "explicit-model",
        "grounded_prompt": "Exact grounded prompt.",
        "reference_media_refs": ("media:asset-a", "media:asset-b"),
    }]
    assert result.provider_output_refs == ("provider-output-1",)
    assert "provider=explicit-provider" in result.message
    assert "model=explicit-model" in result.message
    assert "status=SUCCEEDED" in result.message
    assert "execution_ref=exec-1" in result.message


@pytest.mark.parametrize("field", ["provider_id", "model_id"])
def test_blank_provider_or_model_identity_fails_closed(field: str) -> None:
    values = {"provider_id": "provider", "model_id": "model"}
    values[field] = " "
    with pytest.raises(ValueError, match=field):
        VisualGenerationExecutionConfig(**values)


def test_reference_identity_mismatch_and_ineligible_reference_fail_closed() -> None:
    with pytest.raises(ValueError, match="identity"):
        ResolvedVisualReference(
            requested_asset_id="asset-a",
            resolved_asset_id="asset-b",
            provider_media_ref="media",
            use_eligible=True,
        )
    with pytest.raises(ValueError, match="use-eligible"):
        ResolvedVisualReference(
            requested_asset_id="asset-a",
            resolved_asset_id="asset-a",
            provider_media_ref="media",
            use_eligible=False,
        )


def test_failed_or_malformed_provider_response_cannot_become_success() -> None:
    with pytest.raises(ValueError, match="SUCCEEDED"):
        ProviderExecutionResponse(
            execution_status="FAILED",
            provider_output_refs=("fake-output",),
        )
    with pytest.raises(ValueError, match="must not be empty"):
        ProviderExecutionResponse(
            execution_status="SUCCEEDED",
            provider_output_refs=(),
        )


def test_adapter_has_no_hidden_provider_selection_retry_candidate_or_secret_behavior() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "src" / "rie" / "application"
        / "concrete_visual_generation_execution_adapter.py"
    )
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(a.name.split(".", 1)[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])
    assert imported_roots <= {"__future__", "dataclasses", "typing", "rie"}
    lowered = source.lower()
    for forbidden in (
        "api_key", "authorization", "bearer ", "os.environ", "requests",
        "httpx", "urllib", "retry(", "creativeresultcandidate",
    ):
        assert forbidden not in lowered
