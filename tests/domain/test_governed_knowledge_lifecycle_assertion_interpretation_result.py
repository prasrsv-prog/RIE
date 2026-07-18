from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timezone
from decimal import Decimal
import ast
import hashlib
import inspect
import json
from pathlib import Path
import re
import unicodedata

import pytest

import rie.domain.governed_knowledge_lifecycle_assertion as assertion_domain
import rie.domain.governed_knowledge_lifecycle_assertion_interpretation_premise as premise_domain
import rie.domain.governed_knowledge_lifecycle_assertion_interpretation_result as domain


NOW = datetime(2026, 7, 17, 12, 34, 56, 123456, tzinfo=timezone.utc)
GK_ID = "gk1_" + "1" * 64

PUBLIC_SYMBOLS = {
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_CONTRACT_VERSION",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_ID_PREFIX",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_POLICY_ID",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_POLICY_VERSION",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_CANONICALIZATION_CONTRACT",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_DIGEST_ALGORITHM",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY",
    "GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup",
    "GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput",
    "GovernedKnowledgeLifecycleAssertionInterpretationResult",
    "canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_projection",
    "canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_bytes",
    "compute_governed_knowledge_lifecycle_assertion_interpretation_result_id",
    "governed_knowledge_lifecycle_assertion_interpretation_result_identity_input_from_record",
    "interpret_governed_knowledge_lifecycle_assertion_premise_structurally",
}

VALUE_GROUP_FIELDS = (
    "assertion_value",
    "assertion_ids",
)
IDENTITY_FIELDS = (
    "contract_version",
    "premise",
    "result_status",
    "assertion_value_groups",
    "interpreted_by",
    "interpretation_policy_id",
    "interpretation_policy_version",
    "reason_codes",
)
RECORD_FIELDS = (
    "governed_knowledge_lifecycle_assertion_interpretation_result_id",
    *IDENTITY_FIELDS,
)
PROJECTION_KEYS = {
    "contract_version",
    "premise_id",
    "result_status",
    "assertion_value_groups",
    "interpreted_by",
    "interpretation_policy_id",
    "interpretation_policy_version",
    "reason_codes",
    "identity_canonicalization_contract",
}


def _public_names() -> set[str]:
    return {name for name in vars(domain) if not name.startswith("_")}


def _assertion(value: str, salt: str) -> assertion_domain.GovernedKnowledgeLifecycleAssertion:
    identity = assertion_domain.GovernedKnowledgeLifecycleAssertionIdentityInput(
        contract_version=(
            assertion_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION
        ),
        governed_knowledge_id=GK_ID,
        governed_knowledge_contract_version=(
            assertion_domain._GOVERNED_KNOWLEDGE_CONTRACT_VERSION
        ),
        assertion_scope=(
            assertion_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED
        ),
        assertion_scope_reference=f"scope-{salt}",
        assertion_value=value,
        asserted_by=f"actor-{salt}",
        asserted_at=NOW,
        assertion_policy_id="policy.lifecycle",
        assertion_policy_version="1.0.0",
        reason_codes=(f"reason-{salt}",),
    )
    return assertion_domain.GovernedKnowledgeLifecycleAssertion(
        governed_knowledge_lifecycle_assertion_id=(
            assertion_domain.compute_governed_knowledge_lifecycle_assertion_id(
                identity
            )
        ),
        **identity.__dict__,
    )


def _premise(
    values: tuple[str, ...] = (),
    *,
    completeness: str | None = None,
    declared_by: str = "caller",
    salt: str = "base",
) -> premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise:
    assertions = tuple(
        sorted(
            (
                _assertion(value, f"{salt}-{index}")
                for index, value in enumerate(values)
            ),
            key=lambda item: item.governed_knowledge_lifecycle_assertion_id,
        )
    )
    identity = premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremiseIdentityInput(
        contract_version=(
            premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_CONTRACT_VERSION
        ),
        governed_knowledge_id=GK_ID,
        governed_knowledge_contract_version=(
            premise_domain._GOVERNED_KNOWLEDGE_CONTRACT_VERSION
        ),
        premise_scope=(
            premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_SCOPE_DECLARED
        ),
        premise_scope_reference=f"premise-{salt}",
        completeness_declaration=(
            completeness
            or premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE
        ),
        assertions=assertions,
        declared_by=declared_by,
        declared_at=NOW,
        declaration_policy_id="policy.premise",
        declaration_policy_version="1.0.0",
        reason_codes=("premise-created",),
    )
    return premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise(
        governed_knowledge_lifecycle_assertion_interpretation_premise_id=(
            premise_domain.compute_governed_knowledge_lifecycle_assertion_interpretation_premise_id(
                identity
            )
        ),
        **identity.__dict__,
    )


def _expected_structure(
    premise: premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise,
) -> tuple[
    str,
    tuple[domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup, ...],
]:
    grouped: dict[str, list[str]] = {}
    for assertion in premise.assertions:
        value = unicodedata.normalize("NFC", assertion.assertion_value)
        grouped.setdefault(value, []).append(
            assertion.governed_knowledge_lifecycle_assertion_id
        )
    groups = tuple(
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup(
            assertion_value=value,
            assertion_ids=tuple(sorted(assertion_ids)),
        )
        for value, assertion_ids in sorted(grouped.items())
    )
    if not groups:
        status = (
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY
        )
    elif len(groups) == 1:
        status = (
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM
        )
    else:
        status = (
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY
        )
    return status, groups


