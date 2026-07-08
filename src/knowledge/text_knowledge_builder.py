from typing import Any

from knowledge.text_knowledge import TextKnowledge


REQUIRED_EVIDENCE_FIELDS = {
    "source_path",
    "content",
    "size_bytes",
}


class TextKnowledgeBuilder:

    @staticmethod
    def build(
        evidence_record: Any,
        evidence_index: int,
    ) -> TextKnowledge:
        if not isinstance(evidence_record, dict):
            raise ValueError("Evidence record must be an object.")

        if set(evidence_record) != REQUIRED_EVIDENCE_FIELDS:
            raise ValueError(
                "Evidence record must contain exactly source_path, "
                "content, and size_bytes."
            )

        source_path = evidence_record["source_path"]
        content = evidence_record["content"]
        size_bytes = evidence_record["size_bytes"]

        if not isinstance(source_path, str):
            raise ValueError("Evidence record source_path must be a string.")

        if not isinstance(content, str):
            raise ValueError("Evidence record content must be a string.")

        if not isinstance(size_bytes, int) or isinstance(size_bytes, bool):
            raise ValueError("Evidence record size_bytes must be an integer.")

        return TextKnowledge(
            source_path=source_path,
            content=content,
            size_bytes=size_bytes,
            evidence_index=evidence_index,
        )
