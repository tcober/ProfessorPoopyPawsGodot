#!/usr/bin/env python3
"""Sprite sheet for SCHWEINLER — the bully. A stout, smug pig: big snout, beady angry
eyes, red neckerchief, curly tail, cloven trotters. Rendered FF6 / Chrono
Trigger-style like Basil at 2x density: compact round figure (his stoutness is the
comedy foil to Basil's lanky thirds), 4-tone ramps from _palette.SCHWEINLER,
restrained 2x2 dithering, dark outlines. Writes assets/schweinler_gen.png
(384x384, 96x96 cells, 4x4) matching entities/npcs/schweinler_frames.tres:

  row0 walk_down(4)  row1 walk_up(4)  row2 walk_side(4, faces RIGHT; flip for left)
  row3 point_up(2) + laugh_down(2)

Cutscene actor for now (plants the poop bag, brands the nickname), drawn at Basil's
scale/baseline (feet y=88) so he can walk into gameplay later.
Re-run: python3 assets/_gen_schweinler_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _artlib import Cell, write_cells, ZONE_CELL, ZONE_FEET
from _palette import SCHWEINLER

CELL, COLS, ROWS = ZONE_CELL, 4, 4
FEET = ZONE_FEET

PIG    = SCHWEINLER["PIG"]
BELLY  = SCHWEINLER["BELLY"]
RED    = SCHWEINLER["KERCH"]
HOOF   = SCHWEINLER["HOOF"]
EYE_D  = SCHWEINLER["EYE_D"]
GLINT  = SCHWEINLER["GLINT"]
BROW   = SCHWEINLER["BROW"]
NOSTR  = SCHWEINLER["NOSTR"]
MOUTH  = SCHWEINLER["MOUTH"]
TONGUE = SCHWEINLER["TONGUE"]
MAW    = SCHWEINLER["MAW"]
OUTS, OUT_FB = SCHWEINLER["OUTS"], SCHWEINLER["OUT_FALLBACK"]
OUT_HOOF = (36, 18, 30, 255)


def new_cell():
    return Cell(CELL, grain=2)


def band(c, x0, y0, x1, y1, ramp, sh=0.0):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            t = 0.30 + 0.30 * (x - x0) / max(1, x1 - x0) + sh
            c.set(x, y, c._pick(ramp, t, x, y))


def tri_r(c, apex, base_y, x0, x1, ramp, sh=0.0):
    ax, ay = apex
    span = max(1, base_y - ay)
    for y in range(ay, base_y + 1):
        f = (y - ay) / span
        xl = round(ax + (x0 - ax) * f)
        xr = round(ax + (x1 - ax) * f)
        for x in range(min(xl, xr), max(xl, xr) + 1):
            t = 0.30 + 0.45 * f + sh
            c.set(x, y, c._pick(ramp, t, x, y))


# ---- parts ------------------------------------------------------------------------

def legs(c, lift_l=0, lift_r=0):
    """Sturdy pig legs with cloven hooves."""
    for (x0, x1, lift) in ((36, 43, lift_l), (52, 59, lift_r)):
        band(c, x0, 72 - lift, x1, FEET - 6 - lift, PIG, sh=0.12)
        band(c, x0, FEET - 5 - lift, x1, FEET - lift, HOOF)
        c.rect((x0 + x1) // 2, FEET - 2 - lift, (x0 + x1) // 2 + 1, FEET - lift, OUT_HOOF)  # cloven notch


def curly_tail_down(c, dx=0):
    pts = [(64, 56), (67, 53), (69 + dx * 0.8, 56), (66 + dx * 0.8, 58)]
    for (px_, py_) in pts:
        c.oval(px_, py_, 2.4, 2.4, PIG, sh=0.1)


def body_down(c, dy=0):
    """Stout barrel body, pale belly, red neckerchief with a knot."""
    c.oval(48, 58 + dy, 16.8, 15.2, PIG, power=2.2)
    c.oval(48, 62 + dy, 10.0, 9.2, BELLY, power=2.0, sh=-0.05)
    band(c, 34, 42 + dy, 60, 46 + dy, RED)
    tri_r(c, (48, 46 + dy), 52 + dy, 45, 51, RED, sh=0.1)     # knot tails
    c.rect(46, 45 + dy, 49, 46 + dy, RED[0])                  # the knot itself


def arms_down(c, dy=0, dl=0, dr=0):
    band(c, 26, 48 + dy + dl, 32, 60 + dy + dl, PIG, sh=0.08)
    band(c, 26, 61 + dy + dl, 32, 66 + dy + dl, HOOF)
    band(c, 64, 48 + dy + dr, 70, 60 + dy + dr, PIG, sh=0.18)
    band(c, 64, 61 + dy + dr, 70, 66 + dy + dr, HOOF)


def head_down(c, dy=0, mood="smug"):
    """Compact pig head: droopy triangle ears, beady angry eyes, THE SNOUT."""
    tri_r(c, (30, 4 + dy), 20 + dy, 26, 42, PIG)              # ears
    tri_r(c, (66, 4 + dy), 20 + dy, 54, 70, PIG, sh=0.18)
    tri_r(c, (32, 8 + dy), 18 + dy, 30, 38, PIG, sh=0.35)     # inner shadow
    tri_r(c, (64, 8 + dy), 18 + dy, 60, 66, PIG, sh=0.45)
    c.oval(48, 26 + dy, 18.4, 15.2, PIG, power=2.2)           # head
    # beady eyes + angry brows
    if mood == "laugh":
        for ex in (38, 54):
            c.line([(ex, 19 + dy), (ex + 1, 18 + dy), (ex + 2, 17 + dy),
                    (ex + 3, 18 + dy), (ex + 4, 19 + dy)], MAW)
    else:
        for ex in (38, 54):
            c.rect(ex, 18 + dy, ex + 3, 21 + dy, EYE_D)
            c.rect(ex, 18 + dy, ex + 1, 19 + dy, GLINT)
        c.line([(43, 14 + dy), (42, 15 + dy), (41, 16 + dy)], BROW)   # knit brows
        c.line([(42, 15 + dy), (41, 15 + dy)], BROW)
        c.line([(52, 14 + dy), (53, 15 + dy), (54, 16 + dy)], BROW)
        c.line([(53, 15 + dy), (54, 15 + dy)], BROW)
    # snout: big lighter disc with tall nostrils
    c.oval(48, 31 + dy, 8.8, 5.8, PIG, power=2.0, sh=-0.18)
    c.rect(44, 28 + dy, 45, 33 + dy, NOSTR)
    c.rect(52, 28 + dy, 53, 33 + dy, NOSTR)
    c.set(44, 28 + dy, (222, 168, 158, 255))                  # nostril top light
    c.set(52, 28 + dy, (222, 168, 158, 255))
    # mouth
    if mood == "laugh":
        c.rect(42, 36 + dy, 54, 41 + dy, MAW)                 # roaring laugh
        c.rect(46, 40 + dy, 50, 41 + dy, TONGUE)
        c.rect(43, 36 + dy, 53, 36 + dy, MAW)
    else:
        c.line([(42, 38 + dy), (43, 38 + dy), (44, 38 + dy), (45, 38 + dy),
                (46, 37 + dy), (47, 37 + dy), (48, 36 + dy)], MOUTH)  # smug curl


def head_up(c, dy=0):
    tri_r(c, (30, 4 + dy), 20 + dy, 26, 42, PIG)
    tri_r(c, (66, 4 + dy), 20 + dy, 54, 70, PIG, sh=0.18)
    tri_r(c, (32, 8 + dy), 18 + dy, 30, 38, PIG, sh=0.5)
    tri_r(c, (64, 8 + dy), 18 + dy, 60, 66, PIG, sh=0.55)
    c.oval(48, 26 + dy, 18.4, 15.2, PIG, power=2.2)
    c.line([(42, 36 + dy), (44, 38 + dy), (46, 39 + dy), (50, 39 + dy),
            (52, 38 + dy), (54, 36 + dy)], PIG[3])            # neck crease


def head_side(c, dy=0, mood="smug"):
    """Profile: the snout juts out front."""
    tri_r(c, (36, 2 + dy), 16 + dy, 28, 44, PIG)              # near ear
    tri_r(c, (36, 6 + dy), 14 + dy, 32, 40, PIG, sh=0.4)
    tri_r(c, (52, 4 + dy), 16 + dy, 46, 58, PIG, sh=0.25)     # far ear
    c.oval(46, 25 + dy, 17.2, 14.4, PIG, power=2.2)
    c.oval(63, 29 + dy, 7.6, 5.4, PIG, power=2.0, sh=-0.14)   # snout mass
    c.rect(68, 26 + dy, 69, 32 + dy, NOSTR)                   # forward nostril
    c.set(68, 26 + dy, (222, 168, 158, 255))
    if mood == "smug":
        c.rect(52, 18 + dy, 55, 21 + dy, EYE_D)
        c.rect(52, 18 + dy, 53, 19 + dy, GLINT)
        c.line([(50, 14 + dy), (52, 14 + dy), (54, 14 + dy), (56, 15 + dy), (57, 16 + dy)], BROW)
    c.line([(56, 34 + dy), (58, 35 + dy), (60, 34 + dy), (62, 33 + dy)], MOUTH)


# ---- full poses --------------------------------------------------------------------

def pig_down(c, bob=0, lift_l=0, lift_r=0, swing=0, tail_dx=0, mood="smug"):
    curly_tail_down(c, tail_dx)
    legs(c, lift_l, lift_r)
    body_down(c, bob)
    arms_down(c, bob, swing, -swing)
    head_down(c, bob, mood)
    c.outline(OUTS, OUT_FB)


def pig_up(c, bob=0, lift_l=0, lift_r=0, swing=0, point=False):
    legs(c, lift_l, lift_r)
    c.oval(48, 58 + bob, 16.8, 15.2, PIG, power=2.2)
    band(c, 34, 42 + bob, 60, 44 + bob, RED)                  # kerchief from behind
    # curly tail at his rear, center-low
    for (px_, py_) in ((48, 71), (51, 68), (54, 71), (51, 73)):
        c.oval(px_, py_ + bob, 2.4, 2.4, PIG, sh=0.22)
    if point:
        arms_down(c, bob, 0, 0)
    else:
        arms_down(c, bob, swing, -swing)
    head_up(c, bob)
    if point:                                                 # trotter thrust skyward
        band(c, 62, 10 + bob, 68, 44 + bob, PIG, sh=0.12)
        for y in range(10 + bob, 46 + bob, 3):
            c.set(62, y, PIG[3])                              # arm/body separation
        band(c, 62, 2 + bob, 68, 8 + bob, HOOF)
    c.outline(OUTS, OUT_FB)


def pig_side(c, bob=0, front_dx=0, back_dx=0, lift_f=0, lift_b=0):
    # curly tail behind
    for (px_, py_) in ((28, 50), (25, 47), (22, 50), (25, 53)):
        c.oval(px_, py_ + bob, 2.4, 2.4, PIG, sh=0.15)
    for (x0, x1, dx_, lift) in ((34, 41, back_dx, lift_b), (50, 57, front_dx, lift_f)):
        band(c, x0 + dx_, 72 - lift, x1 + dx_, FEET - 6 - lift, PIG, sh=0.12)
        band(c, x0 + dx_, FEET - 5 - lift, x1 + dx_, FEET - lift, HOOF)
    c.oval(46, 58 + bob, 17.6, 14.8, PIG, power=2.2)          # barrel
    band(c, 32, 42 + bob, 58, 46 + bob, RED)
    band(c, 40 + front_dx // 2, 48 + bob, 46 + front_dx // 2, 60 + bob, PIG, sh=0.16)  # near arm
    band(c, 40 + front_dx // 2, 61 + bob, 46 + front_dx // 2, 64 + bob, HOOF)
    head_side(c, bob)
    c.outline(OUTS, OUT_FB)


# ---- build ---------------------------------------------------------------------------
cells = [[new_cell() for _ in range(COLS)] for _ in range(ROWS)]

walk_bob   = [0, -2, 0, -2]
walk_liftl = [4, 0, 0, 0]
walk_liftr = [0, 0, 4, 0]
walk_swing = [2, 0, -2, 0]
walk_tail  = [0, 2, 4, 2]
for i in range(4):
    pig_down(cells[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
             walk_swing[i], walk_tail[i])
    pig_up(cells[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i], walk_swing[i])
side_front = [6, 0, -6, 0]
side_back  = [-6, 0, 6, 0]
for i in range(4):
    pig_side(cells[2][i], walk_bob[i], side_front[i], side_back[i],
             2 if i == 0 else 0, 2 if i == 2 else 0)

pig_up(cells[3][0], 0, point=True)
pig_up(cells[3][1], -2, point=True)
pig_down(cells[3][2], 0, mood="laugh", tail_dx=4)
pig_down(cells[3][3], -2, mood="laugh", tail_dx=0)

write_cells(os.path.join(HERE, "schweinler_gen.png"), cells, CELL)
