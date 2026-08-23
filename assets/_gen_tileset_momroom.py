#!/usr/bin/env python3
"""MOM'S BEDROOM — a thin room CONFIG (Prologue A0 "The Fever").

Terrain/compose/light/output live in assets/_interior.py; furniture in
assets/_interior_props.py. The sickroom recipe — a SMALL dense diorama
(8-tile interior floating in void), every wall stretch occupied — but a
HOME, not a ward: the family timber walls over a dusty-rose weave, the
warm quilt, Sage's chair pulled up to the bedside, and the nightstand
candle that is the room's one light against an overcast day. Mom lies in
the bed as a separate NPC sprite (npc_mom_bed_gen) the scene spawns at
the pillow — this file only bakes the bed she lies in.

Re-run: python3 assets/_gen_tileset_momroom.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _palette import ramp
from _tilekit import sprite_img
from _interior import Room, weave_px, T
from _interior_props import (window, rug, bed, flask_shelf, chair,
                             potted_plant, wall_clock, nightstand,
                             interior_door)

room = Room("momroom", "momroom", weave_px, (255, 214, 150), floor_chars=".g",
            lit_blend=0.34)

LINEN = ramp((236, 228, 240), "violet", 4)             # pillow / sheet linen
QUILT = ramp((196, 118, 84), "violet", 4)              # a worn russet quilt —
                                                       # warm, older than Basil
RUGB = ramp((168, 108, 120), "violet", 6)              # dusty-rose rug
GREYD = [(214, 220, 230, 255), (186, 196, 212, 255), (154, 166, 192, 255),
         (120, 132, 168, 255), (88, 98, 142, 255)]     # overcast day glass
GLOWC = (255, 214, 150)

WIN = room.bbox("W")
BED = room.bbox("Bb")
NST = room.bbox("t")
FR = room.FLOOR_ROW

# whole-tile light: the candle's pool at the bed's west side, a cool window
# fringe — the room is dim on purpose, and the one warmth is at her pillow
room.lit_cells = {(NST[0], FR + 1)}
room.fringe_cells = {(c, WIN[3] + 1) for c in range(WIN[0], WIN[2] + 1)} \
        | {(NST[0] - 1, FR + 1)}
room.shadow_rows = (room.bbox("#")[3] - 1,)

room.paint_terrain()

# MOM'S DOOR from her side of it: the great room's west-wall plank leaf,
# mirrored onto this room's EAST wall (the two doors are one door)
room.place("-", interior_door(16, 32, room.WALLR, flip=True))

# ---- baked props (Tier 1: wall-flush, nobody stands behind them) -------------------
room.place("g", rug(32, 32, RUGB, (232, 196, 158, 255)))
room.place("Bb", bed(64, 48, QUILT, LINEN))
room.place("W", window(32, 32, GREYD, sun=False, flasks=False, salt=36))
room.place("k", flask_shelf(16, 32))                   # tonic cups and jars
room.place("o", wall_clock())

# ---- y-sorted entities (Tier 3: bodies pass both sides / tuck behind) --------------
# Sage's chair, pulled right up to the west bedside — she has been in it all
# day, and the chair says so
room.bake_shadow("h", 2)
room.emit_prop("Chair", "h", sprite_img(chair(), 16, 16))
# the nightstand and its candle — the room's one light
room.bake_shadow("t", 2)
room.emit_prop("Nightstand", "t", sprite_img(nightstand(16, 22), 16, 22))
room.place("P", potted_plant(16, 32), shadow_h=2)


def _glow(img):
    # the candle's warm pool over the pillow end — the one point of warmth
    nx0, ny0, _, _ = room.px(NST)
    Room.glow_blob(img, nx0 + 7, ny0 - 8, 16, GLOWC, 52)
    Room.glow_blob(img, nx0 + 7, ny0 + 10, 22, GLOWC, 26)
    # cold overcast daylight — a soft standing shaft below the window
    wx0, wy0, wxw, wyh = room.px(WIN)
    img.rect(wx0 + 3, wy0 + 6, wx0 + wxw - 4, wy0 + wyh + 2 * T, (206, 218, 234, 26))


room.write_glow(_glow)
room.south_lift()          # mask the south wall's feet-sink sliver (upper band)
room.finish()
