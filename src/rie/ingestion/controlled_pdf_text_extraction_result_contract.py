"""Value-only contract for controlled PDF text extraction results."""

from __future__ import annotations

from dataclasses import dataclass

from rie.ingestion.controlled_pdf_text_extraction_execution_contract import (
    ControlledPdfTextExtractionExecutionContractResult,
)


TEXT_ONLY_MODE = "text_only"
PRODUCT_SPEC_PDF_FIXTURE_TYPE = "product_spec_pdf"
MAX_PREVIEW_CHARACTERS_LIMIT = 1000

ALLOWED_EXTRACTION_STATUSES = frozenset(
    {
        "not_run",
        "extracted",
        "empty",
        "truncated",
        "parser_error",
        "encrypted",
        "unreadable",
        "unsupported_pdf",
        "blocked",
    }
)
SUCCESSFUL_EXTRACTION_STATUSES = frozenset(
    {
        "extracted",
        "empty",
        "truncated",
        "not_run",
    }
)
ERROR_EXTRACTION_STATUSES = frozenset(
    {
        "parser_error",
        "encrypted",
        "unreadable",
        "unsupported_pdf",
        "blocked",
    }
)


@dataclass(frozen=True)
class ControlledPdfTextExtractionResultInput:
    fixture_id: str
    source_label: str
    fixture_path: str
    fixture_type: str
    extraction_mode: str
    extraction_status: str
    text_length: int
    text_preview: str
    extracted_text: str
    extracted_text_included: bool
    max_extracted_characters: int
    max_preview_characters: int
    truncated: bool
    extraction_error: str
    evidence_allowed: bool
    notes: str


@dataclass(frozen=True)
class ControlledPdfTextExtractionResultContractResult:
    allowed: bool
    reason: str
    fixture_id: str
    source_label: str
    fixture_path: str
    fixture_type: str
    extraction_mode: str
    extraction_status: str
    text_length: int
    text_preview: str
    extracted_text_included: bool
    max_extracted_characters: int
    max_preview_characters: int
    truncated: bool
    extraction_error: str
    evidence_allowed: bool
    notes: str


