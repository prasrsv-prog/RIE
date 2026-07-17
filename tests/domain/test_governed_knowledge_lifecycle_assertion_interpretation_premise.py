from dataclasses import FrozenInstanceError, fields
from datetime import datetime, timedelta, timezone
import ast
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import pytest

import rie.domain.governed_knowledge_lifecycle_assertion as assertion_domain
import rie.domain.governed_knowledge_lifecycle_assertion_interpretation_premise as domain


NOW = datetime(2026, 7, 17, 12, 34, 56, 123456, tzinfo=timezone.utc)
GK_ID = "gk1_" + "1" * 64
OTHER_GK_ID = "gk1_" + "2" * 64

PUBLIC_SYMBOLS = {
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_CONTRACT_VERSION",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_POLICY_ID",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_POLICY_VERSION",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_CANONICALIZATION_CONTRACT",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_DIGEST_ALGORITHM",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_SCOPE_DECLARED",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_INCOMPLETE",
    "GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput",
    "GovernedKnowledgeLifecycleAssertionInterpretationPremise",
    "canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection",
    "canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_bytes",
    "compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id",
    "governed_knowledge_lifecycle_assertion_interpretation_premise_identity_input_from_record",
}

IDENTITY_FIELDS = (
    "contract_version",
    "governed_knowledge_id",
    "governed_knowledge_contract_version",
    "premise_scope",
    "premise_scope_reference",
    "completeness_declaration",
    "assertions",
    "declared_by",
    "declared_at",
    "declaration_policy_id",
    "declaration_policy_version",
    "reason_codes",
)
RECORD_FIELDS = (
    "governed_knowledge_lifecycle_assertion_interpretation_premise_id",
    *IDENTITY_FIELDS,
)
PROJECTION_KEYS = (
    "contract_version",
    "governed_knowledge_id",
    "governed_knowledge_contract_version",
    "premise_scope",
    "premise_scope_reference",
    "completeness_declaration",
    "assertion_ids",
    "declared_by",
    "declared_at",
    "declaration_policy_id",
    "declaration_policy_version",
    "reason_codes",
    "identity_canonicalization_contract",
)


def _assertion_identity(
    **changes: object,
) -> assertion_domain.GovernedKnowledgeLifecycleAssertionIdentityInput:
    values: dict[str, object] = {
        "contract_version": (
            assertion_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION
        ),
        "governed_knowledge_id": GK_ID,
        "governed_knowledge_contract_version": "governed-knowledge-v1",
        "assertion_scope": (
            assertion_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED
        ),
        "assertion_scope_reference": "assertion-reference-1",
        "assertion_value": "candidate",
        "asserted_by": "caller-1",
        "asserted_at": NOW,
        "assertion_policy_id": "assertion-policy-1",
        "assertion_policy_version": "1.0.0",
        "reason_codes": ("caller_supplied_lifecycle_assertion",),
    }
    values.update(changes)
    return assertion_domain.GovernedKnowledgeLifecycleAssertionIdentityInput(
        **values  # type: ignore[arg-type]
    )


def _assertion_record(
    identity: (
        assertion_domain.GovernedKnowledgeLifecycleAssertionIdentityInput
        | None
    ) = None,
    **changes: object,
) -> assertion_domain.GovernedKnowledgeLifecycleAssertion:
    material = identity or _assertion_identity()
    values: dict[str, object] = {
        "governed_knowledge_lifecycle_assertion_id": (
            assertion_domain.compute_governed_knowledge_lifecycle_assertion_id(
                material
            )
        ),
        **{
            item.name: getattr(material, item.name)
            for item in fields(
                assertion_domain.GovernedKnowledgeLifecycleAssertionIdentityInput
            )
        },
    }
    values.update(changes)
    return assertion_domain.GovernedKnowledgeLifecycleAssertion(
        **values  # type: ignore[arg-type]
    )


