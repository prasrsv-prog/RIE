import json
import re
from dataclasses import dataclass
from datetime import datetime
from math import isfinite


_LOWER_TOKEN_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_ALGORITHM_TOKEN_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_GENERAL_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:+-]*$")
_CHECKSUM_PATTERN = re.compile(r"^[0-9a-f]+$")
_RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
_LOCATOR_KEYS = frozenset(
    {
        "column_index",
        "height",
        "page_index",
        "row_index",
        "scope",
        "width",
        "x",
        "y",
    }
)
_LOCATOR_SCOPES = frozenset(
    {"source", "document", "page", "region", "table_cell"}
)


@dataclass(frozen=True)
class EvidenceCandidate:
    source_id: str
    source_type: str
    source_checksum_algorithm: str
    source_checksum: str
    source_authority: str
    source_lifecycle_state: str
    source_reference: str
    execution_id: str
    producer_name: str
    producer_version: str
    result_contract_version: str
    execution_timestamp: str
    payload_type: str
    raw_payload: str
    locator: tuple[tuple[str, str | int | float], ...]
    warnings: tuple[str, ...]
    errors: tuple[str, ...]
    candidate_contract_version: str

    def __post_init__(self) -> None:
        for field_name in (
            "source_id",
            "source_type",
            "source_checksum_algorithm",
            "source_checksum",
            "source_authority",
            "source_lifecycle_state",
            "source_reference",
            "execution_id",
            "producer_name",
            "producer_version",
            "result_contract_version",
            "execution_timestamp",
            "payload_type",
            "raw_payload",
            "candidate_contract_version",
        ):
            _validate_required_string(field_name, getattr(self, field_name))

        for field_name in (
            "source_type",
            "source_authority",
            "source_lifecycle_state",
            "payload_type",
        ):
            _validate_token(
                field_name,
                getattr(self, field_name),
                _LOWER_TOKEN_PATTERN,
            )

        _validate_token(
            "source_checksum_algorithm",
            self.source_checksum_algorithm,
            _ALGORITHM_TOKEN_PATTERN,
        )

        for field_name in (
            "producer_name",
            "producer_version",
            "result_contract_version",
            "candidate_contract_version",
        ):
            _validate_token(
                field_name,
                getattr(self, field_name),
                _GENERAL_TOKEN_PATTERN,
            )

        _validate_checksum(self.source_checksum)
        _validate_execution_timestamp(self.execution_timestamp)
        _validate_canonical_json(self.raw_payload)
        _validate_locator(self.locator)
        _validate_diagnostics("warnings", self.warnings)
        _validate_diagnostics("errors", self.errors)


def _validate_required_string(field_name: str, value: object) -> None:
    if type(value) is not str:
        raise ValueError(f"{field_name} must be a string")

    if value == "" or value.strip() == "":
        raise ValueError(f"{field_name} must not be empty")

    if value != value.strip():
        raise ValueError(
            f"{field_name} must not have leading or trailing whitespace"
        )

    if _contains_control_character(value):
        raise ValueError(f"{field_name} must not contain control characters")


def _contains_control_character(value: str) -> bool:
    return any(
        ord(character) < 32 or 127 <= ord(character) <= 159
        for character in value
    )


def _validate_token(
    field_name: str,
    value: str,
    pattern: re.Pattern[str],
) -> None:
    if pattern.fullmatch(value) is None:
        raise ValueError(f"{field_name} has invalid token syntax")


def _validate_checksum(value: str) -> None:
    if _CHECKSUM_PATTERN.fullmatch(value) is None:
        raise ValueError(
            "source_checksum must contain lower-case hexadecimal characters"
        )

    if len(value) % 2 != 0:
        raise ValueError("source_checksum must have an even length")


