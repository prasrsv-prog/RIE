from math import nan

from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    ControlledPdfStructuralMetadataContract,
)
from rie.ingestion.controlled_pdf_structural_metadata_execution_contract import (
    ControlledPdfStructuralMetadataExecutionContract,
)
from rie.ingestion.controlled_pdf_structural_metadata_result_contract import (
    ENCRYPTED_ERROR,
    MAX_INSPECTION_ERROR_CHARACTERS,
    PARTIAL_INSPECTION_ERROR,
    ControlledPdfStructuralMetadataPageItem,
    ControlledPdfStructuralMetadataResultContract,
    ControlledPdfStructuralMetadataResultInput,
)
from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContract,
    ControlledRealAssetFixtureItem,
)


FIXTURE_ID = "fixture-1"
FIXTURE_PATH = "synthetic/fixture.pdf"
MAX_PAGES = 3


def _execution_contract_result(
    *,
    allow_execution: bool = True,
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


def _page(
    page_index: int,
    *,
    status: str = "inspected",
    width: float = 612.0,
    height: float = 792.0,
    rotation: int = 0,
) -> ControlledPdfStructuralMetadataPageItem:
    return ControlledPdfStructuralMetadataPageItem(
        page_index=page_index,
        width_points=width,
        height_points=height,
        rotation_degrees=rotation,
        inspection_status=status,
    )


def _result_input(**overrides):
    values = {
        "fixture_id": FIXTURE_ID,
        "source_label": "synthetic result",
        "fixture_path": FIXTURE_PATH,
        "fixture_type": "product_spec_pdf",
        "inspection_mode": "structural_metadata_only",
        "inspection_status": "inspected",
        "encrypted": False,
        "page_count": 2,
        "inspected_page_count": 2,
        "page_details_truncated": False,
        "page_details": (_page(0), _page(1, rotation=90)),
        "max_inspected_pages": MAX_PAGES,
        "inspection_error": "",
        "evidence_allowed": False,
        "notes": "",
    }
    values.update(overrides)
    return ControlledPdfStructuralMetadataResultInput(**values)


def test_allows_zero_page_inspected_result() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            page_count=0,
            inspected_page_count=0,
            page_details=(),
        ),
    )

    assert result.allowed is True
    assert result.inspection_status == "inspected"
    assert result.page_count == 0
    assert result.page_details == ()
    assert result.evidence_allowed is False


def test_allows_inspected_result() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(),
    )

    assert result.allowed is True
    assert result.reason == (
        "pdf structural metadata result contract allowed"
    )
    assert result.inspected_page_count == 2
    assert len(result.page_details) == 2
    assert result.evidence_allowed is False


def test_allows_bounded_result() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            inspection_status="bounded",
            page_count=8,
            inspected_page_count=3,
            page_details_truncated=True,
            page_details=(_page(0), _page(1), _page(2)),
        ),
    )

    assert result.allowed is True
    assert result.inspection_status == "bounded"
    assert result.page_details_truncated is True


def test_allows_partial_result() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            inspection_status="partial",
            page_details=(
                _page(0),
                _page(
                    1,
                    status="page_error",
                    width=0,
                    height=0,
                    rotation=0,
                ),
            ),
            inspection_error=PARTIAL_INSPECTION_ERROR,
        ),
    )

    assert result.allowed is True
    assert result.inspection_status == "partial"
    assert result.inspection_error == PARTIAL_INSPECTION_ERROR


def test_allows_encrypted_result() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            inspection_status="encrypted",
            encrypted=True,
            page_count=0,
            inspected_page_count=0,
            page_details=(),
            inspection_error=ENCRYPTED_ERROR,
        ),
    )

    assert result.allowed is True
    assert result.encrypted is True
    assert result.page_count == 0


def test_blocks_missing_execution_contract_result() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=None,
        result_input=_result_input(),
    )

    assert result.allowed is False
    assert result.reason == "execution contract result is required"