def _identity(
    *,
    premise: premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise | None = None,
    result_status: str | None = None,
    assertion_value_groups: tuple[
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup,
        ...,
    ]
    | None = None,
    contract_version: str | None = None,
    interpreted_by: str = "structural-interpreter",
    interpretation_policy_id: str = "policy.structural",
    interpretation_policy_version: str = "1.0.0",
    reason_codes: tuple[str, ...] = ("structural-composition",),
) -> domain.GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput:
    selected_premise = premise or _premise(("active",), salt="identity")
    expected_status, expected_groups = _expected_structure(selected_premise)
    return domain.GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput(
        contract_version=(
            contract_version
            or domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_CONTRACT_VERSION
        ),
        premise=selected_premise,
        result_status=result_status or expected_status,
        assertion_value_groups=(
            expected_groups
            if assertion_value_groups is None
            else assertion_value_groups
        ),
        interpreted_by=interpreted_by,
        interpretation_policy_id=interpretation_policy_id,
        interpretation_policy_version=interpretation_policy_version,
        reason_codes=reason_codes,
    )


def _record(
    identity: domain.GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput
    | None = None,
) -> domain.GovernedKnowledgeLifecycleAssertionInterpretationResult:
    selected = identity or _identity()
    return domain.GovernedKnowledgeLifecycleAssertionInterpretationResult(
        governed_knowledge_lifecycle_assertion_interpretation_result_id=(
            domain.compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
                selected
            )
        ),
        **selected.__dict__,
    )


def test_exact_public_symbol_set() -> None:
    assert _public_names() == PUBLIC_SYMBOLS


def test_exact_constant_values() -> None:
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_CONTRACT_VERSION
        == "governed-knowledge-lifecycle-assertion-interpretation-result-v1"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_ID_PREFIX
        == "gklair1_"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_POLICY_ID
        == "rcis-governed-knowledge-lifecycle-assertion-interpretation-result-identity"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_POLICY_VERSION
        == "1.0.0"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_IDENTITY_CANONICALIZATION_CONTRACT
        == "rcis-governed-knowledge-lifecycle-assertion-interpretation-result-canonical-json-v1"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_DIGEST_ALGORITHM
        == "sha256"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY
        == "empty_assertion_collection"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM
        == "uniform_assertion_value"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY
        == "contradictory_assertion_values"
    )


def test_exact_private_upstream_aliases_and_no_duplicated_identity_literals() -> None:
    assert (
        domain._GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX
        == premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_ID_PREFIX
    )
    assert (
        domain._GovernedKnowledgeLifecycleAssertionInterpretationPremise
        is premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise
    )
    assert (
        domain._GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX
        == assertion_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX
    )
    source = Path(
        "src/rie/domain/"
        "governed_knowledge_lifecycle_assertion_interpretation_result.py"
    ).read_text(encoding="utf-8")
    assert '"gklaip1_"' not in source
    assert '"gkla1_"' not in source


def test_exact_dataclass_field_orders_and_counts() -> None:
    assert tuple(
        item.name
        for item in fields(
            domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup
        )
    ) == VALUE_GROUP_FIELDS
    assert tuple(
        item.name
        for item in fields(
            domain.GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput
        )
    ) == IDENTITY_FIELDS
    assert tuple(
        item.name
        for item in fields(
            domain.GovernedKnowledgeLifecycleAssertionInterpretationResult
        )
    ) == RECORD_FIELDS


def test_exact_identity_projection_and_projected_group_keys() -> None:
    identity = _identity(
        premise=_premise(("active", "inactive"), salt="projection")
    )
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_projection(
            identity
        )
    )
    assert set(projection) == PROJECTION_KEYS
    assert len(projection) == 9
    assert projection["premise_id"] == (
        identity.premise.governed_knowledge_lifecycle_assertion_interpretation_premise_id
    )
    assert all(
        set(group) == {"assertion_value", "assertion_ids"}
        and len(group) == 2
        for group in projection["assertion_value_groups"]
    )


def test_canonical_bytes_match_exact_json_contract() -> None:
    identity = _identity(
        premise=_premise(("\u00e9", "active"), salt="canonical")
    )
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_projection(
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
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_bytes(
            identity
        )
        == expected
    )


def test_deterministic_id_prefix_digest_and_repeatability() -> None:
    identity = _identity()
    first = (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
            identity
        )
    )
    second = (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
            identity
        )
    )
    assert first == second
    assert re.fullmatch(r"gklair1_[0-9a-f]{64}", first)
    assert first == "gklair1_" + hashlib.sha256(
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_bytes(
            identity
        )
    ).hexdigest()


