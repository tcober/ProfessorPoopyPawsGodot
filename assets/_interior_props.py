#!/usr/bin/env python3
"""Interior prop library — every furniture object, authored once, reused by any room.

Each prop is a function returning a `_sprites.Sprite` (jitter=0: hard CT band
edges) sized to its map footprint in PIXELS; `_interior.Room.place()` blits it
(None-tracked, so terrain shows through the silhouette) after baking a
contact-shadow band. Round forms use the Sprite volume kit (`ball`, `capsule`,
`tri`) so they shade as lit volumes; boxy forms are hand-banded but finished
with outlines, creases and single-pixel speculars — the CT prop fidelity:
dark contact edges, 3-tone banding, one glint.

Never draw outside the (w, h) footprint — the Sprite may be bigger (it is
square) but the room owns the neighboring cells.

Stdlib-only, deterministic (fixed salts). Used by assets/_gen_tileset_*.py.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, lerp
from _palette import ramp
from _interior import (TIMBER, BRASS, STEEL, COPPER, IRON, GLASS, MINT,
                       VIOLETF, PAPER, PAPERD, RED, SPEC, WATER, STEAM)
from _propkit import S, ln, edge
from _pixfont import GLYPHS

LEAF = ramp((92, 168, 118), "violet", 4)      # plant foliage (the green accent)
EMBER = (216, 84, 52, 255)
FLAME = (255, 150, 70, 255)
FLAME_IN = (255, 208, 112, 255)
FLAME_CORE = (255, 244, 200, 255)
SUN = (255, 240, 196, 255)
SKYLINE = (58, 38, 92, 255)
FIREBOX = (14, 9, 22, 255)


# ====================================================================================
# structural / soft
# ====================================================================================


def window_geom(w, h, gable):
    """Shared geometry so the window prop, the curtain overlay and the glow
    config all agree: frame rect, glass rect, sill top, flask xs."""
    gh = 12 if gable else 0
    m = 1 if w < 40 else 2                     # small windows keep their glass
    fx0, fy0, fx1, fy1 = m, gh + 1, w - 1 - m, h - 9 - m
    gi = 2 if w < 40 else 3
    gx0, gy0, gx1, gy1 = fx0 + gi, fy0 + gi, fx1 - gi, fy1 - gi
    sill_y = h - 8 - m
    n = max(1, (w - 16) // 14)
    flask_xs = [6 + i * ((w - 14) // max(1, n)) for i in range(n)]
    return dict(gh=gh, frame=(fx0, fy0, fx1, fy1), glass=(gx0, gy0, gx1, gy1),
                sill_y=sill_y, flask_xs=flask_xs)


def sill_flasks(set_px, rect, xs, sill_y):
    """Stoppered glass flasks standing on a sill; drawn via callables so both
    the window Sprite and the curtain-overlay Img can render them in front."""
    liquids = (MINT, VIOLETF, MINT)
    for i, fx in enumerate(xs):
        liq = liquids[i % 3]
        top = sill_y - 10
        rect(fx + 1, top + 2, fx + 4, top + 4, liq)          # bulb
        rect(fx, top + 5, fx + 5, top + 9, liq)
        rect(fx, top + 2, fx, top + 9, GLASS)                # glass walls
        rect(fx + 5, top + 2, fx + 5, top + 9, GLASS)
        rect(fx + 2, top, fx + 3, top + 1, PAPERD)           # cork
        set_px(fx + 1, top + 3, SPEC)


def window(w, h, dawn, curt=None, gable=False, sun=True, flasks=True, salt=31):
    """Mullioned window: quantized dawn glass (the hot accent), optional dormer
    gable, tied-back curtains, sill with flasks or a sprout. Parameterized so
    every room's windows come from this one prop."""
    sp = S(w, h, salt)
    g = window_geom(w, h, gable)
    fx0, fy0, fx1, fy1 = g["frame"]
    gx0, gy0, gx1, gy1 = g["glass"]
    if gable:                                   # dormer wedge against the void
        cx = w // 2
        for y in range(3, g["gh"] + 1):
            half = 3 + (y - 3) * (w // 2 - 4) // max(1, g["gh"] - 3)
            sp.rect(cx - half, y, cx + half - 1, y, TIMBER[3])
            sp.set(cx - half, y, TIMBER[5])
            sp.set(cx + half - 1, y, TIMBER[5])
        sp.rect(cx - 2, 3, cx + 1, 4, TIMBER[5])             # peak cap
        sp.rect(cx - 2, g["gh"] - 5, cx + 1, g["gh"] - 2, BRASS[3])
        sp.rect(cx - 1, g["gh"] - 4, cx, g["gh"] - 3, BRASS[1])
    # frame with a lit inner bevel
    sp.rect(fx0, fy0, fx1, fy1, TIMBER[2])
    sp.rect(fx0, fy0, fx1, fy0, TIMBER[1])
    sp.rect(fx0, fy0, fx0, fy1, TIMBER[1])
    sp.rect(fx1, fy0, fx1, fy1, TIMBER[4])
    sp.rect(fx0, fy1, fx1, fy1, TIMBER[4])
    sp.rect(gx0 - 1, gy0 - 1, gx1 + 1, gy0 - 1, TIMBER[4])   # glass rebate
    # glass: hard dawn bands, gold dominant
    gh_px = gy1 - gy0 + 1
    stops = (0.38, 0.62, 0.80, 0.92, 1.01)
    y = gy0
    for bi, f in enumerate(stops):
        yb = min(gy1, gy0 + int(gh_px * f) - 1)
        if yb >= y:
            sp.rect(gx0, y, gx1, yb, dawn[bi])
        y = yb + 1
    for sx, sw, sh in ((2, 5, 4), (10, 3, 3), ((gx1 - gx0) - 9, 6, 5)):
        x0 = gx0 + sx
        if x0 + sw <= gx1:
            sp.rect(x0, gy1 - sh, x0 + sw, gy1, SKYLINE)     # rooftops
    if sun:
        scx, scy = gx0 + (gx1 - gx0) // 3, gy0 + gh_px // 4
        r = max(3, min(6, gh_px // 5))
        for dy in range(-r, r + 1):
            half = max(1, r - abs(dy))
            sp.rect(scx - half, scy + dy, scx + half, scy + dy, SUN)
        sp.rect(scx - 1, scy - 1, scx + 1, scy, (255, 252, 232, 255))
    sp.set(gx1 - 5, gy0 + 4, SKYLINE)                        # birds
    sp.set(gx1 - 6, gy0 + 3, SKYLINE)
    sp.set(gx1 - 4, gy0 + 3, SKYLINE)
    # mullion cross
    mx = (gx0 + gx1) // 2
    sp.rect(mx, gy0, mx, gy1, TIMBER[4])
    my = gy0 + int(gh_px * 0.55)
    sp.rect(gx0, my, gx1, my, TIMBER[4])
    # slim tied-back curtains
    if curt:
        for side in (0, 1):
            for yy in range(fy0 + 1, fy1):
                waist = fy0 + (fy1 - fy0) * 2 // 3
                pinch = 2 if waist - 3 <= yy <= waist + 1 else 0
                cw = 5 - pinch
                xa = (fx0 + 1 + pinch) if side == 0 else (fx1 - cw - pinch)
                for xx in range(xa, xa + cw):
                    u = (xx - xa) if side == 1 else (xa + cw - 1 - xx)
                    c = curt[0] if u == 0 else (curt[2] if u % 3 == 2 else curt[1])
                    sp.set(xx, yy, c)
            bx = fx0 + 1 if side == 0 else fx1 - 4
            sp.rect(bx, waist - 1, bx + 3, waist, BRASS[2])
    # sill
    sp.rect(0, g["sill_y"], w - 1, g["sill_y"] + 1, TIMBER[1])
    sp.rect(0, g["sill_y"] + 2, w - 1, h - 3, TIMBER[3])
    sp.rect(0, h - 2, w - 1, h - 2, TIMBER[5])
    if flasks:
        sill_flasks(sp.set, sp.rect, g["flask_xs"], g["sill_y"])
    else:                                                    # a sprout + a cup
        px = w // 2 - 5
        sp.rect(px, g["sill_y"] - 4, px + 3, g["sill_y"] - 1, COPPER[2])
        sp.rect(px + 1, g["sill_y"] - 6, px + 2, g["sill_y"] - 5, LEAF[1])
        sp.set(px, g["sill_y"] - 7, LEAF[2])
        sp.set(px + 3, g["sill_y"] - 6, LEAF[0])
        sp.rect(px + 8, g["sill_y"] - 4, px + 11, g["sill_y"] - 1, STEEL[2])
        sp.set(px + 12, g["sill_y"] - 3, STEEL[3])           # cup handle
    return sp


def rug(w, h, base, accent, salt=37):
    """CT area rug: bordered, 16-periodic diamond field (interior cells dedupe),
    corner tassels. Walkable — drawn fully opaque over the floor."""
    sp = S(w, h, salt)
    for y in range(h):
        for x in range(w):
            d = abs(2 * (x % 8) - 7) + abs(2 * (y % 8) - 7)   # diamond metric
            if d <= 4:
                c = accent                                    # filled diamond
            elif d == 6:
                c = base[1]                                   # its lit halo
            else:
                c = base[2] if (x + y) % 2 else base[3]       # tight weave
            sp.set(x, y, c)
    sp.rect(0, 0, w - 1, 0, base[4])                          # border
    sp.rect(0, h - 1, w - 1, h - 1, base[5])
    sp.rect(0, 0, 0, h - 1, base[4])
    sp.rect(w - 1, 0, w - 1, h - 1, base[5])
    sp.rect(1, 1, w - 2, 1, base[1])
    sp.rect(1, h - 2, w - 2, h - 2, base[4])
    sp.rect(1, 1, 1, h - 2, base[1])
    sp.rect(w - 2, 1, w - 2, h - 2, base[4])
    sp.rect(2, 2, w - 3, 2, accent)
    sp.rect(2, h - 3, w - 3, h - 3, accent)
    sp.rect(2, 2, 2, h - 3, accent)
    sp.rect(w - 3, 2, w - 3, h - 3, accent)
    for cx_, cy_ in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        sp.set(cx_, cy_, base[5])                             # corner knots
    return sp


def framed_picture(w, h, dawn, salt=41):
    """A little duotone landscape of the continent — teal hills, peach sky."""
    sp = S(w, h, salt)
    sp.rect(0, 0, w - 1, h - 1, TIMBER[3])
    sp.rect(0, 0, w - 1, 0, TIMBER[1])
    sp.rect(0, h - 1, w - 1, h - 1, TIMBER[5])
    sp.rect(0, 0, 0, h - 1, TIMBER[2])
    sp.rect(w - 1, 0, w - 1, h - 1, TIMBER[4])
    x0, y0, x1, y1 = 2, 2, w - 3, h - 3
    sp.rect(x0, y0, x1, y0 + (y1 - y0) // 2, dawn[1])         # sky
    sp.rect(x0, y0, x1, y0 + 1, dawn[0])
    for i, (hx, hw, hh) in enumerate(((1, 5, 3), (6, 7, 5), (12, 5, 2))):
        if x0 + hx + hw <= x1:
            sp.rect(x0 + hx, y1 - hh, x0 + hx + hw, y1, (62, 132, 138, 255))
    sp.rect(x0, y1 - 1, x1, y1, (44, 96, 110, 255))
    sp.set(x0 + 2, y0 + 2, SUN)
    sp.set(x0 + 3, y0 + 2, SUN)
    return sp


def wall_clock(salt=43):
    """Round brass clock with a short pendulum case — the CT wall clock."""
    sp = S(16, 16, salt)
    sp.ball(7.5, 6, 6, 6, BRASS, power=2.0)
    sp.blob(7.5, 6, 4, 4, PAPER)
    sp.set(7, 3, TIMBER[5])                                   # 12
    sp.set(7, 9, TIMBER[5])                                   # 6
    sp.set(4, 6, TIMBER[5])
    sp.set(11, 6, TIMBER[5])
    ln(sp, 7, 6, 7, 4, TIMBER[5])                             # hands
    ln(sp, 7, 6, 9, 6, TIMBER[4])
    sp.rect(6, 12, 9, 15, TIMBER[3])                          # pendulum case
    sp.rect(6, 12, 9, 12, TIMBER[1])
    sp.set(7, 14, BRASS[1])                                   # bob
    edge(sp)
    return sp


def potted_plant(w, h, salt=47):
    """Leafy plant in a clay pot; use 16x32 against a wall, 16x16 on the floor."""
    sp = S(w, h, salt)
    pw = w - 6
    px0, py0 = 3, h - 7
    sp.rect(px0, py0, px0 + pw - 1, py0 + 1, COPPER[1])       # pot rim
    sp.rect(px0 + 1, py0 + 2, px0 + pw - 2, h - 2, COPPER[2])
    sp.rect(px0 + 1, h - 2, px0 + pw - 2, h - 2, COPPER[4])
    sp.set(px0 + 1, py0 + 2, COPPER[0])
    fy = py0 - 2                                              # foliage clusters
    sp.ball(w // 2, fy - h // 4, w // 2 - 2, h // 3, LEAF, power=1.8)
    sp.ball(w // 2 - 3, fy - h // 8, 3, 4, LEAF)
    sp.ball(w // 2 + 3, fy - h // 3, 3, 4, LEAF)
    for fx, fy2 in ((w // 2 - 4, fy - h // 2), (w // 2 + 4, fy - h // 2 + 2)):
        sp.set(fx, max(1, fy2), LEAF[0])                      # leaf tips
    edge(sp)
    return sp


def dish_shelf(w, h, salt=53):
    """Open shelf of plates and cups over the kitchen counter."""
    sp = S(w, h, salt)
    sp.rect(0, h - 4, w - 1, h - 3, TIMBER[2])                # board
    sp.rect(0, h - 4, w - 1, h - 4, TIMBER[1])
    sp.rect(0, h - 2, w - 1, h - 2, TIMBER[4])
    sp.set(1, h - 1, TIMBER[4])                               # brackets
    sp.set(w - 2, h - 1, TIMBER[4])
    for i in range(3):                                        # upright plates
        px = 2 + i * 7
        sp.ball(px + 2.5, h - 9, 3, 4, STEEL, power=2.4)
        sp.blob(px + 2.5, h - 9, 1.5, 2.5, PAPER)
    cx = w - 8                                                # hanging cups
    sp.rect(cx, h - 9, cx + 3, h - 6, MINT)
    sp.rect(cx, h - 9, cx + 3, h - 9, (170, 255, 190, 255))
    sp.set(cx + 4, h - 8, MINT)
    edge(sp)
    return sp


# ====================================================================================
# bedroom
# ====================================================================================


def privacy_screen(w, h, linen, salt=67):
    """A folding three-panel linen ward screen on little timber feet — the
    hospital read in one prop (sickroom, 2026-07-16). Draw for a 2x1 solid
    footprint as a y-sorted entity: bodies pass both sides."""
    sp = S(w, h, salt)
    pw = w // 3
    for i in range(3):
        x0 = i * pw + (1 if i == 0 else 0)
        x1 = (i + 1) * pw - (2 if i == 2 else 0)
        top = 4 if i == 1 else 7                              # center panel proud
        sp.rect(x0, top, x1, h - 5, TIMBER[3])                # frame
        sp.rect(x0 + 1, top + 1, x1 - 1, h - 6, linen[1])     # linen field
        sp.rect(x0 + 1, top + 1, x1 - 1, top + 1, linen[0])
        sp.rect(x0 + 1, h - 6, x1 - 1, h - 6, linen[3])
        sp.rect(x0 + 1, top + 4, x1 - 1, top + 4, linen[2])   # seam
        sp.set(x0, top, TIMBER[1])                            # lit frame corner
        sp.rect(x0 + 1, h - 5, x0 + 2, h - 2, TIMBER[3])      # feet
        sp.rect(x1 - 2, h - 5, x1 - 1, h - 2, TIMBER[4])
    edge(sp)
    return sp


def drip_stand(w, h, salt=69):
    """A brass drip-stand: weighted tripod base, tall pole, crossarm, and a
    hanging tonic flask with a tube arcing off east toward the sickbed —
    candle-and-gear medicine (sickroom, 2026-07-16). One-cell footprint,
    y-sorted entity."""
    sp = S(w, h, salt)
    px_ = w // 2 - 1
    sp.rect(px_ - 4, h - 4, px_ + 5, h - 3, BRASS[3])         # base
    sp.rect(px_ - 2, h - 6, px_ + 3, h - 5, BRASS[2])
    sp.rect(px_, 4, px_ + 1, h - 6, BRASS[2])                 # pole
    sp.rect(px_, 4, px_, h - 6, BRASS[1])
    sp.rect(px_ - 3, 4, px_ + 4, 5, BRASS[1])                 # crossarm
    sp.set(px_ - 3, 6, BRASS[3])                              # hook
    sp.rect(px_ - 4, 7, px_ - 2, 13, GLASS)                   # hanging flask
    sp.rect(px_ - 4, 10, px_ - 2, 13, MINT)                   # the tonic
    sp.set(px_ - 4, 8, SPEC)
    sp.rect(px_ - 3, 13, px_ - 3, 15, GLASS)                  # flask neck
    # the tube, arcing east toward the bed
    ln(sp, px_ - 3, 16, px_ + 4, 22, COPPER[1])
    ln(sp, px_ + 4, 22, w - 1, 26, COPPER[1])
    edge(sp)
    return sp


def bed(w, h, quilt, linen, salt=3):
    sp = S(w, h, salt)
    for px in (0, w - 3):                                     # posts + ball caps
        sp.rect(px, 3, px + 2, 13, TIMBER[2])
        sp.ball(px + 1, 2, 1.6, 1.6, TIMBER)
        sp.rect(px + 2, 5, px + 2, 13, TIMBER[4])
    sp.rect(3, 4, w - 4, 12, TIMBER[2])                       # headboard, arched
    sp.rect(3, 4, w - 4, 5, TIMBER[1])
    sp.set(3, 4, TIMBER[3])
    sp.set(w - 4, 4, TIMBER[3])
    sp.rect(6, 7, w - 7, 8, TIMBER[4])                        # carved groove
    sp.rect(6, 7, w - 7, 7, TIMBER[1])
    sp.rect(3, 12, w - 4, 12, TIMBER[4])
    sp.ball(w / 2 - 0.5, 19, w / 2 - 5, 4.5, linen, power=2.6)   # pillow volume
    sp.rect(5, 23, w - 6, 23, linen[3])                       # pillow crease
    sp.rect(2, 24, w - 3, 27, linen[1])                       # folded sheet
    sp.rect(2, 24, w - 3, 24, linen[0])
    sp.rect(2, 27, w - 3, 27, linen[3])
    sp.rect(1, 28, w - 2, 51, quilt[1])                       # quilt field
    sp.rect(1, 28, w - 2, 29, quilt[0])
    for y in range(31, 51):                                   # sparse stitch dots
        for x in range(4, w - 4):
            if x % 8 == (0 if y % 16 < 8 else 4) and y % 8 == 2:
                sp.set(x, y, quilt[0])
                sp.set(x, y + 1, quilt[3])
    for fy in (36, 44):                                       # fold creases
        sp.rect(1, fy, w - 2, fy, quilt[3])
    sp.rect(1, 28, 2, 51, quilt[3])                           # side rolls
    sp.rect(w - 3, 28, w - 2, 51, quilt[3])
    sp.rect(1, 52, w - 2, 57, TIMBER[2])                      # footboard
    sp.rect(1, 52, w - 2, 52, TIMBER[1])
    sp.rect(4, 54, w - 5, 55, TIMBER[3])                      # panel
    sp.rect(1, 56, w - 2, 57, TIMBER[4])
    for px in (0, w - 3):
        sp.rect(px, 50, px + 2, 58, TIMBER[2])
        sp.ball(px + 1, 50, 1.6, 1.6, TIMBER)
    edge(sp)
    return sp


def desk(w, h, dawn, salt=5):
    """Research desk, drawn for life as a y-sorted scene ENTITY on a one-row
    solid footprint: a deep solid desktop plane (it hides the legs of a body
    walking the row behind; a body in front y-sorts over it), clutter
    standing on the plane, a brass-pulled drawer and legs below."""
    sp = S(w, h, salt)
    # the desktop plane first — a continuous band so legs vanish cleanly
    sp.rect(1, 6, w - 2, 7, TIMBER[0])                        # lit back edge
    sp.rect(1, 8, w - 2, 17, TIMBER[1])                       # surface
    for gx in range(4, w - 4, 9):
        sp.rect(gx, 10, gx + 4, 10, TIMBER[2])                # grain
        sp.rect(gx + 2, 14, gx + 6, 14, TIMBER[2])
    sp.rect(1, 18, w - 2, 18, TIMBER[2])                      # front lip
    sp.rect(1, 19, w - 2, 19, TIMBER[4])
    # clutter standing on the plane
    mx = 4                                                    # microscope
    sp.rect(mx, 8, mx + 8, 9, STEEL[2])
    sp.rect(mx + 5, 0, mx + 7, 7, STEEL[1])                   # tube
    sp.rect(mx + 7, 1, mx + 7, 7, STEEL[3])
    sp.rect(mx + 3, 3, mx + 4, 7, STEEL[2])                   # arm
    sp.set(mx + 5, 0, SPEC)
    sp.set(mx + 4, 6, MINT)                                   # slide on the stage
    bx = 18                                                   # open journal
    sp.rect(bx, 5, bx + 11, 10, PAPER)
    sp.rect(bx + 5, 5, bx + 6, 10, PAPERD)                    # gutter
    for yy in (6, 8):
        sp.rect(bx + 1, yy, bx + 4, yy, PAPERD)               # text
        sp.rect(bx + 7, yy, bx + 10, yy, PAPERD)
    ix = 33                                                   # inkwell + quill
    sp.rect(ix, 5, ix + 3, 9, IRON[3])
    sp.rect(ix, 5, ix + 3, 5, IRON[1])
    ln(sp, ix + 3, 4, ix + 7, 0, PAPER)
    lx = w - 8                                                # oil lamp
    sp.rect(lx, 8, lx + 4, 9, BRASS[2])
    sp.rect(lx + 1, 6, lx + 3, 7, BRASS[3])
    sp.rect(lx, 0, lx + 4, 5, GLASS)
    sp.rect(lx + 1, 1, lx + 3, 4, dawn[1])                    # flame
    sp.set(lx + 2, 1, SUN)
    # apron, hung drawer, legs (floor shows through the gap)
    sp.rect(2, 20, w - 3, 26, TIMBER[3])
    dx0, dx1 = 14, w - 14
    sp.rect(dx0, 21, dx1, 25, TIMBER[2])
    sp.rect(dx0, 21, dx1, 21, TIMBER[1])
    sp.rect(dx0, 25, dx1, 25, TIMBER[4])
    kx = (dx0 + dx1) // 2
    sp.rect(kx - 1, 23, kx + 1, 23, BRASS[1])                 # pull
    for px2 in (2, w - 6):
        sp.rect(px2, 27, px2 + 3, 31, TIMBER[3])              # legs
        sp.rect(px2 + 3, 27, px2 + 3, 31, TIMBER[4])
        sp.rect(px2, 31, px2 + 3, 31, TIMBER[4])
    edge(sp)
    return sp


def bed_parts(w, h, quilt, linen, cover_span=(24, 58), salt=3):
    """The bed split for the FF/CT under-the-covers read: returns
    (lower, cover). `lower` (headboard, pillow, contact shadow) bakes into
    the under-entities tiles; `cover` (linen fold + quilt + footboard) is a
    y-sorted scene entity whose baseline is the footboard's south edge — a
    body IN the bed sorts under it (only the head shows, on the pillow), a
    body south of the bed sorts over it."""
    full = bed(w, h, quilt, linen, salt)
    low = S(w, h, salt)
    cov = S(w, h, salt)
    y0, y1 = cover_span
    for y in range(full.n):
        for x in range(full.n):
            p = full.px[y][x]
            if p:
                (cov if y0 <= y <= y1 else low).px[y][x] = p
    return low, cov


def bookshelf(w, h, spines, salt=7):
    sp = S(w, h, salt)
    sp.rect(1, 1, w - 2, h - 2, TIMBER[4])                    # case
    sp.rect(2, 2, w - 3, h - 3, TIMBER[5])
    sp.rect(1, 1, w - 2, 2, TIMBER[2])                        # crown
    sp.rect(1, 1, w - 2, 1, TIMBER[1])
    for dx in range(3, w - 3, 3):
        sp.set(dx, 3, TIMBER[3])                              # dentil ticks
    sp.rect(1, h - 4, w - 2, h - 2, TIMBER[4])                # plinth
    sp.rect(1, h - 4, w - 2, h - 4, TIMBER[2])
    shelves = (h // 3, 2 * h // 3)
    for sy in shelves:
        sp.rect(2, sy, w - 3, sy + 1, TIMBER[3])
        sp.rect(2, sy, w - 3, sy, TIMBER[1])
    rows = ((4, shelves[0] - 1), (shelves[0] + 2, shelves[1] - 1))
    for row, (oy0, oy1) in enumerate(rows):
        sx = 3
        slot = 0
        while sx + 3 <= w - 4:
            k = h2(slot, row, 3)
            if k % 8 == 0:
                sx += 3                                       # dark gap
                slot += 1
                continue
            if k % 7 == 0 and sx + 7 <= w - 4:                # flat stack
                for i in range(3):
                    col = spines[(k + i) % 6]
                    sp.rect(sx, oy1 - 2 * i - 1, sx + 6, oy1 - 2 * i, col)
                sx += 8
                slot += 1
                continue
            hgt = 6 + k % 5
            col = spines[k % 6]
            lean = 1 if k % 5 == 0 else 0
            for yy in range(oy1 - hgt, oy1 + 1):
                off = lean * ((oy1 - yy) // 3)
                sp.rect(sx + off, yy, sx + 2 + off, yy, col)
            top = tuple(lerp(col[:3], (255, 255, 255), 0.35)) + (255,)
            sp.rect(sx + lean * (hgt // 3), oy1 - hgt,
                    sx + 2 + lean * (hgt // 3), oy1 - hgt, top)
            if k % 4 == 1:
                sp.set(sx + 1, oy1 - hgt // 2, top)           # band on the spine
            sx += 4
            slot += 1
    boy = shelves[1] + 2                                      # bottom: lab clutter
    sp.rect(4, h - 10, 11, h - 6, PAPER)                      # scroll
    sp.rect(4, h - 7, 11, h - 6, PAPERD)
    sp.set(4, h - 9, PAPERD)
    jx = w - 10
    sp.rect(jx, h - 12, jx + 5, h - 5, GLASS)                 # glow jar
    sp.rect(jx + 1, h - 9, jx + 4, h - 6, MINT)
    sp.set(jx + 1, h - 11, SPEC)
    gx = w // 2                                               # a spare gear
    sp.ball(gx, h - 8, 2.5, 2.5, BRASS)
    sp.set(gx, h - 8, TIMBER[5])
    edge(sp)
    return sp


def corkboard(w, h, quilt, salt=11):
    sp = S(w, h, salt)
    sp.rect(0, 0, w - 1, h - 1, TIMBER[3])
    sp.rect(0, 0, w - 1, 0, TIMBER[1])
    sp.rect(0, h - 1, w - 1, h - 1, TIMBER[5])
    for cx_, cy_ in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
        sp.set(cx_, cy_, BRASS[2])                            # corner screws
    corkf = ramp((182, 132, 92), "violet", 4)
    sp.rect(2, 2, w - 3, h - 3, corkf[2])
    for i in range(26):                                       # dense cork speckle
        px = 2 + h2(i, 0, 21) % (w - 5)
        py = 2 + h2(0, i, 22) % (h - 5)
        sp.set(px, py, corkf[3] if i % 3 else corkf[1])
    notes = ((4, 4, 6, 7, PAPER), (14, 6, 5, 5, MINT), (21, 3, 6, 6, PAPER),
             (8, 15, 6, 5, PAPER), (18, 14, 6, 7, (44, 40, 96, 255)))
    pins = []
    for nx, ny, nw, nh, col in notes:
        if nx + nw > w - 3 or ny + nh > h - 3:
            continue
        sp.rect(nx, ny, nx + nw - 1, ny + nh - 1, col)
        sp.rect(nx + 1, ny + nh - 1, nx + nw - 1, ny + nh - 1,
                PAPERD if col != PAPER else PAPERD)
        if col == (44, 40, 96, 255):                          # star chart
            for si in range(4):
                sp.set(nx + 1 + h2(si, 9, 5) % (nw - 2),
                       ny + 1 + h2(9, si, 6) % (nh - 2), SPEC)
        else:
            for ly in range(ny + 2, ny + nh - 2, 2):
                sp.rect(nx + 1, ly, nx + nw - 3, ly, PAPERD)
        pin = (nx + nw // 2, ny)
        sp.set(pin[0], pin[1], RED if len(pins) % 2 == 0 else BRASS[1])
        pins.append(pin)
    for a, b in zip(pins, pins[1:]):                          # the red string
        ln(sp, a[0], a[1], b[0], b[1], RED)
    return sp


def chair(salt=17):
    sp = S(16, 16, salt)
    sp.rect(3, 2, 12, 5, TIMBER[1])                           # seat
    sp.rect(3, 5, 12, 6, TIMBER[3])
    sp.rect(4, 7, 11, 13, TIMBER[2])                          # backrest
    sp.rect(4, 7, 11, 7, TIMBER[1])
    for gx in (6, 9):
        sp.rect(gx, 8, gx, 12, TIMBER[4])                     # slats
    sp.rect(4, 13, 11, 13, TIMBER[4])
    for px, py in ((3, 14), (12, 14)):                        # turned legs
        sp.set(px, py, TIMBER[4])
        sp.set(px, py + 1, TIMBER[5])
    edge(sp)
    return sp


# ====================================================================================
# kitchen
# ====================================================================================


def hearth(w, h, wall_stone, salt=19):
    """Stone hearth: keystone arch, mantel with candle + jar, kettle on a
    swing arm over a layered fire, andirons — the room's hot light source."""
    sp = S(w, h, salt)
    for y in range(h):                                        # masonry, varied bond
        for x in range(1, w - 1):
            v = y % 8
            u = (x + (5 if (y // 8) % 2 else 0)) % 13
            if v == 0 or u == 0:
                c = wall_stone[4]
            elif v == 1:
                c = wall_stone[1]
            else:
                c = wall_stone[2]
            sp.set(x, y, c)
    sp.rect(1, 0, w - 2, 0, wall_stone[1])                    # lit cap
    sp.rect(0, 0, 0, h - 1, wall_stone[5])                    # silhouette
    sp.rect(w - 1, 0, w - 1, h - 1, wall_stone[5])
    sp.rect(2, 14, w - 3, 15, TIMBER[1])                      # mantel shelf
    sp.rect(2, 16, w - 3, 17, TIMBER[3])
    cx_ = 8                                                   # candle
    sp.rect(cx_, 9, cx_ + 1, 13, PAPER)
    sp.set(cx_, 8, FLAME_IN)
    sp.set(cx_ + 1, 7, FLAME)
    jx = w - 12                                               # mantel jar
    sp.rect(jx, 9, jx + 4, 13, GLASS)
    sp.rect(jx + 1, 11, jx + 3, 12, VIOLETF)
    # firebox arch with keystone
    fx0, fx1 = 10, w - 11
    sp.rect(fx0, 24, fx1, h - 5, FIREBOX)
    sp.rect(fx0 + 2, 22, fx1 - 2, 23, FIREBOX)                # arched top
    sp.rect(fx0 - 1, 24, fx0 - 1, h - 5, wall_stone[5])
    sp.rect(fx1 + 1, 24, fx1 + 1, h - 5, wall_stone[5])
    sp.rect((fx0 + fx1) // 2 - 1, 19, (fx0 + fx1) // 2 + 1, 22, wall_stone[1])
    # the fire itself is the ANIMATED overlay (fire_frames) stamped by the
    # scene over the firebox — the baked prop keeps only the cold iron
    mid = (fx0 + fx1) // 2
    for ax in (fx0 + 3, fx1 - 4):                             # andirons
        sp.rect(ax, h - 9, ax + 1, h - 5, IRON[3])
        sp.set(ax, h - 10, IRON[1])
    ka = mid + 6                                              # kettle on swing arm
    sp.rect(fx1 - 1, 26, ka, 26, IRON[3])
    sp.set(ka, 27, IRON[3])
    sp.ball(ka, 31, 3, 3, IRON, power=1.8)
    sp.rect(ka - 3, 29, ka + 3, 29, IRON[1])
    # hearthstone lip
    sp.rect(1, h - 4, w - 2, h - 4, wall_stone[1])
    sp.rect(1, h - 3, w - 2, h - 1, wall_stone[3])
    return sp


def sink_counter(w, h, salt=23):
    """Kitchen counter with an inset basin, brass faucet, cabinet + towel."""
    sp = S(w, h, salt)
    sp.rect(0, 6, w - 1, 8, TIMBER[1])                        # worktop
    sp.rect(0, 9, w - 1, 10, TIMBER[2])
    sp.rect(0, 11, w - 1, 11, TIMBER[4])
    bx0, bx1 = 4, w - 12                                      # basin
    sp.rect(bx0, 6, bx1, 9, STEEL[3])
    sp.rect(bx0 + 1, 7, bx1 - 1, 9, WATER)
    sp.set(bx0 + 2, 7, SPEC)
    sp.rect(bx0 - 1, 6, bx0 - 1, 9, STEEL[1])
    fx = bx1 + 3                                              # gooseneck faucet
    sp.rect(fx, 2, fx, 6, BRASS[2])
    sp.rect(fx, 2, fx + 3, 2, BRASS[1])
    sp.set(fx + 3, 3, BRASS[2])
    sp.set(fx + 3, 4, WATER)                                  # drip
    px = w - 6                                                # plate + brush
    sp.ball(px, 8, 2.5, 1.5, STEEL, power=2.6)
    sp.rect(px + 2, 5, px + 3, 7, TIMBER[2])
    sp.rect(0, 12, w - 1, h - 3, TIMBER[3])                   # cabinet
    for dx0, dx1 in ((2, w // 2 - 2), (w // 2 + 1, w - 3)):
        sp.rect(dx0, 13, dx1, h - 5, TIMBER[2])
        sp.rect(dx0, 13, dx1, 13, TIMBER[1])
        sp.rect(dx0, h - 5, dx1, h - 5, TIMBER[4])
        sp.set((dx0 + dx1) // 2, (13 + h - 5) // 2, BRASS[1])
    tx = w // 2 - 3                                           # hanging towel
    sp.rect(tx, 12, tx + 5, 12, BRASS[3])                     # bar
    sp.rect(tx + 1, 13, tx + 4, 19, MINT)
    sp.rect(tx + 1, 16, tx + 4, 16, (100, 200, 150, 255))
    sp.rect(0, h - 2, w - 1, h - 1, TIMBER[5])                # plinth shadow
    return sp


def table(w, h, salt=59):
    """Round pedestal table with a teapot and cups — lives on the rug."""
    sp = S(w, h, salt)
    sp.ball(w / 2 - 0.5, 10, w / 2 - 2, 6, TIMBER, power=2.4) # top
    sp.rect(3, 14, w - 4, 15, TIMBER[4])                      # rim shadow
    sp.rect(w // 2 - 2, 16, w // 2 + 1, h - 6, TIMBER[3])     # pedestal
    sp.rect(w // 2 + 1, 16, w // 2 + 1, h - 6, TIMBER[4])
    sp.rect(w // 2 - 5, h - 6, w // 2 + 4, h - 5, TIMBER[3])  # feet
    sp.rect(w // 2 - 5, h - 4, w // 2 + 4, h - 4, TIMBER[5])
    tx = w // 2 - 6                                           # teapot
    sp.ball(tx, 7, 3.5, 3, STEEL, power=1.9)
    sp.rect(tx - 5, 6, tx - 4, 7, STEEL[2])                   # spout
    sp.set(tx + 4, 6, STEEL[3])                               # handle
    sp.set(tx, 3, STEEL[1])                                   # lid knob
    sp.set(tx - 5, 4, STEAM)
    for cxx in (w // 2 + 3, w // 2 + 8):                      # cups
        if cxx < w - 3:
            sp.rect(cxx, 7, cxx + 2, 9, MINT)
            sp.set(cxx + 1, 7, (170, 255, 190, 255))
    edge(sp)
    return sp


# ====================================================================================
# lab
# ====================================================================================


def flask_shelf(w, h, salt=61):
    """Lab shelf: round-bottom flask, erlenmeyer, test-tube rack, bubbling
    retort, labels and a condenser coil."""
    sp = S(w, h, salt)
    sp.rect(1, 1, w - 2, h - 2, TIMBER[4])                    # case
    sp.rect(2, 2, w - 3, h - 3, TIMBER[5])
    sp.rect(1, 1, w - 2, 2, TIMBER[2])
    sp.rect(1, 1, w - 2, 1, TIMBER[1])
    sy = h // 2                                               # mid shelf
    sp.rect(2, sy, w - 3, sy + 1, TIMBER[3])
    sp.rect(2, sy, w - 3, sy, TIMBER[1])
    sp.rect(1, h - 3, w - 2, h - 2, TIMBER[4])                # plinth
    # top row
    sp.ball(8, sy - 5, 4, 4, [GLASS, GLASS, VIOLETF, VIOLETF], power=1.9)  # round flask
    sp.rect(7, sy - 12, 9, sy - 8, GLASS)                     # its neck
    sp.set(6, sy - 7, SPEC)
    ex = 18                                                   # erlenmeyer
    sp.tri((ex + 3, sy - 11), sy - 2, ex, ex + 6, [GLASS, MINT, MINT, MINT])
    sp.rect(ex + 2, sy - 13, ex + 4, sy - 11, GLASS)
    sp.set(ex + 1, sy - 5, SPEC)
    rx = 29                                                   # test-tube rack
    sp.rect(rx, sy - 3, rx + 12, sy - 2, TIMBER[2])
    for i, col in enumerate((MINT, VIOLETF, RED)):
        tx = rx + 1 + i * 4
        sp.rect(tx, sy - 9, tx + 1, sy - 3, GLASS)
        sp.rect(tx, sy - 6, tx + 1, sy - 3, col)
    # bottom row
    bx = 7                                                    # bubbling retort
    sp.ball(bx, h - 8, 4, 3.5, [GLASS, MINT, MINT, MINT], power=1.9)
    sp.rect(bx + 3, h - 13, bx + 9, h - 12, GLASS)            # swan neck
    sp.set(bx - 1, h - 15, STEAM)
    sp.set(bx + 1, h - 17, STEAM)
    sp.set(bx - 1, h - 10, SPEC)
    for i, cy_ in enumerate(range(h - 13, h - 5, 2)):         # condenser coil
        sp.rect(22, cy_, 32, cy_, COPPER[1 + (i % 2)])
    sp.rect(22, h - 13, 22, h - 5, COPPER[3])
    sp.rect(32, h - 13, 32, h - 5, COPPER[3])
    lx = w - 10                                               # labeled bottle
    sp.rect(lx, h - 11, lx + 4, h - 5, GLASS)
    sp.rect(lx + 1, h - 8, lx + 3, h - 6, VIOLETF)
    sp.rect(lx + 1, h - 10, lx + 3, h - 9, PAPER)             # label
    return sp


def boiler_frames(w=32, h=56, n=4):
    """The lab boiler as a FREE-STANDING ANIMATED ENTITY (n frames): a tall
    riveted copper tank on iron feet — gauge needle wiggling, firebox glow
    flickering, a lazy steam leak rising off the safety valve. The scene
    stamps the sheet as a y-sorted Sprite2D; collision comes from the map's
    solid cells as ever."""
    frames = []
    bx0, bx1 = 3, w - 4
    cx = (bx0 + bx1) / 2
    for f in range(n):
        sp = S(w, h, salt=67 + f)
        # safety valve + release stub up top (steam source)
        sp.rect(int(cx) - 2, 1, int(cx) + 1, 5, BRASS[2])
        sp.rect(int(cx) - 2, 1, int(cx) + 1, 1, BRASS[1])
        sp.rect(int(cx) - 4, 3, int(cx) + 3, 3, BRASS[3])     # valve wheel bar
        sp.rect(int(cx) + 2, 4, int(cx) + 5, 4, COPPER[3])    # release stub
        # dome + barrel: volume, then hard structure re-asserted
        sp.ball(cx, 12, (bx1 - bx0) / 2 - 1, 7, COPPER, sh=0.10, power=1.7)
        sp.capsule(cx, 16, cx, h - 16, (bx1 - bx0) / 2, (bx1 - bx0) / 2, COPPER,
                   sh=0.14, wrap=0.36, curve=0.22)
        sp.rect(bx0, 16, bx0, h - 14, COPPER[5])              # silhouette columns
        sp.rect(bx0 + 1, 14, bx0 + 1, h - 14, COPPER[4])
        sp.rect(bx1, 16, bx1, h - 14, COPPER[5])
        sp.rect(bx1 - 1, 14, bx1 - 1, h - 14, COPPER[4])
        sp.rect(bx0 + 3, 7, bx1 - 3, 7, COPPER[0])            # dome crown glint
        for ry in (18, 36):                                   # riveted seams
            sp.rect(bx0 + 1, ry, bx1 - 1, ry, COPPER[5])
            for rx in range(bx0 + 3, bx1 - 1, 4):
                sp.set(rx, ry - 1, COPPER[0])
                sp.set(rx, ry, COPPER[5])
        sp.rect(bx0 + 1, 26, bx1 - 1, 28, IRON[3])            # belly strap
        sp.rect(bx0 + 1, 26, bx1 - 1, 26, IRON[1])
        gx, gy = int(cx), 22                                  # gauge, dark bezel
        sp.blob(gx, gy, 4.6, 4.6, BRASS[3])
        sp.blob(gx, gy, 3.6, 3.6, BRASS[1])
        sp.blob(gx, gy, 2.4, 2.4, GLASS)
        ndx, ndy = ((0, -2), (1, -2), (1, -1), (0, -2))[f % 4]
        sp.set(gx, gy, RED)                                   # wiggling needle
        sp.set(gx + ndx, gy + ndy, RED)
        sp.set(gx, gy - 4, IRON[3])
        sp.set(gx + 4, gy, IRON[3])
        sp.set(gx - 4, gy, IRON[3])
        # firebox: iron door, flickering grate
        sp.rect(bx0 + 1, h - 14, bx1 - 1, h - 4, IRON[3])
        sp.rect(bx0 + 1, h - 14, bx1 - 1, h - 14, IRON[1])
        glow = (FLAME, FLAME_IN, FLAME, EMBER)[f % 4]
        core = (FLAME_IN, FLAME_CORE, FLAME_IN, FLAME)[f % 4]
        sp.rect(bx0 + 4, h - 11, bx1 - 4, h - 9, glow)
        sp.rect(bx0 + 6, h - 10, bx1 - 6, h - 10, core)
        for rx in (bx0 + 2, bx1 - 2):
            sp.set(rx, h - 6, IRON[1])                        # door rivets
        for px2 in (bx0 + 1, bx1 - 3):                        # feet
            sp.rect(px2, h - 4, px2 + 2, h - 1, IRON[2])
            sp.rect(px2, h - 1, px2 + 2, h - 1, IRON[3])
        # the steam leak: two puffs cycling upward off the release stub
        sx = int(cx) + 5
        for k in (0, 1):
            py = 4 - ((f + 2 * k) % 4) * 2
            if py >= 0:
                sp.set(sx + ((f + k) % 2), py, STEAM)
        edge(sp)
        frames.append(sp)
    return frames


def fire_frames(w=28, h=24, n=3):
    """The hearth fire as an animated overlay: ember bed + swaying tongues,
    one drifting spark. Stamped by the scene over the baked (cold) firebox."""
    sways = ((0, 0, 0), (1, -1, 1), (-1, 1, 0))
    hgts = ((8, 14, 10), (9, 12, 11), (7, 13, 9))
    frames = []
    for f in range(n):
        sp = S(w, h, salt=80 + f)
        mid = w // 2
        sp.rect(2, h - 4, w - 3, h - 2, EMBER)                # ember bed
        for i in range(3):
            sp.set(4 + h2(i, f, 9) % (w - 8), h - 3,
                   FLAME_IN if (i + f) % 2 else EMBER)        # winking embers
        for ti, (dx0, hg) in enumerate(zip((-8, 0, 6), hgts[f])):
            dx = dx0 + sways[f][ti]
            sp.tri((mid + dx, h - 3 - hg), h - 3, mid + dx - 3, mid + dx + 3, FLAME)
        sp.tri((mid + sways[f][1], h - hgts[f][1]), h - 3, mid - 2, mid + 2, FLAME_IN)
        sp.rect(mid - 1, h - 7, mid + 1, h - 3, FLAME_CORE)
        sp.set(mid - 5 + f * 3, h - 15 - f, FLAME_IN if f % 2 else FLAME)
        frames.append(sp)
    return frames


def pipe_wall(w, h, salt=79):
    """Copper manifold on the lab wall: a flanged horizontal run, a valve
    wheel, a small dial, and the drop pipe that feeds the boiler standing
    below. Transparent — the wall planks show behind the runs."""
    sp = S(w, h, salt)
    sp.rect(2, 8, w - 6, 8, COPPER[1])                        # horizontal run
    sp.rect(2, 9, w - 6, 10, COPPER[2])
    sp.rect(2, 11, w - 6, 11, COPPER[4])
    for fx in (6, 22, 34):                                    # flange pairs
        sp.rect(fx, 7, fx + 1, 12, COPPER[5])
        sp.set(fx, 7, COPPER[0])
    dx0 = w - 10                                              # drop to the boiler
    sp.rect(dx0, 8, dx0 + 3, h - 1, COPPER[2])
    sp.rect(dx0, 8, dx0, h - 1, COPPER[1])
    sp.rect(dx0 + 3, 8, dx0 + 3, h - 1, COPPER[4])
    for fy in (14, 30, h - 4):
        sp.rect(dx0 - 1, fy, dx0 + 4, fy, IRON[3])            # collars
        sp.set(dx0 - 1, fy, IRON[1])
    sx = 10                                                   # short capped spur
    sp.rect(sx, 11, sx + 3, 22, COPPER[3])
    sp.rect(sx, 11, sx, 22, COPPER[2])
    sp.rect(sx - 1, 22, sx + 4, 23, IRON[3])                  # end cap
    vx, vy = 20, 24                                           # valve wheel
    sp.rect(vx + 1, 12, vx + 2, vy, COPPER[3])                # its riser
    sp.ball(vx + 1.5, vy, 4, 4, BRASS, power=2.0)
    sp.set(vx + 1, vy, TIMBER[5])
    sp.set(vx - 2, vy, BRASS[3])
    sp.set(vx + 5, vy, BRASS[3])
    sp.set(vx + 1, vy - 3, BRASS[0])                          # spoke glint
    gx2, gy2 = 32, 20                                         # small dial
    sp.blob(gx2, gy2, 3.4, 3.4, BRASS[3])
    sp.blob(gx2, gy2, 2.4, 2.4, PAPER)
    sp.set(gx2, gy2, RED)
    sp.set(gx2 - 1, gy2 - 1, RED)
    for bx2, by2 in ((4, 12), (30, 12), (dx0 + 1, h - 2)):    # wall brackets
        sp.set(bx2, by2, TIMBER[5])
    return sp


def workbench(w, h, salt=71):
    """Lab workbench: vise, gear pair, half-built gizmo with lamps, tools,
    scattered screws, a small drawer — open table over the floor."""
    sp = S(w, h, salt)
    # tabletop
    sp.rect(1, 10, w - 2, 12, TIMBER[1])
    for gx in range(5, w - 5, 11):
        sp.rect(gx, 11, gx + 5, 11, TIMBER[2])                # grain
    sp.rect(20, 11, 26, 12, TIMBER[3])                        # scorch mark
    sp.rect(1, 13, w - 2, 14, TIMBER[2])
    sp.rect(1, 15, w - 2, 15, TIMBER[4])
    # clutter on the edge at y=10
    sp.rect(1, 6, 3, 9, IRON[2])                              # vise body
    sp.rect(0, 4, 4, 5, IRON[1])                              # jaw
    sp.rect(4, 7, 6, 7, IRON[3])                              # screw handle
    sp.set(6, 7, BRASS[1])
    gzx = 12                                                  # gizmo
    sp.rect(gzx, 3, gzx + 8, 9, BRASS[2])
    sp.rect(gzx, 3, gzx + 8, 3, BRASS[1])
    sp.rect(gzx, 9, gzx + 8, 9, BRASS[3])
    sp.set(gzx + 2, 5, RED)                                   # lamps
    sp.set(gzx + 6, 5, MINT)
    sp.rect(gzx + 3, 7, gzx + 5, 7, IRON[3])                  # vents
    sp.rect(gzx + 4, 0, gzx + 4, 2, STEEL[2])                 # antenna
    sp.set(gzx + 4, 0, SPEC)
    ln(sp, gzx + 8, 8, gzx + 12, 9, COPPER[1])                # trailing wire
    gx1, gy1 = 30, 6                                          # gear pair
    sp.ball(gx1, gy1, 3.5, 3.5, BRASS, power=2.2)
    for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4)):
        sp.set(gx1 + dx, gy1 + dy, BRASS[3])
    sp.set(gx1, gy1, TIMBER[5])
    sp.ball(gx1 + 6, gy1 + 2, 2, 2, STEEL, power=2.2)
    sp.set(gx1 + 6, gy1 + 2, TIMBER[5])
    wx = 44                                                   # wrench + screwdriver
    sp.rect(wx, 8, wx + 9, 9, STEEL[2])
    sp.rect(wx + 8, 5, wx + 11, 9, STEEL[1])
    sp.set(wx + 10, 7, TIMBER[5])
    sp.rect(wx + 2, 4, wx + 6, 4, STEEL[3])                   # screwdriver shaft
    sp.rect(wx + 7, 4, wx + 9, 4, TIMBER[2])                  # its handle
    for sx_, sy_ in ((26, 9), (39, 8), (41, 9)):              # loose screws
        sp.set(sx_, sy_, STEEL[3])
    # legs + stretcher + side drawer (floor shows through the middle)
    for px2 in (2, w - 6):
        sp.rect(px2, 16, px2 + 3, h - 3, TIMBER[3])
        sp.rect(px2 + 3, 16, px2 + 3, h - 3, TIMBER[4])
        sp.rect(px2, h - 4, px2 + 3, h - 3, TIMBER[4])
    sp.rect(6, h - 7, w - 7, h - 6, TIMBER[3])                # stretcher bar
    sp.rect(w - 18, 16, w - 7, 22, TIMBER[2])                 # hung drawer
    sp.rect(w - 18, 16, w - 7, 16, TIMBER[1])
    sp.rect(w - 18, 22, w - 7, 22, TIMBER[4])
    sp.set(w - 13, 19, BRASS[1])
    edge(sp)
    return sp


def armchair(w, h, quilt, salt=73):
    """Upholstered reading chair — the CT red-sofa energy, in house magenta.
    Hand-banded so back / arms / cushion stay distinct shapes."""
    sp = S(w, h, salt)
    sp.rect(6, 2, w - 7, 12, quilt[1])                        # backrest
    sp.rect(7, 2, w - 8, 2, quilt[0])                         # its lit crown
    sp.set(6, 2, None)
    sp.set(w - 7, 2, None)                                    # rounded corners
    sp.set(6, 3, quilt[0])
    sp.set(w - 7, 3, quilt[2])
    sp.rect(6, 11, w - 7, 12, quilt[3])                       # back-seat seam
    sp.rect(9, 5, w - 10, 5, quilt[2])                        # tuft line
    sp.rect(6, 13, w - 7, 19, quilt[1])                       # seat cushion
    sp.rect(6, 13, w - 7, 13, quilt[0])
    sp.rect(6, 19, w - 7, 19, quilt[3])
    for ax in (1, w - 6):                                     # rolled arms
        sp.rect(ax, 8, ax + 4, 21, quilt[2])
        sp.rect(ax + 1, 7, ax + 3, 7, quilt[1])
        sp.rect(ax + 1, 8, ax + 3, 9, quilt[0])               # roll highlight
        sp.rect(ax, 21, ax + 4, 21, quilt[3])
        sp.rect(ax + (4 if ax == 1 else 0), 10, ax + (4 if ax == 1 else 0), 20,
                quilt[3])                                     # inner shadow line
    sp.rect(4, 22, w - 5, 26, quilt[2])                       # skirt
    sp.rect(4, 22, w - 5, 22, quilt[3])
    sp.rect(4, 26, w - 5, 26, quilt[3])
    bx = w - 11                                               # book on the arm
    sp.rect(bx, 5, bx + 4, 7, PAPER)
    sp.rect(bx + 2, 5, bx + 2, 7, PAPERD)
    for px2 in (4, w - 6):                                    # wooden feet
        sp.rect(px2, 27, px2 + 1, 29, TIMBER[3])
        sp.set(px2, 29, TIMBER[5])
    edge(sp)
    return sp


# ====================================================================================
# academy hall (Prologue B — the lecture, 2026-07-12)
# ====================================================================================


def _stamp_glyphs(sp, text, x, y, color, spacing=6):
    """Chalk-stamp `text` (uppercase) via the shared 5x7 pixel font, straight
    onto the Sprite. Kept local to the props kit — draw_text() wants a pixel
    callback and this just needs sp.set on filled cells."""
    cx = x
    for ch in text.upper():
        rows = GLYPHS.get(ch, GLYPHS.get("?"))
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "X":
                    sp.set(cx + rx, y + ry, color)
        cx += spacing


def chalkboard(w, h, chalk, salt=11):
    """The Academy's slate lecture board (the corkboard skeleton, re-skinned):
    a timber frame around a dark slate field with a chalk 'RE-ENCHANTMENT'
    scrawl, an underline, a little sketched diagram, and a chalk tray. The
    thesis title on the wall — the scene of the humiliation."""
    sp = S(w, h, salt)
    sp.rect(0, 0, w - 1, h - 1, TIMBER[3])                    # frame
    sp.rect(0, 0, w - 1, 0, TIMBER[1])
    sp.rect(0, h - 1, w - 1, h - 1, TIMBER[5])
    for cx_, cy_ in ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2)):
        sp.set(cx_, cy_, BRASS[2])                            # corner bosses
    slate = ramp((44, 52, 66), "violet", 4)
    sp.rect(3, 3, w - 4, h - 6, slate[2])                     # slate field
    for i in range(18):                                       # faint wipe streaks
        sx = 4 + h2(i, 0, 21) % (w - 8)
        sy = 4 + h2(0, i, 22) % (h - 10)
        sp.set(sx, sy, slate[1])
    _stamp_glyphs(sp, "RE-ENCHANTMENT", 6, 6, chalk[0])
    sp.rect(6, 15, w - 20, 15, chalk[1])                      # underline
    _stamp_glyphs(sp, "MAGIC SLEEPS", 6, 19, chalk[1])
    # a little chalk diagram: a flask feeding a spark
    dx, dy = w - 22, 18
    sp.rect(dx, dy, dx + 5, dy + 6, chalk[1])                 # flask body
    sp.rect(dx + 2, dy - 2, dx + 3, dy - 1, chalk[1])         # neck
    for (ox, oy) in ((dx + 8, dy), (dx + 10, dy + 2), (dx + 8, dy + 4),
                     (dx + 11, dy - 1)):                      # spark rays
        sp.set(ox, oy, chalk[0])
    sp.rect(3, h - 5, w - 4, h - 4, TIMBER[2])                # chalk tray
    sp.rect(3, h - 5, w - 4, h - 5, TIMBER[1])
    sp.rect(6, h - 6, 9, h - 6, chalk[0])                     # a chalk stick
    edge(sp)
    return sp


def lectern(w, h, salt=5):
    """The speaker's lectern (the desk y-sorted pattern): a slanted podium top
    on a turned column, an open manuscript catching the light, a brass reading
    lamp. Drawn as a scene ENTITY so a body rounds it."""
    sp = S(w, h, salt)
    # slanted reading top
    for i in range(w - 4):
        yy = 4 + i * 5 // (w - 4)
        sp.set(2 + i, yy, TIMBER[0])
        sp.rect(2 + i, yy + 1, 2 + i, yy + 4, TIMBER[1])
        sp.set(2 + i, yy + 5, TIMBER[3])
    sp.rect(2, 9, w - 3, 10, TIMBER[2])                       # front lip
    sp.rect(2, 11, w - 3, 11, TIMBER[4])
    # the open manuscript on the slope
    mx = 5
    sp.rect(mx, 3, mx + 12, 7, PAPER)
    sp.rect(mx + 6, 3, mx + 6, 7, PAPERD)                     # gutter
    for yy in (4, 6):
        sp.rect(mx + 1, yy, mx + 4, yy, PAPERD)
        sp.rect(mx + 8, yy, mx + 11, yy, PAPERD)
    lx = w - 8                                                # brass reading lamp
    sp.rect(lx, 2, lx + 3, 2, BRASS[2])
    sp.rect(lx + 1, 0, lx + 2, 1, BRASS[1])
    sp.set(lx + 1, 1, MINT)
    # turned column + splayed foot (floor shows past it)
    cx = w // 2
    sp.rect(cx - 2, 12, cx + 1, h - 6, TIMBER[2])
    sp.rect(cx - 2, 12, cx - 2, h - 6, TIMBER[1])
    sp.rect(cx + 1, 12, cx + 1, h - 6, TIMBER[4])
    sp.rect(cx - 4, 16, cx + 3, 17, TIMBER[3])                # collar
    sp.rect(cx - 5, h - 5, cx + 4, h - 4, TIMBER[3])          # foot
    sp.rect(cx - 5, h - 4, cx + 4, h - 4, TIMBER[4])
    edge(sp)
    return sp


def bench(w, h, salt=71):
    """A tiered lecture bench (the workbench counter-walk pattern): a plank
    seat + back on stout legs. Audience NPCs stand on the walkable row behind
    it so their legs tuck under the seat — the seated-in-the-gallery read;
    only the bottom row is solid."""
    sp = S(w, h, salt)
    sp.rect(1, 8, w - 2, 8, TIMBER[0])                        # seat top edge
    sp.rect(1, 9, w - 2, 12, TIMBER[1])                       # seat plank
    for gx in range(4, w - 4, 10):
        sp.rect(gx, 10, gx + 5, 10, TIMBER[2])               # grain
    sp.rect(1, 13, w - 2, 13, TIMBER[2])
    sp.rect(1, 14, w - 2, 14, TIMBER[4])                      # front lip
    sp.rect(2, 2, w - 3, 3, TIMBER[2])                        # low backrest
    sp.rect(2, 2, w - 3, 2, TIMBER[1])
    sp.rect(2, 4, w - 3, 4, TIMBER[4])
    for px2 in (3, w - 6):                                    # backrest posts
        sp.rect(px2, 4, px2 + 1, 8, TIMBER[3])
    for px2 in (3, w - 6):                                    # legs (floor between)
        sp.rect(px2, 15, px2 + 3, h - 3, TIMBER[3])
        sp.rect(px2 + 3, 15, px2 + 3, h - 3, TIMBER[4])
        sp.rect(px2, h - 4, px2 + 3, h - 3, TIMBER[4])
    sp.rect(6, h - 8, w - 7, h - 7, TIMBER[3])                # stretcher
    edge(sp)
    return sp
