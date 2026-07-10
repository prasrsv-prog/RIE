from dataclasses import FrozenInstanceError
import inspect

import pytest

from rie.ingestion import (
    controlled_pdf_text_extraction_result_contract as contract_module,
)
from rie.ingestion.controlled_pdf_text_extraction_execution_contract import (
    ControlledPdfTextExtractionExecutionContractResult,
)
from rie.ingestion.controlled_pdf_text_extraction_result_contract import (
    ControlledPdfTextExtractionResultContract,
    ControlledPdfTextExtractionResultContractResult,
    ControlledPdfTextExtractionResultInput,
)


def _execution_result(
    **overrides: object,
) -> ControlledPdfTextExtractionExecutionContractResult:
    values = {
        "allowed": True,
        "reason": "pdf text extraction execution contract allowed",
        "fixture_id": "fixture-product-spec",
        "fixture_path": "fixtures/sandbox/../product-spec.pdf",
        "fixture_type": "product_spec_pdf",
        "extraction_mode": "text_only",
        "execution_allowed": True,
        "max_extracted_characters": 20000,
        "max_preview_characters": 1000,
        "allow_full_text_storage": False,
        "evidence_allowed": False,
        "notes": "",
    }
    values.update(overrides)
    return ControlledPdfTextExtractionExecutionContractResult(**values)


def _result_input(**overrides: object) -> ControlledPdfTextExtractionResultInput:
    values = {
        "fixture_id": "fixture-product-spec",
        "source_label": "synthetic sandbox copy",
        "fixture_path": "fixtures/sandbox/../product-spec.pdf",
        "fixture_type": "product_spec_pdf",
        "extraction_mode": "text_only",
        "extraction_status": "extracted",
        "text_length": 42,
        "text_preview": "Synthetic product spec preview.",
        "extracted_text": "",
        "extracted_text_included": False,
        "max_extracted_characters": 20000,
        "max_preview_characters": 1000,
        "truncated": False,
        "extraction_error": "",
        "evidence_allowed": False,
        "notes": "",
    }
    values.update(overrides)
    return ControlledPdfTextExtractionResultInput(**values)


def _evaluate(
    execution_result: (
        ControlledPdfTextExtractionExecutionContractResult | object | None
    ) = None,
    result_input: ControlledPdfTextExtractionResultInput | object | None = None,
) -> ControlledPdfTextExtractionResultContractResult:
    execution_value = (
        _execution_result() if execution_result is None else execution_result
    )
    input_value = _result_input() if result_input is None else result_input
    return ControlledPdfTextExtractionResultContract.evaluate(
        execution_contract_result=execution_value,
        result_input=input_value,
    )


def test_allows_extracted_status_with_positive_text_length_and_bounded_preview() -> None:
    result = _evaluate()

    assert result.allowed is True
    assert result.reason == "pdf text extraction result contract allowed"
    assert result.fixture_id == "fixture-product-spec"
    assert result.source_label == "synthetic sandbox copy"
    assert result.fixture_type == "product_spec_pdf"
    assert result.extraction_mode == "text_only"
    assert result.extraction_status == "extracted"
    assert result.text_length == 42
    assert result.text_preview == "Synthetic product spec preview."
    assert result.extracted_text_included is False
    assert result.max_extracted_characters == 20000
    assert result.max_preview_characters == 1000
    assert result.truncated is False
    assert result.extraction_error == ""
    assert result.evidence_allowed is False
    assert result.notes == ""


def test_allows_empty_status() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="empty",
            text_length=0,
            text_preview="",
        ),
    )

    assert result.allowed is True
    assert result.extraction_status == "empty"
    assert result.text_length == 0
    assert result.text_preview == ""
    assert result.truncated is False


def test_allows_truncated_status_with_max_text_length_and_truncated_true() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="truncated",
            text_length=20000,
            truncated=True,
        ),
    )

    assert result.allowed is True
    assert result.extraction_status == "truncated"
    assert result.text_length == 20000
    assert result.truncated is True


