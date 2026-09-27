"""Provider-neutral governed Creative Instruction Package application boundary.

This module deterministically combines a published Creative Product Profile,
Creative Asset Role Profile, and existing CreativePromptBrief into one immutable
PROMPT_CANDIDATE package. It does not render a provider-specific prompt, execute
a provider/model, persist state, approve instructions, or mutate upstream values.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Iterable, Sequence

from rie.application.creative_asset_role_profile import (
    ALLOWED_REFERENCE_STRENGTHS,
    ALLOWED_ROLE_KINDS,
    ALLOWED_VIEW_KINDS,
    CreativeAssetRoleDirective,
    CreativeAssetRoleProfile,
)
from rie.application.creative_product_profile import (
    CreativeProductProfile,
    CreativeProductRule,
    RULE_KINDS,
)
from rie.application.creative_prompt_composer import CreativePromptBrief


class CreativeInstructionPackageContractError(ValueError):
    """Fail-closed contract error for governed instruction-package construction."""


INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE: Final[str] = "PROMPT_CANDIDATE"
READINESS_READY: Final[str] = "READY"
READINESS_BLOCKED: Final[str] = "BLOCKED"
READINESS_VALUES: Final[tuple[str, ...]] = (
    READINESS_READY,
    READINESS_BLOCKED,
)


def _required_ascii_text(name: str, value: object) -> str:
    if not isinstance(value, str):
        raise CreativeInstructionPackageContractError(f"{name} must be text")
    if not value or value != value.strip():
        raise CreativeInstructionPackageContractError(
            f"{name} must be non-empty text without surrounding whitespace"
        )
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise CreativeInstructionPackageContractError(
            f"{name} must be ASCII text"
        ) from exc
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise CreativeInstructionPackageContractError(
            f"{name} must not contain control characters"
        )
    return value


def _text_tuple(name: str, values: Sequence[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise CreativeInstructionPackageContractError(
            f"{name} must be a sequence of text values"
        )
    output = tuple(
        _required_ascii_text(f"{name}[{index}]", value)
        for index, value in enumerate(values)
    )
    if len(output) != len(set(output)):
        raise CreativeInstructionPackageContractError(
            f"{name} must not contain duplicates"
        )
    return output


def _canonical_text_tuple(name: str, values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted(_text_tuple(name, values)))


def _ordered_unique(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return tuple(output)


def _canonical_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _product_unknown_topic(value: object, index: int) -> str:
    topic = getattr(value, "topic", None)
    return _required_ascii_text(f"product_profile.unknown_topics[{index}].topic", topic)


@dataclass(frozen=True, slots=True)
class CreativeInstructionProductDirective:
    rule_id: str
    rule_kind: str
    subject: str
    instruction_value: str
    support_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        _required_ascii_text("rule_id", self.rule_id)
        if self.rule_kind not in RULE_KINDS:
            raise CreativeInstructionPackageContractError(
                f"unsupported rule_kind: {self.rule_kind}"
            )
        _required_ascii_text("subject", self.subject)
        _required_ascii_text("instruction_value", self.instruction_value)
        object.__setattr__(
            self,
            "support_refs",
            _canonical_text_tuple("support_refs", self.support_refs),
        )
        object.__setattr__(
            self,
            "provenance_refs",
            _canonical_text_tuple("provenance_refs", self.provenance_refs),
        )
        if not self.support_refs:
            raise CreativeInstructionPackageContractError(
                "product directive requires explicit support"
            )


@dataclass(frozen=True, slots=True)
class CreativeInstructionAssetDirective:
    directive_id: str
    asset_id: str
    asset_version_identity: str
    role_kind: str
    view_kind: str
    reference_strength: str
    support_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in ("directive_id", "asset_id", "asset_version_identity"):
            _required_ascii_text(field_name, getattr(self, field_name))
        if self.role_kind not in ALLOWED_ROLE_KINDS:
            raise CreativeInstructionPackageContractError(
                f"unsupported role_kind: {self.role_kind}"
            )
        if self.view_kind not in ALLOWED_VIEW_KINDS:
            raise CreativeInstructionPackageContractError(
                f"unsupported view_kind: {self.view_kind}"
            )
        if self.reference_strength not in ALLOWED_REFERENCE_STRENGTHS:
            raise CreativeInstructionPackageContractError(
                f"unsupported reference_strength: {self.reference_strength}"
            )
        object.__setattr__(
            self,
            "support_refs",
            _canonical_text_tuple("support_refs", self.support_refs),
        )
        object.__setattr__(
            self,
            "provenance_refs",
            _canonical_text_tuple("provenance_refs", self.provenance_refs),
        )
        if not self.support_refs:
            raise CreativeInstructionPackageContractError(
                "asset directive requires explicit support"
            )


@dataclass(frozen=True, slots=True)
class CreativeInstructionPackage:
    package_id: str
    package_version: str
    product_id: str
    variant_id: str
    instruction_authority: str
    readiness: str
    product_directives: tuple[CreativeInstructionProductDirective, ...]
    active_asset_directives: tuple[CreativeInstructionAssetDirective, ...]
    creative_brief: CreativePromptBrief
    unknown_topics: tuple[str, ...]
    conflicts: tuple[str, ...]
    provenance_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "package_id",
            "package_version",
            "product_id",
            "variant_id",
        ):
            _required_ascii_text(field_name, getattr(self, field_name))
        if self.instruction_authority != INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE:
            raise CreativeInstructionPackageContractError(
                "instruction_authority must be PROMPT_CANDIDATE"
            )
        if self.readiness not in READINESS_VALUES:
            raise CreativeInstructionPackageContractError(
                f"unsupported readiness: {self.readiness}"
            )
        if not isinstance(self.product_directives, tuple) or any(
            not isinstance(value, CreativeInstructionProductDirective)
            for value in self.product_directives
        ):
            raise CreativeInstructionPackageContractError(
                "product_directives must contain CreativeInstructionProductDirective values"
            )
        if not isinstance(self.active_asset_directives, tuple) or any(
            not isinstance(value, CreativeInstructionAssetDirective)
            for value in self.active_asset_directives
        ):
            raise CreativeInstructionPackageContractError(
                "active_asset_directives must contain CreativeInstructionAssetDirective values"
            )
        if not isinstance(self.creative_brief, CreativePromptBrief):
            raise CreativeInstructionPackageContractError(
                "creative_brief must be CreativePromptBrief"
            )
        object.__setattr__(
            self,
            "unknown_topics",
            _canonical_text_tuple("unknown_topics", self.unknown_topics),
        )
        object.__setattr__(
            self,
            "conflicts",
            _canonical_text_tuple("conflicts", self.conflicts),
        )
        object.__setattr__(
            self,
            "provenance_refs",
            _canonical_text_tuple("provenance_refs", self.provenance_refs),
        )
        expected_readiness = (
            READINESS_BLOCKED
            if self.unknown_topics or self.conflicts
            else READINESS_READY
        )
        if self.readiness != expected_readiness:
            raise CreativeInstructionPackageContractError(
                "readiness must be BLOCKED when unknowns/conflicts exist and READY otherwise"
            )

    @property
    def is_ready(self) -> bool:
        return self.readiness == READINESS_READY


class CreativeInstructionPackageBuilder:
    """Build one deterministic, non-persistent, provider-neutral instruction candidate."""

    def build(
        self,
        *,
        package_id: str,
        package_version: str,
        product_id: str,
        variant_id: str,
        product_profile: CreativeProductProfile,
        asset_role_profile: CreativeAssetRoleProfile,
        creative_brief: CreativePromptBrief,
        instruction_authority: str = INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
        declared_unknown_topics: Sequence[str] = (),
        declared_operator_conflicts: Sequence[str] = (),
        declared_provenance_refs: Sequence[str] = (),
    ) -> CreativeInstructionPackage:
        package_id = _required_ascii_text("package_id", package_id)
        package_version = _required_ascii_text("package_version", package_version)
        product_id = _required_ascii_text("product_id", product_id)
        variant_id = _required_ascii_text("variant_id", variant_id)

        if instruction_authority != INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE:
            raise CreativeInstructionPackageContractError(
                "first-slice instruction_authority must be PROMPT_CANDIDATE"
            )
        if not isinstance(product_profile, CreativeProductProfile):
            raise CreativeInstructionPackageContractError(
                "product_profile must be CreativeProductProfile"
            )
        if not isinstance(asset_role_profile, CreativeAssetRoleProfile):
            raise CreativeInstructionPackageContractError(
                "asset_role_profile must be CreativeAssetRoleProfile"
            )
        if not isinstance(creative_brief, CreativePromptBrief):
            raise CreativeInstructionPackageContractError(
                "creative_brief must be CreativePromptBrief"
            )

        self._require_profile_alignment(
            product_id=product_id,
            variant_id=variant_id,
            product_profile=product_profile,
            asset_role_profile=asset_role_profile,
        )

        product_directives = self._product_directives(product_profile)
        active_asset_directives = self._active_asset_directives(
            creative_brief=creative_brief,
            asset_role_profile=asset_role_profile,
        )

        product_unknowns = tuple(
            _product_unknown_topic(value, index)
            for index, value in enumerate(product_profile.unknown_topics)
        )
        asset_unknowns = _text_tuple(
            "asset_role_profile.unknown_topics",
            asset_role_profile.unknown_topics,
        )
        local_unknowns = _text_tuple(
            "declared_unknown_topics",
            declared_unknown_topics,
        )
        unknown_topics = _canonical_unique(
            (*product_unknowns, *asset_unknowns, *local_unknowns)
        )

        product_conflicts = _text_tuple(
            "product_profile.conflicts",
            product_profile.conflicts,
        )
        asset_conflicts = _text_tuple(
            "asset_role_profile.conflicts",
            asset_role_profile.conflicts,
        )
        operator_conflicts = _text_tuple(
            "declared_operator_conflicts",
            declared_operator_conflicts,
        )
        conflicts = _canonical_unique(
            (*product_conflicts, *asset_conflicts, *operator_conflicts)
        )

        reachable_provenance = _canonical_unique(
            (
                *product_profile.provenance_refs,
                *(
                    provenance_ref
                    for directive in active_asset_directives
                    for provenance_ref in directive.provenance_refs
                ),
            )
        )
        declared_provenance = _text_tuple(
            "declared_provenance_refs",
            declared_provenance_refs,
        )
        unreachable = tuple(
            value for value in declared_provenance
            if value not in set(reachable_provenance)
        )
        if unreachable:
            raise CreativeInstructionPackageContractError(
                "declared provenance is not reachable from supplied governed inputs: "
                + ", ".join(unreachable)
            )

        readiness = (
            READINESS_BLOCKED
            if unknown_topics or conflicts
            else READINESS_READY
        )

        return CreativeInstructionPackage(
            package_id=package_id,
            package_version=package_version,
            product_id=product_id,
            variant_id=variant_id,
            instruction_authority=INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE,
            readiness=readiness,
            product_directives=product_directives,
            active_asset_directives=active_asset_directives,
            creative_brief=creative_brief,
            unknown_topics=unknown_topics,
            conflicts=conflicts,
            provenance_refs=reachable_provenance,
        )

    @staticmethod
    def _require_profile_alignment(
        *,
        product_id: str,
        variant_id: str,
        product_profile: CreativeProductProfile,
        asset_role_profile: CreativeAssetRoleProfile,
    ) -> None:
        if product_profile.product_id != product_id:
            raise CreativeInstructionPackageContractError(
                "product_profile product mismatch"
            )
        if product_profile.variant_id != variant_id:
            raise CreativeInstructionPackageContractError(
                "product_profile variant mismatch"
            )
        if asset_role_profile.product_id != product_id:
            raise CreativeInstructionPackageContractError(
                "asset_role_profile product mismatch"
            )
        if asset_role_profile.variant_id != variant_id:
            raise CreativeInstructionPackageContractError(
                "asset_role_profile variant mismatch"
            )

    @staticmethod
    def _product_directives(
        product_profile: CreativeProductProfile,
    ) -> tuple[CreativeInstructionProductDirective, ...]:
        rules: tuple[CreativeProductRule, ...] = (
            *product_profile.identity_critical_rules,
            *product_profile.preserve_rules,
            *product_profile.variation_rules,
            *product_profile.prohibit_rules,
        )
        seen_ids: set[str] = set()
        directives: list[CreativeInstructionProductDirective] = []
        for rule in rules:
            if not isinstance(rule, CreativeProductRule):
                raise CreativeInstructionPackageContractError(
                    "product profile contains a non-CreativeProductRule value"
                )
            if rule.rule_id in seen_ids:
                raise CreativeInstructionPackageContractError(
                    f"duplicate product rule_id: {rule.rule_id}"
                )
            seen_ids.add(rule.rule_id)
            support_refs = _ordered_unique(
                (*rule.supporting_fact_refs, *rule.supporting_constraint_refs)
            )
            directives.append(
                CreativeInstructionProductDirective(
                    rule_id=rule.rule_id,
                    rule_kind=rule.rule_kind,
                    subject=rule.label,
                    instruction_value=rule.instruction,
                    support_refs=support_refs,
                    provenance_refs=rule.provenance_refs,
                )
            )
        return tuple(
            sorted(
                directives,
                key=lambda value: (
                    value.rule_kind,
                    value.subject,
                    value.rule_id,
                ),
            )
        )

    @staticmethod
    def _active_asset_directives(
        *,
        creative_brief: CreativePromptBrief,
        asset_role_profile: CreativeAssetRoleProfile,
    ) -> tuple[CreativeInstructionAssetDirective, ...]:
        selected_asset_ids = _text_tuple(
            "creative_brief.selected_reference_asset_ids",
            creative_brief.selected_reference_asset_ids,
        )
        if len(selected_asset_ids) != len(set(selected_asset_ids)):
            raise CreativeInstructionPackageContractError(
                "selected_reference_asset_ids must not contain duplicates"
            )

        by_asset: dict[str, list[CreativeAssetRoleDirective]] = {}
        seen_directive_ids: set[str] = set()
        for directive in asset_role_profile.directives:
            if not isinstance(directive, CreativeAssetRoleDirective):
                raise CreativeInstructionPackageContractError(
                    "asset role profile contains a non-CreativeAssetRoleDirective value"
                )
            if directive.directive_id in seen_directive_ids:
                raise CreativeInstructionPackageContractError(
                    f"duplicate asset directive_id: {directive.directive_id}"
                )
            seen_directive_ids.add(directive.directive_id)
            by_asset.setdefault(directive.asset_id, []).append(directive)

        active: list[CreativeInstructionAssetDirective] = []
        for asset_id in selected_asset_ids:
            directives = by_asset.get(asset_id, ())
            if not directives:
                raise CreativeInstructionPackageContractError(
                    f"selected reference asset lacks explicit Asset Role semantics: {asset_id}"
                )
            for directive in directives:
                active.append(
                    CreativeInstructionAssetDirective(
                        directive_id=directive.directive_id,
                        asset_id=directive.asset_id,
                        asset_version_identity=directive.asset_version_identity,
                        role_kind=directive.role_kind,
                        view_kind=directive.view_kind,
                        reference_strength=directive.reference_strength,
                        support_refs=directive.support_refs,
                        provenance_refs=directive.provenance_refs,
                    )
                )

        return tuple(
            sorted(
                active,
                key=lambda value: (
                    value.role_kind,
                    value.view_kind,
                    value.reference_strength,
                    value.asset_id,
                    value.directive_id,
                ),
            )
        )


__all__ = [
    "CreativeInstructionAssetDirective",
    "CreativeInstructionPackage",
    "CreativeInstructionPackageBuilder",
    "CreativeInstructionPackageContractError",
    "CreativeInstructionProductDirective",
    "INSTRUCTION_AUTHORITY_PROMPT_CANDIDATE",
    "READINESS_BLOCKED",
    "READINESS_READY",
    "READINESS_VALUES",
]
