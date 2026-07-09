import json

from rie.knowledge.export_official_knowledge import main as export_main
from rie.knowledge.inspect_official_knowledge import main as inspect_main


FORBIDDEN_FIELDS = {
    "prompt",
    "final_prompt",
    "instruction",
    "system_prompt",
    "user_prompt",
    "ai_output",
    "generated_claim",
    "confidence",
    "embedding",
    "graph",
    "score",
    "creative_direction",
    "image_generation",
    "video_generation",
    "summary",
    "category",
    "label",
    "product_type",
    "variant",
    "style",
    "tone",
    "analysis",
    "model",
}

OFFICIAL_KNOWLEDGE_FIELDS = {
    "knowledge_id",
    "source_path",
    "source_document",
    "source_section",
    "source_page",
    "title",
    "content",
    "status",
    "governance_level",
    "pdf_evidence_index",
    "extraction_index",
    "official_knowledge_index",
}


def test_official_knowledge_cli_smoke_flow_exports_then_inspects(
    tmp_path,
    capsys,
):
    source_path = tmp_path / "official-knowledge-source.json"
    artifact_path = tmp_path / "official-knowledge.json"

    source_path.write_text(
        json.dumps(
            {
                "official_knowledge_source_items": [
                    {
                        "knowledge_id": "EX-001",
                        "source_path": (
                            "docs/example_official_knowledge_base.pdf"
                        ),
                        "source_document": (
                            "Example Official Knowledge Base"
                        ),
                        "source_section": "Example Section",
                        "source_page": 1,
                        "title": "Example Locked Knowledge",
                        "content": "Example official knowledge content.",
                        "status": "LOCKED",
                        "governance_level": "OFFICIAL SOURCE OF TRUTH",
                        "pdf_evidence_index": None,
                        "extraction_index": None,
                    },
                    {
                        "knowledge_id": None,
                        "source_path": (
                            "docs/example_official_knowledge_base.pdf"
                        ),
                        "source_document": (
                            "Example Official Knowledge Base"
                        ),
                        "source_section": None,
                        "source_page": None,
                        "title": "Example Knowledge Without Governance",
                        "content": (
                            "Example official knowledge content without "
                            "governance."
                        ),
                        "status": None,
                        "governance_level": None,
                        "pdf_evidence_index": None,
                        "extraction_index": None,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    export_result = export_main([
        str(source_path),
        "--output",
        str(artifact_path),
    ])

    export_output = capsys.readouterr().out
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    records = artifact["official_knowledge_items"]

    assert export_result == 0
    assert artifact_path.exists()
    assert "Official Knowledge Export" in export_output
    assert "Total Source Items              : 2" in export_output
    assert "Exported Official Knowledge Items: 2" in export_output

    assert set(artifact) == {"official_knowledge_items"}
    assert len(records) == 2
    assert [
        record["title"]
        for record in records
    ] == [
        "Example Locked Knowledge",
        "Example Knowledge Without Governance",
    ]
    assert [
        record["official_knowledge_index"]
        for record in records
    ] == [0, 1]

    assert records[0]["knowledge_id"] == "EX-001"
    assert records[0]["source_path"] == (
        "docs/example_official_knowledge_base.pdf"
    )
    assert records[0]["source_document"] == (
        "Example Official Knowledge Base"
    )
    assert records[0]["source_section"] == "Example Section"
    assert records[0]["source_page"] == 1
    assert records[0]["content"] == "Example official knowledge content."
    assert records[0]["status"] == "LOCKED"
    assert records[0]["governance_level"] == (
        "OFFICIAL SOURCE OF TRUTH"
    )
    assert records[0]["pdf_evidence_index"] is None
    assert records[0]["extraction_index"] is None

    assert records[1]["knowledge_id"] is None
    assert records[1]["source_section"] is None
    assert records[1]["source_page"] is None
    assert records[1]["status"] is None
    assert records[1]["governance_level"] is None
    assert records[1]["pdf_evidence_index"] is None
    assert records[1]["extraction_index"] is None

    assert not set(artifact).intersection(FORBIDDEN_FIELDS)
    for record in records:
        assert set(record) == OFFICIAL_KNOWLEDGE_FIELDS
        assert not set(record).intersection(FORBIDDEN_FIELDS)

    inspect_result = inspect_main([str(artifact_path)])

    inspect_output = capsys.readouterr().out
    assert inspect_result == 0
    assert "Official Knowledge Inspection" in inspect_output
    assert "total_official_knowledge_items: 2" in inspect_output
    assert "missing_required_traceability_count: 0" in inspect_output
    assert "missing_governance_count: 1" in inspect_output
    assert "forbidden_field_count: 0" in inspect_output
    assert "index_mismatch_count: 0" in inspect_output
    assert "is_valid: true" in inspect_output
