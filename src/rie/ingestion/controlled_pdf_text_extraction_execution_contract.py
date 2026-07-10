"""Value-only contract for controlled PDF text extraction execution."""

from __future__ import annotations

from dataclasses import dataclass

from rie.ingestion.controlled_pdf_text_extraction_contract import (
    ControlledPdfTextExtractionContractResult,
)


TEXT_ONLY_MODE = "text_only"
PRODUCT_SPEC_PDF_FIXTURE_TYPE = "product_spec_pdf"
MAX_EXTRACTED_CHARACTERS_LIMIT = 20000
MAX_PREVIEW_CHARACTERS_LIMIT = 1000


@dataclass(frozen=True)
class ControlledPdfTextExtractionExecutionContractResult:
    allowed: bool
    reason: str
    fixture_id: str
    fixture_path: str
    fixture_type: str
    extraction_mode: str
    execution_allowed: bool
    max_extracted_characters: int
    max_preview_characters: int
    allow_full_text_storage: bool
    evidence_allowed: bool
    notes: str


class ControlledPdfTextExtractionExecutionContract:
    @staticmethod
    def evaluate(
        pdf_text_contract_result: ControlledPdfTextExtractionContractResult,
        allow_execution: bool = False,
        max_extracted_characters: int = 0,
        max_preview_characters: int = 0,
        allow_full_text_storage: bool = False,
        allow_evidence_creation: bool = False,
        notes: str = "",
    ) -> ControlledPdfTextExtractionExecutionContractResult:
        if not isinstance(
            pdf_text_contract_result,
            ControlledPdfTextExtractionContractResult,
        ):
            return _blocked_result(
                reason="pdf text extraction contract result is required",
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if pdf_text_contract_result.allowed is False:
            return _blocked_from_upstream(
                reason="pdf text extraction contract is not allowed",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if not pdf_text_contract_result.fixture_id.strip():
            return _blocked_from_upstream(
                reason="fixture_id is required",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if not pdf_text_contract_result.fixture_path.strip():
            return _blocked_from_upstream(
                reason="fixture_path is required",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if (
            pdf_text_contract_result.fixture_type
            != PRODUCT_SPEC_PDF_FIXTURE_TYPE
        ):
            return _blocked_from_upstream(
                reason="fixture_type must be product_spec_pdf",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if pdf_text_contract_result.extraction_mode != TEXT_ONLY_MODE:
            return _blocked_from_upstream(
                reason="extraction_mode must be text_only",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if pdf_text_contract_result.evidence_allowed is True:
            return _blocked_from_upstream(
                reason="upstream evidence flag must remain disabled",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if allow_execution is False:
            return _blocked_from_upstream(
                reason="execution approval is required",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if max_extracted_characters <= 0:
            return _blocked_from_upstream(
                reason="max_extracted_characters must be greater than zero",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if max_extracted_characters > MAX_EXTRACTED_CHARACTERS_LIMIT:
            return _blocked_from_upstream(
                reason=(
                    "max_extracted_characters exceeds execution contract limit"
                ),
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if max_preview_characters <= 0:
            return _blocked_from_upstream(
                reason="max_preview_characters must be greater than zero",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if max_preview_characters > MAX_PREVIEW_CHARACTERS_LIMIT:
            return _blocked_from_upstream(
                reason=(
                    "max_preview_characters exceeds execution contract limit"
                ),
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if max_preview_characters > max_extracted_characters:
            return _blocked_from_upstream(
                reason=(
                    "max_preview_characters must not exceed "
                    "max_extracted_characters"
                ),
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if allow_full_text_storage is True:
            return _blocked_from_upstream(
                reason="full text storage is not allowed by this contract",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if allow_evidence_creation is True:
            return _blocked_from_upstream(
                reason="evidence creation is not allowed by this contract",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        if notes is None:
            return _blocked_from_upstream(
                reason="notes is required",
                pdf_text_contract_result=pdf_text_contract_result,
                allow_execution=allow_execution,
                max_extracted_characters=max_extracted_characters,
                max_preview_characters=max_preview_characters,
                allow_full_text_storage=allow_full_text_storage,
                notes=notes,
            )

        return ControlledPdfTextExtractionExecutionContractResult(
            allowed=True,
            reason="pdf text extraction execution contract allowed",
            fixture_id=pdf_text_contract_result.fixture_id,
            fixture_path=pdf_text_contract_result.fixture_path,
            fixture_type=pdf_text_contract_result.fixture_type,
            extraction_mode=pdf_text_contract_result.extraction_mode,
            execution_allowed=True,
            max_extracted_characters=max_extracted_characters,
            max_preview_characters=max_preview_characters,
            allow_full_text_storage=False,
            evidence_allowed=False,
            notes=notes,
        )


def _blocked_from_upstream(
    *,
    reason: str,
    pdf_text_contract_result: ControlledPdfTextExtractionContractResult,
    allow_execution: bool,
    max_extracted_characters: int,
    max_preview_characters: int,
    allow_full_text_storage: bool,
    notes: str | None,
) -> ControlledPdfTextExtractionExecutionContractResult:
    return _blocked_result(
        reason=reason,
        fixture_id=pdf_text_contract_result.fixture_id,
        fixture_path=pdf_text_contract_result.fixture_path,
        fixture_type=pdf_text_contract_result.fixture_type,
        extraction_mode=pdf_text_contract_result.extraction_mode,
        allow_execution=allow_execution,
        max_extracted_characters=max_extracted_characters,
        max_preview_characters=max_preview_characters,
        allow_full_text_storage=allow_full_text_storage,
        evidence_allowed=pdf_text_contract_result.evidence_allowed,
        notes=notes,
    )


def _blocked_result(
    *,
    reason: str,
    allow_execution: bool,
    max_extracted_characters: int,
    max_preview_characters: int,
    allow_full_text_storage: bool,
    notes: str | None,
    fixture_id: str = "",
    fixture_path: str = "",
    fixture_type: str = "",
    extraction_mode: str = "",
    evidence_allowed: bool = False,
) -> ControlledPdfTextExtractionExecutionContractResult:
    return ControlledPdfTextExtractionExecutionContractResult(
        allowed=False,
        reason=reason,
        fixture_id=fixture_id,
        fixture_path=fixture_path,
        fixture_type=fixture_type,
        extraction_mode=extraction_mode,
        execution_allowed=allow_execution,
        max_extracted_characters=max_extracted_characters,
        max_preview_characters=max_preview_characters,
        allow_full_text_storage=allow_full_text_storage,
        evidence_allowed=evidence_allowed,
        notes="" if notes is None else notes,
    )
