from dataclasses import dataclass

from src.evidence.evidence import Evidence


@dataclass(frozen=True)
class EvidenceCollection:
    evidences: list[Evidence]