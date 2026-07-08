from dataclasses import dataclass

from evidence.pdf_text_extraction_evidence import PdfTextExtractionEvidence


@dataclass(frozen=True)
class PdfTextExtractionEvidenceCollection:
    evidences: list[PdfTextExtractionEvidence]
