from dataclasses import dataclass

from official_source.official_source import EvidenceEligibility
from official_source.official_source import OfficialSource


@dataclass(frozen=True)
class EvidenceEligibilityDecision:
    source_id: str
    evidence_eligibility: EvidenceEligibility
    allowed: bool
    requires_review: bool
    reason: str


class OfficialSourceEvidenceEligibilityPolicy:

    @staticmethod
    def evaluate(
        source: OfficialSource,
    ) -> EvidenceEligibilityDecision:
        evidence_eligibility = source.evidence_eligibility

        if evidence_eligibility == EvidenceEligibility.ELIGIBLE:
            allowed = True
            requires_review = False
            reason = "Source is eligible for evidence workflow."
        elif evidence_eligibility == EvidenceEligibility.ELIGIBLE_WITH_REVIEW:
            allowed = False
            requires_review = True
            reason = "Source requires manual review before evidence workflow."
        elif evidence_eligibility == EvidenceEligibility.NOT_ELIGIBLE:
            allowed = False
            requires_review = False
            reason = "Source is not eligible for evidence workflow."
        else:
            allowed = False
            requires_review = False
            reason = "Source evidence eligibility is unknown."

        return EvidenceEligibilityDecision(
            source_id=source.source_id,
            evidence_eligibility=evidence_eligibility,
            allowed=allowed,
            requires_review=requires_review,
            reason=reason,
        )
