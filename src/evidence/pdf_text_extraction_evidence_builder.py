from typing import Any

from evidence.pdf_text_extraction_evidence import PdfTextExtractionEvidence


REQUIRED_PAGE_EXTRACTION_FIELDS = {
    "source_path",
    "size_bytes",
    "page_number",
    "extraction_index",
    "extraction_method",
    "content",
    "warnings",
}


class PdfTextExtractionEvidenceBuilder:

    @staticmethod
    def build(
        page_extraction_record: Any,
        evidence_index: int,
    ) -> PdfTextExtractionEvidence:
        if not isinstance(page_extraction_record, dict):
            raise ValueError("PDF page extraction record must be an object.")

        if set(page_extraction_record) != REQUIRED_PAGE_EXTRACTION_FIELDS:
            raise ValueError(
                "PDF page extraction record must contain exactly "
                "source_path, size_bytes, page_number, extraction_index, "
                "extraction_method, content, and warnings."
            )

        source_path = page_extraction_record["source_path"]
        content = page_extraction_record["content"]
        size_bytes = page_extraction_record["size_bytes"]
        page_number = page_extraction_record["page_number"]
        extraction_index = page_extraction_record["extraction_index"]
        extraction_method = page_extraction_record["extraction_method"]
        warnings = page_extraction_record["warnings"]

        if not isinstance(source_path, str):
            raise ValueError(
                "PDF page extraction record source_path must be a string."
            )

        if not isinstance(content, str):
            raise ValueError(
                "PDF page extraction record content must be a string."
            )

        if not _is_int_not_bool(size_bytes):
            raise ValueError(
                "PDF page extraction record size_bytes must be an integer."
            )

        if not _is_int_not_bool(page_number):
            raise ValueError(
                "PDF page extraction record page_number must be an integer."
            )

        if not _is_int_not_bool(extraction_index):
            raise ValueError(
                "PDF page extraction record extraction_index must be "
                "an integer."
            )

        if not isinstance(extraction_method, str):
            raise ValueError(
                "PDF page extraction record extraction_method must be "
                "a string."
            )

        if not isinstance(warnings, list):
            raise ValueError(
                "PDF page extraction record warnings must be a list."
            )

        if not all(isinstance(warning, str) for warning in warnings):
            raise ValueError(
                "PDF page extraction record warnings must contain strings."
            )

        if not _is_int_not_bool(evidence_index):
            raise ValueError("Evidence index must be an integer.")

        return PdfTextExtractionEvidence(
            source_path=source_path,
            content=content,
            size_bytes=size_bytes,
            page_number=page_number,
            extraction_index=extraction_index,
            extraction_method=extraction_method,
            warnings=list(warnings),
            evidence_index=evidence_index,
        )


def _is_int_not_bool(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
