"""Procedural city materials extracted from Glyph City."""

import math

FOV = math.radians(76)
FAR = 78.0
EYE = 1.72
TAU = math.tau

# Surface masks keep rain response and facade reflections tied to the material
# under the projected pixel.  Grass deliberately has no wet sheen or facade
# reflection; roads, paving and bridges can catch a reduced wet highlight.
WETNESS_MASK = {"w": 0.35, "r": 1.0, "p": 0.72, "b": 0.82}
REFLECTION_MASK = {"w": 1.0, "r": 0.82, "p": 0.42, "b": 0.58}

# Only small, repeatable decorations use the first LOD.  Buildings, signs,
# landmarks, lamps, people, cars and the boat keep their authored glyphs.
LOD_KINDS = frozenset(("tree", "flowers", "rail", "bench"))
LOD_ENTER_HEIGHT = 2.40
LOD_EXIT_HEIGHT = 1.75
LOD_ENTER_DISTANCE = 40.0
LOD_EXIT_DISTANCE = 43.0
LOD_ART = {
    "tree": (("^",), 1.05, 1.0),
    "flowers": (("*",), 0.55, 0.5),
    "rail": (("=",), 1.15, 0.28),
    "bench": (("_",), 1.0, 0.35),
}

# Tiny interior glimpses keep windows from reading as generic checkerboard
# lights.  They are intentionally abstract: at terminal scale a few props and
# a counter are more readable than detailed sprites.
INTERIOR_ART = {
    "CAFE": ("o=", (245, 183, 101)),
    "BAKERY": ("o=", (249, 196, 118)),
    "RAMEN": ("~=", (245, 155, 91)),
    "JAZZ": ("~|", (197, 146, 241)),
    "VINYL": ("()", (180, 206, 239)),
    "BOOKS": ("[]", (188, 226, 177)),
    "FLORA": ("**", (236, 143, 184)),
    "HOTEL": ("==", (214, 177, 127)),
    "BAR": ("o|", (239, 131, 167)),
    "LOUNGE": ("@~", (244, 121, 173)),
    "18+": ("@~", (244, 121, 173)),
}


def window_interior(sign, seed, bay, story, level):
    """Return a deterministic one-cell interior glimpse and its warm color."""
    key = str(sign).upper()
    mark, color = INTERIOR_ART.get(key, ("o+", (239, 174, 100)))
    index = (int(bay * 7) + story * 3 + int(level * 11) + seed) % len(mark)
    return mark[index], color


def mix(a, b, t):
    t = 0.0 if t < 0 else 1.0 if t > 1 else t
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def scale(color, factor):
    factor = max(0, factor)
    return (
        min(255, int(color[0] * factor)),
        min(255, int(color[1] * factor)),
        min(255, int(color[2] * factor)),
    )


def grain(x, y, seed=0):
    return (
        (x * 374761393 + y * 668265263 + seed * 144269) ^ (x * y * 1274126177)
    ) & 65535


def reflection_tick(time):
    """Quantize animated reflection noise so adjacent frames stay stable."""
    return int(time * 2.0)


def reflection_noise(x, y, seed, tick):
    """World-space, slowly animated noise for a reflection cell."""
    return grain(math.floor(x * 2.0), math.floor(y * 2.0), seed + tick * 7919)


def fog_factor(distance, visibility, ceiling=0.88):
    """Return a smooth, monotonic fog amount for a world-space distance."""
    if visibility <= 0:
        return ceiling
    return min(ceiling, max(0.0, distance / visibility) ** 1.5)


def shadow_band(x, y, seed):
    """Return a stable, subtle world-space shading band."""
    band = grain(math.floor(x / 3.0), math.floor(y / 3.0), seed) % 17
    return 0.9 if band < 2 else 1.0


def local_light(glow, night, lantern=False):
    """Map authored lamp glow to readable local illumination.

    The previous pass multiplied glow directly by night, which made lamps
    disappear at dusk and left the foreground too flat at night. Keep the
    source deterministic while giving nearby pools a visible warm lift.
    """
    value = max(0.0, min(1.0, float(glow)))
    return max(
        value * (0.72 + 1.18 * max(0.0, min(1.0, night))), 0.18 if lantern else 0.0
    )


def cell(ch, fg, bg):
    # Small palette steps make color runs cheaper without changing glyph width.
    return (
        ch,
        (fg[0] & 248, fg[1] & 248, fg[2] & 248),
        (bg[0] & 248, bg[1] & 248, bg[2] & 248),
    )
