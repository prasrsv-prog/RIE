from dataclasses import MISSING, FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone

import pytest

from rie.domain.acceptance_record import (
    AcceptanceDiagnostic,
    AcceptanceRecord,
)


FIXED_TIME = datetime(2026, 7, 12, 9, 0, tzinfo=timezone.utc)
VALID_ACCEPTANCE_ID = f"ar1_{'a' * 64}"
VALID_EVIDENCE_ID = f"ev1_{'b' * 64}"


def _diagnostic(**changes: object) -> AcceptanceDiagnostic:
    values = {
        "code": "accepted",
        "severity": "info",
        "message": "Accepted by explicit policy",
        "field": "acceptance_policy_id",
        "source": "acceptance-policy",
    }
    values.update(changes)
    return AcceptanceDiagnostic(**values)


def _record(**changes: object) -> AcceptanceRecord:
    values = {
        "acceptance_record_id": VALID_ACCEPTANCE_ID,
        "contract_version": "acceptance-record-v1",
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
        "diagnostics": (_diagnostic(),),
    }
    values.update(changes)
    return AcceptanceRecord(**values)


@pytest.mark.parametrize(
    "contract_type",
    (AcceptanceDiagnostic, AcceptanceRecord),
)
def test_acceptance_contracts_are_frozen(
    contract_type: type[object],
) -> None:
    instance = (
        _diagnostic()
        if contract_type is AcceptanceDiagnostic
        else _record()
    )

    with pytest.raises(FrozenInstanceError):
        setattr(instance, fields(contract_type)[0].name, "changed")


@pytest.mark.parametrize(
    "contract_type",
    (AcceptanceDiagnostic, AcceptanceRecord),
)
def test_acceptance_contract_fields_have_no_defaults(
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
            AcceptanceDiagnostic,
            (
                "code",
                "severity",
                "message",
                "field",
                "source",
            ),
        ),
        (
            AcceptanceRecord,
            (
                "acceptance_record_id",
                "contract_version",
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
                "diagnostics",
            ),
        ),
    ),
)
def test_acceptance_contracts_have_exact_fields(
    contract_type: type[object],
    expected_fields: tuple[str, ...],
) -> None:
    assert tuple(field.name for field in fields(contract_type)) == expected_fields


def test_valid_acceptance_record_preserves_explicit_values() -> None:
    record = _record()

    assert record.acceptance_record_id == VALID_ACCEPTANCE_ID
    assert record.evidence_id == VALID_EVIDENCE_ID
    assert record.accepted_at is FIXED_TIME
    assert record.diagnostics == (_diagnostic(),)


@pytest.mark.parametrize(
    "field_name",
    ("code", "severity", "message", "field", "source"),
)
@pytest.mark.parametrize("invalid_value", ("", " "))
def test_acceptance_diagnostic_requires_non_empty_strings(
    field_name: str,
    invalid_value: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _diagnostic(**{field_name: invalid_value})


@pytest.mark.parametrize(
    "severity",
    ("error", "debug", "INFO", "WARNING"),
)
def test_acceptance_diagnostic_rejects_unsupported_severity(
    severity: str,
) -> None:
    with pytest.raises(ValueError, match="severity"):
        _diagnostic(severity=severity)


@pytest.mark.parametrize("severity", ("info", "warning"))
def test_acceptance_diagnostic_allows_exact_severities(
    severity: str,
) -> None:
    assert _diagnostic(severity=severity).severity == severity


@pytest.mark.parametrize(
    "field_name",
    (
        "contract_version",
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
def test_acceptance_record_requires_non_empty_text_fields(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _record(**{field_name: " "})


@pytest.mark.parametrize(
    "invalid_id",
    (
        "",
        "ar1_",
        f"ar1_{'A' * 64}",
        f"ar1_{'a' * 63}",
        f"ar2_{'a' * 64}",
        "not-an-acceptance-id",
    ),
)
def test_acceptance_record_rejects_invalid_acceptance_id(
    invalid_id: str,
) -> None:
    with pytest.raises(ValueError, match="acceptance_record_id"):
        _record(acceptance_record_id=invalid_id)


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
def test_acceptance_record_rejects_invalid_evidence_id(
    invalid_id: str,
) -> None:
    with pytest.raises(ValueError, match="evidence_id"):
        _record(evidence_id=invalid_id)


@pytest.mark.parametrize(
    "invalid_time",
    (
        datetime(2026, 7, 12, 9, 0),
        "2026-07-12T09:00:00Z",
        object(),
    ),
)
def test_acceptance_record_requires_aware_datetime(
    invalid_time: object,
) -> None:
    with pytest.raises(ValueError, match="accepted_at"):
        _record(accepted_at=invalid_time)


def test_acceptance_record_accepts_non_utc_aware_datetime() -> None:
    offset = timezone(timedelta(hours=7))
    accepted_at = FIXED_TIME.astimezone(offset)

    assert _record(accepted_at=accepted_at).accepted_at is accepted_at


@pytest.mark.parametrize(
    "diagnostics",
    (
        [],
        [_diagnostic()],
        ("not-a-diagnostic",),
        (_diagnostic(), object()),
    ),
)
def test_acceptance_record_requires_exact_diagnostic_tuple(
    diagnostics: object,
) -> None:
    with pytest.raises(ValueError, match="diagnostics"):
        _record(diagnostics=diagnostics)


def test_acceptance_record_allows_empty_diagnostic_tuple() -> None:
    assert _record(diagnostics=()).diagnostics == ()


def test_acceptance_record_module_has_no_repository_or_downstream_exports() -> None:
    import rie.domain.acceptance_record as module

    assert not hasattr(module, "EvidenceRepository")
    assert not hasattr(module, "Knowledge")
    assert not hasattr(module, "PromptCandidate")
