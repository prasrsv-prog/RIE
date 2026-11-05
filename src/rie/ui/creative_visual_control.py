"""Pure, offline-only scene directions and bounded before/after hints.

The difference estimate is a coarse pixel statistic, NOT a product identity or
rights decision. It cannot override the governed prompt or Gate 15 checks.
"""
from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageChops, ImageStat, UnidentifiedImageError

SCENES = {
    "as_brief": None,
    "premium_studio": {
        "environment": "dark luxury product studio with a completely new set and pedestal",
        "lighting": "dramatic directional key light, realistic rim highlights and deep shadows",
        "composition": "premium advertising hero shot, deliberate negative space, product dominant",
        "mood": "high-end cinematic commercial product photography",
        "directive": "Rebuild the environment and lighting as a premium studio advertisement, not a near-copy of the original catalog shot.",
    },
    "outdoor_lifestyle": {
        "environment": "outdoor asphalt road setting at golden hour, product safely staged as a still-life",
        "lighting": "warm low-angle sunlight with natural shadow and realistic reflections",
        "composition": "commercial lifestyle product photograph with environmental depth",
        "mood": "authentic cinematic motorcycle-lifestyle campaign",
        "directive": "Create a clearly new outdoor background and mood; do not retain the reference photo background.",
    },
    "campaign": {
        "environment": "purpose-built campaign set with geometric architecture and dramatic depth",
        "lighting": "high-contrast brand advertising lights with controlled realistic reflections",
        "composition": "distinctive campaign key visual, dynamic framing with clean product visibility",
        "mood": "bold premium commercial advertising",
        "directive": "Create a new campaign composition, set design and lighting rather than reproducing the reference photograph.",
    },
}

INTENSITIES = {
    "subtle": "Keep changes mainly in background, staging and illumination.",
    "balanced": "Make a clearly different setting, light and composition while protecting product details.",
    "bold": "Make the scene and lighting substantially different; do not redesign or recolor the actual product.",
}

PRESERVE = (
    "Product is fixed: preserve verified product silhouette, exact approved variant "
    "colorway, graphics, logos, materials and safety-critical components. "
    "Do not invent, replace, recolor or modify product features."
)


def compose_creative_notes(original: str, scene: str, intensity: str) -> str:
    """Append scene-only direction; never erase the original operator notes."""
    if not isinstance(original, str):
        raise TypeError("notes must be text")
    if scene not in SCENES or intensity not in INTENSITIES:
        raise ValueError("unknown visual scene or intensity")
    if scene == "as_brief" and intensity == "balanced":
        return original
    directive = (
        "Respect the operator-specified setting, but adjust its styling as requested."
        if scene == "as_brief" else SCENES[scene]["directive"]
    )
    block = ("SCENE DIRECTION (operator-selected; NOT a product redesign): "
             + directive + " " + INTENSITIES[intensity] + " " + PRESERVE)
    return (original.rstrip() + "\n\n" + block) if original.strip() else block


def approximate_pixel_change(reference: bytes, output: bytes) -> int | None:
    """Return approximate 0..100 pixel difference after normalization.

    This is intentionally NOT a semantic, quality or logo-preservation score.
    No image files, networking, or metadata output is created.
    """
    if not isinstance(reference, bytes) or not isinstance(output, bytes):
        return None
    if not (24 <= len(reference) <= 8 * 1024 * 1024):
        return None
    if not (24 <= len(output) <= 8 * 1024 * 1024):
        return None
    try:
        normalized = []
        for data in (reference, output):
            with Image.open(BytesIO(data)) as source:
                w, h = source.size
                if not (1 <= w <= 4096 and 1 <= h <= 4096 and w * h <= 12_000_000):
                    return None
                normalized.append(source.convert("RGB").resize((96, 96), Image.Resampling.BILINEAR))
        difference = ImageChops.difference(normalized[0], normalized[1])
        score = round(100 * sum(ImageStat.Stat(difference).mean) / (3 * 255))
        return max(0, min(100, int(score)))
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError):
        return None


def suggest_creative_retry(
    pixel_change: int | None, scene: str, intensity: str,
) -> tuple[str, str] | None:
    """Suggest new *prompt settings*, never initiate another provider call.

    A low pixel-change estimate does not prove that an output was copied or
    that product identity is correct. A scene switch is a proposed operator
    choice, not an automatic retry or an external-use authorization.
    """
    if not isinstance(pixel_change, int) or isinstance(pixel_change, bool):
        return None
    if not (0 <= pixel_change < 10):
        return None
    if scene not in SCENES or intensity not in INTENSITIES:
        return None
    if scene == "as_brief":
        return ("premium_studio", "bold")
    if intensity != "bold":
        return (scene, "bold")
    alternative = {
        "premium_studio": "outdoor_lifestyle",
        "outdoor_lifestyle": "campaign",
        "campaign": "premium_studio",
    }
    return (alternative[scene], "bold")


def visual_difference_feedback(
    pixel_change: int | None, *, locale: str = "id-ID",
) -> str:
    """Give a cautious, localized estimate, never a product-quality verdict."""
    is_id = locale == "id-ID"
    if (not isinstance(pixel_change, int) or isinstance(pixel_change, bool)
            or not 0 <= pixel_change <= 100):
        return (
            "Perbandingan belum tersedia; hasil tetap dapat disimpan."
            if is_id else "Comparison unavailable; the output can still be saved."
        )
    base = (
        f"Indikasi perbedaan piksel: {pixel_change}% (perkiraan kasar; "
        "bukan pemeriksaan desain, logo, atau identitas produk)."
        if is_id else
        f"Approximate pixel change: {pixel_change}% (coarse estimate; "
        "not a product, logo, or identity verification)."
    )
    if pixel_change < 10:
        return base + (
            " Sangat mirip dengan referensi. Perkuat/ubah scene dan bangun "
            "ulang prompt; simpan PNG dahulu jika ingin mempertahankan hasil ini."
            if is_id else
            " Very similar to the reference. Strengthen/change the scene and "
            "rebuild the prompt; save this PNG first if you want to keep it."
        )
    return base + (
        " Periksa secara visual apakah identitas produk tetap benar."
        if is_id else " Visually check whether product identity remains correct."
    )
