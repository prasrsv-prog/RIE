from dataclasses import fields

import rie.ingestion.real_filesystem_metadata_adapter_safety_contract as contract_module
from rie.ingestion.real_filesystem_metadata_adapter_safety_contract import (
    RealFilesystemMetadataAdapterSafetyContract,
)
from rie.ingestion.real_filesystem_metadata_adapter_safety_contract import (
    RealFilesystemMetadataAdapterSafetyDecision,
)


def _evaluate(**overrides) -> RealFilesystemMetadataAdapterSafetyDecision:
    values = {
        "max_items": 100,
        "allow_recursive": False,
        "allow_content_reads": False,
        "allow_mutation": False,
        "allow_symlinks": False,
        "require_stable_ordering": True,
    }
    values.update(overrides)
    return RealFilesystemMetadataAdapterSafetyContract.evaluate(**values)


def test_rejects_non_positive_max_items():
    decision = _evaluate(max_items=0)

    assert decision.allowed is False
    assert "max_items" in decision.reason
    assert "required" in decision.reason


def test_rejects_max_items_greater_than_100():
    decision = _evaluate(max_items=101)

    assert decision.allowed is False
    assert "max_items limit" in decision.reason
    assert "exceeded" in decision.reason


def test_rejects_recursive_flag():
    decision = _evaluate(allow_recursive=True)

    assert decision.allowed is False
    assert "Recursive metadata collection" in decision.reason
    assert "forbidden" in decision.reason


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


def test_rejects_symlink_flag():
    decision = _evaluate(allow_symlinks=True)

    assert decision.allowed is False
    assert "Symlink traversal" in decision.reason
    assert "not approved" in decision.reason


def test_rejects_missing_stable_ordering_requirement():
    decision = _evaluate(require_stable_ordering=False)

    assert decision.allowed is False
    assert "Stable ordering" in decision.reason
    assert "required" in decision.reason


def test_allows_safe_defaults():
    decision = _evaluate()

    assert decision.allowed is True
    assert "passed" in decision.reason


def test_preserves_all_input_values_in_decision():
    decision = _evaluate(
        max_items=101,
        allow_recursive=True,
        allow_content_reads=True,
        allow_mutation=True,
        allow_symlinks=True,
        require_stable_ordering=False,
    )

    assert decision.max_items == 101
    assert decision.allow_recursive is True
    assert decision.allow_content_reads is True
    assert decision.allow_mutation is True
    assert decision.allow_symlinks is True
    assert decision.require_stable_ordering is False


def test_exposes_no_filesystem_execution_or_content_derived_fields():
    forbidden_fields = {
        "root",
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
    }

    decision_fields = {
        field.name for field in fields(RealFilesystemMetadataAdapterSafetyDecision)
    }

    assert not decision_fields.intersection(forbidden_fields)


def test_module_does_not_expose_forbidden_dependencies():
    forbidden_exports = {
        "Path",
        "pathlib",
        "os",
        "RealFilesystemMetadataAdapter",
        "CreativeAssetTypeDetector",
        "CreativeAssetBatchScanner",
        "extractor",
        "evidence",
        "knowledge",
        "prompt",
    }

    assert not forbidden_exports.intersection(contract_module.__dict__)
