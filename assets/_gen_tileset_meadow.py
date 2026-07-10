#!/usr/bin/env python3
"""Whisker Meadow, tiled — a thin CONFIG on the shared overworld tile kit.

The meadow map (assets/maps/meadow.txt) rides assets/_overworld_tiles.py's
OverWorld driver directly: the treeline border is the forest class, the pond
is a sea blob with a wet-sand beach arc on its trail-facing W/S shore, the
trail is the wobbly road ribbon, flower drifts are the flowers fabric. This
file only picks the palette and stamps the boulder outcrops (one squat dome
per solid `r` cell, three salted variants) and the trailhead cairn from
assets/_meadow_props.py. No glow overlay: the meadow is a daylight scene.

Re-run: python3 assets/_gen_tileset_meadow.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_tiles import OverWorld, T
from _meadow_props import meadow_boulder, meadow_cairn

md = OverWorld("meadow", "meadow")
md.paint_terrain()

# ---- boulder outcrops: one dome per rock CELL (place_each would leave the
# multi-cell outcrops' extra solid cells bare = invisible walls). Hash-picked
# from three salted variants so clusters vary while cells still dedupe. -------------
variants = [meadow_boulder(md.ROCK, md.GRASS, salt=s) for s in (57, 61, 67)]
for ty in range(md.m.rows_n):
    for tx in range(md.m.cols):
        if md.m.at(tx, ty) == "r":
            md.bg.blit_cell(variants[h2(tx, ty, 55) % 3], tx * T, ty * T)

md.place("c", meadow_cairn(md.ROCK, md.GRASS))

md.finish()
