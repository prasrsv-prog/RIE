"""Pure Gate 8 persisted-Evidence Knowledge construction service."""

from __future__ import annotations

import json as _json

from rie.application.knowledge_constructor import (
    KnowledgeConstructionRequest as _KnowledgeConstructionRequest,
    KnowledgeConstructionResult as _KnowledgeConstructionResult,
    construct_knowledge_candidate as _construct_knowledge_candidate,
)
from rie.domain.acceptance_identity import (
    acceptance_identity_input_from_record as _acceptance_identity_input_from_record,
    calculate_acceptance_identity as _calculate_acceptance_identity,
)
from rie.domain.acceptance_record import (
    AcceptanceRecord as _AcceptanceRecord,
)
from rie.domain.accepted_evidence import (
    AcceptedEvidence as _AcceptedEvidence,
)
from rie.domain.evidence_identity import (
    calculate_evidence_identity as _calculate_evidence_identity,
    identity_input_from_accepted_evidence as _identity_input_from_accepted_evidence,
)
from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_collection_id as _derive_evidence_collection_id,
    derive_evidence_eligibility_snapshot_digest as _derive_snapshot_digest,
    derive_traceable_evidence_id as _derive_traceable_evidence_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EvidenceCollection as _EvidenceCollection,
    EvidenceEligibilitySnapshot as _EvidenceEligibilitySnapshot,
    TraceableEvidence as _TraceableEvidence,
)
from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest as _calculate_payload_digest,
    calculate_evidence_repository_audit_id as _calculate_audit_id,
    calculate_evidence_repository_revision_id as _calculate_revision_id,
)
from rie.evidence_repository.evidence_repository_contract import (
    EvidenceRepositoryAuditRecord as _EvidenceRepositoryAuditRecord,
    EvidenceRepositoryLookupResult as _EvidenceRepositoryLookupResult,
    EvidenceRepositoryRevision as _EvidenceRepositoryRevision,
)

from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION as _EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION as _TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE as _TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
    TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION as _TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION,
    TraceableEvidenceStructuredMetadataProvenance as _TraceableEvidenceStructuredMetadataProvenance,
)

from .persisted_evidence_knowledge_construction_canonicalization import (
    derive_persisted_evidence_knowledge_compatibility_record_id as _derive_compatibility_id,
)
from .persisted_evidence_knowledge_construction_contract import (
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID as _POLICY_ID,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION as _POLICY_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION as _RECORD_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION as _REQUEST_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION as _RESULT_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED as _CONSTRUCTED,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED as _REJECTED,
    PersistedEvidenceKnowledgeCompatibilityRecord as _CompatibilityRecord,
    PersistedEvidenceKnowledgeConstructionRequest as _Request,
    PersistedEvidenceKnowledgeConstructionResult as _Result,
    _issue,
)


def _rejected(
    code: str,
    *,
    compatibility_record: _CompatibilityRecord | None = None,
    knowledge_construction_result: _KnowledgeConstructionResult | None = None,
) -> _Result:
    if code != "knowledge_construction_rejected":
        compatibility_record = None
        knowledge_construction_result = None
    return _Result(
        contract_version=_RESULT_VERSION,
        status=_REJECTED,
        mutation_performed=False,
        compatibility_record=compatibility_record,
        knowledge_construction_result=knowledge_construction_result,
        issue=_issue(code),
    )


def _valid_target_id(value: object) -> bool:
    return (
        type(value) is str
        and value.startswith("evm1_")
        and len(value) == 69
        and all(character in "0123456789abcdef" for character in value[5:])
    )


def _request_core_is_valid(request: _Request) -> bool:
    if not _valid_target_id(getattr(request, "target_evidence_id", None)):
        return False
    nested = getattr(request, "knowledge_construction_request", None)
    if type(nested) is not _KnowledgeConstructionRequest:
        return False
    try:
        nested.__post_init__()
    except Exception:
        return False
    return True


def _lookup_is_valid(lookup: object) -> bool:
    if type(lookup) is not _EvidenceRepositoryLookupResult:
        return False
    try:
        lookup.__post_init__()
    except Exception:
        return False
    return True


