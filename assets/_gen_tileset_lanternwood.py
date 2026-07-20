#!/usr/bin/env python3
"""LANTERNWOOD — Fuji's snowy pine-forest hometown at zone scale, a thin
CONFIG on the shared OverWorld driver (assets/maps/lanternwood.txt).

The winter cabin kit lives in assets/_town_props.py: log-walled cabins under
deep snow gable roofs, every window fire-lit and FLICKERING (the 4-frame
sheets' `windows` recolor), snow-capped stone chimneys breathing lazy grey
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
from _town_props import town_cabin, town_conifer, town_lamp, frozen_pond, WARM as WARMC

tn = OverWorld("lanternwood", "lanternwood")
tn.road_verge = "snow"
_blob = OverWorld.glow_blob

ROOFB = tn.mat("roof_blue")
ROOFG = tn.mat("roof_green")

tn.paint_terrain()

# ---- the cabins: five 4-frame Tier-3 sheets (flicker + woodsmoke) --------------------
tn.bake_shadow("kK", 3)
tn.emit_prop("Library", "kK", town_cabin(ROOFB, tn.SNOW, salt=341, wide=True),
             hframes=4)
tn.bake_shadow("qQ", 3)
tn.emit_prop("FujiHome", "qQ", town_cabin(ROOFG, tn.SNOW, salt=311), hframes=4)
tn.bake_shadow("wW", 3)
tn.emit_prop("CabinA", "wW", town_cabin(ROOFB, tn.SNOW, salt=313), hframes=4)
tn.bake_shadow("eE", 3)
tn.emit_prop("CabinB", "eE", town_cabin(ROOFG, tn.SNOW, salt=317), hframes=4)
tn.bake_shadow("zZ", 3)
tn.emit_prop("CabinC", "zZ", town_cabin(ROOFB, tn.SNOW, salt=331), hframes=4)

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
    for ch in ("kK", "qQ", "wW", "eE", "zZ"):              # every doorway +
        x0, y0, x1, y1 = tn.bbox(ch)                       # window burns warm
        cx = (x0 + x1 + 1) * T // 2
        by = (y1 + 1) * T
        _blob(img, cx, by - 6, 5, WARM, 46)                # the door spill
        _blob(img, cx - (x1 - x0) * 6, by - 12, 4, WARM, 40)   # west window
        _blob(img, cx + (x1 - x0) * 6, by - 12, 4, WARM, 40)   # east window
    for comp in tn.comps("lL"):                            # the lamps
        x0, y0, x1, y1 = tn.comp_bbox(comp)
        _blob(img, x0 * T + 8, y0 * T + 4, 6, WARM, 54)
    ox0, oy0, _, _ = tn.bbox("o")                          # a cold moon-glint
    _blob(img, ox0 * T + 30, oy0 * T + 20, 8, (150, 190, 246), 22)


tn.write_glow(_glow)
tn.finish()
