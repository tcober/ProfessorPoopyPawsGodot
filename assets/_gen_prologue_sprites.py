#!/usr/bin/env python3
"""Prologue A cast — every sprite the childhood chapter needs, built fresh on
the _sprites.py kit (2026-07-12; nothing recovered from the deleted intro).
TRUE SNES density: 48x48 cells, flat 4-tone shading, hard band edges
(jitter=0), every pixel deliberate. Kid figures are ~29px with CT-kid
proportions — the head is nearly half the figure.

Sheets written (all 48px cells, feet baseline y=44 = _core.ZONE_FEET):

  kid_basil_gen.png (288x192, 6x4) — the PLAYABLE kid, matching
      entities/kid/kid_basil_frames.tres:
      row0 walk_down(6)  row1 walk_up(6)  row2 walk_side(6, faces RIGHT)
      row3 hurt(2) + idle-down blink + idle-side tail-flick + happy + sad
      (walk f0 per facing is the planted idle pose, same contract as the
      adults' sheets)

  ONE-ROW NPC sheets (entities/npcs/npc.gd builds SpriteFrames at runtime:
  [idle0, idle1, act0, act1, emote0, emote1] — villagers stop at 4 cols):
      npc_sage_gen.png        (288x48) — Basil's little sister: slate-lavender
          kitten, white socks, sage-green hair bow; act = ribbon-CAST (arms
          up), emote = smug giggle
      npc_schweinler_gen.png  (288x48) — the pig, kid-sized: stout pink,
          red neckerchief; act = POINT, emote = belly laugh
      npc_kitty_gen.png       (288x48) — Kitty Cool: ginger-cream maker girl,
          teal bandana, grease smudge; act = TINKER crouch, emote = beaming
      npc_sheep_gen.png       (192x48) — wool-cloud matron; act = talk nod
      npc_owl_gen.png         (192x48) — the know-it-all owl; act = lecturing
          wing
      npc_goose_gen.png       (192x48) — the chaos goose; act = honk
      npc_mouse_gen.png       (192x48) — the mouse kid; act = wave

  prologue_fx.png (160x16, 16px cells) — [ribbon_magenta, ribbon_gold,
      sparkle_small, sparkle_big, gear, spring, crank, whirligig_droop,
      whirligig_spin0, whirligig_spin1]

Palette: derived 4-tone ramps via _palette.ramp() (violet shadow law), with
Basil's own identity ramps reused for the kid so he IS visibly the same cat.
Re-run: python3 assets/_gen_prologue_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import write_cells, Img, ZONE_CELL
from _sprites import Sprite
from _palette import BASIL, ramp

CELL = ZONE_CELL
CX = 24

# ---- palettes ------------------------------------------------------------------------

FUR = BASIL["FUR"]                 # kid Basil IS Basil: same jet tuxedo ramps
WHITE = BASIL["WHITE"]
EYE_Y, EYE_YL = BASIL["EYE_Y"], BASIL["EYE_YL"]
PUPIL, GLINT = BASIL["PUPIL"], BASIL["GLINT"]
NOSE, MOUTH = BASIL["NOSE"], BASIL["MOUTH"]
EARIN, EARIN_D = BASIL["EARIN"], BASIL["EARIN_D"]
WHISK = BASIL["WHISK"]

SAGE_FUR = ramp((156, 152, 196), "violet", 4)      # slate-lavender kitten
SAGE_BOW = ramp((132, 188, 116), "violet", 4)      # sage-green ribbon
SAGE_EYE, SAGE_EYEL = (140, 186, 240, 255), (190, 218, 250, 255)

KIT_FUR = ramp((238, 172, 104), "violet", 4)       # ginger maker girl
KIT_BAND = ramp((64, 178, 178), "violet", 4)       # teal bandana
KIT_EYE, KIT_EYEL = (150, 208, 232, 255), (200, 234, 248, 255)
SMUDGE = (94, 78, 96, 255)                         # grease on her cheek

PIG = ramp((240, 158, 158), "violet", 4)           # Schweinler pink
KERCH = ramp((214, 66, 76), "violet", 4)           # the red neckerchief
PIG_EYE = (52, 30, 40, 255)
SNOUT = ramp((246, 178, 172), "violet", 4)

WOOL = ramp((240, 230, 214), "violet", 4)          # sheep matron
SHEEP_FACE = ramp((104, 92, 110), "violet", 4)
FEATH = ramp((176, 124, 82), "violet", 4)          # owl feathers
DISC = ramp((242, 226, 190, 255), "violet", 4)
BEAK = ramp((226, 170, 64), "violet", 4)
GOOSE = ramp((246, 242, 234), "violet", 4)         # goose white
BILL = ramp((238, 152, 58), "violet", 4)
MOUSE = ramp((176, 168, 190), "violet", 4)         # mouse gray
MPINK = ramp((234, 156, 168), "violet", 4)

BRASSF = ramp((240, 188, 98), "violet", 4)         # fx: gear brass
STEELF = ramp((176, 176, 212), "violet", 4)        # fx: spring steel
WOODF = ramp((150, 100, 66), "violet", 4)          # fx: crank / whirligig body
RIBBON_M = ramp((240, 96, 170), "violet", 4)       # festival magenta
RIBBON_G = ramp((244, 196, 88), "violet", 4)       # festival gold
SPARK = (255, 252, 220, 255)
SPARK_D = (238, 202, 120, 255)

OUT_DARK = (10, 7, 16, 255)
OUT_LIGHT = (66, 58, 78, 255)
LID = (150, 128, 62, 255)
BLUSH = (238, 160, 158, 255)
MAW = (96, 54, 60, 255)
TONGUE = (226, 120, 128, 255)


def outs_for(*pairs):
    """(ramp, outline) pairs -> the fill->outline dict outline() consumes."""
    o = {}
    for r, c in pairs:
        for tone in r:
            o[tone] = c
    return o


def new():
    return Sprite(CELL, grain=1, salt=9, jitter=0.0)


# ---- shared face bits ------------------------------------------------------------------

def _eye(s, ex, ey, iris, iris_l):
    """3x3 kid eye: big and round, light top row, 1x2 pupil, corner glint."""
    s.rect(ex, ey, ex + 2, ey + 2, iris)
    s.rect(ex, ey, ex + 2, ey, iris_l)
    s.rect(ex + 1, ey + 1, ex + 1, ey + 2, PUPIL)
    s.set(ex + 2, ey, GLINT)


def _closed(s, ex, ey, happy=True):
    """^ ^ (happy) or - - (plain shut)."""
    if happy:
        s.line([(ex, ey + 1), (ex + 1, ey), (ex + 2, ey + 1)], LID)
    else:
        s.line([(ex, ey + 1), (ex + 1, ey + 1), (ex + 2, ey + 1)], LID)


def _wince(s, ex, ey):
    s.line([(ex, ey), (ex + 1, ey + 1)], LID)
    s.line([(ex, ey + 2), (ex + 1, ey + 1)], LID)


# ---- the kid cat (shared by kid Basil / Sage / Kitty) ----------------------------------
# Down-view geometry: ears crest y=15, skull ball cy=25, muzzle 29, round
# tummy cy=36, leg stubs to paws ending on the feet line (fill y=44).

def kid_ears(s, fur, hy, style="up", inner=True):
    if style == "up":
        s.tri((CX - 5, hy - 10), hy - 4, CX - 8, CX - 2, fur)
        s.tri((CX + 5, hy - 10), hy - 4, CX + 2, CX + 8, fur, sh=0.12)
        if inner:
            s.tri((CX - 5, hy - 8), hy - 5, CX - 6, CX - 4, EARIN)
            s.tri((CX + 5, hy - 8), hy - 5, CX + 4, CX + 6, EARIN_D)
    else:                                           # drooped (sad)
        s.tri((CX - 7, hy - 4), hy - 1, CX - 9, CX - 2, fur)
        s.tri((CX + 7, hy - 4), hy - 1, CX + 2, CX + 9, fur, sh=0.12)


def kid_head_down(s, fur, iris, iris_l, dy=0, eyes="open", ears="up",
                  muzzle=WHITE, blaze=False):
    hy = 25 + dy
    kid_ears(s, fur, hy, ears)
    s.ball(CX, hy, 7.2, 6.4, fur, power=2.4, wrap=0.34, curve=0.30)
    if blaze:                                       # the tuxedo blaze up the brow
        s.tri((CX, hy - 5), hy + 1, CX - 1, CX + 1, muzzle, sh=0.05)
    s.ball(CX, hy + 4.4, 4.6, 2.8, muzzle, power=2.2, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    ey = hy - 3
    if eyes == "open":
        _eye(s, CX - 6, ey, iris, iris_l)
        _eye(s, CX + 4, ey, iris, iris_l)
        s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    elif eyes == "blink":
        _closed(s, CX - 6, ey, happy=False)
        _closed(s, CX + 4, ey, happy=False)
        s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    elif eyes == "happy":
        _closed(s, CX - 6, ey)
        _closed(s, CX + 4, ey)
        s.rect(CX - 2, hy + 4, CX + 1, hy + 5, MAW)     # open grin
        s.rect(CX - 1, hy + 5, CX, hy + 5, TONGUE)
        s.set(CX - 7, hy + 2, BLUSH)
        s.set(CX + 6, hy + 2, BLUSH)
    elif eyes == "sad":
        for ex in (CX - 6, CX + 4):
            s.rect(ex, ey, ex + 2, ey + 2, iris)
            s.rect(ex, ey, ex + 2, ey, fur[2])          # heavy lid
            s.set(ex + 1, ey + 1, PUPIL)
            s.set(ex + 2, ey + 2, GLINT)                # welling shine
        s.line([(CX - 2, hy + 5), (CX - 1, hy + 4), (CX, hy + 4),
                (CX + 1, hy + 5)], MOUTH)               # wobble frown
    else:                                               # hurt >_<
        _wince(s, CX - 6, ey)
        _wince(s, CX + 4, ey)
        s.rect(CX - 1, hy + 4, CX, hy + 5, MOUTH)


def kid_body_down(s, fur, belly, dy=0, arms="down", arm_lift=0):
    by = 36 + dy
    s.ball(CX, by, 5.8, 5.0, fur, power=2.2, wrap=0.30, curve=0.24)
    s.ball(CX, by + 1.2, 3.4, 3.0, belly, power=2.2, wrap=0.10, curve=0.10)
    if arms == "down":
        s.capsule(CX - 5.5, by - 3, CX - 6.5, by + 1 - arm_lift, 1.7, 1.5, fur, sh=0.06)
        s.capsule(CX + 5.5, by - 3, CX + 6.5, by + 1 - arm_lift, 1.7, 1.5, fur, sh=0.16)
        s.ball(CX - 6.5, by + 2 - arm_lift, 1.6, 1.4, belly, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 6.5, by + 2 - arm_lift, 1.6, 1.4, belly, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
    elif arms == "up":                              # both paws thrown skyward
        s.capsule(CX - 5.5, by - 3, CX - 8, by - 8, 1.7, 1.5, fur, sh=0.06)
        s.capsule(CX + 5.5, by - 3, CX + 8, by - 8, 1.7, 1.5, fur, sh=0.16)
        s.ball(CX - 8, by - 9, 1.6, 1.4, belly, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 8, by - 9, 1.6, 1.4, belly, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)


def kid_legs_down(s, fur, paw, liftL=0, liftR=0, dy=0):
    for (lx, lift, sh) in ((CX - 3, liftL, 0.0), (CX + 3, liftR, 0.10)):
        s.capsule(lx, 39 + dy, lx, 42 - lift + dy, 2.0, 1.7, fur, sh=sh)
        s.ball(lx, 42.8 - lift + dy, 2.1, 1.6, paw, power=2.2, sh=sh * 0.5,
               wrap=0.10, curve=0.10)


def kid_tail_down(s, fur, sway=0, droop=0, tip=None):
    tx, ty = CX + 6, 37
    if droop:
        s.capsule(tx, ty + 1, tx + 3, ty + 4, 1.5, 1.2, fur, sh=0.08)
        if tip:
            s.set(tx + 4, ty + 4, tip)
        return
    s.capsule(tx, ty, tx + 3, ty - 3, 1.5, 1.2, fur, sh=0.08)
    s.capsule(tx + 3, ty - 3, tx + 3 + sway, ty - 7, 1.2, 1.0, fur, sh=0.12)
    if tip:
        s.set(tx + 3 + sway, ty - 8, tip)


def whiskers_kid_down(s, dy=0):
    for (x, y) in ((15, 28), (14, 30), (33, 28), (34, 30)):
        s.set(x, y + dy, WHISK)


# ---- kid Basil: full playable sheet ----------------------------------------------------

BASIL_OUTS = outs_for((FUR, OUT_DARK), (WHITE, OUT_LIGHT))


def kb_finish(s):
    s.despeckle(passes=1)
    s.outline(BASIL_OUTS, OUT_DARK)


def kb_down(s, bob=0, liftL=0, liftR=0, tail_sway=0, tail_droop=0,
            eyes="open", ears="up", arms="down"):
    kid_tail_down(s, FUR, tail_sway, tail_droop)
    kid_legs_down(s, FUR, WHITE, liftL, liftR, bob)
    kid_body_down(s, FUR, WHITE, bob, arms)
    kid_head_down(s, FUR, EYE_Y, EYE_YL, bob, eyes, ears, WHITE, blaze=True)
    kb_finish(s)
    whiskers_kid_down(s, bob)


def kb_up(s, bob=0, liftL=0, liftR=0, tail_sway=0):
    kid_legs_down(s, FUR, WHITE, liftL, liftR, bob)
    by = 36 + bob
    s.ball(CX, by, 5.8, 5.0, FUR, power=2.2, wrap=0.30, curve=0.24)
    s.capsule(CX - 5.5, by - 3, CX - 6.5, by + 1, 1.7, 1.5, FUR, sh=0.06)
    s.capsule(CX + 5.5, by - 3, CX + 6.5, by + 1, 1.7, 1.5, FUR, sh=0.16)
    # tail swishes up past the tummy, seen from behind
    s.capsule(CX + 5, by + 1, CX + 8, by - 4, 1.5, 1.2, FUR, sh=0.10)
    s.set(CX + 8 + tail_sway, by - 5, FUR[0])
    hy = 25 + bob
    kid_ears(s, FUR, hy, inner=False)
    s.tri((CX - 5, hy - 8), hy - 5, CX - 6, CX - 4, FUR, sh=0.40)
    s.tri((CX + 5, hy - 8), hy - 5, CX + 4, CX + 6, FUR, sh=0.46)
    s.ball(CX, hy, 7.2, 6.4, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
            (CX + 1, hy + 6), (CX + 2, hy + 5)], FUR[3])       # neck part
    kb_finish(s)


def kb_side(s, bob=0, fF=(0, 0), fB=(0, 0), tail_dy=0, eyes="open",
            tail_raised=False):
    """Side view, faces RIGHT (flip_h in code for left)."""
    hx, hy = 23, 25 + bob
    # tail behind, off the rump
    if tail_raised:
        s.capsule(16, 36, 14, 30 + tail_dy, 1.5, 1.2, FUR, sh=0.10)
    else:
        s.capsule(16, 37, 13, 34 + tail_dy, 1.5, 1.2, FUR, sh=0.10)
    # legs: front/back scissor pair, paws on the feet line
    for (base_x, (dx, lift), sh) in (((20), fB, 0.14), ((26), fF, 0.0)):
        lx = base_x + dx
        s.capsule(lx, 38 + bob, lx, 42 - lift, 2.0, 1.7, FUR, sh=sh)
        s.ball(lx + 0.5, 42.8 - lift, 2.1, 1.6, WHITE, power=2.2, sh=sh * 0.4,
               wrap=0.10, curve=0.10)
    # round tummy + white bib toward the front
    s.ball(23, 36 + bob, 5.4, 4.8, FUR, power=2.2, wrap=0.30, curve=0.24)
    s.ball(25.5, 37 + bob, 2.8, 2.8, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.capsule(23, 33 + bob, 24, 37 + bob, 1.7, 1.5, FUR, sh=0.10)   # near arm
    # head: near ear tall, far ear peeking
    s.tri((hx + 4, hy - 9), hy - 4, hx + 2, hx + 6, FUR, sh=0.26)
    s.tri((hx - 1, hy - 10), hy - 4, hx - 3, hx + 1, FUR)
    s.tri((hx - 1, hy - 8), hy - 5, hx - 2, hx, EARIN)
    s.ball(hx, hy, 6.8, 6.0, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.ball(hx + 4.5, hy + 3.4, 4.0, 2.5, WHITE, power=2.0, wrap=0.10, curve=0.10)
    s.rect(hx + 7, hy + 2, hx + 8, hy + 2, NOSE)
    if eyes == "open":
        _eye(s, hx + 2, hy - 3, EYE_Y, EYE_YL)
        s.line([(hx + 6, hy + 4), (hx + 7, hy + 4)], MOUTH)
    elif eyes == "blink":
        _closed(s, hx + 2, hy - 3, happy=False)
        s.line([(hx + 6, hy + 4), (hx + 7, hy + 4)], MOUTH)
    else:
        _wince(s, hx + 2, hy - 3)
        s.rect(hx + 6, hy + 4, hx + 7, hy + 5, MOUTH)
    kb_finish(s)
    for (x, y) in ((31, 27), (32, 29)):
        s.set(x, y + bob, WHISK)


# ---- Sage --------------------------------------------------------------------------------

SAGE_OUTS = outs_for((SAGE_FUR, OUT_DARK), (WHITE, OUT_LIGHT), (SAGE_BOW, OUT_DARK))


def sage_bow(s, hy):
    """The sage-green bow between her ears."""
    s.rect(CX + 1, hy - 9, CX + 3, hy - 8, SAGE_BOW[1])
    s.rect(CX + 4, hy - 10, CX + 6, hy - 8, SAGE_BOW[0])
    s.rect(CX + 4, hy - 9, CX + 5, hy - 9, SAGE_BOW[2])


def sage(s, eyes="open", ears="up", arms="down", bob=0, sway=0, sparkle=False):
    kid_tail_down(s, SAGE_FUR, sway)
    kid_legs_down(s, SAGE_FUR, WHITE, 0, 0, bob)
    kid_body_down(s, SAGE_FUR, WHITE, bob, arms)
    kid_head_down(s, SAGE_FUR, SAGE_EYE, SAGE_EYEL, bob, eyes, ears, WHITE)
    sage_bow(s, 25 + bob)
    s.despeckle(passes=1)
    s.outline(SAGE_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob)
    if sparkle:                                     # her ribbons answer her paws
        for (x, y) in ((13, 24), (35, 23), (15, 20), (33, 19)):
            s.set(x, y, SPARK)
        s.set(14, 22, SPARK_D)
        s.set(34, 21, SPARK_D)


# ---- Kitty Cool ---------------------------------------------------------------------------

KIT_OUTS = outs_for((KIT_FUR, OUT_DARK), (WHITE, OUT_LIGHT), (KIT_BAND, OUT_DARK))


def kitty_bandana(s, hy):
    """Teal kerchief knotted at her throat."""
    s.rect(CX - 4, hy + 7, CX + 4, hy + 8, KIT_BAND[1])
    s.rect(CX + 1, hy + 8, CX + 4, hy + 8, KIT_BAND[2])
    s.tri((CX, hy + 11), hy + 8, CX - 2, CX + 2, KIT_BAND, sh=0.14)


def kitty(s, eyes="open", pose="stand", bob=0, sway=0):
    if pose == "tinker":
        # crouched over the work: everything sinks, arms reach forward-down
        bob += 4
        kid_tail_down(s, KIT_FUR, sway, tip=KIT_FUR[0])
        kid_legs_down(s, KIT_FUR, WHITE, 0, 0, 2)
        kid_body_down(s, KIT_FUR, WHITE, bob, arms="none")
        by = 36 + bob
        s.capsule(CX - 5, by - 2, CX - 4, by + 5, 1.7, 1.5, KIT_FUR, sh=0.06)
        s.capsule(CX + 5, by - 2, CX + 4, by + 5, 1.7, 1.5, KIT_FUR, sh=0.16)
        s.ball(CX - 4, by + 6, 1.6, 1.4, WHITE, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 4, by + 6, 1.6, 1.4, WHITE, power=2.2, sh=0.10, wrap=0.10,
               curve=0.10)
        kid_head_down(s, KIT_FUR, KIT_EYE, KIT_EYEL, bob, eyes, "up", WHITE)
    else:
        kid_tail_down(s, KIT_FUR, sway, tip=KIT_FUR[0])
        kid_legs_down(s, KIT_FUR, WHITE, 0, 0, bob)
        kid_body_down(s, KIT_FUR, WHITE, bob,
                      arms="up" if pose == "cheer" else "down")
        kid_head_down(s, KIT_FUR, KIT_EYE, KIT_EYEL, bob, eyes, "up", WHITE)
    kitty_bandana(s, 25 + bob)
    s.set(CX - 5, 27 + bob, SMUDGE)                 # the grease smudge
    s.set(CX - 6, 28 + bob, SMUDGE)
    s.despeckle(passes=1)
    s.outline(KIT_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob)


# ---- kid Schweinler -------------------------------------------------------------------------

PIG_OUTS = outs_for((PIG, OUT_DARK), (SNOUT, OUT_DARK), (KERCH, OUT_DARK))


def schweinler(s, mood="idle", bob=0):
    hy = 26 + bob
    # flop ears first (head overlaps their roots)
    s.tri((CX - 8, hy - 7), hy - 3, CX - 9, CX - 3, PIG, sh=0.16)
    s.tri((CX + 8, hy - 7), hy - 3, CX + 3, CX + 9, PIG, sh=0.26)
    # stout: head and body nearly merge
    s.ball(CX, hy, 7.6, 6.4, PIG, power=2.4, wrap=0.32, curve=0.28)
    s.ball(CX, 37 + bob, 7.0, 5.4, PIG, power=2.2, wrap=0.28, curve=0.22)
    s.ball(CX, 38 + bob, 4.2, 3.4, SNOUT, power=2.2, wrap=0.10, curve=0.10)
    # trotter arms + legs
    if mood == "point":
        s.capsule(CX - 6.5, 34 + bob, CX - 11, 37 + bob, 1.8, 1.5, PIG, sh=0.06)
        s.set(CX - 12, 37 + bob, PIG[2])
    else:
        s.capsule(CX - 6.5, 34 + bob, CX - 7.5, 38 + bob, 1.8, 1.5, PIG, sh=0.06)
    s.capsule(CX + 6.5, 34 + bob, CX + 7.5, 38 + bob, 1.8, 1.5, PIG, sh=0.16)
    for lx in (CX - 3, CX + 3):
        s.capsule(lx, 40 + bob, lx, 42, 2.0, 1.8, PIG, sh=0.08)
        s.rect(lx - 1, 43, lx + 1, 44, PIG[3])      # cloven trotter
    # curly tail
    s.line([(CX + 8, 36 + bob), (CX + 9, 35 + bob), (CX + 10, 36 + bob),
            (CX + 9, 37 + bob)], PIG[2])
    # neckerchief
    s.rect(CX - 4, hy + 6, CX + 4, hy + 7, KERCH[1])
    s.tri((CX, hy + 10), hy + 7, CX - 2, CX + 2, KERCH, sh=0.14)
    # snout ON the face — the pig read
    s.ball(CX, hy + 2.5, 3.2, 2.2, SNOUT, power=2.0, wrap=0.10, curve=0.10)
    s.set(CX - 1, hy + 2, PIG_EYE)
    s.set(CX + 1, hy + 2, PIG_EYE)
    if mood == "laugh":
        for ex in (CX - 5, CX + 3):
            s.line([(ex, hy - 3), (ex + 1, hy - 4), (ex + 2, hy - 3)], PIG[3])
        s.rect(CX - 2, hy + 5, CX + 2, hy + 7, MAW)
        s.rect(CX - 1, hy + 7, CX + 1, hy + 7, TONGUE)
    else:
        for ex in (CX - 5, CX + 3):
            s.rect(ex, hy - 4, ex + 1, hy - 3, PIG_EYE)
            s.set(ex, hy - 4, GLINT)
        if mood == "point":
            s.rect(CX - 2, hy + 5, CX + 1, hy + 5, MAW)     # mid-jeer
        else:
            s.line([(CX - 1, hy + 5), (CX, hy + 5)], MOUTH)
        s.rect(CX - 6, hy - 6, CX - 3, hy - 6, PIG[3])      # smug brow
        s.rect(CX + 2, hy - 6, CX + 5, hy - 6, PIG[3])
    s.despeckle(passes=1)
    s.outline(PIG_OUTS, OUT_DARK)


# ---- the villager menagerie -----------------------------------------------------------------

SHEEP_OUTS = outs_for((WOOL, OUT_LIGHT), (SHEEP_FACE, OUT_DARK))


def sheep(s, mood="idle", bob=0):
    """Wool-cloud matron: a bumpy cream cloud, soft charcoal face, tiny legs."""
    by = 33 + bob
    for (cx, cy, rx, ry, sh) in ((CX, by + 4, 8.4, 6.2, 0.0),
                                 (CX - 6, by, 4.4, 3.8, 0.05),
                                 (CX + 6, by, 4.4, 3.8, 0.15),
                                 (CX - 3, by - 4, 4.4, 3.6, 0.0),
                                 (CX + 3, by - 4, 4.4, 3.6, 0.10),
                                 (CX, by - 6, 4.0, 3.4, 0.02)):
        s.ball(cx, cy, rx, ry, WOOL, power=2.0, sh=sh, wrap=0.24, curve=0.20)
    for lx in (CX - 4, CX + 4):
        s.capsule(lx, 41, lx, 43, 1.4, 1.2, SHEEP_FACE, sh=0.10)
    hy = 26 + bob + (1 if mood == "talk" else 0)
    s.capsule(CX - 8, hy - 1, CX - 10, hy + 2, 1.6, 1.3, SHEEP_FACE, sh=0.10)
    s.capsule(CX + 8, hy - 1, CX + 10, hy + 2, 1.6, 1.3, SHEEP_FACE, sh=0.20)
    s.ball(CX, hy, 5.0, 4.6, SHEEP_FACE, power=2.2, wrap=0.30, curve=0.24)
    s.ball(CX, hy - 4, 4.6, 2.6, WOOL, power=2.0, wrap=0.16, curve=0.12)  # wool cap
    if mood == "emote":
        _closed(s, CX - 4, hy - 1)
        _closed(s, CX + 2, hy - 1)
    else:
        for ex in (CX - 4, CX + 2):
            s.rect(ex, hy - 1, ex + 1, hy, (24, 18, 30, 255))
            s.set(ex + 1, hy - 1, GLINT)
    if mood == "talk":
        s.rect(CX - 1, hy + 3, CX, hy + 4, MAW)
    else:
        s.line([(CX - 1, hy + 3), (CX, hy + 3)], (52, 40, 56, 255))
    s.despeckle(passes=1)
    s.outline(SHEEP_OUTS, OUT_LIGHT)


OWL_OUTS = outs_for((FEATH, OUT_DARK), (DISC, OUT_LIGHT), (BEAK, OUT_DARK))


def owl(s, mood="idle", bob=0):
    """Upright egg of feathers, huge facial disc, ear tufts, folded wings."""
    hy = 24 + bob
    s.tri((CX - 6, hy - 9), hy - 4, CX - 7, CX - 4, FEATH)          # tufts
    s.tri((CX + 6, hy - 9), hy - 4, CX + 4, CX + 7, FEATH, sh=0.14)
    s.ball(CX, 32 + bob, 7.6, 10.5, FEATH, power=2.2, wrap=0.30, curve=0.24)
    if mood == "act":                               # lecturing wing raised
        s.capsule(CX + 7, 28 + bob, CX + 11, 22 + bob, 2.2, 1.6, FEATH, sh=0.14)
    else:
        s.capsule(CX + 6.5, 28 + bob, CX + 8, 37 + bob, 2.2, 1.7, FEATH, sh=0.22)
    s.capsule(CX - 6.5, 28 + bob, CX - 8, 37 + bob, 2.2, 1.7, FEATH, sh=0.06)
    s.ball(CX, 38 + bob, 4.6, 3.4, DISC, power=2.0, wrap=0.10, curve=0.10)  # belly
    # facial disc: two joined cream rounds
    s.ball(CX - 3, hy, 4.2, 4.0, DISC, power=2.0, wrap=0.12, curve=0.10)
    s.ball(CX + 3, hy, 4.2, 4.0, DISC, power=2.0, sh=0.06, wrap=0.12, curve=0.10)
    if mood == "emote":                             # proudly shut eyes
        _closed(s, CX - 4, hy - 1, happy=False)
        _closed(s, CX + 2, hy - 1, happy=False)
    else:                                           # ENORMOUS scholar eyes
        for ex in (CX - 5, CX + 1):
            s.rect(ex, hy - 2, ex + 3, hy + 1, (244, 214, 96, 255))
            s.rect(ex + 1, hy - 1, ex + 2, hy + 1, PUPIL)
            s.set(ex + 3, hy - 2, GLINT)
    s.tri((CX, hy + 4), hy + 1, CX - 1, CX + 1, BEAK, sh=0.10)
    for lx in (CX - 3, CX + 3):                     # talons
        s.rect(lx - 1, 43, lx + 1, 44, BEAK[2])
    s.despeckle(passes=1)
    s.outline(OWL_OUTS, OUT_DARK)


GOOSE_OUTS = outs_for((GOOSE, OUT_LIGHT), (BILL, OUT_DARK))


def goose(s, mood="idle", bob=0, step=0):
    """Tall white chaos: plump hull, periscope neck, orange bill. `waddle`
    mode alternates the legs and rolls the hull (the ribbon-chase gait)."""
    roll = (1 if step == 0 else -1) if mood == "waddle" else 0
    s.ball(CX + 1 + roll, 37 + bob, 7.6, 5.4, GOOSE, power=2.2, wrap=0.28, curve=0.22)
    s.capsule(CX + 6 + roll, 36 + bob, CX + 9 + roll, 33 + bob - step, 2.0, 1.4,
              GOOSE, sh=0.20)                       # tail tuft
    neck_top = 22 + bob if mood != "act" else 19 + bob
    s.capsule(CX - 3 + roll, 34 + bob, CX - 3 + roll, neck_top, 2.2, 2.0, GOOSE, sh=0.06)
    s.ball(CX - 3 + roll, neck_top - 1, 3.2, 2.8, GOOSE, power=2.2, wrap=0.20, curve=0.16)
    if mood == "act":                               # HONK — bill wide
        s.tri((CX - 10, neck_top - 2), neck_top, CX - 6, CX - 5, BILL, sh=0.08)
        s.tri((CX - 9, neck_top + 1), neck_top - 1, CX - 6, CX - 5, BILL, sh=0.20)
        s.capsule(CX + 4, 34 + bob, CX + 9, 30 + bob, 2.4, 1.6, GOOSE, sh=0.16)
    else:
        s.rect(CX - 8 + roll, neck_top - 2, CX - 5 + roll, neck_top - 1, BILL[1])
        s.set(CX - 8 + roll, neck_top - 1, BILL[2])
    s.set(CX - 3 + roll, neck_top - 2, PUPIL)       # beady eye
    lifts = ((1, 0) if step == 0 else (0, 1)) if mood == "waddle" else (0, 0)
    for lx, lift in ((CX - 1, lifts[0]), (CX + 3, lifts[1])):
        s.capsule(lx + roll, 41 + bob, lx + roll, 43 - lift, 1.2, 1.0, BILL, sh=0.10)
        s.rect(lx - 1 + roll, 43 - lift, lx + 1 + roll, 44 - lift, BILL[1])
    s.despeckle(passes=1)
    s.outline(GOOSE_OUTS, OUT_LIGHT)


# ---- Mom (Prologue A pacing pass, 2026-07-12) -------------------------------------------

MOM_FUR = ramp((178, 162, 152), "violet", 4)       # warm gray matron
MOM_SCARF = ramp((132, 188, 116), "violet", 4)     # the family sage-green
MOM_OUTS = outs_for((MOM_FUR, OUT_DARK), (WHITE, OUT_LIGHT), (MOM_SCARF, OUT_DARK))


def mom(s, mood="idle", bob=0):
    """Basil's mother: soft warm-gray cat, white flour-dusted apron, sage
    headscarf. Adult-sized (~30px) next to the kids."""
    hy = 22 + bob
    # ears peek from under the scarf
    s.tri((CX - 6, hy - 9), hy - 4, CX - 8, CX - 3, MOM_FUR)
    s.tri((CX + 6, hy - 9), hy - 4, CX + 3, CX + 8, MOM_FUR, sh=0.12)
    s.ball(CX, hy, 7.0, 6.2, MOM_FUR, power=2.4, wrap=0.34, curve=0.30)
    # headscarf: a band across the crown with a side knot
    s.rect(CX - 6, hy - 6, CX + 6, hy - 4, MOM_SCARF[1])
    s.rect(CX - 6, hy - 4, CX + 6, hy - 4, MOM_SCARF[2])
    s.rect(CX + 6, hy - 5, CX + 8, hy - 3, MOM_SCARF[0])          # the knot
    s.ball(CX, hy + 4.2, 4.6, 2.8, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    ey = hy - 2
    if mood == "emote":                             # the warm look
        _closed(s, CX - 5, ey)
        _closed(s, CX + 3, ey)
        s.rect(CX - 1, hy + 4, CX, hy + 5, MAW)
        s.set(CX - 6, hy + 2, BLUSH)
        s.set(CX + 5, hy + 2, BLUSH)
    else:
        _eye(s, CX - 5, ey, EYE_Y, EYE_YL)          # Basil's yellow — family
        _eye(s, CX + 3, ey, EYE_Y, EYE_YL)
        s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    # matronly pear body + the apron
    by = 35 + bob
    s.ball(CX, by, 7.4, 7.0, MOM_FUR, power=2.2, wrap=0.28, curve=0.22)
    for y in range(by - 5, by + 6):                 # apron panel, flat bands
        half = 4 + (2 if y > by - 1 else 1)
        for x in range(CX - half, CX + half + 1):
            s.set(x, y, WHITE[0] if x < CX else WHITE[1])
    s.rect(CX - 4, by - 6, CX - 3, by - 5, WHITE[2])              # straps
    s.rect(CX + 3, by - 6, CX + 4, by - 5, WHITE[2])
    s.rect(CX - 2, by + 2, CX + 2, by + 4, WHITE[2])              # pocket
    if mood == "act":                               # dusting flour off her paws
        s.capsule(CX - 6.5, by - 4, CX - 3, by - 7, 1.8, 1.6, MOM_FUR, sh=0.06)
        s.capsule(CX + 6.5, by - 4, CX + 3, by - 7, 1.8, 1.6, MOM_FUR, sh=0.16)
        s.ball(CX - 3, by - 8, 1.7, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 3, by - 8, 1.7, 1.5, WHITE, power=2.2, sh=0.10, wrap=0.10, curve=0.10)
        for (x, y) in ((CX - 1, by - 11), (CX + 2, by - 12), (CX, by - 10)):
            s.set(x, y, WHITE[0])                   # flour puffs
    else:
        s.capsule(CX - 7, by - 4, CX - 8, by + 1, 1.8, 1.6, MOM_FUR, sh=0.06)
        s.capsule(CX + 7, by - 4, CX + 8, by + 1, 1.8, 1.6, MOM_FUR, sh=0.16)
        s.ball(CX - 8, by + 2, 1.7, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 8, by + 2, 1.7, 1.5, WHITE, power=2.2, sh=0.10, wrap=0.10, curve=0.10)
    for lx in (CX - 3, CX + 3):                     # paws under the hem
        s.ball(lx, 43, 2.1, 1.6, MOM_FUR, power=2.2, wrap=0.10, curve=0.10)
    # tail curled around her feet
    s.capsule(CX + 7, 41 + bob, CX + 10, 42 + bob, 1.5, 1.2, MOM_FUR, sh=0.10)
    s.despeckle(passes=1)
    s.outline(MOM_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob - 6)


MOUSE_OUTS = outs_for((MOUSE, OUT_DARK), (MPINK, OUT_DARK), (WHITE, OUT_LIGHT))


def mouse(s, mood="idle", bob=0):
    """Mouse kid, knee-high: dish ears bigger than the head."""
    hy = 30 + bob
    for (ex, sh) in ((CX - 6, 0.0), (CX + 6, 0.12)):    # dish ears
        s.ball(ex, hy - 7, 4.4, 4.2, MOUSE, power=2.0, sh=sh, wrap=0.24, curve=0.18)
        s.ball(ex, hy - 7, 2.4, 2.2, MPINK, power=2.0, sh=sh, wrap=0.10, curve=0.10)
    s.ball(CX, hy, 5.6, 4.8, MOUSE, power=2.4, wrap=0.32, curve=0.26)
    s.ball(CX, 38 + bob, 4.6, 4.0, MOUSE, power=2.2, wrap=0.28, curve=0.20)
    s.ball(CX, 39 + bob, 2.6, 2.4, WHITE, power=2.2, wrap=0.10, curve=0.10)
    if mood == "act":                               # a big wave
        s.capsule(CX + 4.5, 36 + bob, CX + 8, 31 + bob, 1.4, 1.2, MOUSE, sh=0.14)
    else:
        s.capsule(CX + 4.5, 36 + bob, CX + 5.5, 40 + bob, 1.4, 1.2, MOUSE, sh=0.14)
    s.capsule(CX - 4.5, 36 + bob, CX - 5.5, 40 + bob, 1.4, 1.2, MOUSE, sh=0.04)
    for lx in (CX - 2, CX + 2):
        s.capsule(lx, 41 + bob, lx, 43, 1.2, 1.0, MOUSE, sh=0.08)
        s.ball(lx, 43.4, 1.4, 1.0, MPINK, power=2.0, wrap=0.10, curve=0.10)
    s.line([(CX + 5, 41), (CX + 7, 40), (CX + 9, 41), (CX + 10, 43)], MPINK[1])  # tail
    s.ball(CX, hy + 3, 2.8, 1.8, WHITE, power=2.0, wrap=0.10, curve=0.10)  # muzzle
    s.set(CX, hy + 2, MPINK[0])                     # pink nose
    if mood == "emote":
        _closed(s, CX - 4, hy - 2)
        _closed(s, CX + 2, hy - 2)
        s.rect(CX - 1, hy + 4, CX, hy + 5, MAW)
    else:
        for ex in (CX - 4, CX + 2):
            s.rect(ex, hy - 2, ex + 1, hy - 1, PUPIL)
            s.set(ex + 1, hy - 2, GLINT)
        s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    s.despeckle(passes=1)
    s.outline(MOUSE_OUTS, OUT_DARK)


# ---- Prologue B cast (thesis day, 2026-07-12) ----------------------------------------------

VEST = ramp((104, 62, 118, 255), "violet", 4)      # Schweinler's plum waistcoat
BADGER = ramp((128, 118, 140), "violet", 4)        # badger gray
STORK = ramp((244, 240, 232), "violet", 4)         # stork white
LINEN = ramp((236, 228, 240), "violet", 4)         # sickbed gown / bandage
SCHW_A_OUTS = outs_for((PIG, OUT_DARK), (SNOUT, OUT_DARK), (KERCH, OUT_DARK),
                       (VEST, OUT_DARK), (BRASSF, OUT_DARK))


def schweinler_adult(s, mood="idle", bob=0):
    """Schweinler grown: taller, wider, moneyed — plum waistcoat, brass
    buttons, the same smug snout. [idle, point, laugh]."""
    hy = 20 + bob
    s.tri((CX - 8, hy - 8), hy - 3, CX - 9, CX - 3, PIG, sh=0.16)
    s.tri((CX + 8, hy - 8), hy - 3, CX + 3, CX + 9, PIG, sh=0.26)
    s.ball(CX, hy, 7.8, 6.6, PIG, power=2.4, wrap=0.32, curve=0.28)
    # big pear body in the waistcoat
    by = 34 + bob
    s.ball(CX, by, 8.2, 7.6, PIG, power=2.2, wrap=0.28, curve=0.22)
    for y in range(by - 6, by + 7):                 # waistcoat panel
        half = 5 + (2 if y > by - 2 else 1)
        for x in range(CX - half, CX + half + 1):
            s.set(x, y, VEST[0] if x < CX - 1 else VEST[1])
    s.rect(CX, by - 6, CX, by + 6, VEST[3])         # closure shadow line
    for byy in (by - 4, by - 1, by + 2):            # brass buttons
        s.set(CX + 1, byy, BRASSF[0])
    s.rect(CX - 3, hy + 6, CX + 3, hy + 7, KERCH[1])            # cravat
    s.tri((CX, hy + 10), hy + 7, CX - 2, CX + 2, KERCH, sh=0.14)
    if mood == "point":
        s.capsule(CX - 7.5, by - 5, CX - 13, by - 8, 2.0, 1.6, PIG, sh=0.06)
        s.set(CX - 14, by - 9, PIG[2])
    else:
        s.capsule(CX - 7.5, by - 5, CX - 9, by + 2, 2.0, 1.6, PIG, sh=0.06)
    s.capsule(CX + 7.5, by - 5, CX + 9, by + 2, 2.0, 1.6, PIG, sh=0.16)
    for lx in (CX - 3, CX + 3):
        s.rect(lx - 1, 43, lx + 1, 44, PIG[3])      # trotters under the girth
    s.line([(CX + 9, by + 3), (CX + 10, by + 2), (CX + 11, by + 3),
            (CX + 10, by + 4)], PIG[2])             # curly tail
    s.ball(CX, hy + 2.5, 3.4, 2.3, SNOUT, power=2.0, wrap=0.10, curve=0.10)
    s.set(CX - 1, hy + 2, PIG_EYE)
    s.set(CX + 1, hy + 2, PIG_EYE)
    if mood == "laugh":
        for ex in (CX - 5, CX + 3):
            s.line([(ex, hy - 3), (ex + 1, hy - 4), (ex + 2, hy - 3)], PIG[3])
        s.rect(CX - 2, hy + 5, CX + 2, hy + 7, MAW)
        s.rect(CX - 1, hy + 7, CX + 1, hy + 7, TONGUE)
    else:
        for ex in (CX - 5, CX + 3):
            s.rect(ex, hy - 4, ex + 1, hy - 3, PIG_EYE)
            s.set(ex, hy - 4, GLINT)
        s.rect(CX - 6, hy - 6, CX - 3, hy - 6, PIG[3])
        s.rect(CX + 2, hy - 6, CX + 5, hy - 6, PIG[3])
        if mood == "point":
            s.rect(CX - 2, hy + 5, CX + 1, hy + 5, MAW)
        else:
            s.line([(CX - 1, hy + 5), (CX, hy + 5)], MOUTH)
    s.despeckle(passes=1)
    s.outline(SCHW_A_OUTS, OUT_DARK)


BADGER_OUTS = outs_for((BADGER, OUT_DARK), (WHITE, OUT_LIGHT), (FUR, OUT_DARK))


def badger(s, mood="idle", bob=0):
    """The classmate: a blunt young badger — white face, twin dark stripes,
    stocky. His honesty is a blunt instrument. [idle, shrug]."""
    hy = 23 + bob
    s.tri((CX - 6, hy - 8), hy - 4, CX - 8, CX - 3, BADGER)
    s.tri((CX + 6, hy - 8), hy - 4, CX + 3, CX + 8, BADGER, sh=0.12)
    s.ball(CX, hy, 7.0, 6.2, WHITE, power=2.4, wrap=0.26, curve=0.24)   # white face
    for sx in (-4, 4):                              # the badger stripes
        for y in range(hy - 6, hy + 3):
            s.set(CX + sx, y, FUR[1])
            s.set(CX + sx + (1 if sx > 0 else -1), y, FUR[2])
    s.ball(CX, hy + 4, 3.6, 2.2, WHITE, power=2.0, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 3, NOSE)
    for ex in (CX - 6, CX + 4):
        s.rect(ex, hy - 2, ex + 1, hy - 1, PUPIL)
        s.set(ex + 1, hy - 2, GLINT)
    s.line([(CX - 1, hy + 5), (CX + 1, hy + 5)], MOUTH)         # flat mouth
    by = 36 + bob
    s.ball(CX, by, 6.6, 5.6, BADGER, power=2.2, wrap=0.28, curve=0.22)
    s.ball(CX, by + 1, 3.6, 3.2, WHITE, power=2.2, wrap=0.10, curve=0.10)
    if mood == "act":                               # the shrug — palms up
        s.capsule(CX - 6, by - 3, CX - 9, by - 6, 1.8, 1.5, BADGER, sh=0.06)
        s.capsule(CX + 6, by - 3, CX + 9, by - 6, 1.8, 1.5, BADGER, sh=0.16)
        s.ball(CX - 9, by - 7, 1.6, 1.4, WHITE, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 9, by - 7, 1.6, 1.4, WHITE, power=2.2, sh=0.10, wrap=0.10, curve=0.10)
    else:
        s.capsule(CX - 6, by - 3, CX - 7, by + 2, 1.8, 1.5, BADGER, sh=0.06)
        s.capsule(CX + 6, by - 3, CX + 7, by + 2, 1.8, 1.5, BADGER, sh=0.16)
    for lx in (CX - 3, CX + 3):
        s.capsule(lx, by + 4, lx, 42, 2.0, 1.8, BADGER, sh=0.08)
        s.ball(lx, 43, 2.0, 1.5, FUR, power=2.2, wrap=0.10, curve=0.10)
    s.despeckle(passes=1)
    s.outline(BADGER_OUTS, OUT_DARK)


STORK_OUTS = outs_for((STORK, OUT_LIGHT), (BILL, OUT_DARK), (FUR, OUT_DARK))


def stork(s, mood="idle", bob=0):
    """Doctor Ciconia: a tall clinical stork — long orange bill, half-moon
    spectacles perched on it, black flight-feather tips. [idle, consult]."""
    hy = 16 + bob
    s.ball(CX + 2, hy, 3.6, 3.2, STORK, power=2.2, wrap=0.22, curve=0.18)  # head
    # the long bill, angled down-left; spectacles ride it
    s.capsule(CX + 1, hy + 1, CX - 8, hy + 4, 1.2, 0.7, BILL, sh=0.06)
    s.rect(CX - 2, hy + 1, CX, hy + 1, RIMLESS)     # half-moon specs
    s.set(CX - 3, hy + 2, RIMLESS)
    s.set(CX + 3, hy - 1, PUPIL)                    # calm eye
    s.capsule(CX + 3, hy + 2, CX + 2, 26 + bob, 1.8, 2.2, STORK, sh=0.04)  # neck
    s.ball(CX, 33 + bob, 6.4, 7.8, STORK, power=2.2, wrap=0.28, curve=0.22)  # body
    if mood == "act":                               # consulting wing raised
        s.capsule(CX - 5.5, 30 + bob, CX - 10, 24 + bob, 2.0, 1.4, STORK, sh=0.12)
        s.rect(CX - 11, 23 + bob, CX - 9, 24 + bob, FUR[1])       # dark tip
    else:
        s.capsule(CX - 5.5, 30 + bob, CX - 6.5, 38 + bob, 2.0, 1.5, STORK, sh=0.12)
        s.rect(CX - 7, 38 + bob, CX - 5, 39 + bob, FUR[1])
    s.capsule(CX + 5.5, 30 + bob, CX + 6, 38 + bob, 2.0, 1.5, STORK, sh=0.20)
    s.rect(CX + 5, 38 + bob, CX + 7, 39 + bob, FUR[1])            # folded tips
    for lx in (CX - 1, CX + 3):                     # long wading legs
        s.rect(lx, 39 + bob, lx, 43, BILL[2])
        s.rect(lx - 1, 43, lx + 1, 44, BILL[1])
    s.despeckle(passes=1)
    s.outline(STORK_OUTS, OUT_LIGHT)


KITTYBED_OUTS = outs_for((KIT_FUR, OUT_DARK), (WHITE, OUT_LIGHT), (LINEN, OUT_LIGHT))


def kitty_bed(s, mood="rest", bob=0):
    """Adult Kitty, sitting up against the headboard: head + gowned shoulders
    only — the bed cover y-sorts over her lap. A linen bandage wraps her brow.
    [rest(blink), vacant, polite]. The vacant eyes have NO glint — the empty
    look is the whole beat."""
    hy = 24 + bob
    # one ear up, one kinked under the bandage
    s.tri((CX - 5, hy - 9), hy - 4, CX - 7, CX - 2, KIT_FUR)
    s.tri((CX + 6, hy - 7), hy - 3, CX + 3, CX + 8, KIT_FUR, sh=0.16)
    s.ball(CX, hy, 7.0, 6.2, KIT_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(CX - 6, hy - 5, CX + 5, hy - 3, LINEN[1])              # brow bandage
    s.rect(CX - 6, hy - 3, CX + 5, hy - 3, LINEN[2])
    s.rect(CX + 5, hy - 5, CX + 7, hy - 4, LINEN[0])              # bandage tuck
    s.ball(CX, hy + 4.2, 4.4, 2.7, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    ey = hy - 1
    if mood == "rest":
        _closed(s, CX - 5, ey, happy=False)
        _closed(s, CX + 3, ey, happy=False)
        s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    elif mood == "vacant":
        for ex in (CX - 5, CX + 3):
            s.rect(ex, ey, ex + 2, ey + 2, KIT_EYE)
            s.rect(ex + 1, ey + 1, ex + 1, ey + 2, PUPIL)         # no glint
        s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    else:                                           # polite — kind to a stranger
        for ex in (CX - 5, CX + 3):
            s.rect(ex, ey, ex + 2, ey + 2, KIT_EYE)
            s.rect(ex, ey, ex + 2, ey, KIT_EYEL)
            s.rect(ex + 1, ey + 1, ex + 1, ey + 2, PUPIL)
            s.set(ex + 2, ey, GLINT)
        s.line([(CX - 2, hy + 4), (CX - 1, hy + 5), (CX, hy + 5),
                (CX + 1, hy + 4)], MOUTH)
    # gowned shoulders; the cover takes everything below
    s.capsule(CX - 6, hy + 9, CX + 6, hy + 9, 3.2, 3.2, LINEN, sh=0.08)
    s.rect(CX - 1, hy + 8, CX + 1, hy + 11, LINEN[2])             # gown vee
    s.despeckle(passes=1)
    s.outline(KITTYBED_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob - 4)


RIMLESS = (198, 214, 226, 255)                     # the stork's half-moon specs


# ---- fx strip -----------------------------------------------------------------------------

def fx_ribbon(s, r):
    """A wavy festival ribbon standing on its tail (levitated!)."""
    pts = [(8, 2), (7, 3), (7, 4), (8, 5), (9, 6), (9, 7), (8, 8), (7, 9),
           (7, 10), (8, 11), (8, 12), (9, 13)]
    for i, (x, y) in enumerate(pts):
        s.set(x, y, r[1] if i % 4 else r[0])
        s.set(x + 1, y, r[2])
    s.set(8, 1, r[0])


def fx_sparkle(s, big):
    c = 8
    n = 3 if big else 2
    for d in range(1, n + 1):
        s.set(c, c - d, SPARK if d < n else SPARK_D)
        s.set(c, c + d, SPARK if d < n else SPARK_D)
        s.set(c - d, c, SPARK if d < n else SPARK_D)
        s.set(c + d, c, SPARK if d < n else SPARK_D)
    s.set(c, c, GLINT)
    if big:
        for (x, y) in ((c - 1, c - 1), (c + 1, c - 1), (c - 1, c + 1), (c + 1, c + 1)):
            s.set(x, y, SPARK_D)


def fx_gear(s):
    for (x, y) in ((8, 2), (8, 14), (2, 8), (14, 8), (4, 4), (12, 4), (4, 12),
                   (12, 12)):
        s.rect(x - 1, y - 1, x + 1, y + 1, BRASSF[1])
    s.ball(8, 8, 5.0, 5.0, BRASSF, power=2.0, wrap=0.24, curve=0.14)
    s.blob(8, 8, 1.8, 1.8, None)                    # the axle hole
    s.despeckle(passes=1)
    s.outline(outs_for((BRASSF, OUT_DARK)), OUT_DARK)


def fx_spring(s):
    for i, y in enumerate(range(3, 13, 2)):
        s.rect(5, y, 10, y, STEELF[0 if i % 2 == 0 else 1])
        s.set(10, y + 1, STEELF[2])
        s.set(5, y + 1, STEELF[2])
    s.rect(4, 2, 11, 2, STEELF[1])
    s.rect(4, 13, 11, 13, STEELF[2])
    s.outline(outs_for((STEELF, OUT_DARK)), OUT_DARK)


def fx_crank(s):
    s.capsule(5, 12, 5, 5, 1.4, 1.4, STEELF, sh=0.06)   # shaft
    s.capsule(5, 5, 11, 5, 1.3, 1.3, STEELF, sh=0.14)   # arm
    s.capsule(11, 5, 11, 9, 1.6, 1.6, WOODF, sh=0.06)   # wooden grip
    s.despeckle(passes=1)
    s.outline(outs_for((STEELF, OUT_DARK), (WOODF, OUT_DARK)), OUT_DARK)


def fx_whirligig(s, mode):
    """Kitty's hand-cranked flyer: a little wooden pod under a rotor."""
    s.ball(8, 10, 3.0, 3.4, WOODF, power=2.2, wrap=0.24, curve=0.18)   # pod
    s.set(8, 13, BRASSF[1])                          # crank nub
    s.rect(8, 5, 8, 7, STEELF[1])                    # mast
    if mode == "droop":                              # rotor hangs dead
        s.line([(5, 8), (6, 7), (7, 6)], WOODF[2])
        s.line([(9, 6), (10, 7), (11, 8)], WOODF[2])
    elif mode == "spin0":
        s.rect(2, 4, 14, 4, WOODF[1])                # blur bar
        s.set(2, 5, WOODF[2])
        s.set(14, 5, WOODF[2])
    else:
        s.rect(4, 4, 12, 4, WOODF[0])                # alternate blur
        s.set(3, 3, WOODF[2])
        s.set(13, 3, WOODF[2])
    s.despeckle(passes=1)
    s.outline(outs_for((WOODF, OUT_DARK), (STEELF, OUT_DARK), (BRASSF, OUT_DARK)),
              OUT_DARK)


