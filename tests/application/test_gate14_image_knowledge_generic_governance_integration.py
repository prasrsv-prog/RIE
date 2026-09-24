"""Gate 14 proof: image-derived KnowledgeCandidate uses the generic governance pipeline."""

from __future__ import annotations

import inspect
from pathlib import Path
import runpy

from rie.application.governed_knowledge_constructor import construct_governed_knowledge
from rie.application.image_knowledge_constructor import construct_image_knowledge_candidate
from rie.application.knowledge_authority_decider import decide_knowledge_authority
from rie.application.knowledge_conflict_assessor import assess_knowledge_candidate_conflict
from rie.application.knowledge_governor import govern_knowledge_candidate
from rie.application.knowledge_promotion_decider import decide_knowledge_promotion
from rie.application.knowledge_promotion_executor import record_knowledge_promotion_execution
from rie.application.knowledge_promotion_prerequisite_evaluator import (
    evaluate_knowledge_promotion_prerequisites,
)
from rie.application.knowledge_reviewer import review_knowledge_candidate
from rie.application.knowledge_constructor import construct_knowledge_candidate
from rie.domain.governed_knowledge import GovernedKnowledge
from rie.domain.knowledge_candidate import KnowledgeCandidate


ROOT = Path(__file__).resolve().parents[2]


def _load_test_namespace(relative_path: str) -> dict[str, object]:
    return runpy.run_path(str(ROOT / relative_path))


def _helper(namespace: dict[str, object], name: str, **values: object) -> object:
    function = namespace[name]
    assert callable(function), f"{name} must be callable"
    signature = inspect.signature(function)
    has_var_keyword = any(
        parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    )
    if has_var_keyword:
        return function(**values)  # type: ignore[misc]
    accepted = {
        key: value
        for key, value in values.items()
        if key in signature.parameters
    }
    missing = [
        name
        for name, parameter in signature.parameters.items()
        if parameter.default is inspect.Parameter.empty
        and parameter.kind
        not in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        )
        and name not in accepted
    ]
    assert not missing, (
        f"helper {function.__name__} has unsupported required parameters: {missing}; "
        f"signature={signature}"
    )
    return function(**accepted)  # type: ignore[misc]


def _constant(namespace: dict[str, object], prefix: str) -> object:
    matches = [
        value
        for name, value in namespace.items()
        if name.startswith(prefix)
    ]
    assert len(matches) == 1, f"expected one constant for {prefix}, got {len(matches)}"
    return matches[0]


def _image_candidate() -> KnowledgeCandidate:
    namespace = _load_test_namespace(
        "tests/application/test_image_knowledge_constructor.py"
    )
    request = namespace["_request"]()
    result = construct_image_knowledge_candidate(request)
    assert result.knowledge_candidate is not None
    assert type(result.knowledge_candidate) is KnowledgeCandidate
    assert result.relationship_support is not None
    return result.knowledge_candidate


def _text_candidate() -> KnowledgeCandidate:
    namespace = _load_test_namespace(
        "tests/application/test_knowledge_constructor.py"
    )
    request = namespace["_request"]()
    result = construct_knowledge_candidate(request)
    assert result.knowledge_candidate is not None
    assert type(result.knowledge_candidate) is KnowledgeCandidate
    return result.knowledge_candidate


def _review_and_govern(image_candidate: KnowledgeCandidate):
    reviewer = _load_test_namespace(
        "tests/application/test_knowledge_reviewer.py"
    )
    review_request = _helper(
        reviewer,
        "_request",
        candidate=image_candidate,
    )
    review_result = review_knowledge_candidate(review_request)
    assert review_result.review_record is not None

    governor = _load_test_namespace(
        "tests/application/test_knowledge_governor.py"
    )
    governance_request = _helper(
        governor,
        "_request",
        candidate=image_candidate,
        reviews=(review_result.review_record,),
    )
    governance_result = govern_knowledge_candidate(governance_request)
    assert governance_result.governance_decision_record is not None
    return review_result.review_record, governance_result.governance_decision_record


def _authorize(image_candidate: KnowledgeCandidate, governance_record):
    authority = _load_test_namespace(
        "tests/application/test_knowledge_authority_decider.py"
    )
    request = _helper(
        authority,
        "_request",
        candidate=image_candidate,
        governance=(governance_record,),
    )
    result = decide_knowledge_authority(request)
    assert result.authority_decision is not None
    return result.authority_decision


def _pairwise_conflict(
    image_candidate: KnowledgeCandidate,
    text_candidate: KnowledgeCandidate,
    *,
    no_conflict: bool,
):
    namespace = _load_test_namespace(
        "tests/application/test_knowledge_conflict_assessor.py"
    )
    participants = tuple(
        sorted(
            (image_candidate, text_candidate),
            key=lambda candidate: candidate.knowledge_candidate_id,
        )
    )
    values: dict[str, object] = {"participants": participants}
    if no_conflict:
        values["assessment_outcome"] = _constant(
            namespace,
            "ASSESSMENT_OUTCOME_NO_CONFLICT",
        )
        values["reason_codes"] = ("pairwise_no_conflict_identified",)
    else:
        values["assessment_outcome"] = _constant(
            namespace,
            "ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED",
        )
        values["reason_codes"] = ("semantic_conflict_identified",)

    request = _helper(namespace, "_request", **values)
    result = assess_knowledge_candidate_conflict(request)
    assert result.conflict_assessment_record is not None
    record = result.conflict_assessment_record
    assert tuple(
        participant.knowledge_candidate_id for participant in record.participants
    ) == tuple(candidate.knowledge_candidate_id for candidate in participants)
    return record


