from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

import pytest

from rie.application.grounded_prompt_application_service import (
    FROZEN_GROUNDED_PROMPT_ORCHESTRATOR,
    GroundedPromptApplicationContractError,
    GroundedPromptApplicationRequest,
    GroundedPromptApplicationService,
    derive_grounded_prompt_application_foundation_dependency_names,
)


FROZEN_RUNTIME_IDENTITIES = {
    "src/rie/rsv_knowledge/product_catalog.py": (
        "normalized_lf_sha256",
        "a4f56bec5eeb8c1c4d6b41ab5c2acd0192f757287d0ee01a9a2658e34db4d483",
    ),
    "src/rie/rsv_knowledge/ingestion_manifest.py": (
        "normalized_lf_sha256",
        "68075dbd854df927fa910924fced193e0dc0675a55df7f9b83b8275031854874",
    ),
    "src/rie/rsv_knowledge/canonical_knowledge_taxonomy_mapping_materialization.py": (
        "normalized_lf_sha256",
        "173a7966912feecc2ecb4b31ddcc615dd69f828e0a56d8bc3301a4f261640384",
    ),
    "src/rie/rsv_knowledge/governed_prompt_input_materialization.py": (
        "normalized_lf_sha256",
        "335e7bb3a8c76eac8f24e9b811bde30db5604c2e22090a97cadf8ab62a343002",
    ),
    "src/rie/rsv_knowledge/constraint_binding.py": (
        "normalized_lf_sha256",
        "914301a58b749b642364883fb06f1c823270ded2c99074c1254b98c15349ed65",
    ),
    "src/rie/rsv_knowledge/grounded_prompt_compiler.py": (
        "normalized_lf_sha256",
        "527fc8f71b634a46bc3bd99fadae87833e43deb0f42fbcdcc2415b6531dcf375",
    ),
    "src/rie/rsv_knowledge/phase_b_prompt_input_bridge.py": (
        "raw_sha256",
        "8cd9474b6173a5febbe06999107a7d0a5d6c01de50742ea082a082449665af9b",
    ),
    "src/rie/rsv_knowledge/phase_b_grounded_prompt_orchestration.py": (
        "raw_sha256",
        "ef2f455ae632cb019b7081485226df011cacf68b29d99b128164efe182f06362",
    ),
    "src/rie/rsv_knowledge/phase_b_exact_six_active_constraint_bridge.py": (
        "raw_sha256",
        "0d730aafef18d639e9a285945de4191ccbed5e5fb5e1d3e5a44b9f5bdba2cfca",
    ),
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _normalized_lf_sha(path: Path) -> str:
    raw = path.read_bytes()
    crlf = raw.count(b"\r\n")
    assert raw.count(b"\r") == crlf
    assert raw.count(b"\x00") == 0
    assert not raw.startswith(b"\xef\xbb\xbf")
    return _sha_bytes(raw.replace(b"\r\n", b"\n"))


def _raw_sha(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _expected_foundation_dependencies() -> dict[str, object]:
    return {
        name: object()
        for name in derive_grounded_prompt_application_foundation_dependency_names(
            FROZEN_GROUNDED_PROMPT_ORCHESTRATOR
        )
    }


def _request() -> GroundedPromptApplicationRequest:
    return GroundedPromptApplicationRequest(
        product_id="sv300",
        variant_id="motif-carbon",
        creative_variables={"tone": "clean", "channel": "marketplace"},
        requested_output="prompt_text",
    )


def _signature_matched_fake(result=None, exception=None):
    signature = inspect.signature(FROZEN_GROUNDED_PROMPT_ORCHESTRATOR)
    calls = []

    def fake(**kwargs):
        calls.append(kwargs)
        if exception is not None:
            raise exception
        if callable(result):
            return result(kwargs)
        return result

    fake.__signature__ = signature
    fake.calls = calls
    return fake


def test_valid_request_success():
    expected = {
        "prompt_text": "PROMPT",
        "product_id": "sv300",
        "variant_id": "motif-carbon",
        "used_knowledge_ids": ["k1"],
        "used_asset_ids": ["a1"],
        "missing_knowledge": [],
        "conflicts": [],
        "grounding_status": "grounded",
        "bridge_result": {"ok": True},
        "exact_six_bridge_result": {"ok": True},
        "binding_result": {"ok": True},
        "compile_result": {"ok": True},
    }
    fake = _signature_matched_fake(result=expected)
    deps = _expected_foundation_dependencies()
    service = GroundedPromptApplicationService(
        orchestrator=fake,
        foundation_dependencies=deps,
    )

    result = service.execute(_request())

    assert result is expected
    assert len(fake.calls) == 1
    call = fake.calls[0]
    assert call["product_id"] == "sv300"
    assert call["variant_id"] == "motif-carbon"
    assert call["requested_output"] == "prompt_text"
    assert call["creative_variables"] == {
        "tone": "clean",
        "channel": "marketplace",
    }
    for name, value in deps.items():
        assert call[name] is value


def test_invalid_request_fail_closed():
    fake = _signature_matched_fake(result={"ok": True})
    service = GroundedPromptApplicationService(
        orchestrator=fake,
        foundation_dependencies=_expected_foundation_dependencies(),
    )

    with pytest.raises(GroundedPromptApplicationContractError):
        service.execute(
            GroundedPromptApplicationRequest(
                product_id="",
                variant_id="motif-carbon",
                creative_variables={"tone": "clean"},
                requested_output="prompt_text",
            )
        )

    with pytest.raises(GroundedPromptApplicationContractError):
        service.execute(
            GroundedPromptApplicationRequest(
                product_id="sv300",
                variant_id="motif-carbon",
                creative_variables={"tone": ""},
                requested_output="prompt_text",
            )
        )


def test_frozen_core_error_passthrough():
    expected_exception = RuntimeError("frozen orchestrator failure")
    fake = _signature_matched_fake(exception=expected_exception)
    service = GroundedPromptApplicationService(
        orchestrator=fake,
        foundation_dependencies=_expected_foundation_dependencies(),
    )

    with pytest.raises(RuntimeError) as raised:
        service.execute(_request())

    assert raised.value is expected_exception


def test_deterministic_repeat():
    fake = _signature_matched_fake(
        result=lambda kwargs: {
            "prompt_text": kwargs["requested_output"],
            "product_id": kwargs["product_id"],
            "variant_id": kwargs["variant_id"],
            "used_knowledge_ids": ["k1", "k2"],
            "used_asset_ids": ["a1"],
            "missing_knowledge": [],
            "conflicts": [],
            "grounding_status": "grounded",
            "bridge_result": {"stable": True},
            "exact_six_bridge_result": {"stable": True},
            "binding_result": {"stable": True},
            "compile_result": {"stable": True},
        }
    )
    service = GroundedPromptApplicationService(
        orchestrator=fake,
        foundation_dependencies=_expected_foundation_dependencies(),
    )

    first = service.execute(_request())
    second = service.execute(_request())

    assert first == second
    assert len(fake.calls) == 2


def test_audit_surface_preserved():
    expected = {
        "prompt_text": "PROMPT",
        "product_id": "sv300",
        "variant_id": "motif-carbon",
        "used_knowledge_ids": ["k1"],
        "used_asset_ids": ["a1"],
        "missing_knowledge": [],
        "conflicts": [],
        "grounding_status": "grounded",
        "bridge_result": {"layer": 1},
        "exact_six_bridge_result": {"layer": 2},
        "binding_result": {"layer": 3},
        "compile_result": {"layer": 4},
        "extra_metadata": {"keep": "unchanged"},
    }
    fake = _signature_matched_fake(result=expected)
    service = GroundedPromptApplicationService(
        orchestrator=fake,
        foundation_dependencies=_expected_foundation_dependencies(),
    )

    result = service.execute(_request())

    assert result is expected
    assert result["bridge_result"] == {"layer": 1}
    assert result["exact_six_bridge_result"] == {"layer": 2}
    assert result["binding_result"] == {"layer": 3}
    assert result["compile_result"] == {"layer": 4}
    assert result["extra_metadata"] == {"keep": "unchanged"}


def test_frozen_core_identity_unchanged():
    def snapshot() -> dict[str, str]:
        values: dict[str, str] = {}
        repo_root = _repo_root()
        for relative, (mode, expected) in FROZEN_RUNTIME_IDENTITIES.items():
            path = repo_root / relative
            actual = (
                _normalized_lf_sha(path)
                if mode == "normalized_lf_sha256"
                else _raw_sha(path)
            )
            assert actual == expected
            values[relative] = actual
        return values

    before = snapshot()
    fake = _signature_matched_fake(result={"ok": True})
    service = GroundedPromptApplicationService(
        orchestrator=fake,
        foundation_dependencies=_expected_foundation_dependencies(),
    )

    result = service.execute(_request())

    after = snapshot()

    assert result == {"ok": True}
    assert before == after
