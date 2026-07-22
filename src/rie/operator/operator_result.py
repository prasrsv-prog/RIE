"""Deterministic human and JSON operator result rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rie.operator.operator_contract import OperatorResult
from rie.operator.operator_contract import thaw_mapping

RESULT_FIELD_ORDER = (
    "schema_version",
    "command",
    "status",
    "exit_code",
    "issue_code",
    "message",
    "dry_run",
    "identifiers",
    "provenance",
    "audit",
    "outputs",
    "recovery",
)


def to_dict(result: OperatorResult) -> dict[str, Any]:
    if not isinstance(result, OperatorResult):
        raise TypeError("result must be OperatorResult.")
    return {
        "schema_version": result.schema_version,
        "command": result.command,
        "status": result.status.value,
        "exit_code": int(result.exit_code),
        "issue_code": result.issue_code,
        "message": result.message,
        "dry_run": result.dry_run,
        "identifiers": thaw_mapping(result.identifiers),
        "provenance": thaw_mapping(result.provenance),
        "audit": thaw_mapping(result.audit),
        "outputs": thaw_mapping(result.outputs),
        "recovery": thaw_mapping(result.recovery),
    }


def render_json(result: OperatorResult) -> str:
    return json.dumps(
        to_dict(result),
        ensure_ascii=True,
        indent=2,
        separators=(",", ": "),
    )


def render_human(result: OperatorResult) -> str:
    payload = to_dict(result)
    lines = [
        "RIE Operator Result",
        f"command: {payload['command']}",
        f"status: {payload['status']}",
        f"exit_code: {payload['exit_code']}",
        f"issue_code: {payload['issue_code']}",
        f"message: {payload['message']}",
        f"dry_run: {str(payload['dry_run']).lower()}",
    ]
    for section in ("identifiers", "provenance", "audit", "outputs", "recovery"):
        lines.append(f"{section}:")
        values = payload[section]
        if values:
            for key in sorted(values):
                lines.append(f"  {key}: {values[key]}")
        else:
            lines.append("  none")
    return "\n".join(lines)


def render(result: OperatorResult, output_format: str) -> str:
    if output_format == "json":
        return render_json(result)
    if output_format == "human":
        return render_human(result)
    raise ValueError("output_format must be human or json.")


def write_rendered_result(path: str | Path, rendered: str) -> None:
    target = Path(path)
    if target.exists():
        raise FileExistsError("result output path already exists.")
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name("." + target.name + ".tmp")
    if temporary.exists():
        raise FileExistsError("result temporary output path already exists.")
    temporary.write_text(rendered.rstrip("\n") + "\n", encoding="ascii", newline="\n")
    temporary.replace(target)


__all__ = (
    "RESULT_FIELD_ORDER",
    "to_dict",
    "render_json",
    "render_human",
    "render",
    "write_rendered_result",
)
