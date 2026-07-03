#!/usr/bin/env python3
"""Lecture-hall backdrop -> assets/props/hall_bg.png (640x360), one composed
painting replacing the region-repeat Floor/Wall sprites (the last literally
tiled surface in the game).

Composition: plum panelled wall with a wainscot rail, warm sconce pools at the
outer walls (the chalkboard prop covers the center), then a perspective
floorboard hall below with a teal aisle runner leading the eye up to the
podium. Violet shadows, chalk-mint accent, corner vignette.

Run: python3 assets/_gen_scene_hall.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img, h2
from _paint import fbm, tone_i
from _palette import SCENES, ramp

HALL = SCENES["hall"]
SH = HALL["shadow"]
TIMBER = ramp(HALL["mats"]["timber"], SH, 6)
FLOOR = ramp(HALL["mats"]["floor"], SH, 6)
WAIN = ramp((146, 104, 158, 255), SH, 6)
RUNNER = ramp((44, 118, 122, 255), SH, 6)
LAMP = (255, 208, 122, 255)

W, H = 640, 360
WALL_H = 150
img = Img(W, H)
grain = fbm(W, H, 9.0, 2, 501, step=1)
soft = fbm(W, H, 90.0, 2, 502, step=2)

for y in range(H):
    for x in range(W):
        g = grain.sample(x, y)
        s = soft.sample(x, y)
        # corner vignette + a light pool center-top (the lecture spotlight)
        dx = (x - 320) / 320.0
        vig = 0.16 * (dx * dx) + 0.12 * (abs(y - 140) / 220.0)
        if y < WALL_H:
            # panelled wall: vertical boards w/ ridge lines, wainscot band below
            panel = (x // 64) % 2
            edge = x % 64
            t = 0.34 + panel * 0.05 + (g - 0.5) * 0.12 + (s - 0.5) * 0.10 + vig
            if edge < 2:
                t += 0.28                                  # panel seam
            elif edge > 61:
                t -= 0.10                                  # catch light
            if y < 6:
                t += 0.30                                  # ceiling shadow
            if WALL_H - 30 <= y < WALL_H - 24:
                t -= 0.16                                  # wainscot rail light
            ramp_ = WAIN if y >= WALL_H - 24 else TIMBER
            if y >= WALL_H - 24:
                t -= 0.06
            if y >= WALL_H - 3:
                t += 0.34                                  # baseboard shadow
            c = ramp_[tone_i(5, t, x, y, 55)]
        else:
            # perspective floorboards: seam rows spread toward the viewer
            fy = (y - WALL_H) / (H - WALL_H)
            t = 0.30 + fy * 0.16 + (g - 0.5) * 0.10 + (s - 0.5) * 0.12 + vig
            seam_step = 12 + int(fy * 26)
            if (y - WALL_H) % seam_step < 2:
                t += 0.24                                  # plank seam
            px_w = 56 + int(fy * 40)                       # plank ends stagger
            if (x + ((y - WALL_H) // seam_step) * 37) % px_w < 2:
                t += 0.18
            # teal aisle runner up the middle
            half = 44 + fy * 26
            if abs(x - 320) < half:
                rt = 0.30 + fy * 0.14 + (g - 0.5) * 0.12 + vig
                if abs(x - 320) > half - 4:
                    rt += 0.30                             # runner border
                elif abs(abs(x - 320) - (half - 12)) < 2:
                    rt -= 0.14                             # chalk-mint pinstripe
                c = RUNNER[tone_i(5, rt, x, y, 56)]
                img.put(x, y, c)
                continue
            c = FLOOR[tone_i(5, t, x, y, 57)]
        img.put(x, y, c)

# warm sconce pools on the outer wall (center is behind the chalkboard prop)
for (sx, sy) in ((52, 58), (588, 58)):
    img.rect(sx - 3, sy - 8, sx + 3, sy + 2, (58, 36, 62, 255))    # fixture
    img.rect(sx - 2, sy - 7, sx + 2, sy - 1, LAMP)
    img.put(sx, sy - 8, (255, 240, 190, 255))
    for r in range(1, 40):
        a = 0.16 * (1.0 - r / 40.0)
        for k in range(-r, r + 1):
            if h2(sx + k, sy + r, 58) < 200:
                img.mix(sx + k, sy - 4 + (r * 2) // 3, LAMP, a * 0.5)
                img.mix(sx + k, sy - 4 - r // 2, LAMP, a * 0.3)

img.save(os.path.join(HERE, "props", "hall_bg.png"))
