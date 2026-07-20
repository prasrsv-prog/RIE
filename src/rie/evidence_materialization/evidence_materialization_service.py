"""Pure Gate 6 Evidence Materialization service."""

from __future__ import annotations

import hashlib

from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_CONTRACT_VERSION,
    ExtractionArtifact,
)

from .evidence_materialization_canonicalization import (
    derive_evidence_collection_id,
    derive_evidence_eligibility_snapshot_digest,
    derive_traceable_evidence_id,
)
from .evidence_materialization_contract import (
    EVIDENCE_COLLECTION_CONTRACT_VERSION,
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_CONTENT_TYPE,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    EvidenceMaterializationContractError,
    EvidenceMaterializationIssueCode,
    EvidenceMaterializationResult,
    EvidenceMaterializationStatus,
    TraceableEvidence,
    TraceableEvidenceProvenance,
    evidence_materialization_issue,
)


def _rejected(
    code: EvidenceMaterializationIssueCode,
    artifact_id: str = "",
    source_id: str = "",
) -> EvidenceMaterializationResult:
    return EvidenceMaterializationResult(
        contract_version=EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION,
        status=EvidenceMaterializationStatus.REJECTED,
        artifact_id=artifact_id,
        source_id=source_id,
        collection=None,
        issue=evidence_materialization_issue(code),
    )


def _artifact_is_valid(value: object) -> bool:
    if type(value) is not ExtractionArtifact:
        return False
    try:
        value.__post_init__()
    except Exception:
        return False
    return (
        value.contract_version == EXTRACTION_ARTIFACT_CONTRACT_VERSION
        and value.upstream_status == "completed"
        and value.cleanup_completed is True
    )


def _valid_string(value: object) -> bool:
    return type(value) is str and value.strip() != ""


def _valid_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _eligibility_structurally_valid(
    value: EvidenceEligibilitySnapshot,
) -> bool:
    for field_name in (
        "source_id",
        "source_path",
        "source_type",
        "document_classification",
        "authority_status",
        "lifecycle_status",
        "evidence_eligibility",
        "reason",
        "policy_id",
        "policy_version",
        "registry_version",
    ):
        if not _valid_string(getattr(value, field_name, None)):
            return False
    return (
        _valid_sha256(getattr(value, "source_checksum", None))
        and type(getattr(value, "evidence_collection_allowed", None))
        is bool
        and type(getattr(value, "requires_review", None)) is bool
    )


def _snapshot_issue(
    artifact: ExtractionArtifact,
    snapshot: object,
) -> EvidenceMaterializationIssueCode | None:
    if (
        type(snapshot) is not EvidenceEligibilitySnapshot
        or not _eligibility_structurally_valid(snapshot)
    ):
        return (
            EvidenceMaterializationIssueCode
            .INVALID_ELIGIBILITY_SNAPSHOT
        )
    if snapshot.source_id != artifact.source_id:
        return EvidenceMaterializationIssueCode.SOURCE_ID_MISMATCH
    if snapshot.source_path != artifact.source_path:
        return EvidenceMaterializationIssueCode.SOURCE_PATH_MISMATCH
    if snapshot.source_checksum != artifact.source_checksum:
        return EvidenceMaterializationIssueCode.SOURCE_CHECKSUM_MISMATCH
    if (
        snapshot.evidence_eligibility != "eligible"
        or snapshot.evidence_collection_allowed is not True
    ):
        return EvidenceMaterializationIssueCode.SOURCE_NOT_ELIGIBLE
    if snapshot.requires_review is True:
        return EvidenceMaterializationIssueCode.SOURCE_REQUIRES_REVIEW
    if (
        snapshot.contract_version
        != EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION
    ):
        return EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION
    return None


def _unchecked_traceable_evidence(
    *,
    content: str,
    content_digest: str,
    warnings: tuple[str, ...],
    provenance: TraceableEvidenceProvenance,
    eligibility_snapshot_digest: str,
) -> TraceableEvidence:
    value = object.__new__(TraceableEvidence)
    object.__setattr__(
        value,
        "contract_version",
        TRACEABLE_EVIDENCE_CONTRACT_VERSION,
    )
    object.__setattr__(value, "evidence_id", "")
    object.__setattr__(
        value,
        "content_type",
        TRACEABLE_EVIDENCE_CONTENT_TYPE,
    )
    object.__setattr__(value, "content", content)
    object.__setattr__(value, "content_digest", content_digest)
    object.__setattr__(value, "warnings", warnings)
    object.__setattr__(value, "provenance", provenance)
    object.__setattr__(
        value,
        "eligibility_snapshot_digest",
        eligibility_snapshot_digest,
    )
    return value


