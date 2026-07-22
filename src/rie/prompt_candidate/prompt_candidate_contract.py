from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final
import re

from rie.domain.governed_knowledge import GovernedKnowledge
from rie.domain.governed_knowledge_lifecycle_assertion_interpretation_result import (
    GovernedKnowledgeLifecycleAssertionInterpretationResult,
)
from rie.knowledge_repository.knowledge_repository_contract import (
    KnowledgeRepositoryLookupResult,
    KnowledgeRepositoryRevision,
)

PROMPT_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION: Final = (
    "prompt_candidate_construction_request_contract_v1"
)
PROMPT_INTENT_CONTRACT_VERSION: Final = "prompt_intent_contract_v1"
PROMPT_CANDIDATE_PROVENANCE_CONTRACT_VERSION: Final = (
    "prompt_candidate_provenance_contract_v1"
)
PROMPT_CANDIDATE_CONTRACT_VERSION: Final = "prompt_candidate_contract_v1"
PROMPT_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION: Final = (
    "prompt_candidate_construction_result_contract_v1"
)
PROMPT_CANDIDATE_ISSUE_CONTRACT_VERSION: Final = (
    "prompt_candidate_issue_contract_v1"
)
PROMPT_CANDIDATE_SCHEMA_ID: Final = "rcis.prompt_candidate.structural"
PROMPT_CANDIDATE_SCHEMA_VERSION: Final = "1.0.0"
PROMPT_CANDIDATE_CONSTRUCTION_POLICY_ID: Final = (
    "rcis-prompt-candidate-construction"
)
PROMPT_CANDIDATE_CONSTRUCTION_POLICY_VERSION: Final = "1.0.0"
PROMPT_CANDIDATE_DIGEST_ALGORITHM: Final = "sha256"
PROMPT_INTENT_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "prompt_intent_identity_json_v1"
)
PROMPT_CANDIDATE_PROVENANCE_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "prompt_candidate_provenance_identity_json_v1"
)
PROMPT_CANDIDATE_PAYLOAD_CANONICALIZATION_VERSION: Final = (
    "prompt_candidate_payload_json_v1"
)
PROMPT_CANDIDATE_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "prompt_candidate_identity_json_v1"
)
PROMPT_INTENT_ID_PREFIX: Final = "pi1_"
PROMPT_CANDIDATE_PROVENANCE_ID_PREFIX: Final = "pcp1_"
PROMPT_CANDIDATE_ID_PREFIX: Final = "pc1_"
PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED: Final = "constructed"
PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED: Final = "rejected"
PROMPT_CANDIDATE_ISSUE_CODES: Final = (
    "invalid_request",
    "unsupported_request_contract_version",
    "unsupported_prompt_candidate_schema",
    "unsupported_prompt_candidate_schema_version",
    "unsupported_construction_policy",
    "unsupported_construction_policy_version",
    "invalid_prompt_intent",
    "unsupported_prompt_intent_contract_version",
    "invalid_prompt_intent_field",
    "prompt_intent_id_mismatch",
    "invalid_source_revision_lookup_result",
    "unsupported_source_lookup_result_contract_version",
    "source_revision_not_found",
    "source_revision_lookup_rejected",
    "missing_source_revision",
    "invalid_source_revision",
    "source_revision_identity_mismatch",
    "missing_source_governed_knowledge",
    "source_governed_knowledge_identity_mismatch",
    "source_revision_payload_digest_mismatch",
    "missing_source_lifecycle_interpretation_result",
    "source_lifecycle_interpretation_result_mismatch",
    "missing_source_lineage_record",
    "source_lineage_mismatch",
    "missing_source_audit_record",
    "source_audit_mismatch",
    "provenance_identity_mismatch",
    "candidate_payload_digest_mismatch",
    "candidate_identity_mismatch",
    "internal_contract_violation",
)

