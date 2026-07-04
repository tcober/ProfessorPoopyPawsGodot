#!/usr/bin/env python3
"""Core of the procedural art pipeline: canvases, PNG writer, hash noise, scale
constants. Shared by the painted-scene kit (_paint.py), the sprite kit
(_sprites.py) and every assets/_gen_*.py generator.

Single source of truth for the game's scale constants — the generators,
assets/_check_art.py and docs/DESIGN.md's Scale Table must all agree with these.
Stdlib-only (no PIL/numpy) is a pipeline invariant; determinism comes from h2().
"""
import struct, zlib, os

# ---- canonical scale constants (keep in sync with docs/DESIGN.md) ---------------
# TRUE SNES DENSITY (the 2026-07 CT-chunk restart): 384x216 viewport (16:9 —
# fills a widescreen TV, integer-scales 5x to 1920x1080), 16px tiles, 48px
# character cells with a ~32px figure — Chrono Trigger proportions, every pixel
# deliberate. ~24x13.5 tiles visible; the dev window runs 3x at 1152x648.
ZONE_TILE = 16        # zone terrain tile (collision/logic grid; paint is gridless)
ZONE_CELL = 48        # zone character cell (Basil)
ZONE_FEET = 44        # feet baseline inside a zone cell
OW_TILE   = 16        # overworld terrain tile
OW_CELL   = 24        # overworld chibi travel cell
OW_FEET   = 21        # chibi feet baseline
ICON      = 32        # overworld landmark icon
VIEW      = (384, 216)

# ---- deterministic value noise ---------------------------------------------------

def h2(x, y, salt=0):
    """Stable per-pixel hash in 0..255 — keeps re-runs byte-identical."""
    n = (x * 374761393 + y * 668265263 + salt * 2246822519) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return (n ^ (n >> 16)) & 0xFF

# ---- ramp shading ------------------------------------------------------------------

def pick(ramp, t, x, y, lo=0.45, hi=0.58, grain=1):
    """t in 0..1 (0 = lit, 1 = shadow) -> ramp tone, ordered-dithered at band edges.

    grain=2 dithers in 2x2 blocks — use for 2x-density art so the checker reads
    as SNES banding instead of fine noise. (Sprite shading; terrain uses
    _paint.tone(), whose jittered bands avoid checkerboard fields entirely.)
    """
    if grain > 1:
        x, y = x // grain, y // grain
    n = len(ramp) - 1
    b = max(0.0, min(n - 0.001, t * n))
    i = int(b)
    frac = b - i
    if frac > hi or (lo < frac <= hi and (x + y) % 2 == 0):
        i += 1
    return ramp[min(n, i)]


def lerp(c0, c1, t):
    return tuple(round(c0[i] + (c1[i] - c0[i]) * t) for i in range(len(c0)))

# ---- canvases ----------------------------------------------------------------------

class Img:
    """Dense RGBA canvas for scenes, props and backdrops."""

    def __init__(self, w, h, fill=None):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 4)
        if fill:
            self.rect(0, 0, w - 1, h - 1, fill)

    def put(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 4
            self.buf[o:o + 4] = bytes(c)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 4
            return tuple(self.buf[o:o + 4])
        return (0, 0, 0, 0)

    def mix(self, x, y, c, a):
        """Alpha-blend color c at strength a (0..1) over the existing pixel."""
        base = self.get(x, y)
        self.put(x, y, tuple(round(base[i] + (c[i] - base[i]) * a) for i in range(3)) + (max(base[3], c[3]),))

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(x, y, c)

    def oval(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 2):
            for x in range(int(cx - rx), int(cx + rx) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.put(x, y, c)

    def blit_cell(self, cell, ox, oy):
        for y in range(cell.n):
            for x in range(cell.n):
                p = cell.px[y][x]
                if p:
                    self.put(ox + x, oy + y, p)

    def save(self, path):
        write_png(path, self.w, self.h, self.buf)

# ---- PNG output --------------------------------------------------------------------

def _chunk(tag, data):
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def write_png(path, w, h, buf):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += buf[y * w * 4:(y + 1) * w * 4]
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    open(path, "wb").write(png)
    print(f"wrote {os.path.basename(path)} ({w}x{h})")


def write_cells(path, cells, cell_size):
    """Compose a [rows][cols] grid of Cell/Sprite objects into one sheet PNG."""
    rows, cols = len(cells), len(cells[0])
    w, h = cols * cell_size, rows * cell_size
    buf = bytearray(w * h * 4)
    for r in range(rows):
        for ci in range(cols):
            cell = cells[r][ci]
            for y in range(cell_size):
                for x in range(cell_size):
                    p = cell.px[y][x]
                    if p:
                        o = ((r * cell_size + y) * w + (ci * cell_size + x)) * 4
                        buf[o:o + 4] = bytes(p)
    write_png(path, w, h, buf)
