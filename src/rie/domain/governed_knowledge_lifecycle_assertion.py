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


GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION = (
    "governed-knowledge-lifecycle-assertion-v1"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX = "gkla1_"
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_ID = (
    "rcis-governed-knowledge-lifecycle-assertion-identity"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_VERSION = "1.0.0"
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_CANONICALIZATION_CONTRACT = (
    "rcis-governed-knowledge-lifecycle-assertion-canonical-json-v1"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_DIGEST_ALGORITHM = "sha256"
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED = (
    "governed_knowledge_lifecycle_assertion_for_declared_subject"
)


_GOVERNED_KNOWLEDGE_ID_PATTERN = _re.compile(r"^gk1_[0-9a-f]{64}$")
_LIFECYCLE_ASSERTION_ID_PATTERN = _re.compile(r"^gkla1_[0-9a-f]{64}$")


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


def _format_asserted_at(value: _datetime) -> str:
    return value.astimezone(_timezone.utc).isoformat(
        timespec="microseconds"
    ).replace("+00:00", "Z")


@_dataclass(frozen=True)
class GovernedKnowledgeLifecycleAssertionIdentityInput:
    contract_version: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    assertion_scope: str
    assertion_scope_reference: str
    assertion_value: str
    asserted_by: str
    asserted_at: _datetime
    assertion_policy_id: str
    assertion_policy_version: str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION
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
            self.assertion_scope
            != GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED
        ):
            raise ValueError("unsupported assertion_scope")
        _require_string(
            self.assertion_scope_reference,
            "assertion_scope_reference",
        )
        _require_string(self.assertion_value, "assertion_value")
        _require_string(self.asserted_by, "asserted_by")
        _require_aware_datetime(self.asserted_at, "asserted_at")
        _require_string(self.assertion_policy_id, "assertion_policy_id")
        _require_string(
            self.assertion_policy_version,
            "assertion_policy_version",
        )
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")


def canonical_governed_knowledge_lifecycle_assertion_identity_projection(
    identity_input: GovernedKnowledgeLifecycleAssertionIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not GovernedKnowledgeLifecycleAssertionIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionIdentityInput"
        )
    identity_input.__post_init__()
    return _canonicalize(
        {
            "contract_version": identity_input.contract_version,
            "governed_knowledge_id": identity_input.governed_knowledge_id,
            "governed_knowledge_contract_version": (
                identity_input.governed_knowledge_contract_version
            ),
            "assertion_scope": identity_input.assertion_scope,
            "assertion_scope_reference": (
                identity_input.assertion_scope_reference
            ),
            "assertion_value": identity_input.assertion_value,
            "asserted_by": identity_input.asserted_by,
            "asserted_at": _format_asserted_at(identity_input.asserted_at),
            "assertion_policy_id": identity_input.assertion_policy_id,
            "assertion_policy_version": (
                identity_input.assertion_policy_version
            ),
            "reason_codes": identity_input.reason_codes,
            "identity_canonicalization_contract": (
                GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_CANONICALIZATION_CONTRACT
            ),
        }
    )  # type: ignore[return-value]


def canonical_governed_knowledge_lifecycle_assertion_identity_bytes(
    identity_input: GovernedKnowledgeLifecycleAssertionIdentityInput,
) -> bytes:
    if type(identity_input) is not GovernedKnowledgeLifecycleAssertionIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionIdentityInput"
        )
    return _json.dumps(
        canonical_governed_knowledge_lifecycle_assertion_identity_projection(
            identity_input
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_governed_knowledge_lifecycle_assertion_id(
    identity_input: GovernedKnowledgeLifecycleAssertionIdentityInput,
) -> str:
    if type(identity_input) is not GovernedKnowledgeLifecycleAssertionIdentityInput:
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionIdentityInput"
        )
    digest = _hashlib.sha256(
        canonical_governed_knowledge_lifecycle_assertion_identity_bytes(
            identity_input
        )
    ).hexdigest()
    return f"{GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX}{digest}"


@_dataclass(frozen=True)
class GovernedKnowledgeLifecycleAssertion:
    governed_knowledge_lifecycle_assertion_id: str
    contract_version: str
    governed_knowledge_id: str
    governed_knowledge_contract_version: str
    assertion_scope: str
    assertion_scope_reference: str
    assertion_value: str
    asserted_by: str
    asserted_at: _datetime
    assertion_policy_id: str
    assertion_policy_version: str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.governed_knowledge_lifecycle_assertion_id,
            "governed_knowledge_lifecycle_assertion_id",
            _LIFECYCLE_ASSERTION_ID_PATTERN,
        )
        identity_input = (
            governed_knowledge_lifecycle_assertion_identity_input_from_record(
                self
            )
        )
        if self.governed_knowledge_lifecycle_assertion_id != (
            compute_governed_knowledge_lifecycle_assertion_id(identity_input)
        ):
            raise ValueError(
                "governed_knowledge_lifecycle_assertion_id "
                "does not match identity"
            )


def governed_knowledge_lifecycle_assertion_identity_input_from_record(
    record: GovernedKnowledgeLifecycleAssertion,
) -> GovernedKnowledgeLifecycleAssertionIdentityInput:
    if type(record) is not GovernedKnowledgeLifecycleAssertion:
        raise ValueError(
            "record must be an exact GovernedKnowledgeLifecycleAssertion"
        )
    return GovernedKnowledgeLifecycleAssertionIdentityInput(
        contract_version=record.contract_version,
        governed_knowledge_id=record.governed_knowledge_id,
        governed_knowledge_contract_version=(
            record.governed_knowledge_contract_version
        ),
        assertion_scope=record.assertion_scope,
        assertion_scope_reference=record.assertion_scope_reference,
        assertion_value=record.assertion_value,
        asserted_by=record.asserted_by,
        asserted_at=record.asserted_at,
        assertion_policy_id=record.assertion_policy_id,
        assertion_policy_version=record.assertion_policy_version,
        reason_codes=record.reason_codes,
    )
