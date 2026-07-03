#!/usr/bin/env python3
"""Sprite sheet for SCHWEINLER — the bully. A stout, smug pig: big snout, beady angry
eyes, red neckerchief, curly tail, cloven trotters. Rendered FF6 / Chrono
Trigger-style like Basil: compact upright figure (head / body / legs each about a
third), muted 4-tone ramps, restrained dithering, dark outlines. Writes
assets/schweinler_gen.png (192x192, 48x48 cells, 4x4) matching
entities/npcs/schweinler_frames.tres:

  row0 walk_down(4)  row1 walk_up(4)  row2 walk_side(4, faces RIGHT; flip for left)
  row3 point_up(2) + laugh_down(2)

Cutscene actor for now (plants the poop bag, brands the nickname), drawn at Basil's
scale/baseline so he can walk into gameplay later.
Re-run: python3 assets/_gen_schweinler_sprites.py
"""
import struct, zlib, os

HERE = os.path.dirname(os.path.abspath(__file__))
CELL, COLS, ROWS = 48, 4, 4
FEET = 44

# ---- material ramps (light -> dark) --------------------------------------------
PIG   = [(238, 190, 176, 255), (214, 152, 140, 255), (186, 114, 108, 255), (150, 82, 86, 255)]
BELLY = [(246, 214, 200, 255), (230, 182, 168, 255), (206, 144, 134, 255), (178, 110, 106, 255)]
RED   = [(212, 100, 86, 255), (184, 68, 60, 255), (152, 44, 44, 255), (116, 30, 36, 255)]
HOOF  = [(132, 80, 74, 255), (108, 60, 58, 255), (84, 44, 46, 255), (62, 32, 38, 255)]

EYE_D  = (30, 22, 26, 255)
GLINT  = (255, 252, 248, 255)
BROW   = (128, 56, 62, 255)
NOSTR  = (150, 74, 84, 255)
MOUTH  = (150, 74, 84, 255)
TONGUE = (222, 110, 116, 255)
MAW    = (96, 40, 48, 255)

OUT_PIG  = (76, 34, 42, 255)
OUT_RED  = (70, 16, 24, 255)
OUT_HOOF = (36, 18, 24, 255)
OUTS = {}
for r in (PIG, BELLY):
    for c in r:
        OUTS[c] = OUT_PIG
for c in RED:
    OUTS[c] = OUT_RED
for c in HOOF:
    OUTS[c] = OUT_HOOF
OUT_SET = set(OUTS.values())


class Cell:
    def __init__(self):
        self.px = [[None] * CELL for _ in range(CELL)]

    def set(self, x, y, c):
        if 0 <= x < CELL and 0 <= y < CELL:
            self.px[y][x] = c

    def get(self, x, y):
        if 0 <= x < CELL and 0 <= y < CELL:
            return self.px[y][x]
        return None

    @staticmethod
    def _pick(ramp, t, x, y):
        b = max(0.0, min(2.999, t * 3.0))
        i = int(b)
        frac = b - i
        if frac > 0.58 or (0.45 < frac <= 0.58 and (x + y) % 2 == 0):
            i += 1
        return ramp[min(3, i)]

    def oval(self, cx, cy, rx, ry, ramp, sh=0.0, power=2.0):
        for y in range(int(cy - ry), int(cy + ry) + 2):
            for x in range(int(cx - rx), int(cx + rx) + 2):
                nx = (x - cx) / rx
                ny = (y - cy) / ry
                d = abs(nx) ** power + abs(ny) ** power
                if d > 1.0:
                    continue
                t = 0.42 + 0.30 * (nx * 0.55 + ny * 0.80) + 0.30 * d * d + sh
                self.set(x, y, self._pick(ramp, t, x, y))

    def band(self, x0, y0, x1, y1, ramp, sh=0.0):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                t = 0.30 + 0.30 * (x - x0) / max(1, x1 - x0) + sh
                self.set(x, y, self._pick(ramp, t, x, y))

    def tri(self, apex, base_y, x0, x1, ramp, sh=0.0):
        ax, ay = apex
        span = max(1, base_y - ay)
        for y in range(ay, base_y + 1):
            f = (y - ay) / span
            xl = round(ax + (x0 - ax) * f)
            xr = round(ax + (x1 - ax) * f)
            for x in range(min(xl, xr), max(xl, xr) + 1):
                t = 0.30 + 0.45 * f + sh
                self.set(x, y, self._pick(ramp, t, x, y))

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def line(self, pts, c):
        for (x, y) in pts:
            self.set(x, y, c)

    def outline(self):
        edge = []
        for y in range(CELL):
            for x in range(CELL):
                if self.px[y][x] is not None:
                    continue
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    p = self.get(nx, ny)
                    if p and p[3] == 255 and p not in OUT_SET:
                        edge.append((x, y, OUTS.get(p, OUT_PIG)))
                        break
        for x, y, c in edge:
            self.px[y][x] = c


