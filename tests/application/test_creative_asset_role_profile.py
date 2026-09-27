from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from rie.application.creative_asset_role_profile import (
    ALLOWED_REFERENCE_STRENGTHS,
    ALLOWED_ROLE_KINDS,
    ALLOWED_VIEW_KINDS,
    CreativeAssetRoleContractError,
    CreativeAssetRoleDirective,
    CreativeAssetRoleProfileBuilder,
    REFERENCE_CONTEXT_ONLY,
    REFERENCE_PRIMARY,
    REFERENCE_SUPPORTING,
    ROLE_CONTEXT_REFERENCE,
    ROLE_FORM_REFERENCE,
    ROLE_IDENTITY_ANCHOR,
    ROLE_PACKAGING_REFERENCE,
    ROLE_SURFACE_DETAIL_REFERENCE,
    VIEW_CONTEXT,
    VIEW_DETAIL,
    VIEW_FRONT,
    VIEW_THREE_QUARTER,
    VIEW_UNSPECIFIED,
)


SHA_A = "1" * 64
SHA_B = "2" * 64


@dataclass(frozen=True)
class _Asset:
    asset_id: str
    product_id: str
    variant_id: str | None
    sha256: str


def _asset(
    asset_id: str = "asset-front",
    *,
    product_id: str = "sv300",
    variant_id: str | None = "white-glossy",
    sha256: str = SHA_A,
) -> _Asset:
    return _Asset(
        asset_id=asset_id,
        product_id=product_id,
        variant_id=variant_id,
        sha256=sha256,
    )


def _directive(
    directive_id: str = "directive-1",
    *,
    asset_id: str = "asset-front",
    asset_version_identity: str = "sha256:" + SHA_A,
    product_id: str = "sv300",
    variant_id: str = "white-glossy",
    role_kind: str = ROLE_IDENTITY_ANCHOR,
    view_kind: str = VIEW_FRONT,
    reference_strength: str = REFERENCE_PRIMARY,
    support_refs: tuple[str, ...] = ("support:human:1",),
    provenance_refs: tuple[str, ...] = ("source:annotation:1",),
) -> CreativeAssetRoleDirective:
    return CreativeAssetRoleDirective(
        directive_id=directive_id,
        asset_id=asset_id,
        asset_version_identity=asset_version_identity,
        product_id=product_id,
        variant_id=variant_id,
        role_kind=role_kind,
        view_kind=view_kind,
        reference_strength=reference_strength,
        support_refs=support_refs,
        provenance_refs=provenance_refs,
    )


def _build(
    *directives: CreativeAssetRoleDirective,
    assets: tuple[object, ...] | None = None,
    support_provenance: dict[str, tuple[str, ...]] | None = None,
    unknown_topics: tuple[str, ...] = (),
    conflicts: tuple[str, ...] = (),
):
    if assets is None:
        assets = (_asset(),)
    if support_provenance is None:
        support_provenance = {
            "support:human:1": ("source:annotation:1",),
            "support:human:2": ("source:annotation:2",),
            "support:human:3": ("source:annotation:3",),
        }
    return CreativeAssetRoleProfileBuilder().build(
        product_id="sv300",
        variant_id="white-glossy",
        governed_assets=assets,
        directives=directives,
        profile_id="asset-role-profile:sv300:white-glossy",
        profile_version="1.0.0",
        support_provenance=support_provenance,
        unknown_topics=unknown_topics,
        conflicts=conflicts,
    )


@pytest.mark.parametrize("role_kind", ALLOWED_ROLE_KINDS)
def test_all_five_role_kinds_are_accepted_when_explicitly_supported(role_kind: str) -> None:
    strength = (
        REFERENCE_SUPPORTING
        if role_kind == ROLE_CONTEXT_REFERENCE
        else REFERENCE_PRIMARY
    )
    profile = _build(
        _directive(
            role_kind=role_kind,
            view_kind=VIEW_UNSPECIFIED,
            reference_strength=strength,
        )
    )
    assert profile.directives[0].role_kind == role_kind


