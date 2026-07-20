
from dataclasses import replace

from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_CONTRACT_VERSION,
    EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION,
    ExtractionArtifact,
    ExtractionArtifactPageExtraction,
    ExtractionArtifactStructuralMetadata,
    ExtractionArtifactStructuralPage,
)
from rie.extraction.extraction_artifact_serializer import (
    ExtractionArtifactSerializer,
)


def _artifact(*, unicode_text=False):
    source_path = "/synthetic/source.pdf"
    pages = (
        ExtractionArtifactStructuralPage(
            page_index=0,
            width_points=612.0,
            height_points=792.0,
            rotation_degrees=0,
            inspection_status="inspected",
        ),
        ExtractionArtifactStructuralPage(
            page_index=1,
            width_points=612.0,
            height_points=792.0,
            rotation_degrees=0,
            inspection_status="inspected",
        ),
    )
    metadata = ExtractionArtifactStructuralMetadata(
        allowed=True,
        reason="pdf structural metadata result contract allowed",
        fixture_id="SRC-GATE5-001",
        source_label="SRC-GATE5-é" if unicode_text else "SRC-GATE5-001",
        fixture_path=source_path,
        fixture_type="product_spec_pdf",
        inspection_mode="structural_metadata_only",
        inspection_status="inspected",
        encrypted=False,
        page_count=2,
        inspected_page_count=2,
        page_details_truncated=False,
        page_details=pages,
        max_inspected_pages=10,
        inspection_error="",
        evidence_allowed=False,
        notes="",
    )
    extractions = (
        ExtractionArtifactPageExtraction(
            source_path=source_path,
            size_bytes=100,
            page_number=1,
            extraction_index=0,
            extraction_method="embedded_text",
            content="halaman é" if unicode_text else "",
            warnings=("warning α",) if unicode_text else (),
        ),
        ExtractionArtifactPageExtraction(
            source_path=source_path,
            size_bytes=100,
            page_number=2,
            extraction_index=1,
            extraction_method="embedded_text",
            content="page two",
            warnings=("No embedded text found.",),
        ),
    )
    provisional = ExtractionArtifact(
        contract_version=EXTRACTION_ARTIFACT_CONTRACT_VERSION,
        artifact_id="0" * 64,
        upstream_contract_version=(
            EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION
        ),
        upstream_status="completed",
        job_id="job-001",
        source_id="SRC-GATE5-001",
        source_path=source_path,
        source_checksum="a" * 64,
        structural_metadata=metadata,
        page_extractions=extractions,
        execution_report_location="/synthetic/execution.json",
        cleanup_completed=True,
    )
    return replace(
        provisional,
        artifact_id=ExtractionArtifactSerializer.derive_artifact_id(
            provisional
        ),
    )


import json

import pytest

from rie.extraction.extraction_artifact_contract import (
    ExtractionArtifactContractError,
    ExtractionArtifactIssueCode,
)
from rie.extraction.extraction_artifact_deserializer import (
    ExtractionArtifactDeserializer,
)


def _code(data):
    with pytest.raises(ExtractionArtifactContractError) as caught:
        ExtractionArtifactDeserializer.from_bytes(data)
    return caught.value.issue.code


def test_exact_value_and_byte_round_trip():
    artifact = _artifact(unicode_text=True)
    payload = ExtractionArtifactSerializer.to_bytes(artifact)
    restored = ExtractionArtifactDeserializer.from_bytes(payload)
    assert restored == artifact
    assert ExtractionArtifactSerializer.to_bytes(restored) == payload


def test_bytes_input_only():
    assert _code(bytearray(b"{}")) is (
        ExtractionArtifactIssueCode.INVALID_VALUE
    )


def test_invalid_utf8_and_bom_are_rejected():
    assert _code(b"\xff\n") is (
        ExtractionArtifactIssueCode.INVALID_UTF8
    )
    payload = ExtractionArtifactSerializer.to_bytes(_artifact())
    assert _code(b"\xef\xbb\xbf" + payload) is (
        ExtractionArtifactIssueCode.INVALID_UTF8
    )


