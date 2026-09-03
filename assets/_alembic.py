#!/usr/bin/env python3
"""THE ALEMBIC RECIPES — everything the eras of one scene do identically, which
is everything except the palette and the glow.

WHY THIS MODULE EXISTS. `_check_art.py` byte-locks each scene's era map GRIDS,
so the eras cannot disagree about where a plank is. Nothing locked the two
GENERATORS once, and they were ~350 lines of "the same recipe" maintained by
hand in parallel — which had already gone wrong (the fest twin hand-inlined
stamp_columns' loop and so had NO run-height assert at all, in the era where
three chapters of cutscenes walk). The grid being byte-identical is worth
little if one era stamps a band the other doesn't.

SINCE THE 2026-08-23 TWO-SCENE SPLIT there are TWO recipes here, one town:

  build(map_name, scene_key, glow)         — THE FLOOR (town.txt / town_fest.txt):
      the forest-floor village in permanent green dusk. The four great trunks
      are bare shafts baked from row 0 down to their buttress feet, running off
      the top of the map; the rope ladders are real climbable `z` runs that end
      at a TRAVEL MOUTH (the canopy is another scene now).

  build_canopy(map_name, scene_key, glow)  — THE BOUGHS (canopy.txt / canopy_fest.txt):
      four ring decks joined by rope bridges over THE DROP — the void between
      the platforms, repainted as the town itself thirty feet down.

Each era is a thin config: a palette scene key and a glow painter. If a future
era needs to differ in a third way, add a knob — do not fork the file.

See the map headers for the per-grid geometry and docs/DESIGN.md ->
"STACKED WALKABLE STOREYS" for the doctrine (including why the old
REJECTED-two-scene-split bullet was repealed, and what answers its objections).
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, lerp
from _overworld_tiles import OverWorld, T, STRUCT_TERRAIN
from _tilekit import sprite_img, VOID, IRON
from _town_props import (town_cottage, town_shop, town_well, town_lamp,
                         town_stall, town_fountain, town_shade_tree)
from _culture_props import notice_board, owl_roost, hook_lantern, PAPER_STOCK
from _tree_props import (tree_ring, ring_cells, ring_geom, trunk_face,
                         rope_ladder, understory, great_trunk, great_crown,
                         tree_bridge, tree_platform, BARK)

# ---- THE TREE GEOMETRY, in one place ------------------------------------------------
# The ring block is 12 x 9 cells and its walkable cells are the rasterization of
# the very ellipse tree_ring draws (`ring_cells`); the trunk is 4 columns with
# the 2-column rope ladder inside them. The FLOOR map carries only the trunk
# columns (`j`, feet `!`, rungs `z`); the CANOPY map carries the whole block.
RING_W, RING_H = 192, 144          # the tree block: 12 x 9 cells
RING_HOLE = (21, 11)               # the trunk's cross-section through the boards
RING_FASCIA = 18                   # the crescent's depth at due south
# Every char a canopy ring block's BORDER is made of. `R` is the walkable rim
# twin at the ladder landing; `E` is the walkable rim twin at a BRIDGE GATE
# (2026-08-23) — same terrain (`ringedge` -> leaf), the O/U/L idiom, and it has
# to be in the component set or a double-bridged ring's border breaks into two
# arcs and place_each stretches a rail sprite over each.
RING_CHARS = "yRE"
RING_CROWN_ROWS = 1                # block rows the crown covers OPAQUELY
TRUNK_W = 64                       # 4 cells
TRUNK_C0, LADDER_C0 = 4, 5         # ...at block col 4, its ladder at block col 5
CROWN_W, CROWN_H = 224, 128        # see build_canopy's crown comment
RUNG_OVER = 4                      # floor map: painted rungs continuing up the
                                   # bark above the walkable run — the ladder
                                   # visibly goes ON up past the travel mouth

# glow clip sets (light does not spill down a vertical face) — per recipe,
# because the two maps have different vertical-face inventories
FACES_FLOOR = "j!"
FACES_CANOPY = "yJjRE"


def lantern_cells(m, chars, salt):  # kept for import compatibility; no callers
    return []


def shaded(ramp, t0=0.40, t1=0.12):
    """A ramp pulled toward the void — the SAME timber, seen edge-on.

    A vertical face is darker than the surface it hangs off. That is the whole
    idea, and it costs one ramp. The pull is GRADED — hard at the light end,
    gentle at the dark — because darkening every tone equally just lowers the
    exposure, while dropping the highlights and leaving the shadows puts the
    contrast where a turned edge actually shows it, and keeps the dark end
    from silting up into the mud the palette doctrine bans."""
    return [lerp(c[:3], VOID[:3], t0 + (t1 - t0) * (i / 5.0)) + (255,)
            for i, c in enumerate(ramp)]


def _blit_img(dst, img, ox, oy):
    """Copy an Img onto a canvas. `Img.blit_cell` takes a Sprite (it reads `.n`),
    and `great_trunk` hands back Imgs — the shaft is baked rather than emitted,
    so it never goes through emit_prop's own path."""
    for y in range(img.h):
        for x in range(img.w):
            p = img.get(x, y)
            if p[3]:
                dst.put(ox + x, oy + y, p)


