from dataclasses import replace
from datetime import datetime, timezone
import ast
import hashlib
from pathlib import Path

import pytest

from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceLocator,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.knowledge_candidate import (
    PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE,
)
from rie.rsv_knowledge.product_variant_identity_bridge import (
    BRIDGE_STATUS_CONSTRUCTED,
    BRIDGE_STATUS_MATERIALIZED,
    BRIDGE_STATUS_REJECTED,
    BRIDGE_STATUS_SAFE_STOP,
    PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION,
    PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_ID,
    PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE,
    ProductVariantIdentityCandidateConstructionRequest,
    ProductVariantIdentityEvidenceAdmissionRequest,
    ProductVariantIdentityEvidenceAdmissionUnit,
    construct_product_variant_identity_candidate_from_real_accepted_evidence,
    materialize_product_variant_identity_evidence_admission,
)

FIXED = datetime(2026, 8, 22, 10, 0, 0, tzinfo=timezone.utc)


def _unit(**changes):
    values = dict(
        atomic_knowledge_id="knowledge-sv300-black-glossy-variant-identity",
        knowledge_kind="product_variant_identity",
        atomic_statement=(
            "variant_id=sv300-black-glossy; product_id=sv300; "
            "variant_name=Black Glossy"
        ),
        product_family="SV300",
        product_id="sv300",
        variant_id="sv300-black-glossy",
        variant_name_verbatim="Black Glossy",
        source_type="APPROVED_PRODUCT_PHOTO",
        source_authority="RSV_INTERNAL_APPROVED_SOURCE",
        source_status="APPROVED",
        source_version="2026-08-09",
        source_relative_paths=(
            "SV300/Black Glossy/01.jpg",
            "SV300/Black Glossy/02.jpg",
        ),
        manifest_sha256="a" * 64,
        identity_capture_sha256="b" * 64,
        atomic_construction_authority_decision_packet_sha256="c" * 64,
        downstream_binding_policy_decision_packet_sha256="d" * 64,
    )
    values.update(changes)
    return ProductVariantIdentityEvidenceAdmissionUnit(**values)


def _admission(unit=None, **request_changes):
    unit = unit or _unit()
    values = dict(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION
        ),
        unit=unit,
    )
    values.update(request_changes)
    return materialize_product_variant_identity_evidence_admission(
        ProductVariantIdentityEvidenceAdmissionRequest(**values)
    )


def _accepted_and_record(unit=None):
    unit = unit or _unit()
    admission = _admission(unit)
    assert admission.status == BRIDGE_STATUS_MATERIALIZED
    payload_digest = hashlib.sha256(repr(admission.payload).encode("utf-8")).hexdigest()
    evidence_id = "ev1_" + "1" * 64
    acceptance_id = "ar1_" + "2" * 64
    review_id = "review-record-variant-identity"
    source_id = "rsv-variant-identity-source"
    source_digest = "3" * 64
    candidate_digest = "4" * 64

    accepted = AcceptedEvidence(
        evidence_id=evidence_id,
        contract_version="accepted-evidence-v1",
        candidate_reference=EvidenceCandidateReference(
            candidate_contract_version="test-candidate-contract-v1",
            candidate_snapshot_digest=candidate_digest,
            candidate_source_id=source_id,
            candidate_producer_name="test-structured-metadata-producer",
            candidate_producer_version="1.0.0",
            candidate_payload_digest=payload_digest,
        ),
        source_snapshot=EvidenceSourceSnapshot(
            source_id=source_id,
            source_path="approved/variant-identity-metadata.json",
            source_type="structured_metadata",
            document_classification="approved_variant_identity_metadata",
            authority_status="official",
            lifecycle_status="active",
            evidence_eligibility="eligible",
            source_content_digest=source_digest,
        ),
        producer_snapshot=EvidenceProducerSnapshot(
            producer_name="test-structured-metadata-producer",
            producer_version="1.0.0",
            producer_kind="structured_metadata_materializer",
            producer_contract_version="1.0.0",
        ),
        factual_payload=EvidencePayload(
            payload_type=PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE,
            payload_schema_version=(
                PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION
            ),
            payload=admission.payload,
            payload_digest=payload_digest,
            locator=EvidenceLocator(
                locator_type=PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE,
                locator_value=unit.atomic_knowledge_id,
                locator_schema_version=(
                    PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION
                ),
            ),
        ),
        provenance=EvidenceProvenance(
            collection_id="test-variant-identity-collection",
            producer_output_digest="5" * 64,
            lineage=("persisted-structured-metadata-evidence",),
            observed_at=FIXED,
            source_registry_version="test-registry-v1",
        ),
        eligibility_result=AcceptedEligibilityResult(
            decision="eligible",
            policy_id="test-eligibility-policy",
            policy_version="1.0.0",
            candidate_snapshot_digest=candidate_digest,
            source_id=source_id,
            reason_codes=("approved_test_evidence",),
            evaluated_at=FIXED,
            evaluated_by="test-operator",
            diagnostics=(),
        ),
        materialization_record=EvidenceMaterializationRecord(
            materializer_id="test-accepted-evidence-materializer",
            materializer_version="1.0.0",
            materialized_at=FIXED,
            acceptance_record_id=acceptance_id,
            accepted_by="test-operator",
            acceptance_reason="explicit-test-approval",
            review_record_id=review_id,
            identity_policy_id="test-evidence-identity-policy",
            identity_policy_version="1.0.0",
        ),
        diagnostics=(),
    )
    record = AcceptanceRecord(
        acceptance_record_id=acceptance_id,
        contract_version="acceptance-record-v1",
        evidence_id=evidence_id,
        accepted_by="test-operator",
        acceptance_reason="explicit-test-approval",
        review_record_id=review_id,
        accepted_at=FIXED,
        acceptance_policy_id="test-acceptance-policy",
        acceptance_policy_version="1.0.0",
        evidence_identity_policy_id="test-evidence-identity-policy",
        evidence_identity_policy_version="1.0.0",
        materializer_id="test-accepted-evidence-materializer",
        materializer_version="1.0.0",
        diagnostics=(),
    )
    return accepted, record


