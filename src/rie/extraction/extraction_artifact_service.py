"""Value-only Gate 5 Extraction Artifact construction service."""

from __future__ import annotations

from dataclasses import replace

from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_CONTRACT_VERSION,
    EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION,
    ExtractionArtifact,
    ExtractionArtifactContractError,
    ExtractionArtifactIssueCode,
    ExtractionArtifactPageExtraction,
    ExtractionArtifactStructuralMetadata,
    ExtractionArtifactStructuralPage,
    raise_artifact_error,
)
from rie.extraction.extraction_artifact_serializer import (
    ExtractionArtifactSerializer,
)
from rie.ingestion.controlled_pdf_structural_metadata_result_contract import (
    ControlledPdfStructuralMetadataPageItem,
    ControlledPdfStructuralMetadataResultContractResult,
)
from rie.ingestion.pdf_ingestion_orchestrator_contract import (
    PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION,
    PdfIngestionOrchestratorResult,
    PdfIngestionOrchestratorStatus,
)


class ExtractionArtifactService:
    @staticmethod
    def from_completed_result(
        result: PdfIngestionOrchestratorResult,
    ) -> ExtractionArtifact:
        if type(result) is not PdfIngestionOrchestratorResult:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_UPSTREAM_RESULT
            )
        if (
            result.contract_version
            != PDF_INGESTION_ORCHESTRATOR_RESULT_CONTRACT_VERSION
            or result.status is not PdfIngestionOrchestratorStatus.COMPLETED
            or result.issue is not None
            or result.cleanup_completed is not True
            or not isinstance(
                result.structural_metadata,
                ControlledPdfStructuralMetadataResultContractResult,
            )
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_UPSTREAM_RESULT
            )

        try:
            structural = _copy_structural_metadata(
                result.structural_metadata
            )
            page_extractions = tuple(
                ExtractionArtifactPageExtraction(
                    source_path=page.source_path,
                    size_bytes=page.size_bytes,
                    page_number=page.page_number,
                    extraction_index=page.extraction_index,
                    extraction_method=page.extraction_method,
                    content=page.content,
                    warnings=tuple(page.warnings),
                )
                for page in result.page_extractions
            )

            provisional = ExtractionArtifact(
                contract_version=EXTRACTION_ARTIFACT_CONTRACT_VERSION,
                artifact_id="0" * 64,
                upstream_contract_version=(
                    EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION
                ),
                upstream_status=result.status.value,
                job_id=result.job_id,
                source_id=result.source_id,
                source_path=result.source_path,
                source_checksum=result.source_checksum,
                structural_metadata=structural,
                page_extractions=page_extractions,
                execution_report_location=(
                    result.execution_report_location
                ),
                cleanup_completed=result.cleanup_completed,
            )
            artifact_id = (
                ExtractionArtifactSerializer.derive_artifact_id(
                    provisional
                )
            )
            return replace(provisional, artifact_id=artifact_id)
        except ExtractionArtifactContractError:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_UPSTREAM_RESULT
            )


def _copy_structural_metadata(
    value: ControlledPdfStructuralMetadataResultContractResult,
) -> ExtractionArtifactStructuralMetadata:
    pages = tuple(
        _copy_structural_page(page)
        for page in value.page_details
    )
    return ExtractionArtifactStructuralMetadata(
        allowed=value.allowed,
        reason=value.reason,
        fixture_id=value.fixture_id,
        source_label=value.source_label,
        fixture_path=value.fixture_path,
        fixture_type=value.fixture_type,
        inspection_mode=value.inspection_mode,
        inspection_status=value.inspection_status,
        encrypted=value.encrypted,
        page_count=value.page_count,
        inspected_page_count=value.inspected_page_count,
        page_details_truncated=value.page_details_truncated,
        page_details=pages,
        max_inspected_pages=value.max_inspected_pages,
        inspection_error=value.inspection_error,
        evidence_allowed=value.evidence_allowed,
        notes=value.notes,
    )


def _copy_structural_page(
    value: ControlledPdfStructuralMetadataPageItem,
) -> ExtractionArtifactStructuralPage:
    if not isinstance(
        value,
        ControlledPdfStructuralMetadataPageItem,
    ):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_UPSTREAM_RESULT
        )
    return ExtractionArtifactStructuralPage(
        page_index=value.page_index,
        width_points=value.width_points,
        height_points=value.height_points,
        rotation_degrees=value.rotation_degrees,
        inspection_status=value.inspection_status,
    )


__all__ = ("ExtractionArtifactService",)
