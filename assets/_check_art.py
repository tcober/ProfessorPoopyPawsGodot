#!/usr/bin/env python3
"""Contract checker for the art pipeline (stdlib only).

Verifies that every generated sheet has the dimensions the game expects, that the
SpriteFrames .tres regions are cell-sized, grid-aligned and inside their sheet, and
that the TileSet .tres tile_size/physics polygons match _artlib's scale constants.

Run after any `python3 assets/_gen_*.py`: python3 assets/_check_art.py
"""
import os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _artlib import ZONE_TILE, ZONE_CELL, OW_TILE, OW_CELL, ICON

FAILS = []


def check(label, cond, detail=""):
    if cond:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        FAILS.append(label)


def png_size(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return None
    data = open(path, "rb").read()
    return struct.unpack(">II", data[16:24])


# ---- sheet dimensions --------------------------------------------------------------
SHEETS = {
    "assets/basil_gen.png": (6 * ZONE_CELL, 7 * ZONE_CELL),
    "assets/schweinler_gen.png": (4 * ZONE_CELL, 4 * ZONE_CELL),
    "assets/slime_gen.png": (6 * 48, 4 * 48),
    "assets/tileset_gen.png": (4 * ZONE_TILE, 2 * ZONE_TILE),
    "assets/overworld_tiles.png": (8 * OW_TILE, 3 * OW_TILE),
    "assets/overworld_basil.png": (4 * OW_CELL, 3 * OW_CELL),
    "assets/overworld_icons.png": (5 * ICON, ICON),
    "assets/placeholder/hearts.png": (96, 32),
    "assets/placeholder/ammo_pips.png": (32, 16),
    "assets/placeholder/laser_bolt.png": (52, 16),
    "assets/placeholder/muzzle_flash.png": (40, 40),
    "assets/placeholder/beaker.png": (24, 28),
    "assets/placeholder/shadow.png": (48, 20),
}

print("sheets:")
for rel, want in SHEETS.items():
    got = png_size(rel)
    check(rel, got == want, f"want {want}, got {got}")

# ---- SpriteFrames regions -----------------------------------------------------------
FRAMES = {
    "entities/player/player_frames.tres": ("assets/basil_gen.png", ZONE_CELL),
    "entities/enemies/slime_frames.tres": ("assets/slime_gen.png", 48),
    "entities/npcs/schweinler_frames.tres": ("assets/schweinler_gen.png", ZONE_CELL),
    "entities/player/overworld_basil_frames.tres": ("assets/overworld_basil.png", OW_CELL),
}

print("frames:")
for rel, (sheet, cell) in FRAMES.items():
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        check(rel, False, "missing")
        continue
    src = open(path).read()
    dims = png_size(sheet)
    regions = [tuple(int(float(v)) for v in m.split(","))
               for m in re.findall(r"Rect2\(([^)]+)\)", src)]
    ok = bool(regions)
    detail = ""
    for (x, y, w, h) in regions:
        if (w, h) != (cell, cell):
            ok, detail = False, f"region {w}x{h} != cell {cell}"
            break
        if x % cell or y % cell:
            ok, detail = False, f"region ({x},{y}) not on {cell} grid"
            break
        if dims and (x + w > dims[0] or y + h > dims[1]):
            ok, detail = False, f"region ({x},{y}) outside sheet {dims}"
            break
    check(f"{rel} ({len(regions)} regions)", ok, detail)

# ---- TileSets -----------------------------------------------------------------------
TILESETS = {
    "assets/tileset.tres": (ZONE_TILE, {"0:1", "1:1"}),
    "assets/overworld_tileset.tres": (OW_TILE, {"0:0", "1:0", "0:1", "1:1", "4:1", "5:1", "6:1", "7:1", "2:2"}),
}

print("tilesets:")
for rel, (tile, solid) in TILESETS.items():
    path = os.path.join(ROOT, rel)
    src = open(path).read()
    check(f"{rel} tile_size", f"tile_size = Vector2i({tile}, {tile})" in src)
    half = tile // 2
    polys = re.findall(r"physics_layer_0/polygon_0/points = PackedVector2Array\(([^)]+)\)", src)
    want_poly = f"-{half}, -{half}, {half}, -{half}, {half}, {half}, -{half}, {half}"
    check(f"{rel} polygons ±{half}", polys and all(p == want_poly for p in polys),
          f"{sum(1 for p in polys if p != want_poly)} of {len(polys)} off-size")
    have = set(re.findall(r"(\d+:\d+)/0/physics_layer_0", src))
    check(f"{rel} solid tiles", have == solid, f"want {sorted(solid)}, got {sorted(have)}")

print()
if FAILS:
    print(f"{len(FAILS)} check(s) FAILED")
    sys.exit(1)
print("all checks passed")
