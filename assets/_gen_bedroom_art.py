#!/usr/bin/env python3
"""Props for the bedroom wake-up scene (intro part 2), drawn for the 640x360 stage
at the 2x art scale — the CT room-on-black framing gets closer, the furniture
doubles. Same cottage palette as _gen_intro_art.py / _palette.py. Writes PNGs into
assets/props/. Re-run: python3 assets/_gen_bedroom_art.py

  bedroom_bg.png   640x360  Chrono Trigger-style compact room floating on black:
                            timbered wall, window (bird perch ~(476,130)), science
                            shelf, rug, doorway gap + doormat at the bottom
  bed_basil.png    448x160  4 frames (112x160): asleep A / asleep B / bolt upright /
                            empty messy bed
  bird.png         144x48   3 frames (48x48, faces LEFT): perched / chirp+note / flap
  nightstand.png   52x68    little table with a tiny alarm clock on top
  clock_face.png   192x208  close-up alarm clock frozen at 8:57 (alarm hand at 8)
"""
import os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _pixfont import draw_text, text_width
from _artlib import Img as _Img, h2

OUTDIR = os.path.join(HERE, "props")
os.makedirs(OUTDIR, exist_ok=True)


class Img(_Img):
    """_artlib.Img plus the float-tolerant put/ring/line the clock art needs."""

    def put(self, x, y, c):
        super().put(int(x), int(y), c)

    def get(self, x, y):
        return super().get(int(x), int(y))

    def rect(self, x0, y0, x1, y1, c):
        super().rect(int(x0), int(y0), int(x1), int(y1), c)

    def mix(self, x, y, c, a):
        e = self.get(x, y)
        if e[3] == 0:
            return
        self.put(x, y, (int(e[0] * (1 - a) + c[0] * a),
                        int(e[1] * (1 - a) + c[1] * a),
                        int(e[2] * (1 - a) + c[2] * a), 255))

    def ring(self, cx, cy, r0, r1, c):
        for y in range(int(cy - r1), int(cy + r1) + 2):
            for x in range(int(cx - r1), int(cx + r1) + 2):
                d = math.hypot(x - cx, y - cy)
                if r0 <= d <= r1:
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

    def save(self, name):
        super().save(os.path.join(OUTDIR, name))


# ---- shared cottage palette (matches _gen_intro_art.py's color script) -----------
# Paper Girls duotone: periwinkle plaster with violet shadows, plum timber,
# rosewood floor, hot-magenta quilt, teal rug — warm lights, cool shadows.
PLAS  = (208, 196, 232, 255)
PLASD = (178, 164, 210, 255)
PLASL = (228, 220, 246, 255)
BEAM  = (104, 60, 78, 255)
BEAMD = (72, 40, 58, 255)
FRAME = (124, 76, 84, 255)
WOOD  = (198, 128, 100, 255)
WOODD = (164, 98, 88, 255)
WOODL = (222, 158, 118, 255)
KNOB  = (246, 198, 96, 255)
BAG   = (172, 118, 84, 255)
BAGD  = (134, 88, 68, 255)
BAGL  = (198, 148, 104, 255)
# Basil (from _palette.BASIL ramps)
FUR0, FUR1, FUR2, FUR3 = (78, 74, 96, 255), (52, 50, 66, 255), (34, 32, 46, 255), (20, 18, 30, 255)
WHT0, WHT1, WHT3 = (250, 248, 242, 255), (228, 224, 216, 255), (162, 158, 166, 255)
EYE_Y, EYE_YL = (240, 202, 66, 255), (252, 230, 120, 255)
PUPIL, GLINT = (16, 12, 16, 255), (255, 255, 250, 255)
GOG, LENS = (112, 78, 50, 255), (238, 214, 168, 255)
EARIN = (204, 116, 134, 255)
GUNE = (132, 246, 152, 255)
GUNP = (188, 132, 232, 255)
# quilt (hot magenta — the room's Paper Girls accent)
QUILT, QUILTD, QUILTL = (216, 74, 122, 255), (170, 46, 100, 255), (240, 108, 142, 255)
SHEET, SHEETD = (240, 238, 230, 255), (212, 208, 198, 255)
# steel / clock (blue-violet steel)
STL0, STL1, STL2, STL3 = (198, 198, 224, 255), (148, 148, 178, 255), (112, 110, 144, 255), (58, 56, 84, 255)
CLKFACE, CLKFACED = (246, 243, 234, 255), (224, 220, 210, 255)
CLKDARK = (40, 36, 44, 255)
RED = (234, 56, 94, 255)

