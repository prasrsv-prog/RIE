from dataclasses import replace

import pytest

from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    EvidenceEligibilitySnapshot,
    EvidenceMaterializationIssueCode,
    EvidenceMaterializationStatus,
)
from rie.evidence_materialization.evidence_materialization_service import (
    materialize_evidence_collection,
)
from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_CONTRACT_VERSION,
    EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION,
    ExtractionArtifact,
    ExtractionArtifactPageExtraction,
    ExtractionArtifactStructuralMetadata,
    ExtractionArtifactStructuralPage,
)
from rie.extraction.extraction_artifact_serializer import (
    ExtractionArtifactSerializer,
)


def _artifact(
    contents: tuple[str, ...] = ("Page one", "Page two"),
) -> ExtractionArtifact:
    source_path = "controlled/source.pdf"
    pages = tuple(
        ExtractionArtifactStructuralPage(
            page_index=index,
            width_points=612.0,
            height_points=792.0,
            rotation_degrees=0,
            inspection_status="inspected",
        )
        for index in range(len(contents))
    )
    metadata = ExtractionArtifactStructuralMetadata(
        allowed=True,
        reason="Controlled source is allowed.",
        fixture_id="fixture-1",
        source_label="Synthetic source",
        fixture_path=source_path,
        fixture_type="pdf",
        inspection_mode="bounded",
        inspection_status="inspected",
        encrypted=False,
        page_count=len(contents),
        inspected_page_count=len(contents),
        page_details_truncated=False,
        page_details=pages,
        max_inspected_pages=10,
        inspection_error="",
        evidence_allowed=False,
        notes="Gate 5 artifact.",
    )
    extractions = tuple(
        ExtractionArtifactPageExtraction(
            source_path=source_path,
            size_bytes=len(content.encode("utf-8")),
            page_number=index + 1,
            extraction_index=index,
            extraction_method="pypdf",
            content=content,
            warnings=("warning-b", "warning-a", "warning-b"),
        )
        for index, content in enumerate(contents)
    )
    provisional = ExtractionArtifact(
        contract_version=EXTRACTION_ARTIFACT_CONTRACT_VERSION,
        artifact_id="0" * 64,
        upstream_contract_version=(
            EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION
        ),
        upstream_status="completed",
        job_id="job-1",
        source_id="source-1",
        source_path=source_path,
        source_checksum="a" * 64,
        structural_metadata=metadata,
        page_extractions=extractions,
        execution_report_location="memory://report",
        cleanup_completed=True,
    )
    return replace(
        provisional,
        artifact_id=ExtractionArtifactSerializer.derive_artifact_id(
            provisional
        ),
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


def _unchecked_snapshot(**changes: object) -> EvidenceEligibilitySnapshot:
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
    value = object.__new__(EvidenceEligibilitySnapshot)
    for name, item in values.items():
        object.__setattr__(value, name, item)
    return value


def _issue_code(result) -> EvidenceMaterializationIssueCode:
    assert result.status is EvidenceMaterializationStatus.REJECTED
    assert result.collection is None
    assert result.issue is not None
    return result.issue.code


def test_materializes_one_evidence_per_page_in_order() -> None:
    result = materialize_evidence_collection(
        _artifact(("First", "Second")),
        _snapshot(),
    )
    assert result.status is EvidenceMaterializationStatus.MATERIALIZED
    assert result.issue is None
    assert result.collection is not None
    assert tuple(
        item.content for item in result.collection.evidence_items
    ) == ("First", "Second")
    assert tuple(
        item.provenance.page_index
        for item in result.collection.evidence_items
    ) == (0, 1)


def test_exact_content_empty_content_and_warnings_are_preserved() -> None:
    result = materialize_evidence_collection(
        _artifact(("  exact text  ", "")),
        _snapshot(),
    )
    assert result.collection is not None
    first, second = result.collection.evidence_items
    assert first.content == "  exact text  "
    assert second.content == ""
    assert first.warnings == (
        "warning-b",
        "warning-a",
        "warning-b",
    )


def test_provenance_traces_to_artifact_and_page() -> None:
    artifact = _artifact(("First",))
    result = materialize_evidence_collection(artifact, _snapshot())
    assert result.collection is not None
    provenance = result.collection.evidence_items[0].provenance
    assert provenance.artifact_contract_version == artifact.contract_version
    assert provenance.artifact_id == artifact.artifact_id
    assert provenance.upstream_contract_version == (
        artifact.upstream_contract_version
    )
    assert provenance.job_id == artifact.job_id
    assert provenance.source_id == artifact.source_id
    assert provenance.source_path == artifact.source_path
    assert provenance.source_checksum == artifact.source_checksum
    assert provenance.page_index == 0
    assert provenance.page_number == 1
    assert provenance.extraction_index == 0
    assert provenance.extraction_status == "completed"


def test_zero_page_artifact_materializes_empty_collection() -> None:
    result = materialize_evidence_collection(_artifact(()), _snapshot())
    assert result.status is EvidenceMaterializationStatus.MATERIALIZED
    assert result.collection is not None
    assert result.collection.evidence_items == ()


def test_repeated_materialization_is_deterministic() -> None:
    artifact = _artifact(("One", "Two"))
    snapshot = _snapshot()
    assert materialize_evidence_collection(
        artifact,
        snapshot,
    ) == materialize_evidence_collection(artifact, snapshot)


def test_artifact_is_not_mutated() -> None:
    artifact = _artifact(("One",))
    baseline = artifact
    materialize_evidence_collection(artifact, _snapshot())
    assert artifact == baseline


@pytest.mark.parametrize(
    "bad_artifact",
    (
        None,
        object(),
        "artifact",
    ),
)
def test_invalid_artifact_is_rejected(bad_artifact: object) -> None:
    result = materialize_evidence_collection(
        bad_artifact,
        _snapshot(),
    )
    assert _issue_code(result) is (
        EvidenceMaterializationIssueCode.INVALID_ARTIFACT
    )


def test_unchecked_invalid_artifact_is_rejected() -> None:
    artifact = object.__new__(ExtractionArtifact)
    result = materialize_evidence_collection(artifact, _snapshot())
    assert _issue_code(result) is (
        EvidenceMaterializationIssueCode.INVALID_ARTIFACT
    )


@pytest.mark.parametrize(
    "bad_snapshot",
    (
        None,
        object(),
        "snapshot",
    ),
)
def test_invalid_snapshot_type_is_rejected(
    bad_snapshot: object,
) -> None:
    result = materialize_evidence_collection(
        _artifact(("One",)),
        bad_snapshot,
    )
    assert _issue_code(result) is (
        EvidenceMaterializationIssueCode.INVALID_ELIGIBILITY_SNAPSHOT
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"source_id": ""},
        {"source_checksum": "not-sha"},
        {"requires_review": "false"},
        {"evidence_collection_allowed": 1},
    ),
)
def test_structurally_invalid_snapshot_is_rejected(
    changes: dict[str, object],
) -> None:
    result = materialize_evidence_collection(
        _artifact(("One",)),
        _unchecked_snapshot(**changes),
    )
    assert _issue_code(result) is (
        EvidenceMaterializationIssueCode.INVALID_ELIGIBILITY_SNAPSHOT
    )


