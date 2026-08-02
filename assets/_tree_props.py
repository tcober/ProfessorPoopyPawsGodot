#!/usr/bin/env python3
"""TREEHOUSE-TOWN prop kit — the canopy stratum of a town built in the boughs,
at ZONE scale (48px character cell, 33px figure, 16px tiles).

The vocabulary is the same naturey-steampunk alchemist-botanist language the
Alembic buildings speak (leaf-canopy roofs over light-cement walls, twisty
copper pipes, planters, brass rain caps) — this module adds what a
canopy town needs and a ground town does not: a GREAT TRUNK to build on, a plank
DECK to build the house on, a rope BRIDGE between decks, and — because nothing
vertical up here is masonry — a ROPE LADDER and the counterweighted DINGHY LIFT
for the way up, plus the walk-behind BOUGH masses that hide a deck's underside
and the UNDERSTORY dressing for the shaded ground far below.

HOW THIS KIT DIFFERS FROM _town_props, deliberately:

  * every builder takes its MATERIAL RAMPS as parameters. `_town_props`'
    naturey helpers close over module-level FOLIAGE/CEMENT because Alembic and
    its icon share one palette; a canopy town is a different scene with a
    different leaf and a different plaster, and a builder that can't be handed
    a ramp can't be reused across the two. Only the game's shared HARDWARE
    STORE (copper, brass, iron, the WARM candle pair) is taken as read.
  * the deck is a FLOOR, so its plank field is written 16-periodic on purpose
    (see tree_platform): the whole open deck collapses to a couple of atlas
    tiles instead of one per cell.
  * nothing here stands on soil. A canopy house's footing is a timber SILL
    PLATE on joists, never a stone plinth, and every piece that meets a deck
    edge shows its joists/underside so the eye reads a structure with air under
    it rather than a rug lying on the ground.

Palette discipline (docs/DESIGN.md "Art Direction"): hard flat bands, NO dither
inside a form (`_propkit.S` pins the Sprite's jitter to 0, so ball/capsule/tri
come out as clean CT bands). Wood is honest warm brown; mud fields and
un-hue-shifted grey darks are banned. Hemp and mushroom ivory are the only two
new materials and BOTH ARE HAND-PINNED — see the note at ROPE for why deriving
them made every rope in this kit a pink barber pole.

THE T3 COVERAGE FLOOR, checked for every builder. `_check_art.py`'s
invisible-wall lint exempts a SOLID footprint cell only where the prop's frame-0
art covers >= 20% of its 16x16 square (`T3_COVER_MIN`); below that the deduped
atlas hands the cell the same tile as open ground, i.e. a wall you can see
through and still bounce off. Every builder's docstring carries its MEASURED
per-cell floor. Three pieces are under the line and must be typed WALKABLE, which
is what they want anyway because all three hang overhead: `tree_canopy` (0.0%,
both halves — a round mass leaves its corner cells empty), `dinghy_lift_head`
(0.4%) and `dinghy_lift_car` (0.0%). Everything else clears it with room:
`understory` / `tree_platform` / `rope_ladder` at 100% (opaque by construction),
`tree_bridge` 80.5%, `dinghy_lift_drum` 90.2% on its solid row, `tree_trunk`
82.0% on its solid base, `tree_house` 43.0%.

Stdlib-only, deterministic (fixed salts). Consumed by a
assets/_gen_tileset_<canopytown>.py exactly the way _gen_tileset_lanternwood.py
consumes _town_props: place()/place_each() for the Tier-1 opaque pieces,
emit_prop() for the Tier-3 y-sorted ones.
"""
import math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_props import _chimney, DOORDARK, WARM, WARMD
from _propkit import S, ln, edge, split_rows
from _tilekit import (ramp, Img, BRASS, COPPER, IRON, SPEC, STEAM, STEEL, GLASS,
                      MINT, VIOLETF)
from _town_props import (_anim_building, _breathe, _finish, _ph, _pv, _valve,
                         clipw, WIN_PULSE)

# ---- the two new materials ----------------------------------------------------------
# Everything else a canopy town is built of already exists: TIMBER/COPPER/
# BRASS/IRON from the shared hardware store, and the scene's own leaf, plaster,
# bark and ground ramps handed in by the generator.
# BOTH ARE HAND-PINNED, and they have to be. ramp() pulls a dark end toward
# violet AND raises its saturation, which is the law that makes BRASS[2..3]
# unusable — and a warm tan seed goes through it into hot magenta. Derived, every
# rope in this kit came out a candy-pink barber pole and every mushroom cap a
# pink toadstool: the exact "very kiddy" failure mode, arrived at by obeying the
# palette code instead of the palette doctrine. Hemp's darks are warm BROWN and
# the mushroom's gills are a violet-GREY, and neither can be derived.
ROPE = ((234, 208, 160, 255), (196, 164, 116, 255),      # hemp: handrails,
        (144, 114, 82, 255), (94, 70, 58, 255))          # lashings, falls
SHROOM = ((248, 242, 228, 255), (214, 204, 190, 255),    # bone-ivory caps — the
          (158, 150, 158, 255), (98, 90, 112, 255))      # understory's one pale
                                                         # accent. Keep it rare.
# THATCH — dry reed, for the huts' conical roofs. Hand-pinned for the third time
# for the same two reasons ROPE is: a straw seed run through ramp() comes out
# GREEN under a teal scene bias and MAGENTA under a violet one, and a thatch roof
# is the largest single area of a canopy town's silhouette, so it is the last
# place to let the palette code overrule the palette doctrine. Six tones, because
# a cone needs real midtone form: the lit crown, two face bands, the shaded flank,
# and two for the eave fringe's own shadow.
THATCH = ((246, 222, 158, 255), (226, 190, 118, 255), (196, 154, 88, 255),
          (154, 112, 70, 255), (108, 74, 62, 255), (66, 44, 54, 255))
# BARK — the fourth hand-pinned material, and the one with the most riding on it,
# because a great trunk is the LARGEST SINGLE MASS in a canopy town's frame.
#
# The scene's own `trunk` seed is (52, 62, 118): a cold blue-violet, which is
# correct for a distant conifer read against sky on the overworld and completely
# wrong here. Run up to a 350px column it stops being a tree — a huge, smooth,
# blue-grey cylinder is a STONE PIER, and six of them turn a village in the
# boughs into a viaduct. The first preview of the armature was exactly that.
#
# So: honest warm brown, which the palette doctrine explicitly permits for wood,
# with the darks pulled toward violet by hand so it still sits in a teal-biased
# scene rather than glowing orange out of it. Six tones because a cylinder this
# wide needs real midtone form — two lit bands, two turning, two in core shadow.
# Kept clearly DARKER than DECK's honey (240/214/192 at the light end) so a trunk
# never reads as more boardwalk where the two meet, which is the whole risk of
# building both out of wood.
BARK = ((178, 134, 96, 255), (148, 106, 76, 255), (118, 82, 64, 255),
        (88, 60, 58, 255), (58, 40, 52, 255), (34, 24, 38, 255))


# ---- shared sub-builders ------------------------------------------------------------

def _crop(sp, w, h):
    """Clear every pixel outside the w x h footprint — the un-outlined cousin
    of `_propkit.edge(h)` + `_town_props.clipw(w)`, for the OPAQUE tiled pieces
    (deck, bridge, stair, understory) that carry no silhouette and must never
    bleed one pixel onto the cell beyond their footprint."""
    for y in range(sp.n):
        row = sp.px[y]
        for x in range(sp.n):
            if x >= w or y >= h:
                row[x] = None


# A bark cylinder as SEVEN hard flat bands, west (lit) to east (core shadow).
# Not a gradient and not a dither: at 16px tiles a trunk reads as a cylinder
# only if the bands are wide, flat and deliberate, which is the whole CT-chunk
# lesson. The thin dark band at t<0.07 is the west rim turning away from the
# camera — without it the lit band runs off the silhouette and the trunk goes
# flat.
_BARK_BANDS = ((0.07, 2), (0.26, 0), (0.48, 1), (0.69, 2), (0.86, 3),
               (0.95, 4), (1.01, 5))


def _bark_index(t):
    """Ramp index for a position `t` in 0..1 across a bark cylinder."""
    for lim, k in _BARK_BANDS:
        if t < lim:
            return k
    return 5


