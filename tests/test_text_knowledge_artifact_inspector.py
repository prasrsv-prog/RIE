import pytest

from knowledge.text_knowledge_artifact_inspector import inspect_artifact


def test_inspects_valid_text_knowledge_artifact():
    inspection = inspect_artifact(
        {
            "knowledge_items": [
                {
                    "source_path": "first.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                },
                {
                    "source_path": "second.dat",
                    "content": "Second",
                    "size_bytes": 6,
                    "evidence_index": 1,
                },
            ],
        }
    )

    assert inspection.total_knowledge_items == 2
    assert inspection.total_content_characters == 12
    assert inspection.empty_content_count == 0
    assert inspection.invalid_record_count == 0
    assert inspection.forbidden_field_count == 0


def test_counts_empty_content_items():
    inspection = inspect_artifact(
        {
            "knowledge_items": [
                {
                    "source_path": "empty.dat",
                    "content": "",
                    "size_bytes": 0,
                    "evidence_index": 0,
                },
                {
                    "source_path": "whitespace.dat",
                    "content": "   ",
                    "size_bytes": 3,
                    "evidence_index": 1,
                },
            ],
        }
    )

    assert inspection.total_knowledge_items == 2
    assert inspection.total_content_characters == 3
    assert inspection.empty_content_count == 1
    assert inspection.invalid_record_count == 0


def test_counts_invalid_records_for_missing_required_fields():
    inspection = inspect_artifact(
        {
            "knowledge_items": [
                {
                    "source_path": "missing-index.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                },
                {
                    "content": "Missing path",
                    "size_bytes": 12,
                    "evidence_index": 1,
                },
            ],
        }
    )

    assert inspection.total_knowledge_items == 2
    assert inspection.invalid_record_count == 2


def test_counts_invalid_records_for_wrong_field_types():
    inspection = inspect_artifact(
        {
            "knowledge_items": [
                {
                    "source_path": 123,
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                },
                {
                    "source_path": "content-list.dat",
                    "content": ["Prompt"],
                    "size_bytes": 6,
                    "evidence_index": 1,
                },
                {
                    "source_path": "size-string.dat",
                    "content": "Prompt",
                    "size_bytes": "6",
                    "evidence_index": 2,
                },
                {
                    "source_path": "index-string.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": "3",
                },
            ],
        }
    )

    assert inspection.total_knowledge_items == 4
    assert inspection.invalid_record_count == 4


def test_rejects_bool_size_bytes():
    inspection = inspect_artifact(
        {
            "knowledge_items": [
                {
                    "source_path": "bool-size.dat",
                    "content": "Prompt",
                    "size_bytes": True,
                    "evidence_index": 0,
                },
            ],
        }
    )

    assert inspection.total_knowledge_items == 1
    assert inspection.invalid_record_count == 1


def test_rejects_bool_evidence_index():
    inspection = inspect_artifact(
        {
            "knowledge_items": [
                {
                    "source_path": "bool-index.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": False,
                },
            ],
        }
    )

    assert inspection.total_knowledge_items == 1
    assert inspection.invalid_record_count == 1


def test_counts_forbidden_fields():
    inspection = inspect_artifact(
        {
            "knowledge_items": [
                {
                    "source_path": "summary.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 0,
                    "summary": "Do not summarize.",
                },
                {
                    "source_path": "metadata.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 1,
                    "metadata": {},
                    "embedding": [],
                },
            ],
        }
    )

    assert inspection.total_knowledge_items == 2
    assert inspection.invalid_record_count == 2
    assert inspection.forbidden_field_count == 3


def test_rejects_missing_knowledge_items():
    with pytest.raises(ValueError, match="knowledge_items"):
        inspect_artifact({})


def test_rejects_non_list_knowledge_items():
    with pytest.raises(ValueError, match="list"):
        inspect_artifact({"knowledge_items": {}})


def test_rejects_non_dict_top_level_artifact():
    with pytest.raises(ValueError, match="object"):
        inspect_artifact([])


def test_counts_non_dict_knowledge_items_as_invalid():
    inspection = inspect_artifact(
        {
            "knowledge_items": [
                None,
                "not a record",
                {
                    "source_path": "prompt.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "evidence_index": 2,
                },
            ],
        }
    )

    assert inspection.total_knowledge_items == 3
    assert inspection.total_content_characters == 6
    assert inspection.invalid_record_count == 2
