#!/usr/bin/env python3
"""The doctor's surgery — a thin room CONFIG (Prologue B "the verdict").

Terrain/compose/light/output in assets/_interior.py; furniture in
assets/_interior_props.py. Picks the `sickroom` palette (pale lavender walls /
cool slate floor, a warm lamp against the chill), places the sickbed + window
+ tonic shelf + visitor's chair, and a hushed warm glow at the bedside. Kitty
sits up in the bed as a separate NPC sprite (npc_kitty_bed) the scene spawns
at the pillow — this file only bakes the bed she lies in.

Re-run: python3 assets/_gen_tileset_sickroom.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _palette import ramp
from _tilekit import sprite_img
from _interior import Room, weave_px, TIMBER, BRASS, T
from _interior_props import (window, rug, bed, flask_shelf, framed_picture,
                             chair, potted_plant)

room = Room("sickroom", "sickroom", weave_px, (255, 224, 176), floor_chars=".g",
            lit_blend=0.30)

LINEN = ramp((224, 220, 236), "violet", 4)             # the bedclothes: pale
BLANK = ramp((150, 170, 208), "violet", 4)             # cool blue blanket
RUGB = ramp((168, 108, 120), "violet", 6)              # warm dusty-rose rug
                                                       # (one warm note in the chill)
GLASSD = [(214, 224, 232, 255), (188, 200, 214, 255), (160, 172, 196, 255),
          (128, 140, 172, 255), (96, 108, 148, 255)]   # overcast daylight
LAMP = [(255, 236, 176, 255), (255, 210, 132, 255), (238, 158, 120, 255),
        (196, 110, 140, 255), (128, 72, 132, 255)]

WIN = room.bbox("W")
FR = room.FLOOR_ROW

# whole-tile light: a soft lamp pool at the bedside, cool window fringe
room.lit_cells = set()
room.fringe_cells = {(c, WIN[3]) for c in range(WIN[0], WIN[2] + 1)}
room.shadow_rows = (room.bbox("#")[3] - 1,)

room.paint_terrain()

# a panelled lintel over the surgery door on the UPPER canvas (Basil ducks
# under it) — the interior's required walk-behind art. Confined to the door
# cells (terrain "door") so it doesn't fail the ridge-cap lint on the
# flanking floor.
_dx0, _dy0, _dxw, _dyh = room.px(room.bbox("-"))
_dx1 = _dx0 + _dxw - 1
room.ov.rect(_dx0, _dy0, _dx1, _dy0 + 1, TIMBER[2])
room.ov.rect(_dx0, _dy0, _dx1, _dy0, TIMBER[1])
room.ov.rect(_dx0, _dy0 + 2, _dx1, _dy0 + 2, TIMBER[4])

# props — the bed is baked whole (Kitty sits in it as a spawned sprite; no
# under-covers walk here), the tonic shelf, window, chair, picture, plant, rug
room.place("g", rug(32, 48, RUGB, (232, 196, 158, 255)))
room.place("Bb", bed(64, 48, BLANK, LINEN))
room.place("W", window(32, 32, GLASSD, sun=False, flasks=False, salt=35))
room.place("F", flask_shelf(16, 32))
room.place("p", framed_picture(32, 16, GLASSD, salt=45))
room.place("P", potted_plant(16, 32), shadow_h=2)
room.bake_shadow("h", 2)
room.emit_prop("Chair", "h", sprite_img(chair(), 16, 16))


def _glow(img):
    # a warm reading lamp at the bedside — the one point of warmth
    bx0, by0, bxw, byh = room.px(room.bbox("Bb"))
    cx = bx0 + bxw - 6
    cy = by0 + byh + 4
    for r in range(30, 0, -1):
        a = int(30 * (r / 30.0))
        img.rect(cx - r, cy - r // 2, cx + r, cy + r // 2, (255, 214, 150, max(0, 30 - a) // 3 + 6))
    # cool window daylight
    wx0, wy0, wxw, wyh = room.px(WIN)
    img.rect(wx0 + 3, wy0 + 6, wx0 + wxw - 4, wy0 + wyh + T, (210, 224, 236, 22))


room.write_glow(_glow)
room.finish()
