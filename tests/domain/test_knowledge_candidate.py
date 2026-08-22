from dataclasses import FrozenInstanceError, replace
import json

import pytest

from rie.domain.knowledge_candidate import (
    INITIAL_AUTHORITY_STATUS,
    INITIAL_CONFLICT_STATUS,
    INITIAL_LIFECYCLE_STATUS,
    INITIAL_REVIEW_STATUS,
    KNOWLEDGE_CANDIDATE_CANONICALIZATION_CONTRACT,
    KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
    KNOWLEDGE_CANDIDATE_IDENTITY_POLICY_ID,
    KNOWLEDGE_CANDIDATE_IDENTITY_POLICY_VERSION,
    IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE,
    VERBATIM_TEXT_STATEMENT_TYPE,
    KnowledgeCandidate,
    KnowledgeCandidateIdentityInput,
    KnowledgeDiagnostic,
    KnowledgeEvidenceSupport,
    canonical_knowledge_candidate_identity_bytes,
    canonical_knowledge_candidate_identity_projection,
    compute_knowledge_candidate_id,
    identity_input_from_knowledge_candidate,
)


EVIDENCE_ID = "ev1_" + "1" * 64
ACCEPTANCE_ID = "ar1_" + "2" * 64


def _support(**changes: object) -> KnowledgeEvidenceSupport:
    values = {
        "evidence_id": EVIDENCE_ID,
        "acceptance_record_ids": (ACCEPTANCE_ID,),
        "acceptance_review_record_ids": ("review-1",),
        "source_id": "source-1",
        "source_content_digest": "3" * 64,
        "source_authority_status": "official",
        "source_lifecycle_status": "active",
        "payload_digest": "4" * 64,
        "locator_type": "page",
        "locator_value": (1, "paragraph-2"),
        "locator_schema_version": "1.0.0",
    }
    values.update(changes)
    return KnowledgeEvidenceSupport(**values)


def _identity_input(**changes: object) -> KnowledgeCandidateIdentityInput:
    values = {
        "candidate_contract_version": KNOWLEDGE_CANDIDATE_CONTRACT_VERSION,
        "statement_type": VERBATIM_TEXT_STATEMENT_TYPE,
        "statement": "Exact fact",
        "construction_rule_id": "rcis-accepted-text-verbatim",
        "construction_rule_version": "1.0.0",
        "support": (_support(),),
        "authority_status": INITIAL_AUTHORITY_STATUS,
        "lifecycle_status": INITIAL_LIFECYCLE_STATUS,
        "review_status": INITIAL_REVIEW_STATUS,
        "conflict_status": INITIAL_CONFLICT_STATUS,
    }
    values.update(changes)
    return KnowledgeCandidateIdentityInput(**values)


def _candidate(**changes: object) -> KnowledgeCandidate:
    identity_input = changes.pop("identity_input", _identity_input())
    values = {
        "knowledge_candidate_id": compute_knowledge_candidate_id(identity_input),
        "contract_version": identity_input.candidate_contract_version,
        "statement_type": identity_input.statement_type,
        "statement": identity_input.statement,
        "support": identity_input.support,
        "construction_rule_id": identity_input.construction_rule_id,
        "construction_rule_version": identity_input.construction_rule_version,
        "authority_status": identity_input.authority_status,
        "lifecycle_status": identity_input.lifecycle_status,
        "review_status": identity_input.review_status,
        "conflict_status": identity_input.conflict_status,
        "conflict_ids": (),
        "diagnostics": (),
    }
    values.update(changes)
    return KnowledgeCandidate(**values)


def test_identity_policy_constants_are_exact() -> None:
    assert KNOWLEDGE_CANDIDATE_IDENTITY_POLICY_ID == (
        "rcis-knowledge-candidate-identity"
    )
    assert KNOWLEDGE_CANDIDATE_IDENTITY_POLICY_VERSION == "1.0.0"
    assert KNOWLEDGE_CANDIDATE_CANONICALIZATION_CONTRACT == (
        "knowledge-candidate-json-v1"
    )


@pytest.mark.parametrize(
    "instance,field_name,new_value",
    (
        (_support(), "source_id", "changed"),
        (_candidate(), "statement", "changed"),
        (
            KnowledgeDiagnostic("code", "info", "message", "field", "source"),
            "code",
            "changed",
        ),
    ),
)
def test_contracts_are_frozen(
    instance: object,
    field_name: str,
    new_value: str,
) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(instance, field_name, new_value)


def test_candidate_value_equality_and_explicit_identity() -> None:
    assert _candidate() == _candidate()
    assert _candidate().knowledge_candidate_id.startswith("kc1_")


@pytest.mark.parametrize(
    "candidate_id",
    (
        "",
        "kc1_" + "a" * 63,
        "kc1_" + "A" * 64,
        "wrong_" + "a" * 64,
    ),
)
def test_candidate_rejects_invalid_id_format(candidate_id: str) -> None:
    with pytest.raises(ValueError, match="knowledge_candidate_id"):
        _candidate(knowledge_candidate_id=candidate_id)