def test_allows_parser_error_status_with_extraction_error() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="parser_error",
            text_length=0,
            text_preview="",
            extraction_error="parser failed",
        ),
    )

    assert result.allowed is True
    assert result.extraction_status == "parser_error"
    assert result.extraction_error == "parser failed"


def test_preserves_fixture_path_exactly() -> None:
    fixture_path = "fixtures\\sandbox\\..\\selected product spec.pdf"
    execution_result = _execution_result(fixture_path=fixture_path)
    result_input = _result_input(fixture_path=fixture_path)

    result = _evaluate(execution_result, result_input)

    assert result.allowed is True
    assert result.fixture_path == fixture_path


def test_result_does_not_expose_extracted_text_attribute() -> None:
    result = _evaluate()

    assert not hasattr(result, "extracted_text")


def test_result_evidence_allowed_is_false() -> None:
    result = _evaluate()

    assert result.evidence_allowed is False


def test_rejects_non_execution_contract_result() -> None:
    result = _evaluate(execution_result=object())

    assert result.allowed is False
    assert result.reason == "execution contract result is required"


def test_rejects_disallowed_execution_contract_result() -> None:
    result = _evaluate(
        execution_result=_execution_result(
            allowed=False,
            reason="upstream blocked",
        ),
    )

    assert result.allowed is False
    assert result.reason == "execution contract is not allowed"


def test_rejects_execution_allowed_false() -> None:
    result = _evaluate(
        execution_result=_execution_result(execution_allowed=False),
    )

    assert result.allowed is False
    assert result.reason == "execution approval is required"


def test_rejects_upstream_evidence_allowed_true() -> None:
    result = _evaluate(
        execution_result=_execution_result(evidence_allowed=True),
    )

    assert result.allowed is False
    assert result.reason == "upstream evidence flag must remain disabled"


def test_rejects_upstream_allow_full_text_storage_true() -> None:
    result = _evaluate(
        execution_result=_execution_result(allow_full_text_storage=True),
    )

    assert result.allowed is False
    assert result.reason == "full text storage must remain disabled"


def test_rejects_non_result_input() -> None:
    result = _evaluate(result_input=object())

    assert result.allowed is False
    assert result.reason == "result input is required"


def test_rejects_fixture_id_mismatch() -> None:
    result = _evaluate(result_input=_result_input(fixture_id="other-fixture"))

    assert result.allowed is False
    assert result.reason == "fixture_id mismatch"


def test_rejects_fixture_path_mismatch() -> None:
    result = _evaluate(result_input=_result_input(fixture_path="fixtures/other.pdf"))

    assert result.allowed is False
    assert result.reason == "fixture_path mismatch"


def test_rejects_fixture_type_mismatch() -> None:
    result = _evaluate(result_input=_result_input(fixture_type="other_pdf"))

    assert result.allowed is False
    assert result.reason == "fixture_type mismatch"


def test_rejects_extraction_mode_mismatch() -> None:
    result = _evaluate(result_input=_result_input(extraction_mode="other_mode"))

    assert result.allowed is False
    assert result.reason == "extraction_mode mismatch"


def test_rejects_fixture_type_not_product_spec_pdf() -> None:
    execution_result = _execution_result(fixture_type="other_pdf")
    result_input = _result_input(fixture_type="other_pdf")

    result = _evaluate(execution_result, result_input)

    assert result.allowed is False
    assert result.reason == "fixture_type must be product_spec_pdf"


def test_rejects_extraction_mode_not_text_only() -> None:
    execution_result = _execution_result(extraction_mode="other_mode")
    result_input = _result_input(extraction_mode="other_mode")

    result = _evaluate(execution_result, result_input)

    assert result.allowed is False
    assert result.reason == "extraction_mode must be text_only"


def test_rejects_empty_fixture_id() -> None:
    execution_result = _execution_result(fixture_id="   ")
    result_input = _result_input(fixture_id="   ")

    result = _evaluate(execution_result, result_input)

    assert result.allowed is False
    assert result.reason == "fixture_id is required"


