"""Explicit Cloudflare Workers AI text-to-image transport."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Callable, Mapping

from rie.application.concrete_visual_generation_execution_adapter import ProviderExecutionResponse

_PROVIDER_ID = "cloudflare-workers-ai"
_MODEL_ID = "@cf/black-forest-labs/flux-1-schnell"
_API_ROOT = "https://api.cloudflare.com/client/v4/accounts"


@dataclass(frozen=True)
class CloudflareWorkersAIHTTPResponse:
    status_code: int
    body: bytes
    request_id: str = ""


CloudflareWorkersAIHTTPPost = Callable[
    [str, Mapping[str, str], bytes], CloudflareWorkersAIHTTPResponse
]


def make_cloudflare_workers_ai_image_transport(
    *,
    account_id: str,
    api_token: str,
    http_post: CloudflareWorkersAIHTTPPost,
) -> Callable[[Mapping[str, object]], ProviderExecutionResponse]:
    """Build a single-call Cloudflare Workers AI transport."""

    normalized_account_id = account_id.strip()
    normalized_api_token = api_token.strip()
    if not normalized_account_id:
        raise ValueError("Cloudflare account_id must be nonblank")
    if not normalized_api_token:
        raise ValueError("Cloudflare api_token must be nonblank")
    if not callable(http_post):
        raise TypeError("http_post must be callable")

    endpoint = f"{_API_ROOT}/{normalized_account_id}/ai/run/{_MODEL_ID}"

    def transport(payload: Mapping[str, object]) -> ProviderExecutionResponse:
        if set(payload) != {
            "provider_id",
            "model_id",
            "grounded_prompt",
            "reference_media_refs",
        }:
            raise ValueError("unsupported or missing transport payload fields")
        if payload["provider_id"] != _PROVIDER_ID:
            raise ValueError("provider_id mismatch")
        if payload["model_id"] != _MODEL_ID:
            raise ValueError("model_id mismatch")

        prompt = payload["grounded_prompt"]
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("grounded_prompt must be nonblank")

        references = payload["reference_media_refs"]
        if not isinstance(references, (tuple, list)):
            raise TypeError("reference_media_refs must be a sequence")
        if references:
            raise ValueError("reference_media_refs are not supported by this transport")

        request_body = json.dumps(
            {"prompt": prompt},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {normalized_api_token}",
            "Content-Type": "application/json",
        }

        response = http_post(endpoint, headers, request_body)
        if not isinstance(response, CloudflareWorkersAIHTTPResponse):
            raise TypeError("http_post returned unsupported response type")
        if response.status_code < 200 or response.status_code >= 300:
            raise RuntimeError(f"Cloudflare Workers AI request failed with HTTP {response.status_code}")

        try:
            decoded = json.loads(response.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("Cloudflare Workers AI returned malformed JSON") from exc
        if not isinstance(decoded, dict) or decoded.get("success") is not True:
            raise RuntimeError("Cloudflare Workers AI returned unsuccessful response")

        result = decoded.get("result")
        if not isinstance(result, dict):
            raise RuntimeError("Cloudflare Workers AI response is missing result")
        image = result.get("image")
        if not isinstance(image, str) or not image.strip():
            raise RuntimeError("Cloudflare Workers AI response is missing image data")
        try:
            base64.b64decode(image, validate=True)
        except Exception as exc:
            raise RuntimeError("Cloudflare Workers AI image data is not valid base64") from exc

        output_ref = f"data:image/png;base64,{image}"
        return ProviderExecutionResponse(
            execution_status="SUCCEEDED",
            provider_output_refs=(output_ref,),
            provider_execution_ref=response.request_id.strip(),
            diagnostic_message="cloudflare-workers-ai image generation succeeded",
        )

    return transport