BAGP = ramp((166, 128, 84), "violet", 4)            # paper sack
STINK = (150, 196, 120, 210)                        # the wavy stink lines
PRINT = (122, 84, 52, 235)                          # tracked-in brown
PUDDLE = ramp((120, 150, 186), "teal", 4)
BIRDY = ramp((240, 208, 96), "violet", 4)           # Dr. Feathers gold


def fx_bag(s):
    """The bag. THE bag. Crumpled paper sack, stink wisps rising."""
    for y in range(7, 14):
        half = 3 + (1 if y > 9 else 0)
        for x in range(8 - half, 8 + half + 1):
            s.set(x, y, BAGP[0] if x < 7 else BAGP[1])
    s.rect(6, 6, 10, 7, BAGP[2])                    # rolled crumple top
    s.set(5, 7, BAGP[2])
    s.set(11, 7, BAGP[2])
    s.line([(7, 10), (8, 11), (9, 10)], BAGP[3])    # crease
    s.despeckle(passes=1)
    s.outline(outs_for((BAGP, OUT_DARK)), OUT_DARK)
    for (x, y) in ((5, 4), (5, 3), (10, 4), (10, 2), (8, 1)):     # stink, post-outline
        s.set(x, y, STINK)


def fx_pawprint(s):
    """One tracked-in paw print: a pad and three toe dabs."""
    s.rect(7, 9, 9, 11, PRINT)
    s.set(6, 10, PRINT)
    s.set(10, 10, PRINT)
    for (x, y) in ((6, 7), (8, 6), (10, 7)):
        s.rect(x, y, x, y + 1, PRINT)


