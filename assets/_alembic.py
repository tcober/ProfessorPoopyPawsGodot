#!/usr/bin/env python3
"""THE ALEMBIC RECIPE — everything the drained town and the festival town do
identically, which is everything except the palette, the glow and one open door.

WHY THIS MODULE EXISTS. `_check_art.py` byte-locks the two map GRIDS, so the eras
cannot disagree about where a plank is. Nothing locked the two GENERATORS, and they
were ~350 lines of "the same recipe as _gen_tileset_town.py" and "identical
stamping" maintained by hand in parallel — which had already gone wrong once (the
fest twin hand-inlined stamp_columns' loop and so had NO run-height assert at all,
in the era where three chapters of cutscenes walk). The grid being byte-identical
is worth little if one era stamps a band the other doesn't.

So the recipe lives here and each era is a thin config: a palette scene key, a glow
painter, and whether the Academy's door is open. If a future era needs to differ in
a fourth way, add a knob — do not fork the file.

See assets/maps/town.txt's header for the geometry this paints, and
docs/DESIGN.md for the strata doctrine and the trunk armature.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2, lerp
from _overworld_tiles import OverWorld, T, STRUCT_TERRAIN
from _tilekit import sprite_img, VOID, IRON
from _town_props import (town_cottage, town_shop, town_well, town_lamp,
                         town_stall, town_fountain, town_tree)
from _tree_props import (tree_ring, ring_cells, ring_geom, trunk_face,
                         rope_ladder, understory, great_trunk, great_crown, BARK)

# ---- THE TRUNK ARMATURE'S GEOMETRY, in one place -----------------------------------
# The trunk's own cell space, 0 = the top of its crown at map row 14. The five spans
# are the SEGMENTS; the gaps between them are the ring decks, and those gaps are not
# missing art but the boards themselves — which is exactly what a tree passing through
# a platform looks like from above. Keep this table and the map txt's header in step.
#
#   char  map rows  local     what                        footprint
#   g     14-16     0-2       the crown's leaf mass       5 cols, WALKABLE
#   J     17-18     3-4       the shaft at canopy_hi      3 cols
#   %     21-23     7-9       the high fascia it crosses  5 cols
#   j     26-27     12-13     the shaft at canopy_lo      3 cols
#   &     31-33     17-19     the low fascia it crosses   5 cols
#   !     34-36     20-22     the foot + buttress roots   3 cols
RING_W, RING_H = 192, 144          # the tree block: 12 x 9 cells
RING_HOLE = (21, 11)               # the trunk's cross-section through the boards
RING_FASCIA = 18                   # the crescent's depth at due south. One constant,
                                   # because `tree_ring` DRAWS the fascia and
                                   # `_shade_under` has to know where its hem falls to
                                   # put the deck's shadow on the trunk below it.
# Every char a ring block is made of. The block is found as ONE component of these,
# so `R` — the walkable rim — has to be in here or the border breaks into three
# islands at the ring's east and west poles and place_each stretches a sprite over
# each of them. `R` and `y` are the same terrain (`ringedge`, which renders LEAF):
# the rim cells are the ones the disc's curve crosses, so their art is part deck and
# part transparent, and a deck underlay would fill the leftover corner with plank
# fabric and square the circle straight back off. Walkability is the only difference,
# which is the O/U/L twin idiom this town already runs on.
RING_CHARS = "yR"
RING_CROWN_ROWS = 1                # block rows the crown covers OPAQUELY (see the mask)
TRUNK_W = 64                       # 4 cells
TRUNK_C0, LADDER_C0 = 4, 5         # ...at block col 4, its ladder at block col 5
CROWN_W, CROWN_H = 224, 128        # 14 cells wide over a 6-cell footprint, so it
                                   # HANGS three rows south and swallows the shaft's
                                   # top — a tree does not end, it disappears into
                                   # its own leaves

# every char that casts shade on the floor below it, for the understory pass.
# `R` is in here for the same reason `y` is — it is the ring's outer band, a great
# tree's mass seen from above; it being walkable changes nothing about the shade it
# throws on the forest floor thirty feet down.
SHADERS = "yJj!GR"
# every char whose cell the night-glow must be WIPED off — see the clip pass
FACES = "yJj!R"
# stamp_columns picks its face variant with h2(tx, ty, salt) % len(sprites), and the
# LAST variant is the one carrying a lantern. The glow pass repeats that arithmetic
# rather than being handed a list, so the lights can never drift off the lanterns:
# one source of truth, evaluated twice.
LANTERN_OF = 6                     # variants per band
BAND_SALT = {}                     # no face bands left: the canopy is islands now


def lantern_cells(m, chars, salt):
    """The (tx, ty) of every fascia column that got the lantern variant."""
    out = []
    for x in range(m.cols):
        y = 0
        while y < m.rows_n:
            if m.at(x, y) in chars:
                top = y
                while m.at(x, y) in chars:
                    y += 1
                if h2(x, top, salt) % LANTERN_OF == LANTERN_OF - 1:
                    out.append((x, top))
            else:
                y += 1
    return out


def shaded(ramp, t0=0.40, t1=0.12):
    """A ramp pulled toward the void — the SAME timber, seen edge-on.

    THE ONE CHANGE THAT MADE THIS TOWN THREE-DIMENSIONAL. Every horizontal surface
    up here (the deck, the porches, the spans) and every vertical one (the two
    fascias, the span edges) were drawn from the identical DECK ramp, and the first
    build of the four-storey grid came out as a LUMBER YARD: three tiers of
    near-identical honey planks in horizontal stripes, with no cue anywhere that
    one of those bands was a floor and the next was a wall you were standing on top
    of. The structure was right and the value was flat.

    A vertical face is darker than the surface it hangs off. That is the whole
    idea, and it costs one ramp. The pull is GRADED — hard at the light end, gentle
    at the dark — because darkening every tone equally just lowers the exposure,
    while dropping the highlights and leaving the shadows puts the contrast where a
    turned edge actually shows it, and keeps the dark end from silting up into the
    mud the palette doctrine bans."""
    return [lerp(c[:3], VOID[:3], t0 + (t1 - t0) * (i / 5.0)) + (255,)
            for i, c in enumerate(ramp)]


def _blit_img(dst, img, ox, oy):
    """Copy an Img onto a canvas. `Img.blit_cell` takes a Sprite (it reads `.n`),
    and `great_trunk` hands back Imgs — the shaft is baked rather than emitted, so
    it never goes through emit_prop's own path."""
    for y in range(img.h):
        for x in range(img.w):
            p = img.get(x, y)
            if p[3]:
                dst.put(ox + x, oy + y, p)


