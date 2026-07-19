from collections import Counter as _Counter
from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum
from json import JSONDecodeError as _JSONDecodeError
from pathlib import Path as _Path
import re as _re

from official_source.official_source import OfficialSource as _OfficialSource
from official_source.official_source_registry_loader import (
    OfficialSourceRegistryLoader as _OfficialSourceRegistryLoader,
)


OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION = (
    "official_source_registry_validation_contract_v1"
)


class OfficialSourceRegistryValidationStatus(_Enum):
    VALID = "valid"
    INVALID = "invalid"


class OfficialSourceRegistryValidationIssueCode(_Enum):
    REGISTRY_MISSING = "registry_missing"
    REGISTRY_UNREADABLE = "registry_unreadable"
    INVALID_JSON = "invalid_json"
    INVALID_REGISTRY_STRUCTURE = "invalid_registry_structure"
    INVALID_REGISTRY_ENTRY = "invalid_registry_entry"
    DUPLICATE_SOURCE_ID = "duplicate_source_id"


@_dataclass(frozen=True)
class OfficialSourceRegistryValidationRequest:
    registry_path: str | _Path

    def __post_init__(self) -> None:
        if not isinstance(self.registry_path, (str, _Path)):
            raise TypeError("registry_path must be a string or Path.")


@_dataclass(frozen=True)
class OfficialSourceRegistryValidationIssue:
    code: OfficialSourceRegistryValidationIssueCode
    message: str
    item_index: int | None = None
    field_name: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.code,
            OfficialSourceRegistryValidationIssueCode,
        ):
            raise TypeError(
                "code must be OfficialSourceRegistryValidationIssueCode."
            )

        if not isinstance(self.message, str) or self.message.strip() == "":
            raise ValueError("message must be a non-empty string.")

        if self.item_index is not None and (
            not isinstance(self.item_index, int) or self.item_index < 0
        ):
            raise ValueError("item_index must be a non-negative integer or None.")

        if self.field_name is not None and (
            not isinstance(self.field_name, str)
            or self.field_name.strip() == ""
        ):
            raise ValueError("field_name must be a non-empty string or None.")


@_dataclass(frozen=True)
class OfficialSourceRegistryValidationResult:
    contract_version: str
    status: OfficialSourceRegistryValidationStatus
    sources: tuple[_OfficialSource, ...]
    issues: tuple[OfficialSourceRegistryValidationIssue, ...]

    def __post_init__(self) -> None:
        if self.contract_version != (
            OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION
        ):
            raise ValueError("contract_version is unsupported.")

        if not isinstance(
            self.status,
            OfficialSourceRegistryValidationStatus,
        ):
            raise TypeError(
                "status must be OfficialSourceRegistryValidationStatus."
            )

        if not isinstance(self.sources, tuple):
            raise TypeError("sources must be a tuple.")

        if not all(isinstance(source, _OfficialSource) for source in self.sources):
            raise TypeError("sources must contain OfficialSource values.")

        if not isinstance(self.issues, tuple):
            raise TypeError("issues must be a tuple.")

        if not all(
            isinstance(issue, OfficialSourceRegistryValidationIssue)
            for issue in self.issues
        ):
            raise TypeError(
                "issues must contain OfficialSourceRegistryValidationIssue "
                "values."
            )

        if self.status is OfficialSourceRegistryValidationStatus.VALID:
            if self.issues:
                raise ValueError("valid result must not contain issues.")
        else:
            if self.sources:
                raise ValueError("invalid result must not contain sources.")
            if len(self.issues) != 1:
                raise ValueError(
                    "invalid result must contain exactly one issue."
                )


def validate_official_source_registry(
    request: OfficialSourceRegistryValidationRequest,
) -> OfficialSourceRegistryValidationResult:
    if not isinstance(request, OfficialSourceRegistryValidationRequest):
        raise TypeError(
            "request must be OfficialSourceRegistryValidationRequest."
        )

    try:
        sources = _OfficialSourceRegistryLoader.load_from_json_file(
            request.registry_path,
        )
    except FileNotFoundError:
        return _invalid_result(
            OfficialSourceRegistryValidationIssueCode.REGISTRY_MISSING,
            "Official Source registry file does not exist.",
        )
    except (PermissionError, IsADirectoryError, UnicodeError, OSError):
        return _invalid_result(
            OfficialSourceRegistryValidationIssueCode.REGISTRY_UNREADABLE,
            "Official Source registry file is unreadable.",
        )
    except (TypeError, ValueError) as exc:
        return _invalid_loader_result(exc)

    return OfficialSourceRegistryValidationResult(
        contract_version=(
            OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION
        ),
        status=OfficialSourceRegistryValidationStatus.VALID,
        sources=tuple(sources),
        issues=(),
    )


