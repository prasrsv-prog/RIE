import json

from rie.knowledge.export_text_knowledge import main


def _write_artifact(path, data):
    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_export_text_knowledge_writes_valid_knowledge_items(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    output_path = tmp_path / "text-knowledge.json"
    _write_artifact(
        evidence_path,
        {
            "evidences": [
                {
                    "source_path": "first.dat",
                    "content": "First prompt",
                    "size_bytes": 12,
                },
                {
                    "source_path": "second.dat",
                    "content": "Second prompt",
                    "size_bytes": 13,
                },
            ],
        },
    )

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "Text Knowledge Export" in output
    assert "Total Evidence Records  : 2" in output
    assert "Exported Knowledge Items: 2" in output
    assert "Skipped Invalid Records : 0" in output
    assert f"Output Path             : {output_path}" in output
    assert data == {
        "knowledge_items": [
            {
                "source_path": "first.dat",
                "content": "First prompt",
                "size_bytes": 12,
                "evidence_index": 0,
            },
            {
                "source_path": "second.dat",
                "content": "Second prompt",
                "size_bytes": 13,
                "evidence_index": 1,
            },
        ],
    }


def test_export_text_knowledge_preserves_order_and_evidence_index(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    output_path = tmp_path / "text-knowledge.json"
    _write_artifact(
        evidence_path,
        {
            "evidences": [
                {
                    "source_path": "b.dat",
                    "content": "Second",
                    "size_bytes": 6,
                },
                {
                    "source_path": "a.dat",
                    "content": "First",
                    "size_bytes": 5,
                },
            ],
        },
    )

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["knowledge_items"] == [
        {
            "source_path": "b.dat",
            "content": "Second",
            "size_bytes": 6,
            "evidence_index": 0,
        },
        {
            "source_path": "a.dat",
            "content": "First",
            "size_bytes": 5,
            "evidence_index": 1,
        },
    ]


def test_export_text_knowledge_skips_invalid_evidence_records(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    output_path = tmp_path / "text-knowledge.json"
    _write_artifact(
        evidence_path,
        {
            "evidences": [
                {
                    "source_path": "valid-first.dat",
                    "content": "First",
                    "size_bytes": 5,
                },
                {
                    "source_path": "invalid-extra.dat",
                    "content": "Invalid",
                    "size_bytes": 7,
                    "summary": "Do not summarize.",
                },
                "not a record",
                {
                    "source_path": "valid-second.dat",
                    "content": "Second",
                    "size_bytes": 6,
                },
            ],
        },
    )

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "Total Evidence Records  : 4" in output
    assert "Exported Knowledge Items: 2" in output
    assert "Skipped Invalid Records : 2" in output
    assert data["knowledge_items"] == [
        {
            "source_path": "valid-first.dat",
            "content": "First",
            "size_bytes": 5,
            "evidence_index": 0,
        },
        {
            "source_path": "valid-second.dat",
            "content": "Second",
            "size_bytes": 6,
            "evidence_index": 3,
        },
    ]
    assert set(data["knowledge_items"][0]) == {
        "source_path",
        "content",
        "size_bytes",
        "evidence_index",
    }


def test_export_text_knowledge_preserves_non_ascii_content(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    output_path = tmp_path / "text-knowledge.json"
    content = "Caf\u00e9 racer helm: Rancang konsep."
    _write_artifact(
        evidence_path,
        {
            "evidences": [
                {
                    "source_path": "prompt.dat",
                    "content": content,
                    "size_bytes": 34,
                },
            ],
        },
    )

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    raw_json = output_path.read_text(encoding="utf-8")
    data = json.loads(raw_json)

    assert result == 0
    assert content in raw_json
    assert "Caf\\u00e9" not in raw_json
    assert data["knowledge_items"][0]["content"] == content


def test_export_text_knowledge_preserves_newline_content(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    output_path = tmp_path / "text-knowledge.json"
    content = "Line 1\nLine 2\n"
    _write_artifact(
        evidence_path,
        {
            "evidences": [
                {
                    "source_path": "prompt.dat",
                    "content": content,
                    "size_bytes": 14,
                },
            ],
        },
    )

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["knowledge_items"][0]["content"] == content


def test_export_text_knowledge_returns_error_for_missing_artifact(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "missing.json"
    output_path = tmp_path / "text-knowledge.json"

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Evidence artifact not found" in output


def test_export_text_knowledge_returns_error_for_directory(
    tmp_path,
    capsys,
):
    output_path = tmp_path / "text-knowledge.json"

    result = main([
        str(tmp_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_export_text_knowledge_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    output_path = tmp_path / "text-knowledge.json"
    evidence_path.write_text("{invalid-json", encoding="utf-8")

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read evidence artifact" in output


def test_export_text_knowledge_returns_error_for_malformed_artifact(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    output_path = tmp_path / "text-knowledge.json"
    _write_artifact(
        evidence_path,
        {
            "items": [],
        },
    )

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed evidence artifact" in output


def test_export_text_knowledge_returns_error_for_missing_output_parent(
    tmp_path,
    capsys,
):
    evidence_path = tmp_path / "text-evidence.json"
    output_path = tmp_path / "missing" / "text-knowledge.json"
    _write_artifact(
        evidence_path,
        {
            "evidences": [],
        },
    )

    result = main([
        str(evidence_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Output folder not found" in output
