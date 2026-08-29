from __future__ import annotations

import dataclasses
import hashlib
import os
from pathlib import Path
import shutil
import sqlite3

import pytest

import rie.application.grounded_prompt_application_foundation_provider as provider_module
from rie.application.grounded_prompt_application_composition_root import (
    build_grounded_prompt_application_service,
)
from rie.application.grounded_prompt_application_foundation_provider import (
    GroundedPromptApplicationFoundation,
    GroundedPromptApplicationFoundationProviderContractError,
    load_frozen_pilot_grounded_prompt_application_foundation,
)
from rie.application.grounded_prompt_application_service import (
    GroundedPromptApplicationRequest,
    GroundedPromptApplicationService,
)


INTAKE_ROOT = Path(
    os.environ.get(
        "RCIS_TEST_INTAKE_ROOT",
        str(
            Path.home()
            / "Downloads"
            / "RCIS-RSV-Real-Asset-Pilot-01-Intake"
        ),
    )
)
FOUNDATION_FIELDS = (
    "collection_id",
    "catalog",
    "governed_knowledge",
    "knowledge_mappings",
    "traceable_evidence_items",
    "product_constraint_governed_knowledge",
    "product_constraint_ingestion_manifest_records",
    "product_constraint_knowledge_mappings",
)
ARTIFACTS = (
    "pilot-source-intake-manifest.tsv",
    "pilot-source-identity-capture.tsv",
    "pilot-authoritative-knowledge-taxonomy-mapping-canonical-data.json",
    "pilot-product-variant-exact18-canonical-mapping-extension.json",
    "pilot-canonical-evidence-repository-v2-state/pilot-evidence-repository-v2.sqlite3",
    "pilot-governed-knowledge-repository-state/pilot-governed-knowledge-repository.sqlite3",
)


def _load() -> GroundedPromptApplicationFoundation:
    return load_frozen_pilot_grounded_prompt_application_foundation(
        intake_root=INTAKE_ROOT
    )


def _service(foundation: GroundedPromptApplicationFoundation) -> GroundedPromptApplicationService:
    return build_grounded_prompt_application_service(
        collection_id=foundation.collection_id,
        catalog=foundation.catalog,
        governed_knowledge=foundation.governed_knowledge,
        knowledge_mappings=foundation.knowledge_mappings,
        traceable_evidence_items=foundation.traceable_evidence_items,
        product_constraint_governed_knowledge=(
            foundation.product_constraint_governed_knowledge
        ),
        product_constraint_ingestion_manifest_records=(
            foundation.product_constraint_ingestion_manifest_records
        ),
        product_constraint_knowledge_mappings=(
            foundation.product_constraint_knowledge_mappings
        ),
    )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_hashes(root: Path) -> tuple[str, ...]:
    return tuple(_sha(root / Path(relative)) for relative in ARTIFACTS)


