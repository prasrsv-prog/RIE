
from dataclasses import replace

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


def _artifact(*, unicode_text=False):
    source_path = "/synthetic/source.pdf"
    pages = (
        ExtractionArtifactStructuralPage(
            page_index=0,
            width_points=612.0,
            height_points=792.0,
            rotation_degrees=0,
            inspection_status="inspected",
        ),
        ExtractionArtifactStructuralPage(
            page_index=1,
            width_points=612.0,
            height_points=792.0,
            rotation_degrees=0,
            inspection_status="inspected",
        ),
    )
    metadata = ExtractionArtifactStructuralMetadata(
        allowed=True,
        reason="pdf structural metadata result contract allowed",
        fixture_id="SRC-GATE5-001",
        source_label="SRC-GATE5-é" if unicode_text else "SRC-GATE5-001",
        fixture_path=source_path,
        fixture_type="product_spec_pdf",
        inspection_mode="structural_metadata_only",
        inspection_status="inspected",
        encrypted=False,
        page_count=2,
        inspected_page_count=2,
        page_details_truncated=False,
        page_details=pages,
        max_inspected_pages=10,
        inspection_error="",
        evidence_allowed=False,
        notes="",
    )
    extractions = (
        ExtractionArtifactPageExtraction(
            source_path=source_path,
            size_bytes=100,
            page_number=1,
            extraction_index=0,
            extraction_method="embedded_text",
            content="halaman é" if unicode_text else "",
            warnings=("warning α",) if unicode_text else (),
        ),
        ExtractionArtifactPageExtraction(
            source_path=source_path,
            size_bytes=100,
            page_number=2,
            extraction_index=1,
            extraction_method="embedded_text",
            content="page two",
            warnings=("No embedded text found.",),
        ),
    )
    provisional = ExtractionArtifact(
        contract_version=EXTRACTION_ARTIFACT_CONTRACT_VERSION,
        artifact_id="0" * 64,
        upstream_contract_version=(
            EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION
        ),
        upstream_status="completed",
        job_id="job-001",
        source_id="SRC-GATE5-001",
        source_path=source_path,
        source_checksum="a" * 64,
        structural_metadata=metadata,
        page_extractions=extractions,
        execution_report_location="/synthetic/execution.json",
        cleanup_completed=True,
    )
    return replace(
        provisional,
        artifact_id=ExtractionArtifactSerializer.derive_artifact_id(
            provisional
        ),
    )


from dataclasses import FrozenInstanceError, fields, replace
from math import nan

import pytest

from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_CANONICAL_FORMAT_VERSION,
    EXTRACTION_ARTIFACT_FIELD_ORDER,
    EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER,
    EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER,
    EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER,
    EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER,
    ExtractionArtifactContractError,
    ExtractionArtifactIssue,
    ExtractionArtifactIssueCode,
)


def test_version_constants_and_exact_field_orders():
    assert EXTRACTION_ARTIFACT_CONTRACT_VERSION == (
        "extraction_artifact_contract_v1"
    )
    assert EXTRACTION_ARTIFACT_CANONICAL_FORMAT_VERSION == (
        "extraction_artifact_canonical_json_v1"
    )
    assert EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION == (
        "pdf_ingestion_orchestrator_result_contract_v1"
    )
    assert tuple(field.name for field in fields(ExtractionArtifact)) == (
        EXTRACTION_ARTIFACT_FIELD_ORDER
    )
    assert EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER == (
        "contract_version",
        "upstream_contract_version",
        "upstream_status",
        "job_id",
        "source_id",
        "source_path",
        "source_checksum",
        "structural_metadata",
        "page_extractions",
        "execution_report_location",
        "cleanup_completed",
    )
    assert tuple(
        field.name for field in fields(
            ExtractionArtifactStructuralMetadata
        )
    ) == EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER
    assert tuple(
        field.name for field in fields(
            ExtractionArtifactStructuralPage
        )
    ) == EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER
    assert tuple(
        field.name for field in fields(
            ExtractionArtifactPageExtraction
        )
    ) == EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER


def test_issue_codes_are_exact_and_issue_is_frozen():
    assert [item.value for item in ExtractionArtifactIssueCode] == [
        "invalid_upstream_result",
        "invalid_utf8",
        "invalid_json",
        "duplicate_field",
        "missing_field",
        "extra_field",
        "unsupported_version",
        "invalid_value",
        "artifact_id_mismatch",
        "non_canonical_bytes",
    ]
    issue = ExtractionArtifactIssue(
        ExtractionArtifactIssueCode.INVALID_VALUE,
        "stable",
    )
    with pytest.raises(FrozenInstanceError):
        issue.message = "changed"


