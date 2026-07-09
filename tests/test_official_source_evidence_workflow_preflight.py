import pytest

from official_source.official_source import (
    AuthorityStatus,
    DocumentClassification,
    EvidenceEligibility,
    LifecycleStatus,
    OfficialSource,
    SourceType,
)
from official_source.official_source_evidence_workflow_gate import (
    EvidenceWorkflowGateResult,
)
from official_source.official_source_evidence_workflow_preflight import (
    EvidenceWorkflowPreflight,
    EvidenceWorkflowPreflightResult,
)


def test_allowed_workflow_gate_result_allows_preflight() -> None:
    gate_result = EvidenceWorkflowGateResult(
        source_id="source-001",
        workflow_allowed=True,
        requires_review=False,
        reason="Evidence workflow is allowed.",
    )

    result = EvidenceWorkflowPreflight.check(gate_result)

    assert result == EvidenceWorkflowPreflightResult(
        source_id="source-001",
        evidence_collection_allowed=True,
        requires_review=False,
        reason="Evidence workflow is allowed.",
    )


def test_requires_review_blocks_preflight() -> None:
    gate_result = EvidenceWorkflowGateResult(
        source_id="source-001",
        workflow_allowed=False,
        requires_review=True,
        reason="Evidence workflow requires review.",
    )

    result = EvidenceWorkflowPreflight.check(gate_result)

    assert result.evidence_collection_allowed is False
    assert result.requires_review is True
    assert result.reason == "Evidence workflow requires review."


def test_blocked_workflow_gate_result_blocks_preflight() -> None:
    gate_result = EvidenceWorkflowGateResult(
        source_id="source-001",
        workflow_allowed=False,
        requires_review=False,
        reason="Evidence workflow is blocked.",
    )

    result = EvidenceWorkflowPreflight.check(gate_result)

    assert result.evidence_collection_allowed is False
    assert result.requires_review is False
    assert result.reason == "Evidence workflow is blocked."


def test_preserves_source_id() -> None:
    gate_result = EvidenceWorkflowGateResult(
        source_id="source-xyz",
        workflow_allowed=True,
        requires_review=False,
        reason="allowed",
    )

    result = EvidenceWorkflowPreflight.check(gate_result)

    assert result.source_id == "source-xyz"


def test_preserves_requires_review() -> None:
    gate_result = EvidenceWorkflowGateResult(
        source_id="source-001",
        workflow_allowed=False,
        requires_review=True,
        reason="review required",
    )

    result = EvidenceWorkflowPreflight.check(gate_result)

    assert result.requires_review is True


def test_preserves_reason() -> None:
    gate_result = EvidenceWorkflowGateResult(
        source_id="source-001",
        workflow_allowed=False,
        requires_review=False,
        reason="custom reason",
    )

    result = EvidenceWorkflowPreflight.check(gate_result)

    assert result.reason == "custom reason"


def test_rejects_official_source_input() -> None:
    source = OfficialSource(
        source_id="source-001",
        source_path="synthetic/path.json",
        source_type=SourceType.UNKNOWN,
        document_classification=DocumentClassification.UNKNOWN,
        authority_status=AuthorityStatus.UNKNOWN,
        lifecycle_status=LifecycleStatus.UNKNOWN,
        evidence_eligibility=EvidenceEligibility.UNKNOWN,
        version=None,
        review_notes=None,
    )

    with pytest.raises(TypeError):
        EvidenceWorkflowPreflight.check(source)  # type: ignore[arg-type]


def test_rejects_raw_source_path_string_input() -> None:
    with pytest.raises(TypeError):
        EvidenceWorkflowPreflight.check("synthetic/path.json")  # type: ignore[arg-type]


def test_rejects_extraction_report_like_input() -> None:
    with pytest.raises(TypeError):
        EvidenceWorkflowPreflight.check({"extractions": []})  # type: ignore[arg-type]


def test_result_exposes_no_forbidden_fields() -> None:
    result = EvidenceWorkflowPreflightResult(
        source_id="source-001",
        evidence_collection_allowed=True,
        requires_review=False,
        reason="allowed",
    )

    exposed_fields = set(result.__dataclass_fields__)

    assert "source_path" not in exposed_fields
    assert "content" not in exposed_fields
    assert "evidence" not in exposed_fields
    assert "evidence_id" not in exposed_fields
    assert "knowledge" not in exposed_fields
    assert "knowledge_id" not in exposed_fields
    assert "product" not in exposed_fields
    assert "product_type" not in exposed_fields
    assert "prompt" not in exposed_fields
    assert "final_prompt" not in exposed_fields
    assert "asset_path" not in exposed_fields
    assert "artifact" not in exposed_fields
    assert "pdf" not in exposed_fields
    assert "image" not in exposed_fields
    assert "extraction_report" not in exposed_fields


def test_preflight_requires_no_filesystem_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("filesystem access is not allowed")

    monkeypatch.setattr("builtins.open", fail_if_called)

    gate_result = EvidenceWorkflowGateResult(
        source_id="source-001",
        workflow_allowed=True,
        requires_review=False,
        reason="allowed",
    )

    result = EvidenceWorkflowPreflight.check(gate_result)

    assert result.evidence_collection_allowed is True