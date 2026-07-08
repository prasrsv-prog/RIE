import json

from rie.prompt.export_text_prompt_candidates import main


FORBIDDEN_FIELDS = {
    "prompt",
    "final_prompt",
    "instruction",
    "system_prompt",
    "user_prompt",
    "summary",
    "category",
    "label",
    "metadata",
    "confidence",
    "score",
    "embedding",
    "graph",
    "style",
    "tone",
    "creative_direction",
    "image_generation",
    "video_generation",
    "model",
    "analysis",
}


def _write_artifact(path, data):
    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_export_text_prompt_candidates_exports_valid_text_knowledge_json(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        knowledge_path,
        {
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
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert output_path.exists()
    assert "Text Prompt Candidate Export" in output
    assert "Total Knowledge Items       : 2" in output
    assert "Exported Prompt Candidates : 2" in output
    assert "Skipped Invalid Records    : 0" in output
    assert f"Output Path                : {output_path}" in output
    assert data == {
        "prompt_candidates": [
            {
                "source_path": "first.dat",
                "content": "First prompt",
                "size_bytes": 12,
                "evidence_index": 0,
                "knowledge_index": 0,
            },
            {
                "source_path": "second.dat",
                "content": "Second prompt",
                "size_bytes": 13,
                "evidence_index": 1,
                "knowledge_index": 1,
            },
        ],
    }


def test_export_text_prompt_candidates_preserves_exact_content(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    content = "  Prompt with exact spacing.  "
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "prompt.dat",
                    "content": content,
                    "size_bytes": 30,
                    "evidence_index": 0,
                },
            ],
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["prompt_candidates"][0]["content"] == content


def test_export_text_prompt_candidates_preserves_non_ascii_content(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    content = "Caf\u00e9 racer helm: Rancang konsep."
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "prompt.dat",
                    "content": content,
                    "size_bytes": 34,
                    "evidence_index": 2,
                },
            ],
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    raw_json = output_path.read_text(encoding="utf-8")
    data = json.loads(raw_json)

    assert result == 0
    assert content in raw_json
    assert "Caf\\u00e9" not in raw_json
    assert data["prompt_candidates"][0]["content"] == content


def test_export_text_prompt_candidates_preserves_newline_content(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    content = "Line 1\nLine 2\n"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "prompt.dat",
                    "content": content,
                    "size_bytes": 14,
                    "evidence_index": 3,
                },
            ],
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["prompt_candidates"][0]["content"] == content


def test_export_text_prompt_candidates_preserves_empty_content(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "empty.dat",
                    "content": "",
                    "size_bytes": 0,
                    "evidence_index": 4,
                },
            ],
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["prompt_candidates"][0]["content"] == ""


def test_export_text_prompt_candidates_skips_invalid_records_and_preserves_knowledge_index(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "valid-first.dat",
                    "content": "First",
                    "size_bytes": 5,
                    "evidence_index": 0,
                },
                {
                    "source_path": "invalid-extra.dat",
                    "content": "Invalid",
                    "size_bytes": 7,
                    "evidence_index": 1,
                    "summary": "Do not summarize.",
                },
                "not a record",
                {
                    "source_path": "valid-second.dat",
                    "content": "Second",
                    "size_bytes": 6,
                    "evidence_index": 3,
                },
            ],
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert "Total Knowledge Items       : 4" in output
    assert "Exported Prompt Candidates : 2" in output
    assert "Skipped Invalid Records    : 2" in output
    assert data["prompt_candidates"] == [
        {
            "source_path": "valid-first.dat",
            "content": "First",
            "size_bytes": 5,
            "evidence_index": 0,
            "knowledge_index": 0,
        },
        {
            "source_path": "valid-second.dat",
            "content": "Second",
            "size_bytes": 6,
            "evidence_index": 3,
            "knowledge_index": 3,
        },
    ]


def test_export_text_prompt_candidates_rejects_bool_size_bytes(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "bool-size.dat",
                    "content": "Invalid",
                    "size_bytes": True,
                    "evidence_index": 0,
                },
                {
                    "source_path": "valid.dat",
                    "content": "Valid",
                    "size_bytes": 5,
                    "evidence_index": 1,
                },
            ],
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["prompt_candidates"] == [
        {
            "source_path": "valid.dat",
            "content": "Valid",
            "size_bytes": 5,
            "evidence_index": 1,
            "knowledge_index": 1,
        },
    ]


def test_export_text_prompt_candidates_rejects_bool_evidence_index(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "bool-index.dat",
                    "content": "Invalid",
                    "size_bytes": 7,
                    "evidence_index": False,
                },
                {
                    "source_path": "valid.dat",
                    "content": "Valid",
                    "size_bytes": 5,
                    "evidence_index": 1,
                },
            ],
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert data["prompt_candidates"] == [
        {
            "source_path": "valid.dat",
            "content": "Valid",
            "size_bytes": 5,
            "evidence_index": 1,
            "knowledge_index": 1,
        },
    ]


def test_export_text_prompt_candidates_returns_error_for_missing_input(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "missing.json"
    output_path = tmp_path / "text-prompt-candidates.json"

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Knowledge artifact not found" in output


def test_export_text_prompt_candidates_returns_error_for_directory_input(
    tmp_path,
    capsys,
):
    output_path = tmp_path / "text-prompt-candidates.json"

    result = main([
        str(tmp_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_export_text_prompt_candidates_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    knowledge_path.write_text("{invalid-json", encoding="utf-8")

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read knowledge artifact" in output


def test_export_text_prompt_candidates_returns_error_for_malformed_top_level_artifact(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        knowledge_path,
        [],
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed knowledge artifact" in output


def test_export_text_prompt_candidates_returns_error_for_knowledge_items_not_list(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": {},
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed knowledge artifact" in output


def test_export_text_prompt_candidates_output_excludes_forbidden_fields(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    output_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        knowledge_path,
        {
            "knowledge_items": [
                {
                    "source_path": "prompt.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                },
            ],
        },
    )

    result = main([
        str(knowledge_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    candidate = data["prompt_candidates"][0]

    assert result == 0
    assert set(candidate) == {
        "source_path",
        "content",
        "size_bytes",
        "evidence_index",
        "knowledge_index",
    }
    assert not any(field in candidate for field in FORBIDDEN_FIELDS)
