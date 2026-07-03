#!/usr/bin/env python3
"""Repack the irregular basil_sheet.png into a clean 288x336 (48x48, 6x7) sheet that
matches entities/player/player_frames.tres. Each chosen cat is height-normalized,
centered on its alpha centroid (clipping laser beams rather than the cat), and
foot-anchored. Re-run: python3 _repack_basil.py

NOTE: basil_sheet.png has no clean back/up view, so walk_up reuses front-facing frames
as a placeholder. Replace with real back-view art later — no code/tres change needed.
"""
import struct, zlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "basil_sheet.png")
DST = os.path.join(HERE, "basil_packed.png")

CELL = 48
PAD = 2
COLS, PACK_ROWS = 6, 7


def load(path):
    d = open(path, "rb").read(); i = 8; W = H = 0; idat = b""
    while i < len(d):
        ln = struct.unpack(">I", d[i:i+4])[0]; tag = d[i+4:i+8]; data = d[i+8:i+8+ln]; i += 12+ln
        if tag == b"IHDR": W, H = struct.unpack(">II", data[:8])
        elif tag == b"IDAT": idat += data
        elif tag == b"IEND": break
    raw = zlib.decompress(idat); stride = W*4; prev = bytearray(stride); out = bytearray(); pos = 0
    for y in range(H):
        f = raw[pos]; pos += 1; line = bytearray(raw[pos:pos+stride]); pos += stride
        if f == 1:
            for x in range(4, stride): line[x] = (line[x]+line[x-4]) & 255
        elif f == 2:
            for x in range(stride): line[x] = (line[x]+prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x-4] if x >= 4 else 0; line[x] = (line[x]+((a+prev[x])>>1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x-4] if x >= 4 else 0; b = prev[x]; c = prev[x-4] if x >= 4 else 0
                p = a+b-c; pa = abs(p-a); pb = abs(p-b); pc = abs(p-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x]+pr) & 255
        out += line; prev = line
    return W, H, bytes(out)


def save(path, W, H, px):
    raw = bytearray()
    for y in range(H):
        raw.append(0); raw += px[y*W*4:(y+1)*W*4]
    def ch(t, d): c = t+d; return struct.pack(">I", len(d))+c+struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n"
        + ch(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
        + ch(b"IDAT", zlib.compress(bytes(raw), 9)) + ch(b"IEND", b""))


W, H, px = load(SRC)
def A(x, y): return px[(y*W+x)*4+3] if (0 <= x < W and 0 <= y < H) else 0
def rgba(x, y):
    o = (y*W+x)*4; return px[o], px[o+1], px[o+2], px[o+3]

ROW_BANDS = [(15, 149), (153, 305), (308, 460), (473, 613), (628, 767)]


def figures(band):
    y0, y1 = band
    colsum = [sum(A(x, y) for y in range(y0, y1+1, 2)) for x in range(W)]
    thr = max(colsum)*0.04
    figs = []; run = None
    for x, v in enumerate(colsum):
        if v > thr:
            run = [x, x] if run is None else [run[0], x]
        else:
            if run and run[1]-run[0] > 20: figs.append(tuple(run))
            run = None
    if run and run[1]-run[0] > 20: figs.append(tuple(run))
    return figs

FIGS = [figures(b) for b in ROW_BANDS]