def test_record_to_identity_input_exact_transfer() -> None:
    identity = _identity()
    record = _record(identity)
    converted = (
        domain.governed_knowledge_lifecycle_assertion_interpretation_result_identity_input_from_record(
            record
        )
    )
    assert converted == identity


@pytest.mark.parametrize(
    "factory,field_name",
    [
        (
            lambda: domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup(
                assertion_value="active",
                assertion_ids=(_assertion("active", "frozen").governed_knowledge_lifecycle_assertion_id,),
            ),
            "assertion_value",
        ),
        (lambda: _identity(), "interpreted_by"),
        (lambda: _record(), "interpreted_by"),
    ],
)
def test_all_records_are_frozen(factory, field_name: str) -> None:
    record = factory()
    with pytest.raises(FrozenInstanceError):
        setattr(record, field_name, "changed")


@pytest.mark.parametrize(
    "function",
    [
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_projection,
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_bytes,
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_result_id,
    ],
)
def test_identity_functions_require_exact_identity_input_type(function) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "^identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput$"
        ),
    ):
        function(object())


def test_identity_functions_reject_identity_input_subclass() -> None:
    class IdentitySubclass(
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput
    ):
        pass

    base = _identity()
    subclass = IdentitySubclass(**base.__dict__)
    with pytest.raises(
        ValueError,
        match=(
            "^identity_input must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput$"
        ),
    ):
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
            subclass
        )


def test_record_to_input_requires_exact_record_type_and_rejects_subclass() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "^record must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResult$"
        ),
    ):
        domain.governed_knowledge_lifecycle_assertion_interpretation_result_identity_input_from_record(
            object()
        )

    class RecordSubclass(
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResult
    ):
        pass

    base = _record()
    subclass = object.__new__(RecordSubclass)
    for name, value in base.__dict__.items():
        object.__setattr__(subclass, name, value)
    with pytest.raises(
        ValueError,
        match=(
            "^record must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResult$"
        ),
    ):
        domain.governed_knowledge_lifecycle_assertion_interpretation_result_identity_input_from_record(
            subclass
        )


def test_private_structural_helper_requires_exact_premise_type() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "^premise must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremise$"
        ),
    ):
        domain._derive_expected_structure(object())


@pytest.mark.parametrize(
    "assertion_value,assertion_ids,message",
    [
        (1, (), "assertion_value must be an exact non-empty string"),
        (" ", (), "assertion_value must be an exact non-empty string"),
        ("e\u0301", (), "assertion_value must be Unicode NFC normalized"),
        ("active", [], "assertion_ids must be a non-empty tuple"),
        ("active", (), "assertion_ids must be a non-empty tuple"),
        ("active", (1,), "assertion_ids must be an exact non-empty string"),
        ("active", ("",), "assertion_ids must be an exact non-empty string"),
        ("active", ("gkla1_bad",), "assertion_ids has an invalid format"),
    ],
)
def test_value_group_rejects_invalid_value_or_id_material(
    assertion_value,
    assertion_ids,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup(
            assertion_value=assertion_value,
            assertion_ids=assertion_ids,
        )


def test_value_group_rejects_duplicate_and_unordered_ids() -> None:
    first = _assertion("active", "ids-a").governed_knowledge_lifecycle_assertion_id
    second = _assertion("active", "ids-b").governed_knowledge_lifecycle_assertion_id
    ordered = tuple(sorted((first, second)))
    with pytest.raises(
        ValueError,
        match="^assertion_ids must contain unique values$",
    ):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup(
            assertion_value="active",
            assertion_ids=(ordered[0], ordered[0]),
        )
    with pytest.raises(
        ValueError,
        match="^assertion_ids must be lexicographically ordered$",
    ):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup(
            assertion_value="active",
            assertion_ids=tuple(reversed(ordered)),
        )


def test_value_group_validation_stops_at_first_failure() -> None:
    with pytest.raises(
        ValueError,
        match="^assertion_value must be an exact non-empty string$",
    ):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup(
            assertion_value="",
            assertion_ids=[],
        )


def test_identity_validation_precedence_contract_before_premise() -> None:
    with pytest.raises(ValueError, match="^unsupported contract_version$"):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput(
            contract_version="bad",
            premise=object(),
            result_status="bad",
            assertion_value_groups=[],
            interpreted_by="",
            interpretation_policy_id="",
            interpretation_policy_version="",
            reason_codes=(),
        )


def test_identity_validation_precedence_premise_before_status() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "^premise must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremise$"
        ),
    ):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput(
            contract_version=(
                domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_CONTRACT_VERSION
            ),
            premise=object(),
            result_status="bad",
            assertion_value_groups=[],
            interpreted_by="",
            interpretation_policy_id="",
            interpretation_policy_version="",
            reason_codes=(),
        )


def test_nested_premise_and_assertion_are_revalidated() -> None:
    premise = _premise(("active",), salt="mutated-premise")
    object.__setattr__(premise, "declared_by", "")
    with pytest.raises(
        ValueError,
        match="^declared_by must be an exact non-empty string$",
    ):
        _identity(premise=premise)

    premise = _premise(("active",), salt="mutated-assertion")
    object.__setattr__(premise.assertions[0], "asserted_by", "")
    with pytest.raises(
        ValueError,
        match="^asserted_by must be an exact non-empty string$",
    ):
        _identity(premise=premise)


