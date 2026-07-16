from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import ast
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import pytest

import rie.domain.governed_knowledge_lifecycle_assertion as domain


NOW = datetime(2026, 7, 16, 12, 34, 56, 123456, tzinfo=timezone.utc)
GK_ID = "gk1_" + "1" * 64
PUBLIC_SYMBOLS = {
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_ID",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_VERSION",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_CANONICALIZATION_CONTRACT",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_DIGEST_ALGORITHM",
    "GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED",
    "GovernedKnowledgeLifecycleAssertionIdentityInput",
    "GovernedKnowledgeLifecycleAssertion",
    "canonical_governed_knowledge_lifecycle_assertion_identity_projection",
    "canonical_governed_knowledge_lifecycle_assertion_identity_bytes",
    "compute_governed_knowledge_lifecycle_assertion_id",
    "governed_knowledge_lifecycle_assertion_identity_input_from_record",
}
IDENTITY_FIELDS = (
    "contract_version",
    "governed_knowledge_id",
    "governed_knowledge_contract_version",
    "assertion_scope",
    "assertion_scope_reference",
    "assertion_value",
    "asserted_by",
    "asserted_at",
    "assertion_policy_id",
    "assertion_policy_version",
    "reason_codes",
)
RECORD_FIELDS = (
    "governed_knowledge_lifecycle_assertion_id",
    *IDENTITY_FIELDS,
)
PROJECTION_KEYS = (
    *IDENTITY_FIELDS,
    "identity_canonicalization_contract",
)


def _identity(**changes: object) -> domain.GovernedKnowledgeLifecycleAssertionIdentityInput:
    values: dict[str, object] = {
        "contract_version": (
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION
        ),
        "governed_knowledge_id": GK_ID,
        "governed_knowledge_contract_version": "governed-knowledge-v1",
        "assertion_scope": (
            domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED
        ),
        "assertion_scope_reference": "lifecycle-assertion-reference-1",
        "assertion_value": "candidate",
        "asserted_by": "caller-1",
        "asserted_at": NOW,
        "assertion_policy_id": "policy-1",
        "assertion_policy_version": "1.0.0",
        "reason_codes": ("caller_supplied_lifecycle_assertion",),
    }
    values.update(changes)
    return domain.GovernedKnowledgeLifecycleAssertionIdentityInput(
        **values  # type: ignore[arg-type]
    )


def _record(
    identity: domain.GovernedKnowledgeLifecycleAssertionIdentityInput | None = None,
    **changes: object,
) -> domain.GovernedKnowledgeLifecycleAssertion:
    material = identity or _identity()
    values: dict[str, object] = {
        "governed_knowledge_lifecycle_assertion_id": (
            domain.compute_governed_knowledge_lifecycle_assertion_id(material)
        ),
        **{
            field_name: getattr(material, field_name)
            for field_name in IDENTITY_FIELDS
        },
    }
    values.update(changes)
    return domain.GovernedKnowledgeLifecycleAssertion(
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


def test_constant_values_are_exact() -> None:
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_CONTRACT_VERSION
        == "governed-knowledge-lifecycle-assertion-v1"
    )
    assert domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_ID_PREFIX == "gkla1_"
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_ID
        == "rcis-governed-knowledge-lifecycle-assertion-identity"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_POLICY_VERSION
        == "1.0.0"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_IDENTITY_CANONICALIZATION_CONTRACT
        == "rcis-governed-knowledge-lifecycle-assertion-canonical-json-v1"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_DIGEST_ALGORITHM
        == "sha256"
    )
    assert (
        domain.GOVERNED_KNOWLEDGE_LIFECYCLE_ASSERTION_SCOPE_DECLARED
        == "governed_knowledge_lifecycle_assertion_for_declared_subject"
    )


def test_upstream_contract_version_import_is_private_and_literal_is_not_duplicated() -> None:
    path = Path("src/rie/domain/governed_knowledge_lifecycle_assertion.py")
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "rie.domain.governed_knowledge"
    ]
    assert len(imports) == 1
    assert [
        (alias.name, alias.asname)
        for alias in imports[0].names
    ] == [
        (
            "GOVERNED_KNOWLEDGE_CONTRACT_VERSION",
            "_GOVERNED_KNOWLEDGE_CONTRACT_VERSION",
        )
    ]
    assert "governed-knowledge-v1" not in source
    assert "GOVERNED_KNOWLEDGE_CONTRACT_VERSION" not in _public_names()