def _ordered_assertions(
    *records: assertion_domain.GovernedKnowledgeLifecycleAssertion,
) -> tuple[assertion_domain.GovernedKnowledgeLifecycleAssertion, ...]:
    return tuple(
        sorted(
            records,
            key=lambda item: item.governed_knowledge_lifecycle_assertion_id,
        )
    )


def _identity(
    **changes: object,
) -> domain.GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput:
    values: dict[str, object] = {
        "contract_version": (
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_CONTRACT_VERSION
        ),
        "governed_knowledge_id": GK_ID,
        "governed_knowledge_contract_version": "governed-knowledge-v1",
        "premise_scope": (
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_SCOPE_DECLARED
        ),
        "premise_scope_reference": "premise-reference-1",
        "completeness_declaration": (
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE
        ),
        "assertions": (_assertion_record(),),
        "declared_by": "caller-1",
        "declared_at": NOW,
        "declaration_policy_id": "declaration-policy-1",
        "declaration_policy_version": "1.0.0",
        "reason_codes": ("caller_supplied_interpretation_premise",),
    }
    values.update(changes)
    return (
        domain.GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput(
            **values  # type: ignore[arg-type]
        )
    )


def _record(
    identity: (
        domain.GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput
        | None
    ) = None,
    **changes: object,
) -> domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise:
    material = identity or _identity()
    values: dict[str, object] = {
        "governed_knowledge_lifecycle_assertion_interpretation_premise_id": (
            domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
                material
            )
        ),
        **{
            field_name: getattr(material, field_name)
            for field_name in IDENTITY_FIELDS
        },
    }
    values.update(changes)
    return domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise(
        **values  # type: ignore[arg-type]
    )


def _public_names() -> set[str]:
    return {
        name
        for name in vars(domain)
        if not name.startswith("_")
    }


def test_public_contract_symbol_set_is_exact() -> None:
    assert _public_names() == PUBLIC_SYMBOLS
    assert len(PUBLIC_SYMBOLS) == 15


def test_constant_values_are_exact() -> None:
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_CONTRACT_VERSION
        == "governed-knowledge-lifecycle-assertion-interpretation-premise-v1"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX
        == "gklaip1_"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_POLICY_ID
        == "rcis-governed-knowledge-lifecycle-assertion-interpretation-premise-identity"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_POLICY_VERSION
        == "1.0.0"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_IDENTITY_CANONICALIZATION_CONTRACT
        == "rcis-governed-knowledge-lifecycle-assertion-interpretation-premise-canonical-json-v1"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_DIGEST_ALGORITHM
        == "sha256"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_SCOPE_DECLARED
        == "governed_knowledge_lifecycle_assertion_interpretation_for_declared_subject"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE
        == "complete_for_declared_scope"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_INCOMPLETE
        == "incomplete_for_declared_scope"
    )


def test_upstream_imports_are_private_and_literals_are_not_duplicated() -> None:
    path = Path(
        "src/rie/domain/"
        "governed_knowledge_lifecycle_assertion_interpretation_premise.py"
    )
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    governed_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "rie.domain.governed_knowledge"
    ]
    assertion_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "rie.domain.governed_knowledge_lifecycle_assertion"
    ]

    assert len(governed_imports) == 1
    assert [
        (alias.name, alias.asname)
        for alias in governed_imports[0].names
    ] == [
        (
            "GOVERNED_KNOWLEDGE_CONTRACT_VERSION",
            "_GOVERNED_KNOWLEDGE_CONTRACT_VERSION",
        )
    ]
    assert len(assertion_imports) == 1
    assert [
        (alias.name, alias.asname)
        for alias in assertion_imports[0].names
    ] == [
        (
            "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION",
            "_GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION",
        ),
        (
            "GovernedKnowledgeLifecycleAssertion",
            "_GovernedKnowledgeLifecycleAssertion",
        ),
    ]

    string_literals = {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and type(node.value) is str
    }
    assert "governed-knowledge-v1" not in string_literals
    assert "governed-knowledge-lifecycle-assertion-v1" not in string_literals
    assert "GOVERNED_KNOWLEDGE_CONTRACT_VERSION" not in _public_names()
    assert "GovernedKnowledgeLifecycleAssertion" not in _public_names()


