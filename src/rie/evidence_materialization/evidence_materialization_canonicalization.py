"""Canonical identity functions for Gate 6 Evidence Materialization."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .evidence_materialization_contract import (
    EVIDENCE_COLLECTION_ID_PREFIX,
    EVIDENCE_COLLECTION_IDENTITY_FIELD_ORDER,
    EVIDENCE_ELIGIBILITY_FIELD_ORDER,
    TRACEABLE_EVIDENCE_FIELD_ORDER,
    TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER,
    TRACEABLE_EVIDENCE_ID_PREFIX,
    TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    TraceableEvidence,
    TraceableEvidenceProvenance,
)

from . import evidence_materialization_contract as _contract


def _canonical_json_bytes(value: object) -> bytes:
    text = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    result = (text + "\n").encode("utf-8")
    if (
        result.startswith(b"\xef\xbb\xbf")
        or b"\r" in result
        or not result.endswith(b"\n")
        or result.endswith(b"\n\n")
    ):
        raise RuntimeError("canonical byte encoding is invalid.")
    return result


def _eligibility_dict(
    snapshot: EvidenceEligibilitySnapshot,
) -> dict[str, Any]:
    if type(snapshot) is not EvidenceEligibilitySnapshot:
        raise TypeError(
            "snapshot must be exact EvidenceEligibilitySnapshot."
        )
    payload = {
        "contract_version": snapshot.contract_version,
        "source_id": snapshot.source_id,
        "source_path": snapshot.source_path,
        "source_checksum": snapshot.source_checksum,
        "source_type": snapshot.source_type,
        "document_classification": snapshot.document_classification,
        "authority_status": snapshot.authority_status,
        "lifecycle_status": snapshot.lifecycle_status,
        "evidence_eligibility": snapshot.evidence_eligibility,
        "evidence_collection_allowed":
            snapshot.evidence_collection_allowed,
        "requires_review": snapshot.requires_review,
        "reason": snapshot.reason,
        "policy_id": snapshot.policy_id,
        "policy_version": snapshot.policy_version,
        "registry_version": snapshot.registry_version,
    }
    if tuple(payload) != EVIDENCE_ELIGIBILITY_FIELD_ORDER:
        raise RuntimeError("eligibility field order is invalid.")
    return payload


def _provenance_dict(
    provenance: TraceableEvidenceProvenance,
) -> dict[str, Any]:
    if type(provenance) is not TraceableEvidenceProvenance:
        raise TypeError(
            "provenance must be exact TraceableEvidenceProvenance."
        )
    payload = {
        "artifact_contract_version":
            provenance.artifact_contract_version,
        "artifact_id": provenance.artifact_id,
        "upstream_contract_version":
            provenance.upstream_contract_version,
        "job_id": provenance.job_id,
        "source_id": provenance.source_id,
        "source_path": provenance.source_path,
        "source_checksum": provenance.source_checksum,
        "page_index": provenance.page_index,
        "page_number": provenance.page_number,
        "extraction_index": provenance.extraction_index,
        "extraction_method": provenance.extraction_method,
        "extraction_status": provenance.extraction_status,
        "execution_report_location":
            provenance.execution_report_location,
    }
    if tuple(payload) != TRACEABLE_EVIDENCE_PROVENANCE_FIELD_ORDER:
        raise RuntimeError("provenance field order is invalid.")
    return payload



def _ocr_remediation_provenance_dict(value: object) -> dict[str, Any]:
    expected_type = _contract.TraceableEvidenceOcrRemediationProvenance
    if type(value) is not expected_type:
        raise TypeError(
            "OCR remediation provenance has an invalid exact type."
        )
    payload = {
        "producer_operation_id": value.producer_operation_id,
        "producer_artifact_path": value.producer_artifact_path,
        "producer_artifact_sha256": value.producer_artifact_sha256,
        "producer_artifact_set_digest": value.producer_artifact_set_digest,
        "extraction_method": value.extraction_method,
    }
    if (
        tuple(payload)
        != _contract.TRACEABLE_EVIDENCE_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER
    ):
        raise RuntimeError(
            "OCR remediation provenance field order is invalid."
        )
    return payload

def _atomic_text_derivation_provenance_dict(
    value: object,
) -> dict[str, Any]:
    expected_type = _contract.TraceableEvidenceAtomicTextDerivationProvenance
    if type(value) is not expected_type:
        raise TypeError(
            "atomic_text_derivation_provenance must be exact "
            "TraceableEvidenceAtomicTextDerivationProvenance"
        )
    payload = {
        "contract_version": value.contract_version,
        "derivation_type": value.derivation_type,
        "parent_traceable_evidence_id":
            value.parent_traceable_evidence_id,
        "parent_content_digest": value.parent_content_digest,
        "source_span_ids": list(value.source_span_ids),
        "operator_decision_packet_sha256":
            value.operator_decision_packet_sha256,
        "atomic_statement_sha256": value.atomic_statement_sha256,
    }
    if (
        tuple(payload)
        != _contract.TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_PROVENANCE_FIELD_ORDER
    ):
        raise RuntimeError(
            "atomic text derivation provenance field order is invalid."
        )
    return payload




def _evidence_identity_dict(
    evidence: TraceableEvidence,
) -> dict[str, Any]:
    if type(evidence) is not TraceableEvidence:
        raise TypeError("evidence must be exact TraceableEvidence.")
    payload = {
        "contract_version": evidence.contract_version,
        "content_type": evidence.content_type,
        "content": evidence.content,
        "content_digest": evidence.content_digest,
        "warnings": list(evidence.warnings),
        "provenance": _provenance_dict(evidence.provenance),
        "eligibility_snapshot_digest":
            evidence.eligibility_snapshot_digest,
    }
    if (
        evidence.contract_version
        == _contract.TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
    ):
        payload["ocr_remediation_provenance"] = (
            _ocr_remediation_provenance_dict(
                evidence.ocr_remediation_provenance
            )
        )
        payload["atomic_text_derivation_provenance"] = (
            _atomic_text_derivation_provenance_dict(
                evidence.atomic_text_derivation_provenance
            )
        )
        expected_order = (
            _contract.TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_IDENTITY_FIELD_ORDER
        )
    elif (
        evidence.contract_version
        == _contract.TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION
    ):
        payload["ocr_remediation_provenance"] = (
            _ocr_remediation_provenance_dict(
                evidence.ocr_remediation_provenance
            )
        )
        expected_order = (
            _contract.TRACEABLE_EVIDENCE_OCR_IDENTITY_FIELD_ORDER
        )
    else:
        expected_order = TRACEABLE_EVIDENCE_IDENTITY_FIELD_ORDER
    if tuple(payload) != expected_order:
        raise RuntimeError("Evidence identity field order is invalid.")
    return payload




def _evidence_dict(evidence: TraceableEvidence) -> dict[str, Any]:
    payload = {
        "contract_version": evidence.contract_version,
        "evidence_id": evidence.evidence_id,
        "content_type": evidence.content_type,
        "content": evidence.content,
        "content_digest": evidence.content_digest,
        "warnings": list(evidence.warnings),
        "provenance": _provenance_dict(evidence.provenance),
        "eligibility_snapshot_digest":
            evidence.eligibility_snapshot_digest,
    }
    if (
        evidence.contract_version
        == _contract.TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
    ):
        payload["ocr_remediation_provenance"] = (
            _ocr_remediation_provenance_dict(
                evidence.ocr_remediation_provenance
            )
        )
        payload["atomic_text_derivation_provenance"] = (
            _atomic_text_derivation_provenance_dict(
                evidence.atomic_text_derivation_provenance
            )
        )
        expected_order = (
            _contract.TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_FIELD_ORDER
        )
    elif (
        evidence.contract_version
        == _contract.TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION
    ):
        payload["ocr_remediation_provenance"] = (
            _ocr_remediation_provenance_dict(
                evidence.ocr_remediation_provenance
            )
        )
        expected_order = _contract.TRACEABLE_EVIDENCE_OCR_FIELD_ORDER
    else:
        expected_order = TRACEABLE_EVIDENCE_FIELD_ORDER
    if tuple(payload) != expected_order:
        raise RuntimeError("Evidence field order is invalid.")
    return payload


def _collection_identity_dict(
    collection: EvidenceCollection,
) -> dict[str, Any]:
    if type(collection) is not EvidenceCollection:
        raise TypeError("collection must be exact EvidenceCollection.")
    payload = {
        "contract_version": collection.contract_version,
        "artifact_contract_version":
            collection.artifact_contract_version,
        "artifact_id": collection.artifact_id,
        "upstream_contract_version":
            collection.upstream_contract_version,
        "job_id": collection.job_id,
        "source_id": collection.source_id,
        "source_path": collection.source_path,
        "source_checksum": collection.source_checksum,
        "eligibility_snapshot":
            _eligibility_dict(collection.eligibility_snapshot),
        "evidence_items": [
            _evidence_dict(item) for item in collection.evidence_items
        ],
    }
    if tuple(payload) != EVIDENCE_COLLECTION_IDENTITY_FIELD_ORDER:
        raise RuntimeError("collection identity field order is invalid.")
    return payload


def canonicalize_evidence_eligibility_snapshot(
    snapshot: EvidenceEligibilitySnapshot,
) -> bytes:
    return _canonical_json_bytes(_eligibility_dict(snapshot))


def derive_evidence_eligibility_snapshot_digest(
    snapshot: EvidenceEligibilitySnapshot,
) -> str:
    return hashlib.sha256(
        canonicalize_evidence_eligibility_snapshot(snapshot)
    ).hexdigest()


def canonicalize_traceable_evidence_identity(
    evidence: TraceableEvidence,
) -> bytes:
    return _canonical_json_bytes(_evidence_identity_dict(evidence))


def derive_traceable_evidence_id(
    evidence: TraceableEvidence,
) -> str:
    digest = hashlib.sha256(
        canonicalize_traceable_evidence_identity(evidence)
    ).hexdigest()
    return TRACEABLE_EVIDENCE_ID_PREFIX + digest


def canonicalize_evidence_collection_identity(
    collection: EvidenceCollection,
) -> bytes:
    return _canonical_json_bytes(_collection_identity_dict(collection))


def derive_evidence_collection_id(
    collection: EvidenceCollection,
) -> str:
    digest = hashlib.sha256(
        canonicalize_evidence_collection_identity(collection)
    ).hexdigest()
    return EVIDENCE_COLLECTION_ID_PREFIX + digest


__all__ = (
    "canonicalize_evidence_eligibility_snapshot",
    "derive_evidence_eligibility_snapshot_digest",
    "canonicalize_traceable_evidence_identity",
    "derive_traceable_evidence_id",
    "canonicalize_evidence_collection_identity",
    "derive_evidence_collection_id",
)
