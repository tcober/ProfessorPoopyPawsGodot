#!/usr/bin/env python3
"""Overworld travel map painted scene -> assets/scenes/overworld_ground.png +
overworld_overlay.png (2048x1152 = 64x36 tiles from assets/maps/overworld.txt).

The CT/FF6 continent as ONE painting: deepwater->shallow sea with horizontal
ripple banding, double broken foam arcs and a wet-sand coast; forests as canopy
masses (deep canopy on the overlay); the mountain range as a painted ridge of
overlapping lit/shadow peaks with snow caps; a river with dark banks, a lighter
center thread and a rosewood plank bridge; hot-violet drained wastes with crack
webs, dead trees and glowing crystals; violet cloud washes; a worn site pad
under each of the five landmark anchors.

Run: python3 assets/_gen_scene_overworld.py   then: python3 assets/_check_art.py
"""
import math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, ZONE_TILE
from _maps import MapData
from _paint import Painter, fbm, tone_i, paint_canopy

t0 = time.time()
m = MapData(os.path.join(HERE, "maps", "overworld.txt"))
p = Painter(m, "overworld", warp_scale=110.0, salt=7)
W, H = p.W, p.H

SEA = p.mat("sea")
GRASS = p.mat("grass")
GRASS_V = p.mat("grass", shadow="violet")
FOREST = p.mat("forest")
ROCK = p.mat("rock")
SAND = p.mat("sand")                     # hand ramp
WASTE = p.mat("waste", shadow="violet")
SNOW = p.mat("snow")
BRIDGE = p.mat("bridge", shadow="violet", spread=0.85)
TRUNK = p.mat("trunk", spread=0.8)
ACCENT = p.scene["accent"]
SHADOW = FOREST[-1]

macro = fbm(W, H, 240.0, 3, 201, step=2)
mid = fbm(W, H, 52.0, 3, 202, step=2)
fine = fbm(W, H, 10.0, 2, 203, step=1)
cloud = fbm(W, H, 520.0, 2, 204, step=4)
crack = fbm(W, H, 34.0, 2, 205, step=2)    # dedicated field — never sample a
                                           # Field outside its domain (it clamps)

sdf_sea = p.sdf("~", blur=10, step=8)
sdf_forest = p.sdf("f", blur=8, step=8)
sdf_mtn = p.sdf("M", blur=6, step=8)
sdf_river = p.sdf("r", blur=6, step=4)   # narrow ribbon: fine grid, strong smooth
sdf_bridge = p.sdf("=", blur=1, step=4)
sdf_waste = p.sdf("x", blur=8, step=8)
sdf_hills = p.sdf("h", blur=6, step=8)

sb_ = [bytes(c) for c in SEA]
gb_ = [bytes(c) for c in GRASS]
gv_ = [bytes(c) for c in GRASS_V]
fb_ = [bytes(c) for c in FOREST]
rb_ = [bytes(c) for c in ROCK]
nb_ = [bytes(c) for c in SAND]
xb_ = [bytes(c) for c in WASTE]
brb_ = [bytes(c) for c in BRIDGE]
tb_ = [bytes(c) for c in TRUNK]

buf = p.ground.buf
warped = p.warped
sea_, for_, mtn_, riv_, brg_, was_, hil_ = (sdf_sea.sample, sdf_forest.sample,
    sdf_mtn.sample, sdf_river.sample, sdf_bridge.sample, sdf_waste.sample,
    sdf_hills.sample)
crk_ = crack.sample
mac_, mid_, fin_, clo_ = macro.sample, mid.sample, fine.sample, cloud.sample
LK = 0.13 / (W + 1.25 * H)

