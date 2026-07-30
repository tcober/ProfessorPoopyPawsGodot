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
from _overworld_tiles import OverWorld, T
from _tilekit import sprite_img, VOID, IRON
from _culture_props import notice_board, PAPER_STOCK
from _town_props import (town_cottage, town_academy, town_well, town_lamp,
                         town_stall, town_fountain, town_stairs, town_cliff,
                         town_cliff_return, town_tree, town_fence, bridge_fascia)
from _tree_props import (tree_edge, tree_edge_return, tree_span_edge, tree_hut,
                         tree_bridge, tree_canopy, rope_ladder, understory,
                         great_trunk, great_crown, BARK,
                         dinghy_lift_head, dinghy_lift_car, dinghy_lift_drum)

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
TRUNK_SPANS = [(3, 4), (7, 9), (12, 13), (17, 19), (20, 22)]
TRUNK_NAMES = [("J", "TrunkHi"), ("%", "TrunkHiFascia"), ("j", "TrunkLo"),
               ("&", "TrunkLoFascia"), ("!", "TrunkFoot")]
TRUNK_W = 64
TRUNK_LEAN = 3.0
CROWN_W = 112              # wider than its channel, so the crown spills over the bays
                           # — most of what makes both references read as villages
                           # nested in trees rather than as streets with trees on them

# every char that casts shade on the floor below it, for the understory pass
SHADERS = "v&Qaj!%JgC"
# every char whose cell the night-glow must be WIPED off — see the clip pass
FACES = "v&Qy%CajJ!"
# stamp_columns picks its face variant with h2(tx, ty, salt) % len(sprites), and the
# LAST variant is the one carrying a lantern. The glow pass repeats that arithmetic
# rather than being handed a list, so the lights can never drift off the lanterns:
# one source of truth, evaluated twice.
LANTERN_OF = 6                     # variants per band
BAND_SALT = {"y%": 53, "v&Q": 57}  # must match the stamp_columns calls below


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


