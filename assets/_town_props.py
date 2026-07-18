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


def _anim_building(facade, canopy, f, flues=(), streams=(), basins=(),
                   barrels=(), drips=(), dy=0):
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


def _finish(lo, up, w, fy, h, composite, frames, anim):
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
    sheet = Img(w * frames, h + SMOKE_PAD)
    for f in range(frames):
        frm = _pad_top(base, SMOKE_PAD)
        anim(frm, frm, f, SMOKE_PAD)
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
    _anim_building(facade, canopy, f, dy=dy, flues=((56, 2), (104, 2)),
                   streams=((42, 104, 3),),               # riser spout -> the basin
                   basins=((41, 59, 105),),
                   drips=((104, 100), (118, 100)))        # nubs over the planters


# ---- shared naturey-building parts (canopy roof, cement wall, window, door) ----

def _canopy(up, w, fy, flue_xs=()):
    """A leafy canopy roof built from ROUND lobes of one size (keyed to roof
    HEIGHT — a wide building gets MORE lobes, never stretched ellipses), each
    lobe given its own under-arc shadow + crown highlight so the leaf masses
    read individually. The WHOLE silhouette stays >=1px inside every canvas
    edge, so edge() rings it completely (no half-outline that reads as a
    crop), and the top TOP px stay clear as headroom for the copper flue caps
    and their wind-swept smoke (animated later — never clipped)."""
    TOP = 5.0                                              # flue-cap/smoke headroom
    r = max(7.0, fy * 0.40)                                # the one lobe radius
    crown, eave = [], []
    x0, x1 = r * 1.05 + 1.0, w - r * 1.05 - 1.0            # crown row (inset)
    nc = max(1, round(max(1.0, x1 - x0) / (r * 0.9)))
    for i in range(nc + 1):
        bx = x0 + (x1 - x0) * i / max(1, nc)
        crown.append((bx, TOP + r + (r * 0.18 if i % 2 else 0.0)))
    re = r * 0.80                                          # eave row (clamped inside)
    ex0, ex1 = re + 1.5, w - re - 2.5
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
    up.blob(w / 2.0, fy - 1.5, w * 0.47, 2.0, FOLIAGE[5])  # dark under-rim
    for i in range(max(8, w // 6)):                        # leaf-cluster dabs
        hx = 4 + (i * 23) % max(1, w - 10)
        hy = int(TOP + 4 + (i * 11) % max(4, int(fy - TOP - 9)))
        if up.get(hx, hy) is not None and up.get(hx + 2, hy + 1) is not None:
            c, s = (FOLIAGE[1], FOLIAGE[4]) if i % 2 else (FOLIAGE[2], FOLIAGE[5])
            up.set(hx, hy, c); up.set(hx + 1, hy, c)
            up.set(hx + 1, hy + 1, s); up.set(hx + 2, hy + 1, s)
    for i in range(max(6, w // 10)):                       # single-pixel dapple
        hx = (i * 29) % (w - 6) + 3
        hy = int(TOP + 2 + (i * 7) % max(4, int(fy - TOP - 8)))
        if up.get(hx, hy) is not None:
            up.set(hx, hy, FOLIAGE[1] if i % 2 else FOLIAGE[3])
    for fx in flue_xs:                                     # caps BELOW the top edge
        _chimney(up, fx, 2, min(fy - 6, 22))


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
    w, h, fy = 160, 112, 64
    lo, up = S(w, h, salt), S(w, h, salt + 1)
    # ---- roof: the shared canopy, then twin towers rising THROUGH it
    _canopy(up, w, fy, flue_xs=(56, 104))
    for tx0 in (8, w - 30):
        tx1 = tx0 + 21
        cxt = (tx0 + tx1) / 2.0
        for bx, r_ in ((cxt - 5.0, 6.5), (cxt + 5.0, 6.5), (cxt, 7.5)):
            up.ball(bx, 16.0, r_, r_ * 0.9, FOLIAGE, sh=-0.02, power=2.1)   # dome cap
        up.blob(cxt, 20.5, 9.0, 2.2, FOLIAGE[4])           # dome under-rim
        _coursed_wall(up, tx0, 23, tx1, fy - 1, CEMENT, salt=salt, course=7, joint=11)
        up.rect(tx0, 23, tx0, fy - 1, CEMENT[0])           # lit W edge
        up.rect(tx1, 23, tx1, fy - 1, CEMENT[4])
        for wy in (30, 47):                                # mint arrow slits
            up.rect(int(cxt) - 1, wy, int(cxt), wy + 6, DOORDARK)
            up.set(int(cxt) - 1, wy, MINT)
    edge(up, fy)
    # ---- facade: dressed courses over the cement base
    _cement_wall(lo, w, h, fy)
    for cy_ in range(fy + 8, h - 6, 9):                    # ashlar course seams
        lo.rect(3, cy_, w - 4, cy_, CEMENT[2])
        off = 5 if (cy_ // 9) % 2 else 0
        for hx in range(7 + off, w - 5, 11):
            lo.rect(hx, cy_ - 4, hx, cy_ - 1, CEMENT[2])   # offset head joints
    for tx0 in (8, w - 30):                                # the towers' lower shafts
        tx1 = tx0 + 21
        _coursed_wall(lo, tx0, fy, tx1, h - 3, CEMENT, salt=salt, course=7, joint=11)
        lo.rect(tx0, fy, tx0, h - 3, CEMENT[0])
        lo.rect(tx1, fy, tx1, h - 3, CEMENT[4])
        lo.rect(tx0, h - 3, tx1, h - 1, STONER[4])         # plinth into the footing
        cxt = (tx0 + tx1) // 2
        lo.rect(cxt - 1, fy + 16, cxt, fy + 23, DOORDARK)  # slit
        lo.set(cxt - 1, fy + 16, MINT)
        _vine(lo, [(tx0 + 2, h - 4), (cxt + 3, fy + 26), (tx0 + 3, fy + 3)])
    # copper header + risers, routed AROUND the rose window
    _ph(lo, 32, w - 33, fy + 3)
    for rx in (34, w - 36):
        _valve(lo, rx, fy + 4)
    _pv(lo, 34, fy + 4, h - 9); _ph(lo, 34, 42, h - 9)     # left riser -> the basin
    _pv(lo, w - 36, fy + 4, h - 13); _ph(lo, 96, w - 36, h - 13)   # right -> planters
    for nx in (104, 118):
        _pv(lo, nx, h - 12, h - 11)                        # drip nubs (animated)
    # the great arcane rose window
    cx, cy = w // 2 - 1, fy + 17
    for r_, c in ((11.5, COPPER[2]), (10.2, TIMBER[3]), (9.0, DOORDARK),
                  (7.2, MINT), (3.8, FOLIAGE[2])):
        lo.blob(cx, cy, r_, r_, c)
    lo.rect(cx, cy - 9, cx, cy + 9, TIMBER[5])             # tracery cross
    lo.rect(cx - 9, cy, cx + 9, cy, TIMBER[5])
    for sx_, sy_ in ((1, 1), (-1, 1), (1, -1), (-1, -1)):  # radial spokes
        ln(lo, cx + 3 * sx_, cy + 3 * sy_, cx + 7 * sx_, cy + 7 * sy_, TIMBER[5])
    lo.set(cx, cy, CRYSTAL)
    lo.set(cx - 3, cy - 4, WATERL)                         # glass glint
    # the great door — open/welcoming in the festival era, sealed iron in the
    # drained present; both share the arch rows at fy+30 and the fy+33 mouth
    dx0, dx1 = w // 2 - 13, w // 2 + 12
    if open_door:
        _arch_door(lo, dx0, dx1, fy + 27, h)
    else:
        for ay, ah in ((fy + 32, 0), (fy + 31, 2), (fy + 30, 5)):
            lo.rect(dx0 - 1 + ah, ay, dx1 + 1 - ah, ay, COPPER[2])
        lo.rect(dx0 - 2, fy + 33, dx1 + 2, h - 1, TIMBER[4])   # casing
        lo.rect(dx0, fy + 33, dx1, h - 1, DOORDARK)            # the dark mouth
        for gy in range(fy + 36, h - 1, 5):
            lo.rect(dx0, gy, dx1, gy, TIMBER[5])               # plank lines
        for bx in range(dx0 + 3, dx1 - 1, 5):                  # the BARS
            lo.rect(bx, fy + 34, bx, h - 3, IRON[2])
            lo.set(bx, fy + 34, IRON[1])
        for sy_ in (fy + 39, fy + 45):                         # iron straps + rivets
            lo.rect(dx0, sy_, dx1, sy_, IRON[3])
            for rx in range(dx0 + 2, dx1, 6):
                lo.set(rx, sy_, IRON[1])
        lo.set(cx, fy + 42, MINT); lo.set(cx, fy + 48, MINT)   # old-magic seams
    lo.ball(104, fy + 14, 4.2, 4.0, BRASS)                 # brass gauge, right wall
    lo.blob(104, fy + 14, 2.8, 2.6, PAPER)                 # its face (flat color —
                                                           # ball() needs a RAMP; a flat
                                                           # tuple indexes to raw ints)
    ln(lo, 104, fy + 14, 106, fy + 12, IRON[1])
    lo.set(104, fy + 14, IRON[2]); lo.set(103, fy + 13, SPEC)
    # stone basin (left of the door) + planter row (right), riser-fed
    lo.rect(40, h - 8, 60, h - 3, STONER[3]); lo.rect(40, h - 8, 60, h - 8, STONER[1])
    lo.rect(41, h - 7, 59, h - 5, WATER); lo.rect(41, h - 7, 59, h - 7, WATERL)
    for bx0 in (98, 112):
        bx1 = bx0 + 12
        lo.rect(bx0, h - 11, bx1, h - 6, TIMBER[3])
        lo.rect(bx0, h - 11, bx1, h - 11, TIMBER[1])
        lo.rect(bx0, h - 6, bx1, h - 6, TIMBER[5])
        for i, fx in enumerate(range(bx0 + 2, bx1, 4)):
            lo.rect(fx, h - 15, fx, h - 12, FOLIAGE[3])
            _leaf_dab(lo, fx - 1, h - 14); _leaf_dab(lo, fx + 1, h - 16)
    _vine(lo, [(36, h - 3), (40, fy + 26), (34, fy + 8)])
    _vine(lo, [(w - 34, h - 3), (w - 38, fy + 24), (w - 33, fy + 8)])
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


def town_lamp(salt=233):
    """Brass-caged street lamp at zone scale (16x32, a 1x2 solid column);
    the halo rides the additive glow overlay."""
    sp = S(16, 32, salt)
    sp.rect(5, 27, 10, 29, IRON[3])                        # base
    sp.rect(4, 30, 11, 31, IRON[2])
    sp.rect(7, 8, 8, 27, IRON[2])
    sp.rect(7, 8, 7, 27, IRON[1])
    sp.rect(4, 0, 11, 0, BRASS[1])                         # cap
    sp.rect(4, 1, 11, 7, BRASS[3])
    sp.rect(5, 1, 10, 6, MINT)                             # the mantle
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


def town_fountain(stone, salt=271):
    """The square's fountain (48x48, 3x3 solid): a coursed stone basin,
    rippled pool, and a pedestal crowned by a brass alembic bulb — the
    town's little monument to the drained craft. Corners stay transparent
    so the plaza paving shows through."""
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
    for rx0, rx1, ry in ((14, 20, 31), (27, 34, 29), (18, 24, 34)):
        sp.rect(rx0, ry, rx1, ry, GLASS)                   # ripple arcs
    sp.set(15, 30, SPEC)
    sp.set(33, 33, SPEC)
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
    for py in (13, 17, 21):                                # pour streams
        sp.set(19, py, GLASS)
        sp.set(28, py + 2, GLASS)
    sp.set(19, 25, MINT)                                   # splash glints
    sp.set(28, 26, MINT)
    edge(sp, 48)
    return sp


def town_stairs(stone, salt=281):
    """The terrace's grand stair (32x32 over the 2x2 walkable S block):
    eight stone treads between rock cheek walls. FULLY OPAQUE and UNoutlined
    — the flight must butt seamlessly into the road above and below, and
    opaque cells dedupe no matter what the underlay phase does."""
    sp = S(32, 32, salt)
    for i in range(8):                                     # the treads
        y0 = i * 4
        sp.rect(0, y0, 31, y0, stone[1])                   # lit nose
        sp.rect(0, y0 + 1, 31, y0 + 2, stone[2])           # tread face
        sp.rect(0, y0 + 3, 31, y0 + 3, stone[4])           # riser shadow
    for x, y in ((9, 6), (21, 10), (13, 18), (24, 22),     # worn dabs
                 (7, 26), (18, 30)):
        sp.set(x, y, stone[3])
    for cx0 in (0, 28):                                    # cheek walls
        sp.rect(cx0, 0, cx0 + 3, 31, stone[3])
        for y in range(32):
            for x in range(cx0, cx0 + 4):
                if _hatch_px(x + salt, y, 5, 0, -1):
                    sp.set(x, y, stone[4])
        sp.rect(cx0, 0, cx0 + 3, 0, stone[1])              # lit crest
    sp.rect(3, 0, 3, 31, stone[5])                         # inner cheek shade
    sp.rect(28, 0, 28, 31, stone[5])
    return sp


def town_cliff(rock, grass, salt=291):
    """One 16x32 cliff-face column of the terrace band, stamped per column
    from three salted variants (the meadow-boulder pattern). FULLY OPAQUE,
    NO edge(): the underlay's 32-space phase varies beneath it, and a
    per-column outline would print a seam every 16px. Grass lip on top,
    lit brow, strata face, near-black foot."""
    sp = S(16, 32, salt)
    for x in range(16):
        lip = 3 + h2((x + salt) // 5, 0, salt) % 3         # ragged ledge, 5px runs
        for y in range(lip):
            c = grass[2]
            if h2(x, y, salt + 3) % 7 == 0:
                c = grass[1]                               # clump nicks
            sp.set(x, y, c)
        sp.set(x, lip, grass[4])                           # lip turn-under shadow
        sp.set(x, lip + 1, rock[0])                        # the sunlit brow
        sp.set(x, lip + 2, rock[0])
        sp.set(x, lip + 3, rock[1])
        for y in range(lip + 4, 32):                       # the face, darkening down
            if y >= 30:
                c = rock[5]                                # foot dark
            elif y >= 27:
                c = rock[4]
            elif y >= 21:
                c = rock[3]
            else:
                c = rock[2]
            sp.set(x, y, c)
        if h2(x, 29, salt) % 5 == 0:
            sp.set(x, 28, rock[3])                         # foot scree fleck
    for i, sy in enumerate((11, 16, 22)):                  # dashed strata cracks
        yy = sy + h2(i, 2, salt) % 3
        for x in range(16):
            if h2(x // 4 + i, 5, salt) % 3 != 0:
                sp.set(x, yy, rock[4] if yy < 21 else rock[5])
    cx = 3 + h2(salt, 7, 1) % 10                           # one long vertical crack
    ln(sp, cx, 10, cx + (salt % 3) - 1, 18, rock[4])
    ln(sp, cx + (salt % 3) - 1, 18, cx, 26, rock[5])
    clipw(sp, 16)
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
