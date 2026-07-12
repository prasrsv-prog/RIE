from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import datetime, timezone

import pytest

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


FIXED_TIME = datetime(2026, 7, 12, 9, 0, tzinfo=timezone.utc)


def _diagnostic() -> EvidenceDiagnostic:
    return EvidenceDiagnostic(
        code="accepted",
        severity="info",
        message="Accepted by explicit policy",
        field="eligibility_result",
        source="policy",
    )


def _accepted_evidence() -> AcceptedEvidence:
    candidate_reference = EvidenceCandidateReference(
        candidate_contract_version="candidate-v1",
        candidate_snapshot_digest="candidate-digest",
        candidate_source_id="source-1",
        candidate_producer_name="structural-inspector",
        candidate_producer_version="1.0.0",
        candidate_payload_digest="payload-digest",
    )
    source_snapshot = EvidenceSourceSnapshot(
        source_id="source-1",
        source_path="official/source.pdf",
        source_type="pdf",
        document_classification="official_product_specification",
        authority_status="official",
        lifecycle_status="active",
        evidence_eligibility="eligible",
        source_content_digest="source-digest",
    )
    producer_snapshot = EvidenceProducerSnapshot(
        producer_name="structural-inspector",
        producer_version="1.0.0",
        producer_kind="inspector",
        producer_contract_version="result-v1",
    )
    locator = EvidenceLocator(
        locator_type="page",
        locator_value=("page_index", 0),
        locator_schema_version="locator-v1",
    )
    factual_payload = EvidencePayload(
        payload_type="document_structural_metadata",
        payload_schema_version="payload-v1",
        payload=(("page_count", 1), ("title", "SV300")),
        payload_digest="payload-digest",
        locator=locator,
    )
    provenance = EvidenceProvenance(
        collection_id="collection-1",
        producer_output_digest="producer-output-digest",
        lineage=("admission-1", "inspection-1"),
        observed_at=FIXED_TIME,
        source_registry_version="registry-v1",
    )
    eligibility_result = AcceptedEligibilityResult(
        decision="eligible",
        policy_id="official-source-policy",
        policy_version="1.0.0",
        candidate_snapshot_digest="candidate-digest",
        source_id="source-1",
        reason_codes=("official_source_eligible",),
        evaluated_at=FIXED_TIME,
        evaluated_by="eligibility-service",
        diagnostics=(_diagnostic(),),
    )
    materialization_record = EvidenceMaterializationRecord(
        materializer_id="accepted-evidence-materializer",
        materializer_version="1.0.0",
        materialized_at=FIXED_TIME,
        acceptance_record_id="acceptance-record-1",
        accepted_by="review-service",
        acceptance_reason="All explicit prerequisites satisfied",
        review_record_id="review-1",
        identity_policy_id="accepted-evidence-identity",
        identity_policy_version="1.0.0",
    )
    return AcceptedEvidence(
        evidence_id="ev1_fixture",
        contract_version="accepted-evidence-v1",
        candidate_reference=candidate_reference,
        source_snapshot=source_snapshot,
        producer_snapshot=producer_snapshot,
        factual_payload=factual_payload,
        provenance=provenance,
        eligibility_result=eligibility_result,
        materialization_record=materialization_record,
        diagnostics=(_diagnostic(),),
    )


@pytest.mark.parametrize(
    ("instance", "field_name"),
    (
        (_diagnostic(), "code"),
        (
            EvidenceCandidateReference(
                "candidate-v1",
                "candidate-digest",
                "source-1",
                "producer",
                "1.0.0",
                "payload-digest",
            ),
            "candidate_contract_version",
        ),
        (
            EvidenceSourceSnapshot(
                "source-1",
                "source.pdf",
                "pdf",
                "official",
                "official",
                "active",
                "eligible",
                "source-digest",
            ),
            "source_id",
        ),
        (
            EvidenceProducerSnapshot(
                "producer",
                "1.0.0",
                "inspector",
                "result-v1",
            ),
            "producer_name",
        ),
        (
            EvidenceLocator(
                "page",
                ("page_index", 0),
                "locator-v1",
            ),
            "locator_type",
        ),
        (
            EvidencePayload(
                "metadata",
                "payload-v1",
                ("value",),
                "payload-digest",
                EvidenceLocator(
                    "page",
                    ("page_index", 0),
                    "locator-v1",
                ),
            ),
            "payload_type",
        ),
        (
            EvidenceProvenance(
                "collection-1",
                "producer-digest",
                ("lineage-1",),
                FIXED_TIME,
                "registry-v1",
            ),
            "collection_id",
        ),
        (
            AcceptedEligibilityResult(
                "eligible",
                "policy",
                "1.0.0",
                "candidate-digest",
                "source-1",
                ("accepted",),
                FIXED_TIME,
                "reviewer",
                (),
            ),
            "decision",
        ),
        (
            EvidenceMaterializationRecord(
                "materializer",
                "1.0.0",
                FIXED_TIME,
                "acceptance-1",
                "reviewer",
                "accepted",
                "review-1",
                "identity-policy",
                "1.0.0",
            ),
            "materializer_id",
        ),
        (_accepted_evidence(), "evidence_id"),
    ),
)
def test_all_contracts_are_frozen(instance: object, field_name: str) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(instance, field_name, "changed")


