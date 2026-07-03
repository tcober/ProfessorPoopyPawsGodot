#!/usr/bin/env python3
"""High-fidelity procedural sprite sheet for Basil, the science cat.

Rendering aims for an FF6 / Chrono Trigger field-sprite read: taller proportions
(head / torso / legs each roughly a third of the figure), a muted 4-tone SNES
palette, restrained dithering, near-dark unified outlines, and small expressive
eyes. Writes assets/basil_gen.png
(288x336, 48x48 cells, 6x7) matching entities/player/player_frames.tres:

  row0 walk_down(6)   row1 walk_up(6)   row2 walk_side(6, faces RIGHT; code mirrors)
  row3 shoot_down(4)  row4 shoot_up(4)  row5 shoot_side(4)
  row6 hurt(2) + idle_down blink + idle_side tail-flick

Design (from the real Basil's photos/sketches): jet-black tuxedo cat; big close-set
yellow eyes with round dark pupils; wide white blaze flowing into a plump white
muzzle; black nose smudge; aviator goggles pushed up on the forehead; white lab coat
over dark trousers; white "poopy" paws. Feet baseline y=44; origin (24,24); gun
muzzle ~16px from origin (player.gd muzzle_offset).

Re-run: python3 assets/_gen_basil_sprites.py
"""
import struct, zlib, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
CELL, COLS, ROWS = 48, 6, 7
FEET = 44

# ---- material ramps (light -> dark), shadows hue-shift cool/purple ------------
FUR    = [(78, 74, 96, 255), (52, 50, 66, 255), (34, 32, 46, 255), (20, 18, 30, 255)]
WHITE  = [(250, 248, 242, 255), (228, 224, 216, 255), (198, 194, 192, 255), (162, 158, 166, 255)]
COATR  = [(236, 236, 238, 255), (204, 204, 210, 255), (166, 166, 178, 255), (126, 126, 142, 255)]
PANTR  = [(72, 70, 86, 255), (56, 54, 68, 255), (42, 40, 52, 255), (30, 28, 40, 255)]
GOGRIM = [(140, 100, 62, 255), (112, 78, 50, 255), (86, 58, 38, 255), (60, 40, 28, 255)]
GOGLEN = [(238, 214, 168, 255), (206, 178, 132, 255), (174, 146, 104, 255), (140, 114, 82, 255)]
GUNR   = [(140, 148, 164, 255), (108, 114, 130, 255), (80, 86, 102, 255), (56, 60, 76, 255)]

EYE_Y  = (224, 188, 70, 255)
EYE_YL = (242, 218, 118, 255)
PUPIL  = (16, 12, 16, 255)
GLINT  = (255, 255, 250, 255)
NOSE   = (28, 22, 26, 255)
MOUTH  = (146, 108, 104, 255)
EARIN  = (204, 116, 134, 255)
EARIN_D= (160, 84, 104, 255)
WHISK  = (216, 214, 208, 235)
WHISKD = (150, 146, 142, 255)   # whisker dots on the muzzle
GUNE   = (132, 246, 152, 255)
GUNP   = (188, 132, 232, 255)

# outline color per material family
OUT_FUR   = (8, 6, 14, 255)
OUT_LIGHT = (58, 56, 72, 255)    # around whites / coat
OUT_GOG   = (38, 24, 16, 255)
OUTS = {}
for r in (FUR, PANTR):
    for c in r:
        OUTS[c] = OUT_FUR
for r in (WHITE, COATR):
    for c in r:
        OUTS[c] = OUT_LIGHT
for r in (GOGRIM, GOGLEN):
    for c in r:
        OUTS[c] = OUT_GOG
for r in (GUNR,):
    for c in r:
        OUTS[c] = OUT_FUR
OUT_SET = set(OUTS.values())


