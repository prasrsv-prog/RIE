from dataclasses import dataclass


@dataclass(frozen=True)
class TextPromptCandidate:
    source_path: str
    content: str
    size_bytes: int
    evidence_index: int
    knowledge_index: int
