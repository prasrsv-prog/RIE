from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import json
import re
from unicodedata import normalize

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
from rie.domain.evidence_identity import (
    EVIDENCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION,
    EVIDENCE_IDENTITY_DIGEST_ALGORITHM,
    EVIDENCE_IDENTITY_POLICY_ID,
    EVIDENCE_IDENTITY_POLICY_VERSION,
    EvidenceIdentityInput,
    EvidenceIdentityResult,
    calculate_evidence_identity,
    canonicalize_evidence_identity,
    identity_input_from_accepted_evidence,
)


FIXED_TIME = datetime(2026, 7, 12, 9, 0, tzinfo=timezone.utc)

IDENTITY_FIELD_NAMES = (
    "accepted_evidence_contract_version",
    "source_identifier",
    "source_content_digest",
    "producer_name",
    "producer_version",
    "producer_kind",
    "producer_contract_version",
    "payload_type",
    "payload_schema_version",
    "payload_digest",
    "canonical_locator_type",
    "canonical_locator_value",
    "locator_schema_version",
    "producer_output_digest",
)


def _diagnostic(
    *,
    code: str = "accepted",
    message: str = "Accepted by explicit policy",
) -> EvidenceDiagnostic:
    return EvidenceDiagnostic(
        code=code,
        severity="info",
        message=message,
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
    factual_payload = EvidencePayload(
        payload_type="document_structural_metadata",
        payload_schema_version="payload-v1",
        payload=(("page_count", 1), ("title", "SV300")),
        payload_digest="payload-digest",
        locator=EvidenceLocator(
            locator_type="page",
            locator_value=("page_index", 0),
            locator_schema_version="locator-v1",
        ),
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


def _identity_input() -> EvidenceIdentityInput:
    return identity_input_from_accepted_evidence(_accepted_evidence())


def test_identity_input_is_frozen() -> None:
    value = _identity_input()

    with pytest.raises(FrozenInstanceError):
        value.source_identifier = "changed"


def test_identity_result_is_frozen() -> None:
    value = calculate_evidence_identity(_identity_input())

    with pytest.raises(FrozenInstanceError):
        value.digest_hex = "0" * 64


@pytest.mark.parametrize(
    "contract_type",
    (EvidenceIdentityInput, EvidenceIdentityResult),
)
def test_identity_contract_fields_have_no_defaults(
    contract_type: type[object],
) -> None:
    assert all(
        field.default is MISSING
        and field.default_factory is MISSING
        for field in fields(contract_type)
    )


def test_identity_input_has_exact_fourteen_fields_in_fixed_order() -> None:
    assert tuple(field.name for field in fields(EvidenceIdentityInput)) == (
        IDENTITY_FIELD_NAMES
    )


def test_identity_result_has_exact_reviewed_fields() -> None:
    assert tuple(field.name for field in fields(EvidenceIdentityResult)) == (
        "evidence_id",
        "digest_algorithm",
        "digest_hex",
        "identity_policy_id",
        "identity_policy_version",
        "canonicalization_contract_version",
        "canonical_byte_length",
    )


def test_identity_input_extraction_maps_exact_factual_values() -> None:
    accepted = _accepted_evidence()

    assert identity_input_from_accepted_evidence(accepted) == EvidenceIdentityInput(
        accepted_evidence_contract_version="accepted-evidence-v1",
        source_identifier="source-1",
        source_content_digest="source-digest",
        producer_name="structural-inspector",
        producer_version="1.0.0",
        producer_kind="inspector",
        producer_contract_version="result-v1",
        payload_type="document_structural_metadata",
        payload_schema_version="payload-v1",
        payload_digest="payload-digest",
        canonical_locator_type="page",
        canonical_locator_value=("page_index", 0),
        locator_schema_version="locator-v1",
        producer_output_digest="producer-output-digest",
    )


def test_canonical_json_uses_exact_fixed_key_order() -> None:
    canonical = canonicalize_evidence_identity(_identity_input())
    decoded = json.loads(canonical.decode("utf-8"))

    assert tuple(decoded) == IDENTITY_FIELD_NAMES


def test_canonical_json_has_no_insignificant_whitespace() -> None:
    canonical_text = canonicalize_evidence_identity(
        _identity_input()
    ).decode("utf-8")

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text
    assert "\r" not in canonical_text


def test_canonical_json_is_utf8_and_preserves_non_ascii_text() -> None:
    value = replace(
        _identity_input(),
        source_identifier="sumber-helm-Çilek",
    )
    canonical = canonicalize_evidence_identity(value)

    assert "Çilek".encode("utf-8") in canonical
    assert "\\u00c7" not in canonical.decode("utf-8")


def test_text_is_normalized_to_nfc_recursively() -> None:
    decomposed = "Cafe\u0301"
    value = replace(
        _identity_input(),
        source_identifier=decomposed,
        canonical_locator_value=("label", decomposed),
    )
    decoded = json.loads(
        canonicalize_evidence_identity(value).decode("utf-8")
    )

    assert decoded["source_identifier"] == normalize("NFC", decomposed)
    assert decoded["canonical_locator_value"][1] == normalize(
        "NFC",
        decomposed,
    )


def test_canonically_equivalent_unicode_has_same_identity() -> None:
    composed = replace(
        _identity_input(),
        source_identifier="Café",
        canonical_locator_value=("label", "Café"),
    )
    decomposed = replace(
        _identity_input(),
        source_identifier="Cafe\u0301",
        canonical_locator_value=("label", "Cafe\u0301"),
    )

    assert calculate_evidence_identity(composed) == calculate_evidence_identity(
        decomposed
    )


def test_repeated_calculation_is_deterministic() -> None:
    value = _identity_input()

    assert calculate_evidence_identity(value) == calculate_evidence_identity(
        value
    )


def test_result_uses_lowercase_sha256_and_ev1_prefix() -> None:
    result = calculate_evidence_identity(_identity_input())

    assert result.digest_algorithm == "sha256"
    assert re.fullmatch(r"[0-9a-f]{64}", result.digest_hex)
    assert result.evidence_id == f"ev1_{result.digest_hex}"


def test_result_exposes_exact_policy_versions() -> None:
    result = calculate_evidence_identity(_identity_input())

    assert result.digest_algorithm == EVIDENCE_IDENTITY_DIGEST_ALGORITHM
    assert result.identity_policy_id == EVIDENCE_IDENTITY_POLICY_ID
    assert result.identity_policy_version == EVIDENCE_IDENTITY_POLICY_VERSION
    assert (
        result.canonicalization_contract_version
        == EVIDENCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION
    )
    assert result.canonical_byte_length == len(
        canonicalize_evidence_identity(_identity_input())
    )


@pytest.mark.parametrize(
    ("field_name", "changed_value"),
    (
        ("accepted_evidence_contract_version", "accepted-evidence-v2"),
        ("source_identifier", "source-2"),
        ("source_content_digest", "source-digest-2"),
        ("producer_name", "other-producer"),
        ("producer_version", "2.0.0"),
        ("producer_kind", "extractor"),
        ("producer_contract_version", "result-v2"),
        ("payload_type", "other-payload"),
        ("payload_schema_version", "payload-v2"),
        ("payload_digest", "payload-digest-2"),
        ("canonical_locator_type", "section"),
        ("canonical_locator_value", ("page_index", 1)),
        ("locator_schema_version", "locator-v2"),
        ("producer_output_digest", "producer-output-digest-2"),
    ),
)
def test_each_factual_input_changes_identity(
    field_name: str,
    changed_value: object,
) -> None:
    baseline = _identity_input()
    changed = replace(baseline, **{field_name: changed_value})

    assert (
        calculate_evidence_identity(changed).evidence_id
        != calculate_evidence_identity(baseline).evidence_id
    )


def test_excluded_governance_fields_do_not_change_factual_identity() -> None:
    baseline = _accepted_evidence()
    changed = replace(
        baseline,
        source_snapshot=replace(
            baseline.source_snapshot,
            source_path="different/path.pdf",
            document_classification="secondary_reference",
            authority_status="reviewed",
            lifecycle_status="superseded",
            evidence_eligibility="eligible_after_review",
        ),
        provenance=replace(
            baseline.provenance,
            collection_id="collection-2",
            lineage=("different-lineage",),
            observed_at=FIXED_TIME + timedelta(days=1),
            source_registry_version="registry-v2",
        ),
        eligibility_result=replace(
            baseline.eligibility_result,
            policy_id="different-policy",
            policy_version="9.0.0",
            reason_codes=("different-reason",),
            evaluated_at=FIXED_TIME + timedelta(days=1),
            evaluated_by="different-reviewer",
            diagnostics=(_diagnostic(code="changed"),),
        ),
        materialization_record=replace(
            baseline.materialization_record,
            materializer_id="different-materializer",
            materializer_version="9.0.0",
            materialized_at=FIXED_TIME + timedelta(days=1),
            acceptance_record_id="acceptance-record-2",
            accepted_by="different-reviewer",
            acceptance_reason="Different governance reason",
            review_record_id="review-2",
            identity_policy_id="governance-policy",
            identity_policy_version="9.0.0",
        ),
        diagnostics=(_diagnostic(message="Changed diagnostic"),),
    )

    assert calculate_evidence_identity(
        identity_input_from_accepted_evidence(baseline)
    ) == calculate_evidence_identity(
        identity_input_from_accepted_evidence(changed)
    )


@pytest.mark.parametrize(
    "field_name",
    tuple(
        name
        for name in IDENTITY_FIELD_NAMES
        if name != "canonical_locator_value"
    ),
)
def test_string_identity_fields_reject_empty_values(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        replace(_identity_input(), **{field_name: " "})


@pytest.mark.parametrize(
    "locator_value",
    (
        [],
        {},
        set(),
        (),
        None,
        float("nan"),
        float("inf"),
    ),
)
def test_locator_value_rejects_mutable_empty_or_non_finite_values(
    locator_value: object,
) -> None:
    with pytest.raises(ValueError, match="canonical_locator_value"):
        replace(
            _identity_input(),
            canonical_locator_value=locator_value,
        )


@pytest.mark.parametrize(
    "bad_value",
    (
        object(),
        _accepted_evidence(),
        "not-an-input",
    ),
)
def test_canonicalization_requires_exact_identity_input(
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match="identity_input"):
        canonicalize_evidence_identity(bad_value)


@pytest.mark.parametrize(
    "bad_value",
    (
        object(),
        _identity_input(),
        "not-accepted-evidence",
    ),
)
def test_extraction_requires_exact_accepted_evidence(
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match="accepted_evidence"):
        identity_input_from_accepted_evidence(bad_value)


def test_result_rejects_non_sha256_algorithm() -> None:
    valid = calculate_evidence_identity(_identity_input())

    with pytest.raises(ValueError, match="digest_algorithm"):
        replace(valid, digest_algorithm="sha512")


@pytest.mark.parametrize(
    "digest_hex",
    (
        "A" * 64,
        "g" * 64,
        "0" * 63,
        "",
    ),
)
def test_result_rejects_invalid_digest_hex(digest_hex: str) -> None:
    valid = calculate_evidence_identity(_identity_input())

    with pytest.raises(ValueError, match="digest_hex"):
        replace(
            valid,
            digest_hex=digest_hex,
            evidence_id=f"ev1_{digest_hex}",
        )


def test_result_rejects_evidence_id_not_matching_digest() -> None:
    valid = calculate_evidence_identity(_identity_input())

    with pytest.raises(ValueError, match="evidence_id"):
        replace(valid, evidence_id=f"ev1_{'0' * 64}")


@pytest.mark.parametrize("byte_length", (0, -1, 1.5, True))
def test_result_requires_positive_integer_canonical_byte_length(
    byte_length: object,
) -> None:
    valid = calculate_evidence_identity(_identity_input())

    with pytest.raises(ValueError, match="canonical_byte_length"):
        replace(valid, canonical_byte_length=byte_length)


def test_canonical_output_contains_only_fourteen_identity_keys() -> None:
    decoded = json.loads(
        canonicalize_evidence_identity(_identity_input()).decode("utf-8")
    )

    assert set(decoded) == set(IDENTITY_FIELD_NAMES)
    assert len(decoded) == 14


def test_canonical_output_excludes_governance_and_repository_keys() -> None:
    canonical_text = canonicalize_evidence_identity(
        _identity_input()
    ).decode("utf-8")

    for forbidden in (
        "authority_status",
        "lifecycle_status",
        "evidence_eligibility",
        "eligibility_result",
        "materialization_record",
        "acceptance_record_id",
        "repository",
        "knowledge",
        "prompt",
    ):
        assert forbidden not in canonical_text.lower()


def test_identity_calculation_has_no_implicit_clock_or_random_state() -> None:
    value = _identity_input()
    results = tuple(calculate_evidence_identity(value) for _ in range(5))

    assert len(set(results)) == 1
