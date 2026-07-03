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


def ramp4(base, shadow="violet", spread=1.0, alpha=255):
    """4-tone light->dark ramp [lit, base, shade, core] from one seed RGB(A).

    The dark tones pull their hue toward the scene's shadow bias and gain
    saturation; the lit tone drifts slightly sunward. spread scales contrast.
    """
    r, g, b = (v / 255 for v in base[:3])
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    d = SHADOW_HUES[shadow] - h
    if d > 0.5:
        d -= 1.0
    elif d < -0.5:
        d += 1.0
    tones = []
    for dl, pull, ds in ((+0.14, -0.05, -0.08),   # lit
                         (0.00, 0.00, 0.00),      # base
                         (-0.13, 0.30, 0.10),     # shade
                         (-0.24, 0.55, 0.18)):    # core shadow
        hh = (h + d * pull * spread) % 1.0
        rr, gg, bb = colorsys.hls_to_rgb(hh, _clamp(l + dl * spread), _clamp(s + ds * spread))
        tones.append((round(rr * 255), round(gg * 255), round(bb * 255), alpha))
    return tones


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
        "mats": {
            "grass": (94, 178, 118, 255),
            "path": (230, 176, 130, 255),
            "hedge": (34, 106, 94, 255),
            "rock": (158, 148, 176, 255),
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

# Schweinler — smug pig: rosy hide, red neckerchief, violet-leaning shadows
_PIG   = [(248, 186, 178, 255), (226, 148, 150, 255), (192, 110, 130, 255), (150, 78, 110, 255)]
_PIG_D = [(226, 148, 150, 255), (192, 110, 130, 255), (150, 78, 110, 255), (112, 56, 92, 255)]
_KERCH = [(238, 92, 92, 255), (206, 64, 78, 255), (166, 44, 70, 255), (122, 30, 60, 255)]
_HOOF  = [(120, 88, 120, 255), (94, 66, 100, 255), (70, 48, 80, 255), (48, 32, 60, 255)]

_SCHW_OUTS = {}
for _r, _o in ((_PIG, (74, 34, 62, 255)), (_PIG_D, (74, 34, 62, 255)),
               (_KERCH, (86, 18, 44, 255)), (_HOOF, (30, 18, 40, 255))):
    for _c in _r:
        _SCHW_OUTS[_c] = _o

SCHWEINLER = {
    "PIG": _PIG, "PIG_D": _PIG_D, "KERCH": _KERCH, "HOOF": _HOOF,
    "EYE": (34, 22, 36, 255), "SNOUT": (255, 214, 206, 255),
    "OUTS": _SCHW_OUTS, "OUT_FALLBACK": (74, 34, 62, 255),
}

# Slime — meadow gel, teal-shadowed greens
SLIME = {
    "GELR": [(172, 240, 180, 255), (116, 210, 132, 255), (76, 170, 100, 255), (50, 130, 78, 255)],
    "OUT": (24, 62, 40, 255),
    "EYE": (24, 34, 28, 255),
    "GLINT": (235, 250, 238, 255),
}

ACTORS = {"basil": BASIL, "schweinler": SCHWEINLER, "slime": SLIME}
