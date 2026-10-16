"""Separate opt-in FLUX.2 multipart-only HTTP boundary with redirects disabled.

This module makes no request until its function is explicitly invoked. No
credential lookup, retry, JSON fallback, endpoint substitution or persistence.
"""

from __future__ import annotations

import re
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping

from rie.application.cloudflare_workers_ai_image_transport import (
    CloudflareWorkersAIHTTPResponse,
)

_SCHEME = "https"
_HOST = "api.cloudflare.com"
_SUFFIX = "/ai/run/@cf/black-forest-labs/flux-2-klein-4b"
_PREFIX = "/client/v4/accounts/"
_BOUNDARY_RE = re.compile(r"multipart/form-data; boundary=(rcis-[0-9a-f]{32})\Z")
_ACCOUNT_RE = re.compile(r"[a-zA-Z0-9_-]{1,64}\Z")
_MAX_BODY_BYTES = 10 * 1024 * 1024
_MAX_RESPONSE_BYTES = 8 * 1024 * 1024


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def _endpoint(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("endpoint must be a URL string")
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != _SCHEME or parsed.netloc != _HOST:
        raise ValueError("endpoint is not the fixed Cloudflare HTTPS host")
    if parsed.query or parsed.fragment or not parsed.path.startswith(_PREFIX):
        raise ValueError("endpoint contains a forbidden component")
    if not parsed.path.endswith(_SUFFIX):
        raise ValueError("endpoint is not the exact FLUX2 model")
    account = parsed.path[len(_PREFIX) : -len(_SUFFIX)]
    if not _ACCOUNT_RE.fullmatch(account):
        raise ValueError("account ID is invalid")
    return value


def _request_id(headers: object) -> str:
    getter = getattr(headers, "get", None)
    if callable(getter):
        for key in ("cf-ray", "x-request-id"):
            value = getter(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def cloudflare_workers_ai_flux2_urllib_http_post(
    endpoint: str,
    headers: Mapping[str, str],
    body: bytes,
    *,
    timeout_seconds: float = 120.0,
) -> CloudflareWorkersAIHTTPResponse:
    """Execute exactly one fixed-host HTTPS multipart POST when called."""
    url = _endpoint(endpoint)
    if not isinstance(headers, Mapping) or set(headers) != {"Authorization", "Content-Type"}:
        raise ValueError("only Authorization and Content-Type headers are permitted")
    token = headers["Authorization"]
    if not isinstance(token, str) or not token.startswith("Bearer ") or not token[7:].strip():
        raise ValueError("Bearer token is required")
    if "\r" in token or "\n" in token:
        raise ValueError("Bearer token contains forbidden newlines")
    content_type = headers["Content-Type"]
    if not isinstance(content_type, str):
        raise TypeError("Content-Type must be a string")
    match = _BOUNDARY_RE.fullmatch(content_type)
    if match is None:
        raise ValueError("Content-Type must have exact FLUX2 multipart boundary")
    if not isinstance(body, bytes):
        raise TypeError("multipart request body must be bytes")
    if not 1 <= len(body) <= _MAX_BODY_BYTES:
        raise ValueError("multipart request body size is not permitted")
    boundary = match.group(1).encode("ascii")
    if not body.startswith(b"--" + boundary + b"\r\n") or not body.endswith(b"--" + boundary + b"--\r\n"):
        raise ValueError("multipart boundary does not match request body")
    if type(timeout_seconds) not in (int, float) or not 0 < timeout_seconds <= 120:
        raise ValueError("timeout_seconds must be bounded to 120 seconds")

    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    opener = urllib.request.build_opener(_NoRedirect())
    try:
        with opener.open(request, timeout=float(timeout_seconds)) as response:
            status = response.getcode()
            content = response.read(_MAX_RESPONSE_BYTES + 1)
            request_id = _request_id(response.headers)
    except urllib.error.HTTPError as exc:
        content = exc.read(_MAX_RESPONSE_BYTES + 1)
        status = int(exc.code)
        request_id = _request_id(exc.headers)
    except urllib.error.URLError as exc:
        raise RuntimeError("FLUX2 HTTPS request failed") from exc
    if type(status) is not int or not isinstance(content, bytes) or len(content) > _MAX_RESPONSE_BYTES:
        raise RuntimeError("FLUX2 HTTP response is invalid or oversized")
    return CloudflareWorkersAIHTTPResponse(status_code=status, body=content, request_id=request_id)


__all__ = ["cloudflare_workers_ai_flux2_urllib_http_post"]
