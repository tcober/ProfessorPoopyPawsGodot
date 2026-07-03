#!/usr/bin/env python3
"""Whisker Meadow painted scene -> assets/scenes/meadow_ground.png + meadow_overlay.png.

Reads assets/maps/meadow.txt (the collision/logic source of truth) and paints the
whole 1536x768 scene as one composition: scene-scale grass fields (no tile can
repeat), a domain-warped pond with waterline/foam/wet-sand shoreline, a spline
trail (grass and path are both walkable, so the trail ignores the tile grid
entirely and is painted as a smooth curve), a tree-blob border canopy (fringe
below entities, deep canopy on the overlay above them), boulder outcrops, and
off-lattice tufts/flowers/pebbles/sparkles.

The trail SPLINE must stay within a tile of the map's '-' cells so the map file
remains an honest picture of the scene.

Run: python3 assets/_gen_scene_meadow.py   then: python3 assets/_check_art.py
"""
import math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, ZONE_TILE
from _maps import MapData
from _paint import (Painter, fbm, tone_i, curve_field, paint_canopy,
                    stamp_tuft, stamp_flowers, stamp_pebbles, stamp_boulder,
                    stamp_sparkle)

t0 = time.time()
m = MapData(os.path.join(HERE, "maps", "meadow.txt"))
p = Painter(m, "meadow", warp_scale=90.0, salt=3)
W, H = p.W, p.H

GRASS = p.mat("grass")
GRASS2 = p.mat("grass2")                       # warmer drift patches
GRASS_V = p.mat("grass", shadow="violet")      # violet wash under cloud shade
GRASS2_V = p.mat("grass2", shadow="violet")
PATH = p.mat("path")                           # hand-tuned identity ramp
WATER = p.mat("water")
CANOPY = p.mat("treeline")
TRUNK = p.mat("trunk", spread=0.8)
ROCK = p.mat("rock")
ACCENT = p.scene["accent"]
SHADOW = CANOPY[-1]

# scene-scale texture fields (these spanning the whole map is what kills the grid)
macro = fbm(W, H, 190.0, 3, 101, step=2)   # rolling light/dark meadow patches
hue = fbm(W, H, 300.0, 2, 106, step=4)     # warm/cool grass drift
mid = fbm(W, H, 46.0, 3, 102, step=2)      # mottle
fine = fbm(W, H, 9.0, 2, 103, step=1)      # blade-scale grain
cloud = fbm(W, H, 430.0, 2, 104, step=4)   # drifting cloud shade
wfld = fbm(W, H, 150.0, 2, 105, step=4)    # trail width variation

# organic boundaries: coarse+blurred SDFs melt the 32px tile steps entirely
sdf_tree = p.sdf("#", blur=8, step=8)
sdf_pond = p.sdf("o", blur=10, step=8)

# the trail: a Catmull-Rom spline tracking the map's '-' cells (tile coords x32)
TRAIL = [(24.0, 24.5), (23.2, 21.5), (21.5, 19.2), (19.2, 17.0), (17.2, 15.0),
         (15.3, 13.0), (13.6, 11.2), (13.1, 9.8), (14.2, 8.3), (16.5, 7.0),
         (19.5, 6.2), (22.8, 5.7), (26.3, 5.4)]
trail = curve_field(W, H, [(tx * ZONE_TILE, ty * ZONE_TILE) for (tx, ty) in TRAIL])
TRAIL_END = (TRAIL[-1][0] * ZONE_TILE, TRAIL[-1][1] * ZONE_TILE)


def s_path_at(x, y):
    """Signed distance to the trail edge (negative on the path)."""
    hw = 11.0 + (wfld.sample(x, y) - 0.5) * 8.0
    dx = x - TRAIL_END[0]
    dy = y - TRAIL_END[1]
    d2 = dx * dx + dy * dy
    if d2 < 1600.0:                      # trailhead widens toward the cairn
        hw += (40.0 - d2 ** 0.5) * 0.24
    return trail.sample(x, y) - hw


