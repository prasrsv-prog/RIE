from dataclasses import dataclass

from knowledge.text_knowledge import TextKnowledge


@dataclass(frozen=True)
class TextKnowledgeCollection:
    knowledge_items: list[TextKnowledge]
