from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Mapping, Sequence


class CreativeAssetRoleContractError(ValueError):
    """Raised when a creative-asset role profile violates the PR-127B contract."""


ROLE_IDENTITY_ANCHOR: Final[str] = "IDENTITY_ANCHOR"
ROLE_FORM_REFERENCE: Final[str] = "FORM_REFERENCE"
ROLE_SURFACE_DETAIL_REFERENCE: Final[str] = "SURFACE_DETAIL_REFERENCE"
ROLE_PACKAGING_REFERENCE: Final[str] = "PACKAGING_REFERENCE"
ROLE_CONTEXT_REFERENCE: Final[str] = "CONTEXT_REFERENCE"

ALLOWED_ROLE_KINDS: Final[tuple[str, ...]] = (
    ROLE_IDENTITY_ANCHOR,
    ROLE_FORM_REFERENCE,
    ROLE_SURFACE_DETAIL_REFERENCE,
    ROLE_PACKAGING_REFERENCE,
    ROLE_CONTEXT_REFERENCE,
)

VIEW_UNSPECIFIED: Final[str] = "UNSPECIFIED"
VIEW_FRONT: Final[str] = "FRONT"
VIEW_BACK: Final[str] = "BACK"
VIEW_LEFT: Final[str] = "LEFT"
VIEW_RIGHT: Final[str] = "RIGHT"
VIEW_TOP: Final[str] = "TOP"
VIEW_BOTTOM: Final[str] = "BOTTOM"
VIEW_THREE_QUARTER: Final[str] = "THREE_QUARTER"
VIEW_DETAIL: Final[str] = "DETAIL"
VIEW_PACKAGING: Final[str] = "PACKAGING"
VIEW_CONTEXT: Final[str] = "CONTEXT"

ALLOWED_VIEW_KINDS: Final[tuple[str, ...]] = (
    VIEW_UNSPECIFIED,
    VIEW_FRONT,
    VIEW_BACK,
    VIEW_LEFT,
    VIEW_RIGHT,
    VIEW_TOP,
    VIEW_BOTTOM,
    VIEW_THREE_QUARTER,
    VIEW_DETAIL,
    VIEW_PACKAGING,
    VIEW_CONTEXT,
)

REFERENCE_PRIMARY: Final[str] = "PRIMARY"
REFERENCE_SUPPORTING: Final[str] = "SUPPORTING"
REFERENCE_CONTEXT_ONLY: Final[str] = "CONTEXT_ONLY"

ALLOWED_REFERENCE_STRENGTHS: Final[tuple[str, ...]] = (
    REFERENCE_PRIMARY,
    REFERENCE_SUPPORTING,
    REFERENCE_CONTEXT_ONLY,
)

VISUAL_REFERENCE_VERSION_IDENTITY_PREFIX: Final[str] = "sha256:"


def _required_ascii_text(name: str, value: object) -> str:
    if not isinstance(value, str):
        raise CreativeAssetRoleContractError(f"{name} must be text")
    if not value or value != value.strip():
        raise CreativeAssetRoleContractError(
            f"{name} must be non-empty text without surrounding whitespace"
        )
    try:
        value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise CreativeAssetRoleContractError(f"{name} must be ASCII text") from exc
    return value


