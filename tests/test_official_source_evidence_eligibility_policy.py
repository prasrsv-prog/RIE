from official_source.official_source import AuthorityStatus
from official_source.official_source import DocumentClassification
from official_source.official_source import EvidenceEligibility
from official_source.official_source import LifecycleStatus
from official_source.official_source import OfficialSource
from official_source.official_source import SourceType
from official_source.official_source_evidence_eligibility_policy import (
    OfficialSourceEvidenceEligibilityPolicy,
)


def _source(**overrides) -> OfficialSource:
    values = {
        "source_id": "SRC-SYN-001",
        "source_path": "docs/synthetic-policy-source.pdf",
        "source_type": SourceType.PDF,
        "document_classification": DocumentClassification.PROJECT_RULEBOOK,
        "authority_status": AuthorityStatus.SOURCE_OF_TRUTH_CANDIDATE,
        "lifecycle_status": LifecycleStatus.LOCKED,
        "evidence_eligibility": EvidenceEligibility.ELIGIBLE,
        "version": "v1.0",
        "review_notes": "Synthetic policy test data only.",
    }
    values.update(overrides)
    return OfficialSource(**values)


def _evaluate(source: OfficialSource):
    return OfficialSourceEvidenceEligibilityPolicy.evaluate(source)


def test_eligible_returns_allowed_without_review():
    decision = _evaluate(
        _source(evidence_eligibility=EvidenceEligibility.ELIGIBLE),
    )

    assert decision.allowed is True
    assert decision.requires_review is False
    assert decision.reason


def test_eligible_with_review_returns_blocked_with_review_required():
    decision = _evaluate(
        _source(
            evidence_eligibility=EvidenceEligibility.ELIGIBLE_WITH_REVIEW,
        ),
    )

    assert decision.allowed is False
    assert decision.requires_review is True
    assert decision.reason


def test_not_eligible_returns_blocked_without_review_required():
    decision = _evaluate(
        _source(evidence_eligibility=EvidenceEligibility.NOT_ELIGIBLE),
    )

    assert decision.allowed is False
    assert decision.requires_review is False
    assert decision.reason


def test_unknown_returns_blocked_without_review_required():
    decision = _evaluate(
        _source(evidence_eligibility=EvidenceEligibility.UNKNOWN),
    )

    assert decision.allowed is False
    assert decision.requires_review is False
    assert decision.reason


def test_decision_preserves_source_id():
    decision = _evaluate(_source(source_id="SRC-SYN-999"))

    assert decision.source_id == "SRC-SYN-999"


def test_decision_preserves_evidence_eligibility():
    decision = _evaluate(
        _source(evidence_eligibility=EvidenceEligibility.ELIGIBLE_WITH_REVIEW),
    )

    assert decision.evidence_eligibility == (
        EvidenceEligibility.ELIGIBLE_WITH_REVIEW
    )


def test_lifecycle_status_does_not_change_decision():
    active = _evaluate(
        _source(lifecycle_status=LifecycleStatus.ACTIVE),
    )
    superseded = _evaluate(
        _source(lifecycle_status=LifecycleStatus.SUPERSEDED),
    )

    assert active.allowed == superseded.allowed
    assert active.requires_review == superseded.requires_review


def test_authority_status_does_not_change_decision():
    official = _evaluate(
        _source(authority_status=AuthorityStatus.OFFICIAL),
    )
    draft = _evaluate(
        _source(authority_status=AuthorityStatus.DRAFT),
    )

    assert official.allowed == draft.allowed
    assert official.requires_review == draft.requires_review


def test_source_type_does_not_change_decision():
    pdf = _evaluate(
        _source(source_type=SourceType.PDF),
    )
    markdown = _evaluate(
        _source(source_type=SourceType.MARKDOWN),
    )

    assert pdf.allowed == markdown.allowed
    assert pdf.requires_review == markdown.requires_review


def test_nonexistent_source_path_is_not_checked(tmp_path):
    source_path = tmp_path / "missing-synthetic-source.pdf"

    decision = _evaluate(
        _source(source_path=str(source_path)),
    )

    assert decision.allowed is True


def test_tests_use_synthetic_official_source_only():
    source = _source()

    assert source.source_id.startswith("SRC-SYN-")
    assert "synthetic" in source.source_path
    assert "Synthetic" in source.review_notes
    assert source.source_path.startswith("docs/")
