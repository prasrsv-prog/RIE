from __future__ import annotations

from rie.domain.governed_knowledge import GovernedKnowledge
from rie.domain.governed_knowledge_lifecycle_assertion_interpretation_result import (
    GovernedKnowledgeLifecycleAssertionInterpretationResult,
)
from rie.knowledge_repository.knowledge_repository_canonicalization import (
    calculate_governed_knowledge_repository_payload_digest as _source_payload_digest,
    calculate_knowledge_repository_audit_id as _source_audit_id,
    calculate_knowledge_repository_lineage_record_id as _source_lineage_id,
    calculate_knowledge_repository_lifecycle_transition_record_id as _source_transition_id,
    calculate_knowledge_repository_revision_id as _source_revision_id,
)
from rie.knowledge_repository.knowledge_repository_contract import (
    KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION,
    KnowledgeRepositoryAuditRecord,
    KnowledgeRepositoryLineageRecord,
    KnowledgeRepositoryLookupResult,
    KnowledgeRepositoryRevision,
)

from .prompt_candidate_canonicalization import (
    derive_prompt_candidate_id,
    derive_prompt_candidate_payload_digest,
    derive_prompt_candidate_provenance_id,
    derive_prompt_intent_digest,
    derive_prompt_intent_id,
)
from .prompt_candidate_contract import (
    PROMPT_CANDIDATE_CONSTRUCTION_POLICY_ID,
    PROMPT_CANDIDATE_CONSTRUCTION_POLICY_VERSION,
    PROMPT_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION,
    PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION,
    PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED,
    PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED,
    PROMPT_CANDIDATE_CONTRACT_VERSION,
    PROMPT_CANDIDATE_PROVENANCE_CONTRACT_VERSION,
    PROMPT_CANDIDATE_SCHEMA_ID,
    PROMPT_CANDIDATE_SCHEMA_VERSION,
    PROMPT_INTENT_CONTRACT_VERSION,
    PROMPT_CANDIDATE_ID_PREFIX,
    PROMPT_CANDIDATE_PROVENANCE_ID_PREFIX,
    PromptCandidate,
    PromptCandidateConstructionRequest,
    PromptCandidateConstructionResult,
    PromptCandidateProvenance,
    PromptIntent,
    _issue,
)

_ZERO_DIGEST = "0" * 64
_ZERO_CANDIDATE_ID = PROMPT_CANDIDATE_ID_PREFIX + _ZERO_DIGEST
_ZERO_PROVENANCE_ID = PROMPT_CANDIDATE_PROVENANCE_ID_PREFIX + _ZERO_DIGEST


def _rejected(code: str) -> PromptCandidateConstructionResult:
    return PromptCandidateConstructionResult(
        contract_version=PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION,
        status=PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED,
        prompt_candidate=None,
        issue=_issue(code),
    )


def _validate_prompt_intent(value: object) -> str | None:
    if type(value) is not PromptIntent:
        return "invalid_prompt_intent"
    if value.contract_version != PROMPT_INTENT_CONTRACT_VERSION:
        return "unsupported_prompt_intent_contract_version"
    try:
        value.__post_init__()
        expected_id = derive_prompt_intent_id(value)
    except (TypeError, ValueError):
        return "invalid_prompt_intent_field"
    if value.intent_id != expected_id:
        return "prompt_intent_id_mismatch"
    return None


def _validate_revision(value: object) -> str | None:
    if type(value) is not KnowledgeRepositoryRevision:
        return "invalid_source_revision"
    if value.contract_version != KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION:
        return "invalid_source_revision"
    try:
        value.__post_init__()
        expected_id = _source_revision_id(
            governed_knowledge_id=value.governed_knowledge_id,
            revision_number=value.revision_number,
            previous_revision_id=value.previous_revision_id,
            governed_knowledge_payload_digest=(
                value.governed_knowledge_payload_digest
            ),
            lineage_record_id=value.lineage_record_id,
            lifecycle_interpretation_result_id=(
                value.lifecycle_interpretation_result_id
            ),
            lifecycle_interpretation_result_contract_version=(
                value.lifecycle_interpretation_result_contract_version
            ),
            lifecycle_interpretation_result_payload_digest=(
                value.lifecycle_interpretation_result_payload_digest
            ),
            transition_record_id=value.transition_record_id,
            actor_id=value.actor_id,
            recorded_at_utc=value.recorded_at_utc,
        )
    except (TypeError, ValueError):
        return "invalid_source_revision"
    if value.revision_id != expected_id:
        return "source_revision_identity_mismatch"
    return None


