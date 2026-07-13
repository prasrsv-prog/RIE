"""Immutable pairwise Knowledge conflict assessment and identity contracts."""

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
from rie.domain.knowledge_review_record import (
    compute_knowledge_candidate_review_snapshot_digest,
)


KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION = (
    "knowledge-conflict-assessment-record-v1"
)
KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_ID_PREFIX = "kcf1_"
KNOWLEDGE_CONFLICT_IDENTITY_POLICY_ID = (
    "rcis-knowledge-conflict-assessment-record-identity"
)
KNOWLEDGE_CONFLICT_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_CONFLICT_IDENTITY_CANONICALIZATION_CONTRACT = (
    "knowledge-conflict-assessment-record-json-v1"
)
KNOWLEDGE_CONFLICT_DIGEST_ALGORITHM = "sha256"

ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP = (
    "pairwise_knowledge_candidate_semantic_relationship"
)

ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED = "conflict_identified"
ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT = "equivalent_statement"
ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED = "no_conflict_identified"
ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED = "assessment_deferred"

KNOWLEDGE_CONFLICT_DIAGNOSTIC_SEVERITY_INFO = "info"
KNOWLEDGE_CONFLICT_DIAGNOSTIC_SEVERITY_WARNING = "warning"

_ASSESSMENT_OUTCOMES = frozenset(
    {
        ASSESSMENT_OUTCOME_CONFLICT_IDENTIFIED,
        ASSESSMENT_OUTCOME_EQUIVALENT_STATEMENT,
        ASSESSMENT_OUTCOME_NO_CONFLICT_IDENTIFIED,
        ASSESSMENT_OUTCOME_ASSESSMENT_DEFERRED,
    }
)
_DIAGNOSTIC_SEVERITIES = frozenset(
    {
        KNOWLEDGE_CONFLICT_DIAGNOSTIC_SEVERITY_INFO,
        KNOWLEDGE_CONFLICT_DIAGNOSTIC_SEVERITY_WARNING,
    }
)
_CONFLICT_ASSESSMENT_RECORD_ID_PATTERN = re.compile(
    r"^kcf1_[0-9a-f]{64}$"
)
_KNOWLEDGE_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
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


def _require_unique_ordered_strings(value: object, field_name: str) -> None:
    items = _require_tuple(value, field_name)
    if not items:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(items):
        _require_string(item, f"{field_name}[{index}]")
    if len(set(items)) != len(items):
        raise ValueError(f"{field_name} must contain unique values")
    if items != tuple(sorted(items)):
        raise ValueError(f"{field_name} must be lexicographically ordered")


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _format_assessed_at(value: datetime) -> str:
    _require_aware_datetime(value, "assessed_at")
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
class KnowledgeConflictDiagnostic:
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
class KnowledgeConflictParticipant:
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str

    def __post_init__(self) -> None:
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


def _require_participants(value: object) -> None:
    participants = _require_tuple(value, "participants")
    if len(participants) != 2:
        raise ValueError("participants must contain exactly two values")
    candidate_ids: list[str] = []
    for index, participant in enumerate(participants):
        if type(participant) is not KnowledgeConflictParticipant:
            raise ValueError(
                f"participants[{index}] must be an exact "
                "KnowledgeConflictParticipant"
            )
        candidate_ids.append(participant.knowledge_candidate_id)
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("participants must contain unique candidate IDs")
    if candidate_ids != sorted(candidate_ids):
        raise ValueError("participants must be ordered by candidate ID")