def fx_bird(s, wing_up):
    """Dr. Feathers, the morning alarm: a round gold songbird."""
    s.ball(8, 9, 3.4, 3.0, BIRDY, power=2.2, wrap=0.24, curve=0.18)
    s.tri((12, 9), 11, 10, 12, BIRDY, sh=0.3)       # tail
    s.set(4, 8, BILL[1])                            # beak
    s.set(6, 8, PUPIL)
    if wing_up:
        s.line([(8, 5), (9, 4), (10, 4)], BIRDY[2])
        s.tri((10, 3), 6, 8, 11, BIRDY, sh=0.2)
    else:
        s.tri((10, 12), 9, 8, 11, BIRDY, sh=0.2)
    s.rect(7, 12, 7, 13, BILL[2])                   # legs
    s.rect(9, 12, 9, 13, BILL[2])
    s.despeckle(passes=1)
    s.outline(outs_for((BIRDY, OUT_DARK)), OUT_DARK)


def fx_puddle(s):
    """A morning rain puddle — flat, walk-in-it-and-regret-it."""
    for y in range(9, 14):
        vy = abs(y - 11.5)
        half = int(6 - vy * 1.8)
        for x in range(8 - half, 8 + half + 1):
            s.set(x, y, PUDDLE[1] if (x + y) % 7 else PUDDLE[0])
    s.rect(5, 10, 7, 10, PUDDLE[0])                 # shine streak
    s.set(10, 12, PUDDLE[0])
    s.outline(outs_for((PUDDLE, (70, 92, 122, 255))), (70, 92, 122, 255))


