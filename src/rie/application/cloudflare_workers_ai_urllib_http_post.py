"""Concrete stdlib HTTP POST boundary for Cloudflare Workers AI image transport.

This module provides the smallest real outbound HTTPS implementation required by
``make_cloudflare_workers_ai_image_transport``. It performs no provider
selection, retry, regeneration, persistence, or invocation until the returned
callable is explicitly used by a separately authorized execution gate.
"""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping

from rie.application.cloudflare_workers_ai_image_transport import (
    CloudflareWorkersAIHTTPResponse,
)

_API_SCHEME = "https"
_API_HOST = "api.cloudflare.com"
_MODEL_PATH_SUFFIX = "/ai/run/@cf/black-forest-labs/flux-1-schnell"
_DEFAULT_TIMEOUT_SECONDS = 120.0


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _request_id(headers: object) -> str:
    getter = getattr(headers, "get", None)
    if not callable(getter):
        return ""
    for name in ("cf-ray", "x-request-id"):
        value = getter(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _validate_endpoint(endpoint: str) -> str:
    normalized = _required_text(endpoint, "endpoint")
    parsed = urllib.parse.urlsplit(normalized)

    if parsed.scheme != _API_SCHEME or parsed.hostname != _API_HOST:
        raise ValueError("endpoint must use the fixed Cloudflare API HTTPS host")
    if parsed.username is not None or parsed.password is not None or parsed.port is not None:
        raise ValueError("endpoint authority must not contain credentials or a custom port")
    if parsed.query or parsed.fragment:
        raise ValueError("endpoint must not contain query parameters or fragments")

    prefix = "/client/v4/accounts/"
    if not parsed.path.startswith(prefix) or not parsed.path.endswith(_MODEL_PATH_SUFFIX):
        raise ValueError("endpoint is not an allowed Cloudflare Workers AI image endpoint")

    account_id = parsed.path[len(prefix) : -len(_MODEL_PATH_SUFFIX)]
    if not account_id or "/" in account_id:
        raise ValueError("endpoint must contain exactly one non-empty Cloudflare account id")

    return normalized


def cloudflare_workers_ai_urllib_http_post(
    endpoint: str,
    headers: Mapping[str, str],
    body: bytes,
    *,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
) -> CloudflareWorkersAIHTTPResponse:
    """Perform one concrete HTTPS POST to the governed Cloudflare Workers AI endpoint."""

    normalized_endpoint = _validate_endpoint(endpoint)

    if not isinstance(headers, Mapping):
        raise TypeError("headers must be a mapping")
    if not isinstance(body, bytes):
        raise TypeError("body must be bytes")
    if not body:
        raise ValueError("body must not be empty")
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)):
        raise TypeError("timeout_seconds must be numeric")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")

    request_headers: dict[str, str] = {}
    for key, value in headers.items():
        if not isinstance(key, str) or not key.strip():
            raise TypeError("header names must be non-empty strings")
        if not isinstance(value, str) or not value.strip():
            raise TypeError("header values must be non-empty strings")
        request_headers[key] = value

    authorization = request_headers.get("Authorization", "")
    if not authorization.startswith("Bearer ") or not authorization[len("Bearer ") :].strip():
        raise ValueError("Authorization header must contain a non-empty Bearer token")

    if request_headers.get("Content-Type") != "application/json":
        raise ValueError("Content-Type must be application/json")

    request = urllib.request.Request(
        url=normalized_endpoint,
        data=body,
        headers=request_headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=float(timeout_seconds)) as response:
            status_code = response.getcode()
            response_body = response.read()
            request_id = _request_id(response.headers)
    except urllib.error.HTTPError as exc:
        return CloudflareWorkersAIHTTPResponse(
            status_code=int(exc.code),
            body=exc.read(),
            request_id=_request_id(exc.headers),
        )
    except urllib.error.URLError as exc:
        raise RuntimeError("Cloudflare Workers AI network request failed") from exc

    if not isinstance(status_code, int):
        raise RuntimeError("Cloudflare Workers AI HTTP response status is invalid")
    if not isinstance(response_body, bytes):
        raise RuntimeError("Cloudflare Workers AI HTTP response body is invalid")

    return CloudflareWorkersAIHTTPResponse(
        status_code=status_code,
        body=response_body,
        request_id=request_id,
    )


__all__ = [
    "cloudflare_workers_ai_urllib_http_post",
]
