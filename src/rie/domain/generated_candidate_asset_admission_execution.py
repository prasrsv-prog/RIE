from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re

ADMISSION_OUTCOME_ADMITTED = "ADMITTED"

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _require_ascii_nonempty(value: object, name: str) -> str:
    if type(value) is not str:
        raise ValueError(f"{name} must be an exact str")
    if not value or value != value.strip():
        raise ValueError(f"{name} must be nonempty with no surrounding whitespace")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{name} must be ASCII") from exc
    return value


def _require_sha256(value: object, name: str) -> str:
    text = _require_ascii_nonempty(value, name)
    if _SHA256_PATTERN.fullmatch(text) is None:
        raise ValueError(f"{name} must be a lowercase 64-hex SHA256")
    return text


def _require_aware_datetime(value: object, name: str) -> datetime:
    if type(value) is not datetime:
        raise ValueError(f"{name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _require_provenance(value: object) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise ValueError("deterministic_provenance must be a nonempty tuple")
    normalized: list[str] = []
    for index, entry in enumerate(value):
        normalized.append(
            _require_ascii_nonempty(
                entry,
                f"deterministic_provenance[{index}]",
            )
        )
    if len(set(normalized)) != len(normalized):
        raise ValueError("deterministic_provenance must not contain duplicates")
    return tuple(normalized)


@dataclass(frozen=True)
class GeneratedCandidateAssetAdmissionExecution:
    asset_admission_execution_id: str
    authorization_id: str
    decision_id: str
    evaluation_id: str
    candidate_id: str
    candidate_checksum: str
    admitted_asset_reference: str
    execution_actor_reference: str
    execution_timestamp: datetime
    execution_outcome: str
    deterministic_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_sha256(
            self.asset_admission_execution_id,
            "asset_admission_execution_id",
        )
        _require_sha256(self.authorization_id, "authorization_id")
        _require_sha256(self.decision_id, "decision_id")
        _require_ascii_nonempty(self.evaluation_id, "evaluation_id")
        _require_ascii_nonempty(self.candidate_id, "candidate_id")
        _require_sha256(self.candidate_checksum, "candidate_checksum")
        _require_ascii_nonempty(
            self.admitted_asset_reference,
            "admitted_asset_reference",
        )
        _require_ascii_nonempty(
            self.execution_actor_reference,
            "execution_actor_reference",
        )
        _require_aware_datetime(
            self.execution_timestamp,
            "execution_timestamp",
        )
        if self.execution_outcome != ADMISSION_OUTCOME_ADMITTED:
            raise ValueError("execution_outcome must be exactly ADMITTED")
        _require_provenance(self.deterministic_provenance)


__all__ = [
    "ADMISSION_OUTCOME_ADMITTED",
    "GeneratedCandidateAssetAdmissionExecution",
]
