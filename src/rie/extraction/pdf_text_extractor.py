from pathlib import Path
from typing import Any, Callable

from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction
from rie.extraction.pdf_text_extraction_report import (
    PdfTextExtractionAssetError,
)
from rie.extraction.pdf_text_extraction_report import PdfTextExtractionReport


EMBEDDED_TEXT_EXTRACTION_METHOD = "embedded_text"
NO_EMBEDDED_TEXT_WARNING = "No embedded text found."


class PdfTextExtractor:

    def __init__(
        self,
        reader_factory: Callable[[Path], Any] | None = None,
    ) -> None:
        self.reader_factory = reader_factory or _default_reader_factory

    def extract(
        self,
        data: dict[str, Any],
    ) -> PdfTextExtractionReport:
        page_extractions: list[PdfPageTextExtraction] = []
        asset_errors: list[PdfTextExtractionAssetError] = []

        for item in data["items"]:
            if not _is_pdf_item(item):
                continue

            self._extract_item(
                item=item,
                page_extractions=page_extractions,
                asset_errors=asset_errors,
            )

        return PdfTextExtractionReport(
            root=data["root"],
            page_extractions=page_extractions,
            asset_errors=asset_errors,
        )

    def _extract_item(
        self,
        item: dict[str, Any],
        page_extractions: list[PdfPageTextExtraction],
        asset_errors: list[PdfTextExtractionAssetError],
    ) -> None:
        source_path = _item_path(item)
        size_bytes = _item_size(item)

        try:
            reader = self.reader_factory(Path(source_path))
        except Exception as exc:
            asset_errors.append(
                PdfTextExtractionAssetError(
                    source_path=source_path,
                    size_bytes=size_bytes,
                    error=str(exc),
                )
            )
            return

        pages = list(reader.pages)

        if len(pages) == 0:
            asset_errors.append(
                PdfTextExtractionAssetError(
                    source_path=source_path,
                    size_bytes=size_bytes,
                    error="PDF contains no pages.",
                )
            )
            return

        for page_index, page in enumerate(pages):
            content, warnings = _extract_page_content(page)
            page_extractions.append(
                PdfPageTextExtraction(
                    source_path=source_path,
                    size_bytes=size_bytes,
                    page_number=page_index + 1,
                    extraction_index=len(page_extractions),
                    extraction_method=EMBEDDED_TEXT_EXTRACTION_METHOD,
                    content=content,
                    warnings=warnings,
                )
            )


def _default_reader_factory(path: Path) -> Any:
    from pypdf import PdfReader

    return PdfReader(str(path))


def _is_pdf_item(item: dict[str, Any]) -> bool:
    asset_type = item.get("asset_type", item.get("kind"))

    if hasattr(asset_type, "name"):
        asset_type = asset_type.name

    return str(asset_type).upper() == "PDF"


def _item_path(item: dict[str, Any]) -> str:
    return str(item.get("source_path", item.get("path")))


def _item_size(item: dict[str, Any]) -> int:
    return item.get("size_bytes", item.get("size", 0))


def _extract_page_content(page: Any) -> tuple[str, list[str]]:
    warnings: list[str] = []

    try:
        content = page.extract_text()
    except Exception as exc:
        return "", [f"Failed to extract embedded text: {exc}"]

    if content is None:
        content = ""

    if content == "":
        warnings.append(NO_EMBEDDED_TEXT_WARNING)

    return content, warnings
