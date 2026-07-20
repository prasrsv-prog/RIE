
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib

from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_evidence_collection_id,
    derive_evidence_eligibility_snapshot_digest,
    derive_traceable_evidence_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_COLLECTION_CONTRACT_VERSION,
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_CONTENT_TYPE,
    TRACEABLE_EVIDENCE_CONTRACT_VERSION,
    EVIDENCE_COLLECTION_ID_PREFIX,
    TRACEABLE_EVIDENCE_ID_PREFIX,
    EvidenceCollection,
    EvidenceEligibilitySnapshot,
    TraceableEvidence,
    TraceableEvidenceProvenance,
)


def _snapshot(
    *,
    source_id: str = "source-001",
    source_path: str = "official/specification.pdf",
    source_checksum: str = "a" * 64,
) -> EvidenceEligibilitySnapshot:
    return EvidenceEligibilitySnapshot(
        contract_version=EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
        source_id=source_id,
        source_path=source_path,
        source_checksum=source_checksum,
        source_type="pdf",
        document_classification="official_source",
        authority_status="official",
        lifecycle_status="active",
        evidence_eligibility="eligible",
        evidence_collection_allowed=True,
        requires_review=False,
        reason="eligible official source",
        policy_id="official-source-policy",
        policy_version="1",
        registry_version="1",
    )


def _collection(
    content: str = "Exact page text.",
    *,
    artifact_id: str = "b" * 64,
    job_id: str = "job-001",
    source_id: str = "source-001",
    source_path: str = "official/specification.pdf",
    source_checksum: str = "a" * 64,
    warnings: tuple[str, ...] = ("warning-a", "warning-a"),
) -> EvidenceCollection:
    snapshot = _snapshot(
        source_id=source_id,
        source_path=source_path,
        source_checksum=source_checksum,
    )
    provenance = TraceableEvidenceProvenance(
        artifact_contract_version="extraction_artifact_contract_v1",
        artifact_id=artifact_id,
        upstream_contract_version="pdf_ingestion_orchestrator_result_contract_v1",
        job_id=job_id,
        source_id=source_id,
        source_path=source_path,
        source_checksum=source_checksum,
        page_index=0,
        page_number=1,
        extraction_index=0,
        extraction_method="pdf_text",
        extraction_status="completed",
        execution_report_location="reports/extraction.txt",
    )
    content_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    snapshot_digest = derive_evidence_eligibility_snapshot_digest(snapshot)

    unchecked_evidence = object.__new__(TraceableEvidence)
    for name, value in (
        ("contract_version", TRACEABLE_EVIDENCE_CONTRACT_VERSION),
        ("evidence_id", TRACEABLE_EVIDENCE_ID_PREFIX + ("0" * 64)),
        ("content_type", TRACEABLE_EVIDENCE_CONTENT_TYPE),
        ("content", content),
        ("content_digest", content_digest),
        ("warnings", warnings),
        ("provenance", provenance),
        ("eligibility_snapshot_digest", snapshot_digest),
    ):
        object.__setattr__(unchecked_evidence, name, value)

    evidence = TraceableEvidence(
        contract_version=TRACEABLE_EVIDENCE_CONTRACT_VERSION,
        evidence_id=derive_traceable_evidence_id(unchecked_evidence),
        content_type=TRACEABLE_EVIDENCE_CONTENT_TYPE,
        content=content,
        content_digest=content_digest,
        warnings=warnings,
        provenance=provenance,
        eligibility_snapshot_digest=snapshot_digest,
    )

    unchecked_collection = object.__new__(EvidenceCollection)
    for name, value in (
        ("contract_version", EVIDENCE_COLLECTION_CONTRACT_VERSION),
        ("collection_id", EVIDENCE_COLLECTION_ID_PREFIX + ("0" * 64)),
        ("artifact_contract_version", "extraction_artifact_contract_v1"),
        ("artifact_id", artifact_id),
        (
            "upstream_contract_version",
            "pdf_ingestion_orchestrator_result_contract_v1",
        ),
        ("job_id", job_id),
        ("source_id", source_id),
        ("source_path", source_path),
        ("source_checksum", source_checksum),
        ("eligibility_snapshot", snapshot),
        ("evidence_items", (evidence,)),
    ):
        object.__setattr__(unchecked_collection, name, value)

    return EvidenceCollection(
        contract_version=EVIDENCE_COLLECTION_CONTRACT_VERSION,
        collection_id=derive_evidence_collection_id(unchecked_collection),
        artifact_contract_version="extraction_artifact_contract_v1",
        artifact_id=artifact_id,
        upstream_contract_version="pdf_ingestion_orchestrator_result_contract_v1",
        job_id=job_id,
        source_id=source_id,
        source_path=source_path,
        source_checksum=source_checksum,
        eligibility_snapshot=snapshot,
        evidence_items=(evidence,),
    )


FIXED_TIME = datetime(2026, 7, 20, 12, 34, 56, 123456, tzinfo=timezone.utc)

import json

import pytest

from rie.evidence_repository.evidence_repository_canonicalization import (
    calculate_evidence_collection_repository_payload_digest,
    calculate_evidence_repository_audit_id,
    calculate_evidence_repository_revision_id,
    deserialize_evidence_collection_repository_payload,
    serialize_evidence_collection_repository_payload,
)


def test_payload_is_deterministic_utf8_without_bom_or_trailing_bytes():
    collection = _collection(content="Teks café 日本語")
    first = serialize_evidence_collection_repository_payload(collection)
    second = serialize_evidence_collection_repository_payload(collection)
    assert first == second
    assert not first.startswith(b"\xef\xbb\xbf")
    assert first.endswith(b"}")
    assert not first.endswith(b"\n")
    assert "Teks café 日本語".encode("utf-8") in first