def _repository_linkage_matches(
    revision: _EvidenceRepositoryRevision,
    audit: _EvidenceRepositoryAuditRecord,
    collection: _EvidenceCollection,
) -> bool:
    return (
        revision.source_id == collection.source_id
        and revision.collection_id == collection.collection_id
        and revision.audit_id == audit.audit_id
        and audit.revision_id == revision.revision_id
        and audit.source_id == revision.source_id
        and audit.revision_number == revision.revision_number
        and audit.collection_id == revision.collection_id
    )


def _repository_identities_match(
    revision: _EvidenceRepositoryRevision,
    audit: _EvidenceRepositoryAuditRecord,
    collection: _EvidenceCollection,
    target_evidence_id: str,
) -> bool:
    try:
        revision.__post_init__()
        audit.__post_init__()
        if revision.revision_id != _calculate_revision_id(
            source_id=revision.source_id,
            revision_number=revision.revision_number,
            collection_id=revision.collection_id,
            collection_payload_digest=revision.collection_payload_digest,
            previous_revision_id=revision.previous_revision_id,
        ):
            return False
        if audit.audit_id != _calculate_audit_id(
            action=audit.action,
            revision_id=audit.revision_id,
            source_id=audit.source_id,
            revision_number=audit.revision_number,
            collection_id=audit.collection_id,
            actor_id=audit.actor_id,
            recorded_at_utc=audit.recorded_at_utc,
        ):
            return False
        if collection.collection_id != _derive_evidence_collection_id(collection):
            return False
        snapshot_digest = _derive_snapshot_digest(collection.eligibility_snapshot)
        for item in collection.evidence_items:
            if item.eligibility_snapshot_digest != snapshot_digest:
                return False
            if (
                item.evidence_id != target_evidence_id
                and item.evidence_id != _derive_traceable_evidence_id(item)
            ):
                return False
    except Exception:
        return False
    return True


def _target_item(
    collection: _EvidenceCollection,
    target_evidence_id: str,
) -> _TraceableEvidence | None:
    matches = tuple(
        item
        for item in collection.evidence_items
        if item.evidence_id == target_evidence_id
    )
    if len(matches) != 1:
        return None
    return matches[0]


def _target_is_eligible(
    snapshot: _EvidenceEligibilitySnapshot,
) -> bool:
    try:
        snapshot.__post_init__()
    except Exception:
        return False
    return (
        snapshot.evidence_eligibility == "eligible"
        and snapshot.evidence_collection_allowed is True
        and snapshot.requires_review is False
    )


def _accepted_evidence_identity_matches(
    accepted_evidence: _AcceptedEvidence,
) -> bool:
    try:
        accepted_evidence.__post_init__()
        result = _calculate_evidence_identity(
            _identity_input_from_accepted_evidence(accepted_evidence)
        )
    except Exception:
        return False
    return result.evidence_id == accepted_evidence.evidence_id


def _acceptance_records_match(
    accepted_evidence: _AcceptedEvidence,
    records: tuple[_AcceptanceRecord, ...],
) -> bool:
    if type(records) is not tuple or not records:
        return False
    ids = tuple(record.acceptance_record_id for record in records)
    if len(set(ids)) != len(ids):
        return False
    for record in records:
        if type(record) is not _AcceptanceRecord:
            return False
        try:
            record.__post_init__()
            identity = _calculate_acceptance_identity(
                _acceptance_identity_input_from_record(record)
            )
        except Exception:
            return False
        if (
            identity.acceptance_record_id != record.acceptance_record_id
            or record.evidence_id != accepted_evidence.evidence_id
        ):
            return False
    materialization_id = (
        accepted_evidence.materialization_record.acceptance_record_id
    )
    return sum(
        record.acceptance_record_id == materialization_id
        for record in records
    ) == 1