def _reference_tuple(name: str, values: Sequence[str]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise CreativeAssetRoleContractError(f"{name} must be a sequence of references")
    result = tuple(_required_ascii_text(f"{name}[{index}]", value) for index, value in enumerate(values))
    if len(set(result)) != len(result):
        raise CreativeAssetRoleContractError(f"{name} must not contain duplicate references")
    return result


def _canonical_text_tuple(name: str, values: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted(_reference_tuple(name, values)))


@dataclass(frozen=True, slots=True)
class CreativeAssetRoleDirective:
    directive_id: str
    asset_id: str
    asset_version_identity: str
    product_id: str
    variant_id: str
    role_kind: str
    view_kind: str
    reference_strength: str
    support_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "directive_id",
            "asset_id",
            "asset_version_identity",
            "product_id",
            "variant_id",
        ):
            _required_ascii_text(field_name, getattr(self, field_name))

        if self.role_kind not in ALLOWED_ROLE_KINDS:
            raise CreativeAssetRoleContractError(
                f"role_kind must be one of {ALLOWED_ROLE_KINDS!r}"
            )
        if self.view_kind not in ALLOWED_VIEW_KINDS:
            raise CreativeAssetRoleContractError(
                f"view_kind must be one of {ALLOWED_VIEW_KINDS!r}"
            )
        if self.reference_strength not in ALLOWED_REFERENCE_STRENGTHS:
            raise CreativeAssetRoleContractError(
                "reference_strength must be PRIMARY, SUPPORTING, or CONTEXT_ONLY"
            )

        support_refs = _reference_tuple("support_refs", self.support_refs)
        provenance_refs = _reference_tuple("provenance_refs", self.provenance_refs)
        if not support_refs:
            raise CreativeAssetRoleContractError(
                "every creative asset directive requires explicit support"
            )

        if self.reference_strength == REFERENCE_CONTEXT_ONLY and self.role_kind != ROLE_CONTEXT_REFERENCE:
            raise CreativeAssetRoleContractError(
                "CONTEXT_ONLY reference strength is valid only for CONTEXT_REFERENCE"
            )

        object.__setattr__(self, "support_refs", tuple(sorted(support_refs)))
        object.__setattr__(self, "provenance_refs", tuple(sorted(provenance_refs)))


@dataclass(frozen=True, slots=True)
class CreativeAssetRoleProfile:
    profile_id: str
    profile_version: str
    product_id: str
    variant_id: str
    directives: tuple[CreativeAssetRoleDirective, ...]
    unknown_topics: tuple[str, ...]
    conflicts: tuple[str, ...]
    provenance_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in ("profile_id", "profile_version", "product_id", "variant_id"):
            _required_ascii_text(field_name, getattr(self, field_name))
        object.__setattr__(
            self, "unknown_topics", _canonical_text_tuple("unknown_topics", self.unknown_topics)
        )
        object.__setattr__(self, "conflicts", _canonical_text_tuple("conflicts", self.conflicts))
        object.__setattr__(
            self, "provenance_refs", _canonical_text_tuple("provenance_refs", self.provenance_refs)
        )


@dataclass(frozen=True, slots=True)
class _GovernedAssetBinding:
    asset_id: str
    asset_version_identity: str
    product_id: str
    variant_id: str | None


def _asset_attr(asset: object, name: str) -> object:
    if not hasattr(asset, name):
        raise CreativeAssetRoleContractError(
            f"governed asset is missing required attribute {name}"
        )
    return getattr(asset, name)


def _asset_version_identity(asset: object) -> str:
    for attribute in ("asset_version_identity", "version_identity"):
        value = getattr(asset, attribute, None)
        if value is not None:
            return _required_ascii_text(attribute, value)

    sha256 = getattr(asset, "sha256", None)
    if sha256 is None:
        raise CreativeAssetRoleContractError(
            "governed asset must expose asset_version_identity, version_identity, or sha256"
        )
    sha256_text = _required_ascii_text("sha256", sha256).lower()
    if len(sha256_text) != 64 or any(character not in "0123456789abcdef" for character in sha256_text):
        raise CreativeAssetRoleContractError("sha256 must be 64 lowercase hexadecimal characters")
    return VISUAL_REFERENCE_VERSION_IDENTITY_PREFIX + sha256_text