def test_rejects_empty_source_label() -> None:
    result = _evaluate(result_input=_result_input(source_label="   "))

    assert result.allowed is False
    assert result.reason == "source_label is required"


def test_rejects_empty_fixture_path() -> None:
    execution_result = _execution_result(fixture_path="   ")
    result_input = _result_input(fixture_path="   ")

    result = _evaluate(execution_result, result_input)

    assert result.allowed is False
    assert result.reason == "fixture_path is required"


def test_rejects_unsupported_extraction_status() -> None:
    result = _evaluate(result_input=_result_input(extraction_status="unknown"))

    assert result.allowed is False
    assert result.reason == "unsupported extraction_status"


def test_rejects_negative_text_length() -> None:
    result = _evaluate(result_input=_result_input(text_length=-1))

    assert result.allowed is False
    assert result.reason == "text_length must not be negative"


def test_rejects_text_length_above_execution_limit() -> None:
    result = _evaluate(result_input=_result_input(text_length=20001))

    assert result.allowed is False
    assert result.reason == "text_length exceeds extraction limit"


def test_rejects_max_extracted_characters_mismatch() -> None:
    result = _evaluate(result_input=_result_input(max_extracted_characters=19999))

    assert result.allowed is False
    assert result.reason == "max_extracted_characters mismatch"


def test_rejects_max_preview_characters_mismatch() -> None:
    result = _evaluate(result_input=_result_input(max_preview_characters=999))

    assert result.allowed is False
    assert result.reason == "max_preview_characters mismatch"


def test_rejects_max_preview_characters_less_than_or_equal_to_zero() -> None:
    execution_result = _execution_result(max_preview_characters=0)
    result_input = _result_input(max_preview_characters=0)

    result = _evaluate(execution_result, result_input)

    assert result.allowed is False
    assert result.reason == "max_preview_characters must be greater than zero"


def test_rejects_max_preview_characters_greater_than_1000() -> None:
    execution_result = _execution_result(max_preview_characters=1001)
    result_input = _result_input(max_preview_characters=1001)

    result = _evaluate(execution_result, result_input)

    assert result.allowed is False
    assert result.reason == "max_preview_characters exceeds result contract limit"


def test_rejects_preview_length_over_limit() -> None:
    execution_result = _execution_result(max_preview_characters=10)
    result_input = _result_input(
        max_preview_characters=10,
        text_preview="12345678901",
    )

    result = _evaluate(execution_result, result_input)

    assert result.allowed is False
    assert result.reason == "text_preview exceeds preview limit"


def test_rejects_non_empty_extracted_text() -> None:
    result = _evaluate(result_input=_result_input(extracted_text="full text"))

    assert result.allowed is False
    assert result.reason == "extracted_text storage is not allowed by this contract"


def test_rejects_extracted_text_included_true() -> None:
    result = _evaluate(result_input=_result_input(extracted_text_included=True))

    assert result.allowed is False
    assert result.reason == "extracted_text_included must remain false"


def test_rejects_evidence_allowed_true() -> None:
    result = _evaluate(result_input=_result_input(evidence_allowed=True))

    assert result.allowed is False
    assert result.reason == "evidence creation is not allowed by this contract"


def test_rejects_notes_none() -> None:
    result = _evaluate(result_input=_result_input(notes=None))

    assert result.allowed is False
    assert result.reason == "notes is required"


def test_rejects_extraction_error_none() -> None:
    result = _evaluate(result_input=_result_input(extraction_error=None))

    assert result.allowed is False
    assert result.reason == "extraction_error is required"


def test_rejects_successful_status_with_non_empty_extraction_error() -> None:
    result = _evaluate(result_input=_result_input(extraction_error="not empty"))

    assert result.allowed is False
    assert result.reason == "successful status must not have extraction_error"


