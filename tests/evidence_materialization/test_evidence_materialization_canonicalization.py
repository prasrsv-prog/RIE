from dataclasses import replace
import hashlib
import json

from rie.evidence_materialization.evidence_materialization_canonicalization import (
    canonicalize_evidence_collection_identity,
    canonicalize_evidence_eligibility_snapshot,
    canonicalize_traceable_evidence_identity,
    derive_evidence_collection_id,
    derive_evidence_eligibility_snapshot_digest,
    derive_traceable_evidence_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
    EvidenceEligibilitySnapshot,
    EvidenceMaterializationStatus,
)
from rie.evidence_materialization.evidence_materialization_service import (
    materialize_evidence_collection,
)
from rie.extraction.extraction_artifact_contract import (
    EXTRACTION_ARTIFACT_CONTRACT_VERSION,
    EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION,
    ExtractionArtifact,
    ExtractionArtifactPageExtraction,
    ExtractionArtifactStructuralMetadata,
    ExtractionArtifactStructuralPage,
)
from rie.extraction.extraction_artifact_serializer import (
    ExtractionArtifactSerializer,
)


def _artifact(
    contents: tuple[str, ...] = ("First", "Second"),
) -> ExtractionArtifact:
    source_path = "controlled/source.pdf"
    pages = tuple(
        ExtractionArtifactStructuralPage(
            page_index=index,
            width_points=612.0,
            height_points=792.0,
            rotation_degrees=0,
            inspection_status="inspected",
        )
        for index in range(len(contents))
    )
    metadata = ExtractionArtifactStructuralMetadata(
        allowed=True,
        reason="Controlled synthetic PDF is allowed.",
        fixture_id="fixture-1",
        source_label="Synthetic source",
        fixture_path=source_path,
        fixture_type="pdf",
        inspection_mode="bounded",
        inspection_status="inspected",
        encrypted=False,
        page_count=len(contents),
        inspected_page_count=len(contents),
        page_details_truncated=False,
        page_details=pages,
        max_inspected_pages=10,
        inspection_error="",
        evidence_allowed=False,
        notes="Gate 5 artifact.",
    )
    extractions = tuple(
        ExtractionArtifactPageExtraction(
            source_path=source_path,
            size_bytes=len(content.encode("utf-8")),
            page_number=index + 1,
            extraction_index=index,
            extraction_method="pypdf",
            content=content,
            warnings=("warning-b", "warning-a", "warning-b"),
        )
        for index, content in enumerate(contents)
    )
    provisional = ExtractionArtifact(
        contract_version=EXTRACTION_ARTIFACT_CONTRACT_VERSION,
        artifact_id="0" * 64,
        upstream_contract_version=(
            EXTRACTION_ARTIFACT_UPSTREAM_CONTRACT_VERSION
        ),
        upstream_status="completed",
        job_id="job-1",
        source_id="source-1",
        source_path=source_path,
        source_checksum="a" * 64,
        structural_metadata=metadata,
        page_extractions=extractions,
        execution_report_location="memory://report",
        cleanup_completed=True,
    )
    return replace(
        provisional,
        artifact_id=ExtractionArtifactSerializer.derive_artifact_id(
            provisional
        ),
    )


def _snapshot(**changes: object) -> EvidenceEligibilitySnapshot:
    values = {
        "contract_version":
            EVIDENCE_ELIGIBILITY_SNAPSHOT_CONTRACT_VERSION,
        "source_id": "source-1",
        "source_path": "controlled/source.pdf",
        "source_checksum": "a" * 64,
        "source_type": "pdf",
        "document_classification": "official_knowledge_base",
        "authority_status": "official",
        "lifecycle_status": "active",
        "evidence_eligibility": "eligible",
        "evidence_collection_allowed": True,
        "requires_review": False,
        "reason": "Sumber layak untuk Evidence.",
        "policy_id": "official-source-evidence-policy",
        "policy_version": "1.0.0",
        "registry_version": "registry-v1",
    }
    values.update(changes)
    return EvidenceEligibilitySnapshot(**values)


def _materialized(
    contents: tuple[str, ...] = ("First", "Second"),
):
    result = materialize_evidence_collection(
        _artifact(contents),
        _snapshot(),
    )
    assert result.status is EvidenceMaterializationStatus.MATERIALIZED
    assert result.collection is not None
    return result.collection


