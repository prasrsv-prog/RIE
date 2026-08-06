from __future__ import annotations

from io import BytesIO
from pathlib import Path
import tomllib
from urllib.parse import urlencode

import pytest

import rie.local_operator_interface as interface
from rie.local_operator_runtime import build_local_operator_runtime


PROJECT_ID = "project:alpha"
PROJECT_PATH = "/projects/project%3Aalpha"


def _call_application(
    application: object,
    method: str,
    path: str,
    values: dict[str, str] | None = None,
) -> tuple[str, dict[str, str], str]:
    payload = urlencode(values or {}).encode("ascii")
    captured: dict[str, object] = {}

    def start_response(
        status: str,
        headers: list[tuple[str, str]],
    ) -> None:
        captured["status"] = status
        captured["headers"] = headers

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "CONTENT_LENGTH": str(len(payload)),
        "CONTENT_TYPE": "application/x-www-form-urlencoded",
        "wsgi.input": BytesIO(payload),
    }
    chunks = application(environ, start_response)
    body = b"".join(chunks).decode("utf-8")
    headers = {
        str(key): str(value)
        for key, value in captured.get("headers", [])
    }
    return str(captured["status"]), headers, body


def _build_application(state_directory: Path):
    runtime = build_local_operator_runtime(
        state_directory=state_directory
    )
    return runtime, interface.create_application(runtime)


def _create_project(application: object) -> None:
    status, headers, _ = _call_application(
        application,
        "POST",
        "/projects",
        {
            "project_id": PROJECT_ID,
            "display_name": "Project Alpha",
            "campaign_reference": "campaign:one",
            "creative_brief_reference": "brief:approved:001",
        },
    )
    assert status == "303 See Other"
    assert headers["Location"] == PROJECT_PATH


def _add_reference(application: object) -> None:
    status, headers, _ = _call_application(
        application,
        "POST",
        PROJECT_PATH + "/references",
        {
            "gate15_reference": "",
            "gate16_reference": "",
            "evidence_reference": "evidence:001",
        },
    )
    assert status == "303 See Other"
    assert headers["Location"] == PROJECT_PATH


def test_console_entrypoint_resolves_to_local_operator_main() -> None:
    pyproject = tomllib.loads(
        Path("pyproject.toml").read_text(encoding="ascii")
    )
    assert pyproject["project"]["scripts"]["rcis-local"] == (
        "rie.local_operator_interface:main"
    )
    assert callable(interface.main)


def test_real_interface_runtime_create_project_round_trip(
    tmp_path: Path,
) -> None:
    state = tmp_path / "state"
    runtime, application = _build_application(state)
    _create_project(application)

    status, _, body = _call_application(
        application,
        "GET",
        PROJECT_PATH,
    )
    assert status == "200 OK"
    assert PROJECT_ID in body
    assert "REQUESTED" in body

    project = runtime.get_project(PROJECT_ID)
    assert project is not None
    assert project["display_name"] == "Project Alpha"
    assert tuple(runtime.list_projects()) == (project,)


def test_real_interface_runtime_references_persist_across_rebuild(
    tmp_path: Path,
) -> None:
    state = tmp_path / "state"
    _, application = _build_application(state)
    _create_project(application)
    _add_reference(application)

    rebuilt = build_local_operator_runtime(state_directory=state)
    project = rebuilt.get_project(PROJECT_ID)
    assert project is not None
    assert project["references"] == ("evidence:001",)

    rebuilt_application = interface.create_application(rebuilt)
    status, _, body = _call_application(
        rebuilt_application,
        "GET",
        PROJECT_PATH,
    )
    assert status == "200 OK"
    assert "evidence:001" in body


