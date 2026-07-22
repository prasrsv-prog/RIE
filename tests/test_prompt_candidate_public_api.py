import inspect
import re
from pathlib import Path

import rie.prompt_candidate as prompt_candidate


EXPECTED_PUBLIC_API = (
    "PromptCandidateConstructionRequest",
    "PromptIntent",
    "PromptCandidateProvenance",
    "PromptCandidate",
    "PromptCandidateConstructionResult",
    "PromptCandidateIssue",
    "canonicalize_prompt_intent_identity",
    "derive_prompt_intent_digest",
    "derive_prompt_intent_id",
    "canonicalize_prompt_candidate_provenance_identity",
    "derive_prompt_candidate_provenance_id",
    "canonicalize_prompt_candidate_payload",
    "derive_prompt_candidate_payload_digest",
    "canonicalize_prompt_candidate_identity",
    "derive_prompt_candidate_id",
    "construct_prompt_candidate",
    "PROMPT_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION",
    "PROMPT_INTENT_CONTRACT_VERSION",
    "PROMPT_CANDIDATE_PROVENANCE_CONTRACT_VERSION",
    "PROMPT_CANDIDATE_CONTRACT_VERSION",
    "PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION",
    "PROMPT_CANDIDATE_ISSUE_CONTRACT_VERSION",
    "PROMPT_CANDIDATE_SCHEMA_ID",
    "PROMPT_CANDIDATE_SCHEMA_VERSION",
    "PROMPT_CANDIDATE_CONSTRUCTION_POLICY_ID",
    "PROMPT_CANDIDATE_CONSTRUCTION_POLICY_VERSION",
    "PROMPT_CANDIDATE_DIGEST_ALGORITHM",
    "PROMPT_INTENT_IDENTITY_CANONICALIZATION_VERSION",
    "PROMPT_CANDIDATE_PROVENANCE_IDENTITY_CANONICALIZATION_VERSION",
    "PROMPT_CANDIDATE_PAYLOAD_CANONICALIZATION_VERSION",
    "PROMPT_CANDIDATE_IDENTITY_CANONICALIZATION_VERSION",
    "PROMPT_INTENT_ID_PREFIX",
    "PROMPT_CANDIDATE_PROVENANCE_ID_PREFIX",
    "PROMPT_CANDIDATE_ID_PREFIX",
    "PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED",
    "PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED",
    "PROMPT_CANDIDATE_ISSUE_CODES",
)

FORBIDDEN_PRODUCTION_NAMES = (
    "GovernedKnowledgeRepository",
    "SqliteGovernedKnowledgeRepository",
    "persist_initial",
    "append_lifecycle_transition",
    "get_by_revision_id",
    "get_by_governed_knowledge_revision",
    "list_governed_knowledge_history",
    "construct_knowledge_from_persisted_evidence",
    "construct_knowledge_candidate",
    "construct_governed_knowledge",
    "decide_governed_knowledge_acceptance",
    "govern_knowledge_candidate",
    "assess_knowledge_candidate_conflict",
    "decide_knowledge_authority",
    "evaluate_knowledge_promotion_prerequisite",
    "decide_knowledge_promotion",
    "record_knowledge_promotion_execution",
    "interpret_governed_knowledge_lifecycle_assertion_premise_structurally",
    "sqlite3",
    "requests",
    "urllib",
    "socket",
    "subprocess",
    "pathlib",
    "os",
    "time",
    "random",
    "uuid",
    "logging",
)


def test_exact_public_api_and_callable_signature() -> None:
    assert prompt_candidate.__all__ == EXPECTED_PUBLIC_API
    assert len(prompt_candidate.__all__) == 37
    assert len(set(prompt_candidate.__all__)) == 37
    for name in EXPECTED_PUBLIC_API:
        assert hasattr(prompt_candidate, name)
    signature = inspect.signature(prompt_candidate.construct_prompt_candidate)
    assert tuple(signature.parameters) == ("request",)
    assert signature.return_annotation == "PromptCandidateConstructionResult"


def test_production_sources_contain_no_forbidden_names() -> None:
    root = Path(__file__).resolve().parents[1]
    production = root / "src" / "rie" / "prompt_candidate"
    sources = tuple(sorted(production.glob("*.py")))
    assert len(sources) == 4
    for path in sources:
        text = path.read_text(encoding="utf-8")
        for name in FORBIDDEN_PRODUCTION_NAMES:
            pattern = rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])"
            assert re.search(pattern, text) is None, (path, name)
