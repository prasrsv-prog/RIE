from collection.text_extraction_evidence_collection import (
    TextExtractionEvidenceCollection,
)
from evidence.text_extraction_evidence_builder import (
    TextExtractionEvidenceBuilder,
)
from rie.extraction.text_asset_extraction_report import TextAssetExtractionReport


class TextExtractionEvidenceCollector:

    @staticmethod
    def collect(
        report: TextAssetExtractionReport,
    ) -> TextExtractionEvidenceCollection:
        evidences = [
            TextExtractionEvidenceBuilder.build(extraction)
            for extraction in report.extractions
            if extraction.error is None
        ]

        return TextExtractionEvidenceCollection(
            evidences=evidences,
        )
