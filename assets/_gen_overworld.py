#!/usr/bin/env python3
"""Overworld art for the Chrono Trigger / Sea of Stars travel layer, at 2x density.

Generates three sheets (referenced by hand-authored .tres/.tscn files — the
layouts are contracts, keep them stable):

  overworld_tiles.png  256x96 — 8x3 atlas of 32x32 seamless terrain tiles:
    (0,0) water          (1,0) water sparkle   (2,0) sand         (3,0) grass
    (4,0) grass detail   (5,0) scrub           (6,0) path         (7,0) bridge
    (0,1) forest A       (1,1) forest B        (2,1) forest edge  (3,1) hills
    (4,1) mountain       (5,1) snow peak       (6,1) river        (7,1) cliff
    (0,2) cracked A      (1,2) cracked B       (2,2) dead tree    (3,2) crystal
    (4,2)-(7,2) reserved grass variants
  overworld_basil.png  192x144 — 4x3 grid of 48x48 cells: chibi travel-scale
    Basil (big head, goggles, lab coat). row0 walk_down, row1 walk_up,
    row2 walk_side (faces RIGHT; code mirrors). Frames 0/2 are contact poses,
    1/3 passing poses with a 2px bob. Feet baseline y=42 (_artlib.OW_FEET),
    centered on x=24.
  overworld_icons.png  320x64 — five 64x64 landmark icons over ground-shadow
    ellipses, base y~56: 0 home cottage · 1 town · 2 meadow grove ·
    3 cave mouth · 4 obelisk.

Palette: the big terrain fields (sea, grass, path, wastes) derive from
_palette.SCENES["overworld"] via ramp4 — teal sea and sage-teal land with the
drained wastes pushed hot violet (the Paper Girls read). Chibi Basil uses
_palette.BASIL identity ramps. Light upper-left, hash-dithered, deterministic.

Re-run: python3 assets/_gen_overworld.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _artlib import Cell, Img, h2, pick, write_png, OW_TILE, OW_CELL, OW_FEET, ICON
from _palette import SCENES, BASIL, ramp4

PAL = SCENES["overworld"]

# ===== 1) terrain tiles ==========================================================
T, TCOLS, TROWS = OW_TILE, 8, 3

WATR = ramp4(PAL["mats"]["sea"], "teal")            # [ripple, base, deep, gloom]
GRSR = ramp4(PAL["mats"]["grass"], "teal", spread=0.9)
SNDR = ramp4(PAL["mats"]["sand"], "violet", spread=0.55)
PTHR = ramp4((206, 170, 128, 255), "violet", spread=0.55)
WSTR = ramp4(PAL["mats"]["waste"], "violet")        # violet parched wastes

SPARK    = (168, 224, 232, 255)
SPARK_L  = (222, 244, 246, 255)
RIVER    = (70, 118, 150, 255)
RIVER_D  = (56, 100, 136, 255)
RIVER_L  = (104, 152, 176, 255)
FLW_W    = (240, 240, 232, 255)
FLW_P    = (232, 130, 186, 255)                     # hot meadow pink, map-muted
BUSH     = (44, 102, 82, 255)
BUSH_L   = (72, 130, 94, 255)
WOOD     = (150, 110, 72, 255)
WOOD_D   = (118, 84, 56, 255)
WOOD_L   = (176, 136, 92, 255)
WOOD_S   = (86, 60, 42, 255)                        # plank gaps / grain
CANOPY   = [(104, 162, 96, 255), (82, 142, 88, 255), (50, 104, 76, 255), (32, 76, 62, 255)]
LEAF_S   = (22, 58, 50, 255)                        # deepest crevice
MTN      = [(160, 148, 158, 255), (128, 118, 136, 255), (98, 88, 112, 255), (72, 64, 88, 255)]
SNOW     = (236, 238, 246, 255)
SNOW_D   = (198, 206, 230, 255)
CLIFF    = [(128, 116, 128, 255), (104, 94, 110, 255), (82, 72, 92, 255), (58, 50, 70, 255)]
CRACK    = (110, 62, 96, 255)                       # crack lines in the wastes
CRACK_S  = (80, 42, 74, 255)
TRUNK    = (86, 56, 70, 255)
TRUNK_D  = (60, 38, 52, 255)
CRYS     = [(230, 196, 255, 255), (196, 120, 255, 255), (150, 88, 208, 255), (108, 62, 158, 255)]

img = Img(TCOLS * T, TROWS * T)


def tput(tx, ty, x, y, c):
    if 0 <= x < T and 0 <= y < T:
        img.put(tx * T + x, ty * T + y, c)


def tfill(tx, ty, c):
    for y in range(T):
        for x in range(T):
            tput(tx, ty, x, y, c)


def speckle(tx, ty, dark, light, salt, lo=24, hi=234):
    """2x2-block hash speckle."""
    for y in range(T):
        for x in range(T):
            r = h2(x // 2, y // 2, salt)
            if r < lo:
                tput(tx, ty, x, y, dark)
            elif r > hi:
                tput(tx, ty, x, y, light)


def water_base(tx, ty):
    tfill(tx, ty, WATR[1])
    speckle(tx, ty, WATR[2], WATR[1], 21, lo=20, hi=256)
    # dashed ripple bands, phase-shifted per row
    for row, phase in ((6, 0), (16, 10), (26, 20)):
        for x in range(T):
            if h2((x + phase) // 8, row, 22) % 5 < 2:
                tput(tx, ty, x, row, WATR[0])
                tput(tx, ty, x, row + 1, WATR[0])


def grass_tile(tx, ty, salt, detail=False, scrub=False):
    tfill(tx, ty, GRSR[1])
    speckle(tx, ty, GRSR[2], GRSR[0], salt)
    for i in range(5):  # sparse blade ticks — reads as distant turf
        bx, by = h2(i, salt, 11) % (T - 3), h2(salt, i, 12) % (T - 4)
        tput(tx, ty, bx, by, GRSR[0])
        tput(tx, ty, bx, by + 1, GRSR[0])
        tput(tx, ty, bx + 1, by + 2, GRSR[2])
    if detail:
        for i in range(4):
            fx, fy = 2 + h2(i, salt, 31) % (T - 4), 2 + h2(salt, i, 32) % (T - 4)
            col = FLW_W if i % 2 == 0 else FLW_P
            tput(tx, ty, fx, fy, col)
            tput(tx, ty, fx + 1, fy, col)
            tput(tx, ty, fx, fy + 1, (col[0] - 40, col[1] - 60, col[2] - 30, 255))
    if scrub:
        for (bx, by) in ((6, 8), (20, 18)):
            for dy in range(4):
                for dx in range(7):
                    if (dx in (0, 6)) and dy in (0, 3):
                        continue
                    tput(tx, ty, bx + dx, by + dy, BUSH)
            tput(tx, ty, bx, by, BUSH_L)          # lit top-left
            tput(tx, ty, bx + 1, by, BUSH_L)
            tput(tx, ty, bx + 1, by - 1, BUSH_L)
            tput(tx, ty, bx + 2, by - 1, BUSH_L)
            for dx in range(5):                    # cast shadow
                tput(tx, ty, bx + 1 + dx, by + 4, GRSR[2])


def forest_noise(tx, ty):
    """Shared canopy noise (same salt for A/B/edge so their seams match)."""
    for y in range(T):
        for x in range(T):
            r = h2(x // 2, y // 2, 40)
            if r < 18:
                c = LEAF_S
            elif r < 70:
                c = CANOPY[3]
            elif r < 200:
                c = CANOPY[2]
            else:
                c = CANOPY[1]
            tput(tx, ty, x, y, c)


def forest_clusters(tx, ty, domes):
    """Broccoli dome highlights, lit upper-left; kept off tile edges."""
    for (cx, cy, r) in domes:
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                d2 = dx * dx + dy * dy
                if d2 > r * r:
                    continue
                t = 0.28 + 0.55 * ((dx / r) * 0.55 + (dy / r) * 0.80) + 0.15 * d2 / (r * r)
                tput(tx, ty, cx + dx, cy + dy, pick(CANOPY, t, cx + dx, cy + dy, grain=2))
        for dx in range(-r, r + 1):  # crevice under each dome
            dy = int((r * r - dx * dx) ** 0.5)
            if h2(dx, cy, 41) % 3 != 0:
                tput(tx, ty, cx + dx, cy + dy + 1, LEAF_S)


def mountain_tile(tx, ty, snow=False):
    for y in range(T):
        for x in range(T):
            b = (x + y) % 16  # diagonal facets, period 16 wraps across 32px tiles
            if b < 4:
                c = MTN[0]
            elif b < 10:
                c = MTN[1]
            else:
                c = MTN[2]
            r = h2(x // 2, y // 2, 43)
            if r < 20:
                c = MTN[3]
            elif r > 240:
                c = MTN[0]
            if b <= 1 and h2(x, y, 44) < 90:
                c = (188, 178, 196, 255)  # ridge crest glints
            if snow:
                limit = 10 + h2(x, 0, 45) % 6
                if y < limit:
                    c = SNOW_D if b >= 10 else SNOW
                elif y == limit and h2(x, 1, 45) % 2 == 0:
                    c = SNOW_D  # ragged snow line
            tput(tx, ty, x, y, c)


def cracked_tile(tx, ty, salt):
    tfill(tx, ty, WSTR[1])
    speckle(tx, ty, WSTR[2], WSTR[0], salt)
    for i in range(3):  # meandering cracks, kept off the tile border
        x = 6 + h2(i, salt, 50) % 20
        y = 2 + h2(salt, i, 51) % 8
        for step in range(20):
            tput(tx, ty, x, y, CRACK)
            tput(tx, ty, x + 1, y, CRACK)
            if step % 3 == 2:
                tput(tx, ty, x + 2, y, CRACK_S)
            x = max(2, min(T - 4, x + h2(step, i, salt) % 3 - 1))
            y += 1
            if y > T - 5:
                break


# --- row 0 -----------------------------------------------------------------------
water_base(0, 0)
water_base(1, 0)
for (sx, sy) in ((6, 8), (20, 4), (14, 22), (24, 18)):   # sparkle crests
    tput(1, 0, sx, sy, SPARK)
    tput(1, 0, sx + 1, sy, SPARK_L)
    tput(1, 0, sx + 2, sy, SPARK_L)
    tput(1, 0, sx + 3, sy, SPARK)
    tput(1, 0, sx + 1, sy - 1, SPARK)
    tput(1, 0, sx + 2, sy + 1, SPARK)

tfill(2, 0, SNDR[1])
speckle(2, 0, SNDR[2], SNDR[0], 23)
for i in range(3):  # wind-ripple dashes
    rx, ry = h2(i, 5, 24) % (T - 8), 4 + h2(5, i, 25) % (T - 8)
    for dx in range(6):
        tput(2, 0, rx + dx, ry, SNDR[2])

grass_tile(3, 0, 26)
grass_tile(4, 0, 27, detail=True)
grass_tile(5, 0, 28, scrub=True)

tfill(6, 0, PTHR[1])
speckle(6, 0, PTHR[2], PTHR[0], 29, lo=14, hi=242)
for row in (10, 20):  # worn wheel ruts
    for x in range(T):
        if h2(x // 6, row, 30) % 4 < 2:
            tput(6, 0, x, row, PTHR[2])
for (cx, cy) in ((0, 0), (T - 2, 0), (0, T - 2), (T - 2, T - 2)):  # grassy nibbled corners
    for dx in range(2):
        for dy in range(2):
            tput(6, 0, cx + dx, cy + dy, GRSR[1])
    tput(6, 0, cx + (2 if cx == 0 else -1), cy + 1, GRSR[2])
    tput(6, 0, cx + 1, cy + (2 if cy == 0 else -1), GRSR[2])

water_base(7, 0)  # bridge: planks over open water
for y in range(4, 29):
    py = (y - 4) % 6
    for x in range(T):
        if py == 0:
            c = WOOD_L
        elif py == 5:
            c = WOOD_S
        elif py == 4:
            c = WOOD_D
        else:
            c = WOOD
        if py not in (4, 5) and h2(x // 2, y // 2, 33) < 26:
            c = WOOD_D  # grain flecks
        if py != 5 and (x + (y - 4) // 6 * 10) % 16 in (0, 1):
            c = WOOD_S  # staggered butt joints
        tput(7, 0, x, y, c)
for x in range(T):
    tput(7, 0, x, 29, WATR[2])  # bridge shadow on the water
    tput(7, 0, x, 30, WATR[2])

# --- row 1 -----------------------------------------------------------------------
forest_noise(0, 1)
forest_clusters(0, 1, ((8, 8, 6), (22, 12, 8), (12, 24, 6)))
forest_noise(1, 1)
forest_clusters(1, 1, ((22, 6, 6), (8, 18, 8), (24, 24, 6)))

# forest edge: canopy overhanging grass, trunk shadows in the gloom
grass_tile(2, 1, 34)
for y in range(0, 16):
    for x in range(T):
        r = h2(x // 2, y // 2, 40)
        tput(2, 1, x, y, LEAF_S if r < 18 else (CANOPY[3] if r < 70 else CANOPY[2]))
for x in range(T):
    if (x % 10) < 6:
        tput(2, 1, x, 16, CANOPY[3])  # scalloped canopy lip
        tput(2, 1, x, 17, CANOPY[3])
    tput(2, 1, x, 18, GRSR[2])        # cast shade line
    tput(2, 1, x, 19, GRSR[2])
for tx0 in (6, 20):
    for y in range(18, 22):
        tput(2, 1, tx0, y, LEAF_S)    # trunks receding into shadow
        tput(2, 1, tx0 + 1, y, LEAF_S)
        tput(2, 1, tx0 + 2, y, CANOPY[3])

grass_tile(3, 1, 35)
for (cx, cy, rx, ry) in ((10, 18, 8, 6), (22, 8, 6, 4)):  # low mounded hills
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny > 1.0:
                continue
            t = 0.30 + 0.45 * (nx * 0.55 + ny * 0.80)
            tput(3, 1, x, y, pick([GRSR[0], GRSR[1], GRSR[2], BUSH], t, x, y, grain=2))
    for x in range(cx - rx + 2, cx + rx - 1):
        tput(3, 1, x, cy + ry + 1, GRSR[2])  # settle shadow

mountain_tile(4, 1)
mountain_tile(5, 1, snow=True)

tfill(6, 1, RIVER)
speckle(6, 1, RIVER_D, RIVER, 36, lo=20, hi=256)
for col, phase in ((8, 0), (18, 12), (26, 22)):  # vertical flow ticks
    for y in range(T):
        if h2(col, (y + phase) // 8, 37) % 5 < 2:
            tput(6, 1, col, y, RIVER_L)
            tput(6, 1, col + 1, y, RIVER_L)

for y in range(T):  # cliff strata
    band = y % 8
    for x in range(T):
        if band <= 1:
            c = CLIFF[0]
        elif band >= 6:
            c = CLIFF[2]
        else:
            c = CLIFF[1]
        if h2(x // 2, y // 2, 38) < 26:
            c = CLIFF[3]
        tput(7, 1, x, y, c)

# --- row 2 (the violet drained wastes) --------------------------------------------
cracked_tile(0, 2, 52)
cracked_tile(1, 2, 53)

cracked_tile(2, 2, 54)  # dead tree on parched earth
for y in range(12, 28):
    tput(2, 2, 14, y, TRUNK)
    tput(2, 2, 15, y, TRUNK)
    tput(2, 2, 16, y, TRUNK_D)
    tput(2, 2, 17, y, TRUNK_D)
for (bx, by) in ((12, 10), (10, 8), (18, 10), (20, 8), (22, 6), (14, 8), (14, 6),
                 (13, 9), (11, 7), (19, 9), (21, 7), (15, 7)):
    tput(2, 2, bx, by, TRUNK_D)  # bare branches
    tput(2, 2, bx + 1, by, TRUNK_D)
for x in range(12, 21):
    tput(2, 2, x, 28, CRACK_S)   # root shadow
    tput(2, 2, x, 29, CRACK_S)

cracked_tile(3, 2, 55)  # crystal remnant — the one hot-violet glow on the map
for y in range(8, 24):
    if y < 18:
        half = min(4, (y - 7) // 2)
    else:
        half = max(0, 23 - y)
    for x in range(16 - half, 16 + half + 1):
        t = 0.25 + 0.5 * (x - 16 + half) / max(1, 2 * half) + 0.2 * (y - 8) / 16.0
        tput(3, 2, x, y, pick(CRYS, t, x, y, grain=2))
tput(3, 2, 14, 10, CRYS[0])  # glint
tput(3, 2, 15, 10, (246, 230, 255, 255))
tput(3, 2, 15, 11, CRYS[0])
for x in range(12, 21):
    tput(3, 2, x, 24, CRACK_S)

for i, tx in enumerate((4, 5, 6, 7)):  # reserved grass variants
    grass_tile(tx, 2, 60 + i)

img.save(os.path.join(HERE, "overworld_tiles.png"))


# ===== 2) chibi travel Basil (48px mini field sprite) =============================
BCELL, BCOLS, BROWS = OW_CELL, 4, 3
BCX = 24

FUR   = BASIL["FUR"]
COATR = BASIL["COATR"]
WHT   = BASIL["WHITE"]
EYE_Y = BASIL["EYE_Y"]
EARIN = BASIL["EARIN"]
NOSE  = BASIL["NOSE"]
GOG_RIM = BASIL["GOGRIM"][1]
GOG_LEN = BASIL["GOGLEN"][1]
WHISK = BASIL["WHISK"]
OUTS, OUT_FB = BASIL["OUTS"], BASIL["OUT_FALLBACK"]


def _ear(c, apex_x, apex_y, base_y, x0, x1, ramp_tone, inner=None):
    span = max(1, base_y - apex_y)
    for y in range(apex_y, base_y + 1):
        f = (y - apex_y) / span
        xl = round(apex_x + (x0 - apex_x) * f)
        xr = round(apex_x + (x1 - apex_x) * f)
        for x in range(min(xl, xr), max(xl, xr) + 1):
            c.set(x, y, ramp_tone)
    if inner:
        for y in range(apex_y + 2, base_y):
            f = (y - apex_y) / span
            xm = round(apex_x + ((x0 + x1) / 2 - apex_x) * f)
            c.set(xm, y, inner)


def draw_chibi(facing, f):
    c = Cell(BCELL, grain=2)
    bob = -2 if f % 2 == 1 else 0

    if facing in ("down", "up"):
        # legs: fwd foot reaches y=OW_FEET, trailing foot 2px up; bob lifts hips
        foot_l = OW_FEET if f == 0 else OW_FEET - 2
        foot_r = OW_FEET if f == 2 else OW_FEET - 2
        for (x0, foot) in ((19, foot_l), (26, foot_r)):
            for y in range(34 + bob, foot - 1):
                c.set(x0, y, FUR[2])
                c.set(x0 + 1, y, FUR[2])
                c.set(x0 + 2, y, FUR[3])
            c.rect(x0, foot - 1, x0 + 2, foot, WHT[1])
            c.set(x0, foot - 1, WHT[0])
        c.cloth(17, 28 + bob, 30, 36 + bob, COATR, round_=1)
        if facing == "up":  # tail curls out from under the coat back
            for (tx0, ty0) in ((30, 36), (32, 34), (33, 31), (33, 28)):
                c.rect(tx0, ty0 + bob, tx0 + 1, ty0 + 1 + bob, FUR[1])
        else:
            c.set(24, 30 + bob, COATR[3])   # placket hint
            c.set(24, 33 + bob, COATR[3])
        # sleeves + white paws breaking the silhouette
        for sx in (15, 31):
            c.rect(sx, 29 + bob, sx + 1, 32 + bob, COATR[2])
            c.rect(sx, 33 + bob, sx + 1, 34 + bob, WHT[1])
        c.oval(BCX, 21 + bob, 9.2, 7.8, FUR, power=2.2)
        _ear(c, 17, 10 + bob, 16 + bob, 14, 21, FUR[3], EARIN if facing == "down" else None)
        _ear(c, 31, 10 + bob, 16 + bob, 27, 34, FUR[3], EARIN if facing == "down" else None)
        for x in range(16, 33):  # goggle strap on the forehead
            c.set(x, 16 + bob, GOG_RIM)
            c.set(x, 17 + bob, GOG_RIM)
        if facing == "down":
            for gx in (19, 26):  # lenses
                c.rect(gx, 14 + bob, gx + 3, 15 + bob, GOG_LEN)
                c.set(gx, 14 + bob, (252, 240, 214, 255))
            c.rect(24, 19 + bob, 24, 24 + bob, WHT[0])  # blaze
            c.oval(BCX, 25.5 + bob, 4.2, 2.6, WHT, power=2.0)  # plump muzzle
            c.rect(23, 24 + bob, 25, 25 + bob, NOSE)
            for ex in (19, 27):  # 2x2 eyes with pupil
                c.rect(ex, 20 + bob, ex + 1, 21 + bob, EYE_Y)
                c.set(ex + 1, 21 + bob, (16, 12, 16, 255))
        else:
            c.rect(21, 24 + bob, 27, 25 + bob, FUR[3])  # neck fur part
    else:  # side, facing right
        if f == 0:
            pairs = ((18, OW_FEET), (26, OW_FEET))
        elif f == 2:
            pairs = ((20, OW_FEET), (24, OW_FEET - 2))
        else:
            pairs = ((22, OW_FEET),)
        for (x0, foot) in pairs:
            for y in range(34 + bob, foot - 1):
                c.set(x0, y, FUR[2])
                c.set(x0 + 1, y, FUR[2])
                c.set(x0 + 2, y, FUR[3])
            c.rect(x0, foot - 1, x0 + 2, foot, WHT[1])
            c.set(x0, foot - 1, WHT[0])
        for i, (tx0, ty0) in enumerate(((15, 30), (13, 28), (12, 26), (12, 24))):  # tail astern
            c.rect(tx0, ty0 + bob, tx0 + 1, ty0 + 1 + bob, FUR[1 if i == 3 else 2])
        c.cloth(17, 28 + bob, 28, 36 + bob, COATR, round_=1)
        c.rect(26, 29 + bob, 27, 32 + bob, COATR[2])  # front sleeve
        c.rect(26, 33 + bob, 27, 34 + bob, WHT[1])
        c.oval(26, 21 + bob, 8.8, 7.8, FUR, power=2.2)
        _ear(c, 21, 10 + bob, 16 + bob, 18, 25, FUR[3])          # back ear
        _ear(c, 30, 11 + bob, 16 + bob, 27, 34, FUR[2])          # front ear
        for x in range(19, 34):
            c.set(x, 16 + bob, GOG_RIM)
            c.set(x, 17 + bob, GOG_RIM)
        c.rect(28, 14 + bob, 31, 15 + bob, GOG_LEN)              # side lens
        c.set(28, 14 + bob, (252, 240, 214, 255))
        c.oval(32, 24 + bob, 3.4, 2.6, WHT, power=2.0)           # muzzle
        c.rect(34, 22 + bob, 35, 23 + bob, NOSE)
        c.rect(28, 20 + bob, 29, 21 + bob, EYE_Y)                # one eye
        c.set(29, 21 + bob, (16, 12, 16, 255))

    c.outline(OUTS, OUT_FB)
    if facing == "down":  # whiskers after the outline so they break the silhouette
        c.set(13, 24 + bob, WHISK)
        c.set(12, 25 + bob, WHISK)
        c.set(35, 24 + bob, WHISK)
        c.set(36, 25 + bob, WHISK)
    elif facing == "side":
        c.set(37, 25 + bob, WHISK)
        c.set(38, 26 + bob, WHISK)
    return c


chibi = Img(BCOLS * BCELL, BROWS * BCELL)
for row, facing in enumerate(("down", "up", "side")):
    for f in range(4):
        chibi.blit_cell(draw_chibi(facing, f), f * BCELL, row * BCELL)
chibi.save(os.path.join(HERE, "overworld_basil.png"))


# ===== 3) location icons (64px) ===================================================
ICELL = ICON

SHADOW  = (20, 18, 30, 110)
PLASTER = ramp4((214, 196, 214, 255), "violet", spread=0.8)   # lilac-warm plaster
TIMBER  = (110, 78, 96, 255)
ROOF    = [(128, 158, 158, 255), (104, 132, 136, 255), (82, 106, 114, 255), (60, 82, 92, 255)]
BRICK   = (162, 100, 108, 255)
BRICK_D = (126, 74, 86, 255)
GLASS   = (150, 184, 208, 255)
GLASS_L = (202, 226, 238, 255)
SMOKE   = (208, 204, 216, 165)
ROOF_R  = [(190, 108, 108, 255), (162, 84, 90, 255), (128, 62, 76, 255), (96, 46, 64, 255)]
SLATE   = [(140, 142, 166, 255), (114, 116, 140, 255), (88, 90, 114, 255), (64, 66, 88, 255)]
FLAG    = (222, 88, 118, 255)
ROCKR   = [(162, 150, 156, 255), (132, 120, 132, 255), (102, 90, 108, 255), (74, 64, 84, 255)]
CAVE_IN = (18, 14, 26, 255)
CAVE_D  = (8, 6, 14, 255)
OBSL    = [(100, 94, 120, 255), (78, 72, 96, 255), (60, 54, 76, 255), (42, 36, 56, 255)]
RUNE    = (150, 112, 182, 255)
RUNE_L  = (198, 162, 224, 255)


def shadow_ellipse(c, cx, cy, rx, ry):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1.0:
                c.set(x, y, SHADOW)


def _roof_tri(c, apex_x, apex_y, base_y, overhang, ramp):
    for y in range(apex_y, base_y + 1):
        half = (y - apex_y) + overhang
        for x in range(apex_x - half, apex_x + half + 1):
            t = 0.25 + 0.5 * (x - (apex_x - half)) / max(1, 2 * half) + 0.25 * (y - apex_y) / max(1, base_y - apex_y)
            c.set(x, y, pick(ramp, t, x, y, grain=2))


def icon_home():
    c = Cell(ICELL, grain=2)
    shadow_ellipse(c, 32, 56, 22, 6)
    c.cloth(18, 34, 46, 54, PLASTER, round_=0)           # plastered walls
    for x in range(18, 47):
        c.set(x, 54, PLASTER[3])
        c.set(x, 55, PLASTER[3])
    for y in range(34, 56):                              # timber corner posts
        c.rect(18, y, 19, y, TIMBER)
        c.rect(45, y, 46, y, TIMBER)
    for y in range(42, 56):                              # plank door
        c.set(28, y, WOOD_L)
        c.rect(29, y, 32, y, WOOD)
        c.rect(33, y, 34, y, WOOD_D)
    c.rect(33, 48, 34, 49, PLASTER[0])                   # knob
    for (wx, wy) in ((39, 40),):                         # round window
        c.rect(wx, wy, wx + 3, wy + 3, GLASS)
        c.set(wx, wy, GLASS_L)
        c.set(wx + 1, wy, GLASS_L)
        c.set(wx, wy + 1, GLASS_L)
        c.set(wx + 3, wy + 3, SLATE[3])
    _roof_tri(c, 32, 16, 33, 2, ROOF)                    # teal shingle roof
    for x in range(12, 53):
        c.set(x, 32, ROOF[3])
        c.set(x, 33, ROOF[3])                            # eave line
    c.rect(31, 14, 33, 15, ROOF[0])                      # ridge cap
    for y in range(18, 28):                              # crooked chimney
        c.rect(42, y, 44, y, BRICK)
        c.set(45, y, BRICK_D)
    c.rect(42, 18, 45, 18, PLASTER[1])
    for (sx, sy) in ((48, 14), (50, 10), (48, 6), (49, 5)):  # smoke wisp
        c.rect(sx, sy, sx + 1, sy + 1, SMOKE)
    c.outline({}, OBSL[3])
    return c


def icon_town():
    c = Cell(ICELL, grain=2)
    shadow_ellipse(c, 32, 56, 26, 6)
    c.cloth(8, 36, 26, 54, PLASTER, round_=0, sh=0.15)   # back house
    _roof_tri(c, 16, 28, 37, 2, ROOF_R)
    c.cloth(26, 40, 42, 54, PLASTER, round_=0)           # front house
    _roof_tri(c, 34, 32, 41, 1, SLATE)
    for (wx, wy) in ((14, 42), (20, 42), (32, 46), (36, 46)):
        c.rect(wx, wy, wx + 1, wy + 2, SLATE[3])         # dark windows
    c.cloth(46, 20, 56, 54, PLASTER, round_=0)           # clock tower
    _roof_tri(c, 51, 14, 21, 1, SLATE)
    c.rect(50, 28, 53, 31, GLASS)                        # clock face
    c.set(50, 28, GLASS_L)
    c.set(51, 28, GLASS_L)
    c.set(50, 29, GLASS_L)
    c.set(52, 30, SLATE[3])                              # hands
    c.set(52, 31, SLATE[3])
    for y in range(6, 14):
        c.set(51, y, SLATE[3])                           # flag pole
    for x in range(52, 58):
        c.rect(x, 6, x, 8, FLAG)
    c.outline({}, OBSL[3])
    return c


def icon_meadow():
    c = Cell(ICELL, grain=2)
    shadow_ellipse(c, 20, 56, 12, 4)
    shadow_ellipse(c, 44, 56, 12, 4)
    for y in range(44, 56):                              # trunks
        c.rect(18, y, 19, y, WOOD)
        c.rect(20, y, 21, y, WOOD_D)
    for y in range(48, 56):
        c.rect(42, y, 43, y, WOOD)
        c.rect(44, y, 45, y, WOOD_D)
    c.oval(20, 32, 12.4, 10.8, CANOPY, power=2.0)        # puffy crowns
    c.oval(26, 38, 6.8, 5.6, CANOPY, power=2.0, sh=0.18)
    c.oval(44, 38, 10.0, 8.8, CANOPY, power=2.0)
    for (fx, fy, col) in ((30, 54, FLW_W), (34, 52, FLW_P), (26, 52, FLW_P), (38, 54, FLW_W)):
        c.rect(fx, fy, fx + 1, fy, col)
        c.set(fx, fy + 1, (col[0] - 40, col[1] - 60, col[2] - 30, 255))
    c.outline({}, OBSL[3])
    return c


def icon_cave():
    c = Cell(ICELL, grain=2)
    shadow_ellipse(c, 32, 56, 24, 6)
    c.oval(32, 40, 24.0, 17.2, ROCKR, power=2.0)         # rocky knoll
    for (gx, gy) in ((16, 26), (24, 22), (40, 24), (48, 28)):
        c.rect(gx, gy, gx + 1, gy, GRSR[2])              # scrub on the crown
        c.rect(gx + 2, gy, gx + 3, gy, GRSR[1])
    for y in range(38, 56):                              # cave mouth arch
        half = 8 if y >= 44 else y - 36
        for x in range(32 - half, 32 + half + 1):
            c.set(x, y, CAVE_D if abs(x - 32) < half - 2 and y > 40 else CAVE_IN)
    for y in range(38, 56):                              # lit rim
        half = 8 if y >= 44 else y - 36
        c.set(32 - half - 1, y, ROCKR[0])
        c.set(32 - half - 2, y, ROCKR[0])
        c.set(32 + half + 1, y, ROCKR[3])
        c.set(32 + half + 2, y, ROCKR[3])
    c.outline({}, OBSL[3])
    return c


def icon_obelisk():
    c = Cell(ICELL, grain=2)
    shadow_ellipse(c, 32, 56, 18, 6)
    for y in range(12, 56):                              # leaning monolith
        lean = (55 - y) // 6
        half = 4 if y > 24 else 2
        xc = 30 + lean
        for x in range(xc - half, xc + half + 1):
            t = 0.25 + 0.55 * (x - (xc - half)) / max(1, 2 * half) + 0.1 * (y - 12) / 43.0
            c.set(x, y, pick(OBSL, t, x, y, grain=2))
    c.rect(36, 10, 37, 11, OBSL[1])                      # chipped tip
    for (kx, ky) in ((30, 24), (31, 26), (30, 28), (31, 30), (30, 32), (31, 34)):
        c.set(kx, ky, OBSL[3])                           # the great crack
        c.set(kx + 1, ky, OBSL[3])
    for (rx2, ry2) in ((32, 18), (30, 36), (30, 44)):
        c.rect(rx2, ry2, rx2 + 1, ry2 + 1, RUNE)         # dull runes
    c.rect(34, 16, 35, 16, RUNE_L)                       # one faint live glint
    c.outline({}, OBSL[3])
    return c


icons = Img(ICELL * 5, ICELL)
for i, fn in enumerate((icon_home, icon_town, icon_meadow, icon_cave, icon_obelisk)):
    icons.blit_cell(fn(), i * ICELL, 0)
icons.save(os.path.join(HERE, "overworld_icons.png"))
