import json
from typing import Any

from prompting.text_prompt_candidate_collection import (
    TextPromptCandidateCollection,
)


class TextPromptCandidateCollectionSerializer:

    @staticmethod
    def to_dict(
        collection: TextPromptCandidateCollection,
    ) -> dict[str, Any]:
        return {
            "prompt_candidates": [
                {
                    "source_path": candidate.source_path,
                    "content": candidate.content,
                    "size_bytes": candidate.size_bytes,
                    "evidence_index": candidate.evidence_index,
                    "knowledge_index": candidate.knowledge_index,
                }
                for candidate in collection.prompt_candidates
            ],
        }

    @staticmethod
    def to_json(
        collection: TextPromptCandidateCollection,
    ) -> str:
        return json.dumps(
            TextPromptCandidateCollectionSerializer.to_dict(collection),
            indent=2,
            ensure_ascii=False,
        )