def _gloom_rect(cv, x0, y0, x1, y1, tone, k0, k1):
    """Grade every opaque pixel in the rect toward `tone`: k0 at y0 -> k1 at
    y1. This is how a trunk disappears — into the dark canopy overhead on the
    floor map (k0 heavy at the top), into the drop below on the canopy map
    (k1 heavy at the bottom). A hard cut at either end is a chopped tree; the
    grade is what reads as gloom."""
    span = max(1, y1 - y0 - 1)
    for y in range(y0, y1):
        t = k0 + (k1 - k0) * ((y - y0) / span)
        if t <= 0.0:
            continue
        for x in range(x0, x1):
            p = cv.get(x, y)
            if p[3]:
                cv.put(x, y, lerp(p[:3], tone[:3], t) + (255,))


def _shade_under(img, bark, bx0, by0, w, hole, fascia=RING_FASCIA,
                 deep=9, soft=20):
    """Darken `img`'s bark where it lies just under a ring deck's fascia.

    `bx0`/`by0` are the image's top-left in the RING BLOCK's own pixel space, so
    the hem is computed from the very ellipse `tree_ring` drew. Two hard bands
    (bark is banded, never dithered), and anything not literally a BARK colour
    is left alone so the ladder's hemp keeps its own values."""
    cx, cy, rx, ry, _hx, _hy = ring_geom(w, hole=hole)
    idx = {c: i for i, c in enumerate(bark)}
    for x in range(img.w):
        t = (bx0 + x - cx) / rx
        if abs(t) >= 1.0:
            continue
        hem = cy + (ry + fascia) * (1.0 - t * t) ** 0.5
        for y in range(img.h):
            d = by0 + y - hem
            if not 0.0 <= d < soft:
                continue
            i = idx.get(img.get(x, y))
            if i is not None:
                img.put(x, y, bark[min(len(bark) - 1, i + (2 if d < deep else 1))])


def _wild_dist(m, wild, limit):
    """{(x, y): chebyshev distance to the nearest cell whose char is in `wild`},
    for every cell within `limit` of one. Multi-source BFS on the
    8-neighbourhood — a litter gradient drifts into corners and does not
    respect a 4-connected metric."""
    seen = {}
    front = [(x, y) for y in range(m.rows_n) for x in range(m.cols)
             if m.at(x, y) in wild]
    for c in front:
        seen[c] = 0
    d = 0
    while front and d < limit:
        d += 1
        nxt = []
        for x, y in front:
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    c = (x + ax, y + ay)
                    if (0 <= c[0] < m.cols and 0 <= c[1] < m.rows_n
                            and c not in seen):
                        seen[c] = d
                        nxt.append(c)
        front = nxt
    return seen


def _fountain_shadow(tn):
    """Bake the basin's elliptical contact shadow into the plaza paving.

    `bake_shadow` is intentionally rectangular because desks, benches and
    building feet are opaque across their footprint. The fountain is
    transparent in all four corners, so that helper leaves a conspicuous dark
    bar visible under the basin."""
    x0, y0, x1, y1 = tn.bbox("oO")
    assert (x1 - x0 + 1, y1 - y0 + 1) == (3, 3)
    cx, cy = x0 * T + 24, y0 * T + 34
    for py in range(y0 * T + 24, (y1 + 1) * T):
        for px in range(x0 * T, (x1 + 1) * T):
            d = ((px - cx) / 22.0) ** 2 + ((py - cy) / 9.0) ** 2
            if d > 1.0:
                continue
            base = tn.bg.get(px, py)
            strength = 0.30 if d < 0.72 else 0.18
            tn.bg.put(px, py, lerp(base[:3], VOID[:3], strength) + (255,))


def _z_runs(tn):
    """The rope-ladder runs, west to east: [(zx0, ztop, zbot)] per 2-col run."""
    out = []
    for comp in tn.comps("z"):
        xs = [x for x, _ in comp]
        ys = [y for _, y in comp]
        out.append((min(xs), min(ys), max(ys)))
    return sorted(out)


# =====================================================================================
# THE FLOOR — build(): the ground half of the split town
# =====================================================================================

