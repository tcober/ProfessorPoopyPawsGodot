#!/usr/bin/env python3
"""The overworld continent, PRE-EBB ERA — the byte-locked twin of
_gen_tileset_overworld.py in the bright "overworld_bright" palette.

Identical placements and salts apart from the era differences: the big
mountain wears its snow summit (big_mountain, not crystal_summit — no
blaze), and the obelisk network glows MINT (alive) instead of drained
violet. Used by scene/overworld_bright.tscn and the Ebb event scene;
nothing in the live flow walks this era.

Re-run: python3 assets/_gen_tileset_overworld_bright.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _tilekit import GLOW_MINT as MINTG
from _overworld_props import big_mountain
import _gen_tileset_overworld as base

if __name__ == "__main__":
    base.build("overworld_bright", "overworld_bright",
               summit=lambda ow: big_mountain(ow.ROCK, ow.SNOW),
               network_glow=MINTG, summit_blaze=False)
