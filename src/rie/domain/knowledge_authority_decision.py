"""Immutable Knowledge authority decision and deterministic identity contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from math import isfinite
import re
import unicodedata

from rie.domain.knowledge_candidate import (
    KnowledgeCandidate,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)
from rie.domain.knowledge_governance_decision import (
    KnowledgeGovernanceDecision,
    compute_knowledge_governance_decision_id,
    knowledge_governance_identity_input_from_record,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)


KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION = (
    "knowledge-authority-decision-v1"
)
KNOWLEDGE_AUTHORITY_DECISION_ID_PREFIX = "ka1_"
KNOWLEDGE_AUTHORITY_IDENTITY_POLICY_ID = (
    "rcis-knowledge-authority-decision-identity"
)
KNOWLEDGE_AUTHORITY_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_AUTHORITY_IDENTITY_CANONICALIZATION_CONTRACT = (
    "knowledge-authority-decision-json-v1"
)
KNOWLEDGE_AUTHORITY_DIGEST_ALGORITHM = "sha256"

AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY = (
    "intended_future_governed_knowledge_authority"
)

INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE = (
    "authoritative_for_governed_knowledge"
)
INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE = (
    "non_authoritative_for_governed_knowledge"
)

AUTHORITY_DECISION_OUTCOME_AUTHORIZED = "authority_value_authorized"
AUTHORITY_DECISION_OUTCOME_DENIED = "authority_value_denied"
AUTHORITY_DECISION_OUTCOME_DEFERRED = "authority_value_deferred"

KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_INFO = "info"
KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_WARNING = "warning"

_INTENDED_AUTHORITY_VALUES = frozenset(
    {
        INTENDED_AUTHORITY_VALUE_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
        INTENDED_AUTHORITY_VALUE_NON_AUTHORITATIVE_FOR_GOVERNED_KNOWLEDGE,
    }
)
_AUTHORITY_DECISION_OUTCOMES = frozenset(
    {
        AUTHORITY_DECISION_OUTCOME_AUTHORIZED,
        AUTHORITY_DECISION_OUTCOME_DENIED,
        AUTHORITY_DECISION_OUTCOME_DEFERRED,
    }
)
_DIAGNOSTIC_SEVERITIES = frozenset(
    {
        KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_INFO,
        KNOWLEDGE_AUTHORITY_DIAGNOSTIC_SEVERITY_WARNING,
    }
)
_AUTHORITY_DECISION_ID_PATTERN = re.compile(r"^ka1_[0-9a-f]{64}$")
_KNOWLEDGE_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
_KNOWLEDGE_GOVERNANCE_DECISION_ID_PATTERN = re.compile(
    r"^kg1_[0-9a-f]{64}$"
)
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_pattern(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> None:
    _require_string(value, field_name)
    if pattern.fullmatch(value) is None:
        raise ValueError(f"{field_name} has an invalid format")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_tuple(value: object, field_name: str) -> tuple[object, ...]:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")
    return value


def _require_unique_ordered_strings(
    value: object,
    field_name: str,
    *,
    pattern: re.Pattern[str] | None = None,
) -> None:
    items = _require_tuple(value, field_name)
    if not items:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(items):
        if pattern is None:
            _require_string(item, f"{field_name}[{index}]")
        else:
            _require_pattern(item, f"{field_name}[{index}]", pattern)
    if len(set(items)) != len(items):
        raise ValueError(f"{field_name} must contain unique values")
    if items != tuple(sorted(items)):
        raise ValueError(f"{field_name} must be lexicographically ordered")


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _format_decided_at(value: datetime) -> str:
    _require_aware_datetime(value, "decided_at")
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _canonicalize(value: object) -> object:
    if type(value) is str:
        return _normalize_text(value)
    if value is None or type(value) in (int, bool):
        return value
    if type(value) is float:
        if not isfinite(value):
            raise ValueError("canonical value must contain finite floats")
        return value
    if type(value) in (tuple, list):
        return [_canonicalize(item) for item in value]
    if type(value) is dict:
        projection: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("canonical mapping keys must be strings")
            projection[_normalize_text(key)] = _canonicalize(item)
        return projection
    raise ValueError("canonical value contains an unsupported type")


@dataclass(frozen=True)
class KnowledgeAuthorityDiagnostic:
    code: str
    severity: str
    message: str
    field: str
    source: str

    def __post_init__(self) -> None:
        for field_name in ("code", "severity", "message", "field", "source"):
            _require_string(getattr(self, field_name), field_name)
        if self.severity not in _DIAGNOSTIC_SEVERITIES:
            raise ValueError("severity must be info or warning")


def verify_knowledge_authority_candidate_identity(
    candidate: KnowledgeCandidate,
) -> str:
    if type(candidate) is not KnowledgeCandidate:
        raise ValueError("candidate must be an exact KnowledgeCandidate")
    expected_id = compute_knowledge_candidate_id(
        identity_input_from_knowledge_candidate(candidate)
    )
    if candidate.knowledge_candidate_id != expected_id:
        raise ValueError("knowledge_candidate_id does not match identity")
    return candidate.knowledge_candidate_id


def compute_knowledge_authority_candidate_snapshot_digest(
    candidate: KnowledgeCandidate,
) -> str:
    verify_knowledge_authority_candidate_identity(candidate)
    return compute_knowledge_candidate_review_snapshot_digest(candidate)


def verify_knowledge_authority_governance_decision_identity(
    record: KnowledgeGovernanceDecision,
) -> str:
    if type(record) is not KnowledgeGovernanceDecision:
        raise ValueError(
            "record must be an exact KnowledgeGovernanceDecision"
        )
    expected_id = compute_knowledge_governance_decision_id(
        knowledge_governance_identity_input_from_record(record)
    )
    if record.knowledge_governance_decision_id != expected_id:
        raise ValueError(
            "knowledge_governance_decision_id does not match identity"
        )
    return record.knowledge_governance_decision_id


@dataclass(frozen=True)
class KnowledgeAuthorityIdentityInput:
    authority_decision_record_contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_governance_decision_ids: tuple[str, ...]
    authority_scope: str
    intended_authority_value: str
    decision_outcome: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    authority_policy_id: str
    authority_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.authority_decision_record_contract_version
            != KNOWLEDGE_AUTHORITY_DECISION_CONTRACT_VERSION
        ):
            raise ValueError(
                "unsupported authority_decision_record_contract_version"
            )
        _require_pattern(
            self.knowledge_candidate_id,
            "knowledge_candidate_id",
            _KNOWLEDGE_CANDIDATE_ID_PATTERN,
        )
        _require_string(
            self.knowledge_candidate_contract_version,
            "knowledge_candidate_contract_version",
        )
        _require_pattern(
            self.knowledge_candidate_snapshot_digest,
            "knowledge_candidate_snapshot_digest",
            _DIGEST_PATTERN,
        )
        _require_unique_ordered_strings(
            self.knowledge_governance_decision_ids,
            "knowledge_governance_decision_ids",
            pattern=_KNOWLEDGE_GOVERNANCE_DECISION_ID_PATTERN,
        )
        if (
            self.authority_scope
            != AUTHORITY_SCOPE_INTENDED_FUTURE_GOVERNED_KNOWLEDGE_AUTHORITY
        ):
            raise ValueError("unsupported authority_scope")
        if self.intended_authority_value not in _INTENDED_AUTHORITY_VALUES:
            raise ValueError("unsupported intended_authority_value")
        if self.decision_outcome not in _AUTHORITY_DECISION_OUTCOMES:
            raise ValueError("unsupported decision_outcome")
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        for field_name in (
            "decided_by",
            "authority_policy_id",
            "authority_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_aware_datetime(self.decided_at, "decided_at")


def canonical_knowledge_authority_identity_projection(
    identity_input: KnowledgeAuthorityIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgeAuthorityIdentityInput:
        raise ValueError(
            "identity_input must be an exact KnowledgeAuthorityIdentityInput"
        )
    return _canonicalize(
        {
            "authority_decision_record_contract_version": (
                identity_input.authority_decision_record_contract_version
            ),
            "authority_policy_id": identity_input.authority_policy_id,
            "authority_policy_version": identity_input.authority_policy_version,
            "authority_scope": identity_input.authority_scope,
            "decided_at": _format_decided_at(identity_input.decided_at),
            "decided_by": identity_input.decided_by,
            "decision_outcome": identity_input.decision_outcome,
            "identity_canonicalization_contract": (
                KNOWLEDGE_AUTHORITY_IDENTITY_CANONICALIZATION_CONTRACT
            ),
            "intended_authority_value": (
                identity_input.intended_authority_value
            ),
            "knowledge_candidate_contract_version": (
                identity_input.knowledge_candidate_contract_version
            ),
            "knowledge_candidate_id": identity_input.knowledge_candidate_id,
            "knowledge_candidate_snapshot_digest": (
                identity_input.knowledge_candidate_snapshot_digest
            ),
            "knowledge_governance_decision_ids": (
                identity_input.knowledge_governance_decision_ids
            ),
            "reason_codes": identity_input.reason_codes,
        }
    )


def canonical_knowledge_authority_identity_bytes(
    identity_input: KnowledgeAuthorityIdentityInput,
) -> bytes:
    projection = canonical_knowledge_authority_identity_projection(
        identity_input
    )
    return json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_authority_decision_id(
    identity_input: KnowledgeAuthorityIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_authority_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_AUTHORITY_DECISION_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgeAuthorityDecision:
    knowledge_authority_decision_id: str
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_governance_decision_ids: tuple[str, ...]
    authority_scope: str
    intended_authority_value: str
    decision_outcome: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    authority_policy_id: str
    authority_policy_version: str
    diagnostics: tuple[KnowledgeAuthorityDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.knowledge_authority_decision_id,
            "knowledge_authority_decision_id",
            _AUTHORITY_DECISION_ID_PATTERN,
        )
        identity_input = KnowledgeAuthorityIdentityInput(
            authority_decision_record_contract_version=self.contract_version,
            knowledge_candidate_id=self.knowledge_candidate_id,
            knowledge_candidate_contract_version=(
                self.knowledge_candidate_contract_version
            ),
            knowledge_candidate_snapshot_digest=(
                self.knowledge_candidate_snapshot_digest
            ),
            knowledge_governance_decision_ids=(
                self.knowledge_governance_decision_ids
            ),
            authority_scope=self.authority_scope,
            intended_authority_value=self.intended_authority_value,
            decision_outcome=self.decision_outcome,
            reason_codes=self.reason_codes,
            decided_by=self.decided_by,
            decided_at=self.decided_at,
            authority_policy_id=self.authority_policy_id,
            authority_policy_version=self.authority_policy_version,
        )
        diagnostics = _require_tuple(self.diagnostics, "diagnostics")
        for index, diagnostic in enumerate(diagnostics):
            if type(diagnostic) is not KnowledgeAuthorityDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact "
                    "KnowledgeAuthorityDiagnostic"
                )
        if (
            self.knowledge_authority_decision_id
            != compute_knowledge_authority_decision_id(identity_input)
        ):
            raise ValueError(
                "knowledge_authority_decision_id does not match identity"
            )


def knowledge_authority_identity_input_from_record(
    record: KnowledgeAuthorityDecision,
) -> KnowledgeAuthorityIdentityInput:
    if type(record) is not KnowledgeAuthorityDecision:
        raise ValueError(
            "record must be an exact KnowledgeAuthorityDecision"
        )
    return KnowledgeAuthorityIdentityInput(
        authority_decision_record_contract_version=record.contract_version,
        knowledge_candidate_id=record.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            record.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            record.knowledge_candidate_snapshot_digest
        ),
        knowledge_governance_decision_ids=(
            record.knowledge_governance_decision_ids
        ),
        authority_scope=record.authority_scope,
        intended_authority_value=record.intended_authority_value,
        decision_outcome=record.decision_outcome,
        reason_codes=record.reason_codes,
        decided_by=record.decided_by,
        decided_at=record.decided_at,
        authority_policy_id=record.authority_policy_id,
        authority_policy_version=record.authority_policy_version,
    )
