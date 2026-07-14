"""Deterministic, scope-limited Knowledge promotion execution records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import unicodedata


KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION = (
    "knowledge-promotion-execution-v1"
)
KNOWLEDGE_PROMOTION_EXECUTION_ID_PREFIX = "kpx1_"
KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_POLICY_ID = (
    "rcis-knowledge-promotion-execution-identity"
)
KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_CANONICALIZATION_CONTRACT = (
    "knowledge-promotion-execution-json-v1"
)
KNOWLEDGE_PROMOTION_EXECUTION_DIGEST_ALGORITHM = "sha256"

PROMOTION_EXECUTION_SCOPE_DECLARED = "promotion_execution_for_declared_scope"
PROMOTION_EXECUTION_OUTCOME_COMPLETED = (
    "promotion_execution_completed_for_declared_scope"
)
PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION = (
    "authorized_promotion_execution_completed_for_declared_scope"
)

KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_INFO = "info"
KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_WARNING = "warning"

PROMOTION_EXECUTION_CONTROLLED_REASONS = (
    PROMOTION_EXECUTION_REASON_AUTHORIZED_COMPLETION,
)

_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
_EVALUATION_ID_PATTERN = re.compile(r"^kpe1_[0-9a-f]{64}$")
_DECISION_ID_PATTERN = re.compile(r"^kpd1_[0-9a-f]{64}$")
_EXECUTION_ID_PATTERN = re.compile(r"^kpx1_[0-9a-f]{64}$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")

_DIAGNOSTIC_SEVERITIES = frozenset(
    {
        KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_INFO,
        KNOWLEDGE_PROMOTION_EXECUTION_DIAGNOSTIC_SEVERITY_WARNING,
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
        if type(diagnostic) is not KnowledgePromotionExecutionDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgePromotionExecutionDiagnostic"
            )


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _format_executed_at(value: datetime) -> str:
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
class KnowledgePromotionExecutionDiagnostic:
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


@dataclass(frozen=True)
class KnowledgePromotionExecutionIdentityInput:
    execution_record_contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_promotion_prerequisite_evaluation_id: str
    knowledge_promotion_prerequisite_evaluation_contract_version: str
    knowledge_promotion_decision_id: str
    knowledge_promotion_decision_contract_version: str
    promotion_decision_outcome: str
    authorization_scope: str
    execution_scope: str
    execution_outcome: str
    execution_reference: str
    reason_codes: tuple[str, ...]
    executed_by: str
    executed_at: datetime
    execution_policy_id: str
    execution_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.execution_record_contract_version
            != KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION
        ):
            raise ValueError("unsupported execution_record_contract_version")
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
        _require_pattern(
            self.knowledge_promotion_decision_id,
            "knowledge_promotion_decision_id",
            _DECISION_ID_PATTERN,
        )
        _require_string(
            self.knowledge_promotion_decision_contract_version,
            "knowledge_promotion_decision_contract_version",
        )
        _require_string(
            self.promotion_decision_outcome,
            "promotion_decision_outcome",
        )
        _require_string(self.authorization_scope, "authorization_scope")
        if self.execution_scope != PROMOTION_EXECUTION_SCOPE_DECLARED:
            raise ValueError("unsupported execution_scope")
        if self.execution_outcome != PROMOTION_EXECUTION_OUTCOME_COMPLETED:
            raise ValueError("unsupported execution_outcome")
        _require_string(self.execution_reference, "execution_reference")
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        _require_string(self.executed_by, "executed_by")
        _require_aware_datetime(self.executed_at, "executed_at")
        _require_string(self.execution_policy_id, "execution_policy_id")
        _require_string(
            self.execution_policy_version,
            "execution_policy_version",
        )


def canonical_knowledge_promotion_execution_identity_projection(
    identity_input: KnowledgePromotionExecutionIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgePromotionExecutionIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "KnowledgePromotionExecutionIdentityInput"
        )
    return _canonicalize(
        {
            "execution_record_contract_version": (
                identity_input.execution_record_contract_version
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
            "knowledge_promotion_decision_id": (
                identity_input.knowledge_promotion_decision_id
            ),
            "knowledge_promotion_decision_contract_version": (
                identity_input.knowledge_promotion_decision_contract_version
            ),
            "promotion_decision_outcome": (
                identity_input.promotion_decision_outcome
            ),
            "authorization_scope": identity_input.authorization_scope,
            "execution_scope": identity_input.execution_scope,
            "execution_outcome": identity_input.execution_outcome,
            "execution_reference": identity_input.execution_reference,
            "reason_codes": identity_input.reason_codes,
            "executed_by": identity_input.executed_by,
            "executed_at": _format_executed_at(identity_input.executed_at),
            "execution_policy_id": identity_input.execution_policy_id,
            "execution_policy_version": identity_input.execution_policy_version,
            "identity_canonicalization_contract": (
                KNOWLEDGE_PROMOTION_EXECUTION_IDENTITY_CANONICALIZATION_CONTRACT
            ),
        }
    )  # type: ignore[return-value]


def canonical_knowledge_promotion_execution_identity_bytes(
    identity_input: KnowledgePromotionExecutionIdentityInput,
) -> bytes:
    return json.dumps(
        canonical_knowledge_promotion_execution_identity_projection(identity_input),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_promotion_execution_id(
    identity_input: KnowledgePromotionExecutionIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_promotion_execution_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_PROMOTION_EXECUTION_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgePromotionExecutionRecord:
    knowledge_promotion_execution_id: str
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_promotion_prerequisite_evaluation_id: str
    knowledge_promotion_prerequisite_evaluation_contract_version: str
    knowledge_promotion_decision_id: str
    knowledge_promotion_decision_contract_version: str
    promotion_decision_outcome: str
    authorization_scope: str
    execution_scope: str
    execution_outcome: str
    execution_reference: str
    reason_codes: tuple[str, ...]
    executed_by: str
    executed_at: datetime
    execution_policy_id: str
    execution_policy_version: str
    diagnostics: tuple[KnowledgePromotionExecutionDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.knowledge_promotion_execution_id,
            "knowledge_promotion_execution_id",
            _EXECUTION_ID_PATTERN,
        )
        _require_diagnostics(self.diagnostics)
        identity_input = KnowledgePromotionExecutionIdentityInput(
            execution_record_contract_version=self.contract_version,
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
            knowledge_promotion_decision_id=self.knowledge_promotion_decision_id,
            knowledge_promotion_decision_contract_version=(
                self.knowledge_promotion_decision_contract_version
            ),
            promotion_decision_outcome=self.promotion_decision_outcome,
            authorization_scope=self.authorization_scope,
            execution_scope=self.execution_scope,
            execution_outcome=self.execution_outcome,
            execution_reference=self.execution_reference,
            reason_codes=self.reason_codes,
            executed_by=self.executed_by,
            executed_at=self.executed_at,
            execution_policy_id=self.execution_policy_id,
            execution_policy_version=self.execution_policy_version,
        )
        if (
            self.knowledge_promotion_execution_id
            != compute_knowledge_promotion_execution_id(identity_input)
        ):
            raise ValueError(
                "knowledge_promotion_execution_id does not match identity"
            )


def knowledge_promotion_execution_identity_input_from_record(
    record: KnowledgePromotionExecutionRecord,
) -> KnowledgePromotionExecutionIdentityInput:
    if type(record) is not KnowledgePromotionExecutionRecord:
        raise ValueError(
            "record must be an exact KnowledgePromotionExecutionRecord"
        )
    return KnowledgePromotionExecutionIdentityInput(
        execution_record_contract_version=record.contract_version,
        knowledge_candidate_id=record.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            record.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            record.knowledge_candidate_snapshot_digest
        ),
        knowledge_promotion_prerequisite_evaluation_id=(
            record.knowledge_promotion_prerequisite_evaluation_id
        ),
        knowledge_promotion_prerequisite_evaluation_contract_version=(
            record.knowledge_promotion_prerequisite_evaluation_contract_version
        ),
        knowledge_promotion_decision_id=record.knowledge_promotion_decision_id,
        knowledge_promotion_decision_contract_version=(
            record.knowledge_promotion_decision_contract_version
        ),
        promotion_decision_outcome=record.promotion_decision_outcome,
        authorization_scope=record.authorization_scope,
        execution_scope=record.execution_scope,
        execution_outcome=record.execution_outcome,
        execution_reference=record.execution_reference,
        reason_codes=record.reason_codes,
        executed_by=record.executed_by,
        executed_at=record.executed_at,
        execution_policy_id=record.execution_policy_id,
        execution_policy_version=record.execution_policy_version,
    )
