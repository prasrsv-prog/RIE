from dataclasses import FrozenInstanceError, fields
from pathlib import Path

import pytest

from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction
from rie.ingestion.controlled_pdf_structural_metadata_result_contract import (
    ControlledPdfStructuralMetadataResultContractResult,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM,
    CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID,
    CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION,
    CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION,
    IngestionJob,
    derive_ingestion_job_id,
)
from rie.ingestion.pdf_ingestion_orchestrator_contract import (
    PDF_INGESTION_ORCHESTRATOR_REQUEST_FIELD_ORDER,
    PDF_INGESTION_ORCHESTRATOR_RESULT_FIELD_ORDER,
    PdfIngestionOrchestratorIssue,
    PdfIngestionOrchestratorIssueCode,
    PdfIngestionOrchestratorRequest,
    PdfIngestionOrchestratorResult,
    PdfIngestionOrchestratorStatus,
    completed_result,
    failed_result,
    freeze_page_extractions,
)


def _job(**overrides):
    values = {
        "contract_version": (
            CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION
        ),
        "source_id": "SRC-GATE4-001",
        "source_path": str(Path("/synthetic/source.pdf")),
        "expected_source_type": "pdf",
        "authority_snapshot": "official",
        "lifecycle_snapshot": "locked",
        "eligibility_snapshot": "eligible",
        "source_checksum_algorithm": (
            CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM
        ),
        "source_checksum": "a" * 64,
        "execution_policy_id": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID
        ),
        "execution_policy_version": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION
        ),
        "output_location": str(Path("/synthetic/job.json")),
    }
    values.update(
        {
            key: value
            for key, value in overrides.items()
            if key != "job_id"
        }
    )
    job_id = overrides.get(
        "job_id",
        derive_ingestion_job_id(**values),
    )
    return IngestionJob(job_id=job_id, **values)


def _structural(page_count=1):
    return ControlledPdfStructuralMetadataResultContractResult(
        allowed=True,
        reason="allowed",
        fixture_id="SRC-GATE4-001",
        source_label="SRC-GATE4-001",
        fixture_path=str(Path("/synthetic/source.pdf")),
        fixture_type="product_spec_pdf",
        inspection_mode="structural_metadata_only",
        inspection_status="inspected",
        encrypted=False,
        page_count=page_count,
        inspected_page_count=page_count,
        page_details_truncated=False,
        page_details=(),
        max_inspected_pages=10,
        inspection_error="",
        evidence_allowed=False,
        notes="",
    )


def _pages(count=1):
    return freeze_page_extractions(
        [
            PdfPageTextExtraction(
                source_path=str(Path("/synthetic/source.pdf")),
                size_bytes=10,
                page_number=index + 1,
                extraction_index=index,
                extraction_method="embedded_text",
                content=f"page {index + 1}",
                warnings=[],
            )
            for index in range(count)
        ]
    )


def test_request_and_result_field_orders_are_exact():
    assert tuple(
        field.name for field in fields(PdfIngestionOrchestratorRequest)
    ) == PDF_INGESTION_ORCHESTRATOR_REQUEST_FIELD_ORDER
    assert tuple(
        field.name for field in fields(PdfIngestionOrchestratorResult)
    ) == PDF_INGESTION_ORCHESTRATOR_RESULT_FIELD_ORDER


def test_request_is_frozen_and_accepts_one_job_and_report_path():
    request = PdfIngestionOrchestratorRequest(
        _job(),
        "/synthetic/execution.json",
    )
    assert request.job.source_id == "SRC-GATE4-001"
    with pytest.raises(FrozenInstanceError):
        request.execution_report_location = "changed.json"


def test_request_rejects_invalid_job_type():
    with pytest.raises(TypeError):
        PdfIngestionOrchestratorRequest(
            object(),
            "/synthetic/execution.json",
        )


