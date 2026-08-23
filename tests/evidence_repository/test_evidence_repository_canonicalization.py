
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

# PR-086K-D39 synthetic v2 repository compatibility fixture.
def _pr086k_d39_v2_collection():
    import hashlib as _d39_hashlib

    from rie.evidence_materialization.evidence_materialization_canonicalization import (
        derive_evidence_collection_id as _d39_derive_collection_id,
        derive_evidence_eligibility_snapshot_digest as _d39_derive_snapshot_digest,
        derive_traceable_evidence_id as _d39_derive_evidence_id,
    )
    from rie.evidence_materialization.evidence_materialization_contract import (
        EVIDENCE_COLLECTION_OCR_CONTRACT_VERSION as _D39_COLLECTION_V2,
        EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION as _D39_SNAPSHOT_V1,
        TRACEABLE_EVIDENCE_CONTENT_TYPE as _D39_CONTENT_TYPE,
        TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION as _D39_TRACEABLE_V2,
        EvidenceCollection as _D39_EvidenceCollection,
        EvidenceEligibilitySnapshot as _D39_Snapshot,
        TraceableEvidence as _D39_TraceableEvidence,
        TraceableEvidenceOcrRemediationProvenance as _D39_OcrProvenance,
        TraceableEvidenceProvenance as _D39_Provenance,
    )

    snapshot = _D39_Snapshot(
        contract_version=_D39_SNAPSHOT_V1,
        source_id="d39-source",
        source_path="synthetic-d39.pdf",
        source_checksum="a" * 64,
        source_type="pdf",
        document_classification="product_manual",
        authority_status="approved",
        lifecycle_status="locked",
        evidence_eligibility="eligible",
        evidence_collection_allowed=True,
        requires_review=False,
        reason="D39 synthetic eligible source.",
        policy_id="d39-synthetic-policy",
        policy_version="1.0.0",
        registry_version="d39-registry-v1",
    )
    provenance = _D39_Provenance(
        artifact_contract_version="extraction_artifact_contract_v2",
        artifact_id="b" * 64,
        upstream_contract_version="controlled_pdf_text_extraction_result_v1",
        job_id="d39-job",
        source_id=snapshot.source_id,
        source_path=snapshot.source_path,
        source_checksum=snapshot.source_checksum,
        page_index=0,
        page_number=1,
        extraction_index=0,
        extraction_method="bounded_local_ocr",
        extraction_status="completed",
        execution_report_location="report://d39",
    )
    ocr = _D39_OcrProvenance(
        producer_operation_id=(
            "PR_086K_D27_REAL_RSV_ASSET_PILOT_BOUNDED_PDF_IMAGE_TEXT_"
            "EXTRACTION_EXECUTION"
        ),
        producer_artifact_path=(
            r"C:\Users\Kreatif Kris\Downloads\RCIS-RSV-Real-Asset-Pilot-01-"
            r"Intake\pilot-bounded-pdf-image-text-extraction-state\ocr-"
            r"extraction-index.json"
        ),
        producer_artifact_sha256=(
            "d509a7d6337f332038e9a37a42b0855b68762b7cfd15cbd1a34190ba74382ee4"
        ),
        producer_artifact_set_digest=(
            "a36604df0195d6a213a5bbd8e69c1e1726f56f64f8d280935c8b57681fd43264"
        ),
        extraction_method="bounded_local_ocr",
    )

    content = "D39 synthetic repository v2 evidence"
    evidence_values = {
        "contract_version": _D39_TRACEABLE_V2,
        "evidence_id": "evm1_" + "0" * 64,
        "content_type": _D39_CONTENT_TYPE,
        "content": content,
        "content_digest": _d39_hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "warnings": (),
        "provenance": provenance,
        "eligibility_snapshot_digest": _d39_derive_snapshot_digest(snapshot),
    }
    provisional_evidence = object.__new__(_D39_TraceableEvidence)
    for _name, _value in evidence_values.items():
        object.__setattr__(provisional_evidence, _name, _value)
    object.__setattr__(
        provisional_evidence,
        "ocr_remediation_provenance",
        ocr,
    )
    evidence_values["evidence_id"] = _d39_derive_evidence_id(
        provisional_evidence
    )
    evidence = _D39_TraceableEvidence(
        **evidence_values,
        ocr_remediation_provenance=ocr,
    )

    collection_values = {
        "contract_version": _D39_COLLECTION_V2,
        "collection_id": "evc1_" + "0" * 64,
        "artifact_contract_version": provenance.artifact_contract_version,
        "artifact_id": provenance.artifact_id,
        "upstream_contract_version": provenance.upstream_contract_version,
        "job_id": provenance.job_id,
        "source_id": snapshot.source_id,
        "source_path": snapshot.source_path,
        "source_checksum": snapshot.source_checksum,
        "eligibility_snapshot": snapshot,
        "evidence_items": (evidence,),
    }
    provisional_collection = object.__new__(_D39_EvidenceCollection)
    for _name, _value in collection_values.items():
        object.__setattr__(provisional_collection, _name, _value)
    collection_values["collection_id"] = _d39_derive_collection_id(
        provisional_collection
    )
    return _D39_EvidenceCollection(**collection_values)