def build(map_name, scene_key, glow):
    """Paint one era of Alembic Town's FLOOR and finish it. Returns the TileScene."""
    tn = OverWorld(map_name, scene_key)
    ROOFB = tn.mat("roof_blue")
    ROOFG = tn.mat("roof_green")
    PLAST = tn.mat("plaster")
    STONE = tn.ROCK                    # town masonry = the scene's violet slate
    DECK = tn.DECK                     # the ladders' hand-pinned timber
    FOL = tn.FOREST

    tn.paint_terrain()

    # ---- THE GROUND TOWN --------------------------------------------------------------
    tn.emit_prop("CottageW", "q1",
                 town_cottage(ROOFG, PLAST, salt=211, composite=True, frames=4),
                 hframes=4)
    tn.emit_prop("CottageE", "w2",
                 town_cottage(ROOFB, PLAST, salt=213, composite=True, frames=4),
                 hframes=4)
    for name, chars, salt, trade in (("Weapons", "xX", 483, "arms"),
                                     ("Items", "pP", 485, "tonics"),
                                     ("Inn", "iI", 489, "inn")):
        tn.emit_prop(name, chars,
                     town_shop(ROOFG, PLAST, trade, salt=salt, composite=True,
                               frames=8),
                     hframes=8)

    _fountain_shadow(tn)
    tn.emit_prop("Fountain", "oO", town_fountain(STONE, frames=4), hframes=4)
    tn.emit_prop("Well", "uU", sprite_img(town_well(STONE), 32, 32))
    tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(), 16, 32), each=True)
    tn.emit_prop("Stall", "m", sprite_img(town_stall(), 48, 32))

    # ---- THE CULTURE KIT --------------------------------------------------------------
    # The correspondence corner on the plaza's north rim, and the hook lanterns
    # beside every ladder foot and flanking the south gate. Candles are honest
    # fire, so they burn in BOTH eras — and in the permanent dusk they are half
    # the town's light.
    tn.emit_prop("Notice", "kK",
                 sprite_img(notice_board(DECK, PAPER_STOCK, IRON), 48, 32))
    tn.emit_prop("Roost", "cC", owl_roost(DECK, FOL, IRON, frames=4), hframes=4)
    tn.emit_prop("Hooklamp", "hH", hook_lantern(IRON, frames=4), hframes=4,
                 each=True)

    # ---- THE FOUR GREAT TRUNKS (2026-08-23: bare shafts, no rings) --------------------
    # Each trunk is baked Tier-1 from ROW 0 down to its buttress foot: nothing
    # can ever stand behind these columns (they are solid to the map's top), so
    # the depth question never arises and baking is simply correct. The shaft
    # runs off the top of the map, where limit_top = 0 cuts it at the SCREEN
    # edge — a tree whose top is never on screen reads as too tall for the
    # screen, which is the point of a great tree.
    #
    # THE GLOOM IS THE CANOPY OVERHEAD. The crown itself lives in the other
    # scene now, so what says "there are leaves up there" down here is the
    # dark: the shaft's top ~7 rows grade toward the forest's deepest tone, so
    # every trunk climbs up out of the streets and disappears into shadow.
    # A hard edge there would be the chopped-off-tree defect; the grade is
    # load-bearing.
    GLOOM = FOL[5]
    for zx0, ztop, zbot in _z_runs(tn):
        tx0 = zx0 - 1
        shaft = great_trunk(BARK, tn.GRASS, [(0, zbot)], salt=401, w=TRUNK_W)[0]
        _blit_img(tn.bg, shaft, tx0 * T, 0)
        # the ladder: the walkable run PLUS RUNG_OVER painted rungs above it —
        # the rope visibly continues up the bark past the travel mouth, because
        # the climb continues in the other scene. One sprite per tree at that
        # tree's own height (place_each would stretch one across four drops).
        lad = rope_ladder(DECK, BARK, salt=441,
                          cells=(zbot - ztop + 1) + RUNG_OVER)
        tn.bg.blit_cell(lad, zx0 * T, (ztop - RUNG_OVER) * T)
        _gloom_rect(tn.bg, tx0 * T, 0, (tx0 + 4) * T, 7 * T, GLOOM, 0.88, 0.0)

    # ---- walk-behind trees: TWO y-sorted World props per {T,t} component --------------
    # 2x3 blocks: two WALKABLE crown rows over one solid trunk row. BARK, not
    # tn.TRUNK — the derived trunk ramp is a blue pillar (the ramp() violet
    # law), and sharing BARK makes a small tree and a great tree the same
    # species of wood.
    lo, up = town_shade_tree(tn.FOREST, BARK, tn.GRASS)
    tn.emit_prop("TreeTrunk", "Tt", sprite_img(lo, 64, 112), each=True)
    tn.emit_prop("TreeCrown", "Tt", sprite_img(up, 64, 112), each=True,
                 top=-64, base_inset=-16)
    for _comp in tn.comps("Tt"):
        _x0, _y0, _x1, _y1 = tn.comp_bbox(_comp)
        for _cx, _cy in _comp:
            _want_solid = _cy == _y1                       # only the trunk row
            assert tn.m.legend[tn.m.at(_cx, _cy)]["solid"] == _want_solid, (
                f"{tn.name}.txt: tree cell ({_cx},{_cy}) should be "
                f"{'solid trunk' if _want_solid else 'walkable crown'}")

    # ---- THE UNDERSTORY: the forest floor this town stands on -------------------------
    # DENSITY IS A GRADIENT: every cell is scored by its distance to the
    # nearest WILD thing and the odds fall off with it — thick at the edges,
    # worn down the lane. `drift` (warm fallen leaves off the timber ramp) is
    # the common case at every distance, because it is the only piece that
    # changes the field's HUE.
    ROT = [DECK[2], DECK[3], DECK[3], DECK[4], DECK[4], DECK[5]]
    VARIANTS = (("drift", 5), ("fern", 3), ("sapling", 2), ("roots", 2),
                ("log", 2), ("shroom", 1))
    under = {k: [understory(FOL, ROT, tn.GRASS, kind=k, salt=461 + 31 * i + 7 * v)
                 for v in range(n)]
             for i, (k, n) in enumerate(VARIANTS)}
    NEAR = ("drift", "fern", "drift", "fern", "roots", "drift", "log", "shroom")
    MID = ("drift", "fern", "drift", "sapling", "drift", "roots", "drift", "fern")
    FAR = ("drift", "sapling", "drift", "drift", "fern", "drift")
    LITTER = {1: (8, NEAR), 2: (6, NEAR), 3: (5, MID), 4: (4, MID),
              5: (3, FAR), 6: (2, FAR)}
    wild = "#Ttj!"                     # forest wall, town trees, the great trunks
    dist = _wild_dist(tn.m, wild, max(LITTER))
    for y in range(tn.m.rows_n):
        for x in range(tn.m.cols):
            if tn.m.at(x, y) not in ".,":
                continue
            # never over a struct's contact band (it unsticks the building from
            # its ground) — `greattrunk` is the deliberate exception: the trees
            # WANT their feet in the litter
            n = tn.m.legend[tn.m.at(x, y - 1)]["terrain"] if y else ""
            if n in STRUCT_TERRAIN and n != "greattrunk":
                continue
            if any(tn.m.at(x, y - d) == "D" for d in (1, 2)):
                continue               # keep a doorway's approach swept
            d = dist.get((x, y))
            if d is None or d not in LITTER:
                continue
            odds, pool = LITTER[d]
            if h2(x, y, 467) % 16 >= odds:
                continue
            bag = under[pool[h2(x, y, 463) % len(pool)]]
            tn.bg.blit_cell(bag[h2(x, y, 479) % len(bag)], x * T, y * T)

    # NO foot_shade("!") — `greattrunk` is in STRUCT_TERRAIN, so _ground_overlays
    # has already painted the contact band; doubling it collars every tree.
    tn.write_glow(lambda img: glow(tn, img))

    assert_floor(tn, map_name)
    tn.finish()
    return tn


