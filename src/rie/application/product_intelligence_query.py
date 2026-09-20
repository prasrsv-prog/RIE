"""Framework-neutral read-only product intelligence query boundary for PC2."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from rie.application.grounded_prompt_application_foundation_provider import (
    load_frozen_pilot_grounded_prompt_application_foundation,
)
from rie.rsv_knowledge.phase_b_exact_six_active_constraint_bridge import (
    materialize_exact_six_active_product_constraints,
)
from rie.rsv_knowledge.phase_b_prompt_input_bridge import (
    materialize_traceable_evidence_backed_product_variant_prompt_inputs,
)


class ProductIntelligenceQueryContractError(ValueError):
    """Fail-closed contract error for product-intelligence reads."""


@dataclass(frozen=True)
class ProductIntelligenceProduct:
    product_id: str
    label: str


@dataclass(frozen=True)
class ProductIntelligenceVariant:
    variant_id: str
    product_id: str
    label: str


@dataclass(frozen=True)
class ProductIntelligenceFact:
    fact_id: str
    category: str
    label: str
    value: str
    scope: str
    authority_state: str = "grounded"
    provenance_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProductIntelligenceConstraint:
    constraint_id: str
    label: str
    rule_text: str
    scope: str
    severity: str = "preserve"
    source_fact_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProductIntelligenceUnknown:
    topic: str
    user_facing_label: str
    reason: str = "absent"


@dataclass(frozen=True)
class ProductIntelligenceProvenance:
    reference_id: str
    source_type: str = ""
    authority: str = ""
    status: str = ""
    version: str = ""
    source_paths: tuple[str, ...] = ()

    @property
    def summary(self) -> str:
        parts = tuple(
            value
            for value in (
                self.source_type,
                self.authority,
                self.status,
                self.version,
            )
            if value
        )
        return " / ".join(parts) or self.reference_id


@dataclass(frozen=True)
class ProductIntelligenceContext:
    product_id: str
    variant_id: str
    product_label: str
    variant_label: str
    summary: str
    fact_groups: tuple[ProductIntelligenceFact, ...] = ()
    preservation_constraints: tuple[ProductIntelligenceConstraint, ...] = ()
    authorized_reference_asset_ids: tuple[str, ...] = ()
    unknown_topics: tuple[ProductIntelligenceUnknown, ...] = ()
    conflicts: tuple[str, ...] = ()
    provenance_summary: str = ""


def _required_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProductIntelligenceQueryContractError(
            f"{field_name} must be a nonempty string"
        )
    return value.strip()


def _display_label(value: object, field_name: str) -> str:
    return _required_text(value, field_name)


def _record_scope_matches(
    record: object,
    *,
    product_id: str,
    variant_id: str,
) -> bool:
    if getattr(record, "product_id", None) != product_id:
        return False
    record_variant_id = getattr(record, "variant_id", None)
    return record_variant_id is None or record_variant_id == variant_id


class ProductIntelligenceQuery:
    """Read-only projection over published deterministic materialization paths."""

    def __init__(self, *, foundation: object) -> None:
        required = (
            "collection_id",
            "catalog",
            "governed_knowledge",
            "knowledge_mappings",
            "traceable_evidence_items",
            "product_constraint_governed_knowledge",
            "product_constraint_ingestion_manifest_records",
            "product_constraint_knowledge_mappings",
        )
        missing = tuple(name for name in required if not hasattr(foundation, name))
        if missing:
            raise ProductIntelligenceQueryContractError(
                "foundation missing required fields: " + ",".join(missing)
            )

        self._foundation = foundation
        self._identity_bridge = (
            materialize_traceable_evidence_backed_product_variant_prompt_inputs(
                collection_id=foundation.collection_id,
                catalog=foundation.catalog,
                governed_knowledge=foundation.governed_knowledge,
                knowledge_mappings=foundation.knowledge_mappings,
                traceable_evidence_items=foundation.traceable_evidence_items,
            )
        )
        self._exact_six_bridge = materialize_exact_six_active_product_constraints(
            catalog=foundation.catalog,
            governed_knowledge=foundation.product_constraint_governed_knowledge,
            ingestion_manifest_records=(
                foundation.product_constraint_ingestion_manifest_records
            ),
            knowledge_mappings=foundation.product_constraint_knowledge_mappings,
        )
        self._validate_materialized_results()
        self._provenance_index = self._build_provenance_index()

    @classmethod
    def from_intake_root(
        cls,
        *,
        intake_root: str | Path,
    ) -> "ProductIntelligenceQuery":
        foundation = load_frozen_pilot_grounded_prompt_application_foundation(
            intake_root=intake_root
        )
        return cls(foundation=foundation)

    def list_products(self) -> tuple[ProductIntelligenceProduct, ...]:
        products = []
        for product in tuple(self._foundation.catalog.products):
            if getattr(product, "status", None) != "active":
                continue
            product_id = _required_text(
                getattr(product, "product_id", None),
                "product_id",
            )
            label = _display_label(
                getattr(product, "canonical_name", None),
                f"product label for {product_id}",
            )
            products.append(
                ProductIntelligenceProduct(
                    product_id=product_id,
                    label=label,
                )
            )
        labels = tuple(item.label for item in products)
        if len(labels) != len(set(labels)):
            raise ProductIntelligenceQueryContractError(
                "active product presentation labels must be unique"
            )
        return tuple(products)

    def list_variants(
        self,
        product_id: str,
    ) -> tuple[ProductIntelligenceVariant, ...]:
        product_id = _required_text(product_id, "product_id")
        if product_id not in {item.product_id for item in self.list_products()}:
            raise ProductIntelligenceQueryContractError(
                f"unknown active product_id: {product_id}"
            )

        variants = []
        for variant in tuple(self._foundation.catalog.variants):
            if (
                getattr(variant, "status", None) != "active"
                or getattr(variant, "product_id", None) != product_id
            ):
                continue
            variant_id = _required_text(
                getattr(variant, "variant_id", None),
                "variant_id",
            )
            label = _display_label(
                getattr(variant, "canonical_name", None),
                f"variant label for {variant_id}",
            )
            variants.append(
                ProductIntelligenceVariant(
                    variant_id=variant_id,
                    product_id=product_id,
                    label=label,
                )
            )

        labels = tuple(item.label for item in variants)
        if len(labels) != len(set(labels)):
            raise ProductIntelligenceQueryContractError(
                f"active variant presentation labels must be unique for product_id: {product_id}"
            )
        return tuple(variants)

    def get_product_context(
        self,
        product_id: str,
        variant_id: str,
    ) -> ProductIntelligenceContext:
        product_id = _required_text(product_id, "product_id")
        variant_id = _required_text(variant_id, "variant_id")

        product_by_id = {
            item.product_id: item for item in self.list_products()
        }
        if product_id not in product_by_id:
            raise ProductIntelligenceQueryContractError(
                f"unknown active product_id: {product_id}"
            )

        variants = {
            item.variant_id: item for item in self.list_variants(product_id)
        }
        if variant_id not in variants:
            raise ProductIntelligenceQueryContractError(
                f"unknown active variant_id for {product_id}: {variant_id}"
            )

        facts = self._project_facts(
            product_id=product_id,
            variant_id=variant_id,
        )
        constraints = self._project_constraints(
            product_id=product_id,
            variant_id=variant_id,
        )

        unknowns: tuple[ProductIntelligenceUnknown, ...] = ()
        if not facts:
            unknowns = (
                ProductIntelligenceUnknown(
                    topic="grounded_product_facts",
                    user_facing_label=(
                        "No grounded product facts are available for this selection."
                    ),
                    reason="absent",
                ),
            )

        provenance_refs = tuple(
            dict.fromkeys(
                reference_id
                for fact in facts
                for reference_id in fact.provenance_refs
            )
        )
        provenance_items = tuple(
            self.get_provenance(reference_id)
            for reference_id in provenance_refs
        )
        provenance_summary = "; ".join(
            item.summary for item in provenance_items
        )

        summary = (
            f"{len(facts)} grounded fact"
            f"{'' if len(facts) == 1 else 's'} and "
            f"{len(constraints)} preservation constraint"
            f"{'' if len(constraints) == 1 else 's'} available."
        )

        return ProductIntelligenceContext(
            product_id=product_id,
            variant_id=variant_id,
            product_label=product_by_id[product_id].label,
            variant_label=variants[variant_id].label,
            summary=summary,
            fact_groups=facts,
            preservation_constraints=constraints,
            authorized_reference_asset_ids=(),
            unknown_topics=unknowns,
            conflicts=(),
            provenance_summary=provenance_summary,
        )

    def search_product_facts(
        self,
        query: str,
        *,
        product_id: str | None = None,
        variant_id: str | None = None,
    ) -> tuple[ProductIntelligenceFact, ...]:
        query = _required_text(query, "query").casefold()

        contexts: list[ProductIntelligenceContext] = []
        if product_id is not None:
            product_id = _required_text(product_id, "product_id")
            if variant_id is not None:
                contexts.append(
                    self.get_product_context(
                        product_id,
                        _required_text(variant_id, "variant_id"),
                    )
                )
            else:
                for variant in self.list_variants(product_id):
                    contexts.append(
                        self.get_product_context(product_id, variant.variant_id)
                    )
        else:
            if variant_id is not None:
                raise ProductIntelligenceQueryContractError(
                    "variant_id requires product_id"
                )
            for product in self.list_products():
                for variant in self.list_variants(product.product_id):
                    contexts.append(
                        self.get_product_context(
                            product.product_id,
                            variant.variant_id,
                        )
                    )

        matches: dict[str, ProductIntelligenceFact] = {}
        for context in contexts:
            for fact in context.fact_groups:
                haystack = " ".join(
                    (fact.category, fact.label, fact.value)
                ).casefold()
                if query in haystack:
                    matches.setdefault(fact.fact_id, fact)
        return tuple(matches[key] for key in sorted(matches))

    def get_provenance(
        self,
        reference_id: str,
    ) -> ProductIntelligenceProvenance:
        reference_id = _required_text(reference_id, "reference_id")
        if reference_id not in self._provenance_index:
            raise ProductIntelligenceQueryContractError(
                f"unknown provenance reference: {reference_id}"
            )
        return self._provenance_index[reference_id]

    def _validate_materialized_results(self) -> None:
        for label, result in (
            ("identity", self._identity_bridge.prompt_inputs),
            ("exact-six", self._exact_six_bridge.prompt_inputs),
        ):
            if result.materialization_status != "PASSED":
                raise ProductIntelligenceQueryContractError(
                    f"{label} materialization did not pass"
                )
            if result.missing_mappings or result.conflicts:
                raise ProductIntelligenceQueryContractError(
                    f"{label} materialization returned missing/conflict state"
                )

        if len(self._identity_bridge.bridge_records) != len(
            self._identity_bridge.prompt_inputs.knowledge_records
        ):
            raise ProductIntelligenceQueryContractError(
                "identity bridge record count does not match knowledge records"
            )
        if len(self._exact_six_bridge.prompt_inputs.constraint_records) != 6:
            raise ProductIntelligenceQueryContractError(
                "exact-six constraint count drift"
            )

    def _build_provenance_index(
        self,
    ) -> dict[str, ProductIntelligenceProvenance]:
        knowledge_by_id = {
            record.knowledge_id: record
            for record in self._identity_bridge.prompt_inputs.knowledge_records
        }
        asset_by_id = {
            record.asset_id: record
            for record in self._identity_bridge.prompt_inputs.asset_records
        }

        output: dict[str, ProductIntelligenceProvenance] = {}
        for bridge_record in self._identity_bridge.bridge_records:
            knowledge = knowledge_by_id.get(bridge_record.knowledge_id)
            if knowledge is None:
                raise ProductIntelligenceQueryContractError(
                    "bridge record references unknown knowledge_id: "
                    + bridge_record.knowledge_id
                )
            if knowledge.source_asset_id != bridge_record.bridged_source_asset_id:
                raise ProductIntelligenceQueryContractError(
                    "bridge/source asset mismatch for knowledge_id: "
                    + bridge_record.knowledge_id
                )
            asset = asset_by_id.get(bridge_record.bridged_source_asset_id)
            if asset is None:
                raise ProductIntelligenceQueryContractError(
                    "bridge record references unknown bridged asset: "
                    + bridge_record.bridged_source_asset_id
                )
            reference_id = _required_text(
                bridge_record.traceable_evidence_id,
                "traceable_evidence_id",
            )
            if reference_id in output:
                raise ProductIntelligenceQueryContractError(
                    "duplicate traceable_evidence_id: " + reference_id
                )
            source_paths = tuple(bridge_record.source_relative_paths)
            if not source_paths:
                raise ProductIntelligenceQueryContractError(
                    "provenance source paths must not be empty"
                )
            if not all(
                isinstance(path, str) and path.strip()
                for path in source_paths
            ):
                raise ProductIntelligenceQueryContractError(
                    "provenance source paths must be nonempty strings"
                )
            output[reference_id] = ProductIntelligenceProvenance(
                reference_id=reference_id,
                source_type=_required_text(asset.asset_type, "asset_type"),
                authority=_required_text(asset.authority, "authority"),
                status=_required_text(asset.status, "status"),
                version=_required_text(asset.version, "version"),
                source_paths=source_paths,
            )
        return output

    def _project_facts(
        self,
        *,
        product_id: str,
        variant_id: str,
    ) -> tuple[ProductIntelligenceFact, ...]:
        provenance_by_knowledge_id = {
            record.knowledge_id: record.traceable_evidence_id
            for record in self._identity_bridge.bridge_records
        }
        output = []
        for record in self._identity_bridge.prompt_inputs.knowledge_records:
            if not _record_scope_matches(
                record,
                product_id=product_id,
                variant_id=variant_id,
            ):
                continue
            if record.variant_id != variant_id:
                continue
            provenance_id = provenance_by_knowledge_id.get(record.knowledge_id)
            if provenance_id is None:
                raise ProductIntelligenceQueryContractError(
                    "identity knowledge missing traceable evidence bridge: "
                    + record.knowledge_id
                )
            output.append(
                ProductIntelligenceFact(
                    fact_id=record.knowledge_id,
                    category=record.knowledge_type,
                    label=record.property.replace("_", " ").title(),
                    value=record.value,
                    scope="variant",
                    authority_state=record.status,
                    provenance_refs=(provenance_id,),
                )
            )
        return tuple(sorted(output, key=lambda item: item.fact_id))

    def _project_constraints(
        self,
        *,
        product_id: str,
        variant_id: str,
    ) -> tuple[ProductIntelligenceConstraint, ...]:
        records = (
            tuple(self._identity_bridge.prompt_inputs.constraint_records)
            + tuple(self._exact_six_bridge.prompt_inputs.constraint_records)
        )
        output = []
        for record in records:
            if not _record_scope_matches(
                record,
                product_id=product_id,
                variant_id=variant_id,
            ):
                continue
            output.append(
                ProductIntelligenceConstraint(
                    constraint_id=record.constraint_id,
                    label=record.constraint_type.replace("_", " ").title(),
                    rule_text=record.rule,
                    scope=(
                        "variant"
                        if record.variant_id is not None
                        else "product"
                    ),
                    severity="preserve",
                    source_fact_refs=(
                        record.source_knowledge_id_or_asset_id,
                    ),
                )
            )
        return tuple(
            sorted(
                output,
                key=lambda item: (item.scope, item.constraint_id),
            )
        )
