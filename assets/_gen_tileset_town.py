#!/usr/bin/env python3
"""Alembic Town, walkable — a thin CONFIG on the shared overworld tile kit.

The town map (assets/maps/town.txt, 56x34) rides assets/_overworld_tiles.py's
OverWorld driver directly: the tree border is the forest class, lanes are the
wobbly trail painter, yards are the fence class, the SE pond is sea+beach and
the stream a river with one bridge cell. This file picks the palette,
place_split()s the zone-scale facades from assets/_town_props.py (roofs to
the upper layer, so the player walks behind rooflines), stamps the terrace's
cliff columns and the walk-behind trees from salted repeating variants (the
meadow-boulder reuse pattern), and writes the additive night-glow.

Re-run: python3 assets/_gen_tileset_town.py [--preview out.png]
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

tn = OverWorld("town", "town")
_blob = OverWorld.glow_blob            # shared radial glow dab (see TileScene)

ROOFB = tn.mat("roof_blue")
ROOFG = tn.mat("roof_green")
ROOFR = tn.mat("bridge")               # rosewood — the inn's roof
PLAST = tn.mat("plaster")
STONE = tn.ROCK                        # town masonry = the scene's violet slate

tn.paint_terrain()

# ---- the buildings at their map footprints (roofs ride the upper layer).
# Reuse contract: the two shops share one salt (only roof/sign/wares differ)
# and the two cottages share one salt (only the roof differs), so their plain
# facade cells dedupe to the same atlas tiles. ---------------------------------------
# (each building's char set includes its solid ridge digit — the bbox must
# still start at the roof's top row or the facade blits one row low)
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
# street furniture is Tier 3: free-standing (bodies pass both north and
# south of it), so the art rides y-sorted World entities spawned from
# town_props.txt (scene/prop_spawner.gd); the map chars keep the solid
# collision and anchor the glow dabs
tn.bake_shadow("oO", 3)
tn.emit_prop("Fountain", "oO", sprite_img(town_fountain(STONE), 48, 48))
tn.emit_prop("Well", "uU", sprite_img(town_well(STONE), 32, 32))
tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(), 16, 32), each=True)
tn.emit_prop("Stall", "m", sprite_img(town_stall(), 48, 32))

# ---- the terrace cliff band: one 16x32 face column per map column, hash-
# picked from three salted variants (the meadow-boulder per-cell pattern —
# opaque, unoutlined, so ~40 columns dedupe to a handful of tiles) -------------------
cliffs = [town_cliff(tn.ROCK, tn.GRASS, salt=s) for s in (291, 293, 297)]
for ty in range(tn.m.rows_n):
    for tx in range(tn.m.cols):
        if tn.m.at(tx, ty) == "C" and tn.m.at(tx, ty - 1) != "C":
            tn.bg.blit_cell(cliffs[h2(tx, ty, 51) % 3], tx * T, ty * T)

# ---- walk-behind trees: one (lower, upper) pair per connected {^,T,t}
# component — canopy over entities (top row = solid ridge), opaque trunk
# row under them ---------------------------------------------------------------------
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


# ---- additive glow: the sleeping town's little lights ------------------------------
def _glow(img):
    hx, hy = tn.bbox("H")[0] * T, tn.bbox("H")[1] * T      # facade rows origin
    _blob(img, hx + 55, hy + 22, 14, WARM, 66)             # the open doorway
    _blob(img, hx + 15, hy + 17, 9, WARM, 54)              # warm windows
    _blob(img, hx + 80, hy + 17, 9, WARM, 54)
    kx, ky = tn.bbox("K")[0] * T, tn.bbox("K")[1] * T
    _blob(img, kx + 79, ky + 14, 16, MINTG, 46)            # the rose window
    nx, ny = tn.bbox("N")[0] * T, tn.bbox("N")[1] * T      # the inn, wide awake
    for wx_ in (20, 50, 122):                              # upper windows
        _blob(img, nx + wx_, ny + 10, 8, WARM, 50)
    for wx_ in (30, 110):                                  # lower windows
        _blob(img, nx + wx_, ny + 33, 9, WARM, 54)
    _blob(img, nx + 72, ny + 23, 7, WARM, 46)              # the transom
    _blob(img, nx + 56, ny + 31, 6, WARM, 44)              # the wall lantern
    ox_, oy_ = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox_ + 24, oy_ + 29, 10, MINTG, 40)          # fountain shimmer
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            # each lamp component's TOP cell (usually the walkable L head;
            # the inn-nook lamp keeps a solid l top — the goose chase wedges
            # in a walkable pocket there)
            if m.at(x, y) in "lL" and m.at(x, y - 1) not in "lL":
                _blob(img, x * T + 7, y * T + 4, 11, MINTG, 58)


tn.write_glow(_glow)
tn.finish()
