import json
from typing import Any

from rie.extraction.pdf_text_extraction_report import PdfTextExtractionReport


class PdfTextExtractionReportSerializer:

    @staticmethod
    def to_dict(
        report: PdfTextExtractionReport,
    ) -> dict[str, Any]:
        return {
            "root": report.root,
            "total_pdf_assets": report.total_pdf_assets,
            "total_page_extractions": report.total_page_extractions,
            "failed_pdf_assets": report.failed_pdf_assets,
            "page_extractions": [
                {
                    "source_path": extraction.source_path,
                    "size_bytes": extraction.size_bytes,
                    "page_number": extraction.page_number,
                    "extraction_index": extraction.extraction_index,
                    "extraction_method": extraction.extraction_method,
                    "content": extraction.content,
                    "warnings": extraction.warnings,
                }
                for extraction in report.page_extractions
            ],
            "asset_errors": [
                {
                    "source_path": asset_error.source_path,
                    "size_bytes": asset_error.size_bytes,
                    "error": asset_error.error,
                }
                for asset_error in report.asset_errors
            ],
        }

    @staticmethod
    def to_json(
        report: PdfTextExtractionReport,
    ) -> str:
        return json.dumps(
            PdfTextExtractionReportSerializer.to_dict(report),
            indent=2,
            ensure_ascii=False,
        )
