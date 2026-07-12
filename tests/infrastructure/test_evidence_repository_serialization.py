from __future__ import annotations

from dataclasses import MISSING, fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
import json
import unicodedata

import pytest

import rie.infrastructure.evidence_repository_serialization as module
from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
)
from rie.domain.acceptance_record import (
    AcceptanceDiagnostic,
    AcceptanceRecord,
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
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)
from rie.infrastructure.evidence_repository_serialization import (
    ACCEPTANCE_RECORD_PAYLOAD_SCHEMA_ID,
    ACCEPTED_EVIDENCE_PAYLOAD_SCHEMA_ID,
    EVIDENCE_PERSISTENCE_CONTRACT_VERSION,
    PERSISTENCE_DIGEST_ALGORITHM,
    SerializedAcceptanceRecord,
    SerializedAcceptedEvidenceRecord,
    deserialize_acceptance_record,
    deserialize_accepted_evidence,
    serialize_acceptance_record,
    serialize_accepted_evidence,
)


FIXED_TIME = datetime(
    2026,
    7,
    12,
    12,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)


def _build_aggregates(
    *,
    source_path: str = "official/source.pdf",
    accepted_by: str = "reviewer",
    evidence_diagnostics: tuple[EvidenceDiagnostic, ...] = (),
    acceptance_diagnostics: tuple[
        AcceptanceDiagnostic,
        ...,
    ] = (),
    accepted_at: datetime = FIXED_TIME,
) -> tuple[AcceptedEvidence, AcceptanceRecord, str, str]:
    candidate_reference = EvidenceCandidateReference(
        candidate_contract_version="1.0.0",
        candidate_snapshot_digest="candidate-digest",
        candidate_source_id="source-1",
        candidate_producer_name="producer",
        candidate_producer_version="1.0.0",
        candidate_payload_digest="payload-digest",
    )
    source_snapshot = EvidenceSourceSnapshot(
        source_id="source-1",
        source_path=source_path,
        source_type="pdf",
        document_classification="brand_knowledge_spec",
        authority_status="source_of_truth_candidate",
        lifecycle_status="locked",
        evidence_eligibility="eligible",
        source_content_digest="source-content-digest",
    )
    producer_snapshot = EvidenceProducerSnapshot(
        producer_name="producer",
        producer_version="1.0.0",
        producer_kind="deterministic",
        producer_contract_version="1.0.0",
    )
    factual_payload = EvidencePayload(
        payload_type="text",
        payload_schema_version="1.0.0",
        payload=(
            ("active", True),
            ("count", 7),
            ("text", "Fakta café"),
        ),
        payload_digest="payload-digest",
        locator=EvidenceLocator(
            locator_type="page",
            locator_value=("page_index", 1),
            locator_schema_version="1.0.0",
        ),
    )
    provenance = EvidenceProvenance(
        collection_id="collection-1",
        producer_output_digest="producer-output-digest",
        lineage=("candidate-1", "candidate-2"),
        observed_at=accepted_at,
        source_registry_version="1.0.0",
    )
    eligibility_result = AcceptedEligibilityResult(
        decision="eligible",
        policy_id="eligibility-policy",
        policy_version="1.0.0",
        candidate_snapshot_digest="candidate-digest",
        source_id="source-1",
        reason_codes=("eligible", "reviewed"),
        evaluated_at=accepted_at,
        evaluated_by=accepted_by,
        diagnostics=evidence_diagnostics,
    )
    provisional_materialization = EvidenceMaterializationRecord(
        materializer_id="materializer",
        materializer_version="1.0.0",
        materialized_at=accepted_at,
        acceptance_record_id=f"ar1_{'0' * 64}",
        accepted_by=accepted_by,
        acceptance_reason="approved",
        review_record_id="review-1",
        identity_policy_id="rcis-evidence-identity",
        identity_policy_version="1.0.0",
    )
    provisional_evidence = AcceptedEvidence(
        evidence_id=f"ev1_{'0' * 64}",
        contract_version="1.0.0",
        candidate_reference=candidate_reference,
        source_snapshot=source_snapshot,
        producer_snapshot=producer_snapshot,
        factual_payload=factual_payload,
        provenance=provenance,
        eligibility_result=eligibility_result,
        materialization_record=provisional_materialization,
        diagnostics=evidence_diagnostics,
    )
    evidence_identity = calculate_evidence_identity(
        identity_input_from_accepted_evidence(
            provisional_evidence
        )
    )
    provisional_acceptance = AcceptanceRecord(
        acceptance_record_id=f"ar1_{'0' * 64}",
        contract_version="1.0.0",
        evidence_id=evidence_identity.evidence_id,
        accepted_by=accepted_by,
        acceptance_reason="approved",
        review_record_id="review-1",
        accepted_at=accepted_at,
        acceptance_policy_id="acceptance-policy",
        acceptance_policy_version="1.0.0",
        evidence_identity_policy_id="rcis-evidence-identity",
        evidence_identity_policy_version="1.0.0",
        materializer_id="materializer",
        materializer_version="1.0.0",
        diagnostics=acceptance_diagnostics,
    )
    acceptance_identity = calculate_acceptance_identity(
        acceptance_identity_input_from_record(
            provisional_acceptance
        )
    )
    accepted_evidence = replace(
        provisional_evidence,
        evidence_id=evidence_identity.evidence_id,
        materialization_record=replace(
            provisional_materialization,
            acceptance_record_id=(
                acceptance_identity.acceptance_record_id
            ),
        ),
    )
    acceptance_record = replace(
        provisional_acceptance,
        acceptance_record_id=(
            acceptance_identity.acceptance_record_id
        ),
    )
    return (
        accepted_evidence,
        acceptance_record,
        evidence_identity.digest_hex,
        acceptance_identity.digest_hex,
    )


