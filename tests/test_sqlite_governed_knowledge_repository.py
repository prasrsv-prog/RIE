from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3

from rie.application.governed_knowledge_constructor import (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_ID,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_VERSION,
    GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED,
    GovernedKnowledgeConstructionResult,
)
from rie.application.knowledge_constructor import (
    CONSTRUCTION_DECISION_CONSTRUCTED,
    KnowledgeConstructionResult,
)
from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
    REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,
    GovernedKnowledge,
    GovernedKnowledgeIdentityInput,
    compute_governed_knowledge_id,
)
from rie.domain.governed_knowledge_lifecycle_assertion import (
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION,
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED,
    GovernedKnowledgeLifecycleAssertion,
    GovernedKnowledgeLifecycleAssertionIdentityInput,
    compute_governed_knowledge_lifecycle_assertion_id,
)
from rie.domain.governed_knowledge_lifecycle_assertion_interpretation_premise import (
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE,
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_CONTRACT_VERSION,
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_SCOPE_DECLARED,
    GovernedKnowledgeLifecycleAssertionInterpretationPremise,
    GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput,
    compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id,
)
from rie.domain.governed_knowledge_lifecycle_assertion_interpretation_result import (
    interpret_governed_knowledge_lifecycle_assertion_premise_structurally,
)
from rie.domain.knowledge_candidate import (
    INITIAL_AUTHORITY_STATUS,
    INITIAL_CONFLICT_STATUS,
    INITIAL_LIFECYCLE_STATUS,
    INITIAL_REVIEW_STATUS,
    KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
    VERBATIM_TEXT_STATEMENT_TYPE,
    KnowledgeCandidate,
    KnowledgeCandidateIdentityInput,
    KnowledgeEvidenceSupport,
    compute_knowledge_candidate_id,
)
from rie.domain.knowledge_promotion_decision import (
    KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION,
    PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
)
from rie.domain.knowledge_promotion_execution import (
    KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION,
    PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    PROMOTION_EXECUTION_SCOPE_DECLARED,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)
from rie.knowledge_repository import (
    KNOWLEDGE_REPOSITORY_INITIAL_WRITE_REQUEST_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_ID,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_VERSION,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_REQUEST_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_POLICY_ID,
    KNOWLEDGE_REPOSITORY_POLICY_VERSION,
    KnowledgeRepositoryInitialWriteRequest,
    KnowledgeRepositoryLifecycleTransitionRequest,
    SqliteGovernedKnowledgeRepository,
)
from rie.persisted_evidence_knowledge_construction import (
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED,
    PersistedEvidenceKnowledgeCompatibilityRecord,
    PersistedEvidenceKnowledgeConstructionResult,
    derive_persisted_evidence_knowledge_compatibility_record_id,
)

BASE_TIME = datetime(
    2026,
    7,
    21,
    8,
    0,
    tzinfo=timezone.utc,
)


def _hex(prefix: str, character: str) -> str:
    return prefix + character * 64


def _candidate() -> KnowledgeCandidate:
    support = (
        KnowledgeEvidenceSupport(
            evidence_id=_hex("ev1_", "1"),
            acceptance_record_ids=(_hex("ar1_", "2"),),
            acceptance_review_record_ids=("review-1",),
            source_id="source-1",
            source_content_digest="3" * 64,
            source_authority_status="official",
            source_lifecycle_status="active",
            payload_digest="4" * 64,
            locator_type="line",
            locator_value="1",
            locator_schema_version="1.0.0",
        ),
    )
    identity = KnowledgeCandidateIdentityInput(
        candidate_contract_version=(
            KNOWLEDGE_CANDIDATE_CONTRACT_VERSION
        ),
        statement_type=VERBATIM_TEXT_STATEMENT_TYPE,
        statement="The governed fixture statement.",
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        support=support,
        authority_status=INITIAL_AUTHORITY_STATUS,
        lifecycle_status=INITIAL_LIFECYCLE_STATUS,
        review_status=INITIAL_REVIEW_STATUS,
        conflict_status=INITIAL_CONFLICT_STATUS,
    )
    return KnowledgeCandidate(
        knowledge_candidate_id=(
            compute_knowledge_candidate_id(identity)
        ),
        contract_version=identity.candidate_contract_version,
        statement_type=identity.statement_type,
        statement=identity.statement,
        support=identity.support,
        construction_rule_id=identity.construction_rule_id,
        construction_rule_version=(
            identity.construction_rule_version
        ),
        authority_status=identity.authority_status,
        lifecycle_status=identity.lifecycle_status,
        review_status=identity.review_status,
        conflict_status=identity.conflict_status,
        conflict_ids=(),
        diagnostics=(),
    )


