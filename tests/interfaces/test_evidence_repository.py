from __future__ import annotations

from dataclasses import MISSING, FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import inspect
from typing import get_type_hints

import pytest

import rie.interfaces.evidence_repository as repository_module
from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import (
    AcceptedEvidence,
    EvidenceMaterializationRecord,
)
from rie.interfaces.evidence_repository import (
    EVIDENCE_REPOSITORY_CONTRACT_VERSION,
    AcceptanceRecordListResult,
    AcceptanceRecordLookupResult,
    EvidenceLookupResult,
    EvidenceRepository,
    EvidenceWriteClassificationResult,
    EvidenceWriteRequest,
    EvidenceWriteResult,
)


EVIDENCE_DIGEST = "a" * 64
OTHER_EVIDENCE_DIGEST = "b" * 64
ACCEPTANCE_DIGEST = "c" * 64
OTHER_ACCEPTANCE_DIGEST = "d" * 64
EVIDENCE_ID = f"ev1_{EVIDENCE_DIGEST}"
OTHER_EVIDENCE_ID = f"ev1_{OTHER_EVIDENCE_DIGEST}"
ACCEPTANCE_ID = f"ar1_{ACCEPTANCE_DIGEST}"
OTHER_ACCEPTANCE_ID = f"ar1_{OTHER_ACCEPTANCE_DIGEST}"
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


def _materialization_record(
    **changes: object,
) -> EvidenceMaterializationRecord:
    values = {
        "materializer_id": "accepted-evidence-materializer",
        "materializer_version": "1.0.0",
        "materialized_at": FIXED_TIME,
        "acceptance_record_id": ACCEPTANCE_ID,
        "accepted_by": "review-service",
        "acceptance_reason": "Explicit review approval",
        "review_record_id": "review-1",
        "identity_policy_id": "rcis-evidence-identity",
        "identity_policy_version": "1.0.0",
    }
    values.update(changes)
    return EvidenceMaterializationRecord(**values)


def _accepted_evidence(
    *,
    evidence_id: str = EVIDENCE_ID,
    materialization_record: EvidenceMaterializationRecord | None = None,
) -> AcceptedEvidence:
    instance = object.__new__(AcceptedEvidence)
    object.__setattr__(instance, "evidence_id", evidence_id)
    object.__setattr__(
        instance,
        "materialization_record",
        materialization_record or _materialization_record(),
    )
    return instance


def _acceptance_record(**changes: object) -> AcceptanceRecord:
    values = {
        "acceptance_record_id": ACCEPTANCE_ID,
        "contract_version": "acceptance-record-v1",
        "evidence_id": EVIDENCE_ID,
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
        "diagnostics": (),
    }
    values.update(changes)
    return AcceptanceRecord(**values)


def _write_request(**changes: object) -> EvidenceWriteRequest:
    values = {
        "accepted_evidence": _accepted_evidence(),
        "canonical_evidence_bytes_digest": EVIDENCE_DIGEST,
        "acceptance_record": _acceptance_record(),
        "canonical_acceptance_bytes_digest": ACCEPTANCE_DIGEST,
        "repository_contract_version": "1.0.0",
        "expected_identity_policy_id": "rcis-evidence-identity",
        "expected_identity_policy_version": "1.0.0",
    }
    values.update(changes)
    return EvidenceWriteRequest(**values)


FROZEN_CONTRACTS = (
    EvidenceWriteRequest,
    EvidenceLookupResult,
    AcceptanceRecordLookupResult,
    AcceptanceRecordListResult,
    EvidenceWriteClassificationResult,
    EvidenceWriteResult,
)

CLASSIFICATIONS = (
    "new_evidence",
    "exact_replay",
    "governance_replay",
    "same_fact_new_acceptance",
    "identity_collision",
    "acceptance_collision",
    "semantic_duplicate_candidate",
    "conflicting_evidence_candidate",
    "superseding_evidence_candidate",
    "rejected",
)

WRITE_RULES = (
    ("inserted_new_evidence", "new_evidence", True),
    (
        "appended_acceptance_record",
        "same_fact_new_acceptance",
        True,
    ),
    ("unchanged_exact_replay", "exact_replay", False),
    (
        "unchanged_governance_replay",
        "governance_replay",
        False,
    ),
    (
        "rejected_identity_collision",
        "identity_collision",
        False,
    ),
    (
        "rejected_acceptance_collision",
        "acceptance_collision",
        False,
    ),
    ("rejected_invalid_request", "rejected", False),
)


