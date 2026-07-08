from copy import deepcopy

import pytest

from prompting.text_prompt_candidate_artifact_inspector import inspect_artifact


def test_counts_total_prompt_candidates():
    inspection = inspect_artifact(
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
        }
    )

    assert inspection.total_prompt_candidates == 2
    assert inspection.invalid_record_count == 0


def test_counts_total_content_characters():
    inspection = inspect_artifact(
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
                    "source_path": "invalid-extra.dat",
                    "content": "Invalid",
                    "size_bytes": 7,
                    "evidence_index": 1,
                    "knowledge_index": 1,
                    "extra": "field",
                },
            ],
        }
    )

    assert inspection.total_content_characters == 12


def test_counts_empty_content_candidates():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                {
                    "source_path": "empty.dat",
                    "content": "",
                    "size_bytes": 0,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                },
                {
                    "source_path": "whitespace.dat",
                    "content": "   ",
                    "size_bytes": 3,
                    "evidence_index": 1,
                    "knowledge_index": 1,
                },
            ],
        }
    )

    assert inspection.empty_content_candidate_count == 1
    assert inspection.total_content_characters == 3


def test_counts_invalid_records():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                "not a record",
                {
                    "source_path": "missing-index.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                },
                {
                    "source_path": 123,
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 1,
                    "knowledge_index": 1,
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 3


def test_counts_forbidden_fields():
    inspection = inspect_artifact(
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
                {
                    "source_path": "metadata.dat",
                    "content": "Metadata",
                    "size_bytes": 8,
                    "evidence_index": 1,
                    "knowledge_index": 1,
                    "metadata": {},
                    "embedding": [],
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 2
    assert inspection.forbidden_field_count == 3


def test_accepts_exact_valid_fields_only():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                {
                    "source_path": "valid.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 0
    assert inspection.forbidden_field_count == 0


def test_rejects_bool_for_size_bytes():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                {
                    "source_path": "bool-size.dat",
                    "content": "Prompt",
                    "size_bytes": True,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 1


def test_rejects_bool_for_evidence_index():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                {
                    "source_path": "bool-evidence.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": False,
                    "knowledge_index": 0,
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 1


def test_rejects_bool_for_knowledge_index():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                {
                    "source_path": "bool-knowledge.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                    "knowledge_index": True,
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 1


def test_rejects_missing_required_fields():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                {
                    "source_path": "missing-knowledge.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 1


def test_rejects_extra_non_forbidden_fields_as_invalid():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                {
                    "source_path": "extra.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                    "unexpected": "field",
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 1
    assert inspection.forbidden_field_count == 0


def test_counts_forbidden_fields_separately():
    inspection = inspect_artifact(
        {
            "prompt_candidates": [
                {
                    "source_path": "style.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                    "knowledge_index": 0,
                    "style": "cinematic",
                },
            ],
        }
    )

    assert inspection.invalid_record_count == 1
    assert inspection.forbidden_field_count == 1


def test_preserves_inspection_only_behavior_no_mutation():
    artifact = {
        "prompt_candidates": [
            {
                "source_path": "valid.dat",
                "content": "Prompt",
                "size_bytes": 6,
                "evidence_index": 0,
                "knowledge_index": 0,
            },
            {
                "source_path": "invalid.dat",
                "content": "Invalid",
                "size_bytes": 7,
                "evidence_index": 1,
                "knowledge_index": 1,
                "prompt": "Do not write prompts here.",
            },
        ],
    }
    original = deepcopy(artifact)

    inspect_artifact(artifact)

    assert artifact == original


def test_rejects_missing_prompt_candidates():
    with pytest.raises(ValueError, match="prompt_candidates"):
        inspect_artifact({})


def test_rejects_non_list_prompt_candidates():
    with pytest.raises(ValueError, match="list"):
        inspect_artifact({"prompt_candidates": {}})


def test_rejects_non_dict_top_level_artifact():
    with pytest.raises(ValueError, match="object"):
        inspect_artifact([])
