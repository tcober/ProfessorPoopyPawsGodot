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
from _sprites import Sprite
from _tilekit import (TIMBER, BRASS, STEEL, COPPER, IRON, STONER, GLASS, MINT,
                      VIOLETF, PAPER, PAPERD, RED, SPEC, WATER, OUTLINE, STEAM)

DOORDARK = (24, 18, 44, 255)      # an open doorway's inside
WARM = (255, 208, 120, 255)       # candlelight through glass
WARMD = (236, 156, 88, 255)
CRYSTAL = (150, 84, 210, 255)
# the drained-magic crystal ramp: hot facet -> deep violet root
CRYS = [(246, 232, 255, 255), (208, 148, 255, 255), (158, 92, 222, 255),
        (108, 54, 164, 255), (62, 28, 100, 255)]


def S(w, h=None, salt=0):
    """Footprint-sized sparse canvas (square Sprite; draw only in w x h)."""
    return Sprite(max(w, h or w), grain=1, salt=salt, jitter=0.0)


def ln(sp, x0, y0, x1, y1, c):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(int(steps) + 1):
        t = i / steps
        sp.set(round(x0 + (x1 - x0) * t), round(y0 + (y1 - y0) * t), c)


def edge(sp, h=None):
    """Uniform dark CT silhouette outline. Pass the footprint height `h` when
    it is shorter than the (square) canvas: outline() dilates 1px in every
    direction, and the row it writes at y=h would otherwise blit onto the
    walkable map cell SOUTH of the prop."""
    sp.outline({}, OUTLINE)
    if h is not None:
        for y in range(h, sp.n):
            sp.px[y] = [None] * sp.n


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