def _payload_object(serialized: object) -> dict[str, object]:
    return json.loads(serialized.payload_bytes.decode("utf-8"))


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _replace_payload(
    serialized: object,
    payload_bytes: bytes,
) -> object:
    return replace(
        serialized,
        payload_bytes=payload_bytes,
        payload_bytes_digest=hashlib.sha256(
            payload_bytes
        ).hexdigest(),
    )


def _forge_dataclass(instance: object, **changes: object) -> object:
    forged = object.__new__(type(instance))
    for field in fields(instance):
        object.__setattr__(
            forged,
            field.name,
            changes.get(field.name, getattr(instance, field.name)),
        )
    return forged


def _serialized_pair() -> tuple[
    SerializedAcceptedEvidenceRecord,
    SerializedAcceptanceRecord,
]:
    evidence, acceptance, evidence_digest, acceptance_digest = (
        _build_aggregates()
    )
    return (
        serialize_accepted_evidence(evidence, evidence_digest),
        serialize_acceptance_record(
            acceptance,
            acceptance_digest,
        ),
    )


def test_exact_constants() -> None:
    assert EVIDENCE_PERSISTENCE_CONTRACT_VERSION == "1.0.0"
    assert (
        ACCEPTED_EVIDENCE_PAYLOAD_SCHEMA_ID
        == "accepted-evidence-json-v1"
    )
    assert (
        ACCEPTANCE_RECORD_PAYLOAD_SCHEMA_ID
        == "acceptance-record-json-v1"
    )
    assert PERSISTENCE_DIGEST_ALGORITHM == "sha256"