class ControlledPdfTextExtractionResultContract:
    @staticmethod
    def evaluate(
        execution_contract_result: ControlledPdfTextExtractionExecutionContractResult,
        result_input: ControlledPdfTextExtractionResultInput,
    ) -> ControlledPdfTextExtractionResultContractResult:
        if not isinstance(
            execution_contract_result,
            ControlledPdfTextExtractionExecutionContractResult,
        ):
            return _blocked_result(
                reason="execution contract result is required",
            )

        if execution_contract_result.allowed is False:
            return _blocked_from_execution(
                reason="execution contract is not allowed",
                execution_contract_result=execution_contract_result,
            )

        if execution_contract_result.execution_allowed is False:
            return _blocked_from_execution(
                reason="execution approval is required",
                execution_contract_result=execution_contract_result,
            )

        if execution_contract_result.evidence_allowed is True:
            return _blocked_from_execution(
                reason="upstream evidence flag must remain disabled",
                execution_contract_result=execution_contract_result,
            )

        if execution_contract_result.allow_full_text_storage is True:
            return _blocked_from_execution(
                reason="full text storage must remain disabled",
                execution_contract_result=execution_contract_result,
            )

        if not isinstance(result_input, ControlledPdfTextExtractionResultInput):
            return _blocked_from_execution(
                reason="result input is required",
                execution_contract_result=execution_contract_result,
            )

        if result_input.fixture_id != execution_contract_result.fixture_id:
            return _blocked_from_input(
                reason="fixture_id mismatch",
                result_input=result_input,
            )

        if result_input.fixture_path != execution_contract_result.fixture_path:
            return _blocked_from_input(
                reason="fixture_path mismatch",
                result_input=result_input,
            )

        if result_input.fixture_type != execution_contract_result.fixture_type:
            return _blocked_from_input(
                reason="fixture_type mismatch",
                result_input=result_input,
            )

        if (
            result_input.extraction_mode
            != execution_contract_result.extraction_mode
        ):
            return _blocked_from_input(
                reason="extraction_mode mismatch",
                result_input=result_input,
            )

        if not result_input.fixture_id.strip():
            return _blocked_from_input(
                reason="fixture_id is required",
                result_input=result_input,
            )

        if not result_input.source_label.strip():
            return _blocked_from_input(
                reason="source_label is required",
                result_input=result_input,
            )

        if not result_input.fixture_path.strip():
            return _blocked_from_input(
                reason="fixture_path is required",
                result_input=result_input,
            )

        if result_input.fixture_type != PRODUCT_SPEC_PDF_FIXTURE_TYPE:
            return _blocked_from_input(
                reason="fixture_type must be product_spec_pdf",
                result_input=result_input,
            )

        if result_input.extraction_mode != TEXT_ONLY_MODE:
            return _blocked_from_input(
                reason="extraction_mode must be text_only",
                result_input=result_input,
            )

        if result_input.extraction_status not in ALLOWED_EXTRACTION_STATUSES:
            return _blocked_from_input(
                reason="unsupported extraction_status",
                result_input=result_input,
            )

        if result_input.text_length < 0:
            return _blocked_from_input(
                reason="text_length must not be negative",
                result_input=result_input,
            )

        if (
            result_input.text_length
            > execution_contract_result.max_extracted_characters
        ):
            return _blocked_from_input(
                reason="text_length exceeds extraction limit",
                result_input=result_input,
            )

        if (
            result_input.max_extracted_characters
            != execution_contract_result.max_extracted_characters
        ):
            return _blocked_from_input(
                reason="max_extracted_characters mismatch",
                result_input=result_input,
            )

        if (
            result_input.max_preview_characters
            != execution_contract_result.max_preview_characters
        ):
            return _blocked_from_input(
                reason="max_preview_characters mismatch",
                result_input=result_input,
            )

        if result_input.max_preview_characters <= 0:
            return _blocked_from_input(
                reason="max_preview_characters must be greater than zero",
                result_input=result_input,
            )

        if result_input.max_preview_characters > MAX_PREVIEW_CHARACTERS_LIMIT:
            return _blocked_from_input(
                reason=(
                    "max_preview_characters exceeds result contract limit"
                ),
                result_input=result_input,
            )

        if len(result_input.text_preview) > result_input.max_preview_characters:
            return _blocked_from_input(
                reason="text_preview exceeds preview limit",
                result_input=result_input,
            )

        if result_input.extracted_text != "":
            return _blocked_from_input(
                reason=(
                    "extracted_text storage is not allowed by this contract"
                ),
                result_input=result_input,
            )

        if result_input.extracted_text_included is True:
            return _blocked_from_input(
                reason="extracted_text_included must remain false",
                result_input=result_input,
            )

        if result_input.evidence_allowed is True:
            return _blocked_from_input(
                reason="evidence creation is not allowed by this contract",
                result_input=result_input,
            )

        if result_input.notes is None:
            return _blocked_from_input(
                reason="notes is required",
                result_input=result_input,
            )

        if result_input.extraction_error is None:
            return _blocked_from_input(
                reason="extraction_error is required",
                result_input=result_input,
            )

        if (
            result_input.extraction_status in SUCCESSFUL_EXTRACTION_STATUSES
            and result_input.extraction_error != ""
        ):
            return _blocked_from_input(
                reason="successful status must not have extraction_error",
                result_input=result_input,
            )

        if (
            result_input.extraction_status in ERROR_EXTRACTION_STATUSES
            and not result_input.extraction_error.strip()
        ):
            return _blocked_from_input(
                reason="error status requires extraction_error",
                result_input=result_input,
            )

        if result_input.extraction_status == "extracted":
            if result_input.text_length <= 0:
                return _blocked_from_input(
                    reason="extracted status requires positive text_length",
                    result_input=result_input,
                )

            if result_input.truncated is True:
                return _blocked_from_input(
                    reason="extracted status must not be truncated",
                    result_input=result_input,
                )

        if result_input.extraction_status == "empty":
            if result_input.text_length != 0:
                return _blocked_from_input(
                    reason="empty status requires zero text_length",
                    result_input=result_input,
                )

            if result_input.text_preview != "":
                return _blocked_from_input(
                    reason="empty status requires empty text_preview",
                    result_input=result_input,
                )

            if result_input.truncated is True:
                return _blocked_from_input(
                    reason="empty status must not be truncated",
                    result_input=result_input,
                )

        if result_input.extraction_status == "truncated":
            if (
                result_input.text_length
                != execution_contract_result.max_extracted_characters
            ):
                return _blocked_from_input(
                    reason="truncated status requires max text_length",
                    result_input=result_input,
                )

            if result_input.truncated is False:
                return _blocked_from_input(
                    reason="truncated status requires truncated true",
                    result_input=result_input,
                )

        if result_input.extraction_status == "not_run":
            if result_input.text_length != 0:
                return _blocked_from_input(
                    reason="not_run status requires zero text_length",
                    result_input=result_input,
                )

            if result_input.text_preview != "":
                return _blocked_from_input(
                    reason="not_run status requires empty text_preview",
                    result_input=result_input,
                )

            if result_input.truncated is True:
                return _blocked_from_input(
                    reason="not_run status must not be truncated",
                    result_input=result_input,
                )

        if result_input.extraction_status in ERROR_EXTRACTION_STATUSES:
            if result_input.text_length != 0:
                return _blocked_from_input(
                    reason="error status requires zero text_length",
                    result_input=result_input,
                )

            if result_input.text_preview != "":
                return _blocked_from_input(
                    reason="error status requires empty text_preview",
                    result_input=result_input,
                )

            if result_input.truncated is True:
                return _blocked_from_input(
                    reason="error status must not be truncated",
                    result_input=result_input,
                )

        return ControlledPdfTextExtractionResultContractResult(
            allowed=True,
            reason="pdf text extraction result contract allowed",
            fixture_id=result_input.fixture_id,
            source_label=result_input.source_label,
            fixture_path=result_input.fixture_path,
            fixture_type=result_input.fixture_type,
            extraction_mode=result_input.extraction_mode,
            extraction_status=result_input.extraction_status,
            text_length=result_input.text_length,
            text_preview=result_input.text_preview,
            extracted_text_included=result_input.extracted_text_included,
            max_extracted_characters=result_input.max_extracted_characters,
            max_preview_characters=result_input.max_preview_characters,
            truncated=result_input.truncated,
            extraction_error=result_input.extraction_error,
            evidence_allowed=False,
            notes=result_input.notes,
        )


