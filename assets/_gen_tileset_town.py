#!/usr/bin/env python3
"""Alembic Town, walkable — a thin CONFIG on the shared overworld tile kit.

The town map (assets/maps/town.txt) rides assets/_overworld_tiles.py's
OverWorld driver directly: the hedge border is the forest class, lanes are
the wobbly trail painter, yards are the fence class. This file only picks
the palette, place_split()s the zone-scale facades from
assets/_town_props.py (roofs to the upper layer, so the player walks behind
rooflines), and writes the additive night-glow (Basil's doorway and windows,
the lamp mantle, the Academy's rose window).

Re-run: python3 assets/_gen_tileset_town.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _overworld_tiles import OverWorld, T
from _town_props import (town_home, town_cottage, town_academy, town_well,
                         town_lamp, town_stall)

tn = OverWorld("town", "town")

ROOFB = tn.mat("roof_blue")
ROOFG = tn.mat("roof_green")
PLAST = tn.mat("plaster")
STONE = tn.ROCK                        # town masonry = the scene's violet slate
WARM = (255, 200, 120)
MINTG = (150, 246, 190)

tn.paint_terrain()

# ---- the buildings at their map footprints (roofs ride the upper layer) -----------
lo, up = town_home(ROOFB, PLAST)
tn.place_split("hH", lo, up)
lo, up = town_cottage(ROOFG, PLAST, salt=211)
tn.place_split("q1", lo, up)
lo, up = town_cottage(ROOFB, PLAST, salt=217)
tn.place_split("w2", lo, up)
lo, up = town_academy(ROOFB, STONE)
tn.place_split("kK", lo, up)
tn.place("u", town_well(STONE))
tn.place_each("l", town_lamp())
tn.place("m", town_stall())


# ---- additive glow: the sleeping town's little lights ------------------------------
def _blob(img, cx, cy, r, color, a):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            q = (dx * dx + dy * dy) / float(r * r)
            if q <= 1.0:
                img.put(int(cx) + dx, int(cy) + dy,
                        color + (int(a * (1.0 - q)),))


def _glow(img):
    hx, hy = tn.bbox("H")[0] * T, tn.bbox("H")[1] * T      # facade rows origin
    _blob(img, hx + 55, hy + 22, 14, WARM, 66)             # the open doorway
    _blob(img, hx + 15, hy + 17, 9, WARM, 54)              # warm windows
    _blob(img, hx + 80, hy + 17, 9, WARM, 54)
    kx, ky = tn.bbox("K")[0] * T, tn.bbox("K")[1] * T
    _blob(img, kx + 79, ky + 14, 16, MINTG, 46)            # the rose window
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) == "l" and m.at(x, y - 1) != "l":
                _blob(img, x * T + 7, y * T + 4, 11, MINTG, 58)


tn.write_glow(_glow)
tn.finish()
