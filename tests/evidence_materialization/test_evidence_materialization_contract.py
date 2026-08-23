from dataclasses import FrozenInstanceError, fields
from enum import Enum

import pytest

from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_CONTRACT_VERSION,
    EVIDENCE_COLLECTION_FIELD_ORDER,
    EVIDENCE_COLLECTION_IDENTITY_FIELD_ORDER,
    EVIDENCE_COLLECTION_IDENTITY_CANONICALIZATION_VERSION,
    EVIDENCE_COLLECTION_ID_PREFIX,
    EVIDENCE_ELIGIBILITY_FIELD_ORDER,
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CANONICALIZATION_VERSION,
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    EVIDENCE_MATERIALIZATION_ISSUE_FIELD_ORDER,
    EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION,
    EVIDENCE_MATERIALIZATION_RESULT_FIELD_ORDER,
    TRACEABLE_EVIDENCE_CONTENT_TYPE,
    TRACEABLE_EVIDENCE_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_FIELD_ORDER,
    TRACEABLE_EVIDENCE_IDENTITY_CANONICALIZATION_VERSION,
    TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER,
    TRACEABLE_EVIDENCE_ID_PREFIX,
    TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER,
    EvidenceEligibilitySnapshot,
    EvidenceMaterializationContractError,
    EvidenceMaterializationIssue,
    EvidenceMaterializationIssueCode,
    EvidenceMaterializationStatus,
    TraceableEvidenceProvenance,
    evidence_materialization_issue,
)


def _snapshot(**changes: object) -> EvidenceEligibilitySnapshot:
    values = {
        "contract_version":
            EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
        "source_id": "source-1",
        "source_path": "controlled/source.pdf",
        "source_checksum": "a" * 64,
        "source_type": "pdf",
        "document_classification": "official_knowledge_base",
        "authority_status": "official",
        "lifecycle_status": "active",
        "evidence_eligibility": "eligible",
        "evidence_collection_allowed": True,
        "requires_review": False,
        "reason": "Source is explicitly eligible.",
        "policy_id": "official-source-evidence-policy",
        "policy_version": "1.0.0",
        "registry_version": "registry-v1",
    }
    values.update(changes)
    return EvidenceEligibilitySnapshot(**values)


def _provenance(**changes: object) -> TraceableEvidenceProvenance:
    values = {
        "artifact_contract_version": "extraction_artifact_contract_v1",
        "artifact_id": "b" * 64,
        "upstream_contract_version":
            "pdf_ingestion_orchestrator_result_contract_v1",
        "job_id": "job-1",
        "source_id": "source-1",
        "source_path": "controlled/source.pdf",
        "source_checksum": "a" * 64,
        "page_index": 0,
        "page_number": 1,
        "extraction_index": 0,
        "extraction_method": "pypdf",
        "extraction_status": "completed",
        "execution_report_location": "memory://report",
    }
    values.update(changes)
    return TraceableEvidenceProvenance(**values)


def test_version_constants_are_exact() -> None:
    assert EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION == (
        "evidence_materialization_result_contract_v1"
    )
    assert EVIDENCE_COLLECTION_CONTRACT_VERSION == (
        "evidence_collection_contract_v1"
    )
    assert TRACEABLE_EVIDENCE_CONTRACT_VERSION == (
        "traceable_evidence_contract_v1"
    )
    assert EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION == (
        "evidence_eligibility_snapshot_contract_v1"
    )


def test_canonicalization_constants_and_prefixes_are_exact() -> None:
    assert EVIDENCE_ELIGIBILITY_SNAPSHOT_CANONICALIZATION_VERSION == (
        "evidence_eligibility_snapshot_json_v1"
    )
    assert TRACEABLE_EVIDENCE_IDENTITY_CANONICALIZATION_VERSION == (
        "traceable_evidence_identity_json_v1"
    )
    assert EVIDENCE_COLLECTION_IDENTITY_CANONICALIZATION_VERSION == (
        "evidence_collection_identity_json_v1"
    )
    assert TRACEABLE_EVIDENCE_CONTENT_TYPE == "page_text_utf8"
    assert TRACEABLE_EVIDENCE_ID_PREFIX == "evm1_"
    assert EVIDENCE_COLLECTION_ID_PREFIX == "evc1_"