def test_status_validation_precedes_group_validation() -> None:
    premise = _premise(("active",), salt="status-first")
    with pytest.raises(ValueError, match="^unsupported result_status$"):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultIdentityInput(
            contract_version=(
                domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_CONTRACT_VERSION
            ),
            premise=premise,
            result_status="bad",
            assertion_value_groups=[],
            interpreted_by="",
            interpretation_policy_id="",
            interpretation_policy_version="",
            reason_codes=(),
        )


def test_value_group_type_and_item_exact_type_validation() -> None:
    premise = _premise(("active",), salt="group-type")
    status, groups = _expected_structure(premise)
    with pytest.raises(
        ValueError,
        match="^assertion_value_groups must be an exact tuple$",
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=list(groups),
        )

    class GroupSubclass(
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup
    ):
        pass

    subclass = GroupSubclass(**groups[0].__dict__)
    with pytest.raises(
        ValueError,
        match=(
            "^assertion_value_groups must contain exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationResultValueGroup "
            "records$"
        ),
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=(subclass,),
        )


def test_value_group_record_is_revalidated_after_bypass_mutation() -> None:
    premise = _premise(("active",), salt="group-mutation")
    status, groups = _expected_structure(premise)
    object.__setattr__(groups[0], "assertion_value", "")
    with pytest.raises(
        ValueError,
        match="^assertion_value must be an exact non-empty string$",
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=groups,
        )


def test_duplicate_and_unordered_group_values_are_rejected() -> None:
    premise = _premise(("alpha", "beta"), salt="group-order")
    status, groups = _expected_structure(premise)
    duplicate = replace(groups[1], assertion_value=groups[0].assertion_value)
    with pytest.raises(
        ValueError,
        match=(
            "^assertion_value_groups must contain unique assertion values$"
        ),
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=(groups[0], duplicate),
        )
    with pytest.raises(
        ValueError,
        match=(
            "^assertion_value_groups must be lexicographically ordered by "
            "assertion value$"
        ),
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=tuple(reversed(groups)),
        )


@pytest.mark.parametrize(
    "values,expected_status,expected_group_count",
    [
        (
            (),
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY,
            0,
        ),
        (
            ("active",),
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM,
            1,
        ),
        (
            ("active", "active"),
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM,
            1,
        ),
        (
            ("active", "inactive"),
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY,
            2,
        ),
        (
            ("alpha", "beta", "gamma"),
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY,
            3,
        ),
    ],
)
def test_empty_uniform_and_contradictory_structures(
    values: tuple[str, ...],
    expected_status: str,
    expected_group_count: int,
) -> None:
    premise = _premise(values, salt="structures-" + str(len(values)))
    identity = _identity(premise=premise)
    record = _record(identity)
    assert record.result_status == expected_status
    assert len(record.assertion_value_groups) == expected_group_count
    flattened = [
        assertion_id
        for group in record.assertion_value_groups
        for assertion_id in group.assertion_ids
    ]
    assert sorted(flattened) == sorted(
        assertion.governed_knowledge_lifecycle_assertion_id
        for assertion in premise.assertions
    )


@pytest.mark.parametrize(
    "completeness",
    [
        premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE,
        premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_INCOMPLETE,
    ],
)
def test_empty_premise_accepts_both_completeness_declarations(
    completeness: str,
) -> None:
    premise = _premise((), completeness=completeness, salt=completeness)
    identity = _identity(premise=premise)
    assert (
        identity.result_status
        == domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY
    )
    assert identity.assertion_value_groups == ()


def test_unicode_nfc_values_group_together_without_mutating_assertions() -> None:
    decomposed = "e\u0301"
    composed = "\u00e9"
    premise = _premise((decomposed, composed), salt="nfc")
    identity = _identity(premise=premise)
    assert (
        identity.result_status
        == domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM
    )
    assert identity.assertion_value_groups[0].assertion_value == composed
    assert {item.assertion_value for item in premise.assertions} == {
        decomposed,
        composed,
    }


@pytest.mark.parametrize(
    "values",
    [
        ("A", "a"),
        ("active", "active "),
        ("red", "rouge"),
        ("on", "aktif"),
    ],
)
def test_grouping_does_not_casefold_trim_translate_or_expand_synonyms(
    values: tuple[str, str],
) -> None:
    identity = _identity(premise=_premise(values, salt="exact-" + values[0]))
    assert (
        identity.result_status
        == domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY
    )
    assert len(identity.assertion_value_groups) == 2


