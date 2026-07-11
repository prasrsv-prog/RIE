from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    PERMITTED_STRUCTURAL_FIELDS,
    STRUCTURAL_METADATA_ONLY_MODE,
    ControlledPdfStructuralMetadataContract,
)
from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContract,
    ControlledRealAssetFixtureItem,
)


def _fixture_contract_result(
    *,
    fixture_type: str = "product_spec_pdf",
):
    return ControlledRealAssetFixtureContract.evaluate(
        fixtures=(
            ControlledRealAssetFixtureItem(
                fixture_id="fixture-1",
                source_label="controlled fixture",
                fixture_path="sandbox/fixture.pdf",
                fixture_type=fixture_type,
                allowed_for_metadata=True,
                allowed_for_pdf_text_extraction=False,
                allowed_for_image_metadata=False,
                allowed_for_evidence=False,
                notes="",
            ),
        )
    )


def test_allows_approved_structural_metadata_contract() -> None:
    result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-1",
        notes="approved review",
    )

    assert result.allowed is True
    assert result.reason == "pdf structural metadata contract allowed"
    assert result.fixture_id == "fixture-1"
    assert result.fixture_type == "product_spec_pdf"
    assert result.inspection_mode == STRUCTURAL_METADATA_ONLY_MODE
    assert result.permitted_fields == PERMITTED_STRUCTURAL_FIELDS
    assert result.evidence_allowed is False


def test_blocks_missing_fixture_id() -> None:
    result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="",
    )

    assert result.allowed is False
    assert result.reason == "fixture_id is required"


def test_blocks_unknown_fixture_id() -> None:
    result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="missing",
    )

    assert result.allowed is False
    assert result.reason == "fixture_id not found"


def test_blocks_non_pdf_fixture_type() -> None:
    result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=_fixture_contract_result(
            fixture_type="product_photo_jpeg",
        ),
        fixture_id="fixture-1",
    )

    assert result.allowed is False
    assert result.reason == "fixture_type must be product_spec_pdf"


def test_blocks_unsupported_inspection_mode() -> None:
    result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-1",
        inspection_mode="text_only",
    )

    assert result.allowed is False
    assert result.reason == (
        "inspection_mode must be structural_metadata_only"
    )


def test_blocks_unapproved_permitted_fields() -> None:
    result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-1",
        permitted_fields=("page_count",),
    )

    assert result.allowed is False
    assert result.reason == (
        "permitted_fields must match the approved field set"
    )


def test_blocks_evidence_creation() -> None:
    result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id="fixture-1",
        allow_evidence_creation=True,
    )

    assert result.allowed is False
    assert result.reason == (
        "evidence creation is not allowed by this contract"
    )


def test_blocks_disallowed_upstream_contract() -> None:
    result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=ControlledRealAssetFixtureContract.evaluate(
            fixtures=(),
            max_items=0,
        ),
        fixture_id="fixture-1",
    )

    assert result.allowed is False
    assert result.reason == "fixture contract is not allowed"