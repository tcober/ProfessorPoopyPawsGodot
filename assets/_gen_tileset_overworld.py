#!/usr/bin/env python3
"""The overworld continent, POST-EBB (the live travel map) — a thin CONFIG
on the overworld tile kit.

Terrain fabrics, the neighbor-stamp autotile transitions (45-degree corner
cuts included) and the dedupe plumbing live in assets/_overworld_tiles.py;
the landmark compositions come from assets/_overworld_props.py: Alembic
Town's cluster ICON on Forest Land, LANTERNWOOD's snow-cabin icon on the
ice land, the Kingdom's castle + the Horn on Mountain Land, the CRYSTAL
SUMMIT (the big mountain's post-Ebb state — the giant crystal the world's
magic drained into, ablaze on the glow overlay), Basil's HOME TREE on the
SE coast, and the dark obelisk network. This file only picks the prop
palette, places the compositions at their map footprints, and writes the
additive glow overlay. Twin file: _gen_tileset_overworld_bright.py renders
the byte-locked pre-Ebb era (big_mountain, mint network) — keep their
placements and salts IDENTICAL apart from the summit + glow.

Re-run: python3 assets/_gen_tileset_overworld.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _overworld_tiles import OverWorld, T
from _tilekit import GLOW_WARM as WARM, GLOW_MINT as MINTG
from _overworld_props import (town_cluster, lone_tree, castle, home_tree,
                              mountain_peak, crystal_summit, big_mountain,
                              lanternwood_cluster, TOWN_DOORS)

CRYST = (196, 120, 255)
LAVAG = (255, 140, 60)                 # molten-lip glow

# doorway/window dabs inside the Lanternwood icon (cabin door centers from
# lanternwood_cluster's PIECES table) — the town of lanterns, every window lit
LANTERN_DOORS = ((36, 24), (58, 29), (89, 29), (26, 37), (61, 37), (78, 40),
                 (33, 49), (63, 50), (103, 53), (20, 62), (55, 61), (88, 64),
                 (41, 71), (74, 72), (21, 81), (77, 81))


def build(scene_key, map_name, summit, network_glow, summit_blaze):
    """One era of the continent. summit: the prop placed at 'B';
    network_glow: the obelisk/outcrop/shard dab color (violet = dark
    post-Ebb network, mint = alive); summit_blaze: light the crystal."""
    ow = OverWorld(map_name, scene_key)
    _blob = OverWorld.glow_blob

    ROOFB = ow.mat("roof_blue")
    ROOFG = ow.mat("roof_green")
    PLAST = ow.mat("plaster")

    ow.paint_terrain()

    # ---- the landmark compositions at their map footprints -------------------------
    ow.place("T", town_cluster(ROOFG, ROOFB, PLAST, ow.ROCK))
    ow.place("L", lanternwood_cluster(ROOFB, PLAST, ow.ROCK, ow.PINES,
                                      ow.SNOW))
    ow.place("C", castle(ROOFB, ow.ROCK))
    ow.place("V", mountain_peak(ow.ROCK, ow.SNOW))
    ow.place("B", summit(ow))
    # the home tree splits: the whole crown rides the upper layer over the
    # walkable G cells (duck in from the north or west, hidden under the
    # canopy); the trunk rows — and the door Basil lives behind — block
    lo, up = home_tree(ow.FOREST, ow.TRUNK, ow.GRASS)
    ow.place_split("gG", lo, up)
    ow.place_each("t", lone_tree(ow.FOREST))

    # ---- additive glow: lit windows, lanterns, lava lips, the network --------------
    def _glow(img):
        tx, ty = ow.bbox("T")[0] * T, ow.bbox("T")[1] * T
        for dx, dy in TOWN_DOORS:                          # the lit cottages
            _blob(img, tx + dx, ty + dy, 3, WARM, 44)
        _blob(img, tx + 106, ty + 58, 6, WARM, 56)         # the firebox coals
        _blob(img, tx + 114, ty + 42, 3, MINTG, 50)        # the boiler gauge
        _blob(img, tx + 23, ty + 40, 5, MINTG, 46)         # the rose window
        lx, ly = ow.bbox("L")[0] * T, ow.bbox("L")[1] * T
        for dx, dy in LANTERN_DOORS:                       # every cabin lit
            _blob(img, lx + dx, ly + dy, 3, WARM, 42)
        for px_ in (46, 64):                               # the gate lanterns
            _blob(img, lx + px_, ly + 76, 4, WARM, 54)
        cx0, cy0 = ow.bbox("C")[0] * T, ow.bbox("C")[1] * T
        _blob(img, cx0 + 45, cy0 + 36, 3, WARM, 50)        # keep windows
        _blob(img, cx0 + 51, cy0 + 36, 3, WARM, 46)
        _blob(img, cx0 + 44, cy0 + 58, 3, WARM, 42)        # gate lamps
        _blob(img, cx0 + 52, cy0 + 58, 3, WARM, 42)
        gx, gy = ow.bbox("gG")[0] * T, ow.bbox("gG")[1] * T
        _blob(img, gx + 48, gy + 130, 5, WARM, 52)         # the hermit's door
        _blob(img, gx + 28, gy + 99, 3, WARM, 46)          # his lantern
        _blob(img, gx + 56, gy + 88, 2, WARM, 40)          # the round window
        if summit_blaze:                                   # the drained magic,
            bx, by = ow.bbox("B")[0] * T, ow.bbox("B")[1] * T   # ablaze
            _blob(img, bx + 112, by + 10, 22, CRYST, 62)
            _blob(img, bx + 112, by + 46, 14, CRYST, 44)
            for vx, vy in ((88, 108), (140, 104), (108, 116),  # vein nodes
                           (80, 52), (146, 56)):
                _blob(img, bx + vx, by + vy, 4, CRYST, 40)
        for y in range(ow.m.rows_n):                       # molten pool lips
            for x in range(ow.m.cols):
                if ow.m.at(x, y) != "l":
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if ow.m.at(x + dx, y + dy) == "a":
                        _blob(img, x * T + 8 + dx * 8, y * T + 8 + dy * 8,
                              3, LAVAG, 44)

    ow.write_glow(_glow)
    ow.finish()
    return ow


if __name__ == "__main__":
    build("overworld", "overworld",
          summit=lambda ow: crystal_summit(ow.ROCK),
          network_glow=CRYST, summit_blaze=True)
