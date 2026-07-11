#!/usr/bin/env python3
"""Fuji, the librarian cat — sprite sheet on the _sprites.py kit, at TRUE SNES
density (the CT-chunk restart): 48x48 cells, ~33px figure, flat 4-tone shading
with hard band edges (Sprite jitter=0), every pixel deliberate.

Writes assets/fuji_gen.png (288x480, 48x48 cells, 6x10) matching
entities/fuji/fuji_frames.tres (region contract):

  row0 walk_down(6)   row1 walk_up(6)   row2 walk_side(6, faces RIGHT — fuji.gd
                                              sets flip_h only when facing LEFT)
  row3 book_down(6)   row4 book_up(6)   row5 book_side(6)
      the tome swing: windup, peak, strike, IMPACT (held), follow, recover —
      recover redraws walk f0 exactly so the swing closes into idle
  row6 dart_down(4)   row7 dart_up(4)   row8 dart_side(4)   (cols 4-5 empty)
      the blow-pipe: raise, aim, PUFF (dart leaves here), settle
  row9 hurt(2) + idle_down blink + idle_side tail-flick + happy + sad

Art contracts consumed by code: feet baseline y=44 (_core.ZONE_FEET); origin
(24,24); in the leveled dart frames the pipe TIP sits exactly 19px from the
cell center along the facing (fuji.gd muzzle_offset spawns the dart there —
LONGER than Basil's 16px gun contract, the reed pipe reads as a full staff);
the book impact frame plants the tome over the 12px BookHitbox reach (fuji.gd
book_reach); idle_down/idle_side alternate walk f0 with the
blink/tail-flick cells, so walk f0 is a planted neutral pose the extras
redraw exactly.

Character (docs/DESIGN.md): tortoiseshell librarian cat — warm-black fur with
DELIBERATE rust patches (split ears: left black / right ginger, a rust brow
patch, cheek flecks — placed, never dithered), cream muzzle/chest/paws,
green-gold eyes behind round brass reading glasses, a deep plum scholar's
robe worn LONG (hem y=40) with a mustard trim placket + hem stripe and a
draped hood on the back, a clasped leather tome hugged to her chest while
she walks, a reed blow-pipe. CT field-sprite proportions, flat fields, ONE
hard shade band, never gradient mush.

Re-run: python3 assets/_gen_fuji_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import write_cells, ZONE_CELL, ZONE_FEET
from _sprites import Sprite, Rig
from _palette import FUJI

CELL, COLS, ROWS = ZONE_CELL, 6, 10
FEET = ZONE_FEET          # 44 — bottom row of the paw FILL (outline sits at 45)
CX = 24
HEM = 40                  # near-floor robe hem — only paw TIPS peek below it

FUR    = FUJI["FUR"]
GING   = FUJI["GINGER"]
CREAM  = FUJI["CREAM"]
ROBE   = FUJI["ROBE"]
TRIM   = FUJI["TRIM"]
RIM    = FUJI["RIM"]
LENS   = FUJI["LENS"]
BOOK   = FUJI["BOOK"]
PIPE   = FUJI["PIPE"]
EYE_G, EYE_GL = FUJI["EYE_G"], FUJI["EYE_GL"]
PUPIL, GLINT  = FUJI["PUPIL"], FUJI["GLINT"]
NOSE, MOUTH   = FUJI["NOSE"], FUJI["MOUTH"]
EARIN, EARIN_D = FUJI["EARIN"], FUJI["EARIN_D"]
WHISK  = FUJI["WHISK"]
DARTF  = FUJI["DARTF"]

# local expression accents (single-use, kept out of the shared palette)
LID    = (150, 128, 62, 255)      # closed-eye stroke (warm, reads against cream)
BLUSH  = (238, 160, 158, 255)
TEAR   = (170, 214, 250, 255)
MAW    = (96, 54, 60, 255)
TONGUE = (226, 120, 128, 255)
PUFFC  = (250, 250, 244, 220)     # blown-air wisp

OUTS = dict(FUJI["OUTS"])
OUT_FB = FUJI["OUT_FALLBACK"]


def new():
    return Sprite(CELL, grain=1, salt=5, jitter=0.0)   # flat CT bands


def finish(s):
    s.despeckle(passes=1)
    s.outline(OUTS, OUT_FB)


# ---- the body rig (down/up views share it; side view has its own) -----------------
RIG = Rig(
    head=(24, 18),
    robe=(24, 22),
    hipL=(21, 33), hipR=(27, 33),
    footL=(21, 42), footR=(27, 42),
    shL=(18, 23), shR=(30, 23),
    handL=(16, 29), handR=(32, 29),
    tail=(30, 33),
)

RIG_S = Rig(               # side view, facing RIGHT
    skull=(23, 18),
    robe=(23, 22),
    hipF=(25, 33), hipB=(20, 33),
    footF=(25, 42), footB=(20, 42),
    sh=(23, 23), hand=(22, 29),
    tail=(16, 30),
)


# ---- down-view parts ----------------------------------------------------------------

def head_down(s, dx=0, dy=0, eyes="open", ears="up", puff=False):
    hx, hy = CX + dx, 18 + dy
    # ears first (skull overlaps their base): SPLIT tortie ears — left black,
    # right ginger — the instant tortoiseshell read.
    if ears == "up":
        s.tri((hx - 4, hy - 10), hy - 4, hx - 7, hx - 1, FUR)
        s.tri((hx + 4, hy - 10), hy - 4, hx + 1, hx + 7, GING, sh=0.15)
        s.tri((hx - 4, hy - 8), hy - 5, hx - 5, hx - 3, EARIN)
        s.tri((hx + 4, hy - 8), hy - 5, hx + 3, hx + 5, EARIN_D)
    elif ears == "droop":                          # slouched out + down (sad)
        s.tri((hx - 6, hy - 4), hy, hx - 8, hx - 1, FUR)
        s.tri((hx + 6, hy - 4), hy, hx + 1, hx + 8, GING, sh=0.15)
    else:                                          # pinned flat (hurt / effort)
        s.tri((hx - 8, hy - 3), hy, hx - 6, hx - 1, FUR)
        s.tri((hx + 8, hy - 3), hy, hx + 1, hx + 6, GING, sh=0.15)
    # skull dome + tortie patches (fixed, deliberate — never dithered)
    s.ball(hx, hy, 7.2, 6.0, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(hx + 2, hy - 4, hx + 5, hy - 3, GING[1])       # right brow patch
    s.set(hx + 6, hy - 2, GING[2])
    s.rect(hx - 6, hy + 1, hx - 5, hy + 2, GING[2])       # left cheek fleck
    # plump cream muzzle + chin (no tuxedo blaze — the cream stays low)
    s.ball(hx, hy + 4, 4.6, 2.9, CREAM, power=2.2, wrap=0.10, curve=0.10)
    # nose
    s.rect(hx - 1, hy + 2, hx, hy + 2, NOSE)
    # mouths
    if puff:                                               # cheeks full of air
        s.rect(hx - 1, hy + 4, hx, hy + 5, MOUTH)          # pursed o
        s.set(hx, hy + 4, MAW)
        s.set(hx - 5, hy + 3, CREAM[1])                    # bulged cheeks
        s.set(hx + 4, hy + 3, CREAM[1])
        s.set(hx - 5, hy + 2, BLUSH)
        s.set(hx + 4, hy + 2, BLUSH)
    elif eyes == "hurt":
        s.rect(hx - 1, hy + 4, hx, hy + 6, MOUTH)          # open wail
        s.set(hx, hy + 5, MAW)
    elif eyes == "wince":
        s.rect(hx - 2, hy + 4, hx + 1, hy + 5, MOUTH)      # gritted teeth
        s.set(hx, hy + 4, CREAM[0])
    elif eyes == "happy":
        s.rect(hx - 2, hy + 4, hx + 1, hy + 6, MAW)        # open grin
        s.rect(hx - 1, hy + 6, hx, hy + 6, TONGUE)
        s.set(hx - 6, hy + 3, BLUSH)
        s.set(hx + 5, hy + 3, BLUSH)
    elif eyes == "sad":
        s.line([(hx - 2, hy + 5), (hx - 1, hy + 4), (hx, hy + 4),
                (hx + 1, hy + 5)], MOUTH)                  # wobble frown
    else:
        s.line([(hx - 1, hy + 4), (hx, hy + 4)], MOUTH)
    # eyes — green-gold, soft default (she peers OVER a book, not down a scope)
    if eyes == "open":
        _eye(s, hx - 5, hy - 2)
        _eye(s, hx + 3, hy - 2)
    elif eyes in ("closed", "happy"):                      # sweet ^ ^
        for ex in (hx - 5, hx + 3):
            s.line([(ex, hy - 1), (ex + 1, hy - 2), (ex + 2, hy - 1)], LID)
    elif eyes == "sad":                                    # teary, downcast
        for ex in (hx - 5, hx + 3):
            s.rect(ex, hy - 2, ex + 2, hy, EYE_G)
            s.rect(ex, hy - 2, ex + 2, hy - 2, FUR[2])     # heavy upper lid
            s.set(ex + 1, hy, PUPIL)
            s.set(ex + 2, hy - 1, GLINT)                   # shine = teary
        s.set(hx - 5, hy + 2, TEAR)                        # a welling tear
    else:                                                  # hurt / wince >_<
        for ex in (hx - 5, hx + 3):
            s.set(ex, hy - 2, LID)
            s.set(ex + 1, hy - 1, LID)
            s.set(ex, hy, LID)
    specs_down(s, hx, hy)


def specs_down(s, hx, hy):
    """Round brass reading glasses ON the face (her answer to Basil's goggles):
    a rim ring around each eye, a bridge across the nose, a pale glass shine
    cutting each lens' top corner. The eyes ARE the lenses."""
    for ex, sh in ((hx - 5, 0), (hx + 3, 1)):
        s.rect(ex, hy - 3, ex + 2, hy - 3, RIM[sh])        # top rim
        s.rect(ex, hy + 1, ex + 2, hy + 1, RIM[sh + 1])    # bottom rim
        for ry, rc in ((hy - 2, RIM[sh]), (hy - 1, RIM[sh + 1]), (hy, RIM[sh + 1])):
            s.set(ex - 1, ry, rc)                          # outer side
            s.set(ex + 3, ry, rc)                          # inner side
        s.set(ex + 2, hy - 2, LENS[0])                     # glass shine
    s.rect(hx - 1, hy - 2, hx + 1, hy - 2, RIM[2])         # bridge


def _eye(s, ex, ey):
    """3x3 green-gold eye behind the lens: light top row, 1x2 pupil."""
    s.rect(ex, ey, ex + 2, ey + 2, EYE_G)
    s.rect(ex, ey, ex + 2, ey, EYE_GL)
    s.rect(ex + 1, ey + 1, ex + 1, ey + 2, PUPIL)


def whiskers_down(s, dx=0, dy=0):
    """Short strokes off the cheeks at muzzle height, past the outline."""
    for pts in (((15, 21), (14, 21)),
                ((15, 23), (14, 24)),
                ((33, 21), (34, 21)),
                ((33, 23), (34, 24))):
        for (x, y) in pts:
            s.set(x + dx, y + dy, WHISK)


def legs_down(s, p, liftL=0, liftR=0, spread=0):
    """Short dark-fur stubs + chunky cream paws — the long robe hides the leg
    tops, so a step reads as a paw peeking under the hem."""
    for (hip, foot, lift, sp, sh) in (("hipL", "footL", liftL, -spread, 0.0),
                                      ("hipR", "footR", liftR, spread, 0.10)):
        hx, hy = p[hip]
        fx, fy = p[foot]
        hx += sp
        fx += sp
        fy -= lift
        s.capsule(hx, hy, fx, fy - 2, 2.2, 1.7, FUR, sh=sh)
        s.ball(fx, fy + 0.6, 2.2, 1.7, CREAM, power=2.2, sh=sh * 0.5,
               wrap=0.10, curve=0.10)


def robe_down(s, dy=0, back=False, sway=0):
    """Scholar's robe worn near-FLOOR (hem y=HEM). Flat CT bands, hand-set:
    a lit field left of center, mid field right, a hard 1px shade band at
    screen-right, a mustard TRIM stripe above the hem band, hem + turn-under
    dark. `sway` drags just the bottom QUARTER of the skirt sideways 1px.
    Front adds the trim placket, throat clasp and cream chest; back adds the
    draped HOOD and a vent seam."""
    top, hem = 22 + dy, HEM + dy
    h = hem - top

    def off(y):
        return sway if (y - top) / h >= 0.75 else 0

    for y in range(top, hem + 1):
        vy = (y - top) / h
        half = 5.6 + 2.0 * vy
        x0 = int(round(CX - half)) + off(y)
        x1 = int(round(CX + half)) + off(y)
        if y == top:
            x0 += 2
            x1 -= 2
        elif y == top + 1:
            x0 += 1
            x1 -= 1
        for x in range(x0, x1 + 1):
            if y >= hem - 1:                       # hem band
                c = ROBE[3] if x >= x1 - 1 else ROBE[2]
            elif x >= x1 - 1:                      # shade band, screen-right
                c = ROBE[2]
            elif y == hem - 2:                     # mustard trim stripe
                c = TRIM[2]
            elif x < CX + off(y):                  # lit field
                c = ROBE[0]
            else:                                  # mid field
                c = ROBE[1]
            s.set(x, y, c)
    s.rect(CX - 5 + sway, hem + 1, CX + 5 + sway, hem + 1, ROBE[3])  # turn-under
    if back:
        # draped hood between the shoulders — the scholar read from behind
        s.tri((CX, top + 7), top, CX - 5, CX + 5, ROBE, sh=0.42)
        s.set(CX, top + 7, ROBE[3])                               # hood point
        s.rect(CX - 5, top, CX + 5, top, ROBE[3])                 # hood roll
        for y in range(top + 9, hem - 2):                         # vent seam
            s.set(CX + off(y), y, ROBE[2])
        return
    for y in range(top + 4, hem - 2):                             # trim placket
        s.set(CX + off(y), y, TRIM[1])                            # (bends w/ sway)
    s.tri((CX, top), top + 3, CX - 2, CX + 2, CREAM)              # cream chest
    s.rect(CX - 1, top + 2, CX, top + 2, TRIM[0])                 # throat clasp


def book_carry_down(s, dy=0):
    """The tome hugged to her chest, cover out: flat leather fields with one
    hard shade band, spine left, brass clasp right, page block peeking below.
    Sleeves wrap in from the shoulders; cream paws grip the board edges."""
    y0, y1 = 24 + dy, 30 + dy
    for y in range(y0, y1 + 1):
        for x in range(21, 28):
            if y == y1:
                c = CREAM[2]                       # page block
            elif x >= 26:
                c = BOOK[2]                        # shade band
            elif x <= 22:
                c = BOOK[0]                        # lit field
            else:
                c = BOOK[1]
            s.set(x, y, c)
    s.rect(21, y0, 21, y1 - 1, BOOK[3])            # spine
    s.set(27, y0 + 3, TRIM[1])                     # brass clasp
    # sleeves in from the shoulders, paws on the board edges
    s.capsule(18, 23 + dy, 19.5, 26 + dy, 1.8, 1.5, ROBE, sh=0.18)
    s.capsule(30, 23 + dy, 28.5, 26 + dy, 1.8, 1.5, ROBE, sh=0.30)
    s.ball(19.5, 28 + dy, 1.6, 1.4, CREAM, power=2.2, wrap=0.10, curve=0.10)
    s.ball(28.5, 28 + dy, 1.6, 1.4, CREAM, power=2.2, sh=0.12, wrap=0.10, curve=0.10)


def arms_up_walk(s, p):
    """From behind, the hug reads as elbows poking out past the robe."""
    for (sh_a, dxx, sh) in (("shL", -1.5, 0.20), ("shR", 1.5, 0.34)):
        sx, sy = p[sh_a]
        s.capsule(sx, sy, sx + dxx, sy + 3.5, 1.8, 1.5, ROBE, sh=sh)


def tail_down(s, p, sway=0, droop=0):
    """Tail curling out right of the hem; black with the RUST TIP — the tortie
    signature. sway shifts the tip, droop sinks it."""
    tx, ty = p["tail"]
    if droop:
        s.capsule(tx, ty + 1, tx + 3, ty + 3, 1.7, 1.4, FUR, sh=0.08)
        s.capsule(tx + 3, ty + 3, tx + 5, ty + 2, 1.4, 1.1, FUR, sh=0.12)
        s.set(tx + 6, ty + 2, GING[1])
        return
    s.capsule(tx, ty + 1, tx + 3, ty - 3, 1.7, 1.4, FUR, sh=0.08)
    s.capsule(tx + 3, ty - 3, tx + 4 + sway, ty - 7, 1.4, 1.1, FUR, sh=0.12)
    s.set(tx + 2, ty - 1, GING[2])                                # mid patch
    s.set(tx + 3 + sway, ty - 8, GING[1])                         # rust tip
    s.set(tx + 4 + sway, ty - 8, GING[1])


# ---- full down/up poses ---------------------------------------------------------------

def cat_down(s, bobY=0, liftL=0, liftR=0, tail_sway=0, tail_droop=0,
             eyes="open", ears="up", head_dx=0, spread=0, robe_sway=0,
             carry=True):
    p = RIG.pose(head=(head_dx, bobY), tail=(tail_sway // 2, bobY),
                 shL=(0, bobY), shR=(0, bobY))
    tail_down(s, p, tail_sway, tail_droop)
    legs_down(s, p, liftL, liftR, spread)
    robe_down(s, bobY, sway=robe_sway)
    if carry:
        book_carry_down(s, bobY)
    head_down(s, head_dx, bobY, eyes, ears)
    finish(s)
    whiskers_down(s, head_dx, bobY)


def head_up(s, dy=0):
    """Back of the head: dome, split tortie ear backs, a rust patch on the
    crown, the spectacle temples hooking behind the ears, neck part."""
    hy = 18 + dy
    s.tri((CX - 4, hy - 10), hy - 4, CX - 7, CX - 1, FUR)
    s.tri((CX + 4, hy - 10), hy - 4, CX + 1, CX + 7, GING, sh=0.15)
    s.tri((CX - 4, hy - 8), hy - 5, CX - 6, CX - 2, FUR, sh=0.38)
    s.tri((CX + 4, hy - 8), hy - 5, CX + 2, CX + 6, GING, sh=0.46)
    s.ball(CX, hy, 7.2, 6.0, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(CX - 5, hy - 3, CX - 2, hy - 1, GING[1])               # crown patch
    s.set(CX + 3, hy + 2, GING[2])
    s.set(CX - 6, hy - 1, RIM[2])                                 # temple hooks
    s.set(CX + 6, hy - 1, RIM[2])
    s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
            (CX + 1, hy + 6), (CX + 2, hy + 5)], FUR[3])


def tail_up(s, sway=0):
    """Raised swish, seen from behind on her right — rust tip up top."""
    s.capsule(29, 31, 32, 27, 1.7, 1.4, FUR, sh=0.10)
    s.capsule(32, 27, 32 + sway, 22, 1.4, 1.1, FUR, sh=0.14)
    s.set(32 + sway, 21, GING[1])


def cat_up(s, bobY=0, liftL=0, liftR=0, tail_sway=0, robe_sway=0):
    p = RIG.pose(shL=(0, bobY), shR=(0, bobY))
    legs_down(s, p, liftL, liftR)
    robe_down(s, bobY, back=True, sway=robe_sway)
    arms_up_walk(s, p)
    tail_up(s, tail_sway)
    head_up(s, bobY)
    finish(s)


# ---- side view (faces RIGHT) ----------------------------------------------------------

def head_side(s, dx=0, dy=0, eyes="open", ears="up", puff=False):
    hx, hy = 23 + dx, 18 + dy
    if ears == "up":
        s.tri((hx + 3, hy - 10), hy - 5, hx + 1, hx + 5, GING, sh=0.30)  # far ear
        s.tri((hx - 1, hy - 11), hy - 5, hx - 3, hx + 1, FUR)     # near ear, tall
        s.tri((hx - 1, hy - 9), hy - 6, hx - 2, hx, EARIN)
    else:                                                          # swept back
        s.tri((hx - 8, hy - 5), hy - 1, hx - 6, hx - 1, FUR)
    # SHORT-nosed cat with big cheeks: plump cream cheek mass flush against
    # the skull front, nose riding high, jowl rounding the jaw.
    s.ball(hx, hy, 6.8, 5.6, FUR, power=2.4, wrap=0.34, curve=0.30)      # skull
    s.rect(hx - 4, hy - 3, hx - 2, hy - 1, GING[1])                      # nape patch
    s.set(hx - 1, hy + 2, GING[2])                                       # cheek fleck
    cheek_r = 4.0 if puff else 3.2
    s.ball(hx + 4, hy + 2.5, 3.2, 2.7, FUR, power=2.0, wrap=0.30)        # cheek mass
    s.ball(hx + 4.5, hy + 3.2, cheek_r, 2.5, CREAM, power=2.0, wrap=0.10,
           curve=0.10)
    s.rect(hx + 6, hy + 2, hx + 7, hy + 2, NOSE)                         # stub nose
    if puff:
        s.set(hx + 5, hy + 4, MOUTH)                                     # pursed lip
        s.set(hx + 3, hy + 4, BLUSH)
    else:
        s.line([(hx + 5, hy + 4), (hx + 6, hy + 4)], MOUTH)
    if eyes == "open":
        _eye(s, hx + 2, hy - 3)
    elif eyes == "closed":
        s.line([(hx + 2, hy - 2), (hx + 3, hy - 3), (hx + 4, hy - 2)], LID)
    elif eyes == "wince":                                          # squeezed shut >
        s.line([(hx + 2, hy - 3), (hx + 3, hy - 2)], LID)
        s.line([(hx + 2, hy - 1), (hx + 3, hy - 2)], LID)
        s.set(hx + 5, hy - 4, FUR[3])                              # knit brow
    # spectacles in profile: one round rim over the eye, temple arm running back
    s.rect(hx + 2, hy - 4, hx + 4, hy - 4, RIM[0])                 # top rim
    s.rect(hx + 2, hy, hx + 4, hy, RIM[1])                         # bottom rim
    for ry, rc in ((hy - 3, RIM[0]), (hy - 2, RIM[1]), (hy - 1, RIM[1])):
        s.set(hx + 1, ry, rc)
        s.set(hx + 5, ry, rc)
    s.set(hx + 4, hy - 3, LENS[0])                                 # glass shine
    s.rect(hx - 4, hy - 4, hx + 1, hy - 4, RIM[2])                 # temple arm


def whiskers_side(s, dx=0, dy=0):
    """Short strokes off the big cheek, past the outline."""
    for pts in (((32, 19), (33, 19), (34, 20)),
                ((32, 22), (33, 23))):
        for (x, y) in pts:
            s.set(x + dx, y + dy, WHISK)


def robe_side(s, dy=0, lean=0, sway=0):
    """Robe in profile, worn near-FLOOR: straight front edge, back hem
    trailing. Flat CT bands — lit band along the back, mid field, one crisp
    trailing-fold line, a mustard TRIM column inside the dark front edge (the
    closure running down her front) meeting the trim stripe above the hem."""
    top, hem = 22 + dy, HEM + dy
    h = hem - top
    for y in range(top, hem + 1):
        vy = (y - top) / h
        x_off = -lean + int(round(vy * lean * 0.5))
        if vy >= 0.75:
            x_off += sway
        x0 = int(round(17 - vy * 3.0)) + x_off
        x1 = 29 + x_off
        if y == top:
            x0 += 2
            x1 -= 1
        elif y == top + 1:
            x0 += 1
        fold = x0 + 3
        for x in range(x0, x1 + 1):
            if y >= hem - 1:                       # hem band
                c = ROBE[3] if x >= x1 - 1 else ROBE[2]
            elif x == x1:                          # dark front edge
                c = ROBE[3] if y >= top + 2 else ROBE[2]
            elif x == x1 - 1:                      # trim closure column
                c = TRIM[2] if y >= top + 3 else ROBE[2]
            elif y == hem - 2:                     # trim stripe
                c = TRIM[2]
            elif x == fold and y >= top + 4:       # trailing fold crease
                c = ROBE[2]
            elif x <= x0 + 2:                      # lit back
                c = ROBE[0]
            else:                                  # mid field
                c = ROBE[1]
            s.set(x, y, c)
    x_off = -lean + int(round(lean * 0.5)) + sway
    s.rect(16 + x_off, hem + 1, 27 + x_off, hem + 1, ROBE[3])     # turn-under


def book_carry_side(s, dy=0):
    """The tome tucked under her near arm: an edge-on slab with the cream page
    stripe, the sleeve draped over its middle, a paw cupping the fore-edge."""
    y = 28 + dy
    for x in range(20, 30):
        s.set(x, y - 1, BOOK[1])
        s.set(x, y, CREAM[1])                      # pages, edge-on
        s.set(x, y + 1, BOOK[2])
    s.rect(20, y - 1, 20, y + 1, BOOK[3])          # spine cap
    s.rect(29, y - 1, 29, y + 1, BOOK[3])          # fore-edge cap
    s.capsule(23, 23 + dy, 24.5, 27 + dy, 1.8, 1.5, ROBE, sh=0.24)  # sleeve over
    s.ball(28, 30.5 + dy, 1.4, 1.2, CREAM, power=2.2, wrap=0.10, curve=0.10)


def tail_side(s, p, dy=0, raised=False):
    tx, ty = p["tail"]
    if raised:
        s.capsule(tx, ty, tx - 2, ty - 5, 1.7, 1.4, FUR, sh=0.10)
        s.capsule(tx - 2, ty - 5, tx - 1, ty - 9 + dy, 1.4, 1.1, FUR, sh=0.13)
        s.set(tx - 2, ty - 10 + dy, GING[1])
    else:
        s.capsule(tx, ty, tx - 3, ty - 2, 1.7, 1.4, FUR, sh=0.10)
        s.capsule(tx - 3, ty - 2, tx - 6, ty - 4 + dy, 1.4, 1.1, FUR, sh=0.13)
        s.set(tx - 4, ty - 3, GING[2])                            # mid patch
        s.set(tx - 7, ty - 5 + dy, GING[1])


def cat_side(s, bobY=0, fA=(0, 0), fB=(0, 0), tail_dy=0, tail_raised=False,
             eyes="open", ears="up", robe_sway=0, carry=True):
    p = RIG_S.pose(skull=(0, bobY), tail=(0, bobY),
                   footF=(fA[0], -fA[1]), footB=(fB[0], -fB[1]))
    tail_side(s, p, tail_dy, tail_raised)
    for (hip, foot, sh) in (("hipB", "footB", 0.16), ("hipF", "footF", 0.0)):
        hx, hy = p[hip]
        fx, fy = p[foot]
        s.capsule(hx, hy + bobY, fx, fy - 2, 2.1, 1.7, FUR, sh=sh)
        s.ball(fx + 0.5, fy + 0.6, 2.2, 1.7, CREAM, power=2.2, sh=sh * 0.4,
               wrap=0.10, curve=0.10)
    robe_side(s, bobY, 0, robe_sway)
    if carry:
        book_carry_side(s, bobY)
    else:
        sx, sy = p["sh"]
        hxx, hyy = p["hand"]
        s.capsule(sx, sy, hxx, hyy, 1.8, 1.6, ROBE, sh=0.28)
        s.ball(hxx, hyy + 1.6, 1.8, 1.5, CREAM, power=2.2, wrap=0.10, curve=0.10)
    head_side(s, 0, bobY, eyes, ears)
    finish(s)
    whiskers_side(s, 0, bobY)


# ---- the tome (attack rows 3-5) --------------------------------------------------------

def _book_edge(s, x0, y, x1):
    """Edge-on tome, horizontal: leather boards sandwiching the cream page
    stripe (2px boards each side — the BIG 2026-07 tome), dark underside,
    dark caps at both ends."""
    for x in range(x0, x1 + 1):
        s.set(x, y - 2, BOOK[0])
        s.set(x, y - 1, BOOK[1])
        s.set(x, y, CREAM[1])
        s.set(x, y + 1, BOOK[2])
        s.set(x, y + 2, BOOK[3])
    s.rect(x0, y - 2, x0, y + 2, BOOK[3])
    s.rect(x1, y - 2, x1, y + 2, BOOK[3])


def _book_vert(s, x, y0, y1):
    """Edge-on tome, vertical (side-view arc frames): lit board 2px on the
    screen-left, 2px shade board right."""
    for y in range(y0, y1 + 1):
        s.set(x - 2, y, BOOK[0])
        s.set(x - 1, y, BOOK[1])
        s.set(x, y, CREAM[1])
        s.set(x + 1, y, BOOK[2])
        s.set(x + 2, y, BOOK[2])
    s.rect(x - 2, y0, x + 2, y0, BOOK[3])
    s.rect(x - 2, y1, x + 2, y1, BOOK[3])


def _book_flat(s, cx, cy, w=6, h=3):
    """Cover-up tome (the slam): flat leather fields, one hard shade band,
    spine left, brass clasp, page block along the bottom."""
    x0, x1 = cx - w, cx + w
    y0, y1 = cy - h, cy + h
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if y == y1:
                c = CREAM[2]                       # page block
            elif x >= x1 - 1:
                c = BOOK[2]
            elif x <= x0 + 1:
                c = BOOK[0]
            else:
                c = BOOK[1]
            s.set(x, y, c)
    s.rect(x0, y0, x0, y1 - 1, BOOK[3])            # spine
    s.set(x1, cy, TRIM[1])                         # clasp


def _impact_fx(s, pts):
    """Impact stars, placed after the outline like whiskers."""
    for i, (x, y) in enumerate(pts):
        s.set(x, y, GLINT if i % 2 == 0 else TRIM[0])


def book_down(s, phase):
    """Row-3 tome swing, facing camera: a two-paw overhead slam. The impact
    frame plants the tome over the 12px BookHitbox reach in front of her."""
    p = RIG.pose()
    tail = (1, 2, 0, -1, 0, 0)[phase]
    spread = 1 if phase == 3 else 0
    tail_down(s, p, tail)
    legs_down(s, p, spread=spread)
    robe_down(s, 1 if phase == 3 else 0)
    if phase in (0, 1):                            # windup: tome overhead
        by = 6 - phase
        s.capsule(18, 23, 20, by + 4, 1.8, 1.5, ROBE, sh=0.18)
        s.capsule(30, 23, 28, by + 4, 1.8, 1.5, ROBE, sh=0.30)
        s.ball(20, by + 2.5, 1.5, 1.3, CREAM, wrap=0.10)
        s.ball(28, by + 2.5, 1.5, 1.3, CREAM, wrap=0.10)
        head_down(s, 0, -1 if phase == 1 else 0, "open", "up")
        _book_edge(s, 18, by, 30)
        finish(s)
        whiskers_down(s, 0, -1 if phase == 1 else 0)
    elif phase == 2:                               # strike: tome falls past her chest
        s.capsule(18, 23, 20, 25, 1.8, 1.5, ROBE, sh=0.18)
        s.capsule(30, 23, 28, 25, 1.8, 1.5, ROBE, sh=0.30)
        head_down(s, 0, 1, "open", "flat")
        s.ball(20, 27, 1.5, 1.3, CREAM, wrap=0.10)
        s.ball(28, 27, 1.5, 1.3, CREAM, wrap=0.10)
        _book_edge(s, 18, 29, 30)                  # in FRONT of the torso
        finish(s)
        whiskers_down(s, 0, 1)
        for (x, y) in ((23, 18), (25, 22), (24, 14)):   # arc smear
            s.set(x, y, BOOK[2])
    elif phase == 3:                               # IMPACT: tome planted low
        s.capsule(18, 24, 20, 31, 1.8, 1.5, ROBE, sh=0.18)
        s.capsule(30, 24, 28, 31, 1.8, 1.5, ROBE, sh=0.30)
        s.ball(20, 33, 1.5, 1.3, CREAM, wrap=0.10)
        s.ball(28, 33, 1.5, 1.3, CREAM, wrap=0.10)
        head_down(s, 0, 2, "wince", "flat")
        _book_flat(s, 24, 37)
        finish(s)
        whiskers_down(s, 0, 2)
        _impact_fx(s, ((17, 34), (31, 35), (24, 42), (19, 41), (31, 41)))
    elif phase == 4:                               # follow: tome easing up
        s.capsule(18, 23, 20, 29, 1.8, 1.5, ROBE, sh=0.18)
        s.capsule(30, 23, 28, 29, 1.8, 1.5, ROBE, sh=0.30)
        s.ball(20, 30, 1.5, 1.3, CREAM, wrap=0.10)
        s.ball(28, 30, 1.5, 1.3, CREAM, wrap=0.10)
        head_down(s, 0, 1, "open", "up")
        _book_flat(s, 24, 34)
        finish(s)
        whiskers_down(s, 0, 1)
    else:                                          # recover = the carry (walk f0)
        book_carry_down(s)
        head_down(s)
        finish(s)
        whiskers_down(s)


def book_up(s, phase):
    """Row-4 tome swing, facing away: the slam lands beyond her head (drawn
    FIRST so the body overlaps it — it's on the far side)."""
    p = RIG.pose()
    if phase == 3:
        _book_flat(s, 24, 9)                       # planted on the far ground
    elif phase == 4:
        _book_flat(s, 24, 12)
    legs_down(s, p, spread=1 if phase == 3 else 0)
    robe_down(s, 1 if phase == 3 else 0, back=True)
    if phase in (0, 1):                            # windup overhead (same slab)
        by = 6 - phase
        s.capsule(18, 23, 20, by + 4, 1.8, 1.5, ROBE, sh=0.18)
        s.capsule(30, 23, 28, by + 4, 1.8, 1.5, ROBE, sh=0.30)
        head_up(s)
        s.ball(20, by + 2.5, 1.5, 1.3, CREAM, wrap=0.10)
        s.ball(28, by + 2.5, 1.5, 1.3, CREAM, wrap=0.10)
        _book_edge(s, 18, by, 30)
        tail_up(s, 1)
    elif phase == 2:                               # strike: pitching forward/away
        _book_edge(s, 18, 10, 30)
        s.capsule(18, 23, 19, 14, 1.8, 1.5, ROBE, sh=0.18)
        s.capsule(30, 23, 29, 14, 1.8, 1.5, ROBE, sh=0.30)
        head_up(s, 1)
        s.ball(19, 13, 1.5, 1.3, CREAM, wrap=0.10)
        s.ball(29, 13, 1.5, 1.3, CREAM, wrap=0.10)
        tail_up(s, 0)
    elif phase in (3, 4):                          # arms reaching past the head
        s.capsule(18, 23, 19, 15, 1.8, 1.5, ROBE, sh=0.18)
        s.capsule(30, 23, 29, 15, 1.8, 1.5, ROBE, sh=0.30)
        head_up(s, 1 if phase == 3 else 0)
        s.ball(19, 13.5, 1.5, 1.3, CREAM, wrap=0.10)
        s.ball(29, 13.5, 1.5, 1.3, CREAM, wrap=0.10)
        tail_up(s, -1 if phase == 3 else 0)
    else:                                          # recover = walk_up f0
        arms_up_walk(s, p)
        tail_up(s, 0)
        head_up(s)
    finish(s)
    if phase == 3:
        _impact_fx(s, ((17, 6), (31, 7), (24, 4)))


def book_side(s, phase):
    """Row-5 tome swing, facing RIGHT: over-the-shoulder arc into a forward
    plant. The impact frame covers the 12px BookHitbox reach (tome at
    x36-40)."""
    p = RIG_S.pose()
    fA, fB = (0, 0), (0, 0)
    if phase == 3:
        fA = (4, 0)
        fB = (1, 0)
    elif phase == 5:                               # recover = walk_side f0 feet
        fA = (2, 0)
        fB = (-1, 0)
    tail_side(s, p, 0, raised=phase in (0, 1, 3))
    pp = dict(p)
    pp["footF"] = (p["footF"][0] + fA[0], p["footF"][1] - fA[1])
    pp["footB"] = (p["footB"][0] + fB[0], p["footB"][1] - fB[1])
    for (hip, foot, sh) in (("hipB", "footB", 0.16), ("hipF", "footF", 0.0)):
        hx, hy = pp[hip]
        fx, fy = pp[foot]
        s.capsule(hx, hy, fx, fy - 2, 2.1, 1.7, FUR, sh=sh)
        s.ball(fx + 0.5, fy + 0.6, 2.2, 1.7, CREAM, power=2.2, sh=sh * 0.4,
               wrap=0.10, curve=0.10)
    robe_side(s, 0, 2 if phase == 3 else 0)
    if phase == 0:                                 # windup: tome behind the shoulder
        s.capsule(23, 23, 17, 15, 1.7, 1.5, ROBE, sh=0.24)
        s.ball(16.5, 13.5, 1.5, 1.3, CREAM, wrap=0.10)
        head_side(s, 0, 0, "open", "up")
        _book_vert(s, 13, 7, 17)
    elif phase == 1:                               # peak: tome overhead
        s.capsule(23, 23, 23, 11, 1.7, 1.5, ROBE, sh=0.24)
        head_side(s, 0, 0, "open", "up")
        s.ball(23.5, 8.3, 1.5, 1.3, CREAM, wrap=0.10)   # grip between the ears
        _book_edge(s, 17, 5, 29)
    elif phase == 2:                               # strike: mid-arc in front
        s.capsule(23, 23, 29, 15, 1.7, 1.5, ROBE, sh=0.24)
        s.ball(30, 13.5, 1.5, 1.3, CREAM, wrap=0.10)
        head_side(s, 1, 0, "open", "back")
        _book_vert(s, 33, 8, 18)
    elif phase == 3:                               # IMPACT: planted forward
        s.capsule(23, 23, 33, 21, 1.7, 1.5, ROBE, sh=0.24)
        s.ball(34, 22, 1.5, 1.3, CREAM, wrap=0.10)
        head_side(s, 1, 0, "wince", "back")
        _book_vert(s, 38, 17, 29)
    elif phase == 4:                               # follow: easing back
        s.capsule(23, 23, 31, 24, 1.7, 1.5, ROBE, sh=0.24)
        s.ball(32, 25, 1.5, 1.3, CREAM, wrap=0.10)
        head_side(s, 0, 0, "open", "up")
        _book_vert(s, 35, 20, 30)
    else:                                          # recover = walk_side f0 carry
        book_carry_side(s)
        head_side(s)
    finish(s)
    whiskers_side(s, 1 if phase in (2, 3) else 0, 0)
    if phase == 2:
        for (x, y) in ((27, 4), (30, 6), (32, 8)):     # arc smear
            s.set(x, y, BOOK[2])
    elif phase == 3:
        _impact_fx(s, ((41, 17), (42, 25), (36, 16), (41, 29)))


# ---- the blow-pipe (dart rows 6-8) -----------------------------------------------------

def dart_down(s, mode):
    """Row-6 blow-pipe, facing camera: pipe to her lips pointing SOUTH. In the
    leveled frames the tip fills (24, 43) — cell center + muzzle_offset(19)."""
    p = RIG.pose()
    tail_down(s, p, 1 if mode == "puff" else 0)
    legs_down(s, p)
    robe_down(s)
    # off paw hangs
    s.capsule(18, 23, 16, 28, 1.8, 1.6, ROBE, sh=0.18)
    s.ball(16, 30, 1.7, 1.5, CREAM, power=2.2, wrap=0.10, curve=0.10)
    if mode in ("raise", "settle"):                # pipe diagonal at the chest
        head_down(s, 0, 0, "open", "up")
        s.capsule(30, 23, 27.5, 26.5, 1.8, 1.5, ROBE, sh=0.30)
        s.capsule(20, 32, 27, 25, 1.1, 1.0, PIPE, sh=0.08)
        s.set(22, 30, TRIM[1])                     # brass band
        s.ball(26.5, 27.5, 1.5, 1.3, CREAM, wrap=0.10)
    else:                                          # aim / puff: pipe level, south
        head_down(s, 0, 0, "open", "up", puff=(mode == "puff"))
        s.capsule(30, 23, 27.5, 28, 1.8, 1.5, ROBE, sh=0.30)
        # the blowgun reads as a TUBE, not a stick: flared mouthpiece cup at
        # her lips, a dead-straight 2px reed bore (lit left / shaded right,
        # covering the trim placket — it's in front), twin brass cane wraps
        s.rect(23, 24, 26, 24, PIPE[0])            # mouthpiece cup, flared
        s.rect(23, 25, 26, 25, PIPE[2])
        s.rect(24, 26, 24, 41, PIPE[0])            # bore, lit side
        s.rect(25, 26, 25, 41, PIPE[2])            # bore, shade side
        for by in (31, 36):                        # cane wraps
            s.set(24, by, TRIM[1])
            s.set(25, by, TRIM[2])
        s.ball(27, 29.5, 1.5, 1.3, CREAM, wrap=0.10)     # paw steadying the pipe
    finish(s)
    whiskers_down(s)
    if mode in ("aim", "puff"):
        s.set(24, 42, PIPE[3])                     # square-cut muzzle, open bore
        s.set(25, 42, PIPE[3])
        s.set(24, 43, DARTF)                       # dart in the bore — tip kisses
        s.set(25, 43, DARTF)                       # y=43 (contract)
    if mode == "puff":
        for (x, y) in ((18, 42), (30, 42), (24, 46)):
            s.set(x, y, PUFFC)                     # blown-air wisps skirt the paws


def dart_up(s, mode):
    """Row-7 blow-pipe, facing away: the pipe rises past her head on the far
    side (drawn first). Leveled tip fills (23..24, 5)."""
    p = RIG.pose()
    if mode in ("aim", "puff"):                    # pipe beyond the head
        s.rect(23, 7, 23, 19, PIPE[0])             # straight 2px reed bore
        s.rect(24, 7, 24, 19, PIPE[2])
        for by in (9, 12):                         # cane wraps (skull hides below)
            s.set(23, by, TRIM[1])
            s.set(24, by, TRIM[2])
    legs_down(s, p)
    robe_down(s, back=True)
    # off arm hangs; pipe arm reaches up beside the head
    s.capsule(18, 23, 16, 28, 1.8, 1.6, ROBE, sh=0.20)
    s.ball(16, 30, 1.7, 1.5, CREAM, power=2.2, wrap=0.10, curve=0.10)
    if mode in ("raise", "settle"):
        s.capsule(30, 23, 28, 18, 1.8, 1.5, ROBE, sh=0.30)
        tail_up(s, 1)
        head_up(s)
        s.ball(28, 16.5, 1.5, 1.3, CREAM, wrap=0.10)
    else:
        s.capsule(30, 23, 27.5, 16, 1.8, 1.5, ROBE, sh=0.30)
        tail_up(s, 0)
        head_up(s)
        s.ball(27, 14.5, 1.5, 1.3, CREAM, wrap=0.10)
    finish(s)
    if mode in ("aim", "puff"):
        s.set(23, 6, PIPE[3])                      # square-cut muzzle, open bore
        s.set(24, 6, PIPE[3])
        s.set(23, 5, DARTF)                        # dart in the bore — tip kisses
        s.set(24, 5, DARTF)                        # y=5 (contract)
    if mode == "puff":
        for (x, y) in ((21, 6), (27, 6), (24, 2)):
            s.set(x, y, PUFFC)


def dart_side(s, mode):
    """Row-8 blow-pipe, facing RIGHT: pipe level from her lips going EAST,
    cheeks puffed on the shot. Leveled tip fills (43, 23..24)."""
    p = RIG_S.pose()
    tail_side(s, p, 0, raised=(mode == "puff"))
    for (hip, foot, sh) in (("hipB", "footB", 0.16), ("hipF", "footF", 0.0)):
        hx, hy = p[hip]
        fx, fy = p[foot]
        s.capsule(hx, hy, fx, fy - 2, 2.1, 1.7, FUR, sh=sh)
        s.ball(fx + 0.5, fy + 0.6, 2.2, 1.7, CREAM, power=2.2, sh=sh * 0.4,
               wrap=0.10, curve=0.10)
    robe_side(s)
    if mode in ("raise", "settle"):                # pipe swinging up to the lips
        head_side(s, 0, 0, "open", "up")
        s.capsule(23, 23, 26, 26, 1.7, 1.5, ROBE, sh=0.24)
        dy = 2 if mode == "settle" else 0
        s.capsule(26, 27 + dy, 37, 21.5 + dy, 1.1, 1.0, PIPE, sh=0.08)
        s.set(31, 25 + dy, TRIM[1])
        s.ball(27.5, 26.5 + dy, 1.5, 1.3, CREAM, wrap=0.10)
    else:                                          # aim / puff: level at the lips
        head_side(s, 0, 0, "open", "up", puff=(mode == "puff"))
        s.capsule(23, 23, 28, 25.5, 1.7, 1.5, ROBE, sh=0.24)
        # the blowgun as a TUBE: flared mouthpiece cup against her lips, a
        # dead-straight 2px bore (lit top / shaded belly), twin brass wraps
        s.rect(29, 22, 30, 22, PIPE[0])            # mouthpiece cup, flared
        s.rect(29, 23, 30, 24, PIPE[1])
        s.rect(29, 25, 30, 25, PIPE[2])
        s.rect(31, 23, 41, 23, PIPE[0])            # bore, lit top
        s.rect(31, 24, 41, 24, PIPE[2])            # bore, shaded belly
        for bx in (34, 38):                        # cane wraps
            s.set(bx, 23, TRIM[1])
            s.set(bx, 24, TRIM[2])
        s.ball(31.5, 24.5, 1.5, 1.3, CREAM, wrap=0.10)   # paw cupping the bore
    finish(s)
    whiskers_side(s)
    if mode in ("aim", "puff"):
        s.set(42, 23, PIPE[3])                     # square-cut muzzle, open bore
        s.set(42, 24, PIPE[3])
        s.set(43, 23, DARTF)                       # dart in the bore — tip kisses
        s.set(43, 24, DARTF)                       # x=43 (contract)
    if mode == "puff":
        for (x, y) in ((45, 21), (46, 23), (45, 25)):
            s.set(x, y, PUFFC)


# ---- build the sheet -------------------------------------------------------------------
cells = [[new() for _ in range(COLS)] for _ in range(ROWS)]

# walk down/up: f0 planted neutral (idle_down/up reuse it). A SHUFFLE — both
# paw tips stay visible under the hem, the stepping paw lifts only 1px, and
# bob + tail carry the motion (her arms hug the tome, so no arm swing). NO hem
# sway in these views (it reads as a wag); the side view keeps its fore/aft
# sway, which lies along the motion.
walk_bob   = [0, -1, -1, 0, -1, -1]
walk_liftl = [0, 1, 1, 0, 0, 0]
walk_liftr = [0, 0, 0, 0, 1, 1]
walk_tail  = [0, 1, 1, 2, 1, 1]
for i in range(6):
    cat_down(cells[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
             walk_tail[i])
    cat_up(cells[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
           walk_tail[i])

# walk side: the flat SCISSOR shuffle under the near-floor hem (see Basil's
# generator for the full geometry notes) — foot tips slide between x=27 and
# x=19, a bare 1px toe-lift, f0 is the contact pose idle_side reuses.
side_fA   = [(2, 0), (0, 0), (-3, 0), (-6, 0), (-3, 1), (0, 1)]
side_fB   = [(-1, 0), (2, 1), (5, 1), (7, 0), (5, 0), (2, 0)]
side_bob  = [0, -1, -1, 0, -1, -1]
side_tail = [0, -1, -1, 0, 1, 1]
side_sway = [0, -1, -1, 0, 1, 1]       # skirt trails the stride fore/aft
for i in range(6):
    cat_side(cells[2][i], side_bob[i], side_fA[i], side_fB[i],
             side_tail[i], robe_sway=side_sway[i])

# book rows: windup, peak, strike, IMPACT (fuji.gd opens the hitbox around this
# frame), follow, recover (redraws walk f0 so the swing closes into idle)
for i in range(6):
    book_down(cells[3][i], i)
    book_up(cells[4][i], i)
    book_side(cells[5][i], i)

# dart rows: raise, aim, PUFF (the dart leaves here — fuji.gd spawns it at the
# pipe-tip contract), settle. Cols 4-5 stay empty.
for i, m in enumerate(("raise", "aim", "puff", "settle")):
    dart_down(cells[6][i], m)
    dart_up(cells[7][i], m)
    dart_side(cells[8][i], m)

# row 9: hurt x2 (she clutches the tome tighter), idle-down blink, idle-side
# tail-flick, happy, sad
cat_down(cells[9][0], eyes="hurt", ears="flat", head_dx=-1, tail_sway=2)
cat_down(cells[9][1], eyes="hurt", ears="flat", head_dx=1, tail_sway=-1)
cat_down(cells[9][2], eyes="closed")                    # matches walk_down f0
cat_side(cells[9][3], 0, side_fA[0], side_fB[0], side_tail[0],
         tail_raised=True)                              # matches walk_side f0
cat_down(cells[9][4], eyes="happy", tail_sway=2)        # her warm face
cat_down(cells[9][5], eyes="sad", ears="droop", tail_droop=1)

write_cells(os.path.join(HERE, "fuji_gen.png"), cells, CELL)
