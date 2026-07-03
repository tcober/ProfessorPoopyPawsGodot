#!/usr/bin/env python3
"""SCHWEINLER — the bully. A stout, smug pig: big snout, beady angry eyes, red
neckerchief, curly tail, cloven trotters. Rebuilt from scratch on the
_sprites.py kit: capsule limbs, steer-lit ball volumes, cluster-jittered tones,
per-material outlines. His stoutness is the comedy foil to Basil's lanky thirds.

FROZEN layout (entities/npcs/schweinler_frames.tres): assets/schweinler_gen.png
384x384, 96x96 cells, 4x4 —
  row0 walk_down(4)  row1 walk_up(4)  row2 walk_side(4, faces RIGHT; code flips)
  row3 point_up(2) + laugh_down(2)
Feet baseline y=88 (Basil's scale, so he can walk into gameplay later).
Re-run: python3 assets/_gen_schweinler_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import write_cells, ZONE_CELL, ZONE_FEET
from _sprites import Sprite
from _palette import SCHWEINLER

CELL, COLS, ROWS = ZONE_CELL, 4, 4
FEET = ZONE_FEET
CX = 48

PIG = SCHWEINLER["PIG"]
BELLY = SCHWEINLER["BELLY"]
RED = SCHWEINLER["KERCH"]
HOOF = SCHWEINLER["HOOF"]
EYE_D = SCHWEINLER["EYE_D"]
GLINT = SCHWEINLER["GLINT"]
BROW = SCHWEINLER["BROW"]
NOSTR = SCHWEINLER["NOSTR"]
MOUTH = SCHWEINLER["MOUTH"]
TONGUE = SCHWEINLER["TONGUE"]
MAW = SCHWEINLER["MAW"]
OUTS, OUT_FB = SCHWEINLER["OUTS"], SCHWEINLER["OUT_FALLBACK"]
OUT_HOOF = (36, 18, 30, 255)


def new():
    return Sprite(CELL, grain=2)


# ---- parts ---------------------------------------------------------------------------

def leg(s, hx, fx, lift=0, sh=0.0):
    """Sturdy tapered leg + cloven hoof."""
    fy = FEET - lift
    s.capsule(hx, 70, fx, fy - 5, 4.6, 3.8, PIG, sh=0.10 + sh)
    s.capsule(fx, fy - 4, fx, fy - 1.6, 3.9, 3.7, HOOF, sh=sh * 0.5)
    s.rect(fx, fy - 2, fx + 1, fy, OUT_HOOF)                   # cloven notch


def curly_tail(s, cx, cy, sh=0.12):
    for (px_, py_) in ((cx, cy), (cx + 3, cy - 3), (cx + 5, cy), (cx + 2, cy + 2)):
        s.ball(px_, py_, 2.3, 2.3, PIG, sh=sh)


def body_down(s, dy=0, back=False):
    s.ball(CX, 58 + dy, 16.8, 15.0, PIG, power=2.2, wrap=0.30, curve=0.26)
    if not back:
        s.ball(CX, 62 + dy, 10.0, 9.0, BELLY, power=2.0, wrap=0.18, curve=0.14)
    # neckerchief: wrapped band + knot with fluttering tails
    for y in range(42 + dy, 47 + dy):
        for x in range(33, 64):
            t = 0.30 + 0.34 * (x - 33) / 31 + (0.08 if y == 46 + dy else 0)
            s.set(x, y, s.tone(RED, t, x, y))
    if not back:
        s.tri((CX, 46 + dy), 54 + dy, 44, 52, RED, sh=0.12)
        s.rect(45, 45 + dy, 49, 47 + dy, RED[0])


def arm_down(s, sx, dy, d, sh=0.0):
    s.capsule(sx, 48 + dy + d * 0.3, sx + (-3 if sx < CX else 3), 62 + dy + d, 4.2, 3.4, PIG, sh=0.08 + sh)
    ex = sx + (-3 if sx < CX else 3)
    s.capsule(ex, 62 + dy + d, ex, 66 + dy + d, 3.4, 3.2, HOOF, sh=sh * 0.5)


def head_down(s, dy=0, mood="smug"):
    s.tri((30, 4 + dy), 20 + dy, 26, 42, PIG)                  # droopy ears
    s.tri((66, 4 + dy), 20 + dy, 54, 70, PIG, sh=0.18)
    s.tri((32, 8 + dy), 18 + dy, 30, 38, PIG, sh=0.35)
    s.tri((64, 8 + dy), 18 + dy, 60, 66, PIG, sh=0.45)
    s.ball(CX, 26 + dy, 18.2, 15.0, PIG, power=2.2, wrap=0.32, curve=0.26)
    if mood == "laugh":
        for ex in (38, 54):                                    # squeezed-shut mirth
            s.line([(ex, 19 + dy), (ex + 1, 18 + dy), (ex + 2, 17 + dy),
                    (ex + 3, 18 + dy), (ex + 4, 19 + dy)], MAW)
    else:
        for ex in (38, 54):
            s.rect(ex, 18 + dy, ex + 3, 21 + dy, EYE_D)
            s.rect(ex, 18 + dy, ex + 1, 19 + dy, GLINT)
        s.line([(43, 14 + dy), (42, 15 + dy), (41, 16 + dy), (42, 15 + dy)], BROW)
        s.line([(52, 14 + dy), (53, 15 + dy), (54, 16 + dy), (53, 15 + dy)], BROW)
    s.ball(CX, 31 + dy, 8.8, 5.6, BELLY, power=2.0, sh=-0.06, wrap=0.16)  # THE SNOUT
    s.rect(44, 28 + dy, 45, 33 + dy, NOSTR)
    s.rect(52, 28 + dy, 53, 33 + dy, NOSTR)
    s.set(44, 28 + dy, (222, 168, 158, 255))
    s.set(52, 28 + dy, (222, 168, 158, 255))
    if mood == "laugh":
        s.rect(42, 36 + dy, 54, 41 + dy, MAW)
        s.rect(46, 40 + dy, 50, 41 + dy, TONGUE)
    else:
        s.line([(42, 38 + dy), (43, 38 + dy), (44, 38 + dy), (45, 38 + dy),
                (46, 37 + dy), (47, 37 + dy), (48, 36 + dy)], MOUTH)     # smug curl


def head_up(s, dy=0):
    s.tri((30, 4 + dy), 20 + dy, 26, 42, PIG)
    s.tri((66, 4 + dy), 20 + dy, 54, 70, PIG, sh=0.18)
    s.tri((32, 8 + dy), 18 + dy, 30, 38, PIG, sh=0.50)
    s.tri((64, 8 + dy), 18 + dy, 60, 66, PIG, sh=0.55)
    s.ball(CX, 26 + dy, 18.2, 15.0, PIG, power=2.2, wrap=0.32, curve=0.26)
    s.line([(42, 36 + dy), (44, 38 + dy), (46, 39 + dy), (50, 39 + dy),
            (52, 38 + dy), (54, 36 + dy)], PIG[3])             # neck crease


def head_side(s, dy=0):
    s.tri((36, 2 + dy), 16 + dy, 28, 44, PIG)                  # near ear
    s.tri((36, 6 + dy), 14 + dy, 32, 40, PIG, sh=0.40)
    s.tri((52, 4 + dy), 16 + dy, 46, 58, PIG, sh=0.25)         # far ear
    s.ball(46, 25 + dy, 17.0, 14.2, PIG, power=2.2, wrap=0.32, curve=0.26)
    s.ball(63, 29 + dy, 7.6, 5.2, BELLY, power=2.0, sh=-0.04, wrap=0.16)  # snout juts
    s.rect(68, 26 + dy, 69, 32 + dy, NOSTR)
    s.set(68, 26 + dy, (222, 168, 158, 255))
    s.rect(52, 18 + dy, 55, 21 + dy, EYE_D)
    s.rect(52, 18 + dy, 53, 19 + dy, GLINT)
    s.line([(50, 14 + dy), (52, 14 + dy), (54, 14 + dy), (56, 15 + dy), (57, 16 + dy)], BROW)
    s.line([(56, 34 + dy), (58, 35 + dy), (60, 34 + dy), (62, 33 + dy)], MOUTH)


def finish(s):
    s.despeckle(passes=1)
    s.outline(OUTS, OUT_FB)


# ---- full poses ------------------------------------------------------------------------

def pig_down(s, bob=0, lift_l=0, lift_r=0, swing=0, tail_dx=0, mood="smug"):
    curly_tail(s, 64 + tail_dx, 55)
    leg(s, 40, 39, lift_l)
    leg(s, 56, 57, lift_r, sh=0.10)
    body_down(s, bob)
    arm_down(s, 30, bob, swing)
    arm_down(s, 66, bob, -swing, sh=0.12)
    head_down(s, bob, mood)
    finish(s)


def pig_up(s, bob=0, lift_l=0, lift_r=0, swing=0, point=False):
    leg(s, 40, 39, lift_l)
    leg(s, 56, 57, lift_r, sh=0.10)
    body_down(s, bob, back=True)
    curly_tail(s, 46, 69 + bob, sh=0.22)
    arm_down(s, 30, bob, swing if not point else 0)
    if point:                                                  # trotter thrust skyward
        s.capsule(64, 46 + bob, 66, 12 + bob, 4.4, 3.6, PIG, sh=0.10)
        s.capsule(66, 11 + bob, 66, 5 + bob, 3.7, 3.5, HOOF)
    else:
        arm_down(s, 66, bob, -swing, sh=0.12)
    head_up(s, bob)
    finish(s)


def pig_side(s, bob=0, front_dx=0, back_dx=0, lift_f=0, lift_b=0):
    curly_tail(s, 25, 49 + bob, sh=0.15)
    leg(s, 38 + back_dx, 37 + back_dx, lift_b, sh=0.10)
    leg(s, 53 + front_dx, 54 + front_dx, lift_f)
    s.ball(46, 58 + bob, 17.4, 14.6, PIG, power=2.2, wrap=0.30, curve=0.26)  # barrel
    for y in range(42 + bob, 47 + bob):
        for x in range(31, 60):
            s.set(x, y, s.tone(RED, 0.30 + 0.34 * (x - 31) / 29, x, y))
    s.capsule(43 + front_dx // 2, 48 + bob, 43 + front_dx // 2, 61 + bob, 4.2, 3.4, PIG, sh=0.16)
    s.capsule(43 + front_dx // 2, 61 + bob, 43 + front_dx // 2, 64 + bob, 3.4, 3.2, HOOF)
    head_side(s, bob)
    finish(s)


# ---- build ----------------------------------------------------------------------------
cells = [[new() for _ in range(COLS)] for _ in range(ROWS)]

walk_bob = [0, -2, 0, -2]
walk_liftl = [4, 0, 0, 0]
walk_liftr = [0, 0, 4, 0]
walk_swing = [2, 0, -2, 0]
walk_tail = [0, 2, 4, 2]
for i in range(4):
    pig_down(cells[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
             walk_swing[i], walk_tail[i])
    pig_up(cells[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i], walk_swing[i])
side_front = [6, 0, -6, 0]
side_back = [-6, 0, 6, 0]
for i in range(4):
    pig_side(cells[2][i], walk_bob[i], side_front[i], side_back[i],
             2 if i == 0 else 0, 2 if i == 2 else 0)

pig_up(cells[3][0], 0, point=True)
pig_up(cells[3][1], -2, point=True)
pig_down(cells[3][2], 0, mood="laugh", tail_dx=4)
pig_down(cells[3][3], -2, mood="laugh", tail_dx=0)

write_cells(os.path.join(HERE, "schweinler_gen.png"), cells, CELL)
