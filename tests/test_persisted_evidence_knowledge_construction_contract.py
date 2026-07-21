from dataclasses import FrozenInstanceError, MISSING, fields

import pytest

from rie.application.knowledge_constructor import KnowledgeConstructionResult
from rie.persisted_evidence_knowledge_construction import (
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_DIGEST_ALGORITHM,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_IDENTITY_CANONICALIZATION_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_ID_PREFIX,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CODES,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CONTRACT_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED,
    PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED,
    PersistedEvidenceKnowledgeCompatibilityRecord,
    PersistedEvidenceKnowledgeConstructionIssue,
    PersistedEvidenceKnowledgeConstructionRequest,
    PersistedEvidenceKnowledgeConstructionResult,
    derive_persisted_evidence_knowledge_compatibility_record_id,
)
from rie.persisted_evidence_knowledge_construction import (
    persisted_evidence_knowledge_construction_contract as contract_module,
)


REQUEST_FIELDS = (
    "contract_version",
    "repository_lookup_result",
    "target_evidence_id",
    "knowledge_construction_request",
    "compatibility_policy_id",
    "compatibility_policy_version",
)
RECORD_FIELDS = (
    "contract_version",
    "compatibility_record_id",
    "repository_revision_id",
    "source_id",
    "revision_number",
    "previous_revision_id",
    "collection_id",
    "collection_payload_digest",
    "repository_audit_id",
    "traceable_evidence_id",
    "accepted_evidence_id",
    "acceptance_record_ids",
    "construction_rule_id",
    "construction_rule_version",
    "compatibility_policy_id",
    "compatibility_policy_version",
)
RESULT_FIELDS = (
    "contract_version",
    "status",
    "mutation_performed",
    "compatibility_record",
    "knowledge_construction_result",
    "issue",
)
ISSUE_FIELDS = ("code", "message")


def _identity_values(**changes: object) -> dict[str, object]:
    values: dict[str, object] = {
        "contract_version": (
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION
        ),
        "repository_revision_id": "evr1_" + "1" * 64,
        "source_id": "source-1",
        "revision_number": 1,
        "previous_revision_id": None,
        "collection_id": "evc1_" + "2" * 64,
        "collection_payload_digest": "3" * 64,
        "repository_audit_id": "eva1_" + "4" * 64,
        "traceable_evidence_id": "evm1_" + "5" * 64,
        "accepted_evidence_id": "ev1_" + "6" * 64,
        "acceptance_record_ids": (
            "ar1_" + "7" * 64,
            "ar1_" + "8" * 64,
        ),
        "construction_rule_id": "rcis-accepted-text-verbatim",
        "construction_rule_version": "1.0.0",
        "compatibility_policy_id": (
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID
        ),
        "compatibility_policy_version": (
            PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION
        ),
    }
    values.update(changes)
    return values


def _record(**changes: object) -> PersistedEvidenceKnowledgeCompatibilityRecord:
    values = _identity_values()
    values.update(changes)
    record_id = (
        derive_persisted_evidence_knowledge_compatibility_record_id(**values)
    )
    return PersistedEvidenceKnowledgeCompatibilityRecord(
        compatibility_record_id=record_id,
        **values,
    )


def _nested_result(decision: str) -> KnowledgeConstructionResult:
    result = object.__new__(KnowledgeConstructionResult)
    object.__setattr__(result, "decision", decision)
    object.__setattr__(result, "knowledge_candidate", None)
    object.__setattr__(
        result,
        "reason_codes",
        () if decision == "constructed" else ("reason",),
    )
    object.__setattr__(result, "diagnostics", ())
    return result


def _issue(code: str) -> PersistedEvidenceKnowledgeConstructionIssue:
    return contract_module._issue(code)


def test_contract_constants_are_exact() -> None:
    assert (
        PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
        == "persisted_evidence_knowledge_construction_request_contract_v1"
    )
    assert (
        PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION
        == "persisted_evidence_knowledge_compatibility_record_contract_v1"
    )
    assert (
        PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        == "persisted_evidence_knowledge_construction_result_contract_v1"
    )
    assert (
        PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CONTRACT_VERSION
        == "persisted_evidence_knowledge_construction_issue_contract_v1"
    )
    assert (
        PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_IDENTITY_CANONICALIZATION_VERSION
        == "persisted_evidence_knowledge_compatibility_identity_json_v1"
    )
    assert PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_ID_PREFIX == "pekc1_"
    assert (
        PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID
        == "rcis-persisted-evidence-knowledge-compatibility"
    )
    assert PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION == "1.0.0"
    assert PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_DIGEST_ALGORITHM == "sha256"
    assert PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED == "constructed"
    assert PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED == "rejected"


def test_issue_codes_are_exact_and_in_failure_precedence_order() -> None:
    assert PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CODES == (
        "invalid_request",
        "unsupported_contract_version",
        "unsupported_compatibility_policy",
        "invalid_repository_lookup_result",
        "repository_lookup_not_found",
        "repository_lookup_rejected",
        "repository_linkage_mismatch",
        "repository_identity_mismatch",
        "collection_payload_digest_mismatch",
        "target_evidence_not_found",
        "target_evidence_identity_mismatch",
        "ineligible_evidence",
        "accepted_evidence_identity_mismatch",
        "acceptance_record_identity_mismatch",
        "evidence_compatibility_mismatch",
        "knowledge_construction_rejected",
        "internal_contract_violation",
    )


