from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import datetime, timezone

import pytest

from rie.application.evidence_candidate import EvidenceCandidate
from rie.application.evidence_candidate_snapshot import (
    EvidenceCandidateSnapshotResult,
    calculate_evidence_candidate_snapshot,
)
from rie.application.evidence_materializer import (
    MATERIALIZATION_DECISION_MATERIALIZED,
    MATERIALIZATION_DECISION_REJECTED,
    MATERIALIZATION_REJECTION_REASON_CODES,
    EvidenceMaterializationContext,
    EvidenceMaterializationRequest,
    EvidenceMaterializationResult,
    EvidenceMaterializationSnapshot,
    materialize_accepted_evidence,
)
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceDiagnostic,
    EvidenceLocator,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.evidence_identity import (
    EVIDENCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION,
    EVIDENCE_IDENTITY_DIGEST_ALGORITHM,
    EVIDENCE_IDENTITY_POLICY_ID,
    EVIDENCE_IDENTITY_POLICY_VERSION,
    EvidenceIdentityResult,
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)


FIXED_TIME = datetime(2026, 7, 12, 9, 0, tzinfo=timezone.utc)
RAW_PAYLOAD = '{"page_count":1,"title":"SV300"}'
LOCATOR = (("page_index", 0), ("scope", "page"))


def _candidate(**changes: object) -> EvidenceCandidate:
    values = {
        "source_id": "source-1",
        "source_type": "pdf",
        "source_checksum_algorithm": "sha256",
        "source_checksum": "a" * 64,
        "source_authority": "official",
        "source_lifecycle_state": "active",
        "source_reference": "official/source.pdf",
        "execution_id": "collection-1",
        "producer_name": "structural-inspector",
        "producer_version": "1.0.0",
        "result_contract_version": "result-v1",
        "execution_timestamp": "2026-07-12T09:00:00Z",
        "payload_type": "document_structural_metadata",
        "raw_payload": RAW_PAYLOAD,
        "locator": LOCATOR,
        "warnings": ("warning-one",),
        "errors": (),
        "candidate_contract_version": "candidate-v1",
    }
    values.update(changes)
    return EvidenceCandidate(**values)


def _unchecked_instance(contract_type: type[object], **values: object) -> object:
    instance = object.__new__(contract_type)
    for field_name, value in values.items():
        object.__setattr__(instance, field_name, value)
    return instance


def _diagnostic(
    *,
    code: str = "accepted",
    severity: str = "info",
    message: str = "Accepted by explicit policy",
    field: str = "eligibility_result",
    source: str = "policy",
) -> EvidenceDiagnostic:
    return EvidenceDiagnostic(
        code=code,
        severity=severity,
        message=message,
        field=field,
        source=source,
    )


def _source_snapshot(**changes: object) -> EvidenceSourceSnapshot:
    values = {
        "source_id": "source-1",
        "source_path": "official/source.pdf",
        "source_type": "pdf",
        "document_classification": "official_product_specification",
        "authority_status": "official",
        "lifecycle_status": "active",
        "evidence_eligibility": "eligible",
        "source_content_digest": "a" * 64,
    }
    values.update(changes)
    return EvidenceSourceSnapshot(**values)


def _producer_snapshot(**changes: object) -> EvidenceProducerSnapshot:
    values = {
        "producer_name": "structural-inspector",
        "producer_version": "1.0.0",
        "producer_kind": "inspector",
        "producer_contract_version": "result-v1",
    }
    values.update(changes)
    return EvidenceProducerSnapshot(**values)


def _payload(**changes: object) -> EvidencePayload:
    values = {
        "payload_type": "document_structural_metadata",
        "payload_schema_version": "payload-v1",
        "payload": RAW_PAYLOAD,
        "payload_digest": "b" * 64,
        "locator": EvidenceLocator(
            locator_type="page",
            locator_value=LOCATOR,
            locator_schema_version="locator-v1",
        ),
    }
    values.update(changes)
    return EvidencePayload(**values)


def _provenance(**changes: object) -> EvidenceProvenance:
    values = {
        "collection_id": "collection-1",
        "producer_output_digest": "c" * 64,
        "lineage": ("admission-1", "inspection-1"),
        "observed_at": FIXED_TIME,
        "source_registry_version": "registry-v1",
    }
    values.update(changes)
    return EvidenceProvenance(**values)


