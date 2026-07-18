#!/usr/bin/env python3
"""Basil, the science cat — sprite sheet on the _sprites.py kit, at TRUE SNES
density (the CT-chunk restart): 48x48 cells, ~33px figure, flat 4-tone shading
with hard band edges (Sprite jitter=0), every pixel deliberate.

Writes assets/basil_gen.png (288x432, 48x48 cells, 6x9) matching
entities/player/player_frames.tres (FROZEN region contract — rows only ever
APPEND, never reorder or widen):

  row0 walk_down(6)   row1 walk_up(6)   row2 walk_side(6, faces RIGHT — player.gd
                                              sets flip_h only when facing LEFT)
  row3 shoot_down(4)  row4 shoot_up(4)  row5 shoot_side(4)
  row6 hurt(2) + idle_down blink + idle_side tail-flick + happy + sad
  row7 reload(4): he tips a beaker of glow-juice into the gun's open port
  row8 (2026-07-17, the prologue staging pass): look_watch (wrist raised to
       Kitty's watch — every call beat plays this instead of a floating fx) +
       sit (side, the bluff-edge / clinic-steps pose) + bow_head (the slump
       past sad) + knapsack stand + knapsack trudge x2 (the leaving)

Art contracts consumed by code: feet baseline y=44 (_core.ZONE_FEET); origin
(24,24); in the leveled shoot frames the gun muzzle TIP sits exactly 16px from
the cell center along the facing (player.gd muzzle_offset spawns the bolt and
flash there); idle_down/idle_side alternate walk f0 with the blink/tail-flick
cells, so walk f0 is a planted neutral pose the extras redraw exactly.

Character (docs/DESIGN.md): jet-black tuxedo cat — narrow white blaze into a
plump muzzle, white paws/chest, close-set yellow eyes, black nose, whiskers
breaking the silhouette (drawn post-outline), aviator goggles up on the head,
straight-cut lab coat worn LONG (hem y=35 — only paw stubs show, so the walk
reads as feet peeking from under the hem, CT-Lucca style), laser gun (purple
body, green emitter). CT field-sprite proportions: big head over a squat body,
like the Frog sheet; the coat shades as big flat fields with ONE hard shade
band, never gradient mush.

Re-run: python3 assets/_gen_basil_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import write_cells, ZONE_CELL, ZONE_FEET
from _sprites import Sprite, Rig
from _palette import BASIL, ramp

CELL, COLS, ROWS = ZONE_CELL, 6, 9
FEET = ZONE_FEET          # 44 — bottom row of the paw FILL (outline sits at 45)
CX = 24
HEM = 40                  # near-floor lab-coat hem — only paw TIPS peek below it,
                          # so the walk reads as hem sway + paws tucking under

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

# purple laser-gun body ramp derived from the GUNP accent (4-tone)
GUNPR   = ramp(GUNP, "violet", 4)
OUT_GUN = (40, 22, 60, 255)
# local expression accents (single-use, kept out of the shared palette)
LID    = (188, 158, 66, 255)      # closed-eye stroke
BLUSH  = (238, 160, 158, 255)
TEAR   = (170, 214, 250, 255)
MAW    = (96, 54, 60, 255)
TONGUE = (226, 120, 128, 255)
GLASS  = (214, 232, 244, 255)     # reload beaker
GLASSD = (152, 178, 204, 255)
# row-8 prop accents: Kitty's wrist-watch (matches the fx-sheet fx_watch
# palette) and the leaving bindle
WCASE  = (240, 188, 98, 255)      # brass watch case
WFACE  = (150, 246, 190, 255)     # mint ward-glass face
WSTRAP = (58, 134, 140, 255)      # teal strap
STICKR = ramp((146, 94, 62), "violet", 4)     # bindle stick
SACKR  = ramp((196, 140, 90), "violet", 4)    # burlap bindle sack

OUTS = dict(BASIL["OUTS"])
for _c in GUNPR:
    OUTS[_c] = OUT_GUN
OUT_FB = BASIL["OUT_FALLBACK"]
RAMPS = [FUR, WHITE, COATR, PANTR, GOGRIM, GOGLEN, GUNR, GUNPR]


def new():
    return Sprite(CELL, grain=1, salt=5, jitter=0.0)   # flat CT bands


def finish(s):
    s.despeckle(passes=1)
    s.outline(OUTS, OUT_FB)


# ---- the body rig (down/up views share it; side view has its own) -----------------
RIG = Rig(
    head=(24, 18),
    coat=(24, 22),
    hipL=(21, 33), hipR=(27, 33),
    footL=(21, 42), footR=(27, 42),
    shL=(18, 23), shR=(30, 23),
    handL=(16, 29), handR=(32, 29),
    tail=(30, 33),
)

RIG_S = Rig(               # side view, facing RIGHT
    skull=(23, 18),
    coat=(23, 22),
    hipF=(25, 33), hipB=(20, 33),
    footF=(25, 42), footB=(20, 42),
    sh=(23, 23), hand=(22, 29),
    tail=(16, 30),
)


# ---- down-view parts ----------------------------------------------------------------

def head_down(s, dx=0, dy=0, eyes="open", ears="up"):
    hx, hy = CX + dx, 18 + dy
    # ears first (skull overlaps their base): close-set, sitting ON the dome.
    if ears == "up":
        s.tri((hx - 4, hy - 10), hy - 4, hx - 7, hx - 1, FUR)
        s.tri((hx + 4, hy - 10), hy - 4, hx + 1, hx + 7, FUR, sh=0.15)
        s.tri((hx - 4, hy - 8), hy - 5, hx - 5, hx - 3, EARIN)
        s.tri((hx + 4, hy - 8), hy - 5, hx + 3, hx + 5, EARIN_D)
    elif ears == "droop":                          # slouched out + down (sad)
        s.tri((hx - 6, hy - 4), hy, hx - 8, hx - 1, FUR)
        s.tri((hx + 6, hy - 4), hy, hx + 1, hx + 8, FUR, sh=0.15)
    else:                                          # pinned flat (hurt / recoil)
        s.tri((hx - 8, hy - 3), hy, hx - 6, hx - 1, FUR)
        s.tri((hx + 8, hy - 3), hy, hx + 1, hx + 6, FUR, sh=0.15)
    # skull dome + plump white muzzle + narrow blaze between the eyes
    s.ball(hx, hy, 7.2, 6.0, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.ball(hx, hy + 4, 4.6, 2.9, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.tri((hx, hy - 4), hy + 1, hx - 1, hx + 1, WHITE)
    # nose
    s.rect(hx - 1, hy + 2, hx, hy + 2, NOSE)
    # mouths
    if eyes == "hurt":
        s.rect(hx - 1, hy + 4, hx, hy + 6, MOUTH)               # open wail
        s.set(hx, hy + 5, MAW)
    elif eyes == "wince":
        s.rect(hx - 2, hy + 4, hx + 1, hy + 5, MOUTH)           # gritted teeth
        s.set(hx, hy + 4, WHITE[0])
    elif eyes == "happy":
        s.rect(hx - 2, hy + 4, hx + 1, hy + 6, MAW)             # open grin
        s.rect(hx - 1, hy + 6, hx, hy + 6, TONGUE)
        s.set(hx - 6, hy + 3, BLUSH)
        s.set(hx + 5, hy + 3, BLUSH)
    elif eyes == "sad":
        s.line([(hx - 2, hy + 5), (hx - 1, hy + 4), (hx, hy + 4),
                (hx + 1, hy + 5)], MOUTH)                       # wobble frown
    else:
        s.line([(hx - 1, hy + 4), (hx, hy + 4)], MOUTH)
    # eyes — close-set, stern default
    if eyes == "open":
        _eye(s, hx - 5, hy - 2, 0)
        _eye(s, hx + 3, hy - 2, 2)
    elif eyes in ("closed", "happy"):                            # sweet ^ ^
        for ex in (hx - 5, hx + 3):
            s.line([(ex, hy - 1), (ex + 1, hy - 2), (ex + 2, hy - 1)], LID)
    elif eyes == "sad":                                          # teary, downcast
        for ex in (hx - 5, hx + 3):
            s.rect(ex, hy - 2, ex + 2, hy, EYE_Y)
            s.rect(ex, hy - 2, ex + 2, hy - 2, FUR[2])           # heavy upper lid
            s.set(ex + 1, hy, PUPIL)
            s.set(ex + 2, hy - 1, GLINT)                         # shine = teary
        s.set(hx - 5, hy + 2, TEAR)                              # a welling tear
    else:                                                        # hurt / wince >_<
        for ex in (hx - 5, hx + 3):
            s.set(ex, hy - 2, LID)
            s.set(ex + 1, hy - 1, LID)
            s.set(ex, hy, LID)
    goggles_down(s, hx, hy)


def goggles_down(s, hx, hy):
    """Aviator goggles parked on the forehead so they READ as goggles: a strap
    across the dome under two big rimmed round lenses of amber glass (glint in
    each), joined by a bridge pixel. Lenses bump past the dome silhouette."""
    s.rect(hx - 7, hy - 4, hx + 7, hy - 4, GOGRIM[2])             # strap
    for gx, rim_sh in ((hx - 3, 0.0), (hx + 3, 0.18)):
        s.ball(gx, hy - 5.5, 2.4, 1.9, GOGRIM, power=2.0, sh=rim_sh)
        s.blob(gx, hy - 5.5, 1.4, 1.0, GOGLEN[1])                 # amber glass
        s.set(gx - 1, hy - 6, GOGLEN[0])                          # glint
    s.set(hx, hy - 5, GOGRIM[1])                                  # bridge


def _eye(s, ex, ey, brow_out):
    """3x3 stern yellow eye: light top row, 1x2 pupil, dark lid pixel angling
    in at the outer top corner (the scowl — no room for a brow above, the
    goggle strap lives there)."""
    s.rect(ex, ey, ex + 2, ey + 2, EYE_Y)
    s.rect(ex, ey, ex + 2, ey, EYE_YL)
    s.rect(ex + 1, ey + 1, ex + 1, ey + 2, PUPIL)
    s.set(ex + brow_out, ey, FUR[3])


def whiskers_down(s, dx=0, dy=0):
    """Short strokes off the cheeks at muzzle height, past the outline."""
    for pts in (((15, 21), (14, 21)),
                ((15, 23), (14, 24)),
                ((33, 21), (34, 21)),
                ((33, 23), (34, 24))):
        for (x, y) in pts:
            s.set(x + dx, y + dy, WHISK)


def legs_down(s, p, liftL=0, liftR=0, spread=0, heels=False):
    """Short trouser stubs + chunky white paws — the long coat hides the leg
    tops, so a step reads as a paw peeking under the hem. spread braces the
    stance (recoil)."""
    for (hip, foot, lift, sp, sh) in (("hipL", "footL", liftL, -spread, 0.0),
                                      ("hipR", "footR", liftR, spread, 0.10)):
        hx, hy = p[hip]
        fx, fy = p[foot]
        hx += sp
        fx += sp
        fy -= lift
        s.capsule(hx, hy, fx, fy - 2, 2.2, 1.7, PANTR, sh=sh)
        s.ball(fx, fy + 0.6, 2.2, 1.7, WHITE, power=2.2, sh=sh * 0.5,
               wrap=0.10, curve=0.10)


def coat_down(s, dy=0, back=False, sway=0):
    """Straight-cut lab coat worn near-FLOOR (hem y=HEM). Flat CT bands,
    hand-set: a lit field left of the placket, mid field right, a hard 1px
    shade band at screen-right, a hem band with dark turn-under — no gradient,
    no folds. `sway` drags just the bottom QUARTER of the skirt sideways 1px
    so the walk reads as the hem trailing the step — any deeper and the whole
    coat wags like hips. Front adds collar ticks over the chest tuft, hip
    pockets, the purple pen; back adds collar band, belt and vent seam."""
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
                c = COATR[3] if x >= x1 - 1 else COATR[2]
            elif x >= x1 - 1:                      # shade band, screen-right
                c = COATR[2]
            elif x < CX + off(y):                  # lit field
                c = COATR[0]
            else:                                  # mid field
                c = COATR[1]
            s.set(x, y, c)
    s.rect(CX - 5 + sway, hem + 1, CX + 5 + sway, hem + 1, COATR[3])  # turn-under
    if back:
        s.rect(CX - 5, top, CX + 5, top + 1, COATR[1])            # collar band
        s.rect(CX - 4, top + 6, CX + 4, top + 6, COATR[2])        # back belt
        for y in range(top + 8, hem - 1):                         # vent seam
            s.set(CX + off(y), y, COATR[2])
        return
    for y in range(top + 4, hem - 1):                             # center placket
        s.set(CX + off(y), y, COATR[3])                           # (bends w/ sway)
    s.tri((CX, top), top + 3, CX - 2, CX + 2, WHITE)              # chest tuft
    s.set(CX - 2, top + 2, COATR[2])                              # collar ticks
    s.set(CX + 2, top + 2, COATR[2])
    s.rect(CX - 6, top + 12, CX - 3, top + 12, COATR[2])          # hip pockets
    s.rect(CX + 3, top + 12, CX + 6, top + 12, COATR[3])          # (above the sway)
    s.rect(CX - 4, top + 3, CX - 4, top + 4, GUNP)                # breast pen


def arms_down(s, p, dl=0, dr=0):
    """Hanging coat sleeves + white paws; dl/dr swing them. Sleeves shade a
    band darker than the coat body so they separate from the flat fields."""
    for (sh_a, hand, d, sh) in (("shL", "handL", dl, 0.18), ("shR", "handR", dr, 0.32)):
        sx, sy = p[sh_a]
        hx, hy = p[hand]
        hy += d
        s.capsule(sx, sy, hx, hy, 1.9, 1.6, COATR, sh=sh)
        s.ball(hx, hy + 1.6, 1.8, 1.5, WHITE, power=2.2, sh=sh * 0.5,
               wrap=0.10, curve=0.10)


def tail_down(s, p, sway=0, droop=0):
    """Tail curling out right of the hem; sway shifts the tip, droop sinks it."""
    tx, ty = p["tail"]
    if droop:
        s.capsule(tx, ty + 1, tx + 3, ty + 3, 1.7, 1.4, FUR, sh=0.08)
        s.capsule(tx + 3, ty + 3, tx + 5, ty + 2, 1.4, 1.1, FUR, sh=0.12)
        s.set(tx + 6, ty + 2, FUR[0])
        return
    s.capsule(tx, ty + 1, tx + 3, ty - 3, 1.7, 1.4, FUR, sh=0.08)
    s.capsule(tx + 3, ty - 3, tx + 4 + sway, ty - 7, 1.4, 1.1, FUR, sh=0.12)
    s.set(tx + 3 + sway, ty - 8, FUR[0])                          # tip catchlight
    s.set(tx + 4 + sway, ty - 8, FUR[0])


def gun_down(s, dy=0, mode="aim"):
    """Two-paw grip, barrel pointing SOUTH. In leveled frames the emitter tip
    fills (24, 40) — cell center + muzzle_offset(16) toward the facing."""
    k = -2 if mode == "recoil" else 0
    if mode == "raise":                                           # gun still at the chest
        s.capsule(18, 23 + dy, 21, 27 + dy, 1.9, 1.6, COATR)
        s.capsule(30, 23 + dy, 27, 27 + dy, 1.9, 1.6, COATR, sh=0.12)
        s.ball(22.5, 29 + dy, 1.7, 1.5, WHITE, wrap=0.10)
        s.ball(25.5, 29 + dy, 1.7, 1.5, WHITE, wrap=0.10)
        s.capsule(22, 30 + dy, 26, 30 + dy, 1.6, 1.6, GUNPR)
        s.capsule(24, 31 + dy, 24, 34 + dy, 1.3, 1.2, GUNPR, sh=0.08)
        s.rect(24, 35 + dy, 24, 35 + dy, GUNE)
        return
    s.capsule(18, 23 + dy, 21, 28 + dy, 1.9, 1.6, COATR)          # upper arms in
    s.capsule(30, 23 + dy, 27, 28 + dy, 1.9, 1.6, COATR, sh=0.12)
    s.capsule(21, 28 + dy, 22.5, 30 + dy + k, 1.7, 1.5, COATR)
    s.capsule(27, 28 + dy, 25.5, 30 + dy + k, 1.7, 1.5, COATR, sh=0.12)
    s.ball(22.5, 31.5 + dy + k, 1.7, 1.5, WHITE, wrap=0.10)       # gripping paws
    s.ball(25.5, 31.5 + dy + k, 1.7, 1.5, WHITE, wrap=0.10)
    s.capsule(22, 32.5 + dy + k, 26, 32.5 + dy + k, 1.6, 1.6, GUNPR)   # receiver
    s.capsule(24, 34 + dy + k, 24, 38 + dy + k, 1.4, 1.2, GUNPR, sh=0.06)  # barrel
    s.set(23, 35 + dy + k, GUNR[1])                               # side rail
    s.blob(24, 39 + dy + k, 1.5, 1.1, GUNE)                       # emitter tip
    s.set(24, 39 + dy + k, (240, 255, 240, 255))
    if mode != "recoil":
        s.set(24, 40 + dy, GUNE)                                  # tip kisses y=40
        s.set(23, 40 + dy, GUNE)


# ---- full down/up poses ---------------------------------------------------------------

def cat_down(s, bobY=0, liftL=0, liftR=0, swing=0, tail_sway=0, tail_droop=0,
             eyes="open", ears="up", head_dx=0, gun=None, spread=0, coat_sway=0):
    p = RIG.pose(head=(head_dx, bobY), coat=(0, bobY), tail=(tail_sway // 2, bobY),
                 shL=(0, bobY), shR=(0, bobY), handL=(0, bobY), handR=(0, bobY))
    tail_down(s, p, tail_sway, tail_droop)
    legs_down(s, p, liftL, liftR, spread)
    coat_down(s, bobY, sway=coat_sway)
    if gun is None:
        arms_down(s, p, swing, -swing)
    else:
        gun_down(s, bobY, gun)
    head_down(s, head_dx, bobY, eyes, ears)
    finish(s)
    whiskers_down(s, head_dx, bobY)


def head_up(s, dy=0):
    """Back of the head: dome, close-set ear backs, goggle strap + buckle and
    the lens cups peeking over the crown, neck part."""
    hy = 18 + dy
    s.tri((CX - 4, hy - 10), hy - 4, CX - 7, CX - 1, FUR)
    s.tri((CX + 4, hy - 10), hy - 4, CX + 1, CX + 7, FUR, sh=0.15)
    s.tri((CX - 4, hy - 8), hy - 5, CX - 6, CX - 2, FUR, sh=0.38)
    s.tri((CX + 4, hy - 8), hy - 5, CX + 2, CX + 6, FUR, sh=0.46)
    s.ball(CX, hy, 7.2, 6.0, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(CX - 6, hy - 4, CX + 6, hy - 4, GOGRIM[2])             # strap
    s.rect(CX - 1, hy - 4, CX + 1, hy - 4, GOGRIM[1])             # buckle
    s.ball(CX - 3, hy - 5.5, 2.0, 1.4, GOGRIM, power=2.0)         # cup backs
    s.ball(CX + 3, hy - 5.5, 2.0, 1.4, GOGRIM, power=2.0, sh=0.15)  # over the dome
    s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
            (CX + 1, hy + 6), (CX + 2, hy + 5)], FUR[3])


def tail_up(s, sway=0):
    """Raised swish, seen from behind on his right."""
    s.capsule(29, 31, 32, 27, 1.7, 1.4, FUR, sh=0.10)
    s.capsule(32, 27, 32 + sway, 22, 1.4, 1.1, FUR, sh=0.14)
    s.set(32 + sway, 21, FUR[0])


def gun_up(s, dy=0, mode="aim", stage="back"):
    """One-arm skyward aim seen from behind: the barrel rises past the head
    (the `back` stage draws it BEFORE the body), and the `front` stage adds the
    raised gripping paw beside the ear. Leveled tip fills (23..24, 8)."""
    top = {"raise": 13, "recoil": 11}.get(mode, 10)
    if stage == "back":
        s.capsule(24.5, 22 + dy, 24.5, top + 2 + dy, 1.5, 1.3, GUNPR, sh=0.10)
        s.capsule(24.5, top + 2 + dy, 24.5, top + dy, 1.2, 1.1, GUNPR, sh=0.04)
        s.blob(24.5, top - 1 + dy, 1.3, 1.0, GUNE)
        s.set(24, top - 1 + dy, (240, 255, 240, 255))
        return
    grip_dy = 2 if mode == "raise" else 0
    s.ball(27, 15 + dy + grip_dy, 1.6, 1.4, WHITE, wrap=0.10)     # gripping paw


def cat_up(s, bobY=0, liftL=0, liftR=0, swing=0, tail_sway=0, gun=None,
           coat_sway=0):
    p = RIG.pose(coat=(0, bobY), shL=(0, bobY), shR=(0, bobY),
                 handL=(0, bobY), handR=(0, bobY))
    if gun is not None:
        gun_up(s, bobY, gun, stage="back")                        # barrel behind him
    legs_down(s, p, liftL, liftR, heels=True)
    coat_down(s, bobY, back=True, sway=coat_sway)
    if gun is None:
        arms_down(s, p, swing, -swing)
    else:
        # left sleeve hangs; right arm reaches up toward the grip
        sx, sy = p["shL"]
        hxx, hyy = p["handL"]
        s.capsule(sx, sy, hxx, hyy, 1.9, 1.6, COATR, sh=0.18)
        s.ball(hxx, hyy + 1.6, 1.8, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
        s.capsule(30, 23 + bobY, 27, 17 + bobY, 1.8, 1.5, COATR, sh=0.10)
    tail_up(s, tail_sway)
    head_up(s, bobY)
    if gun is not None:
        gun_up(s, bobY, gun, stage="front")                       # paw beside the ear
    finish(s)
    if gun in ("aim", "settle"):
        s.set(23, 8, GUNE)          # tip kisses y=8 — the muzzle contract; set
        s.set(24, 8, GUNE)          # post-outline so despeckle can't eat it


# ---- side view (faces RIGHT) ----------------------------------------------------------

def head_side(s, dx=0, dy=0, eyes="open", ears="up"):
    hx, hy = 23 + dx, 18 + dy
    if ears == "up":
        s.tri((hx + 3, hy - 10), hy - 5, hx + 1, hx + 5, FUR, sh=0.30)  # far ear
        s.tri((hx - 1, hy - 11), hy - 5, hx - 3, hx + 1, FUR)     # near ear, tall
        s.tri((hx - 1, hy - 9), hy - 6, hx - 2, hx, EARIN)
    else:                                                          # swept back
        s.tri((hx - 8, hy - 5), hy - 1, hx - 6, hx - 1, FUR)
    # SHORT-nosed cat with big cheeks: no protruding snout — a plump white
    # cheek mass sits flush against the skull front, the little nose rides
    # high on the flat face, jowl rounds the jaw.
    s.ball(hx, hy, 6.8, 5.6, FUR, power=2.4, wrap=0.34, curve=0.30)      # skull
    s.ball(hx + 4, hy + 2.5, 3.2, 2.7, FUR, power=2.0, wrap=0.30)        # cheek mass
    s.ball(hx + 4.5, hy + 3.2, 3.2, 2.5, WHITE, power=2.0, wrap=0.10, curve=0.10)
    s.rect(hx + 6, hy + 2, hx + 7, hy + 2, NOSE)                         # stub nose
    s.line([(hx + 5, hy + 4), (hx + 6, hy + 4)], MOUTH)
    if eyes == "open":
        _eye(s, hx + 2, hy - 3, 2)
    elif eyes == "closed":
        s.line([(hx + 2, hy - 2), (hx + 3, hy - 3), (hx + 4, hy - 2)], LID)
    elif eyes == "wince":                                          # squeezed shut >
        s.line([(hx + 2, hy - 3), (hx + 3, hy - 2)], LID)
        s.line([(hx + 2, hy - 1), (hx + 3, hy - 2)], LID)
        s.set(hx + 5, hy - 4, FUR[3])                              # knit brow
    # goggles in profile: one big rimmed lens forward, strap running back
    s.rect(hx - 6, hy - 5, hx + 3, hy - 5, GOGRIM[2])              # strap
    s.set(hx - 2, hy - 6, GOGRIM[1])                               # far cup edge
    s.ball(hx + 3, hy - 6.5, 2.3, 1.8, GOGRIM, power=2.0)
    s.blob(hx + 3, hy - 6.5, 1.3, 1.0, GOGLEN[1])                  # amber glass
    s.set(hx + 2, hy - 7, GOGLEN[0])                               # glint


def whiskers_side(s, dx=0, dy=0):
    """Short strokes off the big cheek (front fill ~x30, outline x31)."""
    for pts in (((32, 19), (33, 19), (34, 20)),
                ((32, 22), (33, 23))):
        for (x, y) in pts:
            s.set(x + dx, y + dy, WHISK)


def coat_side(s, dy=0, lean=0, sway=0):
    """Coat in profile, worn near-FLOOR: straight front edge, back hem
    trailing. Flat CT bands — lit band along the back (light upper-left =
    behind him), mid field, one crisp trailing-fold line, dark front edge,
    hem band with turn-under. `sway` drags just the bottom QUARTER of the
    skirt fore/aft 1px with the stride (any deeper wags the whole coat); the
    lean tips the shoulders back (recoil)."""
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
                c = COATR[3] if x >= x1 - 1 else COATR[2]
            elif x == x1:                          # dark front edge
                c = COATR[3] if y >= top + 2 else COATR[2]
            elif x == x1 - 1:                      # shade band inside the edge
                c = COATR[2]
            elif x == fold and y >= top + 4:       # trailing fold crease
                c = COATR[2]
            elif x <= x0 + 2:                      # lit back
                c = COATR[0]
            else:                                  # mid field
                c = COATR[1]
            s.set(x, y, c)
    x_off = -lean + int(round(lean * 0.5)) + sway
    s.rect(16 + x_off, hem + 1, 27 + x_off, hem + 1, COATR[3])     # turn-under


def tail_side(s, p, dy=0, raised=False):
    tx, ty = p["tail"]
    if raised:
        s.capsule(tx, ty, tx - 2, ty - 5, 1.7, 1.4, FUR, sh=0.10)
        s.capsule(tx - 2, ty - 5, tx - 1, ty - 9 + dy, 1.4, 1.1, FUR, sh=0.13)
        s.set(tx - 2, ty - 10 + dy, FUR[0])
    else:
        s.capsule(tx, ty, tx - 3, ty - 2, 1.7, 1.4, FUR, sh=0.10)
        s.capsule(tx - 3, ty - 2, tx - 6, ty - 4 + dy, 1.4, 1.1, FUR, sh=0.13)
        s.set(tx - 7, ty - 5 + dy, FUR[0])


def gun_side(s, dy=0, mode="aim", lean=0):
    """One-arm hold, barrel EAST; leveled tip fills (40, 23..24)."""
    if mode == "raise":                                            # barrel angled up
        s.capsule(23 - lean, 22.5 + dy, 27 - lean, 23 + dy, 1.8, 1.6, COATR)
        s.ball(28.5 - lean, 23 + dy, 1.7, 1.5, WHITE, wrap=0.10)
        s.capsule(29 - lean, 23.5 + dy, 32 - lean, 21 + dy, 1.6, 1.5, GUNPR)
        s.capsule(32 - lean, 21 + dy, 34.5 - lean, 19 + dy, 1.2, 1.1, GUNPR, sh=0.06)
        s.blob(35.5 - lean, 18.3 + dy, 1.2, 1.1, GUNE)
        s.set(35 - lean, 18 + dy, (240, 255, 240, 255))
        return
    k = 2 if mode == "recoil" else 0                               # arm shoved back
    r = 2 if mode == "recoil" else 0                               # barrel kicked up
    s.capsule(23 - k, 22.5 + dy, 28 - k, 23 + dy - r * 0.4, 1.8, 1.6, COATR)
    s.ball(29 - k, 23.5 + dy - r * 0.6, 1.7, 1.5, WHITE, wrap=0.10)
    s.capsule(29.5 - k, 24 + dy - r * 0.7, 34 - k, 24 + dy - r, 1.7, 1.6, GUNPR)
    s.capsule(31.5 - k, 25 + dy - r, 31 - k, 26.5 + dy - r, 1.1, 1.0, GUNR, sh=0.1)  # grip
    s.capsule(34 - k, 24 + dy - r, 38 - k, 24 + dy - r, 1.3, 1.2, GUNPR, sh=0.06)
    s.rect(32 - k, 22.5 + dy - r, 34 - k, 22.5 + dy - r, GUNPR[0])  # top catch
    s.blob(39 - k, 23.8 + dy - r, 1.3, 1.2, GUNE)                  # emitter
    s.set(39 - k, 23 + dy - r, (240, 255, 240, 255))
    if mode != "recoil":
        s.set(40, 23 + dy, GUNE)                                   # tip kisses x=40
        s.set(40, 24 + dy, GUNE)


def cat_side(s, bobY=0, fA=(0, 0), fB=(0, 0), arm_dx=0, tail_dy=0,
             tail_raised=False, eyes="open", ears="up", gun=None, coat_sway=0):
    lean = 2 if gun == "recoil" else 0
    p = RIG_S.pose(skull=(-lean, bobY), coat=(0, bobY), tail=(0, bobY),
                   sh=(0, bobY), hand=(arm_dx, bobY),
                   footF=(fA[0], -fA[1]), footB=(fB[0], -fB[1]))
    tail_side(s, p, tail_dy, tail_raised or gun == "recoil")
    if gun == "recoil":
        p["footF"] = (p["footF"][0] + 4, p["footF"][1])
        p["footB"] = (p["footB"][0] + 2, p["footB"][1])
    for (hip, foot, sh) in (("hipB", "footB", 0.16), ("hipF", "footF", 0.0)):
        hx, hy = p[hip]
        fx, fy = p[foot]
        s.capsule(hx, hy + bobY, fx, fy - 2, 2.1, 1.7, PANTR, sh=sh)
        s.ball(fx + 0.5, fy + 0.6, 2.2, 1.7, WHITE, power=2.2, sh=sh * 0.4,
               wrap=0.10, curve=0.10)
    coat_side(s, bobY, lean, coat_sway)
    if gun is None:
        sx, sy = p["sh"]
        hxx, hyy = p["hand"]
        s.capsule(sx, sy, hxx, hyy, 1.8, 1.6, COATR, sh=0.28)
        s.ball(hxx, hyy + 1.6, 1.8, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
    else:
        gun_side(s, bobY, gun, lean)
    head_side(s, -lean, bobY, eyes, ears)
    finish(s)
    whiskers_side(s, -lean, bobY)


# ---- reload (row 7): pouring a beaker of glow-juice into the gun ----------------------

def _flask(s, x, y, tip):
    """Tiny Erlenmeyer of glow-juice around base center (x, y). tip: 0 upright
    full, 1 tilted toward the gun, 2 pouring mouth-down, 3 upright drained."""
    if tip in (0, 3):
        s.tri((x, y - 3), y + 1, x - 2, x + 2, GLASS)             # cone body
        s.set(x + 1, y, GLASSD)                                   # glass shade
        s.set(x + 2, y + 1, GLASSD)
        if tip == 0:
            s.rect(x - 1, y, x + 1, y + 1, GUNE)                  # full
        else:
            s.set(x, y + 1, GUNE)                                 # last drop
        return
    if tip == 1:                                                  # tilted 45°
        s.line([(x + 2, y - 2), (x + 3, y - 1)], GLASSD)          # base edge
        s.rect(x + 1, y - 1, x + 2, y, GLASS)
        s.line([(x, y), (x + 1, y + 1)], GLASS)
        s.rect(x, y + 1, x + 1, y + 1, GUNE)                      # juice at mouth
        s.set(x - 1, y + 1, GLASS)                                # mouth lip
        return
    # tip == 2: mouth-down over the port, juice falling out
    s.line([(x + 1, y - 2), (x + 2, y - 2)], GLASSD)              # base up top
    s.rect(x, y - 1, x + 2, y, GLASS)
    s.rect(x, y, x + 1, y + 1, GUNE)                              # juice in the neck
    s.set(x - 1, y + 1, GLASS)                                    # mouth lip


def _reload_arm(s, phase):
    """Right arm doing the beaker work; drawn AFTER the head so the raised
    flask reads in front of his chin."""
    if phase == 0:                                                # flask out, at his side
        s.capsule(30, 23, 31, 27, 1.9, 1.6, COATR, sh=0.28)
        s.ball(31.5, 28.5, 1.7, 1.5, WHITE, wrap=0.10)
        _flask(s, 31, 26, 0)
    elif phase == 1:                                              # swung over the gun
        s.capsule(30, 23, 27.5, 25, 1.9, 1.6, COATR, sh=0.28)
        s.ball(27, 26.5, 1.7, 1.5, WHITE, wrap=0.10)
        _flask(s, 24, 26, 1)
    elif phase == 2:                                              # full pour
        s.capsule(30, 23, 27, 24.5, 1.9, 1.6, COATR, sh=0.28)
        s.ball(26.5, 26, 1.7, 1.5, WHITE, wrap=0.10)
        _flask(s, 23, 26, 2)
    else:                                                         # flask stashed, arm drops
        s.capsule(30, 23, 31.5, 28, 1.9, 1.6, COATR, sh=0.28)
        s.ball(32, 30, 1.7, 1.5, WHITE, wrap=0.10)


def _reload_fx(s, phase):
    """Loose pour/sparkle pixels, placed after the outline like whiskers."""
    if phase == 1:
        s.set(23, 28, GUNE)                                       # first drip
    elif phase == 2:
        for y in (28, 29, 30):                                    # the stream
            s.set(22, y, GUNE)
        s.set(23, 30, GUNE)                                       # splash at the port
    elif phase == 3:
        for (x, y) in ((19, 29), (27, 28), (30, 33)):             # charged sparkle
            s.set(x, y, GLINT)


def reload_down(s, phase):
    """Row-7 reload, facing camera: gun held flat at the belly in the left paw,
    port hatch open; the right paw tips a beaker of glow-juice in. Last frame
    sparkles with the sweet ^ ^ eyes."""
    p = RIG.pose()
    tail_down(s, p, (0, 1, 2, 1)[phase])
    legs_down(s, p)
    coat_down(s)
    s.capsule(18, 23, 19.5, 29, 1.9, 1.6, COATR, sh=0.18)         # left arm crosses
    s.ball(20.5, 31, 1.7, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.capsule(21.5, 32.5, 25, 32.5, 1.5, 1.5, GUNPR)              # gun at the belly
    s.capsule(25.5, 32.5, 27.5, 32.5, 1.1, 1.0, GUNPR, sh=0.06)
    s.blob(28.5, 32.5, 1.2, 1.1, GUNE)                            # emitter
    s.set(22, 31, GUNPR[3])                                       # open port hatch
    if phase == 3:
        s.set(28, 32, (240, 255, 240, 255))                       # freshly charged
    head_down(s, 0, 0, "closed" if phase == 3 else "open", "up")
    _reload_arm(s, phase)
    finish(s)
    whiskers_down(s)
    _reload_fx(s, phase)


# ---- row 8: the prologue staging poses (2026-07-17) -----------------------------------

def look_watch_down(s):
    """He raises his left forepaw and turns his muzzle to the little brass
    watch on the wrist — Kitty's watch, the shared comm gesture of every
    call beat (it replaces the old floating watch fx). Down view: right
    sleeve hangs, left sleeve folds up so the paw sits before the chin, the
    watch face drawn post-outline so despeckle can't eat it."""
    p = RIG.pose()
    tail_down(s, p, 1)
    legs_down(s, p)
    coat_down(s)
    sx, sy = p["shL"]                                 # hanging screen-left arm
    hx, hy = p["handL"]
    s.capsule(sx, sy, hx, hy, 1.9, 1.6, COATR, sh=0.18)
    s.ball(hx, hy + 1.6, 1.8, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
    # raised screen-right arm: sleeve folds up, paw before the chin
    s.capsule(31, 23, 30.5, 27, 1.9, 1.6, COATR, sh=0.32)
    s.capsule(30.5, 27, 29, 24, 1.7, 1.5, COATR, sh=0.26)
    s.ball(29, 22.5, 1.9, 1.6, WHITE, power=2.2, wrap=0.10, curve=0.10)
    head_down(s, 1, 0, "open", "up")                  # muzzle tips toward it
    finish(s)
    whiskers_down(s, 1, 0)
    s.rect(27, 26, 31, 26, WSTRAP)                    # strap across the wrist
    s.rect(28, 24, 30, 25, WCASE)                     # brass case
    s.rect(29, 24, 30, 25, WFACE)                     # mint ward-glass face
    s.set(30, 24, GLINT)                              # lit — the call is live


def sit_side(s):
    """Sitting on the ground facing RIGHT — coat pooled into a mound, knees
    up in front, paws planted, tail curled on the ground behind. The
    bluff-edge and clinic-steps pose (flip_h faces it left)."""
    s.capsule(15, 41, 12, 39, 1.6, 1.3, FUR, sh=0.10)     # curled tail
    s.set(11, 38, FUR[0])
    for y in range(30, 43):                                # pooled coat mound
        vy = (y - 30) / 12.0
        half = 5.0 + 4.0 * vy
        x0 = int(round(22 - half))
        x1 = int(round(22 + half * 0.8))
        for x in range(x0, x1 + 1):
            if y >= 41:                                    # hem on the ground
                c = COATR[3] if x >= x1 - 1 else COATR[2]
            elif x <= x0 + 2:                              # lit back band
                c = COATR[0]
            elif x >= x1 - 1:                              # shaded front edge
                c = COATR[2]
            else:
                c = COATR[1]
            s.set(x, y, c)
    s.capsule(27, 34, 28, 39, 2.0, 1.7, PANTR)             # knees up in front
    s.ball(28.5, 41.5, 2.0, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.capsule(22, 31, 27, 33, 1.8, 1.5, COATR, sh=0.26)    # arm over the knees
    s.ball(28, 34, 1.6, 1.4, WHITE, wrap=0.10)
    head_side(s, 0, 8, "open", "up")                       # head sits low
    finish(s)
    whiskers_side(s, 0, 8)


def bow_head_down(s):
    """Head BOWED — the slump past `sad`: the crown turns to the camera, no
    eyes visible, ears fallen, arms hanging heavy, tail flat. The pose that
    says the thing he can't."""
    p = RIG.pose()
    tail_down(s, p, 0, 1)                                  # drooped flat
    legs_down(s, p)
    coat_down(s)
    arms_down(s, p, 1, 1)                                  # both hang forward
    hx, hy = CX, 21                                        # dome dropped 3px
    s.tri((hx - 6, hy - 2), hy + 2, hx - 8, hx - 1, FUR)   # ears fallen wide
    s.tri((hx + 6, hy - 2), hy + 2, hx + 1, hx + 8, FUR, sh=0.15)
    s.ball(hx, hy, 7.2, 6.2, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(hx - 7, hy - 2, hx + 7, hy - 2, GOGRIM[2])      # goggles ride the
    s.ball(hx - 3, hy - 3.5, 2.4, 1.9, GOGRIM, power=2.0)  # crown-forward dome
    s.ball(hx + 3, hy - 3.5, 2.4, 1.9, GOGRIM, power=2.0, sh=0.18)
    s.ball(hx, hy + 5.4, 3.4, 1.6, WHITE, power=2.2, wrap=0.10, curve=0.10)
    finish(s)                                              # muzzle tip peeks


def knapsack_side(s, step=0):
    """The leaving: bindle stick over the shoulder, sack hanging behind,
    facing RIGHT. step 0 = planted stand; 1/2 = a weary two-frame trudge
    (tight stride, head a touch low — nothing jaunty about this walk)."""
    strides = [((2, 0), (-1, 0), 0),
               ((-3, 0), (5, 1), -1),
               ((0, 1), (2, 0), -1)]
    fA, fB, bob = strides[step]
    p = RIG_S.pose(skull=(0, bob + 1), coat=(0, bob), tail=(0, bob),
                   footF=(fA[0], -fA[1]), footB=(fB[0], -fB[1]))
    tail_side(s, p, 1)                                     # low tail
    # the sack hangs off the stick's back end, behind the shoulder
    s.ball(13, 17 + bob, 3.0, 2.6, SACKR, power=2.2, sh=0.10, wrap=0.16)
    s.set(13, 14 + bob, STICKR[3])                         # neck knot
    for (hip, foot, sh) in (("hipB", "footB", 0.16), ("hipF", "footF", 0.0)):
        hx, hy = p[hip]
        fx, fy = p[foot]
        s.capsule(hx, hy + bob, fx, fy - 2, 2.1, 1.7, PANTR, sh=sh)
        s.ball(fx + 0.5, fy + 0.6, 2.2, 1.7, WHITE, power=2.2, sh=sh * 0.4,
               wrap=0.10, curve=0.10)
    coat_side(s, bob)
    # the stick: gripped at the chest, resting over the shoulder to the sack
    s.capsule(26, 26 + bob, 14, 14 + bob, 1.0, 0.9, STICKR, sh=0.06)
    s.ball(26.5, 26.5 + bob, 1.7, 1.5, WHITE, power=2.2, wrap=0.10)  # grip paw
    head_side(s, 0, bob + 1, "open", "up")
    finish(s)
    whiskers_side(s, 0, bob + 1)


# ---- build the sheet -------------------------------------------------------------------
cells = [[new() for _ in range(COLS)] for _ in range(ROWS)]

# walk down/up: f0 planted neutral (idle_down/up reuse it). A SHUFFLE, not a
# churn: both paw tips stay visible under the hem the whole cycle — the
# stepping paw lifts only 1px (a heel-up tap, it never vanishes) — and bob +
# arm swing + tail carry the motion. NO hem sway here: in these views it is
# perpendicular to his travel and reads as a silly side-to-side wag (the side
# view keeps its fore/aft sway, which lies along the motion).
walk_bob   = [0, -1, -1, 0, -1, -1]
walk_liftl = [0, 1, 1, 0, 0, 0]
walk_liftr = [0, 0, 0, 0, 1, 1]
walk_swing = [0, 1, 1, 0, -1, -1]
walk_tail  = [0, 1, 1, 2, 1, 1]
for i in range(6):
    cat_down(cells[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
             walk_swing[i], walk_tail[i])
    cat_up(cells[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
           walk_swing[i], walk_tail[i])

# walk side: a flat SCISSOR shuffle under the near-floor hem — each foot tip
# slides along the ground between x=27 (reach ahead) and x=19 (behind): a
# TIGHT 8px stride, planted while travelling backward, a bare 1px toe-lift
# while swinging forward; the tips never leave the hem line, so nothing
# orbits. Offsets are asymmetric because footF/footB anchor 5px apart — these
# land both feet on the same absolute track, so f3 mirrors f0 instead of
# collapsing to center. f0 is the contact pose (idle_side reuses it, so its
# sway is 0). Body sits low on contact frames. Paired with the 14fps playback
# in player_frames.tres so the cadence keeps up with his ground speed.
side_fA   = [(2, 0), (0, 0), (-3, 0), (-6, 0), (-3, 1), (0, 1)]
side_fB   = [(-1, 0), (2, 1), (5, 1), (7, 0), (5, 0), (2, 0)]
side_bob  = [0, -1, -1, 0, -1, -1]
side_arm  = [-2, -1, 1, 2, 1, -1]
side_tail = [0, -1, -1, 0, 1, 1]
side_sway = [0, -1, -1, 0, 1, 1]       # skirt trails the stride fore/aft
for i in range(6):
    cat_side(cells[2][i], side_bob[i], side_fA[i], side_fB[i],
             side_arm[i], side_tail[i], coat_sway=side_sway[i])

# shoot rows: raise, aim (bolt fires here — muzzle tip on contract), recoil
# (the shot KICKS: body shoved off the muzzle, ears pinned, wince), settle.
for i, g in enumerate(("raise", "aim", "recoil", "settle")):
    rc = g == "recoil"
    gd = "aim" if g == "settle" else g
    cat_down(cells[3][i], bobY=(-2 if rc else 0), gun=gd, spread=(1 if rc else 0),
             eyes=("wince" if rc else "open"), ears=("flat" if rc else "up"))
    cat_up(cells[4][i], bobY=(1 if rc else 0), gun=("settle" if g == "settle" else g))
    cat_side(cells[5][i], bobY=(-1 if rc else 0), gun=gd,
             eyes=("wince" if rc else "open"), ears=("back" if rc else "up"))

# row 6: hurt x2, idle-down blink, idle-side tail-flick, happy, sad
cat_down(cells[6][0], eyes="hurt", ears="flat", head_dx=-1, tail_sway=2)
cat_down(cells[6][1], eyes="hurt", ears="flat", head_dx=1, tail_sway=-1)
cat_down(cells[6][2], eyes="closed")                    # matches walk_down f0
cat_side(cells[6][3], 0, side_fA[0], side_fB[0], side_arm[0],
         tail_raised=True)                              # matches walk_side f0
cat_down(cells[6][4], eyes="happy", tail_sway=2)        # his sweet face
cat_down(cells[6][5], eyes="sad", ears="droop", tail_droop=1)   # heartbroken

# row 7: reload — a spare beaker mag poured into the gun (player.gd plays it
# on the reload action or a dry trigger)
for i in range(4):
    reload_down(cells[7][i], i)

# row 8: the prologue staging poses — look_watch / sit / bow_head / knapsack
look_watch_down(cells[8][0])
sit_side(cells[8][1])
bow_head_down(cells[8][2])
for i in range(3):
    knapsack_side(cells[8][3 + i], i)

write_cells(os.path.join(HERE, "basil_gen.png"), cells, CELL)
