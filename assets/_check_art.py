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
from _tilekit import check_strata, strata_of

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


def png_pixels(rel):
    """Decode an 8-bit RGB(A) non-interlaced PNG -> (w, h, nch, raw rows).
    Stdlib-only, mirror of _core's writer. `png_alpha` narrows this to the
    alpha plane for the coverage lints; the JOIN lint needs the COLOURS too,
    because "are these two sprites the same material at the seam" is the only
    cheap mechanical test for a join being a continuation and not an
    abutment."""
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
    return w, h, nch, rows


def png_alpha(rel):
    """(w, h, alpha rows) — used by the T3 coverage lints to measure how much
    of a footprint cell the y-sorted prop art actually covers."""
    w, h, nch, rows = png_pixels(rel)
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
    "maps/academy.txt",
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

# ---- THE BYTE-LOCK (2026-07-29) --------------------------------------------------------
# Some maps exist as ERA PAIRS that must stay in lockstep cell for cell: the
# drained/bright town and the drained/bright overworld. Only the legend and the
# anchor blocks may legitimately differ — town_fest's Academy door opens, the
# bright overworld's markers move — so the check is on the GRID SECTIONS only.
#
# This invariant was prose in FOUR places (CLAUDE.md standing rule 7,
# assets/CLAUDE.md, the map-authoring skill, both map headers) and nowhere in
# code, which made it the single most likely way this project breaks silently:
# edit one twin, forget the other, and the two eras diverge with no error, no
# lint and no visible symptom until somebody walks through a wall that only
# exists before the Ebb.
print("byte-lock (era twins):")
TWINS = [("maps/town.txt", "maps/town_fest.txt"),
         ("maps/overworld.txt", "maps/overworld_bright.txt")]
for a_rel, b_rel in TWINS:
    ga, gb = maps[a_rel].rows, maps[b_rel].rows
    same = ga == gb
    where = ""
    if not same:
        if len(ga) != len(gb):
            where = f"{len(ga)} rows vs {len(gb)}"
        else:
            diffs = [(y, [x for x in range(min(len(ra), len(rb)))
                          if ra[x] != rb[x]])
                     for y, (ra, rb) in enumerate(zip(ga, gb)) if ra != rb]
            where = f"rows {[(y, cs[:4]) for y, cs in diffs[:3]]}"
    check(f"{a_rel} <-> {b_rel} grids identical", same, where)

