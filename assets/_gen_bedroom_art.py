#!/usr/bin/env python3
"""Bedroom wake-up stage (intro part 2) — full recomposition on the painted-scene
foundation (_core/_paint/_palette). One 640x360 pre-dawn ATTIC composition: gable
ceiling, dusty lavender-blue plaster, and ONE hot light source — the coming dawn
burning through the centered arched window, pooling down the floor and reaching
for Basil's bed. Violet shadows everywhere; rosewood-plum floor (never brown).

Staging map (constants shared with scene/intro_bedroom.gd / .tscn):
  window glass x270..370, sill top y=146  ->  bird PERCH (322, 126)
  bed sprite (120x176 frames) centered    ->  (150, 218)
  nightstand (56x76)                      ->  (240, 188)
  doorway gap in the south frame          ->  x 288..352, doormat at (320, ~300)
  desk / heartbreak corner                ->  right side (his research wall)

  bedroom_bg.png   640x360  the composed room
  bed_basil.png    480x176  4 frames (120x176): asleep A / asleep B / bolt
                            upright / empty messy bed
  bird.png         144x48   3 frames (48x48, faces LEFT): perched / chirp / flap
  nightstand.png   56x76    table + tiny alarm clock on top
  clock_face.png   192x208  close-up, frozen at 8:57 (alarm hand parked at 8)

Re-run: python3 assets/_gen_bedroom_art.py
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, Img, lerp
from _paint import fbm, tone, tone_i
from _palette import SCENES, ramp, BASIL
from _pixfont import draw_text

OUTDIR = os.path.join(HERE, "props")
os.makedirs(OUTDIR, exist_ok=True)

SC = SCENES["bedroom"]
ACCENT = SC["accent"]                                 # hot peach dawn

# 6-tone painted-material ramps (violet shadow law)
WALL = ramp(SC["mats"]["wall"], "violet", 6)          # dusty lavender-blue plaster
FLOOR = ramp(SC["mats"]["floor"], "violet", 6)        # violet-plum plank floor
LINEN = ramp(SC["mats"]["linen"], "violet", 6)

# local material seeds (PALETTE REQUEST: promote into SCENES["bedroom"]["mats"])
TIMBER = ramp((104, 66, 118), "violet", 6)            # plum attic timber
QUILT = ramp((222, 78, 132), "violet", 4)             # hot-magenta quilt (accent kin)
RUGR = ramp((56, 138, 144), "violet", 6)              # teal rug
STEEL = ramp((156, 154, 196), "violet", 6)            # blue-violet clock steel
BRASS = ramp((238, 186, 96), "violet", 4)             # clock bells / knobs
CORK = ramp((196, 132, 140), "violet", 6)             # rose-mauve pin board
CURT = ramp((186, 118, 150), "violet", 6)             # mauve curtains

# dawn seen through the glass — hand ramp, indigo night -> hot peach sunrise
DAWN6 = [(255, 214, 150, 255), (252, 158, 128, 255), (224, 102, 150, 255),
         (166, 72, 158, 255), (96, 54, 142, 255), (46, 36, 96, 255)]

VOID = (10, 8, 24, 255)
VSHADOW = (40, 28, 74, 255)                           # violet cast-shadow color
PAPER = (240, 232, 226, 255)
PAPERD = (206, 196, 204, 255)
INK = (74, 56, 96, 255)
RED = (226, 62, 92, 255)
MINT = (132, 246, 152, 255)                           # lab-fluid green (gun kin)
VIOLETF = (188, 132, 232, 255)                        # round-flask violet

# Basil identity colors
FUR = BASIL["FUR"]
WHT = BASIL["WHITE"]
EYE_Y, EYE_YL = BASIL["EYE_Y"], BASIL["EYE_YL"]
PUPIL, GLINT = BASIL["PUPIL"], BASIL["GLINT"]
GOG, LENS = BASIL["GOGRIM"][1], BASIL["GOGLEN"][0]
EARIN = BASIL["EARIN"]


class P(Img):
    """Img + the float-tolerant line/ring the clock and props want."""

    def put(self, x, y, c):
        super().put(int(x), int(y), c)

    def get(self, x, y):
        return super().get(int(x), int(y))

    def rect(self, x0, y0, x1, y1, c):
        super().rect(int(x0), int(y0), int(x1), int(y1), c)

    def mixv(self, x, y, c, a):
        e = self.get(x, y)
        if e[3] == 0:
            return
        self.put(x, y, (int(e[0] * (1 - a) + c[0] * a),
                        int(e[1] * (1 - a) + c[1] * a),
                        int(e[2] * (1 - a) + c[2] * a), 255))

    def ring(self, cx, cy, r0, r1, c):
        for y in range(int(cy - r1), int(cy + r1) + 2):
            for x in range(int(cx - r1), int(cx + r1) + 2):
                if r0 <= math.hypot(x - cx, y - cy) <= r1:
                    self.put(x, y, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(steps) + 1):
            t = i / steps
            x = round(x0 + (x1 - x0) * t)
            y = round(y0 + (y1 - y0) * t)
            for dy in range(w):
                for dx in range(w):
                    self.put(x + dx, y + dy, c)

    def shadow(self, cx, cy, rx, ry, a=0.30):
        """Soft violet elliptical cast shadow."""
        for y in range(int(cy - ry), int(cy + ry) + 2):
            for x in range(int(cx - rx), int(cx + rx) + 2):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1.0:
                    self.mixv(x, y, VSHADOW, a * (1.0 - d * d))

    def save(self, name):
        super().save(os.path.join(OUTDIR, name))


# =================================================================================
# bedroom_bg.png — the composed 640x360 attic
# =================================================================================
BW, BH = 640, 360
RX0, RY0, RX1, RY1 = 72, 30, 567, 330                 # room interior
WALL_Y = 168                                          # wall / floor split
RIDGE_X, RIDGE_Y, EAVE_Y = 320, 36, 96                # gable geometry
SLOPE = (EAVE_Y - RIDGE_Y) / (RIDGE_X - RX0)
WGX0, WGX1, WGY0, WGY1 = 270, 370, 48, 138            # window glass
SILL_Y = 146
DOOR_X0, DOOR_X1 = 288, 352                           # doorway gap, south frame
BED_X, BED_Y = 150, 218                               # bed sprite center (tscn)
STAND_X, STAND_Y = 240, 188                           # nightstand center (tscn)

bg = P(BW, BH)


def ceil_y(x):
    return RIDGE_Y + abs(x - RIDGE_X) * SLOPE


# ---- void + timber frame around the floating room --------------------------------
bg.rect(0, 0, BW - 1, BH - 1, VOID)
for y in range(BH):
    for x in range(BW):
        if h2(x // 3, y // 3, 90) > 251:
            bg.put(x, y, (18, 14, 38, 255))           # faint void dust
bg.rect(RX0 - 10, RY0 - 10, RX1 + 10, RY1 + 10, TIMBER[5])
bg.rect(RX0 - 7, RY0 - 7, RX1 + 7, RY1 + 7, TIMBER[3])
bg.rect(RX0 - 7, RY0 - 7, RX1 + 7, RY0 - 6, TIMBER[1])   # top catch-light

# ---- wall band: roof underside above the gable line, plaster below ----------------
mottle = fbm(BW, BH, 60.0, 3, 11, step=2)
grain = fbm(BW, BH, 9.0, 2, 12, step=1)
for y in range(RY0, WALL_Y):
    for x in range(RX0, RX1 + 1):
        cl = ceil_y(x)
        if y < cl - 2:
            # sloped roof underside: plank bands parallel to the gable slope
            d = cl - y
            band = int(d / 11)
            t = 0.68 + 0.05 * (band % 3) + (grain.sample(x, y) - 0.5) * 0.16 \
                + d * 0.0022
            bg.put(x, y, tone(TIMBER, min(1.0, t), x, y, 13))
        elif y < cl + 3:
            bg.put(x, y, TIMBER[4])                   # gable trim beam
        else:
            # dusty lavender plaster, brighter toward the dawn window
            wd = max(abs(x - 320) - 58, 0) + max(abs(y - 100) - 52, 0)
            glow = max(0.0, 1.0 - wd / 150.0)
            t = 0.44 + (mottle.sample(x, y) - 0.5) * 0.34 \
                + (grain.sample(x, y) - 0.5) * 0.12 \
                + (y - cl) * 0.0016 - glow * 0.34
            c = tone(WALL, max(0.0, min(1.0, t)), x, y, 14)
            bg.put(x, y, c)
            if glow > 0.42:                           # warm dawn kiss on plaster
                bg.mixv(x, y, ACCENT, (glow - 0.42) * 0.42)
# ridge junction plate
bg.rect(RIDGE_X - 7, RY0, RIDGE_X + 7, RIDGE_Y + 8, TIMBER[4])
bg.rect(RIDGE_X - 7, RY0, RIDGE_X + 7, RY0 + 1, TIMBER[2])
# baseboard
bg.rect(RX0, WALL_Y - 8, RX1, WALL_Y - 3, TIMBER[3])
bg.rect(RX0, WALL_Y - 8, RX1, WALL_Y - 8, TIMBER[1])
bg.rect(RX0, WALL_Y - 3, RX1, WALL_Y - 1, TIMBER[5])

# ---- floor: rosewood-plum planks + the dawn pool ----------------------------------
fmac = fbm(BW, BH, 120.0, 3, 15, step=2)
PLANK_H = 16


def pool_edges(y):
    """The dawn shaft on the floor: a widening cone drifting slightly left."""
    v = (y - (WALL_Y + 4)) / (332.0 - (WALL_Y + 4))
    if v < 0.0:
        return None
    cx = 320 - 34 * v
    hw = 46 + 102 * v
    return cx - hw, cx + hw, v


for y in range(WALL_Y, RY1 + 1):
    plank = (y - WALL_Y) // PLANK_H
    yy = (y - WALL_Y) % PLANK_H
    for x in range(RX0, RX1 + 1):
        t = 0.40 + (fmac.sample(x, y) - 0.5) * 0.30 \
            + (grain.sample(x, y * 2) - 0.5) * 0.14 \
            + (y - WALL_Y) * 0.0009 + abs(x - 320) * 0.00042
        if yy == 0:
            t += 0.30                                 # plank seam
        elif yy == 1:
            t -= 0.12                                 # lit plank edge
        jx = (x + (plank % 2) * 48) % 96              # staggered butt joints
        if jx < 2 and 1 < yy:
            t += 0.22
        if y - WALL_Y < 7:
            t += (7 - (y - WALL_Y)) * 0.045           # wall contact shadow
        bg.put(x, y, tone(FLOOR, max(0.0, min(1.0, t)), x, y, 16))

# the pool of dawn light (with mullion + transom shadow bars: the window's cross
# is cast onto the boards)
for y in range(WALL_Y + 4, RY1 + 1):
    e = pool_edges(y)
    if e is None:
        continue
    xl, xr, v = e
    for x in range(int(xl) - 2, int(xr) + 3):
        u = (x - xl) / (xr - xl)
        if u < 0.0 or u > 1.0:
            continue
        if 0.30 < u < 0.375 or 0.625 < u < 0.70:      # mullion shadows
            continue
        if 0.40 < v < 0.455:                          # transom shadow
            continue
        edge = min(u, 1.0 - u) / 0.12
        if edge > 1.0:
            edge = 1.0
        s = (1.0 - v * 0.52) * edge
        if h2(x // 3, y // 3, 17) < 235:              # clustered dither fringe
            bg.mixv(x, y, (255, 206, 158, 255), 0.34 * s)
# dust motes drifting in the shaft
for k in range(26):
    mx = 250 + h2(k, 1, 18) % 150
    my = WALL_Y + 6 + h2(1, k, 19) % 90
    e = pool_edges(my)
    if e and e[0] + 6 < mx < e[1] - 6:
        bg.put(mx, my, (255, 230, 190, 255))

# ---- doorway gap in the south frame + stairs down + doormat -----------------------
bg.rect(DOOR_X0, RY1 + 1, DOOR_X1, RY1 + 10, FLOOR[2])
for i, (sy0, sy1) in enumerate(((RY1 + 11, RY1 + 18), (RY1 + 19, RY1 + 25),
                                (RY1 + 26, RY1 + 31))):
    inset = 6 + i * 5
    bg.rect(DOOR_X0 + inset, sy0, DOOR_X1 - inset, sy1, FLOOR[4 if i < 2 else 5])
    bg.rect(DOOR_X0 + inset, sy0, DOOR_X1 - inset, sy0, FLOOR[3])
bg.rect(DOOR_X0 - 3, RY1 - 2, DOOR_X0 - 1, RY1 + 10, TIMBER[5])  # jambs
bg.rect(DOOR_X1 + 1, RY1 - 2, DOOR_X1 + 3, RY1 + 10, TIMBER[5])
# doormat
for y in range(292, 316):
    for x in range(280, 361):
        t = 0.38 + (grain.sample(x * 2, y * 2) - 0.5) * 0.30
        if y in (292, 315) or x in (280, 360):
            t = 0.85
        bg.put(x, y, tone(CORK, max(0.0, min(1.0, t)), x, y, 20))
for x in range(288, 353, 16):
    bg.rect(x, 298, x + 6, 300, CORK[4])
    bg.rect(x + 6, 306, x + 12, 308, CORK[4])

# ---- teal rug (center, under Basil's dash to the door) ----------------------------
for y in range(214, 286):
    for x in range(250, 471):
        d = ((x - 360) / 96.0) ** 2 + ((y - 250) / 33.0) ** 2
        if d <= 1.0:
            t = 0.34 + d * 0.34 + (grain.sample(x, y) - 0.5) * 0.22
            if d > 0.86:
                t += 0.30                             # rolled dark edge
            bg.put(x, y, tone(RUGR, max(0.0, min(1.0, t)), x, y, 21))
        elif d <= 1.08:
            bg.mixv(x, y, VSHADOW, 0.18 * (1.08 - d) / 0.08)

# ---- cast shadows that ground the sprite furniture --------------------------------
bg.shadow(BED_X - 12, 304, 76, 15, 0.34)              # bed
bg.shadow(STAND_X - 4, 228, 30, 8, 0.30)              # nightstand
bg.shadow(470, 262, 66, 11, 0.28)                     # desk
bg.shadow(396, 268, 13, 5, 0.26)                      # wastebasket

# ---- the window: arched dawn, curtains, sill (bird perch) -------------------------
# frame + arched glass
for y in range(WGY0 - 8, SILL_Y):
    if y < 70:
        k = (70 - y) / 22.0
        hw = 50 * math.sqrt(max(0.0, 1 - k * k))
    else:
        hw = 50
    fx0, fx1 = 320 - hw - 7, 320 + hw + 7
    for x in range(int(fx0), int(fx1) + 1):
        bg.put(x, y, TIMBER[4 if (x < fx0 + 3 or x > fx1 - 3 or y < WGY0 - 5) else 3])
sky = fbm(BW, BH, 40.0, 2, 22, step=2)
for y in range(WGY0, WGY1 + 1):
    if y < 70:
        k = (70 - y) / 22.0
        hw = 50 * math.sqrt(max(0.0, 1 - k * k))
    else:
        hw = 50
    tv = (y - WGY0) / float(WGY1 - WGY0)
    for x in range(int(320 - hw), int(320 + hw) + 1):
        t = (1.0 - tv) + (sky.sample(x, y) - 0.5) * 0.18
        d = math.hypot(x - 296, y - 120)
        t -= max(0.0, 1.0 - d / 40.0) * 0.55          # sun bloom
        c = tone(DAWN6, max(0.0, min(1.0, t)), x, y, 23)
        bg.put(x, y, c)
        if d < 13:
            bg.put(x, y, (255, 240, 200, 255))        # the rising sun itself
        elif d < 17:
            bg.mixv(x, y, (255, 226, 172, 255), 0.6)
# a sleeping world outside: violet rooftops along the glass bottom
for x in range(272, 369):
    ry = 128 + ((x // 14) * 7 % 9) - 4
    for y in range(ry, WGY1 + 1):
        bg.put(x, y, (58, 42, 104, 255) if y > ry else (108, 74, 150, 255))
# mullions (their shadows are the bars in the floor pool)
bg.rect(317, WGY0 + 4, 322, WGY1, TIMBER[3])
bg.rect(272, 92, 368, 96, TIMBER[3])
bg.rect(317, WGY0 + 4, 318, WGY1, TIMBER[1])
bg.rect(272, 92, 368, 92, TIMBER[1])
# sill — the bird's stage
bg.rect(254, SILL_Y, 386, SILL_Y + 7, WALL[1])
bg.rect(254, SILL_Y, 386, SILL_Y + 1, WALL[0])
bg.rect(254, SILL_Y + 8, 386, SILL_Y + 11, WALL[3])
bg.rect(254, SILL_Y + 12, 386, SILL_Y + 13, VSHADOW)
# half-drawn curtains flanking the glass, tied back (he stopped closing them)
for (cx0, cx1, tie) in ((246, 268, 1), (372, 394, -1)):
    for y in range(44, 158):
        sway = int(2 * math.sin(y * 0.09))
        for x in range(cx0 + sway, cx1 + sway + 1):
            t = 0.30 + 0.5 * abs(math.sin((x - cx0) * 0.55)) \
                + (y - 44) * 0.002
            if y > 118:                               # gathered by the tieback
                t += (y - 118) * 0.004
            bg.put(x, y, tone(CURT, max(0.0, min(1.0, t)), x, y, 24))
    ty = 122
    tx = cx0 + 6 if tie > 0 else cx1 - 12
    bg.rect(tx, ty, tx + 7, ty + 4, BRASS[1])
    bg.rect(tx, ty, tx + 7, ty, BRASS[0])
# curtain rod
bg.rect(240, 40, 400, 43, TIMBER[4])
bg.rect(240, 40, 400, 40, TIMBER[2])

# ---- hanging shelf over the bed: books + a flask (the scientist sleeps under
# his library) -----------------------------------------------------------------
SPINES = [(214, 84, 118, 255), (96, 120, 208, 255), (98, 172, 138, 255),
          (238, 172, 96, 255), (166, 100, 202, 255), (82, 164, 172, 255)]
SHX0, SHX1, SHY = 100, 208, 118
bg.rect(SHX0, SHY, SHX1, SHY + 5, TIMBER[2])          # board
bg.rect(SHX0, SHY, SHX1, SHY, TIMBER[0])
bg.rect(SHX0, SHY + 5, SHX1, SHY + 6, TIMBER[5])
for bx in (SHX0 + 4, SHX1 - 8):                       # brackets
    bg.rect(bx, SHY + 6, bx + 4, SHY + 14, TIMBER[4])
for y in range(SHY + 6, SHY + 12):                    # AO under the board
    for x in range(SHX0, SHX1 + 1):
        if (x + y) % 2 == 0:
            bg.mixv(x, y, VSHADOW, 0.3)
x = SHX0 + 4
k = 0
while x < SHX1 - 26:
    wsp = 8 + h2(x, 0, 25) % 6
    hsp = 18 + h2(x, 1, 26) % 8
    c = SPINES[k % len(SPINES)]
    lean = 1 if h2(x, 2, 27) < 40 else 0
    bg.rect(x + lean, SHY - hsp, x + wsp, SHY - 1, c)
    bg.rect(x + lean, SHY - hsp, x + lean, SHY - 1,
            (max(0, c[0] - 52), max(0, c[1] - 52), max(0, c[2] - 36), 255))
    bg.rect(x + lean, SHY - hsp, x + wsp, SHY - hsp + 1,
            (min(255, c[0] + 34), min(255, c[1] + 34), min(255, c[2] + 34), 255))
    bg.rect(x + 2 + lean, SHY - hsp // 2, x + wsp - 2, SHY - hsp // 2, TIMBER[5])
    x += wsp + 2
    k += 1
# a little round flask at the shelf's end, violet liquid catching nothing yet
bg.ring(SHX1 - 13, SHY - 8, 6.0, 7.6, (216, 226, 240, 255))
for y in range(SHY - 8, SHY - 1):
    for x in range(SHX1 - 20, SHX1 - 6):
        if math.hypot(x - (SHX1 - 13), y - (SHY - 8)) <= 6:
            bg.put(x, y, VIOLETF)
bg.rect(SHX1 - 15, SHY - 19, SHX1 - 11, SHY - 14, (216, 226, 240, 255))
bg.put(SHX1 - 16, SHY - 10, (236, 214, 250, 255))

# ---- the research corner (right): pinned wall of his thesis + desk ----------------
# corkboard with papers, red string, the diploma — and one face-down photo frame
CBX0, CBY0, CBX1, CBY1 = 408, 100, 532, 152
bg.rect(CBX0 - 4, CBY0 - 4, CBX1 + 4, CBY1 + 4, TIMBER[3])
bg.rect(CBX0 - 4, CBY0 - 4, CBX1 + 4, CBY0 - 3, TIMBER[1])
for y in range(CBY0, CBY1 + 1):
    for x in range(CBX0, CBX1 + 1):
        t = 0.42 + (grain.sample(x * 1.7, y * 1.7) - 0.5) * 0.4
        bg.put(x, y, tone(CORK, max(0.0, min(1.0, t)), x, y, 28))
for (px, py, pw, ph, tilt) in ((414, 106, 18, 22, 0), (438, 110, 22, 16, 1),
                               (492, 104, 20, 24, 0), (466, 122, 18, 18, -1)):
    for y in range(py, py + ph):
        off = tilt * (y - py) // 8
        bg.rect(px + off, y, px + pw + off, y, PAPER if (y - py) % 6 else PAPERD)
    for ly in range(py + 4, py + ph - 3, 4):
        bg.rect(px + 2 + tilt * (ly - py) // 8, ly, px + pw - 3, ly, PAPERD)
    bg.put(px + pw // 2, py - 1, RED)                 # pin
# the diploma, gold seal — pinned among the mess now
bg.rect(508, 122, 528, 146, PAPER)
bg.rect(508, 122, 528, 123, (255, 244, 220, 255))
draw_text(bg.put, "PHD", 510, 128, INK, 1)
bg.rect(520, 138, 524, 142, RED)
# red string routing pin to pin (an obsession wall)
bg.line(423, 105, 449, 109, RED)
bg.line(449, 109, 502, 103, RED)
bg.line(502, 103, 475, 121, RED)
draw_text(bg.put, "WHERE DID", 440, 132, INK, 1)
draw_text(bg.put, "IT GO?", 446, 140, INK, 1)

# desk under the board
DKX0, DKX1 = 416, 540
bg.rect(DKX0, 196, DKX1, 202, TIMBER[1])              # lit top slab
bg.rect(DKX0, 202, DKX1, 206, TIMBER[3])
bg.rect(DKX0 + 4, 206, DKX1 - 4, 252, TIMBER[3])      # body
for y in range(206, 252):
    for x in range(DKX0 + 4, DKX1 - 3):
        t = 0.52 + (grain.sample(x, y) - 0.5) * 0.2 + (y - 206) * 0.004
        bg.put(x, y, tone(TIMBER, min(1.0, t), x, y, 29))
bg.rect(DKX0 + 14, 212, DKX1 - 14, 228, TIMBER[4])    # drawer
bg.rect(DKX0 + 14, 212, DKX1 - 14, 213, TIMBER[2])
bg.rect(472, 218, 478, 222, BRASS[1])
bg.rect(DKX0 + 4, 252, DKX0 + 14, 262, TIMBER[5])     # legs
bg.rect(DKX1 - 14, 252, DKX1 - 4, 262, TIMBER[5])
# on the desk: book stack, erlenmeyer with mint fluid, papers, face-down frame
for i, c in enumerate((SPINES[1], SPINES[3], SPINES[0])):
    bw_ = 34 - i * 4
    bg.rect(430, 188 - i * 6, 430 + bw_, 193 - i * 6, c)
    bg.rect(430, 188 - i * 6, 430 + bw_, 188 - i * 6,
            (min(255, c[0] + 30), min(255, c[1] + 30), min(255, c[2] + 30), 255))
for i in range(13):                                   # erlenmeyer
    yy = 174 + i * 1.7
    half = 3 + i * 0.8
    bg.rect(494 - half, yy, 494 + half, yy + 1, (214, 226, 240, 255))
    if i > 6:
        bg.rect(494 - half + 2, yy, 494 + half - 2, yy + 1, MINT)
bg.rect(491, 168, 497, 174, (214, 226, 240, 255))
bg.put(490, 186, (236, 250, 238, 255))
# face-down picture frame — he can't look at her yet
bg.rect(508, 190, 534, 197, TIMBER[2])
bg.rect(508, 190, 534, 191, TIMBER[0])
bg.rect(514, 186, 528, 190, TIMBER[4])                # its little stand, folded
# loose papers
for (px, py) in ((444, 198), (462, 200)):
    bg.rect(px, py - 3, px + 16, py + 2, PAPER)
    bg.rect(px + 2, py - 1, px + 13, py - 1, PAPERD)

# wastebasket + crumpled paper balls that missed
bg.rect(386, 240, 408, 266, STEEL[3])
bg.rect(386, 240, 408, 243, STEEL[1])
bg.rect(388, 244, 390, 264, STEEL[2])
for (cx, cy) in ((376, 270), (414, 274), (398, 236)):
    bg.ring(cx, cy, 0, 3.4, PAPERD)
    bg.put(cx - 1, cy - 1, PAPER)
    bg.put(cx + 1, cy, PAPER)

# a "MAGIC SLEEPS" thesis poster on the left slope's kneewall, slightly askew
bg.rect(94, 62, 96, 96, TIMBER[4])                    # its nail + string
for i, y in enumerate(range(64, 96)):
    off = i // 12
    bg.rect(228 + off, y, 296 + off, y, (226, 220, 238, 255) if (y % 8) else PAPERD)
draw_text(bg.put, "MAGIC", 240, 68, (126, 96, 186, 255), 2)
draw_text(bg.put, "SLEEPS", 236, 82, (170, 120, 150, 255), 2)
bg.put(262, 62, RED)

bg.save("bedroom_bg.png")

# =================================================================================
# bed_basil.png — 4 frames of 120x176 (asleep A / asleep B / upright / empty)
# =================================================================================
FW, FH = 120, 176
bd = P(FW * 4, FH)


def bed_base(ox):
    # corner posts
    for (px, py) in ((6, 8), (104, 8), (6, 156), (104, 156)):
        bd.rect(ox + px, py, ox + px + 9, py + 9, TIMBER[3])
        bd.rect(ox + px, py, ox + px + 1, py + 1, TIMBER[1])
        bd.rect(ox + px + 8, py + 8, ox + px + 9, py + 9, TIMBER[5])
    # headboard: rounded plum slats
    bd.rect(ox + 10, 10, ox + 109, 36, TIMBER[3])
    bd.rect(ox + 12, 8, ox + 107, 10, TIMBER[3])
    bd.rect(ox + 12, 8, ox + 107, 8, TIMBER[1])
    for sx in range(ox + 24, ox + 100, 16):
        bd.rect(sx, 12, sx + 1, 34, TIMBER[5])
    bd.rect(ox + 10, 34, ox + 109, 36, TIMBER[5])
    # mattress
    for y in range(38, 154):
        for x in range(14, 106):
            t = 0.5 + (h2((ox + x) // 3, y // 3, 30) - 127.5) / 640.0
            bd.put(ox + x, y, tone(LINEN, max(0.0, min(1.0, t)), ox + x, y, 31))
    # footboard
    bd.rect(ox + 10, 148, ox + 109, 166, TIMBER[3])
    bd.rect(ox + 10, 148, ox + 109, 149, TIMBER[1])
    bd.rect(ox + 10, 164, ox + 109, 166, TIMBER[5])


def pillow(ox, dented=False):
    for y in range(42, 66):
        for x in range(24, 96):
            ex = min(x - 24, 96 - x)
            ey = min(y - 42, 66 - y)
            if ex + ey < 3:
                continue
            t = 0.16 + 0.34 * (y - 42) / 24.0 + (h2(x // 3, y // 3, 32) - 127.5) / 900.0
            bd.put(ox + x, y, tone(LINEN, max(0.0, min(1.0, t)), ox + x, y, 33))
    if dented:
        for y in range(48, 58):
            for x in range(44, 76):
                if ((x - 60) / 16.0) ** 2 + ((y - 53) / 5.0) ** 2 <= 1.0:
                    bd.mixv(ox + x, y, LINEN[4], 0.5)


def quilt(ox, y0, y1, ridge=True, salt=34):
    """Hot-magenta quilt with a diamond lattice; optional body ridge under it."""
    for y in range(y0, y1 + 1):
        for x in range(14, 106):
            t = 0.34 + 0.3 * (y - y0) / max(1, y1 - y0)
            if ridge and 38 <= x <= 74:               # the sleeping lump
                d = 1.0 - ((x - 56) / 20.0) ** 2
                t -= 0.34 * max(0.0, d) * (1.0 - abs(y - (y0 + y1) / 2) / ((y1 - y0) / 1.6))
            lat = (x + y) % 24
            lat2 = (x - y) % 24
            if lat < 2 or lat2 < 2:
                t += 0.22                             # lattice stitching
            t += (h2(x // 3, y // 3, salt) - 127.5) / 800.0
            bd.put(ox + x, y, tone(QUILT, max(0.0, min(1.0, t)), ox + x, y, salt))
    bd.rect(ox + 14, y1 - 1, ox + 105, y1 + 1, QUILT[3])
    # folded linen band at the top of the quilt
    bd.rect(ox + 14, y0 - 8, ox + 105, y0, LINEN[1])
    bd.rect(ox + 14, y0 - 8, ox + 105, y0 - 7, LINEN[0])
    bd.rect(ox + 14, y0 - 1, ox + 105, y0, LINEN[3])


def head_sleeping(ox, hy, breath=0):
    """Basil asleep on the pillow: black dome, goggles pushed up, sweet ^ ^ eyes."""
    hx = ox + 60
    for (ex, s) in ((-16, 1), (16, -1)):              # relaxed ears
        for i in range(9):
            half = max(1, 4 - i // 2)
            bd.rect(hx + ex - half, hy - 18 + i, hx + ex + half, hy - 18 + i,
                    FUR[1] if s > 0 else FUR[2])
        bd.rect(hx + ex - 1, hy - 14, hx + ex + 1, hy - 12, EARIN)
    for y in range(hy - 12, hy + 13):                 # dome, violet-shadowed
        for x in range(hx - 14, hx + 15):
            d = ((x - hx) / 14.0) ** 2 + ((y - hy) / 12.0) ** 2
            if d <= 1.0:
                t = 0.30 + 0.5 * ((x - hx) / 14.0 * 0.3 + (y - hy) / 12.0 * 0.9) + 0.2 * d
                bd.put(x, y, tone(FUR, max(0.0, min(1.0, t)), x, y, 35))
    bd.rect(hx - 2, hy - 7, hx + 2, hy + 3, WHT[0])   # blaze
    for y in range(hy + 3, hy + 10):                  # muzzle
        for x in range(hx - 6, hx + 7):
            if ((x - hx) / 6.5) ** 2 + ((y - hy - 6) / 4.0) ** 2 <= 1.0:
                bd.put(x, y, WHT[0 if y < hy + 7 else 1])
    for ex in (hx - 9, hx + 5):                       # closed ^ ^ eyes
        bd.put(ex, hy - 1 + breath, WHT[3])
        bd.put(ex + 1, hy - 2 + breath, WHT[3])
        bd.put(ex + 2, hy - 3 + breath, WHT[3])
        bd.put(ex + 3, hy - 2 + breath, WHT[3])
        bd.put(ex + 4, hy - 1 + breath, WHT[3])
    bd.rect(hx - 1, hy + 3, hx + 1, hy + 5, BASIL["NOSE"])
    bd.rect(hx - 13, hy - 11, hx + 13, hy - 9, GOG)   # goggles pushed up
    bd.rect(hx - 4, hy - 15, hx + 3, hy - 12, LENS)
    bd.rect(hx - 4, hy - 15, hx - 1, hy - 14, (252, 236, 200, 255))
    bd.put(hx - 17, hy + 2, WHT[3])                   # whisker ticks
    bd.put(hx + 17, hy + 2, WHT[3])


# frames 0 & 1: asleep, breathing
for f, br in enumerate((0, 1)):
    ox = f * FW
    bed_base(ox)
    pillow(ox)
    quilt(ox, 72 + br * 2, 146, ridge=True, salt=34 + f)
    head_sleeping(ox, 52 + br, br)

# frame 2: bolt upright
ox = FW * 2
bed_base(ox)
pillow(ox, dented=True)
quilt(ox, 112, 146, ridge=False, salt=36)
hx, hy = ox + 60, 56
# torso: black chest with the white bib, arms thrown wide
for y in range(74, 114):
    for x in range(40, 81):
        ex = min(x - 40, 80 - x)
        if ex + min(y - 74, 113 - y) < 3:
            continue
        t = 0.34 + (x - 40) / 60.0 * 0.2 + (y - 74) / 60.0 * 0.4
        bd.put(ox + x, y, tone(FUR, max(0.0, min(1.0, t)), ox + x, y, 37))
for y in range(76, 108):                              # bib
    for x in range(52, 69):
        if ((x - 60) / 8.5) ** 2 + ((y - 90) / 16.0) ** 2 <= 1.0:
            bd.put(ox + x, y, WHT[0 if x < 64 else 1])
for (ax0, ax1, shade) in ((22, 42, 0), (78, 98, 1)):  # arms out
    bd.rect(ox + ax0, 80, ox + ax1, 90, FUR[1 + shade])
    bd.rect(ox + ax0, 80, ox + ax1, 82, FUR[0 + shade])
    cx = ax0 + 3 if ax0 < 60 else ax1 - 3             # white paw mitts
    for y in range(78, 92):
        for x in range(cx - 6, cx + 7):
            if ((x - cx) / 6.0) ** 2 + ((y - 85) / 6.5) ** 2 <= 1.0:
                bd.put(ox + x, y, WHT[0 if y < 86 else 1])
for (ex, s) in ((-17, 1), (17, -1)):                  # tall alarm ears
    for i in range(13):
        half = max(1, 4 - i // 3)
        bd.rect(hx + ex - half, hy - 30 + i, hx + ex + half, hy - 30 + i,
                FUR[1] if s > 0 else FUR[2])
    bd.rect(hx + ex - 1, hy - 24, hx + ex + 1, hy - 22, EARIN)
for y in range(hy - 14, hy + 13):                     # head
    for x in range(hx - 14, hx + 15):
        d = ((x - hx) / 14.0) ** 2 + ((y - hy + 1) / 13.0) ** 2
        if d <= 1.0:
            t = 0.30 + 0.5 * ((x - hx) / 14.0 * 0.3 + (y - hy) / 13.0 * 0.9) + 0.2 * d
            bd.put(x, y, tone(FUR, max(0.0, min(1.0, t)), x, y, 38))
bd.rect(hx - 2, hy - 9, hx + 2, hy + 2, WHT[0])
for y in range(hy + 2, hy + 10):
    for x in range(hx - 6, hx + 7):
        if ((x - hx) / 6.5) ** 2 + ((y - hy - 5) / 4.2) ** 2 <= 1.0:
            bd.put(x, y, WHT[0 if y < hy + 6 else 1])
for ex in (hx - 11, hx + 4):                          # WIDE eyes
    bd.rect(ex, hy - 7, ex + 7, hy - 1, EYE_Y)
    bd.rect(ex, hy - 7, ex + 7, hy - 6, EYE_YL)
    bd.rect(ex + 2, hy - 5, ex + 4, hy - 1, PUPIL)
    bd.put(ex + 2, hy - 5, GLINT)
bd.rect(hx - 2, hy + 5, hx + 2, hy + 8, (96, 54, 60, 255))    # gasp
bd.rect(hx - 13, hy - 13, hx + 13, hy - 11, GOG)
bd.rect(hx - 4, hy - 17, hx + 3, hy - 14, LENS)
for (sx, sy) in ((hx - 24, hy - 32), (hx, hy - 38), (hx + 24, hy - 32)):
    bd.rect(sx, sy - 3, sx, sy, EYE_YL)               # shock ticks
    bd.rect(sx - 2, sy - 1, sx + 2, sy - 1, EYE_YL)

# frame 3: empty, quilt flung over the foot corner
ox = FW * 3
bed_base(ox)
pillow(ox, dented=True)
for y in range(88, 152):                              # the flung heap
    xl = 44 + int((y - 88) * 0.5) + (h2(0, y // 2, 39) % 3 - 1) * 2
    for x in range(xl, 116):
        t = 0.4 + (y - 88) / 90.0 + (h2(x // 3, y // 3, 40) - 127.5) / 700.0
        if (x + y) % 24 < 2 or (x - y) % 24 < 2:
            t += 0.2
        bd.put(ox + x, y, tone(QUILT, max(0.0, min(1.0, t)), ox + x, y, 41))
    bd.put(ox + xl, y, QUILT[3])
for y in range(88, 104):                              # flipped linen corner
    bd.rect(ox + 82 + (y - 88), y, ox + 108, y, LINEN[1])
    bd.rect(ox + 82 + (y - 88), y, ox + 83 + (y - 88), y, LINEN[0])
bd.rect(ox + 16, 140, ox + 44, 144, LINEN[1])         # trailing sheet tail
bd.rect(ox + 16, 143, ox + 44, 144, LINEN[3])

bd.save("bed_basil.png")

# =================================================================================
# bird.png — 3 frames of 48x48, faces LEFT: perched / chirp+note / flap
# =================================================================================
BODY = ramp((112, 152, 226), "violet", 4)
CHEST = (255, 178, 128, 255)
CHESTD = (224, 130, 104, 255)
BEAK = (250, 208, 96, 255)
LEG = (150, 108, 76, 255)
NOTE = (36, 30, 70, 255)
bi = P(144, 48)


def bird(ox, mode):
    up = 3 if mode == "chirp" else 0
    lift = 2 if mode == "flap" else 0
    # tail: kicked up to the right
    for i in range(9):
        ty = 24 - i if mode != "flap" else 26 - i // 2
        bi.rect(ox + 33 + i, ty, ox + 37 + i, ty + 2, BODY[2])
    bi.rect(ox + 41, 16 if mode != "flap" else 22, ox + 43, 18 if mode != "flap" else 24, BODY[3])
    # body
    for y in range(20 - lift, 38 - lift):
        for x in range(12, 38):
            d = ((x - 24) / 12.0) ** 2 + ((y - 29 + lift) / 8.5) ** 2
            if d <= 1.0:
                t = 0.28 + 0.5 * ((x - 24) / 12.0 * 0.35 + (y - 29 + lift) / 8.5 * 0.85) + 0.15 * d
                bi.put(x + ox, y, tone(BODY, max(0.0, min(1.0, t)), x, y, 50, jitter=0.2))
    # peach chest
    for y in range(26 - lift, 38 - lift):
        for x in range(14, 27):
            if ((x - 20) / 6.5) ** 2 + ((y - 32 + lift) / 5.5) ** 2 <= 1.0:
                bi.put(x + ox, y, CHEST if y < 33 - lift else CHESTD)
    # head
    hy = 19 - up - lift
    for y in range(hy - 8, hy + 9):
        for x in range(8, 26):
            if ((x - 16) / 8.5) ** 2 + ((y - hy) / 8.0) ** 2 <= 1.0:
                t = 0.24 + 0.5 * ((x - 16) / 8.5 * 0.35 + (y - hy) / 8.0 * 0.8)
                bi.put(x + ox, y, tone(BODY, max(0.0, min(1.0, t)), x, y, 51, jitter=0.2))
    # wing
    if mode == "flap":
        for i in range(11):                           # both wings up
            bi.rect(ox + 18 + i, 6 + i, ox + 22 + i, 9 + i, BODY[2])
            bi.rect(ox + 30 - i // 2, 8 + i, ox + 33 - i // 2, 10 + i, BODY[1])
        bi.rect(ox + 28, 4, ox + 33, 7, BODY[1])
    else:
        for y in range(22, 33):
            for x in range(24, 37):
                if ((x - 30) / 6.5) ** 2 + ((y - 27) / 5.5) ** 2 <= 1.0:
                    bi.put(x + ox, y, BODY[2 if y < 28 else 3])
        bi.rect(ox + 26, 25, ox + 33, 25, BODY[3])    # feather lines
        bi.rect(ox + 27, 28, ox + 34, 28, BODY[3])
    # face
    bi.rect(ox + 12, hy - 2, ox + 13, hy - 1, PUPIL)
    bi.put(ox + 12, hy - 3, GLINT)
    if mode == "chirp":                               # open beak + eighth note
        bi.rect(ox + 4, hy - 3, ox + 9, hy - 1, BEAK)
        bi.rect(ox + 4, hy + 2, ox + 9, hy + 3, BEAK)
        bi.rect(ox + 38, 4, ox + 39, 13, NOTE)
        bi.ring(ox + 36, 14, 0, 2.6, NOTE)
        bi.rect(ox + 38, 4, ox + 43, 6, NOTE)
    else:
        bi.rect(ox + 4, hy - 1, ox + 9, hy + 1, BEAK)
    # legs
    if mode != "flap":
        for lx in (ox + 20, ox + 27):
            bi.rect(lx, 37, lx + 1, 43, LEG)
            bi.rect(lx - 2, 43, lx + 3, 43, LEG)
    else:
        bi.rect(ox + 21, 36, ox + 22, 40, LEG)
        bi.rect(ox + 26, 36, ox + 27, 40, LEG)


bird(0, "perch")
bird(48, "chirp")
bird(96, "flap")
bi.save("bird.png")

# =================================================================================
# nightstand.png (56x76) — plum table, alarm clock on top, book on the lower shelf
# =================================================================================
ns = P(56, 76)
ns.rect(0, 24, 55, 30, TIMBER[1])                     # top board (lit)
ns.rect(0, 30, 55, 31, TIMBER[4])
ns.rect(4, 32, 51, 64, TIMBER[3])                     # body
for y in range(32, 65):
    for x in range(4, 52):
        t = 0.5 + (h2(x // 2, y // 2, 60) - 127.5) / 600.0 + (y - 32) * 0.004
        ns.put(x, y, tone(TIMBER, max(0.0, min(1.0, t)), x, y, 61))
ns.rect(8, 34, 47, 46, TIMBER[4])                     # drawer
ns.rect(8, 34, 47, 35, TIMBER[2])
ns.rect(25, 38, 29, 42, BRASS[1])
ns.rect(25, 38, 26, 39, BRASS[0])
ns.rect(8, 50, 47, 62, TIMBER[5])                     # open shelf
ns.rect(12, 54, 38, 61, (98, 120, 208, 255))          # a book shoved in
ns.rect(12, 54, 38, 55, (128, 150, 232, 255))
ns.rect(4, 64, 12, 75, TIMBER[5])                     # legs
ns.rect(43, 64, 51, 75, TIMBER[5])
# the little alarm clock on top
ns.rect(19, 4, 23, 6, BRASS[1])                       # bells
ns.rect(20, 2, 22, 3, BRASS[0])
ns.rect(31, 4, 35, 6, BRASS[1])
ns.rect(32, 2, 34, 3, BRASS[0])
for y in range(6, 24):
    for x in range(17, 38):
        d = math.hypot(x - 27, y - 14)
        if d <= 9.5:
            ns.put(x, y, STEEL[2] if d > 6.5 else (246, 242, 232, 255))
            if d > 6.5 and x < 25 and y < 12:
                ns.put(x, y, STEEL[0])                # rim light
ns.rect(26, 10, 27, 14, (40, 36, 54, 255))            # hands ~ 8:57
ns.rect(23, 14, 26, 15, (40, 36, 54, 255))
ns.rect(21, 22, 25, 24, STEEL[4])                     # feet
ns.rect(30, 22, 34, 24, STEEL[4])
ns.save("nightstand.png")

# =================================================================================
# clock_face.png (192x208) — the close-up: 8:57, alarm hand parked at 8
# =================================================================================
ck = P(192, 208)
CX, CY = 96, 120
CFACE, CFACED = (248, 244, 234, 255), (222, 216, 214, 255)
CDARK = (40, 34, 54, 255)
for (bx, flip) in ((54, 1), (138, -1)):               # brass bells
    for y in range(6, 48):
        for x in range(bx - 24, bx + 25):
            d = ((x - bx) / 23.0) ** 2 + ((y - 27) / 21.0) ** 2
            if d <= 1.0:
                t = 0.28 + 0.5 * ((x - bx) / 23.0 * 0.5 + (y - 27) / 21.0 * 0.8) + 0.2 * d
                ck.put(x, y, tone(BRASS, max(0.0, min(1.0, t)), x, y, 70))
    ck.ring(bx, 27, 19.5, 22.5, (150, 108, 56, 255))
    ck.put(bx - 8 * flip, 16, (255, 244, 214, 255))
ck.rect(92, 2, 99, 14, STEEL[3])                      # striker
for y in range(0, 9):
    for x in range(90, 102):
        if ((x - 95.5) / 5.2) ** 2 + ((y - 4) / 4.4) ** 2 <= 1.0:
            ck.put(x, y, STEEL[1])
ck.rect(52, 192, 68, 204, STEEL[4])                   # feet
ck.rect(124, 192, 140, 204, STEEL[4])
ck.rect(48, 202, 72, 206, STEEL[5])
ck.rect(120, 202, 144, 206, STEEL[5])
for y in range(CY - 80, CY + 81):                     # steel body
    for x in range(CX - 80, CX + 81):
        d = math.hypot(x - CX, y - CY)
        if d <= 80:
            t = 0.3 + ((x - CX) * 0.4 + (y - CY) * 0.8) / 160.0 + (d / 80.0) ** 3 * 0.3
            ck.put(x, y, tone(STEEL, max(0.0, min(1.0, t)), x, y, 71))
for a in range(198, 262):                             # dawn rim light upper-left
    x = CX + 77 * math.cos(math.radians(a))
    y = CY + 77 * math.sin(math.radians(a))
    ck.rect(x, y, x + 2, y + 1, (236, 214, 196, 255))
for y in range(CY - 66, CY + 67):                     # cream face
    for x in range(CX - 66, CX + 67):
        d = math.hypot(x - CX, y - CY)
        if d <= 66:
            c = CFACE
            if (x - CX) * 0.45 + (y - CY) * 0.85 > 20 and h2(x // 3, y // 3, 72) < 150:
                c = CFACED                            # violet-cool lower shading
            ck.put(x, y, c)
ck.ring(CX, CY, 64, 66, STEEL[4])
for i in range(12):                                   # ticks
    a = math.radians(i * 30)
    x0 = CX + 56 * math.sin(a); y0 = CY - 56 * math.cos(a)
    x1 = CX + 62 * math.sin(a); y1 = CY - 62 * math.cos(a)
    ck.line(x0, y0, x1, y1, CDARK, 2)
draw_text(ck.put, "12", CX - 11, 54, CDARK, 2)
draw_text(ck.put, "3", CX + 44, CY - 6, CDARK, 2)
draw_text(ck.put, "6", CX - 5, CY + 46, CDARK, 2)
draw_text(ck.put, "9", CX - 52, CY - 6, CDARK, 2)
# alarm hand: still parked at 8 — it never rang
a = math.radians(8 * 30)
ck.line(CX, CY, CX + 40 * math.sin(a), CY - 40 * math.cos(a), RED, 2)
for y in range(-4, 5):
    for x in range(-4, 5):
        if x * x + y * y <= 12:
            ck.put(CX + 44 * math.sin(a) + x, CY - 44 * math.cos(a) + y, RED)
# hour hand just shy of 9, minute at :57
a = math.radians(8.95 * 30)
ck.line(CX, CY, CX + 34 * math.sin(a), CY - 34 * math.cos(a), CDARK, 4)
a = math.radians(57 * 6)
ck.line(CX, CY, CX + 54 * math.sin(a), CY - 54 * math.cos(a), CDARK, 2)
ck.line(CX, CY, CX + 30 * math.sin(a), CY - 30 * math.cos(a), CDARK, 4)
for y in range(-5, 6):                                # hub
    for x in range(-5, 6):
        if x * x + y * y <= 24:
            ck.put(CX + x, CY + y, CDARK)
ck.put(CX - 2, CY - 2, STEEL[1])
ck.save("clock_face.png")