def test_exact_field_order_constants() -> None:
    assert len(EVIDENCE_ELIGIBILITY_FIELD_ORDER) == 15
    assert len(TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER) == 13
    assert len(TRACEABLE_EVIDENCE_FIELD_ORDER) == 8
    assert len(TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER) == 7
    assert len(EVIDENCE_COLLECTION_FIELD_ORDER) == 11
    assert len(EVIDENCE_COLLECTION_IDENTITY_FIELD_ORDER) == 10
    assert EVIDENCE_MATERIALIZATION_ISSUE_FIELD_ORDER == (
        "code",
        "message",
    )
    assert len(EVIDENCE_MATERIALIZATION_RESULT_FIELD_ORDER) == 6


def test_status_values_are_exact() -> None:
    assert tuple(item.value for item in EvidenceMaterializationStatus) == (
        "materialized",
        "rejected",
    )


def test_issue_code_order_is_exact() -> None:
    assert tuple(
        item.value for item in EvidenceMaterializationIssueCode
    ) == (
        "invalid_artifact",
        "invalid_eligibility_snapshot",
        "source_id_mismatch",
        "source_path_mismatch",
        "source_checksum_mismatch",
        "source_not_eligible",
        "source_requires_review",
        "unsupported_version",
        "invalid_value",
        "evidence_id_mismatch",
        "collection_id_mismatch",
    )


def test_issue_values_are_frozen_and_messages_are_fixed() -> None:
    issue = evidence_materialization_issue(
        EvidenceMaterializationIssueCode.INVALID_ARTIFACT
    )
    assert issue.message == "extraction artifact is invalid."
    with pytest.raises(FrozenInstanceError):
        issue.message = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError, match="reviewed issue code"):
        EvidenceMaterializationIssue(
            code=EvidenceMaterializationIssueCode.INVALID_ARTIFACT,
            message="changed",
        )


def test_contract_error_is_immutable() -> None:
    issue = evidence_materialization_issue(
        EvidenceMaterializationIssueCode.INVALID_VALUE
    )
    error = EvidenceMaterializationContractError(issue)
    assert error.issue is issue
    with pytest.raises(AttributeError, match="immutable"):
        error.other = "value"  # type: ignore[attr-defined]


def test_eligibility_snapshot_is_frozen_and_has_exact_fields() -> None:
    snapshot = _snapshot()
    assert tuple(field.name for field in fields(snapshot)) == (
        EVIDENCE_ELIGIBILITY_FIELD_ORDER
    )
    with pytest.raises(FrozenInstanceError):
        snapshot.source_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("changes", "expected_code"),
    (
        (
            {"contract_version": "other"},
            EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION,
        ),
        (
            {"source_checksum": "A" * 64},
            EvidenceMaterializationIssueCode.INVALID_ELIGIBILITY_SNAPSHOT,
        ),
        (
            {"evidence_collection_allowed": False},
            EvidenceMaterializationIssueCode.SOURCE_NOT_ELIGIBLE,
        ),
        (
            {"evidence_eligibility": "not_eligible"},
            EvidenceMaterializationIssueCode.SOURCE_NOT_ELIGIBLE,
        ),
        (
            {"requires_review": True},
            EvidenceMaterializationIssueCode.SOURCE_REQUIRES_REVIEW,
        ),
    ),
)
def test_invalid_eligibility_snapshot_fails_with_exact_issue(
    changes: dict[str, object],
    expected_code: EvidenceMaterializationIssueCode,
) -> None:
    with pytest.raises(EvidenceMaterializationContractError) as raised:
        _snapshot(**changes)
    assert raised.value.issue.code is expected_code