def _contract_instance(contract_type: type[object]) -> object:
    if contract_type is EvidenceWriteRequest:
        return _write_request()
    if contract_type is EvidenceLookupResult:
        return EvidenceLookupResult(
            status="found",
            accepted_evidence=_accepted_evidence(),
            canonical_evidence_bytes_digest=EVIDENCE_DIGEST,
            acceptance_record_ids=(ACCEPTANCE_ID,),
            reason_codes=(),
            diagnostics=(),
        )
    if contract_type is AcceptanceRecordLookupResult:
        return AcceptanceRecordLookupResult(
            status="found",
            acceptance_record=_acceptance_record(),
            canonical_acceptance_bytes_digest=ACCEPTANCE_DIGEST,
            evidence_id=EVIDENCE_ID,
            reason_codes=(),
            diagnostics=(),
        )
    if contract_type is AcceptanceRecordListResult:
        return AcceptanceRecordListResult(
            status="found",
            evidence_id=EVIDENCE_ID,
            acceptance_records=(_acceptance_record(),),
            reason_codes=(),
            diagnostics=(),
        )
    if contract_type is EvidenceWriteClassificationResult:
        return EvidenceWriteClassificationResult(
            classification="new_evidence",
            evidence_id=EVIDENCE_ID,
            acceptance_record_id=ACCEPTANCE_ID,
            existing_evidence_digest=None,
            existing_acceptance_digest=None,
            reason_codes=(),
            diagnostics=(),
        )
    return EvidenceWriteResult(
        status="inserted_new_evidence",
        classification="new_evidence",
        evidence_id=EVIDENCE_ID,
        acceptance_record_id=ACCEPTANCE_ID,
        mutation_performed=True,
        reason_codes=(),
        diagnostics=(),
    )


@pytest.mark.parametrize("contract_type", FROZEN_CONTRACTS)
def test_repository_result_contracts_are_frozen(
    contract_type: type[object],
) -> None:
    instance = _contract_instance(contract_type)

    with pytest.raises(FrozenInstanceError):
        setattr(instance, fields(contract_type)[0].name, "changed")


@pytest.mark.parametrize("contract_type", FROZEN_CONTRACTS)
def test_repository_result_contracts_have_no_defaults(
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
            EvidenceWriteRequest,
            (
                "accepted_evidence",
                "canonical_evidence_bytes_digest",
                "acceptance_record",
                "canonical_acceptance_bytes_digest",
                "repository_contract_version",
                "expected_identity_policy_id",
                "expected_identity_policy_version",
            ),
        ),
        (
            EvidenceLookupResult,
            (
                "status",
                "accepted_evidence",
                "canonical_evidence_bytes_digest",
                "acceptance_record_ids",
                "reason_codes",
                "diagnostics",
            ),
        ),
        (
            AcceptanceRecordLookupResult,
            (
                "status",
                "acceptance_record",
                "canonical_acceptance_bytes_digest",
                "evidence_id",
                "reason_codes",
                "diagnostics",
            ),
        ),
        (
            AcceptanceRecordListResult,
            (
                "status",
                "evidence_id",
                "acceptance_records",
                "reason_codes",
                "diagnostics",
            ),
        ),
        (
            EvidenceWriteClassificationResult,
            (
                "classification",
                "evidence_id",
                "acceptance_record_id",
                "existing_evidence_digest",
                "existing_acceptance_digest",
                "reason_codes",
                "diagnostics",
            ),
        ),
        (
            EvidenceWriteResult,
            (
                "status",
                "classification",
                "evidence_id",
                "acceptance_record_id",
                "mutation_performed",
                "reason_codes",
                "diagnostics",
            ),
        ),
    ),
)
def test_repository_contracts_have_exact_fields(
    contract_type: type[object],
    expected_fields: tuple[str, ...],
) -> None:
    assert tuple(field.name for field in fields(contract_type)) == (
        expected_fields
    )


def test_repository_protocol_has_exact_method_names() -> None:
    methods = {
        name
        for name, value in EvidenceRepository.__dict__.items()
        if inspect.isfunction(value) and not name.startswith("_")
    }

    assert methods == {
        "get_evidence",
        "get_acceptance_record",
        "list_acceptance_records",
        "classify_write",
        "write",
    }


def test_repository_protocol_has_exact_return_annotations() -> None:
    expected = {
        "get_evidence": EvidenceLookupResult,
        "get_acceptance_record": AcceptanceRecordLookupResult,
        "list_acceptance_records": AcceptanceRecordListResult,
        "classify_write": EvidenceWriteClassificationResult,
        "write": EvidenceWriteResult,
    }

    for method_name, result_type in expected.items():
        hints = get_type_hints(
            getattr(EvidenceRepository, method_name)
        )
        assert hints["return"] is result_type


