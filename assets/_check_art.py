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


def png_alpha(rel):
    """Decode an 8-bit RGB(A) non-interlaced PNG -> (w, h, alpha rows).
    Stdlib-only, mirror of _core's writer; used by the T3 coverage lint to
    measure how much of a footprint cell the y-sorted prop art actually
    covers."""
    import zlib
    data = open(os.path.join(ROOT, rel), "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{rel}: not a PNG"
    pos, idat, w, h, bit, color = 8, b"", 0, 0, 0, 0
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        if typ == b"IHDR":
            w, h, bit, color = struct.unpack(">IIBB", data[pos + 8:pos + 18])
        elif typ == b"IDAT":
            idat += data[pos + 8:pos + 8 + ln]
        elif typ == b"IEND":
            break
        pos += 12 + ln
    assert bit == 8 and color in (2, 6), f"{rel}: PNG bit {bit} color {color}"
    nch = 4 if color == 6 else 3
    raw = zlib.decompress(idat)
    stride = w * nch
    rows, prev, p = [], bytearray(stride), 0
    for _y in range(h):
        flt = raw[p]
        line = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        if flt == 1:
            for i in range(nch, stride):
                line[i] = (line[i] + line[i - nch]) & 255
        elif flt == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 255
        elif flt == 3:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif flt == 4:
            for i in range(stride):
                a = line[i - nch] if i >= nch else 0
                b, c = prev[i], (prev[i - nch] if i >= nch else 0)
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc
                                      else b if pb <= pc else c)) & 255
        rows.append(line)
        prev = line
    if nch == 3:
        return w, h, [[255] * w for _ in range(h)]
    return w, h, [[line[i * 4 + 3] for i in range(w)] for line in rows]


# ---- maps ------------------------------------------------------------------------
MAPS = [
    "maps/meadow.txt",
    "maps/overworld.txt",
    "maps/overworld_bright.txt",
    "maps/town.txt",
    "maps/town_fest.txt",
    "maps/lanternwood.txt",
    "maps/house.txt",
    "maps/downstairs.txt",
    "maps/hall.txt",
    "maps/sickroom.txt",
    "maps/library.txt",
    "maps/bluff.txt",
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
    "maps/overworld_bright.txt": ("tilesets/overworld_bright_layout.txt",
                                  "tilesets/overworld_bright_tiles.png",
                                  "tilesets/overworld_bright_tiles.tres"),
    "maps/town.txt": ("tilesets/town_layout.txt",
                      "tilesets/town_tiles.png",
                      "tilesets/town_tiles.tres"),
    "maps/lanternwood.txt": ("tilesets/lanternwood_layout.txt",
                             "tilesets/lanternwood_tiles.png",
                             "tilesets/lanternwood_tiles.tres"),
    "maps/town_fest.txt": ("tilesets/town_fest_layout.txt",
                           "tilesets/town_fest_tiles.png",
                           "tilesets/town_fest_tiles.tres"),
    "maps/hall.txt": ("tilesets/hall_layout.txt", "tilesets/hall_tiles.png",
                      "tilesets/hall_tiles.tres"),
    "maps/sickroom.txt": ("tilesets/sickroom_layout.txt",
                          "tilesets/sickroom_tiles.png",
                          "tilesets/sickroom_tiles.tres"),
    "maps/library.txt": ("tilesets/library_layout.txt",
                         "tilesets/library_tiles.png",
                         "tilesets/library_tiles.tres"),
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
# maps/town.txt is intentionally absent: its buildings + trees are now Tier-3
# y-sorted World sprites (not upper-layer tiles), so its upper layer is empty
# and the z-order checks below short-circuit for it (the invisible-wall +
# T3-coverage lint carry the load). town_fest still bakes them, so it stays.
UPPER_REQUIRED = {"maps/overworld.txt", "maps/overworld_bright.txt",
                  "maps/house.txt", "maps/downstairs.txt", "maps/hall.txt",
                  "maps/sickroom.txt", "maps/library.txt"}
# 24x24 travel chibi, figure <=1 tile tall
CHIBI_MAPS = {"maps/overworld.txt", "maps/overworld_bright.txt"}
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
    "maps/town_fest.txt": "tilesets/town_fest_props.txt",
    "maps/lanternwood.txt": "tilesets/lanternwood_props.txt",
    "maps/hall.txt": "tilesets/hall_props.txt",
    "maps/sickroom.txt": "tilesets/sickroom_props.txt",
    "maps/library.txt": "tilesets/library_props.txt",
}
T3_CHARS = {}                          # map_rel -> chars whose art is y-sorted
T3_PROPS = {}                          # map_rel -> parsed rows (coverage lint)
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
        top = None
        each = False
        for opt in parts[4:]:
            if opt.startswith("hframes="):
                hframes = int(opt.split("=", 1)[1])
            elif opt == "each":
                each = True
            elif opt.startswith("anchor=top:"):
                top = int(opt.split(":", 1)[1])
            elif not opt.startswith("base_inset="):
                ok, detail = False, f"unknown option {opt!r}"
        chars = parts[2]
        if not any(ch in chars for row in mm.rows for ch in row):
            ok, detail = False, f"no {chars!r} cells in the map"
        dims = png_size(os.path.join("assets", "tilesets", parts[3]))
        if dims is None or dims[0] % hframes:
            ok, detail = False, f"png {dims}, hframes {hframes}"
        if ok:
            T3_PROPS.setdefault(map_rel, []).append(
                dict(name=parts[1], chars=chars, png=parts[3],
                     top=top, hframes=hframes, each=each))
        check(f"assets/{props_rel}: {parts[1]}", ok, detail)