def _governed(
    candidate: KnowledgeCandidate,
) -> GovernedKnowledge:
    snapshot = compute_knowledge_candidate_review_snapshot_digest(
        candidate
    )
    fields = dict(
        contract_version=GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            candidate.contract_version
        ),
        knowledge_candidate_snapshot_digest=snapshot,
        statement_type=candidate.statement_type,
        statement=candidate.statement,
        support=candidate.support,
        knowledge_promotion_prerequisite_evaluation_id=(
            _hex("kpe1_", "5")
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION
        ),
        knowledge_promotion_decision_id=(
            _hex("kpd1_", "6")
        ),
        knowledge_promotion_decision_contract_version=(
            KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION
        ),
        promotion_decision_outcome=(
            PROMOTION_DECISION_OUTCOME_AUTHORIZED
        ),
        authorization_scope=PROMOTION_DECISION_AUTHORIZATION_SCOPE,
        knowledge_promotion_execution_id=(
            _hex("kpx1_", "7")
        ),
        knowledge_promotion_execution_contract_version=(
            KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION
        ),
        promotion_execution_scope=PROMOTION_EXECUTION_SCOPE_DECLARED,
        promotion_execution_outcome=(
            PROMOTION_EXECUTION_OUTCOME_COMPLETED
        ),
        construction_scope=GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE,
        construction_reference="fixture-construction",
        reason_codes=(
            REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON,
        ),
        constructed_by="fixture-builder",
        constructed_at=BASE_TIME,
        construction_policy_id=(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_ID
        ),
        construction_policy_version=(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_POLICY_VERSION
        ),
    )
    identity = GovernedKnowledgeIdentityInput(**fields)
    return GovernedKnowledge(
        governed_knowledge_id=compute_governed_knowledge_id(
            identity
        ),
        diagnostics=(),
        **fields,
    )


def _lifecycle(
    governed: GovernedKnowledge,
    value: str,
    offset: int,
):
    asserted_at = BASE_TIME + timedelta(minutes=offset)
    assertion_fields = dict(
        contract_version=(
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION
        ),
        governed_knowledge_id=(
            governed.governed_knowledge_id
        ),
        governed_knowledge_contract_version=(
            governed.contract_version
        ),
        assertion_scope=(
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED
        ),
        assertion_scope_reference="fixture-subject",
        assertion_value=value,
        asserted_by="fixture-builder",
        asserted_at=asserted_at,
        assertion_policy_id="fixture-lifecycle-assertion",
        assertion_policy_version="1.0.0",
        reason_codes=("fixture_lifecycle_assertion",),
    )
    assertion_identity = (
        GovernedKnowledgeLifecycleAssertionIdentityInput(
            **assertion_fields
        )
    )
    assertion = GovernedKnowledgeLifecycleAssertion(
        governed_knowledge_lifecycle_assertion_id=(
            compute_governed_knowledge_lifecycle_assertion_id(
                assertion_identity
            )
        ),
        **assertion_fields,
    )
    premise_fields = dict(
        contract_version=(
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_CONTRACT_VERSION
        ),
        governed_knowledge_id=(
            governed.governed_knowledge_id
        ),
        governed_knowledge_contract_version=(
            governed.contract_version
        ),
        premise_scope=(
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_SCOPE_DECLARED
        ),
        premise_scope_reference="fixture-subject",
        completeness_declaration=(
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE
        ),
        assertions=(assertion,),
        declared_by="fixture-builder",
        declared_at=asserted_at,
        declaration_policy_id="fixture-lifecycle-premise",
        declaration_policy_version="1.0.0",
        reason_codes=("fixture_lifecycle_premise",),
    )
    premise_identity = (
        GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput(
            **premise_fields
        )
    )
    premise = (
        GovernedKnowledgeLifecycleAssertionInterpretationPremise(
            governed_knowledge_lifecycle_assertion_interpretation_premise_id=(
                compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
                    premise_identity
                )
            ),
            **premise_fields,
        )
    )
    return interpret_governed_knowledge_lifecycle_assertion_premise_structurally(
        premise=premise,
        interpreted_by="fixture-builder",
        interpretation_policy_id=(
            "fixture-structural-interpretation"
        ),
        interpretation_policy_version="1.0.0",
        reason_codes=("fixture_structural_interpretation",),
    )


