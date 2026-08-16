
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

def _d34_zero_page_artifact(*, contract_version: str, provenance: object):
    from dataclasses import replace
    import rie.extraction.extraction_artifact_contract as contract
    from rie.extraction.extraction_artifact_serializer import (
        ExtractionArtifactSerializer,
    )

    source_path = "controlled/d34.pdf"
    metadata = contract.ExtractionArtifactStructuralMetadata(
        allowed=True,
        reason="Controlled source is allowed.",
        fixture_id="d34-fixture",
        source_label="D34 synthetic source",
        fixture_path=source_path,
        fixture_type="pdf",
        inspection_mode="bounded",
        inspection_status="inspected",
        encrypted=False,
        page_count=0,
        inspected_page_count=0,
        page_details_truncated=False,
        page_details=(),
        max_inspected_pages=10,
        inspection_error="",
        evidence_allowed=False,
        notes="D34 synthetic artifact.",
    )
    provisional = contract.ExtractionArtifact(
        contract_version=contract_version,
        artifact_id="0" * 64,
        upstream_contract_version=(
            contract.EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION
        ),
        upstream_status="completed",
        job_id="d34-job",
        source_id="d34-source",
        source_path=source_path,
        source_checksum="c" * 64,
        structural_metadata=metadata,
        page_extractions=(),
        execution_report_location="memory://d34-report",
        cleanup_completed=True,
        ocr_remediation_provenance=provenance,
    )
    return replace(
        provisional,
        artifact_id=ExtractionArtifactSerializer.derive_artifact_id(
            provisional
        ),
    )


def _d34_gate5_provenance():
    import rie.extraction.extraction_artifact_contract as contract
    return contract.ExtractionArtifactOcrRemediationProvenance(
        producer_operation_id="PR_086K_D27_REAL_RSV_ASSET_PILOT_BOUNDED_PDF_IMAGE_TEXT_EXTRACTION_EXECUTION",
        producer_artifact_path="memory://ocr-index",
        producer_artifact_sha256="a" * 64,
        producer_artifact_set_digest="b" * 64,
        extraction_method="bounded_local_ocr",
    )

def test_d34_deserializer_dual_version_and_field_presence_rules() -> None:
    import json
    import pytest
    import rie.extraction.extraction_artifact_contract as contract
    from rie.extraction.extraction_artifact_deserializer import (
        ExtractionArtifactDeserializer,
    )
    from rie.extraction.extraction_artifact_serializer import (
        ExtractionArtifactSerializer,
    )

    remediated = _d34_zero_page_artifact(
        contract_version=contract.EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION,
        provenance=_d34_gate5_provenance(),
    )
    encoded = ExtractionArtifactSerializer.to_bytes(remediated)
    decoded = ExtractionArtifactDeserializer.from_bytes(encoded)
    assert decoded == remediated
    assert decoded.ocr_remediation_provenance == (
        remediated.ocr_remediation_provenance
    )

    legacy = _d34_zero_page_artifact(
        contract_version=contract.EXTRACTION_ARTIFACT_CONTRACT_VERSION,
        provenance=None,
    )
    legacy_raw = json.loads(ExtractionArtifactSerializer.to_bytes(legacy))
    legacy_raw["ocr_remediation_provenance"] = {
        "producer_operation_id": "producer",
        "producer_artifact_path": "artifact",
        "producer_artifact_sha256": "a" * 64,
        "producer_artifact_set_digest": "b" * 64,
        "extraction_method": "bounded_local_ocr",
    }
    legacy_extra = (
        json.dumps(
            legacy_raw,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    with pytest.raises(contract.ExtractionArtifactContractError):
        ExtractionArtifactDeserializer.from_bytes(legacy_extra)

    v2_missing = json.loads(encoded)
    del v2_missing["ocr_remediation_provenance"]
    v2_missing_bytes = (
        json.dumps(
            v2_missing,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    with pytest.raises(contract.ExtractionArtifactContractError):
        ExtractionArtifactDeserializer.from_bytes(v2_missing_bytes)
