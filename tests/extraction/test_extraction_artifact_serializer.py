
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


from dataclasses import replace
import json
from math import nan

import pytest

from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_FIELD_ORDER,
    EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER,
    EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER,
    EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER,
    EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER,
    ExtractionArtifactContractError,
    ExtractionArtifactIssueCode,
)
from rie.extraction.extraction_artifact_serializer import (
    ExtractionArtifactSerializer,
)


def test_to_dict_preserves_exact_top_level_and_nested_orders():
    payload = ExtractionArtifactSerializer.to_dict(_artifact())
    assert tuple(payload) == EXTRACTION_ARTIFACT_FIELD_ORDER
    assert tuple(payload["structural_metadata"]) == (
        EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER
    )
    assert tuple(
        payload["structural_metadata"]["page_details"][0]
    ) == EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER
    assert tuple(payload["page_extractions"][0]) == (
        EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER
    )


def test_identity_payload_excludes_artifact_id_and_has_exact_order():
    artifact = _artifact()
    payload = ExtractionArtifactSerializer.identity_dict(artifact)
    assert tuple(payload) == EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER
    assert "artifact_id" not in payload


def test_identity_is_deterministic_and_changes_with_value():
    artifact = _artifact()
    first = ExtractionArtifactSerializer.derive_artifact_id(artifact)
    second = ExtractionArtifactSerializer.derive_artifact_id(artifact)
    assert first == second == artifact.artifact_id
    changed = replace(
        artifact.page_extractions[0],
        content="changed",
    )
    provisional = replace(
        artifact,
        artifact_id="0" * 64,
        page_extractions=(changed, artifact.page_extractions[1]),
    )
    assert (
        ExtractionArtifactSerializer.derive_artifact_id(provisional)
        != artifact.artifact_id
    )


def test_to_bytes_is_compact_utf8_lf_only_and_deterministic():
    first = ExtractionArtifactSerializer.to_bytes(_artifact())
    second = ExtractionArtifactSerializer.to_bytes(_artifact())
    assert first == second
    assert first.endswith(b"\n")
    assert not first.endswith(b"\n\n")
    assert b"\r" not in first
    assert not first.startswith(b"\xef\xbb\xbf")
    assert b": " not in first
    assert b", " not in first


def test_unicode_empty_text_and_warning_order_are_preserved():
    artifact = _artifact(unicode_text=True)
    payload = ExtractionArtifactSerializer.to_bytes(artifact)
    assert "halaman é".encode("utf-8") in payload
    assert "warning α".encode("utf-8") in payload
    assert b"\\u00e9" not in payload
    parsed = json.loads(payload)
    assert parsed["page_extractions"][0]["content"] == "halaman é"
    assert parsed["page_extractions"][0]["warnings"] == ["warning α"]


def test_serializer_rejects_artifact_id_mismatch():
    artifact = replace(_artifact(), artifact_id="b" * 64)
    with pytest.raises(ExtractionArtifactContractError) as caught:
        ExtractionArtifactSerializer.to_bytes(artifact)
    assert caught.value.issue.code is (
        ExtractionArtifactIssueCode.ARTIFACT_ID_MISMATCH
    )


def test_serializer_rejects_non_finite_numeric_value():
    artifact = _artifact()
    object.__setattr__(
        artifact.structural_metadata.page_details[0],
        "width_points",
        nan,
    )
    with pytest.raises(ExtractionArtifactContractError) as caught:
        ExtractionArtifactSerializer.to_bytes(artifact)
    assert caught.value.issue.code is (
        ExtractionArtifactIssueCode.INVALID_VALUE
    )


def test_serializer_is_in_memory_only():
    assert not hasattr(ExtractionArtifactSerializer, "write")
    assert not hasattr(ExtractionArtifactSerializer, "read")

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

def test_d34_v1_bytes_omit_ocr_field_and_v2_bytes_include_it() -> None:
    import json
    import rie.extraction.extraction_artifact_contract as contract
    from rie.extraction.extraction_artifact_serializer import (
        ExtractionArtifactSerializer,
    )

    legacy = _d34_zero_page_artifact(
        contract_version=contract.EXTRACTION_ARTIFACT_CONTRACT_VERSION,
        provenance=None,
    )
    legacy_bytes = ExtractionArtifactSerializer.to_bytes(legacy)
    assert b'"ocr_remediation_provenance"' not in legacy_bytes
    assert tuple(json.loads(legacy_bytes).keys()) == (
        contract.EXTRACTION_ARTIFACT_FIELD_ORDER
    )

    remediated = _d34_zero_page_artifact(
        contract_version=contract.EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION,
        provenance=_d34_gate5_provenance(),
    )
    first = ExtractionArtifactSerializer.to_bytes(remediated)
    second = ExtractionArtifactSerializer.to_bytes(remediated)
    assert first == second
    assert b'"ocr_remediation_provenance"' in first
    assert tuple(json.loads(first).keys()) == (
        contract.EXTRACTION_ARTIFACT_OCR_FIELD_ORDER
    )
