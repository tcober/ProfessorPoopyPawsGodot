#!/usr/bin/env python3
"""Overworld travel actors, rebuilt on the _sprites.py kit:

  assets/overworld_basil.png  192x144, 48x48 cells, 4x3 — chibi Basil
      row0 walk_down(4)  row1 walk_up(4)  row2 walk_side(4, faces RIGHT; code
      flips) — big head, tuxedo blaze, goggles, little lab coat, feet y=42
      (overworld_basil_frames.tres contract).
  assets/overworld_icons.png  320x64 — five 64x64 landmark vignettes in a strip:
      HOME cottage · TOWN rooftops · MEADOW grove · CAVE mouth · OBELISK.
      Painterly minis: rim light, teal shadows, one hot accent each.

Re-run: python3 assets/_gen_overworld_actors.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img, write_cells, write_png, OW_CELL, OW_FEET, ICON, h2
from _sprites import Sprite
from _palette import BASIL, SCENES, ramp

FUR = BASIL["FUR"]
WHITE = BASIL["WHITE"]
COATR = BASIL["COATR"]
PANTR = BASIL["PANTR"]
GOGRIM = BASIL["GOGRIM"]
GOGLEN = BASIL["GOGLEN"]
EARIN = BASIL["EARIN"]
EYE = BASIL["EYE_Y"]
PUPIL = BASIL["PUPIL"]
OUTS, OUT_FB = BASIL["OUTS"], BASIL["OUT_FALLBACK"]

CX = 23.5
FEET = OW_FEET


def chibi_down(s, view, lift_l=0, lift_r=0, bobY=0):
    """Big-head travel Basil; view in (down, up)."""
    hy = 20 + bobY
    # legs
    s.capsule(19, 34, 19, FEET - 3 - lift_l, 2.6, 2.4, PANTR)
    s.capsule(28, 34, 28, FEET - 3 - lift_r, 2.6, 2.4, PANTR, sh=0.1)
    s.ball(19, FEET - 1.4 - lift_l, 2.8, 1.9, WHITE, wrap=0.12)
    s.ball(28, FEET - 1.4 - lift_r, 2.8, 1.9, WHITE, wrap=0.12)
    # tiny lab coat
    s.panel(CX, 30 + bobY, 37 + bobY, 8.0, 9.5, COATR, hem_curve=1, folds=(int(CX),))
    # tail flick (right side)
    s.capsule(32, 35 + bobY, 36, 30 + bobY, 1.8, 1.4, FUR, sh=0.1)
    # ears
    s.tri((16, hy - 15), hy - 5, 12, 21, FUR)
    s.tri((31, hy - 15), hy - 5, 26, 35, FUR, sh=0.15)
    if view == "down":
        s.tri((16, hy - 12), hy - 7, 14, 19, EARIN)
        s.tri((31, hy - 12), hy - 7, 28, 33, EARIN)
    # head
    s.ball(CX, hy, 11.4, 9.6, FUR, power=2.3, wrap=0.32, curve=0.28)
    if view == "down":
        s.ball(CX, hy + 6, 5.6, 3.4, WHITE, power=2.2, wrap=0.14, curve=0.1)
        s.tri((int(CX), hy - 5), hy + 2, CX - 1, CX + 1, WHITE)
        for ex in (19, 26):
            s.rect(ex, hy - 3, ex + 1, hy - 1, EYE)
            s.set(ex + 1, hy - 2, PUPIL)
        s.set(int(CX), hy + 4, BASIL["NOSE"])
        s.rect(16, hy - 7, 31, hy - 6, GOGRIM[2])              # goggles up
        s.ball(20, hy - 8.5, 2.4, 1.7, GOGRIM, power=2.0)
        s.ball(27, hy - 8.5, 2.4, 1.7, GOGRIM, power=2.0, sh=0.15)
        s.set(20, hy - 9, GOGLEN[0])
    else:
        s.rect(17, hy - 6, 30, hy - 5, GOGRIM[2])              # strap from behind
        s.ball(20, hy - 7.5, 1.9, 1.3, GOGRIM, power=2.0)
        s.ball(27, hy - 7.5, 1.9, 1.3, GOGRIM, power=2.0, sh=0.15)
    s.despeckle(passes=1)
    s.outline(OUTS, OUT_FB)


def chibi_side(s, fA=0, fB=0, bobY=0):
    """Side view, faces RIGHT."""
    hy = 20 + bobY
    s.capsule(33, 33 + bobY, 38, 28 + bobY, 1.9, 1.4, FUR, sh=0.1)   # tail — behind
    s.capsule(20 + fB, 34, 20 + fB, FEET - 3, 2.6, 2.4, PANTR, sh=0.12)
    s.capsule(27 + fA, 34, 27 + fA, FEET - 3, 2.6, 2.4, PANTR)
    s.ball(20 + fB, FEET - 1.4, 2.8, 1.9, WHITE, wrap=0.12)
    s.ball(27 + fA, FEET - 1.4, 2.8, 1.9, WHITE, wrap=0.12)
    s.panel(23, 30 + bobY, 37 + bobY, 7.5, 9.0, COATR, hem_curve=1)
    s.tri((18, hy - 15), hy - 6, 14, 23, FUR)                  # near ear
    s.tri((18, hy - 12), hy - 8, 16, 21, EARIN)
    s.tri((28, hy - 14), hy - 6, 23, 32, FUR, sh=0.3)          # far ear
    s.ball(22, hy, 10.8, 9.2, FUR, power=2.3, wrap=0.32, curve=0.28)
    s.ball(31, hy + 4, 4.6, 3.4, FUR, power=2.0, wrap=0.28)    # snout mass
    s.ball(31.5, hy + 5, 3.8, 2.7, WHITE, power=2.0, wrap=0.12)
    s.rect(34, hy + 2, 35, hy + 3, BASIL["NOSE"])
    s.rect(25, hy - 3, 26, hy - 1, EYE)
    s.set(26, hy - 2, PUPIL)
    s.rect(13, hy - 7, 30, hy - 6, GOGRIM[2])
    s.ball(24, hy - 8.5, 2.6, 1.8, GOGRIM, power=2.0)
    s.set(24, hy - 9, GOGLEN[0])
    s.despeckle(passes=1)
    s.outline(OUTS, OUT_FB)


cells = [[Sprite(OW_CELL, grain=2, salt=r * 5 + c) for c in range(4)] for r in range(3)]
lifts = ((0, 0), (3, 0), (0, 0), (0, 3))
bobs = (0, -1, 0, -1)
for i in range(4):
    chibi_down(cells[0][i], "down", lifts[i][0], lifts[i][1], bobs[i])
    chibi_down(cells[1][i], "up", lifts[i][0], lifts[i][1], bobs[i])
strides = ((3, -3), (0, 0), (-3, 3), (0, 0))
for i in range(4):
    chibi_side(cells[2][i], strides[i][0], strides[i][1], bobs[i])
write_cells(os.path.join(HERE, "overworld_basil.png"), cells, OW_CELL)

# ---- landmark icons -------------------------------------------------------------------
OW = SCENES["overworld"]
SH = OW["shadow"]
GRASSR = ramp(OW["mats"]["grass"], SH, 6)
ROCKR = ramp(OW["mats"]["rock"], SH, 6)
FORESTR = ramp(OW["mats"]["forest"], SH, 6)
WASTER = ramp(OW["mats"]["waste"], SH, 6)
ACCENT = OW["accent"]
WALLR = ramp((246, 188, 152, 255), "violet", 6)      # cottage plaster (morning-yard warmth)
ROOFR = ramp((214, 84, 146, 255), "violet", 6)       # magenta shingles
GLOW = (255, 214, 120, 255)


def icon_sprite():
    return Sprite(ICON, grain=2)


def ground_pad(s, ry=8, ramp_=GRASSR):
    for y in range(46, 62):
        ny = (y - 54) / ry
        for x in range(6, 58):
            nx = (x - 32) / 27.0
            if nx * nx + ny * ny <= 1.0:
                s.set(x, y, s.tone(ramp_, 0.45 + 0.3 * ny + 0.12 * nx, x, y))


def icon_home(s):
    ground_pad(s)
    s.panel(32, 30, 50, 13, 14, WALLR, hem_curve=0)            # cottage face
    s.tri((32, 12), 30, 12, 52, ROOFR)                         # big roof
    s.rect(20, 34, 26, 42, ramp((150, 88, 132, 255), "violet", 4)[1])   # door
    s.rect(38, 34, 44, 40, GLOW)                               # lit window
    s.rect(39, 35, 40, 36, (255, 244, 200, 255))
    s.rect(44, 14, 47, 22, ROCKR[2])                           # chimney


def icon_town(s):
    ground_pad(s)
    s.panel(20, 32, 52, 9, 10, WALLR, hem_curve=0, sh=0.12)
    s.tri((20, 20), 32, 8, 32, ROOFR, sh=0.15)
    s.panel(42, 26, 52, 10, 11, WALLR, hem_curve=0)
    s.tri((42, 12), 26, 29, 55, ROOFR)
    s.rect(40, 38, 44, 44, GLOW)
    s.rect(17, 38, 21, 44, GLOW)
    s.rect(50, 16, 52, 24, ROCKR[2])


def icon_meadow(s):
    ground_pad(s)
    s.ball(22, 30, 11, 10, FORESTR, power=2.0, wrap=0.34)      # grove crowns
    s.ball(40, 26, 13, 11, FORESTR, power=2.0, wrap=0.34)
    s.ball(31, 36, 10, 8, FORESTR, power=2.0, wrap=0.30, sh=0.15)
    s.capsule(30, 44, 30, 52, 2.4, 2.2, ramp((110, 76, 96, 255), "violet", 4))
    for (fx, fy) in ((14, 52), (48, 54), (24, 57), (42, 50)):  # hot-pink blooms
        s.rect(fx, fy, fx + 1, fy + 1, (255, 116, 176, 255))
        s.set(fx, fy - 1, (255, 180, 212, 255))


def icon_cave(s):
    ground_pad(s, ramp_=ROCKR)
    s.ball(32, 34, 22, 18, ROCKR, power=2.2, wrap=0.30)        # rock mass
    s.ball(32, 40, 10, 11, ramp((30, 24, 48, 255), "violet", 4), power=1.8, wrap=0.05)
    s.tri((32, 30), 50, 24, 40, (16, 12, 30, 255))             # black mouth
    s.set(26, 30, (214, 246, 248, 255))                        # glint above mouth


def icon_obelisk(s):
    ground_pad(s, ramp_=WASTER)
    s.tri((32, 6), 50, 24, 40, ramp((172, 122, 210, 255), "violet", 6))
    s.rect(22, 50, 42, 54, ROCKR[3])                           # plinth
    s.line([(32, 10), (32, 14), (31, 18), (32, 22)], (240, 220, 255, 255))  # rune glow
    for (gx, gy) in ((18, 26), (46, 30), (24, 14), (44, 12)):
        s.set(gx, gy, ACCENT)                                  # floating motes


icons = [icon_sprite() for _ in range(5)]
for s, fn in zip(icons, (icon_home, icon_town, icon_meadow, icon_cave, icon_obelisk)):
    fn(s)
    s.despeckle(passes=1)
    s.outline({}, (26, 20, 44, 255))

sheet = Img(5 * ICON, ICON)
for i, s in enumerate(icons):
    sheet.blit_cell(s, i * ICON, 0)
sheet.save(os.path.join(HERE, "overworld_icons.png"))
