from dataclasses import MISSING, FrozenInstanceError, fields, replace
import json
from types import MappingProxyType
from unicodedata import normalize

import pytest

from rie.application.evidence_candidate import EvidenceCandidate
from rie.application.evidence_candidate_snapshot import (
    EVIDENCE_CANDIDATE_SNAPSHOT_CANONICALIZATION_CONTRACT_VERSION,
    EVIDENCE_CANDIDATE_SNAPSHOT_DIGEST_ALGORITHM,
    EVIDENCE_CANDIDATE_SNAPSHOT_KEYS,
    EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_ID,
    EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_VERSION,
    EvidenceCandidateSnapshotResult,
    calculate_evidence_candidate_snapshot,
    canonicalize_evidence_candidate_snapshot,
)


EXPECTED_KEYS = (
    "source_id",
    "source_type",
    "source_checksum_algorithm",
    "source_checksum",
    "source_authority",
    "source_lifecycle_state",
    "source_reference",
    "execution_id",
    "producer_name",
    "producer_version",
    "result_contract_version",
    "execution_timestamp",
    "payload_type",
    "raw_payload",
    "locator",
    "warnings",
    "errors",
    "candidate_contract_version",
)


def _candidate(**changes: object) -> EvidenceCandidate:
    values = {
        "source_id": "source-1",
        "source_type": "pdf",
        "source_checksum_algorithm": "sha256",
        "source_checksum": "a" * 64,
        "source_authority": "official",
        "source_lifecycle_state": "active",
        "source_reference": "official/source.pdf",
        "execution_id": "collection-1",
        "producer_name": "structural-inspector",
        "producer_version": "1.0.0",
        "result_contract_version": "result-v1",
        "execution_timestamp": "2026-07-12T10:00:00+00:00",
        "payload_type": "document_structural_metadata",
        "raw_payload": (("page_count", 1), ("title", "SV300")),
        "locator": ("page_index", 0),
        "warnings": ("warning-one",),
        "errors": (),
        "candidate_contract_version": "candidate-v1",
    }
    values.update(changes)

    candidate = object.__new__(EvidenceCandidate)
    for field_name in EXPECTED_KEYS:
        object.__setattr__(candidate, field_name, values[field_name])
    return candidate


def test_snapshot_result_is_frozen() -> None:
    result = calculate_evidence_candidate_snapshot(_candidate())

    with pytest.raises(FrozenInstanceError):
        result.digest_algorithm = "sha512"


def test_snapshot_result_fields_have_no_defaults() -> None:
    assert all(
        field.default is MISSING
        and field.default_factory is MISSING
        for field in fields(EvidenceCandidateSnapshotResult)
    )


def test_snapshot_result_has_exact_six_fields() -> None:
    assert tuple(
        field.name for field in fields(EvidenceCandidateSnapshotResult)
    ) == (
        "candidate_snapshot_digest",
        "digest_algorithm",
        "snapshot_policy_id",
        "snapshot_policy_version",
        "canonicalization_contract_version",
        "canonical_byte_length",
    )


def test_snapshot_uses_exact_eighteen_candidate_keys_in_order() -> None:
    assert EVIDENCE_CANDIDATE_SNAPSHOT_KEYS == EXPECTED_KEYS


def test_canonical_json_uses_exact_fixed_key_order() -> None:
    decoded = json.loads(
        canonicalize_evidence_candidate_snapshot(_candidate()).decode("utf-8")
    )

    assert tuple(decoded) == EXPECTED_KEYS


def test_canonical_json_has_no_insignificant_whitespace() -> None:
    canonical_text = canonicalize_evidence_candidate_snapshot(
        _candidate()
    ).decode("utf-8")

    assert ": " not in canonical_text
    assert ", " not in canonical_text
    assert "\n" not in canonical_text
    assert "\r" not in canonical_text


def test_canonical_json_is_utf8_and_preserves_non_ascii_text() -> None:
    canonical = canonicalize_evidence_candidate_snapshot(
        _candidate(source_id="sumber-Çilek")
    )

    assert "Çilek".encode("utf-8") in canonical
    assert "\\u00c7" not in canonical.decode("utf-8")


def test_text_is_normalized_to_nfc_recursively() -> None:
    decomposed = "Cafe\u0301"
    decoded = json.loads(
        canonicalize_evidence_candidate_snapshot(
            _candidate(
                source_id=decomposed,
                raw_payload=(("title", decomposed),),
                locator=("label", decomposed),
            )
        ).decode("utf-8")
    )

    assert decoded["source_id"] == normalize("NFC", decomposed)
    assert decoded["raw_payload"][0][1] == normalize("NFC", decomposed)
    assert decoded["locator"][1] == normalize("NFC", decomposed)


