#!/usr/bin/env python3
"""Props for the bedroom wake-up scene (intro part 2), drawn for the 640x360 stage
in the same cottage palette as _gen_intro_art.py. Writes PNGs into assets/props/.
Re-run: python3 assets/_gen_bedroom_art.py

  bedroom_bg.png   640x360  Chrono Trigger-style compact room floating on black:
                            timbered wall, window (bird perch ~(418,94)), science
                            shelf, rug, doorway gap + doormat at the bottom
  bed_basil.png    224x80   4 frames (56x80): asleep A / asleep B / bolt upright /
                            empty messy bed
  bird.png         72x24    3 frames (24x24, faces LEFT): perched / chirp+note / flap
  nightstand.png   26x34    little table with a tiny alarm clock on top
  clock_face.png   96x104   close-up alarm clock frozen at 8:57 (alarm hand at 8)
"""
import struct, zlib, os, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _pixfont import draw_text, text_width

OUTDIR = os.path.join(HERE, "props")
os.makedirs(OUTDIR, exist_ok=True)


class Img:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 4)

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (int(y) * self.w + int(x)) * 4
            self.buf[o:o + 4] = bytes(c)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (int(y) * self.w + int(x)) * 4
            return tuple(self.buf[o:o + 4])
        return (0, 0, 0, 0)

    def mix(self, x, y, c, a):
        """Blend c over the existing pixel (only where something is drawn)."""
        e = self.get(x, y)
        if e[3] == 0:
            return
        self.put(x, y, (int(e[0] * (1 - a) + c[0] * a),
                        int(e[1] * (1 - a) + c[1] * a),
                        int(e[2] * (1 - a) + c[2] * a), 255))

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.put(x, y, c)

    def oval(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 2):
            for x in range(int(cx - rx), int(cx + rx) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.put(x, y, c)

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
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * self.w * 4:(y + 1) * self.w * 4]

        def ch(t, d):
            c = t + d
            return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        open(os.path.join(OUTDIR, name), "wb").write(
            b"\x89PNG\r\n\x1a\n"
            + ch(b"IHDR", struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0))
            + ch(b"IDAT", zlib.compress(bytes(raw), 9)) + ch(b"IEND", b""))
        print("wrote", name, f"({self.w}x{self.h})")


