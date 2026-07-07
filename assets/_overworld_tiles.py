#!/usr/bin/env python3
"""Overworld terrain kit — the CT autotile look on the bake->slice->dedupe path.

The continent is painted cell by cell, but every cell's art is a PURE function
of its configuration: (terrain class, the 8-neighbor masks of each differing
class, the coast-distance band) plus tile-LOCAL pixel coordinates. Two cells
with the same configuration are byte-identical, so the _tiles.py slicer
collapses the whole 64x36 map into a few hundred atlas tiles — coastlines,
riverbanks, cliff feet, forest rims and road shoulders all dedupe into the
classic autotile families, exactly like Chrono Trigger's VRAM.

The disciplines (the dedupe contract):
  * terrain fabrics are 16-periodic in (x%16, y%16); grass, forest, mountain
    and waste carry a 32-periodic phase (tx&1, ty&1) on INTERIOR cells only —
    edge cells always render phase 0, so transition families never multiply
    (which is also why lobe GEOMETRY must wrap at 16, never 32);
  * every class boundary has ONE owner that paints the whole band, including
    the far-side wedge of a 45-degree corner cut (water > waste > beach >
    road > forest > mountain own their edges; grassy never paints a band).
    One-sided bands are what let stair-steps in the map txt render as
    continuous diagonal coasts/rims with no seam;
  * transition stamps shade by edge_dist/diag_s of the neighbor masks — never
    by absolute position; road ribbons key their wobble to the shared EDGE
    (and the cell hash), so tiles stay pure functions of configuration;
  * per-cell hash variants (sea sparkle, grass tuft, waste crystal, snow cap)
    are allowed ONLY on interior cells whose 8 neighbors all share the cell's
    family — an edge cell never hashes, or the atlas multiplies;
  * the terrain painter sends NOTHING to the UPPER canvas: the forest
    boundary is a crown-arc silhouette on the ground layer, so no terrain
    pixel ever covers the chibi (landmark props may still split).

Stdlib-only, deterministic. Used by assets/_gen_tileset_overworld.py.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _tilekit import TileScene, T, TIMBER

# ---- 8-neighbor direction bits ------------------------------------------------------
N, NE, E, SE, S, SW, W, NW = 1, 2, 4, 8, 16, 32, 64, 128
DIRS = ((0, -1, N), (1, -1, NE), (1, 0, E), (1, 1, SE),
        (0, 1, S), (-1, 1, SW), (-1, 0, W), (-1, -1, NW))


def edge_dist(mask, x, y):
    """Chebyshev pixel distance from local (x, y) to the cell edges/corners
    whose direction bits are set — the geometry every transition shades by."""
    d = 99
    if mask & N:
        d = min(d, y)
    if mask & S:
        d = min(d, T - 1 - y)
    if mask & W:
        d = min(d, x)
    if mask & E:
        d = min(d, T - 1 - x)
    if mask & NE:
        d = min(d, max(T - 1 - x, y))
    if mask & SE:
        d = min(d, max(T - 1 - x, T - 1 - y))
    if mask & SW:
        d = min(d, max(x, T - 1 - y))
    if mask & NW:
        d = min(d, max(x, y))
    return d


# ---- 45-degree corner cuts ------------------------------------------------------------
# A cell whose "other" mask is exactly one orthogonal pair (both opposites
# clear) renders that corner cut off along the tile diagonal instead of a
# square L. The cut line passes through two tile corners, so consecutive
# stair-step cells chain into one continuous 45-degree boundary.
OPP = {N: S, S: N, E: W, W: E}
_CUT_PAIRS = ((N, E, NE, "NE"), (E, S, SE, "SE"),
              (S, W, SW, "SW"), (W, N, NW, "NW"))
_PAIR_BITS = {"NE": (N, E), "SE": (E, S), "SW": (S, W), "NW": (W, N)}
# The cut line runs corner-to-corner THROUGH the two tile corners adjacent to
# the cut, so those diagonals' bands are already covered by the cut band —
# strip them, or they stamp a redundant square blob on top of the diagonal.
_DIAG_ADJ = {NE: NW | SE, SE: NE | SW, SW: SE | NW, NW: SW | NE}


def cut_of(mask):
    """(corner name | None, leftover mask): detect the single corner cut a
    mask supports and strip its bits; leftovers shade square via edge_dist."""
    orth = mask & (N | E | S | W)
    for a, b, diag, corner in _CUT_PAIRS:
        if orth & a and orth & b and not orth & OPP[a] and not orth & OPP[b]:
            return corner, mask & ~(a | b | diag | _DIAG_ADJ[diag])
    return None, mask


def cuts_of(mask):
    """Multi-cut decomposition: fire a 45-degree cut for EVERY adjacent
    orthogonal pair present (no opposites-clear requirement), union-strip the
    consumed bits. N|W|E -> NW+NE cuts = a pointed inlet head; all four ->
    a center diamond. Renderers min-compose the cuts, so no band changes."""
    orth = mask & (N | E | S | W)
    cuts, used = [], 0
    for a, b, diag, corner in _CUT_PAIRS:
        if orth & a and orth & b:
            cuts.append(corner)
            used |= a | b | diag | _DIAG_ADJ[diag]
    return cuts, mask & ~used


def diag_s(corner, x, y):
    """Signed distance to the corner-cut line in HALF-pixel units (the line
    runs corner-to-corner; one diagonal pixel step changes this by 2, which
    is why straight-edge bands are compared at 2*edge_dist). Negative = the
    cut-off (neighbor) side."""
    if corner == "NE":
        return y - x
    if corner == "SW":
        return x - y
    if corner == "NW":
        return x + y - (T - 1)
    return (T - 1) - (x + y)                               # SE


def _seg_pdist(px_, py_, x0, y0, x1, y1):
    """Distance from a pixel to a segment — the road-ribbon geometry."""
    vx, vy = x1 - x0, y1 - y0
    wx, wy = px_ - x0, py_ - y0
    length = float(vx * vx + vy * vy)
    t = 0.0 if length == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / length))
    dx, dy = wx - t * vx, wy - t * vy
    return (dx * dx + dy * dy) ** 0.5


# ---- tile-local shading primitives -----------------------------------------------------
def _dither_i(n, t, u, v, salt, grain=2, jitter=0.8):
    """Cluster-jittered ramp INDEX (Sprite.tone's formula, standalone —
    the fabric Canvas is a raw Img, not a Sprite): map a continuous
    lit(0)->shadow(1) t onto n tones, offset by a grain-block hash so band
    edges break into organic clumps instead of hard lines. MUST be keyed on
    tile-local (or 32-space phase-wrapped) coordinates only — never absolute
    position — or identical neighbor configurations stop being
    byte-identical and the atlas dedupe dies."""
    q = t * (n - 1) + (h2(u // grain, v // grain, salt) - 127.5) * (jitter / 255.0)
    return max(0, min(n - 1, int(q + 0.5)))


def _grain_dither(ramp, t, u, v, salt, grain=2, jitter=0.8):
    return ramp[_dither_i(len(ramp), t, u, v, salt, grain, jitter)]


def _hatch(u, v, spacing=4, phase=0, diag=1):
    """Ordered diagonal hatch predicate — engraved-linework texture (rock
    strata). Geometric on purpose: hatch reads as carving where
    _grain_dither reads as organic mottle; don't swap one for the other.
    Tile-local coordinates only, same dedupe contract as _dither_i."""
    return (u + diag * v + phase) % spacing == 0


# ---- terrain classification ----------------------------------------------------------
# map legend terrain name -> render class (feature chars render their UNDERLAY
# ground; the placed prop covers it).
TERRAIN_CLS = {
    "sea": "sea", "river": "river", "bridge": "bridge", "beach": "beach",
    "grass": "grass", "hills": "hills", "flowers": "flowers",
    "forest": "forest", "mountain": "mountain", "waste": "waste",
    "road": "road", "plaza": "plaza", "door": "road",
    "home": "grass", "cottageA": "grass", "cottageB": "grass",
    "school": "grass", "well": "grass", "lamp": "grass", "stall": "grass",
    "town": "grass", "tree": "grass",
    # landmark props render their region's fabric as underlay: the castle
    # and peak ride the massif, the obelisk + crystal outcrops ride the
    # wastes, the elder tree rides the plain
    "castle": "mountain", "obelisk": "waste", "crystal": "waste",
    "peak": "mountain", "giant_tree": "grass",
    # Alembic Town at zone scale (assets/maps/town.txt rides this same
    # driver): solid facade rows + WALKABLE roof rows the player passes
    # behind (roof art goes to the upper canvas via place_split), a fence
    # class, and grass underlays for the full-scale props.
    "fence": "fence",
    "homebody": "grass", "homeroof": "grass",
    "cotWbody": "grass", "cotWroof": "grass",
    "cotEbody": "grass", "cotEroof": "grass",
    "academybody": "grass", "academyroof": "grass",
}
# solid built things that drop a contact shadow on the ground cell south of them
STRUCT_TERRAIN = {"home", "cottageA", "cottageB", "school",
                  "well", "lamp", "stall", "fence", "town", "tree",
                  "obelisk", "crystal", "castle", "peak", "giant_tree",
                  "homebody", "cotWbody", "cotEbody", "academybody"}

WATERC = {"sea", "river", "bridge"}     # no coastline forms inside this family
GRASSY = {"grass", "hills", "flowers"}
ROADY = {"road", "plaza"}
GROUND = {"grass", "hills", "flowers", "beach", "waste", "road", "plaza",
          "fence"}
MOUNT_OWN = GROUND | {"forest"}         # what a massif rim opens onto
LANDC = {"grass", "hills", "flowers", "beach", "waste", "road", "plaza",
         "forest", "mountain"}          # what a water cell shores against
FAMILY = {c: (GRASSY if c in GRASSY else WATERC if c in WATERC else {c})
          for c in set(TERRAIN_CLS.values())}


class OverWorld(TileScene):
    """The tiled travel continent: fabrics + neighbor-stamp transitions."""

    def __init__(self, map_name="overworld", scene_key="overworld"):
        super().__init__(map_name, scene_key)
        self.SEA = self.mat("sea", spread=1.1)             # moodier deeps
        self.GRASS = self.mat("grass", spread=1.15)
        self.GRASS2 = self.mat("grass2", spread=1.05)      # warm drift green
        self.SAND = self.mat("sand")                       # hand ramp
        self.ROAD = self.mat("road")                       # hand ramp
        self.FOREST = self.mat("forest", spread=1.2)       # wide range: lit caps
                                                           # to crevice darks
        self.TRUNK = self.mat("trunk", spread=0.8)
        self.ROCK = self.mat("rock", spread=1.2)           # dimensional cliffs
        self.WASTE = self.mat("waste", shadow="violet")
        self.SNOW = self.mat("snow")
        self.BRIDGE = self.mat("bridge", shadow="violet", spread=0.85)
        self.PINK = (255, 116, 176, 255)                   # meadow flower hot-pink
        self.SPARK = (214, 246, 248, 255)
        self.DEAD = ((96, 74, 128, 255), (68, 50, 96, 255), (44, 32, 66, 255))
        self.crystal_cells = []                            # for the glow overlay
        # the crack graph pre-wrapped with reject bboxes (drawn per pixel)
        self._crack_segs = []
        for (x0, y0), (x1, y1) in self._CRACKS32:
            for ox in (-32, 0, 32):
                for oy in (-32, 0, 32):
                    a, b, c, d = x0 + ox, y0 + oy, x1 + ox, y1 + oy
                    self._crack_segs.append(
                        (a, b, c, d, min(a, c) - 2, min(b, d) - 2,
                         max(a, c) + 2, max(b, d) + 2))
        # per-char class + structure flag from the legend's terrain names
        self._cls = {}
        self._struct = set()
        for ch, d in self.m.legend.items():
            assert d["terrain"] in TERRAIN_CLS, f"no render class for {d['terrain']}"
            self._cls[ch] = TERRAIN_CLS[d["terrain"]]
            if d["terrain"] in STRUCT_TERRAIN:
                self._struct.add(ch)
        self._dland = self._water_distance()

    # -- geography helpers -------------------------------------------------------------
    def cls_at(self, tx, ty):
        ch = self.m.at(tx, ty)
        return self._cls[ch] if ch else None

    def _water_distance(self):
        """Chebyshev tile distance to the nearest non-water cell (capped at 5):
        the sea's shallow->deep banding. BFS over 8-neighbors."""
        m = self.m
        INF = 99
        dist = [[INF] * m.cols for _ in range(m.rows_n)]
        frontier = []
        for y in range(m.rows_n):
            for x in range(m.cols):
                if self._cls[m.at(x, y)] not in WATERC:
                    dist[y][x] = 0
                    frontier.append((x, y))
        d = 0
        while frontier and d < 5:
            d += 1
            nxt = []
            for (x, y) in frontier:
                for dx, dy, _ in DIRS:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < m.cols and 0 <= ny < m.rows_n and dist[ny][nx] == INF:
                        dist[ny][nx] = d
                        nxt.append((nx, ny))
            frontier = nxt
        return dist

    def _corner_depths(self, tx, ty):
        """Sea depth at the tile's 4 corner lattice points (NW, NE, SW, SE):
        the average of min(dland, 3) over the <=4 cells sharing each corner,
        rounded to whole steps. Both are atlas-budget dials: 0.5 steps /
        a 4-cell fringe read barely smoother and near-doubled the signature
        space. Adjacent tiles read the same lattice point, so bilinear depth
        is continuous across seams; the signature is a pure function of
        second-ring geography, so the atlas dedupe survives."""
        m = self.m
        out = []
        for cy in (ty, ty + 1):
            for cx in (tx, tx + 1):
                s = 0.0
                for oy in (-1, 0):
                    for ox in (-1, 0):
                        x = min(max(cx + ox, 0), m.cols - 1)
                        y = min(max(cy + oy, 0), m.rows_n - 1)
                        s += min(self._dland[y][x], 3)
                out.append(float(round(s / 4.0)))
        return tuple(out)

    # -- fabrics: pure functions of local (u, v) -----------------------------------------
    def _px_sea(self, u, v, depth, phase=0):
        """Open water: a continuous shallow->deep grade (bilinear corner
        depth through the grain dither, so tone steps break into organic
        clumps instead of quantizing per 16px tile) under staggered swell
        crests whose dash phase drifts with the 32-space quadrant."""
        s = self.SEA
        w, z = u + 16 * (phase & 1), v + 16 * (phase >> 1)
        t = max(0.0, min(1.0, (depth - 0.4) / 2.6))
        i = 1 + _dither_i(4, t, w, z, 71, grain=2, jitter=1.0)
        dash = 7 * (phase & 1) + 3 * (phase >> 1)
        if v in (3, 11):                                   # staggered swell crests
            if (u + dash + (0 if v == 3 else 8)) % 16 < 6:
                return s[max(0, i - 1)]
        if v in (4, 12):                                   # their trough shadow
            if 1 <= (u + dash + (0 if v == 4 else 8)) % 16 < 6:
                return s[min(5, i + 1)]
        return s[i]

    # 32-space grass texture (phase = which 16px quadrant a tile renders):
    # deliberate CT tufts (lit tip over a shaded V, one dark root) ...
    _TUFTS32 = ((4, 10), (13, 27), (20, 3), (28, 17), (9, 19), (24, 25))
    # ... singles: dark nicks / sunlit 2px dashes ...
    _NICKS32 = ((9, 1), (30, 10), (1, 6), (13, 15), (19, 22), (26, 14))
    _DASHES32 = ((8, 6), (30, 28), (17, 8), (22, 30))
    # ... and two BROAD warm-green drift patches (lobe unions, wrapped) —
    # CT's two-green field: the second hue dithered in at matched value,
    # replacing the old stamped dark ellipses that tiled into a dot grid
    _DRIFT32 = (((10, 7, 9.5, 5.5), (17, 11, 7.0, 4.5), (4, 12, 6.0, 3.5)),
                ((26, 23, 8.5, 5.0), (20, 28, 6.5, 4.0), (31, 17, 5.5, 3.5)))

    def _drift_cov(self, w, z):
        """Warm-patch coverage 0..1 at a 32-space point: max over the wrapped
        elliptical lobes, so patches are lobed unions that cross tile lines."""
        cov = 0.0
        for lobes in self._DRIFT32:
            for cx, cy, rx, ry in lobes:
                for ox in (-32, 0, 32):
                    for oy in (-32, 0, 32):
                        dx, dy = (w - cx - ox) / rx, (z - cy - oy) / ry
                        q = dx * dx + dy * dy
                        if q < 1.0:
                            cov = max(cov, 1.0 - q)
        return cov

    def _px_grass(self, u, v, phase=0):
        g = self.GRASS
        w, z = u + 16 * (phase & 1), v + 16 * (phase >> 1)
        for cx, cy in self._TUFTS32:
            if (w, z) == (cx, cy):
                return g[1]
            if (w, z) in ((cx - 1, cy + 1), (cx + 1, cy + 1)):
                return g[3]
            if (w, z) == (cx, cy + 1):
                return g[4]
        if (w, z) in self._NICKS32:
            return g[3]
        if (w, z) in self._DASHES32 or (w - 1, z) in self._DASHES32:
            return g[1]
        # the drift patches: a grain-jittered coverage threshold hands the
        # pixel to the warm ramp, so patch borders break into organic clumps
        cov = self._drift_cov(w, z)
        if cov > 0.10 + (h2(w // 2, z // 2, 93) % 64) / 96.0:
            # quiet interior: the warm ramp's midtones only, low jitter —
            # the patch is a hue drift, not a texture event
            g2 = self.GRASS2
            return _grain_dither((g2[1], g2[2], g2[3]), 0.45, w, z, 91,
                                 grain=3, jitter=0.9)
        # the base field itself: SPARSE dithered clumps around the mid tone
        # (one step either way on ~8% of grain blocks), so the flat 80% of
        # every tile carries quiet turf texture without reading as noise
        return _grain_dither(g, 0.40, w, z, 91, grain=3, jitter=1.15)

    # 32-space hills: two soft turf knolls per 2x2 tiles riding the grass
    # fabric — scattered rises read by their lit brow and thin base shadow,
    # not an egg-carton of dark ovals stamped one per tile
    _KNOLLS32 = ((8, 6, 7.0, 4.6), (22, 21, 6.2, 4.2))

    def _px_hills(self, u, v, phase=0):
        g = self.GRASS
        w, z = u + 16 * (phase & 1), v + 16 * (phase >> 1)
        for cx, cy, rx, ry in self._KNOLLS32:
            for ox in (-32, 0, 32):
                for oy in (-32, 0, 32):
                    dx, dy = (w - cx - ox) / rx, (z - cy - oy) / ry
                    q = dx * dx + dy * dy
                    if q > 1.0:
                        continue
                    if dy < -0.30 and q > 0.45:
                        return g[1]                        # sunlit brow arc
                    if q > 0.72 and dy > 0.25:
                        return g[4]                        # thin base shadow
                    # the raised body: a touch lighter than the field
                    return _grain_dither((g[1], g[2], g[2]), 0.5, w, z, 91,
                                         grain=3, jitter=0.9)
        return self._px_grass(u, v, phase)

    def _px_flowers(self, u, v, phase=0):
        if (u, v) in ((4, 4), (11, 6), (7, 11), (13, 13)):
            return self.PINK
        if (u, v) == (4, 3):
            return self.SPARK
        if (u, v) in ((5, 5), (12, 7), (8, 12)):
            return self.GRASS[1]                           # leaf beside each bloom
        return self._px_grass(u, v, phase)

    def _px_beach(self, u, v):
        s = self.SAND
        if (u, v) in ((3, 5), (9, 2), (13, 9), (6, 12)):
            return s[2]
        if (u, v) in ((10, 6), (2, 11)):
            return s[0]
        if (u, v) == (14, 14):
            return s[3]
        return s[1]

    # 16-periodic canopy GEOMETRY: two staggered rows of chunky crowns per
    # tile (row pitch 8), painter-sorted south-over-north so each row's lit
    # tops overlap the row above's dark bottoms — CT's scalloped stacked
    # canopy. Crowns must wrap at 16, not 32: edge cells always render
    # phase 0, so 32-periodic crown geometry chops mid-crown at every
    # transition seam (the boxy-forest bug). Like the mountain ridges, only
    # the dither TEXTURE varies with the 32-space interior phase.
    _CROWNS16 = ((4, 3, 6.4), (12, 2, 5.6), (0, 11, 6.0), (8, 10, 6.8))

    # small strip crowns (each disc fully inside one tile), used only when
    # a narrow forest run rejects every full-size crown — a 1-cell arm
    # renders as a scrubby tree line instead of vanishing
    _SYNTH16 = ((4, 5, 4.2), (12, 4, 3.8), (3, 12, 4.0), (11, 11, 4.4))

    def _crown_px(self, nx, ny, q, w, z):
        """One canopy ball pixel: NW-lit — bright cap, dithered mid bands,
        hard dark under-rim, near-black at the base."""
        f = self.FOREST
        if q > 0.80 and ny > 0.15:
            return f[5] if ny > 0.55 else f[4]
        lit = -ny * 0.85 - nx * 0.30 + (1.0 - q) * 0.35    # NW-high lambert
        if lit > 0.72:
            return f[0]                                    # rare sun-glint cap
        t = max(0.0, min(1.0, (0.75 - lit) / 1.6))
        return f[1 + _dither_i(4, t, w, z, 66, grain=2, jitter=0.55)]

    def _lobe_win(self, u, v, lobes=None):
        """The winning wrapped lobe at a pixel — the SOUTHERNMOST instance
        containing it (painter's order), so each row's lit tops overlap the
        row above's dark bottoms. (nx, ny, q) or None."""
        win, wkey = None, (-99, -99)
        for cx, cy, r in (lobes or self._CROWNS16):
            for oy in (-16, 0, 16):
                for ox in (-16, 0, 16):
                    dx, dy = u - (cx + ox), v - (cy + oy)
                    q = (dx * dx + dy * dy) / (r * r)
                    if q <= 1.0 and (cy + oy, cx + ox) > wkey:
                        win, wkey = (dx / r, dy / r, q), (cy + oy, cx + ox)
        return win

    def _px_forest(self, u, v, phase=0):
        """Interior canopy: stacked crown balls; gaps are understory."""
        win = self._lobe_win(u, v)
        if win is None:
            return self.FOREST[5]                          # understory hole
        return self._crown_px(win[0], win[1], win[2],
                              u + 16 * (phase & 1), v + 16 * (phase >> 1))

    def _rock_px(self, nx, ny, q, w, z, snow=False):
        """One massif pixel: the lobe shaded as a stylized PEAK — a hard
        two-face split (sunlit west face, shadow east face with engraved
        strata) under a bright vertical ridge crest, the classic SNES
        world-map mountain; snowy cells whiten the summit arc."""
        r = self.ROCK
        if snow and ny < -0.30:                            # the summit cap
            s = self.SNOW
            if ny < -0.60:
                return s[0] if nx < 0.15 else s[1]
            return s[1] if nx < 0 else s[2]                # cap skirt
        if q > 0.82 and ny > 0.18:
            return r[5]                                    # under-rim shadow
        if abs(nx) < 0.09 and ny < 0.40:
            return r[0] if ny < -0.15 else r[1]            # the ridge crest
        if nx < 0:                                         # sunlit west face
            i = 1 if ny < -0.15 else 2
        else:                                              # shadow east face
            i = 3 if ny < -0.15 else 4
            if _hatch(w, z, 4, 1, -1):
                i = min(5, i + 1)                          # engraved strata
        return r[i]

    def _px_mountain(self, u, v, phase=0):
        """Interior massif: painter-sorted peak lobes; clefts between."""
        win = self._lobe_win(u, v)
        if win is None:
            return self.ROCK[5]                            # cleft shadow
        return self._rock_px(win[0], win[1], win[2],
                             u + 16 * (phase & 1), v + 16 * (phase >> 1))

    # 32-space cracked-pan texture: an ANGULAR crack graph — straight
    # segments meeting at Y-junctions, dividing the period into irregular
    # polygonal plates like real dried mud. Border-crossing edges land on
    # congruent nodes (+-32), so the web is seamless. No rounded blotches:
    # smooth loops + elliptical shading read as anatomy, not geology.
    _CRACKS32 = (
        ((3, 4), (14, 2)), ((14, 2), (25, 6)), ((25, 6), (35, 4)),
        ((14, 2), (16, -3)),
        ((3, 4), (8, 10)), ((25, 6), (20, 13)),
        ((8, 10), (20, 13)), ((8, 10), (3, 18)), ((8, 10), (13, 20)),
        ((20, 13), (30, 16)), ((20, 13), (13, 20)), ((30, 16), (35, 18)),
        ((30, 16), (24, 24)),
        ((3, 18), (6, 27)), ((13, 20), (16, 29)), ((13, 20), (24, 24)),
        ((6, 27), (16, 29)), ((24, 24), (28, 29)),
        ((6, 27), (3, 36)), ((28, 29), (25, 38)))
    _WPEBBLES32 = ((4, 6), (17, 3), (29, 19), (9, 30), (24, 30))

    def _px_waste(self, u, v, phase=0):
        w_ = self.WASTE
        w, z = u + 16 * (phase & 1), v + 16 * (phase >> 1)
        for px_, py_ in self._WPEBBLES32:
            if (w, z) == (px_, py_):
                return w_[1]                               # pebble catchlight
            if (w, z) == (px_, py_ + 1):
                return w_[3]                               # its shadow
        d = 99.0
        for x0, y0, x1, y1, bx0, by0, bx1, by1 in self._crack_segs:
            if bx0 <= w <= bx1 and by0 <= z <= by1:
                dd = _seg_pdist(w, z, x0, y0, x1, y1)
                if dd < d:
                    d = dd
        if d < 0.7:
            return w_[4]                                   # the crack itself
        if d < 1.6:                                        # parched plate lip
            return _grain_dither((w_[2], w_[3]), 0.7, w, z, 89,
                                 grain=2, jitter=0.9)
        return _grain_dither(w_, 0.36, w, z, 88, grain=3, jitter=0.8)

    def _px_road(self, u, v):
        rd = self.ROAD
        if (u, v) in ((3, 4), (9, 9), (14, 2), (6, 13)):
            return rd[2]
        if (u, v) in ((11, 6), (4, 10)):
            return rd[3]                                   # pits
        if (u, v) == (7, 2):
            return rd[0]
        return rd[1]

    def _px_plaza(self, u, v):
        """Warm trodden setts (kept for a future cobbled commons — the open
        cluster's ground is plain grass + dirt lanes today). Quiet on purpose."""
        rd = self.ROAD
        u2 = (u + 4 * ((v // 4) % 2)) % 8
        if v % 4 == 0 or u2 == 0:
            return rd[3]                                   # sunken joints
        if ((u + 4 * ((v // 4) % 2)) // 8 + v // 4) % 5 == 2:
            return rd[1]                                   # the odd pale sett
        return rd[2]

    def _px_bridge(self, u, v):
        b = self.BRIDGE
        if v % 4 == 3:
            return b[4]                                    # course seam
        if u == (5 if (v // 4) % 2 else 12) and v % 4 in (1, 2):
            return b[3]                                    # butt seam
        return b[1] if v % 4 == 0 else b[2]

    # -- per-cell painters (all local-pure) ----------------------------------------------
    # Boundary OWNERSHIP: the classes below paint the WHOLE band against their
    # neighbors — line, lip, and (on a corner cut) the neighbor-fabric wedge.
    # The neighbor cell paints pure fabric to its edge. One owner per boundary
    # is what makes the 45-degree cuts chain seamlessly down a stair-step.
    def _fab(self, cls, u, v):
        """A neighbor class's fabric, for cut wedges (always phase 0)."""
        if cls == "hills":
            return self._px_hills(u, v)
        if cls == "flowers":
            return self._px_flowers(u, v)
        if cls == "beach":
            return self._px_beach(u, v)
        if cls == "waste":
            return self._px_waste(u, v)
        if cls in ("road", "plaza"):
            return self._px_grass(u, v)                    # trails sit on grass
        if cls == "forest":
            return self._px_forest(u, v)
        if cls == "mountain":
            return self._px_mountain(u, v)
        return self._px_grass(u, v)

    def _lip_band(self, cls, s2, u, v):
        """The graduated land-side lip a water/waste boundary lays against
        class cls: two tones dithered across the band (s2 in -2..1) instead
        of the old single hard line, so shores blend into their fabric."""
        near, far = {"beach": (self.SAND[2], self.SAND[3]),
                     "waste": (self.WASTE[3], self.WASTE[4]),
                     "forest": (self.FOREST[3], self.FOREST[4]),
                     "mountain": (self.ROCK[3], self.ROCK[4])}.get(
                         cls, (self.GRASS[4], self.GRASS[5]))
        t = max(0.0, min(1.0, (s2 + 2) / 3.0))
        return _grain_dither((near, far), t, u, v, 92, grain=1, jitter=1.1)

    @staticmethod
    def _mkey(cx, cy):
        """Shoreline meander offset at a corner LATTICE point, in half-px
        {0, 3, 6}. Keyed to the shared lattice (both cells hash the same
        point), so bulges stay byte-continuous across tile seams — the
        road-ribbon wobble trick applied to coasts. Amplitude is free:
        the signature space is the same 3 values however far they push."""
        return (h2(cx, cy, 83) % 3) * 3

    # which lattice corner a lone diagonal bit hangs off
    _DIAG_CORNER = {NE: (1, 0), SE: (1, 1), SW: (0, 1), NW: (0, 0)}

    def _shore_prep(self, masks, only, tx=None, ty=None, multi=False):
        """Per-cell boundary geometry: [(corner|None, bit, class, k0, k1)],
        one seg per cut or leftover direction bit. multi=True decomposes
        3+-orthogonal masks into several cuts (pointed inlet heads instead
        of square U's). With tx/ty each seg carries meander offsets at the
        two lattice corners its boundary runs between (k0/k1, half-px);
        without, offsets are 0 and geometry is exactly the classic bands."""
        wob = tx is not None
        segs = []
        for c2, bits in masks.items():
            if c2.startswith("__") or c2 not in only:
                continue
            if multi:
                corners, rest = cuts_of(bits)
            else:
                corner, rest = cut_of(bits)
                corners = [corner] if corner is not None else []
            for cn in corners:
                k0 = k1 = 0
                if wob:
                    if cn in ("NE", "SW"):     # cut line: NW corner -> SE
                        k0, k1 = self._mkey(tx, ty), self._mkey(tx + 1, ty + 1)
                    else:                      # cut line: NE corner -> SW
                        k0, k1 = self._mkey(tx + 1, ty), self._mkey(tx, ty + 1)
                segs.append((cn, 0, c2, k0, k1))
            for dx, dy, bit in DIRS:
                if not rest & bit:
                    continue
                k0 = k1 = 0
                if wob:
                    if bit in (N, S):
                        cy = ty if bit == N else ty + 1
                        k0, k1 = self._mkey(tx, cy), self._mkey(tx + 1, cy)
                    elif bit in (W, E):
                        cx = tx if bit == W else tx + 1
                        k0, k1 = self._mkey(cx, ty), self._mkey(cx, ty + 1)
                    else:                      # lone diagonal: one corner
                        ox, oy = self._DIAG_CORNER[bit]
                        k0 = k1 = self._mkey(tx + ox, ty + oy)
                segs.append((None, bit, c2, k0, k1))
        return segs

    @staticmethod
    def _shore_s(segs, u, v):
        """(s2, class, (kA, kB)) of the nearest boundary in half-pixel units.
        Straight edges sit at 2*d + 1 so the whole band lives inside the
        owner cell; cut diagonals go negative on the cut-off side. The
        meander lerp k0->k1 along the boundary lowers s2 toward the water,
        bulging the land line organically; the winning seg's keys come back
        so foam hashes can vary per shore tile for free. 99 = far interior."""
        best, bc, ka, kb = 99, None, 0, 0
        for corner, bit, c2, k0, k1 in segs:
            if corner is not None:
                s2 = diag_s(corner, u, v)
                t = (u + v) / 30.0 if corner in ("NE", "SW") \
                    else (T - 1 - u + v) / 30.0
            else:
                s2 = 2 * edge_dist(bit, u, v) + 1
                if bit in (N, S):
                    t = u / 15.0
                elif bit in (W, E):
                    t = v / 15.0
                else:
                    t = 0.0
            s2 -= int(k0 + (k1 - k0) * t + 0.5)
            if s2 < best:
                best, bc, ka, kb = s2, c2, k0, k1
        return best, bc, (ka, kb)

    def _sea_cell(self, X, Y, masks, tx, ty, phase):
        segs = self._shore_prep(masks, LANDC, tx, ty, multi=True)
        cd = self._corner_depths(tx, ty)
        if cd != (3.0, 3.0, 3.0, 3.0):
            phase = 0                                      # phase only on the flat
                                                           # deeps: near-shore depth
                                                           # families must not x4
        for v in range(T):
            for u in range(T):
                s2, D, (kA, kB) = self._shore_s(segs, u, v)
                if s2 <= -3:
                    c = self._fab(D, u, v)                 # the cut-off land wedge
                elif s2 <= 1:
                    c = self._lip_band(D, s2, u, v)        # graded land lip
                elif s2 <= 4:
                    c = self.SEA[5]                        # waterline
                elif s2 <= 8 and h2(u + 3 * kA, v + 5 * kB, 73) % 5 < 3:
                    c = self.SEA[0]                        # inner foam arc
                elif 11 <= s2 <= 13 and h2(u + 5 * kB, v + 3 * kA, 74) % 5 < 2:
                    c = self.SEA[1]                        # outer broken arc
                else:
                    fx, fy = (u + 0.5) / T, (v + 0.5) / T
                    depth = (cd[0] * (1 - fx) * (1 - fy) + cd[1] * fx * (1 - fy)
                             + cd[2] * (1 - fx) * fy + cd[3] * fx * fy)
                    if depth < 1.0 and _dither_i(2, depth - 0.2, u, v, 79,
                                                 grain=1, jitter=1.2) == 0:
                        c = self.SEA[0]                    # pale shallow shelf
                    else:
                        c = self._px_sea(u, v, depth, phase)
                self.bg.put(X + u, Y + v, c)

    def _river_cell(self, X, Y, masks):
        segs = self._shore_prep(masks, LANDC, multi=True)  # no meander: 8px channel
        deck = masks.get("bridge", 0)
        for v in range(T):
            for u in range(T):
                s2, D, _ = self._shore_s(segs, u, v)
                if s2 <= -3:
                    c = self._fab(D, u, v)                 # inner-bend wedge
                elif s2 <= 1:
                    c = self._lip_band(D, s2, u, v)
                elif s2 <= 3:
                    c = self.SEA[5]                        # bank line
                elif s2 <= 5:
                    c = self.SEA[4]
                elif u in (7, 8) and v % 6 < 4:
                    c = self.SEA[1]                        # center thread
                else:
                    c = self.SEA[2]
                if deck and edge_dist(deck, u, v) <= 1:
                    c = self.SEA[4]                        # bridge deck shadow
                self.bg.put(X + u, Y + v, c)

    def _bridge_cell(self, X, Y, water, land):
        b = self.BRIDGE
        for v in range(T):
            for u in range(T):
                c = self._px_bridge(u, v)
                if land and edge_dist(land & (E | W), u, v) == 0:
                    c = b[4]                               # plank ends at the banks
                self.bg.put(X + u, Y + v, c)
        if water & N:                                      # rails on the water sides
            self.bg.rect(X, Y, X + T - 1, Y, b[1])
            self.bg.rect(X, Y + 1, X + T - 1, Y + 1, b[3])
            self.bg.rect(X, Y + 2, X + T - 1, Y + 2, b[5])
        if water & S:
            self.bg.rect(X, Y + T - 3, X + T - 1, Y + T - 3, b[1])
            self.bg.rect(X, Y + T - 2, X + T - 1, Y + T - 2, b[3])
            self.bg.rect(X, Y + T - 1, X + T - 1, Y + T - 1, b[5])

    def _beach_cell(self, X, Y, masks):
        gmask = 0                                          # beach owns vs green+trail
        for c2 in ("grass", "hills", "flowers", "road", "plaza"):
            gmask |= masks.get(c2, 0)
        corner, rest = cut_of(gmask)
        for v in range(T):
            for u in range(T):
                c = self._px_beach(u, v)
                s2 = 99
                if corner is not None:
                    s2 = diag_s(corner, u, v)
                if rest:
                    s2 = min(s2, 2 * edge_dist(rest, u, v) + 1)
                if s2 <= -2:
                    c = self._px_grass(u, v)               # the cut-off grass wedge
                elif s2 <= 2 and _dither_i(2, (s2 + 2) / 4.0, u, v, 75,
                                           grain=1, jitter=1.3) == 0:
                    # grass creeping onto the sand, dense at the seam and
                    # thinning out — a graded fringe, not a uniform crumb line
                    c = _grain_dither((self.GRASS[2], self.GRASS[3]),
                                      0.4, u, v, 78, grain=1, jitter=1.0)
                self.bg.put(X + u, Y + v, c)

    def _grassy_cell(self, X, Y, cls, phase):
        px = {"grass": self._px_grass, "hills": self._px_hills,
              "flowers": self._px_flowers}[cls]
        for v in range(T):                                 # pure fabric: every
            for u in range(T):                             # boundary has an owner
                self.bg.put(X + u, Y + v, px(u, v, phase))

    def _waste_cell(self, X, Y, masks, tx, ty, phase):
        """The drained pan's rim on the COAST machinery — lattice-keyed
        meander bulges, multi-cut inlet heads, a graded lip dithering into
        crumbs — so the wastes stop ending in tile-grid stair-steps."""
        segs = self._shore_prep(masks, GRASSY | {"beach"}, tx, ty, multi=True)
        for v in range(T):
            for u in range(T):
                s2, D, _ = self._shore_s(segs, u, v)
                if s2 <= -3:
                    c = self._fab(D, u, v)                 # healthy-ground wedge
                elif s2 <= 1:
                    c = self._lip_band("waste", s2, u, v)  # graded drained rim
                elif s2 <= 5 and h2(u, v, 76) % 3 == 0:
                    c = self.WASTE[3]                      # crumbling fringe
                else:
                    c = self._px_waste(u, v, phase)
                self.bg.put(X + u, Y + v, c)

    def _roady_cell(self, X, Y, cls, conn, tx, ty):
        """A trail: grass verge + a wobbly packed-earth ribbon drawn as the
        union of segments from each connected edge to a drifting mid-point.
        Wobble is keyed to the shared EDGE (both cells compute the same
        offset), so ribbons meet exactly at tile lines; corner turns round
        off through the drift point instead of a square L."""
        if cls == "plaza":
            for v in range(T):
                for u in range(T):
                    self.bg.put(X + u, Y + v, self._px_plaza(u, v))
            return
        wN = (tx * 5 + ty * 3) % 3 - 1
        wS = (tx * 5 + (ty + 1) * 3) % 3 - 1
        wW = (tx * 3 + ty * 5) % 3 - 1
        wE = ((tx + 1) * 3 + ty * 5) % 3 - 1
        cx = 7.5 + ((tx * 7 + ty * 11) % 3 - 1) * 1.0      # mid-cell drift
        cy = 7.5 + ((tx * 11 + ty * 7) % 3 - 1) * 1.0
        hw = 2.3 + ((tx + ty * 3) % 3) * 0.4               # ~5-6px wide
        ends = []
        if conn & N:
            ends.append((7.5 + wN, 0.0))
        if conn & S:
            ends.append((7.5 + wS, 15.0))
        if conn & W:
            ends.append((0.0, 7.5 + wW))
        if conn & E:
            ends.append((15.0, 7.5 + wE))
        if not ends:
            ends.append((cx, cy))
        for v in range(T):
            for u in range(T):
                d = min(_seg_pdist(u, v, ex, ey, cx, cy) for ex, ey in ends)
                if d <= hw - 1.5:
                    c = self._px_road(u, v)                # packed-earth core
                elif d <= hw - 0.6:
                    c = self.ROAD[2]
                elif d <= hw + 0.4:
                    c = self.ROAD[3]                       # trodden edge line
                elif d <= hw + 1.6 and h2(u, v, 77) % 3 == 0:
                    c = self.ROAD[2]                       # crumbs into the verge
                else:
                    c = self._px_grass(u, v)               # the verge itself
                self.bg.put(X + u, Y + v, c)

    def _fence_cell(self, X, Y, link):
        """Zone-scale yard fence on grass: double rails toward each linked
        neighbor, pickets along straight runs, a squared post at joints."""
        tm = TIMBER
        for v in range(T):
            for u in range(T):
                self.bg.put(X + u, Y + v, self._px_grass(u, v))
        if link & W:
            self.bg.rect(X, Y + 6, X + 8, Y + 6, tm[1])
            self.bg.rect(X, Y + 7, X + 8, Y + 7, tm[3])
            self.bg.rect(X, Y + 10, X + 8, Y + 10, tm[2])
        if link & E:
            self.bg.rect(X + 7, Y + 6, X + T - 1, Y + 6, tm[1])
            self.bg.rect(X + 7, Y + 7, X + T - 1, Y + 7, tm[3])
            self.bg.rect(X + 7, Y + 10, X + T - 1, Y + 10, tm[2])
        if link & N:
            self.bg.rect(X + 7, Y, X + 8, Y + 8, tm[3])
        if link & S:
            self.bg.rect(X + 7, Y + 7, X + 8, Y + T - 1, tm[3])
        if link & (W | E) and not link & (N | S):
            for u in (3, 12):                              # pickets
                self.bg.rect(X + u, Y + 4, X + u + 1, Y + 11, tm[2])
                self.bg.put(X + u, Y + 4, tm[1])
                self.bg.rect(X + u, Y + 11, X + u + 1, Y + 11, tm[4])
        else:                                              # post at joints/ends
            self.bg.rect(X + 6, Y + 3, X + 9, Y + 12, tm[2])
            self.bg.rect(X + 6, Y + 3, X + 6, Y + 12, tm[1])
            self.bg.rect(X + 9, Y + 3, X + 9, Y + 12, tm[4])
            self.bg.rect(X + 6, Y + 12, X + 9, Y + 12, tm[5])

    # which lattice corner a lone open diagonal touches (px point)
    _CORNER_PT = {NE: (15.5, -0.5), SE: (15.5, 15.5),
                  SW: (-0.5, 15.5), NW: (-0.5, -0.5)}

    @staticmethod
    def _seg_dist(kind, geo, x, y):
        """Signed px distance from a local point (pixel OR crown center) to
        an open-boundary seg; negative = the open side. kind 'cut' measures
        to the 45-degree line, 'edge' to the tile side, 'corner' to the
        lattice point a lone open diagonal touches."""
        if kind == "cut":
            return diag_s(geo, x, y) * 0.5
        if kind == "corner":
            px_, py_ = geo
            return ((x - px_) ** 2 + (y - py_) ** 2) ** 0.5
        if geo == N:
            return y + 0.5
        if geo == S:
            return T - 0.5 - y
        if geo == W:
            return x + 0.5
        return T - 0.5 - x                                 # E

    def _arc_cell(self, X, Y, masks, phase, own, shade, gap, lobes=None):
        """Shared silhouette machinery for lobed masses (forest crowns,
        mountain rock lobes): build open-boundary segs from the `own`
        neighbor classes, keep pattern instances whose whole disc stays
        inside every boundary (small strip lobes as the fallback for
        narrow runs), then paint kept lobes via shade(), a 1px `gap`
        outline ring around the union, and the neighbor's fabric in the
        bays — the silhouette follows the lobes, never the tile grid, and
        everything stays on the LOWER canvas. Returns False for interior
        cells (no open boundary): the caller paints its pure fabric."""
        segs = []                                          # (kind, geo, class)
        for c2, bits in masks.items():
            if c2.startswith("__") or c2 not in own:
                continue
            cn, rst = cut_of(bits)
            if cn is not None:
                segs.append(("cut", cn, c2))
            for dx, dy, bit in DIRS:
                if not rst & bit:
                    continue
                if bit in (N, E, S, W):
                    segs.append(("edge", bit, c2))
                else:                                      # lone open diagonal:
                    segs.append(("corner", self._CORNER_PT[bit], c2))
        if not segs:
            return False
        kept = []
        for pool in (lobes or self._CROWNS16, self._SYNTH16):
            for cx, cy, r in pool:
                for oy in (-16, 0, 16):
                    for ox in (-16, 0, 16):
                        ax, ay = cx + ox, cy + oy
                        if all(self._seg_dist(k, g, ax, ay) >= r - 1.0
                               for k, g, _ in segs):
                            kept.append((ax, ay, r))
            if kept:                                       # synth only as fallback
                break
        w0, z0 = 16 * (phase & 1), 16 * (phase >> 1)
        for v in range(T):
            for u in range(T):
                win, wkey, qmin = None, (-99, -99), 9.9
                for ax, ay, r in kept:
                    dx, dy = u - ax, v - ay
                    q = (dx * dx + dy * dy) / (r * r)
                    if q < qmin:
                        qmin = q
                    if q <= 1.0 and (ay, ax) > wkey:
                        win, wkey = (dx / r, dy / r, q), (ay, ax)
                if win is not None:
                    c = shade(u + w0, v + z0, win, kept)
                elif qmin <= 1.30:
                    c = gap                                # silhouette outline +
                                                           # dark Vs between lobes
                else:                                      # the open bay
                    D = min(segs,
                            key=lambda s: self._seg_dist(s[0], s[1], u, v))[2]
                    c = self._fab(D, u, v)
                self.bg.put(X + u, Y + v, c)
        return True

    def _forest_cell(self, X, Y, masks, phase):
        """Forest rim, CT-style: the boundary silhouette IS the crown arcs
        (see _arc_cell); the surviving edge crowns' round tops and dark
        under-rims form the outline."""
        shade = (lambda w, z, win, kept:
                 self._crown_px(win[0], win[1], win[2], w, z))
        if not self._arc_cell(X, Y, masks, phase, GROUND, shade,
                              self.FOREST[5]):
            for v in range(T):                             # interior canopy
                for u in range(T):
                    self.bg.put(X + u, Y + v, self._px_forest(u, v, phase))

    def _mountain_cell(self, X, Y, masks, phase=0):
        """Massif rim on the same silhouette machinery, cone-field shaded:
        the kept lobes ARE the relief, and snow whitens the summits
        wherever the cell fronts open ground to the north — a scalloped
        white crest instead of the old straight bands."""
        open_ = 0
        for c2, bits in masks.items():
            if not c2.startswith("__") and c2 in MOUNT_OWN:
                open_ |= bits
        snow = bool(open_ & (N | NE | NW))
        shade = (lambda w, z, win, kept:
                 self._rock_px(win[0], win[1], win[2], w, z, snow))
        if not self._arc_cell(X, Y, masks, phase, MOUNT_OWN, shade,
                              self.ROCK[5]):
            for v in range(T):                             # interior massif
                for u in range(T):
                    self.bg.put(X + u, Y + v, self._px_mountain(u, v, phase))

    # -- shared overlays on ground cells --------------------------------------------------
    def _ground_overlays(self, X, Y, masks, cls):
        """Contact shade under built structures to the north — but NOT on
        the waste pan, where the dark band pops off the hot field as a
        gray underline (crystals ground themselves with root rubble).
        Forest and mountain get NOTHING here — their arc silhouettes
        recede into their own cells, so any band stamped on the neighbor
        floats disconnected (and reads as a z glitch on the chibi)."""
        struct_n = masks.get("__struct__", 0) & (N | NE | NW)
        if struct_n & N and cls != "waste":
            for v, a in ((0, 0.32), (1, 0.20), (2, 0.10)):
                for u in range(T):
                    self.bg.mix(X + u, Y + v, (26, 20, 52, 255), a)

    # -- interior hash variants ------------------------------------------------------------
    def _variant(self, tx, ty, cls, X, Y, band):
        k = h2(tx, ty, 81)
        if cls == "sea" and band >= 2:
            if k % 11 == 0:
                for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1)):
                    self.bg.put(X + 7 + dx, Y + 6 + dy, self.SPARK)
            elif k % 17 == 9:
                self.bg.put(X + 11, Y + 12, self.SPARK)
                self.bg.put(X + 12, Y + 12, self.SPARK)
        elif cls == "grass":
            if k % 5 == 0:
                for u, v in ((5, 6), (6, 6), (5, 7), (12, 3), (3, 12)):
                    self.bg.put(X + u, Y + v, self.GRASS[3])
                self.bg.put(X + 5, Y + 5, self.GRASS[1])
            elif k % 7 == 3:
                self.bg.put(X + 9, Y + 10, self.ROCK[2])
                self.bg.put(X + 10, Y + 10, self.ROCK[3])
            elif k % 11 == 2:                              # a squat boulder
                r = self.ROCK
                self.bg.rect(X + 5, Y + 9, X + 10, Y + 12, r[2])
                self.bg.rect(X + 6, Y + 8, X + 9, Y + 8, r[1])
                self.bg.rect(X + 5, Y + 12, X + 10, Y + 12, r[4])
                self.bg.put(X + 5, Y + 9, r[3])
                self.bg.put(X + 10, Y + 9, r[3])
                self.bg.put(X + 8, Y + 10, r[3])
                for u in range(5, 11):                     # contact shade
                    self.bg.put(X + u, Y + 13, self.GRASS[4])
            elif k % 13 == 4:                              # mossy sink
                g = self.GRASS
                for u, v in ((6, 5), (7, 5), (8, 5), (5, 6), (9, 6),
                             (6, 7), (7, 7), (8, 7)):
                    self.bg.put(X + u, Y + v, g[3])
                self.bg.put(X + 7, Y + 6, g[4])
            elif k % 17 == 6:                              # one wild bloom
                self.bg.put(X + 7, Y + 7, self.PINK)
                self.bg.put(X + 7, Y + 6, self.SPARK)
                self.bg.put(X + 6, Y + 8, self.GRASS[1])
            elif k % 19 == 8:                              # a sedge patch
                g = self.GRASS
                for u, v in ((10, 4), (12, 4), (14, 5), (11, 5), (13, 6)):
                    self.bg.put(X + u, Y + v, g[1])
                    self.bg.put(X + u, Y + v + 1, g[3])
        elif cls == "forest":
            if k % 29 == 0:                                # understory gap: a
                f = self.FOREST                            # graded peek at the
                for v in range(4, 12):                     # floor, not a void
                    for u in range(4, 13):
                        dx, dy = (u - 8.0) / 4.6, (v - 7.5) / 3.6
                        q = dx * dx + dy * dy
                        if q <= 1.0:
                            self.bg.put(X + u, Y + v, f[4] if q > 0.5 else f[5])
                for ux, vy in ((6, 7), (10, 6)):
                    self.bg.rect(X + ux, Y + vy, X + ux, Y + vy + 3,
                                 self.TRUNK[1])
            elif k % 7 == 0:
                for u, v in ((3, 2), (4, 2), (11, 10), (12, 11)):
                    self.bg.put(X + u, Y + v, self.FOREST[0])
        elif cls == "mountain":
            if k % 13 == 3:                                # pale quartz seams
                for u, v in ((4, 5), (5, 5), (11, 9), (12, 10), (7, 12)):
                    self.bg.put(X + u, Y + v, self.ROCK[0])
            elif k % 7 == 0:                               # a dark cave nick
                self.bg.rect(X + 6, Y + 9, X + 9, Y + 10, self.ROCK[5])
                self.bg.rect(X + 7, Y + 8, X + 8, Y + 8, self.ROCK[5])
        elif cls == "waste":
            if k % 13 == 5:                                # glowing crystal shard
                self.crystal_cells.append((tx, ty))
                a = self.ACCENT
                for dy in range(5):
                    hw = max(0, 2 - dy // 2)
                    for dx in range(-hw, hw + 1):
                        c = a if abs(dx) < hw else (150, 84, 210, 255)
                        self.bg.put(X + 7 + dx, Y + 11 - dy, c)
                self.bg.put(X + 7, Y + 6, (244, 226, 255, 255))
            elif k % 11 == 0:                              # a bare snag: trunk
                d0, d1, d2 = self.DEAD                     # + two diagonal forks
                for i in range(7):
                    self.bg.put(X + 7, Y + 13 - i, d1 if i < 5 else d0)
                    self.bg.put(X + 8, Y + 13 - i, d2)
                for j, (bx, by) in enumerate(((6, 6), (5, 5), (4, 4))):
                    self.bg.put(X + bx, Y + by, d1 if j < 2 else d0)
                for j, (bx, by) in enumerate(((9, 5), (10, 4), (11, 3))):
                    self.bg.put(X + bx, Y + by, d2 if j < 2 else d0)
                self.bg.put(X + 7, Y + 6, d0)              # crown tip
                self.bg.put(X + 6, Y + 13, d2)             # root flare
                self.bg.put(X + 9, Y + 13, d2)

    # -- compose --------------------------------------------------------------------------
    def paint_terrain(self):
        m = self.m
        for ty in range(m.rows_n):
            for tx in range(m.cols):
                cls = self.cls_at(tx, ty)
                X, Y = tx * T, ty * T
                masks = {"__struct__": 0}
                interior = True
                conn = 0                                   # trail/deck links
                fconn = 0                                  # fence links
                for dx, dy, bit in DIRS:
                    nch = m.at(tx + dx, ty + dy)
                    ncls = self._cls[nch] if nch else cls
                    if ncls != cls:
                        masks[ncls] = masks.get(ncls, 0) | bit
                        if ncls not in FAMILY[cls]:
                            interior = False
                    if ncls in ROADY or ncls == "bridge":
                        conn |= bit
                    if ncls == "fence":
                        fconn |= bit
                    if nch and nch in self._struct:
                        masks["__struct__"] |= bit
                band = min(self._dland[ty][tx], 4) - 1
                phase = ((tx & 1) | ((ty & 1) << 1)) if interior else 0
                if cls == "sea":
                    self._sea_cell(X, Y, masks, tx, ty, phase)
                elif cls == "river":
                    self._river_cell(X, Y, masks)
                elif cls == "bridge":
                    water = masks.get("river", 0) | masks.get("sea", 0)
                    land = 0
                    for c2, bits in masks.items():
                        if c2 not in WATERC and not c2.startswith("__"):
                            land |= bits
                    self._bridge_cell(X, Y, water, land)
                elif cls == "beach":
                    self._beach_cell(X, Y, masks)
                elif cls in GRASSY:
                    self._grassy_cell(X, Y, cls, phase)
                elif cls == "waste":
                    self._waste_cell(X, Y, masks, tx, ty, phase)
                elif cls in ROADY:
                    self._roady_cell(X, Y, cls, conn, tx, ty)
                elif cls == "fence":
                    self._fence_cell(X, Y, fconn & (N | E | S | W))
                elif cls == "forest":
                    self._forest_cell(X, Y, masks, phase)
                elif cls == "mountain":
                    self._mountain_cell(X, Y, masks, phase)
                # spills + walk-behind canopy on anything that reads as ground
                # (but never INSIDE a landmark footprint — a struct cell south
                # of another struct cell would band the prop's own underlay)
                if cls in GROUND and m.at(tx, ty) not in self._struct:
                    self._ground_overlays(X, Y, masks, cls)
                if interior and cls in ("sea", "grass", "forest", "mountain", "waste") \
                        and m.at(tx, ty) not in self._struct:
                    # (prop cells skip variants: no snow crest / crystal shard
                    # peeking through a landmark's transparent gaps)
                    self._variant(tx, ty, cls, X, Y, band)
