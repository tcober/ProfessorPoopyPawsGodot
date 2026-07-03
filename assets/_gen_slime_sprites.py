#!/usr/bin/env python3
"""Frame-consistent slime sprite sheet (assets/slime_gen.png, 144x96, 24x24 cells, 6x4).

Matches entities/enemies/slime_frames.tres:
  row0 walk_down(6)  row1 walk_up(6)  row2 walk_side(6, faces RIGHT; code mirrors)
  row3 death(4 splat) + 2 empty

The walk rows are one bounce cycle: rest, squash, launch, apex, fall, land. The slime
is airborne on frames 2-4 — slime.gd scales movement speed to match, so it hops.
Feet baseline y=21. Re-run: python3 assets/_gen_slime_sprites.py
"""
import struct, zlib, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
CELL, COLS, ROWS = 24, 6, 4
BASE = 21

# 4-tone gel ramp (light -> dark), shaded like a lit dome with dithered bands
GELR  = [(172, 240, 180, 255), (116, 210, 132, 255), (76, 170, 100, 255), (50, 130, 78, 255)]
GEL   = GELR[1]
GEL_D = GELR[3]
GEL_L = GELR[0]
OUT   = (24, 62, 40, 255)
EYE   = (24, 34, 28, 255)
GLINT = (235, 250, 238, 255)


def pick(t, x, y):
    b = max(0.0, min(2.999, t * 3.0))
    i = int(b)
    frac = b - i
    if frac > 0.58 or (0.45 < frac <= 0.58 and (x + y) % 2 == 0):
        i += 1
    return GELR[min(3, i)]


class Cell:
    def __init__(self):
        self.px = [[None] * CELL for _ in range(CELL)]

    def set(self, x, y, c):
        if 0 <= x < CELL and 0 <= y < CELL:
            self.px[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def outline(self):
        edge = []
        for y in range(CELL):
            for x in range(CELL):
                if self.px[y][x] is None:
                    for nx, ny in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                        if 0 <= nx < CELL and 0 <= ny < CELL and self.px[ny][nx] \
                                and self.px[ny][nx] != OUT:
                            edge.append((x, y))
                            break
        for x, y in edge:
            self.px[y][x] = OUT


def blob(c, half_w, h, dy, face="down", alpha=255):
    def col(rgba):
        return (rgba[0], rgba[1], rgba[2], alpha)
    base = BASE - dy
    top = base - h
    cx = 11.5
    for y in range(top, base + 1):
        f = (y - top) / max(1, h)
        w = half_w * math.sqrt(max(0.0, 1.0 - (1.0 - f) ** 2))
        w = max(1.0, w)
        x0, x1 = round(cx - w), round(cx + w)
        for x in range(x0, x1 + 1):
            nx = (x - cx) / max(1.0, half_w)
            ny = f * 2.0 - 1.0
            t = 0.42 + 0.28 * (nx * 0.55 + ny * 0.75) + 0.24 * (nx * nx + ny * f)
            c.set(x, y, col(pick(t, x, y)))
    # wet top-left sheen
    sx = round(cx - half_w * 0.45)
    sy = top + max(1, h // 5)
    c.rect(sx, sy, sx + 1, sy + 1, col(GLINT))
    c.set(sx + 2, sy + 2, col(GEL_L))
    if face == "up":
        c.rect(sx + 1, sy + 1, sx + 3, sy + 2, col(GEL_L))   # bigger back sheen
        return
    ey = top + max(2, round(h * 0.45))
    shift = 3 if face == "side" else 0
    for ex in (round(cx) - 4 + shift, round(cx) + 2 + shift):
        c.rect(ex, ey, ex + 1, ey + 2, col(EYE))
        c.set(ex, ey, col(GLINT))
    my = ey + 4
    if my < base - 1:
        c.rect(round(cx) - 1 + shift, my, round(cx) + shift, my, col(EYE))


def droplets(c, spread, alpha):
    pts = [(-spread, -2), (spread, -3), (-spread + 2, -6), (spread - 1, -7), (0, -9)]
    for i, (dx, dy) in enumerate(pts):
        x, y = round(11.5 + dx), BASE + dy
        s = 1 if i % 2 else 0
        c.rect(x, y, x + s, y + s, (GEL[0], GEL[1], GEL[2], alpha))


cells = [[Cell() for _ in range(COLS)] for _ in range(ROWS)]

# bounce cycle: (half_w, height, lift)
cycle = [(8, 12, 0), (9, 10, 0), (7, 15, 1), (7, 14, 4), (7, 15, 1), (9, 10, 0)]
for i, (w, h, dy) in enumerate(cycle):
    blob(cells[0][i], w, h, dy, "down")
    blob(cells[1][i], w, h, dy, "up")
    blob(cells[2][i], w, h, dy, "side")

# death: flatten, splat, dissolve
blob(cells[3][0], 10, 7, 0, "down")
blob(cells[3][1], 11, 4, 0, "none")
droplets(cells[3][1], 8, 255)
blob(cells[3][2], 11, 2, 0, "none", alpha=190)
droplets(cells[3][2], 10, 190)
droplets(cells[3][3], 11, 110)

for row in cells:
    for cell in row:
        cell.outline()

W, H = COLS * CELL, ROWS * CELL
buf = bytearray(W * H * 4)
for r in range(ROWS):
    for ci in range(COLS):
        cell = cells[r][ci]
        for y in range(CELL):
            for x in range(CELL):
                p = cell.px[y][x]
                if p:
                    o = ((r * CELL + y) * W + (ci * CELL + x)) * 4
                    buf[o:o + 4] = bytes(p)

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
dst = os.path.join(HERE, "slime_gen.png")
open(dst, "wb").write(png)
print(f"wrote {os.path.relpath(dst, HERE)} ({W}x{H})")
