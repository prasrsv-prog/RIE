from dataclasses import dataclass
from typing import Any


ALLOWED_TOP_LEVEL_FIELDS = {
    "root",
    "total_pdf_assets",
    "total_page_extractions",
    "failed_pdf_assets",
    "page_extractions",
    "asset_errors",
}

ALLOWED_PAGE_EXTRACTION_FIELDS = {
    "source_path",
    "size_bytes",
    "page_number",
    "extraction_index",
    "extraction_method",
    "content",
    "warnings",
}

ALLOWED_ASSET_ERROR_FIELDS = {
    "source_path",
    "size_bytes",
    "error",
}

FORBIDDEN_RECORD_FIELDS = {
    "product_type",
    "product_category",
    "helmet_model",
    "variant",
    "summary",
    "persona",
    "USP",
    "visual_style",
    "prompt",
    "final_prompt",
    "confidence",
    "embedding",
    "graph",
    "knowledge",
    "analysis",
    "style",
    "tone",
    "creative_direction",
}


@dataclass(frozen=True)
class PdfTextExtractionArtifactInspection:
    total_pdf_assets: int
    total_page_extractions: int
    failed_pdf_assets: int
    empty_content_page_count: int
    page_warning_count: int
    asset_error_count: int
    invalid_page_extraction_record_count: int
    invalid_asset_error_record_count: int
    forbidden_field_count: int


def inspect_artifact(
    artifact: Any,
) -> PdfTextExtractionArtifactInspection:
    if not isinstance(artifact, dict):
        raise ValueError("PDF text extraction artifact must be an object.")

    if set(artifact) != ALLOWED_TOP_LEVEL_FIELDS:
        raise ValueError(
            "PDF text extraction artifact must contain exactly root, "
            "total_pdf_assets, total_page_extractions, failed_pdf_assets, "
            "page_extractions, and asset_errors."
        )

    _validate_top_level_fields(artifact)

    page_extractions = artifact["page_extractions"]
    asset_errors = artifact["asset_errors"]

    empty_content_page_count = 0
    page_warning_count = 0
    invalid_page_extraction_record_count = 0
    invalid_asset_error_record_count = 0
    forbidden_field_count = 0

    for page_extraction in page_extractions:
        if not isinstance(page_extraction, dict):
            invalid_page_extraction_record_count += 1
            continue

        content = page_extraction.get("content")

        if isinstance(content, str) and content == "":
            empty_content_page_count += 1

        warnings = page_extraction.get("warnings")

        if isinstance(warnings, list):
            page_warning_count += len(warnings)

        forbidden_field_count += _count_forbidden_fields(page_extraction)

        if not _is_valid_page_extraction(page_extraction):
            invalid_page_extraction_record_count += 1

    for asset_error in asset_errors:
        if not isinstance(asset_error, dict):
            invalid_asset_error_record_count += 1
            continue

        forbidden_field_count += _count_forbidden_fields(asset_error)

        if not _is_valid_asset_error(asset_error):
            invalid_asset_error_record_count += 1

    return PdfTextExtractionArtifactInspection(
        total_pdf_assets=artifact["total_pdf_assets"],
        total_page_extractions=artifact["total_page_extractions"],
        failed_pdf_assets=artifact["failed_pdf_assets"],
        empty_content_page_count=empty_content_page_count,
        page_warning_count=page_warning_count,
        asset_error_count=len(asset_errors),
        invalid_page_extraction_record_count=(
            invalid_page_extraction_record_count
        ),
        invalid_asset_error_record_count=(
            invalid_asset_error_record_count
        ),
        forbidden_field_count=forbidden_field_count,
    )


def _validate_top_level_fields(artifact: dict[str, Any]) -> None:
    if not isinstance(artifact["root"], str):
        raise ValueError("PDF text extraction artifact root must be a string.")

    for field in (
        "total_pdf_assets",
        "total_page_extractions",
        "failed_pdf_assets",
    ):
        if not _is_int_not_bool(artifact[field]):
            raise ValueError(
                f"PDF text extraction artifact {field} must be an integer."
            )

    if not isinstance(artifact["page_extractions"], list):
        raise ValueError(
            "PDF text extraction artifact page_extractions must be a list."
        )

    if not isinstance(artifact["asset_errors"], list):
        raise ValueError(
            "PDF text extraction artifact asset_errors must be a list."
        )


def _is_valid_page_extraction(record: dict[str, Any]) -> bool:
    if set(record) != ALLOWED_PAGE_EXTRACTION_FIELDS:
        return False

    if not isinstance(record["source_path"], str):
        return False

    if not _is_int_not_bool(record["size_bytes"]):
        return False

    if not _is_int_not_bool(record["page_number"]):
        return False

    if not _is_int_not_bool(record["extraction_index"]):
        return False

    if not isinstance(record["extraction_method"], str):
        return False

    if not isinstance(record["content"], str):
        return False

    warnings = record["warnings"]

    if not isinstance(warnings, list):
        return False

    return all(isinstance(warning, str) for warning in warnings)


def _is_valid_asset_error(record: dict[str, Any]) -> bool:
    if set(record) != ALLOWED_ASSET_ERROR_FIELDS:
        return False

    if not isinstance(record["source_path"], str):
        return False

    if not _is_int_not_bool(record["size_bytes"]):
        return False

    return isinstance(record["error"], str)


def _count_forbidden_fields(record: dict[str, Any]) -> int:
    return sum(
        field in FORBIDDEN_RECORD_FIELDS
        for field in record
    )


def _is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
