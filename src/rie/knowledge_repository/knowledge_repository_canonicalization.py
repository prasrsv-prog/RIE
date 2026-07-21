from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
import hashlib
import importlib
import json

from .knowledge_repository_contract import (
    KNOWLEDGE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION,
    KNOWLEDGE_REPOSITORY_AUDIT_ID_PREFIX,
    KNOWLEDGE_REPOSITORY_DIGEST_ALGORITHM,
    KNOWLEDGE_REPOSITORY_LINEAGE_IDENTITY_CANONICALIZATION_VERSION,
    KNOWLEDGE_REPOSITORY_LINEAGE_ID_PREFIX,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_IDENTITY_CANONICALIZATION_VERSION,
    KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_ID_PREFIX,
    KNOWLEDGE_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION,
    KNOWLEDGE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION,
    KNOWLEDGE_REPOSITORY_REVISION_ID_PREFIX,
)

_ALLOWED_MODULES = (
    "rie.domain.knowledge_candidate",
    "rie.domain.governed_knowledge",
    "rie.domain.governed_knowledge_lifecycle_assertion",
    "rie.domain.governed_knowledge_lifecycle_assertion_interpretation_premise",
    "rie.domain.governed_knowledge_lifecycle_assertion_interpretation_result",
    "rie.knowledge_repository.knowledge_repository_contract",
)


def _format_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _encode(value: object) -> object:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            "__dataclass__": (
                value.__class__.__module__
                + ":"
                + value.__class__.__qualname__
            ),
            "fields": {
                field.name: _encode(getattr(value, field.name))
                for field in dataclasses.fields(value)
            },
        }
    if isinstance(value, datetime):
        return {"__datetime__": _format_datetime(value)}
    if isinstance(value, tuple):
        return {"__tuple__": [_encode(item) for item in value]}
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _encode(item) for key, item in value.items()}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported payload type: {type(value)!r}")


def _class_registry() -> dict[str, type]:
    registry: dict[str, type] = {}
    for module_name in _ALLOWED_MODULES:
        module = importlib.import_module(module_name)
        for name in dir(module):
            candidate = getattr(module, name)
            if isinstance(candidate, type) and dataclasses.is_dataclass(candidate):
                registry[
                    module_name + ":" + candidate.__qualname__
                ] = candidate
    return registry


