import json

from rie.knowledge.inspect_text_knowledge import main


def _write_artifact(path, data):
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def test_inspect_text_knowledge_prints_summary(tmp_path, capsys):
    knowledge_path = tmp_path / "text-knowledge.json"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "first.dat",
                    "content": "First",
                    "size_bytes": 5,
                    "evidence_index": 0,
                },
                {
                    "source_path": "empty.dat",
                    "content": "",
                    "size_bytes": 0,
                    "evidence_index": 1,
                },
            ],
        },
    )

    result = main([str(knowledge_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Text Knowledge Inspection" in output
    assert "Total Knowledge Items    : 2" in output
    assert "Total Content Characters : 5" in output
    assert "Empty Content Count      : 1" in output
    assert "Invalid Record Count     : 0" in output
    assert "Forbidden Field Count    : 0" in output


def test_inspect_text_knowledge_returns_error_for_missing_file(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "missing.json"

    result = main([str(knowledge_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Knowledge artifact not found" in output


def test_inspect_text_knowledge_returns_error_for_directory(
    tmp_path,
    capsys,
):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_inspect_text_knowledge_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    knowledge_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(knowledge_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read knowledge artifact" in output


def test_inspect_text_knowledge_returns_error_for_malformed_artifact(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    _write_artifact(
        knowledge_path,
        {
            "items": [],
        },
    )

    result = main([str(knowledge_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed knowledge artifact" in output


def test_inspect_text_knowledge_returns_zero_for_invalid_records_after_readable_artifact(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "summary.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                    "summary": "No summary belongs here.",
                },
                "not a record",
            ],
        },
    )

    result = main([str(knowledge_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total Knowledge Items    : 2" in output
    assert "Invalid Record Count     : 2" in output
    assert "Forbidden Field Count    : 1" in output