def _legacy_text_semantic_anchors_match(
    collection: _EvidenceCollection,
    target: _TraceableEvidence,
    accepted: _AcceptedEvidence,
) -> bool:
    snapshot = collection.eligibility_snapshot
    source = accepted.source_snapshot
    provenance = accepted.provenance
    payload = accepted.factual_payload
    return (
        source.source_id == collection.source_id == snapshot.source_id
        and source.source_path == collection.source_path == snapshot.source_path
        and source.source_content_digest
        == collection.source_checksum
        == snapshot.source_checksum
        and source.source_type == snapshot.source_type
        and source.document_classification
        == snapshot.document_classification
        and source.authority_status == snapshot.authority_status
        and source.lifecycle_status == snapshot.lifecycle_status
        and source.evidence_eligibility == snapshot.evidence_eligibility
        and provenance.source_registry_version == snapshot.registry_version
        and provenance.collection_id == collection.collection_id
        and target.content_type == "page_text_utf8"
        and payload.payload_type == "text"
        and payload.payload_schema_version == "1.0.0"
        and type(payload.payload) is tuple
        and len(payload.payload) == 1
        and type(payload.payload[0]) is tuple
        and len(payload.payload[0]) == 2
        and payload.payload[0][0] == "text"
        and payload.payload[0][1] == target.content
        and payload.payload_digest == target.content_digest
    )

_STRUCTURED_V4_EXACT_COLLECTION_ID = (
    "evc1_06534223733730505e33f7225d3d0507da70157396b5f94944d1e646d1b24f4b"
)
_STRUCTURED_V4_EXACT_TRACEABLE_EVIDENCE_IDS = frozenset(
(
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
)
)
_STRUCTURED_V4_EXACT_INPUT_CARDINALITY = 18
_STRUCTURED_V4_PAYLOAD_SCHEMA_VERSION = "1.0.0"


