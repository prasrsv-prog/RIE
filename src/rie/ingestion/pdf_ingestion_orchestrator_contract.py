"""Immutable contracts for deterministic Gate 4 PDF ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Final

from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction
from rie.ingestion.controlled_pdf_structural_metadata_result_contract import (
    ControlledPdfStructuralMetadataResultContractResult,
)
from rie.ingestion.controlled_source_admission_job_contract import IngestionJob


PDF_INGESTION_ORCHESTRATOR_CONTRACT_VERSION: Final = (
    "pdf_ingestion_orchestrator_contract_v1"
)
PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION: Final = (
    "pdf_ingestion_orchestrator_result_contract_v1"
)

PDF_INGESTION_ORCHESTRATOR_REQUEST_FIELD_ORDER: Final = (
    "job",
    "execution_report_location",
)
PDF_INGESTION_ORCHESTRATOR_RESULT_FIELD_ORDER: Final = (
    "contract_version",
    "status",
    "job_id",
    "source_id",
    "source_path",
    "source_checksum",
    "structural_metadata",
    "page_extractions",
    "issue",
    "execution_report_location",
    "cleanup_completed",
)

_WILDCARD_CHARACTERS = frozenset("*?[]")


class PdfIngestionOrchestratorStatus(Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class PdfIngestionOrchestratorIssueCode(Enum):
    SOURCE_MISSING = "source_missing"
    SOURCE_NOT_FILE = "source_not_file"
    SOURCE_CHECKSUM_MISMATCH = "source_checksum_mismatch"
    UNSUPPORTED_SOURCE = "unsupported_source"
    ENCRYPTED_PDF = "encrypted_pdf"
    PARSER_FAILURE = "parser_failure"
    STRUCTURAL_METADATA_FAILURE = "structural_metadata_failure"
    TEXT_EXTRACTION_FAILURE = "text_extraction_failure"
    OUTPUT_FAILURE = "output_failure"
    AUTHORITY_REJECTED = "authority_rejected"


@dataclass(frozen=True)
class PdfIngestionOrchestratorIssue:
    code: PdfIngestionOrchestratorIssueCode
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.code, PdfIngestionOrchestratorIssueCode):
            raise TypeError(
                "code must be PdfIngestionOrchestratorIssueCode."
            )
        _require_non_empty_string(self.message, "message")


@dataclass(frozen=True)
class PdfIngestionOrchestratorRequest:
    job: IngestionJob
    execution_report_location: str | Path

    def __post_init__(self) -> None:
        if not isinstance(self.job, IngestionJob):
            raise TypeError("job must be IngestionJob.")

        _require_path_value(
            self.execution_report_location,
            "execution_report_location",
        )
        location = str(self.execution_report_location)

        if any(character in location for character in _WILDCARD_CHARACTERS):
            raise ValueError(
                "execution_report_location must not contain wildcard syntax."
            )

        if Path(location).suffix.lower() != ".json":
            raise ValueError(
                "execution_report_location must use the .json suffix."
            )

        if location == self.job.source_path:
            raise ValueError(
                "execution_report_location and source_path must differ."
            )

        if location == self.job.output_location:
            raise ValueError(
                "execution_report_location and Gate 3 output_location "
                "must differ."
            )


@dataclass(frozen=True)
class PdfIngestionOrchestratorResult:
    contract_version: str
    status: PdfIngestionOrchestratorStatus
    job_id: str
    source_id: str
    source_path: str
    source_checksum: str
    structural_metadata: (
        ControlledPdfStructuralMetadataResultContractResult | None
    )
    page_extractions: tuple[PdfPageTextExtraction, ...]
    issue: PdfIngestionOrchestratorIssue | None
    execution_report_location: str
    cleanup_completed: bool

    def __post_init__(self) -> None:
        if self.contract_version != (
            PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("contract_version is unsupported.")

        if not isinstance(self.status, PdfIngestionOrchestratorStatus):
            raise TypeError(
                "status must be PdfIngestionOrchestratorStatus."
            )

        for field_name in (
            "job_id",
            "source_id",
            "source_path",
            "source_checksum",
            "execution_report_location",
        ):
            _require_non_empty_string(
                getattr(self, field_name),
                field_name,
            )

        if not isinstance(self.cleanup_completed, bool):
            raise TypeError("cleanup_completed must be a boolean.")

        if self.cleanup_completed is not True:
            raise ValueError("cleanup_completed must be true.")

        if not isinstance(self.page_extractions, tuple):
            raise TypeError("page_extractions must be a tuple.")

        _validate_page_extractions(
            page_extractions=self.page_extractions,
            source_path=self.source_path,
        )

        if self.status is PdfIngestionOrchestratorStatus.COMPLETED:
            if not isinstance(
                self.structural_metadata,
                ControlledPdfStructuralMetadataResultContractResult,
            ):
                raise ValueError(
                    "completed result must contain structural_metadata."
                )

            if self.structural_metadata.allowed is not True:
                raise ValueError(
                    "completed structural_metadata must be allowed."
                )

            if self.structural_metadata.encrypted is True:
                raise ValueError(
                    "completed structural_metadata must not be encrypted."
                )

            if self.structural_metadata.inspection_status not in {
                "inspected",
                "bounded",
            }:
                raise ValueError(
                    "completed structural_metadata status is unsupported."
                )

            if (
                self.structural_metadata.page_count
                != len(self.page_extractions)
            ):
                raise ValueError(
                    "completed page extraction count must match "
                    "structural page_count."
                )

            if self.issue is not None:
                raise ValueError(
                    "completed result must not contain an issue."
                )
        else:
            if self.structural_metadata is not None:
                raise ValueError(
                    "failed result must not contain structural_metadata."
                )

            if self.page_extractions:
                raise ValueError(
                    "failed result must not contain page_extractions."
                )

            if not isinstance(
                self.issue,
                PdfIngestionOrchestratorIssue,
            ):
                raise ValueError(
                    "failed result must contain one issue."
                )


def freeze_page_extractions(
    values: object,
) -> tuple[PdfPageTextExtraction, ...]:
    if not isinstance(values, (list, tuple)):
        raise TypeError("page extraction values must be a list or tuple.")

    frozen = []

    for value in values:
        if not isinstance(value, PdfPageTextExtraction):
            raise TypeError(
                "page extraction values must contain "
                "PdfPageTextExtraction instances."
            )

        if not isinstance(value.warnings, (list, tuple)):
            raise TypeError("page extraction warnings must be a sequence.")

        warnings = tuple(value.warnings)

        if any(not isinstance(warning, str) for warning in warnings):
            raise TypeError(
                "page extraction warnings must contain strings."
            )

        frozen.append(
            PdfPageTextExtraction(
                source_path=value.source_path,
                size_bytes=value.size_bytes,
                page_number=value.page_number,
                extraction_index=value.extraction_index,
                extraction_method=value.extraction_method,
                content=value.content,
                warnings=warnings,
            )
        )

    return tuple(frozen)


def completed_result(
    *,
    job: IngestionJob,
    structural_metadata:
        ControlledPdfStructuralMetadataResultContractResult,
    page_extractions: tuple[PdfPageTextExtraction, ...],
    execution_report_location: str,
) -> PdfIngestionOrchestratorResult:
    return PdfIngestionOrchestratorResult(
        contract_version=(
            PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION
        ),
        status=PdfIngestionOrchestratorStatus.COMPLETED,
        job_id=job.job_id,
        source_id=job.source_id,
        source_path=job.source_path,
        source_checksum=job.source_checksum,
        structural_metadata=structural_metadata,
        page_extractions=page_extractions,
        issue=None,
        execution_report_location=execution_report_location,
        cleanup_completed=True,
    )


def failed_result(
    *,
    job: IngestionJob,
    code: PdfIngestionOrchestratorIssueCode,
    message: str,
    execution_report_location: str,
) -> PdfIngestionOrchestratorResult:
    return PdfIngestionOrchestratorResult(
        contract_version=(
            PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION
        ),
        status=PdfIngestionOrchestratorStatus.FAILED,
        job_id=job.job_id,
        source_id=job.source_id,
        source_path=job.source_path,
        source_checksum=job.source_checksum,
        structural_metadata=None,
        page_extractions=(),
        issue=PdfIngestionOrchestratorIssue(
            code=code,
            message=message,
        ),
        execution_report_location=execution_report_location,
        cleanup_completed=True,
    )


def _validate_page_extractions(
    *,
    page_extractions: tuple[PdfPageTextExtraction, ...],
    source_path: str,
) -> None:
    expected_page_number = 1
    expected_extraction_index = 0

    for extraction in page_extractions:
        if not isinstance(extraction, PdfPageTextExtraction):
            raise TypeError(
                "page_extractions must contain PdfPageTextExtraction."
            )

        if extraction.source_path != source_path:
            raise ValueError(
                "page extraction source_path must match result source_path."
            )

        if (
            not isinstance(extraction.size_bytes, int)
            or isinstance(extraction.size_bytes, bool)
            or extraction.size_bytes < 0
        ):
            raise ValueError(
                "page extraction size_bytes must be a non-negative integer."
            )

        if extraction.page_number != expected_page_number:
            raise ValueError(
                "page numbers must form a contiguous one-based sequence."
            )

        if extraction.extraction_index != expected_extraction_index:
            raise ValueError(
                "extraction indices must form a contiguous zero-based "
                "sequence."
            )

        _require_non_empty_string(
            extraction.extraction_method,
            "extraction_method",
        )

        if not isinstance(extraction.content, str):
            raise TypeError("page extraction content must be a string.")

        if not isinstance(extraction.warnings, tuple):
            raise TypeError(
                "frozen page extraction warnings must be a tuple."
            )

        if any(
            not isinstance(warning, str)
            for warning in extraction.warnings
        ):
            raise TypeError(
                "page extraction warnings must contain strings."
            )

        expected_page_number += 1
        expected_extraction_index += 1


def _require_non_empty_string(
    value: object,
    field_name: str,
) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")

    if value.strip() == "":
        raise ValueError(f"{field_name} must be non-empty.")


def _require_path_value(
    value: object,
    field_name: str,
) -> None:
    if not isinstance(value, (str, Path)):
        raise TypeError(f"{field_name} must be a string or Path.")

    if str(value).strip() == "":
        raise ValueError(f"{field_name} must be non-empty.")


__all__ = (
    "PDF_INGESTION_ORCHESTRATOR_CONTRACT_VERSION",
    "PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION",
    "PDF_INGESTION_ORCHESTRATOR_REQUEST_FIELD_ORDER",
    "PDF_INGESTION_ORCHESTRATOR_RESULT_FIELD_ORDER",
    "PdfIngestionOrchestratorStatus",
    "PdfIngestionOrchestratorIssueCode",
    "PdfIngestionOrchestratorIssue",
    "PdfIngestionOrchestratorRequest",
    "PdfIngestionOrchestratorResult",
    "freeze_page_extractions",
    "completed_result",
    "failed_result",
)