def test_request_rejects_wildcard_non_json_and_colliding_locations():
    job = _job()
    with pytest.raises(ValueError):
        PdfIngestionOrchestratorRequest(job, "/synthetic/*.json")
    with pytest.raises(ValueError):
        PdfIngestionOrchestratorRequest(job, "/synthetic/report.txt")
    with pytest.raises(ValueError):
        PdfIngestionOrchestratorRequest(job, job.source_path)
    with pytest.raises(ValueError):
        PdfIngestionOrchestratorRequest(job, job.output_location)


def test_status_and_issue_enums_are_exact():
    assert [item.value for item in PdfIngestionOrchestratorStatus] == [
        "completed",
        "failed",
    ]
    assert [
        item.value for item in PdfIngestionOrchestratorIssueCode
    ] == [
        "source_missing",
        "source_not_file",
        "source_checksum_mismatch",
        "unsupported_source",
        "encrypted_pdf",
        "parser_failure",
        "structural_metadata_failure",
        "text_extraction_failure",
        "output_failure",
        "authority_rejected",
    ]


def test_issue_is_frozen_and_requires_enum_and_message():
    issue = PdfIngestionOrchestratorIssue(
        PdfIngestionOrchestratorIssueCode.SOURCE_MISSING,
        "missing",
    )
    with pytest.raises(FrozenInstanceError):
        issue.message = "changed"
    with pytest.raises(TypeError):
        PdfIngestionOrchestratorIssue("source_missing", "missing")
    with pytest.raises(ValueError):
        PdfIngestionOrchestratorIssue(
            PdfIngestionOrchestratorIssueCode.SOURCE_MISSING,
            " ",
        )


def test_completed_result_preserves_identity_and_deep_freezes_pages():
    result = completed_result(
        job=_job(),
        structural_metadata=_structural(),
        page_extractions=_pages(),
        execution_report_location="/synthetic/execution.json",
    )
    assert result.status is PdfIngestionOrchestratorStatus.COMPLETED
    assert result.issue is None
    assert isinstance(result.page_extractions, tuple)
    assert isinstance(result.page_extractions[0].warnings, tuple)
    with pytest.raises(FrozenInstanceError):
        result.status = PdfIngestionOrchestratorStatus.FAILED


def test_completed_result_rejects_page_count_or_source_mismatch():
    with pytest.raises(ValueError):
        completed_result(
            job=_job(),
            structural_metadata=_structural(page_count=2),
            page_extractions=_pages(count=1),
            execution_report_location="/synthetic/execution.json",
        )
    bad_page = PdfPageTextExtraction(
        source_path="/synthetic/other.pdf",
        size_bytes=10,
        page_number=1,
        extraction_index=0,
        extraction_method="embedded_text",
        content="page",
        warnings=(),
    )
    with pytest.raises(ValueError):
        completed_result(
            job=_job(),
            structural_metadata=_structural(),
            page_extractions=(bad_page,),
            execution_report_location="/synthetic/execution.json",
        )


def test_failed_result_contains_exact_issue_and_no_partial_data():
    result = failed_result(
        job=_job(),
        code=PdfIngestionOrchestratorIssueCode.SOURCE_MISSING,
        message="missing",
        execution_report_location="/synthetic/execution.json",
    )
    assert result.status is PdfIngestionOrchestratorStatus.FAILED
    assert result.structural_metadata is None
    assert result.page_extractions == ()
    assert result.issue.code is (
        PdfIngestionOrchestratorIssueCode.SOURCE_MISSING
    )
    assert result.cleanup_completed is True


def test_failed_result_rejects_partial_structural_or_page_output():
    base = failed_result(
        job=_job(),
        code=PdfIngestionOrchestratorIssueCode.SOURCE_MISSING,
        message="missing",
        execution_report_location="/synthetic/execution.json",
    )
    with pytest.raises(ValueError):
        PdfIngestionOrchestratorResult(
            contract_version=base.contract_version,
            status=base.status,
            job_id=base.job_id,
            source_id=base.source_id,
            source_path=base.source_path,
            source_checksum=base.source_checksum,
            structural_metadata=_structural(),
            page_extractions=(),
            issue=base.issue,
            execution_report_location=base.execution_report_location,
            cleanup_completed=True,
        )
