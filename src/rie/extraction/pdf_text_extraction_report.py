from dataclasses import dataclass

from rie.extraction.pdf_page_text_extraction import PdfPageTextExtraction


@dataclass(frozen=True)
class PdfTextExtractionAssetError:
    source_path: str
    size_bytes: int
    error: str


@dataclass(frozen=True)
class PdfTextExtractionReport:
    root: str
    page_extractions: list[PdfPageTextExtraction]
    asset_errors: list[PdfTextExtractionAssetError]

    @property
    def total_pdf_assets(self) -> int:
        source_paths = {
            extraction.source_path
            for extraction in self.page_extractions
        }
        source_paths.update(
            asset_error.source_path
            for asset_error in self.asset_errors
        )

        return len(source_paths)

    @property
    def total_page_extractions(self) -> int:
        return len(self.page_extractions)

    @property
    def failed_pdf_assets(self) -> int:
        return len(self.asset_errors)