def fx_zzz(s):
    """A drifting sleep-Z trio (the wake-up beat)."""
    for (x, y, big) in ((4, 11, False), (8, 7, False), (11, 2, True)):
        w = 3 if big else 2
        s.rect(x, y, x + w, y, SPARK_D if not big else SPARK)
        s.rect(x, y + w, x + w, y + w, SPARK_D if not big else SPARK)
        for i in range(w + 1):
            s.set(x + w - i, y + i, SPARK_D if not big else SPARK)


# ---- build all sheets -----------------------------------------------------------------------

# kid Basil: 6x4
kb = [[new() for _ in range(6)] for _ in range(4)]
walk_bob = [0, -1, -1, 0, -1, -1]
walk_liftl = [0, 1, 1, 0, 0, 0]
walk_liftr = [0, 0, 0, 0, 1, 1]
walk_tail = [0, 1, 1, 2, 1, 1]
for i in range(6):
    kb_down(kb[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i], walk_tail[i])
    kb_up(kb[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i], walk_tail[i])
side_fF = [(2, 0), (0, 0), (-3, 0), (-5, 0), (-3, 1), (0, 1)]
side_fB = [(-1, 0), (2, 1), (4, 1), (6, 0), (4, 0), (2, 0)]
for i in range(6):
    kb_side(kb[2][i], walk_bob[i], side_fF[i], side_fB[i], walk_tail[i] - 1)
