"""Pure Gate 8 persisted-Evidence Knowledge construction service."""

from __future__ import annotations

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


def _shared_semantic_anchors_match(
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
