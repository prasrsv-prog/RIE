"""Offline-only FLUX2 reference serializer tests; no live Cloudflare requests."""
from __future__ import annotations

import base64
import hashlib
import json
import struct
import zlib
from pathlib import Path

import pytest

from rie.application.cloudflare_workers_ai_image_transport import CloudflareWorkersAIHTTPResponse
from rie.application.cloudflare_workers_ai_flux2_reference_transport import (
    GovernedFlux2PNGReference,
    make_cloudflare_workers_ai_flux2_reference_transport,
)


def _png(width: int = 12, height: int = 9) -> bytes:
    def chunk(name: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name + data) & 0xffffffff)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    pixels = b"".join(b"\x00" + (b"\x01\x02\x03" * width) for _ in range(height))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(pixels)) + chunk(b"IEND", b"")


def _refs(tmp_path: Path, count: int = 4) -> tuple[GovernedFlux2PNGReference, ...]:
    answer = []
    for index in range(count):
        content = _png(width=12 + index, height=9 + index)
        path = tmp_path / f"reference-{index}.png"
        path.write_bytes(content)
        answer.append(GovernedFlux2PNGReference(
            media_ref=f"governed:{index}", local_path=str(path),
            sha256=hashlib.sha256(content).hexdigest(), byte_count=len(content),
            width=12 + index, height=9 + index,
        ))
    return tuple(answer)


def _payload(ids, **override):
    value = {
        "provider_id": "cloudflare-workers-ai",
        "model_id": "@cf/black-forest-labs/flux-2-klein-4b",
        "grounded_prompt": "Photograph a governed motorcycle helmet, no invented labels.",
        "reference_media_refs": tuple(ids),
    }
    value.update(override)
    return value


def _transport(tmp_path, count=4, response=None):
    references = _refs(tmp_path, count)
    calls = []
    encoded = base64.b64encode(_png()).decode("ascii")
    good_response = CloudflareWorkersAIHTTPResponse(
        200, json.dumps({"success": True, "result": {"image": encoded}}).encode(), "ray-test"
    )

    def fake_post(endpoint, headers, body):
        calls.append((endpoint, headers, body))
        return response if response is not None else good_response

    handler = make_cloudflare_workers_ai_flux2_reference_transport(
        account_id="account-123", api_token="injected-test-token", http_post=fake_post,
        ordered_references=references,
    )
    return handler, references, calls


def test_exact_four_references_and_multipart_fields_without_network(tmp_path):
    handler, references, calls = _transport(tmp_path)
    reply = handler(_payload([ref.media_ref for ref in references]))
    assert len(calls) == 1
    endpoint, headers, body = calls[0]
    assert endpoint == "https://api.cloudflare.com/client/v4/accounts/account-123/ai/run/@cf/black-forest-labs/flux-2-klein-4b"
    assert headers["Authorization"] == "Bearer injected-test-token"
    boundary = headers["Content-Type"].split("boundary=")[1].encode("ascii")
    assert boundary.startswith(b"rcis-") and len(boundary) == 37
    assert body.count(b'Content-Disposition: form-data; name="prompt"') == 1
    assert b"photograph" not in body  # case-sensitive, prompt starts with Photograph
    assert b"Photograph a governed motorcycle helmet" in body
    assert body.count(b"Content-Type: image/png") == 4
    for i, ref in enumerate(references):
        assert body.count(f'name="input_image_{i}"'.encode()) == 1
        assert body.index(Path(ref.local_path).read_bytes()) > 0
    assert b'input_image_4' not in body
    assert body.endswith(b"--" + boundary + b"--\r\n")
    assert reply.execution_status == "SUCCEEDED"
    assert reply.provider_execution_ref == "ray-test"
    assert reply.provider_output_refs[0].startswith("data:image/png;base64,")


@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_explicit_one_to_four_allowed(tmp_path, count):
    handler, references, calls = _transport(tmp_path, count)
    handler(_payload([ref.media_ref for ref in references]))
    assert len(calls) == 1


