#!/usr/bin/env python3
"""THE SCHOLARLY-TRADE LAYER — the dressing that says somebody LIVES and TRADES
in a canopy village, at ZONE scale (48px character cell, 33px figure, 16px tiles).

`_town_props` and `_tree_props` build the town: walls, roofs, decks, ladders,
trunks, the hoist. Between them they can raise a whole village and it will still
read as UNINHABITED, because a settlement is not a set of buildings — it is a set
of CLAIMS about what happens inside them. This module is only those claims. It
draws no structure at all; every piece here is something a person hung, pinned,
propped or filled, and every piece is an argument about the local economy.

THE ARGUMENT IS: SCHOLARSHIP IS THE INDUSTRY, AND MAGIC IS A LICENSED TRADE.
Hogsmeade grown in a tree — an old village whose trades happen to be the ones a
university town has. Crooked hand-painted boards on wrought-iron brackets. An
apothecary's bottles racked in a leaded window. A notice board thick enough that
the town clearly has both bureaucracy and gossip. A messenger-bird roost, because
the post here is a bird. Candle lanterns on hooks, because the lamps are lit by
hand every evening by somebody whose job that is.

FOUR THINGS THIS FAMILY IS NOT, and each of them is a failure this file exists to
avoid rather than a taste I happen to hold:

  * NOT wizard-hat whimsy. No pointed hats, no stars-and-moons, no wands, no
    lightning. A costume is not a culture. Every object here is a WORKING object
    belonging to an adult who is bad at their feelings, which is the register of
    this whole game; the joke, where there is one, is played straight (the
    weaponsmith's board is a TOOTH, and nobody in town finds that funny).
  * NOT LETTERED. There is no font in this game and painted words at 16px are
    mud, so a trade is announced by its OBJECT — a fang, a flask, a kettle, a
    quill. That constraint is a gift: an object-sign is what a real pre-literate
    high street actually used, and it dates the town four hundred years back
    without a single word.
  * NOT NEW. Every piece is meant to have been there a while: the sign swings
    because its eyes are worn, one notice has been torn off its pin and the pin
    is still there, the flask on the apothecary's board is CRACKED and they never
    repainted it.
  * NOT candy. `ramp()` pulls a dark end toward violet AND raises its
    saturation, and on the two pale materials this family is mostly made of —
    paper and paint — that law arrives at pink. See PAPER_STOCK.

HOW THIS KIT DIFFERS FROM ITS TWO NEIGHBOURS, deliberately:

  * every builder takes its MATERIAL RAMPS as parameters, the `_tree_props`
    contract rather than `_town_props`' closed-over FOLIAGE/CEMENT: culture
    dressing has to sit on a ground town, a canopy town and (eventually) a
    snowbound one, and a builder that cannot be handed a ramp cannot cross
    between them. Only the shared HARDWARE STORE (iron, brass, copper, glass,
    the WARM candle pair) is taken as read.
  * nothing here is STRUCTURE, so nothing here is opaque tiled fabric and
    nothing dedupes. These are Tier-3 y-sorted props and facade inlays, one-off
    by nature, which is why they can afford full per-pixel shading the way
    `_overworld_props`' landmarks do.
  * every piece is authored to work WITH NOTHING BEHIND IT. A sign hangs off a
    flank into open air, a lantern hangs off a fascia over a drop. That is the
    opposite of `_town_props`' facades, which may lean on the wall they are
    drawn onto.

Palette discipline (docs/DESIGN.md "Art Direction"): hard flat bands, NO dither
inside a form (`_propkit.S` pins the Sprite's jitter to 0, so ball/blob come out
as clean CT bands). Warm light is MIX-blended toward WARM, never additive cream —
cream at ~250 added onto a saturated field saturates every channel and arrives
white, which is why the candle's core is WGLINT and never SPEC.

Stdlib-only, deterministic (fixed salts). Consumed by an
assets/_gen_tileset_<town>.py through `emit_prop()` for the y-sorted pieces and
by a building builder for `bottle_window`, which is a hole in a wall.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import h2
from _overworld_props import DOORDARK, WARM, WARMD
from _propkit import S, ln, edge
from _tilekit import (Img, sprite_img, BRASS, COPPER, GLASS, IRON, SPEC, STEEL,
                      PAPER)
from _town_props import WGLINT, _breathe, _wash, clipw, WIN_PULSE
from _tree_props import THATCH

# ---- the three hand-pinned materials -------------------------------------------------
# Everything else this family is made of already exists: IRON/BRASS/COPPER/GLASS
# from the shared hardware store, WARM/WARMD/WGLINT from the game's one warm
# ladder, THATCH for straw (imported rather than re-pinned — the huts' roofs and
# a roost's bedding are the same dry reed, and a town gets ONE straw), and the
# scene's own wood/leaf/glass ramps handed in by the generator.
#
# PAPER_STOCK — old notice paper. HAND-PINNED, and it is not close:
#
#     ramp((238, 226, 196), "violet", 4)
#         -> (254,253,252)  (238,226,196)  (230,144,137)  (228,83,152)
#
# tone 2 is SALMON and tone 3 is HOT MAGENTA. This is the ROPE/THATCH law
# arriving at its worst case: a pale warm seed has nowhere to go but up in
# saturation as it goes down in lightness, so the violet pull lands on pink. A
# notice board is a stack of overlapping paper and the ONLY thing separating one
# sheet from the next is those two dark tones, so derived, the single piece in
# this family whose whole job is "this town has bureaucracy" comes out a stack of
# pink post-its — the exact "very kiddy" failure mode, arrived at by obeying the
# palette code instead of the palette doctrine.
#
# So: rag paper, honestly warm oatmeal, foxed at the edges. Four tones, because
# layered paper needs a field, a lit face, a curl-underside AND the shadow one
# sheet throws on another, and collapsing the last two makes the stack flat. The
# darkest is pulled a little violet by hand so it still sits in a teal- or
# violet-biased scene instead of glowing brown out of it, and `_tilekit.PAPER`
# (240,232,226) is deliberately NOT reused as the field: at that value against a
# dark board every sheet is the same near-white and the layering vanishes.
PAPER_STOCK = ((244, 236, 218, 255),      # a sheet that went up this morning
               (222, 208, 180, 255),      # the field: rag paper, warm oatmeal
               (184, 168, 144, 255),       # foxed edge, a curled corner's back
               (120, 104, 110, 255))      # the shadow paper throws on paper

# GUILD — the paint on a trade board, and the same paint on ALL FOUR of them.
# That is the culture argument, not a shortcut: four boards in four different
# colours are four shopkeepers who each bought a pot, while four boards in ONE
# colour are a town that LICENSES its trades and has a painter on the payroll.
# It is deliberately the verdigris the coppersmith's own patina makes (compare
# _town_props.VERD), so the town's pigment and the town's metal have a shared
# origin the way a real one would.
#
# HAND-PINNED for a different reason than PAPER_STOCK — not because ramp() goes
# pink but because it goes BLACK:
#
#     ramp((38, 86, 84), "violet", 4)
#         -> (68,128,120)  (38,86,84)  (15,31,43)  (0,0,1)
#
# `_ramp_curve` lifts and drops from the SEED's lightness, and a deep seed has
# almost no room below it: tone 3 arrives at (0,0,1), which is DARKER than
# OUTLINE (26,17,36), so the board's own shadow band eats its silhouette edge and
# the sign stops having a shape. The lit end barely clears the seed at the same
# time, so the board has no form either. Pinned, the four tones span a real range
# and tone 3 stays clearly above OUTLINE.
GUILD = ((74, 150, 140, 255),             # the crown, where the sky reaches it
         (44, 108, 106, 255),             # the field
         (28, 68, 80, 255),               # the lower band, in the board's shade
         (18, 44, 60, 255))               # the device's cast line, and cracks

# PAINT — the sign-painter's cream: the fillet run round every board and the
# highlight on every painted device. Hand-pinned for PAPER_STOCK's exact reason
# (a cream seed derives to (249,130,119) coral and (255,57,148) shocking pink),
# and it matters more here than anywhere else in the family because a fillet is
# ONE PIXEL WIDE — there is no area to average a bad tone out over, so a single
# wrong value is the whole read. Two tones only: a hand-loaded brush lays down
# heavy then thin, and that unevenness is what says "painted" instead of
# "printed".
PAINT = ((250, 238, 200, 255), (212, 188, 146, 255))

# The apothecary's stock, as (glass, contents) pairs. Pinned rather than derived
# for the third time and the plainest reason: MINT and VIOLETF are single accent
# colours with no ramp behind them at all, and BRASS[2..3] — the obvious amber —
# are the ramp's violet law gone hot red and magenta, i.e. unusable. Every bottle
# needs a lit glass tone AND a saturated liquid tone, so all eight values are
# authored. Four bottles, four tints, one of them EMPTY: a shelf where every jar
# is full is a display, and a shelf with an empty one is a shop.
TINTS = (((150, 246, 168, 255), (40, 132, 96, 255)),      # a green tincture
         ((198, 148, 238, 255), (92, 56, 146, 255)),      # a violet spirit
         ((238, 188, 108, 255), (152, 96, 44, 255)),      # an amber oil
         ((206, 222, 238, 255), (112, 124, 158, 255)))    # empty — plain glass


# ---- the three animation cycles ------------------------------------------------------
# Every frame-dependent term in this file is periodic in its own cycle and every
# POSITIONAL term is zero-mean, which is the rule the animated water, the window
# breath and the dinghy car all live under (`_tree_props.SWAY`'s note states it):
# a term with a non-zero mean does not oscillate, it TRAVELS, and a swinging sign
# that travels is a sign sliding off a building.

SIGN_SWAY = (0, 1, 0, -1)     # rest, over, rest, back. Mean 0, period 4, and
                              # SIGN_SWAY[0] = 0 so a still bake is the art as
                              # drawn. A pendulum, not a drift.

CANDLE_FLICK = (0, 1, 0, -1)  # the candle's whole animation, driving THREE terms
                              # off one number — the flame's height, the lean of
                              # its tip, and how far its light reaches into the
                              # lantern. All three are mean-0 by construction
                              # because they are affine in this, which is the
                              # only way I know to keep a 3-term flicker honest.

BREATH2 = (0, 1)              # the bottle window's breath, as WIN_PULSE levels.
                              # ONE step, not three: at travel_scene's 0.18s
                              # ANIM_STEP a 2-frame cycle is 0.36s, and a 3-step
                              # ladder crammed into that strobes like a fault
                              # rather than breathing. A 2-cycle is also its own
                              # reverse, so it cannot read as travel no matter
                              # what the levels are — the direction problem
                              # SIGN_SWAY has to solve does not exist here.


# ---- shared sub-builders --------------------------------------------------------------

def _mirror(sp, w):
    """Flip a prop's `w`-wide art about its own centreline — the `rope_ladder`
    `face` idiom, so a wall-mounted piece can hang off either flank of a
    building without a second set of coordinates."""
    for y in range(sp.n):
        row = sp.px[y]
        row[0:w] = row[0:w][::-1]


def _sheet(w, h, salt, frames, draw, face=1):
    """A horizontal frame-sheet Img from a per-frame `draw(sp, f)`.

    Every frame is drawn from scratch and outlined SEPARATELY, which is the
    difference between this and `_town_props._finish`: that one outlines a base
    once and only recolours per frame, because a breathing window never moves.
    Here things MOVE — a board swings, a flame changes height — so the
    silhouette changes and a shared outline would leave the old edge behind as a
    1px ghost trailing the motion.
    """
    out = Img(w * max(1, frames), h)
    for f in range(max(1, frames)):
        sp = S(w, h, salt)
        draw(sp, f)
        edge(sp, h)                 # clears the dilated row at y == h
        clipw(sp, w)                # and the dilated columns at x >= w
        if face < 0:
            _mirror(sp, w)
        out.blit_cell(sp, f * w, 0)
    return out


def _iron_bracket(sp, iron, x0, y0, reach, drop=8):
    """A WROUGHT-IRON BRACKET scrolling out of a wall: a bolted fixing plate on
    the wall face at x0, a two-pixel arm reaching `reach` px east from it, an
    ogee STAY rising from low on the plate to meet the arm's middle, and a
    volute curling off each end.

    The scrolls are authored pixel lists and not arcs, and that is the whole
    reason this helper exists. A quarter-circle drawn by maths at this scale is
    four pixels in a staircase and reads as a mistake; a smith's volute is a
    SHAPE somebody decided on, so it has to be decided on here too. `y0` is the
    arm's top row. Returns the arm's outboard x."""
    sp.rect(x0, y0 - 2, x0 + 2, y0 + drop, iron[2])           # the fixing plate
    sp.rect(x0, y0 - 2, x0, y0 + drop, iron[1])
    sp.rect(x0 + 2, y0 - 2, x0 + 2, y0 + drop, iron[3])
    for by in (y0 + 1, y0 + drop - 2):                        # its two bolts
        sp.set(x0 + 1, by, iron[0])
        sp.set(x0 + 1, by + 1, iron[3])
    ax1 = x0 + reach
    sp.rect(x0 + 2, y0, ax1, y0, iron[1])                     # the arm, 2px
    sp.rect(x0 + 2, y0 + 1, ax1, y0 + 1, iron[3])
    # THE STAY: an ogee, drawn as two runs that meet — flat off the plate, then
    # rising into the arm. One straight diagonal read as a strut on a road sign.
    for i, (sx, sy) in enumerate(((0, drop), (1, drop), (2, drop - 1),
                                  (3, drop - 2), (4, drop - 3), (5, drop - 4),
                                  (6, drop - 5), (6, drop - 6), (7, drop - 7))):
        sp.set(x0 + 2 + sx, y0 + sy, iron[2] if i % 2 else iron[1])
        sp.set(x0 + 2 + sx, y0 + sy + 1, iron[3])
    for vx, vy in ((0, drop + 2), (1, drop + 3), (2, drop + 3), (2, drop + 2)):
        sp.set(x0 + 1 + vx, y0 + vy, iron[2])                 # the stay's volute
    for i, (vx, vy) in enumerate(((1, 0), (2, 1), (2, 2), (1, 3), (0, 3),
                                  (0, 2))):
        sp.set(ax1 + vx, y0 + vy, iron[1] if i < 2 else iron[3])   # the terminal
    return ax1


def _eye_and_ring(sp, iron, x, y):
    """An EYE screwed into the underside of a bracket arm and a RING hanging
    through it — the two pixels of hardware that make a board read as SWINGING
    rather than as bolted flat to a wall.

    The ring is drawn as a 3x3 with its centre left EMPTY, and the hole is the
    entire point: a filled 3x3 is a rivet, and a rivet does not swing. `y` is
    the arm's bottom row; returns the row the board's hanger shank starts on."""
    sp.set(x, y + 1, iron[1])                                 # the eye's shank
    sp.rect(x - 1, y + 2, x + 1, y + 2, iron[1])              # the ring, open
    sp.set(x - 1, y + 3, iron[2]); sp.set(x + 1, y + 3, iron[2])
    sp.rect(x - 1, y + 4, x + 1, y + 4, iron[3])
    return y + 5


# ---- 1. THE TRADE SIGN ---------------------------------------------------------------

# THE BOARD'S SILHOUETTE, as one half-width per row, top to bottom. A shaped
# board, not a rectangle, and the shape is doing real work: a rectangle hanging
# off a bracket is a PANEL — a notice, a shutter, a bit of cladding — while a
# board with chamfered top corners and a tongue cut on the bottom is a thing
# somebody SAWED to hang up. It is also the same shape on all four signs,
# because the town's sign-painter cut all four (see GUILD).
_BOARD = (9, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 10, 9, 7, 5, 3, 2)

# Three insets off that one table, and they have to be derived from it rather
# than written down, because the board TAPERS: a constant left of 8 that is
# comfortably inside the paint at the waist is out in open air by the tongue, and
# the first pass had the kettle's foot floating beside the board for exactly that
# reason. So — the paint stops 1px short of the plank (a brush stops short of an
# edge), the fillet 2px inside the paint, and the device 1px inside the fillet.
_PAINT_IN, _FILLET_IN, _DEV_IN = 1, 3, 4


def _board_paint(sp, wood, r, y, half):
    """One row of the board: a sawn plank, then the paint inset 1px so the raw
    edge shows all the way round.

    That 1px of bare wood is the single cue that makes this a painted BOARD and
    not a painted shape. Filled edge-to-edge with GUILD the sign came out as a
    flat teal blob with a picture on it — the paint has to stop short of the
    edge the way a brush actually stops short of an edge."""
    sp.rect(15 - half, y, 15 + half, y, wood[3])              # the plank
    sp.set(15 - half, y, wood[1])                             # its lit arris
    sp.set(15 + half, y, wood[5])                             # and its shaded one
    if r == 0:
        sp.rect(15 - half, y, 15 + half, y, wood[1])          # the top rail,
        return                                                # catching the light
    if r >= len(_BOARD) - 2 or half < 3:
        return                                                # the tongue: no room
    ih = half - 1
    k = 0 if r <= 2 else 1 if r <= 12 else 2                  # three hard bands,
    sp.rect(15 - ih, y, 15 + ih, y, GUILD[k])                 # never a gradient


def _fillet(sp, ys, halves):
    """The painted BORDER RUN, inset two pixels from the board's paint and
    following its shape — including round the chamfers and down onto the
    tongue, which is why it is drawn from the half-width table rather than as a
    rectangle. A straight-sided fillet on a shaped board reads as a label stuck
    onto it.

    The horizontal step at every change of half-width is what closes the run: a
    fillet drawn as two side columns leaves a gap at each taper and comes out as
    a dashed line."""
    prev = None
    for r, (y, half) in enumerate(zip(ys, halves)):
        ih = half - 3
        if ih < 2:
            prev = None
            continue
        c = PAINT[0] if r < len(halves) // 2 else PAINT[1]
        if prev is None:                                      # the run's top,
            sp.rect(15 - ih, y, 15 + ih, y, c)                # closed across
        else:
            for side in (-1, 1):
                a, b = sorted((15 + side * ih, 15 + side * prev))
                sp.rect(a, y, b, y, c)
        prev = ih
    for r in range(len(halves) - 1, -1, -1):                  # and the run's foot
        ih = halves[r] - 3
        if ih >= 2:
            sp.rect(15 - ih, ys[r], 15 + ih, ys[r], PAINT[1])
            break


def _dev_fang(sp, cy):
    """THE BRASS FANG — the weaponsmith. A curved tooth, root at the top,
    tapering and swinging west to a point.

    A TOOTH and not a blade, and the choice is the joke: a sword on a sign is
    heraldry, a tooth is a claim about what the shop's work is FOR, and nobody in
    the scene finds it funny. Authored row by row because the curve is only ten
    rows long — a maths curve at this length is a staircase."""
    rows = ((3, 6), (3, 6), (3, 6), (3, 5), (2, 5), (2, 5), (2, 4), (1, 3),
            (1, 3), (1, 2), (0, 1), (0, 0))
    for i, (a, b) in enumerate(rows):
        y = cy - 5 + i
        sp.rect(15 + a, y, 15 + b, y, BRASS[1])
        sp.set(15 + a, y, BRASS[0])                           # the lit arris
        sp.set(15 + b, y, IRON[3])                            # the shaded flank
    sp.rect(16, cy - 5, 20, cy - 5, BRASS[0])                 # the root's crown
    sp.set(15, cy + 7, IRON[3])                               # the point
    sp.set(17, cy - 4, SPEC)


def _dev_flask(sp, cy):
    """THE CRACKED FLASK — the apothecary. A round-bottomed boiling flask with a
    flared lip, mint tincture standing in the bulb, and a CRACK.

    The crack is the whole sign. A clean flask says "chemist"; a flask painted
    with a crack in it and never repainted says the apothecary has been here long
    enough to be famous for an accident, which is a town with a history in one
    pixel run."""
    sp.rect(13, cy - 6, 17, cy - 5, GLASS)                    # the flared lip
    sp.rect(13, cy - 5, 17, cy - 5, STEEL[1])
    sp.rect(14, cy - 4, 16, cy - 1, GLASS)                    # the neck
    sp.rect(16, cy - 4, 16, cy - 1, STEEL[1])
    sp.blob(15, cy + 2, 5.2, 3.8, GLASS)                      # the bulb
    sp.blob(15, cy + 3, 4.6, 2.6, TINTS[0][0])                # the tincture,
    sp.blob(15, cy + 4, 4.0, 1.6, TINTS[0][1])                # standing in it
    sp.rect(11, cy + 1, 19, cy + 1, GLASS)                    # the meniscus
    sp.set(12, cy, SPEC); sp.set(13, cy - 1, SPEC)            # the NW catch
    for cx, cyy in ((11, cy + 1), (12, cy), (12, cy + 2), (13, cy + 3),
                    (14, cy + 4), (13, cy + 5)):
        sp.set(cx, cyy, GUILD[3])                             # the crack


def _dev_kettle(sp, cy):
    """THE COPPER KETTLE — the inn. A fat kettle with a bail handle, a spout,
    and a steam curl coming off it.

    Fat is load-bearing. A tall pot is an alembic and this town is full of them;
    a squat wide one with a bail over the top is a KETTLE, i.e. somewhere you
    can sit down, which is the one thing an inn sign has to say."""
    sp.rect(11, cy, 20, cy + 1, COPPER[2])                    # the lid, and its
    sp.rect(11, cy, 20, cy, COPPER[1])                        # lit crown
    sp.rect(15, cy - 2, 16, cy - 1, BRASS[1])                 # the lid's knob
    sp.blob(16, cy + 4, 5.0, 3.4, COPPER[2])                  # the body
    sp.blob(15.4, cy + 3, 3.6, 2.2, COPPER[1])                # its NW band
    sp.blob(16, cy + 6, 4.2, 1.4, COPPER[4])                  # and its foot
    for sx, sy, c in ((12, cy + 3, COPPER[2]), (11, cy + 3, COPPER[1]),
                      (11, cy + 2, COPPER[1]), (10, cy + 2, COPPER[2]),
                      (10, cy + 1, COPPER[2]), (12, cy + 4, COPPER[4])):
        sp.set(sx, sy, c)                                     # the spout
    sp.set(10, cy, COPPER[4])                                 # its open bore
    for hx, hy in ((11, cy - 1), (12, cy - 2), (13, cy - 3), (15, cy - 3),
                   (17, cy - 3), (19, cy - 2), (20, cy - 1)):
        sp.set(hx, hy, IRON[1])                               # the bail, over
        sp.set(hx, hy + 1, IRON[3])                           # the lid
    for kx, ky in ((9, cy - 1), (8, cy - 2), (8, cy - 3), (9, cy - 4),
                   (10, cy - 4), (10, cy - 3)):
        sp.set(kx, ky, PAINT[0])                              # the steam curl,
    sp.set(9, cy - 3, PAINT[1])                               # painted, not puffed


def _dev_quill(sp, cy):
    """THE QUILL — the scribe, and the library. A feather laid ACROSS an open
    book.

    Across, not beside. Two objects side by side are a list; one object lying
    over another is a scene, and the scene is somebody in the middle of copying
    something out. The book's gutter is drawn as a dark V rather than a straight
    line because an open book's pages fan, and a straight gutter reads as a
    closed box."""
    for i, (a, b) in enumerate(((7, 7), (6, 7), (6, 6), (5, 5))):
        y = cy + 1 + i
        sp.rect(15 - a, y, 15 - 1, y, PAINT[0])               # the two page
        sp.rect(15 + 1, y, 15 + b, y, PAINT[0])               # blocks
        sp.rect(15 - a, y, 15 - a, y, PAINT[1])
        sp.rect(15 + b, y, 15 + b, y, PAINT[1])
    for i in range(4):                                        # the gutter's V
        sp.set(15, cy + 1 + i, GUILD[3])
    sp.rect(8, cy + 5, 22, cy + 5, PAINT[1])                  # the fore-edges
    sp.rect(9, cy + 6, 21, cy + 6, GUILD[3])                  # and their shadow
    for i in range(9):                                        # THE SHAFT, laid
        sp.set(10 + i, cy + 3 - i, PAINT[0])                  # over the pages
        sp.set(10 + i, cy + 4 - i, PAINT[1])
    for i in range(5):                                        # the barbs, one
        sp.set(15 + i, cy - 2 - i, PAINT[0])                  # side only — a
        sp.set(16 + i, cy - 2 - i, PAINT[1])                  # symmetric feather
        sp.set(14 + i, cy - 2 - i, PAINT[1])                  # reads as an arrow
    sp.set(10, cy + 4, IRON[3])                               # the cut nib


_DEVICES = {"fang": _dev_fang, "flask": _dev_flask,
            "kettle": _dev_kettle, "quill": _dev_quill}


def trade_sign(kind, iron, wood, salt=505, frames=4, face=1):
    """A HANGING TRADE SIGN, 32x32 over a 2x2 footprint — the single strongest
    culture cue this family has, and the one everything else is dressing for.

    A crooked hand-painted board on a wrought-iron bracket announces four things
    at once, which is why it earns the most work: that the building behind it is
    a SHOP, that the shop has a TRADE, that the trade is old enough to have a
    sign, and that the town is old enough to have a sign-painter. `kind` selects
    the painted device — `"fang"` (the weaponsmith, THE BRASS FANG), `"flask"`
    (the apothecary, THE CRACKED FLASK), `"kettle"` (the inn, THE COPPER KETTLE)
    or `"quill"` (the scribe and the library) — and every one of them is an
    OBJECT rather than a word, because there is no font in this game and painted
    lettering at 16px is mud. See the module docstring on why that constraint
    turned out to be a gift.

    IT SWINGS, and the swing is the difference between a sign and a plaque.
    `SIGN_SWAY` grades a +-1px offset down the board — zero at the ring, one
    pixel at the tongue — while the two hanger shanks tilt the same way, so the
    whole assembly leans about the ring it hangs from. A pure translation was the
    first pass and it read as the sign SLIDING along the wall; the graded offset
    reads as rotation because at this scale one pixel of jog IS a rotation. The
    cycle is `(0, 1, 0, -1)`: mean zero, period 4, and frame 0 is the art as
    drawn, so a still bake is byte-identical to the un-animated build.

    WALL-MOUNTED, WITH NOTHING BEHIND IT. The bracket's fixing plate is drawn at
    the canvas's west edge and the board hangs clear in the air east of it, so
    the art never leans on the facade it is bolted to and the same sheet works on
    a plaster wall, a withy hut and a plank fascia. `face=-1` mirrors the whole
    piece for a building's other flank.

    RETURNS a horizontal frame-sheet `Img` of `32*frames` x 32, ready for
    `emit_prop(name, chars, sheet, hframes=frames)`.

    FOOTPRINT: 2x2 cells. Type the WEST column (the wall the bracket is bolted
    to) SOLID and the EAST column — the lane you walk under the board in —
    WALKABLE.
    ANCHOR: Tier-3, bottom-anchored at the footprint's south edge. No `top=`,
    no `base_inset=`.

    AUTHORING CONSTRAINTS a generator must assert:
      * `hframes` in the manifest MUST equal `frames`, or the sign renders as
        four vertical ribbons of itself.
      * The WEST column must be the building's own solid cells. Standing free
        the bracket reads as a gibbet — the plate needs a wall to be bolted to
        and the eye supplies it from the neighbouring facade.
      * A body in the lane's SOUTH cell sorts in FRONT of the board's lower
        half. That is the `_rail_h` / `town_trestle` read and it is correct
        rather than a compromise: a body walking past a shop sign passes in
        front of it. A body in the lane's NORTH cell is behind it and shows
        through — the board is 21px of a 48px figure's width, nowhere near the
        walk-behind visibility ceiling.
      * `face` must point the bracket INTO the building, never out over open
        air.
    COVERAGE: measured floor 38.3% per cell (the board's own two cells run
    41-54%), so every footprint cell clears `T3_COVER_MIN` = 0.20 and the west
    column is safe typed solid."""
    assert kind in _DEVICES, f"no such trade device {kind!r}"
    assert frames < 2 or frames % len(SIGN_SWAY) == 0, \
        "a swinging sign's sheet must hold whole sway cycles"
    by0, bh = 10, len(_BOARD)

    def draw(sp, fi):
        sw = SIGN_SWAY[fi % len(SIGN_SWAY)]
        _iron_bracket(sp, iron, 1, 4, 21, drop=8)
        ys, halves = [], []
        for r, half in enumerate(_BOARD):
            # THE GRADED OFFSET. round(sw * r / (bh - 1)) is 0 over the top half
            # of the board and sw over the bottom half, i.e. one hard 1px jog at
            # the waist. That jog is what a 1px rotation looks like at 16px
            # tiles; anything smoother needs sub-pixel art this game does not
            # have.
            off = int(round(sw * r / float(bh - 1)))
            _board_paint(sp, wood, r, by0 + r, half)
            if off:                                  # slide the row we just drew
                row = sp.px[by0 + r]
                src = list(row)
                for x in range(15 - half - 1, 15 + half + 2):
                    row[x] = None
                for x in range(15 - half, 15 + half + 1):
                    row[x + off] = src[x]
            ys.append(by0 + r)
            halves.append(half)
        _fillet(sp, ys, halves)
        _DEVICES[kind](sp, by0 + 8)
        if sw:                                       # the device and fillet ride
            for r in range(bh):                      # the same graded offset, so
                off = int(round(sw * r / float(bh - 1)))
                if not off:
                    continue                         # the paint never shears off
                row = sp.px[by0 + r]                 # the plank it is on
                half = _BOARD[r]
                src = list(row)
                for x in range(15 - half - 1, 15 + half + 2):
                    row[x] = None
                for x in range(15 - half, 15 + half + 1):
                    row[x + off] = src[x]
        for hx in (9, 21):
            base = _eye_and_ring(sp, iron, hx, 5)
            # the hanger shank: pinned in the ring at the top, following the
            # board at the foot. One pixel of tilt, which is all a 4px shank has,
            # and it is what puts the pivot visibly AT the ring.
            sp.set(hx, base, iron[2])
            sp.set(hx + (0 if sw == 0 else sw), base + 1, iron[1])
            sp.set(hx + (0 if sw == 0 else sw), base + 2, iron[3])

    return _sheet(32, 32, salt, frames, draw, face=face)


# ---- 2. THE APOTHECARY'S WINDOW ------------------------------------------------------

def _bottle(sp, kind, x, base, tint):
    """One bottle standing on the window's shelf, its FEET at row `base`.

    Three silhouettes and no shared geometry between them, which is the point:
    four copies of one bottle in four colours is a swatch card, and a shelf has
    to look like stock that arrived at different times from different places. The
    liquid level differs per bottle for the same reason.

    Every bottle is three hard bands — pale empty glass above the meniscus, the
    saturated contents below it, a darker foot — plus a 1px lit column on the
    west. No dither: at 16px tiles a dithered bottle is a smudge, and glass is
    exactly the material where a smudge reads as dirt."""
    lit, liq = tint
    if kind == "round":                                    # a round-bottom matras
        sp.rect(x - 2, base - 12, x + 2, base - 11, GLASS)         # flared lip
        sp.rect(x - 1, base - 10, x + 1, base - 6, lit)            # neck
        sp.blob(x, base - 3, 3.4, 3.0, lit)                        # bulb
        sp.blob(x, base - 2, 2.8, 2.0, liq)                        # contents
        sp.rect(x - 2, base, x + 2, base, liq)
        sp.set(x - 2, base - 4, GLASS)
    elif kind == "tall":                                   # a stoppered spirit
        sp.rect(x - 2, base - 14, x + 2, base - 13, lit)           # the stopper
        sp.set(x - 2, base - 13, GLASS)
        sp.rect(x - 1, base - 12, x + 1, base - 10, lit)           # the neck
        sp.rect(x - 2, base - 9, x + 2, base, lit)                 # the body
        sp.rect(x - 2, base - 4, x + 2, base, liq)                 # a third full
        sp.rect(x - 2, base - 9, x - 2, base, GLASS)               # lit column
        sp.set(x + 2, base - 5, liq)
    else:                                                  # a squat covered jar
        sp.rect(x - 3, base - 7, x + 3, base - 7, PAPER_STOCK[1])  # cloth cover
        sp.rect(x - 3, base - 6, x + 3, base - 6, PAPER_STOCK[2])  # tied on
        sp.rect(x - 3, base - 5, x + 3, base, lit)                 # the body
        sp.rect(x - 3, base - 3, x + 3, base, liq)                 # nearly full
        sp.rect(x - 3, base - 5, x - 3, base, GLASS)
        sp.set(x + 3, base - 2, liq)


def bottle_window(glass, iron, f, salt=511, frames=2):
    """AN APOTHECARY'S WINDOW, 32x32 over a 2x2 footprint: a leaded grid of small
    panes with a shelf of coloured bottles racked behind it, an iron casement
    under a copper drip hood, and the shop's own lamplight coming out through the
    glass.

    THE BOTTLES ARE THE SUBJECT AND THE LEADING IS THE FRAME. The cames are
    drawn LAST, straight over the bottles, and that ordering is the whole trick:
    bottles drawn over the leading are bottles sitting in a window box, bottles
    drawn UNDER it are bottles inside a building. Four of them, four silhouettes,
    four tints, one empty (see TINTS), on one shelf with dark shop under it — so
    the window has real depth rather than being a coloured panel.

    Nothing here is a wizard's window. A leaded casement full of stock is what a
    licensed trade looks like from the street, in any century, and the reason it
    reads as an APOTHECARY rather than as a general store is that the stock is
    all glass and all liquid.

    THE LIGHT BREATHES. `_town_props._breathe` is handed the whole glazed rect,
    so the interior's WARM/WARMD climb their own warm ladders and bloom two rings
    onto the casement — the same hearth breath every lit pane in the game shares,
    which is what keeps a shop window in the same world as a cabin window.
    `BREATH2` is one step over two frames and its note explains why not three.
    Step 0 is the art as drawn, so a still bake is byte-identical.

    RETURNS a horizontal frame-sheet `Img` of `32*frames` x 32.

    FOOTPRINT: 2x2 cells, EVERY CELL SOLID — this is a hole in a wall, and the
    wall is solid.
    ANCHOR: either drawn straight onto a building's facade canvas at an offset
    (`Img.blit_cell` it, the `_hearth_window` role) or emitted as a Tier-3 sheet
    bottom-anchored over the facade's own solid cells. Both work because the
    piece carries its own casing and sill and is opaque edge to edge.

    AUTHORING CONSTRAINTS a generator must assert:
      * `hframes` in the manifest MUST equal `frames`.
      * If it is emitted as a prop rather than drawn into a facade, its cells
        must ALREADY be solid building. A window a body can walk through is a
        doorway.
      * One shop, one lit window. A facade where every pane burns has no focus
        for the breath to land on (the `tree_house` / `tree_hut` lesson, and it
        applies to shopfronts twice over).
    COVERAGE: 100% of every cell — opaque by construction — so all four cells
    are safe solid, and the invisible-wall lint has nothing to say about it."""
    assert frames in (1, 2, len(WIN_PULSE)), \
        "a breathing window's sheet is 1, 2 or a whole WIN_PULSE"
    lvls = BREATH2 if frames == 2 else \
        (WIN_PULSE if frames > 2 else (0,))

    def draw(sp, fi):
        sp.rect(0, 0, 31, 2, COPPER[2])                        # the drip hood,
        sp.rect(0, 0, 31, 0, COPPER[1])                        # which is what
        sp.rect(0, 2, 31, 2, COPPER[4])                        # keeps rain off
        sp.rect(1, 3, 30, 28, iron[2])                         # the casement
        sp.rect(1, 3, 1, 28, iron[1]); sp.rect(30, 3, 30, 28, iron[3])
        sp.rect(2, 4, 29, 4, iron[1])
        sp.rect(3, 5, 28, 26, WARMD)                           # the shop inside,
        sp.rect(3, 5, 28, 7, WARM)                             # lamp-lit high up
        sp.rect(3, 20, 28, 26, DOORDARK)                       # dark under-counter
        sp.rect(3, 17, 28, 17, iron[1])                        # THE SHELF
        sp.rect(3, 18, 28, 18, iron[2])
        sp.rect(3, 19, 28, 19, iron[3])
        for bx, kind, ti in ((8, "round", 0), (15, "tall", 1),
                             (22, "jar", 2), (27, "round", 3)):
            _bottle(sp, kind, bx, 16, TINTS[ti])
        # A SPRIG in the empty phial — the botanist half of an apothecary, and
        # the cheapest thing that says the stock is grown and not bought.
        for i, (lx, ly) in enumerate(((27, 9), (26, 8), (28, 7), (27, 6))):
            sp.set(lx, ly, f[1] if i % 2 else f[3])
        # THE LEADED CAMES, over everything. Small panes, because small panes are
        # what a town this old can actually make — one big sheet of glass would
        # date the building four hundred years forward.
        for cx in (10, 17, 24):
            sp.rect(cx, 5, cx, 26, iron[1])
        for cy in (10, 15, 22):
            sp.rect(3, cy, 28, cy, iron[1])
        # and the LIGHT CATCHING THE GLASS: a 1px lit L inside the top-left of
        # the two upper-west panes only. A full diagonal sheen band was the first
        # pass and it had to be broken at every came, which came out as litter;
        # two corner catches read as glazing instantly and cost eight pixels.
        for px0, py0, pw, ph in ((4, 6, 5, 3), (11, 6, 5, 3)):
            sp.rect(px0, py0, px0 + pw, py0, GLASS)
            sp.rect(px0, py0, px0, py0 + ph, GLASS)
        sp.rect(0, 27, 31, 28, iron[2])                        # the sill, proud
        sp.rect(0, 27, 31, 27, iron[1])
        sp.rect(0, 29, 31, 29, iron[3])
        for dx in (5, 24):                                     # leaves draping
            sp.set(dx, 0, f[2]); sp.set(dx, 1, f[4])           # over the hood
            sp.set(dx + 1, 1, f[3])
        lvl = lvls[fi % len(lvls)]
        if lvl:
            _breathe(sp, 3, 5, 26, 15, lvl)

    return _sheet(32, 32, salt, frames, draw)


# ---- 3. THE NOTICE BOARD -------------------------------------------------------------

def _paper_shadow(sp, x, y, paper, dark):
    """A pinned sheet's cast shadow — paper's own dark when it falls on another
    sheet, the board's dark when it falls on the board. One conditional instead
    of two passes, and without it the stack has no depth: a shadow painted flat
    in one colour disappears wherever it crosses a sheet."""
    sp.set(x, y, paper[3] if sp.get(x, y) in paper else dark)


def _pinned(sp, paper, iron, dark, x0, y0, pw, ph, lean, salt, k):
    """ONE NOTICE, pinned crooked, with ruled writing on it and a shadow under
    it.

    The LEAN is what makes a board look pinned rather than printed. It is applied
    as a per-row x offset of `lean * row`, so a 12-row sheet at lean 0.15 walks
    two pixels — enough to read as crooked at 16px tiles, not enough to read as
    falling off. Every sheet on a board leans a DIFFERENT amount and two of them
    lean the other way, because a board where everything tilts the same way reads
    as one warped decal.

    The writing is broken DASHES with gaps, never full-width rules. Full-width
    rules were the first pass and at this scale they read as a lined ledger page;
    two dashes with a gap read as words, which is as close to legible as a game
    with no font gets, and closer than it has any business being."""
    for r in range(ph):
        xo = x0 + int(round(lean * r))
        y = y0 + r
        for x in range(xo, xo + pw):
            _paper_shadow(sp, x + 1, y + 1, paper, dark)       # the cast shadow
        sp.rect(xo, y, xo + pw - 1, y, paper[1])
        sp.set(xo, y, paper[0])                                # the lit left edge
        sp.set(xo + pw - 1, y, paper[2])
    sp.rect(x0, y0, x0 + pw - 1, y0, paper[0])                 # the top, in light
    xb = x0 + int(round(lean * (ph - 1)))
    sp.rect(xb, y0 + ph - 1, xb + pw - 1, y0 + ph - 1, paper[2])
    for i, ly in enumerate(range(y0 + 2, y0 + ph - 1, 3)):     # the writing
        xo = x0 + int(round(lean * (ly - y0)))
        n = 2 + (h2(i, k, salt) % 3)
        sp.rect(xo + 1, ly, xo + n, ly, paper[2])
        if xo + n + 2 <= xo + pw - 2:
            sp.rect(xo + n + 2, ly, xo + pw - 2, ly, paper[2])
    px_ = x0 + pw // 2                                         # and the TACK
    sp.set(px_, y0, iron[3]); sp.set(px_, y0 - 1, iron[1])
    sp.set(px_ + 1, y0, iron[2])
    # THE CURLING CORNER, bottom-right: the sheet lifting off the board, its own
    # back showing, with the board's dark visible in the gap behind it. Three
    # tones in five pixels, and it is the detail that dates a notice.
    cx0 = xb + pw - 1
    cy0 = y0 + ph - 1
    sp.set(cx0, cy0, paper[2]); sp.set(cx0 - 1, cy0, paper[2])
    sp.set(cx0, cy0 - 1, paper[0]); sp.set(cx0 - 1, cy0 - 1, paper[1])
    sp.set(cx0 + 1, cy0, dark); sp.set(cx0 + 1, cy0 - 1, dark)


def notice_board(wood, paper, iron, salt=521):
    """THE VILLAGE NOTICE BOARD, 48x32 over a 3x2 footprint: a free-standing
    board on two posts under a weather ledge, its face LAYERED with pinned
    papers at four different angles, one sheet TORN AWAY with its pinned corner
    still hanging there, and a small chalked slate along the bottom.

    THIS IS THE PIECE THAT SAYS THE TOWN HAS BUREAUCRACY AND GOSSIP, which is
    also the difference between a village and a set of houses. A single notice is
    an event; FOUR overlapping notices plus a torn one plus a slate somebody
    keeps rubbing out is an institution, and an institution is a culture. It is
    the cheapest thing in this family and it argues the hardest.

    `_town_props._notice_board` is the Lanternwood moot hall's, and it is a
    different object on purpose: that one is bolted to a civic wall under a
    snow-loaded ledge and holds three tidy sheets, because it is the CLERK's
    board and the clerk is Mayor Hollis. This one stands in the open street and
    is a mess, because it belongs to everybody.

    NO LETTERING, here least of all. The writing is broken dashes (see `_pinned`)
    and the slate carries dashes and a WIPED SMUDGE — the smudge doing more work
    than the marks, since a rubbed-out line is proof somebody comes back and
    changes this.

    RETURNS an unsplit `Sprite`; the caller wraps it with
    `_tilekit.sprite_img(sp, 48, 32)`.

    FOOTPRINT: 3x2 cells, EVERY CELL SOLID — you bump into it. This is the
    textbook Tier-3 case (`town_well` / `town_stall`): a body stands both north
    and south of it, so it can never be baked into either static layer.
    ANCHOR: Tier-3, one unsplit sprite, bottom-anchored at the footprint's south
    edge. No `top=`, no `base_inset=`.

    AUTHORING CONSTRAINTS a generator must assert:
      * `bake_shadow(..., each=True)` for a SET of boards. The contact band is
        deliberately not drawn into the sprite (this builder takes no ground
        ramp), and a merged bbox smears one band across the gap between two
        boards — the hall-benches lesson.
      * A walkable cell on the SOUTH side. A notice board you cannot stand in
        front of is a wall with paper on it.
      * Never against a facade. Its whole read is free-standing, and the two
        posts' feet are drawn in the round; flush to a wall they read as
        panelling.
    COVERAGE: measured floor 58.6% per cell (the top row runs 75-78%), so all
    six cells clear `T3_COVER_MIN` = 0.20 with room."""
    w, h = 48, 32
    sp = S(w, h, salt)
    dark = wood[5]
    for px_ in (3, 41):                                        # THE TWO POSTS,
        sp.rect(px_, 2, px_ + 3, h - 1, wood[3])               # drawn first so
        sp.rect(px_, 2, px_, h - 1, wood[1])                   # the frame laps
        sp.rect(px_ + 3, 2, px_ + 3, h - 1, wood[5])           # over them
        sp.rect(px_, 2, px_ + 3, 2, wood[0])                   # a chamfered top
        sp.rect(px_ + 1, h - 2, px_ + 2, h - 1, wood[4])       # foot, in shade
    sp.rect(1, 4, 46, 4, wood[0])                              # THE WEATHER
    sp.rect(1, 5, 46, 5, wood[2])                              # LEDGE, proud of
    sp.rect(1, 6, 46, 6, wood[5])                              # the posts
    sp.rect(2, 7, 45, 25, wood[2])                             # the frame
    sp.rect(2, 7, 45, 7, wood[1]); sp.rect(2, 25, 45, 25, wood[5])
    sp.rect(2, 7, 2, 25, wood[1]); sp.rect(45, 7, 45, 25, wood[4])
    sp.rect(4, 8, 43, 24, wood[4])                             # THE BOARD FACE,
    sp.rect(4, 8, 43, 8, wood[5])                              # with the ledge's
    # THE STACK. Four sheets, four leans, two of them the other way, and drawn in
    # the order they went up so the later ones lap the earlier ones. Sizes vary
    # by more than they need to: a board of same-sized sheets is a calendar.
    for x0, y0, pw, ph, lean, k in ((5, 10, 11, 13, -0.10, 1),
                                    (14, 11, 10, 11, 0.16, 2),
                                    (20, 9, 8, 6, -0.16, 3),
                                    (29, 9, 13, 7, 0.08, 4)):
        _pinned(sp, paper, iron, dark, x0, y0, pw, ph, lean, salt, k)
    # THE TORN SHEET: gone, and the pin still in it with a ragged corner hanging
    # off. A board where every notice is intact has no time in it; a pin holding
    # a scrap is the single clearest statement that things happen here and then
    # stop mattering.
    tx, ty = 18, 20
    sp.set(tx, ty - 1, iron[1]); sp.set(tx, ty, iron[3])
    for i, wdt in enumerate((7, 6, 4, 2)):
        y = ty + i
        jag = wdt - (h2(i, 5, salt) % 2)                       # a ragged edge —
        sp.rect(tx - 1, y, tx - 1 + jag, y, paper[1])          # a straight tear
        sp.set(tx - 1, y, paper[0])                            # reads as a CUT
        sp.set(tx - 1 + jag, y, paper[2])
        _paper_shadow(sp, tx + jag, y + 1, paper, dark)
    # THE SLATE, along the bottom right in its own little frame: the part of the
    # board that changes daily. Slate is `iron`'s dark rather than a fifth pinned
    # material — a violet-charcoal is exactly what a wet slate is, and one fewer
    # colour in a prop this busy is worth more than the accuracy would be.
    sp.rect(28, 15, 44, 25, wood[3])
    sp.rect(28, 15, 44, 15, wood[1]); sp.rect(28, 25, 44, 25, wood[5])
    sp.rect(29, 16, 43, 24, iron[3])
    sp.rect(29, 16, 43, 16, iron[2])                           # its lit top edge
    sp.rect(29, 24, 43, 24, iron[2])                           # and chalk dust
    for i, cy in enumerate((18, 20, 22)):                      # the chalked lines
        n = 4 + (h2(i, 7, salt) % 3)
        sp.rect(30, cy, 30 + n, cy, paper[0])
        sp.rect(33 + n, cy, 41 - (i % 2), cy, paper[0])
    sp.rect(35, 20, 39, 21, iron[2])                           # A WIPED SMUDGE —
    sp.set(36, 20, iron[1])                                    # somebody changed
    sp.rect(44, 16, 44, 20, paper[2])                          # their mind. And
    sp.rect(43, 21, 44, 22, paper[0])                          # the chalk, on its
    sp.set(43, 22, paper[2])                                   # string
    edge(sp, h)
    clipw(sp, w)
    return sp


# ---- 4. THE MESSENGER ROOST ----------------------------------------------------------

# THE OCCUPANT, as one (x0, x1) span per row from the crown down. Authored rather
# than built from ball()s for one reason: this must read as a SHAPE and not as a
# character, and the way a generated bird turns into a mascot is by being
# SYMMETRIC and ROUND. Every row here is off-centre, the shoulders step out in
# two hard bands, and the tail runs off east and down past the perch — so the
# silhouette is a hunched lump facing slightly away, which is what a bird waiting
# to be sent somewhere actually looks like. No ear tufts: two tufts over two eyes
# is the cartoon-owl configuration and it is the exact thing that would make this
# piece cute.
_BIRD = ((1, 3), (0, 4), (0, 4), (0, 5), (-1, 5), (-1, 6), (-1, 6), (-1, 6),
         (0, 6), (0, 5), (1, 7), (4, 8), (5, 8))


def owl_roost(wood, f, iron, salt=531, frames=4, face=1):
    """THE MESSENGER ROOST, 32x32 over a 2x2 footprint: a small shingled box on
    an iron bracket with a round entry hole, three perches, straw spilling out of
    the nest and one round-eyed occupant sitting on the lowest perch waiting to
    be sent somewhere.

    THE POST HERE IS A BIRD, and that one substitution does more for the culture
    than any amount of apparatus: a town with a messenger roost is a town that
    CORRESPONDS — with other towns, with a university, with people who write
    back. Coupled to the notice board and the scribe's sign it says the local
    industry is words, which is what this village's whole economy is.

    Restrained on purpose, and the restraint is the art direction rather than
    modesty. The occupant is a hard dark silhouette in `iron`'s two darks with a
    1px lit rim, TWO PIXELS of warm eye-shine, and nothing else — no beak, no
    face, no feather detail (see `_BIRD` for why not, and for why it has no ear
    tufts). Everything that would make it a character has been left out; what is
    left is a shape you recognise, which at 16px tiles is both more legible and
    the only version of this that is not cute.

    IT BLINKS, on the LAST frame of the cycle only. A blink is the one animation
    in this file that cannot be zero-mean — it is a gate that returns to rest,
    not an oscillation — and the invariant that survives is the one that matters:
    nothing MOVES, so no positional term exists to drift. Frame 0 is the art as
    drawn. At travel_scene's 0.18s ANIM_STEP `frames=4` blinks every 0.72s, which
    is a fast nervous blink; pass `frames=8` for 1.44s if the roost wants to read
    as settled rather than as waiting.

    RETURNS a horizontal frame-sheet `Img` of `32*frames` x 32.

    FOOTPRINT: 2x2 cells. Type the WEST column SOLID (the post or wall the
    bracket is bolted to) and the EAST column WALKABLE — you stand under a roost,
    which is also where the straw and the whitewash land.
    ANCHOR: Tier-3, bottom-anchored at the footprint's south edge.

    AUTHORING CONSTRAINTS a generator must assert:
      * `hframes` in the manifest MUST equal `frames`.
      * `frames % 4 == 0` (asserted below) — the blink is keyed to the cycle's
        last frame, so a partial cycle blinks at the wrong rate or not at all.
      * The bracket needs a wall or a post on its `face` side, the `trade_sign`
        constraint verbatim.
      * Never over a door. The whitewash under the perch is drawn, and the joke
        only lands if nobody has to walk through it — which is the register: it
        is funny because the town clearly thought about where to put this and
        got it slightly wrong anyway.
    COVERAGE: measured floor 42.6% per cell, so the west column is safe solid;
    the walkable east column's worst case hides 47.8% of a body, well inside the
    walk-behind visibility ceiling `T3_HIDE_MAX` = 0.90."""
    assert frames < 2 or frames % 4 == 0, \
        "a blinking roost's sheet must hold whole blink cycles"

    def draw(sp, fi):
        # THE BRACKET: a plate, a diagonal strut and the box's own floor as the
        # shelf. Deliberately lighter hardware than `trade_sign`'s scrolled one —
        # a sign is a statement and gets a smith's work, a bird box is a job and
        # gets an angle iron.
        sp.rect(1, 14, 3, 26, iron[2])
        sp.rect(1, 14, 1, 26, iron[1]); sp.rect(3, 14, 3, 26, iron[3])
        sp.set(2, 16, iron[0]); sp.set(2, 24, iron[0])              # its bolts
        ln(sp, 3, 26, 12, 22, iron[3])
        ln(sp, 3, 25, 12, 21, iron[2])
        sp.rect(3, 20, 29, 20, wood[1])                            # the shelf
        sp.rect(3, 21, 29, 21, wood[2])
        sp.rect(3, 22, 29, 22, wood[4])
        # THE BOX. Boarded, not planked-and-battened: three horizontal boards
        # with the seam's lit underside showing, which is the cheapest carpentry
        # read there is and the right one for something nailed up in an afternoon.
        sp.rect(6, 12, 27, 19, wood[3])
        sp.rect(6, 12, 6, 19, wood[1]); sp.rect(27, 12, 27, 19, wood[5])
        for sy in (15, 18):
            sp.rect(6, sy, 27, sy, wood[5])
            sp.rect(6, sy + 1, 27, sy + 1, wood[2])
        # THE ROUND ENTRY HOLE — the single strongest cue in the piece, and the
        # reason the box does not read as a cupboard. Round, dark, and with a
        # WORN lit lip along the bottom where four hundred landings have polished
        # the wood.
        sp.blob(16, 15, 4.2, 3.8, DOORDARK)
        sp.blob(16, 14, 3.4, 2.6, iron[3])
        for lx in range(13, 20):
            sp.set(lx, 18, wood[0])                                # the worn lip
        sp.set(12, 15, wood[5]); sp.set(20, 15, wood[5])
        # THE SHINGLED ROOF: three courses, joints staggered per course. Shingles
        # rather than thatch, because thatch is what the HOUSES wear here and a
        # thing that matches the houses reads as part of the building instead of
        # as something hung on it.
        for c, ry in enumerate((6, 8, 10)):
            sp.rect(4, ry, 29, ry, wood[2])
            sp.rect(4, ry + 1, 29, ry + 1, wood[4])
            for jx in range(4 + c * 2, 30, 5):
                sp.rect(jx, ry, jx, ry + 1, wood[5])
        sp.rect(5, 5, 28, 5, wood[0])                              # the ridge cap
        sp.rect(4, 12, 29, 12, wood[5])                            # the eave line
        # THE PERCHES: three, at three heights, one of them a stick lashed on at
        # an angle. Three because two read as a ladder and a single one reads as
        # a shelf edge; the angled one because everything up a tree in this town
        # is lashed rather than joined.
        for py_, x0, x1 in ((24, 2, 30), (28, 16, 30)):
            sp.rect(x0, py_, x1, py_, wood[1])
            sp.rect(x0, py_ + 1, x1, py_ + 1, wood[4])
        ln(sp, 7, 25, 12, 30, wood[3])
        ln(sp, 8, 25, 13, 30, wood[5])
        # THE STRAW, spilling out of the hole and off the shelf. THATCH is
        # imported from _tree_props rather than re-pinned: the huts' roofs and a
        # roost's bedding are the same dry reed and a town gets ONE straw.
        for i, (sx, sy) in enumerate(((14, 19), (16, 19), (18, 19), (5, 19),
                                      (6, 19), (25, 19), (26, 19), (9, 26),
                                      (21, 26), (13, 30), (24, 31))):
            sp.set(sx, sy, THATCH[1] if i % 2 else THATCH[3])
            if i % 3 == 0:
                sp.set(sx + 1, sy, THATCH[2])
        # THE WHITEWASH under the perch. Three pixels, and they are the piece's
        # whole claim to being a working object rather than an ornament — nobody
        # decorates with this.
        sp.set(7, 26, PAPER_STOCK[0]); sp.set(7, 27, PAPER_STOCK[2])
        sp.set(23, 26, PAPER_STOCK[0])
        # THE OCCUPANT, on the low perch, drawn last so it sits in front of the
        # box it lives in.
        for r, (a, b) in enumerate(_BIRD):
            y = 12 + r
            sp.rect(10 + a, y, 10 + b, y, iron[3])
            sp.set(10 + a, y, iron[2])                             # a 1px lit rim,
        for hx in range(10, 15):                                   # so it is dark
            sp.set(hx, 12, iron[2])                                # and not a hole
        sp.set(11, 13, iron[1]); sp.set(12, 12, iron[1])
        sp.set(10, 24, iron[3]); sp.set(13, 24, iron[3])           # two talons
        # THE EYES: two pixels of WARMD, never SPEC and never white. A white
        # highlight in a dark head is a googly eye and it is the whole distance
        # between this and a mascot. On the blink they close into a 4px lid line
        # one step off the body — a blink at this scale is not the eye shutting,
        # it is the SHINE going out.
        blink = frames > 1 and (fi % frames) == frames - 1
        if blink:
            sp.rect(11, 15, 14, 15, iron[2])
        else:
            sp.set(11, 15, WARMD); sp.set(14, 15, WARMD)
            sp.set(11, 16, iron[3]); sp.set(14, 16, iron[3])
        for i, (lx, ly) in enumerate(((28, 6), (29, 7), (27, 4), (4, 5),
                                      (3, 6))):
            sp.set(lx, ly, f[1] if i % 2 else f[3])                # a bough's
            sp.set(lx, ly + 1, f[4])                               # leaves, over

    return _sheet(32, 32, salt, frames, draw, face=face)


# ---- 5. THE HOOK LANTERN -------------------------------------------------------------

def hook_lantern(iron, salt=541, frames=4):
    """A CANDLE LANTERN on a wrought-iron hook, 16x32 over a 1x2 footprint —
    the smallest piece in this family and the one you place the most of.

    Every lantern in this town is lit by hand, every evening, by somebody whose
    job that is. That is the whole cultural claim and it is worth making
    repeatedly: a street lit by candles under glass is a street with a
    lamplighter in it, which is a trade, which is the argument this module
    exists to make. It is also the piece that makes a canopy village navigable
    after dark without a single spell — the `_bracket_lamp` point, restated for
    somewhere with no walls to bolt anything to.

    Brass cap, iron cage, glass, a wax stub and a flame. Nothing electric,
    nothing crystal, nothing that glows on its own — candle-and-gear over
    circuitry, to the letter.

    THE FLAME IS MIX-BLENDED, ALWAYS. Its core is WGLINT (255,236,170), the top
    of the game's own warm ladder, and never SPEC: cream at ~250 ADDED onto a
    saturated field saturates every channel and arrives white, and a white flame
    is a welding arc. The light it throws onto the brass cap and the pan goes
    through `_town_props._wash`, the same lerp-toward-WARM every lit window in
    the game uses, so a lantern's spill and a hearth's spill are the same
    material.

    IT FLICKERS, and `CANDLE_FLICK` drives all three of the flicker's terms off
    one number — the flame's height, the lean of its tip, and how far its light
    reaches into the lantern. All three are affine in a mean-zero cycle, so all
    three are mean-zero: the flame cannot climb, drift west or brighten over the
    loop, which are the three ways a generated flame turns into a rocket. Frame 0
    is the art as drawn.

    RETURNS a horizontal frame-sheet `Img` of `16*frames` x 32.

    FOOTPRINT: 1x2 cells. The TOP cell is the fascia, bough or post it hangs off
    — type it SOLID. The BOTTOM cell is the air under it: WALKABLE, and you walk
    through it.
    ANCHOR: Tier-3, bottom-anchored at the footprint's south edge, so the
    lantern's pan sits ~10px into the lower cell and hangs at head height. Use
    `each=True` for a run of them off one char — `place`-style whole-map bbox
    behaviour would blit one lantern across the entire street.

    AUTHORING CONSTRAINTS a generator must assert:
      * `hframes` in the manifest MUST equal `frames`, and
        `frames % len(CANDLE_FLICK) == 0` (asserted below).
      * `each=True` for more than one. Two lanterns sharing a char without it is
        the `place()` bbox trap.
      * Something SOLID directly north. A lantern hanging from nothing reads as
        floating, and this is the one piece small enough that the eye has no
        other cue to go on.
      * It belongs on the glow overlay too. The halo is not drawn here — the
        overlay renders UNDER the y-sorted World, so a lantern's light has to
        land on the ground at its feet as ONE continuous wash, and per-lantern
        dabs scallop a boardwalk into circles.
    COVERAGE: measured floor 42.2% per cell, so the top cell is safe solid; a
    body standing on the walkable bottom cell sorts in FRONT of the lantern
    (its feet line is south of the prop's base line), so the walk-behind
    visibility lint never fires on it at all."""
    assert frames < 2 or frames % len(CANDLE_FLICK) == 0, \
        "a flickering lantern's sheet must hold whole flicker cycles"

    def draw(sp, fi):
        k = CANDLE_FLICK[fi % len(CANDLE_FLICK)]
        sp.rect(6, 0, 8, 0, iron[2])                           # the ceiling flange
        sp.rect(7, 1, 7, 2, iron[1])                           # THE HOOK: a J,
        sp.set(8, 3, iron[1]); sp.set(9, 3, iron[2])           # authored pixel by
        sp.set(9, 4, iron[2]); sp.set(8, 5, iron[3])           # pixel — a drawn
        ln(sp, 8, 4, 3, 8, iron[2])                            # arc this short is
        ln(sp, 8, 4, 12, 8, iron[2])                           # a staircase
        sp.set(8, 4, iron[0])                                  # the bail's apex
        sp.rect(7, 6, 8, 6, BRASS[0])                          # THE CAP: a finial,
        sp.rect(5, 7, 10, 7, BRASS[1])                         # a pyramid, and a
        sp.rect(3, 8, 12, 8, BRASS[1])                         # drip edge
        sp.set(3, 8, BRASS[0]); sp.set(12, 8, IRON[3])
        sp.rect(2, 9, 13, 9, iron[2])
        sp.rect(2, 9, 2, 9, iron[1]); sp.rect(13, 9, 13, 9, iron[3])
        sp.set(7, 6, iron[3])                                  # the smoke vent
        sp.rect(3, 10, 3, 21, iron[1])                         # the cage's two
        sp.rect(12, 10, 12, 21, iron[3])                       # corner posts
        # THE INTERIOR, in TWO HARD BANDS: WARM where the flame reaches, WARMD
        # beyond it. A radial falloff here would be a dither at 8px across, and a
        # dithered lantern reads as a dirty one.
        reach = 4 + k
        for y in range(10, 22):
            for x in range(4, 12):
                d = abs(x - 7) + abs(y - 15)
                sp.set(x, y, WARM if d <= reach else WARMD)
        sp.rect(7, 10, 7, 21, iron[2])                         # the glazing bars,
        sp.rect(4, 15, 11, 15, iron[2])                        # a 2x2 pane grid
        sp.rect(6, 17, 8, 20, PAPER)                           # THE WAX STUB
        sp.rect(8, 17, 8, 20, PAPER_STOCK[2])
        sp.set(5, 19, PAPER_STOCK[1])                          # a drip down it
        sp.rect(6, 21, 9, 21, BRASS[1])                        # its pricket
        # THE FLAME. Two pixels wide at the shoulders, one at the tip, and the
        # tip both rises and LEANS on the same mean-zero number — a flame that
        # only changes height pumps, and a flame that only leans wags.
        tipy, tipx = 13 - k, 7 + k
        sp.rect(7, 15, 8, 16, WGLINT)
        sp.rect(7, 16, 8, 16, WARM)
        sp.set(7, 14, WGLINT); sp.set(8, 14, WARM)
        sp.set(tipx, tipy, WARM)
        sp.set(tipx, tipy - 1, WARMD)
        # and its throw onto the metal: MIX, via the same lerp every lit pane in
        # the game uses.
        t = 0.24 + 0.08 * k
        for wx, wy in ((5, 9), (6, 9), (7, 9), (8, 9), (9, 9), (10, 9),
                       (6, 22), (7, 22), (8, 22), (9, 22), (3, 14), (12, 14)):
            sp.set(wx, wy, _wash(sp.get(wx, wy), t))
        sp.rect(2, 22, 13, 22, iron[2])                        # the pan under it
        sp.rect(2, 22, 2, 22, iron[1]); sp.rect(13, 22, 13, 22, iron[3])
        sp.rect(3, 23, 12, 23, iron[3])
        sp.set(7, 24, iron[2]); sp.set(8, 24, iron[3])         # and its drop ring

    return _sheet(16, 32, salt, frames, draw)


__all__ = ["PAPER_STOCK", "GUILD", "PAINT", "TINTS",
           "SIGN_SWAY", "CANDLE_FLICK", "BREATH2",
           "trade_sign", "bottle_window", "notice_board", "owl_roost",
           "hook_lantern"]
