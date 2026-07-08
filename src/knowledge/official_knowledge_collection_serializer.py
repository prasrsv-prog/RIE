import json
from typing import Any

from knowledge.official_knowledge_collection import OfficialKnowledgeCollection


class OfficialKnowledgeCollectionSerializer:

    @staticmethod
    def to_dict(
        collection: OfficialKnowledgeCollection,
    ) -> dict[str, Any]:
        return {
            "official_knowledge_items": [
                {
                    "knowledge_id": item.knowledge_id,
                    "source_path": item.source_path,
                    "source_document": item.source_document,
                    "source_section": item.source_section,
                    "source_page": item.source_page,
                    "title": item.title,
                    "content": item.content,
                    "status": item.status,
                    "governance_level": item.governance_level,
                    "pdf_evidence_index": item.pdf_evidence_index,
                    "extraction_index": item.extraction_index,
                    "official_knowledge_index": (
                        item.official_knowledge_index
                    ),
                }
                for item in collection.official_knowledge_items
            ],
        }

    @staticmethod
    def to_json(
        collection: OfficialKnowledgeCollection,
    ) -> str:
        return json.dumps(
            OfficialKnowledgeCollectionSerializer.to_dict(collection),
            indent=2,
            ensure_ascii=False,
        )
