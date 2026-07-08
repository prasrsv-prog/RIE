import json

from rie.prompt.inspect_text_prompt_candidates import main


def _write_artifact(path, data):
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def test_inspect_text_prompt_candidates_valid_artifact_returns_zero(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        prompt_candidates_path,
        {
            "prompt_candidates": [
                {
                    "source_path": "first.dat",
                    "content": "First",
                    "size_bytes": 5,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                },
            ],
        },
    )

    result = main([str(prompt_candidates_path)])

    capsys.readouterr()
    assert result == 0


def test_inspect_text_prompt_candidates_prints_total_prompt_candidates(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        prompt_candidates_path,
        {
            "prompt_candidates": [
                {
                    "source_path": "first.dat",
                    "content": "First",
                    "size_bytes": 5,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                },
                {
                    "source_path": "second.dat",
                    "content": "Second",
                    "size_bytes": 6,
                    "evidence_index": 1,
                    "knowledge_index": 1,
                },
            ],
        },
    )

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Text Prompt Candidate Inspection" in output
    assert "Total Prompt Candidates   : 2" in output


def test_inspect_text_prompt_candidates_prints_total_content_characters(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        prompt_candidates_path,
        {
            "prompt_candidates": [
                {
                    "source_path": "first.dat",
                    "content": "First",
                    "size_bytes": 5,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                },
                {
                    "source_path": "second.dat",
                    "content": "Second",
                    "size_bytes": 6,
                    "evidence_index": 1,
                    "knowledge_index": 1,
                },
            ],
        },
    )

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total Content Characters  : 11" in output


def test_inspect_text_prompt_candidates_prints_empty_content_count(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        prompt_candidates_path,
        {
            "prompt_candidates": [
                {
                    "source_path": "empty.dat",
                    "content": "",
                    "size_bytes": 0,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                },
            ],
        },
    )

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Empty Content Candidates  : 1" in output


def test_inspect_text_prompt_candidates_prints_invalid_record_count(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        prompt_candidates_path,
        {
            "prompt_candidates": [
                {
                    "source_path": "missing-index.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                },
            ],
        },
    )

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Invalid Record Count      : 1" in output


def test_inspect_text_prompt_candidates_prints_forbidden_field_count(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        prompt_candidates_path,
        {
            "prompt_candidates": [
                {
                    "source_path": "prompt.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                    "prompt": "Do not write prompts here.",
                },
            ],
        },
    )

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Forbidden Field Count     : 1" in output


def test_inspect_text_prompt_candidates_readable_artifact_with_invalid_records_returns_zero(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(
        prompt_candidates_path,
        {
            "prompt_candidates": [
                {
                    "source_path": "prompt.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                    "prompt": "Do not write prompts here.",
                },
                "not a record",
            ],
        },
    )

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Total Prompt Candidates   : 2" in output
    assert "Invalid Record Count      : 2" in output
    assert "Forbidden Field Count     : 1" in output


def test_inspect_text_prompt_candidates_missing_input_file_returns_one(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "missing.json"

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Prompt candidate artifact not found" in output


def test_inspect_text_prompt_candidates_directory_input_returns_one(
    tmp_path,
    capsys,
):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output


def test_inspect_text_prompt_candidates_invalid_json_returns_one(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    prompt_candidates_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read prompt candidate artifact" in output


def test_inspect_text_prompt_candidates_top_level_list_returns_one(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(prompt_candidates_path, [])

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed prompt candidate artifact" in output


def test_inspect_text_prompt_candidates_missing_prompt_candidates_returns_one(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(prompt_candidates_path, {"items": []})

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed prompt candidate artifact" in output


def test_inspect_text_prompt_candidates_prompt_candidates_not_list_returns_one(
    tmp_path,
    capsys,
):
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    _write_artifact(prompt_candidates_path, {"prompt_candidates": {}})

    result = main([str(prompt_candidates_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed prompt candidate artifact" in output