def _bind_governed_asset(asset: object) -> _GovernedAssetBinding:
    asset_id = _required_ascii_text("governed_asset.asset_id", _asset_attr(asset, "asset_id"))
    product_id = _required_ascii_text("governed_asset.product_id", _asset_attr(asset, "product_id"))
    raw_variant = getattr(asset, "variant_id", None)
    if raw_variant is None:
        variant_id: str | None = None
    else:
        variant_id = _required_ascii_text("governed_asset.variant_id", raw_variant)

    return _GovernedAssetBinding(
        asset_id=asset_id,
        asset_version_identity=_asset_version_identity(asset),
        product_id=product_id,
        variant_id=variant_id,
    )


def _support_provenance_map(
    support_provenance: Mapping[str, Sequence[str]] | None,
) -> dict[str, tuple[str, ...]]:
    if support_provenance is None:
        return {}
    if not isinstance(support_provenance, Mapping):
        raise CreativeAssetRoleContractError("support_provenance must be a mapping")

    result: dict[str, tuple[str, ...]] = {}
    for raw_support_ref, raw_provenance_refs in support_provenance.items():
        support_ref = _required_ascii_text("support_provenance key", raw_support_ref)
        result[support_ref] = _canonical_text_tuple(
            f"support_provenance[{support_ref!r}]", raw_provenance_refs
        )
    return result


