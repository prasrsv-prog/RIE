from __future__ import annotations

import io
import urllib.error
from email.message import Message

import pytest

import rie.application.openai_images_urllib_http_post as uut
from rie.application.openai_images_transport import OpenAIImagesHTTPResponse


class _FakeResponse:
    def __init__(self, *, status_code: int, body: bytes, request_id: str = "") -> None:
        self._status_code = status_code
        self._body = body
        self.headers = Message()
        if request_id:
            self.headers["x-request-id"] = request_id

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def getcode(self) -> int:
        return self._status_code

    def read(self) -> bytes:
        return self._body


def _headers(secret: str = "secret") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {secret}",
        "Content-Type": "application/json",
    }


def test_success_performs_one_https_post_to_fixed_openai_root(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request, *, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return _FakeResponse(
            status_code=200,
            body=b'{"data":[{"b64_json":"abc"}]}',
            request_id="req-123",
        )

    monkeypatch.setattr(uut.urllib.request, "urlopen", fake_urlopen)

    result = uut.openai_images_urllib_http_post(
        "/v1/images/generations",
        _headers(),
        b'{"model":"gpt-image-1","prompt":"x"}',
        "secret",
    )

    assert type(result) is OpenAIImagesHTTPResponse
    assert result.status_code == 200
    assert result.body == b'{"data":[{"b64_json":"abc"}]}'
    assert result.request_id == "req-123"

    request = captured["request"]
    assert request.full_url == "https://api.openai.com/v1/images/generations"
    assert request.get_method() == "POST"
    assert request.data == b'{"model":"gpt-image-1","prompt":"x"}'
    assert request.get_header("Authorization") == "Bearer secret"
    assert captured["timeout"] == 120.0


def test_edits_endpoint_is_allowed(monkeypatch) -> None:
    seen: list[str] = []

    def fake_urlopen(request, *, timeout):
        seen.append(request.full_url)
        return _FakeResponse(status_code=200, body=b"{}")

    monkeypatch.setattr(uut.urllib.request, "urlopen", fake_urlopen)

    result = uut.openai_images_urllib_http_post(
        "/v1/images/edits",
        {
            "Authorization": "Bearer secret",
            "Content-Type": "multipart/form-data; boundary=x",
        },
        b"--x--",
        "secret",
        timeout_seconds=5,
    )

    assert result.status_code == 200
    assert seen == ["https://api.openai.com/v1/images/edits"]


def test_http_error_is_returned_as_typed_response(monkeypatch) -> None:
    headers = Message()
    headers["x-request-id"] = "req-rate-limit"

    def fake_urlopen(request, *, timeout):
        raise urllib.error.HTTPError(
            request.full_url,
            429,
            "Too Many Requests",
            headers,
            io.BytesIO(b'{"error":"rate_limit"}'),
        )

    monkeypatch.setattr(uut.urllib.request, "urlopen", fake_urlopen)

    result = uut.openai_images_urllib_http_post(
        "/v1/images/generations",
        _headers(),
        b"{}",
        "secret",
    )

    assert result == OpenAIImagesHTTPResponse(
        status_code=429,
        body=b'{"error":"rate_limit"}',
        request_id="req-rate-limit",
    )


def test_url_error_is_wrapped_without_secret_disclosure(monkeypatch) -> None:
    def fake_urlopen(request, *, timeout):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(uut.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="network request failed") as exc_info:
        uut.openai_images_urllib_http_post(
            "/v1/images/generations",
            _headers("top-secret"),
            b"{}",
            "top-secret",
        )

    assert "top-secret" not in str(exc_info.value)


@pytest.mark.parametrize(
    ("endpoint", "headers", "body", "secret", "expected_exception"),
    [
        ("/v1/chat/completions", _headers(), b"{}", "secret", ValueError),
        ("/v1/images/generations", _headers("other"), b"{}", "secret", ValueError),
        ("/v1/images/generations", _headers(), b"", "secret", ValueError),
        ("/v1/images/generations", _headers(), "{}", "secret", TypeError),
    ],
)
def test_invalid_request_is_rejected_before_network(
    monkeypatch,
    endpoint,
    headers,
    body,
    secret,
    expected_exception,
) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("network must not be called")

    monkeypatch.setattr(uut.urllib.request, "urlopen", fail_if_called)

    with pytest.raises(expected_exception):
        uut.openai_images_urllib_http_post(endpoint, headers, body, secret)


@pytest.mark.parametrize("timeout", [0, -1, True, "120"])
def test_invalid_timeout_is_rejected_before_network(monkeypatch, timeout) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("network must not be called")

    monkeypatch.setattr(uut.urllib.request, "urlopen", fail_if_called)

    with pytest.raises((TypeError, ValueError)):
        uut.openai_images_urllib_http_post(
            "/v1/images/generations",
            _headers(),
            b"{}",
            "secret",
            timeout_seconds=timeout,
        )
