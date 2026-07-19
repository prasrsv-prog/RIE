from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
import re


CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION = (
    "controlled_source_admission_ingestion_job_contract_v1"
)
CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION = (
    "controlled_source_admission_result_contract_v1"
)
CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID = (
    "controlled_source_admission"
)
CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION = "1.0.0"
CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM = "sha256"

INGESTION_JOB_FIELD_ORDER = (
    "contract_version",
    "job_id",
    "source_id",
    "source_path",
    "expected_source_type",
    "authority_snapshot",
    "lifecycle_snapshot",
    "eligibility_snapshot",
    "source_checksum_algorithm",
    "source_checksum",
    "execution_policy_id",
    "execution_policy_version",
    "output_location",
)

INGESTION_JOB_IDENTITY_FIELD_ORDER = tuple(
    field_name
    for field_name in INGESTION_JOB_FIELD_ORDER
    if field_name != "job_id"
)

_LOWERCASE_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")


class ControlledSourceAdmissionStatus(Enum):
    ADMITTED = "admitted"
    REJECTED = "rejected"


class ControlledSourceAdmissionIssueCode(Enum):
    REGISTRY_INVALID = "registry_invalid"
    SOURCE_ID_UNKNOWN = "source_id_unknown"
    SOURCE_REVIEW_REQUIRED = "source_review_required"
    SOURCE_INELIGIBLE = "source_ineligible"
    SOURCE_TYPE_UNSUPPORTED = "source_type_unsupported"
    SOURCE_MISSING = "source_missing"
    SOURCE_NOT_FILE = "source_not_file"
    SOURCE_UNREADABLE = "source_unreadable"
    CHECKSUM_FAILED = "checksum_failed"
    OUTPUT_LOCATION_INVALID = "output_location_invalid"
    OUTPUT_COLLISION = "output_collision"
    MANIFEST_WRITE_FAILED = "manifest_write_failed"
    JOB_VALIDATION_FAILED = "job_validation_failed"


@dataclass(frozen=True)
class ControlledSourceAdmissionRequest:
    registry_path: str | Path
    source_id: str
    output_location: str | Path

    def __post_init__(self) -> None:
        _require_path_value(self.registry_path, "registry_path")
        _require_non_empty_string(self.source_id, "source_id")
        _require_path_value(self.output_location, "output_location")


@dataclass(frozen=True)
class IngestionJob:
    contract_version: str
    job_id: str
    source_id: str
    source_path: str
    expected_source_type: str
    authority_snapshot: str
    lifecycle_snapshot: str
    eligibility_snapshot: str
    source_checksum_algorithm: str
    source_checksum: str
    execution_policy_id: str
    execution_policy_version: str
    output_location: str

    def __post_init__(self) -> None:
        for field_name in INGESTION_JOB_FIELD_ORDER:
            _require_non_empty_string(
                getattr(self, field_name),
                field_name,
            )

        if self.contract_version != (
            CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION
        ):
            raise ValueError("contract_version is unsupported.")

        if _LOWERCASE_SHA256_RE.fullmatch(self.job_id) is None:
            raise ValueError(
                "job_id must contain exactly 64 lower-case "
                "hexadecimal characters."
            )

        if self.source_checksum_algorithm != (
            CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM
        ):
            raise ValueError("source_checksum_algorithm is unsupported.")

        if _LOWERCASE_SHA256_RE.fullmatch(self.source_checksum) is None:
            raise ValueError(
                "source_checksum must contain exactly 64 lower-case "
                "hexadecimal characters."
            )

        if self.execution_policy_id != (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID
        ):
            raise ValueError("execution_policy_id is unsupported.")

        if self.execution_policy_version != (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION
        ):
            raise ValueError("execution_policy_version is unsupported.")

        if self.source_path == self.output_location:
            raise ValueError(
                "source_path and output_location must differ."
            )


@dataclass(frozen=True)
class ControlledSourceAdmissionIssue:
    code: ControlledSourceAdmissionIssueCode
    message: str
    upstream_issue_code: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.code,
            ControlledSourceAdmissionIssueCode,
        ):
            raise TypeError(
                "code must be ControlledSourceAdmissionIssueCode."
            )

        _require_non_empty_string(self.message, "message")

        if self.upstream_issue_code is not None:
            _require_non_empty_string(
                self.upstream_issue_code,
                "upstream_issue_code",
            )


