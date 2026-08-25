import hashlib
import json
from types import SimpleNamespace

import pytest

from rie.domain.governed_knowledge import GovernedKnowledge
from rie.evidence_materialization.evidence_materialization_contract import (
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
    TraceableEvidence,
)
from rie.rsv_knowledge.governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
)
from rie.rsv_knowledge.phase_b_prompt_input_bridge import (
    B1_BRIDGED_ASSET_SOURCE,
    B1_BRIDGED_ASSET_TYPE,
    B1_CONSTRAINT_RULE,
    B1_CONSTRAINT_TYPE,
    PhaseBPromptInputBridgeContractError,
    materialize_traceable_evidence_backed_product_variant_prompt_inputs,
)
from rie.rsv_knowledge.product_catalog import (
    ProductCatalog,
    ProductRecord,
    VariantRecord,
)


SOURCE_ID = "pilot-phase-a-product-variant-identity-atomic-knowledge-construction-result"


def catalog():
    return ProductCatalog(
        products=[ProductRecord("sv300", "SV300", "RSV", "active")],
        variants=[
            VariantRecord("sv300-white-glossy", "sv300", "White Glossy", "active"),
            VariantRecord("sv300-black-glossy", "sv300", "Black Glossy", "active"),
        ],
    )


def governed(governed_id, statement):
    value = object.__new__(GovernedKnowledge)
    object.__setattr__(value, "governed_knowledge_id", governed_id)
    object.__setattr__(value, "statement", statement)
    object.__setattr__(
        value,
        "support",
        (SimpleNamespace(source_id=SOURCE_ID),),
    )
    return value


def mapping(governed_id, variant_id):
    return GovernedKnowledgePromptInputMappingRecord(
        governed_knowledge_id=governed_id,
        knowledge_id=f"knowledge-{variant_id}-variant-identity",
        product_id="sv300",
        variant_id=variant_id,
        source_id=SOURCE_ID,
        source_asset_id="asset-" + ("a" * 64),
        knowledge_type="product_variant_identity",
        subject=variant_id,
        property="approved_variant_identity",
    )


def evidence(variant_id, evidence_suffix, source_paths=None):
    atomic_id = f"knowledge-{variant_id}-variant-identity"
    if source_paths is None:
        source_paths = [f"SV300/{variant_id}.jpg"]
    payload = {
        "knowledge_kind": "product_variant_identity",
        "atomic_knowledge_id": atomic_id,
        "product_id": "sv300",
        "variant_id": variant_id,
        "source_relative_paths": list(source_paths),
        "source_authority": "RSV_INTERNAL_APPROVED_SOURCE",
        "source_version": "2026-08-09",
    }
    content = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    value = object.__new__(TraceableEvidence)
    object.__setattr__(value, "evidence_id", f"evm1_{evidence_suffix * 64}"[:69])
    object.__setattr__(
        value,
        "content_type",
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
    )
    object.__setattr__(value, "content", content)
    object.__setattr__(value, "content_digest", digest)
    object.__setattr__(
        value,
        "provenance",
        SimpleNamespace(
            atomic_knowledge_id=atomic_id,
            source_relative_paths=tuple(source_paths),
        ),
    )
    return value