# ---- the strata rule, RE-RUN FROM THE SHIPPED ARTIFACT ---------------------------------
# The stratum lives in the map txt's legend, so this needs no generator, no
# palette entry and no atlas — which is the point. A hand-edit of a map txt with
# no regen still fails the build here, and a hand-edit is exactly the edit most
# likely to fuse two walkable storeys into one. The rule itself is the kit's
# check_strata(), imported rather than copied: two implementations of "the
# storeys must be disjoint" would eventually disagree, and the one that
# disagreed quietly would be this one.
print("strata:")
for rel, m in maps.items():
    names = sorted(m.strata())
    try:
        check_strata(m, rel)
        ok, detail = True, ""
    except AssertionError as e:
        ok, detail = False, str(e)
    check(f"{rel} strata disjoint ({'+'.join(names)})", ok, detail)

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
    # academy was in MAPS and PROPS but NOT here, so "layout dims match the map",
    # "atlas refs in range" and ".tres declares every tile" never ran on it — the
    # three that catch a footprint change that was not regenerated, which is the
    # single most likely way to break this precinct.
    "maps/academy.txt": ("tilesets/academy_layout.txt", "tilesets/academy_tiles.png",
                         "tilesets/academy_tiles.tres"),
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
    "maps/bluff.txt": ("tilesets/bluff_layout.txt", "tilesets/bluff_tiles.png",
                       "tilesets/bluff_tiles.tres"),
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
# UPPER_REQUIRED is the "this map MUST have a non-empty upper layer" list, and the
# towns are absent from it because their buildings and trees are Tier-3 y-sorted
# World sprites rather than upper-layer tiles, so they are ALLOWED an empty one.
# That is not the same as HAVING one, and the comment here used to claim it was —
# it said the towns' upper layers were empty and the z-order checks below
# short-circuited. They are not and it does not: both town maps carry 9 upper
# cells (the spans' near rails), so the support / corridor-cap / ridge-placement
# lints DO run on them, which is what you want. Only the claim was wrong.
# maps/bluff.txt is genuinely empty up there: its one prop (the windswept tree) is
# a Tier-3 sprite and nothing else is drawn over a body.
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
    # THE ACADEMY WAS NEVER IN EITHER TABLE (found 2026-07-30). The whole
    # precinct — a 64x48 map with six Tier-3 props on it — shipped without
    # the invisible-wall, walk-behind-visibility, floating-art or manifest
    # lints ever looking at it. A map that is not in MAPS is not "passing";
    # it is absent, and the summary line says "all checks passed" either way.
    "maps/academy.txt": "tilesets/academy_props.txt",
    "maps/hall.txt": "tilesets/hall_props.txt",
    "maps/sickroom.txt": "tilesets/sickroom_props.txt",
    "maps/library.txt": "tilesets/library_props.txt",
    "maps/bluff.txt": "tilesets/bluff_props.txt",
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
        if parts[0] == "mask":
            # a mask_band depth strip: explicit pixel rect, no map chars, and
            # no footprint for the T3 coverage lint to measure — but the PNG
            # itself is still a load-bearing file prop_spawner will load(), so
            # verify it exists and its rect parses (2026-08-01: these rows
            # used to be format-checked only, and a renamed or hand-cleaned
            # mask PNG shipped silently as a missing-texture strip)
            ok = len(parts) == 5
            detail = ""
            if ok:
                mdims = png_size(os.path.join("assets", "tilesets", parts[1]))
                if mdims is None:
                    ok, detail = False, f"missing png {parts[1]}"
                else:
                    try:
                        int(parts[2]); int(parts[3]); int(parts[4])
                    except ValueError:
                        ok, detail = False, f"non-integer rect {parts[2:5]}"
            check(f"{props_rel} mask row well-formed", ok, detail or ln)
            continue
        ok = len(parts) >= 4 and parts[0] == "prop"
        if ok:
            T3_CHARS.setdefault(map_rel, set()).update(parts[2])
        detail = ""
        hframes = 1
        top = None
        inset = 0
        each = False
        for opt in parts[4:]:
            if opt.startswith("hframes="):
                hframes = int(opt.split("=", 1)[1])
            elif opt == "each":
                each = True
            elif opt.startswith("anchor=top:"):
                top = int(opt.split(":", 1)[1])
            elif opt.startswith("base_inset="):
                inset = int(opt.split("=", 1)[1])
            else:
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
                     top=top, inset=inset, hframes=hframes, each=each))
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

# ---- walk-behind visibility: the MIRROR of the T3 coverage rule (2026-07-29) ----------
# A Tier-3 prop is y-sorted at its footprint's SOUTH edge (prop_spawner.gd:
# sort_y = rect.end.y - base_inset - PLAYER_FEET; a body's key is body.y and its
# feet draw at body.y + PLAYER_FEET). So the prop draws OVER any body whose feet
# line is north of its base line — i.e. every WALKABLE cell inside a prop's own
# footprint is drawn BEHIND that prop. That is the walk-behind idiom and it is
# the whole point of it: a tree CROWN, a lamp MANTLE, a leaf mass is perforated
# or partial art, and being partly hidden is exactly what reads as depth.
#
# It is a DEFECT when the art over that cell is an OPAQUE CONTINUOUS MASS,
# because then the body doesn't read as "behind" — it is GONE. Measured in
# town.txt: the great trunk is a ~35px shaft centred in a 48px canvas over a 3x5
# footprint whose top two rows are the walkable `J` crown, so the footprint's
# CENTRE column is 100% covered and a body standing there has ZERO visible
# pixels (verified in-engine at cell (41,18)).
#
# THE MEASUREMENT IS THE FIGURE, NOT THE CELL, and it has to be: per-CELL
# coverage cannot separate the two cases. Both the trunk's centre column AND the
# bough leaves' own walkable cell measure 100% of their 16x16 square, so any
# single-cell threshold either misses the trunk or condemns the leaves. Against
# the 22x38 FIGURE the clusters part with 15 points of daylight — everything
# that ships today hides <= 84.9% of a body (the trunk's own crown row at
# (41,17) 84.9%, the bough leaves 84.1%, the library counter 75.5%, the
# gateposts 72%, the conifer crowns <= 69.9%) and the defect hides 100.0%.
#
# The body is placed at MapData.cell_center — the position every anchor, spawn
# and staged NPC actually lands one on a cell.
PLAYER_FEET = 20        # scene/prop_spawner.gd: feet sit at node.y + 20
T3_HIDE_MAX = 0.90      # a walkable footprint cell must leave >= 10% of a body
                        # showing (measured ceiling of the legit walk-behinds:
                        # 84.9%; the one true defect: 100.0%)


