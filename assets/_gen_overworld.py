#!/usr/bin/env python3
"""Overworld art for the Chrono Trigger / Sea of Stars travel layer.

Generates three sheets (referenced by hand-authored .tres/.tscn files — the
layouts are contracts, keep them stable):

  overworld_tiles.png  128x48 — 8x3 atlas of 16x16 seamless terrain tiles:
    (0,0) water          (1,0) water sparkle   (2,0) sand         (3,0) grass
    (4,0) grass detail   (5,0) scrub           (6,0) path         (7,0) bridge
    (0,1) forest A       (1,1) forest B        (2,1) forest edge  (3,1) hills
    (4,1) mountain       (5,1) snow peak       (6,1) river        (7,1) cliff
    (0,2) cracked A      (1,2) cracked B       (2,2) dead tree    (3,2) crystal
    (4,2)-(7,2) reserved grass variants
  overworld_basil.png  96x72 — 4x3 grid of 24x24 cells: chibi travel-scale
    Basil (big head, goggles, lab coat). row0 walk_down, row1 walk_up,
    row2 walk_side (faces RIGHT; code mirrors). Frames 0/2 are contact poses,
    1/3 passing poses with a 1px bob. Feet baseline y=21, centered on x=12.
  overworld_icons.png  160x32 — five 32x32 landmark icons over ground-shadow
    ellipses, base y~28: 0 home cottage · 1 town · 2 meadow grove ·
    3 cave mouth · 4 obelisk.

Muted SNES palette, 4-tone ramps (shadows shift cool), light from the upper
left, hash-dithered detail, deterministic (no random). The cracked / dead-tree
/ crystal tiles are the magic-drained wastes biome east of the river.

Re-run: python3 assets/_gen_overworld.py
"""
import struct, zlib, os

HERE = os.path.dirname(os.path.abspath(__file__))