def test_valid_contract_preserves_all_explicit_values() -> None:
    evidence = _accepted_evidence()

    assert evidence.evidence_id == "ev1_fixture"
    assert evidence.contract_version == "accepted-evidence-v1"
    assert evidence.candidate_reference.candidate_contract_version == "candidate-v1"
    assert evidence.source_snapshot.source_content_digest == "source-digest"
    assert evidence.producer_snapshot.producer_contract_version == "result-v1"
    assert evidence.factual_payload.payload_schema_version == "payload-v1"
    assert evidence.provenance.source_registry_version == "registry-v1"
    assert evidence.eligibility_result.policy_version == "1.0.0"
    assert evidence.materialization_record.identity_policy_version == "1.0.0"


def test_contract_equality_is_value_based() -> None:
    assert _accepted_evidence() == _accepted_evidence()


@pytest.mark.parametrize(
    "contract_type",
    (
        EvidenceDiagnostic,
        EvidenceCandidateReference,
        EvidenceSourceSnapshot,
        EvidenceProducerSnapshot,
        EvidenceLocator,
        EvidencePayload,
        EvidenceProvenance,
        AcceptedEligibilityResult,
        EvidenceMaterializationRecord,
        AcceptedEvidence,
    ),
)
def test_all_contract_fields_are_required(contract_type: type[object]) -> None:
    assert all(
        field.default is MISSING
        and field.default_factory is MISSING
        for field in fields(contract_type)
    )


def test_omitted_required_top_level_field_uses_constructor_semantics() -> None:
    values = _accepted_evidence().__dict__.copy()
    values.pop("evidence_id")

    with pytest.raises(TypeError):
        AcceptedEvidence(**values)


@pytest.mark.parametrize("severity", ("error", "debug", "", " "))
def test_diagnostic_rejects_unapproved_severity(severity: str) -> None:
    with pytest.raises(ValueError, match="severity"):
        EvidenceDiagnostic(
            code="code",
            severity=severity,
            message="message",
            field="field",
            source="source",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "code",
        "message",
        "field",
        "source",
    ),
)
def test_diagnostic_rejects_whitespace_only_strings(
    field_name: str,
) -> None:
    values = _diagnostic().__dict__.copy()
    values[field_name] = " "

    with pytest.raises(ValueError, match=field_name):
        EvidenceDiagnostic(**values)


def test_eligibility_decision_must_be_eligible() -> None:
    valid = _accepted_evidence().eligibility_result

    with pytest.raises(ValueError, match="decision"):
        replace(valid, decision="rejected")


def test_eligibility_requires_at_least_one_reason_code() -> None:
    valid = _accepted_evidence().eligibility_result

    with pytest.raises(ValueError, match="reason_codes"):
        replace(valid, reason_codes=())


def test_provenance_requires_non_empty_lineage() -> None:
    valid = _accepted_evidence().provenance

    with pytest.raises(ValueError, match="lineage"):
        replace(valid, lineage=())