@pytest.mark.parametrize("view_kind", ALLOWED_VIEW_KINDS)
def test_all_allowed_view_kinds_are_accepted(view_kind: str) -> None:
    profile = _build(
        _directive(
            view_kind=view_kind,
            reference_strength=REFERENCE_SUPPORTING,
        )
    )
    assert profile.directives[0].view_kind == view_kind


@pytest.mark.parametrize(
    ("role_kind", "reference_strength"),
    (
        (ROLE_IDENTITY_ANCHOR, REFERENCE_PRIMARY),
        (ROLE_FORM_REFERENCE, REFERENCE_SUPPORTING),
        (ROLE_CONTEXT_REFERENCE, REFERENCE_CONTEXT_ONLY),
    ),
)
def test_all_reference_strengths_are_accepted_in_valid_combinations(
    role_kind: str,
    reference_strength: str,
) -> None:
    assert reference_strength in ALLOWED_REFERENCE_STRENGTHS
    profile = _build(
        _directive(
            role_kind=role_kind,
            reference_strength=reference_strength,
            view_kind=VIEW_CONTEXT if role_kind == ROLE_CONTEXT_REFERENCE else VIEW_FRONT,
        )
    )
    assert profile.directives[0].reference_strength == reference_strength


def test_context_only_is_rejected_for_non_context_role() -> None:
    with pytest.raises(CreativeAssetRoleContractError, match="CONTEXT_ONLY"):
        _directive(reference_strength=REFERENCE_CONTEXT_ONLY)


def test_missing_support_fails_closed() -> None:
    with pytest.raises(CreativeAssetRoleContractError, match="explicit support"):
        _directive(support_refs=(), provenance_refs=())


def test_unknown_asset_id_fails_closed() -> None:
    with pytest.raises(CreativeAssetRoleContractError, match="unknown governed asset_id"):
        _build(_directive(asset_id="asset-missing"))


def test_asset_version_mismatch_fails_closed() -> None:
    with pytest.raises(CreativeAssetRoleContractError, match="asset version mismatch"):
        _build(_directive(asset_version_identity="sha256:" + SHA_B))


def test_product_mismatch_fails_closed() -> None:
    with pytest.raises(CreativeAssetRoleContractError, match="directive product mismatch"):
        _build(_directive(product_id="other-product"))


def test_variant_mismatch_fails_closed() -> None:
    with pytest.raises(CreativeAssetRoleContractError, match="directive variant mismatch"):
        _build(_directive(variant_id="other-variant"))


def test_governed_asset_variant_mismatch_fails_closed() -> None:
    with pytest.raises(CreativeAssetRoleContractError, match="governed asset variant mismatch"):
        _build(_directive(), assets=(_asset(variant_id="other-variant"),))


def test_product_level_asset_is_allowed_only_as_supplied_for_selected_variant() -> None:
    profile = _build(_directive(), assets=(_asset(variant_id=None),))
    assert profile.variant_id == "white-glossy"


def test_duplicate_directive_id_fails_closed() -> None:
    first = _directive()
    second = _directive()
    with pytest.raises(CreativeAssetRoleContractError, match="duplicate directive_id"):
        _build(first, second)


def test_duplicate_directive_id_with_different_content_fails_closed() -> None:
    first = _directive()
    second = _directive(reference_strength=REFERENCE_SUPPORTING)
    with pytest.raises(
        CreativeAssetRoleContractError,
        match="duplicate directive_id with differing content",
    ):
        _build(first, second)


def test_contradictory_strength_assignment_fails_closed() -> None:
    first = _directive(
        directive_id="directive-primary",
        reference_strength=REFERENCE_PRIMARY,
    )
    second = _directive(
        directive_id="directive-supporting",
        reference_strength=REFERENCE_SUPPORTING,
        support_refs=("support:human:2",),
        provenance_refs=("source:annotation:2",),
    )
    with pytest.raises(CreativeAssetRoleContractError, match="contradictory reference strengths"):
        _build(first, second)


def test_multiple_primary_references_for_same_role_view_fail_closed() -> None:
    first = _directive(
        directive_id="directive-primary-a",
        asset_id="asset-front",
        asset_version_identity="sha256:" + SHA_A,
    )
    second = _directive(
        directive_id="directive-primary-b",
        asset_id="asset-alt",
        asset_version_identity="sha256:" + SHA_B,
        support_refs=("support:human:2",),
        provenance_refs=("source:annotation:2",),
    )
    with pytest.raises(CreativeAssetRoleContractError, match="multiple PRIMARY"):
        _build(first, second, assets=(_asset(), _asset("asset-alt", sha256=SHA_B)))


