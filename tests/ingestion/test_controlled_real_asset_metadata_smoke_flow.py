from dataclasses import fields
import inspect
import sys

from rie.ingestion.controlled_real_asset_fixture_contract import (
    ControlledRealAssetFixtureContract,
    ControlledRealAssetFixtureItem,
)
from rie.ingestion.real_asset_dry_run_contract import RealAssetDryRunContract
from rie.ingestion.real_asset_metadata_collection_contract import (
    RealAssetMetadataCollectionContract,
)
from rie.ingestion.real_asset_metadata_collector import (
    RealAssetMetadataCollectionRequest,
    RealAssetMetadataCollector,
)
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunBoundary,
    RealAssetMetadataDryRunItem,
)
from rie.ingestion.real_asset_sandbox_policy import RealAssetSandboxPolicy
from rie.ingestion.real_filesystem_metadata_adapter import (
    RealFilesystemMetadataAdapter,
    RealFilesystemMetadataAdapterRequest,
)
from rie.ingestion.real_filesystem_metadata_adapter_safety_contract import (
    RealFilesystemMetadataAdapterSafetyContract,
)


def _write_placeholder_files(fixture_root):
    spec = fixture_root / "product-spec.pdf"
    photo_jpg = fixture_root / "product-photo-1.jpg"
    photo_png = fixture_root / "product-photo-2.png"

    spec.write_bytes(b"synthetic pdf placeholder")
    photo_jpg.write_bytes(b"synthetic jpg placeholder")
    photo_png.write_bytes(b"synthetic png placeholder")

    return spec, photo_jpg, photo_png


def _fixture_item(
    *,
    fixture_id: str,
    fixture_path: str,
    fixture_type: str,
    allowed_for_pdf_text_extraction: bool = False,
    allowed_for_evidence: bool = False,
) -> ControlledRealAssetFixtureItem:
    return ControlledRealAssetFixtureItem(
        fixture_id=fixture_id,
        source_label="synthetic sandbox copy",
        fixture_path=fixture_path,
        fixture_type=fixture_type,
        allowed_for_metadata=True,
        allowed_for_pdf_text_extraction=allowed_for_pdf_text_extraction,
        allowed_for_image_metadata=False,
        allowed_for_evidence=allowed_for_evidence,
        notes="",
    )


def _fixture_items(fixture_root) -> tuple[ControlledRealAssetFixtureItem, ...]:
    spec, photo_jpg, photo_png = _write_placeholder_files(fixture_root)
    return (
        _fixture_item(
            fixture_id="fixture-product-spec",
            fixture_path=str(spec),
            fixture_type="product_spec_pdf",
        ),
        _fixture_item(
            fixture_id="fixture-product-photo-1",
            fixture_path=str(photo_jpg),
            fixture_type="product_photo_jpeg",
        ),
        _fixture_item(
            fixture_id="fixture-product-photo-2",
            fixture_path=str(photo_png),
            fixture_type="product_photo_png",
        ),
    )


