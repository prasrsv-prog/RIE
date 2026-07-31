from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

import rie.application.image_knowledge_constructor as module
from rie.application.image_evidence_candidate import (
    ImageEvidenceRelationshipOrigin,
)
from rie.application.image_evidence_materializer import (
    AcceptedImageEvidenceRelationship,
    ImageEvidenceMaterializationDecision,
    ImageEvidenceMaterializationResult,
)
from rie.application.image_knowledge_constructor import (
    ImageKnowledgeConstructionDecision,
    ImageKnowledgeConstructionRequest,
    ImageKnowledgeConstructionResult,
    ImageKnowledgeRelationshipSupport,
    construct_image_knowledge_candidate,
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
from rie.domain.knowledge_candidate import (
    IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE,
    INITIAL_AUTHORITY_STATUS,
    INITIAL_CONFLICT_STATUS,
    INITIAL_LIFECYCLE_STATUS,
    INITIAL_REVIEW_STATUS,
    KnowledgeCandidate,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)

EV_ID = "ev1_" + "1" * 64
SUBJECT_EV_ID = "ev1_" + "2" * 64
AR_ID = "ar1_" + "3" * 64
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _accepted_evidence(
    *,
    payload_type: str = "image_structural_facts",
    payload_schema_version: str = "1.0",
    payload: object = (
        ("height", "200"),
        ("width", "100"),
    ),
    evidence_id: str = EV_ID,
) -> AcceptedEvidence:
    payload_digest = "4" * 64
    candidate_digest = "5" * 64
    source_id = "source-1"
    return AcceptedEvidence(
        evidence_id=evidence_id,
        contract_version="accepted-evidence-v1",
        candidate_reference=EvidenceCandidateReference(
            candidate_contract_version="1.0",
            candidate_snapshot_digest=candidate_digest,
            candidate_source_id=source_id,
            candidate_producer_name="gate-14-image-evidence-candidate",
            candidate_producer_version="1.0",
            candidate_payload_digest=payload_digest,
        ),
        source_snapshot=EvidenceSourceSnapshot(
            source_id=source_id,
            source_path="official-image-source:source-1@revision-1",
            source_type="image",
            document_classification="official_image_source",
            authority_status="official",
            lifecycle_status="active",
            evidence_eligibility="eligible",
            source_content_digest="6" * 64,
        ),
        producer_snapshot=EvidenceProducerSnapshot(
            producer_name="gate-14-image-evidence-candidate",
            producer_version="1.0",
            producer_kind="image_evidence_candidate",
            producer_contract_version=(
                "gate_14_explicit_image_evidence_eligibility_"
                "and_provenance_relationship"
            ),
        ),
        factual_payload=EvidencePayload(
            payload_type=payload_type,
            payload_schema_version=payload_schema_version,
            payload=payload,
            payload_digest=payload_digest,
            locator=EvidenceLocator(
                locator_type="image-evidence-binding",
                locator_value=("artifact", "artifact-1"),
                locator_schema_version="1.0",
            ),
        ),
        provenance=EvidenceProvenance(
            collection_id="collection-1",
            producer_output_digest="7" * 64,
            lineage=("artifact:artifact-1", "source:source-1"),
            observed_at=NOW,
            source_registry_version="1.0",
        ),
        eligibility_result=AcceptedEligibilityResult(
            decision="eligible",
            policy_id="gate-14-image-evidence-eligibility",
            policy_version="1.0",
            candidate_snapshot_digest=candidate_digest,
            source_id=source_id,
            reason_codes=("ALL_ELIGIBILITY_PRECONDITIONS_SATISFIED",),
            evaluated_at=NOW,
            evaluated_by="reviewer-1",
            diagnostics=(),
        ),
        materialization_record=EvidenceMaterializationRecord(
            materializer_id=(
                "gate_14_image_evidence_acceptance_"
                "materialization_and_relationship_identity"
            ),
            materializer_version="1.0",
            materialized_at=NOW,
            acceptance_record_id=AR_ID,
            accepted_by="reviewer-1",
            acceptance_reason="accepted",
            review_record_id="review-1",
            identity_policy_id="rcis-evidence-identity",
            identity_policy_version="1.0.0",
        ),
        diagnostics=(),
    )


def _acceptance_record(*, evidence_id: str = EV_ID) -> AcceptanceRecord:
    return AcceptanceRecord(
        acceptance_record_id=AR_ID,
        contract_version="acceptance-record-v1",
        evidence_id=evidence_id,
        accepted_by="reviewer-1",
        acceptance_reason="accepted",
        review_record_id="review-1",
        accepted_at=NOW,
        acceptance_policy_id="gate-14-image-evidence-acceptance",
        acceptance_policy_version="1.0",
        evidence_identity_policy_id="rcis-evidence-identity",
        evidence_identity_policy_version="1.0.0",
        materializer_id=(
            "gate_14_image_evidence_acceptance_"
            "materialization_and_relationship_identity"
        ),
        materializer_version="1.0",
        diagnostics=(),
    )


def _relationship(
    *,
    origin: ImageEvidenceRelationshipOrigin = (
        ImageEvidenceRelationshipOrigin.SOURCE_BACKED
    ),
    object_evidence_id: str = EV_ID,
) -> AcceptedImageEvidenceRelationship:
    return AcceptedImageEvidenceRelationship(
        relationship_type="derived_from",
        origin=origin,
        subject_evidence_id=SUBJECT_EV_ID,
        object_evidence_id=object_evidence_id,
        provenance_reference="relationship-provenance-1",
        authority_reference=(
            "authority-1"
            if origin is ImageEvidenceRelationshipOrigin.SOURCE_BACKED
            else ""
        ),
        operator_reference=(
            "operator-1"
            if origin is ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED
            else ""
        ),
        declaration_basis=(
            "declared"
            if origin is ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED
            else ""
        ),
    )


def _materialization_result(
    *,
    accepted_evidence: AcceptedEvidence | None = None,
    acceptance_record: AcceptanceRecord | None = None,
    accepted_relationship: AcceptedImageEvidenceRelationship | None = None,
) -> ImageEvidenceMaterializationResult:
    return ImageEvidenceMaterializationResult(
        decision=ImageEvidenceMaterializationDecision.MATERIALIZED,
        accepted_evidence=accepted_evidence or _accepted_evidence(),
        acceptance_record=acceptance_record or _acceptance_record(),
        accepted_relationship=accepted_relationship or _relationship(),
        reason_codes=(),
        diagnostics=(),
    )


def _request(**changes: object) -> ImageKnowledgeConstructionRequest:
    values = {
        "materialization_result": _materialization_result(),
        "factual_field_name": "width",
        "statement": "100",
        "construction_rule_id": (
            "rcis-accepted-image-structural-fact-selection"
        ),
        "construction_rule_version": "1.0.0",
        "constructor_id": (
            "gate-14-image-evidence-to-knowledge-candidate-constructor"
        ),
        "constructor_version": "1.0",
        "constructed_at": NOW,
        "automatic_promotion_attempted": False,
        "automatic_conflict_resolution_attempted": False,
        "knowledge_approval_attempted": False,
        "persistence_attempted": False,
        "side_effect_attempted": False,
        "image_access_attempted": False,
        "semantic_execution_attempted": False,
        "real_asset_execution_attempted": False,
    }
    values.update(changes)
    return ImageKnowledgeConstructionRequest(**values)


def test_constructed_happy_path() -> None:
    result = construct_image_knowledge_candidate(_request())
    assert result.decision is ImageKnowledgeConstructionDecision.CONSTRUCTED
    assert type(result.knowledge_candidate) is KnowledgeCandidate
    assert type(result.relationship_support) is ImageKnowledgeRelationshipSupport
    assert result.reason_codes == ()


def test_identical_inputs_produce_identical_outputs() -> None:
    assert construct_image_knowledge_candidate(_request()) == (
        construct_image_knowledge_candidate(_request())
    )


def test_constructed_candidate_uses_exact_statement_contract() -> None:
    candidate = construct_image_knowledge_candidate(_request()).knowledge_candidate
    assert candidate is not None
    assert candidate.statement_type == IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE
    assert candidate.statement == "100"
    assert candidate.construction_rule_id == (
        "rcis-accepted-image-structural-fact-selection"
    )
    assert candidate.construction_rule_version == "1.0.0"


def test_constructed_candidate_uses_initial_governance_states() -> None:
    candidate = construct_image_knowledge_candidate(_request()).knowledge_candidate
    assert candidate is not None
    assert candidate.authority_status == INITIAL_AUTHORITY_STATUS
    assert candidate.lifecycle_status == INITIAL_LIFECYCLE_STATUS
    assert candidate.review_status == INITIAL_REVIEW_STATUS
    assert candidate.conflict_status == INITIAL_CONFLICT_STATUS
    assert candidate.conflict_ids == ()
    assert candidate.diagnostics == ()


def test_constructed_candidate_recomputes_existing_kc1_identity() -> None:
    candidate = construct_image_knowledge_candidate(_request()).knowledge_candidate
    assert candidate is not None
    assert candidate.knowledge_candidate_id == compute_knowledge_candidate_id(
        identity_input_from_knowledge_candidate(candidate)
    )


def test_relationship_support_preserves_ev1_ar1_and_kc1() -> None:
    result = construct_image_knowledge_candidate(_request())
    candidate = result.knowledge_candidate
    support = result.relationship_support
    assert candidate is not None and support is not None
    assert support.knowledge_candidate_id == candidate.knowledge_candidate_id
    assert support.evidence_id == EV_ID
    assert support.acceptance_record_id == AR_ID


def test_source_backed_relationship_metadata_is_preserved() -> None:
    support = construct_image_knowledge_candidate(
        _request()
    ).relationship_support
    assert support is not None
    assert support.relationship_origin is ImageEvidenceRelationshipOrigin.SOURCE_BACKED
    assert support.authority_reference == "authority-1"
    assert support.operator_reference == ""
    assert support.declaration_basis == ""


def test_operator_declared_relationship_metadata_is_preserved() -> None:
    relation = _relationship(
        origin=ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED
    )
    materialization = _materialization_result(
        accepted_relationship=relation
    )
    support = construct_image_knowledge_candidate(
        _request(materialization_result=materialization)
    ).relationship_support
    assert support is not None
    assert support.relationship_origin is (
        ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED
    )
    assert support.operator_reference == "operator-1"
    assert support.declaration_basis == "declared"


def test_source_and_materialization_lineage_is_preserved() -> None:
    support = construct_image_knowledge_candidate(
        _request()
    ).relationship_support
    assert support is not None
    assert support.source_id == "source-1"
    assert support.source_content_digest == "6" * 64
    assert support.payload_digest == "4" * 64
    assert support.source_lineage == (
        "artifact:artifact-1",
        "source:source-1",
    )
    assert support.evidence_materializer_version == "1.0"


def test_request_result_and_support_are_frozen() -> None:
    result = construct_image_knowledge_candidate(_request())
    support = result.relationship_support
    assert support is not None
    for instance, field_name in (
        (_request(), "statement"),
        (result, "decision"),
        (support, "evidence_id"),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(instance, field_name, "changed")


def test_non_request_input_is_rejected_without_output() -> None:
    result = construct_image_knowledge_candidate(object())
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED
    assert result.knowledge_candidate is None
    assert result.relationship_support is None


def test_non_materialized_result_is_rejected_without_output() -> None:
    materialization = ImageEvidenceMaterializationResult(
        decision=ImageEvidenceMaterializationDecision.REJECTED,
        accepted_evidence=None,
        acceptance_record=None,
        accepted_relationship=None,
        reason_codes=("REJECTED",),
        diagnostics=("REJECTED",),
    )
    result = construct_image_knowledge_candidate(
        _request(materialization_result=materialization)
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED
    assert result.knowledge_candidate is None


def test_materialized_result_with_reasons_safe_boundary_rejects() -> None:
    unsafe = object.__new__(ImageEvidenceMaterializationResult)
    valid = _materialization_result()
    for field_name in (
        "decision",
        "accepted_evidence",
        "acceptance_record",
        "accepted_relationship",
        "diagnostics",
    ):
        object.__setattr__(unsafe, field_name, getattr(valid, field_name))
    object.__setattr__(unsafe, "reason_codes", ("unexpected",))
    result = construct_image_knowledge_candidate(
        _request(materialization_result=unsafe)
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED
    assert result.knowledge_candidate is None


def test_mismatched_evidence_and_acceptance_identity_safe_stops() -> None:
    evidence = _accepted_evidence(evidence_id=SUBJECT_EV_ID)
    materialization = _materialization_result(accepted_evidence=evidence)
    result = construct_image_knowledge_candidate(
        _request(materialization_result=materialization)
    )
    assert result.decision is ImageKnowledgeConstructionDecision.SAFE_STOP
    assert result.reason_codes == ("MATERIALIZED_IDENTITY_LINK_MISMATCH",)


def test_mismatched_relationship_object_identity_safe_stops() -> None:
    materialization = _materialization_result(
        accepted_relationship=_relationship(
            object_evidence_id=SUBJECT_EV_ID
        )
    )
    result = construct_image_knowledge_candidate(
        _request(materialization_result=materialization)
    )
    assert result.decision is ImageKnowledgeConstructionDecision.SAFE_STOP


def test_unsupported_payload_type_is_rejected() -> None:
    evidence = _accepted_evidence(payload_type="text")
    result = construct_image_knowledge_candidate(
        _request(
            materialization_result=_materialization_result(
                accepted_evidence=evidence
            )
        )
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED


def test_unsupported_payload_schema_is_rejected() -> None:
    evidence = _accepted_evidence(payload_schema_version="2.0")
    result = construct_image_knowledge_candidate(
        _request(
            materialization_result=_materialization_result(
                accepted_evidence=evidence
            )
        )
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED


def test_missing_factual_field_is_rejected() -> None:
    result = construct_image_knowledge_candidate(
        _request(factual_field_name="missing")
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED
    assert result.reason_codes == ("FACTUAL_FIELD_NOT_FOUND",)


def test_statement_must_equal_selected_field_byte_for_byte() -> None:
    result = construct_image_knowledge_candidate(
        _request(statement="100 ")
    )
    assert result.decision is ImageKnowledgeConstructionDecision.SAFE_STOP
    assert result.reason_codes == ("STATEMENT_SELECTION_MISMATCH",)


def test_blank_explicit_input_is_rejected() -> None:
    result = construct_image_knowledge_candidate(
        _request(factual_field_name=" ")
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED


def test_naive_construction_time_is_rejected() -> None:
    result = construct_image_knowledge_candidate(
        _request(constructed_at=datetime(2026, 1, 1))
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED


def test_unsupported_rule_id_is_rejected() -> None:
    result = construct_image_knowledge_candidate(
        _request(construction_rule_id="other")
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED


def test_unsupported_rule_version_is_rejected() -> None:
    result = construct_image_knowledge_candidate(
        _request(construction_rule_version="2.0.0")
    )
    assert result.decision is ImageKnowledgeConstructionDecision.REJECTED


def test_unsupported_constructor_id_or_version_is_rejected() -> None:
    wrong_id = construct_image_knowledge_candidate(
        _request(constructor_id="other")
    )
    wrong_version = construct_image_knowledge_candidate(
        _request(constructor_version="2.0")
    )
    assert wrong_id.decision is ImageKnowledgeConstructionDecision.REJECTED
    assert wrong_version.decision is ImageKnowledgeConstructionDecision.REJECTED


def test_non_boolean_prohibited_flag_safe_stops() -> None:
    result = construct_image_knowledge_candidate(
        _request(automatic_promotion_attempted="False")
    )
    assert result.decision is ImageKnowledgeConstructionDecision.SAFE_STOP
    assert result.reason_codes == ("PROHIBITED_ATTEMPT_FLAG_INVALID",)


def test_automatic_promotion_attempt_safe_stops() -> None:
    result = construct_image_knowledge_candidate(
        _request(automatic_promotion_attempted=True)
    )
    assert result.decision is ImageKnowledgeConstructionDecision.SAFE_STOP


def test_automatic_conflict_resolution_attempt_safe_stops() -> None:
    result = construct_image_knowledge_candidate(
        _request(automatic_conflict_resolution_attempted=True)
    )
    assert result.decision is ImageKnowledgeConstructionDecision.SAFE_STOP


def test_approval_or_persistence_attempt_safe_stops() -> None:
    approval = construct_image_knowledge_candidate(
        _request(knowledge_approval_attempted=True)
    )
    persistence = construct_image_knowledge_candidate(
        _request(persistence_attempted=True)
    )
    assert approval.decision is ImageKnowledgeConstructionDecision.SAFE_STOP
    assert persistence.decision is ImageKnowledgeConstructionDecision.SAFE_STOP


def test_side_effect_image_semantic_or_real_asset_attempt_safe_stops() -> None:
    for field_name in (
        "side_effect_attempted",
        "image_access_attempted",
        "semantic_execution_attempted",
        "real_asset_execution_attempted",
    ):
        result = construct_image_knowledge_candidate(
            _request(**{field_name: True})
        )
        assert result.decision is ImageKnowledgeConstructionDecision.SAFE_STOP


def test_identity_construction_mismatch_safe_stops_without_partial_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        module,
        "compute_knowledge_candidate_id",
        lambda _identity_input: "kc1_" + "f" * 64,
    )
    result = construct_image_knowledge_candidate(_request())
    assert result.decision is ImageKnowledgeConstructionDecision.SAFE_STOP
    assert result.knowledge_candidate is None
    assert result.relationship_support is None
    assert result.reason_codes == ("DOMAIN_CONSTRUCTION_SAFE_STOP",)
