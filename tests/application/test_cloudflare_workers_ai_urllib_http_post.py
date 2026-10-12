from __future__ import annotations

import base64
import io
import json
import urllib.error
from email.message import Message

import pytest

import rie.application.cloudflare_workers_ai_urllib_http_post as uut
from rie.application.cloudflare_workers_ai_image_transport import (
    CloudflareWorkersAIHTTPResponse,
    make_cloudflare_workers_ai_image_transport,
)


_ENDPOINT = (
    "https://api.cloudflare.com/client/v4/accounts/account-123/"
    "ai/run/@cf/black-forest-labs/flux-1-schnell"
)


class _FakeResponse:
    def __init__(
        self,
        *,
        status_code: int,
        body: bytes,
        request_id: str = "",
    ) -> None:
        self._status_code = status_code
        self._body = body
        self.headers = Message()
        if request_id:
            self.headers["cf-ray"] = request_id

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def getcode(self) -> int:
        return self._status_code

    def read(self) -> bytes:
        return self._body


def _headers(token: str = "token") -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def test_success_performs_one_https_post_to_exact_cloudflare_endpoint(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request, *, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return _FakeResponse(
            status_code=200,
            body=b'{"success":true,"result":{"image":"aGVsbG8="}}',
            request_id="ray-123",
        )

    monkeypatch.setattr(uut.urllib.request, "urlopen", fake_urlopen)

    result = uut.cloudflare_workers_ai_urllib_http_post(
        _ENDPOINT,
        _headers(),
        b'{"prompt":"sphere"}',
    )

    assert type(result) is CloudflareWorkersAIHTTPResponse
    assert result.status_code == 200
    assert result.body == b'{"success":true,"result":{"image":"aGVsbG8="}}'
    assert result.request_id == "ray-123"

    request = captured["request"]
    assert request.full_url == _ENDPOINT
    assert request.get_method() == "POST"
    assert request.data == b'{"prompt":"sphere"}'
    assert request.get_header("Authorization") == "Bearer token"
    assert request.get_header("Content-type") == "application/json"
    assert captured["timeout"] == 120.0


def test_existing_transport_composes_with_concrete_http_callable(monkeypatch) -> None:
    image_b64 = base64.b64encode(b"png-bytes").decode("ascii")

    def fake_urlopen(request, *, timeout):
        payload = json.loads(request.data.decode("utf-8"))
        assert payload == {"prompt": "one white sphere"}
        return _FakeResponse(
            status_code=200,
            body=json.dumps(
                {
                    "success": True,
                    "result": {"image": image_b64},
                }
            ).encode("utf-8"),
            request_id="ray-proof",
        )

    monkeypatch.setattr(uut.urllib.request, "urlopen", fake_urlopen)

    transport = make_cloudflare_workers_ai_image_transport(
        account_id="account-123",
        api_token="token",
        http_post=uut.cloudflare_workers_ai_urllib_http_post,
    )

    result = transport(
        {
            "provider_id": "cloudflare-workers-ai",
            "model_id": "@cf/black-forest-labs/flux-1-schnell",
            "grounded_prompt": "one white sphere",
            "reference_media_refs": (),
        }
    )

    assert result.execution_status == "SUCCEEDED"
    assert result.provider_output_refs == (f"data:image/png;base64,{image_b64}",)
    assert result.provider_execution_ref == "ray-proof"


def test_http_error_is_returned_as_typed_response(monkeypatch) -> None:
    headers = Message()
    headers["cf-ray"] = "ray-rate-limit"

    def fake_urlopen(request, *, timeout):
        raise urllib.error.HTTPError(
            request.full_url,
            429,
            "Too Many Requests",
            headers,
            io.BytesIO(b'{"success":false}'),
        )

    monkeypatch.setattr(uut.urllib.request, "urlopen", fake_urlopen)

    result = uut.cloudflare_workers_ai_urllib_http_post(
        _ENDPOINT,
        _headers(),
        b"{}",
    )

    assert result == CloudflareWorkersAIHTTPResponse(
        status_code=429,
        body=b'{"success":false}',
        request_id="ray-rate-limit",
    )


def test_url_error_is_wrapped_without_token_disclosure(monkeypatch) -> None:
    def fake_urlopen(request, *, timeout):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(uut.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="network request failed") as exc_info:
        uut.cloudflare_workers_ai_urllib_http_post(
            _ENDPOINT,
            _headers("top-secret"),
            b"{}",
        )

    assert "top-secret" not in str(exc_info.value)


@pytest.mark.parametrize(
    ("endpoint", "headers", "body", "expected_exception"),
    [
        (
            "https://evil.example/client/v4/accounts/account-123"
            "/ai/run/@cf/black-forest-labs/flux-1-schnell",
            _headers(),
            b"{}",
            ValueError,
        ),
        (
            "https://api.cloudflare.com/client/v4/accounts/"
            "ai/run/@cf/black-forest-labs/flux-1-schnell",
            _headers(),
            b"{}",
            ValueError,
        ),
        (
            _ENDPOINT + "?x=1",
            _headers(),
            b"{}",
            ValueError,
        ),
        (
            _ENDPOINT,
            {"Authorization": "token", "Content-Type": "application/json"},
            b"{}",
            ValueError,
        ),
        (
            _ENDPOINT,
            {"Authorization": "Bearer token", "Content-Type": "text/plain"},
            b"{}",
            ValueError,
        ),
        (
            _ENDPOINT,
            _headers(),
            b"",
            ValueError,
        ),
        (
            _ENDPOINT,
            _headers(),
            "{}",
            TypeError,
        ),
    ],
)
def test_invalid_request_is_rejected_before_network(
    monkeypatch,
    endpoint,
    headers,
    body,
    expected_exception,
) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("network must not be called")

    monkeypatch.setattr(uut.urllib.request, "urlopen", fail_if_called)

    with pytest.raises(expected_exception):
        uut.cloudflare_workers_ai_urllib_http_post(
            endpoint,
            headers,
            body,
        )


@pytest.mark.parametrize("timeout", [0, -1, True, "120"])
def test_invalid_timeout_is_rejected_before_network(monkeypatch, timeout) -> None:
    def fail_if_called(*args, **kwargs):
        raise AssertionError("network must not be called")

    monkeypatch.setattr(uut.urllib.request, "urlopen", fail_if_called)

    with pytest.raises((TypeError, ValueError)):
        uut.cloudflare_workers_ai_urllib_http_post(
            _ENDPOINT,
            _headers(),
            b"{}",
            timeout_seconds=timeout,
        )
