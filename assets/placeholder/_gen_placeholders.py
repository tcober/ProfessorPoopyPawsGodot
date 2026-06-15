#!/usr/bin/env python3
"""Generate throwaway placeholder PNGs for the vertical slice (pure stdlib, no deps).

These are NOT final art. They exist only so the slice runs and is testable. Replace with
real sprite sheets per docs/DESIGN.md ("Asset Specs"). Re-run: python3 _gen_placeholders.py
"""
import struct, zlib, os

HERE = os.path.dirname(os.path.abspath(__file__))


class Img:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.px = [[(0, 0, 0, 0)] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.px[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1):
            for x in range(x0, x1):
                self.set(x, y, c)

    def disc(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def save(self, path):
        raw = bytearray()
        for row in self.px:
            raw.append(0)  # filter type 0
            for (r, g, b, a) in row:
                raw += bytes((r, g, b, a))

        def chunk(tag, data):
            c = tag + data
            return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0)
        png = (b"\x89PNG\r\n\x1a\n"
               + chunk(b"IHDR", ihdr)
               + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
               + chunk(b"IEND", b""))
        with open(path, "wb") as f:
            f.write(png)
        print("wrote", os.path.relpath(path, HERE), f"({self.w}x{self.h})")


# --- Player: 32x32, science-cat-ish steel-blue body w/ lab coat + face (faces "down") ---
COAT = (220, 228, 235, 255)
BODY = (90, 120, 160, 255)
DARK = (40, 55, 80, 255)
EYE = (25, 25, 30, 255)
p = Img(32, 32)
p.rect(11, 4, 21, 9, BODY)            # head
p.set(11, 3, BODY); p.set(12, 2, BODY); p.set(13, 3, BODY)  # left ear
p.set(20, 3, BODY); p.set(19, 2, BODY); p.set(18, 3, BODY)  # right ear
p.rect(13, 6, 15, 8, EYE)             # eyes
p.rect(17, 6, 19, 8, EYE)
p.rect(10, 9, 22, 26, COAT)           # lab coat body
p.rect(15, 9, 17, 26, DARK)           # coat seam
p.rect(8, 12, 11, 22, BODY)           # left arm
p.rect(21, 12, 24, 22, BODY)          # right arm
p.rect(12, 26, 16, 30, DARK)          # legs
p.rect(16, 26, 20, 30, DARK)
p.save(os.path.join(HERE, "player_placeholder.png"))

# --- Slime: 24x24 green blob ---
s = Img(24, 24)
GEL = (90, 190, 110, 255)
GEL_D = (55, 140, 80, 255)
s.disc(12, 14, 9, GEL)
s.rect(3, 14, 21, 22, GEL)
s.rect(3, 21, 21, 22, GEL_D)
s.rect(8, 10, 10, 13, EYE)            # eyes
s.rect(14, 10, 16, 13, EYE)
s.save(os.path.join(HERE, "slime_placeholder.png"))

# --- Hearts: 48x16 strip, 3 cells: full | half | empty ---
RED = (220, 60, 70, 255)
RED_D = (150, 30, 45, 255)
GREY = (70, 70, 80, 255)


def heart(img, ox, fill_left, fill_right):
    # blocky 16x16 heart centered in cell at x-offset ox
    shape = [
        "..XX..XX..",
        ".XXXXXXXX.",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        "XXXXXXXXXX",
        ".XXXXXXXX.",
        "..XXXXXX..",
        "...XXXX...",
        "....XX....",
    ]
    sx, sy = ox + 3, 3
    mid = 5
    for j, line in enumerate(shape):
        for i, ch in enumerate(line):
            if ch == "X":
                left = i < mid
                col = (fill_left if left else fill_right)
                img.set(sx + i, sy + j, col)


h = Img(48, 16)
heart(h, 0, RED, RED)        # full
heart(h, 16, RED, GREY)      # half
heart(h, 32, GREY, GREY)     # empty
h.save(os.path.join(HERE, "hearts.png"))
