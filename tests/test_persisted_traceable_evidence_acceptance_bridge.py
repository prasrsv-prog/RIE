from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
from unittest.mock import patch

import pytest

from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
)
from rie.domain.evidence_identity import (
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)
from rie.evidence_materialization.atomic_text_evidence_derivation import (
    ATOMIC_TEXT_DERIVATION_PROVENANCE_CONTRACT_VERSION,
    ATOMIC_TEXT_DERIVATION_TYPE,
)
from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_collection_id,
    derive_evidence_eligibility_snapshot_digest,
    derive_traceable_evidence_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_CONTENT_TYPE,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    TraceableEvidence,
    TraceableEvidenceAtomicTextDerivationProvenance,
    TraceableEvidenceOcrRemediationProvenance,
    TraceableEvidenceProvenance,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
    calculate_evidence_repository_audit_id,
    calculate_evidence_repository_revision_id,
)
from rie.evidence_repository.evidence_repository_contract import (
    EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
    EvidenceRepositoryAuditRecord,
    EvidenceRepositoryLookupResult,
    EvidenceRepositoryRevision,
)
import rie.persisted_evidence_knowledge_construction.persisted_traceable_evidence_acceptance_bridge as bridge_module
from rie.persisted_evidence_knowledge_construction.persisted_traceable_evidence_acceptance_bridge import (
    ACCEPTANCE_RECORD_CONTRACT_VERSION,
    ACCEPTED_EVIDENCE_CONTRACT_VERSION,
    PILOT_FFS21_ACCEPTANCE_POLICY_ID,
    PILOT_FFS21_ACCEPTANCE_POLICY_VERSION,
    PILOT_FFS21_ACCEPTANCE_REASON,
    PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS,
    PILOT_FFS21_MATERIALIZER_ID,
    PILOT_FFS21_MATERIALIZER_VERSION,
    PILOT_FFS21_PRIMARY_OPERATOR,
    BRIDGE_STATUS_MATERIALIZED,
    BRIDGE_STATUS_REJECTED,
    PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_ID,
    PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_VERSION,
    PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_REQUEST_CONTRACT_VERSION,
    PersistedTraceableEvidenceAcceptanceBridgeRequest,
    materialize_persisted_traceable_evidence_acceptance,
)


FIXED = datetime(2026, 8, 17, 4, 30, tzinfo=timezone.utc)


def _shell(cls, **values):
    value = object.__new__(cls)
    for name, item in values.items():
        object.__setattr__(value, name, item)
    return value


def _snapshot() -> EvidenceEligibilitySnapshot:
    return EvidenceEligibilitySnapshot(
        contract_version=EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
        source_id="source-test",
        source_path="official/test.pdf",
        source_checksum="a" * 64,
        source_type="pdf",
        document_classification="official_knowledge_base",
        authority_status="official",
        lifecycle_status="active",
        evidence_eligibility="eligible",
        evidence_collection_allowed=True,
        requires_review=False,
        reason="explicitly_eligible",
        policy_id="test-source-eligibility-policy",
        policy_version="1.0.0",
        registry_version="registry-v1",
    )


