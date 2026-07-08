from typing import Any

from collection.pdf_text_extraction_evidence_collection import (
    PdfTextExtractionEvidenceCollection,
)
from evidence.pdf_text_extraction_evidence_builder import (
    PdfTextExtractionEvidenceBuilder,
)


class PdfTextExtractionEvidenceCollector:

    @staticmethod
    def collect(
        artifact: Any,
    ) -> PdfTextExtractionEvidenceCollection:
        if not isinstance(artifact, dict):
            raise ValueError("PDF text extraction artifact must be an object.")

        page_extractions = artifact.get("page_extractions")

        if not isinstance(page_extractions, list):
            raise ValueError(
                "PDF text extraction artifact page_extractions must be "
                "a list."
            )

        evidences = []

        for page_extraction_record in page_extractions:
            try:
                evidences.append(
                    PdfTextExtractionEvidenceBuilder.build(
                        page_extraction_record=page_extraction_record,
                        evidence_index=len(evidences),
                    )
                )
            except ValueError:
                continue

        return PdfTextExtractionEvidenceCollection(
            evidences=evidences,
        )
