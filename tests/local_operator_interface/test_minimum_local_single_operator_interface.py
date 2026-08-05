from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode

import rie.local_operator_interface as interface


class FakeRuntime:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []
        self.projects: dict[str, dict[str, object]] = {
            "project-1": {
                "project_id": "project-1",
                "display_name": "Project One",
                "state": "REQUESTED",
                "references": [],
                "candidates": [],
                "events": [],
                "reasons": [],
                "result": None,
            }
        }

    def list_projects(self):
        self.calls.append(("list_projects", None))
        return tuple(self.projects[key] for key in sorted(self.projects))

    def create_project(self, values):
        self.calls.append(("create_project", dict(values)))
        project_id = values["project_id"]
        project = {
            "project_id": project_id,
            "display_name": values["display_name"],
            "state": "REQUESTED",
            "references": [],
            "candidates": [],
            "events": [],
            "reasons": [],
            "result": None,
        }
        self.projects[project_id] = project
        return project

    def get_project(self, project_id):
        self.calls.append(("get_project", project_id))
        return self.projects.get(project_id)

    def add_references(self, project_id, values):
        self.calls.append(("add_references", project_id, dict(values)))
        project = self.projects[project_id]
        project["references"] = tuple(
            value for value in values.values() if value
        )
        return project

    def submit_assessment(self, project_id, values):
        self.calls.append(("submit_assessment", project_id, dict(values)))
        project = self.projects[project_id]
        project["state"] = values["requested_next_state"]
        project["reasons"] = tuple(
            item.strip()
            for item in values["reason_codes"].split(",")
            if item.strip()
        )
        project["result"] = {"accepted": True}
        return project

    def reopen_project(self, project_id):
        self.calls.append(("reopen_project", project_id))
        project = self.projects[project_id]
        project["reopened"] = True
        return project


class FailingAssessmentRuntime(FakeRuntime):
    def submit_assessment(self, project_id, values):
        raise interface.LocalOperatorRuntimeError(("INVALID_TRANSITION",))


def invoke(application, method="GET", path="/", form=None):
    payload = urlencode(form or {}).encode("utf-8")
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(payload)),
        "wsgi.input": BytesIO(payload),
    }
    body = b"".join(application(environ, start_response)).decode("utf-8")
    return captured["status"], captured["headers"], body


def test_local_bind_only(monkeypatch):
    captured: dict[str, object] = {}

    class Server:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

        def serve_forever(self):
            captured["served"] = True

    def fake_make_server(host, port, application):
        captured["host"] = host
        captured["port"] = port
        captured["application"] = application
        return Server()

    monkeypatch.setattr(interface, "_load_runtime", FakeRuntime)
    monkeypatch.setattr(interface, "make_server", fake_make_server)

    assert interface.main(["--port", "8877"]) == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8877
    assert captured["served"] is True


def test_get_root_returns_minimum_form():
    runtime = FakeRuntime()
    status, headers, body = invoke(interface.create_application(runtime))

    assert status == "200 OK"
    assert headers["Cache-Control"] == "no-store"
    assert '<form method="post" action="/projects">' in body
    assert "Project One" in body


def test_create_project_through_interface():
    runtime = FakeRuntime()
    status, headers, _ = invoke(
        interface.create_application(runtime),
        method="POST",
        path="/projects",
        form={
            "project_id": "project-2",
            "display_name": "Project Two",
            "campaign_reference": "campaign-2",
            "creative_brief_reference": "brief-2",
        },
    )

    assert status == "303 See Other"
    assert headers["Location"] == "/projects/project-2"
    assert runtime.calls[-1][0] == "create_project"
    assert "project-2" in runtime.projects


def test_save_and_reopen_project():
    runtime = FakeRuntime()
    application = interface.create_application(runtime)

    status, _, _ = invoke(
        application,
        method="POST",
        path="/projects/project-1/reopen",
    )
    assert status == "303 See Other"
    assert runtime.projects["project-1"]["reopened"] is True

    status, _, body = invoke(
        application,
        method="GET",
        path="/projects/project-1",
    )
    assert status == "200 OK"
    assert "REQUESTED" in body


def test_reference_entry_reaches_accepted_service():
    runtime = FakeRuntime()
    status, _, _ = invoke(
        interface.create_application(runtime),
        method="POST",
        path="/projects/project-1/references",
        form={
            "gate15_reference": "asset-ref",
            "gate16_reference": "decision-ref",
            "evidence_reference": "evidence-ref",
        },
    )

    assert status == "303 See Other"
    assert runtime.calls[-1][0] == "add_references"
    assert runtime.projects["project-1"]["references"] == (
        "asset-ref",
        "decision-ref",
        "evidence-ref",
    )


def test_assessment_displays_state_reasons_and_result():
    runtime = FakeRuntime()
    application = interface.create_application(runtime)

    status, _, _ = invoke(
        application,
        method="POST",
        path="/projects/project-1/assessment",
        form={
            "requested_next_state": "INPUTS_VALIDATED",
            "reason_codes": "INPUTS_PRESENT,REFERENCES_VALID",
        },
    )
    assert status == "303 See Other"

    status, _, body = invoke(
        application,
        method="GET",
        path="/projects/project-1",
    )
    assert status == "200 OK"
    assert "INPUTS_VALIDATED" in body
    assert "INPUTS_PRESENT" in body
    assert "REFERENCES_VALID" in body
    assert "&quot;accepted&quot;: true" in body


def test_invalid_transition_fails_closed():
    runtime = FailingAssessmentRuntime()
    status, _, body = invoke(
        interface.create_application(runtime),
        method="POST",
        path="/projects/project-1/assessment",
        form={
            "requested_next_state": "COMPLETED",
            "reason_codes": "INVALID_TRANSITION",
        },
    )

    assert status == "409 Conflict"
    assert "Operation failed closed." in body
    assert "INVALID_TRANSITION" in body


def test_ui_contains_no_direct_domain_decision_or_sql():
    source = Path(interface.__file__).read_text(encoding="ascii")
    forbidden = (
        "import sqlite3",
        "CREATE TABLE",
        "INSERT INTO",
        "SELECT * FROM",
        "evaluate_governed_creative_workflow_transition",
        "assess_operator_approval_execution",
        "build_safe_operator_dashboard",
    )

    assert all(marker not in source for marker in forbidden)
    assert "127.0.0.1" in source
    assert "0.0.0.0" not in source
