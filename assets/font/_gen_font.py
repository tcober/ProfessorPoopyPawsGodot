#!/usr/bin/env python3
"""Bake the native 5x7 pixel font (assets/_pixfont.py — caps/digits/punctuation)
into a BMFont bitmap font Godot can load: assets/font/pixel_font.png +
pixel_font.fnt.

BMFont size=8 so Labels with font_size=8 render 1:1 at the 320x180 SNES-density
viewport (advance 6, lineHeight 9 — CT-chunk text scale). All UI text is
uppercase; a lowercase set returns with the dialog system if story scenes do.
Re-run: python3 assets/font/_gen_font.py
"""
import struct, zlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _pixfont import GLYPHS, CHAR_W, CHAR_H, ADVANCE

BASE = 7             # px from line top to baseline (full glyph height)
CELL_W, CELL_H = CHAR_W + 1, CHAR_H + 1
PER_ROW = 16
chars = sorted(GLYPHS.keys())
rows = (len(chars) + PER_ROW - 1) // PER_ROW
W, H = PER_ROW * CELL_W, rows * CELL_H

buf = bytearray(W * H * 4)
entries = []
WHITE = (255, 255, 255, 255)
for i, ch in enumerate(chars):
    gx, gy = (i % PER_ROW) * CELL_W, (i // PER_ROW) * CELL_H
    for ry, row in enumerate(GLYPHS[ch]):
        for rx, bit in enumerate(row):
            if bit == "X":
                o = ((gy + ry) * W + gx + rx) * 4
                buf[o:o + 4] = bytes(WHITE)
    entries.append((ord(ch), gx, gy))

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += buf[y * W * 4:(y + 1) * W * 4]

def chunk(tag, data):
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

open(os.path.join(HERE, "pixel_font.png"), "wb").write(
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    + chunk(b"IEND", b""))

lines = [
    'info face="PoopyPixel" size=8 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=1 padding=0,0,0,0 spacing=0,0 outline=0',
    f'common lineHeight=9 base={BASE} scaleW={W} scaleH={H} pages=1 packed=0 alphaChnl=1 redChnl=0 greenChnl=0 blueChnl=0',
    'page id=0 file="pixel_font.png"',
    f"chars count={len(entries)}",
]
for cid, gx, gy in sorted(entries):
    lines.append(
        f"char id={cid} x={gx} y={gy} width={CHAR_W} height={CHAR_H} "
        f"xoffset=0 yoffset=0 xadvance={ADVANCE} page=0 chnl=15")
open(os.path.join(HERE, "pixel_font.fnt"), "w").write("\n".join(lines) + "\n")
print(f"wrote pixel_font.png ({W}x{H}) + pixel_font.fnt ({len(entries)} chars)")