def test_membership_omission_invention_repetition_and_wrong_group_fail_closed() -> None:
    premise = _premise(("alpha", "beta"), salt="membership")
    status, groups = _expected_structure(premise)

    omitted = (groups[0],)
    with pytest.raises(
        ValueError,
        match="^assertion_value_groups do not match premise assertions$",
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=omitted,
        )

    invented_id = "gkla1_" + "f" * 64
    invented = (
        replace(groups[0], assertion_ids=(invented_id,)),
        groups[1],
    )
    with pytest.raises(
        ValueError,
        match="^assertion_value_groups do not match premise assertions$",
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=invented,
        )

    repeated_across_groups = (
        groups[0],
        replace(
            groups[1],
            assertion_ids=(groups[0].assertion_ids[0],),
        ),
    )
    with pytest.raises(
        ValueError,
        match="^assertion_value_groups do not match premise assertions$",
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=repeated_across_groups,
        )

    wrong_group = (
        replace(groups[0], assertion_ids=groups[1].assertion_ids),
        replace(groups[1], assertion_ids=groups[0].assertion_ids),
    )
    with pytest.raises(
        ValueError,
        match="^assertion_value_groups do not match premise assertions$",
    ):
        _identity(
            premise=premise,
            result_status=status,
            assertion_value_groups=wrong_group,
        )


def test_group_consistency_is_checked_before_status_consistency() -> None:
    premise = _premise(("alpha", "beta"), salt="consistency-order")
    _, groups = _expected_structure(premise)
    with pytest.raises(
        ValueError,
        match="^assertion_value_groups do not match premise assertions$",
    ):
        _identity(
            premise=premise,
            result_status=(
                domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM
            ),
            assertion_value_groups=(groups[0],),
        )


def test_status_consistency_is_checked_after_valid_group_consistency() -> None:
    premise = _premise(("alpha", "beta"), salt="status-consistency")
    _, groups = _expected_structure(premise)
    with pytest.raises(
        ValueError,
        match="^result_status does not match premise assertions$",
    ):
        _identity(
            premise=premise,
            result_status=(
                domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM
            ),
            assertion_value_groups=groups,
        )


@pytest.mark.parametrize(
    "field,value,message",
    [
        (
            "interpreted_by",
            "",
            "interpreted_by must be an exact non-empty string",
        ),
        (
            "interpretation_policy_id",
            "",
            "interpretation_policy_id must be an exact non-empty string",
        ),
        (
            "interpretation_policy_version",
            "",
            "interpretation_policy_version must be an exact non-empty string",
        ),
    ],
)
def test_interpreter_and_policy_provenance_validation(
    field: str,
    value,
    message: str,
) -> None:
    kwargs = {field: value}
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        _identity(**kwargs)


@pytest.mark.parametrize(
    "reason_codes,message",
    [
        ((), "reason_codes must be a non-empty tuple"),
        ([], "reason_codes must be a non-empty tuple"),
        (("",), "reason_codes must be an exact non-empty string"),
        ((1,), "reason_codes must be an exact non-empty string"),
        (
            ("same", "same"),
            "reason_codes must contain unique values",
        ),
        (
            ("z", "a"),
            "reason_codes must be lexicographically ordered",
        ),
    ],
)
def test_reason_code_validation(reason_codes, message: str) -> None:
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        _identity(reason_codes=reason_codes)


@pytest.mark.parametrize(
    "result_id,message",
    [
        (
            1,
            "governed_knowledge_lifecycle_assertion_interpretation_result_id must be an exact non-empty string",
        ),
        (
            "",
            "governed_knowledge_lifecycle_assertion_interpretation_result_id must be an exact non-empty string",
        ),
        (
            "gklair1_bad",
            "governed_knowledge_lifecycle_assertion_interpretation_result_id has an invalid format",
        ),
    ],
)
def test_final_record_result_id_type_and_format(result_id, message: str) -> None:
    identity = _identity()
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResult(
            governed_knowledge_lifecycle_assertion_interpretation_result_id=result_id,
            **identity.__dict__,
        )


def test_final_record_validates_identity_material_before_id_equality() -> None:
    identity = _identity()
    with pytest.raises(ValueError, match="^unsupported contract_version$"):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResult(
            governed_knowledge_lifecycle_assertion_interpretation_result_id=(
                "gklair1_" + "0" * 64
            ),
            **{**identity.__dict__, "contract_version": "bad"},
        )


def test_final_record_rejects_deterministic_id_mismatch() -> None:
    identity = _identity()
    wrong_id = "gklair1_" + "0" * 64
    assert wrong_id != (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
            identity
        )
    )
    with pytest.raises(
        ValueError,
        match=(
            "^governed_knowledge_lifecycle_assertion_interpretation_result_id "
            "does not match identity$"
        ),
    ):
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResult(
            governed_knowledge_lifecycle_assertion_interpretation_result_id=wrong_id,
            **identity.__dict__,
        )


def test_projection_revalidates_identity_and_nested_material() -> None:
    identity = _identity()
    object.__setattr__(identity, "interpreted_by", "")
    with pytest.raises(
        ValueError,
        match="^interpreted_by must be an exact non-empty string$",
    ):
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_projection(
            identity
        )


