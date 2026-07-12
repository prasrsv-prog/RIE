import builtins
import hashlib
import inspect
from dataclasses import FrozenInstanceError, fields

import pytest

import rie.application.evidence_candidate as evidence_candidate_module
from rie.application.evidence_candidate import EvidenceCandidate


RAW_PAYLOAD = (
    '{"encrypted":false,"page_count":1,"pages":'
    '[{"height":792.0,"page_index":0,"rotation":0,"width":612.0}]}'
)


def _candidate(**overrides: object) -> EvidenceCandidate:
    values = {
        "source_id": "SRC-SYN-001",
        "source_type": "pdf",
        "source_checksum_algorithm": "sha256",
        "source_checksum": "a0b1c2d3",
        "source_authority": "official",
        "source_lifecycle_state": "active",
        "source_reference": "controlled://source/SRC-SYN-001",
        "execution_id": "EXEC-SYN-001",
        "producer_name": "controlled_pdf_structural_metadata",
        "producer_version": "1.0.0",
        "result_contract_version": "1.0.0",
        "execution_timestamp": "2026-07-12T12:34:56Z",
        "payload_type": "document_structural_metadata",
        "raw_payload": RAW_PAYLOAD,
        "locator": (("scope", "document"),),
        "warnings": (),
        "errors": (),
        "candidate_contract_version": "candidate-contract-test-v1",
    }
    values.update(overrides)
    return EvidenceCandidate(**values)  # type: ignore[arg-type]


def test_valid_construction_with_all_18_required_fields() -> None:
    candidate = _candidate()

    assert len(fields(candidate)) == 18


def test_exact_field_values_are_preserved() -> None:
    candidate = _candidate()

    assert tuple(getattr(candidate, field.name) for field in fields(candidate)) == (
        "SRC-SYN-001",
        "pdf",
        "sha256",
        "a0b1c2d3",
        "official",
        "active",
        "controlled://source/SRC-SYN-001",
        "EXEC-SYN-001",
        "controlled_pdf_structural_metadata",
        "1.0.0",
        "1.0.0",
        "2026-07-12T12:34:56Z",
        "document_structural_metadata",
        RAW_PAYLOAD,
        (("scope", "document"),),
        (),
        (),
        "candidate-contract-test-v1",
    )


def test_frozen_assignment_is_rejected() -> None:
    candidate = _candidate()

    with pytest.raises(FrozenInstanceError):
        candidate.source_id = "changed"  # type: ignore[misc]


def test_equality_for_identical_values() -> None:
    assert _candidate() == _candidate()


def test_inequality_when_one_field_changes() -> None:
    assert _candidate() != _candidate(execution_id="EXEC-SYN-002")


def test_mutable_warnings_list_is_rejected() -> None:
    with pytest.raises(ValueError, match="warnings"):
        _candidate(warnings=["warning"])


def test_mutable_errors_list_is_rejected() -> None:
    with pytest.raises(ValueError, match="errors"):
        _candidate(errors=["error"])


def test_mutable_locator_list_is_rejected() -> None:
    with pytest.raises(ValueError, match="locator"):
        _candidate(locator=[("scope", "document")])


def test_invalid_locator_entry_shape_is_rejected() -> None:
    invalid_locators = ((), (("scope",),), (("scope", "document", 1),))

    for locator in invalid_locators:
        with pytest.raises(ValueError, match="locator"):
            _candidate(locator=locator)


def test_duplicate_locator_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        _candidate(
            locator=(("scope", "document"), ("scope", "document")),
        )


def test_unordered_locator_keys_are_rejected() -> None:
    with pytest.raises(ValueError, match="ordered"):
        _candidate(locator=(("scope", "page"), ("page_index", 0)))


def test_non_string_locator_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="locator"):
        _candidate(locator=((1, "document"),))


def test_boolean_locator_value_is_rejected() -> None:
    with pytest.raises(ValueError, match="page_index"):
        _candidate(locator=(("page_index", True), ("scope", "page")))


def test_non_finite_locator_float_is_rejected() -> None:
    locator = (
        ("height", 1.0),
        ("scope", "region"),
        ("width", 1.0),
        ("x", float("inf")),
        ("y", 0.0),
    )

    with pytest.raises(ValueError, match="locator"):
        _candidate(locator=locator)


def test_empty_required_strings_are_rejected() -> None:
    string_fields = (
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
        "candidate_contract_version",
    )

    for field_name in string_fields:
        with pytest.raises(ValueError, match=field_name):
            _candidate(**{field_name: ""})


def test_whitespace_only_required_strings_are_rejected() -> None:
    string_fields = (
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
        "candidate_contract_version",
    )

    for field_name in string_fields:
        with pytest.raises(ValueError, match=field_name):
            _candidate(**{field_name: "   "})


def test_leading_or_trailing_whitespace_is_rejected() -> None:
    for value in (" source", "source "):
        with pytest.raises(ValueError, match="source_id"):
            _candidate(source_id=value)


def test_control_or_newline_characters_are_rejected() -> None:
    for value in ("source\x00id", "source\nid", "source\rid"):
        with pytest.raises(ValueError, match="source_id"):
            _candidate(source_id=value)


def test_invalid_execution_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="execution_timestamp"):
        _candidate(execution_timestamp="2026-02-30T12:34:56Z")


def test_timezone_naive_timestamp_is_rejected() -> None:
    with pytest.raises(ValueError, match="execution_timestamp"):
        _candidate(execution_timestamp="2026-07-12T12:34:56")