def test_pr086k_d39_v2_repository_payload_roundtrip_is_exact_and_canonical():
    import hashlib as _d39_hashlib
    import json as _d39_json

    from rie.evidence_materialization.evidence_materialization_contract import (
        EVIDENCE_COLLECTION_FIELD_ORDER as _D39_COLLECTION_FIELDS,
        TRACEABLE_EVIDENCE_OCR_FIELD_ORDER as _D39_EVIDENCE_FIELDS,
        TRACEABLE_EVIDENCE_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER as _D39_OCR_FIELDS,
    )
    from rie.evidence_repository.evidence_repository_canonicalization import (
        calculate_evidence_collection_repository_payload_digest as _d39_digest,
        deserialize_evidence_collection_repository_payload as _d39_deserialize,
        serialize_evidence_collection_repository_payload as _d39_serialize,
    )

    collection = _pr086k_d39_v2_collection()
    payload = _d39_serialize(collection)
    restored = _d39_deserialize(payload)

    assert restored == collection
    assert getattr(
        restored.evidence_items[0],
        "ocr_remediation_provenance",
    ) == getattr(
        collection.evidence_items[0],
        "ocr_remediation_provenance",
    )
    assert _d39_serialize(restored) == payload
    assert _d39_digest(collection) == _d39_hashlib.sha256(payload).hexdigest()

    raw = _d39_json.loads(payload.decode("utf-8"))
    assert tuple(raw) == _D39_COLLECTION_FIELDS
    assert tuple(raw["evidence_items"][0]) == _D39_EVIDENCE_FIELDS
    assert tuple(
        raw["evidence_items"][0]["ocr_remediation_provenance"]
    ) == _D39_OCR_FIELDS

# PR-086BL synthetic v3 compatibility fixture.
def _pr086bl_v3_collection(*, reverse=False):
    import hashlib as _bl_hashlib

    from rie.evidence_materialization.evidence_materialization_canonicalization import (
        derive_evidence_collection_id as _bl_derive_collection_id,
        derive_traceable_evidence_id as _bl_derive_evidence_id,
    )
    from rie.evidence_materialization.evidence_materialization_contract import (
        EVIDENCE_COLLECTION_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION as _BL_COLLECTION_V3,
        TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION as _BL_TRACEABLE_V3,
        TRACEABLE_EVIDENCE_CONTENT_TYPE as _BL_CONTENT_TYPE,
        EvidenceCollection as _BL_Collection,
        TraceableEvidence as _BL_Evidence,
        TraceableEvidenceAtomicTextDerivationProvenance as _BL_AtomicProvenance,
    )

    base = _pr086k_d39_v2_collection()
    parent = base.evidence_items[0]
    items = []

    for content in ("S: 55-56 cm", "M: 57-58 cm"):
        content_digest = _bl_hashlib.sha256(content.encode("utf-8")).hexdigest()
        atomic = _BL_AtomicProvenance(
            contract_version="traceable_evidence_atomic_text_derivation_provenance_v1",
            derivation_type="operator_approved_verbatim_atomic_text",
            parent_traceable_evidence_id=parent.evidence_id,
            parent_content_digest=parent.content_digest,
            source_span_ids=("span-ffs21-0056",),
            operator_decision_packet_sha256="a" * 64,
            atomic_statement_sha256=content_digest,
        )
        values = {
            "contract_version": _BL_TRACEABLE_V3,
            "evidence_id": "evm1_" + "0" * 64,
            "content_type": _BL_CONTENT_TYPE,
            "content": content,
            "content_digest": content_digest,
            "warnings": parent.warnings,
            "provenance": parent.provenance,
            "eligibility_snapshot_digest": parent.eligibility_snapshot_digest,
            "ocr_remediation_provenance": parent.ocr_remediation_provenance,
            "atomic_text_derivation_provenance": atomic,
        }
        provisional = object.__new__(_BL_Evidence)
        for name, value in values.items():
            object.__setattr__(provisional, name, value)
        values["evidence_id"] = _bl_derive_evidence_id(provisional)
        items.append(_BL_Evidence(**values))

    if reverse:
        items.reverse()

    collection_values = {
        "contract_version": _BL_COLLECTION_V3,
        "collection_id": "evc1_" + "0" * 64,
        "artifact_contract_version": base.artifact_contract_version,
        "artifact_id": base.artifact_id,
        "upstream_contract_version": base.upstream_contract_version,
        "job_id": base.job_id,
        "source_id": base.source_id,
        "source_path": base.source_path,
        "source_checksum": base.source_checksum,
        "eligibility_snapshot": base.eligibility_snapshot,
        "evidence_items": tuple(items),
    }
    provisional_collection = object.__new__(_BL_Collection)
    for name, value in collection_values.items():
        object.__setattr__(provisional_collection, name, value)
    collection_values["collection_id"] = _bl_derive_collection_id(
        provisional_collection
    )
    return _BL_Collection(**collection_values)