kb_down(kb[3][0], eyes="hurt", ears="droop", tail_sway=2)
kb_down(kb[3][1], eyes="hurt", ears="droop", tail_sway=-1, bob=1)
kb_down(kb[3][2], eyes="blink")                     # matches walk_down f0
kb_side(kb[3][3], 0, side_fF[0], side_fB[0], 2, tail_raised=True)  # tail-flick
kb_down(kb[3][4], eyes="happy", tail_sway=2, arms="up")
kb_down(kb[3][5], eyes="sad", ears="droop", tail_droop=1)
write_cells(os.path.join(HERE, "kid_basil_gen.png"), kb, CELL)

# Sage: [idle, blink, cast x2, giggle x2]
sg = [[new() for _ in range(6)]]
sage(sg[0][0])
sage(sg[0][1], eyes="blink")
sage(sg[0][2], arms="up", sparkle=True)
sage(sg[0][3], arms="up", bob=-1, sparkle=True)
sage(sg[0][4], eyes="happy", sway=2)
sage(sg[0][5], eyes="happy", bob=-1, sway=-2)
write_cells(os.path.join(HERE, "npc_sage_gen.png"), sg, CELL)

# Schweinler: [idle x2, point x2, laugh x2]
sw = [[new() for _ in range(6)]]
schweinler(sw[0][0])
schweinler(sw[0][1], bob=-1)
schweinler(sw[0][2], mood="point")
schweinler(sw[0][3], mood="point", bob=-1)
schweinler(sw[0][4], mood="laugh")
schweinler(sw[0][5], mood="laugh", bob=-2)
write_cells(os.path.join(HERE, "npc_schweinler_gen.png"), sw, CELL)