def build(map_name, scene_key, glow, open_door=False):
    """Paint one era of Alembic Town and finish it. Returns the TileScene."""
    tn = OverWorld(map_name, scene_key)
    ROOFB = tn.mat("roof_blue")
    ROOFG = tn.mat("roof_green")
    PLAST = tn.mat("plaster")
    STONE = tn.ROCK                    # town masonry = the scene's violet slate
    DECK = tn.DECK                     # the boardwalk's hand-pinned timber
    FACE = shaded(DECK)                # ...the same timber, turned edge-on
    FOL = tn.FOREST                    # the canopy's leaf

    tn.paint_terrain()

    # ---- the buildings, each a single Tier-3 y-sorted World sprite ------------------
    # Native y-sort sorts the whole building against a body at the front-wall
    # baseline, which retires the upper-layer roof + ridge-cap + _eave_lift mask band
    # this scene used to need. The char triples stay (solid facade + roof + ridge
    # digit) purely for collision and the footprint bbox.
    #
    # THE CANOPY BUILDINGS ARE BOUGH HUTS, not cottages, and that is the note the
    # first canopy pass earned: plaster walls and leaf-canopy roofs on a boardwalk
    # read as a raised HIGH STREET, because the silhouette is still a rectangular
    # cottage. A treehouse village reads as one from its silhouette and nothing else
    # — a CONE over a woven BARREL on a PORCH (see tree_hut, and the Slitherbough /
    # Endor references it is drawn from). The GROUND buildings keep Alembic's own
    # plaster-and-cement language on purpose: the old village on the forest floor,
    # the woven canopy above it, and the two do not have to be the same town.
    tn.emit_prop("Home", "hH3",
                 tree_hut(DECK, FOL, DECK, BARK, composite=True, frames=8), hframes=8)
    tn.emit_prop("Hut", "nN0",
                 tree_hut(DECK, FOL, DECK, BARK, salt=487, composite=True, frames=8),
                 hframes=8, each=True)
    tn.emit_prop("Weapons", "xX7",
                 tree_hut(DECK, FOL, DECK, BARK, salt=483, composite=True, frames=8,
                          h=64, wares=True, sign="sword"), hframes=8)
    tn.emit_prop("Items", "pP8",
                 tree_hut(DECK, FOL, DECK, BARK, salt=485, composite=True, frames=8,
                          h=64, wares=True, sign="flask"), hframes=8)
    tn.emit_prop("Inn", "iI9",
                 tree_hut(DECK, FOL, DECK, BARK, salt=489, composite=True, frames=8,
                          h=64, wares=True, sign="kettle"), hframes=8)
    tn.emit_prop("CottageW", "q14",
                 town_cottage(ROOFG, PLAST, salt=211, composite=True, frames=4),
                 hframes=4)
    tn.emit_prop("CottageE", "w25",
                 town_cottage(ROOFB, PLAST, salt=211, composite=True, frames=4),
                 hframes=4)
    tn.emit_prop("Academy", "kK6",
                 town_academy(ROOFB, STONE, composite=True, frames=4,
                              open_door=open_door), hframes=4)
    tn.place("S", town_stairs(STONE))

    # street furniture is Tier 3: free-standing (bodies pass both north and south of
    # it), so the art rides y-sorted World entities spawned from the props manifest;
    # the map chars keep the solid collision and anchor the glow dabs
    tn.bake_shadow("oO", 3)
    tn.emit_prop("Fountain", "oO", town_fountain(STONE, frames=4), hframes=4)
    tn.emit_prop("Well", "uU", sprite_img(town_well(STONE), 32, 32))
    tn.emit_prop("Lamp", "lL", sprite_img(town_lamp(), 16, 32), each=True)
    tn.emit_prop("Stall", "m", sprite_img(town_stall(), 48, 32))
    # THE NOTICE BOARD, free-standing in the stair plaza. `bake_shadow(each=True)`
    # per the builder's own contract: its contact band is deliberately NOT drawn
    # into the sprite, and a merged bbox would smear one band across the gap
    # between two boards (the hall-benches lesson).
    tn.bake_shadow("*", 3, each=True)
    tn.emit_prop("Notice", "*",
                 sprite_img(notice_board(DECK, PAPER_STOCK, IRON), 48, 32),
                 each=True)
    # the fences y-sort like everything a body can stand both sides of (2026-07-19):
    # F = the 3-cell orchard gate runs, G = the 5-cell run
    tn.emit_prop("Fence", "F", sprite_img(town_fence(3), 48, 16), each=True)
    tn.emit_prop("FenceLong", "G", sprite_img(town_fence(5), 80, 16))

    # ---- THE GREAT TRUNKS ----------------------------------------------------------
    # One virtual trunk sliced into its five segments, so the bark bands, the grooves,
    # the taper and the burls are continuous across all of them and the seams fall
    # exactly where the ring decks are. `each=True` gives one sprite per component and
    # there are five identical components per char — asserted below, because two
    # trunks authored edge-to-edge would FUSE into one component and one stretched
    # sprite (the 2026-07-29 spruce lesson) and nothing else complains.
    #
    # THE LEAN is what stops five trunks cut from one builder reading as a colonnade.
    # It is per-CHANNEL, so it cannot vary within a trunk — which is right: a tree
    # leans one way all the way up.
    segs = great_trunk(BARK, tn.GRASS, TRUNK_SPANS, salt=401, w=TRUNK_W,
                       lean=TRUNK_LEAN)
    for (ch, name), img in zip(TRUNK_NAMES, segs):
        tn.emit_prop(name, ch, img, each=True)
    # THE CROWN carries `top=0, base_inset=-16`, and both halves matter. `top=0`
    # anchors the leaves at the footprint's TOP instead of bottom-anchoring them, and
    # the inset pushes the sort key SOUTH of a body standing on the ring's north arc,
    # so the leaves draw IN FRONT of whoever is walking behind the tree. Without it
    # the player walks over their own canopy; with it they read through the gaps
    # between lobes, which is why the mass has to stay perforated.
    tn.emit_prop("Crown", "g",
                 sprite_img(great_crown(FOL, BARK, salt=451, w=CROWN_W, h=48,
                                        lean=TRUNK_LEAN), CROWN_W, 48),
                 each=True, top=0, base_inset=-16)

    # ---- THE FACE BANDS ------------------------------------------------------------
    # One 16 x T*run opaque column per vertical run, hash-picked from three salted
    # variants (the meadow-boulder per-cell pattern — opaque and un-outlined, so a
    # whole band dedupes to a handful of tiles). The Academy's stone terrace and the
    # canopy's two timber fascias are the SAME idiom on the same primitive, which is
    # the point: verticality here is authoring.
    #
    # `y%` and `v&Q` each go in ONE call because the trunk-crossing and shaft chars
    # are PAINT TWINS of the fascia — the band runs unbroken across them and the
    # trunk's own sprite hangs in front of finished fascia art rather than raw fabric.
    # mask_band below is called on the fascia chars ONLY.
    cliffs = [town_cliff(tn.ROCK, tn.GRASS, salt=s) for s in (291, 293, 297)]
    cliff_ret = (town_cliff_return(tn.ROCK, tn.GRASS, face=-1, cap=True),
                 town_cliff_return(tn.ROCK, tn.GRASS, face=-1, cap=False),
                 town_cliff_return(tn.ROCK, tn.GRASS, face=1, cap=True),
                 town_cliff_return(tn.ROCK, tn.GRASS, face=1, cap=False))
    tn.stamp_columns("C", cliffs, ret=cliff_ret)
    # SIX variants, and the sixth carries a hanging lantern — so a boardwalk edge
    # gets a light roughly every six tiles instead of a string of them. The glow
    # pass recomputes these same hashes (see LANTERN_VARIANTS) to put a warm dab on
    # exactly the columns that have one.
    edge3 = [tree_edge(FACE, FOL, salt=s, h=48) for s in (471, 473, 477, 479, 481)]
    edge3.append(tree_edge(FACE, FOL, salt=483, h=48, lantern=True))
    ret3 = (tree_edge_return(FACE, FOL, face=-1, cap=True),
            tree_edge_return(FACE, FOL, face=-1, cap=False),
            tree_edge_return(FACE, FOL, face=1, cap=True),
            tree_edge_return(FACE, FOL, face=1, cap=False))
    tn.stamp_columns("y%", edge3, salt=53, run=3, ret=ret3)
    tn.stamp_columns("v&Q", edge3, salt=57, run=3, ret=ret3)
    tn.foot_shade("C")
    tn.foot_shade("y%")
    tn.foot_shade("v&Q")

    # ---- the Tier-1 canopy: rope ladders and rope spans -----------------------------
    # place_each, never place: two ladders sharing a char would make place() blit one
    # sprite across their combined bbox, i.e. across the whole town.
    tn.place_each("z", rope_ladder(DECK, cells=3))
    tn.place_each("Z", rope_ladder(DECK, cells=3))
    # The spans are blitted PER COMPONENT rather than by place_each, because a span's
    # length is a MAP decision and place_each would silently stretch one sprite across
    # two of different lengths.
    for chars in ("R", "W"):
        for comp in tn.comps(chars):
            x0, y0, x1, y1 = tn.comp_bbox(comp)
            assert y1 - y0 == 1, "a span is TWO rows deep (the rails live in row 2)"
            tn.bg.blit_cell(tree_bridge(DECK, cells=x1 - x0 + 1, salt=431 + x0),
                            x0 * T, y0 * T)

    # ---- the canopy's other Tier-3 props --------------------------------------------
    # The walkable bough masses, as the town_conifer split pair: the leaves ride their
    # own sprite whose y-sort baseline is pushed a tile SOUTH so it beats a body
    # standing among them. Two chars because a walkable char carries exactly one
    # stratum and these sit on two different storeys.
    bough_lo, bough_up = tree_canopy(FOL, BARK)
    for ch in ("c", "A"):
        tn.emit_prop("Bough" + ch.upper(), ch, sprite_img(bough_lo, 48, 48), each=True)
        tn.emit_prop("BoughLeaves" + ch.upper(), ch, sprite_img(bough_up, 48, 48),
                     each=True, top=0, base_inset=-16)
    # THE DINGHY LIFT, three pieces down one column. The car is an 8-frame sheet: it
    # swings a pixel either way on a symmetric zero-mean cycle (so the sway can never
    # read as travel) while its bow lantern breathes.
    tn.emit_prop("LiftHead", "M", sprite_img(dinghy_lift_head(DECK, BARK, STONE),
                                             48, 48))
    tn.emit_prop("LiftCar", "Q", dinghy_lift_car(DECK, composite=True, frames=8),
                 hframes=8)
    tn.emit_prop("LiftDrum", ":+", sprite_img(dinghy_lift_drum(DECK, STONE), 48, 32))

    # ---- walk-behind trees: TWO y-sorted World props per {^,T,t} component -----------
    # The opaque TRUNK sprite sorts at the footprint's south edge; the CROWN sprite's
    # baseline is pushed ~1 tile SOUTH (base_inset=-16) so the canopy overhangs — a
    # body beside the trunk tucks behind it, a body a tile south walks out in front.
    lo, up = town_tree(tn.FOREST, tn.TRUNK, tn.GRASS)
    tn.emit_prop("TreeTrunk", "Tt^", sprite_img(lo, 32, 48), each=True)
    tn.emit_prop("TreeCrown", "Tt^", sprite_img(up, 32, 48), each=True,
                 top=0, base_inset=-16)

    # ---- THE UNDERSTORY: the shaded floor a canopy town stands over ------------------
    # Zero new legend chars, and the rule is DERIVED rather than authored: a ground
    # cell within three rows south of a fascia, a bough or a great trunk is in that
    # thing's shade, so it gets forest-floor litter instead of lawn. Without it the
    # floor reads as a bright green LAWN under a treehouse village, which is the
    # second-loudest thing wrong with a first pass (the first is always the buildings).
    #
    # The litter's WOOD is the deck ramp's DARK HALF, not the ramp itself: handed the
    # whole thing, the root humps came out in the boardwalk's pale honey and read as
    # scattered straw on a lawn. Wet wood on a forest floor is the darkest thing in
    # frame. FERNS carry it, because a clump of fronds is the one understory shape
    # that reads at 16px; mushrooms are the single pale accent and stay rare.
    ROT = [DECK[2], DECK[3], DECK[3], DECK[4], DECK[4], DECK[5]]
    under = [understory(FOL, ROT, tn.GRASS, kind=k, salt=461 + i)
             for i, k in enumerate(("fern", "fern", "fern", "roots", "fern",
                                    "log", "shroom"))]
    for y in range(tn.m.rows_n):
        for x in range(tn.m.cols):
            if tn.m.at(x, y) not in ".,":
                continue
            if not any(tn.m.at(x, y - d) in SHADERS for d in (1, 2, 3)):
                continue
            # ONE CELL IN THREE. The floor has to stay mostly open: litter on every
            # shaded cell is not a forest floor, it is a rug — and foot_shade's band
            # is already doing half this job.
            if h2(x, y, 467) % 3:
                continue
            tn.bg.blit_cell(under[h2(x, y, 463) % len(under)], x * T, y * T)

    tn.write_glow(lambda img: glow(tn, img))

    # ---- the SPANS' upper-layer fascias ---------------------------------------------
    # A span's south row is a ONE-row solid strip between two walkable rows, which the
    # z-order doctrine forbids banding outright (the corridor feet and the south head
    # want the same 12px and one of them always wears it). So it gets AUTHORED art on
    # the upper layer instead — the shipped bridge_fascia idiom — laid on the lower
    # canvas too so the cell never shows raw fabric, at the same coordinates so the
    # two copies can never seam.
    span_edge = tree_span_edge(FACE)
    for y in range(tn.m.rows_n):
        for x in range(tn.m.cols):
            if tn.m.at(x, y) in "Ee":
                tn.bg.blit_cell(span_edge, x * T, y * T)
                tn.upper_cell(x, y, span_edge)

    # ---- DEPTH MASKS ----------------------------------------------------------------
    # A body's collision box hugs its FEET, so pressed south into any solid cell ~11px
    # of sprite hangs past the physics boundary and draws over whatever is below —
    # "the player stands off the edge of the cliff". The face's own top 12px,
    # re-emitted as a Tier-3 Y-SORTED strip keyed at run_top-8, swallow exactly that
    # sliver. MUST come after every lower-canvas write, because it copies FINISHED art.
    #
    # AND ON THE FASCIA CHARS ONLY — never on the trunk-crossing twins `%` / `&`, and
    # never on the lift's `Q`. All three for the same reason: those cells' art is a
    # Tier-3 TRUNK or a BOAT, not the fascia a strip would copy, so a strip there
    # prints fascia planking over the trunk. The trunk's own crossing segment already
    # masks the deck edge in its channel (its footprint's south edge sits below a
    # pressed body's origin), and at the lift the unmasked 3-cell gap in the railing
    # IS the gate you step through onto the boat.
    tn.mask_band("C")
    tn.mask_band("y")
    tn.mask_band("v")
    # The same bug at the creek: standing on the footbridge's south end, a body sinks
    # into the water cell below. That cell ANIMATES on four frames, so a mirrored band
    # would freeze its top half — paint a static near-rail instead.
    for comp in tn.comps("="):
        bx0, by0, bx1, by1 = tn.comp_bbox(comp)
        for bx in range(bx0, bx1 + 1):
            if tn.m.at(bx, by1 + 1) == "r":
                tn.upper_cell(bx, by1 + 1, bridge_fascia(tn.BRIDGE))

    assert_all(tn, map_name)
    tn.finish()
    return tn


