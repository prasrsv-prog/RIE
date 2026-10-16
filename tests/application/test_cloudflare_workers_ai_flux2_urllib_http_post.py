"""No-network tests of the isolated FLUX2 multipart HTTPS function."""
from __future__ import annotations

import io
import urllib.error
from email.message import Message

import pytest

import rie.application.cloudflare_workers_ai_flux2_urllib_http_post as uut
from rie.application.cloudflare_workers_ai_image_transport import CloudflareWorkersAIHTTPResponse

ENDPOINT = "https://api.cloudflare.com/client/v4/accounts/account-123/ai/run/@cf/black-forest-labs/flux-2-klein-4b"
BOUNDARY = "rcis-" + "a" * 32
BODY = (f"--{BOUNDARY}\r\nContent-Disposition: form-data; name=\"prompt\"\r\n\r\nhi\r\n--{BOUNDARY}--\r\n").encode()
HEADERS = {"Authorization": "Bearer local-fake-token", "Content-Type": f"multipart/form-data; boundary={BOUNDARY}"}


class FakeResponse:
    def __init__(self, code=200, body=b'{}', ray="ray-local"):
        self.code, self.body, self.headers = code, body, Message()
        self.headers["cf-ray"] = ray
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def getcode(self): return self.code
    def read(self, limit=-1): return self.body[:limit]


def test_exact_endpoint_and_request_use_fake_opener_only(monkeypatch):
    calls = []
    class FakeOpener:
        def open(self, request, *, timeout):
            calls.append((request, timeout))
            return FakeResponse(200, b'{"success":true}')
    monkeypatch.setattr(uut.urllib.request, "build_opener", lambda handler: FakeOpener())
    response = uut.cloudflare_workers_ai_flux2_urllib_http_post(ENDPOINT, HEADERS, BODY)
    assert isinstance(response, CloudflareWorkersAIHTTPResponse)
    assert response.status_code == 200 and response.request_id == "ray-local"
    assert len(calls) == 1
    request, timeout = calls[0]
    assert request.full_url == ENDPOINT and request.get_method() == "POST"
    assert request.data == BODY and timeout == 120.0
    assert request.get_header("Content-type") == HEADERS["Content-Type"]
    assert isinstance(uut._NoRedirect(), uut.urllib.request.HTTPRedirectHandler)
    assert uut._NoRedirect().redirect_request(None, None, 302, None, None, None) is None


@pytest.mark.parametrize("change", [
    "host", "http", "wrong-model", "query", "credentials", "port", "account", "wrong-content-type", "bad-boundary", "wrong-token", "extra-header", "empty-body", "text-body", "timeout"
])
def test_invalid_parameters_reject_without_opening(monkeypatch, change):
    monkeypatch.setattr(uut.urllib.request, "build_opener", lambda *a: pytest.fail("network opener must not be constructed"))
    endpoint, headers, body, timeout = ENDPOINT, dict(HEADERS), BODY, 120.0
    if change == "host": endpoint = endpoint.replace("api.cloudflare.com", "evil.example")
    elif change == "http": endpoint = endpoint.replace("https://", "http://")
    elif change == "wrong-model": endpoint = endpoint.replace("flux-2-klein-4b", "flux-1-schnell")
    elif change == "query": endpoint += "?oops=1"
    elif change == "credentials": endpoint = endpoint.replace("api.cloudflare.com", "x@api.cloudflare.com")
    elif change == "port": endpoint = endpoint.replace("api.cloudflare.com", "api.cloudflare.com:443")
    elif change == "account": endpoint = endpoint.replace("account-123", "bad/account")
    elif change == "wrong-content-type": headers["Content-Type"] = "application/json"
    elif change == "bad-boundary": body = BODY[:-3]
    elif change == "wrong-token": headers["Authorization"] = "wrong"
    elif change == "extra-header": headers["User-Agent"] = "fake"
    elif change == "empty-body": body = b""
    elif change == "text-body": body = "not bytes"
    elif change == "timeout": timeout = 121
    with pytest.raises((ValueError, TypeError)):
        uut.cloudflare_workers_ai_flux2_urllib_http_post(endpoint, headers, body, timeout_seconds=timeout)


def test_http_429_returns_typed_failure_without_retry(monkeypatch):
    calls = []
    class FakeOpener:
        def open(self, request, *, timeout):
            calls.append(1)
            raise urllib.error.HTTPError(ENDPOINT, 429, "Rate Limit", Message(), io.BytesIO(b'{"success":false}'))
    monkeypatch.setattr(uut.urllib.request, "build_opener", lambda handler: FakeOpener())
    response = uut.cloudflare_workers_ai_flux2_urllib_http_post(ENDPOINT, HEADERS, BODY)
    assert response.status_code == 429 and response.body == b'{"success":false}'
    assert len(calls) == 1


def test_url_error_is_sanitized(monkeypatch):
    class FakeOpener:
        def open(self, request, *, timeout): raise urllib.error.URLError("fake-secret")
    monkeypatch.setattr(uut.urllib.request, "build_opener", lambda handler: FakeOpener())
    with pytest.raises(RuntimeError, match="FLUX2 HTTPS request failed") as error:
        uut.cloudflare_workers_ai_flux2_urllib_http_post(ENDPOINT, HEADERS, BODY)
    assert "fake-secret" not in str(error.value)
