from __future__ import annotations

import ast
from pathlib import Path

import pytest

from rie.application.concrete_visual_generation_execution_adapter import (
    ProviderExecutionResponse,
    ResolvedVisualReference,
    VisualGenerationExecutionConfig,
)
from rie.application.execute_visual_generation_with_provider_response_capture import (
    _SingleCallProviderResponseCapture,
    execute_visual_generation_with_provider_response_capture,
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


def test_exact_response_is_captured_from_one_adapter_transport_call() -> None:
    resolver = _Resolver()
    transport_calls: list[object] = []
    response = ProviderExecutionResponse(
        execution_status="SUCCEEDED",
        provider_output_refs=("provider-output-1",),
        provider_execution_ref="execution-1",
        diagnostic_message="completed",
    )

    def transport(payload):
        transport_calls.append(payload)
        return response

    captured = execute_visual_generation_with_provider_response_capture(
        request=VisualGenerationRequest(
            grounded_prompt="Exact grounded prompt.",
            selected_reference_asset_ids=("asset-a",),
        ),
        execution_config=VisualGenerationExecutionConfig(
            provider_id="explicit-provider",
            model_id="explicit-model",
        ),
        reference_resolver=resolver,
        transport=transport,
    )

    assert resolver.calls == ["asset-a"]
    assert len(transport_calls) == 1
    assert transport_calls[0] == {
        "provider_id": "explicit-provider",
        "model_id": "explicit-model",
        "grounded_prompt": "Exact grounded prompt.",
        "reference_media_refs": ("media:asset-a",),
    }
    assert captured.provider_execution_response is response
    assert captured.visual_generation_result.provider_output_refs == (
        "provider-output-1",
    )
    assert "provider=explicit-provider" in captured.visual_generation_result.message
    assert "model=explicit-model" in captured.visual_generation_result.message
    assert "execution_ref=execution-1" in captured.visual_generation_result.message


def test_single_call_capture_rejects_second_transport_invocation() -> None:
    calls: list[object] = []
    response = ProviderExecutionResponse(
        execution_status="SUCCEEDED",
        provider_output_refs=("provider-output-1",),
    )

    def transport(payload):
        calls.append(payload)
        return response

    capture = _SingleCallProviderResponseCapture(transport)
    payload = {"provider_id": "provider"}

    assert capture(payload) is response
    with pytest.raises(RuntimeError, match="exactly one call"):
        capture(payload)

    assert len(calls) == 1
    assert capture.call_count == 1
    assert capture.response is response


def test_malformed_transport_response_fails_closed() -> None:
    resolver = _Resolver()

    def transport(_payload):
        return object()

    with pytest.raises(TypeError, match="ProviderExecutionResponse"):
        execute_visual_generation_with_provider_response_capture(
            request=VisualGenerationRequest(grounded_prompt="Prompt"),
            execution_config=VisualGenerationExecutionConfig(
                provider_id="provider",
                model_id="model",
            ),
            reference_resolver=resolver,
            transport=transport,
        )


def test_wrong_request_or_config_type_fails_closed() -> None:
    resolver = _Resolver()

    def transport(_payload):
        return ProviderExecutionResponse(
            execution_status="SUCCEEDED",
            provider_output_refs=("output-1",),
        )

    with pytest.raises(TypeError, match="VisualGenerationRequest"):
        execute_visual_generation_with_provider_response_capture(
            request=object(),
            execution_config=VisualGenerationExecutionConfig(
                provider_id="provider",
                model_id="model",
            ),
            reference_resolver=resolver,
            transport=transport,
        )

    with pytest.raises(TypeError, match="VisualGenerationExecutionConfig"):
        execute_visual_generation_with_provider_response_capture(
            request=VisualGenerationRequest(grounded_prompt="Prompt"),
            execution_config=object(),
            reference_resolver=resolver,
            transport=transport,
        )


def test_helper_has_no_candidate_persistence_retry_fallback_or_secret_behavior() -> None:
    module_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "application"
        / "execute_visual_generation_with_provider_response_capture.py"
    )
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".", 1)[0])

    assert imported_roots <= {"__future__", "dataclasses", "typing", "rie"}

    lowered = source.lower()
    for forbidden in (
        "api_key",
        "authorization:",
        "bearer ",
        "os.environ",
        "requests",
        "httpx",
        "urllib",
        "bridge_generated_output_to_creative_result_candidate",
        "retry(",
        "fallback(",
    ):
        assert forbidden not in lowered
