from dataclasses import MISSING, FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
import hashlib
import json
import unicodedata

import pytest

import rie.domain.acceptance_identity as identity_module
from rie.domain.acceptance_identity import (
    ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION,
    ACCEPTANCE_IDENTITY_DIGEST_ALGORITHM,
    ACCEPTANCE_IDENTITY_POLICY_ID,
    ACCEPTANCE_IDENTITY_POLICY_VERSION,
    ACCEPTANCE_RECORD_ID_PREFIX,
    AcceptanceIdentityInput,
    AcceptanceIdentityResult,
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
)
from rie.domain.acceptance_record import (
    AcceptanceDiagnostic,
    AcceptanceRecord,
)


FIXED_TIME = datetime(2026, 7, 12, 9, 0, 0, 123456, tzinfo=timezone.utc)
VALID_EVIDENCE_ID = f"ev1_{'b' * 64}"


def _identity_input(**changes: object) -> AcceptanceIdentityInput:
    values = {
        "acceptance_record_contract_version": "acceptance-record-v1",
        "evidence_id": VALID_EVIDENCE_ID,
        "accepted_by": "review-service",
        "acceptance_reason": "Explicit review approval",
        "review_record_id": "review-1",
        "accepted_at": FIXED_TIME,
        "acceptance_policy_id": "official-source-policy",
        "acceptance_policy_version": "1.0.0",
        "evidence_identity_policy_id": "rcis-evidence-identity",
        "evidence_identity_policy_version": "1.0.0",
        "materializer_id": "accepted-evidence-materializer",
        "materializer_version": "1.0.0",
    }
    values.update(changes)
    return AcceptanceIdentityInput(**values)


def _diagnostic(
    *,
    code: str = "accepted",
    severity: str = "info",
) -> AcceptanceDiagnostic:
    return AcceptanceDiagnostic(
        code=code,
        severity=severity,
        message="Explicit acceptance",
        field="acceptance_policy_id",
        source="acceptance-policy",
    )


def _record(
    *,
    identity_input: AcceptanceIdentityInput | None = None,
    diagnostics: tuple[AcceptanceDiagnostic, ...] | None = None,
) -> AcceptanceRecord:
    identity_input = identity_input or _identity_input()
    result = calculate_acceptance_identity(identity_input)

    return AcceptanceRecord(
        acceptance_record_id=result.acceptance_record_id,
        contract_version=(
            identity_input.acceptance_record_contract_version
        ),
        evidence_id=identity_input.evidence_id,
        accepted_by=identity_input.accepted_by,
        acceptance_reason=identity_input.acceptance_reason,
        review_record_id=identity_input.review_record_id,
        accepted_at=identity_input.accepted_at,
        acceptance_policy_id=identity_input.acceptance_policy_id,
        acceptance_policy_version=(
            identity_input.acceptance_policy_version
        ),
        evidence_identity_policy_id=(
            identity_input.evidence_identity_policy_id
        ),
        evidence_identity_policy_version=(
            identity_input.evidence_identity_policy_version
        ),
        materializer_id=identity_input.materializer_id,
        materializer_version=identity_input.materializer_version,
        diagnostics=(
            diagnostics
            if diagnostics is not None
            else (_diagnostic(),)
        ),
    )


@pytest.mark.parametrize(
    "contract_type",
    (AcceptanceIdentityInput, AcceptanceIdentityResult),
)
def test_acceptance_identity_contracts_are_frozen(
    contract_type: type[object],
) -> None:
    instance = (
        _identity_input()
        if contract_type is AcceptanceIdentityInput
        else calculate_acceptance_identity(_identity_input())
    )

    with pytest.raises(FrozenInstanceError):
        setattr(instance, fields(contract_type)[0].name, "changed")


@pytest.mark.parametrize(
    "contract_type",
    (AcceptanceIdentityInput, AcceptanceIdentityResult),
)
def test_acceptance_identity_fields_have_no_defaults(
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
            AcceptanceIdentityInput,
            (
                "acceptance_record_contract_version",
                "evidence_id",
                "accepted_by",
                "acceptance_reason",
                "review_record_id",
                "accepted_at",
                "acceptance_policy_id",
                "acceptance_policy_version",
                "evidence_identity_policy_id",
                "evidence_identity_policy_version",
                "materializer_id",
                "materializer_version",
            ),
        ),
        (
            AcceptanceIdentityResult,
            (
                "acceptance_record_id",
                "digest_algorithm",
                "digest_hex",
                "identity_policy_id",
                "identity_policy_version",
                "canonicalization_contract_version",
                "canonical_byte_length",
            ),
        ),
    ),
)
def test_acceptance_identity_contracts_have_exact_fields(
    contract_type: type[object],
    expected_fields: tuple[str, ...],
) -> None:
    assert tuple(field.name for field in fields(contract_type)) == expected_fields