@pytest.mark.parametrize(
    "method_name",
    (
        "update",
        "delete",
        "replace",
        "upsert",
        "merge",
        "compact",
        "bulk_write",
    ),
)
def test_repository_protocol_excludes_forbidden_methods(
    method_name: str,
) -> None:
    assert not hasattr(EvidenceRepository, method_name)


def test_repository_contract_version_is_exact() -> None:
    assert EVIDENCE_REPOSITORY_CONTRACT_VERSION == "1.0.0"


def test_valid_write_request_preserves_explicit_contracts() -> None:
    request = _write_request()

    assert request.accepted_evidence.evidence_id == EVIDENCE_ID
    assert request.acceptance_record.acceptance_record_id == (
        ACCEPTANCE_ID
    )
    assert request.canonical_evidence_bytes_digest == EVIDENCE_DIGEST
    assert request.canonical_acceptance_bytes_digest == (
        ACCEPTANCE_DIGEST
    )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("accepted_evidence", object()),
        ("acceptance_record", object()),
    ),
)
def test_write_request_requires_exact_domain_types(
    field_name: str,
    invalid_value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _write_request(**{field_name: invalid_value})


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("canonical_evidence_bytes_digest", "A" * 64),
        ("canonical_evidence_bytes_digest", "a" * 63),
        ("canonical_acceptance_bytes_digest", "C" * 64),
        ("canonical_acceptance_bytes_digest", "c" * 63),
    ),
)
def test_write_request_rejects_invalid_digest_shapes(
    field_name: str,
    invalid_value: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _write_request(**{field_name: invalid_value})


def test_write_request_rejects_repository_version_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match="repository_contract_version",
    ):
        _write_request(repository_contract_version="2.0.0")


def test_write_request_rejects_evidence_id_mismatch() -> None:
    record = _acceptance_record(evidence_id=OTHER_EVIDENCE_ID)

    with pytest.raises(ValueError, match="evidence_id"):
        _write_request(acceptance_record=record)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("expected_identity_policy_id", "other-policy"),
        ("expected_identity_policy_version", "2.0.0"),
        (
            "acceptance_record",
            _acceptance_record(
                evidence_identity_policy_id="other-policy"
            ),
        ),
        (
            "acceptance_record",
            _acceptance_record(
                evidence_identity_policy_version="2.0.0"
            ),
        ),
    ),
)
def test_write_request_rejects_identity_policy_mismatch(
    field_name: str,
    invalid_value: object,
) -> None:
    with pytest.raises(ValueError, match="policy"):
        _write_request(**{field_name: invalid_value})


@pytest.mark.parametrize(
    ("record_changes", "materialization_changes"),
    (
        (
            {"acceptance_record_id": OTHER_ACCEPTANCE_ID},
            {"acceptance_record_id": ACCEPTANCE_ID},
        ),
        (
            {"accepted_by": "other-reviewer"},
            {},
        ),
        (
            {"acceptance_reason": "Other reason"},
            {},
        ),
        (
            {"review_record_id": "review-2"},
            {},
        ),
        (
            {"materializer_id": "other-materializer"},
            {},
        ),
        (
            {"materializer_version": "2.0.0"},
            {},
        ),
        (
            {
                "accepted_at": FIXED_TIME
                + timedelta(seconds=1)
            },
            {},
        ),
    ),
)
def test_write_request_rejects_materialization_mismatch(
    record_changes: dict[str, object],
    materialization_changes: dict[str, object],
) -> None:
    accepted = _accepted_evidence(
        materialization_record=_materialization_record(
            **materialization_changes
        )
    )
    record = _acceptance_record(**record_changes)
    acceptance_digest = record.acceptance_record_id.removeprefix(
        "ar1_"
    )

    with pytest.raises(ValueError, match="mismatch"):
        _write_request(
            accepted_evidence=accepted,
            acceptance_record=record,
            canonical_acceptance_bytes_digest=acceptance_digest,
        )


def test_evidence_lookup_found_shape_is_valid() -> None:
    result = EvidenceLookupResult(
        status="found",
        accepted_evidence=_accepted_evidence(),
        canonical_evidence_bytes_digest=EVIDENCE_DIGEST,
        acceptance_record_ids=(
            ACCEPTANCE_ID,
            OTHER_ACCEPTANCE_ID,
        ),
        reason_codes=(),
        diagnostics=("verified",),
    )

    assert result.status == "found"


