from dataclasses import dataclass

from official_source.official_source_evidence_eligibility_gate import (
    EvidenceEligibilityGateResult,
)


@dataclass(frozen=True)
class EvidenceWorkflowGateResult:
    source_id: str
    workflow_allowed: bool
    requires_review: bool
    reason: str


class EvidenceWorkflowGate:

    @staticmethod
    def check(
        gate_result: EvidenceEligibilityGateResult,
    ) -> EvidenceWorkflowGateResult:
        if not isinstance(gate_result, EvidenceEligibilityGateResult):
            raise TypeError(
                "Evidence workflow gate requires "
                "EvidenceEligibilityGateResult."
            )

        workflow_allowed = (
            gate_result.allowed and not gate_result.requires_review
        )

        return EvidenceWorkflowGateResult(
            source_id=gate_result.source_id,
            workflow_allowed=workflow_allowed,
            requires_review=gate_result.requires_review,
            reason=gate_result.reason,
        )
