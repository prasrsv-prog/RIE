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
