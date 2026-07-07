from dataclasses import dataclass

from rie.extraction.text_asset_extraction import TextAssetExtraction


@dataclass(frozen=True)
class TextAssetExtractionReport:
    root: str
    total_text_assets: int
    extractions: list[TextAssetExtraction]

    @property
    def failed(self) -> int:
        return sum(
            extraction.error is not None
            for extraction in self.extractions
        )