class CreativeAssetRoleProfileBuilder:
    """Build deterministic, model-free creative-use semantics for governed assets."""

    def build(
        self,
        *,
        product_id: str,
        variant_id: str,
        governed_assets: Sequence[object],
        directives: Sequence[CreativeAssetRoleDirective],
        profile_id: str,
        profile_version: str,
        support_provenance: Mapping[str, Sequence[str]] | None = None,
        unknown_topics: Sequence[str] = (),
        conflicts: Sequence[str] = (),
    ) -> CreativeAssetRoleProfile:
        product_id = _required_ascii_text("product_id", product_id)
        variant_id = _required_ascii_text("variant_id", variant_id)
        profile_id = _required_ascii_text("profile_id", profile_id)
        profile_version = _required_ascii_text("profile_version", profile_version)

        if isinstance(governed_assets, (str, bytes)) or not isinstance(governed_assets, Sequence):
            raise CreativeAssetRoleContractError("governed_assets must be a sequence")
        if isinstance(directives, (str, bytes)) or not isinstance(directives, Sequence):
            raise CreativeAssetRoleContractError("directives must be a sequence")

        asset_bindings: dict[str, _GovernedAssetBinding] = {}
        for asset in governed_assets:
            binding = _bind_governed_asset(asset)
            if binding.asset_id in asset_bindings:
                raise CreativeAssetRoleContractError(
                    f"governed asset IDs must be unique: {binding.asset_id}"
                )
            if binding.product_id != product_id:
                raise CreativeAssetRoleContractError(
                    f"governed asset product mismatch: {binding.asset_id}"
                )
            if binding.variant_id is not None and binding.variant_id != variant_id:
                raise CreativeAssetRoleContractError(
                    f"governed asset variant mismatch: {binding.asset_id}"
                )
            asset_bindings[binding.asset_id] = binding

        support_map = _support_provenance_map(support_provenance)

        by_directive_id: dict[str, CreativeAssetRoleDirective] = {}
        semantic_strength: dict[tuple[str, str, str], str] = {}
        primary_by_role_view: dict[tuple[str, str], str] = {}
        all_provenance: set[str] = set()
        accepted: list[CreativeAssetRoleDirective] = []

        for directive in directives:
            if not isinstance(directive, CreativeAssetRoleDirective):
                raise CreativeAssetRoleContractError(
                    "directives must contain CreativeAssetRoleDirective values"
                )

            if directive.directive_id in by_directive_id:
                prior = by_directive_id[directive.directive_id]
                if prior != directive:
                    raise CreativeAssetRoleContractError(
                        f"duplicate directive_id with differing content: {directive.directive_id}"
                    )
                raise CreativeAssetRoleContractError(
                    f"duplicate directive_id: {directive.directive_id}"
                )
            by_directive_id[directive.directive_id] = directive

            if directive.product_id != product_id:
                raise CreativeAssetRoleContractError(
                    f"directive product mismatch: {directive.directive_id}"
                )
            if directive.variant_id != variant_id:
                raise CreativeAssetRoleContractError(
                    f"directive variant mismatch: {directive.directive_id}"
                )

            binding = asset_bindings.get(directive.asset_id)
            if binding is None:
                raise CreativeAssetRoleContractError(
                    f"unknown governed asset_id: {directive.asset_id}"
                )
            if directive.asset_version_identity != binding.asset_version_identity:
                raise CreativeAssetRoleContractError(
                    f"asset version mismatch: {directive.asset_id}"
                )

            reachable_provenance: set[str] = set()
            for support_ref in directive.support_refs:
                if support_ref in support_map:
                    reachable_provenance.update(support_map[support_ref])
                else:
                    # A support reference may itself be the provenance identity.
                    reachable_provenance.add(support_ref)

            declared_provenance = set(directive.provenance_refs)
            if not declared_provenance.issubset(reachable_provenance):
                raise CreativeAssetRoleContractError(
                    f"directive provenance is not reachable from explicit support: {directive.directive_id}"
                )

            semantic_key = (
                directive.asset_id,
                directive.role_kind,
                directive.view_kind,
            )
            prior_strength = semantic_strength.get(semantic_key)
            if prior_strength is not None and prior_strength != directive.reference_strength:
                raise CreativeAssetRoleContractError(
                    "same asset/role/view cannot have contradictory reference strengths"
                )
            semantic_strength[semantic_key] = directive.reference_strength

            if directive.reference_strength == REFERENCE_PRIMARY:
                primary_key = (directive.role_kind, directive.view_kind)
                prior_asset = primary_by_role_view.get(primary_key)
                if prior_asset is not None and prior_asset != directive.asset_id:
                    raise CreativeAssetRoleContractError(
                        "multiple PRIMARY assets for the same role/view are not allowed"
                    )
                primary_by_role_view[primary_key] = directive.asset_id

            all_provenance.update(directive.provenance_refs)
            accepted.append(directive)

        canonical_directives = tuple(
            sorted(
                accepted,
                key=lambda value: (
                    value.role_kind,
                    value.view_kind,
                    value.reference_strength,
                    value.asset_id,
                    value.directive_id,
                ),
            )
        )

        return CreativeAssetRoleProfile(
            profile_id=profile_id,
            profile_version=profile_version,
            product_id=product_id,
            variant_id=variant_id,
            directives=canonical_directives,
            unknown_topics=_canonical_text_tuple("unknown_topics", unknown_topics),
            conflicts=_canonical_text_tuple("conflicts", conflicts),
            provenance_refs=tuple(sorted(all_provenance)),
        )


__all__ = [
    "ALLOWED_REFERENCE_STRENGTHS",
    "ALLOWED_ROLE_KINDS",
    "ALLOWED_VIEW_KINDS",
    "CreativeAssetRoleContractError",
    "CreativeAssetRoleDirective",
    "CreativeAssetRoleProfile",
    "CreativeAssetRoleProfileBuilder",
    "REFERENCE_CONTEXT_ONLY",
    "REFERENCE_PRIMARY",
    "REFERENCE_SUPPORTING",
    "ROLE_CONTEXT_REFERENCE",
    "ROLE_FORM_REFERENCE",
    "ROLE_IDENTITY_ANCHOR",
    "ROLE_PACKAGING_REFERENCE",
    "ROLE_SURFACE_DETAIL_REFERENCE",
    "VIEW_BACK",
    "VIEW_BOTTOM",
    "VIEW_CONTEXT",
    "VIEW_DETAIL",
    "VIEW_FRONT",
    "VIEW_LEFT",
    "VIEW_PACKAGING",
    "VIEW_RIGHT",
    "VIEW_THREE_QUARTER",
    "VIEW_TOP",
    "VIEW_UNSPECIFIED",
    "VISUAL_REFERENCE_VERSION_IDENTITY_PREFIX",
]