def h2(x, y, salt=0):
    n = (x * 374761393 + y * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return (n ^ (n >> 16)) & 0xFF


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
# Basil (from _gen_basil_sprites.py ramps)
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
# bedroom_bg.png (640x360) — Chrono Trigger-style: a compact room floating on a
# black void. Room interior (160,44)-(479,315) inside a timber frame; wall band
# down to y=115, plank floor below, doorway gap at bottom-center (Basil exits
# south over the doormat). Bird perch: sill top y=101, sprite center ~(418,94).
# =================================================================================
BW, BH = 640, 360
RX0, RY0, RX1, RY1 = 160, 44, 479, 315                   # room interior
FLOOR_Y = 116                                            # wall/floor split
DOOR_X0, DOOR_X1 = 296, 344                              # gap in the bottom frame
bg = Img(BW, BH)

# deep-indigo void + timber frame around the room
bg.rect(0, 0, BW - 1, BH - 1, (12, 8, 24, 255))
bg.rect(RX0 - 6, RY0 - 6, RX1 + 6, RY1 + 6, BEAMD)
bg.rect(RX0 - 4, RY0 - 4, RX1 + 4, RY1 + 4, BEAM)
bg.rect(RX0 - 4, RY0 - 4, RX1 + 4, RY0 - 4, WOODL)       # top edge catch-light

# plaster wall band with noise
bg.rect(RX0, RY0, RX1, FLOOR_Y - 1, PLAS)
for y in range(RY0, FLOOR_Y):
    for x in range(RX0, RX1 + 1):
        r = h2(x, y, 11)
        if r < 12:
            bg.put(x, y, PLASD)
        elif r > 246:
            bg.put(x, y, PLASL)
bg.rect(RX0, RY0, RX1, RY0 + 4, BEAMD)                   # ceiling shadow line
for y in range(RY0 + 5, RY0 + 12):                       # violet shadow falloff
    for x in range(RX0, RX1 + 1):
        if (x + y) % 2 == 0 or y < RY0 + 8:
            bg.mix(x, y, (146, 126, 182, 255), 0.45)
# timber verticals (clear of window 380..440 and shelf 180..262)
for bx in (166, 272, 350, 458):
    bg.rect(bx, RY0 + 4, bx + 3, FLOOR_Y - 1, BEAM)
    bg.rect(bx + 3, RY0 + 4, bx + 3, FLOOR_Y - 1, BEAMD)
# baseboard
bg.rect(RX0, FLOOR_Y - 9, RX1, FLOOR_Y - 3, BEAM)
bg.rect(RX0, FLOOR_Y - 3, RX1, FLOOR_Y - 1, BEAMD)

# plank floor (horizontal boards, staggered joints)
bg.rect(RX0, FLOOR_Y, RX1, RY1, WOOD)
bg.rect(DOOR_X0, RY1, DOOR_X1, RY1 + 6, WOOD)            # floor tongue out the door
for y in range(FLOOR_Y, RY1 + 7):
    for x in range(RX0, RX1 + 1):
        if y > RY1 and not (DOOR_X0 <= x <= DOOR_X1):
            continue
        r = h2(x, y, 12)
        if r < 9:
            bg.put(x, y, WOODD)
        elif r > 249:
            bg.put(x, y, WOODL)
for y in range(FLOOR_Y + 15, RY1, 16):
    bg.rect(RX0, y, RX1, y, WOODD)
    off = 32 if ((y - FLOOR_Y) // 16) % 2 else 0
    for jx in range(RX0 + off, RX1, 64):
        bg.rect(jx, y - 15, jx, y - 1, WOODD)
bg.rect(RX0, FLOOR_Y, RX1, FLOOR_Y + 1, WOODD)           # wall contact shadow
bg.rect(DOOR_X0 - 1, RY1 - 2, DOOR_X0 - 1, RY1 + 6, BEAMD)   # door jambs
bg.rect(DOOR_X1 + 1, RY1 - 2, DOOR_X1 + 1, RY1 + 6, BEAMD)

# round rug, center-right of the room (bed sits at x~220) — saturated teal
RUG, RUGD, RUGL = (62, 142, 140, 255), (38, 108, 112, 255), (98, 176, 162, 255)
for y in range(FLOOR_Y, RY1 + 1):
    for x in range(RX0, RX1 + 1):
        d = ((x - 348) / 68.0) ** 2 + ((y - 220) / 30.0) ** 2
        if d <= 1.0:
            c = RUG
            if d > 0.82:
                c = RUGD
            elif d < 0.5 and h2(x, y, 13) < 26:
                c = RUGL
            bg.put(x, y, c)

# window (frame 380..440 x 50..104), Paper Girls dawn: indigo -> magenta -> gold,
# posterize-dithered like the title sky, low sun burning through
bg.rect(380, 50, 440, 104, FRAME)
bg.rect(380, 50, 440, 52, BEAMD)
DAWN = [(0.0, (96, 66, 148)), (0.55, (216, 106, 150)), (1.0, (252, 200, 122))]
for y in range(55, 100):
    t = (y - 55) / 44.0
    for si in range(len(DAWN) - 1):
        t0, c0 = DAWN[si]
        t1, c1 = DAWN[si + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0)
            base = tuple(int(c0[i] + (c1[i] - c0[i]) * f) for i in range(3))
            break
    for x in range(385, 436):
        q = tuple(min(255, (ch // 16) * 16 + (8 if (x + y) % 2 else 0)) for ch in base)
        bg.put(x, y, q + (255,))
for y in range(55, 100):                                 # low sun glow
    for x in range(385, 436):
        d = math.hypot(x - 397, y - 88)
        if d < 11:
            bg.put(x, y, (255, 240, 190, 255))
        elif d < 15:
            bg.mix(x, y, (255, 226, 170, 255), 0.5)
bg.rect(409, 55, 411, 99, FRAME)                         # mullions
bg.rect(385, 76, 435, 77, FRAME)
bg.rect(374, 100, 446, 105, PLASL)                       # sill (bird perch ~(418,94))
bg.rect(374, 105, 446, 107, PLASD)
# a little basil plant on the sill (of course he grows basil)
bg.rect(380, 93, 390, 100, (170, 96, 60, 255))
bg.rect(380, 93, 390, 94, (196, 118, 76, 255))
for (lx, ly) in ((382, 87), (386, 84), (389, 88), (384, 90), (388, 91)):
    bg.oval(lx, ly, 2.4, 1.8, (86, 150, 74, 255))
    bg.put(lx, ly - 1, (120, 190, 96, 255))

# pool of morning light on the floor under the window — warm pink-gold
for y in range(FLOOR_Y, 206):
    t = (y - FLOOR_Y) / 90.0
    xl = 385 - t * 38
    xr = 440 + t * 18
    for x in range(int(xl), int(xr) + 1):
        bg.mix(x, y, (255, 226, 186, 255), 0.26 * (1.0 - t * 0.55))

# science shelf (x180..262, y54..114): books + glowing beakers
bg.rect(180, 54, 262, 114, FRAME)
bg.rect(184, 60, 258, 110, BEAMD)                        # dark back
for sy in (84,):                                         # shelf board
    bg.rect(184, sy, 258, sy + 2, WOODL)
    bg.rect(184, sy + 2, 258, sy + 2, BEAMD)
bg.rect(180, 54, 262, 58, WOODL)                         # top board
SPINES = [(214, 74, 104, 255), (88, 116, 204, 255), (92, 168, 128, 255),
          (238, 172, 84, 255), (166, 96, 198, 255), (72, 162, 168, 255)]
x = 188                                                  # top row: books
k = 0
while x < 250:
    wsp = 6 + h2(x, 0, 14) % 5
    hsp = 15 + h2(x, 0, 15) % 6
    c = SPINES[k % len(SPINES)]
    bg.rect(x, 83 - hsp, x + wsp, 82, c)
    bg.rect(x, 83 - hsp, x, 82,
            (max(0, c[0] - 40), max(0, c[1] - 40), max(0, c[2] - 40), 255))
    bg.rect(x, 85 - hsp, x + wsp, 85 - hsp,
            (min(255, c[0] + 30), min(255, c[1] + 30), min(255, c[2] + 30), 255))
    x += wsp + 2
    k += 1
# bottom shelf: erlenmeyer (green) + round flask (purple)
for i in range(11):                                      # erlenmeyer, apex (204,90)
    y = 90 + i * 1.6
    half = 2 + i
    bg.rect(204 - half, int(y), 204 + half, int(y) + 1, (208, 224, 232, 255))
for i in range(5, 11):                                   # liquid in the bottom half
    y = 90 + i * 1.6
    half = 1 + i
    bg.rect(204 - half, int(y), 204 + half, int(y) + 1, GUNE)
bg.rect(201, 86, 207, 90, (208, 224, 232, 255))          # neck
bg.put(202, 97, (222, 255, 226, 255)); bg.put(205, 103, (222, 255, 226, 255))
bg.oval(238, 100, 8, 7, (208, 224, 232, 255))            # round flask
bg.oval(238, 102, 6.5, 5, GUNP)
bg.rect(235, 88, 241, 94, (208, 224, 232, 255))
bg.put(236, 99, (230, 200, 250, 255)); bg.put(240, 103, (230, 200, 250, 255))

# framed diploma (between shelf and window)
bg.rect(298, 58, 344, 94, FRAME)
bg.rect(298, 58, 344, 60, WOODL)
bg.rect(302, 63, 340, 89, (242, 236, 216, 255))
draw_text(bg.put, "PHD", 313, 67, (110, 88, 60, 255))
bg.rect(328, 80, 332, 84, RED)                           # wax seal + ribbons
bg.put(327, 85, RED); bg.put(333, 85, RED)

# doormat in front of the doorway
bg.rect(294, 288, 346, 310, BAG)
bg.rect(294, 288, 346, 289, BAGL)
bg.rect(294, 309, 346, 310, BAGD)
for x in range(298, 343, 6):
    bg.rect(x, 292, x + 2, 293, BAGD)
    bg.rect(x + 2, 305, x + 4, 306, BAGD)
bg.save("bedroom_bg.png")

# =================================================================================
# bed_basil.png — 4 frames of 56x80, top-down bed
#   0: asleep  1: asleep (breath)  2: bolt upright  3: empty messy bed
# =================================================================================
bd = Img(224, 80)


def sleeping_head(ox, hy):
    """Basil's head on the pillow: black dome, alert ears, narrow white blaze,
    goggles pushed up (he sleeps in them), sweet closed eyes."""
    hx = ox + 27
    for (ex, s) in ((-9, 1), (9, -1)):                   # ears
        for i in range(5):
            bd.rect(hx + ex - (2 - i // 2) * s, hy - 10 + i, hx + ex + (2 - i // 2) * s, hy - 10 + i,
                    FUR1 if s > 0 else FUR2)
        bd.put(hx + ex, hy - 8, EARIN)
    bd.oval(hx, hy, 7.5, 6.5, FUR1)                      # dome
    for y in range(hy, hy + 6):                          # lower shade
        for x in range(hx - 7, hx + 8):
            if bd.get(x, y)[:3] == FUR1[:3] and (x + y) % 2 == 0:
                bd.put(x, y, FUR2)
    bd.rect(hx - 1, hy - 4, hx + 1, hy + 2, WHT0)        # blaze
    bd.oval(hx, hy + 3, 3.4, 2.4, WHT0)                  # muzzle
    for (ex, flip) in ((hx - 5, 0), (hx + 3, 0)):        # closed eyes ^ ^
        bd.put(ex, hy - 1, (168, 164, 176, 255))
        bd.put(ex + 1, hy - 2, (168, 164, 176, 255))
        bd.put(ex + 2, hy - 1, (168, 164, 176, 255))
    bd.rect(hx - 1, hy + 2, hx, hy + 3, (160, 84, 104, 255))   # nose
    bd.rect(hx - 7, hy - 6, hx + 7, hy - 5, GOG)         # goggle strap
    bd.rect(hx - 2, hy - 8, hx + 1, hy - 7, LENS)        # lens catching light
    bd.put(hx - 9, hy + 1, WHT3); bd.put(hx + 9, hy + 1, WHT3)  # whisker ticks


def bed_base(ox):
    bd.rect(ox + 3, 4, ox + 52, 76, WOODD)               # frame
    bd.rect(ox + 5, 4, ox + 50, 14, FRAME)               # headboard
    bd.rect(ox + 5, 4, ox + 50, 5, WOODL)
    for px_ in range(ox + 13, ox + 50, 8):
        bd.rect(px_, 6, px_, 13, BEAM)
    bd.rect(ox + 5, 13, ox + 50, 14, BEAMD)
    bd.rect(ox + 6, 15, ox + 49, 71, SHEETD)             # mattress
    bd.rect(ox + 5, 70, ox + 50, 76, FRAME)              # footboard
    bd.rect(ox + 5, 70, ox + 50, 71, WOODL)
    bd.rect(ox + 5, 75, ox + 50, 76, BEAMD)
    for (px_, py_) in ((ox + 3, 4), (ox + 48, 4), (ox + 3, 72), (ox + 48, 72)):
        bd.rect(px_, py_, px_ + 4, py_ + 4, BEAM)        # posts
        bd.put(px_, py_, WOODL)


def pillow(ox, dented=False):
    bd.rect(ox + 11, 17, ox + 44, 28, WHT0)
    bd.rect(ox + 11, 26, ox + 44, 28, WHT1)
    for (cx_, cy_) in ((ox + 11, 17), (ox + 44, 17), (ox + 11, 28), (ox + 44, 28)):
        bd.put(cx_, cy_, SHEETD)                         # soft corners
    bd.rect(ox + 11, 17, ox + 44, 17, WHT0)
    bd.rect(ox + 11, 28, ox + 44, 28, WHT3)
    if dented:
        bd.rect(ox + 20, 20, ox + 35, 21, WHT3)          # head dent
        bd.rect(ox + 22, 24, ox + 33, 24, WHT1)


def quilt(ox, y0, y1, ridge=True):
    bd.rect(ox + 6, y0, ox + 49, y1, QUILT)
    for y in range(y0, y1 + 1):                          # patch checker
        for x in range(ox + 6, ox + 50):
            if ((x - ox) // 8 + (y - y0) // 8) % 2 == 0 and h2(x, y, 16) < 200:
                bd.put(x, y, QUILTL)
    for fy in range(y0 + 12, y1 - 3, 12):                # fold lines
        bd.rect(ox + 6, fy, ox + 49, fy, QUILTD)
    bd.rect(ox + 6, y0, ox + 6, y1, QUILTD)
    bd.rect(ox + 49, y0, ox + 49, y1, QUILTD)
    bd.rect(ox + 6, y1, ox + 49, y1, QUILTD)
    if ridge:                                            # body under the covers
        for y in range(y0 + 2, y1 - 4):
            for x in range(ox + 21, ox + 35):
                if (x + y) % 2 == 0:
                    bd.mix(x, y, (255, 200, 160, 255), 0.25)


# frames 0 & 1: asleep (breath = head nudge + sheet band shift)
for f, (hdy, band_dy) in enumerate(((0, 0), (1, 1))):
    ox = f * 56
    bed_base(ox)
    pillow(ox)
    quilt(ox, 30, 66)
    bd.rect(ox + 6, 30 + band_dy, ox + 49, 34 + band_dy, SHEET)   # folded sheet
    bd.rect(ox + 6, 34 + band_dy, ox + 49, 34 + band_dy, SHEETD)
    sleeping_head(ox, 22 + hdy)

# frame 2: bolt upright, wide eyes, coat on (he sleeps prepared)
ox = 112
bed_base(ox)
pillow(ox, dented=True)
quilt(ox, 50, 66, ridge=False)
bd.rect(ox + 6, 50, ox + 49, 53, SHEET)                  # covers shoved down
bd.rect(ox + 6, 53, ox + 49, 53, SHEETD)
bd.rect(ox + 19, 32, ox + 35, 49, WHT1)                  # lab-coat torso
bd.rect(ox + 19, 32, ox + 33, 47, WHT0)
bd.rect(ox + 27, 34, ox + 27, 49, WHT3)                  # placket
bd.rect(ox + 12, 34, ox + 18, 40, WHT0)                  # arms thrown out
bd.rect(ox + 36, 34, ox + 42, 40, WHT1)
bd.oval(ox + 12, 37, 1.8, 1.8, WHT0)
bd.oval(ox + 42, 37, 1.8, 1.8, WHT0)
hx, hy = ox + 27, 22
for (ex, s) in ((-9, 1), (9, -1)):                       # tall alert ears
    for i in range(7):
        bd.rect(hx + ex - (2 - i // 3) * s, hy - 13 + i, hx + ex + (2 - i // 3) * s, hy - 13 + i,
                FUR1 if s > 0 else FUR2)
    bd.put(hx + ex, hy - 10, EARIN)
bd.oval(hx, hy, 7.5, 6.5, FUR1)
bd.rect(hx - 1, hy - 4, hx + 1, hy + 2, WHT0)
bd.oval(hx, hy + 3, 3.4, 2.4, WHT0)
for ex in (hx - 6, hx + 2):                              # WIDE eyes
    bd.rect(ex, hy - 3, ex + 3, hy, EYE_Y)
    bd.rect(ex, hy - 3, ex + 3, hy - 3, EYE_YL)
    bd.rect(ex + 1, hy - 2, ex + 2, hy, PUPIL)
    bd.put(ex + 1, hy - 2, GLINT)
bd.rect(hx - 1, hy + 3, hx + 1, hy + 5, (96, 54, 60, 255))   # gasp mouth
bd.rect(hx - 7, hy - 7, hx + 7, hy - 6, GOG)
bd.rect(hx - 2, hy - 9, hx + 1, hy - 8, LENS)
for (sx_, sy_) in ((hx - 12, hy - 14), (hx, hy - 17), (hx + 12, hy - 14)):
    bd.put(sx_, sy_, EYE_YL)                             # shock sparks
    bd.put(sx_, sy_ - 1, EYE_YL)

# frame 3: empty, blanket flung aside
ox = 168
bed_base(ox)
pillow(ox, dented=True)
for y in range(38, 71):                                  # blanket heap on the right
    xl = ox + 22 + int((y - 38) * 0.45) + (h2(0, y, 17) % 3 - 1)
    bd.rect(xl, y, ox + 53, y, QUILT)
    if (y - 38) % 7 == 0:
        bd.rect(xl + 2, y, ox + 51, y, QUILTD)
    bd.put(xl, y, QUILTD)
for y in range(38, 46):                                  # flipped sheet corner
    bd.rect(ox + 40 + (y - 38), y, ox + 52, y, SHEET)
bd.rect(ox + 6, 66, ox + 20, 68, SHEET)                  # trailing sheet tail

bd.save("bed_basil.png")

# =================================================================================
# bird.png — 3 frames of 24x24, faces LEFT: perched / chirp+note / flap
# =================================================================================
BLU, BLUD, BLUL = (86, 140, 214, 255), (58, 102, 170, 255), (130, 178, 236, 255)
CHEST = (232, 150, 70, 255)
BEAK = (240, 196, 60, 255)
bi = Img(72, 24)


def bird(ox, mode):
    up = 1 if mode == "chirp" else 0
    bi.oval(ox + 12, 14, 6.5, 5.0, BLU)                  # body
    bi.oval(ox + 9, 10 - up, 4.4, 4.0, BLU)              # head
    bi.oval(ox + 8, 12 - up, 2.6, 2.0, BLUL)             # cheek light
    bi.oval(ox + 11, 16, 3.6, 2.6, CHEST)                # chest
    for i in range(4):                                   # tail (right, kicked up)
        bi.rect(ox + 17 + i, 11 - i, ox + 19 + i, 12 - i, BLUD)
    if mode == "flap":
        for i in range(5):                               # wings up
            bi.rect(ox + 10 + i, 4 + i, ox + 12 + i, 5 + i, BLUD)
            bi.rect(ox + 14 - i, 4 + i, ox + 15 - i, 5 + i, BLUL)
    else:
        bi.oval(ox + 14, 13, 3.2, 2.6, BLUD)             # folded wing
    bi.put(ox + 7, 9 - up, PUPIL)                        # eye
    bi.put(ox + 7, 8 - up, GLINT)
    if mode == "chirp":                                  # beak open + note
        bi.rect(ox + 3, 7, ox + 5, 8, BEAK)
        bi.rect(ox + 3, 10, ox + 5, 10, BEAK)
        bi.rect(ox + 18, 2, ox + 18, 6, CLKDARK)         # eighth note
        bi.oval(ox + 17, 7, 1.4, 1.2, CLKDARK)
        bi.rect(ox + 18, 2, ox + 20, 3, CLKDARK)
    else:
        bi.rect(ox + 3, 9 - up, ox + 5, 10 - up, BEAK)
    for lx in (ox + 10, ox + 14):                        # legs
        bi.rect(lx, 19, lx, 21, (120, 90, 50, 255))
        bi.rect(lx - 1, 21, lx + 1, 21, (120, 90, 50, 255))


bird(0, "perch")
bird(24, "chirp")
bird(48, "flap")
bi.save("bird.png")

# =================================================================================
# nightstand.png (26x34) — little table, tiny alarm clock on top
# =================================================================================
ns = Img(26, 34)
ns.rect(0, 9, 25, 12, WOODL)                             # top board
ns.rect(0, 12, 25, 12, BEAMD)
ns.rect(2, 13, 23, 29, BEAM)                             # body
ns.rect(4, 15, 21, 21, FRAME)                            # drawer
ns.rect(4, 15, 21, 15, WOODL)
ns.rect(12, 17, 13, 18, KNOB)
ns.rect(4, 24, 21, 24, BEAMD)                            # lower panel line
ns.rect(2, 30, 5, 33, BEAMD)                             # legs
ns.rect(20, 30, 23, 33, BEAMD)
# tiny clock on top
ns.put(9, 1, KNOB); ns.put(10, 0, KNOB)                  # bells
ns.put(16, 1, KNOB); ns.put(15, 0, KNOB)
ns.oval(12.5, 5, 4.4, 4.2, STL2)
ns.oval(12.5, 5, 3.0, 2.8, CLKFACE)
ns.put(12, 4, CLKDARK); ns.put(13, 5, CLKDARK)           # hands
ns.rect(10, 9, 11, 10, STL3); ns.rect(14, 9, 15, 10, STL3)   # feet
ns.save("nightstand.png")

# =================================================================================
# clock_face.png (96x104) — the close-up: 8:57, alarm hand stuck at 8
# =================================================================================
ck = Img(96, 104)
CX, CY = 48, 60
for (bx, flip) in ((27, 1), (69, -1)):                   # brass bells
    ck.oval(bx, 13, 11, 10, KNOB)
    ck.oval(bx - 3 * flip, 10, 5, 4, (232, 206, 130, 255))
    ck.ring(bx, 13, 9.6, 11, (160, 128, 60, 255))
ck.rect(46, 2, 49, 8, STL2)                              # striker
ck.oval(47.5, 2, 2.4, 2.0, STL1)
ck.rect(26, 96, 34, 102, STL3)                           # feet
ck.rect(62, 96, 70, 102, STL3)
ck.rect(24, 101, 36, 102, STL3)
ck.rect(60, 101, 72, 102, STL3)
ck.oval(CX, CY, 40, 40, STL2)                            # steel body
ck.ring(CX, CY, 36, 40, STL1)
for a in range(200, 260):                                # rim highlight upper-left
    x = CX + 38 * math.cos(math.radians(a))
    y = CY + 38 * math.sin(math.radians(a))
    ck.put(x, y, STL0); ck.put(x + 1, y, STL0)
ck.oval(CX, CY, 33, 33, CLKFACE)
for y in range(CY, CY + 33):                             # face shading lower-right
    for x in range(CX, CX + 33):
        if math.hypot(x - CX, y - CY) <= 33 and (x + y) % 2 == 0:
            ck.put(x, y, CLKFACED)
for i in range(12):                                      # hour ticks
    a = math.radians(i * 30)
    x0 = CX + 29 * math.sin(a); y0 = CY - 29 * math.cos(a)
    x1 = CX + 32 * math.sin(a); y1 = CY - 32 * math.cos(a)
    ck.line(x0, y0, x1, y1, CLKDARK)
draw_text(ck.put, "12", CX - 5, 25, CLKDARK)
draw_text(ck.put, "3", CX + 24, CY - 3, CLKDARK)
draw_text(ck.put, "6", CX - 2, CY + 26, CLKDARK)
draw_text(ck.put, "9", CX - 28, CY - 3, CLKDARK)
# alarm hand: still pointing at 8 -- it never rang
a = math.radians(8 * 30)
ck.line(CX, CY, CX + 20 * math.sin(a), CY - 20 * math.cos(a), RED)
ck.oval(CX + 22 * math.sin(a), CY - 22 * math.cos(a), 1.6, 1.6, RED)
# hour hand ~ 8:57 (just shy of 9)
a = math.radians(8.95 * 30)
ck.line(CX, CY, CX + 17 * math.sin(a), CY - 17 * math.cos(a), CLKDARK, 2)
# minute hand at 57
a = math.radians(57 * 6)
ck.line(CX, CY, CX + 27 * math.sin(a), CY - 27 * math.cos(a), CLKDARK)
ck.line(CX, CY, CX + 14 * math.sin(a), CY - 14 * math.cos(a), CLKDARK, 2)
ck.oval(CX, CY, 2.4, 2.4, CLKDARK)                       # hub
ck.save("clock_face.png")
