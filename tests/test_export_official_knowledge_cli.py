import json

from rie.knowledge.export_official_knowledge import main


def _write_source_input(path, data):
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
    }
    item.update(overrides)
    return item


def _source_input(items):
    return {
        "official_knowledge_source_items": items,
    }


def test_export_official_knowledge_writes_valid_artifact(tmp_path, capsys):
    input_path = tmp_path / "official-knowledge-source.json"
    output_path = tmp_path / "official-knowledge.json"
    _write_source_input(
        input_path,
        _source_input([
            _item(
                knowledge_id="BK-001",
                title="First",
                content="First official knowledge content.",
            ),
            _item(
                knowledge_id="BK-002",
                title="Second",
                content="Second official knowledge content.",
                source_page=2,
                pdf_evidence_index=1,
                extraction_index=1,
            ),
        ]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert result == 0
    assert output_path.exists()
    assert "Official Knowledge Export" in output
    assert "Total Source Items              : 2" in output
    assert "Exported Official Knowledge Items: 2" in output
    assert f"Output Path                     : {output_path}" in output
    assert set(data) == {"official_knowledge_items"}
    assert data["official_knowledge_items"] == [
        {
            "knowledge_id": "BK-001",
            "source_path": "docs/example_official_knowledge_base.pdf",
            "source_document": "Example Official Knowledge Base",
            "source_section": "Example Section",
            "source_page": 1,
            "title": "First",
            "content": "First official knowledge content.",
            "status": "LOCKED",
            "governance_level": "OFFICIAL SOURCE OF TRUTH",
            "pdf_evidence_index": 0,
            "extraction_index": 0,
            "official_knowledge_index": 0,
        },
        {
            "knowledge_id": "BK-002",
            "source_path": "docs/example_official_knowledge_base.pdf",
            "source_document": "Example Official Knowledge Base",
            "source_section": "Example Section",
            "source_page": 2,
            "title": "Second",
            "content": "Second official knowledge content.",
            "status": "LOCKED",
            "governance_level": "OFFICIAL SOURCE OF TRUTH",
            "pdf_evidence_index": 1,
            "extraction_index": 1,
            "official_knowledge_index": 1,
        },
    ]


def test_export_official_knowledge_preserves_order_and_indexes(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "official-knowledge-source.json"
    output_path = tmp_path / "official-knowledge.json"
    _write_source_input(
        input_path,
        _source_input([
            _item(knowledge_id="BK-003", title="Third"),
            _item(knowledge_id="BK-001", title="First"),
            _item(knowledge_id="BK-002", title="Second"),
        ]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    records = json.loads(
        output_path.read_text(encoding="utf-8")
    )["official_knowledge_items"]

    assert result == 0
    assert [
        record["title"]
        for record in records
    ] == [
        "Third",
        "First",
        "Second",
    ]
    assert [
        record["official_knowledge_index"]
        for record in records
    ] == [0, 1, 2]


def test_export_official_knowledge_missing_optional_fields_become_null(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "official-knowledge-source.json"
    output_path = tmp_path / "official-knowledge.json"
    source_item = _item()
    for field_name in [
        "knowledge_id",
        "source_section",
        "source_page",
        "status",
        "governance_level",
        "pdf_evidence_index",
        "extraction_index",
    ]:
        del source_item[field_name]
    _write_source_input(input_path, _source_input([source_item]))

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    record = json.loads(
        output_path.read_text(encoding="utf-8")
    )["official_knowledge_items"][0]

    assert result == 0
    assert record["knowledge_id"] is None
    assert record["source_section"] is None
    assert record["source_page"] is None
    assert record["status"] is None
    assert record["governance_level"] is None
    assert record["pdf_evidence_index"] is None
    assert record["extraction_index"] is None


def test_export_official_knowledge_preserves_non_ascii_and_newline_content(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "official-knowledge-source.json"
    output_path = tmp_path / "official-knowledge.json"
    content = "Caf\u00e9 official knowledge content.\nSecond line."
    _write_source_input(
        input_path,
        _source_input([_item(content=content)]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    capsys.readouterr()
    raw_json = output_path.read_text(encoding="utf-8")
    record = json.loads(raw_json)["official_knowledge_items"][0]

    assert result == 0
    assert "Caf\u00e9 official knowledge content." in raw_json
    assert "Caf\\u00e9" not in raw_json
    assert record["content"] == content


def test_export_official_knowledge_returns_error_for_missing_input(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "missing.json"
    output_path = tmp_path / "official-knowledge.json"

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Official Knowledge source input not found" in output
    assert not output_path.exists()


def test_export_official_knowledge_returns_error_for_invalid_json(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "official-knowledge-source.json"
    output_path = tmp_path / "official-knowledge.json"
    input_path.write_text("{invalid-json", encoding="utf-8")

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Failed to read Official Knowledge source input" in output
    assert not output_path.exists()


def test_export_official_knowledge_returns_error_for_invalid_source_shape(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "official-knowledge-source.json"
    output_path = tmp_path / "official-knowledge.json"
    _write_source_input(input_path, {"official_knowledge_items": []})

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Malformed Official Knowledge source input" in output
    assert not output_path.exists()


def test_export_official_knowledge_returns_error_for_forbidden_field(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "official-knowledge-source.json"
    output_path = tmp_path / "official-knowledge.json"
    _write_source_input(
        input_path,
        _source_input([_item(prompt="Do not accept.")]),
    )

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "forbidden field" in output
    assert not output_path.exists()


def test_export_official_knowledge_returns_error_for_missing_output_parent(
    tmp_path,
    capsys,
):
    input_path = tmp_path / "official-knowledge-source.json"
    output_path = tmp_path / "missing" / "official-knowledge.json"
    _write_source_input(input_path, _source_input([_item()]))

    result = main([
        str(input_path),
        "--output",
        str(output_path),
    ])

    output = capsys.readouterr().out
    assert result == 1
    assert "Output folder not found" in output
