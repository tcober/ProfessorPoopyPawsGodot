#!/usr/bin/env python3
"""THE ACADEMY READING ROOM — a thin room CONFIG (Prologue A0 "The Fever").

The Alembic Academy's library, BRIGHT ERA, deliberately on the Lanternwood
library's recipe: the same 18-tile hall, the three free-standing STACKS
with walkable aisles, the reading desk under the clock. Twenty years later
Fuji searches a room shaped exactly like this one, and neither scene says
so. Picks the `academy_library` palette (cream-oak panelling over warm
sandstone flags, mint-glass accent); tall oak wall shelves alternate with
high grey-morning windows — the fever days are the one overcast stretch of
the bright era, and the room is lit by that flat daylight rather than any
fire. The stacks / desk ride y-sorted in academy_library_props.txt.

Re-run: python3 assets/_gen_tileset_academy_library.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _palette import ramp
from _tilekit import sprite_img
from _interior import Room, flag_px, TIMBER, T
from _interior_props import (window, rug, bookshelf, stack, wall_clock, desk)

room = Room("academy_library", "academy_library", flag_px, (232, 236, 240),
            floor_chars=".g", lit_blend=0.30)

SPINES = [(146, 98, 160, 255),   # plum
          (62, 132, 138, 255),   # teal
          (186, 104, 54, 255),   # rust leather
          (226, 214, 190, 255),  # vellum
          (98, 128, 196, 255),   # ultramarine
          (232, 188, 96, 255)]   # mustard
RUGB = ramp((92, 122, 112), "violet", 6)               # sage-green rug
GREYD = [(222, 228, 236, 255), (196, 206, 220, 255), (164, 176, 200, 255),
         (128, 140, 174, 255), (94, 104, 148, 255)]    # grey morning glass
LAMP = [(255, 236, 176, 255), (255, 210, 132, 255), (238, 158, 120, 255),
        (196, 110, 140, 255), (128, 72, 132, 255)]     # the desk's oil lamp

WIN = room.bbox("W")
DOOR = room.bbox("-")
DESK = room.bbox("d")
FR = room.FLOOR_ROW
SOUTH_ROW = DOOR[1]

# whole-tile light: a flat pool below each window (grey daylight, no sun),
# and the desk's own lamp pool at the east end
room.lit_cells = set()
room.fringe_cells = {(c, FR) for comp in room.comps("W")
                     for c in range(room.comp_bbox(comp)[0],
                                    room.comp_bbox(comp)[2] + 1)} \
        | {(c, FR + 1) for c in range(DESK[0], DESK[2] + 1)}
room.shadow_rows = (FR, SOUTH_ROW - 1)


def _wall_rules(tx, ty):
    if ty == SOUTH_ROW:
        room.south_cell(tx, ty)
        return True
    return False


room.paint_terrain(wall_rules=_wall_rules)

# a panelled lintel over the door on the UPPER canvas (the sickroom idiom)
_dx0, _dy0, _dxw, _dyh = room.px(DOOR)
_dx1 = _dx0 + _dxw - 1
room.ov.rect(_dx0, _dy0, _dx1, _dy0 + 1, TIMBER[2])
room.ov.rect(_dx0, _dy0, _dx1, _dy0, TIMBER[1])
room.ov.rect(_dx0, _dy0 + 2, _dx1, _dy0 + 2, TIMBER[4])

# ---- baked props (Tier 1) ----------------------------------------------------------
# place_each for BOTH wall runs (five shelf runs, three windows — a combined
# bbox would blit one sprite across the lot)
room.place("g", rug(64, 32, RUGB, (232, 214, 178, 255)))
room.place_each("K", bookshelf(32, 48, SPINES))
room.place_each("W", window(32, 32, GREYD, sun=False, flasks=False, salt=44))
room.place("o", wall_clock())

# ---- y-sorted entities (Tier 3) ----------------------------------------------------
# THE STACKS — 48px of art on 2x2 footprints; a body in the aisle north of
# one reads as a head above the books (the library recipe, verbatim)
room.bake_shadow("S", 3, each=True)
room.emit_prop("Stack", "S", sprite_img(stack(32, 48, SPINES), 32, 48),
               each=True)
# the reading desk — where the boy copies out half a page he cannot borrow
room.bake_shadow("d", 2)
room.emit_prop("Desk", "d", sprite_img(desk(48, 32, LAMP), 48, 32))


def _glow(img):
    # flat grey daylight standing below every window — no sun on the fever
    # days, and no fire in an Academy room: the light is honest and cold
    for comp in room.comps("W"):
        wx0, wy0, wxw, wyh = room.px(room.comp_bbox(comp))
        img.rect(wx0 + 3, wy0 + 4, wx0 + wxw - 4, wy0 + wyh - 4, (216, 226, 240, 34))
        img.rect(wx0 + 2, wy0 + wyh, wx0 + wxw - 3, wy0 + wyh + 2 * T,
                 (210, 220, 238, 18))
    # the desk's oil lamp — the one warmth, and the light he copies by
    dx0_, dy0_, dxw_, _ = room.px(DESK)
    Room.glow_blob(img, dx0_ + dxw_ - 6, dy0_ - 12, 14, (255, 214, 150), 48)


room.write_glow(_glow)
room.south_lift()          # mask the south wall's feet-sink sliver (upper band)
room.finish()
