"""Minimum persistent local-operator runtime adapter for RCIS.

The adapter owns only local operator snapshots. Governed workflow decisions are
delegated to the accepted application service.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from rie.application.governed_creative_workflow_application_service import (
    assess_governed_creative_workflow,
)
from rie.domain.governed_creative_workflow_request import (
    GovernedCreativeWorkflowRequest,
)
from rie.local_operator_interface import LocalOperatorRuntimeError


_SCHEMA_VERSION = 1
_WORKFLOW_CONTRACT_REFERENCE = ("GATE_18_CREATIVE_WORKFLOW", "1.0")
_INSTRUCTION_AUTHORITY = "APPROVED_INSTRUCTION"
_DEFAULT_STATE_PARTS = ("RCIS", "local_operator")


def _required_text(field_name: str, value: object) -> str:
    if not isinstance(value, str):
        raise LocalOperatorRuntimeError((f"{field_name.upper()}_INVALID",))
    normalized = value.strip()
    if not normalized or not normalized.isascii():
        raise LocalOperatorRuntimeError((f"{field_name.upper()}_INVALID",))
    if any(ord(character) < 32 or ord(character) == 127 for character in normalized):
        raise LocalOperatorRuntimeError((f"{field_name.upper()}_INVALID",))
    return normalized


def _optional_text(field_name: str, value: object) -> str | None:
    if value is None or value == "":
        return None
    return _required_text(field_name, value)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _default_state_directory() -> Path:
    root = os.environ.get("LOCALAPPDATA")
    if not root:
        raise LocalOperatorRuntimeError(("LOCALAPPDATA_UNAVAILABLE",))
    return Path(root).joinpath(*_DEFAULT_STATE_PARTS)


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _json_value(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {
            str(key): _json_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if hasattr(value, "__dict__") and not isinstance(value, type):
        return {
            str(key): _json_value(item)
            for key, item in sorted(vars(value).items())
            if not str(key).startswith("_")
        }
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    raise TypeError(f"unsupported snapshot value: {type(value).__name__}")


def _parse_timestamp(value: object) -> datetime:
    text = _required_text("request_timestamp", value)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise LocalOperatorRuntimeError(("REQUEST_TIMESTAMP_INVALID",)) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LocalOperatorRuntimeError(("REQUEST_TIMESTAMP_INVALID",))
    return parsed


def _reason_codes(value: object) -> tuple[str, ...]:
    if not isinstance(value, str):
        raise LocalOperatorRuntimeError(("REASON_CODES_INVALID",))
    normalized = tuple(
        sorted(
            {
                item.strip()
                for item in value.split(",")
                if item.strip()
            }
        )
    )
    if not normalized:
        raise LocalOperatorRuntimeError(("REASON_CODES_INVALID",))
    return normalized


class LocalOperatorRuntimeAdapter:
    """Persist local project snapshots and delegate governed assessment."""

    def __init__(self, state_directory: str | os.PathLike[str]) -> None:
        self._state_directory = Path(state_directory).expanduser().resolve()
        self._state_directory.mkdir(parents=True, exist_ok=True)

    @property
    def state_directory(self) -> Path:
        return self._state_directory

    def _snapshot_path(self, project_id: str) -> Path:
        digest = hashlib.sha256(project_id.encode("ascii")).hexdigest()
        path = (self._state_directory / f"{digest}.json").resolve()
        if path.parent != self._state_directory:
            raise LocalOperatorRuntimeError(("STATE_DIRECTORY_ESCAPE",))
        return path

    def _read_snapshot(self, path: Path) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="ascii"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise LocalOperatorRuntimeError(("SNAPSHOT_READ_FAILED",)) from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != _SCHEMA_VERSION:
            raise LocalOperatorRuntimeError(("SNAPSHOT_SCHEMA_INVALID",))
        return payload

    def _load_project(self, project_id: str) -> dict[str, Any] | None:
        normalized_id = _required_text("project_id", project_id)
        path = self._snapshot_path(normalized_id)
        if not path.exists():
            return None
        project = self._read_snapshot(path)
        if project.get("project_id") != normalized_id:
            raise LocalOperatorRuntimeError(("SNAPSHOT_PROJECT_ID_MISMATCH",))
        return project

    def _require_project(self, project_id: str) -> dict[str, Any]:
        project = self._load_project(project_id)
        if project is None:
            raise LocalOperatorRuntimeError(("PROJECT_NOT_FOUND",))
        return project

    def _write_project(self, project: Mapping[str, object]) -> None:
        project_id = _required_text("project_id", project.get("project_id"))
        path = self._snapshot_path(project_id)
        payload = json.dumps(
            _json_value(project),
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii") + b"\n"
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=self._state_directory,
                prefix=".rcis-",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_path = Path(handle.name)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, path)
        except OSError as exc:
            raise LocalOperatorRuntimeError(("SNAPSHOT_WRITE_FAILED",)) from exc
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()

    @staticmethod
    def _public_project(project: Mapping[str, object]) -> dict[str, object]:
        return {
            "project_id": project["project_id"],
            "display_name": project["display_name"],
            "state": project["state"],
            "references": tuple(project.get("references", ())),
            "candidates": tuple(project.get("candidates", ())),
            "events": tuple(project.get("events", ())),
            "reasons": tuple(project.get("reasons", ())),
            "result": project.get("result"),
            "reopened": bool(project.get("reopened", False)),
        }

    def list_projects(self) -> Sequence[Mapping[str, object]]:
        projects = [
            self._read_snapshot(path)
            for path in sorted(self._state_directory.glob("*.json"))
        ]
        return tuple(
            self._public_project(project)
            for project in sorted(
                projects,
                key=lambda item: str(item.get("project_id", "")),
            )
        )

    def create_project(
        self,
        values: Mapping[str, str],
    ) -> Mapping[str, object]:
        project_id = _required_text("project_id", values.get("project_id"))
        if self._load_project(project_id) is not None:
            raise LocalOperatorRuntimeError(("PROJECT_ALREADY_EXISTS",))
        display_name = _required_text("display_name", values.get("display_name"))
        campaign_reference = _required_text(
            "campaign_reference",
            values.get("campaign_reference"),
        )
        creative_brief_reference = _required_text(
            "creative_brief_reference",
            values.get("creative_brief_reference"),
        )
        request_timestamp = _utc_now()
        project: dict[str, object] = {
            "schema_version": _SCHEMA_VERSION,
            "project_id": project_id,
            "display_name": display_name,
            "campaign_reference": campaign_reference,
            "creative_brief_reference": creative_brief_reference,
            "workflow_request_id": f"{project_id}:workflow-request",
            "idempotency_key": (
                f"{project_id}:{campaign_reference}:local-operator-request"
            ),
            "instruction_reference": [
                f"{project_id}:local-instruction",
                _INSTRUCTION_AUTHORITY,
            ],
            "requesting_actor_reference": f"{project_id}:local-operator",
            "request_timestamp": request_timestamp.isoformat(),
            "workflow_contract_reference": list(_WORKFLOW_CONTRACT_REFERENCE),
            "state": "REQUESTED",
            "gate15_reference": None,
            "gate16_reference": None,
            "evidence_references": [],
            "references": [],
            "candidates": [],
            "events": [],
            "reasons": [],
            "result": None,
            "assessments": [],
            "reopened": False,
        }
        self._write_project(project)
        return self._public_project(project)

    def get_project(self, project_id: str) -> Mapping[str, object] | None:
        project = self._load_project(project_id)
        if project is None:
            return None
        return self._public_project(project)

    def add_references(
        self,
        project_id: str,
        values: Mapping[str, str],
    ) -> Mapping[str, object]:
        project = self._require_project(project_id)
        gate15 = _optional_text("gate15_reference", values.get("gate15_reference"))
        gate16 = _optional_text("gate16_reference", values.get("gate16_reference"))
        evidence = _optional_text(
            "evidence_reference",
            values.get("evidence_reference"),
        )
        if gate15 is not None:
            project["gate15_reference"] = gate15
        if gate16 is not None:
            project["gate16_reference"] = gate16
        evidence_references = set(project.get("evidence_references", ()))
        if evidence is not None:
            evidence_references.add(evidence)
        project["evidence_references"] = sorted(evidence_references)
        project["references"] = sorted(
            {
                item
                for item in (
                    project.get("gate15_reference"),
                    project.get("gate16_reference"),
                    *project["evidence_references"],
                )
                if isinstance(item, str) and item
            }
        )
        self._write_project(project)
        return self._public_project(project)

    def _workflow_request(
        self,
        project: Mapping[str, object],
    ) -> GovernedCreativeWorkflowRequest:
        project_id = _required_text("project_id", project.get("project_id"))
        campaign_reference = _required_text(
            "campaign_reference",
            project.get("campaign_reference"),
        )
        instruction = project.get("instruction_reference")
        contract = project.get("workflow_contract_reference")
        if not isinstance(instruction, list) or len(instruction) != 2:
            raise LocalOperatorRuntimeError(("INSTRUCTION_REFERENCE_INVALID",))
        if not isinstance(contract, list) or len(contract) != 2:
            raise LocalOperatorRuntimeError(("WORKFLOW_CONTRACT_INVALID",))
        return GovernedCreativeWorkflowRequest(
            workflow_request_id=_required_text(
                "workflow_request_id",
                project.get("workflow_request_id"),
            ),
            idempotency_key=_required_text(
                "idempotency_key",
                project.get("idempotency_key"),
            ),
            project_context_reference=project_id,
            campaign_context_reference=(project_id, campaign_reference),
            creative_brief_reference=_required_text(
                "creative_brief_reference",
                project.get("creative_brief_reference"),
            ),
            approved_knowledge_references=(),
            governed_asset_references=(),
            instruction_reference=(
                _required_text("instruction_reference", instruction[0]),
                _required_text("instruction_authority", instruction[1]),
            ),
            requesting_actor_reference=_required_text(
                "requesting_actor_reference",
                project.get("requesting_actor_reference"),
            ),
            request_timestamp=_parse_timestamp(project.get("request_timestamp")),
            workflow_contract_reference=(
                _required_text("workflow_contract_name", contract[0]),
                _required_text("workflow_contract_version", contract[1]),
            ),
            requested_output_purpose_code="LOCAL_OPERATOR_WORKFLOW",
            requested_review_policy_reference="LOCAL_SINGLE_OPERATOR_REVIEW",
            manual_external_tool_handoff_declared=False,
        )

    def submit_assessment(
        self,
        project_id: str,
        values: Mapping[str, str],
    ) -> Mapping[str, object]:
        project = self._require_project(project_id)
        evidence_values = tuple(
            sorted(
                {
                    _required_text("evidence_reference", item)
                    for item in project.get("evidence_references", ())
                }
            )
        )
        if not evidence_values:
            raise LocalOperatorRuntimeError(("EVIDENCE_REFERENCE_REQUIRED",))

        request = self._workflow_request(project)
        campaign_reference = _required_text(
            "campaign_reference",
            project.get("campaign_reference"),
        )
        requested_state = _required_text(
            "requested_next_state",
            values.get("requested_next_state"),
        )
        reason_codes = _reason_codes(values.get("reason_codes"))
        gate15 = project.get("gate15_reference")
        gate16 = project.get("gate16_reference")

        try:
            assessment = assess_governed_creative_workflow(
                workflow_request=request,
                current_workflow_state=_required_text(
                    "current_workflow_state",
                    project.get("state"),
                ),
                requested_next_workflow_state=requested_state,
                responsible_actor_or_service_reference=(
                    "ACTOR",
                    request.requesting_actor_reference,
                ),
                assessment_timestamp=_utc_now(),
                evidence_references=tuple(
                    (request.project_context_reference, campaign_reference, item)
                    for item in evidence_values
                ),
                reason_codes=reason_codes,
                workflow_contract_reference=request.workflow_contract_reference,
                accepted_gate_16_operator_decision_reference=(
                    None
                    if not isinstance(gate16, str) or not gate16
                    else (
                        request.project_context_reference,
                        campaign_reference,
                        gate16,
                    )
                ),
                accepted_gate_15_governed_asset_reference=(
                    None
                    if not isinstance(gate15, str) or not gate15
                    else (
                        request.project_context_reference,
                        campaign_reference,
                        gate15,
                    )
                ),
            )
        except (TypeError, ValueError) as exc:
            raise LocalOperatorRuntimeError(("ASSESSMENT_INPUT_INVALID",)) from exc

        evaluation = assessment.transition_evaluation
        project["state"] = str(evaluation.resulting_workflow_state)
        project["reasons"] = list(evaluation.reason_codes)
        if assessment.creative_workflow_event is not None:
            project.setdefault("events", []).append(
                _json_value(assessment.creative_workflow_event)
            )
        workflow_result = assessment.governed_creative_workflow_result
        project["result"] = (
            _json_value(workflow_result)
            if workflow_result is not None
            else {
                "assessment_fingerprint": assessment.assessment_fingerprint,
                "disposition": str(evaluation.disposition),
                "requested_workflow_state": str(
                    evaluation.requested_workflow_state
                ),
                "resulting_workflow_state": str(
                    evaluation.resulting_workflow_state
                ),
            }
        )
        project.setdefault("assessments", []).append(
            {
                "assessment_fingerprint": assessment.assessment_fingerprint,
                "disposition": str(evaluation.disposition),
                "reason_codes": list(evaluation.reason_codes),
                "requested_workflow_state": str(
                    evaluation.requested_workflow_state
                ),
                "resulting_workflow_state": str(
                    evaluation.resulting_workflow_state
                ),
            }
        )
        project["reopened"] = False
        self._write_project(project)
        return self._public_project(project)

    def reopen_project(self, project_id: str) -> Mapping[str, object]:
        project = self._require_project(project_id)
        project["reopened"] = True
        project["last_reopened_at"] = _utc_now().isoformat()
        self._write_project(project)
        return self._public_project(project)


def build_local_operator_runtime(
    *,
    state_directory: str | os.PathLike[str] | None = None,
) -> LocalOperatorRuntimeAdapter:
    """Build the minimum local runtime using an explicit or local state path."""

    selected_directory = (
        _default_state_directory()
        if state_directory is None
        else Path(state_directory)
    )
    return LocalOperatorRuntimeAdapter(selected_directory)
