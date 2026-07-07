from dataclasses import dataclass


@dataclass(frozen=True)
class TextExtractionEvidence:
    source_path: str
    content: str
    size_bytes: int