def _shaft(sp, bark, cx, y0, y1, half0, half1, salt,
           grooves=(0.13, 0.31, 0.52, 0.72, 0.89), lean=0.0):
    """A hard-banded bark cylinder from y0 (half-width `half0`) to y1
    (`half1`), with broken vertical grooves at the given width fractions.

    The grooves BREAK — a groove run every ~6px is skipped on a hash — because
    an unbroken 1px line down 80px of trunk reads as a seam in the art rather
    than as bark. Each groove sits two ramp steps under its own band, so a
    groove in the lit band stays lighter than the shadow band beside it and the
    cylinder never loses its form to the texture.

    `lean` slides the centreline by that many px from y0 to y1, so a tall trunk
    can be off-plumb. Over the ~350px of a great trunk a dead-straight shaft
    reads as a column, and six of them read as a colonnade."""
    span_y = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        u = (y - y0) / span_y
        half = half0 + (half1 - half0) * u
        mid = cx + lean * u
        xl, xr = int(round(mid - half)), int(round(mid + half))
        span = max(1, xr - xl)
        for x in range(xl, xr + 1):
            sp.set(x, y, bark[_bark_index((x - xl) / span)])
        # BARK PLATES, not stripes. A groove that runs the whole height is a seam
        # in the art; a groove broken into 6-10px staves with the breaks staggered
        # per column is bark. The stagger comes from keying the hash on the groove
        # index as well as the row band, so two neighbouring grooves never break on
        # the same row and print a horizontal join across the trunk.
        for gi, gt in enumerate(grooves):
            if h2(gi, (y + gi * 3) // 7, salt + 3) % 4 == 0:
                continue                               # the groove breaks
            k = _bark_index(gt)
            gx = xl + int(round(span * gt))
            sp.set(gx, y, bark[min(5, k + 2)])
            # a 1px lit lip on the west side of each fissure, so the plate between
            # two grooves turns rather than sitting flat
            if h2(gi, y // 5, salt + 9) % 3:
                sp.set(gx - 1, y, bark[max(0, k - 1)])


def _leaf_mass(sp, f, lobes):
    """A cluster of round leaf lobes drawn in TWO passes — every dome first,
    then every under-arc and crown sun-catch — so the details land ON TOP of
    the neighbouring lobes instead of being buried by whichever lobe was drawn
    next. That two-pass order is the whole reason `_town_props._canopy`'s roof
    reads as several leaf masses and not as one green slab.

    `lobes` is a list of (cx, cy, r, flat, sh); `flat` squashes a lobe
    vertically (eave lobes are flatter than crown lobes)."""
    for cx, cy, r, flat, sh in lobes:
        sp.ball(cx, cy, r, r * flat, f, sh=sh, power=2.1)
    for i, (cx, cy, r, flat, sh) in enumerate(lobes):
        sp.blob(cx + r * 0.08, cy + r * 0.46 * flat,
                r * 0.58, r * 0.24 * flat, f[4])       # its own under-arc
        # THE SUN-CATCH, BROKEN INTO DABS. One smooth f[0] ellipse per lobe is
        # what made every crown in this kit read as a raft of BALLOONS: a big
        # flat highlight centred on a round mass is the shading of a sphere, and
        # a pile of shaded spheres is bubble wrap however good the silhouette
        # is. Leaves do not have one specular — they have many small ones, and
        # the gaps between them matter more than the light. So: four dabs along
        # the lobe's NW shoulder, sizes falling off, the last two a step down
        # the ramp, and each nudged on a hash so no two lobes catch the light
        # in the same place. Same pixel budget, completely different material.
        for k, (ox, oy, rk, tone) in enumerate(((-0.40, -0.34, 0.26, 0),
                                                (-0.14, -0.46, 0.20, 0),
                                                (0.12, -0.40, 0.16, 1),
                                                (-0.48, -0.04, 0.14, 1))):
            jx = ((h2(i, k, 77) % 5) - 2) * 0.035
            jy = ((h2(i, k + 8, 77) % 5) - 2) * 0.030
            rr = r * rk
            sp.blob(cx + r * (ox + jx), cy + r * (oy + jy) * flat,
                    rr, rr * 0.70 * flat, f[tone])


def _leaf_dabs(sp, f, x0, y0, x1, y1, salt, n=10):
    """Flat 2px leaf-cluster dabs plus single-pixel dapple over an ALREADY
    DRAWN leaf mass. Every dab is gated on the canvas already being filled at
    that pixel, so the texture pass can never print a stray green speck out in
    open sky (which is what makes a generated canopy look noisy)."""
    span, rise = max(1, x1 - x0), max(1, y1 - y0)
    for i in range(n):
        hx = x0 + (i * 23 + h2(i, 1, salt) % 5) % span
        hy = y0 + (i * 11 + h2(i, 2, salt) % 4) % rise
        if sp.get(hx, hy) is None or sp.get(hx + 2, hy + 1) is None:
            continue
        c, s = (f[1], f[4]) if i % 2 else (f[2], f[5])
        sp.set(hx, hy, c); sp.set(hx + 1, hy, c)
        sp.set(hx + 1, hy + 1, s); sp.set(hx + 2, hy + 1, s)
    for i in range(n):
        hx, hy = x0 + (i * 29 + 3) % span, y0 + (i * 7 + 2) % rise
        if sp.get(hx, hy) is not None:
            sp.set(hx, hy, f[1] if i % 2 else f[3])


def _canopy_roof(up, f, w, fy, salt, flue_xs=(), top=5.0):
    """A living leaf-canopy ROOF over a facade whose eave line is `fy`: round
    lobes of ONE radius keyed to the roof HEIGHT (a wider house gets MORE
    lobes, never stretched ellipses), a crown row and a flatter eave row, an
    under-rim shadow along the eave, and the copper flue caps.

    The ramp-taking twin of `_town_props._canopy`. The whole silhouette stays
    >=1px inside every canvas edge so `edge()` rings it completely (a
    half-outlined canopy reads as a crop), and the top `top` px stay clear as
    headroom for the flue caps and the steam `_anim_building` puffs above
    them."""
    r = max(7.0, (fy - top) * 0.52)
    x0, x1 = r * 1.05 + 1.0, w - r * 1.05 - 1.0
    nc = max(1, round(max(1.0, x1 - x0) / (r * 0.90)))
    # Lobe radii wobble +-8% on the salt. Identical radii at an even pitch came
    # out an ARCADE — a row of the same bump, which reads as a moulding rather
    # than as foliage.
    crown = [(x0 + (x1 - x0) * i / max(1, nc),
              top + r + (r * 0.16 if i % 2 else 0.0),
              r * (0.92 + 0.04 * (h2(i, 3, salt) % 5)), 1.0, -0.02)
             for i in range(nc + 1)]
    re = r * 0.78
    ex0, ex1 = re + 1.5, w - re - 2.5
    ne = max(1, round(max(1.0, ex1 - ex0) / (re * 1.05)))
    # The eave lobes keep `_town_props._canopy`'s geometry EXACTLY —
    # cy = fy - re*0.55, flat 0.80, sh 0.08 — and that is a correction of my own
    # second pass, not an accident. A row of overlapping domes puts the ramp's
    # darkest tone round every bottom arc and they merge into a dark band along
    # the eave; I read that as a painted stripe and lifted the lobes clear of the
    # wall to kill it. Rendering the shipped `town_cottage` beside this at 4x
    # settled it: the band is in the shipped art too, it is the canopy's shaded
    # UNDERSIDE, and lifting the lobes only exposed MORE of the arc above the
    # wall line. The additions that did help are kept: the radius wobble, the
    # broken under-rim, and the leaf-tip fringe below.
    eave = [(ex0 + (ex1 - ex0) * i / max(1, ne), fy - re * 0.55,
             re * (0.94 + 0.03 * (h2(i, 5, salt) % 5)), 0.80, 0.08)
            for i in range(ne + 1)]
    _leaf_mass(up, f, crown + eave)
    for x in range(1, w - 1):
        top_y = None
        for y in range(int(fy) - 1, int(fy) - 12, -1):
            if up.get(x, y) is not None:
                top_y = y
                break
        if top_y is None:
            continue
        n = 1 + h2(x // 3, 9, salt) % 4                # 1-4px of leaf tip
        for k in range(1, n + 1):
            if top_y + k >= fy:
                break
            up.set(x, top_y + k, f[2] if k == 1 else f[3] if k < n else f[4])
    _leaf_dabs(up, f, 3, int(top) + 2, w - 4, int(fy) - 6, salt,
               n=max(8, w // 7))
    # The flue is keyed to the ROOF DEPTH, not to a literal 17px. On Alembic's
    # 48px-deep canopy a 20px flue is a stub poking through the leaves; on this
    # 22px-deep one the same number came out a bare copper stick as tall as the
    # roof, which read as a candle on the ridge. Half the depth, and the leaves
    # close in around its base.
    for fx in flue_xs:
        _chimney(up, fx, int(top) - 3,
                 int(top) + max(6, int((fy - top) * 0.46)))
        for dx in (-3, 4):
            if up.get(fx + dx, int(top) + 5) is not None:
                up.set(fx + dx, int(top) + 5, f[1])
                up.set(fx + dx, int(top) + 6, f[4])


def _plaster_wall(lo, wall, f, deck, w, h, fy, salt):
    """The canopy house's facade base: light-cement plaster, corner shade, the
    canopy's shadow along the eave with leaves draping over it, damp streaks —
    and a TIMBER SILL PLATE on joists where a ground house would have a stone
    footing. That swap is the single detail that says "this building is standing
    on a deck in the air"; a plinth here reads as a cottage in a hedge."""
    # wall[2] is the field, not wall[1]: a plaster ramp's second tone is nearly
    # white, and a near-white band across a whole facade is the beige/grey mud
    # field the palette law bans — it read as a hospital corridor. wall[1] is
    # spent on the two rows the eave light actually reaches.
    lo.rect(0, fy, w - 1, h - 1, wall[2])
    lo.rect(0, fy + 1, w - 1, fy + 3, wall[1])         # the rows the eave lights
    # An AO grade down to the foot, in TWO steps. One flat value over a whole
    # facade read as a hospital corridor; one hard step read as a dado rail.
    lo.rect(0, h - 13, w - 1, h - 9, wall[2])
    lo.rect(0, h - 8, w - 1, h - 5, wall[3])
    for dx in range(0, w, 2):                          # the step, broken
        lo.set(dx, h - 9, wall[3])
    lo.rect(0, fy, 1, h - 1, wall[3]); lo.rect(w - 2, fy, w - 1, h - 1, wall[4])
    # the canopy's shadow on the wall, BROKEN into dabs. Drawn as a solid inset
    # row it printed a hard 1px stripe the width of the house — a painted line,
    # not a shadow.
    for dx in range(2, w - 2):
        if h2(dx // 3, 0, salt) % 5:
            lo.set(dx, fy, f[4])
        if h2(dx // 4, 1, salt) % 3 == 0:
            lo.set(dx, fy + 1, f[5])
    for dx in range(5, w - 4, 7):                      # leaves draping over it
        lo.set(dx, fy + 1, f[2]); lo.set(dx, fy + 2, f[3])
        if dx % 2:
            lo.set(dx, fy + 3, f[4])
    for mx in range(4, w - 3, 8):                      # damp algae streaks
        for my in range(fy + 6, h - 7, 5):
            lo.set(mx, my, wall[3])
    lo.rect(0, h - 4, w - 1, h - 4, deck[0])           # the sill plate,
    lo.rect(0, h - 3, w - 1, h - 2, deck[2])           # standing proud
    lo.rect(0, h - 1, w - 1, h - 1, deck[5])           # its shadow line
    for jx in range(3, w - 2, 12):                     # the joists under it
        lo.rect(jx, h - 3, jx + 1, h - 1, deck[4])
        lo.set(jx, h - 3, deck[3])


def _hearth_window(lo, deck, x0, y0, ww, hh):
    """A fire-lit pane: WARM/WARMD glass on the two ladders `_breathe`
    recolours, timber mullions that survive the recolour (wood backlit by a
    hearth is a silhouette), a proud sill. Returns its (x, y, w, h) rect for
    the breath list."""
    lo.rect(x0 - 1, y0 - 1, x0 + ww, y0 + hh, deck[4])
    lo.rect(x0, y0, x0 + ww - 1, y0 + hh - 1, WARMD)
    lo.rect(x0 + 1, y0 + 1, x0 + ww - 2, y0 + 2, WARM)      # the fire's throw
    lo.rect(x0 + ww // 2, y0, x0 + ww // 2, y0 + hh - 1, deck[4])
    lo.rect(x0, y0 + hh // 2, x0 + ww - 1, y0 + hh // 2, deck[4])
    lo.rect(x0 - 2, y0 + hh, x0 + ww + 1, y0 + hh + 1, deck[3])
    lo.set(x0 - 2, y0 + hh, deck[1])
    return (x0, y0, ww, hh)


def _plant_window(lo, f, deck, x0, y0, ww, hh):
    """A wood-framed greenhouse pane with sprigs growing inside — the botanist
    half of the house. Deliberately UNLIT: the one lit window is the hearth,
    and a facade where every pane burns has no focus for the breath to land
    on."""
    lo.rect(x0 - 1, y0 - 1, x0 + ww, y0 + hh, deck[4])
    lo.rect(x0, y0, x0 + ww - 1, y0 + hh - 1, DOORDARK)
    lo.rect(x0, y0, x0 + ww - 1, y0, deck[2])
    lo.rect(x0 - 2, y0 + hh, x0 + ww + 1, y0 + hh + 1, deck[3])   # sill
    lo.rect(x0 + ww // 2, y0, x0 + ww // 2, y0 + hh - 1, deck[4])
    lo.rect(x0, y0 + hh // 2, x0 + ww - 1, y0 + hh // 2, deck[4])
    for i, px_ in enumerate(range(x0 + 1, x0 + ww - 1, 3)):
        lo.rect(px_, y0 + hh - 1 - (3 + i % 2), px_, y0 + hh - 1, f[2])
        lo.set(px_ + 1, y0 + hh - 3 - i % 2, f[1])
        lo.set(px_ + 1, y0 + hh - 2 - i % 2, f[4])


def _planter(lo, f, deck, x0, x1, y):
    """A plank planter box of sprigs standing on the deck (or hung under a
    sill) — the botanist's tell, and the cheapest thing that makes a wall read
    as lived-in rather than as elevation drawing."""
    lo.rect(x0, y, x1, y + 4, deck[3])
    lo.rect(x0, y, x1, y, deck[1])
    lo.rect(x0, y + 4, x1, y + 4, deck[5])
    for i, fx in enumerate(range(x0 + 2, x1, 4)):
        lo.rect(fx, y - 4 - i % 2, fx, y - 1, f[3])
        lo.set(fx + 1, y - 5 - i % 2, f[2])
        lo.set(fx - 1, y - 3, f[1])


def _plank_door(lo, deck, dx0, dx1, fy, h):
    """A plank door under a copper arch with a hemp pull, its threshold spilling
    candlelight onto the deck. The `_town_props._arch_door` idiom with the wood
    ramp handed in, plus the two canopy-town differences: the pull-rope (nobody
    forges a brass handle up a tree) and a threshold that meets PLANKS, so the
    spill lands on the deck boards instead of on soil.

    Returns the glow rect, so the doorway breathes with the hearth — one house,
    one fire."""
    lo.rect(dx0 - 2, fy + 6, dx1 + 2, h - 1, deck[4])       # casing
    for ay, ah in ((fy + 4, 0), (fy + 3, 2)):               # copper arch head
        lo.rect(dx0 - 1 + ah, ay, dx1 + 1 - ah, ay, COPPER[2])
    lo.rect(dx0, fy + 6, dx1, h - 1, DOORDARK)
    for gy in range(fy + 8, h - 1, 4):
        lo.rect(dx0, gy, dx1, gy, deck[5])                  # plank lines
    # A GLAZED LIGHT in the door's head plus the THRESHOLD spill under it. A
    # single warm band across the middle of a plank door (the first pass) read as
    # a shelf bolted to it; a small window high and light leaking low is what a
    # lit door actually looks like.
    gx0, gy0 = dx0 + 3, fy + 8
    lo.rect(gx0 - 1, gy0 - 1, dx1 - 2, gy0 + 6, deck[4])
    lo.rect(gx0, gy0, dx1 - 3, gy0 + 5, WARMD)
    lo.rect(gx0 + 1, gy0 + 1, dx1 - 4, gy0 + 2, WARM)
    lo.rect((gx0 + dx1 - 3) // 2, gy0, (gx0 + dx1 - 3) // 2, gy0 + 5, deck[4])
    lo.rect(dx0, h - 2, dx1, h - 1, WARMD)                  # spill on the deck
    lo.rect(dx0 + 3, h - 1, dx1 - 3, h - 1, WARM)
    px_ = dx1 - 3                                           # the hemp pull
    lo.rect(px_, fy + 18, px_, fy + 21, ROPE[1])
    lo.set(px_, fy + 22, ROPE[3])
    return (gx0 - 1, gy0 - 1, dx1 - gx0 + 2, 8)


def _rope(sp, x0, y0, x1, y1, phase=0, wide=False):
    """A LAID rope from (x0, y0) to (x1, y1).

    The lay — a 3px-period light/mid/dark alternation ALONG the rope — is the
    one detail that makes hemp read as rope at 16px tiles. A straight one-tone
    line at this scale is a scratch, and a straight two-tone line is a wire;
    only the periodic twist says "three strands laid up". `wide` lays a second
    strand a pixel off, out of phase, for a heavy fall or a ladder stile."""
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(int(steps) + 1):
        t = i / steps
        x = int(round(x0 + (x1 - x0) * t))
        y = int(round(y0 + (y1 - y0) * t))
        k = (i + phase) % 3
        sp.set(x, y, (ROPE[0], ROPE[1], ROPE[2])[k])
        if wide:
            dx, dy = (1, 0) if abs(y1 - y0) >= abs(x1 - x0) else (0, 1)
            sp.set(x + dx, y + dy, (ROPE[2], ROPE[3], ROPE[1])[k])


def _lash(sp, a0, a1, b, across=True):
    """A rope seizing at a joint — three turns, the middle one lit. What holds
    every joint in this town together, since nobody up a tree is driving iron
    bolts.

    `across=True` lays the turns ACROSS the member: for a HORIZONTAL beam that
    means three VERTICAL bands, which is the whole correction here. Drawn as
    horizontal bars along a horizontal log the turns read as pale slots cut into
    it — rope wrapped round a spar always crosses the spar."""
    for i, k in enumerate((b, b + 1, b + 2)):
        c = ROPE[1] if i == 1 else ROPE[2]
        if across:
            sp.rect(k, a0, k, a1, c)
            sp.set(k, a0, ROPE[0]); sp.set(k, a1, ROPE[3])
        else:
            sp.rect(a0, k, a1, k, c)
            sp.set(a0, k, ROPE[0]); sp.set(a1, k, ROPE[3])


def _pulley(sp, deck, cx, cy, r=5):
    """A PULLEY BLOCK drawn as an OPEN frame: two timber cheeks either side, an
    iron strap over the crown, and the BRASS SHEAVE fully visible turning between
    them with a dark hub and a rope groove.

    A pulley reads by its WHEEL and by nothing else. Two earlier passes hid the
    sheave — first inside a shaded dome (which read as an egg with a yolk), then
    behind a closed shell with the brass showing only in a slot at the foot
    (which read as a buoy, and the smaller one as a lantern). Show the whole
    wheel between two straight cheeks and it is a block at a glance, at any
    size."""
    cx, cy = int(cx), int(cy)
    sp.blob(cx, cy, r, r, BRASS[1])                        # the brass wheel
    sp.blob(cx - 0.6, cy - 0.6, r * 0.66, r * 0.66, BRASS[0])
    sp.blob(cx, cy, r * 0.28, r * 0.28, IRON[2])           # its hub
    sp.set(cx, cy, IRON[1])
    for k in range(-r, r + 1):                             # the rim's shaded arc
        for q in (-1, 1):
            y = cy + int(round(q * (r * r - k * k) ** 0.5))
            if q > 0 or k > 0:
                sp.set(cx + k, y, IRON[3])
    # The cheeks are OPEN at the foot and there is no disc behind the wheel. Both
    # were in the previous pass and together they closed the block into a dark
    # rectangle with a coin in it — a picture frame. A block's rope has to be able
    # to LEAVE, and the eye needs to see it can.
    for sx in (cx - r - 2, cx + r + 1):                    # the timber cheeks
        sp.rect(sx, cy - r - 2, sx, cy + r + 1, deck[2])
        sp.set(sx, cy - r - 2, deck[0]); sp.set(sx, cy + r + 1, deck[5])
    sp.rect(cx - r - 2, cy - r - 3, cx + r + 1, cy - r - 3, IRON[2])   # the strap
    sp.rect(cx - r - 2, cy - r - 2, cx - r - 2, cy - r - 2, IRON[3])
    sp.rect(cx - 1, cy - r - 6, cx, cy - r - 4, IRON[2])              # its becket
    sp.set(cx - 1, cy - r - 6, IRON[1])


def _rail_h(sp, deck, x0, x1, y, salt, pitch=14, dip=1):
    """A hemp handrail seen from above along an EAST-WEST deck edge: two rope
    lines swagged between squat posts every `pitch` px, dipping `dip` px at
    each mid-span. Ropes are drawn FIRST and the posts over them, so a post
    reads as standing in front of its own rope.

    Drawn strictly inside the footprint. A rail is art; the walkable edge is
    the map — a body standing at the deck's edge draws OVER the near rail,
    exactly as it does over Alembic's bridge rail and FFVI's, and nobody has
    ever noticed."""
    for ry, c in ((y + 1, ROPE[1]), (y + 4, ROPE[2])):
        for x in range(x0, x1 + 1):
            p = (x - x0 - 2) % pitch
            s = dip if 2 < p < pitch - 2 else 0
            sp.set(x, ry + s, c)
            sp.set(x, ry + s + 1, ROPE[3])
    for px_ in range(x0 + 2, x1 - 1, pitch):
        sp.rect(px_, y, px_ + 1, y + 6, deck[3])
        sp.rect(px_, y, px_, y + 6, deck[1])
        sp.set(px_, y - 1, deck[0]); sp.set(px_ + 1, y - 1, deck[4])
        sp.set(px_ + 1, y + 6, deck[5])


def _rail_v(sp, deck, y0, y1, x, salt, pitch=14, dip=1):
    """The NORTH-SOUTH twin of `_rail_h`: the rail runs down a deck's west or
    east edge and the swag bows sideways (`dip` signed — negative bows west)."""
    for rx, c in ((x + 1, ROPE[1]), (x + 4, ROPE[2])):
        for y in range(y0, y1 + 1):
            p = (y - y0 - 2) % pitch
            s = dip if 2 < p < pitch - 2 else 0
            sp.set(rx + s, y, c)
            sp.set(rx + s + (1 if dip >= 0 else -1), y, ROPE[3])
    for py_ in range(y0 + 2, y1 - 1, pitch):
        sp.rect(x, py_, x + 6, py_ + 1, deck[3])
        sp.rect(x, py_, x + 6, py_, deck[1])
        sp.set(x - 1, py_, deck[0]); sp.set(x - 1, py_ + 1, deck[4])
        sp.set(x + 6, py_ + 1, deck[5])


# ---- 1. THE GREAT TRUNK --------------------------------------------------------------

def great_trunk(bark, ground, spans, salt=401, w=48, lean=0.0):
    """THE TRUNK ARMATURE — one great tree crossing a town of STACKED STOREYS,
    returned as ONE IMG PER SEGMENT.

    A treehouse village reads as one because the TRUNKS are the biggest mass in
    frame and the buildings are subordinate to them (Slitherbough, Endor). That
    needs a trunk tall enough to pass a boardwalk, and passing a boardwalk is
    exactly where a single sprite stops working.

    WHY THIS IS SLICED AND NOT ONE SPRITE, which is the whole reason this
    function exists. A Tier-3 prop carries ONE y-sort key — its footprint's
    south edge (scene/prop_spawner.gd) — so it draws over every body whose feet
    line is north of that edge. A trunk with its foot on the forest floor
    therefore draws over a body standing ANYWHERE on either boardwalk above it,
    and since a trunk's shaft is an opaque ~35px mass in a 48px canvas, a body
    on the deck cell behind it is not "behind" anything: it is GONE. That
    shipped once, in the v1 canopy town, and `tools/zwalk.gd lint` measured it
    at zero visible pixels on the great tree's own walkway.

    ONE SPRITE CANNOT DEPTH-SORT AGAINST BODIES ON TWO STOREYS AT ONCE. So the
    trunk is one sprite PER STOREY, each with the storey's own footprint, and
    each storey's walking lane is authored SOUTH of its segment — where the
    body's feet line is south of the segment's base line and the body is
    unconditionally in front. The segments are cut from ONE virtual trunk, so
    the bark bands, the grooves and the taper are continuous across them and the
    seam is invisible; and the rows between segments are not missing art but the
    DECK ITSELF, which is what a tree passing through a platform looks like from
    above — trunk, boards, trunk again.

    THE RING DECK IS WHY THE SEGMENTS ARE SHORT. Each storey's solid trunk
    footprint is a compact block in the MIDDLE of a wider channel, so the deck
    closes all the way around it — north, south, east and west — and you can walk
    a full circle round the tree, passing BEHIND it, which is the single most
    recognisable thing about both references. That works only because every one of
    the trunk's own segments sorts SOUTH of a body on the ring's north arc: the
    crown carries `base_inset=-16` and each band-crossing `-32`, so a body up
    there is behind the leaves, behind the shaft below it and behind the fascia
    above it, all at once. Get one of those insets wrong and the body pops in
    front of the trunk it is standing behind.

    `spans` — [(cell_from, cell_to), ...] INCLUSIVE, in the trunk's own cell
    space where 0 is the top of the shaft, ordered top to bottom. The gaps
    between spans are the ring decks and are deliberately not drawn: the boards
    are what you see there, which is what a tree passing through a platform looks
    like.
    Returns one Img per span, each `w` wide and (to-from+1)*16 tall.

    `lean` tilts the whole shaft by that many px from top to bottom. Six great
    trees cut from one builder are six identical columns without it, and identical
    columns read as ARCHITECTURE — which is the exact failure this rebuild exists
    to undo. Keep it small (±5): the channel is only a tile wider than the shaft.

    FOOTPRINT: `w // 16` cells wide per segment (3 at w=48) and EVERY CELL SOLID.
    That is not a lost opportunity for walk-behind — it is the rule above: nothing
    standable may sit under a continuous mass. Walk-behind belongs to the crown's
    perforated leaves (`great_crown`) and to the 8px of shaft that overhangs the
    ring's side arcs, both of which the visibility lint measures.
    ANCHOR: `emit_prop(name, chars, img, each=True)`, one char per SEGMENT ROLE.
    Band-crossing segments take `base_inset=-32` (see above); shaft and foot
    slices take none.
    COVERAGE: >= 50% on every cell of the shaft, 82% on the foot.
    """
    total = max(s[1] for s in spans) + 1
    h = 16 * total
    sp = S(w, h, salt)
    cx0 = w / 2.0 - lean * 0.5

    def cx_at(y):
        return cx0 + lean * (y / float(max(1, h - 4)))

    # The taper runs over the WHOLE trunk, not per segment — that is the point of
    # building it once. A great tree is barely conical over 22 cells (2-3px), and
    # that restraint is deliberate: a strong taper at this scale reads as a spike.
    # THE SHAFT FILLS ITS FOOTPRINT. It used to be w*0.27..0.335 — about 40px of
    # bark inside a 64px, four-cell footprint — which left the outer third of each
    # FLANKING cell showing raw underlay all the way down the tree. `_alembic`'s own
    # note says "a trunk is drawn by an opaque Tier-3 sprite, so the cell only needs
    # an underlay and a shadow", and that was simply not true of the art. Up in the
    # canopy it showed: `greattrunk` renders grass, everything around it up there
    # renders leaf, and the autotile drew a TRANSITION into that exposed third —
    # a hard-edged pale wedge either side of the ladder that reads as a clipping bug.
    # Chasing it through the terrain table is chasing the symptom; four cells of
    # collision want four cells of bark. It also fixes the proportion: a 2.4-cell
    # trunk under a 12-cell ring deck reads as a lily pad on a stick.
    top_half, bot_half = w * 0.465, w * 0.485
    cx = cx_at(h - 4)
    sp.blob(cx, h - 3, w * 0.40, 2.8, ground[4])       # ground contact shadow,
    sp.blob(cx, h - 2, w * 0.24, 1.8, ground[5])       # kept TIGHT (see below)
    _shaft(sp, bark, cx0, 0, h - 4, top_half, bot_half, salt, lean=lean)
    # BURLS up the whole length rather than the two `tree_trunk` puts near its
    # foot: over 350px, two knots low down read as damage to the base instead of
    # as the surface of a very old tree. Spaced on an irrational-ish stride so
    # they never line up into a column, and alternating sides.
    for i in range(7):
        ky = h - 26 - int(i * h * 0.127) - (h2(i, 7, salt) % 11)
        if ky < 8:
            break
        side = -1 if i % 2 else 1
        r = 3.2 + (h2(i, 11, salt) % 5) * 0.42
        kx = cx_at(ky) + side * (5.5 + i % 2)
        sp.ball(kx, ky, r, r * 0.82, bark, sh=0.24, power=2.4)
        sp.blob(kx, ky, r * 0.42, r * 0.34, bark[5])
        sp.set(int(kx - r * 0.5), int(ky - r * 0.5), bark[1])
    # HEALED BRANCH SCARS — one or two oval collars where a limb came off, on the
    # side the burls are not. Over 350px of otherwise uniform bark these are what
    # stop the shaft reading as a length of pipe: a burl is a lump, a scar is a
    # piece of the tree's HISTORY, and at CT scale that difference is legible.
    for i in range(2):
        sy = int(h * (0.30 + 0.34 * i)) + (h2(i, 13, salt) % 13)
        if sy < 14 or sy > h - 40:
            continue
        sx = cx_at(sy) + (7.0 if i % 2 else -7.0)
        sp.ball(sx, sy, 4.6, 3.2, bark, sh=0.30, power=1.7)
        sp.blob(sx, sy, 3.0, 1.9, bark[4])
        sp.blob(sx, sy - 1, 2.2, 1.1, bark[5])
        sp.set(int(sx - 2), int(sy - 2), bark[1])       # the lit upper lip
    # BUTTRESS ROOTS, drawn AFTER the shaft (behind it they vanish into the
    # contact shadow) so they read as fins standing in FRONT of the trunk and
    # flaring out of it. Each is a wedge lit one step above the band it grows out
    # of, with its own dark seat where it meets the ground — that seat is what
    # plants it. Reach is capped so the flare stays clear of the canvas edge: a
    # root cut off at x=0 gets an edge() outline down the column and reads as a
    # crop rather than as a root.
    for rx, rise, hwd, k in ((-1.00, 34, 8.0, 1), (-0.60, 24, 5.6, 0),
                             (-0.26, 15, 4.0, 2), (1.00, 33, 8.0, 3),
                             (0.62, 25, 5.6, 4), (0.28, 16, 4.0, 2)):
        tipx = cx + rx * (bot_half + 9.0)
        topy = h - 4 - rise
        for y in range(topy, h - 3):
            u = (y - topy) / float(max(1, h - 4 - topy))
            xa = cx + rx * bot_half * 0.30
            xb = xa + (tipx - xa) * (u ** 0.62)            # a splayed fin
            hwy = 1.2 + (hwd - 1.2) * u
            for x in range(int(round(min(xa, xb) - hwy * 0.2)),
                           int(round(max(xa, xb) + hwy * 0.2)) + 1):
                if abs(x - xb) <= hwy:
                    sp.set(x, y, bark[k])
            sp.set(int(round(xb - hwy)), y, bark[max(0, k - 1)])   # lit arris
            sp.set(int(round(xb + hwy)), y, bark[min(5, k + 2)])
        sp.set(int(round(tipx)), h - 4, bark[5])           # its seat
        sp.set(int(round(tipx)) - 1, h - 4, bark[5])
    edge(sp, h)
    clipw(sp, w)
    out = []
    for c0, c1 in spans:
        img = Img(w, (c1 - c0 + 1) * 16)
        for y in range((c1 - c0 + 1) * 16):
            for x in range(w):
                p = sp.px[c0 * 16 + y][x]
                if p:
                    img.put(x, y, p)
        out.append(img)
    return out


def great_crown(f, bark, salt=451, w=96, h=48, lean=0.0, window=None):
    """THE CROWN a great trunk's top disappears into — the north arc of the ring
    deck runs UNDER this, so it is the one piece of the tree a body is allowed to
    stand inside.

    Which makes PERFORATION load-bearing rather than decorative. The whole reason
    the ring deck can pass behind the tree is that these leaves are lobes with
    daylight between them; drawn as one solid mass this becomes the invisible-body
    defect that `great_trunk`'s docstring is about. `_leaf_mass`' two-pass order
    is what keeps the lobes reading separately, and the gaps at the lobe seams are
    the gaps a body shows through.

    WIDER THAN ITS CHANNEL on purpose (96px over a 4-cell footprint): the crown
    spilling over the bays either side is most of what makes both references read
    as villages nested in trees rather than as streets with trees on them.

    FOOTPRINT: `w // 16` x `h // 16`, EVERY CELL WALKABLE — this is deck you walk
    under leaves on.
    ANCHOR: `emit_prop(name, chars, sprite_img(sp, W, H), top=-pad_t,
    base_inset=-16, each=True)` with `(sp, pad_x, pad_t, pad_b)` unpacked from the
    return and `W, H = w + 2 * pad_x, h + pad_t + pad_b`. The `-16` is what pushes
    the sort key south of a body standing on the north arc, so the leaves are in
    front of it. Without it the body walks over its own canopy.
    COVERAGE: ~62% of the figure hidden on the deepest cell — comfortably inside
    the walk-behind visibility rule's 90% ceiling, and that margin IS the effect.

    THE CANVAS IS SIZED TO THE MASS, NEVER THE OTHER WAY ROUND (2026-08-02), and
    that is the fix for a tree that was coming out with a FLAT TOP. `w` x `h` is
    the CHANNEL the lobes are laid out against, not the canvas: the crown is
    deliberately bigger than its channel on every side, and `Sprite.set` discards
    out-of-range pixels SILENTLY — so the four tables below were spilling ~21px
    over the top, ~8 left, ~11 right and ~10 below, and every one of those came
    out as a ruler-straight un-outlined cut through the leaves (`edge()` cannot
    outline a silhouette that has no empty pixel beside it). Measured on the
    shipped 224x128 town crown: a 123px flat cut across the top of the dome, 38
    and 46px flat down the sides, 84 across the bottom — a tree in a box, dead
    centre of the screen, with forest still visible above the cut.

    So the ellipse tables are hoisted, the mass's own bbox is measured off them,
    and the canvas is grown to hold it. The pads come back with the sprite because
    only the caller can place them: `pad_x` is symmetric so a sprite centred on
    its footprint stays centred, and `pad_t` becomes a NEGATIVE `anchor=top:` so
    the channel still lands on the footprint's own top row and nothing in the
    world moves. Every number here is derived, so this holds at any `(w, h)` —
    the Academy's 144-wide crown was spilling ~15 left and ~18 right off the same
    tables, and is fixed by the same arithmetic without a second set of constants.
    """
    r = max(9.0, h * 0.30)
    # THE LIMBS FIRST, so the leaves close over them and the branches read as
    # emerging THROUGH the canopy rather than lying on top of it. That ordering is
    # the whole difference between a tree and a bush with sticks in it. Four of
    # them at four heights and reaches, because two symmetric limbs read as a
    # crossbar.
    LIMBS = ((-1, 0.62, 0.42, 4.0), (1, 0.46, 0.36, 3.6),
             (-1, 0.34, 0.28, 3.0), (1, 0.74, 0.30, 3.2))
    # A DARK UNDER-RANK before the lit lobes: the leaves you see INTO. Without it
    # a lobe cluster is a single sheet of one green and reads as bubble wrap, which
    # is exactly what the first pass came out as. These are drawn low and wide and
    # then mostly buried, so what survives is the daylight BETWEEN the lit lobes
    # having something dark behind it — which is also what lets a body on the ring
    # deck show through the gaps as a silhouette instead of a hole.
    UNDER = ((0.30, 0.74, 0.92), (0.70, 0.78, 0.90), (0.50, 0.66, 0.86),
             (0.14, 0.62, 0.72), (0.86, 0.64, 0.74))
    # THE LIT LOBES, in three ranks. Radius keyed to the crown's HEIGHT and never
    # stretched to fit the width — the law `_canopy_roof` states, for the same
    # reason: a stretched lobe is an ellipse and a mass of ellipses is a bush. The
    # sizes are deliberately UNEQUAL across a 0.72..1.34 range; equal lobes are the
    # bubble-wrap failure however many you draw.
    LIT = ((0.48, 0.24, 1.34, 1.00), (0.24, 0.32, 0.88, 0.96),
           (0.76, 0.30, 1.06, 0.98), (0.09, 0.54, 0.72, 0.88),
           (0.91, 0.56, 0.80, 0.88), (0.36, 0.58, 1.14, 0.94),
           (0.65, 0.62, 0.92, 0.92), (0.19, 0.78, 0.76, 0.80),
           (0.82, 0.80, 0.70, 0.80), (0.52, 0.84, 0.98, 0.82))
    # LEAF CLUSTERS ON THE LIMB TIPS. A limb that ends in a bare stub reads as
    # broken; a small tuft at the end reads as a bough carrying foliage, and it is
    # also what keeps the silhouette ragged out at the sides where the crown
    # overhangs the bays.
    TIPS = ((-1, 0.62, 0.42), (1, 0.46, 0.36), (1, 0.74, 0.30))

    # ---- MEASURE THE MASS, THEN ALLOCATE THE CANVAS ---------------------------------
    # Every filled form this builder draws is an axis-aligned ellipse or a capsule
    # between two of them, and `ball`'s superellipse reaches exactly +-rx / +-ry
    # (at ny = 0 the test is |nx| <= 1), so the union of these bounds IS the
    # silhouette. Everything else — the under-arcs, the sun-catch dabs, the
    # skylights, the window, `_leaf_dabs` — is drawn strictly inside a lobe, and
    # `despeckle` only removes. MARGIN is the 1px `edge()` outline plus one.
    MARGIN = 2
    ch_x = w / 2.0 + lean                          # the channel's own centreline
    bounds = []
    for sgn, ly, reach, rr in LIMBS:
        bounds.append((ch_x + sgn * 3, h * ly, rr, rr))
        bounds.append((ch_x + sgn * w * reach, h * (ly - 0.16), 1.7, 1.7))
    for lx, ly, k in UNDER:
        bounds.append((w * lx, h * ly, r * k, r * k * 0.80))
    for i, (lx, ly, k, flat) in enumerate(LIT):
        bounds.append((w * lx + (h2(i, 5, salt) % 3) - 1,
                       h * ly + (h2(i, 3, salt) % 3) - 1, r * k, r * k * flat))
    for sgn, ly, reach in TIPS:
        bounds.append((ch_x + sgn * w * reach, h * (ly - 0.16), r * 0.44, r * 0.38))
    # pad_x is the MAX of the two sides, never one each: `PropSpawner` centres a
    # prop on its footprint's x, so an asymmetric canvas would slide the whole
    # crown sideways off its own trunk.
    pad_x = int(math.ceil(max(MARGIN - min(b[0] - b[2] for b in bounds),
                              max(b[0] + b[2] for b in bounds) + MARGIN - (w - 1),
                              0.0)))
    pad_t = int(math.ceil(max(MARGIN - min(b[1] - b[3] for b in bounds), 0.0)))
    pad_b = int(math.ceil(max(max(b[1] + b[3] for b in bounds)
                              + MARGIN - (h - 1), 0.0)))
    W, H = w + 2 * pad_x, h + pad_t + pad_b

    sp = S(W, H, salt)
    # the channel's coordinates, moved into the padded canvas — every `w * u` and
    # `h * v` below goes through these, so the art is pixel-identical to what the
    # tables always described, minus the clipping
    def PX(u):
        return pad_x + w * u

    def PY(v):
        return pad_t + h * v

    cx = PX(0.5) + lean
    for sgn, ly, reach, rr in LIMBS:
        sp.capsule(cx + sgn * 3, PY(ly), cx + sgn * w * reach,
                   PY(ly - 0.16), rr, 1.7, bark, end_sh=0.16)
    for lx, ly, k in UNDER:
        sp.ball(PX(lx), PY(ly), r * k, r * k * 0.80,
                (f[3], f[4], f[4], f[5], f[5], f[5]), sh=0.10, power=2.1)
    lobes = []
    for i, (lx, ly, k, flat) in enumerate(LIT):
        lobes.append((PX(lx) + (h2(i, 5, salt) % 3) - 1,
                      PY(ly) + (h2(i, 3, salt) % 3) - 1,
                      r * k, flat, 0.02 + 0.03 * (i % 4)))
    _leaf_mass(sp, f, lobes)
    # dabs over the WHOLE canvas, not the channel: they are gated on the pixel
    # already being filled, so the box only has to reach the leaves — and after
    # the padding the outermost lobes live out in the margin.
    _leaf_dabs(sp, f, 1, 1, W - 2, int(PY(0.92)), salt, n=max(16, W // 3))
    # THE CROWN'S OWN SUN-CATCH, over the top of the per-lobe dabs. Broken for
    # the same reason they are — as one r*0.42 ellipse this was a second, larger
    # balloon laid over the raft.
    for k, (ox, oy, rk) in enumerate(((0.28, 0.17, 0.30), (0.38, 0.24, 0.22),
                                      (0.21, 0.27, 0.17), (0.45, 0.14, 0.13))):
        sp.blob(PX(ox), PY(oy), r * rk, r * rk * 0.62, f[0])
    sp.set(int(PX(0.28)), int(PY(0.14)), SPEC)
    for sgn, ly, reach in TIPS:
        tx, ty = cx + sgn * w * reach, PY(ly - 0.16)
        sp.ball(tx, ty, r * 0.44, r * 0.38, f, sh=0.06, power=2.1)
        sp.blob(tx + r * 0.05, ty + r * 0.18, r * 0.26, r * 0.11, f[4])
        sp.blob(tx - r * 0.16, ty - r * 0.18, r * 0.14, r * 0.10, f[0])
    sp.despeckle(2, 1)
    # ---- THE SKYLIGHTS, and they are load-bearing, not texture ---------------------
    # The ring deck's north arc runs UNDER this crown, so the crown is the one piece
    # of the tree a body is allowed to stand inside — and a leaf mass drawn as a solid
    # sheet makes that body 100% INVISIBLE. `_check_art.py`'s walk-behind visibility
    # rule measured exactly that on the first pass: every middle-row cell at 100%.
    #
    # So the gaps are punched deliberately, AFTER the mass is finished, and they are
    # honest for what this is — a canopy seen from above has daylight through it, and
    # what you glimpse through the gaps is the boards, and whoever is walking on them.
    # Kept off the centreline, because that is where the shaft comes up and a hole
    # there would read as a bite out of the trunk.
    # Each gap is TWO overlapping ellipses at different angles rather than one disc,
    # and every radius, aspect and offset is hashed. A ring of equal circles is the
    # failure to avoid — the first pass punched seven of those and the crown came out
    # POLKA-DOTTED, which is somehow worse than the solid sheet it replaced. Leaves
    # part in ragged lens shapes, never in holes.
    # ALL OF THEM LOW. The gaps exist to keep a body on the ring's north arc from
    # vanishing, and that body's head tops out around 60% of the crown's height — so
    # daylight up in the crown's shoulders buys nothing and costs the silhouette,
    # which is where a canopy is read. Eleven evenly-scattered gaps came out as
    # Swiss cheese; six in the lower half read as the underside of a canopy, which
    # is what you are actually looking at from a deck built inside one.
    for i, (hx, hy, hr) in enumerate((
            (0.17, 0.62, 5.4), (0.32, 0.80, 5.0), (0.45, 0.66, 5.6),
            (0.58, 0.82, 5.0), (0.71, 0.64, 5.4), (0.86, 0.78, 4.6))):
        cut = []
        for k in range(2):
            rr = hr * (0.72 + 0.16 * (h2(i, 17 + k, salt) % 4))
            ax = rr * (0.78 + 0.10 * (h2(i, 23 + k, salt) % 4))
            by = rr * (0.52 + 0.12 * (h2(i, 29 + k, salt) % 4))
            ox = (h2(i, 31 + k, salt) % 5) - 2
            oy = (h2(i, 37 + k, salt) % 5) - 2
            cut.append((PX(hx) + ox, PY(hy) + oy, ax, by))
        lo_x = int(min(c[0] - c[2] for c in cut)) - 2
        hi_x = int(max(c[0] + c[2] for c in cut)) + 3
        lo_y = int(min(c[1] - c[3] for c in cut)) - 2
        hi_y = int(max(c[1] + c[3] for c in cut)) + 3
        for y in range(lo_y, hi_y):
            for x in range(lo_x, hi_x):
                d = min(((x - c[0]) / c[2]) ** 2 + ((y - c[1]) / c[3]) ** 2
                        for c in cut)
                if d <= 1.0:
                    sp.set(x, y, None)
        # a dark inner lip around each gap, so it reads as leaves PARTING rather than
        # as a hole cut in a sheet of green
        for y in range(lo_y, hi_y):
            for x in range(lo_x, hi_x):
                d = min(((x - c[0]) / c[2]) ** 2 + ((y - c[1]) / c[3]) ** 2
                        for c in cut)
                if 1.0 < d <= 1.6 and sp.get(x, y) is not None:
                    sp.set(x, y, f[4] if (x + y) % 2 else f[5])
    # THE LIT WINDOW, stamped LAST so the leaves cannot bury it. It belongs to the
    # crown rather than to `trunk_face` because the shaft segment is only two cells
    # tall — see that builder for why it must not be taller — and because the sketch
    # this town is drawn from puts the window up among the leaves, not down at deck
    # level beside the door. A patch of bark goes behind it so a lit pane is never
    # floating on foliage.
    if window is not None:
        wx, wy, hw, hh = int(PX(0.5)) - 1, int(PY(0.86)), 7, 7
        sp.blob(wx, wy, 13, 11, bark[3])
        sp.blob(wx, wy - 2, 11, 8, bark[2])
        for y in range(wy - hh, wy + hh + 1):
            for x in range(wx - hw, wx + hw + 1):
                lit = abs(x - wx) < hw - 1 and abs(y - wy) < hh - 1
                sp.set(x, y, WARM if lit else window[4])
        for y in range(wy - hh, wy + hh + 1):
            sp.set(wx, y, window[4])
        for x in range(wx - hw, wx + hw + 1):
            sp.set(x, wy, window[4])
        sp.set(wx - hw - 1, wy - hh - 1, window[5])
    edge(sp, H)
    clipw(sp, W)
    # THE CANVAS HAS TO HOLD THE WHOLE SILHOUETTE, and it is worth an assert
    # rather than a lint: this is the one failure mode here that renders, dedupes
    # and passes every check in `_check_art.py` while putting a flat un-outlined
    # cut through the middle of the screen's biggest object. If a future lobe or
    # limb reaches past the measured bounds, say so at build time.
    for x in range(W):
        assert sp.px[0][x] is None and sp.px[H - 1][x] is None, (
            f"great_crown({w}x{h}): leaves on the canvas border at x={x} — the "
            f"mass outgrew its measured bounds and is being cut flat")
    for y in range(H):
        assert sp.px[y][0] is None and sp.px[y][W - 1] is None, (
            f"great_crown({w}x{h}): leaves on the canvas border at y={y} — the "
            f"mass outgrew its measured bounds and is being cut flat")
    return sp, pad_x, pad_t, pad_b


def tree_trunk(bark, ground, salt=401, cells=5, base=1, w=48):
    """SUPERSEDED BY `great_trunk` (2026-07-30) AND CALLED BY NOTHING. Kept as the
    single-storey case: one trunk, one sprite, one y-sort key, a walkable crown
    over a solid base. That is correct for a tree standing on ONE floor and it is
    exactly what breaks on a stacked map — one sprite cannot depth-sort against
    bodies on two storeys, and its walkable crown is the invisible-body defect the
    walk-behind visibility lint now catches. Reach for `great_trunk` in any town
    with more than one walkable storey.

    THE GREAT TRUNK — the structural column a canopy platform rests on, and
    the piece the whole town is measured against: hard-banded bark, broken
    grooves, two burls, and BUTTRESS ROOTS flaring at the foot onto a ground
    contact shadow. The shaft runs clean off the canvas top, so it reads as
    continuing up into the canopy rather than as a stump.

    FOOTPRINT: `w // 16` cells wide (3 at the default w=48) x `cells` tall.
    ANCHOR: Tier-3 y-sorted prop, art bottom-anchored at the footprint's SOUTH
    edge — `emit_prop(name, chars, sprite_img(sp, w, 16*cells))`, no `top=`, no
    `base_inset=`. One unsplit sprite, like `town_conifer_big` and unlike
    `town_conifer`: y-sort at the foot already draws the shaft OVER a body
    standing north of it (walk-behind) and UNDER a body standing south of it,
    which is every case a trunk has.

    AUTHORING CONSTRAINTS a generator must assert:
      * THE CASE-SPLIT (the Lanternwood conifer/lamp idiom). The bottom `base`
        rows of the footprint are SOLID (the trunk you bump into); every row
        above them is WALKABLE walk-behind bough space. Author it as a char
        PAIR whose case means solid-vs-walkable and assert, per connected
        component, that exactly the bottom `base` rows are solid — an all-solid
        trunk turns a 5-row prop into a 5-row wall, and an all-walkable one
        lets you stand inside the tree.
      * `cells >= base + 2`. Below that there is no walk-behind space left and
        the piece should be understory dressing instead.
      * Two trunks authored edge-to-edge FUSE into one component, one bbox and
        one badly stretched sprite (the 2026-07-29 spruce lesson) — assert
        every component is a clean `w//16` x `cells` block.
      * Width is a lint constraint, not a taste one: the buttress flare is what
        keeps all three base cells over the T3 20%-coverage rule, so do not
        widen `w` past 48 without widening the flare with it.
    COVERAGE: measured floor 82.0% on the SOLID base row and 50.0% on the
    walkable rows, both well clear of `T3_COVER_MIN` = 0.20."""
    assert cells >= base + 2, "a great trunk needs walk-behind rows above its base"
    h = 16 * cells
    sp = S(w, h, salt)
    cx = w / 2.0
    top_half, bot_half = w * 0.31, w * 0.365
    flare = h - 22                                     # where the roots spring
    sp.blob(cx, h - 3, w * 0.40, 2.8, ground[4])       # ground contact shadow,
    sp.blob(cx, h - 2, w * 0.24, 1.8, ground[5])       # kept TIGHT: a wide dark
                                                       # pool swallows the roots
    _shaft(sp, bark, cx, 0, h - 4, top_half, bot_half, salt)
    # BUTTRESS ROOTS, drawn AFTER the shaft (the first pass put them behind it
    # and they vanished into the contact shadow) so they read as fins standing
    # in FRONT of the trunk and flaring out of it. Each is a wedge, lit one step
    # above the band it grows out of, with its own dark seat where it meets the
    # ground — that seat is what plants it. Reach is capped at bot_half + 3 so
    # the flare stays >=2px inside the canvas: a root cut off at x=0 gets an
    # edge() outline down the column and reads as a crop, not a root.
    for rx, rise, hwd, k in ((-1.00, 20, 6.0, 1), (-0.52, 14, 4.4, 0),
                             (0.98, 19, 6.0, 3), (0.50, 13, 4.4, 4)):
        tipx = cx + rx * (bot_half + 3.0)
        topy = h - 4 - rise
        for y in range(topy, h - 3):
            u = (y - topy) / float(max(1, h - 4 - topy))
            xa = cx + rx * bot_half * 0.30
            xb = xa + (tipx - xa) * (u ** 0.62)            # a splayed fin
            hwy = 1.2 + (hwd - 1.2) * u
            for x in range(int(round(min(xa, xb) - hwy * 0.2)),
                           int(round(max(xa, xb) + hwy * 0.2)) + 1):
                if abs(x - xb) <= hwy:
                    sp.set(x, y, bark[k])
            sp.set(int(round(xb - hwy)), y, bark[max(0, k - 1)])   # lit arris
            sp.set(int(round(xb + hwy)), y, bark[min(5, k + 2)])
        sp.set(int(round(tipx)), h - 4, bark[5])           # its seat
        sp.set(int(round(tipx)) - 1, h - 4, bark[5])
    for kx, ky, r in ((cx - 6.5, h - 46, 4.2), (cx + 6.0, h - 27, 3.4)):
        if ky < 4:
            continue                                   # a short trunk has room
        sp.ball(kx, ky, r, r * 0.82, bark, sh=0.24, power=2.4)   # for one burl
        sp.blob(kx, ky, r * 0.42, r * 0.34, bark[5])
        sp.set(int(kx - r * 0.5), int(ky - r * 0.5), bark[1])
    for tx, ty, c in ((5, h - 7, ground[1]), (w - 7, h - 6, ground[3]),
                      (int(cx) - 2, h - 4, ground[1])):
        sp.set(tx, ty, c)                              # tufts seating the roots
    edge(sp, h)
    clipw(sp, w)
    return sp


# ---- 2. THE CANOPY HOUSE -------------------------------------------------------------

def tree_house(f, wall, deck, salt=411, composite=True, frames=8, wide=False):
    """SUPERSEDED BY `tree_hut` (2026-07-29) AND CALLED BY NOTHING. Kept because
    it is the evidence for the doctrine below: this is Alembic's OWN language
    (plaster, leaf-canopy roof, copper plumbing) lifted onto a boardwalk, and a row
    of them read as a raised HIGH STREET, because the silhouette is still a
    rectangular cottage. The structure was right and the BUILDING was wrong. Do not
    reach for it for a canopy town; see `tree_hut` and the four cues.

    A CANOPY HOUSE — 80x64 over a 5x4 footprint, or 112x80 over 7x5 with
    `wide`. The naturey-steampunk alchemist-botanist language, built for the
    boughs: an overgrown LIVING leaf-canopy roof with a copper flue venting
    through it, light-cement plaster walls on a TIMBER SILL PLATE and joists
    (never a stone plinth — this thing is standing in the air), a twisty copper
    stovepipe elbowing out of the wall and up through the leaves, one fire-lit
    hearth window, a greenhouse plant window, planter boxes on the deck, an
    arched plank door with a hemp pull, and vines.

    EIGHT FRAMES, like `town_cabin`: `WIN_PULSE` spans the whole sheet so the
    hearth breathes once per ~1.4s (travel_scene's ANIM_STEP is 0.18s), while
    every steam term stays periodic in 4 and simply loops twice — the sheet is
    seamless either way. The hearth window AND the doorway share ONE breath, in
    phase, so the whole front swells together: one house, one fire.

    RETURNS: with `composite=True, frames=8` (the default) a horizontal
    frame-sheet `Img` of `w*frames` x `h + SMOKE_PAD`, ready for
    `emit_prop(name, chars, sheet, hframes=8)`. With `composite=False` the
    legacy `(lower, upper)` pair for `place_split`.

    FOOTPRINT: 5x4 cells (7x5 wide), EVERY CELL SOLID — the whole building is
    one Tier-3 y-sorted sheet, so the footprint is bbox + collision only.
    ANCHOR: bottom-anchored at the footprint's south edge; the SMOKE_PAD sky
    rows extend the art UPWARD for free, so no map or manifest change.

    AUTHORING CONSTRAINTS a generator must assert:
      * `hframes` in the manifest MUST equal `frames` here. A mismatch shows as
        a house sliced into vertical ribbons.
      * `frames % len(WIN_PULSE) == 0` (asserted below) — a partial breath
        cycle makes the sheet jump on the loop.
      * The footprint must sit entirely on DECK cells, never straddling a
        canopy-band row, or `bake_shadow` bakes the house's contact band onto a
        bough face.
      * Nothing walkable may hide behind the sheet: at 64-80px tall it is
        taller than the 2 rows of roof it declares.
    COVERAGE: measured floor 47.3% per cell (43.0% wide), so an all-solid
    footprint is safe — the canopy overhangs every roof cell and the facade fills
    every body cell."""
    assert frames < 2 or frames % len(WIN_PULSE) == 0, \
        "an animated canopy-house sheet must hold whole window-breath cycles"
    # fy = 2 ROOF ROWS (the town_cottage proportion). At fy=28 the roof was 22px
    # over an 80px-wide house and the copper flue came out as tall as the whole
    # canopy — a candle standing on a hedge. A 2-cell roof is what these
    # naturey buildings are drawn to.
    w, h, fy = (112, 80, 32) if wide else (80, 64, 32)
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # The flue sits over the HEARTH, on the west, which is where a stovepipe
    # comes from; the twisty copper riser lives on the EAST where there is wall to
    # spare. The first pass had the flue east and elbowed its pipe straight across
    # the DOORWAY, which read as a shelf hanging over the door.
    flues = (15, w - 30) if wide else (15,)
    flue = flues[0]
    dx0, dx1 = w // 2 - 7, w // 2 + 6                  # arch over the D cell
    # ---- upper: the living leaf canopy + its copper flue(s)
    _canopy_roof(up, f, w, fy, salt, flue_xs=flues)
    edge(up, fy)
    # ---- lower: plaster on a sill plate, apertures, plumbing, greenery
    _plaster_wall(lo, wall, f, deck, w, h, fy, salt)
    wins = [_hearth_window(lo, deck, 8, fy + 10, 12, 12)]
    _plant_window(lo, f, deck, w - 24, fy + 10, 13, 12)
    if wide:
        _plant_window(lo, f, deck, 28, fy + 10, 12, 12)
        wins.append(_hearth_window(lo, deck, w - 46, fy + 10, 11, 12))
    wins.append(_plank_door(lo, deck, dx0, dx1, fy, h))
    # THE STOVEPIPE: out of the wall above each hearth, one jog, up into its flue
    for fx in flues:
        _pv(lo, fx, fy, fy + 5)
        _ph(lo, fx - 8, fx, fy + 5)
        _pv(lo, fx - 8, fy + 5, fy + 8)
    # the twisty copper riser on the east wall, with the one valve on it. The
    # valves used to sit at fy+3 at both corners, where COPPER's violet-law reds
    # printed two hot dots on the eave line and read as berries.
    _pv(lo, w - 7, fy + 6, h - 13)
    _ph(lo, w - 15, w - 7, fy + 6)
    _pv(lo, w - 15, fy + 6, fy + 12)
    _valve(lo, w - 7, fy + 16)
    _planter(lo, f, deck, 6, 22, h - 9)
    _planter(lo, f, deck, w - 26, w - 8, h - 9)
    if wide:
        _planter(lo, f, deck, 26, 42, h - 9)           # the long wall wants a
                                                       # third, or its middle
                                                       # reads as bare plaster
    for pts in ([(3, h - 6), (7, fy + 18), (2, fy + 5)],
                [(w - 4, h - 7), (w - 10, fy + 16), (w - 3, fy + 5)]):
        for i in range(len(pts) - 1):                  # climbing vines
            ln(lo, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], f[2])
        for (vx, vy) in pts[::2]:
            lo.set(vx + 1, vy, f[1]); lo.set(vx + 1, vy + 1, f[4])
    edge(lo, h)
    anim = (lambda fa, ca, f2, dy=0: _anim_building(
        fa, ca, f2, flues=tuple((fx, 2) for fx in flues),
        windows=tuple(wins), dy=dy))
    return _finish(lo, up, w, fy, h, composite, frames, anim)


# ---- 2b. THE BOUGH HUT — the Slitherbough / Endor building ----------------------------
# `tree_house` above is the canopy version of ALEMBIC's own language: plaster
# walls, a leaf-canopy roof, copper plumbing. Put a row of them on a boardwalk and
# what you get reads as a raised HIGH STREET, because the silhouette is still a
# rectangular cottage — which was the note that produced this builder.
#
# A treehouse village reads as one from its SILHOUETTE and nothing else, and the
# two references agree on what that silhouette is: FFXIV's Slitherbough and
# Endor's Ewok village are both ROUND WOVEN HUTS UNDER CONICAL THATCH, lashed
# around trunks far bigger than they are. Four cues, in order of how much they
# carry:
#   1. THE CONE. A round thatch roof with a ragged eave fringe and a lashed peak.
#      Nothing else in this game's vocabulary is round-and-radial, so it reads
#      instantly and at any zoom.
#   2. THE BARREL. The body curves in at both sides, so the whole hut is a
#      silhouette with no vertical edges — the opposite of a cottage.
#   3. WOVEN, NOT BUILT. Vertical withy staves between two lashed hemp hoops. A
#      hut is made of the forest; a cottage is made of quarried and milled things.
#   4. A TIMBER SILL PLATE ON JOISTS, never a plinth. `_plaster_wall` already
#      argues this at length and it is the one detail that says a building is
#      standing in the AIR: a stone footing here reads as a hut in a hedge.
# Everything a shopfront needs — a sign board, a wares shelf — hangs off the
# porch rail instead of being cut into a wall, which is also how both references
# do it.

def _cone_rx(w, roof):
    """The thatch cone's base radius, solved BACKWARDS from the vertical room it
    has. A cone's proportions are fixed by its height, so the radius is not a
    taste knob: the silhouette needs `rx * 0.98` for the cone, `rx * 0.68` for the
    rim ellipse's two halves, and about 11px for the eave fringe and the bound
    crown. Give it more width than that and the roof flattens into a parasol,
    which is precisely how the first pass failed.

    Capped at 0.40 of the footprint width, because a hut wider than that leaves no
    porch — and the porch is both the Ewok read and what keeps the outer footprint
    cells off the invisible-wall lint (see _porch)."""
    return min(w * 0.40, max(12.0, (roof - 11.0) / 1.66))


def _thatch_cone(up, t, f, w, roof, salt):
    """A CONICAL THATCH ROOF: a rim ellipse seen at three-quarters with a proper
    APEX above it, radial bundles of reed converging on the apex, a ragged eave
    fringe, a bound crown, and moss on the wet flank.

    IT HAS TO BE A CONE, NOT A DOME, and the first pass proves why: an ellipse
    shaded from a point reads as a mushroom cap, a clamshell or a parasol — round
    things with no apex are all the same silhouette. A cone is the convex hull of
    an apex and a rim: two STRAIGHT sides tapering up to a point, over the rim
    ellipse's bottom half. That silhouette is unique in this game's vocabulary,
    which is the whole reason the treehouse village reads as one at a glance.

    The reed bundles converge on the apex for the same reason. Horizontal courses
    on a round roof come out as a coil of rope or a stack of tyres; reed laid from
    the peak DOWN AND OUT is what a thatcher does, and the converging lines are
    what carry the cone's form once the silhouette has established it."""
    rx = _cone_rx(w, roof)
    cx = w * 0.5
    rry = rx * 0.34                                    # the rim, at 3/4
    ay = 8.0                                           # the apex, under the crown
    by = ay + rx * 0.98                                # where the rim sits
    span = max(1.0, by - ay)
    for y in range(int(ay), int(by + rry) + 2):
        for x in range(1, w - 1):
            nx = (x - cx) / rx
            if y <= by:
                if abs(nx) > (y - ay) / span:          # the cone's straight sides
                    continue
            elif nx * nx + ((y - by) / rry) ** 2 > 1.0:
                continue                               # the rim's bottom half
            # NW-lit, and the shading runs ACROSS the cone rather than down it:
            # a cone's brightness is a function of which way its surface faces,
            # and every point on one radial line faces the same way.
            k = 1 if nx < -0.42 else 2 if nx < 0.04 else 3 if nx < 0.52 else 4
            if y > by:
                k = min(5, k + 1)                      # the rim, turning under
            # which bundle of reed this pixel belongs to
            ang = _turns64(y - ay, x - cx)
            band = (ang * 3) % 5
            if band == 0:
                k = min(5, k + 2)                      # the gap between bundles
            elif band == 3 and nx < 0.0:
                k = max(0, k - 1)                      # a reed catching the sun
            up.set(x, y, t[k])
    # THE EAVE FRINGE: ragged reed ENDS hanging past the roof line, 3-6px, in two
    # tones. A clean elliptical eave reads as a painted dome; the fringe is the
    # cue that says the roof is loose stalks bound in place, and it is worth more
    # per pixel than anything else here.
    for x in range(1, w - 1):
        low = None
        for y in range(int(by + rry) + 2, int(ay), -1):
            if up.get(x, y) is not None:
                low = y
                break
        if low is None:
            continue
        n = 3 + h2(x // 2, 7, salt) % 4
        for k in range(1, n + 1):
            up.set(x, low + k, t[3] if k == 1 else t[4] if k < n else t[5])
    # THE BOUND CROWN: the reed gathered and seized at the apex, standing proud.
    ax, ai = int(cx), int(ay)
    up.rect(ax - 2, ai - 6, ax + 1, ai + 3, t[2])
    up.rect(ax - 2, ai - 6, ax - 2, ai + 3, t[1])
    up.rect(ax + 1, ai - 6, ax + 1, ai + 3, t[4])
    up.rect(ax - 2, ai - 7, ax + 1, ai - 7, t[0])
    _lash(up, ax - 3, ax + 2, ai - 2, across=False)
    for mx, my in ((cx - rx * 0.46, by - rx * 0.28), (cx + rx * 0.22, by - rx * 0.60),
                   (cx - rx * 0.14, by + rry * 0.4)):
        if up.get(int(mx), int(my)) is not None:       # moss, on the wet flank
            up.set(int(mx), int(my), f[2])
            up.set(int(mx) + 1, int(my), f[3])
            up.set(int(mx), int(my) + 1, f[4])
    return by + rry


def _turns64(dy, dx):
    """atan2 quantized to 64ths of a turn, so the radial banding above stays
    deterministic and integer-keyed."""
    import math
    return int((math.atan2(dy, dx) + math.pi) * 32.0 / math.pi)


def _nest(lo, up, f, bark, w, h, roof, rx, salt):
    """THE BOUGH THE HUT IS NESTLED IN: leaf masses filling both flanks of the
    sprite, a limb sweeping in under them, and a few clusters lapping over the
    eave so foliage reads in FRONT of the roof as well as behind it.

    It earns its place twice. It is the Slitherbough half of the reference — those
    huts are not standing in the open, they are tucked into the crotch of
    something enormous — and it is also what keeps the footprint's outer cells off
    the invisible-wall lint. A cone tall enough to read is narrower than a 6-cell
    footprint (its radius is fixed by its height, see _cone_rx), so the flanks are
    bare, and a solid map cell whose Tier-3 art covers less than 20% of it renders
    as open ground and blocks anyway. Widening the hut was the wrong fix: it
    flattens the cone, which is the one thing carrying the read.

    Drawn on the LOWER canvas under the body and the porch, so the hut sits in
    front of its own foliage, plus a lighter pass on the UPPER one."""
    cx = w * 0.5
    inner_l, inner_r = cx - rx + 5.0, cx + rx - 5.0
    top = roof * 0.30
    bot = h - 15.0
    for side in (-1, 1):
        base = inner_l if side < 0 else inner_r
        # THE LIMB, and it stays mostly BURIED. Run out to the sprite's edge at
        # porch height it read as a pair of blue struts holding the hut up — a
        # bough enters from behind its own leaves and only a stub of it shows.
        lo.capsule(base - side * 26.0, top + 22.0, base, top + 8.0,
                   4.2, 2.6, bark, end_sh=0.18)
        # The lobes run down a line near the sprite's EDGE, not hugging the hut,
        # and that is a coverage requirement as much as a composition one: the
        # outer footprint column has to be >= 20% covered or it is an invisible
        # wall, and a mass tucked against the hut leaves it bare. Two inner lobes
        # bridge the gap so the flank reads as one bough, not a bush and a hut.
        outer = 9.0 if side < 0 else w - 10.0
        lobes = []
        for i in range(5):
            u = i / 4.0
            ly = top + (bot - top - 10.0) * u
            lr = 12.0 + 3.0 * (h2(i, side + 2, salt) % 2)
            lobes.append((outer + side * 2.0 * (i % 2), ly, lr, 0.94,
                          0.02 + 0.05 * i))
        for i in range(2):
            lobes.append((base - side * 6.0, top + (bot - top) * (0.30 + 0.34 * i),
                          10.0, 0.92, 0.14))
        _leaf_mass(lo, f, lobes)
        _leaf_dabs(lo, f, int(min(base, base - side * 20)), int(top),
                   int(max(base, base - side * 20)), int(bot), salt + i, n=12)
        # two clusters lapping OVER the eave, on the upper canvas
        for i, (ly, lr) in enumerate(((roof * 0.52, 9.0), (roof * 0.80, 7.0))):
            _leaf_mass(up, f, [(base + side * (lr * 0.45), ly, lr, 0.90, 0.10)])


def _porch(lo, deck, f, w, h, salt, foot=None):
    """The hut's PORCH: a plank deck with a hemp rail along its front and joists
    under it, spanning the hut's FOOTPRINT plus a 4px apron each side.

    Two jobs, and the second one is a lint. A hut is small relative to its
    platform — that is most of what makes both references read as villages rather
    than as streets — so the building leaves the outer footprint cells bare, and a
    solid map cell whose Tier-3 art covers less than 20% of it is an invisible
    wall. The porch is what covers them, and it is also exactly what should be
    there: you step out of a hut onto its own boards.

    IT IS THE FOOTPRINT'S WIDTH, NEVER THE SHEET'S. A hut sheet is wider than its
    footprint so the hanging sign and the lantern have air to swing in; a porch
    drawn to the sheet's edge instead runs a raised plank deck out over open
    ground on both sides, joists and all, and reads as a shelf bolted to the front
    of the building with nothing holding up its ends."""
    foot = foot or w
    x0, x1 = (w - foot) // 2 - 4, (w + foot) // 2 + 3
    lo.rect(x0, h - 12, x1, h - 5, deck[1])            # the porch boards
    for y in range(h - 12, h - 4, 4):
        lo.rect(x0, y, x1, y, deck[3])
    lo.rect(x0, h - 4, x1, h - 4, deck[0])             # the sill plate, proud
    lo.rect(x0, h - 3, x1, h - 2, deck[2])
    lo.rect(x0, h - 1, x1, h - 1, deck[5])
    for jx in range(x0 + 3, x1 - 2, 11):               # the joists under it
        lo.rect(jx, h - 3, jx + 1, h - 1, deck[4])
        lo.set(jx, h - 3, deck[3])
    for ry, c in ((h - 11, ROPE[1]), (h - 8, ROPE[2])):   # the hemp porch rail
        for x in range(x0, x1 + 1):
            s = 1 if 4 < x % 14 < 10 else 0
            lo.set(x, ry + s, c)
            lo.set(x, ry + s + 1, ROPE[3])
    for px_ in (x0 + 1, x1 - 2):                       # a rail post at each END,
        lo.rect(px_, h - 12, px_ + 1, h - 6, deck[3])  # so the deck stops at
        lo.rect(px_, h - 12, px_, h - 6, deck[1])      # something instead of
        lo.set(px_ + 1, h - 12, deck[4])               # running off into air
    for i, mx in enumerate(range(x0 + 4, x1 - 3, 13)):   # ferns in the porch pots
        lo.set(mx, h - 13, f[2] if i % 2 else f[3])
        lo.set(mx + 1, h - 13, f[4])


def _withy_body(lo, wood, f, deck, w, h, top, salt, half):
    """The hut's WOVEN BARREL body: VERTICAL withy staves between two lashed hemp
    hoops, tucked in at both flanks so the silhouette carries no vertical edge.

    THE STAVES RUN VERTICALLY AND THEIR TONE IS A FUNCTION OF X ALONE. The first
    pass keyed the tone on the barrel's curvature per ROW as well, which put a
    horizontal band across every course and turned the hut into a barrel lying on
    its side. A woven wall seen face-on is a set of vertical strips lit from one
    side; the only horizontal things on it are the hoops that hold it together."""
    bot = h - 13
    for y in range(top, bot + 1):
        u = (y - top) / float(max(1, bot - top))
        hw = half * (0.90 + 0.10 * (1.0 - (u - 0.30) * (u - 0.30) * 4.0))
        x0, x1 = int(w * 0.5 - hw), int(w * 0.5 + hw)
        for x in range(x0, x1 + 1):
            e = (x - w * 0.5) / max(1.0, hw)
            k = 1 if e < -0.46 else 2 if e < 0.10 else 3 if e < 0.62 else 4
            if (x - x0) % 3 == 2:
                k = min(5, k + 2)                      # the gap between staves
            elif (x - x0) % 6 == 0:
                k = max(0, k - 1)                      # a peeled withy, lighter
            lo.set(x, y, wood[k])
        lo.set(x0, y, wood[5]); lo.set(x1, y, wood[5])
    for hy in (top + 3, bot - 2):                      # the two lashed hoops
        for x in range(1, w - 1):
            if lo.get(x, hy) is None:
                continue
            lo.set(x, hy, ROPE[2] if (x // 2) % 2 else ROPE[1])
            if lo.get(x, hy + 1) is not None:
                lo.set(x, hy + 1, ROPE[3])
    for vx in (int(w * 0.5 - half) + 1, int(w * 0.5 + half) - 1):
        for vy in range(top + 4, bot, 2):              # vines up the flanks
            if h2(vx, vy, salt) % 3:
                lo.set(vx, vy, f[2] if vy % 4 else f[3])
    return top, bot


def tree_hut(wood, f, deck, bark, salt=481, composite=True, frames=4, w=96, h=80,
             rise=20, wares=False, sign=None, nest=True, foot=None):
    """A BOUGH HUT — the treehouse village's building, in the Slitherbough /
    Endor language: a round woven barrel of withy staves under a CONICAL THATCH
    roof with a ragged eave, bound with hemp hoops, standing on its own plank
    PORCH over joists, with one fire-lit window, a plank door and a hanging
    lantern.

    `tree_house` above is the canopy version of ALEMBIC's own language — plaster
    walls, a leaf-canopy roof, copper plumbing — and a row of those on a boardwalk
    reads as a raised HIGH STREET, because the silhouette is still a rectangular
    cottage. This is the correction. Four cues carry it, in order of weight:
      1. THE CONE (_thatch_cone). Nothing else in this game is round-and-radial.
      2. THE BARREL (_withy_body). No vertical edge anywhere in the silhouette —
         the exact opposite of a cottage.
      3. WOVEN, NOT BUILT. Withy staves and hemp hoops: a hut is made of the
         forest, a cottage of quarried and milled things.
      4. A PORCH ON JOISTS, never a plinth. `_plaster_wall` argues this at length
         and it is the one detail that says a building stands in the AIR.
    The hut is deliberately SMALLER than its footprint and the porch fills the
    rest, which is both how the references look and how the T3 coverage lint stays
    satisfied (see _porch).

    Drop-in for `_town_props.town_home` / `town_shop`'s slot: the same
    composite-or-`(lower, upper)` return through `_finish`, the same 4-frame
    contract, so a generator swaps one call and the map does not move. `wares` and
    `sign` make it a shopfront the way both references do — furniture hung off the
    porch, not joinery cut into a wall — which is why one silhouette can serve the
    house and both shops without reading as three copies.

    NOTHING CALLS THIS RIGHT NOW, AND THAT IS NOT AN INVITATION. Alembic's three
    shops wore it on the FOREST FLOOR for two days after the canopy became four ring
    decks, and on open grass beside a five-cell plaster cottage every cue above
    inverts: the cone is a tiki roof, the withy barrel has no wall material and you
    see daylight between its staves, "made of the forest" with no forest around it
    is just unfinished, and the whole thing is one flat tan value three cells wide.
    It is kept for the next building that stands in a BOUGH, which is the only place
    it is right. A ground shop is `_town_props.town_shop`.

    `rise` defaults to 20 and that number is a CEILING, not a preference: at 24 the
    sheet's crown reached 2px into the crown terrace's own walkable row and put a
    hut's finial in front of a body standing up there. 20 stops the art inside the
    cliff band. Raise it only after checking what is north of the footprint.

    `rise` IS WHY THE CONE FITS. A cone needs vertical room and a map row is 16px,
    so a three-roof-row footprint gives 48px — enough for a hat, not a cone. But
    `emit_prop` bottom-anchors the sheet at the footprint's SOUTH edge and does not
    care how tall it is (the same mechanism SMOKE_PAD already uses), so the sheet
    is drawn `rise` px taller than the footprint and the roof simply stands up over
    the cells to the north. On this town's boardwalk those cells are the Academy's
    cliff band, and hut roofs poking up in front of the terrace wall is the read
    you want anyway: the village is nestled UNDER the establishment.

    FOOTPRINT: `w // 16` x `h // 16` cells, EVERY CELL SOLID — one Tier-3
    y-sorted sheet, so the footprint is bbox + collision only.
    ANCHOR: bottom-anchored at the footprint's south edge; the `rise` and
    SMOKE_PAD rows extend the art upward for free.

    AUTHORING CONSTRAINTS a generator must assert:
      * `hframes` in the manifest MUST equal `frames`.
      * The footprint sits entirely on DECK cells, never straddling a fascia row.
      * Nothing walkable may hide behind the sheet: with `rise` it is taller than
        the rows it declares, so the cells to the NORTH must be solid (a cliff
        band, a bough) or the roof draws over ground a body can stand on."""
    assert frames < 2 or frames % len(WIN_PULSE) == 0, \
        "an animated hut sheet must hold whole window-breath cycles"
    H = h + rise
    roof = H - 34                          # the room the cone has above the body
    lo, up = S(w, H, salt), S(w, H, salt + 1)
    rx = _cone_rx(w, roof)
    half = rx * 0.78                                   # the body, under the eave
    eave = _thatch_cone(up, THATCH, f, w, roof, salt)
    # `nest=False` for a hut standing on the GROUND. The leaf mass exists to bed a
    # hut into a bough, and on open grass it reads as a hard dark RECTANGLE round
    # the building — the same seam that killed the ring's leaf bed, for the same
    # reason: authored foliage meeting autotiled foliage at a cell boundary.
    if nest:
        _nest(lo, up, f, bark, w, H, roof, rx, salt)
    edge(up, roof + 14)                # the fringe and the lapping foliage
    _porch(lo, deck, f, w, H, salt, foot)
    # THE BODY TUCKS UP UNDER THE EAVE, not below it. The first pass put its top
    # at the roof rows' own boundary and left six px of daylight between the
    # fringe and the wall — a hut with its hat hovering over it. The eave has to
    # OVERHANG the wall it shelters; that overlap is the joint.
    top, bot = _withy_body(lo, wood, f, deck, w, H, int(eave) - 3, salt, half)
    fy = roof                          # what _finish's split path calls the eave
    cx = int(w * 0.5)
    # THE DOOR, centred: a hut has one opening and it faces the walk.
    wins = [_plank_door(lo, deck, cx - 5, cx + 4, top + 2, bot + 1)]
    # ONE fire-lit window, off to the side. A hut with a lit pane at each end has
    # no focus for the breath to land on (the tree_house lesson, verbatim).
    wins.append(_hearth_window(lo, deck, cx - int(half) + 4, top + 8, 8, 8))
    if wares:
        for i, sx in enumerate(range(cx + 8, cx + int(half) - 2, 4)):
            lo.rect(sx, bot - 8, sx + 2, bot - 4, deck[3])
            lo.rect(sx, bot - 8, sx + 2, bot - 8, deck[1])
            lo.set(sx + 1, bot - 7, MINT if i % 2 else VIOLETF)
        lo.rect(cx + 6, bot - 3, cx + int(half) - 1, bot - 2, deck[2])
        lo.rect(cx + 6, bot - 1, cx + int(half) - 1, bot - 1, deck[5])
    if sign:
        # a painted board swinging on two falls from the eave, OUTBOARD of the
        # hut so it breaks the silhouette and reads from down on the floor. This
        # is why the sheet is wider than the footprint: pinch the sheet to the
        # building and the board has nowhere to hang but on top of the wall.
        bx = int(w * 0.5 + rx) + 9
        _rope(lo, bx - 6, top - 6, bx - 6, top + 1)
        _rope(lo, bx + 5, top - 6, bx + 5, top + 1)
        lo.rect(bx - 8, top + 2, bx + 7, top + 14, deck[3])
        lo.rect(bx - 8, top + 2, bx + 7, top + 2, deck[1])
        lo.rect(bx - 8, top + 14, bx + 7, top + 14, deck[5])
        lo.rect(bx - 8, top + 2, bx - 8, top + 14, deck[2])
        # THE DEVICE, never lettering: this game has no font and a painted word at
        # 16px is mud, so a trade is announced by its OBJECT. That is also the
        # scholarly-village register the town wants — a licensed trade hangs its
        # sign, and you read the shop off the thing painted on the board.
        if sign == "fang":
            # THE BRASS FANG — a curved canine, root up and point down, in a
            # collar of iron. `fang` used to fall through to the `else` below and
            # the WEAPON SHOP hung an apothecary's flask over its door, identical
            # to the shop across the square: three huts from one builder, and the
            # one thing that was supposed to tell them apart was drawing the same
            # device twice. A tooth silhouettes at 13px where a sword blade does
            # not, and it is the joke the shop's name is already making.
            # The shaded flank comes out of THATCH, not out of BRASS: BRASS[2] and
            # BRASS[3] resolve to (246,28,26) and (216,0,109), so the first pass
            # of this tooth had a HOT PINK outline. Brass is tones 0/1 only — the
            # shipped law, see the art-pipeline skill's colour section.
            for i in range(9):
                u = i / 8.0
                hw = int(round(3.4 * (1.0 - u) ** 0.75))
                cxx = bx - 1 + int(round(2.0 * u * u))          # the curve
                ty = top + 5 + i
                lo.rect(cxx - hw, ty, cxx + hw, ty, BRASS[1])
                lo.set(cxx - hw, ty, BRASS[0])                  # lit flank
                lo.set(cxx + hw, ty, THATCH[3])                 # shaded flank
            lo.rect(bx - 5, top + 3, bx + 3, top + 5, IRON[1])  # the collar
            lo.rect(bx - 5, top + 3, bx + 3, top + 3, IRON[0])
            lo.rect(bx - 5, top + 5, bx + 3, top + 5, IRON[3])
        elif sign == "sword":
            ln(lo, bx - 5, top + 11, bx + 4, top + 5, STEEL[1])
            ln(lo, bx - 5, top + 12, bx + 3, top + 6, STEEL[2])
            lo.rect(bx - 7, top + 10, bx - 4, top + 12, BRASS[1])
        elif sign == "kettle":
            lo.rect(bx - 4, top + 8, bx + 3, top + 12, COPPER[1])   # the belly
            lo.rect(bx - 4, top + 8, bx + 3, top + 8, COPPER[0])
            lo.rect(bx - 4, top + 12, bx + 3, top + 12, COPPER[3])
            lo.rect(bx - 2, top + 6, bx + 1, top + 7, COPPER[2])    # the lid
            lo.set(bx + 4, top + 9, COPPER[2])                      # the spout
            lo.set(bx + 5, top + 10, COPPER[2])
            ln(lo, bx - 1, top + 5, bx + 1, top + 3, STEAM)         # one steam curl
            lo.set(bx, top + 4, STEAM)
        else:
            lo.rect(bx - 2, top + 5, bx + 1, top + 6, GLASS)
            lo.rect(bx - 4, top + 7, bx + 3, top + 11, MINT)
            lo.rect(bx - 4, top + 7, bx + 3, top + 7, GLASS)
            lo.set(bx - 3, top + 8, SPEC)
    # THE HANGING LANTERN on an iron hook off the eave — the warm dab that makes a
    # hut read as lived in, and the only warm thing outside the window.
    lx = int(w * 0.5 - rx) - 7
    lo.rect(lx, top - 6, lx + 1, top - 3, IRON[2])
    lo.rect(lx - 2, top - 2, lx + 3, top - 2, BRASS[1])
    lo.rect(lx - 1, top - 1, lx + 2, top + 2, WARMD)
    lo.rect(lx, top, lx + 1, top + 1, WARM)
    lo.rect(lx - 2, top + 3, lx + 3, top + 3, IRON[2])
    wins.append((lx - 1, top - 1, 4, 4))
    edge(lo, H)
    anim = (lambda fa, ca, f2, dy=0: _anim_building(
        fa, ca, f2, flues=(), windows=tuple(wins), dy=dy))
    return _finish(lo, up, w, fy, H, composite, frames, anim)


# ---- 3. THE DECK ---------------------------------------------------------------------

def tree_platform(deck, f, salt=421, w=80, h=48, rails="we", fascia=6):
    """THE PLANK DECK a canopy house and its landing sit on: a plank field with
    a visible JOIST/UNDERSIDE edge along its south side and a rope railing on
    whichever sides you ask for.

    THE PLANK FIELD IS 16-PERIODIC ON PURPOSE. Two 8px boards per tile, tone
    keyed on the board index and nothing else, butt joints on a 32px stagger —
    so the whole open deck collapses to a couple of atlas tiles no matter how
    big it is, which is what lets a canopy town be mostly floor without paying
    for it in VRAM. Do not add hash-placed wear to the field: one dab keyed on
    absolute position makes every tile of the deck unique.

    `rails` is any subset of "nsew" — the OPEN sides of the deck, i.e. the ones
    with air beyond them. Leave a side unrailed where a bridge lands, a stair
    arrives, or another deck abuts, or the rail draws straight across the
    joint.
    `fascia` px at the bottom are the deck's underside: a lit edge line, the
    butt ends of the boards, and joists hanging under it every 14px. That band
    is the piece that makes the deck read as a structure with air under it and
    not as a rug lying on the ground.

    FOOTPRINT: `w // 16` x `h // 16` cells, every cell WALKABLE.
    ANCHOR: Tier-1 baked ground art — `place(chars, ...)` (or `place_each` for
    several identical decks), blitted at the feature bbox's top-left corner.
    Rails ride the SAME layer, the `town_trestle` precedent: a body at the deck
    edge draws over the near rail, and that is correct rather than a
    compromise.

    AUTHORING CONSTRAINTS a generator must assert:
      * `w % 16 == 0 and h % 16 == 0` (asserted below), and the feature bbox
        must be exactly `w//16` x `h//16` — `place()` blits at the bbox corner
        and does NOT scale, so an oversized bbox leaves raw fabric showing.
      * `set(rails) <= set("nsew")` (asserted below).
      * The deck's SOUTH row carries the fascia in its bottom `fascia` px, so a
        body standing on that row overhangs the underside by a few px. Either
        accept that (the bridge-rail read) or give the deck one extra south row
        typed SOLID as a canopy edge.
      * `place()` works off a char's WHOLE-MAP bbox, so a second deck region
        sharing the char blits one sprite across everything between them. New
        deck size = new char, or `place_each` with identical components.
    COVERAGE: 100% of every cell (opaque by construction), so a deck cell is safe
    typed solid as well as walkable."""
    assert w % 16 == 0 and h % 16 == 0, "a deck must be a whole number of cells"
    assert set(rails) <= set("nsew"), f"bad rail sides {rails!r}"
    sp = S(w, h, salt)
    fy = h - fascia
    # THE PLANK FIELD. Two tones per board and ONE seam, nothing else. The first
    # pass gave every board a lit crown and a turned far edge as well, i.e. four
    # values across 8 rows, and with butt joints every 32px the deck came out
    # unmistakably a BRICK WALL. A floor seen from above is nearly flat: long
    # boards, a hard seam between them, and the tone difference doing all the
    # work.
    # And the field is drawn from the ramp's LIT end (deck[1]/deck[2]), not its
    # middle. In a top-down scene the horizontal surfaces are the ones facing the
    # light, so a floor has to be the lightest wood on screen — pitched at the
    # same value as the house's timber it read as a vertical wall of planks no
    # matter what the seams did.
    for y in range(fy):
        b, r = (y % 16) // 8, y % 8
        base = deck[1] if b == 0 else deck[2]
        for x in range(w):
            c = (deck[3] if b == 0 else deck[4]) if r == 0 \
                else deck[0] if (r == 1 and b == 0) else base
            if x % 64 == b * 32 + 9:
                c = deck[3]                            # butt joints, rare and
            elif x % 48 == b * 24 + 17 and r in (3, 4):   # one step only
                c = deck[3]                            # a knot in a board
            sp.set(x, y, c)
    # The underside: a lit deck edge, the boards' butt ends, hanging joists. This
    # band is a VERTICAL face, so it drops two steps below the floor — that value
    # break is most of what says the deck has air under it.
    sp.rect(0, fy, w - 1, fy, deck[0])
    for y in range(fy + 1, h - 2):
        for x in range(w):
            sp.set(x, y, deck[4] if (x // 5) % 2 else deck[3])
    sp.rect(0, h - 2, w - 1, h - 2, deck[4])
    sp.rect(0, h - 1, w - 1, h - 1, deck[5])
    for jx in range(4, w - 4, 14):
        sp.rect(jx, fy + 2, jx + 2, h - 1, deck[5])
        sp.rect(jx, fy + 2, jx, h - 1, deck[4])
    if "n" in rails:
        _rail_h(sp, deck, 0, w - 1, 2, salt)
    if "s" in rails:
        _rail_h(sp, deck, 0, w - 1, fy - 8, salt)
    if "w" in rails:
        _rail_v(sp, deck, 0, fy - 1, 1, salt, dip=-1)
    if "e" in rails:
        _rail_v(sp, deck, 0, fy - 1, w - 8, salt, dip=1)
    # Moss in the four corners and nowhere else. Litter out on the open field
    # would be keyed on absolute position and would make every tile of the deck
    # unique — the corners are already off the periodic field because the rails
    # cross them, so this is the one place it is free.
    for mx, my in ((3, 4), (w - 6, fy - 6), (5, fy - 5), (w - 8, 5)):
        sp.set(mx, my, f[3]); sp.set(mx + 1, my, f[4])
        sp.set(mx, my + 1, f[4])
    _crop(sp, w, h)
    return sp


def trunk_face(bark, deck, salt=401, w=64, h=32, door=True):
    """THE TRUNK SEGMENT THE RING PASSES THROUGH — the one that carries the DOOR.

    This is the piece that makes the sketch's idea true: the house IS the tree. Not
    a hut standing on a deck, not a cottage in the boughs — a door cut into the
    trunk at deck level with a lit window over it, and a balcony round the outside.

    Cut from the same `_shaft` the rest of the tree is, at the same half-widths, so
    the bark bands and the taper continue through it and the joins are invisible.

    IT MUST NOT BE TALLER THAN ITS OWN FOOTPRINT (2 cells, h=32). Bottom-anchored
    art that overshoots reaches UP into the ring's north-arc row — a walkable cell —
    and a trunk is an opaque ~40px mass, so a body standing there is not "behind"
    anything, it is GONE. At h=48 that is exactly what shipped: `zwalk lint` measured
    0 visible pixels on all four trees, in both eras, on the one row the map header
    calls "you pass BEHIND the tree here". Anything that covers that row has to be
    PERFORATED, which a shaft cannot be — so the crown covers it and this does not.
    That is also why the window lives on `great_crown` now and not here: two cells is
    a door's worth of height and no more.

    THE DOOR'S THRESHOLD IS THE SPRITE'S BOTTOM EDGE, because that is where the
    ring's south deck meets the bark: you step off the boards straight through it.
    The map's `home` anchor sits on the deck row below, never on the trunk — a door
    does not need a walkable cell, and a walkable cell inside a Tier-3 trunk is a
    body standing behind an opaque mass.

    FOOTPRINT: `w // 16` x `h // 16` cells, EVERY CELL SOLID.
    ANCHOR: `emit_prop(name, chars, img, each=True, base_inset=19)` — that inset
    lands the sort key in the 2px of daylight between a body on the trunk row and a
    body on the deck south of it, so you pass BEHIND the tree on the north arc and
    walk in FRONT of it on the south.
    COVERAGE: 100% of the shaft's own cells.
    """
    sp = S(w, h, salt)
    cx = w / 2.0
    half = w * 0.47          # matches great_trunk: four cells of bark (see there)
    _shaft(sp, bark, cx, 0, h - 1, half, half * 1.03, salt)
    if door:
        base, dhw, dhh = h - 1, 11, h - 5
        for y in range(base - dhh, base + 1):          # the dark reveal, arched
            u = (base - y) / float(dhh)
            hx = dhw * (1.0 - max(0.0, (u - 0.62) / 0.38) ** 2) ** 0.5 \
                if u > 0.62 else dhw
            for x in range(int(cx - hx), int(cx + hx) + 1):
                sp.set(x, y, DOORDARK)
        for y in range(base - dhh + 3, base):          # the plank leaf, set back
            u = (base - y) / float(dhh)
            hx = (dhw - 2) * (1.0 - max(0.0, (u - 0.58) / 0.42) ** 2) ** 0.5 \
                if u > 0.58 else dhw - 2
            for x in range(int(cx - hx), int(cx + hx) + 1):
                sp.set(x, y, deck[3] if (x - int(cx - hx)) % 5 else deck[4])
        sp.set(int(cx + dhw - 4), base - 8, BRASS[0])  # the latch
    _crop(sp, w, h)
    return sp


def ring_geom(w, ry=44, hole=(26, 15)):
    """THE ONE PLACE THE RING'S ELLIPSE IS DEFINED: (cx, cy, rx, ry, hx, hy).

    `tree_ring` draws from these and `ring_cells` rasterizes them, so the art and
    the map's walkable cells cannot be two different opinions of where the deck
    is. They were, for one build: the disc was drawn out to the block edge and
    the map authored a tight blob inside it, which put a one-to-two-cell
    INVISIBLE WALL along the whole rim — you walked a rectangle inside a circle,
    and every cell of the mismatch looked like solid decking."""
    return (w / 2.0, ry + 4.0, w / 2.0 - 2.0, float(ry),
            float(hole[0]), float(hole[1]))


## Where the radial planking stops and the CONCENTRIC RIM BOARD begins, in the
## ellipse's own normalized radius. The rim is the deck's finished edge and the
## railing stands just outside it (at 0.955 of the ellipse, i.e. o = 0.912), so
## this one number is both "where the boards end" and "how far a body may walk".
RIM_O = 0.90


## The party body's collision box relative to its origin: half-width, and the
## top and bottom of the 12x8 footprint at its feet (entities/player/player.tscn,
## `RectangleShape2D_body` 12x8 at offset (0, 6)). The ring's mask is derived
## against this rather than against a point, so it answers the question that
## actually matters — does the BODY fit on the boards, not does the cell's centre.
BODY_BOX = (6.0, 2.0, 10.0)


def ring_cells(w, h, ry=44, hole=(26, 15), T=16, limit=RIM_O, box=BODY_BOX):
    """The ring's deck as a CELL MASK — [row][col] True where a body standing in
    the middle of that cell is ON THE RADIAL PLANKING, whole.

    THE TEST IS THE BODY'S BOX, NOT A POINT, and that is not fastidiousness — a
    single radius cannot express this, because the overhang is DIRECTIONAL. Run
    the numbers on the shipped ellipse: the cell at (row 4, col 2) has its centre
    at o = 0.652, comfortably inside anything you would call the rim, and a body
    standing there has its feet at x 34..46 against a deck that at THAT LINE, ten
    pixels further south where the arc has already curved away, spans 36.3..155.7.
    Its west foot is off the platform. Meanwhile (row 1, col 1) sits at o = 0.884,
    far worse by radius, and is fine — because its feet are ten pixels NORTH of
    its centre, which on the top half of an ellipse is further IN. Any single
    limit either keeps the first or throws away the second.

    So: place the 12x8 box at the cell centre and require all four corners inside
    `limit`. Cheap, and it is the same question the player's hands are asking.

    THE LIMIT IS THE RIM BOARD, NOT THE OUTER EDGE. The rim is the deck's finished
    lip and the handrail stands just outside it; walking to o <= 1.0 puts a body
    at the poles standing ON the rim board with the rail between its ankles. You
    walk the planking and stand BEHIND the rail. The rail is not decking.

    Returns the mask for the whole block, fascia rows included (all False) — the
    caller checks it against the map, so it has to speak about every cell. The
    south rim comes out empty and that is correct: the arc there is at y = 92, so
    ANY cell centred at y = 88 has its feet past it. The one place you are meant
    to stand on that rim is the ladder's landing, and the caller adds it back by
    name (see `_alembic.assert_all`) rather than by loosening this."""
    cx, cy, rx, ry_, hx, hy = ring_geom(w, ry, hole)
    bw, bt, bb = box
    mask = []
    for r in range(h // T):
        row = []
        for c in range(w // T):
            x, y = c * T + T // 2.0, r * T + T // 2.0
            corners = ((x - bw, y + bt), (x + bw, y + bt),
                       (x - bw, y + bb), (x + bw, y + bb))
            row.append(all(((px - cx) / rx) ** 2 + ((py - cy) / ry_) ** 2 <= limit
                           for px, py in corners)
                       and ((x - cx) / hx) ** 2 + ((y - cy) / hy) ** 2 >= 1.0)
        mask.append(row)
    return mask


def tree_ring(deck, bark, f, salt=491, w=144, h=144, ry=44, hole=(26, 15),
              fascia=16, planks=32, rail=True, ladder=True):
    """THE RING — the round collar of decking that wraps a great trunk, and the
    one thing both references are most recognisable for.

    WHY A DEDICATED BUILDER AND NOT A RECTANGLE OF `tree_platform`. The v1 canopy
    town let a body walk the full circle around every trunk and NOBODY COULD SEE
    IT, because the deck ran wall to wall and a round platform drawn in a square
    floor is not a platform, it is floor. The ring has to be an ISLAND with air
    all round it, and it has to be visibly ROUND, or the geometry is invisible and
    the tree reads as a post standing in a warehouse.

    THREE THINGS MAKE IT READ AS A CIRCLE, and it needs all three:

      1. RADIAL PLANKING. The boards run out from the trunk like spokes, so every
         board is a different angle and the eye integrates them into a disc. This
         is the whole trick — a round platform with the deck's normal east-west
         boards reads as a rectangular deck someone rounded the corners off.
      2. A CONCENTRIC RIM. Two boards following the curve right at the edge, which
         is how a real round deck is finished and, more to the point, is the only
         continuous line in the piece: it draws the circle explicitly rather than
         leaving it implied by 32 plank ends.
      3. THE FASCIA IS A CRESCENT. The vertical face hangs below the outer curve's
         SOUTHERN arc only, deepest at due south and thinning to nothing at the
         east and west poles — which is exactly what the side of a disc does seen
         from above and slightly in front. A constant-depth band all the way round
         is a cylinder seen from the side, i.e. a barrel, and that is the shape
         the first pass came out as.

    The ellipse is `w/2` x `ry`, squashed to the scene's oblique (~0.6) rather
    than circular: a true circle in a top-down-with-a-tilt scene reads as a dome.
    `hole` is the trunk's own cross-section, kept slightly WIDER than the shaft so
    a collar of shadowed decking shows all round the bark — that shadow is what
    plants the tree THROUGH the boards instead of on top of them.

    FOOTPRINT: `w//16` x `h//16` cells. The deck cells are WALKABLE on the ring's
    own stratum; the middle of the trunk row is the shaft and stays solid. The
    north arc is walk-behind under the crown, which is why `great_crown` is
    perforated — see its docstring.
    ANCHOR: returns (lower, upper). The deck, the fascia and the rail's NORTH arc
    are Tier-1 (bodies draw over a floor and over the far rail); the rail's SOUTH
    arc is the UPPER layer, so a body on the boards stands behind it. Blit both at
    the block's top-left, per component — one ring per great tree.
    COVERAGE: 100% on the deck rows, >= 62% on the fascia crescent's own cells.
    """
    assert w % 16 == 0 and h % 16 == 0, "a ring must be a whole number of cells"
    sp = S(w, h, salt)
    up = S(w, h, salt + 1)                     # the UPPER layer: the south rail
    cx, cy, rx, ry, hx, hy = ring_geom(w, ry, hole)   # shared with ring_cells
    TAU = 6.283185307179586

    def _out(x, y):
        return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2

    def _in(x, y):
        return ((x - cx) / hx) ** 2 + ((y - cy) / hy) ** 2

    # 0. THE CAST SHADOW, and NOT a leaf bed. The first pass filled the whole canvas
    # with foliage so the block would be opaque — and in-engine that read as a dark
    # RECTANGLE sitting on the forest, because two different leaf renderings meeting
    # at a cell boundary is a seam however good either one is. It was also solving a
    # problem that does not exist: the block's cells render `forest` terrain, which
    # autotiles with the woods around it, so transparent art over them shows canopy
    # and the invisible-wall lint is satisfied by the terrain underneath.
    #
    # What the disc actually needs is separation, and a platform gets that from the
    # shade it throws on the leaves below. Drawn as a band OUTSIDE the outer ellipse,
    # so its edge is a curve rather than the sprite's rect — offset south and east
    # like every other shadow in the game.
    for y in range(h):
        for x in range(w):
            d = ((x - cx - 5) / (rx + 7)) ** 2 + ((y - cy - 6) / (ry + 7)) ** 2
            if 0.62 < d <= 1.0 and _out(x, y) > 1.0:
                sp.set(x, y, f[4] if d < 0.86 else f[5])

    # 1. THE FASCIA CRESCENT, drawn first so the deck's rim overwrites its top
    # edge and the two meet with no seam. For every column the outer curve's
    # SOUTH intercept is ys; the face hangs `fascia` px below it, scaled by how
    # square-on that part of the curve faces us — full depth at due south, zero
    # at the poles. Same graded darkening every other vertical face in this town
    # uses (see _alembic.shaded): a face is darker than the floor it hangs off.
    for x in range(w):
        t = (x - cx) / rx
        if abs(t) >= 1.0:
            continue
        k = (1.0 - t * t) ** 0.5
        ys = cy + ry * k
        d = int(round(fascia * k))
        for i in range(d):
            y = int(ys) + i
            if not 0 <= y < h:
                continue
            # the butt ends of the radial boards, then two darker courses under
            sp.set(x, y, deck[3] if i < 2 else deck[4] if i < d - 2 else deck[5])
        # the lit arris where floor turns into face — one px, and it is what
        # keeps the fascia from reading as a shadow cast on the leaves below
        if 0 <= int(ys) < h:
            sp.set(x, int(ys), deck[0])
    # KNEE BRACES. A ring this wide cannot be holding itself up, and a disc with
    # nothing under it reads as a lily pad floating in the leaves. Four timbers
    # angling back to the trunk say cantilever, which is the structural idea both
    # references are built on. Drawn under the crescent's lower edge only.
    for bt in (-0.74, -0.34, 0.34, 0.74):
        k = (1.0 - bt * bt) ** 0.5
        bx0 = cx + rx * bt
        by0 = cy + ry * k + fascia * k * 0.7
        bx1 = cx + hx * bt * 0.7
        by1 = by0 + 16 + 10 * (1.0 - abs(bt))
        for i in range(int(by1 - by0)):
            u = i / max(1.0, by1 - by0)
            bx = bx0 + (bx1 - bx0) * u
            yy = int(by0 + i)
            if not 0 <= yy < h:
                continue
            sp.set(int(round(bx)), yy, bark[3])
            sp.set(int(round(bx)) + 1, yy, bark[4])
            sp.set(int(round(bx)) - 1, yy, bark[2])
    # 2. THE DECK — radial boards between the trunk hole and the outer curve.
    for y in range(h):
        for x in range(w):
            if _out(x, y) > 1.0 or _in(x, y) < 1.0:
                continue
            a = _turns64(y - cy, x - cx) / 64.0            # 0..1 around the ring
            p = a * planks
            board = int(p)
            # Alternating every board made the whole disc a striped fan. Timber
            # varies irregularly: keep most boards in the field tone and let a
            # salted minority lift one step, with no absolute-position texture.
            c = deck[2] if h2(board, salt, 503) % 5 == 0 else deck[1]
            seam = p - board
            if seam < 0.055:                               # the seam between two
                c = deck[3]                                # boards, one step down
            # Long radial boards still need ends. Stagger one narrow butt joint
            # per board so the spokes read as carpentry rather than painted rays.
            radius = _out(x, y) ** 0.5
            joint = 0.68 + 0.09 * (h2(board, salt, 509) % 3)
            if seam > 0.11 and abs(radius - joint) < 0.006:
                c = deck[3]
            sp.set(x, y, c)
    # 3. THE CONCENTRIC RIM — two boards following the curve, and the SHADOW
    # COLLAR where the boards die into the bark. Both are drawn as bands in the
    # ellipse's own normalized radius so they stay parallel to the edge all the
    # way round rather than bunching at the poles.
    for y in range(h):
        for x in range(w):
            o = _out(x, y)
            if o > 1.0 or _in(x, y) < 1.0:
                continue
            if o > RIM_O:
                sp.set(x, y, deck[2] if o > 0.96 else deck[1])
            if o > 0.985:
                sp.set(x, y, deck[3])
            i2 = _in(x, y)
            if i2 < 1.55:                                   # the trunk's shadow
                sp.set(x, y, deck[4] if i2 < 1.28 else deck[3])
    # 4. THE RAILING, on the outer curve and OPEN AT DUE SOUTH where the ladder
    # and the bridges land. Posts are set on the ellipse itself and the hemp runs
    # post to post, so the handline is the circle drawn a second time, 6px up.
    #
    # THE SOUTHERN HALF OF IT GOES ON THE UPPER LAYER, and this is the whole
    # difference between a railing and a stripe painted on the boards. Baked with
    # the deck, every body on the ring draws OVER the rail — you stand on the
    # handline like it is a kerb. But a ring is a closed curve seen from the
    # south, so the two halves want opposite answers and a y-sorted sprite can
    # only give one: the NORTH arc is behind you (it is further away) and the
    # SOUTH arc is in front of you (it is between you and the camera). Split at
    # the ellipse's own waist and each half is unconditionally right — every
    # walkable cell is INSIDE the curve, so nothing can ever need to draw in
    # front of the south arc. `tree_edge` argues the same point for the fascia
    # and buys it from mask_band; a rail up on the deck rows has no band to hide
    # in, so it buys it from the upper layer instead.
    if rail:
        import math
        n = 26
        pts = []
        for i in range(n):
            a = TAU * i / n
            t = a / TAU
            if 0.20 < t < 0.30:                             # the south gap
                pts.append(None)
                continue
            px_ = cx + rx * 0.955 * -math.sin(a - 1.5707963)
            py_ = cy + ry * 0.955 * math.cos(a - 1.5707963)
            pts.append((px_, py_))
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            if a is None or b is None:
                continue
            for s in range(0, 24):
                u = s / 23.0
                fy = a[1] + (b[1] - a[1]) * u               # the foot of the rail
                lx = int(round(a[0] + (b[0] - a[0]) * u))
                ly = int(round(fy)) - 6
                if 0 <= lx < w and 0 <= ly < h:
                    tgt = up if fy > cy else sp
                    tgt.set(lx, ly, ROPE[1])
                    tgt.set(lx, ly + 1, ROPE[3])
        for pt in pts:
            if pt is None:
                continue
            px_, py_ = int(round(pt[0])), int(round(pt[1]))
            tgt = up if pt[1] > cy else sp
            tgt.rect(px_, py_ - 7, px_ + 1, py_, deck[3])
            tgt.rect(px_, py_ - 7, px_, py_, deck[1])
            tgt.set(px_ + 1, py_, deck[5])
    # 5. THE LADDER HEAD, in the railing's south gap.
    #
    # A rope ladder that simply BEGINS in mid-air below the deck is the single
    # commonest tell that a platform is floating art rather than a place — it was
    # the first thing spotted in the ring preview, and it is spotted because a
    # ladder is the one object in frame whose whole job is to connect two things.
    # Three cues fix it and they are cheap: a stout CLEAT board across the rail
    # gap for the stiles to be lashed to, the stiles OVERSHOOTING the deck by ~10px
    # (every real ladder head stands proud of the thing it leans on — flush with
    # the edge reads as a hole in the boards), and visible LASHINGS wrapping the
    # cleat. Then the stiles run on down to the sprite's bottom edge, so
    # `rope_ladder`'s own run — whose stiles sit at 9 and 22 of a 32-wide box —
    # continues them exactly when it is authored on the cell below.
    if ladder:
        lx0, lx1 = int(round(cx)) - 7, int(round(cx)) + 6
        rim = int(cy + ry)
        # THE CLEAT sits proud of the fascia and two steps LIGHTER than it. Drawn
        # in the fascia's own tones it vanished — a fixing has to out-value the
        # thing it is fixed to or it reads as a stain on the timber.
        sp.rect(lx0 - 6, rim - 4, lx1 + 6, rim, deck[1])
        sp.rect(lx0 - 6, rim - 5, lx1 + 6, rim - 5, deck[0])       # its lit crown
        sp.rect(lx0 - 6, rim + 1, lx1 + 6, rim + 2, deck[5])       # and its shadow
        sp.set(lx0 - 6, rim - 4, deck[3]); sp.set(lx1 + 6, rim - 4, deck[3])
        # the stiles OVERSHOOT by ~8px only. At 15 the ladder read as lying flat
        # ON the boards rather than hanging off the rim behind them.
        for i, sx in enumerate((lx0, lx1)):
            _rope(sp, sx, rim - 8, sx, h - 1, phase=i * 2, wide=True)
        for sx in (lx0, lx1):                                      # the lashings —
            for yy in range(rim - 4, rim + 2):                     # a fat wrap over
                sp.set(sx - 2, yy, ROPE[2]); sp.set(sx - 1, yy, ROPE[0])
                sp.set(sx + 2, yy, ROPE[1]); sp.set(sx + 3, yy, ROPE[3])
            sp.set(sx - 2, rim - 4, ROPE[3]); sp.set(sx + 3, rim + 1, ROPE[3])
        # rungs from the head all the way to the sprite's bottom edge, on the same
        # irregular pitch `rope_ladder` uses — a rung every N px exactly reads as a
        # machined ladder bolted to a wall, and this one is hanging.
        ry_, n = rim - 13, 0
        while ry_ < h - 2:
            if ry_ < rim - 6 or ry_ > rim + 2:            # never across the cleat
                sp.rect(lx0 - 1, ry_, lx1 + 2, ry_ + 1, deck[2])
                sp.rect(lx0 - 1, ry_, lx1 + 2, ry_, deck[0])
                sp.rect(lx0 - 1, ry_ + 2, lx1 + 2, ry_ + 2, deck[5])
            ry_ += 9 + h2(n, 3, salt) % 3
            n += 1
    _crop(sp, w, h)
    _crop(up, w, h)
    assert any(p for row in up.px for p in row), \
        "the ring's upper layer is empty — the south rail did not split"
    return sp, up


# ---- 3b. THE CANOPY EDGE — the piece that carries the whole "this is UP" read ---------
# tree_platform's own fascia is 6px at the bottom of its last row, which is a
# rug's hem, not a storey's face. The map answers it the way the terrace kit
# always has: the deck gets one extra south row typed SOLID, and that row wears
# its own 16 x (16*run) column of opaque face art, stamped per vertical run by
# TileScene.stamp_columns exactly as town_cliff is. This is that art.
#
# THE CREST IS A FIXED 12px AND THAT IS NOT A STYLE CHOICE. TileScene.mask_band
# copies the top `band` px of the run — 12, derived from the 11px of sprite that
# hangs past a south-pressed body's feet box — and re-emits them as a Tier-3
# y-sorted strip keyed at run_top - 8. So whatever lives in the fascia's top 12px
# is the paint that draws OVER a body standing on the deck, and whatever lives
# below it never does. That is the entire reason THE RAIL IS DRAWN INTO THE
# FASCIA rather than added as a char or a prop: put the posts and the lashed
# handline in those twelve pixels and a body at the edge stands BEHIND the rail
# for free, in the one z-order arrangement that is unconditionally right (see
# docs/DESIGN.md's mask-band paragraph, and the 2026-07-19 fence lesson for what
# a railing baked on the lower layer looks like instead: standing ON it).
# Everything below the crest scales with `h`; the crest does not.

_EDGE_CREST = 12         # the mask_band contract: crest rows 0..11, face 12..h-1


def _edge_crest(sp, deck, f, x0, x1, salt, rail=True, post=7):
    """The fascia's top `_EDGE_CREST` px across x0..x1: the deck's own last two
    boards seen in plan, the hemp HANDLINE on its stanchions, and then the edge
    beam's NOSE standing proud with the shadow it throws down the face.

    All three earn their pixels:
      * the last boards continue the deck fabric across the cell line, so the
        fascia does not open on a hard seam;
      * the handline is what a body at the edge is drawn BEHIND (see the section
        note — this is the whole reason the rail lives here);
      * THE NOSE IS THE READ. town_cliff learned it three times over: a crest
        that merely CAPS says "the ground stops", and only a crest that stands
        PROUD and throws a shadow says "this is the TOP of something". Two lit
        rows then two dark ones, in that order and no other.

    `post` is the x of the single stanchion in this 16px column — ONE per cell,
    not one per 8px. At 8px they came out a picket fence beside a 22px cat."""
    for x in range(x0, x1 + 1):
        sp.rect(x, 0, x, 1, deck[1])                   # the deck's last boards,
        sp.set(x, 2, deck[4])                          # continuing past the cell
        sp.rect(x, 3, x, 5, deck[1])                   # line with their seam
        sp.set(x, 6, deck[0])                          # THE NOSE: its lit arris,
        sp.rect(x, 7, x, 8, deck[1])                   # its front, standing proud
        sp.set(x, 9, deck[4])                          # the shadow it throws down
        sp.rect(x, 10, x, 11, deck[5])                 # the face below
    if not rail:
        return
    # THE HANDLINE. Two laid ropes swagged between squat stanchions — _rail_h's
    # geometry re-pitched to the 16px cell so a run of columns comes out one
    # continuous rail however stamp_columns hashes its variants. Ropes first and
    # the post over them: a post has to read as standing in FRONT of its own
    # rope.
    #
    # AND IT ALL STAYS CLEAR OF THE NOSE. The first pass ran the lower rope
    # through the nose rows and painted the nose out, which took the whole "this
    # is a top" cue with it — the crest came out boards, a chain, and then a
    # wall. The rail is furniture standing ON the deck and the nose is the deck's
    # own edge, so the rail gets the crest's top six px and not one more.
    for ry, c in ((0, ROPE[1]), (3, ROPE[2])):
        for x in range(x0, x1 + 1):
            s = 1 if 4 < (x - post) % 16 < 12 else 0   # the swag between posts
            sp.set(x, ry + s, c)
            sp.set(x, ry + s + 1, ROPE[3])
    for px_ in range(post, x1 + 1, 16):
        if px_ < x0:
            continue
        sp.rect(px_, 0, px_ + 1, 5, deck[3])           # the stanchion,
        sp.rect(px_, 0, px_, 5, deck[1])               # lit on its west face
        sp.set(px_ + 1, 0, deck[4])
        sp.set(px_ + 1, 5, deck[5])
        _lash(sp, px_ - 1, px_ + 2, 2, across=False)   # seized to the beam


def tree_edge(deck, f, salt=471, h=32, rail=True, lantern=False):
    """THE CANOPY EDGE — one 16 x `h` column of the fascia along a deck's south
    lip, stamped per vertical run by TileScene.stamp_columns. The timber twin of
    town_cliff, and the piece the whole "this is UP" read hangs on.

    FULLY OPAQUE, NO edge(): the deck fabric's phase varies above it and the
    forest floor's below, and a per-column outline would print a seam every
    16px. Tier-1, baked.

    `h` must equal T * the map run height (32 for a `b` band, 48 for a `v` one).
    The CREST is a fixed 12px — see the section note; only the FACE scales.

    THE THREE LESSONS, transposed from town_cliff(wall=True) to timber:
      1. THE NOSE STANDS PROUD and throws a shadow down the face. Without the
         overhang there is no top, only a boundary. (_edge_crest.)
      2. ALL CONTRAST LIVES IN A REGULAR GRID, none in per-plank value. Cement
         taught it as a running-bond joint grid; timber says it as SHEATHING
         BUTTS on a fixed pitch plus one JOIST per 16px column, one step lighter
         than the boards so it stands off them. Per-plank value variation reads
         as rubble in cement and as driftwood in timber — the salted variants
         differ only in litter, never in the frame.
      3. NEAR-BLACK CONTACT AT THE FOOT, or the storey floats.
    The one addition timber wants and masonry does not: a LASHED LEDGER. Nobody
    up a tree drives iron, so the beam that carries the joists is seized to them
    with hemp — and it runs the full width of every column, so a run of them
    comes out as ONE line across the whole boardwalk. A diagonal brace was tried
    first and is the thing to avoid: 16px is too narrow to hold a diagonal, so
    per column it reads as a scratch and per run as a zigzag.

    It takes NO `bark` ramp, unlike every other piece in this kit, and that is
    the result rather than an omission: bark-backed stanchions and a bark brace
    were both tried and both read as cool blue-violet scratches on warm timber at
    1x, because this game's `trunk` seed is a teal-violet. The whole fascia is
    ONE material plus hemp, which is also what a carpenter would have built it
    out of. The great trunks that pierce a band wear their own sprite.

    FOOTPRINT: 1 x `h // 16` cells, every cell SOLID (it is the face).
    ANCHOR: `stamp_columns(chars, sprites, run=h//16)`, blitted at each run's TOP
    cell. Follow it with `mask_band(chars)` — LAST, after every lower write.
    COVERAGE: 100% of every cell (opaque by construction).

    AUTHORING CONSTRAINTS a generator must assert:
      * `h == 16 * run` and every run of the band char exactly `run` cells —
        stamp_columns' own assert, and the reason it exists.
      * The band's NORTH edge is walkable deck and its south is solid or the
        floor below: TileScene.assert_band_orientation. A fascia IS the south
        edge of a storey, and upside down it renders perfectly.
      * `mask_band` on the band char, never on a char whose run is the lift
         shaft — the unmasked gap there IS the gate onto the boat."""
    assert h % 16 == 0 and h >= 32, "a canopy edge is a whole number of cells >= 2"
    sp = S(16, h, salt)
    foot = h - 2
    # ---- THE FACE: horizontal sheathing, graded down, then the frame over it ----
    # The grade is town_cliff's (b_mid / b_low), in 32nds of the face so h=48
    # scales instead of putting its dark foot across the middle: a vertical face
    # loses light toward the ground and a flat one floats.
    mid = _EDGE_CREST + (h - _EDGE_CREST) * 15 // 32
    for y in range(_EDGE_CREST, h):
        base = deck[3] if y < mid else deck[4]
        for x in range(16):
            sp.set(x, y, base)
    # ONE line per course, ONE STEP DOWN, and ONLY IN THE LIT ZONE. This is
    # town_cliff's cinderblock note applied to boards, and the first pass broke
    # it in every direction at once — a lit bed AND a near-black joint per 8px
    # course, plus a d[1]/d[5] three-px joist, plus joints carried down into the
    # dark zone — so at 1x the fascia came out a PICKET FENCE you read straight
    # through: light posts, dark panels between them, exactly the "wall reads as
    # a lattice" failure. Under a real deck the lower half is in its own shadow
    # and there is nothing to see there, so the grid stops at `mid` and the dark
    # zone stays clean.
    for y in range(_EDGE_CREST + 7, mid, 8):           # the sheathing joints,
        for x in range(16):                            # 8px like the deck's own
            sp.set(x, y, deck[4])
    # THE JOIST: one per column, at a FIXED x in every variant. Its whole job is
    # the 16px rhythm, so a hashed position would dissolve the very grid lesson 2
    # is about — the variants vary litter, never the frame. A 2px hairline, one
    # step off the field: enough to stand off the boards, not enough to become a
    # baluster, and it fades into the shade zone with everything else.
    for y in range(_EDGE_CREST, h - 4):
        sp.set(6, y, deck[2] if y < mid else deck[3])  # lit west arris
        sp.set(7, y, deck[4] if y < mid else deck[5])  # its own shade, east
    # THE LEDGER, seized to the joist: a beam across the full width, one course
    # down from the crest, with three turns of hemp where the two members cross.
    ly = _EDGE_CREST + (h - _EDGE_CREST) * 11 // 32
    for x in range(16):
        sp.set(x, ly, deck[1])
        sp.set(x, ly + 1, deck[2])
        sp.set(x, ly + 2, deck[4])
    _lash(sp, ly - 1, ly + 2, 6, across=True)
    # LITTER — the only thing the salted variants disagree about, and there is
    # exactly one per variant: either a knot in a board or a vine trailing off
    # the nose. Two at once came out as speckle, which reads as mould.
    if h2(salt, 0, 3) % 2:
        kx, ky = 11 + h2(salt, 1, 3) % 3, ly + 5 + h2(salt, 2, 5) % 4
        sp.set(kx, ky, deck[4]); sp.set(kx + 1, ky, deck[5])
        sp.set(kx, ky + 1, deck[5])
    else:
        vx = 12 + h2(salt, 3, 7) % 2
        for vy in range(_EDGE_CREST, min(foot, ly + 4 + h2(salt, 4, 11) % 5)):
            sp.set(vx, vy, f[2] if (vy - _EDGE_CREST) % 3 else f[4])
    if lantern:
        # A CANDLE LANTERN ON A WROUGHT-IRON HOOK, swung under the nose. One
        # variant in six carries it, so a boardwalk gets a light roughly every six
        # tiles rather than a string of them — and the generator's glow pass
        # recomputes the SAME hash to lay a warm dab on exactly these columns.
        #
        # It is the town's one piece of scholarly-trade dressing that costs no
        # legend char and no manifest row: the fascia is already an authored
        # per-column sprite, so the light hangs off the structure that is there.
        # A lantern on a POST would have wanted a walkable mantle char per storey,
        # and a mantle carries a stratum — which is how deck lamps fused two
        # storeys the first time they were tried.
        lx, ly2 = 8, _EDGE_CREST + 2
        sp.set(lx, ly2 - 1, IRON[2])                   # the hook off the nose
        sp.set(lx + 1, ly2 - 1, IRON[1])
        sp.set(lx + 1, ly2, IRON[2])
        sp.rect(lx - 1, ly2 + 1, lx + 2, ly2 + 1, BRASS[1])      # the cap
        sp.rect(lx - 1, ly2 + 2, lx + 2, ly2 + 5, WARMD)         # the horn panes
        sp.rect(lx, ly2 + 3, lx + 1, ly2 + 4, WARM)              # the flame
        sp.rect(lx - 1, ly2 + 6, lx + 2, ly2 + 6, IRON[2])       # the base ring
        sp.set(lx - 2, ly2 + 3, IRON[3])                         # the stays
        sp.set(lx + 3, ly2 + 3, IRON[3])
    for y in range(h - 4, h):                          # the shade deepening to
        for x in range(16):                            # a near-black contact
            sp.set(x, y, deck[5] if y >= h - 2 else deck[4])
    _edge_crest(sp, deck, f, 0, 15, salt, rail=rail)
    clipw(sp, 16)
    return sp


def tree_edge_return(deck, f, salt=471, face=-1, w=5, cap=True):
    """The RETURN at a canopy band's STAIRCASE STEP — the short piece of fascia
    you see edge-on where one run steps down to the next. 16x16, painting only a
    `w`-px strip down the exposed side, blitted by TileScene.stamp_columns(ret=).

    The timber twin of town_cliff_return, and it exists for the identical
    reason: bands must staircase (a uniform band reads as one wall drawn twice),
    and at every step the higher run's face used to stop at a straight vertical
    cut against open air, so two runs read as two unrelated structures instead of
    one boardwalk stepping down. Carrying the NOSE around the corner is what
    resolves them into one.

    Same crest rows as tree_edge so the nose line crosses the corner without a
    seam, one step darker through the body (a side face is turned off the light),
    a lit arris on the inner corner and near-black on the outer silhouette.
    `face` is which side is exposed: -1 west, +1 east. `cap=False` is the LOWER
    run's bottom row, which has solid wall above it and therefore no nose."""
    sp = S(16, 16, salt)
    xs = list(range(w)) if face < 0 else list(range(16 - w, 16))
    inner = w - 1 if face < 0 else 16 - w              # the corner, catching light
    outer = 0 if face < 0 else 15                      # the silhouette edge
    top = _EDGE_CREST if cap else 0
    for x in xs:                                       # the return face, turned
        for y in range(top, 16):                       # away from the light
            sp.set(x, y, deck[4])
        for y in range(top + 7, 16, 8):                # its sheathing joints
            sp.set(x, y, deck[5])
    if cap:
        _edge_crest(sp, deck, f, xs[0], xs[-1], salt, rail=False,
                    post=xs[0] + 1 if face < 0 else xs[-1] - 2)
    for y in range(top, 16):
        sp.set(inner, y, deck[2])                      # lit arris ON the corner
        sp.set(outer, y, deck[5])                      # near-black silhouette
    clipw(sp, 16)
    return sp


def tree_span_edge(deck, salt=479, band=12):
    """A SPAN'S 1-ROW FASCIA — one 16x16 cell of the underside you see along a
    rope bridge's south edge: the bearer beam's lit cap standing proud, the
    shadow it throws, the plank BUTT ENDS above the bearer, its hemp seizings,
    and a near-black underside.

    It carries NO handline, and that is deliberate: `tree_bridge` already draws
    the span's near rail inside its own second row, so a rail here would be the
    same rope twice, 16px apart.

    WHY A 1-ROW FASCIA GETS AUTHORED ART INSTEAD OF A MIRRORED BAND. mask_band is
    illegal on a 1-row run and always was — DESIGN.md's z-order doctrine forbids
    banding a 1-row solid strip between two walkable rows outright, because the
    corridor feet and the south head want the same twelve pixels and one of them
    always wears it. A span's south row IS that strip. So the answer is the
    shipped `bridge_fascia` one: author the art, put it on the UPPER layer where
    it draws over a pressed body unconditionally, and accept that nothing can
    stand south of it anyway (a span's under-mass is solid by the SPAN LAW).

    `band` is how many of the 16 rows the generator lifts to the upper layer —
    12, the same derived number mask_band uses, and the reason the composition is
    front-loaded: everything that has to draw over a body lives in rows 0..11.

    FOOTPRINT: 1x1 cell, SOLID.
    ANCHOR: Tier-1 on the LOWER canvas (`bg.blit_cell`) AND the top `band` rows
    mirrored onto the UPPER canvas — the `_town_props._eave_lift` idiom, so the
    two copies are the same pixels at the same coordinates and can never seam.
    Over a WATER cell it goes upper-ONLY: OverWorld._lower_frames repaints river
    cells every frame and asserts frame 0 is byte-identical, so a lower blit
    there both vanishes and trips the purity assert.
    COVERAGE: 100% (opaque by construction)."""
    sp = S(16, 16, salt)
    sp.rect(0, 0, 15, 0, deck[0])                      # the bearer's lit cap,
    sp.rect(0, 1, 15, 1, deck[1])                      # standing proud
    sp.rect(0, 2, 15, 2, deck[4])                      # the shadow under it
    for y in range(3, 10):                             # the planks' butt ends
        for x in range(16):
            sp.set(x, y, deck[2] if (y - 3) % 4 < 2 else deck[3])
    for x in range(1, 16, 5):                          # their seams
        sp.rect(x, 3, x, 9, deck[4])
    sp.rect(0, 10, 15, 12, deck[4])                    # the bearer beam
    sp.rect(0, 10, 15, 10, deck[3])
    for x in (3, 11):                                  # seized to the stringers
        _lash(sp, 10, 12, x, across=True)
    sp.rect(0, 13, 15, 15, deck[5])                    # the near-black underside
    clipw(sp, 16)
    return sp


# ---- 4. THE ROPE BRIDGE --------------------------------------------------------------

def tree_bridge(deck, salt=431, horiz=True, cells=4, sag=5):
    """A PLANK-AND-ROPE SPAN between two decks, in both orientations.

    `horiz=True`  -> `16*cells` x 32, crossed EAST-WEST, planks running N-S
                     (across the walking direction, as a bridge's boards do),
                     hemp handrails along both long edges.
    `horiz=False` -> 32 x `16*cells`, crossed NORTH-SOUTH, planks running E-W.

    THE SAG IS THE WHOLE READ, and in flat top-down it has to be projected
    rather than drawn. A crossed span dips in the middle, so on an east-west
    bridge the NEAR (south) edge bows toward the camera by `sag` px and the FAR
    edge by a third of that — the asymmetry is what says "this is dipping away
    from me" instead of "this is a bent plank". On a north-south bridge the
    same load makes a rope span SPLAY, so both rails bow OUTWARD at mid-span
    instead. Both curves are `4u(1-u)`, which is exactly zero at both ends —
    that is what keeps the BUTT-ENDS clean.

    The butt-ends are a square 3px bearer beam across the full deck width, with
    no rope or post overshoot: it butts flush against a `tree_platform` fascia
    or a `tree_stair` head with no gap and no overlap.

    FOOTPRINT: `cells` x 2 cells (`horiz`) or 2 x `cells`, every cell WALKABLE.
    ANCHOR: Tier-1 baked, `place()` / `place_each()` at the bbox's top-left.
    Opaque only across the deck band — the rows outside the rails stay clear so
    whatever the map has under the span (leaf mass, void, the understory far
    below) shows through, which is most of why it reads as a bridge and not as
    a corridor.

    AUTHORING CONSTRAINTS a generator must assert:
      * `cells >= 2` (asserted below). A 1-cell span has no mid-span, so the
        sag is zero everywhere and it reads as a doorstep.
      * The 2-cell CROSS dimension is fixed by the art and is not optional: the
        rails live in it. A 1-cell-wide bridge would put a rail on the walking
        line.
      * Both ends must abut a deck or a stair head, never open ground. The
        bearer beam is drawn as though it is bearing on something.
      * The perpendicular run is what a body walks: a `horiz` bridge must be
        entered from the east or west, so do not wall its ends with solid
        cells.
    COVERAGE: measured floor 82.8% (`horiz`) / 80.5% (vertical) — the deck band
    fills most of every cell, so a bridge cell also clears `T3_COVER_MIN` if a map
    ever wants one solid."""
    assert cells >= 2, "a rope span needs a mid-span to sag at"
    W, H = (16 * cells, 32) if horiz else (32, 16 * cells)
    sp = S(W, H, salt)
    run = (W if horiz else H) - 1
    # Geometry in the CROSSING direction at zero sag, then the bow added. The two
    # orientations get their own constants rather than sharing one set: an
    # east-west span bows only southward (so the near edge has all the travel and
    # the far edge almost none) while a north-south span SPLAYS symmetrically,
    # and sharing the numbers put the west rail two pixels off the canvas.
    if horiz:
        A_ROPE, A_EDGE, B_EDGE, B_ROPE = 1, 4, 24, 27
        P_A, P_B = 22, 26                              # the near post
        BOW_A, BOW_B = 0.30, 1.00
    else:
        A_ROPE, A_EDGE, B_EDGE, B_ROPE = 3, 6, 25, 28
        P_A, P_B = 22, 28
        BOW_A, BOW_B = -0.60, 0.60
    for i in range(3, run - 2):
        u = i / float(run)
        bw = 4.0 * u * (1.0 - u)                       # 0 at the ends, 1 mid
        da = int(round(sag * BOW_A * bw))
        db = int(round(sag * BOW_B * bw))
        a0, b0 = A_EDGE + da, B_EDGE + db
        mid = (a0 + b0) // 2
        for k in range(a0, b0 + 1):
            if k == a0:
                c = deck[0]                            # the far stringer, lit
            elif k == b0:
                c = deck[3]                            # the near one, turning
            elif i % 6 == 0:
                c = deck[4]                            # plank seams, running
            elif i % 6 == 1:                           # ACROSS the walk
                c = deck[0]
            elif abs(k - mid) < 2 and h2(i // 3, 0, salt) % 4:
                c = deck[0]                            # the worn walking line
            else:
                c = deck[1] if h2(i // 6, 0, salt) % 3 else deck[2]
            sp.set(*((i, k) if horiz else (k, i)), c)
        sp.set(*((i, b0 + 1) if horiz else (b0 + 1, i)), deck[5])
        for r0, ph in ((A_ROPE + da, 0), (B_ROPE + db, 2)):
            sp.set(*((i, r0) if horiz else (r0, i)),
                   (ROPE[0], ROPE[1], ROPE[2])[(i + ph) % 3])
            sp.set(*((i, r0 + 1) if horiz else (r0 + 1, i)), ROPE[3])
    for i in range(4, run - 3, 16):                    # posts + lashings
        u = i / float(run)
        bw = 4.0 * u * (1.0 - u)
        da = int(round(sag * BOW_A * bw))
        db = int(round(sag * BOW_B * bw))
        for p0, p1 in ((A_ROPE - 1 + da, A_ROPE + 3 + da), (P_A + db, P_B + db)):
            if horiz:
                sp.rect(i, p0, i + 1, p1, deck[3])
                sp.rect(i, p0, i, p1, deck[1])
                sp.set(i + 1, p1, deck[5])
            else:
                sp.rect(p0, i, p1, i + 1, deck[3])
                sp.rect(p0, i, p1, i, deck[1])
                sp.set(p1, i + 1, deck[5])
        for e0 in (A_EDGE + da, B_EDGE + db):
            sp.set(*((i, e0) if horiz else (e0, i)), ROPE[2])
            sp.set(*((i + 1, e0) if horiz else (e0, i + 1)), ROPE[2])
    # THE BUTT-ENDS: a square bearer beam across the full deck band, no rope or
    # post overshoot, so the span meets a deck fascia flush
    for s0 in (0, run - 2):
        for i in range(s0, s0 + 3):
            for k in range(A_EDGE, B_EDGE + 2):
                sp.set(*((i, k) if horiz else (k, i)), deck[3])
            sp.set(*((i, A_EDGE) if horiz else (A_EDGE, i)), deck[0])
            sp.set(*((i, B_EDGE + 1) if horiz else (B_EDGE + 1, i)), deck[5])
    _crop(sp, W, H)
    return sp


# ---- 5. THE WAY UP: rope, not stone --------------------------------------------------
# A canopy town has no masonry stair and never had one: everything vertical here
# is rope over a sheave. Two pieces cover it — the ROPE LADDER everybody uses
# every day, and the DINGHY LIFT, the machine the town is known for.

def rope_ladder(deck, bark=None, salt=441, cells=2, face=1):
    """A ROPE LADDER down a trunk face, 32 x `16*cells` — the everyday way up,
    sized in cells exactly like `town_stairs(cells=n)` so it can pierce a canopy
    band of n rows.

    FULLY OPAQUE and UN-OUTLINED, for the same two reasons the stone flight is:
    the run must butt seamlessly into the deck above and the ground below, and
    an opaque cell dedupes no matter what the fabric underlay's phase is doing
    beneath it. The backing that makes it opaque is the TRUNK the ladder hangs
    on (pass the bark ramp), or a plank chute with `bark=None`.

    WHAT MAKES IT READ AS ROPE. Two things, and neither is optional at 16px
    tiles:
      * the stiles are LAID rope (`_rope`) — a 3px-period light/mid/dark twist
        along their length. A straight one-tone line is a scratch and a
        two-tone one is a wire; only the periodic lay says hemp.
      * the rung spacing is IRREGULAR, hashed +-1px, and every third rung sits
        a pixel out of level. Perfectly pitched rungs read as a machined
        ladder bolted to a wall; a rope ladder hangs, and hanging things are
        never square.

    FOOTPRINT: 2 x `cells` cells, every cell WALKABLE.
    ANCHOR: Tier-1 baked, `place_each(chars, ...)` at each component's
    top-left. `place_each`, never `place` — two ladders sharing a char would
    make `place()` blit one sprite across their combined bbox, i.e. across the
    whole town.
    COVERAGE: 100% of every footprint cell (opaque by construction), so it is
    safe on solid cells too if a map wants the ladder itself impassable.

    AUTHORING CONSTRAINTS a generator must assert:
      * `cells` MUST equal the height of the canopy band it pierces (the
        `town_stairs` law). The art lands on the run's TOP cell, so a short
        ladder leaves the bottom of the drop wearing raw fabric and a tall one
        paints ladder over the walkable cell below it.
      * A walkable cell directly north AND south, so the trail painter's ribbon
        connects through; the opaque blit covers the ribbon afterwards.
      * With `bark` set, author the ladder's 2-cell column INSIDE or directly
        beside the great trunk's footprint so the bark backing continues the
        trunk's own silhouette. Standing alone it reads as a narrow second
        tree.
      * `face` mirrors the whole piece (+1 = the ladder hangs on the trunk's
        east flank, -1 = west), so a pair on the same trunk can face outward."""
    h = 16 * cells
    sp = S(32, h, salt)
    if bark is not None:                               # the trunk behind it
        _shaft(sp, bark, 15.5, 0, h - 1, 15.5, 15.5, salt,
               grooves=(0.05, 0.42, 0.95))
    else:                                              # or a plank chute
        for y in range(h):
            r = y % 8
            for x in range(32):
                c = deck[5] if r == 0 else deck[2] if r == 1 else \
                    deck[4] if r == 7 else deck[3]
                sp.set(x, y, c)
        sp.rect(0, 0, 1, h - 1, deck[5]); sp.rect(30, 0, 31, h - 1, deck[5])
    SX0, SX1 = 9, 22                                   # the two stiles
    for i, sx in enumerate((SX0, SX1)):                # hung from the top, so
        _rope(sp, sx, 0, sx, h - 1, phase=i * 2, wide=True)   # the lay differs
    y = 3                                              # THE RUNGS, unevenly
    n = 0                                              # spaced on a hash
    while y < h - 2:
        tilt = 1 if n % 3 == 2 else 0                  # and a third of them
        for k in range(2):                             # hanging a px off level
            yy = y + k
            sp.rect(SX0 - 1, yy, SX1 + 2, yy + tilt, deck[2] if k == 0 else deck[4])
        sp.rect(SX0 - 1, y, SX1 + 2, y, deck[0])       # the rung's lit crown
        sp.set(SX0 - 1, y + 2 + tilt, deck[5]); sp.set(SX1 + 2, y + 2 + tilt, deck[5])
        _rope(sp, SX0, y - 1, SX0, y + 2 + tilt, phase=n)     # lashed on at
        _rope(sp, SX1, y - 1, SX1, y + 2 + tilt, phase=n + 1)  # both ends
        y += 7 + h2(n, 1, salt) % 3
        n += 1
    _crop(sp, 32, h)
    if face < 0:
        for yy in range(h):
            row = sp.px[yy]
            row[0:32] = row[0:32][::-1]
    return sp


# ---- the DINGHY LIFT: the town's signature machine ------------------------------------
# A counterweighted rope hoist with a beached dinghy pressed into service as the
# car. THREE pieces rather than one tall sprite, because the shaft's height is a
# map decision and not an art one: the head gear hangs from a bough at the top,
# the car hangs in the middle, the crank drum stands on the ground at the
# bottom, and a generator lines them up down one 3-cell column with as much
# `tree_trunk` between them as the town needs. One 7-cell sprite would fix the
# shaft height forever and would put the car's sway animation on the drum too.
#
# It is medieval-steampunk to the letter: brass sheaves, hemp falls, shaped
# timber, one cast gear and an iron pawl. No motor, no cable, no chrome.
#
# COVERAGE WARNING for the whole section. `_check_art.py`'s invisible-wall lint
# exempts a SOLID footprint cell only where the prop's frame-0 art covers >= 20%
# of it (`T3_COVER_MIN`), and a hoist is mostly rope and air: the head measures a
# 0.4% floor and the car a 0.0% one. Only `dinghy_lift_drum`'s bottom row (90.2%)
# may be typed solid. Type the head's and the car's cells WALKABLE — which is
# also what they want to be, since both hang overhead.

SHAFT_X = 18        # THE SHAFT CENTRELINE, shared by all three lift pieces. The
                    # head's main block hangs here, the car's fall comes in
                    # here, the drum's fall rises from here. It is deliberately
                    # WEST of a 48px centre so the counterweight has room beside
                    # it: an offset counterweight forces the car's rope in at an
                    # angle, and the first pass crossed the two ropes above the
                    # boat into a bow tie.

SWAY = (0, 1, 1, 0, 0, -1, -1, 0)   # the car's 8-frame swing. Symmetric and
                                    # zero-mean, so it can never read as travel
                                    # (the WIN_PULSE lesson) — and SWAY[0] = 0,
                                    # which is what keeps a still bake identical
                                    # to the art as drawn.


def dinghy_lift_head(deck, bark, stone, salt=451, w=48, h=48):
    """THE HEAD GEAR of the dinghy lift, 48x48 over a 3x3 footprint: a heavy
    BOUGH BEAM seized across the shaft with rope turns, a brass-sheaved pulley
    block hung under it on a strop at `SHAFT_X`, a smaller fairlead outboard, and
    the COUNTERWEIGHT — a rough stone in a rope NET — hanging on the far fall.
    The hauling fall runs off the bottom edge toward the car.

    The counterweight is the whole reason the machine is believable. A hoist with
    one rope is somebody pulling; a hoist with a stone on the other end is a
    machine a librarian can work, which is exactly the register this town wants.
    It is a NETTED boulder rather than a dressed block, and that took a pass to
    learn: a coursed rectangle with rope down its sides read as a filing cabinet
    with trim, while a lumpy stone in a net reads as a weight instantly.

    FOOTPRINT: 3x3 cells, every cell WALKABLE — all of this is overhead gear a
    body walks underneath.
    ANCHOR: Tier-3, one unsplit sprite, bottom-anchored at the footprint's south
    edge: `emit_prop(name, chars, sprite_img(sp, 48, 48))`. Bottom-anchored with
    an all-walkable footprint is already correct — every body in those cells
    sorts north of the baseline, so the gear draws over all of them.
    COVERAGE: measured per-cell floor 0.4% — the outer cells hold nothing but a
    strand of rope. This piece MUST NOT be typed solid (see the note on
    T3_COVER_MIN at the head of the lift section).

    AUTHORING CONSTRAINTS a generator must assert:
      * All three rows WALKABLE — both because the gear is overhead and because
        the coverage floor is under T3_COVER_MIN.
      * The head, the car and the drum share one 3-cell COLUMN, north to south in
        that order, and all three key their rope to `SHAFT_X`. Nothing lints a
        lift whose rope misses its car.
      * Place it against a `tree_canopy` bough or a `tree_trunk` crown so the
        beam is seized to something. Hanging in bare sky it reads as a mistake."""
    sp = S(w, h, salt)
    FA, FB = SHAFT_X, w - 12                           # main block, fairlead
    # the bough beam: a bark log across the shaft, with rope turns ACROSS it
    sp.capsule(0, 7, w - 1, 6, 6.4, 5.8, bark, sh=0.02)
    for lx in (FA - 4, FB - 4):
        _lash(sp, 1, 12, lx)
    sp.rect(2, 13, w - 3, 13, bark[5])                 # its underside shadow
    # the main block on a strop, and the fairlead outboard of it
    _rope(sp, FA, 13, FA, 15, wide=True)
    _pulley(sp, deck, FA, 25, r=5)
    _rope(sp, FB, 13, FB, 15, wide=True)
    _pulley(sp, deck, FB, 23, r=3)
    # the hauling fall, leaving the canvas toward the car
    _rope(sp, FA, 31, FA, h - 1, phase=1, wide=True)
    # THE COUNTERWEIGHT: a rough stone in a rope net on the far fall
    _rope(sp, FB, 27, FB, 32, phase=2, wide=True)
    scx, scy = FB, 39
    sp.ball(scx, scy, 7.4, 6.4, stone, power=2.6, sh=0.04)
    sp.blob(scx - 2.4, scy - 2.6, 2.4, 1.6, stone[0])  # a flat chipped facet
    sp.blob(scx + 2.6, scy + 2.2, 2.6, 1.8, stone[5])
    for nx in (scx - 4, scx, scx + 4):                 # the net over it
        _rope(sp, nx, scy - 6, nx, scy + 6, phase=nx % 3)
    for ny in (scy - 3, scy + 3):
        _rope(sp, scx - 6, ny, scx + 6, ny, phase=ny % 3)
    sp.rect(scx - 1, scy - 9, scx + 1, scy - 8, IRON[2])       # its becket ring
    sp.set(scx, scy - 9, BRASS[1])
    edge(sp, h)
    clipw(sp, w)
    return sp


def _draw_car(sp, deck, ox, w, h):
    """The dinghy itself, drawn at a sway offset `ox` — a clinker-built open
    boat seen BROADSIDE (bow west, stern east), because a boat read left-to-
    right is instantly a boat and a boat read end-on is a lozenge.

    Every frame redraws it from scratch at its own offset rather than blitting a
    copy, so the falls above it can TILT to meet the shifted hanger instead of
    sliding sideways with it — a rope that translates reads as the whole world
    moving, a rope that tilts reads as a boat swinging under it."""
    cx = SHAFT_X + 4 + ox
    x0, x1 = cx - 17, cx + 17
    TOP, BOT = 20, 36                                  # the sheer and the keel
    for x in range(x0, x1 + 1):
        u = (x - x0) / float(x1 - x0)
        e = abs(u - 0.5) * 2.0                         # 0 amidships, 1 at ends
        # A POINTED BOW west and a FLAT TRANSOM east. Two symmetric rounded ends
        # read as a washtub; the asymmetry is what makes it a boat, and it also
        # says which way the thing is facing.
        if u < 0.5:
            sheer = TOP + int(round(-5.0 * e ** 1.6))
            keel = BOT + int(round(-7.0 * e ** 2.2))
        else:
            sheer = TOP + int(round(-3.0 * e * e))
            keel = BOT + int(round(-3.0 * e * e))
        if keel < sheer:
            continue
        for y in range(sheer, keel + 1):
            v = (y - sheer) / float(max(1, keel - sheer))
            if v < 0.16:
                c = deck[0]                            # the gunwale, lit
            elif v < 0.30:
                c = deck[1]                            # the rubbing strake
            elif v > 0.86:
                c = deck[5]                            # the garboard, in shade
            elif v > 0.66:
                c = deck[4]
            else:
                c = deck[2] if v < 0.50 else deck[3]
            sp.set(x, y, c)
        for lap in (0.42, 0.66):                       # clinker plank laps
            sp.set(x, sheer + int(round(lap * (keel - sheer))), deck[4])
    sp.rect(cx - 12, TOP + 1, cx + 14, TOP + 4, deck[5])       # the open bilge,
    sp.rect(cx - 10, TOP + 1, cx + 12, TOP + 1, deck[4])       # seen from above
    # The thwarts sit AT the gunwale line, not above it. Standing them two px
    # proud made two pale posts that read as bollards on a quay.
    for tx in (cx - 7, cx + 5):
        sp.rect(tx, TOP + 1, tx + 2, TOP + 4, deck[2])
        sp.rect(tx, TOP + 1, tx + 2, TOP + 1, deck[0])
        sp.set(tx + 2, TOP + 4, deck[5])
    sp.rect(cx + 9, TOP + 1, cx + 13, TOP + 4, deck[3])        # a lashed crate
    sp.rect(cx + 9, TOP + 1, cx + 13, TOP + 1, deck[1])
    sp.rect(cx + 13, TOP + 1, cx + 13, TOP + 4, deck[5])
    _rope(sp, cx + 9, TOP + 3, cx + 13, TOP + 3, phase=1)
    for k in range(3):                                         # a coil of rope
        _rope(sp, cx - 12 + k, TOP + 2 + k, cx - 8 + k, TOP + 2 + k, phase=k)
    # THE CRADLE. Bow and stern slings rising to ONE becket ring on the
    # centreline — a Y, and only a Y. The first pass also ran two falls down into
    # the ring from two different sheaves, and the four lines crossing made a
    # bow tie stamped over the boat. One rope in, two out.
    ring = (cx - 1, 10)
    _rope(sp, x0 + 5, TOP - 1, ring[0] - 1, ring[1] + 2, phase=0, wide=True)
    _rope(sp, x1 - 4, TOP - 1, ring[0] + 2, ring[1] + 2, phase=2, wide=True)
    sp.rect(ring[0] - 3, ring[1], ring[0] + 3, ring[1] + 2, IRON[3])   # the ring,
    sp.rect(ring[0] - 2, ring[1], ring[0] + 2, ring[1] + 1, IRON[2])   # big enough
    sp.rect(ring[0] - 1, ring[1], ring[0] + 1, ring[1], BRASS[1])      # to see
    sp.set(ring[0], ring[1] + 1, IRON[1])
    # the lantern on an iron hook at the bow — WARM/WARMD so _breathe can step
    # it up its own ladder, and the only warm thing in the shaft
    lx, ly = x0 + 3, TOP - 9
    sp.rect(lx, ly - 2, lx + 1, ly - 1, IRON[2])               # the hook
    sp.rect(lx - 2, ly, lx + 3, ly, BRASS[1])                  # the hood
    sp.set(lx - 2, ly, IRON[2]); sp.set(lx + 3, ly, IRON[2])
    sp.rect(lx - 1, ly + 1, lx + 2, ly + 5, WARMD)             # its flame
    sp.rect(lx, ly + 2, lx + 1, ly + 4, WARM)
    sp.rect(lx - 2, ly + 6, lx + 3, ly + 6, IRON[2])           # the pan
    return (lx - 1, ly + 1, 4, 5), ring


def dinghy_lift_car(deck, salt=453, composite=True, frames=8, w=48, h=48):
    """THE LIFT CAR — a beached DINGHY slung in a rope cradle, 48x48 over a 3x3
    footprint, as an EIGHT-FRAME animated sheet: the car swings a pixel either
    way on `SWAY`, the two falls above it TILT to follow the swing, and the
    lantern at the bow breathes on `WIN_PULSE`. Frame 0 is the art as drawn, so
    a still bake is byte-identical to the un-animated build.

    Eight frames, not four, and for the same reason `town_cabin` has eight:
    `WIN_PULSE` spans the whole sheet, so the lantern breathes once per ~1.4s
    (travel_scene's ANIM_STEP is 0.18s) instead of guttering. `SWAY` is period-8
    and symmetric, so the swing has no direction and can never read as the car
    travelling sideways.

    RETURNS: with the defaults, a horizontal frame-sheet `Img` of `w*frames` x
    `h` for `emit_prop(name, chars, sheet, hframes=8)`. With `frames == 1` the
    single Sprite (still bake).

    FOOTPRINT: 3x3 cells, every cell WALKABLE — the car hangs in the air; you
    walk under it.
    ANCHOR: Tier-3, bottom-anchored at the footprint's south edge. No `top=`,
    no `base_inset=`.
    COVERAGE: measured per-cell floor 0.0% — the boat occupies the middle band
    and leaves the footprint's top row empty sky. MUST NOT be typed solid.

    AUTHORING CONSTRAINTS a generator must assert:
      * `hframes` in the manifest MUST equal `frames`. A mismatch shows as a
        boat sliced into vertical ribbons.
      * `frames % len(SWAY) == 0` and `frames % len(WIN_PULSE) == 0` (asserted
        below): a partial cycle of either makes the sheet jump on the loop.
      * WALKABLE cells, always — both because the car is neither floor nor
        obstacle and because the coverage floor is 0%.
      * The car's column must match the head's and the drum's: all three key
        their rope to `SHAFT_X`, and nothing lints a rope that misses."""
    assert frames < 2 or (frames % len(SWAY) == 0
                          and frames % len(WIN_PULSE) == 0), \
        "an animated lift-car sheet must hold whole sway and breath cycles"
    if frames < 2:
        sp = S(w, h, salt)
        _car_frame(sp, deck, w, h, 0)
        return sp
    sheet = Img(w * frames, h)
    for f in range(frames):
        frm = S(w, h, salt)
        _car_frame(frm, deck, w, h, f)
        sheet.blit_cell(frm, f * w, 0)
    return sheet


def _car_frame(sp, deck, w, h, f):
    """One frame of the lift car: the falls from the sheave overhead, the boat
    at its sway offset, the lantern stepped up its breath ladder."""
    ox = SWAY[f % len(SWAY)]
    lamp, ring = _draw_car(sp, deck, ox, w, h)
    # ONE hauling fall, from the head's main block on the shaft centreline down
    # to the ring. It TILTS with the sway instead of sliding — a rope that
    # translates reads as the whole world moving.
    _rope(sp, SHAFT_X, 0, ring[0], ring[1] - 1, phase=f % 3, wide=True)
    edge(sp, h)
    clipw(sp, w)
    lvl = WIN_PULSE[f % len(WIN_PULSE)]
    if lvl:
        _breathe(sp, lamp[0], lamp[1], lamp[2], lamp[3], lvl)


def dinghy_lift_drum(deck, stone, salt=455, w=48, h=32):
    """THE CRANK DRUM at the foot of the shaft, 48x32 over a 3x2 footprint: a
    timber cradle on a bedded stone footing, a rope drum with the hauling fall
    coiled on it, a cast BRASS GEAR on the near end with an IRON PAWL dropped
    into its teeth, and a cranked handle. The pawl is the piece that makes the
    machine safe to leave loaded, and it is also the piece that makes it read as
    a machine rather than as a barrel: a ratchet is a decision somebody made.

    FOOTPRINT: 3x2 cells. The BOTTOM row is SOLID (you bump into the works), the
    TOP row is WALKABLE — the `town_gatepost` / conifer case-split idiom, so the
    drum pinches the landing without walling it off.
    ANCHOR: Tier-3, one unsplit sprite, bottom-anchored at the footprint's south
    edge.
    COVERAGE: measured floor 90.2% on the SOLID row (the stone footing spans the
    full width) and 34.8% on the walkable row — the solid row clears
    `T3_COVER_MIN` = 0.20 four times over, and this is the only lift piece that
    may be typed solid at all.

    AUTHORING CONSTRAINTS a generator must assert:
      * The case-split: exactly the bottom row solid, per connected component.
        All-solid makes the landing a dead end; all-walkable lets you stand
        inside the drum.
      * Same 3-cell column as the head and the car, southmost of the three.
      * A walkable cell east or west of the drum's solid row, so a body can
        reach the crank; the lift is the only reason this landing exists."""
    sp = S(w, h, salt)
    # the bedded stone footing the frame stands on
    sp.rect(1, h - 6, w - 2, h - 1, stone[2])
    sp.rect(1, h - 6, w - 2, h - 6, stone[0])
    sp.rect(1, h - 1, w - 2, h - 1, stone[5])
    for jx in range(4, w - 4, 9):
        sp.rect(jx, h - 5, jx, h - 2, stone[4])
    # the timber cradle: two posts, a cross brace
    for px_ in (4, w - 10):
        sp.rect(px_, 9, px_ + 5, h - 6, deck[3])
        sp.rect(px_, 9, px_, h - 6, deck[1])
        sp.rect(px_ + 5, 9, px_ + 5, h - 6, deck[5])
        sp.rect(px_, 9, px_ + 5, 9, deck[0])
    ln(sp, 9, h - 8, w - 11, 13, deck[4])                      # the brace
    ln(sp, 9, h - 9, w - 11, 12, deck[2])
    # THE DRUM, with the hauling fall coiled the WHOLE way along it. The coils are
    # laid rope on a 3px pitch, which at this scale is what tells a drum from a
    # barrel — and leaving bare timber between two coil bands (the first pass) is
    # what made it read as a plain log with two straps on it.
    dx0, dx1 = 11, w - 12
    sp.rect(dx0, 12, dx1, 23, deck[2])
    sp.rect(dx0, 12, dx1, 12, deck[0])
    sp.rect(dx0, 23, dx1, 23, deck[5])
    for cx_ in range(dx0, dx1 + 1):
        k = (cx_ - dx0) % 3
        for i, ry in enumerate(range(13, 23, 2)):
            # CYLINDRICAL shading down the coil: the top turns catch the light,
            # the bottom ones are in shade. Coiled at one flat brightness the drum
            # read as a rolled mat lying in a bed frame.
            band = 0 if i < 2 else 1 if i < 4 else 2
            sp.set(cx_, ry, ROPE[min(3, band + (k + i) % 2)])
            sp.set(cx_, ry + 1, ROPE[min(3, band + 1 + (k + i) % 2)])
    sp.rect(dx0, 22, dx1, 22, ROPE[3])                         # the coil's foot
    for fx in (dx0, dx1):                                      # the end FLANGES,
        sp.rect(fx - 1, 11, fx + 1, 24, deck[3])               # so it reads round
        sp.rect(fx - 1, 11, fx + 1, 12, deck[0])
        sp.rect(fx - 1, 23, fx + 1, 24, deck[5])
        sp.set(fx, 11, deck[1]); sp.set(fx, 24, deck[5])
    _rope(sp, SHAFT_X, 0, SHAFT_X, 13, phase=1, wide=True)     # the fall, rising
    sp.rect(dx0 - 1, 12, dx0 - 1, 23, deck[4])                 # drum cheeks
    sp.rect(dx1 + 1, 12, dx1 + 1, 23, deck[4])
    # THE BRASS GEAR + THE IRON PAWL. Brass is tones 0/1 ONLY — ball()ing the
    # 4-tone BRASS ramp put its violet-law reds into the disc and the gear came
    # out a red-and-yellow bullseye. Two flat brass discs and an iron hub
    # instead, which is also the flatter, more deliberate read.
    gx, gy = 8, 17
    sp.blob(gx, gy, 5.6, 5.4, BRASS[1])
    sp.blob(gx - 0.6, gy - 0.6, 3.8, 3.6, BRASS[0])
    sp.blob(gx, gy, 1.5, 1.4, IRON[2])                         # a ROUND hub — at
    sp.set(gx, gy, IRON[1])                                    # r=1.9 the blob
    for i, (tx, ty) in enumerate(((0, -7), (5, -5), (7, 0), (5, 5),   # squared off
                                  (0, 7), (-5, 5), (-7, 0), (-5, -5))):
        sp.set(gx + tx, gy + ty, BRASS[1] if tx + ty > 0 else BRASS[0])
        sp.set(gx + tx, gy + ty + 1, IRON[3])                  # the tooth's
    sp.set(gx - 3, gy - 3, SPEC)                               # own shadow
    # THE PAWL, angled DOWN INTO a tooth from a pivot above, with its nose
    # clearly in the gear and a little weight on the tail. A straight vertical
    # bar with a kink read as an antenna.
    sp.rect(gx + 2, gy - 12, gx + 3, gy - 11, IRON[2])         # its pivot
    ln(sp, gx + 2, gy - 11, gx - 1, gy - 6, IRON[3])
    ln(sp, gx + 3, gy - 11, gx, gy - 6, IRON[2])
    sp.set(gx - 1, gy - 6, IRON[1]); sp.set(gx, gy - 6, IRON[1])   # the nose
    sp.set(gx + 4, gy - 13, IRON[3]); sp.set(gx + 5, gy - 12, IRON[3])
    # THE CRANK on the far end: a boss on the axle, an iron THROW out and down,
    # and a turned wooden grip across it. Drawn as a single diagonal it read as a
    # post leaning on the frame — a crank needs the elbow AND the grip crossing
    # it at right angles, or it is just a stick.
    hx = w - 8
    sp.blob(hx, 17, 3.0, 3.0, IRON[3])
    sp.blob(hx - 0.4, 16.6, 1.8, 1.8, IRON[2])
    sp.set(hx - 1, 16, BRASS[1])
    ln(sp, hx, 18, hx + 3, 25, IRON[3])                        # the throw
    ln(sp, hx + 1, 18, hx + 4, 25, IRON[2])
    sp.rect(hx, 25, hx + 6, 27, deck[2])                       # the grip, across
    sp.rect(hx, 25, hx + 6, 25, deck[0])
    sp.rect(hx, 27, hx + 6, 27, deck[5])
    sp.set(hx + 6, 26, deck[4])
    edge(sp, h)
    clipw(sp, w)
    return sp

# ---- 6. THE BOUGH ---------------------------------------------------------------------

def tree_canopy(f, bark, salt=451, w=48, h=48, cut=None, face=1):
    """A walk-behind BOUGH — a branch sweeping in from one side under a mass of
    leaves, for dressing a canopy's open edges and for hiding the underside of
    a deck the map runs past.

    Returns the `(lower, upper)` PAIR, the `town_conifer` split idiom: the leaf
    mass above `cut` rides its own y-sorted sprite that draws OVER a body in
    those cells (walk-behind), while the bough's underside and its cast leaf
    shadow bake below one, so a body south of the mass passes in front of it.

    FOOTPRINT: `w // 16` x `h // 16` cells (3x3 at the defaults), every cell
    WALKABLE — a bough is something you walk under, not into.
    ANCHOR: BOTH halves are Tier-3, emitted on the SAME chars:
        emit_prop("BoughBranch", chars, sprite_img(lo, w, h), each=True)
        emit_prop("BoughLeaves", chars, sprite_img(up, w, h), each=True,
                  top=0, base_inset=-16)
    The `top=0, base_inset=-16` on the upper half is what pushes the leaf
    mass's y-sort baseline south of the footprint so it beats a body standing
    inside it. Emitting only the upper half puts a body in front of the leaves;
    emitting only the lower half loses the walk-behind entirely.

    AUTHORING CONSTRAINTS a generator must assert:
      * `each=True` requires IDENTICAL components — assert every component is a
        clean `w//16` x `h//16` block. Two boughs authored edge-to-edge fuse
        into one component and one stretched sprite (the spruce lesson), and
        nothing else complains.
      * All footprint cells walkable, so no T3 coverage rule applies and the
        thin lower half can't trip the invisible-wall lint.
      * `face` is which side the branch enters from, +1 west / -1 east. Mirror
        the pair along a canopy edge so the boughs reach INWARD; a row of
        identically-facing boughs reads as wallpaper.
    COVERAGE: measured floor 0.0% on BOTH halves — the mass is round, so the
    footprint's corner cells are empty, and the split then halves what is left.
    A bough footprint MUST be walkable; typed solid it is a textbook invisible
    wall and the lint will say so."""
    cut = h * 2 // 3 if cut is None else cut
    sp = S(w, h, salt)
    # THE BRANCH, thick and clearly visible, entering low from one side and
    # rising into the mass. The first pass hid it behind the leaves and the piece
    # read as a bush hovering over a dark puddle: without a limb going somewhere
    # a leaf mass is scenery, and this needs to be a BOUGH.
    bx0 = 0 if face > 0 else w - 1
    bx1 = w * 0.58 if face > 0 else w * 0.42
    sp.capsule(bx0, h - 9, bx1, h * 0.42, 4.6, 2.6, bark, end_sh=0.14)
    for i in range(4):                                 # bark bands along it
        t = 0.22 + 0.20 * i
        sp.set(int(bx0 + (bx1 - bx0) * t), int(h - 9 + (h * 0.42 - h + 9) * t),
               bark[4])
    # THE LEAF MASS spans nearly the whole canvas, so the split at `cut` leaves
    # the bottom lobes on the LOWER sprite. Keeping every leaf above the cut was
    # the other half of the same bug — the lower half came out an empty dark
    # sliver with nothing in it to sort behind a body.
    r = max(8.0, w * 0.215)
    _leaf_mass(sp, f, [
        (w * 0.24, r + 1.0, r, 1.00, 0.02),
        (w * 0.58, r - 2.0, r * 1.04, 1.00, -0.06),
        (w * 0.40, r * 2.10, r * 1.06, 0.94, 0.08),
        (w * 0.78, r * 1.80, r * 0.90, 0.96, 0.14),
        (w * 0.60, r * 3.05, r * 0.86, 0.86, 0.20),    # the hanging lower lobe
    ])
    _leaf_dabs(sp, f, 3, 3, w - 4, int(h * 0.72), salt, n=max(10, w // 4))
    sp.blob(w * 0.20, r * 0.40, r * 0.36, r * 0.22, f[0])   # NW sun-catch
    sp.set(int(w * 0.16), int(r * 0.28), SPEC)
    sp.despeckle(2, 1)
    edge(sp, h)
    clipw(sp, w)
    return split_rows(sp, cut)


# ---- 7. THE UNDERSTORY ---------------------------------------------------------------

_UNDERSTORY = ("roots", "fern", "shroom", "log", "drift", "sapling")


def _duff(sp, ground, w, salt):
    """The forest-floor base every understory prop carries: a 3-tone flecked
    fill from the `ground` ramp, exactly `town_tree`'s opaque trunk-row recipe.
    Opaque so the prop dedupes whatever the fabric phase beneath it is doing —
    which is only true if the ramp handed in is the SAME one the terrain
    painter uses for the understory floor. Hand it a different green and the
    prop reads as a square patch."""
    for y in range(16):
        for x in range(w):
            r = h2(x, y, salt + 5) % 11
            sp.set(x, y, ground[1] if r == 0 else
                         ground[3] if r == 1 else ground[2])


def understory(f, wood, ground, kind="roots", salt=461, cells=1):
    """THE GROUND STRATUM'S DRESSING — the shaded floor far below the canopy, as
    small per-cell props. `kind` is one of:

      "roots"  16x16 — three root humps arcing out of the duff, mossed on their
                       lit crowns. The cheapest thing that says "a great trunk
                       stands nearby".
      "fern"   16x16 — a clump of five fronds with pinnae, on its own shadow.
      "shroom" 16x16 — a cluster of bone-ivory caps with violet gills. The
                       understory's ONE pale accent; keep it rare.
      "log"    `16*cells` x 16 — a fallen log with end-grain rings, bark bands,
                       moss along its lit crown and two shelf fungi.
      "drift"  16x16 — a drift of fallen leaves, and THE MOST IMPORTANT ONE.
                       A clearing floor drawn entirely from the grass ramp reads
                       as a LAWN no matter how many ferns are standing on it,
                       because every piece of dressing is the same green as the
                       thing it is dressing. Warm curled leaves in the `wood`
                       ramp are the only cheap thing that breaks the field's hue,
                       so this is the common case and everything else is a
                       feature standing in it.
      "sapling" 16x16 — a knee-high young tree: one leaning stem, four leaves,
                       a lit tip. Vertical interest with almost no silhouette,
                       for the middle distance where a fern clump reads as a
                       blob and a log is too big an event.

    FULLY OPAQUE and UN-OUTLINED per the tile-reusability rule: each prop
    carries its own duff base (see `_duff`) so its cells dedupe regardless of
    the fabric phase under them, and no silhouette outline prints a hard edge
    around a piece of ground.

    FOOTPRINT: `cells` x 1 cells (`cells` is 1 for everything but the log).
    ANCHOR: Tier-1 baked, `place_each(chars, ...)` at each component's
    top-left. One char per kind, and `place_each` rather than `place` — several
    fern clumps share a char, and `place()` would blit one across the whole
    map's bbox.

    AUTHORING CONSTRAINTS a generator must assert:
      * `kind` in the table and `cells == 1` unless `kind == "log"` (both
        asserted below).
      * `ground` must be the SAME ramp the terrain painter uses for the
        understory floor class, or the opaque base reads as a patch.
      * Cells may be walkable or solid: the duff base fills 100% of every cell,
        so the T3 20%-coverage rule and the invisible-wall lint are satisfied
        either way. Prefer WALKABLE for ferns and mushrooms (you can wade
        through them) and SOLID for a log and root humps (you cannot)."""
    assert kind in _UNDERSTORY, f"unknown understory kind {kind!r}"
    assert cells == 1 or kind == "log", \
        f"{kind!r} is a one-cell prop; only a fallen log runs several"
    w = 16 * cells
    sp = S(w, 16, salt)
    _duff(sp, ground, w, salt)
    if kind == "roots":
        # THREE humps, drawn as flat arcs rather than as capsules. Capsules at
        # this size came out as one diagonal stick: a root breaking the surface
        # is WIDE and LOW, and it needs a dark seam where it re-enters the duff
        # or it reads as a branch someone dropped.
        # Three humps RADIATING from off the north-west corner, not arching
        # symmetrically across the cell — a symmetric arch read as a croissant.
        # Roots come from somewhere.
        for (ax, ay, bx, by, arc, thick, k) in ((0, 3, 15, 8, 1.6, 3, 1),
                                                (0, 8, 13, 15, 1.2, 3, 2),
                                                (2, 1, 9, 15, 1.0, 2, 0)):
            steps = max(abs(bx - ax), abs(by - ay), 1)
            for s in range(steps + 1):
                t = s / steps
                x = int(round(ax + (bx - ax) * t))
                y = int(round(ay + (by - ay) * t - arc * 4 * t * (1 - t)))
                sp.rect(x, y, x, y + thick, wood[k + 1])
                sp.set(x, y, wood[k])                  # the lit crown
                sp.set(x, y + thick, wood[5])          # its seam in the duff
        for mx, my in ((4, 5), (11, 11), (7, 9)):      # moss on the crowns
            if sp.get(mx, my) is not None:
                sp.set(mx, my, f[2]); sp.set(mx + 1, my + 1, f[4])
    elif kind == "fern":
        # The fronds are 2px wide with a dark spine, not 1px lines. A 1px frond
        # in the leaf ramp over a green floor has nothing to read against; the
        # silhouette has to be thick enough to hold two values.
        sp.blob(8, 15, 5.0, 1.6, ground[5])            # the crown's shadow
        for i, (tx, ty) in enumerate(((0, 6), (3, 1), (8, 0), (13, 2), (15, 8))):
            steps = max(abs(tx - 8), abs(ty - 14), 1)
            for s in range(steps + 1):
                t = s / steps
                x = int(round(8 + (tx - 8) * t))
                y = int(round(14 + (ty - 14) * t))
                sp.set(x, y, f[1] if t > 0.55 else f[2])
                sp.set(x + 1, y, f[4])
                if s % 2 == 0 and t > 0.2:             # the pinnae
                    sp.set(x - 1, y, f[2] if i % 2 else f[1])
                    sp.set(x + 2, y + 1, f[5])
            sp.set(tx, ty, f[0])                       # the tip, catching light
        sp.rect(7, 13, 9, 14, f[5])                    # the clump's own base
    elif kind == "shroom":
        # Three caps of clearly different SIZE, each with a stem below it and a
        # hard dark gill line under the cap. Three similar pale domes touching
        # merged into one splash of white with no mushroom in it anywhere; the
        # gill line is what separates a cap from its own stem, and the size
        # difference is what separates the caps from each other.
        sp.blob(8, 14, 5.4, 1.6, ground[5])            # the cluster's shadow
        for cx_, cy_, rx_, ry_ in ((8.5, 6.0, 3.4, 2.2), (4.0, 10.0, 2.6, 1.8),
                                   (12.5, 11.0, 2.0, 1.4)):
            ix, iy = int(cx_), int(cy_)
            sp.rect(ix, iy + 1, ix, iy + int(ry_ * 2.6), SHROOM[1])
            sp.rect(ix + 1, iy + 1, ix + 1, iy + int(ry_ * 2.6), SHROOM[2])
            sp.set(ix, iy + int(ry_ * 2.6), SHROOM[3])
            # The cap in THREE HARD BANDS, not a ball(). ball() spent the ramp's
            # near-white on the whole upper dome and three pale domes touching
            # merged into one splash of white with no mushroom in it.
            for dy in range(-int(ry_) - 1, int(ry_) + 1):
                for dx in range(-int(rx_) - 1, int(rx_) + 2):
                    q = (dx / rx_) ** 2 + (dy / ry_) ** 2
                    if q > 1.0:
                        continue
                    sp.set(ix + dx, iy + dy,
                           SHROOM[0] if (dx < 0 and dy < 0 and q < 0.5)
                           else SHROOM[1] if dy <= 0 else SHROOM[2])
            sp.rect(int(cx_ - rx_ * 0.86), iy + int(ry_),
                    int(cx_ + rx_ * 0.86), iy + int(ry_), SHROOM[3])  # the gills
    elif kind == "drift":
        # NO SILHOUETTE AT ALL — this one is pure hue, and the shape of the mark
        # is the whole job. The first pass drew each leaf as a 4px sloping LINE
        # with a stem, and a floor of those reads as a scatter of dead TWIGS: a
        # line has a direction and no area, so thirteen of them per cell come out
        # as bracken, or as damage. A leaf lying face up is a small SOLID patch
        # with a lit edge on one side and its own shadow on the other, three or
        # four pixels across, and eight of those per cell is a drift.
        for i in range(8):
            lx = 2 + h2(i, 0, salt + 11) % 11
            ly = 2 + h2(i, 1, salt + 13) % 11
            k = (1, 2, 0, 3)[h2(i, 2, salt + 17) % 4]   # which warm tone
            if h2(i, 3, salt + 19) % 2:                 # lying across
                sp.rect(lx, ly, lx + 2, ly, wood[k])
                sp.rect(lx, ly + 1, lx + 2, ly + 1, wood[min(k + 2, 5)])
                sp.set(lx, ly, wood[max(k - 1, 0)])
                sp.set(lx + 3, ly + 1, wood[5])         # the stalk
            else:                                       # or end-on
                sp.rect(lx, ly, lx + 1, ly + 2, wood[k])
                sp.set(lx, ly, wood[max(k - 1, 0)])
                sp.set(lx + 1, ly + 2, wood[min(k + 2, 5)])
                sp.set(lx, ly + 3, wood[5])
        for i in range(2):     # a couple still green, so it fell from THESE trees
            gx = 2 + h2(i, 4, salt + 23) % 11
            gy = 3 + h2(i, 5, salt + 29) % 10
            sp.rect(gx, gy, gx + 2, gy, f[2])
            sp.rect(gx, gy + 1, gx + 2, gy + 1, f[4])
    elif kind == "sapling":
        # ONE stem with a LEAN, and the leaves have to be BROAD. Drawn as 1px
        # sloping runs the whole plant came out as another brown twig standing in
        # a field of brown twigs — at 16px a leaf needs two rows to be a leaf, and
        # the stem needs to be shorter than instinct says or the thing reads as a
        # sapling nobody would call knee-high.
        sp.blob(8, 14, 3.6, 1.3, ground[5])            # what it stands in
        for s in range(8):
            t = s / 7.0
            x = 8 - int(round(t * 2))
            y = 14 - s
            sp.set(x, y, wood[3] if t < 0.4 else wood[2])
            sp.set(x + 1, y, wood[5])
        for lx, ly, ll in ((5, 7, 4), (9, 9, 3), (5, 10, 3), (8, 5, 3)):
            dr = 1 if lx < 7 else -1
            for s in range(ll):
                x = lx + dr * s
                sp.set(x, ly - s, f[1] if s else f[2])
                sp.set(x, ly - s + 1, f[2] if s else f[4])
                sp.set(x, ly - s + 2, f[4])
        sp.rect(6, 3, 7, 4, f[1])                      # the growing tip
        sp.set(6, 2, f[0])
    else:                                              # a fallen log
        sp.blob(1, 12, w - 2, 2.2, ground[4])          # the shadow it lies in
        sp.capsule(1, 8, w - 2, 9, 4.4, 3.9, wood, sh=0.02, end_sh=0.08)
        for bx in range(3, w - 3, 6):                  # bark bands along it
            sp.rect(bx, 5, bx, 12, wood[3])
            sp.set(bx + 1, 11, wood[5])
        sp.blob(2, 8, 1.9, 3.7, wood[3])               # end grain, near end
        sp.blob(2, 8, 1.0, 1.9, wood[5])
        sp.blob(w - 3, 9, 1.7, 3.3, wood[4])           # and far
        for mx in range(4, w - 4, 5):                  # moss on the lit crown
            sp.set(mx, 5, f[2]); sp.set(mx + 1, 5, f[1]); sp.set(mx, 6, f[4])
        for sx, sy in ((6, 7), (w - 8, 8)):            # two shelf fungi
            sp.blob(sx, sy, 2.4, 1.1, SHROOM[1])
            sp.blob(sx, sy + 1, 2.0, 0.7, SHROOM[3])
    _crop(sp, w, 16)
    return sp