@pytest.mark.parametrize("variant", ["reordered", "missing", "duplicate", "unknown", "wrong-model", "wrong-provider", "extra-field"])
def test_bad_selection_or_request_fails_before_http(tmp_path, variant):
    handler, references, calls = _transport(tmp_path)
    ids = [ref.media_ref for ref in references]
    req = _payload(ids)
    if variant == "reordered": req["reference_media_refs"] = tuple(reversed(ids))
    elif variant == "missing": req["reference_media_refs"] = tuple(ids[:-1])
    elif variant == "duplicate": req["reference_media_refs"] = (ids[0],) * 4
    elif variant == "unknown": req["reference_media_refs"] = tuple(ids[:3] + ["unknown"])
    elif variant == "wrong-model": req["model_id"] = "@cf/black-forest-labs/flux-1-schnell"
    elif variant == "wrong-provider": req["provider_id"] = "other"
    else: req["seed"] = 5
    with pytest.raises(ValueError): handler(req)
    assert not calls


def test_tampering_with_png_blocks_request(tmp_path):
    handler, references, calls = _transport(tmp_path)
    Path(references[2].local_path).write_bytes(_png(15, 11))
    with pytest.raises(ValueError): handler(_payload([ref.media_ref for ref in references]))
    assert calls == []


def test_png_exact_digest_mismatch_blocks_request(tmp_path):
    references = _refs(tmp_path)
    tampered = list(references)
    first = references[0]
    tampered[0] = GovernedFlux2PNGReference(
        media_ref=first.media_ref, local_path=first.local_path, sha256="0" * 64,
        byte_count=first.byte_count, width=first.width, height=first.height,
    )
    hits = []
    handler = make_cloudflare_workers_ai_flux2_reference_transport(
        account_id="account-123", api_token="token", http_post=lambda *a: hits.append(a),
        ordered_references=tuple(tampered),
    )
    with pytest.raises(ValueError): handler(_payload([r.media_ref for r in tampered]))
    assert hits == []


def test_duplicate_exact_allowlist_blocked_at_factory(tmp_path):
    refs = _refs(tmp_path)
    with pytest.raises(ValueError):
        make_cloudflare_workers_ai_flux2_reference_transport(
            account_id="acct", api_token="token", http_post=lambda *a: None,
            ordered_references=(refs[0], refs[0]),
        )


@pytest.mark.parametrize("bad", [(), None, (1,), tuple(range(5))])
def test_invalid_allowlist_fail_closed(bad):
    with pytest.raises((TypeError, ValueError)):
        make_cloudflare_workers_ai_flux2_reference_transport(
            account_id="acct", api_token="token", http_post=lambda *a: None,
            ordered_references=bad,
        )


@pytest.mark.parametrize("response", [
    CloudflareWorkersAIHTTPResponse(401, b'{}'),
    CloudflareWorkersAIHTTPResponse(429, b'{}'),
    CloudflareWorkersAIHTTPResponse(200, b'not json'),
    CloudflareWorkersAIHTTPResponse(200, b'{"success":false}'),
    CloudflareWorkersAIHTTPResponse(200, b'{"success":true,"result":{}}'),
    CloudflareWorkersAIHTTPResponse(200, b'{"success":true,"result":{"image":"!!!"}}'),
    CloudflareWorkersAIHTTPResponse(200, b'{"success":true,"result":{"image":"aGVsbG8="}}'),
])
def test_failure_response_never_succeeds(tmp_path, response):
    handler, references, calls = _transport(tmp_path, response=response)
    with pytest.raises(RuntimeError): handler(_payload([ref.media_ref for ref in references]))
    assert len(calls) == 1


def test_factory_does_not_invoke_post(tmp_path):
    refs = _refs(tmp_path)
    calls = []
    make_cloudflare_workers_ai_flux2_reference_transport(
        account_id="acct", api_token="token", http_post=lambda *a: calls.append(a),
        ordered_references=refs,
    )
    assert calls == []