# ---- master ground pass -------------------------------------------------------------
# One walk over every pixel; material chosen by warped signed distances, tone by
# layered noise + upper-left light + edge vignettes. Bytes are written directly.
gb = [bytes(c) for c in GRASS]
g2 = [bytes(c) for c in GRASS2]
gbv = [bytes(c) for c in GRASS_V]
g2v = [bytes(c) for c in GRASS2_V]
pb = [bytes(c) for c in PATH]
wb = [bytes(c) for c in WATER]
buf = p.ground.buf
warped = p.warped
sp_ = sdf_pond.sample
st_ = sdf_tree.sample
tr_ = trail.sample
wf_ = wfld.sample
mac_, mid_, fin_, clo_ = macro.sample, mid.sample, fine.sample, cloud.sample
hue_ = hue.sample
LK = 0.14 / (W + 1.25 * H)
EX, EY = TRAIL_END

for y in range(H):
    ylk = 1.25 * y
    o = y * W * 4
    for x in range(W):
        wxp, wyp = warped(x, y)
        s_pond = sp_(wxp, wyp)
        light = (x + ylk) * LK - 0.07
        f = fin_(x, y)
        if s_pond <= 0.0:
            depth = -s_pond
            if depth <= 2.0:
                c = wb[5]
            elif depth <= 6.0 and f > 0.46:
                c = wb[0]
            else:
                d = depth / 60.0
                if d > 1.0:
                    d = 1.0
                # anisotropic mid sample -> CT-style horizontal ripple banding
                t = 0.28 + 0.50 * d + (mid_(x * 0.45, y * 1.9) - 0.5) * 0.22 + light * 0.5
                c = wb[tone_i(5, t, x, y, 21)]
        elif s_pond <= 6.0 and mid_(x, y) > 0.36:
            # wet-sand collar (dry-path tones), broken where grass meets water
            t = 0.24 + s_pond * 0.04 + (f - 0.5) * 0.16 + light
            c = pb[tone_i(5, t, x, y, 22)]
        else:
            hw = 11.0 + (wf_(x, y) - 0.5) * 8.0
            dx = x - EX
            dy = y - EY
            d2 = dx * dx + dy * dy
            if d2 < 1600.0:
                hw += (40.0 - d2 ** 0.5) * 0.24
            s_path = tr_(wxp, wyp) - hw
            md = mid_(x, y)
            if s_path <= 0.0 and not (s_path > -6.0 and md > 0.66):
                t = 0.30 + (md - 0.5) * 0.18 + (f - 0.5) * 0.14 + light
                if s_path > -2.0:
                    t += 0.42                       # thin packed-dirt rim
                elif s_path < -hw * 0.6:
                    t -= 0.10                       # worn light center lane
                spk = h2(x, y, 29)
                if spk < 7:
                    t += 0.30                       # embedded grit
                elif spk > 248:
                    t -= 0.18
                c = pb[tone_i(5, t, x, y, 23)]
            else:
                t = 0.30 + (mac_(x, y) - 0.5) * 0.48 + (md - 0.5) * 0.24 + (f - 0.5) * 0.10 + light
                s_tree = st_(wxp, wyp)
                if s_tree < 44.0:
                    t += (44.0 - s_tree) * 0.0045   # treeline ambient occlusion
                if 0.0 < s_path <= 6.0:
                    t += 0.10                       # trodden fringe
                # warm drift patches, noise-dithered edge, kept off the treeline AO
                warm = s_tree > 30.0 and hue_(x, y) + (f - 0.5) * 0.2 > 0.62
                cl = clo_(x, y)
                if cl > 0.58:
                    # drifting cloud shade as a VIOLET wash (the color-script move)
                    t += (cl - 0.58) * 0.9
                    ramp_b = g2v if warm else gbv
                else:
                    ramp_b = g2 if warm else gb
                c = ramp_b[tone_i(5, t, x, y, 24)]
        buf[o:o + 4] = c
        o += 4
