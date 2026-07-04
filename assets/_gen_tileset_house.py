#!/usr/bin/env python3
"""Basil's loft as a REAL TILESET — authored chips, not a sliced painting.

The Chrono Trigger discipline, enforced by construction instead of hoped for:

  * The repeating fabric (teal weave floor, brown plank walls, void) is painted
    by pure functions of 16-periodic pixel coordinates, so every plain floor
    cell is BYTE-IDENTICAL and the slicer collapses them all to one atlas tile
    — the tile rhythm CT rooms live on. Deliberate variety comes from whole-
    tile variants (a worn floor cell, a knotted plank cell) hash-placed per
    cell, each costing exactly one extra atlas tile.
  * Light is quantized per tile: a floor cell is a lit-weave cell, an ordered-
    dither fringe cell, a shadow-band cell or a plain cell. No per-pixel
    gradients anywhere — they make every tile unique and kill the rhythm.
  * Furniture is a multi-tile OBJECT: each painter draws once inside its map
    footprint (never a pixel outside it), producing a crisp block of unique
    tiles exactly like an SNES furniture metatile. Contact shadows are baked
    into the object's own bottom rows.
  * The stairwell railing goes on the UPPER canvas (drawn over entities), so
    Basil passes behind the balustrade onto steps that descend into the dark.

Palette: warm brown plank walls over a deep teal weave floor, ONE hot light
source (the peach dawn window) — minimal, surreal, violet in the darks.

Reads the room from assets/maps/house.txt (feature chars place the furniture —
move the bed in the map and it moves here), composes the 384x224 room on a
LOWER and UPPER canvas, then slices/dedupes both into:

    assets/tilesets/house_tiles.png    packed atlas (layers share it)
    assets/tilesets/house_tiles.tres   TileSet (visuals only)
    assets/tilesets/house_layout.txt   per-cell atlas coords for tiled_map.gd

Re-run: python3 assets/_gen_tileset_house.py [--preview out.png]
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

m = MapData(os.path.join(HERE, "maps", "house.txt"))
W, H = m.cols * T, m.rows_n * T


def tbbox(chars):
    """Tile-coord bbox (tx0, ty0, tx1, ty1 inclusive) of `chars` cells."""
    cs = [(x, y) for y in range(m.rows_n) for x in range(m.cols)
          if m.at(x, y) in chars]
    assert cs, f"no {chars!r} cells in house.txt"
    xs, ys = [c[0] for c in cs], [c[1] for c in cs]
    return (min(xs), min(ys), max(xs), max(ys))


WIN = tbbox("W")           # dormer window bay (juts above the cornice)
SHELF = tbbox("S")
CORK = tbbox("C")
BED = tbbox("b")
DESK = tbbox("d")
CHAIR = tbbox("h")
BASK = tbbox("w")

FLOOR_ROW = tbbox(".")[1]          # first (north) floor row — wall shadow band
RAIL_ROW = tbbox("R")[1]           # railed south boundary row
WALL_TOP = tbbox("#")[1]           # cornice row of the wall face
WALL_BASE = FLOOR_ROW - 1          # baseboard row (wall meets floor)
_nonvoid = [x for y in range(m.rows_n) for x in range(m.cols)
            if m.at(x, y) != "V"]
LCOL, RCOL = min(_nonvoid), max(_nonvoid)   # side wall columns

# ---- palette (bedroom scene: brown planks / teal weave / hot peach dawn) ----------
SC = SCENES["bedroom"]
ACCENT = SC["accent"]
WALLR = ramp(SC["mats"]["wall"], "violet", 6)     # warm brown planks
FLOORR = ramp(SC["mats"]["floor"], "violet", 6)   # deep teal weave
LINENR = ramp(SC["mats"]["linen"], "violet", 4)
# lit weave: one step lighter, blended hard toward the dawn — warm gold, not gray
FLOOR_LIT = [tuple(lerp(FLOORR[max(0, i - 1)][:3], (255, 218, 148), 0.75)) + (255,)
             for i in range(6)]
TIMBER = ramp((146, 94, 62), "violet", 6)         # furniture wood, redder/darker
QUILT = ramp((226, 76, 132), "violet", 4)         # hot magenta quilt
CURT = ramp((162, 96, 122), "violet", 4)   # dusty rose — must not outshout the quilt
BRASS = ramp((240, 188, 98), "violet", 4)
STEEL = ramp((170, 168, 206), "violet", 4)
CORKF = ramp((182, 132, 92), "violet", 4)
SPINES = [(214, 84, 118, 255), (96, 120, 208, 255), (98, 172, 138, 255),
          (238, 172, 96, 255), (166, 100, 202, 255), (82, 164, 172, 255)]
DAWN = [(255, 232, 160, 255), (255, 186, 122, 255), (244, 126, 128, 255),
        (198, 84, 152, 255), (122, 62, 148, 255)]  # quantized sky bands, top->down
SUN = (255, 240, 196, 255)
SKYLINE = (58, 38, 92, 255)                # rooftops silhouetted in the glass
GLASS = (216, 226, 240, 255)
MINT = (132, 246, 152, 255)
VIOLETF = (188, 132, 232, 255)
PAPER = (240, 232, 226, 255)
PAPERD = (206, 196, 204, 255)
RED = (226, 62, 92, 255)
SPEC = (255, 255, 250, 255)
WATER = (150, 210, 214, 255)
VOID = (10, 8, 24, 255)
DROP1 = (22, 15, 42, 255)                  # first darkness band past the loft edge
DROP2 = (13, 10, 30, 255)                  # deeper darkness (still above void)
STEP2 = (54, 38, 66, 255)                  # second stair step, sinking into dark
STEP2E = (78, 54, 82, 255)                 # its lit front edge
STEP3 = (30, 22, 48, 255)                  # third step, nearly swallowed
STEP3E = (46, 34, 62, 255)


class P(Img):
    def put(self, x, y, c):
        super().put(int(x), int(y), c)

    def rect(self, x0, y0, x1, y1, c):
        super().rect(int(x0), int(y0), int(x1), int(y1), c)

    def line(self, x0, y0, x1, y1, c):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(steps) + 1):
            t = i / steps
            self.put(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), c)


bg = P(W, H, VOID)        # lower layer: drawn under entities
ov = P(W, H)              # upper layer: drawn over entities (railing)

# =================================================================================
# repeating fabric — pure 16-periodic pixel functions, so cells dedupe to ONE tile
# =================================================================================


def weave_px(x, y, ramp6, shade=0):
    """Teal basket weave: 8px slats alternating direction, 16-periodic.
    Deliberately LOW contrast — the floor is the quiet field CT rooms rest on."""
    horiz = ((x % 16) // 8 + (y % 16) // 8) % 2 == 0
    w = y % 8 if horiz else x % 8              # across the slat
    t = x % 8 if horiz else y % 8              # along the slat
    if w == 0:
        i = 3                                  # single soft seam line
    elif w == 1 and t % 4 == 1:
        i = 1                                  # sparse lit stitch, not a hot line
    else:
        i = 2
    if t == 7 and 2 <= w <= 6:
        i = 3                                  # under-weave tuck
    return ramp6[min(5, i + shade)]


def plank_px(x, y):
    """Brown wall planks: 8px courses, staggered butt seams, 16-periodic."""
    v = y % 8
    if v == 7:
        i = 4                                  # course seam shadow
    elif v == 0:
        i = 1                                  # lit top edge
    elif v <= 4:
        i = 2
    else:
        i = 3
    if x % 16 == (5 if (y // 8) % 2 == 0 else 12) and 1 <= v <= 5:
        i = max(i, 3)                          # staggered butt seam, kept soft
    return WALLR[i]


def paint_floor_cell(tx, ty, kind):
    x0, y0 = tx * T, ty * T
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            if kind == "lit":
                c = weave_px(x, y, FLOOR_LIT)
            elif kind == "fringe":                       # ordered 2x2 dither edge
                lit = ((x // 2) + (y // 2)) % 2 == 0
                c = weave_px(x, y, FLOOR_LIT if lit else FLOORR)
            elif kind == "shadow":
                c = weave_px(x, y, FLOORR, shade=1)
            else:
                c = weave_px(x, y, FLOORR)
            bg.put(x, y, c)
    # whole-tile worn variant, hash-placed: one extra atlas tile total
    if kind == "plain" and h2(tx, ty, 7) % 13 == 0:
        for px, py in ((3, 4), (4, 4), (9, 11), (12, 6)):
            bg.put(x0 + px, y0 + py, FLOORR[5])
        bg.rect(x0 + 5, y0 + 9, x0 + 8, y0 + 9, FLOORR[4])


def paint_wall_cell(tx, ty):
    x0, y0 = tx * T, ty * T
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            bg.put(x, y, plank_px(x, y))
    dressed = False
    if ty == WALL_TOP:                                   # cornice beam vs the void
        bg.rect(x0, y0, x0 + T - 1, y0, WALLR[5])
        bg.rect(x0, y0 + 1, x0 + T - 1, y0 + 1, WALLR[4])
        bg.rect(x0, y0 + 2, x0 + T - 1, y0 + 2, WALLR[1])
        dressed = True
    if ty == WALL_BASE:                                  # baseboard + floor junction
        bg.rect(x0, y0 + 10, x0 + T - 1, y0 + 10, TIMBER[1])
        bg.rect(x0, y0 + 11, x0 + T - 1, y0 + 14, TIMBER[3])
        bg.rect(x0, y0 + 15, x0 + T - 1, y0 + 15, TIMBER[5])
        dressed = True
    if tx == LCOL:                                       # dark outer edge vs void
        bg.rect(x0, y0, x0, y0 + T - 1, WALLR[5])
        bg.rect(x0 + 1, y0, x0 + 1, y0 + T - 1, WALLR[4])
        dressed = True
    if tx == RCOL:
        bg.rect(x0 + T - 1, y0, x0 + T - 1, y0 + T - 1, WALLR[5])
        bg.rect(x0 + T - 2, y0, x0 + T - 2, y0 + T - 1, WALLR[4])
        dressed = True
    # whole-tile knot variant on plain field cells only
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
                c = WALLR[5]                             # outer edge vs void
            elif u == 1:
                c = WALLR[4]
            elif u >= 15:
                c = WALLR[5]                             # junction line vs floor
            elif u == 14:
                c = WALLR[4]
            elif u == 2:
                c = WALLR[2]                             # lit inner edge
            else:
                c = WALLR[3] if (x % 5) else WALLR[4]    # shadowed vertical grain
            bg.put(x, y, c)


def paint_drop_cell(tx, ty, stair):
    """Rail row LOWER art: the loft's edge board, then darkness (or the first
    step, on the stair-gap cells) falling toward the unbuilt downstairs."""
    x0, y0 = tx * T, ty * T
    bg.rect(x0, y0, x0 + T - 1, y0, TIMBER[1])           # lit lip of the edge board
    bg.rect(x0, y0 + 1, x0 + T - 1, y0 + 2, TIMBER[3])
    if stair:
        bg.rect(x0, y0 + 3, x0 + T - 1, y0 + 3, TIMBER[1])   # first step, still lit
        bg.rect(x0, y0 + 4, x0 + T - 1, y0 + 8, TIMBER[4])
        bg.rect(x0, y0 + 9, x0 + T - 1, y0 + 15, DROP1)
    else:
        bg.rect(x0, y0 + 3, x0 + T - 1, y0 + 8, DROP1)
        bg.rect(x0, y0 + 9, x0 + T - 1, y0 + 15, DROP2)


def paint_step_cell(tx, ty):
    """Stair-descent cells: one visible step per row, each darker — the CT
    staircase sinking out of the room silhouette."""
    x0, y0 = tx * T, ty * T
    edge, body = (STEP2E, STEP2) if ty - RAIL_ROW <= 1 else (STEP3E, STEP3)
    bg.rect(x0, y0, x0 + T - 1, y0, edge)
    bg.rect(x0, y0 + 1, x0 + T - 1, y0 + 7, body)
    bg.rect(x0, y0 + 8, x0 + T - 1, y0 + 8, edge)     # next tread's front edge
    bg.rect(x0, y0 + 9, x0 + T - 1, y0 + 15, tuple(
        round(v * 0.72) for v in body[:3]) + (255,))


def paint_stub_cell(tx, ty):
    """Stairwell side walls below the rail row: a dark timber jamb."""
    x0, y0 = tx * T, ty * T
    left = m.at(tx + 1, ty) == "-"                       # stairs to our right?
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            u = (x - x0) if not left else (T - 1 - (x - x0))
            if u <= 2:
                c = TIMBER[5]                            # jamb face toward stairs
            elif u == 3:
                c = TIMBER[4]
            else:
                c = VOID
            bg.put(x, y, c)


def paint_rail_cell(tx, ty, newel):
    """Rail row UPPER art: balustrade Basil walks behind."""
    x0, y0 = tx * T, ty * T
    if newel:                                            # chunky post at the gap
        ov.rect(x0 + 3, y0, x0 + 12, y0 + 1, TIMBER[1])  # cap
        ov.rect(x0 + 3, y0 + 2, x0 + 12, y0 + 2, TIMBER[2])
        ov.rect(x0 + 4, y0 + 3, x0 + 11, y0 + 11, TIMBER[2])
        ov.rect(x0 + 10, y0 + 3, x0 + 11, y0 + 11, TIMBER[4])
        ov.rect(x0 + 4, y0 + 3, x0 + 4, y0 + 11, TIMBER[1])
        ov.rect(x0 + 3, y0 + 12, x0 + 12, y0 + 13, TIMBER[4])  # base flare
        return
    ov.rect(x0, y0 + 3, x0 + T - 1, y0 + 3, TIMBER[1])   # handrail
    ov.rect(x0, y0 + 4, x0 + T - 1, y0 + 4, TIMBER[2])
    ov.rect(x0, y0 + 5, x0 + T - 1, y0 + 5, TIMBER[4])
    for bx in (3, 11):                                   # balusters, open between
        ov.rect(x0 + bx, y0 + 6, x0 + bx + 1, y0 + 13, TIMBER[3])
        ov.rect(x0 + bx + 1, y0 + 6, x0 + bx + 1, y0 + 13, TIMBER[4])


# =================================================================================
# furniture objects — each painter stays strictly inside its map footprint
# =================================================================================


def paint_window():
    """Dormer bay: gable jutting into the void, quantized dawn glass (the hot
    accent), curtains, sill with flasks. All its tiles are one-offs — CT keeps
    focal art unique and spends its reuse budget on the fabric."""
    X, Y = WIN[0] * T, WIN[1] * T                       # (160, 0)
    XW = (WIN[2] - WIN[0] + 1) * T                      # 64
    cx = X + XW // 2                                    # bay center seam
    gy1 = Y + T - 1                                     # gable row bottom
    # gable: clean dark roof wedge against the void, brass vent eye
    for y in range(Y + 4, gy1 + 1):
        half = 4 + (y - (Y + 4)) * 2                    # widens 2px per row
        bg.rect(cx - half, y, cx + half - 1, y, WALLR[3])
        bg.put(cx - half, y, WALLR[5])                  # raking edges
        bg.put(cx - half + 1, y, WALLR[4])
        bg.put(cx + half - 1, y, WALLR[5])
        bg.put(cx + half - 2, y, WALLR[4])
    bg.rect(cx - 2, Y + 4, cx + 1, Y + 5, WALLR[5])     # peak cap
    bg.rect(cx - 3, Y + 9, cx + 2, Y + 13, BRASS[3])    # round brass vent
    bg.rect(cx - 2, Y + 10, cx + 1, Y + 12, BRASS[1])
    bg.put(cx - 1, Y + 10, SUN)
    # window frame filling most of the bay
    fx0, fy0, fx1, fy1 = X + 3, Y + T, X + XW - 4, Y + 52
    bg.rect(fx0, fy0, fx1, fy1, TIMBER[2])
    bg.rect(fx0, fy0, fx1, fy0, TIMBER[1])
    bg.rect(fx0, fy0, fx0, fy1, TIMBER[1])
    bg.rect(fx1, fy0, fx1, fy1, TIMBER[4])
    bg.rect(fx0, fy1, fx1, fy1, TIMBER[4])
    # glass: the dawn blazing in hard bands — gold dominates, dark stays a sliver
    gx0, gy0, gx1, gy2 = X + 9, Y + 19, X + XW - 10, Y + 49
    bands = ((0, 12, 0), (13, 20, 1), (21, 25, 2), (26, 28, 3), (29, 30, 4))
    for b0, b1, di in bands:
        bg.rect(gx0, gy0 + b0, gx1, min(gy2, gy0 + b1), DAWN[di])
    for sx, sw, sh in ((3, 6, 5), (12, 4, 3), (28, 8, 6), (39, 5, 4)):
        bg.rect(gx0 + sx, gy2 - sh, gx0 + sx + sw, gy2, SKYLINE)   # rooftops
    scx, scy = cx - 8, gy0 + 7                          # sun: hard flat disc
    for dy in range(-5, 6):
        half = max(1, 6 - abs(dy))
        bg.rect(scx - half, scy + dy, scx + half, scy + dy, SUN)
    bg.rect(scx - 2, scy - 2, scx + 2, scy, (255, 252, 232, 255))  # hot core
    for bx, by in ((gx1 - 10, gy0 + 5), (gx1 - 15, gy0 + 9)):      # birds
        bg.put(bx, by, SKYLINE)
        bg.put(bx - 1, by - 1, SKYLINE)
        bg.put(bx + 1, by - 1, SKYLINE)
    bg.rect(cx - 1, gy0, cx, gy2, TIMBER[4])            # mullion cross
    my = gy0 + 17
    bg.rect(gx0, my, gx1, my, TIMBER[4])
    # slim tied-back curtains hugging the frame
    for side in (0, 1):
        for y in range(fy0 + 1, fy1 - 1):
            pinch = 2 if Y + 34 <= y <= Y + 40 else 0   # tieback waist
            w = 6 - pinch
            xa = (fx0 + 1 + pinch) if side == 0 else (fx1 - w - pinch)
            for x in range(xa, xa + w):
                u = (x - xa) if side == 1 else (xa + w - 1 - x)
                c = CURT[0] if u == 0 else (CURT[2] if u % 3 == 2 else CURT[1])
                bg.put(x, y, c)
        bx0 = fx0 + 1 if side == 0 else fx1 - 5
        bg.rect(bx0, Y + 36, bx0 + 4, Y + 37, BRASS[2])  # brass tieback
    # sill board + flasks (the scientist's windowsill)
    bg.rect(X + 1, Y + 52, X + XW - 2, Y + 53, TIMBER[1])
    bg.rect(X + 1, Y + 54, X + XW - 2, Y + 57, TIMBER[3])
    bg.rect(X + 1, Y + 58, X + XW - 2, Y + 58, TIMBER[5])
    draw_flasks(bg, X, Y)


def draw_flasks(img, X, Y):
    """Sill flasks, shared with the curtain frames: the flasks stand INSIDE
    the room, so closed drapes must draw behind them."""
    for fx, liquid in ((X + 14, MINT), (X + 29, VIOLETF), (X + 44, MINT)):
        img.rect(fx + 1, Y + 44, fx + 4, Y + 46, liquid)         # bulb liquid
        img.rect(fx, Y + 47, fx + 5, Y + 51, liquid)
        img.rect(fx, Y + 44, fx, Y + 51, GLASS)                  # glass edges
        img.rect(fx + 5, Y + 44, fx + 5, Y + 51, GLASS)
        img.rect(fx + 2, Y + 42, fx + 3, Y + 43, PAPERD)         # cork stopper
        img.put(fx + 1, Y + 45, SPEC)


def paint_shelf():
    """Bookshelf: crown, packed spines, scroll + glow jar on the bottom."""
    X, Y = SHELF[0] * T, SHELF[1] * T
    XW, YH = (SHELF[2] - SHELF[0] + 1) * T, (SHELF[3] - SHELF[1] + 1) * T
    x0, y0, x1, y1 = X + 1, Y + 1, X + XW - 2, Y + YH - 2
    bg.rect(x0, y0, x1, y1, TIMBER[4])                  # case
    bg.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, TIMBER[5])  # dark interior
    bg.rect(x0, y0, x1, y0 + 1, TIMBER[2])              # crown
    bg.rect(x0, y0, x1, y0, TIMBER[1])
    bg.rect(x0, y1 - 3, x1, y1, TIMBER[4])              # plinth
    bg.rect(x0, y1 - 3, x1, y1 - 3, TIMBER[2])
    shelves = (y0 + 13, y0 + 26)                        # two shelf boards
    for sy in shelves:
        bg.rect(x0 + 1, sy, x1 - 1, sy + 1, TIMBER[3])
        bg.rect(x0 + 1, sy, x1 - 1, sy, TIMBER[1])
    # books: deterministic spines, a leaner, a couple of dark gaps
    openings = ((y0 + 2, y0 + 12), (shelves[0] + 2, shelves[0] + 12))
    for row, (oy0, oy1) in enumerate(openings):
        sx = x0 + 2
        slot = 0
        while sx + 3 <= x1 - 2:
            k = h2(slot, row, 3)
            if k % 7 == 0:
                sx += 3                                  # gap of dark
                slot += 1
                continue
            hgt = 7 + k % 4
            col = SPINES[k % 6]
            lean = 1 if k % 5 == 0 else 0
            for yy in range(oy1 - hgt, oy1 + 1):
                off = lean * ((oy1 - yy) // 3)
                bg.rect(sx + off, yy, sx + 2 + off, yy, col)
            bg.rect(sx + lean * (hgt // 3), oy1 - hgt, sx + 2 + lean * (hgt // 3),
                    oy1 - hgt, tuple(lerp(col[:3], (255, 255, 255), 0.35)) + (255,))
            sx += 4
            slot += 1
    # bottom opening: scroll + glow jar (lab clutter)
    boy = shelves[1] + 2
    bg.rect(x0 + 3, y1 - 9, x0 + 10, y1 - 5, PAPER)     # scroll on its side
    bg.rect(x0 + 3, y1 - 6, x0 + 10, y1 - 5, PAPERD)
    bg.put(x0 + 3, y1 - 8, PAPERD)
    jx = x1 - 9
    bg.rect(jx, y1 - 10, jx + 5, y1 - 4, GLASS)         # jar
    bg.rect(jx + 1, y1 - 8, jx + 4, y1 - 5, MINT)       # glow
    bg.put(jx + 1, y1 - 9, SPEC)


def paint_cork():
    """Corkboard obsession wall: pinned notes joined by red string."""
    X, Y = CORK[0] * T, CORK[1] * T
    XW, YH = (CORK[2] - CORK[0] + 1) * T, (CORK[3] - CORK[1] + 1) * T
    x0, y0, x1, y1 = X + 2, Y + 2, X + XW - 3, Y + YH - 3
    bg.rect(x0, y0, x1, y1, TIMBER[3])                  # frame
    bg.rect(x0, y0, x1, y0, TIMBER[1])
    bg.rect(x0 + 2, y0 + 2, x1 - 2, y1 - 2, CORKF[2])   # cork field
    for i in range(14):                                 # fixed speckle
        px = x0 + 2 + h2(i, 0, 21) % (x1 - x0 - 4)
        py = y0 + 2 + h2(0, i, 22) % (y1 - y0 - 4)
        bg.put(px, py, CORKF[3])
    notes = ((x0 + 4, y0 + 4, 6, 7, PAPER), (x0 + 14, y0 + 6, 5, 5, MINT),
             (x0 + 21, y0 + 3, 5, 6, PAPER), (x0 + 8, y0 + 15, 6, 5, PAPER),
             (x0 + 18, y0 + 14, 5, 6, PAPERD))
    pins = []
    for nx, ny, nw, nh, col in notes:
        bg.rect(nx, ny, nx + nw - 1, ny + nh - 1, col)
        bg.rect(nx + 1, ny + nh - 1, nx + nw - 1, ny + nh - 1, PAPERD)
        for ly in range(ny + 2, ny + nh - 2, 2):        # scribble lines
            bg.rect(nx + 1, ly, nx + nw - 3, ly, PAPERD if col != PAPERD else CORKF[3])
        pin = (nx + nw // 2, ny)
        bg.put(pin[0], pin[1], RED)
        pins.append(pin)
    for a, b in zip(pins, pins[1:]):                    # the red string
        bg.line(a[0], a[1], b[0], b[1], RED)


def paint_bed():
    """Canopy-less CT bed: headboard, pillow, hot quilt, footboard, baked
    contact shadow."""
    X, Y = BED[0] * T, BED[1] * T
    XW, YH = (BED[2] - BED[0] + 1) * T, (BED[3] - BED[1] + 1) * T
    x1, y1 = X + XW - 1, Y + YH - 1
    # headboard with posts
    for px in (X, x1 - 2):
        bg.rect(px, Y + 2, px + 2, Y + 13, TIMBER[2])
        bg.rect(px, Y + 2, px + 2, Y + 3, TIMBER[1])    # caps
        bg.rect(px + 2, Y + 4, px + 2, Y + 13, TIMBER[4])
    bg.rect(X + 3, Y + 4, x1 - 3, Y + 12, TIMBER[2])
    bg.rect(X + 3, Y + 4, x1 - 3, Y + 5, TIMBER[1])
    bg.rect(X + 3, Y + 10, x1 - 3, Y + 10, TIMBER[4])   # panel groove
    bg.rect(X + 3, Y + 12, x1 - 3, Y + 12, TIMBER[4])
    # pillow
    bg.rect(X + 4, Y + 15, x1 - 4, Y + 23, LINENR[1])
    bg.rect(X + 5, Y + 15, x1 - 5, Y + 17, LINENR[0])
    bg.rect(X + 4, Y + 22, x1 - 4, Y + 23, LINENR[3])
    for cx_, cy_ in ((X + 4, Y + 15), (x1 - 4, Y + 15), (X + 4, Y + 23), (x1 - 4, Y + 23)):
        bg.put(cx_, cy_, weave_px(cx_, cy_, FLOORR))    # knock off the corners
    # folded linen band, then the quilt
    bg.rect(X + 2, Y + 24, x1 - 2, Y + 27, LINENR[1])
    bg.rect(X + 2, Y + 24, x1 - 2, Y + 24, LINENR[0])
    bg.rect(X + 2, Y + 27, x1 - 2, Y + 27, LINENR[3])
    bg.rect(X + 1, Y + 28, x1 - 1, Y + 51, QUILT[1])
    bg.rect(X + 1, Y + 28, x1 - 1, Y + 29, QUILT[0])
    for fy in (Y + 36, Y + 44):                         # fold creases
        bg.rect(X + 1, fy, x1 - 1, fy, QUILT[3])
    bg.rect(X + 1, Y + 28, X + 2, Y + 51, QUILT[3])     # side borders
    bg.rect(x1 - 2, Y + 28, x1 - 1, Y + 51, QUILT[3])
    # footboard with post stubs
    bg.rect(X + 1, Y + 52, x1 - 1, Y + 57, TIMBER[2])
    bg.rect(X + 1, Y + 52, x1 - 1, Y + 52, TIMBER[1])
    bg.rect(X + 1, Y + 56, x1 - 1, Y + 57, TIMBER[4])
    for px in (X, x1 - 2):
        bg.rect(px, Y + 50, px + 2, Y + 58, TIMBER[2])
        bg.rect(px, Y + 50, px + 2, Y + 51, TIMBER[1])
    # baked contact shadow on the weave
    for y in range(Y + 59, Y + YH):
        for x in range(X, X + XW):
            bg.put(x, y, weave_px(x, y, FLOORR, shade=2))
    bg.rect(X, Y + 4, X, Y + 58, TIMBER[5])             # west silhouette edge


def paint_desk():
    """Worktable: microscope, book stack, oil lamp on a lit top; drawers below."""
    X, Y = DESK[0] * T, DESK[1] * T
    XW, YH = (DESK[2] - DESK[0] + 1) * T, (DESK[3] - DESK[1] + 1) * T
    x1, y1 = X + XW - 1, Y + YH - 1
    # props stand on the desktop edge at Y+12
    mx = X + 6                                          # microscope
    bg.rect(mx, Y + 10, mx + 8, Y + 11, STEEL[2])       # base
    bg.rect(mx + 5, Y + 2, mx + 7, Y + 9, STEEL[1])     # tube
    bg.rect(mx + 7, Y + 4, mx + 7, Y + 9, STEEL[3])
    bg.rect(mx + 3, Y + 6, mx + 4, Y + 9, STEEL[2])     # arm
    bg.put(mx + 5, Y + 2, SPEC)
    sx = X + 20                                         # book stack
    for i, col in enumerate((SPINES[1], SPINES[3], SPINES[0])):
        bg.rect(sx - i, Y + 9 - i * 3, sx + 8 - i, Y + 11 - i * 3, col)
    lx = X + 34                                         # oil lamp
    bg.rect(lx + 1, Y + 10, lx + 5, Y + 11, BRASS[2])
    bg.rect(lx + 2, Y + 8, lx + 4, Y + 9, BRASS[3])
    bg.rect(lx + 1, Y + 2, lx + 5, Y + 7, GLASS)        # chimney
    bg.rect(lx + 2, Y + 4, lx + 4, Y + 6, ACCENT)       # flame
    bg.put(lx + 3, Y + 4, SUN)
    # desktop
    bg.rect(X + 2, Y + 12, x1 - 2, Y + 14, TIMBER[1])
    bg.rect(X + 2, Y + 15, x1 - 2, Y + 16, TIMBER[2])
    bg.rect(X + 2, Y + 17, x1 - 2, Y + 17, TIMBER[4])
    # open table: shadowed weave under the top, stout legs, one small drawer
    for y in range(Y + 18, Y + 30):
        for x in range(X + 3, x1 - 2):
            bg.put(x, y, weave_px(x, y, FLOORR, shade=1))
    for px in (X + 4, x1 - 7):
        bg.rect(px, Y + 18, px + 2, Y + 29, TIMBER[3])  # legs
        bg.rect(px + 2, Y + 18, px + 2, Y + 29, TIMBER[4])
        bg.rect(px, Y + 28, px + 2, Y + 29, TIMBER[4])
    bg.rect(X + 18, Y + 18, X + 29, Y + 24, TIMBER[2])  # hung drawer box
    bg.rect(X + 18, Y + 18, X + 29, Y + 18, TIMBER[1])
    bg.rect(X + 18, Y + 24, X + 29, Y + 24, TIMBER[4])
    bg.rect(X + 23, Y + 21, X + 24, Y + 21, BRASS[1])
    # baked contact shadow
    for y in range(Y + 30, Y + YH):
        for x in range(X + 2, x1 - 1):
            bg.put(x, y, weave_px(x, y, FLOORR, shade=2))


def paint_chair():
    """Desk chair seen from behind: seat, then the backrest below it."""
    X, Y = CHAIR[0] * T, CHAIR[1] * T
    bg.rect(X + 3, Y + 2, X + 12, Y + 6, TIMBER[1])     # seat
    bg.rect(X + 3, Y + 6, X + 12, Y + 6, TIMBER[3])
    bg.rect(X + 4, Y + 7, X + 11, Y + 13, TIMBER[2])    # backrest
    bg.rect(X + 4, Y + 7, X + 11, Y + 7, TIMBER[1])
    for gx in (X + 6, X + 9):
        bg.rect(gx, Y + 8, gx, Y + 12, TIMBER[4])       # slats
    bg.rect(X + 4, Y + 13, X + 11, Y + 13, TIMBER[4])
    for px, py in ((X + 3, Y + 14), (X + 12, Y + 14)):
        bg.put(px, py, TIMBER[4])                       # rear legs
    for x in range(X + 4, X + 12):                      # sliver of shadow
        bg.put(x, Y + 15, weave_px(x, Y + 15, FLOORR, shade=2))


def paint_basket():
    """Wash bucket with a still teal eye of water."""
    X, Y = BASK[0] * T, BASK[1] * T
    bg.rect(X + 3, Y + 3, X + 12, Y + 4, TIMBER[1])     # rim
    bg.rect(X + 3, Y + 5, X + 12, Y + 11, TIMBER[2])    # staves
    for sx in (X + 5, X + 8, X + 11):
        bg.rect(sx, Y + 5, sx, Y + 11, TIMBER[4])
    bg.rect(X + 4, Y + 12, X + 11, Y + 12, TIMBER[4])   # bottom curve
    bg.rect(X + 5, Y + 4, X + 10, Y + 6, WATER)         # water
    bg.put(X + 6, Y + 4, SPEC)
    for x in range(X + 4, X + 12):
        bg.put(x, Y + 14, weave_px(x, Y + 14, FLOORR, shade=2))


# =================================================================================
# compose: terrain fabric per cell, then the furniture objects over it
# =================================================================================

# whole-tile light pool under the window: lit core, dither fringe, no gradients
GC0, GC1 = WIN[0] + 1, WIN[2] - 1              # glass columns
lit_cells = {(c, FLOOR_ROW) for c in range(WIN[0], WIN[2] + 1)}
lit_cells |= {(c, FLOOR_ROW + 1) for c in range(WIN[0], WIN[2] + 1)}
lit_cells |= {(GC0, FLOOR_ROW + 2), (GC1, FLOOR_ROW + 2)}
fringe_cells = {(WIN[0], FLOOR_ROW + 2), (WIN[2], FLOOR_ROW + 2),
                (GC0, FLOOR_ROW + 3), (GC1, FLOOR_ROW + 3)}

for ty in range(m.rows_n):
    for tx in range(m.cols):
        ch = m.at(tx, ty)
        if ch == "V":
            continue                                     # canvas fill IS the void tile
        if ch in ".dhwb":                                # weave under floor + furniture
            if (tx, ty) in lit_cells:
                kind = "lit"
            elif (tx, ty) in fringe_cells:
                kind = "fringe"
            elif ty in (FLOOR_ROW, RAIL_ROW - 1):
                kind = "shadow"                          # wall shadow / drop penumbra
            else:
                kind = "plain"
            paint_floor_cell(tx, ty, kind)
        elif ch == "#":
            if ty > RAIL_ROW:
                paint_stub_cell(tx, ty)
            elif ty >= FLOOR_ROW:
                paint_side_cell(tx, ty)
            else:
                paint_wall_cell(tx, ty)
        elif ch in "WSC" and ty >= WALL_TOP:             # planks under wall furniture
            paint_wall_cell(tx, ty)
        elif ch == "R":
            paint_drop_cell(tx, ty, stair=False)
            # posts cap every rail run: at the stair gap and against walls
            newel = m.at(tx - 1, ty) != "R" or m.at(tx + 1, ty) != "R"
            paint_rail_cell(tx, ty, newel)
        elif ch == "s":
            paint_drop_cell(tx, ty, stair=True)
        elif ch == "-":
            paint_step_cell(tx, ty)

paint_window()
paint_shelf()
paint_cork()
paint_bed()
paint_desk()
paint_chair()
paint_basket()

# =================================================================================
# slice, dedupe, write the tileset (both layers share one atlas)
# =================================================================================
tiles, seen = [], {}
_, lower = slice_atlas(bg, tiles, seen)
_, upper = slice_atlas(ov, tiles, seen, skip_empty=True)
write_atlas(os.path.join(OUTDIR, "house_tiles.png"), tiles)
write_tileset_tres(os.path.join(OUTDIR, "house_tiles.tres"),
                   "res://assets/tilesets/house_tiles.png", len(tiles))
write_layout(os.path.join(OUTDIR, "house_layout.txt"),
             {"lower": lower, "upper": upper},
             "from assets/maps/house.txt by _gen_tileset_house.py")
n_upper = sum(1 for row in upper for i in row if i is not None)
print(f"{len(tiles)} unique tiles from {m.cols * m.rows_n} cells "
      f"({n_upper} upper-layer cells)")

# =================================================================================
# scene dressing: window beam + curtain frames (runtime overlays, not tiles)
# =================================================================================
BEAM = (255, 216, 160)


def write_glow():
    """house_glow.png — the dawn beam as an ADDITIVE overlay: hard-banded warm
    light falling from the glass over the pool, stepped edges, no gradients.
    Full canvas size so the scene stamps it at (0, 0); regenerating after a
    map move re-aims it automatically."""
    img = Img(W, H)
    X, Y = WIN[0] * T, WIN[1] * T
    XW = (WIN[2] - WIN[0] + 1) * T
    gx0, gx1 = X + 9, X + XW - 10
    sill_y, floor_y = Y + 52, FLOOR_ROW * T
    img.rect(gx0, Y + 19, gx1, Y + 49, BEAM + (52,))    # halo over the glass
    for y in range(sill_y, floor_y + 4 * T):
        if y < floor_y:                                 # widening past the sill
            k = (y - sill_y) // 4 + 1
            x0, x1 = max(X, gx0 - 3 * k), min(X + XW - 1, gx1 + 3 * k)
            a = 62
        else:                                           # full-width pool bands
            x0, x1 = X, X + XW - 1
            a = 62 if y < floor_y + 2 * T else (44 if y < floor_y + 3 * T else 26)
        img.rect(x0, y, x1, y, BEAM + (a,))
    img.save(os.path.join(OUTDIR, "house_glow.png"))


def write_curtains():
    """house_curtains.png — two 64x64 frames over the window bay (closed,
    half-open); the fully open tied-back drapes are baked in the tiles, so
    the scene hides this sprite once the beat finishes."""
    fw = (WIN[2] - WIN[0] + 1) * T
    sheet = P(fw * 2, 64)
    for fi, cover in enumerate((26, 12)):               # panel width per frame
        ox = fi * fw
        for side in (0, 1):
            xa = ox + 4 if side == 0 else ox + fw - 4 - cover
            for x in range(xa, xa + cover):
                u = (x - xa) if side == 0 else (xa + cover - 1 - x)
                for y in range(17, 52):
                    c = CURT[0] if u == cover - 1 else \
                        (CURT[2] if u % 4 == 2 else CURT[1])
                    sheet.put(x, y, c)
            sheet.rect(xa, 49, xa + cover - 1, 51, CURT[3])      # hem band
            sheet.rect(xa, 17, xa + cover - 1, 18, CURT[3])      # rod shadow
        draw_flasks(sheet, ox, 0)                       # sill flasks in front
    sheet.save(os.path.join(OUTDIR, "house_curtains.png"))


write_glow()
write_curtains()

if "--preview" in sys.argv:
    out = sys.argv[sys.argv.index("--preview") + 1]
    for y in range(H):                                  # composite upper over lower
        for x in range(W):
            p = ov.get(x, y)
            if p[3]:
                bg.put(x, y, p)
    bg.save(out if os.path.isabs(out) else os.path.join(HERE, out))
