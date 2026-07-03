#!/usr/bin/env python3
"""Shared art library for the procedural pixel-art pipeline.

Single home for the code every `assets/_gen_*.py` generator used to copy-paste:
the PNG writer, the deterministic value noise, the 4-tone ramp dither, and the
shaded drawing primitives (superellipse domes, garment panels, outlines).

Also the single source of truth for the game's scale constants — the generators,
`assets/_check_art.py`, and docs/DESIGN.md's Scale Table must all agree with these.

Style contract (docs/DESIGN.md "Art Direction"): SNES composition at 2x pixel
density. Light from the upper-left, 4-tone material ramps whose shadows hue-shift
violet/teal (see assets/_palette.py), ordered dither only at tone-band edges,
per-material dark outlines, details that break the silhouette drawn after the
outline pass.
"""
import struct, zlib, os, math

# ---- canonical scale constants (keep in sync with docs/DESIGN.md) ---------------
ZONE_TILE = 32        # zone terrain tile
ZONE_CELL = 96        # zone character cell (Basil, Schweinler)
ZONE_FEET = 88        # feet baseline inside a zone cell
OW_TILE   = 32        # overworld terrain tile
OW_CELL   = 48        # overworld chibi travel cell
OW_FEET   = 42        # chibi feet baseline
ICON      = 64        # overworld landmark icon
VIEW      = (640, 360)

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
    as SNES banding instead of fine noise.
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

class Cell:
    """None-tracked sparse square canvas for sprites: shaded primitives + outline.

    `grain` feeds the dither (2 for 2x-density art). Outline colors are passed to
    outline() per sheet, not baked in.
    """

    def __init__(self, n, grain=1):
        self.n = n
        self.grain = grain
        self.px = [[None] * n for _ in range(n)]

    def set(self, x, y, c):
        if 0 <= x < self.n and 0 <= y < self.n:
            self.px[y][x] = c

    def get(self, x, y):
        if 0 <= x < self.n and 0 <= y < self.n:
            return self.px[y][x]
        return None

    def _pick(self, ramp, t, x, y):
        return pick(ramp, t, x, y, grain=self.grain)

    # -- shaded primitives ---------------------------------------------------------
    def oval(self, cx, cy, rx, ry, ramp, sh=0.0, power=2.0):
        """Filled superellipse shaded as a dome lit from the upper-left.
        sh biases the whole form darker (parts tucked in shadow)."""
        for y in range(int(cy - ry), int(cy + ry) + 2):
            for x in range(int(cx - rx), int(cx + rx) + 2):
                nx = (x - cx) / rx
                ny = (y - cy) / ry
                d = abs(nx) ** power + abs(ny) ** power
                if d > 1.0:
                    continue
                t = 0.42 + 0.30 * (nx * 0.55 + ny * 0.80) + 0.30 * d * d + sh
                self.set(x, y, self._pick(ramp, t, x, y))

    def cloth(self, x0, y0, x1, y1, ramp, round_=2, folds=(), sh=0.0):
        """Rounded garment panel, lit from the upper-left, with vertical folds."""
        w = max(1, x1 - x0)
        h = max(1, y1 - y0)
        for y in range(y0, y1 + 1):
            vy = (y - y0) / h
            for x in range(x0, x1 + 1):
                hx = (x - x0) / w
                ex = min(x - x0, x1 - x)
                ey = min(y - y0, y1 - y)
                if ex + ey < round_:
                    continue
                t = 0.22 + 0.33 * hx + 0.38 * vy + sh
                for fx in folds:
                    if abs(x - fx) < 1.5:
                        t += 0.22
                self.set(x, y, self._pick(ramp, t, x, y))

    def tri(self, apex, base_y, x0, x1, ramp_or_color, sh=0.0):
        ax, ay = apex
        span = max(1, base_y - ay)
        for y in range(ay, base_y + 1):
            f = (y - ay) / span
            xl = round(ax + (x0 - ax) * f)
            xr = round(ax + (x1 - ax) * f)
            for x in range(min(xl, xr), max(xl, xr) + 1):
                if isinstance(ramp_or_color, list):
                    t = 0.30 + 0.45 * f + 0.25 * (x - xl) / max(1, xr - xl) + sh
                    self.set(x, y, self._pick(ramp_or_color, t, x, y))
                else:
                    self.set(x, y, ramp_or_color)

    def line(self, pts, c):
        for (x, y) in pts:
            self.set(x, y, c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    # -- finishing pass --------------------------------------------------------------
    def outline(self, outs, fallback):
        """1px silhouette outline; color chosen per neighbouring material via `outs`
        (fill-color -> outline-color). Existing outline pixels are not re-outlined."""
        out_set = set(outs.values())
        out_set.add(fallback)
        edge = []
        for y in range(self.n):
            for x in range(self.n):
                if self.px[y][x] is not None:
                    continue
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    p = self.get(nx, ny)
                    if p and p[3] == 255 and p not in out_set:
                        edge.append((x, y, outs.get(p, fallback)))
                        break
        for x, y, c in edge:
            self.px[y][x] = c


class Img:
    """Dense RGBA canvas for tiles, props and backdrops."""

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
    """Compose a [rows][cols] grid of Cell objects into one sheet PNG."""
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
