from pathlib import Path
from typing import Any

from rie.extraction.text_asset_extraction import TextAssetExtraction
from rie.extraction.text_asset_extraction_report import TextAssetExtractionReport


class TextAssetExtractor:

    def extract(
        self,
        data: dict[str, Any],
    ) -> TextAssetExtractionReport:
        extractions = [
            self._extract_item(item)
            for item in data["items"]
            if item["asset_type"] == "UTF8_TEXT"
        ]

        return TextAssetExtractionReport(
            root=data["root"],
            total_text_assets=len(extractions),
            extractions=extractions,
        )

    def _extract_item(
        self,
        item: dict[str, Any],
    ) -> TextAssetExtraction:
        path = Path(item["path"])
        size = item["size"]

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as exc:
            return TextAssetExtraction(
                path=path,
                size=size,
                content="",
                error=str(exc),
            )

        return TextAssetExtraction(
            path=path,
            size=size,
            content=content,
        )
