import json
import os
from pathlib import Path

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
from rie.ingestion.pdf_ingestion_orchestrator_execution_report_serializer import (
    PdfIngestionOrchestratorExecutionReportSerializer,
    PdfIngestionOrchestratorReportWriteError,
)


def _report(*, failed=False):
    issue = None
    status = PdfIngestionOrchestratorStatus.COMPLETED
    structural_count = 2
    extracted_count = 2
    if failed:
        status = PdfIngestionOrchestratorStatus.FAILED
        structural_count = 0
        extracted_count = 0
        issue = PdfIngestionOrchestratorIssue(
            PdfIngestionOrchestratorIssueCode.SOURCE_MISSING,
            "Source missing.",
        )
    return PdfIngestionOrchestratorExecutionReport(
        contract_version=(
            PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_CONTRACT_VERSION
        ),
        status=status,
        job_id="a" * 64,
        source_id="SRC-GATE4-é",
        source_checksum="b" * 64,
        structural_page_count=structural_count,
        extracted_page_count=extracted_count,
        warning_count=1 if not failed else 0,
        issue=issue,
        cleanup_completed=True,
    )


def test_to_dict_preserves_exact_field_order_and_values():
    data = PdfIngestionOrchestratorExecutionReportSerializer.to_dict(
        _report()
    )
    assert tuple(data) == (
        PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_FIELD_ORDER
    )
    assert data["status"] == "completed"
    assert data["issue"] is None


def test_failed_issue_serialization_uses_exact_nested_order():
    data = PdfIngestionOrchestratorExecutionReportSerializer.to_dict(
        _report(failed=True)
    )
    assert tuple(data["issue"]) == ("code", "message")
    assert data["issue"] == {
        "code": "source_missing",
        "message": "Source missing.",
    }


def test_to_bytes_is_deterministic_utf8_lf_only_with_one_final_lf():
    first = PdfIngestionOrchestratorExecutionReportSerializer.to_bytes(
        _report()
    )
    second = PdfIngestionOrchestratorExecutionReportSerializer.to_bytes(
        _report()
    )
    assert first == second
    assert b"\r" not in first
    assert first.endswith(b"\n")
    assert not first.endswith(b"\n\n")
    assert not first.startswith(b"\xef\xbb\xbf")


def test_to_bytes_preserves_non_ascii_without_ascii_escaping():
    payload = PdfIngestionOrchestratorExecutionReportSerializer.to_bytes(
        _report()
    )
    assert "SRC-GATE4-é".encode("utf-8") in payload
    assert b"\\u00e9" not in payload
    assert json.loads(payload)["source_id"] == "SRC-GATE4-é"


def test_write_publishes_exact_bytes_and_removes_temporary_path(
    tmp_path: Path,
):
    output = tmp_path / "execution.json"
    expected = PdfIngestionOrchestratorExecutionReportSerializer.to_bytes(
        _report()
    )
    actual = PdfIngestionOrchestratorExecutionReportSerializer.write(
        _report(),
        output,
    )
    assert actual == expected
    assert output.read_bytes() == expected
    assert not (tmp_path / ".execution.json.tmp").exists()


def test_write_rejects_collision_without_modifying_existing_output(
    tmp_path: Path,
):
    output = tmp_path / "execution.json"
    output.write_bytes(b"existing")
    with pytest.raises(PdfIngestionOrchestratorReportWriteError):
        PdfIngestionOrchestratorExecutionReportSerializer.write(
            _report(),
            output,
        )
    assert output.read_bytes() == b"existing"


def test_write_creates_only_explicit_missing_parent_tree(tmp_path: Path):
    output = tmp_path / "new" / "nested" / "execution.json"
    PdfIngestionOrchestratorExecutionReportSerializer.write(
        _report(),
        output,
    )
    assert output.is_file()
    assert output.parent == tmp_path / "new" / "nested"


def test_write_rejects_existing_temporary_path_without_partial_output(
    tmp_path: Path,
):
    output = tmp_path / "execution.json"
    temporary = tmp_path / ".execution.json.tmp"
    temporary.write_bytes(b"occupied")
    with pytest.raises(PdfIngestionOrchestratorReportWriteError):
        PdfIngestionOrchestratorExecutionReportSerializer.write(
            _report(),
            output,
        )
    assert temporary.read_bytes() == b"occupied"
    assert not output.exists()


def test_link_failure_cleans_private_temporary_and_new_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    output = tmp_path / "new" / "execution.json"

    def fail_link(source, target):
        raise OSError("synthetic link failure")

    monkeypatch.setattr(os, "link", fail_link)
    with pytest.raises(PdfIngestionOrchestratorReportWriteError):
        PdfIngestionOrchestratorExecutionReportSerializer.write(
            _report(),
            output,
        )
    assert not output.exists()
    assert not (tmp_path / "new" / ".execution.json.tmp").exists()
    assert not (tmp_path / "new").exists()


def test_serializer_rejects_invalid_report_and_output_location(
    tmp_path: Path,
):
    with pytest.raises(TypeError):
        PdfIngestionOrchestratorExecutionReportSerializer.to_dict(
            object()
        )
    with pytest.raises(ValueError):
        PdfIngestionOrchestratorExecutionReportSerializer.write(
            _report(),
            tmp_path / "execution.txt",
        )
    with pytest.raises(ValueError):
        PdfIngestionOrchestratorExecutionReportSerializer.write(
            _report(),
            str(tmp_path / "*.json"),
        )
