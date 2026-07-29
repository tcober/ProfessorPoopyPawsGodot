#!/usr/bin/env python3
"""Alembic Town prop library — the overworld cluster's buildings at ZONE
scale (48px player), for assets/maps/town.txt. Same steampunk-medieval
vocabulary as assets/_overworld_props.py (whose drawing helpers this file
reuses), roughly 2x the overworld detail.

Every building returns a (lower, upper) Sprite pair for place_split: the
facade bakes UNDER entities, the roof (and the strip of wall/lintel above the
door mouth, which the 33px player's head overlaps when standing in the D
cell) rides OVER them — the walkable roof-row cells behind a house hide the
player, CT-style. Draw only inside the (w, h) footprint; edge()/clipw() trim
the outline dilation back to it.

Stdlib-only, deterministic (fixed salts). Used by assets/_gen_tileset_town.py.
"""
import math
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_props import (_hip_roof, _window, _chimney, _steam, _coursed_wall,
                              _hatch_px, DOORDARK, WARM, WARMD, CRYSTAL, BLOOM)
from _propkit import S, ln, edge
from _tilekit import (ramp, sprite_img, Img, TIMBER, BRASS, STEEL, IRON, COPPER,
                      STONER, GLASS, MINT, VIOLETF, PAPER, PAPERD, RED, SPEC,
                      WATER, STEAM, OUTLINE)

# naturey-steampunk building accents (living canopy + alchemist apparatus)
VERD = (86, 168, 150, 255)                        # verdigris on aged copper
VERDD = (54, 122, 116, 255)
FOLIAGE = ramp((94, 162, 76), "violet", 6)        # a living leaf canopy / plants
CEMENT = ramp((186, 190, 178), "violet", 6)       # light grey cement wall
WATERL = (196, 232, 226, 255)                     # lit water
SMOKEG = (198, 200, 212, 255)                     # winter woodsmoke, grey
SMOKEGD = (162, 164, 180, 255)
WGLINT = (255, 236, 170, 255)                     # a pane at the top of its breath

# The hearth BREATH (a fire-lit pane's soft pulsing glow). The glass body and
# the fire's throw band each climb their OWN warm ladder, one step per beat, so
# the swell reads as LIGHT rising and never as a hue slide; step 0 is the art as
# drawn, which keeps the baked still frame identical to the un-animated build.
WGLASS = (WARMD, (242, 172, 98, 255), (248, 186, 108, 255), (252, 198, 116, 255))
WTHROW = (WARM, (255, 218, 136, 255), (255, 228, 152, 255), WGLINT)
WIN_BLOOM = (0.0, 0.06, 0.14, 0.24)               # spill onto frame + logs
WIN_PULSE = (0, 1, 2, 3, 3, 2, 1, 0)              # ONE symmetric breath per
                                                  # 8-frame sheet: swell, hold,
                                                  # ebb, rest — no direction, so
                                                  # it can never read as travel


def _leaf_dab(sp, x, y):
    """A tiny 3px leaf clump for vines and canopy edges."""
    sp.set(x, y, FOLIAGE[2]); sp.set(x - 1, y, FOLIAGE[1]); sp.set(x, y + 1, FOLIAGE[4])


def _vine(sp, pts):
    """A climbing tendril through the given points, with leaves along it."""
    for i in range(len(pts) - 1):
        ln(sp, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], FOLIAGE[3])
    for (x, y) in pts[::2]:
        _leaf_dab(sp, x + 1, y)


def _pv(sp, x, y0, y1):                           # 2px vertical copper pipe
    sp.rect(x, y0, x + 1, y1, COPPER[2]); sp.rect(x, y0, x, y1, COPPER[1])
    sp.rect(x + 1, y0, x + 1, y1, COPPER[4])


def _ph(sp, x0, x1, y):                           # 2px horizontal copper pipe
    sp.rect(x0, y, x1, y + 1, COPPER[2]); sp.rect(x0, y, x1, y, COPPER[1])
    sp.rect(x0, y + 1, x1, y + 1, COPPER[4])


def _valve(sp, x, y):                             # a copper valve wheel at a joint
    sp.blob(x, y, 2.4, 2.4, COPPER[3]); sp.blob(x, y, 1.2, 1.2, COPPER[1])
    sp.set(x, y, BRASS[2]); sp.set(x - 3, y, COPPER[1]); sp.set(x + 3, y, COPPER[4])


def _clone(sp):
    """A pixel-copy of a Sprite (for building one animation frame off a base)."""
    c = S(sp.n, salt=sp.salt)
    c.px = [list(row) for row in sp.px]
    return c


## Clear-sky rows added ABOVE every animated building sheet: the plume's
## headroom. prop_spawner bottom-anchors the art at the footprint's south
## edge, so a taller sheet just extends upward — no map or manifest change.
SMOKE_PAD = 10


def _pad_top(sp, pad):
    """A pixel-copy with `pad` clear rows added above (the canvas grows by
    pad): sky the chimney smoke can rise into without clipping at y=0."""
    c = S(sp.n + pad, salt=sp.salt)
    for y, row in enumerate(sp.px):
        c.px[y + pad] = list(row) + [None] * pad
    return c


def _wash(c, t):
    """Blend a pixel t of the way toward candlelight — the spill a lit pane
    throws onto its own frame and the logs around it."""
    if c is None:
        return None
    a = c[3] if len(c) > 3 else 255
    return tuple(int(c[i] + (WARM[i] - c[i]) * t) for i in range(3)) + (a,)


def _breathe(sp, wx, wy, ww, hh, lvl):
    """One pane at breath level `lvl`: the glass steps up its ladder and the
    light spills two rings out onto the pane's frame and the logs. The BLOOM is
    what reads as a glow instead of a recolour — a pane that only changes
    colour reads as a lamp being switched, one that lights its surroundings
    reads as a fire breathing. Mullions stay dark: wood backlit by a hearth is
    a silhouette, and only the glass is the source."""
    for y in range(wy, wy + hh):
        for x in range(wx, wx + ww):
            c = sp.get(x, y)
            if c == WARMD:
                sp.set(x, y, WGLASS[lvl])
            elif c == WARM:
                sp.set(x, y, WTHROW[lvl])
    t = WIN_BLOOM[lvl]
    if t <= 0.0:
        return
    for d in (1, 2):                                      # concentric rings out
        td = t if d == 1 else t * 0.45                    # from the glass, the
        x0, x1 = wx - d, wx + ww - 1 + d                  # spill falling off
        y0, y1 = wy - d, wy + hh - 1 + d
        for x in range(x0, x1 + 1):
            for y in (y0, y1):
                sp.set(x, y, _wash(sp.get(x, y), td))
        for y in range(y0 + 1, y1):
            for x in (x0, x1):
                sp.set(x, y, _wash(sp.get(x, y), td))


