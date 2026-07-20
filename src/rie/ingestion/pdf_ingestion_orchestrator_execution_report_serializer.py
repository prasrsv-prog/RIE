"""Deterministic write-once serializer for Gate 4 execution reports."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from rie.ingestion.pdf_ingestion_orchestrator_contract import (
    PdfIngestionOrchestratorIssue,
)
from rie.ingestion.pdf_ingestion_orchestrator_execution_report_contract import (
    PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_FIELD_ORDER,
    PdfIngestionOrchestratorExecutionReport,
)


class PdfIngestionOrchestratorReportWriteError(RuntimeError):
    """Deterministic public serializer failure."""


class PdfIngestionOrchestratorExecutionReportSerializer:
    @staticmethod
    def to_dict(
        report: PdfIngestionOrchestratorExecutionReport,
    ) -> dict[str, Any]:
        if not isinstance(
            report,
            PdfIngestionOrchestratorExecutionReport,
        ):
            raise TypeError(
                "report must be PdfIngestionOrchestratorExecutionReport."
            )

        issue = _issue_to_dict(report.issue)

        result = {
            "contract_version": report.contract_version,
            "status": report.status.value,
            "job_id": report.job_id,
            "source_id": report.source_id,
            "source_checksum": report.source_checksum,
            "structural_page_count": report.structural_page_count,
            "extracted_page_count": report.extracted_page_count,
            "warning_count": report.warning_count,
            "issue": issue,
            "cleanup_completed": report.cleanup_completed,
        }

        if tuple(result) != (
            PDF_INGESTION_ORCHESTRATOR_EXECUTION_REPORT_FIELD_ORDER
        ):
            raise RuntimeError(
                "execution report field order is invalid."
            )

        return result

    @staticmethod
    def to_bytes(
        report: PdfIngestionOrchestratorExecutionReport,
    ) -> bytes:
        text = json.dumps(
            PdfIngestionOrchestratorExecutionReportSerializer.to_dict(
                report
            ),
            indent=2,
            ensure_ascii=False,
        )
        return (text + "\n").encode("utf-8")

    @staticmethod
    def write(
        report: PdfIngestionOrchestratorExecutionReport,
        output_location: str | Path,
    ) -> bytes:
        output_path = _validated_output_path(output_location)
        expected_bytes = (
            PdfIngestionOrchestratorExecutionReportSerializer.to_bytes(
                report
            )
        )

        parent_path = output_path.parent
        parent_created = False
        temporary_path = output_path.with_name(
            "." + output_path.name + ".tmp"
        )
        output_created = False
        temporary_created = False

        try:
            if parent_path.exists():
                if not parent_path.is_dir():
                    raise PdfIngestionOrchestratorReportWriteError(
                        "execution report parent is not a directory."
                    )
            else:
                parent_path.mkdir(parents=True, exist_ok=False)
                parent_created = True

            if output_path.exists():
                raise PdfIngestionOrchestratorReportWriteError(
                    "execution report output already exists."
                )

            if temporary_path.exists():
                raise PdfIngestionOrchestratorReportWriteError(
                    "execution report temporary path already exists."
                )

            with temporary_path.open("xb") as stream:
                temporary_created = True
                stream.write(expected_bytes)
                stream.flush()
                os.fsync(stream.fileno())

            os.link(temporary_path, output_path)
            output_created = True
            temporary_path.unlink()

            actual_bytes = output_path.read_bytes()

            if actual_bytes != expected_bytes:
                raise PdfIngestionOrchestratorReportWriteError(
                    "execution report read-back verification failed."
                )

            return actual_bytes
        except PdfIngestionOrchestratorReportWriteError:
            _cleanup_paths(
                temporary_path=temporary_path,
                temporary_created=temporary_created,
                output_path=output_path,
                output_created=output_created,
                parent_path=parent_path,
                parent_created=parent_created,
            )
            raise
        except Exception as exc:
            _cleanup_paths(
                temporary_path=temporary_path,
                temporary_created=temporary_created,
                output_path=output_path,
                output_created=output_created,
                parent_path=parent_path,
                parent_created=parent_created,
            )
            raise PdfIngestionOrchestratorReportWriteError(
                "execution report publication failed."
            ) from None


def _validated_output_path(
    output_location: object,
) -> Path:
    if not isinstance(output_location, (str, Path)):
        raise TypeError(
            "output_location must be a string or Path."
        )

    raw_value = str(output_location)

    if raw_value.strip() == "":
        raise ValueError("output_location must be non-empty.")

    if any(character in raw_value for character in "*?[]"):
        raise ValueError(
            "output_location must not contain wildcard syntax."
        )

    output_path = Path(raw_value)

    if output_path.suffix.lower() != ".json":
        raise ValueError("output_location must use the .json suffix.")

    return output_path


def _issue_to_dict(
    issue: PdfIngestionOrchestratorIssue | None,
) -> dict[str, str] | None:
    if issue is None:
        return None

    if not isinstance(issue, PdfIngestionOrchestratorIssue):
        raise TypeError(
            "issue must be PdfIngestionOrchestratorIssue or None."
        )

    return {
        "code": issue.code.value,
        "message": issue.message,
    }


def _cleanup_paths(
    *,
    temporary_path: Path,
    temporary_created: bool,
    output_path: Path,
    output_created: bool,
    parent_path: Path,
    parent_created: bool,
) -> None:
    try:
        if temporary_created and temporary_path.exists():
            temporary_path.unlink()
    except OSError:
        pass

    try:
        if output_created and output_path.exists():
            output_path.unlink()
    except OSError:
        pass

    try:
        if parent_created and parent_path.exists():
            parent_path.rmdir()
    except OSError:
        pass


__all__ = (
    "PdfIngestionOrchestratorReportWriteError",
    "PdfIngestionOrchestratorExecutionReportSerializer",
)
