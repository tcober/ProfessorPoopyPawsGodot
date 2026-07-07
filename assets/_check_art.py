#!/usr/bin/env python3
"""Contract checker for the art pipeline (stdlib only).

Contracts: every assets/maps/*.txt parses, is enclosed except at exit anchors,
and keeps its anchors on walkable cells; every map has a generated layout
matching the map's dims whose every atlas ref exists in the atlas PNG and is
declared in the TileSet .tres; the collision TileSet is a single full-square
physics tile; entities placed in .tscn scenes sit on walkable cells; sheet
dims and .tres regions match.

Run after any `python3 assets/_gen_*.py`: python3 assets/_check_art.py
"""
import os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from _core import ZONE_TILE, ZONE_CELL, OW_CELL, ICON
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


# ---- maps ------------------------------------------------------------------------
MAPS = [
    "maps/meadow.txt",
    "maps/overworld.txt",
    "maps/town.txt",
    "maps/house.txt",
    "maps/downstairs.txt",
]

print("maps:")
maps = {}
for rel in MAPS:
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
    bad_anchors = [(n, txy) for n, txy in m.anchors.items()
                   if m.legend[m.at(txy[0], txy[1])]["solid"]]
    check(f"{rel} anchors on walkable cells", not bad_anchors, str(bad_anchors))

# ---- tiled scenes (atlas + layout generated from the same map file) -------------------
TILED = {
    "maps/meadow.txt": ("tilesets/meadow_layout.txt", "tilesets/meadow_tiles.png",
                        "tilesets/meadow_tiles.tres"),
    "maps/house.txt": ("tilesets/house_layout.txt", "tilesets/house_tiles.png",
                       "tilesets/house_tiles.tres"),
    "maps/downstairs.txt": ("tilesets/downstairs_layout.txt",
                            "tilesets/downstairs_tiles.png",
                            "tilesets/downstairs_tiles.tres"),
    "maps/overworld.txt": ("tilesets/overworld_layout.txt",
                           "tilesets/overworld_tiles.png",
                           "tilesets/overworld_tiles.tres"),
    "maps/town.txt": ("tilesets/town_layout.txt",
                      "tilesets/town_tiles.png",
                      "tilesets/town_tiles.tres"),
}

print("tiled scenes:")
for map_rel, (layout, atlas, tres) in TILED.items():
    mm = maps[map_rel]
    layers = {}
    cur = None
    for ln in open(os.path.join(HERE, layout)):
        ln = ln.strip()
        if not ln or ln.startswith(";"):
            continue
        if ln.startswith("layer "):
            cur = ln.split()[1]
            layers[cur] = []
        else:
            layers[cur].append(ln)
    check(f"assets/{layout} has lower+upper layers",
          set(layers) == {"lower", "upper"}, f"got {sorted(layers)}")
    for name, rows in layers.items():
        check(f"assets/{layout} [{name}] dims match map",
              len(rows) == mm.rows_n and all(len(r.split()) == mm.cols for r in rows),
              f"{len(rows)} rows, map wants {mm.rows_n}x{mm.cols}")
    dims = png_size(os.path.join("assets", atlas))
    check(f"assets/{atlas} tile-aligned", dims is not None
          and dims[0] % ZONE_TILE == 0 and dims[1] % ZONE_TILE == 0, f"got {dims}")
    acols, arows = dims[0] // ZONE_TILE, dims[1] // ZONE_TILE
    refs = {tuple(int(v) for v in tok.split(",")) for rows in layers.values()
            for r in rows for tok in r.split() if tok != "-"}
    check(f"assets/{layout} refs inside atlas",
          all(0 <= cx < acols and 0 <= cy < arows for (cx, cy) in refs),
          f"atlas is {acols}x{arows} tiles")
    tsrc = open(os.path.join(HERE, tres)).read()
    check(f"assets/{tres} tile_size",
          f"tile_size = Vector2i({ZONE_TILE}, {ZONE_TILE})" in tsrc
          and f"texture_region_size = Vector2i({ZONE_TILE}, {ZONE_TILE})" in tsrc)
    undeclared = [rc for rc in refs if f"{rc[0]}:{rc[1]}/0 = 0" not in tsrc]
    check(f"assets/{tres} declares every referenced tile", not undeclared,
          f"missing {sorted(undeclared)[:4]}")

# ---- collision tileset ---------------------------------------------------------------
print("collision tileset:")
src = open(os.path.join(ROOT, "assets/collision_tileset.tres")).read()
half = ZONE_TILE // 2
check("collision_tileset.tres tile_size", f"tile_size = Vector2i({ZONE_TILE}, {ZONE_TILE})" in src)
polys = re.findall(r"physics_layer_0/polygon_0/points = PackedVector2Array\(([^)]+)\)", src)
want_poly = f"-{half}, -{half}, {half}, -{half}, {half}, {half}, -{half}, {half}"
check("collision_tileset.tres one full-square tile", polys == [want_poly], f"got {polys}")
check("collision_tile.png", png_size("assets/collision_tile.png") == (ZONE_TILE, ZONE_TILE))

# ---- entity placement -----------------------------------------------------------------
PLACEMENTS = {
    "scene/meadow.tscn": "maps/meadow.txt",
    "scene/house.tscn": "maps/house.txt",
    "scene/downstairs.tscn": "maps/downstairs.txt",
    "scene/alembic_town.tscn": "maps/town.txt",
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

# ---- sheet dimensions -----------------------------------------------------------------
SHEETS = {
    "assets/basil_gen.png": (6 * ZONE_CELL, 8 * ZONE_CELL),
    "assets/fuji_gen.png": (6 * ZONE_CELL, 10 * ZONE_CELL),
    "assets/slime_gen.png": (6 * 24, 4 * 24),
    "assets/overworld_basil.png": (4 * OW_CELL, 3 * OW_CELL),
    "assets/overworld_fuji.png": (4 * OW_CELL, 3 * OW_CELL),
    "assets/overworld_icons.png": (5 * ICON, ICON),
    "assets/placeholder/hearts.png": (48, 16),
    "assets/placeholder/ammo_pips.png": (16, 8),
    "assets/placeholder/laser_bolt.png": (26, 8),
    "assets/placeholder/muzzle_flash.png": (20, 20),
    "assets/placeholder/beaker.png": (12, 14),
    "assets/placeholder/shadow.png": (24, 10),
    "assets/placeholder/blow_dart.png": (12, 4),
}

print("sheets:")
for rel, want in SHEETS.items():
    got = png_size(rel)
    check(rel, got == want, f"want {want}, got {got}")

# ---- SpriteFrames regions -----------------------------------------------------------
FRAMES = {
    "entities/player/player_frames.tres": ("assets/basil_gen.png", ZONE_CELL),
    "entities/fuji/fuji_frames.tres": ("assets/fuji_gen.png", ZONE_CELL),
    "entities/enemies/slime_frames.tres": ("assets/slime_gen.png", 24),
    "entities/player/overworld_basil_frames.tres": ("assets/overworld_basil.png", OW_CELL),
    "entities/player/overworld_fuji_frames.tres": ("assets/overworld_fuji.png", OW_CELL),
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

print()
if FAILS:
    print(f"{len(FAILS)} check(s) FAILED")
    sys.exit(1)
print("all checks passed")
