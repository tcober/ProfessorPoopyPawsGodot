#!/usr/bin/env python3
"""Alembic Town, DRAINED PRESENT — the era config for the shared Alembic recipe.

The recipe itself is assets/_alembic.py: the buildings, the trunk armature, the
face bands, the ladders, the spans, the understory, the depth masks and the whole
assert block. This file is what makes it the drained town — the `town` palette and
a night glow — and that is deliberately all it is. The two eras were parallel
350-line files once and drifted; see _alembic.py's docstring for what that cost.

For the geometry — the four storeys, the five trunk channels, the ring decks you
walk round every tree — read assets/maps/town.txt's header.

Re-run: python3 assets/_gen_tileset_town.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _alembic import build, FACES, T, BAND_SALT, lantern_cells
from _tilekit import GLOW_WARM as WARM, GLOW_MINT as MINTG
from _overworld_tiles import OverWorld

_blob = OverWorld.glow_blob            # shared radial glow dab (see TileScene)


def glow(tn, img):
    """The sleeping town's little lights. Warm, sparse, and mostly indoors: the
    magic is gone, so nothing out here glows on its own any more."""
    # THE HUTS. Their dabs are derived from the FOOTPRINT rather than hand-offset
    # into a facade, because tree_hut's art is taller than the rows it declares (see
    # its `rise`) — an offset measured down from the bbox top would miss the window by
    # however much the roof happens to stand up. Measured UP from the footprint's
    # south edge it lands on the door, the hearth window and the hanging lantern
    # whatever the cone does.
    for chars in ("H", "N", "X", "P", "I"):
        for comp in tn.comps(chars):
            x0, y0, x1, y1 = tn.comp_bbox(comp)
            cx = (x0 + x1 + 1) * T // 2
            base = (y1 + 1) * T
            _blob(img, cx, base - 8, 13, WARM, 64)            # the doorway
            _blob(img, cx - 24, base - 30, 9, WARM, 54)       # the hearth window
            _blob(img, cx - 46, base - 44, 7, WARM, 44)       # the hanging lantern
    kx, ky = tn.bbox("K")[0] * T, tn.bbox("K")[1] * T
    _blob(img, kx + 79, ky + 14, 16, MINTG, 46)               # the rose window
    ox, oy = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox + 24, oy + 29, 10, MINTG, 40)               # fountain shimmer
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            # each lamp component's TOP cell (usually the walkable L head)
            if m.at(x, y) in "lL" and m.at(x, y - 1) not in "lL":
                _blob(img, x * T + 7, y * T + 4, 11, MINTG, 58)
    qx, qy = tn.bbox("Q")[0] * T, tn.bbox("Q")[1] * T
    # THE CLIP PASS, and it is not optional. Lanternwood's lesson: LIGHT DOES NOT
    # SPILL DOWN A ROCK FACE. The glow overlay renders UNDER the y-sorted World, so a
    # hut lantern's wash bleeding across the fascia below it lands on the boardwalk's
    # own underside and destroys the whole terrace read — the storeys stop looking
    # stacked and start looking painted. Every face band, bough and trunk is wiped,
    # and the car's dab is laid AFTERWARDS because the shaft is exactly the place a
    # light IS meant to be.
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))
    _blob(img, qx + 24, qy + 30, 7, WARM, 54)
    # THE FASCIA LANTERNS, laid AFTER the clip pass for the same reason the lift
    # car's dab is: the clip exists to stop light spilling down a face, and these
    # lights are ON the face. Their columns are recomputed from stamp_columns' own
    # hash, so a light can never end up on a column with no lantern under it.
    for chars, salt in BAND_SALT.items():
        for x, y in lantern_cells(m, chars, salt):
            _blob(img, x * T + 8, y * T + 17, 10, WARM, 60)


build("town", "town", glow)