def test_acceptance_identity_constants_are_exact() -> None:
    assert ACCEPTANCE_IDENTITY_POLICY_ID == (
        "rcis-acceptance-record-identity"
    )
    assert ACCEPTANCE_IDENTITY_POLICY_VERSION == "1.0.0"
    assert ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION == (
        "acceptance-json-v1"
    )
    assert ACCEPTANCE_IDENTITY_DIGEST_ALGORITHM == "sha256"
    assert ACCEPTANCE_RECORD_ID_PREFIX == "ar1_"


def test_calculate_acceptance_identity_is_deterministic() -> None:
    identity_input = _identity_input()

    results = tuple(
        calculate_acceptance_identity(identity_input)
        for _ in range(5)
    )

    assert len(set(results)) == 1


def test_calculate_acceptance_identity_uses_sha256_and_ar1_prefix() -> None:
    identity_input = _identity_input()
    canonical_bytes = (
        identity_module._canonical_acceptance_identity_bytes(
            identity_input
        )
    )
    expected_digest = hashlib.sha256(canonical_bytes).hexdigest()

    result = calculate_acceptance_identity(identity_input)

    assert result.digest_hex == expected_digest
    assert result.acceptance_record_id == f"ar1_{expected_digest}"
    assert result.canonical_byte_length == len(canonical_bytes)


def test_canonical_mapping_has_exact_key_order() -> None:
    mapping = identity_module._canonical_acceptance_identity_mapping(
        _identity_input()
    )

    assert tuple(mapping) == (
        "acceptance_record_contract_version",
        "evidence_id",
        "accepted_by",
        "acceptance_reason",
        "review_record_id",
        "accepted_at",
        "acceptance_policy_id",
        "acceptance_policy_version",
        "evidence_identity_policy_id",
        "evidence_identity_policy_version",
        "materializer_id",
        "materializer_version",
    )


def test_canonical_json_is_compact_utf8_and_has_no_null() -> None:
    identity_input = _identity_input(acceptance_reason="Disetujui ✓")
    canonical_bytes = (
        identity_module._canonical_acceptance_identity_bytes(
            identity_input
        )
    )
    decoded = canonical_bytes.decode("utf-8")

    assert "✓" in decoded
    assert ": " not in decoded
    assert ", " not in decoded
    assert "null" not in decoded
    assert json.loads(decoded)["acceptance_reason"] == "Disetujui ✓"


def test_canonicalization_normalizes_text_to_nfc() -> None:
    decomposed = "Cafe\u0301"
    composed = unicodedata.normalize("NFC", decomposed)

    decomposed_result = calculate_acceptance_identity(
        _identity_input(acceptance_reason=decomposed)
    )
    composed_result = calculate_acceptance_identity(
        _identity_input(acceptance_reason=composed)
    )

    assert decomposed_result == composed_result


def test_timestamp_is_rendered_as_six_digit_utc_rfc3339() -> None:
    mapping = identity_module._canonical_acceptance_identity_mapping(
        _identity_input()
    )

    assert mapping["accepted_at"] == "2026-07-12T09:00:00.123456Z"


def test_equivalent_timezone_offsets_produce_same_identity() -> None:
    offset = timezone(timedelta(hours=7))
    local_time = FIXED_TIME.astimezone(offset)

    utc_result = calculate_acceptance_identity(_identity_input())
    local_result = calculate_acceptance_identity(
        _identity_input(accepted_at=local_time)
    )

    assert utc_result == local_result


@pytest.mark.parametrize(
    "invalid_time",
    (
        datetime(2026, 7, 12, 9, 0),
        "2026-07-12T09:00:00Z",
        object(),
    ),
)
def test_identity_input_requires_timezone_aware_datetime(
    invalid_time: object,
) -> None:
    with pytest.raises(ValueError, match="accepted_at"):
        _identity_input(accepted_at=invalid_time)


