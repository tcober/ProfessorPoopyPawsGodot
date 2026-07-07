#!/usr/bin/env python3
"""Interior room kit — the shared skeleton of every tiled interior.

The generic tiled-scene plumbing (canvas, materials, bbox/px geometry, prop
placement, slice/dedupe/write) lives in _tilekit.py's TileScene, shared with
the overworld driver (_overworld_tiles.py). This module owns what is
INTERIOR: the 16-periodic terrain fabrics (walls with wainscot, weave +
flagstone floors), the per-cell terrain painters with their whole-tile light
dispatch, and the stair/rail/jamb cell painters. A room generator becomes a
thin CONFIG: pick the scene palette, declare terrain rules and light pools,
`place()` props from `_interior_props.py`, `finish()`.

The disciplines this kit enforces (see DESIGN.md "Art pipeline"):
  * fabric painters are pure functions of 16-periodic pixel coordinates, so
    repeated cells are byte-identical and the slicer collapses them;
  * light and shade quantize per tile (lit / ordered-dither fringe / shadow),
    never per-pixel gradients;
  * variety is whole-tile variants hash-placed per cell (worn floor, plank
    knot) — one extra atlas tile each;
  * props stay strictly inside their map footprint; their contact shadow is
    shaded fabric baked by `place()` before the blit.

Stdlib-only, deterministic. Used by assets/_gen_tileset_*.py.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, lerp
from _palette import SCENES, ramp
# Shared kit + materials, re-exported so props/generators keep importing from
# here (one hardware store, one import path).
from _tilekit import (TileScene, Canvas, T, OUTDIR,
                      TIMBER, BRASS, STEEL, COPPER, IRON, STONER, GLASS, MINT,
                      VIOLETF, PAPER, PAPERD, RED, SPEC, WATER, FROST, STEAM,
                      VOID, DROP1, DROP2, OUTLINE)

# ---- terrain fabrics: pure 16-periodic pixel functions ------------------------------


def plank_px(x, y, wallr):
    """Wall planks: 8px courses, staggered butt seams, sparse grain + nails."""
    v = y % 8
    if v == 7:
        i = 4                                  # course seam shadow
    elif v == 0:
        i = 1                                  # lit top edge
    elif v <= 4:
        i = 2
    else:
        i = 3
    seam = 5 if (y // 8) % 2 == 0 else 12
    if x % 16 == seam and 1 <= v <= 5:
        i = max(i, 3)                          # butt seam
    if x % 16 == seam and v == 1:
        return wallr[5]                        # nail head at the seam top
    if v == 3 and x % 16 in (2, 3, 9, 10):
        i = 3 if i == 2 else i                 # grain dashes
    return wallr[i]


def weave_px(x, y, ramp6, shade=0):
    """Teal basket weave: 8px slats alternating direction — quiet slat bands
    (dark seams, one lit edge) with a sparse under-thread tick."""
    horiz = ((x % 16) // 8 + (y % 16) // 8) % 2 == 0
    w = y % 8 if horiz else x % 8              # across the slat
    t = x % 8 if horiz else y % 8              # along the slat
    if w in (0, 7):
        i = 4
    elif w == 1:
        i = 1
    elif w <= 5:
        i = 2
    else:
        i = 3
    if t == 7 and 1 <= w <= 6:
        i = max(i, 3)                          # under-weave tuck shadow
    return ramp6[min(5, i + shade)]


def flag_px(x, y, ramp6, shade=0):
    """Slate flagstones: 16x8 running-bond slabs, chisel marks + corner nicks."""
    v = y % 8
    u = (x + 8 * ((y // 8) % 2)) % 16
    if v == 0 or u == 0:
        i = 3                                  # mortar seam
    elif v == 1 and u % 5 == 1:
        i = 1                                  # lit chisel mark
    elif v == 1 and u == 14:
        i = 3                                  # corner nick
    elif v in (3, 5) and u in (4, 11):
        i = 3                                  # face pitting
    else:
        i = 2
    return ramp6[min(5, i + shade)]


class Room(TileScene):
    """One tiled interior: map + geometry + canvases + palette + plumbing.

    The generator config constructs it, declares light pools, paints terrain
    (with room-specific cell painters for its odd cells), places props, then
    finish()es. Everything positional derives from the map file — move a
    feature char and the room follows.
    """

    def __init__(self, map_name, scene_key, floor_px_fn, lit_target,
                 floor_chars=".g", lit_blend=0.62):
        super().__init__(map_name, scene_key, VOID)
        self.floor_px = floor_px_fn
        self.floor_chars = floor_chars
        sc = SCENES[scene_key]
        self.WALLR = ramp(sc["mats"]["wall"], sc["shadow"], 6)
        self.FLOORR = ramp(sc["mats"]["floor"], sc["shadow"], 6)
        # lit fabric: one step lighter, blended hard toward the light source
        self.FLOOR_LIT = [tuple(lerp(self.FLOORR[max(0, i - 1)][:3],
                                     lit_target, lit_blend)) + (255,)
                          for i in range(6)]
        # geometry from the map
        m = self.m
        nonvoid = [x for y in range(m.rows_n) for x in range(m.cols)
                   if m.at(x, y) != "V"]
        self.LCOL, self.RCOL = min(nonvoid), max(nonvoid)
        self.WALL_TOP = self.bbox("#")[1]
        self.FLOOR_ROW = self.bbox(floor_chars[0])[1]
        self.WALL_BASE = self.FLOOR_ROW - 1
        self.lit_cells = set()
        self.fringe_cells = set()
        self.shadow_rows = (self.FLOOR_ROW,)

    # -- terrain cells ----------------------------------------------------------------
    def floor_cell(self, tx, ty, kind=None):
        if kind is None:
            if (tx, ty) in self.lit_cells:
                kind = "lit"
            elif (tx, ty) in self.fringe_cells:
                kind = "fringe"
            elif ty in self.shadow_rows:
                kind = "shadow"
            else:
                kind = "plain"
        x0, y0 = tx * T, ty * T
        for y in range(y0, y0 + T):
            for x in range(x0, x0 + T):
                if kind == "lit":
                    c = self.floor_px(x, y, self.FLOOR_LIT)
                elif kind == "fringe":
                    lit = ((x // 2) + (y // 2)) % 2 == 0
                    c = self.floor_px(x, y, self.FLOOR_LIT if lit else self.FLOORR)
                elif kind == "shadow":
                    c = self.floor_px(x, y, self.FLOORR, 1)
                else:
                    c = self.floor_px(x, y, self.FLOORR)
                self.bg.put(x, y, c)
        if kind == "plain" and h2(tx, ty, 7) % 13 == 0:   # whole-tile worn variant
            for px_, py_ in ((4, 5), (5, 5), (10, 12), (13, 7)):
                self.bg.put(x0 + px_, y0 + py_, self.FLOORR[5])
            self.bg.rect(x0 + 6, y0 + 10, x0 + 9, y0 + 10, self.FLOORR[4])

    def wall_cell(self, tx, ty):
        """Back-wall cell: planks, auto-dressed by position — cornice at the
        top, WAINSCOT paneling on the base row, dark edges at the room sides,
        hash-placed knot variants in the field."""
        x0, y0 = tx * T, ty * T
        wallr = self.WALLR
        for y in range(y0, y0 + T):
            for x in range(x0, x0 + T):
                self.bg.put(x, y, plank_px(x, y, wallr))
        dressed = False
        if ty == self.WALL_TOP:                          # cornice beam vs the void
            self.bg.rect(x0, y0, x0 + T - 1, y0, wallr[5])
            self.bg.rect(x0, y0 + 1, x0 + T - 1, y0 + 1, wallr[4])
            self.bg.rect(x0, y0 + 2, x0 + T - 1, y0 + 2, wallr[1])
            dressed = True
        if ty == self.WALL_BASE:                         # wainscot + baseboard
            self.bg.rect(x0, y0 + 5, x0 + T - 1, y0 + 5, TIMBER[1])   # chair rail
            self.bg.rect(x0, y0 + 6, x0 + T - 1, y0 + 6, TIMBER[3])
            self.bg.rect(x0, y0 + 7, x0 + T - 1, y0 + 12, TIMBER[2])  # panels
            for px_ in (x0 + 3, x0 + 11):
                self.bg.rect(px_, y0 + 8, px_, y0 + 11, TIMBER[4])    # grooves
            self.bg.rect(x0 + 7, y0 + 8, x0 + 7, y0 + 11, TIMBER[1])  # lit bevel
            self.bg.rect(x0, y0 + 13, x0 + T - 1, y0 + 14, TIMBER[3])
            self.bg.rect(x0, y0 + 13, x0 + T - 1, y0 + 13, TIMBER[4])
            self.bg.rect(x0, y0 + 15, x0 + T - 1, y0 + 15, TIMBER[5]) # floor junction
            dressed = True
        if tx == self.LCOL:
            self.bg.rect(x0, y0, x0, y0 + T - 1, wallr[5])
            self.bg.rect(x0 + 1, y0, x0 + 1, y0 + T - 1, wallr[4])
            dressed = True
        if tx == self.RCOL:
            self.bg.rect(x0 + T - 1, y0, x0 + T - 1, y0 + T - 1, wallr[5])
            self.bg.rect(x0 + T - 2, y0, x0 + T - 2, y0 + T - 1, wallr[4])
            dressed = True
        if not dressed and h2(tx, ty, 11) % 9 == 0:      # whole-tile knot variant
            self.bg.rect(x0 + 9, y0 + 3, x0 + 11, y0 + 5, wallr[3])
            self.bg.put(x0 + 10, y0 + 4, wallr[5])
            self.bg.put(x0 + 9, y0 + 3, wallr[4])
            self.bg.put(x0 + 11, y0 + 5, wallr[4])

    def side_cell(self, tx, ty):
        """Side wall strip beside the floor: vertical boards framing the room."""
        x0, y0 = tx * T, ty * T
        wallr = self.WALLR
        left = tx == self.LCOL
        for y in range(y0, y0 + T):
            for x in range(x0, x0 + T):
                u = (x - x0) if left else (T - 1 - (x - x0))
                if u <= 0:
                    c = wallr[5]
                elif u == 1:
                    c = wallr[4]
                elif u >= 15:
                    c = wallr[5]
                elif u == 14:
                    c = wallr[4]
                elif u == 2:
                    c = wallr[2]
                else:
                    c = wallr[3] if (x % 5) else wallr[4]
                self.bg.put(x, y, c)

    def south_cell(self, tx, ty):
        """South wall band: plank face with a lit cap, sinking dark at its foot."""
        x0, y0 = tx * T, ty * T
        wallr = self.WALLR
        for y in range(y0, y0 + T):
            for x in range(x0, x0 + T):
                self.bg.put(x, y, plank_px(x, y, wallr))
        self.bg.rect(x0, y0, x0 + T - 1, y0, wallr[1])
        self.bg.rect(x0, y0 + 1, x0 + T - 1, y0 + 1, wallr[2])
        self.bg.rect(x0, y0 + 13, x0 + T - 1, y0 + 13, wallr[4])
        self.bg.rect(x0, y0 + 14, x0 + T - 1, y0 + 15, wallr[5])
        if tx == self.LCOL:
            self.bg.rect(x0, y0, x0 + 1, y0 + T - 1, wallr[5])
        if tx == self.RCOL:
            self.bg.rect(x0 + T - 2, y0, x0 + T - 1, y0 + T - 1, wallr[5])

    def jamb_cell(self, tx, ty, stair_char="s", void_backed=False):
        """Stair-alcove side wall: planks (void-backed above the cornice, or
        entirely when the jamb floats past the room silhouette) with a dark
        inner face toward the treads."""
        x0, y0 = tx * T, ty * T
        left_of = self.m.at(tx + 1, ty) == stair_char
        if ty >= self.WALL_TOP and not void_backed:
            for y in range(y0, y0 + T):
                for x in range(x0, x0 + T):
                    self.bg.put(x, y, plank_px(x, y, self.WALLR))
        for y in range(y0, y0 + T):
            for x in range(x0, x0 + T):
                u = (T - 1 - (x - x0)) if left_of else (x - x0)
                if u <= 1:
                    self.bg.put(x, y, TIMBER[5])
                elif u == 2:
                    self.bg.put(x, y, TIMBER[4])
        if ty < self.WALL_TOP:
            self.bg.rect(x0, y0, x0 + T - 1, y0, self.WALLR[5])

    def stair_cell(self, tx, ty, top_row, treads):
        """Two 8px treads per cell, indexed into a depth palette `treads`
        (list of (edge, body) darkest-first)."""
        x0, y0 = tx * T, ty * T
        d = (ty - top_row) * 2
        for half in (0, 1):
            edge, body = treads[min(len(treads) - 1, d + half)]
            yy = y0 + half * 8
            self.bg.rect(x0, yy, x0 + T - 1, yy, edge)
            self.bg.rect(x0, yy + 1, x0 + T - 1, yy + 7, body)

    def drop_cell(self, tx, ty, stair=False):
        """A floor edge falling into darkness (loft rail row lower art)."""
        x0, y0 = tx * T, ty * T
        self.bg.rect(x0, y0, x0 + T - 1, y0, TIMBER[1])
        self.bg.rect(x0, y0 + 1, x0 + T - 1, y0 + 2, TIMBER[3])
        if stair:
            self.bg.rect(x0, y0 + 3, x0 + T - 1, y0 + 3, TIMBER[1])
            self.bg.rect(x0, y0 + 4, x0 + T - 1, y0 + 8, TIMBER[4])
            self.bg.rect(x0, y0 + 9, x0 + T - 1, y0 + 15, DROP1)
        else:
            self.bg.rect(x0, y0 + 3, x0 + T - 1, y0 + 8, DROP1)
            self.bg.rect(x0, y0 + 9, x0 + T - 1, y0 + 15, DROP2)

    def rail_cell(self, tx, ty, newel):
        """UPPER-canvas balustrade Basil walks behind."""
        x0, y0 = tx * T, ty * T
        ov = self.ov
        if newel:
            ov.rect(x0 + 3, y0, x0 + 12, y0 + 1, TIMBER[1])
            ov.rect(x0 + 3, y0 + 2, x0 + 12, y0 + 2, TIMBER[2])
            ov.rect(x0 + 4, y0 + 3, x0 + 11, y0 + 11, TIMBER[2])
            ov.rect(x0 + 10, y0 + 3, x0 + 11, y0 + 11, TIMBER[4])
            ov.rect(x0 + 4, y0 + 3, x0 + 4, y0 + 11, TIMBER[1])
            ov.rect(x0 + 3, y0 + 12, x0 + 12, y0 + 13, TIMBER[4])
            return
        ov.rect(x0, y0 + 3, x0 + T - 1, y0 + 3, TIMBER[1])
        ov.rect(x0, y0 + 4, x0 + T - 1, y0 + 4, TIMBER[2])
        ov.rect(x0, y0 + 5, x0 + T - 1, y0 + 5, TIMBER[4])
        for bx in (3, 11):
            ov.rect(x0 + bx, y0 + 6, x0 + bx + 1, y0 + 13, TIMBER[3])
            ov.rect(x0 + bx + 1, y0 + 6, x0 + bx + 1, y0 + 13, TIMBER[4])

    # -- compose ------------------------------------------------------------------------
    def paint_terrain(self, wall_rules=None, special=None):
        """Paint every cell: void stays canvas fill; floor chars get fabric with
        whole-tile light dispatch; '#' goes through wall/side/south (or
        `wall_rules(tx,ty) -> bool handled` first); feature chars get planks or
        fabric underlay by row; `special` maps a char to a cell painter."""
        m = self.m
        for ty in range(m.rows_n):
            for tx in range(m.cols):
                ch = m.at(tx, ty)
                if ch == "V":
                    continue
                if special and ch in special:
                    special[ch](tx, ty)
                elif ch in self.floor_chars:
                    self.floor_cell(tx, ty)
                elif ch == "#":
                    if wall_rules and wall_rules(tx, ty):
                        continue
                    if ty >= self.FLOOR_ROW:
                        self.side_cell(tx, ty)
                    else:
                        self.wall_cell(tx, ty)
                else:                                    # feature underlay by row
                    if ty < self.FLOOR_ROW:
                        self.wall_cell(tx, ty)
                    else:
                        self.floor_cell(tx, ty, "plain")

    def bake_shadow(self, chars, shadow_h):
        """Contact-shadow band of shaded fabric across a footprint's bottom
        rows (overrides TileScene's darken pass: the interiors repaint their
        own floor fabric two steps darker, so the shadow stays on-weave) —
        also used alone under furniture that lives as a y-sorted scene
        ENTITY rather than baked tiles (desk, boiler: the static upper-tile
        walk-behind trick fails when a 2-tile-tall body stands directly
        south — its head clips behind the furniture top; y-sort is
        unconditionally correct)."""
        X, Y, XW, YH = self.px(self.bbox(chars))
        for y in range(Y + YH - shadow_h, Y + YH):
            for x in range(X + 1, X + XW - 1):
                self.bg.put(x, y, self.floor_px(x, y, self.FLOORR, 2))
