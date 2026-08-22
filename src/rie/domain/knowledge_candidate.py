"""Immutable KnowledgeCandidate domain and deterministic identity contracts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from math import isfinite
import re
from typing import TypeAlias
import unicodedata


KNOWLEDGE_CANDIDATE_CONTRACT_VERSION = "knowledge-candidate-v1"
KNOWLEDGE_CANDIDATE_IDENTITY_POLICY_ID = (
    "rcis-knowledge-candidate-identity"
)
KNOWLEDGE_CANDIDATE_IDENTITY_POLICY_VERSION = "1.0.0"
KNOWLEDGE_CANDIDATE_CANONICALIZATION_CONTRACT = (
    "knowledge-candidate-json-v1"
)
KNOWLEDGE_CANDIDATE_ID_PREFIX = "kc1_"
KNOWLEDGE_CANDIDATE_DIGEST_ALGORITHM = "sha256"

VERBATIM_TEXT_STATEMENT_TYPE = "verbatim_text_fact"
IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE = "image_structural_fact"
PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE = "product_variant_identity"
_SUPPORTED_STATEMENT_TYPES = frozenset(
    {
        VERBATIM_TEXT_STATEMENT_TYPE,
        IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE,
        PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE,
    }
)
INITIAL_AUTHORITY_STATUS = "unassessed"
INITIAL_LIFECYCLE_STATUS = "candidate"
INITIAL_REVIEW_STATUS = "pending_review"
INITIAL_CONFLICT_STATUS = "not_assessed"

LocatorValue: TypeAlias = str | int | float | bool | tuple["LocatorValue", ...]

_KNOWLEDGE_CANDIDATE_ID_PATTERN = re.compile(r"^kc1_[0-9a-f]{64}$")
_EVIDENCE_ID_PATTERN = re.compile(r"^ev1_[0-9a-f]{64}$")
_ACCEPTANCE_RECORD_ID_PATTERN = re.compile(r"^ar1_[0-9a-f]{64}$")
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_DIAGNOSTIC_SEVERITIES = frozenset({"info", "warning"})


def _require_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_pattern(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> None:
    _require_string(value, field_name)
    if pattern.fullmatch(value) is None:
        raise ValueError(f"{field_name} has an invalid format")


def _require_tuple(value: object, field_name: str) -> tuple[object, ...]:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")
    return value


def _require_unique_ordered_strings(
    value: object,
    field_name: str,
    *,
    allow_empty: bool,
    pattern: re.Pattern[str] | None = None,
) -> None:
    items = _require_tuple(value, field_name)
    if not allow_empty and not items:
        raise ValueError(f"{field_name} must not be empty")

    for index, item in enumerate(items):
        if pattern is None:
            _require_string(item, f"{field_name}[{index}]")
        else:
            _require_pattern(item, f"{field_name}[{index}]", pattern)

    if len(set(items)) != len(items):
        raise ValueError(f"{field_name} must contain unique values")
    if items != tuple(sorted(items)):
        raise ValueError(f"{field_name} must be lexicographically ordered")


def _validate_locator_value(value: object, field_name: str) -> None:
    if type(value) is str:
        _require_string(value, field_name)
        return
    if type(value) in (int, bool):
        return
    if type(value) is float:
        if not isfinite(value):
            raise ValueError(f"{field_name} must contain finite floats")
        return
    if type(value) is not tuple or not value:
        raise ValueError(f"{field_name} must be an immutable non-empty value")
    for index, item in enumerate(value):
        _validate_locator_value(item, f"{field_name}[{index}]")


@dataclass(frozen=True)
class KnowledgeDiagnostic:
    code: str
    severity: str
    message: str
    field: str
    source: str

    def __post_init__(self) -> None:
        for field_name in ("code", "severity", "message", "field", "source"):
            _require_string(getattr(self, field_name), field_name)
        if self.severity not in _DIAGNOSTIC_SEVERITIES:
            raise ValueError("severity must be info or warning")


@dataclass(frozen=True)
class KnowledgeEvidenceSupport:
    evidence_id: str
    acceptance_record_ids: tuple[str, ...]
    acceptance_review_record_ids: tuple[str, ...]
    source_id: str
    source_content_digest: str
    source_authority_status: str
    source_lifecycle_status: str
    payload_digest: str
    locator_type: str
    locator_value: LocatorValue
    locator_schema_version: str

    def __post_init__(self) -> None:
        _require_pattern(self.evidence_id, "evidence_id", _EVIDENCE_ID_PATTERN)
        _require_unique_ordered_strings(
            self.acceptance_record_ids,
            "acceptance_record_ids",
            allow_empty=False,
            pattern=_ACCEPTANCE_RECORD_ID_PATTERN,
        )
        _require_unique_ordered_strings(
            self.acceptance_review_record_ids,
            "acceptance_review_record_ids",
            allow_empty=False,
        )
        for field_name in (
            "source_id",
            "source_authority_status",
            "source_lifecycle_status",
            "locator_type",
            "locator_schema_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _require_pattern(
            self.source_content_digest,
            "source_content_digest",
            _DIGEST_PATTERN,
        )
        _require_pattern(self.payload_digest, "payload_digest", _DIGEST_PATTERN)
        _validate_locator_value(self.locator_value, "locator_value")


def _validate_support(value: object) -> None:
    items = _require_tuple(value, "support")
    if not items:
        raise ValueError("support must not be empty")
    evidence_ids: list[str] = []
    for index, item in enumerate(items):
        if type(item) is not KnowledgeEvidenceSupport:
            raise ValueError(
                f"support[{index}] must be an exact KnowledgeEvidenceSupport"
            )
        evidence_ids.append(item.evidence_id)
    if len(set(evidence_ids)) != len(evidence_ids):
        raise ValueError("support must contain unique Evidence IDs")
    if evidence_ids != sorted(evidence_ids):
        raise ValueError("support must be ordered by Evidence ID")


def _validate_initial_states(
    authority_status: object,
    lifecycle_status: object,
    review_status: object,
    conflict_status: object,
    conflict_ids: object | None = None,
) -> None:
    expected = (
        (authority_status, INITIAL_AUTHORITY_STATUS, "authority_status"),
        (lifecycle_status, INITIAL_LIFECYCLE_STATUS, "lifecycle_status"),
        (review_status, INITIAL_REVIEW_STATUS, "review_status"),
        (conflict_status, INITIAL_CONFLICT_STATUS, "conflict_status"),
    )
    for observed, required, field_name in expected:
        _require_string(observed, field_name)
        if observed != required:
            raise ValueError(f"{field_name} must be {required}")
    if conflict_ids is not None:
        items = _require_tuple(conflict_ids, "conflict_ids")
        if items:
            raise ValueError("not_assessed conflict status requires no conflict IDs")


@dataclass(frozen=True)
class KnowledgeCandidateIdentityInput:
    candidate_contract_version: str
    statement_type: str
    statement: str
    construction_rule_id: str
    construction_rule_version: str
    support: tuple[KnowledgeEvidenceSupport, ...]
    authority_status: str
    lifecycle_status: str
    review_status: str
    conflict_status: str

    def __post_init__(self) -> None:
        if self.candidate_contract_version != KNOWLEDGE_CANDIDATE_CONTRACT_VERSION:
            raise ValueError("unsupported candidate_contract_version")
        for field_name in (
            "statement_type",
            "statement",
            "construction_rule_id",
            "construction_rule_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        if self.statement_type not in _SUPPORTED_STATEMENT_TYPES:
            raise ValueError("unsupported statement_type")
        _validate_support(self.support)
        _validate_initial_states(
            self.authority_status,
            self.lifecycle_status,
            self.review_status,
            self.conflict_status,
        )


def _canonicalize(value: object) -> object:
    if type(value) is str:
        return unicodedata.normalize("NFC", value)
    if type(value) is tuple:
        return [_canonicalize(item) for item in value]
    if value is None or type(value) in (int, float, bool):
        return value
    raise ValueError("identity projection contains an unsupported value")


def canonical_knowledge_candidate_identity_projection(
    identity_input: KnowledgeCandidateIdentityInput,
) -> dict[str, object]:
    if type(identity_input) is not KnowledgeCandidateIdentityInput:
        raise ValueError(
            "identity_input must be an exact KnowledgeCandidateIdentityInput"
        )

    support_projection = []
    for item in identity_input.support:
        support_projection.append(
            {
                "acceptance_record_ids": _canonicalize(
                    item.acceptance_record_ids
                ),
                "evidence_id": _canonicalize(item.evidence_id),
                "locator_schema_version": _canonicalize(
                    item.locator_schema_version
                ),
                "locator_type": _canonicalize(item.locator_type),
                "locator_value": _canonicalize(item.locator_value),
                "payload_digest": _canonicalize(item.payload_digest),
                "source_content_digest": _canonicalize(
                    item.source_content_digest
                ),
                "source_id": _canonicalize(item.source_id),
            }
        )

    return {
        "authority_status": _canonicalize(identity_input.authority_status),
        "candidate_contract_version": _canonicalize(
            identity_input.candidate_contract_version
        ),
        "canonicalization_contract": (
            KNOWLEDGE_CANDIDATE_CANONICALIZATION_CONTRACT
        ),
        "conflict_status": _canonicalize(identity_input.conflict_status),
        "construction_rule_id": _canonicalize(
            identity_input.construction_rule_id
        ),
        "construction_rule_version": _canonicalize(
            identity_input.construction_rule_version
        ),
        "lifecycle_status": _canonicalize(identity_input.lifecycle_status),
        "review_status": _canonicalize(identity_input.review_status),
        "statement": _canonicalize(identity_input.statement),
        "statement_type": _canonicalize(identity_input.statement_type),
        "support": support_projection,
    }


def canonical_knowledge_candidate_identity_bytes(
    identity_input: KnowledgeCandidateIdentityInput,
) -> bytes:
    projection = canonical_knowledge_candidate_identity_projection(
        identity_input
    )
    return json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def compute_knowledge_candidate_id(
    identity_input: KnowledgeCandidateIdentityInput,
) -> str:
    digest = hashlib.sha256(
        canonical_knowledge_candidate_identity_bytes(identity_input)
    ).hexdigest()
    return f"{KNOWLEDGE_CANDIDATE_ID_PREFIX}{digest}"


@dataclass(frozen=True)
class KnowledgeCandidate:
    knowledge_candidate_id: str
    contract_version: str
    statement_type: str
    statement: str
    support: tuple[KnowledgeEvidenceSupport, ...]
    construction_rule_id: str
    construction_rule_version: str
    authority_status: str
    lifecycle_status: str
    review_status: str
    conflict_status: str
    conflict_ids: tuple[str, ...]
    diagnostics: tuple[KnowledgeDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_pattern(
            self.knowledge_candidate_id,
            "knowledge_candidate_id",
            _KNOWLEDGE_CANDIDATE_ID_PATTERN,
        )
        if self.contract_version != KNOWLEDGE_CANDIDATE_CONTRACT_VERSION:
            raise ValueError("unsupported contract_version")
        if self.statement_type not in _SUPPORTED_STATEMENT_TYPES:
            raise ValueError("unsupported statement_type")
        for field_name in (
            "statement",
            "construction_rule_id",
            "construction_rule_version",
        ):
            _require_string(getattr(self, field_name), field_name)
        _validate_support(self.support)
        _validate_initial_states(
            self.authority_status,
            self.lifecycle_status,
            self.review_status,
            self.conflict_status,
            self.conflict_ids,
        )
        diagnostics = _require_tuple(self.diagnostics, "diagnostics")
        for index, diagnostic in enumerate(diagnostics):
            if type(diagnostic) is not KnowledgeDiagnostic:
                raise ValueError(
                    f"diagnostics[{index}] must be an exact KnowledgeDiagnostic"
                )

        if self.knowledge_candidate_id != compute_knowledge_candidate_id(
            identity_input_from_knowledge_candidate(self)
        ):
            raise ValueError("knowledge_candidate_id does not match identity")


def identity_input_from_knowledge_candidate(
    candidate: KnowledgeCandidate,
) -> KnowledgeCandidateIdentityInput:
    if type(candidate) is not KnowledgeCandidate:
        raise ValueError("candidate must be an exact KnowledgeCandidate")
    return KnowledgeCandidateIdentityInput(
        candidate_contract_version=candidate.contract_version,
        statement_type=candidate.statement_type,
        statement=candidate.statement,
        construction_rule_id=candidate.construction_rule_id,
        construction_rule_version=candidate.construction_rule_version,
        support=candidate.support,
        authority_status=candidate.authority_status,
        lifecycle_status=candidate.lifecycle_status,
        review_status=candidate.review_status,
        conflict_status=candidate.conflict_status,
    )
