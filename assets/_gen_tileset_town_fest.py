#!/usr/bin/env python3
"""Alembic Town FLOOR, FESTIVAL ERA — Prologue A's bright-era config for the
shared Alembic recipe (assets/_alembic.py, `build`).

The map grid is a BYTE COPY of town.txt and `_check_art.py` enforces it. Two
things differ and they are both here: the PALETTE (town_fest — golden-hour
under the leaves, cream plaster, festival magenta) and the GLOW. The crown was
closed in Basil's childhood too, so even the bright era is filtered light —
which is why the lamps and lanterns burn here as well, just softer: honest
fire owes the sun nothing.

Re-run: python3 assets/_gen_tileset_town_fest.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _alembic import build, FACES_FLOOR, T
from _tilekit import GLOW_WARM as WARM, GLOW_MINT as MINTG
from _overworld_tiles import OverWorld

_blob = OverWorld.glow_blob


def glow(tn, img):
    ox, oy = tn.bbox("oO")[0] * T, tn.bbox("oO")[1] * T
    _blob(img, ox + 24, oy + 24, 13, MINTG, 52)          # the fountain's charm
    # the ground buildings, derived from the footprint (see the drained town's
    # glow for why dabs are measured UP from the south edge)
    for chars in ("XPI", "12"):
        for comp in tn.comps(chars):
            x0, y0, x1, y1 = tn.comp_bbox(comp)
            cx = (x0 + x1 + 1) * T // 2
            base = (y1 + 1) * T
            _blob(img, cx, base - 8, 11, WARM, 46)       # an open doorway
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            # lamps + hook lanterns, softer than the drained era's: it is
            # daylight up there, but not down here
            if m.at(x, y) in "lL" and m.at(x, y - 1) not in "lL":
                _blob(img, x * T + 7, y * T + 4, 9, MINTG, 36)
            if m.at(x, y) in "hH" and m.at(x, y - 1) not in "hH":
                _blob(img, x * T + 8, y * T + 6, 8, WARM, 38)
    # the clip pass — LIGHT DOES NOT SPILL DOWN A VERTICAL FACE
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES_FLOOR:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))


build("town_fest", "town_fest", glow)
