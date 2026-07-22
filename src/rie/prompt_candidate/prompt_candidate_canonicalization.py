from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
import hashlib
import json
from typing import Final

from .prompt_candidate_contract import (
    PROMPT_CANDIDATE_DIGEST_ALGORITHM,
    PROMPT_CANDIDATE_ID_PREFIX,
    PROMPT_CANDIDATE_IDENTITY_CANONICALIZATION_VERSION,
    PROMPT_CANDIDATE_PAYLOAD_CANONICALIZATION_VERSION,
    PROMPT_CANDIDATE_PROVENANCE_ID_PREFIX,
    PROMPT_CANDIDATE_PROVENANCE_IDENTITY_CANONICALIZATION_VERSION,
    PROMPT_INTENT_ID_PREFIX,
    PROMPT_INTENT_IDENTITY_CANONICALIZATION_VERSION,
    PromptCandidate,
    PromptCandidateProvenance,
    PromptIntent,
)

_PLACEHOLDER_DIGEST: Final = "0" * 64


def _format_datetime(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _encode(value: object) -> object:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            "__dataclass__": (
                value.__class__.__module__ + ":" + value.__class__.__qualname__
            ),
            "fields": {
                field.name: _encode(getattr(value, field.name))
                for field in dataclasses.fields(value)
            },
        }
    if type(value) is datetime:
        return {"__datetime__": _format_datetime(value)}
    if type(value) is tuple:
        return {"__tuple__": [_encode(item) for item in value]}
    if type(value) is list:
        return [_encode(item) for item in value]
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is float:
        raise TypeError("floating-point values are not canonical")
    if type(value) in (bytes, bytearray, set, frozenset, dict):
        raise TypeError("unsupported canonical value shape")
    raise TypeError(f"unsupported canonical value type: {type(value)!r}")


def _validate_internal(value: object) -> None:
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise TypeError("canonical object keys must be exact strings")
            _validate_internal(item)
        return
    if type(value) is list:
        for item in value:
            _validate_internal(item)
        return
    if value is None or type(value) in (str, int, bool):
        return
    raise TypeError("unsupported internal canonical value")


def _canonical_json_bytes(value: dict[str, object]) -> bytes:
    _validate_internal(value)
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _digest(payload: bytes) -> str:
    if PROMPT_CANDIDATE_DIGEST_ALGORITHM != "sha256":
        raise RuntimeError("unsupported prompt candidate digest algorithm")
    return hashlib.sha256(payload).hexdigest()


def canonicalize_prompt_intent_identity(prompt_intent: PromptIntent) -> bytes:
    if type(prompt_intent) is not PromptIntent:
        raise TypeError("prompt_intent must be an exact PromptIntent")
    prompt_intent.__post_init__()
    return _canonical_json_bytes(
        {
            "canonicalization_version": (
                PROMPT_INTENT_IDENTITY_CANONICALIZATION_VERSION
            ),
            "identity": {
                "contract_version": prompt_intent.contract_version,
                "objective": prompt_intent.objective,
                "audience": prompt_intent.audience,
                "language": prompt_intent.language,
                "output_format": prompt_intent.output_format,
                "required_constraints": _encode(
                    prompt_intent.required_constraints
                ),
                "forbidden_constraints": _encode(
                    prompt_intent.forbidden_constraints
                ),
            },
        }
    )


def derive_prompt_intent_digest(prompt_intent: PromptIntent) -> str:
    return _digest(canonicalize_prompt_intent_identity(prompt_intent))


def derive_prompt_intent_id(prompt_intent: PromptIntent) -> str:
    return PROMPT_INTENT_ID_PREFIX + derive_prompt_intent_digest(prompt_intent)


def canonicalize_prompt_candidate_provenance_identity(
    provenance: PromptCandidateProvenance,
) -> bytes:
    if type(provenance) is not PromptCandidateProvenance:
        raise TypeError("provenance must be an exact PromptCandidateProvenance")
    provenance.__post_init__()
    return _canonical_json_bytes(
        {
            "canonicalization_version": (
                PROMPT_CANDIDATE_PROVENANCE_IDENTITY_CANONICALIZATION_VERSION
            ),
            "identity": {
                field.name: _encode(getattr(provenance, field.name))
                for field in dataclasses.fields(provenance)
                if field.name != "provenance_id"
            },
        }
    )


def derive_prompt_candidate_provenance_id(
    provenance: PromptCandidateProvenance,
) -> str:
    return PROMPT_CANDIDATE_PROVENANCE_ID_PREFIX + _digest(
        canonicalize_prompt_candidate_provenance_identity(provenance)
    )


def canonicalize_prompt_candidate_payload(candidate: PromptCandidate) -> bytes:
    if type(candidate) is not PromptCandidate:
        raise TypeError("candidate must be an exact PromptCandidate")
    candidate.__post_init__()
    return _canonical_json_bytes(
        {
            "canonicalization_version": (
                PROMPT_CANDIDATE_PAYLOAD_CANONICALIZATION_VERSION
            ),
            "payload": {
                "contract_version": candidate.contract_version,
                "prompt_candidate_schema_id": (
                    candidate.prompt_candidate_schema_id
                ),
                "prompt_candidate_schema_version": (
                    candidate.prompt_candidate_schema_version
                ),
                "construction_policy_id": candidate.construction_policy_id,
                "construction_policy_version": (
                    candidate.construction_policy_version
                ),
                "prompt_intent": _encode(candidate.prompt_intent),
                "source_revision": _encode(candidate.source_revision),
                "governed_knowledge": _encode(candidate.governed_knowledge),
                "lifecycle_interpretation_result": _encode(
                    candidate.lifecycle_interpretation_result
                ),
                "provenance": _encode(candidate.provenance),
            },
        }
    )


def derive_prompt_candidate_payload_digest(candidate: PromptCandidate) -> str:
    return _digest(canonicalize_prompt_candidate_payload(candidate))


def canonicalize_prompt_candidate_identity(candidate: PromptCandidate) -> bytes:
    if type(candidate) is not PromptCandidate:
        raise TypeError("candidate must be an exact PromptCandidate")
    candidate.__post_init__()
    return _canonical_json_bytes(
        {
            "canonicalization_version": (
                PROMPT_CANDIDATE_IDENTITY_CANONICALIZATION_VERSION
            ),
            "identity": {
                "contract_version": candidate.contract_version,
                "prompt_candidate_schema_id": (
                    candidate.prompt_candidate_schema_id
                ),
                "prompt_candidate_schema_version": (
                    candidate.prompt_candidate_schema_version
                ),
                "construction_policy_id": candidate.construction_policy_id,
                "construction_policy_version": (
                    candidate.construction_policy_version
                ),
                "source_revision_id": candidate.source_revision.revision_id,
                "prompt_intent_id": candidate.prompt_intent.intent_id,
                "provenance_id": candidate.provenance.provenance_id,
                "candidate_payload_digest": candidate.candidate_payload_digest,
            },
        }
    )


def derive_prompt_candidate_id(candidate: PromptCandidate) -> str:
    return PROMPT_CANDIDATE_ID_PREFIX + _digest(
        canonicalize_prompt_candidate_identity(candidate)
    )
