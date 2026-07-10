"""Controlled implementation skeleton for explicit PDF text extraction."""

from __future__ import annotations

from dataclasses import dataclass

from rie.ingestion.controlled_pdf_text_extraction_execution_contract import (
    ControlledPdfTextExtractionExecutionContractResult,
)
from rie.ingestion.controlled_pdf_text_extraction_result_contract import (
    ControlledPdfTextExtractionResultContract,
    ControlledPdfTextExtractionResultContractResult,
    ControlledPdfTextExtractionResultInput,
)

try:
    from pypdf import PdfReader as _PDF_READER
except ImportError:
    _PDF_READER = None


TEXT_ONLY_MODE = "text_only"
PRODUCT_SPEC_PDF_FIXTURE_TYPE = "product_spec_pdf"
UNSUPPORTED_PARSER_ERROR = "pdf parser dependency is unavailable"
UNREADABLE_ERROR = "pdf file is unreadable"
PARSER_ERROR = "pdf parser error"
ENCRYPTED_ERROR = "pdf is encrypted"
SAFETY_CHECK_ERROR = "implementation safety checks failed"
REQUEST_REQUIRED_ERROR = "implementation request is required"


@dataclass(frozen=True)
class ControlledPdfTextExtractionImplementationRequest:
    execution_contract_result: ControlledPdfTextExtractionExecutionContractResult
    fixture_id: str
    source_label: str
    fixture_path: str
    fixture_type: str
    extraction_mode: str
    notes: str


class ControlledPdfTextExtractionImplementation:
    @staticmethod
    def extract(
        request: ControlledPdfTextExtractionImplementationRequest,
    ) -> ControlledPdfTextExtractionResultContractResult:
        if not isinstance(
            request,
            ControlledPdfTextExtractionImplementationRequest,
        ):
            return _invalid_request_result()

        blocked_result = _pre_read_contract_result(request)
        if blocked_result is not None:
            return blocked_result

        if _PDF_READER is None:
            return _evaluate_status(
                request=request,
                extraction_status="unsupported_pdf",
                extraction_error=UNSUPPORTED_PARSER_ERROR,
            )

        try:
            extracted_text = _extract_text_from_pdf(request.fixture_path)
        except _EncryptedPdfError:
            return _evaluate_status(
                request=request,
                extraction_status="encrypted",
                extraction_error=ENCRYPTED_ERROR,
            )
        except OSError:
            return _evaluate_status(
                request=request,
                extraction_status="unreadable",
                extraction_error=UNREADABLE_ERROR,
            )
        except Exception:
            return _evaluate_status(
                request=request,
                extraction_status="parser_error",
                extraction_error=PARSER_ERROR,
            )

        return _evaluate_extracted_text(
            request=request,
            extracted_text=extracted_text,
        )


class _EncryptedPdfError(Exception):
    pass


def _pre_read_contract_result(
    request: ControlledPdfTextExtractionImplementationRequest,
) -> ControlledPdfTextExtractionResultContractResult | None:
    execution_contract_result = request.execution_contract_result
    result_input = _result_input(
        request=request,
        extraction_status="blocked",
        extraction_error=SAFETY_CHECK_ERROR,
    )

    if not isinstance(
        execution_contract_result,
        ControlledPdfTextExtractionExecutionContractResult,
    ):
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if execution_contract_result.allowed is False:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if execution_contract_result.execution_allowed is False:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if execution_contract_result.evidence_allowed is True:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if execution_contract_result.allow_full_text_storage is True:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if request.fixture_id != execution_contract_result.fixture_id:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if request.fixture_path != execution_contract_result.fixture_path:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if request.fixture_type != execution_contract_result.fixture_type:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if request.extraction_mode != execution_contract_result.extraction_mode:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if request.fixture_type != PRODUCT_SPEC_PDF_FIXTURE_TYPE:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if request.extraction_mode != TEXT_ONLY_MODE:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if execution_contract_result.max_extracted_characters <= 0:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    if execution_contract_result.max_preview_characters <= 0:
        return ControlledPdfTextExtractionResultContract.evaluate(
            execution_contract_result=execution_contract_result,
            result_input=result_input,
        )

    return None


