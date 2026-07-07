from dataclasses import dataclass

from evidence.evidence import Evidence


@dataclass(frozen=True)
class EvidenceCollection:
    evidences: list[Evidence]