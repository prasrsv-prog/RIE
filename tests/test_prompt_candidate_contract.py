from dataclasses import FrozenInstanceError

import pytest

from rie.prompt_candidate import (
    PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION,
    PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED,
    PROMPT_CANDIDATE_ISSUE_CODES,
    PROMPT_INTENT_CONTRACT_VERSION,
    PromptCandidateConstructionResult,
    PromptCandidateIssue,
    PromptIntent,
    derive_prompt_intent_id,
)


def _intent(**overrides):
    values = dict(
        contract_version=PROMPT_INTENT_CONTRACT_VERSION,
        intent_id="pi1_" + "0" * 64,
        objective="Create a structural product summary.",
        audience="internal reviewer",
        language="en",
        output_format="structured text",
        required_constraints=("preserve exact source facts",),
        forbidden_constraints=("invent unsupported facts",),
    )
    values.update(overrides)
    provisional = PromptIntent(**values)
    values["intent_id"] = derive_prompt_intent_id(provisional)
    return PromptIntent(**values)


def test_prompt_intent_is_immutable_and_preserves_order() -> None:
    intent = _intent(
        required_constraints=("first", "second"),
        forbidden_constraints=("third",),
    )
    assert intent.required_constraints == ("first", "second")
    with pytest.raises(FrozenInstanceError):
        intent.objective = "changed"


def test_prompt_intent_rejects_invalid_fields() -> None:
    with pytest.raises(ValueError):
        _intent(objective="   ")
    with pytest.raises(ValueError):
        _intent(required_constraints=("same", "same"))
    with pytest.raises(ValueError):
        _intent(
            required_constraints=("same",),
            forbidden_constraints=("same",),
        )


def test_issue_vocabulary_and_rejected_result_invariant() -> None:
    assert len(PROMPT_CANDIDATE_ISSUE_CODES) == 30
    assert len(set(PROMPT_CANDIDATE_ISSUE_CODES)) == 30
    issue = PromptCandidateIssue(
        code="invalid_request",
        message="Invalid request.",
    )
    result = PromptCandidateConstructionResult(
        contract_version=(
            PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ),
        status=PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED,
        prompt_candidate=None,
        issue=issue,
    )
    assert result.issue == issue
    with pytest.raises(ValueError):
        PromptCandidateConstructionResult(
            contract_version=(
                PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION
            ),
            status=PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED,
            prompt_candidate=None,
            issue=None,
        )