def test_identity_input_field_order_and_count_are_exact() -> None:
    assert tuple(
        item.name
        for item in fields(
            domain.GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput
        )
    ) == IDENTITY_FIELDS
    assert len(IDENTITY_FIELDS) == 12


def test_final_record_field_order_and_count_are_exact() -> None:
    assert tuple(
        item.name
        for item in fields(
            domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise
        )
    ) == RECORD_FIELDS
    assert len(RECORD_FIELDS) == 13


def test_identity_projection_keys_and_count_are_exact() -> None:
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection(
            _identity()
        )
    )
    assert tuple(projection) == PROJECTION_KEYS
    assert len(projection) == 13
    assert (
        "governed_knowledge_lifecycle_assertion_interpretation_premise_id"
        not in projection
    )


def test_canonical_bytes_are_deterministic_and_exact() -> None:
    identity = _identity()
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection(
            identity
        )
    )
    expected = json.dumps(
        projection,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_bytes(
            identity
        )
        == expected
    )
    assert (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_bytes(
            identity
        )
        == expected
    )


def test_deterministic_premise_id_prefix_and_digest_shape() -> None:
    identity = _identity()
    premise_id = (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            identity
        )
    )
    assert re.fullmatch(r"gklaip1_[0-9a-f]{64}", premise_id)
    assert premise_id == (
        "gklaip1_"
        + hashlib.sha256(
            domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_bytes(
                identity
            )
        ).hexdigest()
    )


@pytest.mark.parametrize(
    ("value", "message"),
    (
        (
            1,
            "governed_knowledge_lifecycle_assertion_interpretation_premise_id "
            "must be an exact non-empty string",
        ),
        (
            "",
            "governed_knowledge_lifecycle_assertion_interpretation_premise_id "
            "must be an exact non-empty string",
        ),
        (
            "gklaip1_bad",
            "governed_knowledge_lifecycle_assertion_interpretation_premise_id "
            "has an invalid format",
        ),
    ),
)
def test_declared_premise_id_type_and_format_rejection(
    value: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=re.escape(message)):
        _record(
            governed_knowledge_lifecycle_assertion_interpretation_premise_id=value
        )


def test_declared_premise_id_mismatch_rejection() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "governed_knowledge_lifecycle_assertion_interpretation_premise_id "
            "does not match identity"
        ),
    ):
        _record(
            governed_knowledge_lifecycle_assertion_interpretation_premise_id=(
                "gklaip1_" + "0" * 64
            )
        )


def test_record_to_input_transfers_exact_material() -> None:
    identity = _identity()
    record = _record(identity)
    assert (
        domain.governed_knowledge_lifecycle_assertion_interpretation_premise_identity_input_from_record(
            record
        )
        == identity
    )


def test_identity_input_is_frozen() -> None:
    identity = _identity()
    with pytest.raises(FrozenInstanceError):
        identity.declared_by = "changed"  # type: ignore[misc]


def test_final_record_is_frozen() -> None:
    record = _record()
    with pytest.raises(FrozenInstanceError):
        record.declared_by = "changed"  # type: ignore[misc]


def test_helpers_reject_wrong_exact_types_and_subclasses() -> None:
    expected_identity_message = (
        "identity_input must be an exact "
        "GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput"
    )

    class IdentitySubclass(
        domain.GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput
    ):
        pass

    base_identity = _identity()
    identity_subclass = IdentitySubclass(
        **{
            field_name: getattr(base_identity, field_name)
            for field_name in IDENTITY_FIELDS
        }
    )
    for value in (object(), identity_subclass):
        for helper in (
            domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection,
            domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_bytes,
            domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id,
        ):
            with pytest.raises(
                ValueError,
                match=expected_identity_message,
            ):
                helper(value)  # type: ignore[arg-type]

    class RecordSubclass(
        domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise
    ):
        pass

    base_record = _record()
    record_subclass = object.__new__(RecordSubclass)
    for field_name in RECORD_FIELDS:
        object.__setattr__(
            record_subclass,
            field_name,
            getattr(base_record, field_name),
        )

    for value in (object(), record_subclass):
        with pytest.raises(
            ValueError,
            match=(
                "record must be an exact "
                "GovernedKnowledgeLifecycleAssertionInterpretationPremise"
            ),
        ):
            domain.governed_knowledge_lifecycle_assertion_interpretation_premise_identity_input_from_record(
                value  # type: ignore[arg-type]
            )


