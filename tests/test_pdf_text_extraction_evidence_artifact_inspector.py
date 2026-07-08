from copy import deepcopy

import pytest

from evidence.pdf_text_extraction_evidence_artifact_inspector import (
    inspect_artifact,
)


def _valid_evidence(**overrides):
    evidence = {
        "source_path": "spec.pdf",
        "content": "Page text",
        "size_bytes": 123,
        "page_number": 1,
        "extraction_index": 0,
        "extraction_method": "embedded_text",
        "warnings": [],
        "evidence_index": 0,
    }
    evidence.update(overrides)
    return evidence


def _valid_artifact(**overrides):
    artifact = {
        "pdf_text_evidences": [
            _valid_evidence(),
        ],
    }
    artifact.update(overrides)
    return artifact


def test_counts_total_pdf_text_evidences():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(),
                _valid_evidence(source_path="second.pdf"),
            ],
        )
    )

    assert inspection.total_pdf_text_evidences == 2


def test_counts_total_content_characters():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(content="First"),
                _valid_evidence(content="Second"),
                _valid_evidence(content=123),
            ],
        )
    )

    assert inspection.total_content_characters == len("FirstSecond")


def test_counts_empty_content_evidence():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(content=""),
                _valid_evidence(content="   "),
            ],
        )
    )

    assert inspection.empty_content_evidence_count == 1


def test_counts_warning_count():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(
                    warnings=[
                        "No embedded text found.",
                        "Failed to extract embedded text from page.",
                    ],
                ),
                _valid_evidence(warnings=[]),
            ],
        )
    )

    assert inspection.warning_count == 2


def test_counts_invalid_records():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                "not a record",
                _valid_evidence(source_path=123),
            ],
        )
    )

    assert inspection.invalid_record_count == 2


def test_counts_forbidden_fields():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(prompt="Do not write prompts here."),
                _valid_evidence(summary="Do not summarize."),
            ],
        )
    )

    assert inspection.forbidden_field_count == 2
    assert inspection.invalid_record_count == 2


def test_accepts_exact_valid_top_level_fields_only():
    inspection = inspect_artifact(_valid_artifact())

    assert inspection.invalid_record_count == 0
    assert inspection.forbidden_field_count == 0


def test_rejects_extra_top_level_key():
    with pytest.raises(ValueError, match="exactly"):
        inspect_artifact(_valid_artifact(extra="field"))


def test_rejects_missing_pdf_text_evidences_key():
    with pytest.raises(ValueError, match="exactly"):
        inspect_artifact({})


@pytest.mark.parametrize(
    "field",
    [
        "size_bytes",
        "page_number",
        "extraction_index",
        "evidence_index",
    ],
)
def test_rejects_bool_integer_fields(field):
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(**{field: True}),
            ],
        )
    )

    assert inspection.invalid_record_count == 1


def test_rejects_missing_required_evidence_fields():
    evidence = _valid_evidence()
    del evidence["warnings"]

    inspection = inspect_artifact(
        _valid_artifact(pdf_text_evidences=[evidence])
    )

    assert inspection.invalid_record_count == 1


def test_rejects_extra_non_forbidden_evidence_fields_as_invalid():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(extra="field"),
            ],
        )
    )

    assert inspection.invalid_record_count == 1
    assert inspection.forbidden_field_count == 0


def test_rejects_invalid_warnings_list():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(warnings="No embedded text found."),
            ],
        )
    )

    assert inspection.invalid_record_count == 1
    assert inspection.warning_count == 0


def test_rejects_warnings_list_with_non_string_item():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(warnings=["Warning", 123]),
            ],
        )
    )

    assert inspection.invalid_record_count == 1
    assert inspection.warning_count == 2


def test_counts_forbidden_fields_separately():
    inspection = inspect_artifact(
        _valid_artifact(
            pdf_text_evidences=[
                _valid_evidence(style="cinematic"),
                _valid_evidence(knowledge="not here"),
            ],
        )
    )

    assert inspection.forbidden_field_count == 2
    assert inspection.invalid_record_count == 2


def test_preserves_inspection_only_behavior_no_mutation():
    artifact = _valid_artifact(
        pdf_text_evidences=[
            _valid_evidence(
                content="Raw summary text may appear here.",
            ),
            _valid_evidence(prompt="Do not write prompts here."),
        ],
    )
    original = deepcopy(artifact)

    inspect_artifact(artifact)

    assert artifact == original


def test_rejects_pdf_text_evidences_not_list():
    with pytest.raises(ValueError, match="pdf_text_evidences"):
        inspect_artifact({"pdf_text_evidences": {}})


def test_rejects_non_dict_top_level_artifact():
    with pytest.raises(ValueError, match="object"):
        inspect_artifact([])
