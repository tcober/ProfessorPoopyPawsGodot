#!/usr/bin/env python3
"""Props for the opening sequence, drawn for the 640x360 stage (2x the original
scale, with detail at the finer grain — mullioned windows, plank grain, stone
courses, readable chalk writing). Writes PNGs into assets/props/.
Re-run: python3 assets/_gen_intro_art.py

  house_front.png    384x128  Basil's cottage
  school_front.png   448x160  the Academy
  poop_bag.png       96x32    3 frames (32x32): bag+stink A / B / squished
  paw_print.png      12x12    one brown print
  hall_floor.png     32x32    plank floor tile
  hall_wall.png      32x32    panelled wall tile
  chalkboard.png     224x72   framed board, readable chalk notes
  podium.png         52x60    wooden lectern
  audience_cats.png  160x40   4 back-of-head cats
"""
import struct, zlib, os, sys

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
            o = (y * self.w + x) * 4
            self.buf[o:o + 4] = bytes(c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

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


def lerp3(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


# ---- Basil's cottage front (384x128) -------------------------------------------
# Paper Girls color script: sun-warmed peach plaster whose shadows hue-shift
# violet, deep plum timber, hot magenta shingles, sunset-gradient glass. The
# render is FF/CT: eave shadow band, lit shingle courses, stone footing, flower
# boxes, door lanterns. Geometry (door/window spots) is unchanged for the scenes.
PLAS   = (238, 214, 196, 255)
PLASD  = (210, 178, 180, 255)    # violet-shifted shade
PLASL  = (250, 232, 210, 255)
PLASS  = (178, 140, 158, 255)    # deep eave shadow
BEAM   = (104, 60, 78, 255)
BEAMD  = (72, 40, 58, 255)
BEAML  = (138, 88, 98, 255)
ROOF   = (214, 82, 112, 255)
ROOFD  = (166, 50, 94, 255)
ROOFL  = (242, 124, 124, 255)
ROOFS  = (118, 34, 76, 255)      # course seams / drip edge
DOORC  = (38, 30, 62, 255)       # midnight-indigo door
DOORP  = (56, 44, 88, 255)
DOORL  = (84, 68, 118, 255)
FRAME  = (124, 76, 84, 255)
GLASS_TOP = (250, 216, 146)      # sunset caught in the panes
GLASS_MID = (234, 142, 148)
GLASS_BOT = (112, 98, 162)
KNOB   = (246, 198, 96, 255)
STONEF  = (168, 150, 178, 255)   # lavender foundation stones
STONEFD = (132, 112, 146, 255)
STONEFL = (196, 178, 200, 255)
FLW_PNK = (255, 106, 168, 255)
FLW_GLD = (255, 208, 92, 255)
LEAFY   = (74, 152, 118, 255)
LEAFYD  = (48, 116, 98, 255)

hw, hh = 384, 128
h = Img(hw, hh)

# plaster field with noise
h.rect(0, 20, hw - 1, hh - 1, PLAS)
for y in range(20, hh):
    for x in range(hw):
        r = h2(x, y, 1)
        if r < 12:
            h.put(x, y, PLASD)
        elif r > 246:
            h.put(x, y, PLASL)
# the roof hangs over the wall: violet eave shadow, dithered out
for y in range(22, 34):
    t = (y - 22) / 12.0
    for x in range(hw):
        if t < 0.5:
            h.put(x, y, PLASS)
        elif t < 0.85 and (x + y) % 2 == 0:
            h.put(x, y, PLASD)
# stone footing: coursed blocks with staggered joints
for y in range(hh - 10, hh):
    for x in range(hw):
        c = STONEF
        r = h2(x // 3, y // 3, 21)
        if r > 240:
            c = STONEFL
        elif r < 16:
            c = STONEFD
        h.put(x, y, c)
for yy in (hh - 10, hh - 5):
    h.rect(0, yy, hw - 1, yy, STONEFD)
for row, yy in enumerate((hh - 9, hh - 4)):
    for jx in range(14 * (row % 2) // 2 + 9, hw, 28):
        h.rect(jx + row * 14, yy, jx + row * 14, yy + 3, STONEFD)
h.rect(0, hh - 11, hw - 1, hh - 11, PLASD)               # settle line above stones

# shingled roof: magenta courses, lit crest per row, deep seams
for y in range(0, 20):
    row = y // 5
    for x in range(hw):
        ph = (x // 12 + row) % 2
        c = ROOF if ph else ROOFD
        if y % 5 == 0:
            c = ROOFL if ph else ROOF
        elif y % 5 == 4:
            c = ROOFS
        if h2(x, y, 22) < 8:
            c = ROOFD
        h.put(x, y, c)
for x in range(hw):                                       # scalloped drip edge
    h.put(x, 20, ROOFS)
    if (x // 6) % 2 == 0:
        h.put(x, 21, ROOFS)

# timber frame: verticals + horizontal girts (skirting door/windows)
for bx in (0, 92, 288, hw - 4):
    h.rect(bx, 22, bx + 3, hh - 11, BEAM)
    h.rect(bx, 22, bx, hh - 11, BEAML)
    h.rect(bx + 3, 22, bx + 3, hh - 11, BEAMD)
for (gx0, gx1) in ((4, 91), (292, hw - 5)):               # girt above the windows
    h.rect(gx0, 40, gx1, 43, BEAM)
    h.rect(gx0, 40, gx1, 40, BEAML)
    h.rect(gx0, 43, gx1, 43, BEAMD)

# door (centered): plum frame, lit lintel, indigo planks, porthole, gold knob
dx0, dx1 = hw // 2 - 24, hw // 2 + 24
h.rect(dx0 - 5, 48, dx1 + 5, hh - 1, FRAME)
h.rect(dx0 - 5, 48, dx1 + 5, 50, BEAML)                   # lintel catches light
h.rect(dx0 - 5, 51, dx1 + 5, 51, BEAMD)
h.rect(dx0 - 5, 48, dx0 - 5, hh - 1, BEAML)
h.rect(dx1 + 5, 48, dx1 + 5, hh - 1, BEAMD)
h.rect(dx0, 52, dx1, hh - 1, DOORC)
for px_ in range(dx0 + 12, dx1, 12):
    h.rect(px_, 52, px_, hh - 1, DOORP)                   # door planks
h.rect(dx0, 52, dx1, 52, DOORL)                           # lit plank tops
for y in range(54, hh - 2, 4):                            # plank grain ticks
    if h2(0, y, 23) < 96:
        h.put(dx0 + 5 + h2(y, 0, 24) % 36, y, DOORP)
# porthole window in the door, glowing warm
h.rect(hw // 2 - 5, 62, hw // 2 + 5, 72, FRAME)
for y in range(63, 72):
    for x in range(hw // 2 - 4, hw // 2 + 5):
        if ((x - hw // 2) / 4.5) ** 2 + ((y - 67) / 4.2) ** 2 <= 1.0:
            h.put(x, y, lerp3(GLASS_TOP, GLASS_MID, (y - 63) / 8.0))
h.rect(dx1 - 9, 88, dx1 - 6, 93, KNOB)
h.put(dx1 - 9, 88, (255, 234, 168, 255))                  # knob glint

# lanterns flanking the door: plum bracket, warm gold flame, glow on the plaster
for lx in (dx0 - 14, dx1 + 10):
    h.rect(lx, 56, lx + 4, 57, BEAMD)                     # bracket
    h.rect(lx + 1, 58, lx + 3, 66, BEAMD)                 # cage
    h.rect(lx + 1, 60, lx + 3, 64, KNOB)                  # glow body
    h.put(lx + 2, 61, (255, 240, 190, 255))               # hot core
    for (gx, gy) in ((lx - 1, 61), (lx + 5, 61), (lx + 2, 58), (lx + 2, 67)):
        h.put(gx, gy, (252, 216, 150, 255))               # spilled glow

# windows: sunset-gradient glass, mullions, sill + hot-pink flower boxes
for wx in (44, 302):
    h.rect(wx - 5, 46, wx + 41, 86, FRAME)
    h.rect(wx - 5, 46, wx + 41, 47, BEAML)
    h.rect(wx - 5, 85, wx + 41, 86, BEAMD)
    for y in range(50, 83):                               # dusk sky in the panes
        t = (y - 50) / 32.0
        if t < 0.5:
            c = lerp3(GLASS_TOP, GLASS_MID, t * 2.0)
        else:
            c = lerp3(GLASS_MID, GLASS_BOT, (t - 0.5) * 2.0)
        for x in range(wx, wx + 37):
            # banded posterize: quantize with a checker dither at the seams
            q = tuple((ch // 18) * 18 + (9 if (x + y) % 2 else 0) for ch in c[:3])
            h.put(x, y, (min(255, q[0]), min(255, q[1]), min(255, q[2]), 255))
    for i in range(10):                                   # diagonal reflection streak
        x = wx + 4 + i
        y = 78 - i * 3
        for dy in range(3):
            if 50 <= y + dy <= 82:
                h.put(x, y + dy, (252, 232, 190, 255))
    h.rect(wx + 17, 50, wx + 19, 82, FRAME)               # mullions
    h.rect(wx, 65, wx + 36, 67, FRAME)
    h.rect(wx - 7, 86, wx + 43, 89, PLASL)                # sill
    h.rect(wx - 7, 89, wx + 43, 90, PLASD)
    # flower box spilling pink + gold blooms
    h.rect(wx - 2, 91, wx + 38, 99, BEAM)
    h.rect(wx - 2, 91, wx + 38, 91, BEAML)
    h.rect(wx - 2, 99, wx + 38, 99, BEAMD)
    for i in range(9):
        fx = wx + 1 + i * 4 + h2(i, wx, 25) % 2
        fy = 90 + h2(wx, i, 26) % 3
        h.put(fx, fy, LEAFYD)
        h.put(fx + 1, fy - 1, LEAFY)
        h.put(fx - 1, fy - 1, LEAFY)
        c = FLW_PNK if i % 3 else FLW_GLD
        h.rect(fx, fy - 3, fx + 1, fy - 2, c)                 # chunky 2x2 bloom
        h.put(fx + i % 2, fy - 4, (255, 236, 240, 255) if i % 3 else (255, 236, 170, 255))
h.save("house_front.png")

# ---- the Academy front (448x160) ---------------------------------------------------
# Same color script: lavender stone, magenta banner, sunset in the windows.
STONE  = (178, 168, 204, 255)
STONED = (146, 136, 176, 255)
STONEL = (206, 198, 228, 255)
BANNER = (172, 48, 116, 255)
BANNERD= (130, 34, 92, 255)
BANNERL= (206, 76, 146, 255)
CHALKW = (240, 242, 240, 255)

sw, sh = 448, 160
s = Img(sw, sh)
s.rect(0, 16, sw - 1, sh - 1, STONE)
for y in range(16, sh):
    for x in range(sw):
        r = h2(x, y, 2)
        if r < 10:
            s.put(x, y, STONED)
        elif r > 248:
            s.put(x, y, STONEL)
# stone block courses w/ offset joints
for y in range(28, sh, 20):
    s.rect(0, y, sw - 1, y + 1, STONED)
    off = 20 if (y // 20) % 2 else 0
    for jx in range(off, sw, 40):
        s.rect(jx, y - 19, jx, y - 1, STONED)
# cornice
s.rect(0, 0, sw - 1, 11, STONEL)
s.rect(0, 11, sw - 1, 15, STONED)
s.rect(0, 6, sw - 1, 7, STONE)
# arched double door
ddx0, ddx1 = sw // 2 - 36, sw // 2 + 36
s.rect(ddx0 - 6, 68, ddx1 + 6, sh - 1, STONED)
s.rect(ddx0, 76, ddx1, sh - 1, DOORC)
for i in range(16):
    s.rect(ddx0 + i, 68 + (16 - i) // 2, ddx1 - i, 76, DOORC)
s.rect(sw // 2 - 1, 80, sw // 2, sh - 1, FRAME)
for px_ in range(ddx0 + 12, ddx1, 12):
    s.rect(px_, 84, px_, sh - 1, (44, 34, 28, 255))
# banner with the school name
bw = text_width("ACADEMY", 2) + 20
bx0 = sw // 2 - bw // 2
s.rect(bx0, 26, bx0 + bw, 56, BANNERD)
s.rect(bx0 + 2, 28, bx0 + bw - 2, 52, BANNER)
s.rect(bx0 + 2, 28, bx0 + bw - 2, 31, BANNERL)
draw_text(s.put, "ACADEMY", bx0 + 11, 35, CHALKW, 2)
# arched windows: the same sunset gradient as the cottage panes
for wx in (52, 124, sw - 156, sw - 84):
    for i in range(8):                                   # arch top
        s.rect(wx + i, 76 + (8 - i) // 2, wx + 30 - i, 80, lerp3(GLASS_TOP, GLASS_MID, 0.1))
    for y in range(80, 123):
        t = (y - 80) / 42.0
        if t < 0.5:
            c = lerp3(GLASS_TOP, GLASS_MID, t * 2.0)
        else:
            c = lerp3(GLASS_MID, GLASS_BOT, (t - 0.5) * 2.0)
        for x in range(wx, wx + 31):
            q = tuple((ch // 18) * 18 + (9 if (x + y) % 2 else 0) for ch in c[:3])
            s.put(x, y, (min(255, q[0]), min(255, q[1]), min(255, q[2]), 255))
    s.rect(wx + 14, 80, wx + 16, 122, STONED)            # mullion
    s.rect(wx - 2, 122, wx + 32, 125, STONEL)            # sill
s.save("school_front.png")

# ---- poop bag (3 frames of 32x32) ---------------------------------------------------
BAG   = (156, 112, 64, 255)
BAGL  = (184, 142, 86, 255)
BAGD  = (120, 84, 50, 255)
POO   = (100, 68, 40, 255)
STINK = (150, 200, 116, 210)

pb = Img(96, 32)
def bag(ox, squished):
    if squished:
        pb.rect(ox + 4, 24, ox + 27, 29, BAGD)
        pb.rect(ox + 6, 22, ox + 25, 24, BAG)
        pb.rect(ox + 8, 22, ox + 12, 23, BAGL)
        pb.rect(ox + 2, 26, ox + 4, 29, POO)             # splurt
        pb.rect(ox + 27, 24, ox + 30, 27, POO)
        pb.rect(ox + 14, 20, ox + 18, 22, POO)
    else:
        pb.rect(ox + 8, 12, ox + 23, 29, BAG)
        pb.rect(ox + 8, 12, ox + 13, 20, BAGL)
        pb.rect(ox + 20, 20, ox + 23, 29, BAGD)
        pb.rect(ox + 10, 8, ox + 21, 12, BAGD)           # crumpled fold
        pb.rect(ox + 12, 6, ox + 19, 8, BAG)
        pb.rect(ox + 13, 6, ox + 15, 7, BAGL)

def stink(ox, phase):
    pts = [(7, 3), (10, 1), (24, 2), (20, 5)] if phase == 0 else [(9, 2), (13, 5), (22, 1), (25, 4)]
    for (x, y) in pts:
        pb.put(ox + x, y, STINK)
        pb.put(ox + x, y + 1, STINK)
        pb.put(ox + x + 1, y + 2, STINK)

bag(0, False);  stink(0, 0)
bag(32, False); stink(32, 1)
bag(64, True)
pb.save("poop_bag.png")

# ---- paw print (12x12) ----------------------------------------------------------------
pp = Img(12, 12)
PRINT = (116, 78, 46, 215)
pp.rect(3, 6, 8, 10, PRINT)                              # pad
pp.put(2, 7, PRINT); pp.put(9, 7, PRINT)
for tx in (1, 5, 9):
    pp.rect(tx, 2, tx + 1, 3, PRINT)
pp.rect(5, 0, 6, 1, PRINT)
pp.save("paw_print.png")

# ---- hall floor / wall tiles (32x32) ----------------------------------------------------
# rosewood planks + plum panelling — warm field, violet-leaning shadows
WOOD  = (188, 130, 104, 255)
WOODD = (156, 100, 88, 255)
WOODL = (214, 158, 122, 255)
f = Img(32, 32)
f.rect(0, 0, 31, 31, WOOD)
for y in range(32):
    for x in range(32):
        r = h2(x, y, 3)
        if r < 10:
            f.put(x, y, WOODD)
        elif r > 248:
            f.put(x, y, WOODL)
for y in (7, 15, 23, 31):                                # plank seams
    f.rect(0, y, 31, y, WOODD)
for y in (0, 8, 16, 24):
    f.rect(0, y, 31, y, WOODL)
for (jx, y0, y1) in ((14, 0, 7), (24, 8, 15), (6, 16, 23), (20, 24, 31)):
    f.rect(jx, y0, jx, y1, WOODD)                        # butt joints
for x in range(0, 32, 2):                                # subtle grain
    if h2(x, 0, 4) < 90:
        f.put(x, 3 + h2(x, 1, 4) % 4, WOODD)
f.save("hall_floor.png")

PANEL  = (122, 80, 88, 255)
PANELD = (94, 60, 70, 255)
PANELL = (148, 104, 104, 255)
w = Img(32, 32)
w.rect(0, 0, 31, 31, PANEL)
w.rect(0, 0, 31, 1, PANELL)
w.rect(0, 26, 31, 31, PANELD)                            # base rail
w.rect(0, 24, 31, 25, PANELL)
for bx in (0, 16):
    w.rect(bx, 2, bx + 1, 23, PANELD)
    w.rect(bx + 14, 2, bx + 15, 23, PANELD)
    w.rect(bx + 4, 5, bx + 11, 6, PANELD)                # inset panel
    w.rect(bx + 4, 19, bx + 11, 20, PANELL)
w.save("hall_wall.png")

# ---- chalkboard (224x72): actual readable chalk notes ------------------------------------
BOARD  = (38, 102, 96, 255)      # deep teal slate
BOARDD = (28, 82, 78, 255)
CHALK  = (228, 234, 228, 255)
CHALKD = (168, 190, 176, 235)
cb = Img(224, 72)
cb.rect(0, 0, 223, 71, FRAME)
cb.rect(2, 2, 221, 3, (146, 106, 70, 255))
cb.rect(6, 6, 217, 65, BOARD)
for y in range(6, 66):
    for x in range(6, 218):
        if h2(x, y, 5) < 6:
            cb.put(x, y, BOARDD)
draw_text(cb.put, "RE-ENCHANTMENT THEORY", 14, 11, CHALK)
draw_text(cb.put, "WHERE DID THE MAGIC GO?", 14, 24, CHALKD)
draw_text(cb.put, "M = WONDER x BELIEF", 14, 37, CHALKD)
draw_text(cb.put, "LECTURE I - PROF. BASIL", 14, 55, CHALKD)
# chalk diagram: circle + arrow
for (x, y) in ((186, 42), (190, 39), (195, 38), (200, 39), (204, 42), (200, 45),
               (195, 46), (190, 45)):
    cb.put(x, y, CHALKD)
    cb.put(x + 1, y, CHALKD)
cb.rect(162, 42, 180, 42, CHALKD)
cb.put(179, 41, CHALKD); cb.put(179, 43, CHALKD)
cb.rect(6, 62, 217, 65, BOARDD)                          # chalk tray shadow
cb.rect(30, 66, 44, 68, CHALK)                           # a bit of chalk on the tray
cb.save("chalkboard.png")

# ---- podium (52x60) ------------------------------------------------------------------------
pd = Img(52, 60)
pd.rect(4, 16, 47, 59, BEAM)
pd.rect(4, 16, 47, 18, BEAMD)
pd.rect(8, 20, 43, 55, FRAME)
pd.rect(8, 20, 43, 21, (146, 104, 70, 255))
pd.rect(22, 30, 29, 45, BEAMD)                           # inset panel
pd.rect(0, 0, 51, 14, BEAMD)                             # slanted top
pd.rect(0, 0, 51, 3, (150, 108, 72, 255))
pd.rect(0, 13, 51, 14, (40, 26, 20, 255))
pd.rect(4, 56, 47, 59, BEAMD)
pd.save("podium.png")

# ---- audience cats (4 colorways, 40x40 each) ------------------------------------------------
COLORWAYS = [
    ((124, 124, 136, 255), (98, 98, 112, 255), (148, 148, 160, 255)),   # gray
    ((202, 128, 60, 255), (168, 100, 46, 255), (224, 152, 78, 255)),    # orange
    ((228, 216, 194, 255), (200, 186, 160, 255), (244, 234, 214, 255)), # cream
    ((128, 96, 64, 255), (102, 74, 50, 255), (150, 116, 80, 255)),      # brown
]
ac = Img(160, 40)
for i, (cfur, cdark, clight) in enumerate(COLORWAYS):
    ox = i * 40
    ac.rect(ox + 8, 12, ox + 31, 31, cfur)               # head
    ac.rect(ox + 8, 12, ox + 31, 14, clight)             # crown light
    ac.rect(ox + 8, 28, ox + 31, 31, cdark)
    for ex in (ox + 8, ox + 24):                         # ears
        ac.rect(ex, 6, ex + 7, 11, cfur)
        ac.rect(ex, 6, ex + 1, 7, cdark)
        ac.rect(ex + 6, 6, ex + 7, 7, cdark)
        ac.rect(ex + 3, 6, ex + 4, 8, cdark)             # inner ear shadow
    ac.rect(ox + 4, 32, ox + 35, 39, cdark)              # shoulders
    ac.rect(ox + 4, 32, ox + 35, 33, cfur)
ac.save("audience_cats.png")
