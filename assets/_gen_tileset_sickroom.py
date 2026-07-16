#!/usr/bin/env python3
"""THE DOCTOR'S OFFICE — a thin room CONFIG (Prologue B "the verdict").

Terrain/compose/light/output in assets/_interior.py; furniture in
assets/_interior_props.py. Reworked 2026-07-16 to the loft-bedroom recipe: a
SMALL dense diorama (8-tile interior floating in void — the front room of
the east neighbor cottage in town), every wall stretch occupied and the
floor packed. Picks the `sickroom` palette (pale lavender walls / cool slate
floor, a warm lamp against the chill); clinical pale-teal bedding (the old
blue-lavender quilt read as a kid's bedroom, not a ward); tonic flasks on
the window sill; the brass drip-stand, the folding ward screen and the
doctor's desk are y-sorted entities. Kitty sits up in the bed as a separate
NPC sprite (npc_kitty_bed) the scene spawns at the pillow — this file only
bakes the bed she lies in.

Re-run: python3 assets/_gen_tileset_sickroom.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _palette import ramp
from _tilekit import sprite_img
from _interior import Room, weave_px, TIMBER, BRASS, T
from _interior_props import (window, rug, bed, flask_shelf, chair,
                             potted_plant, wall_clock, desk, privacy_screen,
                             drip_stand)

room = Room("sickroom", "sickroom", weave_px, (255, 224, 176), floor_chars=".g",
            lit_blend=0.30)

LINEN = ramp((224, 220, 236), "violet", 4)             # gown / screen linen
BEDDING = ramp((192, 214, 210), "violet", 4)           # clinical pale teal
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

# a panelled lintel over the door on the UPPER canvas (Basil ducks under it)
# — the interior's required walk-behind art. Confined to the door cells
# (terrain "door") so it doesn't fail the ridge-cap lint on flanking floor.
_dx0, _dy0, _dxw, _dyh = room.px(room.bbox("-"))
_dx1 = _dx0 + _dxw - 1
room.ov.rect(_dx0, _dy0, _dx1, _dy0 + 1, TIMBER[2])
room.ov.rect(_dx0, _dy0, _dx1, _dy0, TIMBER[1])
room.ov.rect(_dx0, _dy0 + 2, _dx1, _dy0 + 2, TIMBER[4])

# ---- baked props (Tier 1: wall-flush, nobody stands behind them) -------------------
room.place("g", rug(32, 32, RUGB, (232, 196, 158, 255)))
room.place("Bb", bed(64, 48, BEDDING, LINEN))
room.place("W", window(32, 32, GLASSD, sun=False, flasks=True, salt=35))
room.place("F", flask_shelf(16, 32))
room.place("o", wall_clock())

# ---- y-sorted entities (Tier 3: bodies pass both sides / tuck behind) --------------
# the brass drip-stand at the pillow, its tube arcing toward the bed
room.bake_shadow("i", 2)
room.emit_prop("Drip", "i", sprite_img(drip_stand(16, 44), 16, 44))
# the folding ward screen dividing the bed from the office corner
room.bake_shadow("S", 2)
room.emit_prop("Screen", "S", sprite_img(privacy_screen(32, 40, LINEN), 32, 40))
# the doctor's own desk by the door — stand behind it and it hides your legs
room.bake_shadow("d", 2)
room.emit_prop("Desk", "d", sprite_img(desk(48, 32, LAMP), 48, 32))
room.bake_shadow("P", 2, each=True)
room.place_each("P", potted_plant(16, 32))
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
    # cool window daylight — a soft standing shaft down past the drip-stand
    wx0, wy0, wxw, wyh = room.px(WIN)
    img.rect(wx0 + 3, wy0 + 6, wx0 + wxw - 4, wy0 + wyh + 2 * T, (210, 224, 236, 30))
    # the drip flask's tonic, faintly ward-lit
    ix0, iy0, _, _ = room.px(room.bbox("i"))
    Room.glow_blob(img, ix0 + 3, iy0 - 24, 6, (150, 240, 214), 36)
    # the desk lamp's little flame
    dx0_, dy0_, dxw_, _ = room.px(room.bbox("d"))
    Room.glow_blob(img, dx0_ + dxw_ - 6, dy0_ - 12, 8, (255, 214, 150), 40)


room.write_glow(_glow)
room.finish()