def _snapshot(**changes: object) -> EvidenceMaterializationSnapshot:
    values = {
        "accepted_evidence_contract_version": "accepted-evidence-v1",
        "source_snapshot": _source_snapshot(),
        "producer_snapshot": _producer_snapshot(),
        "factual_payload": _payload(),
        "provenance": _provenance(),
        "diagnostics": (_diagnostic(),),
    }
    values.update(changes)
    return EvidenceMaterializationSnapshot(**values)


def _context(**changes: object) -> EvidenceMaterializationContext:
    values = {
        "materializer_id": "accepted-evidence-materializer",
        "materializer_version": "1.0.0",
        "materialized_at": FIXED_TIME,
        "acceptance_record_id": "acceptance-record-1",
        "accepted_by": "review-service",
        "acceptance_reason": "All explicit prerequisites satisfied",
        "review_record_id": "review-1",
    }
    values.update(changes)
    return EvidenceMaterializationContext(**values)


def _eligibility(
    candidate_snapshot_digest: str,
    **changes: object,
) -> AcceptedEligibilityResult:
    values = {
        "decision": "eligible",
        "policy_id": "official-source-policy",
        "policy_version": "1.0.0",
        "candidate_snapshot_digest": candidate_snapshot_digest,
        "source_id": "source-1",
        "reason_codes": ("official_source_eligible",),
        "evaluated_at": FIXED_TIME,
        "evaluated_by": "eligibility-service",
        "diagnostics": (_diagnostic(),),
    }
    values.update(changes)
    return AcceptedEligibilityResult(**values)


def _identity_result(
    *,
    candidate: EvidenceCandidate,
    candidate_snapshot_result: EvidenceCandidateSnapshotResult,
    snapshot: EvidenceMaterializationSnapshot,
    eligibility_result: AcceptedEligibilityResult,
    context: EvidenceMaterializationContext,
) -> EvidenceIdentityResult:
    candidate_reference = EvidenceCandidateReference(
        candidate_contract_version=candidate.candidate_contract_version,
        candidate_snapshot_digest=(
            candidate_snapshot_result.candidate_snapshot_digest
        ),
        candidate_source_id=candidate.source_id,
        candidate_producer_name=candidate.producer_name,
        candidate_producer_version=candidate.producer_version,
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
        identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
    )
    provisional = AcceptedEvidence(
        evidence_id="provisional-evidence-id",
        contract_version=snapshot.accepted_evidence_contract_version,
        candidate_reference=candidate_reference,
        source_snapshot=snapshot.source_snapshot,
        producer_snapshot=snapshot.producer_snapshot,
        factual_payload=snapshot.factual_payload,
        provenance=snapshot.provenance,
        eligibility_result=eligibility_result,
        materialization_record=materialization_record,
        diagnostics=snapshot.diagnostics,
    )
    return calculate_evidence_identity(
        identity_input_from_accepted_evidence(provisional)
    )


def _request(
    *,
    candidate: EvidenceCandidate | None = None,
    candidate_snapshot_result: EvidenceCandidateSnapshotResult | None = None,
    snapshot: EvidenceMaterializationSnapshot | None = None,
    eligibility_result: AcceptedEligibilityResult | None = None,
    identity_result: EvidenceIdentityResult | None = None,
    context: EvidenceMaterializationContext | None = None,
) -> EvidenceMaterializationRequest:
    candidate = candidate or _candidate()
    candidate_snapshot_result = (
        candidate_snapshot_result
        or calculate_evidence_candidate_snapshot(candidate)
    )
    snapshot = snapshot or _snapshot()
    eligibility_result = eligibility_result or _eligibility(
        candidate_snapshot_result.candidate_snapshot_digest
    )
    context = context or _context()
    identity_result = identity_result or _identity_result(
        candidate=candidate,
        candidate_snapshot_result=candidate_snapshot_result,
        snapshot=snapshot,
        eligibility_result=eligibility_result,
        context=context,
    )
    return EvidenceMaterializationRequest(
        candidate=candidate,
        candidate_snapshot_result=candidate_snapshot_result,
        snapshot=snapshot,
        eligibility_result=eligibility_result,
        identity_result=identity_result,
        context=context,
    )


