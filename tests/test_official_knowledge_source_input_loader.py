from copy import deepcopy

import pytest

from knowledge.official_knowledge_source_input_loader import (
    OfficialKnowledgeSourceInputLoader,
)
from knowledge.official_knowledge_source_item import (
    OfficialKnowledgeSourceItem,
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


def test_loads_one_valid_official_knowledge_source_item():
    items = OfficialKnowledgeSourceInputLoader.load(
        _source_input([_item()]),
    )

    assert len(items) == 1
    assert isinstance(items[0], OfficialKnowledgeSourceItem)
    assert items[0].knowledge_id == "BK-001"
    assert items[0].source_path == (
        "docs/example_official_knowledge_base.pdf"
    )
    assert items[0].source_document == "Example Official Knowledge Base"
    assert items[0].source_section == "Example Section"
    assert items[0].source_page == 1
    assert items[0].title == "Example Locked Knowledge"
    assert items[0].content == "Example official knowledge content."
    assert items[0].status == "LOCKED"
    assert items[0].governance_level == "OFFICIAL SOURCE OF TRUTH"
    assert items[0].pdf_evidence_index == 0
    assert items[0].extraction_index == 0


def test_multiple_valid_items_preserve_order():
    items = OfficialKnowledgeSourceInputLoader.load(
        _source_input([
            _item(knowledge_id="BK-001", title="First"),
            _item(knowledge_id="BK-002", title="Second"),
            _item(knowledge_id="BK-003", title="Third"),
        ]),
    )

    assert [
        item.title
        for item in items
    ] == [
        "First",
        "Second",
        "Third",
    ]
    assert [
        item.knowledge_id
        for item in items
    ] == [
        "BK-001",
        "BK-002",
        "BK-003",
    ]


def test_empty_official_knowledge_source_items_list_returns_empty_list():
    assert OfficialKnowledgeSourceInputLoader.load(
        _source_input([]),
    ) == []


def test_omitted_optional_fields_become_none():
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

    items = OfficialKnowledgeSourceInputLoader.load(
        _source_input([source_item]),
    )

    assert items[0].knowledge_id is None
    assert items[0].source_section is None
    assert items[0].source_page is None
    assert items[0].status is None
    assert items[0].governance_level is None
    assert items[0].pdf_evidence_index is None
    assert items[0].extraction_index is None


def test_provided_none_optional_fields_remain_none():
    items = OfficialKnowledgeSourceInputLoader.load(
        _source_input([
            _item(
                knowledge_id=None,
                source_section=None,
                source_page=None,
                status=None,
                governance_level=None,
                pdf_evidence_index=None,
                extraction_index=None,
            ),
        ]),
    )

    assert items[0].knowledge_id is None
    assert items[0].source_section is None
    assert items[0].source_page is None
    assert items[0].status is None
    assert items[0].governance_level is None
    assert items[0].pdf_evidence_index is None
    assert items[0].extraction_index is None


def test_missing_required_fields_fail_clearly():
    for field_name in [
        "source_path",
        "source_document",
        "title",
        "content",
    ]:
        source_item = _item()
        del source_item[field_name]

        with pytest.raises(ValueError, match=field_name):
            OfficialKnowledgeSourceInputLoader.load(
                _source_input([source_item]),
            )


def test_empty_required_string_fields_fail_clearly():
    for field_name in [
        "source_path",
        "source_document",
        "title",
        "content",
    ]:
        source_item = _item(**{field_name: ""})

        with pytest.raises(ValueError, match=field_name):
            OfficialKnowledgeSourceInputLoader.load(
                _source_input([source_item]),
            )


def test_top_level_input_that_is_not_a_dict_fails():
    with pytest.raises(ValueError, match="object"):
        OfficialKnowledgeSourceInputLoader.load([])


def test_missing_official_knowledge_source_items_key_fails():
    with pytest.raises(ValueError, match="official_knowledge_source_items"):
        OfficialKnowledgeSourceInputLoader.load({})


def test_unknown_top_level_key_fails():
    with pytest.raises(ValueError, match="official_knowledge_source_items"):
        OfficialKnowledgeSourceInputLoader.load(
            {
                "official_knowledge_source_items": [],
                "unknown": [],
            },
        )


def test_official_knowledge_source_items_that_is_not_a_list_fails():
    with pytest.raises(ValueError, match="list"):
        OfficialKnowledgeSourceInputLoader.load(
            {
                "official_knowledge_source_items": {},
            },
        )


def test_non_dict_item_fails():
    with pytest.raises(ValueError, match="object"):
        OfficialKnowledgeSourceInputLoader.load(
            _source_input(["not an item"]),
        )


def test_unknown_item_field_fails():
    with pytest.raises(ValueError, match="unknown field"):
        OfficialKnowledgeSourceInputLoader.load(
            _source_input([_item(unexpected="Do not accept.")]),
        )


def test_forbidden_item_field_fails():
    with pytest.raises(ValueError, match="forbidden field"):
        OfficialKnowledgeSourceInputLoader.load(
            _source_input([_item(prompt="Do not accept.")]),
        )


def test_bool_values_for_integer_fields_fail():
    for field_name in [
        "source_page",
        "pdf_evidence_index",
        "extraction_index",
    ]:
        with pytest.raises(ValueError, match=field_name):
            OfficialKnowledgeSourceInputLoader.load(
                _source_input([_item(**{field_name: True})]),
            )


def test_non_int_non_none_values_for_integer_fields_fail():
    for field_name in [
        "source_page",
        "pdf_evidence_index",
        "extraction_index",
    ]:
        with pytest.raises(ValueError, match=field_name):
            OfficialKnowledgeSourceInputLoader.load(
                _source_input([_item(**{field_name: "1"})]),
            )


def test_non_ascii_and_newline_content_are_preserved():
    content = "Caf\u00e9 official knowledge content.\nSecond line."

    items = OfficialKnowledgeSourceInputLoader.load(
        _source_input([_item(content=content)]),
    )

    assert items[0].content == content


def test_loader_does_not_mutate_input():
    source_input = _source_input([_item()])
    original_source_input = deepcopy(source_input)

    OfficialKnowledgeSourceInputLoader.load(source_input)

    assert source_input == original_source_input
