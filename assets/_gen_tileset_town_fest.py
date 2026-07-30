#!/usr/bin/env python3
"""Alembic Town, FESTIVAL ERA — Prologue A's bright-era town, a thin CONFIG on
the shared overworld tile kit (the same recipe as _gen_tileset_town.py, which
paints the drained present).

Same buildings, same salts, same band stamping, same canopy — the map grid is a
byte copy of town.txt (and `_check_art.py` now enforces that rather than asking
nicely), so every lane, every ladder and every plank is recognizable when the
drained present arrives. Only the PALETTE (town_fest: spring grass, cream
plaster, sun-warmed boardwalk timber, festival magenta) and the glow differ. The
festival glow is daylight magic, not candlelight: the Academy's rose window burns
mint (magic is ALIVE here), the fountain shimmers, the lamps stay dark.

Re-run: python3 assets/_gen_tileset_town_fest.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_tiles import OverWorld, T
from _tilekit import COPPER, GLOW_WARM as WARM, GLOW_MINT as MINTG, sprite_img
from _town_props import (town_home, town_cottage, town_academy, town_well,
                         town_lamp, town_stall, town_shop, town_inn,
                         town_fountain, town_stairs, town_cliff, town_tree,
                         town_fence, bridge_fascia)
from _tree_props import (tree_edge, tree_edge_return, tree_span_edge, tree_hut,
                         tree_bridge, tree_trunk, tree_canopy, rope_ladder, understory,
                         dinghy_lift_head, dinghy_lift_car, dinghy_lift_drum)

tn = OverWorld("town_fest", "town_fest")
_blob = OverWorld.glow_blob

ROOFB = tn.mat("roof_blue")
ROOFG = tn.mat("roof_green")
ROOFR = tn.mat("bridge")               # rosewood — the inn's roof
PLAST = tn.mat("plaster")
STONE = tn.ROCK
DECK = tn.DECK
FOL = tn.FOREST

tn.paint_terrain()

# ---- the same buildings as the drained town, as 4-frame animated Tier-3 sprites ----
# THE THREE BUILDINGS UP IN THE BOUGHS ARE BOUGH HUTS, not cottages, and that is
# the note the first pass earned: plaster walls and leaf-canopy roofs on a
# boardwalk read as a raised HIGH STREET, because the silhouette is still a
# rectangular cottage. A treehouse village reads as one from its silhouette and
# nothing else — a CONE over a woven BARREL on a PORCH (see tree_hut, and the
# Slitherbough / Endor references it is drawn from). The GROUND buildings keep
# Alembic's own plaster-and-cement language on purpose: the old town on the forest
# floor, the woven canopy above it, and the two do not have to be the same town.
tn.emit_prop("Home", "hH3",
             tree_hut(DECK, FOL, DECK, tn.TRUNK, composite=True, frames=8), hframes=8)
tn.emit_prop("CottageW", "q14",
             town_cottage(ROOFG, PLAST, salt=211, composite=True, frames=4), hframes=4)
tn.emit_prop("CottageE", "w25",
             town_cottage(ROOFB, PLAST, salt=211, composite=True, frames=4), hframes=4)
tn.emit_prop("Academy", "kK6",
             town_academy(ROOFB, STONE, composite=True, frames=4,
                          open_door=True), hframes=4)
tn.emit_prop("Weapons", "xX7",
             tree_hut(DECK, FOL, DECK, tn.TRUNK, salt=483, composite=True, frames=8,
                      h=64, wares=True, sign="sword"), hframes=8)
tn.emit_prop("Items", "pP8",
             tree_hut(DECK, FOL, DECK, tn.TRUNK, salt=485, composite=True, frames=8,
                      h=64, wares=True, sign="flask"), hframes=8)
tn.emit_prop("Inn", "nN9",
             town_inn(ROOFR, PLAST, salt=261, composite=True, frames=4), hframes=4)
tn.place("S", town_stairs(STONE))
tn.bake_shadow("oO", 3)
tn.emit_prop("Fountain", "oO", town_fountain(STONE, frames=4), hframes=4)
tn.emit_prop("Well", "uU", sprite_img(town_well(STONE), 32, 32))
tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(), 16, 32), each=True)
tn.emit_prop("Stall", "m", sprite_img(town_stall(), 48, 32))
# the fences y-sort like everything a body can stand both sides of
# (2026-07-19): F = the two 3-cell gate runs, G = the 5-cell orchard run
tn.emit_prop("Fence", "F", sprite_img(town_fence(3), 48, 16), each=True)
tn.emit_prop("FenceLong", "G", sprite_img(town_fence(5), 80, 16))

# ---- the face bands, IDENTICAL stamping to the drained town ------------------------
# This used to hand-inline stamp_columns' loop for the cliff band, which meant the
# fest twin had NO RUN-HEIGHT ASSERT AT ALL: a mis-authored band would pass here
# and paint a rock wall over walkable ground, in the era where three chapters of
# cutscenes walk. Fixed 2026-07-29 by calling the shared primitive, and the proof
# it is a true refactor is that the atlas regenerates byte-identical.
cliffs = [town_cliff(tn.ROCK, tn.GRASS, salt=s) for s in (291, 293, 297)]
tn.stamp_columns("C", cliffs)
edge3 = [tree_edge(DECK, FOL, salt=s, h=48) for s in (471, 473, 477)]
edge2 = [tree_edge(DECK, FOL, salt=s, h=32) for s in (471, 473, 477)]
ret2 = (tree_edge_return(DECK, FOL, face=-1, cap=True),
        tree_edge_return(DECK, FOL, face=-1, cap=False),
        tree_edge_return(DECK, FOL, face=1, cap=True),
        tree_edge_return(DECK, FOL, face=1, cap=False))
tn.stamp_columns("vQ", edge3, salt=53, run=3, ret=ret2)
tn.stamp_columns("b", edge2, salt=57, run=2, ret=ret2)
tn.foot_shade("vQ")
tn.foot_shade("b")

# ---- the Tier-1 canopy: rope ladders and rope spans -------------------------------
tn.place_each("z", rope_ladder(DECK, cells=3))
tn.place_each("Z", rope_ladder(DECK, cells=2))
for _comp in tn.comps("W"):
    _x0, _y0, _x1, _y1 = tn.comp_bbox(_comp)
    assert _y1 - _y0 == 1, "a span is TWO rows deep (the rails live in row 2)"
    tn.bg.blit_cell(tree_bridge(DECK, cells=_x1 - _x0 + 1, salt=431 + _x0),
                    _x0 * T, _y0 * T)

# ---- the canopy's Tier-3 props ----------------------------------------------------
tn.emit_prop("GreatTrunk", "jJ", sprite_img(tree_trunk(tn.TRUNK, tn.GRASS,
                                                       cells=5), 48, 80),
             each=True)
_bough_lo, _bough_up = tree_canopy(FOL, tn.TRUNK)
tn.emit_prop("BoughBranch", "A", sprite_img(_bough_lo, 48, 48), each=True)
tn.emit_prop("BoughLeaves", "A", sprite_img(_bough_up, 48, 48), each=True,
             top=0, base_inset=-16)
tn.emit_prop("LiftHead", "M", sprite_img(dinghy_lift_head(DECK, tn.TRUNK, STONE),
                                        48, 48))
tn.emit_prop("LiftCar", "Q", dinghy_lift_car(DECK, composite=True, frames=8),
             hframes=8)
tn.emit_prop("LiftDrum", "Ii", sprite_img(dinghy_lift_drum(DECK, STONE), 48, 32))


# ---- THE UNDERSTORY: the shaded floor a canopy town stands over --------------------
# Zero new legend chars, and the rule is DERIVED rather than authored: a ground cell
# within three rows south of a fascia, a bough or a great trunk is in that thing's
# shade, so it gets forest-floor litter instead of lawn — root humps, ferns, the odd
# pale mushroom cluster, a fallen log. Without it the floor reads as a bright green
# LAWN under a treehouse village, which is the second-loudest thing wrong with the
# first pass (the first was the buildings).
#
# Each piece is opaque and carries its own duff base keyed to THIS scene's grass ramp,
# so the cells dedupe whatever the fabric phase beneath them is doing and the whole
# understory costs a handful of atlas tiles. Blitted per CELL rather than per
# component: place_each would need one char per kind, and the point is that this
# needs no chars at all.
# The litter's WOOD is the deck ramp's DARK HALF, not the ramp itself: handed the
# whole thing, the root humps came out in the boardwalk's pale honey and read as
# scattered straw or dropped twigs lying on a lawn. Wet wood on a forest floor is
# the darkest thing in frame. (The scene's own `trunk` seed is no use here — it is
# a teal-violet, which is right for a standing tree read against the sky and wrong
# for something lying in the duff.)
_ROT = [DECK[2], DECK[3], DECK[3], DECK[4], DECK[4], DECK[5]]
# FERNS carry it, because a clump of fronds is the one understory shape that reads
# at 16px. Mushrooms are the floor's single pale accent and the kit says keep them
# rare — one slot in seven — and a log stub is the rare big thing.
_UNDER = [understory(FOL, _ROT, tn.GRASS, kind=k, salt=461 + i)
          for i, k in enumerate(("fern", "fern", "fern", "roots", "fern",
                                 "log", "shroom"))]
for _y in range(tn.m.rows_n):
    for _x in range(tn.m.cols):
        if tn.m.at(_x, _y) not in ".,":
            continue
        if not any(tn.m.at(_x, _y - _d) in "bvQaj" for _d in (1, 2, 3)):
            continue
        # ONE CELL IN THREE. The floor has to stay mostly open: litter on every
        # shaded cell is not a forest floor, it is a rug — and the shade band from
        # foot_shade is already doing half this job.
        if h2(_x, _y, 467) % 3:
            continue
        tn.bg.blit_cell(_UNDER[h2(_x, _y, 463) % len(_UNDER)], _x * T, _y * T)


# ---- walk-behind trees (identical stamping) ----------------------------------------
lo, up = town_tree(tn.FOREST, tn.TRUNK, tn.GRASS)
tn.emit_prop("TreeTrunk", "Tt^", sprite_img(lo, 32, 48), each=True)
tn.emit_prop("TreeCrown", "Tt^", sprite_img(up, 32, 48), each=True,
             top=0, base_inset=-16)


# ---- festival glow: living magic by daylight -----------------------------------------
def _glow(img):
    kx, ky = tn.bbox("K")[0] * T, tn.bbox("K")[1] * T
    _blob(img, kx + 79, ky + 14, 18, MINTG, 66)            # the rose window AWAKE
    _blob(img, kx + 40, ky + 20, 8, MINTG, 40)             # ward-light in a hall window
    _blob(img, kx + 120, ky + 20, 8, MINTG, 40)
    _blob(img, kx + 79, ky + 37, 11, WARM, 46)             # the OPEN door's warm mouth
    ox_, oy_ = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox_ + 24, oy_ + 24, 13, MINTG, 52)          # the fountain's charm shimmer
    # the canopy huts, derived from the footprint (see the drained town's glow)
    for _chars in ("H", "X", "P"):
        _x0, _y0, _x1, _y1 = tn.bbox(_chars)
        _cx = (_x0 + _x1 + 1) * T // 2
        _base = (_y1 + 1) * T
        _blob(img, _cx, _base - 8, 11, WARM, 46)           # a hut's open doorway
        _blob(img, _cx - 46, _base - 44, 6, WARM, 34)      # its hanging lantern
    # the clip pass — see the drained town's generator: LIGHT DOES NOT SPILL DOWN
    # A FACE, and the glow overlay renders UNDER the y-sorted World, so a wash
    # across a fascia lands on the boardwalk's own underside.
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in "bvQaj":
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))


tn.write_glow(_glow)

# ---- the SPANS' upper-layer fascias (see the drained town's generator) -------------
_span_edge = tree_span_edge(DECK)
for _y in range(tn.m.rows_n):
    for _x in range(tn.m.cols):
        if tn.m.at(_x, _y) == "e":
            tn.bg.blit_cell(_span_edge, _x * T, _y * T)
            tn.upper_cell(_x, _y, _span_edge)
        elif tn.m.at(_x, _y) == "r" and tn.m.at(_x, _y - 1) == "W":
            tn.upper_cell(_x, _y, _span_edge)

# ---- DEPTH MASKS (2026-07-28) -------------------------------------------------------
# Must come after every lower-canvas write, because the band copies FINISHED art.
# And on "v", never "vQ": the unmasked gap at the lift shaft IS the lift gate.
tn.mask_band("C")
tn.mask_band("b")
tn.mask_band("v")
for _comp in tn.comps("="):
    _bx0, _by0, _bx1, _by1 = tn.comp_bbox(_comp)
    for _bx in range(_bx0, _bx1 + 1):
        if tn.m.at(_bx, _by1 + 1) == "r":
            tn.upper_cell(_bx, _by1 + 1, bridge_fascia(tn.BRIDGE))

# ---- THE ASSERT BLOCK — identical to the drained town's, and that is the point ------
tn.assert_strata()
tn.assert_band_orientation("vQ", "canopy", "ground")
tn.assert_band_orientation("b", "canopy", "ground")
tn.assert_span()
tn.assert_stair("S", "C", 2)
tn.assert_stair("z", "v", 3)
tn.assert_stair("Z", "b", 2)
tn.assert_lift("M", "Q", "I", "i")
tn.assert_door_approach(rows=2)
tn.assert_npc_room()
for _chars, _w, _h in (("jJ", 3, 5), ("A", 3, 3), ("Tt^", 2, 3)):
    for _c in tn.comps(_chars):
        _a, _b, _c2, _d = tn.comp_bbox(_c)
        assert (_c2 - _a + 1, _d - _b + 1, len(_c)) == (_w, _h, _w * _h), (
            f"town_fest.txt: the {_chars!r} component at ({_a},{_b}) is not a "
            f"clean {_w}x{_h} block")
tn.assert_reachable("exit_south", "home", "festival")

tn.finish()