def _target(snapshot: EvidenceEligibilitySnapshot) -> TraceableEvidence:
    content = "M: 57-58 cm"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    provenance = TraceableEvidenceProvenance(
        artifact_contract_version="extraction_artifact_contract_v2",
        artifact_id="b" * 64,
        upstream_contract_version="upstream-contract-v1",
        job_id="job-test",
        source_id=snapshot.source_id,
        source_path=snapshot.source_path,
        source_checksum=snapshot.source_checksum,
        page_index=0,
        page_number=1,
        extraction_index=0,
        extraction_method="embedded_text",
        extraction_status="completed",
        execution_report_location="memory://test-report",
    )
    ocr = TraceableEvidenceOcrRemediationProvenance(
        producer_operation_id="test-producer-operation",
        producer_artifact_path="test-artifact.txt",
        producer_artifact_sha256="c" * 64,
        producer_artifact_set_digest="d" * 64,
        extraction_method="bounded_local_ocr",
    )
    atomic = TraceableEvidenceAtomicTextDerivationProvenance(
        contract_version=ATOMIC_TEXT_DERIVATION_PROVENANCE_CONTRACT_VERSION,
        derivation_type=ATOMIC_TEXT_DERIVATION_TYPE,
        parent_traceable_evidence_id="evm1_" + ("e" * 64),
        parent_content_digest="f" * 64,
        source_span_ids=("span-test-0001",),
        operator_decision_packet_sha256="1" * 64,
        atomic_statement_sha256=digest,
    )
    provisional = _shell(
        TraceableEvidence,
        contract_version=TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
        evidence_id="evm1_" + ("0" * 64),
        content_type=TRACEABLE_EVIDENCE_CONTENT_TYPE,
        content=content,
        content_digest=digest,
        warnings=(),
        provenance=provenance,
        eligibility_snapshot_digest=derive_evidence_eligibility_snapshot_digest(
            snapshot
        ),
        ocr_remediation_provenance=ocr,
        atomic_text_derivation_provenance=atomic,
    )
    evidence_id = derive_traceable_evidence_id(provisional)
    return TraceableEvidence(
        contract_version=TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
        evidence_id=evidence_id,
        content_type=TRACEABLE_EVIDENCE_CONTENT_TYPE,
        content=content,
        content_digest=digest,
        warnings=(),
        provenance=provenance,
        eligibility_snapshot_digest=derive_evidence_eligibility_snapshot_digest(
            snapshot
        ),
        ocr_remediation_provenance=ocr,
        atomic_text_derivation_provenance=atomic,
    )


def _collection() -> EvidenceCollection:
    snapshot = _snapshot()
    target = _target(snapshot)
    values = dict(
        contract_version=EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
        collection_id="evc1_" + ("0" * 64),
        artifact_contract_version=target.provenance.artifact_contract_version,
        artifact_id=target.provenance.artifact_id,
        upstream_contract_version=target.provenance.upstream_contract_version,
        job_id=target.provenance.job_id,
        source_id=snapshot.source_id,
        source_path=snapshot.source_path,
        source_checksum=snapshot.source_checksum,
        eligibility_snapshot=snapshot,
        evidence_items=(target,),
    )
    provisional = _shell(EvidenceCollection, **values)
    values["collection_id"] = derive_evidence_collection_id(provisional)
    return EvidenceCollection(**values)


def _lookup() -> EvidenceRepositoryLookupResult:
    collection = _collection()
    payload_digest = calculate_evidence_collection_repository_payload_digest(
        collection
    )
    revision_id = calculate_evidence_repository_revision_id(
        source_id=collection.source_id,
        revision_number=2,
        collection_id=collection.collection_id,
        collection_payload_digest=payload_digest,
        previous_revision_id="evr1_" + ("2" * 64),
    )
    audit_id = calculate_evidence_repository_audit_id(
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=2,
        collection_id=collection.collection_id,
        actor_id="test-repository-writer",
        recorded_at_utc=FIXED,
    )
    revision = EvidenceRepositoryRevision(
        contract_version=EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=2,
        collection_id=collection.collection_id,
        collection_payload_digest=payload_digest,
        previous_revision_id="evr1_" + ("2" * 64),
        actor_id="test-repository-writer",
        recorded_at_utc=FIXED,
        audit_id=audit_id,
    )
    audit = EvidenceRepositoryAuditRecord(
        contract_version=EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
        audit_id=audit_id,
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=2,
        collection_id=collection.collection_id,
        actor_id="test-repository-writer",
        recorded_at_utc=FIXED,
    )
    return EvidenceRepositoryLookupResult(
        contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="found",
        revision=revision,
        audit_record=audit,
        collection=collection,
        issue=None,
    )