@pytest.mark.parametrize(
    ("record_type", "expected_names"),
    (
        (
            SerializedAcceptedEvidenceRecord,
            (
                "persistence_contract_version",
                "payload_schema_id",
                "evidence_id",
                "identity_policy_id",
                "identity_policy_version",
                "canonical_identity_digest",
                "payload_bytes_digest",
                "payload_bytes",
            ),
        ),
        (
            SerializedAcceptanceRecord,
            (
                "persistence_contract_version",
                "payload_schema_id",
                "acceptance_record_id",
                "evidence_id",
                "identity_policy_id",
                "identity_policy_version",
                "canonical_identity_digest",
                "payload_bytes_digest",
                "payload_bytes",
            ),
        ),
    ),
)
def test_exact_frozen_serialized_record_fields(
    record_type: type[object],
    expected_names: tuple[str, ...],
) -> None:
    assert tuple(field.name for field in fields(record_type)) == (
        expected_names
    )
    assert record_type.__dataclass_params__.frozen is True
    assert all(
        field.default is MISSING
        and field.default_factory is MISSING
        for field in fields(record_type)
    )


def test_exact_public_function_set() -> None:
    public_functions = {
        name
        for name, value in inspect.getmembers(
            module,
            inspect.isfunction,
        )
        if value.__module__ == module.__name__
        and not name.startswith("_")
    }

    assert public_functions == {
        "serialize_accepted_evidence",
        "deserialize_accepted_evidence",
        "serialize_acceptance_record",
        "deserialize_acceptance_record",
    }


@pytest.mark.parametrize(
    "serializer_index",
    (0, 1),
)
def test_serialization_is_deterministic(
    serializer_index: int,
) -> None:
    evidence, acceptance, evidence_digest, acceptance_digest = (
        _build_aggregates()
    )
    serializers = (
        lambda: serialize_accepted_evidence(
            evidence,
            evidence_digest,
        ),
        lambda: serialize_acceptance_record(
            acceptance,
            acceptance_digest,
        ),
    )

    first = serializers[serializer_index]()
    second = serializers[serializer_index]()

    assert first.payload_bytes == second.payload_bytes
    assert (
        first.payload_bytes_digest
        == second.payload_bytes_digest
        == hashlib.sha256(first.payload_bytes).hexdigest()
    )


def test_accepted_evidence_round_trip_equality() -> None:
    evidence, _, evidence_digest, _ = _build_aggregates()

    serialized = serialize_accepted_evidence(
        evidence,
        evidence_digest,
    )

    assert deserialize_accepted_evidence(serialized) == evidence


def test_acceptance_record_round_trip_equality() -> None:
    _, acceptance, _, acceptance_digest = _build_aggregates()

    serialized = serialize_acceptance_record(
        acceptance,
        acceptance_digest,
    )

    assert deserialize_acceptance_record(serialized) == acceptance


def test_round_trip_preserves_diagnostics_and_materialization() -> None:
    evidence_diagnostic = EvidenceDiagnostic(
        code="evidence-info",
        severity="info",
        message="diagnostic café",
        field="diagnostics",
        source="test",
    )
    acceptance_diagnostic = AcceptanceDiagnostic(
        code="acceptance-info",
        severity="warning",
        message="review diagnostic",
        field="diagnostics",
        source="test",
    )
    evidence, acceptance, evidence_digest, acceptance_digest = (
        _build_aggregates(
            evidence_diagnostics=(evidence_diagnostic,),
            acceptance_diagnostics=(acceptance_diagnostic,),
        )
    )

    restored_evidence = deserialize_accepted_evidence(
        serialize_accepted_evidence(evidence, evidence_digest)
    )
    restored_acceptance = deserialize_acceptance_record(
        serialize_acceptance_record(
            acceptance,
            acceptance_digest,
        )
    )

    assert restored_evidence.diagnostics == (evidence_diagnostic,)
    assert (
        restored_evidence.eligibility_result.diagnostics
        == (evidence_diagnostic,)
    )
    assert (
        restored_evidence.materialization_record
        == evidence.materialization_record
    )
    assert restored_acceptance.diagnostics == (
        acceptance_diagnostic,
    )