@pytest.mark.parametrize(
    ("contract_type", "expected_fields"),
    (
        (PersistedEvidenceKnowledgeConstructionRequest, REQUEST_FIELDS),
        (PersistedEvidenceKnowledgeCompatibilityRecord, RECORD_FIELDS),
        (PersistedEvidenceKnowledgeConstructionResult, RESULT_FIELDS),
        (PersistedEvidenceKnowledgeConstructionIssue, ISSUE_FIELDS),
    ),
)
def test_public_dataclass_field_order_and_no_defaults_are_exact(
    contract_type: type[object],
    expected_fields: tuple[str, ...],
) -> None:
    contract_fields = fields(contract_type)
    assert tuple(field.name for field in contract_fields) == expected_fields
    assert all(
        field.default is MISSING and field.default_factory is MISSING
        for field in contract_fields
    )
    assert contract_type.__dataclass_params__.frozen is True


def test_fixed_issue_messages_are_not_caller_controlled() -> None:
    observed = tuple(_issue(code).message for code in PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CODES)
    assert len(observed) == 17
    assert len(set(observed)) == 17
    for code, message in zip(
        PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_ISSUE_CODES,
        observed,
    ):
        assert PersistedEvidenceKnowledgeConstructionIssue(code, message) == _issue(code)
        with pytest.raises(ValueError, match="message"):
            PersistedEvidenceKnowledgeConstructionIssue(code, "caller supplied")


def test_compatibility_record_is_frozen_and_rederives_identity() -> None:
    record = _record()
    assert record.acceptance_record_ids == tuple(
        sorted(record.acceptance_record_ids)
    )
    with pytest.raises(FrozenInstanceError):
        record.source_id = "changed"
    with pytest.raises(ValueError, match="compatibility_record_id"):
        PersistedEvidenceKnowledgeCompatibilityRecord(
            compatibility_record_id="pekc1_" + "0" * 64,
            **_identity_values(),
        )


@pytest.mark.parametrize(
    "changes",
    (
        {"acceptance_record_ids": []},
        {
            "acceptance_record_ids": (
                "ar1_" + "8" * 64,
                "ar1_" + "7" * 64,
            )
        },
        {"collection_payload_digest": "A" * 64},
        {"revision_number": True},
        {"construction_rule_id": "   "},
    ),
)
def test_compatibility_record_rejects_invalid_or_mutable_values(
    changes: dict[str, object],
) -> None:
    values = _identity_values(**changes)
    with pytest.raises((TypeError, ValueError)):
        PersistedEvidenceKnowledgeCompatibilityRecord(
            compatibility_record_id="pekc1_" + "0" * 64,
            **values,
        )


def test_constructed_result_shape_is_exact_and_mutation_is_false() -> None:
    result = PersistedEvidenceKnowledgeConstructionResult(
        contract_version=(
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ),
        status=PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED,
        mutation_performed=False,
        compatibility_record=_record(),
        knowledge_construction_result=_nested_result("constructed"),
        issue=None,
    )
    assert result.status == "constructed"
    assert result.mutation_performed is False
    with pytest.raises(FrozenInstanceError):
        result.status = "rejected"


def test_knowledge_constructor_rejection_shape_preserves_nested_result() -> None:
    nested = _nested_result("rejected")
    result = PersistedEvidenceKnowledgeConstructionResult(
        contract_version=(
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ),
        status=PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED,
        mutation_performed=False,
        compatibility_record=_record(),
        knowledge_construction_result=nested,
        issue=_issue("knowledge_construction_rejected"),
    )
    assert result.knowledge_construction_result is nested
    assert result.compatibility_record is not None


def test_preconstruction_rejection_shape_has_no_partial_values() -> None:
    result = PersistedEvidenceKnowledgeConstructionResult(
        contract_version=(
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ),
        status=PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED,
        mutation_performed=False,
        compatibility_record=None,
        knowledge_construction_result=None,
        issue=_issue("invalid_request"),
    )
    assert result.compatibility_record is None
    assert result.knowledge_construction_result is None


@pytest.mark.parametrize(
    "changes",
    (
        {"status": "other"},
        {"mutation_performed": True},
        {"issue": _issue("invalid_request")},
        {"compatibility_record": None},
        {"knowledge_construction_result": None},
    ),
)
def test_impossible_constructed_result_shapes_are_rejected(
    changes: dict[str, object],
) -> None:
    values: dict[str, object] = {
        "contract_version": (
            PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION
        ),
        "status": PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_CONSTRUCTED,
        "mutation_performed": False,
        "compatibility_record": _record(),
        "knowledge_construction_result": _nested_result("constructed"),
        "issue": None,
    }
    values.update(changes)
    with pytest.raises((TypeError, ValueError)):
        PersistedEvidenceKnowledgeConstructionResult(**values)


def test_non_constructor_rejection_cannot_expose_partial_values() -> None:
    with pytest.raises(ValueError, match="pre-construction"):
        PersistedEvidenceKnowledgeConstructionResult(
            contract_version=(
                PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_RESULT_CONTRACT_VERSION
            ),
            status=PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_STATUS_REJECTED,
            mutation_performed=False,
            compatibility_record=_record(),
            knowledge_construction_result=None,
            issue=_issue("invalid_request"),
        )


def test_request_rejects_wrong_exact_dependency_types() -> None:
    with pytest.raises(TypeError, match="repository_lookup_result"):
        PersistedEvidenceKnowledgeConstructionRequest(
            contract_version=(
                PERSISTED_EVIDENCE_KNOWLEDGE_CONSTRUCTION_REQUEST_CONTRACT_VERSION
            ),
            repository_lookup_result=object(),
            target_evidence_id="evm1_" + "1" * 64,
            knowledge_construction_request=object(),
            compatibility_policy_id=(
                PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID
            ),
            compatibility_policy_version=(
                PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION
            ),
        )