for y in range(H):
    ylk = 1.25 * y
    o = y * W * 4
    for x in range(W):
        wxp, wyp = warped(x, y)
        ssea = sea_(wxp, wyp)
        light = (x + ylk) * LK - 0.065
        f = fin_(x, y)
        if ssea <= 0.0:
            depth = -ssea
            if depth <= 2.2:
                c = sb_[5]                                     # waterline
            elif depth <= 5.5 and f > 0.46:
                c = sb_[0]                                     # inner foam arc
            elif 9.0 <= depth <= 12.5 and f > 0.60:
                c = sb_[1]                                     # outer broken arc
            else:
                d = depth / 150.0                              # gentle: enclosed
                if d > 0.9:                                    # lakes stay teal,
                    d = 0.9                                    # not tar
                t = 0.26 + 0.52 * d + (mid_(x * 0.45, y * 1.9) - 0.5) * 0.20 + light * 0.4
                c = sb_[tone_i(5, t, x, y, 31)]
        else:
            sbrg = brg_(wxp, wyp)
            if sbrg <= 3.0:                                    # rosewood planks
                t = 0.30 + ((y // 3) % 2) * 0.14 + (f - 0.5) * 0.12 + light
                if sbrg > 1.0:
                    t += 0.28                                  # rail shadow edge
                c = brb_[tone_i(5, t, x, y, 32)]
            else:
                sriv = riv_(wxp, wyp)
                if sriv <= 3.0:
                    if sriv > 1.4:
                        c = sb_[5]                             # bank line
                    else:
                        t = 0.30 - (0.10 if sriv < -3.0 else 0.0)
                        t += (mid_(x * 0.5, y * 1.7) - 0.5) * 0.18 + light * 0.4
                        c = sb_[tone_i(5, t + 0.06, x, y, 33)]
                else:
                    swas = was_(wxp, wyp)
                    if swas <= 0.0:
                        cr = crk_(x, y)
                        if abs(cr - 0.5) < 0.014:
                            c = xb_[5]                         # crack web
                        else:
                            t = (0.30 + (mac_(x, y) - 0.5) * 0.34
                                 + (mid_(x, y) - 0.5) * 0.22 + (f - 0.5) * 0.12 + light)
                            c = xb_[tone_i(5, t, x, y, 34)]
                    elif ssea <= 13.0:
                        # beach follows the SMOOTH sea contour, not the blocky
                        # 's' cells (those only matter for collision)
                        t = 0.28 + (mid_(x, y) - 0.5) * 0.22 + (f - 0.5) * 0.16 + light
                        if ssea <= 3.0:
                            t += 0.26                          # wet lip
                        c = nb_[tone_i(5, t, x, y, 35)]
                    else:
                        sfor = for_(wxp, wyp)
                        smtn = mtn_(wxp, wyp)
                        if sfor <= 2.0:
                            t = 0.78 + (f - 0.5) * 0.28        # understory
                            c = tb_[tone_i(5, t, x, y, 36)]
                        elif smtn <= 2.0:
                            t = 0.56 + (mid_(x, y) - 0.5) * 0.26 + (f - 0.5) * 0.12
                            c = rb_[tone_i(5, t, x, y, 37)]    # scree base
                        else:
                            t = (0.30 + (mac_(x, y) - 0.5) * 0.44
                                 + (mid_(x, y) - 0.5) * 0.22 + (f - 0.5) * 0.10 + light)
                            shil = hil_(wxp, wyp)
                            if shil < 0.0:
                                t -= 0.10                      # sunny mounds
                            near = sfor if sfor < smtn else smtn
                            if near < 40.0:
                                t += (40.0 - near) * 0.0042
                            cl = clo_(x, y)
                            if cl > 0.58:
                                t += (cl - 0.58) * 0.9
                                c = gv_[tone_i(5, t, x, y, 38)]
                            else:
                                c = gb_[tone_i(5, t, x, y, 38)]
        buf[o:o + 4] = c
        o += 4
print(f"ground pass  {time.time()-t0:5.1f}s")

# ---- forest canopy masses -------------------------------------------------------------
paint_canopy(p, "f", FOREST, TRUNK, salt=11, shadow_color=SHADOW)
print(f"canopy       {time.time()-t0:5.1f}s")

# ---- the mountain range: overlapping painted peaks, north drawn first ------------------
peaks = []
gridp = 26
for gy in range(H // gridp + 1):
    for gx in range(W // gridp + 1):
        cx = gx * gridp + (h2(gx, gy, 41) * gridp) // 255
        cy = gy * gridp + (h2(gx, gy, 42) * gridp) // 255
        if sdf_mtn.sample(cx, cy) <= -10.0:
            peaks.append((cy, cx, h2(gx, gy, 43)))
peaks.sort()
nR = len(ROCK) - 1
nS = len(SNOW) - 1
ground = p.ground
for (cy, cx, seed) in peaks:
    hgt = 34 + seed % 20
    wid = 24 + seed % 14
    ay = cy - int(hgt * 0.62)
    base = cy + int(hgt * 0.38)
    snowy = hgt >= 46
    for y in range(ay, base + 1):
        fy = (y - ay) / max(1, base - ay)
        half = wid * fy
        xl, xr = int(cx - half), int(cx + half)
        for x in range(xl, xr + 1):
            if sdf_mtn.sample(x, y) > 4.0:
                continue
            side = (x - cx) / max(1.0, half)
            if snowy and fy < 0.30:
                t = 0.28 + 0.30 * (side * 0.6 + fy) + (h2(x // 2, y // 2, 44) - 127.5) / 700.0
                ground.put(x, y, SNOW[tone_i(nS, t, x, y, 45)])
                continue
            if side < 0:
                t = 0.24 + 0.20 * fy - 0.18 * side * -1 * 0.4
            else:
                t = 0.58 + 0.20 * fy + 0.14 * side
            if abs(side) < 0.10:
                t -= 0.16                                      # crest light
            t += (h2(x // 2, y // 2, 46) - 127.5) / 620.0
            ground.put(x, y, ROCK[tone_i(nR, t, x, y, 47)])
print(f"mountains    {time.time()-t0:5.1f}s")

# ---- waste props: dead trees + glowing crystals ----------------------------------------
DEAD = [(96, 74, 128, 255), (68, 50, 96, 255), (44, 32, 66, 255)]
for (x, y) in p.scatter("x", cell=64, keep=0.45, salt=51, inset=10):
    if h2(x, y, 52) < 130:                                     # dead tree
        p.cast_shadow(x + 3, y + 2, 9, 4, SHADOW, 0.3)
        for i in range(12):
            ground.put(x, y - i, DEAD[1 if i < 7 else 0])
            ground.put(x + 1, y - i, DEAD[2])
        for (bx, by) in ((-3, -8), (3, -9), (-2, -11), (4, -6)):
            ground.put(x + bx, y + by, DEAD[0])
            ground.put(x + bx // 2, y + by + 2, DEAD[1])
    else:                                                      # crystal shard
        for dy in range(9):
            hw = max(0, 3 - dy // 2)
            for dx in range(-hw, hw + 1):
                c = ACCENT if abs(dx) < hw else (150, 84, 210, 255)
                ground.put(x + dx, y - dy, c)
        ground.put(x, y - 9, (244, 226, 255, 255))
        for r_ in range(3, 7):
            ground.mix(x - r_, y - 4, ACCENT, 0.10)
            ground.mix(x + r_, y - 4, ACCENT, 0.10)

# sea sparkles
for (x, y) in p.scatter("~", cell=90, keep=0.30, salt=61, inset=24):
    ground.put(x, y, (214, 246, 248, 255))
    ground.put(x - 1, y, (214, 246, 248, 255))
    ground.put(x + 1, y, (214, 246, 248, 255))
    ground.put(x, y - 1, (214, 246, 248, 255))

# ---- worn site pads under the five landmark anchors ------------------------------------
nN = len(SAND) - 1
for name in ("home", "meadow", "town", "cave", "obelisk"):
    tx, ty = m.anchors[name]
    cx, cy = tx * ZONE_TILE + 16, ty * ZONE_TILE + 16
    for y in range(cy - 11, cy + 12):
        ny = (y - cy) / 11.0
        for x in range(cx - 20, cx + 21):
            nx = (x - cx) / 20.0
            d = nx * nx + ny * ny
            if d <= 1.0:
                # worn earth blended into the grass, not stamped over it
                t = 0.30 + 0.28 * d + (h2(x // 2, y // 2, 71) - 127.5) / 640.0
                ground.mix(x, y, SAND[tone_i(nN, t, x, y, 72)], 0.62 * (1.0 - d * d))
print(f"props        {time.time()-t0:5.1f}s")

os.makedirs(os.path.join(HERE, "scenes"), exist_ok=True)
p.save(os.path.join(HERE, "scenes", "overworld_ground.png"),
       os.path.join(HERE, "scenes", "overworld_overlay.png"))
print(f"total        {time.time()-t0:5.1f}s")
