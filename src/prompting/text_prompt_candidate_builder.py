from typing import Any

from prompting.text_prompt_candidate import TextPromptCandidate


REQUIRED_KNOWLEDGE_FIELDS = {
    "source_path",
    "content",
    "size_bytes",
    "evidence_index",
}


class TextPromptCandidateBuilder:

    @staticmethod
    def build(
        knowledge_record: Any,
        knowledge_index: int,
    ) -> TextPromptCandidate:
        if not isinstance(knowledge_record, dict):
            raise ValueError("Knowledge record must be an object.")

        if set(knowledge_record) != REQUIRED_KNOWLEDGE_FIELDS:
            raise ValueError(
                "Knowledge record must contain exactly source_path, "
                "content, size_bytes, and evidence_index."
            )

        source_path = knowledge_record["source_path"]
        content = knowledge_record["content"]
        size_bytes = knowledge_record["size_bytes"]
        evidence_index = knowledge_record["evidence_index"]

        if not isinstance(source_path, str):
            raise ValueError("Knowledge record source_path must be a string.")

        if not isinstance(content, str):
            raise ValueError("Knowledge record content must be a string.")

        if not isinstance(size_bytes, int) or isinstance(size_bytes, bool):
            raise ValueError("Knowledge record size_bytes must be an integer.")

        if (
            not isinstance(evidence_index, int)
            or isinstance(evidence_index, bool)
        ):
            raise ValueError(
                "Knowledge record evidence_index must be an integer."
            )

        if (
            not isinstance(knowledge_index, int)
            or isinstance(knowledge_index, bool)
        ):
            raise ValueError("knowledge_index must be an integer.")

        return TextPromptCandidate(
            source_path=source_path,
            content=content,
            size_bytes=size_bytes,
            evidence_index=evidence_index,
            knowledge_index=knowledge_index,
        )
