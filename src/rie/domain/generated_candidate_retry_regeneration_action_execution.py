from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re


_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_AUDIT_MARKERS = (
    "api_key",
    "authorization:",
    "bearer ",
    "credential",
    "password",
    "private_key",
    "secret",
    "session_token",
)


def _require_ascii_nonempty(value: object, name: str) -> str:
    if type(value) is not str:
        raise ValueError(f"{name} must be an exact str")
    if not value or value != value.strip():
        raise ValueError(f"{name} must be nonempty with no surrounding whitespace")
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{name} must be ASCII") from exc
    return value


def _require_sha256(value: object, name: str) -> str:
    text = _require_ascii_nonempty(value, name)
    if _SHA256_PATTERN.fullmatch(text) is None:
        raise ValueError(f"{name} must be a lowercase 64-hex SHA256")
    return text


def _require_aware_datetime(value: object, name: str) -> datetime:
    if type(value) is not datetime:
        raise ValueError(f"{name} must be an exact datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _require_reference_tuple(value: object, name: str) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise ValueError(f"{name} must be an exact tuple")
    checked: list[str] = []
    for index, item in enumerate(value):
        checked.append(_require_ascii_nonempty(item, f"{name}[{index}]"))
    if len(set(checked)) != len(checked):
        raise ValueError(f"{name} must not contain duplicates")
    return tuple(checked)


def _canonical_sha256(payload: dict[str, object]) -> str:
    canonical = json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def derive_retry_generation_request_sha256(
    *,
    grounded_prompt: str,
    selected_reference_asset_ids: tuple[str, ...],
) -> str:
    if type(grounded_prompt) is not str or not grounded_prompt.strip():
        raise ValueError("grounded_prompt must be a nonempty exact str")
    references = _require_reference_tuple(
        selected_reference_asset_ids,
        "selected_reference_asset_ids",
    )
    return _canonical_sha256(
        {
            "grounded_prompt": grounded_prompt,
            "selected_reference_asset_ids": list(references),
        }
    )


def derive_provider_local_result_sha256(
    *,
    provider_output_refs: tuple[str, ...],
    provider_audit_message: str,
) -> str:
    outputs = _require_reference_tuple(provider_output_refs, "provider_output_refs")
    if not outputs:
        raise ValueError("provider_output_refs must not be empty")
    audit = _require_ascii_nonempty(provider_audit_message, "provider_audit_message")
    lowered = audit.lower()
    for marker in _FORBIDDEN_AUDIT_MARKERS:
        if marker in lowered:
            raise ValueError("provider_audit_message must not contain secret material")
    return _canonical_sha256(
        {
            "provider_output_refs": list(outputs),
            "provider_audit_message": audit,
        }
    )


def derive_generated_candidate_retry_regeneration_action_execution_id(
    *,
    authorization_id: str,
    decision_id: str,
    evaluation_id: str,
    candidate_id: str,
    candidate_checksum: str,
    retry_generation_request_sha256: str,
    selected_reference_asset_ids: tuple[str, ...],
    provider_id: str,
    model_id: str,
    provider_local_result_sha256: str,
    execution_actor_reference: str,
    execution_timestamp: datetime,
) -> str:
    _require_sha256(authorization_id, "authorization_id")
    _require_ascii_nonempty(decision_id, "decision_id")
    _require_ascii_nonempty(evaluation_id, "evaluation_id")
    _require_ascii_nonempty(candidate_id, "candidate_id")
    _require_sha256(candidate_checksum, "candidate_checksum")
    _require_sha256(
        retry_generation_request_sha256,
        "retry_generation_request_sha256",
    )
    references = _require_reference_tuple(
        selected_reference_asset_ids,
        "selected_reference_asset_ids",
    )
    _require_ascii_nonempty(provider_id, "provider_id")
    _require_ascii_nonempty(model_id, "model_id")
    _require_sha256(provider_local_result_sha256, "provider_local_result_sha256")
    _require_ascii_nonempty(execution_actor_reference, "execution_actor_reference")
    timestamp = _require_aware_datetime(execution_timestamp, "execution_timestamp")

    return _canonical_sha256(
        {
            "authorization_id": authorization_id,
            "decision_id": decision_id,
            "evaluation_id": evaluation_id,
            "candidate_id": candidate_id,
            "candidate_checksum": candidate_checksum,
            "retry_generation_request_sha256": retry_generation_request_sha256,
            "selected_reference_asset_ids": list(references),
            "provider_id": provider_id,
            "model_id": model_id,
            "provider_local_result_sha256": provider_local_result_sha256,
            "execution_actor_reference": execution_actor_reference,
            "execution_timestamp": timestamp.isoformat(),
        }
    )


@dataclass(frozen=True)
class GeneratedCandidateRetryRegenerationActionExecution:
    retry_regeneration_action_execution_id: str
    authorization_id: str
    decision_id: str
    evaluation_id: str
    candidate_id: str
    candidate_checksum: str
    workflow_request_reference: str
    project_context_reference: str
    campaign_context_reference: str
    creative_brief_reference: str
    instruction_reference: str
    decision_outcome: str
    requested_action: str
    authorization_outcome: str
    retry_generation_request_sha256: str
    selected_reference_asset_ids: tuple[str, ...]
    provider_id: str
    model_id: str
    provider_output_refs: tuple[str, ...]
    provider_audit_message: str
    execution_actor_reference: str
    execution_timestamp: datetime
    deterministic_provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_sha256(
            self.retry_regeneration_action_execution_id,
            "retry_regeneration_action_execution_id",
        )
        _require_sha256(self.authorization_id, "authorization_id")
        _require_ascii_nonempty(self.decision_id, "decision_id")
        _require_ascii_nonempty(self.evaluation_id, "evaluation_id")
        _require_ascii_nonempty(self.candidate_id, "candidate_id")
        _require_sha256(self.candidate_checksum, "candidate_checksum")
        _require_ascii_nonempty(
            self.workflow_request_reference,
            "workflow_request_reference",
        )
        _require_ascii_nonempty(
            self.project_context_reference,
            "project_context_reference",
        )
        _require_ascii_nonempty(
            self.campaign_context_reference,
            "campaign_context_reference",
        )
        _require_ascii_nonempty(
            self.creative_brief_reference,
            "creative_brief_reference",
        )
        _require_ascii_nonempty(self.instruction_reference, "instruction_reference")
        _require_ascii_nonempty(self.decision_outcome, "decision_outcome")
        if self.requested_action != "RETRY_REGENERATION":
            raise ValueError("requested_action must be RETRY_REGENERATION")
        if self.authorization_outcome != "AUTHORIZED":
            raise ValueError("authorization_outcome must be AUTHORIZED")

        _require_sha256(
            self.retry_generation_request_sha256,
            "retry_generation_request_sha256",
        )
        _require_reference_tuple(
            self.selected_reference_asset_ids,
            "selected_reference_asset_ids",
        )
        _require_ascii_nonempty(self.provider_id, "provider_id")
        _require_ascii_nonempty(self.model_id, "model_id")

        result_sha = derive_provider_local_result_sha256(
            provider_output_refs=self.provider_output_refs,
            provider_audit_message=self.provider_audit_message,
        )

        _require_ascii_nonempty(
            self.execution_actor_reference,
            "execution_actor_reference",
        )
        _require_aware_datetime(self.execution_timestamp, "execution_timestamp")

        expected_id = (
            derive_generated_candidate_retry_regeneration_action_execution_id(
                authorization_id=self.authorization_id,
                decision_id=self.decision_id,
                evaluation_id=self.evaluation_id,
                candidate_id=self.candidate_id,
                candidate_checksum=self.candidate_checksum,
                retry_generation_request_sha256=(
                    self.retry_generation_request_sha256
                ),
                selected_reference_asset_ids=self.selected_reference_asset_ids,
                provider_id=self.provider_id,
                model_id=self.model_id,
                provider_local_result_sha256=result_sha,
                execution_actor_reference=self.execution_actor_reference,
                execution_timestamp=self.execution_timestamp,
            )
        )
        if self.retry_regeneration_action_execution_id != expected_id:
            raise ValueError("retry-regeneration action execution identity mismatch")

        expected_provenance = (
            f"authorization_sha256:{self.authorization_id}",
            f"decision_id:{self.decision_id}",
            f"candidate_sha256:{self.candidate_checksum}",
            "requested_action:RETRY_REGENERATION",
            f"retry_generation_request_sha256:{self.retry_generation_request_sha256}",
            f"provider:{self.provider_id}",
            f"model:{self.model_id}",
            f"provider_local_result_sha256:{result_sha}",
            (
                "retry_regeneration_action_execution_sha256:"
                f"{self.retry_regeneration_action_execution_id}"
            ),
        )
        if self.deterministic_provenance != expected_provenance:
            raise ValueError("deterministic_provenance mismatch")


__all__ = [
    "GeneratedCandidateRetryRegenerationActionExecution",
    "derive_generated_candidate_retry_regeneration_action_execution_id",
    "derive_provider_local_result_sha256",
    "derive_retry_generation_request_sha256",
]
