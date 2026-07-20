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