def test_bridge_materializes_exact_source_asset_and_constraint_authority():
    m = mapping("gk1-test-white", "sv300-white-glossy")
    e = evidence("sv300-white-glossy", "1")
    result = materialize_traceable_evidence_backed_product_variant_prompt_inputs(
        collection_id="evc1-test",
        catalog=catalog(),
        governed_knowledge=[governed("gk1-test-white", "variant white")],
        knowledge_mappings=[m],
        traceable_evidence_items=[e],
    )

    assert len(result.bridge_records) == 1
    assert len(result.ingestion_manifest_records) == 1
    assert len(result.bridged_knowledge_mappings) == 1
    assert len(result.constraint_specs) == 1
    assert result.prompt_inputs.materialization_status == "PASSED"
    assert len(result.prompt_inputs.knowledge_records) == 1
    assert len(result.prompt_inputs.asset_records) == 1
    assert len(result.prompt_inputs.constraint_records) == 1

    bridge = result.bridge_records[0]
    assert bridge.original_source_asset_id == m.source_asset_id
    assert bridge.bridged_source_asset_id == "asset-" + e.content_digest
    assert bridge.traceable_evidence_id == e.evidence_id

    manifest = result.ingestion_manifest_records[0]
    assert manifest.source_sha256 == e.content_digest
    assert manifest.asset_type == B1_BRIDGED_ASSET_TYPE
    assert manifest.source == B1_BRIDGED_ASSET_SOURCE
    assert "evc1-test" in manifest.source_path
    assert e.evidence_id in manifest.source_path

    spec = result.constraint_specs[0]
    assert spec.constraint_type == B1_CONSTRAINT_TYPE
    assert spec.rule == B1_CONSTRAINT_RULE
    assert spec.source_knowledge_id_or_asset_id == m.knowledge_id


def test_bridge_is_deterministic_for_reordered_inputs():
    mappings = [
        mapping("gk1-test-white", "sv300-white-glossy"),
        mapping("gk1-test-black", "sv300-black-glossy"),
    ]
    evidence_items = [
        evidence("sv300-white-glossy", "1"),
        evidence("sv300-black-glossy", "2"),
    ]
    governed_values = [
        governed("gk1-test-white", "variant white"),
        governed("gk1-test-black", "variant black"),
    ]
    first = materialize_traceable_evidence_backed_product_variant_prompt_inputs(
        collection_id="evc1-test",
        catalog=catalog(),
        governed_knowledge=governed_values,
        knowledge_mappings=mappings,
        traceable_evidence_items=evidence_items,
    )
    second = materialize_traceable_evidence_backed_product_variant_prompt_inputs(
        collection_id="evc1-test",
        catalog=catalog(),
        governed_knowledge=list(reversed(governed_values)),
        knowledge_mappings=list(reversed(mappings)),
        traceable_evidence_items=list(reversed(evidence_items)),
    )
    assert first == second


def test_bridge_fails_closed_on_zero_evidence_match():
    m = mapping("gk1-test-white", "sv300-white-glossy")
    with pytest.raises(
        PhaseBPromptInputBridgeContractError,
        match="zero TraceableEvidence matches",
    ):
        materialize_traceable_evidence_backed_product_variant_prompt_inputs(
            collection_id="evc1-test",
            catalog=catalog(),
            governed_knowledge=[governed("gk1-test-white", "variant white")],
            knowledge_mappings=[m],
            traceable_evidence_items=[
                evidence("sv300-black-glossy", "2"),
            ],
        )


def test_bridge_fails_closed_on_multiple_evidence_matches():
    m = mapping("gk1-test-white", "sv300-white-glossy")
    first = evidence("sv300-white-glossy", "1")
    second = evidence("sv300-white-glossy", "2")
    with pytest.raises(
        PhaseBPromptInputBridgeContractError,
        match="multiple TraceableEvidence matches",
    ):
        materialize_traceable_evidence_backed_product_variant_prompt_inputs(
            collection_id="evc1-test",
            catalog=catalog(),
            governed_knowledge=[governed("gk1-test-white", "variant white")],
            knowledge_mappings=[m],
            traceable_evidence_items=[first, second],
        )


def test_bridge_fails_closed_on_missing_source_lineage():
    m = mapping("gk1-test-white", "sv300-white-glossy")
    e = evidence("sv300-white-glossy", "1", source_paths=[])
    with pytest.raises(
        PhaseBPromptInputBridgeContractError,
        match="source_relative_paths must be a non-empty list",
    ):
        materialize_traceable_evidence_backed_product_variant_prompt_inputs(
            collection_id="evc1-test",
            catalog=catalog(),
            governed_knowledge=[governed("gk1-test-white", "variant white")],
            knowledge_mappings=[m],
            traceable_evidence_items=[e],
        )
