from datetime import datetime, timezone
import hashlib
import pytest
from rie.application.concrete_visual_generation_execution_adapter import ProviderExecutionResponse
from rie.application.generated_output_creative_result_candidate_bridge import bridge_generated_output_to_creative_result_candidate

def _response(*refs, execution_ref="exec-1"):
    return ProviderExecutionResponse(execution_status="SUCCEEDED",provider_output_refs=tuple(refs),provider_execution_ref=execution_ref)

def _candidate(**overrides):
    values=dict(creative_result_candidate_id="candidate-1",workflow_request_reference="workflow-1",project_context_reference="project-1",campaign_context_reference=("project-1","campaign-1"),creative_brief_reference="brief-1",instruction_reference=("instruction-1","APPROVED_INSTRUCTION"),originating_manual_handoff_reference=None,admission_timestamp=datetime(2026,9,30,tzinfo=timezone.utc),admitting_actor_reference="service-1",provider_id="cloudflare-workers-ai",model_id="@cf/black-forest-labs/flux-1-schnell",provider_execution_response=_response("output-1"),generated_output_bytes=b"generated-image")
    values.update(overrides); return bridge_generated_output_to_creative_result_candidate(**values)

def test_valid_output_constructs_candidate_with_exact_authority_and_provenance():
    c=_candidate(); h=hashlib.sha256(b"generated-image").hexdigest()
    assert c.candidate_content_checksum==h and c.authority_state=="CANDIDATE"
    assert not c.official_source_claimed and not c.accepted_asset_claimed and not c.approved_asset_claimed
    assert c.deterministic_provenance==("workflow_request:workflow-1","provider:cloudflare-workers-ai","model:@cf/black-forest-labs/flux-1-schnell","provider_execution:exec-1","provider_output:output-1",f"content_sha256:{h}")

def test_checksum_only_and_matching_checksum_are_accepted():
    h=hashlib.sha256(b"generated-image").hexdigest()
    assert _candidate(generated_output_checksum=h).candidate_content_checksum==h
    assert _candidate(generated_output_bytes=None,generated_output_checksum=h).candidate_content_checksum==h

@pytest.mark.parametrize("refs",[(),("a","b")])
def test_output_cardinality_fails_closed(refs):
    with pytest.raises(ValueError): _candidate(provider_execution_response=_response(*refs))

def test_mismatched_or_missing_checksum_fails_closed():
    with pytest.raises(ValueError): _candidate(generated_output_checksum="0"*64)
    with pytest.raises(ValueError): _candidate(generated_output_bytes=None,generated_output_checksum=None)

def test_transient_output_ref_is_replaced_by_digest_reference():
    c=_candidate(provider_execution_response=_response("data:image/png;base64,secret"))
    assert all("data:" not in x for x in c.deterministic_provenance)
    assert c.deterministic_provenance[-2].startswith("provider_output:sha256:")

def test_invalid_project_campaign_binding_fails_closed():
    with pytest.raises(ValueError): _candidate(campaign_context_reference=("other","campaign-1"))
