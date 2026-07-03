#!/usr/bin/env python3
"""16x16 meadow tileset for the vertical slice (assets/tileset_gen.png, 64x32, 4x2).

Layout (atlas coords):
  (0,0) grass        (1,0) grass w/ tufts   (2,0) grass w/ flowers  (3,0) dirt path
  (0,1) hedge wall A (1,1) hedge wall B     (2,1) rock (decor)      (3,1) unused

Hedge tiles get full-square physics in assets/tileset.tres. Grass detail is placed by
a deterministic hash so re-runs are stable. Re-run: python3 assets/_gen_tileset.py
"""
import struct, zlib, os

HERE = os.path.dirname(os.path.abspath(__file__))
T, COLS, ROWS = 16, 4, 2
W, H = COLS * T, ROWS * T

# Lush surreal meadow (Secret of Mana lushness, Paper Girls color script): minty
# teal-leaning greens with deep teal shadows, candy-hot flowers, warm peach path
# whose shadows lean violet.
GRASS   = (94, 178, 118, 255)
GRASS_D = (58, 140, 116, 255)    # deep teal shadow
GRASS_L = (136, 210, 124, 255)   # warm sunlit blades
TUFT    = (40, 116, 100, 255)
FLW_W   = (252, 250, 242, 255)
FLW_Y   = (255, 212, 84, 255)
FLW_P   = (255, 116, 176, 255)   # hot pink
FLW_C   = (244, 162, 70, 255)
DIRT    = (230, 176, 130, 255)
DIRT_D  = (196, 132, 116, 255)   # violet-leaning shade
DIRT_L  = (248, 204, 150, 255)
HEDGE   = (34, 106, 94, 255)     # deep blue-green
HEDGE_L = (56, 138, 106, 255)
HEDGE_D = (24, 82, 78, 255)
HEDGE_S = (16, 58, 58, 255)
ROCK    = (158, 148, 176, 255)   # lavender stone
ROCK_L  = (188, 178, 200, 255)
ROCK_D  = (120, 110, 140, 255)

buf = bytearray(W * H * 4)

def put(tx, ty, x, y, c):
    if 0 <= x < T and 0 <= y < T:
        o = ((ty * T + y) * W + (tx * T + x)) * 4
        buf[o:o + 4] = bytes(c)

def fill(tx, ty, c):
    for y in range(T):
        for x in range(T):
            put(tx, ty, x, y, c)

def h2(x, y, salt=0):
    n = (x * 374761393 + y * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return (n ^ (n >> 16)) & 0xFF

def grass_base(tx, ty, salt):
    fill(tx, ty, GRASS)
    for y in range(T):
        for x in range(T):
            r = h2(x, y, salt)
            if r < 26:
                put(tx, ty, x, y, GRASS_D)
            elif r > 232:
                put(tx, ty, x, y, GRASS_L)
    # short blade ticks (light stroke + dark root) for a 16-bit turf feel
    for i in range(5):
        bx, by = h2(i, salt, 11) % (T - 2), h2(salt, i, 12) % (T - 3)
        put(tx, ty, bx, by, GRASS_L)
        put(tx, ty, bx, by + 1, GRASS_L)
        put(tx, ty, bx + 1, by + 2, GRASS_D)

# (0,0) plain grass / (1,0) tufts / (2,0) flowers
grass_base(0, 0, 1)
grass_base(1, 0, 2)
for (x, y) in ((3, 4), (10, 8), (6, 12), (12, 2)):
    put(1, 0, x, y, TUFT); put(1, 0, x + 1, y, TUFT)
    put(1, 0, x, y - 1, TUFT); put(1, 0, x + 2, y - 1, TUFT)
grass_base(2, 0, 3)
for (x, y, c) in ((3, 3, FLW_W), (10, 5, FLW_Y), (5, 11, FLW_P), (12, 12, FLW_W)):
    put(2, 0, x, y - 1, c); put(2, 0, x, y + 1, c)
    put(2, 0, x - 1, y, c); put(2, 0, x + 1, y, c)
    put(2, 0, x, y, FLW_C)

# (3,0) dirt path with pebbles
fill(3, 0, DIRT)
for y in range(T):
    for x in range(T):
        r = h2(x, y, 4)
        if r < 22:
            put(3, 0, x, y, DIRT_D)
        elif r > 236:
            put(3, 0, x, y, DIRT_L)
for i in range(4):
    px_, py_ = h2(i, 9, 13) % (T - 2), h2(9, i, 14) % (T - 2)
    put(3, 0, px_, py_, DIRT_L)                 # pebble catches the light...
    put(3, 0, px_ + 1, py_, DIRT_L)
    put(3, 0, px_ + 1, py_ + 1, DIRT_D)         # ...and casts a tiny shadow

# (0,1) & (1,1) hedge walls: rounded leaf clumps lit from the top-left
for tx, salt in ((0, 5), (1, 6)):
    fill(tx, 1, HEDGE)
    for cy in range(0, T, 4):               # 4x4 leaf clumps, jittered
        for cx in range(0, T, 4):
            jx = h2(cx, cy, salt) % 2
            jy = h2(cy, cx, salt) % 2
            put(tx, 1, cx + jx, cy + jy, HEDGE_L)
            put(tx, 1, cx + jx + 1, cy + jy, HEDGE_L)
            put(tx, 1, cx + jx, cy + jy + 1, HEDGE_L)
            put(tx, 1, cx + jx + 2, cy + jy + 2, HEDGE_D)
            put(tx, 1, cx + jx + 1, cy + jy + 3, HEDGE_S)
    for x in range(T):                      # lit top edge, shadowed base
        put(tx, 1, x, 0, HEDGE_L)
        put(tx, 1, x, T - 2, HEDGE_D)
        put(tx, 1, x, T - 1, HEDGE_S)

# (2,1) rock on grass (decor, no collision)
grass_base(2, 1, 7)
for y in range(5, 13):
    half = 5 - abs(y - 9)
    for x in range(8 - half, 8 + half + 1):
        c = ROCK
        if y <= 7 and x <= 8:
            c = ROCK_L
        elif y >= 11:
            c = ROCK_D
        put(2, 1, x, y, c)

# (3,1) reserved: plain grass so it isn't a hole if ever painted
grass_base(3, 1, 8)

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += buf[y * W * 4:(y + 1) * W * 4]

def chunk(tag, data):
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
       + chunk(b"IEND", b""))
dst = os.path.join(HERE, "tileset_gen.png")
open(dst, "wb").write(png)
print(f"wrote {os.path.relpath(dst, HERE)} ({W}x{H})")
