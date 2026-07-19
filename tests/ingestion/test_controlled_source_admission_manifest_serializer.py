import json
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
    INGESTION_JOB_FIELD_ORDER,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionIssueCode,
)
from rie.ingestion.controlled_source_admission_job_contract import IngestionJob
from rie.ingestion.controlled_source_admission_job_contract import (
    derive_ingestion_job_id,
)
from rie.ingestion.controlled_source_admission_manifest_serializer import (
    ControlledSourceAdmissionManifestError,
)
from rie.ingestion.controlled_source_admission_manifest_serializer import (
    ingestion_job_manifest_bytes,
)
from rie.ingestion.controlled_source_admission_manifest_serializer import (
    write_ingestion_job_manifest,
)


def _job(tmp_path, **overrides):
    values = {
        "contract_version": (
            CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION
        ),
        "source_id": "SRC-SYNTHETIC-é",
        "source_path": str((tmp_path / "source.pdf").resolve()),
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
        "output_location": str((tmp_path / "job.json").resolve()),
    }
    values.update(overrides)
    return IngestionJob(
        job_id=derive_ingestion_job_id(**values),
        **values,
    )


def test_manifest_contains_exactly_thirteen_keys_in_contract_order(tmp_path):
    payload = json.loads(
        ingestion_job_manifest_bytes(_job(tmp_path))
    )

    assert tuple(payload) == INGESTION_JOB_FIELD_ORDER
    assert len(payload) == 13


def test_manifest_uses_indent_two_and_ensure_ascii_false(tmp_path):
    manifest = ingestion_job_manifest_bytes(_job(tmp_path))

    assert b'\n  "contract_version":' in manifest
    assert "SRC-SYNTHETIC-é".encode("utf-8") in manifest
    assert b"\\u00e9" not in manifest


def test_manifest_is_utf8_without_bom(tmp_path):
    manifest = ingestion_job_manifest_bytes(_job(tmp_path))

    assert not manifest.startswith(b"\xef\xbb\xbf")
    assert manifest.decode("utf-8")


def test_manifest_is_lf_only_with_exactly_one_final_lf(tmp_path):
    manifest = ingestion_job_manifest_bytes(_job(tmp_path))

    assert b"\r" not in manifest
    assert manifest.endswith(b"\n")
    assert not manifest.endswith(b"\n\n")


def test_parent_directory_must_already_exist(tmp_path):
    output = tmp_path / "missing" / "job.json"

    with pytest.raises(
        ControlledSourceAdmissionManifestError
    ) as exc_info:
        write_ingestion_job_manifest(
            _job(tmp_path, output_location=str(output.resolve()))
        )

    assert exc_info.value.code is (
        ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID
    )
    assert not output.exists()


def test_existing_output_is_rejected_without_overwrite(tmp_path):
    output = tmp_path / "job.json"
    output.write_bytes(b"sentinel")

    with pytest.raises(
        ControlledSourceAdmissionManifestError
    ) as exc_info:
        write_ingestion_job_manifest(_job(tmp_path))

    assert exc_info.value.code is (
        ControlledSourceAdmissionIssueCode.OUTPUT_COLLISION
    )
    assert output.read_bytes() == b"sentinel"


def test_exclusive_write_once_creation_is_used(tmp_path):
    job = _job(tmp_path)
    first = write_ingestion_job_manifest(job)

    with pytest.raises(
        ControlledSourceAdmissionManifestError
    ) as exc_info:
        write_ingestion_job_manifest(job)

    assert exc_info.value.code is (
        ControlledSourceAdmissionIssueCode.OUTPUT_COLLISION
    )
    assert Path(job.output_location).read_bytes() == first


def test_written_bytes_are_readable_and_exactly_reproducible(tmp_path):
    job = _job(tmp_path)
    expected = ingestion_job_manifest_bytes(job)
    returned = write_ingestion_job_manifest(job)

    assert returned == expected
    assert Path(job.output_location).read_bytes() == expected