def test_canonically_equivalent_unicode_has_same_digest() -> None:
    composed = _candidate(
        source_id="Café",
        raw_payload=(("title", "Café"),),
    )
    decomposed = _candidate(
        source_id="Cafe\u0301",
        raw_payload=(("title", "Cafe\u0301"),),
    )

    assert calculate_evidence_candidate_snapshot(
        composed
    ) == calculate_evidence_candidate_snapshot(decomposed)


def test_tuple_order_is_preserved() -> None:
    first = _candidate(raw_payload=(("a", 1), ("b", 2)))
    second = _candidate(raw_payload=(("b", 2), ("a", 1)))

    assert (
        calculate_evidence_candidate_snapshot(first).candidate_snapshot_digest
        != calculate_evidence_candidate_snapshot(second).candidate_snapshot_digest
    )


def test_mapping_proxy_order_is_preserved_as_ordered_pairs() -> None:
    candidate = _candidate(
        raw_payload=MappingProxyType({"first": 1, "second": 2})
    )
    decoded = json.loads(
        canonicalize_evidence_candidate_snapshot(candidate).decode("utf-8")
    )

    assert decoded["raw_payload"] == [["first", 1], ["second", 2]]


def test_mapping_proxy_order_changes_digest() -> None:
    first = _candidate(
        raw_payload=MappingProxyType({"first": 1, "second": 2})
    )
    second = _candidate(
        raw_payload=MappingProxyType({"second": 2, "first": 1})
    )

    assert (
        calculate_evidence_candidate_snapshot(first).candidate_snapshot_digest
        != calculate_evidence_candidate_snapshot(second).candidate_snapshot_digest
    )


def test_repeated_calculation_is_deterministic() -> None:
    candidate = _candidate()
    results = tuple(
        calculate_evidence_candidate_snapshot(candidate) for _ in range(5)
    )

    assert len(set(results)) == 1


def test_snapshot_result_uses_lowercase_sha256() -> None:
    result = calculate_evidence_candidate_snapshot(_candidate())

    assert result.digest_algorithm == "sha256"
    assert len(result.candidate_snapshot_digest) == 64
    assert (
        result.candidate_snapshot_digest
        == result.candidate_snapshot_digest.lower()
    )
    assert all(
        character in "0123456789abcdef"
        for character in result.candidate_snapshot_digest
    )


def test_snapshot_result_exposes_exact_policy_versions() -> None:
    result = calculate_evidence_candidate_snapshot(_candidate())

    assert (
        result.digest_algorithm
        == EVIDENCE_CANDIDATE_SNAPSHOT_DIGEST_ALGORITHM
    )
    assert result.snapshot_policy_id == EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_ID
    assert (
        result.snapshot_policy_version
        == EVIDENCE_CANDIDATE_SNAPSHOT_POLICY_VERSION
    )
    assert (
        result.canonicalization_contract_version
        == EVIDENCE_CANDIDATE_SNAPSHOT_CANONICALIZATION_CONTRACT_VERSION
    )
    assert result.canonical_byte_length == len(
        canonicalize_evidence_candidate_snapshot(_candidate())
    )


@pytest.mark.parametrize(
    ("field_name", "changed_value"),
    (
        ("source_id", "source-2"),
        ("source_type", "image"),
        ("source_checksum_algorithm", "sha512"),
        ("source_checksum", "b" * 64),
        ("source_authority", "reviewed"),
        ("source_lifecycle_state", "superseded"),
        ("source_reference", "other/source.pdf"),
        ("execution_id", "collection-2"),
        ("producer_name", "other-producer"),
        ("producer_version", "2.0.0"),
        ("result_contract_version", "result-v2"),
        ("execution_timestamp", "2026-07-13T10:00:00+00:00"),
        ("payload_type", "other-payload"),
        ("raw_payload", (("page_count", 2),)),
        ("locator", ("page_index", 1)),
        ("warnings", ("warning-two",)),
        ("errors", ("error-one",)),
        ("candidate_contract_version", "candidate-v2"),
    ),
)
def test_each_candidate_field_changes_snapshot_digest(
    field_name: str,
    changed_value: object,
) -> None:
    baseline = _candidate()
    changed = _candidate(**{field_name: changed_value})

    assert (
        calculate_evidence_candidate_snapshot(
            baseline
        ).candidate_snapshot_digest
        != calculate_evidence_candidate_snapshot(
            changed
        ).candidate_snapshot_digest
    )