def _extract_text_from_pdf(fixture_path: str) -> str:
    if _PDF_READER is None:
        return ""

    reader = _PDF_READER(fixture_path)
    if reader.is_encrypted:
        raise _EncryptedPdfError

    page_texts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text:
            page_texts.append(page_text)

    return "\n".join(page_texts)


def _evaluate_extracted_text(
    *,
    request: ControlledPdfTextExtractionImplementationRequest,
    extracted_text: str,
) -> ControlledPdfTextExtractionResultContractResult:
    execution_contract_result = request.execution_contract_result
    max_extracted_characters = (
        execution_contract_result.max_extracted_characters
    )
    bounded_text = extracted_text[:max_extracted_characters]
    truncated = len(extracted_text) > max_extracted_characters
    text_length = len(bounded_text)

    if truncated:
        extraction_status = "truncated"
    elif text_length > 0:
        extraction_status = "extracted"
    else:
        extraction_status = "empty"

    return _evaluate_status(
        request=request,
        extraction_status=extraction_status,
        text_length=text_length,
        text_preview=bounded_text[
            : execution_contract_result.max_preview_characters
        ],
        truncated=truncated,
    )


def _evaluate_status(
    *,
    request: ControlledPdfTextExtractionImplementationRequest,
    extraction_status: str,
    text_length: int = 0,
    text_preview: str = "",
    truncated: bool = False,
    extraction_error: str = "",
) -> ControlledPdfTextExtractionResultContractResult:
    return ControlledPdfTextExtractionResultContract.evaluate(
        execution_contract_result=request.execution_contract_result,
        result_input=_result_input(
            request=request,
            extraction_status=extraction_status,
            text_length=text_length,
            text_preview=text_preview,
            truncated=truncated,
            extraction_error=extraction_error,
        ),
    )


def _result_input(
    *,
    request: ControlledPdfTextExtractionImplementationRequest,
    extraction_status: str,
    text_length: int = 0,
    text_preview: str = "",
    truncated: bool = False,
    extraction_error: str = "",
) -> ControlledPdfTextExtractionResultInput:
    execution_contract_result = request.execution_contract_result
    return ControlledPdfTextExtractionResultInput(
        fixture_id=request.fixture_id,
        source_label=request.source_label,
        fixture_path=request.fixture_path,
        fixture_type=request.fixture_type,
        extraction_mode=request.extraction_mode,
        extraction_status=extraction_status,
        text_length=text_length,
        text_preview=text_preview,
        extracted_text="",
        extracted_text_included=False,
        max_extracted_characters=(
            execution_contract_result.max_extracted_characters
            if isinstance(
                execution_contract_result,
                ControlledPdfTextExtractionExecutionContractResult,
            )
            else 0
        ),
        max_preview_characters=(
            execution_contract_result.max_preview_characters
            if isinstance(
                execution_contract_result,
                ControlledPdfTextExtractionExecutionContractResult,
            )
            else 0
        ),
        truncated=truncated,
        extraction_error=extraction_error,
        evidence_allowed=False,
        notes=request.notes,
    )


def _invalid_request_result() -> ControlledPdfTextExtractionResultContractResult:
    execution_contract_result = ControlledPdfTextExtractionExecutionContractResult(
        allowed=True,
        reason="implementation request validation",
        fixture_id="",
        fixture_path="",
        fixture_type=PRODUCT_SPEC_PDF_FIXTURE_TYPE,
        extraction_mode=TEXT_ONLY_MODE,
        execution_allowed=True,
        max_extracted_characters=1,
        max_preview_characters=1,
        allow_full_text_storage=False,
        evidence_allowed=False,
        notes="",
    )
    result_input = ControlledPdfTextExtractionResultInput(
        fixture_id="",
        source_label="implementation request",
        fixture_path="",
        fixture_type=PRODUCT_SPEC_PDF_FIXTURE_TYPE,
        extraction_mode=TEXT_ONLY_MODE,
        extraction_status="unsupported_pdf",
        text_length=0,
        text_preview="",
        extracted_text="",
        extracted_text_included=False,
        max_extracted_characters=1,
        max_preview_characters=1,
        truncated=False,
        extraction_error=REQUEST_REQUIRED_ERROR,
        evidence_allowed=False,
        notes="",
    )
    return ControlledPdfTextExtractionResultContract.evaluate(
        execution_contract_result=execution_contract_result,
        result_input=result_input,
    )
