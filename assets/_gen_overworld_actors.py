#!/usr/bin/env python3
"""Overworld travel actors at TRUE SNES density (CT-chunk restart):

  assets/overworld_basil.png  96x72, 24x24 cells, 4x3 — chibi Basil
      row0 walk_down(4)  row1 walk_up(4)  row2 walk_side(4, faces RIGHT; code
      flips) — big head, tuxedo blaze, goggles, little lab coat, feet y=21
      (overworld_basil_frames.tres contract).
  assets/overworld_icons.png  160x32 — five 32x32 landmark vignettes in a strip:
      HOME cottage · TOWN rooftops · MEADOW grove · CAVE mouth · OBELISK.
      Chunky minis: flat tone bands, teal shadows, one hot accent each.

Re-run: python3 assets/_gen_overworld_actors.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img, write_cells, OW_CELL, OW_FEET, ICON, h2
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

CX = 11.5
FEET = OW_FEET


def chibi_down(s, view, lift_l=0, lift_r=0, bobY=0):
    """Big-head travel Basil; view in (down, up)."""
    hy = 10 + bobY
    # legs
    s.capsule(9.5, 17, 9.5, FEET - 1.5 - lift_l, 1.4, 1.3, PANTR)
    s.capsule(14, 17, 14, FEET - 1.5 - lift_r, 1.4, 1.3, PANTR, sh=0.1)
    s.ball(9.5, FEET - 0.7 - lift_l, 1.5, 1.0, WHITE, wrap=0.10)
    s.ball(14, FEET - 0.7 - lift_r, 1.5, 1.0, WHITE, wrap=0.10)
    # tiny lab coat
    s.panel(CX, 15 + bobY, 18 + bobY, 4.0, 4.8, COATR, hem_curve=1, folds=(int(CX),))
    # tail flick (right side)
    s.capsule(16, 17 + bobY, 18, 15 + bobY, 1.0, 0.8, FUR, sh=0.1)
    # ears
    s.tri((8, hy - 7), hy - 2, 6, 10, FUR)
    s.tri((15, hy - 7), hy - 2, 13, 17, FUR, sh=0.15)
    if view == "down":
        s.set(8, hy - 5, EARIN)
        s.set(15, hy - 5, EARIN)
    # head
    s.ball(CX, hy, 5.7, 4.8, FUR, power=2.3, wrap=0.32, curve=0.28)
    if view == "down":
        s.ball(CX, hy + 3, 2.8, 1.7, WHITE, power=2.2, wrap=0.10, curve=0.1)
        s.tri((int(CX), hy - 2), hy + 1, CX - 0.5, CX + 0.5, WHITE)
        for ex in (9, 13):
            s.set(ex, hy - 1, EYE)
            s.set(ex, hy, PUPIL)
        s.set(int(CX), hy + 2, BASIL["NOSE"])
        s.rect(8, hy - 4, 15, hy - 4, GOGRIM[2])               # goggles up
        s.set(10, hy - 5, GOGRIM[1])
        s.set(13, hy - 5, GOGRIM[1])
        s.set(10, hy - 6, GOGLEN[0])
    else:
        s.rect(8, hy - 4, 15, hy - 4, GOGRIM[2])               # strap from behind
        s.set(10, hy - 5, GOGRIM[2])
        s.set(13, hy - 5, GOGRIM[2])
    s.despeckle(passes=1)
    s.outline(OUTS, OUT_FB)


def chibi_side(s, fA=0, fB=0, bobY=0):
    """Side view, faces RIGHT."""
    hy = 10 + bobY
    s.capsule(16, 16 + bobY, 19, 14 + bobY, 1.0, 0.8, FUR, sh=0.1)   # tail — behind
    s.capsule(10 + fB, 17, 10 + fB, FEET - 1.5, 1.4, 1.3, PANTR, sh=0.12)
    s.capsule(13 + fA, 17, 13 + fA, FEET - 1.5, 1.4, 1.3, PANTR)
    s.ball(10 + fB, FEET - 0.7, 1.5, 1.0, WHITE, wrap=0.10)
    s.ball(13 + fA, FEET - 0.7, 1.5, 1.0, WHITE, wrap=0.10)
    s.panel(11, 15 + bobY, 18 + bobY, 3.8, 4.5, COATR, hem_curve=1)
    s.tri((9, hy - 7), hy - 3, 7, 11, FUR)                     # near ear
    s.set(9, hy - 5, EARIN)
    s.tri((14, hy - 7), hy - 3, 12, 16, FUR, sh=0.3)           # far ear
    s.ball(11, hy, 5.4, 4.6, FUR, power=2.3, wrap=0.32, curve=0.28)
    s.ball(15.5, hy + 2, 2.3, 1.7, FUR, power=2.0, wrap=0.28)  # snout mass
    s.ball(16, hy + 2.5, 1.9, 1.4, WHITE, power=2.0, wrap=0.10)
    s.set(17, hy + 1, BASIL["NOSE"])
    s.set(13, hy - 1, EYE)
    s.set(13, hy, PUPIL)
    s.rect(6, hy - 3, 15, hy - 3, GOGRIM[2])
    s.set(12, hy - 4, GOGRIM[1])
    s.set(12, hy - 5, GOGLEN[0])
    s.despeckle(passes=1)
    s.outline(OUTS, OUT_FB)


cells = [[Sprite(OW_CELL, grain=1, salt=r * 5 + c, jitter=0.0) for c in range(4)]
         for r in range(3)]
lifts = ((0, 0), (2, 0), (0, 0), (0, 2))
bobs = (0, -1, 0, -1)
for i in range(4):
    chibi_down(cells[0][i], "down", lifts[i][0], lifts[i][1], bobs[i])
    chibi_down(cells[1][i], "up", lifts[i][0], lifts[i][1], bobs[i])
strides = ((2, -2), (0, 0), (-2, 2), (0, 0))
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
WALLR = ramp((246, 188, 152, 255), "violet", 6)      # cottage plaster (warm)
ROOFR = ramp((214, 84, 146, 255), "violet", 6)       # magenta shingles
GLOW = (255, 214, 120, 255)


def icon_sprite():
    return Sprite(ICON, grain=1, jitter=0.0)


def ground_pad(s, ry=4, ramp_=GRASSR):
    for y in range(23, 31):
        ny = (y - 27) / ry
        for x in range(3, 29):
            nx = (x - 16) / 13.5
            if nx * nx + ny * ny <= 1.0:
                s.set(x, y, s.tone(ramp_, 0.45 + 0.3 * ny + 0.12 * nx, x, y))


def icon_home(s):
    ground_pad(s)
    s.panel(16, 15, 25, 6.5, 7, WALLR, hem_curve=0)            # cottage face
    s.tri((16, 6), 15, 6, 26, ROOFR)                           # big roof
    s.rect(10, 17, 13, 21, ramp((150, 88, 132, 255), "violet", 4)[1])   # door
    s.rect(19, 17, 22, 20, GLOW)                               # lit window
    s.set(19, 17, (255, 244, 200, 255))
    s.rect(22, 7, 23, 11, ROCKR[2])                            # chimney
    s.despeckle(passes=1)


def icon_town(s):
    ground_pad(s)
    s.panel(10, 16, 26, 4.5, 5, WALLR, hem_curve=0, sh=0.12)
    s.tri((10, 10), 16, 4, 16, ROOFR, sh=0.15)
    s.panel(21, 13, 26, 5, 5.5, WALLR, hem_curve=0)
    s.tri((21, 6), 13, 14, 28, ROOFR)
    s.rect(20, 19, 22, 22, GLOW)
    s.rect(8, 19, 10, 22, GLOW)
    s.rect(25, 8, 26, 12, ROCKR[2])
    s.despeckle(passes=1)


def icon_meadow(s):
    ground_pad(s)
    s.ball(11, 15, 5.5, 5, FORESTR, power=2.0, wrap=0.34)      # grove crowns
    s.ball(20, 13, 6.5, 5.5, FORESTR, power=2.0, wrap=0.34)
    s.ball(15, 18, 5, 4, FORESTR, power=2.0, wrap=0.30, sh=0.15)
    s.capsule(15, 22, 15, 26, 1.2, 1.1, ramp((110, 76, 96, 255), "violet", 4))
    for (fx, fy) in ((7, 26), (24, 27), (12, 28), (21, 25)):   # hot-pink blooms
        s.set(fx, fy, (255, 116, 176, 255))
        s.set(fx, fy - 1, (255, 180, 212, 255))


def icon_cave(s):
    ground_pad(s, ramp_=ROCKR)
    s.ball(16, 17, 11, 9, ROCKR, power=2.2, wrap=0.30)         # rock mass
    s.ball(16, 20, 5, 5.5, ramp((30, 24, 48, 255), "violet", 4), power=1.8, wrap=0.05)
    s.tri((16, 15), 25, 12, 20, (16, 12, 30, 255))             # black mouth
    s.set(13, 15, (214, 246, 248, 255))                        # glint above mouth


def icon_obelisk(s):
    ground_pad(s, ramp_=WASTER)
    s.tri((16, 3), 25, 12, 20, ramp((172, 122, 210, 255), "violet", 6))
    s.rect(11, 25, 21, 27, ROCKR[3])                           # plinth
    s.line([(16, 5), (16, 7), (15, 9), (16, 11)], (240, 220, 255, 255))  # rune glow
    for (gx, gy) in ((9, 13), (23, 15), (12, 7), (22, 6)):
        s.set(gx, gy, ACCENT)                                  # floating motes


icons = [icon_sprite() for _ in range(5)]
for s, fn in zip(icons, (icon_home, icon_town, icon_meadow, icon_cave, icon_obelisk)):
    fn(s)
    s.outline({}, (26, 20, 44, 255))

sheet = Img(5 * ICON, ICON)
for i, s in enumerate(icons):
    sheet.blit_cell(s, i * ICON, 0)
sheet.save(os.path.join(HERE, "overworld_icons.png"))
