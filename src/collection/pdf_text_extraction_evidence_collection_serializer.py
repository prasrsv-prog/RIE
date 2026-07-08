import json
from typing import Any

from collection.pdf_text_extraction_evidence_collection import (
    PdfTextExtractionEvidenceCollection,
)


class PdfTextExtractionEvidenceCollectionSerializer:

    @staticmethod
    def to_dict(
        collection: PdfTextExtractionEvidenceCollection,
    ) -> dict[str, Any]:
        return {
            "pdf_text_evidences": [
                {
                    "source_path": evidence.source_path,
                    "content": evidence.content,
                    "size_bytes": evidence.size_bytes,
                    "page_number": evidence.page_number,
                    "extraction_index": evidence.extraction_index,
                    "extraction_method": evidence.extraction_method,
                    "warnings": evidence.warnings,
                    "evidence_index": evidence.evidence_index,
                }
                for evidence in collection.evidences
            ],
        }

    @staticmethod
    def to_json(
        collection: PdfTextExtractionEvidenceCollection,
    ) -> str:
        return json.dumps(
            PdfTextExtractionEvidenceCollectionSerializer.to_dict(collection),
            indent=2,
            ensure_ascii=False,
        )