def test_datetime_is_utc_with_exact_six_digits() -> None:
    offset_time = datetime(
        2026,
        7,
        12,
        17,
        30,
        0,
        654321,
        tzinfo=timezone(timedelta(hours=5, minutes=30)),
    )
    evidence, acceptance, evidence_digest, acceptance_digest = (
        _build_aggregates(accepted_at=offset_time)
    )

    evidence_object = _payload_object(
        serialize_accepted_evidence(evidence, evidence_digest)
    )
    acceptance_object = _payload_object(
        serialize_acceptance_record(
            acceptance,
            acceptance_digest,
        )
    )

    assert (
        evidence_object["provenance"]["observed_at"]
        == "2026-07-12T12:00:00.654321Z"
    )
    assert (
        evidence_object["materialization_record"][
            "materialized_at"
        ]
        == "2026-07-12T12:00:00.654321Z"
    )
    assert (
        acceptance_object["accepted_at"]
        == "2026-07-12T12:00:00.654321Z"
    )


def test_unicode_is_nfc_and_non_ascii_is_preserved() -> None:
    decomposed = "official/cafe\u0301.pdf"
    composed = unicodedata.normalize("NFC", decomposed)
    first, _, first_digest, _ = _build_aggregates(
        source_path=decomposed
    )
    second, _, second_digest, _ = _build_aggregates(
        source_path=composed
    )

    first_record = serialize_accepted_evidence(
        first,
        first_digest,
    )
    second_record = serialize_accepted_evidence(
        second,
        second_digest,
    )

    assert first_record.payload_bytes == second_record.payload_bytes
    assert "café".encode("utf-8") in first_record.payload_bytes
    assert b"\\u00e9" not in first_record.payload_bytes
    assert (
        deserialize_accepted_evidence(
            first_record
        ).source_snapshot.source_path
        == composed
    )


def test_ordered_tuples_and_pairs_are_preserved() -> None:
    evidence, _, evidence_digest, _ = _build_aggregates()

    restored = deserialize_accepted_evidence(
        serialize_accepted_evidence(evidence, evidence_digest)
    )

    assert restored.factual_payload.payload == (
        ("active", True),
        ("count", 7),
        ("text", "Fakta café"),
    )
    assert restored.factual_payload.locator.locator_value == (
        "page_index",
        1,
    )
    assert restored.provenance.lineage == (
        "candidate-1",
        "candidate-2",
    )
    assert restored.eligibility_result.reason_codes == (
        "eligible",
        "reviewed",
    )


@pytest.mark.parametrize(
    ("function", "value"),
    (
        (serialize_accepted_evidence, object()),
        (serialize_acceptance_record, object()),
        (deserialize_accepted_evidence, object()),
        (deserialize_acceptance_record, object()),
    ),
)
def test_invalid_exact_input_type_fails_closed(
    function: object,
    value: object,
) -> None:
    with pytest.raises(ValueError, match="exact"):
        if function in (
            serialize_accepted_evidence,
            serialize_acceptance_record,
        ):
            function(value, "0" * 64)
        else:
            function(value)


@pytest.mark.parametrize(
    "record_index",
    (0, 1),
)
def test_unsupported_contract_version_is_rejected(
    record_index: int,
) -> None:
    records = _serialized_pair()
    invalid = replace(
        records[record_index],
        persistence_contract_version="2.0.0",
    )
    deserializers = (
        deserialize_accepted_evidence,
        deserialize_acceptance_record,
    )

    with pytest.raises(
        ValueError,
        match="unsupported persistence contract",
    ):
        deserializers[record_index](invalid)


@pytest.mark.parametrize(
    "record_index",
    (0, 1),
)
def test_unsupported_schema_id_is_rejected(
    record_index: int,
) -> None:
    records = _serialized_pair()
    invalid = replace(
        records[record_index],
        payload_schema_id="unsupported-json-v9",
    )
    deserializers = (
        deserialize_accepted_evidence,
        deserialize_acceptance_record,
    )

    with pytest.raises(ValueError, match="unsupported payload schema"):
        deserializers[record_index](invalid)


