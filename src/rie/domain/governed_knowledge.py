from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import unicodedata

from rie.domain.knowledge_candidate import (
    KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
    KnowledgeEvidenceSupport,
)
from rie.domain.knowledge_promotion_decision import (
    KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION,
    PROMOTION_DECISION_AUTHORIZATION_SCOPE,
    PROMOTION_DECISION_OUTCOME_AUTHORIZED,
)
from rie.domain.knowledge_promotion_execution import (
    KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION,
    PROMOTION_EXECUTION_OUTCOME_COMPLETED,
    PROMOTION_EXECUTION_SCOPE_DECLARED,
)
from rie.domain.knowledge_promotion_prerequisite_evaluation import (
    KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION,
)


GOVERNED_KNOWLEDGE_CONTRACT_VERSION = "governed-knowledge-v1"
GOVERNED_KNOWLEDGE_ID_PREFIX = "gk1_"
GOVERNED_KNOWLEDGE_IDENTITY_POLICY_ID = "rcis-governed-knowledge-identity"
GOVERNED_KNOWLEDGE_IDENTITY_POLICY_VERSION = "1.0.0"
GOVERNED_KNOWLEDGE_CANONICALIZATION_VERSION = (
    "rcis-governed-knowledge-canonical-json-v1"
)
GOVERNED_KNOWLEDGE_DIGEST_ALGORITHM = "sha256"
GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE = (
    "governed_knowledge_construction_for_declared_scope"
)
REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON = (
    "governed_knowledge_constructed_from_completed_promotion_execution"
)


_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_GOVERNED_KNOWLEDGE_ID_PATTERN = re.compile(r"^gk1_[0-9a-f]{64}$")
_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
_EVALUATION_ID_PATTERN = re.compile(r"^kpe1_[0-9a-f]{64}$")
_DECISION_ID_PATTERN = re.compile(r"^kpd1_[0-9a-f]{64}$")
_EXECUTION_ID_PATTERN = re.compile(r"^kpx1_[0-9a-f]{64}$")
_DIAGNOSTIC_SEVERITIES = frozenset(("info", "warning"))


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be an exact non-empty string")


