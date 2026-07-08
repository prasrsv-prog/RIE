from dataclasses import dataclass


@dataclass(frozen=True)
class PdfPageTextExtraction:
    source_path: str
    size_bytes: int
    page_number: int
    extraction_index: int
    extraction_method: str
    content: str
    warnings: list[str]