def _structured_v4_semantic_anchors_match(
    collection: _EvidenceCollection,
    target: _TraceableEvidence,
    accepted: _AcceptedEvidence,
) -> bool:
    """Exact18 structured-v4 compatibility projection; no text coercion."""

    try:
        structured = target.provenance
        if type(structured) is not _TraceableEvidenceStructuredMetadataProvenance:
            return False
        structured.__post_init__()

        if (
            collection.contract_version != _EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION
            or collection.collection_id != _STRUCTURED_V4_EXACT_COLLECTION_ID
            or len(collection.evidence_items) != _STRUCTURED_V4_EXACT_INPUT_CARDINALITY
            or frozenset(item.evidence_id for item in collection.evidence_items)
            != _STRUCTURED_V4_EXACT_TRACEABLE_EVIDENCE_IDS
            or target.evidence_id not in _STRUCTURED_V4_EXACT_TRACEABLE_EVIDENCE_IDS
            or target.contract_version != _TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION
            or target.content_type != _TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE
            or structured.contract_version
            != _TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION
            or structured.payload_type != _TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE
            or structured.payload_schema_version != _STRUCTURED_V4_PAYLOAD_SCHEMA_VERSION
            or any(
                hasattr(structured, field_name)
                for field_name in ("page_index", "page_number", "extraction_index")
            )
        ):
            return False

        payload_object = _json.loads(target.content)
        if type(payload_object) is not dict:
            return False
        if "source_relative_paths" not in payload_object:
            return False
        if type(payload_object["source_relative_paths"]) is not list:
            return False

        factual_pairs = tuple(
            (
                key,
                tuple(value) if key == "source_relative_paths" else value,
            )
            for key, value in sorted(payload_object.items())
        )
        expected_lineage = (
            target.evidence_id,
            structured.atomic_knowledge_id,
            structured.admission_payload_digest,
            structured.manifest_sha256,
            structured.identity_capture_sha256,
            structured.atomic_construction_authority_decision_packet_sha256,
            structured.downstream_binding_policy_decision_packet_sha256,
            *structured.source_relative_paths,
        )

        snapshot = collection.eligibility_snapshot
        source = accepted.source_snapshot
        payload = accepted.factual_payload
        provenance = accepted.provenance
        candidate = accepted.candidate_reference
        producer = accepted.producer_snapshot
        eligibility = accepted.eligibility_result

        return (
            source.source_id == collection.source_id == snapshot.source_id
            and source.source_path == collection.source_path == snapshot.source_path
            and source.source_content_digest
            == collection.source_checksum
            == snapshot.source_checksum
            and source.source_type == snapshot.source_type
            and source.document_classification == snapshot.document_classification
            and source.authority_status == snapshot.authority_status
            and source.lifecycle_status == snapshot.lifecycle_status
            and source.evidence_eligibility == snapshot.evidence_eligibility
            and provenance.source_registry_version == snapshot.registry_version
            and provenance.collection_id == collection.collection_id
            and payload.payload_type == structured.payload_type
            and payload.payload_schema_version == structured.payload_schema_version
            and payload.payload == factual_pairs
            and payload.payload_digest
            == target.content_digest
            == structured.admission_payload_digest
            and payload.locator.locator_type == structured.locator_type
            and payload.locator.locator_value == structured.locator_value
            and payload.locator.locator_schema_version == structured.locator_schema_version
            and provenance.producer_output_digest == target.content_digest
            and provenance.lineage == expected_lineage
            and candidate.candidate_contract_version == target.contract_version
            and candidate.candidate_snapshot_digest == target.content_digest
            and candidate.candidate_source_id == collection.source_id
            and candidate.candidate_producer_name == structured.payload_type
            and candidate.candidate_producer_version == structured.payload_schema_version
            and candidate.candidate_payload_digest == target.content_digest
            and producer.producer_name == structured.payload_type
            and producer.producer_version == structured.payload_schema_version
            and producer.producer_kind == target.content_type
            and producer.producer_contract_version == structured.contract_version
            and eligibility.decision == snapshot.evidence_eligibility
            and eligibility.policy_id == snapshot.policy_id
            and eligibility.policy_version == snapshot.policy_version
            and eligibility.candidate_snapshot_digest == target.content_digest
            and eligibility.source_id == collection.source_id
            and payload_object.get("atomic_knowledge_id") == structured.atomic_knowledge_id
            and tuple(payload_object.get("source_relative_paths", ()))
            == structured.source_relative_paths
            and payload_object.get("manifest_sha256") == structured.manifest_sha256
            and payload_object.get("identity_capture_sha256")
            == structured.identity_capture_sha256
            and payload_object.get(
                "atomic_construction_authority_decision_packet_sha256"
            )
            == structured.atomic_construction_authority_decision_packet_sha256
            and payload_object.get(
                "downstream_binding_policy_decision_packet_sha256"
            )
            == structured.downstream_binding_policy_decision_packet_sha256
        )
    except Exception:
        return False


def _shared_semantic_anchors_match(
    collection: _EvidenceCollection,
    target: _TraceableEvidence,
    accepted: _AcceptedEvidence,
) -> bool:
    if target.content_type == "page_text_utf8":
        return _legacy_text_semantic_anchors_match(collection, target, accepted)
    if target.content_type == _TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE:
        return _structured_v4_semantic_anchors_match(collection, target, accepted)
    return False


def _compatibility_record(
    request: _Request,
    revision: _EvidenceRepositoryRevision,
    audit: _EvidenceRepositoryAuditRecord,
    collection: _EvidenceCollection,
    target: _TraceableEvidence,
) -> _CompatibilityRecord:
    nested = request.knowledge_construction_request
    accepted = nested.accepted_evidence
    acceptance_ids = tuple(
        sorted(
            record.acceptance_record_id
            for record in nested.acceptance_records
        )
    )
    values = {
        "contract_version": _RECORD_VERSION,
        "repository_revision_id": revision.revision_id,
        "source_id": revision.source_id,
        "revision_number": revision.revision_number,
        "previous_revision_id": revision.previous_revision_id,
        "collection_id": collection.collection_id,
        "collection_payload_digest": revision.collection_payload_digest,
        "repository_audit_id": audit.audit_id,
        "traceable_evidence_id": target.evidence_id,
        "accepted_evidence_id": accepted.evidence_id,
        "acceptance_record_ids": acceptance_ids,
        "construction_rule_id": nested.construction_rule_id,
        "construction_rule_version": nested.construction_rule_version,
        "compatibility_policy_id": request.compatibility_policy_id,
        "compatibility_policy_version": request.compatibility_policy_version,
    }
    record_id = _derive_compatibility_id(**values)
    return _CompatibilityRecord(
        compatibility_record_id=record_id,
        **values,
    )


