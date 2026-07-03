#!/usr/bin/env python3
"""The Paper Girls color script as data — the game's single palette authority.

The law (docs/DESIGN.md "Art Direction"): every scene is a dominant hue FIELD plus
one hot ACCENT; shadows hue-shift toward the scene's bias (violet or teal), never
toward neutral gray; beige/brown/gray fields are forbidden. Material ramps derive
from scene seeds via ramp4() so a sheet cannot drift off its scene's palette.

ACTOR ramps (Basil, Schweinler, slime) are hand-tuned identity colors that already
obey the shadow law; they travel across scenes, so they live here as explicit data
rather than derived ramps.
"""
import colorsys

# HLS hue targets the dark end of every ramp is pulled toward
SHADOW_HUES = {"violet": 0.76, "teal": 0.50}


def _clamp(v):
    return max(0.0, min(1.0, v))


# Ramp curve control points at u = 0, 1/3, 2/3, 1: (lightness delta, hue pull
# toward the shadow bias, saturation delta). ramp() interpolates these for any
# tone count; ramp4() hits them exactly.
_RAMP_STOPS = ((+0.14, -0.05, -0.08),   # lit
               (0.00, 0.00, 0.00),      # base
               (-0.13, 0.30, 0.10),     # shade
               (-0.24, 0.55, 0.18))     # core shadow


def _ramp_curve(u):
    """Piecewise-linear (dl, pull, ds) at u in 0..1 through _RAMP_STOPS."""
    f = u * (len(_RAMP_STOPS) - 1)
    i = min(len(_RAMP_STOPS) - 2, int(f))
    w = f - i
    a, b = _RAMP_STOPS[i], _RAMP_STOPS[i + 1]
    return tuple(a[k] + (b[k] - a[k]) * w for k in range(3))


def ramp(base, shadow="violet", tones=6, spread=1.0, alpha=255):
    """N-tone light->dark ramp from one seed RGB(A).

    The dark tones pull their hue toward the scene's shadow bias and gain
    saturation; the lit tone drifts slightly sunward. spread scales contrast.
    6 tones give painted terrain real midtone form; sprites stay at 4.
    """
    r, g, b = (v / 255 for v in base[:3])
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    d = SHADOW_HUES[shadow] - h
    if d > 0.5:
        d -= 1.0
    elif d < -0.5:
        d += 1.0
    out = []
    for i in range(tones):
        dl, pull, ds = _ramp_curve(i / (tones - 1))
        hh = (h + d * pull * spread) % 1.0
        rr, gg, bb = colorsys.hls_to_rgb(hh, _clamp(l + dl * spread), _clamp(s + ds * spread))
        out.append((round(rr * 255), round(gg * 255), round(bb * 255), alpha))
    return out


def ramp4(base, shadow="violet", spread=1.0, alpha=255):
    """4-tone [lit, base, shade, core] ramp — legacy wrapper over ramp()."""
    return ramp(base, shadow, 4, spread, alpha)


# ---- scene palettes (field / accent / shadow bias + material seeds) ---------------
# Seeds feed ramp4(seed, SCENES[key]["shadow"]). Accents are used raw and hot.

SCENES = {
    "title": {          # indigo -> magenta -> gold posterized sunset
        "shadow": "violet",
        "accent": (255, 196, 84, 255),          # leaf gold
        "mats": {},
    },
    "night_yard": {     # periwinkle-violet night, amber window glow
        "shadow": "violet",
        "accent": (255, 190, 96, 255),
        "mats": {
            "plaster": (150, 148, 214, 255),
            "timber": (96, 74, 142, 255),
            "grass": (74, 120, 158, 255),
        },
    },
    "bedroom": {        # dusty lavender-blue pre-dawn, hot peach sunbeam
        "shadow": "violet",
        "accent": (255, 178, 128, 255),
        "mats": {
            "wall": (168, 162, 216, 255),
            "floor": (128, 108, 176, 255),
            "linen": (226, 222, 240, 255),
        },
    },
    "morning_yard": {   # sun-warmed peach/coral plaster, hot magenta shingles
        "shadow": "violet",
        "accent": (238, 82, 158, 255),
        "mats": {
            "plaster": (246, 188, 152, 255),
            "timber": (150, 88, 132, 255),
            "grass": (110, 186, 138, 255),
        },
    },
    "road": {           # minty teal + peach path in dawn-pink light
        "shadow": "teal",
        "accent": (255, 116, 176, 255),
        "mats": {
            "grass": (104, 186, 128, 255),
            "path": (238, 178, 138, 255),
            "hedge": (38, 112, 98, 255),
        },
    },
    "hall": {           # deep plum timber duotone, chalk-mint accent
        "shadow": "violet",
        "accent": (150, 240, 214, 255),         # chalk mint
        "mats": {
            "timber": (118, 76, 128, 255),
            "floor": (146, 96, 132, 255),
            "board": (36, 72, 74, 255),
        },
    },
    "overworld": {      # teal sea + sage-teal continent, hot violet wastes
        "shadow": "teal",
        "accent": (196, 120, 255, 255),         # wastes crystal violet
        "mats": {
            "sea": (52, 122, 156, 255),
            "grass": (116, 178, 122, 255),
            "forest": (44, 122, 104, 255),
            "rock": (150, 138, 182, 255),
            "sand": (238, 198, 148, 255),
            "waste": (172, 122, 162, 255),
        },
    },
    "meadow": {         # minty teal greens, candy hot-pink flowers
        "shadow": "teal",
        "accent": (255, 116, 176, 255),         # hot pink
        # Hand-tuned identity ramps (same precedent as ACTORS): warm dirt cannot
        # be derived — teal shadows turn it yellow-green, violet ones salmon.
        # This one walks cream -> peach -> dusty rust -> mauve, desaturating.
        "ramps": {
            "path": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
        },
        "mats": {
            "grass": (94, 178, 118, 255),
            "grass2": (108, 182, 108, 255),     # warmer drift patches
            "path": (230, 176, 130, 255),
            "hedge": (34, 106, 94, 255),
            "rock": (144, 150, 172, 255),
            "treeline": (38, 118, 92, 255),     # border canopy mass
            "trunk": (66, 84, 104, 255),        # understory / bark
            "water": (70, 152, 172, 255),       # pond
            "shore": (222, 172, 134, 255),      # wet-sand ring
        },
    },
}

