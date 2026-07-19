from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from official_source.official_source import EvidenceEligibility
from official_source.official_source import SourceType
from official_source.official_source_evidence_eligibility_policy import (
    OfficialSourceEvidenceEligibilityPolicy,
)
from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationRequest,
)
from official_source.official_source_registry_validation import (
    OfficialSourceRegistryValidationStatus,
)
from official_source.official_source_registry_validation import (
    validate_official_source_registry,
)
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
    ControlledSourceAdmissionIssueCode,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionRequest,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    ControlledSourceAdmissionResult,
)
from rie.ingestion.controlled_source_admission_job_contract import IngestionJob
from rie.ingestion.controlled_source_admission_job_contract import (
    admitted_result,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    derive_ingestion_job_id,
)
from rie.ingestion.controlled_source_admission_job_contract import (
    rejected_result,
)
from rie.ingestion.controlled_source_admission_manifest_serializer import (
    ControlledSourceAdmissionManifestError,
)
from rie.ingestion.controlled_source_admission_manifest_serializer import (
    write_ingestion_job_manifest,
)


_SUPPORTED_SOURCE_TYPES = frozenset(
    {
        SourceType.PDF,
        SourceType.MARKDOWN,
        SourceType.DOCX,
        SourceType.IMAGE,
        SourceType.SPREADSHEET,
    }
)
_FORBIDDEN_PATTERN_CHARACTERS = frozenset("*?[]")
_CHECKSUM_CHUNK_SIZE = 1024 * 1024