@pytest.mark.parametrize(
    "contract_type",
    (
        EvidenceMaterializationSnapshot,
        EvidenceMaterializationContext,
        EvidenceMaterializationRequest,
        EvidenceMaterializationResult,
    ),
)
def test_materializer_contracts_are_frozen(
    contract_type: type[object],
) -> None:
    request = _request()
    instances = {
        EvidenceMaterializationSnapshot: request.snapshot,
        EvidenceMaterializationContext: request.context,
        EvidenceMaterializationRequest: request,
        EvidenceMaterializationResult: materialize_accepted_evidence(request),
    }

    with pytest.raises(FrozenInstanceError):
        setattr(instances[contract_type], fields(contract_type)[0].name, "x")


@pytest.mark.parametrize(
    "contract_type",
    (
        EvidenceMaterializationSnapshot,
        EvidenceMaterializationContext,
        EvidenceMaterializationRequest,
        EvidenceMaterializationResult,
    ),
)
def test_materializer_contract_fields_have_no_defaults(
    contract_type: type[object],
) -> None:
    assert all(
        field.default is MISSING
        and field.default_factory is MISSING
        for field in fields(contract_type)
    )


@pytest.mark.parametrize(
    ("contract_type", "expected_fields"),
    (
        (
            EvidenceMaterializationSnapshot,
            (
                "accepted_evidence_contract_version",
                "source_snapshot",
                "producer_snapshot",
                "factual_payload",
                "provenance",
                "diagnostics",
            ),
        ),
        (
            EvidenceMaterializationContext,
            (
                "materializer_id",
                "materializer_version",
                "materialized_at",
                "acceptance_record_id",
                "accepted_by",
                "acceptance_reason",
                "review_record_id",
            ),
        ),
        (
            EvidenceMaterializationRequest,
            (
                "candidate",
                "candidate_snapshot_result",
                "snapshot",
                "eligibility_result",
                "identity_result",
                "context",
            ),
        ),
        (
            EvidenceMaterializationResult,
            (
                "decision",
                "accepted_evidence",
                "reason_codes",
                "diagnostics",
            ),
        ),
    ),
)
def test_materializer_contracts_have_exact_fields(
    contract_type: type[object],
    expected_fields: tuple[str, ...],
) -> None:
    assert tuple(field.name for field in fields(contract_type)) == expected_fields


def test_successful_materialization_returns_immutable_accepted_evidence() -> None:
    result = materialize_accepted_evidence(_request())

    assert result.decision == MATERIALIZATION_DECISION_MATERIALIZED
    assert type(result.accepted_evidence) is AcceptedEvidence
    assert result.reason_codes == ()
    assert result.accepted_evidence.evidence_id.startswith("ev1_")

    with pytest.raises(FrozenInstanceError):
        result.accepted_evidence.evidence_id = "changed"


def test_success_constructs_candidate_reference_from_explicit_inputs() -> None:
    request = _request()
    evidence = materialize_accepted_evidence(request).accepted_evidence

    assert evidence is not None
    assert evidence.candidate_reference == EvidenceCandidateReference(
        candidate_contract_version=request.candidate.candidate_contract_version,
        candidate_snapshot_digest=(
            request.candidate_snapshot_result.candidate_snapshot_digest
        ),
        candidate_source_id=request.candidate.source_id,
        candidate_producer_name=request.candidate.producer_name,
        candidate_producer_version=request.candidate.producer_version,
        candidate_payload_digest=request.snapshot.factual_payload.payload_digest,
    )


def test_success_constructs_materialization_record_from_context() -> None:
    request = _request()
    evidence = materialize_accepted_evidence(request).accepted_evidence

    assert evidence is not None
    assert evidence.materialization_record == EvidenceMaterializationRecord(
        materializer_id=request.context.materializer_id,
        materializer_version=request.context.materializer_version,
        materialized_at=request.context.materialized_at,
        acceptance_record_id=request.context.acceptance_record_id,
        accepted_by=request.context.accepted_by,
        acceptance_reason=request.context.acceptance_reason,
        review_record_id=request.context.review_record_id,
        identity_policy_id=request.identity_result.identity_policy_id,
        identity_policy_version=request.identity_result.identity_policy_version,
    )