def build_fixture_bundle() -> dict[str, object]:
    candidate = _candidate()
    governed = _governed(candidate)
    compatibility_kwargs = dict(
        contract_version=(
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION
        ),
        repository_revision_id=_hex("evr1_", "8"),
        source_id="source-1",
        revision_number=1,
        previous_revision_id=None,
        collection_id=_hex("evc1_", "d"),
        collection_payload_digest="9" * 64,
        repository_audit_id=_hex("eva1_", "a"),
        traceable_evidence_id=_hex("evm1_", "b"),
        accepted_evidence_id=_hex("ev1_", "c"),
        acceptance_record_ids=(_hex("ar1_", "2"),),
        construction_rule_id=candidate.construction_rule_id,
        construction_rule_version=(
            candidate.construction_rule_version
        ),
        compatibility_policy_id=(
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID
        ),
        compatibility_policy_version=(
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION
        ),
    )
    compatibility = (
        PersistedEvidenceKnowledgeCompatibilityRecord(
            compatibility_record_id=(
                derive_persisted_evidence_knowledge_compatibility_record_id(
                    **compatibility_kwargs
                )
            ),
            **compatibility_kwargs,
        )
    )
    candidate_result = KnowledgeConstructionResult(
        decision=CONSTRUCTION_DECISION_CONSTRUCTED,
        knowledge_candidate=candidate,
        reason_codes=(),
        diagnostics=(),
    )
    persisted = PersistedEvidenceKnowledgeConstructionResult(
        contract_version=(
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ),
        status=(
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED
        ),
        mutation_performed=False,
        compatibility_record=compatibility,
        knowledge_construction_result=candidate_result,
        issue=None,
    )
    governed_result = GovernedKnowledgeConstructionResult(
        result_status=(
            GOVERNED_KNOWLEDGE_CONSTRUCTION_RESULT_CONSTRUCTED
        ),
        governed_knowledge=governed,
        reason_codes=(),
        diagnostics=(),
    )
    initial_lifecycle = _lifecycle(
        governed,
        "active",
        1,
    )
    next_lifecycle = _lifecycle(
        governed,
        "retired",
        2,
    )
    initial_request = KnowledgeRepositoryInitialWriteRequest(
        contract_version=(
            KNOWLEDGE_REPOSITORY_INITIAL_WRITE_REQUEST_CONTRACT_VERSION
        ),
        governed_knowledge=governed,
        persisted_evidence_knowledge_construction_result=persisted,
        governed_knowledge_construction_result=governed_result,
        lifecycle_interpretation_result=initial_lifecycle,
        actor_id="fixture-actor",
        recorded_at_utc=BASE_TIME + timedelta(minutes=3),
        repository_policy_id=KNOWLEDGE_REPOSITORY_POLICY_ID,
        repository_policy_version=(
            KNOWLEDGE_REPOSITORY_POLICY_VERSION
        ),
    )
    return {
        "candidate": candidate,
        "governed": governed,
        "initial_lifecycle": initial_lifecycle,
        "next_lifecycle": next_lifecycle,
        "initial_request": initial_request,
    }


def build_transition_request(
    initial_result,
    next_lifecycle,
):
    return KnowledgeRepositoryLifecycleTransitionRequest(
        contract_version=(
            KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_REQUEST_CONTRACT_VERSION
        ),
        governed_knowledge_id=(
            initial_result.governed_knowledge.governed_knowledge_id
        ),
        expected_prior_revision_id=(
            initial_result.revision.revision_id
        ),
        expected_prior_revision_number=(
            initial_result.revision.revision_number
        ),
        next_lifecycle_interpretation_result=(
            next_lifecycle
        ),
        transition_reason_codes=(
            "fixture_lifecycle_transition",
        ),
        actor_id="fixture-actor",
        recorded_at_utc=BASE_TIME + timedelta(minutes=4),
        transition_policy_id=(
            KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_ID
        ),
        transition_policy_version=(
            KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_VERSION
        ),
    )


def test_initial_replay_transition_lookup_history(
    tmp_path: Path,
) -> None:
    bundle = build_fixture_bundle()
    repository = SqliteGovernedKnowledgeRepository(
        tmp_path / "knowledge.sqlite3"
    )
    initial = repository.persist_initial(
        bundle["initial_request"]
    )
    assert initial.status == "persisted_initial"
    assert initial.mutation_performed is True
    replay = repository.persist_initial(
        bundle["initial_request"]
    )
    assert replay.status == "unchanged_exact_replay"
    assert replay.mutation_performed is False

    transition_request = build_transition_request(
        initial,
        bundle["next_lifecycle"],
    )
    transition = repository.append_lifecycle_transition(
        transition_request
    )
    assert transition.status == (
        "appended_lifecycle_transition"
    )
    assert transition.revision.revision_number == 2

    transition_replay = (
        repository.append_lifecycle_transition(
            transition_request
        )
    )
    assert transition_replay.status == (
        "unchanged_exact_replay"
    )
    assert transition_replay.mutation_performed is False

    by_id = repository.get_by_revision_id(
        transition.revision.revision_id
    )
    assert by_id.status == "found"
    by_number = (
        repository.get_by_governed_knowledge_revision(
            initial.governed_knowledge.governed_knowledge_id,
            1,
        )
    )
    assert by_number.status == "found"
    history = repository.list_governed_knowledge_history(
        initial.governed_knowledge.governed_knowledge_id
    )
    assert [
        item.revision_number
        for item in history.revisions
    ] == [1, 2]
    assert len(history.transition_records) == 1