def test_payload_round_trip_preserves_exact_collection():
    collection = _collection(warnings=("a", "a", "b"))
    payload = serialize_evidence_collection_repository_payload(collection)
    restored = deserialize_evidence_collection_repository_payload(payload)
    assert restored == collection
    assert restored.evidence_items[0].warnings == ("a", "a", "b")


def test_payload_digest_is_lowercase_sha256():
    collection = _collection()
    payload = serialize_evidence_collection_repository_payload(collection)
    digest = calculate_evidence_collection_repository_payload_digest(collection)
    assert digest == hashlib.sha256(payload).hexdigest()
    assert len(digest) == 64
    assert digest == digest.lower()


def test_collection_payload_has_exact_top_level_field_order():
    collection = _collection()
    payload = serialize_evidence_collection_repository_payload(collection)
    parsed = json.loads(payload.decode("utf-8"))
    assert tuple(parsed) == (
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


def test_warning_order_and_duplicates_change_payload_and_identity():
    first = _collection(warnings=("a", "a", "b"))
    second = _collection(warnings=("a", "b", "a"))
    assert first.collection_id != second.collection_id
    assert (
        serialize_evidence_collection_repository_payload(first)
        != serialize_evidence_collection_repository_payload(second)
    )


def test_content_is_not_trimmed_or_normalized():
    first = _collection(content=" café ")
    second = _collection(content="café")
    assert first.collection_id != second.collection_id
    restored = deserialize_evidence_collection_repository_payload(
        serialize_evidence_collection_repository_payload(first)
    )
    assert restored.evidence_items[0].content == " café "


def test_invalid_utf8_is_rejected():
    with pytest.raises(ValueError, match="UTF-8"):
        deserialize_evidence_collection_repository_payload(b"\xff")


def test_duplicate_json_key_is_rejected():
    collection = _collection()
    payload = serialize_evidence_collection_repository_payload(collection)
    forged = payload.replace(
        b'{"contract_version":',
        b'{"contract_version":"duplicate","contract_version":',
        1,
    )
    with pytest.raises(ValueError, match="duplicate"):
        deserialize_evidence_collection_repository_payload(forged)


@pytest.mark.parametrize(
    "mutation",
    (
        lambda value: {key: item for key, item in value.items() if key != "job_id"},
        lambda value: {**value, "unexpected": "field"},
    ),
)
def test_missing_or_extra_fields_are_rejected(mutation):
    collection = _collection()
    parsed = json.loads(
        serialize_evidence_collection_repository_payload(collection)
    )
    forged = json.dumps(
        mutation(parsed),
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    with pytest.raises(ValueError):
        deserialize_evidence_collection_repository_payload(forged)


def test_noncanonical_whitespace_is_rejected():
    collection = _collection()
    parsed = json.loads(
        serialize_evidence_collection_repository_payload(collection)
    )
    forged = json.dumps(parsed, ensure_ascii=False, indent=2).encode("utf-8")
    with pytest.raises(ValueError, match="canonical"):
        deserialize_evidence_collection_repository_payload(forged)


def test_trailing_newline_is_rejected_as_noncanonical():
    collection = _collection()
    payload = serialize_evidence_collection_repository_payload(collection)
    with pytest.raises(ValueError, match="canonical"):
        deserialize_evidence_collection_repository_payload(payload + b"\n")


def test_payload_with_forged_collection_identity_is_rejected():
    collection = _collection()
    parsed = json.loads(
        serialize_evidence_collection_repository_payload(collection)
    )
    parsed["collection_id"] = "evc1_" + ("f" * 64)
    forged = json.dumps(
        parsed,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    with pytest.raises(ValueError, match="identity"):
        deserialize_evidence_collection_repository_payload(forged)


def test_payload_with_forged_evidence_identity_is_rejected():
    collection = _collection()
    parsed = json.loads(
        serialize_evidence_collection_repository_payload(collection)
    )
    parsed["evidence_items"][0]["evidence_id"] = "evm1_" + ("f" * 64)
    forged = json.dumps(
        parsed,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    with pytest.raises(ValueError, match="identity"):
        deserialize_evidence_collection_repository_payload(forged)


def test_revision_identity_is_deterministic_and_source_scoped():
    collection = _collection()
    digest = calculate_evidence_collection_repository_payload_digest(collection)
    first = calculate_evidence_repository_revision_id(
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=digest,
        previous_revision_id=None,
    )
    second = calculate_evidence_repository_revision_id(
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=digest,
        previous_revision_id=None,
    )
    changed = calculate_evidence_repository_revision_id(
        source_id="other-source",
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=digest,
        previous_revision_id=None,
    )
    assert first == second
    assert first.startswith("evr1_")
    assert first != changed


def test_audit_identity_is_deterministic_and_timestamp_bearing():
    collection = _collection()
    digest = calculate_evidence_collection_repository_payload_digest(collection)
    revision_id = calculate_evidence_repository_revision_id(
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        collection_payload_digest=digest,
        previous_revision_id=None,
    )
    first = calculate_evidence_repository_audit_id(
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="reviewer",
        recorded_at_utc=FIXED_TIME,
    )
    second = calculate_evidence_repository_audit_id(
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="reviewer",
        recorded_at_utc=FIXED_TIME,
    )
    changed = calculate_evidence_repository_audit_id(
        action="persisted_revision",
        revision_id=revision_id,
        source_id=collection.source_id,
        revision_number=1,
        collection_id=collection.collection_id,
        actor_id="other-reviewer",
        recorded_at_utc=FIXED_TIME,
    )
    assert first == second
    assert first.startswith("eva1_")
    assert first != changed
