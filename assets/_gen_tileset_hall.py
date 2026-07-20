#!/usr/bin/env python3
"""The Alembic Academy lecture hall — a thin room CONFIG (Prologue B).

Terrain/compose/light/output live in assets/_interior.py; furniture in
assets/_interior_props.py. This picks the `hall` palette (plum panelling /
rose floor / chalk-mint accent — already in _palette.py SCENES), declares the
tall-window light pools, places the chalkboard + flanking windows + wall
dressing, emits the y-sorted lectern and the tiered benches (counter-walk),
and writes a cool ward-light glow. The scene of the naming.

Re-run: python3 assets/_gen_tileset_hall.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _palette import ramp
from _tilekit import sprite_img
from _interior import Room, weave_px, TIMBER, BRASS, T
from _interior_props import (window, rug, framed_picture, potted_plant,
                             chalkboard, lectern, bench, desk, stage_front,
                             curtain_leg)

# rose floor lit toward a soft chalk-mint (the board's ward-light spills onto
# the front of the hall)
room = Room("hall", "hall", weave_px, (150, 240, 214), floor_chars=".g",
            lit_blend=0.40)

CHALK = [(214, 246, 236, 255), (150, 240, 214, 255),
         (96, 196, 176, 255), (60, 140, 128, 255)]     # chalk-mint ramp
RUGB = ramp((92, 52, 108), "violet", 6)                # deep plum dais runner
CURT = ramp((152, 38, 54), "violet", 5)                # theater-red curtain
GLASSD = [(206, 232, 240, 255), (170, 206, 224, 255), (150, 176, 206, 255),
          (120, 140, 178, 255), (86, 100, 148, 255)]   # cool daylit glass

BOARD = room.bbox("Q")
LECT = room.bbox("Ll")                 # the full footprint incl. walkable corners
FR = room.FLOOR_ROW

# whole-tile light: the STAGE's whole tuck row is lit (the 2026-07-18 college
# restage — the raised platform reads brighter than the house; the fringe
# dither reads as a harsh checkerboard on the dark rose floor at this
# palette, so skip it — the additive glow carries the soft edge instead)
room.lit_cells = {(c, FR) for c in range(4, 19)}
room.fringe_cells = set()
room.shadow_rows = (room.bbox("#")[3] - 1,)

room.paint_terrain()


def _door_lintel():
    """A panelled lintel over the south doors on the UPPER canvas — Basil ducks
    under it as he enters (and, at the end, is chased back out). Gives the hall
    its required walk-behind art, and reads as the grand double doorway."""
    # confined to the door cells (terrain "door" — exempt from the ridge-cap
    # lint); overhanging onto the flanking floor cells would fail it
    dx0, dy0, dxw, _dyh = room.px(room.bbox("-"))
    dx1 = dx0 + dxw - 1
    ov = room.ov
    ov.rect(dx0, dy0, dx1, dy0 + 1, TIMBER[2])
    ov.rect(dx0, dy0, dx1, dy0, TIMBER[1])
    ov.rect(dx0, dy0 + 2, dx1, dy0 + 3, TIMBER[4])
    ov.put(dx0, dy0 + 1, BRASS[2])                  # small keystone bosses
    ov.put(dx1, dy0 + 1, BRASS[2])


_door_lintel()

# ---- props at their map footprints (W and p appear on BOTH flanks -> _each) --------
room.place("Q", chalkboard(96, 32, CHALK))
room.place_each("W", window(48, 32, GLASSD, sun=True, flasks=False, salt=34))
room.place_each("p", framed_picture(16, 16, GLASSD, salt=44))
room.place("P", potted_plant(16, 32), shadow_h=2)
# the dais runner spans the g bbox INCLUDING the lectern cells between the
# flanks (96px, not 80 — an 80px rug left the right flank cell bare floor)
room.place("g", rug(96, 16, RUGB, (198, 150, 96, 255)))

# free-standing (Tier 3, y-sorted): the lectern a body rounds, and the four
# tiered benches (counter-walk — the E top row is walkable, so a seated NPC's
# legs tuck under the y-sorted seat; only the B bottom row is solid)
room.bake_shadow("Ll", 3)
room.emit_prop("Lectern", "Ll", sprite_img(lectern(64, 32), 64, 32))
room.bake_shadow("BE", 3, each=True)   # four benches — never the merged bbox
room.emit_prop("Bench", "BE", sprite_img(bench(80, 32), 80, 32), each=True)
# the judging panel's long desk on the stage's EAST flank (stage left —
# the west wing stays clear for Basil's stage-right entrance): a one-row
# solid footprint, the desktop plane rising into open row 3 where the four
# professors stand — their legs tuck behind it (the desk() entity idiom);
# the lamp flame burns chalk-mint, the Academy's ward-light
room.bake_shadow("J", 3)
room.emit_prop("PanelDesk", "J", sprite_img(desk(96, 32, CHALK), 96, 32))
# the stage apron: the riser face closing the platform's south edge (the
# college restage) — one full-width y-sorted entity over the solid D row,
# opaque across its footprint (the T3 coverage rule)
room.bake_shadow("D", 3)
room.emit_prop("StageFront", "D", sprite_img(stage_front(272, 32), 272, 32))
# the WEST CURTAIN LEG (the 2026-07-18 curtain pass): a proscenium-height
# drape on its one solid c cell beside the wing — y-sorted, so a body on
# the tuck row hides BEHIND it (the walk-on/flee "behind the curtain"
# read). No bake_shadow: its contact row is covered by the opaque
# StageFront entity, so a baked band would only split dais tiles for
# pixels nobody ever sees.
room.emit_prop("CurtainWest", "c", sprite_img(curtain_leg(24, 64, CURT), 24, 64))


def _stage_dressing():
    """Proscenium dressing baked into the FRONT-WALL art (Tier 1: every
    painted pixel sits over solid wall rows a body can never cross, so the
    lower layer is correct — and unlike upper-layer art it can never occlude
    a head on the tuck row). A scalloped theater-red VALANCE runs the full
    stage opening with a brass fringe tracing the lobes — drawn AFTER the
    place() calls so it hangs over the chalkboard/window top frames (the
    board's title, y>=38, stays legible) — and a slim gathered EAST DRAPE
    drops down the east wall column (the judges' desk runs to the wall, so
    no floor cell is free for a real leg there; the west leg is the
    y-sorted CurtainWest entity instead)."""
    bg = room.bg
    x0, x1 = 3 * T, 20 * T - 1                       # the stage opening
    bg.rect(x0, 16, x1, 26, CURT[1])                 # the straight band
    bg.rect(x0, 16, x1, 17, CURT[0])                 # lit top roll
    bg.rect(x0, 26, x1, 26, CURT[3])
    for fx in range(x0 + 4, x1, 8):                  # gather ticks
        bg.rect(fx, 19, fx, 25, CURT[3 if (fx // 8) % 2 else 2])
    lobe = (1, 3, 5, 6, 7, 7, 8, 8, 8, 8, 7, 7, 6, 5, 3, 1)
    for sx in range(x0, x1, 16):                     # scallop lobes + fringe
        for dx in range(16):
            x = sx + dx
            if x > x1:
                break
            bg.rect(x, 27, x, 27 + lobe[dx], CURT[2])
            bg.put(x, 27 + lobe[dx], CURT[4])        # shaded under-curl
            bg.put(x, 28 + lobe[dx], BRASS[2])       # the fringe line
    ex0, ex1 = 20 * T + 1, 20 * T + 13               # the east drape strip
    fold = (1, 2, 1, 3, 2, 1, 2, 3, 1, 2, 1, 3, 2)
    for x in range(ex0, ex1 + 1):
        bg.rect(x, 18, x, 71, CURT[fold[(x - ex0) % len(fold)]])
    bg.rect(ex0, 16, ex1, 17, CURT[0])               # lit top roll
    bg.rect(ex0, 72, ex1, 73, CURT[3])               # hem
    bg.rect(ex0, 74, ex1, 75, CURT[4])


_stage_dressing()


def _glow(img):
    # cool ward-light washing down off the chalkboard onto the dais
    bx0, by0, bxw, _byh = room.px(BOARD)
    bx1 = bx0 + bxw - 1
    bottom = (FR + 2) * T
    for y in range(by0 + 6, bottom):
        a = int(40 * (1.0 - (y - by0 - 6) / float(bottom - by0 - 6)))
        img.rect(bx0 - 4, y, bx1 + 4, y, (150, 240, 214) + (a,))
    # a soft daylight shaft under every window cell (both flanks)
    m = room.m
    for ty in range(m.rows_n):
        for tx in range(m.cols):
            if m.at(tx, ty) == "W":
                x0, y0 = tx * T, ty * T
                img.rect(x0 + 1, y0 + 6, x0 + T - 2, y0 + 3 * T, (206, 230, 244, 24))


room.write_glow(_glow)
room.south_lift()          # mask the south wall's feet-sink sliver (upper band)
room.finish()
