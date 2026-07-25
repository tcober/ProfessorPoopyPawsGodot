#!/usr/bin/env python3
"""THE LANTERNWOOD LIBRARY, inside — a thin room CONFIG (Act 1 "The Ebb").

Fuji's reading HALL in Lanternwood, her snowy pine-forest hometown, on the
night the world's magic drains and again on the night she finds the thesis.
Terrain/compose/light/output live in assets/_interior.py; the furniture
comes from assets/_interior_props.py. The downstairs-diorama recipe: an
18-tile room floating in void, every wall stretch occupied. Picks the
`library` palette (rosewood plank walls / deep plum weave; firelight amber
the one warmth against cold snow-blue night glass): the stone hearth is the
hot light source — the fire itself is the ANIMATED library_fire.png sheet
the scene stamps over the cold firebox (the downstairs idiom) — four tall
wall bookshelves alternate with three high night windows, and the coffee
COUNTER (brass kettle on its candle warmer + a waiting cup) stands before
the fire, Fuji's midnight coffee station.

REBUILT 2026-07-25 (it was a 10-tile closet): the building outside became a
civic hall, and Act 1's research gate needs somewhere to search. THE THREE
STACKS are free-standing double-sided cases on 2x2 footprints with walkable
aisles between them — y-sorted entities, never baked, because a body walks
BOTH sides of every one. Stacks / desk / armchair / counter all live in
library_props.txt.

Re-run: python3 assets/_gen_tileset_library.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img
from _palette import ramp
from _tilekit import sprite_img
from _interior import Room, weave_px, TIMBER, STONER, T, OUTDIR
from _interior_props import (window, rug, hearth, bookshelf, stack, wall_clock,
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

# whole-tile light: the hearth pool + its rim, and a second pool under the
# desk lamp at the far end — an 18-tile hall lit by one fire in its west
# corner would leave the reading end unreadably dark. Everything between
# them is aisle, and the aisles are MEANT to be dim: the stacks are searched
# by candlelight.
DESK = room.bbox("d")
room.lit_cells = {(c, FR) for c in range(HEARTH[0], HEARTH[2] + 1)} \
        | {(c, FR + 1) for c in range(DESK[0], DESK[2] + 1)}
room.fringe_cells = {(HEARTH[2] + 1, FR), (HEARTH[0], FR + 1),
                     (DESK[0] - 1, FR + 1), (DESK[0], FR), (DESK[2], FR)}
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
# place_each, not place, for BOTH wall runs: the hall has four bookshelves and
# three windows, and a combined bbox would blit one sprite across the lot.
room.place("g", rug(64, 32, RUGB, (238, 186, 116, 255)))
room.place("H", hearth(48, 48, STONER))
room.place_each("K", bookshelf(32, 48, SPINES))
room.place_each("W", window(32, 32, NIGHT, sun=False, flasks=False, salt=39))
room.place("o", wall_clock())

# ---- y-sorted entities (Tier 3: bodies pass both sides / tuck behind) --------------
# THE STACKS — the aisle shelving Act 1's research gate searches. 48px of art
# on a 32px footprint, so the case stands one cell taller than the ground it
# occupies and whoever is in the aisle behind it reads as a head above the
# books. Baked, they would draw UNDER anyone standing south of them.
room.bake_shadow("S", 3, each=True)
room.emit_prop("Stack", "S", sprite_img(stack(32, 48, SPINES), 32, 48),
               each=True)
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
    # the desk's oil lamp — the hall's second pool, and the light she reads by
    dx0_, dy0_, dxw_, _ = room.px(room.bbox("d"))
    Room.glow_blob(img, dx0_ + dxw_ - 6, dy0_ - 12, 14, (255, 214, 150), 52)
    # a candle on top of each stack — the only reason the aisles are findable
    # at all, and the reason a town of honest flame can still read at night
    for comp in room.comps("S"):
        sx0, sy0, _, _ = room.px(room.comp_bbox(comp))
        Room.glow_blob(img, sx0 + 16, sy0 - 12, 11, (255, 206, 140), 40)
    # cold snow-blue night at each window — a faint sheen, a fainter fall down
    # the wainscot (the one cool light against the fire)
    for comp in room.comps("W"):
        wx0, wy0, wxw, wyh = room.px(room.comp_bbox(comp))
        img.rect(wx0 + 3, wy0 + 4, wx0 + wxw - 4, wy0 + wyh - 4, (176, 202, 244, 30))
        img.rect(wx0 + 2, wy0 + wyh, wx0 + wxw - 3, wy0 + wyh + 10,
                 (170, 198, 240, 16))


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