def t3_components(mm, chars, each):
    """The prop's footprint groups, mirroring prop_spawner: 4-connected
    components for `each`, else one group of every chars cell."""
    cells = [(x, y) for y in range(mm.rows_n) for x in range(mm.cols)
             if mm.at(x, y) in chars]
    if not each:
        return [cells]
    pending = set(cells)
    comps = []
    for seed in cells:
        if seed not in pending:
            continue
        pending.discard(seed)
        comp = [seed]
        i = 0
        while i < len(comp):
            cx, cy = comp[i]
            i += 1
            for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if n in pending:
                    pending.discard(n)
                    comp.append(n)
        comps.append(comp)
    return comps


T3_COVER_MIN = 0.20   # a footprint cell keeps its solid map cell only if the
                      # prop's frame-0 art covers >= 20% of the 16px square
                      # (measured floor: legit bases ~25-46%, true walls 0%)


def t3_covered_cells(mm, props):
    """Solid footprint cells the prop art actually covers — the per-cell
    Tier-3 exemption for the invisible-wall lint (placement math mirrors
    scene/prop_spawner.gd: art centered on the group's x, bottom on its
    south edge unless anchor=top)."""
    covered = set()
    for prop in props:
        pw, ph, alpha = png_alpha(os.path.join("assets", "tilesets", prop["png"]))
        fw = pw // prop["hframes"]
        for comp in t3_components(mm, prop["chars"], prop["each"]):
            x0 = min(c[0] for c in comp)
            x1 = max(c[0] for c in comp)
            y0 = min(c[1] for c in comp)
            y1 = max(c[1] for c in comp)
            ax0 = (x0 + x1 + 1) * ZONE_TILE / 2.0 - fw / 2.0
            ay0 = y0 * ZONE_TILE + prop["top"] if prop["top"] is not None \
                else (y1 + 1) * ZONE_TILE - ph
            for (cx, cy) in comp:
                n = 0
                for py in range(ZONE_TILE):
                    sy = int(cy * ZONE_TILE + py - ay0)
                    if not 0 <= sy < ph:
                        continue
                    arow = alpha[sy]
                    for px_ in range(ZONE_TILE):
                        sx = int(cx * ZONE_TILE + px_ - ax0)
                        if 0 <= sx < fw and arow[sx] > 0:
                            n += 1
                if n >= T3_COVER_MIN * ZONE_TILE * ZONE_TILE:
                    covered.add((cx, cy))
    return covered

