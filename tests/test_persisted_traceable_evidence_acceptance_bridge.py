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
    authorized_test_target = frozenset({request.target_traceable_evidence_id})
    with patch.object(
        bridge_module,
        "PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS",
        authorized_test_target,
    ), patch.object(
        bridge_module,
        "PILOT_FFS21_APPROVED_ATOMIC_EVIDENCE_IDS",
        authorized_test_target,
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


def test_approved_runtime_scope_is_exact_five_plus_corrected_l():
    assert bridge_module.PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS == frozenset(
        {
            "evm1_a3e18a4f76968b308e10cf1f0c9de37f709336e6a0f0c2b25515cd98e9d88499",
            "evm1_0bab2e3d3f2ef04b39660d287c7479ce5967027ecf8fb61092b1a72a533db1d0",
            "evm1_32f14d29ef3880b87a658962bdbe6b63c361e6c6c8c2ce6c8d13669948f6c3eb",
            "evm1_57f2bd478bb59f16aa6cd2114d70fdef7e70ddbfb7dd317e166946cd539e6607",
            "evm1_1d00dc2e1cb02e5d1b6510f8e1598ff2c9bcd1df3b6df21b38725e5437536c94",
        }
    )
    assert bridge_module.PILOT_FFS21_CORRECTED_L_ATOMIC_EVIDENCE_ID == (
        "evm1_2abb90e9e4c753e5e857e91e2c894480df51a701d00f7489d1e19769f64afe86"
    )
    assert bridge_module.PILOT_FFS21_APPROVED_ATOMIC_EVIDENCE_IDS == (
        bridge_module.PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS
        | frozenset({bridge_module.PILOT_FFS21_CORRECTED_L_ATOMIC_EVIDENCE_ID})
    )
    assert len(bridge_module.PILOT_FFS21_APPROVED_ATOMIC_EVIDENCE_IDS) == 6


def test_corrected_l_target_requires_target_specific_acceptance_reason():
    request = _request(
        target_traceable_evidence_id=(
            bridge_module.PILOT_FFS21_CORRECTED_L_ATOMIC_EVIDENCE_ID
        ),
        acceptance_reason=bridge_module.PILOT_FFS21_CORRECTED_L_ACCEPTANCE_REASON,
    )
    assert request.acceptance_reason == (
        bridge_module.PILOT_FFS21_CORRECTED_L_ACCEPTANCE_REASON
    )
    with pytest.raises(ValueError, match="acceptance_reason"):
        _request(
            target_traceable_evidence_id=(
                bridge_module.PILOT_FFS21_CORRECTED_L_ATOMIC_EVIDENCE_ID
            ),
            acceptance_reason=PILOT_FFS21_ACCEPTANCE_REASON,
        )


def test_exact_five_target_rejects_corrected_l_acceptance_reason():
    exact_five_target = sorted(PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS)[0]
    with pytest.raises(ValueError, match="acceptance_reason"):
        _request(
            target_traceable_evidence_id=exact_five_target,
            acceptance_reason=bridge_module.PILOT_FFS21_CORRECTED_L_ACCEPTANCE_REASON,
        )


def test_corrected_l_reason_does_not_expand_outside_approved_six_scope():
    outside_target = "evm1_" + ("8" * 64)
    with pytest.raises(ValueError, match="acceptance_reason"):
        _request(
            target_traceable_evidence_id=outside_target,
            acceptance_reason=bridge_module.PILOT_FFS21_CORRECTED_L_ACCEPTANCE_REASON,
        )
    request = _request(target_traceable_evidence_id=outside_target)
    result = materialize_persisted_traceable_evidence_acceptance(request)
    assert result.status == BRIDGE_STATUS_REJECTED
    assert result.reason_codes == (
        "target_traceable_evidence_outside_approved_five_fact_scope",
    )


# PR-086FJ structured-v4 additive acceptance coverage.
from dataclasses import replace as _pr086fj_replace
from datetime import datetime as _pr086fj_datetime
from datetime import timezone as _pr086fj_timezone
from unittest.mock import patch as _pr086fj_patch

from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
    EvidenceEligibilitySnapshot,
    TraceableEvidenceStructuredMetadataProvenance,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest as _pr086fj_payload_digest,
    calculate_evidence_repository_audit_id as _pr086fj_audit_id,
    calculate_evidence_repository_revision_id as _pr086fj_revision_id,
)
from rie.evidence_repository.evidence_repository_contract import (
    EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
    EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
    EvidenceRepositoryAuditRecord,
    EvidenceRepositoryLookupResult,
    EvidenceRepositoryRevision,
)
from rie.rsv_knowledge.product_variant_identity_bridge import (
    BRIDGE_STATUS_CONSTRUCTED as _PR086FJ_PRODUCT_VARIANT_CONSTRUCTED,
    PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION,
    PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_ID,
    PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE,
    ProductVariantIdentityCandidateConstructionRequest,
    ProductVariantIdentityEvidenceAdmissionRequest,
    ProductVariantIdentityEvidenceAdmissionUnit,
    construct_product_variant_identity_candidate_from_real_accepted_evidence,
)
from rie.rsv_knowledge.product_variant_identity_evidence_binding import (
    PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256,
    PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SOURCE_ID,
    PILOT_PRODUCT_VARIANT_IDENTITY_AUTHORITY_STATUS,
    PILOT_PRODUCT_VARIANT_IDENTITY_DOCUMENT_CLASSIFICATION,
    PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_ID,
    PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_VERSION,
    PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REASON,
    PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REGISTRY_VERSION,
    PILOT_PRODUCT_VARIANT_IDENTITY_LIFECYCLE_STATUS,
    PILOT_PRODUCT_VARIANT_IDENTITY_SOURCE_TYPE,
    PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_REQUEST_CONTRACT_VERSION,
    ProductVariantIdentityStructuredMetadataEvidenceBindingRequest,
    materialize_product_variant_identity_structured_metadata_evidence_binding,
)


