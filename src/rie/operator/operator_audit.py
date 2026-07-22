"""Deterministic append-only operator audit records."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

from rie.operator.operator_configuration import OperatorConfiguration
from rie.operator.operator_contract import OPERATOR_CONTRACT_VERSION
from rie.operator.operator_contract import OperatorRequest
from rie.operator.operator_contract import OperatorResult
from rie.operator.operator_contract import PACKAGE_VERSION
from rie.operator.operator_result import to_dict as result_to_dict

AUDIT_SCHEMA_VERSION = "rie_operator_audit_v1"


class OperatorAuditError(OSError):
    pass


def derive_operation_id(
    request: OperatorRequest,
    configuration: OperatorConfiguration,
) -> str:
    payload = {
        "command": request.command,
        "arguments": list(request.arguments),
        "output_path": request.output_path or "",
        "dry_run": request.dry_run,
        "configuration_identity": configuration.identity,
        "configuration_digest": configuration.digest,
        "package_version": PACKAGE_VERSION,
        "operator_contract_version": OPERATOR_CONTRACT_VERSION,
    }
    return sha256(_canonical_bytes(payload)).hexdigest()


def audit_preview(
    *,
    request: OperatorRequest,
    configuration: OperatorConfiguration,
    result: OperatorResult,
) -> dict[str, str]:
    operation_id = derive_operation_id(request, configuration)
    sequence = _operation_sequence(configuration.audit_path, operation_id)
    audit_id = _audit_id(operation_id, sequence, result.status.value)
    prior = _prior_audit_id(configuration.audit_path, operation_id)
    return {
        "audit_id": audit_id,
        "operation_id": operation_id,
        "sequence": str(sequence),
        "prior_audit_id": prior,
        "persisted": "false",
    }


def persist_audit(
    *,
    request: OperatorRequest,
    configuration: OperatorConfiguration,
    result: OperatorResult,
) -> dict[str, str]:
    preview = audit_preview(
        request=request,
        configuration=configuration,
        result=result,
    )
    record = {
        "audit_schema_version": AUDIT_SCHEMA_VERSION,
        "audit_id": preview["audit_id"],
        "operation_id": preview["operation_id"],
        "sequence": int(preview["sequence"]),
        "prior_audit_id": preview["prior_audit_id"],
        "command": request.command,
        "arguments": list(request.arguments),
        "output_path": request.output_path or "",
        "dry_run": request.dry_run,
        "package_version": PACKAGE_VERSION,
        "operator_contract_version": OPERATOR_CONTRACT_VERSION,
        "configuration_identity": configuration.identity,
        "configuration_digest": configuration.digest,
        "result": result_to_dict(result),
    }
    records = list(read_audit_records(configuration.audit_path))
    if any(item.get("audit_id") == record["audit_id"] for item in records):
        raise OperatorAuditError("audit identity collision.")
    records.append(record)
    _write_records(configuration.audit_path, records)
    preview["persisted"] = "true"
    return preview


def read_audit_records(path: str | Path) -> Iterable[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return ()
    try:
        lines = source.read_text(encoding="ascii").splitlines()
        values = tuple(json.loads(line) for line in lines if line.strip())
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OperatorAuditError("audit file is unreadable or invalid.") from exc
    if any(not isinstance(value, dict) for value in values):
        raise OperatorAuditError("audit file contains a non-object record.")
    return values


def find_audit(path: str | Path, audit_id: str) -> dict[str, Any] | None:
    for record in read_audit_records(path):
        if record.get("audit_id") == audit_id:
            return record
    return None


def _operation_sequence(path: Path, operation_id: str) -> int:
    return sum(
        1
        for record in read_audit_records(path)
        if record.get("operation_id") == operation_id
    )


def _prior_audit_id(path: Path, operation_id: str) -> str:
    matching = [
        str(record.get("audit_id", ""))
        for record in read_audit_records(path)
        if record.get("operation_id") == operation_id
    ]
    return matching[-1] if matching else ""


def _audit_id(operation_id: str, sequence: int, status: str) -> str:
    return sha256(
        f"{operation_id}\n{sequence}\n{status}".encode("ascii")
    ).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _write_records(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "".join(
        json.dumps(
            record,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for record in records
    ).encode("ascii")
    temporary = path.with_name("." + path.name + ".tmp")
    if temporary.exists():
        raise OperatorAuditError("audit temporary path already exists.")
    try:
        temporary.write_bytes(payload)
        temporary.replace(path)
    except OSError as exc:
        try:
            if temporary.exists():
                temporary.unlink()
        except OSError:
            pass
        raise OperatorAuditError("audit persistence failed.") from exc


__all__ = (
    "AUDIT_SCHEMA_VERSION",
    "OperatorAuditError",
    "derive_operation_id",
    "audit_preview",
    "persist_audit",
    "read_audit_records",
    "find_audit",
)
