"""Deterministic, scope-limited Knowledge promotion decision records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import unicodedata

from rie.domain.knowledge_candidate import (
    KnowledgeCandidate,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
    PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
    KnowledgePromotionPrerequisiteEvaluation,
    compute_knowledge_promotion_prerequisite_evaluation_id,
    knowledge_promotion_prerequisite_identity_input_from_record,
)
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)


KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION = "knowledge-promotion-decision-v1"
KNOWLEDGE_PROMOTION_DECISION_ID_PREFIX = "kpd1_"
KNOWLEDGE_PROMOTION_DECISION_IDENTITY_POLICY_ID = (
    "rcis-knowledge-promotion-decision-identity"
)
KNOWLEDGE_PROMOTION_DECISION_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_PROMOTION_DECISION_IDENTITY_CANONICALIZATION_CONTRACT = (
    "knowledge-promotion-decision-json-v1"
)
KNOWLEDGE_PROMOTION_DECISION_DIGEST_ALGORITHM = "sha256"

PROMOTION_DECISION_AUTHORIZATION_SCOPE = (
    "eligible_for_future_promotion_execution_for_declared_scope"
)
PROMOTION_DECISION_OUTCOME_AUTHORIZED = (
    "promotion_authorized_for_future_execution"
)
PROMOTION_DECISION_OUTCOME_DENIED = "promotion_denied"
PROMOTION_DECISION_OUTCOME_DEFERRED = "promotion_decision_deferred"

KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_INFO = "info"
KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING = "warning"

PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION = (
    "satisfied_evaluation_supports_future_execution_authorization"
)
PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION = (
    "promotion_denied_despite_satisfied_evaluation"
)
PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION = (
    "promotion_decision_deferred_despite_satisfied_evaluation"
)
PROMOTION_DECISION_REASON_PROMOTION_DENIED_FOR_NOT_SATISFIED_EVALUATION = (
    "promotion_denied_for_not_satisfied_evaluation"
)
PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_NOT_SATISFIED_EVALUATION = (
    "promotion_decision_deferred_for_not_satisfied_evaluation"
)
PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_DEFERRED_EVALUATION = (
    "promotion_decision_deferred_for_deferred_evaluation"
)

PROMOTION_DECISION_CONTROLLED_REASONS = (
    PROMOTION_DECISION_REASON_SATISFIED_EVALUATION_SUPPORTS_FUTURE_EXECUTION_AUTHORIZATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_DESPITE_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DENIED_FOR_NOT_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_NOT_SATISFIED_EVALUATION,
    PROMOTION_DECISION_REASON_PROMOTION_DECISION_DEFERRED_FOR_DEFERRED_EVALUATION,
)

_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
_EVALUATION_ID_PATTERN = re.compile(r"^kpe1_[0-9a-f]{64}$")
_DECISION_ID_PATTERN = re.compile(r"^kpd1_[0-9a-f]{64}$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")

_EVALUATION_OUTCOMES = frozenset(
    {
        PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
        PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
        PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    }
)
_PROMOTION_DECISIONS = frozenset(
    {
        PROMOTION_DECISION_OUTCOME_AUTHORIZED,
        PROMOTION_DECISION_OUTCOME_DENIED,
        PROMOTION_DECISION_OUTCOME_DEFERRED,
    }
)
_DIAGNOSTIC_SEVERITIES = frozenset(
    {
        KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_INFO,
        KNOWLEDGE_PROMOTION_DECISION_DIAGNOSTIC_SEVERITY_WARNING,
    }
)


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_pattern(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> None:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError(f"{field_name} has an invalid format")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_unique_ordered_strings(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")
    if not value:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(value):
        _require_string(item, f"{field_name}[{index}]")
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must contain unique values")
    if value != tuple(sorted(value)):
        raise ValueError(f"{field_name} must be lexicographically ordered")
    return value


def _require_diagnostics(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("diagnostics must be a tuple")
    for index, diagnostic in enumerate(value):
        if type(diagnostic) is not KnowledgePromotionDecisionDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgePromotionDecisionDiagnostic"
            )


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _format_decided_at(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(
        timespec="microseconds"
    ).replace("+00:00", "Z")


def _canonicalize(value: object) -> object:
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("canonical values must be finite")
        return value
    if type(value) is str:
        return _normalize_text(value)
    if type(value) in (tuple, list):
        return [_canonicalize(item) for item in value]
    if type(value) is dict:
        result: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("canonical mapping keys must be strings")
            result[_normalize_text(key)] = _canonicalize(item)
        return result
    raise ValueError("unsupported canonical value")


@dataclass(frozen=True)
class KnowledgePromotionDecisionDiagnostic:
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


def verify_knowledge_promotion_decision_candidate_identity(
    candidate: KnowledgeCandidate,
) -> str:
    if type(candidate) is not KnowledgeCandidate:
        raise ValueError("candidate must be an exact KnowledgeCandidate")
    expected = compute_knowledge_candidate_id(
        identity_input_from_knowledge_candidate(candidate)
    )
    if candidate.knowledge_candidate_id != expected:
        raise ValueError("knowledge_candidate_id does not match identity")
    return expected


def compute_knowledge_promotion_decision_candidate_snapshot_digest(
    candidate: KnowledgeCandidate,
) -> str:
    verify_knowledge_promotion_decision_candidate_identity(candidate)
    return compute_knowledge_candidate_review_snapshot_digest(candidate)


def verify_knowledge_promotion_prerequisite_evaluation_identity(
    evaluation: KnowledgePromotionPrerequisiteEvaluation,
) -> str:
    if type(evaluation) is not KnowledgePromotionPrerequisiteEvaluation:
        raise ValueError(
            "evaluation must be an exact "
            "KnowledgePromotionPrerequisiteEvaluation"
        )
    expected = compute_knowledge_promotion_prerequisite_evaluation_id(
        knowledge_promotion_prerequisite_identity_input_from_record(evaluation)
    )
    if evaluation.knowledge_promotion_prerequisite_evaluation_id != expected:
        raise ValueError(
            "knowledge_promotion_prerequisite_evaluation_id does not match identity"
        )
    return expected


@dataclass(frozen=True)
class KnowledgePromotionDecisionIdentityInput:
    decision_record_contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_promotion_prerequisite_evaluation_id: str
    knowledge_promotion_prerequisite_evaluation_contract_version: str
    promotion_prerequisite_evaluation_outcome: str
    authorization_scope: str
    promotion_decision: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    decision_policy_id: str
    decision_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.decision_record_contract_version
            != KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION
        ):
            raise ValueError("unsupported decision_record_contract_version")
        _require_pattern(
            self.knowledge_candidate_id,
            "knowledge_candidate_id",
            _CANDIDATE_ID_PATTERN,
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
        _require_pattern(
            self.knowledge_promotion_prerequisite_evaluation_id,
            "knowledge_promotion_prerequisite_evaluation_id",
            _EVALUATION_ID_PATTERN,
        )
        _require_string(
            self.knowledge_promotion_prerequisite_evaluation_contract_version,
            "knowledge_promotion_prerequisite_evaluation_contract_version",
        )
        if self.promotion_prerequisite_evaluation_outcome not in _EVALUATION_OUTCOMES:
            raise ValueError("unsupported promotion_prerequisite_evaluation_outcome")
        if self.authorization_scope != PROMOTION_DECISION_AUTHORIZATION_SCOPE:
            raise ValueError("unsupported authorization_scope")
        if self.promotion_decision not in _PROMOTION_DECISIONS:
            raise ValueError("unsupported promotion_decision")
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        _require_string(self.decided_by, "decided_by")
        _require_aware_datetime(self.decided_at, "decided_at")
        _require_string(self.decision_policy_id, "decision_policy_id")
        _require_string(self.decision_policy_version, "decision_policy_version")


def canonical_knowledge_promotion_decision_identity_projection(
    identity_input: KnowledgePromotionDecisionIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgePromotionDecisionIdentityInput:
        raise ValueError(
            "identity_input must be an exact KnowledgePromotionDecisionIdentityInput"
        )
    return _canonicalize(
        {
            "decision_record_contract_version": (
                identity_input.decision_record_contract_version
            ),
            "knowledge_candidate_id": identity_input.knowledge_candidate_id,
            "knowledge_candidate_contract_version": (
                identity_input.knowledge_candidate_contract_version
            ),
            "knowledge_candidate_snapshot_digest": (
                identity_input.knowledge_candidate_snapshot_digest
            ),
            "knowledge_promotion_prerequisite_evaluation_id": (
                identity_input.knowledge_promotion_prerequisite_evaluation_id
            ),
            "knowledge_promotion_prerequisite_evaluation_contract_version": (
                identity_input.knowledge_promotion_prerequisite_evaluation_contract_version
            ),
            "promotion_prerequisite_evaluation_outcome": (
                identity_input.promotion_prerequisite_evaluation_outcome
            ),
            "authorization_scope": identity_input.authorization_scope,
            "promotion_decision": identity_input.promotion_decision,
            "reason_codes": identity_input.reason_codes,
            "decided_by": identity_input.decided_by,
            "decided_at": _format_decided_at(identity_input.decided_at),
            "decision_policy_id": identity_input.decision_policy_id,
            "decision_policy_version": identity_input.decision_policy_version,
            "identity_canonicalization_contract": (
                KNOWLEDGE_PROMOTION_DECISION_IDENTITY_CANONICALIZATION_CONTRACT
            ),
        }
    )  # type: ignore[return-value]


def canonical_knowledge_promotion_decision_identity_bytes(
    identity_input: KnowledgePromotionDecisionIdentityInput,
) -> bytes:
    return json.dumps(
        canonical_knowledge_promotion_decision_identity_projection(identity_input),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_promotion_decision_id(
    identity_input: KnowledgePromotionDecisionIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_promotion_decision_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_PROMOTION_DECISION_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgePromotionDecision:
    knowledge_promotion_decision_id: str
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_promotion_prerequisite_evaluation_id: str
    knowledge_promotion_prerequisite_evaluation_contract_version: str
    promotion_prerequisite_evaluation_outcome: str
    authorization_scope: str
    promotion_decision: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    decision_policy_id: str
    decision_policy_version: str
    diagnostics: tuple[KnowledgePromotionDecisionDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.knowledge_promotion_decision_id,
            "knowledge_promotion_decision_id",
            _DECISION_ID_PATTERN,
        )
        _require_diagnostics(self.diagnostics)
        identity_input = KnowledgePromotionDecisionIdentityInput(
            decision_record_contract_version=self.contract_version,
            knowledge_candidate_id=self.knowledge_candidate_id,
            knowledge_candidate_contract_version=(
                self.knowledge_candidate_contract_version
            ),
            knowledge_candidate_snapshot_digest=(
                self.knowledge_candidate_snapshot_digest
            ),
            knowledge_promotion_prerequisite_evaluation_id=(
                self.knowledge_promotion_prerequisite_evaluation_id
            ),
            knowledge_promotion_prerequisite_evaluation_contract_version=(
                self.knowledge_promotion_prerequisite_evaluation_contract_version
            ),
            promotion_prerequisite_evaluation_outcome=(
                self.promotion_prerequisite_evaluation_outcome
            ),
            authorization_scope=self.authorization_scope,
            promotion_decision=self.promotion_decision,
            reason_codes=self.reason_codes,
            decided_by=self.decided_by,
            decided_at=self.decided_at,
            decision_policy_id=self.decision_policy_id,
            decision_policy_version=self.decision_policy_version,
        )
        if (
            self.knowledge_promotion_decision_id
            != compute_knowledge_promotion_decision_id(identity_input)
        ):
            raise ValueError(
                "knowledge_promotion_decision_id does not match identity"
            )


def knowledge_promotion_decision_identity_input_from_record(
    record: KnowledgePromotionDecision,
) -> KnowledgePromotionDecisionIdentityInput:
    if type(record) is not KnowledgePromotionDecision:
        raise ValueError("record must be an exact KnowledgePromotionDecision")
    return KnowledgePromotionDecisionIdentityInput(
        decision_record_contract_version=record.contract_version,
        knowledge_candidate_id=record.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            record.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=record.knowledge_candidate_snapshot_digest,
        knowledge_promotion_prerequisite_evaluation_id=(
            record.knowledge_promotion_prerequisite_evaluation_id
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            record.knowledge_promotion_prerequisite_evaluation_contract_version
        ),
        promotion_prerequisite_evaluation_outcome=(
            record.promotion_prerequisite_evaluation_outcome
        ),
        authorization_scope=record.authorization_scope,
        promotion_decision=record.promotion_decision,
        reason_codes=record.reason_codes,
        decided_by=record.decided_by,
        decided_at=record.decided_at,
        decision_policy_id=record.decision_policy_id,
        decision_policy_version=record.decision_policy_version,
    )
