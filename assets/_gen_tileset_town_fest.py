#!/usr/bin/env python3
"""Alembic Town, FESTIVAL ERA — Prologue A's bright-era config for the shared
Alembic recipe (assets/_alembic.py).

The map grid is a BYTE COPY of town.txt and `_check_art.py` enforces it, so every
lane, every ladder, every ring deck and every plank is recognisable when the
drained present arrives. Three things differ and they are all here: the PALETTE
(town_fest — spring grass, cream plaster, sun-warmed boardwalk timber, festival
magenta), the GLOW, and the Academy's door, which is OPEN.

The festival glow is daylight MAGIC, not candlelight: the fountain is charmed, the
great trees' windows are lit for the day, and the street lamps stay dark because
nobody has needed one yet. The Academy is not in this grid any more — it is its own
scene, reached by the north lane — so the rose window's mint went with it.

Re-run: python3 assets/_gen_tileset_town_fest.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _alembic import build, FACES, RING_CHARS, T
from _tilekit import GLOW_WARM as WARM, GLOW_MINT as MINTG
from _overworld_tiles import OverWorld

_blob = OverWorld.glow_blob


def glow(tn, img):
    ox, oy = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox + 24, oy + 24, 13, MINTG, 52)          # the fountain's charm shimmer
    # the ground buildings, derived from the footprint (see the drained town's glow
    # for why it is measured UP from the south edge and not down from the bbox top)
    for chars in ("XPI", "12"):
        for comp in tn.comps(chars):
            x0, y0, x1, y1 = tn.comp_bbox(comp)
            cx = (x0 + x1 + 1) * T // 2
            base = (y1 + 1) * T
            _blob(img, cx, base - 8, 11, WARM, 46)       # an open doorway
    # every great tree's window, lit for the festival — the one warm note in an era
    # whose light is otherwise all charm-mint
    for comp in tn.comps(RING_CHARS):
        x0, y0, x1, y1 = tn.comp_bbox(comp)
        cx = (x0 + x1 + 1) * T // 2
        _blob(img, cx - 8, y0 * T + 26, 10, WARM, 44)
    # the clip pass — see the drained town's generator: LIGHT DOES NOT SPILL DOWN A
    # VERTICAL FACE, and the glow overlay renders UNDER the y-sorted World.
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))


build("town_fest", "town_fest", glow)