@pytest.mark.parametrize(
    "change",
    [
        "premise",
        "status_and_groups",
        "interpreted_by",
        "interpretation_policy_id",
        "interpretation_policy_version",
        "reason_codes",
    ],
)
def test_identity_binds_all_material(change: str) -> None:
    base = _identity()
    base_id = (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
            base
        )
    )
    if change == "premise":
        changed = _identity(
            premise=_premise(("inactive",), salt="changed-premise")
        )
    elif change == "status_and_groups":
        changed = _identity(
            premise=_premise(("alpha", "beta"), salt="changed-groups")
        )
    elif change == "interpreted_by":
        changed = replace(base, interpreted_by="other-interpreter")
    elif change == "interpretation_policy_id":
        changed = replace(base, interpretation_policy_id="other-policy")
    elif change == "interpretation_policy_version":
        changed = replace(base, interpretation_policy_version="2.0.0")
    else:
        changed = replace(base, reason_codes=("other-reason",))
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_interpretation_result_id(
            changed
        )
        != base_id
    )


def test_identity_uses_nested_premise_id_not_full_premise_projection() -> None:
    identity = _identity()
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_interpretation_result_identity_projection(
            identity
        )
    )
    assert projection["premise_id"] == (
        identity.premise.governed_knowledge_lifecycle_assertion_interpretation_premise_id
    )
    assert "premise" not in projection
    assert "assertions" not in projection


def test_canonicalizer_supported_values_and_unicode_nfc() -> None:
    value = {
        "text": "e\u0301",
        "items": (None, True, 3, 1.5, ["x"]),
    }
    assert domain._canonicalize(value) == {
        "text": "\u00e9",
        "items": [None, True, 3, 1.5, ["x"]],
    }


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_canonicalizer_rejects_non_finite_exact_float(value: float) -> None:
    with pytest.raises(
        ValueError,
        match="^canonical values must be finite$",
    ):
        domain._canonicalize(value)


@pytest.mark.parametrize(
    "value",
    [
        Decimal("1"),
        {1, 2},
        object(),
    ],
)
def test_canonicalizer_rejects_unsupported_exact_type(value) -> None:
    with pytest.raises(ValueError, match="^unsupported canonical value$"):
        domain._canonicalize(value)


def test_canonicalizer_rejects_non_string_mapping_key() -> None:
    with pytest.raises(
        ValueError,
        match="^canonical mapping keys must be strings$",
    ):
        domain._canonicalize({1: "value"})


def test_canonicalizer_rejects_unicode_normalized_key_collision() -> None:
    with pytest.raises(
        ValueError,
        match="^canonical mapping keys must remain unique$",
    ):
        domain._canonicalize({"\u00e9": 1, "e\u0301": 2})


def test_no_interpretation_timestamp_selected_assertion_or_authority_fields() -> None:
    all_fields = set(VALUE_GROUP_FIELDS) | set(IDENTITY_FIELDS) | set(
        RECORD_FIELDS
    )
    forbidden = {
        "interpreted_at",
        "interpretation_timestamp",
        "selected_assertion",
        "selected_assertion_id",
        "winning_assertion",
        "preferred_value",
        "current_effective",
        "confidence",
        "authority_rank",
        "recommendation",
        "resolution",
        "prior_state",
        "resulting_state",
        "current_state",
        "transition",
        "repository",
        "persistence",
        "serializer",
    }
    assert forbidden.isdisjoint(all_fields)
    assert forbidden.isdisjoint(_public_names())


def test_only_exact_public_structural_interpretation_callable_is_added() -> None:
    public_lower = {name.lower() for name in _public_names()}
    assert (
        "interpret_governed_knowledge_lifecycle_assertion_premise_structurally"
        in _public_names()
    )
    forbidden_fragments = {
        "derive",
        "constructor",
        "diagnostic",
        "selected",
        "transition",
        "current_state",
        "repository",
        "persistence",
        "serializer",
        "registry",
        "dispatch",
    }
    assert not any(
        fragment in name
        for name in public_lower
        for fragment in forbidden_fragments
    )


def test_package_initializer_has_no_result_export() -> None:
    initializer = Path("src/rie/domain/__init__.py").read_text(
        encoding="utf-8-sig"
    )
    assert (
        "governed_knowledge_lifecycle_assertion_interpretation_result"
        not in initializer
    )
    assert (
        "GovernedKnowledgeLifecycleAssertionInterpretationResult"
        not in initializer
    )