def _request(**changes):
    lookup = changes.pop("repository_lookup_result", _lookup())
    target = lookup.collection.evidence_items[0]
    values = dict(
        contract_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_REQUEST_CONTRACT_VERSION
        ),
        repository_lookup_result=lookup,
        target_traceable_evidence_id=target.evidence_id,
        accepted_by=PILOT_FFS21_PRIMARY_OPERATOR,
        acceptance_reason=PILOT_FFS21_ACCEPTANCE_REASON,
        review_record_id="test-review-record",
        accepted_at=FIXED,
        acceptance_policy_id=PILOT_FFS21_ACCEPTANCE_POLICY_ID,
        acceptance_policy_version=PILOT_FFS21_ACCEPTANCE_POLICY_VERSION,
        materializer_id=PILOT_FFS21_MATERIALIZER_ID,
        materializer_version=PILOT_FFS21_MATERIALIZER_VERSION,
        eligibility_evaluated_by=PILOT_FFS21_PRIMARY_OPERATOR,
        eligibility_evaluated_at=FIXED,
        provenance_observed_at=FIXED,
        compatibility_policy_id=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_ID
        ),
        compatibility_policy_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_VERSION
        ),
    )
    values.update(changes)
    return PersistedTraceableEvidenceAcceptanceBridgeRequest(**values)


def _materialize_authorized_test_target(request):
    with patch.object(
        bridge_module,
        "PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS",
        frozenset({request.target_traceable_evidence_id}),
    ):
        return materialize_persisted_traceable_evidence_acceptance(request)


def test_production_scope_allowlist_is_exact_five_approved_ids():
    assert PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS == frozenset(
        {
            "evm1_a3e18a4f76968b308e10cf1f0c9de37f709336e6a0f0c2b25515cd98e9d88499",
            "evm1_0bab2e3d3f2ef04b39660d287c7479ce5967027ecf8fb61092b1a72a533db1d0",
            "evm1_32f14d29ef3880b87a658962bdbe6b63c361e6c6c8c2ce6c8d13669948f6c3eb",
            "evm1_57f2bd478bb59f16aa6cd2114d70fdef7e70ddbfb7dd317e166946cd539e6607",
            "evm1_1d00dc2e1cb02e5d1b6510f8e1598ff2c9bcd1df3b6df21b38725e5437536c94",
        }
    )


def test_unapproved_target_fails_closed_before_repository_projection():
    request = _request()
    result = materialize_persisted_traceable_evidence_acceptance(request)
    assert result.status == BRIDGE_STATUS_REJECTED
    assert result.accepted_evidence is None
    assert result.acceptance_record is None
    assert result.reason_codes == (
        "target_traceable_evidence_outside_approved_five_fact_scope",
    )


def test_materializes_exact_legacy_contracts_from_persisted_v3_plus_explicit_metadata():
    request = _request()
    target = request.repository_lookup_result.collection.evidence_items[0]
    result = _materialize_authorized_test_target(request)

    assert result.status == BRIDGE_STATUS_MATERIALIZED
    assert result.reason_codes == ()
    assert result.target_traceable_evidence_id == target.evidence_id
    assert result.accepted_evidence.contract_version == ACCEPTED_EVIDENCE_CONTRACT_VERSION
    assert result.acceptance_record.contract_version == ACCEPTANCE_RECORD_CONTRACT_VERSION

    evidence = result.accepted_evidence
    acceptance = result.acceptance_record
    assert evidence.source_snapshot.source_id == target.provenance.source_id
    assert evidence.source_snapshot.source_content_digest == target.provenance.source_checksum
    assert evidence.factual_payload.payload_type == "text"
    assert evidence.factual_payload.payload_schema_version == "1.0.0"
    assert evidence.factual_payload.payload == (("text", target.content),)
    assert evidence.factual_payload.payload_digest == target.content_digest
    assert evidence.candidate_reference.candidate_snapshot_digest == target.content_digest
    assert evidence.provenance.lineage[0] == target.evidence_id
    assert evidence.provenance.lineage[1] == (
        target.atomic_text_derivation_provenance.parent_traceable_evidence_id
    )
    assert acceptance.accepted_by == request.accepted_by
    assert acceptance.acceptance_reason == request.acceptance_reason
    assert acceptance.review_record_id == request.review_record_id
    assert acceptance.accepted_at == request.accepted_at
    assert acceptance.evidence_id == evidence.evidence_id


def test_bridge_outputs_recompute_existing_deterministic_identities():
    result = _materialize_authorized_test_target(_request())
    assert result.status == BRIDGE_STATUS_MATERIALIZED
    evidence_identity = calculate_evidence_identity(
        identity_input_from_accepted_evidence(result.accepted_evidence)
    )
    acceptance_identity = calculate_acceptance_identity(
        acceptance_identity_input_from_record(result.acceptance_record)
    )
    assert result.accepted_evidence.evidence_id == evidence_identity.evidence_id
    assert (
        result.acceptance_record.acceptance_record_id
        == acceptance_identity.acceptance_record_id
    )


