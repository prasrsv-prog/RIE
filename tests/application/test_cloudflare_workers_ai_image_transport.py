from __future__ import annotations

import ast
import base64
import json
from pathlib import Path

import pytest

from rie.application.cloudflare_workers_ai_image_transport import (
    CloudflareWorkersAIHTTPResponse,
    make_cloudflare_workers_ai_image_transport,
)

PROVIDER = "cloudflare-workers-ai"
MODEL = "@cf/black-forest-labs/flux-1-schnell"


def payload(**changes: object) -> dict[str, object]:
    value: dict[str, object] = {
        "provider_id": PROVIDER,
        "model_id": MODEL,
        "grounded_prompt": "Exact governed prompt.",
        "reference_media_refs": (),
    }
    value.update(changes)
    return value


def success_body(image: bytes = b"png") -> bytes:
    encoded = base64.b64encode(image).decode("ascii")
    return json.dumps({"success": True, "result": {"image": encoded}}).encode()


def test_success_is_deterministic_and_invokes_http_once() -> None:
    calls: list[tuple[str, dict[str, str], bytes]] = []

    def post(url: str, headers: dict[str, str], body: bytes) -> CloudflareWorkersAIHTTPResponse:
        calls.append((url, headers, body))
        return CloudflareWorkersAIHTTPResponse(200, success_body(), "req-1")

    transport = make_cloudflare_workers_ai_image_transport(
        account_id="acct", api_token="secret", http_post=post
    )
    result = transport(payload())

    assert len(calls) == 1
    url, headers, body = calls[0]
    assert url == (
        "https://api.cloudflare.com/client/v4/accounts/acct/ai/run/"
        "@cf/black-forest-labs/flux-1-schnell"
    )
    assert headers == {
        "Authorization": "Bearer secret",
        "Content-Type": "application/json",
    }
    assert body == b'{"prompt":"Exact governed prompt."}'
    assert result.execution_status == "SUCCEEDED"
    assert result.provider_output_refs == ("data:image/png;base64,cG5n",)
    assert result.provider_execution_ref == "req-1"


@pytest.mark.parametrize("field,value", [
    ("provider_id", "other"),
    ("model_id", "other"),
])
def test_exact_provider_and_model_are_required(field: str, value: str) -> None:
    called = False
    def post(*args: object) -> CloudflareWorkersAIHTTPResponse:
        nonlocal called
        called = True
        raise AssertionError
    transport = make_cloudflare_workers_ai_image_transport(
        account_id="acct", api_token="token", http_post=post
    )
    with pytest.raises(ValueError):
        transport(payload(**{field: value}))
    assert called is False


def test_references_fail_before_network() -> None:
    called = False
    def post(*args: object) -> CloudflareWorkersAIHTTPResponse:
        nonlocal called
        called = True
        raise AssertionError
    transport = make_cloudflare_workers_ai_image_transport(
        account_id="acct", api_token="token", http_post=post
    )
    with pytest.raises(ValueError):
        transport(payload(reference_media_refs=("asset-1",)))
    assert called is False


@pytest.mark.parametrize("account,token", [("", "token"), ("acct", "")])
def test_missing_credentials_fail_at_factory(account: str, token: str) -> None:
    with pytest.raises(ValueError):
        make_cloudflare_workers_ai_image_transport(
            account_id=account, api_token=token, http_post=lambda *args: None
        )


@pytest.mark.parametrize("response", [
    CloudflareWorkersAIHTTPResponse(429, b'{"success":false}'),
    CloudflareWorkersAIHTTPResponse(401, b'{"success":false}'),
    CloudflareWorkersAIHTTPResponse(200, b"not-json"),
    CloudflareWorkersAIHTTPResponse(200, b'{"success":false}'),
    CloudflareWorkersAIHTTPResponse(200, b'{"success":true,"result":{}}'),
    CloudflareWorkersAIHTTPResponse(200, b'{"success":true,"result":{"image":"!"}}'),
])
def test_error_and_malformed_responses_fail_closed(
    response: CloudflareWorkersAIHTTPResponse,
) -> None:
    calls = 0
    def post(*args: object) -> CloudflareWorkersAIHTTPResponse:
        nonlocal calls
        calls += 1
        return response
    transport = make_cloudflare_workers_ai_image_transport(
        account_id="acct", api_token="token", http_post=post
    )
    with pytest.raises(RuntimeError):
        transport(payload())
    assert calls == 1


def test_source_has_no_hidden_network_env_retry_or_candidate_admission() -> None:
    path = Path(__file__).parents[2] / "src/rie/application/cloudflare_workers_ai_image_transport.py"
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    imports = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    from_imports = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not ({"requests", "httpx", "urllib.request", "os"} & (imports | from_imports))
    lowered = text.lower()
    for forbidden in (
        "os.environ", "getenv(", "retry", "creative_result_candidate",
        "time.sleep", "requests.", "httpx.", "urllib.request",
    ):
        assert forbidden not in lowered
