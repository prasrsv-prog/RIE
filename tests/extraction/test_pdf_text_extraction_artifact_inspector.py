from copy import deepcopy

import pytest

from rie.extraction.pdf_text_extraction_artifact_inspector import (
    inspect_artifact,
)


def _valid_page(**overrides):
    page = {
        "source_path": "spec.pdf",
        "size_bytes": 123,
        "page_number": 1,
        "extraction_index": 0,
        "extraction_method": "embedded_text",
        "content": "Page text",
        "warnings": [],
    }
    page.update(overrides)
    return page


def _valid_asset_error(**overrides):
    asset_error = {
        "source_path": "broken.pdf",
        "size_bytes": 321,
        "error": "Cannot read PDF.",
    }
    asset_error.update(overrides)
    return asset_error


def _valid_artifact(**overrides):
    artifact = {
        "root": "D:\\SPEC",
        "total_pdf_assets": 1,
        "total_page_extractions": 1,
        "failed_pdf_assets": 0,
        "page_extractions": [
            _valid_page(),
        ],
        "asset_errors": [],
    }
    artifact.update(overrides)
    return artifact


def test_counts_total_pdf_assets():
    inspection = inspect_artifact(
        _valid_artifact(total_pdf_assets=3)
    )

    assert inspection.total_pdf_assets == 3


def test_counts_total_page_extractions():
    inspection = inspect_artifact(
        _valid_artifact(total_page_extractions=2)
    )

    assert inspection.total_page_extractions == 2


def test_counts_failed_pdf_assets():
    inspection = inspect_artifact(
        _valid_artifact(failed_pdf_assets=1)
    )

    assert inspection.failed_pdf_assets == 1


def test_counts_empty_content_pages():
    inspection = inspect_artifact(
        _valid_artifact(
            page_extractions=[
                _valid_page(content=""),
                _valid_page(content="   "),
            ],
            total_page_extractions=2,
        )
    )

    assert inspection.empty_content_page_count == 1


def test_counts_page_warnings():
    inspection = inspect_artifact(
        _valid_artifact(
            page_extractions=[
                _valid_page(
                    warnings=[
                        "No embedded text found.",
                        "Page text extraction warning.",
                    ],
                ),
            ],
        )
    )

    assert inspection.page_warning_count == 2


def test_counts_asset_errors():
    inspection = inspect_artifact(
        _valid_artifact(
            asset_errors=[
                _valid_asset_error(),
                _valid_asset_error(source_path="other.pdf"),
            ],
            failed_pdf_assets=2,
        )
    )

    assert inspection.asset_error_count == 2


def test_counts_invalid_page_extraction_records():
    inspection = inspect_artifact(
        _valid_artifact(
            page_extractions=[
                "not a page",
                _valid_page(source_path=123),
            ],
            total_page_extractions=2,
        )
    )

    assert inspection.invalid_page_extraction_record_count == 2


def test_counts_invalid_asset_error_records():
    inspection = inspect_artifact(
        _valid_artifact(
            asset_errors=[
                "not an asset error",
                _valid_asset_error(error=123),
            ],
            failed_pdf_assets=2,
        )
    )

    assert inspection.invalid_asset_error_record_count == 2


def test_counts_forbidden_fields():
    inspection = inspect_artifact(
        _valid_artifact(
            page_extractions=[
                _valid_page(prompt="Do not write prompts here."),
            ],
            asset_errors=[
                _valid_asset_error(summary="Do not summarize."),
            ],
        )
    )

    assert inspection.forbidden_field_count == 2
    assert inspection.invalid_page_extraction_record_count == 1
    assert inspection.invalid_asset_error_record_count == 1


def test_accepts_exact_valid_top_level_fields_only():
    inspection = inspect_artifact(_valid_artifact())

    assert inspection.invalid_page_extraction_record_count == 0
    assert inspection.invalid_asset_error_record_count == 0
    assert inspection.forbidden_field_count == 0


def test_rejects_extra_top_level_fields():
    artifact = _valid_artifact(extra="field")

    with pytest.raises(ValueError, match="exactly"):
        inspect_artifact(artifact)


def test_rejects_bool_for_top_level_integer_fields():
    for field in (
        "total_pdf_assets",
        "total_page_extractions",
        "failed_pdf_assets",
    ):
        artifact = _valid_artifact(**{field: True})

        with pytest.raises(ValueError, match="integer"):
            inspect_artifact(artifact)


