from rie.ingestion.controlled_pdf_structural_metadata_contract import (
    PERMITTED_STRUCTURAL_FIELDS,
    STRUCTURAL_METADATA_ONLY_MODE,
    ControlledPdfStructuralMetadataContract,
)
from rie.ingestion.controlled_pdf_structural_metadata_execution_contract import (
    ControlledPdfStructuralMetadataExecutionContract,
)
from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContract,
    ControlledRealAssetFixtureItem,
)


FIXTURE_ID = "synthetic-pdf-structural-metadata"
FIXTURE_PATH = "synthetic/controlled-structural-metadata.pdf"
MAX_INSPECTED_PAGES = 3


def _fixture_contract_result():
    return ControlledRealAssetFixtureContract.evaluate(
        fixtures=(
            ControlledRealAssetFixtureItem(
                fixture_id=FIXTURE_ID,
                source_label="synthetic structural metadata fixture",
                fixture_path=FIXTURE_PATH,
                fixture_type="product_spec_pdf",
                allowed_for_metadata=True,
                allowed_for_pdf_text_extraction=False,
                allowed_for_image_metadata=False,
                allowed_for_evidence=False,
                notes="value-only synthetic contract verification",
            ),
        )
    )


def _metadata_contract_result():
    return ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=_fixture_contract_result(),
        fixture_id=FIXTURE_ID,
        notes="value-only structural metadata contract verification",
    )


def test_structural_metadata_contract_chain_allows_bounded_execution() -> None:
    fixture_result = _fixture_contract_result()

    assert fixture_result.allowed is True
    assert fixture_result.fixture_count == 1

    metadata_result = ControlledPdfStructuralMetadataContract.evaluate(
        fixture_contract_result=fixture_result,
        fixture_id=FIXTURE_ID,
        notes="value-only structural metadata contract verification",
    )

    assert metadata_result.allowed is True
    assert metadata_result.fixture_id == FIXTURE_ID
    assert metadata_result.fixture_path == FIXTURE_PATH
    assert metadata_result.fixture_type == "product_spec_pdf"
    assert metadata_result.inspection_mode == STRUCTURAL_METADATA_ONLY_MODE
    assert metadata_result.permitted_fields == (
        "encrypted",
        "page_count",
        "page_width_points",
        "page_height_points",
        "page_rotation_degrees",
    )
    assert metadata_result.permitted_fields == PERMITTED_STRUCTURAL_FIELDS
    assert metadata_result.evidence_allowed is False

    execution_result = (
        ControlledPdfStructuralMetadataExecutionContract.evaluate(
            metadata_contract_result=metadata_result,
            allow_execution=True,
            max_inspected_pages=MAX_INSPECTED_PAGES,
            notes="bounded value-only execution authority",
        )
    )

    assert execution_result.allowed is True
    assert execution_result.fixture_id == FIXTURE_ID
    assert execution_result.fixture_path == FIXTURE_PATH
    assert execution_result.fixture_type == "product_spec_pdf"
    assert execution_result.inspection_mode == STRUCTURAL_METADATA_ONLY_MODE
    assert execution_result.permitted_fields == PERMITTED_STRUCTURAL_FIELDS
    assert execution_result.execution_allowed is True
    assert execution_result.max_inspected_pages == MAX_INSPECTED_PAGES
    assert execution_result.allow_content_extraction is False
    assert execution_result.allow_output_file_creation is False
    assert execution_result.evidence_allowed is False


def test_fixture_metadata_authority_does_not_authorize_execution() -> None:
    metadata_result = _metadata_contract_result()

    assert metadata_result.allowed is True

    execution_result = (
        ControlledPdfStructuralMetadataExecutionContract.evaluate(
            metadata_contract_result=metadata_result,
            allow_execution=False,
            max_inspected_pages=MAX_INSPECTED_PAGES,
        )
    )

    assert execution_result.allowed is False
    assert execution_result.reason == "execution approval is required"
    assert execution_result.execution_allowed is False
    assert execution_result.evidence_allowed is False


def test_execution_contract_blocks_content_extraction() -> None:
    metadata_result = _metadata_contract_result()

    assert metadata_result.allowed is True

    execution_result = (
        ControlledPdfStructuralMetadataExecutionContract.evaluate(
            metadata_contract_result=metadata_result,
            allow_execution=True,
            max_inspected_pages=MAX_INSPECTED_PAGES,
            allow_content_extraction=True,
        )
    )

    assert execution_result.allowed is False
    assert execution_result.reason == (
        "content extraction is not allowed by this contract"
    )
    assert execution_result.allow_content_extraction is True
    assert execution_result.allow_output_file_creation is False
    assert execution_result.evidence_allowed is False