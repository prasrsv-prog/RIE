import json

from rie.knowledge.inspect_official_knowledge import main


def _write_artifact(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False),
        encoding="utf-8",
    )


def _item(**overrides):
    item = {
        "knowledge_id": "BK-001",
        "source_path": "docs/example_official_knowledge_base.pdf",
        "source_document": "Example Official Knowledge Base",
        "source_section": "Example Section",
        "source_page": 1,
        "title": "Example Locked Knowledge",
        "content": "Example official knowledge content.",
        "status": "LOCKED",
        "governance_level": "OFFICIAL SOURCE OF TRUTH",
        "pdf_evidence_index": 0,
        "extraction_index": 0,
        "official_knowledge_index": 0,
    }
    item.update(overrides)
    return item


def _artifact(items):
    return {
        "official_knowledge_items": items,
    }


def test_inspect_official_knowledge_valid_artifact_returns_zero(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "official-knowledge.json"
    _write_artifact(artifact_path, _artifact([_item()]))

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "Official Knowledge Inspection" in output
    assert "total_official_knowledge_items: 1" in output
    assert "missing_required_traceability_count: 0" in output
    assert "missing_governance_count: 0" in output
    assert "forbidden_field_count: 0" in output
    assert "index_mismatch_count: 0" in output
    assert "is_valid: true" in output


def test_inspect_official_knowledge_empty_items_is_valid(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "official-knowledge.json"
    _write_artifact(artifact_path, _artifact([]))

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "total_official_knowledge_items: 0" in output
    assert "is_valid: true" in output


def test_inspect_official_knowledge_missing_governance_is_counted_but_valid(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "official-knowledge.json"
    _write_artifact(
        artifact_path,
        _artifact([
            _item(status=None),
            _item(
                knowledge_id="BK-002",
                governance_level="",
                official_knowledge_index=1,
            ),
        ]),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 0
    assert "total_official_knowledge_items: 2" in output
    assert "missing_governance_count: 2" in output
    assert "is_valid: true" in output


def test_inspect_official_knowledge_missing_required_traceability_is_invalid(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "official-knowledge.json"
    _write_artifact(
        artifact_path,
        _artifact([_item(source_document="")]),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "missing_required_traceability_count: 1" in output
    assert "is_valid: false" in output


def test_inspect_official_knowledge_forbidden_field_is_invalid(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "official-knowledge.json"
    _write_artifact(
        artifact_path,
        _artifact([_item(prompt="Do not accept.")]),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "forbidden_field_count: 1" in output
    assert "is_valid: false" in output


def test_inspect_official_knowledge_index_mismatch_is_invalid(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "official-knowledge.json"
    _write_artifact(
        artifact_path,
        _artifact([_item(official_knowledge_index=7)]),
    )

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "index_mismatch_count: 1" in output
    assert "is_valid: false" in output


def test_inspect_official_knowledge_returns_error_for_missing_file(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "missing.json"

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Official Knowledge artifact not found" in output


def test_inspect_official_knowledge_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    artifact_path = tmp_path / "official-knowledge.json"
    artifact_path.write_text("{invalid-json", encoding="utf-8")

    result = main([str(artifact_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read Official Knowledge artifact" in output


def test_inspect_official_knowledge_returns_error_for_directory(
    tmp_path,
    capsys,
):
    result = main([str(tmp_path)])

    output = capsys.readouterr().out
    assert result == 1
    assert "Not a file" in output
