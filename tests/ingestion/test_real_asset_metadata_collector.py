from dataclasses import fields

import rie.ingestion.real_asset_metadata_collector as collector_module
from rie.ingestion.real_asset_metadata_collection_contract import (
    RealAssetMetadataCollectionDecision,
)
from rie.ingestion.real_asset_metadata_collector import (
    RealAssetMetadataCollectionRequest,
)
from rie.ingestion.real_asset_metadata_collector import (
    RealAssetMetadataCollectionResult,
)
from rie.ingestion.real_asset_metadata_collector import (
    RealAssetMetadataCollector,
)
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunItem,
)


def _decision(**overrides) -> RealAssetMetadataCollectionDecision:
    values = {
        "allowed": True,
        "reason": (
            "Real asset metadata collection contract passed as "
            "disabled skeleton-only."
        ),
        "boundary_allowed": True,
        "boundary_reason": "Real asset metadata-only boundary passed.",
        "mode": "metadata_only",
        "allow_filesystem_metadata": False,
        "allow_recursive_collection": False,
        "allow_content_reads": False,
        "allow_mutation": False,
    }
    values.update(overrides)
    return RealAssetMetadataCollectionDecision(**values)


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


def _collect(**overrides) -> RealAssetMetadataCollectionResult:
    values = {
        "decision": _decision(),
        "items": (),
    }
    values.update(overrides)
    return RealAssetMetadataCollector.collect(
        RealAssetMetadataCollectionRequest(**values),
    )


def test_rejects_blocked_collection_decision():
    decision = _decision(
        allowed=False,
        reason="Collection contract blocked.",
    )

    result = _collect(decision=decision)

    assert result.allowed is False
    assert "collection contract" in result.reason
    assert "blocked" in result.reason
    assert result.decision_allowed is False
    assert result.decision_reason == decision.reason


def test_returns_empty_items_when_decision_is_blocked():
    result = _collect(
        decision=_decision(allowed=False),
        items=(_item(),),
    )

    assert result.item_count == 0
    assert result.items == ()


def test_allows_supplied_synthetic_metadata_items_when_decision_is_allowed():
    item = _item()

    result = _collect(items=(item,))

    assert result.allowed is True
    assert "supplied metadata items only" in result.reason
    assert result.items == (item,)


def test_preserves_supplied_items_exactly():
    items = (
        _item(path="synthetic/assets/spec.pdf", relative_path="spec.pdf"),
        _item(path="synthetic/assets/photo.jpg", relative_path="photo.jpg"),
    )

    result = _collect(items=items)

    assert result.items is items


def test_preserves_item_count_from_supplied_items():
    result = _collect(
        items=(
            _item(path="synthetic/a.png", relative_path="a.png"),
            _item(path="synthetic/b.png", relative_path="b.png"),
            _item(path="synthetic/c.png", relative_path="c.png"),
        ),
    )

    assert result.item_count == 3


def test_preserves_decision_allowed_and_reason():
    decision = _decision(
        allowed=True,
        reason="Synthetic collection contract passed.",
    )

    result = _collect(decision=decision)

    assert result.decision_allowed == decision.allowed
    assert result.decision_reason == decision.reason


def test_accepts_empty_supplied_items_when_decision_is_allowed():
    result = _collect(items=())

    assert result.allowed is True
    assert result.item_count == 0
    assert result.items == ()


def test_exposes_no_filesystem_execution_or_content_derived_fields():
    forbidden_fields = {
        "root",
        "folder",
        "filesystem_path",
        "recursive",
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

    request_fields = {
        field.name for field in fields(RealAssetMetadataCollectionRequest)
    }
    result_fields = {
        field.name for field in fields(RealAssetMetadataCollectionResult)
    }

    assert not request_fields.intersection(forbidden_fields)
    assert not result_fields.intersection(forbidden_fields)


def test_module_does_not_expose_path_based_behavior():
    assert "Path" not in collector_module.__dict__
    assert "pathlib" not in collector_module.__dict__
    assert "os" not in collector_module.__dict__


def test_collector_has_no_forbidden_dependency_exports():
    forbidden_exports = {
        "CreativeAssetTypeDetector",
        "CreativeAssetBatchScanner",
        "extractor",
        "evidence",
        "knowledge",
        "prompt",
    }

    assert not forbidden_exports.intersection(collector_module.__dict__)
