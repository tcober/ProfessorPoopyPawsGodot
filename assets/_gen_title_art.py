#!/usr/bin/env python3
"""The TITLE SCREEN backdrop — one 384x216 painting (a one-off set, like
accident_bg): an autumn beechwood corridor, from the user's own sketch. Thick
near trunks frame a leaf-drifted ride that runs straight at a bright vanishing
point; the canopy is clumped gold with the light burning through it, the floor
is a crimson carpet, and the title is stamped down the left in the game's own
pixel font at 4x — cream, flat, with a dark warm outline so it survives the
foliage behind it.

What the first cut got wrong, kept here so it stays wrong only once: thin
pole-trunks read as a fence, not a wood — the sketch's trees are 24-40px
COLUMNS and the two biggest live at the frame's edges, half out of shot; a
canopy painted as one field with small mottle is a yellow WALL — it needs
lobes at r3-8 with real band contrast over a darker base, and it must CLOSE
OVER the trunk tops (foliage drawn in front, denser toward y=0) or every tree
reads as a post nailed to the sky; and the far wood's foot wants red FOLIAGE
lobes straddling the horizon, not a hard shade band, which reads as a wall.

Palette law: the GOLD field with the CRIMSON accent, darks violet-shifted, no
mud. Basil himself is not in the painting: the title scene stands his real
walk_down sprite on the ride, so the opening screen is the game's actual art,
not a poster of it. Falling leaves are runtime too (scene/title.gd).
"""
import os

from _core import Img, h2
from _pixfont import draw_text

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 384, 216
VP = (222, 104)                     # the corridor's vanishing point

# ---- the cast of colors ---------------------------------------------------------
LIGHT2 = (254, 242, 190, 255)       # the burn at the corridor's mouth
LIGHT = (252, 230, 148, 255)
GOLD_L = (240, 200, 102, 255)
GOLD = (220, 170, 76, 255)
GOLD_D = (192, 132, 56, 255)
DEEP = (156, 96, 50, 255)           # canopy at the frame's corners
UNDER = (124, 70, 48, 255)          # the dark ground the lobes sit on
RUST = (182, 84, 44, 255)           # the mid-distance red trees
CARP_L = (212, 102, 54, 255)        # the leaf carpet
CARP = (174, 66, 44, 255)
CARP_D = (128, 42, 44, 255)
POOL_L = (238, 150, 80, 255)        # light lying on the ride
POOL = (198, 104, 60, 255)
BARK_L = (128, 78, 68, 255)         # near trunks
BARK = (78, 46, 56, 255)
BARK_D = (48, 28, 42, 255)
FAR_BARK = (150, 92, 60, 255)       # hazed against the glow
CREAM = (242, 230, 172, 255)        # the title
INK = (74, 32, 40, 255)             # its outline/shadow

FIELD = [LIGHT, GOLD_L, GOLD, GOLD_D, DEEP]


