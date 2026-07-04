#!/usr/bin/env python3
"""Basil's ground floor as an authored tileset — kitchen + steampunk lab.

Same disciplines as assets/_gen_tileset_house.py (the loft reference):

  * Repeating fabric (slate flagstone floor, brown plank walls, void) painted
    by pure 16-periodic pixel functions, so plain cells are byte-identical and
    the slicer collapses them to single atlas tiles.
  * Light quantized per tile: the hearth throws whole lit-flag cells + an
    ordered-dither fringe; the open front door spills a dither fringe. No
    per-pixel gradients anywhere.
  * Furniture is a footprint-bounded multi-tile OBJECT (never a pixel outside
    its map bbox; contact shadows baked into its own bottom rows): kitchen
    west (stone hearth with a live fire — the room's one hot light source —
    counter, brass-latched icebox), STEAMPUNK LAB east (flask shelf, riveted
    copper boiler with gauge + pipe, workbench with a half-built gizmo).
  * The loft staircase descends through a top-center alcove jutting above the
    cornice; the front-door lintel rides the UPPER canvas so Basil passes
    under it stepping out.

Reads the room from assets/maps/downstairs.txt and emits:

    assets/tilesets/downstairs_tiles.png / .tres / downstairs_layout.txt
    assets/tilesets/downstairs_glow.png   (additive hearth glow, drawn UNDER
                                           entities — over sprites it reads
                                           as transparency)

Re-run: python3 assets/_gen_tileset_downstairs.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, lerp, Img, ZONE_TILE
from _maps import MapData
from _palette import SCENES, ramp
from _tiles import slice_atlas, write_atlas, write_tileset_tres, write_layout

T = ZONE_TILE
OUTDIR = os.path.join(HERE, "tilesets")
os.makedirs(OUTDIR, exist_ok=True)

m = MapData(os.path.join(HERE, "maps", "downstairs.txt"))
W, H = m.cols * T, m.rows_n * T


def tbbox(chars):
    """Tile-coord bbox (tx0, ty0, tx1, ty1 inclusive) of `chars` cells."""
    cs = [(x, y) for y in range(m.rows_n) for x in range(m.cols)
          if m.at(x, y) in chars]
    assert cs, f"no {chars!r} cells in downstairs.txt"
    xs, ys = [c[0] for c in cs], [c[1] for c in cs]
    return (min(xs), min(ys), max(xs), max(ys))


HEARTH = tbbox("H")
COUNTER = tbbox("C")
ICEBOX = tbbox("I")
FLASKS = tbbox("F")
BOILER = tbbox("A")
BENCH = tbbox("B")
STAIR = tbbox("s")
DOOR = tbbox("-")

FLOOR_ROW = tbbox(".")[1]          # first floor row
SOUTH_ROW = tbbox("#")[3]          # the south wall band (holds the doorway)
WALL_TOP = tbbox("#")[1]           # cornice row of the back wall
WALL_BASE = FLOOR_ROW - 1
_nonvoid = [x for y in range(m.rows_n) for x in range(m.cols)
            if m.at(x, y) != "V"]
LCOL, RCOL = min(_nonvoid), max(_nonvoid)

# ---- palette (downstairs scene: brown timber / slate flags / hot hearth amber) ----
SC = SCENES["downstairs"]
ACCENT = SC["accent"]
WALLR = ramp(SC["mats"]["wall"], "violet", 6)
FLOORR = ramp(SC["mats"]["floor"], "violet", 6)
STONE = ramp(SC["mats"]["stone"], "violet", 6)
# lit flags: one step lighter, blended hard toward the hearth amber
FLOOR_LIT = [tuple(lerp(FLOORR[max(0, i - 1)][:3], (255, 186, 110), 0.62)) + (255,)
             for i in range(6)]
TIMBER = ramp((146, 94, 62), "violet", 6)
COPPER = ramp((198, 112, 72), "violet", 6)
BRASS = ramp((240, 188, 98), "violet", 4)
STEEL = ramp((170, 168, 206), "violet", 4)
IRON = ramp((104, 100, 124), "violet", 4)
BREAD = ramp((214, 156, 92), "violet", 4)
GLASS = (216, 226, 240, 255)
MINT = (132, 246, 152, 255)
VIOLETF = (188, 132, 232, 255)
PAPER = (240, 232, 226, 255)
PAPERD = (206, 196, 204, 255)
RED = (226, 62, 92, 255)
SPEC = (255, 255, 250, 255)
FROST = (214, 240, 242, 255)
STEAM = (226, 224, 240, 255)
VOID = (10, 8, 24, 255)
FIREBOX = (14, 9, 22, 255)
EMBER = (216, 84, 52, 255)
FLAME = (255, 150, 70, 255)
FLAME_IN = (255, 208, 112, 255)
FLAME_CORE = (255, 244, 200, 255)
DAYL0 = (255, 228, 164, 255)               # daylight through the open door
DAYL1 = (255, 196, 124, 255)
GLOWC = (255, 186, 116)                    # additive hearth glow color
# stair treads, brightest at the floor and swallowed by the loft dark on top
TREADS = [((20, 16, 38, 255), (12, 10, 26, 255)),
          ((32, 24, 50, 255), (20, 15, 40, 255)),
          ((46, 34, 62, 255), (30, 22, 48, 255)),
          ((78, 54, 82, 255), (54, 38, 66, 255)),
          (TIMBER[2], TIMBER[4]),
          (TIMBER[2], TIMBER[4]),
          (TIMBER[1], TIMBER[3]),
          (TIMBER[0], TIMBER[2])]


class P(Img):
    def put(self, x, y, c):
        super().put(int(x), int(y), c)

    def rect(self, x0, y0, x1, y1, c):
        super().rect(int(x0), int(y0), int(x1), int(y1), c)


bg = P(W, H, VOID)        # lower layer: drawn under entities
ov = P(W, H)              # upper layer: drawn over entities (door lintel)

# =================================================================================
# repeating fabric — pure 16-periodic pixel functions, so cells dedupe to ONE tile
# =================================================================================


def flag_px(x, y, ramp6, shade=0):
    """Slate flagstones: 16x8 slabs in a running bond, low contrast."""
    v = y % 8
    u = (x + 8 * ((y // 8) % 2)) % 16
    if v == 0 or u == 0:
        i = 3                                  # mortar seam
    elif v == 1 and u % 5 == 1:
        i = 1                                  # sparse lit chisel mark
    else:
        i = 2
    return ramp6[min(5, i + shade)]


def plank_px(x, y):
    """Brown wall planks — same courses as the loft, one house one timber."""
    v = y % 8
    if v == 7:
        i = 4
    elif v == 0:
        i = 1
    elif v <= 4:
        i = 2
    else:
        i = 3
    if x % 16 == (5 if (y // 8) % 2 == 0 else 12) and 1 <= v <= 5:
        i = max(i, 3)
    return WALLR[i]


def paint_floor_cell(tx, ty, kind):
    x0, y0 = tx * T, ty * T
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            if kind == "lit":
                c = flag_px(x, y, FLOOR_LIT)
            elif kind == "fringe":
                lit = ((x // 2) + (y // 2)) % 2 == 0
                c = flag_px(x, y, FLOOR_LIT if lit else FLOORR)
            elif kind == "shadow":
                c = flag_px(x, y, FLOORR, shade=1)
            else:
                c = flag_px(x, y, FLOORR)
            bg.put(x, y, c)
    if kind == "plain" and h2(tx, ty, 7) % 13 == 0:     # whole-tile worn variant
        for px, py in ((4, 5), (5, 5), (10, 12), (13, 7)):
            bg.put(x0 + px, y0 + py, FLOORR[5])
        bg.rect(x0 + 6, y0 + 10, x0 + 9, y0 + 10, FLOORR[4])


def paint_wall_cell(tx, ty):
    x0, y0 = tx * T, ty * T
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            bg.put(x, y, plank_px(x, y))
    dressed = False
    if ty == WALL_TOP:
        bg.rect(x0, y0, x0 + T - 1, y0, WALLR[5])
        bg.rect(x0, y0 + 1, x0 + T - 1, y0 + 1, WALLR[4])
        bg.rect(x0, y0 + 2, x0 + T - 1, y0 + 2, WALLR[1])
        dressed = True
    if ty == WALL_BASE:
        bg.rect(x0, y0 + 10, x0 + T - 1, y0 + 10, TIMBER[1])
        bg.rect(x0, y0 + 11, x0 + T - 1, y0 + 14, TIMBER[3])
        bg.rect(x0, y0 + 15, x0 + T - 1, y0 + 15, TIMBER[5])
        dressed = True
    if tx == LCOL:
        bg.rect(x0, y0, x0, y0 + T - 1, WALLR[5])
        bg.rect(x0 + 1, y0, x0 + 1, y0 + T - 1, WALLR[4])
        dressed = True
    if tx == RCOL:
        bg.rect(x0 + T - 1, y0, x0 + T - 1, y0 + T - 1, WALLR[5])
        bg.rect(x0 + T - 2, y0, x0 + T - 2, y0 + T - 1, WALLR[4])
        dressed = True
    if not dressed and h2(tx, ty, 11) % 9 == 0:
        bg.rect(x0 + 9, y0 + 3, x0 + 11, y0 + 5, WALLR[3])
        bg.put(x0 + 10, y0 + 4, WALLR[5])
        bg.put(x0 + 9, y0 + 3, WALLR[4])
        bg.put(x0 + 11, y0 + 5, WALLR[4])


def paint_side_cell(tx, ty):
    """Side wall strip beside the floor: vertical boards framing the room."""
    x0, y0 = tx * T, ty * T
    left = tx == LCOL
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            u = (x - x0) if left else (T - 1 - (x - x0))
            if u <= 0:
                c = WALLR[5]
            elif u == 1:
                c = WALLR[4]
            elif u >= 15:
                c = WALLR[5]
            elif u == 14:
                c = WALLR[4]
            elif u == 2:
                c = WALLR[2]
            else:
                c = WALLR[3] if (x % 5) else WALLR[4]
            bg.put(x, y, c)


def paint_south_cell(tx, ty):
    """South wall band: plank face with a lit cap, sinking dark at its foot."""
    x0, y0 = tx * T, ty * T
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            bg.put(x, y, plank_px(x, y))
    bg.rect(x0, y0, x0 + T - 1, y0, WALLR[1])
    bg.rect(x0, y0 + 1, x0 + T - 1, y0 + 1, WALLR[2])
    bg.rect(x0, y0 + 13, x0 + T - 1, y0 + 13, WALLR[4])
    bg.rect(x0, y0 + 14, x0 + T - 1, y0 + 15, WALLR[5])
    if tx == LCOL:
        bg.rect(x0, y0, x0 + 1, y0 + T - 1, WALLR[5])
    if tx == RCOL:
        bg.rect(x0 + T - 2, y0, x0 + T - 1, y0 + T - 1, WALLR[5])


def paint_jamb_cell(tx, ty):
    """Stair-alcove side walls: planks (void-backed above the cornice) with a
    dark inner face toward the treads."""
    x0, y0 = tx * T, ty * T
    left_of_stairs = m.at(tx + 1, ty) == "s"
    if ty >= WALL_TOP:
        for y in range(y0, y0 + T):
            for x in range(x0, x0 + T):
                bg.put(x, y, plank_px(x, y))
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            u = (T - 1 - (x - x0)) if left_of_stairs else (x - x0)
            if u <= 1:
                bg.put(x, y, TIMBER[5])
            elif u == 2:
                bg.put(x, y, TIMBER[4])
            elif ty < WALL_TOP and u >= 3:
                pass                                   # void stays void up top
    if ty < WALL_TOP:                                  # alcove cap vs the void
        bg.rect(x0, y0, x0 + T - 1, y0, WALLR[5] if m.at(tx, ty - 1) != "#" else WALLR[4])


def paint_stair_cell(tx, ty):
    """Two 8px treads per cell, darkest at the loft hole, lit at the floor."""
    x0, y0 = tx * T, ty * T
    d = (ty - STAIR[1]) * 2
    for half in (0, 1):
        edge, body = TREADS[min(len(TREADS) - 1, d + half)]
        yy = y0 + half * 8
        bg.rect(x0, yy, x0 + T - 1, yy, edge)
        bg.rect(x0, yy + 1, x0 + T - 1, yy + 7, body)


# =================================================================================
# furniture objects — each painter stays strictly inside its map footprint
# =================================================================================


def paint_hearth():
    """Stone chimney breast with a live fire — the room's hot light source."""
    X, Y = HEARTH[0] * T, HEARTH[1] * T
    XW, YH = (HEARTH[2] - HEARTH[0] + 1) * T, (HEARTH[3] - HEARTH[1] + 1) * T
    x1, y1 = X + XW - 1, Y + YH - 1
    # masonry: 8px stone courses, running bond, flat
    for y in range(Y, y1 + 1):
        for x in range(X + 1, x1):
            v = (y - Y) % 8
            u = (x + 8 * (((y - Y) // 8) % 2)) % 16
            if v == 0 or u == 0:
                c = STONE[4]
            elif v == 1:
                c = STONE[1]
            else:
                c = STONE[2]
            bg.put(x, y, c)
    bg.rect(X + 1, Y, x1 - 1, Y, STONE[1])              # lit cap at the cornice
    bg.rect(X, Y, X, y1, STONE[5])                      # silhouette edges
    bg.rect(x1, Y, x1, y1, STONE[5])
    # brass mantel band
    bg.rect(X + 3, Y + 16, x1 - 3, Y + 17, BRASS[1])
    bg.rect(X + 3, Y + 18, x1 - 3, Y + 18, BRASS[3])
    # firebox arch + fire
    fx0, fx1 = X + 12, x1 - 12
    bg.rect(fx0, Y + 22, fx1, y1 - 4, FIREBOX)
    bg.rect(fx0 - 1, Y + 22, fx0 - 1, y1 - 4, STONE[5])
    bg.rect(fx1 + 1, Y + 22, fx1 + 1, y1 - 4, STONE[5])
    cx = (fx0 + fx1) // 2
    bg.rect(fx0 + 2, y1 - 7, fx1 - 2, y1 - 5, EMBER)    # ember bed
    for dx, hgt in ((-7, 8), (0, 13), (6, 9)):          # hard-banded tongues
        tip_y = y1 - 7 - hgt
        for i, yy in enumerate(range(tip_y, y1 - 6)):
            half = max(1, min(3, i // 2 + 1))
            bg.rect(cx + dx - half, yy, cx + dx + half, yy, FLAME)
    bg.rect(cx - 3, y1 - 13, cx + 3, y1 - 7, FLAME_IN)  # inner tongue
    bg.rect(cx - 1, y1 - 10, cx + 1, y1 - 6, FLAME_CORE)
    # hearthstone lip at the floor junction
    bg.rect(X + 1, y1 - 3, x1 - 1, y1 - 3, STONE[1])
    bg.rect(X + 1, y1 - 2, x1 - 1, y1, STONE[3])


def paint_counter():
    """Kitchen counter: worktop with bread + bowl + bottle, cupboards below."""
    X, Y = COUNTER[0] * T, COUNTER[1] * T
    XW, YH = (COUNTER[2] - COUNTER[0] + 1) * T, (COUNTER[3] - COUNTER[1] + 1) * T
    x1, y1 = X + XW - 1, Y + YH - 1
    # items stand on the worktop edge
    bg.rect(X + 4, Y + 5, X + 13, Y + 9, BREAD[1])      # bread loaf
    bg.rect(X + 4, Y + 5, X + 13, Y + 5, BREAD[0])
    for sx in (X + 6, X + 9, X + 12):
        bg.put(sx, Y + 6, BREAD[3])                     # scored slashes
    bg.rect(X + 19, Y + 6, X + 26, Y + 9, STEEL[2])     # mixing bowl
    bg.rect(X + 19, Y + 6, X + 26, Y + 6, STEEL[1])
    bg.rect(X + 21, Y + 5, X + 24, Y + 5, MINT)         # something green inside
    bg.rect(X + 34, Y + 2, X + 37, Y + 9, GLASS)        # bottle
    bg.rect(X + 35, Y + 4, X + 36, Y + 9, VIOLETF)
    bg.put(X + 35, Y + 1, PAPERD)
    # worktop
    bg.rect(X + 1, Y + 10, x1 - 1, Y + 12, TIMBER[1])
    bg.rect(X + 1, Y + 13, x1 - 1, Y + 14, TIMBER[2])
    bg.rect(X + 1, Y + 15, x1 - 1, Y + 15, TIMBER[4])
    # cupboard fronts
    bg.rect(X + 1, Y + 16, x1 - 1, y1 - 2, TIMBER[3])
    for dx0, dx1 in ((X + 4, X + 21), (X + 26, x1 - 4)):
        bg.rect(dx0, Y + 18, dx1, y1 - 5, TIMBER[2])
        bg.rect(dx0, Y + 18, dx1, Y + 18, TIMBER[1])
        bg.rect(dx0, y1 - 5, dx1, y1 - 5, TIMBER[4])
        kx = (dx0 + dx1) // 2
        bg.rect(kx, Y + 22, kx + 1, Y + 22, BRASS[1])
    bg.rect(X + 1, y1 - 1, x1 - 1, y1, TIMBER[5])       # foot shadow at the wall base


def paint_icebox():
    """Brass-latched ice chest with a frosted lid."""
    X, Y = ICEBOX[0] * T, ICEBOX[1] * T
    XW, YH = (ICEBOX[2] - ICEBOX[0] + 1) * T, (ICEBOX[3] - ICEBOX[1] + 1) * T
    x1, y1 = X + XW - 1, Y + YH - 1
    bg.rect(X + 2, Y + 4, x1 - 2, y1 - 5, TIMBER[2])    # body
    bg.rect(X + 2, Y + 4, x1 - 2, Y + 8, TIMBER[1])     # lid
    bg.rect(X + 3, Y + 5, x1 - 3, Y + 5, FROST)         # frosty glint
    bg.rect(X + 2, Y + 9, x1 - 2, Y + 9, TIMBER[4])     # lid seam
    for sx in (X + 4, x1 - 5):                          # brass corner straps
        bg.rect(sx, Y + 4, sx + 1, y1 - 5, BRASS[3])
    cx = (X + x1) // 2
    bg.rect(cx - 1, Y + 9, cx + 1, Y + 13, BRASS[1])    # latch
    bg.put(cx, Y + 12, BRASS[3])
    bg.rect(X + 2, y1 - 5, x1 - 2, y1 - 4, TIMBER[4])   # plinth
    bg.rect(X + 2, Y + 4, X + 2, y1 - 4, TIMBER[5])     # silhouette edges
    bg.rect(x1 - 2, Y + 4, x1 - 2, y1 - 4, TIMBER[5])
    for y in range(y1 - 3, y1 + 1):                     # baked contact shadow
        for x in range(X + 1, x1):
            bg.put(x, y, flag_px(x, y, FLOORR, shade=2))


def paint_flasks():
    """Lab shelf: glass vessels + copper coil on two timber shelves."""
    X, Y = FLASKS[0] * T, FLASKS[1] * T
    XW, YH = (FLASKS[2] - FLASKS[0] + 1) * T, (FLASKS[3] - FLASKS[1] + 1) * T
    x1, y1 = X + XW - 1, Y + YH - 1
    bg.rect(X + 1, Y + 1, x1 - 1, y1 - 1, TIMBER[4])    # case
    bg.rect(X + 2, Y + 2, x1 - 2, y1 - 2, TIMBER[5])    # dark interior
    bg.rect(X + 1, Y + 1, x1 - 1, Y + 2, TIMBER[2])     # crown
    bg.rect(X + 1, Y + 1, x1 - 1, Y + 1, TIMBER[1])
    sy = Y + 15                                         # middle shelf board
    bg.rect(X + 2, sy, x1 - 2, sy + 1, TIMBER[3])
    bg.rect(X + 2, sy, x1 - 2, sy, TIMBER[1])
    bg.rect(X + 1, y1 - 3, x1 - 1, y1 - 1, TIMBER[4])   # plinth
    bg.rect(X + 1, y1 - 3, x1 - 1, y1 - 3, TIMBER[2])
    # top row: three stoppered flasks
    for fx, liquid in ((X + 6, MINT), (X + 19, VIOLETF), (X + 32, ACCENT)):
        bg.rect(fx + 1, sy - 8, fx + 4, sy - 6, liquid)
        bg.rect(fx, sy - 5, fx + 5, sy - 1, liquid)
        bg.rect(fx, sy - 8, fx, sy - 1, GLASS)
        bg.rect(fx + 5, sy - 8, fx + 5, sy - 1, GLASS)
        bg.rect(fx + 2, sy - 10, fx + 3, sy - 9, PAPERD)
        bg.put(fx + 1, sy - 7, SPEC)
    # bottom row: mint jar + copper coil condenser
    bg.rect(X + 6, y1 - 12, X + 12, y1 - 4, GLASS)
    bg.rect(X + 7, y1 - 10, X + 11, y1 - 5, MINT)
    bg.put(X + 7, y1 - 11, SPEC)
    for i, cy in enumerate(range(y1 - 12, y1 - 4, 2)):  # coil arcs
        bg.rect(X + 22, cy, X + 34, cy, COPPER[1 + (i % 2)])
    bg.rect(X + 22, y1 - 12, X + 22, y1 - 4, COPPER[3])
    bg.rect(X + 34, y1 - 12, X + 34, y1 - 4, COPPER[3])


def paint_boiler():
    """Riveted copper boiler: dome, gauge, firebox slit, pipe to the cornice."""
    X, Y = BOILER[0] * T, BOILER[1] * T
    XW, YH = (BOILER[2] - BOILER[0] + 1) * T, (BOILER[3] - BOILER[1] + 1) * T
    x1, y1 = X + XW - 1, Y + YH - 1
    bx0, bx1 = X + 4, x1 - 10                           # tank body span
    # pipe up to the cornice, with elbow + brackets
    bg.rect(x1 - 7, Y, x1 - 4, Y + 14, COPPER[2])
    bg.rect(x1 - 7, Y, x1 - 7, Y + 14, COPPER[1])
    bg.rect(x1 - 4, Y, x1 - 4, Y + 14, COPPER[4])
    for by in (Y + 2, Y + 10):
        bg.rect(x1 - 8, by, x1 - 3, by, IRON[3])        # brackets
    bg.rect(x1 - 9, Y + 14, x1 - 4, Y + 17, COPPER[3])  # elbow into the tank
    bg.put(x1 - 6, Y + 1, STEAM)                        # wisps escaping the seam
    bg.put(x1 - 5, Y + 3, STEAM)
    # tank: rounded dome + banded barrel, lit hot from the west (hearth side)
    bg.rect(bx0 + 4, Y + 5, bx1 - 4, Y + 7, COPPER[0])  # dome cap, hot
    bg.rect(bx0 + 2, Y + 8, bx1 - 2, Y + 10, COPPER[1])
    bg.rect(bx0 + 1, Y + 11, bx1 - 1, Y + 12, COPPER[1])
    bg.rect(bx0, Y + 13, bx1, y1 - 8, COPPER[2])        # barrel
    bg.rect(bx0 + 1, Y + 13, bx0 + 6, y1 - 8, COPPER[1])   # wide lit band
    bg.rect(bx0 + 2, Y + 14, bx0 + 3, y1 - 9, COPPER[0])   # hot specular column
    bg.rect(bx1 - 5, Y + 13, bx1 - 1, y1 - 8, COPPER[3])   # shaded east band
    bg.rect(bx0, Y + 13, bx0, y1 - 8, COPPER[4])        # silhouette edges
    bg.rect(bx1, Y + 13, bx1, y1 - 8, COPPER[5])
    for ry in (Y + 19, Y + 31):                         # riveted seams
        bg.rect(bx0 + 1, ry, bx1 - 1, ry, COPPER[4])
        for rx in range(bx0 + 3, bx1 - 1, 4):
            bg.put(rx, ry, COPPER[5])
    gx, gy = bx0 + 11, Y + 25                           # brass gauge + red needle
    bg.rect(gx - 4, gy - 4, gx + 4, gy + 4, BRASS[3])
    bg.rect(gx - 3, gy - 3, gx + 3, gy + 3, BRASS[1])
    bg.rect(gx - 2, gy - 2, gx + 2, gy + 2, GLASS)
    bg.put(gx, gy, RED)
    bg.put(gx + 1, gy - 1, RED)
    # firebox slit at the base + stout legs
    bg.rect(bx0 + 2, y1 - 7, bx1 - 2, y1 - 4, IRON[3])
    bg.rect(bx0 + 4, y1 - 6, bx1 - 4, y1 - 6, ACCENT)   # glowing grate line
    for px in (bx0 + 2, bx1 - 4):
        bg.rect(px, y1 - 3, px + 2, y1, IRON[2])
    bg.rect(bx0, y1 - 1, bx1, y1, TIMBER[5])            # base shadow line


def paint_bench():
    """Lab workbench: open table with a half-built gizmo, gear and wrench."""
    X, Y = BENCH[0] * T, BENCH[1] * T
    XW, YH = (BENCH[2] - BENCH[0] + 1) * T, (BENCH[3] - BENCH[1] + 1) * T
    x1, y1 = X + XW - 1, Y + YH - 1
    # tools stand on the tabletop edge at Y+10
    bg.rect(X + 5, Y + 4, X + 12, Y + 9, BRASS[2])      # gizmo: brass box
    bg.rect(X + 5, Y + 4, X + 12, Y + 4, BRASS[1])
    bg.put(X + 7, Y + 6, RED)                           # button
    bg.put(X + 10, Y + 6, MINT)                         # indicator lamp
    bg.rect(X + 8, Y + 1, X + 8, Y + 3, STEEL[2])       # antenna
    bg.put(X + 8, Y + 0, SPEC)
    gx, gy = X + 24, Y + 7                              # brass gear
    bg.rect(gx - 3, gy - 3, gx + 3, gy + 3, BRASS[2])
    for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4)):
        bg.put(gx + dx, gy + dy, BRASS[3])              # teeth
    bg.put(gx, gy, TIMBER[5])                           # hub
    bg.rect(X + 36, Y + 8, X + 47, Y + 9, STEEL[2])     # wrench shaft
    bg.rect(X + 46, Y + 5, X + 49, Y + 9, STEEL[1])     # jaw
    bg.put(X + 48, Y + 7, TIMBER[5])
    # tabletop
    bg.rect(X + 2, Y + 10, x1 - 2, Y + 12, TIMBER[1])
    bg.rect(X + 2, Y + 13, x1 - 2, Y + 14, TIMBER[2])
    bg.rect(X + 2, Y + 15, x1 - 2, Y + 15, TIMBER[4])
    # open under-table: shadowed flags + stout legs
    for y in range(Y + 16, Y + 28):
        for x in range(X + 3, x1 - 2):
            bg.put(x, y, flag_px(x, y, FLOORR, shade=1))
    for px in (X + 4, x1 - 7):
        bg.rect(px, Y + 16, px + 2, Y + 27, TIMBER[3])
        bg.rect(px + 2, Y + 16, px + 2, Y + 27, TIMBER[4])
    for y in range(Y + 28, Y + YH):                     # baked contact shadow
        for x in range(X + 2, x1 - 1):
            bg.put(x, y, flag_px(x, y, FLOORR, shade=2))


def paint_door():
    """The front door: an OPEN doorway spilling daylight, lintel on the upper
    canvas (Basil passes under it), stone stoop sinking into the void."""
    X, Y = DOOR[0] * T, DOOR[1] * T
    XW = (DOOR[2] - DOOR[0] + 1) * T
    x1 = X + XW - 1
    dy1 = Y + T - 1                                     # doorway row bottom
    # daylight opening between timber posts
    bg.rect(X + 3, Y, x1 - 3, Y + 9, DAYL0)
    bg.rect(X + 3, Y + 10, x1 - 3, dy1 - 2, DAYL1)
    bg.rect(X + 3, dy1 - 1, x1 - 3, dy1, TIMBER[5])     # threshold
    for side in (0, 1):                                 # posts
        px = X if side == 0 else x1 - 2
        bg.rect(px, Y, px + 2, dy1, TIMBER[3])
        bg.rect(px + (2 if side == 0 else 0), Y, px + (2 if side == 0 else 0), dy1, TIMBER[1])
        bg.rect(px + (0 if side == 0 else 2), Y, px + (0 if side == 0 else 2), dy1, TIMBER[5])
    # lintel rides the UPPER layer — Basil ducks under it stepping out
    ov.rect(X, Y, x1, Y + 1, TIMBER[2])
    ov.rect(X, Y, x1, Y, TIMBER[1])
    ov.rect(X, Y + 2, x1, Y + 3, TIMBER[4])
    # stoop: two stone steps narrowing into the dark
    sy = Y + T
    bg.rect(X + 2, sy, x1 - 2, sy, STONE[1])
    bg.rect(X + 2, sy + 1, x1 - 2, sy + 5, STONE[3])
    bg.rect(X + 4, sy + 6, x1 - 4, sy + 6, STONE[2])
    bg.rect(X + 4, sy + 7, x1 - 4, sy + 10, STONE[4])
    bg.rect(X + 6, sy + 11, x1 - 6, sy + 13, (24, 18, 44, 255))


# =================================================================================
# compose: terrain fabric per cell, then the furniture objects over it
# =================================================================================

# hearth light pool + doorway daylight fringe, whole tiles only
lit_cells = {(c, FLOOR_ROW) for c in range(HEARTH[0], HEARTH[2] + 1)}
fringe_cells = {(HEARTH[0] - 1, FLOOR_ROW), (HEARTH[2] + 1, FLOOR_ROW)}
fringe_cells |= {(c, FLOOR_ROW + 1) for c in range(HEARTH[0], HEARTH[2] + 1)}
fringe_cells |= {(c, SOUTH_ROW - 1) for c in range(DOOR[0], DOOR[2] + 1)}

for ty in range(m.rows_n):
    for tx in range(m.cols):
        ch = m.at(tx, ty)
        if ch == "V" or ch == "-":                      # door object paints '-'
            continue
        if ch in ".IB":
            if (tx, ty) in lit_cells:
                kind = "lit"
            elif (tx, ty) in fringe_cells:
                kind = "fringe"
            elif ty in (FLOOR_ROW, SOUTH_ROW - 1):
                kind = "shadow"
            else:
                kind = "plain"
            paint_floor_cell(tx, ty, kind)
        elif ch == "s":
            paint_stair_cell(tx, ty)
        elif ch == "#":
            if m.at(tx - 1, ty) == "s" or m.at(tx + 1, ty) == "s":
                paint_jamb_cell(tx, ty)
            elif ty == SOUTH_ROW:
                paint_south_cell(tx, ty)
            elif ty >= FLOOR_ROW:
                paint_side_cell(tx, ty)
            else:
                paint_wall_cell(tx, ty)
        elif ch in "HCFA":                              # planks under wall furniture
            paint_wall_cell(tx, ty)

paint_hearth()
paint_counter()
paint_icebox()
paint_flasks()
paint_boiler()
paint_bench()
paint_door()

# =================================================================================
# slice, dedupe, write the tileset (both layers share one atlas)
# =================================================================================
tiles, seen = [], {}
_, lower = slice_atlas(bg, tiles, seen)
_, upper = slice_atlas(ov, tiles, seen, skip_empty=True)
write_atlas(os.path.join(OUTDIR, "downstairs_tiles.png"), tiles)
write_tileset_tres(os.path.join(OUTDIR, "downstairs_tiles.tres"),
                   "res://assets/tilesets/downstairs_tiles.png", len(tiles))
write_layout(os.path.join(OUTDIR, "downstairs_layout.txt"),
             {"lower": lower, "upper": upper},
             "from assets/maps/downstairs.txt by _gen_tileset_downstairs.py")
n_upper = sum(1 for row in upper for i in row if i is not None)
print(f"{len(tiles)} unique tiles from {m.cols * m.rows_n} cells "
      f"({n_upper} upper-layer cells)")


# =================================================================================
# scene dressing: the hearth's additive glow (runtime overlay, not tiles)
# =================================================================================
def write_glow():
    """downstairs_glow.png — hard-banded amber glow over the firebox spilling
    onto the lit flags, plus a soft shaft at the open front door. Drawn UNDER
    entities (additive light over a sprite reads as transparency)."""
    img = Img(W, H)
    hx0, hy0 = HEARTH[0] * T, HEARTH[1] * T
    hx1 = HEARTH[2] * T + T - 1
    fy = FLOOR_ROW * T
    img.rect(hx0 + 10, hy0 + 20, hx1 - 10, hy0 + 47, GLOWC + (50,))
    for y in range(hy0 + 44, fy + 2 * T):
        if y < fy:
            x0, x1, a = hx0 + 8, hx1 - 8, 56
        elif y < fy + T:
            x0, x1, a = hx0 - 6, hx1 + 6, 40
        else:
            x0, x1, a = hx0 + 2, hx1 - 2, 24
        img.rect(max(0, x0), y, min(W - 1, x1), y, GLOWC + (a,))
    dx0, dy0 = DOOR[0] * T, DOOR[1] * T                 # daylight at the doorway
    img.rect(dx0 + 3, dy0 - 12, dx0 + 28, dy0 + 12, (255, 226, 170, 26))
    img.save(os.path.join(OUTDIR, "downstairs_glow.png"))


write_glow()

if "--preview" in sys.argv:
    out = sys.argv[sys.argv.index("--preview") + 1]
    for y in range(H):
        for x in range(W):
            p = ov.get(x, y)
            if p[3]:
                bg.put(x, y, p)
    bg.save(out if os.path.isabs(out) else os.path.join(HERE, out))