def test_real_interface_runtime_assessment_returns_accepted_result(
    tmp_path: Path,
) -> None:
    state = tmp_path / "state"
    runtime, application = _build_application(state)
    _create_project(application)
    _add_reference(application)

    status, headers, _ = _call_application(
        application,
        "POST",
        PROJECT_PATH + "/assessment",
        {
            "requested_next_state": "INPUTS_VALIDATED",
            "reason_codes": "ASSESSMENT_ACCEPTED",
        },
    )
    assert status == "303 See Other"
    assert headers["Location"] == PROJECT_PATH

    project = runtime.get_project(PROJECT_ID)
    assert project is not None
    assert project["state"] == "INPUTS_VALIDATED"
    assert project["reasons"] == ("ASSESSMENT_ACCEPTED",)
    assert isinstance(project["result"], dict)
    assert project["result"]["resulting_workflow_state"] == (
        "INPUTS_VALIDATED"
    )

    status, _, body = _call_application(
        application,
        "GET",
        PROJECT_PATH,
    )
    assert status == "200 OK"
    assert "INPUTS_VALIDATED" in body
    assert "ASSESSMENT_ACCEPTED" in body


def test_invalid_transition_fails_closed_end_to_end(
    tmp_path: Path,
) -> None:
    state = tmp_path / "state"
    runtime, application = _build_application(state)
    _create_project(application)
    _add_reference(application)

    status, headers, _ = _call_application(
        application,
        "POST",
        PROJECT_PATH + "/assessment",
        {
            "requested_next_state": "COMPLETED",
            "reason_codes": "ASSESSMENT_ACCEPTED",
        },
    )
    assert status == "303 See Other"
    assert headers["Location"] == PROJECT_PATH

    project = runtime.get_project(PROJECT_ID)
    assert project is not None
    assert project["state"] == "REQUESTED"
    assert "INVALID_STATE_TRANSITION" in project["reasons"]
    assert "SAFE_STOP_REQUIRED" in project["reasons"]
    assert isinstance(project["result"], dict)
    assert project["result"]["resulting_workflow_state"] == "REQUESTED"

    status, _, body = _call_application(
        application,
        "GET",
        PROJECT_PATH,
    )
    assert status == "200 OK"
    assert "INVALID_STATE_TRANSITION" in body
    assert "SAFE_STOP_REQUIRED" in body


def test_reopen_flow_persists_across_runtime_rebuild(
    tmp_path: Path,
) -> None:
    state = tmp_path / "state"
    _, application = _build_application(state)
    _create_project(application)

    status, headers, _ = _call_application(
        application,
        "POST",
        PROJECT_PATH + "/reopen",
    )
    assert status == "303 See Other"
    assert headers["Location"] == PROJECT_PATH

    rebuilt = build_local_operator_runtime(state_directory=state)
    project = rebuilt.get_project(PROJECT_ID)
    assert project is not None
    assert project["reopened"] is True


def test_end_to_end_state_is_confined_to_temporary_directory(
    tmp_path: Path,
) -> None:
    state = tmp_path / "selected-state"
    runtime, application = _build_application(state)
    _create_project(application)
    _add_reference(application)

    assert runtime.state_directory == state.resolve()
    json_paths = tuple(state.glob("*.json"))
    assert len(json_paths) == 1
    assert not tuple(state.glob("*.tmp"))
    assert {path.name for path in tmp_path.iterdir()} == {
        "selected-state"
    }


def test_rcis_local_main_binds_loopback_for_bounded_smoke_cycle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    local_app_data = tmp_path / "local-app-data"
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    captured: dict[str, object] = {}

    class BoundedServer:
        def __init__(
            self,
            host: str,
            port: int,
            application: object,
        ) -> None:
            captured["host"] = host
            captured["port"] = port
            captured["application"] = application

        def __enter__(self):
            return self

        def __exit__(
            self,
            exc_type: object,
            exc: object,
            traceback: object,
        ) -> bool:
            return False

        def serve_forever(self) -> None:
            captured["serve_forever_called"] = True
            status, _, body = _call_application(
                captured["application"],
                "GET",
                "/",
            )
            captured["status"] = status
            captured["body"] = body

    def bounded_make_server(
        host: str,
        port: int,
        application: object,
    ) -> BoundedServer:
        return BoundedServer(host, port, application)

    monkeypatch.setattr(interface, "make_server", bounded_make_server)

    assert interface.main(["--port", "18765"]) == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 18765
    assert captured["serve_forever_called"] is True
    assert captured["status"] == "200 OK"
    assert "RCIS Local Operator" in str(captured["body"])
    assert (
        local_app_data / "RCIS" / "local_operator"
    ).resolve().is_dir()