def render_official_source_registry_validation_report(
    result: OfficialSourceRegistryValidationResult,
) -> str:
    if not isinstance(result, OfficialSourceRegistryValidationResult):
        raise TypeError(
            "result must be OfficialSourceRegistryValidationResult."
        )

    lines = [
        "Official Source Registry Validation Report",
        f"contract_version: {result.contract_version}",
        f"status: {result.status.value}",
    ]

    if result.status is OfficialSourceRegistryValidationStatus.INVALID:
        issue = result.issues[0]
        lines.extend(
            [
                f"issue_code: {issue.code.value}",
                f"issue_message: {issue.message}",
            ]
        )

        if issue.item_index is not None:
            lines.append(f"item_index: {issue.item_index}")

        if issue.field_name is not None:
            lines.append(f"field_name: {issue.field_name}")

        return "\n".join(lines)

    lines.append(f"total_official_sources: {len(result.sources)}")
    _append_count_section(
        lines,
        "source_type",
        _Counter(source.source_type.value for source in result.sources),
    )
    _append_count_section(
        lines,
        "document_classification",
        _Counter(
            source.document_classification.value
            for source in result.sources
        ),
    )
    _append_count_section(
        lines,
        "authority_status",
        _Counter(source.authority_status.value for source in result.sources),
    )
    _append_count_section(
        lines,
        "lifecycle_status",
        _Counter(source.lifecycle_status.value for source in result.sources),
    )
    _append_count_section(
        lines,
        "evidence_eligibility",
        _Counter(
            source.evidence_eligibility.value
            for source in result.sources
        ),
    )

    return "\n".join(lines)


def _invalid_loader_result(
    exc: TypeError | ValueError,
) -> OfficialSourceRegistryValidationResult:
    message = str(exc)

    if isinstance(exc.__cause__, _JSONDecodeError):
        return _invalid_result(
            OfficialSourceRegistryValidationIssueCode.INVALID_JSON,
            "Official Source registry file contains invalid JSON.",
        )

    if message.startswith("duplicate source_id:"):
        return _invalid_result(
            OfficialSourceRegistryValidationIssueCode.DUPLICATE_SOURCE_ID,
            "Official Source registry contains a duplicate source_id.",
            field_name="source_id",
        )

    item_index, field_name = _extract_item_location(message)

    if item_index is not None:
        return _invalid_result(
            OfficialSourceRegistryValidationIssueCode.INVALID_REGISTRY_ENTRY,
            "Official Source registry item is invalid.",
            item_index=item_index,
            field_name=field_name,
        )

    return _invalid_result(
        OfficialSourceRegistryValidationIssueCode.INVALID_REGISTRY_STRUCTURE,
        "Official Source registry structure is invalid.",
    )


def _invalid_result(
    code: OfficialSourceRegistryValidationIssueCode,
    message: str,
    *,
    item_index: int | None = None,
    field_name: str | None = None,
) -> OfficialSourceRegistryValidationResult:
    issue = OfficialSourceRegistryValidationIssue(
        code=code,
        message=message,
        item_index=item_index,
        field_name=field_name,
    )
    return OfficialSourceRegistryValidationResult(
        contract_version=(
            OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION
        ),
        status=OfficialSourceRegistryValidationStatus.INVALID,
        sources=(),
        issues=(issue,),
    )


def _extract_item_location(
    message: str,
) -> tuple[int | None, str | None]:
    index_match = _re.search(
        r"Official Source registry item (?P<index>\d+)",
        message,
    )

    if index_match is None:
        return None, None

    item_index = int(index_match.group("index"))
    field_name = None

    field_patterns = (
        r"(?:contains forbidden field|contains unknown field|"
        r"missing required field): (?P<field>[a-z_]+)\.",
        r"item \d+ (?P<field>[a-z_]+) "
        r"(?:must|has invalid enum value)",
    )

    for pattern in field_patterns:
        field_match = _re.search(pattern, message)

        if field_match is not None:
            field_name = field_match.group("field")
            break

    return item_index, field_name


def _append_count_section(
    lines: list[str],
    label: str,
    counts: _Counter[str],
) -> None:
    lines.append(f"{label}:")

    for value in sorted(counts):
        lines.append(f"  {value}: {counts[value]}")


__all__ = (
    "OFFICIAL_SOURCE_REGISTRY_VALIDATION_CONTRACT_VERSION",
    "OfficialSourceRegistryValidationStatus",
    "OfficialSourceRegistryValidationIssueCode",
    "OfficialSourceRegistryValidationRequest",
    "OfficialSourceRegistryValidationIssue",
    "OfficialSourceRegistryValidationResult",
    "validate_official_source_registry",
    "render_official_source_registry_validation_report",
)
