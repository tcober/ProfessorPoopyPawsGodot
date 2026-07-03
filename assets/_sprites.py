#!/usr/bin/env python3
"""Sprite construction kit — the from-scratch successor to _artlib.Cell.

Everything character-sized is built here: a None-tracked sparse canvas
(`Sprite`, write_cells-compatible), volume primitives (`ball` superellipse dome
with a steerable light vector, `capsule` tapered limbs/tails — the silhouette
upgrade over rectangle limbs, `panel` garment with curved hem + fold bands,
plus tri/line/rect/px), CT-style finishing passes (`cluster_shade` merges lone
dither pixels into 2-3px tone clusters, `despeckle` shaves 1px silhouette
jaggies, `outline` per-material dark edges, `crease` interior lines drawn after
outlining), and `Rig` — named part anchors with per-frame offsets so a walk
cycle animates as ONE body instead of six slightly different redraws.

Shading model: 4-tone _palette ramps; tone selection is cluster-jittered (2px
hash clusters, like _paint.tone) instead of ordered-dithered, so band edges
break into organic clumps and checkerboard fields never appear. Light defaults
to the upper-left but is a parameter — recoil poses and rim accents can move it.

Stdlib-only; deterministic via _core.h2. Used by assets/_gen_*_sprites.py,
_gen_overworld_actors.py and _gen_fx.py.
"""
import math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import h2

LIGHT = (-0.60, -0.80)   # default light direction (points toward the source: upper-left)


