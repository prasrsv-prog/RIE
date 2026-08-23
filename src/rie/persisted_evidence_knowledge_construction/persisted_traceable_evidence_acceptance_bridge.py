"""Minimum persisted TraceableEvidence v3 acceptance compatibility bridge.

This module is intentionally narrow. It projects only persisted, already-validated
TraceableEvidence v3 / repository state plus explicit caller-supplied acceptance
metadata into the legacy AcceptedEvidence + AcceptanceRecord contracts required by
the existing persisted-evidence knowledge-construction runtime.

It does not persist, infer semantic decisions, reuse test fixtures, or invent
operator metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
import hashlib
import json
from typing import Final

from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record,
    calculate_acceptance_identity,
)
from rie.domain.acceptance_record import AcceptanceRecord
from rie.domain.accepted_evidence import (
    AcceptedEligibilityResult,
    AcceptedEvidence,
    EvidenceCandidateReference,
    EvidenceLocator,
    EvidenceMaterializationRecord,
    EvidencePayload,
    EvidenceProducerSnapshot,
    EvidenceProvenance,
    EvidenceSourceSnapshot,
)
from rie.domain.evidence_identity import (
    EVIDENCE_IDENTITY_POLICY_ID,
    EVIDENCE_IDENTITY_POLICY_VERSION,
    calculate_evidence_identity,
    identity_input_from_accepted_evidence,
)
from rie.evidence_materialization.atomic_text_evidence_derivation import (
    ATOMIC_TEXT_DERIVATION_PROVENANCE_CONTRACT_VERSION,
    ATOMIC_TEXT_DERIVATION_TYPE,
)
from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_eligibility_snapshot_digest,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION,
    TraceableEvidence,
    TraceableEvidenceAtomicTextDerivationProvenance,
    TraceableEvidenceStructuredMetadataProvenance,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
    calculate_evidence_repository_audit_id,
    calculate_evidence_repository_revision_id,
)
from rie.evidence_repository.evidence_repository_contract import (
    EvidenceRepositoryLookupResult,
)
from rie.rsv_knowledge.product_variant_identity_bridge import (
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION,
    PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE,
)


PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_REQUEST_CONTRACT_VERSION: Final = (
    "persisted_traceable_evidence_acceptance_bridge_request_contract_v1"
)
PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION: Final = (
    "persisted_traceable_evidence_acceptance_bridge_result_contract_v1"
)
PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_ID: Final = (
    "rcis-persisted-traceable-evidence-acceptance-compatibility"
)
PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_VERSION: Final = "1.0.0"

PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS: Final = frozenset(
    {
        "evm1_a3e18a4f76968b308e10cf1f0c9de37f709336e6a0f0c2b25515cd98e9d88499",
        "evm1_0bab2e3d3f2ef04b39660d287c7479ce5967027ecf8fb61092b1a72a533db1d0",
        "evm1_32f14d29ef3880b87a658962bdbe6b63c361e6c6c8c2ce6c8d13669948f6c3eb",
        "evm1_57f2bd478bb59f16aa6cd2114d70fdef7e70ddbfb7dd317e166946cd539e6607",
        "evm1_1d00dc2e1cb02e5d1b6510f8e1598ff2c9bcd1df3b6df21b38725e5437536c94",
    }
)
PILOT_FFS21_CORRECTED_L_ATOMIC_EVIDENCE_ID: Final = (
    "evm1_2abb90e9e4c753e5e857e91e2c894480df51a701d00f7489d1e19769f64afe86"
)
PILOT_FFS21_APPROVED_ATOMIC_EVIDENCE_IDS: Final = (
    PILOT_FFS21_FIVE_CLEAN_ATOMIC_EVIDENCE_IDS
    | frozenset({PILOT_FFS21_CORRECTED_L_ATOMIC_EVIDENCE_ID})
)
PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS: Final = frozenset(
    {
        "evm1_009c6c903d897e9bd67bef3852e947cb5d5f66ac21672c44ebb30227e3a4c202",
        "evm1_0ad37b5cd8765d292143f98a31a0dcb7b31dced09b7c13e19f4eecd358f784de",
        "evm1_24cd78892b74ca07a87a5e04b141ae056c7c7b287f04367d5fc5fd9afa9a7b26",
        "evm1_2ada2177e9ad3b79e0dca72cc9e4e85fefed8dd713771d20fdf1fea747ad2eb2",
        "evm1_2e10a2610d2e3d07dcfbebcd5baa28ccb7792981beb72643de50e52714ce484a",
        "evm1_2e350a8d1b61ce11ad4d4b25218a0ae5ab8de8f524a9037611cafa0a8c988e6e",
        "evm1_3353406b885d205d9fd0dce93022e93e37a8a805e10df089722f847f6259e8f7",
        "evm1_54956c4f8205ae61a73c041cf75c7237ae593f2249351cfe0de1d2fa4ae50f2e",
        "evm1_6daf9d7af75892b728a8c5fa57b6be68b45327aaccb3a1e0664dd96cd4732bf9",
        "evm1_8088836878d452f73aff7c26ba36b66683144576c3ca804297f361a0449382c1",
        "evm1_95c87a9869239eba36478468f77aa14e1c4f32a228992017b861bbbfe7f0c5a9",
        "evm1_bdd92e5807c49621bde8390393dff1d84d8034dc36516cf8a35b1320c66189dd",
        "evm1_c0275e89aa2619b80cb6a7a2489e8871e9e2199010d1eda8d705645fbfc9a2d4",
        "evm1_cbe10029707a5ae58e0e2211c2c92de3f8f46dffcf1df98564412d50195b1b96",
        "evm1_dd86d5b43d2d0d32e20e60a161f80a09a5f053e1d02e2de4a91b45361c7ae193",
        "evm1_e20d39d207e4d133741c8ce091b43e27e1d3215d2cf6c00ed62049f42529505a",
        "evm1_e5080797d36e0bfd898225ffcc7345a50c3ff092be0f741220ba1c0912e88069",
        "evm1_ee617df3d287341953b5e40556122f0a648b64dacd52dfdf402de489b1003217",
    }
)
PILOT_PRODUCT_VARIANT_STRUCTURED_ACCEPTANCE_REASON: Final = (
    "explicit_operator_approved_structured_product_variant_identity_exact18_canonical_evidence"
)
PILOT_PRODUCT_VARIANT_STRUCTURED_REVIEW_RECORD_ID: Final = (
    "operator-decision-packet:pilot-phase-a-structured-product-variant-canonical-evidence-repository-write-and-acceptance-lineage-explicit-operator-decision-fe-c1.json:sha256:0751e89c18a74cae63041620bd1a302c1e05068517fcef7774404a435eb6e9ff"
)

PILOT_FFS21_PRIMARY_OPERATOR: Final = (
    "rcis-rsv-real-asset-pilot-primary-operator"
)
PILOT_FFS21_ACCEPTANCE_REASON: Final = (
    "explicit_operator_approved_five_clean_ffs21_atomic_facts"
)
PILOT_FFS21_CORRECTED_L_ACCEPTANCE_REASON: Final = (
    "explicit_operator_approved_corrected_l_ffs21_atomic_fact"
)
PILOT_FFS21_ACCEPTANCE_POLICY_ID: Final = (
    "rcis-explicit-operator-atomic-evidence-acceptance"
)
PILOT_FFS21_ACCEPTANCE_POLICY_VERSION: Final = "1.0.0"
PILOT_FFS21_MATERIALIZER_ID: Final = "accepted-evidence-materializer"
PILOT_FFS21_MATERIALIZER_VERSION: Final = "1.0.0"

ACCEPTED_EVIDENCE_CONTRACT_VERSION: Final = "accepted-evidence-v1"
ACCEPTANCE_RECORD_CONTRACT_VERSION: Final = "acceptance-record-v1"

BRIDGE_STATUS_MATERIALIZED: Final = "materialized"
BRIDGE_STATUS_REJECTED: Final = "rejected"

_PLACEHOLDER_EVIDENCE_ID: Final = "ev1_" + ("0" * 64)
_PLACEHOLDER_ACCEPTANCE_RECORD_ID: Final = "ar1_" + ("0" * 64)


def _require_non_empty_string(value: object, field_name: str) -> None:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_aware_datetime(value: object, field_name: str) -> None:
    if type(value) is not datetime:
        raise ValueError(f"{field_name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True)
class PersistedTraceableEvidenceAcceptanceBridgeRequest:
    contract_version: str
    repository_lookup_result: EvidenceRepositoryLookupResult
    target_traceable_evidence_id: str
    accepted_by: str
    acceptance_reason: str
    review_record_id: str
    accepted_at: datetime
    acceptance_policy_id: str
    acceptance_policy_version: str
    materializer_id: str
    materializer_version: str
    eligibility_evaluated_by: str
    eligibility_evaluated_at: datetime
    provenance_observed_at: datetime
    compatibility_policy_id: str
    compatibility_policy_version: str

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_REQUEST_CONTRACT_VERSION
        ):
            raise ValueError("unsupported bridge request contract version")
        if type(self.repository_lookup_result) is not EvidenceRepositoryLookupResult:
            raise TypeError(
                "repository_lookup_result must be exact EvidenceRepositoryLookupResult"
            )
        for field_name in (
            "target_traceable_evidence_id",
            "accepted_by",
            "acceptance_reason",
            "review_record_id",
            "acceptance_policy_id",
            "acceptance_policy_version",
            "materializer_id",
            "materializer_version",
            "eligibility_evaluated_by",
            "compatibility_policy_id",
            "compatibility_policy_version",
        ):
            _require_non_empty_string(getattr(self, field_name), field_name)
        for field_name in (
            "accepted_at",
            "eligibility_evaluated_at",
            "provenance_observed_at",
        ):
            _require_aware_datetime(getattr(self, field_name), field_name)
        if (
            self.compatibility_policy_id
            != PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_ID
            or self.compatibility_policy_version
            != PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_POLICY_VERSION
        ):
            raise ValueError("unsupported bridge compatibility policy")
        if self.accepted_by != PILOT_FFS21_PRIMARY_OPERATOR:
            raise ValueError("accepted_by is outside approved pilot authority")
        if (
            self.target_traceable_evidence_id
            in PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS
        ):
            expected_acceptance_reason = (
                PILOT_PRODUCT_VARIANT_STRUCTURED_ACCEPTANCE_REASON
            )
        elif (
            self.target_traceable_evidence_id
            == PILOT_FFS21_CORRECTED_L_ATOMIC_EVIDENCE_ID
        ):
            expected_acceptance_reason = PILOT_FFS21_CORRECTED_L_ACCEPTANCE_REASON
        else:
            expected_acceptance_reason = PILOT_FFS21_ACCEPTANCE_REASON
        if self.acceptance_reason != expected_acceptance_reason:
            raise ValueError("acceptance_reason is outside approved pilot authority")
        if (
            self.target_traceable_evidence_id
            in PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS
            and self.review_record_id
            != PILOT_PRODUCT_VARIANT_STRUCTURED_REVIEW_RECORD_ID
        ):
            raise ValueError(
                "review_record_id is outside approved structured pilot authority"
            )
        if self.acceptance_policy_id != PILOT_FFS21_ACCEPTANCE_POLICY_ID:
            raise ValueError("unsupported approved acceptance policy")
        if (
            self.acceptance_policy_version
            != PILOT_FFS21_ACCEPTANCE_POLICY_VERSION
        ):
            raise ValueError("unsupported approved acceptance policy version")
        if self.materializer_id != PILOT_FFS21_MATERIALIZER_ID:
            raise ValueError("materializer_id is outside approved pilot authority")
        if self.materializer_version != PILOT_FFS21_MATERIALIZER_VERSION:
            raise ValueError("materializer_version is outside approved pilot authority")
        if self.eligibility_evaluated_by != PILOT_FFS21_PRIMARY_OPERATOR:
            raise ValueError(
                "eligibility_evaluated_by is outside approved pilot authority"
            )
        if self.eligibility_evaluated_at != self.accepted_at:
            raise ValueError(
                "eligibility_evaluated_at must equal the approved operation timestamp"
            )
        if self.provenance_observed_at != self.accepted_at:
            raise ValueError(
                "provenance_observed_at must equal the approved operation timestamp"
            )


@dataclass(frozen=True)
class PersistedTraceableEvidenceAcceptanceBridgeResult:
    contract_version: str
    status: str
    target_traceable_evidence_id: str
    accepted_evidence: AcceptedEvidence | None
    acceptance_record: AcceptanceRecord | None
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.contract_version
            != PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION
        ):
            raise ValueError("unsupported bridge result contract version")
        if self.status not in (BRIDGE_STATUS_MATERIALIZED, BRIDGE_STATUS_REJECTED):
            raise ValueError("bridge status is invalid")
        _require_non_empty_string(
            self.target_traceable_evidence_id,
            "target_traceable_evidence_id",
        )
        if type(self.reason_codes) is not tuple:
            raise ValueError("reason_codes must be a tuple")
        if self.status == BRIDGE_STATUS_MATERIALIZED:
            if type(self.accepted_evidence) is not AcceptedEvidence:
                raise TypeError("materialized bridge result requires AcceptedEvidence")
            if type(self.acceptance_record) is not AcceptanceRecord:
                raise TypeError("materialized bridge result requires AcceptanceRecord")
            if self.reason_codes:
                raise ValueError("materialized bridge result cannot contain reason codes")
        else:
            if self.accepted_evidence is not None or self.acceptance_record is not None:
                raise ValueError("rejected bridge result cannot contain outputs")
            if not self.reason_codes:
                raise ValueError("rejected bridge result requires a reason code")
        for index, code in enumerate(self.reason_codes):
            _require_non_empty_string(code, f"reason_codes[{index}]")


def _rejected(
    target_traceable_evidence_id: str,
    reason_code: str,
) -> PersistedTraceableEvidenceAcceptanceBridgeResult:
    return PersistedTraceableEvidenceAcceptanceBridgeResult(
        contract_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION
        ),
        status=BRIDGE_STATUS_REJECTED,
        target_traceable_evidence_id=target_traceable_evidence_id,
        accepted_evidence=None,
        acceptance_record=None,
        reason_codes=(reason_code,),
    )


def _validate_persisted_lookup(
    lookup: EvidenceRepositoryLookupResult,
) -> str | None:
    try:
        lookup.__post_init__()
    except Exception:
        return "invalid_repository_lookup_result"
    if lookup.status != "found":
        return "repository_lookup_not_found_or_rejected"

    revision = lookup.revision
    audit = lookup.audit_record
    collection = lookup.collection
    if revision is None or audit is None or collection is None:
        return "invalid_repository_lookup_result"

    try:
        revision.__post_init__()
        audit.__post_init__()
        collection.__post_init__()
    except Exception:
        return "invalid_persisted_repository_state"

    expected_payload_digest = (
        calculate_evidence_collection_repository_payload_digest(collection)
    )
    if revision.collection_payload_digest != expected_payload_digest:
        return "collection_payload_digest_mismatch"
    if (
        revision.collection_id != collection.collection_id
        or revision.source_id != collection.source_id
        or audit.revision_id != revision.revision_id
        or audit.source_id != revision.source_id
        or audit.revision_number != revision.revision_number
        or audit.collection_id != revision.collection_id
        or audit.actor_id != revision.actor_id
        or audit.recorded_at_utc != revision.recorded_at_utc
        or revision.audit_id != audit.audit_id
    ):
        return "repository_linkage_mismatch"

    expected_revision_id = calculate_evidence_repository_revision_id(
        source_id=revision.source_id,
        revision_number=revision.revision_number,
        collection_id=revision.collection_id,
        collection_payload_digest=revision.collection_payload_digest,
        previous_revision_id=revision.previous_revision_id,
    )
    if expected_revision_id != revision.revision_id:
        return "repository_revision_identity_mismatch"

    expected_audit_id = calculate_evidence_repository_audit_id(
        action=audit.action,
        revision_id=audit.revision_id,
        source_id=audit.source_id,
        revision_number=audit.revision_number,
        collection_id=audit.collection_id,
        actor_id=audit.actor_id,
        recorded_at_utc=audit.recorded_at_utc,
    )
    if expected_audit_id != audit.audit_id:
        return "repository_audit_identity_mismatch"
    return None



_STRUCTURED_PRODUCT_VARIANT_PAYLOAD_KEYS: Final = (
    "atomic_construction_authority_decision_packet_sha256",
    "atomic_knowledge_id",
    "atomic_statement",
    "downstream_binding_policy_decision_packet_sha256",
    "identity_capture_sha256",
    "knowledge_kind",
    "manifest_sha256",
    "product_family",
    "product_id",
    "source_authority",
    "source_relative_paths",
    "source_status",
    "source_type",
    "source_version",
    "variant_id",
    "variant_name_verbatim",
)


def _materialize_structured_product_variant_acceptance(
    request: PersistedTraceableEvidenceAcceptanceBridgeRequest,
) -> PersistedTraceableEvidenceAcceptanceBridgeResult:
    lookup = request.repository_lookup_result
    lookup_issue = _validate_persisted_lookup(lookup)
    if lookup_issue is not None:
        return _rejected(request.target_traceable_evidence_id, lookup_issue)

    collection = lookup.collection
    assert collection is not None
    if (
        collection.contract_version
        != EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "unsupported_structured_collection_contract_version",
        )

    matches = tuple(
        item
        for item in collection.evidence_items
        if item.evidence_id == request.target_traceable_evidence_id
    )
    if len(matches) != 1:
        return _rejected(
            request.target_traceable_evidence_id,
            "target_traceable_evidence_not_found_or_not_unique",
        )
    target = matches[0]
    try:
        target.__post_init__()
    except Exception:
        return _rejected(
            request.target_traceable_evidence_id,
            "invalid_target_traceable_evidence",
        )
    if (
        target.contract_version
        != TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION
        or target.content_type
        != TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "target_traceable_evidence_not_v4_structured_metadata",
        )

    structured = target.provenance
    if type(structured) is not TraceableEvidenceStructuredMetadataProvenance:
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_metadata_provenance_missing",
        )
    try:
        structured.__post_init__()
    except Exception:
        return _rejected(
            request.target_traceable_evidence_id,
            "invalid_structured_metadata_provenance",
        )
    if (
        structured.contract_version
        != TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION
        or structured.payload_type
        != PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_TYPE
        or structured.payload_schema_version
        != PRODUCT_VARIANT_IDENTITY_EVIDENCE_PAYLOAD_SCHEMA_VERSION
        or structured.locator_type
        != PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_TYPE
        or structured.locator_schema_version
        != PRODUCT_VARIANT_IDENTITY_EVIDENCE_LOCATOR_SCHEMA_VERSION
        or structured.locator_value != structured.atomic_knowledge_id
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_metadata_provenance_contract_mismatch",
        )

    if (
        hashlib.sha256(target.content.encode("utf-8")).hexdigest()
        != target.content_digest
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_content_digest_mismatch",
        )
    if structured.admission_payload_digest != target.content_digest:
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_admission_payload_digest_mismatch",
        )

    try:
        payload_object = json.loads(target.content)
    except (TypeError, ValueError, json.JSONDecodeError):
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_content_json_invalid",
        )
    if (
        type(payload_object) is not dict
        or tuple(sorted(payload_object))
        != _STRUCTURED_PRODUCT_VARIANT_PAYLOAD_KEYS
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_payload_keys_mismatch",
        )
    canonical_content = (
        json.dumps(
            payload_object,
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )
    if canonical_content != target.content:
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_content_not_canonical",
        )

    source_relative_paths = payload_object["source_relative_paths"]
    if (
        type(source_relative_paths) is not list
        or not source_relative_paths
        or any(
            type(item) is not str or not item.strip()
            for item in source_relative_paths
        )
        or len(source_relative_paths) != len(set(source_relative_paths))
        or tuple(source_relative_paths) != structured.source_relative_paths
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_source_relative_paths_mismatch",
        )
    provenance_payload_pairs = (
        ("atomic_knowledge_id", structured.atomic_knowledge_id),
        ("manifest_sha256", structured.manifest_sha256),
        ("identity_capture_sha256", structured.identity_capture_sha256),
        (
            "atomic_construction_authority_decision_packet_sha256",
            structured.atomic_construction_authority_decision_packet_sha256,
        ),
        (
            "downstream_binding_policy_decision_packet_sha256",
            structured.downstream_binding_policy_decision_packet_sha256,
        ),
    )
    if any(
        payload_object[key] != expected
        for key, expected in provenance_payload_pairs
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_payload_provenance_mismatch",
        )

    snapshot = collection.eligibility_snapshot
    try:
        snapshot.__post_init__()
    except Exception:
        return _rejected(
            request.target_traceable_evidence_id,
            "invalid_eligibility_snapshot",
        )
    if (
        target.eligibility_snapshot_digest
        != derive_evidence_eligibility_snapshot_digest(snapshot)
        or snapshot.evidence_eligibility != "eligible"
        or snapshot.evidence_collection_allowed is not True
        or snapshot.requires_review is not False
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "structured_eligibility_snapshot_mismatch",
        )

    factual_pairs = tuple(
        (
            key,
            tuple(value) if key == "source_relative_paths" else value,
        )
        for key, value in sorted(payload_object.items())
    )
    candidate_reference = EvidenceCandidateReference(
        candidate_contract_version=target.contract_version,
        candidate_snapshot_digest=target.content_digest,
        candidate_source_id=collection.source_id,
        candidate_producer_name=structured.payload_type,
        candidate_producer_version=structured.payload_schema_version,
        candidate_payload_digest=target.content_digest,
    )
    source_snapshot = EvidenceSourceSnapshot(
        source_id=collection.source_id,
        source_path=collection.source_path,
        source_type=snapshot.source_type,
        document_classification=snapshot.document_classification,
        authority_status=snapshot.authority_status,
        lifecycle_status=snapshot.lifecycle_status,
        evidence_eligibility=snapshot.evidence_eligibility,
        source_content_digest=collection.source_checksum,
    )
    producer_snapshot = EvidenceProducerSnapshot(
        producer_name=structured.payload_type,
        producer_version=structured.payload_schema_version,
        producer_kind=target.content_type,
        producer_contract_version=structured.contract_version,
    )
    factual_payload = EvidencePayload(
        payload_type=structured.payload_type,
        payload_schema_version=structured.payload_schema_version,
        payload=factual_pairs,
        payload_digest=target.content_digest,
        locator=EvidenceLocator(
            locator_type=structured.locator_type,
            locator_value=structured.locator_value,
            locator_schema_version=structured.locator_schema_version,
        ),
    )
    provenance = EvidenceProvenance(
        collection_id=collection.collection_id,
        producer_output_digest=target.content_digest,
        lineage=(
            target.evidence_id,
            structured.atomic_knowledge_id,
            structured.admission_payload_digest,
            structured.manifest_sha256,
            structured.identity_capture_sha256,
            structured.atomic_construction_authority_decision_packet_sha256,
            structured.downstream_binding_policy_decision_packet_sha256,
            *structured.source_relative_paths,
        ),
        observed_at=request.provenance_observed_at,
        source_registry_version=snapshot.registry_version,
    )
    eligibility_result = AcceptedEligibilityResult(
        decision=snapshot.evidence_eligibility,
        policy_id=snapshot.policy_id,
        policy_version=snapshot.policy_version,
        candidate_snapshot_digest=target.content_digest,
        source_id=collection.source_id,
        reason_codes=(snapshot.reason,),
        evaluated_at=request.eligibility_evaluated_at,
        evaluated_by=request.eligibility_evaluated_by,
        diagnostics=(),
    )
    provisional_materialization = EvidenceMaterializationRecord(
        materializer_id=request.materializer_id,
        materializer_version=request.materializer_version,
        materialized_at=request.accepted_at,
        acceptance_record_id=_PLACEHOLDER_ACCEPTANCE_RECORD_ID,
        accepted_by=request.accepted_by,
        acceptance_reason=request.acceptance_reason,
        review_record_id=request.review_record_id,
        identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
    )
    provisional_evidence = AcceptedEvidence(
        evidence_id=_PLACEHOLDER_EVIDENCE_ID,
        contract_version=ACCEPTED_EVIDENCE_CONTRACT_VERSION,
        candidate_reference=candidate_reference,
        source_snapshot=source_snapshot,
        producer_snapshot=producer_snapshot,
        factual_payload=factual_payload,
        provenance=provenance,
        eligibility_result=eligibility_result,
        materialization_record=provisional_materialization,
        diagnostics=(),
    )
    evidence_identity = calculate_evidence_identity(
        identity_input_from_accepted_evidence(provisional_evidence)
    )
    provisional_acceptance = AcceptanceRecord(
        acceptance_record_id=_PLACEHOLDER_ACCEPTANCE_RECORD_ID,
        contract_version=ACCEPTANCE_RECORD_CONTRACT_VERSION,
        evidence_id=evidence_identity.evidence_id,
        accepted_by=request.accepted_by,
        acceptance_reason=request.acceptance_reason,
        review_record_id=request.review_record_id,
        accepted_at=request.accepted_at,
        acceptance_policy_id=request.acceptance_policy_id,
        acceptance_policy_version=request.acceptance_policy_version,
        evidence_identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        evidence_identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
        materializer_id=request.materializer_id,
        materializer_version=request.materializer_version,
        diagnostics=(),
    )
    acceptance_identity = calculate_acceptance_identity(
        acceptance_identity_input_from_record(provisional_acceptance)
    )
    materialization_record = replace(
        provisional_materialization,
        acceptance_record_id=acceptance_identity.acceptance_record_id,
    )
    accepted_evidence = replace(
        provisional_evidence,
        evidence_id=evidence_identity.evidence_id,
        materialization_record=materialization_record,
    )
    acceptance_record = replace(
        provisional_acceptance,
        acceptance_record_id=acceptance_identity.acceptance_record_id,
    )
    if (
        calculate_evidence_identity(
            identity_input_from_accepted_evidence(accepted_evidence)
        )
        != evidence_identity
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "accepted_evidence_identity_recomputation_mismatch",
        )
    if (
        calculate_acceptance_identity(
            acceptance_identity_input_from_record(acceptance_record)
        )
        != acceptance_identity
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "acceptance_record_identity_recomputation_mismatch",
        )
    if acceptance_record.evidence_id != accepted_evidence.evidence_id:
        return _rejected(
            request.target_traceable_evidence_id,
            "accepted_output_evidence_id_mismatch",
        )

    return PersistedTraceableEvidenceAcceptanceBridgeResult(
        contract_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION
        ),
        status=BRIDGE_STATUS_MATERIALIZED,
        target_traceable_evidence_id=target.evidence_id,
        accepted_evidence=accepted_evidence,
        acceptance_record=acceptance_record,
        reason_codes=(),
    )


def materialize_persisted_traceable_evidence_acceptance(
    request: object,
) -> PersistedTraceableEvidenceAcceptanceBridgeResult:
    if type(request) is not PersistedTraceableEvidenceAcceptanceBridgeRequest:
        return _rejected("<invalid-request>", "invalid_request")
    try:
        request.__post_init__()
    except Exception:
        return _rejected(
            getattr(request, "target_traceable_evidence_id", "<invalid-request>"),
            "invalid_request",
        )

    if (
        request.target_traceable_evidence_id
        in PILOT_PRODUCT_VARIANT_STRUCTURED_EVIDENCE_IDS
    ):
        return _materialize_structured_product_variant_acceptance(request)

    if (
        request.target_traceable_evidence_id
        not in PILOT_FFS21_APPROVED_ATOMIC_EVIDENCE_IDS
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "target_traceable_evidence_outside_approved_five_fact_scope",
        )

    lookup = request.repository_lookup_result
    lookup_issue = _validate_persisted_lookup(lookup)
    if lookup_issue is not None:
        return _rejected(request.target_traceable_evidence_id, lookup_issue)

    collection = lookup.collection
    assert collection is not None
    if (
        collection.contract_version
        != EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "unsupported_collection_contract_version",
        )

    matches = tuple(
        item
        for item in collection.evidence_items
        if item.evidence_id == request.target_traceable_evidence_id
    )
    if len(matches) != 1:
        return _rejected(
            request.target_traceable_evidence_id,
            "target_traceable_evidence_not_found_or_not_unique",
        )
    target = matches[0]

    try:
        target.__post_init__()
    except Exception:
        return _rejected(
            request.target_traceable_evidence_id,
            "invalid_target_traceable_evidence",
        )
    if (
        target.contract_version
        != TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "target_traceable_evidence_not_v3_atomic",
        )

    atomic = getattr(target, "atomic_text_derivation_provenance", None)
    if type(atomic) is not TraceableEvidenceAtomicTextDerivationProvenance:
        return _rejected(
            request.target_traceable_evidence_id,
            "atomic_text_derivation_provenance_missing",
        )
    if (
        atomic.contract_version
        != ATOMIC_TEXT_DERIVATION_PROVENANCE_CONTRACT_VERSION
        or atomic.derivation_type != ATOMIC_TEXT_DERIVATION_TYPE
        or atomic.atomic_statement_sha256 != target.content_digest
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "atomic_text_derivation_provenance_mismatch",
        )

    snapshot = collection.eligibility_snapshot
    if target.eligibility_snapshot_digest != derive_evidence_eligibility_snapshot_digest(
        snapshot
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "eligibility_snapshot_digest_mismatch",
        )
    if (
        snapshot.evidence_eligibility != "eligible"
        or snapshot.evidence_collection_allowed is not True
        or snapshot.requires_review is not False
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "persisted_evidence_not_finally_eligible",
        )
    if (
        target.provenance.source_id != collection.source_id
        or target.provenance.source_path != collection.source_path
        or target.provenance.source_checksum != collection.source_checksum
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "persisted_source_provenance_mismatch",
        )

    candidate_reference = EvidenceCandidateReference(
        candidate_contract_version=target.contract_version,
        candidate_snapshot_digest=target.content_digest,
        candidate_source_id=collection.source_id,
        candidate_producer_name=target.provenance.extraction_method,
        candidate_producer_version=target.provenance.upstream_contract_version,
        candidate_payload_digest=target.content_digest,
    )
    source_snapshot = EvidenceSourceSnapshot(
        source_id=collection.source_id,
        source_path=collection.source_path,
        source_type=snapshot.source_type,
        document_classification=snapshot.document_classification,
        authority_status=snapshot.authority_status,
        lifecycle_status=snapshot.lifecycle_status,
        evidence_eligibility=snapshot.evidence_eligibility,
        source_content_digest=collection.source_checksum,
    )
    producer_snapshot = EvidenceProducerSnapshot(
        producer_name=target.provenance.extraction_method,
        producer_version=target.provenance.upstream_contract_version,
        producer_kind=target.provenance.extraction_status,
        producer_contract_version=target.provenance.artifact_contract_version,
    )
    factual_payload = EvidencePayload(
        payload_type="text",
        payload_schema_version="1.0.0",
        payload=(("text", target.content),),
        payload_digest=target.content_digest,
        locator=EvidenceLocator(
            locator_type=target.provenance.extraction_method,
            locator_value=(
                target.provenance.page_index,
                target.provenance.page_number,
                target.provenance.extraction_index,
            ),
            locator_schema_version=target.contract_version,
        ),
    )
    lineage = (
        target.evidence_id,
        atomic.parent_traceable_evidence_id,
        *atomic.source_span_ids,
        atomic.operator_decision_packet_sha256,
    )
    provenance = EvidenceProvenance(
        collection_id=collection.collection_id,
        producer_output_digest=target.content_digest,
        lineage=lineage,
        observed_at=request.provenance_observed_at,
        source_registry_version=snapshot.registry_version,
    )
    eligibility_result = AcceptedEligibilityResult(
        decision=snapshot.evidence_eligibility,
        policy_id=snapshot.policy_id,
        policy_version=snapshot.policy_version,
        candidate_snapshot_digest=target.content_digest,
        source_id=collection.source_id,
        reason_codes=(snapshot.reason,),
        evaluated_at=request.eligibility_evaluated_at,
        evaluated_by=request.eligibility_evaluated_by,
        diagnostics=(),
    )

    provisional_materialization = EvidenceMaterializationRecord(
        materializer_id=request.materializer_id,
        materializer_version=request.materializer_version,
        materialized_at=request.accepted_at,
        acceptance_record_id=_PLACEHOLDER_ACCEPTANCE_RECORD_ID,
        accepted_by=request.accepted_by,
        acceptance_reason=request.acceptance_reason,
        review_record_id=request.review_record_id,
        identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
    )
    provisional_evidence = AcceptedEvidence(
        evidence_id=_PLACEHOLDER_EVIDENCE_ID,
        contract_version=ACCEPTED_EVIDENCE_CONTRACT_VERSION,
        candidate_reference=candidate_reference,
        source_snapshot=source_snapshot,
        producer_snapshot=producer_snapshot,
        factual_payload=factual_payload,
        provenance=provenance,
        eligibility_result=eligibility_result,
        materialization_record=provisional_materialization,
        diagnostics=(),
    )
    evidence_identity = calculate_evidence_identity(
        identity_input_from_accepted_evidence(provisional_evidence)
    )

    provisional_acceptance = AcceptanceRecord(
        acceptance_record_id=_PLACEHOLDER_ACCEPTANCE_RECORD_ID,
        contract_version=ACCEPTANCE_RECORD_CONTRACT_VERSION,
        evidence_id=evidence_identity.evidence_id,
        accepted_by=request.accepted_by,
        acceptance_reason=request.acceptance_reason,
        review_record_id=request.review_record_id,
        accepted_at=request.accepted_at,
        acceptance_policy_id=request.acceptance_policy_id,
        acceptance_policy_version=request.acceptance_policy_version,
        evidence_identity_policy_id=EVIDENCE_IDENTITY_POLICY_ID,
        evidence_identity_policy_version=EVIDENCE_IDENTITY_POLICY_VERSION,
        materializer_id=request.materializer_id,
        materializer_version=request.materializer_version,
        diagnostics=(),
    )
    acceptance_identity = calculate_acceptance_identity(
        acceptance_identity_input_from_record(provisional_acceptance)
    )

    materialization_record = replace(
        provisional_materialization,
        acceptance_record_id=acceptance_identity.acceptance_record_id,
    )
    accepted_evidence = replace(
        provisional_evidence,
        evidence_id=evidence_identity.evidence_id,
        materialization_record=materialization_record,
    )
    acceptance_record = replace(
        provisional_acceptance,
        acceptance_record_id=acceptance_identity.acceptance_record_id,
    )

    if (
        calculate_evidence_identity(
            identity_input_from_accepted_evidence(accepted_evidence)
        )
        != evidence_identity
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "accepted_evidence_identity_recomputation_mismatch",
        )
    if (
        calculate_acceptance_identity(
            acceptance_identity_input_from_record(acceptance_record)
        )
        != acceptance_identity
    ):
        return _rejected(
            request.target_traceable_evidence_id,
            "acceptance_record_identity_recomputation_mismatch",
        )
    if acceptance_record.evidence_id != accepted_evidence.evidence_id:
        return _rejected(
            request.target_traceable_evidence_id,
            "accepted_output_evidence_id_mismatch",
        )

    return PersistedTraceableEvidenceAcceptanceBridgeResult(
        contract_version=(
            PERSISTED_TRACEABLE_EVIDENCE_ACCEPTANCE_BRIDGE_RESULT_CONTRACT_VERSION
        ),
        status=BRIDGE_STATUS_MATERIALIZED,
        target_traceable_evidence_id=target.evidence_id,
        accepted_evidence=accepted_evidence,
        acceptance_record=acceptance_record,
        reason_codes=(),
    )
