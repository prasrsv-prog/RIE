from rie.prompt_candidate import (
    canonicalize_prompt_candidate_identity,
    canonicalize_prompt_candidate_payload,
    canonicalize_prompt_candidate_provenance_identity,
    canonicalize_prompt_intent_identity,
    construct_prompt_candidate,
    derive_prompt_candidate_id,
    derive_prompt_candidate_payload_digest,
    derive_prompt_candidate_provenance_id,
    derive_prompt_intent_digest,
    derive_prompt_intent_id,
)
from test_prompt_candidate_service import build_request


def test_canonical_intent_bytes_are_exact_and_deterministic(tmp_path) -> None:
    intent = build_request(tmp_path).prompt_intent
    first = canonicalize_prompt_intent_identity(intent)
    second = canonicalize_prompt_intent_identity(intent)
    assert first == second
    assert first.startswith(b'{"canonicalization_version"')
    assert not first.endswith(b"\n")
    assert derive_prompt_intent_digest(intent) == derive_prompt_intent_digest(intent)
    assert intent.intent_id == derive_prompt_intent_id(intent)


def test_candidate_canonical_graph_is_non_cyclic(tmp_path) -> None:
    result = construct_prompt_candidate(build_request(tmp_path))
    candidate = result.prompt_candidate
    provenance_bytes = canonicalize_prompt_candidate_provenance_identity(
        candidate.provenance
    )
    payload_bytes = canonicalize_prompt_candidate_payload(candidate)
    identity_bytes = canonicalize_prompt_candidate_identity(candidate)
    assert provenance_bytes != payload_bytes
    assert payload_bytes != identity_bytes
    assert candidate.provenance.provenance_id == (
        derive_prompt_candidate_provenance_id(candidate.provenance)
    )
    assert candidate.candidate_payload_digest == (
        derive_prompt_candidate_payload_digest(candidate)
    )
    assert candidate.candidate_id == derive_prompt_candidate_id(candidate)


def test_non_ascii_is_escaped_with_preserved_intent_order(tmp_path) -> None:
    request = build_request(tmp_path)
    intent = request.prompt_intent
    object.__setattr__(intent, "objective", "Caf\u00e9 \U0001f680")
    object.__setattr__(intent, "intent_id", derive_prompt_intent_id(intent))
    payload = canonicalize_prompt_intent_identity(intent)
    assert b"\\u00e9" in payload
    assert b"\\ud83d\\ude80" in payload
