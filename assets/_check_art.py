#!/usr/bin/env python3
"""Contract checker for the art pipeline (stdlib only).

Painted-scene contracts: every assets/maps/*.txt parses and is enclosed except
at exit anchors; each map's scenes/<name>_ground.png and _overlay.png exist at
cols*32 x rows*32 with a majority-transparent overlay; the collision TileSet is
a single full-square physics tile; entities placed in painted .tscn scenes sit
on walkable cells. Legacy sheet/tileset checks remain until the overhaul's
remaining phases retire that art.

Run after any `python3 assets/_gen_*.py`: python3 assets/_check_art.py
"""
import os, re, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _core import ZONE_TILE, ZONE_CELL, OW_TILE, OW_CELL, ICON
from _maps import MapData

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


def png_alpha_ratio(rel):
    """Fraction of fully transparent pixels (our PNGs are filter-0 RGBA)."""
    path = os.path.join(ROOT, rel)
    data = open(path, "rb").read()
    w, h = struct.unpack(">II", data[16:24])
    idat, pos = b"", 8
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        if data[pos + 4:pos + 8] == b"IDAT":
            idat += data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * 4
    clear = 0
    for y in range(h):
        row = raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)]
        clear += sum(1 for i in range(3, stride, 4) if row[i] == 0)
    return clear / (w * h)


# ---- painted scenes -----------------------------------------------------------------
MAPS = {
    "maps/meadow.txt": ("scenes/meadow_ground.png", "scenes/meadow_overlay.png"),
    "maps/overworld.txt": ("scenes/overworld_ground.png", "scenes/overworld_overlay.png"),
    "maps/road.txt": ("scenes/road_ground.png", "scenes/road_overlay.png"),
    "maps/yard.txt": ("scenes/yard_ground.png", "scenes/yard_overlay.png"),
}

print("maps + painted scenes:")
maps = {}
for rel, (ground, overlay) in MAPS.items():
    m = MapData(os.path.join(HERE, rel))   # asserts rows/legend/anchors
    maps[rel] = m
    exits = [txy for name, txy in m.anchors.items() if name.startswith("exit_")]
    leaks = []
    for y in range(m.rows_n):
        for x in range(m.cols):
            if (x in (0, m.cols - 1) or y in (0, m.rows_n - 1)) and not m.legend[m.at(x, y)]["solid"]:
                if not any(abs(x - ex) <= 3 and abs(y - ey) <= 3 for (ex, ey) in exits):
                    leaks.append((x, y))
    check(f"{rel} enclosed (except exits)", not leaks, f"leaks at {leaks[:4]}")
    want = (m.cols * ZONE_TILE, m.rows_n * ZONE_TILE)
    for png in (ground, overlay):
        got = png_size(os.path.join("assets", png))
        check(f"assets/{png}", got == want, f"want {want}, got {got}")
    ratio = png_alpha_ratio(os.path.join("assets", overlay))
    check(f"assets/{overlay} mostly transparent", ratio > 0.5, f"only {ratio:.0%} clear")

# ---- collision tileset ---------------------------------------------------------------
print("collision tileset:")
src = open(os.path.join(ROOT, "assets/collision_tileset.tres")).read()
half = ZONE_TILE // 2
check("collision_tileset.tres tile_size", f"tile_size = Vector2i({ZONE_TILE}, {ZONE_TILE})" in src)
polys = re.findall(r"physics_layer_0/polygon_0/points = PackedVector2Array\(([^)]+)\)", src)
want_poly = f"-{half}, -{half}, {half}, -{half}, {half}, {half}, -{half}, {half}"
check("collision_tileset.tres one full-square tile", polys == [want_poly], f"got {polys}")
check("collision_tile.png", png_size("assets/collision_tile.png") == (ZONE_TILE, ZONE_TILE))

# ---- entity placement in painted scenes ----------------------------------------------
PLACEMENTS = {
    "scene/test_room.tscn": "maps/meadow.txt",
    "scene/intro_road.tscn": "maps/road.txt",
}

print("placements:")
for rel, map_rel in PLACEMENTS.items():
    m = maps[map_rel]
    src = open(os.path.join(ROOT, rel)).read()
    bad = []
    for name, x, y in re.findall(
            r'\[node name="(\w+)" parent="World"[^\]]*\]\nposition = Vector2\(([\d.]+), ([\d.]+)\)', src):
        tx, ty = int(float(x)) // ZONE_TILE, int(float(y)) // ZONE_TILE
        if m.legend[m.at(tx, ty)]["solid"]:
            bad.append((name, tx, ty))
    check(f"{rel} entities on walkable cells", not bad, str(bad))

# ---- sheet dimensions (legacy art still in play keeps its checks) --------------------
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

# ---- legacy TileSets (retired scene by scene as the overhaul lands) ------------------
TILESETS = {
    "assets/tileset.tres": (ZONE_TILE, {"0:1", "1:1"}),
    "assets/overworld_tileset.tres": (OW_TILE, {"0:0", "1:0", "0:1", "1:1", "4:1", "5:1", "6:1", "7:1", "2:2"}),
}

print("legacy tilesets:")
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
