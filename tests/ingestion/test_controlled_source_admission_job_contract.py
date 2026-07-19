from dataclasses import FrozenInstanceError
from dataclasses import fields
from pathlib import Path

import pytest

from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    INGESTION_JOB_FIELD_ORDER,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionIssue,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionIssueCode,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionRequest,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionResult,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionStatus,
)
from rie.ingestion.controlled_source_admission_job_contract import IngestionJob
from rie.ingestion.controlled_source_admission_job_contract import (
    canonical_ingestion_job_identity_bytes,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    derive_ingestion_job_id,
)


def _identity_fields(**overrides):
    values = {
        "contract_version": (
            CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION
        ),
        "source_id": "SRC-SYNTHETIC-001",
        "source_path": str(Path("/synthetic/source.pdf")),
        "expected_source_type": "pdf",
        "authority_snapshot": "official",
        "lifecycle_snapshot": "locked",
        "eligibility_snapshot": "eligible",
        "source_checksum_algorithm": (
            CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM
        ),
        "source_checksum": "a" * 64,
        "execution_policy_id": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID
        ),
        "execution_policy_version": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION
        ),
        "output_location": str(Path("/synthetic/job.json")),
    }
    values.update(overrides)
    return values


def _job(**overrides):
    identity = _identity_fields()
    identity.update(
        {
            key: value
            for key, value in overrides.items()
            if key != "job_id"
        }
    )
    job_id = overrides.get(
        "job_id",
        derive_ingestion_job_id(**identity),
    )
    return IngestionJob(job_id=job_id, **identity)


def test_request_dataclass_is_frozen():
    request = ControlledSourceAdmissionRequest(
        "registry.json",
        "SRC-SYNTHETIC-001",
        "job.json",
    )

    with pytest.raises(FrozenInstanceError):
        request.source_id = "changed"


def test_ingestion_job_dataclass_is_frozen():
    job = _job()

    with pytest.raises(FrozenInstanceError):
        job.job_id = "b" * 64


def test_issue_dataclass_is_frozen():
    issue = ControlledSourceAdmissionIssue(
        ControlledSourceAdmissionIssueCode.SOURCE_ID_UNKNOWN,
        "Synthetic rejection.",
    )

    with pytest.raises(FrozenInstanceError):
        issue.message = "changed"


def test_result_dataclass_is_frozen():
    result = ControlledSourceAdmissionResult(
        CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION,
        ControlledSourceAdmissionStatus.ADMITTED,
        _job(),
        None,
    )

    with pytest.raises(FrozenInstanceError):
        result.status = ControlledSourceAdmissionStatus.REJECTED


def test_status_enum_contains_only_admitted_and_rejected():
    assert [member.value for member in ControlledSourceAdmissionStatus] == [
        "admitted",
        "rejected",
    ]


def test_issue_enum_contains_exact_thirteen_codes():
    assert [
        member.value
        for member in ControlledSourceAdmissionIssueCode
    ] == [
        "registry_invalid",
        "source_id_unknown",
        "source_review_required",
        "source_ineligible",
        "source_type_unsupported",
        "source_missing",
        "source_not_file",
        "source_unreadable",
        "checksum_failed",
        "output_location_invalid",
        "output_collision",
        "manifest_write_failed",
        "job_validation_failed",
    ]


def test_ingestion_job_field_order_is_exact():
    assert tuple(field.name for field in fields(IngestionJob)) == (
        INGESTION_JOB_FIELD_ORDER
    )


def test_all_required_strings_reject_empty_values():
    with pytest.raises(ValueError):
        ControlledSourceAdmissionRequest(
            "registry.json",
            " ",
            "job.json",
        )

    for field_name in INGESTION_JOB_FIELD_ORDER:
        values = _identity_fields()
        job_id = derive_ingestion_job_id(**values)
        kwargs = {"job_id": job_id, **values}
        kwargs[field_name] = " "

        with pytest.raises(ValueError):
            IngestionJob(**kwargs)


def test_job_id_requires_lowercase_sha256_shape():
    for invalid in ("a" * 63, "A" * 64, "g" * 64):
        with pytest.raises(ValueError):
            _job(job_id=invalid)


def test_source_checksum_requires_lowercase_sha256_shape():
    for invalid in ("a" * 63, "A" * 64, "g" * 64):
        with pytest.raises(ValueError):
            _job(source_checksum=invalid)


def test_contract_and_policy_constants_reject_mismatches():
    invalid_fields = {
        "contract_version": "unsupported",
        "source_checksum_algorithm": "sha1",
        "execution_policy_id": "other",
        "execution_policy_version": "2.0.0",
    }

    for field_name, value in invalid_fields.items():
        with pytest.raises(ValueError):
            _job(**{field_name: value})

    with pytest.raises(ValueError):
        ControlledSourceAdmissionResult(
            "unsupported",
            ControlledSourceAdmissionStatus.REJECTED,
            None,
            ControlledSourceAdmissionIssue(
                ControlledSourceAdmissionIssueCode.SOURCE_ID_UNKNOWN,
                "Synthetic rejection.",
            ),
        )


def test_admitted_and_rejected_result_invariants_are_enforced():
    issue = ControlledSourceAdmissionIssue(
        ControlledSourceAdmissionIssueCode.SOURCE_ID_UNKNOWN,
        "Synthetic rejection.",
    )

    with pytest.raises(ValueError):
        ControlledSourceAdmissionResult(
            CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION,
            ControlledSourceAdmissionStatus.ADMITTED,
            None,
            None,
        )

    with pytest.raises(ValueError):
        ControlledSourceAdmissionResult(
            CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION,
            ControlledSourceAdmissionStatus.ADMITTED,
            _job(),
            issue,
        )

    with pytest.raises(ValueError):
        ControlledSourceAdmissionResult(
            CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION,
            ControlledSourceAdmissionStatus.REJECTED,
            _job(),
            issue,
        )

    with pytest.raises(ValueError):
        ControlledSourceAdmissionResult(
            CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION,
            ControlledSourceAdmissionStatus.REJECTED,
            None,
            None,
        )


def test_canonical_identity_bytes_and_job_id_are_deterministic():
    identity = _identity_fields(source_id="SRC-SYNTHETIC-é")

    first_bytes = canonical_ingestion_job_identity_bytes(**identity)
    second_bytes = canonical_ingestion_job_identity_bytes(**identity)
    first_id = derive_ingestion_job_id(**identity)
    second_id = derive_ingestion_job_id(**identity)

    assert first_bytes == second_bytes
    assert first_id == second_id
    assert len(first_id) == 64
    assert b"\n" not in first_bytes
    assert "SRC-SYNTHETIC-é".encode("utf-8") in first_bytes
