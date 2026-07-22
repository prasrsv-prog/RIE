from dataclasses import replace
from pathlib import Path

from rie.knowledge_repository import SqliteGovernedKnowledgeRepository
from rie.prompt_candidate import (
    PROMPT_CANDIDATE_CONSTRUCTION_POLICY_ID,
    PROMPT_CANDIDATE_CONSTRUCTION_POLICY_VERSION,
    PROMPT_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION,
    PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED,
    PROMPT_CANDIDATE_SCHEMA_ID,
    PROMPT_CANDIDATE_SCHEMA_VERSION,
    PROMPT_INTENT_CONTRACT_VERSION,
    PromptCandidateConstructionRequest,
    PromptIntent,
    construct_prompt_candidate,
    derive_prompt_candidate_id,
    derive_prompt_candidate_payload_digest,
    derive_prompt_candidate_provenance_id,
    derive_prompt_intent_digest,
    derive_prompt_intent_id,
)
from test_sqlite_governed_knowledge_repository import build_fixture_bundle


def build_valid_lookup(tmp_path: Path):
    bundle = build_fixture_bundle()
    repository = SqliteGovernedKnowledgeRepository(tmp_path / "knowledge.sqlite3")
    initial = repository.persist_initial(bundle["initial_request"])
    assert initial.status == "persisted_initial"
    lookup = repository.get_by_revision_id(initial.revision.revision_id)
    assert lookup.status == "found"
    return lookup


def build_valid_intent() -> PromptIntent:
    provisional = PromptIntent(
        contract_version=PROMPT_INTENT_CONTRACT_VERSION,
        intent_id="pi1_" + "0" * 64,
        objective="Create an exact structural product brief.",
        audience="creative team",
        language="en",
        output_format="structured brief",
        required_constraints=(
            "preserve source identity",
            "preserve source facts",
        ),
        forbidden_constraints=(
            "invoke a model",
            "invent unsupported facts",
        ),
    )
    return replace(provisional, intent_id=derive_prompt_intent_id(provisional))


def build_request(tmp_path: Path) -> PromptCandidateConstructionRequest:
    return PromptCandidateConstructionRequest(
        contract_version=(
            PROMPT_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
        ),
        source_revision_lookup_result=build_valid_lookup(tmp_path),
        prompt_intent=build_valid_intent(),
        prompt_candidate_schema_id=PROMPT_CANDIDATE_SCHEMA_ID,
        prompt_candidate_schema_version=PROMPT_CANDIDATE_SCHEMA_VERSION,
        construction_policy_id=PROMPT_CANDIDATE_CONSTRUCTION_POLICY_ID,
        construction_policy_version=(
            PROMPT_CANDIDATE_CONSTRUCTION_POLICY_VERSION
        ),
    )


def test_constructed_result_is_deterministic_and_traceable(
    tmp_path: Path,
) -> None:
    request = build_request(tmp_path)
    first = construct_prompt_candidate(request)
    second = construct_prompt_candidate(request)
    assert first == second
    assert first.status == PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED
    candidate = first.prompt_candidate
    assert candidate.source_revision == request.source_revision_lookup_result.revision
    assert candidate.governed_knowledge == (
        request.source_revision_lookup_result.governed_knowledge
    )
    assert candidate.prompt_intent == request.prompt_intent
    assert candidate.provenance.source_revision_id == candidate.source_revision.revision_id
    assert candidate.provenance.prompt_intent_digest == derive_prompt_intent_digest(
        request.prompt_intent
    )
    assert candidate.provenance.provenance_id == (
        derive_prompt_candidate_provenance_id(candidate.provenance)
    )
    assert candidate.candidate_payload_digest == (
        derive_prompt_candidate_payload_digest(candidate)
    )
    assert candidate.candidate_id == derive_prompt_candidate_id(candidate)


def test_validation_stops_at_first_failure(tmp_path: Path) -> None:
    request = build_request(tmp_path)
    result = construct_prompt_candidate(
        replace(
            request,
            contract_version="unsupported",
            prompt_candidate_schema_id="unsupported",
        )
    )
    assert result.issue.code == "unsupported_request_contract_version"

    result = construct_prompt_candidate(
        replace(request, prompt_candidate_schema_id="unsupported")
    )
    assert result.issue.code == "unsupported_prompt_candidate_schema"

    invalid_intent = replace(request.prompt_intent, intent_id="pi1_" + "f" * 64)
    result = construct_prompt_candidate(replace(request, prompt_intent=invalid_intent))
    assert result.issue.code == "prompt_intent_id_mismatch"


def test_source_lookup_and_revision_fail_closed(tmp_path: Path) -> None:
    request = build_request(tmp_path)
    missing = SqliteGovernedKnowledgeRepository(
        tmp_path / "missing.sqlite3"
    ).get_by_revision_id("gkr1_" + "0" * 64)
    result = construct_prompt_candidate(
        replace(request, source_revision_lookup_result=missing)
    )
    assert result.issue.code == "source_revision_not_found"

    lookup = request.source_revision_lookup_result
    invalid_revision = replace(
        lookup.revision,
        revision_id="gkr1_" + "f" * 64,
    )
    result = construct_prompt_candidate(
        replace(
            request,
            source_revision_lookup_result=replace(
                lookup,
                revision=invalid_revision,
            ),
        )
    )
    assert result.issue.code == "source_revision_identity_mismatch"
