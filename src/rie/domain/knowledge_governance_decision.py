"""Immutable Knowledge governance decision and deterministic identity contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from math import isfinite
import re
import unicodedata

from rie.domain.knowledge_candidate import KnowledgeCandidate
from rie.domain.knowledge_review_record import (
    KnowledgeReviewRecord,
    compute_knowledge_candidate_review_snapshot_digest,
    compute_knowledge_review_record_id,
    knowledge_review_identity_input_from_record,
)


KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION = (
    "knowledge-governance-decision-v1"
)
KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_ID = (
    "rcis-knowledge-governance-decision-identity"
)
KNOWLEDGE_GOVERNANCE_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_GOVERNANCE_IDENTITY_CANONICALIZATION_CONTRACT = (
    "knowledge-governance-decision-json-v1"
)
KNOWLEDGE_GOVERNANCE_DIGEST_ALGORITHM = "sha256"
KNOWLEDGE_GOVERNANCE_DECISION_ID_PREFIX = "kg1_"

AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION = (
    "eligible_for_future_promotion_evaluation"
)

GOVERNANCE_DECISION_AUTHORIZED = "authorized"
GOVERNANCE_DECISION_DENIED = "denied"
GOVERNANCE_DECISION_DEFERRED = "deferred"

KNOWLEDGE_GOVERNANCE_DIAGNOSTIC_SEVERITY_INFO = "info"
KNOWLEDGE_GOVERNANCE_DIAGNOSTIC_SEVERITY_WARNING = "warning"

_GOVERNANCE_DECISIONS = frozenset(
    {
        GOVERNANCE_DECISION_AUTHORIZED,
        GOVERNANCE_DECISION_DENIED,
        GOVERNANCE_DECISION_DEFERRED,
    }
)
_DIAGNOSTIC_SEVERITIES = frozenset(
    {
        KNOWLEDGE_GOVERNANCE_DIAGNOSTIC_SEVERITY_INFO,
        KNOWLEDGE_GOVERNANCE_DIAGNOSTIC_SEVERITY_WARNING,
    }
)
_GOVERNANCE_DECISION_ID_PATTERN = re.compile(r"^kg1_[0-9a-f]{64}$")
_KNOWLEDGE_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
_KNOWLEDGE_REVIEW_RECORD_ID_PATTERN = re.compile(r"^kr1_[0-9a-f]{64}$")
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
    utc_value = value.astimezone(timezone.utc)
    return utc_value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


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
class KnowledgeGovernanceDiagnostic:
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


def compute_knowledge_governance_candidate_snapshot_digest(
    candidate: KnowledgeCandidate,
) -> str:
    if type(candidate) is not KnowledgeCandidate:
        raise ValueError("candidate must be an exact KnowledgeCandidate")
    return compute_knowledge_candidate_review_snapshot_digest(candidate)


def verify_knowledge_review_record_identity(
    record: KnowledgeReviewRecord,
) -> str:
    if type(record) is not KnowledgeReviewRecord:
        raise ValueError("record must be an exact KnowledgeReviewRecord")
    expected_id = compute_knowledge_review_record_id(
        knowledge_review_identity_input_from_record(record)
    )
    if record.knowledge_review_record_id != expected_id:
        raise ValueError("knowledge_review_record_id does not match identity")
    return record.knowledge_review_record_id


@dataclass(frozen=True)
class KnowledgeGovernanceIdentityInput:
    governance_decision_contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_review_record_ids: tuple[str, ...]
    authorization_scope: str
    governance_decision: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    governance_policy_id: str
    governance_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.governance_decision_contract_version
            != KNOWLEDGE_GOVERNANCE_DECISION_CONTRACT_VERSION
        ):
            raise ValueError("unsupported governance_decision_contract_version")
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
            self.knowledge_review_record_ids,
            "knowledge_review_record_ids",
            pattern=_KNOWLEDGE_REVIEW_RECORD_ID_PATTERN,
        )
        _require_string(self.authorization_scope, "authorization_scope")
        if (
            self.authorization_scope
            != AUTHORIZATION_SCOPE_ELIGIBLE_FOR_FUTURE_PROMOTION_EVALUATION
        ):
            raise ValueError("unsupported authorization_scope")
        _require_string(self.governance_decision, "governance_decision")
        if self.governance_decision not in _GOVERNANCE_DECISIONS:
            raise ValueError("unsupported governance_decision")
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        for field_name in (
            "decided_by",
            "governance_policy_id",
            "governance_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_aware_datetime(self.decided_at, "decided_at")


def canonical_knowledge_governance_identity_projection(
    identity_input: KnowledgeGovernanceIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgeGovernanceIdentityInput:
        raise ValueError(
            "identity_input must be an exact KnowledgeGovernanceIdentityInput"
        )
    return _canonicalize(
        {
            "authorization_scope": identity_input.authorization_scope,
            "decided_at": _format_decided_at(identity_input.decided_at),
            "decided_by": identity_input.decided_by,
            "governance_decision": identity_input.governance_decision,
            "governance_decision_contract_version": (
                identity_input.governance_decision_contract_version
            ),
            "governance_policy_id": identity_input.governance_policy_id,
            "governance_policy_version": (
                identity_input.governance_policy_version
            ),
            "identity_canonicalization_contract": (
                KNOWLEDGE_GOVERNANCE_IDENTITY_CANONICALIZATION_CONTRACT
            ),
            "knowledge_candidate_contract_version": (
                identity_input.knowledge_candidate_contract_version
            ),
            "knowledge_candidate_id": identity_input.knowledge_candidate_id,
            "knowledge_candidate_snapshot_digest": (
                identity_input.knowledge_candidate_snapshot_digest
            ),
            "knowledge_review_record_ids": (
                identity_input.knowledge_review_record_ids
            ),
            "reason_codes": identity_input.reason_codes,
        }
    )


def canonical_knowledge_governance_identity_bytes(
    identity_input: KnowledgeGovernanceIdentityInput,
) -> bytes:
    projection = canonical_knowledge_governance_identity_projection(
        identity_input
    )
    return json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_governance_decision_id(
    identity_input: KnowledgeGovernanceIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_governance_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_GOVERNANCE_DECISION_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgeGovernanceDecision:
    knowledge_governance_decision_id: str
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_review_record_ids: tuple[str, ...]
    authorization_scope: str
    governance_decision: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    governance_policy_id: str
    governance_policy_version: str
    diagnostics: tuple[KnowledgeGovernanceDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.knowledge_governance_decision_id,
            "knowledge_governance_decision_id",
            _GOVERNANCE_DECISION_ID_PATTERN,
        )
        identity_input = KnowledgeGovernanceIdentityInput(
            governance_decision_contract_version=self.contract_version,
            knowledge_candidate_id=self.knowledge_candidate_id,
            knowledge_candidate_contract_version=(
                self.knowledge_candidate_contract_version
            ),
            knowledge_candidate_snapshot_digest=(
                self.knowledge_candidate_snapshot_digest
            ),
            knowledge_review_record_ids=self.knowledge_review_record_ids,
            authorization_scope=self.authorization_scope,
            governance_decision=self.governance_decision,
            reason_codes=self.reason_codes,
            decided_by=self.decided_by,
            decided_at=self.decided_at,
            governance_policy_id=self.governance_policy_id,
            governance_policy_version=self.governance_policy_version,
        )
        diagnostics = _require_tuple(self.diagnostics, "diagnostics")
        for index, diagnostic in enumerate(diagnostics):
            if type(diagnostic) is not KnowledgeGovernanceDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact "
                    "KnowledgeGovernanceDiagnostic"
                )
        if (
            self.knowledge_governance_decision_id
            != compute_knowledge_governance_decision_id(identity_input)
        ):
            raise ValueError(
                "knowledge_governance_decision_id does not match identity"
            )


def knowledge_governance_identity_input_from_record(
    record: KnowledgeGovernanceDecision,
) -> KnowledgeGovernanceIdentityInput:
    if type(record) is not KnowledgeGovernanceDecision:
        raise ValueError(
            "record must be an exact KnowledgeGovernanceDecision"
        )
    return KnowledgeGovernanceIdentityInput(
        governance_decision_contract_version=record.contract_version,
        knowledge_candidate_id=record.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            record.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            record.knowledge_candidate_snapshot_digest
        ),
        knowledge_review_record_ids=record.knowledge_review_record_ids,
        authorization_scope=record.authorization_scope,
        governance_decision=record.governance_decision,
        reason_codes=record.reason_codes,
        decided_by=record.decided_by,
        decided_at=record.decided_at,
        governance_policy_id=record.governance_policy_id,
        governance_policy_version=record.governance_policy_version,
    )
