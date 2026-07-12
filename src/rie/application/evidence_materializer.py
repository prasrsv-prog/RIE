"""Pure accepted-Evidence materialization contracts and compatibility service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from rie.application.evidence_candidate import EvidenceCandidate
from rie.application.evidence_candidate_snapshot import (
    EvidenceCandidateSnapshotResult,
    calculate_evidence_candidate_snapshot,
)
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceDiagnostic,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.evidence_identity import (
    EVIDENCE_IDENTITY_POLICY_ID,
    EVIDENCE_IDENTITY_POLICY_VERSION,
    EvidenceIdentityResult,
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)


MATERIALIZATION_DECISION_MATERIALIZED = "materialized"
MATERIALIZATION_DECISION_REJECTED = "rejected"

MATERIALIZATION_REJECTION_REASON_CODES = (
    "candidate_has_errors",
    "unsupported_source_checksum_algorithm",
    "candidate_snapshot_mismatch",
    "candidate_contract_version_mismatch",
    "candidate_source_id_mismatch",
    "candidate_source_type_mismatch",
    "candidate_source_authority_mismatch",
    "candidate_source_lifecycle_mismatch",
    "candidate_source_reference_mismatch",
    "candidate_source_digest_mismatch",
    "candidate_producer_name_mismatch",
    "candidate_producer_version_mismatch",
    "candidate_producer_contract_mismatch",
    "candidate_payload_type_mismatch",
    "candidate_payload_value_mismatch",
    "candidate_locator_value_mismatch",
    "candidate_collection_id_mismatch",
    "candidate_observed_at_mismatch",
    "eligibility_not_eligible",
    "eligibility_candidate_digest_mismatch",
    "eligibility_source_id_mismatch",
    "identity_result_mismatch",
    "identity_policy_mismatch",
    "materialization_context_invalid",
    "diagnostics_invalid",
    "request_invalid",
)

_ALLOWED_REJECTION_REASON_CODES = frozenset(
    MATERIALIZATION_REJECTION_REASON_CODES
)

_REASON_FIELDS = {
    "candidate_has_errors": "candidate.errors",
    "unsupported_source_checksum_algorithm": (
        "candidate.source_checksum_algorithm"
    ),
    "candidate_snapshot_mismatch": "candidate_snapshot_result",
    "candidate_contract_version_mismatch": (
        "candidate.candidate_contract_version"
    ),
    "candidate_source_id_mismatch": "snapshot.source_snapshot.source_id",
    "candidate_source_type_mismatch": "snapshot.source_snapshot.source_type",
    "candidate_source_authority_mismatch": (
        "snapshot.source_snapshot.authority_status"
    ),
    "candidate_source_lifecycle_mismatch": (
        "snapshot.source_snapshot.lifecycle_status"
    ),
    "candidate_source_reference_mismatch": (
        "snapshot.source_snapshot.source_path"
    ),
    "candidate_source_digest_mismatch": (
        "snapshot.source_snapshot.source_content_digest"
    ),
    "candidate_producer_name_mismatch": (
        "snapshot.producer_snapshot.producer_name"
    ),
    "candidate_producer_version_mismatch": (
        "snapshot.producer_snapshot.producer_version"
    ),
    "candidate_producer_contract_mismatch": (
        "snapshot.producer_snapshot.producer_contract_version"
    ),
    "candidate_payload_type_mismatch": "snapshot.factual_payload.payload_type",
    "candidate_payload_value_mismatch": "snapshot.factual_payload.payload",
    "candidate_locator_value_mismatch": (
        "snapshot.factual_payload.locator.locator_value"
    ),
    "candidate_collection_id_mismatch": "snapshot.provenance.collection_id",
    "candidate_observed_at_mismatch": "snapshot.provenance.observed_at",
    "eligibility_not_eligible": "eligibility_result.decision",
    "eligibility_candidate_digest_mismatch": (
        "eligibility_result.candidate_snapshot_digest"
    ),
    "eligibility_source_id_mismatch": "eligibility_result.source_id",
    "identity_result_mismatch": "identity_result",
    "identity_policy_mismatch": "identity_result.identity_policy_id",
    "materialization_context_invalid": "context",
    "diagnostics_invalid": "snapshot.diagnostics",
    "request_invalid": "request",
}


def _require_exact_type(
    value: object,
    expected_type: type[object],
    field_name: str,
) -> None:
    if type(value) is not expected_type:
        raise ValueError(
            f"{field_name} must be an exact {expected_type.__name__}"
        )


def _require_non_empty_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_timezone_aware_datetime(
    value: object,
    field_name: str,
) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _require_diagnostics(
    value: object,
    field_name: str,
) -> None:
    if type(value) is not tuple:
        raise ValueError(f"{field_name} must be a tuple")
    for index, item in enumerate(value):
        _require_exact_type(
            item,
            EvidenceDiagnostic,
            f"{field_name}[{index}]",
        )


def _require_reason_codes(
    value: object,
    *,
    allow_empty: bool,
) -> None:
    if type(value) is not tuple:
        raise ValueError("reason_codes must be a tuple")
    if not allow_empty and not value:
        raise ValueError("reason_codes must not be empty")
    if len(set(value)) != len(value):
        raise ValueError("reason_codes must not contain duplicates")
    for index, reason_code in enumerate(value):
        _require_non_empty_string(
            reason_code,
            f"reason_codes[{index}]",
        )
        if reason_code not in _ALLOWED_REJECTION_REASON_CODES:
            raise ValueError(
                f"reason_codes[{index}] is not an approved reason code"
            )
    expected_order = tuple(
        reason_code
        for reason_code in MATERIALIZATION_REJECTION_REASON_CODES
        if reason_code in value
    )
    if value != expected_order:
        raise ValueError("reason_codes must use deterministic approved order")


@dataclass(frozen=True)
class EvidenceMaterializationSnapshot:
    accepted_evidence_contract_version: str
    source_snapshot: EvidenceSourceSnapshot
    producer_snapshot: EvidenceProducerSnapshot
    factual_payload: EvidencePayload
    provenance: EvidenceProvenance
    diagnostics: tuple[EvidenceDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_non_empty_string(
            self.accepted_evidence_contract_version,
            "accepted_evidence_contract_version",
        )
        _require_exact_type(
            self.source_snapshot,
            EvidenceSourceSnapshot,
            "source_snapshot",
        )
        _require_exact_type(
            self.producer_snapshot,
            EvidenceProducerSnapshot,
            "producer_snapshot",
        )
        _require_exact_type(
            self.factual_payload,
            EvidencePayload,
            "factual_payload",
        )
        _require_exact_type(
            self.provenance,
            EvidenceProvenance,
            "provenance",
        )
        _require_diagnostics(self.diagnostics, "diagnostics")


@dataclass(frozen=True)
class EvidenceMaterializationContext:
    materializer_id: str
    materializer_version: str
    materialized_at: datetime
    acceptance_record_id: str
    accepted_by: str
    acceptance_reason: str
    review_record_id: str

    def __post_init__(self) -> None:
        for field_name in (
            "materializer_id",
            "materializer_version",
            "acceptance_record_id",
            "accepted_by",
            "acceptance_reason",
            "review_record_id",
        ):
            _require_non_empty_string(
                getattr(self, field_name),
                field_name,
            )
        _require_timezone_aware_datetime(
            self.materialized_at,
            "materialized_at",
        )


@dataclass(frozen=True)
class EvidenceMaterializationRequest:
    candidate: EvidenceCandidate
    candidate_snapshot_result: EvidenceCandidateSnapshotResult
    snapshot: EvidenceMaterializationSnapshot
    eligibility_result: AcceptedEligibilityResult
    identity_result: EvidenceIdentityResult
    context: EvidenceMaterializationContext

    def __post_init__(self) -> None:
        _require_exact_type(
            self.candidate,
            EvidenceCandidate,
            "candidate",
        )
        _require_exact_type(
            self.candidate_snapshot_result,
            EvidenceCandidateSnapshotResult,
            "candidate_snapshot_result",
        )
        _require_exact_type(
            self.snapshot,
            EvidenceMaterializationSnapshot,
            "snapshot",
        )
        _require_exact_type(
            self.eligibility_result,
            AcceptedEligibilityResult,
            "eligibility_result",
        )
        _require_exact_type(
            self.identity_result,
            EvidenceIdentityResult,
            "identity_result",
        )
        _require_exact_type(
            self.context,
            EvidenceMaterializationContext,
            "context",
        )


@dataclass(frozen=True)
class EvidenceMaterializationResult:
    decision: str
    accepted_evidence: AcceptedEvidence | None
    reason_codes: tuple[str, ...]
    diagnostics: tuple[EvidenceDiagnostic, ...]

    def __post_init__(self) -> None:
        _require_non_empty_string(self.decision, "decision")
        _require_diagnostics(self.diagnostics, "diagnostics")

        if self.decision == MATERIALIZATION_DECISION_MATERIALIZED:
            _require_exact_type(
                self.accepted_evidence,
                AcceptedEvidence,
                "accepted_evidence",
            )
            _require_reason_codes(
                self.reason_codes,
                allow_empty=True,
            )
            if self.reason_codes:
                raise ValueError(
                    "materialized result reason_codes must be empty"
                )
            return

        if self.decision == MATERIALIZATION_DECISION_REJECTED:
            if self.accepted_evidence is not None:
                raise ValueError(
                    "rejected result accepted_evidence must be None"
                )
            _require_reason_codes(
                self.reason_codes,
                allow_empty=False,
            )
            if not self.diagnostics:
                raise ValueError(
                    "rejected result diagnostics must not be empty"
                )
            return

        raise ValueError("decision must be materialized or rejected")


def _ordered_reason_codes(
    observed_reason_codes: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    observed = frozenset(observed_reason_codes)
    return tuple(
        reason_code
        for reason_code in MATERIALIZATION_REJECTION_REASON_CODES
        if reason_code in observed
    )


def _rejection_diagnostic(reason_code: str) -> EvidenceDiagnostic:
    return EvidenceDiagnostic(
        code=reason_code,
        severity="warning",
        message=f"Materialization rejected: {reason_code}",
        field=_REASON_FIELDS[reason_code],
        source="accepted-evidence-materializer",
    )


def _reject(
    reason_codes: tuple[str, ...] | list[str],
) -> EvidenceMaterializationResult:
    ordered = _ordered_reason_codes(reason_codes)
    if not ordered:
        ordered = ("request_invalid",)
    return EvidenceMaterializationResult(
        decision=MATERIALIZATION_DECISION_REJECTED,
        accepted_evidence=None,
        reason_codes=ordered,
        diagnostics=tuple(
            _rejection_diagnostic(reason_code)
            for reason_code in ordered
        ),
    )


def _parse_rfc3339_timestamp(value: object) -> datetime | None:
    if type(value) is not str or not value:
        return None
    if not (
        value.endswith("Z")
        or (
            len(value) >= 6
            and value[-6] in ("+", "-")
            and value[-3] == ":"
        )
    ):
        return None
    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _candidate_compatibility_reason_codes(
    request: EvidenceMaterializationRequest,
) -> tuple[str, ...]:
    candidate = request.candidate
    snapshot = request.snapshot
    reason_codes: list[str] = []

    if candidate.errors:
        reason_codes.append("candidate_has_errors")

    if candidate.source_checksum_algorithm != "sha256":
        reason_codes.append("unsupported_source_checksum_algorithm")

    try:
        calculated_snapshot = calculate_evidence_candidate_snapshot(
            candidate
        )
    except ValueError:
        reason_codes.append("request_invalid")
    else:
        if calculated_snapshot != request.candidate_snapshot_result:
            reason_codes.append("candidate_snapshot_mismatch")

    source = snapshot.source_snapshot
    producer = snapshot.producer_snapshot
    payload = snapshot.factual_payload
    provenance = snapshot.provenance

    if candidate.source_id != source.source_id:
        reason_codes.append("candidate_source_id_mismatch")
    if candidate.source_type != source.source_type:
        reason_codes.append("candidate_source_type_mismatch")
    if candidate.source_authority != source.authority_status:
        reason_codes.append("candidate_source_authority_mismatch")
    if candidate.source_lifecycle_state != source.lifecycle_status:
        reason_codes.append("candidate_source_lifecycle_mismatch")
    if candidate.source_reference != source.source_path:
        reason_codes.append("candidate_source_reference_mismatch")
    if candidate.source_checksum != source.source_content_digest:
        reason_codes.append("candidate_source_digest_mismatch")
    if candidate.producer_name != producer.producer_name:
        reason_codes.append("candidate_producer_name_mismatch")
    if candidate.producer_version != producer.producer_version:
        reason_codes.append("candidate_producer_version_mismatch")
    if candidate.result_contract_version != producer.producer_contract_version:
        reason_codes.append("candidate_producer_contract_mismatch")
    if candidate.payload_type != payload.payload_type:
        reason_codes.append("candidate_payload_type_mismatch")
    if candidate.raw_payload != payload.payload:
        reason_codes.append("candidate_payload_value_mismatch")
    if candidate.locator != payload.locator.locator_value:
        reason_codes.append("candidate_locator_value_mismatch")
    if candidate.execution_id != provenance.collection_id:
        reason_codes.append("candidate_collection_id_mismatch")

    candidate_observed_at = _parse_rfc3339_timestamp(
        candidate.execution_timestamp
    )
    if (
        candidate_observed_at is None
        or candidate_observed_at != provenance.observed_at
    ):
        reason_codes.append("candidate_observed_at_mismatch")

    eligibility = request.eligibility_result
    if eligibility.decision != "eligible":
        reason_codes.append("eligibility_not_eligible")
    if (
        eligibility.candidate_snapshot_digest
        != request.candidate_snapshot_result.candidate_snapshot_digest
    ):
        reason_codes.append("eligibility_candidate_digest_mismatch")
    if eligibility.source_id != source.source_id:
        reason_codes.append("eligibility_source_id_mismatch")

    if (
        request.identity_result.identity_policy_id
        != EVIDENCE_IDENTITY_POLICY_ID
        or request.identity_result.identity_policy_version
        != EVIDENCE_IDENTITY_POLICY_VERSION
    ):
        reason_codes.append("identity_policy_mismatch")

    return _ordered_reason_codes(reason_codes)


def _build_accepted_evidence(
    request: EvidenceMaterializationRequest,
) -> AcceptedEvidence:
    snapshot = request.snapshot
    context = request.context
    identity_result = request.identity_result

    candidate_reference = EvidenceCandidateReference(
        candidate_contract_version=(
            request.candidate.candidate_contract_version
        ),
        candidate_snapshot_digest=(
            request.candidate_snapshot_result.candidate_snapshot_digest
        ),
        candidate_source_id=request.candidate.source_id,
        candidate_producer_name=request.candidate.producer_name,
        candidate_producer_version=request.candidate.producer_version,
        candidate_payload_digest=snapshot.factual_payload.payload_digest,
    )
    materialization_record = EvidenceMaterializationRecord(
        materializer_id=context.materializer_id,
        materializer_version=context.materializer_version,
        materialized_at=context.materialized_at,
        acceptance_record_id=context.acceptance_record_id,
        accepted_by=context.accepted_by,
        acceptance_reason=context.acceptance_reason,
        review_record_id=context.review_record_id,
        identity_policy_id=identity_result.identity_policy_id,
        identity_policy_version=identity_result.identity_policy_version,
    )
    return AcceptedEvidence(
        evidence_id=identity_result.evidence_id,
        contract_version=snapshot.accepted_evidence_contract_version,
        candidate_reference=candidate_reference,
        source_snapshot=snapshot.source_snapshot,
        producer_snapshot=snapshot.producer_snapshot,
        factual_payload=snapshot.factual_payload,
        provenance=snapshot.provenance,
        eligibility_result=request.eligibility_result,
        materialization_record=materialization_record,
        diagnostics=snapshot.diagnostics,
    )


def materialize_accepted_evidence(
    request: object,
) -> EvidenceMaterializationResult:
    if type(request) is not EvidenceMaterializationRequest:
        return _reject(("request_invalid",))

    try:
        _require_exact_type(
            request.candidate,
            EvidenceCandidate,
            "candidate",
        )
        _require_exact_type(
            request.candidate_snapshot_result,
            EvidenceCandidateSnapshotResult,
            "candidate_snapshot_result",
        )
        _require_exact_type(
            request.snapshot,
            EvidenceMaterializationSnapshot,
            "snapshot",
        )
        _require_exact_type(
            request.eligibility_result,
            AcceptedEligibilityResult,
            "eligibility_result",
        )
        _require_exact_type(
            request.identity_result,
            EvidenceIdentityResult,
            "identity_result",
        )
    except ValueError:
        return _reject(("request_invalid",))

    try:
        _require_exact_type(
            request.context,
            EvidenceMaterializationContext,
            "context",
        )
        request.context.__post_init__()
    except (AttributeError, ValueError):
        return _reject(("materialization_context_invalid",))

    try:
        request.snapshot.__post_init__()
    except (AttributeError, ValueError):
        return _reject(("diagnostics_invalid",))

    reason_codes = _candidate_compatibility_reason_codes(request)
    if reason_codes:
        return _reject(reason_codes)

    try:
        accepted_evidence = _build_accepted_evidence(request)
    except ValueError:
        return _reject(("request_invalid",))

    calculated_identity_result = calculate_evidence_identity(
        identity_input_from_accepted_evidence(accepted_evidence)
    )
    if calculated_identity_result != request.identity_result:
        return _reject(("identity_result_mismatch",))

    return EvidenceMaterializationResult(
        decision=MATERIALIZATION_DECISION_MATERIALIZED,
        accepted_evidence=accepted_evidence,
        reason_codes=(),
        diagnostics=accepted_evidence.diagnostics,
    )
