import json

from rie.prompt.export_text_prompt_candidates import main as export_main
from rie.prompt.inspect_text_prompt_candidates import main as inspect_main


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


def test_text_prompt_candidate_artifact_smoke_flow_exports_then_inspects(
    tmp_path,
    capsys,
):
    knowledge_path = tmp_path / "text-knowledge.json"
    prompt_candidates_path = tmp_path / "text-prompt-candidates.json"
    normal_content = "Normal prompt candidate source"
    non_ascii_newline_content = "Caf\u00e9 prompt\nBaris kedua"
    empty_content = ""
    expected_content_characters = (
        len(normal_content)
        + len(non_ascii_newline_content)
        + len(empty_content)
    )

    knowledge_path.write_text(
        json.dumps(
            {
                "knowledge_items": [
                    {
                        "source_path": "normal.txt",
                        "content": normal_content,
                        "size_bytes": 30,
                        "evidence_index": 0,
                    },
                    {
                        "source_path": "localized.txt",
                        "content": non_ascii_newline_content,
                        "size_bytes": 25,
                        "evidence_index": 1,
                    },
                    {
                        "source_path": "invalid.txt",
                        "content": "Should not become a prompt candidate",
                        "size_bytes": 36,
                        "evidence_index": 2,
                        "prompt": "Do not write prompts here.",
                    },
                    {
                        "source_path": "empty.txt",
                        "content": empty_content,
                        "size_bytes": 0,
                        "evidence_index": 3,
                    },
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    export_result = export_main([
        str(knowledge_path),
        "--output",
        str(prompt_candidates_path),
    ])

    export_output = capsys.readouterr().out
    prompt_candidate_artifact = json.loads(
        prompt_candidates_path.read_text(encoding="utf-8")
    )

    assert export_result == 0
    assert prompt_candidates_path.exists()
    assert "Exported Prompt Candidates : 3" in export_output
    assert "Skipped Invalid Records    : 1" in export_output

    assert prompt_candidate_artifact == {
        "prompt_candidates": [
            {
                "source_path": "normal.txt",
                "content": normal_content,
                "size_bytes": 30,
                "evidence_index": 0,
                "knowledge_index": 0,
            },
            {
                "source_path": "localized.txt",
                "content": non_ascii_newline_content,
                "size_bytes": 25,
                "evidence_index": 1,
                "knowledge_index": 1,
            },
            {
                "source_path": "empty.txt",
                "content": empty_content,
                "size_bytes": 0,
                "evidence_index": 3,
                "knowledge_index": 3,
            },
        ],
    }

    for candidate in prompt_candidate_artifact["prompt_candidates"]:
        assert set(candidate) == {
            "source_path",
            "content",
            "size_bytes",
            "evidence_index",
            "knowledge_index",
        }
        assert not any(field in candidate for field in FORBIDDEN_FIELDS)

    inspect_result = inspect_main([str(prompt_candidates_path)])

    inspect_output = capsys.readouterr().out
    assert inspect_result == 0
    assert "Total Prompt Candidates   : 3" in inspect_output
    assert (
        f"Total Content Characters  : {expected_content_characters}"
        in inspect_output
    )
    assert "Empty Content Candidates  : 1" in inspect_output
    assert "Invalid Record Count      : 0" in inspect_output
    assert "Forbidden Field Count     : 0" in inspect_output
