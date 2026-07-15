from dataclasses import dataclass as _dataclass
import hashlib as _hashlib
import json as _json
import math as _math
import re as _re
import unicodedata as _unicodedata

from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION as _GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
)
from rie.domain.governed_knowledge_acceptance_decision import (
    GOVERNED_KNOWLEDGE_ACCEPTANCE_DECISION_CONTRACT_VERSION as _ACCEPTANCE_DECISION_CONTRACT_VERSION,
    GOVERNED_KNOWLEDGE_ACCEPTANCE_SCOPE_DECLARED as _ACCEPTANCE_SCOPE_DECLARED,
)


GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_CONTRACT_VERSION = (
    "governed-knowledge-acceptance-history-interpretation-v1"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_ID_PREFIX = "gkai1_"
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_IDENTITY_POLICY_ID = (
    "rcis-governed-knowledge-acceptance-history-interpretation-identity"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_IDENTITY_POLICY_VERSION = "1.0.0"
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_IDENTITY_CANONICALIZATION_CONTRACT = (
    "rcis-governed-knowledge-acceptance-history-interpretation-canonical-json-v1"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIGEST_ALGORITHM = "sha256"
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_COMPLETENESS_SCOPE_CALLER_ASSERTED_COMPLETE_BOUNDED_SUBJECT_HISTORY = (
    "caller_asserted_complete_bounded_subject_history"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_NO_DECISIONS = (
    "no_decisions"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_ONLY = (
    "accepted_only"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_ONLY = (
    "rejected_only"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_DEFERRED_ONLY = (
    "deferred_only"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_REJECTED = (
    "accepted_and_rejected"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_DEFERRED = (
    "accepted_and_deferred"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_AND_DEFERRED = (
    "rejected_and_deferred"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_REJECTED_AND_DEFERRED = (
    "accepted_rejected_and_deferred"
)
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIAGNOSTIC_SEVERITY_INFO = "info"
GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIAGNOSTIC_SEVERITY_WARNING = (
    "warning"
)


_GOVERNED_KNOWLEDGE_ID_PATTERN = _re.compile(r"^gk1_[0-9a-f]{64}$")
_ACCEPTANCE_DECISION_ID_PATTERN = _re.compile(r"^gka1_[0-9a-f]{64}$")
_INTERPRETATION_ID_PATTERN = _re.compile(r"^gkai1_[0-9a-f]{64}$")
_OUTCOME_COMPOSITIONS = frozenset(
    (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_NO_DECISIONS,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_ONLY,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_ONLY,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_DEFERRED_ONLY,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_REJECTED,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_AND_DEFERRED,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_REJECTED_AND_DEFERRED,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_OUTCOME_COMPOSITION_ACCEPTED_REJECTED_AND_DEFERRED,
    )
)
_DIAGNOSTIC_SEVERITIES = frozenset(
    (
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIAGNOSTIC_SEVERITY_INFO,
        GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_DIAGNOSTIC_SEVERITY_WARNING,
    )
)


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be an exact non-empty string")


def _require_pattern(value: object, field_name: str, pattern: object) -> None:
    _require_string(value, field_name)
    if pattern.fullmatch(value) is None:  # type: ignore[union-attr]
        raise ValueError(f"{field_name} has an invalid format")


def _require_decision_ids(value: object) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise ValueError("acceptance_decision_ids must be a tuple")
    for item in value:
        _require_pattern(item, "acceptance_decision_ids", _ACCEPTANCE_DECISION_ID_PATTERN)
    if len(set(value)) != len(value):
        raise ValueError("acceptance_decision_ids must contain unique values")
    if tuple(sorted(value)) != value:
        raise ValueError("acceptance_decision_ids must be lexicographically ordered")
    return value  # type: ignore[return-value]


def _canonicalize(value: object) -> object:
    if value is None or type(value) in (bool, int):
        return value
    if type(value) is float:
        if not _math.isfinite(value):
            raise ValueError("canonical values must be finite")
        return value
    if type(value) is str:
        return _unicodedata.normalize("NFC", value)
    if type(value) in (tuple, list):
        return [_canonicalize(item) for item in value]
    if type(value) is dict:
        result: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("canonical mapping keys must be strings")
            normalized_key = _unicodedata.normalize("NFC", key)
            if normalized_key in result:
                raise ValueError("canonical mapping keys must remain unique")
            result[normalized_key] = _canonicalize(item)
        return result
    raise ValueError("unsupported canonical value")


@_dataclass(frozen=True)
class GovernedKnowledgeAcceptanceHistoryInterpretationDiagnostic:
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


@_dataclass(frozen=True)
class GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput:
    contract_version: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    acceptance_scope: str
    acceptance_scope_reference: str
    acceptance_decision_contract_version: str
    acceptance_decision_ids: tuple[str, ...]
    completeness_scope: str
    completeness_reference: str
    outcome_composition: str
    interpretation_policy_id: str
    interpretation_policy_version: str

    def __post_init__(self) -> None:
        _require_string(self.contract_version, "contract_version")
        if (
            self.contract_version
            != GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_CONTRACT_VERSION
        ):
            raise ValueError("unsupported contract_version")
        _require_pattern(
            self.governed_knowledge_id,
            "governed_knowledge_id",
            _GOVERNED_KNOWLEDGE_ID_PATTERN,
        )
        _require_string(
            self.governed_knowledge_contract_version,
            "governed_knowledge_contract_version",
        )
        if self.governed_knowledge_contract_version != _GOVERNED_KNOWLEDGE_CONTRACT_VERSION:
            raise ValueError("unsupported governed_knowledge_contract_version")
        _require_string(self.acceptance_scope, "acceptance_scope")
        if self.acceptance_scope != _ACCEPTANCE_SCOPE_DECLARED:
            raise ValueError("unsupported acceptance_scope")
        _require_string(self.acceptance_scope_reference, "acceptance_scope_reference")
        _require_string(
            self.acceptance_decision_contract_version,
            "acceptance_decision_contract_version",
        )
        if self.acceptance_decision_contract_version != _ACCEPTANCE_DECISION_CONTRACT_VERSION:
            raise ValueError("unsupported acceptance_decision_contract_version")
        _require_decision_ids(self.acceptance_decision_ids)
        _require_string(self.completeness_scope, "completeness_scope")
        if (
            self.completeness_scope
            != GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_COMPLETENESS_SCOPE_CALLER_ASSERTED_COMPLETE_BOUNDED_SUBJECT_HISTORY
        ):
            raise ValueError("unsupported completeness_scope")
        _require_string(self.completeness_reference, "completeness_reference")
        if type(self.outcome_composition) is not str or self.outcome_composition not in _OUTCOME_COMPOSITIONS:
            raise ValueError("unsupported outcome_composition")
        _require_string(self.interpretation_policy_id, "interpretation_policy_id")
        _require_string(
            self.interpretation_policy_version,
            "interpretation_policy_version",
        )


def canonical_governed_knowledge_acceptance_history_interpretation_identity_projection(
    identity_input: GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput"
        )
    identity_input.__post_init__()
    return _canonicalize(
        {
            "contract_version": identity_input.contract_version,
            "governed_knowledge_id": identity_input.governed_knowledge_id,
            "governed_knowledge_contract_version": identity_input.governed_knowledge_contract_version,
            "acceptance_scope": identity_input.acceptance_scope,
            "acceptance_scope_reference": identity_input.acceptance_scope_reference,
            "acceptance_decision_contract_version": identity_input.acceptance_decision_contract_version,
            "acceptance_decision_ids": identity_input.acceptance_decision_ids,
            "completeness_scope": identity_input.completeness_scope,
            "completeness_reference": identity_input.completeness_reference,
            "outcome_composition": identity_input.outcome_composition,
            "interpretation_policy_id": identity_input.interpretation_policy_id,
            "interpretation_policy_version": identity_input.interpretation_policy_version,
            "identity_canonicalization_contract": GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_IDENTITY_CANONICALIZATION_CONTRACT,
        }
    )  # type: ignore[return-value]


def canonical_governed_knowledge_acceptance_history_interpretation_identity_bytes(
    identity_input: GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput,
) -> bytes:
    if type(identity_input) is not GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput"
        )
    return _json.dumps(
        canonical_governed_knowledge_acceptance_history_interpretation_identity_projection(
            identity_input
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_governed_knowledge_acceptance_history_interpretation_id(
    identity_input: GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput,
) -> str:
    if type(identity_input) is not GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput"
        )
    digest = _hashlib.sha256(
        canonical_governed_knowledge_acceptance_history_interpretation_identity_bytes(
            identity_input
        )
    ).hexdigest()
    return f"{GOVERNED_KNOWLEDGE_ACCEPTANCE_HISTORY_INTERPRETATION_ID_PREFIX}{digest}"


@_dataclass(frozen=True)
class GovernedKnowledgeAcceptanceHistoryInterpretation:
    governed_knowledge_acceptance_history_interpretation_id: str
    contract_version: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    acceptance_scope: str
    acceptance_scope_reference: str
    acceptance_decision_contract_version: str
    acceptance_decision_ids: tuple[str, ...]
    completeness_scope: str
    completeness_reference: str
    outcome_composition: str
    interpretation_policy_id: str
    interpretation_policy_version: str
    diagnostics: tuple[GovernedKnowledgeAcceptanceHistoryInterpretationDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.governed_knowledge_acceptance_history_interpretation_id,
            "governed_knowledge_acceptance_history_interpretation_id",
            _INTERPRETATION_ID_PATTERN,
        )
        if type(self.diagnostics) is not tuple:
            raise ValueError("diagnostics must be a tuple")
        for index, diagnostic in enumerate(self.diagnostics):
            if type(diagnostic) is not GovernedKnowledgeAcceptanceHistoryInterpretationDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact "
                    "GovernedKnowledgeAcceptanceHistoryInterpretationDiagnostic"
                )
            diagnostic.__post_init__()
        identity_input = governed_knowledge_acceptance_history_interpretation_identity_input_from_record(
            self
        )
        if self.governed_knowledge_acceptance_history_interpretation_id != (
            compute_governed_knowledge_acceptance_history_interpretation_id(
                identity_input
            )
        ):
            raise ValueError(
                "governed_knowledge_acceptance_history_interpretation_id does not match identity"
            )


def governed_knowledge_acceptance_history_interpretation_identity_input_from_record(
    record: GovernedKnowledgeAcceptanceHistoryInterpretation,
) -> GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput:
    if type(record) is not GovernedKnowledgeAcceptanceHistoryInterpretation:
        raise ValueError(
            "record must be an exact "
            "GovernedKnowledgeAcceptanceHistoryInterpretation"
        )
    return GovernedKnowledgeAcceptanceHistoryInterpretationIdentityInput(
        contract_version=record.contract_version,
        governed_knowledge_id=record.governed_knowledge_id,
        governed_knowledge_contract_version=record.governed_knowledge_contract_version,
        acceptance_scope=record.acceptance_scope,
        acceptance_scope_reference=record.acceptance_scope_reference,
        acceptance_decision_contract_version=record.acceptance_decision_contract_version,
        acceptance_decision_ids=record.acceptance_decision_ids,
        completeness_scope=record.completeness_scope,
        completeness_reference=record.completeness_reference,
        outcome_composition=record.outcome_composition,
        interpretation_policy_id=record.interpretation_policy_id,
        interpretation_policy_version=record.interpretation_policy_version,
    )
