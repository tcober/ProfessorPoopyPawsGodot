#!/usr/bin/env python3
"""Combat/HUD fx sprites, rebuilt from scratch (replaces the retired
placeholder/_gen_placeholders.py at the SAME paths and dims — hud.gd and the
projectile/pickup scenes reference these files):

  placeholder/hearts.png      96x32  (32px ruby heart: full | half | empty)
  placeholder/ammo_pips.png   32x16  (16px energy cell: full | empty)
  placeholder/laser_bolt.png  52x16  (green bolt, white-hot core, tapered trail)
  placeholder/muzzle_flash.png 40x40 (starburst)
  placeholder/beaker.png      24x28  (conical flask of glowing laser fluid)
  placeholder/shadow.png      48x20  (soft violet hop shadow)

Style: glossy CT-item read — rim-lit volumes, one hot accent, violet shadows
(no gray). Laser green = BASIL["GUNE"] so bolt/flash/beaker fluid all match the
gun. Re-run: python3 assets/_gen_fx.py
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img, h2
from _palette import BASIL

OUT = os.path.join(HERE, "placeholder")
GREEN = BASIL["GUNE"][:3]           # (132, 246, 152)
RUBY = [(255, 150, 160), (236, 80, 104), (192, 44, 80), (128, 24, 62)]
SOCKET = [(74, 58, 96), (52, 40, 70), (34, 26, 50)]


def heart_mask(cx, cy, r, x, y):
    """Classic two-lobe heart: inside either lobe circle or the lower wedge."""
    lx, ly = abs(x - cx) - r * 0.5, y - (cy - r * 0.35)
    in_lobe = lx * lx + ly * ly <= (r * 0.62) ** 2
    fy = (y - cy) / (r * 1.15)
    in_wedge = 0.0 <= fy <= 1.0 and abs(x - cx) <= r * 1.05 * (1.0 - fy)
    return in_lobe or in_wedge


def draw_heart(img, ox, kind):
    cx, cy, r = ox + 16, 14.5, 11.0
    for y in range(32):
        for x in range(ox, ox + 32):
            if not heart_mask(cx, cy, r, x, y):
                continue
            nx, ny = (x - cx) / r, (y - cy) / r
            filled = kind == "full" or (kind == "half" and x < cx)
            ramp = RUBY if filled else SOCKET
            t = 0.38 + 0.34 * (nx * 0.55 + ny * 0.8) + 0.10 * (nx * nx + ny * ny)
            n = len(ramp) - 1
            q = max(0, min(n, int(t * n + (h2(x // 2, y // 2, 3) - 127.5) / 340 + 0.5)))
            img.put(x, y, ramp[q] + (255,))
    if kind != "empty":
        img.rect(int(cx - r * 0.55), int(cy - r * 0.42), int(cx - r * 0.3), int(cy - r * 0.2),
                 (255, 226, 232, 255))                        # glint
        img.put(int(cx - r * 0.2), int(cy - r * 0.5), (255, 226, 232, 255))
    # 1px outline
    edge = []
    for y in range(32):
        for x in range(ox, ox + 32):
            if img.get(x, y)[3] == 0 and any(
                    img.get(nx_, ny_)[3] == 255 for nx_, ny_ in
                    ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))):
                edge.append((x, y))
    for x, y in edge:
        img.put(x, y, (40, 14, 40, 255))


hearts = Img(96, 32)
for i, kind in enumerate(("full", "half", "empty")):
    draw_heart(hearts, i * 32, kind)
hearts.save(os.path.join(OUT, "hearts.png"))

# ---- ammo pips: glowing energy cells --------------------------------------------------
pips = Img(32, 16)
for i, full in enumerate((True, False)):
    ox = i * 16
    for y in range(2, 14):
        for x in range(ox + 3, ox + 13):
            nx, ny = (x - ox - 7.5) / 5.0, (y - 8.0) / 6.0
            if nx * nx + ny * ny > 1.0:
                continue
            if full:
                t = 0.5 + 0.4 * (nx * 0.5 + ny * 0.8)
                g = (int(GREEN[0] * (1.15 - t * 0.5)), int(GREEN[1] * (1.15 - t * 0.5)),
                     int(GREEN[2] * (1.15 - t * 0.5)))
                pips.put(x, y, (min(255, g[0]), min(255, g[1]), min(255, g[2]), 255))
            else:
                q = SOCKET[1] if (nx * 0.5 + ny * 0.8) < 0.2 else SOCKET[2]
                pips.put(x, y, q + (255,))
    if full:
        pips.rect(ox + 5, 4, ox + 6, 6, (235, 255, 238, 255))
    for y in range(16):
        for x in range(ox, ox + 16):
            if pips.get(x, y)[3] == 0 and any(
                    pips.get(nx_, ny_)[3] == 255 for nx_, ny_ in
                    ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))):
                pips.put(x, y, (30, 44, 52, 255))
pips.save(os.path.join(OUT, "ammo_pips.png"))

# ---- laser bolt: white-hot core, green glow, tapered trail ----------------------------
bolt = Img(52, 16)
for y in range(16):
    for x in range(52):
        u = x / 51.0                                          # 1 = nose (right)
        ry = 5.2 * (0.25 + 0.75 * u)                          # taper toward the tail
        d = abs(y - 7.5) / ry
        if d > 1.0 or u < 0.04:
            continue
        if d < 0.34 and u > 0.3:
            c = (240, 255, 244, 255)                          # core
        elif d < 0.75:
            c = (GREEN[0], GREEN[1], GREEN[2], 255)
        else:
            c = (66, 168, 108, 255)                           # glow edge
        if u < 0.45 and (h2(x, y, 9) & 3) == 0:
            continue                                          # trail breakup
        bolt.put(x, y, c)
bolt.save(os.path.join(OUT, "laser_bolt.png"))

# ---- muzzle flash: 8-ray starburst -----------------------------------------------------
flash = Img(40, 40)
for y in range(40):
    for x in range(40):
        dx, dy = x - 19.5, y - 19.5
        r = math.hypot(dx, dy)
        if r > 19 or r < 1:
            continue
        a = math.atan2(dy, dx)
        ray = abs(math.cos(a * 4.0)) ** 3
        reach = 6 + 13 * ray
        if r > reach:
            continue
        if r < 5:
            flash.put(x, y, (244, 255, 246, 255))
        elif r < reach * 0.75:
            flash.put(x, y, (GREEN[0], GREEN[1], GREEN[2], 255))
        else:
            flash.put(x, y, (66, 168, 108, 230))
flash.save(os.path.join(OUT, "muzzle_flash.png"))

# ---- beaker: conical flask of glowing fluid --------------------------------------------
beaker = Img(24, 28)
GLASS = (196, 224, 236)
for y in range(3, 27):
    f = (y - 3) / 23.0
    half = 2.5 if f < 0.28 else 2.5 + 8.5 * ((f - 0.28) / 0.72)
    for x in range(24):
        d = abs(x - 11.5)
        if d > half:
            continue
        fluid = f > 0.52
        if d > half - 1.2 or y >= 26:
            beaker.put(x, y, GLASS + (235,))                  # glass wall
        elif fluid:
            t = (h2(x // 2, y // 2, 5) - 127) / 500.0
            g = (int(GREEN[0] * (0.9 - f * 0.25 + t)), int(GREEN[1] * (0.95 - f * 0.2 + t)),
                 int(GREEN[2] * (0.9 - f * 0.25 + t)))
            beaker.put(x, y, (max(0, min(255, g[0])), max(0, min(255, g[1])),
                              max(0, min(255, g[2])), 255))
        else:
            beaker.put(x, y, GLASS + (70,))                   # empty glass
beaker.rect(9, 1, 14, 2, GLASS + (235,))                      # lip
beaker.rect(6, 15, 7, 22, (240, 255, 246, 200))               # inner highlight
for (bx, by) in ((10, 18), (13, 22), (11, 24)):               # bubbles
    beaker.put(bx, by, (214, 255, 224, 255))
beaker.save(os.path.join(OUT, "beaker.png"))

# ---- hop shadow: soft violet ellipse ---------------------------------------------------
shadow = Img(48, 20)
for y in range(20):
    for x in range(48):
        nx, ny = (x - 23.5) / 21.0, (y - 9.5) / 8.0
        d = nx * nx + ny * ny
        if d <= 1.0:
            shadow.put(x, y, (24, 14, 40, int(150 * (1.0 - d * d))))
shadow.save(os.path.join(OUT, "shadow.png"))
