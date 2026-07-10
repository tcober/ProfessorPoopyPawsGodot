#!/usr/bin/env python3
"""Basil's loft bedroom — a thin room CONFIG on the interior kit.

Terrain, compose, light dispatch and output plumbing live in
assets/_interior.py; the furniture comes from assets/_interior_props.py.
This file only picks the palette, declares the light pools and the room's
odd cells (loft rail + descending stairs), places the props at their map
footprints, and writes the two runtime overlays (dawn beam glow + curtain
frames for the open/close mechanic).

Re-run: python3 assets/_gen_tileset_house.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img
from _palette import ramp
from _interior import (Room, Canvas, weave_px, TIMBER, OUTDIR, T)
from _interior_props import (window, window_geom, sill_flasks, rug, bed_parts,
                             desk, bookshelf, corkboard, chair, framed_picture)

room = Room("house", "bedroom", weave_px, (255, 218, 148), lit_blend=0.75)

LINENR = ramp(room.mats["linen"], "violet", 4)
QUILT = ramp((226, 76, 132), "violet", 4)
CURT = ramp((162, 96, 122), "violet", 4)
RUGB = ramp((110, 86, 152), "violet", 6)           # rug base: readable violet
SPINES = [(214, 84, 118, 255), (96, 120, 208, 255), (98, 172, 138, 255),
          (238, 172, 96, 255), (166, 100, 202, 255), (82, 164, 172, 255)]
DAWN = [(255, 232, 160, 255), (255, 186, 122, 255), (244, 126, 128, 255),
        (198, 84, 152, 255), (122, 62, 148, 255)]
BEAM = (255, 216, 160)
STEPS = [((78, 54, 82, 255), (54, 38, 66, 255)),   # descending-away treads
         ((46, 34, 62, 255), (30, 22, 48, 255)),
         ((32, 24, 50, 255), (20, 15, 40, 255)),
         ((20, 16, 38, 255), (12, 10, 26, 255))]
TREADS = [(TIMBER[1], TIMBER[3])] + STEPS          # brightest at the room edge

WIN = room.bbox("W")
RAIL_ROW = room.bbox("R")[1]
FR = room.FLOOR_ROW
GC = (WIN[0] + WIN[2]) // 2

# whole-tile dawn pool under the (now 3x3) window
room.lit_cells = {(c, FR) for c in range(WIN[0], WIN[2] + 1)} | {(GC, FR + 1)}
room.fringe_cells = {(WIN[0], FR + 1), (WIN[2], FR + 1), (GC, FR + 2)}
room.shadow_rows = (FR, RAIL_ROW - 1)


def _rail(tx, ty):
    room.drop_cell(tx, ty, stair=False)
    newel = room.m.at(tx - 1, ty) != "R" or room.m.at(tx + 1, ty) != "R"
    room.rail_cell(tx, ty, newel)


def _stair_gap(tx, ty):
    room.drop_cell(tx, ty, stair=True)


def _steps(tx, ty):
    room.stair_cell(tx, ty, RAIL_ROW + 1, TREADS)


def _wall_rules(tx, ty):
    if ty > RAIL_ROW:                                  # stair jambs past the room
        room.jamb_cell(tx, ty, stair_char="-", void_backed=True)
        return True
    return False


room.paint_terrain(wall_rules=_wall_rules,
                   special={"R": _rail, "s": _stair_gap, "-": _steps})

# props at their map footprints
room.place("g", rug(32, 48, RUGB, QUILT[1]))
room.place("W", window(48, 48, DAWN, curt=CURT, gable=True, sun=True,
                       flasks=True))
room.place("C", corkboard(32, 32, QUILT))
room.place("p", framed_picture(16, 16, DAWN))
room.place("S", bookshelf(32, 48, SPINES))
# the bed splits for the under-the-covers read: headboard/pillow bake here,
# the quilt+footboard cover rides as a y-sorted scene entity (sheet below)
_bed_low, _bed_cover = bed_parts(32, 64, QUILT, LINENR)
room.place("bB", _bed_low, shadow_h=5)
# the desk is a y-sorted scene entity too (walk behind it, stand in front of
# it — no static-layer head clipping); only its contact shadow bakes
room.bake_shadow("d", 3)
room.place("h", chair(), shadow_h=2)


def _entity_sheets():
    """house_desk.png + house_bed_cover.png — furniture that lives in the
    scene's y-sorted World (house.gd positions them from the map bboxes)."""
    dsk = desk(48, 32, DAWN)
    img = Img(48, 32)
    img.blit_cell(dsk, 0, 0)
    img.save(os.path.join(OUTDIR, "house_desk.png"))
    cy0, cy1 = 24, 59                      # cover crop (bed_parts cover_span)
    img = Img(32, cy1 - cy0 + 1)
    for y in range(_bed_cover.n):
        for x in range(_bed_cover.n):
            p = _bed_cover.px[y][x]
            if p and cy0 <= y <= cy1:
                img.put(x, y - cy0, p)
    img.save(os.path.join(OUTDIR, "house_bed_cover.png"))


_entity_sheets()


# runtime overlays: additive dawn beam + the curtain frames -------------------------
def _glow(img):
    X, Y, XW, YH = room.px(WIN)
    g = window_geom(XW, YH, gable=True)
    gx0, gy0, gx1, gy1 = (X + g["glass"][0], Y + g["glass"][1],
                          X + g["glass"][2], Y + g["glass"][3])
    sill_y, floor_y = Y + g["sill_y"], FR * T
    img.rect(gx0, gy0, gx1, gy1, BEAM + (52,))          # halo over the glass
    for y in range(sill_y, floor_y + 3 * T):
        if y < floor_y:                                 # widening past the sill
            k = (y - sill_y) // 4 + 1
            x0, x1 = max(X, gx0 - 3 * k), min(X + XW - 1, gx1 + 3 * k)
            a = 62
        else:
            x0, x1 = X, X + XW - 1
            a = 62 if y < floor_y + T else (40 if y < floor_y + 2 * T else 24)
        img.rect(x0, y, x1, y, BEAM + (a,))


room.write_glow(_glow)


def _curtains():
    """house_curtains.png — closed/half frames over the window bay; the open
    tied-back drapes are baked in the window prop, so the scene hides this
    sprite once the toggle finishes. Sill flasks redraw IN FRONT."""
    X, Y, XW, YH = room.px(WIN)
    g = window_geom(XW, YH, gable=True)
    fx0, fy0, fx1, fy1 = g["frame"]
    sheet = Canvas(XW * 2, YH)
    for fi, cover in enumerate((19, 8)):               # panel width per frame
        ox = fi * XW
        for side in (0, 1):
            xa = ox + fx0 + 1 if side == 0 else ox + fx1 - cover
            for x in range(xa, xa + cover):
                u = (x - xa) if side == 0 else (xa + cover - 1 - x)
                for y in range(fy0 + 1, fy1):
                    c = CURT[0] if u == cover - 1 else \
                        (CURT[2] if u % 4 == 2 else CURT[1])
                    sheet.put(x, y, c)
            sheet.rect(xa, fy1 - 2, xa + cover - 1, fy1 - 1, CURT[3])
            sheet.rect(xa, fy0 + 1, xa + cover - 1, fy0 + 2, CURT[3])
        sill_flasks(sheet.put, sheet.rect,
                    [ox + fx for fx in g["flask_xs"]], g["sill_y"])
    sheet.save(os.path.join(OUTDIR, "house_curtains.png"))


_curtains()
room.finish()
