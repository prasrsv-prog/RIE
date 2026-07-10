from dataclasses import fields

import rie.ingestion.real_asset_metadata_collector as collector_module
import rie.ingestion.real_filesystem_metadata_adapter as adapter_module
from rie.ingestion.real_asset_dry_run_contract import RealAssetDryRunContract
from rie.ingestion.real_asset_metadata_collection_contract import (
    RealAssetMetadataCollectionContract,
)
from rie.ingestion.real_asset_metadata_collector import (
    RealAssetMetadataCollectionRequest,
)
from rie.ingestion.real_asset_metadata_collector import (
    RealAssetMetadataCollector,
)
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunBoundary,
)
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunItem,
)
from rie.ingestion.real_asset_sandbox_policy import RealAssetSandboxPolicy
from rie.ingestion.real_filesystem_metadata_adapter import (
    RealFilesystemMetadataAdapter,
)
from rie.ingestion.real_filesystem_metadata_adapter import (
    RealFilesystemMetadataAdapterRequest,
)
from rie.ingestion.real_filesystem_metadata_adapter_safety_contract import (
    RealFilesystemMetadataAdapterSafetyContract,
)


def _run_controlled_flow(
    root,
    *,
    collection_overrides=None,
    safety_overrides=None,
):
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

    collection_values = {
        "allow_filesystem_metadata": False,
        "allow_recursive_collection": False,
        "allow_content_reads": False,
        "allow_mutation": False,
    }
    if collection_overrides:
        collection_values.update(collection_overrides)

    collection_decision = RealAssetMetadataCollectionContract.evaluate(
        boundary_result=metadata_boundary,
        **collection_values,
    )

    safety_values = {
        "max_items": 100,
        "allow_recursive": False,
        "allow_content_reads": False,
        "allow_mutation": False,
        "allow_symlinks": False,
        "require_stable_ordering": True,
    }
    if safety_overrides:
        safety_values.update(safety_overrides)

    safety_decision = RealFilesystemMetadataAdapterSafetyContract.evaluate(
        **safety_values,
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
        "sandbox_decision": sandbox_decision,
        "dry_run_result": dry_run_result,
        "metadata_boundary": metadata_boundary,
        "collection_decision": collection_decision,
        "safety_decision": safety_decision,
        "adapter_result": adapter_result,
        "collector_result": collector_result,
    }


def _item_by_relative_path(items, relative_path):
    return next(item for item in items if item.relative_path == relative_path)


def test_controlled_smoke_flow_collects_only_immediate_tmp_path_metadata_items(
    tmp_path,
):
    photo = tmp_path / "photo.png"
    photo.write_bytes(b"synthetic image bytes")
    spec = tmp_path / "spec.pdf"
    spec.write_bytes(b"synthetic pdf bytes")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "inside.txt").write_text("nested synthetic", encoding="utf-8")

    result = _run_controlled_flow(tmp_path)

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
    assert relative_paths == {"photo.png", "spec.pdf", "nested"}
    assert _item_by_relative_path(
        result["collector_result"].items,
        "photo.png",
    ).suffix == ".png"
    assert _item_by_relative_path(
        result["collector_result"].items,
        "spec.pdf",
    ).suffix == ".pdf"
    assert _item_by_relative_path(
        result["collector_result"].items,
        "nested",
    ).is_file is False
    assert all(
        isinstance(item, RealAssetMetadataDryRunItem)
        for item in result["collector_result"].items
    )


def test_controlled_smoke_flow_does_not_recurse_into_nested_directory(
    tmp_path,
):
    nested = tmp_path / "nested"
    nested.mkdir()
    nested_file = nested / "inside.txt"
    nested_file.write_text("nested synthetic", encoding="utf-8")

    result = _run_controlled_flow(tmp_path)

    returned_paths = {item.path for item in result["collector_result"].items}
    assert str(nested) in returned_paths
    assert str(nested_file) not in returned_paths
    assert result["collector_result"].item_count == 1


def test_controlled_smoke_flow_blocks_before_adapter_when_safety_is_unsafe(
    monkeypatch,
    tmp_path,
):
    def fail_collect(*args, **kwargs):
        raise AssertionError("adapter should not be called")

    monkeypatch.setattr(RealFilesystemMetadataAdapter, "collect", fail_collect)

    result = _run_controlled_flow(
        tmp_path,
        safety_overrides={"allow_recursive": True},
    )

    assert result["collection_decision"].allowed is True
    assert result["safety_decision"].allowed is False
    assert result["adapter_result"] is None
    assert result["collector_result"] is None


def test_controlled_smoke_flow_blocks_before_adapter_when_collection_is_unsafe(
    monkeypatch,
    tmp_path,
):
    def fail_collect(*args, **kwargs):
        raise AssertionError("adapter should not be called")

    monkeypatch.setattr(RealFilesystemMetadataAdapter, "collect", fail_collect)

    result = _run_controlled_flow(
        tmp_path,
        collection_overrides={"allow_content_reads": True},
    )

    assert result["collection_decision"].allowed is False
    assert result["safety_decision"].allowed is True
    assert result["adapter_result"] is None
    assert result["collector_result"] is None


def test_controlled_smoke_flow_exposes_no_content_derived_fields(tmp_path):
    (tmp_path / "photo.png").write_bytes(b"synthetic")

    result = _run_controlled_flow(tmp_path)
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

    assert not item_fields.intersection(forbidden_fields)
    assert result["collector_result"].allowed is True
    assert result["collector_result"].item_count == 1


def test_controlled_smoke_flow_does_not_create_artifact_types(tmp_path):
    (tmp_path / "photo.png").write_bytes(b"synthetic")

    result = _run_controlled_flow(tmp_path)

    assert not hasattr(result["collector_result"], "evidence")
    assert not hasattr(result["collector_result"], "knowledge")
    assert not hasattr(result["collector_result"], "prompt")


def test_smoke_flow_tests_use_tmp_path_only(tmp_path):
    result = _run_controlled_flow(tmp_path)

    assert result["adapter_result"].root == str(tmp_path)
    assert result["collector_result"].allowed is True


def test_smoke_flow_modules_do_not_expose_forbidden_dependencies():
    forbidden_exports = {
        "CreativeAssetTypeDetector",
        "CreativeAssetBatchScanner",
        "extractor",
        "evidence",
        "knowledge",
        "prompt",
    }

    assert not forbidden_exports.intersection(adapter_module.__dict__)
    assert not forbidden_exports.intersection(collector_module.__dict__)
