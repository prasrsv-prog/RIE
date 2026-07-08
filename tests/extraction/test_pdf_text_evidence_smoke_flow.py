import json

from rie.extraction.export_pdf_text_evidence import main as export_main
from rie.extraction.inspect_pdf_text_evidence import main as inspect_main


FORBIDDEN_FIELDS = {
    "product_type",
    "product_category",
    "helmet_model",
    "variant",
    "summary",
    "persona",
    "USP",
    "visual_style",
    "prompt",
    "final_prompt",
    "confidence",
    "embedding",
    "graph",
    "knowledge",
    "analysis",
    "style",
    "tone",
    "creative_direction",
}

PDF_TEXT_EVIDENCE_FIELDS = {
    "source_path",
    "content",
    "size_bytes",
    "page_number",
    "extraction_index",
    "extraction_method",
    "warnings",
    "evidence_index",
}


def test_pdf_text_evidence_artifact_smoke_flow_exports_then_inspects(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "pdf-text-extractions.json"
    output_path = tmp_path / "pdf-text-evidence.json"
    normal_content = "Shell construction and visor notes."
    non_ascii_newline_content = "Caf\u00e9 racer helm\nBaris kedua"
    empty_content = ""
    warning = "No embedded text found."
    broken_source_path = "broken-spec.pdf"

    input_path.write_text(
        json.dumps(
            {
                "root": str(tmp_path),
                "total_pdf_assets": 2,
                "total_page_extractions": 4,
                "failed_pdf_assets": 1,
                "page_extractions": [
                    {
                        "source_path": "helmet-normal.pdf",
                        "size_bytes": 4096,
                        "page_number": 1,
                        "extraction_index": 0,
                        "extraction_method": "embedded_text",
                        "content": normal_content,
                        "warnings": [],
                    },
                    {
                        "source_path": "helmet-non-ascii.pdf",
                        "size_bytes": 8192,
                        "page_number": 2,
                        "extraction_index": 1,
                        "extraction_method": "embedded_text",
                        "content": non_ascii_newline_content,
                        "warnings": [],
                    },
                    {
                        "source_path": "invalid-page.pdf",
                        "size_bytes": True,
                        "page_number": 3,
                        "extraction_index": 2,
                        "extraction_method": "embedded_text",
                        "content": "Invalid page should be skipped.",
                        "warnings": [],
                        "prompt": "Do not promote this field.",
                    },
                    {
                        "source_path": "helmet-empty.pdf",
                        "size_bytes": 2048,
                        "page_number": 4,
                        "extraction_index": 3,
                        "extraction_method": "embedded_text",
                        "content": empty_content,
                        "warnings": [warning],
                    },
                ],
                "asset_errors": [
                    {
                        "source_path": broken_source_path,
                        "size_bytes": 1024,
                        "error": "Cannot read PDF.",
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    export_result = export_main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    records = artifact["pdf_text_evidences"]

    assert export_result == 0
    assert output_path.exists()
    assert set(artifact) == {"pdf_text_evidences"}
    assert len(records) == 3
    assert broken_source_path not in [
        record["source_path"]
        for record in records
    ]

    assert records == [
        {
            "source_path": "helmet-normal.pdf",
            "content": normal_content,
            "size_bytes": 4096,
            "page_number": 1,
            "extraction_index": 0,
            "extraction_method": "embedded_text",
            "warnings": [],
            "evidence_index": 0,
        },
        {
            "source_path": "helmet-non-ascii.pdf",
            "content": non_ascii_newline_content,
            "size_bytes": 8192,
            "page_number": 2,
            "extraction_index": 1,
            "extraction_method": "embedded_text",
            "warnings": [],
            "evidence_index": 1,
        },
        {
            "source_path": "helmet-empty.pdf",
            "content": empty_content,
            "size_bytes": 2048,
            "page_number": 4,
            "extraction_index": 3,
            "extraction_method": "embedded_text",
            "warnings": [warning],
            "evidence_index": 2,
        },
    ]
    assert records[2]["evidence_index"] != records[2]["page_number"]
    assert records[2]["evidence_index"] != records[2]["extraction_index"]

    for record in records:
        assert set(record) == PDF_TEXT_EVIDENCE_FIELDS
        assert not set(record).intersection(FORBIDDEN_FIELDS)

    assert not set(artifact).intersection(FORBIDDEN_FIELDS)

    inspect_result = inspect_main([str(output_path)])

    inspection_output = capsys.readouterr().out
    expected_content_characters = (
        len(normal_content)
        + len(non_ascii_newline_content)
        + len(empty_content)
    )

    assert inspect_result == 0
    assert "Total PDF Text Evidences       : 3" in inspection_output
    assert (
        f"Total Content Characters       : {expected_content_characters}"
        in inspection_output
    )
    assert "Empty Content Evidence Count   : 1" in inspection_output
    assert "Warning Count                  : 1" in inspection_output
    assert "Invalid Record Count           : 0" in inspection_output
    assert "Forbidden Field Count          : 0" in inspection_output
