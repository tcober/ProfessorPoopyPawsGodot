#!/usr/bin/env python3
"""Shared base of every TILED scene (interiors AND the overworld).

One module owns what _interior.py's Room and _overworld_tiles.py's OverWorld
would otherwise duplicate: the int-casting canvas, the shared material ramps
(one hardware store for the whole game), map-footprint geometry (bbox/px),
prop placement (place / place_upper / place_split with a baked contact
shadow), the additive glow writer, and finish() — the slice/dedupe/write
plumbing that turns the LOWER + UPPER compositions into one shared atlas,
a TileSet .tres and a layout file (see _tiles.py).

The disciplines this kit enforces (see DESIGN.md "Art pipeline"):
  * repeating art is a pure function of 16-periodic pixel coordinates (or,
    on the overworld, of the cell's neighbor configuration), so recurring
    cells are byte-identical and the slicer collapses them;
  * variety is whole-tile variants hash-placed per cell — never per-pixel
    noise, which makes every tile unique and kills the dedupe;
  * props stay strictly inside their map footprint.

Stdlib-only, deterministic. Used by _interior.py and _overworld_tiles.py.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import lerp, Img, ZONE_TILE
from _maps import MapData
from _palette import SCENES, ramp
from _tiles import slice_atlas, write_atlas, write_tileset_tres, write_layout

T = ZONE_TILE
OUTDIR = os.path.join(HERE, "tilesets")

# ---- shared materials: one house, one hardware store -------------------------------
TIMBER = ramp((146, 94, 62), "violet", 6)     # furniture wood
BRASS = ramp((240, 188, 98), "violet", 4)
STEEL = ramp((170, 168, 206), "violet", 4)
COPPER = ramp((198, 112, 72), "violet", 6)
IRON = ramp((104, 100, 124), "violet", 4)
STONER = ramp((144, 138, 170), "violet", 6)   # masonry
GLASS = (216, 226, 240, 255)
MINT = (132, 246, 152, 255)
VIOLETF = (188, 132, 232, 255)
PAPER = (240, 232, 226, 255)
PAPERD = (206, 196, 204, 255)
RED = (226, 62, 92, 255)
SPEC = (255, 255, 250, 255)
WATER = (150, 210, 214, 255)
STEAM = (226, 224, 240, 255)
VOID = (10, 8, 24, 255)
DROP1 = (22, 15, 42, 255)                     # darkness bands past a floor edge
DROP2 = (13, 10, 30, 255)
OUTLINE = (26, 17, 36, 255)                   # prop silhouette edge

# additive night-glow accents (shared by the overworld + town generators)
GLOW_WARM = (255, 200, 120)                   # lamp / window / coal light
GLOW_MINT = (150, 246, 190)                   # gauge / rose-window glow


class Canvas(Img):
    """Scene canvas: int-casting put/rect."""

    def put(self, x, y, c):
        super().put(int(x), int(y), c)

    def rect(self, x0, y0, x1, y1, c):
        super().rect(int(x0), int(y0), int(x1), int(y1), c)


class TileScene:
    """One tiled scene: map + canvases + palette + placement + plumbing.

    A driver subclass (Room, OverWorld) adds its terrain painters; the
    generator config constructs it, paints terrain, places props from map
    feature bboxes, then finish()es. Everything positional derives from the
    map file — move a feature char and the scene follows.
    """

    def __init__(self, map_name, scene_key, fill=VOID):
        self.name = map_name
        self.m = MapData(os.path.join(HERE, "maps", map_name + ".txt"))
        self.W, self.H = self.m.cols * T, self.m.rows_n * T
        self.bg = Canvas(self.W, self.H, fill)
        self.ov = Canvas(self.W, self.H)
        sc = SCENES[scene_key]
        self.scene = sc
        self.shadow = sc["shadow"]
        self.ACCENT = sc["accent"]
        self.mats = dict(sc.get("mats", {}))

    def mat(self, name, tones=6, spread=1.0, shadow=None):
        """Material ramp: the scene's hand ramp if it has one, else derived
        from the seed color."""
        hand = self.scene.get("ramps", {}).get(name)
        if hand:
            return list(hand)      # copy: callers must not mutate the registry
        return ramp(self.mats[name], shadow or self.shadow, tones, spread)

    # -- geometry ---------------------------------------------------------------------
    def bbox(self, chars):
        cs = [(x, y) for y in range(self.m.rows_n) for x in range(self.m.cols)
              if self.m.at(x, y) in chars]
        assert cs, f"no {chars!r} cells in {self.name}.txt"
        xs, ys = [c[0] for c in cs], [c[1] for c in cs]
        return (min(xs), min(ys), max(xs), max(ys))

    def px(self, bbox):
        """(X, Y, W, H) pixel rect of a tile bbox."""
        return (bbox[0] * T, bbox[1] * T,
                (bbox[2] - bbox[0] + 1) * T, (bbox[3] - bbox[1] + 1) * T)

    # -- prop placement -----------------------------------------------------------------
    def bake_shadow(self, chars, shadow_h):
        """Contact-shadow band across a footprint's bottom rows: darken the
        already-painted ground toward the scene's dark, whatever fabric is
        under it. (Room overrides this with its repaint-the-fabric version,
        which the interiors' whole-tile light dispatch depends on.)"""
        X, Y, XW, YH = self.px(self.bbox(chars))
        for y in range(Y + YH - shadow_h, Y + YH):
            for x in range(X + 1, X + XW - 1):
                base = self.bg.get(x, y)
                self.bg.put(x, y, lerp(base[:3], VOID[:3], 0.35) + (255,))

    def place(self, chars, sprite, shadow_h=0):
        """Blit a prop Sprite at its feature bbox; bake a contact-shadow band
        across the footprint's bottom rows first."""
        X, Y, XW, YH = self.px(self.bbox(chars))
        if shadow_h:
            self.bake_shadow(chars, shadow_h)
        self.bg.blit_cell(sprite, X, Y)

    def place_upper(self, chars, sprite):
        X, Y, _, _ = self.px(self.bbox(chars))
        self.ov.blit_cell(sprite, X, Y)

    def place_split(self, chars, lower, upper, shadow_h=0):
        """A prop split across the layers (the bed_parts idiom generalized):
        `lower` bakes under entities, `upper` rides over them — bodies pass
        behind gate arches and lintels."""
        self.place(chars, lower, shadow_h)
        self.place_upper(chars, upper)

    def place_each(self, chars, sprite):
        """Blit one sprite per CONNECTED COMPONENT of the feature chars (two
        lamp posts share a char; each gets the same sprite, and identical
        cells dedupe to the same atlas tiles)."""
        m = self.m
        todo = {(x, y) for y in range(m.rows_n) for x in range(m.cols)
                if m.at(x, y) in chars}
        assert todo, f"no {chars!r} cells in {self.name}.txt"
        while todo:
            comp = [todo.pop()]
            i = 0
            while i < len(comp):
                cx, cy = comp[i]
                i += 1
                for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if n in todo:
                        todo.remove(n)
                        comp.append(n)
            self.bg.blit_cell(sprite, min(c[0] for c in comp) * T,
                              min(c[1] for c in comp) * T)

    # -- output --------------------------------------------------------------------------
    def write_overlay(self, suffix, draw_fn):
        """A full-map static overlay PNG beside the atlas (additive glow,
        multiply cloud-shade, ...) — scene .tscn picks the blend mode."""
        img = Img(self.W, self.H)
        draw_fn(img)
        img.save(os.path.join(OUTDIR, f"{self.name}_{suffix}.png"))

    def write_glow(self, draw_fn):
        self.write_overlay("glow", draw_fn)

    @staticmethod
    def glow_blob(img, cx, cy, r, color, a):
        """One radial dab on an additive glow overlay: alpha peaks at the
        center and falls to 0 at radius r."""
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                q = (dx * dx + dy * dy) / float(r * r)
                if q <= 1.0:
                    img.put(int(cx) + dx, int(cy) + dy,
                            color + (int(a * (1.0 - q)),))

    def finish(self):
        os.makedirs(OUTDIR, exist_ok=True)
        tiles, seen = [], {}
        _, lower = slice_atlas(self.bg, tiles, seen)
        _, upper = slice_atlas(self.ov, tiles, seen, skip_empty=True)
        write_atlas(os.path.join(OUTDIR, f"{self.name}_tiles.png"), tiles)
        write_tileset_tres(os.path.join(OUTDIR, f"{self.name}_tiles.tres"),
                           f"res://assets/tilesets/{self.name}_tiles.png", len(tiles))
        write_layout(os.path.join(OUTDIR, f"{self.name}_layout.txt"),
                     {"lower": lower, "upper": upper},
                     f"from assets/maps/{self.name}.txt")
        n_upper = sum(1 for row in upper for i in row if i is not None)
        print(f"{len(tiles)} unique tiles from {self.m.cols * self.m.rows_n} cells "
              f"({n_upper} upper-layer cells)")
        if "--preview" in sys.argv:
            out = sys.argv[sys.argv.index("--preview") + 1]
            for y in range(self.H):
                for x in range(self.W):
                    p = self.ov.get(x, y)
                    if p[3]:
                        self.bg.put(x, y, p)
            self.bg.save(out if os.path.isabs(out) else os.path.join(HERE, out))