def test_success_preserves_explicit_snapshot_and_eligibility_values() -> None:
    request = _request()
    evidence = materialize_accepted_evidence(request).accepted_evidence

    assert evidence is not None
    assert evidence.contract_version == (
        request.snapshot.accepted_evidence_contract_version
    )
    assert evidence.source_snapshot is request.snapshot.source_snapshot
    assert evidence.producer_snapshot is request.snapshot.producer_snapshot
    assert evidence.factual_payload is request.snapshot.factual_payload
    assert evidence.provenance is request.snapshot.provenance
    assert evidence.eligibility_result is request.eligibility_result
    assert evidence.diagnostics is request.snapshot.diagnostics


def test_candidate_snapshot_is_recalculated() -> None:
    candidate = _candidate(source_id="source-2")
    stale_result = calculate_evidence_candidate_snapshot(_candidate())
    snapshot = _snapshot(source_snapshot=_source_snapshot(source_id="source-2"))
    eligibility = _eligibility(
        stale_result.candidate_snapshot_digest,
        source_id="source-2",
    )
    request = _request(
        candidate=candidate,
        candidate_snapshot_result=stale_result,
        snapshot=snapshot,
        eligibility_result=eligibility,
    )

    result = materialize_accepted_evidence(request)

    assert result.decision == MATERIALIZATION_DECISION_REJECTED
    assert "candidate_snapshot_mismatch" in result.reason_codes


@pytest.mark.parametrize(
    ("candidate_changes", "snapshot_changes", "reason_code"),
    (
        (
            {"source_id": "source-2"},
            {"source_snapshot": _source_snapshot(source_id="source-1")},
            "candidate_source_id_mismatch",
        ),
        (
            {"source_type": "image"},
            {"source_snapshot": _source_snapshot(source_type="pdf")},
            "candidate_source_type_mismatch",
        ),
        (
            {"source_authority": "reviewed"},
            {"source_snapshot": _source_snapshot(authority_status="official")},
            "candidate_source_authority_mismatch",
        ),
        (
            {"source_lifecycle_state": "superseded"},
            {"source_snapshot": _source_snapshot(lifecycle_status="active")},
            "candidate_source_lifecycle_mismatch",
        ),
        (
            {"source_reference": "other/source.pdf"},
            {"source_snapshot": _source_snapshot(source_path="official/source.pdf")},
            "candidate_source_reference_mismatch",
        ),
        (
            {"source_checksum": "d" * 64},
            {"source_snapshot": _source_snapshot(source_content_digest="a" * 64)},
            "candidate_source_digest_mismatch",
        ),
        (
            {"producer_name": "other-producer"},
            {"producer_snapshot": _producer_snapshot(producer_name="structural-inspector")},
            "candidate_producer_name_mismatch",
        ),
        (
            {"producer_version": "2.0.0"},
            {"producer_snapshot": _producer_snapshot(producer_version="1.0.0")},
            "candidate_producer_version_mismatch",
        ),
        (
            {"result_contract_version": "result-v2"},
            {"producer_snapshot": _producer_snapshot(producer_contract_version="result-v1")},
            "candidate_producer_contract_mismatch",
        ),
        (
            {"payload_type": "other_payload"},
            {"factual_payload": _payload(payload_type="document_structural_metadata")},
            "candidate_payload_type_mismatch",
        ),
        (
            {"raw_payload": '{"page_count":2}'},
            {"factual_payload": _payload(payload=RAW_PAYLOAD)},
            "candidate_payload_value_mismatch",
        ),
        (
            {"locator": (("page_index", 1), ("scope", "page"))},
            {"factual_payload": _payload()},
            "candidate_locator_value_mismatch",
        ),
        (
            {"execution_id": "collection-2"},
            {"provenance": _provenance(collection_id="collection-1")},
            "candidate_collection_id_mismatch",
        ),
        (
            {"execution_timestamp": "2026-07-12T10:00:00+00:00"},
            {"provenance": _provenance(observed_at=FIXED_TIME)},
            "candidate_observed_at_mismatch",
        ),
    ),
)
def test_each_candidate_compatibility_mismatch_is_rejected(
    candidate_changes: dict[str, object],
    snapshot_changes: dict[str, object],
    reason_code: str,
) -> None:
    candidate = _candidate(**candidate_changes)
    snapshot = _snapshot(**snapshot_changes)
    snapshot_result = calculate_evidence_candidate_snapshot(candidate)
    eligibility = _eligibility(
        snapshot_result.candidate_snapshot_digest,
        source_id=snapshot.source_snapshot.source_id,
    )
    request = _request(
        candidate=candidate,
        candidate_snapshot_result=snapshot_result,
        snapshot=snapshot,
        eligibility_result=eligibility,
        identity_result=_request().identity_result,
    )

    result = materialize_accepted_evidence(request)

    assert result.decision == MATERIALIZATION_DECISION_REJECTED
    assert reason_code in result.reason_codes