def assert_all(tn, map_name):
    """THE ASSERT BLOCK — the elevation "system", and the reason both eras call one
    function: every failure here is SILENT otherwise. It renders, it dedupes, every
    lint in _check_art.py passes it, and it ships."""
    tn.assert_strata()
    tn.assert_band_orientation("C", "ground", "canopy_hi")
    tn.assert_band_orientation("y%", "canopy_hi", "canopy_lo")
    tn.assert_band_orientation("v&Q", "canopy_lo", "ground")
    tn.assert_span("R", "E")
    tn.assert_span("W", "e")
    tn.assert_stair("S", "C", 2)
    tn.assert_stair("z", "y%", 3)
    tn.assert_stair("Z", "v&", 3)
    tn.assert_lift("M", "Q", ":", "+", canopy="canopy_lo")
    tn.assert_door_approach(rows=2)
    tn.assert_npc_room()
    # THE COMPONENT SHAPES, and the reason is the 2026-07-29 spruce lesson: two of
    # these authored edge-to-edge FUSE into one component, one bbox and one badly
    # stretched sprite, and nothing else complains. The COUNT is asserted as well as
    # the shape, because a channel silently missing its shaft would otherwise pass
    # every other check here.
    for chars, w, h, n in (("g", 5, 3, 5), ("J", 3, 2, 5), ("%", 5, 3, 5),
                           ("j", 3, 2, 5), ("&", 5, 3, 5), ("!", 3, 3, 5),
                           ("c", 3, 3, 2), ("A", 3, 3, 1), ("*", 3, 2, 1),
                           ("hH3", 6, 5, 1), ("nN0", 6, 5, 2),
                           ("xX7", 6, 4, 1), ("pP8", 6, 4, 1), ("iI9", 6, 4, 1),
                           ("Tt^", 2, 3, 12)):
        cs = tn.comps(chars)
        assert len(cs) == n, (
            f"{map_name}.txt: {chars!r} has {len(cs)} components, want {n}")
        for c in cs:
            a, b, c2, d = tn.comp_bbox(c)
            assert (c2 - a + 1, d - b + 1) == (w, h), (
                f"{map_name}.txt: the {chars!r} component at ({a},{b}) is "
                f"{c2 - a + 1}x{d - b + 1}, want {w}x{h}")
    # THE RING IS THE FEATURE, SO ASSERT IT. For every trunk channel, on every
    # walkable storey, the cells around the shaft must be walkable and on ONE stratum
    # — that is what "you can walk the full circle around the tree" means, and it is
    # one mistyped cell away from a dead end nobody notices, because the deck still
    # looks continuous from the south where the player is standing.
    # J and j ONLY. The foot has no ring and must not: it meets the low fascia
    # directly, because two rows of open floor between them made every great tree
    # read as a STUMP — and you cannot walk between a trunk and the structure
    # behind it anyway. The raised circular walk belongs to the canopy storeys.
    for ch in ("J", "j"):
        for c in tn.comps(ch):
            a, b, c2, d = tn.comp_bbox(c)
            ring = [(a - 1, b), (c2 + 1, b), (a - 1, d), (c2 + 1, d),
                    ((a + c2) // 2, b - 1), ((a + c2) // 2, d + 1)]
            strata = set()
            for rx, ry in ring:
                s = tn.m.stratum(rx, ry)
                assert s is not None, (
                    f"{map_name}.txt: the {ch!r} trunk at ({a},{b}) has no ring — "
                    f"({rx},{ry}) is solid, so you cannot walk round this tree")
                strata.add(s)
            assert len(strata) == 1, (
                f"{map_name}.txt: the ring round the {ch!r} trunk at ({a},{b}) "
                f"spans strata {sorted(strata)} — a ring is one storey")
    # assert_reachable LAST, and with BOTH arrivals: this town has four storeys and
    # the player can enter it at the south gate or on Basil's own doorstep.
    tn.assert_reachable("exit_south", "home")
