"""Minimum generated-output to CreativeResultCandidate provenance bridge."""
from __future__ import annotations
from datetime import datetime
import hashlib
from rie.application.concrete_visual_generation_execution_adapter import ProviderExecutionResponse
from rie.domain.creative_result_candidate import CANDIDATE_AUTHORITY_STATE, CreativeResultCandidate

def _required_ascii(value: object, name: str) -> str:
    if not isinstance(value, str): raise TypeError(f"{name} must be text")
    if not value or not value.strip(): raise ValueError(f"{name} must not be empty")
    if not value.isascii(): raise ValueError(f"{name} must contain ASCII text only")
    return value

def _checksum(data: bytes | None, supplied: str | None) -> str:
    if data is None and supplied is None: raise ValueError("generated output bytes or checksum is required")
    if data is not None and not isinstance(data, bytes): raise TypeError("generated_output_bytes must be bytes")
    derived = hashlib.sha256(data).hexdigest() if data is not None else None
    if supplied is not None:
        if not isinstance(supplied, str) or len(supplied) != 64 or any(c not in "0123456789abcdef" for c in supplied):
            raise ValueError("generated_output_checksum must be a lowercase SHA256 value")
        if derived is not None and supplied != derived: raise ValueError("generated output checksum does not match bytes")
        return supplied
    assert derived is not None
    return derived

def bridge_generated_output_to_creative_result_candidate(*, creative_result_candidate_id: str, workflow_request_reference: str, project_context_reference: str, campaign_context_reference: tuple[str, str], creative_brief_reference: str, instruction_reference: tuple[str, str], originating_manual_handoff_reference: str | None, admission_timestamp: datetime, admitting_actor_reference: str, provider_id: str, model_id: str, provider_execution_response: ProviderExecutionResponse, generated_output_bytes: bytes | None = None, generated_output_checksum: str | None = None) -> CreativeResultCandidate:
    if not isinstance(provider_execution_response, ProviderExecutionResponse): raise TypeError("provider_execution_response must be ProviderExecutionResponse")
    if len(provider_execution_response.provider_output_refs) != 1: raise ValueError("provider execution must contain exactly one output")
    provider=_required_ascii(provider_id,"provider_id"); model=_required_ascii(model_id,"model_id"); workflow=_required_ascii(workflow_request_reference,"workflow_request_reference")
    checksum=_checksum(generated_output_bytes,generated_output_checksum)
    output_ref=provider_execution_response.provider_output_refs[0]
    immutable_ref=output_ref if output_ref.isascii() and not output_ref.lower().startswith(("http://","https://","data:")) else f"sha256:{checksum}"
    provenance=[f"workflow_request:{workflow}",f"provider:{provider}",f"model:{model}"]
    if provider_execution_response.provider_execution_ref:
        provenance.append(f"provider_execution:{_required_ascii(provider_execution_response.provider_execution_ref,'provider_execution_ref')}")
    provenance.extend((f"provider_output:{immutable_ref}",f"content_sha256:{checksum}"))
    return CreativeResultCandidate(creative_result_candidate_id=creative_result_candidate_id,workflow_request_reference=workflow_request_reference,project_context_reference=project_context_reference,campaign_context_reference=campaign_context_reference,creative_brief_reference=creative_brief_reference,instruction_reference=instruction_reference,originating_manual_handoff_reference=originating_manual_handoff_reference,candidate_content_checksum=checksum,artifact_type="IMAGE",admission_timestamp=admission_timestamp,admitting_actor_reference=admitting_actor_reference,deterministic_provenance=tuple(provenance),authority_state=CANDIDATE_AUTHORITY_STATE,official_source_claimed=False,accepted_asset_claimed=False,approved_asset_claimed=False)

__all__=["bridge_generated_output_to_creative_result_candidate"]