@pytest.mark.parametrize(
    ("changes", "expected"),
    (
        (
            {"source_id": "other"},
            EvidenceMaterializationIssueCode.SOURCE_ID_MISMATCH,
        ),
        (
            {"source_path": "other.pdf"},
            EvidenceMaterializationIssueCode.SOURCE_PATH_MISMATCH,
        ),
        (
            {"source_checksum": "b" * 64},
            EvidenceMaterializationIssueCode.SOURCE_CHECKSUM_MISMATCH,
        ),
        (
            {"evidence_eligibility": "not_eligible"},
            EvidenceMaterializationIssueCode.SOURCE_NOT_ELIGIBLE,
        ),
        (
            {"evidence_collection_allowed": False},
            EvidenceMaterializationIssueCode.SOURCE_NOT_ELIGIBLE,
        ),
        (
            {"requires_review": True},
            EvidenceMaterializationIssueCode.SOURCE_REQUIRES_REVIEW,
        ),
        (
            {"contract_version": "other"},
            EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION,
        ),
    ),
)
def test_snapshot_rejection_uses_exact_issue(
    changes: dict[str, object],
    expected: EvidenceMaterializationIssueCode,
) -> None:
    result = materialize_evidence_collection(
        _artifact(("One",)),
        _unchecked_snapshot(**changes),
    )
    assert _issue_code(result) is expected


