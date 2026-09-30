from __future__ import annotations
from datetime import datetime
import hashlib, json
from rie.domain.creative_result_candidate import CANDIDATE_AUTHORITY_STATE, CreativeResultCandidate
from rie.domain.generated_candidate_evaluation import GeneratedCandidateCriterionResult, GeneratedCandidateEvaluation, derive_aggregate_outcome

def evaluate_generated_candidate(*, candidate: CreativeResultCandidate, criterion_results: tuple[GeneratedCandidateCriterionResult,...], evaluator_actor_reference: str, evaluation_timestamp: datetime) -> GeneratedCandidateEvaluation:
    if not isinstance(candidate, CreativeResultCandidate): raise TypeError("candidate must be CreativeResultCandidate")
    if candidate.authority_state != CANDIDATE_AUTHORITY_STATE or candidate.official_source_claimed or candidate.accepted_asset_claimed or candidate.approved_asset_claimed: raise ValueError("candidate authority invariants invalid")
    aggregate=derive_aggregate_outcome(criterion_results)
    if not isinstance(evaluator_actor_reference,str): raise TypeError("evaluator_actor_reference must be text")
    if not evaluator_actor_reference or not evaluator_actor_reference.strip() or not evaluator_actor_reference.isascii(): raise ValueError("evaluator_actor_reference must be non-empty ASCII")
    if not isinstance(evaluation_timestamp,datetime): raise TypeError("evaluation_timestamp must be datetime")
    if evaluation_timestamp.tzinfo is None or evaluation_timestamp.utcoffset() is None: raise ValueError("evaluation_timestamp must be timezone-aware")
    payload={"candidate_id":candidate.creative_result_candidate_id,"workflow":candidate.workflow_request_reference,"project":candidate.project_context_reference,"campaign":candidate.campaign_context_reference,"brief":candidate.creative_brief_reference,"instruction":candidate.instruction_reference,"checksum":candidate.candidate_content_checksum,"artifact_type":candidate.artifact_type,"candidate_provenance":candidate.deterministic_provenance,"criteria":[(x.criterion_id,x.outcome,x.reason_evidence_reference) for x in criterion_results],"evaluator":evaluator_actor_reference,"timestamp":evaluation_timestamp.isoformat()}
    eid=hashlib.sha256(json.dumps(payload,ensure_ascii=True,separators=(",",":"),sort_keys=True).encode("ascii")).hexdigest()
    provenance=(f"candidate:{candidate.creative_result_candidate_id}",f"content_sha256:{candidate.candidate_content_checksum}",f"evaluation_sha256:{eid}")
    return GeneratedCandidateEvaluation(eid,candidate.creative_result_candidate_id,candidate.workflow_request_reference,candidate.project_context_reference,candidate.campaign_context_reference,candidate.creative_brief_reference,candidate.instruction_reference,candidate.candidate_content_checksum,candidate.artifact_type,candidate.deterministic_provenance,criterion_results,aggregate,evaluator_actor_reference,evaluation_timestamp,provenance)