def test_identity_input_validation_precedence_stops_at_first_failure() -> None:
    with pytest.raises(ValueError, match="unsupported contract_version"):
        _identity(
            contract_version="wrong",
            governed_knowledge_id="wrong",
            governed_knowledge_contract_version="wrong",
        )
    with pytest.raises(
        ValueError,
        match="governed_knowledge_id has an invalid format",
    ):
        _identity(
            governed_knowledge_id="wrong",
            governed_knowledge_contract_version="wrong",
            premise_scope="wrong",
        )
    with pytest.raises(
        ValueError,
        match="unsupported governed_knowledge_contract_version",
    ):
        _identity(
            governed_knowledge_contract_version="wrong",
            premise_scope="wrong",
            premise_scope_reference="",
        )
    with pytest.raises(ValueError, match="unsupported premise_scope"):
        _identity(
            premise_scope="wrong",
            premise_scope_reference="",
            completeness_declaration="wrong",
        )
    with pytest.raises(
        ValueError,
        match="premise_scope_reference must be an exact non-empty string",
    ):
        _identity(
            premise_scope_reference="",
            completeness_declaration="wrong",
            assertions=[],
        )
    with pytest.raises(
        ValueError,
        match="unsupported completeness_declaration",
    ):
        _identity(
            completeness_declaration="wrong",
            assertions=[],
            declared_by="",
        )


def test_final_record_validation_precedence_is_id_then_identity_then_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "governed_knowledge_lifecycle_assertion_interpretation_premise_id "
            "has an invalid format"
        ),
    ):
        _record(
            governed_knowledge_lifecycle_assertion_interpretation_premise_id="wrong",
            contract_version="wrong",
        )
    with pytest.raises(ValueError, match="unsupported contract_version"):
        _record(
            governed_knowledge_lifecycle_assertion_interpretation_premise_id=(
                "gklaip1_" + "0" * 64
            ),
            contract_version="wrong",
        )
    with pytest.raises(
        ValueError,
        match=(
            "governed_knowledge_lifecycle_assertion_interpretation_premise_id "
            "does not match identity"
        ),
    ):
        _record(
            governed_knowledge_lifecycle_assertion_interpretation_premise_id=(
                "gklaip1_" + "0" * 64
            )
        )


def test_projection_revalidates_mutated_identity_input() -> None:
    identity = _identity()
    object.__setattr__(identity, "declared_by", "")
    with pytest.raises(
        ValueError,
        match="declared_by must be an exact non-empty string",
    ):
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection(
            identity
        )


def test_contract_version_rejection() -> None:
    with pytest.raises(ValueError, match="unsupported contract_version"):
        _identity(contract_version="unsupported")


@pytest.mark.parametrize(
    ("value", "message"),
    (
        (
            1,
            "governed_knowledge_id must be an exact non-empty string",
        ),
        (
            "",
            "governed_knowledge_id must be an exact non-empty string",
        ),
        (
            "gk1_bad",
            "governed_knowledge_id has an invalid format",
        ),
    ),
)
def test_governed_knowledge_id_type_and_format_rejection(
    value: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=re.escape(message)):
        _identity(governed_knowledge_id=value)


def test_governed_knowledge_contract_version_rejection() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported governed_knowledge_contract_version",
    ):
        _identity(governed_knowledge_contract_version="unsupported")


