from dataclasses import fields

import pytest

from official_source.official_source import AuthorityStatus
from official_source.official_source import DocumentClassification
from official_source.official_source import EvidenceEligibility
from official_source.official_source import LifecycleStatus
from official_source.official_source import OfficialSource
from official_source.official_source import SourceType


def make_official_source(
    *,
    source_id: str = "SRC-001",
    source_path: str = "docs/example_official_source.pdf",
    source_type: SourceType = SourceType.PDF,
    document_classification: DocumentClassification = (
        DocumentClassification.OFFICIAL_KNOWLEDGE_BASE
    ),
    authority_status: AuthorityStatus = AuthorityStatus.OFFICIAL,
    lifecycle_status: LifecycleStatus = LifecycleStatus.LOCKED,
    evidence_eligibility: EvidenceEligibility = (
        EvidenceEligibility.ELIGIBLE_WITH_REVIEW
    ),
    version: str | None = "v1.0",
    review_notes: str | None = "Reviewed as generic test data.",
) -> OfficialSource:
    return OfficialSource(
        source_id=source_id,
        source_path=source_path,
        source_type=source_type,
        document_classification=document_classification,
        authority_status=authority_status,
        lifecycle_status=lifecycle_status,
        evidence_eligibility=evidence_eligibility,
        version=version,
        review_notes=review_notes,
    )


def test_creates_valid_official_source():
    source = make_official_source()

    assert source.source_id == "SRC-001"
    assert source.source_path == "docs/example_official_source.pdf"
    assert source.source_type == SourceType.PDF
    assert source.document_classification == (
        DocumentClassification.OFFICIAL_KNOWLEDGE_BASE
    )
    assert source.authority_status == AuthorityStatus.OFFICIAL
    assert source.lifecycle_status == LifecycleStatus.LOCKED
    assert source.evidence_eligibility == (
        EvidenceEligibility.ELIGIBLE_WITH_REVIEW
    )
    assert source.version == "v1.0"
    assert source.review_notes == "Reviewed as generic test data."


def test_official_source_enums_expose_expected_values():
    assert SourceType.PDF.value == "pdf"
    assert SourceType.UNKNOWN.value == "unknown"
    assert DocumentClassification.PROJECT_RULEBOOK.value == (
        "project_rulebook"
    )
    assert AuthorityStatus.SOURCE_OF_TRUTH_CANDIDATE.value == (
        "source_of_truth_candidate"
    )
    assert LifecycleStatus.SUPERSEDED.value == "superseded"
    assert EvidenceEligibility.NOT_ELIGIBLE.value == "not_eligible"


def test_source_id_and_source_path_must_be_non_empty_strings():
    for field_name in [
        "source_id",
        "source_path",
    ]:
        with pytest.raises(ValueError, match=field_name):
            make_official_source(**{field_name: ""})


def test_source_path_does_not_need_to_exist():
    source = make_official_source(
        source_path="docs/not-a-real-locked-source.pdf",
    )

    assert source.source_path == "docs/not-a-real-locked-source.pdf"


def test_status_and_classification_fields_must_be_enum_instances():
    invalid_values = {
        "source_type": "pdf",
        "document_classification": "official_knowledge_base",
        "authority_status": "official",
        "lifecycle_status": "locked",
        "evidence_eligibility": "eligible",
    }

    for field_name, value in invalid_values.items():
        with pytest.raises(ValueError, match=field_name):
            make_official_source(**{field_name: value})


def test_optional_metadata_can_be_none():
    source = make_official_source(
        version=None,
        review_notes=None,
    )

    assert source.version is None
    assert source.review_notes is None


def test_optional_metadata_must_be_strings_when_provided():
    for field_name in [
        "version",
        "review_notes",
    ]:
        with pytest.raises(ValueError, match=field_name):
            make_official_source(**{field_name: 1})


def test_official_source_exposes_no_downstream_workflow_fields():
    source = make_official_source()

    assert [field.name for field in fields(source)] == [
        "source_id",
        "source_path",
        "source_type",
        "document_classification",
        "authority_status",
        "lifecycle_status",
        "evidence_eligibility",
        "version",
        "review_notes",
    ]

    forbidden_fields = [
        "content",
        "knowledge_id",
        "official_knowledge_index",
        "evidence_index",
        "prompt",
        "final_prompt",
        "product_type",
        "classification_reason",
        "ai_output",
        "model",
    ]

    for field_name in forbidden_fields:
        assert not hasattr(source, field_name)