# Kitty: [idle, blink, tinker x2, beam x2]
kt = [[new() for _ in range(6)]]
kitty(kt[0][0])
kitty(kt[0][1], eyes="blink")
kitty(kt[0][2], pose="tinker")
kitty(kt[0][3], pose="tinker", bob=-1)
kitty(kt[0][4], eyes="happy", pose="cheer", sway=2)
kitty(kt[0][5], eyes="happy", pose="cheer", bob=-1, sway=-2)
write_cells(os.path.join(HERE, "npc_kitty_gen.png"), kt, CELL)

# villagers: [idle x2, act x2]
for fname, fn in (("npc_sheep_gen.png", sheep), ("npc_owl_gen.png", owl),
                  ("npc_mouse_gen.png", mouse)):
    vg = [[new() for _ in range(4)]]
    fn(vg[0][0])
    fn(vg[0][1], bob=-1)
    fn(vg[0][2], mood="act" if fn is not sheep else "talk")
    fn(vg[0][3], mood="act" if fn is not sheep else "talk", bob=-1)
    write_cells(os.path.join(HERE, fname), vg, CELL)

# the goose: [idle x2, honk x2, WADDLE x2] — the ribbon chase needs a gait
gg = [[new() for _ in range(6)]]
goose(gg[0][0])
goose(gg[0][1], bob=-1)
goose(gg[0][2], mood="act")
goose(gg[0][3], mood="act", bob=-1)
goose(gg[0][4], mood="waddle", step=0)
goose(gg[0][5], mood="waddle", step=1)
write_cells(os.path.join(HERE, "npc_goose_gen.png"), gg, CELL)