def test_premise_scope_rejection() -> None:
    with pytest.raises(ValueError, match="unsupported premise_scope"):
        _identity(premise_scope="unsupported")


@pytest.mark.parametrize("value", ("", " ", 1))
def test_premise_scope_reference_rejection(value: object) -> None:
    with pytest.raises(
        ValueError,
        match="premise_scope_reference must be an exact non-empty string",
    ):
        _identity(premise_scope_reference=value)


@pytest.mark.parametrize("value", ("", "wrong", 1))
def test_completeness_declaration_rejection(value: object) -> None:
    with pytest.raises(
        ValueError,
        match="unsupported completeness_declaration",
    ):
        _identity(completeness_declaration=value)


@pytest.mark.parametrize("value", ([], "assertions", None))
def test_assertions_require_exact_tuple(value: object) -> None:
    with pytest.raises(
        ValueError,
        match="assertions must be an exact tuple",
    ):
        _identity(assertions=value)


def test_assertions_require_exact_lifecycle_assertion_records() -> None:
    class AssertionSubclass(
        assertion_domain.GovernedKnowledgeLifecycleAssertion
    ):
        pass

    base = _assertion_record()
    subclass = object.__new__(AssertionSubclass)
    for item in fields(
        assertion_domain.GovernedKnowledgeLifecycleAssertion
    ):
        object.__setattr__(subclass, item.name, getattr(base, item.name))

    for value in (object(), subclass):
        with pytest.raises(
            ValueError,
            match=(
                "assertions must contain exact "
                "GovernedKnowledgeLifecycleAssertion records"
            ),
        ):
            _identity(assertions=(value,))


def test_nested_lifecycle_assertion_is_revalidated_after_bypass_mutation() -> None:
    assertion = _assertion_record()
    object.__setattr__(assertion, "assertion_value", "")
    with pytest.raises(
        ValueError,
        match="assertion_value must be an exact non-empty string",
    ):
        _identity(assertions=(assertion,))


def test_cross_subject_assertion_rejection() -> None:
    other = _assertion_record(
        _assertion_identity(governed_knowledge_id=OTHER_GK_ID)
    )
    with pytest.raises(
        ValueError,
        match="assertions must match governed_knowledge_id",
    ):
        _identity(assertions=(other,))


def test_assertion_governed_knowledge_contract_version_mismatch_rejection() -> None:
    assertion = _assertion_record()
    object.__setattr__(
        assertion,
        "governed_knowledge_contract_version",
        "unsupported",
    )
    with pytest.raises(
        ValueError,
        match="unsupported governed_knowledge_contract_version",
    ):
        _identity(assertions=(assertion,))


def test_lifecycle_assertion_contract_version_mismatch_rejection() -> None:
    assertion = _assertion_record()
    object.__setattr__(assertion, "contract_version", "unsupported")
    with pytest.raises(ValueError, match="unsupported contract_version"):
        _identity(assertions=(assertion,))


def test_empty_assertion_tuple_is_valid_and_projects_empty_array() -> None:
    identity = _identity(assertions=())
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection(
            identity
        )
    )
    assert projection["assertion_ids"] == []
    assert re.fullmatch(
        r"gklaip1_[0-9a-f]{64}",
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            identity
        ),
    )


def test_duplicate_assertion_ids_are_rejected() -> None:
    assertion = _assertion_record()
    with pytest.raises(
        ValueError,
        match="assertions must contain unique lifecycle assertion IDs",
    ):
        _identity(assertions=(assertion, assertion))


def test_assertions_require_lexicographic_id_order() -> None:
    first = _assertion_record(
        _assertion_identity(assertion_value="first")
    )
    second = _assertion_record(
        _assertion_identity(assertion_value="second")
    )
    ordered = _ordered_assertions(first, second)
    if ordered[0].governed_knowledge_lifecycle_assertion_id == (
        ordered[1].governed_knowledge_lifecycle_assertion_id
    ):
        pytest.fail("test assertions unexpectedly share an ID")
    with pytest.raises(
        ValueError,
        match=(
            "assertions must be lexicographically ordered by "
            "lifecycle assertion ID"
        ),
    ):
        _identity(assertions=tuple(reversed(ordered)))