def _run_metadata_flow_after_fixture_contract(
    *,
    fixture_contract_result,
    root,
    collection_allow_filesystem_metadata: bool = False,
):
    if fixture_contract_result.allowed is False:
        return {
            "fixture_contract": fixture_contract_result,
            "sandbox_decision": None,
            "dry_run_result": None,
            "metadata_boundary": None,
            "collection_decision": None,
            "safety_decision": None,
            "adapter_result": None,
            "collector_result": None,
        }

    sandbox_decision = RealAssetSandboxPolicy.evaluate(
        root=root,
        recursive=False,
        read_only=True,
        allow_real_asset_reads=False,
        allow_mutation=False,
    )
    dry_run_result = RealAssetDryRunContract.evaluate(
        sandbox_decision=sandbox_decision,
        mode="metadata_only",
        planned_scan_allowed=False,
        planned_real_asset_reads_allowed=False,
        planned_mutation_allowed=False,
    )
    metadata_boundary = RealAssetMetadataDryRunBoundary.evaluate(
        dry_run_result=dry_run_result,
        items=(),
    )
    collection_decision = RealAssetMetadataCollectionContract.evaluate(
        boundary_result=metadata_boundary,
        allow_filesystem_metadata=collection_allow_filesystem_metadata,
        allow_recursive_collection=False,
        allow_content_reads=False,
        allow_mutation=False,
    )
    safety_decision = RealFilesystemMetadataAdapterSafetyContract.evaluate(
        max_items=4,
        allow_recursive=False,
        allow_content_reads=False,
        allow_mutation=False,
        allow_symlinks=False,
        require_stable_ordering=True,
    )

    adapter_result = None
    collector_result = None
    if collection_decision.allowed and safety_decision.allowed:
        adapter_result = RealFilesystemMetadataAdapter.collect(
            RealFilesystemMetadataAdapterRequest(
                root=root,
                max_items=safety_decision.max_items,
            ),
        )
        collector_result = RealAssetMetadataCollector.collect(
            RealAssetMetadataCollectionRequest(
                decision=collection_decision,
                items=adapter_result.items,
            ),
        )

    return {
        "fixture_contract": fixture_contract_result,
        "sandbox_decision": sandbox_decision,
        "dry_run_result": dry_run_result,
        "metadata_boundary": metadata_boundary,
        "collection_decision": collection_decision,
        "safety_decision": safety_decision,
        "adapter_result": adapter_result,
        "collector_result": collector_result,
    }


def test_controlled_real_asset_metadata_smoke_flow_uses_explicit_tmp_path_fixture(
    tmp_path,
):
    fixture_root = tmp_path / "controlled-fixture"
    fixture_root.mkdir()
    fixtures = _fixture_items(fixture_root)

    fixture_contract_result = ControlledRealAssetFixtureContract.evaluate(
        fixtures=fixtures,
        max_items=4,
    )
    result = _run_metadata_flow_after_fixture_contract(
        fixture_contract_result=fixture_contract_result,
        root=fixture_root,
    )

    assert result["fixture_contract"].allowed is True
    assert result["fixture_contract"].fixture_count == 3
    assert result["sandbox_decision"].allowed is True
    assert result["dry_run_result"].allowed is True
    assert result["metadata_boundary"].allowed is True
    assert result["collection_decision"].allowed is True
    assert result["safety_decision"].allowed is True
    assert result["adapter_result"].allowed is True
    assert result["collector_result"].allowed is True
    assert result["collector_result"].item_count == 3

    relative_paths = {
        item.relative_path for item in result["collector_result"].items
    }
    suffixes = {item.suffix for item in result["collector_result"].items}

    assert relative_paths == {
        "product-spec.pdf",
        "product-photo-1.jpg",
        "product-photo-2.png",
    }
    assert suffixes == {".pdf", ".jpg", ".png"}
    assert all(item.error is None for item in result["collector_result"].items)
    assert all(
        isinstance(item, RealAssetMetadataDryRunItem)
        for item in result["collector_result"].items
    )
    assert not hasattr(result["collector_result"], "evidence")
    assert not hasattr(result["collector_result"], "knowledge")
    assert not hasattr(result["collector_result"], "prompt")


def test_current_pr016_contract_blocks_filesystem_metadata_flag(tmp_path):
    fixture_root = tmp_path / "controlled-fixture"
    fixture_root.mkdir()
    fixtures = _fixture_items(fixture_root)
    fixture_contract_result = ControlledRealAssetFixtureContract.evaluate(
        fixtures=fixtures,
        max_items=4,
    )

    result = _run_metadata_flow_after_fixture_contract(
        fixture_contract_result=fixture_contract_result,
        root=fixture_root,
        collection_allow_filesystem_metadata=True,
    )

    assert result["fixture_contract"].allowed is True
    assert result["collection_decision"].allowed is False
    assert (
        result["collection_decision"].reason
        == "Filesystem metadata collection is not approved in PR-016H."
    )
    assert result["adapter_result"] is None
    assert result["collector_result"] is None


