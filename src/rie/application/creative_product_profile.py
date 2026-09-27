"""Governed Creative Product Profile application boundary.

This module is framework-neutral, deterministic, non-persistent, and model-free.
It projects explicit, grounded Product Intelligence support into creative-fidelity
rules. It does not inspect images, select reference assets, compose prompts,
execute generators, approve outputs, or mutate governed assets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rie.application.product_intelligence_query import (
    ProductIntelligenceConstraint,
    ProductIntelligenceContext,
    ProductIntelligenceFact,
    ProductIntelligenceUnknown,
)


class CreativeProductProfileContractError(ValueError):
    """Fail-closed contract error for Creative Product Profile construction."""


RULE_KIND_IDENTITY_CRITICAL = "IDENTITY_CRITICAL"
RULE_KIND_PRESERVE = "PRESERVE"
RULE_KIND_MAY_VARY = "MAY_VARY"
RULE_KIND_PROHIBIT = "PROHIBIT"

RULE_KINDS = (
    RULE_KIND_IDENTITY_CRITICAL,
    RULE_KIND_PRESERVE,
    RULE_KIND_MAY_VARY,
    RULE_KIND_PROHIBIT,
)

SCOPE_PRODUCT = "PRODUCT"
SCOPE_VARIANT = "VARIANT"
RULE_SCOPES = (SCOPE_PRODUCT, SCOPE_VARIANT)


def _required_ascii_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise CreativeProductProfileContractError(
            f"{field_name} must be nonempty ASCII text"
        )
    if value != value.strip():
        raise CreativeProductProfileContractError(
            f"{field_name} must not have leading or trailing whitespace"
        )
    if not value.isascii():
        raise CreativeProductProfileContractError(
            f"{field_name} must be ASCII text"
        )
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise CreativeProductProfileContractError(
            f"{field_name} must not contain control characters"
        )
    return value


def _reference_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, tuple):
        raise CreativeProductProfileContractError(
            f"{field_name} must be a tuple"
        )
    output = tuple(
        _required_ascii_text(item, f"{field_name}[{index}]")
        for index, item in enumerate(value)
    )
    if len(output) != len(set(output)):
        raise CreativeProductProfileContractError(
            f"{field_name} must not contain duplicates"
        )
    return output


@dataclass(frozen=True, slots=True)
class CreativeProductRule:
    rule_id: str
    rule_kind: str
    label: str
    instruction: str
    scope: str
    supporting_fact_refs: tuple[str, ...] = ()
    supporting_constraint_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _required_ascii_text(self.rule_id, "rule_id")
        _required_ascii_text(self.label, "label")
        _required_ascii_text(self.instruction, "instruction")
        if self.rule_kind not in RULE_KINDS:
            raise CreativeProductProfileContractError(
                f"unsupported rule_kind: {self.rule_kind}"
            )
        if self.scope not in RULE_SCOPES:
            raise CreativeProductProfileContractError(
                f"unsupported scope: {self.scope}"
            )
        _reference_tuple(self.supporting_fact_refs, "supporting_fact_refs")
        _reference_tuple(
            self.supporting_constraint_refs,
            "supporting_constraint_refs",
        )
        _reference_tuple(self.provenance_refs, "provenance_refs")
        if not self.supporting_fact_refs and not self.supporting_constraint_refs:
            raise CreativeProductProfileContractError(
                "every creative product rule requires explicit grounded support"
            )


@dataclass(frozen=True, slots=True)
class CreativeProductProfile:
    profile_id: str
    profile_version: str
    product_id: str
    variant_id: str
    identity_critical_rules: tuple[CreativeProductRule, ...] = ()
    preserve_rules: tuple[CreativeProductRule, ...] = ()
    variation_rules: tuple[CreativeProductRule, ...] = ()
    prohibit_rules: tuple[CreativeProductRule, ...] = ()
    unknown_topics: tuple[ProductIntelligenceUnknown, ...] = ()
    conflicts: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _required_ascii_text(self.profile_id, "profile_id")
        _required_ascii_text(self.profile_version, "profile_version")
        _required_ascii_text(self.product_id, "product_id")
        _required_ascii_text(self.variant_id, "variant_id")
        for field_name, expected_kind in (
            ("identity_critical_rules", RULE_KIND_IDENTITY_CRITICAL),
            ("preserve_rules", RULE_KIND_PRESERVE),
            ("variation_rules", RULE_KIND_MAY_VARY),
            ("prohibit_rules", RULE_KIND_PROHIBIT),
        ):
            rules = getattr(self, field_name)
            if not isinstance(rules, tuple):
                raise CreativeProductProfileContractError(
                    f"{field_name} must be a tuple"
                )
            if any(
                not isinstance(rule, CreativeProductRule)
                or rule.rule_kind != expected_kind
                for rule in rules
            ):
                raise CreativeProductProfileContractError(
                    f"{field_name} contains an incompatible rule kind"
                )
        if not isinstance(self.unknown_topics, tuple) or any(
            not isinstance(item, ProductIntelligenceUnknown)
            for item in self.unknown_topics
        ):
            raise CreativeProductProfileContractError(
                "unknown_topics must preserve ProductIntelligenceUnknown values"
            )
        _reference_tuple(self.conflicts, "conflicts")
        _reference_tuple(self.provenance_refs, "provenance_refs")


def _unique_by_id(
    values: Iterable[object],
    *,
    id_field: str,
    label: str,
) -> dict[str, object]:
    output: dict[str, object] = {}
    for value in values:
        identity = _required_ascii_text(
            getattr(value, id_field, None),
            f"{label}.{id_field}",
        )
        if identity in output:
            raise CreativeProductProfileContractError(
                f"duplicate {label} identity: {identity}"
            )
        output[identity] = value
    return output


def _ordered_union(sequences: Iterable[Iterable[str]]) -> tuple[str, ...]:
    output: list[str] = []
    seen: set[str] = set()
    for sequence in sequences:
        for value in sequence:
            if value not in seen:
                output.append(value)
                seen.add(value)
    return tuple(output)


class CreativeProductProfileBuilder:
    """Validate explicit declarations against one exact Product Intelligence context."""

    def build(
        self,
        *,
        context: ProductIntelligenceContext,
        profile_id: str,
        profile_version: str,
        rules: tuple[CreativeProductRule, ...],
    ) -> CreativeProductProfile:
        if not isinstance(context, ProductIntelligenceContext):
            raise CreativeProductProfileContractError(
                "context must be ProductIntelligenceContext"
            )
        profile_id = _required_ascii_text(profile_id, "profile_id")
        profile_version = _required_ascii_text(
            profile_version,
            "profile_version",
        )
        product_id = _required_ascii_text(context.product_id, "context.product_id")
        variant_id = _required_ascii_text(context.variant_id, "context.variant_id")

        if not isinstance(rules, tuple):
            raise CreativeProductProfileContractError("rules must be a tuple")
        if any(not isinstance(rule, CreativeProductRule) for rule in rules):
            raise CreativeProductProfileContractError(
                "rules must contain only CreativeProductRule values"
            )

        facts = _unique_by_id(
            context.fact_groups,
            id_field="fact_id",
            label="fact",
        )
        constraints = _unique_by_id(
            context.preservation_constraints,
            id_field="constraint_id",
            label="constraint",
        )

        validated_rules: list[CreativeProductRule] = []
        seen_rule_ids: set[str] = set()
        for rule in rules:
            if rule.rule_id in seen_rule_ids:
                raise CreativeProductProfileContractError(
                    f"duplicate rule_id: {rule.rule_id}"
                )
            seen_rule_ids.add(rule.rule_id)
            validated_rules.append(
                self._validate_rule(
                    rule=rule,
                    facts=facts,
                    constraints=constraints,
                )
            )

        self._reject_exact_contradictions(tuple(validated_rules))

        identity_rules = tuple(
            rule
            for rule in validated_rules
            if rule.rule_kind == RULE_KIND_IDENTITY_CRITICAL
        )
        preserve_rules = tuple(
            rule
            for rule in validated_rules
            if rule.rule_kind == RULE_KIND_PRESERVE
        )
        variation_rules = tuple(
            rule
            for rule in validated_rules
            if rule.rule_kind == RULE_KIND_MAY_VARY
        )
        prohibit_rules = tuple(
            rule
            for rule in validated_rules
            if rule.rule_kind == RULE_KIND_PROHIBIT
        )

        profile_provenance = _ordered_union(
            rule.provenance_refs for rule in validated_rules
        )

        return CreativeProductProfile(
            profile_id=profile_id,
            profile_version=profile_version,
            product_id=product_id,
            variant_id=variant_id,
            identity_critical_rules=identity_rules,
            preserve_rules=preserve_rules,
            variation_rules=variation_rules,
            prohibit_rules=prohibit_rules,
            unknown_topics=tuple(context.unknown_topics),
            conflicts=tuple(context.conflicts),
            provenance_refs=profile_provenance,
        )

    def _validate_rule(
        self,
        *,
        rule: CreativeProductRule,
        facts: dict[str, object],
        constraints: dict[str, object],
    ) -> CreativeProductRule:
        supporting_facts: list[ProductIntelligenceFact] = []
        supporting_constraints: list[ProductIntelligenceConstraint] = []

        for fact_ref in rule.supporting_fact_refs:
            fact = facts.get(fact_ref)
            if not isinstance(fact, ProductIntelligenceFact):
                raise CreativeProductProfileContractError(
                    f"unknown supporting fact reference: {fact_ref}"
                )
            supporting_facts.append(fact)

        for constraint_ref in rule.supporting_constraint_refs:
            constraint = constraints.get(constraint_ref)
            if not isinstance(constraint, ProductIntelligenceConstraint):
                raise CreativeProductProfileContractError(
                    f"unknown supporting constraint reference: {constraint_ref}"
                )
            supporting_constraints.append(constraint)

        self._validate_scope(
            rule=rule,
            supporting_facts=tuple(supporting_facts),
            supporting_constraints=tuple(supporting_constraints),
        )

        reachable_provenance: list[tuple[str, ...]] = []
        for fact in supporting_facts:
            reachable_provenance.append(
                _reference_tuple(
                    fact.provenance_refs,
                    f"fact[{fact.fact_id}].provenance_refs",
                )
            )
        for constraint in supporting_constraints:
            source_refs = _reference_tuple(
                constraint.source_fact_refs,
                f"constraint[{constraint.constraint_id}].source_fact_refs",
            )
            for source_ref in source_refs:
                source_fact = facts.get(source_ref)
                if not isinstance(source_fact, ProductIntelligenceFact):
                    raise CreativeProductProfileContractError(
                        "constraint source fact is absent from supplied context: "
                        + source_ref
                    )
                reachable_provenance.append(
                    _reference_tuple(
                        source_fact.provenance_refs,
                        f"fact[{source_fact.fact_id}].provenance_refs",
                    )
                )

        derived_provenance = _ordered_union(reachable_provenance)
        if rule.provenance_refs and rule.provenance_refs != derived_provenance:
            raise CreativeProductProfileContractError(
                "rule provenance_refs must exactly match reachable grounded provenance"
            )

        return CreativeProductRule(
            rule_id=rule.rule_id,
            rule_kind=rule.rule_kind,
            label=rule.label,
            instruction=rule.instruction,
            scope=rule.scope,
            supporting_fact_refs=rule.supporting_fact_refs,
            supporting_constraint_refs=rule.supporting_constraint_refs,
            provenance_refs=derived_provenance,
        )

    @staticmethod
    def _validate_scope(
        *,
        rule: CreativeProductRule,
        supporting_facts: tuple[ProductIntelligenceFact, ...],
        supporting_constraints: tuple[ProductIntelligenceConstraint, ...],
    ) -> None:
        support_scopes = tuple(
            getattr(item, "scope", None)
            for item in (*supporting_facts, *supporting_constraints)
        )
        for index, support_scope in enumerate(support_scopes):
            if support_scope not in ("product", "variant"):
                raise CreativeProductProfileContractError(
                    f"unsupported upstream support scope at index {index}: "
                    + str(support_scope)
                )
        if rule.scope == SCOPE_PRODUCT and any(
            support_scope != "product"
            for support_scope in support_scopes
        ):
            raise CreativeProductProfileContractError(
                "PRODUCT rule scope must not widen variant-scoped support"
            )

    @staticmethod
    def _reject_exact_contradictions(
        rules: tuple[CreativeProductRule, ...],
    ) -> None:
        by_subject: dict[tuple[str, str], set[str]] = {}
        for rule in rules:
            subject = (rule.scope, rule.label)
            by_subject.setdefault(subject, set()).add(rule.rule_kind)

        for (scope, label), kinds in by_subject.items():
            if RULE_KIND_MAY_VARY in kinds and (
                RULE_KIND_PRESERVE in kinds
                or RULE_KIND_PROHIBIT in kinds
                or RULE_KIND_IDENTITY_CRITICAL in kinds
            ):
                raise CreativeProductProfileContractError(
                    "exact modeled contradiction for "
                    f"{scope}/{label}: MAY_VARY conflicts with protected rule"
                )


__all__ = [
    "CreativeProductProfile",
    "CreativeProductProfileBuilder",
    "CreativeProductProfileContractError",
    "CreativeProductRule",
    "RULE_KIND_IDENTITY_CRITICAL",
    "RULE_KIND_MAY_VARY",
    "RULE_KIND_PRESERVE",
    "RULE_KIND_PROHIBIT",
    "RULE_KINDS",
    "RULE_SCOPES",
    "SCOPE_PRODUCT",
    "SCOPE_VARIANT",
]
