from __future__ import annotations

from dataclasses import dataclass
import hashlib

from .evidence_materialization_canonicalization import (
    derive_traceable_evidence_id,
)
from .evidence_materialization_contract import (
    TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    TraceableEvidence,
    TraceableEvidenceAtomicTextDerivationProvenance,
)

ATOMIC_TEXT_DERIVATION_PROVENANCE_CONTRACT_VERSION = "traceable_evidence_atomic_text_derivation_provenance_v1"
ATOMIC_TEXT_DERIVATION_TYPE = "operator_approved_verbatim_atomic_text"
APPROVED_PARENT_TRACEABLE_EVIDENCE_ID = "evm1_f96022ff4a4718aea695f1f34d7195a24d98053ba389aed8fbd818e014b85238"
APPROVED_PARENT_CONTENT_DIGEST = "b044cd92773ff4b066cf7505165c47284f55c24e4ff53f5a4e748c0747b98243"
APPROVED_PARENT_SOURCE_ID = "pilot-rsv-ffs21-product-manual"
APPROVED_PARENT_SOURCE_CHECKSUM = "67e7d5f723fd84180bcfcf091dfc16801b3498d95b5caefe8be351aebfc40a82"
APPROVED_OPERATOR_DECISION_PACKET_SHA256 = "5210145e81bd83de277fc4a831291802b0cdc5a763542c36e6342f95beb65d65"

_APPROVED_STATEMENT_SHA256_TO_SOURCE_SPAN_IDS = {
    '45cb06fea0f3fc355e88b8b3067e1f2ba998568e90f0d98a43e09a90e07dbb60': ('span-ffs21-0055', 'span-ffs21-0056'),
    '07ca18fe06f1765c0ad87713e72db50dc77ac0c41bd98787962213c1d9fb7e61': ('span-ffs21-0056',),
    '85788ad3dc64769b944d7e3c21e6a76759f75846419f825bdde0e45fcee939f6': ('span-ffs21-0056',),
    '58523f0092c93ed26e52385a1dc22ed6f8305a391ebd946d3a4bbdd371934efe': ('span-ffs21-0057',),
    '0aebb4a3fd1030a553c05506ea890467071285d6f30c8a524d1e44e08b0f0f72': ('span-ffs21-0057',),
}

_CORRECTED_L_OPERATOR_STATEMENT_SHA256 = "cc2ede60e51f222d69181e92d0107ab600c35f6e214e4ed85c7dc4d045052cc8"
_CORRECTED_L_SOURCE_LITERAL = "L: 59-60,"
_CORRECTED_L_SOURCE_SPAN_IDS = ("span-ffs21-0056",)

_APPROVED_CORRECTED_STATEMENT_SHA256_TO_SOURCE_PROOF = {
    _CORRECTED_L_OPERATOR_STATEMENT_SHA256: (
        _CORRECTED_L_SOURCE_LITERAL,
        _CORRECTED_L_SOURCE_SPAN_IDS,
    ),
}


@dataclass(frozen=True)
class AtomicTextEvidenceDerivationRequest:
    parent_traceable_evidence: TraceableEvidence
    atomic_statement: str
    approved_span_text: str
    source_span_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.parent_traceable_evidence) is not TraceableEvidence:
            raise TypeError(
                "parent_traceable_evidence must be exact TraceableEvidence"
            )
        if type(self.atomic_statement) is not str or not self.atomic_statement:
            raise ValueError("atomic_statement must be non-empty text")
        if (
            type(self.approved_span_text) is not str
            or not self.approved_span_text
        ):
            raise ValueError("approved_span_text must be non-empty text")
        if type(self.source_span_ids) is not tuple or not self.source_span_ids:
            raise ValueError("source_span_ids must be a non-empty tuple")

        parent = self.parent_traceable_evidence
        if parent.evidence_id != APPROVED_PARENT_TRACEABLE_EVIDENCE_ID:
            raise ValueError("parent TraceableEvidence id is not approved")
        if parent.content_digest != APPROVED_PARENT_CONTENT_DIGEST:
            raise ValueError("parent content digest is not approved")
        if parent.provenance.source_id != APPROVED_PARENT_SOURCE_ID:
            raise ValueError("parent source id is not approved")
        if parent.provenance.source_checksum != APPROVED_PARENT_SOURCE_CHECKSUM:
            raise ValueError("parent source checksum is not approved")

        statement_sha256 = hashlib.sha256(
            self.atomic_statement.encode("utf-8")
        ).hexdigest()
        expected_span_ids = (
            _APPROVED_STATEMENT_SHA256_TO_SOURCE_SPAN_IDS.get(
                statement_sha256
            )
        )
        if expected_span_ids is not None:
            if self.source_span_ids != expected_span_ids:
                raise ValueError("source_span_ids do not match approved fact")
            if parent.content.count(self.atomic_statement) != 1:
                raise ValueError(
                    "atomic statement must occur exactly once in approved parent"
                )
            if self.approved_span_text.count(self.atomic_statement) != 1:
                raise ValueError(
                    "atomic statement must occur exactly once in approved span text"
                )
            return

        correction_proof = (
            _APPROVED_CORRECTED_STATEMENT_SHA256_TO_SOURCE_PROOF.get(
                statement_sha256
            )
        )
        if correction_proof is None:
            raise ValueError("atomic statement is outside approved fact scope")

        source_literal, corrected_span_ids = correction_proof
        if self.source_span_ids != corrected_span_ids:
            raise ValueError("source_span_ids do not match approved correction")
        if parent.content.count(source_literal) != 1:
            raise ValueError(
                "corrected source literal must occur exactly once in approved parent"
            )
        if self.approved_span_text.count(source_literal) != 1:
            raise ValueError(
                "corrected source literal must occur exactly once in approved span text"
            )


