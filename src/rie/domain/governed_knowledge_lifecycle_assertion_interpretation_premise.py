from dataclasses import dataclass as _dataclass
from datetime import datetime as _datetime, timezone as _timezone
import hashlib as _hashlib
import json as _json
import math as _math
import re as _re
import unicodedata as _unicodedata

from rie.domain.governed_knowledge import (
    GOVERNED_KNOWLEDGE_CONTRACT_VERSION as _GOVERNED_KNOWLEDGE_CONTRACT_VERSION,
)
from rie.domain.governed_knowledge_lifecycle_assertion import (
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION as _GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION,
    GovernedKnowledgeLifecycleAssertion as _GovernedKnowledgeLifecycleAssertion,
)


GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_CONTRACT_VERSION = (
    "governed-knowledge-lifecycle-assertion-interpretation-premise-v1"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX = (
    "gklaip1_"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_POLICY_ID = (
    "rcis-governed-knowledge-lifecycle-assertion-interpretation-premise-identity"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_POLICY_VERSION = (
    "1.0.0"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_CANONICALIZATION_CONTRACT = (
    "rcis-governed-knowledge-lifecycle-assertion-interpretation-premise-canonical-json-v1"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_DIGEST_ALGORITHM = (
    "sha256"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_SCOPE_DECLARED = (
    "governed_knowledge_lifecycle_assertion_interpretation_for_declared_subject"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE = (
    "complete_for_declared_scope"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_INCOMPLETE = (
    "incomplete_for_declared_scope"
)


_GOVERNED_KNOWLEDGE_ID_PATTERN = _re.compile(r"^gk1_[0-9a-f]{64}$")
_PREMISE_ID_PATTERN = _re.compile(r"^gklaip1_[0-9a-f]{64}$")


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be an exact non-empty string")


def _require_pattern(
    value: object,
    field_name: str,
    pattern: _re.Pattern[str],
) -> None:
    _require_string(value, field_name)
    if pattern.fullmatch(value) is None:  # type: ignore[arg-type]
        raise ValueError(f"{field_name} has an invalid format")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not _datetime:
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


def _format_declared_at(value: _datetime) -> str:
    return value.astimezone(_timezone.utc).isoformat(
        timespec="microseconds"
    ).replace("+00:00", "Z")


def _validate_assertions(
    value: object,
    governed_knowledge_id: str,
    governed_knowledge_contract_version: str,
) -> tuple[_GovernedKnowledgeLifecycleAssertion, ...]:
    if type(value) is not tuple:
        raise ValueError("assertions must be an exact tuple")

    assertion_ids: list[str] = []
    for assertion in value:
        if type(assertion) is not _GovernedKnowledgeLifecycleAssertion:
            raise ValueError(
                "assertions must contain exact "
                "GovernedKnowledgeLifecycleAssertion records"
            )
        assertion.__post_init__()
        if assertion.governed_knowledge_id != governed_knowledge_id:
            raise ValueError("assertions must match governed_knowledge_id")
        if (
            assertion.governed_knowledge_contract_version
            != governed_knowledge_contract_version
        ):
            raise ValueError(
                "assertions must match governed_knowledge_contract_version"
            )
        if (
            assertion.contract_version
            != _GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION
        ):
            raise ValueError(
                "assertions must use supported lifecycle assertion "
                "contract_version"
            )
        assertion_ids.append(
            assertion.governed_knowledge_lifecycle_assertion_id
        )

    if len(set(assertion_ids)) != len(assertion_ids):
        raise ValueError(
            "assertions must contain unique lifecycle assertion IDs"
        )
    if tuple(sorted(assertion_ids)) != tuple(assertion_ids):
        raise ValueError(
            "assertions must be lexicographically ordered by "
            "lifecycle assertion ID"
        )
    return value  # type: ignore[return-value]


@_dataclass(frozen=True)
class GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput:
    contract_version: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    premise_scope: str
    premise_scope_reference: str
    completeness_declaration: str
    assertions: tuple[_GovernedKnowledgeLifecycleAssertion, ...]
    declared_by: str
    declared_at: _datetime
    declaration_policy_id: str
    declaration_policy_version: str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_CONTRACT_VERSION
        ):
            raise ValueError("unsupported contract_version")
        _require_pattern(
            self.governed_knowledge_id,
            "governed_knowledge_id",
            _GOVERNED_KNOWLEDGE_ID_PATTERN,
        )
        if (
            self.governed_knowledge_contract_version
            != _GOVERNED_KNOWLEDGE_CONTRACT_VERSION
        ):
            raise ValueError("unsupported governed_knowledge_contract_version")
        if (
            self.premise_scope
            != GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_SCOPE_DECLARED
        ):
            raise ValueError("unsupported premise_scope")
        _require_string(
            self.premise_scope_reference,
            "premise_scope_reference",
        )
        if self.completeness_declaration not in (
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE,
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_INCOMPLETE,
        ):
            raise ValueError("unsupported completeness_declaration")
        _validate_assertions(
            self.assertions,
            self.governed_knowledge_id,
            self.governed_knowledge_contract_version,
        )
        _require_string(self.declared_by, "declared_by")
        _require_aware_datetime(self.declared_at, "declared_at")
        _require_string(
            self.declaration_policy_id,
            "declaration_policy_id",
        )
        _require_string(
            self.declaration_policy_version,
            "declaration_policy_version",
        )
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")


def canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection(
    identity_input: GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput,
) -> dict[str, object]:
    if (
        type(identity_input)
        is not GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput
    ):
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput"
        )
    identity_input.__post_init__()
    return _canonicalize(
        {
            "contract_version": identity_input.contract_version,
            "governed_knowledge_id": identity_input.governed_knowledge_id,
            "governed_knowledge_contract_version": (
                identity_input.governed_knowledge_contract_version
            ),
            "premise_scope": identity_input.premise_scope,
            "premise_scope_reference": identity_input.premise_scope_reference,
            "completeness_declaration": (
                identity_input.completeness_declaration
            ),
            "assertion_ids": tuple(
                assertion.governed_knowledge_lifecycle_assertion_id
                for assertion in identity_input.assertions
            ),
            "declared_by": identity_input.declared_by,
            "declared_at": _format_declared_at(identity_input.declared_at),
            "declaration_policy_id": identity_input.declaration_policy_id,
            "declaration_policy_version": (
                identity_input.declaration_policy_version
            ),
            "reason_codes": identity_input.reason_codes,
            "identity_canonicalization_contract": (
                GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_CANONICALIZATION_CONTRACT
            ),
        }
    )  # type: ignore[return-value]


def canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_bytes(
    identity_input: GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput,
) -> bytes:
    if (
        type(identity_input)
        is not GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput
    ):
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput"
        )
    return _json.dumps(
        canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection(
            identity_input
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
    identity_input: GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput,
) -> str:
    if (
        type(identity_input)
        is not GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput
    ):
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput"
        )
    digest = _hashlib.sha256(
        canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_bytes(
            identity_input
        )
    ).hexdigest()
    return (
        f"{GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX}"
        f"{digest}"
    )


@_dataclass(frozen=True)
class GovernedKnowledgeLifecycleAssertionInterpretationPremise:
    governed_knowledge_lifecycle_assertion_interpretation_premise_id: str
    contract_version: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    premise_scope: str
    premise_scope_reference: str
    completeness_declaration: str
    assertions: tuple[_GovernedKnowledgeLifecycleAssertion, ...]
    declared_by: str
    declared_at: _datetime
    declaration_policy_id: str
    declaration_policy_version: str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.governed_knowledge_lifecycle_assertion_interpretation_premise_id,
            "governed_knowledge_lifecycle_assertion_interpretation_premise_id",
            _PREMISE_ID_PATTERN,
        )
        identity_input = (
            governed_knowledge_lifecycle_assertion_interpretation_premise_identity_input_from_record(
                self
            )
        )
        if (
            self.governed_knowledge_lifecycle_assertion_interpretation_premise_id
            != compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
                identity_input
            )
        ):
            raise ValueError(
                "governed_knowledge_lifecycle_assertion_interpretation_premise_id "
                "does not match identity"
            )


def governed_knowledge_lifecycle_assertion_interpretation_premise_identity_input_from_record(
    record: GovernedKnowledgeLifecycleAssertionInterpretationPremise,
) -> GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput:
    if (
        type(record)
        is not GovernedKnowledgeLifecycleAssertionInterpretationPremise
    ):
        raise ValueError(
            "record must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremise"
        )
    return GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput(
        contract_version=record.contract_version,
        governed_knowledge_id=record.governed_knowledge_id,
        governed_knowledge_contract_version=(
            record.governed_knowledge_contract_version
        ),
        premise_scope=record.premise_scope,
        premise_scope_reference=record.premise_scope_reference,
        completeness_declaration=record.completeness_declaration,
        assertions=record.assertions,
        declared_by=record.declared_by,
        declared_at=record.declared_at,
        declaration_policy_id=record.declaration_policy_id,
        declaration_policy_version=record.declaration_policy_version,
        reason_codes=record.reason_codes,
    )
