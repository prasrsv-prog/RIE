"""Strict canonical parser for Gate 5 Extraction Artifact bytes."""

from __future__ import annotations

import json
from typing import Any

from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_CONTRACT_VERSION,
    EXTRACTION_ARTIFACT_FIELD_ORDER,
    EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER,
    EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER,
    EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER,
    EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION,
    ExtractionArtifact,
    ExtractionArtifactContractError,
    ExtractionArtifactIssueCode,
    ExtractionArtifactPageExtraction,
    ExtractionArtifactStructuralMetadata,
    ExtractionArtifactStructuralPage,
    raise_artifact_error,
)
from rie.extraction.extraction_artifact_serializer import (
    ExtractionArtifactSerializer,
)

from rie.extraction import extraction_artifact_contract as _artifact_contract


class _DuplicateFieldError(ValueError):
    pass


class ExtractionArtifactDeserializer:
    @staticmethod
    def from_bytes(data: bytes) -> ExtractionArtifact:
        if type(data) is not bytes:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if data.startswith(b"\xef\xbb\xbf"):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_UTF8
            )
        try:
            text = data.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_UTF8
            )

        try:
            raw = json.loads(
                text,
                object_pairs_hook=_unique_object,
                parse_constant=_reject_constant,
            )
        except _DuplicateFieldError:
            raise_artifact_error(
                ExtractionArtifactIssueCode.DUPLICATE_FIELD
            )
        except (json.JSONDecodeError, ValueError):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_JSON
            )

        artifact = _artifact_from_raw(raw)

        expected_id = (
            ExtractionArtifactSerializer.derive_artifact_id(artifact)
        )
        if artifact.artifact_id != expected_id:
            raise_artifact_error(
                ExtractionArtifactIssueCode.ARTIFACT_ID_MISMATCH
            )

        canonical = ExtractionArtifactSerializer.to_bytes(artifact)
        if canonical != data:
            raise_artifact_error(
                ExtractionArtifactIssueCode.NON_CANONICAL_BYTES
            )
        return artifact



def _ocr_remediation_provenance_from_raw(
    raw: object,
) -> _artifact_contract.ExtractionArtifactOcrRemediationProvenance:
    mapping = _require_mapping(raw)
    _validate_fields(
        mapping,
        _artifact_contract.EXTRACTION_ARTIFACT_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER,
    )
    try:
        return _artifact_contract.ExtractionArtifactOcrRemediationProvenance(
            producer_operation_id=mapping["producer_operation_id"],
            producer_artifact_path=mapping["producer_artifact_path"],
            producer_artifact_sha256=mapping["producer_artifact_sha256"],
            producer_artifact_set_digest=(
                mapping["producer_artifact_set_digest"]
            ),
            extraction_method=mapping["extraction_method"],
        )
    except ExtractionArtifactContractError:
        raise
    except (TypeError, ValueError):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )



def _artifact_from_raw(raw: object) -> ExtractionArtifact:
    mapping = _require_mapping(raw)
    contract_version = mapping.get("contract_version")

    if contract_version == EXTRACTION_ARTIFACT_CONTRACT_VERSION:
        _validate_fields(mapping, EXTRACTION_ARTIFACT_FIELD_ORDER)
        ocr_remediation_provenance = None
    elif (
        contract_version
        == _artifact_contract.EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION
    ):
        _validate_fields(
            mapping,
            _artifact_contract.EXTRACTION_ARTIFACT_OCR_FIELD_ORDER,
        )
        ocr_remediation_provenance = (
            _ocr_remediation_provenance_from_raw(
                mapping["ocr_remediation_provenance"]
            )
        )
    else:
        raise_artifact_error(
            ExtractionArtifactIssueCode.UNSUPPORTED_VERSION
        )

    if (
        mapping["upstream_contract_version"]
        != EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION
    ):
        raise_artifact_error(
            ExtractionArtifactIssueCode.UNSUPPORTED_VERSION
        )

    structural = _structural_metadata_from_raw(
        mapping["structural_metadata"]
    )
    page_values = _require_list(mapping["page_extractions"])
    pages = tuple(
        _page_extraction_from_raw(value)
        for value in page_values
    )

    try:
        return ExtractionArtifact(
            contract_version=mapping["contract_version"],
            artifact_id=mapping["artifact_id"],
            upstream_contract_version=(
                mapping["upstream_contract_version"]
            ),
            upstream_status=mapping["upstream_status"],
            job_id=mapping["job_id"],
            source_id=mapping["source_id"],
            source_path=mapping["source_path"],
            source_checksum=mapping["source_checksum"],
            structural_metadata=structural,
            page_extractions=pages,
            execution_report_location=(
                mapping["execution_report_location"]
            ),
            cleanup_completed=mapping["cleanup_completed"],
            ocr_remediation_provenance=ocr_remediation_provenance,
        )
    except ExtractionArtifactContractError:
        raise
    except (TypeError, ValueError):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )


