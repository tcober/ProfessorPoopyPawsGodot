#!/usr/bin/env python3
"""THE BOUGHS, FESTIVAL ERA — Prologue A's bright-era config for the canopy
recipe (assets/_alembic.py, `build_canopy`).

The grid is a BYTE COPY of canopy.txt (enforced). The palette is canopy_fest —
the same leaves in the childhood's filtered gold — and the glow is softer: the
trunk windows are lit for the day, the town below is awake rather than
lamplit, so its pinpricks barely read and the lantern carries the landing.

Re-run: python3 assets/_gen_tileset_canopy_fest.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _alembic import build_canopy, FACES_CANOPY, RING_CHARS, T
from _tilekit import GLOW_WARM as WARM
from _overworld_tiles import OverWorld

_blob = OverWorld.glow_blob


def glow(tn, img):
    for comp in tn.comps(RING_CHARS):
        x0, y0, x1, y1 = tn.comp_bbox(comp)
        cx = (x0 + x1 + 1) * T // 2
        _blob(img, cx - 8, y0 * T + 26, 10, WARM, 44)         # the trunk window
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in "hH" and m.at(x, y - 1) not in "hH":
                _blob(img, x * T + 8, y * T + 6, 8, WARM, 38)
    for px, py in tn.drop_windows:
        _blob(img, px, py, 3, WARM, 24)
    # the clip pass — LIGHT DOES NOT SPILL DOWN A VERTICAL FACE
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES_CANOPY:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))


build_canopy("canopy_fest", "canopy_fest", glow)
