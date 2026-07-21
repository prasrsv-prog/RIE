from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from rie.knowledge_repository import (
    KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_ISSUE_CODES,
    KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_LOOKUP_STATUSES,
    KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION,
    KNOWLEDGE_REPOSITORY_WRITE_STATUSES,
    KnowledgeRepositoryAuditRecord,
    KnowledgeRepositoryIssue,
    KnowledgeRepositoryLineageRecord,
    KnowledgeRepositoryLookupResult,
    KnowledgeRepositoryRevision,
)

NOW = datetime(2026, 7, 21, 8, 0, tzinfo=timezone.utc)


def test_frozen_contract_shapes_and_statuses() -> None:
    assert len(KNOWLEDGE_REPOSITORY_ISSUE_CODES) == 34
    assert KNOWLEDGE_REPOSITORY_WRITE_STATUSES == (
        "persisted_initial",
        "appended_lifecycle_transition",
        "unchanged_exact_replay",
        "rejected",
    )
    assert KNOWLEDGE_REPOSITORY_LOOKUP_STATUSES == (
        "found",
        "not_found",
        "rejected",
    )
    lineage = KnowledgeRepositoryLineageRecord(
        contract_version=(
            KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION
        ),
        lineage_record_id="gkrl1_" + "1" * 64,
        governed_knowledge_id="gk1_" + "2" * 64,
        governed_knowledge_contract_version=(
            "governed-knowledge-v1"
        ),
        knowledge_candidate_id="kc1_" + "3" * 64,
        knowledge_candidate_contract_version=(
            "knowledge-candidate-v1"
        ),
        knowledge_candidate_snapshot_digest="4" * 64,
        persisted_evidence_knowledge_compatibility_record_id=(
            "pekc1_" + "5" * 64
        ),
        evidence_repository_revision_id=(
            "evr1_" + "6" * 64
        ),
        evidence_repository_audit_id=(
            "eva1_" + "7" * 64
        ),
        source_id="source-1",
        source_revision_number=1,
        traceable_evidence_id="ev1_" + "8" * 64,
        accepted_evidence_id="ev1_" + "9" * 64,
        acceptance_record_ids=("ar1_" + "a" * 64,),
        construction_rule_id="rcis-accepted-text-verbatim",
        construction_rule_version="1.0.0",
        governed_knowledge_construction_policy_id=(
            "rcis-governed-knowledge-construction"
        ),
        governed_knowledge_construction_policy_version=(
            "1.0.0"
        ),
        lineage_policy_id=(
            "rcis-governed-knowledge-repository"
        ),
        lineage_policy_version="1.0.0",
    )
    revision = KnowledgeRepositoryRevision(
        contract_version=(
            KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION
        ),
        revision_id="gkr1_" + "b" * 64,
        governed_knowledge_id=(
            lineage.governed_knowledge_id
        ),
        revision_number=1,
        previous_revision_id=None,
        governed_knowledge_payload_digest="c" * 64,
        lineage_record_id=lineage.lineage_record_id,
        lifecycle_interpretation_result_id=(
            "gklair1_" + "d" * 64
        ),
        lifecycle_interpretation_result_contract_version=(
            "governed-knowledge-lifecycle-assertion-"
            "interpretation-result-v1"
        ),
        lifecycle_interpretation_result_payload_digest=(
            "e" * 64
        ),
        transition_record_id=None,
        actor_id="tester",
        recorded_at_utc=NOW,
        audit_id="gkra1_" + "f" * 64,
    )
    audit = KnowledgeRepositoryAuditRecord(
        contract_version=(
            KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION
        ),
        audit_id=revision.audit_id,
        action="persist_initial_governed_knowledge",
        revision_id=revision.revision_id,
        governed_knowledge_id=(
            revision.governed_knowledge_id
        ),
        revision_number=1,
        lineage_record_id=lineage.lineage_record_id,
        transition_record_id=None,
        actor_id="tester",
        recorded_at_utc=NOW,
    )
    with pytest.raises(FrozenInstanceError):
        revision.revision_number = 2

    issue = KnowledgeRepositoryIssue(
        code="invalid_request",
        message="Invalid request.",
    )
    rejected = KnowledgeRepositoryLookupResult(
        contract_version=(
            KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION
        ),
        status="rejected",
        revision=None,
        lineage_record=None,
        transition_record=None,
        audit_record=None,
        governed_knowledge=None,
        lifecycle_interpretation_result=None,
        issue=issue,
    )
    assert rejected.issue == issue
    assert audit.revision_id == revision.revision_id


def test_contract_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        KnowledgeRepositoryIssue(
            code="unknown",
            message="bad",
        )
