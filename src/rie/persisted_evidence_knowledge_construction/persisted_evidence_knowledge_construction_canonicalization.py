"""Deterministic Gate 8 compatibility identity canonicalization."""

from __future__ import annotations

import hashlib as _hashlib
import json as _json

from .persisted_evidence_knowledge_construction_contract import (
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_ID_PREFIX as _ID_PREFIX,
    _validate_compatibility_identity_values,
)


_IDENTITY_FIELD_ORDER = (
    "contract_version",
    "repository_revision_id",
    "source_id",
    "revision_number",
    "previous_revision_id",
    "collection_id",
    "collection_payload_digest",
    "repository_audit_id",
    "traceable_evidence_id",
    "accepted_evidence_id",
    "acceptance_record_ids",
    "construction_rule_id",
    "construction_rule_version",
    "compatibility_policy_id",
    "compatibility_policy_version",
)


def canonicalize_persisted_evidence_knowledge_compatibility_identity(
    *,
    contract_version: str,
    repository_revision_id: str,
    source_id: str,
    revision_number: int,
    previous_revision_id: str | None,
    collection_id: str,
    collection_payload_digest: str,
    repository_audit_id: str,
    traceable_evidence_id: str,
    accepted_evidence_id: str,
    acceptance_record_ids: tuple[str, ...],
    construction_rule_id: str,
    construction_rule_version: str,
    compatibility_policy_id: str,
    compatibility_policy_version: str,
) -> bytes:
    if type(acceptance_record_ids) is not tuple:
        raise ValueError("acceptance_record_ids must be an exact tuple")
    normalized_ids = tuple(sorted(acceptance_record_ids))
    _validate_compatibility_identity_values(
        contract_version=contract_version,
        repository_revision_id=repository_revision_id,
        source_id=source_id,
        revision_number=revision_number,
        previous_revision_id=previous_revision_id,
        collection_id=collection_id,
        collection_payload_digest=collection_payload_digest,
        repository_audit_id=repository_audit_id,
        traceable_evidence_id=traceable_evidence_id,
        accepted_evidence_id=accepted_evidence_id,
        acceptance_record_ids=normalized_ids,
        construction_rule_id=construction_rule_id,
        construction_rule_version=construction_rule_version,
        compatibility_policy_id=compatibility_policy_id,
        compatibility_policy_version=compatibility_policy_version,
        require_sorted_acceptance_record_ids=True,
        require_supported_values=True,
    )
    value = {
        "contract_version": contract_version,
        "repository_revision_id": repository_revision_id,
        "source_id": source_id,
        "revision_number": revision_number,
        "previous_revision_id": previous_revision_id,
        "collection_id": collection_id,
        "collection_payload_digest": collection_payload_digest,
        "repository_audit_id": repository_audit_id,
        "traceable_evidence_id": traceable_evidence_id,
        "accepted_evidence_id": accepted_evidence_id,
        "acceptance_record_ids": normalized_ids,
        "construction_rule_id": construction_rule_id,
        "construction_rule_version": construction_rule_version,
        "compatibility_policy_id": compatibility_policy_id,
        "compatibility_policy_version": compatibility_policy_version,
    }
    if tuple(value) != _IDENTITY_FIELD_ORDER:
        raise RuntimeError("compatibility identity field order mismatch")
    return _json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def derive_persisted_evidence_knowledge_compatibility_record_id(
    *,
    contract_version: str,
    repository_revision_id: str,
    source_id: str,
    revision_number: int,
    previous_revision_id: str | None,
    collection_id: str,
    collection_payload_digest: str,
    repository_audit_id: str,
    traceable_evidence_id: str,
    accepted_evidence_id: str,
    acceptance_record_ids: tuple[str, ...],
    construction_rule_id: str,
    construction_rule_version: str,
    compatibility_policy_id: str,
    compatibility_policy_version: str,
) -> str:
    canonical_bytes = (
        canonicalize_persisted_evidence_knowledge_compatibility_identity(
            contract_version=contract_version,
            repository_revision_id=repository_revision_id,
            source_id=source_id,
            revision_number=revision_number,
            previous_revision_id=previous_revision_id,
            collection_id=collection_id,
            collection_payload_digest=collection_payload_digest,
            repository_audit_id=repository_audit_id,
            traceable_evidence_id=traceable_evidence_id,
            accepted_evidence_id=accepted_evidence_id,
            acceptance_record_ids=acceptance_record_ids,
            construction_rule_id=construction_rule_id,
            construction_rule_version=construction_rule_version,
            compatibility_policy_id=compatibility_policy_id,
            compatibility_policy_version=compatibility_policy_version,
        )
    )
    return _ID_PREFIX + _hashlib.sha256(canonical_bytes).hexdigest()
