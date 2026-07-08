from typing import Any

from knowledge.text_knowledge_builder import TextKnowledgeBuilder
from knowledge.text_knowledge_collection import TextKnowledgeCollection


class TextKnowledgeCollector:

    @staticmethod
    def collect(
        artifact: Any,
    ) -> TextKnowledgeCollection:
        if not isinstance(artifact, dict):
            raise ValueError("Evidence artifact must be an object.")

        evidences = artifact.get("evidences")

        if not isinstance(evidences, list):
            raise ValueError("Evidence artifact evidences must be a list.")

        knowledge_items = []

        for index, evidence_record in enumerate(evidences):
            try:
                knowledge_items.append(
                    TextKnowledgeBuilder.build(
                        evidence_record=evidence_record,
                        evidence_index=index,
                    )
                )
            except ValueError:
                continue

        return TextKnowledgeCollection(
            knowledge_items=knowledge_items,
        )
