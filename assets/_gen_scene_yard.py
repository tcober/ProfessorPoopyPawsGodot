#!/usr/bin/env python3
"""Basil's front yard painted scene -> assets/scenes/yard_ground.png +
yard_overlay.png (640x384 = 20x12 tiles from assets/maps/yard.txt).

Painted ONCE in the morning_yard palette (sun-warmed lawn, hot magenta accents);
the night scene applies its violet CanvasModulate on top — one tint mechanism.
Composition: lawn with scene-scale texture, the door path down to the road,
flower beds flanking the door, hedge border, and a soft violet cast shadow
grounding the cottage facade onto the lawn (the house_front.png prop draws over
rows 0-6 at runtime).

Run: python3 assets/_gen_scene_yard.py   then: python3 assets/_check_art.py
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, ZONE_TILE
from _maps import MapData
from _paint import (Painter, fbm, tone_i, curve_field, paint_canopy,
                    stamp_tuft, stamp_flowers)

t0 = time.time()
m = MapData(os.path.join(HERE, "maps", "yard.txt"))
p = Painter(m, "morning_yard", warp_scale=70.0, salt=17)
W, H = p.W, p.H

GRASS = p.mat("grass")
GRASS2 = p.mat("grass2")
PATH = p.mat("path")
HEDGE = p.mat("hedge")
TRUNK = p.mat("timber", spread=0.8)
ACCENT = p.scene["accent"]
SHADOW = HEDGE[-1]

macro = fbm(W, H, 150.0, 3, 401, step=2)
hue = fbm(W, H, 240.0, 2, 406, step=4)
mid = fbm(W, H, 40.0, 3, 402, step=2)
fine = fbm(W, H, 9.0, 2, 403, step=1)
wfld = fbm(W, H, 120.0, 2, 405, step=4)

sdf_hedge = p.sdf("#", blur=6, step=4)

# door path: straight walk from the stoop to the road, gently swaying
WALK = [(10.0, 6.4), (9.95, 8.0), (10.05, 10.0), (10.0, 12.6)]
trail = curve_field(W, H, [(tx * ZONE_TILE, ty * ZONE_TILE) for (tx, ty) in WALK])

gb = [bytes(c) for c in GRASS]
g2 = [bytes(c) for c in GRASS2]
pb = [bytes(c) for c in PATH]
buf = p.ground.buf
warped = p.warped
sh_ = sdf_hedge.sample
tr_ = trail.sample
wf_ = wfld.sample
mac_, mid_, fin_, hue_ = macro.sample, mid.sample, fine.sample, hue.sample
LK = 0.15 / (W + 1.25 * H)
HOUSE_Y = 224.0                                   # facade base (prop bottom edge)

for y in range(H):
    ylk = 1.25 * y
    o = y * W * 4
    for x in range(W):
        wxp, wyp = warped(x, y)
        light = (x + ylk) * LK - 0.075
        f = fin_(x, y)
        hw = 11.0 + (wf_(x, y) - 0.5) * 5.0
        s_path = tr_(wxp, wyp) - hw
        md = mid_(x, y)
        if s_path <= 0.0 and not (s_path > -5.0 and md > 0.68):
            t = 0.30 + (md - 0.5) * 0.18 + (f - 0.5) * 0.14 + light
            if s_path > -2.0:
                t += 0.40
            spk = h2(x, y, 49)
            if spk < 8:
                t += 0.28
            c = pb[tone_i(5, t, x, y, 53)]
        else:
            t = 0.30 + (mac_(x, y) - 0.5) * 0.42 + (md - 0.5) * 0.24 + (f - 0.5) * 0.10 + light
            shd = sh_(wxp, wyp)
            if shd < 30.0:
                t += (30.0 - shd) * 0.005          # hedge contact shade
            # the cottage throws morning shade onto the lawn under the facade
            dy_h = y - HOUSE_Y
            if -6.0 <= dy_h <= 34.0:
                t += 0.16 * (1.0 - abs(dy_h - 8.0) / 30.0)
            if 0.0 < s_path <= 5.0:
                t += 0.10
            ramp_b = g2 if hue_(x, y) + (f - 0.5) * 0.2 > 0.62 else gb
            c = ramp_b[tone_i(5, t, x, y, 54)]
        buf[o:o + 4] = c
        o += 4
print(f"ground pass  {time.time()-t0:5.1f}s")

paint_canopy(p, "#", HEDGE, TRUNK, salt=31, shadow_color=SHADOW)

for (x, y) in p.scatter(".f-", cell=20, keep=0.5, salt=61, inset=3):
    if trail.sample(x, y) > 18.0 and y > 200:
        stamp_tuft(p, x, y, GRASS, salt=62)

for ty in range(m.rows_n):
    for tx in range(m.cols):
        if m.at(tx, ty) != "f":
            continue
        for k in range(2 + h2(tx, ty, 71) % 2):
            fx = tx * ZONE_TILE + 4 + h2(tx + k, ty, 72) % 24
            fy = ty * ZONE_TILE + 4 + h2(tx, ty + k, 73) % 24
            stamp_flowers(p, fx, fy, ACCENT, GRASS, salt=tx * 13 + ty + k)
print(f"detail       {time.time()-t0:5.1f}s")

os.makedirs(os.path.join(HERE, "scenes"), exist_ok=True)
p.save(os.path.join(HERE, "scenes", "yard_ground.png"),
       os.path.join(HERE, "scenes", "yard_overlay.png"))
print(f"total        {time.time()-t0:5.1f}s")
