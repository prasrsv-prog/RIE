from dataclasses import fields

import pytest

from official_source.official_source import AuthorityStatus
from official_source.official_source import DocumentClassification
from official_source.official_source import EvidenceEligibility
from official_source.official_source import LifecycleStatus
from official_source.official_source import OfficialSource
from official_source.official_source import SourceType
from official_source.official_source_evidence_eligibility_gate import (
    EvidenceEligibilityGate,
)
from official_source.official_source_evidence_eligibility_policy import (
    EvidenceEligibilityDecision,
)


def _decision(**overrides) -> EvidenceEligibilityDecision:
    values = {
        "source_id": "SRC-SYN-GATE-001",
        "evidence_eligibility": EvidenceEligibility.ELIGIBLE,
        "allowed": True,
        "requires_review": False,
        "reason": "Synthetic gate decision.",
    }
    values.update(overrides)
    return EvidenceEligibilityDecision(**values)


def _official_source() -> OfficialSource:
    return OfficialSource(
        source_id="SRC-SYN-GATE-001",
        source_path="docs/synthetic-gate-source.pdf",
        source_type=SourceType.PDF,
        document_classification=DocumentClassification.PROJECT_RULEBOOK,
        authority_status=AuthorityStatus.SOURCE_OF_TRUTH_CANDIDATE,
        lifecycle_status=LifecycleStatus.LOCKED,
        evidence_eligibility=EvidenceEligibility.ELIGIBLE,
        version="v1.0",
        review_notes="Synthetic gate test data only.",
    )


def test_allowed_decision_passes():
    result = EvidenceEligibilityGate.check(
        _decision(allowed=True, requires_review=False),
    )

    assert result.allowed is True


def test_requires_review_decision_blocks():
    result = EvidenceEligibilityGate.check(
        _decision(allowed=False, requires_review=True),
    )

    assert result.allowed is False
    assert result.requires_review is True


def test_not_allowed_decision_blocks():
    result = EvidenceEligibilityGate.check(
        _decision(allowed=False, requires_review=False),
    )

    assert result.allowed is False


def test_blocked_non_review_decision_preserves_non_review_blocked_shape():
    result = EvidenceEligibilityGate.check(
        _decision(allowed=False, requires_review=False),
    )

    assert result.allowed is False
    assert result.requires_review is False


def test_gate_result_preserves_source_id():
    result = EvidenceEligibilityGate.check(
        _decision(source_id="SRC-SYN-GATE-999"),
    )

    assert result.source_id == "SRC-SYN-GATE-999"


def test_gate_result_preserves_requires_review():
    result = EvidenceEligibilityGate.check(
        _decision(allowed=False, requires_review=True),
    )

    assert result.requires_review is True


def test_gate_result_has_non_empty_reason():
    result = EvidenceEligibilityGate.check(
        _decision(reason="Synthetic gate reason."),
    )

    assert result.reason == "Synthetic gate reason."


def test_gate_accepts_decision_not_official_source():
    with pytest.raises(TypeError, match="EvidenceEligibilityDecision"):
        EvidenceEligibilityGate.check(_official_source())


def test_gate_result_exposes_no_source_path_field():
    result = EvidenceEligibilityGate.check(_decision())

    assert "source_path" not in [field.name for field in fields(result)]


def test_gate_result_exposes_no_downstream_workflow_fields():
    result = EvidenceEligibilityGate.check(_decision())
    result_field_names = [field.name for field in fields(result)]

    forbidden_fields = [
        "content",
        "evidence",
        "evidence_index",
        "knowledge",
        "knowledge_id",
        "official_knowledge",
        "official_knowledge_index",
        "prompt",
        "final_prompt",
        "product",
        "product_type",
    ]

    for field_name in forbidden_fields:
        assert field_name not in result_field_names


def test_tests_use_synthetic_data_only():
    decision = _decision()
    source = _official_source()

    assert decision.source_id.startswith("SRC-SYN-GATE-")
    assert "Synthetic" in decision.reason
    assert source.source_path.startswith("docs/synthetic")
    assert "Synthetic" in source.review_notes
