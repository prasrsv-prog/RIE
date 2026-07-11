import inspect
from pathlib import Path
import sys

import pytest

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


def _minimal_pdf_bytes() -> bytes:
    objects = (
        b"1 0 obj\n"
        b"<< /Type /Catalog /Pages 2 0 R >>\n"
        b"endobj\n",
        b"2 0 obj\n"
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>\n"
        b"endobj\n",
        b"3 0 obj\n"
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 72 72] "
        b"/Resources << >> >>\n"
        b"endobj\n",
    )
    content = b"%PDF-1.4\n"
    offsets = []
    for pdf_object in objects:
        offsets.append(len(content))
        content += pdf_object

    xref_offset = len(content)
    content += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    content += b"0000000000 65535 f \n"
    for offset in offsets:
        content += f"{offset:010d} 00000 n \n".encode("ascii")
    content += b"trailer\n"
    content += f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode(
        "ascii",
    )
    content += b"startxref\n"
    content += f"{xref_offset}\n".encode("ascii")
    content += b"%%EOF\n"
    return content


def _write_synthetic_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "synthetic-product-spec.pdf"
    pdf_path.write_bytes(_minimal_pdf_bytes())
    return pdf_path


def _fixture(pdf_path: Path) -> ControlledRealAssetFixtureItem:
    return ControlledRealAssetFixtureItem(
        fixture_id="fixture-product-spec",
        source_label="synthetic smoke fixture",
        fixture_path=str(pdf_path),
        fixture_type="product_spec_pdf",
        allowed_for_metadata=True,
        allowed_for_pdf_text_extraction=False,
        allowed_for_image_metadata=False,
        allowed_for_evidence=False,
        notes="synthetic smoke flow only",
    )


def _run_smoke_flow(
    pdf_path: Path,
    *,
    allow_execution: bool = True,
) -> tuple[object, object, object, ControlledPdfTextExtractionResultContractResult]:
    fixture = _fixture(pdf_path)
    fixture_result = ControlledRealAssetFixtureContract.evaluate((fixture,))
    pdf_text_result = ControlledPdfTextExtractionContract.evaluate(
        fixture_contract_result=fixture_result,
        fixture_id=fixture.fixture_id,
        notes=fixture.notes,
    )
    execution_result = ControlledPdfTextExtractionExecutionContract.evaluate(
        pdf_text_contract_result=pdf_text_result,
        max_extracted_characters=20000,
        max_preview_characters=1000,
        allow_execution=allow_execution,
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
    return fixture_result, pdf_text_result, execution_result, result


def test_synthetic_pdf_text_extraction_smoke_flow_reaches_result_contract(
    tmp_path: Path,
) -> None:
    pdf_path = _write_synthetic_pdf(tmp_path)

    fixture_result, pdf_text_result, execution_result, result = (
        _run_smoke_flow(pdf_path)
    )

    assert fixture_result.allowed is True
    assert pdf_text_result.allowed is True
    assert execution_result.allowed is True
    assert isinstance(result, ControlledPdfTextExtractionResultContractResult)
    assert result.allowed is True
    assert result.extraction_status in {
        "extracted",
        "empty",
        "truncated",
        "parser_error",
        "unsupported_pdf",
    }
    assert result.fixture_id == "fixture-product-spec"
    assert result.source_label == "synthetic smoke fixture"
    assert result.fixture_path == str(pdf_path)
    assert result.fixture_type == "product_spec_pdf"
    assert result.extraction_mode == "text_only"
    assert result.evidence_allowed is False
    assert result.extracted_text_included is False
    assert not hasattr(result, "extracted_text")

    if implementation_module._PDF_READER is None:
        assert result.extraction_status == "unsupported_pdf"
        assert result.extraction_error == "pdf parser dependency is unavailable"


def test_smoke_flow_does_not_reach_file_read_when_execution_contract_blocks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_path = _write_synthetic_pdf(tmp_path)

    def fail_if_called(fixture_path: str) -> str:
        raise AssertionError(f"parser called for {fixture_path}")

    monkeypatch.setattr(
        implementation_module,
        "_extract_text_from_pdf",
        fail_if_called,
    )

    fixture_result, pdf_text_result, execution_result, result = (
        _run_smoke_flow(pdf_path, allow_execution=False)
    )

    assert fixture_result.allowed is True
    assert pdf_text_result.allowed is True
    assert execution_result.allowed is False
    assert execution_result.reason == "execution approval is required"
    assert isinstance(result, ControlledPdfTextExtractionResultContractResult)
    assert result.allowed is False
    assert result.reason == "execution contract is not allowed"


def test_smoke_flow_does_not_create_evidence_or_downstream_artifacts(
    tmp_path: Path,
) -> None:
    pdf_path = _write_synthetic_pdf(tmp_path)
    modules_before = frozenset(sys.modules)

    _, _, _, result = _run_smoke_flow(pdf_path)

    newly_loaded_modules = frozenset(sys.modules).difference(modules_before)
    downstream_module_fragments = (
        "evidence_" + "collection",
        "official_" + "knowledge",
        "product_" + "knowledge",
        "prompt_" + "candidate",
        "knowledge_" + "repository",
    )
    downstream_type_names = (
        "Evidence" + "Collection",
        "Official" + "Knowledge",
        "Product" + "Knowledge",
        "Prompt" + "Candidate",
        "Knowledge" + "Repository",
    )

    assert type(result) is ControlledPdfTextExtractionResultContractResult
    assert type(result).__name__ not in downstream_type_names
    assert all(
        type(value).__name__ not in downstream_type_names
        for value in vars(result).values()
    )
    assert all(
        fragment not in module_name
        for module_name in newly_loaded_modules
        for fragment in downstream_module_fragments
    )


def test_smoke_flow_source_has_no_forbidden_discovery_or_downstream_fragments(
) -> None:
    test_source = inspect.getsource(sys.modules[__name__])
    implementation_source = inspect.getsource(implementation_module)
    forbidden_fragments = (
        "iter" + "dir",
        "r" + "glob",
        "scan" + "dir",
        "walk" + "(",
        "glob" + "(",
        "CreativeAssetType" + "Detector",
        "CreativeAssetBatch" + "Scanner",
        "Official" + "Knowledge",
        "Product" + "Knowledge",
        "Prompt" + "Candidate",
        "Evidence" + "Collection",
        "Knowledge" + "Repository",
    )

    for source in (test_source, implementation_source):
        for fragment in forbidden_fragments:
            assert fragment not in source