def test_pr086bl_v3_repository_payload_roundtrip_is_exact_and_json_v1_is_preserved():
    import hashlib as _bl_hashlib
    import json as _bl_json

    from rie.evidence_materialization.evidence_materialization_contract import (
        EVIDENCE_COLLECTION_FIELD_ORDER as _BL_COLLECTION_FIELDS,
        TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_FIELD_ORDER as _BL_EVIDENCE_FIELDS,
        TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_PROVENANCE_FIELD_ORDER as _BL_ATOMIC_FIELDS,
        TRACEABLE_EVIDENCE_OCR_REMEDIATION_PROVENANCE_FIELD_ORDER as _BL_OCR_FIELDS,
    )
    from rie.evidence_repository.evidence_repository_canonicalization import (
        calculate_evidence_collection_repository_payload_digest as _bl_digest,
        deserialize_evidence_collection_repository_payload as _bl_deserialize,
        serialize_evidence_collection_repository_payload as _bl_serialize,
    )
    from rie.evidence_repository.evidence_repository_contract import (
        EVIDENCE_COLLECTION_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION as _BL_PAYLOAD_VERSION,
    )

    collection = _pr086bl_v3_collection()
    payload = _bl_serialize(collection)
    restored = _bl_deserialize(payload)

    assert _BL_PAYLOAD_VERSION == "evidence_collection_repository_payload_json_v1"
    assert restored == collection
    assert _bl_serialize(restored) == payload
    assert _bl_digest(collection) == _bl_hashlib.sha256(payload).hexdigest()
    assert tuple(item.provenance.page_index for item in restored.evidence_items) == (0, 0)

    raw = _bl_json.loads(payload.decode("utf-8"))
    assert tuple(raw) == _BL_COLLECTION_FIELDS
    assert tuple(raw["evidence_items"][0]) == _BL_EVIDENCE_FIELDS
    assert tuple(raw["evidence_items"][0]["ocr_remediation_provenance"]) == _BL_OCR_FIELDS
    assert tuple(raw["evidence_items"][0]["atomic_text_derivation_provenance"]) == _BL_ATOMIC_FIELDS


def test_pr086bl_v3_caller_item_order_changes_collection_identity_and_payload():
    from rie.evidence_repository.evidence_repository_canonicalization import (
        serialize_evidence_collection_repository_payload as _bl_serialize,
    )

    first = _pr086bl_v3_collection()
    second = _pr086bl_v3_collection(reverse=True)
    assert first.collection_id != second.collection_id
    assert _bl_serialize(first) != _bl_serialize(second)

# PR-086EW repository v4 route publication coverage.
def test_pr086ew_repository_v4_route_is_published_without_replacing_old_routes() -> None:
    import inspect

    import rie.evidence_repository.evidence_repository_canonicalization as module

    serializer = inspect.getsource(module.serialize_evidence_collection_repository_payload)
    deserializer = inspect.getsource(module.deserialize_evidence_collection_repository_payload)
    assert "evidence_collection_contract_v4" in deserializer
    assert "_EVIDENCE_COLLECTION_STRUCTURED_METADATA_CONTRACT_VERSION" in serializer
    assert "evidence_collection_contract_v3" in deserializer
    assert "evidence_collection_contract_v2" in deserializer