def _structural_page_from_raw(
    raw: object,
) -> ExtractionArtifactStructuralPage:
    mapping = _require_mapping(raw)
    _validate_fields(
        mapping,
        EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER,
    )
    try:
        return ExtractionArtifactStructuralPage(
            page_index=mapping["page_index"],
            width_points=mapping["width_points"],
            height_points=mapping["height_points"],
            rotation_degrees=mapping["rotation_degrees"],
            inspection_status=mapping["inspection_status"],
        )
    except ExtractionArtifactContractError:
        raise
    except (TypeError, ValueError):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )


def _structural_metadata_from_raw(
    raw: object,
) -> ExtractionArtifactStructuralMetadata:
    mapping = _require_mapping(raw)
    _validate_fields(
        mapping,
        EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER,
    )
    page_values = _require_list(mapping["page_details"])
    pages = tuple(
        _structural_page_from_raw(value)
        for value in page_values
    )
    try:
        return ExtractionArtifactStructuralMetadata(
            allowed=mapping["allowed"],
            reason=mapping["reason"],
            fixture_id=mapping["fixture_id"],
            source_label=mapping["source_label"],
            fixture_path=mapping["fixture_path"],
            fixture_type=mapping["fixture_type"],
            inspection_mode=mapping["inspection_mode"],
            inspection_status=mapping["inspection_status"],
            encrypted=mapping["encrypted"],
            page_count=mapping["page_count"],
            inspected_page_count=mapping["inspected_page_count"],
            page_details_truncated=(
                mapping["page_details_truncated"]
            ),
            page_details=pages,
            max_inspected_pages=mapping["max_inspected_pages"],
            inspection_error=mapping["inspection_error"],
            evidence_allowed=mapping["evidence_allowed"],
            notes=mapping["notes"],
        )
    except ExtractionArtifactContractError:
        raise
    except (TypeError, ValueError):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )


def _page_extraction_from_raw(
    raw: object,
) -> ExtractionArtifactPageExtraction:
    mapping = _require_mapping(raw)
    _validate_fields(
        mapping,
        EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER,
    )
    warning_values = _require_list(mapping["warnings"])
    try:
        return ExtractionArtifactPageExtraction(
            source_path=mapping["source_path"],
            size_bytes=mapping["size_bytes"],
            page_number=mapping["page_number"],
            extraction_index=mapping["extraction_index"],
            extraction_method=mapping["extraction_method"],
            content=mapping["content"],
            warnings=tuple(warning_values),
        )
    except ExtractionArtifactContractError:
        raise
    except (TypeError, ValueError):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )


def _unique_object(
    pairs: list[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateFieldError(key)
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(value)


def _require_mapping(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    return value


def _require_list(value: object) -> list[Any]:
    if not isinstance(value, list):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    return value


def _validate_fields(
    mapping: dict[str, Any],
    field_order: tuple[str, ...],
) -> None:
    missing = tuple(
        field for field in field_order if field not in mapping
    )
    if missing:
        raise_artifact_error(
            ExtractionArtifactIssueCode.MISSING_FIELD
        )
    extra = tuple(
        field for field in mapping if field not in field_order
    )
    if extra:
        raise_artifact_error(
            ExtractionArtifactIssueCode.EXTRA_FIELD
        )


__all__ = ("ExtractionArtifactDeserializer",)
