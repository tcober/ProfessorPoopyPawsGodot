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
from _core import h2
from _overworld_props import (_hip_roof, _window, _chimney, _coursed_wall,
                              _hatch_px, DOORDARK, WARM, WARMD, CRYSTAL, BLOOM)
from _propkit import S, ln, edge
from _tilekit import (TIMBER, BRASS, STEEL, IRON, STONER, GLASS, MINT,
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


def _eave_lift(lo, up, w, fy, band=12):
    """Mirror a solid row's top pixels onto the UPPER canvas (pixel-identical
    composite): a body pressed against the row from the NORTH sinks its
    visual feet ~10px past its physics box into the row (plus sprite bottom
    and shadow), over the lower-layer art — the lifted band masks that
    sliver. A body pressed from the SOUTH is safe: its head tops out in the
    row's bottom ~3px, below a 12px band. Call after edge(up, …) so the band
    gets no outline of its own (it must blend seamlessly). This is the ONLY
    legal way to put upper art on a body-adjacent solid row (see the z-order
    doctrine's mask-band rule)."""
    for y in range(fy, fy + band):
        for x in range(w):
            p = lo.px[y][x]
            if p:
                up.px[y][x] = p


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
    _eave_lift(lo, up, w, fy)
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
    _eave_lift(lo, up, w, fy)
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


def town_shop(roof, plaster, sign, wares, salt=251):
    """A shuttered shopfront: 96x64 over 6x4 (2 roof + 2 facade rows).
    Cottage vocabulary plus a wide display window of wares under a striped
    awning and a hanging sign board whose glyph names the trade. BOTH shops
    call this with the SAME salt (only roof / sign / wares differ), so every
    plain facade cell dedupes between them — the reuse contract."""
    w, h, fy = 96, 64, 32
    dx0, dx1 = 49, 62                                      # leaf over the D cell
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # ---- lower: the facade
    lo.rect(0, fy, w - 1, h - 1, plaster[1])
    lo.rect(0, fy, 1, h - 1, TIMBER[3])                    # corner posts
    lo.rect(w - 2, fy, w - 1, h - 1, TIMBER[3])
    lo.rect(0, fy, w - 1, fy + 1, TIMBER[1])               # eave beam
    lo.rect(0, fy + 2, w - 1, fy + 2, TIMBER[3])
    lo.rect(2, h - 2, w - 3, h - 1, STONER[4])             # footing
    # the closed iron-strapped door (town's asleep)
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
    # the wide display window, wares on show behind dark glass
    wx, wy = 12, fy + 10
    _window(lo, wx, wy, 26, 16, GLASS, MINT)
    if wares == "arms":
        ln(lo, wx + 4, wy + 11, wx + 11, wy + 4, STEEL[1]) # a blade on its rack
        ln(lo, wx + 5, wy + 12, wx + 12, wy + 5, STEEL[3])
        lo.set(wx + 12, wy + 4, SPEC)
        lo.rect(wx + 15, wy + 8, wx + 18, wy + 11, BRASS[3])   # a gear
        lo.rect(wx + 16, wy + 9, wx + 17, wy + 10, BRASS[1])
        lo.set(wx + 16, wy + 9, TIMBER[5])
        lo.rect(wx + 21, wy + 9, wx + 23, wy + 12, IRON[2])    # a helm dome
        lo.set(wx + 21, wy + 9, IRON[1])
    else:                                                  # "tonics"
        lo.rect(wx + 4, wy + 7, wx + 6, wy + 12, MINT)     # a flask
        lo.set(wx + 5, wy + 5, PAPERD)
        lo.rect(wx + 10, wy + 9, wx + 11, wy + 12, VIOLETF)    # a vial
        lo.rect(wx + 15, wy + 11, wx + 19, wy + 12, PAPER)     # a scroll
        lo.set(wx + 17, wy + 11, PAPERD)
    # striped awning over the display window (the stall's cloth)
    for x in range(wx - 3, wx + 29):
        c = RED if ((x - wx + 3) // 5) % 2 == 0 else PAPER
        lo.rect(x, fy + 3, x, fy + 8, c)
        if (x - wx + 3) % 5 == 4:
            lo.set(x, fy + 9, PAPERD)
    lo.rect(wx - 3, fy + 8, wx + 28, fy + 8, TIMBER[4])    # awning bar
    # hanging sign right of the door
    sx = dx1 + 7
    lo.rect(sx, fy + 4, sx, fy + 11, IRON[2])              # bracket
    lo.rect(sx - 1, fy + 4, sx + 8, fy + 4, IRON[3])
    lo.rect(sx + 1, fy + 7, sx + 8, fy + 19, TIMBER[2])    # board
    lo.rect(sx + 1, fy + 7, sx + 8, fy + 7, TIMBER[1])
    if sign == "sword":
        lo.rect(sx + 4, fy + 9, sx + 5, fy + 14, STEEL[1]) # upright blade
        lo.set(sx + 4, fy + 9, SPEC)
        lo.rect(sx + 2, fy + 15, sx + 7, fy + 15, BRASS[1])    # crossguard
        lo.rect(sx + 4, fy + 16, sx + 5, fy + 17, TIMBER[3])   # grip
        lo.set(sx + 4, fy + 18, BRASS[3])                  # pommel
    else:                                                  # "flask"
        lo.rect(sx + 3, fy + 11, sx + 6, fy + 17, MINT)
        lo.rect(sx + 4, fy + 9, sx + 5, fy + 10, PAPERD)
    edge(lo, h)
    # ---- upper: roof + chimney + door-top strip (cottage idiom)
    _hip_roof(up, 0, w - 1, 0, fy - 1, w // 5, roof)
    _chimney(up, w * 2 // 3 + 6, 3, 16)
    up.rect(dx0 - 2, fy, dx1 + 2, fy + 1, TIMBER[1])
    up.rect(dx0 - 2, fy + 2, dx1 + 2, fy + 2, TIMBER[3])
    up.rect(dx0 - 2, fy + 3, dx1 + 2, fy + 8, TIMBER[4])   # casing head
    up.rect(dx0 - 1, fy + 9, dx1 + 1, fy + 9, TIMBER[1])   # lintel
    edge(up, fy + 10)
    _eave_lift(lo, up, w, fy)
    return lo, up


def town_inn(roof, plaster, salt=261):
    """The inn: 144x80 over 9x5 (2 roof + 3 facade rows) — the town's one
    two-story facade. A timber string-course splits the storeys, three lit
    upper windows over two lit lower ones (somebody's always awake at an
    inn), a heavy closed double door under a warm transom, a tankard sign,
    and a wall lantern (its light rides the glow overlay)."""
    w, h, fy = 144, 80, 32
    dx0, dx1 = 65, 78                                      # doors over the D cell
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # ---- lower: the two-story facade
    lo.rect(0, fy, w - 1, h - 1, plaster[1])
    lo.rect(0, fy, 2, h - 1, TIMBER[3])                    # corner posts
    lo.rect(w - 3, fy, w - 1, h - 1, TIMBER[3])
    lo.rect(0, fy, w - 1, fy + 1, TIMBER[1])               # eave beam
    lo.rect(0, fy + 2, w - 1, fy + 2, TIMBER[3])
    lo.rect(3, h - 2, w - 4, h - 1, STONER[4])             # footing
    lo.rect(0, fy + 18, w - 1, fy + 18, TIMBER[1])         # string course
    lo.rect(0, fy + 19, w - 1, fy + 19, TIMBER[3])
    for x in (32, 112):                                    # half-timber studs
        lo.rect(x, fy + 3, x + 1, fy + 17, TIMBER[2])
    # three lit upper windows
    for ux in (14, 44, 116):
        _window(lo, ux, fy + 4, 12, 13, WARMD, WARM)
    # the double door: heavy leaves, meeting stile, brass, warm transom
    lo.rect(dx0 - 3, fy + 20, dx1 + 3, h - 1, TIMBER[4])   # casing
    lo.rect(dx0, fy + 21, dx1, fy + 24, WARMD)             # transom light
    lo.rect(dx0 + 2, fy + 22, dx1 - 2, fy + 23, WARM)
    lo.rect(dx0 - 1, fy + 25, dx1 + 1, fy + 25, TIMBER[1]) # transom rail
    lo.rect(dx0, fy + 26, dx1, h - 1, TIMBER[2])           # the leaves
    lo.rect(dx0, fy + 26, dx0, h - 1, TIMBER[1])
    lo.rect(dx1, fy + 26, dx1, h - 1, TIMBER[4])
    cxd = (dx0 + dx1) // 2
    lo.rect(cxd, fy + 26, cxd, h - 1, TIMBER[5])           # meeting stile
    for by in (fy + 30, fy + 40):
        lo.rect(dx0, by, dx1, by, IRON[3])                 # iron straps
    lo.set(cxd - 2, fy + 35, BRASS[1])                     # ring handles
    lo.set(cxd - 2, fy + 36, BRASS[3])
    lo.set(cxd + 2, fy + 35, BRASS[1])
    lo.set(cxd + 2, fy + 36, BRASS[3])
    # two lit lower windows flanking the door
    _window(lo, 24, fy + 26, 13, 15, WARMD, WARM)
    _window(lo, 104, fy + 26, 13, 15, WARMD, WARM)
    # wall lantern left of the door (halo on the glow overlay)
    lx = dx0 - 9
    lo.rect(lx, fy + 26, lx, fy + 28, IRON[2])             # bracket
    lo.rect(lx - 1, fy + 29, lx + 1, fy + 33, BRASS[3])    # cage
    lo.rect(lx, fy + 30, lx, fy + 32, MINT)                # the mantle
    # the tankard sign right of the door
    sx = dx1 + 8
    lo.rect(sx, fy + 20, sx, fy + 26, IRON[2])             # bracket
    lo.rect(sx - 1, fy + 20, sx + 8, fy + 20, IRON[3])
    lo.rect(sx + 1, fy + 23, sx + 8, fy + 35, TIMBER[2])   # board
    lo.rect(sx + 1, fy + 23, sx + 8, fy + 23, TIMBER[1])
    lo.rect(sx + 3, fy + 27, sx + 6, fy + 32, BRASS[1])    # the tankard
    lo.rect(sx + 3, fy + 27, sx + 3, fy + 32, BRASS[0])
    lo.rect(sx + 3, fy + 26, sx + 6, fy + 26, PAPER)       # the foam head
    lo.set(sx + 5, fy + 25, PAPER)
    lo.set(sx + 7, fy + 28, BRASS[3])                      # handle arc
    lo.set(sx + 7, fy + 30, BRASS[3])
    edge(lo, h)
    # ---- upper: roof, twin flues, and the TALL door-top strip (three facade
    # rows put the head overlap zone a full row higher than the cottages)
    _hip_roof(up, 0, w - 1, 0, fy - 1, w // 5, roof)
    _chimney(up, 30, 3, 16)
    _chimney(up, w - 40, 4, 17)
    up.rect(dx0 - 3, fy, dx1 + 3, fy + 1, TIMBER[1])       # eave over the mouth
    up.rect(dx0 - 3, fy + 2, dx1 + 3, fy + 2, TIMBER[3])
    up.rect(dx0 - 3, fy + 3, dx1 + 3, fy + 17, plaster[1]) # wall over the door
    up.rect(dx0 - 3, fy + 18, dx1 + 3, fy + 18, TIMBER[1]) # string course
    up.rect(dx0 - 3, fy + 19, dx1 + 3, fy + 19, TIMBER[3])
    up.rect(dx0 - 3, fy + 20, dx1 + 3, fy + 20, TIMBER[4]) # casing head
    edge(up, fy + 21)
    _eave_lift(lo, up, w, fy)
    return lo, up


def town_fountain(stone, salt=271):
    """The square's fountain (48x48, 3x3 solid): a coursed stone basin,
    rippled pool, and a pedestal crowned by a brass alembic bulb — the
    town's little monument to the drained craft. Corners stay transparent
    so the plaza paving shows through."""
    sp = S(48, 48, salt)
    # the basin: stacked ellipses, sunlit N rim to shaded S wall
    sp.blob(24, 30, 21.5, 12.5, stone[3])                  # S wall shade base
    sp.blob(24, 28.5, 20.5, 11.5, stone[1])                # basin wall
    sp.blob(24, 27, 19.0, 10.5, stone[0])                  # lit rim
    sp.blob(24, 28, 15.5, 8.2, stone[3])                   # inner lip shade
    sp.blob(24, 29, 14.5, 7.4, WATER)                      # the pool
    for jx, jy in ((8, 24), (14, 19), (24, 17), (34, 19),  # rim course joints
                   (40, 24), (11, 33), (37, 33), (24, 38)):
        sp.set(jx, jy, stone[3])
    for rx0, rx1, ry in ((14, 20, 31), (27, 34, 29), (18, 24, 34)):
        sp.rect(rx0, ry, rx1, ry, GLASS)                   # ripple arcs
    sp.set(15, 30, SPEC)
    sp.set(33, 33, SPEC)
    # the pedestal and its brass alembic-bulb finial
    sp.rect(21, 12, 26, 27, stone[1])                      # column
    sp.rect(21, 12, 21, 27, stone[0])                      # lit W edge
    sp.rect(26, 12, 26, 27, stone[3])
    sp.blob(24, 28, 5.0, 2.0, stone[4])                    # foot in the water
    sp.rect(19, 10, 28, 11, stone[0])                      # cap course
    sp.set(19, 11, stone[3])
    sp.set(28, 11, stone[3])
    sp.rect(22, 7, 25, 9, BRASS[3])                        # the alembic neck
    sp.ball(23.5, 4, 3.8, 3.4, BRASS, power=2.0)           # the bulb
    sp.set(22, 2, SPEC)
    for py in (13, 17, 21):                                # pour streams
        sp.set(19, py, GLASS)
        sp.set(28, py + 2, GLASS)
    sp.set(19, 25, MINT)                                   # splash glints
    sp.set(28, 26, MINT)
    edge(sp, 48)
    return sp


def town_stairs(stone, salt=281):
    """The terrace's grand stair (32x32 over the 2x2 walkable S block):
    eight stone treads between rock cheek walls. FULLY OPAQUE and UNoutlined
    — the flight must butt seamlessly into the road above and below, and
    opaque cells dedupe no matter what the underlay phase does."""
    sp = S(32, 32, salt)
    for i in range(8):                                     # the treads
        y0 = i * 4
        sp.rect(0, y0, 31, y0, stone[1])                   # lit nose
        sp.rect(0, y0 + 1, 31, y0 + 2, stone[2])           # tread face
        sp.rect(0, y0 + 3, 31, y0 + 3, stone[4])           # riser shadow
    for x, y in ((9, 6), (21, 10), (13, 18), (24, 22),     # worn dabs
                 (7, 26), (18, 30)):
        sp.set(x, y, stone[3])
    for cx0 in (0, 28):                                    # cheek walls
        sp.rect(cx0, 0, cx0 + 3, 31, stone[3])
        for y in range(32):
            for x in range(cx0, cx0 + 4):
                if _hatch_px(x + salt, y, 5, 0, -1):
                    sp.set(x, y, stone[4])
        sp.rect(cx0, 0, cx0 + 3, 0, stone[1])              # lit crest
    sp.rect(3, 0, 3, 31, stone[5])                         # inner cheek shade
    sp.rect(28, 0, 28, 31, stone[5])
    return sp


def town_cliff(rock, grass, salt=291):
    """One 16x32 cliff-face column of the terrace band, stamped per column
    from three salted variants (the meadow-boulder pattern). FULLY OPAQUE,
    NO edge(): the underlay's 32-space phase varies beneath it, and a
    per-column outline would print a seam every 16px. Grass lip on top,
    lit brow, strata face, near-black foot."""
    sp = S(16, 32, salt)
    for x in range(16):
        lip = 3 + h2((x + salt) // 5, 0, salt) % 3         # ragged ledge, 5px runs
        for y in range(lip):
            c = grass[2]
            if h2(x, y, salt + 3) % 7 == 0:
                c = grass[1]                               # clump nicks
            sp.set(x, y, c)
        sp.set(x, lip, grass[4])                           # lip turn-under shadow
        sp.set(x, lip + 1, rock[0])                        # the sunlit brow
        sp.set(x, lip + 2, rock[0])
        sp.set(x, lip + 3, rock[1])
        for y in range(lip + 4, 32):                       # the face, darkening down
            if y >= 30:
                c = rock[5]                                # foot dark
            elif y >= 27:
                c = rock[4]
            elif y >= 21:
                c = rock[3]
            else:
                c = rock[2]
            sp.set(x, y, c)
        if h2(x, 29, salt) % 5 == 0:
            sp.set(x, 28, rock[3])                         # foot scree fleck
    for i, sy in enumerate((11, 16, 22)):                  # dashed strata cracks
        yy = sy + h2(i, 2, salt) % 3
        for x in range(16):
            if h2(x // 4 + i, 5, salt) % 3 != 0:
                sp.set(x, yy, rock[4] if yy < 21 else rock[5])
    cx = 3 + h2(salt, 7, 1) % 10                           # one long vertical crack
    ln(sp, cx, 10, cx + (salt % 3) - 1, 18, rock[4])
    ln(sp, cx + (salt % 3) - 1, 18, cx, 26, rock[5])
    clipw(sp, 16)
    return sp


def town_tree(f, trunk, grass, salt=301):
    """A town tree: (lower, upper) pair on 32x48 for a 2x3 FULLY SOLID
    footprint — a body-height tree is too small for a walk-behind corridor
    (the doctrine's small-prop rule: heads/ears poke over a 2-row crown),
    so nobody stands inside it; the crown rides the upper layer purely so a
    body passing east/west tucks its inner shoulder behind the silhouette,
    and a body pressed on the south face draws over the trunk row's art.
    The trunk row is FULLY OPAQUE (flat grass base under the crown shadow)
    so its tiles dedupe whatever the fabric phase beneath. Three salted
    variants; lobe geometry drifts with the salt."""
    w, h = 32, 48
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    o1 = salt % 3 - 1                                      # per-salt lobe drift
    o2 = (salt // 3) % 3 - 1
    # ---- lower: the opaque trunk row (y 32..47)
    for y in range(32, 48):
        for x in range(w):
            c = grass[2]
            r = h2(x, y, salt + 5) % 11
            if r == 0:
                c = grass[1]
            elif r == 1:
                c = grass[3]
            lo.set(x, y, c)
    lo.blob(16, 40, 13.5, 4.5, grass[4])                   # canopy ground shadow
    lo.blob(16, 40, 8.5, 3.0, grass[5])
    lo.capsule(16, 44, 9, 47, 2.5, 1.5, trunk)             # root flare
    lo.capsule(16, 44, 23, 47, 2.5, 1.5, trunk)
    lo.capsule(16, 46, 16, 30, 4.5, 3.5, trunk)            # the trunk
    for y in range(34, 46):                                # bark grooves
        hw = int(3.5 + (y - 30) / 16.0) - 1                # inside the taper
        for x in range(16 - hw, 16 + hw + 1):
            if (x + y // 5) % 4 == 0:
                lo.set(x, y, trunk[3])
    lo.rect(13, 36, 13, 43, trunk[1])                      # west rim light
    # ---- upper: the crown (rows 0-1) + its under-rim fringe into the trunk row
    for cx, cy, rx, ry, sh in ((10 + o1, 14, 9.5, 8.0, 0.10),
                               (22 + o2, 12, 9.5, 8.0, 0.04),
                               (16 + o1, 21, 11.0, 9.0, -0.06)):
        up.ball(cx, cy, rx, ry, f, sh=sh, power=2.2)
    up.blob(15 + o2, 15, 3.0, 1.8, f[4])                   # lobe seam shadow
    up.blob(16, 29, 10.0, 3.2, f[4])                       # crown under-rim
    up.blob(16, 32, 6.5, 2.2, f[5])
    up.blob(8 + o1, 6, 3.5, 2.2, f[0])                     # NW sun-catch
    up.set(7 + o1, 5, SPEC)
    if salt % 3 == 1:
        up.set(21 + o2, 8, BLOOM)                          # a surviving bloom
        up.set(11 + o1, 18, BLOOM)
    up.despeckle(2, 1)
    edge(up, 38)
    for y in range(up.n):                                  # clip lobe drift back
        for x in range(w, up.n):                           # into the footprint
            up.px[y][x] = None
    return lo, up
