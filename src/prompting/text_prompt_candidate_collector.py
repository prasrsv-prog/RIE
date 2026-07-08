from typing import Any

from prompting.text_prompt_candidate_builder import (
    TextPromptCandidateBuilder,
)
from prompting.text_prompt_candidate_collection import (
    TextPromptCandidateCollection,
)


class TextPromptCandidateCollector:

    @staticmethod
    def collect(
        artifact: Any,
    ) -> TextPromptCandidateCollection:
        if not isinstance(artifact, dict):
            raise ValueError("Knowledge artifact must be an object.")

        knowledge_items = artifact.get("knowledge_items")

        if not isinstance(knowledge_items, list):
            raise ValueError("Knowledge artifact knowledge_items must be a list.")

        prompt_candidates = []

        for index, knowledge_record in enumerate(knowledge_items):
            try:
                prompt_candidates.append(
                    TextPromptCandidateBuilder.build(
                        knowledge_record=knowledge_record,
                        knowledge_index=index,
                    )
                )
            except ValueError:
                continue

        return TextPromptCandidateCollection(
            prompt_candidates=prompt_candidates,
        )