@pytest.mark.parametrize("status", ("not_found", "failed"))
def test_evidence_lookup_non_found_shapes_are_valid(
    status: str,
) -> None:
    result = EvidenceLookupResult(
        status=status,
        accepted_evidence=None,
        canonical_evidence_bytes_digest=None,
        acceptance_record_ids=(),
        reason_codes=("not-found",),
        diagnostics=(),
    )

    assert result.status == status


@pytest.mark.parametrize(
    ("accepted_evidence", "digest", "record_ids"),
    (
        (None, EVIDENCE_DIGEST, (ACCEPTANCE_ID,)),
        (_accepted_evidence(), None, (ACCEPTANCE_ID,)),
        (_accepted_evidence(), EVIDENCE_DIGEST, ()),
    ),
)
def test_evidence_lookup_rejects_invalid_found_shapes(
    accepted_evidence: AcceptedEvidence | None,
    digest: str | None,
    record_ids: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError):
        EvidenceLookupResult(
            status="found",
            accepted_evidence=accepted_evidence,
            canonical_evidence_bytes_digest=digest,
            acceptance_record_ids=record_ids,
            reason_codes=(),
            diagnostics=(),
        )


@pytest.mark.parametrize(
    "record_ids",
    (
        (ACCEPTANCE_ID, ACCEPTANCE_ID),
        (OTHER_ACCEPTANCE_ID, ACCEPTANCE_ID),
        ("invalid",),
    ),
)
def test_evidence_lookup_requires_ordered_unique_valid_ids(
    record_ids: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError):
        EvidenceLookupResult(
            status="found",
            accepted_evidence=_accepted_evidence(),
            canonical_evidence_bytes_digest=EVIDENCE_DIGEST,
            acceptance_record_ids=record_ids,
            reason_codes=(),
            diagnostics=(),
        )


def test_acceptance_record_lookup_found_shape_is_valid() -> None:
    result = AcceptanceRecordLookupResult(
        status="found",
        acceptance_record=_acceptance_record(),
        canonical_acceptance_bytes_digest=ACCEPTANCE_DIGEST,
        evidence_id=EVIDENCE_ID,
        reason_codes=(),
        diagnostics=(),
    )

    assert result.acceptance_record.acceptance_record_id == (
        ACCEPTANCE_ID
    )


@pytest.mark.parametrize("status", ("not_found", "failed"))
def test_acceptance_record_lookup_non_found_shapes_are_valid(
    status: str,
) -> None:
    result = AcceptanceRecordLookupResult(
        status=status,
        acceptance_record=None,
        canonical_acceptance_bytes_digest=None,
        evidence_id=None,
        reason_codes=(),
        diagnostics=(),
    )

    assert result.status == status


@pytest.mark.parametrize(
    ("record", "digest", "evidence_id"),
    (
        (None, ACCEPTANCE_DIGEST, EVIDENCE_ID),
        (_acceptance_record(), None, EVIDENCE_ID),
        (
            _acceptance_record(),
            ACCEPTANCE_DIGEST,
            OTHER_EVIDENCE_ID,
        ),
    ),
)
def test_acceptance_record_lookup_rejects_invalid_found_shapes(
    record: AcceptanceRecord | None,
    digest: str | None,
    evidence_id: str | None,
) -> None:
    with pytest.raises(ValueError):
        AcceptanceRecordLookupResult(
            status="found",
            acceptance_record=record,
            canonical_acceptance_bytes_digest=digest,
            evidence_id=evidence_id,
            reason_codes=(),
            diagnostics=(),
        )


def test_acceptance_record_list_found_shape_is_valid() -> None:
    first = _acceptance_record()
    second = _acceptance_record(
        acceptance_record_id=OTHER_ACCEPTANCE_ID
    )

    result = AcceptanceRecordListResult(
        status="found",
        evidence_id=EVIDENCE_ID,
        acceptance_records=(first, second),
        reason_codes=(),
        diagnostics=(),
    )

    assert len(result.acceptance_records) == 2


@pytest.mark.parametrize("status", ("not_found", "failed"))
def test_acceptance_record_list_non_found_shapes_are_valid(
    status: str,
) -> None:
    result = AcceptanceRecordListResult(
        status=status,
        evidence_id=EVIDENCE_ID,
        acceptance_records=(),
        reason_codes=(),
        diagnostics=(),
    )

    assert result.status == status