def cottage(w, h, roof, plaster, salt=101):
    """A townsfolk cottage, squat CT proportions (48x32: the hero stands more
    than half its height): broad hip roof, plaster-and-timber facade, an ajar
    doorway on the door-mouth cell, two cold mullioned windows, copper flue."""
    sp = S(w, h, salt)
    fy = 18                                                # facade top
    # facade
    sp.rect(0, fy, w - 1, h - 1, plaster[1])
    sp.rect(0, fy, 1, h - 1, TIMBER[3])                    # corner posts
    sp.rect(w - 2, fy, w - 1, h - 1, TIMBER[3])
    sp.rect(0, fy, w - 1, fy, TIMBER[1])                   # eave beam
    sp.rect(0, fy + 1, w - 1, fy + 1, TIMBER[3])
    sp.rect(2, h - 1, w - 3, h - 1, STONER[4])             # footing
    # the doorway, ajar: dark mouth, one leaf swung inward
    dx0, dx1 = w // 2 - 4, w // 2 + 3
    sp.rect(dx0 - 1, fy + 3, dx1 + 1, h - 1, TIMBER[4])    # casing
    sp.rect(dx0, fy + 3, dx1, fy + 4, TIMBER[1])           # lintel
    sp.rect(dx0, fy + 5, dx1, h - 1, DOORDARK)
    sp.rect(dx0, fy + 5, dx0 + 2, h - 1, TIMBER[2])        # the ajar leaf
    sp.rect(dx0 + 2, fy + 5, dx0 + 2, h - 1, TIMBER[4])
    sp.set(dx0 + 1, fy + 10, BRASS[1])
    # cold windows either side
    _window(sp, 4, fy + 4, 7, 8, GLASS, MINT)
    _window(sp, w - 11, fy + 4, 7, 8, GLASS, MINT)
    # roof over it all
    _hip_roof(sp, 0, w - 1, 0, fy - 1, w // 5, roof)
    _chimney(sp, w * 2 // 3 + 3, 2, fy + 1, cast=roof)
    sp.despeckle(2, 1)
    sp.cluster_shade([roof, plaster], passes=1)
    edge(sp, h)
    return sp


def home_cottage(w, h, roof, plaster, salt=103):
    """Basil's cottage — the hero house at the same squat scale: an OPEN
    candle-lit doorway (the door mouth walks down to the lab), a round brass
    porthole in the roof, warm lit windows and a hanging flask sign."""
    sp = S(w, h, salt)
    fy = 18
    sp.rect(0, fy, w - 1, h - 1, plaster[0])               # brighter plaster
    sp.rect(0, fy, 1, h - 1, TIMBER[3])
    sp.rect(w - 2, fy, w - 1, h - 1, TIMBER[3])
    sp.rect(0, fy, w - 1, fy, TIMBER[1])
    sp.rect(0, fy + 1, w - 1, fy + 1, TIMBER[3])
    sp.rect(2, h - 1, w - 3, h - 1, STONER[4])
    # the open doorway, centered on the walkable door cell (middle third)
    dx0, dx1 = w // 2 - 5, w // 2 + 4
    sp.rect(dx0 - 2, fy + 2, dx1 + 2, h - 1, TIMBER[3])    # casing
    sp.rect(dx0 - 1, fy + 2, dx1 + 1, fy + 3, TIMBER[1])   # lintel
    sp.rect(dx0, fy + 4, dx1, h - 1, DOORDARK)
    sp.rect(dx0 + 1, fy + 4, dx1 - 1, fy + 7, WARMD)       # lamplit inside
    sp.rect(dx0 + 2, fy + 5, dx1 - 2, fy + 6, WARM)
    sp.rect(dx0, h - 1, dx1, h - 1, WARMD)                 # light on the sill
    # warm windows
    _window(sp, 3, fy + 4, 7, 8, WARMD, WARM)
    _window(sp, w - 10, fy + 4, 7, 8, WARMD, WARM)
    # hanging flask sign by the door
    px = dx1 + 4
    sp.rect(px, fy + 2, px, fy + 7, IRON[2])               # bracket
    sp.rect(px - 1, fy + 2, px + 4, fy + 2, IRON[3])
    sp.rect(px + 1, fy + 4, px + 4, fy + 9, TIMBER[2])     # board
    sp.rect(px + 1, fy + 4, px + 4, fy + 4, TIMBER[1])
    sp.rect(px + 2, fy + 6, px + 3, fy + 8, MINT)          # the flask glyph
    sp.set(px + 2, fy + 5, PAPERD)
    # roof + the round brass porthole set into it
    _hip_roof(sp, 0, w - 1, 0, fy - 1, w // 5, roof)
    cx = w // 3
    for r, c in ((3.2, BRASS[3]), (2.2, BRASS[1]), (1.4, WARM)):
        sp.blob(cx, 9, r, r, c)                            # porthole
    sp.set(cx - 1, 8, SPEC)
    _chimney(sp, w * 3 // 4 + 1, 1, 8, cast=roof)
    sp.despeckle(2, 1)
    sp.cluster_shade([roof, plaster], passes=1)
    edge(sp, h)
    return sp


def school(w, h, roof, stone, salt=107):
    """The Alembic Academy — the wizarding school at the squat landmark scale
    (80x48): twin conical towers, a keep with the alchemical rose window,
    hanging violet banners, gear bosses, and a barred double door."""
    sp = S(w, h, salt)
    tw = 16                                                # tower width
    # keep body first
    kx0, kx1 = tw, w - tw - 1
    ky = 17
    _coursed_wall(sp, kx0, ky, kx1, h - 1, stone, salt=3, course=6)
    sp.rect(kx0, ky, kx1, ky, stone[1])                    # parapet line
    sp.rect(kx0, ky + 1, kx1, ky + 1, stone[3])
    sp.rect(kx0, h - 1, kx1, h - 1, stone[4])              # footing
    # keep roof + central finial
    _hip_roof(sp, kx0, kx1, 5, ky - 1, 10, roof)
    sp.rect(w // 2 - 3, 1, w // 2 + 2, 4, stone[2])        # spire drum
    sp.tri((w // 2 - 1, 0), 1, w // 2 - 4, w // 2 + 3, roof[1])
    sp.rect(w // 2 - 1, 0, w // 2, 0, BRASS[1])            # finial
    # the great rose window (the apparatus)
    cx, cy = w // 2 - 1, 24
    for r, c in ((6.4, BRASS[3]), (5.4, BRASS[1]), (4.6, GLASS)):
        sp.blob(cx, cy, r, r, c)
    sp.blob(cx, cy, 3.4, 3.4, MINT)
    sp.blob(cx, cy, 1.6, 1.6, VIOLETF)
    sp.rect(cx, cy - 4, cx, cy + 4, TIMBER[4])             # mullion cross
    sp.rect(cx - 4, cy, cx + 4, cy, TIMBER[4])
    sp.set(cx - 2, cy - 2, SPEC)
    # hanging banners
    for bx in (kx0 + 5, kx1 - 8):
        sp.rect(bx, 22, bx + 3, 33, VIOLETF)
        sp.rect(bx, 22, bx + 3, 22, CRYSTAL)
        sp.rect(bx + 1, 27, bx + 2, 27, CRYSTAL)           # device stripe
        sp.set(bx, 33, None)
        sp.set(bx + 3, 33, None)                           # swallowtail cut
    # gear bosses on the wall
    for gx in (kx0 + 10, kx1 - 9):
        sp.ball(gx, 39, 2.5, 2.5, BRASS, power=2.2)
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            sp.set(gx + dx, 39 + dy, BRASS[3])
        sp.set(gx, 39, TIMBER[5])
    # the barred great door, centered on the door-mouth cell
    dx0, dx1 = w // 2 - 8, w // 2 + 7
    sp.rect(dx0 - 1, 32, dx1 + 1, 33, stone[4])            # arch
    sp.rect(dx0 - 2, 34, dx1 + 2, h - 1, stone[4])         # arch ring
    sp.rect(dx0, 34, dx1, 35, stone[1])                    # keystone lit course
    sp.rect(dx0, 36, dx1, h - 1, TIMBER[3])                # the doors
    sp.rect(w // 2 - 1, 36, w // 2 - 1, h - 1, TIMBER[5])  # meeting stile
    for by in (39, 44):
        sp.rect(dx0, by, dx1, by, IRON[3])                 # iron straps
        for rx in range(dx0 + 1, dx1, 4):
            sp.set(rx, by, IRON[1])
    for hx in (w // 2 - 4, w // 2 + 2):
        sp.set(hx, 41, BRASS[1])                           # ring handles
        sp.set(hx, 42, BRASS[3])
    sp.set(w // 2 - 1, 37, MINT)                           # a seam of old magic
    sp.set(w // 2 - 1, 40, MINT)
    # towers last (they stand proud of the keep)
    for tx0 in (0, w - tw):
        sp.tri((tx0 + 7, 0), 10, tx0, tx0 + tw - 1, roof)  # shaded cone
        sp.rect(tx0 + 7, 0, tx0 + 8, 0, BRASS[1])
        sp.rect(tx0, 10, tx0 + tw - 1, 10, roof[4])        # eave line
        for y in range(11, h):                             # cylindrical shaft
            for x in range(tx0, tx0 + tw):
                t = 0.22 + 0.52 * ((x - tx0) / float(tw - 1))
                if (y - 11) % 6 == 5:
                    t += 0.22
                sp.set(x, y, sp.tone(stone, t, x, y, jitter=0.35))
            sp.set(tx0, y, stone[3])
            sp.set(tx0 + tw - 1, y, stone[4])
        for wy in (17, 32):                                # arrow slits, mint-lit
            sp.rect(tx0 + 7, wy, tx0 + 8, wy + 4, DOORDARK)
            sp.set(tx0 + 7, wy, MINT)
        sp.rect(tx0, h - 1, tx0 + tw - 1, h - 1, stone[4])
    sp.despeckle(2, 1)
    sp.cluster_shade([roof, stone], passes=1)
    edge(sp, h)
    return sp


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


def town_cluster(roof_a, roof_b, plaster, stone, salt=151):
    """Alembic Town as a CT-overworld ICON — one 128x96 composition over an
    8x6 solid footprint: a DENSE cluster of small overlapping roofs (openings
    are dabs — a town read from across the plain), the Academy's castle-keep
    at the back rank, the steamworks' copper drum venting a plume, a well and
    a market awning on the apron, and an open mouth in the huddle over the
    walkable D cell (map col 8 -> prop x 48..63) that travels INTO
    scene/alembic_town.tscn. Returns (lower, upper); upper is empty today
    (the old gate archway is gone — the mouth is just the gap)."""
    w, h = 128, 96
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    rd = [(240, 206, 160, 255), (228, 184, 136, 255), (212, 158, 116, 255),
          (184, 124, 100, 255), (146, 84, 90, 255), (104, 54, 74, 255)]
    # the dirt apron, an organic blob everything stands on
    wob = (0, 2, 3, 2, 1, 2, 4, 3, 1, 0, 2, 3, 4, 2, 1, 2)
    for y in range(24, h):
        f = (y - 24) / float(h - 24)
        half = 46 + 16 * f
        cx = 62
        xl = int(cx - half) + wob[y % 16] // 2
        xr = int(cx + half) - wob[(y + 7) % 16] // 2
        for x in range(max(2, xl), min(w - 3, xr + 1)):
            c = rd[1]
            if (x + y * 3) % 11 == 0:
                c = rd[2]
            if x in (xl, xl + 1) or x in (xr, xr - 1):
                c = rd[3] if (x + y) % 3 else rd[2]        # crumbled edge
            lo.set(x, y, c)
    for x in range(46, 66):                                # worn mouth run
        for y in range(84, h):
            lo.set(x, y, rd[1] if (x + y) % 7 else rd[0])
    # back rank: the Academy keep + the steamworks
    _keep(lo, 2, 6, 42, roof_b, stone)
    _boiler_house(lo, 98, 26, stone)
    # a SWARM of tiny houses (10-12px — well under the travel chibi, the CT
    # ratio) in eight painter ranks at ~6px pitch: every rank's roofs bury
    # most of the facades behind, so the town reads as one interlocked mass
    # of rooftops. The mouth stays open mid-front (x46-65) down to the worn
    # run at the D cell — no archway, just the gap in the huddle. Pointed
    # gables are always BLUE — a dark verdigris cone reads as a fir tree
    # from map distance; green stays on the rounded hip/side roofs.
    HOUSES = (
        (48, 20, 12, 11, "a", "hip", dict(flue=True)),     # A (steamed)
        (62, 20, 11, 10, "b", "gable", {}),
        (76, 20, 12, 11, "a", "side", {}),
        (42, 26, 11, 10, "b", "gable", {}),                # B
        (55, 26, 12, 11, "a", "hip", dict(lit=True)),
        (70, 26, 11, 10, "b", "gable", {}),
        (84, 26, 12, 11, "a", "side", dict(flue=True)),
        (28, 32, 12, 11, "a", "hip", {}),                  # C, onto the wall
        (46, 32, 11, 10, "b", "gable", {}),
        (60, 32, 12, 11, "a", "side", {}),
        (75, 32, 11, 10, "b", "gable", {}),
        (88, 32, 11, 11, "a", "hip", {}),
        (20, 38, 11, 11, "b", "gable", {}),                # D
        (34, 38, 12, 10, "a", "side", {}),
        (52, 38, 11, 10, "b", "gable", {}),
        (66, 38, 12, 11, "a", "hip", dict(lit=True)),
        (80, 38, 11, 10, "b", "gable", {}),
        (12, 44, 12, 11, "a", "hip", {}),                  # E, tower foot
        (28, 44, 11, 10, "b", "gable", {}),
        (46, 44, 12, 11, "a", "side", {}),
        (62, 44, 11, 11, "b", "gable", {}),
        (76, 44, 12, 10, "a", "hip", {}),
        (18, 50, 11, 10, "b", "gable", {}),                # F
        (33, 50, 12, 11, "a", "hip", dict(lit=True)),
        (52, 50, 11, 10, "b", "gable", {}),
        (68, 50, 12, 11, "a", "side", {}),
        (84, 50, 11, 11, "b", "gable", {}),
        (10, 57, 12, 11, "b", "hip", {}),                  # G, wall foot
        (26, 57, 11, 10, "a", "hip", {}),
        (64, 57, 11, 10, "b", "gable", {}),
        (78, 57, 12, 11, "a", "hip", {}),
        (18, 63, 11, 10, "b", "gable", {}),                # H, the front step
        (34, 63, 12, 11, "b", "hip", dict(lit=True)),
        (66, 63, 11, 10, "a", "hip", {}),
    )
    ramps = {"a": roof_a, "b": roof_b}
    for i, (hx, hy, hw, hh, rk, shape, kw) in enumerate(HOUSES):
        fx, fy2 = _house_stamp(lo, hx, hy, hw, hh, ramps[rk], plaster,
                               shape=shape, **kw)
        if i == 0:
            _steam(lo, fx, fy2, drift=1)
    # commons life in the open ground: a well by the mouth + a market awning
    lo.blob(52.5, 77, 3.4, 2.2, stone[2])                  # well ring
    lo.rect(50, 76, 55, 76, stone[1])
    lo.rect(51, 77, 54, 78, DOORDARK)
    lo.set(51, 77, WATER)
    for i in range(6):                                     # awning stripes
        lo.rect(90 + i, 62, 90 + i, 64, RED if (i // 2) % 2 == 0 else PAPER)
    lo.rect(90, 65, 90, 68, TIMBER[3])
    lo.rect(95, 65, 95, 68, TIMBER[3])
    lo.set(92, 65, MINT)                                   # flask on the counter
    lo.despeckle(2, 1)
    lo.cluster_shade([roof_a, roof_b, plaster, stone], passes=1)
    edge(lo, h)
    return lo, up


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


def giant_tree(f, trunk, grass, salt=181):
    """The ELDER TREE — a 64x96 landmark over a 4x6 grass footprint between
    the trail and the river, the plain's sense-of-scale anchor (5x the
    travel chibi): a crown of overlapping lambert-lit lobes with dark seam
    shadows, a bark-grooved trunk two cells wide, root flare gripping its
    own shadowed ground, a few pink blooms surviving in the old canopy.
    Same contract as the castle: pure landmark, solid cells."""
    w, h = 64, 96
    sp = S(w, h, salt)
    sp.blob(32, 89, 17, 4.5, grass[4])                     # canopy ground shadow
    sp.blob(32, 89, 11, 3.0, grass[5])
    for x1_, y1_, rt in ((14, 92, 2.0), (24, 94, 2.2),     # root flare
                         (42, 94, 2.2), (51, 91, 2.0)):
        sp.capsule(32, 84, x1_, y1_, 5.0, rt, trunk)
    sp.capsule(32, 86, 32, 48, 8.5, 5.5, trunk)            # the trunk
    for y in range(54, 89):                                # bark grooves
        for x in range(22, 43):
            if sp.get(x, y) is not None and (x + (y // 7)) % 5 == 0:
                sp.set(x, y, sp.tone(trunk, 0.84, x, y, jitter=0.4))
    for y in range(54, 85):                                # west rim light
        if sp.get(26, y) is not None:
            sp.set(26, y, trunk[1])
    # the crown: back lobes first, canopy masses overlapping forward
    for cx, cy, rx, ry, sh in ((18, 26, 13, 11, 0.10), (46, 24, 13, 11, 0.06),
                               (32, 15, 14, 11, -0.04), (12, 40, 10, 8, 0.16),
                               (52, 42, 9, 8, 0.14), (32, 34, 15, 12, -0.10)):
        sp.ball(cx, cy, rx, ry, f, sh=sh, power=2.2)
    for cx, cy in ((21, 28), (43, 26), (17, 44), (47, 44)):
        sp.blob(cx, cy, 3.5, 2.0, f[4])                    # lobe seam shadows
    sp.blob(32, 48, 12, 3.5, f[4])                         # crown underside
    sp.blob(32, 51, 8, 2.5, f[5])
    sp.blob(24, 9, 4.5, 2.5, f[0])                         # NW sun-catch
    sp.blob(12, 23, 3, 2, f[0])
    for bx, by in ((20, 18), (40, 12), (51, 31)):          # surviving blooms
        sp.set(bx, by, BLOOM)
    sp.set(21, 17, SPEC)
    sp.despeckle(2, 1)
    sp.cluster_shade([f, trunk], passes=2)
    edge(sp, h)
    return sp


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


def well(stone, salt=109):
    """The commons well: shingle cap, timber posts, stone ring, rope + pail."""
    sp = S(16, 16, salt)
    for y in range(9, 16):                                 # stone ring
        for x in range(2, 14):
            c = stone[2] if y < 12 else stone[3]
            if (x + y) % 5 == 0:
                c = stone[4]
            sp.set(x, y, c)
    sp.rect(2, 9, 13, 9, stone[1])                         # lit rim
    sp.rect(4, 10, 11, 11, DOORDARK)                       # the shaft
    sp.set(5, 10, WATER)
    sp.rect(2, 5, 3, 9, TIMBER[3])                         # posts
    sp.rect(12, 5, 13, 9, TIMBER[3])
    sp.tri((7, 0), 4, 0, 15, TIMBER[2])                    # little roof
    sp.rect(6, 0, 9, 0, TIMBER[1])
    sp.rect(7, 4, 7, 8, PAPERD)                            # rope
    sp.rect(6, 8, 8, 9, STEEL[2])                          # pail
    edge(sp)
    return sp


def lamp_post(salt=113):
    """Brass-caged street lamp; its halo rides the additive glow overlay."""
    sp = S(16, 16, salt)
    sp.rect(6, 13, 9, 14, IRON[3])                         # base
    sp.rect(5, 15, 10, 15, IRON[2])
    sp.rect(7, 4, 8, 13, IRON[2])
    sp.rect(7, 4, 7, 13, IRON[1])
    sp.rect(5, 0, 10, 0, BRASS[1])                         # cap
    sp.rect(5, 1, 10, 4, BRASS[3])
    sp.rect(6, 1, 9, 3, MINT)                              # the mantle
    sp.set(7, 1, SPEC)
    sp.set(4, 1, BRASS[2])
    sp.set(11, 1, BRASS[2])                                # cage arms
    edge(sp)
    return sp


def market_stall(w, h, salt=127):
    """A flask-seller's stall: striped awning over a timber counter."""
    sp = S(w, h, salt)
    sp.rect(1, 3, 2, 12, TIMBER[3])                        # posts
    sp.rect(w - 3, 3, w - 2, 12, TIMBER[3])
    for x in range(0, w):                                  # awning
        c = RED if (x // 4) % 2 == 0 else PAPER
        sp.rect(x, 0, x, 3, c)
        if x % 4 == 3:
            sp.set(x, 3, PAPERD)
    sp.rect(0, 4, w - 1, 4, TIMBER[4])                     # awning bar
    sp.rect(2, 8, w - 3, 8, TIMBER[1])                     # counter top
    sp.rect(2, 9, w - 3, 12, TIMBER[2])
    sp.rect(2, 12, w - 3, 12, TIMBER[4])
    gx = w // 2 - 4                                        # wares
    sp.rect(gx, 6, gx + 1, 7, MINT)
    sp.rect(gx + 3, 5, gx + 4, 7, VIOLETF)
    sp.set(gx + 6, 6, BRASS[1])
    sp.set(gx + 7, 7, BRASS[3])
    sp.rect(3, 13, 4, 15, TIMBER[4])                       # legs
    sp.rect(w - 5, 13, w - 4, 15, TIMBER[4])
    edge(sp, h)
    return sp
