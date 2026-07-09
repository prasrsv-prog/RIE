from dataclasses import fields

import pytest

from official_source.official_source import AuthorityStatus
from official_source.official_source import DocumentClassification
from official_source.official_source import EvidenceEligibility
from official_source.official_source import LifecycleStatus
from official_source.official_source import OfficialSource
from official_source.official_source import SourceType
from official_source.official_source_evidence_eligibility_gate import (
    EvidenceEligibilityGateResult,
)
from official_source.official_source_evidence_workflow_gate import (
    EvidenceWorkflowGate,
)


def _gate_result(**overrides) -> EvidenceEligibilityGateResult:
    values = {
        "source_id": "SRC-SYN-WORKFLOW-001",
        "allowed": True,
        "requires_review": False,
        "reason": "Synthetic workflow gate input.",
    }
    values.update(overrides)
    return EvidenceEligibilityGateResult(**values)


def _official_source() -> OfficialSource:
    return OfficialSource(
        source_id="SRC-SYN-WORKFLOW-001",
        source_path="docs/synthetic-workflow-source.pdf",
        source_type=SourceType.PDF,
        document_classification=DocumentClassification.PROJECT_RULEBOOK,
        authority_status=AuthorityStatus.SOURCE_OF_TRUTH_CANDIDATE,
        lifecycle_status=LifecycleStatus.LOCKED,
        evidence_eligibility=EvidenceEligibility.ELIGIBLE,
        version="v1.0",
        review_notes="Synthetic workflow gate test data only.",
    )


def test_allowed_gate_result_allows_workflow():
    result = EvidenceWorkflowGate.check(
        _gate_result(allowed=True, requires_review=False),
    )

    assert result.workflow_allowed is True


def test_requires_review_gate_result_blocks_workflow():
    result = EvidenceWorkflowGate.check(
        _gate_result(allowed=False, requires_review=True),
    )

    assert result.workflow_allowed is False
    assert result.requires_review is True


def test_blocked_gate_result_blocks_workflow():
    result = EvidenceWorkflowGate.check(
        _gate_result(allowed=False, requires_review=False),
    )

    assert result.workflow_allowed is False


def test_preserves_source_id():
    result = EvidenceWorkflowGate.check(
        _gate_result(source_id="SRC-SYN-WORKFLOW-999"),
    )

    assert result.source_id == "SRC-SYN-WORKFLOW-999"


def test_preserves_requires_review():
    result = EvidenceWorkflowGate.check(
        _gate_result(allowed=False, requires_review=True),
    )

    assert result.requires_review is True


def test_preserves_reason():
    result = EvidenceWorkflowGate.check(
        _gate_result(reason="Synthetic workflow gate reason."),
    )

    assert result.reason == "Synthetic workflow gate reason."


def test_rejects_official_source_input():
    with pytest.raises(TypeError, match="EvidenceEligibilityGateResult"):
        EvidenceWorkflowGate.check(_official_source())


def test_rejects_raw_source_path_string_input():
    with pytest.raises(TypeError, match="EvidenceEligibilityGateResult"):
        EvidenceWorkflowGate.check("docs/synthetic-workflow-source.pdf")


def test_result_exposes_no_downstream_or_asset_fields():
    result = EvidenceWorkflowGate.check(_gate_result())
    result_field_names = [field.name for field in fields(result)]

    forbidden_fields = [
        "source_path",
        "content",
        "evidence",
        "evidence_id",
        "knowledge",
        "knowledge_id",
        "product",
        "product_type",
        "prompt",
        "final_prompt",
        "asset_path",
        "artifact",
        "pdf",
        "image",
    ]

    for field_name in forbidden_fields:
        assert field_name not in result_field_names


def test_tests_use_synthetic_data_only():
    gate_result = _gate_result()
    source = _official_source()

    assert gate_result.source_id.startswith("SRC-SYN-WORKFLOW-")
    assert "Synthetic" in gate_result.reason
    assert source.source_path.startswith("docs/synthetic")
    assert "Synthetic" in source.review_notes


def test_no_filesystem_reads_are_required(monkeypatch):
    def fail_open(*args, **kwargs):
        raise AssertionError("Workflow gate must not read files.")

    monkeypatch.setattr("builtins.open", fail_open)

    result = EvidenceWorkflowGate.check(_gate_result())

    assert result.workflow_allowed is True
