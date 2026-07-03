#!/usr/bin/env python3
"""32x32 meadow tileset for the zones (assets/tileset_gen.png, 128x64, 4x2).

Layout (atlas coords — contract with assets/tileset.tres, keep stable):
  (0,0) grass        (1,0) grass w/ tufts   (2,0) grass w/ flowers  (3,0) dirt path
  (0,1) hedge wall A (1,1) hedge wall B     (2,1) rock (decor)      (3,1) unused

Hedge tiles get full-square physics in assets/tileset.tres. Grass detail is placed by
a deterministic hash so re-runs are stable. Palette derives from
_palette.SCENES["meadow"] — minty teal greens, candy hot-pink flowers, warm peach
path with violet-leaning shadows. Re-run: python3 assets/_gen_tileset.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _artlib import Img, h2, pick, ZONE_TILE
from _palette import SCENES, ramp4

T, COLS, ROWS = ZONE_TILE, 4, 2

PAL = SCENES["meadow"]
GRASS_R = ramp4(PAL["mats"]["grass"], "teal")            # [lit, base, shade, core]
PATH_R  = ramp4(PAL["mats"]["path"], "violet", spread=0.8)   # peach, violet shadows
HEDGE_R = ramp4(PAL["mats"]["hedge"], "teal", spread=1.15)
ROCK_R  = ramp4(PAL["mats"]["rock"], "violet")

FLW_W = (252, 250, 242, 255)
FLW_Y = (255, 212, 84, 255)
FLW_P = PAL["accent"]                                    # candy hot pink
FLW_C = (244, 162, 70, 255)

img = Img(COLS * T, ROWS * T)


def put(tx, ty, x, y, c):
    if 0 <= x < T and 0 <= y < T:
        img.put(tx * T + x, ty * T + y, c)


def fill(tx, ty, c):
    for y in range(T):
        for x in range(T):
            put(tx, ty, x, y, c)


def speckle(tx, ty, salt, ramp, lo=26, hi=232):
    """2x2-block hash speckle: shade dabs below lo, lit dabs above hi."""
    for y in range(T):
        for x in range(T):
            r = h2(x // 2, y // 2, salt)
            if r < lo:
                put(tx, ty, x, y, ramp[2])
            elif r > hi:
                put(tx, ty, x, y, ramp[0])


def grass_base(tx, ty, salt):
    fill(tx, ty, GRASS_R[1])
    speckle(tx, ty, salt, GRASS_R)
    # blade clumps: 2px lit strokes with a dark root, turf feel at 2x density
    for i in range(8):
        bx = h2(i, salt, 11) % (T - 4)
        by = h2(salt, i, 12) % (T - 6)
        put(tx, ty, bx, by + 1, GRASS_R[0])
        put(tx, ty, bx, by + 2, GRASS_R[0])
        put(tx, ty, bx + 1, by, GRASS_R[0])
        put(tx, ty, bx + 1, by + 1, GRASS_R[0])
        put(tx, ty, bx + 1, by + 2, GRASS_R[1])
        put(tx, ty, bx + 2, by + 3, GRASS_R[2])
        put(tx, ty, bx + 1, by + 4, GRASS_R[3])              # root shadow
        put(tx, ty, bx + 2, by + 4, GRASS_R[3])


# (0,0) plain grass / (1,0) tufts / (2,0) flowers
grass_base(0, 0, 1)
grass_base(1, 0, 2)
for (x, y) in ((6, 9), (20, 17), (12, 25), (24, 5)):
    # sedge tuft: a little fan of dark blades
    put(1, 0, x, y, GRASS_R[3]); put(1, 0, x + 1, y, GRASS_R[3])
    put(1, 0, x - 1, y - 1, GRASS_R[3]); put(1, 0, x - 2, y - 2, GRASS_R[2])
    put(1, 0, x + 2, y - 1, GRASS_R[3]); put(1, 0, x + 3, y - 2, GRASS_R[2])
    put(1, 0, x, y - 1, GRASS_R[2]); put(1, 0, x + 1, y - 2, GRASS_R[2])
    put(1, 0, x, y + 1, GRASS_R[3]); put(1, 0, x + 1, y + 1, GRASS_R[3])
grass_base(2, 0, 3)
for (x, y, c) in ((7, 7, FLW_W), (21, 11, FLW_Y), (10, 23, FLW_P), (25, 25, FLW_P)):
    # layered flower head ~6px: 4 petals (2x2 each) around a warm center
    for px_, py_ in ((x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)):
        put(2, 0, px_, py_, c)
        put(2, 0, px_ + (1 if px_ <= x else -1), py_, c)
        put(2, 0, px_, py_ + 1, (c[0] - 30, max(0, c[1] - 40), c[2] - 20, 255))
    put(2, 0, x, y, FLW_C)
    put(2, 0, x + 1, y, FLW_C)
    put(2, 0, x, y + 4, GRASS_R[3])                          # stem shadow
    put(2, 0, x + 1, y + 5, GRASS_R[3])

# (3,0) dirt path with pebbles (peach field, violet shade)
fill(3, 0, PATH_R[1])
speckle(3, 0, 4, PATH_R, lo=12, hi=240)
for i in range(6):
    px_ = h2(i, 9, 13) % (T - 4)
    py_ = h2(9, i, 14) % (T - 3)
    put(3, 0, px_, py_, PATH_R[0])                           # pebble catches the light...
    put(3, 0, px_ + 1, py_, PATH_R[0])
    put(3, 0, px_ + 2, py_, PATH_R[1])
    put(3, 0, px_, py_ + 1, PATH_R[1])
    put(3, 0, px_ + 1, py_ + 1, PATH_R[2])
    put(3, 0, px_ + 2, py_ + 1, PATH_R[3])                   # ...and casts a tiny shadow
    put(3, 0, px_ + 1, py_ + 2, PATH_R[3])

# (0,1) & (1,1) hedge walls: overlapping leaf-ball domes lit from the top-left
for tx, salt in ((0, 5), (1, 6)):
    fill(tx, 1, HEDGE_R[2])
    # back layer: dark pockets so gaps between domes read as depth
    speckle(tx, 1, salt + 20, [HEDGE_R[1], HEDGE_R[2], HEDGE_R[3], HEDGE_R[3]], lo=60, hi=250)
    for cy in range(0, T, 6):                # jittered overlapping leaf balls
        for cx in range(0, T, 6):
            jx = h2(cx, cy, salt) % 4 - 1
            jy = h2(cy, cx, salt) % 4 - 1
            bx, by = cx + 3 + jx, cy + 2 + jy
            r = 3.4 + (h2(cx, cy, salt + 1) % 3) * 0.5
            for y in range(round(by - r), round(by + r) + 1):
                for x in range(round(bx - r), round(bx + r) + 1):
                    nx = (x - bx) / r
                    ny = (y - by) / r
                    d = nx * nx + ny * ny
                    if d > 1.0:
                        continue
                    t = 0.30 + 0.34 * (nx * 0.55 + ny * 0.85) + 0.34 * d
                    put(tx, 1, x, y, pick(HEDGE_R, t, x, y, grain=2))
    for x in range(T):                       # lit top edge, shadowed base
        put(tx, 1, x, 0, HEDGE_R[0])
        if h2(x, 1, salt) % 3:
            put(tx, 1, x, 1, HEDGE_R[0])
        put(tx, 1, x, T - 3, HEDGE_R[3])
        put(tx, 1, x, T - 2, HEDGE_R[3])
        put(tx, 1, x, T - 1, HEDGE_R[3])

# (2,1) rock on grass (decor, no collision): lavender boulder, upper-left lit
grass_base(2, 1, 7)
for y in range(10, 27):
    half = 10 - abs(y - 19) * 0.62
    for x in range(round(16 - half), round(16 + half) + 1):
        nx = (x - 16) / 10.0
        ny = (y - 18) / 9.0
        t = 0.40 + 0.32 * (nx * 0.6 + ny * 0.8) + 0.20 * (nx * nx + ny * ny)
        put(2, 1, x, y, pick(ROCK_R, t, x, y, grain=2))
for x, y in ((12, 13), (13, 13), (14, 14), (19, 17), (20, 18)):   # facet cracks
    put(2, 1, x, y, ROCK_R[3])
for x in range(9, 24):                                            # ground shadow
    put(2, 1, x, 27, GRASS_R[3])

# (3,1) reserved: plain grass so it isn't a hole if ever painted
grass_base(3, 1, 8)

img.save(os.path.join(HERE, "tileset_gen.png"))
