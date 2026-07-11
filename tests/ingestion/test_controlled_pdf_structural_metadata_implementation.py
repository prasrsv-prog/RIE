from dataclasses import replace
from math import inf

import pytest

import rie.ingestion.controlled_pdf_structural_metadata_implementation as implementation_module
from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    ControlledPdfStructuralMetadataContract,
)
from rie.ingestion.controlled_pdf_structural_metadata_execution_contract import (
    ControlledPdfStructuralMetadataExecutionContract,
)
from rie.ingestion.controlled_pdf_structural_metadata_implementation import (
    ControlledPdfStructuralMetadataImplementation,
    ControlledPdfStructuralMetadataImplementationRequest,
)
from rie.ingestion.controlled_pdf_structural_metadata_result_contract import (
    ENCRYPTED_ERROR,
    PARSER_ERROR,
    PARSER_UNAVAILABLE_ERROR,
    PARTIAL_INSPECTION_ERROR,
    REQUEST_REQUIRED_ERROR,
    SAFETY_CHECK_ERROR,
    UNREADABLE_ERROR,
)
from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContract,
    ControlledRealAssetFixtureItem,
)


FIXTURE_ID = "implementation-fixture"
FIXTURE_PATH = "synthetic/implementation-fixture.pdf"
MAX_PAGES = 3


class _FakeMediaBox:
    def __init__(
        self,
        *,
        width=612.0,
        height=792.0,
    ):
        self.width = width
        self.height = height


class _FakePage:
    def __init__(
        self,
        *,
        width=612.0,
        height=792.0,
        rotation=0,
        media_box_error=None,
        rotation_error=None,
    ):
        self._media_box = _FakeMediaBox(
            width=width,
            height=height,
        )
        self._rotation = rotation
        self._media_box_error = media_box_error
        self._rotation_error = rotation_error

    @property
    def mediabox(self):
        if self._media_box_error is not None:
            raise self._media_box_error

        return self._media_box

    @property
    def rotation(self):
        if self._rotation_error is not None:
            raise self._rotation_error

        return self._rotation

    def extract_text(self):
        raise AssertionError("text extraction must not be called")


class _FakePages:
    def __init__(
        self,
        pages,
        *,
        length_error=None,
    ):
        self._pages = tuple(pages)
        self._length_error = length_error
        self.accessed_indices = []

    def __len__(self):
        if self._length_error is not None:
            raise self._length_error

        return len(self._pages)

    def __getitem__(self, index):
        self.accessed_indices.append(index)

        value = self._pages[index]

        if isinstance(value, BaseException):
            raise value

        return value


class _FakeReader:
    def __init__(
        self,
        pages,
        *,
        encrypted=False,
    ):
        self._pages = pages
        self._encrypted = encrypted

    @property
    def is_encrypted(self):
        return self._encrypted

    @property
    def pages(self):
        return self._pages

    @property
    def metadata(self):
        raise AssertionError("document metadata must not be accessed")


class _EncryptedReader:
    @property
    def is_encrypted(self):
        return True

    @property
    def pages(self):
        raise AssertionError(
            "encrypted pages must not be accessed"
        )

    @property
    def metadata(self):
        raise AssertionError("document metadata must not be accessed")


def _execution_contract_result(
    *,
    allow_execution=True,
):
    fixture_result = ControlledRealAssetFixtureContract.evaluate(
        fixtures=(
            ControlledRealAssetFixtureItem(
                fixture_id=FIXTURE_ID,
                source_label="controlled fixture",
                fixture_path=FIXTURE_PATH,
                fixture_type="product_spec_pdf",
                allowed_for_metadata=True,
                allowed_for_pdf_text_extraction=False,
                allowed_for_image_metadata=False,
                allowed_for_evidence=False,
                notes="",
            ),
        )
    )

    metadata_result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=fixture_result,
        fixture_id=FIXTURE_ID,
        notes="metadata contract",
    )

    return ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=metadata_result,
        allow_execution=allow_execution,
        max_inspected_pages=MAX_PAGES,
        notes="execution contract",
    )


def _request(**overrides):
    values = {
        "execution_contract_result": (
            _execution_contract_result()
        ),
        "source_label": "controlled implementation test",
        "allow_implementation_execution": True,
        "notes": "value-only parser test",
    }
    values.update(overrides)

    return ControlledPdfStructuralMetadataImplementationRequest(
        **values
    )


def _install_reader(monkeypatch, reader):
    calls = []

    def reader_factory(path):
        calls.append(path)
        return reader

    monkeypatch.setattr(
        implementation_module,
        "PdfReader",
        reader_factory,
    )

    return calls


