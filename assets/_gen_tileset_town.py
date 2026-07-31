#!/usr/bin/env python3
"""Alembic Town, DRAINED PRESENT — the era config for the shared Alembic recipe.

The recipe itself is assets/_alembic.py: the buildings, the trunk armature, the
face bands, the ladders, the spans, the understory, the depth masks and the whole
assert block. This file is what makes it the drained town — the `town` palette and
a night glow — and that is deliberately all it is. The two eras were parallel
350-line files once and drifted; see _alembic.py's docstring for what that cost.

For the geometry — the forest-floor clearing, the four great trees and the ring
decks you walk round every one of them — read assets/maps/town.txt's header.

Re-run: python3 assets/_gen_tileset_town.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _alembic import build, FACES, RING_CHARS, T, BAND_SALT, lantern_cells
from _tilekit import GLOW_WARM as WARM, GLOW_MINT as MINTG
from _overworld_tiles import OverWorld

_blob = OverWorld.glow_blob            # shared radial glow dab (see TileScene)


def glow(tn, img):
    """The sleeping town's little lights. Warm, sparse, and mostly indoors: the
    magic is gone, so nothing out here glows on its own any more."""
    # THE GROUND BUILDINGS. Their dabs are derived from the FOOTPRINT and measured UP
    # from its SOUTH EDGE, never down from the bbox top: a building's sheet may stand
    # taller than the rows it declares, and an offset from the top then misses the
    # window by however much the roof happens to rise. The two kinds put their lit
    # pane in different places, though — `town_shop`'s display window is low and wide
    # because it IS the shopfront, the cottage's hearth window is up under the eave —
    # so they take their own offsets rather than sharing one that fits neither.
    for chars, (px, py, r, a) in (("XPI", (-23, -12, 11, 66)),
                                  ("12", (-24, -30, 9, 54))):
        for comp in tn.comps(chars):
            x0, y0, x1, y1 = tn.comp_bbox(comp)
            cx = (x0 + x1 + 1) * T // 2
            base = (y1 + 1) * T
            _blob(img, cx, base - 8, 13, WARM, 64)            # the doorway
            _blob(img, cx + px, base + py, r, WARM, a)        # the lit pane
    # THE LIT WINDOW IN EVERY GREAT TRUNK — the one light up in the canopy, and the
    # cue that says somebody lives in the tree rather than on it. Derived from the
    # ring block's own bbox so it cannot drift off the door when a tree moves.
    for comp in tn.comps(RING_CHARS):
        x0, y0, x1, y1 = tn.comp_bbox(comp)
        cx = (x0 + x1 + 1) * T // 2
        _blob(img, cx - 8, y0 * T + 26, 12, WARM, 62)         # the trunk window
        _blob(img, cx - 8, y0 * T + 62, 11, WARM, 48)         # the doorway below it
    ox, oy = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox + 24, oy + 29, 10, MINTG, 40)               # fountain shimmer
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            # each lamp component's TOP cell (usually the walkable L head)
            if m.at(x, y) in "lL" and m.at(x, y - 1) not in "lL":
                _blob(img, x * T + 7, y * T + 4, 11, MINTG, 58)
    # THE CLIP PASS, and it is not optional. Lanternwood's lesson: LIGHT DOES NOT
    # SPILL DOWN A VERTICAL FACE. The glow overlay renders UNDER the y-sorted World,
    # so a window's wash bleeding across the trunk below it lands on bark that is
    # thirty feet from the light and flattens the whole tree.
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))


build("town", "town", glow)
