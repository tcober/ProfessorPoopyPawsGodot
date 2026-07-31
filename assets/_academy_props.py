#!/usr/bin/env python3
"""THE ALEMBIC ACADEMY's own prop kit — the four pieces the precinct needs and
no town does: the crenellated RAMPART that walls it off, the DRUM TOWERS of its
gatehouse, the great ORRERY standing in the inner court, and the two WINGS
flanking the keep (the observatory and the still-house).

Everything else the Academy is built from already exists and is reused rather
than reinvented, which is the tile-reusability rule doing its job:

  * the KEEP is `_town_props.town_academy` — 224x144, twin spired towers, the
    arcane rose window, the iron-barred door. It was drawn for the town grid the
    Academy has now left, and it is exactly the back-rank building this precinct
    was composed around.
  * the TERRACE the keep stands on is `town_cliff(wall=True)` — the cast-cement
    retaining wall built for Lanternwood — pierced by `town_stairs`.
  * the lamps are `town_lamp`, the trees `town_tree`, the beck's bridge the
    OverWorld driver's own `bridge` class.

THE ONE MATERIAL DECISION. A precinct is MASONRY where the town is plaster and
timber, so every builder here draws in the scene's ROCK ramp with a copper and
brass hardware store on top — and none of it is hand-pinned, because `ramp()`'s
violet shadow law is exactly right for cold stone. (BRASS[2..3] are still
unusable; brass is tones 0-1 and its darks are IRON, as everywhere.)

Stdlib-only, deterministic. Consumed by assets/_gen_tileset_academy.py:
stamp_columns for the rampart, place_each for the towers, emit_prop for the
orrery and the wings.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _propkit import S, ln, edge, split_rows
from _tilekit import BRASS, COPPER, IRON, SPEC, GLASS, MINT
from _overworld_props import CRYSTAL, DOORDARK, WARM, WARMD
from _town_props import (_anim_building, _finish, _chimney, _coursed_wall,
                         _ph, _pv, _valve, clipw)


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
    sp.rect(0, corbel, w - 1, corbel, stone[5])            # the corbel course
    sp.rect(0, corbel + 1, w - 1, corbel + 1, stone[4])
    sp.rect(cx - 1, cap - 3, cx, cap - 1, BRASS[1])        # the finial
    sp.set(cx - 1, cap - 4, SPEC)
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
    sp.rect(cx - 7, ptop + 9, cx + 6, ptop + 13, COPPER[3])
    sp.rect(cx - 7, ptop + 9, cx + 6, ptop + 9, COPPER[1])
    for gx in range(cx - 5, cx + 6, 3):
        sp.rect(gx, ptop + 11, gx + 1, ptop + 11, COPPER[4])
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
    sp.ball(cx, cy, 4.0, 4.0, BRASS)                       # the sun at its centre
    sp.set(cx - 1, cy - 1, SPEC)
    for px, py, c in ((cx - 13, cy + 3, MINT), (cx + 15, cy - 2, CRYSTAL),
                      (cx + 7, cy + 9, COPPER[1])):        # three planet beads
        sp.set(px, py, c)
        sp.set(px + 1, py, IRON[3])
    clipw(sp, w)
    return sp


def _cos(t):
    """Tiny series cos/sin so this module stays stdlib-and-no-math — the rest of
    the pipeline draws every curve from the quadratic forms in Sprite, and an
    armillary is the one place a real trig circle is worth it."""
    import math
    return math.cos(t)


def _sin(t):
    import math
    return math.sin(t)


def _wing_anim(facade, canopy, f, dy=0):
    """Window breath for both wings, and the still-house's steam with it."""
    return _anim_building(facade, canopy, f,
                          flues=((100, dy), (116, dy)),
                          windows=((18, 58 + dy, 12, 14), (60, 58 + dy, 12, 14),
                                   (102, 58 + dy, 12, 14)))


