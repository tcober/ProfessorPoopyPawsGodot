#!/usr/bin/env python3
"""The overworld continent — a thin CONFIG on the overworld tile kit.

Terrain fabrics, the neighbor-stamp autotile transitions (45-degree corner
cuts included) and the dedupe plumbing live in assets/_overworld_tiles.py;
the landmark compositions come from assets/_overworld_props.py: Alembic
Town's cluster ICON (dense roofs + Academy keep + the steamworks' plume),
the Capital's mountain-hold castle, the wastes' crystal obelisk + outcrops,
and the scattered plains trees. This file only picks the prop palette,
places the compositions at their map footprints, and writes the additive
night-glow overlay (lit windows, the rose window, firebox coals, crystals).

Re-run: python3 assets/_gen_tileset_overworld.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _overworld_tiles import OverWorld, T
from _tilekit import GLOW_WARM as WARM, GLOW_MINT as MINTG
from _overworld_props import (town_cluster, lone_tree, castle, obelisk,
                              crystal_outcrop, giant_tree, mountain_peak)

ow = OverWorld("overworld", "overworld")
_blob = OverWorld.glow_blob            # shared radial glow dab (see TileScene)

ROOFB = ow.mat("roof_blue")
ROOFG = ow.mat("roof_green")
PLAST = ow.mat("plaster")
STONE = ow.ROCK                        # town masonry = the scene's violet slate
CRYST = (196, 120, 255)

ow.paint_terrain()

# ---- the landmark compositions at their map footprints ------------------------------
ow.place("T", town_cluster(ROOFG, ROOFB, PLAST, STONE))
ow.place("C", castle(ROOFB, ow.ROCK))
ow.place("V", mountain_peak(ow.ROCK, ow.SNOW))
# the elder tree splits: the whole crown rides the upper layer over the
# walkable G cells (duck in from the north or west, hidden under the canopy)
lo, up = giant_tree(ow.FOREST, ow.TRUNK, ow.GRASS)
ow.place_split("gG", lo, up)
ow.place("O", obelisk())
ow.place_each("K", crystal_outcrop())
ow.place_each("t", lone_tree(ow.FOREST))


# ---- additive glow: lit windows, coals, and the drained crystals ---------------------
def _glow(img):
    tx, ty = ow.bbox("T")[0] * T, ow.bbox("T")[1] * T
    _blob(img, tx + 61, ty + 34, 4, WARM, 50)              # B-rank lit door
    _blob(img, tx + 57, ty + 33, 3, WARM, 40)              # its window
    _blob(img, tx + 72, ty + 46, 4, WARM, 50)              # D-rank lit door
    _blob(img, tx + 68, ty + 45, 3, WARM, 40)              # its window
    _blob(img, tx + 39, ty + 58, 4, WARM, 52)              # F-rank lit door
    _blob(img, tx + 35, ty + 57, 3, WARM, 42)              # its window
    _blob(img, tx + 40, ty + 71, 4, WARM, 52)              # H-rank lit door
    _blob(img, tx + 36, ty + 70, 3, WARM, 42)              # its window
    _blob(img, tx + 106, ty + 58, 6, WARM, 56)             # the firebox coals
    _blob(img, tx + 114, ty + 42, 3, MINTG, 50)            # the boiler gauge
    _blob(img, tx + 23, ty + 40, 5, MINTG, 46)             # the rose window
    cx0, cy0 = ow.bbox("C")[0] * T, ow.bbox("C")[1] * T
    _blob(img, cx0 + 45, cy0 + 36, 3, WARM, 50)            # keep windows
    _blob(img, cx0 + 51, cy0 + 36, 3, WARM, 46)
    _blob(img, cx0 + 44, cy0 + 58, 3, WARM, 42)            # gate lamps
    _blob(img, cx0 + 52, cy0 + 58, 3, WARM, 42)
    ox0, oy0 = ow.bbox("O")[0] * T, ow.bbox("O")[1] * T
    _blob(img, ox0 + 24, oy0 + 48, 11, CRYST, 56)          # the crystal burst
    _blob(img, ox0 + 40, oy0 + 9, 4, CRYST, 66)            # the floating shard
    Ks = {(x, y) for y in range(ow.m.rows_n) for x in range(ow.m.cols)
          if ow.m.at(x, y) == "K"}
    for (x, y) in Ks:                                      # outcrop glow (one
        if (x - 1, y) not in Ks and (x, y - 1) not in Ks:  # per 2x2 block)
            _blob(img, x * T + 15, y * T + 13, 9, CRYST, 50)
    for (x, y) in ow.crystal_cells:                        # the hash shards
        _blob(img, x * T + 7, y * T + 9, 8, CRYST, 46)


ow.write_glow(_glow)
ow.finish()
