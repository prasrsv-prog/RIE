from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Final, Literal, TypeAlias

PASSED: Final = "passed"
FAILED: Final = "failed"
DEFERRED: Final = "deferred"
EvaluationOutcome: TypeAlias = Literal["passed", "failed", "deferred"]
ALLOWED_OUTCOMES: Final = frozenset({PASSED, FAILED, DEFERRED})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

def _ascii(name: str, value: object) -> str:
    if not isinstance(value, str): raise TypeError(f"{name} must be text")
    if not value or not value.strip(): raise ValueError(f"{name} must not be empty")
    if not value.isascii(): raise ValueError(f"{name} must contain ASCII text only")
    if any(ord(c) < 32 or ord(c) == 127 for c in value): raise ValueError(f"{name} must not contain control characters")
    return value

@dataclass(frozen=True)
class GeneratedCandidateCriterionResult:
    criterion_id: str
    outcome: EvaluationOutcome
    reason_evidence_reference: str
    def __post_init__(self) -> None:
        _ascii("criterion_id", self.criterion_id)
        if self.outcome not in ALLOWED_OUTCOMES: raise ValueError("outcome must be exactly passed, failed, or deferred")
        _ascii("reason_evidence_reference", self.reason_evidence_reference)

def derive_aggregate_outcome(results: tuple[GeneratedCandidateCriterionResult, ...]) -> EvaluationOutcome:
    if not isinstance(results, tuple): raise TypeError("criterion_results must be a tuple")
    if not results: raise ValueError("criterion_results must not be empty")
    if any(not isinstance(x, GeneratedCandidateCriterionResult) for x in results): raise TypeError("criterion_results contain invalid record")
    ids=tuple(x.criterion_id for x in results)
    if len(set(ids)) != len(ids): raise ValueError("criterion_id values must be unique")
    if any(x.outcome == FAILED for x in results): return FAILED
    if any(x.outcome == DEFERRED for x in results): return DEFERRED
    return PASSED

@dataclass(frozen=True)
class GeneratedCandidateEvaluation:
    evaluation_id: str
    creative_result_candidate_id: str
    workflow_request_reference: str
    project_context_reference: str
    campaign_context_reference: tuple[str, str]
    creative_brief_reference: str
    instruction_reference: tuple[str, str]
    candidate_content_checksum: str
    artifact_type: str
    candidate_deterministic_provenance: tuple[str, ...]
    criterion_results: tuple[GeneratedCandidateCriterionResult, ...]
    aggregate_outcome: EvaluationOutcome
    evaluator_actor_reference: str
    evaluation_timestamp: datetime
    deterministic_provenance: tuple[str, ...]
    def __post_init__(self) -> None:
        if _SHA256.fullmatch(self.evaluation_id) is None: raise ValueError("evaluation_id must be lowercase SHA256")
        for n in ("creative_result_candidate_id","workflow_request_reference","project_context_reference","creative_brief_reference","artifact_type","evaluator_actor_reference"): _ascii(n,getattr(self,n))
        if not isinstance(self.campaign_context_reference,tuple) or len(self.campaign_context_reference)!=2: raise ValueError("campaign_context_reference must contain exactly two values")
        for i,x in enumerate(self.campaign_context_reference): _ascii(f"campaign_context_reference[{i}]",x)
        if self.campaign_context_reference[0] != self.project_context_reference: raise ValueError("campaign project binding mismatch")
        if not isinstance(self.instruction_reference,tuple) or len(self.instruction_reference)!=2: raise ValueError("instruction_reference must contain exactly two values")
        for i,x in enumerate(self.instruction_reference): _ascii(f"instruction_reference[{i}]",x)
        if _SHA256.fullmatch(self.candidate_content_checksum) is None: raise ValueError("candidate_content_checksum must be lowercase SHA256")
        if not isinstance(self.candidate_deterministic_provenance,tuple) or not self.candidate_deterministic_provenance: raise ValueError("candidate provenance must be non-empty tuple")
        for i,x in enumerate(self.candidate_deterministic_provenance): _ascii(f"candidate_deterministic_provenance[{i}]",x)
        if len(set(self.candidate_deterministic_provenance)) != len(self.candidate_deterministic_provenance): raise ValueError("candidate provenance must not contain duplicates")
        if self.aggregate_outcome != derive_aggregate_outcome(self.criterion_results): raise ValueError("aggregate_outcome mismatch")
        if not isinstance(self.evaluation_timestamp,datetime): raise TypeError("evaluation_timestamp must be datetime")
        if self.evaluation_timestamp.tzinfo is None or self.evaluation_timestamp.utcoffset() is None: raise ValueError("evaluation_timestamp must be timezone-aware")
        if not isinstance(self.deterministic_provenance,tuple) or not self.deterministic_provenance: raise ValueError("deterministic_provenance must be non-empty tuple")
        for i,x in enumerate(self.deterministic_provenance): _ascii(f"deterministic_provenance[{i}]",x)
        if len(set(self.deterministic_provenance)) != len(self.deterministic_provenance): raise ValueError("deterministic_provenance must not contain duplicates")