class Cell:
    def __init__(self):
        self.px = [[None] * CELL for _ in range(CELL)]

    def set(self, x, y, c):
        if 0 <= x < CELL and 0 <= y < CELL:
            self.px[y][x] = c

    def get(self, x, y):
        if 0 <= x < CELL and 0 <= y < CELL:
            return self.px[y][x]
        return None

    # -- shaded primitives -----------------------------------------------------
    @staticmethod
    def _pick(ramp, t, x, y):
        """t in 0..1 (0 = lit, 1 = shadow) -> ramp tone, dithered at band edges."""
        b = max(0.0, min(2.999, t * 3.0))
        i = int(b)
        frac = b - i
        lo, hi = 0.45, 0.58        # narrow dither band: clean fields, soft edges
        if frac > hi or (lo < frac <= hi and (x + y) % 2 == 0):
            i += 1
        return ramp[min(3, i)]

    def oval(self, cx, cy, rx, ry, ramp, sh=0.0, power=2.0):
        """Filled superellipse shaded as a dome lit from the upper-left.
        sh biases the whole form darker (parts tucked in shadow)."""
        for y in range(int(cy - ry), int(cy + ry) + 2):
            for x in range(int(cx - rx), int(cx + rx) + 2):
                nx = (x - cx) / rx
                ny = (y - cy) / ry
                d = abs(nx) ** power + abs(ny) ** power
                if d > 1.0:
                    continue
                t = 0.42 + 0.30 * (nx * 0.55 + ny * 0.80) + 0.30 * d * d + sh
                self.set(x, y, self._pick(ramp, t, x, y))

    def cloth(self, x0, y0, x1, y1, ramp, round_=2, folds=(), sh=0.0):
        """Rounded garment panel, lit from the upper-left, with vertical folds."""
        w = max(1, x1 - x0)
        h = max(1, y1 - y0)
        for y in range(y0, y1 + 1):
            vy = (y - y0) / h
            for x in range(x0, x1 + 1):
                hx = (x - x0) / w
                # rounded corners
                ex = min(x - x0, x1 - x)
                ey = min(y - y0, y1 - y)
                if ex + ey < round_:
                    continue
                t = 0.22 + 0.33 * hx + 0.38 * vy + sh
                for fx in folds:
                    if abs(x - fx) < 1.5:
                        t += 0.22
                self.set(x, y, self._pick(ramp, t, x, y))

    def tri(self, apex, base_y, x0, x1, ramp_or_color, sh=0.0):
        ax, ay = apex
        span = max(1, base_y - ay)
        for y in range(ay, base_y + 1):
            f = (y - ay) / span
            xl = round(ax + (x0 - ax) * f)
            xr = round(ax + (x1 - ax) * f)
            for x in range(min(xl, xr), max(xl, xr) + 1):
                if isinstance(ramp_or_color, list):
                    t = 0.30 + 0.45 * f + 0.25 * (x - xl) / max(1, xr - xl) + sh
                    self.set(x, y, self._pick(ramp_or_color, t, x, y))
                else:
                    self.set(x, y, ramp_or_color)

    def line(self, pts, c):
        for (x, y) in pts:
            self.set(x, y, c)

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    # -- finishing passes --------------------------------------------------------
    def outline(self):
        edge = []
        for y in range(CELL):
            for x in range(CELL):
                if self.px[y][x] is not None:
                    continue
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    p = self.get(nx, ny)
                    if p and p[3] == 255 and p not in OUT_SET:
                        edge.append((x, y, OUTS.get(p, OUT_FUR)))
                        break
        for x, y, c in edge:
            self.px[y][x] = c


# ---- shared body parts ---------------------------------------------------------