def test_exact_replay_is_deterministic():
    request = _request()
    first = _materialize_authorized_test_target(request)
    second = _materialize_authorized_test_target(request)
    assert first == second


def test_explicit_acceptance_metadata_changes_acceptance_identity_not_factual_identity():
    base = _request()
    changed = _request(
        repository_lookup_result=base.repository_lookup_result,
        review_record_id="other-test-review",
        accepted_at=FIXED + timedelta(seconds=1),
        eligibility_evaluated_at=FIXED + timedelta(seconds=1),
        provenance_observed_at=FIXED + timedelta(seconds=1),
    )
    first = _materialize_authorized_test_target(base)
    second = _materialize_authorized_test_target(changed)
    assert first.status == second.status == BRIDGE_STATUS_MATERIALIZED
    assert first.accepted_evidence.evidence_id == second.accepted_evidence.evidence_id
    assert (
        first.acceptance_record.acceptance_record_id
        != second.acceptance_record.acceptance_record_id
    )


def test_missing_target_fails_closed_without_outputs():
    request = _request(
        target_traceable_evidence_id="evm1_" + ("9" * 64)
    )
    result = _materialize_authorized_test_target(request)
    assert result.status == BRIDGE_STATUS_REJECTED
    assert result.accepted_evidence is None
    assert result.acceptance_record is None
    assert result.reason_codes == (
        "target_traceable_evidence_not_found_or_not_unique",
    )


def test_unapproved_acceptance_actor_is_rejected_at_request_boundary():
    with pytest.raises(ValueError, match="accepted_by"):
        _request(accepted_by="other-operator")


def test_unapproved_acceptance_policy_is_rejected_at_request_boundary():
    with pytest.raises(ValueError, match="acceptance policy"):
        _request(acceptance_policy_id="other-policy")


def test_unapproved_eligibility_actor_is_rejected_at_request_boundary():
    with pytest.raises(ValueError, match="eligibility_evaluated_by"):
        _request(eligibility_evaluated_by="other-operator")


def test_operation_timestamps_must_match():
    with pytest.raises(ValueError, match="eligibility_evaluated_at"):
        _request(eligibility_evaluated_at=FIXED + timedelta(seconds=1))
    with pytest.raises(ValueError, match="provenance_observed_at"):
        _request(provenance_observed_at=FIXED + timedelta(seconds=1))


def test_naive_explicit_timestamp_is_rejected_at_request_boundary():
    with pytest.raises(ValueError, match="accepted_at"):
        _request(accepted_at=datetime(2026, 8, 17, 4, 30))


def test_unsupported_bridge_policy_is_rejected_at_request_boundary():
    with pytest.raises(ValueError, match="compatibility policy"):
        _request(compatibility_policy_id="other")


def test_projection_uses_only_persisted_or_explicit_values_for_acceptance_surface():
    request = _request()
    target = request.repository_lookup_result.collection.evidence_items[0]
    result = _materialize_authorized_test_target(request)
    evidence = result.accepted_evidence
    acceptance = result.acceptance_record

    assert evidence.producer_snapshot.producer_name == target.provenance.extraction_method
    assert (
        evidence.producer_snapshot.producer_version
        == target.provenance.upstream_contract_version
    )
    assert evidence.producer_snapshot.producer_kind == target.provenance.extraction_status
    assert (
        evidence.producer_snapshot.producer_contract_version
        == target.provenance.artifact_contract_version
    )
    assert evidence.eligibility_result.policy_id == (
        request.repository_lookup_result.collection.eligibility_snapshot.policy_id
    )
    assert evidence.eligibility_result.evaluated_by == request.eligibility_evaluated_by
    assert evidence.eligibility_result.evaluated_at == request.eligibility_evaluated_at
    assert evidence.provenance.observed_at == request.provenance_observed_at
    assert acceptance.acceptance_policy_id == request.acceptance_policy_id
    assert acceptance.materializer_id == request.materializer_id