def _anim_building(facade, canopy, f, flues=(), streams=(), basins=(),
                   barrels=(), drips=(), windows=(), wood_flues=(), dy=0):
    """Frame-f animated water + smoke for ANY building. `facade` takes the
    water, `canopy` the smoke — they are the same image when compositing one
    frame, or (lo, up) when baking frame 0. Positions are sprite-local to the
    UNPADDED art; `dy` is the _pad_top shift of a padded frame (every
    coordinate rides down with the art; the smoke needs the freed sky)."""
    for mx, my in flues:                                  # chimney smoke: puffs
        for p in range(3):                                # RISE off the cap and
            ph = (f - p) % 4                              # swell, wafting a px
            pr = 0.8 + 0.35 * ph                          # (needs SMOKE_PAD of
            canopy.blob(mx + 3.0 + (0.8 if ph % 2 else -0.4) + ph * 0.5,
                        my + dy - 1.5 - ph * 2.6,         # sky above the cap)
                        pr, pr * 0.9, PAPER if ph == 0 else STEAM)
    for sx, sy, slen in streams:                          # falling water columns
        for i in range(slen):
            lit = (i + f) % 2 == 0
            facade.set(sx, sy + dy + i, WATERL if lit else WATER)
            facade.set(sx + 1, sy + dy + i, WATER if lit else WATERL)
    for x0, x1, y in basins:                              # rippling surfaces
        for k in range(3):
            facade.set(x0 + (f * 4 + k * 5) % max(1, x1 - x0), y + dy, WATERL)
    for x0, x1, y in barrels:
        facade.set(x0 + (f * 3) % max(1, x1 - x0), y + dy, WATERL)
    for nx, ny in drips:                                  # falling drips
        facade.set(nx, ny + dy + (f % 4), WATER)
    lvl = WIN_PULSE[f % len(WIN_PULSE)]                   # fire-lit windows: ONE
    if lvl:                                               # hearth breath the whole
        for wx, wy, ww, hh in windows:                    # house shares. Panes are
            _breathe(facade, wx, wy + dy, ww, hh, lvl)    # IN PHASE — the old
                                                          # half-cycle offset and
                                                          # its corner-marching
                                                          # glint read as light
                                                          # ROLLING along the wall
    for mx, my in wood_flues:                             # winter woodsmoke:
        for p in range(5):                                # taller, lazier and
            ph = (f - p) % 4                              # greyer than steam —
            lift = ph + 4 * (p // 4)                      # the 5th puff rides
            pr = 0.80 + 0.24 * lift                       # a cycle higher and
            canopy.blob(mx + 1.5 + (0.9 if (p + ph) % 2 else -0.7)
                        + lift * 0.12,                    # swells as it goes
                        my + dy - 1.5 - lift * 1.9,
                        pr, pr * 0.95, SMOKEG if ph % 2 else SMOKEGD)


def _finish(lo, up, w, fy, h, composite, frames, anim, pad=SMOKE_PAD):
    """Shared building tail. Split mode (legacy) returns (lo, up) with frame
    0 baked. Composite (both towns) returns a horizontal frame-sheet padded
    SMOKE_PAD taller (clear sky for the rising plumes) if frames>1 and an
    anim(facade, canopy, f, dy) is supplied, else one Img."""
    animate = composite and frames > 1 and anim is not None
    if not animate:
        if anim is not None:
            anim(lo, up, 0)
        if not composite:
            _eave_lift(lo, up, w, fy, h=h)
            return lo, up
        return sprite_img(_flat(lo, up), w, h)
    base = _flat(lo, up)
    sheet = Img(w * frames, h + pad)
    for f in range(frames):
        frm = _pad_top(base, pad)
        anim(frm, frm, f, pad)
        sheet.blit_cell(frm, f * w, 0)
    return sheet


def _home_anim(facade, canopy, f, dy=0):
    _anim_building(facade, canopy, f, dy=dy,
                   flues=((27, 2), (66, 2)),              # = _canopy flue_xs, caps at y=2
                   streams=((39, 67, 6),),                # h-13
                   basins=((31, 44, 74),),                # h-6
                   barrels=((79, 89, 69),),               # h-11
                   drips=((12, 73), (22, 73), (36, 73), (70, 73), (84, 73)))


def _cottage_anim(facade, canopy, f, dy=0):
    _anim_building(facade, canopy, f, dy=dy, flues=((53, 2),),
                   barrels=((62, 73, 55),), drips=((10, 58),))


def _shop_anim(facade, canopy, f, dy=0):
    _anim_building(facade, canopy, f, dy=dy, flues=((66, 2),),
                   barrels=((78, 89, 55),))


def _inn_anim(facade, canopy, f, dy=0):
    _anim_building(facade, canopy, f, dy=dy, flues=((28, 2), (72, 2), (116, 2)),
                   basins=((45, 59, 73),), barrels=((120, 134, 69),),
                   drips=((10, 73),))


def _academy_anim(facade, canopy, f, dy=0):
    # geometry follows town_academy's 224x144 rebuild: flues sit on the canopy
    # BETWEEN the two spired towers, the basin and planters moved out with the
    # wider facade
    _anim_building(facade, canopy, f, dy=dy, flues=((86, 31), (138, 31)),
                   streams=((59, 136, 3),),               # riser spout -> the basin
                   basins=((57, 81, 137),),
                   drips=((152, 132), (168, 132)))        # nubs over the planters


# ---- shared naturey-building parts (canopy roof, cement wall, window, door) ----

def _canopy(up, w, fy, flue_xs=(), sx0=0, sx1=None, lobe=None, top=5.0):
    """A leafy canopy roof built from ROUND lobes of one size (keyed to roof
    HEIGHT — a wide building gets MORE lobes, never stretched ellipses), each
    lobe given its own under-arc shadow + crown highlight so the leaf masses
    read individually. The WHOLE silhouette stays >=1px inside every canvas
    edge, so edge() rings it completely (no half-outline that reads as a
    crop), and the top TOP px stay clear as headroom for the copper flue caps
    and their wind-swept smoke (animated later — never clipped)."""
    # sx0/sx1 confine the leaf mass to a SPAN of the building rather than its
    # whole width, `lobe` overrides the radius, and `top` drops the crown —
    # all three so the Academy's canopy can sit BETWEEN its towers and BELOW
    # their spires instead of swallowing them. Defaults reproduce the
    # original full-width canopy exactly (every other building relies on it).
    sx1 = w if sx1 is None else sx1
    TOP = top                                              # flue-cap/smoke headroom
    r = lobe if lobe else max(7.0, fy * 0.40)              # the one lobe radius
    crown, eave = [], []
    x0, x1 = sx0 + r * 1.05 + 1.0, sx1 - r * 1.05 - 1.0    # crown row (inset)
    nc = max(1, round(max(1.0, x1 - x0) / (r * 0.9)))
    for i in range(nc + 1):
        bx = x0 + (x1 - x0) * i / max(1, nc)
        crown.append((bx, TOP + r + (r * 0.18 if i % 2 else 0.0)))
    re = r * 0.80                                          # eave row (clamped inside)
    ex0, ex1 = sx0 + re + 1.5, sx1 - re - 2.5
    ne = max(1, round(max(1.0, ex1 - ex0) / (re * 1.05)))
    for i in range(ne + 1):
        eave.append((ex0 + (ex1 - ex0) * i / max(1, ne), fy - re * 0.55))
    for bx, by in crown:
        up.ball(bx, by, r, r, FOLIAGE, sh=-0.02, power=2.1)
    for bx, by in eave:
        up.ball(bx, by, re, re * 0.80, FOLIAGE, sh=0.08, power=2.2)
    # per-lobe under-arcs + crown highlights: each leaf mass reads round
    for bx, by in eave:
        up.blob(bx + re * 0.08, by + re * 0.40, re * 0.60, re * 0.26, FOLIAGE[4])
    for bx, by in crown:
        up.blob(bx + r * 0.08, by + r * 0.50, r * 0.60, r * 0.26, FOLIAGE[4])
        up.blob(bx - r * 0.36, by - r * 0.44, r * 0.32, r * 0.20, FOLIAGE[0])
    span = sx1 - sx0
    up.blob((sx0 + sx1) / 2.0, fy - 1.5, span * 0.47, 2.0, FOLIAGE[5])  # under-rim
    for i in range(max(8, span // 6)):                     # leaf-cluster dabs
        hx = sx0 + 4 + (i * 23) % max(1, span - 10)
        hy = int(TOP + 4 + (i * 11) % max(4, int(fy - TOP - 9)))
        if up.get(hx, hy) is not None and up.get(hx + 2, hy + 1) is not None:
            c, s = (FOLIAGE[1], FOLIAGE[4]) if i % 2 else (FOLIAGE[2], FOLIAGE[5])
            up.set(hx, hy, c); up.set(hx + 1, hy, c)
            up.set(hx + 1, hy + 1, s); up.set(hx + 2, hy + 1, s)
    for i in range(max(6, span // 10)):                    # single-pixel dapple
        hx = sx0 + (i * 29) % (span - 6) + 3
        hy = int(TOP + 2 + (i * 7) % max(4, int(fy - TOP - 8)))
        if up.get(hx, hy) is not None:
            up.set(hx, hy, FOLIAGE[1] if i % 2 else FOLIAGE[3])
    for fx in flue_xs:                                     # caps BELOW the top edge
        # keyed to TOP, not to y=0: a canopy slung lower (the Academy's, which
        # sits between its towers) would otherwise leave its flues floating in
        # the sky above the leaves. TOP=5 reproduces the original 2 .. 22.
        _chimney(up, fx, int(TOP) - 3, min(fy - 6, int(TOP) + 17))


def _cement_wall(lo, w, h, fy):
    """Greeny-light-cement facade base: fill, corner shade, canopy-shadow row +
    draping leaves, faint algae streaks, stone footing with moss."""
    lo.rect(0, fy, w - 1, h - 1, CEMENT[1])
    lo.rect(0, fy, 1, h - 1, CEMENT[3]); lo.rect(w - 2, fy, w - 1, h - 1, CEMENT[3])
    lo.rect(2, fy, w - 3, fy, FOLIAGE[4])                 # soft canopy shadow (inset
                                                          # to match the rounded eave)
    for dx in range(5, w - 4, 7):
        lo.set(dx, fy + 1, FOLIAGE[2]); lo.set(dx, fy + 2, FOLIAGE[3])
        if dx % 2:
            lo.set(dx, fy + 3, FOLIAGE[4])
    for mx in range(4, w - 3, 8):
        for my in range(fy + 6, h - 4, 5):
            lo.set(mx, my, CEMENT[3])
    lo.rect(2, h - 3, w - 3, h - 1, STONER[4])
    for mx in range(5, w - 4, 6):
        lo.set(mx, h - 3, FOLIAGE[3]); lo.set(mx + 1, h - 2, FOLIAGE[4])


def _wood_window(lo, x0, y0, ww, hh, plants=True):
    """A wood-framed greenhouse window; green sprigs grow inside if plants."""
    lo.rect(x0 - 1, y0 - 1, x0 + ww, y0 + hh, TIMBER[4])
    lo.rect(x0, y0, x0 + ww - 1, y0 + hh - 1, DOORDARK)
    lo.rect(x0, y0, x0 + ww - 1, y0, TIMBER[2])
    lo.rect(x0 - 2, y0 + hh, x0 + ww + 1, y0 + hh + 1, TIMBER[3])   # sill
    lo.rect(x0 + ww // 2, y0, x0 + ww // 2, y0 + hh - 1, TIMBER[4])
    lo.rect(x0, y0 + hh // 2, x0 + ww - 1, y0 + hh // 2, TIMBER[4])
    if plants:
        for i, px_ in enumerate(range(x0 + 1, x0 + ww - 1, 3)):
            lo.rect(px_, y0 + hh - 1 - (3 + i % 2), px_, y0 + hh - 1, FOLIAGE[2])
            _leaf_dab(lo, px_ + 1, y0 + hh - 3 - i % 2)


def _arch_door(lo, dx0, dx1, fy, h, warm=True):
    """An arched plank door under a copper arch, warm candle within if warm."""
    lo.rect(dx0 - 2, fy + 6, dx1 + 2, h - 1, TIMBER[4])
    for ay, ah in ((fy + 4, 0), (fy + 3, 2)):
        lo.rect(dx0 - 1 + ah, ay, dx1 + 1 - ah, ay, COPPER[2])
    lo.rect(dx0, fy + 6, dx1, h - 1, DOORDARK)
    if warm:
        lo.rect(dx0 + 2, fy + 9, dx1 - 2, fy + 13, WARMD)
        lo.rect(dx0 + 4, fy + 11, dx1 - 4, fy + 12, WARM)
        lo.rect(dx0, h - 1, dx1, h - 1, WARMD)
    for gy in range(fy + 8, h - 1, 4):
        lo.rect(dx0, gy, dx1, gy, TIMBER[5])


def clipw(sp, w):
    """Clear columns at x >= w — the sideways cousin of edge()'s row clip,
    for props narrower than their (square) canvas."""
    for y in range(sp.n):
        for x in range(w, sp.n):
            sp.px[y][x] = None


def _stone_courses(sp, x0, y0, x1, y1, stone):
    """Coursed masonry fill (the Academy's keep at zone scale) — the shared
    dressed-masonry treatment, at zone-scale course/joint periods."""
    _coursed_wall(sp, x0, y0, x1, y1, stone, salt=21, course=8, joint=12)


def _flat(lo, up):
    """Composite the UPPER canvas over LOWER and return LOWER — pixel-identical
    to how the two tile layers render (and to finish()'s --preview). Flattens a
    split building into ONE opaque feet-origin sprite for emit_prop (a Tier-3
    y-sorted World prop), which replaces place_split + the _eave_lift mask band:
    native y-sort sorts the whole building against a body at the front-wall
    baseline, so no pressed-body sliver survives to mask."""
    for y in range(len(up.px)):
        row = up.px[y]
        for x in range(len(row)):
            if row[x]:
                lo.px[y][x] = row[x]
    return lo


def _eave_lift(lo, up, w, fy, band=12, h=None, side=6):
    """Mirror a solid row's top pixels onto the UPPER canvas (pixel-identical
    composite): a body pressed against the row from the NORTH sinks its
    visual feet ~10px past its physics box into the row (plus sprite bottom
    and shadow), over the lower-layer art — the lifted band masks that
    sliver. A body pressed from the SOUTH is safe: its head tops out in the
    row's bottom ~3px, below a 12px band. Pass `h` to also mirror the
    facade's outer `side` columns down to the footing (the SIDE band,
    2026-07-12): a body pressed against the building's west/east face
    overlaps the wall edge at every height — its sliver reads as standing ON
    the corner without the mask. Call after edge(up, …) so the bands get no
    outline of their own (they must blend seamlessly). This is the ONLY
    legal way to put upper art on a body-adjacent solid row (see the z-order
    doctrine's mask-band rule)."""
    for y in range(fy, fy + band):
        for x in range(w):
            p = lo.px[y][x]
            if p:
                up.px[y][x] = p
    if h is None:
        return
    for y in range(fy, h):
        for x in list(range(side)) + list(range(w - side, w)):
            p = lo.px[y][x]
            if p:
                up.px[y][x] = p


def town_home(roof, plaster, salt=201, composite=False, frames=1):
    """Basil's alchemist-botanist cottage, 96x80 over a 6x5 footprint: an
    overgrown LIVING leaf-canopy roof with copper flues venting steam up
    through it; greeny-cement walls webbed in a twisty copper pipe network
    with valves that irrigates flower planters and a stone water-basin (a
    spout + a rain-barrel), wood greenhouse windows, an arched wood door and
    climbing vines. Minimal palette: cement-green / wood / copper / water /
    leaf. (`roof` and `plaster` params are ignored — the roof is a canopy, the
    wall is cement.)"""
    w, h, fy = 96, 80, 48
    dx0, dx1 = 47, 62                                      # arch over the D cell
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # ---- upper: the living leaf canopy (shared helper — rounded, never clips)
    _canopy(up, w, fy, flue_xs=(27, 66))
    edge(up, fy)
    # ---- lower: greeny-cement wall, twisty copper plumbing, running water
    lo.rect(0, fy, w - 1, h - 1, CEMENT[1])
    lo.rect(0, fy, 1, h - 1, CEMENT[3]); lo.rect(w - 2, fy, w - 1, h - 1, CEMENT[3])
    lo.rect(0, fy, w - 1, fy, FOLIAGE[4])                  # soft canopy shadow
    for dx in range(5, w - 4, 7):                          # leaves over the eave
        lo.set(dx, fy + 1, FOLIAGE[2]); lo.set(dx, fy + 2, FOLIAGE[3])
        if dx % 2:
            lo.set(dx, fy + 3, FOLIAGE[4])
    for mx in range(4, w - 3, 8):                          # damp algae streaks
        for my in range(fy + 6, h - 4, 5):
            lo.set(mx, my, CEMENT[3])
    lo.rect(2, h - 3, w - 3, h - 1, STONER[4])             # stone footing
    for mx in range(5, w - 4, 6):                          # moss
        lo.set(mx, h - 3, FOLIAGE[3]); lo.set(mx + 1, h - 2, FOLIAGE[4])

    def _gh(x0, y0, ww, hh):                               # wood greenhouse window
        lo.rect(x0 - 1, y0 - 1, x0 + ww, y0 + hh, TIMBER[4])
        lo.rect(x0, y0, x0 + ww - 1, y0 + hh - 1, DOORDARK)
        lo.rect(x0, y0, x0 + ww - 1, y0, TIMBER[2])
        lo.rect(x0 - 2, y0 + hh, x0 + ww + 1, y0 + hh + 1, TIMBER[3])  # sill
        lo.rect(x0 + ww // 2, y0, x0 + ww // 2, y0 + hh - 1, TIMBER[4])
        lo.rect(x0, y0 + hh // 2, x0 + ww - 1, y0 + hh // 2, TIMBER[4])
        for i, px_ in enumerate(range(x0 + 1, x0 + ww - 1, 3)):       # plants
            lo.rect(px_, y0 + hh - 1 - (3 + i % 2), px_, y0 + hh - 1, FOLIAGE[2])
            _leaf_dab(lo, px_ + 1, y0 + hh - 3 - i % 2)
    _gh(7, fy + 8, 15, 14)
    _gh(74, fy + 8, 14, 12)

    # arched wood door (copper arch) over the D cell, one warm glow
    lo.rect(dx0 - 2, fy + 6, dx1 + 2, h - 1, TIMBER[4])    # casing
    for ay, ah in ((fy + 4, 0), (fy + 3, 2)):              # copper arch head
        lo.rect(dx0 - 1 + ah, ay, dx1 + 1 - ah, ay, COPPER[2])
    lo.rect(dx0, fy + 6, dx1, h - 1, DOORDARK)
    lo.rect(dx0 + 2, fy + 9, dx1 - 2, fy + 13, WARMD)      # candlelight within
    lo.rect(dx0 + 4, fy + 11, dx1 - 4, fy + 12, WARM)
    lo.rect(dx0, h - 1, dx1, h - 1, WARMD)
    for gy in range(fy + 8, h - 1, 4):
        lo.rect(dx0, gy, dx1, gy, TIMBER[5])               # plank lines

    # the twisty copper pipe network
    _ph(lo, 4, w - 5, fy + 3)                              # header under the eave
    _pv(lo, 27, fy, fy + 3); _pv(lo, 66, fy, fy + 3)       # short flue drops
    for sx in (4, w - 6):                                  # jogged side-risers
        j = 5 if sx < 48 else -5
        _pv(lo, sx, fy + 3, fy + 13)
        _ph(lo, min(sx, sx + j), max(sx, sx + j), fy + 13)
        _pv(lo, sx + j, fy + 13, h - 9)
    for ax, bx in ((5, 23), (73, 90)):                     # arches over the windows
        _ph(lo, ax, bx, fy + 6); _pv(lo, ax, fy + 6, fy + 8); _pv(lo, bx, fy + 6, fy + 8)
    _pv(lo, 40, fy + 4, fy + 9); _ph(lo, 33, 41, fy + 9)   # a twisty centre feed
    _pv(lo, 33, fy + 9, fy + 15); _ph(lo, 33, 39, fy + 15)
    _pv(lo, 39, fy + 15, h - 13)
    _ph(lo, 8, 44, h - 9); _ph(lo, 64, w - 9, h - 9)       # low line, around the door
    for nx in (12, 22, 36, 70, 84):
        _pv(lo, nx, h - 9, h - 7)                          # drip-nub pipes (drips animated)
    for vx in (4, w - 6, 27, 66):
        _valve(lo, vx, fy + 3)

    # running water: a spout into a stone basin, left of the door
    bx0, bx1 = 30, 44
    lo.rect(bx0, h - 8, bx1, h - 3, STONER[3]); lo.rect(bx0, h - 8, bx1, h - 8, STONER[1])
    lo.rect(bx0 + 1, h - 7, bx1 - 1, h - 5, WATER); lo.rect(bx0 + 1, h - 7, bx1 - 1, h - 7, WATERL)
    lo.rect(39, h - 13, 40, h - 12, COPPER[3])             # spout nozzle (stream animated)
    rx0, rx1 = 78, 90                                      # wood rain-barrel
    lo.rect(rx0, h - 12, rx1, h - 3, TIMBER[3]); lo.rect(rx0, h - 12, rx1, h - 12, TIMBER[1])
    lo.rect(rx0, h - 12, rx1, h - 11, WATER); lo.rect(rx0, h - 11, rx1, h - 11, WATERL)
    for by in (h - 9, h - 5):
        lo.rect(rx0, by, rx1, by, TIMBER[5])

    # planters + climbing vines (the leafy overgrowth)
    for bx0 in (7, 74):
        for i, fx in enumerate(range(bx0 + 1, bx0 + 15, 4)):
            lo.rect(fx, h - 8, fx, h - 4, FOLIAGE[3])
            _leaf_dab(lo, fx - 1, h - 7); _leaf_dab(lo, fx + 1, h - 9)
    _vine(lo, [(3, h - 4), (7, fy + 26), (2, fy + 14), (6, fy + 3)])
    _vine(lo, [(w - 4, h - 6), (w - 9, fy + 24), (w - 3, fy + 12), (w - 8, fy + 3)])
    _vine(lo, [(24, h - 3), (27, fy + 30), (23, fy + 22)])
    _vine(lo, [(70, h - 3), (66, fy + 28), (71, fy + 22)])
    edge(lo, h)
    return _finish(lo, up, w, fy, h, composite, frames, _home_anim)


def town_cottage(roof, plaster, salt=211, composite=False, frames=1):
    """A townsfolk cottage in the naturey language: 80x64 (2 roof + 2 facade
    rows) — a small leaf canopy with one flue, greeny-cement walls, wood
    plant-windows, a copper pipe into a rain-barrel, an arched door, vines."""
    w, h, fy = 80, 64, 32
    dx0, dx1 = 33, 46                                      # arch over the D cell
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    _canopy(up, w, fy, flue_xs=(53,))
    edge(up, fy)
    _cement_wall(lo, w, h, fy)
    _wood_window(lo, 8, fy + 6, 13, 12)
    _wood_window(lo, 59, fy + 6, 12, 12)
    _arch_door(lo, dx0, dx1, fy, h)
    _ph(lo, 4, w - 5, fy + 3)                              # header
    _pv(lo, 4, fy + 3, h - 8); _valve(lo, 4, fy + 3)       # left riser
    _pv(lo, w - 6, fy + 3, h - 10); _valve(lo, w - 6, fy + 3)   # right riser
    rx0, rx1 = 62, 73                                      # rain-barrel
    lo.rect(rx0, h - 10, rx1, h - 3, TIMBER[3]); lo.rect(rx0, h - 10, rx1, h - 10, TIMBER[1])
    lo.rect(rx0, h - 10, rx1, h - 9, WATER); lo.rect(rx0, h - 9, rx1, h - 9, WATERL)
    lo.rect(rx0, h - 6, rx1, h - 6, TIMBER[5])
    for fx in range(7, 15, 3):                             # a planter, left base
        lo.rect(fx, h - 7, fx, h - 4, FOLIAGE[3]); _leaf_dab(lo, fx + 1, h - 6)
    _vine(lo, [(3, h - 4), (6, fy + 16), (2, fy + 5)])
    _vine(lo, [(w - 4, h - 5), (w - 8, fy + 14), (w - 3, fy + 4)])
    edge(lo, h)
    return _finish(lo, up, w, fy, h, composite, frames, _cottage_anim)


def town_academy(roof, stone, salt=221, composite=False, frames=1,
                 open_door=False):
    """The Alembic Academy — the town's grand landmark, 160x112. A wide leaf
    canopy flanked by two coursed-masonry TOWERS that rise through it to
    little leaf-dome caps; between them the great arcane rose window (mint
    greenhouse glass — it burns on the glow overlay) over the great arch
    door — SEALED iron-barred in the drained present, an open welcoming
    plank arch in the festival era (`open_door`); dressed-course cement
    walls, a copper header feeding a stone basin and a planter row, ivy
    everywhere — the wizard college gone quiet, kept alive by its garden.
    (`roof`/`stone` unused.)"""
    w, h, fy = 224, 144, 80
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    TW = 38                                                # tower width
    TOWERS = (5, w - TW - 5)
    # The building sits on the map's top row, so when the camera hits its
    # upper clamp the canvas top IS the screen top — the spires start low
    # enough to leave the pennants clear sky instead of flying off-frame.
    CONE_TIP, CONE_BASE = 14, 42
    PEN = 7                                                # pennant top
    # ---- roof: twin SPIRED towers, the canopy slung BETWEEN and BELOW them.
    # The old build gave both towers little leaf domes level with a full-width
    # canopy, so the silhouette was one rounded slab and the towers vanished —
    # while the overworld icon promises a keep with two coned spires. This is
    # that promise kept at zone scale: cones clear above the leaf line.
    _canopy(up, w, fy, flue_xs=(86, 138),
            sx0=TOWERS[0] + TW - 4, sx1=TOWERS[1] + 4, lobe=17.0, top=34.0)
    for tx0 in TOWERS:
        tx1 = tx0 + TW - 1
        cxt = (tx0 + tx1) // 2
        # cylindrical shaft: tone ramps left-lit to right-shadowed, banded
        for y in range(CONE_BASE, fy):
            for x in range(tx0, tx1 + 1):
                t = 0.18 + 0.56 * ((x - tx0) / float(TW - 1))
                if (y - CONE_BASE) % 9 == 8:
                    t += 0.20                              # course shadow
                up.set(x, y, up.tone(CEMENT, t, x, y, jitter=0.30))
        up.tri((cxt, CONE_TIP), CONE_BASE, tx0 - 3, tx1 + 4, FOLIAGE)   # spire
        up.rect(tx0 - 3, CONE_BASE, tx1 + 4, CONE_BASE, FOLIAGE[5])     # eave line
        up.set(cxt, CONE_TIP - 2, BRASS[1])                # finial
        up.rect(cxt, PEN, cxt, CONE_TIP - 3, IRON[1])      # pennant pole
        for i in range(4):                                 # swallowtail pennant
            up.rect(cxt + 1, PEN + i, cxt + 6 - i, PEN + i, VIOLETF)
        up.set(cxt + 2, PEN + 1, CRYSTAL)                  # its device
        for wy in (CONE_BASE + 10, CONE_BASE + 26):        # mint-lit arrow slits
            up.rect(cxt - 1, wy, cxt, wy + 7, DOORDARK)
            up.set(cxt - 1, wy, MINT)
        up.blob(cxt, CONE_BASE + 5, 6.0, 1.6, CEMENT[4])   # shade under the eave
    edge(up, fy)
    # ---- facade: dressed courses over the cement base
    _cement_wall(lo, w, h, fy)
    for cy_ in range(fy + 8, h - 6, 9):                    # ashlar course seams
        lo.rect(3, cy_, w - 4, cy_, CEMENT[2])
        off = 5 if (cy_ // 9) % 2 else 0
        for hx in range(7 + off, w - 5, 11):
            lo.rect(hx, cy_ - 4, hx, cy_ - 1, CEMENT[2])   # offset head joints
    for tx0 in TOWERS:                                     # the towers' lower shafts
        tx1 = tx0 + TW - 1
        _coursed_wall(lo, tx0, fy, tx1, h - 3, CEMENT, salt=salt, course=7, joint=11)
        lo.rect(tx0, fy, tx0, h - 3, CEMENT[0])
        lo.rect(tx1, fy, tx1, h - 3, CEMENT[4])
        lo.rect(tx0, h - 3, tx1, h - 1, STONER[4])         # plinth into the footing
        cxt = (tx0 + tx1) // 2
        for sy_ in (fy + 14, fy + 34):                     # tall paired slits
            lo.rect(cxt - 1, sy_, cxt, sy_ + 9, DOORDARK)
            lo.set(cxt - 1, sy_, MINT)
        _vine(lo, [(tx0 + 2, h - 4), (cxt + 4, fy + 30), (tx0 + 3, fy + 3)])
    # copper header + risers, routed AROUND the rose window
    _ph(lo, TOWERS[0] + TW + 6, TOWERS[1] - 7, fy + 3)
    for rx in (TOWERS[0] + TW + 8, TOWERS[1] - 9):
        _valve(lo, rx, fy + 4)
    _pv(lo, 51, fy + 4, h - 9); _ph(lo, 51, 62, h - 9)     # left riser -> the basin
    _pv(lo, w - 53, fy + 4, h - 13)                        # right -> the planters
    _ph(lo, 146, w - 53, h - 13)
    for nx in (152, 168):
        _pv(lo, nx, h - 12, h - 11)                        # drip nubs (animated)
    # the great arcane rose window — scaled up with the building
    cx, cy = w // 2 - 1, fy + 20
    for r_, c in ((14.5, COPPER[2]), (13.0, TIMBER[3]), (11.5, DOORDARK),
                  (9.2, MINT), (4.8, FOLIAGE[2])):
        lo.blob(cx, cy, r_, r_, c)
    lo.rect(cx, cy - 11, cx, cy + 11, TIMBER[5])           # tracery cross
    lo.rect(cx - 11, cy, cx + 11, cy, TIMBER[5])
    for sx_, sy_ in ((1, 1), (-1, 1), (1, -1), (-1, -1)):  # radial spokes
        ln(lo, cx + 4 * sx_, cy + 4 * sy_, cx + 9 * sx_, cy + 9 * sy_, TIMBER[5])
    lo.set(cx, cy, CRYSTAL)
    lo.set(cx - 4, cy - 5, WATERL)                         # glass glint
    # the great door — open/welcoming in the festival era, sealed iron in the
    # drained present; both share the arch rows at DT and the DT+3 mouth
    DT = fy + 36
    dx0, dx1 = w // 2 - 17, w // 2 + 16
    if open_door:
        _arch_door(lo, dx0, dx1, DT - 3, h)
    else:
        for ay, ah in ((DT + 2, 0), (DT + 1, 2), (DT, 5)):
            lo.rect(dx0 - 1 + ah, ay, dx1 + 1 - ah, ay, COPPER[2])
        lo.rect(dx0 - 2, DT + 3, dx1 + 2, h - 1, TIMBER[4])    # casing
        lo.rect(dx0, DT + 3, dx1, h - 1, DOORDARK)             # the dark mouth
        for gy in range(DT + 6, h - 1, 5):
            lo.rect(dx0, gy, dx1, gy, TIMBER[5])               # plank lines
        for bx in range(dx0 + 3, dx1 - 1, 5):                  # the BARS
            lo.rect(bx, DT + 4, bx, h - 3, IRON[2])
            lo.set(bx, DT + 4, IRON[1])
        for sy_ in (DT + 9, DT + 16):                          # iron straps + rivets
            lo.rect(dx0, sy_, dx1, sy_, IRON[3])
            for rx in range(dx0 + 2, dx1, 6):
                lo.set(rx, sy_, IRON[1])
        lo.set(cx, DT + 12, MINT); lo.set(cx, DT + 19, MINT)   # old-magic seams
    # tall lancet windows flanking the rose — the wall either side of it read
    # as bare cement at this size, which is what made the old build look like
    # a shed rather than a college hall
    for wx in (56, w - 72):
        lo.rect(wx - 1, fy + 13, wx + 16, fy + 38, TIMBER[4])   # frame
        lo.rect(wx, fy + 14, wx + 15, fy + 37, DOORDARK)
        lo.blob(wx + 7.5, fy + 15.0, 8.0, 5.0, TIMBER[4])       # arched head
        lo.blob(wx + 7.5, fy + 16.5, 6.5, 4.0, DOORDARK)
        for gy in range(fy + 16, fy + 37, 2):                   # leaded glass
            lo.rect(wx + 1, gy, wx + 14, gy, MINT if gy % 4 else GLASS)
        lo.rect(wx + 7, fy + 14, wx + 8, fy + 37, TIMBER[5])    # mullion
        for i in range(6):                                      # sky-catch streak
            lo.set(wx + 12 - i, fy + 19 + i, WATERL)
        lo.rect(wx - 2, fy + 38, wx + 17, fy + 39, CEMENT[0])   # lit sill
        lo.rect(wx - 2, fy + 40, wx + 17, fy + 40, CEMENT[4])
    gx = 136                                               # brass gauge, right wall
    lo.ball(gx, fy + 16, 4.6, 4.4, BRASS)
    lo.blob(gx, fy + 16, 3.0, 2.8, PAPER)                  # its face (flat color —
                                                           # ball() needs a RAMP; a flat
                                                           # tuple indexes to raw ints)
    ln(lo, gx, fy + 16, gx + 2, fy + 14, IRON[1])
    lo.set(gx, fy + 16, IRON[2]); lo.set(gx - 1, fy + 15, SPEC)
    # stone basin (left of the door) + planter row (right), riser-fed
    lo.rect(56, h - 8, 82, h - 3, STONER[3]); lo.rect(56, h - 8, 82, h - 8, STONER[1])
    lo.rect(57, h - 7, 81, h - 5, WATER); lo.rect(57, h - 7, 81, h - 7, WATERL)
    for bx0 in (144, 160):
        bx1 = bx0 + 13
        lo.rect(bx0, h - 11, bx1, h - 6, TIMBER[3])
        lo.rect(bx0, h - 11, bx1, h - 11, TIMBER[1])
        lo.rect(bx0, h - 6, bx1, h - 6, TIMBER[5])
        for i, fx in enumerate(range(bx0 + 2, bx1, 4)):
            lo.rect(fx, h - 15, fx, h - 12, FOLIAGE[3])
            _leaf_dab(lo, fx - 1, h - 14); _leaf_dab(lo, fx + 1, h - 16)
    _vine(lo, [(50, h - 3), (56, fy + 30), (47, fy + 8)])
    _vine(lo, [(w - 50, h - 3), (w - 56, fy + 28), (w - 47, fy + 8)])
    edge(lo, h)
    return _finish(lo, up, w, fy, h, composite, frames, _academy_anim)


def town_well(stone, salt=231):
    """The commons well at zone scale (32x32, 2x2 solid): shingled cap on
    timber posts over a coursed stone ring, rope and pail."""
    sp = S(32, 32, salt)
    for y in range(18, 32):                                # stone ring
        for x in range(3, 29):
            c = stone[2] if y < 24 else stone[3]
            if (x + y) % 6 == 0:
                c = stone[4]
            sp.set(x, y, c)
    sp.rect(3, 18, 28, 18, stone[1])                       # lit rim
    sp.rect(7, 20, 24, 23, DOORDARK)                       # the shaft
    sp.rect(9, 21, 12, 21, WATER)
    sp.rect(4, 8, 6, 18, TIMBER[3])                        # posts
    sp.rect(25, 8, 27, 18, TIMBER[3])
    sp.tri((15, 0), 8, 0, 31, TIMBER[2])                   # shingle cap
    sp.rect(12, 0, 19, 0, TIMBER[1])
    sp.rect(15, 8, 15, 17, PAPERD)                         # rope
    sp.rect(13, 16, 17, 19, STEEL[2])                      # pail
    sp.rect(13, 16, 17, 16, STEEL[1])
    edge(sp)
    return sp


def town_lamp(salt=233, mantle=MINT):
    """Brass-caged street lamp at zone scale (16x32, a 1x2 solid column);
    the halo rides the additive glow overlay."""
    sp = S(16, 32, salt)
    sp.rect(5, 27, 10, 29, IRON[3])                        # base
    sp.rect(4, 30, 11, 31, IRON[2])
    sp.rect(7, 8, 8, 27, IRON[2])
    sp.rect(7, 8, 7, 27, IRON[1])
    sp.rect(4, 0, 11, 0, BRASS[1])                         # cap
    sp.rect(4, 1, 11, 7, BRASS[3])
    sp.rect(5, 1, 10, 6, mantle)                           # the mantle
    sp.set(6, 2, SPEC)
    sp.set(3, 2, BRASS[2])
    sp.set(12, 2, BRASS[2])                                # cage arms
    edge(sp, 32)
    clipw(sp, 16)
    return sp


def town_stall(salt=241):
    """The flask-seller's stall at zone scale (48x32, 3x2 solid): striped
    awning over a timber counter of glinting wares."""
    w, h = 48, 32
    sp = S(w, h, salt)
    sp.rect(2, 6, 4, 24, TIMBER[3])                        # posts
    sp.rect(w - 5, 6, w - 3, 24, TIMBER[3])
    for x in range(0, w):                                  # awning
        c = RED if (x // 6) % 2 == 0 else PAPER
        sp.rect(x, 0, x, 6, c)
        if x % 6 == 5:
            sp.set(x, 6, PAPERD)
    sp.rect(0, 7, w - 1, 7, TIMBER[4])                     # awning bar
    sp.rect(3, 16, w - 4, 17, TIMBER[1])                   # counter top
    sp.rect(3, 18, w - 4, 25, TIMBER[2])
    sp.rect(3, 25, w - 4, 25, TIMBER[4])
    gx = w // 2 - 8                                        # wares
    sp.rect(gx, 11, gx + 2, 15, MINT)
    sp.rect(gx + 5, 9, gx + 7, 15, VIOLETF)
    sp.rect(gx + 10, 12, gx + 11, 15, BRASS[1])
    sp.set(gx + 13, 13, BRASS[3])
    sp.set(gx + 1, 10, PAPERD)
    sp.rect(5, 26, 7, 31, TIMBER[4])                       # legs
    sp.rect(w - 8, 26, w - 6, 31, TIMBER[4])
    edge(sp, h)
    return sp


def town_fence(cells, salt=247):
    """The yard fence as a Tier-3 y-sorted RUN (2026-07-19): the old baked
    `_fence_cell` rails lived on the lower canvas and drew UNDER every body —
    but a fence is standable both north and south, the doctrine's textbook
    Tier 3. Art matches the bake exactly (twin rails stopping 7px shy of the
    run ends, two pickets per 16px cell, no outline — it never had one);
    `cells` = horizontal run length in map cells, image cells*16 x 16."""
    w = cells * 16
    sp = S(w, 16, salt)
    tm = TIMBER
    x0, x1 = 7, w - 8
    sp.rect(x0, 4, x1, 4, tm[0])                           # top rail, lit crest
    sp.rect(x0, 5, x1, 6, tm[2])
    sp.rect(x0, 7, x1, 7, tm[4])
    sp.rect(x0, 9, x1, 9, tm[0])                           # bottom rail
    sp.rect(x0, 10, x1, 11, tm[2])
    sp.rect(x0, 12, x1, 12, tm[4])
    for c in range(cells):
        for u in (c * 16 + 3, c * 16 + 12):                # pickets
            sp.rect(u, 2, u + 1, 13, tm[3])
            sp.rect(u, 2, u, 13, tm[1])
            sp.set(u, 1, tm[0])
            sp.set(u + 1, 13, tm[5])
    return sp


def town_shop(roof, plaster, sign, wares, salt=251, composite=False, frames=1):
    """A shopfront in the naturey language: 96x64 (2 roof + 2 facade rows) —
    leaf canopy + flue, greeny-cement walls, a wide wood DISPLAY window of
    wares, a hanging trade sign (sword / flask), a copper pipe + rain-barrel,
    and vines. Both shops share the salt; only sign / wares differ."""
    w, h, fy = 96, 64, 32
    dx0, dx1 = 49, 62                                      # arch over the D cell
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    _canopy(up, w, fy, flue_xs=(66,))
    edge(up, fy)
    _cement_wall(lo, w, h, fy)
    # the wide wood display window, wares behind the glass
    wx, wy = 10, fy + 6
    lo.rect(wx - 1, wy - 1, wx + 26, wy + 15, TIMBER[4])
    lo.rect(wx, wy, wx + 25, wy + 14, DOORDARK)
    lo.rect(wx, wy, wx + 25, wy, TIMBER[2])
    lo.rect(wx - 2, wy + 15, wx + 27, wy + 16, TIMBER[3])  # sill
    for mx in range(wx + 6, wx + 25, 7):
        lo.rect(mx, wy, mx, wy + 13, TIMBER[4])            # mullions
    if wares == "arms":
        ln(lo, wx + 4, wy + 12, wx + 11, wy + 5, STEEL[1]); ln(lo, wx + 5, wy + 13, wx + 12, wy + 6, STEEL[3])
        lo.set(wx + 12, wy + 5, SPEC)
        lo.rect(wx + 15, wy + 9, wx + 18, wy + 12, BRASS[3]); lo.set(wx + 16, wy + 10, TIMBER[5])
        lo.rect(wx + 21, wy + 10, wx + 23, wy + 13, IRON[2])
    else:                                                  # tonics
        lo.rect(wx + 5, wy + 8, wx + 7, wy + 13, MINT); lo.set(wx + 6, wy + 6, PAPERD)
        lo.rect(wx + 12, wy + 10, wx + 13, wy + 13, WATER)
        lo.rect(wx + 18, wy + 9, wx + 20, wy + 13, FOLIAGE[2])   # a potted plant
    _arch_door(lo, dx0, dx1, fy, h)
    # the hanging trade sign right of the door
    sx = dx1 + 6
    lo.rect(sx, fy + 4, sx, fy + 10, IRON[2]); lo.rect(sx - 1, fy + 4, sx + 8, fy + 4, IRON[3])
    lo.rect(sx + 1, fy + 6, sx + 8, fy + 17, TIMBER[2]); lo.rect(sx + 1, fy + 6, sx + 8, fy + 6, TIMBER[1])
    if sign == "sword":
        lo.rect(sx + 4, fy + 8, sx + 5, fy + 13, STEEL[1]); lo.set(sx + 4, fy + 8, SPEC)
        lo.rect(sx + 2, fy + 14, sx + 7, fy + 14, BRASS[1]); lo.set(sx + 4, fy + 16, BRASS[3])
    else:
        lo.rect(sx + 3, fy + 9, sx + 6, fy + 15, MINT); lo.rect(sx + 4, fy + 7, sx + 5, fy + 8, PAPERD)
    # copper pipe + rain-barrel, right base
    _ph(lo, 4, w - 5, fy + 3); _pv(lo, w - 6, fy + 3, h - 10); _valve(lo, w - 6, fy + 3)
    rx0, rx1 = 78, 89
    lo.rect(rx0, h - 10, rx1, h - 3, TIMBER[3]); lo.rect(rx0, h - 10, rx1, h - 10, TIMBER[1])
    lo.rect(rx0, h - 10, rx1, h - 9, WATER); lo.rect(rx0, h - 9, rx1, h - 9, WATERL)
    lo.rect(rx0, h - 6, rx1, h - 6, TIMBER[5])
    _vine(lo, [(3, h - 4), (6, fy + 14), (2, fy + 4)])
    _vine(lo, [(w - 4, h - 5), (w - 9, fy + 12), (w - 3, fy + 4)])
    edge(lo, h)
    return _finish(lo, up, w, fy, h, composite, frames, _shop_anim)


def town_inn(roof, plaster, salt=261, composite=False, frames=1):
    """The inn in the naturey language: 144x80, the town's biggest cottage — a
    broad leaf canopy with THREE flues, a two-story greeny-cement facade, wood
    plant-windows (one warm-lit), a big arched double door under a tankard
    sign, an elaborate copper pipe web feeding a trough + rain-barrel, vines."""
    w, h, fy = 144, 80, 32
    dx0, dx1 = 65, 78                                      # arch over the D cell
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    _canopy(up, w, fy, flue_xs=(28, 72, 116))
    edge(up, fy)
    _cement_wall(lo, w, h, fy)
    lo.rect(0, fy + 18, w - 1, fy + 18, TIMBER[3])         # string course
    for ux in (14, 44, 116):                              # upper plant-windows
        _wood_window(lo, ux, fy + 4, 12, 11)
    _wood_window(lo, 24, fy + 24, 13, 13)                 # lower plant-window
    lo.rect(105, fy + 23, 118, fy + 37, TIMBER[4])        # one warm-lit window
    lo.rect(106, fy + 24, 117, fy + 36, WARMD); lo.rect(108, fy + 27, 115, fy + 34, WARM)
    lo.rect(111, fy + 24, 111, fy + 36, TIMBER[4]); lo.rect(106, fy + 30, 117, fy + 30, TIMBER[4])
    _arch_door(lo, dx0, dx1, fy, h)
    sx = dx1 + 6                                          # tankard sign
    lo.rect(sx, fy + 20, sx, fy + 26, IRON[2]); lo.rect(sx - 1, fy + 20, sx + 8, fy + 20, IRON[3])
    lo.rect(sx + 1, fy + 22, sx + 8, fy + 33, TIMBER[2]); lo.rect(sx + 1, fy + 22, sx + 8, fy + 22, TIMBER[1])
    lo.rect(sx + 3, fy + 25, sx + 6, fy + 30, BRASS[1]); lo.rect(sx + 3, fy + 24, sx + 6, fy + 24, PAPER)
    # the elaborate copper pipe web
    _ph(lo, 4, w - 5, fy + 3); _ph(lo, 4, w - 5, fy + 20)
    for rx in (4, w - 6, 40, 104):
        _pv(lo, rx, fy + 3, fy + 20); _valve(lo, rx, fy + 20)
    _pv(lo, 4, fy + 20, h - 8); _pv(lo, w - 6, fy + 20, h - 12)
    _pv(lo, 52, fy + 21, h - 13)                           # centre feed to the trough
    # a stone water-trough (spout) + a rain-barrel
    lo.rect(44, h - 8, 60, h - 3, STONER[3]); lo.rect(44, h - 8, 60, h - 8, STONER[1])
    lo.rect(45, h - 7, 59, h - 5, WATER); lo.rect(45, h - 7, 59, h - 7, WATERL)
    lo.rect(51, h - 13, 52, h - 12, COPPER[3])             # spout
    rx0, rx1 = 120, 134
    lo.rect(rx0, h - 12, rx1, h - 3, TIMBER[3]); lo.rect(rx0, h - 12, rx1, h - 12, TIMBER[1])
    lo.rect(rx0, h - 12, rx1, h - 11, WATER); lo.rect(rx0, h - 11, rx1, h - 11, WATERL)
    for by in (h - 9, h - 5):
        lo.rect(rx0, by, rx1, by, TIMBER[5])
    for fx in range(8, 20, 3):                             # a planter, left base
        lo.rect(fx, h - 7, fx, h - 4, FOLIAGE[3]); _leaf_dab(lo, fx + 1, h - 6)
    _vine(lo, [(3, h - 4), (6, fy + 20), (2, fy + 4)])
    _vine(lo, [(w - 4, h - 5), (w - 9, fy + 18), (w - 3, fy + 4)])
    edge(lo, h)
    return _finish(lo, up, w, fy, h, composite, frames, _inn_anim)


_FOUNTAIN_STREAMS = ((19, 12, 24), (28, 14, 25))          # pour columns x, y0, y1
_FOUNTAIN_ARCS = ((14, 20, 31), (27, 34, 29), (18, 24, 34))


def _fountain_anim(sp, f):
    """Frame-f water inside town_fountain's FIXED silhouette (the outline
    is already baked — only recolor, never move a silhouette pixel): pour
    dashes fall 1px/frame (4-period: seamless loop), the pool's ripple
    arcs wobble a px, splash glints and pool sparkles blink."""
    for x, y0, y1 in _FOUNTAIN_STREAMS:                    # falling dashes
        for y in range(y0, y1 + 1):
            sp.set(x, y, GLASS if (y - f) % 4 < 2 else WATER)
    for k, (rx0, rx1, ry) in enumerate(_FOUNTAIN_ARCS):    # ripple arcs: only
        dx = ((f + k) % 4) // 2                            # over open pool, so
        for x in range(rx0 + dx, rx1 + dx + 1):            # the pedestal foot
            if sp.px[ry][x] == WATER:                      # keeps its layering
                sp.set(x, ry, GLASS)
    sp.set(19, 25, MINT if f % 2 == 0 else WATERL)         # splash glints
    sp.set(28, 26, MINT if f % 2 == 1 else WATERL)
    sp.set(15, 30, SPEC if f % 2 == 0 else WATER)          # pool sparkles
    sp.set(33, 33, SPEC if f % 2 == 1 else WATER)


def town_fountain(stone, salt=271, frames=1):
    """The square's fountain (48x48, 3x3 solid): a coursed stone basin,
    rippled pool, and a pedestal crowned by a brass alembic bulb — the
    town's little monument to the drained craft. Corners stay transparent
    so the plaza paving shows through. With frames>1 returns a horizontal
    frame-sheet Img (pouring, rippling, glinting — see _fountain_anim)."""
    sp = S(48, 48, salt)
    # the basin: stacked ellipses, sunlit N rim to shaded S wall
    sp.blob(24, 30, 21.5, 12.5, stone[3])                  # S wall shade base
    sp.blob(24, 28.5, 20.5, 11.5, stone[1])                # basin wall
    sp.blob(24, 27, 19.0, 10.5, stone[0])                  # lit rim
    sp.blob(24, 28, 15.5, 8.2, stone[3])                   # inner lip shade
    sp.blob(24, 29, 14.5, 7.4, WATER)                      # the pool
    for jx, jy in ((8, 24), (14, 19), (24, 17), (34, 19),  # rim course joints
                   (40, 24), (11, 33), (37, 33), (24, 38)):
        sp.set(jx, jy, stone[3])
    # the pedestal and its brass alembic-bulb finial
    sp.rect(21, 12, 26, 27, stone[1])                      # column
    sp.rect(21, 12, 21, 27, stone[0])                      # lit W edge
    sp.rect(26, 12, 26, 27, stone[3])
    sp.blob(24, 28, 5.0, 2.0, stone[4])                    # foot in the water
    sp.rect(19, 10, 28, 11, stone[0])                      # cap course
    sp.set(19, 11, stone[3])
    sp.set(28, 11, stone[3])
    sp.rect(22, 7, 25, 9, BRASS[3])                        # the alembic neck
    sp.ball(23.5, 4, 3.8, 3.4, BRASS, power=2.0)           # the bulb
    sp.set(22, 2, SPEC)
    for x, y0, y1 in _FOUNTAIN_STREAMS:                    # pour streams: solid
        sp.rect(x, y0, x, y1, WATER)                       # columns IN the base
                                                           # silhouette, so the
                                                           # baked outline never
                                                           # ghosts a moved px
    edge(sp, 48)
    if frames == 1:
        _fountain_anim(sp, 0)
        return sp
    sheet = Img(48 * frames, 48)
    for f in range(frames):
        frm = _clone(sp)
        _fountain_anim(frm, f)
        sheet.blit_cell(frm, f * 48, 0)
    return sheet


def town_stairs(stone, salt=281, cheek=None, cells=2):
    """The terrace's grand stair (32 x 16*`cells`, over a 2-wide x `cells`-tall
    walkable stair block): four stone treads per cell between rock cheek walls.
    FULLY OPAQUE and UNoutlined — the flight must butt seamlessly into the road
    above and below, and opaque cells dedupe no matter what the underlay phase
    does.
    `cheek`: an optional second ramp for the flanking walls — pass the snow ramp
    in a winter town so the flight reads as cut through a drift.
    `cells`: MUST match the height of the cliff band it pierces. A terraced town
    runs cliffs at several heights on purpose, so the flight has to come in the
    same sizes; a 2-cell stair in a 4-cell band leaves half the drop unclimbed
    and wearing raw fabric. Defaults keep Alembic's shipped flight identical."""
    ch = cheek or stone
    h = 16 * cells
    sp = S(32, h, salt)
    for i in range(h // 4):                                # the treads
        y0 = i * 4
        sp.rect(0, y0, 31, y0, stone[1])                   # lit nose
        sp.rect(0, y0 + 1, 31, y0 + 2, stone[2])           # tread face
        sp.rect(0, y0 + 3, 31, y0 + 3, stone[4])           # riser shadow
    for x, y in ((9, 6), (21, 10), (13, 18), (24, 22),     # worn dabs
                 (7, 26), (18, 30)):
        if y < h:
            sp.set(x, y, stone[3])
    for y in range(32, h, 16):                             # more, further down
        sp.set(9 + h2(y, 3, salt) % 14, y + h2(y, 5, salt) % 9, stone[3])
    for cx0 in (0, 28):                                    # cheek walls
        sp.rect(cx0, 0, cx0 + 3, h - 1, ch[3])
        for y in range(h):
            for x in range(cx0, cx0 + 4):
                if _hatch_px(x + salt, y, 5, 0, -1):
                    sp.set(x, y, ch[4])
        sp.rect(cx0, 0, cx0 + 3, 0, ch[1])                 # lit crest
    sp.rect(3, 0, 3, h - 1, ch[5])                         # inner cheek shade
    sp.rect(28, 0, 28, h - 1, ch[5])
    return sp


RIFTDARK = (10, 8, 24, 255)                       # the bottom of a rift; no hue


def _rift_face(rock, grass, salt, h):
    """One 16 x `h` column of a CHASM, seen from directly above.

    REWRITTEN 2026-07-29, because the first pass was a cliff face wearing a
    different ramp — mid-tone at the top darkening to black at the foot — and a
    lit-at-the-top, dark-at-the-bottom band IS a wall. The rift read as a low
    stone wall with a wooden panel set into it, the panel being the trestle, and
    the whole crossing looked like a typing mistake in the map.

    What you actually see looking into a slot is the reverse. The NEAR wall
    falls away directly beneath your feet, so you never see its face at all —
    only black. The far wall is what fills the band, and its RIM is the lowest
    thing on screen and the brightest, because the light comes from above. So
    the ramp runs dark-to-light DOWNWARD and the lit arris a cliff spends on its
    crest gets spent here on the bottom edge instead.

    Cuts in 32nds like town_cliff's, so a rift authored 3 rows deep keeps its
    proportions instead of putting the far wall across the middle."""
    sp = S(16, h, salt)
    v_snow = max(1, h * 1 // 32)                       # the near rim's last snow
    v_far = h * 17 // 32                               # the far wall's base
    v_rim = h - max(1, h * 2 // 32)                    # its lit rim
    for x in range(16):
        for y in range(h):
            if y < v_snow:
                c = grass[3]                           # snow, already turning
            elif y < v_snow + 1:
                c = grass[5]                           # its underside, hard
            elif y < v_far:
                # The void. Flat black would read as a hole punched in the
                # canvas, so a few flecks of the deepest rock catch on the
                # near wall as it falls away — barely visible, and enough.
                c = RIFTDARK
                if h2(x, y, salt + 5) % 23 == 0:
                    c = rock[5]
            elif y < v_far + h * 4 // 32:
                c = rock[5]                            # far wall, deepest
            elif y < v_rim - h * 3 // 32:
                c = rock[4]
            elif y < v_rim:
                c = rock[3]
            elif y < h - 1:
                c = rock[1]                            # the far rim, lit
            else:
                c = rock[0]
            sp.set(x, y, c)
    # two short courses on the far wall only — strata across the void would be
    # scratches on nothing
    for i, sn in enumerate((24, 28)):
        yy = min(h * sn // 32 + h2(i, 2, salt) % 2, v_rim - 1)
        if yy < v_far:
            continue
        for x in range(16):
            if h2(x // 4 + i, 5, salt) % 3 != 0:
                sp.set(x, yy, rock[5])
    clipw(sp, 16)
    return sp


def town_cliff(rock, grass, salt=291, h=32, void=False, wall=False):
    """One 16 x `h` cliff-face column of a terrace band, stamped per column from
    three salted variants (the meadow-boulder pattern) by
    TileScene.stamp_columns. FULLY OPAQUE, NO edge(): the underlay's 32-space
    phase varies beneath it, and a per-column outline would print a seam every
    16px. Lip on top (pass the SNOW ramp as `grass` in a winter town), lit brow,
    strata face, near-black foot.

    `h` must equal T * the map run height — every band cut below is expressed as
    `h * N // 32`, never a literal row, so a taller face doesn't end up with its
    dark foot across the middle. (The // 32 form is deliberate over a float
    fraction: at the default h=32 it collapses to exactly N, which is what keeps
    Alembic's shipped terrace byte-identical.)

    `wall=True` draws a CAST CEMENT/CINDERBLOCK WALL instead of an eroded rock
    face (2026-07-29). It took three passes and each one was a different wrong
    answer, so the reasoning is worth keeping:

    1. Only the crest changed — a straight snow cap over a near-black turn-under
       and one lit arris, replacing a lip that rambled 3-5px per 5px run over
       the ramp's two brightest rows. That was right for "the upper ground
       stops" but the crest still read as an edge rather than as a TOP.
    2. The face went to rustic coursed masonry. Wrong the other way: the eroded
       rock FACE was liked, and heavy per-stone value variation reads as rubble.
    3. What was actually wanted: a MADE wall of cast block. Cement is FLAT, so
       all the contrast lives in a regular joint grid (16x8 running bond, the
       vertical joint alternating course by course) and none of it in per-stone
       value — that is the whole difference between a cast wall and a rubble
       one. Joints sit two steps down the ramp, never black, or it reads as a
       lattice.

    And the crest is a COPING that stands PROUD of the wall, throwing a shadow
    down it, under BROKEN snow. Both halves matter: without the overhang there
    is no top, only a boundary, and an unbroken white band along a terrace is a
    drift lying on the ground — bare cap showing through the gaps is what says
    the white is sitting ON something.

    Alembic's terrace does not pass the flag and regenerates byte-identical.

    `void=True` makes the CHASM instead — see _rift_face. That one flag is why
    chasms still need no render class of their own."""
    if void:
        return _rift_face(rock, grass, salt, h)
    sp = S(16, h, salt)
    # band cuts in 32nds of the face, so `h` scales and h=32 is the shipped art
    b_mid, b_low, b_foot = h * 21 // 32, h * 27 // 32, h * 30 // 32
    for x in range(16):
        if wall:
            # A CEMENT COPING under PATCHY snow. Two things make a crest read as
            # the TOP OF something rather than as an edge where the ground
            # stops. First the cap course stands PROUD of the wall and throws a
            # shadow down it — without that overhang there is no top, only a
            # boundary. Second the snow is BROKEN: an unbroken white band along
            # a terrace is a drift lying on the ground, while bare cap showing
            # through in gaps says the white is sitting ON something. Runs are
            # hashed 6px wide so drifts come out 6-18px, not per-pixel noise.
            CAP = 3
            # Runs are keyed on (x + salt) so their boundaries land differently
            # in every stamped variant — keyed on x alone the drifts came out
            # the same width at the same pitch all the way along the terrace and
            # read as crenellations. Ends taper a pixel so a drift has slopes.
            def _drift(px, salt=salt):
                return (0, 0, 1, 2, 3, 3)[h2((px + salt * 3) // 5, 3, salt) % 6]
            snow_h = _drift(x)
            if snow_h and min(_drift(x - 1), _drift(x + 1)) == 0:
                snow_h = max(1, snow_h - 1)
            for y in range(CAP):
                if snow_h and y >= CAP - snow_h:
                    sp.set(x, y, grass[1] if y == CAP - snow_h else grass[2])
                else:
                    sp.set(x, y, rock[1])          # bare cap, weathered pale
            sp.set(x, CAP, grass[4] if snow_h else rock[2])
            sp.set(x, CAP + 1, rock[0])            # the coping's lit arris
            sp.set(x, CAP + 2, rock[1])            # its front, proud of the wall
            sp.set(x, CAP + 3, rock[1])
            sp.set(x, CAP + 4, rock[4])            # the shadow it throws down
            sp.set(x, CAP + 5, rock[5])
            top = CAP + 6
        else:
            lip = 3 + h2((x + salt) // 5, 0, salt) % 3 # ragged ledge, 5px runs
            for y in range(lip):
                c = grass[2]
                if h2(x, y, salt + 3) % 7 == 0:
                    c = grass[1]                       # clump nicks
                sp.set(x, y, c)
            sp.set(x, lip, grass[4])                   # lip turn-under shadow
            sp.set(x, lip + 1, rock[0])                # the sunlit brow
            sp.set(x, lip + 2, rock[0])
            sp.set(x, lip + 3, rock[1])
            top = lip + 4
        if wall:
            continue                                   # cinderblock, drawn below
        for y in range(top, h):                        # the face, darkening down
            if y >= b_foot:
                c = rock[5]                            # foot dark
            elif y >= b_low:
                c = rock[4]
            elif y >= b_mid:
                c = rock[3]
            else:
                c = rock[2]
            sp.set(x, y, c)
        if h2(x, 29, salt) % 5 == 0:
            sp.set(x, h * 28 // 32, rock[3])           # foot scree fleck
    if wall:
        # CINDERBLOCK. A running bond on a REGULAR grid — 16x8 blocks, the
        # vertical joint alternating between the column's two edges course by
        # course. Cement is FLAT: all of the contrast lives in the joint grid
        # and none of it in per-stone value, which is the whole difference
        # between a cast wall and a rubble one. Joints are two steps down the
        # ramp rather than black, or the wall reads as a lattice.
        BH = 8
        row, n = top, 0
        while row < h:
            bed = min(row + BH - 1, h - 1)
            base = 2 if (row - top) / max(1.0, h - 1 - top) < 0.55 else 3
            vj = 0 if n % 2 == 0 else 8
            for x in range(16):
                k = base
                if h2(x, row, salt + 7) % 11 == 0:
                    k = min(5, base + 1)               # aggregate, showing
                elif h2(x, row, salt + 13) % 17 == 0:
                    k = max(0, base - 1)
                for y in range(row, bed + 1):
                    sp.set(x, y, rock[k])
                sp.set(x, row, rock[max(0, k - 1)])    # the block's lit bed
                sp.set(x, bed, rock[min(5, k + 2)])    # and the joint under it
                if x == vj:
                    for y in range(row, bed + 1):
                        sp.set(x, y, rock[min(5, k + 2)])
            row += BH
            n += 1
        for x in range(16):
            sp.set(x, h - 1, rock[5])                  # contact dark at the foot
        clipw(sp, 16)
        return sp

    # Dashed strata. THREE evenly spaced courses is right on a 32px step and
    # reads as MASONRY on a 64px wall, so both the count and a per-column wobble
    # scale with the face — but only above h=32, which keeps Alembic's shipped
    # terrace byte-identical.
    if h <= 32:
        strata = (11, 16, 22)
    else:
        n = max(4, h // 10)
        strata = tuple(4 + (24 * i) // (n - 1) + h2(i, salt, 9) % 3
                       for i in range(n))
    for i, sn in enumerate(strata):
        yy = h * sn // 32 + h2(i, 2, salt) % 3
        for x in range(16):
            wob = 0 if h <= 32 else (h2(x // 3, i, salt) % 3) - 1
            if h2(x // 4 + i, 5, salt) % 3 != 0:
                y2 = min(max(yy + wob, 0), h - 1)
                sp.set(x, y2, rock[4] if y2 < b_mid else rock[5])
    for k in range(1 if h <= 32 else 3):                   # long vertical cracks
        cx = 3 + h2(salt + k * 7, 7, 1) % 10
        a, b, c = h * 10 // 32, h * 18 // 32, h * 26 // 32
        if k:                                              # stagger the extras
            a, b, c = a + k * h // 9, b + k * h // 11, min(c + k * h // 13, h - 1)
        ln(sp, cx, a, cx + (salt % 3) - 1, b, rock[4])
        ln(sp, cx + (salt % 3) - 1, b, cx, c, rock[5])
    clipw(sp, 16)
    return sp


def town_cliff_return(rock, grass, salt=291, face=-1, w=5, cap=True):
    """The RETURN at a terrace band's STAIRCASE STEP (2026-07-29) — the short
    piece of wall you see edge-on where one run steps down to the next. 16x16,
    painting only a `w`-px strip down the exposed side, blitted over the top
    cell of the higher run by TileScene.stamp_columns.

    WHY. Every band in this town staircases (uniform bands read as one cliff
    drawn twice), and at each step the higher run's face simply STOPPED at a
    straight vertical cut against open snow. Two runs sitting near each other
    with nothing joining them do not read as one wall that steps down; they read
    as two walls, or as a mistake. The fix is the corner: carry the coping
    AROUND it and down to meet the lower run's coping, and the whole terrace
    resolves into a single structure.

    Same crest rows as town_cliff(wall=True) so the cap line crosses the corner
    without a seam, one step darker through the body (a side face turned off the
    light), a lit arris on the inner corner and the silhouette's own shadow on
    the outer edge. `face` is which side is exposed: -1 west, +1 east."""
    sp = S(16, 16, salt)
    xs = range(w) if face < 0 else range(16 - w, 16)
    inner = w - 1 if face < 0 else 16 - w          # the corner, catching light
    outer = 0 if face < 0 else 15                  # the silhouette edge
    CAP = 3 if cap else -1
    for x in xs:
        if cap:
            for y in range(CAP):                   # the cap, carried around
                c = grass[2]
                if h2(x, y, salt + 3) % 9 == 0:
                    c = grass[3]
                sp.set(x, y, c)
            sp.set(x, CAP, grass[5])               # the snow's own underside
            sp.set(x, CAP + 1, rock[2])            # the coping's return face:
            sp.set(x, CAP + 2, rock[2])            # dimmer than the front arris,
            sp.set(x, CAP + 3, rock[3])            # because it is turned away
            sp.set(x, CAP + 4, rock[5])            # and the shadow under it
        for y in range(CAP + 5, 16):               # the body, two steps darker
            sp.set(x, y, rock[4])
    for y in range(CAP + 1, 16):
        sp.set(inner, y, rock[1])                  # lit arris ON the corner
        sp.set(outer, y, rock[5])                  # near-black silhouette
    clipw(sp, 16)
    return sp


def town_gatepost(timber, stone, snow, face=1, salt=345):
    """One pier of a town GATE (2026-07-29): a squared log post on a coursed
    fieldstone footing under settled snow, with a hooded oil lamp on an iron
    bracket reaching out over the road. 16x48 on a 1x3 footprint — two WALKABLE
    crown cells over a solid base, the conifer/lamp idiom — so a pair can stand
    either side of a gate mouth and pinch it without walling it shut.

    Three cells, not two, and that is the whole design. At 32px these read as
    bollards beside a 33px cat; at 48 they stand OVER the lane and the gate is
    legible from the far end of the street, which is the entire point of it.

    `face` is the side the lamp reaches, +1 east / -1 west, so a pair aims both
    lamps INTO the lane. Everything else about the two is identical, which is
    what keeps the finished atlas paying for one silhouette rather than two.

    WHY THIS EXISTS. Lanternwood's south lane used to run three cells past the
    stairs and stop in open snow, with the exit trigger floating invisibly on
    it. Nothing on screen said "this is the way out of town", so a fight in the
    lower street kept ending with the player on the overworld by accident. A
    gate is the cheapest possible fix: it names the boundary, and it narrows the
    way through it from a whole snowfield to two cells."""
    h = 48
    sp = S(16, h, salt)
    _stone_courses(sp, 1, 34, 14, h - 1, stone)            # the fieldstone foot
    sp.rect(1, 34, 14, 34, snow[3])                        # snow on its top course
    sp.rect(1, h - 1, 14, h - 1, stone[5])
    sp.rect(4, 7, 11, 35, timber[2])                       # the squared post
    sp.rect(4, 7, 5, 35, timber[1])                        # lit west face
    sp.rect(10, 7, 11, 35, timber[4])                      # shaded east face
    for y in range(11, 34, 7):                             # adze marks
        sp.rect(6, y, 9, y, timber[3])
    sp.rect(2, 5, 13, 6, timber[4])                        # the capping plate,
    sp.rect(2, 4, 13, 4, timber[3])                        # overhanging the post
    sp.rect(2, 1, 13, 3, snow[2])                          # and its snow load
    sp.rect(2, 0, 13, 0, snow[1])
    sp.set(3, 1, snow[3])
    sp.set(12, 1, snow[3])
    _bracket_lamp(sp, 8 if face > 0 else 7, 15, face)
    edge(sp, h)
    clipw(sp, 16)
    return sp


def town_trestle(timber, snow, salt=351, cells=2):
    """A plank walkway spanning a chasm — the signature Narshe silhouette, and
    what makes a terraced town read as BUILT rather than merely eroded.
    32 x 16*`cells`: a two-cell-wide deck crossed NORTH-SOUTH, boards running
    across the walking direction, a rail down each long edge with its posts, and
    settled snow along the caps.

    The N-S orientation is forced and worth knowing why: stamp_columns asserts
    2-row VERTICAL runs, so a chasm band — like a cliff band — runs east-west
    across the map. The only way to cross one is perpendicular. (A rift running
    north-south would be a single tall column run and would fail that assert on
    the first cell.)

    Tier-1 on purpose, like the cliffs. A zone map's upper tile layer is
    load-bearing for the z-order lint — _check_art.py short-circuits that whole
    family on an empty upper layer — and a rail on a walkable deck cell fails
    both `upper art supported` and `walk-behind corridors capped` by
    construction. A body drawing OVER the near rail is exactly what the shipped
    _bridge_cell already does for Alembic's stream, and FFVI's bridges read the
    same way; nobody has ever noticed."""
    h = 16 * cells
    sp = S(32, h, salt)
    for y in range(h):                                     # the deck boards
        for x in range(3, 29):
            c = timber[1] if y % 5 < 2 else timber[2]
            if h2(x // 6, y // 5, salt) % 4 == 0:           # board-to-board tone
                c = timber[2] if y % 5 < 2 else timber[3]
            sp.set(x, y, c)
    for y in range(0, h, 5):                               # board seams
        sp.rect(3, y, 28, y, timber[3])
    for x in (13, 14):                                     # the worn walking line
        for y in range(h):
            if h2(x, y // 3, salt) % 3:
                sp.set(x, y, timber[2])
    for rx in (0, 29):                                     # rails, both long edges
        sp.rect(rx, 0, rx + 2, h - 1, timber[3])
        sp.rect(rx + 1, 0, rx + 1, h - 1, timber[2])       # lit cap down the middle
        for y in range(1, h, 7):                           # posts
            sp.rect(rx, y, rx + 2, min(y + 1, h - 1), timber[4])
        sp.rect(rx if rx else rx + 2, 0, rx if rx else rx + 2, h - 1, timber[5])
    sp.rect(3, 0, 3, h - 1, timber[4])                     # deck-to-rail shadow
    sp.rect(28, 0, 28, h - 1, timber[4])
    for y in range(2, h, 9):                               # settled snow on caps
        sp.rect(0, y, 2, min(y + 2, h - 1), snow[1])
        sp.rect(29, y, 31, min(y + 2, h - 1), snow[1])
    for y in range(5, h, 11):
        sp.set(7 + h2(y, 1, salt) % 14, y, snow[2])        # drift on the boards
    return sp


def bridge_fascia(bridge, salt=353, band=12):
    """The bridge's NEAR RAIL: a 16 x `band` strip painted onto the UPPER tile
    layer over the water cell directly south of a deck's south end.

    Same bug as the cliff overhang — a body standing on the last deck cell sinks
    ~11px of sprite into the river below it — but the terrace kit's mask_band
    can't be used here, because river cells ANIMATE on four frames and a mirrored
    band would freeze the top 12px at frame 0 while the rest of the cell kept
    flowing. So this is authored art instead of mirrored art: static by nature,
    no animation to keep in lockstep, and it reads as something that should have
    been there anyway — you are standing behind the bridge's own rail.

    Legal on the WATER cell and only there. Putting it on the walkable deck cell
    instead would demand upper art on every cell north of it, all the way up the
    span: `_check_art.py`'s "walk-behind corridors capped" requires a walkable
    cell under upper art to have upper art to its north, recursively."""
    sp = S(16, band, salt)
    sp.rect(0, 0, 15, 0, bridge[1])                        # lit rail cap
    sp.rect(0, 1, 15, 1, bridge[2])
    sp.rect(0, 2, 15, 2, bridge[4])                        # under-rail shadow
    for y in range(3, band - 1):                           # the deck's side
        for x in range(16):
            c = bridge[2] if (y + x // 5) % 3 else bridge[3]
            sp.set(x, y, c)
    for x in range(0, 16, 5):                              # plank butt seams
        sp.rect(x, 3, x, band - 2, bridge[4])
    for x in range(2, 16, 7):                              # the bearer stubs
        sp.rect(x, band - 4, x + 1, band - 1, bridge[4])
    sp.rect(0, band - 1, 15, band - 1, bridge[5])          # dark underside
    return sp


def town_tree(f, trunk, grass, salt=301):
    """A town tree: (lower, upper) pair on 32x48 for a 2x3 FULLY SOLID
    footprint — a body-height tree is too small for a walk-behind corridor
    (the doctrine's small-prop rule: heads/ears poke over a 2-row crown),
    so nobody stands inside it; the crown rides the upper layer purely so a
    body passing east/west tucks its inner shoulder behind the silhouette,
    and a body pressed on the south face draws over the trunk row's art.
    The trunk row is FULLY OPAQUE (flat grass base under the crown shadow)
    so its tiles dedupe whatever the fabric phase beneath. Three salted
    variants; lobe geometry drifts with the salt."""
    w, h = 32, 48
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    o1 = salt % 3 - 1                                      # per-salt lobe drift
    o2 = (salt // 3) % 3 - 1
    # ---- lower: the opaque trunk row (y 32..47)
    for y in range(32, 48):
        for x in range(w):
            c = grass[2]
            r = h2(x, y, salt + 5) % 11
            if r == 0:
                c = grass[1]
            elif r == 1:
                c = grass[3]
            lo.set(x, y, c)
    lo.blob(16, 40, 13.5, 4.5, grass[4])                   # canopy ground shadow
    lo.blob(16, 40, 8.5, 3.0, grass[5])
    lo.capsule(16, 44, 9, 47, 2.5, 1.5, trunk)             # root flare
    lo.capsule(16, 44, 23, 47, 2.5, 1.5, trunk)
    lo.capsule(16, 46, 16, 30, 4.5, 3.5, trunk)            # the trunk
    for y in range(34, 46):                                # bark grooves
        hw = int(3.5 + (y - 30) / 16.0) - 1                # inside the taper
        for x in range(16 - hw, 16 + hw + 1):
            if (x + y // 5) % 4 == 0:
                lo.set(x, y, trunk[3])
    lo.rect(13, 36, 13, 43, trunk[1])                      # west rim light
    # ---- upper: the crown (rows 0-1) + its under-rim fringe into the trunk row
    for cx, cy, rx, ry, sh in ((10 + o1, 14, 9.5, 8.0, 0.10),
                               (22 + o2, 12, 9.5, 8.0, 0.04),
                               (16 + o1, 21, 11.0, 9.0, -0.06)):
        up.ball(cx, cy, rx, ry, f, sh=sh, power=2.2)
    up.blob(15 + o2, 15, 3.0, 1.8, f[4])                   # lobe seam shadow
    up.blob(16, 29, 10.0, 3.2, f[4])                       # crown under-rim
    up.blob(16, 32, 6.5, 2.2, f[5])
    up.blob(8 + o1, 6, 3.5, 2.2, f[0])                     # NW sun-catch
    up.set(7 + o1, 5, SPEC)
    if salt % 3 == 1:
        up.set(21 + o2, 8, BLOOM)                          # a surviving bloom
        up.set(11 + o1, 18, BLOOM)
    up.despeckle(2, 1)
    edge(up, 38)
    for y in range(up.n):                                  # clip lobe drift back
        for x in range(w, up.n):                           # into the footprint
            up.px[y][x] = None
    return lo, up


# ---- Lanternwood: the winter cabin kit (Fuji's hometown zone) -----------------------

def _log_wall(lo, w, h, fy, snow):
    """Stacked-log cabin facade: lit log crowns, dark grooves with pale
    chinking dashes, end-grain corner notches, a drifted snow footing."""
    for y in range(fy + 1, h):
        r = (y - fy - 1) % 4
        c = TIMBER[1] if r == 0 else TIMBER[2] if r in (1, 2) else TIMBER[4]
        lo.rect(0, y, w - 1, y, c)
        if r == 3:
            for x in range(2, w - 2, 3):
                lo.set(x, y, PAPERD)                       # chinking dashes
    for x in (0, 1, w - 2, w - 1):                         # end-grain corners
        for y in range(fy + 1, h, 4):
            lo.set(x, y, TIMBER[3] if (x + y) % 2 else TIMBER[1])
    lo.rect(0, h - 2, w - 1, h - 1, snow[1])               # drifted footing
    for x in range(3, w - 2, 7):
        lo.set(x, h - 3, snow[0])


def _lit_window(lo, x0, y0, ww, hh):
    """A fire-lit cabin window: WARM/WARMD glass the _anim_building windows
    flicker recolors per frame (TIMBER mullions survive the recolor).
    Returns its (x, y, w, h) rect for the flicker list."""
    lo.rect(x0 - 1, y0 - 1, x0 + ww, y0 + hh, TIMBER[4])
    lo.rect(x0, y0, x0 + ww - 1, y0 + hh - 1, WARMD)
    lo.rect(x0 + 1, y0 + 1, x0 + ww - 2, y0 + 2, WARM)     # the fire's throw
    lo.rect(x0 + ww // 2, y0, x0 + ww // 2, y0 + hh - 1, TIMBER[4])
    lo.rect(x0, y0 + hh // 2, x0 + ww - 1, y0 + hh // 2, TIMBER[4])
    lo.rect(x0 - 2, y0 + hh, x0 + ww + 1, y0 + hh + 1, TIMBER[3])   # sill
    lo.set(x0 - 2, y0 + hh, TIMBER[1])
    return (x0, y0, ww, hh)


def _snow_roof(up, w, fy, roof, snow, ridge=0, ridge_half=None):
    """A steep side-gable roof under a deep snow blanket: the pitched slope
    is drawn, then all but its lowest rows recolor to drifted snow with sag
    lines; icicle teeth hang under the eave.

    `ridge` drops the ridge line off the canvas top, leaving clear sky above
    it for something that rises THROUGH the roof (the library's lantern
    cupola); `ridge_half` narrows the ridge for a steeper hip. Both default
    to the cabins' geometry, whose sheets stay byte-identical."""
    if ridge_half is None:
        ridge_half = max(4, w // 2 - 10)
    _hip_roof(up, 0, w - 1, ridge, fy - 1, ridge_half, roof)
    for y in range(0, fy - 3):                             # the snow blanket
        for x in range(w):
            if up.get(x, y) is None:
                continue
            t = 0.16 + 0.50 * (y / max(1.0, fy - 3.0))
            if y % 6 == 5 and (x + y) % 3:
                t += 0.30                                  # sag lines
            up.set(x, y, up.tone(snow, t, x, y, jitter=0.5))
    for x in range(2, w - 2, 5):                           # icicle teeth
        up.set(x, fy, snow[1])
        if x % 2:
            up.set(x, fy + 1, snow[2])


def _stone_chimney(up, x, y0, y1, snow):
    """A squat fieldstone chimney through the snow roof (Alembic keeps its
    copper flues; Lanternwood burns wood in stone) — snow-capped."""
    for y in range(y0, y1 + 1):
        for x_ in range(x, x + 5):
            t = 0.28 + 0.40 * ((x_ - x) / 4.0)
            if (y - y0) % 3 == 2:
                t += 0.24                                  # course seams
            up.set(x_, y, up.tone(STONER, t, x_, y, jitter=0.4))
    up.rect(x, y0, x + 4, y0, STONER[4])                   # sooty crown
    up.rect(x - 1, y0 - 1, x + 5, y0 - 1, snow[0])         # the snow cap
    up.set(x - 1, y0, snow[1])
    up.set(x + 5, y0, snow[1])


def town_cabin(roof, snow, salt=311, composite=True, frames=8, wide=False):
    """A Lanternwood log cabin — 80x64 over 5x4 (or 96x80 over 6x5 with
    `wide`, the library hall): stacked-log walls, a deep snow-blanketed
    gable roof, fire-lit windows softly PULSING (the sheet breathes them via
    _anim_building's `windows`), a plank door spilling lamplight, a hooded
    stoop lantern, and a snow-capped stone chimney breathing lazy grey
    WOODSMOKE (`wood_flues`, pad=18 headroom).

    EIGHT frames, not the woodsmoke's four: the hearth breath wants a slow
    ~1.4s cycle (travel_scene's ANIM_STEP is 0.18s) and WIN_PULSE spans the
    whole sheet, while every smoke term stays periodic in 4 and simply loops
    twice — so the sheet is seamless either way."""
    assert frames < 2 or frames % len(WIN_PULSE) == 0, \
        "an animated cabin sheet must hold whole window-breath cycles"
    w, h, fy = (96, 80, 40) if wide else (80, 64, 30)
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    _snow_roof(up, w, fy, roof, snow)
    mx = w - 22                                            # the chimney: a
    _stone_chimney(up, mx, 3, 13, snow)                    # squat stack poking
                                                           # through the snow
    edge(up, fy + 2)                                       # keep the icicles
    _log_wall(lo, w, h, fy, snow)
    cx = w // 2
    wins = [_lit_window(lo, 9, fy + 8, 10, 10),
            _lit_window(lo, w - 20, fy + 8, 10, 10)]
    if wide:
        wins.append(_lit_window(lo, 30, fy + 8, 10, 10))
    lo.rect(cx - 6, fy + 6, cx + 6, h - 2, TIMBER[4])      # the plank door
    lo.rect(cx - 5, fy + 7, cx + 5, h - 2, TIMBER[2])
    for gy in range(fy + 10, h - 2, 4):
        lo.rect(cx - 5, gy, cx + 5, gy, TIMBER[4])
    lo.rect(cx - 5, fy + 7, cx + 5, fy + 7, TIMBER[1])     # lit lintel
    lo.set(cx + 3, fy + 15, BRASS[0])                      # the latch
    lo.rect(cx - 4, h - 3, cx + 4, h - 2, WARMD)           # lamplight spill
    lo.set(cx, h - 3, WARM)
    lo.rect(cx - 10, fy + 9, cx - 9, fy + 12, BRASS[2])    # stoop lantern
    lo.rect(cx - 10, fy + 9, cx - 9, fy + 9, BRASS[1])
    lo.set(cx - 10, fy + 10, WARM)
    edge(lo, h)
    anim = (lambda fa, ca, f2, dy=0: _anim_building(
        fa, ca, f2, wood_flues=((mx + 1, 3),), windows=tuple(wins), dy=dy))
    return _finish(lo, up, w, fy, h, composite, frames, anim, pad=18)


def _arch_rows(cx, y0, y1, r):
    """Rows of a round-headed opening `y0` (the CROWN) to `y1`: a semicircular
    head of radius r springing at y0+r-1, then a straight shaft. Yields
    (y, xl, xr) — the one geometry the library's windows, its door arch and
    its fanlight all cut themselves from, so a frame drawn by dilating these
    rows can never drift off its own glass. Springing off the crown, never off
    the sill: keyed to the sill instead, a tall window loses its whole head."""
    spring = y0 + r - 1
    for y in range(y0, y1 + 1):
        if y >= spring:
            hw = r
        else:
            d = (spring - y) / float(r)
            hw = r * max(0.0, 1.0 - d * d) ** 0.5
        yield y, int(round(cx - hw)), int(round(cx + hw))


def _arch_window(lo, cx, y0, y1, r, mullions=True):
    """A tall arched READING window — the library's one loud break from the
    cabins' little square panes. Timber frame dilated off the opening, warm
    glass on the WARM/WARMD ladders the hearth breath recolors, leaded
    mullions dividing it into small panes, a stone sill. Returns the rect for
    the breath list."""
    rows = list(_arch_rows(cx, y0, y1, r))
    for y, xl, xr in rows:                                 # frame: the opening
        lo.rect(xl - 1, y, xr + 1, y, TIMBER[4])           # dilated one pixel
    lo.rect(rows[0][1] - 1, y0 - 1, rows[0][2] + 1, y0 - 1, TIMBER[4])
    for y, xl, xr in rows:
        lo.rect(xl, y, xr, y, WARMD)                       # the glass
    for y, xl, xr in rows[:4]:                             # the fire's throw,
        lo.rect(xl, y, xr, y, WARM)                        # pooled in the head
    if mullions:
        for y, xl, xr in rows:                             # leaded panes: one
            if y > y0 + r // 2:                            # mullion, transoms
                lo.set(cx, y, TIMBER[4])                   # every 8 rows
            if (y - y0 - r) % 8 == 0 and y > y0 + r:
                lo.rect(xl, y, xr, y, TIMBER[4])
    lo.rect(rows[-1][1] - 3, y1 + 1, rows[-1][2] + 3, y1 + 2, STONER[3])  # sill
    lo.rect(rows[-1][1] - 3, y1 + 1, rows[-1][2] + 3, y1 + 1, STONER[1])
    # BOTH edges come off the SHAFT row (the widest), like the sill above. Taking
    # the left edge off the CROWN row instead shifts the rect ~4px east, and the
    # westmost glass column then never steps with the breath — a dark stripe that
    # reads as a mullion that isn't there.
    return (rows[-1][1] - 1, y0 - 1, rows[-1][2] - rows[-1][1] + 3, y1 - y0 + 3)


def _rose_window(up, cx, cy, r):
    """The gable's round window: a timber wheel of warm glass with radial
    spokes and a hub — a library front's one flourish, and the highest lit
    thing on the street after the cupola. Returns its rect for the breath."""
    for dy in range(-r - 1, r + 2):
        for dx in range(-r - 1, r + 2):
            q = (dx * dx + dy * dy) / float(r * r)
            if q <= 1.0:
                up.set(cx + dx, cy + dy, WARMD if q > 0.34 else WARM)
            elif q <= 1.44:
                up.set(cx + dx, cy + dy, TIMBER[4] if q > 1.1 else TIMBER[2])
    for ax, ay in ((0, -1), (0, 1), (-1, 0), (1, 0),       # eight spokes
                   (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)):
        ln(up, cx + ax * 2, cy + ay * 2, cx + ax * r, cy + ay * r, TIMBER[4])
    up.set(cx, cy, TIMBER[2])                              # the hub
    return (cx - r - 1, cy - r - 1, 2 * r + 3, 2 * r + 3)


def _lantern_cupola(up, cx, y1, snow):
    """The ridge LANTERN — a glazed belfry standing clear above the roofline,
    burning all night. Lanternwood's name made into a landmark: the library is
    the lamp the town is named for, and this is the one silhouette no cabin
    can grow. Drawn DOWN from the canvas top (there is no headroom above a
    prop sheet — the pad rows belong to the smoke), so the finial can't clip.
    Returns the glass rect for the breath."""
    hw = 13
    up.rect(cx - 1, 0, cx, 2, BRASS[1])                    # the brass finial
    up.set(cx - 1, 0, BRASS[0])
    up.tri((cx, 2), 10, cx - hw - 2, cx + hw + 3, snow)    # its snow cap
    up.rect(cx - hw - 2, 10, cx + hw + 2, 11, TIMBER[4])   # the cap's eave
    gy0, gy1 = 12, y1 - 4                                  # the glazed body:
    up.rect(cx - hw + 3, gy0 - 1, cx + hw - 3, gy1 + 1, TIMBER[4])
    up.rect(cx - hw + 4, gy0, cx + hw - 4, gy1, WARM)      # the brightest thing
    up.rect(cx - hw + 4, gy1 - 1, cx + hw - 4, gy1, WARMD)  # on the street
    for px_ in (cx - hw + 7, cx, cx + hw - 7):             # slim glazing bars
        up.rect(px_, gy0, px_, gy1, TIMBER[4])
    up.rect(cx - hw - 1, y1 - 3, cx + hw + 1, y1 - 2, TIMBER[2])   # the deck it
    up.rect(cx - hw - 1, y1 - 1, cx + hw + 1, y1, TIMBER[4])       # stands on
    return (cx - hw + 3, gy0 - 1, 2 * hw - 5, gy1 - gy0 + 3)


def _gable_front(up, cx, apex, eave, half, snow, salt):
    """The cross-gable over the entry: a board-and-batten gable END facing the
    camera off the main ridge, snow banked along both rakes. The cabins are
    one long roof each; a gable turned to face the street is what tells a
    passer-by this building has a FRONT."""
    span = float(eave - apex)
    for y in range(apex, eave + 1):
        hw = int(round(half * (y - apex) / span))
        for x in range(cx - hw, cx + hw + 1):
            t = 0.30 + 0.34 * ((x - cx + hw) / max(1.0, 2.0 * hw))
            if (x - cx) % 7 == 0:
                t += 0.22                                  # batten shadows
            up.set(x, y, up.tone(TIMBER, t, x, y, jitter=0.35))
    for y in range(apex, eave + 1):                        # the snow-banked
        hw = half * (y - apex) / span                      # rakes: a 4px band
        for k in range(5):                                 # riding each slope
            for sx in (cx - hw + k, cx + hw - k):
                up.set(int(round(sx)), y - 3 + k // 2,
                       snow[0] if k < 3 else snow[1])
    up.rect(cx - 4, apex - 4, cx + 3, apex + 2, TIMBER[2])         # ridge board
    up.rect(cx - 4, apex - 4, cx + 3, apex - 3, snow[0])
    up.rect(cx - half + 6, eave - 5, cx + half - 6, eave - 4, TIMBER[1])  # tie
    up.rect(cx - half + 6, eave - 3, cx + half - 6, eave - 3, TIMBER[5])


def _portal(lo, cx, y0, y1, half, salt):
    """The great arched doorway: a coursed-stone frontispiece standing proud
    of the log walls, a keystoned round arch, a lit fanlight over double plank
    doors. Returns the fanlight rect for the breath list."""
    _coursed_wall(lo, cx - half, y0, cx + half, y1, STONER, salt=salt,
                  course=6, joint=9, t0=0.26)
    lo.rect(cx - half - 2, y0, cx + half + 2, y0 + 2, STONER[1])   # the cornice
    lo.rect(cx - half - 2, y0 + 3, cx + half + 2, y0 + 3, STONER[4])
    r, ay0 = 12, y0 + 6
    door_top = ay0 + 18                                    # the transom line
    rows = list(_arch_rows(cx, ay0, y1, r))
    for y, xl, xr in rows:                                 # voussoir ring
        lo.rect(xl - 2, y, xr + 2, y, STONER[0])
        if y < door_top:
            lo.rect(xl, y, xr, y, WARMD)                   # the lit fanlight
    for y, xl, xr in rows[:4]:
        lo.rect(xl, y, xr, y, WARM)
    lo.rect(cx - 3, ay0 - 5, cx + 2, ay0 + 1, STONER[1])   # the keystone,
    lo.rect(cx - 3, ay0 - 5, cx + 2, ay0 - 5, STONER[0])   # straddling the
    lo.rect(cx - 4, ay0 - 5, cx - 4, ay0 + 1, STONER[4])   # crown, not sunk
    lo.rect(cx + 3, ay0 - 5, cx + 3, ay0 + 1, STONER[4])   # through the glass
    for ax, ay in ((-1.0, 0.0), (-0.7, -0.7), (0.0, -1.0),  # the fan's leading
                   (0.7, -0.7), (1.0, 0.0)):
        ln(lo, cx, door_top, cx + ax * r, door_top + ay * r, TIMBER[4])
    lo.rect(cx - r, door_top, cx + r, door_top + 1, TIMBER[4])     # the transom
    lo.rect(cx - r, door_top + 2, cx + r, y1, TIMBER[2])           # the doors
    for gx in range(cx - r + 2, cx + r, 4):
        lo.rect(gx, door_top + 3, gx, y1 - 1, TIMBER[4])           # plank seams
    lo.rect(cx - 1, door_top + 2, cx, y1, TIMBER[4])               # meeting stile
    for hy in (door_top + 15, door_top + 16):                      # brass rings
        lo.rect(cx - 5, hy, cx - 4, hy, BRASS[1])
        lo.rect(cx + 4, hy, cx + 5, hy, BRASS[1])
    lo.rect(cx - r + 1, y1 - 1, cx + r - 1, y1, WARMD)             # the light
    lo.rect(cx - 4, y1 - 1, cx + 3, y1, WARM)                      # under the door
    return (cx - r - 1, ay0 - 1, 2 * r + 3, door_top - ay0 + 2)


def _bracket_lamp(lo, x, y, face):
    """A hooded oil lamp on a scrolled iron bracket off the facade — the pair
    that flank the library door, and the reason nobody in Lanternwood needs
    magic to find their way home. `face` is the side it reaches out to."""
    gx = x + 5 * face
    ln(lo, x, y, gx, y, IRON[2])                           # the bracket arm
    ln(lo, x, y + 3, x + 3 * face, y + 1, IRON[3])         # its scrolled stay
    lo.set(gx, y + 1, IRON[2])
    # BRASS runs out after index 1 (2-3 are the ramp's violet law gone hot
    # red/magenta — the cabins' stoop lantern wears that as a stray red pixel);
    # brass here is 0/1 only, and every dark is IRON.
    lo.rect(gx - 2, y + 2, gx + 2, y + 2, BRASS[1])        # the hood, wider
    lo.set(gx - 2, y + 2, IRON[2])                         # than the flame it
    lo.set(gx + 2, y + 2, IRON[2])                         # keeps the snow off
    lo.rect(gx - 1, y + 3, gx + 1, y + 7, WARMD)           # its little flame
    lo.rect(gx - 1, y + 4, gx + 1, y + 6, WARM)
    lo.rect(gx - 2, y + 8, gx + 2, y + 8, IRON[2])         # the pan it sits in
    lo.set(gx, y + 8, BRASS[1])
    return (gx - 1, y + 3, 3, 5)


def town_library(roof, snow, salt=341, composite=True, frames=8):
    """THE LANTERNWOOD LIBRARY — the town's one civic building and Fuji's
    workplace, 144x112 over a 9x7 footprint: nearly twice a cabin in every
    direction, and deliberately built of different STUFF. Log walls like its
    neighbours, but standing on a coursed fieldstone plinth, fronted by a
    keystoned stone portal with a lit fanlight, lit by four tall arched
    reading windows instead of little square panes, gabled toward the street
    with a rose window in the peak — and crowned by the glazed LANTERN CUPOLA
    that gives the town its name. Seven warm apertures share the one hearth
    breath, so the whole front swells and ebbs together: from the lane it
    reads as the only building in Lanternwood that is still awake.

    (It was a `wide=True` cabin until 2026-07-25 — a five-window shed nobody
    could pick out of a snowy street, let alone believe a scholar worked in.)
    """
    assert frames < 2 or frames % len(WIN_PULSE) == 0, \
        "an animated cabin sheet must hold whole window-breath cycles"
    w, h, fy = 144, 112, 56
    cx = w // 2
    RIDGE = 18                                             # clear sky above it
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # ---- roof: a long hall ridge, a gable turned to the street, the cupola
    _snow_roof(up, w, fy, roof, snow, ridge=RIDGE, ridge_half=50)
    _gable_front(up, cx, 26, fy - 1, 30, snow, salt)
    rose = _rose_window(up, cx, 42, 9)
    lantern = _lantern_cupola(up, cx, RIDGE + 3, snow)
    mx = w - 32                                            # a tall stack, well
    _stone_chimney(up, mx, 6, 34, snow)                    # clear of the ridge
    edge(up, fy + 2)                                       # keep the icicles
    # ---- facade: logs on a stone plinth
    _log_wall(lo, w, h, fy, snow)
    _coursed_wall(lo, 0, h - 16, w - 1, h - 3, STONER, salt=salt + 2,
                  course=6, joint=11)
    lo.rect(0, h - 17, w - 1, h - 16, STONER[1])           # the water table
    lo.rect(0, h - 2, w - 1, h - 1, snow[1])               # drifted footing
    wins = [_arch_window(lo, x, 62, 93, 8) for x in (14, 34, w - 35, w - 15)]
    wins.append(_portal(lo, cx, 58, h - 4, 19, salt + 3))
    wins.append(_bracket_lamp(lo, cx - 21, 70, -1))
    wins.append(_bracket_lamp(lo, cx + 21, 70, 1))
    lo.rect(cx - 26, h - 5, cx + 25, h - 1, STONER[2])     # two broad steps up
    lo.rect(cx - 26, h - 5, cx + 25, h - 5, STONER[0])     # out of the snow
    lo.rect(cx - 21, h - 9, cx + 20, h - 6, STONER[2])
    lo.rect(cx - 21, h - 9, cx + 20, h - 9, STONER[0])
    wins.append(rose)
    wins.append(lantern)
    edge(lo, h)
    anim = (lambda fa, ca, f2, dy=0: _anim_building(
        fa, ca, f2, wood_flues=((mx + 1, 6),), windows=tuple(wins), dy=dy))
    return _finish(lo, up, w, fy, h, composite, frames, anim, pad=18)


def _conifer_snowload(sp, snow, limit):
    """Snow along the current topmost silhouette (run per tier, before the
    next overlaps): every exposed bough shoulder keeps its load."""
    for x in range(sp.n):
        for y in range(min(limit, sp.n)):
            if sp.get(x, y) is None:
                continue
            sp.set(x, y, snow[0])
            if sp.get(x, y + 1) is not None and x % 2:
                sp.set(x, y + 1, snow[1])
            break


def town_conifer(f, trunk, snow, salt=321):
    """A zone-scale snow-laden spruce (32x64 over a 2x4 FULLY SOLID
    footprint — the small-prop rule): four stacked shaded tiers, each
    snow-loaded before the next overlaps it, over a grooved trunk on
    shadowed snow. Returns (lower, upper) split at px 44 for the
    ConiferTrunk / ConiferCrown T3 pair (crown baseline pushed south via
    base_inset, the town_tree idiom)."""
    sp = S(32, 64, salt)
    sp.blob(16, 58, 12, 3.5, snow[2])                      # ground shadow
    sp.blob(16, 58, 8, 2.5, snow[3])
    sp.rect(14, 42, 17, 57, trunk[2])                      # the trunk
    sp.rect(14, 42, 14, 57, trunk[1])
    sp.rect(17, 42, 17, 57, trunk[4])
    for (ax, ay), by, hw, sh in (((16, 28), 46, 14, 0.10),
                                 ((16, 16), 36, 11, 0.02),
                                 ((16, 7), 26, 8, -0.06),
                                 ((16, 1), 15, 5, -0.12)):
        sp.tri((ax, ay), by, 16 - hw, 16 + hw, f, sh=sh)
        _conifer_snowload(sp, snow, 48)
    edge(sp, 64)
    from _propkit import split_rows
    return split_rows(sp, 44)


def town_conifer_big(f, trunk, snow, salt=323):
    """The old-growth spruce: 32x96 over a 2x6 FULLY SOLID footprint — the same
    tree as town_conifer with six tiers instead of four, standing about three
    times the player's height. A winter town wants a few of these towering over
    the small ones; a forest of one tree size reads as wallpaper.

    Deliberately 2 cells WIDE, not 3, and that is a lint constraint rather than
    an art choice: on a 3-wide trunk the outer columns of the trunk rows carry
    no art at all, fall under T3_COVER_MIN, and any of them touching a walkable
    cell fires the invisible-wall lint. Height is free; width is not.

    Its map FOOTPRINT is 2x4, the same as the small spruce — not 2x6. The art is
    bottom-anchored, so the extra 32px simply overhangs upward into open sky,
    and the footprint covers only the art's widest 64px. Sizing the footprint to
    the art instead put the two narrow top tiers on their own cells, where the
    left and right columns hold a few pixels of bough each and fail T3 coverage.
    Overhang, don't extend: it also means a big spruce drops in anywhere a small
    one fits, including terraces too shallow for six rows.

    Returns ONE sprite, unsplit — unlike town_conifer. The trunk/crown split
    exists so a body can pass BEHIND a canopy and IN FRONT of a trunk, which a
    spruce whose boughs reach the ground has no use for; plain y-sort at the
    footprint's south edge is already correct for it."""
    sp = S(32, 96, salt)
    sp.blob(16, 90, 12, 3.5, snow[2])                      # ground shadow
    sp.blob(16, 90, 8, 2.5, snow[3])
    sp.rect(14, 66, 17, 89, trunk[2])                      # the trunk
    sp.rect(14, 66, 14, 89, trunk[1])
    sp.rect(17, 66, 17, 89, trunk[4])
    for (ax, ay), by, hw, sh in (((16, 44), 72, 14, 0.10),
                                 ((16, 34), 60, 12, 0.06),
                                 ((16, 25), 50, 10, 0.01),
                                 ((16, 17), 40, 8, -0.05),
                                 ((16, 9), 30, 6, -0.09),
                                 ((16, 2), 20, 4, -0.13)):
        sp.tri((ax, ay), by, 16 - hw, 16 + hw, f, sh=sh)
        _conifer_snowload(sp, snow, 76)
    edge(sp, 96)
    return sp


def frozen_pond(snow, salt=331, w=64, h=48, skated=False):
    """The skating pond — flat Tier-1 ground art baked via place() over WALKABLE
    pond cells, never sea/river (those classes ANIMATE): a pale ice sheet, long
    pressure cracks, swept glints, a drifted rim.

    `w`/`h` default to the shipped 64x48 (4x3 cells) and every feature is placed
    proportionally, so the default regenerates byte-identical while the town
    RINK can be the same treatment at 128x64.

    `skated=True` cuts the loops people leave. It is the whole difference
    between a rink and a puddle: an untouched sheet of ice reads as scenery,
    and a figure-eight reads as somewhere the town goes."""
    ICE = ((222, 238, 248, 255), (196, 220, 240, 255), (168, 196, 228, 255),
           (136, 162, 204, 255), (104, 126, 172, 255))
    sx, sy = w / 64.0, h / 48.0
    def _p(x, y):                                          # shipped coords ->
        return (int(round(x * sx)), int(round(y * sy)))     # this pond's
    sp = S(w, h, salt)
    cx, cy = w / 2.0, h / 2.0
    for y in range(h):
        for x in range(w):
            dx, dy = (x - cx) / (cx - 1.0), (y - cy) / (cy - 1.0)
            q = dx * dx + dy * dy
            if q > 1.0:
                continue
            if q > 0.82:                                   # drifted rim
                sp.set(x, y, snow[0] if (x + y) % 3 else snow[1])
                continue
            t = 0.18 + 0.5 * q
            i = min(3, int(t * 4 + ((x * 7 + y * 13) % 5 - 2) * 0.12))
            sp.set(x, y, ICE[max(0, i)])
    if skated:
        # (1) the shadow the snow banked round the rim throws in across the
        # north-west arc, and (2) a sheen sweeping the other way. Both STEP the
        # ice ramp by one rather than painting a tone, so they ride the radial
        # shading already there instead of flattening it — a white oval with no
        # depth in it was most of what made this read as unfinished.
        for y in range(h):
            for x in range(w):
                dx, dy = (x - cx) / (cx - 1.0), (y - cy) / (cy - 1.0)
                q = dx * dx + dy * dy
                if q > 0.82:
                    continue
                cur = sp.get(x, y)
                if cur not in ICE:
                    continue
                i = ICE.index(cur)
                if q > 0.44 and dx + dy < -0.35:
                    i = min(4, i + 1)                      # banked-rim shadow
                elif abs((x * 0.55 + y) - w * 0.42) < h * 0.09:
                    i = max(0, i - 1)                      # sheen
                sp.set(x, y, ICE[i])
        for k in range(3):                                 # (3) wind scour
            ry = int(h * (0.30 + 0.19 * k)) + h2(k, salt, 5) % 3
            for x in range(w):
                dx, dy = (x - cx) / (cx - 1.0), (ry - cy) / (cy - 1.0)
                if dx * dx + dy * dy > 0.70 or h2(x // 5, k, salt) % 4 == 0:
                    continue
                cur = sp.get(x, ry)
                if cur in ICE:
                    sp.set(x, ry, ICE[min(4, ICE.index(cur) + 1)])
        for xa, ya, xb, yb in ((0.17, 0.64, 0.43, 0.33),   # (4) straight strides
                               (0.59, 0.70, 0.85, 0.44)):
            ln(sp, int(w * xa), int(h * ya) + 1, int(w * xb), int(h * yb) + 1,
               ICE[3])
            ln(sp, int(w * xa), int(h * ya), int(w * xb), int(h * yb), ICE[0])
        # ...then the loops, cut in the ice's brightest tone with a shaded lip
        # under each — the shading is what stops them reading as cracks, which
        # the pond already has three of.
        for ex, ey, rx, ry in ((0.41, 0.42, 0.085, 0.115),
                               (0.57, 0.60, 0.075, 0.100)):
            pts = []
            for k in range(33):
                a = k * 6.283185 / 32.0
                pts.append((int(cx * 2 * ex + w * rx * math.cos(a)),
                            int(cy * 2 * ey + h * ry * math.sin(a))))
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                ln(sp, xa, ya + 1, xb, yb + 1, ICE[3])
                ln(sp, xa, ya, xb, yb, ICE[0])
        sweep = [(int(w * f), int(h * (0.34 + 0.26 * math.sin(f * 3.4))))
                 for f in (0.16, 0.30, 0.44, 0.58, 0.72, 0.84)]
        for (xa, ya), (xb, yb) in zip(sweep, sweep[1:]):
            ln(sp, xa, ya + 1, xb, yb + 1, ICE[3])
            ln(sp, xa, ya, xb, yb, ICE[0])
    for pts in (((14, 30), (30, 22), (44, 26)),            # pressure cracks
                ((26, 14), (34, 24)), ((40, 34), (50, 28))):
        for a, b in zip(pts, pts[1:]):
            (xa, ya), (xb, yb) = _p(*a), _p(*b)
            ln(sp, xa, ya, xb, yb, ICE[4])
    for x, y in ((20, 18), (38, 16), (46, 32), (24, 34)):
        sp.set(*_p(x, y), SPEC)                            # swept glints
    edge(sp, h)
    return sp
