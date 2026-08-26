import hashlib
import json
from types import SimpleNamespace

from rie.domain.governed_knowledge import GovernedKnowledge
from rie.evidence_materialization.evidence_materialization_contract import (
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
    TraceableEvidence,
)
from rie.rsv_knowledge.constraint_binding import bind_canonical_constraints
from rie.rsv_knowledge.governed_prompt_input_materialization import (
    GovernedKnowledgePromptInputMappingRecord,
)
from rie.rsv_knowledge.grounded_prompt_compiler import compile_grounded_prompt
from rie.rsv_knowledge.ingestion_manifest import IngestionManifestRecord
from rie.rsv_knowledge.phase_b_exact_six_active_constraint_bridge import (
    EXPECTED_PRODUCT_MANUAL_MAPPINGS,
    materialize_exact_six_active_product_constraints,
)
from rie.rsv_knowledge.phase_b_grounded_prompt_orchestration import (
    PhaseBGroundedPromptOrchestrationResult,
    orchestrate_exact18_grounded_prompt_request,
)
from rie.rsv_knowledge.phase_b_prompt_input_bridge import (
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
        products=[
            ProductRecord("ffs21", "FFS21", "RSV", "active"),
            ProductRecord("new-windtail", "New Windtail", "RSV", "active"),
            ProductRecord("sv300", "SV300", "RSV", "active"),
        ],
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


def evidence(variant_id, evidence_suffix):
    atomic_id = f"knowledge-{variant_id}-variant-identity"
    source_paths = [f"SV300/{variant_id}.jpg"]
    payload = {
        "knowledge_kind": "product_variant_identity",
        "atomic_knowledge_id": atomic_id,
        "product_id": "sv300",
        "variant_id": variant_id,
        "source_relative_paths": source_paths,
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


def fixture_values():
    mappings = [
        mapping("gk1-test-white", "sv300-white-glossy"),
        mapping("gk1-test-black", "sv300-black-glossy"),
    ]
    governed_values = [
        governed("gk1-test-white", "variant white"),
        governed("gk1-test-black", "variant black"),
    ]
    evidence_items = [
        evidence("sv300-white-glossy", "1"),
        evidence("sv300-black-glossy", "2"),
    ]
    return mappings, governed_values, evidence_items


def manual_governed(product_id):
    expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]
    value = object.__new__(GovernedKnowledge)
    object.__setattr__(
        value,
        "governed_knowledge_id",
        expected["governed_knowledge_id"],
    )
    object.__setattr__(value, "statement", f"synthetic manual for {product_id}")
    object.__setattr__(
        value,
        "support",
        (SimpleNamespace(source_id=expected["source_id"]),),
    )
    return value


def manual_mapping(product_id):
    expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]
    return GovernedKnowledgePromptInputMappingRecord(
        governed_knowledge_id=expected["governed_knowledge_id"],
        knowledge_id=expected["knowledge_id"],
        product_id=product_id,
        variant_id=None,
        source_id=expected["source_id"],
        source_asset_id=expected["source_asset_id"],
        knowledge_type=expected["knowledge_type"],
        subject=expected["subject"],
        property=expected["property"],
    )


def manual_manifest(product_id):
    expected = EXPECTED_PRODUCT_MANUAL_MAPPINGS[product_id]
    return IngestionManifestRecord(
        source_path=expected["source_path"],
        source_sha256=expected["source_sha256"],
        product_id=product_id,
        variant_id=None,
        knowledge_type="product_manual",
        asset_type="pdf",
        source=expected["source_id"],
        authority="RSV_INTERNAL_APPROVED_SOURCE",
        version="2026-08-09",
        status="active",
    )


def manual_fixture_values():
    product_ids = ("ffs21", "new-windtail", "sv300")
    return (
        [manual_governed(product_id) for product_id in product_ids],
        [manual_manifest(product_id) for product_id in product_ids],
        [manual_mapping(product_id) for product_id in product_ids],
    )


def orchestrated(*, creative_variables=None, variant_id="sv300-white-glossy"):
    mappings, governed_values, evidence_items = fixture_values()
    manual_governed_values, manual_manifests, manual_mappings = (
        manual_fixture_values()
    )
    return orchestrate_exact18_grounded_prompt_request(
        collection_id="evc1-test",
        catalog=catalog(),
        governed_knowledge=governed_values,
        knowledge_mappings=mappings,
        traceable_evidence_items=evidence_items,
        product_constraint_governed_knowledge=manual_governed_values,
        product_constraint_ingestion_manifest_records=manual_manifests,
        product_constraint_knowledge_mappings=manual_mappings,
        product_id="sv300",
        variant_id=variant_id,
        creative_variables=creative_variables
        if creative_variables is not None
        else {
            "background": "dark studio",
            "camera_angle": "front",
        },
        requested_output="grounded product prompt",
    )


def test_orchestration_returns_all_four_existing_audit_layers():
    result = orchestrated()
    assert isinstance(result, PhaseBGroundedPromptOrchestrationResult)
    assert result.bridge_result.prompt_inputs.materialization_status == "PASSED"
    assert (
        result.exact_six_bridge_result.prompt_inputs.materialization_status
        == "PASSED"
    )
    assert result.binding_result.binding_status == "PASSED"
    assert result.compile_result.grounding_status == "PASSED"
    assert result.compile_result.product_id == "sv300"
    assert result.compile_result.variant_id == "sv300-white-glossy"
    assert result.compile_result.used_knowledge_ids == (
        "knowledge-sv300-official-product-manual",
        "knowledge-sv300-white-glossy-variant-identity",
    )
    assert len(result.binding_result.bound_constraints) == 3