def _parse_datetime(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("canonical datetime must use UTC Z form")
    return datetime.fromisoformat(value[:-1] + "+00:00")


def _decode(value: object, registry: dict[str, type]) -> object:
    if isinstance(value, list):
        return [_decode(item, registry) for item in value]
    if not isinstance(value, dict):
        return value
    if set(value) == {"__datetime__"}:
        return _parse_datetime(value["__datetime__"])
    if set(value) == {"__tuple__"}:
        items = value["__tuple__"]
        if not isinstance(items, list):
            raise ValueError("invalid tuple payload")
        return tuple(_decode(item, registry) for item in items)
    if set(value) == {"__dataclass__", "fields"}:
        type_name = value["__dataclass__"]
        fields = value["fields"]
        if (
            not isinstance(type_name, str)
            or type_name not in registry
            or not isinstance(fields, dict)
        ):
            raise ValueError("unsupported dataclass payload")
        cls = registry[type_name]
        return cls(
            **{
                key: _decode(item, registry)
                for key, item in fields.items()
            }
        )
    return {
        key: _decode(item, registry)
        for key, item in value.items()
    }


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _digest(payload: bytes) -> str:
    if KNOWLEDGE_REPOSITORY_DIGEST_ALGORITHM != "sha256":
        raise RuntimeError("unsupported repository digest")
    return hashlib.sha256(payload).hexdigest()


def serialize_governed_knowledge_repository_payload(
    value: object,
) -> bytes:
    return _canonical_json_bytes(
        {
            "canonicalization_version": (
                KNOWLEDGE_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION
            ),
            "payload": _encode(value),
        }
    )


def deserialize_governed_knowledge_repository_payload(
    payload_bytes: bytes,
) -> object:
    if not isinstance(payload_bytes, bytes):
        raise TypeError("payload_bytes must be bytes")
    decoded = json.loads(payload_bytes.decode("utf-8"))
    if (
        not isinstance(decoded, dict)
        or decoded.get("canonicalization_version")
        != KNOWLEDGE_REPOSITORY_PAYLOAD_CANONICALIZATION_VERSION
        or set(decoded) != {"canonicalization_version", "payload"}
    ):
        raise ValueError("unsupported repository payload")
    value = _decode(decoded["payload"], _class_registry())
    if (
        serialize_governed_knowledge_repository_payload(value)
        != payload_bytes
    ):
        raise ValueError("repository payload is not canonical")
    return value


def calculate_governed_knowledge_repository_payload_digest(
    value: object,
) -> str:
    return _digest(
        serialize_governed_knowledge_repository_payload(value)
    )


def _identity(
    prefix: str,
    version: str,
    fields: dict[str, object],
) -> str:
    return prefix + _digest(
        _canonical_json_bytes(
            {
                "canonicalization_version": version,
                "identity": fields,
            }
        )
    )


def calculate_knowledge_repository_lineage_record_id(
    *,
    governed_knowledge_id: str,
    governed_knowledge_contract_version: str,
    knowledge_candidate_id: str,
    knowledge_candidate_contract_version: str,
    knowledge_candidate_snapshot_digest: str,
    persisted_evidence_knowledge_compatibility_record_id: str,
    evidence_repository_revision_id: str,
    evidence_repository_audit_id: str,
    source_id: str,
    source_revision_number: int,
    traceable_evidence_id: str,
    accepted_evidence_id: str,
    acceptance_record_ids: tuple[str, ...],
    construction_rule_id: str,
    construction_rule_version: str,
    governed_knowledge_construction_policy_id: str,
    governed_knowledge_construction_policy_version: str,
    lineage_policy_id: str,
    lineage_policy_version: str,
) -> str:
    fields = dict(locals())
    fields["acceptance_record_ids"] = sorted(
        set(acceptance_record_ids)
    )
    return _identity(
        KNOWLEDGE_REPOSITORY_LINEAGE_ID_PREFIX,
        KNOWLEDGE_REPOSITORY_LINEAGE_IDENTITY_CANONICALIZATION_VERSION,
        fields,
    )


def calculate_knowledge_repository_lifecycle_transition_record_id(
    *,
    governed_knowledge_id: str,
    from_revision_id: str,
    from_revision_number: int,
    previous_lifecycle_interpretation_result_id: str,
    next_lifecycle_interpretation_result_id: str,
    transition_reason_codes: tuple[str, ...],
    actor_id: str,
    recorded_at_utc: datetime,
    transition_policy_id: str,
    transition_policy_version: str,
) -> str:
    fields = dict(locals())
    fields["transition_reason_codes"] = sorted(
        set(transition_reason_codes)
    )
    fields["recorded_at_utc"] = _format_datetime(recorded_at_utc)
    return _identity(
        KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_ID_PREFIX,
        (
            KNOWLEDGE_REPOSITORY_LIFECYCLE_TRANSITION_IDENTITY_CANONICALIZATION_VERSION
        ),
        fields,
    )


def calculate_knowledge_repository_revision_id(
    *,
    governed_knowledge_id: str,
    revision_number: int,
    previous_revision_id: str | None,
    governed_knowledge_payload_digest: str,
    lineage_record_id: str,
    lifecycle_interpretation_result_id: str,
    lifecycle_interpretation_result_contract_version: str,
    lifecycle_interpretation_result_payload_digest: str,
    transition_record_id: str | None,
    actor_id: str,
    recorded_at_utc: datetime,
) -> str:
    fields = dict(locals())
    fields["recorded_at_utc"] = _format_datetime(recorded_at_utc)
    return _identity(
        KNOWLEDGE_REPOSITORY_REVISION_ID_PREFIX,
        KNOWLEDGE_REPOSITORY_REVISION_IDENTITY_CANONICALIZATION_VERSION,
        fields,
    )


def calculate_knowledge_repository_audit_id(
    *,
    action: str,
    revision_id: str,
    governed_knowledge_id: str,
    revision_number: int,
    lineage_record_id: str,
    transition_record_id: str | None,
    actor_id: str,
    recorded_at_utc: datetime,
) -> str:
    fields = dict(locals())
    fields["recorded_at_utc"] = _format_datetime(recorded_at_utc)
    return _identity(
        KNOWLEDGE_REPOSITORY_AUDIT_ID_PREFIX,
        KNOWLEDGE_REPOSITORY_AUDIT_IDENTITY_CANONICALIZATION_VERSION,
        fields,
    )