def _unchecked_collection(
    *,
    artifact: ExtractionArtifact,
    eligibility_snapshot: EvidenceEligibilitySnapshot,
    evidence_items: tuple[TraceableEvidence, ...],
) -> EvidenceCollection:
    value = object.__new__(EvidenceCollection)
    object.__setattr__(
        value,
        "contract_version",
        EVIDENCE_COLLECTION_CONTRACT_VERSION,
    )
    object.__setattr__(value, "collection_id", "")
    object.__setattr__(
        value,
        "artifact_contract_version",
        artifact.contract_version,
    )
    object.__setattr__(value, "artifact_id", artifact.artifact_id)
    object.__setattr__(
        value,
        "upstream_contract_version",
        artifact.upstream_contract_version,
    )
    object.__setattr__(value, "job_id", artifact.job_id)
    object.__setattr__(value, "source_id", artifact.source_id)
    object.__setattr__(value, "source_path", artifact.source_path)
    object.__setattr__(
        value,
        "source_checksum",
        artifact.source_checksum,
    )
    object.__setattr__(
        value,
        "eligibility_snapshot",
        eligibility_snapshot,
    )
    object.__setattr__(value, "evidence_items", evidence_items)
    return value


def _materialized_collection(
    artifact: ExtractionArtifact,
    snapshot: EvidenceEligibilitySnapshot,
) -> EvidenceCollection:
    eligibility_digest = (
        derive_evidence_eligibility_snapshot_digest(snapshot)
    )
    items: list[TraceableEvidence] = []

    for extraction in artifact.page_extractions:
        provenance = TraceableEvidenceProvenance(
            artifact_contract_version=artifact.contract_version,
            artifact_id=artifact.artifact_id,
            upstream_contract_version=artifact.upstream_contract_version,
            job_id=artifact.job_id,
            source_id=artifact.source_id,
            source_path=artifact.source_path,
            source_checksum=artifact.source_checksum,
            page_index=extraction.extraction_index,
            page_number=extraction.page_number,
            extraction_index=extraction.extraction_index,
            extraction_method=extraction.extraction_method,
            extraction_status=artifact.upstream_status,
            execution_report_location=(
                artifact.execution_report_location
            ),
        )
        content_digest = hashlib.sha256(
            extraction.content.encode("utf-8")
        ).hexdigest()
        provisional = _unchecked_traceable_evidence(
            content=extraction.content,
            content_digest=content_digest,
            warnings=tuple(extraction.warnings),
            provenance=provenance,
            eligibility_snapshot_digest=eligibility_digest,
        )
        evidence_id = derive_traceable_evidence_id(provisional)
        items.append(
            TraceableEvidence(
                contract_version=TRACEABLE_EVIDENCE_CONTRACT_VERSION,
                evidence_id=evidence_id,
                content_type=TRACEABLE_EVIDENCE_CONTENT_TYPE,
                content=extraction.content,
                content_digest=content_digest,
                warnings=tuple(extraction.warnings),
                provenance=provenance,
                eligibility_snapshot_digest=eligibility_digest,
            )
        )

    evidence_items = tuple(items)
    provisional_collection = _unchecked_collection(
        artifact=artifact,
        eligibility_snapshot=snapshot,
        evidence_items=evidence_items,
    )
    collection_id = derive_evidence_collection_id(
        provisional_collection
    )
    return EvidenceCollection(
        contract_version=EVIDENCE_COLLECTION_CONTRACT_VERSION,
        collection_id=collection_id,
        artifact_contract_version=artifact.contract_version,
        artifact_id=artifact.artifact_id,
        upstream_contract_version=artifact.upstream_contract_version,
        job_id=artifact.job_id,
        source_id=artifact.source_id,
        source_path=artifact.source_path,
        source_checksum=artifact.source_checksum,
        eligibility_snapshot=snapshot,
        evidence_items=evidence_items,
    )


def materialize_evidence_collection(
    artifact: object,
    eligibility_snapshot: object,
) -> EvidenceMaterializationResult:
    if not _artifact_is_valid(artifact):
        return _rejected(
            EvidenceMaterializationIssueCode.INVALID_ARTIFACT
        )

    artifact_id = artifact.artifact_id
    source_id = artifact.source_id

    issue_code = _snapshot_issue(
        artifact,
        eligibility_snapshot,
    )
    if issue_code is not None:
        return _rejected(issue_code, artifact_id, source_id)

    try:
        collection = _materialized_collection(
            artifact,
            eligibility_snapshot,
        )
    except EvidenceMaterializationContractError as error:
        return _rejected(error.issue.code, artifact_id, source_id)
    except (TypeError, ValueError, UnicodeError):
        return _rejected(
            EvidenceMaterializationIssueCode.INVALID_VALUE,
            artifact_id,
            source_id,
        )

    return EvidenceMaterializationResult(
        contract_version=EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION,
        status=EvidenceMaterializationStatus.MATERIALIZED,
        artifact_id=artifact_id,
        source_id=source_id,
        collection=collection,
        issue=None,
    )


__all__ = ("materialize_evidence_collection",)