def _blocked_from_execution(
    *,
    reason: str,
    execution_contract_result: ControlledPdfTextExtractionExecutionContractResult,
) -> ControlledPdfTextExtractionResultContractResult:
    return _blocked_result(
        reason=reason,
        fixture_id=execution_contract_result.fixture_id,
        fixture_path=execution_contract_result.fixture_path,
        fixture_type=execution_contract_result.fixture_type,
        extraction_mode=execution_contract_result.extraction_mode,
        max_extracted_characters=(
            execution_contract_result.max_extracted_characters
        ),
        max_preview_characters=execution_contract_result.max_preview_characters,
        evidence_allowed=execution_contract_result.evidence_allowed,
        notes=execution_contract_result.notes,
    )


def _blocked_from_input(
    *,
    reason: str,
    result_input: ControlledPdfTextExtractionResultInput,
) -> ControlledPdfTextExtractionResultContractResult:
    return _blocked_result(
        reason=reason,
        fixture_id=result_input.fixture_id,
        source_label=result_input.source_label,
        fixture_path=result_input.fixture_path,
        fixture_type=result_input.fixture_type,
        extraction_mode=result_input.extraction_mode,
        extraction_status=result_input.extraction_status,
        text_length=result_input.text_length,
        text_preview=result_input.text_preview,
        extracted_text_included=result_input.extracted_text_included,
        max_extracted_characters=result_input.max_extracted_characters,
        max_preview_characters=result_input.max_preview_characters,
        truncated=result_input.truncated,
        extraction_error=(
            "" if result_input.extraction_error is None
            else result_input.extraction_error
        ),
        evidence_allowed=result_input.evidence_allowed,
        notes="" if result_input.notes is None else result_input.notes,
    )


def _blocked_result(
    *,
    reason: str,
    fixture_id: str = "",
    source_label: str = "",
    fixture_path: str = "",
    fixture_type: str = "",
    extraction_mode: str = "",
    extraction_status: str = "",
    text_length: int = 0,
    text_preview: str = "",
    extracted_text_included: bool = False,
    max_extracted_characters: int = 0,
    max_preview_characters: int = 0,
    truncated: bool = False,
    extraction_error: str = "",
    evidence_allowed: bool = False,
    notes: str = "",
) -> ControlledPdfTextExtractionResultContractResult:
    return ControlledPdfTextExtractionResultContractResult(
        allowed=False,
        reason=reason,
        fixture_id=fixture_id,
        source_label=source_label,
        fixture_path=fixture_path,
        fixture_type=fixture_type,
        extraction_mode=extraction_mode,
        extraction_status=extraction_status,
        text_length=text_length,
        text_preview=text_preview,
        extracted_text_included=extracted_text_included,
        max_extracted_characters=max_extracted_characters,
        max_preview_characters=max_preview_characters,
        truncated=truncated,
        extraction_error=extraction_error,
        evidence_allowed=evidence_allowed,
        notes=notes,
    )
