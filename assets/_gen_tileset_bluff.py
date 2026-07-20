#!/usr/bin/env python3
"""The sunset bluff, tiled — a thin CONFIG on the shared overworld tile kit.

The bluff map (assets/maps/bluff.txt) rides assets/_overworld_tiles.py's
OverWorld driver directly: forest windbreak border, gilded grass headland
with flower drifts, and the sea running across the NORTH of the screen
(the 2026-07-17 from-behind restage — a body at the lip faces up-screen,
back to the camera, looking out at the sunset water). This file picks the
`bluff` sunset palette (assets/_palette.py) and authors three one-off
pieces:

  - the CLIFF-LIP band: 16x16 rim cells stamped per C column (three salted
    variants, the town_cliff recipe turned 90°). A north-facing drop shows
    no face in SNES perspective — the lip reads as a ragged sunlit brow
    with a dark crevice line where the rock falls away into the water.
  - the WINDSWEPT TREE (`t`): one 48x64 Tier-3 y-sorted prop leaning over
    the lip, crown streaming east off the sea wind, sunset rim-light on
    its north lobes. emit_prop -> bluff_props.txt -> scene/prop_spawner.gd.
  - the SUN GLINT lane: an additive glow overlay laying the low sun's
    reflection down the water toward the couple's spot (the scene tints it
    per phase — bluff.gd owns the hour).

Re-run: python3 assets/_gen_tileset_bluff.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_tiles import OverWorld, T
from _propkit import S, ln, edge
from _tilekit import sprite_img

bl = OverWorld("bluff", "bluff")
bl.paint_terrain()


# ---- the cliff lip: one 16x16 rim cell per C column. Reading south->north
# (bottom of the cell to the top): headland grass, the sod's turn-under
# shadow, a sunlit rock brow (the low sun sits OVER the water, so the rim's
# north curve catches it), then the 1-2px near-black crevice where the face
# falls away — the drop itself is hidden at this angle; the dark line against
# the indigo water IS the height. FULLY OPAQUE, no edge() (per-column outlines
# would print a seam every 16px — the town_cliff rule). ---------------------------
def bluff_lip(rock, grass, salt=291):
    sp = S(16, 16, salt)
    for x in range(16):
        drop = 1 + h2((x + salt) // 4, 0, salt) % 2        # crevice depth, 4px runs
        brow = drop + 2 + h2((x + salt) // 5, 1, salt) % 2  # lit brow band
        grs = 12 + h2((x + salt) // 3, 2, salt) % 3        # ragged sod line
        for y in range(16):
            if y < drop:
                c = rock[5]                                # the drop's crevice
            elif y <= brow:
                c = rock[0] if y < brow else rock[1]       # sunlit brow curve
            elif y >= grs:
                c = grass[2]                               # headland sod
                if h2(x, y, salt + 3) % 7 == 0:
                    c = grass[1]                           # clump nicks
            elif y == grs - 1:
                c = grass[4]                               # sod turn-under
            elif y >= grs - 3:
                c = rock[3]                                # shaded under-ledge
            else:
                c = rock[2]                                # mid face sliver
            sp.set(x, y, c)
        if h2(x, 9, salt) % 5 == 0:                        # strata fleck
            sp.set(x, 6 + h2(x, 3, salt) % 3, rock[4])
    yy = 7 + h2(salt, 2, 1) % 2                            # one dashed strata crack
    for x in range(16):
        if h2(x // 3, 5, salt) % 3 != 0:
            sp.set(x, yy, rock[4])
    return sp


lips = [bluff_lip(bl.ROCK, bl.GRASS, salt=s) for s in (291, 293, 297)]
for ty in range(bl.m.rows_n):
    for tx in range(bl.m.cols):
        if bl.m.at(tx, ty) == "C":
            bl.bg.blit_cell(lips[h2(tx, ty, 51) % 3], tx * T, ty * T)


# ---- the windswept tree: one hero 48x64 prop at the lip (`t`), trunk leaning
# east, crown streaming east off the north sea wind, dusk-violet foliage with
# the sunset's amber rim on its north lobes. Tier-3 y-sorted (a body stands
# beside and south of it); the west/east flanks below the crown stay EMPTY so
# a body walking beside the trunk overlaps only air. -------------------------------
def bluff_tree(forest, trunk, accent, salt=311):
    sp = S(48, 64, salt)
    north_lit = (0.0, -1.0)                                # the sun is on the water
    # bare windward stubs first (the trunk overlaps their base)
    sp.capsule(20, 44, 12, 40, 1.2, 0.8, trunk, sh=0.16)
    sp.capsule(24, 34, 18, 29, 1.1, 0.8, trunk, sh=0.12)
    # roots + the leaning trunk
    sp.capsule(17, 60, 11, 63, 2.4, 1.4, trunk, sh=0.10)
    sp.capsule(18, 60, 25, 63, 2.4, 1.4, trunk, sh=0.16)
    sp.capsule(17, 61, 22, 42, 3.8, 3.0, trunk, sh=0.04)
    sp.capsule(22, 42, 28, 27, 2.8, 2.0, trunk, sh=0.08)
    sp.capsule(28, 27, 35, 21, 1.8, 1.4, trunk, sh=0.12)   # limb into the crown
    for y in range(44, 60):                                # bark grooves
        if (y // 3) % 2 == 0:
            sp.set(18 + (y - 44) // 5, y, trunk[3])
    sp.rect(15, 46, 15, 58, trunk[1])                      # west rim light
    # the crown: flag-form lobes streaming east, lit from the north
    for cx, cy, rx, ry, sh in ((21, 22, 8.5, 6.0, 0.12),
                               (31, 15, 11.0, 7.0, 0.02),
                               (41, 19, 6.5, 4.5, 0.14),
                               (30, 25, 9.0, 5.0, 0.20),
                               (23, 11, 7.0, 5.0, 0.00)):
        sp.ball(cx, cy, rx, ry, forest, sh=sh, power=2.2, light=north_lit)
    sp.blob(28, 21, 4.0, 2.0, forest[4])                   # lobe seam shadows
    sp.blob(34, 24, 5.0, 2.0, forest[5])
    sp.despeckle(passes=1)
    edge(sp)
    for y in range(sp.n):                                  # clip to the footprint
        for x in range(48, sp.n):
            sp.px[y][x] = None
    # sunset rim: deliberate amber catches along the crown's north silhouette,
    # drawn AFTER the outline (the sage sparkle rule)
    for (x, y) in ((18, 7), (19, 6), (24, 5), (25, 5), (30, 8), (31, 8),
                   (36, 12), (37, 13), (43, 15), (44, 16), (16, 10)):
        if sp.get(x, y) is not None:
            sp.set(x, y, accent)
    return sp


bl.bake_shadow("t", 3)
bl.emit_prop("BluffTree", "t", sprite_img(bluff_tree(
    bl.FOREST, bl.TRUNK, bl.ACCENT), 48, 64))


# ---- the sky band (2026-07-18): the sea used to run to the frame's top edge
# and read as a NIGHT SKY. An opaque overlay now owns the top of the frame —
# banded sky art down to a horizon line at y=HORIZON, transparent below so
# the animated water still plays underneath. Two textures (sunset / day);
# bluff.gd swaps them per phase and its CanvasModulate carries the hour, so
# the one dusk painting serves sunset, dusk AND night. Flat hard bands on
# purpose (the CT-sky read) — no dither, one hot seam line at the waterline.
HORIZON = 28


def _sky_bands(img, bands):
    """Horizontal hard bands from y=0 down: each entry is (to_y, rgb)."""
    y0 = 0
    for to_y, c in bands:
        for y in range(y0, to_y):
            for x in range(bl.W):
                img.put(x, y, c + (255,))
        y0 = to_y


def _sky_dusk(img):
    # dusk violet up top -> rose -> hot amber -> gold at the waterline; the
    # SUN itself lives on the glow overlay, so putting the glow out at night
    # sets it — the sky art never needs to change
    _sky_bands(img, [
        (8, (74, 48, 110)),                                # high dusk violet
        (14, (128, 62, 118)),                              # magenta-rose
        (19, (196, 92, 110)),                              # rose-orange
        (24, (240, 150, 96)),                              # hot amber
        (HORIZON - 1, (252, 206, 128)),                    # gold at the water
        (HORIZON, (255, 236, 178)),                        # the horizon shimmer
    ])


def _sky_day(img):
    # the meet phase's bright afternoon: cyan paling to the waterline, one
    # small high sun baked opaque (day needs no glint lane)
    _sky_bands(img, [
        (10, (96, 168, 216)),
        (18, (140, 196, 228)),
        (24, (188, 222, 236)),
        (HORIZON - 1, (228, 240, 244)),
        (HORIZON, (244, 250, 252)),                        # pale shimmer line
    ])
    for dy in range(-4, 5):                                # the day sun, high E
        for dx in range(-4, 5):
            q = dx * dx + dy * dy
            if q <= 16:
                img.put(330 + dx, 8 + dy,
                        (255, 244, 200, 255) if q > 6 else (255, 252, 230, 255))


def _stars(img):
    # additive night layer: hand-set twinkles down to the horizon, a small
    # moon NE of the sun lane, and its faint glint on the water below. Fades
    # IN as bluff.gd's night falls; the scene alpha-pulses it for twinkle.
    stars = [
        (18, 5, 2), (52, 12, 1), (84, 3, 2), (120, 18, 1), (147, 7, 2),
        (178, 13, 1), (205, 4, 1), (238, 9, 2), (262, 16, 1), (300, 6, 2),
        (330, 20, 1), (356, 24, 1), (388, 11, 2), (420, 17, 1), (447, 6, 2),
        (470, 14, 1), (500, 8, 1), (30, 22, 1), (108, 24, 1),
        (272, 24, 1), (368, 3, 1), (496, 21, 1),
    ]
    for (x, y, r) in stars:
        OverWorld.glow_blob(img, x, y, r + 1, (210, 224, 255), 46)
        img.put(x, y, (240, 248, 255, 200))
    # the moon: a small bright disc + halo
    OverWorld.glow_blob(img, 352, 9, 8, (190, 214, 255), 34)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dx * dx + dy * dy <= 10:
                img.put(352 + dx, 9 + dy, (226, 238, 255, 170))
    # moon-glint: a faint silver lane on the water under it (the amber sun
    # lane fades OUT at night; this fades in with the stars to replace it)
    for i, y in enumerate(range(HORIZON + 2, 64, 5)):
        x = 352 + (h2(i, 3, 13) % 5) - 2
        OverWorld.glow_blob(img, x, y, 3, (196, 214, 244), 16)


bl.write_overlay("sky_dusk", _sky_dusk)
bl.write_overlay("sky_day", _sky_day)
bl.write_overlay("stars", _stars)


# ---- the sun glint: the setting sun ON the horizon line plus its reflection
# lane down the water, aimed at the couple's lip spot (kitty_pos x≈248).
# Additive overlay; bluff.gd fades it per phase (full at sunset, low at dusk,
# out at night — fading the glow IS the sunset, since the sun disc lives
# here and not on the opaque sky art). ----------------------------------------------
def _glow(img):
    # a dense chain of small overlapping dabs — one continuous tapering
    # lane, never a row of readable circles
    for i, y in enumerate(range(HORIZON + 2, 68, 5)):
        r = 13 - i                                         # wide at the horizon
        x = 240 + (h2(i, 1, 7) % 7) - 3                    # lane wobble
        OverWorld.glow_blob(img, x, y, max(5, r), (255, 198, 126), 30)
        OverWorld.glow_blob(img, x, y, max(3, r - 6), (255, 214, 150), 22)
    for (x, y) in ((196, 40), (286, 44), (214, 56), (270, 34)):
        OverWorld.glow_blob(img, x, y, 3, (255, 214, 150), 26)  # stray twinkles
    # the sun, half-set on the horizon — drawn LAST so its core wins the lane
    OverWorld.glow_blob(img, 240, HORIZON - 2, 11, (255, 214, 142), 58)
    OverWorld.glow_blob(img, 240, HORIZON - 2, 6, (255, 240, 190), 78)


bl.write_glow(_glow)

bl.finish()
