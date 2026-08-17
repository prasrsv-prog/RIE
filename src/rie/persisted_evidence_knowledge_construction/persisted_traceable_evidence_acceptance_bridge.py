"""Minimum persisted TraceableEvidence v3 acceptance compatibility bridge.

This module is intentionally narrow. It projects only persisted, already-validated
TraceableEvidence v3 / repository state plus explicit caller-supplied acceptance
metadata into the legacy AcceptedEvidence + AcceptanceRecord contracts required by
the existing persisted-evidence knowledge-construction runtime.

It does not persist, infer semantic decisions, reuse test fixtures, or invent
operator metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import Final

from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
)
from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceLocator,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.evidence_identity import (
    EVIDENCE_IDENTITY_POLICY_ID,
    EVIDENCE_IDENTITY_POLICY_VERSION,
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)
from rie.evidence_materialization.atomic_text_evidence_derivation import (
    ATOMIC_TEXT_DERIVATION_PROVENANCE_CONTRACT_VERSION,
    ATOMIC_TEXT_DERIVATION_TYPE,
)
from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_eligibility_snapshot_digest,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    TraceableEvidence,
    TraceableEvidenceAtomicTextDerivationProvenance,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
    calculate_evidence_repository_audit_id,
    calculate_evidence_repository_revision_id,
)
from rie.evidence_repository.evidence_repository_contract import (
    EvidenceRepositoryLookupResult,
)


PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_REQUEST_CONTRACT_VERSION: Final = (
    "persisted_traceable_evidence_acceptance_bridge_request_contract_v1"
)
PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION: Final = (
    "persisted_traceable_evidence_acceptance_bridge_result_contract_v1"
)
PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_ID: Final = (
    "rcis-persisted-traceable-evidence-acceptance-compatibility"
)
PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_VERSION: Final = "1.0.0"

PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS: Final = frozenset(
    {
        "evm1_a3e18a4f76968b308e10cf1f0c9de37f709336e6a0f0c2b25515cd98e9d88499",
        "evm1_0bab2e3d3f2ef04b39660d287c7479ce5967027ecf8fb61092b1a72a533db1d0",
        "evm1_32f14d29ef3880b87a658962bdbe6b63c361e6c6c8c2ce6c8d13669948f6c3eb",
        "evm1_57f2bd478bb59f16aa6cd2114d70fdef7e70ddbfb7dd317e166946cd539e6607",
        "evm1_1d00dc2e1cb02e5d1b6510f8e1598ff2c9bcd1df3b6df21b38725e5437536c94",
    }
)
PILOT_FFS21_PRIMARY_OPERATOR: Final = (
    "rcis-rsv-real-asset-pilot-primary-operator"
)
PILOT_FFS21_ACCEPTANCE_REASON: Final = (
    "explicit_operator_approved_five_clean_ffs21_atomic_facts"
)
PILOT_FFS21_ACCEPTANCE_POLICY_ID: Final = (
    "rcis-explicit-operator-atomic-evidence-acceptance"
)
PILOT_FFS21_ACCEPTANCE_POLICY_VERSION: Final = "1.0.0"
PILOT_FFS21_MATERIALIZER_ID: Final = "accepted-evidence-materializer"
PILOT_FFS21_MATERIALIZER_VERSION: Final = "1.0.0"

ACCEPTED_EVIDENCE_CONTRACT_VERSION: Final = "accepted-evidence-v1"
ACCEPTANCE_RECORD_CONTRACT_VERSION: Final = "acceptance-record-v1"

BRIDGE_STATUS_MATERIALIZED: Final = "materialized"
BRIDGE_STATUS_REJECTED: Final = "rejected"

_PLACEHOLDER_EVIDENCE_ID: Final = "ev1_" + ("0" * 64)
_PLACEHOLDER_ACCEPTANCE_RECORD_ID: Final = "ar1_" + ("0" * 64)


def _require_non_empty_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True)
class PersistedTraceableEvidenceAcceptanceBridgeRequest:
    contract_version: str
    repository_lookup_result: EvidenceRepositoryLookupResult
    target_traceable_evidence_id: str
    accepted_by: str
    acceptance_reason: str
    review_record_id: str
    accepted_at: datetime
    acceptance_policy_id: str
    acceptance_policy_version: str
    materializer_id: str
    materializer_version: str
    eligibility_evaluated_by: str
    eligibility_evaluated_at: datetime
    provenance_observed_at: datetime
    compatibility_policy_id: str
    compatibility_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_REQUEST_CONTRACT_VERSION
        ):
            raise ValueError("unsupported bridge request contract version")
        if type(self.repository_lookup_result) is not EvidenceRepositoryLookupResult:
            raise TypeError(
                "repository_lookup_result must be exact EvidenceRepositoryLookupResult"
            )
        for field_name in (
            "target_traceable_evidence_id",
            "accepted_by",
            "acceptance_reason",
            "review_record_id",
            "acceptance_policy_id",
            "acceptance_policy_version",
            "materializer_id",
            "materializer_version",
            "eligibility_evaluated_by",
            "compatibility_policy_id",
            "compatibility_policy_version",
        ):
            _require_non_empty_string(getattr(self, field_name), field_name)
        for field_name in (
            "accepted_at",
            "eligibility_evaluated_at",
            "provenance_observed_at",
        ):
            _require_aware_datetime(getattr(self, field_name), field_name)
        if (
            self.compatibility_policy_id
            != PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_ID
            or self.compatibility_policy_version
            != PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_VERSION
        ):
            raise ValueError("unsupported bridge compatibility policy")
        if self.accepted_by != PILOT_FFS21_PRIMARY_OPERATOR:
            raise ValueError("accepted_by is outside approved pilot authority")
        if self.acceptance_reason != PILOT_FFS21_ACCEPTANCE_REASON:
            raise ValueError("acceptance_reason is outside approved pilot authority")
        if self.acceptance_policy_id != PILOT_FFS21_ACCEPTANCE_POLICY_ID:
            raise ValueError("unsupported approved acceptance policy")
        if (
            self.acceptance_policy_version
            != PILOT_FFS21_ACCEPTANCE_POLICY_VERSION
        ):
            raise ValueError("unsupported approved acceptance policy version")
        if self.materializer_id != PILOT_FFS21_MATERIALIZER_ID:
            raise ValueError("materializer_id is outside approved pilot authority")
        if self.materializer_version != PILOT_FFS21_MATERIALIZER_VERSION:
            raise ValueError("materializer_version is outside approved pilot authority")
        if self.eligibility_evaluated_by != PILOT_FFS21_PRIMARY_OPERATOR:
            raise ValueError(
                "eligibility_evaluated_by is outside approved pilot authority"
            )
        if self.eligibility_evaluated_at != self.accepted_at:
            raise ValueError(
                "eligibility_evaluated_at must equal the approved operation timestamp"
            )
        if self.provenance_observed_at != self.accepted_at:
            raise ValueError(
                "provenance_observed_at must equal the approved operation timestamp"
            )


@dataclass(frozen=True)
class PersistedTraceableEvidenceAcceptanceBridgeResult:
    contract_version: str
    status: str
    target_traceable_evidence_id: str
    accepted_evidence: AcceptedEvidence | None
    acceptance_record: AcceptanceRecord | None
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported bridge result contract version")
        if self.status not in (BRIDGE_STATUS_MATERIALIZED, BRIDGE_STATUS_REJECTED):
            raise ValueError("bridge status is invalid")
        _require_non_empty_string(
            self.target_traceable_evidence_id,
            "target_traceable_evidence_id",
        )
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        if self.status == BRIDGE_STATUS_MATERIALIZED:
            if type(self.accepted_evidence) is not AcceptedEvidence:
                raise TypeError("materialized bridge result requires AcceptedEvidence")
            if type(self.acceptance_record) is not AcceptanceRecord:
                raise TypeError("materialized bridge result requires AcceptanceRecord")
            if self.reason_codes:
                raise ValueError("materialized bridge result cannot contain reason codes")
        else:
            if self.accepted_evidence is not None or self.acceptance_record is not None:
                raise ValueError("rejected bridge result cannot contain outputs")
            if not self.reason_codes:
                raise ValueError("rejected bridge result requires a reason code")
        for index, code in enumerate(self.reason_codes):
            _require_non_empty_string(code, f"reason_codes[{index}]")


def _rejected(
    target_traceable_evidence_id: str,
    reason_code: str,
) -> PersistedTraceableEvidenceAcceptanceBridgeResult:
    return PersistedTraceableEvidenceAcceptanceBridgeResult(
        contract_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION
        ),
        status=BRIDGE_STATUS_REJECTED,
        target_traceable_evidence_id=target_traceable_evidence_id,
        accepted_evidence=None,
        acceptance_record=None,
        reason_codes=(reason_code,),
    )


def _validate_persisted_lookup(
    lookup: EvidenceRepositoryLookupResult,
) -> str | None:
    try:
        lookup.__post_init__()
    except Exception:
        return "invalid_repository_lookup_result"
    if lookup.status != "found":
        return "repository_lookup_not_found_or_rejected"

    revision = lookup.revision
    audit = lookup.audit_record
    collection = lookup.collection
    if revision is None or audit is None or collection is None:
        return "invalid_repository_lookup_result"

    try:
        revision.__post_init__()
        audit.__post_init__()
        collection.__post_init__()
    except Exception:
        return "invalid_persisted_repository_state"

    expected_payload_digest = (
        calculate_evidence_collection_repository_payload_digest(collection)
    )
    if revision.collection_payload_digest != expected_payload_digest:
        return "collection_payload_digest_mismatch"
    if (
        revision.collection_id != collection.collection_id
        or revision.source_id != collection.source_id
        or audit.revision_id != revision.revision_id
        or audit.source_id != revision.source_id
        or audit.revision_number != revision.revision_number
        or audit.collection_id != revision.collection_id
        or audit.actor_id != revision.actor_id
        or audit.recorded_at_utc != revision.recorded_at_utc
        or revision.audit_id != audit.audit_id
    ):
        return "repository_linkage_mismatch"

    expected_revision_id = calculate_evidence_repository_revision_id(
        source_id=revision.source_id,
        revision_number=revision.revision_number,
        collection_id=revision.collection_id,
        collection_payload_digest=revision.collection_payload_digest,
        previous_revision_id=revision.previous_revision_id,
    )
    if expected_revision_id != revision.revision_id:
        return "repository_revision_identity_mismatch"

    expected_audit_id = calculate_evidence_repository_audit_id(
        action=audit.action,
        revision_id=audit.revision_id,
        source_id=audit.source_id,
        revision_number=audit.revision_number,
        collection_id=audit.collection_id,
        actor_id=audit.actor_id,
        recorded_at_utc=audit.recorded_at_utc,
    )
    if expected_audit_id != audit.audit_id:
        return "repository_audit_identity_mismatch"
    return None


def materialize_persisted_traceable_evidence_acceptance(
    request: object,
) -> PersistedTraceableEvidenceAcceptanceBridgeResult:
    if type(request) is not PersistedTraceableEvidenceAcceptanceBridgeRequest:
        return _rejected("<invalid-request>", "invalid_request")
    try:
        request.__post_init__()
    except Exception:
        return _rejected(
            getattr(request, "target_traceable_evidence_id", "<invalid-request>"),
            "invalid_request",
        )

    if (
        request.target_traceable_evidence_id
        not in PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "target_traceable_evidence_outside_approved_five_fact_scope",
        )

    lookup = request.repository_lookup_result
    lookup_issue = _validate_persisted_lookup(lookup)
    if lookup_issue is not None:
        return _rejected(request.target_traceable_evidence_id, lookup_issue)

    collection = lookup.collection
    assert collection is not None
    if (
        collection.contract_version
        != EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "unsupported_collection_contract_version",
        )

    matches = tuple(
        item
        for item in collection.evidence_items
        if item.evidence_id == request.target_traceable_evidence_id
    )
    if len(matches) != 1:
        return _rejected(
            request.target_traceable_evidence_id,
            "target_traceable_evidence_not_found_or_not_unique",
        )
    target = matches[0]

    try:
        target.__post_init__()
    except Exception:
        return _rejected(
            request.target_traceable_evidence_id,
            "invalid_target_traceable_evidence",
        )
    if (
        target.contract_version
        != TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "target_traceable_evidence_not_v3_atomic",
        )

    atomic = getattr(target, "atomic_text_derivation_provenance", None)
    if type(atomic) is not TraceableEvidenceAtomicTextDerivationProvenance:
        return _rejected(
            request.target_traceable_evidence_id,
            "atomic_text_derivation_provenance_missing",
        )
    if (
        atomic.contract_version
        != ATOMIC_TEXT_DERIVATION_PROVENANCE_CONTRACT_VERSION
        or atomic.derivation_type != ATOMIC_TEXT_DERIVATION_TYPE
        or atomic.atomic_statement_sha256 != target.content_digest
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "atomic_text_derivation_provenance_mismatch",
        )

    snapshot = collection.eligibility_snapshot
    if target.eligibility_snapshot_digest != derive_evidence_eligibility_snapshot_digest(
        snapshot
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "eligibility_snapshot_digest_mismatch",
        )
    if (
        snapshot.evidence_eligibility != "eligible"
        or snapshot.evidence_collection_allowed is not True
        or snapshot.requires_review is not False
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "persisted_evidence_not_finally_eligible",
        )
    if (
        target.provenance.source_id != collection.source_id
        or target.provenance.source_path != collection.source_path
        or target.provenance.source_checksum != collection.source_checksum
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "persisted_source_provenance_mismatch",
        )

    candidate_reference = EvidenceCandidateReference(
        candidate_contract_version=target.contract_version,
        candidate_snapshot_digest=target.content_digest,
        candidate_source_id=collection.source_id,
        candidate_producer_name=target.provenance.extraction_method,
        candidate_producer_version=target.provenance.upstream_contract_version,
        candidate_payload_digest=target.content_digest,
    )
    source_snapshot = EvidenceSourceSnapshot(
        source_id=collection.source_id,
        source_path=collection.source_path,
        source_type=snapshot.source_type,
        document_classification=snapshot.document_classification,
        authority_status=snapshot.authority_status,
        lifecycle_status=snapshot.lifecycle_status,
        evidence_eligibility=snapshot.evidence_eligibility,
        source_content_digest=collection.source_checksum,
    )
    producer_snapshot = EvidenceProducerSnapshot(
        producer_name=target.provenance.extraction_method,
        producer_version=target.provenance.upstream_contract_version,
        producer_kind=target.provenance.extraction_status,
        producer_contract_version=target.provenance.artifact_contract_version,
    )
    factual_payload = EvidencePayload(
        payload_type=target.content_type,
        payload_schema_version=target.contract_version,
        payload=target.content,
        payload_digest=target.content_digest,
        locator=EvidenceLocator(
            locator_type=target.provenance.extraction_method,
            locator_value=(
                target.provenance.page_index,
                target.provenance.page_number,
                target.provenance.extraction_index,
            ),
            locator_schema_version=target.contract_version,
        ),
    )
    lineage = (
        target.evidence_id,
        atomic.parent_traceable_evidence_id,
        *atomic.source_span_ids,
        atomic.operator_decision_packet_sha256,
    )
    provenance = EvidenceProvenance(
        collection_id=collection.collection_id,
        producer_output_digest=target.content_digest,
        lineage=lineage,
        observed_at=request.provenance_observed_at,
        source_registry_version=snapshot.registry_version,
    )
    eligibility_result = AcceptedEligibilityResult(
        decision=snapshot.evidence_eligibility,
        policy_id=snapshot.policy_id,
        policy_version=snapshot.policy_version,
        candidate_snapshot_digest=target.content_digest,
        source_id=collection.source_id,
        reason_codes=(snapshot.reason,),
        evaluated_at=request.eligibility_evaluated_at,
        evaluated_by=request.eligibility_evaluated_by,
        diagnostics=(),
    )

    provisional_materialization = EvidenceMaterializationRecord(
        materializer_id=request.materializer_id,
        materializer_version=request.materializer_version,
        materialized_at=request.accepted_at,
        acceptance_record_id=_PLACEHOLDER_ACCEPTANCE_RECORD_ID,
        accepted_by=request.accepted_by,
        acceptance_reason=request.acceptance_reason,
        review_record_id=request.review_record_id,
        identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
    )
    provisional_evidence = AcceptedEvidence(
        evidence_id=_PLACEHOLDER_EVIDENCE_ID,
        contract_version=ACCEPTED_EVIDENCE_CONTRACT_VERSION,
        candidate_reference=candidate_reference,
        source_snapshot=source_snapshot,
        producer_snapshot=producer_snapshot,
        factual_payload=factual_payload,
        provenance=provenance,
        eligibility_result=eligibility_result,
        materialization_record=provisional_materialization,
        diagnostics=(),
    )
    evidence_identity = calculate_evidence_identity(
        identity_input_from_accepted_evidence(provisional_evidence)
    )

    provisional_acceptance = AcceptanceRecord(
        acceptance_record_id=_PLACEHOLDER_ACCEPTANCE_RECORD_ID,
        contract_version=ACCEPTANCE_RECORD_CONTRACT_VERSION,
        evidence_id=evidence_identity.evidence_id,
        accepted_by=request.accepted_by,
        acceptance_reason=request.acceptance_reason,
        review_record_id=request.review_record_id,
        accepted_at=request.accepted_at,
        acceptance_policy_id=request.acceptance_policy_id,
        acceptance_policy_version=request.acceptance_policy_version,
        evidence_identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        evidence_identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
        materializer_id=request.materializer_id,
        materializer_version=request.materializer_version,
        diagnostics=(),
    )
    acceptance_identity = calculate_acceptance_identity(
        acceptance_identity_input_from_record(provisional_acceptance)
    )

    materialization_record = replace(
        provisional_materialization,
        acceptance_record_id=acceptance_identity.acceptance_record_id,
    )
    accepted_evidence = replace(
        provisional_evidence,
        evidence_id=evidence_identity.evidence_id,
        materialization_record=materialization_record,
    )
    acceptance_record = replace(
        provisional_acceptance,
        acceptance_record_id=acceptance_identity.acceptance_record_id,
    )

    if (
        calculate_evidence_identity(
            identity_input_from_accepted_evidence(accepted_evidence)
        )
        != evidence_identity
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "accepted_evidence_identity_recomputation_mismatch",
        )
    if (
        calculate_acceptance_identity(
            acceptance_identity_input_from_record(acceptance_record)
        )
        != acceptance_identity
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "acceptance_record_identity_recomputation_mismatch",
        )
    if acceptance_record.evidence_id != accepted_evidence.evidence_id:
        return _rejected(
            request.target_traceable_evidence_id,
            "accepted_output_evidence_id_mismatch",
        )

    return PersistedTraceableEvidenceAcceptanceBridgeResult(
        contract_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION
        ),
        status=BRIDGE_STATUS_MATERIALIZED,
        target_traceable_evidence_id=target.evidence_id,
        accepted_evidence=accepted_evidence,
        acceptance_record=acceptance_record,
        reason_codes=(),
    )
