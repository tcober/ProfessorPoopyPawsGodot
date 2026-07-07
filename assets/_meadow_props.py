#!/usr/bin/env python3
"""Whisker Meadow props: the boulder outcrops and the trailhead cairn.

One-off zone-scale props on the shared prop vocabulary (_propkit.S/ln/edge +
Sprite volume shading) — like every prop kit, full per-pixel shading is fine
because props are blitted once, not derived per-tile. Each sprite fills
exactly one 16px cell (the map's solid `r`/`c` cells); the grass fabric shows
through unset pixels, and the driver's STRUCT contact band grounds the cell
below.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _propkit import S, ln, edge


def meadow_boulder(rock, grass, salt=57):
    """A squat lichen-flecked lavender dome in one 16px cell — the painted
    meadow's boulder look: NW-lit low dome, a crack, a dark seated base,
    base tufts. Geometry nudges on the salt so outcrop cells vary."""
    k = salt % 3
    cx = 7.5 + (0.5 if k == 1 else -0.5 if k == 2 else 0.0)
    rx = 5.6 + (0.5 if k == 0 else 0.0)
    ry = 3.6 + (0.4 if k == 1 else 0.0)
    sp = S(16, 16, salt)
    sp.ball(cx, 9.6, rx, ry, rock, power=2.4)          # low wide dome
    for x in range(int(cx - rx) + 1, int(cx + rx)):    # dark seated base
        sp.set(x, 12, rock[4])
    ln(sp, cx - 1 - k, 7, cx + 1, 10, rock[4])         # the crack
    sp.set(int(cx + 1), 11, rock[3])
    sp.set(int(cx - 2), 7, grass[1])                   # lichen on the lit shoulder
    if k != 2:
        sp.set(int(cx + 2 - k), 8, grass[2])
    sp.set(int(cx - rx) + 1, 12, grass[2])             # base tufts seat it
    sp.set(int(cx + rx) - 1, 12, grass[3])
    edge(sp)
    return sp


def meadow_cairn(rock, grass, salt=71):
    """The trailhead cairn: a stacked boulder pair marking the trail's end
    (the painted meadow's focal landmark). Squat seated dome + a smaller
    offset capstone, lit a touch harder so the stack reads."""
    sp = S(16, 16, salt)
    sp.ball(7.5, 10.5, 5.4, 3.4, rock, power=2.4)      # the seated base
    sp.ball(6.5, 5.5, 3.4, 2.6, rock, sh=-0.06)        # the capstone
    for x in range(4, 12):
        sp.set(x, 13, rock[4])                         # settle band
    ln(sp, 9, 4, 11, 7, rock[4])                       # capstone crack
    sp.set(4, 5, grass[1])                             # lichen
    sp.set(10, 9, grass[2])
    sp.set(3, 13, grass[2])                            # base tufts
    sp.set(12, 13, grass[3])
    edge(sp)
    return sp
