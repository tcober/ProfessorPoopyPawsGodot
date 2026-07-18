#!/usr/bin/env python3
"""The sunset bluff, tiled — a thin CONFIG on the shared overworld tile kit.

The bluff map (assets/maps/bluff.txt) rides assets/_overworld_tiles.py's
OverWorld driver directly: forest windbreak border, gilded grass headland
with flower drifts, and the sea wrapping the point. This file only picks
the `bluff` sunset palette (assets/_palette.py) and stamps the 2-row cliff
band from the town's 16x32 face columns (assets/_town_props.town_cliff —
the same three-salted-variants recipe as the Academy terrace), so the
headland visibly DROPS into the evening water. No glow overlay: the scene's
CanvasModulate carries the hour (scene/bluff.gd tints the call phases
cooler over this one warm painting — the tint law).

Re-run: python3 assets/_gen_tileset_bluff.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_tiles import OverWorld, T
from _town_props import town_cliff

bl = OverWorld("bluff", "bluff")
bl.paint_terrain()

# ---- the cliff band: one 16x32 face column per map column, stamped at the
# TOP C cell (the column art spans both band rows), hash-picked from three
# salted variants so the face varies while cells still dedupe -----------------------
cliffs = [town_cliff(bl.ROCK, bl.GRASS, salt=s) for s in (291, 293, 297)]
for ty in range(bl.m.rows_n):
    for tx in range(bl.m.cols):
        if bl.m.at(tx, ty) == "C" and bl.m.at(tx, ty - 1) != "C":
            bl.bg.blit_cell(cliffs[h2(tx, ty, 51) % 3], tx * T, ty * T)

bl.finish()