def test_valid_uppercase_z_timestamp_is_accepted() -> None:
    candidate = _candidate(execution_timestamp="2026-07-12T12:34:56Z")

    assert candidate.execution_timestamp == "2026-07-12T12:34:56Z"


def test_valid_offset_timestamp_is_accepted() -> None:
    timestamp = "2026-07-12T19:34:56+07:00"

    assert _candidate(execution_timestamp=timestamp).execution_timestamp == timestamp


def test_invalid_json_is_rejected() -> None:
    with pytest.raises(ValueError, match="raw_payload"):
        _candidate(raw_payload="{")


def test_duplicate_json_keys_are_rejected() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        _candidate(raw_payload='{"page_count":1,"page_count":2}')


def test_nan_json_is_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        _candidate(raw_payload="NaN")


def test_infinity_json_is_rejected() -> None:
    for raw_payload in ("Infinity", "-Infinity"):
        with pytest.raises(ValueError, match="finite"):
            _candidate(raw_payload=raw_payload)


def test_overflow_produced_non_finite_json_number_is_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        _candidate(raw_payload="1e999")


def test_non_canonical_json_is_rejected() -> None:
    for raw_payload in ('{"b":1,"a":2}', '{"a": 1}'):
        with pytest.raises(ValueError, match="canonical"):
            _candidate(raw_payload=raw_payload)


def test_canonical_json_is_accepted() -> None:
    assert _candidate(raw_payload='{"a":1,"b":2}').raw_payload == '{"a":1,"b":2}'


def test_raw_payload_is_preserved_exactly() -> None:
    candidate = _candidate(raw_payload='"ข้อมูล"')

    assert candidate.raw_payload == '"ข้อมูล"'


def test_invalid_checksum_characters_are_rejected() -> None:
    with pytest.raises(ValueError, match="source_checksum"):
        _candidate(source_checksum="A0-B1")


def test_odd_length_checksum_is_rejected() -> None:
    with pytest.raises(ValueError, match="source_checksum"):
        _candidate(source_checksum="abc")


def test_lowercase_hexadecimal_checksum_is_accepted() -> None:
    assert _candidate(source_checksum="abcdef01").source_checksum == "abcdef01"


def test_source_reference_causes_no_filesystem_access(monkeypatch) -> None:
    def fail_open(*args: object, **kwargs: object) -> None:
        raise AssertionError("filesystem access is prohibited")

    monkeypatch.setattr(builtins, "open", fail_open)

    candidate = _candidate(source_reference="missing://synthetic/source")

    assert candidate.source_reference == "missing://synthetic/source"


def test_dto_does_not_calculate_checksum(monkeypatch) -> None:
    def fail_checksum(*args: object, **kwargs: object) -> None:
        raise AssertionError("checksum calculation is prohibited")

    monkeypatch.setattr(hashlib, "sha256", fail_checksum)

    assert _candidate().source_checksum == "a0b1c2d3"


def test_no_default_current_timestamp_exists() -> None:
    parameter = inspect.signature(EvidenceCandidate).parameters[
        "execution_timestamp"
    ]

    assert parameter.default is inspect.Parameter.empty


def test_candidate_contains_no_eligibility_fields() -> None:
    names = {field.name for field in fields(EvidenceCandidate)}

    assert not names.intersection(
        {"eligibility", "eligible", "accepted", "rejected", "review_status"}
    )


def test_candidate_contains_no_evidence_id() -> None:
    names = {field.name for field in fields(EvidenceCandidate)}

    assert "evidence_id" not in names
    assert "candidate_id" not in names


def test_candidate_contains_no_knowledge_fields() -> None:
    names = {field.name for field in fields(EvidenceCandidate)}

    assert not names.intersection(
        {"knowledge_id", "semantic_summary", "normalized_meaning"}
    )


def test_candidate_creates_no_evidence_or_collection_insertion() -> None:
    candidate = _candidate()

    assert type(candidate) is EvidenceCandidate
    assert not hasattr(candidate, "to_evidence")
    assert not hasattr(candidate, "insert")
    assert not hasattr(candidate, "collect")


def test_candidate_performs_no_persistence_parser_ingestion_or_network_call() -> None:
    prohibited_names = {
        "EvidenceCollection",
        "PdfReader",
        "requests",
        "socket",
        "subprocess",
        "urlopen",
    }

    assert not prohibited_names.intersection(evidence_candidate_module.__dict__)
    assert not hasattr(_candidate(), "save")
    assert not hasattr(_candidate(), "parse")
    assert not hasattr(_candidate(), "ingest")


def test_diagnostic_order_and_duplicates_are_preserved() -> None:
    diagnostics = ("warning-b", "warning-a", "warning-b")
    candidate = _candidate(warnings=diagnostics, errors=diagnostics)

    assert candidate.warnings == diagnostics
    assert candidate.errors == diagnostics


def test_empty_diagnostic_tuples_are_accepted() -> None:
    candidate = _candidate(warnings=(), errors=())

    assert candidate.warnings == ()
    assert candidate.errors == ()


def test_empty_or_whitespace_diagnostic_entries_are_rejected() -> None:
    for field_name in ("warnings", "errors"):
        for value in ("", " ", "line\nbreak"):
            with pytest.raises(ValueError, match=field_name):
                _candidate(**{field_name: (value,)})


def test_construction_is_deterministic_and_direct_import_works() -> None:
    first = _candidate()
    second = _candidate()

    assert first == second
    assert hash(first) == hash(second)
    assert EvidenceCandidate.__module__ == "rie.application.evidence_candidate"