print(f"ground pass  {time.time()-t0:5.1f}s")

# ---- canopy border (fringe under entities, deep canopy on overlay) ------------------
paint_canopy(p, "#", CANOPY, TRUNK, salt=1, shadow_color=SHADOW)
print(f"canopy       {time.time()-t0:5.1f}s")

# ---- boulder outcrops (one squat boulder per rock cell, jittered, north first) ------
rocks = sorted((c for c in m.solid_cells() if m.at(*c) == "r"), key=lambda c: (c[1], c[0]))
for (tx, ty) in rocks:
    cx = tx * ZONE_TILE + 16 + (h2(tx, ty, 51) % 7) - 3
    cy = ty * ZONE_TILE + 16 + (h2(tx, ty, 52) % 5) - 2
    stamp_boulder(p, cx, cy, 17 + h2(tx, ty, 53) % 4, ROCK, GRASS, SHADOW, salt=tx * 7 + ty)

# trailhead cairn — the focal point the path leads to (walkable; just paint)
cx, cy = int(TRAIL_END[0]), int(TRAIL_END[1])
stamp_boulder(p, cx, cy - 3, 13, ROCK, GRASS, SHADOW, salt=201)
stamp_boulder(p, cx - 2, cy - 13, 8, ROCK, GRASS, SHADOW, salt=202)
for k in range(7):
    ang = math.radians(k * 51 + h2(cx, k, 209) % 30)
    rr = 30 + h2(k, cy, 208) % 14
    fx = cx + int(rr * math.cos(ang))
    fy = cy + int(rr * 0.7 * math.sin(ang))
    stamp_flowers(p, fx, fy, ACCENT, GRASS, salt=210 + k)
print(f"boulders     {time.time()-t0:5.1f}s")

# ---- scattered detail (all off-lattice, all deterministic) --------------------------
for (x, y) in p.scatter(".f-", cell=22, keep=0.55, salt=61, inset=3):
    if s_path_at(x, y) > 2.0 and sdf_pond.sample(x, y) > 12.0:
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
        for k in range(3):  # baby's-breath specks between the clumps
            sx = tx * ZONE_TILE + h2(tx * 3 + k, ty, 75) % ZONE_TILE
            sy = ty * ZONE_TILE + h2(tx, ty * 3 + k, 76) % ZONE_TILE
            if s_path_at(sx, sy) > 3.0:
                p.ground.put(sx, sy, (246, 244, 236, 255))

for (x, y) in p.scatter(".", cell=96, keep=0.30, salt=81, inset=8):
    if s_path_at(x, y) > 10.0 and sdf_pond.sample(x, y) > 16.0 and sdf_tree.sample(x, y) > 20.0:
        stamp_flowers(p, x, y, ACCENT, GRASS, salt=x + y)

for (tx, ty) in p.tiles("-", pad=1):
    if h2(tx, ty, 91) > 110:
        continue
    x = tx * ZONE_TILE + h2(tx, ty, 92) % ZONE_TILE
    y = ty * ZONE_TILE + h2(tx, ty, 93) % ZONE_TILE
    s = s_path_at(x, y)
    if 2.0 <= s <= 9.0 and sdf_pond.sample(x, y) > 12.0:
        stamp_pebbles(p, x, y, ROCK, salt=94)

SPARKLE = (214, 246, 248, 255)
for (x, y) in p.scatter("o", cell=44, keep=0.45, salt=95, inset=12):
    stamp_sparkle(p, x, y, SPARKLE)
print(f"detail       {time.time()-t0:5.1f}s")

os.makedirs(os.path.join(HERE, "scenes"), exist_ok=True)
p.save(os.path.join(HERE, "scenes", "meadow_ground.png"),
       os.path.join(HERE, "scenes", "meadow_overlay.png"))
print(f"total        {time.time()-t0:5.1f}s")
