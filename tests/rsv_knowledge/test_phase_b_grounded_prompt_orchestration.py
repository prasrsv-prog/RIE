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


def orchestrated(*, creative_variables=None, variant_id="sv300-white-glossy"):
    mappings, governed_values, evidence_items = fixture_values()
    return orchestrate_exact18_grounded_prompt_request(
        collection_id="evc1-test",
        catalog=catalog(),
        governed_knowledge=governed_values,
        knowledge_mappings=mappings,
        traceable_evidence_items=evidence_items,
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


def test_orchestration_returns_all_three_existing_audit_layers():
    result = orchestrated()
    assert isinstance(result, PhaseBGroundedPromptOrchestrationResult)
    assert result.bridge_result.prompt_inputs.materialization_status == "PASSED"
    assert result.binding_result.binding_status == "PASSED"
    assert result.compile_result.grounding_status == "PASSED"
    assert result.compile_result.product_id == "sv300"
    assert result.compile_result.variant_id == "sv300-white-glossy"
    assert result.compile_result.used_knowledge_ids == (
        "knowledge-sv300-white-glossy-variant-identity",
    )


def test_orchestration_equals_the_existing_manual_composition():
    mappings, governed_values, evidence_items = fixture_values()
    c = catalog()
    bridge = materialize_traceable_evidence_backed_product_variant_prompt_inputs(
        collection_id="evc1-test",
        catalog=c,
        governed_knowledge=governed_values,
        knowledge_mappings=mappings,
        traceable_evidence_items=evidence_items,
    )
    binding = bind_canonical_constraints(
        catalog=c,
        product_id="sv300",
        variant_id="sv300-white-glossy",
        knowledge_records=bridge.prompt_inputs.knowledge_records,
        asset_records=bridge.prompt_inputs.asset_records,
        constraint_records=bridge.prompt_inputs.constraint_records,
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
        product_id="sv300",
        variant_id="sv300-white-glossy",
        creative_variables={
            "background": "dark studio",
            "camera_angle": "front",
        },
        requested_output="grounded product prompt",
    )
    assert actual.bridge_result == bridge
    assert actual.binding_result == binding
    assert actual.compile_result == compiled


def test_orchestration_is_deterministic_for_reordered_foundation_inputs():
    mappings, governed_values, evidence_items = fixture_values()
    first = orchestrate_exact18_grounded_prompt_request(
        collection_id="evc1-test",
        catalog=catalog(),
        governed_knowledge=governed_values,
        knowledge_mappings=mappings,
        traceable_evidence_items=evidence_items,
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


def test_orchestration_scopes_binding_to_the_requested_variant():
    result = orchestrated(variant_id="sv300-black-glossy")
    assert result.binding_result.binding_status == "PASSED"
    assert result.compile_result.grounding_status == "PASSED"
    assert result.compile_result.variant_id == "sv300-black-glossy"
    assert result.compile_result.used_knowledge_ids == (
        "knowledge-sv300-black-glossy-variant-identity",
    )