@pytest.mark.parametrize(
    "field_name",
    tuple(
        key
        for key in EXPECTED_KEYS
        if key not in {"raw_payload", "locator", "warnings", "errors"}
    ),
)
def test_string_candidate_fields_reject_empty_values(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        canonicalize_evidence_candidate_snapshot(
            _candidate(**{field_name: " "})
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("raw_payload", []),
        ("raw_payload", {}),
        ("raw_payload", set()),
        ("raw_payload", bytearray(b"x")),
        ("locator", []),
        ("locator", {}),
        ("warnings", ["warning"]),
        ("errors", ["error"]),
    ),
)
def test_mutable_values_fail_closed(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        canonicalize_evidence_candidate_snapshot(
            _candidate(**{field_name: value})
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("raw_payload", (("value", float("nan")),)),
        ("raw_payload", (("value", float("inf")),)),
        ("locator", ("offset", float("-inf"))),
    ),
)
def test_non_finite_floats_fail_closed(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        canonicalize_evidence_candidate_snapshot(
            _candidate(**{field_name: value})
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("raw_payload", None),
        ("locator", None),
    ),
)
def test_null_values_fail_closed(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        canonicalize_evidence_candidate_snapshot(
            _candidate(**{field_name: value})
        )


@pytest.mark.parametrize(
    "bad_value",
    (
        object(),
        "not-a-candidate",
        None,
    ),
)
def test_snapshot_requires_exact_evidence_candidate(
    bad_value: object,
) -> None:
    with pytest.raises(ValueError, match="candidate"):
        canonicalize_evidence_candidate_snapshot(bad_value)


def test_warning_and_error_entries_must_be_non_empty_strings() -> None:
    with pytest.raises(ValueError, match=r"warnings\[0\]"):
        canonicalize_evidence_candidate_snapshot(
            _candidate(warnings=(" ",))
        )

    with pytest.raises(ValueError, match=r"errors\[0\]"):
        canonicalize_evidence_candidate_snapshot(
            _candidate(errors=(1,))
        )


def test_canonical_output_contains_only_eighteen_candidate_keys() -> None:
    decoded = json.loads(
        canonicalize_evidence_candidate_snapshot(_candidate()).decode("utf-8")
    )

    assert set(decoded) == set(EXPECTED_KEYS)
    assert len(decoded) == 18


def test_canonical_output_excludes_downstream_concepts() -> None:
    canonical_text = canonicalize_evidence_candidate_snapshot(
        _candidate()
    ).decode("utf-8").lower()

    for forbidden in (
        "eligibility_result",
        "accepted_evidence",
        "acceptance_record_id",
        "repository",
        "knowledge",
        "prompt",
        "materializer",
    ):
        assert forbidden not in canonical_text


def test_snapshot_calculation_has_no_implicit_clock_or_random_state() -> None:
    candidate = _candidate()
    results = tuple(
        calculate_evidence_candidate_snapshot(candidate) for _ in range(5)
    )

    assert len(set(results)) == 1


def test_result_rejects_non_sha256_algorithm() -> None:
    valid = calculate_evidence_candidate_snapshot(_candidate())

    with pytest.raises(ValueError, match="digest_algorithm"):
        replace(valid, digest_algorithm="sha512")


@pytest.mark.parametrize(
    "digest",
    (
        "A" * 64,
        "g" * 64,
        "0" * 63,
        "",
    ),
)
def test_result_rejects_invalid_snapshot_digest(digest: str) -> None:
    valid = calculate_evidence_candidate_snapshot(_candidate())

    with pytest.raises(ValueError, match="candidate_snapshot_digest"):
        replace(valid, candidate_snapshot_digest=digest)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("snapshot_policy_id", "other-policy"),
        ("snapshot_policy_version", "2.0.0"),
        ("canonicalization_contract_version", "candidate-json-v2"),
    ),
)
def test_result_rejects_unreviewed_policy_metadata(
    field_name: str,
    value: str,
) -> None:
    valid = calculate_evidence_candidate_snapshot(_candidate())

    with pytest.raises(ValueError, match=field_name):
        replace(valid, **{field_name: value})


@pytest.mark.parametrize("byte_length", (0, -1, 1.5, True))
def test_result_requires_positive_integer_canonical_byte_length(
    byte_length: object,
) -> None:
    valid = calculate_evidence_candidate_snapshot(_candidate())

    with pytest.raises(ValueError, match="canonical_byte_length"):
        replace(valid, canonical_byte_length=byte_length)
