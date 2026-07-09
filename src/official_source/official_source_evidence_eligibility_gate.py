from dataclasses import dataclass

from official_source.official_source_evidence_eligibility_policy import (
    EvidenceEligibilityDecision,
)


@dataclass(frozen=True)
class EvidenceEligibilityGateResult:
    source_id: str
    allowed: bool
    requires_review: bool
    reason: str


class EvidenceEligibilityGate:

    @staticmethod
    def check(
        decision: EvidenceEligibilityDecision,
    ) -> EvidenceEligibilityGateResult:
        if not isinstance(decision, EvidenceEligibilityDecision):
            raise TypeError(
                "Evidence eligibility gate requires "
                "EvidenceEligibilityDecision."
            )

        allowed = decision.allowed and not decision.requires_review
        reason = decision.reason

        if reason.strip() == "":
            reason = "Evidence eligibility gate decision has no reason."

        return EvidenceEligibilityGateResult(
            source_id=decision.source_id,
            allowed=allowed,
            requires_review=decision.requires_review,
            reason=reason,
        )
