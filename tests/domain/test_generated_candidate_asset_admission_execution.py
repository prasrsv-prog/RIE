from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from rie.domain.generated_candidate_asset_admission_execution import (
    ADMISSION_OUTCOME_ADMITTED,
    GeneratedCandidateAssetAdmissionExecution,
)


FIXED_TIME = datetime(2026, 10, 1, 6, 0, tzinfo=timezone.utc)


def _record(**overrides):
    values = {
        "asset_admission_execution_id": "e" * 64,
        "authorization_id": "a" * 64,
        "decision_id": "d" * 64,
        "evaluation_id": "evaluation-1",
        "candidate_id": "candidate-1",
        "candidate_checksum": "b" * 64,
        "admitted_asset_reference": "asset-1",
        "execution_actor_reference": "actor-1",
        "execution_timestamp": FIXED_TIME,
        "execution_outcome": ADMISSION_OUTCOME_ADMITTED,
        "deterministic_provenance": (
            "candidate_sha256:" + "b" * 64,
            "authorization_sha256:" + "a" * 64,
            "asset_admission_execution_sha256:" + "e" * 64,
        ),
    }
    values.update(overrides)
    return GeneratedCandidateAssetAdmissionExecution(**values)


def test_record_is_immutable_and_preserves_exact_bindings():
    record = _record()
    assert record.authorization_id == "a" * 64
    assert record.decision_id == "d" * 64
    assert record.evaluation_id == "evaluation-1"
    assert record.candidate_id == "candidate-1"
    assert record.candidate_checksum == "b" * 64
    assert record.execution_outcome == "ADMITTED"
    with pytest.raises(FrozenInstanceError):
        record.execution_outcome = "OTHER"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("asset_admission_execution_id", "not-sha"),
        ("authorization_id", "not-sha"),
        ("decision_id", "not-sha"),
        ("candidate_checksum", "not-sha"),
    ],
)
def test_sha256_fields_fail_closed(field, value):
    with pytest.raises(ValueError):
        _record(**{field: value})


def test_execution_outcome_must_be_exactly_admitted():
    with pytest.raises(ValueError, match="ADMITTED"):
        _record(execution_outcome="PENDING")


def test_timezone_naive_execution_timestamp_fails_closed():
    with pytest.raises(ValueError, match="timezone-aware"):
        _record(execution_timestamp=datetime(2026, 10, 1, 6, 0))


def test_required_reference_must_be_ascii_nonempty():
    with pytest.raises(ValueError):
        _record(admitted_asset_reference="")
    with pytest.raises(ValueError):
        _record(execution_actor_reference="aktor-é")


def test_provenance_must_be_nonempty_and_unique():
    with pytest.raises(ValueError):
        _record(deterministic_provenance=())
    with pytest.raises(ValueError):
        _record(deterministic_provenance=("same", "same"))
