#!/usr/bin/env python3
"""Alembic Town, walkable — a thin CONFIG on the shared overworld tile kit.

The town map (assets/maps/town.txt, 56x34) rides assets/_overworld_tiles.py's
OverWorld driver directly: the tree border is the forest class, lanes are the
wobbly trail painter, yards are the fence class, the SE pond is sea+beach and
the stream a river with one bridge cell. This file picks the palette,
emit_prop()s the zone-scale facades and trees from assets/_town_props.py as
single Tier-3 y-sorted World sprites, stamps every authored FACE BAND from
salted repeating variants, and writes the additive night-glow.

SINCE 2026-07-29 IT IS A TWO-STRATA CANOPY TOWN, and the whole elevation
"system" is three things: the `stratum:` legend token, the assert block at the
bottom of this file, and the discipline of calling them. There is no per-cell
level field, no second collision layer and no level-aware AI — a storey is a
flat walkable region of the SAME grid, disjoint from the others, joined to them
by a band of solid cells wearing opaque face art (assets/_tree_props.tree_edge)
and pierced by rope ladders. See the map txt's header for why that works and
what it forbids.

ORDER MATTERS HERE, top to bottom:
  paint_terrain -> the Tier-3 buildings and furniture -> stamp_columns for every
  face band -> the Tier-1 ladders and spans -> the canopy props -> the spans'
  upper-layer fascias -> write_glow -> mask_band LAST (it copies FINISHED lower
  art) -> the asserts -> finish.

Re-run: python3 assets/_gen_tileset_town.py [--preview out.png]
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

tn = OverWorld("town", "town")
_blob = OverWorld.glow_blob            # shared radial glow dab (see TileScene)

ROOFB = tn.mat("roof_blue")
ROOFG = tn.mat("roof_green")
ROOFR = tn.mat("bridge")               # rosewood — the inn's roof
PLAST = tn.mat("plaster")
STONE = tn.ROCK                        # town masonry = the scene's violet slate
DECK = tn.DECK                         # the boardwalk's hand-pinned timber
FOL = tn.FOREST                        # the canopy's leaf

tn.paint_terrain()

# ---- the buildings, each a single Tier-3 y-sorted World sprite ----------------------
# Native y-sort sorts the whole building against a body at the front-wall
# baseline, which retires the upper-layer roof + ridge-cap + _eave_lift mask band
# this scene used to need. The char triples stay (solid facade + WALKABLE roof
# corridor + solid ridge digit) purely for collision + the footprint bbox.
# Every building is a 4-frame sheet (animated water + chimney smoke), cycled by
# scene/alembic_town.gd the way downstairs cycles its boiler.
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
             town_academy(ROOFB, STONE, composite=True, frames=4), hframes=4)
tn.emit_prop("Weapons", "xX7",
             tree_hut(DECK, FOL, DECK, tn.TRUNK, salt=483, composite=True, frames=8,
                      h=64, wares=True, sign="sword"), hframes=8)
tn.emit_prop("Items", "pP8",
             tree_hut(DECK, FOL, DECK, tn.TRUNK, salt=485, composite=True, frames=8,
                      h=64, wares=True, sign="flask"), hframes=8)
tn.emit_prop("Inn", "nN9",
             town_inn(ROOFR, PLAST, salt=261, composite=True, frames=4), hframes=4)
tn.place("S", town_stairs(STONE))
# street furniture is Tier 3: free-standing (bodies pass both north and
# south of it), so the art rides y-sorted World entities spawned from
# town_props.txt (scene/prop_spawner.gd); the map chars keep the solid
# collision and anchor the glow dabs
tn.bake_shadow("oO", 3)
tn.emit_prop("Fountain", "oO", town_fountain(STONE, frames=4), hframes=4)
tn.emit_prop("Well", "uU", sprite_img(town_well(STONE), 32, 32))
tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(), 16, 32), each=True)
tn.emit_prop("Stall", "m", sprite_img(town_stall(), 48, 32))
# the fences y-sort like everything a body can stand both sides of
# (2026-07-19): F = the two 3-cell gate runs, G = the 5-cell orchard run
tn.emit_prop("Fence", "F", sprite_img(town_fence(3), 48, 16), each=True)
tn.emit_prop("FenceLong", "G", sprite_img(town_fence(5), 80, 16))

# ---- THE FACE BANDS: one 16 x T*run opaque column per vertical run, hash-picked
# from three salted variants (the meadow-boulder per-cell pattern — opaque,
# unoutlined, so a whole band dedupes to a handful of tiles). The Academy's stone
# terrace and the canopy's timber fascias are the SAME idiom on the same
# primitive, which is the point: verticality here is authoring. ---------------------
cliffs = [town_cliff(tn.ROCK, tn.GRASS, salt=s) for s in (291, 293, 297)]
tn.stamp_columns("C", cliffs)
# `vQ` in one call: Q is a PAINT TWIN of v, so the band runs unbroken across the
# lift shaft and the boat hangs in front of finished fascia art rather than raw
# fabric. mask_band below is called on "v" ONLY — never "vQ".
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
# place_each, never place: two ladders sharing a char would make place() blit one
# sprite across their combined bbox, i.e. across the whole town.
tn.place_each("z", rope_ladder(DECK, cells=3))
tn.place_each("Z", rope_ladder(DECK, cells=2))
# The spans are blitted PER COMPONENT rather than by place_each, because they are
# deliberately different lengths — 4 cells over the west bough mass and 4 over
# the creek today, but the point is that a span's length is a map decision and
# place_each would silently stretch one sprite across both.
for _comp in tn.comps("W"):
    _x0, _y0, _x1, _y1 = tn.comp_bbox(_comp)
    assert _y1 - _y0 == 1, "a span is TWO rows deep (the rails live in row 2)"
    tn.bg.blit_cell(tree_bridge(DECK, cells=_x1 - _x0 + 1, salt=431 + _x0),
                    _x0 * T, _y0 * T)

# ---- the canopy's Tier-3 props ----------------------------------------------------
# THE GREAT TREE: one unsplit sprite bottom-anchored at the footprint's south
# edge. y-sort at the foot already draws the shaft OVER a body standing north of
# it (walk-behind, on the decked J crown) and UNDER one standing south, which is
# every case a trunk has.
tn.emit_prop("GreatTrunk", "jJ", sprite_img(tree_trunk(tn.TRUNK, tn.GRASS,
                                                       cells=5), 48, 80),
             each=True)
# the lookout's bough mass, as the town_conifer split pair: the leaves ride their
# own sprite whose y-sort baseline is pushed a tile SOUTH so it beats a body
# standing among them.
_bough_lo, _bough_up = tree_canopy(FOL, tn.TRUNK)
tn.emit_prop("BoughBranch", "A", sprite_img(_bough_lo, 48, 48), each=True)
tn.emit_prop("BoughLeaves", "A", sprite_img(_bough_up, 48, 48), each=True,
             top=0, base_inset=-16)
# THE DINGHY LIFT, three pieces down one column. The car is an 8-frame sheet: it
# swings a pixel either way on a symmetric zero-mean cycle (so the sway can never
# read as travel) while its bow lantern breathes.
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


# ---- walk-behind trees: TWO y-sorted World props per {^,T,t} component ------------
# The opaque TRUNK sprite sorts at the footprint's south edge; the CROWN sprite's
# y-sort baseline is pushed ~1 tile SOUTH (base_inset=-16) so the canopy
# overhangs — a body beside the trunk tucks behind it, a body a tile south walks
# out in front.
lo, up = town_tree(tn.FOREST, tn.TRUNK, tn.GRASS)
tn.emit_prop("TreeTrunk", "Tt^", sprite_img(lo, 32, 48), each=True)
tn.emit_prop("TreeCrown", "Tt^", sprite_img(up, 32, 48), each=True,
             top=0, base_inset=-16)


# ---- additive glow: the sleeping town's little lights ------------------------------
def _glow(img):
    # THE THREE CANOPY HUTS. Their dabs are derived from the FOOTPRINT rather than
    # hand-offset into a facade, because tree_hut's art is taller than the rows it
    # declares (see `rise`) — an offset measured down from the bbox top would miss
    # the window by however much the roof happens to stand up. Measured UP from the
    # footprint's south edge it lands on the door, the hearth window and the
    # hanging lantern whatever the cone does.
    for _chars in ("H", "X", "P"):
        _x0, _y0, _x1, _y1 = tn.bbox(_chars)
        _cx = (_x0 + _x1 + 1) * T // 2
        _base = (_y1 + 1) * T
        _blob(img, _cx, _base - 8, 13, WARM, 64)           # the doorway
        _blob(img, _cx - 24, _base - 30, 9, WARM, 54)      # the hearth window
        _blob(img, _cx - 46, _base - 44, 7, WARM, 44)      # the hanging lantern
    kx, ky = tn.bbox("K")[0] * T, tn.bbox("K")[1] * T
    _blob(img, kx + 79, ky + 14, 16, MINTG, 46)            # the rose window
    nx, ny = tn.bbox("N")[0] * T, tn.bbox("N")[1] * T      # the inn, wide awake
    for wx_ in (20, 50, 122):                              # upper windows
        _blob(img, nx + wx_, ny + 10, 8, WARM, 50)
    for wx_ in (30, 110):                                  # lower windows
        _blob(img, nx + wx_, ny + 33, 9, WARM, 54)
    _blob(img, nx + 72, ny + 23, 7, WARM, 46)              # the transom
    _blob(img, nx + 56, ny + 31, 6, WARM, 44)              # the wall lantern
    ox_, oy_ = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox_ + 24, oy_ + 29, 10, MINTG, 40)          # fountain shimmer
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            # each lamp component's TOP cell (usually the walkable L head)
            if m.at(x, y) in "lL" and m.at(x, y - 1) not in "lL":
                _blob(img, x * T + 7, y * T + 4, 11, MINTG, 58)
    # the lift car's bow lantern — the only warm thing in the shaft
    qx, qy = tn.bbox("Q")[0] * T, tn.bbox("Q")[1] * T
    # THE CLIP PASS, and it is not optional. Lanternwood's lesson: LIGHT DOES NOT
    # SPILL DOWN A ROCK FACE. The glow overlay renders UNDER the y-sorted World,
    # so a hut lantern's wash bleeding across the fascia below it lands on the
    # boardwalk's own underside and destroys the whole terrace read — the storeys
    # stop looking stacked and start looking painted. Every face band, bough and
    # trunk is wiped, and the car's dab is laid AFTERWARDS because the shaft is
    # exactly the place a light IS meant to be.
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in "bvQaj":
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))
    _blob(img, qx + 24, qy + 30, 7, WARM, 54)


tn.write_glow(_glow)

# ---- the SPANS' upper-layer fascias -----------------------------------------------
# A span's south row is a ONE-row solid strip between two walkable rows, which the
# z-order doctrine forbids banding outright (the corridor feet and the south head
# want the same 12px and one of them always wears it). So it gets AUTHORED art on
# the upper layer instead — the shipped bridge_fascia idiom — laid on the lower
# canvas too so the cell never shows raw fabric, at the same coordinates so the
# two copies can never seam. Over the creek it is upper-ONLY: _lower_frames
# repaints river cells per frame and asserts frame 0 is byte-identical.
_span_edge = tree_span_edge(DECK)
for _y in range(tn.m.rows_n):
    for _x in range(tn.m.cols):
        if tn.m.at(_x, _y) == "e":
            tn.bg.blit_cell(_span_edge, _x * T, _y * T)
            tn.upper_cell(_x, _y, _span_edge)
        elif tn.m.at(_x, _y) == "r" and tn.m.at(_x, _y - 1) == "W":
            tn.upper_cell(_x, _y, _span_edge)      # the creek under the hero span

# ---- DEPTH MASKS (2026-07-28) -------------------------------------------------------
# A body's collision box hugs its FEET, so pressed south into any solid cell ~11px
# of sprite hangs past the physics boundary and draws over whatever is below —
# "the player stands off the edge of the cliff". The face's own top 12px,
# re-emitted as a Tier-3 Y-SORTED strip keyed at run_top-8, swallow exactly that
# sliver. MUST come after every lower-canvas write, because the band copies
# FINISHED art. And on "v", never "vQ": the 3-cell unmasked gap at the lift shaft
# IS the gate you step through onto the boat.
tn.mask_band("C")
tn.mask_band("b")
tn.mask_band("v")
# The same bug at the stream: standing on the footbridge's south end, a body sinks
# into the water cell below. That cell ANIMATES on four frames, so a mirrored
# band would freeze its top half — paint a static near-rail instead.
for _comp in tn.comps("="):
    _bx0, _by0, _bx1, _by1 = tn.comp_bbox(_comp)
    for _bx in range(_bx0, _bx1 + 1):
        if tn.m.at(_bx, _by1 + 1) == "r":
            tn.upper_cell(_bx, _by1 + 1, bridge_fascia(tn.BRIDGE))

# ---- THE ASSERT BLOCK — the elevation "system" -------------------------------------
# Every failure this catches is SILENT otherwise: it renders, it dedupes, every
# lint in _check_art.py passes it, and it ships.
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
# The component asserts the kit demands, and the reason is the 2026-07-29 spruce
# lesson: two of these authored edge-to-edge FUSE into one component, one bbox and
# one badly stretched sprite, and nothing else complains.
for _chars, _w, _h in (("jJ", 3, 5), ("A", 3, 3), ("Tt^", 2, 3)):
    for _c in tn.comps(_chars):
        _a, _b, _c2, _d = tn.comp_bbox(_c)
        assert (_c2 - _a + 1, _d - _b + 1, len(_c)) == (_w, _h, _w * _h), (
            f"town.txt: the {_chars!r} component at ({_a},{_b}) is not a clean "
            f"{_w}x{_h} block")
for _c in tn.comps("jJ"):                  # exactly the bottom 3 rows solid
    _a, _b, _c2, _d = tn.comp_bbox(_c)
    for _y in range(_b, _d + 1):
        _want = _y >= _d - 2
        for _x in range(_a, _c2 + 1):
            assert tn.m.legend[tn.m.at(_x, _y)]["solid"] == _want, (
                f"town.txt: the great trunk at ({_a},{_b}) must be walkable crown "
                f"over exactly 3 solid rows of trunk")
# assert_reachable LAST, and with BOTH arrivals: this town has two storeys and
# the player can enter it at the south gate or on Basil's own doorstep.
tn.assert_reachable("exit_south", "home")

tn.finish()
