from datetime import datetime, timezone
import pytest
from rie.application.evaluate_generated_candidate import evaluate_generated_candidate
from rie.domain.creative_result_candidate import CANDIDATE_AUTHORITY_STATE, CreativeResultCandidate
from rie.domain.generated_candidate_evaluation import GeneratedCandidateCriterionResult
def candidate():
    return CreativeResultCandidate("candidate-1","workflow-1","project-1",("project-1","campaign-1"),"brief-1",("instruction-1","APPROVED_INSTRUCTION"),None,"c"*64,"IMAGE",datetime(2026,9,30,8,tzinfo=timezone.utc),"service-1",("workflow_request:workflow-1","content_sha256:"+"c"*64),CANDIDATE_AUTHORITY_STATE,False,False,False)
def criteria(): return (GeneratedCandidateCriterionResult("truth","passed","evidence:1"),GeneratedCandidateCriterionResult("quality","deferred","evidence:2"))
def test_evaluation_preserves_candidate_and_does_not_promote_authority():
    c=candidate(); r=evaluate_generated_candidate(candidate=c,criterion_results=criteria(),evaluator_actor_reference="evaluator-1",evaluation_timestamp=datetime(2026,9,30,9,tzinfo=timezone.utc))
    assert r.aggregate_outcome=="deferred" and r.candidate_content_checksum==c.candidate_content_checksum
    assert c.authority_state=="CANDIDATE" and not c.accepted_asset_claimed and not c.approved_asset_claimed
def test_identity_is_deterministic_and_ordered_criteria_are_identity_bearing():
    kw=dict(candidate=candidate(),evaluator_actor_reference="evaluator-1",evaluation_timestamp=datetime(2026,9,30,9,tzinfo=timezone.utc))
    a=evaluate_generated_candidate(criterion_results=criteria(),**kw); b=evaluate_generated_candidate(criterion_results=criteria(),**kw); d=evaluate_generated_candidate(criterion_results=tuple(reversed(criteria())),**kw)
    assert a.evaluation_id==b.evaluation_id and a.evaluation_id!=d.evaluation_id
def test_invalid_inputs_fail_closed():
    with pytest.raises(TypeError): evaluate_generated_candidate(candidate=object(),criterion_results=criteria(),evaluator_actor_reference="evaluator-1",evaluation_timestamp=datetime(2026,9,30,9,tzinfo=timezone.utc))
    with pytest.raises(ValueError): evaluate_generated_candidate(candidate=candidate(),criterion_results=criteria(),evaluator_actor_reference="",evaluation_timestamp=datetime(2026,9,30,9,tzinfo=timezone.utc))
    with pytest.raises(ValueError): evaluate_generated_candidate(candidate=candidate(),criterion_results=criteria(),evaluator_actor_reference="evaluator-1",evaluation_timestamp=datetime(2026,9,30,9))
