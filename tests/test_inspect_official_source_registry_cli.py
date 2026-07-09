import json

import pytest

from rie.official_source.inspect_official_source_registry import main


def _item(**overrides):
    item = {
        "source_id": "SRC-001",
        "source_path": "docs/synthetic-registry-source.pdf",
        "source_type": "pdf",
        "document_classification": "project_rulebook",
        "authority_status": "source_of_truth_candidate",
        "lifecycle_status": "locked",
        "evidence_eligibility": "eligible_with_review",
        "version": "v1.0",
        "review_notes": "Synthetic example only.",
    }
    item.update(overrides)
    return item


def _registry(items):
    return {
        "official_sources": items,
    }


def _write_registry(path, data):
    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def test_valid_synthetic_registry_returns_zero(tmp_path, capsys):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(registry_path, _registry([_item()]))

    result = main([str(registry_path)])

    capsys.readouterr()
    assert result == 0


def test_valid_synthetic_registry_prints_total_official_sources(
    tmp_path,
    capsys,
):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(registry_path, _registry([_item(), _item(
        source_id="SRC-002",
        source_type="markdown",
    )]))

    result = main([str(registry_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Official Source Registry Inspection" in output
    assert "total_official_sources: 2" in output


def test_valid_synthetic_registry_prints_aggregate_enum_counts(
    tmp_path,
    capsys,
):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(
                source_id="SRC-001",
                source_type="pdf",
                document_classification="project_rulebook",
                authority_status="source_of_truth_candidate",
                lifecycle_status="locked",
                evidence_eligibility="eligible_with_review",
            ),
            _item(
                source_id="SRC-002",
                source_type="markdown",
                document_classification="working_note",
                authority_status="reference",
                lifecycle_status="superseded",
                evidence_eligibility="not_eligible",
            ),
        ]),
    )

    result = main([str(registry_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "source_type:" in output
    assert "pdf: 1" in output
    assert "markdown: 1" in output
    assert "document_classification:" in output
    assert "project_rulebook: 1" in output
    assert "working_note: 1" in output
    assert "authority_status:" in output
    assert "source_of_truth_candidate: 1" in output
    assert "reference: 1" in output
    assert "lifecycle_status:" in output
    assert "locked: 1" in output
    assert "superseded: 1" in output
    assert "evidence_eligibility:" in output
    assert "eligible_with_review: 1" in output
    assert "not_eligible: 1" in output


def test_output_does_not_include_source_path(tmp_path, capsys):
    registry_path = tmp_path / "official-source-registry.json"
    source_path = "docs/synthetic-source-path-that-must-not-print.pdf"
    _write_registry(registry_path, _registry([_item(source_path=source_path)]))

    result = main([str(registry_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert source_path not in output
    assert "source_path" not in output


def test_missing_argument_exits_non_zero_through_argparse():
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code != 0


def test_missing_registry_file_returns_one(tmp_path, capsys):
    registry_path = tmp_path / "missing-registry.json"

    result = main([str(registry_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to inspect Official Source Registry" in output


def test_invalid_json_returns_one(tmp_path, capsys):
    registry_path = tmp_path / "official-source-registry.json"
    registry_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(registry_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to inspect Official Source Registry" in output


def test_invalid_registry_shape_returns_one(tmp_path, capsys):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(registry_path, [])

    result = main([str(registry_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to inspect Official Source Registry" in output


def test_nonexistent_source_path_inside_registry_still_succeeds(
    tmp_path,
    capsys,
):
    registry_path = tmp_path / "official-source-registry.json"
    _write_registry(
        registry_path,
        _registry([
            _item(source_path="docs/not-a-real-synthetic-source.pdf"),
        ]),
    )

    result = main([str(registry_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "total_official_sources: 1" in output


def test_no_real_rsv_locked_content_is_used(tmp_path):
    registry_path = tmp_path / "official-source-registry.json"
    registry = _registry([_item()])
    _write_registry(registry_path, registry)

    raw_registry = registry_path.read_text(encoding="utf-8")
    assert "synthetic" in raw_registry
    assert "RSV" not in raw_registry
    assert "Creative Logic Specification" not in raw_registry
    assert "Official Knowledge Base" not in raw_registry
