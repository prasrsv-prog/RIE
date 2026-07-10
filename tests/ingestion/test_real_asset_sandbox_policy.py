from pathlib import Path

from rie.ingestion.real_asset_sandbox_policy import RealAssetSandboxPolicy


def _evaluate(**overrides):
    values = {
        "root": Path("synthetic/real-asset-sandbox"),
        "recursive": False,
        "read_only": True,
        "allow_real_asset_reads": False,
        "allow_mutation": False,
    }
    values.update(overrides)
    return RealAssetSandboxPolicy.evaluate(**values)


def test_rejects_missing_root():
    decision = _evaluate(root=None)

    assert decision.allowed is False
    assert "root" in decision.reason
    assert "required" in decision.reason


def test_rejects_non_read_only_mode():
    decision = _evaluate(read_only=False)

    assert decision.allowed is False
    assert "read-only" in decision.reason


def test_rejects_mutation():
    decision = _evaluate(allow_mutation=True)

    assert decision.allowed is False
    assert "mutation" in decision.reason
    assert "forbidden" in decision.reason


def test_rejects_real_asset_reads():
    decision = _evaluate(allow_real_asset_reads=True)

    assert decision.allowed is False
    assert "Real asset reads" in decision.reason
    assert "PR-016B" in decision.reason


def test_rejects_recursive_mode():
    decision = _evaluate(recursive=True)

    assert decision.allowed is False
    assert "Recursive" in decision.reason
    assert "PR-016B" in decision.reason


def test_allows_explicit_safe_non_recursive_read_only_sandbox_config():
    decision = _evaluate()

    assert decision.allowed is True
    assert "passed" in decision.reason


def test_decision_preserves_all_input_values():
    root = Path("synthetic/custom-sandbox")

    decision = _evaluate(
        root=root,
        recursive=True,
        read_only=False,
        allow_real_asset_reads=True,
        allow_mutation=True,
    )

    assert decision.root == root
    assert decision.recursive is True
    assert decision.read_only is False
    assert decision.allow_real_asset_reads is True
    assert decision.allow_mutation is True
