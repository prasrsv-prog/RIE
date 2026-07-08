from dataclasses import dataclass

from knowledge.official_knowledge_item import OfficialKnowledgeItem


@dataclass(frozen=True)
class OfficialKnowledgeCollection:
    official_knowledge_items: list[OfficialKnowledgeItem]