def test_rejection_precedence_uses_reviewed_issue_order() -> None:
    result = materialize_evidence_collection(
        _artifact(("One",)),
        _unchecked_snapshot(
            source_id="other",
            source_path="other.pdf",
            evidence_eligibility="not_eligible",
            requires_review=True,
        ),
    )
    assert _issue_code(result) is (
        EvidenceMaterializationIssueCode.SOURCE_ID_MISMATCH
    )


def test_not_eligible_precedes_requires_review() -> None:
    result = materialize_evidence_collection(
        _artifact(("One",)),
        _unchecked_snapshot(
            evidence_eligibility="not_eligible",
            evidence_collection_allowed=False,
            requires_review=True,
        ),
    )
    assert _issue_code(result) is (
        EvidenceMaterializationIssueCode.SOURCE_NOT_ELIGIBLE
    )


def test_rejected_result_contains_no_partial_evidence() -> None:
    artifact = _artifact(("One", "Two"))
    result = materialize_evidence_collection(
        artifact,
        _unchecked_snapshot(source_checksum="b" * 64),
    )
    assert result.status is EvidenceMaterializationStatus.REJECTED
    assert result.collection is None
    assert result.artifact_id == artifact.artifact_id
    assert result.source_id == artifact.source_id


def test_materialized_result_preserves_artifact_identity() -> None:
    artifact = _artifact(("One",))
    result = materialize_evidence_collection(artifact, _snapshot())
    assert result.artifact_id == artifact.artifact_id
    assert result.source_id == artifact.source_id
    assert result.collection is not None
    assert result.collection.artifact_id == artifact.artifact_id

# PR-086K-D34 OCR provenance propagation tests.
def test_d34_v2_artifact_propagates_ocr_provenance_to_gate6() -> None:
    from dataclasses import replace
    import rie.extraction.extraction_artifact_contract as gate5
    import rie.evidence_materialization.evidence_materialization_contract as gate6
    from rie.extraction.extraction_artifact_serializer import (
        ExtractionArtifactSerializer,
    )

    provenance = gate5.ExtractionArtifactOcrRemediationProvenance(
        producer_operation_id="PR_086K_D27_REAL_RSV_ASSET_PILOT_BOUNDED_PDF_IMAGE_TEXT_EXTRACTION_EXECUTION",
        producer_artifact_path="memory://ocr-index",
        producer_artifact_sha256="a" * 64,
        producer_artifact_set_digest="b" * 64,
        extraction_method="bounded_local_ocr",
    )
    base = _artifact(("D34 OCR text",))
    provisional = replace(
        base,
        contract_version=gate5.EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION,
        artifact_id="0" * 64,
        ocr_remediation_provenance=provenance,
    )
    artifact = replace(
        provisional,
        artifact_id=ExtractionArtifactSerializer.derive_artifact_id(
            provisional
        ),
    )

    result = materialize_evidence_collection(artifact, _snapshot())
    assert result.collection is not None
    assert result.collection.contract_version == (
        gate6.EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION
    )
    evidence = result.collection.evidence_items[0]
    assert evidence.contract_version == (
        gate6.TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION
    )
    assert evidence.ocr_remediation_provenance is not None
    assert evidence.ocr_remediation_provenance.producer_operation_id == (
        provenance.producer_operation_id
    )
    assert evidence.ocr_remediation_provenance.producer_artifact_sha256 == (
        provenance.producer_artifact_sha256
    )

    legacy = materialize_evidence_collection(_artifact(("Legacy",)), _snapshot())
    assert legacy.collection is not None
    assert legacy.collection.contract_version == (
        gate6.EVIDENCE_COLLECTION_CONTRACT_VERSION
    )
    assert legacy.collection.evidence_items[0].ocr_remediation_provenance is None