def test_provenance_is_frozen_and_has_exact_fields() -> None:
    provenance = _provenance()
    assert tuple(field.name for field in fields(provenance)) == (
        TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER
    )
    with pytest.raises(FrozenInstanceError):
        provenance.job_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    "changes",
    (
        {"page_index": -1},
        {"page_number": 0},
        {"extraction_index": -1},
        {"page_index": 1, "extraction_index": 0},
        {"page_number": 2},
        {"extraction_status": "failed"},
        {"artifact_id": "not-sha"},
        {"source_checksum": "not-sha"},
    ),
)
def test_invalid_provenance_fails_closed(
    changes: dict[str, object],
) -> None:
    with pytest.raises(EvidenceMaterializationContractError) as raised:
        _provenance(**changes)
    assert (
        raised.value.issue.code
        is EvidenceMaterializationIssueCode.INVALID_VALUE
    )


def test_contract_classes_are_not_enums_except_reviewed_enums() -> None:
    assert issubclass(EvidenceMaterializationStatus, Enum)
    assert issubclass(EvidenceMaterializationIssueCode, Enum)
    assert not issubclass(EvidenceEligibilitySnapshot, Enum)

# PR-086K-D34 OCR provenance extension tests.
def test_d34_traceable_ocr_provenance_contract_is_exact_and_validated() -> None:
    from dataclasses import fields
    import pytest
    import rie.evidence_materialization.evidence_materialization_contract as contract

    value = contract.TraceableEvidenceOcrRemediationProvenance(
        producer_operation_id="PR_086K_D27_REAL_RSV_ASSET_PILOT_BOUNDED_PDF_IMAGE_TEXT_EXTRACTION_EXECUTION",
        producer_artifact_path="memory://ocr-index",
        producer_artifact_sha256="a" * 64,
        producer_artifact_set_digest="b" * 64,
        extraction_method="bounded_local_ocr",
    )
    assert tuple(field.name for field in fields(type(value))) == (
        "producer_operation_id",
        "producer_artifact_path",
        "producer_artifact_sha256",
        "producer_artifact_set_digest",
        "extraction_method",
    )
    assert contract.TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION == (
        "traceable_evidence_contract_v2"
    )
    assert contract.EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION == (
        "evidence_collection_contract_v2"
    )
    traceable_field_names = tuple(
        field.name for field in fields(contract.TraceableEvidence)
    )
    assert traceable_field_names == contract.TRACEABLE_EVIDENCE_FIELD_ORDER
    assert "ocr_remediation_provenance" not in traceable_field_names
    with pytest.raises(contract.EvidenceMaterializationContractError):
        contract.TraceableEvidenceOcrRemediationProvenance(
            producer_operation_id="producer",
            producer_artifact_path="artifact",
            producer_artifact_sha256="a" * 64,
            producer_artifact_set_digest="b" * 64,
            extraction_method="other",
        )

# PR-086EW structured-metadata v4 additive contract coverage.
def test_pr086ew_structured_metadata_v4_contract_is_additive() -> None:
    import dataclasses

    from rie.evidence_materialization.evidence_materialization_contract import (
        EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
        TRACEABLE_EVIDENCE_FIELD_ORDER,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION,
        TraceableEvidence,
        TraceableEvidenceStructuredMetadataProvenance,
    )

    assert TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION == "traceable_evidence_contract_v4"
    assert EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION == "evidence_collection_contract_v4"
    assert TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE == "product_variant_identity_structured_metadata"
    assert tuple(field.name for field in dataclasses.fields(TraceableEvidence)) == TRACEABLE_EVIDENCE_FIELD_ORDER

    provenance = TraceableEvidenceStructuredMetadataProvenance(
        contract_version=TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION,
        payload_type="product_variant_identity_structured_metadata",
        payload_schema_version="1.0.0",
        locator_type="atomic_knowledge_id",
        locator_value="atomic-1",
        locator_schema_version="1.0.0",
        atomic_knowledge_id="atomic-1",
        source_relative_paths=("official/a.jpg",),
        manifest_sha256="a" * 64,
        identity_capture_sha256="b" * 64,
        atomic_construction_authority_decision_packet_sha256="c" * 64,
        downstream_binding_policy_decision_packet_sha256="d" * 64,
        admission_payload_digest="e" * 64,
    )
    assert not hasattr(provenance, "page_index")
    assert not hasattr(provenance, "page_number")
    assert not hasattr(provenance, "extraction_index")