# ---- invisible walls (silhouette-fit rule, DESIGN.md) ---------------------------------
# A solid cell whose art dedupes to a tile also used on open walkable ground
# reads as walkable but blocks — the deduped atlas makes this exact: an
# art-free prop-footprint corner shares its atlas tile with plain fabric.
# Only faces a body can press count (4-adjacent to a walkable cell). The
# Tier-3 exemption is per CELL (2026-07-12): a footprint cell is exempt only
# where the y-sorted prop art covers >= T3_COVER_MIN of its square — an
# art-free corner must be retyped walkable (the O/L/U twins).
print("invisible walls:")
for map_rel, layers in LAYERS.items():
    mm = maps[map_rel]
    lower = [row.split() for row in layers["lower"]]
    upper = {(x, y) for y, row in enumerate(layers["upper"])
             for x, tok in enumerate(row.split()) if tok != "-"}
    covered = t3_covered_cells(mm, T3_PROPS.get(map_rel, []))

    def solid(x, y, mm=mm):
        ch = mm.at(x, y)
        return mm.legend[ch]["solid"] if ch else True

    walk_toks = {lower[y][x] for y in range(mm.rows_n) for x in range(mm.cols)
                 if not solid(x, y)}
    bad = [(x, y) for y in range(mm.rows_n) for x in range(mm.cols)
           if solid(x, y) and (x, y) not in covered
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
    "scene/lanternwood.tscn": "maps/lanternwood.txt",
    "scene/town_fest.tscn": "maps/town_fest.txt",
    "scene/town_thesis.tscn": "maps/town_fest.txt",
    "scene/house_thesis.tscn": "maps/house.txt",
    "scene/hall.tscn": "maps/hall.txt",
    "scene/sickroom.tscn": "maps/sickroom.txt",
    "scene/library.tscn": "maps/library.txt",
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
    "assets/basil_gen.png": (6 * ZONE_CELL, 10 * ZONE_CELL),
    "assets/fuji_gen.png": (6 * ZONE_CELL, 10 * ZONE_CELL),
    # the Ebb-night npc cast: a layout change here must fail the build, or
    # scene frame_cols would slice AtlasTexture regions off the sheet edge
    "assets/npc_fuji_gen.png": (10 * ZONE_CELL, ZONE_CELL),
    "assets/npc_hare_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_beaver_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_foxkid_gen.png": (6 * ZONE_CELL, ZONE_CELL),
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
    # the Prologue A cast (assets/_gen_prologue_sprites.py)
    "assets/kid_basil_gen.png": (6 * ZONE_CELL, 5 * ZONE_CELL),
    "assets/npc_sage_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_schweinler_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_kitty_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_sheep_gen.png": (8 * ZONE_CELL, ZONE_CELL),
    "assets/npc_owl_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_goose_gen.png": (8 * ZONE_CELL, ZONE_CELL),
    "assets/npc_mouse_gen.png": (8 * ZONE_CELL, ZONE_CELL),
    "assets/prologue_fx.png": (256, 32),
    "assets/accident_kitty_gen.png": (5 * ZONE_CELL, ZONE_CELL),
    "assets/accident_atv_gen.png": (5 * ZONE_CELL, ZONE_CELL),
    "assets/accident_bike_down_gen.png": (ZONE_CELL, ZONE_CELL),
    "assets/accident_bg.png": (384, 216),
    # thesis-day cast (Prologue B) + Mom (the A pacing pass)
    "assets/npc_mom_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_schweinler_adult_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_badger_gen.png": (8 * ZONE_CELL, ZONE_CELL),
    "assets/npc_stork_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_kitty_bed_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_kittymom_gen.png": (6 * ZONE_CELL, ZONE_CELL),
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
    "entities/enemies/big_slime_frames.tres": ("assets/slime_big_gen.png", 36),
    "entities/player/overworld_basil_frames.tres": ("assets/overworld_basil.png", OW_CELL),
    "entities/player/overworld_fuji_frames.tres": ("assets/overworld_fuji.png", OW_CELL),
    "entities/kid/kid_basil_frames.tres": ("assets/kid_basil_gen.png", ZONE_CELL),
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
