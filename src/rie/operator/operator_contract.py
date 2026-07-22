"""Immutable Gate 11 operator contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Mapping

OPERATOR_SCHEMA_VERSION = "rie_operator_result_v1"
OPERATOR_CONTRACT_VERSION = "rie_operator_contract_v1"
PACKAGE_VERSION = "0.1.0"

REQUIRED_COMMANDS = (
    "registry validate",
    "source inspect",
    "ingest pdf",
    "evidence build",
    "evidence inspect",
    "knowledge build",
    "knowledge inspect",
    "prompt-candidate build",
    "audit job",
    "export",
)


class ExitCode(IntEnum):
    SUCCESS = 0
    UNEXPECTED_INTERNAL_FAILURE = 1
    CLI_USAGE_INVALID = 2
    CONFIGURATION_INVALID = 3
    SOURCE_OR_INPUT_INVALID = 4
    CONTRACT_OR_ELIGIBILITY_REJECTED = 5
    STATE_CONFLICT_OR_IDEMPOTENCY_VIOLATION = 6
    PERSISTENCE_OR_IO_FAILURE = 7
    AUDIT_OR_EXPORT_FAILURE = 8


class OperatorStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    REUSED_EXISTING = "REUSED_EXISTING"
    NO_CHANGE = "NO_CHANGE"
    DRY_RUN_VALID = "DRY_RUN_VALID"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


def freeze_mapping(values: Mapping[str, object] | None) -> tuple[tuple[str, str], ...]:
    if values is None:
        return ()
    if not isinstance(values, Mapping):
        raise TypeError("values must be a mapping or None.")
    return tuple(
        (str(key), _string_value(value))
        for key, value in sorted(values.items(), key=lambda item: str(item[0]))
    )


def thaw_mapping(values: tuple[tuple[str, str], ...]) -> dict[str, str]:
    return {key: value for key, value in values}


def _string_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


@dataclass(frozen=True)
class OperatorRequest:
    command: str
    arguments: tuple[tuple[str, str], ...] = ()
    output_format: str = "human"
    output_path: str | None = None
    dry_run: bool = False

    def __post_init__(self) -> None:
        if self.command not in REQUIRED_COMMANDS:
            raise ValueError("command is unsupported.")
        if self.output_format not in {"human", "json"}:
            raise ValueError("output_format must be human or json.")
        if not isinstance(self.arguments, tuple):
            raise TypeError("arguments must be a tuple.")
        if not isinstance(self.dry_run, bool):
            raise TypeError("dry_run must be a boolean.")

    @property
    def argument_map(self) -> dict[str, str]:
        return thaw_mapping(self.arguments)


@dataclass(frozen=True)
class OperatorResult:
    schema_version: str
    command: str
    status: OperatorStatus
    exit_code: ExitCode
    issue_code: str
    message: str
    dry_run: bool
    identifiers: tuple[tuple[str, str], ...] = ()
    provenance: tuple[tuple[str, str], ...] = ()
    audit: tuple[tuple[str, str], ...] = ()
    outputs: tuple[tuple[str, str], ...] = ()
    recovery: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.schema_version != OPERATOR_SCHEMA_VERSION:
            raise ValueError("schema_version is unsupported.")
        if self.command not in REQUIRED_COMMANDS:
            raise ValueError("command is unsupported.")
        if not isinstance(self.status, OperatorStatus):
            raise TypeError("status must be OperatorStatus.")
        if not isinstance(self.exit_code, ExitCode):
            raise TypeError("exit_code must be ExitCode.")
        if not isinstance(self.issue_code, str):
            raise TypeError("issue_code must be a string.")
        if not isinstance(self.message, str) or self.message.strip() == "":
            raise ValueError("message must be non-empty.")
        if not isinstance(self.dry_run, bool):
            raise TypeError("dry_run must be a boolean.")
        successful = {
            OperatorStatus.SUCCEEDED,
            OperatorStatus.REUSED_EXISTING,
            OperatorStatus.NO_CHANGE,
            OperatorStatus.DRY_RUN_VALID,
        }
        if self.status in successful and self.exit_code is not ExitCode.SUCCESS:
            raise ValueError("successful status must use exit code 0.")
        if self.status in {OperatorStatus.REJECTED, OperatorStatus.FAILED}:
            if self.exit_code is ExitCode.SUCCESS:
                raise ValueError("non-success status must use a nonzero exit code.")


def make_result(
    *,
    command: str,
    status: OperatorStatus,
    exit_code: ExitCode,
    issue_code: str,
    message: str,
    dry_run: bool,
    identifiers: Mapping[str, object] | None = None,
    provenance: Mapping[str, object] | None = None,
    audit: Mapping[str, object] | None = None,
    outputs: Mapping[str, object] | None = None,
    recovery: Mapping[str, object] | None = None,
) -> OperatorResult:
    return OperatorResult(
        schema_version=OPERATOR_SCHEMA_VERSION,
        command=command,
        status=status,
        exit_code=exit_code,
        issue_code=issue_code,
        message=message,
        dry_run=dry_run,
        identifiers=freeze_mapping(identifiers),
        provenance=freeze_mapping(provenance),
        audit=freeze_mapping(audit),
        outputs=freeze_mapping(outputs),
        recovery=freeze_mapping(recovery),
    )


__all__ = (
    "OPERATOR_SCHEMA_VERSION",
    "OPERATOR_CONTRACT_VERSION",
    "PACKAGE_VERSION",
    "REQUIRED_COMMANDS",
    "ExitCode",
    "OperatorStatus",
    "OperatorRequest",
    "OperatorResult",
    "freeze_mapping",
    "thaw_mapping",
    "make_result",
)