@dataclass(frozen=True)
class ControlledSourceAdmissionResult:
    contract_version: str
    status: ControlledSourceAdmissionStatus
    job: IngestionJob | None
    issue: ControlledSourceAdmissionIssue | None

    def __post_init__(self) -> None:
        if self.contract_version != (
            CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("contract_version is unsupported.")

        if not isinstance(
            self.status,
            ControlledSourceAdmissionStatus,
        ):
            raise TypeError(
                "status must be ControlledSourceAdmissionStatus."
            )

        if self.status is ControlledSourceAdmissionStatus.ADMITTED:
            if not isinstance(self.job, IngestionJob):
                raise ValueError(
                    "admitted result must contain one IngestionJob."
                )
            if self.issue is not None:
                raise ValueError(
                    "admitted result must not contain an issue."
                )
        else:
            if self.job is not None:
                raise ValueError(
                    "rejected result must not contain a job."
                )
            if not isinstance(
                self.issue,
                ControlledSourceAdmissionIssue,
            ):
                raise ValueError(
                    "rejected result must contain one issue."
                )


def canonical_ingestion_job_identity_bytes(
    *,
    contract_version: str,
    source_id: str,
    source_path: str,
    expected_source_type: str,
    authority_snapshot: str,
    lifecycle_snapshot: str,
    eligibility_snapshot: str,
    source_checksum_algorithm: str,
    source_checksum: str,
    execution_policy_id: str,
    execution_policy_version: str,
    output_location: str,
) -> bytes:
    payload = {
        "contract_version": contract_version,
        "source_id": source_id,
        "source_path": source_path,
        "expected_source_type": expected_source_type,
        "authority_snapshot": authority_snapshot,
        "lifecycle_snapshot": lifecycle_snapshot,
        "eligibility_snapshot": eligibility_snapshot,
        "source_checksum_algorithm": source_checksum_algorithm,
        "source_checksum": source_checksum,
        "execution_policy_id": execution_policy_id,
        "execution_policy_version": execution_policy_version,
        "output_location": output_location,
    }

    for field_name in INGESTION_JOB_IDENTITY_FIELD_ORDER:
        _require_non_empty_string(payload[field_name], field_name)

    if contract_version != CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION:
        raise ValueError("contract_version is unsupported.")

    if source_checksum_algorithm != (
        CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM
    ):
        raise ValueError("source_checksum_algorithm is unsupported.")

    if _LOWERCASE_SHA256_RE.fullmatch(source_checksum) is None:
        raise ValueError(
            "source_checksum must contain exactly 64 lower-case "
            "hexadecimal characters."
        )

    if execution_policy_id != (
        CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID
    ):
        raise ValueError("execution_policy_id is unsupported.")

    if execution_policy_version != (
        CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION
    ):
        raise ValueError("execution_policy_version is unsupported.")

    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def derive_ingestion_job_id(**identity_fields: str) -> str:
    return sha256(
        canonical_ingestion_job_identity_bytes(**identity_fields)
    ).hexdigest()


def admitted_result(
    job: IngestionJob,
) -> ControlledSourceAdmissionResult:
    return ControlledSourceAdmissionResult(
        contract_version=(
            CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION
        ),
        status=ControlledSourceAdmissionStatus.ADMITTED,
        job=job,
        issue=None,
    )


def rejected_result(
    code: ControlledSourceAdmissionIssueCode,
    message: str,
    *,
    upstream_issue_code: str | None = None,
) -> ControlledSourceAdmissionResult:
    return ControlledSourceAdmissionResult(
        contract_version=(
            CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION
        ),
        status=ControlledSourceAdmissionStatus.REJECTED,
        job=None,
        issue=ControlledSourceAdmissionIssue(
            code=code,
            message=message,
            upstream_issue_code=upstream_issue_code,
        ),
    )


def _require_non_empty_string(value: object, field_name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")

    if value.strip() == "":
        raise ValueError(f"{field_name} must be a non-empty string.")


def _require_path_value(value: object, field_name: str) -> None:
    if not isinstance(value, (str, Path)):
        raise TypeError(f"{field_name} must be a string or Path.")

    if str(value).strip() == "":
        raise ValueError(f"{field_name} must be non-empty.")


__all__ = (
    "CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION",
    "CONTROLLED_SOURCE_ADMISSION_RESULT_CONTRACT_VERSION",
    "CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID",
    "CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION",
    "CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM",
    "INGESTION_JOB_FIELD_ORDER",
    "INGESTION_JOB_IDENTITY_FIELD_ORDER",
    "ControlledSourceAdmissionStatus",
    "ControlledSourceAdmissionIssueCode",
    "ControlledSourceAdmissionRequest",
    "IngestionJob",
    "ControlledSourceAdmissionIssue",
    "ControlledSourceAdmissionResult",
    "canonical_ingestion_job_identity_bytes",
    "derive_ingestion_job_id",
    "admitted_result",
    "rejected_result",
)
