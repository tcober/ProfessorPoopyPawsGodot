#!/usr/bin/env python3
"""Meadow slime sheet (assets/slime_gen.png, 144x96, 24x24 cells, 6x4) on the
_sprites.py kit, at TRUE SNES density (CT-chunk restart).

FROZEN contracts (entities/enemies/slime_frames.tres + slime.gd):
  row0 walk_down(6)  row1 walk_up(6)  row2 walk_side(6, faces RIGHT; code mirrors)
  row3 death(4 splat)   ·   frames 2-4 of each walk row are AIRBORNE — slime.gd
  scales movement speed to those frames so slimes hop instead of glide.

The bounce is squash-and-stretch with conserved volume (half_w x height stays
~constant), a darker gel nucleus that lags the body, a wet glint, and a
translucent bottom rim where light passes through the gel. Feet baseline y=21.
Palette: ACTORS["slime"]. Re-run: python3 assets/_gen_slime_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import write_cells
from _sprites import Sprite
from _palette import SLIME

CELL, COLS, ROWS = 24, 6, 4
BASE = 21
CX = 11.5

GELR = SLIME["GELR"]
OUT = SLIME["OUT"]
EYE = SLIME["EYE"]
GLINT = SLIME["GLINT"]
NUCR = [(96, 178, 122, 255), (70, 148, 100, 255), (50, 122, 84, 255), (36, 98, 70, 255)]


def body(s, half_w, h, dy, alpha=255):
    """Gel dome with a flat base: sqrt-profile silhouette, wrap-lit, bottom rim
    light where the ground bounces light through the gel."""
    base = BASE - dy
    top = base - h
    for y in range(top, base + 1):
        f = (y - top) / max(1, h)
        w = half_w * max(0.06, (1.0 - (1.0 - f) ** 2)) ** 0.5
        x0, x1 = round(CX - w), round(CX + w)
        for x in range(x0, x1 + 1):
            nx = (x - CX) / max(1.0, half_w)
            ny = f * 2.0 - 1.0
            t = 0.40 + 0.30 * (nx * 0.55 + ny * 0.75) + 0.22 * nx * nx
            if f > 0.86 and abs(nx) < 0.62:
                t -= 0.34                     # translucent bottom rim
            c = s.tone(GELR, t, x, y)
            s.set(x, y, (c[0], c[1], c[2], alpha))


def nucleus(s, half_w, h, dy, lag=0.0, alpha=255):
    """Darker inner blob that lags a touch behind the bounce."""
    base = BASE - dy
    cy = base - h * 0.42 + lag
    rx, ry = half_w * 0.42, h * 0.26
    for y in range(int(cy - ry), int(cy + ry) + 1):
        ny = (y - cy) / ry
        for x in range(int(CX - rx), int(CX + rx) + 2):
            nx = (x - CX) / rx
            if nx * nx + ny * ny <= 1.0:
                t = 0.45 + 0.3 * (nx * 0.5 + ny * 0.8)
                c = s.tone(NUCR, t, x, y)
                s.set(x, y, (c[0], c[1], c[2], alpha))


def sheen(s, half_w, h, dy, alpha=255):
    base = BASE - dy
    top = base - h
    sx = round(CX - half_w * 0.45)
    sy = top + max(1, h // 5)
    s.rect(sx, sy, sx + 1, sy, (GLINT[0], GLINT[1], GLINT[2], alpha))
    s.set(sx + 1, sy + 1, (GELR[0][0], GELR[0][1], GELR[0][2], alpha))


def face(s, half_w, h, dy, view, alpha=255):
    if view == "up":
        return
    base = BASE - dy
    top = base - h
    ey = top + max(2, round(h * 0.44))
    shift = 3 if view == "side" else 0
    for ex in (round(CX) - 4 + shift, round(CX) + 2 + shift):
        s.rect(ex, ey, ex + 1, ey + 2, (EYE[0], EYE[1], EYE[2], alpha))
        s.set(ex, ey, (GELR[3][0], GELR[3][1], GELR[3][2], alpha))   # lid corner
        s.set(ex + 1, ey + 1, (GLINT[0], GLINT[1], GLINT[2], alpha))
    my = ey + 4
    if my < base - 1:
        mx = round(CX) + shift
        s.line([(mx - 1, my), (mx, my + 1), (mx + 1, my)],
               (EYE[0], EYE[1], EYE[2], alpha))


def slime(s, half_w, h, dy, view, lag=0.0, alpha=255, eyes=True):
    body(s, half_w, h, dy, alpha)
    nucleus(s, half_w, h, dy, lag, alpha)
    sheen(s, half_w, h, dy, alpha)
    if eyes:
        face(s, half_w, h, dy, view, alpha)
    s.despeckle(passes=1)
    s.outline({}, OUT)


def droplets(s, spread, alpha):
    for i, (dx, dyy) in enumerate(((-1.0, -2), (1.0, -3), (-0.72, -6), (0.85, -7), (0.1, -9))):
        x, y = round(CX + dx * spread), BASE + dyy
        k = 1 if i % 2 else 0
        s.rect(x, y, x + k, y + k, (GELR[1][0], GELR[1][1], GELR[1][2], alpha))
        s.set(x, y, (GELR[0][0], GELR[0][1], GELR[0][2], alpha))


cells = [[Sprite(CELL, grain=1, salt=r * 7 + c, jitter=0.0) for c in range(COLS)]
         for r in range(ROWS)]

# bounce cycle: rest, squash, launch, apex, fall, land — volume ~conserved,
# nucleus lags down on launch and floats up at apex.
cycle = [(8.0, 12, 0, 0.0), (9.2, 10, 0, 0.8), (6.8, 14, 1, 1.0),
         (6.5, 15, 4, -1.0), (6.8, 14, 1, -0.5), (9.2, 10, 0, 0.8)]
for i, (w, h, dy, lag) in enumerate(cycle):
    slime(cells[0][i], w, h, dy, "down", lag)
    slime(cells[1][i], w, h, dy, "up", lag)
    slime(cells[2][i], w, h, dy, "side", lag)

# death: flinch flat, burst, melt, evaporate
slime(cells[3][0], 10.0, 7, 0, "down", 0.5)
slime(cells[3][1], 11.0, 4, 0, "down", 0.0, eyes=False)
droplets(cells[3][1], 8, 255)
slime(cells[3][2], 11.2, 2, 0, "down", 0.0, alpha=190, eyes=False)
droplets(cells[3][2], 10, 190)
droplets(cells[3][3], 11, 110)

write_cells(os.path.join(HERE, "slime_gen.png"), cells, CELL)
