from datetime import datetime, timezone

import pytest

from rie.application.consume_generated_candidate_asset_admission_execution_for_workflow_transition import (
    consume_generated_candidate_asset_admission_execution_for_workflow_transition,
)
from rie.domain.evaluate_governed_creative_workflow_transition import (
    TRANSITION_DISPOSITION_ACCEPTED,
    evaluate_governed_creative_workflow_transition,
)
from rie.domain.generated_candidate_asset_admission_execution import (
    ADMISSION_OUTCOME_ADMITTED,
    GeneratedCandidateAssetAdmissionExecution,
)


PROJECT = "project:001"
CAMPAIGN = (PROJECT, "campaign:001")
ADMITTED_REFERENCE = "asset:generated:001"
BOUND_ASSET = (PROJECT, CAMPAIGN[1], ADMITTED_REFERENCE)
NOW = datetime(2026, 10, 2, 6, 30, tzinfo=timezone.utc)


def _admission():
    execution_id = "a" * 64
    authorization_id = "b" * 64
    decision_id = "c" * 64
    evaluation_id = "evaluation:001"
    candidate_checksum = "d" * 64
    return GeneratedCandidateAssetAdmissionExecution(
        asset_admission_execution_id=execution_id,
        authorization_id=authorization_id,
        decision_id=decision_id,
        evaluation_id=evaluation_id,
        candidate_id="candidate:generated:001",
        candidate_checksum=candidate_checksum,
        admitted_asset_reference=ADMITTED_REFERENCE,
        execution_actor_reference="actor:admission",
        execution_timestamp=NOW,
        execution_outcome=ADMISSION_OUTCOME_ADMITTED,
        deterministic_provenance=(
            f"candidate_sha256:{candidate_checksum}",
            f"evaluation_id:{evaluation_id}",
            f"decision_id:{decision_id}",
            f"authorization_sha256:{authorization_id}",
            f"admitted_asset_reference:{ADMITTED_REFERENCE}",
            f"asset_admission_execution_sha256:{execution_id}",
        ),
    )


def _kwargs():
    return {
        "workflow_request_reference": "workflow:001",
        "idempotency_key": "idem:001",
        "project_context_reference": PROJECT,
        "campaign_context_reference": CAMPAIGN,
        "creative_brief_reference": "brief:001",
        "instruction_reference": ("instruction:001", "APPROVED_INSTRUCTION"),
        "current_workflow_state": "ASSET_ADMISSION_PENDING",
        "requested_next_workflow_state": "GOVERNED_ASSET_REFERENCE_RECORDED",
        "responsible_actor_or_service_reference": ("ACTOR", "actor:workflow"),
        "event_timestamp": NOW,
        "evidence_references": ((PROJECT, CAMPAIGN[1], "evidence:001"),),
        "reason_codes": ("ASSET_ADMISSION_EXECUTED",),
        "workflow_contract_reference": ("GATE_18_CREATIVE_WORKFLOW", "1.0"),
        "canonical_input_fingerprint": "1" * 64,
        "consumption_actor_reference": "actor:consumer",
        "consumption_timestamp": NOW,
        "creative_result_candidate_reference": (
            PROJECT,
            CAMPAIGN[1],
            "candidate:001",
        ),
        "accepted_operator_decision_reference": (
            PROJECT,
            CAMPAIGN[1],
            "operator-decision:001",
        ),
    }


def test_consumer_binds_exact_admitted_reference_and_invokes_evaluator_once():
    calls = []

    def evaluator(**kwargs):
        calls.append(dict(kwargs))
        return evaluate_governed_creative_workflow_transition(**kwargs)

    result = (
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            _admission(),
            **_kwargs(),
            workflow_transition_evaluator=evaluator,
        )
    )

    assert len(calls) == 1
    assert calls[0]["accepted_governed_asset_reference"] == BOUND_ASSET
    assert calls[0]["asset_admission_execution_requested"] is False
    assert calls[0]["approval_execution_requested"] is False
    assert calls[0]["authority_bypass_requested"] is False
    assert calls[0]["prohibited_automation_requested"] is False
    assert calls[0]["lifecycle_mutation_requested"] is False
    assert calls[0]["production_release_requested"] is False
    assert result.accepted_governed_asset_reference == BOUND_ASSET
    assert result.workflow_transition_evaluation.disposition == (
        TRANSITION_DISPOSITION_ACCEPTED
    )
    assert result.workflow_transition_evaluation.resulting_workflow_state == (
        "GOVERNED_ASSET_REFERENCE_RECORDED"
    )


def test_consumer_is_deterministic_for_identical_exact_inputs():
    first = (
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            _admission(),
            **_kwargs(),
        )
    )
    second = (
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            _admission(),
            **_kwargs(),
        )
    )

    assert first.consumption_id == second.consumption_id
    assert first.deterministic_provenance == second.deterministic_provenance
    assert first.workflow_transition_evaluation == (
        second.workflow_transition_evaluation
    )


def test_consumer_accepts_preexisting_exact_bound_asset_reference():
    result = (
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            _admission(),
            **_kwargs(),
            accepted_governed_asset_reference=BOUND_ASSET,
        )
    )

    assert result.accepted_governed_asset_reference == BOUND_ASSET


def test_consumer_rejects_mismatched_preexisting_asset_reference_before_evaluation():
    calls = []

    def evaluator(**kwargs):
        calls.append(kwargs)
        return evaluate_governed_creative_workflow_transition(**kwargs)

    with pytest.raises(ValueError, match="must match the exact admitted"):
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            _admission(),
            **_kwargs(),
            accepted_governed_asset_reference=(
                PROJECT,
                CAMPAIGN[1],
                "asset:other",
            ),
            workflow_transition_evaluator=evaluator,
        )

    assert calls == []


def test_consumer_rejects_tampered_admission_provenance_before_evaluation():
    admission = _admission()
    object.__setattr__(
        admission,
        "deterministic_provenance",
        ("tampered",),
    )
    calls = []

    def evaluator(**kwargs):
        calls.append(kwargs)
        return evaluate_governed_creative_workflow_transition(**kwargs)

    with pytest.raises(ValueError, match="deterministic provenance mismatch"):
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            admission,
            **_kwargs(),
            workflow_transition_evaluator=evaluator,
        )

    assert calls == []


def test_consumer_rejects_wrong_admission_type():
    with pytest.raises(ValueError, match="exact GeneratedCandidateAssetAdmission"):
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            object(),
            **_kwargs(),
        )


def test_consumer_rejects_naive_consumption_timestamp_before_evaluation():
    kwargs = _kwargs()
    kwargs["consumption_timestamp"] = NOW.replace(tzinfo=None)
    calls = []

    def evaluator(**values):
        calls.append(values)
        return evaluate_governed_creative_workflow_transition(**values)

    with pytest.raises(ValueError, match="timezone-aware"):
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            _admission(),
            **kwargs,
            workflow_transition_evaluator=evaluator,
        )

    assert calls == []


def test_consumer_rejects_non_exact_evaluator_result():
    def evaluator(**kwargs):
        return object()

    with pytest.raises(ValueError, match="must return an exact"):
        consume_generated_candidate_asset_admission_execution_for_workflow_transition(
            _admission(),
            **_kwargs(),
            workflow_transition_evaluator=evaluator,
        )


def test_consumer_does_not_mutate_admission_record():
    admission = _admission()
    before = admission

    consume_generated_candidate_asset_admission_execution_for_workflow_transition(
        admission,
        **_kwargs(),
    )

    assert admission == before
    assert admission.execution_outcome == ADMISSION_OUTCOME_ADMITTED
