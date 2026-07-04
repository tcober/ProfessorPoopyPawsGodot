#!/usr/bin/env python3
"""Painted-scene kit: composes each map as one ground image + one overlay image.

This is the antidote to the tiled look — there is no per-tile texture anywhere.
Texture fields (FBM value noise) span the whole scene, biome boundaries are the
warped zero-contours of distance fields built from the map's tile mask, and all
detail (flower clumps, tufts, pebbles, boulders, tree blobs) is stamped at
arbitrary pixel positions. The 32px grid survives only as collision data.

Paint-vs-collision tolerance rule (docs/DESIGN.md): boundary warp is clamped to
WARP_AMP <= 6px and solid paint may only overfill OUTWARD into walkable tiles
(never leave walkable-looking paint deep inside a solid cell); entity collision
shapes keep bodies far enough from solid tile edges that the overfill can never
read as standing on water/canopy.

Layering rule: pixels deeper than OVERLAY_DEPTH inside a solid region go to the
overlay image (drawn above entities); the fringe stays on the ground image so a
player hugging a tree wall draws in front of the near foliage and only tucks
under the deep canopy. Sprites never extend deeper than OVERLAY_DEPTH px into a
solid region, so occlusion can't go wrong.

Everything is deterministic from _core.h2 — re-runs are byte-identical.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _core import h2, Img, ZONE_TILE
from _palette import SCENES, ramp

WARP_AMP = 5.0        # px, boundary meander amplitude (must stay <= 6)
OVERLAY_DEPTH = 26.0  # px into a solid region where paint moves above entities

# ---- sampled float fields ----------------------------------------------------------


class Field:
    """Float grid at `step` px spacing with clamped bilinear sampling."""

    __slots__ = ("rows", "step", "inv", "umax", "vmax")

    def __init__(self, gw, gh, step, rows):
        self.rows = rows
        self.step = step
        self.inv = 1.0 / step
        self.umax = gw - 1.001
        self.vmax = gh - 1.001

    def sample(self, x, y):
        u = x * self.inv
        v = y * self.inv
        if u < 0.0:
            u = 0.0
        elif u > self.umax:
            u = self.umax
        if v < 0.0:
            v = 0.0
        elif v > self.vmax:
            v = self.vmax
        iu = int(u)
        iv = int(v)
        fu = u - iu
        fv = v - iv
        r0 = self.rows[iv]
        r1 = self.rows[iv + 1]
        a = r0[iu]
        b = r0[iu + 1]
        c = r1[iu]
        d = r1[iu + 1]
        return (a + (b - a) * fu) * (1.0 - fv) + (c + (d - c) * fu) * fv


def fbm(w, h, scale, octaves=4, salt=0, gain=0.5, lacunarity=2.0, step=1):
    """Multi-octave value noise Field over a w×h px area, values ~0..1.

    Row-cached lattice interpolation (the fast pure-Python form). `step` computes
    the field at reduced resolution for cheap broad fields (warp, macro light);
    keep step=1..2 for fine texture so octaves don't alias.
    """
    gw = w // step + 2
    gh = h // step + 2
    rows = [[0.0] * gw for _ in range(gh)]
    total = 0.0
    amp = 1.0
    freq = 1.0 / scale
    for o in range(octaves):
        so = salt * 31 + o * 97 + 1
        nlat = int((gw - 1) * step * freq) + 3
        sf = step * freq
        for j in range(gh):
            v = j * sf
            jy = int(v)
            ty = v - jy
            ty = ty * ty * (3.0 - 2.0 * ty)
            row0 = [h2(i, jy, so) for i in range(nlat)]
            row1 = [h2(i, jy + 1, so) for i in range(nlat)]
            out = rows[j]
            for i in range(gw):
                u = i * sf
                ix = int(u)
                tx = u - ix
                tx = tx * tx * (3.0 - 2.0 * tx)
                a = row0[ix]
                b = row0[ix + 1]
                c = row1[ix]
                d = row1[ix + 1]
                out[i] += amp * ((a + (b - a) * tx) * (1.0 - ty) + (c + (d - c) * tx) * ty)
        total += amp * 255.0
        amp *= gain
        freq *= lacunarity
    inv = 1.0 / total
    for j in range(gh):
        row = rows[j]
        for i in range(gw):
            row[i] *= inv
    return Field(gw, gh, step, rows)


def _blur_grid(grid, gw, gh, passes):
    for _ in range(passes):
        nxt = [row[:] for row in grid]
        for j in range(1, gh - 1):
            s0, s1, s2 = grid[j - 1], grid[j], grid[j + 1]
            nj = nxt[j]
            for i in range(1, gw - 1):
                nj[i] = (s0[i] + s1[i - 1] + s1[i] + s1[i + 1] + s2[i]) * 0.2
        grid = nxt
    return grid


def sdf_from_mask(mask, tile_px=ZONE_TILE, step=4, blur=2):
    """Signed distance Field (px; negative inside) to a tile-resolution bool mask.

    Chamfer (1, 1.4) two-pass transform on a step-px grid, then box-blurred to
    round the blocky tile corners; Painter.warped() adds the organic meander.
    """
    rows_t = len(mask)
    cols_t = len(mask[0])
    w = cols_t * tile_px
    h = rows_t * tile_px
    gw = w // step
    gh = h // step
    half = step // 2
    inside = [[mask[min(rows_t - 1, (j * step + half) // tile_px)]
               [min(cols_t - 1, (i * step + half) // tile_px)]
               for i in range(gw)] for j in range(gh)]
    INF = 1e9

    def chamfer(target):
        d = [[0.0 if inside[j][i] == target else INF for i in range(gw)] for j in range(gh)]
        for j in range(gh):
            dj = d[j]
            up = d[j - 1] if j > 0 else None
            for i in range(gw):
                v = dj[i]
                if i > 0 and dj[i - 1] + 1.0 < v:
                    v = dj[i - 1] + 1.0
                if up is not None:
                    if up[i] + 1.0 < v:
                        v = up[i] + 1.0
                    if i > 0 and up[i - 1] + 1.4 < v:
                        v = up[i - 1] + 1.4
                    if i < gw - 1 and up[i + 1] + 1.4 < v:
                        v = up[i + 1] + 1.4
                dj[i] = v
        for j in range(gh - 1, -1, -1):
            dj = d[j]
            dn = d[j + 1] if j < gh - 1 else None
            for i in range(gw - 1, -1, -1):
                v = dj[i]
                if i < gw - 1 and dj[i + 1] + 1.0 < v:
                    v = dj[i + 1] + 1.0
                if dn is not None:
                    if dn[i] + 1.0 < v:
                        v = dn[i] + 1.0
                    if i < gw - 1 and dn[i + 1] + 1.4 < v:
                        v = dn[i + 1] + 1.4
                    if i > 0 and dn[i - 1] + 1.4 < v:
                        v = dn[i - 1] + 1.4
                dj[i] = v
        return d

    d_in = chamfer(True)    # distance to nearest inside cell (0 inside)
    d_out = chamfer(False)  # distance to nearest outside cell (0 outside)
    sdf = [[(d_in[j][i] - d_out[j][i]) * step for i in range(gw)] for j in range(gh)]
    return Field(gw, gh, step, _blur_grid(sdf, gw, gh, blur))


def spline_points(waypoints, spacing=3.0):
    """Catmull-Rom samples (px) through waypoints, roughly `spacing` px apart."""
    pts = [waypoints[0]] + list(waypoints) + [waypoints[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        seg = max(2, int((abs(p2[0] - p1[0]) + abs(p2[1] - p1[1])) / spacing))
        for k in range(seg):
            u = k / seg
            u2, u3 = u * u, u * u * u
            out.append((
                0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3),
                0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3)))
    out.append(waypoints[-1])
    return out


def curve_field(w, h, waypoints, step=4, blur=1):
    """Unsigned distance Field (px) to a smooth spline through waypoints (px).

    The independence from the tile grid is the point: walkable-on-walkable paint
    (trails, streams under bridges, worn patches) can be genuinely curved.
    """
    gw = w // step
    gh = h // step
    on = [[False] * gw for _ in range(gh)]
    for (x, y) in spline_points(waypoints, spacing=step * 0.75):
        gx = int(x) // step
        gy = int(y) // step
        if 0 <= gx < gw and 0 <= gy < gh:
            on[gy][gx] = True
    INF = 1e9
    d = [[0.0 if on[j][i] else INF for i in range(gw)] for j in range(gh)]
    for j in range(gh):
        dj = d[j]
        up = d[j - 1] if j > 0 else None
        for i in range(gw):
            v = dj[i]
            if i > 0 and dj[i - 1] + 1.0 < v:
                v = dj[i - 1] + 1.0
            if up is not None:
                if up[i] + 1.0 < v:
                    v = up[i] + 1.0
                if i > 0 and up[i - 1] + 1.4 < v:
                    v = up[i - 1] + 1.4
                if i < gw - 1 and up[i + 1] + 1.4 < v:
                    v = up[i + 1] + 1.4
            dj[i] = v
    for j in range(gh - 1, -1, -1):
        dj = d[j]
        dn = d[j + 1] if j < gh - 1 else None
        for i in range(gw - 1, -1, -1):
            v = dj[i]
            if i < gw - 1 and dj[i + 1] + 1.0 < v:
                v = dj[i + 1] + 1.0
            if dn is not None:
                if dn[i] + 1.0 < v:
                    v = dn[i] + 1.0
                if i < gw - 1 and dn[i + 1] + 1.4 < v:
                    v = dn[i + 1] + 1.4
                if i > 0 and dn[i - 1] + 1.4 < v:
                    v = dn[i - 1] + 1.4
            dj[i] = v
    for j in range(gh):
        dj = d[j]
        for i in range(gw):
            dj[i] *= step
    return Field(gw, gh, step, _blur_grid(d, gw, gh, blur))

# ---- cluster-jittered tone quantization ---------------------------------------------
# Terrain shading: t is quantized to the ramp with 2px-cluster hash jitter, so
# band edges break into organic clumps — never the checkerboard of pick().


def tone_i(n, t, x, y, salt=7, jitter=0.55):
    """Ramp index (0..n) for t in 0..1, band edges jittered in 2px clusters."""
    q = t * n + (h2(x // 2, y // 2, salt) - 127.5) * (jitter / 255.0) * n * 0.5
    if q < 0.0:
        return 0
    if q > n:
        return n
    return int(q + 0.5)


def tone(ramp_, t, x, y, salt=7, jitter=0.55):
    return ramp_[tone_i(len(ramp_) - 1, t, x, y, salt, jitter)]

# ---- the painter --------------------------------------------------------------------


class Painter:
    """Owns the ground/overlay canvases, palette, warp and memoized SDFs for one map."""

    def __init__(self, mapdata, scene, warp_scale=45.0, warp_amp=WARP_AMP, salt=0):
        self.map = mapdata
        self.W = mapdata.cols * ZONE_TILE
        self.H = mapdata.rows_n * ZONE_TILE
        self.ground = Img(self.W, self.H)
        self.overlay = Img(self.W, self.H)
        self.scene = SCENES[scene]
        self.shadow = self.scene["shadow"]
        self.salt = salt
        assert warp_amp <= 6.0, "warp beyond 6px can contradict collision"
        self.warp_amp = warp_amp
        self.wx = fbm(self.W, self.H, warp_scale, 3, salt * 7 + 11, step=4)
        self.wy = fbm(self.W, self.H, warp_scale, 3, salt * 7 + 23, step=4)
        self._sdf = {}

    def mat(self, name, tones=6, spread=1.0, shadow=None):
        """N-tone ramp for a scene material: a hand-tuned identity ramp from the
        scene's "ramps" dict when one exists (warm dirt can't be derived — teal
        shadows turn it yellow-green, violet ones salmon), else derived from the
        material seed. `shadow` overrides the scene bias per material."""
        if name in self.scene.get("ramps", {}):
            return list(self.scene["ramps"][name])
        return ramp(self.scene["mats"][name], shadow or self.shadow, tones, spread)

    def sdf(self, chars, blur=2, step=4):
        """Memoized region SDF. Use step=8/blur>=8 for organic biome boundaries
        (melts the 32px tile steps); the tight default only suits logic queries."""
        key = ("".join(sorted(chars)), blur, step)
        if key not in self._sdf:
            self._sdf[key] = sdf_from_mask(self.map.mask(chars), ZONE_TILE, step, blur)
        return self._sdf[key]

    def warped(self, x, y):
        """Domain-warped sample position — apply to SDF lookups for organic edges."""
        a = self.warp_amp * 2.0
        return (x + (self.wx.sample(x, y) - 0.5) * a,
                y + (self.wy.sample(x, y) - 0.5) * a)

    def tiles(self, chars, pad=1):
        """Tile coords within `pad` tiles of any `chars` cell — restricts passes."""
        m = self.map
        mask = m.mask(chars)
        out = set()
        for ty in range(m.rows_n):
            row = mask[ty]
            for tx in range(m.cols):
                if row[tx]:
                    for dy in range(-pad, pad + 1):
                        ny = ty + dy
                        if 0 <= ny < m.rows_n:
                            for dx in range(-pad, pad + 1):
                                nx = tx + dx
                                if 0 <= nx < m.cols:
                                    out.add((nx, ny))
        return sorted(out)

    def scatter(self, chars, cell=12, keep=0.5, salt=0, inset=3):
        """Deterministic jittered-grid points at least `inset` px inside region."""
        pts = []
        sdf = self.sdf(chars)
        for gy in range(self.H // cell):
            for gx in range(self.W // cell):
                if h2(gx, gy, salt) > keep * 255:
                    continue
                x = gx * cell + 3 + (h2(gx, gy, salt + 1) * (cell - 6)) // 255
                y = gy * cell + 3 + (h2(gx, gy, salt + 2) * (cell - 6)) // 255
                if sdf.sample(x, y) <= -inset:
                    pts.append((x, y))
        return pts

    def cast_shadow(self, cx, cy, rx, ry, color, alpha=0.30):
        """Soft elliptical contact shadow (violet/teal per palette law)."""
        g = self.ground
        for y in range(int(cy - ry), int(cy + ry) + 2):
            for x in range(int(cx - rx), int(cx + rx) + 2):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if d <= 1.0:
                    g.mix(x, y, color, alpha * (1.0 - d * d))

    def save(self, ground_path, overlay_path):
        self.ground.save(ground_path)
        self.overlay.save(overlay_path)

# ---- canopy (tree walls / thickets) --------------------------------------------------


def paint_canopy(p, chars, canopy_ramp, trunk_ramp, salt=0, shadow_color=None,
                 sdf_blur=8, sdf_step=8):
    """Paint a solid region as a mass of overlapping shaded tree blobs.

    Understory darkness fills the region; jittered tree crowns (2-3 lobes each,
    dome-lit upper-left, leaf-noise mottle) are drawn north-to-south so southern
    crowns overlap northern ones and the wall reads as receding depth. Fringe
    pixels (within OVERLAY_DEPTH of walkable) land on ground, deeper on overlay.
    A contact shadow band grounds the wall onto the walkable side.
    """
    sdf = p.sdf(chars, blur=sdf_blur, step=sdf_step)
    leaf = fbm(p.W, p.H, 6.5, 2, salt * 13 + 5, step=1)
    nC = len(canopy_ramp) - 1
    nT = len(trunk_ramp) - 1
    ground, overlay = p.ground, p.overlay
    sample = sdf.sample
    warped = p.warped

    # understory + contact shadow
    if shadow_color is None:
        shadow_color = canopy_ramp[nC]
    for (tx, ty) in p.tiles(chars, pad=1):
        for y in range(ty * ZONE_TILE, ty * ZONE_TILE + ZONE_TILE):
            for x in range(tx * ZONE_TILE, tx * ZONE_TILE + ZONE_TILE):
                wxp, wyp = warped(x, y)
                s = sample(wxp, wyp)
                if s <= 2.0:
                    t = 0.78 + (leaf.sample(x, y) - 0.5) * 0.30
                    c = trunk_ramp[tone_i(nT, t, x, y, salt + 3)]
                    if sample(x, y) <= -OVERLAY_DEPTH:
                        overlay.put(x, y, c)
                    else:
                        ground.put(x, y, c)
                elif s <= 8.0:
                    ground.mix(x, y, shadow_color, 0.38 * (1.0 - s / 8.0))

    # tree crowns: dense jittered grid drawn north->south so each southern crown
    # overlaps the dark base of the one behind — a continuous scalloped mass with
    # lit tops and crevice shadows, not separate spheres.
    crowns = []
    grid = 10
    for gy in range(p.H // grid + 1):
        for gx in range(p.W // grid + 1):
            if h2(gx, gy, salt + 40) > 235:
                continue
            cx = gx * grid + (h2(gx, gy, salt + 41) * grid) // 255
            cy = gy * grid + (h2(gx, gy, salt + 42) * grid) // 255
            if sample(cx, cy) <= -0.25:
                crowns.append((cy, cx, h2(gx, gy, salt + 43)))
    # small clumps blur to a shallow SDF and would stay bare understory: every
    # region tile also seeds one crown at its center, so lone thickets read as
    # trees instead of dark holes.
    mask = p.map.mask(chars)
    for ty in range(p.map.rows_n):
        for tx in range(p.map.cols):
            if mask[ty][tx]:
                crowns.append((ty * ZONE_TILE + ZONE_TILE // 2,
                               tx * ZONE_TILE + ZONE_TILE // 2, h2(tx, ty, salt + 44)))
    crowns.sort()
    for (cy, cx, seed) in crowns:
        r = 7 + (seed % 4)
        lobes = ((0, 0, r),
                 (-(r * 5) // 8, 2 + (seed % 3), (r * 5) // 8),
                 ((r * 5) // 8, 3 - (seed % 3), (r * 5) // 8))
        for (ox, oy, lr) in lobes:
            lx, ly = cx + ox, cy + oy
            for y in range(ly - lr, ly + lr + 1):
                ny = (y - ly) / lr
                for x in range(lx - lr, lx + lr + 1):
                    nx = (x - lx) / lr
                    d = nx * nx + ny * ny
                    if d > 1.0:
                        continue
                    wxp, wyp = warped(x, y)
                    if sample(wxp, wyp) > 4.0:
                        continue
                    t = (0.30 + 0.34 * (nx * 0.30 + ny * 0.95)
                         + 0.10 * d + (leaf.sample(x, y) - 0.5) * 0.42)
                    c = canopy_ramp[tone_i(nC, t, x, y, salt + 5)]
                    if sample(x, y) <= -OVERLAY_DEPTH:
                        overlay.put(x, y, c)
                    else:
                        ground.put(x, y, c)

# ---- stamps -------------------------------------------------------------------------


def stamp_tuft(p, x, y, grass_ramp, salt=0):
    """Small grass blade cluster; alternates lit and shaded tufts by hash."""
    g = p.ground
    n = len(grass_ramp) - 1
    lit = h2(x, y, salt) & 1
    a = grass_ramp[1 if lit else n - 1]
    b = grass_ramp[0 if lit else n]
    for k in range(2 + h2(x, y, salt + 1) % 2):
        bx = x + (h2(x + k, y, salt + 2) % 5) - 2
        by = y + (h2(x, y + k, salt + 3) % 3) - 1
        g.put(bx, by, a)
        g.put(bx, by - 1, a)
        g.put(bx + (1 if h2(bx, by, salt) & 1 else -1), by - 2, b)


def stamp_flowers(p, x, y, accent, grass_ramp, salt=0):
    """Tight clump of 2-4 chunky flower heads (accent-heavy mix of pink/white/
    gold) over a small shaded patch — reads as one flower cluster at game zoom,
    not confetti."""
    g = p.ground
    heads = ((accent[0], accent[1], accent[2], 255),
             (250, 246, 238, 255),
             (255, 208, 110, 255))
    dark = grass_ramp[len(grass_ramp) - 2]
    stem = grass_ramp[len(grass_ramp) - 1]
    for yy in range(y - 2, y + 3):
        for xx in range(x - 3, x + 4):
            if (xx - x) ** 2 + (yy - y) ** 2 <= 7 and h2(xx, yy, salt) < 150:
                g.mix(xx, yy, dark, 0.30)
    for k in range(2 + h2(x, y, salt + 9) % 2):
        hx = x + (h2(x + k * 3, y, salt + 10) % 5) - 2
        hy = y + (h2(x, y + k * 3, salt + 11) % 4) - 2
        c = heads[0 if h2(hx, hy, salt + 12) < 150 else 1 + (h2(hx, hy, salt + 13) & 1)]
        deep = (max(0, c[0] - 70), max(0, c[1] - 80), max(0, c[2] - 50), 255)
        g.put(hx, hy + 2, stem)
        g.rect(hx, hy - 1, hx + 1, hy, c)
        g.put(hx + 1, hy + 1, deep)
        g.put(hx, hy - 1, (min(255, c[0] + 30), min(255, c[1] + 30), min(255, c[2] + 30), 255))


def stamp_pebbles(p, x, y, rock_ramp, salt=0):
    g = p.ground
    n = len(rock_ramp) - 1
    for k in range(1 + h2(x, y, salt) % 2):
        bx = x + (h2(x + k, y, salt + 1) % 5) - 2
        by = y + (h2(x, y + k, salt + 2) % 3) - 1
        g.rect(bx, by, bx + 1, by + 1, rock_ramp[n - 2])
        g.put(bx, by, rock_ramp[1])
        g.put(bx + 1, by + 1, rock_ramp[n])


def stamp_boulder(p, cx, cy, r, rock_ramp, grass_ramp, shadow_color, salt=0):
    """Squat lichen-flecked boulder: wide low domes, lit top rim, crack, dark
    seated base, cast shadow and base tufts."""
    n = len(rock_ramp) - 1
    p.cast_shadow(cx + r * 0.30, cy + r * 0.42, r * 1.3, r * 0.55, shadow_color, 0.36)
    g = p.ground
    lobes = ((0, 0, r, 0.0), (-(r * 3) // 5, r // 5, (r * 3) // 5, 0.10),
             ((r * 5) // 8, r // 6, r // 2, 0.14))
    for (ox, oy, lr, dark) in lobes:
        lx, ly = cx + ox, cy + oy
        ry = lr * 0.78
        for y in range(int(ly - ry), int(ly + ry) + 1):
            ny = (y - ly) / ry
            for x in range(int(lx - lr), int(lx + lr) + 1):
                nx = (x - lx) / lr
                d = abs(nx) ** 2.6 + abs(ny) ** 2.6
                if d > 1.0:
                    continue
                t = 0.24 + 0.44 * (nx * 0.45 + ny * 0.90) + 0.18 * d + dark
                if ny < -0.35 and d > 0.55:
                    t -= 0.22          # lit top rim
                if ny > 0.55:
                    t += 0.20          # seated dark base
                t += (h2(x // 2, y // 2, salt + 6) - 127.5) / 800.0
                if h2(x, y, salt + 8) < 9:
                    g.put(x, y, grass_ramp[1])   # lichen fleck
                    continue
                g.put(x, y, rock_ramp[tone_i(n, t, x, y, salt + 7)])
    ck = h2(cx, cy, salt + 9) % (r // 2 + 1) - r // 4
    for i in range(r // 2):
        g.put(cx + ck + i // 2, cy - r // 3 + i, rock_ramp[n])
    for k in range(2, 5):
        stamp_tuft(p, cx - r + (h2(cx, cy, salt + k) % (2 * r)), cy + int(r * 0.7), grass_ramp, salt + k)


def stamp_sparkle(p, x, y, color):
    g = p.ground
    g.put(x, y, color)
    g.put(x - 1, y, color)
    g.put(x + 1, y, color)
    g.put(x, y - 1, color)
    g.put(x, y + 1, color)