# ---- parts ------------------------------------------------------------------------

def legs(c, lift_l=0, lift_r=0):
    """Sturdy pig legs with cloven hooves."""
    for (x0, x1, lift) in ((18, 21, lift_l), (26, 29, lift_r)):
        c.band(x0, 36 - lift, x1, FEET - 3 - lift, PIG, sh=0.12)
        c.band(x0, FEET - 2 - lift, x1, FEET - lift, HOOF)
        c.set((x0 + x1) // 2, FEET - lift, OUT_HOOF)          # cloven notch


def curly_tail_down(c, dx=0):
    pts = [(32, 28), (33.5, 26.5), (34.5 + dx * 0.4, 28), (33 + dx * 0.4, 29)]
    for (px_, py_) in pts:
        c.oval(px_, py_, 1.2, 1.2, PIG, sh=0.1)


def body_down(c, dy=0):
    """Stout barrel body, pale belly, red neckerchief with a knot."""
    c.oval(24, 29 + dy, 8.4, 7.6, PIG, power=2.2)
    c.oval(24, 31 + dy, 5.0, 4.6, BELLY, power=2.0, sh=-0.05)
    c.band(17, 21 + dy, 30, 23 + dy, RED)
    c.tri((24, 24 + dy), 28 + dy, 21, 27, RED, sh=0.1)        # knot tails


def arms_down(c, dy=0, dl=0, dr=0, point=False):
    c.band(13, 24 + dy + dl, 16, 30 + dy + dl, PIG, sh=0.08)
    c.band(13, 31 + dy + dl, 16, 33 + dy + dl, HOOF)
    c.band(32, 24 + dy + dr, 35, 30 + dy + dr, PIG, sh=0.18)
    c.band(32, 31 + dy + dr, 35, 33 + dy + dr, HOOF)


def head_down(c, dy=0, mood="smug"):
    """Compact pig head: droopy triangle ears, beady angry eyes, THE SNOUT."""
    c.tri((15, 2 + dy), 10 + dy, 13, 21, PIG)                 # ears
    c.tri((33, 2 + dy), 10 + dy, 27, 35, PIG, sh=0.18)
    c.tri((16, 4 + dy), 9 + dy, 15, 19, PIG, sh=0.35)         # inner shadow
    c.tri((32, 4 + dy), 9 + dy, 30, 33, PIG, sh=0.45)
    c.oval(24, 13 + dy, 9.2, 7.6, PIG, power=2.2)             # head
    # beady eyes + angry brows
    if mood == "laugh":
        for ex in (19, 27):
            c.line([(ex, 9 + dy), (ex + 1, 8 + dy), (ex + 2, 9 + dy)], MAW)
    else:
        for ex in (19, 27):
            c.rect(ex, 9 + dy, ex + 1, 10 + dy, EYE_D)
            c.set(ex, 9 + dy, GLINT)
        c.line([(21, 7 + dy), (20, 8 + dy)], BROW)
        c.line([(26, 7 + dy), (27, 8 + dy)], BROW)
    # snout: big lighter disc with tall nostrils
    c.oval(24, 15.5 + dy, 4.4, 2.9, PIG, power=2.0, sh=-0.18)
    c.rect(22, 14 + dy, 22, 16 + dy, NOSTR)
    c.rect(26, 14 + dy, 26, 16 + dy, NOSTR)
    # mouth
    if mood == "laugh":
        c.rect(21, 18 + dy, 27, 20 + dy, MAW)                 # roaring laugh
        c.rect(23, 20 + dy, 25, 20 + dy, TONGUE)
    else:
        c.line([(21, 19 + dy), (22, 19 + dy), (23, 19 + dy), (24, 18 + dy)], MOUTH)


def head_up(c, dy=0):
    c.tri((15, 2 + dy), 10 + dy, 13, 21, PIG)
    c.tri((33, 2 + dy), 10 + dy, 27, 35, PIG, sh=0.18)
    c.tri((16, 4 + dy), 9 + dy, 15, 19, PIG, sh=0.5)
    c.tri((32, 4 + dy), 9 + dy, 30, 33, PIG, sh=0.55)
    c.oval(24, 13 + dy, 9.2, 7.6, PIG, power=2.2)
    c.line([(21, 18 + dy), (23, 19 + dy), (25, 19 + dy), (27, 18 + dy)], PIG[3])


def head_side(c, dy=0, mood="smug"):
    """Profile: the snout juts out front."""
    c.tri((18, 1 + dy), 8 + dy, 14, 22, PIG)                  # near ear
    c.tri((18, 3 + dy), 7 + dy, 16, 20, PIG, sh=0.4)
    c.tri((26, 2 + dy), 8 + dy, 23, 29, PIG, sh=0.25)         # far ear
    c.oval(23, 12.5 + dy, 8.6, 7.2, PIG, power=2.2)
    c.oval(31.5, 14.5 + dy, 3.8, 2.7, PIG, power=2.0, sh=-0.14)  # snout mass
    c.rect(34, 13 + dy, 34, 15 + dy, NOSTR)                   # forward nostril
    if mood == "smug":
        c.rect(26, 9 + dy, 27, 10 + dy, EYE_D)
        c.set(26, 9 + dy, GLINT)
        c.line([(25, 7 + dy), (27, 7 + dy), (28, 8 + dy)], BROW)
    c.line([(28, 17 + dy), (30, 17 + dy), (31, 16 + dy)], MOUTH)


# ---- full poses --------------------------------------------------------------------

def pig_down(c, bob=0, lift_l=0, lift_r=0, swing=0, tail_dx=0, mood="smug"):
    curly_tail_down(c, tail_dx)
    legs(c, lift_l, lift_r)
    body_down(c, bob)
    arms_down(c, bob, swing, -swing)
    head_down(c, bob, mood)
    c.outline()


def pig_up(c, bob=0, lift_l=0, lift_r=0, swing=0, point=False):
    legs(c, lift_l, lift_r)
    c.oval(24, 29 + bob, 8.4, 7.6, PIG, power=2.2)
    c.band(17, 21 + bob, 30, 22 + bob, RED)                   # kerchief from behind
    # curly tail at his rear, center-low
    for (px_, py_) in ((24, 35.5), (25.5, 34), (27, 35.5), (25.5, 36.5)):
        c.oval(px_, py_ + bob, 1.2, 1.2, PIG, sh=0.22)
    if point:
        arms_down(c, bob, 0, 0)
    else:
        arms_down(c, bob, swing, -swing)
    head_up(c, bob)
    if point:                                                 # trotter thrust skyward
        c.band(31, 5 + bob, 34, 22 + bob, PIG, sh=0.12)
        for y in range(5 + bob, 23 + bob, 2):
            c.set(31, y, PIG[3])                              # arm/body separation
        c.band(31, 1 + bob, 34, 4 + bob, HOOF)
    c.outline()


def pig_side(c, bob=0, front_dx=0, back_dx=0, lift_f=0, lift_b=0):
    # curly tail behind
    for (px_, py_) in ((14, 25), (12.5, 23.5), (11, 25), (12.5, 26.5)):
        c.oval(px_, py_ + bob, 1.2, 1.2, PIG, sh=0.15)
    for (x0, x1, dx_, lift) in ((17, 20, back_dx, lift_b), (25, 28, front_dx, lift_f)):
        c.band(x0 + dx_, 36 - lift, x1 + dx_, FEET - 3 - lift, PIG, sh=0.12)
        c.band(x0 + dx_, FEET - 2 - lift, x1 + dx_, FEET - lift, HOOF)
    c.oval(23, 29 + bob, 8.8, 7.4, PIG, power=2.2)            # barrel
    c.band(16, 21 + bob, 29, 23 + bob, RED)
    c.band(20 + front_dx // 2, 24 + bob, 23 + front_dx // 2, 30 + bob, PIG, sh=0.16)  # near arm
    c.band(20 + front_dx // 2, 31 + bob, 23 + front_dx // 2, 32 + bob, HOOF)
    head_side(c, bob)
    c.outline()


# ---- build ---------------------------------------------------------------------------
cells = [[Cell() for _ in range(COLS)] for _ in range(ROWS)]

walk_bob   = [0, -1, 0, -1]
walk_liftl = [2, 0, 0, 0]
walk_liftr = [0, 0, 2, 0]
walk_swing = [1, 0, -1, 0]
walk_tail  = [0, 1, 2, 1]
for i in range(4):
    pig_down(cells[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
             walk_swing[i], walk_tail[i])
    pig_up(cells[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i], walk_swing[i])
side_front = [3, 0, -3, 0]
side_back  = [-3, 0, 3, 0]
for i in range(4):
    pig_side(cells[2][i], walk_bob[i], side_front[i], side_back[i],
             1 if i == 0 else 0, 1 if i == 2 else 0)

pig_up(cells[3][0], 0, point=True)
pig_up(cells[3][1], -1, point=True)
pig_down(cells[3][2], 0, mood="laugh", tail_dx=2)
pig_down(cells[3][3], -1, mood="laugh", tail_dx=0)

W, H = COLS * CELL, ROWS * CELL
buf = bytearray(W * H * 4)
for r in range(ROWS):
    for ci in range(COLS):
        cell = cells[r][ci]
        for y in range(CELL):
            for x in range(CELL):
                p = cell.px[y][x]
                if p:
                    o = ((r * CELL + y) * W + (ci * CELL + x)) * 4
                    buf[o:o + 4] = bytes(p)

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += buf[y * W * 4:(y + 1) * W * 4]

def chunk(tag, data):
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

open(os.path.join(HERE, "schweinler_gen.png"), "wb").write(
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    + chunk(b"IEND", b""))
print(f"wrote schweinler_gen.png ({W}x{H})")
