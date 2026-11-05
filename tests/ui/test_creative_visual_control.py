from io import BytesIO

from PIL import Image
import pytest

from rie.ui.creative_visual_control import (
    compose_creative_notes, approximate_pixel_change, SCENES,
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
