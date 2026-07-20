#!/usr/bin/env python3
"""Shared prop-drawing primitives used by every prop kit (_interior_props,
_overworld_props, _town_props): the footprint-sized canvas, an interpolated
1px line, and the silhouette outline. Stdlib-only, deterministic.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _sprites import Sprite
from _tilekit import OUTLINE


def S(w, h=None, salt=0):
    """Footprint-sized sparse canvas (square Sprite; draw only in w x h)."""
    return Sprite(max(w, h or w), grain=1, salt=salt, jitter=0.0)


def ln(sp, x0, y0, x1, y1, c):
    """Interpolated 1px line from (x0, y0) to (x1, y1)."""
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(int(steps) + 1):
        t = i / steps
        sp.set(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), c)


def edge(sp, h=None):
    """Uniform dark CT silhouette outline. Pass the footprint height `h` when
    it is shorter than the (square) canvas: outline() dilates 1px in every
    direction, and the row it writes at y=h would otherwise blit onto the
    walkable map cell SOUTH of the prop."""
    sp.outline({}, OUTLINE)
    if h is not None:
        for y in range(h, sp.n):
            sp.px[y] = [None] * sp.n


def split_rows(sp, y_cut):
    """Split a finished (already edge()d) prop into a (lower, upper) pair at
    pixel row y_cut: rows above the cut ride the UPPER tile layer (bodies walk
    behind them), the rest bakes below entities. Pixels are copied verbatim,
    so the silhouette outline crosses the cut with no seam."""
    lo, up = S(sp.n, salt=sp.salt), S(sp.n, salt=sp.salt)
    for y in range(sp.n):
        dst = up if y < y_cut else lo
        dst.px[y] = list(sp.px[y])
    return lo, up
