from dataclasses import dataclass

from src.collection.evidence_collection import EvidenceCollection
from src.analysis.repository_statistics import RepositoryStatistics


@dataclass(frozen=True)
class RepositoryReport:
    evidences: EvidenceCollection
    statistics: RepositoryStatistics