def assert_floor(tn, map_name):
    """THE ASSERT BLOCK for the floor map — every failure here is SILENT
    otherwise: it renders, it dedupes, every lint in _check_art.py passes it,
    and it ships."""
    tn.assert_strata()
    tn.assert_door_approach(rows=2)
    tn.assert_npc_room()
    # component shapes AND counts (two blocks authored edge-to-edge fuse into
    # one stretched sprite; a missing lantern passes every other check)
    for chars, w, h, n in (("q1", 5, 4, 1), ("w2", 5, 4, 1),
                           ("xX", 5, 4, 1), ("pP", 5, 4, 1), ("iI", 5, 4, 1),
                           ("Tt", 2, 3, 6),
                           ("kK", 3, 2, 1), ("cC", 2, 2, 1), ("hH", 1, 2, 6)):
        cs = tn.comps(chars)
        assert len(cs) == n, (
            f"{map_name}.txt: {chars!r} has {len(cs)} components, want {n}")
        for c in cs:
            a, b, c2, d = tn.comp_bbox(c)
            assert (c2 - a + 1, d - b + 1) == (w, h), (
                f"{map_name}.txt: the {chars!r} component at ({a},{b}) is "
                f"{c2 - a + 1}x{d - b + 1}, want {w}x{h}")
    # THE TRUNKS: four, each exactly 4 columns wide, typed from row 6 down —
    # the shaft art is blitted from row 0 on that assumption
    trunks = tn.comps("j!z")
    assert len(trunks) == 4, (
        f"{map_name}.txt: {len(trunks)} great trunks, want 4")
    for c in trunks:
        a, b, c2, d = tn.comp_bbox(c)
        assert c2 - a + 1 == 4, (
            f"{map_name}.txt: the trunk at ({a},{b}) is {c2 - a + 1} cols wide, "
            f"want 4 (jzzj)")
        assert b == 6, (
            f"{map_name}.txt: the trunk at ({a},{b}) starts at row {b}, want 6")
    # THE LADDERS: 2 cols, boxed by trunk timber on both sides for their whole
    # length (or a body steps sideways off rung eight onto open ground), rungs
    # continuing up into solid trunk above (the travel mouth is mid-ladder, not
    # at the tree's top), and the floor below the last rung walkable.
    runs = _z_runs(tn)
    assert len(runs) == 4, f"{map_name}.txt: {len(runs)} ladders, want 4"
    for i, (a, b, d) in enumerate(runs, 1):
        c2 = a + 1
        for y in range(b, d + 1):
            for x in (a - 1, c2 + 1):
                ch = tn.m.at(x, y)
                assert ch in "j!", (
                    f"{map_name}.txt: the ladder at ({a},{b}) has {ch!r} beside "
                    f"it at ({x},{y}) — a ladder needs solid timber both sides")
        assert tn.m.at(a, b - 1) == "j" and tn.m.at(c2, b - 1) == "j", (
            f"{map_name}.txt: the ladder at ({a},{b}) must continue into solid "
            f"trunk above — its travel mouth is mid-ladder")
        assert not tn.m.legend[tn.m.at(a, d + 1)]["solid"], (
            f"{map_name}.txt: the ladder at ({a},{b}) ends on solid ground at "
            f"({a},{d + 1}) — it must emerge onto the floor")
        # the travel anchors are pinned to the run itself, so a moved ladder
        # takes its mouth and its foot with it
        assert tn.m.anchors[f"top{i}"] == (a, b), (
            f"{map_name}.txt: anchor top{i} is {tn.m.anchors.get(f'top{i}')}, "
            f"want ({a},{b}) — the z run's own top rung")
        assert tn.m.anchors[f"foot{i}"] == (a, d + 1), (
            f"{map_name}.txt: anchor foot{i} is {tn.m.anchors.get(f'foot{i}')}, "
            f"want ({a},{d + 1}) — the floor cell below the last rung")
    # reachable from BOTH arrivals: the south gate and any ladder foot
    tn.assert_reachable("exit_south", "foot1", "foot2", "foot3", "foot4")


