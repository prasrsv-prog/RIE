from __future__ import annotations

import dataclasses

import pytest

from rie.evidence_materialization.atomic_text_evidence_derivation import (
    AtomicTextEvidenceDerivationRequest,
    derive_operator_approved_atomic_text_evidence,
)
from rie.evidence_materialization.evidence_materialization_canonicalization import (
    derive_traceable_evidence_id,
)
from rie.evidence_materialization.evidence_materialization_contract import (
    TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    TRACEABLE_EVIDENCE_CONTENT_TYPE,
    TRACEABLE_EVIDENCE_FIELD_ORDER,
    TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION,
    TraceableEvidence,
    TraceableEvidenceOcrRemediationProvenance,
    TraceableEvidenceProvenance,
)


def _shell(cls, **values):
    value = object.__new__(cls)
    for name, item in values.items():
        object.__setattr__(value, name, item)
    return value


def _approved_parent() -> TraceableEvidence:
    provenance = _shell(
        TraceableEvidenceProvenance,
        artifact_contract_version="extraction_artifact_contract_v2",
        artifact_id="a" * 64,
        upstream_contract_version="upstream-contract-v1",
        job_id="job-ffs21",
        source_id="pilot-rsv-ffs21-product-manual",
        source_path="FFS21.pdf",
        source_checksum="67e7d5f723fd84180bcfcf091dfc16801b3498d95b5caefe8be351aebfc40a82",
        page_index=0,
        page_number=1,
        extraction_index=0,
        extraction_method="ocr",
        extraction_status="extracted",
        execution_report_location="report",
    )
    ocr = _shell(
        TraceableEvidenceOcrRemediationProvenance,
        producer_operation_id="producer-operation",
        producer_artifact_path="artifact.txt",
        producer_artifact_sha256="b" * 64,
        producer_artifact_set_digest="c" * 64,
        extraction_method="ocr",
    )
    return _shell(
        TraceableEvidence,
        contract_version=TRACEABLE_EVIDENCE_OCR_CONTRACT_VERSION,
        evidence_id="evm1_f96022ff4a4718aea695f1f34d7195a24d98053ba389aed8fbd818e014b85238",
        content_type=TRACEABLE_EVIDENCE_CONTENT_TYPE,
        content="prefix " + 'XS is suitable for those who have XS\r\nhead circumference 53-54 cm' + " suffix",
        content_digest="b044cd92773ff4b066cf7505165c47284f55c24e4ff53f5a4e748c0747b98243",
        warnings=(),
        provenance=provenance,
        eligibility_snapshot_digest="d" * 64,
        ocr_remediation_provenance=ocr,
        atomic_text_derivation_provenance=None,
    )


def test_traceable_evidence_published_physical_shape_remains_unchanged() -> None:
    physical_names = tuple(
        field.name for field in dataclasses.fields(TraceableEvidence)
    )
    assert physical_names == TRACEABLE_EVIDENCE_FIELD_ORDER
    assert "atomic_text_derivation_provenance" not in physical_names
    assert (
        "atomic_text_derivation_provenance"
        in TraceableEvidence.__dataclass_fields__
    )


def test_v3_atomic_derivation_is_deterministic_and_identity_bearing() -> None:
    parent = _approved_parent()
    statement = 'XS is suitable for those who have XS\r\nhead circumference 53-54 cm'
    request = AtomicTextEvidenceDerivationRequest(
        parent_traceable_evidence=parent,
        atomic_statement=statement,
        approved_span_text="context " + statement + " context",
        source_span_ids=("span-ffs21-0055", "span-ffs21-0056"),
    )
    first = derive_operator_approved_atomic_text_evidence(request)
    second = derive_operator_approved_atomic_text_evidence(request)
    assert first == second
    assert (
        first.contract_version
        == TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
    )
    assert first.evidence_id == derive_traceable_evidence_id(first)
    assert first.atomic_text_derivation_provenance is not None
    assert first.atomic_text_derivation_provenance.source_span_ids == (
        "span-ffs21-0055",
        "span-ffs21-0056",
    )


