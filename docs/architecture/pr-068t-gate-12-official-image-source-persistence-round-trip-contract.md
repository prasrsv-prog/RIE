# PR-068T Gate 12 Official Image Source Persistence Round-Trip Contract Detail

Status: CANONICAL_SUBORDINATE_GATE_12_PERSISTENCE_ROUND_TRIP_CONTRACT_DETAIL_MATERIALIZED_PENDING_INDEPENDENT_REVIEW
Contract detail name: GATE_12_OFFICIAL_IMAGE_SOURCE_PERSISTENCE_ROUND_TRIP_CONTRACT_V1
Parent contract: GATE_12_OFFICIAL_IMAGE_SOURCE_DOMAIN_CONTRACT_V1
Parent Definition of Done criterion: persistence_round_trip_is_proven

## 1. Purpose

Define the minimum deterministic canonical byte representation and pure encode/decode boundary required to prove an OfficialImageSource persistence round trip without introducing a storage backend or changing the canonical twelve-field record.

## 2. Scope and Persistence Definition

For Gate 12 Contract V1, persistence round trip means:

OfficialImageSource record -> canonical persistence bytes -> OfficialImageSource record.

The persistence boundary is a pure codec boundary. It proves that every canonical record field can be encoded, retained in a stable byte representation, decoded, and reconstructed without information loss or record mutation.

Filesystem I/O, database I/O, registry integration, network storage, schema migration, and admission-audit persistence are outside this contract detail.

The future implementation is reserved for:

- src/rie/official_source/official_image_source_persistence.py
- tests/test_official_image_source_persistence.py

The future public codec operations are:

- encode_official_image_source(source: OfficialImageSource) -> bytes
- decode_official_image_source(payload: bytes) -> OfficialImageSource

## 3. Exact Twelve-Field Persisted Mapping

The canonical payload contains exactly these twelve keys in this exact order:

1. source_id: JSON string
2. source_locator: JSON string
3. source_kind: JSON string containing the SourceKind value
4. content_sha256: JSON string
5. byte_length: JSON integer
6. authority_class: JSON string containing the AuthorityClass value
7. rights_status: JSON string containing the RightsStatus value
8. lifecycle_state: JSON string containing the LifecycleState value
9. admission_status: JSON string containing the AdmissionStatus value
10. provenance_parent_id: JSON null or JSON string
11. registered_at_utc: JSON string in canonical UTC timestamp form
12. registered_by: JSON string

No key may be omitted, duplicated, renamed, reordered, or added.

## 4. Canonical Byte Representation

The representation enforces exactly these nine canonical rules:

1. payload_type_is_bytes
2. payload_is_utf8_without_bom
3. payload_is_one_json_object
4. keys_follow_exact_twelve_field_order
5. json_uses_no_insignificant_whitespace
6. json_strings_use_deterministic_ascii_escaping
7. json_separators_are_comma_and_colon_only
8. payload_has_no_trailing_line_feed
9. canonical_reencoding_must_equal_original_bytes

The encoder must use the semantic equivalent of:

- ensure_ascii=True
- allow_nan=False
- separators=(',', ':')
- insertion order equal to the twelve-field mapping
- UTF-8 encoding without a byte-order mark

The canonical timestamp form is exactly YYYY-MM-DDTHH:MM:SS.ffffffZ.

The timestamp form always contains six fractional-second digits and the literal Z suffix. It represents a datetime whose tzinfo is datetime.timezone.utc.

## 5. Deterministic Encoder Validation

The encoder enforces exactly these six rules:

1. source_must_be_official_image_source
2. exact_twelve_field_mapping_is_used
3. enum_members_encode_as_controlled_string_values
4. provenance_parent_none_encodes_as_json_null
5. registered_at_utc_encodes_in_canonical_timestamp_form
6. encoding_does_not_mutate_source_record

The same valid record must always produce exactly the same byte sequence.

## 6. Deterministic Decoder Validation

The decoder enforces exactly these twelve rules:

1. payload_must_be_bytes
2. payload_must_be_nonempty
3. utf8_decode_must_be_strict
4. byte_order_mark_is_rejected
5. top_level_value_must_be_json_object
6. duplicate_keys_are_rejected
7. missing_extra_or_reordered_keys_are_rejected
8. field_json_types_must_match_the_mapping
9. controlled_enum_values_must_be_valid
10. registered_at_utc_must_match_canonical_timestamp_form
11. official_image_source_construction_validation_must_pass
12. canonical_reencoding_must_match_input_bytes

JSON booleans are not valid integers for byte_length.

The decoder must construct the existing OfficialImageSource type so that all canonical construction validation, authority, rights, checksum, byte-length, provenance, lifecycle, admission-status, and UTC requirements remain authoritative.

## 7. Persistence Round-Trip Invariants

This contract detail enforces exactly these ten invariants:

1. persisted_key_set_and_order_match_the_twelve_field_record
2. controlled_enum_values_round_trip_exactly
3. byte_length_round_trips_as_a_non_boolean_integer
4. provenance_parent_null_or_string_round_trips_exactly
5. registered_at_utc_round_trips_with_exact_microsecond_value
6. equal_records_encode_to_equal_bytes
7. decode_of_encode_returns_an_equal_record
8. encode_of_decode_returns_identical_canonical_bytes
9. malformed_or_noncanonical_payloads_are_rejected
10. encoding_and_decoding_do_not_mutate_existing_records

Record equality for this contract is the frozen dataclass value equality of OfficialImageSource.

## 8. Persistence Round-Trip Definition of Done

The persistence_round_trip_is_proven criterion is proven only when all nine subordinate criteria are independently accepted:

1. persistence_round_trip_contract_detail_is_materialized_and_accepted
2. canonical_twelve_field_encoder_is_implemented
3. canonical_twelve_field_decoder_is_implemented
4. exact_mapping_and_canonical_byte_representation_are_enforced
5. duplicate_missing_extra_reordered_and_noncanonical_payloads_are_rejected
6. enum_timestamp_integer_and_provenance_decode_validation_is_enforced
7. record_to_bytes_to_record_round_trip_is_proven
8. canonical_bytes_to_record_to_bytes_round_trip_is_proven
9. targeted_tests_and_operator_evidence_are_accepted

## 9. Explicit Exclusions

The following twelve capability classes are excluded from this contract detail:

- filesystem_or_database_storage
- registry_integration
- parser_integration
- cli_integration
- network_storage
- schema_version_migration
- encryption_or_compression
- admission_decision_audit_persistence
- real_asset_execution
- gate_13_work
- modification_of_the_twelve_field_official_image_source_record
- image_semantic_interpretation

## 10. PR-068T Materialization Boundary

PR-068T is authorized only to:

- preserve the canonical Gate 12 contract unchanged;
- preserve the admission-decision audit contract unchanged;
- preserve all existing source and test modules unchanged;
- materialize this subordinate persistence round-trip contract-detail document at the selected path;
- verify that the reserved persistence source and test targets remain absent;
- emit external review evidence.

PR-068T does not authorize persistence implementation, source or test creation, mutation of OfficialImageSource, registry integration, parser integration, CLI integration, Python, pytest, the full suite, stage, commit, push, Gate 13, tag, or release.