def test_orchestration_equals_the_existing_manual_composition():
    mappings, governed_values, evidence_items = fixture_values()
    manual_governed_values, manual_manifests, manual_mappings = (
        manual_fixture_values()
    )
    c = catalog()
    bridge = materialize_traceable_evidence_backed_product_variant_prompt_inputs(
        collection_id="evc1-test",
        catalog=c,
        governed_knowledge=governed_values,
        knowledge_mappings=mappings,
        traceable_evidence_items=evidence_items,
    )
    exact_six_bridge = materialize_exact_six_active_product_constraints(
        catalog=c,
        governed_knowledge=manual_governed_values,
        ingestion_manifest_records=manual_manifests,
        knowledge_mappings=manual_mappings,
    )

    knowledge_records = tuple(
        sorted(
            bridge.prompt_inputs.knowledge_records
            + exact_six_bridge.prompt_inputs.knowledge_records,
            key=lambda record: record.knowledge_id,
        )
    )
    asset_records = tuple(
        sorted(
            bridge.prompt_inputs.asset_records
            + exact_six_bridge.prompt_inputs.asset_records,
            key=lambda record: record.asset_id,
        )
    )
    constraint_records = tuple(
        sorted(
            bridge.prompt_inputs.constraint_records
            + exact_six_bridge.prompt_inputs.constraint_records,
            key=lambda record: record.constraint_id,
        )
    )

    binding = bind_canonical_constraints(
        catalog=c,
        product_id="sv300",
        variant_id="sv300-white-glossy",
        knowledge_records=knowledge_records,
        asset_records=asset_records,
        constraint_records=constraint_records,
    )
    compiled = compile_grounded_prompt(
        binding_result=binding,
        creative_variables={
            "background": "dark studio",
            "camera_angle": "front",
        },
        requested_output="grounded product prompt",
    )
    actual = orchestrate_exact18_grounded_prompt_request(
        collection_id="evc1-test",
        catalog=c,
        governed_knowledge=governed_values,
        knowledge_mappings=mappings,
        traceable_evidence_items=evidence_items,
        product_constraint_governed_knowledge=manual_governed_values,
        product_constraint_ingestion_manifest_records=manual_manifests,
        product_constraint_knowledge_mappings=manual_mappings,
        product_id="sv300",
        variant_id="sv300-white-glossy",
        creative_variables={
            "background": "dark studio",
            "camera_angle": "front",
        },
        requested_output="grounded product prompt",
    )
    assert actual.bridge_result == bridge
    assert actual.exact_six_bridge_result == exact_six_bridge
    assert actual.binding_result == binding
    assert actual.compile_result == compiled


def test_orchestration_is_deterministic_for_reordered_foundation_inputs():
    mappings, governed_values, evidence_items = fixture_values()
    manual_governed_values, manual_manifests, manual_mappings = (
        manual_fixture_values()
    )
    first = orchestrate_exact18_grounded_prompt_request(
        collection_id="evc1-test",
        catalog=catalog(),
        governed_knowledge=governed_values,
        knowledge_mappings=mappings,
        traceable_evidence_items=evidence_items,
        product_constraint_governed_knowledge=manual_governed_values,
        product_constraint_ingestion_manifest_records=manual_manifests,
        product_constraint_knowledge_mappings=manual_mappings,
        product_id="sv300",
        variant_id="sv300-white-glossy",
        creative_variables={
            "background": "dark studio",
            "camera_angle": "front",
        },
        requested_output="grounded product prompt",
    )
    second = orchestrate_exact18_grounded_prompt_request(
        collection_id="evc1-test",
        catalog=catalog(),
        governed_knowledge=list(reversed(governed_values)),
        knowledge_mappings=list(reversed(mappings)),
        traceable_evidence_items=list(reversed(evidence_items)),
        product_constraint_governed_knowledge=list(
            reversed(manual_governed_values)
        ),
        product_constraint_ingestion_manifest_records=list(
            reversed(manual_manifests)
        ),
        product_constraint_knowledge_mappings=list(
            reversed(manual_mappings)
        ),
        product_id="sv300",
        variant_id="sv300-white-glossy",
        creative_variables={
            "camera_angle": "front",
            "background": "dark studio",
        },
        requested_output="grounded product prompt",
    )
    assert second == first


def test_orchestration_preserves_existing_creative_override_fail_closed_behavior():
    result = orchestrated(
        creative_variables={
            "product_variant_identity": "change product identity",
        }
    )
    assert result.binding_result.binding_status == "PASSED"
    assert result.compile_result.grounding_status == "FAILED"
    assert result.compile_result.prompt_text == ""
    assert "creative_override:product_variant_identity" in result.compile_result.conflicts


def test_orchestration_scopes_identity_and_product_constraints_to_requested_variant():
    result = orchestrated(variant_id="sv300-black-glossy")
    assert result.binding_result.binding_status == "PASSED"
    assert result.compile_result.grounding_status == "PASSED"
    assert result.compile_result.variant_id == "sv300-black-glossy"
    assert result.compile_result.used_knowledge_ids == (
        "knowledge-sv300-black-glossy-variant-identity",
        "knowledge-sv300-official-product-manual",
    )
    assert tuple(
        record.constraint_id for record in result.binding_result.bound_constraints
    ) == (
        "constraint-sv300-chinstrap-retention-d-ring",
        "constraint-sv300-helmet-body-material-abs",
        "constraint-sv300-black-glossy-product-variant-identity",
    )
