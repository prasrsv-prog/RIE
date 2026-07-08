import pytest

from collection.text_extraction_evidence_artifact_inspector import (
    inspect_artifact,
)


def test_inspects_valid_text_extraction_evidence_artifact():
    inspection = inspect_artifact(
        {
            "evidences": [
                {
                    "source_path": "first.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                },
                {
                    "source_path": "second.dat",
                    "content": "Second",
                    "size_bytes": 6,
                },
            ],
        }
    )

    assert inspection.total_evidences == 2
    assert inspection.total_content_characters == 12
    assert inspection.empty_content_count == 0
    assert inspection.invalid_record_count == 0
    assert inspection.forbidden_field_count == 0


def test_counts_empty_content_records():
    inspection = inspect_artifact(
        {
            "evidences": [
                {
                    "source_path": "empty.dat",
                    "content": "",
                    "size_bytes": 0,
                },
                {
                    "source_path": "whitespace.dat",
                    "content": "   ",
                    "size_bytes": 3,
                },
            ],
        }
    )

    assert inspection.total_evidences == 2
    assert inspection.total_content_characters == 3
    assert inspection.empty_content_count == 1
    assert inspection.invalid_record_count == 0


def test_counts_invalid_records_for_missing_required_fields():
    inspection = inspect_artifact(
        {
            "evidences": [
                {
                    "source_path": "missing-size.dat",
                    "content": "Prompt",
                },
                {
                    "content": "Missing path",
                    "size_bytes": 12,
                },
            ],
        }
    )

    assert inspection.total_evidences == 2
    assert inspection.invalid_record_count == 2


def test_counts_invalid_records_for_wrong_field_types():
    inspection = inspect_artifact(
        {
            "evidences": [
                {
                    "source_path": 123,
                    "content": "Prompt",
                    "size_bytes": 6,
                },
                {
                    "source_path": "content-list.dat",
                    "content": ["Prompt"],
                    "size_bytes": 6,
                },
                {
                    "source_path": "size-string.dat",
                    "content": "Prompt",
                    "size_bytes": "6",
                },
            ],
        }
    )

    assert inspection.total_evidences == 3
    assert inspection.invalid_record_count == 3


def test_counts_forbidden_fields():
    inspection = inspect_artifact(
        {
            "evidences": [
                {
                    "source_path": "summary.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "summary": "Do not summarize.",
                },
                {
                    "source_path": "metadata.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                    "metadata": {},
                    "embedding": [],
                },
            ],
        }
    )

    assert inspection.total_evidences == 2
    assert inspection.invalid_record_count == 2
    assert inspection.forbidden_field_count == 3


def test_rejects_missing_evidences():
    with pytest.raises(ValueError, match="evidences"):
        inspect_artifact({})


def test_rejects_non_list_evidences():
    with pytest.raises(ValueError, match="list"):
        inspect_artifact({"evidences": {}})


def test_rejects_non_dict_top_level_artifact():
    with pytest.raises(ValueError, match="object"):
        inspect_artifact([])


def test_rejects_bool_size_bytes():
    inspection = inspect_artifact(
        {
            "evidences": [
                {
                    "source_path": "bool-size.dat",
                    "content": "Prompt",
                    "size_bytes": True,
                },
            ],
        }
    )

    assert inspection.total_evidences == 1
    assert inspection.invalid_record_count == 1


def test_counts_non_dict_evidence_entries_as_invalid():
    inspection = inspect_artifact(
        {
            "evidences": [
                None,
                "not a record",
                {
                    "source_path": "prompt.dat",
                    "content": "Prompt",
                    "size_bytes": 6,
                },
            ],
        }
    )

    assert inspection.total_evidences == 3
    assert inspection.total_content_characters == 6
    assert inspection.invalid_record_count == 2