@pytest.mark.parametrize(
    "field_name",
    (
        "acceptance_record_contract_version",
        "accepted_by",
        "acceptance_reason",
        "review_record_id",
        "acceptance_policy_id",
        "acceptance_policy_version",
        "evidence_identity_policy_id",
        "evidence_identity_policy_version",
        "materializer_id",
        "materializer_version",
    ),
)
def test_identity_input_requires_non_empty_text_fields(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _identity_input(**{field_name: " "})


@pytest.mark.parametrize(
    "invalid_id",
    (
        "",
        "ev1_",
        f"ev1_{'B' * 64}",
        f"ev1_{'b' * 63}",
        f"ev2_{'b' * 64}",
        "not-an-evidence-id",
    ),
)
def test_identity_input_rejects_invalid_evidence_id(
    invalid_id: str,
) -> None:
    with pytest.raises(ValueError, match="evidence_id"):
        _identity_input(evidence_id=invalid_id)


@pytest.mark.parametrize("invalid_input", (None, object(), "input"))
def test_calculate_identity_rejects_non_input(
    invalid_input: object,
) -> None:
    with pytest.raises(ValueError, match="identity_input"):
        calculate_acceptance_identity(invalid_input)


def test_record_to_identity_input_mapping_is_exact() -> None:
    record = _record()

    assert acceptance_identity_input_from_record(record) == (
        _identity_input()
    )


@pytest.mark.parametrize("invalid_record", (None, object(), "record"))
def test_record_to_identity_input_rejects_non_record(
    invalid_record: object,
) -> None:
    with pytest.raises(ValueError, match="record"):
        acceptance_identity_input_from_record(invalid_record)


def test_record_recalculation_matches_record_id_and_full_result() -> None:
    record = _record()
    identity_input = acceptance_identity_input_from_record(record)
    result = calculate_acceptance_identity(identity_input)

    assert result.acceptance_record_id == record.acceptance_record_id
    assert result.identity_policy_id == ACCEPTANCE_IDENTITY_POLICY_ID
    assert result.identity_policy_version == (
        ACCEPTANCE_IDENTITY_POLICY_VERSION
    )
    assert result.canonicalization_contract_version == (
        ACCEPTANCE_IDENTITY_CANONICALIZATION_CONTRACT_VERSION
    )
    assert result.digest_algorithm == ACCEPTANCE_IDENTITY_DIGEST_ALGORITHM


def test_diagnostics_do_not_change_acceptance_identity() -> None:
    record_a = _record(diagnostics=(_diagnostic(code="a"),))
    record_b = _record(
        diagnostics=(
            _diagnostic(code="b", severity="warning"),
        )
    )

    result_a = calculate_acceptance_identity(
        acceptance_identity_input_from_record(record_a)
    )
    result_b = calculate_acceptance_identity(
        acceptance_identity_input_from_record(record_b)
    )

    assert result_a == result_b


@pytest.mark.parametrize(
    ("field_name", "changed_value"),
    (
        ("accepted_by", "review-service-2"),
        ("acceptance_reason", "Second explicit approval"),
        ("review_record_id", "review-2"),
        ("accepted_at", FIXED_TIME + timedelta(seconds=1)),
        ("acceptance_policy_version", "1.0.1"),
        ("materializer_version", "1.0.1"),
    ),
)
def test_same_fact_new_acceptance_values_produce_distinct_identity(
    field_name: str,
    changed_value: object,
) -> None:
    first = calculate_acceptance_identity(_identity_input())
    second = calculate_acceptance_identity(
        _identity_input(**{field_name: changed_value})
    )

    assert first.acceptance_record_id != second.acceptance_record_id
    assert first.digest_hex != second.digest_hex


def test_acceptance_collision_is_detectable_by_digest_difference() -> None:
    first = calculate_acceptance_identity(_identity_input())
    second = calculate_acceptance_identity(
        _identity_input(accepted_by="different-reviewer")
    )

    externally_reused_id = first.acceptance_record_id

    assert externally_reused_id == first.acceptance_record_id
    assert first.digest_hex != second.digest_hex


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("acceptance_record_id", f"ar1_{'0' * 64}"),
        ("digest_algorithm", "sha512"),
        ("digest_hex", "0" * 64),
        ("identity_policy_id", "other-policy"),
        ("identity_policy_version", "2.0.0"),
        ("canonicalization_contract_version", "other-json-v1"),
        ("canonical_byte_length", 0),
        ("canonical_byte_length", True),
    ),
)
def test_identity_result_rejects_invalid_shapes(
    field_name: str,
    invalid_value: object,
) -> None:
    valid = calculate_acceptance_identity(_identity_input())
    values = {
        field.name: getattr(valid, field.name)
        for field in fields(AcceptanceIdentityResult)
    }
    values[field_name] = invalid_value

    with pytest.raises(ValueError):
        AcceptanceIdentityResult(**values)


def test_acceptance_identity_module_has_no_repository_or_downstream_exports() -> None:
    assert not hasattr(identity_module, "EvidenceRepository")
    assert not hasattr(identity_module, "Knowledge")
    assert not hasattr(identity_module, "PromptCandidate")
