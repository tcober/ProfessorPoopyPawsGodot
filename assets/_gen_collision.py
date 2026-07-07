#!/usr/bin/env python3
"""Fully transparent 16x16 tile for the invisible physics-only collision
TileSet (assets/collision_tileset.tres) that every scene builds at runtime.

Run: python3 assets/_gen_collision.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import Img, ZONE_TILE

Img(ZONE_TILE, ZONE_TILE).save(os.path.join(HERE, "collision_tile.png"))
