from dataclasses import FrozenInstanceError
import inspect

import pytest

from rie.ingestion import (
    controlled_pdf_text_extraction_execution_contract as contract_module,
)
from rie.ingestion.controlled_pdf_text_extraction_contract import (
    ControlledPdfTextExtractionContractResult,
)
from rie.ingestion.controlled_pdf_text_extraction_execution_contract import (
    ControlledPdfTextExtractionExecutionContract,
    ControlledPdfTextExtractionExecutionContractResult,
)


def _upstream_result(**overrides: object) -> ControlledPdfTextExtractionContractResult:
    values = {
        "allowed": True,
        "reason": "pdf text extraction contract allowed",
        "fixture_id": "fixture-product-spec",
        "fixture_path": "fixtures/sandbox/../product-spec.pdf",
        "fixture_type": "product_spec_pdf",
        "extraction_mode": "text_only",
        "evidence_allowed": False,
        "notes": "",
    }
    values.update(overrides)
    return ControlledPdfTextExtractionContractResult(**values)


def _evaluate(
    upstream_result: ControlledPdfTextExtractionContractResult | object | None = None,
    **overrides: object,
) -> ControlledPdfTextExtractionExecutionContractResult:
    values = {
        "pdf_text_contract_result": (
            _upstream_result() if upstream_result is None else upstream_result
        ),
        "allow_execution": True,
        "max_extracted_characters": 20000,
        "max_preview_characters": 1000,
        "allow_full_text_storage": False,
        "allow_evidence_creation": False,
        "notes": "",
    }
    values.update(overrides)
    return ControlledPdfTextExtractionExecutionContract.evaluate(**values)


def test_allows_valid_upstream_contract_with_bounded_execution_limits() -> None:
    result = _evaluate(notes="execution gate only")

    assert result.allowed is True
    assert result.reason == "pdf text extraction execution contract allowed"
    assert result.fixture_id == "fixture-product-spec"
    assert result.fixture_type == "product_spec_pdf"
    assert result.extraction_mode == "text_only"
    assert result.execution_allowed is True
    assert result.max_extracted_characters == 20000
    assert result.max_preview_characters == 1000
    assert result.allow_full_text_storage is False
    assert result.evidence_allowed is False
    assert result.notes == "execution gate only"


def test_preserves_fixture_path_exactly() -> None:
    fixture_path = "fixtures\\sandbox\\..\\selected product spec.pdf"
    upstream_result = _upstream_result(fixture_path=fixture_path)

    result = _evaluate(upstream_result)

    assert result.allowed is True
    assert result.fixture_path == fixture_path


def test_result_evidence_allowed_is_false() -> None:
    result = _evaluate()

    assert result.evidence_allowed is False


def test_result_allow_full_text_storage_is_false() -> None:
    result = _evaluate()

    assert result.allow_full_text_storage is False


def test_rejects_non_pdf_text_contract_result() -> None:
    result = _evaluate(object())

    assert result.allowed is False
    assert result.reason == "pdf text extraction contract result is required"


def test_rejects_disallowed_upstream_contract_result() -> None:
    upstream_result = _upstream_result(
        allowed=False,
        reason="upstream blocked",
    )

    result = _evaluate(upstream_result)

    assert result.allowed is False
    assert result.reason == "pdf text extraction contract is not allowed"


def test_rejects_empty_fixture_id() -> None:
    upstream_result = _upstream_result(fixture_id="   ")

    result = _evaluate(upstream_result)

    assert result.allowed is False
    assert result.reason == "fixture_id is required"


def test_rejects_empty_fixture_path() -> None:
    upstream_result = _upstream_result(fixture_path="   ")

    result = _evaluate(upstream_result)

    assert result.allowed is False
    assert result.reason == "fixture_path is required"


@pytest.mark.parametrize(
    "fixture_type",
    ("product_photo_jpeg", "product_photo_png"),
)
def test_rejects_product_photo_fixture_types(fixture_type: str) -> None:
    upstream_result = _upstream_result(fixture_type=fixture_type)

    result = _evaluate(upstream_result)

    assert result.allowed is False
    assert result.reason == "fixture_type must be product_spec_pdf"
    assert result.fixture_type == fixture_type


