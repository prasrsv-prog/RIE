from rie.application.asset import Asset

from src.collection.evidence_collection import EvidenceCollection
from src.evidence.evidence_builder import EvidenceBuilder


class EvidenceCollector:
    
    @staticmethod
    def collect(
        assets: list[Asset]
    ) -> EvidenceCollection:
        
        evidences = []

        for asset in assets:
            evidence = EvidenceBuilder.build(asset)
            evidences.append(evidence)

        return EvidenceCollection(
                evidences=evidences
        )