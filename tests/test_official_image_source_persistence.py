from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
import json

import pytest

from rie.official_source.official_image_source import (
    AdmissionStatus,
    AuthorityClass,
    LifecycleState,
    OfficialImageSource,
    RightsStatus,
    SourceKind,
)
from rie.official_source.official_image_source_persistence import (
    decode_official_image_source,
    encode_official_image_source,
)
import rie.official_source.official_image_source_persistence as persistence


VALID_SHA256 = "a" * 64
VALID_TIME = datetime(
    2026,
    7,
    29,
    12,
    34,
    56,
    123456,
    tzinfo=timezone.utc,
)
FIELD_NAMES = (
    "source_id",
    "source_locator",
    "source_kind",
    "content_sha256",
    "byte_length",
    "authority_class",
    "rights_status",
    "lifecycle_state",
    "admission_status",
    "provenance_parent_id",
    "registered_at_utc",
    "registered_by",
)


def make_source(**overrides: object) -> OfficialImageSource:
    values: dict[str, object] = {
        "source_id": "image-source-001",
        "source_locator": "repository://assets/controlled/image-001.png",
        "source_kind": SourceKind.REPOSITORY_ASSET,
        "content_sha256": VALID_SHA256,
        "byte_length": 1234,
        "authority_class": AuthorityClass.OFFICIAL_INTERNAL,
        "rights_status": RightsStatus.OWNED,
        "lifecycle_state": LifecycleState.CANDIDATE,
        "admission_status": AdmissionStatus.PENDING,
        "provenance_parent_id": None,
        "registered_at_utc": VALID_TIME,
        "registered_by": "operator-001",
    }
    values.update(overrides)
    return OfficialImageSource(**values)  # type: ignore[arg-type]


def canonical_mapping(**overrides: object) -> dict[str, object]:
    mapping: dict[str, object] = {
        "source_id": "image-source-001",
        "source_locator": "repository://assets/controlled/image-001.png",
        "source_kind": "REPOSITORY_ASSET",
        "content_sha256": VALID_SHA256,
        "byte_length": 1234,
        "authority_class": "OFFICIAL_INTERNAL",
        "rights_status": "OWNED",
        "lifecycle_state": "CANDIDATE",
        "admission_status": "PENDING",
        "provenance_parent_id": None,
        "registered_at_utc": "2026-07-29T12:34:56.123456Z",
        "registered_by": "operator-001",
    }
    mapping.update(overrides)
    return mapping


