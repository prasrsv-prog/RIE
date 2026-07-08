from knowledge.official_knowledge_collection import OfficialKnowledgeCollection
from knowledge.official_knowledge_item import OfficialKnowledgeItem
from knowledge.official_knowledge_source_item import OfficialKnowledgeSourceItem


class OfficialKnowledgeCollector:

    @staticmethod
    def collect(
        source_items: list[OfficialKnowledgeSourceItem],
    ) -> OfficialKnowledgeCollection:
        official_knowledge_items = [
            OfficialKnowledgeItem(
                knowledge_id=source_item.knowledge_id,
                source_path=source_item.source_path,
                source_document=source_item.source_document,
                source_section=source_item.source_section,
                source_page=source_item.source_page,
                title=source_item.title,
                content=source_item.content,
                status=source_item.status,
                governance_level=source_item.governance_level,
                pdf_evidence_index=source_item.pdf_evidence_index,
                extraction_index=source_item.extraction_index,
                official_knowledge_index=index,
            )
            for index, source_item in enumerate(source_items)
        ]

        return OfficialKnowledgeCollection(
            official_knowledge_items=official_knowledge_items,
        )
