"""Deterministic EvidenceCandidate snapshot digest contracts and policy."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from types import MappingProxyType
from unicodedata import normalize

from rie.application.evidence_candidate import EvidenceCandidate


EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_ID = "rcis-evidence-candidate-snapshot"
EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_VERSION = "1.0.0"
EVIDENCE_CANDIDATE_SNAPSHOT_CANONICALIZATION_CONTRACT_VERSION = (
    "candidate-json-v1"
)
EVIDENCE_CANDIDATE_SNAPSHOT_DIGEST_ALGORITHM = "sha256"

EVIDENCE_CANDIDATE_SNAPSHOT_KEYS = (
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
    "locator",
    "warnings",
    "errors",
    "candidate_contract_version",
)

_STRING_FIELDS = frozenset(
    key
    for key in EVIDENCE_CANDIDATE_SNAPSHOT_KEYS
    if key not in {"raw_payload", "locator", "warnings", "errors"}
)


def _require_non_empty_string(value: object, field_name: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return normalize("NFC", value)


def _canonical_value(value: object, field_name: str) -> object:
    if type(value) is str:
        return normalize("NFC", value)
    if type(value) in (bool, int):
        return value
    if type(value) is float:
        if not isfinite(value):
            raise ValueError(f"{field_name} must contain only finite floats")
        return value
    if type(value) is tuple:
        return tuple(
            _canonical_value(item, f"{field_name}[{index}]")
            for index, item in enumerate(value)
        )
    if type(value) is MappingProxyType:
        return tuple(
            (
                _canonical_value(key, f"{field_name}.key[{index}]"),
                _canonical_value(item, f"{field_name}.value[{index}]"),
            )
            for index, (key, item) in enumerate(value.items())
        )
    if value is None:
        raise ValueError(f"{field_name} must not contain null")
    if isinstance(value, (list, dict, set, bytearray)):
        raise ValueError(f"{field_name} must use an immutable representation")
    raise ValueError(
        f"{field_name} contains an unsupported value type: "
        f"{type(value).__name__}"
    )


def _candidate_values(candidate: EvidenceCandidate) -> dict[str, object]:
    if type(candidate) is not EvidenceCandidate:
        raise ValueError("candidate must be an exact EvidenceCandidate")

    values: dict[str, object] = {}

    for key in EVIDENCE_CANDIDATE_SNAPSHOT_KEYS:
        value = getattr(candidate, key)

        if key in _STRING_FIELDS:
            values[key] = _require_non_empty_string(value, key)
            continue

        if key in {"warnings", "errors"}:
            if type(value) is not tuple:
                raise ValueError(f"{key} must be a tuple")
            values[key] = tuple(
                _require_non_empty_string(item, f"{key}[{index}]")
                for index, item in enumerate(value)
            )
            continue

        values[key] = _canonical_value(value, key)

    return values


@dataclass(frozen=True)
class EvidenceCandidateSnapshotResult:
    candidate_snapshot_digest: str
    digest_algorithm: str
    snapshot_policy_id: str
    snapshot_policy_version: str
    canonicalization_contract_version: str
    canonical_byte_length: int

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.candidate_snapshot_digest,
            "candidate_snapshot_digest",
        )
        _require_non_empty_string(self.digest_algorithm, "digest_algorithm")
        _require_non_empty_string(self.snapshot_policy_id, "snapshot_policy_id")
        _require_non_empty_string(
            self.snapshot_policy_version,
            "snapshot_policy_version",
        )
        _require_non_empty_string(
            self.canonicalization_contract_version,
            "canonicalization_contract_version",
        )

        if self.digest_algorithm != EVIDENCE_CANDIDATE_SNAPSHOT_DIGEST_ALGORITHM:
            raise ValueError("digest_algorithm must be sha256")
        if self.snapshot_policy_id != EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_ID:
            raise ValueError("snapshot_policy_id must match the reviewed policy")
        if (
            self.snapshot_policy_version
            != EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_VERSION
        ):
            raise ValueError(
                "snapshot_policy_version must match the reviewed policy"
            )
        if (
            self.canonicalization_contract_version
            != EVIDENCE_CANDIDATE_SNAPSHOT_CANONICALIZATION_CONTRACT_VERSION
        ):
            raise ValueError(
                "canonicalization_contract_version must match the reviewed "
                "contract"
            )
        if (
            len(self.candidate_snapshot_digest) != 64
            or self.candidate_snapshot_digest
            != self.candidate_snapshot_digest.lower()
            or any(
                character not in "0123456789abcdef"
                for character in self.candidate_snapshot_digest
            )
        ):
            raise ValueError(
                "candidate_snapshot_digest must be 64 lowercase "
                "hexadecimal characters"
            )
        if (
            type(self.canonical_byte_length) is not int
            or self.canonical_byte_length <= 0
        ):
            raise ValueError(
                "canonical_byte_length must be a positive integer"
            )


def canonicalize_evidence_candidate_snapshot(
    candidate: EvidenceCandidate,
) -> bytes:
    canonical_text = json.dumps(
        _candidate_values(candidate),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )
    return canonical_text.encode("utf-8")


def calculate_evidence_candidate_snapshot(
    candidate: EvidenceCandidate,
) -> EvidenceCandidateSnapshotResult:
    canonical_bytes = canonicalize_evidence_candidate_snapshot(candidate)
    digest_hex = sha256(canonical_bytes).hexdigest()

    return EvidenceCandidateSnapshotResult(
        candidate_snapshot_digest=digest_hex,
        digest_algorithm=EVIDENCE_CANDIDATE_SNAPSHOT_DIGEST_ALGORITHM,
        snapshot_policy_id=EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_ID,
        snapshot_policy_version=EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_VERSION,
        canonicalization_contract_version=(
            EVIDENCE_CANDIDATE_SNAPSHOT_CANONICALIZATION_CONTRACT_VERSION
        ),
        canonical_byte_length=len(canonical_bytes),
    )