def construct_knowledge_from_persisted_evidence(request: object) -> _Result:
    if type(request) is not _Request:
        return _rejected("invalid_request")
    if getattr(request, "contract_version", None) != _REQUEST_VERSION:
        return _rejected("unsupported_contract_version")
    if (
        getattr(request, "compatibility_policy_id", None) != _POLICY_ID
        or getattr(request, "compatibility_policy_version", None)
        != _POLICY_VERSION
    ):
        return _rejected("unsupported_compatibility_policy")
    if not _request_core_is_valid(request):
        return _rejected("invalid_request")

    lookup = getattr(request, "repository_lookup_result", None)
    if not _lookup_is_valid(lookup):
        return _rejected("invalid_repository_lookup_result")
    if lookup.status == "not_found":
        return _rejected("repository_lookup_not_found")
    if lookup.status == "rejected":
        return _rejected("repository_lookup_rejected")

    revision = lookup.revision
    audit = lookup.audit_record
    collection = lookup.collection
    if (
        type(revision) is not _EvidenceRepositoryRevision
        or type(audit) is not _EvidenceRepositoryAuditRecord
        or type(collection) is not _EvidenceCollection
    ):
        return _rejected("invalid_repository_lookup_result")
    if not _repository_linkage_matches(revision, audit, collection):
        return _rejected("repository_linkage_mismatch")
    if not _repository_identities_match(
        revision,
        audit,
        collection,
        request.target_evidence_id,
    ):
        return _rejected("repository_identity_mismatch")
    try:
        payload_digest = _calculate_payload_digest(collection)
    except Exception:
        return _rejected("repository_identity_mismatch")
    if payload_digest != revision.collection_payload_digest:
        return _rejected("collection_payload_digest_mismatch")

    target = _target_item(collection, request.target_evidence_id)
    if target is None:
        return _rejected("target_evidence_not_found")
    try:
        if target.evidence_id != _derive_traceable_evidence_id(target):
            return _rejected("target_evidence_identity_mismatch")
    except Exception:
        return _rejected("target_evidence_identity_mismatch")
    if not _target_is_eligible(collection.eligibility_snapshot):
        return _rejected("ineligible_evidence")

    nested = request.knowledge_construction_request
    accepted = nested.accepted_evidence
    if not _accepted_evidence_identity_matches(accepted):
        return _rejected("accepted_evidence_identity_mismatch")
    if not _acceptance_records_match(
        accepted,
        nested.acceptance_records,
    ):
        return _rejected("acceptance_record_identity_mismatch")
    if not _shared_semantic_anchors_match(
        collection,
        target,
        accepted,
    ):
        return _rejected("evidence_compatibility_mismatch")

    try:
        compatibility = _compatibility_record(
            request,
            revision,
            audit,
            collection,
            target,
        )
    except Exception:
        return _rejected("internal_contract_violation")

    try:
        nested_result = _construct_knowledge_candidate(nested)
    except Exception:
        return _rejected("internal_contract_violation")
    if type(nested_result) is not _KnowledgeConstructionResult:
        return _rejected("internal_contract_violation")
    try:
        nested_result.__post_init__()
    except Exception:
        return _rejected("internal_contract_violation")
    if nested_result.decision == "rejected":
        return _rejected(
            "knowledge_construction_rejected",
            compatibility_record=compatibility,
            knowledge_construction_result=nested_result,
        )
    if nested_result.decision != "constructed":
        return _rejected("internal_contract_violation")

    return _Result(
        contract_version=_RESULT_VERSION,
        status=_CONSTRUCTED,
        mutation_performed=False,
        compatibility_record=compatibility,
        knowledge_construction_result=nested_result,
        issue=None,
    )
