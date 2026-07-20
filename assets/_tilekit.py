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
from _tiles import slice_atlas, pack_tiles, write_atlas, write_tileset_tres, \
    write_layout

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


def sprite_img(sp, w, h):
    """Crop a (square, sparse) prop Sprite to its w x h footprint as an Img —
    the emit_prop() input for props authored on the _propkit canvas."""
    img = Img(w, h)
    img.blit_cell(sp, 0, 0)
    return img


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
        self._props = []               # Tier-3 manifest rows (emit_prop)
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

    def comps(self, chars):
        """4-connected components of the chars' cells, each as a cell list
        (the place_each / emit_prop each=True idiom)."""
        m = self.m
        todo = {(x, y) for y in range(m.rows_n) for x in range(m.cols)
                if m.at(x, y) in chars}
        assert todo, f"no {chars!r} cells in {self.name}.txt"
        out = []
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
            out.append(comp)
        return out

    def comp_bbox(self, comp):
        xs, ys = [c[0] for c in comp], [c[1] for c in comp]
        return (min(xs), min(ys), max(xs), max(ys))

    # -- prop placement -----------------------------------------------------------------
    def bake_shadow(self, chars, shadow_h, each=False):
        """Contact-shadow band across a footprint's bottom rows: darken the
        already-painted ground toward the scene's dark, whatever fabric is
        under it. (Room overrides this with its repaint-the-fabric version,
        which the interiors' whole-tile light dispatch depends on.)
        `each`: one band per connected component — a shared-char prop set
        (the hall's four benches) must NOT shade the combined bbox, which
        smears the band across the open cells between them."""
        boxes = [self.comp_bbox(c) for c in self.comps(chars)] if each \
                else [self.bbox(chars)]
        for box in boxes:
            X, Y, XW, YH = self.px(box)
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
        assert any(p for row in sprite.px for p in row), \
            f"upper sprite for {chars!r} is fully transparent (dead split)"
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
        for comp in self.comps(chars):
            self.bg.blit_cell(sprite, min(c[0] for c in comp) * T,
                              min(c[1] for c in comp) * T)

    def emit_prop(self, name, chars, img, fname=None, top=None, base_inset=0,
                  hframes=1, each=False):
        """A y-sorted WORLD prop (Tier 3): save its PNG beside the atlas and
        record a manifest row that scene/prop_spawner.gd spawns into the
        scene's y-sorted World at the chars' map bbox. For anything a body
        can stand both north and south of — the static layers can't sort it
        (see DESIGN.md "Z-order / layering doctrine").

        `top`: anchor the sprite's top at bbox_top + top px instead of its
        bottom at the bbox's south edge (the bed-cover crop case).
        `base_inset`: y-sort baseline pulled up from the south edge (a baked
        contact shadow's rows don't count as body).
        `each`: one sprite per connected component of the chars (the
        place_each idiom — several lamp posts share one char)."""
        self.bbox(chars)                   # assert the chars exist in the map
        fname = fname or f"{self.name}_{name.lower()}.png"
        img.save(os.path.join(OUTDIR, fname))
        opts = ([f"anchor=top:{int(top)}"] if top is not None else []) + \
               ([f"base_inset={int(base_inset)}"] if base_inset else []) + \
               ([f"hframes={hframes}"] if hframes > 1 else []) + \
               (["each"] if each else [])
        self._props.append(" ".join(["prop", name, chars, fname] + opts))

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

    def _lower_frames(self):
        """Lower-canvas animation frames. Scenes with animated fabric
        (OverWorld's water) override; default is static — cells identical
        across every frame dedupe to plain static tiles either way."""
        return [self.bg]

    def finish(self):
        os.makedirs(OUTDIR, exist_ok=True)
        tiles, seen = [], {}
        _, lower = slice_atlas(self._lower_frames(), tiles, seen)
        _, upper = slice_atlas(self.ov, tiles, seen, skip_empty=True)
        cells, coords = pack_tiles(tiles)
        write_atlas(os.path.join(OUTDIR, f"{self.name}_tiles.png"), cells)
        write_tileset_tres(os.path.join(OUTDIR, f"{self.name}_tiles.tres"),
                           f"res://assets/tilesets/{self.name}_tiles.png", coords)
        write_layout(os.path.join(OUTDIR, f"{self.name}_layout.txt"),
                     {"lower": lower, "upper": upper}, coords,
                     f"from assets/maps/{self.name}.txt")
        if self._props:
            with open(os.path.join(OUTDIR, f"{self.name}_props.txt"), "w") as f:
                f.write(f"; y-sorted World props from assets/maps/"
                        f"{self.name}.txt — see scene/prop_spawner.gd\n")
                f.write("\n".join(self._props) + "\n")
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