def test_candidate_errors_reject_materialization() -> None:
    request = _request(candidate=_candidate(errors=("producer-error",)))

    result = materialize_accepted_evidence(request)

    assert result.reason_codes[0] == "candidate_has_errors"


def test_unsupported_checksum_algorithm_rejects_materialization() -> None:
    base = _candidate()
    candidate = _unchecked_instance(
        EvidenceCandidate,
        **{
            field.name: (
                "sha512"
                if field.name == "source_checksum_algorithm"
                else getattr(base, field.name)
            )
            for field in fields(EvidenceCandidate)
        },
    )
    request = _request(candidate=candidate)

    result = materialize_accepted_evidence(request)

    assert "unsupported_source_checksum_algorithm" in result.reason_codes


@pytest.mark.parametrize(
    "timestamp",
    (
        "2026-07-12T09:00:00",
        "2026-07-12 09:00:00",
        "not-a-timestamp",
    ),
)
def test_naive_or_invalid_candidate_timestamp_is_rejected(
    timestamp: str,
) -> None:
    base = _candidate()
    candidate = _unchecked_instance(
        EvidenceCandidate,
        **{
            field.name: (
                timestamp
                if field.name == "execution_timestamp"
                else getattr(base, field.name)
            )
            for field in fields(EvidenceCandidate)
        },
    )
    request = _request(candidate=candidate)

    result = materialize_accepted_evidence(request)

    assert "candidate_observed_at_mismatch" in result.reason_codes


def test_equivalent_offset_timestamp_is_accepted() -> None:
    request = _request(
        candidate=_candidate(
            execution_timestamp="2026-07-12T16:00:00+07:00"
        )
    )

    result = materialize_accepted_evidence(request)

    assert result.decision == MATERIALIZATION_DECISION_MATERIALIZED


def test_eligibility_not_eligible_is_rejected() -> None:
    request = _request()
    values = {
        field.name: getattr(request.eligibility_result, field.name)
        for field in fields(AcceptedEligibilityResult)
    }
    values["decision"] = "ineligible"
    eligibility = _unchecked_instance(AcceptedEligibilityResult, **values)
    request = _unchecked_instance(
        EvidenceMaterializationRequest,
        candidate=request.candidate,
        candidate_snapshot_result=request.candidate_snapshot_result,
        snapshot=request.snapshot,
        eligibility_result=eligibility,
        identity_result=request.identity_result,
        context=request.context,
    )

    result = materialize_accepted_evidence(request)

    assert "eligibility_not_eligible" in result.reason_codes


def test_eligibility_candidate_digest_mismatch_is_rejected() -> None:
    request = _request()
    eligibility = replace(
        request.eligibility_result,
        candidate_snapshot_digest="different-candidate-digest",
    )
    request = _request(
        eligibility_result=eligibility,
        identity_result=request.identity_result,
    )

    result = materialize_accepted_evidence(request)

    assert "eligibility_candidate_digest_mismatch" in result.reason_codes


def test_eligibility_source_id_mismatch_is_rejected() -> None:
    request = _request()
    eligibility = replace(
        request.eligibility_result,
        source_id="source-2",
    )
    request = _request(
        eligibility_result=eligibility,
        identity_result=request.identity_result,
    )

    result = materialize_accepted_evidence(request)

    assert "eligibility_source_id_mismatch" in result.reason_codes


def test_identity_result_is_recalculated_and_mismatch_is_rejected() -> None:
    request = _request()
    mismatched = EvidenceIdentityResult(
        evidence_id=f"ev1_{'0' * 64}",
        digest_algorithm=EVIDENCE_IDENTITY_DIGEST_ALGORITHM,
        digest_hex="0" * 64,
        identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
        canonicalization_contract_version=(
            EVIDENCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION
        ),
        canonical_byte_length=1,
    )
    request = replace(request, identity_result=mismatched)

    result = materialize_accepted_evidence(request)

    assert result.reason_codes == ("identity_result_mismatch",)


