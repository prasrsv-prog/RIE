import hashlib
import inspect
import json
from pathlib import Path

import pytest

from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction
from rie.extraction.pdf_text_extraction_report import (
    PdfTextExtractionAssetError,
    PdfTextExtractionReport,
)
from rie.ingestion import pdf_ingestion_orchestrator_service as service_module
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
    PdfIngestionOrchestratorIssueCode,
    PdfIngestionOrchestratorRequest,
    PdfIngestionOrchestratorStatus,
)
from rie.ingestion.pdf_ingestion_orchestrator_execution_report_serializer import (
    PdfIngestionOrchestratorExecutionReportSerializer,
)
from rie.ingestion.pdf_ingestion_orchestrator_service import (
    PdfIngestionOrchestratorService,
)


def _pdf_bytes():
    return b"%PDF-1.4\nsynthetic deterministic bytes\n%%EOF\n"


def _job(source: Path, **overrides):
    values = {
        "contract_version": (
            CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION
        ),
        "source_id": "SRC-GATE4-001",
        "source_path": str(source.resolve(strict=False)),
        "expected_source_type": "pdf",
        "authority_snapshot": "official",
        "lifecycle_snapshot": "locked",
        "eligibility_snapshot": "eligible",
        "source_checksum_algorithm": (
            CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM
        ),
        "source_checksum": (
            hashlib.sha256(source.read_bytes()).hexdigest()
            if source.is_file()
            else "a" * 64
        ),
        "execution_policy_id": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID
        ),
        "execution_policy_version": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION
        ),
        "output_location": str(
            (source.parent / "gate3-job.json").resolve(strict=False)
        ),
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


def _structural(job, *, status="inspected", encrypted=False, pages=2):
    fatal = status in {
        "encrypted",
        "parser_error",
        "parser_unavailable",
        "unreadable",
        "blocked",
    }
    return ControlledPdfStructuralMetadataResultContractResult(
        allowed=True,
        reason="allowed",
        fixture_id=job.source_id,
        source_label=job.source_id,
        fixture_path=job.source_path,
        fixture_type="product_spec_pdf",
        inspection_mode="structural_metadata_only",
        inspection_status=status,
        encrypted=encrypted,
        page_count=0 if fatal else pages,
        inspected_page_count=0 if fatal else min(pages, 10),
        page_details_truncated=pages > 10 if not fatal else False,
        page_details=(),
        max_inspected_pages=10,
        inspection_error="synthetic" if fatal else "",
        evidence_allowed=False,
        notes="",
    )


def _text_report(job, *, pages=2, warning=False, asset_errors=None):
    size = Path(job.source_path).stat().st_size
    page_extractions = [
        PdfPageTextExtraction(
            source_path=job.source_path,
            size_bytes=size,
            page_number=index + 1,
            extraction_index=index,
            extraction_method="embedded_text",
            content=f"page {index + 1}",
            warnings=(
                ["No embedded text found."]
                if warning and index == 0
                else []
            ),
        )
        for index in range(pages)
    ]
    return PdfTextExtractionReport(
        root=str(Path(job.source_path).parent),
        page_extractions=page_extractions,
        asset_errors=[] if asset_errors is None else asset_errors,
    )


def _request(job, tmp_path, name="execution.json"):
    return PdfIngestionOrchestratorRequest(
        job,
        tmp_path / name,
    )