def test_scope_rejects_unapproved_statement() -> None:
    parent = _approved_parent()
    with pytest.raises(ValueError):
        AtomicTextEvidenceDerivationRequest(
            parent_traceable_evidence=parent,
            atomic_statement="not approved",
            approved_span_text="not approved",
            source_span_ids=("span-ffs21-0055",),
        )


def test_scope_rejects_wrong_span_ids() -> None:
    parent = _approved_parent()
    statement = 'XS is suitable for those who have XS\r\nhead circumference 53-54 cm'
    with pytest.raises(ValueError):
        AtomicTextEvidenceDerivationRequest(
            parent_traceable_evidence=parent,
            atomic_statement=statement,
            approved_span_text=statement,
            source_span_ids=("span-ffs21-0055",),
        )

def _pr086cq_corrected_l_parent() -> TraceableEvidence:
    parent = _approved_parent()
    object.__setattr__(
        parent,
        "content",
        "prefix L: 59-60, suffix",
    )
    return parent


def test_pr086cq_corrected_l_derivation_uses_explicit_source_omission_proof() -> None:
    parent = _pr086cq_corrected_l_parent()
    request = AtomicTextEvidenceDerivationRequest(
        parent_traceable_evidence=parent,
        atomic_statement="L: 59-60 cm",
        approved_span_text="context L: 59-60, context",
        source_span_ids=("span-ffs21-0056",),
    )
    first = derive_operator_approved_atomic_text_evidence(request)
    second = derive_operator_approved_atomic_text_evidence(request)

    assert first == second
    assert first.content == "L: 59-60 cm"
    assert first.content_digest == "cc2ede60e51f222d69181e92d0107ab600c35f6e214e4ed85c7dc4d045052cc8"
    assert first.atomic_text_derivation_provenance is not None
    assert first.atomic_text_derivation_provenance.source_span_ids == (
        "span-ffs21-0056",
    )
    assert (
        first.atomic_text_derivation_provenance.operator_decision_packet_sha256
        == "5210145e81bd83de277fc4a831291802b0cdc5a763542c36e6342f95beb65d65"
    )
    assert (
        first.atomic_text_derivation_provenance.atomic_statement_sha256
        == "cc2ede60e51f222d69181e92d0107ab600c35f6e214e4ed85c7dc4d045052cc8"
    )


def test_pr086cq_corrected_l_requires_locked_source_span() -> None:
    parent = _pr086cq_corrected_l_parent()
    with pytest.raises(ValueError):
        AtomicTextEvidenceDerivationRequest(
            parent_traceable_evidence=parent,
            atomic_statement="L: 59-60 cm",
            approved_span_text="context L: 59-60, context",
            source_span_ids=("span-ffs21-0057",),
        )


def test_pr086cq_corrected_l_requires_source_literal_in_parent() -> None:
    parent = _approved_parent()
    with pytest.raises(ValueError):
        AtomicTextEvidenceDerivationRequest(
            parent_traceable_evidence=parent,
            atomic_statement="L: 59-60 cm",
            approved_span_text="context L: 59-60, context",
            source_span_ids=("span-ffs21-0056",),
        )


def test_pr086cq_corrected_l_requires_source_literal_in_approved_span() -> None:
    parent = _pr086cq_corrected_l_parent()
    with pytest.raises(ValueError):
        AtomicTextEvidenceDerivationRequest(
            parent_traceable_evidence=parent,
            atomic_statement="L: 59-60 cm",
            approved_span_text="context without corrected source literal",
            source_span_ids=("span-ffs21-0056",),
        )


def test_pr086cq_rejects_unapproved_correction_like_statement() -> None:
    parent = _pr086cq_corrected_l_parent()
    with pytest.raises(ValueError):
        AtomicTextEvidenceDerivationRequest(
            parent_traceable_evidence=parent,
            atomic_statement="L: 59-60 mm",
            approved_span_text="context L: 59-60, context",
            source_span_ids=("span-ffs21-0056",),
        )
