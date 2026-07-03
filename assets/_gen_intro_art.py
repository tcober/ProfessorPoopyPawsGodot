#!/usr/bin/env python3
"""Props for the opening sequence at the 2x art scale (96px actors on a 640x360
stage — the framing gets closer and more cinematic; big props overflow the frame,
door-centered). Palette follows _palette.py's color script: peach/violet cottage,
lavender Academy, plum hall. Writes PNGs into assets/props/.
Re-run: python3 assets/_gen_intro_art.py

  house_front.png    768x256  Basil's cottage (door-centered on the stage)
  school_front.png   896x320  the Academy
  poop_bag.png       192x64   3 frames (64x64): bag+stink A / B / squished
  paw_print.png      24x24    one brown print
  hall_floor.png     64x64    plank floor tile
  hall_wall.png      64x64    panelled wall tile
  chalkboard.png     448x144  framed board, readable chalk notes
  podium.png         104x120  wooden lectern
  audience_cats.png  320x80   4 back-of-head cats
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _pixfont import draw_text, text_width
from _artlib import Img, h2, lerp

OUTDIR = os.path.join(HERE, "props")
os.makedirs(OUTDIR, exist_ok=True)


def lerp3(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def save(img, name):
    img.save(os.path.join(OUTDIR, name))


# ---- Basil's cottage front (768x256) -------------------------------------------
# Paper Girls color script: sun-warmed peach plaster whose shadows hue-shift
# violet, deep plum timber, hot magenta shingles, sunset-gradient glass. The
# render is FF/CT: eave shadow band, lit shingle courses, stone footing, flower
# boxes, door lanterns. Door stays centered at x = w/2.
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

hw, hh = 768, 256
h = Img(hw, hh)

# plaster field with noise
h.rect(0, 40, hw - 1, hh - 1, PLAS)
for y in range(40, hh):
    for x in range(hw):
        r = h2(x // 2, y // 2, 1)
        if r < 12:
            h.put(x, y, PLASD)
        elif r > 246:
            h.put(x, y, PLASL)
# the roof hangs over the wall: violet eave shadow, dithered out
for y in range(44, 68):
    t = (y - 44) / 24.0
    for x in range(hw):
        if t < 0.5:
            h.put(x, y, PLASS)
        elif t < 0.85 and (x // 2 + y // 2) % 2 == 0:
            h.put(x, y, PLASD)
# stone footing: coursed blocks with staggered joints
for y in range(hh - 20, hh):
    for x in range(hw):
        c = STONEF
        r = h2(x // 6, y // 6, 21)
        if r > 240:
            c = STONEFL
        elif r < 16:
            c = STONEFD
        h.put(x, y, c)
for yy in (hh - 20, hh - 10):
    h.rect(0, yy, hw - 1, yy + 1, STONEFD)
for row, yy in enumerate((hh - 18, hh - 8)):
    for jx in range(18 + row * 28, hw, 56):
        h.rect(jx, yy, jx + 1, yy + 6, STONEFD)
h.rect(0, hh - 22, hw - 1, hh - 22, PLASD)               # settle line above stones

# shingled roof: magenta courses, lit crest per row, deep seams
for y in range(0, 40):
    row = y // 10
    for x in range(hw):
        ph = (x // 24 + row) % 2
        c = ROOF if ph else ROOFD
        if y % 10 <= 1:
            c = ROOFL if ph else ROOF
        elif y % 10 >= 8:
            c = ROOFS
        if h2(x // 2, y // 2, 22) < 8:
            c = ROOFD
        h.put(x, y, c)
for x in range(hw):                                       # scalloped drip edge
    h.put(x, 40, ROOFS)
    h.put(x, 41, ROOFS)
    if (x // 12) % 2 == 0:
        h.put(x, 42, ROOFS)
        h.put(x, 43, ROOFS)

# timber frame: verticals + horizontal girts (skirting door/windows)
for bx in (0, 184, 576, hw - 8):
    h.rect(bx, 44, bx + 7, hh - 21, BEAM)
    h.rect(bx, 44, bx + 1, hh - 21, BEAML)
    h.rect(bx + 6, 44, bx + 7, hh - 21, BEAMD)
for (gx0, gx1) in ((8, 182), (584, hw - 9)):              # girt above the windows
    h.rect(gx0, 80, gx1, 86, BEAM)
    h.rect(gx0, 80, gx1, 81, BEAML)
    h.rect(gx0, 86, gx1, 86, BEAMD)

# door (centered): plum frame, lit lintel, indigo planks, porthole, gold knob
dx0, dx1 = hw // 2 - 48, hw // 2 + 48
h.rect(dx0 - 10, 96, dx1 + 10, hh - 1, FRAME)
h.rect(dx0 - 10, 96, dx1 + 10, 100, BEAML)                # lintel catches light
h.rect(dx0 - 10, 101, dx1 + 10, 102, BEAMD)
h.rect(dx0 - 10, 96, dx0 - 9, hh - 1, BEAML)
h.rect(dx1 + 9, 96, dx1 + 10, hh - 1, BEAMD)
h.rect(dx0, 104, dx1, hh - 1, DOORC)
for px_ in range(dx0 + 24, dx1, 24):
    h.rect(px_, 104, px_ + 1, hh - 1, DOORP)              # door planks
h.rect(dx0, 104, dx1, 105, DOORL)                         # lit plank tops
for y in range(108, hh - 4, 8):                           # plank grain ticks
    if h2(0, y, 23) < 96:
        gx = dx0 + 10 + h2(y, 0, 24) % 72
        h.rect(gx, y, gx + 1, y, DOORP)
# porthole window in the door, glowing warm
h.rect(hw // 2 - 10, 124, hw // 2 + 10, 144, FRAME)
for y in range(126, 144):
    for x in range(hw // 2 - 8, hw // 2 + 9):
        if ((x - hw // 2) / 9.0) ** 2 + ((y - 134) / 8.4) ** 2 <= 1.0:
            h.put(x, y, lerp3(GLASS_TOP, GLASS_MID, (y - 126) / 16.0))
h.rect(dx1 - 18, 176, dx1 - 12, 186, KNOB)
h.rect(dx1 - 18, 176, dx1 - 17, 177, (255, 234, 168, 255))  # knob glint

# lanterns flanking the door: plum bracket, warm gold flame, glow on the plaster
for lx in (dx0 - 28, dx1 + 20):
    h.rect(lx, 112, lx + 8, 114, BEAMD)                   # bracket
    h.rect(lx + 2, 116, lx + 6, 132, BEAMD)               # cage
    h.rect(lx + 2, 120, lx + 6, 128, KNOB)                # glow body
    h.rect(lx + 3, 122, lx + 4, 123, (255, 240, 190, 255))  # hot core
    for (gx, gy) in ((lx - 2, 122), (lx + 10, 122), (lx + 4, 116), (lx + 4, 134)):
        h.rect(gx, gy, gx + 1, gy + 1, (252, 216, 150, 255))  # spilled glow

# windows: sunset-gradient glass, mullions, sill + hot-pink flower boxes
for wx in (88, 604):
    h.rect(wx - 10, 92, wx + 82, 172, FRAME)
    h.rect(wx - 10, 92, wx + 82, 94, BEAML)
    h.rect(wx - 10, 170, wx + 82, 172, BEAMD)
    for y in range(100, 166):                             # dusk sky in the panes
        t = (y - 100) / 64.0
        if t < 0.5:
            c = lerp3(GLASS_TOP, GLASS_MID, t * 2.0)
        else:
            c = lerp3(GLASS_MID, GLASS_BOT, (t - 0.5) * 2.0)
        for x in range(wx, wx + 74):
            # banded posterize: quantize with a checker dither at the seams
            q = tuple((ch // 18) * 18 + (9 if (x // 2 + y // 2) % 2 else 0) for ch in c[:3])
            h.put(x, y, (min(255, q[0]), min(255, q[1]), min(255, q[2]), 255))
    for i in range(20):                                   # diagonal reflection streak
        x = wx + 8 + i
        y = 156 - i * 3
        for dy in range(6):
            if 100 <= y + dy <= 164:
                h.put(x, y + dy, (252, 232, 190, 255))
    h.rect(wx + 34, 100, wx + 38, 164, FRAME)             # mullions
    h.rect(wx, 130, wx + 73, 134, FRAME)
    h.rect(wx - 14, 172, wx + 86, 178, PLASL)             # sill
    h.rect(wx - 14, 178, wx + 86, 180, PLASD)
    # flower box spilling pink + gold blooms
    h.rect(wx - 4, 182, wx + 76, 198, BEAM)
    h.rect(wx - 4, 182, wx + 76, 183, BEAML)
    h.rect(wx - 4, 197, wx + 76, 198, BEAMD)
    for i in range(9):
        fx = wx + 2 + i * 8 + h2(i, wx, 25) % 4
        fy = 180 + h2(wx, i, 26) % 5
        h.rect(fx, fy, fx + 1, fy + 1, LEAFYD)
        h.rect(fx + 2, fy - 2, fx + 3, fy - 1, LEAFY)
        h.rect(fx - 2, fy - 2, fx - 1, fy - 1, LEAFY)
        c = FLW_PNK if i % 3 else FLW_GLD
        h.rect(fx, fy - 6, fx + 3, fy - 3, c)             # chunky bloom
        h.rect(fx + i % 2, fy - 8, fx + 1 + i % 2, fy - 7,
               (255, 236, 240, 255) if i % 3 else (255, 236, 170, 255))
save(h, "house_front.png")

# ---- the Academy front (896x320) ---------------------------------------------------
# Same color script: lavender stone, magenta banner, sunset in the windows.
STONE  = (178, 168, 204, 255)
STONED = (146, 136, 176, 255)
STONEL = (206, 198, 228, 255)
BANNER = (172, 48, 116, 255)
BANNERD= (130, 34, 92, 255)
BANNERL= (206, 76, 146, 255)
CHALKW = (240, 242, 240, 255)

sw, sh = 896, 320
s = Img(sw, sh)
s.rect(0, 32, sw - 1, sh - 1, STONE)
for y in range(32, sh):
    for x in range(sw):
        r = h2(x // 2, y // 2, 2)
        if r < 10:
            s.put(x, y, STONED)
        elif r > 248:
            s.put(x, y, STONEL)
# stone block courses w/ offset joints
for y in range(56, sh, 40):
    s.rect(0, y, sw - 1, y + 2, STONED)
    off = 40 if (y // 40) % 2 else 0
    for jx in range(off, sw, 80):
        s.rect(jx, y - 38, jx + 1, y - 2, STONED)
# cornice
s.rect(0, 0, sw - 1, 22, STONEL)
s.rect(0, 22, sw - 1, 30, STONED)
s.rect(0, 12, sw - 1, 14, STONE)
# arched double door
ddx0, ddx1 = sw // 2 - 72, sw // 2 + 72
s.rect(ddx0 - 12, 136, ddx1 + 12, sh - 1, STONED)
s.rect(ddx0, 152, ddx1, sh - 1, DOORC)
for i in range(32):
    s.rect(ddx0 + i, 136 + (32 - i) // 2, ddx1 - i, 152, DOORC)
s.rect(sw // 2 - 2, 160, sw // 2 + 1, sh - 1, FRAME)
for px_ in range(ddx0 + 24, ddx1, 24):
    s.rect(px_, 168, px_ + 1, sh - 1, (44, 34, 28, 255))
# banner with the school name
bw = text_width("ACADEMY", 4) + 40
bx0 = sw // 2 - bw // 2
s.rect(bx0, 52, bx0 + bw, 112, BANNERD)
s.rect(bx0 + 4, 56, bx0 + bw - 4, 104, BANNER)
s.rect(bx0 + 4, 56, bx0 + bw - 4, 62, BANNERL)
draw_text(s.put, "ACADEMY", bx0 + 22, 70, CHALKW, 4)
# arched windows: the same sunset gradient as the cottage panes
for wx in (104, 248, sw - 312, sw - 168):
    for i in range(16):                                  # arch top
        s.rect(wx + i, 152 + (16 - i) // 2, wx + 60 - i, 160, lerp3(GLASS_TOP, GLASS_MID, 0.1))
    for y in range(160, 246):
        t = (y - 160) / 84.0
        if t < 0.5:
            c = lerp3(GLASS_TOP, GLASS_MID, t * 2.0)
        else:
            c = lerp3(GLASS_MID, GLASS_BOT, (t - 0.5) * 2.0)
        for x in range(wx, wx + 62):
            q = tuple((ch // 18) * 18 + (9 if (x // 2 + y // 2) % 2 else 0) for ch in c[:3])
            s.put(x, y, (min(255, q[0]), min(255, q[1]), min(255, q[2]), 255))
    s.rect(wx + 28, 160, wx + 32, 244, STONED)           # mullion
    s.rect(wx - 4, 244, wx + 64, 250, STONEL)            # sill
save(s, "school_front.png")

# ---- poop bag (3 frames of 64x64) ---------------------------------------------------
BAG   = (156, 112, 64, 255)
BAGL  = (184, 142, 86, 255)
BAGD  = (120, 84, 50, 255)
POO   = (100, 68, 40, 255)
STINK = (150, 200, 116, 210)

pb = Img(192, 64)
def bag(ox, squished):
    if squished:
        pb.rect(ox + 8, 48, ox + 54, 58, BAGD)
        pb.rect(ox + 12, 44, ox + 50, 48, BAG)
        pb.rect(ox + 16, 44, ox + 24, 46, BAGL)
        pb.rect(ox + 4, 52, ox + 8, 58, POO)             # splurt
        pb.rect(ox + 54, 48, ox + 60, 54, POO)
        pb.rect(ox + 28, 40, ox + 36, 44, POO)
    else:
        pb.rect(ox + 16, 24, ox + 46, 58, BAG)
        pb.rect(ox + 16, 24, ox + 26, 40, BAGL)
        pb.rect(ox + 40, 40, ox + 46, 58, BAGD)
        pb.rect(ox + 20, 16, ox + 42, 24, BAGD)          # crumpled fold
        pb.rect(ox + 24, 12, ox + 38, 16, BAG)
        pb.rect(ox + 26, 12, ox + 30, 14, BAGL)

def stink(ox, phase):
    pts = [(14, 6), (20, 2), (48, 4), (40, 10)] if phase == 0 else [(18, 4), (26, 10), (44, 2), (50, 8)]
    for (x, y) in pts:
        pb.rect(ox + x, y, ox + x + 1, y + 3, STINK)
        pb.rect(ox + x + 2, y + 4, ox + x + 3, y + 5, STINK)

bag(0, False);   stink(0, 0)
bag(64, False);  stink(64, 1)
bag(128, True)
save(pb, "poop_bag.png")

# ---- paw print (24x24) ----------------------------------------------------------------
pp = Img(24, 24)
PRINT = (116, 78, 46, 215)
pp.rect(6, 12, 17, 20, PRINT)                            # pad
pp.rect(4, 14, 5, 16, PRINT)
pp.rect(18, 14, 19, 16, PRINT)
for tx in (2, 10, 18):
    pp.rect(tx, 4, tx + 3, 7, PRINT)
pp.rect(10, 0, 13, 3, PRINT)
save(pp, "paw_print.png")

# ---- hall floor / wall tiles (64x64) ----------------------------------------------------
# rosewood planks + plum panelling — warm field, violet-leaning shadows
WOODF  = (188, 130, 104, 255)
WOODD = (156, 100, 88, 255)
WOODL = (214, 158, 122, 255)
f = Img(64, 64)
f.rect(0, 0, 63, 63, WOODF)
for y in range(64):
    for x in range(64):
        r = h2(x // 2, y // 2, 3)
        if r < 10:
            f.put(x, y, WOODD)
        elif r > 248:
            f.put(x, y, WOODL)
for y in (15, 31, 47, 63):                               # plank seams
    f.rect(0, y - 1, 63, y, WOODD)
for y in (0, 16, 32, 48):
    f.rect(0, y, 63, y, WOODL)
for (jx, y0, y1) in ((28, 0, 14), (48, 16, 30), (12, 32, 46), (40, 48, 62)):
    f.rect(jx, y0, jx + 1, y1, WOODD)                    # butt joints
for x in range(0, 64, 4):                                # subtle grain
    if h2(x, 0, 4) < 90:
        gy = 6 + h2(x, 1, 4) % 8
        f.rect(x, gy, x + 1, gy, WOODD)
save(f, "hall_floor.png")

PANEL  = (122, 80, 88, 255)
PANELD = (94, 60, 70, 255)
PANELL = (148, 104, 104, 255)
w = Img(64, 64)
w.rect(0, 0, 63, 63, PANEL)
w.rect(0, 0, 63, 3, PANELL)
w.rect(0, 52, 63, 63, PANELD)                            # base rail
w.rect(0, 48, 63, 51, PANELL)
for bx in (0, 32):
    w.rect(bx, 4, bx + 3, 47, PANELD)
    w.rect(bx + 28, 4, bx + 31, 47, PANELD)
    w.rect(bx + 8, 10, bx + 23, 13, PANELD)              # inset panel
    w.rect(bx + 8, 38, bx + 23, 41, PANELL)
save(w, "hall_wall.png")

# ---- chalkboard (448x144): actual readable chalk notes ------------------------------------
BOARD  = (38, 102, 96, 255)      # deep teal slate
BOARDD = (28, 82, 78, 255)
CHALK  = (228, 234, 228, 255)
CHALKD = (168, 190, 176, 235)
cb = Img(448, 144)
cb.rect(0, 0, 447, 143, FRAME)
cb.rect(4, 4, 443, 7, (146, 106, 70, 255))
cb.rect(12, 12, 435, 131, BOARD)
for y in range(12, 132):
    for x in range(12, 436):
        if h2(x // 2, y // 2, 5) < 6:
            cb.put(x, y, BOARDD)
draw_text(cb.put, "RE-ENCHANTMENT THEORY", 28, 22, CHALK, 2)
draw_text(cb.put, "WHERE DID THE MAGIC GO?", 28, 48, CHALKD, 2)
draw_text(cb.put, "M = WONDER x BELIEF", 28, 74, CHALKD, 2)
draw_text(cb.put, "LECTURE I - PROF. BASIL", 28, 110, CHALKD, 2)
# chalk diagram: circle + arrow
for (x, y) in ((372, 84), (380, 78), (390, 76), (400, 78), (408, 84), (400, 90),
               (390, 92), (380, 90)):
    cb.rect(x, y, x + 3, y + 1, CHALKD)
cb.rect(324, 84, 360, 85, CHALKD)
cb.rect(358, 82, 359, 83, CHALKD)
cb.rect(358, 86, 359, 87, CHALKD)
cb.rect(12, 124, 435, 131, BOARDD)                       # chalk tray shadow
cb.rect(60, 132, 88, 137, CHALK)                         # a bit of chalk on the tray
save(cb, "chalkboard.png")

# ---- podium (104x120) ------------------------------------------------------------------------
pd = Img(104, 120)
pd.rect(8, 32, 95, 119, BEAM)
pd.rect(8, 32, 95, 36, BEAMD)
pd.rect(16, 40, 87, 111, FRAME)
pd.rect(16, 40, 87, 43, (146, 104, 70, 255))
pd.rect(44, 60, 59, 91, BEAMD)                           # inset panel
pd.rect(0, 0, 103, 28, BEAMD)                            # slanted top
pd.rect(0, 0, 103, 7, (150, 108, 72, 255))
pd.rect(0, 26, 103, 28, (40, 26, 20, 255))
pd.rect(8, 112, 95, 119, BEAMD)
save(pd, "podium.png")

# ---- audience cats (4 colorways, 80x80 each) ------------------------------------------------
COLORWAYS = [
    ((124, 124, 136, 255), (98, 98, 112, 255), (148, 148, 160, 255)),   # gray
    ((202, 128, 60, 255), (168, 100, 46, 255), (224, 152, 78, 255)),    # orange
    ((228, 216, 194, 255), (200, 186, 160, 255), (244, 234, 214, 255)), # cream
    ((128, 96, 64, 255), (102, 74, 50, 255), (150, 116, 80, 255)),      # brown
]
ac = Img(320, 80)
for i, (cfur, cdark, clight) in enumerate(COLORWAYS):
    ox = i * 80
    ac.rect(ox + 16, 24, ox + 62, 62, cfur)              # head
    ac.rect(ox + 16, 24, ox + 62, 28, clight)            # crown light
    ac.rect(ox + 16, 56, ox + 62, 62, cdark)
    for ex in (ox + 16, ox + 48):                        # ears
        ac.rect(ex, 12, ex + 14, 22, cfur)
        ac.rect(ex, 12, ex + 2, 14, cdark)
        ac.rect(ex + 12, 12, ex + 14, 14, cdark)
        ac.rect(ex + 6, 12, ex + 8, 17, cdark)           # inner ear shadow
    ac.rect(ox + 8, 64, ox + 71, 79, cdark)              # shoulders
    ac.rect(ox + 8, 64, ox + 71, 66, cfur)
save(ac, "audience_cats.png")
