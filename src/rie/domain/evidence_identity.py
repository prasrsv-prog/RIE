"""Deterministic factual Evidence identity contracts and policy."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from math import isfinite
from unicodedata import normalize

from rie.domain.accepted_evidence import AcceptedEvidence, LocatorValue


EVIDENCE_IDENTITY_POLICY_ID = "rcis-evidence-identity"
EVIDENCE_IDENTITY_POLICY_VERSION = "1.0.0"
EVIDENCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION = "identity-json-v1"
EVIDENCE_IDENTITY_DIGEST_ALGORITHM = "sha256"
EVIDENCE_ID_PREFIX = "ev1_"

_IDENTITY_KEYS = (
    "accepted_evidence_contract_version",
    "source_identifier",
    "source_content_digest",
    "producer_name",
    "producer_version",
    "producer_kind",
    "producer_contract_version",
    "payload_type",
    "payload_schema_version",
    "payload_digest",
    "canonical_locator_type",
    "canonical_locator_value",
    "locator_schema_version",
    "producer_output_digest",
)


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _validate_locator_value(value: object, field_name: str) -> None:
    if type(value) is str:
        _require_string(value, field_name)
        return
    if type(value) in (int, bool):
        return
    if type(value) is float:
        if not isfinite(value):
            raise ValueError(f"{field_name} must contain only finite floats")
        return
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be an immutable scalar or tuple")
    if not value:
        raise ValueError(f"{field_name} must not be empty")
    for index, item in enumerate(value):
        _validate_locator_value(item, f"{field_name}[{index}]")


def _normalize_locator_value(value: LocatorValue) -> LocatorValue:
    if type(value) is str:
        return normalize("NFC", value)
    if type(value) is tuple:
        return tuple(_normalize_locator_value(item) for item in value)
    return value


@dataclass(frozen=True)
class EvidenceIdentityInput:
    accepted_evidence_contract_version: str
    source_identifier: str
    source_content_digest: str
    producer_name: str
    producer_version: str
    producer_kind: str
    producer_contract_version: str
    payload_type: str
    payload_schema_version: str
    payload_digest: str
    canonical_locator_type: str
    canonical_locator_value: LocatorValue
    locator_schema_version: str
    producer_output_digest: str

    def __post_init__(self) -> None:
        for field_name in _IDENTITY_KEYS:
            if field_name == "canonical_locator_value":
                _validate_locator_value(
                    self.canonical_locator_value,
                    field_name,
                )
            else:
                _require_string(getattr(self, field_name), field_name)


@dataclass(frozen=True)
class EvidenceIdentityResult:
    evidence_id: str
    digest_algorithm: str
    digest_hex: str
    identity_policy_id: str
    identity_policy_version: str
    canonicalization_contract_version: str
    canonical_byte_length: int

    def __post_init__(self) -> None:
        _require_string(self.evidence_id, "evidence_id")
        _require_string(self.digest_algorithm, "digest_algorithm")
        _require_string(self.digest_hex, "digest_hex")
        _require_string(self.identity_policy_id, "identity_policy_id")
        _require_string(
            self.identity_policy_version,
            "identity_policy_version",
        )
        _require_string(
            self.canonicalization_contract_version,
            "canonicalization_contract_version",
        )
        if self.digest_algorithm != EVIDENCE_IDENTITY_DIGEST_ALGORITHM:
            raise ValueError("digest_algorithm must be sha256")
        if (
            len(self.digest_hex) != 64
            or self.digest_hex != self.digest_hex.lower()
            or any(character not in "0123456789abcdef" for character in self.digest_hex)
        ):
            raise ValueError("digest_hex must be 64 lowercase hexadecimal characters")
        if self.evidence_id != f"{EVIDENCE_ID_PREFIX}{self.digest_hex}":
            raise ValueError("evidence_id must equal ev1_ followed by digest_hex")
        if type(self.canonical_byte_length) is not int or self.canonical_byte_length <= 0:
            raise ValueError("canonical_byte_length must be a positive integer")


def identity_input_from_accepted_evidence(
    accepted_evidence: AcceptedEvidence,
) -> EvidenceIdentityInput:
    if type(accepted_evidence) is not AcceptedEvidence:
        raise ValueError("accepted_evidence must be an exact AcceptedEvidence")

    return EvidenceIdentityInput(
        accepted_evidence_contract_version=accepted_evidence.contract_version,
        source_identifier=accepted_evidence.source_snapshot.source_id,
        source_content_digest=(
            accepted_evidence.source_snapshot.source_content_digest
        ),
        producer_name=accepted_evidence.producer_snapshot.producer_name,
        producer_version=accepted_evidence.producer_snapshot.producer_version,
        producer_kind=accepted_evidence.producer_snapshot.producer_kind,
        producer_contract_version=(
            accepted_evidence.producer_snapshot.producer_contract_version
        ),
        payload_type=accepted_evidence.factual_payload.payload_type,
        payload_schema_version=(
            accepted_evidence.factual_payload.payload_schema_version
        ),
        payload_digest=accepted_evidence.factual_payload.payload_digest,
        canonical_locator_type=(
            accepted_evidence.factual_payload.locator.locator_type
        ),
        canonical_locator_value=(
            accepted_evidence.factual_payload.locator.locator_value
        ),
        locator_schema_version=(
            accepted_evidence.factual_payload.locator.locator_schema_version
        ),
        producer_output_digest=accepted_evidence.provenance.producer_output_digest,
    )


def canonicalize_evidence_identity(
    identity_input: EvidenceIdentityInput,
) -> bytes:
    if type(identity_input) is not EvidenceIdentityInput:
        raise ValueError("identity_input must be an exact EvidenceIdentityInput")

    canonical_values: dict[str, object] = {}

    for key in _IDENTITY_KEYS:
        value = getattr(identity_input, key)
        if key == "canonical_locator_value":
            canonical_values[key] = _normalize_locator_value(value)
        else:
            canonical_values[key] = normalize("NFC", value)

    canonical_text = json.dumps(
        canonical_values,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )
    return canonical_text.encode("utf-8")


def calculate_evidence_identity(
    identity_input: EvidenceIdentityInput,
) -> EvidenceIdentityResult:
    canonical_bytes = canonicalize_evidence_identity(identity_input)
    digest_hex = sha256(canonical_bytes).hexdigest()

    return EvidenceIdentityResult(
        evidence_id=f"{EVIDENCE_ID_PREFIX}{digest_hex}",
        digest_algorithm=EVIDENCE_IDENTITY_DIGEST_ALGORITHM,
        digest_hex=digest_hex,
        identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
        canonicalization_contract_version=(
            EVIDENCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION
        ),
        canonical_byte_length=len(canonical_bytes),
    )
