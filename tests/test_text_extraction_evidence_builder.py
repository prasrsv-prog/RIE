from dataclasses import fields

import pytest

from evidence.text_extraction_evidence_builder import (
    TextExtractionEvidenceBuilder,
)
from rie.extraction.text_asset_extraction import TextAssetExtraction


def test_builds_text_extraction_evidence_from_successful_extraction(tmp_path):
    path = tmp_path / "prompt.dat"
    extraction = TextAssetExtraction(
        path=path,
        size=42,
        content="Generate a helmet concept.",
    )

    evidence = TextExtractionEvidenceBuilder.build(extraction)

    assert evidence.source_path == str(path)
    assert evidence.content == "Generate a helmet concept."
    assert evidence.size_bytes == 42


def test_preserves_extracted_content_exactly_including_non_ascii_text(tmp_path):
    path = tmp_path / "prompt.dat"
    content = "Line 1\nCafé racer helmet\nRancang helm RSV.\n"
    extraction = TextAssetExtraction(
        path=path,
        size=52,
        content=content,
    )

    evidence = TextExtractionEvidenceBuilder.build(extraction)

    assert evidence.content == content


def test_text_extraction_evidence_does_not_expose_analysis_or_size_class(
    tmp_path,
):
    extraction = TextAssetExtraction(
        path=tmp_path / "prompt.dat",
        size=12,
        content="Prompt text",
    )

    evidence = TextExtractionEvidenceBuilder.build(extraction)

    assert [field.name for field in fields(evidence)] == [
        "source_path",
        "content",
        "size_bytes",
    ]
    assert not hasattr(evidence, "analysis")
    assert not hasattr(evidence, "size_class")


def test_builder_rejects_failed_text_extraction(tmp_path):
    extraction = TextAssetExtraction(
        path=tmp_path / "missing.dat",
        size=10,
        content="",
        error="missing file",
    )

    with pytest.raises(ValueError):
        TextExtractionEvidenceBuilder.build(extraction)