def test_unknown_view_may_remain_unspecified() -> None:
    profile = _build(
        _directive(
            role_kind=ROLE_SURFACE_DETAIL_REFERENCE,
            view_kind=VIEW_UNSPECIFIED,
            reference_strength=REFERENCE_SUPPORTING,
        )
    )
    assert profile.directives[0].view_kind == VIEW_UNSPECIFIED


def test_unknown_topics_and_conflicts_are_preserved_deterministically() -> None:
    profile = _build(
        _directive(),
        unknown_topics=("view:side", "surface:microtexture"),
        conflicts=("annotation:conflict-b", "annotation:conflict-a"),
    )
    assert profile.unknown_topics == ("surface:microtexture", "view:side")
    assert profile.conflicts == ("annotation:conflict-a", "annotation:conflict-b")


def test_declared_provenance_must_be_reachable_from_explicit_support() -> None:
    with pytest.raises(CreativeAssetRoleContractError, match="not reachable"):
        _build(
            _directive(provenance_refs=("source:unrelated",)),
            support_provenance={"support:human:1": ("source:annotation:1",)},
        )


def test_support_reference_can_itself_be_provenance_identity() -> None:
    directive = _directive(
        support_refs=("source:annotation:1",),
        provenance_refs=("source:annotation:1",),
    )
    profile = _build(directive, support_provenance={})
    assert profile.provenance_refs == ("source:annotation:1",)


def test_explicit_version_identity_is_accepted_without_sha_derivation() -> None:
    @dataclass(frozen=True)
    class _VersionedAsset:
        asset_id: str = "asset-front"
        product_id: str = "sv300"
        variant_id: str = "white-glossy"
        asset_version_identity: str = "version:explicit:1"

    profile = _build(
        _directive(asset_version_identity="version:explicit:1"),
        assets=(_VersionedAsset(),),
    )
    assert profile.directives[0].asset_version_identity == "version:explicit:1"


def test_equivalent_construction_is_deterministic() -> None:
    first = _directive(
        directive_id="directive-form",
        role_kind=ROLE_FORM_REFERENCE,
        view_kind=VIEW_THREE_QUARTER,
        reference_strength=REFERENCE_SUPPORTING,
    )
    second = _directive(
        directive_id="directive-detail",
        role_kind=ROLE_SURFACE_DETAIL_REFERENCE,
        view_kind=VIEW_DETAIL,
        reference_strength=REFERENCE_SUPPORTING,
        support_refs=("support:human:2",),
        provenance_refs=("source:annotation:2",),
    )

    profile_a = _build(
        first,
        second,
        unknown_topics=("unknown:b", "unknown:a"),
        conflicts=("conflict:b", "conflict:a"),
    )
    profile_b = _build(
        second,
        first,
        unknown_topics=("unknown:a", "unknown:b"),
        conflicts=("conflict:a", "conflict:b"),
    )
    assert profile_a == profile_b


def test_first_slice_is_framework_neutral_model_free_non_persistent_and_has_no_inference_path() -> None:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "rie"
        / "application"
        / "creative_asset_role_profile.py"
    )
    text = source_path.read_text(encoding="utf-8")
    lowered = text.lower()

    for forbidden in (
        "pyside6",
        "tkinter",
        "sqlite3",
        "requests",
        "httpx",
        "openai",
        "torch",
        "transformers",
        "image.open",
        "pillow",
        "opencv",
        "cv2",
        "load_preview_bytes",
        "os.listdir",
        "glob(",
        "pathlib.path.glob",
        "governed_asset_library_registry",
        "json_file_governed_asset_library_repository",
        "creative_prompt_composer",
        "visual_generation_provider",
    ):
        assert forbidden not in lowered

    assert "getattr(asset, \"sha256\"" in text
    assert "filename" not in lowered
    assert "exif" not in lowered
    assert "embedding" not in lowered