def _validate_governed(
    revision: KnowledgeRepositoryRevision,
    value: object,
) -> str | None:
    if type(value) is not GovernedKnowledge:
        return "missing_source_governed_knowledge" if value is None else (
            "source_governed_knowledge_identity_mismatch"
        )
    try:
        value.__post_init__()
    except (TypeError, ValueError):
        return "source_governed_knowledge_identity_mismatch"
    if revision.governed_knowledge_id != value.governed_knowledge_id:
        return "source_governed_knowledge_identity_mismatch"
    try:
        payload_digest = _source_payload_digest(value)
    except (TypeError, ValueError):
        return "source_revision_payload_digest_mismatch"
    if revision.governed_knowledge_payload_digest != payload_digest:
        return "source_revision_payload_digest_mismatch"
    return None


def _validate_lifecycle(
    revision: KnowledgeRepositoryRevision,
    governed: GovernedKnowledge,
    value: object,
) -> str | None:
    if value is None:
        return "missing_source_lifecycle_interpretation_result"
    if type(value) is not GovernedKnowledgeLifecycleAssertionInterpretationResult:
        return "source_lifecycle_interpretation_result_mismatch"
    try:
        value.__post_init__()
    except (TypeError, ValueError):
        return "source_lifecycle_interpretation_result_mismatch"
    if (
        revision.lifecycle_interpretation_result_id
        != value.governed_knowledge_lifecycle_assertion_interpretation_result_id
        or revision.lifecycle_interpretation_result_contract_version
        != value.contract_version
        or value.premise.governed_knowledge_id != governed.governed_knowledge_id
    ):
        return "source_lifecycle_interpretation_result_mismatch"
    try:
        payload_digest = _source_payload_digest(value)
    except (TypeError, ValueError):
        return "source_lifecycle_interpretation_result_mismatch"
    if revision.lifecycle_interpretation_result_payload_digest != payload_digest:
        return "source_lifecycle_interpretation_result_mismatch"
    return None


def _validate_lineage(
    revision: KnowledgeRepositoryRevision,
    governed: GovernedKnowledge,
    value: object,
) -> str | None:
    if value is None:
        return "missing_source_lineage_record"
    if type(value) is not KnowledgeRepositoryLineageRecord:
        return "source_lineage_mismatch"
    if value.contract_version != KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION:
        return "source_lineage_mismatch"
    try:
        value.__post_init__()
        expected_id = _source_lineage_id(
            governed_knowledge_id=value.governed_knowledge_id,
            governed_knowledge_contract_version=(
                value.governed_knowledge_contract_version
            ),
            knowledge_candidate_id=value.knowledge_candidate_id,
            knowledge_candidate_contract_version=(
                value.knowledge_candidate_contract_version
            ),
            knowledge_candidate_snapshot_digest=(
                value.knowledge_candidate_snapshot_digest
            ),
            persisted_evidence_knowledge_compatibility_record_id=(
                value.persisted_evidence_knowledge_compatibility_record_id
            ),
            evidence_repository_revision_id=(
                value.evidence_repository_revision_id
            ),
            evidence_repository_audit_id=value.evidence_repository_audit_id,
            source_id=value.source_id,
            source_revision_number=value.source_revision_number,
            traceable_evidence_id=value.traceable_evidence_id,
            accepted_evidence_id=value.accepted_evidence_id,
            acceptance_record_ids=value.acceptance_record_ids,
            construction_rule_id=value.construction_rule_id,
            construction_rule_version=value.construction_rule_version,
            governed_knowledge_construction_policy_id=(
                value.governed_knowledge_construction_policy_id
            ),
            governed_knowledge_construction_policy_version=(
                value.governed_knowledge_construction_policy_version
            ),
            lineage_policy_id=value.lineage_policy_id,
            lineage_policy_version=value.lineage_policy_version,
        )
    except (TypeError, ValueError):
        return "source_lineage_mismatch"
    if (
        value.lineage_record_id != expected_id
        or revision.lineage_record_id != value.lineage_record_id
        or value.governed_knowledge_id != governed.governed_knowledge_id
        or value.governed_knowledge_contract_version != governed.contract_version
    ):
        return "source_lineage_mismatch"
    return None


