#!/usr/bin/env python3
"""Combat/HUD support sprites at the 2x scale (pure stdlib, via assets/_artlib.py).

Palette-locked to assets/_palette.py: the laser bolt, muzzle flash and beaker fluid
all share Basil's gun accents (GUNE laser green / GUNP gun purple), so weapon, shot
and ammo pickup read as one system. Cell contracts:

  hearts.png       96x32  — three 32x32 frames: full | half | empty (hud.gd CELL)
  ammo_pips.png    32x16  — two 16x16 frames: full | empty (hud.gd AMMO_CELL)
  laser_bolt.png   52x16  — points +x (rotation 0 == facing right)
  muzzle_flash.png 40x40
  beaker.png       24x28
  shadow.png       48x20

Re-run: python3 assets/placeholder/_gen_placeholders.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _artlib import Img, h2
from _palette import BASIL

GUNE = BASIL["GUNE"]          # laser green
GUNP = BASIL["GUNP"]          # gun purple

# --- Hearts: 96x32 strip, 3 cells: full | half | empty -----------------------------
RED   = (236, 84, 102, 255)
RED_L = (255, 150, 160, 255)
RED_D = (150, 40, 70, 255)     # violet-leaning shadow
EMPTY   = (58, 50, 72, 255)
EMPTY_D = (38, 32, 52, 255)

HEART = [
    "...XXXX....XXXX...",
    "..XXXXXX..XXXXXX..",
    ".XXXXXXXXXXXXXXXX.",
    ".XXXXXXXXXXXXXXXX.",
    "XXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXX",
    ".XXXXXXXXXXXXXXXX.",
    ".XXXXXXXXXXXXXXXX.",
    "..XXXXXXXXXXXXXX..",
    "...XXXXXXXXXXXX...",
    "....XXXXXXXXXX....",
    "......XXXXXX......",
    ".......XXXX.......",
    "........XX........",
]


def heart(img, ox, left_full, right_full):
    sx, sy = ox + 7, 8
    for j, line in enumerate(HEART):
        for i, ch in enumerate(line):
            if ch != "X":
                continue
            full = left_full if i < 9 else right_full
            if full:
                c = RED
                if j <= 3 and 2 < i < 8:
                    c = RED_L                     # top-left shine
                elif j >= 9 or i >= 15:
                    c = RED_D                     # violet-shadow lower rim
            else:
                c = EMPTY if j < 9 else EMPTY_D
            img.put(sx + i, sy + j, c)


hp = Img(96, 32)
heart(hp, 0, True, True)
heart(hp, 32, True, False)
heart(hp, 64, False, False)
hp.save(os.path.join(HERE, "hearts.png"))

# --- Ammo pips: 32x16, 2 frames of 16x16: full | empty -----------------------------
AM_ON_L = (208, 255, 216, 255)
AM_OFF  = (45, 60, 60, 255)
AM_OFF_D = (30, 42, 44, 255)
ap = Img(32, 16)
for ox, on in ((0, True), (16, False)):
    for y in range(2, 14):
        for x in range(2, 14):
            r = abs(x - 7.5) + abs(y - 7.5)      # diamond pip
            if r > 8:
                continue
            if on:
                c = GUNE
                if x + y < 12:
                    c = AM_ON_L
                elif r > 6.5:
                    c = (86, 190, 120, 255)
            else:
                c = AM_OFF if r <= 6.5 else AM_OFF_D
            ap.put(ox + x, y, c)
ap.save(os.path.join(HERE, "ammo_pips.png"))

# --- Laser bolt: 52x16, points +x ---------------------------------------------------
LZ_CORE = (240, 255, 240, 255)
LZ_EDGE = GUNE
LZ_GLOW = (GUNE[0], GUNE[1], GUNE[2], 90)
LZ_TAIL = (GUNE[0], GUNE[1], GUNE[2], 50)
lb = Img(52, 16)
lb.rect(0, 6, 16, 9, LZ_TAIL)                    # long fading tail
lb.rect(8, 6, 47, 9, LZ_GLOW)                    # glow along the length
lb.rect(12, 4, 45, 11, LZ_EDGE)                  # body
lb.rect(18, 2, 41, 13, LZ_EDGE)                  # rounded middle
lb.rect(16, 4, 40, 11, LZ_CORE)                  # bright core
lb.rect(38, 4, 51, 11, (255, 255, 255, 255))     # white-hot leading tip
lb.rect(48, 6, 51, 9, GUNP)                      # purple sparkle at the very tip
lb.save(os.path.join(HERE, "laser_bolt.png"))

# --- Muzzle flash: 40x40 green starburst at the gun root ---------------------------
mf = Img(40, 40)
mf.oval(19.5, 19.5, 16, 16, (110, 240, 150, 70))          # outer glow
mf.rect(0, 18, 39, 23, (190, 255, 205, 150))              # horizontal spoke
mf.rect(16, 0, 23, 39, (190, 255, 205, 150))              # vertical spoke
for d in (-1, 1):                                         # short diagonal sparks
    for i in range(6, 13):
        mf.put(19 + i, 19 + d * i, (190, 255, 205, 130))
        mf.put(19 - i, 19 + d * i, (190, 255, 205, 130))
mf.oval(19.5, 19.5, 9, 9, (160, 255, 190, 210))           # inner glow
mf.oval(19.5, 19.5, 5, 5, (255, 255, 255, 255))           # white-hot core
mf.save(os.path.join(HERE, "muzzle_flash.png"))

# --- Beaker pickup: 24x28 — glass flask of laser-green refill fluid ----------------
GLASS   = (214, 232, 244, 255)
GLASS_D = (150, 168, 200, 255)
FLUID   = GUNE
FLUID_D = (86, 190, 120, 255)
FLUID_L = (208, 255, 216, 255)
bk = Img(24, 28)
bk.rect(8, 0, 15, 3, GLASS)                      # neck lip
bk.rect(9, 0, 14, 1, GLASS_D)
bk.rect(9, 3, 14, 8, GLASS)                      # neck
for y in range(8, 27):                           # conical flask body
    half = 3 + round((y - 8) * 0.38 * 10) / 10
    x0, x1 = round(11.5 - half), round(11.5 + half)
    bk.rect(x0, y, x1, y, GLASS)
    bk.put(x0, y, GLASS_D)
    bk.put(x1, y, GLASS_D)
for y in range(16, 26):                          # fluid, sloshed to a line
    half = 3 + round((y - 8) * 0.38 * 10) / 10 - 1
    x0, x1 = round(11.5 - half), round(11.5 + half)
    bk.rect(x0, y, x1, y, FLUID if y > 17 else FLUID_L)
    if y >= 24:
        bk.rect(x0, y, x1, y, FLUID_D)
bk.rect(26, 26, 0, 0, GLASS)                     # (no-op guard)
bk.rect(6, 26, 17, 27, GLASS_D)                  # base
bk.rect(9, 10, 9, 14, (255, 255, 255, 255))      # glass glint
bk.put(10, 15, (255, 255, 255, 200))
for i in range(3):                               # rising bubbles
    bx = 10 + h2(i, 3) % 5
    by = 19 + h2(3, i) % 5
    bk.put(bx, by, FLUID_L)
bk.save(os.path.join(HERE, "beaker.png"))

# --- Jump shadow: 48x20 soft black ellipse ------------------------------------------
sh = Img(48, 20)
for yy in range(20):
    for xx in range(48):
        nx = (xx - 23.5) / 23.5
        ny = (yy - 9.5) / 9.5
        d = nx * nx + ny * ny
        if d <= 1.0:
            a = int(115 * (1.0 - d * 0.5))       # softer toward the edge
            sh.put(xx, yy, (0, 0, 0, a))
sh.save(os.path.join(HERE, "shadow.png"))