@pytest.mark.parametrize(
    "record_index",
    (0, 1),
)
def test_invalid_record_identifier_is_rejected(
    record_index: int,
) -> None:
    records = _serialized_pair()
    identifier_field = (
        "evidence_id"
        if record_index == 0
        else "acceptance_record_id"
    )
    invalid = _forge_dataclass(
        records[record_index],
        **{identifier_field: "invalid"},
    )
    deserializers = (
        deserialize_accepted_evidence,
        deserialize_acceptance_record,
    )

    with pytest.raises(ValueError, match="invalid format"):
        deserializers[record_index](invalid)


@pytest.mark.parametrize(
    ("field_name", "expected_message"),
    (
        ("identity_policy_id", "identity policy id mismatch"),
        (
            "identity_policy_version",
            "identity policy version mismatch",
        ),
    ),
)
def test_identity_policy_metadata_mismatch_is_rejected(
    field_name: str,
    expected_message: str,
) -> None:
    evidence_record, _ = _serialized_pair()
    invalid = replace(
        evidence_record,
        **{field_name: "wrong-policy"},
    )

    with pytest.raises(ValueError, match=expected_message):
        deserialize_accepted_evidence(invalid)


@pytest.mark.parametrize(
    "serializer_index",
    (0, 1),
)
def test_caller_identity_digest_mismatch_is_rejected(
    serializer_index: int,
) -> None:
    evidence, acceptance, _, _ = _build_aggregates()
    values = (evidence, acceptance)
    serializers = (
        serialize_accepted_evidence,
        serialize_acceptance_record,
    )

    with pytest.raises(ValueError, match="digest suffix mismatch"):
        serializers[serializer_index](
            values[serializer_index],
            "f" * 64,
        )


@pytest.mark.parametrize(
    "record_index",
    (0, 1),
)
def test_payload_digest_mismatch_is_rejected(
    record_index: int,
) -> None:
    records = _serialized_pair()
    invalid = replace(
        records[record_index],
        payload_bytes_digest="f" * 64,
    )
    deserializers = (
        deserialize_accepted_evidence,
        deserialize_acceptance_record,
    )

    with pytest.raises(ValueError, match="payload bytes digest"):
        deserializers[record_index](invalid)


def test_invalid_utf8_is_rejected() -> None:
    evidence_record, _ = _serialized_pair()
    invalid = _replace_payload(
        evidence_record,
        b"\xff\xfe\xfd",
    )

    with pytest.raises(ValueError, match="valid UTF-8"):
        deserialize_accepted_evidence(invalid)


def test_duplicate_json_key_is_rejected() -> None:
    evidence_record, _ = _serialized_pair()
    duplicate = (
        b'{"evidence_id":"one","evidence_id":"two"}'
    )
    invalid = _replace_payload(evidence_record, duplicate)

    with pytest.raises(ValueError, match="duplicate JSON key"):
        deserialize_accepted_evidence(invalid)


@pytest.mark.parametrize(
    ("mutation", "expected_message"),
    (
        ("missing", "fields mismatch"),
        ("extra", "fields mismatch"),
    ),
)
def test_missing_and_extra_fields_are_rejected(
    mutation: str,
    expected_message: str,
) -> None:
    evidence_record, _ = _serialized_pair()
    payload = _payload_object(evidence_record)
    if mutation == "missing":
        payload.pop("diagnostics")
    else:
        payload["unexpected"] = "value"
    invalid = _replace_payload(
        evidence_record,
        _canonical_bytes(payload),
    )

    with pytest.raises(ValueError, match=expected_message):
        deserialize_accepted_evidence(invalid)