def figure_px():
    """Basil's planted idle_down silhouette as pixel offsets from his node
    origin — the sheet's cell (0,0), the 22x38 figure inside the 48x48 cell.
    Read rather than hard-coded so a redrawn cast re-measures itself."""
    _, _, alpha = png_alpha("assets/basil_gen.png")
    half = ZONE_CELL // 2
    return [(x - half, y - half) for y in range(ZONE_CELL)
            for x in range(ZONE_CELL) if alpha[y][x] > 0]


def t3_hidden_cells(mm, props, figure):
    """Walkable footprint cells where the prop's frame-0 art swallows more than
    T3_HIDE_MAX of a body standing on them -> [(cell, prop_name, fraction)].
    Placement math mirrors scene/prop_spawner.gd, base_inset included: it moves
    the y-sort baseline (so it decides WHICH rows are walk-behind at all) but
    never the art, which anchors on the footprint's south edge or anchor=top."""
    out = []
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
            sort_y = (y1 + 1) * ZONE_TILE - prop["inset"] - PLAYER_FEET
            # SCAN THE ART RECT, NOT THE FOOTPRINT — the 2026-07-30 blind spot.
            # A Tier-3 sprite may be taller or wider than the cells it declares:
            # `top=0` with a long sprite hangs art SOUTH of the footprint, and a
            # bottom-anchored sprite that overshoots reaches NORTH of it. The cells
            # it covers out there belong to no prop component, so iterating `comp`
            # could never see them — and that is exactly where the defect landed.
            # A great trunk's art overshot one row up into its ring's walkable north
            # arc and measured ZERO visible pixels on four decks in two eras while
            # this lint printed all clear. The rule could not see the case it exists
            # to catch, which is worse than not having it.
            hits = []
            for cy in range(max(0, int(ay0 // ZONE_TILE)),
                            min(mm.rows_n, int((ay0 + ph) // ZONE_TILE) + 1)):
                for cx in range(max(0, int(ax0 // ZONE_TILE)),
                                min(mm.cols, int((ax0 + fw) // ZONE_TILE) + 1)):
                    if mm.legend[mm.at(cx, cy)]["solid"]:
                        continue
                    ox = cx * ZONE_TILE + ZONE_TILE / 2.0
                    oy = cy * ZONE_TILE + ZONE_TILE / 2.0
                    if oy >= sort_y:
                        continue      # the body sorts in FRONT: nothing hidden
                    n = 0
                    for (dx, dy) in figure:
                        sx, sy = int(ox + dx - ax0), int(oy + dy - ay0)
                        if 0 <= sx < fw and 0 <= sy < ph and alpha[sy][sx] > 0:
                            n += 1
                    hits.append(((cx, cy), n / float(len(figure))))
            # THE PASS-BEHIND EXEMPTION. Walking fully behind a great tree is the
            # effect this whole town is built for, and Basil's hall flee is staged
            # behind a curtain leg on purpose — so vanishing is not by itself a
            # defect. What IS a defect is vanishing for LONG ENOUGH TO GET LOST,
            # which is what v1 shipped: a ring deck running clear under an opaque
            # shaft, every cell of the crossing invisible, no way over that did not
            # leave the player gone.
            #
            # So the test is the length of the hidden RUN, not the fact of hiding.
            # Up to two cells is a step you pass through; three or more is a place
            # you disappear into. The cell must also have a way OUT — some
            # 4-neighbour that is not itself hidden — or a two-cell run against a
            # wall would slip through.
            dark = {c for c, fr in hits if fr > T3_HIDE_MAX}
            for (cx, cy), frac in hits:
                if (cx, cy) not in dark:
                    continue
                run = 1
                d = 1
                while (cx - d, cy) in dark:
                    run += 1
                    d += 1
                d = 1
                while (cx + d, cy) in dark:
                    run += 1
                    d += 1
                out_of_it = any((cx + ax, cy + ay) not in dark
                                for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if run <= 2 and out_of_it:
                    continue          # a pass-behind, not a trap
                out.append(((cx, cy), prop["name"], frac))
    return out


print("walk-behind visibility:")
FIGURE = figure_px()
for map_rel in PROPS:
    hidden = t3_hidden_cells(maps[map_rel], T3_PROPS.get(map_rel, []), FIGURE)
    check(f"{map_rel} walk-behind cells keep a body visible", not hidden,
          "opaque mass over walkable footprint cells "
          + ", ".join(f"{c} {n} {f * 100:.0f}%" for c, n, f in sorted(hidden)[:6])
          + " — retype it solid (and give it a walkable TWIN elsewhere if the "
            "cell has to be crossed), or perforate the art")

# ---- JOINS: two sprites that are meant to be ONE OBJECT (2026-08-02) ------------------
# The three bugs that produced this lint were all at the SAME seam — Alembic's great
# trees, where the crown prop and the trunk-face prop have to read as one tree — and
# every one of them rendered, deduped and passed every check above:
#
#   1. the crown's leaf mass was CUT FLAT by its own canvas (a tree in a box);
#   2. fixing that by padding the canvas moved the hem UP off the trunk, and bare deck
#      showed in the daylight between them;
#   3. closing that gap left the two sprites ABUTTING along a line, which reads as a
#      crop however exactly the line is placed.
#
# Nothing in this file was looking at seams. The z-order lints ask "is a body visible"
# and "does a solid cell look walkable"; they cannot see two pieces of scenery that are
# supposed to be continuous and are not. So: name the pairs, and check them.
#
# The lower prop's own top row is the SEAM. Two things must hold along it:
#
#   NO DAYLIGHT   — for every column of the seam, the upper art must be opaque for
#                   `overlap` rows above it. This is bug 2, and it is what the eye
#                   reads as a gap.
#   CONTINUATION  — the upper art's pixel just above the seam must be the SAME PIXEL as
#                   the lower art's own top pixel, for most columns. That is bug 3, and
#                   it is the whole difference between "the crown carries the trunk's
#                   shaft behind its leaves" and "the leaves stop where the trunk
#                   starts". Same ramp + same half-width + same banding law => the same
#                   colour falls out per column, so exact equality is a fair test; the
#                   grooves are hashed on y and legitimately differ, which is what the
#                   threshold is for. MEASURED on all four of Alembic's trees: 58/61
#                   columns (0.95) with the crown carrying the shaft, 0/61 (0.00)
#                   without it. Both failure modes were re-introduced and confirmed to
#                   fail this lint before it was called done.
JOINS = {
    "maps/town.txt": [("Crown", "TrunkRing", 6)],
    "maps/town_fest.txt": [("Crown", "TrunkRing", 6)],
}
JOIN_SAME_MIN = 0.60


def t3_art_placements(mm, prop):
    """(frame w, png h, nch, rows, [(art x, art y), ...]) for a prop — one art
    origin per component, mirroring scene/prop_spawner.gd exactly (the same
    math t3_covered_cells uses: centred on the component's x, bottom on its
    south edge unless anchor=top, which is SIGNED)."""
    pw, ph, nch, rows = png_pixels(os.path.join("assets", "tilesets", prop["png"]))
    fw = pw // prop["hframes"]
    places = []
    for comp in t3_components(mm, prop["chars"], prop["each"]):
        x0 = min(c[0] for c in comp)
        x1 = max(c[0] for c in comp)
        y0 = min(c[1] for c in comp)
        y1 = max(c[1] for c in comp)
        ax = (x0 + x1 + 1) * ZONE_TILE / 2.0 - fw / 2.0
        ay = y0 * ZONE_TILE + prop["top"] if prop["top"] is not None \
            else (y1 + 1) * ZONE_TILE - ph
        places.append((int(round(ax)), int(round(ay))))
    return fw, ph, nch, rows, sorted(places)


def _texel(rows, nch, w, h, x, y):
    """The opaque pixel at (x, y) as an RGB tuple, or None off-canvas/clear."""
    if not (0 <= x < w and 0 <= y < h):
        return None
    line = rows[y]
    if nch == 4 and line[x * 4 + 3] == 0:
        return None
    return tuple(line[x * nch:x * nch + 3])


def join_faults(mm, props, upper_name, lower_name, overlap):
    """[(detail string), ...] for one declared join — empty when the two props
    read as one object at every seam in the map."""
    by = {p["name"]: p for p in props}
    if upper_name not in by or lower_name not in by:
        return [f"no prop named {upper_name!r}/{lower_name!r} in the manifest"]
    ufw, uph, unch, urows, uplaces = t3_art_placements(mm, by[upper_name])
    lfw, lph, lnch, lrows, lplaces = t3_art_placements(mm, by[lower_name])
    out = []
    for (lx, ly) in lplaces:
        # the upper piece this lower one belongs to: spans its centre column and
        # sits above it. Pairing by geometry rather than by index, so a tree
        # moving in the map txt cannot silently pair a crown with its neighbour.
        centre = lx + lfw // 2
        cands = [(uy, ux) for (ux, uy) in uplaces
                 if ux <= centre < ux + ufw and uy < ly]
        if not cands:
            out.append(f"the {lower_name} at ({lx},{ly}) has no {upper_name} over it")
            continue
        uy, ux = max(cands)
        seam = [x for x in range(lfw)
                if _texel(lrows, lnch, lfw, lph, x, 0) is not None]
        if not seam:
            continue                     # nothing on the lower art's top row
        gaps, same = [], 0
        for x in seam:
            wx = lx + x
            above = [_texel(urows, unch, ufw, uph, wx - ux, ly - 1 - k - uy)
                     for k in range(overlap)]
            if any(p is None for p in above):
                gaps.append(wx)
            elif above[0] == _texel(lrows, lnch, lfw, lph, x, 0):
                same += 1
        if gaps:
            out.append(f"daylight over the {lower_name} at ({lx},{ly}): "
                       f"{len(gaps)}/{len(seam)} seam columns show through "
                       f"(x={gaps[0]}..{gaps[-1]}) — the {upper_name} does not "
                       f"reach it")
        elif same < JOIN_SAME_MIN * len(seam):
            out.append(f"the {upper_name}/{lower_name} seam at ({lx},{ly}) is an "
                       f"ABUTMENT: only {same}/{len(seam)} columns continue the "
                       f"same material — the upper sprite has to carry the lower "
                       f"one's own art behind it, not stop on top of it")
    return out


print("joins (two sprites, one object):")
for map_rel, pairs in JOINS.items():
    for upper, lower, overlap in pairs:
        bad = join_faults(maps[map_rel], T3_PROPS.get(map_rel, []),
                          upper, lower, overlap)
        check(f"{map_rel} {upper} reads as one object with {lower}", not bad,
              "; ".join(bad[:3]))

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
    "scene/academy.tscn": "maps/academy.txt",
    "scene/town_fest.tscn": "maps/town_fest.txt",
    "scene/town_thesis.tscn": "maps/town_fest.txt",
    "scene/house_thesis.tscn": "maps/house.txt",
    "scene/hall.tscn": "maps/hall.txt",
    "scene/sickroom.tscn": "maps/sickroom.txt",
    "scene/library.tscn": "maps/library.txt",
    "scene/bluff.tscn": "maps/bluff.txt",
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
    # row 10 is the LADDER CLIMB (2026-07-30) — Alembic is reached by rope
    # ladder and a body on one used to play walk_up, i.e. slide up the rungs
    "assets/basil_gen.png": (6 * ZONE_CELL, 11 * ZONE_CELL),
    "assets/fuji_gen.png": (6 * ZONE_CELL, 11 * ZONE_CELL),
    # THE VILLAGER SHEET CONTRACT IS 10 COLUMNS. Row 0 is the POSE row:
    #   [0,1] idle_down · [2,3] act · [4,5] emote · [6,7] back · [8,9] side
    # and the side pair is drawn facing LEFT (npc.gd flips it for east).
    # 6-column sheets are LEGACY BUT LEGAL — npc.gd builds only the clips whose
    # columns exist, so an old 288x48 villager simply has no back/side and never
    # turns. A NEW villager should be 480 wide; anything that walks or is walked
    # around MUST be, or it glides through the scene face-on.
    #
    # ROWS 1-3 ARE THE WALK CYCLE (2026-07-29) and they are OPTIONAL — one
    # direction per row, six cells each, cols 6-9 padded empty:
    #   row 1 walk_down x6 · row 2 walk_up x6 · row 3 walk_side x6 (faces LEFT)
    # i.e. a walking villager is 480x192. That is the same contract the party
    # sheets use (direction is the ROW), which is why the proven 6-frame stride
    # tables are reused verbatim. npc.gd gates these on the sheet's real HEIGHT
    # and NOT on frame_cols, so a sheet that grows rows starts walking with no
    # scene edit — a 48px-tall sheet stays legal and stays a statue.
    # A layout change here must fail the build either way, or scene frame_cols
    # would slice AtlasTexture regions off the sheet edge.
    "assets/npc_fuji_gen.png": (10 * ZONE_CELL, ZONE_CELL),
    # the Lanternwood street — walk rows, so the Ebb night is not three statues
    "assets/npc_hare_gen.png": (10 * ZONE_CELL, 4 * ZONE_CELL),
    "assets/npc_beaver_gen.png": (10 * ZONE_CELL, 4 * ZONE_CELL),
    "assets/npc_foxkid_gen.png": (10 * ZONE_CELL, 4 * ZONE_CELL),
    # Mayor Hollis of Lanternwood — 10 columns from the start (2026-07-29).
    # He does NOT wander (motion_probe pins him to his own step); the walk rows
    # are for the one staged walk out of the moot hall door.
    "assets/npc_mayor_gen.png": (10 * ZONE_CELL, 4 * ZONE_CELL),
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
    "assets/kid_basil_gen.png": (6 * ZONE_CELL, 6 * ZONE_CELL),
    # the three CHILDREN widened to the 10-column contract (2026-07-29) so they
    # stop gliding around the recital and the schoolyard permanently face-on
    "assets/npc_sage_gen.png": (10 * ZONE_CELL, ZONE_CELL),
    "assets/npc_schweinler_gen.png": (10 * ZONE_CELL, ZONE_CELL),
    "assets/npc_kitty_gen.png": (10 * ZONE_CELL, ZONE_CELL),
    "assets/npc_sheep_gen.png": (8 * ZONE_CELL, ZONE_CELL),
    "assets/npc_owl_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_goose_gen.png": (8 * ZONE_CELL, ZONE_CELL),
    "assets/npc_mouse_gen.png": (8 * ZONE_CELL, ZONE_CELL),
    "assets/prologue_fx.png": (256, 32),
    "assets/accident_kitty_gen.png": (5 * ZONE_CELL, ZONE_CELL),
    "assets/accident_atv_gen.png": (5 * ZONE_CELL, ZONE_CELL),
    "assets/accident_bike_down_gen.png": (ZONE_CELL, ZONE_CELL),
    "assets/accident_bg.png": (384, 216),
    # thesis-day cast (Prologue B) + Mom (the A pacing pass). Mom got the walk
    # rows so she can WORK her kitchen instead of standing in it.
    "assets/npc_mom_gen.png": (10 * ZONE_CELL, 4 * ZONE_CELL),
    # both grew to 10 cols + the walk rows on 2026-07-30 — see the accident
    "assets/npc_schweinler_adult_gen.png": (10 * ZONE_CELL, 4 * ZONE_CELL),
    "assets/npc_badger_gen.png": (10 * ZONE_CELL, 4 * ZONE_CELL),
    "assets/npc_stork_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_kitty_bed_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    "assets/npc_kittymom_gen.png": (6 * ZONE_CELL, ZONE_CELL),
    # were never dimension-linted at all until 2026-07-29 — the gap that let a
    # sheet change shape without the build noticing
    "assets/npc_kitty_adult_gen.png": (10 * ZONE_CELL, ZONE_CELL),
    "assets/bluff_kiss_gen.png": (3 * 96, 96),
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
