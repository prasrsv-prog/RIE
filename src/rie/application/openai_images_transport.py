"""Explicit OpenAI Images transport for one governed visual-generation request."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from rie.application.concrete_visual_generation_execution_adapter import (
    ProviderExecutionResponse,
)


@dataclass(frozen=True, slots=True)
class OpenAIImagesHTTPResponse:
    status_code: int
    body: bytes
    request_id: str = ""


OpenAIImagesHTTPPost = Callable[
    [str, Mapping[str, str], bytes, str],
    OpenAIImagesHTTPResponse,
]


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _decode_media_ref(value: str) -> tuple[str, bytes]:
    ref = _text(value, "reference_media_refs")
    prefix = "data:image/"
    if not ref.startswith(prefix) or ";base64," not in ref:
        raise ValueError("reference_media_refs must be base64 image data URLs")
    media_type, encoded = ref.split(";base64,", 1)
    subtype = media_type[len("data:image/"):]
    if subtype not in {"png", "jpeg", "jpg", "webp"}:
        raise ValueError("unsupported reference image type")
    try:
        payload = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise ValueError("invalid reference image base64") from exc
    if not payload:
        raise ValueError("reference image must not be empty")
    filename = f"reference.{('jpg' if subtype == 'jpeg' else subtype)}"
    return filename, payload


def _multipart(
    *,
    boundary: str,
    model: str,
    prompt: str,
    refs: Sequence[str],
) -> bytes:
    chunks: list[bytes] = []

    def field(name: str, value: str) -> None:
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode(),
            value.encode("utf-8"),
            b"\r\n",
        ])

    field("model", model)
    field("prompt", prompt)
    for ref in refs:
        filename, payload = _decode_media_ref(ref)
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="image[]"; filename="{filename}"\r\n'.encode(),
            b"Content-Type: application/octet-stream\r\n\r\n",
            payload,
            b"\r\n",
        ])
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks)


def make_openai_images_transport(
    *,
    api_key: str,
    http_post: OpenAIImagesHTTPPost,
) -> Callable[[Mapping[str, object]], ProviderExecutionResponse]:
    secret = _text(api_key, "api_key")
    if not callable(http_post):
        raise TypeError("http_post must be callable")

    def transport(payload: Mapping[str, object]) -> ProviderExecutionResponse:
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be a mapping")
        expected = {"provider_id", "model_id", "grounded_prompt", "reference_media_refs"}
        if set(payload) != expected:
            raise ValueError("payload fields do not match the OpenAI Images contract")
        if _text(payload["provider_id"], "provider_id") != "openai":
            raise ValueError("provider_id must be exactly openai")
        model = _text(payload["model_id"], "model_id")
        prompt = _text(payload["grounded_prompt"], "grounded_prompt")
        refs = payload["reference_media_refs"]
        if not isinstance(refs, tuple) or any(not isinstance(x, str) for x in refs):
            raise TypeError("reference_media_refs must be a tuple of strings")

        headers = {"Authorization": f"Bearer {secret}"}
        if refs:
            boundary = "rcis-openai-images-boundary"
            headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
            body = _multipart(boundary=boundary, model=model, prompt=prompt, refs=refs)
            endpoint = "/v1/images/edits"
        else:
            headers["Content-Type"] = "application/json"
            body = json.dumps(
                {"model": model, "prompt": prompt},
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            endpoint = "/v1/images/generations"

        response = http_post(endpoint, headers, body, secret)
        if not isinstance(response, OpenAIImagesHTTPResponse):
            raise TypeError("http_post returned an invalid response")
        if response.status_code < 200 or response.status_code >= 300:
            raise RuntimeError(f"OpenAI Images request failed with status {response.status_code}")
        try:
            decoded = json.loads(response.body.decode("utf-8"))
            data = decoded["data"]
        except Exception as exc:
            raise ValueError("OpenAI Images response is malformed") from exc
        if not isinstance(data, list) or not data:
            raise ValueError("OpenAI Images response contains no output")
        outputs: list[str] = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("OpenAI Images response item is malformed")
            value = item.get("url") or item.get("b64_json")
            outputs.append(_text(value, "provider output"))
        if len(set(outputs)) != len(outputs):
            raise ValueError("OpenAI Images response contains duplicate outputs")
        return ProviderExecutionResponse(
            execution_status="SUCCEEDED",
            provider_output_refs=tuple(outputs),
            provider_execution_ref=response.request_id,
            diagnostic_message="openai-images-completed",
        )

    return transport


__all__ = [
    "OpenAIImagesHTTPPost",
    "OpenAIImagesHTTPResponse",
    "make_openai_images_transport",
]
