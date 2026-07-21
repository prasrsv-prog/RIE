import ast
from pathlib import Path

import rie.knowledge_repository as package

EXPECTED = {
    "KnowledgeRepositoryInitialWriteRequest",
    "KnowledgeRepositoryLifecycleTransitionRequest",
    "KnowledgeRepositoryLineageRecord",
    "KnowledgeRepositoryRevision",
    "KnowledgeRepositoryLifecycleTransitionRecord",
    "KnowledgeRepositoryAuditRecord",
    "KnowledgeRepositoryWriteResult",
    "KnowledgeRepositoryLookupResult",
    "KnowledgeRepositoryHistoryResult",
    "KnowledgeRepositoryIssue",
    "GovernedKnowledgeRepository",
    "SqliteGovernedKnowledgeRepository",
    "serialize_governed_knowledge_repository_payload",
    "deserialize_governed_knowledge_repository_payload",
    "calculate_governed_knowledge_repository_payload_digest",
    "calculate_knowledge_repository_lineage_record_id",
    "calculate_knowledge_repository_lifecycle_transition_record_id",
    "calculate_knowledge_repository_revision_id",
    "calculate_knowledge_repository_audit_id",
    "KNOWLEDGE_REPOSITORY_INITIAL_WRITE_REQUEST_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_REQUEST_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_LINEAGE_RECORD_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_REVISION_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_RECORD_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_WRITE_RESULT_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_HISTORY_RESULT_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_ISSUE_CONTRACT_VERSION",
    "KNOWLEDGE_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION",
    "KNOWLEDGE_REPOSITORY_LINEAGE_IDENTITY_CANONICALIZATION_VERSION",
    "KNOWLEDGE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION",
    "KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_IDENTITY_CANONICALIZATION_VERSION",
    "KNOWLEDGE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION",
    "KNOWLEDGE_REPOSITORY_POLICY_ID",
    "KNOWLEDGE_REPOSITORY_POLICY_VERSION",
    "KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_ID",
    "KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_POLICY_VERSION",
    "KNOWLEDGE_REPOSITORY_DIGEST_ALGORITHM",
    "KNOWLEDGE_REPOSITORY_LINEAGE_ID_PREFIX",
    "KNOWLEDGE_REPOSITORY_REVISION_ID_PREFIX",
    "KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_ID_PREFIX",
    "KNOWLEDGE_REPOSITORY_AUDIT_ID_PREFIX",
    "KNOWLEDGE_REPOSITORY_WRITE_STATUSES",
    "KNOWLEDGE_REPOSITORY_LOOKUP_STATUSES",
    "KNOWLEDGE_REPOSITORY_ISSUE_CODES",
    "SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_ID",
    "SQLITE_GOVERNED_KNOWLEDGE_REPOSITORY_SCHEMA_VERSION",
}
FORBIDDEN = {
    "construct_knowledge_from_persisted_evidence",
    "construct_knowledge_candidate",
    "construct_governed_knowledge",
    "decide_governed_knowledge_acceptance",
    "interpret_governed_knowledge_lifecycle_assertion_premise_structurally",
    "govern_knowledge_candidate",
    "decide_knowledge_authority",
    "assess_knowledge_candidate_conflict",
    "decide_knowledge_promotion",
    "record_knowledge_promotion_execution",
}


def test_exact_public_api() -> None:
    assert len(EXPECTED) == 48
    assert set(package.__all__) == EXPECTED
    assert len(package.__all__) == 48
    for name in EXPECTED:
        assert hasattr(package, name)


def test_production_ast_has_no_forbidden_workflow_calls() -> None:
    package_root = Path(package.__file__).parent
    for path in package_root.glob("*.py"):
        tree = ast.parse(
            path.read_text(encoding="ascii"),
            filename=str(path),
        )
        names = {
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
        }
        attributes = {
            node.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
        }
        imported = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(
                node,
                (ast.Import, ast.ImportFrom),
            )
            for alias in node.names
        }
        assert not FORBIDDEN.intersection(
            names | attributes | imported
        )