@pytest.mark.parametrize(
    ("instance", "field_name"),
    (
        (_accepted_evidence().provenance, "observed_at"),
        (_accepted_evidence().eligibility_result, "evaluated_at"),
        (_accepted_evidence().materialization_record, "materialized_at"),
    ),
)
def test_audit_timestamps_must_be_timezone_aware(
    instance: object,
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        replace(
            instance,
            **{field_name: datetime(2026, 7, 12, 9, 0)},
        )


@pytest.mark.parametrize(
    "mutable_payload",
    (
        ["value"],
        {"key": "value"},
        {"value"},
    ),
)
def test_payload_rejects_mutable_values(
    mutable_payload: object,
) -> None:
    valid = _accepted_evidence().factual_payload

    with pytest.raises(ValueError, match="payload"):
        replace(valid, payload=mutable_payload)


def test_payload_rejects_duplicate_mapping_keys() -> None:
    valid = _accepted_evidence().factual_payload

    with pytest.raises(ValueError, match="unique"):
        replace(
            valid,
            payload=(("key", 1), ("key", 2)),
        )


def test_payload_rejects_unsorted_mapping_keys() -> None:
    valid = _accepted_evidence().factual_payload

    with pytest.raises(ValueError, match="ordered"):
        replace(
            valid,
            payload=(("z", 1), ("a", 2)),
        )


@pytest.mark.parametrize("value", (float("nan"), float("inf")))
def test_payload_rejects_non_finite_float(value: float) -> None:
    valid = _accepted_evidence().factual_payload

    with pytest.raises(ValueError, match="finite"):
        replace(valid, payload=value)


@pytest.mark.parametrize(
    "locator_value",
    (
        [],
        {},
        (),
    ),
)
def test_locator_rejects_mutable_or_empty_values(
    locator_value: object,
) -> None:
    valid = _accepted_evidence().factual_payload.locator

    with pytest.raises(ValueError, match="locator_value"):
        replace(valid, locator_value=locator_value)


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    (
        ("diagnostics", []),
        ("eligibility_diagnostics", []),
        ("reason_codes", ["accepted"]),
        ("lineage", ["lineage-1"]),
    ),
)
def test_collection_fields_require_exact_tuples(
    field_name: str,
    bad_value: object,
) -> None:
    evidence = _accepted_evidence()

    if field_name == "diagnostics":
        with pytest.raises(ValueError, match="diagnostics"):
            replace(evidence, diagnostics=bad_value)
    elif field_name == "eligibility_diagnostics":
        with pytest.raises(ValueError, match="diagnostics"):
            replace(
                evidence.eligibility_result,
                diagnostics=bad_value,
            )
    elif field_name == "reason_codes":
        with pytest.raises(ValueError, match="reason_codes"):
            replace(
                evidence.eligibility_result,
                reason_codes=bad_value,
            )
    else:
        with pytest.raises(ValueError, match="lineage"):
            replace(
                evidence.provenance,
                lineage=bad_value,
            )


@pytest.mark.parametrize(
    ("target", "replacement", "message"),
    (
        (
            "candidate_source_id",
            "different-source",
            "candidate_source_id",
        ),
        (
            "candidate_producer_name",
            "different-producer",
            "candidate_producer_name",
        ),
        (
            "candidate_producer_version",
            "2.0.0",
            "candidate_producer_version",
        ),
        (
            "candidate_payload_digest",
            "different-payload",
            "candidate_payload_digest",
        ),
        (
            "eligibility_candidate_digest",
            "different-candidate",
            "candidate_snapshot_digest",
        ),
        (
            "eligibility_source_id",
            "different-source",
            "eligibility source_id",
        ),
    ),
)
def test_cross_field_reference_mismatches_are_rejected(
    target: str,
    replacement: str,
    message: str,
) -> None:
    evidence = _accepted_evidence()

    if target.startswith("candidate_"):
        candidate_reference = replace(
            evidence.candidate_reference,
            **{target: replacement},
        )
        with pytest.raises(ValueError, match=message):
            replace(
                evidence,
                candidate_reference=candidate_reference,
            )
    elif target == "eligibility_candidate_digest":
        eligibility_result = replace(
            evidence.eligibility_result,
            candidate_snapshot_digest=replacement,
        )
        with pytest.raises(ValueError, match=message):
            replace(
                evidence,
                eligibility_result=eligibility_result,
            )
    else:
        eligibility_result = replace(
            evidence.eligibility_result,
            source_id=replacement,
        )
        with pytest.raises(ValueError, match=message):
            replace(
                evidence,
                eligibility_result=eligibility_result,
            )


def test_nested_contracts_require_exact_runtime_types() -> None:
    evidence = _accepted_evidence()

    with pytest.raises(ValueError, match="candidate_reference"):
        replace(
            evidence,
            candidate_reference=object(),
        )


def test_payload_is_recursively_immutable() -> None:
    payload = _accepted_evidence().factual_payload.payload

    with pytest.raises(TypeError):
        payload[0] = ("changed", 1)


def test_construction_uses_only_supplied_audit_timestamps() -> None:
    evidence = _accepted_evidence()

    assert evidence.provenance.observed_at is FIXED_TIME
    assert evidence.eligibility_result.evaluated_at is FIXED_TIME
    assert evidence.materialization_record.materialized_at is FIXED_TIME
