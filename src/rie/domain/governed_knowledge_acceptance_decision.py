from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import unicodedata

from rie.domain.governed_knowledge import GOVERNED_KNOWLEDGE_CONTRACT_VERSION


GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION = (
    "governed-knowledge-acceptance-decision-v1"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_ID_PREFIX = "gka1_"
GOVERNED_KNOWLEDGE_ACCEPTANCE_IDENTITY_POLICY_ID = (
    "rcis-governed-knowledge-acceptance-decision-identity"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_IDENTITY_POLICY_VERSION = "1.0.0"
GOVERNED_KNOWLEDGE_ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT = (
    "rcis-governed-knowledge-acceptance-decision-canonical-json-v1"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_DIGEST_ALGORITHM = "sha256"
GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED = (
    "governed_knowledge_acceptance_for_declared_scope"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED = "accepted"
GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED = "rejected"
GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED = "deferred"
GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE = (
    "governed_knowledge_accepted_for_declared_scope"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE = (
    "governed_knowledge_rejected_for_declared_scope"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE = (
    "governed_knowledge_acceptance_deferred_for_declared_scope"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_DIAGNOSTIC_SEVERITY_INFO = "info"
GOVERNED_KNOWLEDGE_ACCEPTANCE_DIAGNOSTIC_SEVERITY_WARNING = "warning"


_GOVERNED_KNOWLEDGE_ID_PATTERN = re.compile(r"^gk1_[0-9a-f]{64}$")
_ACCEPTANCE_DECISION_ID_PATTERN = re.compile(r"^gka1_[0-9a-f]{64}$")
_OUTCOMES = frozenset(
    (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED,
    )
)
_REQUIRED_REASON_BY_OUTCOME = {
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_ACCEPTED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_ACCEPTED_FOR_DECLARED_SCOPE
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_REJECTED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_REJECTED_FOR_DECLARED_SCOPE
    ),
    GOVERNED_KNOWLEDGE_ACCEPTANCE_OUTCOME_DEFERRED: (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_REASON_DEFERRED_FOR_DECLARED_SCOPE
    ),
}
_DIAGNOSTIC_SEVERITIES = frozenset(
    (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_DIAGNOSTIC_SEVERITY_INFO,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_DIAGNOSTIC_SEVERITY_WARNING,
    )
)


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be an exact non-empty string")


def _require_pattern(value: object, field_name: str, pattern: re.Pattern[str]) -> None:
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


def _canonicalize(value: object) -> object:
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("canonical values must be finite")
        return value
    if type(value) is str:
        return unicodedata.normalize("NFC", value)
    if type(value) in (tuple, list):
        return [_canonicalize(item) for item in value]
    if type(value) is dict:
        result: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("canonical mapping keys must be strings")
            normalized_key = unicodedata.normalize("NFC", key)
            if normalized_key in result:
                raise ValueError("canonical mapping keys must remain unique")
            result[normalized_key] = _canonicalize(item)
        return result
    raise ValueError("unsupported canonical value")


def _format_decided_at(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(
        timespec="microseconds"
    ).replace("+00:00", "Z")


@dataclass(frozen=True)
class GovernedKnowledgeAcceptanceDiagnostic:
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
class GovernedKnowledgeAcceptanceDecisionIdentityInput:
    contract_version: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    acceptance_scope: str
    acceptance_scope_reference: str
    acceptance_outcome: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    acceptance_policy_id: str
    acceptance_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION
        ):
            raise ValueError("unsupported contract_version")
        _require_pattern(
            self.governed_knowledge_id,
            "governed_knowledge_id",
            _GOVERNED_KNOWLEDGE_ID_PATTERN,
        )
        if self.governed_knowledge_contract_version != GOVERNED_KNOWLEDGE_CONTRACT_VERSION:
            raise ValueError("unsupported governed_knowledge_contract_version")
        if self.acceptance_scope != GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED:
            raise ValueError("unsupported acceptance_scope")
        _require_string(self.acceptance_scope_reference, "acceptance_scope_reference")
        if type(self.acceptance_outcome) is not str or self.acceptance_outcome not in _OUTCOMES:
            raise ValueError("unsupported acceptance_outcome")
        reasons = _require_unique_ordered_strings(self.reason_codes, "reason_codes")
        if _REQUIRED_REASON_BY_OUTCOME[self.acceptance_outcome] not in reasons:
            raise ValueError("required acceptance reason missing")
        _require_string(self.decided_by, "decided_by")
        _require_aware_datetime(self.decided_at, "decided_at")
        _require_string(self.acceptance_policy_id, "acceptance_policy_id")
        _require_string(self.acceptance_policy_version, "acceptance_policy_version")


def canonical_governed_knowledge_acceptance_decision_identity_projection(
    identity_input: GovernedKnowledgeAcceptanceDecisionIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not GovernedKnowledgeAcceptanceDecisionIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeAcceptanceDecisionIdentityInput"
        )
    identity_input.__post_init__()
    return _canonicalize(
        {
            "contract_version": identity_input.contract_version,
            "governed_knowledge_id": identity_input.governed_knowledge_id,
            "governed_knowledge_contract_version": (
                identity_input.governed_knowledge_contract_version
            ),
            "acceptance_scope": identity_input.acceptance_scope,
            "acceptance_scope_reference": identity_input.acceptance_scope_reference,
            "acceptance_outcome": identity_input.acceptance_outcome,
            "reason_codes": identity_input.reason_codes,
            "decided_by": identity_input.decided_by,
            "decided_at": _format_decided_at(identity_input.decided_at),
            "acceptance_policy_id": identity_input.acceptance_policy_id,
            "acceptance_policy_version": identity_input.acceptance_policy_version,
            "identity_canonicalization_contract": (
                GOVERNED_KNOWLEDGE_ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT
            ),
        }
    )  # type: ignore[return-value]


def canonical_governed_knowledge_acceptance_decision_identity_bytes(
    identity_input: GovernedKnowledgeAcceptanceDecisionIdentityInput,
) -> bytes:
    if type(identity_input) is not GovernedKnowledgeAcceptanceDecisionIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeAcceptanceDecisionIdentityInput"
        )
    return json.dumps(
        canonical_governed_knowledge_acceptance_decision_identity_projection(
            identity_input
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_governed_knowledge_acceptance_decision_id(
    identity_input: GovernedKnowledgeAcceptanceDecisionIdentityInput,
) -> str:
    if type(identity_input) is not GovernedKnowledgeAcceptanceDecisionIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeAcceptanceDecisionIdentityInput"
        )
    digest = hashlib.sha256(
        canonical_governed_knowledge_acceptance_decision_identity_bytes(identity_input)
    ).hexdigest()
    return f"{GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class GovernedKnowledgeAcceptanceDecision:
    governed_knowledge_acceptance_decision_id: str
    contract_version: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    acceptance_scope: str
    acceptance_scope_reference: str
    acceptance_outcome: str
    reason_codes: tuple[str, ...]
    decided_by: str
    decided_at: datetime
    acceptance_policy_id: str
    acceptance_policy_version: str
    diagnostics: tuple[GovernedKnowledgeAcceptanceDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.governed_knowledge_acceptance_decision_id,
            "governed_knowledge_acceptance_decision_id",
            _ACCEPTANCE_DECISION_ID_PATTERN,
        )
        if type(self.diagnostics) is not tuple:
            raise ValueError("diagnostics must be a tuple")
        for index, diagnostic in enumerate(self.diagnostics):
            if type(diagnostic) is not GovernedKnowledgeAcceptanceDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact "
                    "GovernedKnowledgeAcceptanceDiagnostic"
                )
            diagnostic.__post_init__()
        identity_input = governed_knowledge_acceptance_decision_identity_input_from_record(
            self
        )
        if self.governed_knowledge_acceptance_decision_id != (
            compute_governed_knowledge_acceptance_decision_id(identity_input)
        ):
            raise ValueError(
                "governed_knowledge_acceptance_decision_id does not match identity"
            )


def governed_knowledge_acceptance_decision_identity_input_from_record(
    record: GovernedKnowledgeAcceptanceDecision,
) -> GovernedKnowledgeAcceptanceDecisionIdentityInput:
    if type(record) is not GovernedKnowledgeAcceptanceDecision:
        raise ValueError(
            "record must be an exact GovernedKnowledgeAcceptanceDecision"
        )
    return GovernedKnowledgeAcceptanceDecisionIdentityInput(
        contract_version=record.contract_version,
        governed_knowledge_id=record.governed_knowledge_id,
        governed_knowledge_contract_version=(
            record.governed_knowledge_contract_version
        ),
        acceptance_scope=record.acceptance_scope,
        acceptance_scope_reference=record.acceptance_scope_reference,
        acceptance_outcome=record.acceptance_outcome,
        reason_codes=record.reason_codes,
        decided_by=record.decided_by,
        decided_at=record.decided_at,
        acceptance_policy_id=record.acceptance_policy_id,
        acceptance_policy_version=record.acceptance_policy_version,
    )