def _execute_with_pages(monkeypatch, pages):
    fake_pages = _FakePages(pages)
    fake_reader = _FakeReader(fake_pages)
    calls = _install_reader(monkeypatch, fake_reader)

    result = ControlledPdfStructuralMetadataImplementation.execute(
        _request()
    )

    return result, fake_pages, calls


def test_requires_explicit_implementation_approval(
    monkeypatch,
) -> None:
    def forbidden_reader(path):
        raise AssertionError("reader must not be constructed")

    monkeypatch.setattr(
        implementation_module,
        "PdfReader",
        forbidden_reader,
    )

    result = ControlledPdfStructuralMetadataImplementation.execute(
        _request(allow_implementation_execution=False)
    )

    assert result.allowed is False
    assert result.inspection_status == "blocked"
    assert result.inspection_error == REQUEST_REQUIRED_ERROR
    assert result.evidence_allowed is False


def test_invalid_execution_authority_blocks_before_reader(
    monkeypatch,
) -> None:
    def forbidden_reader(path):
        raise AssertionError("reader must not be constructed")

    monkeypatch.setattr(
        implementation_module,
        "PdfReader",
        forbidden_reader,
    )

    result = ControlledPdfStructuralMetadataImplementation.execute(
        _request(
            execution_contract_result=(
                _execution_contract_result(
                    allow_execution=False,
                )
            )
        )
    )

    assert result.allowed is False
    assert result.inspection_status == "blocked"
    assert result.inspection_error == SAFETY_CHECK_ERROR


def test_parser_unavailable_result(monkeypatch) -> None:
    monkeypatch.setattr(
        implementation_module,
        "PdfReader",
        None,
    )

    result = ControlledPdfStructuralMetadataImplementation.execute(
        _request()
    )

    assert result.allowed is True
    assert result.inspection_status == "parser_unavailable"
    assert result.inspection_error == PARSER_UNAVAILABLE_ERROR
    assert result.page_details == ()
    assert result.evidence_allowed is False


def test_encrypted_result_does_not_access_pages(
    monkeypatch,
) -> None:
    calls = _install_reader(monkeypatch, _EncryptedReader())

    result = ControlledPdfStructuralMetadataImplementation.execute(
        _request()
    )

    assert calls == [FIXTURE_PATH]
    assert result.allowed is True
    assert result.inspection_status == "encrypted"
    assert result.encrypted is True
    assert result.inspection_error == ENCRYPTED_ERROR
    assert result.page_count == 0
    assert result.page_details == ()


def test_zero_page_document_is_inspected(monkeypatch) -> None:
    result, fake_pages, calls = _execute_with_pages(
        monkeypatch,
        [],
    )

    assert calls == [FIXTURE_PATH]
    assert fake_pages.accessed_indices == []
    assert result.allowed is True
    assert result.inspection_status == "inspected"
    assert result.page_count == 0
    assert result.inspected_page_count == 0
    assert result.page_details == ()
    assert result.page_details_truncated is False


def test_normal_document_is_inspected(monkeypatch) -> None:
    result, fake_pages, calls = _execute_with_pages(
        monkeypatch,
        [
            _FakePage(rotation=0),
            _FakePage(rotation=90),
        ],
    )

    assert calls == [FIXTURE_PATH]
    assert fake_pages.accessed_indices == [0, 1]
    assert result.allowed is True
    assert result.inspection_status == "inspected"
    assert result.page_count == 2
    assert result.inspected_page_count == 2
    assert result.page_details_truncated is False
    assert result.page_details[0].width_points == 612.0
    assert result.page_details[1].rotation_degrees == 90


def test_document_above_page_limit_is_bounded(
    monkeypatch,
) -> None:
    result, fake_pages, _ = _execute_with_pages(
        monkeypatch,
        [
            _FakePage(),
            _FakePage(),
            _FakePage(),
            _FakePage(),
            _FakePage(),
        ],
    )

    assert result.allowed is True
    assert result.inspection_status == "bounded"
    assert result.page_count == 5
    assert result.inspected_page_count == MAX_PAGES
    assert result.page_details_truncated is True
    assert fake_pages.accessed_indices == [0, 1, 2]


def test_one_page_failure_creates_partial_result(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [
            _FakePage(),
            _FakePage(rotation=45),
        ],
    )

    assert result.allowed is True
    assert result.inspection_status == "partial"
    assert result.inspection_error == PARTIAL_INSPECTION_ERROR
    assert result.page_details[0].inspection_status == "inspected"
    assert result.page_details[1].inspection_status == "page_error"
    assert result.page_details[1].width_points == 0
    assert result.page_details[1].height_points == 0


