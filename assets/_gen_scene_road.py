#!/usr/bin/env python3
"""Academy road painted scene -> assets/scenes/road_ground.png + road_overlay.png
(2560x736 = 80x23 tiles from assets/maps/road.txt).

Basil's poopy morning sprint: a spline S-curve dirt avenue west->east through a
minty dawn meadow, treeline walls, flower verges, boulder outcrops, and a
widened forecourt at the Academy door. DAWN LIGHT COMES FROM THE EAST (he runs
toward the sunrise — light gradient is reversed vs. the other scenes). The
school facade prop covers the solid 's' block; the ground beneath it just gets
courtyard grass.

The road SPLINE must stay within a tile of the map's '-' cells.

Run: python3 assets/_gen_scene_road.py   then: python3 assets/_check_art.py
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, ZONE_TILE
from _maps import MapData
from _paint import (Painter, fbm, tone_i, curve_field, paint_canopy,
                    stamp_tuft, stamp_flowers, stamp_pebbles, stamp_boulder)

t0 = time.time()
m = MapData(os.path.join(HERE, "maps", "road.txt"))
p = Painter(m, "road", warp_scale=95.0, salt=13)
W, H = p.W, p.H

GRASS = p.mat("grass")
GRASS2 = p.mat("grass2")
GRASS_V = p.mat("grass", shadow="violet")
PATH = p.mat("path")
CANOPY = p.mat("treeline")
TRUNK = p.mat("trunk", spread=0.8)
ROCK = p.mat("rock")
ACCENT = p.scene["accent"]
SHADOW = CANOPY[-1]

macro = fbm(W, H, 190.0, 3, 301, step=2)
hue = fbm(W, H, 300.0, 2, 306, step=4)
mid = fbm(W, H, 46.0, 3, 302, step=2)
fine = fbm(W, H, 9.0, 2, 303, step=1)
cloud = fbm(W, H, 430.0, 2, 304, step=4)
wfld = fbm(W, H, 160.0, 2, 305, step=4)

sdf_tree = p.sdf("#", blur=8, step=8)
sdf_school = p.sdf("s", blur=4, step=8)

# the avenue: west edge -> crest north -> dip south -> Academy forecourt
AVENUE = [(0.5, 12.5), (4.0, 12.4), (8.0, 11.5), (12.0, 10.4), (16.0, 9.2),
          (20.0, 7.9), (25.0, 7.4), (30.0, 7.8), (34.0, 9.2), (38.0, 10.8),
          (41.0, 12.2), (44.0, 13.6), (48.0, 14.9), (52.0, 15.2), (55.0, 14.3),
          (58.0, 13.0), (61.0, 11.9), (64.0, 11.2), (66.5, 10.6)]
trail = curve_field(W, H, [(tx * ZONE_TILE, ty * ZONE_TILE) for (tx, ty) in AVENUE])
DOOR = (66.5 * ZONE_TILE, 10.6 * ZONE_TILE)


def s_path_at(x, y):
    hw = 14.0 + (wfld.sample(x, y) - 0.5) * 9.0
    dx = x - DOOR[0]
    dy = y - DOOR[1]
    d2 = dx * dx + dy * dy
    if d2 < 8100.0:                                # forecourt widens at the door
        hw += (90.0 - d2 ** 0.5) * 0.30
    return trail.sample(x, y) - hw


gb = [bytes(c) for c in GRASS]
g2 = [bytes(c) for c in GRASS2]
gv = [bytes(c) for c in GRASS_V]
pb = [bytes(c) for c in PATH]
buf = p.ground.buf
warped = p.warped
st_ = sdf_tree.sample
ss_ = sdf_school.sample
tr_ = trail.sample
wf_ = wfld.sample
mac_, mid_, fin_, clo_, hue_ = macro.sample, mid.sample, fine.sample, cloud.sample, hue.sample
LK = 0.15 / (W + 1.25 * H)
EX, EY = DOOR

for y in range(H):
    ylk = 1.25 * y
    o = y * W * 4
    for x in range(W):
        wxp, wyp = warped(x, y)
        light = 0.075 - (x + ylk) * LK            # DAWN: lit from the east
        f = fin_(x, y)
        hw = 14.0 + (wf_(x, y) - 0.5) * 9.0
        dx = x - EX
        dy = y - EY
        d2 = dx * dx + dy * dy
        if d2 < 8100.0:
            hw += (90.0 - d2 ** 0.5) * 0.30
        s_path = tr_(wxp, wyp) - hw
        md = mid_(x, y)
        if s_path <= 0.0 and not (s_path > -6.0 and md > 0.66):
            t = 0.30 + (md - 0.5) * 0.18 + (f - 0.5) * 0.14 + light
            if s_path > -2.0:
                t += 0.42                          # packed rim
            elif s_path < -hw * 0.6:
                t -= 0.10                          # worn center
            spk = h2(x, y, 39)
            if spk < 7:
                t += 0.30
            elif spk > 248:
                t -= 0.18
            c = pb[tone_i(5, t, x, y, 43)]
        else:
            t = 0.30 + (mac_(x, y) - 0.5) * 0.46 + (md - 0.5) * 0.24 + (f - 0.5) * 0.10 + light
            s_tree = st_(wxp, wyp)
            if s_tree < 44.0:
                t += (44.0 - s_tree) * 0.0045
            ssch = ss_(wxp, wyp)
            if ssch < 30.0:
                t += (30.0 - ssch) * 0.003         # academy wall shade
            if 0.0 < s_path <= 6.0:
                t += 0.10
            warm = s_tree > 30.0 and hue_(x, y) + (f - 0.5) * 0.2 > 0.62
            cl = clo_(x, y)
            if cl > 0.58:
                t += (cl - 0.58) * 0.9
                ramp_b = gv
            else:
                ramp_b = g2 if warm else gb
            c = ramp_b[tone_i(5, t, x, y, 44)]
        buf[o:o + 4] = c
        o += 4
print(f"ground pass  {time.time()-t0:5.1f}s")

paint_canopy(p, "#", CANOPY, TRUNK, salt=21, shadow_color=SHADOW)
print(f"canopy       {time.time()-t0:5.1f}s")

rocks = sorted((c for c in m.solid_cells() if m.at(*c) == "r"), key=lambda c: (c[1], c[0]))
for (tx, ty) in rocks:
    cx = tx * ZONE_TILE + 16 + (h2(tx, ty, 51) % 7) - 3
    cy = ty * ZONE_TILE + 16 + (h2(tx, ty, 52) % 5) - 2
    stamp_boulder(p, cx, cy, 17 + h2(tx, ty, 53) % 4, ROCK, GRASS, SHADOW, salt=tx * 7 + ty)

for (x, y) in p.scatter(".f-", cell=22, keep=0.55, salt=61, inset=3):
    if s_path_at(x, y) > 2.0:
        stamp_tuft(p, x, y, GRASS, salt=62)

for ty in range(m.rows_n):
    for tx in range(m.cols):
        if m.at(tx, ty) != "f":
            continue
        for k in range(2 + h2(tx, ty, 71) % 2):
            fx = tx * ZONE_TILE + 4 + h2(tx + k, ty, 72) % 24
            fy = ty * ZONE_TILE + 4 + h2(tx, ty + k, 73) % 24
            if s_path_at(fx, fy) > 4.0:
                stamp_flowers(p, fx, fy, ACCENT, GRASS, salt=tx * 13 + ty + k)
        for k in range(3):
            sx = tx * ZONE_TILE + h2(tx * 3 + k, ty, 75) % ZONE_TILE
            sy = ty * ZONE_TILE + h2(tx, ty * 3 + k, 76) % ZONE_TILE
            if s_path_at(sx, sy) > 3.0:
                p.ground.put(sx, sy, (246, 244, 236, 255))

for (tx, ty) in p.tiles("-", pad=1):
    if h2(tx, ty, 91) > 110:
        continue
    x = tx * ZONE_TILE + h2(tx, ty, 92) % ZONE_TILE
    y = ty * ZONE_TILE + h2(tx, ty, 93) % ZONE_TILE
    if 2.0 <= s_path_at(x, y) <= 9.0:
        stamp_pebbles(p, x, y, ROCK, salt=94)
print(f"detail       {time.time()-t0:5.1f}s")

os.makedirs(os.path.join(HERE, "scenes"), exist_ok=True)
p.save(os.path.join(HERE, "scenes", "road_ground.png"),
       os.path.join(HERE, "scenes", "road_overlay.png"))
print(f"total        {time.time()-t0:5.1f}s")