def test_success_executes_structural_text_and_report_in_order(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.write_bytes(_pdf_bytes())
    original = source.read_bytes()
    job = _job(source)
    calls = []

    def structural(request):
        calls.append("structural")
        return _structural(job)

    def text(data):
        calls.append("text")
        return _text_report(job, warning=True)

    def writer(report, location):
        calls.append("report")
        return PdfIngestionOrchestratorExecutionReportSerializer.write(
            report,
            location,
        )

    result = PdfIngestionOrchestratorService(
        structural_executor=structural,
        page_text_extractor=text,
        report_writer=writer,
    ).execute(_request(job, tmp_path))

    assert calls == ["structural", "text", "report"]
    assert result.status is PdfIngestionOrchestratorStatus.COMPLETED
    assert len(result.page_extractions) == 2
    assert result.page_extractions[0].warnings == (
        "No embedded text found.",
    )
    assert source.read_bytes() == original
    data = json.loads((tmp_path / "execution.json").read_text())
    assert data["structural_page_count"] == 2
    assert data["extracted_page_count"] == 2
    assert data["warning_count"] == 1


def test_source_missing_returns_failure_and_publishes_failed_report(
    tmp_path: Path,
):
    source = tmp_path / "missing.pdf"
    job = _job(source)
    result = PdfIngestionOrchestratorService(
        structural_executor=lambda request: pytest.fail(
            "structural executor must not run"
        ),
    ).execute(_request(job, tmp_path))

    assert result.issue.code is (
        PdfIngestionOrchestratorIssueCode.SOURCE_MISSING
    )
    data = json.loads((tmp_path / "execution.json").read_text())
    assert data["status"] == "failed"
    assert data["issue"]["code"] == "source_missing"


def test_source_directory_returns_source_not_file_before_parser(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.mkdir()
    job = _job(source)
    result = PdfIngestionOrchestratorService(
        structural_executor=lambda request: pytest.fail(
            "structural executor must not run"
        ),
    ).execute(_request(job, tmp_path))

    assert result.issue.code is (
        PdfIngestionOrchestratorIssueCode.SOURCE_NOT_FILE
    )


def test_checksum_mismatch_is_rejected_before_structural_execution(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.write_bytes(_pdf_bytes())
    job = _job(source, source_checksum="b" * 64)
    result = PdfIngestionOrchestratorService(
        structural_executor=lambda request: pytest.fail(
            "structural executor must not run"
        ),
    ).execute(_request(job, tmp_path))

    assert result.issue.code is (
        PdfIngestionOrchestratorIssueCode.SOURCE_CHECKSUM_MISMATCH
    )
    assert result.issue.code is not (
        PdfIngestionOrchestratorIssueCode.AUTHORITY_REJECTED
    )


def test_unsupported_expected_type_or_pdf_header_is_rejected(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.write_bytes(_pdf_bytes())
    non_pdf_job = _job(source, expected_source_type="jpeg")
    first = PdfIngestionOrchestratorService().execute(
        _request(non_pdf_job, tmp_path, "first.json")
    )
    assert first.issue.code is (
        PdfIngestionOrchestratorIssueCode.UNSUPPORTED_SOURCE
    )

    source.write_bytes(b"not a pdf")
    bad_header_job = _job(source)
    second = PdfIngestionOrchestratorService().execute(
        _request(bad_header_job, tmp_path, "second.json")
    )
    assert second.issue.code is (
        PdfIngestionOrchestratorIssueCode.UNSUPPORTED_SOURCE
    )


def test_ineligible_or_identity_mismatched_job_is_authority_rejected(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.write_bytes(_pdf_bytes())
    review_job = _job(source, eligibility_snapshot="eligible_with_review")
    first = PdfIngestionOrchestratorService().execute(
        _request(review_job, tmp_path, "first.json")
    )
    assert first.issue.code is (
        PdfIngestionOrchestratorIssueCode.AUTHORITY_REJECTED
    )

    mismatch_job = _job(source, job_id="f" * 64)
    second = PdfIngestionOrchestratorService().execute(
        _request(mismatch_job, tmp_path, "second.json")
    )
    assert second.issue.code is (
        PdfIngestionOrchestratorIssueCode.AUTHORITY_REJECTED
    )


def test_encrypted_structural_result_blocks_text_extraction(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.write_bytes(_pdf_bytes())
    job = _job(source)
    result = PdfIngestionOrchestratorService(
        structural_executor=lambda request: _structural(
            job,
            status="encrypted",
            encrypted=True,
            pages=0,
        ),
        page_text_extractor=lambda data: pytest.fail(
            "page text extractor must not run"
        ),
    ).execute(_request(job, tmp_path))

    assert result.issue.code is (
        PdfIngestionOrchestratorIssueCode.ENCRYPTED_PDF
    )


def test_structural_partial_and_executor_exception_map_exactly(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.write_bytes(_pdf_bytes())
    job = _job(source)

    partial = PdfIngestionOrchestratorService(
        structural_executor=lambda request: _structural(
            job,
            status="partial",
        ),
    ).execute(_request(job, tmp_path, "partial.json"))
    assert partial.issue.code is (
        PdfIngestionOrchestratorIssueCode.STRUCTURAL_METADATA_FAILURE
    )

    def raise_parser(request):
        raise RuntimeError("private parser detail")

    parser = PdfIngestionOrchestratorService(
        structural_executor=raise_parser,
    ).execute(_request(job, tmp_path, "parser.json"))
    assert parser.issue.code is (
        PdfIngestionOrchestratorIssueCode.PARSER_FAILURE
    )
    assert "private parser detail" not in parser.issue.message


def test_text_asset_error_page_mismatch_or_page_warning_fails(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.write_bytes(_pdf_bytes())
    job = _job(source)
    structural = lambda request: _structural(job)

    asset_error = PdfIngestionOrchestratorService(
        structural_executor=structural,
        page_text_extractor=lambda data: _text_report(
            job,
            pages=0,
            asset_errors=[
                PdfTextExtractionAssetError(
                    source_path=job.source_path,
                    size_bytes=source.stat().st_size,
                    error="private",
                )
            ],
        ),
    ).execute(_request(job, tmp_path, "asset.json"))
    assert asset_error.issue.code is (
        PdfIngestionOrchestratorIssueCode.TEXT_EXTRACTION_FAILURE
    )

    mismatch = PdfIngestionOrchestratorService(
        structural_executor=structural,
        page_text_extractor=lambda data: _text_report(job, pages=1),
    ).execute(_request(job, tmp_path, "mismatch.json"))
    assert mismatch.issue.code is (
        PdfIngestionOrchestratorIssueCode.TEXT_EXTRACTION_FAILURE
    )

    warning_report = _text_report(job)
    warning_report.page_extractions[0].warnings.append(
        "Failed to extract embedded text: private"
    )
    warning = PdfIngestionOrchestratorService(
        structural_executor=structural,
        page_text_extractor=lambda data: warning_report,
    ).execute(_request(job, tmp_path, "warning.json"))
    assert warning.issue.code is (
        PdfIngestionOrchestratorIssueCode.TEXT_EXTRACTION_FAILURE
    )


def test_output_collision_or_writer_failure_preserves_source_and_cleans_temp(
    tmp_path: Path,
):
    source = tmp_path / "source.pdf"
    source.write_bytes(_pdf_bytes())
    original = source.read_bytes()
    job = _job(source)
    collision = tmp_path / "collision.json"
    collision.write_bytes(b"existing")

    first = PdfIngestionOrchestratorService().execute(
        PdfIngestionOrchestratorRequest(job, collision)
    )
    assert first.issue.code is (
        PdfIngestionOrchestratorIssueCode.OUTPUT_FAILURE
    )
    assert collision.read_bytes() == b"existing"

    def failing_writer(report, location):
        temporary = Path(location).with_name(
            "." + Path(location).name + ".tmp"
        )
        temporary.write_bytes(b"partial")
        raise OSError("private output detail")

    second = PdfIngestionOrchestratorService(
        structural_executor=lambda request: _structural(job),
        page_text_extractor=lambda data: _text_report(job),
        report_writer=failing_writer,
    ).execute(_request(job, tmp_path, "failed-write.json"))
    assert second.issue.code is (
        PdfIngestionOrchestratorIssueCode.OUTPUT_FAILURE
    )
    assert not (tmp_path / ".failed-write.json.tmp").exists()
    assert source.read_bytes() == original

    source_text = inspect.getsource(service_module)
    for fragment in (
        "iterdir",
        "rglob",
        "scandir",
        "walk(",
        "glob(",
        "Evidence",
        "Knowledge",
        "PromptCandidate",
    ):
        assert fragment not in source_text
