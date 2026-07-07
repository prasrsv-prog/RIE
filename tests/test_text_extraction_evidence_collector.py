from collection.text_extraction_evidence_collection import (
    TextExtractionEvidenceCollection,
)
from collection.text_extraction_evidence_collector import (
    TextExtractionEvidenceCollector,
)
from rie.extraction.text_asset_extraction import TextAssetExtraction
from rie.extraction.text_asset_extraction_report import TextAssetExtractionReport


def test_collects_evidence_from_successful_text_extractions(tmp_path):
    first_path = tmp_path / "first.dat"
    second_path = tmp_path / "second.dat"
    report = TextAssetExtractionReport(
        root=str(tmp_path),
        total_text_assets=2,
        extractions=[
            TextAssetExtraction(
                path=first_path,
                size=10,
                content="First prompt",
            ),
            TextAssetExtraction(
                path=second_path,
                size=20,
                content="Second prompt",
            ),
        ],
    )

    collection = TextExtractionEvidenceCollector.collect(report)

    assert isinstance(collection, TextExtractionEvidenceCollection)
    assert len(collection.evidences) == 2
    assert collection.evidences[0].source_path == str(first_path)
    assert collection.evidences[0].content == "First prompt"
    assert collection.evidences[0].size_bytes == 10
    assert collection.evidences[1].source_path == str(second_path)
    assert collection.evidences[1].content == "Second prompt"
    assert collection.evidences[1].size_bytes == 20


def test_skips_failed_text_extractions(tmp_path):
    successful_path = tmp_path / "prompt.dat"
    failed_path = tmp_path / "missing.dat"
    report = TextAssetExtractionReport(
        root=str(tmp_path),
        total_text_assets=2,
        extractions=[
            TextAssetExtraction(
                path=successful_path,
                size=11,
                content="Prompt text",
            ),
            TextAssetExtraction(
                path=failed_path,
                size=0,
                content="",
                error="missing file",
            ),
        ],
    )

    collection = TextExtractionEvidenceCollector.collect(report)

    assert len(collection.evidences) == 1
    assert collection.evidences[0].source_path == str(successful_path)
