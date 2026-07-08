from dataclasses import dataclass
from typing import Any


ALLOWED_TOP_LEVEL_FIELDS = {
    "pdf_text_evidences",
}

ALLOWED_RECORD_FIELDS = {
    "source_path",
    "content",
    "size_bytes",
    "page_number",
    "extraction_index",
    "extraction_method",
    "warnings",
    "evidence_index",
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
class PdfTextExtractionEvidenceArtifactInspection:
    total_pdf_text_evidences: int
    total_content_characters: int
    empty_content_evidence_count: int
    warning_count: int
    invalid_record_count: int
    forbidden_field_count: int


def inspect_artifact(
    artifact: Any,
) -> PdfTextExtractionEvidenceArtifactInspection:
    if not isinstance(artifact, dict):
        raise ValueError("PDF text evidence artifact must be an object.")

    if set(artifact) != ALLOWED_TOP_LEVEL_FIELDS:
        raise ValueError(
            "PDF text evidence artifact must contain exactly "
            "pdf_text_evidences."
        )

    pdf_text_evidences = artifact["pdf_text_evidences"]

    if not isinstance(pdf_text_evidences, list):
        raise ValueError(
            "PDF text evidence artifact pdf_text_evidences must be a list."
        )

    total_content_characters = 0
    empty_content_evidence_count = 0
    warning_count = 0
    invalid_record_count = 0
    forbidden_field_count = 0

    for evidence in pdf_text_evidences:
        if not isinstance(evidence, dict):
            invalid_record_count += 1
            continue

        content = evidence.get("content")

        if isinstance(content, str):
            total_content_characters += len(content)

            if content == "":
                empty_content_evidence_count += 1

        warnings = evidence.get("warnings")

        if isinstance(warnings, list):
            warning_count += len(warnings)

        forbidden_field_count += _count_forbidden_fields(evidence)

        if not _is_valid_pdf_text_evidence(evidence):
            invalid_record_count += 1

    return PdfTextExtractionEvidenceArtifactInspection(
        total_pdf_text_evidences=len(pdf_text_evidences),
        total_content_characters=total_content_characters,
        empty_content_evidence_count=empty_content_evidence_count,
        warning_count=warning_count,
        invalid_record_count=invalid_record_count,
        forbidden_field_count=forbidden_field_count,
    )


def _is_valid_pdf_text_evidence(record: dict[str, Any]) -> bool:
    if set(record) != ALLOWED_RECORD_FIELDS:
        return False

    if not isinstance(record["source_path"], str):
        return False

    if not isinstance(record["content"], str):
        return False

    if not _is_int_not_bool(record["size_bytes"]):
        return False

    if not _is_int_not_bool(record["page_number"]):
        return False

    if not _is_int_not_bool(record["extraction_index"]):
        return False

    if not isinstance(record["extraction_method"], str):
        return False

    warnings = record["warnings"]

    if not isinstance(warnings, list):
        return False

    if not all(isinstance(warning, str) for warning in warnings):
        return False

    return _is_int_not_bool(record["evidence_index"])


def _count_forbidden_fields(record: dict[str, Any]) -> int:
    return sum(
        field in FORBIDDEN_RECORD_FIELDS
        for field in record
    )


def _is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