_PR086FJ_EXACT18 = frozenset(('evm1_009c6c903d897e9bd67bef3852e947cb5d5f66ac21672c44ebb30227e3a4c202', 'evm1_0ad37b5cd8765d292143f98a31a0dcb7b31dced09b7c13e19f4eecd358f784de', 'evm1_24cd78892b74ca07a87a5e04b141ae056c7c7b287f04367d5fc5fd9afa9a7b26', 'evm1_2ada2177e9ad3b79e0dca72cc9e4e85fefed8dd713771d20fdf1fea747ad2eb2', 'evm1_2e10a2610d2e3d07dcfbebcd5baa28ccb7792981beb72643de50e52714ce484a', 'evm1_2e350a8d1b61ce11ad4d4b25218a0ae5ab8de8f524a9037611cafa0a8c988e6e', 'evm1_3353406b885d205d9fd0dce93022e93e37a8a805e10df089722f847f6259e8f7', 'evm1_54956c4f8205ae61a73c041cf75c7237ae593f2249351cfe0de1d2fa4ae50f2e', 'evm1_6daf9d7af75892b728a8c5fa57b6be68b45327aaccb3a1e0664dd96cd4732bf9', 'evm1_8088836878d452f73aff7c26ba36b66683144576c3ca804297f361a0449382c1', 'evm1_95c87a9869239eba36478468f77aa14e1c4f32a228992017b861bbbfe7f0c5a9', 'evm1_bdd92e5807c49621bde8390393dff1d84d8034dc36516cf8a35b1320c66189dd', 'evm1_c0275e89aa2619b80cb6a7a2489e8871e9e2199010d1eda8d705645fbfc9a2d4', 'evm1_cbe10029707a5ae58e0e2211c2c92de3f8f46dffcf1df98564412d50195b1b96', 'evm1_dd86d5b43d2d0d32e20e60a161f80a09a5f053e1d02e2de4a91b45361c7ae193', 'evm1_e20d39d207e4d133741c8ce091b43e27e1d3215d2cf6c00ed62049f42529505a', 'evm1_e5080797d36e0bfd898225ffcc7345a50c3ff092be0f741220ba1c0912e88069', 'evm1_ee617df3d287341953b5e40556122f0a648b64dacd52dfdf402de489b1003217'))
_PR086FJ_FIXED = _pr086fj_datetime(
    2026, 8, 23, 7, 30, 0, tzinfo=_pr086fj_timezone.utc
)


