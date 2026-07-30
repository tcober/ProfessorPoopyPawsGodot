#!/usr/bin/env python3
"""Alembic Town, FESTIVAL ERA — Prologue A's bright-era config for the shared
Alembic recipe (assets/_alembic.py).

The map grid is a BYTE COPY of town.txt and `_check_art.py` enforces it, so every
lane, every ladder, every ring deck and every plank is recognisable when the
drained present arrives. Three things differ and they are all here: the PALETTE
(town_fest — spring grass, cream plaster, sun-warmed boardwalk timber, festival
magenta), the GLOW, and the Academy's door, which is OPEN.

The festival glow is daylight MAGIC, not candlelight: the rose window burns mint
because magic is alive here, the fountain is charmed, and the lamps stay dark
because nobody has needed to light one.

Re-run: python3 assets/_gen_tileset_town_fest.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _alembic import build, FACES, T, BAND_SALT, lantern_cells
from _tilekit import GLOW_WARM as WARM, GLOW_MINT as MINTG
from _overworld_tiles import OverWorld

_blob = OverWorld.glow_blob


def glow(tn, img):
    kx, ky = tn.bbox("K")[0] * T, tn.bbox("K")[1] * T
    _blob(img, kx + 79, ky + 14, 18, MINTG, 66)          # the rose window AWAKE
    _blob(img, kx + 40, ky + 20, 8, MINTG, 40)           # ward-light in a hall window
    _blob(img, kx + 120, ky + 20, 8, MINTG, 40)
    _blob(img, kx + 79, ky + 37, 11, WARM, 46)           # the OPEN door's warm mouth
    ox, oy = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox + 24, oy + 24, 13, MINTG, 52)          # the fountain's charm shimmer
    # the canopy huts, derived from the footprint (see the drained town's glow for
    # why it is measured UP from the south edge and not down from the bbox top)
    for chars in ("H", "N", "X", "P", "I"):
        for comp in tn.comps(chars):
            x0, y0, x1, y1 = tn.comp_bbox(comp)
            cx = (x0 + x1 + 1) * T // 2
            base = (y1 + 1) * T
            _blob(img, cx, base - 8, 11, WARM, 46)       # a hut's open doorway
            _blob(img, cx - 46, base - 44, 6, WARM, 34)  # its hanging lantern
    # the clip pass — see the drained town's generator: LIGHT DOES NOT SPILL DOWN A
    # FACE, and the glow overlay renders UNDER the y-sorted World, so a wash across a
    # fascia lands on the boardwalk's own underside.
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))
    # The boardwalk's hanging lanterns are LIT EVEN BY DAY here, faintly — a
    # festival is a thing you light lamps for in the afternoon, and it is the one
    # warm note in an era whose light is otherwise all charm-mint.
    for chars, salt in BAND_SALT.items():
        for x, y in lantern_cells(m, chars, salt):
            _blob(img, x * T + 8, y * T + 17, 8, WARM, 34)


build("town_fest", "town_fest", glow, open_door=True)
