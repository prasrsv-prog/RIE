"""Opt-in, source-bound FLUX.2 Klein 4B multipart reference transport.

No credential lookup, network access, source rewriting, provider choice, retry,
asset admission or persistence occurs in this module. The creator supplies the
exact ordered governed PNG allowlist and a separately authorized HTTP callable.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import secrets
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from rie.application.cloudflare_workers_ai_image_transport import (
    CloudflareWorkersAIHTTPResponse,
)
from rie.application.concrete_visual_generation_execution_adapter import (
    ProviderExecutionResponse,
)

_PROVIDER_ID = "cloudflare-workers-ai"
_MODEL_ID = "@cf/black-forest-labs/flux-2-klein-4b"
_ENDPOINT_BASE = "https://api.cloudflare.com/client/v4/accounts"
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_MAX_PNG_BYTES = 2 * 1024 * 1024
_MAX_RESPONSE_BYTES = 8 * 1024 * 1024
_REFERENCE_ID = re.compile(r"[a-zA-Z0-9_.:-]{1,128}\Z")
_ACCOUNT_ID = re.compile(r"[a-zA-Z0-9_-]{1,64}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")

Flux2HTTPPost = Callable[
    [str, Mapping[str, str], bytes], CloudflareWorkersAIHTTPResponse
]


@dataclass(frozen=True, slots=True)
class GovernedFlux2PNGReference:
    """Immutable exact-byte reference descriptor supplied by an approved gate."""

    media_ref: str
    local_path: str
    sha256: str
    byte_count: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if not isinstance(self.media_ref, str) or not _REFERENCE_ID.fullmatch(self.media_ref):
            raise ValueError("invalid explicit governed media_ref")
        if not isinstance(self.local_path, str) or not self.local_path.strip():
            raise ValueError("local_path must be nonblank")
        if not isinstance(self.sha256, str) or not _SHA256.fullmatch(self.sha256):
            raise ValueError("sha256 must be lowercase hex")
        if type(self.byte_count) is not int or not (24 <= self.byte_count <= _MAX_PNG_BYTES):
            raise ValueError("PNG byte_count exceeds governed bounds")
        for value in (self.width, self.height):
            if type(value) is not int or not (1 <= value < 512):
                raise ValueError("reference PNG axes must be below 512")


def _read_exact_png(reference: GovernedFlux2PNGReference) -> bytes:
    path = Path(reference.local_path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("governed reference must be an existing regular file")
    if path.stat().st_size != reference.byte_count:
        raise ValueError("governed reference byte count mismatch")
    content = path.read_bytes()
    if len(content) != reference.byte_count:
        raise ValueError("governed reference bytes changed during read")
    if hashlib.sha256(content).hexdigest() != reference.sha256:
        raise ValueError("governed reference SHA256 mismatch")
    if content[:8] != _PNG_SIGNATURE or content[12:16] != b"IHDR":
        raise ValueError("governed reference PNG header invalid")
    if struct.unpack(">II", content[16:24]) != (reference.width, reference.height):
        raise ValueError("governed reference PNG dimension mismatch")
    return content


def _multipart_body(prompt: str, references: tuple[bytes, ...]) -> tuple[str, bytes]:
    boundary = "rcis-" + secrets.token_hex(16)
    marker = boundary.encode("ascii")
    # Fail rather than encode an ambiguous multipart request.
    if any(marker in image for image in references) or marker in prompt.encode("utf-8"):
        raise ValueError("multipart boundary collision")
    chunks: list[bytes] = [
        b"--" + marker + b"\r\n"
        b'Content-Disposition: form-data; name="prompt"\r\n\r\n'
        + prompt.encode("utf-8") + b"\r\n"
    ]
    for index, image in enumerate(references):
        chunks.append(
            b"--" + marker + b"\r\n"
            + (f'Content-Disposition: form-data; name="input_image_{index}"; '
               f'filename="reference-{index}.png"\r\n').encode("ascii")
            + b"Content-Type: image/png\r\n\r\n"
            + image + b"\r\n"
        )
    chunks.append(b"--" + marker + b"--\r\n")
    return boundary, b"".join(chunks)


def make_cloudflare_workers_ai_flux2_reference_transport(
    *,
    account_id: str,
    api_token: str,
    http_post: Flux2HTTPPost,
    ordered_references: tuple[GovernedFlux2PNGReference, ...],
) -> Callable[[Mapping[str, object]], ProviderExecutionResponse]:
    """Create an explicitly selected transport; never auto-route or auto-call."""
    if not isinstance(account_id, str) or not _ACCOUNT_ID.fullmatch(account_id):
        raise ValueError("account_id must be a single safe path component")
    if not isinstance(api_token, str) or not api_token.strip():
        raise ValueError("api_token must be nonblank")
    if "\n" in api_token or "\r" in api_token:
        raise ValueError("api_token must not contain newlines")
    if not callable(http_post):
        raise TypeError("http_post must be callable")
    if not isinstance(ordered_references, tuple) or not 1 <= len(ordered_references) <= 4:
        raise ValueError("explicit selection must contain 1 to 4 ordered references")
    if not all(isinstance(ref, GovernedFlux2PNGReference) for ref in ordered_references):
        raise TypeError("ordered_references must be governed reference descriptors")
    ids = tuple(ref.media_ref for ref in ordered_references)
    if len(set(ids)) != len(ids) or len({ref.sha256 for ref in ordered_references}) != len(ids):
        raise ValueError("duplicate reference identity is forbidden")

    endpoint = f"{_ENDPOINT_BASE}/{account_id}/ai/run/{_MODEL_ID}"

    def transport(payload: Mapping[str, object]) -> ProviderExecutionResponse:
        if not isinstance(payload, Mapping) or set(payload) != {
            "provider_id", "model_id", "grounded_prompt", "reference_media_refs"
        }:
            raise ValueError("unsupported or missing transport fields")
        if payload["provider_id"] != _PROVIDER_ID or payload["model_id"] != _MODEL_ID:
            raise ValueError("provider/model mismatch")
        prompt = payload["grounded_prompt"]
        if not isinstance(prompt, str) or not prompt.strip() or len(prompt.encode("utf-8")) > 4096:
            raise ValueError("prompt must be nonblank and at most 4096 UTF8 bytes")
        requested = payload["reference_media_refs"]
        if not isinstance(requested, (tuple, list)) or tuple(requested) != ids:
            raise ValueError("reference identity or explicit order mismatch")
        image_bytes = tuple(_read_exact_png(ref) for ref in ordered_references)
        boundary, request_body = _multipart_body(prompt, image_bytes)
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
        response = http_post(endpoint, headers, request_body)
        if not isinstance(response, CloudflareWorkersAIHTTPResponse):
            raise TypeError("HTTP callable returned unsupported response type")
        if not 200 <= response.status_code < 300:
            raise RuntimeError(f"Cloudflare Workers AI request failed with HTTP {response.status_code}")
        if not isinstance(response.body, bytes) or len(response.body) > _MAX_RESPONSE_BYTES:
            raise RuntimeError("FLUX2 response exceeded bounded length or type")
        try:
            document = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("FLUX2 returned malformed JSON") from exc
        if not isinstance(document, dict) or document.get("success") is not True:
            raise RuntimeError("FLUX2 response is unsuccessful")
        result = document.get("result")
        if not isinstance(result, dict) or not isinstance(result.get("image"), str):
            raise RuntimeError("FLUX2 image response schema is unexpected")
        encoded_image = result["image"]
        try:
            decoded_image = base64.b64decode(encoded_image, validate=True)
        except (ValueError, base64.binascii.Error) as exc:
            raise RuntimeError("FLUX2 image is not valid base64") from exc
        if not decoded_image.startswith(_PNG_SIGNATURE):
            raise RuntimeError("FLUX2 decoded output is not PNG")
        return ProviderExecutionResponse(
            execution_status="SUCCEEDED",
            provider_output_refs=("data:image/png;base64," + encoded_image,),
            provider_execution_ref=response.request_id.strip(),
            diagnostic_message="cloudflare-workers-ai FLUX2 reference generation succeeded",
        )

    return transport


__all__ = ["GovernedFlux2PNGReference", "make_cloudflare_workers_ai_flux2_reference_transport"]