def _copy_frozen_artifacts(target: Path) -> None:
    for relative in ARTIFACTS:
        source = INTAKE_ROOT / Path(relative)
        destination = target / Path(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def test_frozen_foundation_dataclass_has_exact_eight_fields_and_is_immutable() -> None:
    assert tuple(field.name for field in dataclasses.fields(
        GroundedPromptApplicationFoundation
    )) == FOUNDATION_FIELDS
    foundation = _load()
    with pytest.raises(dataclasses.FrozenInstanceError):
        foundation.collection_id = "changed"


def test_real_frozen_pilot_state_loads_exact_eight_dependencies_with_18_18_18_and_3_3_3_counts() -> None:
    foundation = _load()

    assert foundation.collection_id.startswith("evc1_")
    assert len(foundation.catalog.products) == 3
    assert len(foundation.catalog.variants) == 18
    assert len(foundation.governed_knowledge) == 18
    assert len(foundation.knowledge_mappings) == 18
    assert len(foundation.traceable_evidence_items) == 18
    assert len(foundation.product_constraint_governed_knowledge) == 3
    assert len(foundation.product_constraint_ingestion_manifest_records) == 3
    assert len(foundation.product_constraint_knowledge_mappings) == 3
    assert all(
        isinstance(value, tuple)
        for value in (
            foundation.governed_knowledge,
            foundation.knowledge_mappings,
            foundation.traceable_evidence_items,
            foundation.product_constraint_governed_knowledge,
            foundation.product_constraint_ingestion_manifest_records,
            foundation.product_constraint_knowledge_mappings,
        )
    )


def test_real_loaded_foundation_constructs_published_application_service_through_published_composition_root() -> None:
    service = _service(_load())
    assert isinstance(service, GroundedPromptApplicationService)


def test_real_loaded_service_executes_one_explicit_known_request_with_passed_grounding_without_provider_product_variant_selection() -> None:
    service = _service(_load())
    result = service.execute(
        GroundedPromptApplicationRequest(
            product_id="sv300",
            variant_id="sv300-white-glossy",
            creative_variables={
                "background": "dark studio",
                "camera_angle": "front",
            },
            requested_output="grounded product prompt",
        )
    )

    assert result.bridge_result.prompt_inputs.materialization_status == "PASSED"
    assert result.exact_six_bridge_result.prompt_inputs.materialization_status == "PASSED"
    assert result.binding_result.binding_status == "PASSED"
    assert result.compile_result.grounding_status == "PASSED"
    assert result.compile_result.product_id == "sv300"
    assert result.compile_result.variant_id == "sv300-white-glossy"


def test_wrong_or_mutated_artifact_hash_fails_closed_before_repository_materialization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _copy_frozen_artifacts(tmp_path)
    manifest = tmp_path / "pilot-source-intake-manifest.tsv"
    manifest.write_bytes(manifest.read_bytes() + b"X")

    repository_constructed = False

    def forbidden_repository(*args, **kwargs):
        nonlocal repository_constructed
        repository_constructed = True
        raise AssertionError("repository must not be constructed after hash failure")

    monkeypatch.setattr(
        provider_module,
        "SqliteEvidenceCollectionRepository",
        forbidden_repository,
    )

    with pytest.raises(
        GroundedPromptApplicationFoundationProviderContractError,
        match="SHA256 mismatch",
    ):
        load_frozen_pilot_grounded_prompt_application_foundation(
            intake_root=tmp_path
        )
    assert repository_constructed is False


def test_missing_or_duplicate_mapping_or_repository_lookup_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_materializer = provider_module.materialize_canonical_knowledge_taxonomy_mapping_records

    def duplicate_exact18(dataset):
        records = tuple(real_materializer(dataset))
        if len(records) == 18:
            return records[:-1] + (records[0],)
        return records

    monkeypatch.setattr(
        provider_module,
        "materialize_canonical_knowledge_taxonomy_mapping_records",
        duplicate_exact18,
    )

    with pytest.raises(
        GroundedPromptApplicationFoundationProviderContractError,
        match="duplication",
    ):
        _load()


def test_provider_is_deterministic_for_same_verified_frozen_state() -> None:
    first = _load()
    second = _load()

    assert first.collection_id == second.collection_id
    assert first.catalog.products == second.catalog.products
    assert first.catalog.variants == second.catalog.variants
    assert tuple(x.governed_knowledge_id for x in first.governed_knowledge) == tuple(
        x.governed_knowledge_id for x in second.governed_knowledge
    )
    assert first.knowledge_mappings == second.knowledge_mappings
    assert tuple(x.evidence_id for x in first.traceable_evidence_items) == tuple(
        x.evidence_id for x in second.traceable_evidence_items
    )
    assert tuple(
        x.governed_knowledge_id
        for x in first.product_constraint_governed_knowledge
    ) == tuple(
        x.governed_knowledge_id
        for x in second.product_constraint_governed_knowledge
    )
    assert (
        first.product_constraint_ingestion_manifest_records
        == second.product_constraint_ingestion_manifest_records
    )
    assert (
        first.product_constraint_knowledge_mappings
        == second.product_constraint_knowledge_mappings
    )


def test_provider_performs_no_database_or_frozen_artifact_write_and_preserves_all_six_sha256_values() -> None:
    before = _artifact_hashes(INTAKE_ROOT)
    evidence_db = (
        INTAKE_ROOT
        / "pilot-canonical-evidence-repository-v2-state"
        / "pilot-evidence-repository-v2.sqlite3"
    )
    governed_db = (
        INTAKE_ROOT
        / "pilot-governed-knowledge-repository-state"
        / "pilot-governed-knowledge-repository.sqlite3"
    )

    _load()

    after = _artifact_hashes(INTAKE_ROOT)
    assert after == before

    for database in (evidence_db, governed_db):
        uri = database.resolve().as_uri() + "?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
        try:
            assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        finally:
            connection.close()
