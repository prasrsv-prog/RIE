
import builtins
import inspect
from pathlib import Path

import pytest

from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction
from rie.extraction.extraction_artifact_contract import (
    ExtractionArtifactContractError,
    ExtractionArtifactIssueCode,
)
from rie.extraction.extraction_artifact_serializer import (
    ExtractionArtifactSerializer,
)
from rie.extraction import extraction_artifact_service as service_module
from rie.extraction.extraction_artifact_service import (
    ExtractionArtifactService,
)
from rie.ingestion.controlled_pdf_structural_metadata_result_contract import (
    ControlledPdfStructuralMetadataPageItem,
    ControlledPdfStructuralMetadataResultContractResult,
)
from rie.ingestion.pdf_ingestion_orchestrator_contract import (
    PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION,
    PdfIngestionOrchestratorIssue,
    PdfIngestionOrchestratorIssueCode,
    PdfIngestionOrchestratorResult,
    PdfIngestionOrchestratorStatus,
)


def _structural():
    return ControlledPdfStructuralMetadataResultContractResult(
        allowed=True,
        reason="pdf structural metadata result contract allowed",
        fixture_id="SRC-GATE5-001",
        source_label="SRC-GATE5-é",
        fixture_path="/synthetic/source.pdf",
        fixture_type="product_spec_pdf",
        inspection_mode="structural_metadata_only",
        inspection_status="inspected",
        encrypted=False,
        page_count=2,
        inspected_page_count=2,
        page_details_truncated=False,
        page_details=(
            ControlledPdfStructuralMetadataPageItem(
                page_index=0,
                width_points=612.0,
                height_points=792.0,
                rotation_degrees=0,
                inspection_status="inspected",
            ),
            ControlledPdfStructuralMetadataPageItem(
                page_index=1,
                width_points=612.0,
                height_points=792.0,
                rotation_degrees=0,
                inspection_status="inspected",
            ),
        ),
        max_inspected_pages=10,
        inspection_error="",
        evidence_allowed=False,
        notes="",
    )


def _pages():
    return (
        PdfPageTextExtraction(
            source_path="/synthetic/source.pdf",
            size_bytes=100,
            page_number=1,
            extraction_index=0,
            extraction_method="embedded_text",
            content="halaman é",
            warnings=("first", "second"),
        ),
        PdfPageTextExtraction(
            source_path="/synthetic/source.pdf",
            size_bytes=100,
            page_number=2,
            extraction_index=1,
            extraction_method="embedded_text",
            content="",
            warnings=(),
        ),
    )


def _completed():
    return PdfIngestionOrchestratorResult(
        contract_version=(
            PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION
        ),
        status=PdfIngestionOrchestratorStatus.COMPLETED,
        job_id="job-001",
        source_id="SRC-GATE5-001",
        source_path="/synthetic/source.pdf",
        source_checksum="a" * 64,
        structural_metadata=_structural(),
        page_extractions=_pages(),
        issue=None,
        execution_report_location="/synthetic/execution.json",
        cleanup_completed=True,
    )


def _failed():
    return PdfIngestionOrchestratorResult(
        contract_version=(
            PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION
        ),
        status=PdfIngestionOrchestratorStatus.FAILED,
        job_id="job-001",
        source_id="SRC-GATE5-001",
        source_path="/synthetic/source.pdf",
        source_checksum="a" * 64,
        structural_metadata=None,
        page_extractions=(),
        issue=PdfIngestionOrchestratorIssue(
            PdfIngestionOrchestratorIssueCode.SOURCE_MISSING,
            "source missing.",
        ),
        execution_report_location="/synthetic/execution.json",
        cleanup_completed=True,
    )


def test_completed_result_values_are_copied_exactly():
    result = _completed()
    artifact = ExtractionArtifactService.from_completed_result(result)
    assert artifact.job_id == result.job_id
    assert artifact.source_id == result.source_id
    assert artifact.source_path == result.source_path
    assert artifact.source_checksum == result.source_checksum
    assert artifact.execution_report_location == (
        result.execution_report_location
    )
    assert artifact.structural_metadata.source_label == "SRC-GATE5-é"
    assert artifact.page_extractions[0].content == "halaman é"
    assert artifact.page_extractions[0].warnings == (
        "first",
        "second",
    )


def test_repeated_construction_produces_same_identity_and_bytes():
    first = ExtractionArtifactService.from_completed_result(
        _completed()
    )
    second = ExtractionArtifactService.from_completed_result(
        _completed()
    )
    assert first.artifact_id == second.artifact_id
    assert (
        ExtractionArtifactSerializer.to_bytes(first)
        == ExtractionArtifactSerializer.to_bytes(second)
    )


def test_service_deep_freezes_nested_collections():
    artifact = ExtractionArtifactService.from_completed_result(
        _completed()
    )
    assert isinstance(artifact.page_extractions, tuple)
    assert isinstance(artifact.page_extractions[0].warnings, tuple)
    assert isinstance(
        artifact.structural_metadata.page_details,
        tuple,
    )


def test_failed_result_is_rejected_with_exact_issue():
    with pytest.raises(ExtractionArtifactContractError) as caught:
        ExtractionArtifactService.from_completed_result(_failed())
    assert caught.value.issue.code is (
        ExtractionArtifactIssueCode.INVALID_UPSTREAM_RESULT
    )


def test_lookalike_value_is_rejected():
    class Lookalike:
        status = PdfIngestionOrchestratorStatus.COMPLETED

    with pytest.raises(ExtractionArtifactContractError) as caught:
        ExtractionArtifactService.from_completed_result(Lookalike())
    assert caught.value.issue.code is (
        ExtractionArtifactIssueCode.INVALID_UPSTREAM_RESULT
    )


def test_invalid_completed_structural_value_is_rejected_as_upstream():
    result = _completed()
    object.__setattr__(
        result.structural_metadata,
        "inspected_page_count",
        1,
    )
    with pytest.raises(ExtractionArtifactContractError) as caught:
        ExtractionArtifactService.from_completed_result(result)
    assert caught.value.issue.code is (
        ExtractionArtifactIssueCode.INVALID_UPSTREAM_RESULT
    )


def test_service_does_not_read_source_or_publish_files(
    monkeypatch: pytest.MonkeyPatch,
):
    def fail(*args, **kwargs):
        raise AssertionError("filesystem access is forbidden")

    monkeypatch.setattr(builtins, "open", fail)
    monkeypatch.setattr(Path, "read_bytes", fail)
    monkeypatch.setattr(Path, "write_bytes", fail)
    artifact = ExtractionArtifactService.from_completed_result(
        _completed()
    )
    assert artifact.source_path == "/synthetic/source.pdf"


def test_service_source_has_no_discovery_or_later_stage_behavior():
    source = inspect.getsource(service_module)
    for fragment in (
        "iterdir",
        "rglob",
        "scandir",
        "walk(",
        "glob(",
        "write_bytes",
        "open(",
        "PromptCandidate",
        "FinalPrompt",
    ):
        assert fragment not in source