def _validate_execution_timestamp(value: str) -> None:
    if _RFC3339_PATTERN.fullmatch(value) is None:
        raise ValueError(
            "execution_timestamp must use timezone-aware RFC 3339 syntax"
        )

    validation_value = value[:-1] + "+00:00" if value.endswith("Z") else value

    try:
        parsed = datetime.fromisoformat(validation_value)
    except ValueError:
        raise ValueError(
            "execution_timestamp must contain a valid calendar date and time"
        ) from None

    if parsed.utcoffset() is None:
        raise ValueError("execution_timestamp must contain a UTC offset")


def _reject_duplicate_object_pairs(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                "raw_payload must not contain duplicate JSON object keys"
            )
        result[key] = value

    return result


def _reject_non_finite_constant(value: str) -> None:
    raise ValueError(
        f"raw_payload must contain finite JSON numbers, not {value}"
    )


def _validate_canonical_json(value: str) -> None:
    try:
        parsed = json.loads(
            value,
            object_pairs_hook=_reject_duplicate_object_pairs,
            parse_constant=_reject_non_finite_constant,
        )
    except json.JSONDecodeError:
        raise ValueError("raw_payload must contain valid JSON") from None

    try:
        canonical = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except ValueError:
        raise ValueError("raw_payload must contain finite JSON numbers") from None

    if canonical != value:
        raise ValueError("raw_payload must contain repository-canonical JSON")


def _validate_locator(
    locator: tuple[tuple[str, str | int | float], ...],
) -> None:
    if type(locator) is not tuple:
        raise ValueError("locator must be a tuple")

    if not locator:
        raise ValueError("locator must not be empty")

    keys: list[str] = []
    values: dict[str, str | int | float] = {}

    for entry in locator:
        if type(entry) is not tuple or len(entry) != 2:
            raise ValueError("locator entries must be two-item tuples")

        key, value = entry

        if type(key) is not str or _LOWER_TOKEN_PATTERN.fullmatch(key) is None:
            raise ValueError("locator keys must be lower-case string tokens")

        if key not in _LOCATOR_KEYS:
            raise ValueError(f"locator contains unsupported key: {key}")

        if key in values:
            raise ValueError(f"locator contains duplicate key: {key}")

        if type(value) not in {str, int, float}:
            raise ValueError(f"locator value for {key} has an invalid type")

        if type(value) is str:
            _validate_required_string(f"locator {key}", value)

        if type(value) is float and not isfinite(value):
            raise ValueError(f"locator value for {key} must be finite")

        keys.append(key)
        values[key] = value

    if keys != sorted(keys):
        raise ValueError("locator keys must be lexicographically ordered")

    scope = values.get("scope")

    if type(scope) is not str or scope not in _LOCATOR_SCOPES:
        raise ValueError("locator scope is required and must be supported")

    if scope in {"source", "document"}:
        allowed_key_sets = ({"scope"},)
    elif scope == "page":
        allowed_key_sets = ({"page_index", "scope"},)
    elif scope == "region":
        required = {"height", "scope", "width", "x", "y"}
        allowed_key_sets = (required, required | {"page_index"})
    else:
        required = {"column_index", "row_index", "scope"}
        allowed_key_sets = (required, required | {"page_index"})

    if set(keys) not in allowed_key_sets:
        raise ValueError(f"locator keys do not match {scope} scope")

    for key in ("page_index", "row_index", "column_index"):
        if key not in values:
            continue

        value = values[key]

        if type(value) is not int or value < 0:
            raise ValueError(f"locator {key} must be a non-negative integer")

    for key in ("x", "y", "width", "height"):
        if key not in values:
            continue

        value = values[key]

        if type(value) not in {int, float}:
            raise ValueError(f"locator {key} must be numeric")

        if type(value) is float and not isfinite(value):
            raise ValueError(f"locator {key} must be finite")

        if key in {"x", "y"} and value < 0:
            raise ValueError(f"locator {key} must not be negative")

        if key in {"width", "height"} and value <= 0:
            raise ValueError(f"locator {key} must be greater than zero")


def _validate_diagnostics(
    field_name: str,
    diagnostics: tuple[str, ...],
) -> None:
    if type(diagnostics) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")

    for diagnostic in diagnostics:
        _validate_required_string(field_name, diagnostic)