def _pr086fj_unit():
    return ProductVariantIdentityEvidenceAdmissionUnit(
        atomic_knowledge_id="knowledge-sv300-black-glossy-variant-identity",
        knowledge_kind="product_variant_identity",
        atomic_statement=(
            "variant_id=sv300-black-glossy; product_id=sv300; "
            "variant_name=Black Glossy"
        ),
        product_family="SV300",
        product_id="sv300",
        variant_id="sv300-black-glossy",
        variant_name_verbatim="Black Glossy",
        source_type="APPROVED_PRODUCT_PHOTO",
        source_authority="RSV_INTERNAL_APPROVED_SOURCE",
        source_status="APPROVED",
        source_version="2026-08-09",
        source_relative_paths=(
            "SV300/Black Glossy/01.jpg",
            "SV300/Black Glossy/02.jpg",
        ),
        manifest_sha256="a" * 64,
        identity_capture_sha256="b" * 64,
        atomic_construction_authority_decision_packet_sha256="c" * 64,
        downstream_binding_policy_decision_packet_sha256="d" * 64,
    )


def _pr086fj_binding():
    admissions = []
    first_unit = None
    for index in range(18):
        path_count = 7 if index == 0 else 6
        paths = tuple(
            f"official/variant-{index:02d}/asset-{path_index:02d}.jpg"
            for path_index in range(path_count)
        )
        unit = ProductVariantIdentityEvidenceAdmissionUnit(
            atomic_knowledge_id=f"atomic-variant-{index:02d}",
            knowledge_kind="product_variant_identity",
            atomic_statement=(
                f"Variant {index:02d} is an approved product variant."
            ),
            product_family="pilot-family",
            product_id=f"pilot-product-{index:02d}",
            variant_id=f"pilot-variant-{index:02d}",
            variant_name_verbatim=f"Pilot Variant {index:02d}",
            source_type="official_asset",
            source_authority="official",
            source_status="locked",
            source_version="1",
            source_relative_paths=paths,
            manifest_sha256="a" * 64,
            identity_capture_sha256="b" * 64,
            atomic_construction_authority_decision_packet_sha256="c" * 64,
            downstream_binding_policy_decision_packet_sha256="d" * 64,
        )
        if first_unit is None:
            first_unit = unit
        admissions.append(
            ProductVariantIdentityEvidenceAdmissionRequest(
                contract_version=(
                    PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION
                ),
                unit=unit,
            )
        )
    assert first_unit is not None
    assert len(admissions) == 18
    assert sum(
        len(value.unit.source_relative_paths) for value in admissions
    ) == 109

    snapshot = EvidenceEligibilitySnapshot(
        contract_version=EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
        source_id=PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SOURCE_ID,
        source_path=(
            "pilot-phase-a-product-variant-identity-atomic-knowledge-"
            "construction-result.json"
        ),
        source_checksum=PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256,
        source_type=PILOT_PRODUCT_VARIANT_IDENTITY_SOURCE_TYPE,
        document_classification=(
            PILOT_PRODUCT_VARIANT_IDENTITY_DOCUMENT_CLASSIFICATION
        ),
        authority_status=PILOT_PRODUCT_VARIANT_IDENTITY_AUTHORITY_STATUS,
        lifecycle_status=PILOT_PRODUCT_VARIANT_IDENTITY_LIFECYCLE_STATUS,
        evidence_eligibility="eligible",
        evidence_collection_allowed=True,
        requires_review=False,
        reason=PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REASON,
        policy_id=PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_ID,
        policy_version=PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_POLICY_VERSION,
        registry_version=PILOT_PRODUCT_VARIANT_IDENTITY_ELIGIBILITY_REGISTRY_VERSION,
    )
    request = ProductVariantIdentityStructuredMetadataEvidenceBindingRequest(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_STRUCTURED_METADATA_EVIDENCE_BINDING_REQUEST_CONTRACT_VERSION
        ),
        admission_requests=tuple(admissions),
        eligibility_snapshot=snapshot,
        artifact_contract_version="product_variant_identity_atomic_result_v1",
        artifact_id=PILOT_PRODUCT_VARIANT_IDENTITY_ATOMIC_RESULT_SHA256,
        upstream_contract_version="product_variant_identity_atomic_construction_v1",
        job_id="pr086fj-c1-structured-v4-test",
        actor_id=bridge_module.PILOT_FFS21_PRIMARY_OPERATOR,
        recorded_at_utc=_PR086FJ_FIXED,
    )
    return (
        first_unit,
        materialize_product_variant_identity_structured_metadata_evidence_binding(
            request
        ),
    )


