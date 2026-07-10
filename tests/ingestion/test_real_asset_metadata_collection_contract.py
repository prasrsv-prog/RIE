from dataclasses import fields

from rie.ingestion.real_asset_metadata_collection_contract import (
    RealAssetMetadataCollectionContract,
)
from rie.ingestion.real_asset_metadata_collection_contract import (
    RealAssetMetadataCollectionDecision,
)
from rie.ingestion.real_asset_metadata_dry_run_boundary import (
    RealAssetMetadataDryRunBoundaryResult,
)


def _boundary_result(**overrides) -> RealAssetMetadataDryRunBoundaryResult:
    values = {
        "allowed": True,
        "reason": "Real asset metadata-only boundary passed.",
        "dry_run_allowed": True,
        "dry_run_reason": "Real asset dry-run contract passed.",
        "mode": "metadata_only",
        "item_count": 0,
        "items": (),
    }
    values.update(overrides)
    return RealAssetMetadataDryRunBoundaryResult(**values)


def _evaluate(**overrides) -> RealAssetMetadataCollectionDecision:
    values = {
        "boundary_result": _boundary_result(),
        "allow_filesystem_metadata": False,
        "allow_recursive_collection": False,
        "allow_content_reads": False,
        "allow_mutation": False,
    }
    values.update(overrides)
    return RealAssetMetadataCollectionContract.evaluate(**values)


def test_rejects_blocked_boundary_result():
    boundary_result = _boundary_result(
        allowed=False,
        reason="Metadata boundary blocked.",
    )

    decision = _evaluate(boundary_result=boundary_result)

    assert decision.allowed is False
    assert "Metadata dry-run boundary" in decision.reason
    assert "blocked" in decision.reason
    assert decision.boundary_allowed is False
    assert decision.boundary_reason == boundary_result.reason


def test_rejects_non_metadata_only_mode():
    decision = _evaluate(
        boundary_result=_boundary_result(mode="header_only"),
    )

    assert decision.allowed is False
    assert "metadata_only" in decision.reason
    assert "approved" in decision.reason


def test_rejects_filesystem_metadata_flag():
    decision = _evaluate(allow_filesystem_metadata=True)

    assert decision.allowed is False
    assert "Filesystem metadata collection" in decision.reason
    assert "PR-016H" in decision.reason


def test_rejects_recursive_collection_flag():
    decision = _evaluate(allow_recursive_collection=True)

    assert decision.allowed is False
    assert "Recursive collection" in decision.reason
    assert "PR-016H" in decision.reason


def test_rejects_content_reads_flag():
    decision = _evaluate(allow_content_reads=True)

    assert decision.allowed is False
    assert "Content reads" in decision.reason
    assert "forbidden" in decision.reason


def test_rejects_mutation_flag():
    decision = _evaluate(allow_mutation=True)

    assert decision.allowed is False
    assert "mutation" in decision.reason
    assert "forbidden" in decision.reason


def test_allows_safe_disabled_skeleton_config():
    decision = _evaluate()

    assert decision.allowed is True
    assert "passed" in decision.reason
    assert "disabled skeleton-only" in decision.reason


def test_preserves_boundary_result_values():
    boundary_result = _boundary_result(
        allowed=True,
        reason="Synthetic metadata boundary passed.",
        mode="metadata_only",
    )

    decision = _evaluate(boundary_result=boundary_result)

    assert decision.boundary_allowed == boundary_result.allowed
    assert decision.boundary_reason == boundary_result.reason
    assert decision.mode == boundary_result.mode


def test_preserves_contract_input_flags():
    decision = _evaluate(
        allow_filesystem_metadata=True,
        allow_recursive_collection=True,
        allow_content_reads=True,
        allow_mutation=True,
    )

    assert decision.allow_filesystem_metadata is True
    assert decision.allow_recursive_collection is True
    assert decision.allow_content_reads is True
    assert decision.allow_mutation is True


def test_exposes_no_filesystem_execution_or_content_derived_fields():
    forbidden_fields = {
        "path",
        "relative_path",
        "items",
        "item_count",
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
        "scan_result",
        "collector",
    }

    decision_fields = {
        field.name for field in fields(RealAssetMetadataCollectionDecision)
    }

    assert not decision_fields.intersection(forbidden_fields)
