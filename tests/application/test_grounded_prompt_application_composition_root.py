from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import rie.application.grounded_prompt_application_composition_root as composition_root
from rie.application.grounded_prompt_application_service import (
    FROZEN_GROUNDED_PROMPT_ORCHESTRATOR,
    GroundedPromptApplicationService,
)


EXPECTED_DEPENDENCY_NAMES = (
    "collection_id",
    "catalog",
    "governed_knowledge",
    "knowledge_mappings",
    "traceable_evidence_items",
    "product_constraint_governed_knowledge",
    "product_constraint_ingestion_manifest_records",
    "product_constraint_knowledge_mappings",
)

PUBLISHED_APPLICATION_SERVICE_SHA256 = (
    "d160737397a1836b5b4d7ca82c3b572ca52475675fb78dfb97559eb80c11ab7a"
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


def _dependencies() -> dict[str, object]:
    return {name: object() for name in EXPECTED_DEPENDENCY_NAMES}


def _build_kwargs(dependencies: dict[str, object]) -> dict[str, object]:
    return {name: dependencies[name] for name in EXPECTED_DEPENDENCY_NAMES}


def test_exact_eight_dependency_assembly(monkeypatch):
    captured = {}

    class FakeService:
        def __init__(self, *, orchestrator, foundation_dependencies):
            captured["orchestrator"] = orchestrator
            captured["foundation_dependencies"] = foundation_dependencies

    monkeypatch.setattr(
        composition_root,
        "GroundedPromptApplicationService",
        FakeService,
    )

    dependencies = _dependencies()
    result = composition_root.build_grounded_prompt_application_service(
        **_build_kwargs(dependencies)
    )

    assert isinstance(result, FakeService)
    assert tuple(captured["foundation_dependencies"]) == EXPECTED_DEPENDENCY_NAMES
    assert len(captured["foundation_dependencies"]) == 8


def test_returns_published_application_service():
    dependencies = _dependencies()

    result = composition_root.build_grounded_prompt_application_service(
        **_build_kwargs(dependencies)
    )

    assert isinstance(result, GroundedPromptApplicationService)


def test_uses_exact_frozen_orchestrator(monkeypatch):
    captured = {}

    class FakeService:
        def __init__(self, *, orchestrator, foundation_dependencies):
            captured["orchestrator"] = orchestrator
            captured["foundation_dependencies"] = foundation_dependencies

    monkeypatch.setattr(
        composition_root,
        "GroundedPromptApplicationService",
        FakeService,
    )

    composition_root.build_grounded_prompt_application_service(
        **_build_kwargs(_dependencies())
    )

    assert captured["orchestrator"] is FROZEN_GROUNDED_PROMPT_ORCHESTRATOR


def test_dependency_object_identity_preserved(monkeypatch):
    captured = {}

    class FakeService:
        def __init__(self, *, orchestrator, foundation_dependencies):
            captured["foundation_dependencies"] = foundation_dependencies

    monkeypatch.setattr(
        composition_root,
        "GroundedPromptApplicationService",
        FakeService,
    )

    dependencies = _dependencies()
    composition_root.build_grounded_prompt_application_service(
        **_build_kwargs(dependencies)
    )

    for name in EXPECTED_DEPENDENCY_NAMES:
        assert captured["foundation_dependencies"][name] is dependencies[name]


def test_application_service_constructor_failure_passthrough(monkeypatch):
    expected = RuntimeError("application service constructor failure")

    class FailingService:
        def __init__(self, *, orchestrator, foundation_dependencies):
            raise expected

    monkeypatch.setattr(
        composition_root,
        "GroundedPromptApplicationService",
        FailingService,
    )

    with pytest.raises(RuntimeError) as raised:
        composition_root.build_grounded_prompt_application_service(
            **_build_kwargs(_dependencies())
        )

    assert raised.value is expected


def test_published_service_and_frozen_core_identity_unchanged():
    repo_root = _repo_root()
    service_path = (
        repo_root
        / "src/rie/application/grounded_prompt_application_service.py"
    )

    before_service = _raw_sha(service_path)
    assert before_service == PUBLISHED_APPLICATION_SERVICE_SHA256

    before_frozen = {}
    for relative, (mode, expected) in FROZEN_RUNTIME_IDENTITIES.items():
        path = repo_root / relative
        actual = (
            _normalized_lf_sha(path)
            if mode == "normalized_lf_sha256"
            else _raw_sha(path)
        )
        assert actual == expected
        before_frozen[relative] = actual

    composition_root.build_grounded_prompt_application_service(
        **_build_kwargs(_dependencies())
    )

    after_service = _raw_sha(service_path)
    after_frozen = {}
    for relative, (mode, expected) in FROZEN_RUNTIME_IDENTITIES.items():
        path = repo_root / relative
        actual = (
            _normalized_lf_sha(path)
            if mode == "normalized_lf_sha256"
            else _raw_sha(path)
        )
        assert actual == expected
        after_frozen[relative] = actual

    assert before_service == after_service
    assert before_frozen == after_frozen
