"""Framework-neutral read/local models for the RCIS product-completion shell."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


FactScope = Literal["product", "variant"]
ConstraintSeverity = Literal["preserve", "caution"]
UnknownReason = Literal["absent", "unresolved", "conflicting"]


def _required_text(value: str, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    return normalized


@dataclass(frozen=True)
class ProductFact:
    fact_id: str
    category: str
    label: str
    value: str
    scope: FactScope
    authority_state: str = "grounded"
    provenance_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("fact_id", "category", "label", "value", "authority_state"):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name),
            )
        if self.scope not in ("product", "variant"):
            raise ValueError("scope must be product or variant")


@dataclass(frozen=True)
class ProductConstraint:
    constraint_id: str
    label: str
    rule_text: str
    scope: FactScope
    severity: ConstraintSeverity = "preserve"
    source_fact_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("constraint_id", "label", "rule_text"):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name),
            )
        if self.scope not in ("product", "variant"):
            raise ValueError("scope must be product or variant")
        if self.severity not in ("preserve", "caution"):
            raise ValueError("severity must be preserve or caution")


@dataclass(frozen=True)
class ProductUnknown:
    topic: str
    user_facing_label: str
    reason: UnknownReason = "absent"

    def __post_init__(self) -> None:
        object.__setattr__(self, "topic", _required_text(self.topic, "topic"))
        object.__setattr__(
            self,
            "user_facing_label",
            _required_text(self.user_facing_label, "user_facing_label"),
        )
        if self.reason not in ("absent", "unresolved", "conflicting"):
            raise ValueError("unsupported unknown reason")


@dataclass(frozen=True)
class ProductContextSnapshot:
    product_id: str
    variant_id: str
    product_label: str
    variant_label: str
    summary: str = ""
    fact_groups: tuple[ProductFact, ...] = ()
    preservation_constraints: tuple[ProductConstraint, ...] = ()
    authorized_reference_asset_ids: tuple[str, ...] = ()
    unknown_topics: tuple[ProductUnknown, ...] = ()
    conflicts: tuple[str, ...] = ()
    provenance_summary: str = ""

    def __post_init__(self) -> None:
        for field_name in (
            "product_id",
            "variant_id",
            "product_label",
            "variant_label",
        ):
            object.__setattr__(
                self,
                field_name,
                _required_text(getattr(self, field_name), field_name),
            )

    @property
    def display_name(self) -> str:
        return f"{self.product_label} / {self.variant_label}"


@dataclass(frozen=True)
class CreativeBrief:
    objective: str = ""
    deliverable: str = ""
    environment: str = ""
    camera_angle: str = ""
    shot_type: str = ""
    lighting_style: str = ""
    composition: str = ""
    mood_style: str = ""
    aspect_ratio: str = ""
    orientation: str = ""
    product_emphasis: str = ""
    preserve_constraints: tuple[str, ...] = field(default_factory=tuple)
    avoid_constraints: tuple[str, ...] = field(default_factory=tuple)
    selected_reference_asset_ids: tuple[str, ...] = field(default_factory=tuple)
    freeform_notes: str = ""

    def legacy_submit_fields(self) -> dict[str, str]:
        """Project the richer brief onto the existing grounded-prompt contract."""
        return {
            "background": self.environment.strip(),
            "camera_angle": self.camera_angle.strip(),
            "requested_output": self.deliverable.strip(),
        }