import hashlib
import inspect
import json

import pytest

from rie.persisted_evidence_knowledge_construction import (
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_ID,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_POLICY_VERSION,
    PERSISTED_EVIDENCE_KNOWLEDGE_COMPATIBILITY_RECORD_CONTRACT_VERSION,
    canonicalize_persisted_evidence_knowledge_compatibility_identity,
    derive_persisted_evidence_knowledge_compatibility_record_id,
)


def _values(**changes: object) -> dict[str, object]:
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
            "ar1_" + "8" * 64,
            "ar1_" + "7" * 64,
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


def test_function_signatures_are_exact_keyword_only_identity_fields() -> None:
    expected = (
        "contract_version",
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
    for function in (
        canonicalize_persisted_evidence_knowledge_compatibility_identity,
        derive_persisted_evidence_knowledge_compatibility_record_id,
    ):
        parameters = inspect.signature(function).parameters
        assert tuple(parameters) == expected
        assert all(
            parameter.kind is inspect.Parameter.KEYWORD_ONLY
            for parameter in parameters.values()
        )


def test_known_canonical_bytes_and_identifier_fixture() -> None:
    canonical = (
        canonicalize_persisted_evidence_knowledge_compatibility_identity(
            **_values()
        )
    )
    expected_object = _values(
        acceptance_record_ids=(
            "ar1_" + "7" * 64,
            "ar1_" + "8" * 64,
        )
    )
    expected = json.dumps(
        expected_object,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    assert canonical == expected
    assert len(canonical) == 1091
    assert hashlib.sha256(canonical).hexdigest() == (
        "1378b67fedd1c59c7a11c5a457bca0a3"
        "d126d641105ee32378b1804d84360113"
    )
    assert derive_persisted_evidence_knowledge_compatibility_record_id(
        **_values()
    ) == (
        "pekc1_1378b67fedd1c59c7a11c5a457bca0a3"
        "d126d641105ee32378b1804d84360113"
    )


def test_canonical_bytes_are_utf8_compact_and_have_no_bom_or_newline() -> None:
    canonical = (
        canonicalize_persisted_evidence_knowledge_compatibility_identity(
            **_values(source_id="sumber-cafe")
        )
    )
    assert not canonical.startswith(b"\xef\xbb\xbf")
    assert not canonical.endswith(b"\n")
    assert b" " not in canonical
    assert json.loads(canonical.decode("utf-8"))["source_id"] == "sumber-cafe"


def test_acceptance_record_input_order_does_not_affect_identity() -> None:
    forward = _values(
        acceptance_record_ids=(
            "ar1_" + "7" * 64,
            "ar1_" + "8" * 64,
        )
    )
    reverse = _values(
        acceptance_record_ids=(
            "ar1_" + "8" * 64,
            "ar1_" + "7" * 64,
        )
    )
    assert (
        canonicalize_persisted_evidence_knowledge_compatibility_identity(
            **forward
        )
        == canonicalize_persisted_evidence_knowledge_compatibility_identity(
            **reverse
        )
    )
    assert derive_persisted_evidence_knowledge_compatibility_record_id(
        **forward
    ) == derive_persisted_evidence_knowledge_compatibility_record_id(
        **reverse
    )


def test_duplicate_acceptance_record_ids_are_rejected_not_repaired() -> None:
    duplicate = "ar1_" + "7" * 64
    with pytest.raises(ValueError, match="unique"):
        canonicalize_persisted_evidence_knowledge_compatibility_identity(
            **_values(acceptance_record_ids=(duplicate, duplicate))
        )


@pytest.mark.parametrize(
    ("field_name", "replacement"),
    (
        ("contract_version", "other-contract"),
        ("repository_revision_id", "evr1_" + "9" * 64),
        ("source_id", "source-2"),
        ("revision_number", 2),
        ("previous_revision_id", "evr1_" + "9" * 64),
        ("collection_id", "evc1_" + "9" * 64),
        ("collection_payload_digest", "9" * 64),
        ("repository_audit_id", "eva1_" + "9" * 64),
        ("traceable_evidence_id", "evm1_" + "9" * 64),
        ("accepted_evidence_id", "ev1_" + "9" * 64),
        ("acceptance_record_ids", ("ar1_" + "9" * 64,)),
        ("construction_rule_id", "other-rule"),
        ("construction_rule_version", "2.0.0"),
        ("compatibility_policy_id", "other-policy"),
        ("compatibility_policy_version", "2.0.0"),
    ),
)
def test_every_identity_field_changes_or_is_rejected(
    field_name: str,
    replacement: object,
) -> None:
    baseline = derive_persisted_evidence_knowledge_compatibility_record_id(
        **_values()
    )
    changes = {field_name: replacement}
    if field_name == "revision_number":
        changes["previous_revision_id"] = "evr1_" + "8" * 64
    if field_name == "previous_revision_id":
        changes["revision_number"] = 2
    if field_name in (
        "contract_version",
        "compatibility_policy_id",
        "compatibility_policy_version",
    ):
        with pytest.raises(ValueError):
            derive_persisted_evidence_knowledge_compatibility_record_id(
                **_values(**changes)
            )
    else:
        changed = derive_persisted_evidence_knowledge_compatibility_record_id(
            **_values(**changes)
        )
        assert changed != baseline


@pytest.mark.parametrize(
    "changes",
    (
        {"repository_revision_id": "evr1_bad"},
        {"revision_number": True},
        {"previous_revision_id": "evr1_bad", "revision_number": 2},
        {"collection_payload_digest": "A" * 64},
        {"acceptance_record_ids": []},
        {"construction_rule_id": "   "},
    ),
)
def test_invalid_identity_values_fail_closed(changes: dict[str, object]) -> None:
    with pytest.raises((TypeError, ValueError)):
        canonicalize_persisted_evidence_knowledge_compatibility_identity(
            **_values(**changes)
        )