def _shade_under(img, bark, bx0, by0, w, hole, fascia=RING_FASCIA,
                 deep=9, soft=20):
    """Darken `img`'s bark where it lies just under a ring deck's fascia.

    `bx0`/`by0` are the image's top-left in the RING BLOCK's own pixel space, so
    the hem is computed from the very ellipse `tree_ring` drew: for each column
    the fascia's lower edge is at `cy + (ry + fascia) * k`, k the same
    sqrt(1 - t^2) the crescent is scaled by. Two hard bands (see `_BARK_BANDS` —
    bark is banded, never dithered), `deep` px at two ramp steps and the rest at
    one, and anything not literally a BARK colour is left alone so the ladder's
    hemp and the buttress arrises keep their own values."""
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
    for every cell within `limit` of one. Multi-source BFS on the 8-neighbourhood,
    so a cell diagonally off a trunk is distance 1 — which is what the eye reads,
    and what a litter gradient wants: drift banks into a corner, it does not
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


def build(map_name, scene_key, glow, open_door=False):
    """Paint one era of Alembic Town and finish it. Returns the TileScene."""
    tn = OverWorld(map_name, scene_key)
    ROOFB = tn.mat("roof_blue")
    ROOFG = tn.mat("roof_green")
    PLAST = tn.mat("plaster")
    STONE = tn.ROCK                    # town masonry = the scene's violet slate
    DECK = tn.DECK                     # the ring decks' hand-pinned timber
    FACE = shaded(DECK)                # ...the same timber, turned edge-on
    FOL = tn.FOREST                    # the canopy's leaf

    tn.paint_terrain()

    # ---- THE GROUND TOWN — this is the town now --------------------------------------
    # The public village is on the forest floor and keeps Alembic's own
    # plaster-and-cement language: an old ground village that four great trees grew
    # up through. The canopy is not a street any more, it is four balconies.
    tn.emit_prop("CottageW", "q1",
                 town_cottage(ROOFG, PLAST, salt=211, composite=True, frames=4),
                 hframes=4)
    tn.emit_prop("CottageE", "w2",
                 town_cottage(ROOFB, PLAST, salt=213, composite=True, frames=4),
                 hframes=4)
    # THE THREE SHOPS ARE COTTAGES THAT SELL SOMETHING, and that is a correction.
    # They were `tree_hut`s — cone of thatch over a barrel of withy staves — which
    # is the right building for a BOUGH and a tiki hut on a forest floor: one tan
    # value throughout, no wall material, and three cells wide beside a five-cell
    # cottage. `town_shop` is the town's own envelope (leaf canopy, greeny cement,
    # copper, vines) with an awning, a lit display window and a hanging device.
    for name, chars, salt, trade in (("Weapons", "xX", 483, "arms"),
                                     ("Items", "pP", 485, "tonics"),
                                     ("Inn", "iI", 489, "inn")):
        tn.emit_prop(name, chars,
                     town_shop(ROOFG, PLAST, trade, salt=salt, composite=True,
                               frames=8),
                     hframes=8)

    tn.bake_shadow("oO", 3)
    tn.emit_prop("Fountain", "oO", town_fountain(STONE, frames=4), hframes=4)
    tn.emit_prop("Well", "uU", sprite_img(town_well(STONE), 32, 32))
    tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(), 16, 32), each=True)
    tn.emit_prop("Stall", "m", sprite_img(town_stall(), 48, 32))

    # ---- THE FOUR GREAT TREES ---------------------------------------------------------
    # Derived from the map, never from a table: every tree is one `y` component, and
    # its bbox IS the ring block (12 x 9). Reading the geometry back out of the grid
    # is what stops the art and the collision drifting apart the moment a tree moves.
    ring_lo, ring_up = tree_ring(DECK, BARK, FOL, salt=491, w=RING_W, h=RING_H,
                                 hole=RING_HOLE, fascia=RING_FASCIA)

    # THE CROWN AND THE TRUNK'S TOP ARE ONE SPRITE, and that is the whole answer to
    # the tree reading as CHOPPED OFF. A trunk drawn as its own piece starts at a cell
    # boundary and ends in a hard horizontal cut against the leaves; a tree's top does
    # not end, it disappears into its own foliage. So the crown hangs three rows BELOW
    # its footprint (`top=0` + a 9-row sprite over a 6-row footprint) and covers the
    # shaft's upper end, and `base_inset=-52` pushes its sort key south of the trunk
    # segment's so the leaves are genuinely in front rather than merely adjacent.
    #
    # That inset also puts the crown in front of a body on the ring's NORTH ARC, which
    # is the walk-behind this town is built around — so the mass stays PERFORATED. See
    # great_crown: solid leaves there make that body 100% invisible, measured.
    tn.emit_prop("Crown", "G",
                 sprite_img(great_crown(FOL, BARK, salt=451, w=CROWN_W, h=CROWN_H,
                                        window=DECK), CROWN_W, CROWN_H),
                 each=True, top=0, base_inset=-52)
    # THE RAIL'S NEAR ARC — Tier-3, and it has to be a y-sorted PROP rather than
    # upper-layer paint. Baked with the deck (where it lived until 2026-07-30) every
    # body on the ring draws OVER the handline, so you stand on the rail like it is a
    # kerb instead of behind it like it is a railing. The upper layer is the other
    # obvious home and it is wrong for the opposite reason: that layer is for art a
    # body may never poke out of — lintels, arches — so `_check_art`'s corridor cap
    # requires the silhouette to continue north of every walkable cell it covers, and
    # a rail is two pixels of hemp you are MEANT to be seen over. As a prop it just
    # sorts: its key is the block's south edge, every walkable cell of the ring is
    # north of that, and the far arc stays baked because it is behind you.
    tn.emit_prop("RingRail", RING_CHARS,
                 sprite_img(ring_up, RING_W, RING_H), each=True, top=0)
    # the shaft segment crossing the ring — Tier-3, because this is the ONE piece of
    # the tree a body passes behind. base_inset=19 lands its key in the 2px of daylight
    # between a body on the trunk row and a body on the south deck.
    tn.emit_prop("TrunkRing", "J",
                 sprite_img(trunk_face(BARK, DECK, salt=401, w=TRUNK_W, h=32),
                            TRUNK_W, 32),
                 each=True, base_inset=19)

    # The shaft below the ring and the foot are TIER-1 BAKED, not sprites, and the
    # reason is the ladder: it runs down inside the trunk's own columns, so a Tier-3
    # shaft would draw over the climber. Nothing can stand behind these rows either —
    # they are enclosed by the ring above and the floor below — so the depth question
    # never arises and baking is simply correct.
    for comp in tn.comps(RING_CHARS):
        cx0, cy0, cx1, cy1 = tn.comp_bbox(comp)
        assert (cx1 - cx0 + 1, cy1 - cy0 + 1) == (RING_W // T, RING_H // T), (
            f"{map_name}.txt: the ring at ({cx0},{cy0}) is not {RING_W // T}x"
            f"{RING_H // T} — one sprite would be stretched over it")
        tx0 = cx0 + TRUNK_C0                       # the trunk's own 4 columns
        # how far down does this tree go? to the last row of its `!` foot.
        fy = cy1
        while fy + 1 < tn.m.rows_n and tn.m.at(tx0, fy + 1) in "j!":
            fy += 1
        # THE SHAFT GOES DOWN FIRST, AND THE RING GOES DOWN ON TOP OF IT. Order is
        # the whole difference between a trunk that FEEDS THROUGH the platform and
        # one that is CHOPPED OFF under it, and it took two wrong answers to see.
        #
        # The build before this one blitted the shaft after the ring and one row
        # below the block, which left two rows of the trunk's own columns with no
        # trunk art at all — raw `ringedge` underlay autotiling into the ladder's
        # `ropeladder`, i.e. a pale hard-edged wedge either side of the rungs that
        # reads exactly like a clipping bug. Moving the shaft up two rows filled
        # those rows and fixed that, but it fixed it by drawing the bark ON TOP of
        # the fascia: the shaft's own top edge — an `edge()` outline, dead straight,
        # 64px wide — landed just under the crescent, so the trunk visibly BEGAN at
        # a horizontal cut two px below a platform it was supposed to be growing
        # through. A post nailed under a saucer.
        #
        # Drawn UNDERNEATH, the line that crosses the trunk is the fascia's own
        # lower edge, which is an ARC, and an arc crossing a cylinder is an overlap.
        # The shaft starts two rows above the block's foot so that straight top edge
        # is buried under opaque decking, and everything from the crescent's hem
        # down is the tree.
        shaft = great_trunk(BARK, tn.GRASS, [(0, fy - cy1 + 2)], salt=401,
                            w=TRUNK_W)[0]
        # ...and the deck throws its SHADOW on the bark. Order alone is not enough:
        # bark under a platform and bark in the open are the same six colours, so
        # without this the fascia's hem reads as a change of material rather than as
        # something in front. Two graded bands off the same ramp, their lower edge
        # following the fascia's own arc, so what emerges is emerging out of shade.
        _shade_under(shaft, BARK, tx0 * T - cx0 * T,
                     (cy1 - 2 - cy0) * T, RING_W, RING_HOLE)
        _blit_img(tn.bg, shaft, tx0 * T, (cy1 - 2) * T)
        # the deck, the fascia and the rail's FAR arc: Tier-1, over the shaft and
        # under the bodies (the place_each idiom, by hand — the near rail is emitted
        # separately above and place_each only knows the lower canvas)
        tn.bg.blit_cell(ring_lo, cx0 * T, cy0 * T)
        # the ladder, from the ring's fascia to the floor, ONE sprite per tree at that
        # tree's own height — place_each would stretch one across four different drops
        lx0 = cx0 + LADDER_C0
        top = cy0
        while tn.m.at(lx0, top) != "z":
            top += 1
        bot = top
        while bot + 1 < tn.m.rows_n and tn.m.at(lx0, bot + 1) == "z":
            bot += 1
        tn.bg.blit_cell(rope_ladder(DECK, BARK, salt=441, cells=bot - top + 1),
                        lx0 * T, top * T)

    # ---- walk-behind trees: TWO y-sorted World props per {T,t} component -------------
    lo, up = town_tree(tn.FOREST, tn.TRUNK, tn.GRASS)
    tn.emit_prop("TreeTrunk", "Tt", sprite_img(lo, 32, 48), each=True)
    tn.emit_prop("TreeCrown", "Tt", sprite_img(up, 32, 48), each=True,
                 top=0, base_inset=-16)

    # ---- THE UNDERSTORY: the forest floor this town stands on ------------------------
    # THE TOWN IS THE FLOOR NOW, so the floor has to be a forest floor everywhere and
    # not only in the tree shade. The first pass dressed a cell only if a trunk, a foot
    # or a ring's fascia stood within three rows north of it, which is a band round each
    # tree and nothing else — and the rest of an 80x56 clearing came out a flat green
    # LAWN with four trees standing on it.
    #
    # DENSITY IS A GRADIENT, NOT A COIN-FLIP, and that is the whole idea. Leaf drift and
    # undergrowth pile up against whatever stands still — the forest wall, a trunk, a
    # town tree — and thin out across the middle, where the town walks. So every cell is
    # scored by its distance to the nearest WILD thing and the odds fall off with it,
    # which gives a floor that is thick at the edges, worn down the lane, and reads as a
    # clearing somebody lives in rather than as texture applied uniformly.
    #
    # WHAT IT IS DRESSED WITH MATTERS MORE THAN HOW MUCH. Ferns, roots and saplings are
    # all drawn from the leaf ramp, so a floor dressed only in those is still green
    # dressing on green ground; "drift" — warm fallen leaves out of the timber ramp — is
    # the only piece that changes the field's HUE, so it is the common case at every
    # distance and everything else is a feature standing in it.
    ROT = [DECK[2], DECK[3], DECK[3], DECK[4], DECK[4], DECK[5]]
    # SEVERAL SALTED VARIANTS PER KIND, and the count is not decoration. A litter
    # cell is fully opaque, so each variant costs exactly ONE atlas tile — and with
    # one variant apiece the drift, which is half the pool by design, is the SAME
    # sixteen pixels repeated three hundred times across the clearing. At this
    # density that is not texture, it is wallpaper, and the eye finds the period
    # immediately. Five drifts and three ferns cost eight tiles and the repeat
    # stops being visible.
    VARIANTS = (("drift", 5), ("fern", 3), ("sapling", 2), ("roots", 2),
                ("log", 2), ("shroom", 1))
    under = {k: [understory(FOL, ROT, tn.GRASS, kind=k, salt=461 + 31 * i + 7 * v)
                 for v in range(n)]
             for i, (k, n) in enumerate(VARIANTS)}
    # chance out of 16, then the pool, by distance to the nearest wild cell
    NEAR = ("drift", "fern", "drift", "fern", "roots", "drift", "log", "shroom")
    MID = ("drift", "fern", "drift", "sapling", "drift", "roots", "drift", "fern")
    FAR = ("drift", "sapling", "drift", "drift", "fern", "drift")
    LITTER = {1: (8, NEAR), 2: (6, NEAR), 3: (5, MID), 4: (4, MID),
              5: (3, FAR), 6: (2, FAR)}
    wild = "#Tt" + SHADERS              # forest wall, town trees, the great trees
    dist = _wild_dist(tn.m, wild, max(LITTER))
    for y in range(tn.m.rows_n):
        for x in range(tn.m.cols):
            if tn.m.at(x, y) not in ".,":
                continue
            # NEVER over a struct's contact band. _ground_overlays has already darkened
            # the top three pixel rows of the cell south of anything built, and an
            # opaque litter cell blitted on top erases exactly those rows — which
            # unsticks the cottage, the well or the stall from the ground it sits on.
            # `greattrunk` is the deliberate exception: the trees WANT their feet in the
            # litter, and that is what this pass was written for.
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

    # NO foot_shade("!") — `greattrunk` is already in _overworld_tiles.STRUCT_TERRAIN,
    # so _ground_overlays has painted a contact band on those same three pixel rows
    # already. Calling it again stacks a second band on the first and roughly doubles
    # the darkening, which is what put a hard black collar round every great tree's
    # base and made the foot read as a rectangle sitting on the grass.
    tn.write_glow(lambda img: glow(tn, img))

    # ---- NO DEPTH MASK, AND THAT IS THE POINT ------------------------------------
    # The terrace kit's `mask_band` re-draws a face's top 12px over a body pressed
    # south against it, and the ring used to ask for one on its fascia cells. It is
    # WRONG HERE, and it shipped as a 16x12 SLAB OF DECK PLANKING drawn over anything
    # standing on the row above — a body cropped to the head, one either side of the
    # ladder, which is exactly where the eye goes.
    #
    # The reason is geometric, not a tuning error. A terrace's walkable row ENDS at
    # its face: press south and your sunk feet are over the wall, so the wall's crest
    # has to come back over them. The ring's walkable deck stops a WHOLE ROW north of
    # where the fascia crescent begins (the arc is at y=92; the last standable row is
    # centred at y=72), so a body pressed south there overhangs onto more DECK — the
    # boards it is standing on — and there is nothing to swallow. Worse, the strip was
    # copied from the run's top row, which at those columns is deck rather than face,
    # so the paint it re-drew was floor.
    #
    # The ring has no face RUN at all: its fascia is a crescent painted inside one
    # sprite, not a column of band cells. So the `v` chars are gone from the grid, and
    # with them the band assert and the mask. Do not put them back without first
    # showing that a body can press against the crescent.

    assert_all(tn, map_name)
    tn.finish()
    return tn


