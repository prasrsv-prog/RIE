"""Concrete stdlib HTTP POST boundary for the existing OpenAI Images transport.

This module supplies the smallest real outbound HTTP implementation required by
``make_openai_images_transport``. It does not select providers or models,
retry, regenerate, persist data, or invoke a provider until the callable is
actually used by an explicitly authorized execution gate.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from collections.abc import Mapping

from rie.application.openai_images_transport import OpenAIImagesHTTPResponse

_OPENAI_API_ROOT = "https://api.openai.com"
_ALLOWED_ENDPOINTS = frozenset(
    {
        "/v1/images/generations",
        "/v1/images/edits",
    }
)
_DEFAULT_TIMEOUT_SECONDS = 120.0


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _request_id(headers: object) -> str:
    getter = getattr(headers, "get", None)
    if not callable(getter):
        return ""
    value = getter("x-request-id")
    return value.strip() if isinstance(value, str) else ""


def openai_images_urllib_http_post(
    endpoint: str,
    headers: Mapping[str, str],
    body: bytes,
    secret: str,
    *,
    timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
) -> OpenAIImagesHTTPResponse:
    """Perform one concrete HTTPS POST to the fixed OpenAI Images API root."""

    normalized_endpoint = _required_text(endpoint, "endpoint")
    normalized_secret = _required_text(secret, "secret")

    if normalized_endpoint not in _ALLOWED_ENDPOINTS:
        raise ValueError("endpoint is not an allowed OpenAI Images endpoint")
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

    expected_authorization = f"Bearer {normalized_secret}"
    if request_headers.get("Authorization") != expected_authorization:
        raise ValueError("Authorization header does not match the supplied secret")

    url = f"{_OPENAI_API_ROOT}{normalized_endpoint}"
    request = urllib.request.Request(
        url=url,
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
        response_body = exc.read()
        return OpenAIImagesHTTPResponse(
            status_code=int(exc.code),
            body=response_body,
            request_id=_request_id(exc.headers),
        )
    except urllib.error.URLError as exc:
        raise RuntimeError("OpenAI Images network request failed") from exc

    if not isinstance(status_code, int):
        raise RuntimeError("OpenAI Images HTTP response status is invalid")
    if not isinstance(response_body, bytes):
        raise RuntimeError("OpenAI Images HTTP response body is invalid")

    return OpenAIImagesHTTPResponse(
        status_code=status_code,
        body=response_body,
        request_id=request_id,
    )


__all__ = [
    "openai_images_urllib_http_post",
]