def test_rejects_error_status_with_empty_extraction_error() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="parser_error",
            text_length=0,
            text_preview="",
        ),
    )

    assert result.allowed is False
    assert result.reason == "error status requires extraction_error"


def test_rejects_extracted_status_with_zero_text_length() -> None:
    result = _evaluate(result_input=_result_input(text_length=0))

    assert result.allowed is False
    assert result.reason == "extracted status requires positive text_length"


def test_rejects_extracted_status_with_truncated_true() -> None:
    result = _evaluate(result_input=_result_input(truncated=True))

    assert result.allowed is False
    assert result.reason == "extracted status must not be truncated"


def test_rejects_empty_status_with_non_zero_text_length() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="empty",
            text_length=1,
            text_preview="",
        ),
    )

    assert result.allowed is False
    assert result.reason == "empty status requires zero text_length"


def test_rejects_empty_status_with_non_empty_preview() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="empty",
            text_length=0,
            text_preview="preview",
        ),
    )

    assert result.allowed is False
    assert result.reason == "empty status requires empty text_preview"


def test_rejects_empty_status_with_truncated_true() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="empty",
            text_length=0,
            text_preview="",
            truncated=True,
        ),
    )

    assert result.allowed is False
    assert result.reason == "empty status must not be truncated"


def test_rejects_truncated_status_with_text_length_below_max() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="truncated",
            text_length=19999,
            truncated=True,
        ),
    )

    assert result.allowed is False
    assert result.reason == "truncated status requires max text_length"


def test_rejects_truncated_status_with_truncated_false() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="truncated",
            text_length=20000,
            truncated=False,
        ),
    )

    assert result.allowed is False
    assert result.reason == "truncated status requires truncated true"


def test_rejects_not_run_status_with_non_zero_text_length() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="not_run",
            text_length=1,
            text_preview="",
        ),
    )

    assert result.allowed is False
    assert result.reason == "not_run status requires zero text_length"


def test_rejects_not_run_status_with_non_empty_preview() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="not_run",
            text_length=0,
            text_preview="preview",
        ),
    )

    assert result.allowed is False
    assert result.reason == "not_run status requires empty text_preview"


def test_rejects_not_run_status_with_truncated_true() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="not_run",
            text_length=0,
            text_preview="",
            truncated=True,
        ),
    )

    assert result.allowed is False
    assert result.reason == "not_run status must not be truncated"


def test_rejects_error_status_with_non_zero_text_length() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="encrypted",
            text_length=1,
            text_preview="",
            extraction_error="encrypted",
        ),
    )

    assert result.allowed is False
    assert result.reason == "error status requires zero text_length"


def test_rejects_error_status_with_non_empty_preview() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="unreadable",
            text_length=0,
            text_preview="preview",
            extraction_error="unreadable",
        ),
    )

    assert result.allowed is False
    assert result.reason == "error status requires empty text_preview"


def test_rejects_error_status_with_truncated_true() -> None:
    result = _evaluate(
        result_input=_result_input(
            extraction_status="blocked",
            text_length=0,
            text_preview="",
            truncated=True,
            extraction_error="blocked",
        ),
    )

    assert result.allowed is False
    assert result.reason == "error status must not be truncated"


def test_dataclass_results_are_immutable() -> None:
    result_input = _result_input()
    result = _evaluate(result_input=result_input)

    with pytest.raises(FrozenInstanceError):
        result.allowed = False

    with pytest.raises(FrozenInstanceError):
        result_input.text_length = 0


def test_contract_module_has_no_filesystem_pdf_or_downstream_dependencies() -> None:
    source = inspect.getsource(contract_module)

    forbidden_fragments = (
        "Path(",
        "pathlib",
        "os.",
        "open(",
        "read_bytes",
        "read_text",
        "pdfplumber",
        "pypdf",
        "PyPDF",
        "fitz",
        "OCR",
        "CreativeAssetTypeDetector",
        "CreativeAssetBatchScanner",
        "OfficialKnowledge",
        "ProductKnowledge",
        "PromptCandidate",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