def test_all_bounded_pages_failing_maps_to_parser_error(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [
            _FakePage(rotation=45),
            _FakePage(width=0),
        ],
    )

    assert result.allowed is True
    assert result.inspection_status == "parser_error"
    assert result.inspection_error == PARSER_ERROR
    assert result.page_count == 0
    assert result.inspected_page_count == 0
    assert result.page_details == ()


def test_reader_construction_oserror_maps_to_unreadable(
    monkeypatch,
) -> None:
    def reader_factory(path):
        raise OSError("raw operating-system message")

    monkeypatch.setattr(
        implementation_module,
        "PdfReader",
        reader_factory,
    )

    result = ControlledPdfStructuralMetadataImplementation.execute(
        _request()
    )

    assert result.allowed is True
    assert result.inspection_status == "unreadable"
    assert result.inspection_error == UNREADABLE_ERROR
    assert "raw operating-system message" not in result.reason


def test_reader_construction_generic_error_maps_to_parser_error(
    monkeypatch,
) -> None:
    def reader_factory(path):
        raise RuntimeError("raw parser message")

    monkeypatch.setattr(
        implementation_module,
        "PdfReader",
        reader_factory,
    )

    result = ControlledPdfStructuralMetadataImplementation.execute(
        _request()
    )

    assert result.allowed is True
    assert result.inspection_status == "parser_error"
    assert result.inspection_error == PARSER_ERROR
    assert "raw parser message" not in result.reason


def test_page_count_error_maps_to_parser_error(
    monkeypatch,
) -> None:
    fake_pages = _FakePages(
        [],
        length_error=RuntimeError("page count failed"),
    )
    fake_reader = _FakeReader(fake_pages)
    _install_reader(monkeypatch, fake_reader)

    result = ControlledPdfStructuralMetadataImplementation.execute(
        _request()
    )

    assert result.allowed is True
    assert result.inspection_status == "parser_error"
    assert result.inspection_error == PARSER_ERROR
    assert result.page_details == ()


@pytest.mark.parametrize(
    ("rotation", "expected_rotation"),
    (
        (None, 0),
        (360, 0),
        (450, 90),
        (-90, 270),
    ),
)
def test_rotation_is_normalized(
    monkeypatch,
    rotation,
    expected_rotation,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [_FakePage(rotation=rotation)],
    )

    assert result.allowed is True
    assert result.inspection_status == "inspected"
    assert (
        result.page_details[0].rotation_degrees
        == expected_rotation
    )


def test_invalid_rotation_creates_page_error(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [
            _FakePage(),
            _FakePage(rotation=45),
        ],
    )

    assert result.inspection_status == "partial"
    assert result.page_details[1].inspection_status == "page_error"


def test_invalid_width_creates_page_error(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [
            _FakePage(),
            _FakePage(width=0),
        ],
    )

    assert result.inspection_status == "partial"
    assert result.page_details[1].inspection_status == "page_error"


def test_invalid_height_creates_page_error(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [
            _FakePage(),
            _FakePage(height=-1),
        ],
    )

    assert result.inspection_status == "partial"
    assert result.page_details[1].inspection_status == "page_error"


def test_non_finite_dimension_creates_page_error(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [
            _FakePage(),
            _FakePage(width=inf),
        ],
    )

    assert result.inspection_status == "partial"
    assert result.page_details[1].inspection_status == "page_error"


def test_bounded_access_never_exceeds_maximum(
    monkeypatch,
) -> None:
    result, fake_pages, _ = _execute_with_pages(
        monkeypatch,
        [_FakePage() for _ in range(20)],
    )

    assert result.inspection_status == "bounded"
    assert fake_pages.accessed_indices == [0, 1, 2]
    assert max(fake_pages.accessed_indices) < MAX_PAGES


def test_document_metadata_is_never_accessed(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [_FakePage()],
    )

    assert result.allowed is True
    assert result.inspection_status == "inspected"


def test_page_text_extraction_is_never_called(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [_FakePage()],
    )

    assert result.allowed is True
    assert result.inspection_status == "inspected"


def test_result_always_disables_evidence(
    monkeypatch,
) -> None:
    result, _, _ = _execute_with_pages(
        monkeypatch,
        [_FakePage()],
    )

    assert result.allowed is True
    assert result.evidence_allowed is False


def test_invalid_request_type_is_blocked(
    monkeypatch,
) -> None:
    def forbidden_reader(path):
        raise AssertionError("reader must not be constructed")

    monkeypatch.setattr(
        implementation_module,
        "PdfReader",
        forbidden_reader,
    )

    result = ControlledPdfStructuralMetadataImplementation.execute(
        None
    )

    assert result.allowed is False
    assert result.inspection_status == "blocked"
    assert result.inspection_error == SAFETY_CHECK_ERROR
    assert result.evidence_allowed is False