def test_identity_input_field_order_and_count_are_exact() -> None:
    assert tuple(item.name for item in fields(
        domain.GovernedKnowledgeLifecycleAssertionIdentityInput
    )) == IDENTITY_FIELDS
    assert len(IDENTITY_FIELDS) == 11


def test_final_record_field_order_and_count_are_exact() -> None:
    assert tuple(item.name for item in fields(
        domain.GovernedKnowledgeLifecycleAssertion
    )) == RECORD_FIELDS
    assert len(RECORD_FIELDS) == 12


def test_identity_projection_keys_and_count_are_exact() -> None:
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_identity_projection(
            _identity()
        )
    )
    assert tuple(projection) == PROJECTION_KEYS
    assert len(projection) == 12
    assert "governed_knowledge_lifecycle_assertion_id" not in projection


def test_canonical_bytes_are_deterministic_and_exact() -> None:
    identity = _identity()
    projection = (
        domain.canonical_governed_knowledge_lifecycle_assertion_identity_projection(
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
        domain.canonical_governed_knowledge_lifecycle_assertion_identity_bytes(
            identity
        )
        == expected
    )
    assert (
        domain.canonical_governed_knowledge_lifecycle_assertion_identity_bytes(
            identity
        )
        == expected
    )


def test_deterministic_id_prefix_and_digest_shape() -> None:
    identity = _identity()
    assertion_id = (
        domain.compute_governed_knowledge_lifecycle_assertion_id(identity)
    )
    assert re.fullmatch(r"gkla1_[0-9a-f]{64}", assertion_id)
    assert assertion_id == (
        "gkla1_"
        + hashlib.sha256(
            domain.canonical_governed_knowledge_lifecycle_assertion_identity_bytes(
                identity
            )
        ).hexdigest()
    )


@pytest.mark.parametrize(
    ("value", "message"),
    (
        (
            1,
            "governed_knowledge_lifecycle_assertion_id "
            "must be an exact non-empty string",
        ),
        (
            "",
            "governed_knowledge_lifecycle_assertion_id "
            "must be an exact non-empty string",
        ),
        (
            "gkla1_bad",
            "governed_knowledge_lifecycle_assertion_id has an invalid format",
        ),
    ),
)
def test_declared_assertion_id_type_and_format_rejection(
    value: object,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=re.escape(message)):
        _record(
            governed_knowledge_lifecycle_assertion_id=value
        )


def test_declared_assertion_id_mismatch_rejection() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "governed_knowledge_lifecycle_assertion_id "
            "does not match identity"
        ),
    ):
        _record(
            governed_knowledge_lifecycle_assertion_id=(
                "gkla1_" + "0" * 64
            )
        )


def test_record_to_input_transfers_exact_material() -> None:
    identity = _identity()
    record = _record(identity)
    assert (
        domain.governed_knowledge_lifecycle_assertion_identity_input_from_record(
            record
        )
        == identity
    )


def test_identity_input_is_frozen() -> None:
    identity = _identity()
    with pytest.raises(FrozenInstanceError):
        identity.assertion_value = "changed"  # type: ignore[misc]


def test_final_record_is_frozen() -> None:
    record = _record()
    with pytest.raises(FrozenInstanceError):
        record.assertion_value = "changed"  # type: ignore[misc]


