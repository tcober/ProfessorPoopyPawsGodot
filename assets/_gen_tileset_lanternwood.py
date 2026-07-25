#!/usr/bin/env python3
"""LANTERNWOOD — Fuji's snowy pine-forest hometown at zone scale, a thin
CONFIG on the shared OverWorld driver (assets/maps/lanternwood.txt).

The winter cabin kit lives in assets/_town_props.py: log-walled cabins under
deep snow gable roofs, every window fire-lit and softly PULSING (the 8-frame
sheets' `windows` breath), snow-capped stone chimneys breathing lazy grey
WOODSMOKE (`wood_flues`, pad=18 — deliberately not Alembic's copper-flue
steam), snow-laden spruces as ConiferTrunk/ConiferCrown T3 pairs, warm-
mantled lamps, and the frozen skating pond baked Tier-1 over walkable pond
cells. Lanes render with road_verge="snow".

Re-run: python3 assets/_gen_tileset_lanternwood.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _overworld_tiles import OverWorld, T
from _tilekit import GLOW_WARM as WARM, sprite_img
from _town_props import (town_cabin, town_library, town_conifer, town_lamp,
                         frozen_pond, WARM as WARMC)

tn = OverWorld("lanternwood", "lanternwood")
tn.road_verge = "snow"
_blob = OverWorld.glow_blob

ROOFB = tn.mat("roof_blue")
ROOFG = tn.mat("roof_green")

tn.paint_terrain()

# ---- the library + four cabins: 8-frame Tier-3 sheets (breath + woodsmoke) -----------
# hframes MUST match the builders' `frames` (8 — one slow hearth pulse per sheet).
tn.bake_shadow("kK", 3)
tn.emit_prop("Library", "kK", town_library(ROOFB, tn.SNOW, salt=341), hframes=8)
tn.bake_shadow("qQ", 3)
tn.emit_prop("FujiHome", "qQ", town_cabin(ROOFG, tn.SNOW, salt=311), hframes=8)
tn.bake_shadow("wW", 3)
tn.emit_prop("CabinA", "wW", town_cabin(ROOFB, tn.SNOW, salt=313), hframes=8)
tn.bake_shadow("eE", 3)
tn.emit_prop("CabinB", "eE", town_cabin(ROOFG, tn.SNOW, salt=317), hframes=8)
tn.bake_shadow("zZ", 3)
tn.emit_prop("CabinC", "zZ", town_cabin(ROOFB, tn.SNOW, salt=331), hframes=8)

# ---- spruces, lamps, the pond --------------------------------------------------------
lo, up = town_conifer(tn.PINES, tn.TRUNK, tn.SNOW)
tn.emit_prop("ConiferTrunk", "Yy", sprite_img(lo, 32, 64), each=True)
tn.emit_prop("ConiferCrown", "Yy", sprite_img(up, 32, 64), each=True,
             top=0, base_inset=-16)
tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(mantle=WARMC), 16, 32),
             each=True)
tn.place("o", frozen_pond(tn.SNOW))                        # baked Tier-1 ice


# ---- additive glow: the town of lanterns ---------------------------------------------
def _glow(img):
    for ch in ("qQ", "wW", "eE", "zZ"):                    # every doorway +
        x0, y0, x1, y1 = tn.bbox(ch)                       # window burns warm
        cx = (x0 + x1 + 1) * T // 2
        by = (y1 + 1) * T
        _blob(img, cx, by - 6, 5, WARM, 46)                # the door spill
        _blob(img, cx - (x1 - x0) * 6, by - 12, 4, WARM, 40)   # west window
        _blob(img, cx + (x1 - x0) * 6, by - 12, 4, WARM, 40)   # east window
    # The library burns on a different scale — but the overlay renders UNDER
    # the y-sorted World, so a blob at window height is simply hidden behind
    # the building. Its light has to land where it can be SEEN: on the snow at
    # its feet. Keyed off the footprint's own corner so it travels with it.
    lx0, _ly0, lx1, ly1 = tn.bbox("kK")
    ax, by = lx0 * T, (ly1 + 1) * T                        # art x0, ground line
    # one CONTINUOUS wash the length of the frontage (overlapping dabs, not
    # one per aperture — spaced dabs scallop the snow into circles), with the
    # doorway pooling brightest on the forecourt
    for dx in range(8, 137, 10):
        _blob(img, ax + dx, by + 2, 15, WARM, 34)
    _blob(img, ax + 72, by + 9, 27, WARM, 78)
    _blob(img, ax + 72, by + 3, 15, WARM, 54)
    for comp in tn.comps("lL"):                            # the lamps
        x0, y0, x1, y1 = tn.comp_bbox(comp)
        _blob(img, x0 * T + 8, y0 * T + 4, 6, WARM, 54)
    ox0, oy0, _, _ = tn.bbox("o")                          # a cold moon-glint
    _blob(img, ox0 * T + 30, oy0 * T + 20, 8, (150, 190, 246), 22)


tn.write_glow(_glow)
tn.finish()