def _promotion_evaluation(
    image_candidate: KnowledgeCandidate,
    text_candidate: KnowledgeCandidate,
    governance_record,
    conflict_record,
    authority_record,
):
    namespace = _load_test_namespace(
        "tests/application/test_knowledge_promotion_prerequisite_evaluator.py"
    )
    scope = _helper(
        namespace,
        "_scope",
        target=image_candidate,
        peers=(text_candidate,),
    )
    request = _helper(
        namespace,
        "_request",
        candidate=image_candidate,
        scope=scope,
        governance=(governance_record,),
        conflicts=(conflict_record,),
        authorities=(authority_record,),
        reasons=("declared_scope_prerequisites_satisfied",),
    )
    return evaluate_knowledge_promotion_prerequisites(request)


def test_explicit_cross_modal_conflict_is_recorded_and_cannot_auto_promote() -> None:
    image_candidate = _image_candidate()
    text_candidate = _text_candidate()
    original_conflict_status = image_candidate.conflict_status
    original_conflict_ids = image_candidate.conflict_ids

    _, governance = _review_and_govern(image_candidate)
    authority = _authorize(image_candidate, governance)
    conflict = _pairwise_conflict(
        image_candidate,
        text_candidate,
        no_conflict=False,
    )

    assert conflict.reason_codes == ("semantic_conflict_identified",)
    assert image_candidate.conflict_status == original_conflict_status
    assert image_candidate.conflict_ids == original_conflict_ids

    evaluation_result = _promotion_evaluation(
        image_candidate,
        text_candidate,
        governance,
        conflict,
        authority,
    )

    if evaluation_result.evaluation is None:
        assert evaluation_result.reason_codes
        return

    decider = _load_test_namespace(
        "tests/application/test_knowledge_promotion_decider.py"
    )
    request = _helper(
        decider,
        "_request",
        candidate=image_candidate,
        evaluation=evaluation_result.evaluation,
    )
    decision_result = decide_knowledge_promotion(request)
    assert decision_result.promotion_decision_record is None


def test_explicit_no_conflict_image_candidate_reaches_generic_governed_knowledge() -> None:
    image_candidate = _image_candidate()
    text_candidate = _text_candidate()

    review_record, governance = _review_and_govern(image_candidate)
    authority = _authorize(image_candidate, governance)
    conflict = _pairwise_conflict(
        image_candidate,
        text_candidate,
        no_conflict=True,
    )

    assert conflict.reason_codes == ("pairwise_no_conflict_identified",)
    assert review_record.knowledge_candidate_id == image_candidate.knowledge_candidate_id
    assert governance.knowledge_candidate_id == image_candidate.knowledge_candidate_id
    assert authority.knowledge_candidate_id == image_candidate.knowledge_candidate_id

    evaluation_result = _promotion_evaluation(
        image_candidate,
        text_candidate,
        governance,
        conflict,
        authority,
    )
    assert evaluation_result.evaluation is not None
    evaluation = evaluation_result.evaluation
    assert evaluation.knowledge_candidate_id == image_candidate.knowledge_candidate_id

    decider = _load_test_namespace(
        "tests/application/test_knowledge_promotion_decider.py"
    )
    decision_request = _helper(
        decider,
        "_request",
        candidate=image_candidate,
        evaluation=evaluation,
    )
    decision_result = decide_knowledge_promotion(decision_request)
    assert decision_result.promotion_decision_record is not None
    decision = decision_result.promotion_decision_record

    executor = _load_test_namespace(
        "tests/application/test_knowledge_promotion_executor.py"
    )
    execution_request = _helper(
        executor,
        "_request",
        candidate=image_candidate,
        evaluation=evaluation,
        decision=decision,
    )
    execution_result = record_knowledge_promotion_execution(execution_request)
    assert execution_result.promotion_execution_record is not None
    execution = execution_result.promotion_execution_record

    governed = _load_test_namespace(
        "tests/application/test_governed_knowledge_constructor.py"
    )
    construction_request = _helper(
        governed,
        "_request",
        candidate=image_candidate,
        evaluation=evaluation,
        decision=decision,
        execution=execution,
    )
    construction_result = construct_governed_knowledge(construction_request)
    assert construction_result.governed_knowledge is not None
    assert type(construction_result.governed_knowledge) is GovernedKnowledge
    assert (
        construction_result.governed_knowledge.knowledge_candidate_id
        == image_candidate.knowledge_candidate_id
    )