def test_fixture_contract_rejects_pdf_text_extraction_before_metadata_flow(
    tmp_path,
):
    fixture_root = tmp_path / "controlled-fixture"
    fixture_root.mkdir()
    spec, _photo_jpg, _photo_png = _write_placeholder_files(fixture_root)
    fixture = _fixture_item(
        fixture_id="fixture-product-spec",
        fixture_path=str(spec),
        fixture_type="product_spec_pdf",
        allowed_for_pdf_text_extraction=True,
    )

    fixture_contract_result = ControlledRealAssetFixtureContract.evaluate(
        fixtures=(fixture,),
        max_items=4,
    )
    result = _run_metadata_flow_after_fixture_contract(
        fixture_contract_result=fixture_contract_result,
        root=fixture_root,
    )

    assert fixture_contract_result.allowed is False
    assert (
        fixture_contract_result.reason
        == "pdf text extraction is not allowed by this contract"
    )
    assert result["sandbox_decision"] is None
    assert result["adapter_result"] is None
    assert result["collector_result"] is None


def test_fixture_contract_rejects_evidence_before_metadata_flow(tmp_path):
    fixture_root = tmp_path / "controlled-fixture"
    fixture_root.mkdir()
    spec, _photo_jpg, _photo_png = _write_placeholder_files(fixture_root)
    fixture = _fixture_item(
        fixture_id="fixture-product-spec",
        fixture_path=str(spec),
        fixture_type="product_spec_pdf",
        allowed_for_evidence=True,
    )

    fixture_contract_result = ControlledRealAssetFixtureContract.evaluate(
        fixtures=(fixture,),
        max_items=4,
    )
    result = _run_metadata_flow_after_fixture_contract(
        fixture_contract_result=fixture_contract_result,
        root=fixture_root,
    )

    assert fixture_contract_result.allowed is False
    assert (
        fixture_contract_result.reason
        == "evidence creation is not allowed by this contract"
    )
    assert result["sandbox_decision"] is None
    assert result["adapter_result"] is None
    assert result["collector_result"] is None


def test_controlled_real_asset_metadata_smoke_flow_does_not_include_nested_files(
    tmp_path,
):
    fixture_root = tmp_path / "controlled-fixture"
    fixture_root.mkdir()
    fixtures = _fixture_items(fixture_root)
    nested = fixture_root / "nested"
    nested.mkdir()
    nested_file = nested / "inside.pdf"
    nested_file.write_bytes(b"nested synthetic placeholder")

    fixture_contract_result = ControlledRealAssetFixtureContract.evaluate(
        fixtures=fixtures,
        max_items=4,
    )
    result = _run_metadata_flow_after_fixture_contract(
        fixture_contract_result=fixture_contract_result,
        root=fixture_root,
    )

    relative_paths = {
        item.relative_path for item in result["collector_result"].items
    }
    collected_paths = {item.path for item in result["collector_result"].items}

    assert result["collector_result"].allowed is True
    assert result["collector_result"].item_count == 4
    assert "nested" in relative_paths
    assert str(nested) in collected_paths
    assert str(nested_file) not in collected_paths
    assert "inside.pdf" not in relative_paths


def test_collected_items_expose_no_content_derived_fields(tmp_path):
    fixture_root = tmp_path / "controlled-fixture"
    fixture_root.mkdir()
    fixtures = _fixture_items(fixture_root)
    fixture_contract_result = ControlledRealAssetFixtureContract.evaluate(
        fixtures=fixtures,
        max_items=4,
    )

    result = _run_metadata_flow_after_fixture_contract(
        fixture_contract_result=fixture_contract_result,
        root=fixture_root,
    )
    forbidden_fields = {
        "asset_type",
        "detected_asset_type",
        "mime_type",
        "content_type",
        "text",
        "caption",
        "description",
        "evidence",
        "knowledge",
        "prompt",
    }
    item_fields = {field.name for field in fields(RealAssetMetadataDryRunItem)}

    assert result["collector_result"].allowed is True
    assert not item_fields.intersection(forbidden_fields)


def test_smoke_flow_test_file_uses_no_batch_scanner_or_type_detector() -> None:
    source = inspect.getsource(sys.modules[__name__])
    type_detector_name = (
        "Creative" + "Asset" + "Type" + "Detector"
    )
    batch_scanner_name = (
        "Creative" + "Asset" + "Batch" + "Scanner"
    )

    assert type_detector_name not in source
    assert batch_scanner_name not in source
