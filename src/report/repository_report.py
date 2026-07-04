from dataclasses import dataclass

from src.analysis.repository_statistics import RepositoryStatistics
from src.collection.evidence_collection import EvidenceCollection
from src.report.repository_insight import RepositoryInsight


@dataclass(frozen=True)
class RepositoryReport:
    evidences: EvidenceCollection
    statistics: RepositoryStatistics
    insight: RepositoryInsight