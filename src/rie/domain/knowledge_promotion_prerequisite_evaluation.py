"""Deterministic, scope-relative promotion-prerequisite evaluation records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import unicodedata


KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION = (
    "knowledge-promotion-evaluation-scope-v1"
)
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_ID_PREFIX = "kps1_"
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_POLICY_ID = (
    "rcis-knowledge-promotion-evaluation-scope-identity"
)
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_CANONICALIZATION_CONTRACT = (
    "knowledge-promotion-evaluation-scope-json-v1"
)
KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_DIGEST_ALGORITHM = "sha256"

KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION = (
    "knowledge-promotion-prerequisite-evaluation-v1"
)
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_ID_PREFIX = "kpe1_"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_POLICY_ID = (
    "rcis-knowledge-promotion-prerequisite-evaluation-identity"
)
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_CANONICALIZATION_CONTRACT = (
    "knowledge-promotion-prerequisite-evaluation-json-v1"
)
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_DIGEST_ALGORITHM = "sha256"

PROMOTION_EVALUATION_SCOPE_COMPLETENESS_QUALIFIER_COMPLETE_ONLY_FOR_DECLARED_PEER_SCOPE = (
    "complete_only_for_declared_peer_scope"
)
PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE = (
    "candidate_governance_conflict_authority_for_declared_peer_scope"
)
PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY = (
    "declared_scope_only"
)

PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE = (
    "prerequisites_satisfied_for_declared_scope"
)
PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE = (
    "prerequisites_not_satisfied_for_declared_scope"
)
PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE = (
    "prerequisites_deferred_for_declared_scope"
)

PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED = (
    "declared_scope_prerequisites_satisfied"
)
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED = (
    "declared_scope_prerequisites_not_satisfied"
)
PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED = (
    "governance_evidence_denied"
)
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_IDENTIFIED = (
    "declared_scope_conflict_identified"
)
PROMOTION_PREREQUISITE_REASON_AUTHORITY_VALUE_NOT_AUTHORITATIVE = (
    "authority_value_not_authoritative"
)
PROMOTION_PREREQUISITE_REASON_AUTHORITATIVE_VALUE_DENIED = (
    "authoritative_value_denied"
)
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED = (
    "declared_scope_prerequisites_deferred"
)
PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY = (
    "declared_peer_scope_empty"
)
PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DEFERRED = (
    "governance_evidence_deferred"
)
PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_CONTRADICTORY = (
    "governance_evidence_contradictory"
)
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_COVERAGE_INCOMPLETE = (
    "declared_scope_conflict_coverage_incomplete"
)
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_AMBIGUOUS = (
    "declared_scope_conflict_evidence_ambiguous"
)
PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_DEFERRED = (
    "declared_scope_conflict_evidence_deferred"
)
PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_DEFERRED = (
    "authority_evidence_deferred"
)
PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_CONTRADICTORY = (
    "authority_evidence_contradictory"
)
PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_NOT_AFFIRMATIVE = (
    "authority_evidence_not_affirmative"
)

KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_INFO = "info"
KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING = "warning"

PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_RECORDED = "recorded"
PROMOTION_PREREQUISITE_EVALUATION_RESULT_STATUS_REJECTED = "rejected"
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_ID = (
    "rcis-knowledge-promotion-prerequisite-evaluation"
)
KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_POLICY_VERSION = "1.0.0"
PROMOTION_EVALUATION_SCOPE_POLICY_ID = (
    "rcis-declared-knowledge-promotion-evaluation-scope"
)
PROMOTION_EVALUATION_SCOPE_POLICY_VERSION = "1.0.0"

PROMOTION_PREREQUISITE_EVALUATION_REJECTION_REASONS = (
    "unsupported_promotion_prerequisite_evaluation_policy",
    "unsupported_promotion_evaluation_scope_policy",
    "scope_candidate_mismatch",
    "scope_candidate_contract_mismatch",
    "scope_candidate_snapshot_mismatch",
    "unsupported_governance_evidence_policy",
    "governance_candidate_mismatch",
    "governance_candidate_contract_mismatch",
    "governance_candidate_snapshot_mismatch",
    "unsupported_conflict_evidence_policy",
    "conflict_record_outside_declared_scope",
    "conflict_participant_contract_mismatch",
    "conflict_participant_snapshot_mismatch",
    "unsupported_authority_evidence_policy",
    "authority_candidate_mismatch",
    "authority_candidate_contract_mismatch",
    "authority_candidate_snapshot_mismatch",
    "authority_governance_lineage_mismatch",
    "missing_or_mismatched_required_evaluation_reason",
)

_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
_GOVERNANCE_ID_PATTERN = re.compile(r"^kg1_[0-9a-f]{64}$")
_CONFLICT_ID_PATTERN = re.compile(r"^kcf1_[0-9a-f]{64}$")
_AUTHORITY_ID_PATTERN = re.compile(r"^ka1_[0-9a-f]{64}$")
_SCOPE_ID_PATTERN = re.compile(r"^kps1_[0-9a-f]{64}$")
_EVALUATION_ID_PATTERN = re.compile(r"^kpe1_[0-9a-f]{64}$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")

_DIAGNOSTIC_SEVERITIES = frozenset(
    {
        KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_INFO,
        KNOWLEDGE_PROMOTION_PREREQUISITE_DIAGNOSTIC_SEVERITY_WARNING,
    }
)
_EVALUATION_OUTCOMES = frozenset(
    {
        PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE,
        PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE,
        PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE,
    }
)
_BLOCKER_REASONS = frozenset(
    {
        PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DENIED,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_IDENTIFIED,
        PROMOTION_PREREQUISITE_REASON_AUTHORITY_VALUE_NOT_AUTHORITATIVE,
        PROMOTION_PREREQUISITE_REASON_AUTHORITATIVE_VALUE_DENIED,
    }
)
_DEFERRED_REASONS = frozenset(
    {
        PROMOTION_PREREQUISITE_REASON_DECLARED_PEER_SCOPE_EMPTY,
        PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_DEFERRED,
        PROMOTION_PREREQUISITE_REASON_GOVERNANCE_EVIDENCE_CONTRADICTORY,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_COVERAGE_INCOMPLETE,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_AMBIGUOUS,
        PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_CONFLICT_EVIDENCE_DEFERRED,
        PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_DEFERRED,
        PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_CONTRADICTORY,
        PROMOTION_PREREQUISITE_REASON_AUTHORITY_EVIDENCE_NOT_AFFIRMATIVE,
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
    *,
    allow_empty: bool,
    pattern: re.Pattern[str] | None = None,
) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")
    if not allow_empty and not value:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(value):
        if pattern is None:
            _require_string(item, f"{field_name}[{index}]")
        else:
            _require_pattern(item, f"{field_name}[{index}]", pattern)
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must contain unique values")
    if value != tuple(sorted(value)):
        raise ValueError(f"{field_name} must be lexicographically ordered")
    return value


def _require_peers(
    value: object,
    target_candidate_id: str,
) -> tuple[KnowledgePromotionEvaluationScopePeer, ...]:
    if type(value) is not tuple:
        raise ValueError("peers must be a tuple")
    candidate_ids: list[str] = []
    for index, peer in enumerate(value):
        if type(peer) is not KnowledgePromotionEvaluationScopePeer:
            raise ValueError(
                f"peers[{index}] must be an exact "
                "KnowledgePromotionEvaluationScopePeer"
            )
        if peer.knowledge_candidate_id == target_candidate_id:
            raise ValueError("target candidate must not appear as a peer")
        candidate_ids.append(peer.knowledge_candidate_id)
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("peers must contain unique candidate IDs")
    if candidate_ids != sorted(candidate_ids):
        raise ValueError("peers must be ordered by candidate ID")
    return value


def _require_evaluation_reason_codes(
    value: object,
    outcome: str,
) -> tuple[str, ...]:
    reasons = _require_unique_ordered_strings(
        value,
        "reason_codes",
        allow_empty=False,
    )
    reason_set = set(reasons)
    if outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_SATISFIED_FOR_DECLARED_SCOPE:
        if reasons != (
            PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_SATISFIED,
        ):
            raise ValueError("satisfied evaluation reasons are inconsistent")
    elif outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_NOT_SATISFIED_FOR_DECLARED_SCOPE:
        general = PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_NOT_SATISFIED
        if general not in reason_set or not reason_set.issubset(_BLOCKER_REASONS | {general}):
            raise ValueError("not-satisfied evaluation reasons are inconsistent")
    elif outcome == PROMOTION_PREREQUISITE_EVALUATION_OUTCOME_DEFERRED_FOR_DECLARED_SCOPE:
        general = PROMOTION_PREREQUISITE_REASON_DECLARED_SCOPE_PREREQUISITES_DEFERRED
        if general not in reason_set or not reason_set.issubset(_DEFERRED_REASONS | {general}):
            raise ValueError("deferred evaluation reasons are inconsistent")
    return reasons


def _require_diagnostics(value: object) -> None:
    if type(value) is not tuple:
        raise ValueError("diagnostics must be a tuple")
    for index, diagnostic in enumerate(value):
        if type(diagnostic) is not KnowledgePromotionPrerequisiteDiagnostic:
            raise ValueError(
                f"diagnostics[{index}] must be an exact "
                "KnowledgePromotionPrerequisiteDiagnostic"
            )


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _format_timestamp(value: datetime) -> str:
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
class KnowledgePromotionEvaluationScopePeer:
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str

    def __post_init__(self) -> None:
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


@dataclass(frozen=True)
class KnowledgePromotionEvaluationScopeIdentityInput:
    scope_contract_version: str
    target_knowledge_candidate_id: str
    target_knowledge_candidate_contract_version: str
    target_knowledge_candidate_snapshot_digest: str
    peers: tuple[KnowledgePromotionEvaluationScopePeer, ...]
    completeness_qualifier: str
    scoped_by: str
    reason_codes: tuple[str, ...]
    scoped_at: datetime
    scope_policy_id: str
    scope_policy_version: str

    def __post_init__(self) -> None:
        if self.scope_contract_version != KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_CONTRACT_VERSION:
            raise ValueError("unsupported scope_contract_version")
        _require_pattern(self.target_knowledge_candidate_id, "target_knowledge_candidate_id", _CANDIDATE_ID_PATTERN)
        _require_string(self.target_knowledge_candidate_contract_version, "target_knowledge_candidate_contract_version")
        _require_pattern(self.target_knowledge_candidate_snapshot_digest, "target_knowledge_candidate_snapshot_digest", _DIGEST_PATTERN)
        _require_peers(self.peers, self.target_knowledge_candidate_id)
        if self.completeness_qualifier != PROMOTION_EVALUATION_SCOPE_COMPLETENESS_QUALIFIER_COMPLETE_ONLY_FOR_DECLARED_PEER_SCOPE:
            raise ValueError("unsupported completeness_qualifier")
        _require_string(self.scoped_by, "scoped_by")
        _require_unique_ordered_strings(self.reason_codes, "reason_codes", allow_empty=False)
        _require_aware_datetime(self.scoped_at, "scoped_at")
        _require_string(self.scope_policy_id, "scope_policy_id")
        _require_string(self.scope_policy_version, "scope_policy_version")


def canonical_knowledge_promotion_evaluation_scope_identity_projection(
    identity_input: KnowledgePromotionEvaluationScopeIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgePromotionEvaluationScopeIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "KnowledgePromotionEvaluationScopeIdentityInput"
        )
    return _canonicalize(
        {
            "scope_contract_version": identity_input.scope_contract_version,
            "target_knowledge_candidate_id": identity_input.target_knowledge_candidate_id,
            "target_knowledge_candidate_contract_version": identity_input.target_knowledge_candidate_contract_version,
            "target_knowledge_candidate_snapshot_digest": identity_input.target_knowledge_candidate_snapshot_digest,
            "peers": tuple(
                {
                    "knowledge_candidate_id": peer.knowledge_candidate_id,
                    "knowledge_candidate_contract_version": peer.knowledge_candidate_contract_version,
                    "knowledge_candidate_snapshot_digest": peer.knowledge_candidate_snapshot_digest,
                }
                for peer in identity_input.peers
            ),
            "completeness_qualifier": identity_input.completeness_qualifier,
            "scoped_by": identity_input.scoped_by,
            "reason_codes": identity_input.reason_codes,
            "scoped_at": _format_timestamp(identity_input.scoped_at),
            "scope_policy_id": identity_input.scope_policy_id,
            "scope_policy_version": identity_input.scope_policy_version,
            "identity_canonicalization_contract": KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_IDENTITY_CANONICALIZATION_CONTRACT,
        }
    )  # type: ignore[return-value]


def canonical_knowledge_promotion_evaluation_scope_identity_bytes(
    identity_input: KnowledgePromotionEvaluationScopeIdentityInput,
) -> bytes:
    return json.dumps(
        canonical_knowledge_promotion_evaluation_scope_identity_projection(identity_input),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_promotion_evaluation_scope_id(
    identity_input: KnowledgePromotionEvaluationScopeIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_promotion_evaluation_scope_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_PROMOTION_EVALUATION_SCOPE_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgePromotionEvaluationScope:
    knowledge_promotion_evaluation_scope_id: str
    contract_version: str
    target_knowledge_candidate_id: str
    target_knowledge_candidate_contract_version: str
    target_knowledge_candidate_snapshot_digest: str
    peers: tuple[KnowledgePromotionEvaluationScopePeer, ...]
    completeness_qualifier: str
    scoped_by: str
    reason_codes: tuple[str, ...]
    scoped_at: datetime
    scope_policy_id: str
    scope_policy_version: str

    def __post_init__(self) -> None:
        _require_pattern(self.knowledge_promotion_evaluation_scope_id, "knowledge_promotion_evaluation_scope_id", _SCOPE_ID_PATTERN)
        identity_input = KnowledgePromotionEvaluationScopeIdentityInput(
            scope_contract_version=self.contract_version,
            target_knowledge_candidate_id=self.target_knowledge_candidate_id,
            target_knowledge_candidate_contract_version=self.target_knowledge_candidate_contract_version,
            target_knowledge_candidate_snapshot_digest=self.target_knowledge_candidate_snapshot_digest,
            peers=self.peers,
            completeness_qualifier=self.completeness_qualifier,
            scoped_by=self.scoped_by,
            reason_codes=self.reason_codes,
            scoped_at=self.scoped_at,
            scope_policy_id=self.scope_policy_id,
            scope_policy_version=self.scope_policy_version,
        )
        if self.knowledge_promotion_evaluation_scope_id != compute_knowledge_promotion_evaluation_scope_id(identity_input):
            raise ValueError("knowledge_promotion_evaluation_scope_id does not match identity")


def knowledge_promotion_evaluation_scope_identity_input_from_record(
    record: KnowledgePromotionEvaluationScope,
) -> KnowledgePromotionEvaluationScopeIdentityInput:
    if type(record) is not KnowledgePromotionEvaluationScope:
        raise ValueError(
            "record must be an exact KnowledgePromotionEvaluationScope"
        )
    return KnowledgePromotionEvaluationScopeIdentityInput(
        scope_contract_version=record.contract_version,
        target_knowledge_candidate_id=record.target_knowledge_candidate_id,
        target_knowledge_candidate_contract_version=record.target_knowledge_candidate_contract_version,
        target_knowledge_candidate_snapshot_digest=record.target_knowledge_candidate_snapshot_digest,
        peers=record.peers,
        completeness_qualifier=record.completeness_qualifier,
        scoped_by=record.scoped_by,
        reason_codes=record.reason_codes,
        scoped_at=record.scoped_at,
        scope_policy_id=record.scope_policy_id,
        scope_policy_version=record.scope_policy_version,
    )


@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteDiagnostic:
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
class KnowledgePromotionPrerequisiteIdentityInput:
    evaluation_record_contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_promotion_evaluation_scope_id: str
    knowledge_governance_decision_ids: tuple[str, ...]
    knowledge_conflict_assessment_record_ids: tuple[str, ...]
    knowledge_authority_decision_ids: tuple[str, ...]
    evaluation_scope: str
    completeness_basis: str
    evaluation_outcome: str
    reason_codes: tuple[str, ...]
    evaluated_by: str
    evaluated_at: datetime
    evaluation_policy_id: str
    evaluation_policy_version: str

    def __post_init__(self) -> None:
        if self.evaluation_record_contract_version != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION:
            raise ValueError("unsupported evaluation_record_contract_version")
        _require_pattern(self.knowledge_candidate_id, "knowledge_candidate_id", _CANDIDATE_ID_PATTERN)
        _require_string(self.knowledge_candidate_contract_version, "knowledge_candidate_contract_version")
        _require_pattern(self.knowledge_candidate_snapshot_digest, "knowledge_candidate_snapshot_digest", _DIGEST_PATTERN)
        _require_pattern(self.knowledge_promotion_evaluation_scope_id, "knowledge_promotion_evaluation_scope_id", _SCOPE_ID_PATTERN)
        _require_unique_ordered_strings(self.knowledge_governance_decision_ids, "knowledge_governance_decision_ids", allow_empty=False, pattern=_GOVERNANCE_ID_PATTERN)
        _require_unique_ordered_strings(self.knowledge_conflict_assessment_record_ids, "knowledge_conflict_assessment_record_ids", allow_empty=True, pattern=_CONFLICT_ID_PATTERN)
        _require_unique_ordered_strings(self.knowledge_authority_decision_ids, "knowledge_authority_decision_ids", allow_empty=False, pattern=_AUTHORITY_ID_PATTERN)
        if self.evaluation_scope != PROMOTION_PREREQUISITE_EVALUATION_SCOPE_CANDIDATE_GOVERNANCE_CONFLICT_AUTHORITY_FOR_DECLARED_PEER_SCOPE:
            raise ValueError("unsupported evaluation_scope")
        if self.completeness_basis != PROMOTION_PREREQUISITE_EVALUATION_COMPLETENESS_BASIS_DECLARED_SCOPE_ONLY:
            raise ValueError("unsupported completeness_basis")
        if self.evaluation_outcome not in _EVALUATION_OUTCOMES:
            raise ValueError("unsupported evaluation_outcome")
        _require_evaluation_reason_codes(self.reason_codes, self.evaluation_outcome)
        _require_string(self.evaluated_by, "evaluated_by")
        _require_aware_datetime(self.evaluated_at, "evaluated_at")
        _require_string(self.evaluation_policy_id, "evaluation_policy_id")
        _require_string(self.evaluation_policy_version, "evaluation_policy_version")


def canonical_knowledge_promotion_prerequisite_identity_projection(
    identity_input: KnowledgePromotionPrerequisiteIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgePromotionPrerequisiteIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "KnowledgePromotionPrerequisiteIdentityInput"
        )
    return _canonicalize(
        {
            "evaluation_record_contract_version": identity_input.evaluation_record_contract_version,
            "knowledge_candidate_id": identity_input.knowledge_candidate_id,
            "knowledge_candidate_contract_version": identity_input.knowledge_candidate_contract_version,
            "knowledge_candidate_snapshot_digest": identity_input.knowledge_candidate_snapshot_digest,
            "knowledge_promotion_evaluation_scope_id": identity_input.knowledge_promotion_evaluation_scope_id,
            "knowledge_governance_decision_ids": identity_input.knowledge_governance_decision_ids,
            "knowledge_conflict_assessment_record_ids": identity_input.knowledge_conflict_assessment_record_ids,
            "knowledge_authority_decision_ids": identity_input.knowledge_authority_decision_ids,
            "evaluation_scope": identity_input.evaluation_scope,
            "completeness_basis": identity_input.completeness_basis,
            "evaluation_outcome": identity_input.evaluation_outcome,
            "reason_codes": identity_input.reason_codes,
            "evaluated_by": identity_input.evaluated_by,
            "evaluated_at": _format_timestamp(identity_input.evaluated_at),
            "evaluation_policy_id": identity_input.evaluation_policy_id,
            "evaluation_policy_version": identity_input.evaluation_policy_version,
            "identity_canonicalization_contract": KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_IDENTITY_CANONICALIZATION_CONTRACT,
        }
    )  # type: ignore[return-value]


def canonical_knowledge_promotion_prerequisite_identity_bytes(
    identity_input: KnowledgePromotionPrerequisiteIdentityInput,
) -> bytes:
    return json.dumps(
        canonical_knowledge_promotion_prerequisite_identity_projection(identity_input),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_promotion_prerequisite_evaluation_id(
    identity_input: KnowledgePromotionPrerequisiteIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_promotion_prerequisite_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgePromotionPrerequisiteEvaluation:
    knowledge_promotion_prerequisite_evaluation_id: str
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    knowledge_promotion_evaluation_scope_id: str
    knowledge_governance_decision_ids: tuple[str, ...]
    knowledge_conflict_assessment_record_ids: tuple[str, ...]
    knowledge_authority_decision_ids: tuple[str, ...]
    evaluation_scope: str
    completeness_basis: str
    evaluation_outcome: str
    reason_codes: tuple[str, ...]
    evaluated_by: str
    evaluated_at: datetime
    evaluation_policy_id: str
    evaluation_policy_version: str
    diagnostics: tuple[KnowledgePromotionPrerequisiteDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(self.knowledge_promotion_prerequisite_evaluation_id, "knowledge_promotion_prerequisite_evaluation_id", _EVALUATION_ID_PATTERN)
        _require_diagnostics(self.diagnostics)
        identity_input = KnowledgePromotionPrerequisiteIdentityInput(
            evaluation_record_contract_version=self.contract_version,
            knowledge_candidate_id=self.knowledge_candidate_id,
            knowledge_candidate_contract_version=self.knowledge_candidate_contract_version,
            knowledge_candidate_snapshot_digest=self.knowledge_candidate_snapshot_digest,
            knowledge_promotion_evaluation_scope_id=self.knowledge_promotion_evaluation_scope_id,
            knowledge_governance_decision_ids=self.knowledge_governance_decision_ids,
            knowledge_conflict_assessment_record_ids=self.knowledge_conflict_assessment_record_ids,
            knowledge_authority_decision_ids=self.knowledge_authority_decision_ids,
            evaluation_scope=self.evaluation_scope,
            completeness_basis=self.completeness_basis,
            evaluation_outcome=self.evaluation_outcome,
            reason_codes=self.reason_codes,
            evaluated_by=self.evaluated_by,
            evaluated_at=self.evaluated_at,
            evaluation_policy_id=self.evaluation_policy_id,
            evaluation_policy_version=self.evaluation_policy_version,
        )
        if self.knowledge_promotion_prerequisite_evaluation_id != compute_knowledge_promotion_prerequisite_evaluation_id(identity_input):
            raise ValueError("knowledge_promotion_prerequisite_evaluation_id does not match identity")


def knowledge_promotion_prerequisite_identity_input_from_record(
    record: KnowledgePromotionPrerequisiteEvaluation,
) -> KnowledgePromotionPrerequisiteIdentityInput:
    if type(record) is not KnowledgePromotionPrerequisiteEvaluation:
        raise ValueError(
            "record must be an exact KnowledgePromotionPrerequisiteEvaluation"
        )
    return KnowledgePromotionPrerequisiteIdentityInput(
        evaluation_record_contract_version=record.contract_version,
        knowledge_candidate_id=record.knowledge_candidate_id,
        knowledge_candidate_contract_version=record.knowledge_candidate_contract_version,
        knowledge_candidate_snapshot_digest=record.knowledge_candidate_snapshot_digest,
        knowledge_promotion_evaluation_scope_id=record.knowledge_promotion_evaluation_scope_id,
        knowledge_governance_decision_ids=record.knowledge_governance_decision_ids,
        knowledge_conflict_assessment_record_ids=record.knowledge_conflict_assessment_record_ids,
        knowledge_authority_decision_ids=record.knowledge_authority_decision_ids,
        evaluation_scope=record.evaluation_scope,
        completeness_basis=record.completeness_basis,
        evaluation_outcome=record.evaluation_outcome,
        reason_codes=record.reason_codes,
        evaluated_by=record.evaluated_by,
        evaluated_at=record.evaluated_at,
        evaluation_policy_id=record.evaluation_policy_id,
        evaluation_policy_version=record.evaluation_policy_version,
    )
