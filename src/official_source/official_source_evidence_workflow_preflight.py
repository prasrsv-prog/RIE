from dataclasses import dataclass

from official_source.official_source_evidence_workflow_gate import (
    EvidenceWorkflowGateResult,
)


@dataclass(frozen=True)
class EvidenceWorkflowPreflightResult:
    source_id: str
    evidence_collection_allowed: bool
    requires_review: bool
    reason: str


class EvidenceWorkflowPreflight:

    @staticmethod
    def check(
        gate_result: EvidenceWorkflowGateResult,
    ) -> EvidenceWorkflowPreflightResult:
        if not isinstance(gate_result, EvidenceWorkflowGateResult):
            raise TypeError(
                "Evidence workflow preflight requires "
                "EvidenceWorkflowGateResult."
            )

        return EvidenceWorkflowPreflightResult(
            source_id=gate_result.source_id,
            evidence_collection_allowed=gate_result.workflow_allowed
            and not gate_result.requires_review,
            requires_review=gate_result.requires_review,
            reason=gate_result.reason,
        )