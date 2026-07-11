"""Value-only contract for controlled PDF structural metadata execution."""

from __future__ import annotations

from dataclasses import dataclass

from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    PERMITTED_STRUCTURAL_FIELDS,
    PRODUCT_SPEC_PDF_FIXTURE_TYPE,
    STRUCTURAL_METADATA_ONLY_MODE,
    ControlledPdfStructuralMetadataContractResult,
)


MAX_INSPECTED_PAGES_LIMIT = 10


@dataclass(frozen=True)
class ControlledPdfStructuralMetadataExecutionContractResult:
    allowed: bool
    reason: str
    fixture_id: str
    fixture_path: str
    fixture_type: str
    inspection_mode: str
    execution_allowed: bool
    permitted_fields: tuple[str, ...]
    max_inspected_pages: int
    allow_content_extraction: bool
    allow_output_file_creation: bool
    evidence_allowed: bool
    notes: str


class ControlledPdfStructuralMetadataExecutionContract:
    @staticmethod
    def evaluate(
        metadata_contract_result: ControlledPdfStructuralMetadataContractResult,
        allow_execution: bool = False,
        max_inspected_pages: int = 0,
        allow_content_extraction: bool = False,
        allow_output_file_creation: bool = False,
        allow_evidence_creation: bool = False,
        notes: str = "",
    ) -> ControlledPdfStructuralMetadataExecutionContractResult:
        if not isinstance(
            metadata_contract_result,
            ControlledPdfStructuralMetadataContractResult,
        ):
            return _blocked_result(
                reason="structural metadata contract result is required",
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if metadata_contract_result.allowed is False:
            return _blocked_from_upstream(
                reason="structural metadata contract is not allowed",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if not metadata_contract_result.fixture_id.strip():
            return _blocked_from_upstream(
                reason="fixture_id is required",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if not metadata_contract_result.fixture_path.strip():
            return _blocked_from_upstream(
                reason="fixture_path is required",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if (
            metadata_contract_result.fixture_type
            != PRODUCT_SPEC_PDF_FIXTURE_TYPE
        ):
            return _blocked_from_upstream(
                reason="fixture_type must be product_spec_pdf",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if (
            metadata_contract_result.inspection_mode
            != STRUCTURAL_METADATA_ONLY_MODE
        ):
            return _blocked_from_upstream(
                reason="inspection_mode must be structural_metadata_only",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if (
            metadata_contract_result.permitted_fields
            != PERMITTED_STRUCTURAL_FIELDS
        ):
            return _blocked_from_upstream(
                reason="upstream permitted_fields are not approved",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if metadata_contract_result.evidence_allowed is True:
            return _blocked_from_upstream(
                reason="upstream evidence flag must remain disabled",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if allow_execution is False:
            return _blocked_from_upstream(
                reason="execution approval is required",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if max_inspected_pages <= 0:
            return _blocked_from_upstream(
                reason="max_inspected_pages must be greater than zero",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if max_inspected_pages > MAX_INSPECTED_PAGES_LIMIT:
            return _blocked_from_upstream(
                reason="max_inspected_pages exceeds execution contract limit",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if allow_content_extraction is True:
            return _blocked_from_upstream(
                reason="content extraction is not allowed by this contract",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if allow_output_file_creation is True:
            return _blocked_from_upstream(
                reason="output file creation is not allowed by this contract",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if allow_evidence_creation is True:
            return _blocked_from_upstream(
                reason="evidence creation is not allowed by this contract",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        if notes is None:
            return _blocked_from_upstream(
                reason="notes is required",
                metadata_contract_result=metadata_contract_result,
                allow_execution=allow_execution,
                max_inspected_pages=max_inspected_pages,
                allow_content_extraction=allow_content_extraction,
                allow_output_file_creation=allow_output_file_creation,
                notes=notes,
            )

        return ControlledPdfStructuralMetadataExecutionContractResult(
            allowed=True,
            reason="pdf structural metadata execution contract allowed",
            fixture_id=metadata_contract_result.fixture_id,
            fixture_path=metadata_contract_result.fixture_path,
            fixture_type=metadata_contract_result.fixture_type,
            inspection_mode=metadata_contract_result.inspection_mode,
            execution_allowed=True,
            permitted_fields=metadata_contract_result.permitted_fields,
            max_inspected_pages=max_inspected_pages,
            allow_content_extraction=False,
            allow_output_file_creation=False,
            evidence_allowed=False,
            notes=notes,
        )


def _blocked_from_upstream(
    *,
    reason: str,
    metadata_contract_result: ControlledPdfStructuralMetadataContractResult,
    allow_execution: bool,
    max_inspected_pages: int,
    allow_content_extraction: bool,
    allow_output_file_creation: bool,
    notes: str | None,
) -> ControlledPdfStructuralMetadataExecutionContractResult:
    return _blocked_result(
        reason=reason,
        fixture_id=metadata_contract_result.fixture_id,
        fixture_path=metadata_contract_result.fixture_path,
        fixture_type=metadata_contract_result.fixture_type,
        inspection_mode=metadata_contract_result.inspection_mode,
        permitted_fields=metadata_contract_result.permitted_fields,
        allow_execution=allow_execution,
        max_inspected_pages=max_inspected_pages,
        allow_content_extraction=allow_content_extraction,
        allow_output_file_creation=allow_output_file_creation,
        evidence_allowed=metadata_contract_result.evidence_allowed,
        notes=notes,
    )


def _blocked_result(
    *,
    reason: str,
    allow_execution: bool,
    max_inspected_pages: int,
    allow_content_extraction: bool,
    allow_output_file_creation: bool,
    notes: str | None,
    fixture_id: str = "",
    fixture_path: str = "",
    fixture_type: str = "",
    inspection_mode: str = "",
    permitted_fields: tuple[str, ...] = (),
    evidence_allowed: bool = False,
) -> ControlledPdfStructuralMetadataExecutionContractResult:
    return ControlledPdfStructuralMetadataExecutionContractResult(
        allowed=False,
        reason=reason,
        fixture_id=fixture_id,
        fixture_path=fixture_path,
        fixture_type=fixture_type,
        inspection_mode=inspection_mode,
        execution_allowed=allow_execution,
        permitted_fields=permitted_fields,
        max_inspected_pages=max_inspected_pages,
        allow_content_extraction=allow_content_extraction,
        allow_output_file_creation=allow_output_file_creation,
        evidence_allowed=evidence_allowed,
        notes="" if notes is None else notes,
    )