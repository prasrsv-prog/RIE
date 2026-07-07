from dataclasses import dataclass

from analysis.repository_statistics import RepositoryStatistics
from collection.evidence_collection import EvidenceCollection
from report.repository_insight import RepositoryInsight


@dataclass(frozen=True)
class RepositoryReport:
    evidences: EvidenceCollection
    statistics: RepositoryStatistics
    insight: RepositoryInsight