# ---- actor palettes (identity colors; hand-tuned, shadow-law compliant) -----------

# Basil — jet-black tuxedo cat, violet-shifted fur shadows, cool white coat
_FUR    = [(78, 74, 96, 255), (52, 50, 66, 255), (34, 32, 46, 255), (20, 18, 30, 255)]
_WHITE  = [(250, 248, 242, 255), (228, 224, 216, 255), (198, 194, 192, 255), (162, 158, 166, 255)]
_COATR  = [(236, 236, 238, 255), (204, 204, 210, 255), (166, 166, 178, 255), (126, 126, 142, 255)]
_PANTR  = [(72, 70, 86, 255), (56, 54, 68, 255), (42, 40, 52, 255), (30, 28, 40, 255)]
_GOGRIM = [(140, 100, 62, 255), (112, 78, 50, 255), (86, 58, 38, 255), (60, 40, 28, 255)]
_GOGLEN = [(238, 214, 168, 255), (206, 178, 132, 255), (174, 146, 104, 255), (140, 114, 82, 255)]
_GUNR   = [(140, 148, 164, 255), (108, 114, 130, 255), (80, 86, 102, 255), (56, 60, 76, 255)]

_OUT_FUR   = (8, 6, 14, 255)
_OUT_LIGHT = (58, 56, 72, 255)
_OUT_GOG   = (38, 24, 16, 255)

_BASIL_OUTS = {}
for _r, _o in ((_FUR, _OUT_FUR), (_PANTR, _OUT_FUR), (_GUNR, _OUT_FUR),
               (_WHITE, _OUT_LIGHT), (_COATR, _OUT_LIGHT),
               (_GOGRIM, _OUT_GOG), (_GOGLEN, _OUT_GOG)):
    for _c in _r:
        _BASIL_OUTS[_c] = _o

BASIL = {
    "FUR": _FUR, "WHITE": _WHITE, "COATR": _COATR, "PANTR": _PANTR,
    "GOGRIM": _GOGRIM, "GOGLEN": _GOGLEN, "GUNR": _GUNR,
    "EYE_Y": (224, 188, 70, 255), "EYE_YL": (242, 218, 118, 255),
    "PUPIL": (16, 12, 16, 255), "GLINT": (255, 255, 250, 255),
    "NOSE": (28, 22, 26, 255), "MOUTH": (146, 108, 104, 255),
    "EARIN": (204, 116, 134, 255), "EARIN_D": (160, 84, 104, 255),
    "WHISK": (216, 214, 208, 235), "WHISKD": (150, 146, 142, 255),
    "GUNE": (132, 246, 152, 255),   # laser emitter green (bolt + muzzle flash too)
    "GUNP": (188, 132, 232, 255),   # gun purple (and the coat pen)
    "OUTS": _BASIL_OUTS, "OUT_FALLBACK": _OUT_FUR,
}

# Schweinler — smug pig: rosy hide, pale belly, red neckerchief, cloven trotters.
# Hand-tuned like Basil's; dark ends nudged violet per the shadow law.
_PIG   = [(238, 190, 176, 255), (214, 152, 140, 255), (186, 114, 112, 255), (148, 80, 96, 255)]
_BELLY = [(246, 214, 200, 255), (230, 182, 168, 255), (206, 144, 138, 255), (176, 108, 114, 255)]
_KERCH = [(212, 100, 86, 255), (184, 68, 60, 255), (152, 44, 50, 255), (114, 30, 52, 255)]
_HOOF  = [(132, 80, 78, 255), (108, 60, 62, 255), (84, 44, 54, 255), (60, 32, 48, 255)]

_SCHW_OUTS = {}
for _r, _o in ((_PIG, (76, 34, 48, 255)), (_BELLY, (76, 34, 48, 255)),
               (_KERCH, (70, 16, 32, 255)), (_HOOF, (36, 18, 30, 255))):
    for _c in _r:
        _SCHW_OUTS[_c] = _o

SCHWEINLER = {
    "PIG": _PIG, "BELLY": _BELLY, "KERCH": _KERCH, "HOOF": _HOOF,
    "EYE_D": (30, 22, 26, 255), "GLINT": (255, 252, 248, 255),
    "BROW": (128, 56, 62, 255), "NOSTR": (150, 74, 84, 255),
    "MOUTH": (150, 74, 84, 255), "TONGUE": (222, 110, 116, 255),
    "MAW": (96, 40, 48, 255),
    "OUTS": _SCHW_OUTS, "OUT_FALLBACK": (76, 34, 48, 255),
}

# Slime — meadow gel, teal-shadowed greens
SLIME = {
    "GELR": [(172, 240, 180, 255), (116, 210, 132, 255), (76, 170, 100, 255), (50, 130, 78, 255)],
    "OUT": (24, 62, 40, 255),
    "EYE": (24, 34, 28, 255),
    "GLINT": (235, 250, 238, 255),
}

ACTORS = {"basil": BASIL, "schweinler": SCHWEINLER, "slime": SLIME}
