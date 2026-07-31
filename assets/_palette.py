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
    "hall": {           # deep plum panelling / rose floor, chalk-mint accent
        "shadow": "violet",                     # (Prologue B lecture hall)
        "accent": (150, 240, 214, 255),         # chalk mint
        "mats": {
            "wall": (118, 76, 128, 255),        # plum panelling (Room wants `wall`)
            "floor": (150, 100, 136, 255),      # dusty rose floor
        },
    },
    "sickroom": {       # the doctor's surgery (Prologue B): pale linen walls,
        "shadow": "violet",                     # cool lavender floor, a single
        "accent": (238, 214, 168, 255),         # warm lamp against the chill
        "mats": {
            "wall": (206, 198, 224, 255),       # pale lavender plaster
            "floor": (150, 158, 190, 255),      # cool slate-blue boards
        },
    },
    "library": {        # Fuji's Lanternwood library, the night of the Ebb:
        "shadow": "violet",                 # a candle-lit timber-and-plum den —
        "accent": (255, 188, 102, 255),     # firelight amber, the one warmth
        # against the cold snow-blue night in the window glass (the glass
        # ramp is hand data in the generator; glass is a light, not a mat).
        "mats": {
            "wall": (158, 104, 88, 255),    # rosewood planks (violet darks)
            "floor": (112, 72, 118, 255),   # deep plum weave
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
            # incandescence can't be derived — ramp()'s shadow law would pull
            # the darks violet-cold; molten rock walks white-gold -> orange ->
            # scorched crust by hand
            "lava": [(255, 244, 180, 255), (255, 196, 88, 255), (244, 120, 52, 255),
                     (188, 62, 48, 255), (84, 38, 54, 255), (44, 22, 40, 255)],
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
            # the five-lands biomes (2026-07): pale dusty-lavender dunes (a
            # wide L gap above basalt so the two violet lands never blur),
            # violet-charcoal volcanic crust, deep blue-spruce winter mass
            "desert": (178, 150, 208, 255),
            "basalt": (74, 62, 92, 255),
            "pines": (30, 90, 104, 255),
            # Alembic Town (the CT pitched-roof cluster + the Academy):
            "roof_blue": (70, 124, 178, 255),   # deep slate-blue shingles
            "roof_green": (62, 138, 110, 255),  # deep verdigris shingles
            "plaster": (168, 158, 196, 255),    # dusky lavender walls
        },
    },
    "overworld_bright": {   # the PRE-EBB continent: the drained overworld's
        "shadow": "teal",   # seeds lifted (higher L, kept S, same teal lean —
        "accent": (196, 120, 255, 255),     # the town_fest formula at world
        # scale). Geology stays put: desert/basalt/lava identical in both
        # eras. The WASTE pan re-seeds to ordinary dry-gold parched earth —
        # pre-Ebb there is no drained blight, just dry ground (the byte-
        # locked grid keeps the cells; the palette tells the era).
        "ramps": {
            "sand": [(250, 228, 182, 255), (242, 206, 152, 255), (230, 182, 132, 255),
                     (204, 146, 112, 255), (162, 98, 98, 255), (114, 62, 80, 255)],
            "road": [(246, 214, 166, 255), (236, 192, 142, 255), (222, 168, 122, 255),
                     (194, 134, 106, 255), (154, 92, 94, 255), (110, 58, 78, 255)],
            "lava": [(255, 244, 180, 255), (255, 196, 88, 255), (244, 120, 52, 255),
                     (188, 62, 48, 255), (84, 38, 54, 255), (44, 22, 40, 255)],
            # pre-Ebb the pans are ordinary parched earth: a hand straw->umber
            # walk (the driver derives waste with VIOLET shadows, which turns
            # any warm seed salmon-brick)
            "waste": [(232, 206, 152, 255), (216, 186, 130, 255), (196, 162, 108, 255),
                      (168, 132, 88, 255), (128, 96, 74, 255), (88, 64, 58, 255)],
        },
        "mats": {
            "sea": (48, 128, 164, 255),
            "grass": (84, 172, 108, 255),
            "grass2": (110, 178, 94, 255),
            "forest": (52, 148, 112, 255),
            "rock": (122, 114, 168, 255),
            "sand": (244, 210, 160, 255),
            "waste": (206, 172, 120, 255),      # (unused: hand ramp above wins)
            "snow": (240, 246, 255, 255),
            "bridge": (168, 102, 122, 255),
            "trunk": (66, 78, 138, 255),
            "desert": (178, 150, 208, 255),     # geology: identical both eras
            "basalt": (74, 62, 92, 255),
            "pines": (38, 104, 118, 255),       # living winter spruce, lifted
            "roof_blue": (86, 146, 198, 255),
            "roof_green": (78, 158, 124, 255),
            "plaster": (236, 210, 182, 255),
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
            # THE CANOPY TOWN'S TIMBER (2026-07-29), and it has to be hand-pinned
            # for TWO reasons, neither of them taste.
            #
            # 1. ramp() cannot make it. This scene's bias is TEAL, and a warm
            #    brown seed pulled toward teal goes GREEN at the dark end —
            #    ramp((176,120,78), "teal", 6) ends on (40,103,29), a moss
            #    stick. The module-level TIMBER derives on VIOLET instead, which
            #    is the right law for wood, but its tone 3 lands on (115,40,44):
            #    a saturated brick red, and a whole town's fascia painted in it
            #    read as MASONRY at 4x. Wood is a material, not the field — it is
            #    allowed its honest warm brown, and this is that brown written
            #    down.
            # 2. THE BOARDWALK MUST SURVIVE town_thesis's TINT_NIGHT, which
            #    multiplies by (0.42, 0.40, 0.66) — a 1.57x blue advantage over
            #    red. So every tone a body walks on is pinned with R > 1.6*B, or
            #    the whole canopy goes muddy violet on the one night the player
            #    walks home across it (the plan's R19). The field tones also sit
            #    ABOVE the night grass in luminance on purpose: the canopy is up
            #    in what light there is and the forest floor is in its shadow, so
            #    a deck darker than the ground below it reads as a hole.
            "timber": [(240, 204, 144, 255), (214, 172, 120, 255), (192, 148, 98, 255),
                       (150, 108, 76, 255), (104, 68, 66, 255), (62, 40, 56, 255)],
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
            "desert": (178, 150, 208, 255),     # ride-alongs, unused: the
            "basalt": (74, 62, 92, 255),        # shared driver constructs
            "pines": (30, 90, 104, 255),        # every ramp it knows
            "lava": (244, 120, 52, 255),
            "roof_blue": (70, 124, 178, 255),
            "roof_green": (62, 138, 110, 255),
            "plaster": (168, 158, 196, 255),
        },
    },
    "town_fest": {      # Alembic Town, FESTIVAL ERA (Prologue A) — the same
        "shadow": "teal",               # town ALIVE: spring grass, cream
        "accent": (240, 96, 170, 255),  # plaster, festival-banner magenta
        # Sunnier walk ramps than the drained town's (closer to morning_yard's
        # warmth) — the era difference must read in the ground itself.
        "ramps": {
            "sand": [(250, 228, 182, 255), (242, 206, 152, 255), (230, 182, 132, 255),
                     (204, 146, 112, 255), (162, 98, 98, 255), (114, 62, 80, 255)],
            "road": [(246, 214, 166, 255), (236, 192, 142, 255), (222, 168, 122, 255),
                     (194, 134, 106, 255), (154, 92, 94, 255), (110, 58, 78, 255)],
            # The canopy town's timber, festival era — see the drained town's
            # entry for why it is hand-pinned at all. Same warm brown, sunnier:
            # this boardwalk has had a spring morning on it and the drained one
            # has had years of nobody sweeping it.
            "timber": [(252, 224, 168, 255), (232, 194, 136, 255), (210, 168, 110, 255),
                       (168, 124, 86, 255), (118, 78, 74, 255), (74, 48, 62, 255)],
        },
        # The drained "town" seeds, lifted: higher L, kept saturation, same
        # teal lean — bright but never candy (the darker-tone law still
        # holds; this is spring, not sugar).
        "mats": {
            "sea": (48, 128, 164, 255),
            "grass": (84, 172, 108, 255),
            "grass2": (110, 178, 94, 255),
            "forest": (52, 148, 112, 255),
            "rock": (122, 114, 168, 255),
            "sand": (244, 210, 160, 255),
            "waste": (188, 112, 178, 255),
            "snow": (234, 242, 252, 255),
            "bridge": (168, 102, 122, 255),
            "trunk": (66, 78, 138, 255),
            "desert": (178, 150, 208, 255),     # ride-alongs, unused
            "basalt": (74, 62, 92, 255),
            "pines": (30, 90, 104, 255),
            "lava": (244, 120, 52, 255),
            "roof_blue": (86, 146, 198, 255),
            "roof_green": (78, 158, 124, 255),
            "plaster": (236, 210, 182, 255),
        },
    },
    "academy": {        # THE ALEMBIC ACADEMY, its own scene since 2026-07-30 —
        "shadow": "violet",                 # the same forest the town stands in,
        "accent": (168, 232, 214, 255),     # seen from a COLDER place.
        # THE PRECINCT IS ALEMBIC'S PALETTE PULLED ONE STEP TOWARD THE INSTITUTION
        # IT IS, and the two moves are deliberate:
        #
        # 1. THE SHADOW BIAS FLIPS TEAL -> VIOLET. Alembic Town is teal-shadowed:
        #    mossy, walked-in, alive. A college that has been shut since the Ebb
        #    is not, and violet darks are what the palette registry already uses
        #    for every cold place in this game (Lanternwood, the library, the
        #    hall). It costs nothing — the greens stay Alembic's greens, and only
        #    the darks move — and it does the whole job of saying you have left
        #    the village.
        # 2. THE ACCENT IS MINT, NOT CANDLE AMBER. Alembic's accent is the warm
        #    (255, 190, 96) of a lit window. Here the one thing still burning is
        #    the rose window, and DESIGN.md has always said it burns MINT on the
        #    glow. The lamps are warm and few; the magic light is cold and there
        #    is exactly one of it.
        #
        # `rock` carries this whole scene — the rampart, the towers, the keep's
        # coursed courses, the plinth — so it is seeded a full step lighter and
        # less saturated than the town's, because a mass that big at the town's
        # value comes out as one violet slab.
        "ramps": {
            "sand": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
            # THE PROCESSIONAL WAY IS FLAGSTONE, NOT A TRAIL. Seeded warm the
            # first time (Alembic's own packed-earth road, lightened) it came out
            # a huge flat pink-beige field that read as SAND with a violet castle
            # standing in it. Cool grey-violet puts the paving in the same family
            # as the walls it runs between, two full steps lighter, so the way
            # reads as the lit thing and the masonry as the mass.
            "road": [(206, 200, 214, 255), (186, 178, 198, 255), (162, 152, 178, 255),
                     (128, 118, 150, 255), (92, 82, 116, 255), (62, 52, 80, 255)],
        },
        "mats": {
            "sea": (46, 112, 158, 255),
            "grass": (66, 150, 100, 255),
            "grass2": (94, 158, 88, 255),
            "forest": (40, 128, 100, 255),
            "rock": (150, 142, 186, 255),       # THE PRECINCT'S OWN STONE
            "sand": (238, 202, 152, 255),
            "waste": (176, 100, 168, 255),      # ride-alongs, unused
            "snow": (228, 236, 250, 255),
            "bridge": (152, 106, 72, 255),
            "trunk": (58, 68, 126, 255),
            "desert": (170, 142, 200, 255),
            "basalt": (68, 56, 86, 255),
            "pines": (26, 82, 96, 255),
            "lava": (240, 116, 48, 255),
            "roof_blue": (78, 134, 188, 255),
            "roof_green": (70, 148, 116, 255),
            "plaster": (228, 202, 176, 255),
        },
    },
    "lanternwood": {    # Fuji's hometown at zone scale — RE-SEEDED 2026-07-28
        "shadow": "violet",                 # to the NARSHE read (FFVI): a dark
        "accent": (255, 190, 96, 255),      # slate-violet mining town of stacked
        # terraces, near-black spruce, and every window burning firelight amber.
        #
        # THE SNOW SPLIT IS LOAD-BEARING — read before touching either seed.
        # `snow` is now the GROUND FIELD ONLY (it seeds OverWorld.SNOW, which
        # `_px_snow` paints and which `_px_verge` borrows for the lane
        # shoulders), and it is DARK because Narshe is bright caps on dark rock,
        # never a white field. `snowcap` is the SNOW-LOAD material handed to
        # town_cabin/town_library/town_conifer/frozen_pond and to town_cliff as
        # its lip — the actual settled snow, and it stays near-white. Collapse
        # the two back into one seed and every gable, bough and cliff lip goes
        # slate with the ground: a uniformly muddy town, which is exactly the
        # "flat and kiddy" failure this pass exists to fix.
        #
        # Hand ramps: packed-snow lanes (derived road turns salmon under violet
        # shadows). The lane is dropped exactly ONE step from its old ladder and
        # no further — against a dark field the pale trodden lane IS the
        # navigation affordance and half the Narshe read.
        # `snow` and `snowcap` are BOTH hand ramps, for two different reasons:
        #  - snow, because _px_snow is written for a BRIGHT field and draws
        #    almost entirely from s[0]/s[1]. A derived ramp lightens its seed
        #    for the lit end, so no seed dark enough to give a Narshe ground
        #    survives the derivation — you have to state the top of the ladder.
        #  - snowcap, because ramp()'s violet law turns a near-white seed's
        #    darks into saturated periwinkle (the same rule that forces lava's
        #    hand ramp), and those darks are the cliff lip's turn-under shadow
        #    and every roof's shaded eave.
        "ramps": {
            "road": [(206, 216, 236, 255), (182, 192, 220, 255), (150, 158, 196, 255),
                     (114, 118, 164, 255), (80, 80, 126, 255), (56, 54, 92, 255)],
            "sand": [(206, 216, 236, 255), (182, 192, 220, 255), (150, 158, 196, 255),
                     (114, 118, 164, 255), (80, 80, 126, 255), (56, 54, 92, 255)],
            "snow": [(116, 124, 156, 255), (100, 108, 140, 255), (86, 92, 124, 255),
                     (70, 74, 106, 255), (56, 58, 88, 255), (42, 42, 68, 255)],
            "snowcap": [(255, 255, 255, 255), (236, 242, 252, 255), (208, 218, 238, 255),
                        (172, 182, 210, 255), (132, 140, 175, 255), (96, 102, 140, 255)],
        },
        "mats": {
            "sea": (60, 110, 168, 255),         # ride-along ice-water
            "grass": (150, 162, 196, 255),      # ride-along (snow is the field)
            "grass2": (140, 152, 188, 255),
            "forest": (20, 52, 66, 255),        # blue-spruce hedgerows
            "pines": (18, 48, 62, 255),         # the deep winter wood border
            "rock": (72, 72, 112, 255),         # THE town's primary value now:
                                                # the terrace faces and chasm
                                                # walls, dark slate-violet
            "snow": (104, 112, 148, 255),       # THE ground field. It must stay
                                                # well DARKER than the road ramp
                                                # below — at (150,162,196) its
                                                # fabric matched the lane's
                                                # mid-tones and the whole trail
                                                # network simply vanished.
            "snowcap": (222, 232, 248, 255),    # settled snow: roofs, boughs,
                                                # cliff lips, the pond ice
            "waste": (188, 112, 178, 255),      # ride-alongs, unused
            "bridge": (150, 88, 112, 255),
            "trunk": (56, 46, 80, 255),         # cold violet-brown boles
            "timber": (128, 92, 72, 255),       # the trestle decks + posts
            "desert": (178, 150, 208, 255),
            "basalt": (74, 62, 92, 255),
            "lava": (244, 120, 52, 255),
            "roof_blue": (72, 94, 136, 255),    # slate cabin roofs (under snow)
            "roof_green": (58, 106, 98, 255),
            "plaster": (214, 208, 228, 255),
        },
    },
    "bluff": {          # the sunset bluff over the water (Prologue B: the
        "shadow": "violet",                     # watch romance + both calls) —
        "accent": (255, 168, 112, 255),         # amber-rose hour, violet darks
        # Same hand-tuned warm walk as the meadow's (derived ramps turn warm
        # dirt salmon under violet shadows) — serves any path scuffs + the
        # driver's mandatory sand ramp.
        "ramps": {
            "road": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
            "sand": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
        },
        # Duotone cast: one gilded-grass field against one deep evening sea,
        # rose-lit cliff stone between them, dusk-violet windbreak.
        "mats": {
            "grass": (150, 128, 62, 255),       # sun-gilded dry headland
            "grass2": (174, 144, 72, 255),      # warmer crest drift
            "forest": (74, 56, 92, 255),        # dusk-violet windbreak
            "trunk": (52, 40, 84, 255),
            "rock": (164, 108, 106, 255),       # rose-lit cliff face
            "sea": (56, 64, 138, 255),          # deep evening indigo water
            "waste": (188, 112, 178, 255),      # ride-along, unused
            "snow": (234, 242, 252, 255),
            "bridge": (150, 88, 112, 255),
            "desert": (178, 150, 208, 255),     # ride-alongs, unused
            "basalt": (74, 62, 92, 255),
            "pines": (30, 90, 104, 255),
            "lava": (244, 120, 52, 255),
        },
    },
    "meadow": {         # minty teal greens, candy hot-pink flowers — the
        "shadow": "teal",                       # overworld's mossy register
        "accent": (255, 116, 176, 255),         # walked into, cooler; hot pink
        # Hand-tuned identity ramps (same precedent as the actor ramps): warm dirt cannot
        # be derived — teal shadows turn it yellow-green, violet ones salmon.
        # This walk (cream -> peach -> dusty rust -> mauve) serves the trail
        # AND the pond's wet-sand collar. Rides the shared OverWorld driver,
        # so every ramp it constructs gets a seed (waste/snow/bridge unused).
        "ramps": {
            "road": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
            "sand": [(248, 224, 178, 255), (240, 200, 148, 255), (226, 176, 128, 255),
                     (198, 138, 108, 255), (156, 92, 96, 255), (110, 58, 78, 255)],
        },
        # 2026-07 darker pass: same mint-cyan leans as the old painted seeds,
        # L pulled toward the overworld's mossy field — cooler than its
        # (60,140,98) but no longer candy.
        "mats": {
            "grass": (48, 156, 112, 255),       # minty emerald, surreal-cool
            "grass2": (76, 158, 94, 255),       # warmer drift patches
            "forest": (26, 98, 96, 255),        # teal-indigo canopy mass
            "trunk": (54, 66, 126, 255),        # indigo understory
            "rock": (122, 114, 162, 255),       # lavender outcrops (paler than
                                                # the overworld's violet-slate)
            "sea": (40, 136, 158, 255),         # cyan-forward pond (b > g)
            "waste": (188, 112, 178, 255),      # ride-along, unused
            "snow": (234, 242, 252, 255),
            "bridge": (150, 88, 112, 255),
            "desert": (178, 150, 208, 255),     # ride-alongs, unused
            "basalt": (74, 62, 92, 255),
            "pines": (30, 90, 104, 255),
            "lava": (244, 120, 52, 255),
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

# Fuji — tortoiseshell librarian cat: warm-black fur brindled with deliberate
# rust patches (placed, never dithered), cream chin/chest/paws, green-gold eyes
# behind round brass reading glasses, a deep plum scholar's robe with mustard
# trim, a clasped leather tome and a reed blow-pipe. Violet-shifted darks.
_F_FUR   = [(88, 72, 84, 255), (60, 48, 62, 255), (40, 30, 44, 255), (24, 16, 30, 255)]
_F_GING  = [(226, 140, 70, 255), (186, 104, 54, 255), (142, 72, 50, 255), (98, 46, 48, 255)]
_F_CREAM = [(250, 240, 214, 255), (226, 210, 180, 255), (192, 172, 154, 255), (152, 132, 128, 255)]
_F_ROBE  = [(146, 98, 160, 255), (112, 72, 128, 255), (82, 48, 98, 255), (56, 30, 72, 255)]
_F_TRIM  = [(232, 188, 96, 255), (198, 150, 70, 255), (158, 112, 54, 255), (116, 76, 46, 255)]
_F_RIM   = [(196, 148, 84, 255), (158, 112, 62, 255), (120, 80, 48, 255), (84, 54, 38, 255)]
_F_LENS  = [(228, 238, 244, 255), (192, 206, 220, 255), (152, 166, 188, 255), (114, 124, 152, 255)]
_F_BOOK  = [(164, 92, 74, 255), (130, 68, 58, 255), (98, 48, 48, 255), (68, 32, 40, 255)]
_F_PIPE  = [(134, 96, 66, 255), (104, 72, 52, 255), (78, 52, 42, 255), (54, 34, 32, 255)]

_OUT_FFUR  = (10, 6, 14, 255)
_OUT_FLGT  = (66, 54, 62, 255)
_OUT_FROBE = (36, 18, 50, 255)
_OUT_FBRAS = (38, 24, 16, 255)
_OUT_FBOOK = (42, 20, 24, 255)

_FUJI_OUTS = {}
for _r, _o in ((_F_FUR, _OUT_FFUR), (_F_GING, _OUT_FFUR), (_F_PIPE, _OUT_FFUR),
               (_F_CREAM, _OUT_FLGT), (_F_LENS, _OUT_FLGT),
               (_F_ROBE, _OUT_FROBE),
               (_F_TRIM, _OUT_FBRAS), (_F_RIM, _OUT_FBRAS),
               (_F_BOOK, _OUT_FBOOK)):
    for _c in _r:
        _FUJI_OUTS[_c] = _o

FUJI = {
    "FUR": _F_FUR, "GINGER": _F_GING, "CREAM": _F_CREAM, "ROBE": _F_ROBE,
    "TRIM": _F_TRIM, "RIM": _F_RIM, "LENS": _F_LENS, "BOOK": _F_BOOK,
    "PIPE": _F_PIPE,
    "EYE_G": (170, 206, 96, 255), "EYE_GL": (208, 232, 140, 255),
    "PUPIL": (16, 12, 16, 255), "GLINT": (255, 255, 250, 255),
    "NOSE": (52, 30, 34, 255), "MOUTH": (146, 108, 104, 255),
    "EARIN": (206, 122, 130, 255), "EARIN_D": (162, 88, 100, 255),
    "WHISK": (216, 214, 208, 235), "WHISKD": (150, 146, 142, 255),
    "DARTF": (232, 190, 90, 255),   # dart fletching mustard (projectile + fx)
    "OUTS": _FUJI_OUTS, "OUT_FALLBACK": _OUT_FFUR,
}

# Slime — meadow gel, teal-shadowed greens
SLIME = {
    "GELR": [(172, 240, 180, 255), (116, 210, 132, 255), (76, 170, 100, 255), (50, 130, 78, 255)],
    "OUT": (24, 62, 40, 255),
    "EYE": (24, 34, 28, 255),
    "GLINT": (235, 250, 238, 255),
}

# Big slime — the heavy. A bruise-VIOLET gel rather than a scaled-up green one,
# so "this one is tougher" reads at a glance from the colour alone (the duotone
# rule: one hue field, one hot accent) instead of only from its size. Denser and
# lower-L than SLIME across the ramp — it looks like it weighs more.
SLIME_BIG = {
    "GELR": [(196, 168, 246, 255), (150, 116, 214, 255), (108, 78, 172, 255), (72, 48, 124, 255)],
    "OUT": (34, 22, 58, 255),
    "EYE": (26, 20, 38, 255),
    "GLINT": (244, 236, 255, 255),
    "NUCR": [(126, 100, 190, 255), (96, 72, 158, 255), (70, 50, 126, 255), (48, 32, 96, 255)],
}
