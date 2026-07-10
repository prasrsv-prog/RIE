from dataclasses import FrozenInstanceError
import inspect

import pytest

from rie.ingestion import controlled_pdf_text_extraction_contract as contract_module
from rie.ingestion.controlled_pdf_text_extraction_contract import (
    ControlledPdfTextExtractionContract,
    ControlledPdfTextExtractionContractResult,
)
from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContractResult,
    ControlledRealAssetFixtureItem,
)


def _fixture(**overrides: object) -> ControlledRealAssetFixtureItem:
    values = {
        "fixture_id": "fixture-product-spec",
        "source_label": "synthetic sandbox copy",
        "fixture_path": "fixtures/sandbox/../product-spec.pdf",
        "fixture_type": "product_spec_pdf",
        "allowed_for_metadata": True,
        "allowed_for_pdf_text_extraction": False,
        "allowed_for_image_metadata": False,
        "allowed_for_evidence": False,
        "notes": "",
    }
    values.update(overrides)
    return ControlledRealAssetFixtureItem(**values)


def _fixture_contract_result(
    *,
    allowed: bool = True,
    fixtures: tuple[ControlledRealAssetFixtureItem, ...] | None = None,
) -> ControlledRealAssetFixtureContractResult:
    fixture_tuple = (_fixture(),) if fixtures is None else fixtures
    return ControlledRealAssetFixtureContractResult(
        allowed=allowed,
        reason="fixture contract allowed" if allowed else "fixture blocked",
        fixture_count=len(fixture_tuple),
        fixtures=fixture_tuple,
    )


def test_allows_product_spec_pdf_fixture_in_text_only_mode() -> None:
    fixture_contract_result = _fixture_contract_result()

    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_contract_result,
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is True
    assert result.reason == "pdf text extraction contract allowed"
    assert result.fixture_id == "fixture-product-spec"
    assert result.fixture_type == "product_spec_pdf"
    assert result.extraction_mode == "text_only"
    assert result.evidence_allowed is False
    assert result.notes == ""


def test_preserves_fixture_path_exactly() -> None:
    fixture_path = "fixtures\\sandbox\\..\\selected product spec.pdf"
    fixture = _fixture(fixture_path=fixture_path)
    fixture_contract_result = _fixture_contract_result(fixtures=(fixture,))

    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_contract_result,
        fixture_id="fixture-product-spec",
        notes="reviewed only",
    )

    assert result.allowed is True
    assert result.fixture_path == fixture_path
    assert result.notes == "reviewed only"


def test_result_evidence_allowed_is_false() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-product-spec",
    )

    assert result.evidence_allowed is False


def test_rejects_non_fixture_contract_result() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=object(),
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is False
    assert result.reason == "fixture contract result is required"


def test_rejects_disallowed_fixture_contract_result() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(allowed=False),
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is False
    assert result.reason == "fixture contract is not allowed"


def test_rejects_empty_fixture_id() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="   ",
    )

    assert result.allowed is False
    assert result.reason == "fixture_id is required"


def test_rejects_missing_fixture_id() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="missing-fixture",
    )

    assert result.allowed is False
    assert result.reason == "fixture_id not found"


def test_rejects_duplicate_fixture_id() -> None:
    first = _fixture(fixture_path="fixtures/one.pdf")
    second = _fixture(fixture_path="fixtures/two.pdf")
    fixture_contract_result = _fixture_contract_result(
        fixtures=(first, second),
    )

    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_contract_result,
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is False
    assert result.reason == "duplicate fixture_id"


@pytest.mark.parametrize(
    "fixture_type",
    ("product_photo_jpeg", "product_photo_png"),
)
def test_rejects_product_photo_fixtures(fixture_type: str) -> None:
    fixture = _fixture(fixture_type=fixture_type)
    fixture_contract_result = _fixture_contract_result(fixtures=(fixture,))

    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_contract_result,
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is False
    assert result.reason == "fixture_type must be product_spec_pdf"
    assert result.fixture_type == fixture_type


def test_rejects_fixture_with_metadata_disabled() -> None:
    fixture = _fixture(allowed_for_metadata=False)
    fixture_contract_result = _fixture_contract_result(fixtures=(fixture,))

    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_contract_result,
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is False
    assert result.reason == "metadata access must be allowed"


def test_rejects_fixture_with_pdf_text_extraction_flag_enabled() -> None:
    fixture = _fixture(allowed_for_pdf_text_extraction=True)
    fixture_contract_result = _fixture_contract_result(fixtures=(fixture,))

    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_contract_result,
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is False
    assert (
        result.reason
        == "fixture pdf text extraction flag must remain disabled"
    )


def test_rejects_fixture_with_evidence_flag_enabled() -> None:
    fixture = _fixture(allowed_for_evidence=True)
    fixture_contract_result = _fixture_contract_result(fixtures=(fixture,))

    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_contract_result,
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is False
    assert result.reason == "fixture evidence flag must remain disabled"


def test_rejects_unsupported_extraction_mode() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-product-spec",
        extraction_mode="full_text",
    )

    assert result.allowed is False
    assert result.reason == "unsupported extraction_mode"


def test_rejects_allow_pdf_text_extraction_true() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-product-spec",
        allow_pdf_text_extraction=True,
    )

    assert result.allowed is False
    assert (
        result.reason
        == "pdf text extraction execution is not allowed by this contract"
    )


def test_rejects_allow_evidence_creation_true() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-product-spec",
        allow_evidence_creation=True,
    )

    assert result.allowed is False
    assert result.reason == "evidence creation is not allowed by this contract"


def test_rejects_notes_none() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-product-spec",
        notes=None,
    )

    assert result.allowed is False
    assert result.reason == "notes is required"
    assert result.notes == ""


def test_fixture_type_is_not_inferred_from_fixture_path() -> None:
    fixture = _fixture(
        fixture_path="fixtures/product-photo.jpg",
        fixture_type="product_spec_pdf",
    )
    fixture_contract_result = _fixture_contract_result(fixtures=(fixture,))

    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_contract_result,
        fixture_id="fixture-product-spec",
    )

    assert result.allowed is True
    assert result.fixture_path == "fixtures/product-photo.jpg"
    assert result.fixture_type == "product_spec_pdf"


def test_dataclass_result_is_immutable() -> None:
    result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-product-spec",
    )

    with pytest.raises(FrozenInstanceError):
        result.allowed = False


def test_result_dataclass_can_be_constructed_directly() -> None:
    result = ControlledPdfTextExtractionContractResult(
        allowed=False,
        reason="synthetic",
        fixture_id="fixture",
        fixture_path="fixtures/spec.pdf",
        fixture_type="product_spec_pdf",
        extraction_mode="text_only",
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