def admit_controlled_source(
    request: ControlledSourceAdmissionRequest,
) -> ControlledSourceAdmissionResult:
    if not isinstance(request, ControlledSourceAdmissionRequest):
        raise TypeError(
            "request must be ControlledSourceAdmissionRequest."
        )

    registry_raw = str(request.registry_path)
    source_id = request.source_id
    output_raw = str(request.output_location)

    if _contains_forbidden_pattern(registry_raw):
        return rejected_result(
            ControlledSourceAdmissionIssueCode.REGISTRY_INVALID,
            "Registry path contains forbidden wildcard or recursive syntax.",
        )

    if _contains_forbidden_pattern(source_id):
        return rejected_result(
            ControlledSourceAdmissionIssueCode.SOURCE_ID_UNKNOWN,
            "Source identifier contains forbidden wildcard syntax.",
        )

    if _contains_forbidden_pattern(output_raw):
        return rejected_result(
            ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID,
            "Output location contains forbidden wildcard or recursive syntax.",
        )

    registry_result = validate_official_source_registry(
        OfficialSourceRegistryValidationRequest(
            registry_path=request.registry_path,
        )
    )

    if (
        registry_result.status
        is not OfficialSourceRegistryValidationStatus.VALID
    ):
        upstream_issue_code = None

        if registry_result.issues:
            upstream_issue_code = registry_result.issues[0].code.value

        return rejected_result(
            ControlledSourceAdmissionIssueCode.REGISTRY_INVALID,
            "Official Source registry is invalid.",
            upstream_issue_code=upstream_issue_code,
        )

    source = next(
        (
            candidate
            for candidate in registry_result.sources
            if candidate.source_id == source_id
        ),
        None,
    )

    if source is None:
        return rejected_result(
            ControlledSourceAdmissionIssueCode.SOURCE_ID_UNKNOWN,
            "Source identifier is not present in the registry.",
        )

    eligibility = OfficialSourceEvidenceEligibilityPolicy.evaluate(source)

    if eligibility.requires_review:
        return rejected_result(
            ControlledSourceAdmissionIssueCode.SOURCE_REVIEW_REQUIRED,
            "Source requires manual review before admission.",
        )

    if (
        not eligibility.allowed
        or eligibility.evidence_eligibility
        in {
            EvidenceEligibility.NOT_ELIGIBLE,
            EvidenceEligibility.UNKNOWN,
        }
    ):
        return rejected_result(
            ControlledSourceAdmissionIssueCode.SOURCE_INELIGIBLE,
            "Source is not eligible for controlled admission.",
        )

    if source.source_type not in _SUPPORTED_SOURCE_TYPES:
        return rejected_result(
            ControlledSourceAdmissionIssueCode.SOURCE_TYPE_UNSUPPORTED,
            "Source type is unsupported for controlled admission.",
        )

    registry_path = Path(request.registry_path).resolve()
    source_path = Path(source.source_path)

    if not source_path.is_absolute():
        source_path = registry_path.parent / source_path

    source_path = source_path.resolve()
    output_path = Path(request.output_location).resolve()

    if not source_path.exists():
        return rejected_result(
            ControlledSourceAdmissionIssueCode.SOURCE_MISSING,
            "Selected source file does not exist.",
        )

    if not source_path.is_file():
        return rejected_result(
            ControlledSourceAdmissionIssueCode.SOURCE_NOT_FILE,
            "Selected source path is not a regular file.",
        )

    try:
        source_checksum = _calculate_source_sha256(source_path)
    except PermissionError:
        return rejected_result(
            ControlledSourceAdmissionIssueCode.SOURCE_UNREADABLE,
            "Selected source file is not readable.",
        )
    except OSError:
        return rejected_result(
            ControlledSourceAdmissionIssueCode.CHECKSUM_FAILED,
            "Selected source checksum could not be calculated.",
        )

    if output_path.suffix.lower() != ".json":
        return rejected_result(
            ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID,
            "Output location must be an explicit JSON file path.",
        )

    if not output_path.parent.exists() or not output_path.parent.is_dir():
        return rejected_result(
            ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID,
            "Output location parent directory is invalid.",
        )

    if source_path == output_path:
        return rejected_result(
            ControlledSourceAdmissionIssueCode.OUTPUT_LOCATION_INVALID,
            "Output location must differ from the source path.",
        )

    if output_path.exists():
        return rejected_result(
            ControlledSourceAdmissionIssueCode.OUTPUT_COLLISION,
            "Output location already exists.",
        )

    identity_fields = {
        "contract_version": (
            CONTROLLED_SOURCE_ADMISSION_JOB_CONTRACT_VERSION
        ),
        "source_id": source.source_id,
        "source_path": str(source_path),
        "expected_source_type": source.source_type.value,
        "authority_snapshot": source.authority_status.value,
        "lifecycle_snapshot": source.lifecycle_status.value,
        "eligibility_snapshot": source.evidence_eligibility.value,
        "source_checksum_algorithm": (
            CONTROLLED_SOURCE_ADMISSION_CHECKSUM_ALGORITHM
        ),
        "source_checksum": source_checksum,
        "execution_policy_id": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_ID
        ),
        "execution_policy_version": (
            CONTROLLED_SOURCE_ADMISSION_EXECUTION_POLICY_VERSION
        ),
        "output_location": str(output_path),
    }

    try:
        job_id = derive_ingestion_job_id(**identity_fields)
        job = IngestionJob(
            job_id=job_id,
            **identity_fields,
        )
    except (TypeError, ValueError):
        return rejected_result(
            ControlledSourceAdmissionIssueCode.JOB_VALIDATION_FAILED,
            "Ingestion job validation failed.",
        )

    try:
        write_ingestion_job_manifest(job)
    except ControlledSourceAdmissionManifestError as exc:
        return rejected_result(
            exc.code,
            exc.message,
        )

    return admitted_result(job)


def _contains_forbidden_pattern(value: str) -> bool:
    return (
        "**" in value
        or any(
            character in value
            for character in _FORBIDDEN_PATTERN_CHARACTERS
        )
    )


def _calculate_source_sha256(source_path: Path) -> str:
    digest = sha256()

    with source_path.open("rb") as stream:
        while True:
            chunk = stream.read(_CHECKSUM_CHUNK_SIZE)

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


__all__ = (
    "admit_controlled_source",
)
