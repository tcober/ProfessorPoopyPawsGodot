#!/usr/bin/env python3
"""Frame-consistent slime sprite sheet (assets/slime_gen.png, 288x192, 48x48 cells, 6x4).

Matches entities/enemies/slime_frames.tres:
  row0 walk_down(6)  row1 walk_up(6)  row2 walk_side(6, faces RIGHT; code mirrors)
  row3 death(4 splat) + 2 empty

The walk rows are one bounce cycle: rest, squash, launch, apex, fall, land. The slime
is airborne on frames 2-4 — slime.gd scales movement speed to match, so it hops.
Feet baseline y=42. Palette: assets/_palette.py ACTORS["slime"] (meadow gel, teal
shadows). Re-run: python3 assets/_gen_slime_sprites.py
"""
import os, math, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _artlib import Cell, write_cells
from _palette import SLIME

CELL, COLS, ROWS = 48, 6, 4
BASE = 42
CX = 23.5

GELR  = SLIME["GELR"]
GEL   = GELR[1]
GEL_L = GELR[0]
OUT   = SLIME["OUT"]
EYE   = SLIME["EYE"]
GLINT = SLIME["GLINT"]


def blob(c, half_w, h, dy, face="down", alpha=255):
    def col(rgba):
        return (rgba[0], rgba[1], rgba[2], alpha)
    base = BASE - dy
    top = base - h
    for y in range(top, base + 1):
        f = (y - top) / max(1, h)
        w = half_w * math.sqrt(max(0.0, 1.0 - (1.0 - f) ** 2))
        w = max(1.0, w)
        x0, x1 = round(CX - w), round(CX + w)
        for x in range(x0, x1 + 1):
            nx = (x - CX) / max(1.0, half_w)
            ny = f * 2.0 - 1.0
            t = 0.42 + 0.28 * (nx * 0.55 + ny * 0.75) + 0.24 * (nx * nx + ny * f)
            c.set(x, y, col(c._pick(GELR, t, x, y)))
    # wet top-left sheen: a soft 2-step highlight blob
    sx = round(CX - half_w * 0.45)
    sy = top + max(2, h // 5)
    c.rect(sx, sy, sx + 3, sy + 2, col(GLINT))
    c.rect(sx + 1, sy + 3, sx + 4, sy + 4, col(GEL_L))
    c.set(sx + 5, sy + 5, col(GEL_L))
    if face == "up":
        c.rect(sx + 2, sy + 2, sx + 7, sy + 5, col(GEL_L))   # bigger back sheen
        return
    # face: glossy dark eyes with a heavy upper lid, double glint, sweet mouth
    ey = top + max(4, round(h * 0.45))
    shift = 6 if face == "side" else 0
    for ex in (round(CX) - 8 + shift, round(CX) + 4 + shift):
        c.rect(ex, ey, ex + 3, ey + 5, col(EYE))
        c.rect(ex, ey, ex + 3, ey, col((GELR[3][0], GELR[3][1], GELR[3][2], alpha)))  # lid
        c.rect(ex + 1, ey + 1, ex + 2, ey + 2, col(GLINT))    # big wet glint
        c.set(ex + 3, ey + 4, col(GEL_L))                     # low shine
    my = ey + 8
    if my < base - 2:
        mx = round(CX) + shift
        c.line([(mx - 2, my), (mx - 1, my + 1), (mx, my + 1), (mx + 1, my)], col(EYE))


def droplets(c, spread, alpha):
    pts = [(-spread, -4), (spread, -6), (-spread + 4, -12), (spread - 2, -14), (0, -18)]
    for i, (dx, dy) in enumerate(pts):
        x, y = round(CX + dx), BASE + dy
        s = 2 if i % 2 else 1
        c.rect(x, y, x + s, y + s, (GEL[0], GEL[1], GEL[2], alpha))


cells = [[Cell(CELL, grain=2) for _ in range(COLS)] for _ in range(ROWS)]

# bounce cycle: (half_w, height, lift) — 2x the classic 24px values
cycle = [(16, 24, 0), (18, 20, 0), (14, 30, 2), (14, 28, 8), (14, 30, 2), (18, 20, 0)]
for i, (w, h, dy) in enumerate(cycle):
    blob(cells[0][i], w, h, dy, "down")
    blob(cells[1][i], w, h, dy, "up")
    blob(cells[2][i], w, h, dy, "side")

# death: flatten, splat, dissolve
blob(cells[3][0], 20, 14, 0, "down")
blob(cells[3][1], 22, 8, 0, "none")
droplets(cells[3][1], 16, 255)
blob(cells[3][2], 22, 4, 0, "none", alpha=190)
droplets(cells[3][2], 20, 190)
droplets(cells[3][3], 22, 110)

for row in cells:
    for cell in row:
        cell.outline({}, OUT)

write_cells(os.path.join(HERE, "slime_gen.png"), cells, CELL)
