from rie.extraction.text_asset_extraction import TextAssetExtraction

from evidence.text_extraction_evidence import TextExtractionEvidence


class TextExtractionEvidenceBuilder:

    @staticmethod
    def build(
        extraction: TextAssetExtraction,
    ) -> TextExtractionEvidence:
        if extraction.error is not None:
            raise ValueError(
                "Failed text extraction cannot become evidence."
            )

        return TextExtractionEvidence(
            source_path=str(extraction.path),
            content=extraction.content,
            size_bytes=extraction.size,
        )
