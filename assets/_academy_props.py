#!/usr/bin/env python3
"""THE ALEMBIC ACADEMY's own prop kit — the pieces the precinct needs and no town
does: the timber KEEP whose corner towers are two great trees, the crenellated
RAMPART that walls it off, the DRUM TOWERS of its gatehouse, the great ORRERY in
the inner court, the two WINGS (observatory and still-house), and the weeds
coming up through the court's paving.

Everything else is reused rather than reinvented, which is the tile-reusability
rule doing its job: the TERRACE the keep stands on is `town_cliff(wall=True)` —
the cast-cement retaining wall built for Lanternwood — pierced by `town_stairs`;
the lamps are `town_lamp`, the small trees `town_tree`, the beck's bridge the
OverWorld driver's own `bridge` class; the keep's trunks and crowns are the same
`great_trunk` / `great_crown` armature Alembic's four canopy trees are built on.

TWO MATERIAL DECISIONS, and the second one is a correction.

  1. A PRECINCT IS MASONRY where the town is plaster and timber, so the wall, the
     towers, the wings and the orrery all draw in the scene's ROCK ramp. None of
     that is hand-pinned, because `ramp()`'s violet shadow law is exactly right
     for cold stone.
  2. ...AND EVERYTHING WARM ON TOP OF IT HAD TO BE. The same law takes a warm seed
     straight to red: `BRASS[2..3]` are (246,28,26) and (216,0,109), and
     `COPPER[3..5]` are (174,43,57), (150,31,77), (126,22,89). Drawn down those
     ramps the observatory's dome shipped as a TAN AND RED MUSHROOM, the
     still-house's boiler as a wine barrel, the orrery's sun as a red bead and its
     founder's plate as a magenta bar. Not one of those was a drawing mistake.
     Hence OAK / SHAKE / DAUB for the keep and VERDI / COPPERD here, all
     hand-pinned — the BRASSD and SACKR precedent, five more times.

Stdlib-only, deterministic. Consumed by assets/_gen_tileset_academy.py:
emit_prop for the keep and the wings, stamp_columns for the rampart, place_each
for the towers, and a blit pass for the court weeds.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _propkit import S, ln, edge, split_rows
from _tilekit import BRASS, BRASSD, COPPER, IRON, SPEC, GLASS, MINT, VIOLETF
from _overworld_props import CRYSTAL, DOORDARK, WARM, WARMD
from _town_props import (_anim_building, _finish, _chimney, _coursed_wall,
                         _ph, _pv, _valve, clipw, _leaf_dab, _vine)
from _tree_props import great_trunk, great_crown


# ---- THE KEEP'S OWN MATERIALS, ALL THREE HAND-PINNED ---------------------------------
# `ramp()`'s violet shadow law is exactly right for cold stone and exactly wrong
# for a building made of wood. TIMBER's own darks are (115,40,44) / (92,28,50) /
# (68,18,49) — brick-red, plum, plum — so a hall framed in TIMBER is a RED hall,
# which is the same failure the litter ramp below was hand-pinned to dodge and
# the same one BRASSD and SACKR exist for. Three materials, and the whole
# building's read is the contrast between them: a DARK frame, a PALE panel, a
# DARKER roof.
# ...and they are LISTS, not tuples, because Sprite.tri decides "ramp or flat
# colour" with `isinstance(x, list)` — hand a tri a tuple-of-tuples and it stores
# the whole ramp as one pixel, which blows up in the PNG writer several hundred
# lines away from the mistake.
OAK = [(186, 150, 108, 255), (158, 120, 84, 255), (128, 93, 68, 255),
       (98, 69, 60, 255), (68, 48, 54, 255), (43, 30, 44, 255)]
# weathered cedar shakes — warm grey-brown falling into violet, and deliberately
# darker than BOTH the daub and the pale stone, so at 384x216 the roof is the
# building's MASS and the wall is the thing cut into it
SHAKE = [(146, 126, 112, 255), (122, 101, 96, 255), (99, 80, 84, 255),
         (77, 60, 72, 255), (56, 43, 58, 255), (36, 27, 42, 255)]
# limewashed daub in the frame's panels: the one pale field on the whole keep
DAUB = [(240, 231, 212, 255), (224, 210, 192, 255), (202, 186, 180, 255),
        (174, 156, 162, 255), (142, 122, 140, 255), (108, 88, 114, 255)]
# ...and two more for the WINGS, for the same reason and against the same law.
# COPPER is `ramp((198,112,72), "violet", 6)` and its tones 3-5 come out
# (174,43,57) / (150,31,77) / (126,22,89) — literally red, magenta, magenta. The
# observatory's dome was drawn straight down that ramp and shipped as a TAN AND
# RED MUSHROOM; the still-house's boiler as a wine barrel. Neither was a drawing
# mistake. It is the documented violet shadow law doing exactly what it does to a
# warm seed, which is why BRASSD and SACKR exist.
#  - VERDI is the honest answer for the dome: copper left out in the weather for
#    two hundred years IS green, so the fix and the fiction are the same fix.
#  - COPPERD keeps the still's boiler a hot metal by holding the hue brown into
#    the darks instead of letting it swing to magenta.
VERDI = [(172, 228, 208, 255), (124, 198, 178, 255), (86, 166, 152, 255),
         (58, 128, 124, 255), (40, 92, 98, 255), (26, 60, 74, 255)]
COPPERD = [(238, 198, 160, 255), (212, 162, 118, 255), (180, 126, 88, 255),
           (142, 94, 70, 255), (102, 64, 58, 255), (66, 40, 48, 255)]


def _flue(sp, x, y0, y1, cast=None):
    """`_overworld_props._chimney` on an honest copper, plus the assert that would
    have caught the still-house.

    TWO REASONS THIS EXISTS, and the second one is the important one.

    1. The shared `_chimney` draws its shaft in `COPPER[2]` (197,89,59), its east
       column in `COPPER[4]` (150,31,77) and two cap shoulders in `BRASS[3]`
       (216,0,109) — brick and MAGENTA, the violet shadow law on a warm seed,
       the same law `COPPERD` exists for.

    2. `Sprite.rect` on an INVERTED range draws nothing, and says nothing. The
       still-house shipped `_chimney(up, fx, 12, base - 12)` with `base = 22`, so
       `y1 = 10 < y0 = 12`: eight pixels of rain cap, no shaft under it at all,
       while `_wing_anim` went on faithfully smoking from the same coordinate.
       That is the user's ORIGINAL complaint — smoke with no chimney — put back
       by the change that fixed it, and nothing in the pipeline noticed: it
       renders, it dedupes, and every lint in `_check_art.py` passes it.
       A flue is one of the few things in this file with a shape it MUST have,
       so it gets to assert on it."""
    assert y1 > y0, (
        f"_flue: shaft y{y0}..y{y1} is inverted — Sprite.rect draws NOTHING on a "
        f"backwards range, so this is a rain cap floating over open air with a "
        f"smoke plume already aimed at it.")
    if cast is not None:
        for i in range(4):
            for j in range(3 - (i + 1) // 2):
                if sp.get(x + 4 + j, y1 - 3 + i) is not None:
                    sp.set(x + 4 + j, y1 - 3 + i, cast[4])
    sp.rect(x, y0 + 1, x + 3, y1, COPPERD[2])
    sp.rect(x, y0 + 1, x, y1, COPPERD[1])
    sp.rect(x + 3, y0 + 1, x + 3, y1, COPPERD[4])
    sp.rect(x - 1, y0, x + 4, y0, BRASSD[1])
    sp.set(x, y0, BRASSD[0])
    sp.set(x - 1, y0 + 1, BRASSD[2])
    sp.set(x + 4, y0 + 1, BRASSD[2])


def _ashlar(sp, x0, y0, x1, y1, stone, salt, course=8, joint=16, off=True):
    """Dressed ashlar: a REGULAR joint grid and no per-stone value variation.
    That distinction is the whole difference between a made wall and a rubble
    one, and it is the lesson `town_cliff(wall=True)` was rewritten twice to
    learn — heavy per-stone variation reads as rubble no matter how carefully
    each stone is shaded. Joints sit two steps down the ramp, NEVER black, or
    the wall reads as a lattice with light behind it."""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            sp.set(x, y, stone[2])
    for cy in range(y0 + course - 1, y1 + 1, course):      # bed joints
        sp.rect(x0, cy, x1, cy, stone[4])
    for i, cy in enumerate(range(y0, y1 + 1, course)):     # head joints
        shift = (joint // 2) if (off and i % 2) else 0
        for hx in range(x0 + shift, x1 + 1, joint):
            sp.rect(hx, cy, hx, min(cy + course - 2, y1), stone[4])
    sp.rect(x0, y0, x1, y0, stone[1])                      # the lit top arris


def academy_rampart(stone, salt=601, h=32, crest=9):
    """ONE 16 x `h` column of the Academy's curtain wall, stamped per column
    from several salted variants by TileScene.stamp_columns.

    It is the terrace band's idiom (fully opaque, no edge(), art lands on the
    run's TOP cell) wearing a different hat: this wall is DEFENSIVE, so the
    crest is a MERLON course rather than a coping, and the merlons are what make
    the silhouette read from across the ward.

    THE MERLONS ARE DRAWN PER COLUMN AND MUST TILE. A 16px column carries
    exactly one merlon and one embrasure, phase-locked to the column's own x
    rather than to the map, so a 50-cell wall comes out as one continuous
    battlement and still dedupes to `len(sprites)` atlas tiles. Get that phase
    from the salt instead and neighbouring columns disagree about where the gaps
    are, which reads as a wall someone has been chewing.

    COVERAGE: 100% (opaque by construction) — solid cells under it are safe from
    the invisible-wall lint."""
    sp = S(16, h, salt)
    merlon = h * 5 // 32                                   # the toothed crest
    walk = merlon + 3                                      # the wall-walk behind
    # the crest: merlon left half, embrasure right half, so two columns side by
    # side make one tooth and one gap
    for x in range(16):
        tooth = x < 9
        for y in range(h):
            if y < merlon and not tooth:
                continue                                   # the embrasure: sky
            if y < merlon:
                c = stone[1] if y == 0 else stone[2]
                if x == 8:
                    c = stone[4]                           # the tooth's own edge
            elif y < walk:
                c = stone[4] if tooth else stone[3]        # the wall-walk in shade
            else:
                c = None
            if c is not None:
                sp.set(x, y, c)
    _ashlar(sp, 0, walk, 15, h - 3, stone, salt, course=h * 8 // 32,
            joint=16, off=True)
    sp.rect(0, walk, 15, walk, stone[0])                   # the string course
    sp.rect(0, walk + 1, 15, walk + 1, stone[4])           # ...and its shadow
    sp.rect(0, h - 2, 15, h - 1, stone[5])                 # the plinth, near-black
    # ARROW SLITS on one variant in three. Rare on purpose: a slit in every
    # column is a colonnade, and the wall stops being a mass.
    if h2(salt, 3, 11) % 3 == 0:
        sy = walk + h * 5 // 32
        sp.rect(7, sy, 8, sy + h * 8 // 32, DOORDARK)
        sp.set(7, sy, stone[0]); sp.set(8, sy, stone[0])
    for k in range(2):                                     # weathering streaks
        cx = 2 + h2(salt + k * 7, 7, 1) % 12
        ln(sp, cx, walk + 2, cx + (salt % 3) - 1, h - 4, stone[4])
    clipw(sp, 16)
    return sp


def academy_tower(stone, salt=611, w=32, h=48):
    """One DRUM TOWER of the gatehouse — 32x48 on a 2x3 solid footprint, blitted
    Tier-1 by place_each (both towers are the same sprite: a gatehouse is
    symmetrical, and one sprite is half the atlas).

    It stands one row PROUD of the rampart so the gate has a silhouette. A wall
    with a hole in it is a hole in a wall; a wall with two towers either side of
    the hole is a gate, and that is the entire reason those two cells exist.

    Drawn as a CYLINDER — the tone ramps across its width, lit left, and the
    ashlar courses BOW: a course drawn as a straight line across a round tower
    flattens it into a flat panel with a curved outline, which is the single
    most common way a drum tower fails. A conical cap over a corbel course, a
    brass finial, and one lit arrow slit.

    COVERAGE: 100% on every footprint cell."""
    sp = S(w, h, salt)
    cx = w // 2
    cap, corbel = h * 5 // 48, h * 15 // 48
    # the cone
    for y in range(cap, corbel):
        t = (y - cap) / float(max(corbel - cap - 1, 1))
        half = 2 + int(round(t * (w // 2 - 1)))
        for x in range(cx - half, cx + half):
            u = (x - (cx - half)) / float(max(2 * half - 1, 1))
            sp.set(x, y, stone[0] if u < 0.22 else
                         stone[1] if u < 0.5 else
                         stone[2] if u < 0.78 else stone[4])
    # THE CORBEL COURSE, and it is the tower's strongest line: it is where the
    # cone stops and the drum starts, and drawn as one dark row it read as a seam.
    # Three rows — a lit oversail, the course, and the shade it throws — and the
    # cap sits ON something instead of being painted on.
    sp.rect(0, corbel - 2, w - 1, corbel - 2, stone[0])
    sp.rect(0, corbel - 1, w - 1, corbel - 1, stone[1])
    sp.rect(0, corbel, w - 1, corbel, stone[5])            # the corbel course
    sp.rect(0, corbel + 1, w - 1, corbel + 2, stone[4])
    sp.rect(cx - 1, cap - 5, cx, cap - 1, IRON[1])         # the staff...
    for i in range(5):                                     # ...and a swallowtail
        sp.rect(cx + 1, cap - 5 + i, cx + 7 - i, cap - 5 + i, VIOLETF)
    sp.set(cx + 2, cap - 4, CRYSTAL)
    sp.set(cx - 1, cap - 6, BRASSD[1])
    # the shaft, as a cylinder
    for y in range(corbel + 2, h):
        for x in range(w):
            u = x / float(w - 1)
            c = (stone[0] if u < 0.14 else stone[1] if u < 0.34 else
                 stone[2] if u < 0.62 else stone[3] if u < 0.84 else stone[4])
            sp.set(x, y, c)
    # BOWED ashlar courses — the cue that makes it round
    for cy in range(corbel + 8, h - 2, 8):
        for x in range(w):
            u = (x / float(w - 1)) * 2.0 - 1.0
            sp.set(x, cy - int(round((1.0 - u * u) * 2.0)), stone[4])
    for i, cy in enumerate(range(corbel + 4, h - 2, 8)):   # head joints
        for hx in range((0 if i % 2 else 6), w, 12):
            u = (hx / float(w - 1)) * 2.0 - 1.0
            yy = cy - int(round((1.0 - u * u) * 2.0))
            sp.rect(hx, yy, hx, min(yy + 6, h - 1), stone[4])
    sy = corbel + 10                                        # the arrow slit
    sp.rect(cx - 1, sy, cx, sy + 11, DOORDARK)
    sp.set(cx - 1, sy, MINT)
    sp.rect(0, h - 2, w - 1, h - 1, stone[5])               # the plinth
    clipw(sp, w)
    return sp


def court_weed(road, grass, salt=701, kind=0):
    """ONE 16x16 OVERLAY FOR A PAVING CELL — a hairline crack with something
    growing out of it. Blitted onto the finished lower canvas, so a cell that
    takes one becomes its own atlas tile and the rest of the court still dedupes.

    THE COURT IS 300-ODD CELLS OF ONE FLAT STONE and that was the single biggest
    thing wrong with this precinct after the buildings — a swept bailey at CT zoom
    reads as a car park. The doctrine in DESIGN.md ("PAVING ONLY WHERE THE
    PROCESSION WALKS, LAWN EITHER SIDE") was written for exactly this and the map
    does not keep it, but re-cutting the map would also cost the court its shape.
    Weeds are the better answer and they are not a compromise: this is a college
    the world stopped funding, in a season when magic drained out of the ground
    overnight. NOBODY HAS SWEPT IT. The cracks are the story, the flat stone was
    just flat.

    Four kinds, salted, so a hundred of them never read as a pattern:
      0  a joint that has opened, with a tuft in it
      1  a spray of blades, no crack — a seed that landed in a seam
      2  a moss patch bleeding along two joints
      3  a chipped stone, dark, with grit round it — wear without growth, which
         is what keeps the other three from reading as a lawn
    """
    sp = S(16, 16, salt)
    hx, hy = 2 + h2(salt, 1, 3) % 11, 2 + h2(salt, 5, 7) % 11
    if kind in (0, 2):
        y = hy
        for x in range(16):                                # the crack, wandering
            sp.set(x, y, road[4] if (x + salt) % 5 else road[5])
            if h2(x, salt, 11) % 4 == 0:
                y = max(1, min(14, y + (1 if h2(x, salt, 13) % 2 else -1)))
    if kind == 2:
        for i in range(9):                                 # moss along the seam
            mx = 1 + (i * 3 + salt) % 14
            my = hy + (h2(mx, salt, 17) % 3) - 1
            sp.set(mx, my, grass[4])
            sp.set(mx, my + 1, grass[5])
    elif kind == 3:
        sp.blob(hx, hy, 2.6, 2.0, road[4])                 # a chip out of a stone
        sp.blob(hx, hy, 1.4, 1.0, road[5])
        for i in range(5):
            sp.set(hx - 3 + (h2(i, salt, 19) % 7), hy - 2 + (h2(i, salt, 23) % 5),
                   road[3])
    else:
        for i in range(4 + salt % 3):                      # the blades
            bx = hx - 2 + (h2(i, salt, 29) % 5)
            hh = 2 + h2(i, salt, 31) % 4
            lean = -1 if i % 2 else 1
            for k in range(hh):
                sp.set(bx + (lean if k >= hh - 1 else 0), hy - k,
                       grass[2] if k == hh - 1 else grass[3])
            sp.set(bx, hy + 1, grass[5])
    return sp


def academy_orrery(stone, salt=621, w=96, h=64):
    """THE GREAT ORRERY — a brass armillary sphere on a stone plinth, standing
    dead on the precinct's axis. 64x48 over a 4x3 footprint: the top two rows
    are WALKABLE (the sphere's own walk-behind crown, the lamp idiom) and the
    bottom row is the solid plinth, so the monument is something you go round
    and something you can be hidden by.

    THE RINGS ARE ELLIPSES OF DIFFERENT ECCENTRICITY AND THAT IS THE WHOLE
    TRICK. Three concentric circles read as a target painted on a wall; three
    ellipses whose minor axes differ read as three hoops at three angles, which
    is a sphere. The equatorial ring is nearly edge-on, the meridian nearly
    face-on, and the third is between them and TILTED, because a symmetric pair
    reads as a plus sign.

    COVERAGE: the solid plinth row is 100%. The walkable crown rows are not
    measured — they are walkable precisely because a sphere leaves its corner
    cells empty."""
    sp = S(w, h, salt)
    cx, cy = w // 2, h * 17 // 48
    # ---- the plinth: a stepped ashlar block, widest at the bottom
    ptop = h * 30 // 48
    for i, (inset, y0, y1) in enumerate(((10, ptop, ptop + 3),
                                         (6, ptop + 4, ptop + 7),
                                         (2, ptop + 8, h - 1))):
        _ashlar(sp, inset, y0, w - 1 - inset, y1, stone, salt + i,
                course=4, joint=10)
        sp.rect(inset, y0, w - 1 - inset, y0, stone[0])
        sp.rect(inset, y1, w - 1 - inset, y1, stone[4])
    sp.rect(0, h - 2, w - 1, h - 1, stone[5])
    # a bronze plate on the face — the founder's name nobody reads any more
    # COPPERD, NOT COPPER. `COPPER[3]` is (174,43,57) and `COPPER[4]` is
    # (150,31,77) — the violet shadow law again — so the founder's plate shipped
    # as a RED-AND-MAGENTA bar in the middle of a grey monument, which is what the
    # eye went to first in the whole court.
    sp.rect(cx - 7, ptop + 9, cx + 6, ptop + 13, COPPERD[3])
    sp.rect(cx - 7, ptop + 9, cx + 6, ptop + 9, COPPERD[1])
    for gx in range(cx - 5, cx + 6, 3):
        sp.rect(gx, ptop + 11, gx + 1, ptop + 11, COPPERD[4])
    # ---- the armature the sphere sits in
    sp.rect(cx - 1, cy + 6, cx, ptop + 1, BRASS[1])
    sp.rect(cx + 1, cy + 6, cx + 1, ptop + 1, IRON[2])
    # ---- three rings, three eccentricities
    for rx, ry, tilt, lit in ((19, 6, 0.0, True),          # the equator, edge-on
                              (13, 17, 0.0, False),        # the meridian
                              (16, 11, 0.35, True)):       # the ecliptic, tilted
        for a in range(0, 360, 2):
            th = a * 3.14159 / 180.0
            ex = rx * _cos(th)
            ey = ry * _sin(th)
            x = cx + int(round(ex * _cos(tilt) - ey * _sin(tilt)))
            y = cy + int(round(ex * _sin(tilt) + ey * _cos(tilt)))
            near = ey > 0                                  # the near half of a hoop
            c = (BRASS[0] if (lit and near) else BRASS[1] if near else
                 IRON[2] if lit else IRON[3])
            sp.set(x, y, c)
            sp.set(x, y + 1, IRON[2] if near else IRON[3])
    sp.ball(cx, cy, 4.0, 4.0, BRASSD)                      # the sun at its centre
                                                           # (BRASS[2] is PURE RED —
                                                           # it was a red bead)
    sp.set(cx - 1, cy - 1, SPEC)
    for px, py, c in ((cx - 13, cy + 3, MINT), (cx + 15, cy - 2, CRYSTAL),
                      (cx + 7, cy + 9, COPPER[1])):        # three planet beads
        sp.set(px, py, c)
        sp.set(px + 1, py, IRON[3])
    clipw(sp, w)
    return sp


# ======================================================================================
# THE KEEP — a TIMBER CASTLE-SCHOOL whose corner towers are two great trees
# ======================================================================================

def _blit_sp(dst, src, ox, oy):
    """Copy a Sprite's opaque pixels onto another Sprite."""
    for y in range(src.n):
        row = src.px[y]
        for x in range(src.n):
            if row[x]:
                dst.set(ox + x, oy + y, row[x])


def _blit_img(dst, img, ox, oy):
    """...and an Img's. `great_trunk` hands back Imgs — it slices one virtual
    trunk into storey segments — and here the trunk is drawn INTO the keep's own
    canvas rather than emitted as a prop of its own (see academy_keep)."""
    for y in range(img.h):
        for x in range(img.w):
            p = img.get(x, y)
            if p[3]:
                dst.set(ox + x, oy + y, p)


def _pitch(sp, cx, ytop, ybot, half_top, half_bot, mat, salt, course=7):
    """A CEDAR-SHAKE ROOF PLANE, drawn as a trapezoid from a ridge half-width to
    an eave half-width.

    Three things stop 74px of pitch reading as one flat trapezoid, and all three
    are cheap:
      * the value ramps DOWN the slope — the courses near the ridge face the sky
        and the ones at the eaves are looking at you nearly edge-on;
      * every course is seated on its own DARK BUTT LINE, which is the shadow the
        shake above throws on the one below and the only reason a shingle roof
        reads as made of pieces at all;
      * the vertical joints STAGGER course to course. Aligned, they draw a grid
        and a grid on a roof reads as tile, not shake.
    """
    n = len(mat) - 1
    for y in range(ytop, ybot + 1):
        u = (y - ytop) / float(max(1, ybot - ytop))
        half = half_top + (half_bot - half_top) * u
        x0, x1 = int(round(cx - half)), int(round(cx + half))
        c = int(y - ytop) // course                       # which course we are in
        butt = (y - ytop) % course == course - 1
        for x in range(x0, x1 + 1):
            t = 0.16 + 0.46 * u + 0.06 * ((h2(x // 9, c, salt) % 3) - 1)
            if butt:
                t += 0.34                                 # the shadow under a butt
            if (x + 4 * c + (h2(c, 1, salt) % 5)) % 9 == 0:
                t += 0.22                                 # the staggered joint
            i = min(n, max(0, int(t * n + 0.5)))
            sp.set(x, y, mat[i])
        sp.set(x0, y, mat[min(n, 4)])                     # the verge boards, which
        sp.set(x1, y, mat[min(n, 5)])                     # is what caps a pitch


def _timber_wall(sp, x0, y0, x1, y1, oak, daub, salt, posts=6, brace=True):
    """HALF-TIMBERING: a dark oak frame with limewashed daub panels in it.

    This is the whole reason the keep stops being flat. A wall of one fabric is
    one plane however carefully it is shaded; a wall of framed PANELS is a grid
    of small planes, each with its own lit top edge and its own shadow under the
    rail above it, and the eye reads that as relief at any resolution.

    The braces matter more than the posts. Verticals alone read as a fence; a
    pair of curved braces springing off each post is what says CARPENTRY, and it
    is the single silhouette cue that separates a timber hall from a shed.
    """
    for y in range(y0, y1 + 1):                            # the daub, first
        for x in range(x0, x1 + 1):
            t = 0.22 + 0.030 * ((h2(x // 5, y // 5, salt) % 5) - 2)
            sp.set(x, y, daub[min(len(daub) - 1, max(0, int(t * 5 + 0.5)))])
    rail_y = y0 + (y1 - y0) * 2 // 5                       # the mid rail
    step = max(18, (x1 - x0) // max(1, posts))
    xs = list(range(x0, x1 - 3, step))
    for bx in xs:                                          # the posts
        sp.rect(bx, y0, bx + 4, y1, oak[3])
        sp.rect(bx, y0, bx, y1, oak[2])                    # lit arris
        sp.rect(bx + 4, y0, bx + 4, y1, oak[5])            # and its shadow
        sp.rect(bx + 5, y0, bx + 6, y1, daub[3])           # the shade it throws east
    for ry, hh in ((y0, 4), (rail_y, 4), (y1 - 3, 4)):     # sill, rail, wall-plate
        sp.rect(x0, ry, x1, ry + hh - 1, oak[3])
        sp.rect(x0, ry, x1, ry, oak[2])
        sp.rect(x0, ry + hh - 1, x1, ry + hh - 1, oak[5])
        if ry + hh <= y1 - 1:
            sp.rect(x0, ry + hh, x1, ry + hh + 1, daub[3])  # and ITS shade below
    if brace:
        # UP AND OUT from the foot of each post to the rail above it. Drawn the other
        # way round — springing off the rail and curving DOWN — they read as rope
        # swags hung between the posts, which is what the first cut of this shipped
        # as: a hall with bunting on it. A brace carries load upward.
        for bx in xs:
            for sgn in (-1, 1):
                for i in range(11):
                    u = i / 10.0
                    px_ = bx + 1 + sgn * int(round(13 * u))
                    py_ = y1 - 5 - int(round(15 * (1.0 - (1.0 - u) ** 2)))
                    if x0 + 1 <= px_ <= x1 - 1 and py_ > rail_y + 3:
                        sp.rect(px_, py_, px_, py_ + 2, oak[3])
                        sp.set(px_, py_, oak[2])
                        sp.set(px_, py_ + 2, oak[5])


def _lancet(sp, cx, y0, y1, half, oak, stone):
    """A tall traceried window: arched head, one mullion, warm glass, stone sill.

    The glass is WARMD/WARM by VALUE because `_breathe` matches those two colours
    exactly — a pane painted in any other tone is simply inert, and the hall's
    windows are the thing that says the school is still lit."""
    sp.rect(cx - half - 2, y0 - 1, cx + half + 2, y1 + 1, oak[4])   # the frame
    sp.rect(cx - half, y0, cx + half, y1, WARMD)
    sp.blob(cx, y0 + half * 0.6, half + 0.5, half * 0.9, oak[4])    # arched head
    sp.blob(cx, y0 + half * 0.8, half - 0.8, half * 0.7, WARMD)
    # THE THROW BAND STAYS IN THE TOP THIRD. Run down the whole pane at a 2-on-2-off
    # duty cycle — which is how this shipped — a lit window is a saturated ORANGE
    # BARCODE, the most candy-coloured thing in the precinct and squarely in the
    # "very kiddy" failure mode this project's art has as its standing risk. Firelight
    # falls off; `_tree_props._hearth_window` already confines its throw to two rows
    # for the same reason. `_breathe` still matches WARM/WARMD by VALUE, so the
    # hearth breath is unaffected.
    for gy in range(y0 + 3, y0 + (y1 - y0) // 3, 3):
        sp.rect(cx - half + 1, gy, cx + half - 1, gy, WARM)         # the hearth throw
    for gy in range(y0 + 5, y1, 6):                                 # leaded bars —
        sp.rect(cx - half + 1, gy, cx + half - 1, gy, oak[5])       # dark and sparse,
    sp.rect(cx, y0, cx, y1, oak[5])                                 # not a barcode
    for i in range(5):
        sp.set(cx + 3 + i, y0 + 5 + i, GLASS)                       # sky-catch streak
    sp.rect(cx - half - 3, y1 + 2, cx + half + 3, y1 + 3, stone[0])  # the lit sill
    sp.rect(cx - half - 3, y1 + 4, cx + half + 3, y1 + 4, stone[4])


def _shade_band(sp, x0, y0, x1, y1, steps=2):
    """Pull whatever is already drawn in a rect DOWN the ramp it was drawn from,
    without knowing which ramp that was — the cast shadow an overhang throws.

    An eave that does not darken the wall under it is not an overhang, it is a
    line. This is the same argument `_alembic._shade_under` makes for a trunk
    coming out from under a deck, and it is the cheapest depth cue in the file.
    """
    TABLE = (OAK, SHAKE, DAUB)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            c = sp.get(x, y)
            if c is None:
                continue
            for mat in TABLE:
                if c in mat:
                    sp.set(x, y, mat[min(len(mat) - 1, mat.index(c) + steps)])
                    break
            else:
                sp.set(x, y, tuple(int(v * 0.62) for v in c[:3]) + (c[3],))


def _cos(t):
    """Tiny series cos/sin so this module stays stdlib-and-no-math — the rest of
    the pipeline draws every curve from the quadratic forms in Sprite, and an
    armillary is the one place a real trig circle is worth it."""
    import math
    return math.cos(t)


def _sin(t):
    import math
    return math.sin(t)


def _keep_anim(facade, canopy, f, dy=0):
    """The keep's two stacks and its four lit windows. Coordinates are
    sprite-local to the UNPADDED art and `dy` is passed THROUGH to
    _anim_building, which is the contract every other _*_anim in the project
    keeps — see the note on _wing_anim, which broke it and drew smoke out of
    thin air for exactly that reason."""
    _anim_building(facade, canopy, f, dy=dy,
                   flues=((148, 104), (264, 104)),
                   windows=((110, 132, 25, 33), (282, 132, 25, 33)))


def academy_keep(stone, bark, fol, ground, salt=221, composite=True, frames=8):
    """THE KEEP — a TIMBER CASTLE-SCHOOL, 416x192 over a 22x9 footprint, whose
    CORNER TOWERS ARE TWO GREAT TREES.

    It replaces `_town_props.town_academy`, which was drawn for the town grid the
    Academy left and read, in this precinct, as a flat cream wall with a garden
    on top. Three things were wrong with it and only one was style:

      1. IT WAS FLAT. One plane of cement, one plane of leaf, and every opening
         cut flush into the wall. Nothing overhung anything, so nothing cast a
         shadow onto anything, so there was no second surface for the eye to
         find. Here the depth is structural, in descending order of how much each
         cue buys: the porch bay standing proud of the hall (its gable, its own
         pitch, and the shadow it throws on the wall beside it), the deep eaves
         with a shade band under them, half-timbered PANELS instead of a fabric,
         and the trunks overlapping the roof's own corners.
      2. ITS TOWERS WERE NOT THE TREES. The two great trees stood six cells out
         in the lawn, centred under their own crowns, which at ground level — the
         only level the player is ever at — is landscaping beside a building.
         Here they are IN the building's footprint and IN its sprite: the hall's
         roof runs out and DIES INTO each trunk, so the tree is load-bearing in
         the composition, not next to it. That also settles the map problem for
         free: one char per cell means a separate crown block can never overlap
         the keep's, and a crown that cannot lean over the roof cannot flank it.
      3. IT WAS 16px OFF THE AXIS. The gate, the grand stair and the orrery all
         sit on x=496 (the col 30/31 boundary); the old keep's door was at col 32.
         A processional way whose door is one cell off its own stair is not a
         processional way. Everything here is centred on 496.

    THE SPRITE IS WIDER THAN THE FOOTPRINT — 26 cells of art over 22 cells of
    collision. emit_prop centres art on the block, so the crowns hang two cells
    into the lawn either side and you walk under the leaves. That is the
    walk-behind idiom, and the hang is deliberately only 2 cells: the visibility
    lint forgives a hidden RUN of two (a step you pass through) and condemns
    three (a place you disappear into).

    FOOTPRINT: 26x12 of art over 22x9 of cells, every cell SOLID except the two
    door cells on the south row. ANCHOR: emit_prop(..., hframes=frames) — bottom
    anchored, so the extra three rows of art run UP into the forest border and
    the crowns join the wood behind the precinct.
    COVERAGE: 100% on the four facade rows (the plinth runs the full width under
    everything); the roof rows are the crowns and are perforated on purpose.

    THE CAMERA ONLY EVER SHOWS 100px ABOVE A BUILDING'S FOOT — it is y-centred on
    the body over a 216-tall viewport, so it shows 108px above the player, and a
    player at the door stands ~8px south of the base line. Backing away does not
    help: the camera backs away too. That is a real constraint and it was worth
    measuring, but the conclusion it first produced — squash the hall until the
    whole silhouette fits — was WRONG, and the screenshots settled it. A building
    that fits inside the frame reads as a cottage. A building whose roof leaves
    the top of the frame reads as too big for the screen, which is the thing you
    actually want out of a keep, and it is how every great tree in this project
    already works.

    So: the hall stays TALL and the ridge stays off screen. What the constraint
    buys instead is a rule about FURNITURE — anything the player is meant to READ
    (the rose window, the bell, the door, the galleries, and every chimney cap,
    because a plume whose flue is off screen is the exact defect this pass began
    with) must sit below y=92. Hence the two chimney BREASTS, which run all the
    way down the facade to the plinth rather than perching on a ridge nobody can
    see, and which are worth more as depth than a ridge stack ever was.
    """
    W, H, FY = 416, 192, 122
    CX = 208                                     # the precinct's axis, x=496 on the map
    GY = H - 1
    TCX = (72, W - 72)                           # the two trunk centrelines
    WX0, WX1 = 104, 311                          # the hall's wall
    RIDGE_Y, EAVE_Y = 52, 122                    # the great pitch
    RIDGE_H, EAVE_H = 62, 128
    PX0, PX1 = CX - 40, CX + 40                  # the porch bay
    PORCH_APEX, PORCH_EAVE = 62, 116
    BREAST = (150, 266)                          # the two chimney breasts
    sp = S(W, H, salt)

    # ---- 1. THE STONE FOOTING, and it runs the WHOLE width -----------------------------
    # A timber building on the ground is a timber building rotting into the ground.
    # It also does the lint's work: the four facade rows are opaque edge to edge
    # whatever the trees do, so no solid cell can render as open lawn.
    # ...AND IT STOPS AT THE BLOCK, not at the canvas. The art is 26 cells wide over
    # 22 cells of collision, so a footing run to `W - 1` lays 32px of dressed stone
    # across open walkable lawn at each end and then stops in a hard vertical cut
    # against the grass — a kerb going nowhere. The crowns are the only thing that
    # may use the overhang; they are perforated leaves, which is what an overhang is
    # for.
    BX0, BX1 = (W - 22 * 16) // 2, W - 1 - (W - 22 * 16) // 2
    _ashlar(sp, BX0, H - 14, BX1, GY, stone, salt, course=6, joint=15)
    sp.rect(BX0, H - 14, BX1, H - 14, stone[0])
    sp.rect(BX0, GY - 1, BX1, GY, stone[5])
    sp.rect(PX0 - 5, H - 18, PX1 + 5, H - 15, stone[1])   # the porch's own step,
    sp.rect(PX0 - 5, H - 18, PX1 + 5, H - 18, stone[0])   # standing proud

    # ---- 2. THE HALL WALL: dark oak frame, limewashed panels ---------------------------
    _timber_wall(sp, WX0, FY, WX1, H - 15, OAK, DAUB, salt, posts=10)
    _lancet(sp, 122, 132, 164, 12, OAK, stone)
    _lancet(sp, 294, 132, 164, 12, OAK, stone)

    # ---- 3. THE GREAT PITCH ------------------------------------------------------------
    _pitch(sp, CX, RIDGE_Y, EAVE_Y, RIDGE_H, EAVE_H, SHAKE, salt, course=6)
    sp.rect(CX - RIDGE_H, RIDGE_Y - 2, CX + RIDGE_H, RIDGE_Y - 1, SHAKE[1])  # ridge cap
    sp.rect(CX - RIDGE_H, RIDGE_Y - 3, CX + RIDGE_H, RIDGE_Y - 3, SHAKE[0])
    for i in range(8):                                     # crested ridge tiles
        sp.rect(CX - 56 + i * 16, RIDGE_Y - 5, CX - 54 + i * 16, RIDGE_Y - 4, SHAKE[0])
    # THE EAVE: a barge board hanging past the wall, then its shadow ON the wall.
    # This pair is the difference between an overhang and a drawn line.
    sp.rect(CX - EAVE_H, EAVE_Y, CX + EAVE_H, EAVE_Y + 2, OAK[3])
    sp.rect(CX - EAVE_H, EAVE_Y, CX + EAVE_H, EAVE_Y, OAK[2])
    sp.rect(CX - EAVE_H, EAVE_Y + 3, CX + EAVE_H, EAVE_Y + 3, OAK[5])
    _shade_band(sp, WX0, EAVE_Y + 4, WX1, EAVE_Y + 11, steps=2)
    for bx in range(WX0 + 8, WX1 - 6, 26):                 # the rafter feet under it
        sp.rect(bx, EAVE_Y - 3, bx + 2, EAVE_Y - 1, OAK[4])

    # ---- 4. THE PORCH BAY, which is the building's whole third dimension ---------------
    # Drawn AFTER the pitch and the wall so it is unambiguously in front of both, and
    # given its own cast shadow on the wall to its east — LIGHT comes from the NW, and
    # a bay that throws no shadow is a rectangle painted on a wall.
    _shade_band(sp, PX1 + 6, PORCH_EAVE + 2, PX1 + 18, H - 16, steps=2)
    _pitch(sp, CX, PORCH_APEX, PORCH_EAVE, 3, 48, SHAKE, salt + 3, course=6)
    sp.rect(CX - 48, PORCH_EAVE, CX + 48, PORCH_EAVE + 2, OAK[3])
    sp.rect(CX - 48, PORCH_EAVE, CX + 48, PORCH_EAVE, OAK[2])
    sp.rect(CX - 48, PORCH_EAVE + 3, CX + 48, PORCH_EAVE + 3, OAK[5])
    _timber_wall(sp, PX0, PORCH_EAVE + 4, PX1, H - 19, OAK, DAUB, salt + 5,
                 posts=4, brace=False)
    for sgn in (-1, 1):                                    # the bay's corner posts
        bx = CX + sgn * 40
        sp.rect(bx - 3, PORCH_EAVE + 4, bx + 2, H - 15, OAK[4])
        sp.rect(bx - 3, PORCH_EAVE + 4, bx - 3, H - 15, OAK[2])
        sp.rect(bx + 2, PORCH_EAVE + 4, bx + 2, H - 15, OAK[5])

    # ---- 5. THE ROSE WINDOW, in the porch gable, burning MINT --------------------------
    # DESIGN.md has said since the overworld icon was drawn that the Academy's rose
    # window is the one cold light in this game that is not a lamp.
    rcx, rcy = CX, PORCH_APEX + 42
    for r_, c in ((14.0, OAK[4]), (12.4, OAK[5]), (10.8, DOORDARK),
                  (8.4, MINT), (4.0, fol[2])):
        sp.blob(rcx, rcy, r_, r_, c)
    sp.rect(rcx, rcy - 11, rcx, rcy + 11, OAK[5])          # the tracery cross
    sp.rect(rcx - 11, rcy, rcx + 11, rcy, OAK[5])
    for sx_, sy_ in ((1, 1), (-1, 1), (1, -1), (-1, -1)):  # radial spokes
        ln(sp, rcx + 4 * sx_, rcy + 4 * sy_, rcx + 8 * sx_, rcy + 8 * sy_,
           OAK[5])
    sp.set(rcx, rcy, CRYSTAL)
    sp.set(rcx - 4, rcy - 5, GLASS)

    # ---- 6. THE GREAT DOOR — BIG, arched, iron-barred, and it stays shut ---------------
    # Nothing has stirred in here since the Ebb. The era that opens this door is the
    # prologue's, and the prologue plays INSIDE the lecture hall.
    #
    # IT IS DELIBERATELY OVERSIZED — 48px of opening under a stone arch 64px across,
    # nearly two of the 33px cat. A door scaled to the body reads as a house's front
    # door however grand the wall around it; a door you could drive a cart through is
    # most of what says "this building is not for you".
    SPRING, DTOP = 152, 126                                # the arch springs and crowns
    sp.blob(CX, SPRING, 32.0, SPRING - DTOP + 4, stone[3])  # the voussoir ring...
    sp.rect(CX - 32, SPRING, CX + 32, GY - 2, stone[3])
    sp.blob(CX, SPRING, 30.0, SPRING - DTOP + 2, stone[1])  # ...lit on its face
    sp.rect(CX - 30, SPRING, CX + 30, GY - 3, stone[1])
    for a in range(-5, 6):                                 # the voussoir joints
        u = a / 5.0
        jx = CX + int(round(u * 30))
        jy = SPRING - int(round((SPRING - DTOP + 2) * (1.0 - u * u) ** 0.5))
        ln(sp, jx, jy, CX + int(round(u * 24)),
           SPRING - int(round((SPRING - DTOP - 4) * (1.0 - u * u) ** 0.5)), stone[4])
    sp.blob(CX, SPRING, 26.0, SPRING - DTOP - 2, stone[4])  # the reveal, in shade
    sp.rect(CX - 26, SPRING, CX + 26, GY - 3, stone[4])
    DX0, DX1, DT = CX - 24, CX + 24, DTOP + 4
    sp.blob(CX, SPRING, 24.0, SPRING - DT, OAK[4])         # the leaves' own frame
    sp.rect(DX0, SPRING, DX1, GY - 4, OAK[4])
    sp.blob(CX, SPRING, 22.0, SPRING - DT - 2, DOORDARK)   # ...and the dark mouth
    sp.rect(DX0 + 2, SPRING, DX1 - 2, GY - 5, DOORDARK)
    for gy in range(DT + 10, GY - 4, 7):
        sp.rect(DX0 + 2, gy, DX1 - 2, gy, OAK[5])          # plank lines
    sp.rect(CX, DT + 4, CX, GY - 5, OAK[5])                # the meeting stile: two leaves
    for bx in range(DX0 + 5, DX1 - 2, 7):                  # THE BARS
        sp.rect(bx, DT + 8, bx, GY - 6, IRON[2])
        sp.set(bx, DT + 8, IRON[1])
    for sy_ in (DT + 16, DT + 34, DT + 52):                # straps and rivets
        if sy_ >= GY - 6:
            continue
        sp.rect(DX0 + 2, sy_, DX1 - 2, sy_, IRON[3])
        for rx in range(DX0 + 4, DX1 - 2, 8):
            sp.set(rx, sy_, IRON[1])
    for sgn in (-1, 1):                                    # two iron ring handles
        sp.blob(CX + sgn * 8, DT + 44, 3.0, 3.0, IRON[2])
        sp.blob(CX + sgn * 8, DT + 44, 1.6, 1.6, DOORDARK)
    sp.set(CX, DT + 24, MINT); sp.set(CX, DT + 42, MINT)   # old-magic seams
    sp.rect(CX - 36, GY - 3, CX + 36, GY - 2, stone[1])    # the worn threshold
    sp.rect(CX - 36, GY - 1, CX + 36, GY, stone[5])

    # ---- 7. THE TWO CHIMNEY BREASTS ----------------------------------------------------
    # They run the WHOLE height of the facade, from the plinth up through the wall and
    # out through the eave, rather than perching on the ridge — which is both better
    # architecture for a timber hall (the one masonry thing in it is the fire) and the
    # only way the caps are on screen at all. Each one interrupts the half-timbering,
    # breaks the eave line, and throws a shadow east: three depth cues for one object.
    for fx in BREAST:
        for x in range(fx - 9, fx + 10):                   # rounded across its width
            u = (x - (fx - 9)) / 18.0
            c = stone[1] if u < 0.16 else stone[2] if u < 0.62 else stone[3]
            sp.rect(x, 116, x, H - 15, c)
        _coursed_wall(sp, fx - 9, 116, fx + 9, H - 15, stone,
                      salt=salt + fx, course=7, joint=13)
        sp.rect(fx - 9, 116, fx - 9, H - 15, stone[0])     # the lit west arris
        sp.rect(fx + 9, 116, fx + 9, H - 15, stone[5])     # its own east shade
        sp.rect(fx + 8, 116, fx + 8, H - 15, stone[4])
        sp.rect(fx - 11, 112, fx + 11, 115, stone[1])      # the corbelled cap
        sp.rect(fx - 11, 112, fx + 11, 112, stone[0])
        sp.rect(fx - 11, 116, fx + 11, 116, stone[4])
        _shade_band(sp, fx + 10, 118, fx + 20, H - 16, steps=2)
        # THE CAP SITS AT y=104 AND NOT A PIXEL HIGHER. _anim_building lofts its puffs
        # ~9px above a flue, the top of the screen is y=92, and a plume whose chimney
        # is on screen but whose smoke is not is precisely the defect this whole pass
        # started from, in the other direction.
        _flue(sp, fx - 2, 104, 111, cast=SHAKE)

    # ---- 8. THE TWO GREAT TREES, which are the corner towers ---------------------------
    # The trunk goes on AFTER the roof so the pitch dies INTO it — that overlap is the
    # join, and it is the only thing in the sprite that makes the tree part of the
    # building rather than beside it. Baked order is depth (art-pipeline skill).
    for i, tcx in enumerate(TCX):
        shaft = great_trunk(bark, ground, [(0, 8)], salt=401 + 30 * i, w=64,
                            lean=2.0 if i else -2.0)[0]
        _blit_img(sp, shaft, tcx - 32, H - shaft.h)
        # THE TOWER DOOR: narrow, arched, iron-strapped. ONE opening, not three — a
        # trunk with a door AND a round window AND a balcony is a gingerbread tree,
        # and "very kiddy" is the standing failure mode in this project's art.
        dx0, dx1, dy0 = tcx - 9, tcx + 9, 158
        sp.blob(tcx, dy0 + 3, 10.5, 7.0, OAK[5])
        sp.rect(dx0 - 1, dy0 + 3, dx1 + 1, GY - 3, OAK[5])
        sp.blob(tcx, dy0 + 4, 9.0, 5.6, OAK[3])
        sp.rect(dx0, dy0 + 4, dx1, GY - 4, OAK[3])
        for gy in range(dy0 + 2, GY - 4, 5):
            sp.rect(dx0, gy, dx1, gy, OAK[5])
        for sy_ in (dy0 + 11, dy0 + 22):
            sp.rect(dx0, sy_, dx1, sy_, IRON[3])
            for rx in range(dx0 + 2, dx1, 6):
                sp.set(rx, sy_, IRON[1])
        sp.set(dx1 - 3, dy0 + 16, BRASSD[1])               # the ring handle

    # ---- 9. THE CROWNS, over everything, and off the top of the frame ------------------
    # They are DELIBERATELY cut by the screen's top edge. Every great tree in this
    # project runs off the top and that is what sells the scale: the trees are the one
    # thing here you never see all of.
    for i, tcx in enumerate(TCX):
        crown = great_crown(fol, bark, salt=451 + 30 * i, w=144, h=128,
                            lean=-5.0 if i else 5.0)
        _blit_sp(sp, crown, tcx - 72, 0)

    # ---- 10. THE GALLERIES, and the BELL — drawn OVER the leaves -----------------------
    # A hooped timber deck round each trunk, level with the hall's own eaves and butting
    # into them: the hoarding a castle puts on a corner tower, in the only material this
    # Academy has. It is what turns a tree beside a building into a tower OF it.
    #
    # LAST, over the crowns, because the gallery projects toward the camera and the
    # leaves are behind it. Drawn before them (which is how this first read) the crown
    # buries the rail and the deck comes out as a brown eyebrow across the trunk.
    for i, tcx in enumerate(TCX):
        gy0 = EAVE_Y - 2
        for bxs in (-30, -18, 18, 30):                     # the brackets, first
            for k in range(9):
                bxx = tcx + bxs + (k if bxs < 0 else -k)
                sp.rect(bxx, gy0 + 9 + k, bxx, gy0 + 11 + k, OAK[4])
                sp.set(bxx, gy0 + 9 + k, OAK[3])
        sp.rect(tcx - 30, gy0, tcx + 30, gy0 + 8, OAK[2])  # the deck — NARROWER than
        sp.rect(tcx - 30, gy0, tcx + 30, gy0, OAK[1])      # the 64px trunk, so bark
        sp.rect(tcx - 30, gy0 + 7, tcx + 30, gy0 + 8, OAK[5])   # shows past both ends
        for px_ in range(tcx - 29, tcx + 30, 7):                # and the tower still
            sp.rect(px_, gy0 + 1, px_, gy0 + 6, OAK[3])         # tapers past it
        # A VERTICAL FACE MUST BE DARKER THAN THE SURFACE IT HANGS OFF (the Alembic
        # rebuild's own lesson, 2026-07-30). A deck that does not darken the bark
        # under it is a decal, and this one call is worth more than every baluster
        # above it.
        _shade_band(sp, tcx - 32, gy0 + 9, tcx + 32, gy0 + 22, steps=2)
        sp.rect(tcx - 32, gy0 - 13, tcx + 32, gy0 - 12, OAK[3])   # the rail
        sp.rect(tcx - 32, gy0 - 13, tcx + 32, gy0 - 13, OAK[2])
        for px_ in range(tcx - 30, tcx + 31, 8):                  # its balusters
            sp.rect(px_, gy0 - 11, px_, gy0 - 1, OAK[4])
        if i == 0:
            # THE ACADEMY BELL, hung in the west tower on an iron yoke under its own
            # gallery. It is the one cue in the whole precinct that says SCHOOL and not
            # CASTLE, and there is nowhere else on screen to put it: a cote on the ridge
            # or on the porch apex would sit above y=92 and never be seen at all.
            # A 14px bell has to be a SILHOUETTE with a lit rim — the same argument the
            # shop windows' wares are drawn from. Brass in its own colours at this size
            # is a yellow smudge.
            byy = gy0 + 11
            sp.rect(tcx - 13, byy - 5, tcx + 13, byy - 4, IRON[3])      # the yoke beam
            sp.rect(tcx - 13, byy - 5, tcx + 13, byy - 5, IRON[1])
            sp.rect(tcx - 1, byy - 4, tcx, byy - 1, IRON[2])            # the headstock
            # DARK BODY, ONE LIT RIM — the comment two lines up said exactly this and
            # the first cut did the opposite: a cream-to-brown cone 27px wide hung
            # dead centre on a dark trunk is a LAMPSHADE, not a bell. Smaller, darker
            # than its ground, and lit only on the west edge.
            for k in range(13):
                u = k / 12.0
                hw = 2.8 + 4.6 * (u ** 1.55)
                for x in range(int(tcx - hw), int(tcx + hw) + 1):
                    v = (x - (tcx - hw)) / max(1.0, 2.0 * hw)
                    sp.set(x, byy + k, BRASSD[1] if v < 0.16 else
                                       BRASSD[3] if v < 0.42 else
                                       IRON[3] if v < 0.82 else DOORDARK)
            sp.rect(tcx - 7, byy + 13, tcx + 7, byy + 14, IRON[3])      # the flared lip
            sp.rect(tcx - 7, byy + 13, tcx + 7, byy + 13, BRASSD[2])
            sp.set(tcx - 7, byy + 13, BRASSD[1])
            sp.rect(tcx - 6, byy + 15, tcx + 6, byy + 15, DOORDARK)     # its dark mouth
            sp.rect(tcx, byy + 16, tcx, byy + 18, IRON[2])              # the clapper
        else:
            sp.rect(tcx + 22, gy0 - 19, tcx + 24, gy0 - 14, IRON[2])    # a lamp, instead
            sp.blob(tcx + 23, gy0 - 22, 2.8, 3.2, MINT)
            sp.set(tcx + 22, gy0 - 23, SPEC)

    # ---- 11. ivy, because the college is kept alive by its garden ----------------------
    # ON THE STACKS. Routed up the wall the way this first shipped, both tendrils
    # crossed a lit lancet and read as cracks in the glass.
    _vine(sp, [(BREAST[0] - 10, H - 16), (BREAST[0] - 4, 150), (BREAST[0] - 11, 116)])
    _vine(sp, [(BREAST[1] + 10, H - 16), (BREAST[1] + 4, 152), (BREAST[1] + 11, 118)])
    _vine(sp, [(WX0 + 2, H - 18), (WX0 + 7, FY + 24), (WX0 + 1, FY + 6)])
    _vine(sp, [(WX1 - 2, H - 18), (WX1 - 8, FY + 28), (WX1 - 1, FY + 8)])
    _leaf_dab(sp, PX0 - 7, H - 22)
    _leaf_dab(sp, PX1 + 7, H - 24)

    edge(sp, H)
    clipw(sp, W)
    return _finish(sp, S(W, H, salt + 1), W, FY, H, composite, frames, _keep_anim)


def _wing_anim(still):
    """Both wings' lit windows, and the still-house's two flues.

    Returns the closure `_finish` wants, because WHICH WING IT IS has to reach the
    animator: only the still-house has chimneys, and a shared animator that does
    not know that is exactly how the observatory ended up smoking.

    THE OLD VERSION OF THIS FUNCTION IS WHY THE USER SAW SMOKE COMING OUT OF
    NOTHING. It read:

        _anim_building(facade, canopy, f,
                       flues=((100, dy), (116, dy)),
                       windows=((18, 58 + dy, 12, 14), ...))

    Three separate faults in three lines, and each one is invisible in the code:
      1. `dy` was baked INTO the coordinates instead of being passed on as
         `dy=dy`, so every position was off by the pad;
      2. the flues were given to BOTH kinds, and the observatory has no chimney
         anywhere on it — two plumes rose out of clear sky above a dome;
      3. the still-house's own `_chimney` calls are at cx-30 and cx+26 (42 and
         98), which line up with neither 100 nor 116, so one plume floated and
         its left-hand flue never smoked at all.

    The rule the rest of the project keeps and this one broke: positions are
    sprite-local to the UNPADDED art, and `dy` is PASSED THROUGH.
    """
    def anim(facade, canopy, f, dy=0):
        _anim_building(facade, canopy, f, dy=dy,
                       windows=((20, 56, 22, 26), (102, 56, 22, 26)),
                       flues=(((30, 4), (110, 4)) if still else ()))
    return anim


def academy_wing(stone, salt=631, kind="observatory", composite=True, frames=8):
    """ONE WING of the back rank — 144x96 on a 9x6 footprint, flanking the keep on
    the lawns either side of the processional way.

    `kind` picks the CROWN and the roof furniture and nothing else:

      "observatory" — a VERDIGRIS dome on a drum, split by a shutter slit with a
                      brass refractor out of it. The Academy looking up.
      "still"       — a riveted copper boiler on a cradle with two flues venting.
                      The Academy's potion-craft, which is the one science that
                      looks enough like magic (DESIGN.md).

    ONE BUILDER AND ONE SALT FOR BOTH, deliberately: the facades come out
    byte-identical and only the crown rows differ.

    WHY THIS WAS REDRAWN. The first cut was a violet ashlar rectangle with three
    lit slots in it, a flat pale band for a roof, and no door — and it read, in
    the user's words, "very flat", which it was. Nothing on it overhung anything,
    so nothing cast a shadow on anything, so there was no second surface anywhere
    for the eye to catch. The cues below are in descending order of how much each
    one buys, and the first two are worth more than all the rest together:

      1. THE PORCH BAY standing proud of the wall, with the door in it and its
         own little pitch. One object that is demonstrably in front of another.
      2. THE DEEP EAVE and the shade band it throws down the wall. An eave that
         does not darken the wall under it is not an overhang, it is a line.
      3. THE BUTTRESSES at the corners, stepped, each with its own lit west face
         and dark east one — which also breaks the silhouette, so the building
         stops being a rectangle before you have read a single detail.
      4. Window HOODS and sills: every opening gets a lip above and a ledge
         below, so the glass sits in a hole rather than on a surface.
      5. A pitched roof with verge boards and a ridge, instead of a pale band.

    COVERAGE: 100% on the facade rows."""
    assert kind in ("observatory", "still"), f"unknown wing {kind!r}"
    w, h, fy = 144, 96, 46
    still = kind == "still"
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    cx = w // 2
    PLINTH, EAVE = h - 11, fy - 4
    RIDGE = 6                                              # the gable's ridge line
    BX0, BX1 = cx - 17, cx + 17                            # the porch bay

    # ---- 1. the plinth, and it steps out under the bay --------------------------------
    _ashlar(lo, 0, PLINTH, w - 1, h - 1, stone, salt, course=5, joint=13)
    lo.rect(0, PLINTH, w - 1, PLINTH, stone[0])
    lo.rect(0, h - 2, w - 1, h - 1, stone[5])
    lo.rect(BX0 - 4, PLINTH - 3, BX1 + 4, PLINTH - 1, stone[1])
    lo.rect(BX0 - 4, PLINTH - 3, BX1 + 4, PLINTH - 3, stone[0])

    # ---- 2. the wall ------------------------------------------------------------------
    _ashlar(lo, 0, fy, w - 1, PLINTH - 1, stone, salt, course=9, joint=18)
    lo.rect(0, fy, 0, PLINTH - 1, stone[1])
    lo.rect(w - 1, fy, w - 1, PLINTH - 1, stone[4])

    # ---- 3. THE TWO WINDOWS, in real reveals ------------------------------------------
    for wx in (22, 104):
        lo.rect(wx - 4, fy + 8, wx + 21, PLINTH - 6, stone[4])   # the reveal
        lo.rect(wx - 2, fy + 10, wx + 19, PLINTH - 8, WARMD)
        lo.blob(wx + 8.5, fy + 11.0, 11.0, 6.5, stone[4])        # the arched head
        lo.blob(wx + 8.5, fy + 12.5, 9.0, 5.0, WARMD)
        for gy in range(fy + 14, fy + 26, 3):                    # the throw, TOP THIRD
            lo.rect(wx - 1, gy, wx + 18, gy, WARM)               # only — see _lancet
        lo.rect(wx + 8, fy + 10, wx + 9, PLINTH - 8, stone[5])   # ONE mullion, so a
        for i in range(6):                                       # silhouette gets a
            lo.set(wx + 14 - i, fy + 16 + i, GLASS)              # whole pane to itself
        lo.rect(wx - 6, fy + 4, wx + 23, fy + 6, stone[1])       # the HOOD MOULD...
        lo.rect(wx - 6, fy + 4, wx + 23, fy + 4, stone[0])
        lo.rect(wx - 6, fy + 7, wx + 23, fy + 8, stone[4])       # ...and its shadow
        lo.rect(wx - 5, PLINTH - 5, wx + 22, PLINTH - 4, stone[0])   # the sill...
        lo.rect(wx - 5, PLINTH - 3, wx + 22, PLINTH - 3, stone[4])   # ...and its
        lo.rect(wx - 3, PLINTH - 2, wx + 20, PLINTH - 2, stone[4])   # own drip shade

    # ---- 4. THE BUTTRESSES ------------------------------------------------------------
    for bx, sgn in ((3, 1), (w - 12, -1)):
        for step, (sy, inset) in enumerate(((fy + 6, 3), (fy + 22, 1), (PLINTH, 0))):
            lo.rect(bx + inset, sy, bx + 8 - inset, h - 3, stone[2])
            lo.rect(bx + inset if sgn > 0 else bx + 8 - inset, sy,
                    bx + inset if sgn > 0 else bx + 8 - inset, h - 3,
                    stone[0] if sgn > 0 else stone[4])
            lo.rect(bx + inset, sy, bx + 8 - inset, sy, stone[1])   # the weathering
            lo.rect(bx + inset, sy + 1, bx + 8 - inset, sy + 1, stone[4])
        _shade_band(lo, bx + 9, fy + 6, bx + 14, h - 3, steps=1) if sgn > 0 else None
    lo.rect(0, h - 3, w - 1, h - 1, stone[5])

    # ---- 5. THE PORCH BAY and its door -------------------------------------------------
    _shade_band(lo, BX1 + 1, EAVE + 6, BX1 + 9, h - 4, steps=2)
    lo.tri((cx, EAVE - 14), EAVE + 2, BX0 - 6, BX1 + 6, stone)  # its own little pitch
    lo.rect(BX0 - 6, EAVE + 2, BX1 + 6, EAVE + 4, stone[1])
    lo.rect(BX0 - 6, EAVE + 2, BX1 + 6, EAVE + 2, stone[0])
    lo.rect(BX0 - 6, EAVE + 5, BX1 + 6, EAVE + 5, stone[4])
    _ashlar(lo, BX0, EAVE + 6, BX1, h - 4, stone, salt + 2, course=8, joint=16)
    lo.rect(BX0, EAVE + 6, BX0, h - 4, stone[0])
    lo.rect(BX1, EAVE + 6, BX1, h - 4, stone[4])
    dt, dsp = EAVE + 16, EAVE + 34                         # the door: arch on jambs
    lo.blob(cx, dsp, 14.0, dsp - dt, stone[3]); lo.rect(cx - 14, dsp, cx + 14, h - 4, stone[3])
    lo.blob(cx, dsp, 12.0, dsp - dt - 2, DOORDARK)
    lo.rect(cx - 12, dsp, cx + 12, h - 4, DOORDARK)
    for gy in range(dt + 8, h - 4, 5):
        lo.rect(cx - 12, gy, cx + 12, gy, stone[5])        # plank lines
    lo.rect(cx, dt + 4, cx, h - 5, stone[5])
    for sy_ in (dt + 12, dt + 24):
        lo.rect(cx - 11, sy_, cx + 11, sy_, IRON[3])
        for rx in range(cx - 9, cx + 10, 6):
            lo.set(rx, sy_, IRON[1])
    lo.blob(cx - 5, dt + 30, 2.4, 2.4, IRON[2]); lo.blob(cx + 5, dt + 30, 2.4, 2.4, IRON[2])
    lo.rect(cx - 18, h - 4, cx + 18, h - 3, stone[1])      # the worn step

    # ---- 6. THE EAVE and the shade it throws — the cue that was missing entirely -------
    lo.rect(0, EAVE, w - 1, EAVE + 2, stone[1])
    lo.rect(0, EAVE, w - 1, EAVE, stone[0])
    lo.rect(0, EAVE + 3, w - 1, EAVE + 3, stone[5])
    _shade_band(lo, 0, EAVE + 4, w - 1, EAVE + 10, steps=2)
    for bx in range(6, w - 6, 12):                         # a corbel table under it
        lo.rect(bx, EAVE - 3, bx + 3, EAVE - 1, stone[2])
        lo.set(bx, EAVE - 3, stone[0])
    edge(lo, h)

    # ---- 7. THE ROOF: a GABLE, full width, ridge across the top ------------------------
    # NOT a hipped trapezoid narrowing to a short ridge. That is the correct drawing
    # of a hip and it is the wrong building: it leaves the footprint's two BACK
    # CORNERS with no art on them at all, and a solid cell with no art rendering the
    # plain grass underlay next to walkable grass IS an invisible wall. Measured at
    # 0%, 0%, 6% and 9% across the block's top row — `_check_art.py` caught it the
    # first run after the academy was finally added to its MAPS table, which is the
    # whole argument for that table.
    #
    # A long hall's ridge runs the length of the building anyway, so the gable is
    # both the fix and the better architecture: full width at the ridge, verge boards
    # closing it at each end, and the dome or the boiler sitting ON it.
    for y in range(RIDGE, EAVE):
        u = (y - RIDGE) / float(max(1, EAVE - RIDGE - 1))
        c = stone[1] if u < 0.20 else stone[2] if u < 0.58 else stone[3]
        up.rect(1, y, w - 2, y, c)
        if int(u * 26) % 5 == 4:
            up.rect(1, y, w - 2, y, stone[4])              # lead roll seams
        up.set(1, y, stone[0]); up.set(w - 2, y, stone[4]) # the verge boards
    up.rect(1, RIDGE, w - 2, RIDGE + 1, stone[0])          # the ridge, catching sun
    up.rect(1, RIDGE + 2, w - 2, RIDGE + 2, stone[4])
    for rx in range(10, w - 10, 26):                       # ridge crestings
        up.rect(rx, RIDGE - 2, rx + 2, RIDGE - 1, stone[1])
    up.rect(0, EAVE - 1, w - 1, EAVE - 1, stone[5])

    # ---- 8. and the crown, which is the only thing the two kinds differ in -------------
    if not still:
        base = 30                                          # the dome sits ON the roof
        for y in range(base - 24, base):                   # THE VERDIGRIS DOME
            t = (base - y) / 24.0
            half = int(round(28 * (1.0 - t * t) ** 0.5))
            for x in range(cx - half, cx + half + 1):
                u = (x - (cx - half)) / float(max(2 * half, 1))
                up.set(x, y, VERDI[0] if u < 0.16 else VERDI[1] if u < 0.42 else
                             VERDI[2] if u < 0.68 else VERDI[3] if u < 0.87 else VERDI[4])
        for rr in (-18, -9, 0, 9, 18):                     # the dome's ribs
            for y in range(base - 24, base):
                t = (base - y) / 24.0
                half = 28 * (1.0 - t * t) ** 0.5
                x = cx + int(round(rr / 28.0 * half))
                if abs(rr) <= half:
                    up.set(x, y, VERDI[4])
        up.rect(cx - 29, base, cx + 29, base + 2, IRON[3])     # the turning ring
        up.rect(cx - 29, base, cx + 29, base, IRON[1])
        up.rect(cx - 3, base - 24, cx + 2, base, DOORDARK)     # the shutter, cranked
        up.rect(cx - 4, base - 24, cx - 4, base, VERDI[1])     # half open, and it has
        up.rect(cx + 3, base - 24, cx + 3, base, VERDI[4])     # been a long time
        # THE REFRACTOR sits IN the slit and leans only a little. Drawn as a long
        # tube climbing out of the top of the dome it ran off the canvas at
        # negative y and simply did not render — the same trap the cupola note in
        # the art-pipeline skill is about (a crown is drawn DOWN from the top).
        # Short and in the opening is also the better picture: what you see is the
        # instrument through the shutter, which is what a half-open dome shows.
        for i in range(11):
            up.rect(cx - 2 + i, base - 16 - i, cx + 1 + i, base - 14 - i, BRASSD[1])
            up.set(cx - 2 + i, base - 16 - i, BRASSD[0])
            up.set(cx + 1 + i, base - 14 - i, BRASSD[3])
        up.blob(cx + 10, base - 26, 2.6, 2.0, GLASS)
        up.set(cx, base - 9, MINT)                             # a light on inside
    else:
        base = 32
        up.capsule(cx - 21, base - 15, cx + 21, base - 15, 13.0, 13.0, COPPERD)
        for bx in (cx - 16, cx - 5, cx + 6, cx + 17):          # riveted straps, and
            up.rect(bx, base - 28, bx + 1, base - 3, IRON[2])  # they have to be
            up.rect(bx, base - 28, bx, base - 3, IRON[1])      # LEGIBLE: a plain
            up.rect(bx + 2, base - 28, bx + 2, base - 3, COPPERD[4])   # brown capsule
            for ry in range(base - 26, base - 4, 5):           # with faint marks on
                up.set(bx, ry, IRON[0])                        # it is a loaf of bread
        up.rect(cx - 24, base - 2, cx + 24, base, IRON[3])     # the cradle...
        up.rect(cx - 24, base - 2, cx + 24, base - 2, IRON[1])
        _shade_band(up, cx - 26, base + 1, cx + 26, base + 4, steps=2)  # ...and its shade
        up.blob(cx - 7, base - 22, 6.0, 3.4, COPPERD[0])       # the boiler's hot band
        up.blob(cx - 7, base - 23, 3.4, 1.8, SPEC)
        _valve(up, cx + 23, base - 18)
        # THE TWO FLUES. They are OUTBOARD of the boiler (which spans x 38..106) so
        # they stand clear of it instead of being drawn on its face, and they carry
        # 28px of real shaft so they read as chimneys — see _flue for what the first
        # attempt at this actually drew.
        for fx in (30, 110):
            _flue(up, fx, 4, 30, cast=stone)
    edge(up, EAVE)
    return _finish(lo, up, w, fy, h, composite, frames, _wing_anim(still))