def _candidate_request(unit=None, **changes):
    unit = unit or _unit()
    accepted, record = _accepted_and_record(unit)
    values = dict(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
        ),
        unit=unit,
        accepted_evidence=accepted,
        acceptance_records=(record,),
        construction_rule_id=PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_ID,
        construction_rule_version=(
            PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_VERSION
        ),
    )
    values.update(changes)
    return ProductVariantIdentityCandidateConstructionRequest(**values)


def test_product_variant_identity_statement_type_is_exact() -> None:
    assert PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE == "product_variant_identity"


def test_admission_materializes_only_structured_metadata_payload() -> None:
    unit = _unit()
    result = _admission(unit)
    assert result.status == BRIDGE_STATUS_MATERIALIZED
    assert result.reason_codes == ()
    assert result.locator_value == unit.atomic_knowledge_id
    assert dict(result.payload)["atomic_statement"] == unit.atomic_statement
    assert dict(result.payload)["source_relative_paths"] == unit.source_relative_paths


def test_admission_payload_keys_are_lexicographically_ordered() -> None:
    result = _admission()
    keys = tuple(key for key, _ in result.payload)
    assert keys == tuple(sorted(keys))


def test_admission_safe_stops_prohibited_operations() -> None:
    for field_name in (
        "image_content_interpretation_attempted",
        "additional_semantic_inference_attempted",
        "repository_write_attempted",
        "network_operation_attempted",
    ):
        result = _admission(**{field_name: True})
        assert result.status == BRIDGE_STATUS_SAFE_STOP
        assert result.reason_codes == ("prohibited_operation_attempted",)


def test_candidate_constructs_from_exact_accepted_evidence_and_lineage() -> None:
    unit = _unit()
    result = construct_product_variant_identity_candidate_from_real_accepted_evidence(
        _candidate_request(unit)
    )
    assert result.status == BRIDGE_STATUS_CONSTRUCTED
    assert result.reason_codes == ()
    candidate = result.knowledge_candidate
    assert candidate.statement_type == PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE
    assert candidate.statement == unit.atomic_statement
    assert candidate.construction_rule_id == PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_ID
    assert candidate.construction_rule_version == PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_VERSION
    assert len(candidate.support) == 1
    assert candidate.support[0].acceptance_record_ids == ("ar1_" + "2" * 64,)
    assert candidate.support[0].acceptance_review_record_ids == (
        "review-record-variant-identity",
    )


def test_candidate_rejects_wrong_rule_without_fallback() -> None:
    result = construct_product_variant_identity_candidate_from_real_accepted_evidence(
        _candidate_request(construction_rule_id="other")
    )
    assert result.status == BRIDGE_STATUS_REJECTED
    assert result.reason_codes == ("unsupported_construction_rule",)


def test_candidate_rejects_acceptance_evidence_mismatch() -> None:
    request = _candidate_request()
    record = request.acceptance_records[0]
    mismatched = replace(record, evidence_id="ev1_" + "9" * 64)
    result = construct_product_variant_identity_candidate_from_real_accepted_evidence(
        replace(request, acceptance_records=(mismatched,))
    )
    assert result.status == BRIDGE_STATUS_REJECTED
    assert result.reason_codes == ("acceptance_record_evidence_id_mismatch",)


def test_candidate_rejects_payload_tamper() -> None:
    request = _candidate_request()
    payload = request.accepted_evidence.factual_payload
    tampered_payload = replace(
        payload,
        payload=(("atomic_statement", "tampered"),),
    )
    tampered_evidence = replace(
        request.accepted_evidence,
        factual_payload=tampered_payload,
    )
    result = construct_product_variant_identity_candidate_from_real_accepted_evidence(
        replace(request, accepted_evidence=tampered_evidence)
    )
    assert result.status == BRIDGE_STATUS_REJECTED
    assert result.reason_codes == ("variant_identity_payload_mismatch",)


def test_candidate_safe_stops_prohibited_operations() -> None:
    for field_name in (
        "image_content_interpretation_attempted",
        "additional_semantic_inference_attempted",
        "repository_write_attempted",
        "network_operation_attempted",
    ):
        result = construct_product_variant_identity_candidate_from_real_accepted_evidence(
            _candidate_request(**{field_name: True})
        )
        assert result.status == BRIDGE_STATUS_SAFE_STOP
        assert result.reason_codes == ("prohibited_operation_attempted",)


def test_bridge_rejects_duck_typed_requests() -> None:
    with pytest.raises(ValueError, match="exact ProductVariantIdentityEvidenceAdmissionRequest"):
        materialize_product_variant_identity_evidence_admission(object())
    with pytest.raises(ValueError, match="exact ProductVariantIdentityCandidateConstructionRequest"):
        construct_product_variant_identity_candidate_from_real_accepted_evidence(object())


def test_bridge_module_has_no_repository_network_or_image_imports() -> None:
    import rie.rsv_knowledge.product_variant_identity_bridge as module

    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    forbidden = (
        "sqlite3",
        "requests",
        "urllib",
        "http",
        "socket",
        "openai",
        "PIL",
        "cv2",
        "rie.evidence_repository",
        "rie.knowledge_repository",
    )
    assert not any(
        item == prefix or item.startswith(prefix + ".")
        for item in imported
        for prefix in forbidden
    )
