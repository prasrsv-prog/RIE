"""Explicit Gate 11 operator configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

CONFIGURATION_SCHEMA_VERSION = "rie_operator_configuration_v1"
_ALLOWED_FIELDS = {"schema_version", "workspace_path", "audit_path"}


class OperatorConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class OperatorConfiguration:
    schema_version: str
    source_path: Path
    workspace_path: Path
    audit_path: Path
    identity: str
    digest: str


def load_configuration(path: str | Path) -> OperatorConfiguration:
    source = Path(path).resolve()
    try:
        raw = source.read_bytes()
    except OSError as exc:
        raise OperatorConfigurationError("configuration file is unreadable.") from exc
    try:
        data: Any = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise OperatorConfigurationError("configuration file is invalid JSON.") from exc
    if not isinstance(data, dict):
        raise OperatorConfigurationError("configuration must be an object.")
    if set(data) != _ALLOWED_FIELDS:
        raise OperatorConfigurationError(
            "configuration must contain exactly schema_version, workspace_path, and audit_path."
        )
    if data["schema_version"] != CONFIGURATION_SCHEMA_VERSION:
        raise OperatorConfigurationError("configuration schema_version is unsupported.")
    workspace = _resolve_explicit_path(source.parent, data["workspace_path"], "workspace_path")
    audit = _resolve_explicit_path(source.parent, data["audit_path"], "audit_path")
    if audit == workspace:
        raise OperatorConfigurationError("audit_path must be a file path distinct from workspace_path.")
    canonical = json.dumps(data, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    digest = sha256(canonical).hexdigest()
    identity = sha256((str(source) + "\n" + digest).encode("utf-8")).hexdigest()
    return OperatorConfiguration(
        schema_version=CONFIGURATION_SCHEMA_VERSION,
        source_path=source,
        workspace_path=workspace,
        audit_path=audit,
        identity=identity,
        digest=digest,
    )


def _resolve_explicit_path(base: Path, value: object, field_name: str) -> Path:
    if not isinstance(value, str) or value.strip() == "":
        raise OperatorConfigurationError(f"{field_name} must be a non-empty string.")
    if any(character in value for character in "*?[]"):
        raise OperatorConfigurationError(f"{field_name} must not contain wildcard syntax.")
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = base / candidate
    return candidate.resolve()


__all__ = (
    "CONFIGURATION_SCHEMA_VERSION",
    "OperatorConfiguration",
    "OperatorConfigurationError",
    "load_configuration",
)