# Animation layout -> list of (source_row, figure_index). Must match player_frames.tres.
# Source views identified by inspection:
#   sheet row0 figs0-5 = FRONT (down)         sheet row0 figs7-8 = side-right shoot
#   sheet row1 figs0-5 = side facing LEFT     (unused: code mirrors the RIGHT row)
#   sheet row2 figs0-5 = side facing RIGHT    sheet row2 figs6-8 = BACK (up), 7-8 firing up
#   sheet row3 figs0-2 = BACK standing        sheet row3 figs3-6 = side-right shoot
#   sheet row4 figs0-3 = FRONT firing down    sheet row4 figs4-7 = BACK firing
# The cat's native side art faces RIGHT; player.gd flips_h only when facing LEFT.
# NOTE: sheet row0 mixes front and back poses (figs 0,3,4 are FRONT; 1,2,5 are BACK),
# so walk_down uses only the front figs; walk_up uses the consistent back set in row3.
LAYOUT = [
    [(0, 0), (0, 3), (0, 4), (0, 0), (0, 3), (0, 4)],   # row0 walk_down  (front / DOWN)
    [(3, 0), (3, 1), (3, 2), (3, 0), (3, 1), (3, 2)],   # row1 walk_up    (back / UP)
    [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5)],   # row2 walk_side  (side, native RIGHT)
    [(4, 0), (4, 1), (4, 2), (4, 1)],                   # row3 shoot_down (front; drop twisted diagonal fig3)
    [(2, 7), (2, 8), (2, 7), (2, 8)],                   # row4 shoot_up   (back firing; drop dead standing fig6)
    [(3, 3), (3, 4), (3, 5), (3, 6)],                   # row5 shoot_side (side RIGHT firing)
    [(0, 0), (0, 3)],                                   # row6 hurt       (front flinch)
]

OUT_W, OUT_H = COLS*CELL, PACK_ROWS*CELL
out = bytearray(OUT_W*OUT_H*4)


def tight_bbox(fx0, fx1, fy0, fy1):
    minx = miny = 10**9; maxx = maxy = -1
    for y in range(fy0, fy1+1):
        for x in range(fx0, fx1+1):
            if A(x, y) > 32:
                minx = min(minx, x); maxx = max(maxx, x)
                miny = min(miny, y); maxy = max(maxy, y)
    return minx, miny, maxx, maxy


def centroid_x(fx0, fx1, fy0, fy1):
    sw = 0.0; sx = 0.0
    for y in range(fy0, fy1+1, 2):
        for x in range(fx0, fx1+1):
            a = A(x, y)
            if a > 32:
                sw += a; sx += a*x
    return sx/sw if sw else (fx0+fx1)/2


def place(cell_col, cell_row, src_row, fig_idx):
    fx0, fx1 = FIGS[src_row][fig_idx]
    fy0, fy1 = ROW_BANDS[src_row]
    minx, miny, maxx, maxy = tight_bbox(fx0, fx1, fy0, fy1)
    if maxy < 0:
        return
    cx = centroid_x(fx0, fx1, fy0, fy1)
    inner = CELL - 2*PAD
    s = inner / float(maxy - miny + 1)          # scale to fit height
    dx0 = cell_col*CELL; dy0 = cell_row*CELL
    feet_dest = CELL - PAD                       # feet near bottom of cell
    for dy in range(CELL):
        # source y so that feet_dest maps to maxy
        sy = int(round(maxy - (feet_dest - dy)/s))
        for dx in range(CELL):
            sx = int(round(cx + (dx - CELL/2.0)/s))
            if fx0 <= sx <= fx1 and fy0 <= sy <= fy1 and A(sx, sy) > 16:
                r, g, b, a = rgba(sx, sy)
                # Strip the painted-in laser beam (green core + purple/magenta halo) so
                # the live bolt + muzzle flash are the only laser and the firing frames
                # don't show a stale diagonal beam after the shot has left. The cat's
                # grays/browns/cream keep green ~= the other channels, so this is safe.
                is_green = g >= 140 and (g - r) >= 25 and (b - g) <= 60
                is_purple = b >= 100 and (r - g) >= 15 and (b - g) >= 20
                if is_green or is_purple:
                    continue
                o = ((dy0+dy)*OUT_W + (dx0+dx))*4
                out[o:o+4] = bytes((r, g, b, a))


for ri, anim in enumerate(LAYOUT):
    for ci, (sr, fi) in enumerate(anim):
        if fi < len(FIGS[sr]):
            place(ci, ri, sr, fi)

save(DST, OUT_W, OUT_H, bytes(out))
print(f"wrote {os.path.relpath(DST, HERE)} ({OUT_W}x{OUT_H})")
