from dataclasses import FrozenInstanceError
import inspect

import pytest

from rie.ingestion import controlled_real_asset_fixture_contract as fixture_contract_module
from rie.ingestion.controlled_real_asset_fixture_contract import (
    ALLOWED_FIXTURE_TYPES,
    ControlledRealAssetFixtureContract,
    ControlledRealAssetFixtureItem,
)


def _fixture(**overrides: object) -> ControlledRealAssetFixtureItem:
    values = {
        "fixture_id": "fixture-001",
        "source_label": "sandbox copy",
        "fixture_path": "fixtures/product-spec.pdf",
        "fixture_type": "product_spec_pdf",
        "allowed_for_metadata": True,
        "allowed_for_pdf_text_extraction": False,
        "allowed_for_image_metadata": False,
        "allowed_for_evidence": False,
        "notes": "",
    }
    values.update(overrides)
    return ControlledRealAssetFixtureItem(**values)


def _fixtures(count: int) -> tuple[ControlledRealAssetFixtureItem, ...]:
    return tuple(
        _fixture(
            fixture_id=f"fixture-{index}",
            fixture_path=f"fixtures/fixture-{index}.dat",
            fixture_type=ALLOWED_FIXTURE_TYPES[index % len(ALLOWED_FIXTURE_TYPES)],
        )
        for index in range(count)
    )


def test_allows_empty_fixture_set_with_default_max_items() -> None:
    result = ControlledRealAssetFixtureContract.evaluate()

    assert result.allowed is True
    assert result.reason == "fixture contract allowed"
    assert result.fixture_count == 0
    assert result.fixtures == ()


def test_allows_one_product_spec_pdf_metadata_only_fixture() -> None:
    fixture = _fixture()

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is True
    assert result.reason == "fixture contract allowed"
    assert result.fixture_count == 1
    assert result.fixtures == (fixture,)


def test_allows_up_to_four_metadata_only_fixtures() -> None:
    fixtures = _fixtures(4)

    result = ControlledRealAssetFixtureContract.evaluate(fixtures)

    assert result.allowed is True
    assert result.reason == "fixture contract allowed"
    assert result.fixture_count == 4
    assert result.fixtures == fixtures


def test_rejects_max_items_less_than_or_equal_to_zero() -> None:
    result = ControlledRealAssetFixtureContract.evaluate(max_items=0)

    assert result.allowed is False
    assert result.reason == "max_items must be greater than zero"


def test_rejects_max_items_greater_than_four() -> None:
    result = ControlledRealAssetFixtureContract.evaluate(max_items=5)

    assert result.allowed is False
    assert result.reason == "max_items exceeds fixture contract limit"


def test_rejects_fixture_count_greater_than_max_items() -> None:
    fixtures = _fixtures(2)

    result = ControlledRealAssetFixtureContract.evaluate(fixtures, max_items=1)

    assert result.allowed is False
    assert result.reason == "fixture count exceeds max_items"
    assert result.fixture_count == 2
    assert result.fixtures == fixtures


def test_rejects_fixture_count_greater_than_four() -> None:
    fixtures = _fixtures(5)

    result = ControlledRealAssetFixtureContract.evaluate(fixtures)

    assert result.allowed is False
    assert result.reason == "fixture count exceeds fixture contract limit"
    assert result.fixture_count == 5
    assert result.fixtures == fixtures


def test_rejects_non_fixture_item() -> None:
    result = ControlledRealAssetFixtureContract.evaluate((object(),))

    assert result.allowed is False
    assert result.reason == "fixture must be ControlledRealAssetFixtureItem"


@pytest.mark.parametrize(
    ("field_name", "reason"),
    (
        ("fixture_id", "fixture_id is required"),
        ("source_label", "source_label is required"),
        ("fixture_path", "fixture_path is required"),
    ),
)
def test_rejects_empty_required_strings(field_name: str, reason: str) -> None:
    fixture = _fixture(**{field_name: "   "})

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is False
    assert result.reason == reason


def test_rejects_unsupported_fixture_type() -> None:
    fixture = _fixture(fixture_type="unknown_directory")

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is False
    assert result.reason == "unsupported fixture_type"


def test_rejects_notes_none() -> None:
    fixture = _fixture(notes=None)

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is False
    assert result.reason == "notes is required"


def test_rejects_allowed_for_metadata_false() -> None:
    fixture = _fixture(allowed_for_metadata=False)

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is False
    assert result.reason == "metadata access must be allowed"


def test_rejects_allowed_for_pdf_text_extraction_true() -> None:
    fixture = _fixture(allowed_for_pdf_text_extraction=True)

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is False
    assert result.reason == "pdf text extraction is not allowed by this contract"


def test_rejects_allowed_for_image_metadata_true() -> None:
    fixture = _fixture(allowed_for_image_metadata=True)

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is False
    assert result.reason == "image metadata is not allowed by this contract"


def test_rejects_allowed_for_evidence_true() -> None:
    fixture = _fixture(allowed_for_evidence=True)

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is False
    assert result.reason == "evidence creation is not allowed by this contract"


def test_rejects_duplicate_fixture_id() -> None:
    first = _fixture(fixture_id="duplicate", fixture_path="fixtures/one.pdf")
    second = _fixture(fixture_id="duplicate", fixture_path="fixtures/two.pdf")

    result = ControlledRealAssetFixtureContract.evaluate((first, second))

    assert result.allowed is False
    assert result.reason == "duplicate fixture_id"


def test_rejects_duplicate_fixture_path() -> None:
    first = _fixture(fixture_id="one", fixture_path="fixtures/duplicate.pdf")
    second = _fixture(fixture_id="two", fixture_path="fixtures/duplicate.pdf")

    result = ControlledRealAssetFixtureContract.evaluate((first, second))

    assert result.allowed is False
    assert result.reason == "duplicate fixture_path"


def test_fixture_path_string_is_preserved_exactly_and_not_normalized() -> None:
    fixture_path = "fixtures\\sandbox\\..\\selected product spec.pdf"
    fixture = _fixture(fixture_path=fixture_path)

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is True
    assert result.fixtures[0].fixture_path == fixture_path


def test_fixture_type_is_not_inferred_from_fixture_path() -> None:
    fixture = _fixture(
        fixture_path="fixtures/product-photo.jpg",
        fixture_type="product_spec_pdf",
    )

    result = ControlledRealAssetFixtureContract.evaluate((fixture,))

    assert result.allowed is True
    assert result.fixtures[0].fixture_type == "product_spec_pdf"


def test_result_fixtures_are_tuple() -> None:
    result = ControlledRealAssetFixtureContract.evaluate([_fixture()])

    assert isinstance(result.fixtures, tuple)


def test_fixture_item_is_immutable() -> None:
    fixture = _fixture()

    with pytest.raises(FrozenInstanceError):
        fixture.fixture_path = "fixtures/changed.pdf"


def test_contract_module_has_no_filesystem_or_scanner_dependencies() -> None:
    source = inspect.getsource(fixture_contract_module)

    forbidden_fragments = (
        "Path(",
        "pathlib",
        "os.",
        "open(",
        "read_bytes",
        "read_text",
        "CreativeAssetTypeDetector",
        "CreativeAssetBatchScanner",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