def test_identity_policy_mismatch_is_rejected_before_identity_comparison() -> None:
    request = _request()
    values = {
        field.name: getattr(request.identity_result, field.name)
        for field in fields(EvidenceIdentityResult)
    }
    values["identity_policy_id"] = "other-policy"
    identity_result = _unchecked_instance(EvidenceIdentityResult, **values)
    request = _unchecked_instance(
        EvidenceMaterializationRequest,
        candidate=request.candidate,
        candidate_snapshot_result=request.candidate_snapshot_result,
        snapshot=request.snapshot,
        eligibility_result=request.eligibility_result,
        identity_result=identity_result,
        context=request.context,
    )

    result = materialize_accepted_evidence(request)

    assert result.reason_codes == ("identity_policy_mismatch",)


def test_invalid_materialization_context_is_rejected() -> None:
    context = _unchecked_instance(
        EvidenceMaterializationContext,
        materializer_id="accepted-evidence-materializer",
        materializer_version="1.0.0",
        materialized_at=datetime(2026, 7, 12, 9, 0),
        acceptance_record_id="acceptance-record-1",
        accepted_by="review-service",
        acceptance_reason="Accepted",
        review_record_id="review-1",
    )
    base = _request()
    request = _unchecked_instance(
        EvidenceMaterializationRequest,
        candidate=base.candidate,
        candidate_snapshot_result=base.candidate_snapshot_result,
        snapshot=base.snapshot,
        eligibility_result=base.eligibility_result,
        identity_result=base.identity_result,
        context=context,
    )

    result = materialize_accepted_evidence(request)

    assert result.reason_codes == ("materialization_context_invalid",)


def test_invalid_snapshot_diagnostics_are_rejected() -> None:
    base = _request()
    snapshot = _unchecked_instance(
        EvidenceMaterializationSnapshot,
        accepted_evidence_contract_version=(
            base.snapshot.accepted_evidence_contract_version
        ),
        source_snapshot=base.snapshot.source_snapshot,
        producer_snapshot=base.snapshot.producer_snapshot,
        factual_payload=base.snapshot.factual_payload,
        provenance=base.snapshot.provenance,
        diagnostics=("not-a-diagnostic",),
    )
    request = _unchecked_instance(
        EvidenceMaterializationRequest,
        candidate=base.candidate,
        candidate_snapshot_result=base.candidate_snapshot_result,
        snapshot=snapshot,
        eligibility_result=base.eligibility_result,
        identity_result=base.identity_result,
        context=base.context,
    )

    result = materialize_accepted_evidence(request)

    assert result.reason_codes == ("diagnostics_invalid",)


@pytest.mark.parametrize("invalid_request", (None, object(), "request"))
def test_non_request_input_is_rejected(invalid_request: object) -> None:
    result = materialize_accepted_evidence(invalid_request)

    assert result.decision == MATERIALIZATION_DECISION_REJECTED
    assert result.reason_codes == ("request_invalid",)
    assert result.accepted_evidence is None


def test_rejection_reason_codes_use_deterministic_order_without_duplicates() -> None:
    candidate = _candidate(
        source_id="source-2",
        source_checksum_algorithm="sha512",
        source_checksum="a" * 128,
        errors=("producer-error",),
    )
    snapshot = _snapshot(
        source_snapshot=_source_snapshot(
            source_content_digest="a" * 128,
        )
    )
    request = _request(
        candidate=candidate,
        snapshot=snapshot,
        identity_result=_request().identity_result,
    )

    result = materialize_accepted_evidence(request)

    assert result.reason_codes == tuple(
        reason_code
        for reason_code in MATERIALIZATION_REJECTION_REASON_CODES
        if reason_code in {
            "candidate_has_errors",
            "unsupported_source_checksum_algorithm",
            "candidate_source_id_mismatch",
        }
    )
    assert len(result.reason_codes) == len(set(result.reason_codes))


def test_rejection_diagnostics_match_reason_codes() -> None:
    result = materialize_accepted_evidence(
        _request(candidate=_candidate(errors=("producer-error",)))
    )

    assert tuple(item.code for item in result.diagnostics) == result.reason_codes
    assert all(item.severity == "warning" for item in result.diagnostics)
    assert all(
        item.source == "accepted-evidence-materializer"
        for item in result.diagnostics
    )


def test_materialization_does_not_mutate_any_input_contract() -> None:
    request = _request()
    before = repr(request)

    result = materialize_accepted_evidence(request)

    assert repr(request) == before
    assert request.snapshot.source_snapshot is (
        result.accepted_evidence.source_snapshot
    )
    assert request.snapshot.factual_payload is (
        result.accepted_evidence.factual_payload
    )


