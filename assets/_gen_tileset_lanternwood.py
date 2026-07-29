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


# ---- additive glow: the town of lanterns --------------------------------------------
# Alphas are deliberately LOWER than the pre-Narshe build's: they were balanced
# against a near-white field, and the same dab on a dark one blows out to a
# white smear.
def _glow(img):
    for ch in ("qQ", "wW", "eE", "zZ"):                    # every doorway +
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

tn.assert_reachable()
tn.finish()