def _validate_audit(
    revision: KnowledgeRepositoryRevision,
    governed: GovernedKnowledge,
    value: object,
) -> str | None:
    if value is None:
        return "missing_source_audit_record"
    if type(value) is not KnowledgeRepositoryAuditRecord:
        return "source_audit_mismatch"
    if value.contract_version != KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION:
        return "source_audit_mismatch"
    try:
        value.__post_init__()
        expected_id = _source_audit_id(
            action=value.action,
            revision_id=value.revision_id,
            governed_knowledge_id=value.governed_knowledge_id,
            revision_number=value.revision_number,
            lineage_record_id=value.lineage_record_id,
            transition_record_id=value.transition_record_id,
            actor_id=value.actor_id,
            recorded_at_utc=value.recorded_at_utc,
        )
    except (TypeError, ValueError):
        return "source_audit_mismatch"
    if (
        value.audit_id != expected_id
        or revision.audit_id != value.audit_id
        or value.revision_id != revision.revision_id
        or value.governed_knowledge_id != governed.governed_knowledge_id
        or value.revision_number != revision.revision_number
        or value.lineage_record_id != revision.lineage_record_id
        or value.transition_record_id != revision.transition_record_id
    ):
        return "source_audit_mismatch"
    return None


def _transition_matches(
    revision: KnowledgeRepositoryRevision,
    transition: object,
) -> bool:
    if revision.transition_record_id is None:
        return transition is None
    if transition is None:
        return False
    transition_type = type(transition)
    if (
        transition_type.__module__
        != "rie.knowledge_repository.knowledge_repository_contract"
        or transition_type.__qualname__
        != "KnowledgeRepositoryLifecycleTransitionRecord"
    ):
        return False
    try:
        transition.__post_init__()
        expected_id = _source_transition_id(
            governed_knowledge_id=transition.governed_knowledge_id,
            from_revision_id=transition.from_revision_id,
            from_revision_number=transition.from_revision_number,
            previous_lifecycle_interpretation_result_id=(
                transition.previous_lifecycle_interpretation_result_id
            ),
            next_lifecycle_interpretation_result_id=(
                transition.next_lifecycle_interpretation_result_id
            ),
            transition_reason_codes=transition.transition_reason_codes,
            actor_id=transition.actor_id,
            recorded_at_utc=transition.recorded_at_utc,
            transition_policy_id=transition.transition_policy_id,
            transition_policy_version=transition.transition_policy_version,
        )
    except (AttributeError, TypeError, ValueError):
        return False
    return (
        transition.transition_record_id == expected_id
        and transition.transition_record_id == revision.transition_record_id
        and transition.governed_knowledge_id == revision.governed_knowledge_id
    )