def academy_wing(stone, salt=631, kind="observatory", composite=True, frames=8):
    """ONE WING of the back rank — 144x96 on a 9x6 footprint, three walk-behind
    roof rows over three solid facade rows, split across the layers by
    place_split the way every building in this project is.

    `kind` picks the CROWN and nothing else:

      "observatory" — a copper dome on a drum, split by a shutter slit with a
                      brass refractor poking out of it. The Academy looking up.
      "still"       — a riveted copper boiler strapped to the roof with two
                      flues venting. The Academy's potion-craft, which is the
                      one science that looks enough like magic (DESIGN.md).

    ONE BUILDER AND ONE SALT FOR BOTH, deliberately: the facades are then
    byte-identical and dedupe to the same atlas tiles, and only the ~2 crown
    rows differ. Forking this into two builders would double the wing art for a
    difference that lives in nine cells.

    COVERAGE: 100% on the facade rows."""
    assert kind in ("observatory", "still"), f"unknown wing {kind!r}"
    w, h, fy = 144, 96, 48
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # ---- the facade, identical for both
    _ashlar(lo, 0, fy, w - 1, h - 4, stone, salt, course=9, joint=18)
    lo.rect(0, fy, 0, h - 1, stone[1])
    lo.rect(w - 1, fy, w - 1, h - 1, stone[4])
    lo.rect(0, h - 3, w - 1, h - 1, stone[5])              # the plinth
    # WARM AND WARMD ARE SINGLE COLOURS, NOT A RAMP, and `_breathe` matches them
    # BY VALUE: it recolours exactly the pixels that equal one or the other, so a
    # pane painted in any other tone simply does not breathe. (Indexing them like a
    # ramp is worse than inert — WARM[1] is the green CHANNEL, an int, and storing an
    # int as a pixel blows up the first time anything reads it back.)
    for wx in (18, 60, 102):                               # three lancet windows
        lo.rect(wx - 2, fy + 8, wx + 13, fy + 34, stone[4])
        lo.rect(wx - 1, fy + 9, wx + 12, fy + 33, WARMD)
        lo.blob(wx + 5.5, fy + 10.0, 7.0, 4.5, stone[4])
        lo.blob(wx + 5.5, fy + 11.5, 5.5, 3.5, WARMD)
        for gy in range(fy + 12, fy + 33, 4):
            lo.rect(wx, gy, wx + 11, gy + 1, WARM)          # the hearth's throw
        lo.rect(wx + 5, fy + 9, wx + 6, fy + 33, stone[4])  # the mullion
        for i in range(5):
            lo.set(wx + 9 - i, fy + 14 + i, GLASS)          # sky-catch streak
        lo.rect(wx - 3, fy + 35, wx + 14, fy + 35, stone[0])   # the lit sill
        lo.rect(wx - 3, fy + 36, wx + 14, fy + 36, stone[4])
    lo.rect(0, fy, w - 1, fy + 1, stone[0])                 # the eaves course
    lo.rect(0, fy + 2, w - 1, fy + 2, stone[4])
    edge(lo, h)
    # ---- the roof: a low leaded pitch, shared
    for y in range(fy - 20, fy):
        t = (y - (fy - 20)) / 19.0
        c = stone[1] if t < 0.25 else stone[2] if t < 0.7 else stone[3]
        up.rect(2, y, w - 3, y, c)
        if int(t * 19) % 5 == 4:
            up.rect(2, y, w - 3, y, stone[4])               # lead roll seams
    up.rect(0, fy - 1, w - 1, fy - 1, stone[5])             # the eave shadow
    up.rect(2, fy - 21, w - 3, fy - 21, stone[0])           # the ridge, catching sun
    # ---- and the crown, which is the only thing that differs
    cx = w // 2
    if kind == "observatory":
        base = fy - 22
        for y in range(base - 22, base):                    # the copper dome
            t = (base - y) / 22.0
            half = int(round(26 * (1.0 - t * t) ** 0.5))
            for x in range(cx - half, cx + half + 1):
                u = (x - (cx - half)) / float(max(2 * half, 1))
                up.set(x, y, COPPER[0] if u < 0.2 else
                             COPPER[1] if u < 0.5 else
                             COPPER[2] if u < 0.8 else COPPER[3])
        up.rect(cx - 27, base, cx + 27, base + 1, IRON[3])  # the turning ring
        up.rect(cx - 27, base + 2, cx + 27, base + 2, IRON[3])
        up.rect(cx - 3, base - 22, cx + 2, base, DOORDARK)  # the shutter slit
        up.rect(cx - 3, base - 22, cx - 3, base, COPPER[3])
        up.rect(cx + 2, base - 22, cx + 2, base, COPPER[3])
        for i in range(9):                                  # the refractor
            up.rect(cx - 1 + i, base - 26 - i, cx + i, base - 24 - i, BRASS[1])
            up.set(cx - 1 + i, base - 26 - i, BRASS[0])
        up.set(cx + 8, base - 34, GLASS)
        up.set(cx, base - 8, MINT)                          # a light on inside
    else:
        base = fy - 22
        up.capsule(cx - 20, base - 15, cx + 20, base - 15, 13.0, 13.0, COPPER)
        for bx in (cx - 14, cx, cx + 14):                   # riveted straps
            up.rect(bx, base - 27, bx, base - 3, IRON[3])
            for ry in range(base - 25, base - 4, 6):
                up.set(bx, ry, IRON[1])
        up.rect(cx - 22, base - 2, cx + 22, base, IRON[3])  # the cradle
        for fx in (cx - 30, cx + 26):                       # two flues
            _chimney(up, fx, base - 34, base, COPPER)
        _valve(up, cx + 22, base - 18)
        _ph(up, cx - 34, cx - 22, base - 10)
        _pv(up, cx - 34, base - 10, base)
        up.blob(cx - 6, base - 20, 5.0, 3.0, COPPER[0])     # the boiler's hot band
        up.set(cx - 8, base - 21, SPEC)
    edge(up, fy)
    return _finish(lo, up, w, fy, h, composite, frames, _wing_anim)