_ISSUE_MESSAGES = MappingProxyType(
    {
        code: code.replace("_", " ").capitalize() + "."
        for code in PROMPT_CANDIDATE_ISSUE_CODES
    }
)
_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_PROMPT_INTENT_ID_PATTERN = re.compile(r"^pi1_[0-9a-f]{64}$")
_PROVENANCE_ID_PATTERN = re.compile(r"^pcp1_[0-9a-f]{64}$")
_CANDIDATE_ID_PATTERN = re.compile(r"^pc1_[0-9a-f]{64}$")


def _require_exact_string(value: object, field_name: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be an exact non-empty string")
    return value


def _require_optional_exact_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_exact_string(value, field_name)


def _require_pattern(
    value: object,
    field_name: str,
    pattern: re.Pattern[str],
) -> str:
    result = _require_exact_string(value, field_name)
    if pattern.fullmatch(result) is None:
        raise ValueError(f"{field_name} has an invalid format")
    return result


def _require_digest(value: object, field_name: str) -> str:
    return _require_pattern(value, field_name, _DIGEST_PATTERN)


def _require_constraint_tuple(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be an exact tuple")
    for item in value:
        _require_exact_string(item, field_name)
    if len(set(value)) != len(value):
        raise ValueError(f"{field_name} must not contain duplicates")
    return value


@dataclass(frozen=True)
class PromptIntent:
    contract_version: str
    intent_id: str
    objective: str
    audience: str | None
    language: str | None
    output_format: str | None
    required_constraints: tuple[str, ...]
    forbidden_constraints: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_exact_string(self.contract_version, "contract_version")
        _require_pattern(self.intent_id, "intent_id", _PROMPT_INTENT_ID_PATTERN)
        _require_exact_string(self.objective, "objective")
        _require_optional_exact_string(self.audience, "audience")
        _require_optional_exact_string(self.language, "language")
        _require_optional_exact_string(self.output_format, "output_format")
        required = _require_constraint_tuple(
            self.required_constraints,
            "required_constraints",
        )
        forbidden = _require_constraint_tuple(
            self.forbidden_constraints,
            "forbidden_constraints",
        )
        if set(required).intersection(forbidden):
            raise ValueError(
                "required_constraints and forbidden_constraints must not overlap"
            )


@dataclass(frozen=True)
class PromptCandidateConstructionRequest:
    contract_version: str
    source_revision_lookup_result: object
    prompt_intent: object
    prompt_candidate_schema_id: str
    prompt_candidate_schema_version: str
    construction_policy_id: str
    construction_policy_version: str

    def __post_init__(self) -> None:
        _require_exact_string(self.contract_version, "contract_version")
        _require_exact_string(
            self.prompt_candidate_schema_id,
            "prompt_candidate_schema_id",
        )
        _require_exact_string(
            self.prompt_candidate_schema_version,
            "prompt_candidate_schema_version",
        )
        _require_exact_string(
            self.construction_policy_id,
            "construction_policy_id",
        )
        _require_exact_string(
            self.construction_policy_version,
            "construction_policy_version",
        )


@dataclass(frozen=True)
class PromptCandidateProvenance:
    contract_version: str
    provenance_id: str
    source_lookup_result_contract_version: str
    source_revision_id: str
    source_governed_knowledge_id: str
    source_revision_number: int
    source_governed_knowledge_payload_digest: str
    source_lineage_record_id: str
    source_audit_id: str
    source_lifecycle_interpretation_result_id: str
    prompt_intent_id: str
    prompt_intent_digest: str
    prompt_candidate_schema_id: str
    prompt_candidate_schema_version: str
    construction_policy_id: str
    construction_policy_version: str

    def __post_init__(self) -> None:
        _require_exact_string(self.contract_version, "contract_version")
        _require_pattern(
            self.provenance_id,
            "provenance_id",
            _PROVENANCE_ID_PATTERN,
        )
        for field_name in (
            "source_lookup_result_contract_version",
            "source_revision_id",
            "source_governed_knowledge_id",
            "source_lineage_record_id",
            "source_audit_id",
            "source_lifecycle_interpretation_result_id",
            "prompt_candidate_schema_id",
            "prompt_candidate_schema_version",
            "construction_policy_id",
            "construction_policy_version",
        ):
            _require_exact_string(getattr(self, field_name), field_name)
        if type(self.source_revision_number) is not int or self.source_revision_number < 1:
            raise ValueError("source_revision_number must be a positive exact integer")
        _require_digest(
            self.source_governed_knowledge_payload_digest,
            "source_governed_knowledge_payload_digest",
        )
        _require_pattern(
            self.prompt_intent_id,
            "prompt_intent_id",
            _PROMPT_INTENT_ID_PATTERN,
        )
        _require_digest(self.prompt_intent_digest, "prompt_intent_digest")


@dataclass(frozen=True)
class PromptCandidate:
    contract_version: str
    candidate_id: str
    prompt_candidate_schema_id: str
    prompt_candidate_schema_version: str
    construction_policy_id: str
    construction_policy_version: str
    prompt_intent: PromptIntent
    source_revision: KnowledgeRepositoryRevision
    governed_knowledge: GovernedKnowledge
    lifecycle_interpretation_result: (
        GovernedKnowledgeLifecycleAssertionInterpretationResult
    )
    provenance: PromptCandidateProvenance
    candidate_payload_digest: str

    def __post_init__(self) -> None:
        _require_exact_string(self.contract_version, "contract_version")
        _require_pattern(self.candidate_id, "candidate_id", _CANDIDATE_ID_PATTERN)
        for field_name in (
            "prompt_candidate_schema_id",
            "prompt_candidate_schema_version",
            "construction_policy_id",
            "construction_policy_version",
        ):
            _require_exact_string(getattr(self, field_name), field_name)
        if type(self.prompt_intent) is not PromptIntent:
            raise ValueError("prompt_intent has an invalid type")
        if type(self.source_revision) is not KnowledgeRepositoryRevision:
            raise ValueError("source_revision has an invalid type")
        if type(self.governed_knowledge) is not GovernedKnowledge:
            raise ValueError("governed_knowledge has an invalid type")
        if type(self.lifecycle_interpretation_result) is not (
            GovernedKnowledgeLifecycleAssertionInterpretationResult
        ):
            raise ValueError("lifecycle_interpretation_result has an invalid type")
        if type(self.provenance) is not PromptCandidateProvenance:
            raise ValueError("provenance has an invalid type")
        _require_digest(
            self.candidate_payload_digest,
            "candidate_payload_digest",
        )


@dataclass(frozen=True)
class PromptCandidateIssue:
    code: str
    message: str

    def __post_init__(self) -> None:
        if self.code not in PROMPT_CANDIDATE_ISSUE_CODES:
            raise ValueError("unsupported prompt candidate issue code")
        _require_exact_string(self.message, "message")
        if self.message != _ISSUE_MESSAGES[self.code]:
            raise ValueError("issue message does not match issue code")


@dataclass(frozen=True)
class PromptCandidateConstructionResult:
    contract_version: str
    status: str
    prompt_candidate: PromptCandidate | None
    issue: PromptCandidateIssue | None

    def __post_init__(self) -> None:
        _require_exact_string(self.contract_version, "contract_version")
        if self.status not in (
            PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED,
            PROMPT_CANDIDATE_CONSTRUCTION_STATUS_REJECTED,
        ):
            raise ValueError("unsupported prompt candidate construction status")
        if self.status == PROMPT_CANDIDATE_CONSTRUCTION_STATUS_CONSTRUCTED:
            if (
                type(self.prompt_candidate) is not PromptCandidate
                or self.issue is not None
            ):
                raise ValueError("constructed result invariant violated")
        elif self.prompt_candidate is not None or type(self.issue) is not PromptCandidateIssue:
            raise ValueError("rejected result invariant violated")


def _issue(code: str) -> PromptCandidateIssue:
    return PromptCandidateIssue(code=code, message=_ISSUE_MESSAGES[code])