def _require_pattern(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> None:
    _require_string(value, field_name)
    if pattern.fullmatch(value) is None:  # type: ignore[arg-type]
        raise ValueError(f"{field_name} has an invalid format")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_unique_ordered_strings(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise ValueError(f"{field_name} must be a non-empty tuple")
    for item in value:
        _require_string(item, field_name)
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must contain unique values")
    if tuple(sorted(value)) != value:
        raise ValueError(f"{field_name} must be lexicographically ordered")
    return value  # type: ignore[return-value]


def _require_support(value: object) -> tuple[KnowledgeEvidenceSupport, ...]:
    if type(value) is not tuple or not value:
        raise ValueError("support must be a non-empty tuple")
    evidence_ids: list[str] = []
    for index, item in enumerate(value):
        if type(item) is not KnowledgeEvidenceSupport:
            raise ValueError(
                f"support[{index}] must be an exact KnowledgeEvidenceSupport"
            )
        item.__post_init__()
        evidence_ids.append(item.evidence_id)
    if len(set(evidence_ids)) != len(evidence_ids):
        raise ValueError("support must contain unique Evidence IDs")
    if evidence_ids != sorted(evidence_ids):
        raise ValueError("support must be ordered by Evidence ID")
    return value  # type: ignore[return-value]


def _normalize_text(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def _format_constructed_at(value: datetime) -> str:
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
            normalized_key = _normalize_text(key)
            if normalized_key in result:
                raise ValueError("canonical mapping keys must remain unique")
            result[normalized_key] = _canonicalize(item)
        return result
    raise ValueError("unsupported canonical value")


@dataclass(frozen=True)
class GovernedKnowledgeDiagnostic:
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
class GovernedKnowledgeIdentityInput:
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    statement_type: str
    statement: str
    support: tuple[KnowledgeEvidenceSupport, ...]
    knowledge_promotion_prerequisite_evaluation_id: str
    knowledge_promotion_prerequisite_evaluation_contract_version: str
    knowledge_promotion_decision_id: str
    knowledge_promotion_decision_contract_version: str
    promotion_decision_outcome: str
    authorization_scope: str
    knowledge_promotion_execution_id: str
    knowledge_promotion_execution_contract_version: str
    promotion_execution_scope: str
    promotion_execution_outcome: str
    construction_scope: str
    construction_reference: str
    reason_codes: tuple[str, ...]
    constructed_by: str
    constructed_at: datetime
    construction_policy_id: str
    construction_policy_version: str

    def __post_init__(self) -> None:
        if self.contract_version != GOVERNED_KNOWLEDGE_CONTRACT_VERSION:
            raise ValueError("unsupported contract_version")
        _require_pattern(
            self.knowledge_candidate_id,
            "knowledge_candidate_id",
            _CANDIDATE_ID_PATTERN,
        )
        if (
            self.knowledge_candidate_contract_version
            != KNOWLEDGE_CANDIDATE_CONTRACT_VERSION
        ):
            raise ValueError("unsupported knowledge_candidate_contract_version")
        _require_pattern(
            self.knowledge_candidate_snapshot_digest,
            "knowledge_candidate_snapshot_digest",
            _DIGEST_PATTERN,
        )
        _require_string(self.statement_type, "statement_type")
        _require_string(self.statement, "statement")
        _require_support(self.support)
        _require_pattern(
            self.knowledge_promotion_prerequisite_evaluation_id,
            "knowledge_promotion_prerequisite_evaluation_id",
            _EVALUATION_ID_PATTERN,
        )
        if (
            self.knowledge_promotion_prerequisite_evaluation_contract_version
            != KNOWLEDGE_PROMOTION_PREREQUISITE_EVALUATION_CONTRACT_VERSION
        ):
            raise ValueError(
                "unsupported "
                "knowledge_promotion_prerequisite_evaluation_contract_version"
            )
        _require_pattern(
            self.knowledge_promotion_decision_id,
            "knowledge_promotion_decision_id",
            _DECISION_ID_PATTERN,
        )
        if (
            self.knowledge_promotion_decision_contract_version
            != KNOWLEDGE_PROMOTION_DECISION_CONTRACT_VERSION
        ):
            raise ValueError(
                "unsupported knowledge_promotion_decision_contract_version"
            )
        if self.promotion_decision_outcome != PROMOTION_DECISION_OUTCOME_AUTHORIZED:
            raise ValueError("unsupported promotion_decision_outcome")
        if self.authorization_scope != PROMOTION_DECISION_AUTHORIZATION_SCOPE:
            raise ValueError("unsupported authorization_scope")
        _require_pattern(
            self.knowledge_promotion_execution_id,
            "knowledge_promotion_execution_id",
            _EXECUTION_ID_PATTERN,
        )
        if (
            self.knowledge_promotion_execution_contract_version
            != KNOWLEDGE_PROMOTION_EXECUTION_CONTRACT_VERSION
        ):
            raise ValueError(
                "unsupported knowledge_promotion_execution_contract_version"
            )
        if self.promotion_execution_scope != PROMOTION_EXECUTION_SCOPE_DECLARED:
            raise ValueError("unsupported promotion_execution_scope")
        if self.promotion_execution_outcome != PROMOTION_EXECUTION_OUTCOME_COMPLETED:
            raise ValueError("unsupported promotion_execution_outcome")
        if self.construction_scope != GOVERNED_KNOWLEDGE_CONSTRUCTION_SCOPE:
            raise ValueError("unsupported construction_scope")
        _require_string(self.construction_reference, "construction_reference")
        reasons = _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        if REQUIRED_GOVERNED_KNOWLEDGE_CONSTRUCTION_REASON not in reasons:
            raise ValueError("required governed-Knowledge construction reason missing")
        _require_string(self.constructed_by, "constructed_by")
        _require_aware_datetime(self.constructed_at, "constructed_at")
        _require_string(self.construction_policy_id, "construction_policy_id")
        _require_string(self.construction_policy_version, "construction_policy_version")


def canonical_governed_knowledge_identity_projection(
    identity_input: GovernedKnowledgeIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not GovernedKnowledgeIdentityInput:
        raise ValueError(
            "identity_input must be an exact GovernedKnowledgeIdentityInput"
        )
    support_projection = tuple(
        {
            "evidence_id": item.evidence_id,
            "acceptance_record_ids": item.acceptance_record_ids,
            "acceptance_review_record_ids": item.acceptance_review_record_ids,
            "source_id": item.source_id,
            "source_content_digest": item.source_content_digest,
            "source_authority_status": item.source_authority_status,
            "source_lifecycle_status": item.source_lifecycle_status,
            "payload_digest": item.payload_digest,
            "locator_type": item.locator_type,
            "locator_value": item.locator_value,
            "locator_schema_version": item.locator_schema_version,
        }
        for item in identity_input.support
    )
    return _canonicalize(
        {
            "contract_version": identity_input.contract_version,
            "knowledge_candidate_id": identity_input.knowledge_candidate_id,
            "knowledge_candidate_contract_version": (
                identity_input.knowledge_candidate_contract_version
            ),
            "knowledge_candidate_snapshot_digest": (
                identity_input.knowledge_candidate_snapshot_digest
            ),
            "statement_type": identity_input.statement_type,
            "statement": identity_input.statement,
            "support": support_projection,
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
            "promotion_decision_outcome": identity_input.promotion_decision_outcome,
            "authorization_scope": identity_input.authorization_scope,
            "knowledge_promotion_execution_id": (
                identity_input.knowledge_promotion_execution_id
            ),
            "knowledge_promotion_execution_contract_version": (
                identity_input.knowledge_promotion_execution_contract_version
            ),
            "promotion_execution_scope": identity_input.promotion_execution_scope,
            "promotion_execution_outcome": identity_input.promotion_execution_outcome,
            "construction_scope": identity_input.construction_scope,
            "construction_reference": identity_input.construction_reference,
            "reason_codes": identity_input.reason_codes,
            "constructed_by": identity_input.constructed_by,
            "constructed_at": _format_constructed_at(identity_input.constructed_at),
            "construction_policy_id": identity_input.construction_policy_id,
            "construction_policy_version": identity_input.construction_policy_version,
            "identity_canonicalization_contract": (
                GOVERNED_KNOWLEDGE_CANONICALIZATION_VERSION
            ),
        }
    )  # type: ignore[return-value]


def canonical_governed_knowledge_identity_bytes(
    identity_input: GovernedKnowledgeIdentityInput,
) -> bytes:
    return json.dumps(
        canonical_governed_knowledge_identity_projection(identity_input),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_governed_knowledge_id(
    identity_input: GovernedKnowledgeIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_governed_knowledge_identity_bytes(identity_input)
    ).hexdigest()
    return f"{GOVERNED_KNOWLEDGE_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class GovernedKnowledge:
    governed_knowledge_id: str
    contract_version: str
    knowledge_candidate_id: str
    knowledge_candidate_contract_version: str
    knowledge_candidate_snapshot_digest: str
    statement_type: str
    statement: str
    support: tuple[KnowledgeEvidenceSupport, ...]
    knowledge_promotion_prerequisite_evaluation_id: str
    knowledge_promotion_prerequisite_evaluation_contract_version: str
    knowledge_promotion_decision_id: str
    knowledge_promotion_decision_contract_version: str
    promotion_decision_outcome: str
    authorization_scope: str
    knowledge_promotion_execution_id: str
    knowledge_promotion_execution_contract_version: str
    promotion_execution_scope: str
    promotion_execution_outcome: str
    construction_scope: str
    construction_reference: str
    reason_codes: tuple[str, ...]
    constructed_by: str
    constructed_at: datetime
    construction_policy_id: str
    construction_policy_version: str
    diagnostics: tuple[GovernedKnowledgeDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.governed_knowledge_id,
            "governed_knowledge_id",
            _GOVERNED_KNOWLEDGE_ID_PATTERN,
        )
        if type(self.diagnostics) is not tuple:
            raise ValueError("diagnostics must be a tuple")
        for index, diagnostic in enumerate(self.diagnostics):
            if type(diagnostic) is not GovernedKnowledgeDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact "
                    "GovernedKnowledgeDiagnostic"
                )
            diagnostic.__post_init__()
        identity_input = governed_knowledge_identity_input_from_record(self)
        if self.governed_knowledge_id != compute_governed_knowledge_id(identity_input):
            raise ValueError("governed_knowledge_id does not match identity")


def governed_knowledge_identity_input_from_record(
    record: GovernedKnowledge,
) -> GovernedKnowledgeIdentityInput:
    if type(record) is not GovernedKnowledge:
        raise ValueError("record must be an exact GovernedKnowledge")
    return GovernedKnowledgeIdentityInput(
        contract_version=record.contract_version,
        knowledge_candidate_id=record.knowledge_candidate_id,
        knowledge_candidate_contract_version=(
            record.knowledge_candidate_contract_version
        ),
        knowledge_candidate_snapshot_digest=record.knowledge_candidate_snapshot_digest,
        statement_type=record.statement_type,
        statement=record.statement,
        support=record.support,
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
        knowledge_promotion_execution_id=record.knowledge_promotion_execution_id,
        knowledge_promotion_execution_contract_version=(
            record.knowledge_promotion_execution_contract_version
        ),
        promotion_execution_scope=record.promotion_execution_scope,
        promotion_execution_outcome=record.promotion_execution_outcome,
        construction_scope=record.construction_scope,
        construction_reference=record.construction_reference,
        reason_codes=record.reason_codes,
        constructed_by=record.constructed_by,
        constructed_at=record.constructed_at,
        construction_policy_id=record.construction_policy_id,
        construction_policy_version=record.construction_policy_version,
    )
