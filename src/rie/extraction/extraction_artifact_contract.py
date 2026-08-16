"""Immutable Gate 5 Extraction Artifact value contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Final
from dataclasses import InitVar


EXTRACTION_ARTIFACT_CONTRACT_VERSION: Final = (
    "extraction_artifact_contract_v1"
)
EXTRACTION_ARTIFACT_CANONICAL_FORMAT_VERSION: Final = (
    "extraction_artifact_canonical_json_v1"
)
EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION: Final = (
    "pdf_ingestion_orchestrator_result_contract_v1"
)

EXTRACTION_ARTIFACT_FIELD_ORDER: Final = (
    "contract_version",
    "artifact_id",
    "upstream_contract_version",
    "upstream_status",
    "job_id",
    "source_id",
    "source_path",
    "source_checksum",
    "structural_metadata",
    "page_extractions",
    "execution_report_location",
    "cleanup_completed",
)
EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER: Final = (
    "contract_version",
    "upstream_contract_version",
    "upstream_status",
    "job_id",
    "source_id",
    "source_path",
    "source_checksum",
    "structural_metadata",
    "page_extractions",
    "execution_report_location",
    "cleanup_completed",
)
EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER: Final = (
    "allowed",
    "reason",
    "fixture_id",
    "source_label",
    "fixture_path",
    "fixture_type",
    "inspection_mode",
    "inspection_status",
    "encrypted",
    "page_count",
    "inspected_page_count",
    "page_details_truncated",
    "page_details",
    "max_inspected_pages",
    "inspection_error",
    "evidence_allowed",
    "notes",
)
EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER: Final = (
    "page_index",
    "width_points",
    "height_points",
    "rotation_degrees",
    "inspection_status",
)
EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER: Final = (
    "source_path",
    "size_bytes",
    "page_number",
    "extraction_index",
    "extraction_method",
    "content",
    "warnings",
)


EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION: Final = (
    "extraction_artifact_contract_v2"
)
EXTRACTION_ARTIFACT_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER: Final = (
    "producer_operation_id",
    "producer_artifact_path",
    "producer_artifact_sha256",
    "producer_artifact_set_digest",
    "extraction_method",
)
EXTRACTION_ARTIFACT_OCR_FIELD_ORDER: Final = (
    EXTRACTION_ARTIFACT_FIELD_ORDER + ("ocr_remediation_provenance",)
)
EXTRACTION_ARTIFACT_OCR_IDENTITY_FIELD_ORDER: Final = (
    EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER + ("ocr_remediation_provenance",)
)

_LOWER_HEX = frozenset("0123456789abcdef")


class ExtractionArtifactIssueCode(Enum):
    INVALID_UPSTREAM_RESULT = "invalid_upstream_result"
    INVALID_UTF8 = "invalid_utf8"
    INVALID_JSON = "invalid_json"
    DUPLICATE_FIELD = "duplicate_field"
    MISSING_FIELD = "missing_field"
    EXTRA_FIELD = "extra_field"
    UNSUPPORTED_VERSION = "unsupported_version"
    INVALID_VALUE = "invalid_value"
    ARTIFACT_ID_MISMATCH = "artifact_id_mismatch"
    NON_CANONICAL_BYTES = "non_canonical_bytes"


_ISSUE_MESSAGES: Final = {
    ExtractionArtifactIssueCode.INVALID_UPSTREAM_RESULT:
        "upstream result is invalid.",
    ExtractionArtifactIssueCode.INVALID_UTF8:
        "artifact bytes are not valid UTF-8.",
    ExtractionArtifactIssueCode.INVALID_JSON:
        "artifact bytes are not valid JSON.",
    ExtractionArtifactIssueCode.DUPLICATE_FIELD:
        "artifact contains a duplicate field.",
    ExtractionArtifactIssueCode.MISSING_FIELD:
        "artifact is missing a required field.",
    ExtractionArtifactIssueCode.EXTRA_FIELD:
        "artifact contains an extra field.",
    ExtractionArtifactIssueCode.UNSUPPORTED_VERSION:
        "artifact contract version is unsupported.",
    ExtractionArtifactIssueCode.INVALID_VALUE:
        "artifact contains an invalid value.",
    ExtractionArtifactIssueCode.ARTIFACT_ID_MISMATCH:
        "artifact_id does not match the canonical identity payload.",
    ExtractionArtifactIssueCode.NON_CANONICAL_BYTES:
        "artifact bytes are not canonical.",
}


@dataclass(frozen=True)
class ExtractionArtifactIssue:
    code: ExtractionArtifactIssueCode
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.code, ExtractionArtifactIssueCode):
            raise TypeError(
                "code must be ExtractionArtifactIssueCode."
            )
        if not isinstance(self.message, str):
            raise TypeError("message must be a string.")
        if self.message.strip() == "":
            raise ValueError("message must be non-empty.")


class ExtractionArtifactContractError(ValueError):
    """Deterministic public Gate 5 contract failure."""

    __slots__ = ("_issue",)

    def __init__(self, issue: ExtractionArtifactIssue) -> None:
        if not isinstance(issue, ExtractionArtifactIssue):
            raise TypeError("issue must be ExtractionArtifactIssue.")
        object.__setattr__(self, "_issue", issue)
        super().__init__(issue.message)

    @property
    def issue(self) -> ExtractionArtifactIssue:
        return self._issue

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(
            "ExtractionArtifactContractError is immutable."
        )


def artifact_issue(
    code: ExtractionArtifactIssueCode,
) -> ExtractionArtifactIssue:
    if not isinstance(code, ExtractionArtifactIssueCode):
        raise TypeError("code must be ExtractionArtifactIssueCode.")
    return ExtractionArtifactIssue(code=code, message=_ISSUE_MESSAGES[code])


def raise_artifact_error(
    code: ExtractionArtifactIssueCode,
) -> None:
    raise ExtractionArtifactContractError(artifact_issue(code))


@dataclass(frozen=True)
class ExtractionArtifactStructuralPage:
    page_index: int
    width_points: float
    height_points: float
    rotation_degrees: int
    inspection_status: str

    def __post_init__(self) -> None:
        if not _is_integer(self.page_index) or self.page_index < 0:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if not _is_finite_number(self.width_points):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if not _is_finite_number(self.height_points):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if (
            not _is_integer(self.rotation_degrees)
            or self.rotation_degrees not in {0, 90, 180, 270}
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if self.inspection_status != "inspected":
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if self.width_points <= 0 or self.height_points <= 0:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )


@dataclass(frozen=True)
class ExtractionArtifactStructuralMetadata:
    allowed: bool
    reason: str
    fixture_id: str
    source_label: str
    fixture_path: str
    fixture_type: str
    inspection_mode: str
    inspection_status: str
    encrypted: bool
    page_count: int
    inspected_page_count: int
    page_details_truncated: bool
    page_details: tuple[ExtractionArtifactStructuralPage, ...]
    max_inspected_pages: int
    inspection_error: str
    evidence_allowed: bool
    notes: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "page_details",
            _freeze_typed_tuple(
                self.page_details,
                ExtractionArtifactStructuralPage,
            ),
        )

        for field_name in (
            "allowed",
            "encrypted",
            "page_details_truncated",
            "evidence_allowed",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )

        for field_name in (
            "reason",
            "fixture_id",
            "source_label",
            "fixture_path",
            "fixture_type",
            "inspection_mode",
            "inspection_status",
            "inspection_error",
            "notes",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )

        for field_name in (
            "reason",
            "fixture_id",
            "source_label",
            "fixture_path",
            "fixture_type",
            "inspection_mode",
            "inspection_status",
        ):
            if getattr(self, field_name).strip() == "":
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )

        for field_name in (
            "page_count",
            "inspected_page_count",
            "max_inspected_pages",
        ):
            value = getattr(self, field_name)
            if not _is_integer(value):
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )

        if (
            self.allowed is not True
            or self.encrypted is not False
            or self.evidence_allowed is not False
            or self.inspection_status not in {"inspected", "bounded"}
            or self.page_count < 0
            or self.inspected_page_count < 0
            or self.max_inspected_pages <= 0
            or self.inspected_page_count != len(self.page_details)
            or self.inspected_page_count > self.page_count
            or self.inspected_page_count > self.max_inspected_pages
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )

        expected_truncated = (
            self.page_count > self.max_inspected_pages
        )
        if self.page_details_truncated is not expected_truncated:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )

        expected_status = (
            "bounded" if expected_truncated else "inspected"
        )
        if self.inspection_status != expected_status:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )

        if self.inspection_error != "":
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )

        if tuple(
            page.page_index for page in self.page_details
        ) != tuple(range(len(self.page_details))):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )


@dataclass(frozen=True)
class ExtractionArtifactPageExtraction:
    source_path: str
    size_bytes: int
    page_number: int
    extraction_index: int
    extraction_method: str
    content: str
    warnings: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "warnings",
            _freeze_string_tuple(self.warnings),
        )

        for field_name in (
            "source_path",
            "extraction_method",
            "content",
        ):
            if not isinstance(getattr(self, field_name), str):
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )

        if (
            self.source_path.strip() == ""
            or self.extraction_method.strip() == ""
            or not _is_integer(self.size_bytes)
            or self.size_bytes < 0
            or not _is_integer(self.page_number)
            or self.page_number <= 0
            or not _is_integer(self.extraction_index)
            or self.extraction_index < 0
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )



@dataclass(frozen=True)
class ExtractionArtifactOcrRemediationProvenance:
    producer_operation_id: str
    producer_artifact_path: str
    producer_artifact_sha256: str
    producer_artifact_set_digest: str
    extraction_method: str

    def __post_init__(self) -> None:
        for field_name in (
            "producer_operation_id",
            "producer_artifact_path",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or value.strip() == "":
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )
        if (
            not _is_sha256(self.producer_artifact_sha256)
            or not _is_sha256(self.producer_artifact_set_digest)
            or self.extraction_method != "bounded_local_ocr"
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )


@dataclass(frozen=True)
class ExtractionArtifact:
    contract_version: str
    artifact_id: str
    upstream_contract_version: str
    upstream_status: str
    job_id: str
    source_id: str
    source_path: str
    source_checksum: str
    structural_metadata: ExtractionArtifactStructuralMetadata
    page_extractions: tuple[ExtractionArtifactPageExtraction, ...]
    execution_report_location: str
    cleanup_completed: bool
    ocr_remediation_provenance: InitVar[ExtractionArtifactOcrRemediationProvenance | None] = None

    def __post_init__(
        self,
        ocr_remediation_provenance: (
            ExtractionArtifactOcrRemediationProvenance | None
        ) = None,
    ) -> None:
        stored_ocr_remediation_provenance = self.__dict__.get(
            "ocr_remediation_provenance",
            None,
        )
        effective_ocr_remediation_provenance = (
            ocr_remediation_provenance
            if ocr_remediation_provenance is not None
            else stored_ocr_remediation_provenance
        )
        object.__setattr__(
            self,
            "ocr_remediation_provenance",
            effective_ocr_remediation_provenance,
        )
        object.__setattr__(
            self,
            "page_extractions",
            _freeze_typed_tuple(
                self.page_extractions,
                ExtractionArtifactPageExtraction,
            ),
        )

        if self.contract_version == EXTRACTION_ARTIFACT_CONTRACT_VERSION:
            if self.ocr_remediation_provenance is not None:
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )
        elif self.contract_version == EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION:
            if (
                type(self.ocr_remediation_provenance)
                is not ExtractionArtifactOcrRemediationProvenance
            ):
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )
        else:
            raise_artifact_error(
                ExtractionArtifactIssueCode.UNSUPPORTED_VERSION
            )
        if (
            self.upstream_contract_version
            != EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.UNSUPPORTED_VERSION
            )
        if self.upstream_status != "completed":
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )

        for field_name in (
            "job_id",
            "source_id",
            "source_path",
            "execution_report_location",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or value.strip() == "":
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )

        if not _is_sha256(self.artifact_id):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if not _is_sha256(self.source_checksum):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if not isinstance(
            self.structural_metadata,
            ExtractionArtifactStructuralMetadata,
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if not isinstance(self.cleanup_completed, bool):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if self.cleanup_completed is not True:
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if (
            self.structural_metadata.fixture_path
            != self.source_path
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )
        if (
            self.structural_metadata.page_count
            != len(self.page_extractions)
        ):
            raise_artifact_error(
                ExtractionArtifactIssueCode.INVALID_VALUE
            )

        expected_page_number = 1
        expected_extraction_index = 0

        for extraction in self.page_extractions:
            if (
                extraction.source_path != self.source_path
                or extraction.page_number != expected_page_number
                or extraction.extraction_index
                != expected_extraction_index
            ):
                raise_artifact_error(
                    ExtractionArtifactIssueCode.INVALID_VALUE
                )
            expected_page_number += 1
            expected_extraction_index += 1


def _freeze_typed_tuple(
    value: object,
    expected_type: type,
) -> tuple:
    if not isinstance(value, (list, tuple)):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    frozen = tuple(value)
    if any(not isinstance(item, expected_type) for item in frozen):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    return frozen


def _freeze_string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    frozen = tuple(value)
    if any(not isinstance(item, str) for item in frozen):
        raise_artifact_error(
            ExtractionArtifactIssueCode.INVALID_VALUE
        )
    return frozen


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_finite_number(value: object) -> bool:
    if isinstance(value, bool):
        return False
    return isinstance(value, (int, float)) and isfinite(value)


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in _LOWER_HEX for character in value)
    )


__all__ = (
    "EXTRACTION_ARTIFACT_CONTRACT_VERSION",
    "EXTRACTION_ARTIFACT_CANONICAL_FORMAT_VERSION",
    "EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION",
    "EXTRACTION_ARTIFACT_FIELD_ORDER",
    "EXTRACTION_ARTIFACT_IDENTITY_FIELD_ORDER",
    "EXTRACTION_ARTIFACT_STRUCTURAL_METADATA_FIELD_ORDER",
    "EXTRACTION_ARTIFACT_STRUCTURAL_PAGE_FIELD_ORDER",
    "EXTRACTION_ARTIFACT_PAGE_EXTRACTION_FIELD_ORDER",
    "ExtractionArtifactIssueCode",
    "ExtractionArtifactIssue",
    "ExtractionArtifactContractError",
    "ExtractionArtifactStructuralPage",
    "ExtractionArtifactStructuralMetadata",
    "ExtractionArtifactPageExtraction",
    "ExtractionArtifact",
    "artifact_issue",
    "raise_artifact_error",
)
