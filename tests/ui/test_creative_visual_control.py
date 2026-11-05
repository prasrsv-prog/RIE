from io import BytesIO

from PIL import Image
import pytest

from rie.ui.creative_visual_control import (
    compose_creative_notes, approximate_pixel_change, SCENES,
    suggest_creative_retry, visual_difference_feedback,
)


def _png(color):
    image = Image.new("RGB", (64, 64), color)
    data = BytesIO()
    image.save(data, format="PNG")
    return data.getvalue()


def test_original_notes_untouched_in_default_as_brief_mode():
    assert compose_creative_notes(" operator text ", "as_brief", "balanced") == " operator text "


def test_strength_alone_changes_direction_and_preserves_notes():
    result = compose_creative_notes(" operator text ", "as_brief", "bold")
    assert "operator text" in result
    assert "Make the scene and lighting substantially different" in result
    assert "Do not invent, replace, recolor" in result


@pytest.mark.parametrize("scene", [s for s in SCENES if s != "as_brief"])
def test_scene_direction_has_grounded_product_identity_guard(scene):
    notes = compose_creative_notes("manual", scene, "bold")
    assert notes.startswith("manual")
    assert "NOT a product redesign" in notes
    assert "exact approved variant" in notes
    assert "Do not invent, replace, recolor" in notes


@pytest.mark.parametrize("scene,intensity", [("bogus", "bold"), ("campaign", "bogus")])
def test_bad_mode_rejected(scene, intensity):
    with pytest.raises(ValueError):
        compose_creative_notes("", scene, intensity)


def test_pixel_difference_equal_and_opposite():
    black = _png("black")
    assert approximate_pixel_change(black, black) == 0
    assert approximate_pixel_change(black, _png("white")) == 100


def test_pixel_difference_invalid_input_returns_none():
    assert approximate_pixel_change(b"nope", _png("black")) is None
    assert approximate_pixel_change(_png("black"), b"notimage" * 100) is None


@pytest.mark.parametrize("scene,intensity,expected", [
    ("as_brief", "balanced", ("premium_studio", "bold")),
    ("premium_studio", "subtle", ("premium_studio", "bold")),
    ("outdoor_lifestyle", "balanced", ("outdoor_lifestyle", "bold")),
    ("premium_studio", "bold", ("outdoor_lifestyle", "bold")),
    ("outdoor_lifestyle", "bold", ("campaign", "bold")),
    ("campaign", "bold", ("premium_studio", "bold")),
])
def test_i45_suggests_new_bounded_scene_without_provider_call(scene, intensity, expected):
    assert suggest_creative_retry(0, scene, intensity) == expected


@pytest.mark.parametrize("score", [None, -1, 10, 100, True])
def test_i45_no_retry_for_unavailable_or_not_very_similar(score):
    assert suggest_creative_retry(score, "as_brief", "balanced") is None


def test_i45_similarity_advice_is_localized_and_not_a_product_quality_claim():
    id_text = visual_difference_feedback(0, locale="id-ID")
    en_text = visual_difference_feedback(0, locale="en-US")
    assert "0%" in id_text and "Sangat mirip" in id_text
    assert "bukan pemeriksaan" in id_text
    assert "0%" in en_text and "Very similar" in en_text
    assert "not a product" in en_text
    assert "Periksa secara visual" in visual_difference_feedback(30)
    assert "Comparison unavailable" in visual_difference_feedback(None, locale="en-US")