def verify_knowledge_conflict_candidate_identity(
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


def compute_knowledge_conflict_candidate_snapshot_digest(
    candidate: KnowledgeCandidate,
) -> str:
    verify_knowledge_conflict_candidate_identity(candidate)
    return compute_knowledge_candidate_review_snapshot_digest(candidate)


def knowledge_conflict_participant_from_candidate(
    candidate: KnowledgeCandidate,
) -> KnowledgeConflictParticipant:
    verify_knowledge_conflict_candidate_identity(candidate)
    return KnowledgeConflictParticipant(
        knowledge_candidate_id=candidate.knowledge_candidate_id,
        knowledge_candidate_contract_version=candidate.contract_version,
        knowledge_candidate_snapshot_digest=(
            compute_knowledge_conflict_candidate_snapshot_digest(candidate)
        ),
    )


@dataclass(frozen=True)
class KnowledgeConflictIdentityInput:
    conflict_assessment_record_contract_version: str
    participants: tuple[KnowledgeConflictParticipant, ...]
    assessment_scope: str
    assessment_outcome: str
    reason_codes: tuple[str, ...]
    assessed_by: str
    assessed_at: datetime
    assessment_policy_id: str
    assessment_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.conflict_assessment_record_contract_version
            != KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_CONTRACT_VERSION
        ):
            raise ValueError(
                "unsupported conflict_assessment_record_contract_version"
            )
        _require_participants(self.participants)
        _require_string(self.assessment_scope, "assessment_scope")
        if (
            self.assessment_scope
            != ASSESSMENT_SCOPE_PAIRWISE_KNOWLEDGE_CANDIDATE_SEMANTIC_RELATIONSHIP
        ):
            raise ValueError("unsupported assessment_scope")
        _require_string(self.assessment_outcome, "assessment_outcome")
        if self.assessment_outcome not in _ASSESSMENT_OUTCOMES:
            raise ValueError("unsupported assessment_outcome")
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        for field_name in (
            "assessed_by",
            "assessment_policy_id",
            "assessment_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_aware_datetime(self.assessed_at, "assessed_at")


def canonical_knowledge_conflict_identity_projection(
    identity_input: KnowledgeConflictIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgeConflictIdentityInput:
        raise ValueError(
            "identity_input must be an exact KnowledgeConflictIdentityInput"
        )
    participant_projection = tuple(
        {
            "knowledge_candidate_contract_version": (
                participant.knowledge_candidate_contract_version
            ),
            "knowledge_candidate_id": participant.knowledge_candidate_id,
            "knowledge_candidate_snapshot_digest": (
                participant.knowledge_candidate_snapshot_digest
            ),
        }
        for participant in identity_input.participants
    )
    return _canonicalize(
        {
            "assessed_at": _format_assessed_at(identity_input.assessed_at),
            "assessed_by": identity_input.assessed_by,
            "assessment_outcome": identity_input.assessment_outcome,
            "assessment_policy_id": identity_input.assessment_policy_id,
            "assessment_policy_version": (
                identity_input.assessment_policy_version
            ),
            "assessment_scope": identity_input.assessment_scope,
            "conflict_assessment_record_contract_version": (
                identity_input.conflict_assessment_record_contract_version
            ),
            "identity_canonicalization_contract": (
                KNOWLEDGE_CONFLICT_IDENTITY_CANONICALIZATION_CONTRACT
            ),
            "participants": participant_projection,
            "reason_codes": identity_input.reason_codes,
        }
    )


def canonical_knowledge_conflict_identity_bytes(
    identity_input: KnowledgeConflictIdentityInput,
) -> bytes:
    projection = canonical_knowledge_conflict_identity_projection(identity_input)
    return json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_conflict_assessment_record_id(
    identity_input: KnowledgeConflictIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_conflict_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_CONFLICT_ASSESSMENT_RECORD_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgeConflictAssessmentRecord:
    knowledge_conflict_assessment_record_id: str
    contract_version: str
    participants: tuple[KnowledgeConflictParticipant, ...]
    assessment_scope: str
    assessment_outcome: str
    reason_codes: tuple[str, ...]
    assessed_by: str
    assessed_at: datetime
    assessment_policy_id: str
    assessment_policy_version: str
    diagnostics: tuple[KnowledgeConflictDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.knowledge_conflict_assessment_record_id,
            "knowledge_conflict_assessment_record_id",
            _CONFLICT_ASSESSMENT_RECORD_ID_PATTERN,
        )
        identity_input = KnowledgeConflictIdentityInput(
            conflict_assessment_record_contract_version=self.contract_version,
            participants=self.participants,
            assessment_scope=self.assessment_scope,
            assessment_outcome=self.assessment_outcome,
            reason_codes=self.reason_codes,
            assessed_by=self.assessed_by,
            assessed_at=self.assessed_at,
            assessment_policy_id=self.assessment_policy_id,
            assessment_policy_version=self.assessment_policy_version,
        )
        diagnostics = _require_tuple(self.diagnostics, "diagnostics")
        for index, diagnostic in enumerate(diagnostics):
            if type(diagnostic) is not KnowledgeConflictDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact "
                    "KnowledgeConflictDiagnostic"
                )
        if (
            self.knowledge_conflict_assessment_record_id
            != compute_knowledge_conflict_assessment_record_id(identity_input)
        ):
            raise ValueError(
                "knowledge_conflict_assessment_record_id does not match identity"
            )


def knowledge_conflict_identity_input_from_record(
    record: KnowledgeConflictAssessmentRecord,
) -> KnowledgeConflictIdentityInput:
    if type(record) is not KnowledgeConflictAssessmentRecord:
        raise ValueError(
            "record must be an exact KnowledgeConflictAssessmentRecord"
        )
    return KnowledgeConflictIdentityInput(
        conflict_assessment_record_contract_version=record.contract_version,
        participants=record.participants,
        assessment_scope=record.assessment_scope,
        assessment_outcome=record.assessment_outcome,
        reason_codes=record.reason_codes,
        assessed_by=record.assessed_by,
        assessed_at=record.assessed_at,
        assessment_policy_id=record.assessment_policy_id,
        assessment_policy_version=record.assessment_policy_version,
    )