def test_eligibility_canonical_bytes_use_exact_order() -> None:
    canonical = canonicalize_evidence_eligibility_snapshot(_snapshot())
    decoded = json.loads(canonical.decode("utf-8"))
    assert tuple(decoded) == (
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


def test_all_canonical_bytes_have_exact_encoding_shape() -> None:
    collection = _materialized(("Isi halaman",))
    evidence = collection.evidence_items[0]
    values = (
        canonicalize_evidence_eligibility_snapshot(
            collection.eligibility_snapshot
        ),
        canonicalize_traceable_evidence_identity(evidence),
        canonicalize_evidence_collection_identity(collection),
    )
    for value in values:
        assert not value.startswith(b"\xef\xbb\xbf")
        assert b"\r" not in value
        assert value.endswith(b"\n")
        assert not value.endswith(b"\n\n")
        assert b": " not in value
        assert b", " not in value


def test_non_ascii_text_is_preserved_as_utf8() -> None:
    collection = _materialized(("Informasi helm \u00c7ilek",))
    canonical = canonicalize_traceable_evidence_identity(
        collection.evidence_items[0]
    )
    assert "\u00c7ilek".encode("utf-8") in canonical
    assert b"\\u00c7" not in canonical


def test_eligibility_digest_is_lowercase_sha256_and_deterministic() -> None:
    snapshot = _snapshot()
    first = derive_evidence_eligibility_snapshot_digest(snapshot)
    second = derive_evidence_eligibility_snapshot_digest(snapshot)
    assert first == second
    assert first == hashlib.sha256(
        canonicalize_evidence_eligibility_snapshot(snapshot)
    ).hexdigest()
    assert len(first) == 64
    assert first == first.lower()


def test_traceable_evidence_id_matches_canonical_identity() -> None:
    evidence = _materialized(("Text",)).evidence_items[0]
    expected = "evm1_" + hashlib.sha256(
        canonicalize_traceable_evidence_identity(evidence)
    ).hexdigest()
    assert evidence.evidence_id == expected
    assert derive_traceable_evidence_id(evidence) == expected


def test_collection_id_matches_canonical_identity() -> None:
    collection = _materialized(("One", "Two"))
    expected = "evc1_" + hashlib.sha256(
        canonicalize_evidence_collection_identity(collection)
    ).hexdigest()
    assert collection.collection_id == expected
    assert derive_evidence_collection_id(collection) == expected


def test_repeated_materialization_has_equal_canonical_bytes_and_ids() -> None:
    first = _materialized(("One", "Two"))
    second = _materialized(("One", "Two"))
    assert first == second
    assert first.collection_id == second.collection_id
    assert canonicalize_evidence_collection_identity(
        first
    ) == canonicalize_evidence_collection_identity(second)


def test_content_change_changes_evidence_and_collection_ids() -> None:
    first = _materialized(("One",))
    second = _materialized(("Changed",))
    assert (
        first.evidence_items[0].evidence_id
        != second.evidence_items[0].evidence_id
    )
    assert first.collection_id != second.collection_id


def test_warning_order_and_duplicates_affect_identity() -> None:
    artifact = _artifact(("One",))
    extraction = artifact.page_extractions[0]
    changed_extraction = replace(
        extraction,
        warnings=("warning-a", "warning-b", "warning-b"),
    )
    provisional = replace(
        artifact,
        artifact_id="0" * 64,
        page_extractions=(changed_extraction,),
    )
    changed_artifact = replace(
        provisional,
        artifact_id=ExtractionArtifactSerializer.derive_artifact_id(
            provisional
        ),
    )
    first = materialize_evidence_collection(artifact, _snapshot())
    second = materialize_evidence_collection(changed_artifact, _snapshot())
    assert first.collection is not None
    assert second.collection is not None
    assert (
        first.collection.evidence_items[0].evidence_id
        != second.collection.evidence_items[0].evidence_id
    )


def test_empty_content_has_sha256_of_empty_utf8_bytes() -> None:
    evidence = _materialized(("",)).evidence_items[0]
    assert evidence.content == ""
    assert evidence.content_digest == hashlib.sha256(b"").hexdigest()


def test_zero_page_collection_has_deterministic_identity() -> None:
    first = _materialized(())
    second = _materialized(())
    assert first.evidence_items == ()
    assert first.collection_id == second.collection_id

# PR-086K-D34 dual-version canonicalization tests.
def test_d34_v1_canonical_bytes_omit_ocr_and_v2_include_ocr() -> None:
    from dataclasses import replace
    import rie.extraction.extraction_artifact_contract as gate5
    import rie.evidence_materialization.evidence_materialization_contract as gate6

    legacy = _materialized(("Legacy",))
    legacy_bytes = canonicalize_traceable_evidence_identity(
        legacy.evidence_items[0]
    )
    assert b'"ocr_remediation_provenance"' not in legacy_bytes

    provenance = gate5.ExtractionArtifactOcrRemediationProvenance(
        producer_operation_id="PR_086K_D27_REAL_RSV_ASSET_PILOT_BOUNDED_PDF_IMAGE_TEXT_EXTRACTION_EXECUTION",
        producer_artifact_path="memory://ocr-index",
        producer_artifact_sha256="a" * 64,
        producer_artifact_set_digest="b" * 64,
        extraction_method="bounded_local_ocr",
    )
    base = _artifact(("D34 OCR text",))
    provisional = replace(
        base,
        contract_version=gate5.EXTRACTION_ARTIFACT_OCR_CONTRACT_VERSION,
        artifact_id="0" * 64,
        ocr_remediation_provenance=provenance,
    )
    artifact = replace(
        provisional,
        artifact_id=ExtractionArtifactSerializer.derive_artifact_id(
            provisional
        ),
    )
    result = materialize_evidence_collection(artifact, _snapshot())
    assert result.collection is not None
    evidence = result.collection.evidence_items[0]
    assert evidence.contract_version == (
        gate6.TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION
    )
    first = canonicalize_traceable_evidence_identity(evidence)
    second = canonicalize_traceable_evidence_identity(evidence)
    assert first == second
    assert b'"ocr_remediation_provenance"' in first

# PR-086EW structured-metadata v4 canonical identity coverage.
def test_pr086ew_structured_metadata_v4_identity_has_no_page_provenance() -> None:
    import hashlib

    from rie.evidence_materialization.evidence_materialization_canonicalization import (
        derive_traceable_evidence_id,
    )
    from rie.evidence_materialization.evidence_materialization_contract import (
        TRACEABLE_EVIDENCE_ID_PREFIX,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE,
        TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION,
        TraceableEvidence,
        TraceableEvidenceStructuredMetadataProvenance,
    )

    content = '{"atomic_knowledge_id":"atomic-1"}\n'
    provenance = TraceableEvidenceStructuredMetadataProvenance(
        contract_version=TRACEABLE_EVIDENCE_STRUCTURED_METADATA_PROVENANCE_CONTRACT_VERSION,
        payload_type="product_variant_identity_structured_metadata",
        payload_schema_version="1.0.0",
        locator_type="atomic_knowledge_id",
        locator_value="atomic-1",
        locator_schema_version="1.0.0",
        atomic_knowledge_id="atomic-1",
        source_relative_paths=("official/a.jpg",),
        manifest_sha256="a" * 64,
        identity_capture_sha256="b" * 64,
        atomic_construction_authority_decision_packet_sha256="c" * 64,
        downstream_binding_policy_decision_packet_sha256="d" * 64,
        admission_payload_digest=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )
    value = object.__new__(TraceableEvidence)
    object.__setattr__(value, "contract_version", TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTRACT_VERSION)
    object.__setattr__(value, "evidence_id", TRACEABLE_EVIDENCE_ID_PREFIX + ("0" * 64))
    object.__setattr__(value, "content_type", TRACEABLE_EVIDENCE_STRUCTURED_METADATA_CONTENT_TYPE)
    object.__setattr__(value, "content", content)
    object.__setattr__(value, "content_digest", hashlib.sha256(content.encode("utf-8")).hexdigest())
    object.__setattr__(value, "warnings", ())
    object.__setattr__(value, "provenance", provenance)
    object.__setattr__(value, "eligibility_snapshot_digest", "f" * 64)
    object.__setattr__(value, "ocr_remediation_provenance", None)
    object.__setattr__(value, "atomic_text_derivation_provenance", None)

    first = derive_traceable_evidence_id(value)
    second = derive_traceable_evidence_id(value)
    assert first == second
    assert first.startswith(TRACEABLE_EVIDENCE_ID_PREFIX)