def assert_all(tn, map_name):
    """THE ASSERT BLOCK — the "elevation system", and the reason both eras call one
    function: every failure here is SILENT otherwise. It renders, it dedupes, every
    lint in _check_art.py passes it, and it ships."""
    tn.assert_strata()
    tn.assert_door_approach(rows=2)
    tn.assert_npc_room()
    # THE COMPONENT SHAPES. Two of these authored edge-to-edge FUSE into one
    # component, one bbox and one badly stretched sprite, and nothing else complains
    # (the 2026-07-29 spruce lesson). The COUNT is asserted as well as the shape,
    # because a tree silently missing its crown would pass every other check here.
    for chars, w, h, n in ((RING_CHARS, 12, 9, 4), ("G", 14, 6, 4), ("J", 4, 2, 4),
                           ("q1", 5, 4, 1), ("w2", 5, 4, 1),
                           ("xX", 5, 4, 1), ("pP", 5, 4, 1), ("iI", 5, 4, 1),
                           ("Tt", 2, 2, 6)):
        cs = tn.comps(chars)
        assert len(cs) == n, (
            f"{map_name}.txt: {chars!r} has {len(cs)} components, want {n}")
        for c in cs:
            a, b, c2, d = tn.comp_bbox(c)
            assert (c2 - a + 1, d - b + 1) == (w, h), (
                f"{map_name}.txt: the {chars!r} component at ({a},{b}) is "
                f"{c2 - a + 1}x{d - b + 1}, want {w}x{h}")
    # THE RING'S WALKABLE CELLS ARE THE ELLIPSE'S CELLS. The disc is drawn from
    # ring_geom and the map used to be a hand-guessed blob INSIDE it: at the east and
    # west poles two whole columns of drawn decking were solid, and the north and
    # south tips were solid too, so a round platform was walked as a rectangle with an
    # invisible wall following its rim the whole way round. Nothing complained,
    # because a cell that looks like deck and stops you looks exactly like a cell you
    # have not reached yet.
    #
    # So the mask is derived, never authored: `ring_cells` rasterizes the same ellipse
    # tree_ring draws, and a cell is walkable iff its CENTRE is on decking. The trunk
    # and its ladder are skipped — they own their cells and are asserted below.
    base = ring_cells(RING_W, RING_H, hole=RING_HOLE)
    # EXCEPTION 1, and it is not a fudge: the disc's north tip is drawn, but it lies
    # under the HEART of the crown, where the leaf mass measures 96-100% opaque. A
    # body standing there is a body you cannot see — _check_art's walk-behind lint
    # says so in numbers, which is how this row was caught. The north ARC (block row
    # 1) stays walkable because the crown is perforated exactly that far and no
    # further; pushing the perforation deeper to buy four cells nobody looks at would
    # thin the leaves over the walk-behind that this town is built around.
    for r in range(RING_CROWN_ROWS):
        base[r] = [False] * len(base[r])
    for comp in tn.comps(RING_CHARS):
        cx0, cy0, _, _ = tn.comp_bbox(comp)
        # EXCEPTION 2, THE LANDING. The mask empties the south rim, correctly: the
        # arc is at y=92, so a body centred anywhere on that row has its feet past
        # it. But the ladder head is IN that rim — it is the one place you are meant
        # to stand on the lip, because standing there IS stepping onto the rungs, and
        # the ring draws its cleat and its head boards over exactly those two cells.
        # Two cells, named off the ladder itself rather than typed as a row number,
        # so a ladder that moves takes its landing with it.
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
                if ch in "Jj!z":                     # trunk, foot, ladder
                    continue
                if tn.m.legend[ch]["solid"] == want:
                    bad.append(f"({cx0 + c},{cy0 + r}) is {ch!r}, want "
                               + ("walkable deck" if want else "solid"))
        assert not bad, (
            f"{map_name}.txt: the ring at ({cx0},{cy0}) does not match the disc "
            f"tree_ring draws — " + "; ".join(bad[:6])
            + (f" (+{len(bad) - 6} more)" if len(bad) > 6 else ""))
    # THE RING IS THE FEATURE, SO ASSERT IT. Round every trunk's ring segment the
    # cells must be walkable and on ONE stratum — that is what "you can walk the full
    # circle around the tree, passing behind it" means, and it is one mistyped cell
    # away from a dead end nobody notices, because the deck still looks continuous
    # from the south, which is where the player is standing.
    for c in tn.comps("J"):
        a, b, c2, d = tn.comp_bbox(c)
        ring = [(a - 1, b), (c2 + 1, b), (a - 1, d), (c2 + 1, d),
                ((a + c2) // 2, b - 1), ((a + c2) // 2, d + 1)]
        strata = set()
        for rx, ry in ring:
            s = tn.m.stratum(rx, ry)
            assert s is not None, (
                f"{map_name}.txt: the trunk at ({a},{b}) has no ring — ({rx},{ry}) "
                f"is solid, so you cannot walk round this tree")
            strata.add(s)
        assert len(strata) == 1, (
            f"{map_name}.txt: the ring round the trunk at ({a},{b}) spans strata "
            f"{sorted(strata)} — a ring is one storey")
    # EVERY LADDER MUST BE BOXED IN BY ITS OWN TRUNK. A link is exempt from the
    # fusion rule, so a ladder with open floor beside it passes assert_strata and
    # still lets you walk sideways off rung eight onto ground thirty feet below.
    for c in tn.comps("z"):
        a, b, c2, d = tn.comp_bbox(c)
        for y in range(b, d):                       # every row but the last
            for x in (a - 1, c2 + 1):
                ch = tn.m.at(x, y)
                assert ch in "jJ!yv", (
                    f"{map_name}.txt: the ladder at ({a},{b}) has {ch!r} beside it "
                    f"at ({x},{y}) — a ladder needs solid timber both sides or it "
                    f"is a walkable ramp into thin air")
        assert not tn.m.legend[tn.m.at(a, d + 1)]["solid"], (
            f"{map_name}.txt: the ladder at ({a},{b}) ends on solid ground at "
            f"({a},{d + 1}) — it joins its ring to nothing")
    # assert_reachable LAST, and with BOTH arrivals: the player can enter this town
    # at the south gate or on Basil's own doorstep, up the tree.
    tn.assert_reachable("exit_south", "home")