# =================================================================================
# bedroom_bg.png (640x360) — CT room floating on a black void, framed CLOSER for
# the 2x furniture. Room interior (96,24)-(543,335); wall band down to y=167,
# plank floor below, doorway gap at bottom-center (Basil exits south over the
# doormat). Bird perch: sill top y=148, sprite center ~(476,130).
# =================================================================================
BW, BH = 640, 360
RX0, RY0, RX1, RY1 = 96, 24, 543, 335                     # room interior
FLOOR_Y = 168                                             # wall/floor split
DOOR_X0, DOOR_X1 = 280, 360                               # gap in the bottom frame
bg = Img(BW, BH)

# deep-indigo void + timber frame around the room
bg.rect(0, 0, BW - 1, BH - 1, (12, 8, 24, 255))
bg.rect(RX0 - 10, RY0 - 10, RX1 + 10, RY1 + 10, BEAMD)
bg.rect(RX0 - 7, RY0 - 7, RX1 + 7, RY1 + 7, BEAM)
bg.rect(RX0 - 7, RY0 - 7, RX1 + 7, RY0 - 7, WOODL)        # top edge catch-light
bg.rect(RX0 - 7, RY0 - 6, RX1 + 7, RY0 - 6, WOODL)

# plaster wall band with noise
bg.rect(RX0, RY0, RX1, FLOOR_Y - 1, PLAS)
for y in range(RY0, FLOOR_Y):
    for x in range(RX0, RX1 + 1):
        r = h2(x // 2, y // 2, 11)
        if r < 12:
            bg.put(x, y, PLASD)
        elif r > 246:
            bg.put(x, y, PLASL)
bg.rect(RX0, RY0, RX1, RY0 + 7, BEAMD)                    # ceiling shadow line
for y in range(RY0 + 8, RY0 + 20):                        # violet shadow falloff
    for x in range(RX0, RX1 + 1):
        if (x // 2 + y // 2) % 2 == 0 or y < RY0 + 14:
            bg.mix(x, y, (146, 126, 182, 255), 0.45)
# timber verticals (clear of shelf 128..296, diploma 316..392, window 400..520)
for bx in (104, 302, 394, 528):
    bg.rect(bx, RY0 + 7, bx + 6, FLOOR_Y - 1, BEAM)
    bg.rect(bx + 5, RY0 + 7, bx + 6, FLOOR_Y - 1, BEAMD)
# baseboard
bg.rect(RX0, FLOOR_Y - 16, RX1, FLOOR_Y - 5, BEAM)
bg.rect(RX0, FLOOR_Y - 5, RX1, FLOOR_Y - 1, BEAMD)

# plank floor (horizontal boards, staggered joints)
bg.rect(RX0, FLOOR_Y, RX1, RY1, WOOD)
bg.rect(DOOR_X0, RY1, DOOR_X1, RY1 + 10, WOOD)            # floor tongue out the door
for y in range(FLOOR_Y, RY1 + 11):
    for x in range(RX0, RX1 + 1):
        if y > RY1 and not (DOOR_X0 <= x <= DOOR_X1):
            continue
        r = h2(x // 2, y // 2, 12)
        if r < 9:
            bg.put(x, y, WOODD)
        elif r > 249:
            bg.put(x, y, WOODL)
for y in range(FLOOR_Y + 31, RY1, 32):
    bg.rect(RX0, y, RX1, y + 1, WOODD)
    off = 64 if ((y - FLOOR_Y) // 32) % 2 else 0
    for jx in range(RX0 + off, RX1, 128):
        bg.rect(jx, y - 30, jx + 1, y - 2, WOODD)
bg.rect(RX0, FLOOR_Y, RX1, FLOOR_Y + 2, WOODD)            # wall contact shadow
bg.rect(DOOR_X0 - 2, RY1 - 4, DOOR_X0 - 1, RY1 + 10, BEAMD)   # door jambs
bg.rect(DOOR_X1 + 1, RY1 - 4, DOOR_X1 + 2, RY1 + 10, BEAMD)

# round rug, center-right of the room (bed sits at x~208) — saturated teal
RUG, RUGD, RUGL = (62, 142, 140, 255), (38, 108, 112, 255), (98, 176, 162, 255)
for y in range(FLOOR_Y, RY1 + 1):
    for x in range(RX0, RX1 + 1):
        d = ((x - 408) / 118.0) ** 2 + ((y - 258) / 52.0) ** 2
        if d <= 1.0:
            c = RUG
            if d > 0.82:
                c = RUGD
            elif d < 0.5 and h2(x // 2, y // 2, 13) < 26:
                c = RUGL
            bg.put(x, y, c)

# window (frame 400..520 x 36..148), Paper Girls dawn: indigo -> magenta -> gold,
# posterize-dithered like the title sky, low sun burning through
bg.rect(400, 36, 520, 148, FRAME)
bg.rect(400, 36, 520, 40, BEAMD)
DAWN = [(0.0, (96, 66, 148)), (0.55, (216, 106, 150)), (1.0, (252, 200, 122))]
for y in range(44, 140):
    t = (y - 44) / 95.0
    for si in range(len(DAWN) - 1):
        t0, c0 = DAWN[si]
        t1, c1 = DAWN[si + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            base = tuple(int(c0[i] + (c1[i] - c0[i]) * f) for i in range(3))
            break
    for x in range(408, 513):
        q = tuple(min(255, (ch // 16) * 16 + (8 if (x // 2 + y // 2) % 2 else 0)) for ch in base)
        bg.put(x, y, q + (255,))
for y in range(44, 140):                                  # low sun glow
    for x in range(408, 513):
        d = math.hypot(x - 432, y - 116)
        if d < 22:
            bg.put(x, y, (255, 240, 190, 255))
        elif d < 30:
            bg.mix(x, y, (255, 226, 170, 255), 0.5)
bg.rect(457, 44, 462, 139, FRAME)                         # mullions
bg.rect(408, 88, 512, 91, FRAME)
bg.rect(388, 140, 532, 150, PLASL)                        # sill (bird perch ~(476,130))
bg.rect(388, 150, 532, 154, PLASD)
# a little basil plant on the sill (of course he grows basil)
bg.rect(408, 126, 428, 140, (170, 96, 60, 255))
bg.rect(408, 126, 428, 128, (196, 118, 76, 255))
for (lx, ly) in ((412, 114), (420, 108), (426, 116), (416, 120), (424, 122)):
    bg.oval(lx, ly, 4.8, 3.6, (86, 150, 74, 255))
    bg.rect(lx - 1, ly - 3, lx + 1, ly - 2, (120, 190, 96, 255))

# pool of morning light on the floor under the window — warm pink-gold
for y in range(FLOOR_Y, 320):
    t = (y - FLOOR_Y) / 152.0
    xl = 408 - t * 76
    xr = 520 + t * 36
    for x in range(int(xl), int(xr) + 1):
        bg.mix(x, y, (255, 226, 186, 255), 0.26 * (1.0 - t * 0.55))

# science shelf (x128..296, y40..164): books + glowing beakers
bg.rect(128, 40, 296, 164, FRAME)
bg.rect(136, 52, 288, 156, BEAMD)                         # dark back
bg.rect(136, 100, 288, 104, WOODL)                        # shelf board
bg.rect(136, 104, 288, 105, BEAMD)
bg.rect(128, 40, 296, 48, WOODL)                          # top board
SPINES = [(214, 74, 104, 255), (88, 116, 204, 255), (92, 168, 128, 255),
          (238, 172, 84, 255), (166, 96, 198, 255), (72, 162, 168, 255)]
x = 144                                                   # top row: books
k = 0
while x < 272:
    wsp = 12 + h2(x, 0, 14) % 10
    hsp = 30 + h2(x, 0, 15) % 12
    c = SPINES[k % len(SPINES)]
    bg.rect(x, 98 - hsp, x + wsp, 97, c)
    bg.rect(x, 98 - hsp, x + 1, 97,
            (max(0, c[0] - 40), max(0, c[1] - 40), max(0, c[2] - 40), 255))
    bg.rect(x, 98 - hsp, x + wsp, 99 - hsp,
            (min(255, c[0] + 30), min(255, c[1] + 30), min(255, c[2] + 30), 255))
    bg.rect(x + 3, 92 - hsp // 2, x + wsp - 3, 93 - hsp // 2, BEAMD)   # spine band
    x += wsp + 4
    k += 1
# bottom shelf: erlenmeyer (green) + round flask (purple)
for i in range(22):                                       # erlenmeyer, apex (176,112)
    y = 112 + i * 1.6
    half = 4 + i
    bg.rect(176 - half, int(y), 176 + half, int(y) + 1, (208, 224, 232, 255))
for i in range(10, 22):                                   # liquid in the bottom half
    y = 112 + i * 1.6
    half = 2 + i
    bg.rect(176 - half, int(y), 176 + half, int(y) + 1, GUNE)
bg.rect(170, 104, 182, 112, (208, 224, 232, 255))         # neck
bg.rect(172, 126, 173, 127, (222, 255, 226, 255))
bg.rect(178, 138, 179, 139, (222, 255, 226, 255))
bg.oval(244, 132, 16, 14, (208, 224, 232, 255))           # round flask
bg.oval(244, 136, 13, 10, GUNP)
bg.rect(238, 108, 250, 120, (208, 224, 232, 255))
bg.rect(240, 130, 241, 131, (230, 200, 250, 255))
bg.rect(248, 138, 249, 139, (230, 200, 250, 255))

# framed diploma (between shelf and window)
bg.rect(316, 44, 392, 112, FRAME)
bg.rect(316, 44, 392, 47, WOODL)
bg.rect(322, 52, 386, 104, (242, 236, 216, 255))
draw_text(bg.put, "PHD", 340, 60, (110, 88, 60, 255), 2)
bg.rect(366, 88, 374, 96, RED)                            # wax seal + ribbons
bg.rect(364, 97, 366, 99, RED)
bg.rect(374, 97, 376, 99, RED)

# doormat in front of the doorway
bg.rect(272, 300, 368, 332, BAG)
bg.rect(272, 300, 368, 302, BAGL)
bg.rect(272, 330, 368, 332, BAGD)
for x in range(280, 362, 12):
    bg.rect(x, 308, x + 4, 310, BAGD)
    bg.rect(x + 4, 322, x + 8, 324, BAGD)
bg.save("bedroom_bg.png")

# =================================================================================
# bed_basil.png — 4 frames of 112x160, top-down bed
#   0: asleep  1: asleep (breath)  2: bolt upright  3: empty messy bed
# =================================================================================
bd = Img(448, 160)


def sleeping_head(ox, hy):
    """Basil's head on the pillow: black dome, alert ears, narrow white blaze,
    goggles pushed up (he sleeps in them), sweet closed eyes."""
    hx = ox + 54
    for (ex, s) in ((-18, 1), (18, -1)):                  # ears
        for i in range(10):
            bd.rect(hx + ex - (4 - i // 2) * s, hy - 20 + i, hx + ex + (4 - i // 2) * s, hy - 20 + i,
                    FUR1 if s > 0 else FUR2)
        bd.rect(hx + ex - 1, hy - 16, hx + ex + 1, hy - 14, EARIN)
    bd.oval(hx, hy, 15, 13, FUR1)                         # dome
    for y in range(hy, hy + 12):                          # lower shade
        for x in range(hx - 14, hx + 16):
            if bd.get(x, y)[:3] == FUR1[:3] and (x // 2 + y // 2) % 2 == 0:
                bd.put(x, y, FUR2)
    bd.rect(hx - 2, hy - 8, hx + 2, hy + 4, WHT0)         # blaze
    bd.oval(hx, hy + 6, 6.8, 4.8, WHT0)                   # muzzle
    for ex in (hx - 10, hx + 6):                          # closed eyes ^ ^
        bd.put(ex, hy - 1, (168, 164, 176, 255))
        bd.put(ex + 1, hy - 2, (168, 164, 176, 255))
        bd.put(ex + 2, hy - 3, (168, 164, 176, 255))
        bd.put(ex + 3, hy - 2, (168, 164, 176, 255))
        bd.put(ex + 4, hy - 1, (168, 164, 176, 255))
    bd.rect(hx - 2, hy + 4, hx + 1, hy + 6, (160, 84, 104, 255))   # nose
    bd.rect(hx - 14, hy - 12, hx + 14, hy - 10, GOG)      # goggle strap
    bd.rect(hx - 4, hy - 16, hx + 2, hy - 14, LENS)       # lens catching light
    bd.rect(hx - 18, hy + 2, hx - 17, hy + 2, WHT3)       # whisker ticks
    bd.rect(hx + 17, hy + 2, hx + 18, hy + 2, WHT3)


def bed_base(ox):
    bd.rect(ox + 6, 8, ox + 104, 152, WOODD)              # frame
    bd.rect(ox + 10, 8, ox + 100, 28, FRAME)              # headboard
    bd.rect(ox + 10, 8, ox + 100, 10, WOODL)
    for px_ in range(ox + 26, ox + 100, 16):
        bd.rect(px_, 12, px_ + 1, 26, BEAM)
    bd.rect(ox + 10, 26, ox + 100, 28, BEAMD)
    bd.rect(ox + 12, 30, ox + 98, 142, SHEETD)            # mattress
    bd.rect(ox + 10, 140, ox + 100, 152, FRAME)           # footboard
    bd.rect(ox + 10, 140, ox + 100, 142, WOODL)
    bd.rect(ox + 10, 150, ox + 100, 152, BEAMD)
    for (px_, py_) in ((ox + 6, 8), (ox + 96, 8), (ox + 6, 144), (ox + 96, 144)):
        bd.rect(px_, py_, px_ + 8, py_ + 8, BEAM)         # posts
        bd.rect(px_, py_, px_ + 1, py_ + 1, WOODL)


def pillow(ox, dented=False):
    bd.rect(ox + 22, 34, ox + 88, 56, WHT0)
    bd.rect(ox + 22, 52, ox + 88, 56, WHT1)
    for (cx_, cy_) in ((ox + 22, 34), (ox + 88, 34), (ox + 22, 56), (ox + 88, 56)):
        bd.put(cx_, cy_, SHEETD)                          # soft corners
    bd.rect(ox + 22, 34, ox + 88, 35, WHT0)
    bd.rect(ox + 22, 55, ox + 88, 56, WHT3)
    if dented:
        bd.rect(ox + 40, 40, ox + 70, 43, WHT3)           # head dent
        bd.rect(ox + 44, 48, ox + 66, 49, WHT1)


def quilt(ox, y0, y1, ridge=True):
    bd.rect(ox + 12, y0, ox + 98, y1, QUILT)
    for y in range(y0, y1 + 1):                           # patch checker
        for x in range(ox + 12, ox + 100):
            if ((x - ox) // 16 + (y - y0) // 16) % 2 == 0 and h2(x // 2, y // 2, 16) < 200:
                bd.put(x, y, QUILTL)
    for fy in range(y0 + 24, y1 - 6, 24):                 # fold lines
        bd.rect(ox + 12, fy, ox + 98, fy + 1, QUILTD)
    bd.rect(ox + 12, y0, ox + 13, y1, QUILTD)
    bd.rect(ox + 97, y0, ox + 98, y1, QUILTD)
    bd.rect(ox + 12, y1 - 1, ox + 98, y1, QUILTD)
    if ridge:                                             # body under the covers
        for y in range(y0 + 4, y1 - 8):
            for x in range(ox + 42, ox + 70):
                if (x // 2 + y // 2) % 2 == 0:
                    bd.mix(x, y, (255, 200, 160, 255), 0.25)


# frames 0 & 1: asleep (breath = head nudge + sheet band shift)
for f, (hdy, band_dy) in enumerate(((0, 0), (2, 2))):
    ox = f * 112
    bed_base(ox)
    pillow(ox)
    quilt(ox, 60, 132)
    bd.rect(ox + 12, 60 + band_dy, ox + 98, 68 + band_dy, SHEET)   # folded sheet
    bd.rect(ox + 12, 68 + band_dy, ox + 98, 69 + band_dy, SHEETD)
    sleeping_head(ox, 44 + hdy)

# frame 2: bolt upright, wide eyes, coat on (he sleeps prepared)
ox = 224
bed_base(ox)
pillow(ox, dented=True)
quilt(ox, 100, 132, ridge=False)
bd.rect(ox + 12, 100, ox + 98, 106, SHEET)                # covers shoved down
bd.rect(ox + 12, 106, ox + 98, 107, SHEETD)
bd.rect(ox + 38, 64, ox + 70, 98, WHT1)                   # lab-coat torso
bd.rect(ox + 38, 64, ox + 66, 94, WHT0)
bd.rect(ox + 54, 68, ox + 55, 98, WHT3)                   # placket
bd.rect(ox + 24, 68, ox + 36, 80, WHT0)                   # arms thrown out
bd.rect(ox + 72, 68, ox + 84, 80, WHT1)
bd.oval(ox + 24, 74, 3.6, 3.6, WHT0)
bd.oval(ox + 84, 74, 3.6, 3.6, WHT0)
hx, hy = ox + 54, 44
for (ex, s) in ((-18, 1), (18, -1)):                      # tall alert ears
    for i in range(14):
        bd.rect(hx + ex - (4 - i // 3) * s, hy - 26 + i, hx + ex + (4 - i // 3) * s, hy - 26 + i,
                FUR1 if s > 0 else FUR2)
    bd.rect(hx + ex - 1, hy - 20, hx + ex + 1, hy - 18, EARIN)
bd.oval(hx, hy, 15, 13, FUR1)
bd.rect(hx - 2, hy - 8, hx + 2, hy + 4, WHT0)
bd.oval(hx, hy + 6, 6.8, 4.8, WHT0)
for ex in (hx - 12, hx + 4):                              # WIDE eyes
    bd.rect(ex, hy - 6, ex + 7, hy, EYE_Y)
    bd.rect(ex, hy - 6, ex + 7, hy - 5, EYE_YL)
    bd.rect(ex + 2, hy - 4, ex + 4, hy, PUPIL)
    bd.rect(ex + 2, hy - 4, ex + 3, hy - 3, GLINT)
bd.rect(hx - 2, hy + 6, hx + 2, hy + 10, (96, 54, 60, 255))   # gasp mouth
bd.rect(hx - 14, hy - 14, hx + 14, hy - 12, GOG)
bd.rect(hx - 4, hy - 18, hx + 2, hy - 16, LENS)
for (sx_, sy_) in ((hx - 24, hy - 28), (hx, hy - 34), (hx + 24, hy - 28)):
    bd.rect(sx_, sy_ - 2, sx_ + 1, sy_, EYE_YL)           # shock sparks

# frame 3: empty, blanket flung aside
ox = 336
bed_base(ox)
pillow(ox, dented=True)
for y in range(76, 142):                                  # blanket heap on the right
    xl = ox + 44 + int((y - 76) * 0.45) + (h2(0, y // 2, 17) % 3 - 1) * 2
    bd.rect(xl, y, ox + 106, y, QUILT)
    if (y - 76) % 14 == 0:
        bd.rect(xl + 4, y, ox + 102, y, QUILTD)
    bd.rect(xl, y, xl + 1, y, QUILTD)
for y in range(76, 92):                                   # flipped sheet corner
    bd.rect(ox + 80 + (y - 76), y, ox + 104, y, SHEET)
bd.rect(ox + 12, 132, ox + 40, 136, SHEET)                # trailing sheet tail

bd.save("bed_basil.png")

# =================================================================================
# bird.png — 3 frames of 48x48, faces LEFT: perched / chirp+note / flap
# =================================================================================
BLU, BLUD, BLUL = (86, 140, 214, 255), (58, 102, 170, 255), (130, 178, 236, 255)
CHEST = (232, 150, 70, 255)
BEAK = (240, 196, 60, 255)
bi = Img(144, 48)


def bird(ox, mode):
    up = 2 if mode == "chirp" else 0
    bi.oval(ox + 24, 28, 13, 10, BLU)                     # body
    bi.oval(ox + 18, 20 - up, 8.8, 8.0, BLU)              # head
    bi.oval(ox + 16, 24 - up, 5.2, 4.0, BLUL)             # cheek light
    bi.oval(ox + 22, 32, 7.2, 5.2, CHEST)                 # chest
    for i in range(8):                                    # tail (right, kicked up)
        bi.rect(ox + 34 + i, 22 - i, ox + 38 + i, 24 - i, BLUD)
    if mode == "flap":
        for i in range(10):                               # wings up
            bi.rect(ox + 20 + i, 8 + i, ox + 24 + i, 10 + i, BLUD)
            bi.rect(ox + 28 - i, 8 + i, ox + 30 - i, 10 + i, BLUL)
    else:
        bi.oval(ox + 28, 26, 6.4, 5.2, BLUD)              # folded wing
    bi.rect(ox + 13, 18 - up, ox + 14, 19 - up, PUPIL)    # eye
    bi.put(ox + 13, 16 - up, GLINT)
    if mode == "chirp":                                   # beak open + note
        bi.rect(ox + 6, 14, ox + 10, 16, BEAK)
        bi.rect(ox + 6, 20, ox + 10, 21, BEAK)
        bi.rect(ox + 36, 4, ox + 37, 12, CLKDARK)         # eighth note
        bi.oval(ox + 34, 14, 2.8, 2.4, CLKDARK)
        bi.rect(ox + 36, 4, ox + 41, 6, CLKDARK)
    else:
        bi.rect(ox + 6, 18 - up, ox + 10, 20 - up, BEAK)
    for lx in (ox + 20, ox + 28):                         # legs
        bi.rect(lx, 38, lx + 1, 43, (120, 90, 50, 255))
        bi.rect(lx - 2, 43, lx + 3, 43, (120, 90, 50, 255))


bird(0, "perch")
bird(48, "chirp")
bird(96, "flap")
bi.save("bird.png")

# =================================================================================
# nightstand.png (52x68) — little table, tiny alarm clock on top
# =================================================================================
ns = Img(52, 68)
ns.rect(0, 18, 51, 24, WOODL)                             # top board
ns.rect(0, 24, 51, 25, BEAMD)
ns.rect(4, 26, 47, 59, BEAM)                              # body
ns.rect(8, 30, 43, 43, FRAME)                             # drawer
ns.rect(8, 30, 43, 31, WOODL)
ns.rect(24, 34, 27, 37, KNOB)
ns.rect(8, 48, 43, 49, BEAMD)                             # lower panel line
ns.rect(4, 60, 11, 67, BEAMD)                             # legs
ns.rect(40, 60, 47, 67, BEAMD)
# tiny clock on top
ns.rect(18, 2, 21, 3, KNOB)                               # bells
ns.rect(20, 0, 21, 1, KNOB)
ns.rect(30, 2, 33, 3, KNOB)
ns.rect(30, 0, 31, 1, KNOB)
ns.oval(25, 10, 8.8, 8.4, STL2)
ns.oval(25, 10, 6.0, 5.6, CLKFACE)
ns.rect(24, 8, 25, 9, CLKDARK)                            # hands
ns.rect(26, 10, 27, 11, CLKDARK)
ns.rect(20, 18, 23, 20, STL3)                             # feet
ns.rect(28, 18, 31, 20, STL3)
ns.save("nightstand.png")

# =================================================================================
# clock_face.png (192x208) — the close-up: 8:57, alarm hand stuck at 8
# =================================================================================
ck = Img(192, 208)
CX, CY = 96, 120
for (bx, flip) in ((54, 1), (138, -1)):                   # brass bells
    ck.oval(bx, 26, 22, 20, KNOB)
    ck.oval(bx - 6 * flip, 20, 10, 8, (232, 206, 130, 255))
    ck.ring(bx, 26, 19.2, 22, (160, 128, 60, 255))
ck.rect(92, 4, 99, 16, STL2)                              # striker
ck.oval(95.5, 4, 4.8, 4.0, STL1)
ck.rect(52, 192, 68, 204, STL3)                           # feet
ck.rect(124, 192, 140, 204, STL3)
ck.rect(48, 202, 72, 205, STL3)
ck.rect(120, 202, 144, 205, STL3)
ck.oval(CX, CY, 80, 80, STL2)                             # steel body
ck.ring(CX, CY, 72, 80, STL1)
for a in range(200, 260):                                 # rim highlight upper-left
    x = CX + 76 * math.cos(math.radians(a))
    y = CY + 76 * math.sin(math.radians(a))
    ck.rect(x, y, x + 2, y + 1, STL0)
ck.oval(CX, CY, 66, 66, CLKFACE)
for y in range(CY, CY + 66):                              # face shading lower-right
    for x in range(CX, CX + 66):
        if math.hypot(x - CX, y - CY) <= 66 and (x // 2 + y // 2) % 2 == 0:
            ck.put(x, y, CLKFACED)
for i in range(12):                                       # hour ticks
    a = math.radians(i * 30)
    x0 = CX + 58 * math.sin(a); y0 = CY - 58 * math.cos(a)
    x1 = CX + 64 * math.sin(a); y1 = CY - 64 * math.cos(a)
    ck.line(x0, y0, x1, y1, CLKDARK, 2)
draw_text(ck.put, "12", CX - 11, 52, CLKDARK, 2)
draw_text(ck.put, "3", CX + 46, CY - 6, CLKDARK, 2)
draw_text(ck.put, "6", CX - 5, CY + 50, CLKDARK, 2)
draw_text(ck.put, "9", CX - 54, CY - 6, CLKDARK, 2)
# alarm hand: still pointing at 8 -- it never rang
a = math.radians(8 * 30)
ck.line(CX, CY, CX + 40 * math.sin(a), CY - 40 * math.cos(a), RED, 2)
ck.oval(CX + 44 * math.sin(a), CY - 44 * math.cos(a), 3.2, 3.2, RED)
# hour hand ~ 8:57 (just shy of 9)
a = math.radians(8.95 * 30)
ck.line(CX, CY, CX + 34 * math.sin(a), CY - 34 * math.cos(a), CLKDARK, 4)
# minute hand at 57
a = math.radians(57 * 6)
ck.line(CX, CY, CX + 54 * math.sin(a), CY - 54 * math.cos(a), CLKDARK, 2)
ck.line(CX, CY, CX + 28 * math.sin(a), CY - 28 * math.cos(a), CLKDARK, 4)
ck.oval(CX, CY, 4.8, 4.8, CLKDARK)                        # hub
ck.save("clock_face.png")
