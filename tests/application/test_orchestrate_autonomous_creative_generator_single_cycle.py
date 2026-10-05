from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from rie.application.concrete_visual_generation_execution_adapter import (
    ProviderExecutionResponse,
    ResolvedVisualReference,
    VisualGenerationExecutionConfig,
)
from rie.application.orchestrate_autonomous_creative_generator_single_cycle import (
    AssetAdmissionActionInputs,
    AutonomousIterationActionInputs,
    RetryRegenerationActionInputs,
    WorkflowTransitionActionInputs,
    orchestrate_autonomous_creative_generator_single_cycle,
)
from rie.application.visual_generation_provider import VisualGenerationRequest
from rie.domain.generated_candidate_evaluation import (
    GeneratedCandidateCriterionResult,
)


T0 = datetime(2026, 10, 5, 8, 0, tzinfo=timezone.utc)


class Resolver:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def resolve(self, asset_id: str) -> ResolvedVisualReference:
        self.calls.append(asset_id)
        return ResolvedVisualReference(
            requested_asset_id=asset_id,
            resolved_asset_id=asset_id,
            provider_media_ref=f"media:{asset_id}",
            use_eligible=True,
        )


def _transport(calls: list[object], *, output_ref: str = "provider-output:1"):
    def transport(payload):
        calls.append(payload)
        return ProviderExecutionResponse(
            execution_status="SUCCEEDED",
            provider_output_refs=(output_ref,),
            provider_execution_ref="provider-execution:1",
            diagnostic_message="completed",
        )
    return transport


def _base_kwargs(*, requested_action: str, authorization_outcome: str):
    calls: list[object] = []
    resolver = Resolver()
    return {
        "calls": calls,
        "resolver": resolver,
        "kwargs": {
            "request": VisualGenerationRequest(
                grounded_prompt="Generate one governed creative candidate.",
                selected_reference_asset_ids=("asset:reference:1",),
            ),
            "execution_config": VisualGenerationExecutionConfig(
                provider_id="provider:explicit",
                model_id="model:explicit",
            ),
            "reference_resolver": resolver,
            "transport": _transport(calls),
            "creative_result_candidate_id": "candidate:1",
            "workflow_request_reference": "workflow:1",
            "project_context_reference": "project:1",
            "campaign_context_reference": ("project:1", "campaign:1"),
            "creative_brief_reference": "brief:1",
            "instruction_reference": (
                "instruction:1",
                "APPROVED_INSTRUCTION",
            ),
            "originating_manual_handoff_reference": None,
            "candidate_admission_timestamp": T0 + timedelta(minutes=1),
            "candidate_admitting_actor_reference": "actor:admitter",
            "generated_output_bytes": b"generated-image-content",
            "generated_output_checksum": None,
            "criterion_results": (
                GeneratedCandidateCriterionResult(
                    criterion_id="criterion:1",
                    outcome="passed",
                    reason_evidence_reference="evidence:criterion:1",
                ),
            ),
            "evaluator_actor_reference": "actor:evaluator",
            "evaluation_timestamp": T0 + timedelta(minutes=2),
            "decision_outcome": "ACCEPTED",
            "decision_reason_evidence_reference": "evidence:decision:1",
            "decision_actor_reference": "actor:decision",
            "decision_timestamp": T0 + timedelta(minutes=3),
            "requested_action": requested_action,
            "authorization_outcome": authorization_outcome,
            "authorization_reason_evidence_reference": (
                "evidence:authorization:1"
            ),
            "authorization_actor_reference": "actor:authorization",
            "authorization_timestamp": T0 + timedelta(minutes=4),
            "action_inputs": None,
            "cycle_actor_reference": "actor:cycle",
            "cycle_timestamp": T0 + timedelta(minutes=6),
        },
    }


def test_denied_authorization_executes_no_action_and_one_initial_provider_call() -> None:
    case = _base_kwargs(
        requested_action="ASSET_ADMISSION",
        authorization_outcome="DENIED",
    )
    result = orchestrate_autonomous_creative_generator_single_cycle(
        **case["kwargs"]
    )

    assert len(case["calls"]) == 1
    assert case["resolver"].calls == ["asset:reference:1"]
    assert result.authorization.authorization_outcome == "DENIED"
    assert result.action_execution is None
    assert result.branch_outcome == "NO_ACTION"


def test_asset_admission_branch_executes_exactly_one_matching_action() -> None:
    case = _base_kwargs(
        requested_action="ASSET_ADMISSION",
        authorization_outcome="AUTHORIZED",
    )
    case["kwargs"]["action_inputs"] = AssetAdmissionActionInputs(
        admitted_asset_reference="asset:admitted:1",
        execution_actor_reference="actor:asset-service",
        execution_timestamp=T0 + timedelta(minutes=5),
    )

    result = orchestrate_autonomous_creative_generator_single_cycle(
        **case["kwargs"]
    )

    assert len(case["calls"]) == 1
    assert result.branch_outcome == "ASSET_ADMISSION"
    assert result.action_execution.admitted_asset_reference == "asset:admitted:1"
    assert (
        result.action_execution.authorization_id
        == result.authorization.authorization_id
    )