def test_competing_child_and_no_change(
    tmp_path: Path,
) -> None:
    bundle = build_fixture_bundle()
    repository = SqliteGovernedKnowledgeRepository(
        tmp_path / "knowledge.sqlite3"
    )
    initial = repository.persist_initial(
        bundle["initial_request"]
    )
    request = build_transition_request(
        initial,
        bundle["next_lifecycle"],
    )
    assert repository.append_lifecycle_transition(
        request
    ).status == "appended_lifecycle_transition"

    competing_lifecycle = _lifecycle(
        bundle["governed"],
        "archived",
        5,
    )
    competing = KnowledgeRepositoryLifecycleTransitionRequest(
        contract_version=request.contract_version,
        governed_knowledge_id=request.governed_knowledge_id,
        expected_prior_revision_id=(
            request.expected_prior_revision_id
        ),
        expected_prior_revision_number=(
            request.expected_prior_revision_number
        ),
        next_lifecycle_interpretation_result=(
            competing_lifecycle
        ),
        transition_reason_codes=("competing_transition",),
        actor_id=request.actor_id,
        recorded_at_utc=(
            request.recorded_at_utc
            + timedelta(minutes=1)
        ),
        transition_policy_id=(
            request.transition_policy_id
        ),
        transition_policy_version=(
            request.transition_policy_version
        ),
    )
    conflict = repository.append_lifecycle_transition(
        competing
    )
    assert conflict.status == "rejected"
    assert conflict.issue.code == (
        "lifecycle_transition_conflict"
    )

    second = SqliteGovernedKnowledgeRepository(
        tmp_path / "second.sqlite3"
    )
    second_initial = second.persist_initial(
        bundle["initial_request"]
    )
    no_change = KnowledgeRepositoryLifecycleTransitionRequest(
        contract_version=request.contract_version,
        governed_knowledge_id=(
            second_initial.governed_knowledge.governed_knowledge_id
        ),
        expected_prior_revision_id=(
            second_initial.revision.revision_id
        ),
        expected_prior_revision_number=1,
        next_lifecycle_interpretation_result=(
            bundle["initial_lifecycle"]
        ),
        transition_reason_codes=("no_change",),
        actor_id=request.actor_id,
        recorded_at_utc=request.recorded_at_utc,
        transition_policy_id=(
            request.transition_policy_id
        ),
        transition_policy_version=(
            request.transition_policy_version
        ),
    )
    rejected = second.append_lifecycle_transition(
        no_change
    )
    assert rejected.issue.code == (
        "lifecycle_transition_no_change"
    )


def test_not_found_unsupported_schema_and_corrupt(
    tmp_path: Path,
) -> None:
    missing = SqliteGovernedKnowledgeRepository(
        tmp_path / "missing.sqlite3"
    )
    assert missing.get_by_revision_id(
        _hex("gkr1_", "0")
    ).status == "not_found"

    unsupported_path = (
        tmp_path / "unsupported.sqlite3"
    )
    connection = sqlite3.connect(unsupported_path)
    connection.execute("CREATE TABLE alien(value TEXT)")
    connection.commit()
    connection.close()
    unsupported = SqliteGovernedKnowledgeRepository(
        unsupported_path
    )
    result = unsupported.get_by_revision_id(
        _hex("gkr1_", "0")
    )
    assert result.status == "rejected"
    assert result.issue.code == "unsupported_schema"

    corrupt_path = tmp_path / "corrupt.sqlite3"
    corrupt_path.write_bytes(b"not a sqlite database")
    corrupt = SqliteGovernedKnowledgeRepository(
        corrupt_path
    )
    result = corrupt.get_by_revision_id(
        _hex("gkr1_", "0")
    )
    assert result.status == "rejected"
    assert result.issue.code in {
        "repository_corrupt",
        "repository_unavailable",
    }


def test_unavailable_parent(tmp_path: Path) -> None:
    repository = SqliteGovernedKnowledgeRepository(
        tmp_path
        / "missing-parent"
        / "knowledge.sqlite3"
    )
    result = repository.get_by_revision_id(
        _hex("gkr1_", "0")
    )
    assert result.status == "rejected"
    assert result.issue.code == "repository_unavailable"
