from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from rie.ingestion import (
    controlled_pdf_text_extraction_implementation as implementation_module,
)
from rie.ingestion.controlled_pdf_text_extraction_contract import (
    ControlledPdfTextExtractionContract,
)
from rie.ingestion.controlled_pdf_text_extraction_execution_contract import (
    ControlledPdfTextExtractionExecutionContract,
)
from rie.ingestion.controlled_pdf_text_extraction_implementation import (
    ControlledPdfTextExtractionImplementation,
    ControlledPdfTextExtractionImplementationRequest,
)
from rie.ingestion.controlled_pdf_text_extraction_result_contract import (
    ControlledPdfTextExtractionResultContractResult,
)
from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContract,
    ControlledRealAssetFixtureItem,
)


def _write_blank_synthetic_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "synthetic-parser-execution.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(str(pdf_path))
    return pdf_path


def test_controlled_synthetic_pdf_parser_execution_reaches_empty_result(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_path = _write_blank_synthetic_pdf(tmp_path)
    fixture = ControlledRealAssetFixtureItem(
        fixture_id="fixture-product-spec",
        source_label="synthetic parser fixture",
        fixture_path=str(pdf_path),
        fixture_type="product_spec_pdf",
        allowed_for_metadata=True,
        allowed_for_pdf_text_extraction=False,
        allowed_for_image_metadata=False,
        allowed_for_evidence=False,
        notes="synthetic parser execution only",
    )
    parser_paths: list[str] = []

    def tracking_reader(fixture_path: str) -> PdfReader:
        parser_paths.append(fixture_path)
        return PdfReader(fixture_path)

    assert implementation_module._PDF_READER is not None
    monkeypatch.setattr(implementation_module, "_PDF_READER", tracking_reader)

    fixture_result = ControlledRealAssetFixtureContract.evaluate((fixture,))
    pdf_text_result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_result,
        fixture_id=fixture.fixture_id,
        notes=fixture.notes,
    )
    execution_result = ControlledPdfTextExtractionExecutionContract.evaluate(
        pdf_text_contract_result=pdf_text_result,
        allow_execution=True,
        max_extracted_characters=20000,
        max_preview_characters=1000,
        allow_full_text_storage=False,
        allow_evidence_creation=False,
        notes=fixture.notes,
    )
    request = ControlledPdfTextExtractionImplementationRequest(
        execution_contract_result=execution_result,
        fixture_id=fixture.fixture_id,
        source_label=fixture.source_label,
        fixture_path=fixture.fixture_path,
        fixture_type=fixture.fixture_type,
        extraction_mode=pdf_text_result.extraction_mode,
        notes=fixture.notes,
    )

    result = ControlledPdfTextExtractionImplementation.extract(request)

    assert fixture_result.allowed is True
    assert pdf_text_result.allowed is True
    assert execution_result.allowed is True
    assert execution_result.allow_full_text_storage is False
    assert execution_result.evidence_allowed is False
    assert parser_paths == [str(pdf_path)]
    assert type(result) is ControlledPdfTextExtractionResultContractResult
    assert result.allowed is True
    assert result.extraction_status == "empty"
    assert result.extraction_status != "unsupported_pdf"
    assert result.fixture_path == str(pdf_path)
    assert result.fixture_type == "product_spec_pdf"
    assert result.extraction_mode == "text_only"
    assert result.text_length == 0
    assert result.text_preview == ""
    assert result.extraction_error == ""
    assert not hasattr(result, "extracted_text")
    assert result.extracted_text_included is False
    assert result.evidence_allowed is False
