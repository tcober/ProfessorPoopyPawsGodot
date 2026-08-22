#!/usr/bin/env python3
"""THE GREAT HALL of the Alembic Academy — a Room CONFIG (both prologue beats).

Rebuilt 2026-08-04 from the ground up: the FF6 OPERA SHOT in the
wizard-school register — the only walkable ground is the stage and the pit
strip at its foot; the house is AMBIANCE (packed pews, rows of heads, the
runner falling into gloom). Terrain/compose/light/output live in assets/
_interior.py; furniture in assets/_interior_props.py. This picks the `hall`
palette (plum stone / rose flag floor / chalk-mint accent), hand-paints THE
VAULT (rows 0-7: ashlar field, two great piers, the pointed arch whose crown
sits above the podium camera's own frame line, the mint rose window, the
glittering midnight backdrop, the theater-red velvet valance + pier tails), the
timber STAGE BOARDS, the dim house runner and the gloom band with the
far-off doors, emits the y-sorted lectern / pews / panel desk / stage apron
/ west curtain leg, hangs the FLOATING CANDLES (Tier-3, hframes=4 flicker,
doused by scene/hall.gd), and writes a candle-warm + ward-mint glow. The
scene of the recital and the naming.

Re-run: python3 assets/_gen_tileset_hall.py [--preview out.png]
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _palette import ramp
from _tilekit import sprite_img, BRASSD
from _interior import Room, flag_px, T
from _interior_props import (rug, chalkboard, lectern, desk,
                             stage_front, curtain_leg, floating_candle,
                             FLAME, FLAME_IN, FLAME_CORE, WAX)

# rose flag floor lit toward chalk-mint on the stage (the board's ward-light
# spills onto the platform; the house below lives on candle-warm instead —
# that contrast is the room's whole light story)
room = Room("hall", "hall", flag_px, (150, 240, 214), floor_chars=".g",
            lit_blend=0.40)

CHALK = [(214, 246, 236, 255), (150, 240, 214, 255),
         (96, 196, 176, 255), (60, 140, 128, 255)]     # chalk-mint ramp
RUGB = ramp((92, 52, 108), "violet", 6)                # deep plum runner
CURT = ramp((152, 38, 54), "violet", 5)                # theater-red velvet
ROSEG = [(214, 250, 238, 255), (150, 240, 214, 255),   # rose-window glass,
         (96, 196, 176, 255), (54, 128, 118, 255)]     # mint (the ward-light)
STONE = room.WALLR                                     # the vault's plum ashlar
PAPERC = (240, 232, 226, 255)                          # the cartouche clock face

BOARD = room.bbox("Q")
LECT = room.bbox("Ll")                 # the full footprint incl. walkable corners
FR = room.FLOOR_ROW                    # 8 — the stage tuck row

# ---- the vault's shared geometry (one set of numbers; the paint, the baked
# ---- candles and the glow all read from it, so they can never drift) --------
VAULT_H = 8 * T                        # rows 0-7, y 0..127
PIER_W = {"wx0": 3 * T, "wx1": 5 * T - 1,      # west pier, x48..79
          "ex0": 19 * T, "ex1": 21 * T - 1}    # east pier, x304..335
ARCH_X0, ARCH_X1 = 5 * T, 19 * T - 1   # the opening between the piers
ARCH_CX = 12 * T                       # 192 — the map's own midline
ARCH_SPRING = 64                       # where the arcs leave the piers
ARCH_CROWN = 6                         # above the podium camera's y=28 line
ROSE_C, ROSE_R = (ARCH_CX, 43), 14
VAL_Y0, VAL_DIP = 58, 22               # valance top; deepest catenary reach
                                       # (under-hem kisses the board's top
                                       # frame at y96; title at 102 stays clear)
VAL_UNDER = 8                          # how much deeper the under-layer hangs
# The stage floor is TIMBER BOARDS — a stage is built, not paved, and the
# warm platform against the cold flag house is the FF6 opera read in one
# material change. Lit cells blend toward the board's own mint pool.
# HAND-PINNED (a list, per the tri law): ramp()'s violet shadow law took the
# warm seed straight to brick and the platform shipped terracotta — the same
# family as BRASS[2..3] and the Academy keep's red timber frame. Wood may be
# an honest warm brown; these are oak.
STAGEB = [(214, 172, 128, 255), (192, 146, 104, 255), (168, 122, 84, 255),
          (140, 96, 64, 255), (108, 70, 50, 255), (78, 48, 40, 255)]
STAGE_LIT = [tuple(int(STAGEB[max(0, i - 1)][j] +
                       ((150, 240, 214)[j] - STAGEB[max(0, i - 1)][j]) * 0.35)
                   for j in range(3)) + (255,) for i in range(6)]
STAGE_SH = [STAGEB[min(5, i + 2)] for i in range(6)]
# Nave wall pilasters land on the pew rows — architecture answering furniture.
PILASTER_ROWS = (11, 13, 15, 17)
# THE HOUSE IS AN AMPHITHEATRE ("it is so boxy", 2026-08-04): each pew tier
# is an ARC centred on the podium — nearest the stage at the aisle, sweeping
# HOUSE_ARC px south by the walls — and the whole band falls away on a RADIAL
# gloom centred on the stage, which is what rounds the room's corners off.
# hall.gd's AUD_ARC nudges the audience onto the same curve: keep them married.
HOUSE_ARC = 12
TIER_TOPS = (13, 15, 17)               # each tier's own base row
ARC_HALF = 9 * T                       # the house band's half-width


def _arch_y(x):
    """The great arch's curve: crown at the midline, springing at the pier
    faces — a wide basket arch (t^2), the opera-house reference's shape, so
    the gilt frame fills the band instead of spiking through it."""
    t = min(1.0, abs(x - ARCH_CX) / float(ARCH_CX - ARCH_X0))
    return ARCH_CROWN + (ARCH_SPRING - ARCH_CROWN) * (t * t)


def _ashlar_px(x, y, shade=0):
    """Dressed ashlar as a pure 16-periodic pixel function (the _academy_props
    _ashlar builder's grammar, made tile-local so plain field cells dedupe):
    8px courses with a lit top arris, head joints on a 16px running bond.
    Joints two steps down the ramp, NEVER black (the lattice rule)."""
    v = y % 8
    u = (x + 8 * ((y // 8) % 2)) % 16
    if v == 7:
        i = 4                                   # bed joint
    elif u == 0 and v > 0:
        i = 4                                   # head joint
    elif v == 0:
        i = 1                                   # lit course arris
    else:
        i = 2
    return STONE[min(5, i + shade)]


# whole-tile light: the STAGE tuck row bathes in the board's ward-light (the
# platform reads brighter than the house); the back of the house falls into
# shadow toward the doors — the dark narthex is the void that makes the front
# read full. Fringe dither reads as a checkerboard on the rose flags, skip it.
room.lit_cells = {(c, FR) for c in range(4, 19)}
room.fringe_cells = set()
room.shadow_rows = (12,)      # the pit's south row falls toward the house


def _vault_rules(tx, ty):
    """Claim every wall cell in the vault band (rows 0-7) — _vault() paints
    the whole composition in one pass, so the default plank painter must not
    touch it."""
    return ty < FR


def _noop(tx, ty):
    return None


def _r_cell(tx, ty):
    """The processional runner CONTINUING through the house as SOLID paint —
    the same 8px diamond field as the walkable rug, pulled down the ramp and
    stripped of its lit accent, deeper still past the middle tier. The value
    drop is load-bearing twice over: it reads as the aisle falling away into
    the dark, and it keeps the invisible-wall lint honest (a solid cell that
    deduped to the walkable rug's own tiles would read as walkable and
    block)."""
    deep = 1 if ty >= 16 else 0
    x0, y0 = tx * T, ty * T
    for y in range(y0, y0 + T):
        for x in range(x0, x0 + T):
            d = abs(2 * (x % 8) - 7) + abs(2 * (y % 8) - 7)
            if d <= 4:
                c = RUGB[3 + deep]
            elif d == 6:
                c = RUGB[4]
            else:
                c = RUGB[4 + deep] if (x + y) % 2 else RUGB[5]
            room.bg.put(x, y, c)


def _n_cell(tx, ty):
    """The gloom band — the back of the house falling out of the light. The
    southmost camera clamp shows two pixels of this row; the rest exists for
    the preview and for honesty (a border band that is a hole reads as a
    hole). The far doors glint into it in _door_glint()."""
    x0, y0 = tx * T, ty * T
    room.bg.rect(x0, y0, x0 + T - 1, y0 + T - 1, (22, 15, 42, 255))
    room.bg.rect(x0, y0, x0 + T - 1, y0 + 1, (34, 24, 58, 255))


def _amb_cell(tx, ty):
    """Underlay for a house candle's own cell: the runner if it hangs over
    the aisle strip, plain floor otherwise (those cells sit under opaque pew
    art and are never seen) — a prop's underlay is the ground it moved to."""
    if 10 <= tx <= 13:
        _r_cell(tx, ty)
    else:
        room.floor_cell(tx, ty, "plain")


room.paint_terrain(wall_rules=_vault_rules,
                   special={"Q": _noop, "^": _noop,
                            "r": _r_cell, "n": _n_cell, "&": _amb_cell})


def _vault():
    """THE PROSCENIUM (rows 0-7), re-derived 2026-08-04 from the opera-house
    reference photo, whose one structural lesson is a VALUE FLIP: THE
    OPENING IS DARK AND THE FRAME IS GOLD. A near-black offstage shell edge
    to edge (the stage band below is full-bleed, so the theatre's dark
    shell runs off the frame with it); inside the arch a deep glittering
    MIDNIGHT BACKDROP — static two-value glints, no dither — against which
    the mint rose window and the chalkboard become the lights in the dark
    (the thesis title glowing against the institution); a great GILT
    MULTI-ORDER ARCH (lit stone, a gold band set with studs, a deep red
    piping) carried down onto two ornamented piers, each with a gold-trimmed
    arris and a lit NICHE holding a little gold owl of the Academy — the
    reference's flanking statues, in Strix's own species. Baked order is
    depth: shell, field, rose, arch, piers; the valance comes later, after
    the chalkboard place(), tucked INSIDE the frame."""
    bg = room.bg
    SHELL = (26, 19, 46, 255)              # the offstage dark
    SHELLF = (32, 22, 52, 255)             # its faint velvet fold
    FIELD = (40, 30, 66, 255)              # the opening's midnight backdrop
    FIELD2 = (48, 36, 76, 255)
    GLINT1 = (108, 92, 150, 255)           # the backdrop's static glitter
    GLINT2 = (74, 60, 108, 255)
    PIPE = (110, 32, 52, 255)              # the frame's deep red piping
    # 1. the shell, edge to edge, with velvet fold hints in the wings
    for y in range(0, VAULT_H):
        for x in range(0, room.W):
            bg.put(x, y, SHELL)
    for x in list(range(0, PIER_W["wx0"])) +              list(range(PIER_W["ex1"] + 1, room.W)):
        if (x * 3 // 4) % 3 == 0:
            bg.rect(x, 0, x, VAULT_H - 1, SHELLF)
    # 2. the opening: the midnight field and its glitter
    for y in range(0, VAULT_H):
        for x in range(ARCH_X0, ARCH_X1 + 1):
            if y > _arch_y(x):
                bg.put(x, y, FIELD if (x + y) % 2 else FIELD2)
    for gx in range(ARCH_X0, ARCH_X1 + 1):
        for gy in range(8, VAULT_H - 6):
            if gy > _arch_y(gx) + 5 and h2(gx, gy, 97) % 53 == 0:
                bg.put(gx, gy, GLINT1)
                if h2(gx, gy, 98) % 3 == 0:
                    bg.put(gx, gy - 1, GLINT2)
    # 3. the rose window — mint glass in a stone wheel, now a LIGHT against
    # the midnight field. Visible ONLY from the podium: the pit camera never
    # reaches it, so the grandest thing in the room belongs to the beat that
    # destroys him under it.
    rcx, rcy = ROSE_C
    for dy in range(-ROSE_R - 2, ROSE_R + 3):
        for dx in range(-ROSE_R - 2, ROSE_R + 3):
            q = (dx * dx + dy * dy) / float(ROSE_R * ROSE_R)
            if q <= 1.0:
                bg.put(rcx + dx, rcy + dy,
                       ROSEG[0] if q <= 0.08 else
                       (ROSEG[1] if q <= 0.4 else ROSEG[2]))
            elif q <= 1.5:
                bg.put(rcx + dx, rcy + dy, STONE[4] if q > 1.2 else STONE[1])
    for ax, ay in ((0, -1), (0, 1), (-1, 0), (1, 0),
                   (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)):
        for sp_ in range(2, ROSE_R):
            bg.put(int(rcx + ax * sp_), int(rcy + ay * sp_), ROSEG[3])
    bg.put(rcx, rcy, STONE[2])                          # the hub
    # 4. THE GILT ARCH — a 12px multi-order frame following the curve:
    # lit stone outer order, a gold band set with studs, deep red piping,
    # and a hard shadow cast into the opening below it
    for x in range(ARCH_X0, ARCH_X1 + 1):
        ay = int(_arch_y(x))
        bg.rect(x, ay - 9, x, ay - 7, STONE[1])
        bg.put(x, ay - 9, STONE[0])
        bg.rect(x, ay - 6, x, ay - 3, BRASSD[1])
        bg.rect(x, ay - 2, x, ay - 1, PIPE)
        bg.put(x, ay, (30, 20, 44, 255))
        bg.put(x, ay + 1, (36, 26, 54, 255))
        if x % 16 == 8:                                 # the jewel studs
            bg.rect(x - 1, ay - 6, x, ay - 5, BRASSD[0])
            bg.put(x + 1, ay - 4, BRASSD[3])
    # 5. THE PIERS: ashlar cores, gold-trimmed arrises, corbel caps at the
    # springing, a lit niche with a gold owl apiece, and the cast shadow
    # each throws east into the opening (light is NW)
    for px0, px1 in ((PIER_W["wx0"], PIER_W["wx1"]),
                     (PIER_W["ex0"], PIER_W["ex1"])):
        for y in range(10, VAULT_H):
            for x in range(px0, px1 + 1):
                bg.put(x, y, _ashlar_px(x, y))
        bg.rect(px0, 10, px1, 10, STONE[0])             # lit cap course
        bg.rect(px0, 11, px1, 11, STONE[1])
        for gx_ in (px0, px1 - 1):                      # gold-trimmed arrises
            bg.rect(gx_, 12, gx_, VAULT_H - 1, BRASSD[2])
            bg.rect(gx_ + 1, 12, gx_ + 1, VAULT_H - 1, BRASSD[1])
        # corbel band where the arch springs
        bg.rect(px0, ARCH_SPRING - 8, px1, ARCH_SPRING - 6, STONE[1])
        bg.rect(px0, ARCH_SPRING - 5, px1, ARCH_SPRING - 4, STONE[4])
        # THE NICHE: an arched recess of the opening's own dark, and the
        # little gold owl on a plinth — the Academy watching its own stage.
        # HIGH on the pier, above the masking legs' tops (y=64): the first
        # placement sat at mid-height and the curtains hid both statues
        # completely — the reference's figures sit up beside the arch, and
        # now so do these. Centre y=38: fully under the podium camera's
        # frame line by the time the dialogue starts.
        ncx, ncy = (px0 + px1) // 2, 38
        for dy in range(-13, 14):
            for dx in range(-6, 7):
                q = (dx * dx) / 36.0 + (dy * dy) / 169.0
                if q <= 1.0:
                    bg.put(ncx + dx, ncy + dy, FIELD)
                elif q <= 1.45:
                    bg.put(ncx + dx, ncy + dy,
                           BRASSD[1] if dy < 0 else STONE[4])
        bg.rect(ncx - 4, ncy + 7, ncx + 4, ncy + 9, BRASSD[2])   # the plinth
        bg.rect(ncx - 2, ncy - 3, ncx + 2, ncy + 6, BRASSD[1])   # the owl: body
        bg.rect(ncx - 2, ncy - 6, ncx + 2, ncy - 4, BRASSD[0])   # head, lit
        bg.put(ncx - 1, ncy - 5, (60, 40, 30, 255))              # eyes
        bg.put(ncx + 1, ncy - 5, (60, 40, 30, 255))
        bg.rect(ncx - 2, ncy - 7, ncx - 2, ncy - 7, BRASSD[0])   # ear tufts
        bg.rect(ncx + 2, ncy - 7, ncx + 2, ncy - 7, BRASSD[0])
        # the cast shadow east of the pier
        for y in range(11, VAULT_H):
            for x in range(px1 + 1, min(px1 + 5, room.W)):
                c = bg.get(x, y)
                bg.put(x, y, tuple(int(v * 0.72) for v in c[:3]) + (255,))
    # 6. the backdrop's foot: a near-black line where it meets the boards
    bg.rect(ARCH_X0, VAULT_H - 2, ARCH_X1, VAULT_H - 1, (30, 21, 48, 255))


_vault()


def _nave_walls():
    """The nave's side walls, rows 8-30: flat stone with an engaged PILASTER
    on every pew row (the same block every time, so the whole run dedupes to
    a handful of tiles) and a little baked sconce candle burning at each
    pilaster's head — the rhythm that walks you up the room. The pilaster is
    the respond idiom at 16px: a lit proud face, a dark reveal toward the
    room, a cast shadow row beneath."""
    m = room.m
    for ty in range(FR, 20):
        for tx in (2, 21):
            if m.at(tx, ty) != "#":
                continue
            x0, y0 = tx * T, ty * T
            left = tx == 2
            # the flat wall strip (over the default side_cell paint)
            for y in range(y0, y0 + T):
                for x in range(x0, x0 + T):
                    u = (x - x0) if left else (T - 1 - (x - x0))
                    if u == 0:
                        c = STONE[5]
                    elif u == 1:
                        c = STONE[4]
                    elif u >= 14:
                        c = STONE[4] if u == 14 else STONE[5]
                    else:
                        c = _ashlar_px(x, y, 1)
                    bgput = room.bg.put
                    bgput(x, y, c)
            if ty in PILASTER_ROWS:
                # the engaged pilaster: proud lit face + roomward reveal
                fx0 = x0 + (3 if left else 5)
                fx1 = x0 + (10 if left else 12)
                room.bg.rect(fx0, y0, fx1, y0 + T - 1, STONE[2])
                room.bg.rect(fx0, y0, fx1, y0, STONE[0])       # lit cap
                room.bg.rect(fx0 if left else fx1, y0 + 1,
                             fx0 if left else fx1, y0 + T - 1, STONE[1])
                room.bg.rect(fx1 if left else fx0, y0 + 1,
                             fx1 if left else fx0, y0 + T - 1, STONE[4])
                room.bg.rect(fx0, y0 + T - 1, fx1, y0 + T - 1, STONE[4])
                # the sconce flame at its head
                scx = (fx0 + fx1) // 2
                room.bg.put(scx, y0 + 3, FLAME)
                room.bg.put(scx, y0 + 4, FLAME_IN)
                room.bg.put(scx, y0 + 5, FLAME_CORE)
                room.bg.rect(scx - 1, y0 + 6, scx + 1, y0 + 8, WAX[1])
                room.bg.put(scx - 1, y0 + 6, WAX[0])


_nave_walls()


def _stage_boards():
    """THE STAGE FLOOR IS TIMBER — rows 8-9 repainted as warm boards over the
    flag paint (a stage is BUILT; the platform's material change against the
    cold stone house is the FF6 opera read, and it is what makes the riser
    below it read as a riser instead of a kerb). The ward-light pool rides
    the boards (lit cells blend toward mint), a 2px foot-shade band under
    the vault wall makes the platform meet it as a FLOOR PLANE, and the
    Academy's seal is inlaid in the boards behind the podium — the spot the
    boy is not allowed to stand on, and the spot the adult is destroyed on.
    The lectern and panel desk get board-native contact shadows here (the
    Room.bake_shadow flag repaint would stamp flagstone back onto the
    boards)."""
    from _interior import plank_px
    bg = room.bg
    # the walkable platform, frame edge to frame edge (the full-bleed band)
    m = room.m
    for ty in (FR, FR + 1):
        for tx in range(1, 23):
            # the w cells live under the opaque masking legs, never seen in
            # game — shadowed boards, so a solid cell can't dedupe to the
            # walkable platform's own tiles (the invisible-wall lint)
            if m.at(tx, ty) == "w":
                ramp6 = STAGE_SH
            else:
                ramp6 = STAGE_LIT if (tx, ty) in room.lit_cells else STAGEB
            x0, y0 = tx * T, ty * T
            for y in range(y0, y0 + T):
                for x in range(x0, x0 + T):
                    bg.put(x, y, plank_px(x, y, ramp6))
    # the border cells (rows 8-10, x0/x23): the same boards two steps down
    # with a near-black outer edge — the stage runs OFF the frame into the
    # offstage dark, and the value drop keeps the invisible-wall lint honest
    for ty in (FR, FR + 1, FR + 2):
        for tx in (0, 23):
            x0, y0 = tx * T, ty * T
            for y in range(y0, y0 + T):
                for x in range(x0, x0 + T):
                    bg.put(x, y, plank_px(x, y, STAGE_SH))
            ex0 = x0 if tx == 0 else x0 + 10
            bg.rect(ex0, y0, ex0 + 5, y0 + T - 1, (24, 17, 42, 255))
    # the vault wall's foot shade — an overhang that darkens nothing under
    # it is a line, not a wall
    bg.rect(1 * T, FR * T, 23 * T - 1, FR * T, STAGEB[4])
    bg.rect(1 * T, FR * T + 1, 23 * T - 1, FR * T + 1, STAGEB[3])
    # the inlaid seal, dead centre behind the podium: two board-tone rings
    # and four compass studs — quiet, but it names the spot
    scx, scy = ARCH_CX, FR * T + 6
    for dy in range(-5, 6):
        for dx in range(-11, 12):
            q = (dx * dx) / 121.0 + (dy * dy) / 25.0
            if 0.62 <= q <= 1.0:
                bg.put(scx + dx, scy + dy, STAGEB[4])
            elif 0.30 <= q <= 0.48:
                bg.put(scx + dx, scy + dy, STAGEB[0])
    for dx, dy in ((0, -5), (0, 5), (-11, 0), (11, 0)):
        bg.put(scx + dx, scy + dy, BRASSD[1])
    # board-native contact shadows under the lectern and the panel desk
    for chars in ("Ll", "J"):
        X, Y, XW, YH = room.px(room.bbox(chars))
        for y in range(Y + YH - 3, Y + YH):
            for x in range(X + 1, X + XW - 1):
                bg.put(x, y, plank_px(x, y, STAGE_SH))


_stage_boards()


def _tier_arc(x, top_row):
    """One pew tier's curve: nearest the stage at the aisle, HOUSE_ARC px
    deeper by the walls — the amphitheatre wrap, same grammar as _arch_y."""
    u = (x - ARCH_CX) / float(ARC_HALF)
    return top_row * T + int(HOUSE_ARC * u * u)


def _house_arcs():
    """THE HOUSE IS AN AMPHITHEATRE ("it is so boxy", 2026-08-04): the three
    pew tiers are drawn as ARCS centred on the podium, and the whole band
    falls away on a quantized RADIAL gloom centred on the stage — concentric
    rings of dark, which is what rounds the room's corners off without moving
    a single collision cell. Pure baked paint: the band is solid ambiance, so
    the art owes the grid nothing; the 30 audience NPCs ride the same curve
    via hall.gd's AUD_ARC nudge (keep the two constants married), and their
    heads against these backs are the whole FF6 crowd read. Collision stays
    the straight row-13 line, always NORTH of the art, so a body in the pit
    can never clip a pew back."""
    bg = room.bg
    X0, X1 = 3 * T, 21 * T - 1
    # 1. the house floor: dark flags under everything but the runner
    for y in range(13 * T, 19 * T):
        for x in range(X0, X1 + 1):
            if 10 * T <= x < 14 * T:
                continue
            bg.put(x, y, flag_px(x, y, STONE, 2))
    # 2. the pew-back arcs, broken at the aisle like real pews
    spans = (list(range(X0, 10 * T)), list(range(14 * T, X1 + 1)))
    for top in TIER_TOPS:
        for span in spans:
            for x in span:
                ay = _tier_arc(x, top)
                bg.put(x, ay, STAGEB[0])                  # lit crown rail
                bg.rect(x, ay + 1, x, ay + 6, STAGEB[2])  # panelled back
                if x % 12 == 0:
                    bg.rect(x, ay + 2, x, ay + 5, STAGEB[4])   # groove
                elif x % 12 == 1:
                    bg.rect(x, ay + 2, x, ay + 5, STAGEB[1])   # lit bevel
                bg.put(x, ay + 7, STAGEB[4])              # base rail
                bg.rect(x, ay + 8, x, ay + 9, STAGEB[5])  # shadow under it
                bg.rect(x, ay + 10, x, ay + 13, STAGEB[3])  # the seat below
        # scrolled end caps where the pews meet the aisle
        for ex in (10 * T - 2, 14 * T):
            ay = _tier_arc(ex, top)
            bg.rect(ex, ay, ex + 1, ay + 12, STAGEB[3])
            bg.rect(ex, ay, ex + 1, ay, STAGEB[1])
            bg.put(ex, ay + 1, STAGEB[0])
    # 3. the radial gloom — two quantized rings of dark centred on the stage
    centre = (ARCH_CX, 10 * T)
    TABLE = (STONE, STAGEB, RUGB)
    for y in range(13 * T, 20 * T):
        for x in range(2 * T, 22 * T):
            r = ((x - centre[0]) ** 2 + (y - centre[1]) ** 2) ** 0.5
            steps = 2 if r > 215 else (1 if r > 170 else 0)
            if not steps:
                continue
            c = bg.get(x, y)
            for mat in TABLE:
                if c in mat:
                    bg.put(x, y, mat[min(len(mat) - 1, mat.index(c) + steps)])
                    break
            else:
                k = 0.76 if steps == 1 else 0.56
                bg.put(x, y, tuple(int(v * k) for v in c[:3]) + (255,))


_house_arcs()


def _side_door():
    """The little service door in the west wall at the pit — the way the kid
    comes in (everybody enters this room from the wings: the adult through
    the west curtain leg, the kid through the side door; the great doors at
    the back are scenery). A modest arch, a dark leaf, a brass ring — the
    unbilled entrance, which is the point."""
    bg = room.bg
    x0, y0 = 2 * T, 11 * T + 2
    bg.rect(x0 + 2, y0, x0 + 13, y0 + 25, STONE[4])            # reveal
    bg.rect(x0 + 3, y0 + 2, x0 + 12, y0 + 25, (24, 18, 44, 255))   # the leaf
    for dx in range(3, 13):                                    # arched head
        t = abs(dx - 7.5) / 4.5
        bg.put(x0 + dx, y0 + 1 + int(2 * t * t), STONE[1])
    bg.rect(x0 + 4, y0 + 4, x0 + 11, y0 + 4, (54, 40, 70, 255))    # rail
    bg.put(x0 + 10, y0 + 14, BRASSD[1])                        # the ring
    bg.rect(x0 + 2, y0 + 26, x0 + 13, y0 + 27, STONE[1])       # threshold


_side_door()


def _door_glint():
    """The great doors, seen from the front of the house as a warm sliver in
    the gloom band — scenery now, not a walk (the opera restage: nobody
    walks the house). A distant arch of candlelight leaking around the door
    leaves, and the runner's last glint beneath it."""
    bg = room.bg
    cx, top = ARCH_CX, 19 * T + 2
    for x in range(cx - 12, cx + 13):
        t = abs(x - cx) / 12.0
        ay = top + int(5 * t * t)
        bg.put(x, ay, (120, 84, 62, 255))
        bg.put(x, ay + 1, (66, 44, 52, 255))
    bg.rect(cx - 10, top + 6, cx + 10, top + 11, (48, 30, 46, 255))
    bg.rect(cx - 1, top + 6, cx + 1, top + 11, (150, 104, 70, 255))  # the gap
    bg.rect(cx - 12, top + 12, cx + 12, top + 13, (58, 36, 60, 255))


_door_glint()

# ---- Tier-1 props at their map footprints ------------------------------------------
# the chalkboard rides the vault wall under the rose (its 32px art drops from
# the Q row into row 7, still all solid wall)
room.place("Q", chalkboard(96, 32, CHALK))
# the processional runner where bodies actually stand: the pit strip's two
# rows. Its continuation through the house is the solid _r_cell paint. The
# candle cell inside its bbox paints plain floor first and the rug blits
# over it — the bbox is what place() covers, not the char set.
room.place("g", rug(64, 32, RUGB, (198, 150, 96, 255)))


def _swag():
    """THE GREAT VALANCE — the reference's triple swag, hung INSIDE the gilt
    frame: three deep catenary scallops across the opening in TWO LAYERS of
    velvet (a dark under-swag hanging deeper than the lit over-swag), gold
    fringe on both hems, tassels at the gather points, a little gilt CLOCK
    cartouche at the centre top (the reference has one; a lecture hall has
    every reason to), and a gathered TAIL falling the full height of each
    pier's inner face — which the y-sorted masking legs then continue below
    the swag line: one unbroken curtain from valance to stage boards. Drawn
    AFTER the chalkboard place() so the fabric hangs over the board's top
    frame (the title, y>=102, stays legible under the deepest dip), and
    every column is clipped to start INSIDE the arch (max of the valance
    line and the frame's own curve) — the velvet is inside the gold, never
    over it. The under-hem's deepest reach is y96, the board's own top
    frame row: the fabric kisses the frame, the title stays legible. All Tier 1: solid wall rows, baked order is depth."""
    bg = room.bg
    span = (ARCH_X1 - ARCH_X0 + 1) // 3
    fold = (1, 2, 1, 3, 2, 1, 2, 3, 1, 2, 1, 3, 2)
    def hem(x, extra):
        u = ((x - ARCH_X0) % span) / float(span)
        return VAL_Y0 + 8 + int((VAL_DIP + extra) * 4.0 * u * (1.0 - u))
    # the under-swag: darker, deeper — the doubled velvet's shadowed layer
    for x in range(ARCH_X0, ARCH_X1 + 1):
        top = max(VAL_Y0 + 4, int(_arch_y(x)) + 2)
        dip = hem(x, VAL_UNDER)
        if dip > top:
            bg.rect(x, top, x, dip, CURT[3 if (x * 3 // 4) % 3 else 4])
            bg.put(x, dip, CURT[4])
            bg.put(x, dip + 1, BRASSD[2])                  # under-fringe
    # the over-swag: the lit layer riding shallower on top of it
    for x in range(ARCH_X0, ARCH_X1 + 1):
        top = max(VAL_Y0, int(_arch_y(x)) + 2)
        dip = hem(x, 0)
        if dip > top:
            bg.rect(x, top, x, dip, CURT[fold[(x * 3 // 4) % len(fold)]])
            bg.put(x, top, CURT[0])                        # lit top roll
            bg.put(x, dip, CURT[4])                        # turned-under hem
            bg.put(x, dip + 1, BRASSD[1])                  # the gold fringe
            if x % 4 == 0:
                bg.put(x, dip + 2, BRASSD[2])              # fringe drops
    # tassels at the two interior gathers, rosettes at the pier gathers
    for gx in (ARCH_X0 + span, ARCH_X0 + 2 * span):
        bg.rect(gx - 1, VAL_Y0 + 4, gx + 1, VAL_Y0 + 10, CURT[2])
        bg.rect(gx, VAL_Y0 + 11, gx, VAL_Y0 + 15, BRASSD[2])   # the cord
        bg.rect(gx - 1, VAL_Y0 + 16, gx + 1, VAL_Y0 + 19, BRASSD[1])
        bg.put(gx, VAL_Y0 + 20, BRASSD[2])                 # the tassel tip
    for gx in (ARCH_X0 + 1, ARCH_X1 - 1):
        bg.rect(gx - 2, VAL_Y0 + 1, gx + 2, VAL_Y0 + 6, CURT[2])
        bg.put(gx, VAL_Y0 + 3, BRASSD[1])
    # the gilt clock cartouche at the centre top — small, round, and telling
    # the hour nobody in either beat is watching
    ccx, ccy = ARCH_CX, VAL_Y0 + 3
    for dy in range(-4, 5):
        for dx in range(-5, 6):
            q = (dx * dx) / 25.0 + (dy * dy) / 16.0
            if q <= 0.55:
                bg.put(ccx + dx, ccy + dy, PAPERC)
            elif q <= 1.0:
                bg.put(ccx + dx, ccy + dy,
                       BRASSD[0] if dy < 0 else BRASSD[1])
    bg.put(ccx, ccy - 1, (60, 44, 60, 255))                # the hands
    bg.put(ccx + 1, ccy, (60, 44, 60, 255))
    # the grand tails: gathered velvet the full width of each pier's inner
    # face, valance to the stage boards (the y-sorted LEGS hang in the wings
    # in front of these — baked behind, sorted in front, two depths of the
    # same curtain)
    for tx0, tx1 in ((ARCH_X0, ARCH_X0 + 13), (ARCH_X1 - 13, ARCH_X1)):
        for x in range(tx0, tx1 + 1):
            top = max(VAL_Y0 + 6, int(_arch_y(x)) + 2)
            bg.rect(x, top, x, VAULT_H - 3,
                    CURT[fold[((x - tx0) * 3 // 4) % len(fold)]])
        bg.rect(tx0, VAULT_H - 2, tx1, VAULT_H - 1, CURT[4])   # hem at the boards


_swag()

# ---- free-standing (Tier 3, y-sorted) ------------------------------------------------
# the lectern — THE PODIUM — dead on the map's midline; a body rounds it and
# the naming presents from the tuck row behind it. Its contact shadow is
# board-native, baked in _stage_boards (Room.bake_shadow would repaint flag)
room.emit_prop("Lectern", "Ll", sprite_img(lectern(64, 32), 64, 32))
# the judging panel's long desk on the stage's EAST flank (stage left — the
# west wing stays clear for Basil's stage-right entrance); the lamp flame
# burns chalk-mint, the Academy's ward-light. Board-native shadow, as above.
# 80px since the opera restage: the east curtain leg owns the last cell.
room.emit_prop("PanelDesk", "J", sprite_img(desk(80, 32, CHALK), 80, 32))
# the stage apron: the riser face closing the platform's south edge — one
# full-width y-sorted entity over the solid D row, opaque across its
# footprint (the T3 coverage rule — the sealed stage stays sealed). No baked
# shadow: the art is opaque over its whole footprint, nobody sees the floor.
room.emit_prop("StageFront", "D", sprite_img(stage_front(352, 32), 352, 32))
# the TWIN CURTAIN LEGS are MASKING FLATS (2026-08-04, "how are they going
# to exit stage left or right when the curtains are that thin?"): 48px of
# velvet over a one-cell block (a Tier-3 sprite may be wider than its
# block), proscenium height, each spanning its ENTIRE wing — the west leg
# covers x32-80, dead on the pier face, so the y-sorted leg below the swag
# line continues the baked pier tail above it: one unbroken curtain from
# swag to stage boards, three cells deep. A body in the wing is genuinely
# SWALLOWED: the adult spawns fully hidden and steps out of the velvet on
# the Dean's summons, and the flee carries him back into it before the
# modulate fade even lands. Everybody enters and leaves this room from the
# wings. No bake_shadow: their contact rows are covered by the StageFront.
room.emit_prop("CurtainLeg", "c", sprite_img(curtain_leg(48, 96, CURT), 48, 96),
               each=True)

# ---- THE FLOATING CANDLES (Tier 3, hframes=4 — hall.gd cycles + douses them) --------
# One cell per candle, asserted: each=True stretches one sprite across a
# fused component, and two adjacent chars would ship as one smeared candle.
for ch in "*+%^&":
    for comp in room.comps(ch):
        assert len(comp) == 1, \
            f"candle char {ch!r} component {comp} spans {len(comp)} cells " \
            f"— every floating candle is exactly one cell"
# high over the centre aisle / mid in the side aisles / low over the pit and
# narthex: three hang heights so the drift reads as FLOATING, not as lamps
# on a shelf. Negative anchor=top hangs the art above its own walkable cell;
# the vault candles (^) sit bottom-anchored in their solid wall cells.
room.emit_prop("CandleHigh", "*", floating_candle(salt=91), top=-52,
               hframes=4, each=True)
room.emit_prop("CandleMid", "+", floating_candle(salt=92), top=-44,
               hframes=4, each=True)
room.emit_prop("CandleLow", "%", floating_candle(salt=93), top=-36,
               hframes=4, each=True)
room.emit_prop("CandleVault", "^", floating_candle(salt=94),
               hframes=4, each=True)
room.emit_prop("CandleAmb", "&", floating_candle(salt=95), top=-40,
               hframes=4, each=True)


def _dab(img, cx, cy, r, color, a):
    """One radial dab composited by MAX-ALPHA — glow_blob's put() would cut
    its own zero-alpha rim into the broad wash under it, scalloping the nave
    into rings. A dab may only ever RAISE a pixel's alpha."""
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            q = (dx * dx + dy * dy) / float(r * r)
            if q > 1.0:
                continue
            na = int(a * (1.0 - q))
            base = img.get(cx + dx, cy + dy)
            if base is None or na > base[3]:
                img.put(cx + dx, cy + dy, color + (na,))


def _glow(img):
    # one broad candle-warm wash down the whole nave FIRST — the overlay
    # renders UNDER the y-sorted World, so the light must land on the ground
    # as ONE continuous field (per-candle dabs alone scallop the floor into
    # circles); everything after may only raise alpha over it
    for y in range(FR * T, 19 * T):
        img.rect(2 * T, y, 22 * T - 1, y, (255, 200, 120, 10))
    # cool ward-light washing down off the chalkboard onto the stage — the
    # Academy's signature, kept from the old room
    bx0, by0, bxw, _byh = room.px(BOARD)
    bx1 = bx0 + bxw - 1
    bottom = (FR + 2) * T
    for y in range(by0 + 6, bottom):
        a = int(40 * (1.0 - (y - by0 - 6) / float(bottom - by0 - 6)))
        img.rect(bx0 - 4, y, bx1 + 4, y, (150, 240, 214) + (a,))
    # the rose window's mint halo
    rcx, rcy = ROSE_C
    _dab(img, rcx, rcy, ROSE_R + 9, (150, 240, 214), 34)
    # ...and a soft warm core under every candle, floating or baked
    m = room.m
    spots = []
    for ty in range(m.rows_n):
        for tx in range(m.cols):
            ch = m.at(tx, ty)
            if ch in "*+%&":
                hang = {"*": 52, "+": 44, "%": 36, "&": 40}[ch]
                spots.append((tx * T + 8, ty * T - hang + 8))
            elif ch == "^":
                spots.append((tx * T + 8, ty * T + 8))
    for ty in PILASTER_ROWS:                       # the baked wall sconces
        if ty != 11:                               # west row 11 is the side door
            spots.append((2 * T + 7, ty * T + 5))
        spots.append((21 * T + 9, ty * T + 5))
    for px0, px1 in ((PIER_W["wx0"], PIER_W["wx1"]),   # the pier niches' owls
                     (PIER_W["ex0"], PIER_W["ex1"])):
        spots.append(((px0 + px1) // 2, 38))
    for cx, cy in spots:
        _dab(img, cx, cy, 10, (255, 200, 120), 46)


room.write_glow(_glow)
# No south_lift and no upper layer at all (2026-08-04): the opera restage has
# no south wall a body can press and no walk-behind bake — everything that
# ever draws over a body here is y-sorted (the riser, the curtain leg, the
# candles). _check_art.py's UPPER_REQUIRED table carries the exemption.
room.finish()