def test_contract_error_exposes_one_immutable_issue():
    issue = ExtractionArtifactIssue(
        ExtractionArtifactIssueCode.INVALID_VALUE,
        "stable",
    )
    error = ExtractionArtifactContractError(issue)
    assert error.issue is issue
    assert str(error) == "stable"
    with pytest.raises(AttributeError):
        error.issue = ExtractionArtifactIssue(
            ExtractionArtifactIssueCode.INVALID_JSON,
            "changed",
        )


def test_structural_page_is_frozen_and_rejects_invalid_values():
    page = _artifact().structural_metadata.page_details[0]
    with pytest.raises(FrozenInstanceError):
        page.page_index = 2
    for value in (-1, True):
        with pytest.raises(ExtractionArtifactContractError):
            ExtractionArtifactStructuralPage(
                page_index=value,
                width_points=612.0,
                height_points=792.0,
                rotation_degrees=0,
                inspection_status="inspected",
            )
    with pytest.raises(ExtractionArtifactContractError):
        replace(page, width_points=nan)
    with pytest.raises(ExtractionArtifactContractError):
        replace(page, inspection_status="page_error")


def test_structural_metadata_deep_freezes_pages():
    artifact = _artifact()
    metadata = replace(
        artifact.structural_metadata,
        page_details=list(
            artifact.structural_metadata.page_details
        ),
    )
    assert isinstance(metadata.page_details, tuple)
    with pytest.raises(FrozenInstanceError):
        metadata.page_count = 3


def test_structural_metadata_rejects_count_and_status_mismatch():
    metadata = _artifact().structural_metadata
    with pytest.raises(ExtractionArtifactContractError):
        replace(metadata, inspected_page_count=1)
    with pytest.raises(ExtractionArtifactContractError):
        replace(metadata, inspection_status="bounded")
    with pytest.raises(ExtractionArtifactContractError):
        replace(metadata, evidence_allowed=True)


def test_page_extraction_deep_freezes_warnings_and_content_is_exact():
    page = replace(
        _artifact().page_extractions[0],
        warnings=["first", "second"],
        content="",
    )
    assert page.warnings == ("first", "second")
    assert page.content == ""
    with pytest.raises(FrozenInstanceError):
        page.content = "changed"


def test_page_extraction_rejects_invalid_numeric_or_collection_values():
    page = _artifact().page_extractions[0]
    with pytest.raises(ExtractionArtifactContractError):
        replace(page, size_bytes=-1)
    with pytest.raises(ExtractionArtifactContractError):
        replace(page, page_number=True)
    with pytest.raises(ExtractionArtifactContractError):
        replace(page, warnings=["ok", 1])


def test_artifact_deep_freezes_page_collection():
    artifact = replace(
        _artifact(),
        page_extractions=list(_artifact().page_extractions),
    )
    assert isinstance(artifact.page_extractions, tuple)
    with pytest.raises(FrozenInstanceError):
        artifact.source_id = "changed"


def test_artifact_rejects_versions_hashes_and_cleanup():
    artifact = _artifact()
    with pytest.raises(ExtractionArtifactContractError) as caught:
        replace(artifact, contract_version="v2")
    assert caught.value.issue.code is (
        ExtractionArtifactIssueCode.UNSUPPORTED_VERSION
    )
    with pytest.raises(ExtractionArtifactContractError):
        replace(artifact, artifact_id="A" * 64)
    with pytest.raises(ExtractionArtifactContractError):
        replace(artifact, source_checksum="a" * 63)
    with pytest.raises(ExtractionArtifactContractError):
        replace(artifact, cleanup_completed=False)


def test_artifact_rejects_source_count_and_sequence_mismatch():
    artifact = _artifact()
    with pytest.raises(ExtractionArtifactContractError):
        replace(
            artifact,
            source_path="/synthetic/other.pdf",
        )
    with pytest.raises(ExtractionArtifactContractError):
        replace(
            artifact,
            page_extractions=artifact.page_extractions[:1],
        )
    bad_page = replace(
        artifact.page_extractions[0],
        extraction_index=1,
    )
    with pytest.raises(ExtractionArtifactContractError):
        replace(
            artifact,
            page_extractions=(bad_page, artifact.page_extractions[1]),
        )