def test_helpers_reject_wrong_exact_types_and_subclasses() -> None:
    expected_identity_message = (
        "identity_input must be an exact "
        "GovernedKnowledgeLifecycleAssertionIdentityInput"
    )

    class IdentitySubclass(
        domain.GovernedKnowledgeLifecycleAssertionIdentityInput
    ):
        pass

    identity_subclass = IdentitySubclass(
        **{
            field_name: getattr(_identity(), field_name)
            for field_name in IDENTITY_FIELDS
        }
    )
    for value in (object(), identity_subclass):
        for helper in (
            domain.canonical_governed_knowledge_lifecycle_assertion_identity_projection,
            domain.canonical_governed_knowledge_lifecycle_assertion_identity_bytes,
            domain.compute_governed_knowledge_lifecycle_assertion_id,
        ):
            with pytest.raises(
                ValueError,
                match=expected_identity_message,
            ):
                helper(value)  # type: ignore[arg-type]

    class RecordSubclass(domain.GovernedKnowledgeLifecycleAssertion):
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
                "GovernedKnowledgeLifecycleAssertion"
            ),
        ):
            domain.governed_knowledge_lifecycle_assertion_identity_input_from_record(
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
        match=(
            "governed_knowledge_id has an invalid format"
        ),
    ):
        _identity(
            governed_knowledge_id="wrong",
            governed_knowledge_contract_version="wrong",
            assertion_scope="wrong",
        )
    with pytest.raises(
        ValueError,
        match="unsupported governed_knowledge_contract_version",
    ):
        _identity(
            governed_knowledge_contract_version="wrong",
            assertion_scope="wrong",
            assertion_scope_reference="",
        )


def test_final_record_validation_precedence_is_id_then_identity_then_mismatch() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "governed_knowledge_lifecycle_assertion_id has an invalid format"
        ),
    ):
        _record(
            governed_knowledge_lifecycle_assertion_id="wrong",
            contract_version="wrong",
        )
    with pytest.raises(ValueError, match="unsupported contract_version"):
        _record(
            governed_knowledge_lifecycle_assertion_id=(
                "gkla1_" + "0" * 64
            ),
            contract_version="wrong",
        )
    with pytest.raises(
        ValueError,
        match=(
            "governed_knowledge_lifecycle_assertion_id "
            "does not match identity"
        ),
    ):
        _record(
            governed_knowledge_lifecycle_assertion_id=(
                "gkla1_" + "0" * 64
            )
        )


def test_projection_revalidates_mutated_identity_input() -> None:
    identity = _identity()
    object.__setattr__(identity, "assertion_value", "")
    with pytest.raises(
        ValueError,
        match="assertion_value must be an exact non-empty string",
    ):
        domain.canonical_governed_knowledge_lifecycle_assertion_identity_projection(
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


def test_assertion_scope_rejection() -> None:
    with pytest.raises(ValueError, match="unsupported assertion_scope"):
        _identity(assertion_scope="unsupported")


@pytest.mark.parametrize(
    "field_name",
    (
        "assertion_scope_reference",
        "assertion_value",
        "asserted_by",
        "assertion_policy_id",
        "assertion_policy_version",
    ),
)
@pytest.mark.parametrize("value", ("", " ", 1))
def test_required_string_field_rejection(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            f"{field_name} must be an exact non-empty string"
        ),
    ):
        _identity(**{field_name: value})


def test_non_datetime_and_naive_datetime_rejection() -> None:
    with pytest.raises(
        ValueError,
        match="asserted_at must be an exact datetime",
    ):
        _identity(asserted_at="2026-07-16")  # type: ignore[arg-type]
    with pytest.raises(
        ValueError,
        match="asserted_at must be timezone-aware",
    ):
        _identity(asserted_at=NOW.replace(tzinfo=None))


def test_equivalent_instants_across_offsets_have_same_identity() -> None:
    offset = timezone(timedelta(hours=7))
    local = NOW.astimezone(offset)
    assert (
        domain.canonical_governed_knowledge_lifecycle_assertion_identity_bytes(
            _identity(asserted_at=NOW)
        )
        == domain.canonical_governed_knowledge_lifecycle_assertion_identity_bytes(
            _identity(asserted_at=local)
        )
    )
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_id(
            _identity(asserted_at=NOW)
        )
        == domain.compute_governed_knowledge_lifecycle_assertion_id(
            _identity(asserted_at=local)
        )
    )


def test_different_microseconds_are_distinct() -> None:
    first = _identity(asserted_at=NOW)
    second = _identity(asserted_at=NOW + timedelta(microseconds=1))
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_id(first)
        != domain.compute_governed_knowledge_lifecycle_assertion_id(second)
    )


