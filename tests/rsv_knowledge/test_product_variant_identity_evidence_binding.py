from __future__ import annotations

from datetime import datetime, timezone

import pytest

from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    EvidenceEligibilitySnapshot,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
    deserialize_evidence_collection_repository_payload,
    serialize_evidence_collection_repository_payload,
)
from rie.evidence_repository.evidence_repository_contract import (
    EVIDENCE_REPOSITORY_WRITE_REQUEST_V3_CONTRACT_VERSION,
)
from rie.rsv_knowledge.product_variant_identity_bridge import (
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION,
    ProductVariantIdentityEvidenceAdmissionRequest,
    ProductVariantIdentityEvidenceAdmissionUnit,
)
from rie.rsv_knowledge.product_variant_identity_evidence_binding import (
    PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256,
    PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SOURCE_ID,
    PILOT_PRODUCT_VARIANT_IDENTITY_AUTHORITY_STATUS,
    PILOT_PRODUCT_VARIANT_IDENTITY_DOCUMENT_CLASSIFICATION,
    PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_ID,
    PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_VERSION,
    PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REASON,
    PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REGISTRY_VERSION,
    PILOT_PRODUCT_VARIANT_IDENTITY_LIFECYCLE_STATUS,
    PILOT_PRODUCT_VARIANT_IDENTITY_SOURCE_TYPE,
    PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_REQUEST_CONTRACT_VERSION,
    ProductVariantIdentityStructuredMetadataEvidenceBindingRequest,
    materialize_product_variant_identity_structured_metadata_evidence_binding,
)


def _requests() -> tuple[ProductVariantIdentityEvidenceAdmissionRequest, ...]:
    values = []
    for index in range(18):
        path_count = 7 if index == 0 else 6
        paths = tuple(
            f"official/variant-{index:02d}/asset-{path_index:02d}.jpg"
            for path_index in range(path_count)
        )
        unit = ProductVariantIdentityEvidenceAdmissionUnit(
            atomic_knowledge_id=f"atomic-variant-{index:02d}",
            knowledge_kind="product_variant_identity",
            atomic_statement=f"Variant {index:02d} is an approved product variant.",
            product_family="pilot-family",
            product_id=f"pilot-product-{index:02d}",
            variant_id=f"pilot-variant-{index:02d}",
            variant_name_verbatim=f"Pilot Variant {index:02d}",
            source_type="official_asset",
            source_authority="official",
            source_status="locked",
            source_version="1",
            source_relative_paths=paths,
            manifest_sha256="a" * 64,
            identity_capture_sha256="b" * 64,
            atomic_construction_authority_decision_packet_sha256="c" * 64,
            downstream_binding_policy_decision_packet_sha256="d" * 64,
        )
        values.append(
            ProductVariantIdentityEvidenceAdmissionRequest(
                contract_version=(
                    PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION
                ),
                unit=unit,
            )
        )
    return tuple(values)


def _snapshot() -> EvidenceEligibilitySnapshot:
    return EvidenceEligibilitySnapshot(
        contract_version=EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
        source_id=PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SOURCE_ID,
        source_path="pilot-phase-a-product-variant-identity-atomic-knowledge-construction-result.json",
        source_checksum=PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256,
        source_type=PILOT_PRODUCT_VARIANT_IDENTITY_SOURCE_TYPE,
        document_classification=PILOT_PRODUCT_VARIANT_IDENTITY_DOCUMENT_CLASSIFICATION,
        authority_status=PILOT_PRODUCT_VARIANT_IDENTITY_AUTHORITY_STATUS,
        lifecycle_status=PILOT_PRODUCT_VARIANT_IDENTITY_LIFECYCLE_STATUS,
        evidence_eligibility="eligible",
        evidence_collection_allowed=True,
        requires_review=False,
        reason=PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REASON,
        policy_id=PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_ID,
        policy_version=PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_VERSION,
        registry_version=PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REGISTRY_VERSION,
    )


def _binding_request(
    admission_requests: tuple[ProductVariantIdentityEvidenceAdmissionRequest, ...] | None = None,
) -> ProductVariantIdentityStructuredMetadataEvidenceBindingRequest:
    return ProductVariantIdentityStructuredMetadataEvidenceBindingRequest(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_REQUEST_CONTRACT_VERSION
        ),
        admission_requests=admission_requests or _requests(),
        eligibility_snapshot=_snapshot(),
        artifact_contract_version="product_variant_identity_atomic_result_v1",
        artifact_id=PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256,
        upstream_contract_version="product_variant_identity_atomic_construction_v1",
        job_id="pr086ew-test",
        actor_id="rcis-rsv-real-asset-pilot-primary-operator",
        recorded_at_utc=datetime(2026, 8, 22, 14, 0, tzinfo=timezone.utc),
    )


def test_pr086ew_exact18_109_binding_is_deterministic_and_repository_roundtrips() -> None:
    first = materialize_product_variant_identity_structured_metadata_evidence_binding(
        _binding_request()
    )
    second = materialize_product_variant_identity_structured_metadata_evidence_binding(
        _binding_request()
    )
    assert first.collection == second.collection
    assert len(first.evidence_items) == 18
    assert len({item.evidence_id for item in first.evidence_items}) == 18
    assert sum(len(item.provenance.source_relative_paths) for item in first.evidence_items) == 109
    assert all(not hasattr(item.provenance, "page_index") for item in first.evidence_items)
    assert (
        first.write_request.contract_version
        == EVIDENCE_REPOSITORY_WRITE_REQUEST_V3_CONTRACT_VERSION
    )
    assert (
        first.write_request.expected_collection_payload_digest
        == calculate_evidence_collection_repository_payload_digest(first.collection)
    )

    payload = serialize_evidence_collection_repository_payload(first.collection)
    assert b'"page_index"' not in payload
    restored = deserialize_evidence_collection_repository_payload(payload)
    assert restored == first.collection
    assert serialize_evidence_collection_repository_payload(restored) == payload


def test_pr086ew_binding_rejects_non_exact18_scope() -> None:
    with pytest.raises(ValueError):
        _binding_request(_requests()[:-1])
