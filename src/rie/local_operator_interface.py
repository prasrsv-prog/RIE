"""Minimum local single-operator web interface for RCIS.

This module contains presentation and HTTP routing only. It delegates project
storage and governed workflow decisions to a supplied local runtime.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from html import escape
import importlib
import json
from typing import Protocol
from urllib.parse import parse_qs, quote, unquote
from wsgiref.simple_server import make_server


LOCAL_BIND_ADDRESS = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_FORM_BYTES = 65536


class LocalOperatorRuntime(Protocol):
    """Minimum runtime surface required by the local operator interface."""

    def list_projects(self) -> Sequence[Mapping[str, object]]:
        """Return saved local projects in deterministic display order."""

    def create_project(
        self,
        values: Mapping[str, str],
    ) -> Mapping[str, object]:
        """Create and persist one minimum local project."""

    def get_project(self, project_id: str) -> Mapping[str, object] | None:
        """Return one saved local project or None."""

    def add_references(
        self,
        project_id: str,
        values: Mapping[str, str],
    ) -> Mapping[str, object]:
        """Supply accepted references through the runtime."""

    def submit_assessment(
        self,
        project_id: str,
        values: Mapping[str, str],
    ) -> Mapping[str, object]:
        """Submit operator input to accepted application services."""

    def reopen_project(self, project_id: str) -> Mapping[str, object]:
        """Reopen one saved local project through the runtime."""


class LocalOperatorRuntimeError(Exception):
    """Controlled fail-closed runtime error exposed as reason codes."""

    def __init__(self, reason_codes: Sequence[str]) -> None:
        normalized = tuple(str(item) for item in reason_codes)
        if not normalized:
            normalized = ("RUNTIME_OPERATION_FAILED",)
        self.reason_codes = normalized
        super().__init__("|".join(normalized))


def _html(value: object) -> str:
    return escape(str(value), quote=True)


def _response(
    start_response: object,
    status: str,
    body: str,
    headers: Sequence[tuple[str, str]] = (),
) -> list[bytes]:
    payload = body.encode("utf-8")
    response_headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(payload))),
        ("Cache-Control", "no-store"),
        ("X-Content-Type-Options", "nosniff"),
    ]
    response_headers.extend(headers)
    start_response(status, response_headers)
    return [payload]


def _redirect(start_response: object, location: str) -> list[bytes]:
    return _response(
        start_response,
        "303 See Other",
        "<!doctype html><title>Continue</title><p>Continue.</p>",
        (("Location", location),),
    )


def _page(title: str, content: str) -> str:
    return (
        "<!doctype html>"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{_html(title)}</title>"
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;"
        "padding:0 1rem;line-height:1.45}"
        "form,section{border:1px solid #bbb;padding:1rem;margin:1rem 0}"
        "label{display:block;margin:.6rem 0}"
        "input,textarea,select{width:100%;box-sizing:border-box;padding:.45rem}"
        "button{padding:.55rem .9rem}"
        "code,pre{white-space:pre-wrap;overflow-wrap:anywhere}"
        ".reason{font-weight:700}"
        "</style></head><body>"
        f"<h1>{_html(title)}</h1>{content}</body></html>"
    )


def _read_form(environ: Mapping[str, object]) -> dict[str, str]:
    raw_length = str(environ.get("CONTENT_LENGTH") or "0")
    try:
        length = int(raw_length)
    except ValueError as exc:
        raise LocalOperatorRuntimeError(("INVALID_CONTENT_LENGTH",)) from exc
    if length < 0 or length > MAX_FORM_BYTES:
        raise LocalOperatorRuntimeError(("FORM_SIZE_INVALID",))
    stream = environ.get("wsgi.input")
    if stream is None or not hasattr(stream, "read"):
        raise LocalOperatorRuntimeError(("REQUEST_BODY_UNAVAILABLE",))
    raw = stream.read(length)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise LocalOperatorRuntimeError(("FORM_ENCODING_INVALID",)) from exc
    parsed = parse_qs(text, keep_blank_values=True, strict_parsing=False)
    return {
        str(key): str(values[-1]) if values else ""
        for key, values in parsed.items()
    }


def _project_location(project_id: str) -> str:
    return "/projects/" + quote(project_id, safe="")


def _project_id(project: Mapping[str, object]) -> str:
    value = project.get("project_id")
    if not isinstance(value, str) or not value:
        raise LocalOperatorRuntimeError(("PROJECT_ID_MISSING",))
    return value


def _items(value: object) -> tuple[object, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes, bytearray)):
        return (value,)
    if isinstance(value, Sequence):
        return tuple(value)
    return (value,)


def _render_list(title: str, value: object) -> str:
    items = _items(value)
    if not items:
        return f"<h3>{_html(title)}</h3><p>&lt;none&gt;</p>"
    rendered = "".join(f"<li><code>{_html(item)}</code></li>" for item in items)
    return f"<h3>{_html(title)}</h3><ul>{rendered}</ul>"


def _render_root(projects: Sequence[Mapping[str, object]]) -> str:
    links: list[str] = []
    for project in projects:
        project_id = _project_id(project)
        name = project.get("display_name", project_id)
        state = project.get("state", "UNKNOWN")
        links.append(
            "<li>"
            f'<a href="{_html(_project_location(project_id))}">{_html(name)}</a> '
            f"<code>{_html(state)}</code>"
            "</li>"
        )
    project_list = "".join(links) or "<li>&lt;none&gt;</li>"
    return _page(
        "RCIS Local Operator",
        "<section><h2>Saved projects</h2>"
        f"<ul>{project_list}</ul></section>"
        '<form method="post" action="/projects">'
        "<h2>Create project</h2>"
        '<label>Project ID<input name="project_id" required></label>'
        '<label>Display name<input name="display_name" required></label>'
        '<label>Campaign reference<input name="campaign_reference" required></label>'
        '<label>Creative brief reference'
        '<input name="creative_brief_reference" required></label>'
        '<button type="submit">Create</button></form>',
    )


def _render_project(project: Mapping[str, object]) -> str:
    project_id = _project_id(project)
    state = project.get("state", "UNKNOWN")
    result = project.get("result")
    content = (
        f'<p><a href="/">Back</a></p>'
        f"<p>Project: <code>{_html(project_id)}</code></p>"
        f"<p>State: <code>{_html(state)}</code></p>"
        + _render_list("References", project.get("references"))
        + _render_list("Candidates", project.get("candidates"))
        + _render_list("Events", project.get("events"))
        + _render_list("Reasons", project.get("reasons"))
        + "<h3>Result</h3>"
        + (
            f"<pre>{_html(json.dumps(result, ensure_ascii=True, sort_keys=True))}</pre>"
            if result is not None
            else "<p>&lt;none&gt;</p>"
        )
        + (
            f'<form method="post" action="{_html(_project_location(project_id))}/references">'
            "<h2>Add references</h2>"
            '<label>Gate 15 governed asset reference'
            '<input name="gate15_reference"></label>'
            '<label>Gate 16 operator decision reference'
            '<input name="gate16_reference"></label>'
            '<label>Other evidence reference'
            '<input name="evidence_reference"></label>'
            '<button type="submit">Save references</button></form>'
        )
        + (
            f'<form method="post" action="{_html(_project_location(project_id))}/assessment">'
            "<h2>Submit assessment</h2>"
            '<label>Requested next state<input name="requested_next_state" required>'
            "</label>"
            '<label>Reason codes<textarea name="reason_codes" required></textarea>'
            "</label>"
            '<button type="submit">Assess</button></form>'
        )
        + (
            f'<form method="post" action="{_html(_project_location(project_id))}/reopen">'
            '<button type="submit">Reopen saved work</button></form>'
        )
    )
    return _page("RCIS Project", content)


def _render_reasons(reason_codes: Sequence[str]) -> str:
    items = "".join(
        f'<li class="reason"><code>{_html(code)}</code></li>'
        for code in reason_codes
    )
    return _page("RCIS Safe Stop", f"<p>Operation failed closed.</p><ul>{items}</ul>")


class LocalOperatorApplication:
    """WSGI interface that delegates all governed behavior to a runtime."""

    def __init__(self, runtime: LocalOperatorRuntime) -> None:
        if runtime is None:
            raise TypeError("runtime must not be None")
        self._runtime = runtime

    def __call__(
        self,
        environ: Mapping[str, object],
        start_response: object,
    ) -> list[bytes]:
        method = str(environ.get("REQUEST_METHOD") or "GET").upper()
        path = unquote(str(environ.get("PATH_INFO") or "/"))
        try:
            if method == "GET" and path == "/":
                return _response(
                    start_response,
                    "200 OK",
                    _render_root(self._runtime.list_projects()),
                )
            if method == "POST" and path == "/projects":
                project = self._runtime.create_project(_read_form(environ))
                return _redirect(
                    start_response,
                    _project_location(_project_id(project)),
                )
            if path.startswith("/projects/"):
                parts = tuple(part for part in path.split("/") if part)
                if len(parts) == 2 and method == "GET":
                    project = self._runtime.get_project(parts[1])
                    if project is None:
                        return _response(
                            start_response,
                            "404 Not Found",
                            _page("Not Found", "<p>PROJECT_NOT_FOUND</p>"),
                        )
                    return _response(
                        start_response,
                        "200 OK",
                        _render_project(project),
                    )
                if len(parts) == 3 and method == "POST":
                    project_id = parts[1]
                    action = parts[2]
                    if action == "references":
                        self._runtime.add_references(
                            project_id,
                            _read_form(environ),
                        )
                    elif action == "assessment":
                        self._runtime.submit_assessment(
                            project_id,
                            _read_form(environ),
                        )
                    elif action == "reopen":
                        self._runtime.reopen_project(project_id)
                    else:
                        return _response(
                            start_response,
                            "404 Not Found",
                            _page("Not Found", "<p>ROUTE_NOT_FOUND</p>"),
                        )
                    return _redirect(
                        start_response,
                        _project_location(project_id),
                    )
            return _response(
                start_response,
                "404 Not Found",
                _page("Not Found", "<p>ROUTE_NOT_FOUND</p>"),
            )
        except LocalOperatorRuntimeError as exc:
            return _response(
                start_response,
                "409 Conflict",
                _render_reasons(exc.reason_codes),
            )
        except Exception:
            return _response(
                start_response,
                "503 Service Unavailable",
                _render_reasons(("DEPENDENCY_FAILURE",)),
            )


def create_application(runtime: LocalOperatorRuntime) -> LocalOperatorApplication:
    """Create the minimum local WSGI application."""

    return LocalOperatorApplication(runtime)


def _load_runtime() -> LocalOperatorRuntime:
    try:
        module = importlib.import_module("rie.local_operator_runtime")
        factory = getattr(module, "build_local_operator_runtime")
        runtime = factory()
    except Exception as exc:
        raise LocalOperatorRuntimeError(
            ("LOCAL_OPERATOR_RUNTIME_UNAVAILABLE",)
        ) from exc
    if runtime is None:
        raise LocalOperatorRuntimeError(("LOCAL_OPERATOR_RUNTIME_UNAVAILABLE",))
    return runtime


def main(argv: Sequence[str] | None = None) -> int:
    """Run the interface on the local loopback address only."""

    parser = argparse.ArgumentParser(prog="rcis-local")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    namespace = parser.parse_args(argv)
    if namespace.port < 1 or namespace.port > 65535:
        parser.error("--port must be from 1 through 65535")
    try:
        runtime = _load_runtime()
    except LocalOperatorRuntimeError as exc:
        print("|".join(exc.reason_codes))
        return 2
    application = create_application(runtime)
    with make_server(LOCAL_BIND_ADDRESS, namespace.port, application) as server:
        print(f"http://{LOCAL_BIND_ADDRESS}:{namespace.port}/")
        server.serve_forever()
    return 0


__all__ = (
    "DEFAULT_PORT",
    "LOCAL_BIND_ADDRESS",
    "LocalOperatorApplication",
    "LocalOperatorRuntime",
    "LocalOperatorRuntimeError",
    "create_application",
    "main",
)
