#!/usr/bin/env python3
"""Meadow slime sheet (assets/slime_gen.png, 288x192, 48x48 cells, 6x4) on the
_sprites.py kit.

FROZEN contracts (entities/enemies/slime_frames.tres + slime.gd):
  row0 walk_down(6)  row1 walk_up(6)  row2 walk_side(6, faces RIGHT; code mirrors)
  row3 death(4 splat)   ·   frames 2-4 of each walk row are AIRBORNE — slime.gd
  scales movement speed to those frames so slimes hop instead of glide.

The bounce is squash-and-stretch with conserved volume (half_w x height stays
~constant), a darker gel nucleus that lags the body, a wet double glint, and a
translucent bottom rim where light passes through the gel. Feet baseline y=42.
Palette: ACTORS["slime"]. Re-run: python3 assets/_gen_slime_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import write_cells
from _sprites import Sprite
from _palette import SLIME

CELL, COLS, ROWS = 48, 6, 4
BASE = 42
CX = 23.5

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
    sy = top + max(2, h // 5)
    s.rect(sx, sy, sx + 3, sy + 1, (GLINT[0], GLINT[1], GLINT[2], alpha))
    s.rect(sx + 1, sy + 2, sx + 3, sy + 3, (GELR[0][0], GELR[0][1], GELR[0][2], alpha))
    s.set(sx + 5, sy + 4, (GELR[0][0], GELR[0][1], GELR[0][2], alpha))


def face(s, half_w, h, dy, view, alpha=255):
    if view == "up":
        return
    base = BASE - dy
    top = base - h
    ey = top + max(4, round(h * 0.44))
    shift = 5 if view == "side" else 0
    for ex in (round(CX) - 8 + shift, round(CX) + 4 + shift):
        s.rect(ex, ey, ex + 3, ey + 4, (EYE[0], EYE[1], EYE[2], alpha))
        s.rect(ex, ey, ex + 3, ey, (GELR[3][0], GELR[3][1], GELR[3][2], alpha))  # lid
        s.rect(ex + 1, ey + 1, ex + 2, ey + 2, (GLINT[0], GLINT[1], GLINT[2], alpha))
    my = ey + 7
    if my < base - 2:
        mx = round(CX) + shift
        s.line([(mx - 2, my), (mx - 1, my + 1), (mx, my + 1), (mx + 1, my)],
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
    for i, (dx, dyy) in enumerate(((-1.0, -4), (1.0, -6), (-0.72, -12), (0.85, -14), (0.1, -18))):
        x, y = round(CX + dx * spread), BASE + dyy
        k = 2 if i % 2 else 1
        s.rect(x, y, x + k, y + k, (GELR[1][0], GELR[1][1], GELR[1][2], alpha))
        s.set(x, y, (GELR[0][0], GELR[0][1], GELR[0][2], alpha))


cells = [[Sprite(CELL, grain=2, salt=r * 7 + c) for c in range(COLS)] for r in range(ROWS)]

# bounce cycle: rest, squash, launch, apex, fall, land — volume ~conserved,
# nucleus lags down on launch and floats up at apex.
cycle = [(16.0, 24, 0, 0.0), (18.5, 20, 0, 1.5), (13.5, 29, 2, 2.0),
         (13.0, 30, 8, -2.0), (13.5, 29, 2, -1.0), (18.5, 20, 0, 1.5)]
for i, (w, h, dy, lag) in enumerate(cycle):
    slime(cells[0][i], w, h, dy, "down", lag)
    slime(cells[1][i], w, h, dy, "up", lag)
    slime(cells[2][i], w, h, dy, "side", lag)

# death: flinch flat, burst, melt, evaporate
slime(cells[3][0], 20.0, 13, 0, "down", 1.0)
slime(cells[3][1], 22.0, 8, 0, "down", 0.0, eyes=False)
droplets(cells[3][1], 16, 255)
slime(cells[3][2], 22.5, 4, 0, "down", 0.0, alpha=190, eyes=False)
droplets(cells[3][2], 20, 190)
droplets(cells[3][3], 22, 110)

write_cells(os.path.join(HERE, "slime_gen.png"), cells, CELL)
