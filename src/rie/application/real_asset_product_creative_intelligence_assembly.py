"""Minimum governed Real Asset / Product creative-intelligence assembly.

This module is deliberately application-layer only. It delegates product truth,
governed visual-reference reads, profile construction, role semantics, and
instruction-package readiness/authority to the already-published boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from rie.application.creative_asset_role_profile import (
    CreativeAssetRoleDirective,
    CreativeAssetRoleProfile,
    CreativeAssetRoleProfileBuilder,
)
from rie.application.creative_instruction_package import (
    CreativeInstructionPackage,
    CreativeInstructionPackageBuilder,
)
from rie.application.creative_product_profile import (
    CreativeProductProfile,
    CreativeProductProfileBuilder,
    CreativeProductRule,
)
from rie.application.creative_prompt_composer import CreativePromptBrief
from rie.application.product_intelligence_query import ProductIntelligenceQuery
from rie.application.visual_reference_asset_query import (
    VisualReferenceAsset,
    VisualReferenceAssetQuery,
)

READINESS_READY = "READY"
READINESS_BLOCKED = "BLOCKED"


class RealAssetProductCreativeIntelligenceAssemblyContractError(ValueError):
    """Fail-closed contract error for governed creative-intelligence assembly."""


@dataclass(frozen=True, slots=True)
class RealAssetProductCreativeIntelligenceAssemblyResult:
    product_id: str
    variant_id: str
    selected_reference_assets: tuple[VisualReferenceAsset, ...]
    product_profile: CreativeProductProfile
    asset_role_profile: CreativeAssetRoleProfile
    instruction_package: CreativeInstructionPackage
    readiness: str
    blocking_reasons: tuple[str, ...]
    unknowns: tuple[str, ...]
    conflicts: tuple[str, ...]
    provenance_refs: tuple[str, ...]

    @property
    def is_ready(self) -> bool:
        return self.readiness == READINESS_READY


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise RealAssetProductCreativeIntelligenceAssemblyContractError(
            f"{field_name} must be nonempty trimmed text"
        )
    return value


def _ordered_unique(values: Sequence[str]) -> tuple[str, ...]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return tuple(output)


class RealAssetProductCreativeIntelligenceAssembler:
    """Deterministic, provider-neutral orchestration over published boundaries."""

    def __init__(
        self,
        *,
        product_intelligence_query: ProductIntelligenceQuery,
        visual_reference_asset_query: VisualReferenceAssetQuery,
        product_profile_builder: CreativeProductProfileBuilder | None = None,
        asset_role_profile_builder: CreativeAssetRoleProfileBuilder | None = None,
        instruction_package_builder: CreativeInstructionPackageBuilder | None = None,
    ) -> None:
        self._product_intelligence_query = product_intelligence_query
        self._visual_reference_asset_query = visual_reference_asset_query
        self._product_profile_builder = (
            product_profile_builder or CreativeProductProfileBuilder()
        )
        self._asset_role_profile_builder = (
            asset_role_profile_builder or CreativeAssetRoleProfileBuilder()
        )
        self._instruction_package_builder = (
            instruction_package_builder or CreativeInstructionPackageBuilder()
        )

    def assemble(
        self,
        *,
        product_id: str,
        variant_id: str,
        product_profile_id: str,
        product_profile_version: str,
        product_rules: tuple[CreativeProductRule, ...],
        asset_role_profile_id: str,
        asset_role_profile_version: str,
        asset_role_directives: tuple[CreativeAssetRoleDirective, ...],
        instruction_package_id: str,
        instruction_package_version: str,
        creative_brief: CreativePromptBrief,
    ) -> RealAssetProductCreativeIntelligenceAssemblyResult:
        product_id = _required_text(product_id, "product_id")
        variant_id = _required_text(variant_id, "variant_id")

        context = self._product_intelligence_query.get_product_context(
            product_id,
            variant_id,
        )
        product_profile = self._product_profile_builder.build(
            context=context,
            profile_id=product_profile_id,
            profile_version=product_profile_version,
            rules=product_rules,
        )

        governed_assets = tuple(
            self._visual_reference_asset_query.list_assets(
                product_id=product_id,
                variant_id=variant_id,
            )
        )
        assets_by_reference_id = {
            _required_text(asset.reference_id, "governed_asset.reference_id"): asset
            for asset in governed_assets
        }
        if len(assets_by_reference_id) != len(governed_assets):
            raise RealAssetProductCreativeIntelligenceAssemblyContractError(
                "governed visual-reference result contains duplicate reference_id"
            )

        selected_reference_ids = tuple(creative_brief.selected_reference_asset_ids)
        if len(selected_reference_ids) != len(set(selected_reference_ids)):
            raise RealAssetProductCreativeIntelligenceAssemblyContractError(
                "selected_reference_asset_ids must not contain duplicates"
            )

        missing_references = tuple(
            reference_id
            for reference_id in selected_reference_ids
            if reference_id not in assets_by_reference_id
        )
        if missing_references:
            raise RealAssetProductCreativeIntelligenceAssemblyContractError(
                "selected reference is not governed for exact product/variant: "
                + ",".join(missing_references)
            )

        selected_assets = tuple(
            assets_by_reference_id[reference_id]
            for reference_id in selected_reference_ids
        )
        selected_asset_ids = tuple(
            _required_text(asset.asset_id, "governed_asset.asset_id")
            for asset in selected_assets
        )
        directive_asset_ids = tuple(
            _required_text(directive.asset_id, "asset_role_directive.asset_id")
            for directive in asset_role_directives
        )

        if len(directive_asset_ids) != len(set(directive_asset_ids)):
            raise RealAssetProductCreativeIntelligenceAssemblyContractError(
                "asset-role directives must contain exactly one directive per selected asset"
            )
        if set(directive_asset_ids) != set(selected_asset_ids):
            raise RealAssetProductCreativeIntelligenceAssemblyContractError(
                "explicit asset-role directive is required for every selected asset and only selected assets"
            )

        asset_role_profile = self._asset_role_profile_builder.build(
            product_id=product_id,
            variant_id=variant_id,
            governed_assets=selected_assets,
            directives=asset_role_directives,
            profile_id=asset_role_profile_id,
            profile_version=asset_role_profile_version,
        )

        instruction_package = self._instruction_package_builder.build(
            package_id=instruction_package_id,
            package_version=instruction_package_version,
            product_id=product_id,
            variant_id=variant_id,
            product_profile=product_profile,
            asset_role_profile=asset_role_profile,
            creative_brief=creative_brief,
        )

        readiness = _required_text(
            instruction_package.readiness,
            "instruction_package.readiness",
        )
        if readiness not in (READINESS_READY, READINESS_BLOCKED):
            raise RealAssetProductCreativeIntelligenceAssemblyContractError(
                "instruction package returned unsupported readiness"
            )

        unknowns = _ordered_unique(
            tuple(getattr(item, "topic", str(item)) for item in product_profile.unknown_topics)
            + tuple(asset_role_profile.unknown_topics)
            + tuple(instruction_package.unknown_topics)
        )
        conflicts = _ordered_unique(
            tuple(product_profile.conflicts)
            + tuple(asset_role_profile.conflicts)
            + tuple(instruction_package.conflicts)
        )
        provenance_refs = _ordered_unique(
            tuple(product_profile.provenance_refs)
            + tuple(asset_role_profile.provenance_refs)
            + tuple(instruction_package.provenance_refs)
        )

        blocking_reasons = ()
        if readiness == READINESS_BLOCKED:
            blocking_reasons = _ordered_unique(unknowns + conflicts)
            if not blocking_reasons:
                blocking_reasons = ("instruction-package-blocked",)

        return RealAssetProductCreativeIntelligenceAssemblyResult(
            product_id=product_id,
            variant_id=variant_id,
            selected_reference_assets=selected_assets,
            product_profile=product_profile,
            asset_role_profile=asset_role_profile,
            instruction_package=instruction_package,
            readiness=readiness,
            blocking_reasons=blocking_reasons,
            unknowns=unknowns,
            conflicts=conflicts,
            provenance_refs=provenance_refs,
        )