def construct_prompt_candidate(
    request: PromptCandidateConstructionRequest,
) -> PromptCandidateConstructionResult:
    if type(request) is not PromptCandidateConstructionRequest:
        return _rejected("invalid_request")
    if request.contract_version != (
        PROMPT_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
    ):
        return _rejected("unsupported_request_contract_version")
    if request.prompt_candidate_schema_id != PROMPT_CANDIDATE_SCHEMA_ID:
        return _rejected("unsupported_prompt_candidate_schema")
    if request.prompt_candidate_schema_version != PROMPT_CANDIDATE_SCHEMA_VERSION:
        return _rejected("unsupported_prompt_candidate_schema_version")
    if request.construction_policy_id != PROMPT_CANDIDATE_CONSTRUCTION_POLICY_ID:
        return _rejected("unsupported_construction_policy")
    if request.construction_policy_version != (
        PROMPT_CANDIDATE_CONSTRUCTION_POLICY_VERSION
    ):
        return _rejected("unsupported_construction_policy_version")

    intent_issue = _validate_prompt_intent(request.prompt_intent)
    if intent_issue is not None:
        return _rejected(intent_issue)
    prompt_intent = request.prompt_intent

    lookup = request.source_revision_lookup_result
    if type(lookup) is not KnowledgeRepositoryLookupResult:
        return _rejected("invalid_source_revision_lookup_result")
    if lookup.contract_version != KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION:
        return _rejected("unsupported_source_lookup_result_contract_version")
    if lookup.status == "not_found":
        return _rejected("source_revision_not_found")
    if lookup.status == "rejected":
        return _rejected("source_revision_lookup_rejected")
    if lookup.status != "found":
        return _rejected("invalid_source_revision_lookup_result")

    if lookup.revision is None:
        return _rejected("missing_source_revision")
    revision_issue = _validate_revision(lookup.revision)
    if revision_issue is not None:
        return _rejected(revision_issue)
    revision = lookup.revision

    governed_issue = _validate_governed(revision, lookup.governed_knowledge)
    if governed_issue is not None:
        return _rejected(governed_issue)
    governed = lookup.governed_knowledge

    lifecycle_issue = _validate_lifecycle(
        revision,
        governed,
        lookup.lifecycle_interpretation_result,
    )
    if lifecycle_issue is not None:
        return _rejected(lifecycle_issue)
    lifecycle = lookup.lifecycle_interpretation_result

    lineage_issue = _validate_lineage(revision, governed, lookup.lineage_record)
    if lineage_issue is not None:
        return _rejected(lineage_issue)
    lineage = lookup.lineage_record

    audit_issue = _validate_audit(revision, governed, lookup.audit_record)
    if audit_issue is not None:
        return _rejected(audit_issue)
    audit = lookup.audit_record

    if not _transition_matches(revision, lookup.transition_record):
        return _rejected("source_revision_identity_mismatch")

    try:
        intent_digest = derive_prompt_intent_digest(prompt_intent)
        provisional_provenance = PromptCandidateProvenance(
            contract_version=PROMPT_CANDIDATE_PROVENANCE_CONTRACT_VERSION,
            provenance_id=_ZERO_PROVENANCE_ID,
            source_lookup_result_contract_version=lookup.contract_version,
            source_revision_id=revision.revision_id,
            source_governed_knowledge_id=governed.governed_knowledge_id,
            source_revision_number=revision.revision_number,
            source_governed_knowledge_payload_digest=(
                revision.governed_knowledge_payload_digest
            ),
            source_lineage_record_id=lineage.lineage_record_id,
            source_audit_id=audit.audit_id,
            source_lifecycle_interpretation_result_id=(
                lifecycle.governed_knowledge_lifecycle_assertion_interpretation_result_id
            ),
            prompt_intent_id=prompt_intent.intent_id,
            prompt_intent_digest=intent_digest,
            prompt_candidate_schema_id=request.prompt_candidate_schema_id,
            prompt_candidate_schema_version=request.prompt_candidate_schema_version,
            construction_policy_id=request.construction_policy_id,
            construction_policy_version=request.construction_policy_version,
        )
        provenance_id = derive_prompt_candidate_provenance_id(
            provisional_provenance
        )
        provenance = PromptCandidateProvenance(
            **{
                **provisional_provenance.__dict__,
                "provenance_id": provenance_id,
            }
        )
        if derive_prompt_candidate_provenance_id(provenance) != provenance_id:
            return _rejected("provenance_identity_mismatch")

        provisional_candidate = PromptCandidate(
            contract_version=PROMPT_CANDIDATE_CONTRACT_VERSION,
            candidate_id=_ZERO_CANDIDATE_ID,
            prompt_candidate_schema_id=request.prompt_candidate_schema_id,
            prompt_candidate_schema_version=request.prompt_candidate_schema_version,
            construction_policy_id=request.construction_policy_id,
            construction_policy_version=request.construction_policy_version,
            prompt_intent=prompt_intent,
            source_revision=revision,
            governed_knowledge=governed,
            lifecycle_interpretation_result=lifecycle,
            provenance=provenance,
            candidate_payload_digest=_ZERO_DIGEST,
        )
        payload_digest = derive_prompt_candidate_payload_digest(
            provisional_candidate
        )
        identity_candidate = PromptCandidate(
            **{
                **provisional_candidate.__dict__,
                "candidate_payload_digest": payload_digest,
            }
        )
        candidate_id = derive_prompt_candidate_id(identity_candidate)
        candidate = PromptCandidate(
            **{
                **identity_candidate.__dict__,
                "candidate_id": candidate_id,
            }
        )
        if derive_prompt_candidate_payload_digest(candidate) != payload_digest:
            return _rejected("candidate_payload_digest_mismatch")
        if derive_prompt_candidate_id(candidate) != candidate_id:
            return _rejected("candidate_identity_mismatch")
        result = PromptCandidateConstructionResult(
            contract_version=(
                PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION
            ),
            status=PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED,
            prompt_candidate=candidate,
            issue=None,
        )
        result.__post_init__()
        return result
    except (TypeError, ValueError, RuntimeError):
        return _rejected("internal_contract_violation")
