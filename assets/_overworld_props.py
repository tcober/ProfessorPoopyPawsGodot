#!/usr/bin/env python3
"""Overworld prop library — Alembic Town's buildings at CT-overworld detail.

Each building is a function returning a `_sprites.Sprite` (jitter=0: hard CT
band edges) sized to its map footprint in PIXELS; `TileScene.place()` blits it
over the grass underlay (None-tracked, so the meadow shows through the
silhouette). Steampunk-medieval per the design bible: pitched blue/green
shingle roofs, lavender plaster over timber frames, copper flues and brass
fittings, flask glints — candle-and-gear, never chrome. Squat CT proportions:
a 48x32 cottage stands ~1.8x the 24px travel chibi, so the hero reads big.

Never draw outside the (w, h) footprint — the Sprite may be bigger (it is
square) but the map owns the neighboring cells. `edge(sp, h)` clips the
outline dilation back to the footprint for props shorter than their canvas.

Stdlib-only, deterministic (fixed salts). Used by assets/_gen_tileset_overworld.py.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import lerp
from _tilekit import (TIMBER, BRASS, STEEL, COPPER, IRON, STONER, GLASS, MINT,
                      VIOLETF, PAPER, PAPERD, RED, SPEC, WATER, STEAM, ramp)
from _propkit import S, ln, edge, split_rows

DOORDARK = (24, 18, 44, 255)      # an open doorway's inside
WARM = (255, 208, 120, 255)       # candlelight through glass
WARMD = (236, 156, 88, 255)
CRYSTAL = (150, 84, 210, 255)
# the naturey-steampunk town vocabulary at ICON scale (matches the zone
# buildings since the 2026-07-15 direction): living leaf canopies over
# light-cement walls — same seeds as _town_props uses at zone scale
FOLIAGE = ramp((94, 162, 76), "violet", 6)
CEMENT = ramp((186, 190, 178), "violet", 6)
# the drained-magic crystal ramp: hot facet -> deep violet root
CRYS = [(246, 232, 255, 255), (208, 148, 255, 255), (158, 92, 222, 255),
        (108, 54, 164, 255), (62, 28, 100, 255)]


def _hatch_px(x, y, spacing=4, phase=0, diag=1):
    """Diagonal hatch predicate on ABSOLUTE sprite-canvas pixels — engraved
    shingle/strata/tooling linework for one-off prop compositions. Props are
    never atlas-deduped so absolute coords are fine HERE; the terrain kit
    has its own tile-local _hatch in _overworld_tiles.py. Keep the two
    separate: an absolute-position hatch reaching terrain code would
    silently multiply the atlas."""
    return (x + diag * y + phase) % spacing == 0


def _coursed_wall(sp, x0, y0, x1, y1, stone, salt=7, course=5, joint=9,
                  t0=0.30):
    """Dressed masonry: a continuous AO grade (lit high, darker at the
    foot), dithered mortar seams every `course` rows with offset head
    joints, and faint tooling hatch — replaces the flat fill + hairline
    modulo coursing everywhere stone gets laid. `t0` biases the whole face
    lighter (a sun-caught gatehouse) or darker."""
    hh = float(max(1, y1 - y0))
    for y in range(y0, y1 + 1):
        v = y - y0
        for x in range(x0, x1 + 1):
            t = t0 + 0.26 * (v / hh)
            if v % course == course - 1:
                t += 0.24                                  # mortar seam
            elif (x + (course - 2) * ((v // course) % 2)) % joint == 0:
                t += 0.17                                  # offset head joint
            elif _hatch_px(x + salt, y, 6, 0, -1):
                t += 0.07                                  # tooling marks
            sp.set(x, y, sp.tone(stone, t, x, y, jitter=0.4))


def _hip_roof(sp, x0, x1, y0, y1, ridge_half, roof, sh=0.0):
    """Pitched hip roof: hard ridge cap and hip edges (deliberate CT
    punctuation) over a continuously lambert-shaded slope — lit toward the
    NW light, graded darker down-slope and eastward, shingle courses one
    dithered step deeper, engraved course hatch across the mid-slope.
    Fills the trapezoid from ridge (y0) to eaves (y1). Negative sh biases
    the whole slope lighter (icon houses catching the map's light)."""
    cx = (x0 + x1) / 2.0
    full = (x1 - x0 + 1) / 2.0
    span = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        f = (y - y0) / span
        half = ridge_half + (full - ridge_half) * f
        xl, xr = round(cx - half), round(cx + half - 1)
        for x in range(xl, xr + 1):
            if y <= y0 + 1:
                c = roof[0]                                # ridge cap
            elif y >= y1 - 1:
                c = roof[4] if y == y1 else roof[3]        # eave shadow
            else:
                nx = (x - cx) / max(1.0, half)
                lam = -nx * 0.62 - (f - 0.35) * 0.55       # NW-lit slope
                t = 0.46 - lam * 0.38 + sh
                if (y - y0) % 5 == 4:
                    t += 0.24                              # shingle course
                elif f > 0.3 and _hatch_px(x, y, 4, 1, -1):
                    t += 0.12                              # course hatch
                c = sp.tone(roof, t, x, y, jitter=0.5)
        # hip edges
            if x in (xl, xr) and y > y0 + 1:
                c = roof[0] if x == xl else roof[4]
            sp.set(x, y, c)


def _window(sp, x, y, w, h, glass, glint):
    """Small mullioned window with real depth: timber frame, a recessed
    reveal (shadow along the inside right/bottom per the NW light), a
    diagonal sky-catch streak across the glass, and an asymmetric
    lit-to-shade sill."""
    sp.rect(x, y, x + w - 1, y + h - 1, TIMBER[4])
    sp.rect(x + 1, y + 1, x + w - 2, y + h - 3, glass)
    st = lerp(glass[:3], (255, 255, 250), 0.45) + (255,)
    for i in range(max(1, min(w - 4, h - 5))):             # sky-catch streak
        sp.set(x + w - 3 - i, y + 1 + i, st)
    sp.rect(x + w - 2, y + 1, x + w - 2, y + h - 3, TIMBER[5])   # reveal shade
    sp.rect(x + 1, y + h - 3, x + w - 2, y + h - 3, TIMBER[5])
    sp.rect(x + w // 2, y + 1, x + w // 2, y + h - 3, TIMBER[4])
    sp.rect(x + 1, y + h // 2, x + w - 2, y + h // 2, TIMBER[4])
    sp.set(x + 1, y + 1, glint)
    sp.rect(x - 1, y + h - 2, x + w, y + h - 1, TIMBER[1])   # sill
    sp.rect(x - 1, y + h - 1, x + w, y + h - 1, TIMBER[3])
    sp.set(x - 1, y + h - 2, TIMBER[0])                      # lit near end
    sp.set(x + w, y + h - 2, TIMBER[3])                      # shaded far end
    sp.set(x + w, y + h - 1, TIMBER[4])


def _chimney(sp, x, y0, y1, cast=None):
    """Copper flue with a brass rain cap — the steampunk tell. Pass the
    ramp of the roof it rises from as `cast` to throw the flue's shadow SE
    onto the shingles (recolors only already-filled pixels)."""
    if cast is not None:
        for i in range(4):
            for j in range(3 - (i + 1) // 2):
                px_, py_ = x + 4 + j, y1 - 3 + i
                if sp.get(px_, py_) is not None:
                    sp.set(px_, py_, cast[4])
    sp.rect(x, y0 + 1, x + 3, y1, COPPER[2])
    sp.rect(x, y0 + 1, x, y1, COPPER[1])
    sp.rect(x + 3, y0 + 1, x + 3, y1, COPPER[4])
    sp.rect(x - 1, y0, x + 4, y0, BRASS[1])
    sp.set(x, y0, BRASS[0])                                # lit cap edge
    sp.set(x - 1, y0 + 1, BRASS[3])
    sp.set(x + 4, y0 + 1, BRASS[3])


def _steam(sp, x, y, drift=1, big=False):
    """A rising steam plume: puffs shrink and drift as they climb. Lit PAPER
    lobe NW, STEAM body, PAPERD shade SE — drawn last so the vapor overlaps
    whatever roofline it rises past."""
    puffs = ((0, 0, 3.2), (2 * drift, -5, 2.6), (4 * drift, -9, 2.0),
             (6 * drift, -12, 1.3)) if big else \
            ((0, 0, 1.9), (drift, -4, 1.5), (2 * drift, -7, 1.0))
    for dx, dy, r in puffs:
        sp.blob(x + dx, y + dy, r + 0.5, r, STEAM)
        sp.blob(x + dx + r * 0.4, y + dy + r * 0.4, r * 0.55, r * 0.45, PAPERD)
        sp.blob(x + dx - r * 0.35, y + dy - r * 0.3, r * 0.6, r * 0.5, PAPER)


def _tiny_house(sp, x0, y0, w, h, roof, plaster, lit=False, shape="hip",
                flue=False):
    """One CT-density icon house: the ROOF owns ~70% of h; the facade is a
    4px sliver under the eave (three plaster rows + footing) with a 3px door
    dab and one 2x2 window — a town read from across the plain, all
    rooftops. shape: 'hip' | 'gable' (front-facing peak) | 'side'
    (horizontal ridge, for silhouette variety). A flue needs 5px of clear
    canvas above y0. Returns the flue mouth."""
    fy = y0 + h - 5                                        # the eave line
    x1, y1 = x0 + w - 1, y0 + h - 1
    sp.rect(x0, fy + 1, x1, y1, plaster[1])                # the facade sliver
    sp.rect(x0, fy + 1, x0, y1, plaster[0])                # NW-lit corner
    sp.rect(x1, fy + 1, x1, y1, plaster[3])
    sp.rect(x0 + 1, y1, x1 - 1, y1, STONER[4])             # footing
    if shape == "gable":                                   # front-facing peak,
        cx = x0 + w // 2                                   # blunted 2px so it
        sp.tri((cx, y0 + 2), fy - 1, x0, x1, roof, sh=-0.12)   # reads house
        ln(sp, cx, y0 + 2, x1, fy - 1, roof[4])            # east verge
        ln(sp, cx, y0 + 2, x0, fy - 1, roof[0])            # lit verge
    elif shape == "side":                                  # long horizontal
        _hip_roof(sp, x0, x1, y0 + 1, fy - 1,              # ridge = a wide-
                  max(4, w // 2 - 2), roof, sh=-0.10)      # crowned low hip
    else:
        _hip_roof(sp, x0, x1, y0, fy - 1, max(2, w // 6), roof, sh=-0.10)
    sp.rect(x0, fy, x1, fy, roof[4])                       # eave shadow line
    dx = x0 + w // 2                                       # the door dab
    sp.rect(dx - 1, fy + 1, dx + 1, y1 - 1, WARMD if lit else DOORDARK)
    if lit:
        sp.set(dx, fy + 1, WARM)
    if w >= 12:                                            # one window dab
        sp.rect(x0 + 2, fy + 1, x0 + 3, fy + 2, WARMD if lit else GLASS)
    fx = x0 + w * 2 // 3
    if flue:                                               # copper flue stub
        sp.rect(fx, y0 - 2, fx + 1, y0 + 2, COPPER[2])
        sp.rect(fx, y0 - 2, fx, y0 + 2, COPPER[1])
        sp.rect(fx - 1, y0 - 3, fx + 2, y0 - 3, BRASS[1])
    return fx, y0 - 5


def _stamp(dst, src, ox, oy):
    """Blit a sprite's non-empty pixels at an offset (painter's order)."""
    for y in range(src.n):
        row = src.px[y]
        for x in range(src.n):
            if row[x] is not None:
                dst.set(ox + x, oy + y, row[x])


def _house_stamp(lo, x0, y0, w, h, roof, plaster, lit=False, shape="hip",
                 flue=False):
    """One house drawn on its own margin canvas, hard-outlined, then stamped
    into the cluster — the 1px rim is what makes a front roof visibly
    OCCLUDE the facade behind it: the CT roof-stacking read."""
    M = 5                                                  # flue headroom
    hs = S(w + 2, h + M + 1, salt=x0 * 31 + y0)
    fx, fy2 = _tiny_house(hs, 1, M, w, h, roof, plaster, lit=lit,
                          shape=shape, flue=flue)
    edge(hs)
    _stamp(lo, hs, x0 - 1, y0 - M)
    return x0 - 1 + fx, y0 - M + fy2


def _keep(sp, x0, y0, w, roof, stone):
    """The Academy as the town's castle-keep: twin conical towers with
    violet pennants over a crenellated curtain wall, the rose window
    burning in the middle — the icon's back rank."""
    tw = 10
    wy, base = y0 + 24, y0 + 48
    # curtain wall between the towers
    _coursed_wall(sp, x0 + 2, wy, x0 + w - 3, base, stone, salt=5,
                  course=5, joint=7)
    sp.rect(x0 + 2, base, x0 + w - 3, base, stone[4])
    for x in range(x0 + 2, x0 + w - 2):                    # crenellation
        sp.set(x, wy, stone[1])
        if ((x - x0) // 2) % 2 == 0:
            sp.set(x, wy - 1, stone[1])
            sp.set(x, wy - 2, stone[0])
    cx = x0 + w // 2                                       # the rose window
    for r, c in ((3.6, BRASS[1]), (2.4, GLASS)):
        sp.blob(cx, wy + 10, r, r, c)
    sp.blob(cx, wy + 10, 1.2, 1.2, MINT)
    sp.set(cx - 1, wy + 9, SPEC)
    for bx in (x0 + 7, x0 + w - 10):                       # hanging banners
        sp.rect(bx, wy + 3, bx + 2, wy + 11, VIOLETF)
        sp.rect(bx, wy + 3, bx + 2, wy + 3, CRYSTAL)
        sp.set(bx + 1, wy + 7, CRYSTAL)                    # device stripe
        sp.set(bx, wy + 11, None)
        sp.set(bx + 2, wy + 11, None)                      # swallowtail cut
    for tx0 in (x0, x0 + w - tw):                          # the twin towers
        cxt = tx0 + tw // 2
        for y in range(y0 + 12, base + 1):                 # cylindrical shaft
            for x in range(tx0, tx0 + tw):
                t = 0.20 + 0.54 * ((x - tx0) / float(tw - 1))
                if (y - y0) % 6 == 5:
                    t += 0.22
                sp.set(x, y, sp.tone(stone, t, x, y, jitter=0.35))
        sp.rect(tx0, base, tx0 + tw - 1, base, stone[4])
        sp.tri((cxt, y0 + 4), y0 + 12, tx0 - 1, tx0 + tw, roof)   # shaded cone
        sp.rect(tx0 - 1, y0 + 12, tx0 + tw, y0 + 12, roof[4])
        sp.set(cxt, y0 + 3, BRASS[1])                      # finial
        sp.rect(cxt, y0, cxt, y0 + 2, IRON[1])             # pennant pole
        for i in range(3):
            sp.rect(cxt + 1, y0 + i, cxt + 4 - i, y0 + i, VIOLETF)
        for sy in (y0 + 20, y0 + 32):                      # mint-lit slits
            sp.rect(cxt - 1, sy, cxt - 1, sy + 3, DOORDARK)
            sp.set(cxt - 1, sy, MINT)


def _boiler_house(sp, x0, y0, stone):
    """The town steamworks: a slate-roofed shed feeding a riveted vertical
    copper boiler with brass hoops, a mint gauge and the tall flue — the
    plume the whole plain can read. THE boiler on the horizon."""
    sx1 = x0 + 28
    _coursed_wall(sp, x0, y0 + 24, sx1, y0 + 33, stone, salt=17, course=4,
                  joint=6)                                 # the shed wall
    sp.rect(x0, y0 + 33, sx1, y0 + 33, stone[4])
    for x in range(x0 - 1, sx1 + 2):                       # its slate roof strip
        sp.set(x, y0 + 21, stone[1])
        sp.set(x, y0 + 22, stone[2])
        sp.set(x, y0 + 23, stone[4])
    mx = x0 + 5                                            # firebox mouth
    sp.rect(mx, y0 + 29, mx + 4, y0 + 33, IRON[3])
    sp.rect(mx + 1, y0 + 30, mx + 3, y0 + 33, DOORDARK)
    sp.rect(mx + 1, y0 + 32, mx + 3, y0 + 33, WARMD)       # banked coals
    sp.set(mx + 2, y0 + 31, WARM)
    cx = x0 + 18                                           # the boiler: a riveted
    bx0, bx1 = cx - 7, cx + 7                              # vertical cylinder
    for y in range(y0 + 8, y0 + 26):                       # rounded via tone
        for x in range(bx0, bx1 + 1):
            t = 0.16 + 0.60 * ((x - bx0) / float(bx1 - bx0))
            sp.set(x, y, sp.tone(COPPER, t, x, y, jitter=0.35))
    sp.rect(bx0, y0 + 8, bx0, y0 + 25, COPPER[0])          # lit seam
    sp.rect(bx1, y0 + 8, bx1, y0 + 25, COPPER[4])
    for y in range(y0 + 4, y0 + 8):                        # crowned dome top
        sq = ((y - (y0 + 8)) / 4.0) ** 2
        hw = int(7.5 * (1.0 - sq) ** 0.5)
        for x in range(cx - hw, cx + hw + 1):
            u = x - (cx - hw)
            c = COPPER[1] if u < hw * 2 // 3 else COPPER[2]
            sp.set(x, y, c)
    for hy in (y0 + 10, y0 + 20):                          # brass hoops
        sp.rect(bx0, hy, bx1, hy, BRASS[1])
        sp.rect(bx0, hy + 1, bx1, hy + 1, BRASS[3])
        for x in range(bx0 + 1, bx1, 3):
            sp.set(x, hy, IRON[3])                         # rivet studs
    sp.blob(cx - 2, y0 + 15, 2.2, 2.2, BRASS[1])           # the gauge
    sp.blob(cx - 2, y0 + 15, 1.0, 1.0, MINT)
    sp.set(cx - 3, y0 + 14, SPEC)
    fx = cx + 4                                            # flue + plume
    sp.rect(fx, y0 - 2, fx + 1, y0 + 4, COPPER[2])
    sp.rect(fx, y0 - 2, fx, y0 + 4, COPPER[1])
    sp.rect(fx - 1, y0 - 3, fx + 2, y0 - 3, BRASS[1])
    _steam(sp, fx + 1, y0 - 7, drift=-1, big=True)


def _path(lo, pts, rd):
    """A thin trodden path ribbon through the given points — flat ground art
    (the icon sits on the GRASS underlay now; the old full dirt apron read
    as a desert patch from map distance)."""
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(steps) + 1):
            t = i / steps
            cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for dy in (-1, 0, 1):
                for dx in (-2, -1, 0, 1, 2):
                    if dx * dx + dy * dy * 3 <= 4:
                        c = rd[1] if (int(cx + dx) + int(cy + dy) * 3) % 7                             else rd[2]
                        lo.set(cx + dx, cy + dy, c)


def _tiny_natur(lo, x0, y0, w, h, lit=False, flue=False):
    """One CT-density NATUREY icon house: a round living leaf-canopy (two
    lobes, under-rim, crown light) over a 4px cement facade sliver with a
    door dab, a window dab and an optional copper flue venting through the
    leaves — the zone's alchemist-botanist cottages read from across the
    plain. Returns the flue mouth."""
    M = 6
    hs = S(w + 4, h + M + 2, salt=x0 * 31 + y0)
    fy = M + h - 5
    x1 = 2 + w - 1
    hs.rect(2, fy + 1, x1, M + h - 1, CEMENT[1])           # facade sliver
    hs.rect(2, fy + 1, 2, M + h - 1, CEMENT[0])
    hs.rect(x1, fy + 1, x1, M + h - 1, CEMENT[3])
    hs.rect(3, M + h - 1, x1 - 1, M + h - 1, STONER[4])    # footing
    r = (h - 4) * 0.74                                     # the canopy
    cxa, cxb = 2 + w * 0.32, 2 + w * 0.68
    cy = M + (h - 5) * 0.40
    hs.ball(cxa, cy, r, r * 0.94, FOLIAGE, sh=0.05, power=2.1)
    hs.ball(cxb, cy - 1, r, r * 0.94, FOLIAGE, sh=-0.05, power=2.1)
    hs.blob(2 + w * 0.5, fy - 1, w * 0.46, 1.6, FOLIAGE[5])    # under-rim
    hs.blob(cxb - r * 0.3, cy - r * 0.55, r * 0.42, r * 0.30, FOLIAGE[0])
    hs.set(int(cxa - r * 0.4), int(cy - r * 0.5), FOLIAGE[1])  # leaf dapple
    hs.set(int(cxb + r * 0.2), int(cy + r * 0.3), FOLIAGE[4])
    dx = 2 + w // 2                                        # the door dab
    hs.rect(dx - 1, fy + 1, dx + 1, M + h - 2, WARMD if lit else DOORDARK)
    if lit:
        hs.set(dx, fy + 1, WARM)
    if w >= 11:                                            # one window dab
        hs.rect(4, fy + 1, 5, fy + 2, WARMD if lit else GLASS)
    fx = 2 + w * 2 // 3
    if flue:                                               # copper flue through
        hs.rect(fx, M - 4, fx + 1, M + 2, COPPER[2])       # the leaves
        hs.rect(fx, M - 4, fx, M + 2, COPPER[1])
        hs.rect(fx - 1, M - 5, fx + 2, M - 5, BRASS[1])
    edge(hs)
    _stamp(lo, hs, x0 - 2, y0 - M)
    return x0 + w * 2 // 3, y0 - M - 6


# lit-door glow dabs inside the icon (import target for the generator)
TOWN_DOORS = ((56, 30), (64, 38), (94, 44), (38, 56), (94, 63), (76, 74))


def town_cluster(roof_a, roof_b, plaster, stone, salt=151):
    """Alembic Town as a CT-overworld ICON, redrawn 2026-07-19 in the
    NATUREY-STEAMPUNK language the zone actually wears (the old pitched
    shingle-roof huddle predated the leaf-canopy direction): one 128x96
    composition over an 8x6 solid footprint — a swarm of tiny leaf-canopy
    cottages on open GRASS (no dirt apron; just a thin trodden path web),
    the Academy keep's towers capped leaf-green at the back rank, the
    steamworks' riveted copper boiler venting THE plume, a well and a
    market awning on the commons, and the open mouth in the huddle over
    the walkable D cell (map col 3 -> prop x 48..63) that travels INTO
    scene/alembic_town.tscn. (roof_a/roof_b/plaster are unused — the town
    is canopy-and-cement now; stone keeps the masonry.)"""
    w, h = 128, 96
    lo = S(w, h, salt)
    rd = [(240, 206, 160, 255), (228, 184, 136, 255), (212, 158, 116, 255),
          (184, 124, 100, 255), (146, 84, 90, 255), (104, 54, 74, 255)]
    # the trodden path web: mouth -> commons -> keep / boiler / west lanes
    _path(lo, ((56, 94), (56, 74), (56, 52)), rd)
    _path(lo, ((56, 74), (34, 62), (22, 46)), rd)
    _path(lo, ((56, 74), (82, 66), (102, 60)), rd)
    # back rank: the Academy keep (leaf-capped towers) + the steamworks
    _keep(lo, 2, 6, 42, FOLIAGE, stone)
    _boiler_house(lo, 98, 26, stone)
    # the cottage swarm, painter ranks; the mouth stays open (x46-65 front)
    HOUSES = (
        (50, 22, 13, 11, dict(lit=True, flue=True)),
        (66, 22, 12, 10, {}), (82, 24, 12, 10, {}),
        (30, 28, 12, 10, {}), (58, 30, 13, 11, dict(lit=True)),
        (74, 30, 12, 10, dict(flue=True)),
        (16, 34, 12, 10, {}), (42, 36, 13, 11, {}),
        (88, 36, 12, 11, dict(lit=True)),
        (24, 42, 12, 10, {}), (66, 42, 12, 10, {}),
        (12, 48, 12, 10, {}), (32, 48, 13, 11, dict(lit=True)),
        (78, 48, 12, 10, dict(flue=True)),
        (20, 56, 12, 10, {}), (68, 56, 13, 11, {}),
        (88, 56, 12, 10, dict(lit=True)),
        (30, 64, 12, 10, {}), (70, 66, 12, 10, dict(lit=True)),
    )
    for i, (hx, hy, hw, hh, kw) in enumerate(HOUSES):
        fx, fy2 = _tiny_natur(lo, hx, hy, hw, hh, **kw)
        if i == 0:
            _steam(lo, fx, fy2, drift=1)
    # commons life: a well by the mouth + the flask-market awning
    lo.blob(52.5, 79, 3.4, 2.2, stone[2])                  # well ring
    lo.rect(50, 78, 55, 78, stone[1])
    lo.rect(51, 79, 54, 80, DOORDARK)
    lo.set(51, 79, WATER)
    for i in range(6):                                     # awning stripes
        lo.rect(90 + i, 74, 90 + i, 76, RED if (i // 2) % 2 == 0 else PAPER)
    lo.rect(90, 77, 90, 80, TIMBER[3])
    lo.rect(95, 77, 95, 80, TIMBER[3])
    lo.set(92, 77, MINT)                                   # flask on the counter
    lo.despeckle(2, 1)
    lo.cluster_shade([FOLIAGE, CEMENT, stone], passes=1)
    edge(lo, h)
    return lo


def castle(roof, rock, salt=163):
    """The Capital's mountain-hold as a SMALL CT map icon: a ~46x54
    cluster centered in the 6x5 footprint, nestled into the massif — crag
    foot, squat curtain wall between two slim corner towers, the keep's
    cone rising behind, a small lit gate mouth, one steaming flue. The
    elements stay tiny (7px towers, a 3px gate) so the hold reads DISTANT
    and grand, never a walk-up building scaled up. Walls are pale STONER
    masonry so it pops off the violet massif."""
    w, h = 96, 80
    stone = STONER
    sp = S(w, h, salt)
    for y in range(56, 73):                                # the crag foot
        f = (y - 56) / 17.0
        xl, xr = int(30 - 10 * f), int(66 + 10 * f)
        for x in range(xl, xr + 1):
            c = rock[2]
            if (x * 3 + y) % 9 == 0:
                c = rock[3]
            if (x + y * 2) % 13 == 0:
                c = rock[1]
            if y > 69:
                c = rock[3] if (x + y) % 3 else rock[4]
            sp.set(x, y, c)
    # the keep behind: a compact block under the great cone
    _coursed_wall(sp, 41, 30, 55, 50, stone, salt=11, course=5)
    for wx in (44, 50):                                    # warm keep windows
        sp.rect(wx, 35, wx + 1, 37, DOORDARK)
        sp.rect(wx, 35, wx + 1, 36, WARM)
    sp.tri((48, 17), 30, 38, 58, roof)
    sp.rect(38, 30, 58, 30, roof[4])
    sp.set(48, 16, BRASS[1])                               # finial + pennant
    sp.rect(48, 13, 48, 15, IRON[1])
    for i in range(2):
        sp.rect(49, 13 + i, 51 - i, 13 + i, RED)
    # curtain wall + crenellation between the towers
    _coursed_wall(sp, 32, 48, 64, 60, stone, salt=13, course=4, joint=7)
    sp.rect(32, 60, 64, 60, stone[4])
    for x in range(32, 65):
        sp.set(x, 48, stone[1])
        if (x // 2) % 2 == 0:
            sp.set(x, 47, stone[0])
    for bx in (36, 58):                                    # hanging banners
        sp.rect(bx, 50, bx + 1, 55, VIOLETF)
        sp.set(bx, 50, CRYSTAL)
    # slim corner towers + cones
    for tx0 in (26, 64):
        cxt = tx0 + 3
        for y in range(40, 62):                            # cylindrical shaft
            for x in range(tx0, tx0 + 7):
                t = 0.22 + 0.50 * ((x - tx0) / 6.0)
                if (y - 40) % 5 == 4:
                    t += 0.20
                sp.set(x, y, sp.tone(stone, t, x, y, jitter=0.35))
        sp.rect(tx0, 62, tx0 + 6, 62, stone[4])
        sp.tri((cxt, 32), 40, tx0 - 1, tx0 + 7, roof)      # tower cone
        sp.rect(tx0 - 1, 40, tx0 + 7, 40, roof[4])
        sp.set(cxt, 31, BRASS[1])
        sp.rect(cxt, 28, cxt, 30, IRON[1])                 # pennant
        for i in range(2):
            sp.rect(cxt + 1, 28 + i, cxt + 3 - i, 28 + i, VIOLETF)
        sp.rect(cxt, 46, cxt, 48, DOORDARK)                # slit
        sp.set(cxt, 46, MINT)
    # the gate mouth (a sun-caught face proud of the wall)
    _coursed_wall(sp, 44, 52, 52, 64, stone, salt=19, course=4, joint=7,
                  t0=0.12)
    sp.rect(44, 52, 52, 52, stone[0])                      # lit parapet
    sp.rect(46, 56, 50, 64, stone[4])                      # arch ring
    sp.rect(47, 58, 49, 64, DOORDARK)                      # the mouth
    sp.rect(48, 59, 48, 63, BRASS[1])                      # portcullis bar
    for lx in (44, 52):                                    # gate lamps
        sp.set(lx, 58, WARM)
        sp.set(lx, 59, WARMD)
    fx = 60                                                # east-wing flue
    sp.rect(fx - 1, 42, fx, 48, COPPER[2])
    sp.rect(fx - 1, 42, fx - 1, 48, COPPER[1])
    sp.rect(fx - 2, 41, fx + 1, 41, BRASS[1])
    _steam(sp, fx, 37, drift=1)
    sp.despeckle(2, 1)
    sp.cluster_shade([roof, stone, rock], passes=1)
    edge(sp, h)
    return sp


def _crystal(sp, ax, ay, x0, x1, base_y):
    """One faceted drained-magic shard: lit west face, dark east arris."""
    sp.tri((ax, ay), base_y, x0, x1, CRYS[2])
    sp.tri((ax, ay), base_y, x0, ax, CRYS[1])
    ln(sp, ax, ay, x1, base_y, CRYS[3])
    ln(sp, ax, ay, x0, base_y, CRYS[0])
    sp.set(ax, ay, CRYS[0])
    sp.set(ax, ay + 1, CRYS[0])


def obelisk(salt=167):
    """THE DRAIN as a monument (48x64 over 3x4 waste cells): a great
    FACETED CRYSTAL obelisk over the burst that drank the world's magic;
    one shard still floats. Hard two-face shading on the CRYS ramp — lit
    west facet, deep east facet, bright rim — so it reads crystal at map
    zoom, not a smudged basalt stick. Its glow rides the additive
    overlay."""
    w, h = 48, 64
    sp = S(w, h, salt)
    for y in range(10, 54):                                # the tapered prism
        f = (y - 10) / 44.0
        cx = 26 - int(2 * f)
        hw = 2 + int(3.5 * f)
        for x in range(cx - hw, cx + hw + 1):
            if x < cx - hw // 2:
                c = CRYS[1]                                # lit west facet
            elif x <= cx:
                c = CRYS[2]
            else:
                c = CRYS[3]                                # deep east facet
            if (y - x) % 11 == 0 and x > cx:
                c = CRYS[4]                                # internal fracture
            sp.set(x, y, c)
        sp.set(cx - hw, y, CRYS[0])                        # bright rim
        sp.set(cx + hw, y, CRYS[4])                        # dark rim
    for i in range(4):                                     # the tip
        for x in range(26 - i, 26 + i + 1):
            sp.set(x, 6 + i, CRYS[1] if x <= 26 else CRYS[2])
    sp.set(26, 5, CRYS[0])
    sp.set(25, 6, SPEC)                                    # tip glint
    for ry in range(16, 50, 6):                            # rune score, west face
        f = (ry - 10) / 44.0
        sp.set(24 - int(2 * f), ry, MINT if (ry // 6) % 3 else CRYSTAL)
    # the crystal burst at its foot
    _crystal(sp, 33, 24, 28, 39, 56)
    _crystal(sp, 11, 32, 7, 16, 58)
    _crystal(sp, 20, 40, 17, 24, 60)
    _crystal(sp, 41, 44, 38, 45, 58)
    sp.set(32, 22, SPEC)                                   # facet catch
    for i, hw2 in enumerate((1, 2, 3, 2, 1)):              # the floating shard
        for x in range(40 - hw2 + 1, 40 + hw2):
            sp.set(x, 8 + i, CRYS[1] if x < 40 else CRYS[2])
    sp.set(39, 9, CRYS[0])
    sp.set(40, 7, SPEC)
    for x, y in ((5, 61), (14, 62), (26, 62), (36, 61), (44, 60)):
        sp.set(x, y, CRYS[4])                              # root rubble
    edge(sp, h)
    return sp


def crystal_outcrop(salt=173):
    """A drained-magic outcrop (32x32 over 2x2 waste cells): three shards
    leaning out of the cracked pan — the wastes' scatter landmark, big
    enough to read from the bridge."""
    sp = S(32, 32, salt)
    _crystal(sp, 11, 3, 8, 18, 26)                         # the big lean
    _crystal(sp, 23, 12, 20, 28, 28)
    _crystal(sp, 5, 16, 2, 9, 28)
    sp.set(10, 1, SPEC)
    for x, y in ((7, 29), (14, 30), (20, 30), (27, 29)):
        sp.set(x, y, CRYS[4])                              # root rubble
    sp.set(30, 27, CRYS[3])
    edge(sp)
    return sp


BLOOM = (255, 116, 176, 255)      # the scene's wild-flower hot pink


def home_tree(f, trunk, grass, salt=181):
    """THE HOME TREE — Basil's hermitage, grown to a true landmark (96x144
    over a 6x9 footprint on Forest Land's SE coast, ~6x the travel chibi,
    per the sketch): a great crown of overlapping lambert-lit lobes over a
    bark-grooved trunk that now carries an arched door spilling warm light,
    a round lit window, a hanging brass lantern, and a stub flue poking
    through the canopy with a lazy curl — somebody LIVES in there.
    Returns (lower, upper) split at px row 96 (the map's walkable G crown
    rows vs the trunk rows): the whole crown draws over the chibi — it
    ducks behind the canopy; only the 2x3 trunk-core cells block."""
    w, h = 96, 144
    sp = S(w, h, salt)
    sp.blob(48, 134, 26, 6.5, grass[4])                    # canopy ground shadow
    sp.blob(48, 134, 17, 4.2, grass[5])
    for x1_, y1_, rt in ((21, 138, 3.0), (34, 142, 3.3),   # root flare
                         (62, 142, 3.3), (76, 137, 3.0)):
        sp.capsule(48, 127, x1_, y1_, 7.5, rt, trunk)
    sp.capsule(48, 130, 48, 72, 13.0, 8.0, trunk)          # the trunk
    for y in range(82, 134):                               # bark grooves
        for x in range(33, 65):
            if sp.get(x, y) is not None and (x + (y // 7)) % 5 == 0:
                sp.set(x, y, sp.tone(trunk, 0.84, x, y, jitter=0.4))
    for y in range(82, 128):                               # west rim light
        if sp.get(39, y) is not None:
            sp.set(39, y, trunk[1])
    # the dwelling: an arched plank door set into the trunk base...
    sp.rect(43, 118, 53, 134, DOORDARK)
    sp.rect(44, 117, 52, 117, DOORDARK)                    # arch crown
    sp.rect(42, 118, 42, 134, trunk[1])                    # lit west jamb
    sp.rect(54, 118, 54, 134, trunk[4])
    for y in range(120, 134, 4):
        sp.rect(44, y, 52, y, TIMBER[4])                   # door planks
    sp.set(52, 127, BRASS[0])                              # brass knob
    sp.rect(45, 131, 51, 134, WARMD)                       # light under the door
    sp.rect(47, 132, 49, 133, WARM)
    # ...a round lit window up the trunk...
    sp.blob(56, 88, 3.4, 3.4, TIMBER[4])
    sp.blob(56, 88, 2.2, 2.2, WARMD)
    sp.set(56, 88, WARM)
    sp.set(55, 87, SPEC)
    # ...and a hanging lantern off a low west bough
    ln(sp, 34, 92, 28, 95, TIMBER[3])                      # bracket
    sp.set(28, 96, IRON[1])                                # chain link
    sp.rect(26, 97, 30, 102, BRASS[2])
    sp.rect(26, 97, 30, 97, BRASS[1])
    sp.rect(28, 98, 28, 101, WARM)
    # the crown: back lobes first, canopy masses overlapping forward
    for cx, cy, rx, ry, sh in ((27, 39, 19.5, 16.5, 0.10),
                               (69, 36, 19.5, 16.5, 0.06),
                               (28, 16, 10.0, 12.0, 0.04),
                               (66, 16, 10.0, 12.0, 0.10),
                               (48, 22, 21.0, 16.5, -0.04),
                               (18, 60, 15.0, 12.0, 0.16),
                               (78, 63, 13.5, 12.0, 0.14),
                               (48, 51, 22.5, 18.0, -0.10)):
        sp.ball(cx, cy, rx, ry, f, sh=sh, power=2.2)
    for cx, cy in ((31, 42), (64, 39), (25, 66), (70, 66)):
        sp.blob(cx, cy, 5.0, 3.0, f[4])                    # lobe seam shadows
    sp.blob(48, 72, 18.0, 5.0, f[4])                       # crown underside
    sp.blob(48, 76, 12.0, 3.7, f[5])
    sp.blob(36, 13, 6.7, 3.7, f[0])                        # NW sun-catch
    sp.blob(18, 34, 4.5, 3.0, f[0])
    for bx, by in ((30, 27), (60, 18), (76, 46)):          # surviving blooms
        sp.set(bx, by, BLOOM)
    sp.set(31, 26, SPEC)
    # the hermit's flue pokes through the canopy east, a lazy static curl
    sp.rect(70, 38, 71, 47, COPPER[2])
    sp.rect(70, 38, 70, 47, COPPER[1])
    sp.rect(69, 37, 72, 37, BRASS[1])
    sp.blob(73, 32, 2.2, 1.8, STEAM)
    sp.blob(72.5, 31.5, 1.2, 1.0, PAPER)
    sp.blob(76, 26, 1.6, 1.3, PAPER)
    # clip the two crown-top corner cells (round crown, square cells) one px
    # past the cell line so the outline dilation can't spill in
    for y in range(0, 17):
        for x in range(0, 17):
            sp.px[y][x] = None
        for x in range(79, w):
            sp.px[y][x] = None
    sp.despeckle(2, 1)
    sp.cluster_shade([f, trunk], passes=2)
    edge(sp, h)
    lo, up = split_rows(sp, 96)
    # mask band (the town _eave_lift idiom at chibi scale): a body pressed
    # against the trunk rows sinks its feet a few px into them — mirror the
    # rows' top onto the upper canvas so the crown swallows them
    for y in range(96, 108):
        for x in range(w):
            if lo.px[y][x]:
                up.px[y][x] = lo.px[y][x]
    return lo, up


def mountain_peak(rock, snow, salt=191):
    """THE HORN — an 80x64 summit at the massif's NW tip, rising behind the
    Capital's hold: three overlapping lambert-shaded facets, a permanent
    snowcap with wind-torn fingers, crevasse lines and strata hatch. The
    one summit that breaks the ridge rhythm — the range's sense of scale."""
    w, h = 80, 64
    sp = S(w, h, salt)
    sp.tri((52, 10), 62, 30, 78, rock, sh=0.10)            # east shoulder
    sp.tri((22, 16), 62, 2, 44, rock, sh=0.04)             # west shoulder
    sp.tri((38, 2), 63, 12, 66, rock)                      # the horn
    sp.tri((38, 2), 63, 12, 38, rock, sh=-0.18)            # its sunlit west face
    ln(sp, 38, 2, 20, 62, rock[0])                         # lit west arris
    ln(sp, 38, 2, 56, 63, rock[4])                         # shaded east arris
    for y in range(22, 60):                                # strata hatch
        for x in range(3, 78):
            if sp.get(x, y) is not None and _hatch_px(x, y, 7, 3, -1):
                sp.set(x, y, sp.tone(rock, 0.62, x, y, jitter=0.4))
    sp.tri((38, 2), 20, 25, 52, snow)                      # the snowcap
    for fx_, fy_ in ((28, 24), (33, 28), (38, 31),         # wind-torn fingers
                     (43, 27), (48, 23)):
        sp.rect(fx_, 19, fx_ + 1, fy_, snow[1])
        sp.set(fx_ + 1, fy_, snow[2])
    ln(sp, 37, 14, 32, 42, rock[4])                        # crevasses
    ln(sp, 40, 16, 46, 38, rock[5])
    for x, y in ((10, 58), (24, 61), (55, 60), (68, 57), (40, 62)):
        sp.set(x, y, rock[5])                              # base scree
    sp.despeckle(2, 1)
    sp.cluster_shade([rock, snow], passes=1)
    edge(sp, h)
    return sp


def lone_tree(f, salt=157):
    """A single CT plains tree in one 16px cell: round NW-lit crown over a
    stub trunk (the map's 't' cells, scattered via place_each). `f` is the
    scene's forest ramp so plains trees match the canopy masses."""
    sp = S(16, 16, salt)
    sp.rect(7, 11, 8, 15, TIMBER[3])                       # trunk
    sp.set(7, 11, TIMBER[2])
    sp.blob(7.5, 6, 6.2, 5.4, f[2])                        # crown
    sp.blob(6, 4.5, 3.6, 3.0, f[1])                        # lit lobe
    sp.blob(5, 3.5, 1.8, 1.4, f[0])
    for x, y in ((11, 8), (10, 9), (12, 7)):
        sp.set(x, y, f[3])                                 # SE shade
    sp.rect(4, 10, 11, 10, f[3])
    sp.set(6, 15, None)
    sp.set(9, 15, None)
    edge(sp)
    return sp


def _mountain_body(sp, rock):
    """THE BIG MOUNTAIN's massif body (224x160 over the 14x10 'B' footprint
    — it DOMINATES Mountain Land, per the sketch) — shared verbatim by both
    era toppers: same canvas salt + same body means the Ebb swap changes
    ONLY the summit. Two great shoulders under one vast cone, lit west
    arris, strata hatch, crevasses, base scree. The summit region above
    ~y58 belongs to the topper."""
    sp.tri((60, 52), 152, 4, 122, rock, sh=0.06)           # west shoulder
    sp.tri((164, 46), 152, 104, 220, rock, sh=0.14)        # east shoulder
    sp.tri((112, 12), 154, 24, 200, rock)                  # the great cone
    sp.tri((112, 12), 154, 24, 112, rock, sh=-0.16)        # sunlit west face
    ln(sp, 112, 12, 60, 150, rock[0])                      # lit west arris
    ln(sp, 112, 12, 168, 154, rock[4])                     # shaded east arris
    for y in range(46, 148):                               # strata hatch
        for x in range(6, 218):
            if sp.get(x, y) is not None and _hatch_px(x, y, 7, 3, -1):
                sp.set(x, y, sp.tone(rock, 0.62, x, y, jitter=0.4))
    ln(sp, 102, 40, 86, 112, rock[4])                      # crevasses
    ln(sp, 126, 44, 146, 108, rock[5])
    ln(sp, 76, 84, 70, 136, rock[5])
    ln(sp, 150, 80, 158, 132, rock[4])
    for x, y in ((16, 148), (52, 154), (112, 157), (172, 152), (204, 146)):
        sp.set(x, y, rock[5])                              # base scree


def big_mountain(rock, snow, salt=197):
    """THE BIG MOUNTAIN, pre-Ebb (224x160 over 'B'): the world's proudest
    summit at the heart of Mountain Land — the shared massif body under a
    deep permanent snowcap with wind-torn fingers. The overworld_bright
    generator places this; after the Ebb it becomes crystal_summit."""
    w, h = 224, 160
    sp = S(w, h, salt)
    _mountain_body(sp, rock)
    sp.tri((112, 12), 58, 74, 150, snow)                   # the great snowcap
    for fx_, fy_ in ((84, 68), (96, 78), (108, 86),        # wind-torn fingers
                     (120, 82), (132, 72), (144, 64)):
        sp.rect(fx_, 57, fx_ + 1, fy_, snow[1])
        sp.set(fx_ + 1, fy_, snow[2])
    sp.set(112, 11, snow[0])                               # sun-caught crest
    sp.set(110, 14, SPEC)
    sp.despeckle(2, 1)
    sp.cluster_shade([rock, snow], passes=1)
    edge(sp, h)
    return sp


def crystal_summit(rock, salt=197):
    """THE BIG MOUNTAIN, post-Ebb (224x160 over 'B'): the SAME massif body —
    same salt, byte-identical rock — but the summit is now the GIANT
    CRYSTAL the world's magic drained into on the night of the Ebb: a
    towering faceted prism seated in the cone's throat, side shards at the
    collar, dark crystal veins running down the slopes (their glow rides
    the additive overlay), and tiny shards floating around the tip."""
    w, h = 224, 160
    sp = S(w, h, salt)
    _mountain_body(sp, rock)
    for y in range(8, 79):                                 # the great prism
        f = (y - 8) / 70.0
        cx, hw = 112, 4 + int(20 * f)
        for x in range(cx - hw, cx + hw + 1):
            if x < cx - hw // 2:
                c = CRYS[1]                                # lit west facet
            elif x <= cx:
                c = CRYS[2]
            else:
                c = CRYS[3]                                # deep east facet
            if (y - x) % 13 == 0 and x > cx:
                c = CRYS[4]                                # internal fracture
            elif (x + 2 * y) % 19 == 0 and x < cx:
                c = CRYS[0]                                # inner fire vein
            sp.set(x, y, c)
        sp.set(cx - hw, y, CRYS[0])                        # bright rim
        sp.set(cx + hw, y, CRYS[4])                        # dark rim
    for i in range(8):                                     # the tip
        for x in range(112 - i // 2, 112 + i // 2 + 1):
            sp.set(x, i, CRYS[1] if x <= 112 else CRYS[2])
    sp.set(112, 0, CRYS[0])
    sp.set(111, 3, SPEC)                                   # tip glint
    for x in range(86, 139):                               # collar seat shadow
        if sp.get(x, 79) is not None:
            sp.set(x, 79, rock[5])
    _crystal(sp, 80, 52, 70, 93, 92)                       # collar shards
    _crystal(sp, 146, 56, 132, 158, 96)
    for pts in (((98, 82), (88, 108), (80, 140)),          # crystal veins down
                ((126, 82), (140, 104), (150, 136)),       # the slopes (glow
                ((112, 84), (108, 116), (102, 148))):      # dabs ride overlay)
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            ln(sp, xa, ya, xb, yb, CRYS[3])
        for (xa, ya) in pts[1:]:
            sp.set(xa, ya, CRYS[1])                        # lit vein nodes
    for fx_, fy_ in ((90, 16), (136, 22), (122, 6)):       # floating shards
        sp.set(fx_, fy_, CRYS[1])
        sp.set(fx_, fy_ - 1, CRYS[0])
    sp.despeckle(2, 1)
    sp.cluster_shade([rock, CRYS], passes=1)
    edge(sp, h)
    return sp


def _snowload(hs, snow):
    """Winterize a stamped icon piece: recolor each column's topmost filled
    rows to lying snow. Run per painter layer (before the next tier/rank
    draws over) so every exposed shoulder keeps its load."""
    for x in range(hs.n):
        for y in range(hs.n):
            if hs.get(x, y) is None:
                continue
            hs.set(x, y, snow[0])
            if hs.get(x, y + 1) is not None:
                hs.set(x, y + 1, snow[1] if x % 3 else snow[2])
            break


def _tiny_conifer(lo, cx, base_y, hh, f, snow, salt=3):
    """One icon-scale snow-laden spruce: three stacked shaded tiers, each
    snow-dusted before the next overlaps it, over a stub trunk."""
    n = hh + 6
    hs = S(n, n, salt=salt * 31 + cx)
    c, ty = n // 2, 3
    tiers = (((c, ty + int(hh * 0.30)), ty + hh, int(hh * 0.46), 0.10),
             ((c, ty + int(hh * 0.10)), ty + int(hh * 0.70), int(hh * 0.36), 0.0),
             ((c, ty), ty + int(hh * 0.42), int(hh * 0.24), -0.10))
    for (ax, ay), by, hw, sh in tiers:
        sp_hw = max(2, hw)
        hs.tri((ax, ay), by, c - sp_hw, c + sp_hw, f, sh=sh)
        _snowload(hs, snow)
    hs.rect(c - 1, ty + hh, c, ty + hh + 2, TIMBER[3])     # stub trunk
    edge(hs)
    _stamp(lo, hs, cx - c, base_y - (ty + hh + 3))


def lanternwood_cluster(roof, plaster, stone, f, snow, salt=223):
    """LANTERNWOOD as a CT-overworld ICON — one 128x96 composition over an
    8x6 solid footprint on the ice land: a quaint cluster of snow-laden
    cabin roofs nestled AMONG icon spruces on a wind-swept snow apron,
    every window and doorway burning warm (the town of lanterns read from
    across the sea), a bigger side-roofed hall at the back rank (the
    library), lantern posts flanking the open gate mouth over the walkable
    'd' cell (map col 3 of the block -> prop x 48..63), and a trodden snow
    run leading in. Same recipe as town_cluster — ranks of stamped pieces,
    painter order by y — just winterized."""
    w, h = 128, 96
    lo = S(w, h, salt)
    # the snow apron everything stands on
    wob = (0, 2, 3, 2, 1, 2, 4, 3, 1, 0, 2, 3, 4, 2, 1, 2)
    for y in range(22, h):
        f_ = (y - 22) / float(h - 22)
        half = 44 + 18 * f_
        xl = int(62 - half) + wob[y % 16] // 2
        xr = int(62 + half) - wob[(y + 7) % 16] // 2
        for x in range(max(2, xl), min(w - 3, xr + 1)):
            c = snow[1]
            if (x + y * 3) % 13 == 0:
                c = snow[0]
            elif (x * 3 + y) % 17 == 0:
                c = snow[2]
            if x in (xl, xl + 1, xr, xr - 1):
                c = snow[2] if (x + y) % 3 else snow[1]    # drifted edge
            lo.set(x, y, c)
    for x in range(46, 66):                                # trodden mouth run
        for y in range(84, h):
            lo.set(x, y, snow[2] if (x + y) % 5 else snow[3])
    # ranks, painter order: (kind, args...) sorted by ground line
    def cabin(x0, y0, cw, ch, shape, flue=False):
        M = 5
        hs = S(cw + 2, ch + M + 1, salt=x0 * 37 + y0)
        _tiny_house(hs, 1, M, cw, ch, roof, plaster, lit=True, shape=shape,
                    flue=flue)
        _snowload(hs, snow)
        fy = M + ch - 5                                    # icicles at the eave
        for x in range(2, cw, 5):
            if hs.get(x, fy) is not None:
                hs.set(x, fy + 1, snow[1])
        edge(hs)
        _stamp(lo, hs, x0 - 1, y0 - M)

    PIECES = (
        ("tree", (16, 20, 16)), ("cabin", (30, 14, 12, 11, "side", True)),
        ("tree", (98, 18, 18)),
        ("cabin", (48, 16, 20, 14, "side", True)),         # the library hall
        ("tree", (76, 24, 14)), ("cabin", (84, 20, 11, 10, "gable")),
        ("cabin", (20, 27, 12, 11, "gable", True)), ("tree", (40, 34, 15)),
        ("cabin", (56, 28, 11, 10, "gable")),
        ("cabin", (72, 30, 12, 11, "side", True)), ("tree", (106, 34, 16)),
        ("tree", (10, 40, 14)), ("cabin", (28, 40, 11, 10, "gable")),
        ("cabin", (58, 40, 12, 11, "side")), ("tree", (86, 42, 17)),
        ("cabin", (98, 44, 11, 10, "gable", True)),
        ("cabin", (14, 52, 12, 11, "gable", True)), ("tree", (34, 54, 15)),
        ("cabin", (50, 52, 11, 10, "gable")), ("tree", (70, 54, 13)),
        ("cabin", (82, 54, 12, 11, "side")),
        ("tree", (24, 66, 16)), ("cabin", (36, 62, 11, 10, "gable")),
        ("cabin", (68, 62, 12, 11, "gable", True)), ("tree", (92, 66, 14)),
        ("cabin", (16, 72, 11, 10, "gable")), ("tree", (40, 76, 13)),
        ("cabin", (72, 72, 11, 10, "gable")), ("tree", (86, 78, 15)),
    )
    def ground(p):
        if p[0] == "tree":
            return p[1][1] + 14                            # its stamped base
        return p[1][1] + p[1][3]                           # the facade foot
    for kind, a in sorted(PIECES, key=ground):
        if kind == "tree":
            _tiny_conifer(lo, a[0], a[1] + 14, a[2], f, snow, salt=a[0] + a[1])
        else:
            cabin(*a)
    for px_ in (46, 64):                                   # gate lantern posts
        lo.rect(px_, 78, px_, 83, TIMBER[3])
        lo.rect(px_ - 1, 75, px_ + 1, 77, BRASS[2])
        lo.rect(px_ - 1, 75, px_ + 1, 75, BRASS[1])
        lo.set(px_, 76, WARM)
        lo.set(px_, 74, snow[0])                           # snow on the cap
    lo.despeckle(2, 1)
    lo.cluster_shade([roof, plaster, stone, f, snow], passes=1)
    edge(lo, h)
    return lo
