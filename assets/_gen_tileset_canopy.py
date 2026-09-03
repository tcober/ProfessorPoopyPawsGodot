#!/usr/bin/env python3
"""THE BOUGHS, DRAINED PRESENT — the canopy scene's era config for the shared
Alembic recipe (assets/_alembic.py, `build_canopy`).

Up here the glow has three jobs: the trunk windows and doorways that say
somebody LIVES in the trees, the landing's hook lantern, and — the whole point
of the scene — the amber pinpricks of the town's own windows thirty feet down
in the drop field (`tn.drop_windows`, collected by `_drop_field`). The
fireflies are live scene code, above deck AND below it — motes drifting under
your feet are what sell the height.

Re-run: python3 assets/_gen_tileset_canopy.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _alembic import build_canopy, FACES_CANOPY, RING_CHARS, T
from _tilekit import GLOW_WARM as WARM
from _overworld_tiles import OverWorld

_blob = OverWorld.glow_blob


def glow(tn, img):
    # THE LIT WINDOW IN EVERY GREAT TRUNK — derived from the ring block's own
    # bbox so it cannot drift off the door when a tree moves.
    for comp in tn.comps(RING_CHARS):
        x0, y0, x1, y1 = tn.comp_bbox(comp)
        cx = (x0 + x1 + 1) * T // 2
        _blob(img, cx - 8, y0 * T + 26, 12, WARM, 62)         # the trunk window
        _blob(img, cx - 8, y0 * T + 62, 11, WARM, 48)         # the doorway below
    m = tn.m
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in "hH" and m.at(x, y - 1) not in "hH":
                _blob(img, x * T + 8, y * T + 6, 10, WARM, 56)
    # THE TOWN BELOW: every window _drop_field drew gets a pinprick. Small and
    # dim on purpose — light thirty feet down is scale, not illumination.
    for px, py in tn.drop_windows:
        _blob(img, px, py, 4, WARM, 46)
    # the clip pass — LIGHT DOES NOT SPILL DOWN A VERTICAL FACE (the trunk
    # segments, the rims and the gates; the drop cells are NOT faces, they are
    # the view, and their pinpricks stay)
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in FACES_CANOPY:
                for py in range(y * T, y * T + T):
                    for px in range(x * T, x * T + T):
                        img.put(px, py, (0, 0, 0, 0))


build_canopy("canopy", "canopy", glow)
