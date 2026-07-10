from pathlib import Path

from rie.ingestion.real_asset_dry_run_contract import RealAssetDryRunContract
from rie.ingestion.real_asset_sandbox_policy import RealAssetSandboxPolicy


def _sandbox_decision(**overrides):
    values = {
        "root": Path("synthetic/real-asset-sandbox"),
        "recursive": False,
        "read_only": True,
        "allow_real_asset_reads": False,
        "allow_mutation": False,
    }
    values.update(overrides)
    return RealAssetSandboxPolicy.evaluate(**values)


def _evaluate(**overrides):
    values = {
        "sandbox_decision": _sandbox_decision(),
        "mode": "metadata_only",
        "planned_scan_allowed": False,
        "planned_real_asset_reads_allowed": False,
        "planned_mutation_allowed": False,
    }
    values.update(overrides)
    return RealAssetDryRunContract.evaluate(**values)


def test_rejects_blocked_sandbox_policy_decision():
    sandbox_decision = _sandbox_decision(root=None)

    decision = _evaluate(sandbox_decision=sandbox_decision)

    assert decision.allowed is False
    assert "Sandbox policy" in decision.reason
    assert "blocked" in decision.reason
    assert decision.sandbox_allowed is False
    assert decision.sandbox_reason == sandbox_decision.reason


def test_rejects_header_only_mode():
    decision = _evaluate(mode="header_only")

    assert decision.allowed is False
    assert "Header-only" in decision.reason
    assert "PR-016D" in decision.reason


def test_rejects_extraction_preview_mode():
    decision = _evaluate(mode="extraction_preview")

    assert decision.allowed is False
    assert "Extraction preview" in decision.reason
    assert "PR-016D" in decision.reason


def test_rejects_unknown_mode():
    decision = _evaluate(mode="visual_preview")

    assert decision.allowed is False
    assert "Unsupported dry-run mode" in decision.reason


def test_rejects_planned_scan():
    decision = _evaluate(planned_scan_allowed=True)

    assert decision.allowed is False
    assert "Scan execution" in decision.reason
    assert "PR-016D" in decision.reason


def test_rejects_planned_real_asset_reads():
    decision = _evaluate(planned_real_asset_reads_allowed=True)

    assert decision.allowed is False
    assert "Real asset reads" in decision.reason
    assert "PR-016D" in decision.reason


def test_rejects_planned_mutation():
    decision = _evaluate(planned_mutation_allowed=True)

    assert decision.allowed is False
    assert "mutation" in decision.reason
    assert "forbidden" in decision.reason


def test_allows_safe_metadata_only_contract_when_policy_passed():
    decision = _evaluate()

    assert decision.allowed is True
    assert "passed" in decision.reason
    assert decision.item_count == 0


def test_preserves_all_sandbox_decision_values():
    sandbox_decision = _sandbox_decision(
        root=Path("synthetic/custom-sandbox"),
        recursive=True,
        read_only=False,
        allow_real_asset_reads=True,
        allow_mutation=True,
    )

    decision = _evaluate(sandbox_decision=sandbox_decision)

    assert decision.sandbox_allowed == sandbox_decision.allowed
    assert decision.sandbox_reason == sandbox_decision.reason
    assert decision.root == sandbox_decision.root
    assert decision.recursive == sandbox_decision.recursive
    assert decision.read_only == sandbox_decision.read_only
    assert decision.allow_real_asset_reads == (
        sandbox_decision.allow_real_asset_reads
    )
    assert decision.allow_mutation == sandbox_decision.allow_mutation


def test_preserves_all_dry_run_contract_input_values():
    decision = _evaluate(
        mode="header_only",
        planned_scan_allowed=True,
        planned_real_asset_reads_allowed=True,
        planned_mutation_allowed=True,
    )

    assert decision.mode == "header_only"
    assert decision.planned_scan_allowed is True
    assert decision.planned_real_asset_reads_allowed is True
    assert decision.planned_mutation_allowed is True


def test_reports_item_count_zero():
    rejected = _evaluate(mode="header_only")
    allowed = _evaluate()

    assert rejected.item_count == 0
    assert allowed.item_count == 0
