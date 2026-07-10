from dataclasses import fields

import pytest

import rie.ingestion.real_filesystem_metadata_adapter as adapter_module
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunItem,
)
from rie.ingestion.real_filesystem_metadata_adapter import (
    RealFilesystemMetadataAdapter,
)
from rie.ingestion.real_filesystem_metadata_adapter import (
    RealFilesystemMetadataAdapterRequest,
)
from rie.ingestion.real_filesystem_metadata_adapter import (
    RealFilesystemMetadataAdapterResult,
)


def _collect(root, max_items=100) -> RealFilesystemMetadataAdapterResult:
    return RealFilesystemMetadataAdapter.collect(
        RealFilesystemMetadataAdapterRequest(
            root=root,
            max_items=max_items,
        ),
    )


def test_rejects_non_positive_max_items(tmp_path):
    result = _collect(tmp_path, max_items=0)

    assert result.allowed is False
    assert result.item_count == 0
    assert result.items == ()
    assert "max_items" in result.reason
    assert "required" in result.reason


def test_rejects_missing_explicit_root(tmp_path):
    root = tmp_path / "missing"

    result = _collect(root)

    assert result.allowed is False
    assert result.item_count == 0
    assert result.items == ()
    assert "root does not exist" in result.reason


def test_rejects_root_that_is_a_file(tmp_path):
    root = tmp_path / "root.txt"
    root.write_text("synthetic", encoding="utf-8")

    result = _collect(root)

    assert result.allowed is False
    assert result.item_count == 0
    assert result.items == ()
    assert "root must be a directory" in result.reason


def test_collects_metadata_for_immediate_child_file_in_tmp_path(tmp_path):
    child = tmp_path / "photo.png"
    child.write_bytes(b"synthetic-content")

    result = _collect(tmp_path)

    assert result.allowed is True
    assert result.item_count == 1
    assert result.items[0] == RealAssetMetadataDryRunItem(
        path=str(child),
        relative_path="photo.png",
        exists=True,
        is_file=True,
        size=child.stat().st_size,
        suffix=".png",
        error=None,
    )


def test_collects_metadata_for_immediate_child_directory_in_tmp_path(tmp_path):
    child = tmp_path / "nested"
    child.mkdir()

    result = _collect(tmp_path)

    assert result.allowed is True
    assert result.item_count == 1
    assert result.items[0].path == str(child)
    assert result.items[0].relative_path == "nested"
    assert result.items[0].exists is True
    assert result.items[0].is_file is False
    assert result.items[0].size == 0
    assert result.items[0].suffix == ""
    assert result.items[0].error is None


def test_does_not_recurse_into_nested_directories(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    nested_file = nested / "inside.txt"
    nested_file.write_text("synthetic", encoding="utf-8")

    result = _collect(tmp_path)

    returned_paths = {item.path for item in result.items}
    assert str(nested) in returned_paths
    assert str(nested_file) not in returned_paths
    assert result.item_count == 1


def test_applies_max_items_limit(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "c.txt").write_text("c", encoding="utf-8")

    result = _collect(tmp_path, max_items=2)

    assert result.allowed is True
    assert result.item_count == 2
    assert len(result.items) == 2


def test_returns_real_asset_metadata_dry_run_item_values(tmp_path):
    (tmp_path / "photo.png").write_bytes(b"synthetic")

    result = _collect(tmp_path)

    assert isinstance(result.items[0], RealAssetMetadataDryRunItem)


def test_preserves_suffix_and_relative_path(tmp_path):
    (tmp_path / "manual.pdf").write_bytes(b"synthetic")

    result = _collect(tmp_path)

    assert result.items[0].relative_path == "manual.pdf"
    assert result.items[0].suffix == ".pdf"


def test_does_not_read_file_contents(monkeypatch, tmp_path):
    child = tmp_path / "manual.pdf"
    child.write_bytes(b"%PDF-synthetic")

    def fail_content_read(*args, **kwargs):
        raise AssertionError("content read should not be called")

    monkeypatch.setattr(type(child), "read_bytes", fail_content_read)
    monkeypatch.setattr(type(child), "read_text", fail_content_read)

    result = _collect(tmp_path)

    assert result.allowed is True
    assert result.item_count == 1


def test_exposes_no_content_derived_fields():
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

    result_fields = {
        field.name for field in fields(RealFilesystemMetadataAdapterResult)
    }

    assert not result_fields.intersection(forbidden_fields)


def test_module_does_not_expose_scanner_detector_or_artifact_dependencies():
    forbidden_exports = {
        "CreativeAssetTypeDetector",
        "CreativeAssetBatchScanner",
        "extractor",
        "evidence",
        "knowledge",
        "prompt",
    }

    assert not forbidden_exports.intersection(adapter_module.__dict__)


def test_collects_child_metadata_error_without_raising(monkeypatch, tmp_path):
    child = tmp_path / "broken.txt"
    child.write_text("synthetic", encoding="utf-8")
    original_stat = type(child).stat

    def fail_child_stat(self, *args, **kwargs):
        if self == child:
            raise OSError("synthetic stat failure")
        return original_stat(self, *args, **kwargs)

    monkeypatch.setattr(type(child), "stat", fail_child_stat)

    result = _collect(tmp_path)

    assert result.allowed is True
    assert result.item_count == 1
    assert result.items[0].path == str(child)
    assert result.items[0].size == 0
    assert result.items[0].is_file is False
    assert "synthetic stat failure" in result.items[0].error


def test_tests_use_tmp_path_only_for_adapter_roots(tmp_path):
    result = _collect(tmp_path)

    assert result.root == str(tmp_path)