def test_retry_branch_performs_one_separately_authorized_retry_only() -> None:
    case = _base_kwargs(
        requested_action="RETRY_REGENERATION",
        authorization_outcome="AUTHORIZED",
    )
    retry_calls: list[object] = []
    retry_resolver = Resolver()
    case["kwargs"]["action_inputs"] = RetryRegenerationActionInputs(
        retry_request=VisualGenerationRequest(
            grounded_prompt="Explicit retry request.",
            selected_reference_asset_ids=("asset:retry:1",),
        ),
        execution_config=VisualGenerationExecutionConfig(
            provider_id="provider:retry",
            model_id="model:retry",
        ),
        reference_resolver=retry_resolver,
        transport=_transport(retry_calls, output_ref="provider-output:retry:1"),
        execution_actor_reference="actor:retry-service",
        execution_timestamp=T0 + timedelta(minutes=5),
    )

    result = orchestrate_autonomous_creative_generator_single_cycle(
        **case["kwargs"]
    )

    assert len(case["calls"]) == 1
    assert len(retry_calls) == 1
    assert result.branch_outcome == "RETRY_REGENERATION"
    assert not hasattr(result.action_execution, "creative_result_candidate_id")
    assert (
        result.candidate.creative_result_candidate_id
        == "candidate:1"
    )


def test_workflow_transition_branch_uses_accepted_executor() -> None:
    case = _base_kwargs(
        requested_action="WORKFLOW_TRANSITION",
        authorization_outcome="AUTHORIZED",
    )
    case["kwargs"]["action_inputs"] = WorkflowTransitionActionInputs(
        idempotency_key="idempotency:1",
        campaign_context_reference=("project:1", "campaign:1"),
        instruction_reference=("instruction:1", "APPROVED_INSTRUCTION"),
        current_workflow_state="REQUESTED",
        requested_next_workflow_state="INPUTS_VALIDATED",
        responsible_actor_or_service_reference=(
            "ACTOR",
            "actor:workflow-service",
        ),
        evidence_references=(
            ("project:1", "campaign:1", "evidence:workflow:1"),
        ),
        reason_codes=("TRANSITION_ACCEPTED",),
        workflow_contract_reference=("GATE_18_CREATIVE_WORKFLOW", "1.0"),
        canonical_input_fingerprint="1" * 64,
        execution_actor_reference="actor:workflow-service",
        execution_timestamp=T0 + timedelta(minutes=5),
    )

    result = orchestrate_autonomous_creative_generator_single_cycle(
        **case["kwargs"]
    )

    assert len(case["calls"]) == 1
    assert result.branch_outcome == "WORKFLOW_TRANSITION"
    assert (
        result.action_execution.requested_next_workflow_state
        == "INPUTS_VALIDATED"
    )


def test_autonomous_iteration_branch_does_not_increment_or_recurse() -> None:
    case = _base_kwargs(
        requested_action="AUTONOMOUS_ITERATION",
        authorization_outcome="AUTHORIZED",
    )
    case["kwargs"]["action_inputs"] = AutonomousIterationActionInputs(
        iteration_plan_reference="iteration-plan:1",
        current_iteration_index=1,
        maximum_iteration_count=3,
        next_step_reference="next-step:review:2",
        execution_actor_reference="actor:iteration-service",
        execution_timestamp=T0 + timedelta(minutes=5),
    )

    result = orchestrate_autonomous_creative_generator_single_cycle(
        **case["kwargs"]
    )

    assert len(case["calls"]) == 1
    assert result.branch_outcome == "AUTONOMOUS_ITERATION"
    assert result.action_execution.current_iteration_index == 1
    assert result.action_execution.maximum_iteration_count == 3
    assert result.action_execution.next_step_reference == "next-step:review:2"


def test_explicit_decision_is_not_inferred_from_passed_evaluation() -> None:
    case = _base_kwargs(
        requested_action="AUTONOMOUS_ITERATION",
        authorization_outcome="DENIED",
    )
    case["kwargs"]["decision_outcome"] = "REJECTED"

    result = orchestrate_autonomous_creative_generator_single_cycle(
        **case["kwargs"]
    )

    assert result.evaluation.aggregate_outcome == "passed"
    assert result.decision.decision_outcome == "REJECTED"
    assert result.action_execution is None


def test_wrong_action_bundle_fails_closed_without_second_provider_call() -> None:
    case = _base_kwargs(
        requested_action="RETRY_REGENERATION",
        authorization_outcome="AUTHORIZED",
    )
    case["kwargs"]["action_inputs"] = AssetAdmissionActionInputs(
        admitted_asset_reference="asset:wrong",
        execution_actor_reference="actor:asset-service",
        execution_timestamp=T0 + timedelta(minutes=5),
    )

    with pytest.raises(ValueError, match="RetryRegenerationActionInputs"):
        orchestrate_autonomous_creative_generator_single_cycle(
            **case["kwargs"]
        )
    assert len(case["calls"]) == 1


def test_non_authorized_action_inputs_are_rejected_without_executor_call() -> None:
    case = _base_kwargs(
        requested_action="ASSET_ADMISSION",
        authorization_outcome="DEFERRED",
    )
    case["kwargs"]["action_inputs"] = AssetAdmissionActionInputs(
        admitted_asset_reference="asset:unused",
        execution_actor_reference="actor:asset-service",
        execution_timestamp=T0 + timedelta(minutes=5),
    )
    with pytest.raises(ValueError, match="action_inputs to be None"):
        orchestrate_autonomous_creative_generator_single_cycle(
            **case["kwargs"]
        )
    assert len(case["calls"]) == 1


def test_identical_exact_inputs_and_provider_evidence_have_same_cycle_identity() -> None:
    first = _base_kwargs(
        requested_action="ASSET_ADMISSION",
        authorization_outcome="DENIED",
    )
    second = _base_kwargs(
        requested_action="ASSET_ADMISSION",
        authorization_outcome="DENIED",
    )

    first_result = orchestrate_autonomous_creative_generator_single_cycle(
        **first["kwargs"]
    )
    second_result = orchestrate_autonomous_creative_generator_single_cycle(
        **second["kwargs"]
    )

    assert first_result.cycle_id == second_result.cycle_id
    assert (
        first_result.deterministic_provenance
        == second_result.deterministic_provenance
    )