def test_candidate_rejects_valid_shape_id_that_does_not_match_content() -> None:
    with pytest.raises(ValueError, match="does not match identity"):
        _candidate(knowledge_candidate_id="kc1_" + "f" * 64)


@pytest.mark.parametrize(
    "field_name,bad_value",
    (
        ("acceptance_record_ids", [ACCEPTANCE_ID]),
        ("acceptance_record_ids", ()),
        ("acceptance_record_ids", (ACCEPTANCE_ID, ACCEPTANCE_ID)),
        (
            "acceptance_record_ids",
            ("ar1_" + "3" * 64, ACCEPTANCE_ID),
        ),
        ("acceptance_record_ids", ("not-an-id",)),
        ("acceptance_review_record_ids", ["review-1"]),
        ("acceptance_review_record_ids", ()),
        ("acceptance_review_record_ids", ("review-1", "review-1")),
        ("acceptance_review_record_ids", ("review-2", "review-1")),
    ),
)
def test_support_requires_strict_ordered_unique_tuples(
    field_name: str,
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _support(**{field_name: bad_value})


@pytest.mark.parametrize(
    "field_name,bad_value",
    (
        ("evidence_id", "ev1_bad"),
        ("source_id", " "),
        ("source_content_digest", "not-a-digest"),
        ("payload_digest", "A" * 64),
        ("locator_type", ""),
        ("locator_value", []),
        ("locator_value", ()),
        ("locator_schema_version", " "),
    ),
)
def test_support_fails_closed_for_invalid_required_values(
    field_name: str,
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _support(**{field_name: bad_value})


def test_candidate_rejects_empty_non_tuple_wrong_exact_and_duplicate_support() -> None:
    with pytest.raises(ValueError, match="support must be a tuple"):
        _identity_input(support=[_support()])
    with pytest.raises(ValueError, match="support must not be empty"):
        _identity_input(support=())

    class SupportSubclass(KnowledgeEvidenceSupport):
        pass

    subclass = SupportSubclass(**_support().__dict__)
    with pytest.raises(ValueError, match="exact KnowledgeEvidenceSupport"):
        _identity_input(support=(subclass,))
    with pytest.raises(ValueError, match="unique Evidence IDs"):
        _identity_input(support=(_support(), _support()))


def test_candidate_requires_support_ordered_by_evidence_id() -> None:
    first = _support(evidence_id="ev1_" + "1" * 64)
    second = _support(evidence_id="ev1_" + "2" * 64)
    with pytest.raises(ValueError, match="ordered by Evidence ID"):
        _identity_input(support=(second, first))


@pytest.mark.parametrize(
    "field_name,bad_value",
    (
        ("authority_status", "official"),
        ("lifecycle_status", "accepted"),
        ("review_status", "approved"),
        ("conflict_status", "none_identified"),
    ),
)
def test_only_initial_governance_states_are_supported(
    field_name: str,
    bad_value: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _identity_input(**{field_name: bad_value})


def test_not_assessed_conflict_state_requires_empty_conflict_ids() -> None:
    with pytest.raises(ValueError, match="requires no conflict IDs"):
        _candidate(conflict_ids=("conflict-1",))
    with pytest.raises(ValueError, match="conflict_ids must be a tuple"):
        _candidate(conflict_ids=[])


def test_canonical_projection_and_bytes_are_stable_and_compact() -> None:
    identity_input = _identity_input()
    first = canonical_knowledge_candidate_identity_bytes(identity_input)
    second = canonical_knowledge_candidate_identity_bytes(identity_input)
    projection = canonical_knowledge_candidate_identity_projection(identity_input)

    assert first == second
    assert b"\n" not in first
    assert json.loads(first) == projection
    assert first == json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    assert projection["canonicalization_contract"] == (
        "knowledge-candidate-json-v1"
    )
    assert tuple(projection) == tuple(sorted(projection))


def test_unicode_nfc_changes_identity_projection_not_visible_statement() -> None:
    decomposed = "Cafe\u0301"
    composed = "Caf\u00e9"
    first = _identity_input(statement=decomposed)
    second = _identity_input(statement=composed)

    assert compute_knowledge_candidate_id(first) == compute_knowledge_candidate_id(
        second
    )
    assert _candidate(identity_input=first).statement == decomposed
    assert _candidate(identity_input=second).statement == composed


def test_replay_identity_is_stable_and_sha256_shaped() -> None:
    first = compute_knowledge_candidate_id(_identity_input())
    second = compute_knowledge_candidate_id(_identity_input())
    assert first == second
    assert len(first) == len("kc1_") + 64


@pytest.mark.parametrize(
    "changed_input",
    (
        _identity_input(statement="Different fact"),
        _identity_input(
            support=(_support(evidence_id="ev1_" + "5" * 64),)
        ),
        _identity_input(
            support=(
                _support(acceptance_record_ids=("ar1_" + "5" * 64,)),
            )
        ),
        _identity_input(support=(_support(source_id="source-2"),)),
        _identity_input(
            support=(_support(source_content_digest="5" * 64),)
        ),
        _identity_input(support=(_support(payload_digest="5" * 64),)),
        _identity_input(support=(_support(locator_value=(2,)),)),
        _identity_input(construction_rule_version="1.0.1"),
    ),
)
def test_material_identity_changes_change_candidate_id(
    changed_input: KnowledgeCandidateIdentityInput,
) -> None:
    assert compute_knowledge_candidate_id(changed_input) != (
        compute_knowledge_candidate_id(_identity_input())
    )


def test_each_governance_state_is_present_in_identity_projection() -> None:
    baseline = _identity_input()
    baseline_id = compute_knowledge_candidate_id(baseline)
    for field_name, changed_value in (
        ("authority_status", "changed-authority"),
        ("lifecycle_status", "changed-lifecycle"),
        ("review_status", "changed-review"),
        ("conflict_status", "changed-conflict"),
    ):
        unsafe = object.__new__(KnowledgeCandidateIdentityInput)
        for name, value in baseline.__dict__.items():
            object.__setattr__(unsafe, name, value)
        object.__setattr__(unsafe, field_name, changed_value)
        assert compute_knowledge_candidate_id(unsafe) != baseline_id


def test_diagnostics_and_non_identity_support_metadata_are_excluded() -> None:
    baseline = _identity_input()
    metadata_changed = _identity_input(
        support=(
            _support(
                acceptance_review_record_ids=("review-2",),
                source_authority_status="reviewed",
                source_lifecycle_status="superseded",
            ),
        )
    )
    diagnostic = KnowledgeDiagnostic(
        "notice",
        "info",
        "Non-identity diagnostic",
        "statement",
        "test",
    )

    assert compute_knowledge_candidate_id(baseline) == (
        compute_knowledge_candidate_id(metadata_changed)
    )
    assert _candidate(diagnostics=(diagnostic,)).knowledge_candidate_id == (
        _candidate().knowledge_candidate_id
    )
    projection_text = json.dumps(
        canonical_knowledge_candidate_identity_projection(baseline)
    )
    assert "diagnostic" not in projection_text
    assert "source_path" not in projection_text
    assert "timestamp" not in projection_text


def test_identity_extraction_rejects_duck_typed_inputs() -> None:
    class DuckIdentity:
        pass

    class DuckCandidate:
        pass

    with pytest.raises(ValueError, match="exact KnowledgeCandidateIdentityInput"):
        compute_knowledge_candidate_id(DuckIdentity())
    with pytest.raises(ValueError, match="exact KnowledgeCandidate"):
        identity_input_from_knowledge_candidate(DuckCandidate())


def test_identity_extraction_round_trip_is_exact() -> None:
    candidate = _candidate()
    assert identity_input_from_knowledge_candidate(candidate) == _identity_input()

def test_image_structural_fact_statement_type_constant_is_exact() -> None:
    assert IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE == "image_structural_fact"


def test_identity_input_accepts_image_structural_fact_statement_type() -> None:
    identity_input = _identity_input(
        statement_type=IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE,
        statement="width=100",
        construction_rule_id=(
            "rcis-accepted-image-structural-fact-selection"
        ),
    )
    first = compute_knowledge_candidate_id(identity_input)
    second = compute_knowledge_candidate_id(identity_input)
    assert first == second
    assert first.startswith("kc1_")


def test_candidate_accepts_image_structural_fact_statement_type() -> None:
    identity_input = _identity_input(
        statement_type=IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE,
        statement="height=200",
        construction_rule_id=(
            "rcis-accepted-image-structural-fact-selection"
        ),
    )
    candidate = _candidate(identity_input=identity_input)
    assert candidate.statement_type == IMAGE_STRUCTURAL_FACT_STATEMENT_TYPE
    assert identity_input_from_knowledge_candidate(candidate) == identity_input


def test_unsupported_statement_type_rejected_and_verbatim_preserved() -> None:
    with pytest.raises(ValueError, match="unsupported statement_type"):
        _identity_input(statement_type="unsupported_fact")
    unsafe = object.__new__(KnowledgeCandidateIdentityInput)
    for name, value in _identity_input().__dict__.items():
        object.__setattr__(unsafe, name, value)
    object.__setattr__(unsafe, "statement_type", "unsupported_fact")
    with pytest.raises(ValueError, match="unsupported statement_type"):
        _candidate(identity_input=unsafe)
    assert _candidate().statement_type == VERBATIM_TEXT_STATEMENT_TYPE


def test_product_variant_identity_statement_type_extension_is_exact() -> None:
    import rie.domain.knowledge_candidate as module

    assert (
        module.PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE
        == "product_variant_identity"
    )
    assert (
        module.PRODUCT_VARIANT_IDENTITY_STATEMENT_TYPE
        in module._SUPPORTED_STATEMENT_TYPES
    )
