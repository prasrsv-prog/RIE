from dataclasses import fields

from rie.ingestion.real_asset_dry_run_contract import RealAssetDryRunResult
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunBoundary,
)
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunBoundaryResult,
)
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunItem,
)


def _dry_run_result(**overrides) -> RealAssetDryRunResult:
    values = {
        "allowed": True,
        "reason": "Real asset dry-run contract passed.",
        "sandbox_allowed": True,
        "sandbox_reason": "Real asset sandbox policy passed.",
        "root": None,
        "recursive": False,
        "read_only": True,
        "allow_real_asset_reads": False,
        "allow_mutation": False,
        "mode": "metadata_only",
        "planned_scan_allowed": False,
        "planned_real_asset_reads_allowed": False,
        "planned_mutation_allowed": False,
        "item_count": 0,
    }
    values.update(overrides)
    return RealAssetDryRunResult(**values)


def _item(**overrides) -> RealAssetMetadataDryRunItem:
    values = {
        "path": "synthetic/assets/product-photo.png",
        "relative_path": "product-photo.png",
        "exists": True,
        "is_file": True,
        "size": 128,
        "suffix": ".png",
        "error": None,
    }
    values.update(overrides)
    return RealAssetMetadataDryRunItem(**values)


def _evaluate(**overrides) -> RealAssetMetadataDryRunBoundaryResult:
    values = {
        "dry_run_result": _dry_run_result(),
        "items": (),
    }
    values.update(overrides)
    return RealAssetMetadataDryRunBoundary.evaluate(**values)


def test_rejects_blocked_real_asset_dry_run_result():
    dry_run_result = _dry_run_result(
        allowed=False,
        reason="Dry-run contract blocked.",
    )

    decision = _evaluate(dry_run_result=dry_run_result)

    assert decision.allowed is False
    assert "Dry-run contract" in decision.reason
    assert "blocked" in decision.reason
    assert decision.dry_run_allowed is False
    assert decision.dry_run_reason == dry_run_result.reason


def test_rejects_non_metadata_only_mode():
    decision = _evaluate(
        dry_run_result=_dry_run_result(mode="header_only"),
    )

    assert decision.allowed is False
    assert "metadata_only" in decision.reason
    assert "approved" in decision.reason


def test_rejects_negative_size():
    decision = _evaluate(items=(_item(size=-1),))

    assert decision.allowed is False
    assert "negative size" in decision.reason
    assert "invalid" in decision.reason


def test_rejects_empty_path():
    decision = _evaluate(items=(_item(path=""),))

    assert decision.allowed is False
    assert "path" in decision.reason
    assert "required" in decision.reason


def test_rejects_empty_relative_path():
    decision = _evaluate(items=(_item(relative_path=""),))

    assert decision.allowed is False
    assert "relative_path" in decision.reason
    assert "required" in decision.reason


def test_allows_empty_supplied_item_list():
    decision = _evaluate(items=())

    assert decision.allowed is True
    assert "passed" in decision.reason
    assert decision.item_count == 0
    assert decision.items == ()


def test_allows_supplied_synthetic_metadata_items():
    item = _item()

    decision = _evaluate(items=(item,))

    assert decision.allowed is True
    assert decision.item_count == 1
    assert decision.items == (item,)


def test_preserves_dry_run_result_values():
    dry_run_result = _dry_run_result(
        allowed=True,
        reason="Synthetic dry-run contract passed.",
        mode="metadata_only",
    )

    decision = _evaluate(dry_run_result=dry_run_result)

    assert decision.dry_run_allowed == dry_run_result.allowed
    assert decision.dry_run_reason == dry_run_result.reason
    assert decision.mode == dry_run_result.mode


def test_preserves_item_values_exactly():
    item = _item(
        path="synthetic/assets/spec-sheet.pdf",
        relative_path="spec-sheet.pdf",
        exists=False,
        is_file=False,
        size=0,
        suffix=".pdf",
        error="Synthetic metadata failure.",
    )

    decision = _evaluate(items=(item,))

    assert decision.items == (item,)
    assert decision.items[0].path == "synthetic/assets/spec-sheet.pdf"
    assert decision.items[0].relative_path == "spec-sheet.pdf"
    assert decision.items[0].exists is False
    assert decision.items[0].is_file is False
    assert decision.items[0].size == 0
    assert decision.items[0].suffix == ".pdf"
    assert decision.items[0].error == "Synthetic metadata failure."


def test_derives_item_count_only_from_supplied_items():
    dry_run_result = _dry_run_result(item_count=999)
    items = (
        _item(path="synthetic/a.png", relative_path="a.png"),
        _item(path="synthetic/b.png", relative_path="b.png"),
    )

    decision = _evaluate(
        dry_run_result=dry_run_result,
        items=items,
    )

    assert decision.item_count == 2


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

    item_fields = {field.name for field in fields(RealAssetMetadataDryRunItem)}
    result_fields = {
        field.name for field in fields(RealAssetMetadataDryRunBoundaryResult)
    }

    assert not item_fields.intersection(forbidden_fields)
    assert not result_fields.intersection(forbidden_fields)
