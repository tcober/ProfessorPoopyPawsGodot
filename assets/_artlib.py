#!/usr/bin/env python3
"""LEGACY shim — being retired by the painted-scene art overhaul.

The shared core (constants, h2, pick, Img, PNG writer) moved to assets/_core.py;
new art is built on assets/_paint.py (scenes) and assets/_sprites.py (sheets).
This module re-exports the core plus the old Cell sprite canvas so the not-yet-
rewritten generators keep running. Deleted in the overhaul's final phase — do not
add new imports of this module.
"""
from _core import (  # noqa: F401 — re-exported for legacy generators
    ZONE_TILE, ZONE_CELL, ZONE_FEET, OW_TILE, OW_CELL, OW_FEET, ICON, VIEW,
    h2, pick, lerp, Img, write_png, write_cells,
)


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
