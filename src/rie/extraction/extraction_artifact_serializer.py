"""Canonical in-memory serializer for Gate 5 Extraction Artifacts."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_FIELD_ORDER,
    EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER,
    EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER,
    EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER,
    EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER,
    ExtractionArtifact,
    ExtractionArtifactIssueCode,
    ExtractionArtifactPageExtraction,
    ExtractionArtifactStructuralMetadata,
    ExtractionArtifactStructuralPage,
    raise_artifact_error,
)

from rie.extraction import extraction_artifact_contract as _artifact_contract


class ExtractionArtifactSerializer:
    @staticmethod
    def to_dict(artifact: ExtractionArtifact) -> dict[str, Any]:
        _require_artifact(artifact)
        payload = {
            "contract_version": artifact.contract_version,
            "artifact_id": artifact.artifact_id,
            "upstream_contract_version":
                artifact.upstream_contract_version,
            "upstream_status": artifact.upstream_status,
            "job_id": artifact.job_id,
            "source_id": artifact.source_id,
            "source_path": artifact.source_path,
            "source_checksum": artifact.source_checksum,
            "structural_metadata": _structural_metadata_to_dict(
                artifact.structural_metadata
            ),
            "page_extractions": [
                _page_extraction_to_dict(item)
                for item in artifact.page_extractions
            ],
            "execution_report_location":
                artifact.execution_report_location,
            "cleanup_completed": artifact.cleanup_completed,
        }
        if (
            artifact.contract_version
            == _artifact_contract.EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION
        ):
            payload["ocr_remediation_provenance"] = (
                _ocr_remediation_provenance_to_dict(
                    artifact.ocr_remediation_provenance
                )
            )
            expected_order = _artifact_contract.EXTRACTION_ARTIFACT_OCR_FIELD_ORDER
        else:
            expected_order = EXTRACTION_ARTIFACT_FIELD_ORDER
        if tuple(payload) != expected_order:
            raise RuntimeError("artifact field order is invalid.")
        return payload

    @staticmethod
    def identity_dict(
        artifact: ExtractionArtifact,
    ) -> dict[str, Any]:
        _require_artifact(artifact)
        payload = {
            "contract_version": artifact.contract_version,
            "upstream_contract_version":
                artifact.upstream_contract_version,
            "upstream_status": artifact.upstream_status,
            "job_id": artifact.job_id,
            "source_id": artifact.source_id,
            "source_path": artifact.source_path,
            "source_checksum": artifact.source_checksum,
            "structural_metadata": _structural_metadata_to_dict(
                artifact.structural_metadata
            ),
            "page_extractions": [
                _page_extraction_to_dict(item)
                for item in artifact.page_extractions
            ],
            "execution_report_location":
                artifact.execution_report_location,
            "cleanup_completed": artifact.cleanup_completed,
        }
        if (
            artifact.contract_version
            == _artifact_contract.EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION
        ):
            payload["ocr_remediation_provenance"] = (
                _ocr_remediation_provenance_to_dict(
                    artifact.ocr_remediation_provenance
                )
            )
            expected_order = (
                _artifact_contract.EXTRACTION_ARTIFACT_OCR_IDENTITY_FIELD_ORDER
            )
        else:
            expected_order = EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER
        if tuple(payload) != expected_order:
            raise RuntimeError(
                "artifact identity field order is invalid."
            )
        return payload

    @staticmethod
    def identity_bytes(artifact: ExtractionArtifact) -> bytes:
        return _canonical_json_bytes(
            ExtractionArtifactSerializer.identity_dict(artifact)
        )

    @staticmethod
    def derive_artifact_id(
        artifact: ExtractionArtifact,
    ) -> str:
        return hashlib.sha256(
            ExtractionArtifactSerializer.identity_bytes(artifact)
        ).hexdigest()

    @staticmethod
    def to_bytes(artifact: ExtractionArtifact) -> bytes:
        expected_id = (
            ExtractionArtifactSerializer.derive_artifact_id(artifact)
        )
        if artifact.artifact_id != expected_id:
            raise_artifact_error(
                ExtractionArtifactIssueCode.ARTIFACT_ID_MISMATCH
            )
        return _canonical_json_bytes(
            ExtractionArtifactSerializer.to_dict(artifact)
        )



def _ocr_remediation_provenance_to_dict(value: object) -> dict[str, Any]:
    expected_type = _artifact_contract.ExtractionArtifactOcrRemediationProvenance
    if type(value) is not expected_type:
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    payload = {
        "producer_operation_id": value.producer_operation_id,
        "producer_artifact_path": value.producer_artifact_path,
        "producer_artifact_sha256": value.producer_artifact_sha256,
        "producer_artifact_set_digest": value.producer_artifact_set_digest,
        "extraction_method": value.extraction_method,
    }
    if (
        tuple(payload)
        != _artifact_contract.EXTRACTION_ARTIFACT_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER
    ):
        raise RuntimeError(
            "OCR remediation provenance field order is invalid."
        )
    return payload


def _canonical_json_bytes(value: object) -> bytes:
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    result = (text + "\n").encode("utf-8")
    if (
        result.startswith(b"\xef\xbb\xbf")
        or b"\r" in result
        or not result.endswith(b"\n")
        or result.endswith(b"\n\n")
    ):
        raise RuntimeError("canonical byte encoding is invalid.")
    return result


def _structural_page_to_dict(
    page: ExtractionArtifactStructuralPage,
) -> dict[str, Any]:
    if not isinstance(page, ExtractionArtifactStructuralPage):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    payload = {
        "page_index": page.page_index,
        "width_points": page.width_points,
        "height_points": page.height_points,
        "rotation_degrees": page.rotation_degrees,
        "inspection_status": page.inspection_status,
    }
    if tuple(payload) != EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER:
        raise RuntimeError("structural page field order is invalid.")
    return payload


def _structural_metadata_to_dict(
    metadata: ExtractionArtifactStructuralMetadata,
) -> dict[str, Any]:
    if not isinstance(
        metadata,
        ExtractionArtifactStructuralMetadata,
    ):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    payload = {
        "allowed": metadata.allowed,
        "reason": metadata.reason,
        "fixture_id": metadata.fixture_id,
        "source_label": metadata.source_label,
        "fixture_path": metadata.fixture_path,
        "fixture_type": metadata.fixture_type,
        "inspection_mode": metadata.inspection_mode,
        "inspection_status": metadata.inspection_status,
        "encrypted": metadata.encrypted,
        "page_count": metadata.page_count,
        "inspected_page_count": metadata.inspected_page_count,
        "page_details_truncated":
            metadata.page_details_truncated,
        "page_details": [
            _structural_page_to_dict(page)
            for page in metadata.page_details
        ],
        "max_inspected_pages": metadata.max_inspected_pages,
        "inspection_error": metadata.inspection_error,
        "evidence_allowed": metadata.evidence_allowed,
        "notes": metadata.notes,
    }
    if (
        tuple(payload)
        != EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER
    ):
        raise RuntimeError(
            "structural metadata field order is invalid."
        )
    return payload


def _page_extraction_to_dict(
    extraction: ExtractionArtifactPageExtraction,
) -> dict[str, Any]:
    if not isinstance(
        extraction,
        ExtractionArtifactPageExtraction,
    ):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    payload = {
        "source_path": extraction.source_path,
        "size_bytes": extraction.size_bytes,
        "page_number": extraction.page_number,
        "extraction_index": extraction.extraction_index,
        "extraction_method": extraction.extraction_method,
        "content": extraction.content,
        "warnings": list(extraction.warnings),
    }
    if (
        tuple(payload)
        != EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER
    ):
        raise RuntimeError(
            "page extraction field order is invalid."
        )
    return payload


def _require_artifact(value: object) -> None:
    if not isinstance(value, ExtractionArtifact):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )


__all__ = ("ExtractionArtifactSerializer",)