class Sprite:
    """None-tracked sparse square canvas. Same px[y][x] interface as the old
    Cell so _core.write_cells / Img.blit_cell compose it unchanged."""

    def __init__(self, n, grain=2, salt=0):
        self.n = n
        self.grain = max(1, grain)
        self.salt = salt
        self.px = [[None] * n for _ in range(n)]

    # -- pixels ---------------------------------------------------------------------
    def set(self, x, y, c):
        if 0 <= x < self.n and 0 <= y < self.n:
            self.px[int(y)][int(x)] = c

    def get(self, x, y):
        if 0 <= x < self.n and 0 <= y < self.n:
            return self.px[int(y)][int(x)]
        return None

    def tone(self, ramp, t, x, y, jitter=0.85):
        """Ramp tone for t in 0..1 (0 = lit) with cluster-jittered band edges.

        The jitter is hashed on grain-sized clusters (2x2 at grain=2), so a band
        edge dissolves into 2-3px clumps — the CT texture — never a checkerboard.
        """
        n = len(ramp) - 1
        g = self.grain
        q = t * n + (h2(x // g, y // g, self.salt) - 127.5) * (jitter / 255.0)
        i = int(q + 0.5)
        if i < 0:
            i = 0
        elif i > n:
            i = n
        return ramp[i]

    # -- volume primitives ------------------------------------------------------------
    def ball(self, cx, cy, rx, ry, ramp, sh=0.0, power=2.0, light=LIGHT,
             wrap=0.30, curve=0.28):
        """Filled superellipse shaded as a dome. `light` is the direction toward
        the light source; `sh` biases the whole form darker (tucked in shadow);
        `wrap` is diffuse strength, `curve` the edge falloff."""
        lx, ly = light
        for y in range(int(cy - ry), int(cy + ry) + 2):
            ny = (y - cy) / ry
            for x in range(int(cx - rx), int(cx + rx) + 2):
                nx = (x - cx) / rx
                d = abs(nx) ** power + abs(ny) ** power
                if d > 1.0:
                    continue
                lam = nx * lx + ny * ly            # >0 on the lit side
                t = 0.46 - wrap * lam + curve * d * d + sh
                self.set(x, y, self.tone(ramp, t, x, y))

    def capsule(self, x0, y0, x1, y1, r0, r1, ramp, sh=0.0, light=LIGHT,
                wrap=0.34, curve=0.24, end_sh=0.0):
        """Tapered capsule limb/tail from (x0,y0,r0) to (x1,y1,r1), shaded as a
        lit cylinder with round caps. `end_sh` darkens toward the far end."""
        lx, ly = light
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        if L2 == 0:
            L2 = 1.0
        rmax = max(r0, r1) + 1
        for y in range(int(min(y0, y1) - rmax), int(max(y0, y1) + rmax) + 2):
            for x in range(int(min(x0, x1) - rmax), int(max(x0, x1) + rmax) + 2):
                u = ((x - x0) * dx + (y - y0) * dy) / L2
                if u < 0.0:
                    u = 0.0
                elif u > 1.0:
                    u = 1.0
                px_, py_ = x0 + dx * u, y0 + dy * u
                r = r0 + (r1 - r0) * u
                qx, qy = x - px_, y - py_
                q = math.sqrt(qx * qx + qy * qy) / max(0.6, r)
                if q > 1.0:
                    continue
                nx, ny = qx / max(0.6, r), qy / max(0.6, r)
                lam = nx * lx + ny * ly
                t = 0.46 - wrap * lam + curve * q * q + sh + end_sh * u
                self.set(x, y, self.tone(ramp, t, x, y))

    def panel(self, cx, y0, y1, half_top, half_bot, ramp, hem_curve=2, folds=(),
              fold_w=1.4, sh=0.0, light=LIGHT, round_top=2, hem_band=2, wrap=0.20):
        """Garment panel: straight top, sides lerping half_top->half_bot, hem
        curved by hem_curve (>0 dips at center, <0 lifts). Folds are soft dark
        vertical bands at the given x positions; the hem gets a dark turn-under
        band. Shading wraps gently around the column like loose cloth."""
        lx, _ly = light
        h = max(1, y1 - y0)
        for y in range(y0, y1 + max(0, hem_curve) + 1):
            vy = (y - y0) / h
            half = half_top + (half_bot - half_top) * min(1.0, vy)
            x_lo = int(math.floor(cx - half))
            x_hi = int(math.ceil(cx + half))
            for x in range(x_lo, x_hi + 1):
                xn = (x - cx) / max(1.0, half)
                if abs(xn) > 1.0:
                    continue
                hem_y = y1 + hem_curve * (1.0 - xn * xn)
                if y > hem_y:
                    continue
                if (y - y0) < round_top and abs(xn) > 1.0 - (round_top - (y - y0)) / max(1.0, half):
                    continue
                t = 0.42 - wrap * (xn * lx) + 0.14 * vy + sh
                for fx in folds:
                    d = abs(x - fx)
                    if d < fold_w:
                        t += 0.26
                    elif d < fold_w + 1.2:
                        t += 0.10
                if y > hem_y - hem_band:
                    t += 0.30
                if xn > 0.82:
                    t += 0.22                       # turned-under dark edge
                elif xn < -0.86:
                    t -= 0.08                       # lit edge catch
                self.set(x, y, self.tone(ramp, t, x, y))

    def tri(self, apex, base_y, x0, x1, ramp_or_color, sh=0.0, light=LIGHT, wrap=0.30):
        """Filled triangle from apex down to base_y spanning x0..x1; shaded when
        given a ramp, flat when given a color."""
        ax, ay = apex
        span = max(1, base_y - ay)
        flat = not isinstance(ramp_or_color, list)
        lx, ly = light
        for y in range(ay, base_y + 1):
            f = (y - ay) / span
            xl = round(ax + (x0 - ax) * f)
            xr = round(ax + (x1 - ax) * f)
            for x in range(min(xl, xr), max(xl, xr) + 1):
                if flat:
                    self.set(x, y, ramp_or_color)
                else:
                    w = max(1, abs(xr - xl))
                    nx = (x - (xl + xr) / 2) / w * 2.0
                    lam = nx * lx + (f - 0.5) * 2.0 * ly
                    t = 0.46 - wrap * lam + sh
                    self.set(x, y, self.tone(ramp_or_color, t, x, y))

    def line(self, pts, c):
        for (x, y) in pts:
            self.set(x, y, c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.set(x, y, c)

    def blob(self, cx, cy, rx, ry, c, power=2.0):
        """Flat-color superellipse (eyes, glints, socket shapes)."""
        for y in range(int(cy - ry), int(cy + ry) + 2):
            ny = (y - cy) / ry
            for x in range(int(cx - rx), int(cx + rx) + 2):
                nx = (x - cx) / rx
                if abs(nx) ** power + abs(ny) ** power <= 1.0:
                    self.set(x, y, c)

    # -- finishing passes --------------------------------------------------------------
    def cluster_shade(self, ramps, passes=2):
        """Merge isolated dither pixels into 2-3px tone clusters (the CT look).

        A pixel with zero same-color 4-neighbours is voted into the majority
        neighbour tone, but only within its own material ramp — single-pixel
        details of a different material (glints, noses) are never eaten.
        """
        fam = {}
        for i, r in enumerate(ramps):
            for c in r:
                fam[c] = i
        for _ in range(passes):
            changed = False
            for y in range(self.n):
                row = self.px[y]
                for x in range(self.n):
                    c = row[x]
                    if c is None or c not in fam:
                        continue
                    same = 0
                    counts = {}
                    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                        p = self.get(nx, ny)
                        if p is None:
                            continue
                        if p == c:
                            same += 1
                        elif fam.get(p, -9) == fam[c]:
                            counts[p] = counts.get(p, 0) + 1
                    if same == 0 and counts:
                        best, n_best = max(counts.items(), key=lambda kv: kv[1])
                        if n_best >= 3:
                            row[x] = best
                            changed = True
            if not changed:
                break

    def despeckle(self, min_neighbors=2, passes=2):
        """Shave 1px jaggies off the silhouette: filled pixels with fewer than
        `min_neighbors` filled 4-neighbours are cleared. Run BEFORE outline();
        draw deliberate specks (whiskers, droplets) after finishing."""
        for _ in range(passes):
            drop = []
            for y in range(self.n):
                row = self.px[y]
                for x in range(self.n):
                    if row[x] is None:
                        continue
                    cnt = 0
                    for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                        if self.get(nx, ny) is not None:
                            cnt += 1
                    if cnt < min_neighbors:
                        drop.append((x, y))
            for x, y in drop:
                self.px[y][x] = None
            if not drop:
                break

    def outline(self, outs, fallback):
        """1px silhouette outline; color per neighbouring material via `outs`
        (fill color -> outline color). Existing outline pixels aren't re-edged."""
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

    def crease(self, pts, color):
        """Interior detail line drawn after outlining — only lands on already
        filled pixels, so creases can never leak past the silhouette."""
        for (x, y) in pts:
            if self.get(x, y) is not None:
                self.set(x, y, color)


# ---- rig: one body, many frames ------------------------------------------------------

class Rig:
    """Named part anchors with per-frame offsets.

    Define the body ONCE as base anchor points; each frame asks for a pose with
    small named offsets. Part-drawing functions consume pose coordinates, so
    volumes and landmarks stay identical across the cycle — no per-frame redraw
    drift, which is what makes a generated walk read as one character.
    """

    def __init__(self, **anchors):
        self.base = dict(anchors)

    def pose(self, **offsets):
        """Anchor dict with (dx, dy) offsets applied; unknown names are new
        anchors (handy for frame-only props like a raised gun)."""
        p = dict(self.base)
        for name, d in offsets.items():
            if name in p:
                x, y = p[name]
                p[name] = (x + d[0], y + d[1])
            else:
                p[name] = d
        return p


def bob(i, amp=2.0, period=6, phase=0.0):
    """Sinusoidal body bob for frame i of a `period`-frame cycle."""
    return amp * math.sin(2.0 * math.pi * (i + phase) / period)