def test_unicode_nfc_equivalence() -> None:
    composed = "café"
    decomposed = unicodedata.normalize("NFD", composed)
    assert composed != decomposed
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_id(
            _identity(assertion_value=composed)
        )
        == domain.compute_governed_knowledge_lifecycle_assertion_id(
            _identity(assertion_value=decomposed)
        )
    )


@pytest.mark.parametrize("value", ((), [], "reason"))
def test_reason_codes_require_non_empty_tuple(value: object) -> None:
    with pytest.raises(
        ValueError,
        match="reason_codes must be a non-empty tuple",
    ):
        _identity(reason_codes=value)


@pytest.mark.parametrize("value", ((1,), ("",), (" ",)))
def test_reason_codes_require_exact_non_empty_strings(value: object) -> None:
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


@pytest.mark.parametrize(
    "value",
    (
        object(),
        {1, 2},
        datetime(2026, 7, 16, tzinfo=timezone.utc),
        True.__class__("x") if False else complex(1, 2),
    ),
)
def test_unsupported_canonical_exact_type_rejection(value: object) -> None:
    with pytest.raises(ValueError, match="unsupported canonical value"):
        domain._canonicalize(value)


@pytest.mark.parametrize("value", (float("nan"), float("inf"), float("-inf")))
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
        domain._canonicalize({"é": 1, "e\u0301": 2})


def test_identical_identity_material_gives_identical_id() -> None:
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_id(_identity())
        == domain.compute_governed_knowledge_lifecycle_assertion_id(_identity())
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"contract_version": "governed-knowledge-lifecycle-assertion-v2"},
        {"governed_knowledge_id": "gk1_" + "2" * 64},
        {"governed_knowledge_contract_version": "governed-knowledge-v2"},
        {"assertion_scope": "another_scope"},
        {"assertion_scope_reference": "reference-2"},
        {"assertion_value": "accepted"},
        {"asserted_by": "caller-2"},
        {"asserted_at": NOW + timedelta(microseconds=1)},
        {"assertion_policy_id": "policy-2"},
        {"assertion_policy_version": "2.0.0"},
        {"reason_codes": ("another_reason",)},
    ),
)
def test_each_material_field_changes_or_fails_closed(
    changes: dict[str, object],
) -> None:
    base = _identity()
    base_id = domain.compute_governed_knowledge_lifecycle_assertion_id(base)
    try:
        changed = _identity(**changes)
    except ValueError:
        return
    assert (
        domain.compute_governed_knowledge_lifecycle_assertion_id(changed)
        != base_id
    )


def test_contradictory_assertion_values_coexist_as_distinct_valid_records() -> None:
    first_identity = _identity(assertion_value="candidate")
    second_identity = _identity(assertion_value="withdrawn")
    first = _record(first_identity)
    second = _record(second_identity)
    assert first.assertion_value != second.assertion_value
    assert (
        first.governed_knowledge_lifecycle_assertion_id
        != second.governed_knowledge_lifecycle_assertion_id
    )
    assert isinstance(first, domain.GovernedKnowledgeLifecycleAssertion)
    assert isinstance(second, domain.GovernedKnowledgeLifecycleAssertion)


def test_no_diagnostics_field_or_unapproved_behavioral_surface() -> None:
    identity_names = {item.name for item in fields(
        domain.GovernedKnowledgeLifecycleAssertionIdentityInput
    )}
    record_names = {item.name for item in fields(
        domain.GovernedKnowledgeLifecycleAssertion
    )}
    forbidden = {
        "diagnostics",
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


def test_package_initializer_has_no_lifecycle_assertion_export() -> None:
    initializer = Path("src/rie/domain/__init__.py").read_text(
        encoding="utf-8-sig"
    )
    assert "governed_knowledge_lifecycle_assertion" not in initializer
    assert "GovernedKnowledgeLifecycleAssertion" not in initializer


def test_module_has_no_filesystem_database_network_clock_or_randomness_dependency() -> None:
    path = Path("src/rie/domain/governed_knowledge_lifecycle_assertion.py")
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
