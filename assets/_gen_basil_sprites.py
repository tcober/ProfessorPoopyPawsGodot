#!/usr/bin/env python3
"""Basil, the science cat — sprite sheet on the _sprites.py kit.

Writes assets/basil_gen.png (576x672, 96x96 cells, 6x7) matching
entities/player/player_frames.tres (FROZEN region contract):

  row0 walk_down(6)   row1 walk_up(6)   row2 walk_side(6, faces RIGHT — player.gd
                                              sets flip_h only when facing LEFT)
  row3 shoot_down(4)  row4 shoot_up(4)  row5 shoot_side(4)
  row6 hurt(2) + idle_down blink + idle_side tail-flick + happy + sad

Art contracts consumed by code: feet baseline y=88 (_core.ZONE_FEET); origin
(48,48); in the leveled shoot frames the gun muzzle TIP sits exactly 32px from
the cell center along the facing (player.gd muzzle_offset spawns the bolt and
flash there); idle_down/idle_side alternate walk f0 with the blink/tail-flick
cells, so walk f0 is a planted neutral pose the extras redraw exactly.

Character (docs/DESIGN.md): jet-black tuxedo cat — narrow white blaze into a
plump muzzle, white paws/chest, close-set yellow eyes with round pupils (stern
default, sweet ^^ on blink), black nose smudge, whiskers breaking the
silhouette (drawn post-outline), aviator goggles up on the head, straight-cut
lab coat, laser gun (purple GUNP body, green GUNE emitter). CT field-sprite
proportions: ~66px figure, head/torso/legs each roughly a third; the whole body
is one Rig so walk cycles keep volumes frame-to-frame.

Re-run: python3 assets/_gen_basil_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import write_cells, ZONE_CELL, ZONE_FEET
from _sprites import Sprite, Rig
from _palette import BASIL, ramp4

CELL, COLS, ROWS = ZONE_CELL, 6, 7
FEET = ZONE_FEET          # 88 — bottom row of the paw FILL (outline sits at 89)
CX = 48

FUR    = BASIL["FUR"]
WHITE  = BASIL["WHITE"]
COATR  = BASIL["COATR"]
PANTR  = BASIL["PANTR"]
GOGRIM = BASIL["GOGRIM"]
GOGLEN = BASIL["GOGLEN"]
GUNR   = BASIL["GUNR"]
EYE_Y, EYE_YL = BASIL["EYE_Y"], BASIL["EYE_YL"]
PUPIL, GLINT  = BASIL["PUPIL"], BASIL["GLINT"]
NOSE, MOUTH   = BASIL["NOSE"], BASIL["MOUTH"]
EARIN, EARIN_D = BASIL["EARIN"], BASIL["EARIN_D"]
WHISK, WHISKD  = BASIL["WHISK"], BASIL["WHISKD"]
GUNE, GUNP     = BASIL["GUNE"], BASIL["GUNP"]

# PALETTE REQUEST: purple laser-gun body ramp derived from the GUNP accent (the
# brief specifies a purple gun body; _palette only carries the gray GUNR ramp).
GUNPR   = ramp4(GUNP, "violet")
OUT_GUN = (40, 22, 60, 255)
# local expression accents (single-use, kept out of the shared palette)
LID    = (188, 158, 66, 255)      # closed-eye stroke
BLUSH  = (238, 160, 158, 255)
TEAR   = (170, 214, 250, 255)
MAW    = (96, 54, 60, 255)
TONGUE = (226, 120, 128, 255)

OUTS = dict(BASIL["OUTS"])
for _c in GUNPR:
    OUTS[_c] = OUT_GUN
OUT_FB = BASIL["OUT_FALLBACK"]
RAMPS = [FUR, WHITE, COATR, PANTR, GOGRIM, GOGLEN, GUNR, GUNPR]


def new():
    return Sprite(CELL, grain=2, salt=5)


def finish(s):
    s.despeckle(passes=1)
    s.cluster_shade(RAMPS)
    s.outline(OUTS, OUT_FB)


# ---- the body rig (down/up views share it; side view has its own) -----------------
RIG = Rig(
    head=(48, 36),
    coat=(48, 44),
    hipL=(43, 66), hipR=(53, 66),
    footL=(43, 85), footR=(53, 85),
    shL=(36, 47), shR=(60, 47),
    handL=(32.5, 58), handR=(63.5, 58),
    tail=(60, 66),
)

RIG_S = Rig(               # side view, facing RIGHT
    skull=(46, 36),
    coat=(46, 44),
    hipF=(50, 66), hipB=(41, 66),
    footF=(51, 85), footB=(41, 85),
    sh=(47, 46), hand=(45, 58),
    tail=(33, 60),
)


# ---- down-view parts ----------------------------------------------------------------

def head_down(s, dx=0, dy=0, eyes="open", ears="up"):
    hx, hy = CX + dx, 36 + dy
    # ears first (skull overlaps their base). Tall triangles, pink inner.
    if ears == "up":
        s.tri((hx - 11, hy - 21), hy - 6, hx - 17, hx - 3, FUR)
        s.tri((hx + 11, hy - 21), hy - 6, hx + 3, hx + 17, FUR, sh=0.15)
        s.tri((hx - 11, hy - 17), hy - 8, hx - 15, hx - 6, EARIN)
        s.tri((hx + 11, hy - 17), hy - 8, hx + 7, hx + 16, EARIN_D)
    elif ears == "droop":                          # slouched out + down (sad)
        s.tri((hx - 14, hy - 8), hy, hx - 18, hx - 4, FUR)
        s.tri((hx + 14, hy - 8), hy, hx + 4, hx + 18, FUR, sh=0.15)
    else:                                          # pinned flat (hurt / recoil)
        s.tri((hx - 20, hy - 6), hy, hx - 14, hx - 2, FUR)
        s.tri((hx + 20, hy - 6), hy, hx + 2, hx + 14, FUR, sh=0.15)
    # skull dome + plump white muzzle + narrow blaze between the eyes
    s.ball(hx, hy, 13.0, 10.8, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.ball(hx, hy + 8, 7.6, 4.6, WHITE, power=2.2, wrap=0.16, curve=0.14)
    s.tri((hx, hy - 7), hy + 4, hx - 1.5, hx + 1.5, WHITE)
    # cheek sheen ticks
    s.line([(hx - 12, hy - 3), (hx - 11, hy - 4), (hx - 10, hy - 5)], FUR[0])
    s.line([(hx + 10, hy - 5), (hx + 11, hy - 4), (hx + 12, hy - 3)], FUR[1])
    # nose smudge
    s.rect(hx - 2, hy + 5, hx + 1, hy + 6, NOSE)
    s.set(hx - 2, hy + 5, (52, 42, 48, 255))
    # mouths
    if eyes == "hurt":
        s.rect(hx - 2, hy + 8, hx + 1, hy + 11, MOUTH)          # open wail
        s.rect(hx - 1, hy + 10, hx, hy + 11, MAW)
    elif eyes == "wince":
        s.rect(hx - 4, hy + 8, hx + 3, hy + 9, MOUTH)           # gritted teeth
        s.rect(hx - 1, hy + 8, hx, hy + 9, WHITE[0])
    elif eyes == "happy":
        s.rect(hx - 4, hy + 7, hx + 3, hy + 11, MAW)            # open grin
        s.rect(hx - 2, hy + 10, hx + 1, hy + 11, TONGUE)
        s.rect(hx - 12, hy + 5, hx - 11, hy + 6, BLUSH)
        s.rect(hx + 11, hy + 5, hx + 12, hy + 6, BLUSH)
    elif eyes == "sad":
        s.line([(hx - 3, hy + 9), (hx - 2, hy + 8), (hx - 1, hy + 9),
                (hx, hy + 8), (hx + 1, hy + 9)], MOUTH)         # wobble frown
    else:
        s.set(hx - 1, hy + 7, MOUTH)
        s.set(hx, hy + 7, MOUTH)
        s.line([(hx - 3, hy + 8), (hx - 2, hy + 8)], MOUTH)
        s.line([(hx + 1, hy + 8), (hx + 2, hy + 8)], MOUTH)
    # whisker dots on the muzzle
    for wx, wy in ((-7, 5), (-9, 8), (6, 5), (8, 8)):
        s.set(hx + wx, hy + wy, WHISKD)
    # eyes — close-set, stern default
    if eyes == "open":
        _eye(s, hx - 8, hy - 4, 0)
        _eye(s, hx + 4, hy - 4, 3)
    elif eyes in ("closed", "happy"):                            # sweet ^ ^
        for ex in (hx - 8, hx + 4):
            s.line([(ex, hy - 1), (ex + 1, hy - 2), (ex + 2, hy - 3),
                    (ex + 3, hy - 2), (ex + 4, hy - 1)], LID)
    elif eyes == "sad":                                          # teary, downcast
        for ex in (hx - 8, hx + 4):
            s.rect(ex, hy - 3, ex + 3, hy + 1, EYE_Y)
            s.rect(ex, hy - 3, ex + 3, hy - 2, FUR[2])           # heavy upper lid
            s.rect(ex + 1, hy - 1, ex + 2, hy + 1, PUPIL)
            s.set(ex + 1, hy + 1, GLINT)
            s.set(ex + 3, hy, GLINT)                             # double shine = teary
        s.line([(hx - 5, hy - 5), (hx - 4, hy - 6)], FUR[0])     # raised inner brows
        s.line([(hx + 4, hy - 6), (hx + 5, hy - 5)], FUR[0])
        s.rect(hx - 8, hy + 3, hx - 8, hy + 4, TEAR)             # a welling tear
    else:                                                        # hurt / wince >_<
        for ex, o in ((hx - 8, 2), (hx + 6, -2)):
            s.line([(ex, hy - 4), (ex + 1, hy - 3)], LID)
            s.set(ex + o, hy - 2, LID)
            s.line([(ex, hy, ), (ex + 1, hy - 1)], LID)
    # goggles pushed up on the forehead: strap + rimmed lenses bumping the dome
    s.rect(hx - 15, hy - 9, hx + 15, hy - 8, GOGRIM[2])
    for gx in (hx - 7, hx + 7):
        s.ball(gx, hy - 11, 4.4, 3.6, GOGRIM, power=2.0)
        s.ball(gx, hy - 11, 2.6, 2.0, GOGLEN, power=2.0)
        s.set(gx - 1, hy - 12, (252, 240, 214, 255))
        s.set(gx, hy - 12, (252, 240, 214, 255))


def _eye(s, ex, ey, brow_out):
    """4x5 stern yellow eye: bright top band, 2px pupil, hard glint, outer brow."""
    s.rect(ex, ey, ex + 3, ey + 4, EYE_Y)
    s.rect(ex, ey, ex + 3, ey + 1, EYE_YL)
    s.rect(ex + 1, ey + 2, ex + 2, ey + 4, PUPIL)
    s.set(ex + 1, ey + 1, GLINT)
    s.set(ex + brow_out, ey - 2, FUR[3])
    s.set(ex + brow_out + (1 if brow_out == 0 else -1), ey - 2, FUR[3])


def whiskers_down(s, dx=0, dy=0):
    """Solid strokes off the cheeks, past the outline (drawn last)."""
    for pts in (((31, 40), (29, 40), (27, 41), (25, 42)),
                ((31, 44), (29, 45), (27, 46)),
                ((65, 40), (67, 40), (69, 41), (71, 42)),
                ((65, 44), (67, 45), (69, 46))):
        for (x, y) in pts:
            s.set(x + dx, y + dy, WHISK)


def legs_down(s, p, liftL=0, liftR=0, spread=0, heels=False):
    """Tapered trouser legs + white paws. spread braces the stance (recoil)."""
    for (hip, foot, lift, sp, sh) in (("hipL", "footL", liftL, -spread, 0.0),
                                      ("hipR", "footR", liftR, spread, 0.10)):
        hx, hy = p[hip]
        fx, fy = p[foot]
        hx += sp
        fx += sp
        fy -= lift
        s.capsule(hx, hy, fx, fy - 3, 4.0, 3.0, PANTR, sh=sh)
        s.ball(fx, fy + 0.6, 4.1, 2.9, WHITE, power=2.2, sh=sh * 0.5,
               wrap=0.14, curve=0.12)
        if not heels:
            s.rect(fx - 0.5, fy + 2, fx + 0.5, fy + 3, WHITE[3])   # toe notch


def coat_down(s, dy=0, back=False):
    """Straight-cut lab coat. Front: placket + lapels over a white chest tuft,
    hip pocket, purple pen. Back: vent seam, belt, collar band."""
    top, hem = 44 + dy, 65 + dy
    s.panel(CX, top, hem, 11.0, 13.6, COATR, hem_curve=2,
            folds=(CX - 7, CX + 6) if not back else (CX - 6, CX + 7),
            round_top=3)
    if back:
        for y in range(top + 4, hem + 2):
            s.set(CX, y, COATR[2])
            s.set(CX + 1, y, COATR[2])
        s.rect(CX - 6, top + 9, CX + 5, top + 11, COATR[1])       # back belt
        s.rect(CX - 5, top + 10, CX - 4, top + 10, COATR[3])
        s.rect(CX + 3, top + 10, CX + 4, top + 10, COATR[3])
        s.rect(CX - 11, top, CX + 10, top + 2, COATR[1])          # collar band
        return
    for y in range(top + 6, hem + 2):                             # center placket
        s.set(CX, y, COATR[3])
        s.set(CX + 1, y, COATR[3])
        s.set(CX - 1, y, COATR[0])
    s.tri((CX, top), top + 6, CX - 4, CX + 4, WHITE)              # chest tuft
    s.line([(CX - 6, top + 2), (CX - 5, top + 3), (CX - 4, top + 4)], COATR[0])
    s.line([(CX + 6, top + 2), (CX + 5, top + 3), (CX + 4, top + 4)], COATR[2])
    s.rect(CX - 12, top + 18, CX - 6, top + 18, COATR[3])         # hip pocket
    s.rect(CX - 12, top + 19, CX - 6, top + 19, COATR[2])
    s.rect(CX - 8, top + 6, CX - 7, top + 9, GUNP)                # breast pen
    s.rect(CX - 8, top + 9, CX - 7, top + 10, (132, 84, 174, 255))


def arms_down(s, p, dl=0, dr=0):
    """Hanging coat sleeves (tapered) + white paws; dl/dr swing them."""
    for (sh_a, hand, d, sh) in (("shL", "handL", dl, 0.0), ("shR", "handR", dr, 0.12)):
        sx, sy = p[sh_a]
        hx, hy = p[hand]
        hy += d
        s.capsule(sx, sy, hx, hy, 3.6, 3.0, COATR, sh=sh)
        s.rect(hx - 3, hy - 1, hx + 3, hy, COATR[3])              # cuff
        s.ball(hx, hy + 2.6, 3.2, 2.7, WHITE, power=2.2, sh=sh * 0.5,
               wrap=0.14, curve=0.12)


def tail_down(s, p, sway=0, droop=0):
    """Tail curling out right of the hem; sway shifts the tip, droop sinks it."""
    tx, ty = p["tail"]
    if droop:
        s.capsule(tx, ty + 2, tx + 6, ty + 6, 3.2, 2.6, FUR, sh=0.08)
        s.capsule(tx + 6, ty + 6, tx + 10, ty + 4, 2.6, 2.1, FUR, sh=0.12)
        s.set(tx + 11, ty + 3, FUR[0])
        return
    s.capsule(tx, ty + 2, tx + 6, ty - 6, 3.2, 2.6, FUR, sh=0.08)
    s.capsule(tx + 6, ty - 6, tx + 7 + sway, ty - 14, 2.6, 2.1, FUR, sh=0.12)
    s.set(tx + 6 + sway, ty - 16, FUR[0])                         # tip catchlight
    s.set(tx + 7 + sway, ty - 16, FUR[0])


def gun_down(s, dy=0, mode="aim"):
    """Two-paw grip, barrel pointing SOUTH. In leveled frames the emitter tip
    fills (48, 80) — cell center + muzzle_offset(32) toward the facing."""
    k = -4 if mode == "recoil" else 0
    if mode == "raise":                                           # gun still at the chest
        s.capsule(36, 47 + dy, 42, 55 + dy, 3.4, 3.0, COATR)
        s.capsule(60, 47 + dy, 54, 55 + dy, 3.4, 3.0, COATR, sh=0.12)
        s.ball(45, 58 + dy, 3.0, 2.6, WHITE, wrap=0.14)
        s.ball(51, 58 + dy, 3.0, 2.6, WHITE, wrap=0.14)
        s.capsule(44, 60 + dy, 52, 60 + dy, 2.8, 2.8, GUNPR)
        s.capsule(48, 62 + dy, 48, 68 + dy, 2.3, 2.1, GUNPR, sh=0.08)
        s.rect(47, 69 + dy, 49, 70 + dy, GUNE)
        return
    s.capsule(36, 47 + dy, 42, 56 + dy, 3.4, 3.0, COATR)          # upper arms in
    s.capsule(60, 47 + dy, 54, 56 + dy, 3.4, 3.0, COATR, sh=0.12)
    s.capsule(42, 56 + dy, 45, 61 + dy + k, 3.0, 2.8, COATR)
    s.capsule(54, 56 + dy, 51, 61 + dy + k, 3.0, 2.8, COATR, sh=0.12)
    s.ball(45, 63 + dy + k, 3.0, 2.6, WHITE, wrap=0.14)           # gripping paws
    s.ball(51, 63 + dy + k, 3.0, 2.6, WHITE, wrap=0.14)
    s.capsule(44, 64.5 + dy + k, 52, 64.5 + dy + k, 2.9, 2.9, GUNPR)   # receiver
    s.capsule(48, 67 + dy + k, 48, 76 + dy + k, 2.5, 2.2, GUNPR, sh=0.06)  # barrel
    s.rect(46, 70 + dy + k, 46, 73 + dy + k, GUNR[1])             # side rail
    s.blob(48, 78.7 + dy + k, 2.6, 1.9, GUNE)                     # emitter tip
    s.set(48, 79 + dy + k, (240, 255, 240, 255))
    if mode != "recoil":
        s.set(48, 80 + dy, GUNE)                                  # tip kisses y=80


# ---- full down/up poses ---------------------------------------------------------------

def cat_down(s, bobY=0, liftL=0, liftR=0, swing=0, tail_sway=0, tail_droop=0,
             eyes="open", ears="up", head_dx=0, gun=None, spread=0):
    p = RIG.pose(head=(head_dx, bobY), coat=(0, bobY), tail=(tail_sway // 2, bobY),
                 shL=(0, bobY), shR=(0, bobY), handL=(0, bobY), handR=(0, bobY))
    tail_down(s, p, tail_sway, tail_droop)
    legs_down(s, p, liftL, liftR, spread)
    coat_down(s, bobY)
    if gun is None:
        arms_down(s, p, swing, -swing)
    else:
        gun_down(s, bobY, gun)
    head_down(s, head_dx, bobY, eyes, ears)
    finish(s)
    whiskers_down(s, head_dx, bobY)


def head_up(s, dy=0):
    """Back of the head: dome, ear backs, goggle strap + buckle, neck part."""
    hy = 36 + dy
    s.tri((CX - 11, hy - 21), hy - 6, CX - 17, CX - 3, FUR)
    s.tri((CX + 11, hy - 21), hy - 6, CX + 3, CX + 17, FUR, sh=0.15)
    s.tri((CX - 11, hy - 17), hy - 8, CX - 15, CX - 6, FUR, sh=0.38)
    s.tri((CX + 11, hy - 17), hy - 8, CX + 7, CX + 16, FUR, sh=0.46)
    s.ball(CX, hy, 13.0, 10.8, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(CX - 11, hy - 8, CX + 11, hy - 7, GOGRIM[2])           # thin strap
    s.rect(CX - 2, hy - 8, CX + 2, hy - 7, GOGRIM[1])             # buckle
    s.ball(CX - 4, hy - 9.5, 2.2, 1.5, GOGRIM, power=2.0)         # cup tops, barely
    s.ball(CX + 4, hy - 9.5, 2.2, 1.5, GOGRIM, power=2.0, sh=0.15)  # peeking over
    s.line([(CX - 6, hy + 10), (CX - 4, hy + 11), (CX - 2, hy + 12), (CX + 2, hy + 12),
            (CX + 4, hy + 11), (CX + 6, hy + 10)], FUR[3])


def tail_up(s, sway=0):
    """Raised swish, seen from behind on his right."""
    s.capsule(58, 62, 64, 54, 3.1, 2.6, FUR, sh=0.10)
    s.capsule(64, 54, 65 + sway, 45, 2.6, 2.1, FUR, sh=0.14)
    s.set(64 + sway, 43, FUR[0])
    s.set(65 + sway, 43, FUR[0])


def gun_up(s, dy=0, mode="aim", stage="back"):
    """One-arm skyward aim seen from behind: the barrel rises past the head
    (the `back` stage draws it BEFORE the body, so the torso/head occlude all
    but the muzzle between the ears), and the `front` stage adds the raised
    gripping paw beside the ear. Leveled tip fills (48..49, 16)."""
    top = {"raise": 27, "recoil": 22}.get(mode, 19)
    if stage == "back":
        s.capsule(49, 44 + dy, 49, top + 3 + dy, 2.7, 2.4, GUNPR, sh=0.10)
        s.capsule(49, top + 3 + dy, 49, top + dy, 2.2, 2.0, GUNPR, sh=0.04)
        s.blob(49, top - 1.5 + dy, 2.4, 1.8, GUNE)
        s.set(49, top - 2 + dy, (240, 255, 240, 255))
        if mode in ("aim", "settle"):
            s.set(48, 16 + dy, GUNE)                              # tip kisses y=16
            s.set(49, 16 + dy, GUNE)
        return
    grip_dy = 3 if mode == "raise" else 0
    s.ball(53, 31 + dy + grip_dy, 2.9, 2.5, WHITE, wrap=0.14)     # gripping paw


def cat_up(s, bobY=0, liftL=0, liftR=0, swing=0, tail_sway=0, gun=None):
    p = RIG.pose(coat=(0, bobY), shL=(0, bobY), shR=(0, bobY),
                 handL=(0, bobY), handR=(0, bobY))
    if gun is not None:
        gun_up(s, bobY, gun, stage="back")                        # barrel behind him
    legs_down(s, p, liftL, liftR, heels=True)
    coat_down(s, bobY, back=True)
    if gun is None:
        arms_down(s, p, swing, -swing)
    else:
        # left sleeve hangs; right arm reaches up toward the grip
        sx, sy = p["shL"]
        hxx, hyy = p["handL"]
        s.capsule(sx, sy, hxx, hyy, 3.6, 3.0, COATR)
        s.rect(hxx - 3, hyy - 1, hxx + 3, hyy, COATR[3])
        s.ball(hxx, hyy + 2.6, 3.2, 2.7, WHITE, power=2.2, wrap=0.14, curve=0.12)
        s.capsule(60, 47 + bobY, 54, 34 + bobY, 3.3, 2.8, COATR, sh=0.10)
    tail_up(s, tail_sway)
    head_up(s, bobY)
    if gun is not None:
        gun_up(s, bobY, gun, stage="front")                       # paw beside the ear
    finish(s)


# ---- side view (faces RIGHT) ----------------------------------------------------------

def head_side(s, dx=0, dy=0, eyes="open", ears="up"):
    hx, hy = 46 + dx, 36 + dy
    if ears == "up":
        s.tri((hx - 5, hy - 21), hy - 7, hx - 13, hx + 3, FUR)
        s.tri((hx - 5, hy - 18), hy - 9, hx - 9, hx, EARIN)
        s.tri((hx + 9, hy - 19), hy - 7, hx + 3, hx + 15, FUR, sh=0.30)   # far ear
    else:                                                          # swept back
        s.tri((hx - 18, hy - 9), hy - 2, hx - 14, hx - 2, FUR)
    s.ball(hx, hy, 12.4, 10.2, FUR, power=2.4, wrap=0.34, curve=0.30)     # skull
    s.ball(hx + 12, hy + 5, 6.4, 5.2, FUR, power=2.0, wrap=0.30)          # snout mass
    s.ball(hx + 13, hy + 6.5, 5.4, 4.0, WHITE, power=2.0, wrap=0.14, curve=0.12)
    s.rect(hx + 16, hy + 2, hx + 18, hy + 3, NOSE)
    s.set(hx + 16, hy + 2, (52, 42, 48, 255))
    s.line([(hx + 15, hy + 8), (hx + 14, hy + 9), (hx + 12, hy + 10)], MOUTH)
    s.set(hx + 8, hy + 4, WHISKD)
    s.set(hx + 6, hy + 7, WHISKD)
    if eyes == "open":
        _eye(s, hx + 4, hy - 6, 3)
    elif eyes == "closed":
        s.line([(hx + 4, hy - 3), (hx + 5, hy - 4), (hx + 6, hy - 5),
                (hx + 7, hy - 4), (hx + 8, hy - 3)], LID)
    elif eyes == "wince":                                          # squeezed shut >
        s.line([(hx + 4, hy - 6), (hx + 5, hy - 5)], LID)
        s.set(hx + 6, hy - 4, LID)
        s.line([(hx + 4, hy - 2), (hx + 5, hy - 3)], LID)
        s.set(hx + 9, hy - 8, FUR[3])                              # knit brow
    s.rect(hx - 12, hy - 11, hx + 13, hy - 10, GOGRIM[2])          # strap
    s.ball(hx + 6, hy - 13.5, 4.6, 3.6, GOGRIM, power=2.0)
    s.ball(hx + 6, hy - 13.5, 2.7, 2.0, GOGLEN, power=2.0)
    s.set(hx + 5, hy - 14, (252, 240, 214, 255))
    s.set(hx + 6, hy - 14, (252, 240, 214, 255))


def whiskers_side(s, dx=0, dy=0):
    for pts in (((65, 37), (67, 37), (69, 38), (71, 39)),
                ((65, 43), (67, 43), (69, 44))):
        for (x, y) in pts:
            s.set(x + dx, y + dy, WHISK)


def coat_side(s, dy=0, lean=0):
    """Coat in profile: straight front edge, back hem trailing, hem band. The
    lean tips the shoulders back further than the hem (recoil)."""
    top, hem = 44 + dy, 65 + dy
    h = hem - top
    for y in range(top, hem + 3):
        vy = min(1.0, (y - top) / h)
        x_off = -lean + int(round(vy * lean * 0.5))
        x0 = int(round(34 - vy * 5)) + x_off
        x1 = 58 + x_off
        if y > hem + (2 if vy > 0.5 else 0):
            continue
        for x in range(x0, x1 + 1):
            hx = (x - x0) / max(1, x1 - x0)
            t = 0.36 + 0.20 * hx
            if x >= x1 - 2:
                t += 0.26
            elif x <= x0 + 1:
                t -= 0.10
            if abs(x - (x0 + 7)) < 1.5:
                t += 0.18                                          # trailing fold
            if y >= hem:
                t += 0.30
            s.set(x, y, s.tone(COATR, t, x, y))
    for y in range(top + 4, hem + 1):                              # coat front edge
        s.set(58 - lean + int(round(min(1.0, (y - top) / h) * lean * 0.5)) - 2, y, COATR[3])


def tail_side(s, p, dy=0, raised=False):
    tx, ty = p["tail"]
    if raised:
        s.capsule(tx, ty, tx - 4, ty - 9, 3.2, 2.7, FUR, sh=0.10)
        s.capsule(tx - 4, ty - 9, tx - 3, ty - 17 + dy, 2.7, 2.2, FUR, sh=0.13)
        s.set(tx - 4, ty - 19 + dy, FUR[0])
        s.set(tx - 3, ty - 19 + dy, FUR[0])
    else:
        s.capsule(tx, ty, tx - 6, ty - 3, 3.2, 2.7, FUR, sh=0.10)
        s.capsule(tx - 6, ty - 3, tx - 11, ty - 7 + dy, 2.7, 2.2, FUR, sh=0.13)
        s.set(tx - 13, ty - 8 + dy, FUR[0])
        s.set(tx - 12, ty - 9 + dy, FUR[0])


def gun_side(s, dy=0, mode="aim", lean=0):
    """One-arm hold, barrel EAST; leveled tip fills (80, 47..48)."""
    if mode == "raise":                                            # barrel angled up
        s.capsule(46 - lean, 45 + dy, 55 - lean, 46 + dy, 3.3, 2.9, COATR)
        s.ball(57 - lean, 46 + dy, 3.0, 2.7, WHITE, wrap=0.14)
        s.capsule(58 - lean, 47 + dy, 64 - lean, 42 + dy, 3.0, 2.7, GUNPR)
        s.capsule(64 - lean, 42 + dy, 69 - lean, 38 + dy, 2.3, 2.1, GUNPR, sh=0.06)
        s.blob(71 - lean, 36.5 + dy, 2.3, 2.0, GUNE)
        s.set(71 - lean, 36 + dy, (240, 255, 240, 255))
        return
    k = 5 if mode == "recoil" else 0                               # arm shoved back
    r = 4 if mode == "recoil" else 0                               # barrel kicked up
    s.capsule(46 - k, 45 + dy, 56 - k, 46.5 + dy - r * 0.4, 3.3, 2.9, COATR)
    s.ball(58 - k, 47 + dy - r * 0.6, 3.0, 2.7, WHITE, wrap=0.14)
    s.capsule(59 - k, 47.5 + dy - r * 0.7, 68 - k, 47.5 + dy - r, 3.1, 2.9, GUNPR)
    s.capsule(63 - k, 50 + dy - r, 62 - k, 53 + dy - r, 1.9, 1.7, GUNR, sh=0.1)  # grip
    s.capsule(68 - k, 47.5 + dy - r, 76 - k, 47.5 + dy - r, 2.3, 2.1, GUNPR, sh=0.06)
    s.rect(64 - k, 45 + dy - r, 69 - k, 45 + dy - r, GUNPR[0])     # top catch
    s.blob(78.5 - k, 47.5 + dy - r, 2.4, 2.2, GUNE)                # emitter
    s.set(78 - k, 47 + dy - r, (240, 255, 240, 255))
    if mode != "recoil":
        s.set(80, 47 + dy, GUNE)                                   # tip kisses x=80
        s.set(80, 48 + dy, GUNE)


def cat_side(s, bobY=0, fA=(0, 0), fB=(0, 0), arm_dx=0, tail_dy=0,
             tail_raised=False, eyes="open", ears="up", gun=None):
    lean = 4 if gun == "recoil" else 0
    p = RIG_S.pose(skull=(-lean, bobY), coat=(0, bobY), tail=(0, bobY),
                   sh=(0, bobY), hand=(arm_dx, bobY),
                   footF=(fA[0], -fA[1]), footB=(fB[0], -fB[1]))
    tail_side(s, p, tail_dy, tail_raised or gun == "recoil")
    if gun == "recoil":
        p["footF"] = (p["footF"][0] + 7, p["footF"][1])
        p["footB"] = (p["footB"][0] + 3, p["footB"][1])
    for (hip, foot, sh) in (("hipB", "footB", 0.16), ("hipF", "footF", 0.0)):
        hx, hy = p[hip]
        fx, fy = p[foot]
        s.capsule(hx, hy + bobY, fx, fy - 3, 3.9, 3.0, PANTR, sh=sh)
        s.ball(fx + 1, fy + 0.6, 4.0, 2.9, WHITE, power=2.2, sh=sh * 0.4,
               wrap=0.14, curve=0.12)
    coat_side(s, bobY, lean)
    if gun is None:
        sx, sy = p["sh"]
        hxx, hyy = p["hand"]
        s.capsule(sx, sy, hxx, hyy, 3.5, 3.0, COATR, sh=0.10)
        s.rect(hxx - 3, hyy - 1, hxx + 3, hyy, COATR[3])           # cuff
        s.ball(hxx, hyy + 2.6, 3.4, 2.8, WHITE, power=2.2, wrap=0.14, curve=0.12)
    else:
        gun_side(s, bobY, gun, lean)
    head_side(s, -lean, bobY, eyes, ears)
    finish(s)
    whiskers_side(s, -lean, bobY)


# ---- build the sheet -------------------------------------------------------------------
cells = [[new() for _ in range(COLS)] for _ in range(ROWS)]

# walk down/up: f0 planted neutral (idle_down/up reuse it), then alternating
# steps with the body rising through the passing frames.
walk_bob   = [0, -1, -2, 0, -1, -2]
walk_liftl = [0, 5, 2, 0, 0, 0]
walk_liftr = [0, 0, 0, 0, 5, 2]
walk_swing = [0, 2, 1, 0, -2, -1]
walk_tail  = [0, 1, 2, 3, 2, 1]
for i in range(6):
    cat_down(cells[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
             walk_swing[i], walk_tail[i])
    cat_up(cells[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
           walk_swing[i], walk_tail[i])

# walk side: real stride — each foot plants forward, travels back under the
# body, then lifts and swings forward; f0 is the near-planted contact pose.
side_fA   = [(4, 0), (2, 0), (-2, 0), (-4, 1), (-1, 4), (3, 2)]
side_fB   = [(-4, 1), (-1, 4), (3, 2), (4, 0), (2, 0), (-2, 0)]
side_bob  = [0, 1, -1, 0, 1, -1]
side_arm  = [-4, -2, 2, 4, 2, -2]
side_tail = [0, -1, -2, 0, 1, 2]
for i in range(6):
    cat_side(cells[2][i], side_bob[i], side_fA[i], side_fB[i],
             side_arm[i], side_tail[i])

# shoot rows: raise, aim (bolt fires here — muzzle tip on contract), recoil
# (the shot KICKS: body shoved off the muzzle, ears pinned, wince), settle.
for i, g in enumerate(("raise", "aim", "recoil", "settle")):
    rc = g == "recoil"
    gd = "aim" if g == "settle" else g
    cat_down(cells[3][i], bobY=(-3 if rc else 0), gun=gd, spread=(2 if rc else 0),
             eyes=("wince" if rc else "open"), ears=("flat" if rc else "up"))
    cat_up(cells[4][i], bobY=(1 if rc else 0), gun=("settle" if g == "settle" else g))
    cat_side(cells[5][i], bobY=(-1 if rc else 0), gun=gd,
             eyes=("wince" if rc else "open"), ears=("back" if rc else "up"))

# row 6: hurt x2, idle-down blink, idle-side tail-flick, happy, sad
cat_down(cells[6][0], eyes="hurt", ears="flat", head_dx=-2, tail_sway=3)
cat_down(cells[6][1], eyes="hurt", ears="flat", head_dx=2, tail_sway=-1)
cat_down(cells[6][2], eyes="closed")                    # matches walk_down f0
cat_side(cells[6][3], 0, side_fA[0], side_fB[0], side_arm[0],
         tail_raised=True)                              # matches walk_side f0
cat_down(cells[6][4], eyes="happy", tail_sway=3)        # his sweet face
cat_down(cells[6][5], eyes="sad", ears="droop", tail_droop=1)   # heartbroken

write_cells(os.path.join(HERE, "basil_gen.png"), cells, CELL)