def _provisional_v3(
    *,
    parent: TraceableEvidence,
    atomic_statement: str,
    atomic_statement_sha256: str,
    provenance: TraceableEvidenceAtomicTextDerivationProvenance,
) -> TraceableEvidence:
    value = object.__new__(TraceableEvidence)
    object.__setattr__(
        value,
        "contract_version",
        TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION,
    )
    object.__setattr__(value, "evidence_id", "evm1_" + ("0" * 64))
    object.__setattr__(value, "content_type", parent.content_type)
    object.__setattr__(value, "content", atomic_statement)
    object.__setattr__(value, "content_digest", atomic_statement_sha256)
    object.__setattr__(value, "warnings", parent.warnings)
    object.__setattr__(value, "provenance", parent.provenance)
    object.__setattr__(
        value,
        "eligibility_snapshot_digest",
        parent.eligibility_snapshot_digest,
    )
    object.__setattr__(
        value,
        "ocr_remediation_provenance",
        parent.ocr_remediation_provenance,
    )
    object.__setattr__(
        value,
        "atomic_text_derivation_provenance",
        provenance,
    )
    return value


def derive_operator_approved_atomic_text_evidence(
    request: AtomicTextEvidenceDerivationRequest,
) -> TraceableEvidence:
    if type(request) is not AtomicTextEvidenceDerivationRequest:
        raise TypeError(
            "request must be exact AtomicTextEvidenceDerivationRequest"
        )
    request.__post_init__()

    parent = request.parent_traceable_evidence
    atomic_statement_sha256 = hashlib.sha256(
        request.atomic_statement.encode("utf-8")
    ).hexdigest()
    provenance = TraceableEvidenceAtomicTextDerivationProvenance(
        contract_version=(
            ATOMIC_TEXT_DERIVATION_PROVENANCE_CONTRACT_VERSION
        ),
        derivation_type=ATOMIC_TEXT_DERIVATION_TYPE,
        parent_traceable_evidence_id=parent.evidence_id,
        parent_content_digest=parent.content_digest,
        source_span_ids=request.source_span_ids,
        operator_decision_packet_sha256=(
            APPROVED_OPERATOR_DECISION_PACKET_SHA256
        ),
        atomic_statement_sha256=atomic_statement_sha256,
    )
    provisional = _provisional_v3(
        parent=parent,
        atomic_statement=request.atomic_statement,
        atomic_statement_sha256=atomic_statement_sha256,
        provenance=provenance,
    )
    evidence_id = derive_traceable_evidence_id(provisional)

    return TraceableEvidence(
        contract_version=(
            TRACEABLE_EVIDENCE_ATOMIC_TEXT_DERIVATION_CONTRACT_VERSION
        ),
        evidence_id=evidence_id,
        content_type=parent.content_type,
        content=request.atomic_statement,
        content_digest=atomic_statement_sha256,
        warnings=parent.warnings,
        provenance=parent.provenance,
        eligibility_snapshot_digest=parent.eligibility_snapshot_digest,
        ocr_remediation_provenance=parent.ocr_remediation_provenance,
        atomic_text_derivation_provenance=provenance,
    )
