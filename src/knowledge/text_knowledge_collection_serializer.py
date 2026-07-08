import json
from typing import Any

from knowledge.text_knowledge_collection import TextKnowledgeCollection


def to_json(
    collection: TextKnowledgeCollection,
) -> str:
    return json.dumps(
        to_dict(collection),
        indent=2,
        ensure_ascii=False,
    )


def to_dict(
    collection: TextKnowledgeCollection,
) -> dict[str, Any]:
    return {
        "knowledge_items": [
            {
                "source_path": knowledge.source_path,
                "content": knowledge.content,
                "size_bytes": knowledge.size_bytes,
                "evidence_index": knowledge.evidence_index,
            }
            for knowledge in collection.knowledge_items
        ],
    }
