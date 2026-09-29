from __future__ import annotations

import base64
import json

import pytest

from rie.application.openai_images_transport import (
    OpenAIImagesHTTPResponse,
    make_openai_images_transport,
)


def _payload(refs=()):
    return {
        "provider_id": "openai",
        "model_id": "explicit-model",
        "grounded_prompt": "Exact governed prompt.",
        "reference_media_refs": refs,
    }


def test_prompt_only_uses_generations_exactly_once() -> None:
    calls = []
    def post(endpoint, headers, body, secret):
        calls.append((endpoint, headers, body, secret))
        return OpenAIImagesHTTPResponse(200, b'{"data":[{"url":"out-1"}]}', "req-1")
    transport = make_openai_images_transport(api_key="runtime-secret", http_post=post)
    result = transport(_payload())
    assert len(calls) == 1
    endpoint, headers, body, secret = calls[0]
    assert endpoint == "/v1/images/generations"
    assert headers["Authorization"] == "Bearer runtime-secret"
    assert secret == "runtime-secret"
    assert json.loads(body) == {"model": "explicit-model", "prompt": "Exact governed prompt."}
    assert result.provider_output_refs == ("out-1",)
    assert result.provider_execution_ref == "req-1"
    assert "runtime-secret" not in result.diagnostic_message


def test_reference_images_use_edits_once_and_preserve_order() -> None:
    calls = []
    a = "data:image/png;base64," + base64.b64encode(b"A").decode()
    b = "data:image/webp;base64," + base64.b64encode(b"B").decode()
    def post(endpoint, headers, body, secret):
        calls.append((endpoint, headers, body))
        return OpenAIImagesHTTPResponse(200, b'{"data":[{"b64_json":"generated"}]}')
    result = make_openai_images_transport(api_key="secret", http_post=post)(_payload((a, b)))
    assert len(calls) == 1
    endpoint, headers, body = calls[0]
    assert endpoint == "/v1/images/edits"
    assert headers["Content-Type"].startswith("multipart/form-data; boundary=")
    assert body.index(b"A") < body.index(b"B")
    assert result.provider_output_refs == ("generated",)


@pytest.mark.parametrize("provider", ["", "other"])
def test_provider_identity_fails_closed(provider: str) -> None:
    calls = []
    transport = make_openai_images_transport(
        api_key="secret",
        http_post=lambda *args: calls.append(args),
    )
    payload = _payload()
    payload["provider_id"] = provider
    with pytest.raises(ValueError):
        transport(payload)
    assert calls == []


def test_missing_credential_fails_before_network() -> None:
    with pytest.raises(ValueError, match="api_key"):
        make_openai_images_transport(api_key=" ", http_post=lambda *args: None)


def test_malformed_rejected_empty_and_duplicate_responses_fail_closed() -> None:
    bodies = [
        OpenAIImagesHTTPResponse(401, b'{"error":"denied"}'),
        OpenAIImagesHTTPResponse(200, b"not-json"),
        OpenAIImagesHTTPResponse(200, b'{"data":[]}'),
        OpenAIImagesHTTPResponse(200, b'{"data":[{"url":"x"},{"url":"x"}]}'),
    ]
    for response in bodies:
        transport = make_openai_images_transport(
            api_key="secret",
            http_post=lambda *args, response=response: response,
        )
        with pytest.raises((RuntimeError, ValueError)):
            transport(_payload())


def test_no_retry_fallback_candidate_or_environment_secret_read() -> None:
    from pathlib import Path
    source = (
        Path(__file__).resolve().parents[2]
        / "src" / "rie" / "application" / "openai_images_transport.py"
    ).read_text(encoding="utf-8").lower()
    for forbidden in (
        "os.environ", "getenv(", "retry(", "fallback", "creativeresultcandidate",
        "requests", "httpx",
    ):
        assert forbidden not in source