def _pr086fj_lookup(collection):
    payload_digest = _pr086fj_payload_digest(collection)
    revision_id = _pr086fj_revision_id(
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=payload_digest,
        previous_revision_id=None,
    )
    audit_id = _pr086fj_audit_id(
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="test-repository-writer",
        recorded_at_utc=_PR086FJ_FIXED,
    )
    revision = EvidenceRepositoryRevision(
        contract_version=EVIDENCE_REPOSITORY_REVISION_CONTRACT_VERSION,
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=payload_digest,
        previous_revision_id=None,
        actor_id="test-repository-writer",
        recorded_at_utc=_PR086FJ_FIXED,
        audit_id=audit_id,
    )
    audit = EvidenceRepositoryAuditRecord(
        contract_version=EVIDENCE_REPOSITORY_AUDIT_RECORD_CONTRACT_VERSION,
        audit_id=audit_id,
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="test-repository-writer",
        recorded_at_utc=_PR086FJ_FIXED,
    )
    return EvidenceRepositoryLookupResult(
        contract_version=EVIDENCE_REPOSITORY_LOOKUP_RESULT_CONTRACT_VERSION,
        status="found",
        revision=revision,
        audit_record=audit,
        collection=collection,
        issue=None,
    )


def _pr086fj_request(lookup):
    target = lookup.collection.evidence_items[0]
    return PersistedTraceableEvidenceAcceptanceBridgeRequest(
        contract_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_REQUEST_CONTRACT_VERSION
        ),
        repository_lookup_result=lookup,
        target_traceable_evidence_id=target.evidence_id,
        accepted_by=bridge_module.PILOT_FFS21_PRIMARY_OPERATOR,
        acceptance_reason=(
            bridge_module.PILOT_PRODUCT_VARIANT_STRUCTURED_ACCEPTANCE_REASON
        ),
        review_record_id=(
            bridge_module.PILOT_PRODUCT_VARIANT_STRUCTURED_REVIEW_RECORD_ID
        ),
        accepted_at=_PR086FJ_FIXED,
        acceptance_policy_id=bridge_module.PILOT_FFS21_ACCEPTANCE_POLICY_ID,
        acceptance_policy_version=(
            bridge_module.PILOT_FFS21_ACCEPTANCE_POLICY_VERSION
        ),
        materializer_id=bridge_module.PILOT_FFS21_MATERIALIZER_ID,
        materializer_version=bridge_module.PILOT_FFS21_MATERIALIZER_VERSION,
        eligibility_evaluated_by=bridge_module.PILOT_FFS21_PRIMARY_OPERATOR,
        eligibility_evaluated_at=_PR086FJ_FIXED,
        provenance_observed_at=_PR086FJ_FIXED,
        compatibility_policy_id=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_ID
        ),
        compatibility_policy_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_VERSION
        ),
    )


def _pr086fj_materialize():
    unit, binding = _pr086fj_binding()
    target = binding.collection.evidence_items[0]
    lookup = _pr086fj_lookup(binding.collection)
    with _pr086fj_patch.object(
        bridge_module,
        "PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS",
        frozenset({target.evidence_id}),
    ):
        request = _pr086fj_request(lookup)
        result = materialize_persisted_traceable_evidence_acceptance(request)
    return unit, target, result


def test_pr086fj_structured_scope_matches_exact18_operator_authority():
    assert (
        bridge_module.PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS
        == _PR086FJ_EXACT18
    )
    assert len(bridge_module.PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS) == 18
    assert bridge_module.PILOT_FFS21_APPROVED_ATOMIC_EVIDENCE_IDS.isdisjoint(
        bridge_module.PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS
    )


def test_pr086fj_structured_request_requires_exact_reason_and_review():
    _, binding = _pr086fj_binding()
    target = binding.collection.evidence_items[0]
    lookup = _pr086fj_lookup(binding.collection)
    with _pr086fj_patch.object(
        bridge_module,
        "PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS",
        frozenset({target.evidence_id}),
    ):
        request = _pr086fj_request(lookup)
        with pytest.raises(ValueError, match="acceptance_reason"):
            _pr086fj_replace(
                request,
                acceptance_reason=PILOT_FFS21_ACCEPTANCE_REASON,
            )
        with pytest.raises(ValueError, match="review_record_id"):
            _pr086fj_replace(
                request,
                review_record_id="other-review",
            )


