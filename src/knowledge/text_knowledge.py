from dataclasses import dataclass


@dataclass(frozen=True)
class TextKnowledge:
    source_path: str
    content: str
    size_bytes: int
    evidence_index: int