def meander(v, salt, amp):
    a = h2(v // 16, salt, 3) / 255.0
    b = h2(v // 16 + 1, salt, 3) / 255.0
    return int(round((a + (b - a) * ((v % 16) / 16.0)) * amp))


def horizon(x):
    """Where the carpet meets the far wood — an arc off the vanishing point."""
    return VP[1] + 8 + int(abs(x - VP[0]) * 0.16) + meander(x, 71, 6)


def glow_d(x, y):
    return ((x - VP[0]) ** 2 + ((y - VP[1]) * 1.25) ** 2) ** 0.5


def field_band(x, y):
    """Radial glow: 0 at the vanishing point, 4 at the frame corners."""
    d = glow_d(x, y)
    for i, thr in enumerate((40, 88, 156, 240)):
        if d < thr:
            return i
    return 4


def main():
    img = Img(W, H)

    def lobe(cx_, cy_, r, c, lit):
        """A leaf mass is a solid PATCH with a lit crown — never a line."""
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            for dx in range(-half, half + 1):
                img.put(cx_ + dx, cy_ + dy, lit if dy < -r * 0.45 else c)

    # ---- base: dark under-canopy above the horizon, the carpet below -----------
    for y in range(H):
        cx = VP[0] + int((y - VP[1]) * 0.16)          # the ride bends right a hair
        hw = 4 + max(0, y - VP[1]) * 0.62             # its half-width, opening south
        for x in range(W):
            m = h2(x // 3, y // 3, 5)
            if y < horizon(x):
                band = field_band(x, y)
                # the glow's two inner rings stay luminous; everything else is
                # painted DARK so the lobe pass reads as lit clumps over depth
                img.put(x, y, FIELD[band] if band < 2 else UNDER)
            else:
                jit = hw * (0.75 + h2(x // 5, y // 4, 31) / 255.0 * 0.5)
                dx = abs(x - cx)
                if dx < jit * 0.6:
                    c = POOL_L if m > 118 else POOL
                elif dx < jit:
                    c = POOL if m > 150 else (CARP_L if m > 60 else CARP)
                else:
                    c = CARP_D if m < 36 else (CARP_L if m > 208 else CARP)
                img.put(x, y, c)
                if h2(x, y, 9) < 7:                              # gold strays
                    img.put(x, y, GOLD_D)
                    img.put(x + 1, y, GOLD_D)

    # ---- the canopy: clumped lobes over the dark base --------------------------
    def lobe_field(y_lo, y_hi, step, salt, keep_glow, ramp=False):
        for gy in range(y_lo, y_hi, step):
            for gx in range(-8, W + 8, step):
                if ramp:                          # front pass: dense at the top
                    keep = max(12, 235 - gy * 3)
                    if h2(gx, gy, salt + 9) > keep:
                        continue
                elif h2(gx, gy, salt + 9) > 210:  # back pass: mostly solid
                    continue
                jx = gx + h2(gx, gy, salt) % 13 - 6
                jy = gy + h2(gx, gy, salt + 1) % 9 - 4
                if jy >= horizon(jx) - 3:
                    continue
                if keep_glow and glow_d(jx, jy) < 52 + h2(jx, jy, 4) % 16:
                    continue                      # the light window stays open
                band = field_band(jx, jy)
                band = min(4, max(0, band + (1, 0, 0, -1)[h2(jx, jy, 6) % 4]))
                r = 3 + h2(jx, jy, salt + 2) % 5
                lobe(jx, jy, r, FIELD[band], FIELD[max(0, band - 1)])

    lobe_field(0, 150, 7, 11, True)

    # the mid-distance red trees: crimson foliage straddling the far wood's
    # foot, thinning to nothing at the bright mouth — the carpet grows out of
    # them instead of meeting a wall
    for gx in range(-8, W + 8, 6):
        for k in range(3):
            jx = gx + h2(gx, k, 61) % 11 - 5
            hy = horizon(jx)
            jy = hy - 12 + h2(gx, k, 62) % 15
            if glow_d(jx, jy) < 64 + h2(jx, k, 63) % 12:
                continue
            c = (RUST, CARP, CARP_L)[h2(gx, k, 64) % 3]
            lobe(jx, jy, 2 + h2(gx, k, 65) % 3, c, RUST if c == CARP else CARP_L)

    # ---- trunks: two great edge columns, ranked inward to the light ------------
    def trunk(fx, w, foot, lit_right, haze=False):
        top_w = max(2, int(w * 0.72))
        body, dark, litc = (FAR_BARK, BARK, GOLD_D) if haze \
            else (BARK, BARK_D, BARK_L)
        top = max(0, foot - int(w * 14))
        for y in range(top, min(foot, H)):
            t = (y - top) / max(1.0, float(foot - top))
            half = (top_w + (w - top_w) * t) / 2.0
            flare = (12 - (foot - y)) // 4 if foot - y < 12 else 0
            c = fx + meander(y, fx & 63, 4) - 2
            x0 = int(c - half) - flare
            x1 = int(c + half) + flare
            for x in range(x0, x1 + 1):
                # bark: vertical streaks keyed to the trunk's OWN column so
                # they ride its meander instead of shearing off it
                s = h2(x - c, y // 6, fx & 31)
                img.put(x, y, dark if s < 64 else (body if s < 236 else litc))
            if lit_right:
                img.rect(x1 - 1, y, x1, y, litc)
                img.put(x0, y, dark)
            else:
                img.rect(x0, y, x0 + 1, y, litc)
                img.put(x1, y, dark)

    farers = ((206, 4, 130), (240, 5, 133), (176, 6, 146), (258, 7, 150))
    for (fx, w, foot) in farers:
        trunk(fx, w, foot, fx < VP[0], haze=True)
    nears = ((150, 10, 174), (98, 16, 200), (30, 27, 216 + 14),
             (262, 11, 172), (300, 18, 198), (352, 29, 216 + 16))
    for (fx, w, foot) in nears:
        trunk(fx, w, foot, fx < VP[0])

    # leaf mounds burying every visible foot — a trunk standing ON the carpet
    for (fx, w, foot) in farers + nears:
        if foot > H:
            continue
        for k in range(6):
            mx = fx + h2(fx, k, 21) % (w + 10) - (w + 10) // 2
            my = min(H - 2, foot - 2 + h2(fx, k, 22) % 5)
            c = (CARP_L, CARP, GOLD_D)[h2(fx, k, 24) % 3]
            lobe(mx, my, 2 + h2(fx, k, 23) % 3, c, CARP_L if c != CARP_L else POOL_L)

    # ---- foliage IN FRONT: the canopy closes over every trunk's top ------------
    lobe_field(0, 108, 7, 41, False, ramp=True)
    for (cx_, cy_) in ((16, 96), (368, 100), (64, 46), (326, 52), (198, 20)):
        for k in range(8):                       # crimson accent clusters
            jx = cx_ + h2(cx_, k, 51) % 29 - 14
            jy = cy_ + h2(cx_, k, 52) % 21 - 10
            lobe(jx, jy, 2 + h2(cx_, k, 53) % 3, CARP, RUST)

    # ---- the title, stamped in the game's own font at 4x -----------------------
    rows = (("PROFESSOR", 12, 10), ("POOPY", 12, 54), ("PAWS", 12, 98))
    for (word, tx, ty) in rows:
        for (ox, oy) in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2),
                         (-2, 2), (2, 2), (3, 3), (4, 4)):
            draw_text(img.put, word, tx + ox, ty + oy, INK, 4)
    for (word, tx, ty) in rows:
        draw_text(img.put, word, tx, ty, CREAM, 4)

    img.save(os.path.join(HERE, "title_bg.png"))
    print("title_bg.png  384x216")


if __name__ == "__main__":
    main()
