from dataclasses import FrozenInstanceError, fields

import pytest

from rie.ingestion.pdf_ingestion_orchestrator_contract import (
    PdfIngestionOrchestratorIssue,
    PdfIngestionOrchestratorIssueCode,
    PdfIngestionOrchestratorStatus,
)
from rie.ingestion.pdf_ingestion_orchestrator_execution_report_contract import (
    PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_CONTRACT_VERSION,
    PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_FIELD_ORDER,
    PdfIngestionOrchestratorExecutionReport,
)


def _issue():
    return PdfIngestionOrchestratorIssue(
        PdfIngestionOrchestratorIssueCode.SOURCE_MISSING,
        "missing",
    )


def _report(**overrides):
    values = {
        "contract_version": (
            PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_CONTRACT_VERSION
        ),
        "status": PdfIngestionOrchestratorStatus.COMPLETED,
        "job_id": "a" * 64,
        "source_id": "SRC-GATE4-001",
        "source_checksum": "b" * 64,
        "structural_page_count": 2,
        "extracted_page_count": 2,
        "warning_count": 0,
        "issue": None,
        "cleanup_completed": True,
    }
    values.update(overrides)
    return PdfIngestionOrchestratorExecutionReport(**values)


def test_execution_report_field_order_is_exact():
    assert tuple(
        field.name
        for field in fields(PdfIngestionOrchestratorExecutionReport)
    ) == PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_FIELD_ORDER


def test_completed_report_is_frozen_and_valid():
    report = _report()
    assert report.status is PdfIngestionOrchestratorStatus.COMPLETED
    with pytest.raises(FrozenInstanceError):
        report.warning_count = 1


def test_failed_report_requires_one_issue_and_zero_extracted_pages():
    report = _report(
        status=PdfIngestionOrchestratorStatus.FAILED,
        structural_page_count=0,
        extracted_page_count=0,
        issue=_issue(),
    )
    assert report.issue.code is (
        PdfIngestionOrchestratorIssueCode.SOURCE_MISSING
    )


def test_contract_version_must_match():
    with pytest.raises(ValueError):
        _report(contract_version="unsupported")


def test_status_must_be_enum():
    with pytest.raises(TypeError):
        _report(status="completed")


def test_identity_fields_must_be_non_empty_strings():
    for field_name in ("job_id", "source_id", "source_checksum"):
        with pytest.raises((TypeError, ValueError)):
            _report(**{field_name: " "})


def test_counts_must_be_non_negative_integers():
    for field_name in (
        "structural_page_count",
        "extracted_page_count",
        "warning_count",
    ):
        with pytest.raises((TypeError, ValueError)):
            _report(**{field_name: -1})
        with pytest.raises((TypeError, ValueError)):
            _report(**{field_name: True})


def test_completed_report_rejects_issue():
    with pytest.raises(ValueError):
        _report(issue=_issue())


def test_completed_report_requires_matching_page_counts():
    with pytest.raises(ValueError):
        _report(structural_page_count=2, extracted_page_count=1)


def test_failed_report_rejects_missing_issue_or_extracted_pages():
    with pytest.raises(ValueError):
        _report(
            status=PdfIngestionOrchestratorStatus.FAILED,
            structural_page_count=0,
            extracted_page_count=0,
            issue=None,
        )
    with pytest.raises(ValueError):
        _report(
            status=PdfIngestionOrchestratorStatus.FAILED,
            structural_page_count=2,
            extracted_page_count=1,
            issue=_issue(),
        )
