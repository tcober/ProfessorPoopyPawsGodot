#!/usr/bin/env python3
"""Alembic Town, FESTIVAL ERA — Prologue A's bright-era town, a thin CONFIG on
the shared overworld tile kit (the same recipe as _gen_tileset_town.py, which
paints the drained present).

Same buildings, same salts, same cliff/tree stamping — the map grid is a byte
copy of town.txt (see maps/town_fest.txt) so every lane is recognizable when
the drained present arrives; only the PALETTE (town_fest: spring grass, cream
plaster, festival magenta) and the glow differ. The festival glow is daylight
magic, not candlelight: the Academy's rose window burns mint (magic is ALIVE
here), the fountain shimmers, the lamps stay dark.

Re-run: python3 assets/_gen_tileset_town_fest.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_tiles import OverWorld, T
from _tilekit import COPPER, GLOW_WARM as WARM, GLOW_MINT as MINTG, sprite_img
from _town_props import (town_home, town_cottage, town_academy, town_well,
                         town_lamp, town_stall, town_shop, town_inn,
                         town_fountain, town_stairs, town_cliff, town_tree)

tn = OverWorld("town_fest", "town_fest")
_blob = OverWorld.glow_blob

ROOFB = tn.mat("roof_blue")
ROOFG = tn.mat("roof_green")
ROOFR = tn.mat("bridge")               # rosewood — the inn's roof
PLAST = tn.mat("plaster")
STONE = tn.ROCK

tn.paint_terrain()

# ---- the same buildings as the drained town (shared builders + salts) ---------------
lo, up = town_home(ROOFB, PLAST)
tn.place_split("hH3", lo, up)
lo, up = town_cottage(ROOFG, PLAST, salt=211)
tn.place_split("q14", lo, up)
lo, up = town_cottage(ROOFB, PLAST, salt=211)
tn.place_split("w25", lo, up)
lo, up = town_academy(ROOFB, STONE)
tn.place_split("kK6", lo, up)
lo, up = town_shop(COPPER, PLAST, sign="sword", wares="arms", salt=251)
tn.place_split("xX7", lo, up)
lo, up = town_shop(ROOFG, PLAST, sign="flask", wares="tonics", salt=251)
tn.place_split("pP8", lo, up)
lo, up = town_inn(ROOFR, PLAST, salt=261)
tn.place_split("nN9", lo, up)
tn.place("S", town_stairs(STONE))
tn.bake_shadow("oO", 3)
tn.emit_prop("Fountain", "oO", sprite_img(town_fountain(STONE), 48, 48))
tn.emit_prop("Well", "uU", sprite_img(town_well(STONE), 32, 32))
tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(), 16, 32), each=True)
tn.emit_prop("Stall", "m", sprite_img(town_stall(), 48, 32))

# ---- terrace cliff band + walk-behind trees (identical stamping) --------------------
cliffs = [town_cliff(tn.ROCK, tn.GRASS, salt=s) for s in (291, 293, 297)]
for ty in range(tn.m.rows_n):
    for tx in range(tn.m.cols):
        if tn.m.at(tx, ty) == "C" and tn.m.at(tx, ty - 1) != "C":
            tn.bg.blit_cell(cliffs[h2(tx, ty, 51) % 3], tx * T, ty * T)

trees = [town_tree(tn.FOREST, tn.TRUNK, tn.GRASS, salt=s) for s in (301, 307, 311)]
_todo = {(x, y) for y in range(tn.m.rows_n) for x in range(tn.m.cols)
         if tn.m.at(x, y) in "Tt^"}
while _todo:
    comp = [_todo.pop()]
    i = 0
    while i < len(comp):
        cx, cy = comp[i]
        i += 1
        for nb in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
            if nb in _todo:
                _todo.remove(nb)
                comp.append(nb)
    ox, oy = min(c[0] for c in comp), min(c[1] for c in comp)
    lo, up = trees[h2(ox, oy, 59) % 3]
    tn.bg.blit_cell(lo, ox * T, oy * T)
    tn.ov.blit_cell(up, ox * T, oy * T)


# ---- festival glow: living magic by daylight -----------------------------------------
def _glow(img):
    kx, ky = tn.bbox("K")[0] * T, tn.bbox("K")[1] * T
    _blob(img, kx + 79, ky + 14, 18, MINTG, 66)            # the rose window AWAKE
    _blob(img, kx + 40, ky + 20, 8, MINTG, 40)             # ward-light in a hall window
    _blob(img, kx + 120, ky + 20, 8, MINTG, 40)
    ox_, oy_ = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox_ + 24, oy_ + 24, 13, MINTG, 52)          # the fountain's charm shimmer
    hx, hy = tn.bbox("H")[0] * T, tn.bbox("H")[1] * T
    _blob(img, hx + 55, hy + 22, 10, WARM, 44)             # Basil's open doorway


tn.write_glow(_glow)
tn.finish()
