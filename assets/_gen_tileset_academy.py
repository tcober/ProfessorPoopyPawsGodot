#!/usr/bin/env python3
"""THE ALEMBIC ACADEMY — the precinct north of Alembic Town, its own scene.

Read assets/maps/academy.txt's header for the composition and why it is shaped
the way it is; this file only paints it. The five pieces no town has live in
assets/_academy_props.py (the KEEP, the rampart, the drum towers, the orrery,
the two wings); the rest is REUSED from _town_props — the terrace is
Lanternwood's cast-cement `town_cliff(wall=True)`, the flight is `town_stairs`,
the lamps and small trees are the town's own.

THE KEEP USED TO BE `_town_props.town_academy`, a cement landmark drawn for the
town grid the Academy has since left, with the two great trees standing six cells
out in the lawn beside it. It is now `_academy_props.academy_keep` — a timber hall
whose corner towers ARE those trees, in one 416x192 sprite. `town_academy` had no
other caller and has been retired.

THE BECK NEEDS NO FASCIA AND NO MASK BAND. Alembic's stream takes a hand-drawn
`bridge_fascia` on the water cell south of its deck, because there you stand ON
a deck with water below and want the bridge's own rail in front of you. Here the
water is TERRAIN with paving beside it: a body at the bank hangs 11px of sprite
over the beck exactly the way it hangs over every shoreline in this game, and
there is no vertical face for a band to re-draw. Masking it would be masking the
water.

Re-run: python3 assets/_gen_tileset_academy.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_tiles import OverWorld, T
from _tilekit import sprite_img, GLOW_WARM as WARM, GLOW_MINT as MINTG
from _town_props import town_cliff, town_stairs, town_lamp, town_tree
from _academy_props import (academy_rampart, academy_tower, academy_orrery,
                            academy_wing, academy_keep, court_weed)
from _tree_props import understory, BARK

_blob = OverWorld.glow_blob

RAMP_SALTS = (601, 607, 613, 619, 623, 629)
CLIFF_SALTS = (291, 293, 297, 299, 307, 311)
# every char whose cell the glow must be WIPED off — see the clip pass
FACES = "WuC"


# THE LITTER'S OWN BROWN, HAND-PINNED. Derived from this scene's timber the way the
# town's is, it comes out RED: the academy palette is violet-biased and the module
# TIMBER seed is already warm, so ramp()'s violet shadow law lands its midtones on
# brick — scattered over a green lawn that reads as blood, not leaves.
ROT_LATER = [(196, 168, 116, 255), (170, 138, 92, 255), (142, 112, 78, 255),
             (112, 86, 68, 255), (80, 60, 62, 255), (52, 38, 50, 255)]


def build():
    ac = OverWorld("academy", "academy")
    STONE = ac.ROCK                    # the precinct's own violet-pale masonry
    FOL = ac.FOREST
    DECK = ac.DECK

    ac.paint_terrain()

    # ---- THE TERRACE the keep stands on, and the flight through it -------------------
    # town_cliff(wall=True): the cast-cement retaining wall built for Lanternwood. A
    # precinct wants a MADE wall, not an eroded rock face — all the contrast in a
    # regular joint grid and none of it in per-stone value.
    ac.stamp_columns("C", [town_cliff(STONE, ac.GRASS, salt=s, h=2 * T, wall=True)
                           for s in CLIFF_SALTS], salt=53, run=2)
    ac.place("S", town_stairs(STONE, cells=2))

    # ---- THE RAMPART and its gatehouse -----------------------------------------------
    ac.stamp_columns("W", [academy_rampart(STONE, salt=s, h=2 * T)
                           for s in RAMP_SALTS], salt=59, run=2)
    ac.place_each("u", academy_tower(STONE, salt=611, w=2 * T, h=3 * T))

    # ---- THE BACK RANK ----------------------------------------------------------------
    # THE KEEP IS A TIMBER CASTLE-SCHOOL AND ITS CORNER TOWERS ARE THE TWO GREAT
    # TREES — one sprite, 416x192, over the whole 22x9 `Aa` block. It replaced
    # `town_academy`, which was drawn for the town grid the Academy has left and
    # read here as a flat cream wall with a garden on top, with the two trees
    # standing six cells out in the lawn where nothing could tie them to it.
    # The art is 26 cells wide over 22 cells of collision: emit_prop centres art on
    # its block, so the crowns hang two cells of leaf into the lawn either side and
    # you walk under them.
    ac.emit_prop("Keep", "Aa",
                 academy_keep(STONE, BARK, FOL, ac.GRASS, salt=221,
                              composite=True, frames=8),
                 hframes=8)
    # THE TWO WINGS ARE ONE BUILDER, ONE SALT, TWO CROWNS. Their facades come out
    # byte-identical and dedupe to the same atlas tiles; only the ~2 crown rows
    # differ. They carry separate CHARS rather than sharing a pair because emit_prop
    # places a sprite at the chars' BBOX — one shared pair would stretch a single
    # sprite across both wings and the width of the court between them.
    for name, chars, kind in (("Observatory", "Be", "observatory"),
                              ("Stillhouse", "Nn", "still")):
        ac.emit_prop(name, chars,
                     academy_wing(STONE, salt=631, kind=kind, composite=True,
                                  frames=8),
                     hframes=8)

    # ---- the court furniture ----------------------------------------------------------
    ac.emit_prop("Orrery", "Qq",
                 sprite_img(academy_orrery(STONE, salt=621, w=6 * T, h=4 * T),
                            6 * T, 4 * T))
    ac.emit_prop("Lamp", "mL", sprite_img(town_lamp(), T, 2 * T), each=True)
    lo, up = town_tree(FOL, ac.TRUNK, ac.GRASS)
    ac.emit_prop("TreeTrunk", "Tt", sprite_img(lo, 2 * T, 3 * T), each=True)
    ac.emit_prop("TreeCrown", "Tt", sprite_img(up, 2 * T, 3 * T), each=True,
                 top=0, base_inset=-16)

    # ---- the litter, and ONLY off the paving ------------------------------------------
    # The precinct is a clearing in the same forest the town stands in, so it gets the
    # same floor — but a swept court is the whole point of a court, so this runs on
    # grass and flowers only and banks against the treeline, never out onto the stone.
    # THE LITTER'S OWN BROWN, HAND-PINNED. Derived from this scene's timber the way
    # the town's is, it comes out RED: the academy palette is violet-biased and the
    # module TIMBER seed is already warm, so ramp()'s violet shadow law lands its
    # midtones on brick. Scattered over a green lawn that reads as blood, not leaves.
    ROT = ROT_LATER
    KINDS = (("drift", 4), ("fern", 2), ("sapling", 2), ("roots", 1))
    under = {k: [understory(FOL, ROT, ac.GRASS, kind=k, salt=461 + 31 * i + 7 * v)
                 for v in range(n)]
             for i, (k, n) in enumerate(KINDS)}
    POOL = ("drift", "drift", "fern", "drift", "sapling", "roots")
    for y in range(ac.m.rows_n):
        for x in range(ac.m.cols):
            if ac.m.at(x, y) not in ".,":
                continue
            near = any((ac.m.at(x + ax, y + ay) or "") in "#Tt"
                       for ax in (-1, 0, 1) for ay in (-1, 0, 1))
            if not near or h2(x, y, 467) % 16 >= 7:
                continue
            bag = under[POOL[h2(x, y, 463) % len(POOL)]]
            ac.bg.blit_cell(bag[h2(x, y, 479) % len(bag)], x * T, y * T)

    # ---- NOBODY HAS SWEPT THE COURT ---------------------------------------------------
    # 300-odd cells of one flat stone was the biggest remaining problem in the
    # precinct after the buildings, and the cheapest honest fix is not more paving
    # detail — it is the fact that this is a college the world stopped funding, in the
    # season the magic drained out of the ground. Cracks, weeds and moss, banked toward
    # the edges where the sweeping stops first and thinning along the axis where feet
    # still fall. See _academy_props.court_weed.
    WEEDS = [court_weed(ac.ROAD, ac.GRASS, salt=701 + 17 * i, kind=i % 4)
             for i in range(12)]
    for y in range(ac.m.rows_n):
        for x in range(ac.m.cols):
            if ac.m.at(x, y) != "-":
                continue
            edgeward = any((ac.m.at(x + ax, y + ay) or "") in ".,#TtCWuBeNn"
                           for ax in (-1, 0, 1) for ay in (-1, 0, 1))
            axis = abs(x - 30) <= 1                        # the way feet still take
            # PATCHES, NOT CONFETTI. Rolled per cell at an even rate the weeds came
            # out as uniform speckle over the whole ward, which is its own kind of
            # flat — a texture rather than a place that has been let go. Weeds
            # colonise: gate the roll on a coarse 3x3 field first, so growth comes
            # in drifts with swept stone between them.
            if h2(x // 3, y // 3, 743) % 5 >= 3:
                continue
            chance = 4 if axis else (13 if edgeward else 9)
            if h2(x, y, 733) % 16 >= chance:
                continue
            ac.bg.blit_cell(WEEDS[h2(x, y, 739) % len(WEEDS)], x * T, y * T)

    # ---- THE BECK'S BANKS ---------------------------------------------------------------
    # The stream shipped as a flat blue strip laid across a green one, with no edge
    # between them at all: two fabrics meeting on a grid line read as a painted band,
    # not as water in a channel. Reeds and bank stones on the cells that touch it are
    # what make it a beck.
    REEDS = [understory(FOL, ROT_LATER, ac.GRASS, kind="fern", salt=751 + 13 * i)
             for i in range(3)]
    for y in range(ac.m.rows_n):
        for x in range(ac.m.cols):
            if ac.m.at(x, y) not in ".," :
                continue
            if not any((ac.m.at(x + ax, y + ay) or "") == "r"
                       for ax in (-1, 0, 1) for ay in (-1, 0, 1)):
                continue
            if h2(x, y, 757) % 8 >= 5:
                continue
            ac.bg.blit_cell(REEDS[h2(x, y, 761) % len(REEDS)], x * T, y * T)

    ac.write_glow(lambda img: glow(ac, img))

    # ---- THE DEPTH MASKS --------------------------------------------------------------
    # Both walls and both towers: pressed south into any of them ~11px of sprite hangs
    # past the physics box and draws over the face below. MUST come after every
    # lower-canvas write — it copies FINISHED art. NOT on the keep or the wings:
    # those are Tier-3 y-sorted sprites and sort correctly on their own.
    for ch in ("C", "W", "u"):
        ac.mask_band(ch)

    assert_all(ac)
    ac.finish()
    return ac


def glow(ac, img):
    """Almost nothing burns here any more, and that is the beat. The rose window is
    the exception, and it is the one cold light in the game that is not a lamp:
    DESIGN.md has said since the town icon was drawn that the Academy's rose window
    burns MINT."""
    m = ac.m
    x0, y0, x1, y1 = ac.bbox("Aa")
    cx = (x0 + x1 + 1) * T // 2                             # = 496, the precinct axis
    # The keep's sprite is 416x192 bottom-anchored on a 22x9 block, so its own
    # origin is (axis - 208, block_bottom - 192) and every dab below is quoted as
    # a SPRITE-LOCAL coordinate off that. Quoting them off the bbox instead is how
    # the old build ended up lighting a rose window that had moved.
    base = (y1 + 1) * T - 192                               # the keep sprite's own y0
    _blob(img, cx, base + 104, 21, MINTG, 108)              # THE ROSE WINDOW
    _blob(img, cx, base + 186, 18, MINTG, 32)               # its wash on the door
    for dx in (-86, 86):                                    # the hall's lancets
        _blob(img, cx + dx, base + 148, 15, WARM, 66)
    _blob(img, cx + 159, base + 100, 9, MINTG, 52)          # the gallery lamp
    for chars in ("Be", "Nn"):                              # the wings' windows
        wx0, wy0, wx1, wy1 = ac.bbox(chars)
        wbase = (wy1 + 1) * T
        for dx in (-42, 0, 42):
            _blob(img, (wx0 + wx1 + 1) * T // 2 + dx, wbase - 30, 10, WARM, 56)
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in "mL" and m.at(x, y - 1) not in "mL":
                _blob(img, x * T + 7, y * T + 4, 10, MINTG, 34)
    # THE CLIP PASS, and it is not optional. Light does not spill down a vertical
    # face: the glow overlay renders UNDER the y-sorted World, so a court lamp's wash
    # bleeding onto the rampart behind it lands on stone nowhere near the light and
    # flattens the whole wall.
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))


def assert_all(ac):
    """Every failure below is SILENT otherwise: it renders, it dedupes, and every
    lint in _check_art.py passes it."""
    ac.assert_strata()
    ac.assert_stair("S", "C", 2)
    ac.assert_door_approach(rows=2)
    ac.assert_npc_room()
    for chars, w, h, n in (("AaD", 22, 9, 1), ("Be", 9, 6, 1), ("Nn", 9, 6, 1),
                           ("Qq", 6, 4, 1), ("u", 2, 3, 2), ("Tt", 2, 2, 18)):
        cs = ac.comps(chars)
        assert len(cs) == n, (
            f"academy.txt: {chars!r} has {len(cs)} components, want {n}")
        for c in cs:
            a, b, c2, d = ac.comp_bbox(c)
            assert (c2 - a + 1, d - b + 1) == (w, h), (
                f"academy.txt: the {chars!r} component at ({a},{b}) is "
                f"{c2 - a + 1}x{d - b + 1}, want {w}x{h}")
    # THE GATE IS THE ONLY WAY THROUGH THE RAMPART, and that IS the composition. If a
    # second hole opens in the wall the sequence stops being a sequence, and nothing
    # else here would notice: the map still renders, and assert_reachable is satisfied
    # by EITHER hole.
    for wall, want, what in (("W", [30, 31], "the gate"),
                             ("C", [30, 31], "the grand stair")):
        rows = sorted({y for y in range(ac.m.rows_n) for x in range(ac.m.cols)
                       if ac.m.at(x, y) == wall})
        assert rows, f"academy.txt: no {wall!r} wall in the grid at all"
        holes = [x for x in range(ac.m.cols)
                 if all(not ac.m.legend[ac.m.at(x, y)]["solid"] for y in rows)]
        assert holes == want, (
            f"academy.txt: the {wall!r} wall is pierced at columns {holes}, want "
            f"{want} — {what} must be the only way through. A cross-map wall that "
            f"stops one cell short of the forest border leaves a grass lane round "
            f"the end of it, which is exactly how this first shipped.")
    ac.assert_reachable("player_start", "hall", "orrery", "gate", "observatory",
                        "stillhouse")


if __name__ == "__main__":
    build()
