from dataclasses import dataclass

from evidence.text_extraction_evidence import TextExtractionEvidence


@dataclass(frozen=True)
class TextExtractionEvidenceCollection:
    evidences: list[TextExtractionEvidence]