def test_malformed_json_is_rejected():
    assert _code(b"{\n") is (
        ExtractionArtifactIssueCode.INVALID_JSON
    )


def test_duplicate_top_level_field_is_rejected():
    payload = ExtractionArtifactSerializer.to_bytes(_artifact())
    text = payload.decode("utf-8")
    duplicate = text.replace(
        '{"contract_version":',
        '{"contract_version":"duplicate","contract_version":',
        1,
    ).encode("utf-8")
    assert _code(duplicate) is (
        ExtractionArtifactIssueCode.DUPLICATE_FIELD
    )


def test_duplicate_nested_field_is_rejected():
    payload = ExtractionArtifactSerializer.to_bytes(_artifact())
    text = payload.decode("utf-8")
    duplicate = text.replace(
        '"structural_metadata":{"allowed":',
        '"structural_metadata":{"allowed":true,"allowed":',
        1,
    ).encode("utf-8")
    assert _code(duplicate) is (
        ExtractionArtifactIssueCode.DUPLICATE_FIELD
    )


def test_missing_field_is_rejected_before_canonical_check():
    parsed = json.loads(
        ExtractionArtifactSerializer.to_bytes(_artifact())
    )
    parsed.pop("job_id")
    payload = json.dumps(parsed).encode("utf-8")
    assert _code(payload) is (
        ExtractionArtifactIssueCode.MISSING_FIELD
    )


def test_extra_top_level_and_nested_fields_are_rejected():
    parsed = json.loads(
        ExtractionArtifactSerializer.to_bytes(_artifact())
    )
    parsed["extra"] = True
    assert _code(json.dumps(parsed).encode("utf-8")) is (
        ExtractionArtifactIssueCode.EXTRA_FIELD
    )
    parsed = json.loads(
        ExtractionArtifactSerializer.to_bytes(_artifact())
    )
    parsed["structural_metadata"]["extra"] = True
    assert _code(json.dumps(parsed).encode("utf-8")) is (
        ExtractionArtifactIssueCode.EXTRA_FIELD
    )


def test_unsupported_versions_are_rejected():
    parsed = json.loads(
        ExtractionArtifactSerializer.to_bytes(_artifact())
    )
    parsed["contract_version"] = "v2"
    assert _code(json.dumps(parsed).encode("utf-8")) is (
        ExtractionArtifactIssueCode.UNSUPPORTED_VERSION
    )


def test_invalid_scalar_and_collection_values_are_rejected():
    parsed = json.loads(
        ExtractionArtifactSerializer.to_bytes(_artifact())
    )
    parsed["cleanup_completed"] = False
    assert _code(json.dumps(parsed).encode("utf-8")) is (
        ExtractionArtifactIssueCode.INVALID_VALUE
    )
    parsed = json.loads(
        ExtractionArtifactSerializer.to_bytes(_artifact())
    )
    parsed["page_extractions"] = {}
    assert _code(json.dumps(parsed).encode("utf-8")) is (
        ExtractionArtifactIssueCode.INVALID_VALUE
    )


def test_artifact_id_mismatch_is_rejected():
    parsed = json.loads(
        ExtractionArtifactSerializer.to_bytes(_artifact())
    )
    parsed["artifact_id"] = "b" * 64
    payload = (
        json.dumps(
            parsed,
            ensure_ascii=False,
            separators=(",", ":"),
        ) + "\n"
    ).encode("utf-8")
    assert _code(payload) is (
        ExtractionArtifactIssueCode.ARTIFACT_ID_MISMATCH
    )


def test_semantically_valid_non_canonical_bytes_are_rejected():
    payload = ExtractionArtifactSerializer.to_bytes(_artifact())
    non_canonical = payload[:-1] + b" \n"
    assert _code(non_canonical) is (
        ExtractionArtifactIssueCode.NON_CANONICAL_BYTES
    )
