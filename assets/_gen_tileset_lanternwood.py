#!/usr/bin/env python3
"""LANTERNWOOD — Fuji's hometown at zone scale, a thin CONFIG on the shared
OverWorld driver (assets/maps/lanternwood.txt).

REBUILT 2026-07-28 to the NARSHE read (FFVI): a dark slate-violet mining town
of STACKED TERRACES rather than a flat white snow field. Three things carry it,
and all three are cheap because none of them is an engine feature:

  1. THE PALETTE. `mats["snow"]` is now dark — it is the ground field only —
     while a separate `mats["snowcap"]` stays near-white and is what every
     builder here gets handed as its snow-load material. Bright caps on dark
     rock. Collapse those two seeds back together and the whole town goes
     muddy; see the long note in _palette.py.
  2. THE TERRACE KIT (TileScene.stamp_columns / foot_shade / assert_reachable).
     A terrace is two flat walkable regions separated by a band of solid cells
     wearing opaque authored face art, pierced by a walkable stair gap. Alembic's
     Academy terrace proved the idiom; this is the second user and the reason it
     moved into the kit.
  3. THE RINK. The east flank of LEVEL 3 carries the town's skating rink —
     frozen_pond at 8x4 and `skated`, flanked by two lamps. It replaced a
     chasm-and-trestle that never read as a chasm; see lanternwood.txt.

THE HARBOUR AND THE MOOT HALL (2026-07-29) add a fourth thing, and it is the
first WATER this town has ever shown — which was overdue for a town whose only
way off its island is a boat. The east end of LEVEL 1 is a cove: an opaque
Tier-1 town_dock pier over walkable `dock` cells (render class `bridge`, so no
coastline forms under it), the town's steam launch as an 8-frame Tier-3 prop on
`berth` cells (render class `sea`, so the hull floats on animated water rather
than on painted planks), and town_moot_hall on a cabin's 5x4 footprint beside
them. Two shoreline treatments were already written and are simply used here:
_lip_band's "snow" pair, which is an ICE SHELF, and the sea's own depth banding.
See the long note in lanternwood.txt for why each class was chosen.

The winter cabin kit is unchanged: log-walled cabins under deep snow gable
roofs, every window fire-lit and softly PULSING (the 8-frame sheets' `windows`
breath — the "glowing windows" were always there, they just had a white field
to compete with), snow-capped stone chimneys breathing lazy grey WOODSMOKE
(`wood_flues`, deliberately not Alembic's copper-flue steam), snow-laden
spruces as ConiferTrunk/ConiferCrown T3 pairs, warm-mantled lamps, and the
frozen skating pond baked Tier-1 over walkable pond cells. Lanes render with
road_verge="snow".

Re-run: python3 assets/_gen_tileset_lanternwood.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _overworld_tiles import OverWorld, T
from _tilekit import GLOW_WARM as WARM, sprite_img
from _town_props import (town_cabin, town_library, town_conifer, town_lamp,
                         town_conifer_big, town_cliff, town_cliff_return,
                         town_stairs,
                         town_gatepost, frozen_pond,
                         town_moot_hall, town_dock, town_launch,
                         WARM as WARMC)

tn = OverWorld("lanternwood", "lanternwood")
tn.road_verge = "snow"
_blob = OverWorld.glow_blob

ROOFB = tn.mat("roof_blue")
ROOFG = tn.mat("roof_green")
# SNOWCAP is SETTLED snow (roofs, boughs, cliff lips, pond rim). tn.SNOW is the
# dark ground field. Handing tn.SNOW to a builder is the single easiest way to
# undo this whole pass — every gable and bough would go slate with the ground.
SNOWCAP = tn.mat("snowcap")
TIMBER = tn.mat("timber")

tn.paint_terrain()

# ---- THE TERRACES: four bands at THREE HEIGHTS. One opaque
# 16x(16*n) face column per map column, hash-picked from three salted variants.
#
# The height VARIETY is the point, and it is what the first draft of this map
# got wrong: two uniform 2-row bands read as one cliff drawn twice, not as a
# town stacked up a mountainside. C=2 rows (a step), X=3 (a drop), B=4 (the big
# back wall). The bands also staircase across the map — see lanternwood.txt —
# which costs nothing here because stamp_columns works per column run.
#
# stamp_columns asserts every run matches its declared height: a short run would
# paint a rock wall over the WALKABLE cell below, and nothing lints that. -----------
# FIVE salted variants per height, not three: strata rows are per-sprite, so
# they align wherever the same variant lands twice in a row, and with only three
# in the bag a long band prints a visible repeat.
for ch, rows, salts in (("C", 2, (291, 293, 297, 373, 379)),
                        ("X", 3, (301, 303, 307, 383, 389)),
                        ("B", 4, (311, 313, 317, 397, 401))):
    # wall=True: a cast cement/cinderblock wall under a snow-broken coping,
    # not an eroded rock face. Alembic does NOT pass the flag and stays
    # byte-identical — there the terrace sits on pale grass and the eroded read
    # is right. Here it sat on a dark snow field where a rambling bright lip is
    # indistinguishable from a snowdrift and dashed strata read as railings.
    # See town_cliff, which carries the three passes this took.
    # ret=: the corner at every staircase step, without which the higher run's
    # face stops at a straight cut against open snow and the band reads as two
    # unrelated walls. See town_cliff_return.
    tn.stamp_columns(ch, [town_cliff(tn.ROCK, SNOWCAP, salt=s, h=16 * rows,
                                     wall=True)
                          for s in salts], run=rows,
                     ret=tuple(town_cliff_return(tn.ROCK, SNOWCAP,
                                                 salt=salts[0], face=f,
                                                 w=6, cap=c)
                               for f in (-1, 1) for c in (True, False)))
    tn.foot_shade(ch)
# NOTE the RIFT is gone (2026-07-29) — see the note in lanternwood.txt. A 2-row
# band of dark in flat top-down is a wall no matter which way its ramp runs, and
# the trestle over it read as a wooden panel set into one. town_cliff(void=) and
# town_trestle stay in the kit; no map uses them.

# ---- the crossings: a stair per band height ----------------------------------------
# place_each, not place: two stairs share a char, and place() would blit one
# sprite across their combined bbox — i.e. across the whole town.
for ch, rows in (("S", 2), ("s", 3), ("T", 4)):
    tn.place_each(ch, town_stairs(tn.ROCK, cheek=SNOWCAP, cells=rows))

# ---- the library + four cabins: 8-frame Tier-3 sheets (breath + woodsmoke) ----------
# hframes MUST match the builders' `frames` (8 — one slow hearth pulse per sheet).
tn.bake_shadow("kK", 3)
tn.emit_prop("Library", "kK", town_library(ROOFB, SNOWCAP, salt=341), hframes=8)
tn.bake_shadow("qQ", 3)
tn.emit_prop("FujiHome", "qQ", town_cabin(ROOFG, SNOWCAP, salt=311), hframes=8)
tn.bake_shadow("wW", 3)
tn.emit_prop("CabinA", "wW", town_cabin(ROOFB, SNOWCAP, salt=313), hframes=8)
tn.bake_shadow("eE", 3)
tn.emit_prop("CabinB", "eE", town_cabin(ROOFG, SNOWCAP, salt=317), hframes=8)
tn.bake_shadow("zZ", 3)
tn.emit_prop("CabinC", "zZ", town_cabin(ROOFB, SNOWCAP, salt=331), hframes=8)
# THE MOOT HALL — the council hall on LEVEL 1, beside the harbour (2026-07-29).
# A cabin's 5x4 footprint on purpose: the whole point is that it reads CIVIC
# without needing a bigger hole in the map. The bell-cote on its ridge is the
# silhouette, the way the cupola is the library's.
tn.bake_shadow("vV", 3)
tn.emit_prop("MootHall", "vV", town_moot_hall(ROOFG, SNOWCAP, salt=361), hframes=8)

# ---- spruces, lamps, the pond -------------------------------------------------------
lo, up = town_conifer(tn.PINES, tn.TRUNK, SNOWCAP)
tn.emit_prop("ConiferTrunk", "Yy", sprite_img(lo, 32, 64), each=True)
tn.emit_prop("ConiferCrown", "Yy", sprite_img(up, 32, 64), each=True,
             top=0, base_inset=-16)
# The old-growth spruces: ONE unsplit sprite on the SAME 2x4 footprint as the
# small one, bottom-anchored so its extra 32px overhangs upward. No trunk/crown
# split — a spruce whose boughs reach the ground never needs a body to pass
# in front of its trunk and behind its canopy.
tn.emit_prop("BigConifer", "Pp",
             sprite_img(town_conifer_big(tn.PINES, tn.TRUNK, SNOWCAP), 32, 96),
             each=True)
tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(mantle=WARMC), 16, 32),
             each=True)
# THE SOUTH GATE'S TWO PIERS. Separate char pairs rather than one, only so each
# lamp can reach INTO the lane — everything else about the two sprites is the
# same call. See town_gatepost for why the gate exists at all.
for _ch, _face in (("nN", 1), ("mM", -1)):
    tn.emit_prop("GatePost" + ("W" if _face > 0 else "E"), _ch,
                 sprite_img(town_gatepost(TIMBER, tn.ROCK, SNOWCAP,
                                          face=_face), 16, 48), each=True)
tn.place("o", frozen_pond(SNOWCAP))                        # baked Tier-1 ice
# THE RINK: the same treatment at 8x4, and SKATED. A separate CHAR rather than
# more `o` cells because place() works off a char's whole-map bbox — a second
# `o` region would blit ONE pond sprite across everything between the two.
tn.place("O", frozen_pond(SNOWCAP, w=128, h=64, skated=True))

# ---- the harbour: the pier baked Tier-1, the launch y-sorted on the water ----------
# The DECK is one opaque 112x32 blit over the 7x2 run of walkable `=` cells, the
# town_trestle/cliff-face idiom: its rope rails sit ON walkable cells, and upper-layer
# art over a walkable cell is exactly what the z-order doctrine forbids. Nothing
# autotiles it either — the deck is walked along its length, and its west end butts
# the shore while its east end and both flanks are open water.
tn.place("=", town_dock(TIMBER, SNOWCAP))
# THE LAUNCH sits on the `b` berth cells, which paint as animated SEA. It is Tier-3
# and y-sorted SOUTH of the deck, which is what swallows the ~11px a body pressed
# into the deck's south row hangs over the water — the mask-band problem answered by
# composition instead of by a mask.
tn.emit_prop("Launch", "b", town_launch(TIMBER, SNOWCAP, salt=365), hframes=8)


# ---- additive glow: the town of lanterns --------------------------------------------
# Alphas are deliberately LOWER than the pre-Narshe build's: they were balanced
# against a near-white field, and the same dab on a dark one blows out to a
# white smear.
def _glow(img):
    for ch in ("qQ", "wW", "eE", "zZ", "vV"):              # every doorway +
        x0, y0, x1, y1 = tn.bbox(ch)                       # window burns warm
        cx = (x0 + x1 + 1) * T // 2
        by = (y1 + 1) * T
        _blob(img, cx, by - 6, 5, WARM, 38)                # the door spill
        _blob(img, cx - (x1 - x0) * 6, by - 12, 4, WARM, 32)   # west window
        _blob(img, cx + (x1 - x0) * 6, by - 12, 4, WARM, 32)   # east window
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
        _blob(img, ax + dx, by + 2, 11, WARM, 14)
    _blob(img, ax + 72, by + 6, 18, WARM, 30)
    _blob(img, ax + 72, by + 2, 10, WARM, 22)
    for chars, lx in (("nN", 13), ("mM", 2)):              # the gate lamps,
        for comp in tn.comps(chars):                       # each aimed at the
            x0, y0, _x1, y1 = tn.comp_bbox(comp)           # lane between them
            _blob(img, x0 * T + lx, y0 * T + 20, 4, WARM, 44)
            _blob(img, x0 * T + lx, (y1 + 1) * T, 8, WARM, 18)
    for comp in tn.comps("lL"):                            # the lamps
        x0, y0, x1, y1 = tn.comp_bbox(comp)
        # Small and dim, and BOTH dabs the same amber. A radial dab falls off
        # linearly, which on a pale field reads as a soft halo and on this dark
        # one reads as a hard disc lying on the snow — so the pool that was
        # r13/a34 against near-white had to come most of the way down.
        _blob(img, x0 * T + 8, y0 * T + 6, 4, WARM, 44)     # the mantle
        _blob(img, x0 * T + 8, (y1 + 1) * T, 8, WARM, 16)   # its pool on the snow
    ox0, oy0, _, _ = tn.bbox("o")                          # a cold moon-glint
    _blob(img, ox0 * T + 30, oy0 * T + 20, 8, (150, 190, 246), 20)
    # THE HARBOUR. Same lesson as the library: the overlay renders UNDER the
    # y-sorted World, so a dab at the launch's lantern height is simply hidden
    # behind the hull. The boat's light has to land on the WATER, and it is worth
    # spending — a lit boat at the end of a dark pier is the whole invitation.
    bx0, by0, bx1, by1 = tn.bbox("b")                      # the berth
    for dx in range(6, (bx1 - bx0 + 1) * T, 12):           # a continuous wash
        _blob(img, bx0 * T + dx, (by1 + 1) * T - 2, 9, WARM, 13)  # down the hull
    _blob(img, bx1 * T + 10, by0 * T + 8, 13, WARM, 34)    # the bow lantern
    _blob(img, bx1 * T + 10, (by1 + 1) * T - 6, 9, WARM, 18)
    dx0, dy0, dx1, dy1 = tn.bbox("=")                      # the pier: a low pool
    _blob(img, (dx0 + dx1) * T // 2 + 8, (dy1 + 1) * T - 8, 14, WARM, 12)
    # the cove itself, moonlit and cold — the one place in town that is not amber
    for _cx, _cy, _r in ((52, 42, 13), (49, 49, 11), (54, 46, 9)):
        _blob(img, _cx * T + 8, _cy * T + 8, _r, (150, 190, 246), 16)
    # CLIP: light does not spill down a rock face. Unclipped, the cabin and lamp
    # washes bleed onto the cliff below them and the terrace stops reading as a
    # terrace — the single thing this whole rebuild is for.
    for y in range(tn.m.rows_n):
        for x in range(tn.m.cols):
            if tn.m.at(x, y) in "CXB":
                for py in range(y * T, (y + 1) * T):
                    for px in range(x * T, (x + 1) * T):
                        img.put(px, py, (0, 0, 0, 0))


tn.write_glow(_glow)

# ---- the mask bands: swallow the ~11px of sprite that hangs past a cliff's
# physics boundary when a body presses south into it. All four faces get one —
# Must come after every lower-canvas write, because the band copies finished
# art. -----------------------------------------------------------------------------
for _face in ("C", "X", "B"):
    tn.mask_band(_face)

# ---- spruce authoring guard. Each spruce is one 2x4 connected component of
# {crown, trunk} chars: three walkable crown rows a body can stand among, then a
# solid trunk row. The old "alternate the case so adjacent blocks stay separate
# components" trick is GONE now that case means crown-vs-trunk, so two spruces
# authored edge-to-edge would fuse into a single component, a single bbox and
# one badly stretched sprite. Nothing else would complain.
for _chars in ("Yy", "Pp"):
    for _comp in tn.comps(_chars):
        _x0, _y0, _x1, _y1 = tn.comp_bbox(_comp)
        assert (_x1 - _x0, _y1 - _y0, len(_comp)) == (1, 3, 8), (
            f"lanternwood.txt: {_chars!r} component at ({_x0},{_y0}) is not a "
            f"clean 2x4 block — two spruces authored edge-to-edge fuse into one")
        for _cx, _cy in _comp:
            _want_solid = _cy == _y1                       # only the trunk row
            assert tn.m.legend[tn.m.at(_cx, _cy)]["solid"] == _want_solid, (
                f"lanternwood.txt: spruce cell ({_cx},{_cy}) should be "
                f"{'solid trunk' if _want_solid else 'walkable crown'}")

# ---- harbour + moot hall authoring guards (2026-07-29). The builders hard-code
# their pixel sizes, and prop_spawner centres art on the footprint bbox and puts
# its bottom on the bbox's south edge — so a footprint one cell wider silently
# mis-centres the whole building by 8px and one cell taller floats it. Nothing
# lints that; these do. -------------------------------------------------------------
_MOOT = tn.bbox("vV")                                  # town_moot_hall is 80x64
assert (_MOOT[2] - _MOOT[0], _MOOT[3] - _MOOT[1]) == (4, 3), (
    f"lanternwood.txt: the moot hall footprint is {_MOOT}, not 5x4 — "
    f"town_moot_hall draws 80x64 and prop_spawner will mis-centre it")
for _cx in range(_MOOT[0], _MOOT[2] + 1):              # roof rows over body rows
    assert (tn.m.at(_cx, _MOOT[1]), tn.m.at(_cx, _MOOT[3])) == ("v", "V"), _cx
assert tn.m.at((_MOOT[0] + _MOOT[2]) // 2, _MOOT[3] + 1) == "D", (
    "lanternwood.txt: the moot hall's D cell must sit one row south of the "
    "footprint at its x-centre — the door arch is drawn there in the art")

_DECK = tn.bbox("=")                                   # town_dock is 112x32
assert (_DECK[2] - _DECK[0], _DECK[3] - _DECK[1]) == (6, 1), (
    f"lanternwood.txt: the pier deck is {_DECK}, not 7x2 — town_dock draws 112x32")
_BERTH = tn.bbox("b")                                  # town_launch is 96x32
assert (_BERTH[2] - _BERTH[0], _BERTH[3] - _BERTH[1]) == (5, 1), (
    f"lanternwood.txt: the berth is {_BERTH}, not 6x2 — town_launch draws 96x32")
assert _BERTH[1] == _DECK[3] + 1, (
    "lanternwood.txt: the berth must lie DIRECTLY south of the deck — that "
    "adjacency is what makes the hull swallow a pressed body's overhang")
for _cx, _cy in ((x, y) for y in range(_DECK[1], _DECK[3] + 1)
                 for x in range(_DECK[0], _DECK[2] + 1)):
    assert not tn.m.legend[tn.m.at(_cx, _cy)]["solid"], (
        f"lanternwood.txt: pier cell ({_cx},{_cy}) must be WALKABLE")

tn.assert_reachable()
tn.finish()
