from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

import rie.application.image_evidence_materializer as module
from rie.application.image_evidence_candidate import (
    CONTRACT_NAME,
    CONTRACT_VERSION,
    ImageEvidenceCandidate,
    ImageEvidenceEligibilityDecision,
    ImageEvidenceEligibilityResult,
    ImageEvidenceRelationship,
    ImageEvidenceRelationshipOrigin,
)
from rie.application.image_evidence_materializer import (
    AcceptedImageEvidenceRelationship,
    ImageEvidenceMaterializationDecision,
    ImageEvidenceMaterializationRequest,
    ImageEvidenceMaterializationResult,
    materialize_image_evidence_candidate,
)
from rie.domain.acceptance_identity import AcceptanceIdentityResult
from rie.domain.acceptance_record import (
    AcceptanceDiagnostic,
    AcceptanceRecord,
)
from rie.domain.accepted_evidence import (
    AcceptedEvidence,
    EvidenceDiagnostic,
    EvidenceLocator,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.evidence_identity import EvidenceIdentityResult


FIXED_TIME = datetime(2026, 7, 31, 4, 0, tzinfo=timezone.utc)
SUBJECT_ID = f"ev1_{'f' * 64}"


def _relationship(
    *,
    origin: ImageEvidenceRelationshipOrigin = (
        ImageEvidenceRelationshipOrigin.SOURCE_BACKED
    ),
    object_evidence_id: str = "SELF_IMAGE_EVIDENCE",
    subject_evidence_id: str = SUBJECT_ID,
    authority_reference: str = "authority-record-001",
    operator_reference: str = "",
    declaration_basis: str = "",
) -> ImageEvidenceRelationship:
    return ImageEvidenceRelationship(
        relationship_type="SUPPORTS",
        origin=origin,
        subject_evidence_id=subject_evidence_id,
        object_evidence_id=object_evidence_id,
        provenance_reference="relationship-provenance-001",
        authority_reference=authority_reference,
        operator_reference=operator_reference,
        declaration_basis=declaration_basis,
    )


def _candidate(
    *,
    relationship: ImageEvidenceRelationship | None = None,
    contract_name: str = CONTRACT_NAME,
    contract_version: str = CONTRACT_VERSION,
    source_checksum: str = "a" * 64,
    artifact_checksum: str = "b" * 64,
    factual_structural_fields: tuple[tuple[str, str], ...] = (
        ("height_px", "1080"),
        ("media_type", "image/png"),
        ("width_px", "1920"),
    ),
) -> ImageEvidenceCandidate:
    return ImageEvidenceCandidate(
        contract_name=contract_name,
        contract_version=contract_version,
        source_id="image-source-001",
        source_revision="rev-001",
        source_checksum=source_checksum,
        artifact_id="image-artifact-001",
        artifact_version="1.0",
        artifact_checksum=artifact_checksum,
        source_authority="RSV_OFFICIAL",
        rights_state="AUTHORIZED",
        lifecycle_state="ACTIVE",
        factual_structural_fields=factual_structural_fields,
        relationship=relationship if relationship is not None else _relationship(),
        eligibility_decision=ImageEvidenceEligibilityDecision.ELIGIBLE,
        eligibility_reasons=("ALL_ELIGIBILITY_PRECONDITIONS_SATISFIED",),
    )


def _locator_value(
    candidate: ImageEvidenceCandidate,
    relationship: ImageEvidenceRelationship,
) -> tuple[str, ...]:
    return (
        "source_revision",
        candidate.source_revision,
        "artifact_id",
        candidate.artifact_id,
        "artifact_version",
        candidate.artifact_version,
        "artifact_checksum",
        candidate.artifact_checksum,
        "relationship_type",
        relationship.relationship_type,
        "relationship_origin",
        relationship.origin.value,
        "relationship_subject",
        relationship.subject_evidence_id,
        "relationship_object",
        "SELF_IMAGE_EVIDENCE",
        "relationship_provenance",
        relationship.provenance_reference,
        "authority_reference",
        relationship.authority_reference or "NONE",
        "operator_reference",
        relationship.operator_reference or "NONE",
        "declaration_basis",
        relationship.declaration_basis or "NONE",
    )


def _lineage(
    candidate: ImageEvidenceCandidate,
    relationship: ImageEvidenceRelationship,
) -> tuple[str, ...]:
    return (
        f"source_revision:{candidate.source_revision}",
        f"rights_state:{candidate.rights_state}",
        f"artifact_id:{candidate.artifact_id}",
        f"artifact_version:{candidate.artifact_version}",
        f"artifact_checksum:{candidate.artifact_checksum}",
        f"relationship_type:{relationship.relationship_type}",
        f"relationship_origin:{relationship.origin.value}",
        f"relationship_subject:{relationship.subject_evidence_id}",
        "relationship_object:SELF_IMAGE_EVIDENCE",
        f"relationship_provenance:{relationship.provenance_reference}",
        f"authority_reference:{relationship.authority_reference}",
        f"operator_reference:{relationship.operator_reference}",
        f"declaration_basis:{relationship.declaration_basis}",
        "mapping_contract:gate_14_image_evidence_acceptance_materialization_and_relationship_identity",
        "mapping_version:1.0",
    )


def _request(
    *,
    candidate: ImageEvidenceCandidate | None = None,
    eligibility_decision: ImageEvidenceEligibilityDecision = (
        ImageEvidenceEligibilityDecision.ELIGIBLE
    ),
    accepted_at: datetime = FIXED_TIME,
    eligibility_evaluated_at: datetime = FIXED_TIME,
) -> ImageEvidenceMaterializationRequest:
    candidate = candidate or _candidate()
    relationship = candidate.relationship
    assert relationship is not None

    eligibility = ImageEvidenceEligibilityResult(
        decision=eligibility_decision,
        candidate=(
            candidate
            if eligibility_decision is ImageEvidenceEligibilityDecision.ELIGIBLE
            else None
        ),
        reasons=(
            candidate.eligibility_reasons
            if eligibility_decision is ImageEvidenceEligibilityDecision.ELIGIBLE
            else ("NOT_ELIGIBLE",)
        ),
    )
    source_snapshot = EvidenceSourceSnapshot(
        source_id=candidate.source_id,
        source_path=(
            f"official-image-source:{candidate.source_id}@"
            f"{candidate.source_revision}"
        ),
        source_type="image",
        document_classification="official_image_source",
        authority_status=candidate.source_authority,
        lifecycle_status=candidate.lifecycle_state,
        evidence_eligibility="eligible",
        source_content_digest=candidate.source_checksum,
    )
    producer_snapshot = EvidenceProducerSnapshot(
        producer_name="gate-14-image-evidence-candidate",
        producer_version=candidate.contract_version,
        producer_kind="image_evidence_candidate",
        producer_contract_version=candidate.contract_name,
    )
    payload = EvidencePayload(
        payload_type="image_structural_facts",
        payload_schema_version="1.0",
        payload=candidate.factual_structural_fields,
        payload_digest="d" * 64,
        locator=EvidenceLocator(
            locator_type="image-evidence-binding",
            locator_value=_locator_value(candidate, relationship),
            locator_schema_version="1.0",
        ),
    )
    provenance = EvidenceProvenance(
        collection_id="image-evidence-collection-001",
        producer_output_digest="e" * 64,
        lineage=_lineage(candidate, relationship),
        observed_at=FIXED_TIME,
        source_registry_version="image-source-registry-v1",
    )
    return ImageEvidenceMaterializationRequest(
        eligibility_result=eligibility,
        accepted_evidence_contract_version="accepted-evidence-v1",
        candidate_snapshot_digest="c" * 64,
        source_snapshot=source_snapshot,
        producer_snapshot=producer_snapshot,
        factual_payload=payload,
        provenance=provenance,
        evidence_diagnostics=(
            EvidenceDiagnostic(
                code="eligible",
                severity="info",
                message="Image Evidence eligibility accepted",
                field="eligibility_result",
                source="gate-14-image-evidence",
            ),
        ),
        eligibility_policy_id="gate-14-image-evidence-eligibility",
        eligibility_policy_version="1.0",
        eligibility_evaluated_at=eligibility_evaluated_at,
        eligibility_evaluated_by="gate-14-eligibility-review",
        accepted_by="operator-001",
        acceptance_reason="Explicit governed Image Evidence acceptance",
        review_record_id="review-001",
        accepted_at=accepted_at,
        acceptance_policy_id="gate-14-image-evidence-acceptance",
        acceptance_policy_version="1.0",
        materializer_id="gate_14_image_evidence_acceptance_materialization_and_relationship_identity",
        materializer_version="1.0",
        acceptance_diagnostics=(
            AcceptanceDiagnostic(
                code="accepted",
                severity="info",
                message="Explicit acceptance recorded",
                field="acceptance_policy_id",
                source="gate-14-image-evidence",
            ),
        ),
        automatic_knowledge_promotion_attempted=False,
        automatic_conflict_resolution_attempted=False,
        side_effect_attempted=False,
        image_access_attempted=False,
        semantic_execution_attempted=False,
        real_asset_execution_attempted=False,
    )


def _unchecked_request(
    request: ImageEvidenceMaterializationRequest,
    **changes: object,
) -> ImageEvidenceMaterializationRequest:
    value = object.__new__(ImageEvidenceMaterializationRequest)
    for field_name in request.__dataclass_fields__:
        object.__setattr__(
            value,
            field_name,
            changes.get(field_name, getattr(request, field_name)),
        )
    return value


def test_materialized_happy_path() -> None:
    result = materialize_image_evidence_candidate(_request())
    assert result.decision is ImageEvidenceMaterializationDecision.MATERIALIZED
    assert result.reason_codes == ()


def test_identical_inputs_produce_identical_result() -> None:
    request = _request()
    assert materialize_image_evidence_candidate(
        request
    ) == materialize_image_evidence_candidate(request)


def test_outputs_use_exact_existing_contracts_and_identity_prefixes() -> None:
    result = materialize_image_evidence_candidate(_request())
    assert type(result.accepted_evidence) is AcceptedEvidence
    assert type(result.acceptance_record) is AcceptanceRecord
    assert type(result.accepted_relationship) is AcceptedImageEvidenceRelationship
    assert result.accepted_evidence.evidence_id.startswith("ev1_")
    assert result.acceptance_record.acceptance_record_id.startswith("ar1_")

    prebound_relationship = _relationship(
        object_evidence_id=result.accepted_evidence.evidence_id
    )
    prebound_result = materialize_image_evidence_candidate(
        _request(candidate=_candidate(relationship=prebound_relationship))
    )
    assert (
        prebound_result.decision
        is ImageEvidenceMaterializationDecision.MATERIALIZED
    )


def test_self_object_binding_resolves_and_subject_is_preserved() -> None:
    result = materialize_image_evidence_candidate(_request())
    assert result.accepted_relationship is not None
    assert result.accepted_evidence is not None
    assert result.acceptance_record is not None
    assert result.accepted_relationship.subject_evidence_id == SUBJECT_ID
    assert (
        result.accepted_relationship.object_evidence_id
        == result.accepted_evidence.evidence_id
        == result.acceptance_record.evidence_id
    )


def test_source_backed_relationship_provenance_is_preserved() -> None:
    result = materialize_image_evidence_candidate(_request())
    relationship = result.accepted_relationship
    assert relationship is not None
    assert relationship.origin is ImageEvidenceRelationshipOrigin.SOURCE_BACKED
    assert relationship.authority_reference == "authority-record-001"
    assert relationship.provenance_reference == "relationship-provenance-001"


def test_operator_declared_relationship_materializes() -> None:
    relationship = _relationship(
        origin=ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED,
        authority_reference="",
        operator_reference="operator-001",
        declaration_basis="manual governed review",
    )
    result = materialize_image_evidence_candidate(
        _request(candidate=_candidate(relationship=relationship))
    )
    assert result.decision is ImageEvidenceMaterializationDecision.MATERIALIZED
    assert result.accepted_relationship.operator_reference == "operator-001"


def test_result_contract_is_frozen() -> None:
    result = materialize_image_evidence_candidate(_request())
    with pytest.raises(FrozenInstanceError):
        result.reason_codes = ("changed",)


def test_request_contract_is_frozen() -> None:
    request = _request()
    with pytest.raises(FrozenInstanceError):
        request.accepted_by = "changed"


def test_accepted_relationship_contract_is_frozen() -> None:
    relationship = materialize_image_evidence_candidate(
        _request()
    ).accepted_relationship
    assert relationship is not None
    with pytest.raises(FrozenInstanceError):
        relationship.object_evidence_id = SUBJECT_ID


def test_non_request_input_is_rejected_without_outputs() -> None:
    result = materialize_image_evidence_candidate(object())
    assert result.decision is ImageEvidenceMaterializationDecision.REJECTED
    assert result.reason_codes == ("REQUEST_INVALID",)
    assert result.accepted_evidence is None
    assert result.acceptance_record is None
    assert result.accepted_relationship is None


def test_non_eligible_result_is_rejected() -> None:
    request = _request(
        eligibility_decision=ImageEvidenceEligibilityDecision.INELIGIBLE
    )
    result = materialize_image_evidence_candidate(request)
    assert result.reason_codes == ("ELIGIBILITY_NOT_ELIGIBLE",)


def test_missing_candidate_is_rejected() -> None:
    request = _request()
    eligibility = ImageEvidenceEligibilityResult(
        decision=ImageEvidenceEligibilityDecision.ELIGIBLE,
        candidate=None,
        reasons=request.eligibility_result.reasons,
    )
    result = materialize_image_evidence_candidate(
        _unchecked_request(request, eligibility_result=eligibility)
    )
    assert result.reason_codes == ("CANDIDATE_MISSING_OR_INVALID",)


def test_unsupported_candidate_contract_is_rejected() -> None:
    request = _request(candidate=_candidate(contract_version="2.0"))
    result = materialize_image_evidence_candidate(request)
    assert result.reason_codes == (
        "CANDIDATE_CONTRACT_OR_ELIGIBILITY_MISMATCH",
    )


def test_incomplete_candidate_identity_is_rejected() -> None:
    request = _request(candidate=_candidate(source_checksum="not-a-checksum"))
    result = materialize_image_evidence_candidate(request)
    assert result.reason_codes == ("CANDIDATE_IDENTITY_INCOMPLETE",)


def test_unsorted_factual_fields_are_rejected() -> None:
    request = _request()
    candidate = replace(
        request.eligibility_result.candidate,
        factual_structural_fields=(
            ("width_px", "1920"),
            ("height_px", "1080"),
        ),
    )
    eligibility = replace(request.eligibility_result, candidate=candidate)
    result = materialize_image_evidence_candidate(
        _unchecked_request(request, eligibility_result=eligibility)
    )
    assert result.reason_codes == ("FACTUAL_STRUCTURAL_FIELDS_INVALID",)


def test_relationship_is_required() -> None:
    request = _request()
    candidate = replace(request.eligibility_result.candidate, relationship=None)
    eligibility = replace(request.eligibility_result, candidate=candidate)
    result = materialize_image_evidence_candidate(
        _unchecked_request(request, eligibility_result=eligibility)
    )
    assert result.reason_codes == ("RELATIONSHIP_REQUIRED",)


def test_invalid_relationship_subject_is_rejected() -> None:
    relationship = _relationship(subject_evidence_id="text-evidence-001")
    result = materialize_image_evidence_candidate(
        _request(candidate=_candidate(relationship=relationship))
    )
    assert result.reason_codes == ("RELATIONSHIP_INVALID",)

    real_relationship = replace(_relationship(), synthetic=False)
    real_result = materialize_image_evidence_candidate(
        _request(candidate=_candidate(relationship=real_relationship))
    )
    assert real_result.reason_codes == (
        "REAL_ASSET_RELATIONSHIP_PROHIBITED",
    )


def test_mismatched_supplied_object_identity_safe_stops() -> None:
    relationship = _relationship(object_evidence_id=f"ev1_{'1' * 64}")
    request = _request(candidate=_candidate(relationship=relationship))
    result = materialize_image_evidence_candidate(request)
    assert result.reason_codes == ("RELATIONSHIP_OBJECT_IDENTITY_MISMATCH",)


def test_source_backed_relationship_requires_authority_reference() -> None:
    relationship = _relationship(authority_reference="")
    result = materialize_image_evidence_candidate(
        _request(candidate=_candidate(relationship=relationship))
    )
    assert result.reason_codes == (
        "SOURCE_BACKED_AUTHORITY_REFERENCE_MISSING",
    )


def test_operator_relationship_requires_declaration_metadata() -> None:
    relationship = _relationship(
        origin=ImageEvidenceRelationshipOrigin.OPERATOR_DECLARED,
        authority_reference="",
    )
    result = materialize_image_evidence_candidate(
        _request(candidate=_candidate(relationship=relationship))
    )
    assert result.reason_codes == ("OPERATOR_DECLARATION_INCOMPLETE",)


def test_naive_acceptance_time_is_rejected() -> None:
    acceptance_result = materialize_image_evidence_candidate(
        _request(accepted_at=datetime(2026, 7, 31, 4, 0))
    )
    eligibility_result = materialize_image_evidence_candidate(
        _request(
            eligibility_evaluated_at=datetime(2026, 7, 31, 4, 0)
        )
    )
    assert acceptance_result.reason_codes == (
        "TIMEZONE_AWARE_TIMESTAMP_REQUIRED",
    )
    assert eligibility_result.reason_codes == (
        "TIMEZONE_AWARE_TIMESTAMP_REQUIRED",
    )


def test_unsupported_policy_or_materializer_is_rejected() -> None:
    request = _request()
    fields = (
        ("eligibility_policy_id", "other-policy"),
        ("acceptance_policy_version", "2.0"),
        ("materializer_id", "other-materializer"),
    )
    for field_name, value in fields:
        result = materialize_image_evidence_candidate(
            _unchecked_request(request, **{field_name: value})
        )
        assert result.reason_codes == (
            "UNSUPPORTED_POLICY_OR_MATERIALIZER",
        )


def test_source_snapshot_mismatch_is_rejected() -> None:
    request = _request()
    source = replace(request.source_snapshot, source_path="other")
    result = materialize_image_evidence_candidate(
        _unchecked_request(request, source_snapshot=source)
    )
    assert result.reason_codes == ("SOURCE_SNAPSHOT_MISMATCH",)


def test_factual_payload_mismatch_is_rejected() -> None:
    request = _request()
    payload = replace(request.factual_payload, payload_type="semantic_summary")
    result = materialize_image_evidence_candidate(
        _unchecked_request(request, factual_payload=payload)
    )
    assert result.reason_codes == ("FACTUAL_PAYLOAD_MISMATCH",)


def test_provenance_lineage_mismatch_is_rejected() -> None:
    request = _request()
    provenance = replace(
        request.provenance,
        lineage=request.provenance.lineage[:-1],
    )
    result = materialize_image_evidence_candidate(
        _unchecked_request(request, provenance=provenance)
    )
    assert result.reason_codes == ("PROVENANCE_LINEAGE_MISMATCH",)


def test_all_prohibited_attempt_flags_safe_stop() -> None:
    request = _request()
    flag_names = (
        "automatic_knowledge_promotion_attempted",
        "automatic_conflict_resolution_attempted",
        "side_effect_attempted",
        "image_access_attempted",
        "semantic_execution_attempted",
        "real_asset_execution_attempted",
    )
    for flag_name in flag_names:
        result = materialize_image_evidence_candidate(
            _unchecked_request(request, **{flag_name: True})
        )
        assert result.reason_codes == ("PROHIBITED_OPERATION_ATTEMPTED",)
        assert result.accepted_evidence is None


def test_evidence_identity_recomputation_mismatch_safe_stops(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = module.calculate_evidence_identity
    call_count = 0

    def changing_identity(identity_input: object) -> EvidenceIdentityResult:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return original(identity_input)
        return EvidenceIdentityResult(
            evidence_id=f"ev1_{'1' * 64}",
            digest_algorithm="sha256",
            digest_hex="1" * 64,
            identity_policy_id="rcis-evidence-identity",
            identity_policy_version="1.0.0",
            canonicalization_contract_version="identity-json-v1",
            canonical_byte_length=1,
        )

    monkeypatch.setattr(module, "calculate_evidence_identity", changing_identity)
    result = materialize_image_evidence_candidate(_request())
    assert result.reason_codes == ("EVIDENCE_IDENTITY_RECOMPUTATION_MISMATCH",)


def test_acceptance_identity_recomputation_mismatch_safe_stops(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = module.calculate_acceptance_identity
    call_count = 0

    def changing_identity(identity_input: object) -> AcceptanceIdentityResult:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return original(identity_input)
        return AcceptanceIdentityResult(
            acceptance_record_id=f"ar1_{'2' * 64}",
            digest_algorithm="sha256",
            digest_hex="2" * 64,
            identity_policy_id="rcis-acceptance-record-identity",
            identity_policy_version="1.0.0",
            canonicalization_contract_version="acceptance-json-v1",
            canonical_byte_length=1,
        )

    monkeypatch.setattr(module, "calculate_acceptance_identity", changing_identity)
    result = materialize_image_evidence_candidate(_request())
    assert result.reason_codes == (
        "ACCEPTANCE_IDENTITY_RECOMPUTATION_MISMATCH",
    )