def test_projection_contains_exact_ordered_assertion_ids() -> None:
    first = _assertion_record(
        _assertion_identity(assertion_value="first")
    )
    second = _assertion_record(
        _assertion_identity(assertion_value="second")
    )
    ordered = _ordered_assertions(first, second)
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_premise_identity_projection(
            _identity(assertions=ordered)
        )
    )
    assert projection["assertion_ids"] == [
        item.governed_knowledge_lifecycle_assertion_id
        for item in ordered
    ]


def test_contradictory_assertions_coexist_without_selection() -> None:
    candidate = _assertion_record(
        _assertion_identity(assertion_value="candidate")
    )
    withdrawn = _assertion_record(
        _assertion_identity(assertion_value="withdrawn")
    )
    assertions = _ordered_assertions(candidate, withdrawn)
    identity = _identity(assertions=assertions)
    record = _record(identity)
    assert len(record.assertions) == 2
    assert {
        item.assertion_value
        for item in record.assertions
    } == {"candidate", "withdrawn"}


@pytest.mark.parametrize("value", ("", " ", 1))
def test_declared_by_rejection(value: object) -> None:
    with pytest.raises(
        ValueError,
        match="declared_by must be an exact non-empty string",
    ):
        _identity(declared_by=value)


def test_non_datetime_and_naive_datetime_rejection() -> None:
    with pytest.raises(
        ValueError,
        match="declared_at must be an exact datetime",
    ):
        _identity(declared_at="2026-07-17")
    with pytest.raises(
        ValueError,
        match="declared_at must be timezone-aware",
    ):
        _identity(declared_at=NOW.replace(tzinfo=None))


def test_equivalent_instants_across_offsets_have_same_identity() -> None:
    local = NOW.astimezone(timezone(timedelta(hours=7)))
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            _identity(declared_at=NOW)
        )
        == domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            _identity(declared_at=local)
        )
    )


def test_different_microseconds_are_distinct() -> None:
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            _identity(declared_at=NOW)
        )
        != domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            _identity(declared_at=NOW + timedelta(microseconds=1))
        )
    )


@pytest.mark.parametrize(
    "field_name",
    ("declaration_policy_id", "declaration_policy_version"),
)
@pytest.mark.parametrize("value", ("", " ", 1))
def test_declaration_policy_field_rejection(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must be an exact non-empty string",
    ):
        _identity(**{field_name: value})


@pytest.mark.parametrize("value", ((), [], "reason"))
def test_reason_codes_require_non_empty_tuple(value: object) -> None:
    with pytest.raises(
        ValueError,
        match="reason_codes must be a non-empty tuple",
    ):
        _identity(reason_codes=value)


@pytest.mark.parametrize("value", ((1,), ("",), (" ",)))
def test_reason_codes_require_exact_non_empty_strings(
    value: object,
) -> None:
    with pytest.raises(
        ValueError,
        match="reason_codes must be an exact non-empty string",
    ):
        _identity(reason_codes=value)


def test_reason_codes_reject_duplicates() -> None:
    with pytest.raises(
        ValueError,
        match="reason_codes must contain unique values",
    ):
        _identity(reason_codes=("a", "a"))


def test_reason_codes_require_lexicographic_order() -> None:
    with pytest.raises(
        ValueError,
        match="reason_codes must be lexicographically ordered",
    ):
        _identity(reason_codes=("b", "a"))


def test_unicode_nfc_equivalence() -> None:
    composed = "caf\u00e9"
    decomposed = unicodedata.normalize("NFD", composed)
    assert composed != decomposed
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            _identity(premise_scope_reference=composed)
        )
        == domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            _identity(premise_scope_reference=decomposed)
        )
    )