def test_rejects_bool_for_page_integer_fields():
    for field in (
        "size_bytes",
        "page_number",
        "extraction_index",
    ):
        inspection = inspect_artifact(
            _valid_artifact(
                page_extractions=[
                    _valid_page(**{field: False}),
                ],
            )
        )

        assert inspection.invalid_page_extraction_record_count == 1


def test_rejects_bool_for_asset_error_integer_fields():
    inspection = inspect_artifact(
        _valid_artifact(
            asset_errors=[
                _valid_asset_error(size_bytes=True),
            ],
            failed_pdf_assets=1,
        )
    )

    assert inspection.invalid_asset_error_record_count == 1


def test_rejects_missing_required_page_fields():
    page = _valid_page()
    del page["warnings"]

    inspection = inspect_artifact(
        _valid_artifact(page_extractions=[page])
    )

    assert inspection.invalid_page_extraction_record_count == 1


def test_rejects_extra_non_forbidden_page_fields_as_invalid():
    inspection = inspect_artifact(
        _valid_artifact(
            page_extractions=[
                _valid_page(extra="field"),
            ],
        )
    )

    assert inspection.invalid_page_extraction_record_count == 1
    assert inspection.forbidden_field_count == 0


def test_rejects_invalid_warnings_list():
    inspection = inspect_artifact(
        _valid_artifact(
            page_extractions=[
                _valid_page(warnings="No embedded text found."),
            ],
        )
    )

    assert inspection.invalid_page_extraction_record_count == 1
    assert inspection.page_warning_count == 0


def test_rejects_warnings_list_with_non_string_item():
    inspection = inspect_artifact(
        _valid_artifact(
            page_extractions=[
                _valid_page(warnings=["Warning", 123]),
            ],
        )
    )

    assert inspection.invalid_page_extraction_record_count == 1
    assert inspection.page_warning_count == 2


def test_rejects_missing_required_asset_error_fields():
    asset_error = _valid_asset_error()
    del asset_error["error"]

    inspection = inspect_artifact(
        _valid_artifact(
            asset_errors=[asset_error],
            failed_pdf_assets=1,
        )
    )

    assert inspection.invalid_asset_error_record_count == 1


def test_rejects_extra_non_forbidden_asset_error_fields_as_invalid():
    inspection = inspect_artifact(
        _valid_artifact(
            asset_errors=[
                _valid_asset_error(extra="field"),
            ],
            failed_pdf_assets=1,
        )
    )

    assert inspection.invalid_asset_error_record_count == 1
    assert inspection.forbidden_field_count == 0


def test_counts_forbidden_fields_separately():
    inspection = inspect_artifact(
        _valid_artifact(
            page_extractions=[
                _valid_page(style="cinematic"),
            ],
            asset_errors=[
                _valid_asset_error(knowledge="not here"),
            ],
            failed_pdf_assets=1,
        )
    )

    assert inspection.forbidden_field_count == 2
    assert inspection.invalid_page_extraction_record_count == 1
    assert inspection.invalid_asset_error_record_count == 1


def test_preserves_inspection_only_behavior_no_mutation():
    artifact = _valid_artifact(
        page_extractions=[
            _valid_page(content="Raw summary text may appear here."),
            _valid_page(prompt="Do not write prompts here."),
        ],
        asset_errors=[
            _valid_asset_error(),
        ],
        failed_pdf_assets=1,
    )
    original = deepcopy(artifact)

    inspect_artifact(artifact)

    assert artifact == original


def test_rejects_missing_required_top_level_key():
    artifact = _valid_artifact()
    del artifact["asset_errors"]

    with pytest.raises(ValueError, match="exactly"):
        inspect_artifact(artifact)


def test_rejects_page_extractions_not_list():
    artifact = _valid_artifact(page_extractions={})

    with pytest.raises(ValueError, match="page_extractions"):
        inspect_artifact(artifact)


def test_rejects_asset_errors_not_list():
    artifact = _valid_artifact(asset_errors={})

    with pytest.raises(ValueError, match="asset_errors"):
        inspect_artifact(artifact)


def test_rejects_non_dict_top_level_artifact():
    with pytest.raises(ValueError, match="object"):
        inspect_artifact([])
