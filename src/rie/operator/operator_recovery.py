"""Deterministic fail-closed recovery guidance."""

from __future__ import annotations

_GUIDANCE = {
    "CLI_USAGE_INVALID": "Correct the explicit command arguments and run the command again.",
    "CONFIGURATION_INVALID": "Correct the explicit configuration file and run the command again.",
    "SOURCE_OR_INPUT_INVALID": "Verify the exact input identity, path, and digest before running again.",
    "CONTRACT_OR_ELIGIBILITY_REJECTED": "Resolve the reported contract or eligibility issue without bypassing governed policy.",
    "STATE_CONFLICT_OR_IDEMPOTENCY_VIOLATION": "Inspect the existing output and audit record; use a new explicit output only when the governed input changed.",
    "PERSISTENCE_OR_IO_FAILURE": "Restore access to the reported path and repeat the same command; do not edit persisted artifacts manually.",
    "AUDIT_OR_EXPORT_FAILURE": "Restore the audit or export destination and repeat the same command; do not discard prior evidence.",
    "UNEXPECTED_INTERNAL_FAILURE": "Preserve the audit preview and failure details, then obtain an implementation review before retrying.",
}


def recovery_for(issue_code: str) -> dict[str, str]:
    instruction = _GUIDANCE.get(
        issue_code,
        "Preserve the failure evidence and obtain a controlled review before retrying.",
    )
    return {
        "safe_to_repeat": "true",
        "instruction": instruction,
        "prohibited_actions": (
            "blind deletion; manual persisted-artifact editing; history reset; "
            "force push; hidden replacement; contract bypass"
        ),
    }


__all__ = ("recovery_for",)
