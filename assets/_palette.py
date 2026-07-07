#!/usr/bin/env python3
"""The Paper Girls color script as data — the game's single palette authority.

The law (docs/DESIGN.md "Art Direction"): every scene is MINIMAL and surreal —
a duo/tri-tone cast: one dominant hue FIELD plus one hot ACCENT; shadows
hue-shift toward the scene's bias (violet or teal), never toward neutral gray.
Wood may be an honest warm brown (it is a material, not the field) — the ban is
on naturalistic beige/gray mud as a scene's whole field, and on muddy
un-hue-shifted darks. Material ramps derive from scene seeds via ramp() so a
sheet cannot drift off its scene's palette.

ACTOR ramps (Basil, slime) are hand-tuned identity colors that already
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
# tone count.
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


# ---- scene palettes (field / accent / shadow bias + material seeds) ---------------
# Seeds feed ramp(seed, SCENES[key]["shadow"], tones). Accents are used raw and hot.

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
    "bedroom": {        # warm brown plank loft / cool teal floor, hot peach dawn
        "shadow": "violet",
        "accent": (255, 178, 128, 255),
        "mats": {
            "wall": (168, 118, 82, 255),     # warm brown planks (violet darks)
            "floor": (62, 130, 136, 255),    # deep teal weave
            "linen": (226, 222, 240, 255),
        },
    },
    "downstairs": {     # kitchen+lab great room: same timber, slate flags, hearth amber
        "shadow": "violet",
        "accent": (255, 176, 88, 255),
        "mats": {
            "wall": (168, 118, 82, 255),     # shared house timber
            "floor": (98, 106, 132, 255),    # cool slate flagstones
            "stone": (144, 138, 170, 255),   # hearth masonry, lavender-gray
        },
    },
    "morning_yard": {   # sun-warmed peach/coral plaster, hot magenta shingles
        "shadow": "violet",
        "accent": (238, 82, 158, 255),
        "ramps": {
            "path": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
        },
        "mats": {
            "plaster": (246, 188, 152, 255),
            "timber": (150, 88, 132, 255),
            "hedge": (44, 128, 102, 255),
            "grass2": (128, 190, 120, 255),
            "grass": (110, 186, 138, 255),
        },
    },
    "road": {           # minty teal + peach path in dawn-pink light
        "shadow": "teal",
        "accent": (255, 116, 176, 255),
        "ramps": {
            "path": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
        },
        "mats": {
            "grass": (88, 192, 138, 255),
            "grass2": (112, 196, 118, 255),
            "path": (238, 178, 138, 255),
            "hedge": (38, 112, 98, 255),
            "treeline": (30, 116, 104, 255),
            "trunk": (54, 66, 126, 255),
            "rock": (154, 146, 190, 255),
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
    "overworld": {      # hot teal sea + minty continent, hot violet wastes
        "shadow": "teal",
        "accent": (196, 120, 255, 255),         # wastes crystal violet
        # Warm earth can't be derived (see meadow) — cream->mauve hand walks:
        # sand for the coasts, a rosier packed-dirt walk for the town roads.
        "ramps": {
            "sand": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
            "road": [(240, 206, 160, 255), (228, 184, 136, 255), (212, 158, 116, 255),
                     (184, 124, 100, 255), (146, 84, 90, 255), (104, 54, 74, 255)],
        },
        # 2026-07 darker pass: the candy-mint field seeds dropped to mossy,
        # richer values (lower L, kept/raised S, same teal lean) — the law
        # holds, the kiddy read goes. Wastes stay HOT (premise color).
        "mats": {
            "sea": (34, 100, 140, 255),         # deep ocean teal
            "grass": (60, 140, 98, 255),        # mossy emerald, not candy
            "grass2": (82, 146, 84, 255),       # warmer drift green (CT two-green field)
            "forest": (36, 128, 104, 255),
            "rock": (100, 92, 144, 255),        # violet-slate cliffs
            "sand": (238, 198, 148, 255),
            "waste": (188, 112, 178, 255),
            "snow": (234, 242, 252, 255),
            "bridge": (150, 88, 112, 255),      # rosewood planks
            "trunk": (52, 62, 118, 255),        # forest understory indigo
            # Alembic Town (the CT pitched-roof cluster + the Academy):
            "roof_blue": (70, 124, 178, 255),   # deep slate-blue shingles
            "roof_green": (62, 138, 110, 255),  # deep verdigris shingles
            "plaster": (168, 158, 196, 255),    # dusky lavender walls
        },
    },
    "town": {           # Alembic Town at zone scale — the overworld palette
        "shadow": "teal",                   # walked into: mossy lanes, dusky
        "accent": (255, 190, 96, 255),      # plaster, candle amber
        # Same hand ramps + mats as the overworld so the town IS its icon up
        # close (waste/snow/bridge seeds ride along unused: the shared
        # OverWorld driver constructs every ramp it knows).
        "ramps": {
            "sand": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
            "road": [(240, 206, 160, 255), (228, 184, 136, 255), (212, 158, 116, 255),
                     (184, 124, 100, 255), (146, 84, 90, 255), (104, 54, 74, 255)],
        },
        "mats": {
            "sea": (34, 100, 140, 255),
            "grass": (60, 140, 98, 255),
            "grass2": (82, 146, 84, 255),
            "forest": (36, 128, 104, 255),      # hedge borders + garden bushes
            "rock": (100, 92, 144, 255),
            "sand": (238, 198, 148, 255),
            "waste": (188, 112, 178, 255),
            "snow": (234, 242, 252, 255),
            "bridge": (150, 88, 112, 255),
            "trunk": (52, 62, 118, 255),
            "roof_blue": (70, 124, 178, 255),
            "roof_green": (62, 138, 110, 255),
            "plaster": (168, 158, 196, 255),
        },
    },
    "meadow": {         # minty teal greens, candy hot-pink flowers
        "shadow": "teal",
        "accent": (255, 116, 176, 255),         # hot pink
        # Hand-tuned identity ramps (same precedent as the actor ramps): warm dirt cannot
        # be derived — teal shadows turn it yellow-green, violet ones salmon.
        # This one walks cream -> peach -> dusty rust -> mauve, desaturating.
        "ramps": {
            "path": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
        },
        "mats": {
            "grass": (62, 192, 142, 255),       # minty emerald, surreal-cool
            "grass2": (96, 196, 116, 255),      # warmer drift patches
            "path": (230, 176, 130, 255),
            "hedge": (34, 106, 94, 255),
            "rock": (154, 146, 190, 255),       # lavender outcrops
            "treeline": (30, 112, 110, 255),    # teal-indigo canopy mass
            "trunk": (54, 66, 126, 255),        # indigo understory
            "water": (54, 170, 192, 255),       # hot cyan pond
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

# Slime — meadow gel, teal-shadowed greens
SLIME = {
    "GELR": [(172, 240, 180, 255), (116, 210, 132, 255), (76, 170, 100, 255), (50, 130, 78, 255)],
    "OUT": (24, 62, 40, 255),
    "EYE": (24, 34, 28, 255),
    "GLINT": (235, 250, 238, 255),
}
