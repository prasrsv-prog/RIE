"""Immutable Gate 6 Evidence Materialization value contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Final
from dataclasses import InitVar


EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION: Final = (
    "evidence_materialization_result_contract_v1"
)
EVIDENCE_COLLECTION_CONTRACT_VERSION: Final = (
    "evidence_collection_contract_v1"
)
TRACEABLE_EVIDENCE_CONTRACT_VERSION: Final = (
    "traceable_evidence_contract_v1"
)
EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION: Final = (
    "evidence_eligibility_snapshot_contract_v1"
)
EVIDENCE_ELIGIBILITY_SNAPSHOT_CANONICALIZATION_VERSION: Final = (
    "evidence_eligibility_snapshot_json_v1"
)
TRACEABLE_EVIDENCE_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "traceable_evidence_identity_json_v1"
)
EVIDENCE_COLLECTION_IDENTITY_CANONICALIZATION_VERSION: Final = (
    "evidence_collection_identity_json_v1"
)
TRACEABLE_EVIDENCE_CONTENT_TYPE: Final = "page_text_utf8"
TRACEABLE_EVIDENCE_ID_PREFIX: Final = "evm1_"
EVIDENCE_COLLECTION_ID_PREFIX: Final = "evc1_"

EVIDENCE_ELIGIBILITY_FIELD_ORDER: Final = (
    "contract_version",
    "source_id",
    "source_path",
    "source_checksum",
    "source_type",
    "document_classification",
    "authority_status",
    "lifecycle_status",
    "evidence_eligibility",
    "evidence_collection_allowed",
    "requires_review",
    "reason",
    "policy_id",
    "policy_version",
    "registry_version",
)
TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER: Final = (
    "artifact_contract_version",
    "artifact_id",
    "upstream_contract_version",
    "job_id",
    "source_id",
    "source_path",
    "source_checksum",
    "page_index",
    "page_number",
    "extraction_index",
    "extraction_method",
    "extraction_status",
    "execution_report_location",
)
TRACEABLE_EVIDENCE_FIELD_ORDER: Final = (
    "contract_version",
    "evidence_id",
    "content_type",
    "content",
    "content_digest",
    "warnings",
    "provenance",
    "eligibility_snapshot_digest",
)
TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER: Final = (
    "contract_version",
    "content_type",
    "content",
    "content_digest",
    "warnings",
    "provenance",
    "eligibility_snapshot_digest",
)
EVIDENCE_COLLECTION_FIELD_ORDER: Final = (
    "contract_version",
    "collection_id",
    "artifact_contract_version",
    "artifact_id",
    "upstream_contract_version",
    "job_id",
    "source_id",
    "source_path",
    "source_checksum",
    "eligibility_snapshot",
    "evidence_items",
)
EVIDENCE_COLLECTION_IDENTITY_FIELD_ORDER: Final = (
    "contract_version",
    "artifact_contract_version",
    "artifact_id",
    "upstream_contract_version",
    "job_id",
    "source_id",
    "source_path",
    "source_checksum",
    "eligibility_snapshot",
    "evidence_items",
)
EVIDENCE_MATERIALIZATION_ISSUE_FIELD_ORDER: Final = (
    "code",
    "message",
)
EVIDENCE_MATERIALIZATION_RESULT_FIELD_ORDER: Final = (
    "contract_version",
    "status",
    "artifact_id",
    "source_id",
    "collection",
    "issue",
)


EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION: Final = (
    "evidence_collection_contract_v2"
)
EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION = "evidence_collection_contract_v3"
TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION: Final = (
    "traceable_evidence_contract_v2"
)
TRACEABLE_EVIDENCE_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER: Final = (
    "producer_operation_id",
    "producer_artifact_path",
    "producer_artifact_sha256",
    "producer_artifact_set_digest",
    "extraction_method",
)
TRACEABLE_EVIDENCE_OCR_FIELD_ORDER: Final = (
    TRACEABLE_EVIDENCE_FIELD_ORDER + ("ocr_remediation_provenance",)
)
TRACEABLE_EVIDENCE_OCR_IDENTITY_FIELD_ORDER: Final = (
    TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER + ("ocr_remediation_provenance",)
)

TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION = "traceable_evidence_contract_v3"
TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_FIELD_ORDER = (
    TRACEABLE_EVIDENCE_OCR_FIELD_ORDER
    + ("atomic_text_derivation_provenance",)
)
TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_IDENTITY_FIELD_ORDER = (
    TRACEABLE_EVIDENCE_OCR_IDENTITY_FIELD_ORDER
    + ("atomic_text_derivation_provenance",)
)
TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_PROVENANCE_FIELD_ORDER = (
    "contract_version",
    "derivation_type",
    "parent_traceable_evidence_id",
    "parent_content_digest",
    "source_span_ids",
    "operator_decision_packet_sha256",
    "atomic_statement_sha256",
)

_LOWER_HEX: Final = frozenset("0123456789abcdef")


class EvidenceMaterializationStatus(Enum):
    MATERIALIZED = "materialized"
    REJECTED = "rejected"


class EvidenceMaterializationIssueCode(Enum):
    INVALID_ARTIFACT = "invalid_artifact"
    INVALID_ELIGIBILITY_SNAPSHOT = "invalid_eligibility_snapshot"
    SOURCE_ID_MISMATCH = "source_id_mismatch"
    SOURCE_PATH_MISMATCH = "source_path_mismatch"
    SOURCE_CHECKSUM_MISMATCH = "source_checksum_mismatch"
    SOURCE_NOT_ELIGIBLE = "source_not_eligible"
    SOURCE_REQUIRES_REVIEW = "source_requires_review"
    UNSUPPORTED_VERSION = "unsupported_version"
    INVALID_VALUE = "invalid_value"
    EVIDENCE_ID_MISMATCH = "evidence_id_mismatch"
    COLLECTION_ID_MISMATCH = "collection_id_mismatch"


_ISSUE_MESSAGES: Final = {
    EvidenceMaterializationIssueCode.INVALID_ARTIFACT:
        "extraction artifact is invalid.",
    EvidenceMaterializationIssueCode.INVALID_ELIGIBILITY_SNAPSHOT:
        "evidence eligibility snapshot is invalid.",
    EvidenceMaterializationIssueCode.SOURCE_ID_MISMATCH:
        "eligibility source_id does not match the extraction artifact.",
    EvidenceMaterializationIssueCode.SOURCE_PATH_MISMATCH:
        "eligibility source_path does not match the extraction artifact.",
    EvidenceMaterializationIssueCode.SOURCE_CHECKSUM_MISMATCH:
        "eligibility source_checksum does not match the extraction artifact.",
    EvidenceMaterializationIssueCode.SOURCE_NOT_ELIGIBLE:
        "source is not eligible for evidence materialization.",
    EvidenceMaterializationIssueCode.SOURCE_REQUIRES_REVIEW:
        "source requires review before evidence materialization.",
    EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION:
        "evidence materialization contract version is unsupported.",
    EvidenceMaterializationIssueCode.INVALID_VALUE:
        "evidence materialization value is invalid.",
    EvidenceMaterializationIssueCode.EVIDENCE_ID_MISMATCH:
        "evidence_id does not match the canonical identity payload.",
    EvidenceMaterializationIssueCode.COLLECTION_ID_MISMATCH:
        "collection_id does not match the canonical identity payload.",
}


@dataclass(frozen=True)
class EvidenceMaterializationIssue:
    code: EvidenceMaterializationIssueCode
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.code, EvidenceMaterializationIssueCode):
            raise TypeError(
                "code must be EvidenceMaterializationIssueCode."
            )
        if self.message != _ISSUE_MESSAGES[self.code]:
            raise ValueError("message must match the reviewed issue code.")


class EvidenceMaterializationContractError(ValueError):
    """Deterministic public Gate 6 contract failure."""

    __slots__ = ("_issue",)

    def __init__(self, issue: EvidenceMaterializationIssue) -> None:
        if not isinstance(issue, EvidenceMaterializationIssue):
            raise TypeError(
                "issue must be EvidenceMaterializationIssue."
            )
        object.__setattr__(self, "_issue", issue)
        super().__init__(issue.message)

    @property
    def issue(self) -> EvidenceMaterializationIssue:
        return self._issue

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(
            "EvidenceMaterializationContractError is immutable."
        )


def evidence_materialization_issue(
    code: EvidenceMaterializationIssueCode,
) -> EvidenceMaterializationIssue:
    if not isinstance(code, EvidenceMaterializationIssueCode):
        raise TypeError(
            "code must be EvidenceMaterializationIssueCode."
        )
    return EvidenceMaterializationIssue(
        code=code,
        message=_ISSUE_MESSAGES[code],
    )


def raise_evidence_materialization_error(
    code: EvidenceMaterializationIssueCode,
) -> None:
    raise EvidenceMaterializationContractError(
        evidence_materialization_issue(code)
    )


def _require_string(
    value: object,
    code: EvidenceMaterializationIssueCode,
    *,
    allow_empty: bool = False,
) -> str:
    if type(value) is not str:
        raise_evidence_materialization_error(code)
    if not allow_empty and value.strip() == "":
        raise_evidence_materialization_error(code)
    return value


def _require_bool(
    value: object,
    code: EvidenceMaterializationIssueCode,
) -> bool:
    if type(value) is not bool:
        raise_evidence_materialization_error(code)
    return value


def _require_non_negative_int(
    value: object,
    code: EvidenceMaterializationIssueCode,
) -> int:
    if type(value) is not int or value < 0:
        raise_evidence_materialization_error(code)
    return value


def _require_positive_int(
    value: object,
    code: EvidenceMaterializationIssueCode,
) -> int:
    if type(value) is not int or value <= 0:
        raise_evidence_materialization_error(code)
    return value


def _is_sha256(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and all(character in _LOWER_HEX for character in value)
    )


def _is_prefixed_sha256(value: object, prefix: str) -> bool:
    return (
        type(value) is str
        and value.startswith(prefix)
        and _is_sha256(value[len(prefix):])
    )


def _freeze_warnings(value: object) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        raise_evidence_materialization_error(
            EvidenceMaterializationIssueCode.INVALID_VALUE
        )
    frozen = tuple(value)
    if any(type(item) is not str for item in frozen):
        raise_evidence_materialization_error(
            EvidenceMaterializationIssueCode.INVALID_VALUE
        )
    return frozen


@dataclass(frozen=True)
class EvidenceEligibilitySnapshot:
    contract_version: str
    source_id: str
    source_path: str
    source_checksum: str
    source_type: str
    document_classification: str
    authority_status: str
    lifecycle_status: str
    evidence_eligibility: str
    evidence_collection_allowed: bool
    requires_review: bool
    reason: str
    policy_id: str
    policy_version: str
    registry_version: str

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION
            )
        for field_name in (
            "source_id",
            "source_path",
            "source_type",
            "document_classification",
            "authority_status",
            "lifecycle_status",
            "evidence_eligibility",
            "reason",
            "policy_id",
            "policy_version",
            "registry_version",
        ):
            _require_string(
                getattr(self, field_name),
                EvidenceMaterializationIssueCode.INVALID_ELIGIBILITY_SNAPSHOT,
            )
        if not _is_sha256(self.source_checksum):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_ELIGIBILITY_SNAPSHOT
            )
        _require_bool(
            self.evidence_collection_allowed,
            EvidenceMaterializationIssueCode.INVALID_ELIGIBILITY_SNAPSHOT,
        )
        _require_bool(
            self.requires_review,
            EvidenceMaterializationIssueCode.INVALID_ELIGIBILITY_SNAPSHOT,
        )
        if self.requires_review:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.SOURCE_REQUIRES_REVIEW
            )
        if (
            self.evidence_eligibility != "eligible"
            or self.evidence_collection_allowed is not True
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.SOURCE_NOT_ELIGIBLE
            )


@dataclass(frozen=True)
class TraceableEvidenceProvenance:
    artifact_contract_version: str
    artifact_id: str
    upstream_contract_version: str
    job_id: str
    source_id: str
    source_path: str
    source_checksum: str
    page_index: int
    page_number: int
    extraction_index: int
    extraction_method: str
    extraction_status: str
    execution_report_location: str

    def __post_init__(self) -> None:
        for field_name in (
            "artifact_contract_version",
            "upstream_contract_version",
            "job_id",
            "source_id",
            "source_path",
            "extraction_method",
            "extraction_status",
            "execution_report_location",
        ):
            _require_string(
                getattr(self, field_name),
                EvidenceMaterializationIssueCode.INVALID_VALUE,
            )
        if not _is_sha256(self.artifact_id):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if not _is_sha256(self.source_checksum):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        _require_non_negative_int(
            self.page_index,
            EvidenceMaterializationIssueCode.INVALID_VALUE,
        )
        _require_positive_int(
            self.page_number,
            EvidenceMaterializationIssueCode.INVALID_VALUE,
        )
        _require_non_negative_int(
            self.extraction_index,
            EvidenceMaterializationIssueCode.INVALID_VALUE,
        )
        if self.page_index != self.extraction_index:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if self.page_number != self.page_index + 1:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if self.extraction_status != "completed":
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )



@dataclass(frozen=True)
class TraceableEvidenceOcrRemediationProvenance:
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
            _require_string(
                getattr(self, field_name),
                EvidenceMaterializationIssueCode.INVALID_VALUE,
            )
        if (
            not _is_sha256(self.producer_artifact_sha256)
            or not _is_sha256(self.producer_artifact_set_digest)
            or self.extraction_method != "bounded_local_ocr"
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )



@dataclass(frozen=True)
class TraceableEvidenceAtomicTextDerivationProvenance:
    contract_version: str
    derivation_type: str
    parent_traceable_evidence_id: str
    parent_content_digest: str
    source_span_ids: tuple[str, ...]
    operator_decision_packet_sha256: str
    atomic_statement_sha256: str

    def __post_init__(self) -> None:
        if self.contract_version != "traceable_evidence_atomic_text_derivation_provenance_v1":
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION
            )
        if self.derivation_type != "operator_approved_verbatim_atomic_text":
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if not _is_prefixed_sha256(
            self.parent_traceable_evidence_id,
            TRACEABLE_EVIDENCE_ID_PREFIX,
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        for value in (
            self.parent_content_digest,
            self.operator_decision_packet_sha256,
            self.atomic_statement_sha256,
        ):
            if not _is_sha256(value):
                raise_evidence_materialization_error(
                    EvidenceMaterializationIssueCode.INVALID_VALUE
                )
        if type(self.source_span_ids) is not tuple or not self.source_span_ids:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if len(set(self.source_span_ids)) != len(self.source_span_ids):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        for span_id in self.source_span_ids:
            if (
                type(span_id) is not str
                or not span_id.startswith("span-")
                or any(
                    ch not in "abcdefghijklmnopqrstuvwxyz0123456789-"
                    for ch in span_id
                )
            ):
                raise_evidence_materialization_error(
                    EvidenceMaterializationIssueCode.INVALID_VALUE
                )
@dataclass(frozen=True)
class TraceableEvidence:
    contract_version: str
    evidence_id: str
    content_type: str
    content: str
    content_digest: str
    warnings: tuple[str, ...]
    provenance: TraceableEvidenceProvenance
    eligibility_snapshot_digest: str
    ocr_remediation_provenance: InitVar[TraceableEvidenceOcrRemediationProvenance | None] = None
    atomic_text_derivation_provenance: InitVar[TraceableEvidenceAtomicTextDerivationProvenance | None] = None


    def __post_init__(
        self,
        ocr_remediation_provenance: (
            TraceableEvidenceOcrRemediationProvenance | None
        ) = None,
        atomic_text_derivation_provenance: (
            TraceableEvidenceAtomicTextDerivationProvenance | None
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

        stored_atomic_text_derivation_provenance = self.__dict__.get(
            "atomic_text_derivation_provenance",
            None,
        )
        effective_atomic_text_derivation_provenance = (
            atomic_text_derivation_provenance
            if atomic_text_derivation_provenance is not None
            else stored_atomic_text_derivation_provenance
        )
        object.__setattr__(
            self,
            "atomic_text_derivation_provenance",
            effective_atomic_text_derivation_provenance,
        )

        object.__setattr__(self, "warnings", _freeze_warnings(self.warnings))

        if self.contract_version == TRACEABLE_EVIDENCE_CONTRACT_VERSION:
            if (
                self.ocr_remediation_provenance is not None
                or self.atomic_text_derivation_provenance is not None
            ):
                raise_evidence_materialization_error(
                    EvidenceMaterializationIssueCode.INVALID_VALUE
                )
        elif self.contract_version == TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION:
            if (
                type(self.ocr_remediation_provenance)
                is not TraceableEvidenceOcrRemediationProvenance
                or self.atomic_text_derivation_provenance is not None
            ):
                raise_evidence_materialization_error(
                    EvidenceMaterializationIssueCode.INVALID_VALUE
                )
        elif (
            self.contract_version
            == TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
        ):
            if (
                type(self.ocr_remediation_provenance)
                is not TraceableEvidenceOcrRemediationProvenance
                or type(self.atomic_text_derivation_provenance)
                is not TraceableEvidenceAtomicTextDerivationProvenance
            ):
                raise_evidence_materialization_error(
                    EvidenceMaterializationIssueCode.INVALID_VALUE
                )
            self.atomic_text_derivation_provenance.__post_init__()
        else:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION
            )

        if not _is_prefixed_sha256(
            self.evidence_id,
            TRACEABLE_EVIDENCE_ID_PREFIX,
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if self.content_type != TRACEABLE_EVIDENCE_CONTENT_TYPE:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        _require_string(
            self.content,
            EvidenceMaterializationIssueCode.INVALID_VALUE,
            allow_empty=True,
        )
        if not _is_sha256(self.content_digest):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        expected_content_digest = hashlib.sha256(
            self.content.encode("utf-8")
        ).hexdigest()
        if self.content_digest != expected_content_digest:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if type(self.provenance) is not TraceableEvidenceProvenance:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if not _is_sha256(self.eligibility_snapshot_digest):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )

        from .evidence_materialization_canonicalization import (
            derive_traceable_evidence_id,
        )

        if self.evidence_id != derive_traceable_evidence_id(self):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.EVIDENCE_ID_MISMATCH
            )


@dataclass(frozen=True)
class EvidenceCollection:
    contract_version: str
    collection_id: str
    artifact_contract_version: str
    artifact_id: str
    upstream_contract_version: str
    job_id: str
    source_id: str
    source_path: str
    source_checksum: str
    eligibility_snapshot: EvidenceEligibilitySnapshot
    evidence_items: tuple[TraceableEvidence, ...]

    def __post_init__(self) -> None:
        if type(self.evidence_items) not in (tuple, list):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        frozen_items = tuple(self.evidence_items)
        if any(type(item) is not TraceableEvidence for item in frozen_items):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        object.__setattr__(self, "evidence_items", frozen_items)

        if self.contract_version not in (
            EVIDENCE_COLLECTION_CONTRACT_VERSION,
            EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION,
            EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION
            )
        if (
            self.contract_version in (
                EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION,
                EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
            )
            and self.artifact_contract_version != "extraction_artifact_contract_v2"
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if not _is_prefixed_sha256(
            self.collection_id,
            EVIDENCE_COLLECTION_ID_PREFIX,
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        for field_name in (
            "artifact_contract_version",
            "upstream_contract_version",
            "job_id",
            "source_id",
            "source_path",
        ):
            _require_string(
                getattr(self, field_name),
                EvidenceMaterializationIssueCode.INVALID_VALUE,
            )
        if not _is_sha256(self.artifact_id):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if not _is_sha256(self.source_checksum):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if type(self.eligibility_snapshot) is not EvidenceEligibilitySnapshot:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if (
            self.eligibility_snapshot.source_id != self.source_id
            or self.eligibility_snapshot.source_path != self.source_path
            or self.eligibility_snapshot.source_checksum != self.source_checksum
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )

        if (
            self.contract_version
            != EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
        ):
            expected_indexes = tuple(range(len(frozen_items)))
            actual_indexes = tuple(
                item.provenance.page_index for item in frozen_items
            )
            if actual_indexes != expected_indexes:
                raise_evidence_materialization_error(
                    EvidenceMaterializationIssueCode.INVALID_VALUE
                )

        for item in frozen_items:
            provenance = item.provenance
            if (
                provenance.artifact_contract_version != self.artifact_contract_version
                or provenance.artifact_id != self.artifact_id
                or provenance.upstream_contract_version != self.upstream_contract_version
                or provenance.job_id != self.job_id
                or provenance.source_id != self.source_id
                or provenance.source_path != self.source_path
                or provenance.source_checksum != self.source_checksum
            ):
                raise_evidence_materialization_error(
                    EvidenceMaterializationIssueCode.INVALID_VALUE
                )

        if self.contract_version == EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION:
            for item in frozen_items:
                if (
                    item.contract_version != TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION
                    or type(item.ocr_remediation_provenance)
                    is not TraceableEvidenceOcrRemediationProvenance
                ):
                    raise_evidence_materialization_error(
                        EvidenceMaterializationIssueCode.INVALID_VALUE
                    )
        elif (
            self.contract_version
            == EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
        ):
            for item in frozen_items:
                if (
                    item.contract_version
                    != TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
                    or type(item.ocr_remediation_provenance)
                    is not TraceableEvidenceOcrRemediationProvenance
                    or type(item.atomic_text_derivation_provenance)
                    is not TraceableEvidenceAtomicTextDerivationProvenance
                ):
                    raise_evidence_materialization_error(
                        EvidenceMaterializationIssueCode.INVALID_VALUE
                    )

        from .evidence_materialization_canonicalization import (
            derive_evidence_collection_id,
        )
        if self.collection_id != derive_evidence_collection_id(self):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.COLLECTION_ID_MISMATCH
            )


@dataclass(frozen=True)
class EvidenceMaterializationResult:
    contract_version: str
    status: EvidenceMaterializationStatus
    artifact_id: str
    source_id: str
    collection: EvidenceCollection | None
    issue: EvidenceMaterializationIssue | None

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.UNSUPPORTED_VERSION
            )
        if not isinstance(self.status, EvidenceMaterializationStatus):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if type(self.artifact_id) is not str:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if type(self.source_id) is not str:
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )
        if self.status is EvidenceMaterializationStatus.MATERIALIZED:
            if (
                type(self.collection) is not EvidenceCollection
                or self.issue is not None
                or self.artifact_id != self.collection.artifact_id
                or self.source_id != self.collection.source_id
            ):
                raise_evidence_materialization_error(
                    EvidenceMaterializationIssueCode.INVALID_VALUE
                )
            return
        if (
            self.collection is not None
            or type(self.issue) is not EvidenceMaterializationIssue
        ):
            raise_evidence_materialization_error(
                EvidenceMaterializationIssueCode.INVALID_VALUE
            )


__all__ = (
    "EVIDENCE_MATERIALIZATION_RESULT_CONTRACT_VERSION",
    "EVIDENCE_COLLECTION_CONTRACT_VERSION",
    "TRACEABLE_EVIDENCE_CONTRACT_VERSION",
    "EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION",
    "EVIDENCE_ELIGIBILITY_SNAPSHOT_CANONICALIZATION_VERSION",
    "TRACEABLE_EVIDENCE_IDENTITY_CANONICALIZATION_VERSION",
    "EVIDENCE_COLLECTION_IDENTITY_CANONICALIZATION_VERSION",
    "TRACEABLE_EVIDENCE_CONTENT_TYPE",
    "TRACEABLE_EVIDENCE_ID_PREFIX",
    "EVIDENCE_COLLECTION_ID_PREFIX",
    "EVIDENCE_ELIGIBILITY_FIELD_ORDER",
    "TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER",
    "TRACEABLE_EVIDENCE_FIELD_ORDER",
    "TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER",
    "EVIDENCE_COLLECTION_FIELD_ORDER",
    "EVIDENCE_COLLECTION_IDENTITY_FIELD_ORDER",
    "EVIDENCE_MATERIALIZATION_ISSUE_FIELD_ORDER",
    "EVIDENCE_MATERIALIZATION_RESULT_FIELD_ORDER",
    "EvidenceMaterializationStatus",
    "EvidenceMaterializationIssueCode",
    "EvidenceMaterializationIssue",
    "EvidenceMaterializationContractError",
    "EvidenceEligibilitySnapshot",
    "TraceableEvidenceProvenance",
    "TraceableEvidence",
    "EvidenceCollection",
    "EvidenceMaterializationResult",
    "evidence_materialization_issue",
    "raise_evidence_materialization_error",
)
