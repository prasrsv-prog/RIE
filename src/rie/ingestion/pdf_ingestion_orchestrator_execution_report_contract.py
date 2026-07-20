"""Frozen deterministic execution-report contract for Gate 4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from rie.ingestion.pdf_ingestion_orchestrator_contract import (
    PdfIngestionOrchestratorIssue,
    PdfIngestionOrchestratorStatus,
)


PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_CONTRACT_VERSION: Final = (
    "pdf_ingestion_orchestrator_execution_report_contract_v1"
)

PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_FIELD_ORDER: Final = (
    "contract_version",
    "status",
    "job_id",
    "source_id",
    "source_checksum",
    "structural_page_count",
    "extracted_page_count",
    "warning_count",
    "issue",
    "cleanup_completed",
)


@dataclass(frozen=True)
class PdfIngestionOrchestratorExecutionReport:
    contract_version: str
    status: PdfIngestionOrchestratorStatus
    job_id: str
    source_id: str
    source_checksum: str
    structural_page_count: int
    extracted_page_count: int
    warning_count: int
    issue: PdfIngestionOrchestratorIssue | None
    cleanup_completed: bool

    def __post_init__(self) -> None:
        if self.contract_version != (
            PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_CONTRACT_VERSION
        ):
            raise ValueError("contract_version is unsupported.")

        if not isinstance(self.status, PdfIngestionOrchestratorStatus):
            raise TypeError(
                "status must be PdfIngestionOrchestratorStatus."
            )

        for field_name in (
            "job_id",
            "source_id",
            "source_checksum",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string.")

            if value.strip() == "":
                raise ValueError(f"{field_name} must be non-empty.")

        for field_name in (
            "structural_page_count",
            "extracted_page_count",
            "warning_count",
        ):
            value = getattr(self, field_name)

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
            ):
                raise TypeError(f"{field_name} must be an integer.")

            if value < 0:
                raise ValueError(
                    f"{field_name} must not be negative."
                )

        if not isinstance(self.cleanup_completed, bool):
            raise TypeError("cleanup_completed must be a boolean.")

        if self.cleanup_completed is not True:
            raise ValueError("cleanup_completed must be true.")

        if self.status is PdfIngestionOrchestratorStatus.COMPLETED:
            if self.issue is not None:
                raise ValueError(
                    "completed report must not contain an issue."
                )

            if (
                self.structural_page_count
                != self.extracted_page_count
            ):
                raise ValueError(
                    "completed report page counts must match."
                )
        else:
            if not isinstance(
                self.issue,
                PdfIngestionOrchestratorIssue,
            ):
                raise ValueError(
                    "failed report must contain one issue."
                )

            if self.extracted_page_count != 0:
                raise ValueError(
                    "failed report must have zero extracted_page_count."
                )


__all__ = (
    "PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_CONTRACT_VERSION",
    "PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_FIELD_ORDER",
    "PdfIngestionOrchestratorExecutionReport",
)