def test_module_has_no_filesystem_database_network_clock_or_randomness_dependency() -> None:
    path = Path(
        "src/rie/domain/"
        "governed_knowledge_lifecycle_assertion_interpretation_result.py"
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

def _interpret(
    premise: premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise
    | None = None,
    *,
    interpreted_by: str = "structural-interpreter",
    interpretation_policy_id: str = "policy.structural",
    interpretation_policy_version: str = "1.0.0",
    reason_codes: tuple[str, ...] = ("structural-composition",),
) -> domain.GovernedKnowledgeLifecycleAssertionInterpretationResult:
    return domain.interpret_governed_knowledge_lifecycle_assertion_premise_structurally(
        premise or _premise(("active",), salt="interpret"),
        interpreted_by,
        interpretation_policy_id,
        interpretation_policy_version,
        reason_codes,
    )


def test_structural_interpreter_exact_signature_annotations_and_defaults() -> None:
    signature = inspect.signature(
        domain.interpret_governed_knowledge_lifecycle_assertion_premise_structurally
    )
    parameters = tuple(signature.parameters.values())
    assert tuple(parameter.name for parameter in parameters) == (
        "premise",
        "interpreted_by",
        "interpretation_policy_id",
        "interpretation_policy_version",
        "reason_codes",
    )
    assert all(
        parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        for parameter in parameters
    )
    assert all(
        parameter.default is inspect.Parameter.empty
        for parameter in parameters
    )
    assert parameters[0].annotation is (
        premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise
    )
    assert parameters[1].annotation is str
    assert parameters[2].annotation is str
    assert parameters[3].annotation is str
    assert parameters[4].annotation == tuple[str, ...]
    assert signature.return_annotation is (
        domain.GovernedKnowledgeLifecycleAssertionInterpretationResult
    )


def test_structural_interpreter_supports_positional_and_keyword_invocation() -> None:
    premise = _premise(("active",), salt="invocation")
    positional = (
        domain.interpret_governed_knowledge_lifecycle_assertion_premise_structurally(
            premise,
            "structural-interpreter",
            "policy.structural",
            "1.0.0",
            ("structural-composition",),
        )
    )
    keyword = (
        domain.interpret_governed_knowledge_lifecycle_assertion_premise_structurally(
            premise=premise,
            interpreted_by="structural-interpreter",
            interpretation_policy_id="policy.structural",
            interpretation_policy_version="1.0.0",
            reason_codes=("structural-composition",),
        )
    )
    expected = _record(
        _identity(
            premise=premise,
            interpreted_by="structural-interpreter",
            interpretation_policy_id="policy.structural",
            interpretation_policy_version="1.0.0",
            reason_codes=("structural-composition",),
        )
    )
    assert positional == keyword == expected


def test_structural_interpreter_requires_exact_premise_type_and_rejects_subclass() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "^premise must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremise$"
        ),
    ):
        domain.interpret_governed_knowledge_lifecycle_assertion_premise_structurally(
            object(),
            "",
            "",
            "",
            (),
        )

    class PremiseSubclass(
        premise_domain.GovernedKnowledgeLifecycleAssertionInterpretationPremise
    ):
        pass

    base = _premise(("active",), salt="premise-subclass")
    subclass = object.__new__(PremiseSubclass)
    for name, value in base.__dict__.items():
        object.__setattr__(subclass, name, value)
    with pytest.raises(
        ValueError,
        match=(
            "^premise must be an exact "
            "GovernedKnowledgeLifecycleAssertionInterpretationPremise$"
        ),
    ):
        _interpret(subclass)


def test_structural_interpreter_revalidates_nested_premise_and_assertions() -> None:
    premise = _premise(("active",), salt="interpreter-mutated-premise")
    object.__setattr__(premise, "declared_by", "")
    with pytest.raises(
        ValueError,
        match="^declared_by must be an exact non-empty string$",
    ):
        _interpret(premise)

    premise = _premise(("active",), salt="interpreter-mutated-assertion")
    object.__setattr__(premise.assertions[0], "asserted_by", "")
    with pytest.raises(
        ValueError,
        match="^asserted_by must be an exact non-empty string$",
    ):
        _interpret(premise)


