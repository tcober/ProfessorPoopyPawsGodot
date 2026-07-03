#!/usr/bin/env python3
"""High-fidelity procedural sprite sheet for Basil, the science cat.

FF6 / Chrono Trigger field-sprite proportions at 2x pixel density: head, torso and
legs each roughly a third of a ~66px figure in a 96x96 cell. 4-tone ramps with
violet-shifted shadows (assets/_palette.py), restrained 2x2 dither, near-dark unified
outlines, small expressive eyes. Writes assets/basil_gen.png (576x672, 96x96 cells,
6x7) matching entities/player/player_frames.tres:

  row0 walk_down(6)   row1 walk_up(6)   row2 walk_side(6, faces RIGHT; code mirrors)
  row3 shoot_down(4)  row4 shoot_up(4)  row5 shoot_side(4)
  row6 hurt(2) + idle_down blink + idle_side tail-flick + happy + sad

Design (from the real Basil): jet-black tuxedo cat; close-set yellow eyes with round
pupils (stern by default, sweet ^ ^ on the idle blink); narrow white blaze into a
plump muzzle; black nose smudge; whiskers breaking the silhouette; aviator goggles
pushed up on the forehead; straight-cut lab coat over dark trousers; white paws.

Landmarks (art contracts consumed by code): feet baseline y=88 (_artlib.ZONE_FEET);
origin (48,48); gun muzzle ~32px from origin (player.gd muzzle_offset).

Re-run: python3 assets/_gen_basil_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _artlib import Cell, write_cells, ZONE_CELL, ZONE_FEET
from _palette import BASIL

CELL, COLS, ROWS = ZONE_CELL, 6, 7
FEET = ZONE_FEET          # 88
CX = 48                   # figure center x

# vertical landmarks: head 22..47 | coat 44..66 | legs 66..88 (thirds-ish, cat-cute)
COAT_TOP, HEM = 44, 66

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
OUTS, OUT_FB   = BASIL["OUTS"], BASIL["OUT_FALLBACK"]
LID = (188, 158, 66, 255)         # closed-eye stroke


def new_cell():
    return Cell(CELL, grain=2)


# ---- shared body parts ---------------------------------------------------------

def legs_front(c, lift_l=0, lift_r=0, spread=0):
    """Slim trouser legs (a third of the figure now) with white paws and a toe
    notch. spread widens the stance (braced against recoil)."""
    for (x0, x1, lift, sp) in ((37, 43, lift_l, -spread), (53, 59, lift_r, spread)):
        c.cloth(x0 + sp, HEM - lift, x1 + sp, FEET - 5 - lift, PANTR, round_=0)
        # knee crease + inner-edge shade keep the long legs reading as two columns
        c.line([(x0 + sp + 1, HEM + 9 - lift), (x0 + sp + 2, HEM + 9 - lift)], PANTR[3])
        c.oval((x0 + x1) / 2 + sp, FEET - 2.6 - lift, 4.2, 3.0, WHITE)
        c.rect((x0 + x1) // 2 + sp - 1, FEET - lift - 1, (x0 + x1) // 2 + sp, FEET - lift, WHITE[3])  # toe notch


def coat_front(c, dy=0):
    """Lab coat, front: straight A-line silhouette, flat panels, crisp center
    placket, lapels over a white chest tuft, hip pocket, hem line."""
    top_y, hem_y = COAT_TOP + dy, HEM + dy
    for y in range(top_y, hem_y + 1):
        vy = (y - top_y) / (hem_y - top_y)
        half = 11.2 + vy * 3.2                 # slight flare only
        x0, x1 = int(round(CX - half)), int(round(CX - 1 + half))
        for x in range(x0, x1 + 1):
            hx = (x - x0) / max(1, x1 - x0)
            t = 0.26 + 0.22 * hx               # flat panel, gentle side light
            if x >= x1 - 2:
                t += 0.30                      # shaded right edge
            elif x <= x0 + 1:
                t -= 0.10                      # lit left edge
            if y >= hem_y - 1:
                t += 0.34                      # hem line
            c.set(x, y, c._pick(COATR, t, x, y))
    # center opening: dark placket + light catch on its edge
    for y in range(top_y + 6, hem_y + 1):
        c.set(CX, y, COATR[3])
        c.set(CX + 1, y, COATR[3])
        c.set(CX - 1, y, COATR[0])
    # open collar: white chest tuft framed by lapels
    c.tri((CX, top_y), top_y + 6, 44, 52, WHITE)
    c.line([(42, top_y + 2), (43, top_y + 3), (44, top_y + 4)], COATR[0])
    c.line([(54, top_y + 2), (53, top_y + 3), (52, top_y + 4)], COATR[2])
    # hip pocket + a purple pen clipped at the breast
    c.rect(36, 62 + dy, 42, 62 + dy, COATR[3])
    c.rect(36, 63 + dy, 42, 63 + dy, COATR[2])
    c.rect(40, 50 + dy, 41, 53 + dy, GUNP)
    c.rect(40, 53 + dy, 41, 54 + dy, (132, 84, 174, 255))


def arms_hanging(c, dy=0, dl=0, dr=0):
    """Coat sleeves with white paws; dl/dr swing them. Cuff + inner-edge lines keep
    the sleeves reading against the coat body."""
    c.cloth(28, 45 + dy + dl, 35, 59 + dy + dl, COATR, round_=2, sh=0.10)
    for y in range(45 + dy + dl, 60 + dy + dl):
        c.set(35, y, COATR[3])
    c.rect(28, 59 + dy + dl, 35, 60 + dy + dl, COATR[3])      # cuff
    c.oval(31.4, 62.6 + dy + dl, 3.4, 3.0, WHITE)
    c.cloth(60, 45 + dy + dr, 67, 59 + dy + dr, COATR, round_=2, sh=0.18)
    for y in range(45 + dy + dr, 60 + dy + dr):
        c.set(60, y, COATR[3])
    c.rect(60, 59 + dy + dr, 67, 60 + dy + dr, COATR[3])
    c.oval(63.8, 62.6 + dy + dr, 3.4, 3.0, WHITE, sh=0.10)


def tail_curl(c, dx=0, dy=0):
    """Tail curling out right of the hem, dithered fur shading, fluffy tip."""
    path = [(63, 70), (66, 66), (68, 61), (68.4 + dx * 0.5, 56), (67.6 + dx, 51)]
    for i, (px_, py_) in enumerate(path):
        r = 3.4 if i < 2 else 2.8
        c.oval(px_, py_ + dy, r, r, FUR, sh=0.1 - i * 0.06)
    c.set(int(66 + dx), int(49 + dy), FUR[0])                 # tip catchlight
    c.set(int(67 + dx), int(49 + dy), FUR[0])


def _eye_open(c, ex, ey, brow_out):
    """4x5 stern yellow eye: bright top band, 2px pupil, hard glint, outer brow."""
    c.rect(ex, ey, ex + 3, ey + 4, EYE_Y)
    c.rect(ex, ey, ex + 3, ey + 1, EYE_YL)
    c.rect(ex + 1, ey + 2, ex + 2, ey + 4, PUPIL)
    c.set(ex + 1, ey + 1, GLINT)
    c.set(ex + brow_out, ey - 2, FUR[3])                      # stern brow
    c.set(ex + brow_out + (1 if brow_out == 0 else -1), ey - 2, FUR[3])


def head_down(c, dy=0, dx=0, eyes="open", ears="up"):
    """The face. eyes: open (stern-sweet) / closed (^ ^) / happy / sad / hurt (>_<).
    ears: up / flat (hurt) / droop (sad)."""
    # ears (behind head): tall curved triangles w/ pink inner, tips clear the goggles
    if ears == "up":
        c.tri((37 + dx, 16 + dy), 30 + dy, 31 + dx, 45 + dx, FUR)
        c.tri((59 + dx, 16 + dy), 30 + dy, 51 + dx, 65 + dx, FUR, sh=0.15)
        c.tri((37 + dx, 19 + dy), 28 + dy, 33 + dx, 42 + dx, EARIN)
        c.tri((59 + dx, 19 + dy), 28 + dy, 55 + dx, 63 + dx, EARIN_D)
    elif ears == "droop":                                     # slouched out + down (sad)
        c.tri((34 + dx, 28 + dy), 36 + dy, 30 + dx, 44 + dx, FUR)
        c.tri((62 + dx, 28 + dy), 36 + dy, 52 + dx, 66 + dx, FUR, sh=0.15)
    else:                                                     # flattened (hurt)
        c.tri((28 + dx, 30 + dy), 36 + dy, 34 + dx, 46 + dx, FUR)
        c.tri((68 + dx, 30 + dy), 36 + dy, 50 + dx, 62 + dx, FUR, sh=0.15)
    # skull: soft dome
    c.oval(CX + dx, 37 + dy, 13.0, 10.5, FUR, power=2.4)
    # plump white muzzle + NARROW blaze (eyes sit in black fur; the white is a thin
    # stripe between them that fans out at the nose)
    c.oval(CX + dx, 44 + dy, 7.6, 4.6, WHITE, power=2.2)
    c.tri((CX + dx, 29 + dy), 40 + dy, CX - 1.5 + dx, CX + 1.5 + dx, WHITE)
    # fur ticks (cheek sheen)
    c.line([(36 + dx, 33 + dy), (37 + dx, 32 + dy), (38 + dx, 31 + dy)], FUR[0])
    c.line([(58 + dx, 31 + dy), (59 + dx, 32 + dy), (60 + dx, 33 + dy)], FUR[1])
    # nose smudge + cat mouth
    c.rect(46 + dx, 41 + dy, 49 + dx, 42 + dy, NOSE)
    c.set(46 + dx, 41 + dy, (52, 42, 48, 255))                # nose highlight
    if eyes == "hurt":
        c.rect(46 + dx, 44 + dy, 49 + dx, 47 + dy, MOUTH)     # little open wail
        c.rect(47 + dx, 46 + dy, 48 + dx, 47 + dy, (96, 54, 60, 255))
    elif eyes == "wince":
        c.rect(44 + dx, 44 + dy, 51 + dx, 45 + dy, MOUTH)     # gritted teeth
        c.rect(47 + dx, 44 + dy, 48 + dx, 45 + dy, WHITE[0])
    elif eyes == "happy":
        c.rect(44 + dx, 43 + dy, 51 + dx, 47 + dy, (96, 54, 60, 255))   # open grin
        c.rect(46 + dx, 46 + dy, 49 + dx, 47 + dy, (226, 120, 128, 255))  # tongue
        c.rect(45 + dx, 43 + dy, 50 + dx, 43 + dy, (96, 54, 60, 255))
        c.rect(36 + dx, 41 + dy, 37 + dx, 42 + dy, (238, 160, 158, 255))  # blush
        c.rect(59 + dx, 41 + dy, 60 + dx, 42 + dy, (238, 160, 158, 255))
    elif eyes == "sad":
        c.line([(45 + dx, 45 + dy), (46 + dx, 44 + dy), (47 + dx, 45 + dy),
                (48 + dx, 44 + dy), (49 + dx, 45 + dy)], MOUTH)  # wobble frown
    else:
        c.set(47 + dx, 43 + dy, MOUTH)
        c.set(48 + dx, 43 + dy, MOUTH)
        c.line([(45 + dx, 44 + dy), (46 + dx, 44 + dy)], MOUTH)
        c.line([(49 + dx, 44 + dy), (50 + dx, 44 + dy)], MOUTH)
    # whisker dots on the muzzle
    for wx, wy in ((41, 41), (39, 44), (54, 41), (56, 44)):
        c.set(wx + dx, wy + dy, WHISKD)
    # eyes: close-set, small CT read
    if eyes == "open":
        _eye_open(c, 40 + dx, 32 + dy, 0)
        _eye_open(c, 52 + dx, 32 + dy, 3)
    elif eyes in ("closed", "happy"):                         # sweet ^ ^
        for ex in (40, 52):
            c.line([(ex + dx, 35 + dy), (ex + 1 + dx, 34 + dy), (ex + 2 + dx, 33 + dy),
                    (ex + 3 + dx, 34 + dy), (ex + 4 + dx, 35 + dy)], LID)
    elif eyes == "sad":                                       # glossy, downcast, teary
        for ex in (40, 52):
            c.rect(ex + dx, 33 + dy, ex + 3 + dx, 37 + dy, EYE_Y)
            c.rect(ex + dx, 33 + dy, ex + 3 + dx, 34 + dy, FUR[2])     # heavy upper lid
            c.rect(ex + 1 + dx, 35 + dy, ex + 2 + dx, 37 + dy, PUPIL)
            c.set(ex + 1 + dx, 37 + dy, GLINT)                # low watery glint
            c.set(ex + 3 + dx, 36 + dy, GLINT)                # double shine = teary
        c.line([(43 + dx, 31 + dy), (44 + dx, 30 + dy)], FUR[0])       # raised inner brows
        c.line([(52 + dx, 30 + dy), (53 + dx, 31 + dy)], FUR[0])
        c.rect(40 + dx, 39 + dy, 40 + dx, 40 + dy, (170, 214, 250, 255))  # a welling tear
    else:                                                     # hurt / wince >_<
        for ex, s in ((40, 2), (54, -2)):
            c.line([(ex + dx, 32 + dy), (ex + 1 + dx, 33 + dy)], LID)
            c.set(ex + s + dx, 34 + dy, LID)
            c.line([(ex + dx, 36 + dy), (ex + 1 + dx, 35 + dy)], LID)
    # goggles: rimmed lenses pushed up on the forehead + strap
    c.rect(33 + dx, 27 + dy, 63 + dx, 28 + dy, GOGRIM[2])
    for gx in (41, 55):
        c.oval(gx + dx, 25.0 + dy, 4.4, 3.6, GOGRIM, power=2.0)
        c.oval(gx + dx, 25.0 + dy, 2.6, 2.0, GOGLEN, power=2.0)
        c.set(gx - 1 + dx, 24 + dy, (252, 240, 214, 255))     # glint inside the lens
        c.set(gx + dx, 24 + dy, (252, 240, 214, 255))


def head_up(c, dy=0):
    """Back of head: dome, ear backs, goggle strap + buckle."""
    c.tri((37, 16 + dy), 30 + dy, 31, 45, FUR)
    c.tri((59, 16 + dy), 30 + dy, 51, 65, FUR, sh=0.15)
    c.tri((37, 19 + dy), 28 + dy, 33, 42, FUR, sh=0.35)
    c.tri((59, 19 + dy), 28 + dy, 55, 63, FUR, sh=0.45)
    c.oval(CX, 37 + dy, 13.0, 10.5, FUR, power=2.4)
    c.rect(32, 27 + dy, 64, 30 + dy, GOGRIM[2])
    c.rect(32, 27 + dy, 64, 28 + dy, GOGRIM[1])
    c.rect(45, 27 + dy, 51, 30 + dy, GOGRIM[0])               # buckle
    c.rect(47, 28 + dy, 49, 29 + dy, GOGRIM[2])
    # neck fur part line
    c.line([(42, 46 + dy), (44, 47 + dy), (46, 48 + dy), (50, 48 + dy),
            (52, 47 + dy), (54, 46 + dy)], FUR[3])


def head_side(c, dy=0, dx=0, eyes="open", ears="up"):
    """Right-facing profile: snout, one small eye, goggles with one lens.
    dx shifts the whole head — the recoil lean-back."""
    if ears == "up":
        c.tri((41 + dx, 15 + dy), 29 + dy, 33 + dx, 49 + dx, FUR)
        c.tri((41 + dx, 18 + dy), 27 + dy, 37 + dx, 45 + dx, EARIN)
        c.tri((55 + dx, 17 + dy), 29 + dy, 49 + dx, 61 + dx, FUR, sh=0.3)   # far ear
    else:                                                     # swept back
        c.tri((28 + dx, 27 + dy), 34 + dy, 32 + dx, 44 + dx, FUR)
    c.oval(46 + dx, 36 + dy, 12.5, 10.0, FUR, power=2.4)      # skull
    c.oval(58 + dx, 41 + dy, 6.4, 5.2, FUR, power=2.0)        # snout mass
    c.oval(59 + dx, 42.5 + dy, 5.4, 4.0, WHITE, power=2.0)    # white muzzle
    c.rect(62 + dx, 38 + dy, 64 + dx, 39 + dy, NOSE)          # nose smudge
    c.set(62 + dx, 38 + dy, (52, 42, 48, 255))
    c.line([(61 + dx, 44 + dy), (60 + dx, 45 + dy), (58 + dx, 46 + dy)], MOUTH)
    c.set(54 + dx, 40 + dy, WHISKD); c.set(52 + dx, 43 + dy, WHISKD)
    if eyes == "open":
        _eye_open(c, 50 + dx, 30 + dy, 3)
    elif eyes == "closed":
        c.line([(50 + dx, 33 + dy), (51 + dx, 32 + dy), (52 + dx, 31 + dy),
                (53 + dx, 32 + dy), (54 + dx, 33 + dy)], LID)
    elif eyes == "wince":                                     # squeezed shut >
        c.line([(50 + dx, 30 + dy), (51 + dx, 31 + dy)], LID)
        c.set(52 + dx, 32 + dy, LID)
        c.line([(50 + dx, 34 + dy), (51 + dx, 33 + dy)], LID)
        c.set(55 + dx, 28 + dy, FUR[3])                       # knit brow
    # goggles: strap + one lens on the forehead
    c.rect(34 + dx, 25 + dy, 59 + dx, 26 + dy, GOGRIM[2])
    c.oval(52 + dx, 22.5 + dy, 4.6, 3.6, GOGRIM, power=2.0)
    c.oval(52 + dx, 22.5 + dy, 2.7, 2.0, GOGLEN, power=2.0)
    c.set(51 + dx, 22 + dy, (252, 240, 214, 255))
    c.set(52 + dx, 22 + dy, (252, 240, 214, 255))


def whiskers_down(c, dy=0, dx=0):
    """Whiskers breaking the silhouette (drawn after the outline): solid strokes
    off the cheeks, not dotted specks."""
    for pts in (((31, 40), (29, 40), (27, 41), (25, 42)),
                ((31, 44), (29, 45), (27, 46)),
                ((65, 40), (67, 40), (69, 41), (71, 42)),
                ((65, 44), (67, 45), (69, 46))):
        for (x, y) in pts:
            c.set(x + dx, y + dy, WHISK)


def whiskers_side(c, dy=0, dx=0):
    for pts in (((65, 37), (67, 37), (69, 38), (71, 39)),
                ((65, 43), (67, 43), (69, 44))):
        for (x, y) in pts:
            c.set(x + dx, y + dy, WHISK)


# ---- full poses -----------------------------------------------------------------

def cat_down(c, bob=0, lift_l=0, lift_r=0, swing=0, tail_dx=0,
             eyes="open", ears="up", head_dx=0, gun=None, spread=0):
    tail_curl(c, tail_dx, bob)
    legs_front(c, lift_l, lift_r, spread)
    coat_front(c, bob)
    if gun is None:
        arms_hanging(c, bob, swing, -swing)
    elif gun == "raise":
        arms_hanging(c, bob, 0, -4)
        c.cloth(58, 55 + bob, 66, 61 + bob, GUNR, round_=0)   # gun at hip
        c.rect(61, 57 + bob, 62, 58 + bob, GUNE)
    else:
        k = -4 if gun == "recoil" else 0                      # recoil kicks UP
        c.cloth(28, 46 + bob, 35, 57 + bob, COATR, round_=2, sh=0.1)
        c.cloth(60, 46 + bob, 67, 57 + bob, COATR, round_=2, sh=0.16)
        c.cloth(32, 57 + bob, 40, 63 + bob, COATR, round_=2, sh=0.1)
        c.cloth(55, 57 + bob, 63, 63 + bob, COATR, round_=2, sh=0.16)
        c.oval(47.5, 64 + bob + k, 6.4, 3.4, WHITE)           # gripping paws
        c.cloth(42, 66 + bob + k, 53, 72 + bob + k, GUNR, round_=2)
        c.cloth(44, 69 + bob + k, 51, 80 + bob + k, GUNR, round_=0)
        c.rect(42, 68 + bob + k, 42, 69 + bob + k, GUNE)
        c.rect(53, 68 + bob + k, 53, 69 + bob + k, GUNE)
        c.rect(44, 80 + bob + k, 51, 81 + bob + k, GUNP)
        c.rect(46, 82 + bob + k, 49, 83 + bob + k, GUNP)
    head_down(c, bob, head_dx, eyes, ears)
    c.outline(OUTS, OUT_FB)
    whiskers_down(c, bob, head_dx)


def coat_back(c, bob):
    """Coat back: straight flat panel, center vent seam, back belt, collar band."""
    top_y, hem_y = COAT_TOP + bob, HEM + bob
    for y in range(top_y, hem_y + 1):
        vy = (y - top_y) / (hem_y - top_y)
        half = 11.2 + vy * 3.2
        x0, x1 = int(round(CX - half)), int(round(CX - 1 + half))
        for x in range(x0, x1 + 1):
            hx = (x - x0) / max(1, x1 - x0)
            t = 0.26 + 0.22 * hx
            if x >= x1 - 2:
                t += 0.30
            elif x <= x0 + 1:
                t -= 0.10
            if y >= hem_y - 1:
                t += 0.34
            c.set(x, y, c._pick(COATR, t, x, y))
    for y in range(top_y + 4, hem_y + 1):                     # back vent seam
        c.set(CX, y, COATR[2])
        c.set(CX + 1, y, COATR[2])
    c.line([(39, 55 + bob), (40, 55 + bob), (55, 55 + bob), (56, 55 + bob)], COATR[3])
    c.rect(42, 53 + bob, 53, 55 + bob, COATR[1])              # back belt
    c.rect(43, 54 + bob, 44, 54 + bob, COATR[3])              # belt button L
    c.rect(51, 54 + bob, 52, 54 + bob, COATR[3])              # belt button R
    c.rect(37, top_y, 58, top_y + 2, COATR[1])                # collar band


def cat_up(c, bob=0, lift_l=0, lift_r=0, swing=0, tail_dx=0, gun=None):
    legs_front(c, lift_l, lift_r)
    coat_back(c, bob)
    if gun is None:
        arms_hanging(c, bob, swing, -swing)
    else:
        arms_hanging(c, bob, 0, 0)
    tail_up_swish(c, tail_dx)
    head_up(c, bob)
    if gun is not None:                                       # raised gun over the head
        k = 2 if gun == "recoil" else 0
        if gun == "raise":
            c.oval(59, 20 + bob, 3.8, 3.8, WHITE)
            c.cloth(56, 10 + bob, 61, 16 + bob, GUNR, round_=0)
            c.rect(58, 12 + bob, 59, 13 + bob, GUNE)
        else:
            c.oval(59, 17 + bob + k, 3.8, 3.8, WHITE)
            c.cloth(56, 4 + bob + k, 61, 12 + bob + k, GUNR, round_=0)
            c.rect(58, 8 + bob + k, 59, 9 + bob + k, GUNE)
            c.rect(56, 2 + bob + k, 61, 3 + bob + k, GUNP)
    c.outline(OUTS, OUT_FB)


def tail_up_swish(c, dx=0):
    path = [(60, 64), (64, 60), (66, 55), (67 + dx * 0.5, 50), (66 + dx, 45)]
    for i, (px_, py_) in enumerate(path):
        c.oval(px_, py_, 3.2, 3.2, FUR, sh=0.12 - i * 0.05)
    c.set(int(64 + dx), 42, FUR[0])
    c.set(int(65 + dx), 42, FUR[0])


def cat_side(c, bob=0, front_dx=0, back_dx=0, lift_f=0, lift_b=0, arm_dx=0,
             tail_dy=0, tail_raised=False, eyes="open", ears="up", gun=None):
    # Recoil throws the torso/head BACK while the feet skid FORWARD under him —
    # the classic braced-against-the-blast lean.
    lean = 4 if gun == "recoil" else 0
    tail_side(c, tail_dy, tail_raised or gun == "recoil")
    if gun == "recoil":
        front_dx += 6
        back_dx += 4
    for (x0, x1, dx_, lift) in ((34, 40, back_dx, lift_b), (50, 56, front_dx, lift_f)):
        c.cloth(x0 + dx_, HEM - lift, x1 + dx_, FEET - 5 - lift, PANTR, round_=0)
        c.oval((x0 + x1) / 2 + dx_, FEET - 2.6 - lift, 4.0, 3.0, WHITE)
    # coat in profile: straight panel with a trailing back hem; the lean tips the
    # shoulders further back than the hem
    top_y, hem_y = COAT_TOP + bob, HEM + bob
    for y in range(top_y, hem_y + 1):
        vy = (y - top_y) / (hem_y - top_y)
        x_off = -lean + int(round(vy * lean * 0.5))
        x0 = int(round(34 - vy * 5)) + x_off                  # back hem trails
        x1 = 58 + x_off
        for x in range(x0, x1 + 1):
            hx = (x - x0) / max(1, x1 - x0)
            t = 0.26 + 0.22 * hx
            if x >= x1 - 2:
                t += 0.30
            elif x <= x0 + 1:
                t -= 0.10
            if y >= hem_y - 1:
                t += 0.34
            c.set(x, y, c._pick(COATR, t, x, y))
        if y >= top_y + 4:                                    # coat front edge
            c.set(x1 - 2, y, COATR[3])
    if gun is None:
        c.cloth(42 + arm_dx, 45 + bob, 49 + arm_dx, 56 + bob, COATR, round_=2, sh=0.14)
        for y in range(46 + bob, 57 + bob):                   # sleeve seam
            c.set(49 + arm_dx, y, COATR[3])
        c.rect(42 + arm_dx, 56 + bob, 49 + arm_dx, 57 + bob, COATR[3])   # cuff
        c.oval(45 + arm_dx, 60.5 + bob, 4.0, 3.6, WHITE)
    else:
        k = 4 if gun == "recoil" else 0                       # arm shoved back...
        r = 4 if gun == "recoil" else 0                       # ...barrel kicked up
        if gun == "raise":
            c.cloth(46, 43 + bob, 57, 49 + bob, COATR, round_=2, sh=0.1)
            c.oval(60, 45.5 + bob, 3.8, 3.6, WHITE)
            c.cloth(58, 35 + bob, 65, 43 + bob, GUNR, round_=0)
            c.rect(60, 38 + bob, 61, 39 + bob, GUNE)
        else:
            c.cloth(48 - k, 44 + bob, 61 - k, 51 + bob, COATR, round_=2, sh=0.1)
            c.oval(64 - k, 49 + bob - r * 0.5, 3.8, 3.6, WHITE)
            c.cloth(66 - k, 44 + bob - r, 77 - k, 50 + bob - r, GUNR, round_=2)
            c.cloth(68 - k, 52 + bob - r, 73 - k, 55 + bob - r, GUNR, round_=0)
            c.rect(70 - k, 46 + bob - r, 71 - k, 47 + bob - r, GUNE)
            c.rect(73 - k, 46 + bob - r, 74 - k, 47 + bob - r, GUNE)
            c.rect(78 - k, 44 + bob - r, 80 - k, 47 + bob - r, GUNP)
    head_side(c, bob, -lean, eyes, ears)
    c.outline(OUTS, OUT_FB)
    whiskers_side(c, bob, -lean)


def tail_side(c, dy=0, raised=False):
    if raised:
        path = [(32, 54), (29, 49), (27, 44), (27, 39)]
    else:
        path = [(32, 58), (29, 55), (26, 53), (23, 50)]
    for i, (px_, py_) in enumerate(path):
        c.oval(px_, py_ + dy, 3.4, 3.4, FUR, sh=0.15 - i * 0.05)
    tx, ty = path[-1]
    c.set(int(tx) - 2, int(ty) - 4 + dy, FUR[0])
    c.set(int(tx) - 1, int(ty) - 4 + dy, FUR[0])


# ---- build the sheet -------------------------------------------------------------
cells = [[new_cell() for _ in range(COLS)] for _ in range(ROWS)]

walk_bob   = [0, -2, 0, 0, -2, 0]
walk_liftl = [4, 2, 0, 0, 0, 0]
walk_liftr = [0, 0, 0, 4, 2, 0]
walk_swing = [2, 1, 0, -2, -1, 0]
walk_tail  = [0, 2, 4, 4, 2, 0]
for i in range(6):
    cat_down(cells[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
             walk_swing[i], walk_tail[i])
    cat_up(cells[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
           walk_swing[i], walk_tail[i])

side_front = [6, 2, 0, -6, -2, 0]
side_back  = [-6, -2, 0, 6, 2, 0]
side_liftf = [2, 0, 0, 0, 2, 0]
side_liftb = [0, 2, 0, 2, 0, 0]
side_bob   = [0, 0, -2, 0, 0, -2]
side_arm   = [-4, -2, 0, 4, 2, 0]
side_tail  = [0, -2, -2, 0, 2, 2]
for i in range(6):
    cat_side(cells[2][i], side_bob[i], side_front[i], side_back[i],
             side_liftf[i], side_liftb[i], side_arm[i], side_tail[i])

for i, g in enumerate(("raise", "aim", "recoil", "aim")):
    rc = g == "recoil"
    # Recoil frame: body shoved back off the muzzle, feet braced forward, ears
    # pinned, eyes squeezed in a wince — the shot should look like it KICKS.
    cat_down(cells[3][i], gun=g, bob=(-4 if rc else 0), spread=(2 if rc else 0),
             eyes=("wince" if rc else "open"), ears=("flat" if rc else "up"))
    cat_up(cells[4][i], gun=g, bob=(2 if rc else 0))
    cat_side(cells[5][i], gun=g, bob=(-2 if rc else 0),
             eyes=("wince" if rc else "open"), ears=("back" if rc else "up"))

cat_down(cells[6][0], eyes="hurt", ears="flat", head_dx=-2, tail_dx=4)
cat_down(cells[6][1], eyes="hurt", ears="flat", head_dx=2, tail_dx=0)
cat_down(cells[6][2], eyes="closed")
cat_side(cells[6][3], tail_raised=True)
cat_down(cells[6][4], eyes="happy", tail_dx=4)                # his sweet face
cat_down(cells[6][5], eyes="sad", ears="droop")               # his heartbroken face

write_cells(os.path.join(HERE, "basil_gen.png"), cells, CELL)