def test_noncanonical_json_bytes_are_rejected() -> None:
    evidence_record, _ = _serialized_pair()
    payload = _payload_object(evidence_record)
    noncanonical = json.dumps(
        payload,
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
    invalid = _replace_payload(
        evidence_record,
        noncanonical,
    )

    with pytest.raises(ValueError, match="not canonical JSON"):
        deserialize_accepted_evidence(invalid)


@pytest.mark.parametrize(
    ("path", "value"),
    (
        ("source_snapshot", []),
        ("payload_float", 1.5),
    ),
)
def test_invalid_nested_type_or_float_is_rejected(
    path: str,
    value: object,
) -> None:
    evidence_record, _ = _serialized_pair()
    payload = _payload_object(evidence_record)
    if path == "source_snapshot":
        payload["source_snapshot"] = value
    else:
        payload["factual_payload"]["locator"][
            "locator_value"
        ] = value
    invalid = _replace_payload(
        evidence_record,
        _canonical_bytes(payload),
    )

    with pytest.raises(ValueError):
        deserialize_accepted_evidence(invalid)


@pytest.mark.parametrize(
    "datetime_path",
    ("observed_at", "materialized_at"),
)
def test_invalid_datetime_is_rejected(
    datetime_path: str,
) -> None:
    evidence_record, _ = _serialized_pair()
    payload = _payload_object(evidence_record)
    if datetime_path == "observed_at":
        payload["provenance"]["observed_at"] = (
            "2026-07-12T12:00:00Z"
        )
    else:
        payload["materialization_record"][
            "materialized_at"
        ] = "not-a-datetime"
    invalid = _replace_payload(
        evidence_record,
        _canonical_bytes(payload),
    )

    with pytest.raises(ValueError, match="datetime"):
        deserialize_accepted_evidence(invalid)


def test_reconstructed_evidence_identity_mismatch_is_rejected() -> None:
    evidence_record, _ = _serialized_pair()
    payload = _payload_object(evidence_record)
    payload["source_snapshot"]["source_content_digest"] = (
        "different-source-digest"
    )
    invalid = _replace_payload(
        evidence_record,
        _canonical_bytes(payload),
    )

    with pytest.raises(ValueError, match="identity"):
        deserialize_accepted_evidence(invalid)


def test_reconstructed_acceptance_identity_mismatch_is_rejected() -> None:
    _, acceptance_record = _serialized_pair()
    payload = _payload_object(acceptance_record)
    payload["acceptance_reason"] = "different reason"
    invalid = _replace_payload(
        acceptance_record,
        _canonical_bytes(payload),
    )

    with pytest.raises(ValueError, match="identity"):
        deserialize_acceptance_record(invalid)


def test_acceptance_metadata_factual_id_mismatch_is_rejected() -> None:
    _, acceptance_record = _serialized_pair()
    different_evidence_id = f"ev1_{'a' * 64}"
    invalid = replace(
        acceptance_record,
        evidence_id=different_evidence_id,
    )

    with pytest.raises(ValueError, match="evidence_id mismatch"):
        deserialize_acceptance_record(invalid)


def test_serialized_payload_has_no_bom_or_trailing_whitespace() -> None:
    evidence_record, acceptance_record = _serialized_pair()

    for record in (evidence_record, acceptance_record):
        assert not record.payload_bytes.startswith(b"\xef\xbb\xbf")
        assert record.payload_bytes == record.payload_bytes.rstrip()


def test_error_messages_do_not_echo_payload_content() -> None:
    evidence_record, _ = _serialized_pair()
    invalid = _replace_payload(
        evidence_record,
        b"SECRET-CONTENT",
    )

    with pytest.raises(ValueError) as exc_info:
        deserialize_accepted_evidence(invalid)

    assert "SECRET-CONTENT" not in str(exc_info.value)


def test_source_has_no_io_sqlite_retry_knowledge_or_prompt_behavior() -> None:
    source = inspect.getsource(module)
    forbidden_fragments = (
        "import os",
        "from os",
        "pathlib",
        "sqlite3",
        "pickle",
        "shelve",
        "subprocess",
        "requests",
        "httpx",
        "socket",
        "logging",
        "os.environ",
        "open(",
        "sleep(",
        "retry",
        "Knowledge",
        "PromptCandidate",
    )

    assert all(
        fragment not in source
        for fragment in forbidden_fragments
    )