def test_materialization_is_deterministic_for_same_request() -> None:
    request = _request()

    results = tuple(materialize_accepted_evidence(request) for _ in range(5))

    assert len(set(results)) == 1


def test_result_rejects_unknown_reason_code() -> None:
    with pytest.raises(ValueError, match="approved reason code"):
        EvidenceMaterializationResult(
            decision="rejected",
            accepted_evidence=None,
            reason_codes=("not-approved",),
            diagnostics=(_diagnostic(),),
        )


def test_result_rejects_out_of_order_reason_codes() -> None:
    with pytest.raises(ValueError, match="deterministic approved order"):
        EvidenceMaterializationResult(
            decision="rejected",
            accepted_evidence=None,
            reason_codes=(
                "request_invalid",
                "candidate_has_errors",
            ),
            diagnostics=(_diagnostic(),),
        )


def test_result_rejects_duplicate_reason_codes() -> None:
    with pytest.raises(ValueError, match="duplicates"):
        EvidenceMaterializationResult(
            decision="rejected",
            accepted_evidence=None,
            reason_codes=(
                "request_invalid",
                "request_invalid",
            ),
            diagnostics=(_diagnostic(),),
        )


@pytest.mark.parametrize(
    ("decision", "accepted_evidence", "reason_codes", "diagnostics"),
    (
        ("materialized", None, (), ()),
        ("materialized", object(), (), ()),
        ("rejected", _request(), ("request_invalid",), (_diagnostic(),)),
        ("rejected", None, (), (_diagnostic(),)),
        ("rejected", None, ("request_invalid",), ()),
        ("other", None, ("request_invalid",), (_diagnostic(),)),
    ),
)
def test_result_contract_rejects_invalid_decision_shapes(
    decision: str,
    accepted_evidence: object,
    reason_codes: tuple[str, ...],
    diagnostics: tuple[EvidenceDiagnostic, ...],
) -> None:
    with pytest.raises(ValueError):
        EvidenceMaterializationResult(
            decision=decision,
            accepted_evidence=accepted_evidence,
            reason_codes=reason_codes,
            diagnostics=diagnostics,
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("accepted_evidence_contract_version", " "),
        ("source_snapshot", object()),
        ("producer_snapshot", object()),
        ("factual_payload", object()),
        ("provenance", object()),
        ("diagnostics", []),
    ),
)
def test_snapshot_contract_rejects_invalid_fields(
    field_name: str,
    value: object,
) -> None:
    values = {
        field.name: getattr(_snapshot(), field.name)
        for field in fields(EvidenceMaterializationSnapshot)
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        EvidenceMaterializationSnapshot(**values)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("materializer_id", " "),
        ("materializer_version", ""),
        ("materialized_at", datetime(2026, 7, 12, 9, 0)),
        ("acceptance_record_id", " "),
        ("accepted_by", ""),
        ("acceptance_reason", " "),
        ("review_record_id", ""),
    ),
)
def test_context_contract_rejects_invalid_fields(
    field_name: str,
    value: object,
) -> None:
    values = {
        field.name: getattr(_context(), field.name)
        for field in fields(EvidenceMaterializationContext)
    }
    values[field_name] = value

    with pytest.raises(ValueError):
        EvidenceMaterializationContext(**values)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("candidate", object()),
        ("candidate_snapshot_result", object()),
        ("snapshot", object()),
        ("eligibility_result", object()),
        ("identity_result", object()),
        ("context", object()),
    ),
)
def test_request_contract_requires_exact_types(
    field_name: str,
    value: object,
) -> None:
    request = _request()
    values = {
        field.name: getattr(request, field.name)
        for field in fields(EvidenceMaterializationRequest)
    }
    values[field_name] = value

    with pytest.raises(ValueError, match=field_name):
        EvidenceMaterializationRequest(**values)


def test_materializer_module_has_no_repository_or_downstream_exports() -> None:
    import rie.application.evidence_materializer as module

    assert not hasattr(module, "EvidenceRepository")
    assert not hasattr(module, "Knowledge")
    assert not hasattr(module, "KnowledgeRepository")
    assert not hasattr(module, "PromptCandidate")
    assert not hasattr(module, "AcceptedEvidenceMaterializer")