def h2(x, y, salt=0):
    n = (x * 374761393 + y * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return (n ^ (n >> 16)) & 0xFF


def pick(ramp, t, x, y):
    """t in 0..1 (0 = lit, 1 = shadow) -> ramp tone, dithered at band edges."""
    b = max(0.0, min(2.999, t * 3.0))
    i = int(b)
    frac = b - i
    if frac > 0.58 or (0.45 < frac <= 0.58 and (x + y) % 2 == 0):
        i += 1
    return ramp[min(3, i)]


def write_png(name, w, h, buf):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += buf[y * w * 4:(y + 1) * w * 4]

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    dst = os.path.join(HERE, name)
    open(dst, "wb").write(png)
    print(f"wrote {name} ({w}x{h})")


# ===== 1) terrain tiles ==========================================================
T, TCOLS, TROWS = 16, 8, 3
TW, TH = TCOLS * T, TROWS * T
tiles = bytearray(TW * TH * 4)

WATER    = (38, 64, 102, 255)
WATER_D  = (30, 52, 88, 255)
WATER_R  = (56, 88, 128, 255)    # ripple band
SPARK    = (168, 204, 224, 255)
SPARK_L  = (214, 234, 242, 255)
RIVER    = (70, 110, 146, 255)
RIVER_D  = (56, 94, 132, 255)
RIVER_L  = (98, 140, 170, 255)
SAND     = (216, 196, 150, 255)
SAND_D   = (192, 170, 126, 255)
SAND_L   = (232, 214, 172, 255)
GRASS    = (92, 148, 84, 255)    # more muted / distant than the zone meadow
GRASS_D  = (68, 122, 80, 255)    # teal-shifted shadow
GRASS_L  = (118, 170, 94, 255)
FLW_W    = (238, 238, 228, 255)
FLW_Y    = (224, 190, 90, 255)
BUSH     = (48, 100, 70, 255)
BUSH_L   = (74, 128, 82, 255)
PATHC    = (188, 152, 106, 255)
PATH_D   = (160, 126, 86, 255)
PATH_L   = (206, 174, 124, 255)
WOOD     = (150, 110, 72, 255)
WOOD_D   = (118, 84, 56, 255)
WOOD_L   = (176, 136, 92, 255)
WOOD_S   = (86, 60, 42, 255)     # plank gaps / grain
CANOPY   = [(108, 160, 88, 255), (86, 140, 80, 255), (52, 102, 66, 255), (34, 74, 52, 255)]
LEAF_S   = (24, 56, 42, 255)     # deepest crevice
MTN      = (128, 118, 110, 255)
MTN_D    = (100, 90, 88, 255)
MTN_D2   = (76, 68, 70, 255)
MTN_L    = (156, 146, 132, 255)
MTN_LL   = (176, 166, 150, 255)
SNOW     = (232, 236, 240, 255)
SNOW_D   = (198, 208, 220, 255)
CLIFF    = (104, 96, 96, 255)
CLIFF_D  = (80, 72, 76, 255)
CLIFF_L  = (126, 118, 114, 255)
CLIFF_S  = (60, 54, 60, 255)
CRACKED  = (160, 142, 116, 255)
CRACK_D  = (136, 118, 96, 255)
CRACK_L  = (178, 162, 134, 255)
CRACK    = (92, 76, 64, 255)
CRACK_S  = (70, 56, 48, 255)
TRUNK    = (74, 56, 44, 255)
TRUNK_D  = (52, 38, 32, 255)
CRYS     = [(216, 206, 228, 255), (166, 146, 186, 255), (134, 112, 158, 255), (100, 82, 124, 255)]


def tput(tx, ty, x, y, c):
    if 0 <= x < T and 0 <= y < T:
        o = ((ty * T + y) * TW + (tx * T + x)) * 4
        tiles[o:o + 4] = bytes(c)


def tfill(tx, ty, c):
    for y in range(T):
        for x in range(T):
            tput(tx, ty, x, y, c)


def speckle(tx, ty, dark, light, salt, lo=24, hi=234):
    for y in range(T):
        for x in range(T):
            r = h2(x, y, salt)
            if r < lo:
                tput(tx, ty, x, y, dark)
            elif r > hi:
                tput(tx, ty, x, y, light)


def water_base(tx, ty):
    tfill(tx, ty, WATER)
    speckle(tx, ty, WATER_D, WATER, 21, lo=20, hi=256)
    # dashed ripple bands, phase-shifted per row
    for row, phase in ((3, 0), (8, 5), (13, 10)):
        for x in range(T):
            if h2((x + phase) // 4, row, 22) % 5 < 2:
                tput(tx, ty, x, row, WATER_R)


def grass_tile(tx, ty, salt, detail=False, scrub=False):
    tfill(tx, ty, GRASS)
    speckle(tx, ty, GRASS_D, GRASS_L, salt)
    for i in range(3):  # sparse blade ticks — reads as distant turf
        bx, by = h2(i, salt, 11) % (T - 2), h2(salt, i, 12) % (T - 3)
        tput(tx, ty, bx, by, GRASS_L)
        tput(tx, ty, bx + 1, by + 1, GRASS_D)
    if detail:
        for i in range(4):
            fx, fy = 1 + h2(i, salt, 31) % (T - 2), 1 + h2(salt, i, 32) % (T - 2)
            tput(tx, ty, fx, fy, FLW_W if i % 2 == 0 else FLW_Y)
    if scrub:
        for (bx, by) in ((3, 4), (10, 9)):
            for dx in range(3):
                tput(tx, ty, bx + dx, by, BUSH)
                tput(tx, ty, bx + dx, by + 1, BUSH)
            tput(tx, ty, bx, by, BUSH_L)          # lit top-left
            tput(tx, ty, bx + 1, by - 1, BUSH_L)
            tput(tx, ty, bx + 2, by + 2, GRASS_D)  # cast shadow


def forest_noise(tx, ty):
    """Shared canopy noise (same salt for A/B/edge so their seams match)."""
    for y in range(T):
        for x in range(T):
            r = h2(x, y, 40)
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
                tput(tx, ty, cx + dx, cy + dy, pick(CANOPY, t, cx + dx, cy + dy))
        for dx in range(-r, r + 1):  # crevice under each dome
            dy = int((r * r - dx * dx) ** 0.5)
            if h2(dx, cy, 41) % 3 != 0:
                tput(tx, ty, cx + dx, cy + dy + 1, LEAF_S)


def mountain_tile(tx, ty, snow=False):
    for y in range(T):
        for x in range(T):
            b = (x + y) % 8  # diagonal facets, period 8 wraps across 16px tiles
            if b < 2:
                c = MTN_L
            elif b < 5:
                c = MTN
            else:
                c = MTN_D
            r = h2(x, y, 43)
            if r < 20:
                c = MTN_D2
            elif r > 240:
                c = MTN_LL
            if b == 0 and h2(x, y, 44) < 90:
                c = MTN_LL  # ridge crest glints
            if snow:
                limit = 5 + h2(x, 0, 45) % 3
                if y < limit:
                    c = SNOW_D if b >= 5 else SNOW
                elif y == limit and h2(x, 1, 45) % 2 == 0:
                    c = SNOW_D  # ragged snow line
            tput(tx, ty, x, y, c)


def cracked_tile(tx, ty, salt):
    tfill(tx, ty, CRACKED)
    speckle(tx, ty, CRACK_D, CRACK_L, salt)
    for i in range(3):  # meandering cracks, kept off the tile border
        x = 3 + h2(i, salt, 50) % 10
        y = 1 + h2(salt, i, 51) % 4
        for step in range(10):
            tput(tx, ty, x, y, CRACK)
            if step % 3 == 2:
                tput(tx, ty, x + 1, y, CRACK_S)
            x = max(1, min(T - 2, x + h2(step, i, salt) % 3 - 1))
            y += 1
            if y > T - 3:
                break


# --- row 0 -----------------------------------------------------------------------
water_base(0, 0)
water_base(1, 0)
for (sx, sy) in ((3, 4), (10, 2), (7, 11), (12, 9)):   # sparkle crests
    tput(1, 0, sx, sy, SPARK)
    tput(1, 0, sx + 1, sy, SPARK_L)
    tput(1, 0, sx + 2, sy, SPARK)

tfill(2, 0, SAND)
speckle(2, 0, SAND_D, SAND_L, 23)
for i in range(3):  # wind-ripple dashes
    rx, ry = h2(i, 5, 24) % (T - 4), 2 + h2(5, i, 25) % (T - 4)
    for dx in range(3):
        tput(2, 0, rx + dx, ry, SAND_D)

grass_tile(3, 0, 26)
grass_tile(4, 0, 27, detail=True)
grass_tile(5, 0, 28, scrub=True)

tfill(6, 0, PATHC)
speckle(6, 0, PATH_D, PATH_L, 29)
for row in (5, 10):  # worn wheel ruts
    for x in range(T):
        if h2(x // 3, row, 30) % 4 < 2:
            tput(6, 0, x, row, PATH_D)
for (cx, cy) in ((0, 0), (T - 1, 0), (0, T - 1), (T - 1, T - 1)):  # grassy nibbled corners
    tput(6, 0, cx, cy, GRASS)
    tput(6, 0, cx + (1 if cx == 0 else -1), cy, GRASS_D)
    tput(6, 0, cx, cy + (1 if cy == 0 else -1), GRASS_D)

water_base(7, 0)  # bridge: planks over open water
for y in range(2, 14):
    py = (y - 2) % 3
    for x in range(T):
        c = WOOD_L if py == 0 else (WOOD_S if py == 2 else WOOD)
        if py != 2 and h2(x, y, 33) < 26:
            c = WOOD_D  # grain flecks
        if py != 2 and (x + (y - 2) // 3 * 5) % 8 == 0:
            c = WOOD_S  # staggered butt joints
        tput(7, 0, x, y, c)
for x in range(T):
    tput(7, 0, x, 14, WATER_D)  # bridge shadow on the water

# --- row 1 -----------------------------------------------------------------------
forest_noise(0, 1)
forest_clusters(0, 1, ((4, 4, 3), (11, 6, 4), (6, 12, 3)))
forest_noise(1, 1)
forest_clusters(1, 1, ((11, 3, 3), (4, 9, 4), (12, 12, 3)))

# forest edge: canopy overhanging grass, trunk shadows in the gloom
grass_tile(2, 1, 34)
for y in range(0, 8):
    for x in range(T):
        r = h2(x, y, 40)
        tput(2, 1, x, y, LEAF_S if r < 18 else (CANOPY[3] if r < 70 else CANOPY[2]))
for x in range(T):
    if (x % 5) < 3:
        tput(2, 1, x, 8, CANOPY[3])  # scalloped canopy lip
    tput(2, 1, x, 9, GRASS_D)        # cast shade line
for tx0 in (3, 10):
    for y in (9, 10):
        tput(2, 1, tx0, y, LEAF_S)   # trunks receding into shadow
        tput(2, 1, tx0 + 1, y, CANOPY[3])

grass_tile(3, 1, 35)
for (cx, cy, rx, ry) in ((5, 9, 4, 3), (11, 4, 3, 2)):  # low mounded hills
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny > 1.0:
                continue
            t = 0.30 + 0.45 * (nx * 0.55 + ny * 0.80)
            tput(3, 1, x, y, pick([GRASS_L, GRASS, GRASS_D, BUSH], t, x, y))
    for x in range(cx - rx + 1, cx + rx):
        tput(3, 1, x, cy + ry + 1, GRASS_D)  # settle shadow

mountain_tile(4, 1)
mountain_tile(5, 1, snow=True)

tfill(6, 1, RIVER)
speckle(6, 1, RIVER_D, RIVER, 36, lo=20, hi=256)
for col, phase in ((4, 0), (9, 6), (13, 11)):  # vertical flow ticks
    for y in range(T):
        if h2(col, (y + phase) // 4, 37) % 5 < 2:
            tput(6, 1, col, y, RIVER_L)

for y in range(T):  # cliff strata
    band = y % 4
    for x in range(T):
        c = CLIFF_L if band == 0 else (CLIFF_D if band == 3 else CLIFF)
        if h2(x, y, 38) < 26:
            c = CLIFF_S
        tput(7, 1, x, y, c)

# --- row 2 -----------------------------------------------------------------------
cracked_tile(0, 2, 52)
cracked_tile(1, 2, 53)

cracked_tile(2, 2, 54)  # dead tree on parched earth
for y in range(6, 14):
    tput(2, 2, 7, y, TRUNK)
    tput(2, 2, 8, y, TRUNK_D)
for (bx, by) in ((6, 5), (5, 4), (9, 5), (10, 4), (11, 3), (7, 4), (7, 3)):
    tput(2, 2, bx, by, TRUNK_D)  # bare branches
for x in range(6, 11):
    tput(2, 2, x, 14, CRACK_S)   # root shadow

cracked_tile(3, 2, 55)  # dull crystal remnant
for y in range(4, 12):
    half = min(2, (y - 3) // 2) if y < 9 else max(0, 11 - y)
    for x in range(8 - half, 8 + half + 1):
        t = 0.25 + 0.5 * ((x - 8 + half) / max(1, 2 * half)) + 0.2 * (y - 4) / 8.0
        tput(3, 2, x, y, pick(CRYS, t, x, y))
tput(3, 2, 7, 5, CRYS[0])  # glint
for x in range(6, 11):
    tput(3, 2, x, 12, CRACK_S)

for i, tx in enumerate((4, 5, 6, 7)):  # reserved grass variants
    grass_tile(tx, 2, 60 + i)

write_png("overworld_tiles.png", TW, TH, tiles)


# ===== 2) chibi travel Basil =====================================================
BCELL, BCOLS, BROWS = 24, 4, 3
BW, BH = BCOLS * BCELL, BROWS * BCELL

FUR   = [(78, 74, 96, 255), (52, 50, 66, 255), (34, 32, 46, 255), (20, 18, 30, 255)]
COATR = [(236, 236, 238, 255), (204, 204, 210, 255), (166, 166, 178, 255), (126, 126, 142, 255)]
WHT   = [(250, 248, 242, 255), (228, 224, 216, 255), (198, 194, 192, 255), (162, 158, 166, 255)]
EYE_Y   = (224, 188, 70, 255)
EARIN   = (204, 116, 134, 255)
NOSE    = (28, 22, 26, 255)
GOG_RIM = (112, 78, 50, 255)
GOG_LEN = (206, 178, 132, 255)
WHISK   = (216, 214, 208, 235)
OUT_DARK  = (8, 6, 14, 255)
OUT_LIGHT = (58, 56, 72, 255)
LIGHT_SET = set(COATR) | set(WHT) | {GOG_LEN}


class CellImg:
    def __init__(self, n):
        self.n = n
        self.px = [[None] * n for _ in range(n)]

    def set(self, x, y, c):
        if 0 <= x < self.n and 0 <= y < self.n:
            self.px[y][x] = c

    def get(self, x, y):
        if 0 <= x < self.n and 0 <= y < self.n:
            return self.px[y][x]
        return None

    def dome(self, cx, cy, rx, ry, ramp, power=2.2, sh=0.0):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                d = abs(nx) ** power + abs(ny) ** power
                if d > 1.0:
                    continue
                t = 0.40 + 0.28 * (nx * 0.55 + ny * 0.80) + 0.25 * d * d + sh
                self.set(x, y, pick(ramp, t, x, y))

    def panel(self, x0, y0, x1, y1, ramp, sh=0.0):
        w, h = max(1, x1 - x0), max(1, y1 - y0)
        for y in range(y0, y1 + 1):
            vy = (y - y0) / h
            for x in range(x0, x1 + 1):
                if min(x - x0, x1 - x) + min(y - y0, y1 - y) < 1:
                    continue
                t = 0.25 + 0.30 * (x - x0) / w + 0.35 * vy + sh
                self.set(x, y, pick(ramp, t, x, y))

    def outline(self):
        edge = []
        for y in range(self.n):
            for x in range(self.n):
                if self.px[y][x] is not None:
                    continue
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    p = self.get(nx, ny)
                    if p and p[3] == 255 and p not in (OUT_DARK, OUT_LIGHT):
                        edge.append((x, y, OUT_LIGHT if p in LIGHT_SET else OUT_DARK))
                        break
        for x, y, c in edge:
            self.px[y][x] = c

    def blit(self, buf, bufw, ox, oy):
        for y in range(self.n):
            for x in range(self.n):
                p = self.px[y][x]
                if p is None:
                    continue
                o = ((oy + y) * bufw + (ox + x)) * 4
                buf[o:o + 4] = bytes(p)


def _legs_vertical(c, f):
    """Down/up rows: fwd foot reaches y=21, trailing foot y=20; bob lifts hips."""
    bob = -1 if f % 2 == 1 else 0
    foot_l = 21 if f == 0 else 20
    foot_r = 21 if f == 2 else 20
    for (x0, foot) in ((10, foot_l), (13, foot_r)):
        for y in range(17 + bob, foot):
            c.set(x0, y, FUR[2])
            c.set(x0 + 1, y, FUR[3])
        c.set(x0, foot, WHT[0])
        c.set(x0 + 1, foot, WHT[1])


def _ears(c, bob, inner):
    for r, xs in ((5, (8,)), (6, (8, 9)), (7, (8, 9, 10))):
        for x in xs:
            c.set(x, r + bob, FUR[2] if x == xs[-1] else FUR[3])
    for r, xs in ((5, (16,)), (6, (15, 16)), (7, (14, 15, 16))):
        for x in xs:
            c.set(x, r + bob, FUR[2] if x == xs[0] else FUR[3])
    if inner:
        c.set(9, 7 + bob, EARIN)
        c.set(15, 7 + bob, EARIN)


def draw_chibi(facing, f):
    c = CellImg(BCELL)
    bob = -1 if f % 2 == 1 else 0

    if facing in ("down", "up"):
        _legs_vertical(c, f)
        c.panel(9, 14 + bob, 15, 18 + bob, COATR)
        if facing == "up":  # tail curls out from under the coat back
            for (tx0, ty0) in ((15, 18), (16, 17), (17, 16), (17, 15)):
                c.set(tx0, ty0 + bob, FUR[1])
        # sleeves + white paws breaking the silhouette
        for sx in (8, 16):
            c.set(sx, 15 + bob, COATR[2])
            c.set(sx, 16 + bob, COATR[3])
            c.set(sx, 17 + bob, WHT[1])
        c.dome(12, 11 + bob, 4.6, 3.9, FUR)
        _ears(c, bob, inner=(facing == "down"))
        for x in range(9, 16):  # goggle strap on the forehead
            c.set(x, 8 + bob, GOG_RIM)
        if facing == "down":
            c.set(10, 7 + bob, GOG_LEN)
            c.set(11, 7 + bob, GOG_LEN)
            c.set(13, 7 + bob, GOG_LEN)
            c.set(14, 7 + bob, GOG_LEN)
            c.set(12, 11 + bob, WHT[0])  # blaze
            c.set(12, 12 + bob, WHT[0])
            for x in (11, 12, 13):       # plump muzzle
                c.set(x, 13 + bob, WHT[1])
            c.set(12, 13 + bob, NOSE)
            c.set(10, 11 + bob, EYE_Y)
            c.set(14, 11 + bob, EYE_Y)
    else:  # side, facing right
        bobp = bob
        if f == 0:
            pairs = ((9, 21), (13, 21))
        elif f == 2:
            pairs = ((10, 21), (12, 20))
        else:
            pairs = ((11, 21),)
        for (x0, foot) in pairs:
            for y in range(17 + bobp, foot):
                c.set(x0, y, FUR[2])
                c.set(x0 + 1, y, FUR[3])
            c.set(x0, foot, WHT[0])
            c.set(x0 + 1, foot, WHT[1])
        for (tx0, ty0) in ((8, 15), (7, 14), (6, 13), (6, 12)):  # tail astern
            c.set(tx0, ty0 + bobp, FUR[1])
        c.panel(9, 14 + bobp, 14, 18 + bobp, COATR)
        c.set(13, 15 + bobp, COATR[2])  # front sleeve
        c.set(13, 16 + bobp, COATR[3])
        c.set(13, 17 + bobp, WHT[1])
        c.dome(13, 11 + bobp, 4.4, 3.9, FUR)
        for r, xs in ((5, (10,)), (6, (10, 11)), (7, (10, 11, 12))):  # back ear
            for x in xs:
                c.set(x, r + bobp, FUR[3])
        for r, xs in ((5, (15,)), (6, (14, 15)), (7, (13, 14, 15))):  # front ear
            for x in xs:
                c.set(x, r + bobp, FUR[2])
        for x in range(10, 17):
            c.set(x, 8 + bobp, GOG_RIM)
        c.set(14, 7 + bobp, GOG_LEN)
        c.set(15, 7 + bobp, GOG_LEN)
        for (mx, my) in ((16, 11), (17, 11), (16, 12), (17, 12), (16, 13)):  # muzzle blaze
            c.set(mx, my + bobp, WHT[0] if my == 11 else WHT[1])
        c.set(17, 12 + bobp, NOSE)
        c.set(14, 10 + bobp, EYE_Y)

    c.outline()
    if facing == "down":  # whiskers after the outline so they break the silhouette
        c.set(7, 12 + bob, WHISK)
        c.set(17, 12 + bob, WHISK)
    elif facing == "side":
        c.set(18, 13 + bob, WHISK)
    return c


basil = bytearray(BW * BH * 4)
for row, facing in enumerate(("down", "up", "side")):
    for f in range(4):
        draw_chibi(facing, f).blit(basil, BW, f * BCELL, row * BCELL)
write_png("overworld_basil.png", BW, BH, basil)


# ===== 3) location icons =========================================================
ICELL, ICONS = 32, 5
IW, IH = ICELL * ICONS, ICELL

SHADOW  = (20, 18, 30, 110)
PLASTER = [(226, 214, 190, 255), (206, 192, 166, 255), (178, 164, 140, 255), (144, 130, 112, 255)]
TIMBER  = (110, 84, 60, 255)
ROOF    = [(128, 152, 152, 255), (104, 128, 130, 255), (82, 104, 108, 255), (60, 80, 86, 255)]
BRICK   = (150, 100, 86, 255)
BRICK_D = (118, 76, 66, 255)
GLASS   = (150, 180, 200, 255)
GLASS_L = (198, 220, 232, 255)
SMOKE   = (204, 204, 212, 165)
ROOF_R  = [(178, 108, 84, 255), (152, 84, 68, 255), (122, 64, 54, 255), (92, 48, 44, 255)]
SLATE   = [(134, 140, 156, 255), (110, 116, 132, 255), (86, 92, 108, 255), (64, 68, 84, 255)]
FLAG    = (196, 84, 92, 255)
ROCKR   = [(156, 146, 132, 255), (128, 118, 110, 255), (100, 90, 88, 255), (76, 68, 70, 255)]
CAVE_IN = (16, 14, 22, 255)
CAVE_D  = (8, 6, 12, 255)
OBSL    = [(96, 92, 112, 255), (74, 70, 88, 255), (58, 54, 70, 255), (40, 36, 52, 255)]
RUNE    = (134, 112, 158, 255)
RUNE_L  = (176, 158, 196, 255)


def shadow_ellipse(c, cx, cy, rx, ry):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny <= 1.0:
                c.set(x, y, SHADOW)


def icon_home():
    c = CellImg(ICELL)
    shadow_ellipse(c, 16, 28, 11, 3)
    c.panel(9, 17, 23, 27, PLASTER)                      # plastered walls
    for x in range(9, 24):
        c.set(x, 27, PLASTER[3])
    for y in range(17, 28):                              # timber corner posts
        c.set(9, y, TIMBER)
        c.set(23, y, TIMBER)
    for y in range(21, 28):                              # plank door
        c.set(14, y, WOOD_L)
        c.set(15, y, WOOD)
        c.set(16, y, WOOD)
        c.set(17, y, WOOD_D)
    c.set(16, 24, PLASTER[0])                            # knob
    c.set(20, 20, GLASS_L)                               # round window
    c.set(21, 20, GLASS)
    c.set(20, 21, GLASS)
    c.set(21, 21, GLASS)
    for y in range(8, 17):                               # teal shingle roof
        half = y - 6
        for x in range(16 - half, 16 + half + 1):
            t = 0.25 + 0.5 * (x - (16 - half)) / max(1, 2 * half) + 0.25 * (y - 8) / 9.0
            c.set(x, y, pick(ROOF, t, x, y))
    for x in range(6, 27):
        c.set(x, 16, ROOF[3])                            # eave line
    c.set(16, 7, ROOF[0])                                # ridge cap
    for y in range(9, 14):                               # crooked chimney
        c.set(21, y, BRICK)
        c.set(22, y, BRICK)
        c.set(23, y, BRICK_D)
    c.set(21, 9, PLASTER[1])
    for (sx, sy) in ((24, 7), (25, 5), (24, 3)):         # smoke wisp
        c.set(sx, sy, SMOKE)
    c.outline()
    return c


def icon_town():
    c = CellImg(ICELL)
    shadow_ellipse(c, 16, 28, 13, 3)
    c.panel(4, 18, 13, 27, PLASTER, sh=0.15)             # back house
    for y in range(14, 19):
        half = y - 13
        for x in range(8 - half, 8 + half + 3):
            c.set(x, y, pick(ROOF_R, 0.3 + 0.5 * (y - 14) / 4.0, x, y))
    c.panel(13, 20, 21, 27, PLASTER)                     # front house
    for y in range(16, 21):
        half = y - 15
        for x in range(17 - half, 17 + half + 1):
            c.set(x, y, pick(SLATE, 0.3 + 0.5 * (y - 16) / 4.0, x, y))
    for (wx, wy) in ((7, 21), (10, 21), (16, 23), (18, 23)):
        c.set(wx, wy, SLATE[3])                          # dark windows
    c.panel(23, 10, 28, 27, PLASTER)                     # clock tower
    for y in range(7, 11):                               # slate cap
        half = y - 6
        for x in range(25 - half, 25 + half + 2):
            c.set(x, y, pick(SLATE, 0.3 + 0.5 * (y - 7) / 3.0, x, y))
    c.set(25, 14, GLASS_L)                               # clock face
    c.set(26, 14, GLASS)
    c.set(25, 15, GLASS)
    c.set(26, 15, SLATE[3])
    for y in range(3, 7):
        c.set(25, y, SLATE[3])                           # flag pole
    for x in range(26, 29):
        c.set(x, 3, FLAG)
        c.set(x, 4, FLAG)
    c.outline()
    return c


def icon_meadow():
    c = CellImg(ICELL)
    shadow_ellipse(c, 10, 28, 6, 2)
    shadow_ellipse(c, 22, 28, 6, 2)
    for y in range(22, 28):                              # trunks
        c.set(9, y, WOOD)
        c.set(10, y, WOOD_D)
    for y in range(24, 28):
        c.set(21, y, WOOD)
        c.set(22, y, WOOD_D)
    c.dome(10, 16, 6.2, 5.4, CANOPY, power=2.0)          # puffy crowns
    c.dome(13, 19, 3.4, 2.8, CANOPY, power=2.0, sh=0.18)
    c.dome(22, 19, 5.0, 4.4, CANOPY, power=2.0)
    for (fx, fy, col) in ((15, 27, FLW_W), (17, 26, FLW_Y), (13, 26, FLW_Y), (19, 27, FLW_W)):
        c.set(fx, fy, col)
    c.outline()
    return c


def icon_cave():
    c = CellImg(ICELL)
    shadow_ellipse(c, 16, 28, 12, 3)
    c.dome(16, 20, 12.0, 8.6, ROCKR, power=2.0)          # rocky knoll
    for (gx, gy) in ((8, 13), (12, 11), (20, 12), (24, 14)):
        c.set(gx, gy, GRASS_D)                           # scrub on the crown
        c.set(gx + 1, gy, GRASS)
    for y in range(19, 28):                              # cave mouth arch
        half = 4 if y >= 22 else y - 18
        for x in range(16 - half, 16 + half + 1):
            c.set(x, y, CAVE_D if abs(x - 16) < half - 1 and y > 20 else CAVE_IN)
    for y in range(19, 28):                              # lit rim
        half = 4 if y >= 22 else y - 18
        c.set(16 - half - 1, y, ROCKR[0])
        c.set(16 + half + 1, y, ROCKR[3])
    c.outline()
    return c


def icon_obelisk():
    c = CellImg(ICELL)
    shadow_ellipse(c, 16, 28, 9, 3)
    for y in range(6, 28):                               # leaning monolith
        lean = (27 - y) // 6
        half = 2 if y > 12 else 1
        xc = 15 + lean
        for x in range(xc - half, xc + half + 1):
            t = 0.25 + 0.55 * (x - (xc - half)) / max(1, 2 * half) + 0.1 * (y - 6) / 21.0
            c.set(x, y, pick(OBSL, t, x, y))
    c.set(18, 5, OBSL[1])                                # chipped tip
    for (kx, ky) in ((15, 12), (16, 13), (15, 14), (16, 15), (15, 16)):
        c.set(kx, ky, OBSL[3])                           # the great crack
    for (rx2, ry2) in ((16, 9), (15, 18), (15, 22)):
        c.set(rx2, ry2, RUNE)                            # dull runes
    c.set(17, 8, RUNE_L)                                 # one faint live glint
    c.outline()
    return c


icons = bytearray(IW * IH * 4)
for i, fn in enumerate((icon_home, icon_town, icon_meadow, icon_cave, icon_obelisk)):
    fn().blit(icons, IW, i * ICELL, 0)
write_png("overworld_icons.png", IW, IH, icons)
