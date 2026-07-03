#!/usr/bin/env python3
"""Title-screen poster -> assets/title_bg.png (640x360) + assets/leaf.png (10x10).

The game's poster, recomposed: a posterized indigo->magenta->gold sunset with
streaked clouds and a sinking sun, the drained world as far silhouettes (the
Academy tower west, the OBELISK east — the whole story on one card), a dark
meadow field with hot-pink flower glints, framing treeline silhouettes, and the
stacked gold logo in the native 10x16 font. Basil's walking sprite
(scene/title.tscn) crosses the bottom band at y=318; the composition keeps that
strip readable.

Run: python3 assets/_gen_title.py
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img, h2, lerp
from _paint import fbm
from font._glyphs14 import GLYPHS16, ADVANCE

W, H = 640, 360
HORIZON = 232

# posterized sky stations, top -> horizon
SKY = [(34, 24, 74), (66, 34, 108), (118, 44, 132), (176, 56, 138),
       (226, 92, 128), (248, 152, 108), (255, 206, 96)]
FIELD = [(46, 96, 96), (36, 76, 88), (28, 58, 76), (22, 42, 62)]
SILH = (52, 30, 84)          # far hills / landmarks
TREE = (24, 18, 52)          # framing canopy
SUN = ((255, 238, 170), (255, 214, 110), (255, 182, 92))
ACCENT = (255, 116, 176)

img = Img(W, H)
# cloud streaks are sampled anisotropically at y*2.6 — the field must be tall
# enough to cover that or Field.sample clamps into vertical banding
streak = fbm(W, H * 3, 26.0, 2, 601, step=2)
grain = fbm(W, H, 8.0, 2, 602, step=1)

for y in range(H):
    for x in range(W):
        if y < HORIZON:
            f = y / HORIZON
            q = f * (len(SKY) - 1)
            # cluster-jittered posterized bands
            q += (h2(x // 3, y // 3, 603) - 127.5) / 255.0 * 0.55
            i = max(0, min(len(SKY) - 1, int(q + 0.5)))
            c = SKY[i]
            # long horizontal cloud streaks, gold-rimmed near the sunset band
            st = streak.sample(x * 0.22, y * 2.6)
            if st > 0.62 and 0.25 < f < 0.95:
                c = lerp(c, SKY[max(0, i - 2)], 0.55)
                if st > 0.72:
                    c = lerp(c, (255, 214, 130), 0.35 * (1.0 - abs(f - 0.75)))
            img.put(x, y, (c[0], c[1], c[2], 255))
        else:
            f = (y - HORIZON) / (H - HORIZON)
            q = f * (len(FIELD) - 1) + (h2(x // 3, y // 3, 604) - 127.5) / 255.0 * 0.7
            q += (grain.sample(x, y) - 0.5) * 0.8
            i = max(0, min(len(FIELD) - 1, int(q + 0.5)))
            c = FIELD[i]
            img.put(x, y, (c[0], c[1], c[2], 255))

# stars in the indigo
for k in range(70):
    sx = h2(k, 1, 605) * W // 255
    sy = (h2(1, k, 606) * 90) // 255
    if h2(sx, sy, 607) < 160:
        img.put(sx, sy, (230, 224, 255, 255))

# the sinking sun + posterized halo
scx, scy, sr = 452, 208, 30
for r, c in ((sr + 14, (250, 170, 110)), (sr + 7, SUN[2]), (sr, SUN[1])):
    for y in range(scy - r, min(HORIZON, scy + r) + 1):
        for x in range(scx - r, scx + r + 1):
            if (x - scx) ** 2 + (y - scy) ** 2 <= r * r:
                if r > sr:
                    img.mix(x, y, (c[0], c[1], c[2], 255), 0.42)
                else:
                    img.put(x, y, (c[0], c[1], c[2], 255))
img.rect(scx - sr + 6, scy - sr + 8, scx - sr + 14, scy - sr + 12,
         (SUN[0][0], SUN[0][1], SUN[0][2], 255))

# far silhouettes on the horizon: rolling hills, Academy tower west, OBELISK east
for x in range(W):
    hh = 10 + int(6 * math.sin(x * 0.02) + 4 * math.sin(x * 0.053 + 2))
    for y in range(HORIZON - hh, HORIZON + 2):
        img.put(x, y, (SILH[0], SILH[1], SILH[2], 255))
img.rect(66, HORIZON - 30, 98, HORIZON, (SILH[0], SILH[1], SILH[2], 255))
img.rect(74, HORIZON - 44, 90, HORIZON - 30, (SILH[0], SILH[1], SILH[2], 255))
img.rect(70, HORIZON - 52, 78, HORIZON - 44, (SILH[0], SILH[1], SILH[2], 255))
for i in range(46):                                              # the obelisk
    hw = max(1, 7 - i // 6)
    img.rect(560 - hw, HORIZON - i, 560 + hw, HORIZON - i, (SILH[0], SILH[1], SILH[2], 255))
img.put(560, HORIZON - 47, (ACCENT[0], ACCENT[1], ACCENT[2], 255))  # its stolen spark
img.put(560, HORIZON - 49, (240, 220, 255, 255))

# meadow glints: hot-pink flowers + chalk-mint motes catching the last light
for k in range(140):
    fx = h2(k, 3, 609) * W // 255
    fy = HORIZON + 14 + (h2(3, k, 610) * (H - HORIZON - 22)) // 255
    if h2(fx, fy, 611) < 110:
        img.put(fx, fy, (ACCENT[0], ACCENT[1], ACCENT[2], 255))
        img.put(fx, fy - 1, (255, 190, 220, 255))
    elif h2(fx, fy, 612) < 80:
        img.put(fx, fy, (150, 240, 214, 255))

# framing treeline silhouettes, bottom corners
for (cx, cy, n) in ((-30, 372, 7), (668, 368, 7), (40, 392, 5), (600, 396, 5)):
    for k in range(n):
        bx = cx + (h2(k, cy, 613) % 130) - 65
        by = cy - (h2(cx, k, 614) % 46)
        r = 26 + h2(bx, by, 615) % 22
        for y in range(max(0, by - r), min(H, by + r)):
            for x in range(max(0, bx - r), min(W, bx + r)):
                if (x - bx) ** 2 + (y - by) ** 2 <= r * r:
                    img.put(x, y, (TREE[0], TREE[1], TREE[2], 255))


# ---- stacked gold logo in the native 10x16 font (2x = 20x32 caps) ---------------------
def stamp_line(text, cy, scale=2):
    width = len(text) * ADVANCE * scale - 2 * scale
    x0 = (W - width) // 2
    # collect glyph pixels first
    pix = set()
    cx = x0
    for ch in text:
        rows = GLYPHS16.get(ch, GLYPHS16["?"])
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "X":
                    for sy in range(scale):
                        for sx in range(scale):
                            pix.add((cx + rx * scale + sx, cy + ry * scale + sy))
        cx += ADVANCE * scale
    for (x, y) in pix:                                           # dark halo
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-2, -1, 0, 1, 2):
                if (x + dx, y + dy) not in pix:
                    img.put(x + dx, y + dy, (44, 22, 64, 255))
    for (x, y) in pix:
        f = ((y - cy) / (16.0 * scale))
        c = lerp((255, 236, 160), (244, 164, 84), f)
        img.put(x, y, (c[0], c[1], c[2], 255))


stamp_line("PROFESSOR", 36)
stamp_line("POOPY PAWS", 76)

img.save(os.path.join(HERE, "title_bg.png"))

# a drifting leaf for the CPUParticles emitter
leaf = Img(10, 10)
for (x, y) in ((4, 1), (3, 2), (4, 2), (5, 2), (2, 3), (3, 3), (4, 3), (5, 3),
               (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (3, 5), (4, 5), (5, 5),
               (6, 5), (4, 6), (5, 6), (6, 6), (5, 7)):
    leaf.put(x, y, (255, 178, 96, 255))
for (x, y) in ((4, 2), (4, 3), (4, 4), (5, 5), (5, 6)):
    leaf.put(x, y, (226, 128, 70, 255))                          # midrib
leaf.save(os.path.join(HERE, "leaf.png"))