def test_rejects_unsupported_extraction_mode() -> None:
    upstream_result = _upstream_result(extraction_mode="header_only")

    result = _evaluate(upstream_result)

    assert result.allowed is False
    assert result.reason == "extraction_mode must be text_only"


def test_rejects_upstream_evidence_allowed_true() -> None:
    upstream_result = _upstream_result(evidence_allowed=True)

    result = _evaluate(upstream_result)

    assert result.allowed is False
    assert result.reason == "upstream evidence flag must remain disabled"


def test_rejects_allow_execution_false() -> None:
    result = _evaluate(allow_execution=False)

    assert result.allowed is False
    assert result.reason == "execution approval is required"


@pytest.mark.parametrize("max_extracted_characters", (0, -1))
def test_rejects_max_extracted_characters_less_than_or_equal_to_zero(
    max_extracted_characters: int,
) -> None:
    result = _evaluate(max_extracted_characters=max_extracted_characters)

    assert result.allowed is False
    assert (
        result.reason
        == "max_extracted_characters must be greater than zero"
    )


def test_rejects_max_extracted_characters_greater_than_limit() -> None:
    result = _evaluate(max_extracted_characters=20001)

    assert result.allowed is False
    assert (
        result.reason
        == "max_extracted_characters exceeds execution contract limit"
    )


@pytest.mark.parametrize("max_preview_characters", (0, -1))
def test_rejects_max_preview_characters_less_than_or_equal_to_zero(
    max_preview_characters: int,
) -> None:
    result = _evaluate(max_preview_characters=max_preview_characters)

    assert result.allowed is False
    assert result.reason == "max_preview_characters must be greater than zero"


def test_rejects_max_preview_characters_greater_than_limit() -> None:
    result = _evaluate(max_preview_characters=1001)

    assert result.allowed is False
    assert (
        result.reason
        == "max_preview_characters exceeds execution contract limit"
    )


def test_rejects_max_preview_characters_greater_than_extracted_limit() -> None:
    result = _evaluate(
        max_extracted_characters=100,
        max_preview_characters=101,
    )

    assert result.allowed is False
    assert (
        result.reason
        == "max_preview_characters must not exceed max_extracted_characters"
    )


def test_rejects_allow_full_text_storage_true() -> None:
    result = _evaluate(allow_full_text_storage=True)

    assert result.allowed is False
    assert result.reason == "full text storage is not allowed by this contract"
    assert result.allow_full_text_storage is True


def test_rejects_allow_evidence_creation_true() -> None:
    result = _evaluate(allow_evidence_creation=True)

    assert result.allowed is False
    assert result.reason == "evidence creation is not allowed by this contract"


def test_rejects_notes_none() -> None:
    result = _evaluate(notes=None)

    assert result.allowed is False
    assert result.reason == "notes is required"
    assert result.notes == ""


def test_fixture_type_is_not_inferred_from_fixture_path() -> None:
    upstream_result = _upstream_result(
        fixture_path="fixtures/product-photo.jpg",
        fixture_type="product_spec_pdf",
    )

    result = _evaluate(upstream_result)

    assert result.allowed is True
    assert result.fixture_path == "fixtures/product-photo.jpg"
    assert result.fixture_type == "product_spec_pdf"


def test_dataclass_result_is_immutable() -> None:
    result = _evaluate()

    with pytest.raises(FrozenInstanceError):
        result.allowed = False


def test_result_dataclass_can_be_constructed_directly() -> None:
    result = ControlledPdfTextExtractionExecutionContractResult(
        allowed=False,
        reason="synthetic",
        fixture_id="fixture",
        fixture_path="fixtures/spec.pdf",
        fixture_type="product_spec_pdf",
        extraction_mode="text_only",
        execution_allowed=False,
        max_extracted_characters=0,
        max_preview_characters=0,
        allow_full_text_storage=False,
        evidence_allowed=False,
        notes="",
    )

    assert result.allowed is False
    assert result.evidence_allowed is False


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
