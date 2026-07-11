from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    ControlledPdfStructuralMetadataContract,
)
from rie.ingestion.controlled_pdf_structural_metadata_execution_contract import (
    MAX_INSPECTED_PAGES_LIMIT,
    ControlledPdfStructuralMetadataExecutionContract,
)
from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContract,
    ControlledRealAssetFixtureItem,
)


def _metadata_contract_result():
    fixture_result = ControlledRealAssetFixtureContract.evaluate(
        fixtures=(
            ControlledRealAssetFixtureItem(
                fixture_id="fixture-1",
                source_label="controlled fixture",
                fixture_path="sandbox/fixture.pdf",
                fixture_type="product_spec_pdf",
                allowed_for_metadata=True,
                allowed_for_pdf_text_extraction=False,
                allowed_for_image_metadata=False,
                allowed_for_evidence=False,
                notes="",
            ),
        )
    )

    return ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=fixture_result,
        fixture_id="fixture-1",
        notes="contract review",
    )


def test_allows_approved_execution_contract() -> None:
    result = ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=_metadata_contract_result(),
        allow_execution=True,
        max_inspected_pages=MAX_INSPECTED_PAGES_LIMIT,
        notes="approved execution boundary",
    )

    assert result.allowed is True
    assert result.reason == (
        "pdf structural metadata execution contract allowed"
    )
    assert result.execution_allowed is True
    assert result.max_inspected_pages == MAX_INSPECTED_PAGES_LIMIT
    assert result.allow_content_extraction is False
    assert result.allow_output_file_creation is False
    assert result.evidence_allowed is False


def test_blocks_missing_execution_approval() -> None:
    result = ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=_metadata_contract_result(),
        max_inspected_pages=1,
    )

    assert result.allowed is False
    assert result.reason == "execution approval is required"


def test_blocks_zero_page_limit() -> None:
    result = ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=_metadata_contract_result(),
        allow_execution=True,
        max_inspected_pages=0,
    )

    assert result.allowed is False
    assert result.reason == (
        "max_inspected_pages must be greater than zero"
    )


def test_blocks_page_limit_above_contract_limit() -> None:
    result = ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=_metadata_contract_result(),
        allow_execution=True,
        max_inspected_pages=MAX_INSPECTED_PAGES_LIMIT + 1,
    )

    assert result.allowed is False
    assert result.reason == (
        "max_inspected_pages exceeds execution contract limit"
    )


def test_blocks_content_extraction() -> None:
    result = ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=_metadata_contract_result(),
        allow_execution=True,
        max_inspected_pages=1,
        allow_content_extraction=True,
    )

    assert result.allowed is False
    assert result.reason == (
        "content extraction is not allowed by this contract"
    )


def test_blocks_output_file_creation() -> None:
    result = ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=_metadata_contract_result(),
        allow_execution=True,
        max_inspected_pages=1,
        allow_output_file_creation=True,
    )

    assert result.allowed is False
    assert result.reason == (
        "output file creation is not allowed by this contract"
    )


def test_blocks_evidence_creation() -> None:
    result = ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=_metadata_contract_result(),
        allow_execution=True,
        max_inspected_pages=1,
        allow_evidence_creation=True,
    )

    assert result.allowed is False
    assert result.reason == (
        "evidence creation is not allowed by this contract"
    )


def test_blocks_disallowed_upstream_contract() -> None:
    blocked_metadata_result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=ControlledRealAssetFixtureContract.evaluate(
            fixtures=(),
            max_items=0,
        ),
        fixture_id="fixture-1",
    )

    result = ControlledPdfStructuralMetadataExecutionContract.evaluate(
        metadata_contract_result=blocked_metadata_result,
        allow_execution=True,
        max_inspected_pages=1,
    )

    assert result.allowed is False
    assert result.reason == (
        "structural metadata contract is not allowed"
    )