# =====================================================================================
# THE BOUGHS — build_canopy(): the treetop half of the split town
# =====================================================================================

# The drop field's own tones are hand-pinned FRACTIONS of the scene's grass —
# the town seen from above at dusk is a view, not a material, and it must stay
# darker than everything a body can stand on or the void reads as floor.
DROP_PULL = (0.66, 0.58, 0.52)     # lerp-to-VOID per fabric tone (dark -> darker)
DROP_WINDOW = (255, 196, 110, 255)  # the amber pinpricks thirty feet down


def _drop_field(tn):
    """Repaint the INTERIOR drop/span cells as THE DROP — the clearing floor
    far below — and return the window pixels for the glow overlay.

    Boundary drop cells keep paint_terrain's leaf lattice, so every void
    pocket arrives fringed in foliage; only cells fully surrounded by drop
    (map edges count as drop) go down into the view. The fabric is TILE-LOCAL
    dither, so the open field collapses to a couple of atlas tiles; the
    houses are keyed on absolute position and each costs its cells' tiles,
    which is the price of a view and is paid ~40 cells at a time.

    The old chasm lesson ("a hole is an absence and authoring absence fails")
    does not apply, and knowing why matters: the drop is BELOW the camera's
    subject, not beside it, and it is full of named positive things — roofs,
    windows, lanes. What failed in Lanternwood was two rows of dark painted on
    flat ground; what works here is what makes Slitherbough and Endor read:
    platforms as figure, a live world as ground."""
    m = tn.m
    dropch = {c for c, d in m.legend.items()
              if d["terrain"] in ("drop", "span")}
    # the descending trunks and their rungs HANG IN the void, so for the
    # interior test they count as drop — otherwise every trunk lands in a
    # bright leaf pocket instead of fading into the dark below it
    near = dropch | set("jz")

    def isd(x, y):
        if not (0 <= x < m.cols and 0 <= y < m.rows_n):
            return True                # off-map counts as drop: the view runs
        return m.at(x, y) in near      # to the frame edge

    interior = set()
    for y in range(m.rows_n):
        for x in range(m.cols):
            if m.at(x, y) in dropch and all(isd(x + dx, y + dy)
                                            for dx in (-1, 0, 1)
                                            for dy in (-1, 0, 1)):
                interior.add((x, y))

    G = tn.GRASS
    fab = [lerp(G[2 + i][:3], VOID[:3], DROP_PULL[i]) + (255,)
           for i in range(3)]
    for (x, y) in interior:
        X, Y = x * T, y * T
        for py in range(T):
            for px in range(T):
                r = h2(px, py, 977) % 16
                c = fab[0] if r == 0 else fab[2] if r < 4 else fab[1]
                tn.bg.put(X + px, Y + py, c)

    def put(px, py, c):
        if (px // T, py // T) in interior:
            tn.bg.put(px, py, c)

    # THE LANES BELOW: two soft ribbons wandering across the deep field, one
    # value step up from the fabric — the town's road web read from thirty
    # feet, before a single roof lands on it. Drawn first so the houses sit
    # over them the way real houses sit over a lane's edge.
    import math
    lane = lerp(tn.ROAD[3][:3], VOID[:3], 0.60) + (255,)
    H_PX = m.rows_n * T
    for base_y, amp, period, ph in ((H_PX - 118, 13.0, 170.0, 0.0),
                                    (H_PX - 52, 9.0, 210.0, 2.1)):
        for px in range(m.cols * T):
            cy = base_y + amp * math.sin(px / period + ph)
            for dy in range(5):
                put(px, int(cy) + dy, lane)

    # THE HOUSES BELOW: tiny roofs on a jittered grid over the deep field.
    # Value discipline: a roof is a couple of steps up from the fabric with a
    # lit ridge, never a bright object — at this depth the WINDOWS carry the
    # read, and they get their real light from the glow overlay (returned to
    # the caller).
    roofA = lerp(tn.mat("roof_green")[1][:3], VOID[:3], 0.30) + (255,)
    roofB = lerp(tn.mat("roof_blue")[1][:3], VOID[:3], 0.30) + (255,)
    ridge = lerp(tn.mat("plaster")[2][:3], VOID[:3], 0.28) + (255,)
    shade = lerp(fab[2][:3], VOID[:3], 0.5) + (255,)
    windows = []
    for gx in range(m.cols // 4):
        for gy in range(m.rows_n // 4):
            if h2(gx, gy, 911) % 3 == 0:
                continue
            hx = gx * 4 * T + 6 + h2(gx, gy, 913) % (2 * T)
            hy = gy * 4 * T + 8 + h2(gx, gy, 917) % (2 * T)
            hw, hh = 14 + h2(gx, gy, 919) % 6, 9
            # only where the WHOLE house lands in the deep field
            cells = {(px // T, py // T)
                     for px in (hx, hx + hw) for py in (hy, hy + hh + 1)}
            if not cells <= interior:
                continue
            roof = roofA if h2(gx, gy, 923) % 2 else roofB
            for py in range(hy, hy + hh):
                for px in range(hx, hx + hw):
                    put(px, py, roof)
            for px in range(hx, hx + hw):
                put(px, hy, ridge)                     # the lit ridge line
                put(px, hy + hh, shade)                # contact shadow
            wx, wy = hx + 3 + h2(gx, gy, 929) % (hw - 6), hy + hh - 3
            for px in range(wx, wx + 3):
                for py in range(wy, wy + 2):
                    put(px, py, DROP_WINDOW)
            windows.append((wx + 1, wy + 1))
    return windows


def build_canopy(map_name, scene_key, glow):
    """Paint one era of THE BOUGHS and finish it. Returns the TileScene."""
    tn = OverWorld(map_name, scene_key)
    DECK = tn.DECK
    FOL = tn.FOREST

    tn.paint_terrain()
    tn.drop_windows = _drop_field(tn)

    ring_lo, ring_up = tree_ring(DECK, BARK, FOL, salt=491, w=RING_W, h=RING_H,
                                 hole=RING_HOLE, fascia=RING_FASCIA)
    # THE CROWN AND THE TRUNK'S TOP ARE ONE SPRITE — the crown hangs three rows
    # below its footprint and carries the shaft's continuation behind its
    # leaves (`shaft_w`), so the hem cuts through bark over the trunk's own
    # columns and the two sprites are one shaft. `great_crown` measures its own
    # mass and hands back the margins (`cpx`/`cpt`) — hardcoding the canvas
    # re-introduces the flat-top tree. base_inset=-52 pushes the sort key south
    # of the trunk segment's so the leaves are genuinely in front of a body on
    # the ring's north arc — the walk-behind this scene is built around, which
    # is why the mass stays PERFORATED.
    crown, cpx, cpt = great_crown(FOL, BARK, salt=451, w=CROWN_W, h=CROWN_H,
                                  window=DECK, shaft_w=TRUNK_W)
    tn.emit_prop("Crown", "G",
                 sprite_img(crown, CROWN_W + 2 * cpx, CROWN_H + cpt),
                 each=True, top=-cpt, base_inset=-52)
    # THE RAIL'S NEAR ARC — Tier-3: baked, every body draws OVER the handline;
    # upper-layer, the corridor cap forbids art a body is MEANT to be seen
    # over. As a prop it just sorts. The far arc stays baked with the deck.
    tn.emit_prop("RingRail", RING_CHARS,
                 sprite_img(ring_up, RING_W, RING_H), each=True, top=0)
    # the shaft segment crossing the ring — the ONE piece of the tree a body
    # passes behind; base_inset=19 lands its key in the 2px of daylight between
    # a body on the trunk row and a body on the south deck
    tn.emit_prop("TrunkRing", "J",
                 sprite_img(trunk_face(BARK, DECK, salt=401, w=TRUNK_W, h=32),
                            TRUNK_W, 32),
                 each=True, base_inset=19)

    GLOOM = lerp(tn.GRASS[5][:3], VOID[:3], 0.6) + (255,)
    for comp in tn.comps(RING_CHARS):
        cx0, cy0, cx1, cy1 = tn.comp_bbox(comp)
        assert (cx1 - cx0 + 1, cy1 - cy0 + 1) == (RING_W // T, RING_H // T), (
            f"{map_name}.txt: the ring at ({cx0},{cy0}) is not {RING_W // T}x"
            f"{RING_H // T} — one sprite would be stretched over it")
        tx0 = cx0 + TRUNK_C0
        fy = cy1
        while fy + 1 < tn.m.rows_n and tn.m.at(tx0, fy + 1) == "j":
            fy += 1
        # THE SHAFT GOES DOWN FIRST, AND THE RING GOES DOWN ON TOP OF IT.
        # Blitted the other way round, the shaft's dead-straight edge() top
        # lands two px under the crescent and the tree BEGINS at a horizontal
        # cut — a post nailed to a saucer. Starting two rows above the block's
        # foot buries that edge under opaque decking; the only line crossing
        # the trunk is then the fascia's hem, which is an ARC, and an arc
        # crossing a cylinder is an overlap.
        shaft = great_trunk(BARK, tn.GRASS, [(0, fy - (cy1 - 2))], salt=401,
                            w=TRUNK_W)[0]
        # ...and the deck throws its SHADOW on the bark — bark under a platform
        # and bark in the open are otherwise the same six colours.
        _shade_under(shaft, BARK, (tx0 - cx0) * T,
                     (cy1 - 2 - cy0) * T, RING_W, RING_HOLE)
        _blit_img(tn.bg, shaft, tx0 * T, (cy1 - 2) * T)
        tn.bg.blit_cell(ring_lo, cx0 * T, cy0 * T)
        # the ladder, from the fascia cut down the descending trunk
        lx0 = cx0 + LADDER_C0
        top = cy0
        while tn.m.at(lx0, top) != "z":
            top += 1
        bot = top
        while bot + 1 < tn.m.rows_n and tn.m.at(lx0, bot + 1) == "z":
            bot += 1
        tn.bg.blit_cell(rope_ladder(DECK, BARK, salt=441, cells=bot - top + 1),
                        lx0 * T, top * T)
        # the trunk and its rungs FADE into the drop — the tree does not end at
        # row `fy`, the view does
        _gloom_rect(tn.bg, tx0 * T, fy * T - 6, (tx0 + 4) * T, (fy + 1) * T,
                    GLOOM, 0.0, 0.92)

    # THE LANDING between trees 2 and 3 — Tier-1 (100% opaque over its cells),
    # rails on the open north/south sides only: the bridges land east and west,
    # and a rail across a joint is a wall you can see through.
    comps_n = tn.comps("nhH")
    assert len(comps_n) == 1, f"{map_name}.txt: want exactly one landing"
    la, lb, lc, ld = tn.comp_bbox(comps_n[0])
    plat = tree_platform(DECK, FOL, salt=421, w=(lc - la + 1) * T,
                         h=(ld - lb + 1) * T, rails="ns", fascia=6)
    tn.bg.blit_cell(plat, la * T, lb * T)

    # THE BRIDGES — blitted AFTER the rings and the landing, one cell wider
    # each side than their walkable run, so the bearer beams land ON the bridge
    # gates and the platform edge and overdraw the rim board there. Tier-1
    # order is depth: the later blit wins, and here that is the design.
    for comp in tn.comps("="):
        a, b, c2, d = tn.comp_bbox(comp)
        br = tree_bridge(DECK, salt=431 + a, horiz=True, cells=(c2 - a + 1) + 2)
        tn.bg.blit_cell(br, (a - 1) * T, b * T)

    # the landing's hook lantern — on the deck, so `decklamp`, not `hooklamp`
    tn.emit_prop("Hooklamp", "hH", hook_lantern(IRON, frames=4), hframes=4,
                 each=True)

    tn.write_glow(lambda img: glow(tn, img))

    assert_canopy(tn, map_name)
    tn.finish()
    return tn


def assert_canopy(tn, map_name):
    """THE ASSERT BLOCK for the boughs — the derived-ring law plus the split's
    own rules (gates, spans, ladders that end at a travel mouth)."""
    tn.assert_strata()
    tn.assert_npc_room()
    for chars, w, h, n in ((RING_CHARS, 12, 9, 4), ("G", 14, 6, 4),
                           ("J", 4, 2, 4), ("nhH", 4, 2, 1), ("hH", 1, 2, 1)):
        cs = tn.comps(chars)
        assert len(cs) == n, (
            f"{map_name}.txt: {chars!r} has {len(cs)} components, want {n}")
        for c in cs:
            a, b, c2, d = tn.comp_bbox(c)
            assert (c2 - a + 1, d - b + 1) == (w, h), (
                f"{map_name}.txt: the {chars!r} component at ({a},{b}) is "
                f"{c2 - a + 1}x{d - b + 1}, want {w}x{h}")
    # THE RING'S WALKABLE CELLS ARE THE ELLIPSE'S CELLS — derived, never
    # authored (the walked-as-a-rectangle lesson). Named exceptions only: the
    # crown-heart row (bodies 100% hidden), the ladder LANDING (standing on the
    # lip IS stepping onto the rungs), and — new with the split — the BRIDGE
    # GATES, skipped as `E` exactly as the trunk chars are skipped.
    base = ring_cells(RING_W, RING_H, hole=RING_HOLE)
    for r in range(RING_CROWN_ROWS):
        base[r] = [False] * len(base[r])
    for comp in tn.comps(RING_CHARS):
        cx0, cy0, _, _ = tn.comp_bbox(comp)
        mask = [row[:] for row in base]
        lx = cx0 + LADDER_C0
        top = cy0
        while top < tn.m.rows_n and tn.m.at(lx, top) != "z":
            top += 1
        for c in (LADDER_C0, LADDER_C0 + 1):
            mask[top - 1 - cy0][c] = True
        bad = []
        for r, mrow in enumerate(mask):
            for c, want in enumerate(mrow):
                ch = tn.m.at(cx0 + c, cy0 + r)
                if ch in "Jj!zE":                    # trunk, ladder, gates
                    continue
                if tn.m.legend[ch]["solid"] == want:
                    bad.append(f"({cx0 + c},{cy0 + r}) is {ch!r}, want "
                               + ("walkable deck" if want else "solid"))
        assert not bad, (
            f"{map_name}.txt: the ring at ({cx0},{cy0}) does not match the disc "
            f"tree_ring draws — " + "; ".join(bad[:6])
            + (f" (+{len(bad) - 6} more)" if len(bad) > 6 else ""))
    # walk the full circle round every trunk
    for c in tn.comps("J"):
        a, b, c2, d = tn.comp_bbox(c)
        ring = [(a - 1, b), (c2 + 1, b), (a - 1, d), (c2 + 1, d),
                ((a + c2) // 2, b - 1), ((a + c2) // 2, d + 1)]
        for rx, ry in ring:
            assert not tn.m.legend[tn.m.at(rx, ry)]["solid"], (
                f"{map_name}.txt: the trunk at ({a},{b}) has no ring — "
                f"({rx},{ry}) is solid, so you cannot walk round this tree")
    # EVERY GATE SERVES A SPAN: an E cell with no bridge beside it is a hole in
    # the rim board with a thirty-foot drop behind it
    for y in range(tn.m.rows_n):
        for x in range(tn.m.cols):
            if tn.m.at(x, y) == "E":
                assert tn.m.at(x - 1, y) in "=nY" or tn.m.at(x + 1, y) in "=nY", (
                    f"{map_name}.txt: the bridge gate at ({x},{y}) serves no "
                    f"span")
    # EVERY SPAN: 2 rows deep, and both ends land on a gate or the landing —
    # a bridge into leaf is a corridor, a bridge into the drop is the chasm
    for comp in tn.comps("="):
        a, b, c2, d = tn.comp_bbox(comp)
        assert d - b + 1 == 2, (
            f"{map_name}.txt: the span at ({a},{b}) is {d - b + 1} rows deep, "
            f"want 2 (the rails live in the cross dimension)")
        assert c2 - a + 1 >= 2, (
            f"{map_name}.txt: the span at ({a},{b}) has no mid-span to sag at")
        for y in (b, d):
            for x, side in ((a - 1, "west"), (c2 + 1, "east")):
                ch = tn.m.at(x, y)
                assert ch in "EnH", (
                    f"{map_name}.txt: the span at ({a},{b})'s {side} end lands "
                    f"on {ch!r} at ({x},{y}) — a bridge must abut a gate or "
                    f"the landing")
    # THE LADDERS: boxed in bark for their whole length, and ending AGAINST
    # THE DROP — the travel mouth is the bottom two rungs; the old "ends on
    # walkable ground" rule lives on the floor map now
    runs = _z_runs(tn)
    assert len(runs) == 4, f"{map_name}.txt: {len(runs)} ladders, want 4"
    for i, (a, b, d) in enumerate(runs, 1):
        c2 = a + 1
        for y in range(b, d + 1):
            for x in (a - 1, c2 + 1):
                ch = tn.m.at(x, y)
                assert ch in "jJ!y", (
                    f"{map_name}.txt: the ladder at ({a},{b}) has {ch!r} beside "
                    f"it at ({x},{y}) — a ladder needs solid timber both sides")
        assert tn.m.legend[tn.m.at(a, d + 1)]["solid"], (
            f"{map_name}.txt: the canopy ladder at ({a},{b}) must end against "
            f"the drop — its last rungs are the travel mouth")
        assert tn.m.anchors[f"head{i}"] == (a, d - 1), (
            f"{map_name}.txt: anchor head{i} is {tn.m.anchors.get(f'head{i}')}, "
            f"want ({a},{d - 1}) — one rung above the run's last")
    # reachable from the home deck, every ladder mouth and every door — with
    # full=True this also proves no bridge or arc is stranded
    tn.assert_reachable("home", "head1", "head2", "head3", "head4",
                        "door2", "door3", "door4")