def test_blocks_disallowed_execution_contract() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(
            allow_execution=False,
        ),
        result_input=_result_input(),
    )

    assert result.allowed is False
    assert result.reason == "execution contract is not allowed"


def test_blocks_fixture_identity_mismatch() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(fixture_id="other-fixture"),
    )

    assert result.allowed is False
    assert result.reason == "fixture_id mismatch"


def test_blocks_maximum_page_mismatch() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(max_inspected_pages=2),
    )

    assert result.allowed is False
    assert result.reason == "max_inspected_pages mismatch"


def test_blocks_negative_page_count() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            page_count=-1,
            inspected_page_count=0,
            page_details=(),
        ),
    )

    assert result.allowed is False
    assert result.reason == "page_count must not be negative"


def test_blocks_page_detail_count_mismatch() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(inspected_page_count=1),
    )

    assert result.allowed is False
    assert result.reason == (
        "inspected_page_count must match page_details count"
    )


def test_blocks_non_contiguous_page_indices() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            page_details=(_page(0), _page(2)),
        ),
    )

    assert result.allowed is False
    assert result.reason == (
        "page indices must form a contiguous zero-based prefix"
    )


def test_blocks_zero_dimension_for_inspected_page() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            page_count=1,
            inspected_page_count=1,
            page_details=(_page(0, width=0),),
        ),
    )

    assert result.allowed is False
    assert result.reason == (
        "inspected page width must be greater than zero"
    )


def test_blocks_nan_dimension() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            page_count=1,
            inspected_page_count=1,
            page_details=(_page(0, width=nan),),
        ),
    )

    assert result.allowed is False
    assert result.reason == "page width must be a finite numeric value"


def test_blocks_invalid_rotation() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            page_count=1,
            inspected_page_count=1,
            page_details=(_page(0, rotation=45),),
        ),
    )

    assert result.allowed is False
    assert result.reason == "unsupported page rotation"


def test_blocks_incorrect_truncation_flag() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(page_details_truncated=True),
    )

    assert result.allowed is False
    assert result.reason == (
        "page_details_truncated does not match page boundary"
    )


def test_blocks_partial_result_without_mixed_page_statuses() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            inspection_status="partial",
            inspection_error=PARTIAL_INSPECTION_ERROR,
        ),
    )

    assert result.allowed is False
    assert result.reason == (
        "partial status requires mixed page statuses"
    )


def test_blocks_fatal_result_with_page_details() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            inspection_status="encrypted",
            encrypted=True,
            page_count=2,
            inspection_error=ENCRYPTED_ERROR,
        ),
    )

    assert result.allowed is False
    assert result.reason == "fatal status requires zero page_count"


def test_blocks_oversized_inspection_error() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            inspection_status="parser_error",
            page_count=0,
            inspected_page_count=0,
            page_details=(),
            inspection_error=(
                "x" * (MAX_INSPECTION_ERROR_CHARACTERS + 1)
            ),
        ),
    )

    assert result.allowed is False
    assert result.reason == (
        "inspection_error exceeds result contract limit"
    )


def test_blocks_evidence_authority() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(evidence_allowed=True),
    )

    assert result.allowed is False
    assert result.reason == (
        "evidence creation is not allowed by this contract"
    )


def test_blocks_mutable_page_details_collection() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(
            page_details=[_page(0), _page(1)],
        ),
    )

    assert result.allowed is False
    assert result.reason == "page_details must be a tuple"


def test_blocks_boolean_page_count() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(page_count=True),
    )

    assert result.allowed is False
    assert result.reason == "page_count must be an integer"


def test_blocks_encrypted_true_for_inspected_status() -> None:
    result = ControlledPdfStructuralMetadataResultContract.evaluate(
        execution_contract_result=_execution_contract_result(),
        result_input=_result_input(encrypted=True),
    )

    assert result.allowed is False
    assert result.reason == (
        "encrypted must be false for non-encrypted status"
    )