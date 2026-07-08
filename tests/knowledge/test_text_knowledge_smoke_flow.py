import json

from rie.knowledge.export_text_knowledge import main as export_main
from rie.knowledge.inspect_text_knowledge import main as inspect_main


def test_text_knowledge_artifact_smoke_flow_exports_then_inspects(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    knowledge_path = tmp_path / "text-knowledge.json"
    non_ascii_newline_content = "Caf\u00e9 racer helm\nRancang konsep.\n"

    evidence_path.write_text(
        json.dumps(
            {
                "evidences": [
                    {
                        "source_path": "normal.dat",
                        "content": "First prompt",
                        "size_bytes": 12,
                    },
                    {
                        "source_path": "non-ascii.dat",
                        "content": non_ascii_newline_content,
                        "size_bytes": 34,
                    },
                    {
                        "source_path": "invalid.dat",
                        "content": "Invalid",
                        "size_bytes": 7,
                        "summary": "Do not summarize.",
                    },
                    {
                        "source_path": "empty.dat",
                        "content": "",
                        "size_bytes": 0,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    export_result = export_main([
        str(evidence_path),
        "--output",
        str(knowledge_path),
    ])

    export_output = capsys.readouterr().out
    raw_knowledge_json = knowledge_path.read_text(encoding="utf-8")
    knowledge = json.loads(raw_knowledge_json)
    records = knowledge["knowledge_items"]

    assert export_result == 0
    assert knowledge_path.exists()
    assert "Exported Knowledge Items: 3" in export_output
    assert "Skipped Invalid Records : 1" in export_output
    assert len(records) == 3
    assert [record["source_path"] for record in records] == [
        "normal.dat",
        "non-ascii.dat",
        "empty.dat",
    ]
    assert [record["evidence_index"] for record in records] == [
        0,
        1,
        3,
    ]
    assert "invalid.dat" not in [
        record["source_path"]
        for record in records
    ]
    assert "Caf\u00e9" in raw_knowledge_json
    assert "Caf\\u00e9" not in raw_knowledge_json
    assert records[1]["content"] == non_ascii_newline_content
    assert records[2]["content"] == ""

    forbidden_fields = {
        "knowledge_type",
        "summary",
        "category",
        "label",
        "metadata",
        "confidence",
        "embedding",
        "prompt",
        "analysis",
        "size_class",
        "checksum",
        "artifact_id",
    }

    for record in records:
        assert set(record) == {
            "source_path",
            "content",
            "size_bytes",
            "evidence_index",
        }
        assert not any(field in record for field in forbidden_fields)

    inspect_result = inspect_main([str(knowledge_path)])

    inspection_output = capsys.readouterr().out
    expected_character_count = (
        len("First prompt")
        + len(non_ascii_newline_content)
    )

    assert inspect_result == 0
    assert "Total Knowledge Items    : 3" in inspection_output
    assert (
        f"Total Content Characters : {expected_character_count}"
        in inspection_output
    )
    assert "Empty Content Count      : 1" in inspection_output
    assert "Invalid Record Count     : 0" in inspection_output
    assert "Forbidden Field Count    : 0" in inspection_output
