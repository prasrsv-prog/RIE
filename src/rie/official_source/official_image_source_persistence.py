"""Canonical persistence codec for Gate 12 Official Image Source records.

This module implements a pure deterministic JSON byte codec only.
Filesystem storage, databases, registry integration, parser integration,
CLI behavior, schema migration, admission-audit persistence, real assets,
Gate 13 behavior, and semantic interpretation are intentionally excluded.
"""

from __future__ import annotations

from datetime import datetime as _datetime
from datetime import timezone as _timezone
from enum import Enum as _Enum
import json as _json
import re as _re
from typing import Final as _Final

from rie.official_source.official_image_source import (
    AdmissionStatus as _AdmissionStatus,
    AuthorityClass as _AuthorityClass,
    LifecycleState as _LifecycleState,
    OfficialImageSource as _OfficialImageSource,
    RightsStatus as _RightsStatus,
    SourceKind as _SourceKind,
)


__all__ = (
    "encode_official_image_source",
    "decode_official_image_source",
)


_FIELD_NAMES: _Final[tuple[str, ...]] = (
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

_TIMESTAMP_PATTERN: _Final[_re.Pattern[str]] = _re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T"
    r"(\d{2}):(\d{2}):(\d{2})\.(\d{6})Z$"
)

_UTF8_BOM: _Final[bytes] = b"\xef\xbb\xbf"


class _ObjectPairs(list[tuple[str, object]]):
    """Distinguish a JSON object from a JSON array after decoding."""


def encode_official_image_source(source: _OfficialImageSource) -> bytes:
    """Encode one OfficialImageSource as canonical UTF-8 JSON bytes."""

    if not isinstance(source, _OfficialImageSource):
        raise TypeError("source must be an OfficialImageSource")

    payload = {
        "source_id": source.source_id,
        "source_locator": source.source_locator,
        "source_kind": source.source_kind.value,
        "content_sha256": source.content_sha256,
        "byte_length": source.byte_length,
        "authority_class": source.authority_class.value,
        "rights_status": source.rights_status.value,
        "lifecycle_state": source.lifecycle_state.value,
        "admission_status": source.admission_status.value,
        "provenance_parent_id": source.provenance_parent_id,
        "registered_at_utc": _format_utc_timestamp(source.registered_at_utc),
        "registered_by": source.registered_by,
    }

    text = _json.dumps(
        payload,
        ensure_ascii=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    return text.encode("utf-8")


def decode_official_image_source(payload: bytes) -> _OfficialImageSource:
    """Decode canonical UTF-8 JSON bytes into an OfficialImageSource."""

    if not isinstance(payload, bytes):
        raise TypeError("payload must be bytes")
    if not payload:
        raise ValueError("payload must be non-empty")
    if payload.startswith(_UTF8_BOM):
        raise ValueError("payload must not contain a UTF-8 byte-order mark")

    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise ValueError("payload must contain valid UTF-8") from error

    try:
        decoded = _json.loads(
            text,
            object_pairs_hook=_capture_object_pairs,
            parse_constant=_reject_json_constant,
        )
    except _json.JSONDecodeError as error:
        raise ValueError("payload must contain valid JSON") from error

    if not isinstance(decoded, _ObjectPairs):
        raise ValueError("payload top-level value must be a JSON object")

    keys = tuple(key for key, _value in decoded)
    if keys != _FIELD_NAMES:
        raise ValueError(
            "payload keys must match the exact canonical twelve-field order"
        )

    values = dict(decoded)
    _require_json_string(values, "source_id")
    _require_json_string(values, "source_locator")
    _require_json_string(values, "source_kind")
    _require_json_string(values, "content_sha256")
    _require_json_integer(values, "byte_length")
    _require_json_string(values, "authority_class")
    _require_json_string(values, "rights_status")
    _require_json_string(values, "lifecycle_state")
    _require_json_string(values, "admission_status")
    _require_json_optional_string(values, "provenance_parent_id")
    _require_json_string(values, "registered_at_utc")
    _require_json_string(values, "registered_by")

    source = _OfficialImageSource(
        source_id=values["source_id"],
        source_locator=values["source_locator"],
        source_kind=_decode_enum(
            "source_kind",
            values["source_kind"],
            _SourceKind,
        ),
        content_sha256=values["content_sha256"],
        byte_length=values["byte_length"],
        authority_class=_decode_enum(
            "authority_class",
            values["authority_class"],
            _AuthorityClass,
        ),
        rights_status=_decode_enum(
            "rights_status",
            values["rights_status"],
            _RightsStatus,
        ),
        lifecycle_state=_decode_enum(
            "lifecycle_state",
            values["lifecycle_state"],
            _LifecycleState,
        ),
        admission_status=_decode_enum(
            "admission_status",
            values["admission_status"],
            _AdmissionStatus,
        ),
        provenance_parent_id=values["provenance_parent_id"],
        registered_at_utc=_parse_utc_timestamp(values["registered_at_utc"]),
        registered_by=values["registered_by"],
    )

    if encode_official_image_source(source) != payload:
        raise ValueError("payload must use the canonical byte representation")

    return source


def _capture_object_pairs(pairs: list[tuple[str, object]]) -> _ObjectPairs:
    seen: set[str] = set()

    for key, _value in pairs:
        if key in seen:
            raise ValueError("payload contains duplicate JSON object keys")
        seen.add(key)

    return _ObjectPairs(pairs)


def _reject_json_constant(value: str) -> object:
    raise ValueError(f"payload contains unsupported JSON constant {value}")


def _format_utc_timestamp(value: _datetime) -> str:
    return (
        f"{value.year:04d}-{value.month:02d}-{value.day:02d}T"
        f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}."
        f"{value.microsecond:06d}Z"
    )


def _parse_utc_timestamp(value: str) -> _datetime:
    match = _TIMESTAMP_PATTERN.fullmatch(value)

    if match is None:
        raise ValueError(
            "registered_at_utc must use YYYY-MM-DDTHH:MM:SS.ffffffZ"
        )

    try:
        return _datetime(
            year=int(match.group(1)),
            month=int(match.group(2)),
            day=int(match.group(3)),
            hour=int(match.group(4)),
            minute=int(match.group(5)),
            second=int(match.group(6)),
            microsecond=int(match.group(7)),
            tzinfo=_timezone.utc,
        )
    except ValueError as error:
        raise ValueError(
            "registered_at_utc must contain a valid canonical UTC timestamp"
        ) from error


def _require_json_string(values: dict[str, object], name: str) -> None:
    if type(values[name]) is not str:
        raise TypeError(f"{name} must be a JSON string")


def _require_json_integer(values: dict[str, object], name: str) -> None:
    if type(values[name]) is not int:
        raise TypeError(f"{name} must be a JSON integer")


def _require_json_optional_string(
    values: dict[str, object],
    name: str,
) -> None:
    if values[name] is not None and type(values[name]) is not str:
        raise TypeError(f"{name} must be JSON null or a JSON string")


def _decode_enum(
    name: str,
    value: str,
    enum_type: type[_Enum],
) -> _Enum:
    try:
        return enum_type(value)
    except ValueError as error:
        raise ValueError(f"{name} contains an unsupported controlled value") from error