# Mom: [idle x2, flour-dust act x2, warm emote x2]
mm = [[new() for _ in range(6)]]
mom(mm[0][0])
mom(mm[0][1], bob=-1)
mom(mm[0][2], mood="act")
mom(mm[0][3], mood="act", bob=-1)
mom(mm[0][4], mood="emote")
mom(mm[0][5], mood="emote", bob=-1)
write_cells(os.path.join(HERE, "npc_mom_gen.png"), mm, CELL)

# Prologue B cast
sa = [[new() for _ in range(6)]]
schweinler_adult(sa[0][0])
schweinler_adult(sa[0][1], bob=-1)
schweinler_adult(sa[0][2], mood="point")
schweinler_adult(sa[0][3], mood="point", bob=-1)
schweinler_adult(sa[0][4], mood="laugh")
schweinler_adult(sa[0][5], mood="laugh", bob=-2)
write_cells(os.path.join(HERE, "npc_schweinler_adult_gen.png"), sa, CELL)

bd = [[new() for _ in range(4)]]
badger(bd[0][0])
badger(bd[0][1], bob=-1)
badger(bd[0][2], mood="act")
badger(bd[0][3], mood="act", bob=-1)
write_cells(os.path.join(HERE, "npc_badger_gen.png"), bd, CELL)

