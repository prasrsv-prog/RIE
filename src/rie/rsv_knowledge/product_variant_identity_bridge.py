"""Narrow Product Variant Identity bridge for real accepted Evidence.

This module is intentionally side-effect-free. It does not persist Evidence,
query repositories, execute acceptance, promote Knowledge, or perform network
operations. Real-pilot orchestration remains separately governed.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import AcceptedEvidence
from rie.domain.knowledge_candidate import (
    INITIAL_AUTHORITY_STATUS,
    INITIAL_CONFLICT_STATUS,
    INITIAL_LIFECYCLE_STATUS,
    INITIAL_REVIEW_STATUS,
    KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
    PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE,
    KnowledgeCandidate,
    KnowledgeCandidateIdentityInput,
    KnowledgeEvidenceSupport,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)

PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION = (
    "product_variant_identity_evidence_admission_request_contract_v1"
)
PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_RESULT_CONTRACT_VERSION = (
    "product_variant_identity_evidence_admission_result_contract_v1"
)
PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION = (
    "product_variant_identity_candidate_construction_request_contract_v1"
)
PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION = (
    "product_variant_identity_candidate_construction_result_contract_v1"
)

PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE = (
    "product_variant_identity_structured_metadata"
)
PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION = "1.0.0"
PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE = "atomic_knowledge_id"
PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION = "1.0.0"

PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_ID = (
    "rcis-approved-product-variant-identity"
)
PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_VERSION = "1.0.0"

BRIDGE_STATUS_MATERIALIZED = "materialized"
BRIDGE_STATUS_CONSTRUCTED = "constructed"
BRIDGE_STATUS_REJECTED = "rejected"
BRIDGE_STATUS_SAFE_STOP = "safe_stop"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _require_non_empty_string(value: object, name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _require_digest(value: object, name: str) -> None:
    if type(value) is not str or _DIGEST.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lower-case sha256 digest")


def _require_exact_string_tuple(value: object, name: str) -> tuple[str, ...]:
    if type(value) is not tuple or not value:
        raise ValueError(f"{name} must be a non-empty tuple")
    for index, item in enumerate(value):
        _require_non_empty_string(item, f"{name}[{index}]")
    if len(set(value)) != len(value):
        raise ValueError(f"{name} must not contain duplicates")
    return value


@dataclass(frozen=True)
class ProductVariantIdentityEvidenceAdmissionUnit:
    atomic_knowledge_id: str
    knowledge_kind: str
    atomic_statement: str
    product_family: str
    product_id: str
    variant_id: str
    variant_name_verbatim: str
    source_type: str
    source_authority: str
    source_status: str
    source_version: str
    source_relative_paths: tuple[str, ...]
    manifest_sha256: str
    identity_capture_sha256: str
    atomic_construction_authority_decision_packet_sha256: str
    downstream_binding_policy_decision_packet_sha256: str

    def __post_init__(self) -> None:
        for name in (
            "atomic_knowledge_id",
            "atomic_statement",
            "product_family",
            "product_id",
            "variant_id",
            "variant_name_verbatim",
            "source_type",
            "source_authority",
            "source_status",
            "source_version",
        ):
            _require_non_empty_string(getattr(self, name), name)
        if self.knowledge_kind != "product_variant_identity":
            raise ValueError("knowledge_kind must be product_variant_identity")
        _require_exact_string_tuple(
            self.source_relative_paths,
            "source_relative_paths",
        )
        for name in (
            "manifest_sha256",
            "identity_capture_sha256",
            "atomic_construction_authority_decision_packet_sha256",
            "downstream_binding_policy_decision_packet_sha256",
        ):
            _require_digest(getattr(self, name), name)


@dataclass(frozen=True)
class ProductVariantIdentityEvidenceAdmissionRequest:
    contract_version: str
    unit: ProductVariantIdentityEvidenceAdmissionUnit
    image_content_interpretation_attempted: bool = False
    additional_semantic_inference_attempted: bool = False
    repository_write_attempted: bool = False
    network_operation_attempted: bool = False

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_REQUEST_CONTRACT_VERSION
        ):
            raise ValueError("unsupported admission request contract version")
        if type(self.unit) is not ProductVariantIdentityEvidenceAdmissionUnit:
            raise ValueError(
                "unit must be an exact ProductVariantIdentityEvidenceAdmissionUnit"
            )
        for name in (
            "image_content_interpretation_attempted",
            "additional_semantic_inference_attempted",
            "repository_write_attempted",
            "network_operation_attempted",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be a bool")


@dataclass(frozen=True)
class ProductVariantIdentityEvidenceAdmissionResult:
    contract_version: str
    status: str
    payload: tuple[tuple[str, object], ...] | None
    locator_type: str | None
    locator_value: str | None
    locator_schema_version: str | None
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported admission result contract version")
        if self.status not in (
            BRIDGE_STATUS_MATERIALIZED,
            BRIDGE_STATUS_REJECTED,
            BRIDGE_STATUS_SAFE_STOP,
        ):
            raise ValueError("invalid admission result status")
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        if self.status == BRIDGE_STATUS_MATERIALIZED:
            if type(self.payload) is not tuple or not self.payload:
                raise ValueError("materialized result requires payload")
            for value in (
                self.locator_type,
                self.locator_value,
                self.locator_schema_version,
            ):
                _require_non_empty_string(value, "locator")
            if self.reason_codes:
                raise ValueError("materialized result cannot contain reason codes")
        else:
            if any(
                value is not None
                for value in (
                    self.payload,
                    self.locator_type,
                    self.locator_value,
                    self.locator_schema_version,
                )
            ):
                raise ValueError("non-materialized result cannot contain outputs")
            if not self.reason_codes:
                raise ValueError("non-materialized result requires reason codes")


@dataclass(frozen=True)
class ProductVariantIdentityCandidateConstructionRequest:
    contract_version: str
    unit: ProductVariantIdentityEvidenceAdmissionUnit
    accepted_evidence: AcceptedEvidence
    acceptance_records: tuple[AcceptanceRecord, ...]
    construction_rule_id: str
    construction_rule_version: str
    image_content_interpretation_attempted: bool = False
    additional_semantic_inference_attempted: bool = False
    repository_write_attempted: bool = False
    network_operation_attempted: bool = False

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
        ):
            raise ValueError("unsupported candidate request contract version")
        if type(self.unit) is not ProductVariantIdentityEvidenceAdmissionUnit:
            raise ValueError(
                "unit must be an exact ProductVariantIdentityEvidenceAdmissionUnit"
            )
        if type(self.accepted_evidence) is not AcceptedEvidence:
            raise ValueError("accepted_evidence must be an exact AcceptedEvidence")
        if type(self.acceptance_records) is not tuple or not self.acceptance_records:
            raise ValueError("acceptance_records must be a non-empty tuple")
        for index, record in enumerate(self.acceptance_records):
            if type(record) is not AcceptanceRecord:
                raise ValueError(
                    f"acceptance_records[{index}] must be an exact AcceptanceRecord"
                )
        _require_non_empty_string(self.construction_rule_id, "construction_rule_id")
        _require_non_empty_string(
            self.construction_rule_version,
            "construction_rule_version",
        )
        for name in (
            "image_content_interpretation_attempted",
            "additional_semantic_inference_attempted",
            "repository_write_attempted",
            "network_operation_attempted",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be a bool")


@dataclass(frozen=True)
class ProductVariantIdentityCandidateConstructionResult:
    contract_version: str
    status: str
    knowledge_candidate: KnowledgeCandidate | None
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported candidate result contract version")
        if self.status not in (
            BRIDGE_STATUS_CONSTRUCTED,
            BRIDGE_STATUS_REJECTED,
            BRIDGE_STATUS_SAFE_STOP,
        ):
            raise ValueError("invalid candidate result status")
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        if self.status == BRIDGE_STATUS_CONSTRUCTED:
            if type(self.knowledge_candidate) is not KnowledgeCandidate:
                raise ValueError("constructed result requires KnowledgeCandidate")
            if self.reason_codes:
                raise ValueError("constructed result cannot contain reason codes")
        else:
            if self.knowledge_candidate is not None:
                raise ValueError("non-constructed result cannot contain candidate")
            if not self.reason_codes:
                raise ValueError("non-constructed result requires reason codes")


def _admission_payload(
    unit: ProductVariantIdentityEvidenceAdmissionUnit,
) -> tuple[tuple[str, object], ...]:
    return (
        (
            "atomic_construction_authority_decision_packet_sha256",
            unit.atomic_construction_authority_decision_packet_sha256,
        ),
        ("atomic_knowledge_id", unit.atomic_knowledge_id),
        ("atomic_statement", unit.atomic_statement),
        (
            "downstream_binding_policy_decision_packet_sha256",
            unit.downstream_binding_policy_decision_packet_sha256,
        ),
        ("identity_capture_sha256", unit.identity_capture_sha256),
        ("knowledge_kind", unit.knowledge_kind),
        ("manifest_sha256", unit.manifest_sha256),
        ("product_family", unit.product_family),
        ("product_id", unit.product_id),
        ("source_authority", unit.source_authority),
        ("source_relative_paths", unit.source_relative_paths),
        ("source_status", unit.source_status),
        ("source_type", unit.source_type),
        ("source_version", unit.source_version),
        ("variant_id", unit.variant_id),
        ("variant_name_verbatim", unit.variant_name_verbatim),
    )


def _admission_non_materialized(
    status: str,
    reason_code: str,
) -> ProductVariantIdentityEvidenceAdmissionResult:
    return ProductVariantIdentityEvidenceAdmissionResult(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_RESULT_CONTRACT_VERSION
        ),
        status=status,
        payload=None,
        locator_type=None,
        locator_value=None,
        locator_schema_version=None,
        reason_codes=(reason_code,),
    )


def materialize_product_variant_identity_evidence_admission(
    request: ProductVariantIdentityEvidenceAdmissionRequest,
) -> ProductVariantIdentityEvidenceAdmissionResult:
    if type(request) is not ProductVariantIdentityEvidenceAdmissionRequest:
        raise ValueError(
            "request must be an exact ProductVariantIdentityEvidenceAdmissionRequest"
        )
    if (
        request.image_content_interpretation_attempted
        or request.additional_semantic_inference_attempted
        or request.repository_write_attempted
        or request.network_operation_attempted
    ):
        return _admission_non_materialized(
            BRIDGE_STATUS_SAFE_STOP,
            "prohibited_operation_attempted",
        )
    try:
        request.unit.__post_init__()
    except ValueError:
        return _admission_non_materialized(
            BRIDGE_STATUS_REJECTED,
            "invalid_admission_unit",
        )
    return ProductVariantIdentityEvidenceAdmissionResult(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_EVIDENCE_ADMISSION_RESULT_CONTRACT_VERSION
        ),
        status=BRIDGE_STATUS_MATERIALIZED,
        payload=_admission_payload(request.unit),
        locator_type=PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE,
        locator_value=request.unit.atomic_knowledge_id,
        locator_schema_version=(
            PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION
        ),
        reason_codes=(),
    )


def _candidate_non_constructed(
    status: str,
    reason_code: str,
) -> ProductVariantIdentityCandidateConstructionResult:
    return ProductVariantIdentityCandidateConstructionResult(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ),
        status=status,
        knowledge_candidate=None,
        reason_codes=(reason_code,),
    )


def _acceptance_linkage_reason(
    accepted_evidence: AcceptedEvidence,
    records: tuple[AcceptanceRecord, ...],
) -> str | None:
    record_ids = tuple(record.acceptance_record_id for record in records)
    if len(set(record_ids)) != len(record_ids):
        return "duplicate_acceptance_record_id"
    if any(record.evidence_id != accepted_evidence.evidence_id for record in records):
        return "acceptance_record_evidence_id_mismatch"
    materialization = accepted_evidence.materialization_record
    matching = tuple(
        record
        for record in records
        if record.acceptance_record_id == materialization.acceptance_record_id
    )
    if len(matching) != 1:
        return "missing_or_ambiguous_materialization_acceptance_record"
    record = matching[0]
    if (
        record.accepted_by != materialization.accepted_by
        or record.acceptance_reason != materialization.acceptance_reason
        or record.review_record_id != materialization.review_record_id
        or record.materializer_id != materialization.materializer_id
        or record.materializer_version != materialization.materializer_version
        or record.accepted_at != materialization.materialized_at
        or record.evidence_identity_policy_id != materialization.identity_policy_id
        or record.evidence_identity_policy_version
        != materialization.identity_policy_version
    ):
        return "materialization_acceptance_mismatch"
    if any(not record.review_record_id.strip() for record in records):
        return "missing_acceptance_review_lineage"
    return None


def construct_product_variant_identity_candidate_from_real_accepted_evidence(
    request: ProductVariantIdentityCandidateConstructionRequest,
) -> ProductVariantIdentityCandidateConstructionResult:
    if type(request) is not ProductVariantIdentityCandidateConstructionRequest:
        raise ValueError(
            "request must be an exact ProductVariantIdentityCandidateConstructionRequest"
        )
    if (
        request.image_content_interpretation_attempted
        or request.additional_semantic_inference_attempted
        or request.repository_write_attempted
        or request.network_operation_attempted
    ):
        return _candidate_non_constructed(
            BRIDGE_STATUS_SAFE_STOP,
            "prohibited_operation_attempted",
        )
    if (
        request.construction_rule_id
        != PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_ID
        or request.construction_rule_version
        != PRODUCT_VARIANT_IDENTITY_CONSTRUCTION_RULE_VERSION
    ):
        return _candidate_non_constructed(
            BRIDGE_STATUS_REJECTED,
            "unsupported_construction_rule",
        )

    evidence = request.accepted_evidence
    try:
        evidence.__post_init__()
    except Exception:
        return _candidate_non_constructed(
            BRIDGE_STATUS_REJECTED,
            "invalid_accepted_evidence",
        )
    if evidence.eligibility_result.decision != "eligible":
        return _candidate_non_constructed(
            BRIDGE_STATUS_REJECTED,
            "ineligible_accepted_evidence",
        )
    payload = evidence.factual_payload
    if (
        payload.payload_type
        != PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE
        or payload.payload_schema_version
        != PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION
    ):
        return _candidate_non_constructed(
            BRIDGE_STATUS_REJECTED,
            "unsupported_variant_identity_payload_contract",
        )
    if payload.payload != _admission_payload(request.unit):
        return _candidate_non_constructed(
            BRIDGE_STATUS_REJECTED,
            "variant_identity_payload_mismatch",
        )
    if (
        payload.locator.locator_type
        != PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE
        or payload.locator.locator_value != request.unit.atomic_knowledge_id
        or payload.locator.locator_schema_version
        != PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION
    ):
        return _candidate_non_constructed(
            BRIDGE_STATUS_REJECTED,
            "variant_identity_locator_mismatch",
        )

    linkage_reason = _acceptance_linkage_reason(
        evidence,
        request.acceptance_records,
    )
    if linkage_reason is not None:
        return _candidate_non_constructed(
            BRIDGE_STATUS_REJECTED,
            linkage_reason,
        )

    record_ids = tuple(
        sorted(record.acceptance_record_id for record in request.acceptance_records)
    )
    review_ids = tuple(
        sorted({record.review_record_id for record in request.acceptance_records})
    )
    try:
        support = KnowledgeEvidenceSupport(
            evidence_id=evidence.evidence_id,
            acceptance_record_ids=record_ids,
            acceptance_review_record_ids=review_ids,
            source_id=evidence.source_snapshot.source_id,
            source_content_digest=evidence.source_snapshot.source_content_digest,
            source_authority_status=evidence.source_snapshot.authority_status,
            source_lifecycle_status=evidence.source_snapshot.lifecycle_status,
            payload_digest=evidence.factual_payload.payload_digest,
            locator_type=evidence.factual_payload.locator.locator_type,
            locator_value=evidence.factual_payload.locator.locator_value,
            locator_schema_version=(
                evidence.factual_payload.locator.locator_schema_version
            ),
        )
        identity_input = KnowledgeCandidateIdentityInput(
            candidate_contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
            statement_type=PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE,
            statement=request.unit.atomic_statement,
            construction_rule_id=request.construction_rule_id,
            construction_rule_version=request.construction_rule_version,
            support=(support,),
            authority_status=INITIAL_AUTHORITY_STATUS,
            lifecycle_status=INITIAL_LIFECYCLE_STATUS,
            review_status=INITIAL_REVIEW_STATUS,
            conflict_status=INITIAL_CONFLICT_STATUS,
        )
        candidate_id = compute_knowledge_candidate_id(identity_input)
        candidate = KnowledgeCandidate(
            knowledge_candidate_id=candidate_id,
            contract_version=KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
            statement_type=PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE,
            statement=request.unit.atomic_statement,
            support=(support,),
            construction_rule_id=request.construction_rule_id,
            construction_rule_version=request.construction_rule_version,
            authority_status=INITIAL_AUTHORITY_STATUS,
            lifecycle_status=INITIAL_LIFECYCLE_STATUS,
            review_status=INITIAL_REVIEW_STATUS,
            conflict_status=INITIAL_CONFLICT_STATUS,
            conflict_ids=(),
            diagnostics=(),
        )
    except (TypeError, ValueError):
        return _candidate_non_constructed(
            BRIDGE_STATUS_SAFE_STOP,
            "domain_construction_safe_stop",
        )
    if (
        compute_knowledge_candidate_id(
            identity_input_from_knowledge_candidate(candidate)
        )
        != candidate.knowledge_candidate_id
    ):
        return _candidate_non_constructed(
            BRIDGE_STATUS_SAFE_STOP,
            "knowledge_candidate_identity_recomputation_mismatch",
        )
    return ProductVariantIdentityCandidateConstructionResult(
        contract_version=(
            PRODUCT_VARIANT_IDENTITY_CANDIDATE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ),
        status=BRIDGE_STATUS_CONSTRUCTED,
        knowledge_candidate=candidate,
        reason_codes=(),
    )
