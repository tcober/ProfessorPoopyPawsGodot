#!/usr/bin/env python3
"""Basil's ground floor BEFORE THE LAB — Prologue A0 "The Fever".

The byte-locked twin of _gen_tileset_downstairs.py, on the same `downstairs`
palette so the two rooms read as one room across the swap: the kitchen west
end is identical (hearth, sink window, dish shelf, rug + table, the loft
stair, the front door), and the east end is NOT a lab yet — bare plank wall
where the pipe manifold will hang, a stack of household crates where the
boiler will stand, low crates and preserve jars where the workbench will go.
The flask shelf is already here as MOM'S PRESERVE SHELF (same art — the
point: he repurposes the house). Mom's plank door in the west wall is
WALKABLE in this map's grid; scene/downstairs_fever.gd loads this room until
prologue_remedy_made and the built downstairs after it.

Re-run: python3 assets/_gen_tileset_downstairs_bare.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _palette import ramp
from _tilekit import sprite_img
from _interior import (Room, flag_px, TIMBER, STONER, T)
from _interior_props import (window, rug, hearth, sink_counter,
                             dish_shelf, flask_shelf, table,
                             armchair, potted_plant, framed_picture,
                             wall_clock, interior_door, crates)

room = Room("downstairs_bare", "downstairs", flag_px, (255, 186, 110),
            lit_blend=0.62)

QUILT = ramp((226, 76, 132), "violet", 4)          # the house's hot upholstery
RUGB = ramp((64, 70, 96), "violet", 6)             # rug base: deep slate
DAWN = [(255, 232, 160, 255), (255, 186, 122, 255), (244, 126, 128, 255),
        (198, 84, 152, 255), (122, 62, 148, 255)]
GLOWC = (255, 186, 116)
DAYL0 = (255, 228, 164, 255)
DAYL1 = (255, 196, 124, 255)
TREADS = [((20, 16, 38, 255), (12, 10, 26, 255)),  # swallowed by the loft dark
          ((32, 24, 50, 255), (20, 15, 40, 255)),
          ((46, 34, 62, 255), (30, 22, 48, 255)),
          ((78, 54, 82, 255), (54, 38, 66, 255)),
          (TIMBER[2], TIMBER[4]),
          (TIMBER[2], TIMBER[4]),
          (TIMBER[1], TIMBER[3]),
          (TIMBER[0], TIMBER[2])]

HEARTH = room.bbox("H")
WIN = room.bbox("W")
DOOR = room.bbox("-")
STAIR = room.bbox("s")
SOUTH_ROW = room.bbox("#")[3]
FR = room.FLOOR_ROW

# whole-tile light: hearth pool, window fringe beside it, doorway daylight
room.lit_cells = {(c, FR) for c in range(HEARTH[0], HEARTH[2] + 1)}
room.fringe_cells = ({(c, FR) for c in range(WIN[0], WIN[2] + 1)} |
                     {(c, SOUTH_ROW - 1) for c in range(DOOR[0], DOOR[2] + 1)})
room.shadow_rows = (FR, SOUTH_ROW - 1)


def _stairs(tx, ty):
    room.stair_cell(tx, ty, STAIR[1], TREADS)


def _wall_rules(tx, ty):
    if room.m.at(tx - 1, ty) == "s" or room.m.at(tx + 1, ty) == "s":
        room.jamb_cell(tx, ty, stair_char="s")
        return True
    if ty == SOUTH_ROW:
        room.south_cell(tx, ty)
        return True
    return False


room.paint_terrain(wall_rules=_wall_rules,
                   special={"s": _stairs, "-": lambda tx, ty: None})


def _door():
    """The front door: an OPEN doorway spilling daylight, lintel on the upper
    canvas, stone stoop sinking into the void — verbatim the downstairs
    recipe (same room, same door)."""
    X, Y, XW, YH = room.px(DOOR)
    x1 = X + XW - 1
    dy1 = Y + T - 1
    bg, ov = room.bg, room.ov
    bg.rect(X + 3, Y, x1 - 3, Y + 9, DAYL0)
    bg.rect(X + 3, Y + 10, x1 - 3, dy1 - 2, DAYL1)
    bg.rect(X + 3, dy1 - 1, x1 - 3, dy1, TIMBER[5])     # threshold
    for side in (0, 1):                                 # posts
        px = X if side == 0 else x1 - 2
        bg.rect(px, Y, px + 2, dy1, TIMBER[3])
        bg.rect(px + (2 if side == 0 else 0), Y, px + (2 if side == 0 else 0), dy1, TIMBER[1])
        bg.rect(px + (0 if side == 0 else 2), Y, px + (0 if side == 0 else 2), dy1, TIMBER[5])
    ov.rect(X, Y, x1, Y + 1, TIMBER[2])                 # lintel rides UPPER
    ov.rect(X, Y, x1, Y, TIMBER[1])
    ov.rect(X, Y + 2, x1, Y + 3, TIMBER[4])
    sy = Y + T                                          # stoop
    bg.rect(X + 2, sy, x1 - 2, sy, STONER[1])
    bg.rect(X + 2, sy + 1, x1 - 2, sy + 5, STONER[3])
    bg.rect(X + 4, sy + 6, x1 - 4, sy + 6, STONER[2])
    bg.rect(X + 4, sy + 7, x1 - 4, sy + 10, STONER[4])
    bg.rect(X + 6, sy + 11, x1 - 6, sy + 13, (24, 18, 44, 255))


_door()

# props at their map footprints — the kitchen west end is the built room's,
# verbatim; the east end is what a house keeps in a spare corner
room.place("g", rug(64, 48, RUGB, (238, 168, 96, 255)))
room.place("H", hearth(48, 48, STONER))
room.place("W", window(32, 32, DAWN, sun=False, flasks=False, salt=33))
room.place("k", dish_shelf(32, 16))
room.place("C", sink_counter(32, 32))
room.place("p", framed_picture(32, 16, DAWN, salt=42))
room.place("o", wall_clock())
# the flask shelf, already on the wall — MOM'S PRESERVE SHELF (the same art
# the lab will inherit; he doesn't buy a lab, he repurposes the house)
room.place("F", flask_shelf(48, 32))
# MOM'S DOOR, set into the WEST wall and WALKABLE here: the fever chapter
# walks through it into scene/momroom.tscn (SOLID in the downstairs.txt twin)
room.place("'", interior_door(16, 32, room.WALLR))
# free-standing furniture rides y-sorted (the downstairs recipe): table,
# armchair, and the two crate piles holding the corner the lab will claim
room.bake_shadow("r", 3)
room.emit_prop("Table", "tT", sprite_img(table(32, 32), 32, 32))
room.emit_prop("Armchair", "r", sprite_img(armchair(32, 32, QUILT), 32, 32))
room.bake_shadow("q", 3)
room.emit_prop("Crates", "q", sprite_img(crates(32, 40), 32, 40))
room.bake_shadow("u", 2)
room.emit_prop("Cratepair", "u", sprite_img(crates(32, 24, low=True), 32, 24))
room.place("P", potted_plant(16, 32), shadow_h=2)


def _glow(img):
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
    wx0, wy0, wxw, wyh = room.px(WIN)                   # window daylight
    img.rect(wx0 + 4, wy0 + 6, wx0 + wxw - 5, wy0 + wyh - 4, (255, 226, 170, 34))
    img.rect(wx0 + 2, wy0 + wyh, wx0 + wxw - 3, fy + T - 1, (255, 226, 170, 22))
    dx0, dy0, dxw, dyh = room.px(DOOR)                  # doorway shaft
    img.rect(dx0 + 3, dy0 - 12, dx0 + dxw - 4, dy0 + 12, (255, 226, 170, 26))


room.write_glow(_glow)
room.south_lift()          # mask the south wall's feet-sink sliver (upper band)
room.finish()