st = [[new() for _ in range(4)]]
stork(st[0][0])
stork(st[0][1], bob=-1)
stork(st[0][2], mood="act")
stork(st[0][3], mood="act", bob=-1)
write_cells(os.path.join(HERE, "npc_stork_gen.png"), st, CELL)

kb2 = [[new() for _ in range(6)]]
kitty_bed(kb2[0][0], "rest")
kitty_bed(kb2[0][1], "rest", bob=-1)
kitty_bed(kb2[0][2], "vacant")
kitty_bed(kb2[0][3], "vacant", bob=-1)
kitty_bed(kb2[0][4], "polite")
kitty_bed(kb2[0][5], "polite", bob=-1)
write_cells(os.path.join(HERE, "npc_kitty_bed_gen.png"), kb2, CELL)

# fx strip — 16 cells (256x16); cells 0-9 are Prologue A's, 10-15 thesis day's
fx = [[Sprite(16, grain=1, salt=3, jitter=0.0) for _ in range(16)]]
fx_ribbon(fx[0][0], RIBBON_M)
fx_ribbon(fx[0][1], RIBBON_G)
fx_sparkle(fx[0][2], False)
fx_sparkle(fx[0][3], True)
fx_gear(fx[0][4])
fx_spring(fx[0][5])
fx_crank(fx[0][6])
fx_whirligig(fx[0][7], "droop")
fx_whirligig(fx[0][8], "spin0")
fx_whirligig(fx[0][9], "spin1")
fx_bag(fx[0][10])
fx_pawprint(fx[0][11])
fx_bird(fx[0][12], False)
fx_bird(fx[0][13], True)
fx_puddle(fx[0][14])
fx_zzz(fx[0][15])
write_cells(os.path.join(HERE, "prologue_fx.png"), fx, 16)

print("prologue cast written: kid_basil (6x4) + 12 NPC sheets + fx strip x16")