def canonical_payload(**overrides: object) -> bytes:
    return json.dumps(
        canonical_mapping(**overrides),
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def test_public_api_tuple_is_exact() -> None:
    assert persistence.__all__ == (
        "encode_official_image_source",
        "decode_official_image_source",
    )


def test_encoder_returns_bytes() -> None:
    assert type(encode_official_image_source(make_source())) is bytes


def test_encoder_is_deterministic_for_equal_records() -> None:
    assert encode_official_image_source(make_source()) == (
        encode_official_image_source(make_source())
    )


def test_encoder_emits_exact_canonical_root_payload() -> None:
    expected = (
        b'{"source_id":"image-source-001",'
        b'"source_locator":"repository://assets/controlled/image-001.png",'
        b'"source_kind":"REPOSITORY_ASSET",'
        b'"content_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",'
        b'"byte_length":1234,'
        b'"authority_class":"OFFICIAL_INTERNAL",'
        b'"rights_status":"OWNED",'
        b'"lifecycle_state":"CANDIDATE",'
        b'"admission_status":"PENDING",'
        b'"provenance_parent_id":null,'
        b'"registered_at_utc":"2026-07-29T12:34:56.123456Z",'
        b'"registered_by":"operator-001"}'
    )

    assert encode_official_image_source(make_source()) == expected


def test_encoder_uses_exact_field_order() -> None:
    payload = encode_official_image_source(make_source())
    assert tuple(json.loads(payload).keys()) == FIELD_NAMES


def test_encoder_emits_controlled_enum_values() -> None:
    mapping = json.loads(encode_official_image_source(make_source()))
    assert mapping["source_kind"] == "REPOSITORY_ASSET"
    assert mapping["authority_class"] == "OFFICIAL_INTERNAL"
    assert mapping["rights_status"] == "OWNED"
    assert mapping["lifecycle_state"] == "CANDIDATE"
    assert mapping["admission_status"] == "PENDING"


def test_encoder_emits_json_null_for_absent_parent() -> None:
    mapping = json.loads(encode_official_image_source(make_source()))
    assert mapping["provenance_parent_id"] is None


def test_encoder_emits_parent_string_exactly() -> None:
    source = make_source(provenance_parent_id="image-source-parent")
    mapping = json.loads(encode_official_image_source(source))
    assert mapping["provenance_parent_id"] == "image-source-parent"


def test_encoder_emits_six_digit_utc_timestamp() -> None:
    mapping = json.loads(encode_official_image_source(make_source()))
    assert mapping["registered_at_utc"] == "2026-07-29T12:34:56.123456Z"


def test_encoder_zero_pads_microseconds() -> None:
    source = make_source(
        registered_at_utc=datetime(
            2026,
            1,
            2,
            3,
            4,
            5,
            7,
            tzinfo=timezone.utc,
        )
    )
    assert b'"registered_at_utc":"2026-01-02T03:04:05.000007Z"' in (
        encode_official_image_source(source)
    )


def test_encoder_uses_ascii_escaping() -> None:
    payload = encode_official_image_source(
        make_source(registered_by="op\N{LATIN SMALL LETTER E WITH ACUTE}rator")
    )
    assert b"\\u00e9" in payload
    assert "op\N{LATIN SMALL LETTER E WITH ACUTE}rator".encode("utf-8") not in payload


def test_encoder_uses_no_insignificant_whitespace() -> None:
    payload = encode_official_image_source(make_source())
    assert b": " not in payload
    assert b", " not in payload
    assert not payload.startswith(b" ")
    assert not payload.endswith(b" ")


def test_encoder_emits_no_bom_or_line_feed() -> None:
    payload = encode_official_image_source(make_source())
    assert not payload.startswith(b"\xef\xbb\xbf")
    assert b"\n" not in payload
    assert not payload.endswith(b"\n")


def test_encoder_does_not_mutate_source() -> None:
    source = make_source()
    before = source
    encode_official_image_source(source)
    assert source == before
    with pytest.raises(FrozenInstanceError):
        source.source_id = "changed"  # type: ignore[misc]


def test_encoder_rejects_none() -> None:
    with pytest.raises(TypeError, match="source must be an OfficialImageSource"):
        encode_official_image_source(None)  # type: ignore[arg-type]


def test_encoder_rejects_mapping() -> None:
    with pytest.raises(TypeError, match="source must be an OfficialImageSource"):
        encode_official_image_source(canonical_mapping())  # type: ignore[arg-type]


def test_decoder_returns_equal_record() -> None:
    source = make_source()
    assert decode_official_image_source(
        encode_official_image_source(source)
    ) == source


def test_record_to_bytes_to_record_round_trip() -> None:
    source = make_source(provenance_parent_id="parent-source")
    decoded = decode_official_image_source(
        encode_official_image_source(source)
    )
    assert decoded == source


def test_bytes_to_record_to_bytes_round_trip() -> None:
    payload = canonical_payload()
    decoded = decode_official_image_source(payload)
    assert encode_official_image_source(decoded) == payload


def test_round_trip_preserves_microseconds_exactly() -> None:
    source = make_source(
        registered_at_utc=datetime(
            2026,
            12,
            31,
            23,
            59,
            59,
            999999,
            tzinfo=timezone.utc,
        )
    )
    decoded = decode_official_image_source(
        encode_official_image_source(source)
    )
    assert decoded.registered_at_utc == source.registered_at_utc


def test_round_trip_preserves_all_enum_members_for_valid_record() -> None:
    source = make_source(
        source_kind=SourceKind.FILE,
        authority_class=AuthorityClass.OFFICIAL_PARTNER,
        rights_status=RightsStatus.LICENSED,
        lifecycle_state=LifecycleState.ACTIVE,
        admission_status=AdmissionStatus.ACCEPTED,
    )
    assert decode_official_image_source(
        encode_official_image_source(source)
    ) == source


def test_round_trip_preserves_superseded_parent() -> None:
    source = make_source(
        lifecycle_state=LifecycleState.SUPERSEDED,
        admission_status=AdmissionStatus.ACCEPTED,
        provenance_parent_id="image-source-parent",
    )
    assert decode_official_image_source(
        encode_official_image_source(source)
    ) == source


def test_decoder_does_not_mutate_payload_or_record() -> None:
    payload = canonical_payload()
    original = bytes(payload)
    source = decode_official_image_source(payload)
    assert payload == original
    with pytest.raises(FrozenInstanceError):
        source.registered_by = "changed"  # type: ignore[misc]


def test_decoder_rejects_bytearray() -> None:
    with pytest.raises(TypeError, match="payload must be bytes"):
        decode_official_image_source(bytearray(canonical_payload()))  # type: ignore[arg-type]


def test_decoder_rejects_memoryview() -> None:
    with pytest.raises(TypeError, match="payload must be bytes"):
        decode_official_image_source(memoryview(canonical_payload()))  # type: ignore[arg-type]


def test_decoder_rejects_string() -> None:
    with pytest.raises(TypeError, match="payload must be bytes"):
        decode_official_image_source("{}")  # type: ignore[arg-type]


def test_decoder_rejects_empty_bytes() -> None:
    with pytest.raises(ValueError, match="payload must be non-empty"):
        decode_official_image_source(b"")


def test_decoder_rejects_utf8_bom() -> None:
    with pytest.raises(ValueError, match="byte-order mark"):
        decode_official_image_source(b"\xef\xbb\xbf" + canonical_payload())


def test_decoder_rejects_invalid_utf8() -> None:
    with pytest.raises(ValueError, match="valid UTF-8"):
        decode_official_image_source(b"\xff")


def test_decoder_rejects_invalid_json() -> None:
    with pytest.raises(ValueError, match="valid JSON"):
        decode_official_image_source(b"{")


def test_decoder_rejects_top_level_array() -> None:
    with pytest.raises(ValueError, match="top-level value"):
        decode_official_image_source(b"[]")


def test_decoder_rejects_top_level_string() -> None:
    with pytest.raises(ValueError, match="top-level value"):
        decode_official_image_source(b'"record"')


def test_decoder_rejects_top_level_null() -> None:
    with pytest.raises(ValueError, match="top-level value"):
        decode_official_image_source(b"null")


def test_decoder_rejects_duplicate_keys() -> None:
    payload = canonical_payload().replace(
        b'{"source_id":"image-source-001",',
        b'{"source_id":"duplicate","source_id":"image-source-001",',
        1,
    )
    with pytest.raises(ValueError, match="duplicate JSON object keys"):
        decode_official_image_source(payload)


def test_decoder_rejects_missing_key() -> None:
    mapping = canonical_mapping()
    del mapping["registered_by"]
    payload = json.dumps(
        mapping,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    with pytest.raises(ValueError, match="exact canonical twelve-field order"):
        decode_official_image_source(payload)


def test_decoder_rejects_extra_key() -> None:
    mapping = canonical_mapping()
    mapping["extra"] = "not-authorized"
    payload = json.dumps(
        mapping,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    with pytest.raises(ValueError, match="exact canonical twelve-field order"):
        decode_official_image_source(payload)


def test_decoder_rejects_reordered_keys() -> None:
    mapping = canonical_mapping()
    reordered = {
        "source_locator": mapping["source_locator"],
        "source_id": mapping["source_id"],
        **{
            key: value
            for key, value in mapping.items()
            if key not in {"source_id", "source_locator"}
        },
    }
    payload = json.dumps(
        reordered,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    with pytest.raises(ValueError, match="exact canonical twelve-field order"):
        decode_official_image_source(payload)


def test_decoder_rejects_leading_whitespace() -> None:
    with pytest.raises(ValueError, match="canonical byte representation"):
        decode_official_image_source(b" " + canonical_payload())


def test_decoder_rejects_trailing_whitespace() -> None:
    with pytest.raises(ValueError, match="canonical byte representation"):
        decode_official_image_source(canonical_payload() + b" ")


def test_decoder_rejects_trailing_line_feed() -> None:
    with pytest.raises(ValueError, match="canonical byte representation"):
        decode_official_image_source(canonical_payload() + b"\n")


def test_decoder_rejects_pretty_printed_json() -> None:
    payload = json.dumps(
        canonical_mapping(),
        ensure_ascii=True,
        indent=2,
    ).encode("utf-8")
    with pytest.raises(ValueError, match="canonical byte representation"):
        decode_official_image_source(payload)


def test_decoder_rejects_non_ascii_literal_when_escape_is_canonical() -> None:
    canonical = encode_official_image_source(
        make_source(registered_by="op\N{LATIN SMALL LETTER E WITH ACUTE}rator")
    )
    payload = canonical.replace(
        b"\\u00e9",
        "\N{LATIN SMALL LETTER E WITH ACUTE}".encode("utf-8"),
    )
    with pytest.raises(ValueError, match="canonical byte representation"):
        decode_official_image_source(payload)


def test_decoder_rejects_uppercase_unicode_escape_hex() -> None:
    canonical = encode_official_image_source(
        make_source(registered_by="op\N{LATIN SMALL LETTER E WITH ACUTE}rator")
    )
    payload = canonical.replace(b"\\u00e9", b"\\u00E9")
    with pytest.raises(ValueError, match="canonical byte representation"):
        decode_official_image_source(payload)


def test_decoder_rejects_escaped_forward_slash() -> None:
    payload = canonical_payload().replace(
        b"repository://",
        b"repository:" + b"\\/" + b"\\/",
        1,
    )
    with pytest.raises(ValueError, match="canonical byte representation"):
        decode_official_image_source(payload)


def test_decoder_rejects_non_string_source_id() -> None:
    with pytest.raises(TypeError, match="source_id must be a JSON string"):
        decode_official_image_source(canonical_payload(source_id=123))


def test_decoder_rejects_non_string_source_locator() -> None:
    with pytest.raises(TypeError, match="source_locator must be a JSON string"):
        decode_official_image_source(canonical_payload(source_locator=[]))


def test_decoder_rejects_non_string_source_kind() -> None:
    with pytest.raises(TypeError, match="source_kind must be a JSON string"):
        decode_official_image_source(canonical_payload(source_kind=1))


def test_decoder_rejects_non_string_sha256() -> None:
    with pytest.raises(TypeError, match="content_sha256 must be a JSON string"):
        decode_official_image_source(canonical_payload(content_sha256=None))


def test_decoder_rejects_boolean_byte_length() -> None:
    with pytest.raises(TypeError, match="byte_length must be a JSON integer"):
        decode_official_image_source(canonical_payload(byte_length=True))


def test_decoder_rejects_float_byte_length() -> None:
    with pytest.raises(TypeError, match="byte_length must be a JSON integer"):
        decode_official_image_source(canonical_payload(byte_length=1234.0))


def test_decoder_rejects_non_string_authority_class() -> None:
    with pytest.raises(TypeError, match="authority_class must be a JSON string"):
        decode_official_image_source(canonical_payload(authority_class={}))


def test_decoder_rejects_non_string_rights_status() -> None:
    with pytest.raises(TypeError, match="rights_status must be a JSON string"):
        decode_official_image_source(canonical_payload(rights_status=False))


def test_decoder_rejects_non_string_lifecycle_state() -> None:
    with pytest.raises(TypeError, match="lifecycle_state must be a JSON string"):
        decode_official_image_source(canonical_payload(lifecycle_state=5))


def test_decoder_rejects_non_string_admission_status() -> None:
    with pytest.raises(TypeError, match="admission_status must be a JSON string"):
        decode_official_image_source(canonical_payload(admission_status=[]))


def test_decoder_rejects_non_string_parent() -> None:
    with pytest.raises(TypeError, match="provenance_parent_id must be JSON null"):
        decode_official_image_source(canonical_payload(provenance_parent_id=1))


def test_decoder_rejects_non_string_timestamp() -> None:
    with pytest.raises(TypeError, match="registered_at_utc must be a JSON string"):
        decode_official_image_source(canonical_payload(registered_at_utc=0))


def test_decoder_rejects_non_string_registered_by() -> None:
    with pytest.raises(TypeError, match="registered_by must be a JSON string"):
        decode_official_image_source(canonical_payload(registered_by=None))


def test_decoder_rejects_unknown_source_kind() -> None:
    with pytest.raises(ValueError, match="source_kind contains an unsupported"):
        decode_official_image_source(canonical_payload(source_kind="UNKNOWN"))


def test_decoder_rejects_unknown_authority_class() -> None:
    with pytest.raises(ValueError, match="authority_class contains an unsupported"):
        decode_official_image_source(
            canonical_payload(authority_class="UNKNOWN")
        )


def test_decoder_rejects_unknown_rights_status() -> None:
    with pytest.raises(ValueError, match="rights_status contains an unsupported"):
        decode_official_image_source(canonical_payload(rights_status="UNKNOWN"))


def test_decoder_rejects_unknown_lifecycle_state() -> None:
    with pytest.raises(ValueError, match="lifecycle_state contains an unsupported"):
        decode_official_image_source(
            canonical_payload(lifecycle_state="UNKNOWN")
        )


def test_decoder_rejects_unknown_admission_status() -> None:
    with pytest.raises(ValueError, match="admission_status contains an unsupported"):
        decode_official_image_source(
            canonical_payload(admission_status="UNKNOWN")
        )


def test_decoder_rejects_timestamp_without_fraction() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DDTHH:MM:SS"):
        decode_official_image_source(
            canonical_payload(
                registered_at_utc="2026-07-29T12:34:56Z"
            )
        )


def test_decoder_rejects_timestamp_with_five_fraction_digits() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DDTHH:MM:SS"):
        decode_official_image_source(
            canonical_payload(
                registered_at_utc="2026-07-29T12:34:56.12345Z"
            )
        )


def test_decoder_rejects_timestamp_with_offset() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DDTHH:MM:SS"):
        decode_official_image_source(
            canonical_payload(
                registered_at_utc="2026-07-29T12:34:56.123456+00:00"
            )
        )


def test_decoder_rejects_invalid_calendar_timestamp() -> None:
    with pytest.raises(ValueError, match="valid canonical UTC timestamp"):
        decode_official_image_source(
            canonical_payload(
                registered_at_utc="2026-02-30T12:34:56.123456Z"
            )
        )


def test_decoder_rejects_nan_constant() -> None:
    payload = canonical_payload().replace(b'"byte_length":1234', b'"byte_length":NaN')
    with pytest.raises(ValueError, match="unsupported JSON constant NaN"):
        decode_official_image_source(payload)


def test_decoder_rejects_infinity_constant() -> None:
    payload = canonical_payload().replace(
        b'"byte_length":1234',
        b'"byte_length":Infinity',
    )
    with pytest.raises(ValueError, match="unsupported JSON constant Infinity"):
        decode_official_image_source(payload)


def test_decoder_reapplies_source_id_model_validation() -> None:
    with pytest.raises(ValueError, match="source_id must be non-empty"):
        decode_official_image_source(canonical_payload(source_id=""))


def test_decoder_reapplies_locator_model_validation() -> None:
    with pytest.raises(ValueError, match="surrounding whitespace"):
        decode_official_image_source(
            canonical_payload(source_locator=" locator")
        )


def test_decoder_reapplies_sha256_model_validation() -> None:
    with pytest.raises(ValueError, match="exactly 64 lowercase"):
        decode_official_image_source(canonical_payload(content_sha256="A" * 64))


def test_decoder_reapplies_positive_byte_length_validation() -> None:
    with pytest.raises(ValueError, match="byte_length must be positive"):
        decode_official_image_source(canonical_payload(byte_length=0))


def test_decoder_reapplies_parent_difference_validation() -> None:
    with pytest.raises(ValueError, match="must differ from source_id"):
        decode_official_image_source(
            canonical_payload(provenance_parent_id="image-source-001")
        )


def test_decoder_reapplies_active_admission_validation() -> None:
    with pytest.raises(ValueError, match="ACTIVE requires admission_status ACCEPTED"):
        decode_official_image_source(
            canonical_payload(
                lifecycle_state="ACTIVE",
                admission_status="PENDING",
            )
        )


def test_decoder_reapplies_superseded_parent_validation() -> None:
    with pytest.raises(ValueError, match="SUPERSEDED requires provenance_parent_id"):
        decode_official_image_source(
            canonical_payload(
                lifecycle_state="SUPERSEDED",
                admission_status="ACCEPTED",
                provenance_parent_id=None,
            )
        )


def test_equal_records_encode_to_equal_bytes() -> None:
    first = make_source()
    second = make_source()
    assert first == second
    assert encode_official_image_source(first) == (
        encode_official_image_source(second)
    )


def test_different_records_encode_to_different_bytes() -> None:
    first = make_source()
    second = make_source(registered_by="operator-002")
    assert encode_official_image_source(first) != (
        encode_official_image_source(second)
    )


def test_canonical_payload_is_stable_after_two_round_trips() -> None:
    payload = canonical_payload()
    first = encode_official_image_source(
        decode_official_image_source(payload)
    )
    second = encode_official_image_source(
        decode_official_image_source(first)
    )
    assert first == payload
    assert second == payload
