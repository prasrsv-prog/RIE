from dataclasses import dataclass as _dataclass
import hashlib as _hashlib
import json as _json
import math as _math
import re as _re
import unicodedata as _unicodedata

from rie.domain.governed_knowledge_lifecycle_assertion import (
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX as _GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX,
)
from rie.domain.governed_knowledge_lifecycle_assertion_interpretation_premise import (
    GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX as _GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX,
    GovernedKnowledgeLifecycleAssertionInterpretationPremise as _GovernedKnowledgeLifecycleAssertionInterpretationPremise,
)


GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_CONTRACT_VERSION = (
    "governed-knowledge-lifecycle-assertion-interpretation-result-v1"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_ID_PREFIX = (
    "gklair1_"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_POLICY_ID = (
    "rcis-governed-knowledge-lifecycle-assertion-interpretation-result-identity"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_POLICY_VERSION = (
    "1.0.0"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_CANONICALIZATION_CONTRACT = (
    "rcis-governed-knowledge-lifecycle-assertion-interpretation-result-canonical-json-v1"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_DIGEST_ALGORITHM = (
    "sha256"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY = (
    "empty_assertion_collection"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM = (
    "uniform_assertion_value"
)
GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY = (
    "contradictory_assertion_values"
)


_RESULT_ID_PATTERN = _re.compile(
    rf"^{GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_ID_PREFIX}"
    r"[0-9a-f]{64}$"
)
_PREMISE_ID_PATTERN = _re.compile(
    rf"^{_GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX}"
    r"[0-9a-f]{64}$"
)
_ASSERTION_ID_PATTERN = _re.compile(
    rf"^{_GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX}"
    r"[0-9a-f]{64}$"
)


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


@_dataclass(frozen=True)
class GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup:
    assertion_value: str
    assertion_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_string(self.assertion_value, "assertion_value")
        if _unicodedata.normalize("NFC", self.assertion_value) != self.assertion_value:
            raise ValueError("assertion_value must be Unicode NFC normalized")
        if type(self.assertion_ids) is not tuple or not self.assertion_ids:
            raise ValueError("assertion_ids must be a non-empty tuple")
        for assertion_id in self.assertion_ids:
            _require_pattern(
                assertion_id,
                "assertion_ids",
                _ASSERTION_ID_PATTERN,
            )
        if len(set(self.assertion_ids)) != len(self.assertion_ids):
            raise ValueError("assertion_ids must contain unique values")
        if tuple(sorted(self.assertion_ids)) != self.assertion_ids:
            raise ValueError("assertion_ids must be lexicographically ordered")


def _derive_expected_structure(
    premise: _GovernedKnowledgeLifecycleAssertionInterpretationPremise,
) -> tuple[
    str,
    tuple[GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup, ...],
]:
    if type(premise) is not _GovernedKnowledgeLifecycleAssertionInterpretationPremise:
        raise ValueError(
            "premise must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremise"
        )
    premise.__post_init__()

    grouped: dict[str, list[str]] = {}
    for assertion in premise.assertions:
        normalized_value = _unicodedata.normalize(
            "NFC",
            assertion.assertion_value,
        )
        grouped.setdefault(normalized_value, []).append(
            assertion.governed_knowledge_lifecycle_assertion_id
        )

    groups = tuple(
        GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup(
            assertion_value=assertion_value,
            assertion_ids=tuple(sorted(assertion_ids)),
        )
        for assertion_value, assertion_ids in sorted(grouped.items())
    )

    if not groups:
        status = (
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY
        )
    elif len(groups) == 1:
        status = (
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM
        )
    else:
        status = (
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY
        )

    return status, groups


def _validate_value_groups(
    value: object,
) -> tuple[GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup, ...]:
    if type(value) is not tuple:
        raise ValueError("assertion_value_groups must be an exact tuple")

    assertion_values: list[str] = []
    for group in value:
        if (
            type(group)
            is not GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup
        ):
            raise ValueError(
                "assertion_value_groups must contain exact "
                "GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup "
                "records"
            )
        group.__post_init__()
        assertion_values.append(group.assertion_value)

    if len(set(assertion_values)) != len(assertion_values):
        raise ValueError(
            "assertion_value_groups must contain unique assertion values"
        )
    if tuple(sorted(assertion_values)) != tuple(assertion_values):
        raise ValueError(
            "assertion_value_groups must be lexicographically ordered by "
            "assertion value"
        )

    return value  # type: ignore[return-value]


@_dataclass(frozen=True)
class GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput:
    contract_version: str
    premise: _GovernedKnowledgeLifecycleAssertionInterpretationPremise
    result_status: str
    assertion_value_groups: tuple[
        GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup,
        ...,
    ]
    interpreted_by: str
    interpretation_policy_id: str
    interpretation_policy_version: str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported contract_version")
        if (
            type(self.premise)
            is not _GovernedKnowledgeLifecycleAssertionInterpretationPremise
        ):
            raise ValueError(
                "premise must be an exact "
                "GovernedKnowledgeLifecycleAssertionInterpretationPremise"
            )
        self.premise.__post_init__()
        if self.result_status not in (
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY,
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM,
            GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY,
        ):
            raise ValueError("unsupported result_status")

        groups = _validate_value_groups(self.assertion_value_groups)
        expected_status, expected_groups = _derive_expected_structure(
            self.premise
        )

        if groups != expected_groups:
            raise ValueError(
                "assertion_value_groups do not match premise assertions"
            )
        if self.result_status != expected_status:
            raise ValueError(
                "result_status does not match premise assertions"
            )

        _require_string(self.interpreted_by, "interpreted_by")
        _require_string(
            self.interpretation_policy_id,
            "interpretation_policy_id",
        )
        _require_string(
            self.interpretation_policy_version,
            "interpretation_policy_version",
        )
        _require_unique_ordered_strings(self.reason_codes, "reason_codes")


def canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_projection(
    identity_input: GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput,
) -> dict[str, object]:
    if (
        type(identity_input)
        is not GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput
    ):
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput"
        )
    identity_input.__post_init__()

    _require_pattern(
        identity_input.premise.governed_knowledge_lifecycle_assertion_interpretation_premise_id,
        "governed_knowledge_lifecycle_assertion_interpretation_premise_id",
        _PREMISE_ID_PATTERN,
    )

    return _canonicalize(
        {
            "contract_version": identity_input.contract_version,
            "premise_id": (
                identity_input.premise.governed_knowledge_lifecycle_assertion_interpretation_premise_id
            ),
            "result_status": identity_input.result_status,
            "assertion_value_groups": tuple(
                {
                    "assertion_value": group.assertion_value,
                    "assertion_ids": group.assertion_ids,
                }
                for group in identity_input.assertion_value_groups
            ),
            "interpreted_by": identity_input.interpreted_by,
            "interpretation_policy_id": (
                identity_input.interpretation_policy_id
            ),
            "interpretation_policy_version": (
                identity_input.interpretation_policy_version
            ),
            "reason_codes": identity_input.reason_codes,
            "identity_canonicalization_contract": (
                GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_CANONICALIZATION_CONTRACT
            ),
        }
    )  # type: ignore[return-value]


def canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_bytes(
    identity_input: GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput,
) -> bytes:
    if (
        type(identity_input)
        is not GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput
    ):
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput"
        )
    return _json.dumps(
        canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_projection(
            identity_input
        ),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
    identity_input: GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput,
) -> str:
    if (
        type(identity_input)
        is not GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput
    ):
        raise ValueError(
            "identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput"
        )
    digest = _hashlib.sha256(
        canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_bytes(
            identity_input
        )
    ).hexdigest()
    return (
        f"{GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_ID_PREFIX}"
        f"{digest}"
    )


@_dataclass(frozen=True)
class GovernedKnowledgeLifecycleAssertionInterpretationResult:
    governed_knowledge_lifecycle_assertion_interpretation_result_id: str
    contract_version: str
    premise: _GovernedKnowledgeLifecycleAssertionInterpretationPremise
    result_status: str
    assertion_value_groups: tuple[
        GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup,
        ...,
    ]
    interpreted_by: str
    interpretation_policy_id: str
    interpretation_policy_version: str
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.governed_knowledge_lifecycle_assertion_interpretation_result_id,
            "governed_knowledge_lifecycle_assertion_interpretation_result_id",
            _RESULT_ID_PATTERN,
        )
        identity_input = (
            governed_knowledge_lifecycle_assertion_interpretation_result_identity_input_from_record(
                self
            )
        )
        if (
            self.governed_knowledge_lifecycle_assertion_interpretation_result_id
            != compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
                identity_input
            )
        ):
            raise ValueError(
                "governed_knowledge_lifecycle_assertion_interpretation_result_id "
                "does not match identity"
            )


def governed_knowledge_lifecycle_assertion_interpretation_result_identity_input_from_record(
    record: GovernedKnowledgeLifecycleAssertionInterpretationResult,
) -> GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput:
    if type(record) is not GovernedKnowledgeLifecycleAssertionInterpretationResult:
        raise ValueError(
            "record must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResult"
        )
    return GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput(
        contract_version=record.contract_version,
        premise=record.premise,
        result_status=record.result_status,
        assertion_value_groups=record.assertion_value_groups,
        interpreted_by=record.interpreted_by,
        interpretation_policy_id=record.interpretation_policy_id,
        interpretation_policy_version=record.interpretation_policy_version,
        reason_codes=record.reason_codes,
    )

def interpret_governed_knowledge_lifecycle_assertion_premise_structurally(
    premise: _GovernedKnowledgeLifecycleAssertionInterpretationPremise,
    interpreted_by: str,
    interpretation_policy_id: str,
    interpretation_policy_version: str,
    reason_codes: tuple[str, ...],
) -> GovernedKnowledgeLifecycleAssertionInterpretationResult:
    if type(premise) is not _GovernedKnowledgeLifecycleAssertionInterpretationPremise:
        raise ValueError(
            "premise must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremise"
        )
    premise.__post_init__()
    _require_string(interpreted_by, "interpreted_by")
    _require_string(
        interpretation_policy_id,
        "interpretation_policy_id",
    )
    _require_string(
        interpretation_policy_version,
        "interpretation_policy_version",
    )
    _require_unique_ordered_strings(reason_codes, "reason_codes")

    result_status, assertion_value_groups = _derive_expected_structure(premise)
    identity_input = (
        GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput(
            contract_version=(
                GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_CONTRACT_VERSION
            ),
            premise=premise,
            result_status=result_status,
            assertion_value_groups=assertion_value_groups,
            interpreted_by=interpreted_by,
            interpretation_policy_id=interpretation_policy_id,
            interpretation_policy_version=interpretation_policy_version,
            reason_codes=reason_codes,
        )
    )
    result_id = (
        compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
            identity_input
        )
    )
    return GovernedKnowledgeLifecycleAssertionInterpretationResult(
        governed_knowledge_lifecycle_assertion_interpretation_result_id=result_id,
        **identity_input.__dict__,
    )