def legs_front(c, lift_l=0, lift_r=0, spread=0):
    """Slim trouser legs with small white paws and a toe notch. spread widens the
    stance (braced against recoil)."""
    for (x0, x1, lift, sp) in ((18, 21, lift_l, -spread), (26, 29, lift_r, spread)):
        c.cloth(x0 + sp, 35 - lift, x1 + sp, FEET - 3 - lift, PANTR, round_=0)
        c.oval((x0 + x1) / 2 + sp, FEET - 1.6 - lift, 2.2, 1.7, WHITE)
        c.set((x0 + x1) // 2 + sp, FEET - lift, WHITE[3])     # toe notch


def coat_front(c, dy=0):
    """Lab coat, front: straight A-line silhouette, flat panels (no puff), crisp
    center placket, lapels over a white chest tuft, hip pocket, hem line."""
    top_y, hem_y = 20 + dy, 35 + dy
    for y in range(top_y, hem_y + 1):
        vy = (y - top_y) / (hem_y - top_y)
        half = 5.6 + vy * 1.6                  # slight flare only
        x0, x1 = int(round(24 - half)), int(round(23 + half))
        for x in range(x0, x1 + 1):
            hx = (x - x0) / max(1, x1 - x0)
            t = 0.26 + 0.22 * hx               # flat panel, gentle side light
            if x >= x1 - 1:
                t += 0.30                      # shaded right edge
            elif x <= x0:
                t -= 0.10                      # lit left edge
            if y >= hem_y:
                t += 0.34                      # hem line
            c.set(x, y, c._pick(COATR, t, x, y))
    # center opening: dark placket + light catch on its edge
    for y in range(top_y + 3, hem_y + 1):
        c.set(24, y, COATR[3])
        c.set(23, y, COATR[0])
    # open collar: white chest tuft framed by lapels
    c.tri((24, top_y), top_y + 3, 22, 26, WHITE)
    c.line([(21, top_y + 1), (22, top_y + 2)], COATR[0])
    c.line([(27, top_y + 1), (26, top_y + 2)], COATR[2])
    # hip pocket + a 2px purple pen clipped in the breast (reads as an object,
    # not stray noise, at 1x)
    c.line([(18, 31 + dy), (19, 31 + dy), (20, 31 + dy)], COATR[3])
    c.set(20, 23 + dy, GUNP)
    c.set(20, 24 + dy, (132, 84, 174, 255))


def arms_hanging(c, dy=0, dl=0, dr=0):
    """Coat sleeves with white paws; dl/dr swing them. Cuff + inner-edge lines keep
    the sleeves reading against the coat body."""
    c.cloth(14, 22 + dy + dl, 17, 29 + dy + dl, COATR, round_=1, sh=0.10)
    for y in range(22 + dy + dl, 30 + dy + dl):
        c.set(17, y, COATR[3])
    c.rect(14, 29 + dy + dl, 17, 29 + dy + dl, COATR[3])      # cuff
    c.oval(15.6, 31.2 + dy + dl, 1.7, 1.6, WHITE)
    c.cloth(30, 22 + dy + dr, 33, 29 + dy + dr, COATR, round_=1, sh=0.18)
    for y in range(22 + dy + dr, 30 + dy + dr):
        c.set(30, y, COATR[3])
    c.rect(30, 29 + dy + dr, 33, 29 + dy + dr, COATR[3])
    c.oval(31.8, 31.2 + dy + dr, 1.7, 1.6, WHITE, sh=0.10)


def tail_curl(c, dx=0, dy=0):
    """Tail curling out right of the hem, dithered fur shading, fluffy tip."""
    path = [(31.5, 35), (33, 33), (34, 30.5), (34.2 + dx * 0.5, 28), (33.8 + dx, 25.5)]
    for i, (px_, py_) in enumerate(path):
        r = 1.7 if i < 2 else 1.4
        c.oval(px_, py_ + dy, r, r, FUR, sh=0.1 - i * 0.06)
    c.set(int(33 + dx), int(24 + dy), FUR[0])                 # tip catchlight


def head_down(c, dy=0, dx=0, eyes="open", ears="up"):
    """The face. eyes: open (stern-sweet) / closed (^ ^) / happy / sad / hurt (>_<).
    ears: up / flat (hurt) / droop (sad)."""
    # ears (behind head): curved triangles w/ pink inner + tuft
    if ears == "up":
        c.tri((17 + dx, 1 + dy), 8 + dy, 14 + dx, 22 + dx, FUR)
        c.tri((31 + dx, 1 + dy), 8 + dy, 26 + dx, 34 + dx, FUR, sh=0.15)
        c.tri((17 + dx, 3 + dy), 7 + dy, 15 + dx, 20 + dx, EARIN)
        c.tri((31 + dx, 3 + dy), 7 + dy, 28 + dx, 33 + dx, EARIN_D)
    elif ears == "droop":                                     # slouched out + down (sad)
        c.tri((15 + dx, 4 + dy), 9 + dy, 13 + dx, 20 + dx, FUR)
        c.tri((33 + dx, 4 + dy), 9 + dy, 28 + dx, 35 + dx, FUR, sh=0.15)
    else:                                                     # flattened (hurt)
        c.tri((12 + dx, 6 + dy), 10 + dy, 15 + dx, 21 + dx, FUR)
        c.tri((36 + dx, 6 + dy), 10 + dy, 27 + dx, 33 + dx, FUR, sh=0.15)
    # skull: soft dome, CT-scaled (about a third of the figure)
    c.oval(24 + dx, 12.5 + dy, 8.8, 7.4, FUR, power=2.4)
    # plump white muzzle + NARROW blaze (his eyes sit in black fur, the white is a
    # thin stripe between them that fans out at the nose)
    c.oval(24 + dx, 17 + dy, 5.4, 3.2, WHITE, power=2.2)
    c.tri((24 + dx, 7 + dy), 14 + dy, 23 + dx, 25 + dx, WHITE)
    # fur ticks (cheek sheen)
    c.line([(17 + dx, 10 + dy), (18 + dx, 9 + dy)], FUR[0])
    c.line([(30 + dx, 9 + dy), (31 + dx, 10 + dy)], FUR[1])
    # nose smudge + cat mouth
    c.rect(23 + dx, 15 + dy, 25 + dx, 15 + dy, NOSE)
    c.set(23 + dx, 15 + dy, (52, 42, 48, 255))                # nose highlight
    if eyes == "hurt":
        c.rect(23 + dx, 17 + dy, 25 + dx, 18 + dy, MOUTH)     # little open wail
    elif eyes == "wince":
        c.rect(22 + dx, 17 + dy, 26 + dx, 17 + dy, MOUTH)     # gritted teeth
        c.set(24 + dx, 17 + dy, WHITE[0])
    elif eyes == "happy":
        c.rect(22 + dx, 16 + dy, 26 + dx, 18 + dy, (96, 54, 60, 255))   # open grin
        c.rect(23 + dx, 18 + dy, 25 + dx, 18 + dy, (226, 120, 128, 255))  # tongue
        c.set(18 + dx, 15 + dy, (238, 160, 158, 255))         # blush
        c.set(30 + dx, 15 + dy, (238, 160, 158, 255))
    elif eyes == "sad":
        c.line([(23 + dx, 17 + dy), (24 + dx, 16 + dy), (25 + dx, 17 + dy)], MOUTH)  # wobble frown
    else:
        c.set(24 + dx, 16 + dy, MOUTH)
        c.line([(22 + dx, 17 + dy), (23 + dx, 17 + dy)], MOUTH)
        c.line([(25 + dx, 17 + dy), (26 + dx, 17 + dy)], MOUTH)
    # whisker dots
    for wx, wy in ((20, 15), (19, 17), (28, 15), (29, 17)):
        c.set(wx + dx, wy + dy, WHISKD)
    # eyes: close-set, small CT read: yellow with a dark pupil + glint
    if eyes == "open":
        for ex in (19, 27):
            c.rect(ex + dx, 10 + dy, ex + 2 + dx, 12 + dy, EYE_Y)
            c.rect(ex + dx, 10 + dy, ex + 2 + dx, 10 + dy, EYE_YL)
            c.rect(ex + 1 + dx, 11 + dy, ex + 1 + dx, 12 + dy, PUPIL)
            c.set(ex + 1 + dx, 10 + dy, GLINT)
            c.set(ex + dx if ex == 19 else ex + 2 + dx, 9 + dy, FUR[3])  # stern brow
    elif eyes in ("closed", "happy"):                         # sweet ^ ^
        for ex in (19, 27):
            c.line([(ex + dx, 12 + dy), (ex + 1 + dx, 11 + dy),
                    (ex + 2 + dx, 12 + dy)], (188, 158, 66, 255))
    elif eyes == "sad":                                       # glossy, downcast, teary
        for ex in (19, 27):
            c.rect(ex + dx, 11 + dy, ex + 2 + dx, 13 + dy, EYE_Y)
            c.rect(ex + dx, 11 + dy, ex + 2 + dx, 11 + dy, FUR[2])     # heavy upper lid
            c.rect(ex + 1 + dx, 12 + dy, ex + 1 + dx, 13 + dy, PUPIL)
            c.set(ex + 1 + dx, 13 + dy, GLINT)                # low watery glint
            c.set(ex + 2 + dx, 12 + dy, GLINT)                # double shine = teary
        c.set(21 + dx, 9 + dy, FUR[0])                        # raised inner brows
        c.set(27 + dx, 9 + dy, FUR[0])
        c.set(19 + dx, 14 + dy, (170, 214, 250, 255))         # a welling tear
    else:                                                     # hurt / wince >_<
        for ex, s in ((19, 1), (29, -1)):
            c.set(ex + dx, 10 + dy, (188, 158, 66, 255))
            c.set(ex + s + dx, 11 + dy, (188, 158, 66, 255))
            c.set(ex + dx, 12 + dy, (188, 158, 66, 255))
    # goggles: rimmed lenses pushed up on the forehead + strap
    c.rect(16 + dx, 7 + dy, 32 + dx, 7 + dy, GOGRIM[2])
    c.line([(22 + dx, 4 + dy), (23 + dx, 4 + dy), (24 + dx, 4 + dy), (25 + dx, 4 + dy)], GOGRIM[1])
    for gx in (17, 26):
        c.oval(gx + 2.5 + dx, 5.5 + dy, 2.8, 2.4, GOGRIM, power=2.0)
        c.oval(gx + 2.5 + dx, 5.5 + dy, 1.7, 1.4, GOGLEN, power=2.0)
        c.set(gx + 1 + dx, 4 + dy, (252, 240, 214, 255))      # hard glint


def head_up(c, dy=0):
    """Back of head: dome, ear backs, goggle strap + buckle."""
    c.tri((17, 1 + dy), 8 + dy, 14, 22, FUR)
    c.tri((31, 1 + dy), 8 + dy, 26, 34, FUR, sh=0.15)
    c.tri((17, 3 + dy), 7 + dy, 15, 20, FUR, sh=0.35)
    c.tri((31, 3 + dy), 7 + dy, 28, 33, FUR, sh=0.45)
    c.oval(24, 12.5 + dy, 8.8, 7.4, FUR, power=2.4)
    c.rect(16, 7 + dy, 32, 8 + dy, GOGRIM[2])
    c.rect(16, 7 + dy, 32, 7 + dy, GOGRIM[1])
    c.rect(22, 7 + dy, 25, 8 + dy, GOGRIM[0])                 # buckle
    # neck fur part line
    c.line([(21, 18 + dy), (23, 19 + dy), (25, 19 + dy), (27, 18 + dy)], FUR[3])


def head_side(c, dy=0, dx=0, eyes="open", ears="up"):
    """Right-facing profile: snout, one small eye, goggles with one lens.
    dx shifts the whole head — the recoil lean-back."""
    if ears == "up":
        c.tri((19 + dx, 0 + dy), 7 + dy, 15 + dx, 23 + dx, FUR)
        c.tri((19 + dx, 2 + dy), 6 + dy, 17 + dx, 21 + dx, EARIN)
        c.tri((27 + dx, 1 + dy), 7 + dy, 24 + dx, 30 + dx, FUR, sh=0.3)   # far ear
    else:                                                     # swept back
        c.tri((13 + dx, 5 + dy), 9 + dy, 15 + dx, 21 + dx, FUR)
    c.oval(23 + dx, 12 + dy, 8.6, 7.0, FUR, power=2.4)        # skull
    c.oval(29 + dx, 14.5 + dy, 4.0, 3.4, FUR, power=2.0)      # snout mass
    c.oval(29.5 + dx, 15.5 + dy, 3.4, 2.6, WHITE, power=2.0)  # white muzzle
    c.rect(31 + dx, 13 + dy, 32 + dx, 13 + dy, NOSE)          # nose smudge
    c.set(30 + dx, 16 + dy, MOUTH); c.set(29 + dx, 17 + dy, MOUTH)
    c.set(27 + dx, 14 + dy, WHISKD); c.set(26 + dx, 16 + dy, WHISKD)
    if eyes == "open":
        c.rect(25 + dx, 9 + dy, 27 + dx, 11 + dy, EYE_Y)
        c.rect(25 + dx, 9 + dy, 27 + dx, 9 + dy, EYE_YL)
        c.rect(26 + dx, 10 + dy, 26 + dx, 11 + dy, PUPIL)
        c.set(26 + dx, 9 + dy, GLINT)
        c.set(28 + dx, 8 + dy, FUR[3])                        # brow
    elif eyes == "closed":
        c.line([(25 + dx, 11 + dy), (26 + dx, 10 + dy), (27 + dx, 11 + dy)], (188, 158, 66, 255))
    elif eyes == "wince":                                     # squeezed shut >
        c.set(25 + dx, 9 + dy, (188, 158, 66, 255))
        c.set(26 + dx, 10 + dy, (188, 158, 66, 255))
        c.set(25 + dx, 11 + dy, (188, 158, 66, 255))
        c.set(28 + dx, 8 + dy, FUR[3])                        # knit brow
    # goggles: strap + one lens on the forehead
    c.rect(16 + dx, 6 + dy, 30 + dx, 6 + dy, GOGRIM[2])
    c.oval(26 + dx, 4.5 + dy, 3.0, 2.4, GOGRIM, power=2.0)
    c.oval(26 + dx, 4.5 + dy, 1.8, 1.4, GOGLEN, power=2.0)
    c.set(25 + dx, 3 + dy, (252, 240, 214, 255))


def whiskers_down(c, dy=0, dx=0):
    """Whiskers breaking the silhouette (drawn after the outline): solid strokes
    off the cheeks, not dotted specks."""
    for pts in (((15, 16), (14, 16), (13, 17)),
                ((15, 18), (14, 19)),
                ((33, 16), (34, 16), (35, 17)),
                ((33, 18), (34, 19))):
        for (x, y) in pts:
            c.set(x + dx, y + dy, WHISK)


def whiskers_side(c, dy=0, dx=0):
    for pts in (((33, 14), (34, 14), (35, 15)),
                ((33, 17), (34, 17), (35, 18))):
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
        arms_hanging(c, bob, 0, -2)
        c.cloth(29, 27 + bob, 33, 30 + bob, GUNR, round_=0)   # gun at hip
        c.set(31, 28 + bob, GUNE)
    else:
        k = -2 if gun == "recoil" else 0                      # recoil kicks UP
        c.cloth(14, 23 + bob, 17, 28 + bob, COATR, round_=1, sh=0.1)
        c.cloth(30, 23 + bob, 33, 28 + bob, COATR, round_=1, sh=0.16)
        c.cloth(16, 28 + bob, 20, 31 + bob, COATR, round_=1, sh=0.1)
        c.cloth(27, 28 + bob, 31, 31 + bob, COATR, round_=1, sh=0.16)
        c.oval(23.5, 32 + bob + k, 3.2, 1.7, WHITE)           # gripping paws
        c.cloth(21, 33 + bob + k, 26, 36 + bob + k, GUNR, round_=1)
        c.cloth(22, 34 + bob + k, 25, 40 + bob + k, GUNR, round_=0)
        c.set(21, 34 + bob + k, GUNE); c.set(26, 34 + bob + k, GUNE)
        c.rect(22, 40 + bob + k, 25, 40 + bob + k, GUNP)
        c.rect(23, 41 + bob + k, 24, 41 + bob + k, GUNP)
    head_down(c, bob, head_dx, eyes, ears)
    c.outline()
    whiskers_down(c, bob, head_dx)


def cat_up(c, bob=0, lift_l=0, lift_r=0, swing=0, tail_dx=0, gun=None):
    legs_front(c, lift_l, lift_r)
    # coat back: straight flat panel, center seam, back belt
    top_y, hem_y = 20 + bob, 35 + bob
    for y in range(top_y, hem_y + 1):
        vy = (y - top_y) / (hem_y - top_y)
        half = 5.6 + vy * 1.6
        x0, x1 = int(round(24 - half)), int(round(23 + half))
        for x in range(x0, x1 + 1):
            hx = (x - x0) / max(1, x1 - x0)
            t = 0.26 + 0.22 * hx
            if x >= x1 - 1:
                t += 0.30
            elif x <= x0:
                t -= 0.10
            if y >= hem_y:
                t += 0.34
            c.set(x, y, c._pick(COATR, t, x, y))
    for y in range(top_y + 2, hem_y + 1):                     # back vent seam
        c.set(24, y, COATR[2])
    c.line([(19, 27 + bob), (20, 27 + bob), (27, 27 + bob), (28, 27 + bob)], COATR[3])
    c.rect(21, 26 + bob, 26, 27 + bob, COATR[1])              # back belt
    c.rect(18, top_y, 29, top_y + 1, COATR[1])                # collar band
    if gun is None:
        arms_hanging(c, bob, swing, -swing)
    else:
        arms_hanging(c, bob, 0, 0)
    tail_up_swish(c, tail_dx)
    head_up(c, bob)
    if gun is not None:                                       # raised gun over the head
        k = 1 if gun == "recoil" else 0
        if gun == "raise":
            c.oval(29.5, 10 + bob, 1.9, 1.9, WHITE)
            c.cloth(28, 5 + bob, 30, 8 + bob, GUNR, round_=0)
            c.set(29, 6 + bob, GUNE)
        else:
            c.oval(29.5, 8.5 + bob + k, 1.9, 1.9, WHITE)
            c.cloth(28, 2 + bob + k, 30, 6 + bob + k, GUNR, round_=0)
            c.set(29, 4 + bob + k, GUNE)
            c.rect(28, 1 + bob + k, 30, 1 + bob + k, GUNP)
    c.outline()


def tail_up_swish(c, dx=0):
    path = [(30, 32), (32, 30), (33, 27.5), (33.5 + dx * 0.5, 25), (33 + dx, 22.5)]
    for i, (px_, py_) in enumerate(path):
        c.oval(px_, py_, 1.6, 1.6, FUR, sh=0.12 - i * 0.05)
    c.set(int(32 + dx), 21, FUR[0])


def cat_side(c, bob=0, front_dx=0, back_dx=0, lift_f=0, lift_b=0, arm_dx=0,
             tail_dy=0, tail_raised=False, eyes="open", ears="up", gun=None):
    # Recoil throws the torso/head BACK while the feet skid FORWARD under him —
    # the classic braced-against-the-blast lean.
    lean = 2 if gun == "recoil" else 0
    tail_side(c, tail_dy, tail_raised or gun == "recoil")
    if gun == "recoil":
        front_dx += 3
        back_dx += 2
    for (x0, x1, dx_, lift) in ((17, 20, back_dx, lift_b), (25, 28, front_dx, lift_f)):
        c.cloth(x0 + dx_, 35 - lift, x1 + dx_, FEET - 3 - lift, PANTR, round_=0)
        c.oval((x0 + x1) / 2 + dx_, FEET - 1.6 - lift, 2.1, 1.7, WHITE)
    # coat in profile: straight panel with a trailing back hem; the lean tips the
    # shoulders further back than the hem
    top_y, hem_y = 20 + bob, 35 + bob
    for y in range(top_y, hem_y + 1):
        vy = (y - top_y) / (hem_y - top_y)
        x_off = -lean + int(round(vy * lean * 0.5))
        x0 = int(round(17 - vy * 2.5)) + x_off                # back hem trails
        x1 = 29 + x_off
        for x in range(x0, x1 + 1):
            hx = (x - x0) / max(1, x1 - x0)
            t = 0.26 + 0.22 * hx
            if x >= x1 - 1:
                t += 0.30
            elif x <= x0:
                t -= 0.10
            if y >= hem_y:
                t += 0.34
            c.set(x, y, c._pick(COATR, t, x, y))
        if y >= top_y + 2:                                    # coat front edge
            c.set(x1 - 1, y, COATR[3])
    if gun is None:
        c.cloth(21 + arm_dx, 22 + bob, 24 + arm_dx, 28 + bob, COATR, round_=1, sh=0.14)
        for y in range(23 + bob, 29 + bob):                   # sleeve seam
            c.set(24 + arm_dx, y, COATR[3])
        c.rect(21 + arm_dx, 28 + bob, 24 + arm_dx, 28 + bob, COATR[3])   # cuff
        c.oval(22.5 + arm_dx, 30 + bob, 2.0, 2.0, WHITE)
    else:
        k = 2 if gun == "recoil" else 0                       # arm shoved back...
        r = 2 if gun == "recoil" else 0                       # ...barrel kicked up
        if gun == "raise":
            c.cloth(23, 21 + bob, 28, 24 + bob, COATR, round_=1, sh=0.1)
            c.oval(30, 22.5 + bob, 1.9, 1.9, WHITE)
            c.cloth(29, 17 + bob, 32, 21 + bob, GUNR, round_=0)
            c.set(30, 19 + bob, GUNE)
        else:
            c.cloth(24 - k, 22 + bob, 30 - k, 25 + bob, COATR, round_=1, sh=0.1)
            c.oval(32 - k, 24.5 + bob - r * 0.5, 1.9, 1.9, WHITE)
            c.cloth(33 - k, 22 + bob - r, 38 - k, 25 + bob - r, GUNR, round_=1)
            c.cloth(34 - k, 26 + bob - r, 36 - k, 27 + bob - r, GUNR, round_=0)
            c.set(35 - k, 23 + bob - r, GUNE); c.set(36 - k, 23 + bob - r, GUNE)
            c.rect(39 - k, 22 + bob - r, 40 - k, 23 + bob - r, GUNP)
    head_side(c, bob, -lean, eyes, ears)
    c.outline()
    whiskers_side(c, bob, -lean)


def tail_side(c, dy=0, raised=False):
    if raised:
        path = [(16, 27), (14.5, 24.5), (13.5, 22), (13.5, 19.5)]
    else:
        path = [(16, 29), (14.5, 27.5), (13, 26.5), (11.5, 25)]
    for i, (px_, py_) in enumerate(path):
        c.oval(px_, py_ + dy, 1.7, 1.7, FUR, sh=0.15 - i * 0.05)
    tx, ty = path[-1]
    c.set(int(tx) - 1, int(ty) - 2 + dy, FUR[0])


# ---- build the sheet -------------------------------------------------------------
cells = [[Cell() for _ in range(COLS)] for _ in range(ROWS)]

walk_bob   = [0, -1, 0, 0, -1, 0]
walk_liftl = [2, 1, 0, 0, 0, 0]
walk_liftr = [0, 0, 0, 2, 1, 0]
walk_swing = [1, 0, 0, -1, 0, 0]
walk_tail  = [0, 1, 2, 2, 1, 0]
for i in range(6):
    cat_down(cells[0][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
             walk_swing[i], walk_tail[i])
    cat_up(cells[1][i], walk_bob[i], walk_liftl[i], walk_liftr[i],
           walk_swing[i], walk_tail[i])

side_front = [3, 1, 0, -3, -1, 0]
side_back  = [-3, -1, 0, 3, 1, 0]
side_liftf = [1, 0, 0, 0, 1, 0]
side_liftb = [0, 1, 0, 1, 0, 0]
side_bob   = [0, 0, -1, 0, 0, -1]
side_arm   = [-2, -1, 0, 2, 1, 0]
side_tail  = [0, -1, -1, 0, 1, 1]
for i in range(6):
    cat_side(cells[2][i], side_bob[i], side_front[i], side_back[i],
             side_liftf[i], side_liftb[i], side_arm[i], side_tail[i])

for i, g in enumerate(("raise", "aim", "recoil", "aim")):
    rc = g == "recoil"
    # Recoil frame: body shoved back off the muzzle, feet braced forward, ears
    # pinned, eyes squeezed in a wince — the shot should look like it KICKS.
    cat_down(cells[3][i], gun=g, bob=(-2 if rc else 0), spread=(1 if rc else 0),
             eyes=("wince" if rc else "open"), ears=("flat" if rc else "up"))
    cat_up(cells[4][i], gun=g, bob=(1 if rc else 0))
    cat_side(cells[5][i], gun=g, bob=(-1 if rc else 0),
             eyes=("wince" if rc else "open"), ears=("back" if rc else "up"))

cat_down(cells[6][0], eyes="hurt", ears="flat", head_dx=-1, tail_dx=2)
cat_down(cells[6][1], eyes="hurt", ears="flat", head_dx=1, tail_dx=0)
cat_down(cells[6][2], eyes="closed")
cat_side(cells[6][3], tail_raised=True)
cat_down(cells[6][4], eyes="happy", tail_dx=2)               # his sweet face
cat_down(cells[6][5], eyes="sad", ears="droop")              # his heartbroken face

# ---- write PNG --------------------------------------------------------------------
W, H = COLS * CELL, ROWS * CELL
buf = bytearray(W * H * 4)
for r in range(ROWS):
    for ci in range(COLS):
        cell = cells[r][ci]
        for y in range(CELL):
            for x in range(CELL):
                p = cell.px[y][x]
                if p:
                    o = ((r * CELL + y) * W + (ci * CELL + x)) * 4
                    buf[o:o + 4] = bytes(p)

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += buf[y * W * 4:(y + 1) * W * 4]

def chunk(tag, data):
    c = tag + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

open(os.path.join(HERE, "basil_gen.png"), "wb").write(
    b"\x89PNG\r\n\x1a\n"
    + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 6, 0, 0, 0))
    + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    + chunk(b"IEND", b""))
print(f"wrote basil_gen.png ({W}x{H})")
