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
LAYERS = {}
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
    LAYERS[map_rel] = layers

# ---- z-order doctrine (see DESIGN.md "Z-order / layering doctrine") -------------------
# Upper-layer art draws over EVERY body unconditionally, so it is only legal
# where a body can never stand south of it un-occluded: anchored on solid
# ground (or more upper art), with walk-behind corridors capped by a solid
# ridge row so at most a head-peek crosses the silhouette.
print("z-order:")
UPPER_REQUIRED = {"maps/overworld.txt", "maps/town.txt",
                  "maps/house.txt", "maps/downstairs.txt"}
CHIBI_MAPS = {"maps/overworld.txt"}    # 24x24 travel chibi, figure <=1 tile tall
for map_rel, layers in LAYERS.items():
    mm = maps[map_rel]
    upper = {(x, y) for y, row in enumerate(layers["upper"])
             for x, tok in enumerate(row.split()) if tok != "-"}
    if map_rel in UPPER_REQUIRED:
        check(f"{map_rel} upper layer non-empty", bool(upper))
    if not upper:
        continue

    def terr(x, y, mm=mm):
        ch = mm.at(x, y)
        return mm.legend[ch]["terrain"] if ch else None

    def solid(x, y, mm=mm):
        ch = mm.at(x, y)
        return mm.legend[ch]["solid"] if ch else True

    # (support) every upper cell IS solid (the mask-band idiom: _eave_lift
    # mirrors a solid row's top <=12px so pressed bodies' feet are swallowed
    # — a south body's head only reaches the row's bottom ~3px), or rests on
    # solid ground / more upper art / a doorway (lintels + door-top strips
    # float over the walk-through by design)
    bad = [(x, y) for (x, y) in upper
           if not (solid(x, y) or solid(x, y + 1) or (x, y + 1) in upper
                   or terr(x, y) == "door" or terr(x, y + 1) == "door")]
    check(f"{map_rel} upper art supported", not bad,
          f"floating over walkable ground at {sorted(bad)[:4]}")
    # (head clearance) a walkable covered cell needs covered art due north:
    # the corridor is capped by a solid ridge row, so a body can never poke
    # more than its head over the prop's silhouette. Scale-gated: a chibi map's
    # figure fits inside one tile, so it can't out-peek a silhouette — whole
    # crowns/roofs may be open walk-behind there, no cap required
    if map_rel not in CHIBI_MAPS:
        bad = [(x, y) for (x, y) in upper
               if not solid(x, y) and terr(x, y) != "door" and (x, y - 1) not in upper]
        check(f"{map_rel} walk-behind corridors capped", not bad,
              f"make the row above a solid ridge at {sorted(bad)[:4]}")
    # (ridge placement) a ridge cell exists to sit under a prop's top rows —
    # it (or, at silhouette corners, a 4-neighbor) must carry upper art
    bad = [(x, y) for y in range(mm.rows_n) for x in range(mm.cols)
           if terr(x, y) == "ridge" and (x, y) not in upper
           and not any(n in upper for n in ((x + 1, y), (x - 1, y),
                                            (x, y + 1), (x, y - 1)))]
    check(f"{map_rel} ridge cells under upper art", not bad, str(bad[:4]))

# ---- Tier-3 props manifests (TileScene.emit_prop -> scene/prop_spawner.gd) -----------
print("props manifests:")
PROPS = {
    "maps/house.txt": "tilesets/house_props.txt",
    "maps/downstairs.txt": "tilesets/downstairs_props.txt",
    "maps/town.txt": "tilesets/town_props.txt",
}
T3_CHARS = {}                          # map_rel -> chars whose art is y-sorted
for map_rel, props_rel in PROPS.items():
    mm = maps[map_rel]
    path = os.path.join(HERE, props_rel)
    if not os.path.exists(path):
        check(f"assets/{props_rel} exists", False)
        continue
    for ln in open(path):
        ln = ln.strip()
        if not ln or ln.startswith(";"):
            continue
        parts = ln.split()
        ok = len(parts) >= 4 and parts[0] == "prop"
        if ok:
            T3_CHARS.setdefault(map_rel, set()).update(parts[2])
        detail = ""
        hframes = 1
        for opt in parts[4:]:
            if opt.startswith("hframes="):
                hframes = int(opt.split("=", 1)[1])
            elif opt != "each" and not opt.startswith(("anchor=top:", "base_inset=")):
                ok, detail = False, f"unknown option {opt!r}"
        chars = parts[2]
        if not any(ch in chars for row in mm.rows for ch in row):
            ok, detail = False, f"no {chars!r} cells in the map"
        dims = png_size(os.path.join("assets", "tilesets", parts[3]))
        if dims is None or dims[0] % hframes:
            ok, detail = False, f"png {dims}, hframes {hframes}"
        check(f"assets/{props_rel}: {parts[1]}", ok, detail)

# ---- invisible walls (silhouette-fit rule, DESIGN.md) ---------------------------------
# A solid cell whose art dedupes to a tile also used on open walkable ground
# reads as walkable but blocks — the deduped atlas makes this exact: an
# art-free prop-footprint corner shares its atlas tile with plain fabric.
# Only faces a body can press count (4-adjacent to a walkable cell); Tier-3
# chars are exempt (their solid cells sit under y-sorted World sprites).
print("invisible walls:")
for map_rel, layers in LAYERS.items():
    mm = maps[map_rel]
    lower = [row.split() for row in layers["lower"]]
    upper = {(x, y) for y, row in enumerate(layers["upper"])
             for x, tok in enumerate(row.split()) if tok != "-"}
    exempt = T3_CHARS.get(map_rel, set())

    def solid(x, y, mm=mm):
        ch = mm.at(x, y)
        return mm.legend[ch]["solid"] if ch else True

    walk_toks = {lower[y][x] for y in range(mm.rows_n) for x in range(mm.cols)
                 if not solid(x, y)}
    bad = [(x, y) for y in range(mm.rows_n) for x in range(mm.cols)
           if solid(x, y) and mm.at(x, y) not in exempt
           and lower[y][x] != "-" and lower[y][x] in walk_toks
           and (x, y) not in upper
           and any(not solid(*n) for n in ((x + 1, y), (x - 1, y),
                                           (x, y + 1), (x, y - 1)))]
    check(f"{map_rel} no invisible walls", not bad,
          f"solid cells rendering as open ground at {sorted(bad)[:6]}")

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