@pytest.mark.parametrize(
    "interpreted_by,policy_id,policy_version,message",
    [
        (
            "",
            "",
            "",
            "interpreted_by must be an exact non-empty string",
        ),
        (
            "interpreter",
            "",
            "",
            "interpretation_policy_id must be an exact non-empty string",
        ),
        (
            "interpreter",
            "policy",
            "",
            "interpretation_policy_version must be an exact non-empty string",
        ),
    ],
)
def test_structural_interpreter_provenance_validation_order(
    interpreted_by,
    policy_id,
    policy_version,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        _interpret(
            interpreted_by=interpreted_by,
            interpretation_policy_id=policy_id,
            interpretation_policy_version=policy_version,
            reason_codes=(),
        )


@pytest.mark.parametrize(
    "reason_codes,message",
    [
        ((), "reason_codes must be a non-empty tuple"),
        ([], "reason_codes must be a non-empty tuple"),
        (("",), "reason_codes must be an exact non-empty string"),
        ((1,), "reason_codes must be an exact non-empty string"),
        (
            ("same", "same"),
            "reason_codes must contain unique values",
        ),
        (
            ("z", "a"),
            "reason_codes must be lexicographically ordered",
        ),
    ],
)
def test_structural_interpreter_reason_code_validation(
    reason_codes,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=f"^{re.escape(message)}$"):
        _interpret(reason_codes=reason_codes)


@pytest.mark.parametrize(
    "values,completeness,expected_status,expected_group_count",
    [
        (
            (),
            premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE,
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY,
            0,
        ),
        (
            (),
            premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_INCOMPLETE,
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_EMPTY,
            0,
        ),
        (
            ("active", "active"),
            premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE,
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM,
            1,
        ),
        (
            ("active", "withdrawn"),
            premise_domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_PREMISE_COMPLETENESS_COMPLETE,
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY,
            2,
        ),
    ],
)
def test_structural_interpreter_empty_uniform_and_contradictory_results(
    values: tuple[str, ...],
    completeness: str,
    expected_status: str,
    expected_group_count: int,
) -> None:
    premise = _premise(
        values,
        completeness=completeness,
        salt="interpreter-structure-" + str(expected_group_count),
    )
    result = _interpret(premise)
    expected_status_value, expected_groups = _expected_structure(premise)
    assert result.result_status == expected_status == expected_status_value
    assert result.assertion_value_groups == expected_groups
    assert len(result.assertion_value_groups) == expected_group_count
    assert result.premise is premise


def test_structural_interpreter_unicode_nfc_grouping_without_other_normalization() -> None:
    nfc_result = _interpret(
        _premise(("\u00e9", "e\u0301"), salt="interpreter-nfc")
    )
    assert nfc_result.result_status == (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_UNIFORM
    )
    assert tuple(
        group.assertion_value for group in nfc_result.assertion_value_groups
    ) == ("\u00e9",)

    distinct_result = _interpret(
        _premise(
            ("Active", "active", "active ", "enabled"),
            salt="interpreter-distinct",
        )
    )
    assert distinct_result.result_status == (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_INTERPRETATION_RESULT_STATUS_CONTRADICTORY
    )
    assert tuple(
        group.assertion_value for group in distinct_result.assertion_value_groups
    ) == ("Active", "active", "active ", "enabled")


def test_structural_interpreter_preserves_each_assertion_id_exactly_once() -> None:
    premise = _premise(
        ("active", "withdrawn", "active"),
        salt="interpreter-membership",
    )
    result = _interpret(premise)
    actual_ids = tuple(
        assertion_id
        for group in result.assertion_value_groups
        for assertion_id in group.assertion_ids
    )
    expected_ids = tuple(
        sorted(
            assertion.governed_knowledge_lifecycle_assertion_id
            for assertion in premise.assertions
        )
    )
    assert tuple(sorted(actual_ids)) == expected_ids
    assert len(actual_ids) == len(set(actual_ids)) == len(premise.assertions)


def test_structural_interpreter_is_deterministic_and_identity_binds_provenance() -> None:
    premise = _premise(
        ("active", "withdrawn"),
        salt="interpreter-identity",
    )
    base = _interpret(premise)
    repeated = _interpret(premise)
    assert repeated == base
    assert (
        repeated.governed_knowledge_lifecycle_assertion_interpretation_result_id
        == base.governed_knowledge_lifecycle_assertion_interpretation_result_id
    )

    changed_results = (
        _interpret(premise, interpreted_by="other-interpreter"),
        _interpret(premise, interpretation_policy_id="policy.other"),
        _interpret(premise, interpretation_policy_version="2.0.0"),
        _interpret(premise, reason_codes=("other-reason",)),
    )
    assert all(
        result.governed_knowledge_lifecycle_assertion_interpretation_result_id
        != base.governed_knowledge_lifecycle_assertion_interpretation_result_id
        for result in changed_results
    )


def test_structural_interpreter_preserves_inputs_and_returns_frozen_record() -> None:
    premise = _premise(("active",), salt="interpreter-immutable")
    before = premise
    before_assertions = premise.assertions
    reason_codes = ("structural-composition",)
    result = _interpret(premise, reason_codes=reason_codes)
    assert premise is before
    assert premise.assertions is before_assertions
    assert result.premise is premise
    assert result.reason_codes is reason_codes
    with pytest.raises(FrozenInstanceError):
        result.interpreted_by = "changed"  # type: ignore[misc]


def test_structural_interpreter_has_no_timestamp_selection_transition_or_storage_surface() -> None:
    result = _interpret()
    forbidden = {
        "interpreted_at",
        "interpretation_timestamp",
        "selected_assertion",
        "selected_assertion_id",
        "winning_assertion",
        "preferred_value",
        "current_effective",
        "confidence",
        "authority_rank",
        "recommendation",
        "resolution",
        "prior_state",
        "resulting_state",
        "current_state",
        "transition",
        "repository",
        "persistence",
        "serializer",
    }
    assert forbidden.isdisjoint(result.__dict__)
    signature = inspect.signature(
        domain.interpret_governed_knowledge_lifecycle_assertion_premise_structurally
    )
    assert forbidden.isdisjoint(signature.parameters)


def test_structural_interpreter_reuses_private_structural_derivation_once() -> None:
    source = Path(
        "src/rie/domain/"
        "governed_knowledge_lifecycle_assertion_interpretation_result.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name
        == "interpret_governed_knowledge_lifecycle_assertion_premise_structurally"
    )
    calls = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_derive_expected_structure"
    ]
    assert len(calls) == 1


def test_structural_interpreter_does_not_add_policy_registry_or_external_dependencies() -> None:
    source = Path(
        "src/rie/domain/"
        "governed_knowledge_lifecycle_assertion_interpretation_result.py"
    ).read_text(encoding="utf-8")
    lowered = source.lower()
    forbidden = {
        "policy_registry",
        "plugin",
        "repository",
        "persistence",
        "serializer",
        "sqlite",
        "requests",
        "socket",
        "random",
        "uuid",
        "datetime",
        "time.time",
        "os.environ",
        "callback",
        "dispatch",
    }
    assert all(item not in lowered for item in forbidden)