def test_pr086fj_structured_v4_materializes_without_page_provenance():
    unit, target, result = _pr086fj_materialize()
    assert result.status == BRIDGE_STATUS_MATERIALIZED
    assert result.reason_codes == ()
    assert (
        type(target.provenance)
        is TraceableEvidenceStructuredMetadataProvenance
    )
    assert (
        target.contract_version
        == TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION
    )
    assert not hasattr(target.provenance, "page_index")
    assert result.accepted_evidence.factual_payload.payload_type == (
        PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE
    )
    assert result.accepted_evidence.factual_payload.payload_schema_version == (
        PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION
    )
    assert dict(result.accepted_evidence.factual_payload.payload)[
        "atomic_statement"
    ] == unit.atomic_statement
    assert dict(result.accepted_evidence.factual_payload.payload)[
        "source_relative_paths"
    ] == unit.source_relative_paths
    assert result.accepted_evidence.factual_payload.locator.locator_value == (
        unit.atomic_knowledge_id
    )
    assert result.accepted_evidence.evidence_id == calculate_evidence_identity(
        identity_input_from_accepted_evidence(result.accepted_evidence)
    ).evidence_id
    assert result.acceptance_record.acceptance_record_id == (
        calculate_acceptance_identity(
            acceptance_identity_input_from_record(result.acceptance_record)
        ).acceptance_record_id
    )


def test_pr086fj_structured_v4_exact_replay_is_deterministic():
    _, binding = _pr086fj_binding()
    target = binding.collection.evidence_items[0]
    lookup = _pr086fj_lookup(binding.collection)
    with _pr086fj_patch.object(
        bridge_module,
        "PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS",
        frozenset({target.evidence_id}),
    ):
        request = _pr086fj_request(lookup)
        first = materialize_persisted_traceable_evidence_acceptance(request)
        second = materialize_persisted_traceable_evidence_acceptance(request)
    assert first == second


def test_pr086fj_structured_accepted_evidence_reaches_candidate_bridge():
    unit, _, result = _pr086fj_materialize()
    candidate_request = ProductVariantIdentityCandidateConstructionRequest(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
        ),
        unit=unit,
        accepted_evidence=result.accepted_evidence,
        acceptance_records=(result.acceptance_record,),
        construction_rule_id=PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_ID,
        construction_rule_version=PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_VERSION,
    )
    candidate_result = (
        construct_product_variant_identity_candidate_from_real_accepted_evidence(
            candidate_request
        )
    )
    assert candidate_result.status == _PR086FJ_PRODUCT_VARIANT_CONSTRUCTED
    assert candidate_result.reason_codes == ()
    assert candidate_result.knowledge_candidate.statement == unit.atomic_statement


def test_pr086fj_structured_v4_outside_exact_scope_still_rejects():
    _, binding = _pr086fj_binding()
    lookup = _pr086fj_lookup(binding.collection)
    target = lookup.collection.evidence_items[0]
    request = PersistedTraceableEvidenceAcceptanceBridgeRequest(
        contract_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_REQUEST_CONTRACT_VERSION
        ),
        repository_lookup_result=lookup,
        target_traceable_evidence_id=target.evidence_id,
        accepted_by=bridge_module.PILOT_FFS21_PRIMARY_OPERATOR,
        acceptance_reason=PILOT_FFS21_ACCEPTANCE_REASON,
        review_record_id="legacy-compatible-review",
        accepted_at=_PR086FJ_FIXED,
        acceptance_policy_id=bridge_module.PILOT_FFS21_ACCEPTANCE_POLICY_ID,
        acceptance_policy_version=(
            bridge_module.PILOT_FFS21_ACCEPTANCE_POLICY_VERSION
        ),
        materializer_id=bridge_module.PILOT_FFS21_MATERIALIZER_ID,
        materializer_version=bridge_module.PILOT_FFS21_MATERIALIZER_VERSION,
        eligibility_evaluated_by=bridge_module.PILOT_FFS21_PRIMARY_OPERATOR,
        eligibility_evaluated_at=_PR086FJ_FIXED,
        provenance_observed_at=_PR086FJ_FIXED,
        compatibility_policy_id=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_ID
        ),
        compatibility_policy_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_VERSION
        ),
    )
    result = materialize_persisted_traceable_evidence_acceptance(request)
    assert result.status == BRIDGE_STATUS_REJECTED
    assert result.accepted_evidence is None
    assert result.acceptance_record is None
