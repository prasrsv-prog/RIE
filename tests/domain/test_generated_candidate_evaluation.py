from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import pytest
from rie.domain.generated_candidate_evaluation import GeneratedCandidateCriterionResult, GeneratedCandidateEvaluation, derive_aggregate_outcome
def c(i="c1",o="passed"): return GeneratedCandidateCriterionResult(i,o,"evidence-1")
def test_aggregate_precedence():
    assert derive_aggregate_outcome((c("a"),c("b","deferred")))=="deferred"
    assert derive_aggregate_outcome((c("a","deferred"),c("b","failed")))=="failed"
def test_empty_duplicate_and_uncontrolled_fail_closed():
    with pytest.raises(ValueError): derive_aggregate_outcome(())
    with pytest.raises(ValueError): derive_aggregate_outcome((c("same"),c("same","deferred")))
    with pytest.raises(ValueError): c(o="accepted")
def test_record_is_immutable_and_rejects_wrong_aggregate():
    r=GeneratedCandidateEvaluation("a"*64,"candidate","workflow","project",("project","campaign"),"brief",("instruction","APPROVED_INSTRUCTION"),"b"*64,"IMAGE",("source:1",),(c(),),"passed","evaluator",datetime(2026,9,30,tzinfo=timezone.utc),("evaluation:a",))
    with pytest.raises(FrozenInstanceError): r.aggregate_outcome="failed"
    with pytest.raises(ValueError): GeneratedCandidateEvaluation("a"*64,"candidate","workflow","project",("project","campaign"),"brief",("instruction","APPROVED_INSTRUCTION"),"b"*64,"IMAGE",("source:1",),(c(),),"failed","evaluator",datetime(2026,9,30,tzinfo=timezone.utc),("evaluation:a",))
