from dataclasses import dataclass


@dataclass(frozen=True)
class PdfTextExtractionEvidence:
    source_path: str
    content: str
    size_bytes: int
    page_number: int
    extraction_index: int
    extraction_method: str
    warnings: list[str]
    evidence_index: int
