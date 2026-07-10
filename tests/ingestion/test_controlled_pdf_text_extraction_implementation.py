import inspect
from pathlib import Path

import pytest

from rie.ingestion import (
    controlled_pdf_text_extraction_implementation as implementation_module,
)
from rie.ingestion.controlled_pdf_text_extraction_execution_contract import (
    ControlledPdfTextExtractionExecutionContractResult,
)
from rie.ingestion.controlled_pdf_text_extraction_implementation import (
    ControlledPdfTextExtractionImplementation,
    ControlledPdfTextExtractionImplementationRequest,
)
from rie.ingestion.controlled_pdf_text_extraction_result_contract import (
    ControlledPdfTextExtractionResultContractResult,
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


def _write_minimal_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "controlled-product-spec.pdf"
    pdf_path.write_bytes(_minimal_pdf_bytes())
    return pdf_path


def _write_invalid_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "invalid-product-spec.pdf"
    pdf_path.write_bytes(b"not a pdf")
    return pdf_path


def _execution_result(
    fixture_path: str,
    **overrides: object,
) -> ControlledPdfTextExtractionExecutionContractResult:
    values = {
        "allowed": True,
        "reason": "pdf text extraction execution contract allowed",
        "fixture_id": "fixture-product-spec",
        "fixture_path": fixture_path,
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


def _request(
    execution_fixture_path: str,
    *,
    execution_overrides: dict[str, object] | None = None,
    **overrides: object,
) -> ControlledPdfTextExtractionImplementationRequest:
    execution_values = {} if execution_overrides is None else execution_overrides
    values = {
        "execution_contract_result": _execution_result(
            execution_fixture_path,
            **execution_values,
        ),
        "fixture_id": "fixture-product-spec",
        "source_label": "synthetic sandbox copy",
        "fixture_path": execution_fixture_path,
        "fixture_type": "product_spec_pdf",
        "extraction_mode": "text_only",
        "notes": "",
    }
    values.update(overrides)
    return ControlledPdfTextExtractionImplementationRequest(**values)


def _extract(
    request: ControlledPdfTextExtractionImplementationRequest,
) -> ControlledPdfTextExtractionResultContractResult:
    return ControlledPdfTextExtractionImplementation.extract(request)


def test_returns_unsupported_pdf_through_result_contract_when_parser_is_absent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_path = _write_minimal_pdf(tmp_path)
    monkeypatch.setattr(implementation_module, "_PDF_READER", None)

    result = _extract(_request(str(pdf_path)))

    assert isinstance(result, ControlledPdfTextExtractionResultContractResult)
    assert result.allowed is True
    assert result.extraction_status == "unsupported_pdf"
    assert result.extraction_error == "pdf parser dependency is unavailable"


def test_uses_existing_parser_dependency_for_synthetic_pdf_when_available(
    tmp_path: Path,
) -> None:
    pdf_path = _write_minimal_pdf(tmp_path)

    result = _extract(_request(str(pdf_path)))

    assert isinstance(result, ControlledPdfTextExtractionResultContractResult)
    if implementation_module._PDF_READER is None:
        assert result.extraction_status == "unsupported_pdf"
    else:
        assert result.allowed is True
        assert result.extraction_status in {"empty", "extracted"}
        assert result.reason == "pdf text extraction result contract allowed"


def test_does_not_expose_extracted_text_on_final_result(tmp_path: Path) -> None:
    pdf_path = _write_minimal_pdf(tmp_path)

    result = _extract(_request(str(pdf_path)))

    assert not hasattr(result, "extracted_text")


def test_result_evidence_allowed_is_false(tmp_path: Path) -> None:
    pdf_path = _write_minimal_pdf(tmp_path)

    result = _extract(_request(str(pdf_path)))

    assert result.evidence_allowed is False


def test_preserves_fixture_fields(tmp_path: Path) -> None:
    pdf_path = _write_minimal_pdf(tmp_path)

    result = _extract(_request(str(pdf_path), notes="implementation skeleton"))

    assert result.fixture_id == "fixture-product-spec"
    assert result.source_label == "synthetic sandbox copy"
    assert result.fixture_path == str(pdf_path)
    assert result.fixture_type == "product_spec_pdf"
    assert result.extraction_mode == "text_only"
    assert result.notes == "implementation skeleton"


@pytest.mark.parametrize(
    ("execution_overrides", "request_overrides", "expected_reason"),
    (
        (
            {"allowed": False, "reason": "blocked"},
            {},
            "execution contract is not allowed",
        ),
        (
            {"execution_allowed": False},
            {},
            "execution approval is required",
        ),
        (
            {"evidence_allowed": True},
            {},
            "upstream evidence flag must remain disabled",
        ),
        (
            {"allow_full_text_storage": True},
            {},
            "full text storage must remain disabled",
        ),
        (
            {},
            {"fixture_id": "other-fixture"},
            "fixture_id mismatch",
        ),
        (
            {},
            {"fixture_path": "other.pdf"},
            "fixture_path mismatch",
        ),
        (
            {},
            {"fixture_type": "other_pdf"},
            "fixture_type mismatch",
        ),
        (
            {},
            {"extraction_mode": "other_mode"},
            "extraction_mode mismatch",
        ),
    ),
)
def test_does_not_read_file_when_gate_or_identity_check_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    execution_overrides: dict[str, object],
    request_overrides: dict[str, object],
    expected_reason: str,
) -> None:
    pdf_path = tmp_path / "must-not-be-read.pdf"

    def fail_if_called(fixture_path: str) -> str:
        raise AssertionError(f"read attempted for {fixture_path}")

    monkeypatch.setattr(
        implementation_module,
        "_extract_text_from_pdf",
        fail_if_called,
    )

    result = _extract(
        _request(
            str(pdf_path),
            execution_overrides=execution_overrides,
            **request_overrides,
        ),
    )

    assert isinstance(result, ControlledPdfTextExtractionResultContractResult)
    assert result.allowed is False
    assert result.reason == expected_reason


def test_unreadable_file_becomes_deterministic_result_contract_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_path = tmp_path / "missing-product-spec.pdf"

    def unreadable_parser(fixture_path: str) -> object:
        raise OSError(fixture_path)

    monkeypatch.setattr(implementation_module, "_PDF_READER", unreadable_parser)

    result = _extract(_request(str(pdf_path)))

    assert isinstance(result, ControlledPdfTextExtractionResultContractResult)
    assert result.allowed is True
    assert result.extraction_status == "unreadable"
    assert result.extraction_error == "pdf file is unreadable"
    assert result.text_length == 0
    assert result.text_preview == ""


def test_parser_error_becomes_deterministic_result_contract_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_path = _write_invalid_pdf(tmp_path)

    def failing_parser(fixture_path: str) -> object:
        raise ValueError(fixture_path)

    monkeypatch.setattr(implementation_module, "_PDF_READER", failing_parser)

    result = _extract(_request(str(pdf_path)))

    assert isinstance(result, ControlledPdfTextExtractionResultContractResult)
    assert result.allowed is True
    assert result.extraction_status == "parser_error"
    assert result.extraction_error == "pdf parser error"
    assert result.text_length == 0
    assert result.text_preview == ""


def test_final_output_is_always_result_contract_result(tmp_path: Path) -> None:
    pdf_path = _write_minimal_pdf(tmp_path)

    result = _extract(_request(str(pdf_path)))

    assert isinstance(result, ControlledPdfTextExtractionResultContractResult)


def test_contract_module_has_no_forbidden_downstream_dependencies() -> None:
    source = inspect.getsource(implementation_module)

    forbidden_fragments = (
        "CreativeAssetTypeDetector",
        "CreativeAssetBatchScanner",
        "OfficialKnowledge",
        "ProductKnowledge",
        "PromptCandidate",
        "EvidenceCollection",
        "KnowledgeRepository",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source


def test_contract_module_has_no_folder_scanning_fragments() -> None:
    source = inspect.getsource(implementation_module)

    forbidden_fragments = (
        "iterdir",
        "rglob",
        "scandir",
        "walk(",
        "glob(",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