@pytest.mark.parametrize(
    "value",
    (
        object(),
        {1, 2},
        datetime(2026, 7, 17, tzinfo=timezone.utc),
        complex(1, 2),
    ),
)
def test_unsupported_canonical_exact_type_rejection(
    value: object,
) -> None:
    with pytest.raises(ValueError, match="unsupported canonical value"):
        domain._canonicalize(value)


@pytest.mark.parametrize(
    "value",
    (float("nan"), float("inf"), float("-inf")),
)
def test_non_finite_exact_float_rejection(value: float) -> None:
    with pytest.raises(
        ValueError,
        match="canonical values must be finite",
    ):
        domain._canonicalize(value)


def test_non_string_canonical_mapping_key_rejection() -> None:
    with pytest.raises(
        ValueError,
        match="canonical mapping keys must be strings",
    ):
        domain._canonicalize({1: "value"})


def test_normalized_canonical_mapping_key_collision_rejection() -> None:
    with pytest.raises(
        ValueError,
        match="canonical mapping keys must remain unique",
    ):
        domain._canonicalize({"\u00e9": 1, "e\u0301": 2})


def test_identical_identity_material_gives_identical_id() -> None:
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            _identity()
        )
        == domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            _identity()
        )
    )


@pytest.mark.parametrize(
    "changes",
    (
        {
            "contract_version": (
                "governed-knowledge-lifecycle-assertion-interpretation-premise-v2"
            )
        },
        {"governed_knowledge_id": OTHER_GK_ID},
        {"governed_knowledge_contract_version": "governed-knowledge-v2"},
        {"premise_scope": "another_scope"},
        {"premise_scope_reference": "reference-2"},
        {
            "completeness_declaration": (
                domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_INCOMPLETE
            )
        },
        {"assertions": ()},
        {"declared_by": "caller-2"},
        {"declared_at": NOW + timedelta(microseconds=1)},
        {"declaration_policy_id": "policy-2"},
        {"declaration_policy_version": "2.0.0"},
        {"reason_codes": ("another_reason",)},
    ),
)
def test_each_material_field_changes_identity_or_fails_closed(
    changes: dict[str, object],
) -> None:
    base = _identity()
    base_id = (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            base
        )
    )
    try:
        changed = _identity(**changes)
    except ValueError:
        return
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
            changed
        )
        != base_id
    )


def test_no_diagnostics_interpretation_or_runtime_surface() -> None:
    identity_names = {
        item.name
        for item in fields(
            domain.GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput
        )
    }
    record_names = {
        item.name
        for item in fields(
            domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise
        )
    }
    forbidden = {
        "diagnostics",
        "interpretation_result",
        "composition_status",
        "selected_assertion",
        "current_state",
        "current_effective",
        "prior_state",
        "resulting_state",
        "transition",
        "repository",
        "persistence",
        "serializer",
        "winner",
        "supersedes",
    }
    assert forbidden.isdisjoint(identity_names)
    assert forbidden.isdisjoint(record_names)
    assert forbidden.isdisjoint(_public_names())


def test_package_initializer_has_no_premise_export() -> None:
    initializer = Path("src/rie/domain/__init__.py").read_text(
        encoding="utf-8-sig"
    )
    assert (
        "governed_knowledge_lifecycle_assertion_interpretation_premise"
        not in initializer
    )
    assert (
        "GovernedKnowledgeLifecycleAssertionInterpretationPremise"
        not in initializer
    )


def test_module_has_no_filesystem_database_network_clock_or_randomness_dependency() -> None:
    path = Path(
        "src/rie/domain/"
        "governed_knowledge_lifecycle_assertion_interpretation_premise.py"
    )
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    assert imported.isdisjoint(
        {
            "os",
            "pathlib",
            "sqlite3",
            "socket",
            "requests",
            "urllib",
            "time",
            "random",
            "secrets",
            "uuid",
        }
    )
    forbidden_calls = {
        "open",
        "now",
        "utcnow",
        "time",
        "random",
        "randint",
        "uuid4",
        "connect",
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
    }
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
    }
    assert forbidden_calls.isdisjoint(called_names | called_attributes)
