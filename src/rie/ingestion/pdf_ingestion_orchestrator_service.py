"""Deterministic Gate 4 PDF ingestion orchestration service."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Callable

from rie.extraction.pdf_text_extraction_report import (
    PdfTextExtractionReport,
)
from rie.extraction.pdf_text_extractor import PdfTextExtractor
from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    PERMITTED_STRUCTURAL_FIELDS,
    PRODUCT_SPEC_PDF_FIXTURE_TYPE,
    STRUCTURAL_METADATA_ONLY_MODE,
)
from rie.ingestion.controlled_pdf_structural_metadata_execution_contract import (
    MAX_INSPECTED_PAGES_LIMIT,
    ControlledPdfStructuralMetadataExecutionContractResult,
)
from rie.ingestion.controlled_pdf_structural_metadata_implementation import (
    ControlledPdfStructuralMetadataImplementation,
    ControlledPdfStructuralMetadataImplementationRequest,
)
from rie.ingestion.controlled_pdf_structural_metadata_result_contract import (
    ControlledPdfStructuralMetadataResultContractResult,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    IngestionJob,
    derive_ingestion_job_id,
)
from rie.ingestion.pdf_ingestion_orchestrator_contract import (
    PdfIngestionOrchestratorIssueCode,
    PdfIngestionOrchestratorRequest,
    PdfIngestionOrchestratorResult,
    PdfIngestionOrchestratorStatus,
    completed_result,
    failed_result,
    freeze_page_extractions,
)
from rie.ingestion.pdf_ingestion_orchestrator_execution_report_contract import (
    PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_CONTRACT_VERSION,
    PdfIngestionOrchestratorExecutionReport,
)
from rie.ingestion.pdf_ingestion_orchestrator_execution_report_serializer import (
    PdfIngestionOrchestratorExecutionReportSerializer,
)


_SOURCE_MISSING_MESSAGE = "Admitted source does not exist."
_SOURCE_NOT_FILE_MESSAGE = "Admitted source is not a regular file."
_SOURCE_CHECKSUM_MISMATCH_MESSAGE = (
    "Admitted source checksum could not be reproduced."
)
_UNSUPPORTED_SOURCE_MESSAGE = "Admitted source is not a supported PDF."
_ENCRYPTED_PDF_MESSAGE = "Encrypted PDF ingestion is not allowed."
_PARSER_FAILURE_MESSAGE = "PDF parser execution failed."
_STRUCTURAL_METADATA_FAILURE_MESSAGE = (
    "PDF structural metadata inspection failed."
)
_TEXT_EXTRACTION_FAILURE_MESSAGE = "PDF page text extraction failed."
_OUTPUT_FAILURE_MESSAGE = "Execution report publication failed."
_AUTHORITY_REJECTED_MESSAGE = (
    "Ingestion job authority or identity is not acceptable."
)

_PDF_HEADER = b"%PDF-"
_CHECKSUM_CHUNK_SIZE = 1024 * 1024


class PdfIngestionOrchestratorService:
    def __init__(
        self,
        *,
        structural_executor: Callable[[object], object] | None = None,
        page_text_extractor: Callable[[dict[str, object]], object] | None = None,
        report_writer: Callable[[object, str | Path], bytes] | None = None,
    ) -> None:
        self._structural_executor = (
            structural_executor
            or ControlledPdfStructuralMetadataImplementation.execute
        )
        self._page_text_extractor = (
            page_text_extractor
            or PdfTextExtractor().extract
        )
        self._report_writer = (
            report_writer
            or PdfIngestionOrchestratorExecutionReportSerializer.write
        )

    def execute(
        self,
        request: PdfIngestionOrchestratorRequest,
    ) -> PdfIngestionOrchestratorResult:
        if not isinstance(
            request,
            PdfIngestionOrchestratorRequest,
        ):
            raise TypeError(
                "request must be PdfIngestionOrchestratorRequest."
            )

        job = request.job
        report_path = Path(
            request.execution_report_location
        ).resolve(strict=False)
        report_location = str(report_path)

        authority_issue = _validate_job_authority(job)

        if authority_issue is not None:
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.AUTHORITY_REJECTED,
                message=_AUTHORITY_REJECTED_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        source_path = Path(job.source_path)

        if not source_path.exists():
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.SOURCE_MISSING,
                message=_SOURCE_MISSING_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if not source_path.is_file():
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.SOURCE_NOT_FILE,
                message=_SOURCE_NOT_FILE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if not _source_type_is_pdf(job, source_path):
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.UNSUPPORTED_SOURCE,
                message=_UNSUPPORTED_SOURCE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if not _report_location_is_acceptable(
            job=job,
            source_path=source_path,
            report_path=report_path,
        ):
            return failed_result(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.OUTPUT_FAILURE,
                message=_OUTPUT_FAILURE_MESSAGE,
                execution_report_location=report_location,
            )

        try:
            checksum, header, size_bytes = _read_source_identity(
                source_path
            )
        except OSError:
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .SOURCE_CHECKSUM_MISMATCH
                ),
                message=_SOURCE_CHECKSUM_MISMATCH_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if header != _PDF_HEADER:
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.UNSUPPORTED_SOURCE,
                message=_UNSUPPORTED_SOURCE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if checksum != job.source_checksum:
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .SOURCE_CHECKSUM_MISMATCH
                ),
                message=_SOURCE_CHECKSUM_MISMATCH_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        structural_status, structural_result = (
            self._execute_structural_metadata(job)
        )

        if structural_status == "parser_failure":
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.PARSER_FAILURE,
                message=_PARSER_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if structural_status != "ok" or structural_result is None:
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .STRUCTURAL_METADATA_FAILURE
                ),
                message=_STRUCTURAL_METADATA_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if structural_result.encrypted is True or (
            structural_result.inspection_status == "encrypted"
        ):
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.ENCRYPTED_PDF,
                message=_ENCRYPTED_PDF_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if structural_result.inspection_status in {
            "parser_unavailable",
            "parser_error",
            "unreadable",
        }:
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.PARSER_FAILURE,
                message=_PARSER_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if (
            structural_result.allowed is not True
            or structural_result.inspection_status
            not in {"inspected", "bounded"}
        ):
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .STRUCTURAL_METADATA_FAILURE
                ),
                message=_STRUCTURAL_METADATA_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        extraction_status, extraction_report = (
            self._execute_page_text_extraction(
                job=job,
                source_path=source_path,
                size_bytes=size_bytes,
            )
        )

        if extraction_status == "parser_failure":
            return self._failure(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.PARSER_FAILURE,
                message=_PARSER_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if extraction_status != "ok" or extraction_report is None:
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .TEXT_EXTRACTION_FAILURE
                ),
                message=_TEXT_EXTRACTION_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if extraction_report.asset_errors:
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .TEXT_EXTRACTION_FAILURE
                ),
                message=_TEXT_EXTRACTION_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        try:
            page_extractions = freeze_page_extractions(
                extraction_report.page_extractions
            )
        except (TypeError, ValueError):
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .TEXT_EXTRACTION_FAILURE
                ),
                message=_TEXT_EXTRACTION_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if not _page_extractions_are_acceptable(
            page_extractions=page_extractions,
            source_path=job.source_path,
            size_bytes=size_bytes,
            structural_page_count=structural_result.page_count,
        ):
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .TEXT_EXTRACTION_FAILURE
                ),
                message=_TEXT_EXTRACTION_FAILURE_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        try:
            final_checksum, final_header, final_size = (
                _read_source_identity(source_path)
            )
        except OSError:
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .SOURCE_CHECKSUM_MISMATCH
                ),
                message=_SOURCE_CHECKSUM_MISMATCH_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        if (
            final_checksum != job.source_checksum
            or final_header != _PDF_HEADER
            or final_size != size_bytes
        ):
            return self._failure(
                job=job,
                code=(
                    PdfIngestionOrchestratorIssueCode
                    .SOURCE_CHECKSUM_MISMATCH
                ),
                message=_SOURCE_CHECKSUM_MISMATCH_MESSAGE,
                report_path=report_path,
                report_location=report_location,
            )

        result = completed_result(
            job=job,
            structural_metadata=structural_result,
            page_extractions=page_extractions,
            execution_report_location=report_location,
        )
        execution_report = _execution_report_from_result(result)

        try:
            self._report_writer(
                execution_report,
                report_path,
            )
        except Exception:
            _cleanup_private_temporary_path(report_path)
            return failed_result(
                job=job,
                code=PdfIngestionOrchestratorIssueCode.OUTPUT_FAILURE,
                message=_OUTPUT_FAILURE_MESSAGE,
                execution_report_location=report_location,
            )

        return result

    def _execute_structural_metadata(
        self,
        job: IngestionJob,
    ) -> tuple[
        str,
        ControlledPdfStructuralMetadataResultContractResult | None,
    ]:
        execution_contract = (
            ControlledPdfStructuralMetadataExecutionContractResult(
                allowed=True,
                reason="Gate 4 structural metadata adapter.",
                fixture_id=job.source_id,
                fixture_path=job.source_path,
                fixture_type=PRODUCT_SPEC_PDF_FIXTURE_TYPE,
                inspection_mode=STRUCTURAL_METADATA_ONLY_MODE,
                execution_allowed=True,
                permitted_fields=PERMITTED_STRUCTURAL_FIELDS,
                max_inspected_pages=MAX_INSPECTED_PAGES_LIMIT,
                allow_content_extraction=False,
                allow_output_file_creation=False,
                evidence_allowed=False,
                notes="",
            )
        )
        implementation_request = (
            ControlledPdfStructuralMetadataImplementationRequest(
                execution_contract_result=execution_contract,
                source_label=job.source_id,
                allow_implementation_execution=True,
                notes="",
            )
        )

        try:
            result = self._structural_executor(
                implementation_request
            )
        except Exception:
            return "parser_failure", None

        if not isinstance(
            result,
            ControlledPdfStructuralMetadataResultContractResult,
        ):
            return "structural_failure", None

        if (
            result.fixture_id != job.source_id
            or result.fixture_path != job.source_path
            or result.fixture_type != PRODUCT_SPEC_PDF_FIXTURE_TYPE
            or result.inspection_mode != STRUCTURAL_METADATA_ONLY_MODE
            or result.evidence_allowed is not False
        ):
            return "structural_failure", (
                ControlledPdfStructuralMetadataResultContractResult(
                allowed=False,
                reason="Gate 4 structural metadata identity mismatch.",
                fixture_id="",
                source_label="",
                fixture_path="",
                fixture_type="",
                inspection_mode="",
                inspection_status="blocked",
                encrypted=False,
                page_count=0,
                inspected_page_count=0,
                page_details_truncated=False,
                page_details=(),
                max_inspected_pages=0,
                inspection_error="implementation safety checks failed",
                evidence_allowed=False,
                notes="",
                )
            )

        return "ok", result

    def _execute_page_text_extraction(
        self,
        *,
        job: IngestionJob,
        source_path: Path,
        size_bytes: int,
    ) -> tuple[str, PdfTextExtractionReport | None]:
        request_data: dict[str, object] = {
            "root": str(source_path.parent),
            "items": [
                {
                    "asset_type": "PDF",
                    "source_path": job.source_path,
                    "size_bytes": size_bytes,
                }
            ],
        }

        try:
            result = self._page_text_extractor(request_data)
        except Exception:
            return "parser_failure", None

        if not isinstance(result, PdfTextExtractionReport):
            return "text_failure", None

        if result.root != str(source_path.parent):
            return "text_failure", None

        return "ok", result

    def _failure(
        self,
        *,
        job: IngestionJob,
        code: PdfIngestionOrchestratorIssueCode,
        message: str,
        report_path: Path,
        report_location: str,
    ) -> PdfIngestionOrchestratorResult:
        result = failed_result(
            job=job,
            code=code,
            message=message,
            execution_report_location=report_location,
        )
        report = _execution_report_from_result(result)

        try:
            self._report_writer(report, report_path)
        except Exception:
            _cleanup_private_temporary_path(report_path)

        return result


def _validate_job_authority(
    job: IngestionJob,
) -> str | None:
    if not isinstance(job, IngestionJob):
        return "invalid job type"

    identity_fields = {
        "contract_version": job.contract_version,
        "source_id": job.source_id,
        "source_path": job.source_path,
        "expected_source_type": job.expected_source_type,
        "authority_snapshot": job.authority_snapshot,
        "lifecycle_snapshot": job.lifecycle_snapshot,
        "eligibility_snapshot": job.eligibility_snapshot,
        "source_checksum_algorithm": job.source_checksum_algorithm,
        "source_checksum": job.source_checksum,
        "execution_policy_id": job.execution_policy_id,
        "execution_policy_version": job.execution_policy_version,
        "output_location": job.output_location,
    }

    try:
        expected_job_id = derive_ingestion_job_id(
            **identity_fields
        )
    except (TypeError, ValueError):
        return "invalid job identity"

    if expected_job_id != job.job_id:
        return "job identity mismatch"

    if job.eligibility_snapshot != "eligible":
        return "source eligibility is not acceptable"

    if not Path(job.source_path).is_absolute():
        return "source_path is not absolute"

    if not Path(job.output_location).is_absolute():
        return "output_location is not absolute"

    return None


def _source_type_is_pdf(
    job: IngestionJob,
    source_path: Path,
) -> bool:
    return (
        job.expected_source_type.casefold() == "pdf"
        and source_path.suffix.casefold() == ".pdf"
    )


def _report_location_is_acceptable(
    *,
    job: IngestionJob,
    source_path: Path,
    report_path: Path,
) -> bool:
    job_output_path = Path(job.output_location).resolve(
        strict=False
    )
    source_canonical = source_path.resolve(strict=False)

    if report_path in {source_canonical, job_output_path}:
        return False

    if report_path.exists():
        return False

    parent_path = report_path.parent

    if parent_path.exists() and not parent_path.is_dir():
        return False

    temporary_path = report_path.with_name(
        "." + report_path.name + ".tmp"
    )

    return not temporary_path.exists()


def _read_source_identity(
    source_path: Path,
) -> tuple[str, bytes, int]:
    digest = sha256()
    header = b""
    size_bytes = 0

    with source_path.open("rb") as stream:
        while True:
            chunk = stream.read(_CHECKSUM_CHUNK_SIZE)

            if not chunk:
                break

            if size_bytes == 0:
                header = chunk[: len(_PDF_HEADER)]

            digest.update(chunk)
            size_bytes += len(chunk)

    return digest.hexdigest(), header, size_bytes


def _page_extractions_are_acceptable(
    *,
    page_extractions: tuple,
    source_path: str,
    size_bytes: int,
    structural_page_count: int,
) -> bool:
    if len(page_extractions) != structural_page_count:
        return False

    for index, extraction in enumerate(page_extractions):
        if extraction.source_path != source_path:
            return False

        if extraction.size_bytes != size_bytes:
            return False

        if extraction.page_number != index + 1:
            return False

        if extraction.extraction_index != index:
            return False

        if extraction.extraction_method != "embedded_text":
            return False

        if any(
            warning.startswith(
                "Failed to extract embedded text:"
            )
            for warning in extraction.warnings
        ):
            return False

    return True


def _execution_report_from_result(
    result: PdfIngestionOrchestratorResult,
) -> PdfIngestionOrchestratorExecutionReport:
    if result.status is PdfIngestionOrchestratorStatus.COMPLETED:
        structural_page_count = (
            result.structural_metadata.page_count
            if result.structural_metadata is not None
            else 0
        )
        extracted_page_count = len(result.page_extractions)
        warning_count = sum(
            len(extraction.warnings)
            for extraction in result.page_extractions
        )
    else:
        structural_page_count = 0
        extracted_page_count = 0
        warning_count = 0

    return PdfIngestionOrchestratorExecutionReport(
        contract_version=(
            PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_CONTRACT_VERSION
        ),
        status=result.status,
        job_id=result.job_id,
        source_id=result.source_id,
        source_checksum=result.source_checksum,
        structural_page_count=structural_page_count,
        extracted_page_count=extracted_page_count,
        warning_count=warning_count,
        issue=result.issue,
        cleanup_completed=result.cleanup_completed,
    )


def _cleanup_private_temporary_path(
    report_path: Path,
) -> None:
    temporary_path = report_path.with_name(
        "." + report_path.name + ".tmp"
    )

    try:
        if temporary_path.exists():
            temporary_path.unlink()
    except OSError:
        pass


__all__ = ("PdfIngestionOrchestratorService",)
