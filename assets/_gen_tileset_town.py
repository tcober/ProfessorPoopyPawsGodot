#!/usr/bin/env python3
"""Alembic Town FLOOR, DRAINED PRESENT — the era config for the shared Alembic
recipe (assets/_alembic.py, `build`).

This is the permanent-dusk town: the four great trunks run off the top of the
frame, the canopy is another scene (alembic_canopy.tscn), and the town's light
is its own — doorways, panes, the fountain's dying shimmer, the street lamps
and the hook lanterns, all warm points in a blue-green dark. The fireflies are
live scene code (components/fireflies.gd), not paint.

Re-run: python3 assets/_gen_tileset_town.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _alembic import build, FACES_FLOOR, T
from _tilekit import GLOW_WARM as WARM, GLOW_MINT as MINTG
from _overworld_tiles import OverWorld

_blob = OverWorld.glow_blob            # shared radial glow dab (see TileScene)


def glow(tn, img):
    """The dusk town's lights. In permanent dusk the glow overlay is not
    decoration, it is half the palette: every warm dab below is somewhere a
    body can stand, because the overlay renders UNDER the y-sorted World."""
    # THE GROUND BUILDINGS. Dabs derived from the FOOTPRINT and measured UP
    # from its SOUTH EDGE, never down from the bbox top: a building's sheet may
    # stand taller than the rows it declares. Shops and cottages put their lit
    # pane in different places, so they take their own offsets.
    for chars, (px, py, r, a) in (("XPI", (-23, -12, 11, 70)),
                                  ("12", (-24, -30, 9, 58))):
        for comp in tn.comps(chars):
            x0, y0, x1, y1 = tn.comp_bbox(comp)
            cx = (x0 + x1 + 1) * T // 2
            base = (y1 + 1) * T
            _blob(img, cx, base - 8, 13, WARM, 68)            # the doorway
            _blob(img, cx + px, base + py, r, WARM, a)        # the lit pane
    ox, oy = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox + 24, oy + 29, 10, MINTG, 40)               # fountain shimmer
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            # each lamp component's TOP cell (usually the walkable head)
            if m.at(x, y) in "lL" and m.at(x, y - 1) not in "lL":
                _blob(img, x * T + 7, y * T + 4, 11, MINTG, 58)
            # the hook lanterns: candle amber beside every ladder foot and the
            # south gate — in the dusk town these carry the streets
            if m.at(x, y) in "hH" and m.at(x, y - 1) not in "hH":
                _blob(img, x * T + 8, y * T + 6, 10, WARM, 56)
    # THE CLIP PASS, and it is not optional: LIGHT DOES NOT SPILL DOWN A
    # VERTICAL FACE. The glow overlay renders UNDER the y-sorted World, so a
    # wash bleeding across a trunk flattens the whole tree.
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES_FLOOR:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))


build("town", "town", glow)