@pytest.mark.parametrize(
    "records",
    (
        (),
        (_acceptance_record(), _acceptance_record()),
        (
            _acceptance_record(
                acceptance_record_id=OTHER_ACCEPTANCE_ID
            ),
            _acceptance_record(),
        ),
        (
            _acceptance_record(
                evidence_id=OTHER_EVIDENCE_ID
            ),
        ),
    ),
)
def test_acceptance_record_list_rejects_invalid_found_shapes(
    records: tuple[AcceptanceRecord, ...],
) -> None:
    with pytest.raises(ValueError):
        AcceptanceRecordListResult(
            status="found",
            evidence_id=EVIDENCE_ID,
            acceptance_records=records,
            reason_codes=(),
            diagnostics=(),
        )


@pytest.mark.parametrize("classification", CLASSIFICATIONS)
def test_write_classification_accepts_exact_tokens(
    classification: str,
) -> None:
    result = EvidenceWriteClassificationResult(
        classification=classification,
        evidence_id=EVIDENCE_ID,
        acceptance_record_id=ACCEPTANCE_ID,
        existing_evidence_digest=EVIDENCE_DIGEST,
        existing_acceptance_digest=ACCEPTANCE_DIGEST,
        reason_codes=(),
        diagnostics=(),
    )

    assert result.classification == classification


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    (
        ("classification", "unknown"),
        ("evidence_id", "invalid"),
        ("acceptance_record_id", "invalid"),
        ("existing_evidence_digest", "A" * 64),
    ),
)
def test_write_classification_rejects_invalid_values(
    field_name: str,
    invalid_value: object,
) -> None:
    values = {
        "classification": "new_evidence",
        "evidence_id": EVIDENCE_ID,
        "acceptance_record_id": ACCEPTANCE_ID,
        "existing_evidence_digest": None,
        "existing_acceptance_digest": None,
        "reason_codes": (),
        "diagnostics": (),
    }
    values[field_name] = invalid_value

    with pytest.raises(ValueError):
        EvidenceWriteClassificationResult(**values)


@pytest.mark.parametrize(
    ("status", "classification", "mutation"),
    WRITE_RULES,
)
def test_write_result_enforces_exact_status_mapping(
    status: str,
    classification: str,
    mutation: bool,
) -> None:
    result = EvidenceWriteResult(
        status=status,
        classification=classification,
        evidence_id=EVIDENCE_ID,
        acceptance_record_id=ACCEPTANCE_ID,
        mutation_performed=mutation,
        reason_codes=(),
        diagnostics=(),
    )

    assert result.status == status


@pytest.mark.parametrize("classification", CLASSIFICATIONS)
def test_failed_repository_operation_accepts_controlled_classification(
    classification: str,
) -> None:
    result = EvidenceWriteResult(
        status="failed_repository_operation",
        classification=classification,
        evidence_id=EVIDENCE_ID,
        acceptance_record_id=ACCEPTANCE_ID,
        mutation_performed=False,
        reason_codes=("operation-failed",),
        diagnostics=(),
    )

    assert result.mutation_performed is False


@pytest.mark.parametrize(
    ("status", "classification", "mutation"),
    (
        ("inserted_new_evidence", "exact_replay", True),
        ("unchanged_exact_replay", "exact_replay", True),
        (
            "failed_repository_operation",
            "rejected",
            True,
        ),
    ),
)
def test_write_result_rejects_status_mapping_mismatch(
    status: str,
    classification: str,
    mutation: bool,
) -> None:
    with pytest.raises(ValueError):
        EvidenceWriteResult(
            status=status,
            classification=classification,
            evidence_id=EVIDENCE_ID,
            acceptance_record_id=ACCEPTANCE_ID,
            mutation_performed=mutation,
            reason_codes=(),
            diagnostics=(),
        )


@pytest.mark.parametrize(
    ("contract_type", "changes"),
    (
        (
            EvidenceLookupResult,
            {"reason_codes": ["mutable"]},
        ),
        (
            AcceptanceRecordLookupResult,
            {"diagnostics": ["mutable"]},
        ),
        (
            EvidenceWriteClassificationResult,
            {"reason_codes": ("",)},
        ),
        (
            EvidenceWriteResult,
            {"diagnostics": (" ",)},
        ),
    ),
)
def test_repository_results_require_immutable_non_empty_messages(
    contract_type: type[object],
    changes: dict[str, object],
) -> None:
    instance = _contract_instance(contract_type)

    with pytest.raises(ValueError):
        replace(instance, **changes)


def test_repository_module_has_no_adapter_or_downstream_exports() -> None:
    forbidden = (
        "InMemoryEvidenceRepository",
        "FileEvidenceRepository",
        "SqlEvidenceRepository",
        "Knowledge",
        "PromptCandidate",
    )

    assert all(
        not hasattr(repository_module, name)
        for name in forbidden
    )
