from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import rie.local_operator_runtime as runtime_module
from rie.local_operator_runtime import (
    LocalOperatorRuntimeAdapter,
    build_local_operator_runtime,
)


def create_project(runtime: LocalOperatorRuntimeAdapter) -> dict[str, object]:
    return dict(
        runtime.create_project(
            {
                "project_id": "project:alpha",
                "display_name": "Project Alpha",
                "campaign_reference": "campaign:one",
                "creative_brief_reference": "brief:approved:001",
            }
        )
    )


def add_evidence(runtime: LocalOperatorRuntimeAdapter) -> dict[str, object]:
    return dict(
        runtime.add_references(
            "project:alpha",
            {
                "gate15_reference": "",
                "gate16_reference": "",
                "evidence_reference": "evidence:001",
            },
        )
    )


def test_build_runtime_returns_protocol_adapter(tmp_path: Path) -> None:
    runtime = build_local_operator_runtime(state_directory=tmp_path / "state")
    assert isinstance(runtime, LocalOperatorRuntimeAdapter)
    for name in (
        "list_projects",
        "create_project",
        "get_project",
        "add_references",
        "submit_assessment",
        "reopen_project",
    ):
        assert callable(getattr(runtime, name))


def test_create_list_get_project_round_trip(tmp_path: Path) -> None:
    runtime = build_local_operator_runtime(state_directory=tmp_path / "state")
    created = create_project(runtime)
    assert created["project_id"] == "project:alpha"
    assert created["state"] == "REQUESTED"
    assert tuple(runtime.list_projects()) == (created,)
    assert runtime.get_project("project:alpha") == created
    assert runtime.get_project("missing") is None


def test_references_persist_across_runtime_rebuild(tmp_path: Path) -> None:
    state = tmp_path / "state"
    runtime = build_local_operator_runtime(state_directory=state)
    create_project(runtime)
    saved = add_evidence(runtime)
    assert saved["references"] == ("evidence:001",)

    rebuilt = build_local_operator_runtime(state_directory=state)
    reopened = rebuilt.get_project("project:alpha")
    assert reopened is not None
    assert reopened["references"] == ("evidence:001",)


def test_assessment_delegates_to_accepted_application_service(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    def fake_assess(**kwargs: object) -> object:
        calls.append(kwargs)
        evaluation = SimpleNamespace(
            disposition="ACCEPTED",
            prior_workflow_state="REQUESTED",
            requested_workflow_state="INPUTS_VALIDATED",
            resulting_workflow_state="INPUTS_VALIDATED",
            reason_codes=("ASSESSMENT_ACCEPTED",),
        )
        return SimpleNamespace(
            assessment_fingerprint="a" * 64,
            transition_evaluation=evaluation,
            creative_workflow_event=None,
            governed_creative_workflow_result=None,
        )

    monkeypatch.setattr(
        runtime_module,
        "assess_governed_creative_workflow",
        fake_assess,
    )
    runtime = build_local_operator_runtime(
        state_directory=tmp_path / "state"
    )
    create_project(runtime)
    add_evidence(runtime)

    project = runtime.submit_assessment(
        "project:alpha",
        {
            "requested_next_state": "INPUTS_VALIDATED",
            "reason_codes": "ASSESSMENT_ACCEPTED",
        },
    )

    assert len(calls) == 1
    call = calls[0]
    assert call["current_workflow_state"] == "REQUESTED"
    assert call["requested_next_workflow_state"] == "INPUTS_VALIDATED"
    assert call["reason_codes"] == ("ASSESSMENT_ACCEPTED",)
    assert call["evidence_references"] == (
        ("project:alpha", "campaign:one", "evidence:001"),
    )
    assert project["state"] == "INPUTS_VALIDATED"
    assert project["reasons"] == ("ASSESSMENT_ACCEPTED",)


def test_invalid_transition_preserves_accepted_reason_codes(
    tmp_path: Path,
) -> None:
    runtime = build_local_operator_runtime(
        state_directory=tmp_path / "state"
    )
    create_project(runtime)
    add_evidence(runtime)

    project = runtime.submit_assessment(
        "project:alpha",
        {
            "requested_next_state": "COMPLETED",
            "reason_codes": "ASSESSMENT_ACCEPTED",
        },
    )

    assert project["state"] == "REQUESTED"
    assert "INVALID_STATE_TRANSITION" in project["reasons"]
    assert "SAFE_STOP_REQUIRED" in project["reasons"]
    result = project["result"]
    assert isinstance(result, dict)
    assert result["resulting_workflow_state"] == "REQUESTED"


def test_reopen_persists_across_runtime_rebuild(tmp_path: Path) -> None:
    state = tmp_path / "state"
    runtime = build_local_operator_runtime(state_directory=state)
    create_project(runtime)
    reopened = runtime.reopen_project("project:alpha")
    assert reopened["reopened"] is True

    rebuilt = build_local_operator_runtime(state_directory=state)
    persisted = rebuilt.get_project("project:alpha")
    assert persisted is not None
    assert persisted["reopened"] is True


def test_storage_is_confined_to_configured_state_directory(
    tmp_path: Path,
) -> None:
    state = tmp_path / "selected-state"
    runtime = build_local_operator_runtime(state_directory=state)
    create_project(runtime)
    add_evidence(runtime)

    assert runtime.state_directory == state.resolve()
    assert tuple(path.name for path in state.glob("*.json"))
    assert not tuple(state.glob("*.tmp"))
    assert {path.name for path in tmp_path.iterdir()} == {"selected-state"}


def test_source_contains_no_domain_decision_network_or_external_process() -> None:
    source_path = Path("src/rie/local_operator_runtime.py")
    source = source_path.read_text(encoding="ascii")
    forbidden = (
        "import requests",
        "import socket",
        "import subprocess",
        "urllib.request",
        "http.client",
        "authority_bypass_requested=True",
        "prohibited_automation_requested=True",
        "approval_execution_requested=True",
        "asset_admission_execution_requested=True",
        "lifecycle_mutation_requested=True",
        "production_release_requested=True",
        "ALLOWED_WORKFLOW_STATES",
        "_ALLOWED_DIRECT_TRANSITIONS",
        "INVALID_STATE_TRANSITION =",
    )
    for marker in forbidden:
        assert marker not in source
    assert "assess_governed_creative_workflow(" in source
    assert "os.replace(" in source
