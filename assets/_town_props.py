#!/usr/bin/env python3
"""Alembic Town prop library — the overworld cluster's buildings at ZONE
scale (48px player), for assets/maps/town.txt. Same steampunk-medieval
vocabulary as assets/_overworld_props.py (whose drawing helpers this file
reuses), roughly 2x the overworld detail.

Every building returns a (lower, upper) Sprite pair for place_split: the
facade bakes UNDER entities, the roof (and the strip of wall/lintel above the
door mouth, which the 33px player's head overlaps when standing in the D
cell) rides OVER them — the walkable roof-row cells behind a house hide the
player, CT-style. Draw only inside the (w, h) footprint; edge()/clipw() trim
the outline dilation back to it.

Stdlib-only, deterministic (fixed salts). Used by assets/_gen_tileset_town.py.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _overworld_props import (S, ln, edge, _hip_roof, _window, _chimney,
                              _coursed_wall,
                              DOORDARK, WARM, WARMD, CRYSTAL)
from _tilekit import (TIMBER, BRASS, STEEL, COPPER, IRON, STONER, GLASS, MINT,
                      VIOLETF, PAPER, PAPERD, RED, SPEC, WATER, OUTLINE)


def clipw(sp, w):
    """Clear columns at x >= w — the sideways cousin of edge()'s row clip,
    for props narrower than their (square) canvas."""
    for y in range(sp.n):
        for x in range(w, sp.n):
            sp.px[y][x] = None


def _stone_courses(sp, x0, y0, x1, y1, stone):
    """Coursed masonry fill (the Academy's keep at zone scale) — the shared
    dressed-masonry treatment, at zone-scale course/joint periods."""
    _coursed_wall(sp, x0, y0, x1, y1, stone, salt=21, course=8, joint=12)


def town_home(roof, plaster, salt=201):
    """Basil's cottage up close: 96x80 over a 6x5 footprint (3 roof rows +
    2 facade rows). Open candle-lit doorway on the D cell, warm mullioned
    windows, hanging flask sign, brass porthole in the roof."""
    w, h, fy = 96, 80, 48
    dx0, dx1 = 46, 63                                      # mouth over the D cell
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # ---- lower: the facade
    lo.rect(0, fy, w - 1, h - 1, plaster[0])
    lo.rect(0, fy, 2, h - 1, TIMBER[3])                    # corner posts
    lo.rect(w - 3, fy, w - 1, h - 1, TIMBER[3])
    lo.rect(0, fy, w - 1, fy + 1, TIMBER[1])               # eave beam
    lo.rect(0, fy + 2, w - 1, fy + 2, TIMBER[3])
    lo.rect(3, h - 2, w - 4, h - 1, STONER[4])             # footing
    for x in (26, 70):                                     # half-timber studs
        lo.rect(x, fy + 3, x + 1, h - 3, TIMBER[2])
    # the open doorway
    lo.rect(dx0 - 3, fy + 3, dx1 + 3, h - 1, TIMBER[3])    # casing
    lo.rect(dx0, fy + 10, dx1, h - 1, DOORDARK)
    lo.rect(dx0 + 2, fy + 10, dx1 - 2, fy + 17, WARMD)     # lamplit inside
    lo.rect(dx0 + 4, fy + 12, dx1 - 4, fy + 15, WARM)
    lo.rect(dx0, h - 1, dx1, h - 1, WARMD)                 # light on the sill
    # warm windows either side
    _window(lo, 9, fy + 9, 13, 15, WARMD, WARM)
    _window(lo, w - 22, fy + 9, 13, 15, WARMD, WARM)
    # hanging flask sign by the door
    sx = dx1 + 7
    lo.rect(sx, fy + 4, sx, fy + 11, IRON[2])              # bracket
    lo.rect(sx - 1, fy + 4, sx + 8, fy + 4, IRON[3])
    lo.rect(sx + 1, fy + 7, sx + 8, fy + 19, TIMBER[2])    # board
    lo.rect(sx + 1, fy + 7, sx + 8, fy + 7, TIMBER[1])
    lo.rect(sx + 3, fy + 11, sx + 6, fy + 17, MINT)        # the flask glyph
    lo.rect(sx + 4, fy + 9, sx + 5, fy + 10, PAPERD)       # its neck
    edge(lo, h)
    # ---- upper: roof, porthole, chimney, and the door-top strip
    _hip_roof(up, 0, w - 1, 0, fy - 1, w // 5, roof)
    cx = w // 3
    for r, c in ((6.2, BRASS[3]), (4.6, BRASS[1]), (3.0, WARM)):
        up.blob(cx, 20, r, r, c)
    up.set(cx - 2, 17, SPEC)
    _chimney(up, w * 3 // 4 + 2, 4, 20)
    up.rect(dx0 - 3, fy, dx1 + 3, fy + 1, TIMBER[1])       # eave over the mouth
    up.rect(dx0 - 3, fy + 2, dx1 + 3, fy + 2, TIMBER[3])
    up.rect(dx0 - 3, fy + 3, dx1 + 3, fy + 7, TIMBER[3])   # casing head
    up.rect(dx0 - 1, fy + 8, dx1 + 1, fy + 8, TIMBER[1])   # lintel
    up.rect(dx0, fy + 9, dx1, fy + 9, TIMBER[4])           # its shadow
    edge(up, fy + 10)
    return lo, up


def town_cottage(roof, plaster, salt=211):
    """A townsfolk cottage at zone scale: 80x64 over 5x4 (2 roof + 2 facade
    rows). Cold windows and a CLOSED iron-strapped door — town's asleep."""
    w, h, fy = 80, 64, 32
    dx0, dx1 = 33, 46                                      # leaf over the D cell
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # ---- lower: the facade
    lo.rect(0, fy, w - 1, h - 1, plaster[1])
    lo.rect(0, fy, 1, h - 1, TIMBER[3])
    lo.rect(w - 2, fy, w - 1, h - 1, TIMBER[3])
    lo.rect(0, fy, w - 1, fy + 1, TIMBER[1])
    lo.rect(0, fy + 2, w - 1, fy + 2, TIMBER[3])
    lo.rect(2, h - 2, w - 3, h - 1, STONER[4])
    # the closed door
    lo.rect(dx0 - 2, fy + 4, dx1 + 2, h - 1, TIMBER[4])    # casing
    lo.rect(dx0, fy + 10, dx1, h - 1, TIMBER[2])           # the leaf
    lo.rect(dx0, fy + 10, dx0, h - 1, TIMBER[1])
    lo.rect(dx1, fy + 10, dx1, h - 1, TIMBER[4])
    for by in (fy + 14, fy + 24):
        lo.rect(dx0, by, dx1, by, IRON[3])                 # iron straps
        lo.set(dx0 + 2, by, IRON[1])
        lo.set(dx1 - 2, by, IRON[1])
    lo.set(dx1 - 3, fy + 19, BRASS[1])                     # handle
    lo.set(dx1 - 3, fy + 20, BRASS[3])
    # cold windows
    _window(lo, 7, fy + 8, 12, 14, GLASS, MINT)
    _window(lo, w - 19, fy + 8, 12, 14, GLASS, MINT)
    edge(lo, h)
    # ---- upper: roof + chimney + door-top strip
    _hip_roof(up, 0, w - 1, 0, fy - 1, w // 5, roof)
    _chimney(up, w * 2 // 3 + 4, 3, 16)
    up.rect(dx0 - 2, fy, dx1 + 2, fy + 1, TIMBER[1])
    up.rect(dx0 - 2, fy + 2, dx1 + 2, fy + 2, TIMBER[3])
    up.rect(dx0 - 2, fy + 3, dx1 + 2, fy + 8, TIMBER[4])   # casing head
    up.rect(dx0 - 1, fy + 9, dx1 + 1, fy + 9, TIMBER[1])   # lintel
    edge(up, fy + 10)
    return lo, up


def town_academy(roof, stone, salt=221):
    """The Alembic Academy at zone scale: 160x112 over 10x7 (4 roof + 3 wall
    rows). Twin conical towers, keep roof over a parapet, the alchemical rose
    window, violet banners, gear bosses, and the great barred door (sealed —
    the yard gate D on the fence is the marker cell)."""
    w, h = 160, 112
    split = 64                                             # roof rows / wall rows
    tw = 24                                                # tower width
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    kx0, kx1 = tw, w - tw - 1
    # ---- upper: keep roof + parapet + upper wall band
    _hip_roof(up, kx0, kx1, 10, 46, 18, roof)
    up.rect(kx0, 47, kx1, 47, stone[1])                    # parapet line
    up.rect(kx0, 48, kx1, 48, stone[3])
    _stone_courses(up, kx0, 49, kx1, split - 1, stone)
    up.rect(w // 2 - 4, 4, w // 2 + 3, 9, stone[2])        # spire drum
    up.tri((w // 2 - 1, 0), 4, w // 2 - 6, w // 2 + 5, roof[1])
    up.rect(w // 2 - 1, 0, w // 2, 0, BRASS[1])            # finial
    # ---- lower: wall rows
    _stone_courses(lo, kx0, split, kx1, h - 1, stone)
    lo.rect(kx0, h - 1, kx1, h - 1, stone[4])              # footing
    # the great rose window (drawn on the wall, straddling nothing)
    cx, cy = w // 2 - 1, 78
    for r, c in ((13.0, BRASS[3]), (11.0, BRASS[1]), (9.4, GLASS)):
        lo.blob(cx, cy, r, r, c)
    lo.blob(cx, cy, 7.0, 7.0, MINT)
    lo.blob(cx, cy, 3.2, 3.2, VIOLETF)
    lo.rect(cx, cy - 9, cx, cy + 9, TIMBER[4])             # mullion cross
    lo.rect(cx - 9, cy, cx + 9, cy, TIMBER[4])
    lo.set(cx - 4, cy - 4, SPEC)
    # hanging banners
    for bx in (kx0 + 10, kx1 - 17):
        lo.rect(bx, 66, bx + 7, 92, VIOLETF)
        lo.rect(bx, 66, bx + 7, 67, CRYSTAL)
        lo.rect(bx + 2, 78, bx + 5, 79, CRYSTAL)           # device stripe
        for cutx in (bx, bx + 1, bx + 6, bx + 7):
            lo.set(cutx, 92, None)                         # swallowtail cut
    # gear bosses
    for gx in (kx0 + 22, kx1 - 21):
        lo.ball(gx, 98, 4.5, 4.5, BRASS, power=2.2)
        for dx, dy in ((-6, 0), (6, 0), (0, -6), (0, 6)):
            lo.rect(gx + dx, 98 + dy, gx + dx, 98 + dy, BRASS[3])
        lo.set(gx, 98, TIMBER[5])
    # the barred great door
    dx0, dx1 = w // 2 - 12, w // 2 + 11
    lo.rect(dx0 - 3, 84, dx1 + 3, h - 1, stone[4])         # arch ring
    lo.rect(dx0 - 1, 86, dx1 + 1, 87, stone[1])            # keystone course
    lo.rect(dx0, 88, dx1, h - 1, TIMBER[3])                # the doors
    lo.rect(w // 2 - 1, 88, w // 2 - 1, h - 1, TIMBER[5])  # meeting stile
    for by in (93, 102):
        lo.rect(dx0, by, dx1, by, IRON[3])                 # iron straps
        for rx in range(dx0 + 2, dx1, 6):
            lo.set(rx, by, IRON[1])
    for hx in (w // 2 - 6, w // 2 + 4):
        lo.set(hx, 97, BRASS[1])                           # ring handles
        lo.set(hx, 98, BRASS[3])
    lo.set(w // 2 - 1, 90, MINT)                           # seams of old magic
    lo.set(w // 2 - 1, 95, MINT)
    # ---- towers, split across both canvases (they stand proud of the keep)
    for tx0 in (0, w - tw):
        up.tri((tx0 + 11, 0), 14, tx0, tx0 + tw - 1, roof[2])
        up.tri((tx0 + 10, 0), 14, tx0, tx0 + 13, roof[1])  # lit slope
        up.rect(tx0 + 10, 0, tx0 + 12, 0, BRASS[1])
        up.rect(tx0, 15, tx0 + tw - 1, 15, roof[4])        # eave line
        for sp, y0, y1 in ((up, 16, split - 1), (lo, split, h - 1)):
            for y in range(y0, y1 + 1):
                for x in range(tx0, tx0 + tw):
                    u = x - tx0
                    c = stone[1] if u < 6 else (stone[2] if u < 17 else stone[3])
                    if (y - 16) % 8 == 7:
                        c = stone[4]
                    sp.set(x, y, c)
                sp.set(tx0, y, stone[3])
                sp.set(tx0 + tw - 1, y, stone[4])
        for sp, wy in ((up, 26), (up, 50), (lo, 78)):      # mint arrow slits
            sp.rect(tx0 + 10, wy, tx0 + 12, wy + 7, DOORDARK)
            sp.set(tx0 + 10, wy, MINT)
            sp.set(tx0 + 11, wy + 1, MINT)
        lo.rect(tx0, h - 1, tx0 + tw - 1, h - 1, stone[4])
    edge(lo, h)
    edge(up, split + 16)
    return lo, up


def town_well(stone, salt=231):
    """The commons well at zone scale (32x32, 2x2 solid): shingled cap on
    timber posts over a coursed stone ring, rope and pail."""
    sp = S(32, 32, salt)
    for y in range(18, 32):                                # stone ring
        for x in range(3, 29):
            c = stone[2] if y < 24 else stone[3]
            if (x + y) % 6 == 0:
                c = stone[4]
            sp.set(x, y, c)
    sp.rect(3, 18, 28, 18, stone[1])                       # lit rim
    sp.rect(7, 20, 24, 23, DOORDARK)                       # the shaft
    sp.rect(9, 21, 12, 21, WATER)
    sp.rect(4, 8, 6, 18, TIMBER[3])                        # posts
    sp.rect(25, 8, 27, 18, TIMBER[3])
    sp.tri((15, 0), 8, 0, 31, TIMBER[2])                   # shingle cap
    sp.rect(12, 0, 19, 0, TIMBER[1])
    sp.rect(15, 8, 15, 17, PAPERD)                         # rope
    sp.rect(13, 16, 17, 19, STEEL[2])                      # pail
    sp.rect(13, 16, 17, 16, STEEL[1])
    edge(sp)
    return sp


def town_lamp(salt=233):
    """Brass-caged street lamp at zone scale (16x32, a 1x2 solid column);
    the halo rides the additive glow overlay."""
    sp = S(16, 32, salt)
    sp.rect(5, 27, 10, 29, IRON[3])                        # base
    sp.rect(4, 30, 11, 31, IRON[2])
    sp.rect(7, 8, 8, 27, IRON[2])
    sp.rect(7, 8, 7, 27, IRON[1])
    sp.rect(4, 0, 11, 0, BRASS[1])                         # cap
    sp.rect(4, 1, 11, 7, BRASS[3])
    sp.rect(5, 1, 10, 6, MINT)                             # the mantle
    sp.set(6, 2, SPEC)
    sp.set(3, 2, BRASS[2])
    sp.set(12, 2, BRASS[2])                                # cage arms
    edge(sp, 32)
    clipw(sp, 16)
    return sp


def town_stall(salt=241):
    """The flask-seller's stall at zone scale (48x32, 3x2 solid): striped
    awning over a timber counter of glinting wares."""
    w, h = 48, 32
    sp = S(w, h, salt)
    sp.rect(2, 6, 4, 24, TIMBER[3])                        # posts
    sp.rect(w - 5, 6, w - 3, 24, TIMBER[3])
    for x in range(0, w):                                  # awning
        c = RED if (x // 6) % 2 == 0 else PAPER
        sp.rect(x, 0, x, 6, c)
        if x % 6 == 5:
            sp.set(x, 6, PAPERD)
    sp.rect(0, 7, w - 1, 7, TIMBER[4])                     # awning bar
    sp.rect(3, 16, w - 4, 17, TIMBER[1])                   # counter top
    sp.rect(3, 18, w - 4, 25, TIMBER[2])
    sp.rect(3, 25, w - 4, 25, TIMBER[4])
    gx = w // 2 - 8                                        # wares
    sp.rect(gx, 11, gx + 2, 15, MINT)
    sp.rect(gx + 5, 9, gx + 7, 15, VIOLETF)
    sp.rect(gx + 10, 12, gx + 11, 15, BRASS[1])
    sp.set(gx + 13, 13, BRASS[3])
    sp.set(gx + 1, 10, PAPERD)
    sp.rect(5, 26, 7, 31, TIMBER[4])                       # legs
    sp.rect(w - 8, 26, w - 6, 31, TIMBER[4])
    edge(sp, h)
    return sp
