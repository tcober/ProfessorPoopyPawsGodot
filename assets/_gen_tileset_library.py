#!/usr/bin/env python3
"""THE LANTERNWOOD LIBRARY — a thin room CONFIG (Act 1 "The Ebb").

Fuji's small library in Lanternwood, her snowy pine-forest hometown, on the
night the world's magic drains. Terrain/compose/light/output live in
assets/_interior.py; the furniture comes from assets/_interior_props.py.
The loft-diorama recipe: a SMALL dense timber reading room floating in void
(10-tile interior), every wall stretch occupied. Picks the `library`
palette (rosewood plank walls / deep plum weave; firelight amber the one
warmth against cold snow-blue night glass in the window): the stone hearth
is the hot light source — the fire itself is the ANIMATED library_fire.png
sheet the scene stamps over the cold firebox (the downstairs idiom) — two
tall bookshelves flank the high night window, and the coffee COUNTER (the
new counter-walk prop: brass kettle on its candle warmer + a waiting cup)
stands before the fire, Fuji's midnight coffee station. Desk / armchair /
counter live as y-sorted entities (library_props.txt).

Re-run: python3 assets/_gen_tileset_library.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img
from _palette import ramp
from _tilekit import sprite_img
from _interior import Room, weave_px, TIMBER, STONER, T, OUTDIR
from _interior_props import (window, rug, hearth, bookshelf, wall_clock,
                             desk, armchair, coffee_counter, fire_frames)

room = Room("library", "library", weave_px, (255, 200, 124), floor_chars=".g",
            lit_blend=0.50)

SPINES = [(186, 104, 54, 255),   # rust leather
          (146, 98, 160, 255),   # plum
          (232, 188, 96, 255),   # mustard
          (62, 132, 138, 255),   # teal
          (226, 214, 190, 255),  # vellum
          (154, 58, 74, 255)]    # wine
RUGB = ramp((70, 58, 104), "violet", 6)                # deep indigo-plum rug
CHAIRR = ramp((188, 92, 74), "violet", 4)              # rust leather armchair
NIGHT = [(196, 214, 242, 255), (150, 176, 220, 255), (106, 132, 194, 255),
         (70, 92, 162, 255), (44, 60, 124, 255)]       # snow-blue night glass
LAMP = [(255, 236, 176, 255), (255, 210, 132, 255), (238, 158, 120, 255),
        (196, 110, 140, 255), (128, 72, 132, 255)]     # the desk's oil lamp
GLOWC = (255, 186, 116)

HEARTH = room.bbox("H")
WIN = room.bbox("W")
DOOR = room.bbox("-")
FR = room.FLOOR_ROW
SOUTH_ROW = DOOR[1]

# whole-tile light: the hearth pool + its rim; the room edges sit in shade
# (night of the Ebb — the fire and the candles carry the room)
room.lit_cells = {(c, FR) for c in range(HEARTH[0], HEARTH[2] + 1)}
room.fringe_cells = {(HEARTH[2] + 1, FR), (HEARTH[0], FR + 1)}
room.shadow_rows = (FR, SOUTH_ROW - 1)


def _wall_rules(tx, ty):
    if ty == SOUTH_ROW:
        room.south_cell(tx, ty)
        return True
    return False


room.paint_terrain(wall_rules=_wall_rules)

# a panelled lintel over the door on the UPPER canvas (the sickroom idiom —
# confined to the door cells, so it can't fail the ridge-cap lint)
_dx0, _dy0, _dxw, _dyh = room.px(DOOR)
_dx1 = _dx0 + _dxw - 1
room.ov.rect(_dx0, _dy0, _dx1, _dy0 + 1, TIMBER[2])
room.ov.rect(_dx0, _dy0, _dx1, _dy0, TIMBER[1])
room.ov.rect(_dx0, _dy0 + 2, _dx1, _dy0 + 2, TIMBER[4])

# ---- baked props (Tier 1: wall-flush or walkable, nobody stands behind them) -------
room.place("g", rug(48, 32, RUGB, (238, 186, 116, 255)))
room.place("H", hearth(48, 48, STONER))
room.place_each("K", bookshelf(32, 48, SPINES))
room.place("W", window(32, 32, NIGHT, sun=False, flasks=False, salt=39))
room.place("o", wall_clock())

# ---- y-sorted entities (Tier 3: bodies pass both sides / tuck behind) --------------
# the reading desk — stand on the row behind it and it hides your legs
room.bake_shadow("d", 2)
room.emit_prop("Desk", "d", sprite_img(desk(48, 32, LAMP), 48, 32))
# the rust reading armchair in the east nook
room.bake_shadow("r", 3)
room.emit_prop("Armchair", "r", sprite_img(armchair(32, 32, CHAIRR), 32, 32))
# the coffee counter before the fire (counter-walk: top row c is the tuck
# row — the kettle anchor cell — bottom row C solid)
room.bake_shadow("cC", 3)
room.emit_prop("Counter", "cC", sprite_img(coffee_counter(32, 32), 32, 32))


def _glow(img):
    # the hearth wash — the room's one big warmth (the downstairs recipe)
    hx0, hy0, hxw, hyh = room.px(HEARTH)
    hx1 = hx0 + hxw - 1
    fy = FR * T
    img.rect(hx0 + 10, hy0 + 20, hx1 - 10, hy0 + 47, GLOWC + (50,))
    for y in range(hy0 + 44, fy + 2 * T):
        if y < fy:
            x0, x1, a = hx0 + 8, hx1 - 8, 56
        elif y < fy + T:
            x0, x1, a = hx0 - 6, hx1 + 6, 40
        else:
            x0, x1, a = hx0 + 2, hx1 - 2, 24
        img.rect(max(0, x0), y, min(room.W - 1, x1), y, GLOWC + (a,))
    # the mantel candle's little tongue
    Room.glow_blob(img, hx0 + 8, hy0 + 9, 5, (255, 214, 150), 36)
    # the kettle's candle warmer on the counter
    cx0, cy0, _, _ = room.px(room.bbox("cC"))
    Room.glow_blob(img, cx0 + 9, cy0 + 5, 8, (255, 214, 150), 44)
    # the desk's oil lamp
    dx0_, dy0_, dxw_, _ = room.px(room.bbox("d"))
    Room.glow_blob(img, dx0_ + dxw_ - 6, dy0_ - 12, 8, (255, 214, 150), 40)
    # cold snow-blue night at the window — a faint sheen, a fainter fall
    # down the wainscot (the one cool light against the fire)
    wx0, wy0, wxw, wyh = room.px(WIN)
    img.rect(wx0 + 3, wy0 + 4, wx0 + wxw - 4, wy0 + wyh - 4, (176, 202, 244, 30))
    img.rect(wx0 + 2, wy0 + wyh, wx0 + wxw - 3, wy0 + wyh + 10, (170, 198, 240, 16))


room.write_glow(_glow)


def _fire_sheet():
    """The hearth fire (3 frames): the scene stamps a root Sprite2D over the
    cold firebox and cycles it — the downstairs_fire idiom."""
    fire = fire_frames()
    fw, fh = 28, 24
    sheet = Img(fw * len(fire), fh)
    for i, f in enumerate(fire):
        sheet.blit_cell(f, i * fw, 0)
    sheet.save(os.path.join(OUTDIR, "library_fire.png"))


_fire_sheet()
room.south_lift()          # mask the south wall's feet-sink sliver (upper band)
room.finish()
