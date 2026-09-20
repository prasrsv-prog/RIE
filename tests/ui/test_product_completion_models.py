from __future__ import annotations

import pytest

from rie.ui.product_completion_models import (
    CreativeBrief,
    ProductConstraint,
    ProductContextSnapshot,
    ProductFact,
    ProductUnknown,
)


def test_product_fact_requires_grounded_nonempty_identity_fields() -> None:
    fact = ProductFact(
        fact_id="fact-material",
        category="Appearance",
        label="Material",
        value="ABS",
        scope="product",
        provenance_refs=("gk1_example",),
    )
    assert fact.value == "ABS"
    assert fact.scope == "product"


def test_product_fact_rejects_unsupported_scope() -> None:
    with pytest.raises(ValueError, match="scope"):
        ProductFact(
            fact_id="fact",
            category="Appearance",
            label="Material",
            value="ABS",
            scope="creative",  # type: ignore[arg-type]
        )


def test_product_context_display_name_keeps_human_labels() -> None:
    snapshot = ProductContextSnapshot(
        product_id="sv300",
        variant_id="white-glossy",
        product_label="SV300",
        variant_label="White Glossy",
    )
    assert snapshot.display_name == "SV300 / White Glossy"


def test_product_context_keeps_fact_constraint_unknown_classes_separate() -> None:
    fact = ProductFact(
        fact_id="f1",
        category="Appearance",
        label="Material",
        value="ABS",
        scope="product",
    )
    constraint = ProductConstraint(
        constraint_id="c1",
        label="Shell material",
        rule_text="Preserve ABS shell material",
        scope="product",
    )
    unknown = ProductUnknown(
        topic="exact-weight",
        user_facing_label="Exact weight is not available",
    )
    snapshot = ProductContextSnapshot(
        product_id="sv300",
        variant_id="white-glossy",
        product_label="SV300",
        variant_label="White Glossy",
        fact_groups=(fact,),
        preservation_constraints=(constraint,),
        unknown_topics=(unknown,),
    )
    assert snapshot.fact_groups == (fact,)
    assert snapshot.preservation_constraints == (constraint,)
    assert snapshot.unknown_topics == (unknown,)


def test_creative_brief_projects_only_legacy_submit_fields() -> None:
    brief = CreativeBrief(
        objective="hero image",
        deliverable="grounded product prompt",
        environment="dark studio",
        camera_angle="front",
        lighting_style="soft",
        mood_style="premium",
    )
    assert brief.legacy_submit_fields() == {
        "background": "dark studio",
        "camera_angle": "front",
        "requested_output": "grounded product prompt",
    }