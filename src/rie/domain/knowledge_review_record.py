"""Immutable Knowledge review record and deterministic identity contracts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from math import isfinite
import re
import unicodedata

from rie.domain.knowledge_candidate import KnowledgeCandidate


KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION = "knowledge-review-record-v1"
KNOWLEDGE_REVIEW_IDENTITY_POLICY_ID = "rcis-knowledge-review-record-identity"
KNOWLEDGE_REVIEW_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_REVIEW_IDENTITY_CANONICALIZATION_CONTRACT = (
    "knowledge-review-record-json-v1"
)
KNOWLEDGE_CANDIDATE_REVIEW_SNAPSHOT_CANONICALIZATION_CONTRACT = (
    "knowledge-candidate-review-snapshot-json-v1"
)
KNOWLEDGE_REVIEW_DIGEST_ALGORITHM = "sha256"
KNOWLEDGE_REVIEW_RECORD_ID_PREFIX = "kr1_"

REVIEW_DECISION_PASSED = "passed"
REVIEW_DECISION_REJECTED = "rejected"
REVIEW_DECISION_DEFERRED = "deferred"

_REVIEW_DECISIONS = frozenset(
    {
        REVIEW_DECISION_PASSED,
        REVIEW_DECISION_REJECTED,
        REVIEW_DECISION_DEFERRED,
    }
)
_REVIEW_RECORD_ID_PATTERN = re.compile(r"^kr1_[0-9a-f]{64}$")
_KNOWLEDGE_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
_EVIDENCE_ID_PATTERN = re.compile(r"^ev1_[0-9a-f]{64}$")
_ACCEPTANCE_RECORD_ID_PATTERN = re.compile(r"^ar1_[0-9a-f]{64}$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_DIAGNOSTIC_SEVERITIES = frozenset({"info", "warning"})


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


def _format_reviewed_at(value: datetime) -> str:
    _require_aware_datetime(value, "reviewed_at")
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
class KnowledgeReviewDiagnostic:
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


def _knowledge_candidate_review_snapshot_projection(
    candidate: KnowledgeCandidate,
) -> dict[str, object]:
    if type(candidate) is not KnowledgeCandidate:
        raise ValueError("candidate must be an exact KnowledgeCandidate")

    support_projection = []
    for support in candidate.support:
        support_projection.append(
            {
                "acceptance_record_ids": support.acceptance_record_ids,
                "acceptance_review_record_ids": (
                    support.acceptance_review_record_ids
                ),
                "evidence_id": support.evidence_id,
                "locator_schema_version": support.locator_schema_version,
                "locator_type": support.locator_type,
                "locator_value": support.locator_value,
                "payload_digest": support.payload_digest,
                "source_authority_status": support.source_authority_status,
                "source_content_digest": support.source_content_digest,
                "source_id": support.source_id,
                "source_lifecycle_status": support.source_lifecycle_status,
            }
        )

    diagnostics_projection = []
    for diagnostic in candidate.diagnostics:
        diagnostics_projection.append(
            {
                "code": diagnostic.code,
                "field": diagnostic.field,
                "message": diagnostic.message,
                "severity": diagnostic.severity,
                "source": diagnostic.source,
            }
        )

    return _canonicalize(
        {
            "authority_status": candidate.authority_status,
            "conflict_ids": candidate.conflict_ids,
            "conflict_status": candidate.conflict_status,
            "construction_rule_id": candidate.construction_rule_id,
            "construction_rule_version": candidate.construction_rule_version,
            "contract_version": candidate.contract_version,
            "diagnostics": diagnostics_projection,
            "knowledge_candidate_id": candidate.knowledge_candidate_id,
            "lifecycle_status": candidate.lifecycle_status,
            "review_status": candidate.review_status,
            "snapshot_canonicalization_contract": (
                KNOWLEDGE_CANDIDATE_REVIEW_SNAPSHOT_CANONICALIZATION_CONTRACT
            ),
            "statement": candidate.statement,
            "statement_type": candidate.statement_type,
            "support": support_projection,
        }
    )


def _canonical_knowledge_candidate_review_snapshot_bytes(
    candidate: KnowledgeCandidate,
) -> bytes:
    projection = _knowledge_candidate_review_snapshot_projection(candidate)
    return json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_candidate_review_snapshot_digest(
    candidate: KnowledgeCandidate,
) -> str:
    return hashlib.sha256(
        _canonical_knowledge_candidate_review_snapshot_bytes(candidate)
    ).hexdigest()


@dataclass(frozen=True)
class KnowledgeReviewIdentityInput:
    review_record_contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    review_decision: str
    reason_codes: tuple[str, ...]
    reviewed_evidence_ids: tuple[str, ...]
    reviewed_acceptance_record_ids: tuple[str, ...]
    reviewed_acceptance_review_record_ids: tuple[str, ...]
    reviewed_by: str
    reviewed_at: datetime
    review_policy_id: str
    review_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.review_record_contract_version
            != KNOWLEDGE_REVIEW_RECORD_CONTRACT_VERSION
        ):
            raise ValueError("unsupported review_record_contract_version")
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
        _require_string(self.review_decision, "review_decision")
        if self.review_decision not in _REVIEW_DECISIONS:
            raise ValueError("unsupported review_decision")
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        _require_unique_ordered_strings(
            self.reviewed_evidence_ids,
            "reviewed_evidence_ids",
            pattern=_EVIDENCE_ID_PATTERN,
        )
        _require_unique_ordered_strings(
            self.reviewed_acceptance_record_ids,
            "reviewed_acceptance_record_ids",
            pattern=_ACCEPTANCE_RECORD_ID_PATTERN,
        )
        _require_unique_ordered_strings(
            self.reviewed_acceptance_review_record_ids,
            "reviewed_acceptance_review_record_ids",
        )
        for field_name in (
            "reviewed_by",
            "review_policy_id",
            "review_policy_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_aware_datetime(self.reviewed_at, "reviewed_at")


def _knowledge_review_identity_projection(
    identity_input: KnowledgeReviewIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgeReviewIdentityInput:
        raise ValueError(
            "identity_input must be an exact KnowledgeReviewIdentityInput"
        )
    return _canonicalize(
        {
            "candidate_snapshot_canonicalization_contract": (
                KNOWLEDGE_CANDIDATE_REVIEW_SNAPSHOT_CANONICALIZATION_CONTRACT
            ),
            "identity_canonicalization_contract": (
                KNOWLEDGE_REVIEW_IDENTITY_CANONICALIZATION_CONTRACT
            ),
            "knowledge_candidate_contract_version": (
                identity_input.knowledge_candidate_contract_version
            ),
            "knowledge_candidate_id": identity_input.knowledge_candidate_id,
            "knowledge_candidate_snapshot_digest": (
                identity_input.knowledge_candidate_snapshot_digest
            ),
            "reason_codes": identity_input.reason_codes,
            "review_decision": identity_input.review_decision,
            "review_policy_id": identity_input.review_policy_id,
            "review_policy_version": identity_input.review_policy_version,
            "review_record_contract_version": (
                identity_input.review_record_contract_version
            ),
            "reviewed_acceptance_record_ids": (
                identity_input.reviewed_acceptance_record_ids
            ),
            "reviewed_acceptance_review_record_ids": (
                identity_input.reviewed_acceptance_review_record_ids
            ),
            "reviewed_at": _format_reviewed_at(identity_input.reviewed_at),
            "reviewed_by": identity_input.reviewed_by,
            "reviewed_evidence_ids": identity_input.reviewed_evidence_ids,
        }
    )


def canonical_knowledge_review_identity_bytes(
    identity_input: KnowledgeReviewIdentityInput,
) -> bytes:
    projection = _knowledge_review_identity_projection(identity_input)
    return json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_review_record_id(
    identity_input: KnowledgeReviewIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_review_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_REVIEW_RECORD_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgeReviewRecord:
    knowledge_review_record_id: str
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    review_decision: str
    reason_codes: tuple[str, ...]
    reviewed_evidence_ids: tuple[str, ...]
    reviewed_acceptance_record_ids: tuple[str, ...]
    reviewed_acceptance_review_record_ids: tuple[str, ...]
    reviewed_by: str
    reviewed_at: datetime
    review_policy_id: str
    review_policy_version: str
    diagnostics: tuple[KnowledgeReviewDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.knowledge_review_record_id,
            "knowledge_review_record_id",
            _REVIEW_RECORD_ID_PATTERN,
        )
        identity_input = KnowledgeReviewIdentityInput(
            review_record_contract_version=self.contract_version,
            knowledge_candidate_id=self.knowledge_candidate_id,
            knowledge_candidate_contract_version=(
                self.knowledge_candidate_contract_version
            ),
            knowledge_candidate_snapshot_digest=(
                self.knowledge_candidate_snapshot_digest
            ),
            review_decision=self.review_decision,
            reason_codes=self.reason_codes,
            reviewed_evidence_ids=self.reviewed_evidence_ids,
            reviewed_acceptance_record_ids=self.reviewed_acceptance_record_ids,
            reviewed_acceptance_review_record_ids=(
                self.reviewed_acceptance_review_record_ids
            ),
            reviewed_by=self.reviewed_by,
            reviewed_at=self.reviewed_at,
            review_policy_id=self.review_policy_id,
            review_policy_version=self.review_policy_version,
        )
        diagnostics = _require_tuple(self.diagnostics, "diagnostics")
        for index, diagnostic in enumerate(diagnostics):
            if type(diagnostic) is not KnowledgeReviewDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact "
                    "KnowledgeReviewDiagnostic"
                )
        if self.knowledge_review_record_id != compute_knowledge_review_record_id(
            identity_input
        ):
            raise ValueError("knowledge_review_record_id does not match identity")


def knowledge_review_identity_input_from_record(
    record: KnowledgeReviewRecord,
) -> KnowledgeReviewIdentityInput:
    if type(record) is not KnowledgeReviewRecord:
        raise ValueError("record must be an exact KnowledgeReviewRecord")
    return KnowledgeReviewIdentityInput(
        review_record_contract_version=record.contract_version,
        knowledge_candidate_id=record.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            record.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=(
            record.knowledge_candidate_snapshot_digest
        ),
        review_decision=record.review_decision,
        reason_codes=record.reason_codes,
        reviewed_evidence_ids=record.reviewed_evidence_ids,
        reviewed_acceptance_record_ids=record.reviewed_acceptance_record_ids,
        reviewed_acceptance_review_record_ids=(
            record.reviewed_acceptance_review_record_ids
        ),
        reviewed_by=record.reviewed_by,
        reviewed_at=record.reviewed_at,
        review_policy_id=record.review_policy_id,
        review_policy_version=record.review_policy_version,
    )
