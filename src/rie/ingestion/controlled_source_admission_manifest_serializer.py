from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionIssueCode,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    INGESTION_JOB_FIELD_ORDER,
)
from rie.ingestion.controlled_source_admission_job_contract import IngestionJob


@dataclass(frozen=True)
class ControlledSourceAdmissionManifestError(Exception):
    code: ControlledSourceAdmissionIssueCode
    message: str

    def __str__(self) -> str:
        return self.message


def ingestion_job_manifest_bytes(job: IngestionJob) -> bytes:
    if not isinstance(job, IngestionJob):
        raise TypeError("job must be an IngestionJob.")

    payload = {
        "contract_version": job.contract_version,
        "job_id": job.job_id,
        "source_id": job.source_id,
        "source_path": job.source_path,
        "expected_source_type": job.expected_source_type,
        "authority_snapshot": job.authority_snapshot,
        "lifecycle_snapshot": job.lifecycle_snapshot,
        "eligibility_snapshot": job.eligibility_snapshot,
        "source_checksum_algorithm": job.source_checksum_algorithm,
        "source_checksum": job.source_checksum,
        "execution_policy_id": job.execution_policy_id,
        "execution_policy_version": job.execution_policy_version,
        "output_location": job.output_location,
    }

    if tuple(payload) != INGESTION_JOB_FIELD_ORDER:
        raise RuntimeError("manifest field order is invalid.")

    return (
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def write_ingestion_job_manifest(job: IngestionJob) -> bytes:
    manifest_bytes = ingestion_job_manifest_bytes(job)
    output_path = Path(job.output_location)

    if output_path.suffix.lower() != ".json":
        raise ControlledSourceAdmissionManifestError(
            ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID,
            "Output location must be an explicit JSON file path.",
        )

    parent = output_path.parent

    if not parent.exists() or not parent.is_dir():
        raise ControlledSourceAdmissionManifestError(
            ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID,
            "Output location parent directory is invalid.",
        )

    if output_path.exists():
        raise ControlledSourceAdmissionManifestError(
            ControlledSourceAdmissionIssueCode.OUTPUT_COLLISION,
            "Output location already exists.",
        )

    try:
        with output_path.open("xb") as stream:
            stream.write(manifest_bytes)
    except FileExistsError:
        raise ControlledSourceAdmissionManifestError(
            ControlledSourceAdmissionIssueCode.OUTPUT_COLLISION,
            "Output location already exists.",
        ) from None
    except OSError:
        raise ControlledSourceAdmissionManifestError(
            ControlledSourceAdmissionIssueCode.MANIFEST_WRITE_FAILED,
            "Ingestion job manifest could not be written.",
        ) from None

    try:
        written_bytes = output_path.read_bytes()
    except OSError:
        raise ControlledSourceAdmissionManifestError(
            ControlledSourceAdmissionIssueCode.MANIFEST_WRITE_FAILED,
            "Ingestion job manifest could not be verified.",
        ) from None

    if written_bytes != manifest_bytes:
        raise ControlledSourceAdmissionManifestError(
            ControlledSourceAdmissionIssueCode.MANIFEST_WRITE_FAILED,
            "Ingestion job manifest bytes are not reproducible.",
        )

    return manifest_bytes


__all__ = (
    "ControlledSourceAdmissionManifestError",
    "ingestion_job_manifest_bytes",
    "write_ingestion_job_manifest",
)
