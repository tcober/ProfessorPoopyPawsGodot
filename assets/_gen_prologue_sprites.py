#!/usr/bin/env python3
"""Prologue A cast — every sprite the childhood chapter needs, built fresh on
the _sprites.py kit (2026-07-12; nothing recovered from the deleted intro).
TRUE SNES density: 48x48 cells, flat 4-tone shading, hard band edges
(jitter=0), every pixel deliberate. Kid figures are ~29px with CT-kid
proportions — the head is nearly half the figure.

Sheets written (all 48px cells, feet baseline y=44 = _core.ZONE_FEET):

  kid_basil_gen.png (288x288, 6x6) — the PLAYABLE kid, matching
      entities/kid/kid_basil_frames.tres:
      row0 walk_down(6)  row1 walk_up(6)  row2 walk_side(6, faces RIGHT)
      row3 hurt(2) + idle-down blink + idle-side tail-flick + happy + sad
      row4 sleep + wake + sigh (the fest sunrise wake-up cutscene) + 3 spare
      row5 climb_up(4) + 2 spare — the rope-ladder climb, the same clip the
      adult sheet carries on its row 10
      (walk f0 per facing is the planted idle pose, same contract as the
      adults' sheets)

  ONE-ROW NPC sheets (entities/npcs/npc.gd builds SpriteFrames at runtime:
  [idle0, idle1, act0, act1, emote0, emote1] — ALL cast sheets carry the
  emote pair since 2026-07-17, so the hall gallery can laugh; spawn them
  with frame_cols = 6):
      npc_sage_gen.png        (480x48) — Basil's little sister: slate-lavender
          kitten, white socks, sage-green hair bow; act = ribbon-CAST (arms
          up), emote = smug giggle; cols 6-9 = BACK x2 + SIDE x2 (the bow
          between the ear backs; the crown loop breaks the profile)
      npc_schweinler_gen.png  (480x48) — the pig, kid-sized: stout pink,
          red neckerchief; act = POINT, emote = belly laugh; cols 6-9 =
          BACK x2 (flop-ear backs + the curly tail coiled on the rump) +
          SIDE x2 (the snout is the read)
      npc_kitty_gen.png       (480x48) — Kitty Cool: ginger-cream maker girl,
          teal bandana, grease smudge; act = TINKER crouch, emote = beaming;
          cols 6-9 = BACK x2 (the bandana knot at the nape) + SIDE x2
          (kerchief at the throat + the smudge on the cheek she IS showing)
      npc_kitty_adult_gen.png (480x48) — college-age Kitty (the bluff
          romance + her fountain-rim stall): same fur/bandana/smudge grown
          to the adult body, waxed-canvas work apron; act = TINKER (paws up
          at the work), emote = the beam-whoop (arms flung); cols 6-9 =
          BACK x2 + SIDE x2 (the bluff's from-behind staging — npc.gd
          builds them only when frame_cols >= 8/10)
      npc_sheep_gen.png       (384x48) — wool-cloud matron; act = talk nod;
          cols 6-7 = BACK x2 (the hall's tiered gallery, 2026-07-18)
      npc_owl_gen.png         (288x48) — the know-it-all owl; act = lecturing
          wing
      npc_goose_gen.png       (288x48) — the chaos goose; act = honk
      npc_mouse_gen.png       (384x48) — the mouse kid; act = wave; cols
          6-7 = BACK x2
      npc_fuji_gen.png        (480x48) — Fuji, the librarian (the Ebb night):
          canonical tortoiseshell design from _gen_fuji_sprites.py redrawn on
          the NPC contract; act = WAND CAST (slim brass wand, glass bead tip),
          emote = STARTLED (ears pinned, shoulders up); cols 6-7 = BACK x2,
          cols 8-9 = SIDE x2 (left profile — play_side(true) faces her east);
          spawn with frame_cols = 10
  SEVEN WALKING NPC sheets (480x192, 10 cols x 4 rows) — five from the
  2026-07-29 pass, plus the two thesis-day bystanders on 2026-07-30.
  Row 0 is the ordinary 10-cell pose row above; rows 1-3 are the WALK:
      row 1  walk_down x6   row 2  walk_up x6   row 3  walk_side x6 (LEFT)
  each padded out to 10 cells (write_cells wants a square grid). Frame 0 of the
  down and up rows is the planted neutral pose, so it is byte-identical to row-0
  cells 0 and 6; the stride tables are kid Basil's, verbatim — a SHUFFLE, not a
  churn (the stepping paw lifts 1px, both paw tips stay visible under the hem),
  no hem sway in the down/up views, and a flat ~8px scissor in the side:
      npc_hare_gen.png        (480x192) — Bramble, the flustered snow hare
          (Lanternwood, the Ebb night): blue-white fur, long upright ears,
          russet knit scarf; act = the dead warming-wand held up to one long
          ear, emote = paws thrown up, ears crossed back; cols 6-9 = BACK x2
          (ear backs + THE COTTONTAIL, which is the whole read from behind) +
          SIDE x2 (a short rounded snout — run long it read as a duck's bill)
      npc_beaver_gen.png      (480x192) — Alder, the elderly beaver
          woodworker: quilted steel-blue coat, amber knit cap, paddle tail;
          act = peering at the dead charm-stone at arm's length, emote =
          scratching under the cap, tail pressed flat; cols 6-9 = BACK x2 (the
          paddle DRAGGED out past the coat's edge — hung straight down it sat
          inside the silhouette and read as dirt) + SIDE x2 (the ear rides
          below the cap brim and behind the skull, or the knit eats it)
      npc_mom_gen.png         (480x192) — Basil's mother: rosewood-brown
          matron, white flour-dusted apron, sage headscarf; act = dusting
          flour off her paws, emote = the warm look; cols 6-9 = BACK x2 (the
          scarf knot on the nape and the apron straps CROSSING her back to the
          waist bow) + SIDE x2 (the apron as a tapered panel — a flat
          rectangle down the profile read as a sheet of paper pinned to her)
      npc_foxkid_gen.png      (480x192) — Pip, the fox kid: rust fur, cream
          muzzle/tail-tip, frost-blue bobble hat + mittens; act = shaking
          the dark glow-marble, emote = thrilled-AND-scared, tail bristled;
          cols 6-9 = BACK x2 (the brush drawn OVER his back, cream tip up) +
          SIDE x2. The brush also sways fore/aft across the walk — it is his
          silhouette, and a still brush on a moving kit reads as a prop.
      npc_mayor_gen.png       (480x192) — MAYOR HOLLIS, the old elk who is
          Lanternwood's mayor and its clerk: broad asymmetric antlers with one
          tine snapped blunt, a brass CHAIN OF OFFICE, half-moon spectacles on
          a cord, an ink-stained hoof; act = WRITING (the ledger up, pencil at
          it, head bowed), emote = the civic hoof raised as if calling a
          motion; cols 6-9 = BACK x2 (the rack unobstructed, the asymmetry
          mirrored, the pale rump tuft in the coat vent) + SIDE x2 (the chain
          survives the profile). Spawn with frame_cols = 10.
      npc_schweinler_adult_gen.png (480x192) — the grown pig. Was SIX cells
          until 2026-07-30, when the accident set-piece needed him to cross to
          his machine instead of blinking onto it; cols 6-9 = BACK x2 (the
          waistcoat with no placket and no buttons, which is the whole
          difference from the front, plus the curly tail on the rump) +
          SIDE x2 (the placket and its brass run down the FRONT edge of the
          flank — at this size they are what says which way he faces)
      npc_badger_gen.png      (480x192) — Ridley. Was EIGHT cells (he had
          backs for the hall tiers but no profile) until the same pass; cols
          8-9 = SIDE x2. His face stripes run VERTICALLY in the front cell, so
          the profile carries ONE vertical band down the skull with the dark
          ear atop it — drawn as the real animal's horizontal nose-to-ear
          stripe he is a different creature, and 2px high he is a bird

  prologue_fx.png (256x32, TWO 16-cell rows of 16px cells) — row 0 FROZEN
      [ribbon_magenta, ribbon_gold, sparkle_small, sparkle_big, gear, spring,
      crank, whirligig_droop, whirligig_spin0, whirligig_spin1, bag, pawprint,
      bird, bird_wing_up, puddle, zzz]; row 1 [watch(16), poof(17), lines(18),
      kiss heart(19), magic spark(20), magic spark dim(21)]

Palette: derived 4-tone ramps via _palette.ramp() (violet shadow law), with
Basil's own identity ramps reused for the kid so he IS visibly the same cat.
Re-run: python3 assets/_gen_prologue_sprites.py
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import write_cells, Img, ZONE_CELL, h2
from _propkit import ln
from _sprites import Sprite
from _palette import BASIL, FUJI, ramp

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
MSPARK_W = (255, 255, 255, 255)                    # magic spark: white-hot heart
MSPARK = (214, 246, 248, 255)                      # mint-white body (the Ebb night)
MSPARK_V = (156, 112, 220, 255)                    # violet fringe (the violet law)
BURST_W = (255, 255, 255, 255)                     # firework: white-hot core
BURST_C = (255, 250, 236, 255)                     # firework: cream body
BURST_D = (226, 214, 190, 255)                     # firework: dim outer specks

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


def whiskers_kid_side(s, dy=0):
    """Profile whiskers off the muzzle — drawn AFTER the finishing passes
    (despeckle eats lone specks; the sage sparkle rule)."""
    for (x, y) in ((31, 27), (32, 29)):
        s.set(x, y + dy, WHISK)


def _mirror_cell(s):
    """Flip a FINISHED cell horizontally: side cells are authored on the
    canonical RIGHT-facing geometry, the npc kit stores LEFT-facing cells
    (play_side(true) flips back east). Runtime-flipped profiles already
    forfeit the global light direction, so the mirrored shade bands are
    exactly as legal as npc.gd's own flip_h."""
    for row in s.px:
        row.reverse()


# ---- the kid cat's BACK and SIDE views -------------------------------------------------
# The npc kit's optional facings (cols 6-9) need a back and a left profile for
# every child in the cast. kid Basil's playable sheet already solved both for a
# kid cat, so those two cells ARE the shared cores (2026-07-29): kb_up / kb_side
# delegate here unchanged, and Kitty and Sage call the same geometry and hang
# their own accessory off the returned head anchor. Draw-only — the caller runs
# despeckle / outline / whiskers, because each character owns its own outline
# dict.


def kid_back(s, fur, paw, bob=0, liftL=0, liftR=0, tail_sway=0, reach=None):
    """The kid cat from BEHIND. Ear BACKS (no inner pink), hanging arms drawn
    under the skull so the nape reads, tail swishing up past the tummy, the
    neck part creased into the shoulders. Returns the head y.

    `reach` = (left, right) px above the shoulder swaps the hanging arms for
    RAISED ones — the ladder climb, the only pose that needs them. Each paw
    goes straight up and slightly OUT, to x = CX +/- 8, which is the same
    place kid_body_down's "up" arms put them and is just clear of the skull's
    silhouette. The adult's forearms CONVERGE on the rungs (see
    _gen_basil_sprites.arms_climb); a kid's head is nearly as wide as his
    shoulders, so converging arms are swallowed by it and the climb reads as
    a walk again — which is the whole thing this pose exists to stop."""
    kid_legs_down(s, fur, paw, liftL, liftR, bob)
    by = 36 + bob
    s.ball(CX, by, 5.8, 5.0, fur, power=2.2, wrap=0.30, curve=0.24)
    if reach is not None:
        s.capsule(CX - 5.5, by - 3, CX - 8, by - 3 - reach[0], 1.7, 1.5, fur, sh=0.06)
        s.capsule(CX + 5.5, by - 3, CX + 8, by - 3 - reach[1], 1.7, 1.5, fur, sh=0.16)
        s.ball(CX - 8, by - 4 - reach[0], 1.6, 1.4, paw, power=2.2,
               wrap=0.10, curve=0.10)
        s.ball(CX + 8, by - 4 - reach[1], 1.6, 1.4, paw, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
    else:
        s.capsule(CX - 5.5, by - 3, CX - 6.5, by + 1, 1.7, 1.5, fur, sh=0.06)
        s.capsule(CX + 5.5, by - 3, CX + 6.5, by + 1, 1.7, 1.5, fur, sh=0.16)
    # tail swishes up past the tummy, seen from behind
    s.capsule(CX + 5, by + 1, CX + 8, by - 4, 1.5, 1.2, fur, sh=0.10)
    s.set(CX + 8 + tail_sway, by - 5, fur[0])
    hy = 25 + bob
    kid_ears(s, fur, hy, inner=False)
    s.tri((CX - 5, hy - 8), hy - 5, CX - 6, CX - 4, fur, sh=0.40)
    s.tri((CX + 5, hy - 8), hy - 5, CX + 4, CX + 6, fur, sh=0.46)
    s.ball(CX, hy, 7.2, 6.4, fur, power=2.4, wrap=0.34, curve=0.30)
    s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
            (CX + 1, hy + 6), (CX + 2, hy + 5)], fur[3])       # neck part
    return hy


def kid_side(s, fur, belly, iris, iris_l, bob=0, fF=(0, 0), fB=(0, 0),
             tail_dy=0, eyes="open", tail_raised=False, earin=EARIN):
    """The kid cat in PROFILE, facing RIGHT. Tail off the rump behind, the
    front/back leg scissor pair planted on the feet line, the white bib and
    muzzle toward the front, near ear tall with the far ear peeking. Returns
    (hx, hy) so a caller can hang a bow or a kerchief off the head."""
    hx, hy = 23, 25 + bob
    # tail behind, off the rump
    if tail_raised:
        s.capsule(16, 36, 14, 30 + tail_dy, 1.5, 1.2, fur, sh=0.10)
    else:
        s.capsule(16, 37, 13, 34 + tail_dy, 1.5, 1.2, fur, sh=0.10)
    # legs: front/back scissor pair, paws on the feet line
    for (base_x, (dx, lift), sh) in (((20), fB, 0.14), ((26), fF, 0.0)):
        lx = base_x + dx
        s.capsule(lx, 38 + bob, lx, 42 - lift, 2.0, 1.7, fur, sh=sh)
        s.ball(lx + 0.5, 42.8 - lift, 2.1, 1.6, belly, power=2.2, sh=sh * 0.4,
               wrap=0.10, curve=0.10)
    # round tummy + white bib toward the front
    s.ball(23, 36 + bob, 5.4, 4.8, fur, power=2.2, wrap=0.30, curve=0.24)
    s.ball(25.5, 37 + bob, 2.8, 2.8, belly, power=2.2, wrap=0.10, curve=0.10)
    s.capsule(23, 33 + bob, 24, 37 + bob, 1.7, 1.5, fur, sh=0.10)   # near arm
    # head: near ear tall, far ear peeking
    s.tri((hx + 4, hy - 9), hy - 4, hx + 2, hx + 6, fur, sh=0.26)
    s.tri((hx - 1, hy - 10), hy - 4, hx - 3, hx + 1, fur)
    s.tri((hx - 1, hy - 8), hy - 5, hx - 2, hx, earin)
    s.ball(hx, hy, 6.8, 6.0, fur, power=2.4, wrap=0.34, curve=0.30)
    s.ball(hx + 4.5, hy + 3.4, 4.0, 2.5, belly, power=2.0, wrap=0.10, curve=0.10)
    s.rect(hx + 7, hy + 2, hx + 8, hy + 2, NOSE)
    if eyes == "open":
        _eye(s, hx + 2, hy - 3, iris, iris_l)
        s.line([(hx + 6, hy + 4), (hx + 7, hy + 4)], MOUTH)
    elif eyes == "blink":
        _closed(s, hx + 2, hy - 3, happy=False)
        s.line([(hx + 6, hy + 4), (hx + 7, hy + 4)], MOUTH)
    else:
        _wince(s, hx + 2, hy - 3)
        s.rect(hx + 6, hy + 4, hx + 7, hy + 5, MOUTH)
    return hx, hy


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
    kid_back(s, FUR, WHITE, bob, liftL, liftR, tail_sway)
    kb_finish(s)


def kb_climb(s, step):
    """THE LADDER CLIMB — back view, four frames, opposite limbs together.

    The same clip the adult sheet grew on 2026-07-30 (row 10 there), cut for the
    kid rig: Alembic's great trees are reached by rope ladder, and a body without
    this row falls back to `walk_up` — arms at its sides, feet strolling — which
    reads as a cat sliding up the rungs.

    Contralateral, like the walk cycle already is: left paw high with the RIGHT
    foot lifted. Frames 0 and 2 are the two reaches, 1 and 3 the passing
    positions, so the cycle reads at 8fps with no hitch frame. Cell 0 is
    deliberately NOT a planted neutral — there is no neutral on a ladder, and the
    clip only ever plays on one.

    The kid's foot lift is 2px where the adult's is 5: his round tummy hangs
    lower than a coat hem, and anything above 2 puts the paw behind it, which
    costs the frame its only visible leg action."""
    hi = (6, 4, 6, 4)[step]                 # the high paw's reach above the shoulder
    lo = (2, 4, 2, 4)[step]                 # ...and the low one's
    left_high = step in (0, 1)
    rl, rr = (hi, lo) if left_high else (lo, hi)
    liftL, liftR = (0, 2) if left_high else (2, 0)
    bob = -1 if step in (0, 2) else 0
    kid_back(s, FUR, WHITE, bob, liftL, liftR, 1 if left_high else -1,
             reach=(rl, rr))
    kb_finish(s)


def kb_side(s, bob=0, fF=(0, 0), fB=(0, 0), tail_dy=0, eyes="open",
            tail_raised=False):
    """Side view, faces RIGHT (flip_h in code for left)."""
    kid_side(s, FUR, WHITE, EYE_Y, EYE_YL, bob, fF, fB, tail_dy, eyes,
             tail_raised)
    kb_finish(s)
    whiskers_kid_side(s, bob)


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


def sage_back(s, bob=0, sway=0):
    """Sage from behind (2026-07-29). The bow is a GIFT from this angle — it is
    tied over her west ear, so from the back it sits between the ear backs
    where nothing occludes it, and the two ribbon tails fall down the nape.
    The front cell's knot/loop mirrored, one tone brighter so the sage green
    still separates from the slate-lavender crown."""
    hy = kid_back(s, SAGE_FUR, WHITE, bob, tail_sway=sway)
    # BETWEEN the ears, and only between them: at CX +- 4 the bow starts eating
    # the ear backs and the whole crown reads as a blank blob with a green bar.
    s.rect(CX - 3, hy - 7, CX + 3, hy - 6, SAGE_BOW[1])     # band across the crown
    s.rect(CX - 3, hy - 8, CX - 1, hy - 5, SAGE_BOW[0])     # west loop
    s.rect(CX + 1, hy - 8, CX + 3, hy - 5, SAGE_BOW[1])     # east loop
    s.set(CX - 2, hy - 7, SAGE_BOW[2])                      # loop hollows
    s.set(CX + 2, hy - 7, SAGE_BOW[2])
    s.rect(CX, hy - 8, CX, hy - 5, SAGE_BOW[2])             # the knot pinch
    s.set(CX - 1, hy - 4, SAGE_BOW[2])                      # tails down the nape
    s.set(CX + 1, hy - 4, SAGE_BOW[2])
    s.despeckle(passes=1)
    s.outline(SAGE_OUTS, OUT_DARK)
    s.crease([(CX + 4, hy + 10), (CX + 5, hy + 9)], SAGE_FUR[3])   # tail root


def sage_side(s, bob=0):
    """Sage in profile. The bow perches on the crown behind the near ear and
    breaks the top silhouette, so the profile is unmistakably hers; ribbon
    tails trail off the back of the skull."""
    hx, hy = kid_side(s, SAGE_FUR, WHITE, SAGE_EYE, SAGE_EYEL, bob)
    # the bow perched on the BACK of the crown, its loop poking past the skull
    # so it breaks the silhouette — on top of the head it hides behind the ears
    s.rect(hx - 4, hy - 6, hx - 2, hy - 4, SAGE_BOW[1])     # the knot
    s.rect(hx - 8, hy - 7, hx - 5, hy - 3, SAGE_BOW[0])     # the loop, swept back
    s.rect(hx - 7, hy - 6, hx - 6, hy - 5, SAGE_BOW[2])     # loop hollow
    s.set(hx - 5, hy - 2, SAGE_BOW[2])                      # trailing tails
    s.set(hx - 6, hy - 1, SAGE_BOW[2])
    s.despeckle(passes=1)
    s.outline(SAGE_OUTS, OUT_DARK)
    whiskers_kid_side(s, bob)
    _mirror_cell(s)


# ---- Kitty Cool ---------------------------------------------------------------------------

KIT_OUTS = outs_for((KIT_FUR, OUT_DARK), (WHITE, OUT_LIGHT), (KIT_BAND, OUT_DARK))


def kitty_bandana(s, hy):
    """Teal kerchief knotted at her throat."""
    s.rect(CX - 4, hy + 7, CX + 4, hy + 8, KIT_BAND[1])
    s.rect(CX + 1, hy + 8, CX + 4, hy + 8, KIT_BAND[2])
    s.tri((CX, hy + 11), hy + 8, CX - 2, CX + 2, KIT_BAND, sh=0.14)


def kitty(s, eyes="open", pose="stand", bob=0, sway=0):
    if pose == "tinker":
        # crouched over the work: body/head sink, arms reach forward-down.
        # Feet stay PLANTED (legs dy=0) and the crouch is capped at 2 so the
        # reach-paws' bottom outline stays inside the cell (fill<=45, edge 46).
        bob += 2
        kid_tail_down(s, KIT_FUR, sway, tip=KIT_FUR[0])
        kid_legs_down(s, KIT_FUR, WHITE, 0, 0, 0)
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


def kitty_back(s, bob=0, sway=0):
    """Kid Kitty from behind (2026-07-29 — she is staged turning and walking
    all over Prologue A). The kerchief hangs at her throat, so from this side
    the teal band and its KNOT at the nape carry the whole read; the grease
    smudge is on the cheek she is not showing. Same trade the adult back cell
    makes."""
    hy = kid_back(s, KIT_FUR, WHITE, bob, tail_sway=sway)
    s.rect(CX - 4, hy + 7, CX + 4, hy + 8, KIT_BAND[1])     # band at the nape
    s.rect(CX - 4, hy + 8, CX - 2, hy + 8, KIT_BAND[2])
    s.rect(CX + 2, hy + 8, CX + 4, hy + 8, KIT_BAND[2])
    s.rect(CX - 1, hy + 7, CX + 1, hy + 9, KIT_BAND[0])     # the knot
    s.set(CX, hy + 8, KIT_BAND[2])                          # its pinch
    s.set(CX - 2, hy + 10, KIT_BAND[2])                     # knot tails
    s.set(CX + 2, hy + 10, KIT_BAND[2])
    s.despeckle(passes=1)
    s.outline(KIT_OUTS, OUT_DARK)
    s.crease([(CX + 4, hy + 10), (CX + 5, hy + 9)], KIT_FUR[3])    # tail root


def kitty_side(s, bob=0):
    """Kid Kitty in profile: the teal band round the throat with the kerchief
    triangle hanging down her front, and the grease smudge on the cheek she IS
    showing. (The kerchief hangs by explicit shrinking rows — Sprite.tri only
    draws apex-up, which is why the down cells' downward triangle never
    rendered.)"""
    hx, hy = kid_side(s, KIT_FUR, WHITE, KIT_EYE, KIT_EYEL, bob)
    s.set(hx - 2, hy + 1, SMUDGE)                   # some things do not wash off
    s.set(hx - 3, hy + 2, SMUDGE)                   # (on the LIT cheek band —
    s.set(hx - 2, hy + 2, SMUDGE)                   # against KIT_FUR[3] it went
    #                                                 invisible)
    s.rect(hx - 4, hy + 7, hx + 3, hy + 8, KIT_BAND[1])     # the band
    s.rect(hx - 4, hy + 8, hx - 2, hy + 8, KIT_BAND[2])
    s.rect(hx + 1, hy + 9, hx + 4, hy + 9, KIT_BAND[1])     # kerchief, hanging
    s.rect(hx + 2, hy + 10, hx + 4, hy + 10, KIT_BAND[2])
    s.set(hx + 3, hy + 11, KIT_BAND[2])
    s.despeckle(passes=1)
    s.outline(KIT_OUTS, OUT_DARK)
    whiskers_kid_side(s, bob)
    _mirror_cell(s)


# ---- kid Schweinler -------------------------------------------------------------------------

PIG_OUTS = outs_for((PIG, OUT_DARK), (SNOUT, OUT_DARK), (KERCH, OUT_DARK))


def _pig_curl(s, ox, oy, d=-1):
    """The curly tail as an explicit POST-outline squiggle carrying its own dark
    edge. A 1px zigzag is the only shape that reads as a corkscrew at 48px, and
    drawn before the finishing passes it is eaten — despeckle drops anything
    with fewer than two filled 4-neighbours and the path is diagonal. Coils of
    fat capsules don't work either: at r>1 they close up into a lump with no
    hole, which reads as a button on the rump. Same post-outline idiom as the
    hare's inert wand and Kitty's pinched gear. `d` = -1 west / +1 east."""
    squig = ((0, 0), (1, -1), (2, 0), (3, 1), (4, 0), (5, -1))
    for (sx, sy) in squig:
        for (ex, ey) in ((0, -1), (0, 1), (1, 0), (-1, 0)):
            if s.get(ox + (sx + ex) * d, oy + sy + ey) is None:
                s.set(ox + (sx + ex) * d, oy + sy + ey, OUT_DARK)
    for i, (sx, sy) in enumerate(squig):
        s.set(ox + sx * d, oy + sy, PIG[0] if i % 2 else PIG[1])


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


def schweinler_back(s, bob=0):
    """Kid Schweinler from behind (2026-07-29). A pig, so none of the kid-cat
    cores apply: the read is the two flop-ear BACKS hanging wider than the
    skull and the CURLY TAIL coiled on the rump, lit a tone up with a hard
    shadow under it so the coil reads as raised. No snout, no face, and only
    the kerchief's tie band and knot — the triangle hangs at his chest."""
    hy = 26 + bob
    # flop ears from behind: the outer faces, wider and flatter than the front
    s.tri((CX - 8, hy - 7), hy - 2, CX - 10, CX - 4, PIG, sh=0.30)
    s.tri((CX + 8, hy - 7), hy - 2, CX + 4, CX + 10, PIG, sh=0.38)
    s.ball(CX, hy, 7.6, 6.4, PIG, power=2.4, wrap=0.32, curve=0.28)
    s.ball(CX, 37 + bob, 7.0, 5.4, PIG, power=2.2, wrap=0.28, curve=0.22)
    s.capsule(CX - 6.5, 34 + bob, CX - 7.5, 38 + bob, 1.8, 1.5, PIG, sh=0.06)
    s.capsule(CX + 6.5, 34 + bob, CX + 7.5, 38 + bob, 1.8, 1.5, PIG, sh=0.16)
    for lx in (CX - 3, CX + 3):
        s.capsule(lx, 40 + bob, lx, 42, 2.0, 1.8, PIG, sh=0.08)
        s.rect(lx - 1, 43, lx + 1, 44, PIG[3])      # cloven trotter
    # the spine crease, so the back is not a blank pink oval
    for sy in range(hy + 9, 38 + bob):
        s.set(CX, sy, PIG[2])
    # the kerchief's tie band + knot at the nape. The knot reads by its DARK
    # pinch, not by being lighter: KERCH[0] is a pale pink and washes straight
    # into the pig
    s.rect(CX - 4, hy + 6, CX + 4, hy + 6, KERCH[1])
    s.rect(CX - 4, hy + 7, CX + 4, hy + 7, KERCH[2])
    s.rect(CX - 1, hy + 6, CX + 1, hy + 8, KERCH[1])            # the knot
    s.set(CX - 2, hy + 7, KERCH[3])                             # its pinch
    s.set(CX + 2, hy + 7, KERCH[3])
    s.set(CX, hy + 8, KERCH[3])
    s.despeckle(passes=1)
    s.outline(PIG_OUTS, OUT_DARK)
    _pig_curl(s, CX - 8, 36 + bob)                  # THE CURLY TAIL, west hip


def schweinler_side(s, bob=0):
    """Kid Schweinler in profile, facing RIGHT before the mirror. The SNOUT is
    the read — a blunt cylinder out past the cheek with its disc end and one
    nostril — under a flop ear draped forward over the eye. The curly tail
    coils off the rump behind him."""
    hy, by = 26 + bob, 37 + bob
    # -- trotters / the stout body --------------------------------------
    for (lx, sh) in ((20, 0.16), (26, 0.0)):
        s.capsule(lx, 39 + bob, lx, 42, 2.0, 1.8, PIG, sh=sh)
        s.rect(lx - 1, 43, lx + 1, 44, PIG[3])
    s.ball(23, by, 7.0, 5.4, PIG, power=2.2, wrap=0.28, curve=0.22)
    s.capsule(24, 34 + bob, 26, 38 + bob, 1.8, 1.5, PIG, sh=0.10)   # near arm
    # -- the far flop ear behind the skull ------------------------------
    s.tri((20, hy - 7), hy - 1, 16, 21, PIG, sh=0.36)
    # -- skull, then THE SNOUT ------------------------------------------
    s.ball(22, hy, 7.2, 6.2, PIG, power=2.4, wrap=0.32, curve=0.28)
    s.capsule(27, hy + 3, 31, hy + 3, 2.7, 2.4, SNOUT, sh=0.06)
    s.rect(32, hy + 1, 32, hy + 5, SNOUT[2])                # the disc end
    s.set(32, hy + 3, PIG_EYE)                              # one nostril
    s.set(31, hy + 5, SNOUT[3])
    # -- the near flop ear draped forward over the cheek ----------------
    s.tri((21, hy - 8), hy + 2, 24, 29, PIG, sh=0.16)
    s.rect(26, hy + 2, 28, hy + 3, PIG[2])                  # its heavy tip
    # -- eye under the ear + the smug brow ------------------------------
    s.rect(24, hy - 2, 25, hy - 1, PIG_EYE)
    s.set(24, hy - 2, GLINT)
    s.rect(23, hy - 4, 26, hy - 4, PIG[3])
    s.line([(29, hy + 6), (30, hy + 6)], MOUTH)             # the mouth line
    # -- the neckerchief: band round the throat, triangle hanging front --
    s.rect(19, hy + 7, 27, hy + 8, KERCH[1])
    s.rect(19, hy + 8, 21, hy + 8, KERCH[2])
    s.rect(25, hy + 9, 28, hy + 9, KERCH[1])
    s.rect(26, hy + 10, 28, hy + 10, KERCH[2])
    s.set(27, hy + 11, KERCH[2])
    s.despeckle(passes=1)
    s.outline(PIG_OUTS, OUT_DARK)
    _pig_curl(s, 17, 36 + bob)                      # the curly tail, behind him
    _mirror_cell(s)


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
    if mood == "back":
        # the gallery-from-behind cell (hall tiers, 2026-07-18): the wool
        # cloud wraps right over the head — ears peek, no face
        s.ball(CX, hy - 1, 5.0, 4.4, WOOL, power=2.0, wrap=0.18, curve=0.14)
    else:
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
    mode alternates the legs and rolls the hull (the ribbon-chase gait).
    `fly` mode is the AIRBORNE side profile (facing LEFT, the side-cell
    convention — the scene flips it east): hull centered ~y26, NOT the feet
    register y44 — the scene's tween owns the altitude, so art drawn at the
    ground register would swoop 12px low. `step` picks the wingbeat."""
    if mood == "fly":
        # stretched-out glide: neck level with the hull, legs tucked
        s.ball(CX + 2, 26, 7.4, 4.4, GOOSE, power=2.2, wrap=0.28, curve=0.22)
        s.capsule(CX + 8, 25, CX + 12, 23, 2.0, 1.4, GOOSE, sh=0.20)  # tail
        s.capsule(CX - 3, 25, CX - 10, 24, 2.2, 1.9, GOOSE, sh=0.06)  # neck
        s.ball(CX - 11, 24, 3.1, 2.7, GOOSE, power=2.2, wrap=0.20, curve=0.16)
        s.rect(CX - 15, 23, CX - 13, 24, BILL[1])
        s.set(CX - 15, 24, BILL[2])
        s.set(CX - 11, 23, PUPIL)
        if step == 0:                               # wings UP
            s.capsule(CX + 2, 24, CX + 5, 14, 2.8, 1.8, GOOSE, sh=0.12)
        else:                                       # wings swept DOWN
            s.capsule(CX + 2, 28, CX + 6, 35, 2.8, 1.8, GOOSE, sh=0.24)
        s.rect(CX + 3, 30, CX + 5, 31, BILL[1])     # tucked legs
        s.despeckle(passes=1)
        s.outline(GOOSE_OUTS, OUT_LIGHT)
        return
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

# 2026-07-29 less-kiddy pass (the overworld darker-pass recipe, _palette.py:177
# — lower L, keep or RAISE S, hold the hue lean, keep the violet darks). Her old
# (178,162,152) "warm gray" was S=0.14: a beige/gray MUD field, the ban in the
# palette doctrine, and it read like a plush toy. Committed to the hue instead —
# a rosewood-brown matron, S=0.24 at L=0.49 — with the spread up so the flat
# apron-and-fur silhouette gets real internal contrast.
MOM_FUR = ramp((156, 102, 94), "violet", 4, spread=1.1)     # rosewood matron
MOM_SCARF = ramp((88, 158, 78), "violet", 4, spread=1.1)    # the family sage-green
MOM_OUTS = outs_for((MOM_FUR, OUT_DARK), (WHITE, OUT_LIGHT), (MOM_SCARF, OUT_DARK))


def mom(s, mood="idle", bob=0, liftL=0, liftR=0):
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
    for (lx, lift) in ((CX - 3, liftL), (CX + 3, liftR)):   # paws under the hem
        s.ball(lx, 43 - lift, 2.1, 1.6, MOM_FUR, power=2.2, wrap=0.10,
               curve=0.10)
    # tail curled around her feet
    s.capsule(CX + 7, 41 + bob, CX + 10, 42 + bob, 1.5, 1.2, MOM_FUR, sh=0.10)
    s.despeckle(passes=1)
    s.outline(MOM_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob - 6)


def mom_back(s, bob=0, liftL=0, liftR=0):
    """Basil's mother from BEHIND (2026-07-29). The headscarf is the whole
    read: the band round the crown, its KNOT and two tied ends sitting on the
    nape. The apron is on the far side of her, so what shows is the pair of
    straps crossing her back down to the waist tie. Adult cat proportions —
    small skull on a heavy pear, not the kid dome."""
    hy, by = 22 + bob, 35 + bob
    s.tri((CX - 6, hy - 9), hy - 4, CX - 8, CX - 3, MOM_FUR, sh=0.28)
    s.tri((CX + 6, hy - 9), hy - 4, CX + 3, CX + 8, MOM_FUR, sh=0.36)
    for (lx, lift) in ((CX - 3, liftL), (CX + 3, liftR)):
        s.ball(lx, 43 - lift, 2.1, 1.6, MOM_FUR, power=2.2, sh=0.20, wrap=0.10,
               curve=0.10)
    s.capsule(CX + 7, 41 + bob, CX + 10, 42 + bob, 1.5, 1.2, MOM_FUR, sh=0.10)
    s.ball(CX, by, 7.4, 7.0, MOM_FUR, power=2.2, wrap=0.28, curve=0.22)
    # the apron STRAPS crossing her back, down to the waist tie and its bow —
    # 2px wide, because at 1px they read as scratches next to the chunky tie
    ln(s, CX - 4, by - 6, CX + 3, by + 1, WHITE[1])
    ln(s, CX - 3, by - 6, CX + 4, by + 1, WHITE[2])
    ln(s, CX + 4, by - 6, CX - 3, by + 1, WHITE[1])
    ln(s, CX + 3, by - 6, CX - 4, by + 1, WHITE[2])
    s.rect(CX - 5, by + 2, CX + 5, by + 2, WHITE[1])            # the waist tie
    s.rect(CX - 5, by + 3, CX + 5, by + 3, WHITE[2])
    s.rect(CX - 3, by + 4, CX - 2, by + 5, WHITE[0])            # the bow loops
    s.rect(CX + 2, by + 4, CX + 3, by + 5, WHITE[2])
    s.capsule(CX - 7, by - 4, CX - 8, by + 1, 1.8, 1.6, MOM_FUR, sh=0.16)
    s.capsule(CX + 7, by - 4, CX + 8, by + 1, 1.8, 1.6, MOM_FUR, sh=0.26)
    s.ball(CX - 8, by + 2, 1.7, 1.5, WHITE, power=2.2, sh=0.26, wrap=0.10,
           curve=0.10)
    s.ball(CX + 8, by + 2, 1.7, 1.5, WHITE, power=2.2, sh=0.36, wrap=0.10,
           curve=0.10)
    s.ball(CX, hy, 7.0, 6.2, MOM_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
            (CX + 1, hy + 6), (CX + 2, hy + 5)], MOM_FUR[3])    # nape part
    # the scarf: the band all the way round, the knot and its ends on the nape
    s.rect(CX - 6, hy - 6, CX + 6, hy - 4, MOM_SCARF[1])
    s.rect(CX - 6, hy - 4, CX + 6, hy - 4, MOM_SCARF[2])
    s.rect(CX + 5, hy - 5, CX + 7, hy - 2, MOM_SCARF[0])        # the knot
    s.rect(CX + 6, hy - 2, CX + 8, hy + 2, MOM_SCARF[1])        # the tied ends
    s.rect(CX + 8, hy - 2, CX + 8, hy + 2, MOM_SCARF[2])
    s.despeckle(passes=1)
    s.outline(MOM_OUTS, OUT_DARK)


def mom_side(s, bob=0, fF=(0, 0), fB=(0, 0)):
    """Basil's mother in PROFILE, drawn facing RIGHT and mirrored last. The
    scarf's knot rides the back of the crown, the apron panel hangs down the
    front of the pear, and the tail trails behind her."""
    hx, hy, by = 22, 22 + bob, 35 + bob
    s.tri((hx + 4, hy - 8), hy - 4, hx + 2, hx + 6, MOM_FUR, sh=0.26)
    s.tri((hx - 1, hy - 9), hy - 4, hx - 3, hx + 1, MOM_FUR)
    s.capsule(15, 41 + bob, 10, 42 + bob, 1.5, 1.2, MOM_FUR, sh=0.10)  # tail
    for (base_x, (dx, lift), sh) in ((19, fB, 0.22), (26, fF, 0.0)):
        lx = base_x + dx
        s.ball(lx + 0.5, 43 - lift, 2.1, 1.6, MOM_FUR, power=2.2, sh=sh,
               wrap=0.10, curve=0.10)
    s.ball(22, by, 7.0, 7.0, MOM_FUR, power=2.2, wrap=0.28, curve=0.22)
    # the apron as a tapered PANEL, not a slab: a flat rectangle down the
    # profile read as a sheet of paper pinned to her
    s.panel(24.5, by - 6, by + 4, 2.6, 3.8, WHITE, hem_curve=1, round_top=1,
            hem_band=1, sh=0.04)
    s.rect(23, by - 7, 24, by - 6, WHITE[2])                    # the strap
    s.rect(23, by + 1, 26, by + 3, WHITE[2])                    # the pocket
    s.capsule(23, by - 4, 25, by + 1, 1.8, 1.6, MOM_FUR, sh=0.14)   # near arm
    s.ball(25, by + 2, 1.7, 1.5, WHITE, power=2.2, sh=0.24, wrap=0.10,
           curve=0.10)
    s.ball(hx, hy, 6.8, 6.0, MOM_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.ball(hx + 4.5, hy + 3.4, 4.0, 2.5, WHITE, power=2.0, wrap=0.10,
           curve=0.10)
    s.rect(hx + 7, hy + 2, hx + 8, hy + 2, NOSE)
    _eye(s, hx + 2, hy - 2, EYE_Y, EYE_YL)
    s.line([(hx + 6, hy + 5), (hx + 7, hy + 5)], MOUTH)
    s.rect(hx - 6, hy - 6, hx + 5, hy - 4, MOM_SCARF[1])        # the band
    s.rect(hx - 6, hy - 4, hx + 5, hy - 4, MOM_SCARF[2])
    s.rect(hx - 8, hy - 5, hx - 6, hy - 2, MOM_SCARF[0])        # the knot, back
    s.rect(hx - 9, hy - 2, hx - 7, hy + 2, MOM_SCARF[1])
    s.despeckle(passes=1)
    s.outline(MOM_OUTS, OUT_DARK)
    for (x, y) in ((hx + 9, hy + 1), (hx + 10, hy + 3)):
        s.set(x, y, WHISK)                          # post-outline specks
    _mirror_cell(s)


# ---- Kitty's mother (2026-07-18 sickroom banishment beat) ------------------------------

KMOM_FUR = ramp((222, 150, 92), "violet", 4)       # older ginger — Kitty's mother
KMOM_SHAWL = ramp((170, 86, 110), "violet", 4)     # berry-wine shawl (NOT Basil-mom's sage)
KMOM_OUTS = outs_for((KMOM_FUR, OUT_DARK), (WHITE, OUT_LIGHT), (KMOM_SHAWL, OUT_DARK))


def kittymom(s, mood="idle", bob=0):
    """Kitty's mother: an older ginger cat matron — Kitty's ginger gone a touch
    muted, a berry shawl over the crown, and Kitty's OWN blue eyes so the
    mother/daughter reads at a glance. idle = arms down; act = the horrified
    hands-to-cheeks gasp ('Oh no, Kitty!'); emote = the accusing point + a
    hard shouting face (the banishment). Built on the Mom matron rig, but her
    own function so Basil's mother is untouched."""
    hy = 22 + bob
    # ears peek from under the shawl
    s.tri((CX - 6, hy - 9), hy - 4, CX - 8, CX - 3, KMOM_FUR)
    s.tri((CX + 6, hy - 9), hy - 4, CX + 3, CX + 8, KMOM_FUR, sh=0.12)
    s.ball(CX, hy, 7.0, 6.2, KMOM_FUR, power=2.4, wrap=0.34, curve=0.30)
    # shawl: a band across the crown with a side knot
    s.rect(CX - 6, hy - 6, CX + 6, hy - 4, KMOM_SHAWL[1])
    s.rect(CX - 6, hy - 4, CX + 6, hy - 4, KMOM_SHAWL[2])
    s.rect(CX + 6, hy - 5, CX + 8, hy - 3, KMOM_SHAWL[0])          # the knot
    s.ball(CX, hy + 4.2, 4.6, 2.8, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    ey = hy - 2
    if mood == "emote":                             # the hard, accusing look
        s.rect(CX - 5, ey + 1, CX - 3, ey + 2, KIT_EYE)
        s.rect(CX + 3, ey + 1, CX + 5, ey + 2, KIT_EYE)
        s.line([(CX - 5, ey), (CX - 3, ey)], OUT_DARK)            # brows drawn down
        s.line([(CX + 3, ey), (CX + 5, ey)], OUT_DARK)
        s.rect(CX - 2, hy + 4, CX + 1, hy + 5, MAW)               # open, shouting
    else:
        _eye(s, CX - 5, ey, KIT_EYE, KIT_EYEL)      # Kitty's blue — mother & daughter
        _eye(s, CX + 3, ey, KIT_EYE, KIT_EYEL)
        if mood == "act":
            s.rect(CX - 1, hy + 4, CX, hy + 5, MAW)               # a gasp — mouth open
        else:
            s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    # matronly pear body + apron
    by = 35 + bob
    s.ball(CX, by, 7.4, 7.0, KMOM_FUR, power=2.2, wrap=0.28, curve=0.22)
    for y in range(by - 5, by + 6):                 # apron panel, flat bands
        half = 4 + (2 if y > by - 1 else 1)
        for x in range(CX - half, CX + half + 1):
            s.set(x, y, WHITE[0] if x < CX else WHITE[1])
    s.rect(CX - 4, by - 6, CX - 3, by - 5, WHITE[2])              # straps
    s.rect(CX + 3, by - 6, CX + 4, by - 5, WHITE[2])
    s.rect(CX - 8, by - 6, CX - 6, by - 3, KMOM_SHAWL[1])         # shawl drape, both shoulders
    s.rect(CX + 6, by - 6, CX + 8, by - 3, KMOM_SHAWL[1])
    if mood == "act":                               # hands flown up to her cheeks
        s.capsule(CX - 7, by - 3, CX - 5, hy + 3, 1.8, 1.5, KMOM_FUR, sh=0.06)
        s.capsule(CX + 7, by - 3, CX + 5, hy + 3, 1.8, 1.5, KMOM_FUR, sh=0.16)
        s.ball(CX - 5, hy + 3, 1.9, 1.6, KMOM_FUR, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 5, hy + 3, 1.9, 1.6, KMOM_FUR, power=2.2, sh=0.10, wrap=0.10, curve=0.10)
    elif mood == "emote":                           # the accusing arm, thrust out west
        s.capsule(CX - 6, by - 4, CX - 14, by - 7, 2.0, 1.5, KMOM_FUR, sh=0.06)
        s.ball(CX - 15, by - 7, 2.2, 1.5, KMOM_FUR, power=2.2, wrap=0.10, curve=0.10)
        s.capsule(CX + 7, by - 4, CX + 8, by + 1, 1.8, 1.6, KMOM_FUR, sh=0.16)
        s.ball(CX + 8, by + 2, 1.7, 1.5, KMOM_FUR, power=2.2, sh=0.10, wrap=0.10, curve=0.10)
    else:
        s.capsule(CX - 7, by - 4, CX - 8, by + 1, 1.8, 1.6, KMOM_FUR, sh=0.06)
        s.capsule(CX + 7, by - 4, CX + 8, by + 1, 1.8, 1.6, KMOM_FUR, sh=0.16)
        s.ball(CX - 8, by + 2, 1.7, 1.5, KMOM_FUR, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 8, by + 2, 1.7, 1.5, KMOM_FUR, power=2.2, sh=0.10, wrap=0.10, curve=0.10)
    for lx in (CX - 3, CX + 3):                     # paws under the hem
        s.ball(lx, 43, 2.1, 1.6, KMOM_FUR, power=2.2, wrap=0.10, curve=0.10)
    # tail curled around her feet
    s.capsule(CX + 7, 41 + bob, CX + 10, 42 + bob, 1.5, 1.2, KMOM_FUR, sh=0.10)
    s.despeckle(passes=1)
    s.outline(KMOM_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob - 6)


MOUSE_OUTS = outs_for((MOUSE, OUT_DARK), (MPINK, OUT_DARK), (WHITE, OUT_LIGHT))


def mouse(s, mood="idle", bob=0):
    """Mouse kid, knee-high: dish ears bigger than the head."""
    hy = 30 + bob
    for (ex, sh) in ((CX - 6, 0.0), (CX + 6, 0.12)):    # dish ears
        s.ball(ex, hy - 7, 4.4, 4.2, MOUSE, power=2.0, sh=sh, wrap=0.24, curve=0.18)
        if mood != "back":                              # pink dish: front only
            s.ball(ex, hy - 7, 2.4, 2.2, MPINK, power=2.0, sh=sh, wrap=0.10, curve=0.10)
    s.ball(CX, hy, 5.6, 4.8, MOUSE, power=2.4, wrap=0.32, curve=0.26)
    s.ball(CX, 38 + bob, 4.6, 4.0, MOUSE, power=2.2, wrap=0.28, curve=0.20)
    if mood != "back":                                  # white belly: front only
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
    if mood != "back":                              # the face: front only
        s.ball(CX, hy + 3, 2.8, 1.8, WHITE, power=2.0, wrap=0.10, curve=0.10)  # muzzle
        s.set(CX, hy + 2, MPINK[0])                 # pink nose
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


def schweinler_adult(s, mood="idle", bob=0, liftL=0, liftR=0):
    """Schweinler grown: taller, wider, moneyed — plum waistcoat, brass
    buttons, the same smug snout. [idle, point, laugh]. `liftL`/`liftR` are
    the walk rows' paw lifts (2026-07-30) — on this body the trotters are
    all that shows under the girth, so the lift IS the leg animation."""
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
    for (lx, lift) in ((CX - 3, liftL), (CX + 3, liftR)):
        s.rect(lx - 1, 43 - lift, lx + 1, 44 - lift, PIG[3])  # trotters, girth
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


def schweinler_adult_back(s, bob=0, liftL=0, liftR=0):
    """The grown pig from behind (2026-07-30) — the flop-ear BACKS, the curly
    tail on the rump, and a waistcoat with NO placket and NO buttons, which
    is the whole difference between this and the front redrawn. The cravat
    survives as its knot at the nape; the triangle hangs out of sight."""
    hy, by = 20 + bob, 34 + bob
    s.tri((CX - 8, hy - 8), hy - 3, CX - 10, CX - 4, PIG, sh=0.30)
    s.tri((CX + 8, hy - 8), hy - 3, CX + 4, CX + 10, PIG, sh=0.38)
    s.ball(CX, hy, 7.8, 6.6, PIG, power=2.4, wrap=0.32, curve=0.28)
    s.ball(CX, by, 8.2, 7.6, PIG, power=2.2, wrap=0.28, curve=0.22)
    for y in range(by - 6, by + 7):                 # the waistcoat's back
        half = 5 + (2 if y > by - 2 else 1)
        for x in range(CX - half, CX + half + 1):
            s.set(x, y, VEST[1] if x < CX else VEST[2])
    for sy in range(by - 6, by + 7):
        s.set(CX, sy, VEST[3])                      # its centre seam
    s.capsule(CX - 7.5, by - 5, CX - 9, by + 2, 2.0, 1.6, PIG, sh=0.06)
    s.capsule(CX + 7.5, by - 5, CX + 9, by + 2, 2.0, 1.6, PIG, sh=0.16)
    for (lx, lift) in ((CX - 3, liftL), (CX + 3, liftR)):
        s.rect(lx - 1, 43 - lift, lx + 1, 44 - lift, PIG[3])
    s.rect(CX - 4, hy + 6, CX + 4, hy + 6, KERCH[1])            # the knot
    s.rect(CX - 4, hy + 7, CX + 4, hy + 7, KERCH[2])
    s.rect(CX - 1, hy + 6, CX + 1, hy + 8, KERCH[1])
    s.set(CX - 2, hy + 7, KERCH[3])
    s.set(CX + 2, hy + 7, KERCH[3])
    s.despeckle(passes=1)
    s.outline(SCHW_A_OUTS, OUT_DARK)
    # start the curl one px INSIDE the silhouette: _pig_curl only lays its dark
    # edge on EMPTY pixels, so a squiggle begun exactly on the body's rim loses
    # its root to the outline and hangs in space (the shipped kid cells do)
    _pig_curl(s, CX - 7, by + 2)                    # THE CURLY TAIL, west hip


def schweinler_adult_side(s, bob=0, fF=(0, 0), fB=(0, 0)):
    """The grown pig in profile, drawn facing RIGHT and mirrored last. Same
    read as the kid's: the SNOUT out past the cheek under a flop ear draped
    forward over the eye — but on the moneyed body, so the waistcoat's
    placket and its brass run down the FRONT edge of the flank, where they
    are the only thing that says which way he is facing at a glance."""
    hy, by = 20 + bob, 34 + bob
    for (base_x, (dx, lift), sh) in ((19, fB, 0.20), (27, fF, 0.0)):
        lx = base_x + dx
        s.capsule(lx, by + 6, lx, 42 - lift, 2.1, 1.9, PIG, sh=sh)
        s.rect(lx - 1, 43 - lift, lx + 1, 44 - lift, PIG[3])
    s.ball(23, by, 8.0, 7.4, PIG, power=2.2, wrap=0.28, curve=0.22)
    for y in range(by - 6, by + 7):                 # the waistcoat, front-biased
        half = 5 + (2 if y > by - 2 else 1)
        for x in range(24 - half, 24 + half + 1):
            s.set(x, y, VEST[0] if x < 24 else VEST[1])
    s.rect(28, by - 5, 28, by + 5, VEST[3])         # the placket shadow
    for byy in (by - 4, by - 1, by + 2):
        s.set(27, byy, BRASSF[0])                   # brass, one column
    s.capsule(25, by - 5, 27, by + 1, 2.0, 1.6, PIG, sh=0.10)        # near arm
    s.tri((19, hy - 8), hy - 2, 15, 20, PIG, sh=0.36)                # far ear
    s.ball(22, hy, 7.6, 6.4, PIG, power=2.4, wrap=0.32, curve=0.28)
    s.capsule(27, hy + 3, 31, hy + 3, 2.8, 2.5, SNOUT, sh=0.06)
    s.rect(32, hy + 1, 32, hy + 5, SNOUT[2])                         # disc end
    s.set(32, hy + 3, PIG_EYE)                                       # nostril
    s.set(31, hy + 5, SNOUT[3])
    s.tri((21, hy - 9), hy + 2, 24, 30, PIG, sh=0.16)   # near ear, draped fwd
    s.rect(27, hy + 2, 29, hy + 3, PIG[2])              # its heavy tip
    s.rect(24, hy - 2, 25, hy - 1, PIG_EYE)
    s.set(24, hy - 2, GLINT)
    s.rect(23, hy - 4, 26, hy - 4, PIG[3])              # the smug brow
    s.line([(29, hy + 6), (30, hy + 6)], MOUTH)
    s.rect(19, hy + 6, 27, hy + 7, KERCH[1])            # the cravat band
    s.rect(19, hy + 7, 22, hy + 7, KERCH[2])
    s.tri((26, hy + 11), hy + 8, 24, 28, KERCH, sh=0.14)   # its hanging point
    s.despeckle(passes=1)
    s.outline(SCHW_A_OUTS, OUT_DARK)
    _pig_curl(s, 16, by + 1)                        # one px inside — see above
    _mirror_cell(s)


BADGER_OUTS = outs_for((BADGER, OUT_DARK), (WHITE, OUT_LIGHT), (FUR, OUT_DARK))


def badger(s, mood="idle", bob=0, liftL=0, liftR=0):
    """The classmate: a blunt young badger — white face, twin dark stripes,
    stocky. His honesty is a blunt instrument. [idle, shrug, belly laugh].
    `liftL`/`liftR` are the walk rows' 1px paw lifts (2026-07-30); at 0 the
    cell is byte-identical to the shipped pose, which is the planted-neutral
    contract walk_down f0 / walk_up f0 rely on."""
    hy = 23 + bob
    s.tri((CX - 6, hy - 8), hy - 4, CX - 8, CX - 3, BADGER)
    s.tri((CX + 6, hy - 8), hy - 4, CX + 3, CX + 8, BADGER, sh=0.12)
    # from behind (hall tiers, 2026-07-18) the head is gray fur — the twin
    # stripes run right over the crown, so they still read; no face
    s.ball(CX, hy, 7.0, 6.2, BADGER if mood == "back" else WHITE,
           power=2.4, wrap=0.26, curve=0.24)
    for sx in (-4, 4):                              # the badger stripes
        for y in range(hy - 6, hy + 3):
            s.set(CX + sx, y, FUR[1])
            s.set(CX + sx + (1 if sx > 0 else -1), y, FUR[2])
    if mood != "back":
        s.ball(CX, hy + 4, 3.6, 2.2, WHITE, power=2.0, wrap=0.10, curve=0.10)
        s.rect(CX - 1, hy + 2, CX, hy + 3, NOSE)
        if mood == "emote":                         # the belly laugh
            for ex in (CX - 6, CX + 4):
                s.line([(ex, hy - 1), (ex + 1, hy - 2), (ex + 2, hy - 1)], PUPIL)
            s.rect(CX - 1, hy + 4, CX + 1, hy + 6, MAW)         # open laugh
        else:
            for ex in (CX - 6, CX + 4):
                s.rect(ex, hy - 2, ex + 1, hy - 1, PUPIL)
                s.set(ex + 1, hy - 2, GLINT)
            s.line([(CX - 1, hy + 5), (CX + 1, hy + 5)], MOUTH)  # flat mouth
    by = 36 + bob
    s.ball(CX, by, 6.6, 5.6, BADGER, power=2.2, wrap=0.28, curve=0.22)
    if mood != "back":                              # white belly: front only
        s.ball(CX, by + 1, 3.6, 3.2, WHITE, power=2.2, wrap=0.10, curve=0.10)
    if mood == "act":                               # the shrug — palms up
        s.capsule(CX - 6, by - 3, CX - 9, by - 6, 1.8, 1.5, BADGER, sh=0.06)
        s.capsule(CX + 6, by - 3, CX + 9, by - 6, 1.8, 1.5, BADGER, sh=0.16)
        s.ball(CX - 9, by - 7, 1.6, 1.4, WHITE, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 9, by - 7, 1.6, 1.4, WHITE, power=2.2, sh=0.10, wrap=0.10, curve=0.10)
    elif mood == "emote":                           # paws hugging the shake
        s.capsule(CX - 6, by - 3, CX - 4, by + 1, 1.8, 1.5, BADGER, sh=0.06)
        s.capsule(CX + 6, by - 3, CX + 4, by + 1, 1.8, 1.5, BADGER, sh=0.16)
    else:
        s.capsule(CX - 6, by - 3, CX - 7, by + 2, 1.8, 1.5, BADGER, sh=0.06)
        s.capsule(CX + 6, by - 3, CX + 7, by + 2, 1.8, 1.5, BADGER, sh=0.16)
    for (lx, lift) in ((CX - 3, liftL), (CX + 3, liftR)):
        s.capsule(lx, by + 4, lx, 42 - lift, 2.0, 1.8, BADGER, sh=0.08)
        s.ball(lx, 43 - lift, 2.0, 1.5, FUR, power=2.2, wrap=0.10, curve=0.10)
    s.despeckle(passes=1)
    s.outline(BADGER_OUTS, OUT_DARK)


def badger_side(s, bob=0, fF=(0, 0), fB=(0, 0)):
    """Ridley in PROFILE (2026-07-30), drawn facing RIGHT and mirrored last
    (the npc kit stores left-facing side cells).

    His whole read at 48px is the FACE, and it has to be THIS character's
    face, not a photograph of a badger. The front view's stripes run
    VERTICALLY — crown, through the eye, down to the jaw, flanking a white
    blaze — so in profile the near one is a vertical band down the side of
    the skull with the dark ear sitting on top of it. Drawn as the real
    animal's horizontal nose-to-ear stripe it is a different creature, and
    at 2px of drift it hoods him and reads as a bird.

    The other half of the identity is proportion: in the front cell the HEAD
    is bigger than the trunk and the white belly covers most of the chest.
    Reverse either one and it is some other stocky animal in his colours."""
    hx, hy, by = 21, 24 + bob, 36 + bob
    for (base_x, (dx, lift), sh) in ((18, fB, 0.24), (25, fF, 0.0)):
        lx = base_x + dx                            # the fore/aft scissor
        s.capsule(lx, by + 4, lx, 42 - lift, 2.0, 1.8, BADGER, sh=sh)
        s.ball(lx, 43 - lift, 2.0, 1.5, FUR, power=2.2, sh=sh, wrap=0.10,
               curve=0.10)
    s.ball(13, by + 1, 1.8, 1.5, BADGER, power=2.0, sh=0.30, wrap=0.12,
           curve=0.10)                              # the stub tail, rear
    s.ball(20, by, 6.6, 5.6, BADGER, power=2.2, wrap=0.28, curve=0.22)
    s.ball(22, by + 1, 4.0, 3.4, WHITE, power=2.2, sh=0.12, wrap=0.10,
           curve=0.10)                              # the belly, most of the chest
    s.capsule(23, by - 4, 24.5, by + 1, 1.8, 1.5, BADGER, sh=0.12)   # near arm
    s.ball(24.5, by + 2, 1.7, 1.4, WHITE, power=2.2, sh=0.26, wrap=0.10,
           curve=0.10)
    # NO NECK. The front view has none either — the skull sits straight on the
    # trunk, and a visible column between them turns a stocky chibi badger into
    # something long and hunched
    s.ball(hx, hy, 6.8, 6.0, WHITE, power=2.4, wrap=0.30, curve=0.26)
    # a SHORT muzzle bump — run out as a proper snout the white skull and the
    # white muzzle fuse into one mass with nothing to break it up
    s.ball(hx + 5, hy + 3, 2.6, 1.9, WHITE, power=2.0, wrap=0.12, curve=0.10)
    s.rect(hx + 7, hy + 2, hx + 8, hy + 3, NOSE)
    for y in range(hy - 6, hy + 5):                 # THE stripe, vertical
        s.rect(hx, y, hx + 1, y, FUR[1])
        s.set(hx + 2, y, FUR[2])
    s.ball(hx - 1, hy - 6, 2.6, 2.0, FUR, power=2.2, sh=0.20, wrap=0.14,
           curve=0.12)                              # the ear, atop the stripe
    s.rect(hx, hy - 1, hx + 1, hy, PUPIL)           # the eye INSIDE the stripe —
    s.set(hx + 1, hy - 1, GLINT)                    # only the glint finds it
    s.line([(hx + 5, hy + 5), (hx + 6, hy + 5)], MOUTH)
    s.despeckle(passes=1)
    s.outline(BADGER_OUTS, OUT_DARK)
    _mirror_cell(s)


STORK_OUTS = outs_for((STORK, OUT_LIGHT), (BILL, OUT_DARK), (FUR, OUT_DARK))


def stork(s, mood="idle", bob=0):
    """Doctor Ciconia: a tall clinical stork — long orange bill, half-moon
    spectacles perched on it, black flight-feather tips. [idle, consult,
    dry chuckle (the panel cracking at the naming)]."""
    hy = 16 + bob
    s.ball(CX + 2, hy, 3.6, 3.2, STORK, power=2.2, wrap=0.22, curve=0.18)  # head
    if mood == "emote":                             # bill tips UP, eye shut
        s.capsule(CX + 1, hy + 1, CX - 8, hy - 2, 1.2, 0.7, BILL, sh=0.06)
        s.rect(CX - 2, hy, CX, hy, RIMLESS)         # specs ride the lift
        s.set(CX - 3, hy - 1, RIMLESS)
        s.line([(CX + 2, hy - 1), (CX + 3, hy - 2), (CX + 4, hy - 1)], PUPIL)
    else:
        # the long bill, angled down-left; spectacles ride it
        s.capsule(CX + 1, hy + 1, CX - 8, hy + 4, 1.2, 0.7, BILL, sh=0.06)
        s.rect(CX - 2, hy + 1, CX, hy + 1, RIMLESS) # half-moon specs
        s.set(CX - 3, hy + 2, RIMLESS)
        s.set(CX + 3, hy - 1, PUPIL)                # calm eye
    s.capsule(CX + 3, hy + 2, CX + 2, 26 + bob, 1.8, 2.2, STORK, sh=0.04)  # neck
    s.ball(CX, 33 + bob, 6.4, 7.8, STORK, power=2.2, wrap=0.28, curve=0.22)  # body
    if mood in ("act", "emote"):                    # wing raised (consult /
        s.capsule(CX - 5.5, 30 + bob, CX - 10, 24 + bob, 2.0, 1.4, STORK, sh=0.12)
        s.rect(CX - 11, 23 + bob, CX - 9, 24 + bob, FUR[1])       # at the bill)
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
    only — the bed's own art carries everything below. Redrawn 2026-07-16 at
    the cast's full chibi scale (the old head read as a small blob against
    the quilt): head nearly the whole figure, big kid-sheet eyes, a proper
    three-band brow bandage where the bandana usually sits — the whole story
    in one sprite. [rest(blink), vacant, polite]. The vacant eyes have NO
    glint — the empty look is the whole beat."""
    hy = 22 + bob
    # one ear up, one kinked flat under the bandage
    s.tri((CX - 6, hy - 11), hy - 5, CX - 9, CX - 3, KIT_FUR)
    s.tri((CX + 7, hy - 8), hy - 4, CX + 3, CX + 10, KIT_FUR, sh=0.16)
    s.tri((CX - 6, hy - 9), hy - 6, CX - 7, CX - 5, EARIN)
    # softer wrap than the walking sheets: at this head size the full band
    # left half the face raw shade-red — the sickbed pallor wants gentler
    s.ball(CX, hy, 7.8, 7.0, KIT_FUR, power=2.4, wrap=0.24, curve=0.22)
    # the brow bandage: three clean linen bands + the tuck over the kinked ear
    s.rect(CX - 7, hy - 7, CX + 6, hy - 4, LINEN[1])
    s.rect(CX - 7, hy - 7, CX + 6, hy - 7, LINEN[0])
    s.rect(CX - 7, hy - 4, CX + 6, hy - 4, LINEN[3])
    s.rect(CX + 5, hy - 8, CX + 8, hy - 6, LINEN[0])              # tuck
    s.set(CX + 7, hy - 5, LINEN[2])
    s.ball(CX, hy + 4.6, 5.0, 3.0, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    ey = hy - 2
    if mood == "rest":
        _closed(s, CX - 6, ey, happy=False)
        _closed(s, CX + 4, ey, happy=False)
        s.line([(CX - 1, hy + 5), (CX, hy + 5)], MOUTH)
    elif mood == "vacant":
        for ex in (CX - 6, CX + 4):
            s.rect(ex, ey, ex + 2, ey + 2, KIT_EYE)
            s.rect(ex + 1, ey + 1, ex + 1, ey + 2, PUPIL)         # no glint
        s.line([(CX - 1, hy + 5), (CX, hy + 5)], MOUTH)
    else:                                           # polite — kind to a stranger
        for ex in (CX - 6, CX + 4):
            s.rect(ex, ey, ex + 2, ey + 2, KIT_EYE)
            s.rect(ex, ey, ex + 2, ey, KIT_EYEL)
            s.rect(ex + 1, ey + 1, ex + 1, ey + 2, PUPIL)
            s.set(ex + 2, ey, GLINT)
        s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
                (CX + 1, hy + 5)], MOUTH)
    # gowned shoulders; the bed cover takes everything below
    s.capsule(CX - 8, hy + 11, CX + 8, hy + 11, 3.6, 3.4, LINEN, sh=0.08)
    s.rect(CX - 1, hy + 10, CX + 1, hy + 14, LINEN[2])            # gown vee
    s.despeckle(passes=1)
    s.outline(KITTYBED_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob - 6)


MOMBED_OUTS = outs_for((MOM_FUR, OUT_DARK), (WHITE, OUT_LIGHT),
                       (LINEN, OUT_LIGHT), (MOM_SCARF, OUT_DARK))


def mom_bed(s, mood="rest", bob=0):
    """Mom propped up against the headboard (Prologue A0 "The Fever"):
    head + gowned shoulders only — the bed's own art carries everything
    below (the kitty_bed recipe, same chibi scale). The sage headscarf
    stays on — it is her identity the way the bandage is Kitty's — but
    tied SOFT, the knot slumped to one side. [rest (asleep), act (awake,
    weak), emote (the warm look)]."""
    hy = 22 + bob
    # ears out from under the slumped scarf
    s.tri((CX - 6, hy - 10), hy - 4, CX - 8, CX - 3, MOM_FUR)
    s.tri((CX + 6, hy - 9), hy - 4, CX + 3, CX + 8, MOM_FUR, sh=0.14)
    s.ball(CX, hy, 7.6, 6.8, MOM_FUR, power=2.4, wrap=0.28, curve=0.26)
    # the scarf, tied soft: the band a row lower than her working knot
    s.rect(CX - 7, hy - 7, CX + 6, hy - 4, MOM_SCARF[1])
    s.rect(CX - 7, hy - 4, CX + 6, hy - 4, MOM_SCARF[2])
    s.rect(CX + 5, hy - 6, CX + 8, hy - 3, MOM_SCARF[0])      # the slumped knot
    s.ball(CX, hy + 4.4, 4.8, 2.9, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    ey = hy - 2
    if mood == "rest":
        _closed(s, CX - 5, ey, happy=False)
        _closed(s, CX + 3, ey, happy=False)
        s.line([(CX - 1, hy + 5), (CX, hy + 5)], MOUTH)
    elif mood == "act":                             # awake, weak — but HER
        _eye(s, CX - 5, ey, EYE_Y, EYE_YL)
        _eye(s, CX + 3, ey, EYE_Y, EYE_YL)
        s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    else:                                           # emote — the warm look
        _closed(s, CX - 5, ey)
        _closed(s, CX + 3, ey)
        s.rect(CX - 1, hy + 4, CX, hy + 5, MAW)
        s.set(CX - 6, hy + 2, BLUSH)
        s.set(CX + 5, hy + 2, BLUSH)
    # gowned shoulders; the bed cover takes everything below
    s.capsule(CX - 8, hy + 11, CX + 8, hy + 11, 3.6, 3.4, LINEN, sh=0.08)
    s.rect(CX - 1, hy + 10, CX + 1, hy + 14, LINEN[2])        # gown vee
    s.despeckle(passes=1)
    s.outline(MOMBED_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob - 6)


RIMLESS = (198, 214, 226, 255)                     # the stork's half-moon specs


# ---- college-age Kitty ----------------------------------------------------------------------

APRON = ramp((172, 134, 92), "violet", 4)          # waxed-canvas work apron
KITADULT_OUTS = outs_for((KIT_FUR, OUT_DARK), (WHITE, OUT_LIGHT),
                         (KIT_BAND, OUT_DARK), (APRON, OUT_DARK))


def kitty_adult(s, mood="idle", bob=0):
    """Kitty Cool grown into the stall keeper (the workshop interlude + the
    fountain-rim stall, 2026-07-16): the kid sheet's ginger fur, teal
    bandana and grease smudge carried onto the adult body (the mom idiom),
    plus a waxed-canvas work apron with a brass-glint pocket. [idle x2,
    TINKER act x2 (paws up at the work), BEAM emote x2 (the whoop)]."""
    hy = 22 + bob
    # both ears up — she never lost the alert tilt
    s.tri((CX - 6, hy - 10), hy - 4, CX - 8, CX - 3, KIT_FUR)
    s.tri((CX + 6, hy - 10), hy - 4, CX + 3, CX + 8, KIT_FUR, sh=0.12)
    s.tri((CX - 6, hy - 8), hy - 5, CX - 7, CX - 5, EARIN)
    s.tri((CX + 6, hy - 8), hy - 5, CX + 5, CX + 7, EARIN)
    s.ball(CX, hy, 7.0, 6.2, KIT_FUR, power=2.4, wrap=0.30, curve=0.26)
    s.ball(CX, hy + 4.2, 4.6, 2.8, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    ey = hy - 2
    if mood == "beam":
        _closed(s, CX - 5, ey)
        _closed(s, CX + 3, ey)
        s.rect(CX - 1, hy + 4, CX, hy + 5, MAW)
        s.set(CX - 6, hy + 2, BLUSH)
        s.set(CX + 5, hy + 2, BLUSH)
    else:
        _eye(s, CX - 5, ey, KIT_EYE, KIT_EYEL)
        _eye(s, CX + 3, ey, KIT_EYE, KIT_EYEL)
        s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    # the grease smudge — some things do not wash off
    s.set(CX + 5, hy + 3, SMUDGE)
    s.set(CX + 6, hy + 2, SMUDGE)
    # slim maker body under the apron panel (flat bands, mom's recipe)
    by = 35 + bob
    s.ball(CX, by, 6.8, 6.6, KIT_FUR, power=2.2, wrap=0.26, curve=0.20)
    for y in range(by - 4, by + 6):
        half = 3 + (2 if y > by - 1 else 1)
        for x in range(CX - half, CX + half + 1):
            s.set(x, y, APRON[0] if x < CX else APRON[1])
    s.rect(CX - 3, by - 6, CX - 2, by - 5, APRON[2])              # straps
    s.rect(CX + 2, by - 6, CX + 3, by - 5, APRON[2])
    s.rect(CX - 2, by + 2, CX + 2, by + 4, APRON[2])              # pocket
    s.set(CX + 1, by + 2, BRASSF[0])                # a gear peeking out
    s.set(CX - 1, by + 2, STEELF[1])                # and a spring end
    # bandana at the throat — the kid kerchief, worn ever since
    s.rect(CX - 4, hy + 7, CX + 4, hy + 8, KIT_BAND[1])
    s.rect(CX + 1, hy + 8, CX + 4, hy + 8, KIT_BAND[2])
    s.tri((CX, hy + 11), hy + 8, CX - 2, CX + 2, KIT_BAND, sh=0.14)
    if mood == "tinker":
        # both paws up at the work, a brass bit pinched mid-air
        s.capsule(CX - 6.5, by - 4, CX - 3, by - 8, 1.8, 1.6, KIT_FUR, sh=0.06)
        s.capsule(CX + 6.5, by - 4, CX + 3, by - 8, 1.8, 1.6, KIT_FUR, sh=0.16)
        s.ball(CX - 3, by - 9, 1.7, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
        s.ball(CX + 3, by - 9, 1.7, 1.5, WHITE, power=2.2, sh=0.10, wrap=0.10,
               curve=0.10)
        # the pinched gear + work glint are drawn AFTER the finishing
        # passes at the bottom — despeckle eats lone specks (the sage rule)
    elif mood == "beam":
        # arms flung up — the whoop
        s.capsule(CX - 7, by - 4, CX - 9, by - 9, 1.8, 1.6, KIT_FUR, sh=0.06)
        s.capsule(CX + 7, by - 4, CX + 9, by - 9, 1.8, 1.6, KIT_FUR, sh=0.16)
        s.ball(CX - 9, by - 10, 1.7, 1.5, WHITE, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 9, by - 10, 1.7, 1.5, WHITE, power=2.2, sh=0.10, wrap=0.10,
               curve=0.10)
    else:
        s.capsule(CX - 7, by - 4, CX - 8, by + 1, 1.8, 1.6, KIT_FUR, sh=0.06)
        s.capsule(CX + 7, by - 4, CX + 8, by + 1, 1.8, 1.6, KIT_FUR, sh=0.16)
        s.ball(CX - 8, by + 2, 1.7, 1.5, WHITE, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 8, by + 2, 1.7, 1.5, WHITE, power=2.2, sh=0.10, wrap=0.10,
               curve=0.10)
    for lx in (CX - 3, CX + 3):                     # paws under the hem
        s.ball(lx, 43, 2.1, 1.6, KIT_FUR, power=2.2, wrap=0.10, curve=0.10)
    # tail up in a question-mark curl — the maker's antenna. CAPSULE
    # strokes, never s.line pixels: line() doesn't interpolate and
    # despeckle eats disconnected specks (the sibling tails are all
    # capsules for the same reason)
    s.capsule(CX + 7, 41 + bob, CX + 10, 37 + bob, 1.5, 1.3, KIT_FUR, sh=0.10)
    s.capsule(CX + 10, 37 + bob, CX + 9, 33 + bob, 1.3, 1.2, KIT_FUR, sh=0.06)
    s.ball(CX + 9, 32 + bob, 1.5, 1.4, KIT_FUR, power=2.2, wrap=0.10,
           curve=0.10)
    s.despeckle(passes=1)
    s.outline(KITADULT_OUTS, OUT_DARK)
    whiskers_kid_down(s, bob - 6)
    if mood == "tinker":
        # deliberate specks AFTER despeckle/outline (sage's sparkle rule:
        # details that break the silhouette draw over the finished art)
        s.set(CX, by - 10, BRASSF[1])               # the pinched gear
        s.set(CX + 1, by - 10, BRASSF[0])
        s.set(CX, by - 12, SPARK)                   # work glint


# ---- Kitty adult BACK + SIDE views (2026-07-17, the bluff from-behind
# restage): the sunset scene stages its cast facing the water — up-screen,
# backs to the camera — turning to profile only to look at each other. The
# cores are parameterized on an (ox, oy) blit offset + head tilt so the kiss
# composition below reuses the exact same body. --------------------------------------

def _kitty_back_core(s, ox=0, oy=0, bob=0, head_dx=0, head_dy=0):
    """Kitty from behind: ear backs, the bandana KNOT at the nape, apron
    straps crossed over her back with the waist bow, question-curl tail."""
    hx, hy = CX + ox + head_dx, 22 + oy + bob + head_dy
    # ears from behind: fur backs, no inner
    s.tri((hx - 6, hy - 10), hy - 4, hx - 8, hx - 3, KIT_FUR)
    s.tri((hx + 6, hy - 10), hy - 4, hx + 3, hx + 8, KIT_FUR, sh=0.20)
    s.tri((hx - 6, hy - 8), hy - 5, hx - 7, hx - 5, KIT_FUR, sh=0.34)
    s.tri((hx + 6, hy - 8), hy - 5, hx + 5, hx + 7, KIT_FUR, sh=0.42)
    bx, by = CX + ox, 35 + oy + bob
    # body + hanging arms (drawn under the skull so the nape reads)
    s.ball(bx, by, 6.8, 6.6, KIT_FUR, power=2.2, wrap=0.26, curve=0.20)
    s.capsule(bx - 7, by - 4, bx - 8, by + 1, 1.8, 1.6, KIT_FUR, sh=0.06)
    s.capsule(bx + 7, by - 4, bx + 8, by + 1, 1.8, 1.6, KIT_FUR, sh=0.16)
    s.ball(bx - 8, by + 2, 1.7, 1.5, KIT_FUR, power=2.2, wrap=0.10, curve=0.10)
    s.ball(bx + 8, by + 2, 1.7, 1.5, KIT_FUR, power=2.2, sh=0.10, wrap=0.10,
           curve=0.10)
    # apron straps crossed over the back + the tie bow
    ln(s, bx - 3, by - 5, bx + 2, by + 1, APRON[2])
    ln(s, bx + 3, by - 5, bx - 2, by + 1, APRON[2])
    s.rect(bx - 1, by + 1, bx + 1, by + 2, APRON[1])       # the bow knot
    s.set(bx - 2, by + 3, APRON[2])                        # bow tails
    s.set(bx + 2, by + 3, APRON[2])
    for lx in (bx - 3, bx + 3):                            # paws under the hem
        s.ball(lx, 43 + oy, 2.1, 1.6, KIT_FUR, power=2.2, wrap=0.10, curve=0.10)
    # the skull over the nape, then the bandana band + knot at the nape
    s.ball(hx, hy, 7.0, 6.2, KIT_FUR, power=2.4, wrap=0.30, curve=0.26)
    s.line([(hx - 2, hy + 5), (hx - 1, hy + 6), (hx, hy + 6),
            (hx + 1, hy + 6), (hx + 2, hy + 5)], KIT_FUR[3])   # neck part
    s.rect(hx - 4, hy + 7, hx + 4, hy + 8, KIT_BAND[1])
    s.rect(hx - 4, hy + 8, hx - 1, hy + 8, KIT_BAND[2])
    s.rect(hx - 1, hy + 8, hx + 1, hy + 9, KIT_BAND[2])    # the knot
    s.set(hx - 2, hy + 10, KIT_BAND[3])                    # knot tails
    s.set(hx + 2, hy + 10, KIT_BAND[3])


def _kitty_tail_curl(s, bx, oy, bob, west=False):
    """The maker's-antenna question curl, east by default (her down-view
    tail); west mirrors it toward a partner standing screen-left."""
    d = -1 if west else 1
    s.capsule(bx + 7 * d, 41 + oy + bob, bx + 10 * d, 37 + oy + bob,
              1.5, 1.3, KIT_FUR, sh=0.10)
    s.capsule(bx + 10 * d, 37 + oy + bob, bx + 9 * d, 33 + oy + bob,
              1.3, 1.2, KIT_FUR, sh=0.06)
    s.ball(bx + 9 * d, 32 + oy + bob, 1.5, 1.4, KIT_FUR, power=2.2,
           wrap=0.10, curve=0.10)


def kitty_adult_back(s, bob=0):
    _kitty_back_core(s, bob=bob)
    _kitty_tail_curl(s, CX, 0, bob)
    s.despeckle(passes=1)
    s.outline(KITADULT_OUTS, OUT_DARK)


def _kitty_side_core(s, ox=0, oy=0, bob=0, lean=0, eyes="open", arm=True):
    """Kitty in LEFT profile (the bluff stages her east of Basil, so her
    turn-to-him is a left profile — the NPC kit's flip_h serves the other
    side). White cheek forward, smudge behind it, kerchief triangle at the
    throat, apron panel on the front half, tail curling behind (east).
    A negative `bob` reads as TIPTOE: the body lifts, leg stubs stretch,
    the paws stay planted (the kiss frame). `arm=False` skips the hanging
    near arm so a composer can pose its own reach."""
    hx, hy = 25 - lean + ox, 21 + oy + bob
    # ears: near ear tall, far ear peeking front
    s.tri((hx - 3, hy - 10), hy - 5, hx - 5, hx - 1, KIT_FUR, sh=0.28)
    s.tri((hx + 1, hy - 11), hy - 5, hx - 1, hx + 3, KIT_FUR)
    s.tri((hx + 1, hy - 9), hy - 6, hx, hx + 2, EARIN)
    bx, by = 26 + ox, 35 + oy + bob
    _kitty_tail_curl(s, bx, oy, bob)
    # leg stubs bridge body to the planted paws (visible on tiptoe)
    for (lx, sh) in ((bx - 3, 0.0), (bx + 2, 0.12)):
        s.capsule(lx, by + 4, lx, 42 + oy, 1.9, 1.6, KIT_FUR, sh=sh)
    # slim body, apron panel on the front (west) half + shoulder strap
    s.ball(bx, by, 5.8, 6.4, KIT_FUR, power=2.2, wrap=0.26, curve=0.20)
    for y in range(by - 4, by + 6):
        half = 3 + (2 if y > by - 1 else 1)
        for x in range(bx - half, bx + 1):
            s.set(x, y, APRON[0] if x < bx - 2 else APRON[1])
    s.rect(bx - half, by + 5, bx, by + 5, APRON[2])        # hem shade
    ln(s, bx - 2, by - 6, bx - 1, by - 4, APRON[2])        # shoulder strap
    if arm:
        # near arm hanging over the panel
        s.capsule(bx - 1, by - 4, bx - 3, by + 1, 1.8, 1.6, KIT_FUR, sh=0.10)
        s.ball(bx - 3, by + 2, 1.7, 1.5, KIT_FUR, power=2.2, wrap=0.10, curve=0.10)
    for lx in (bx - 3, bx + 2):                            # planted paws
        s.ball(lx, 43 + oy, 2.1, 1.6, KIT_FUR, power=2.2, wrap=0.10, curve=0.10)
    # skull + the plump white cheek forward
    s.ball(hx, hy, 6.4, 5.8, KIT_FUR, power=2.4, wrap=0.30, curve=0.26)
    s.ball(hx - 4, hy + 2.5, 3.0, 2.6, KIT_FUR, power=2.0, wrap=0.30)
    s.ball(hx - 4.5, hy + 3.2, 3.0, 2.4, WHITE, power=2.0, wrap=0.10, curve=0.10)
    s.rect(hx - 7, hy + 2, hx - 6, hy + 2, NOSE)
    s.line([(hx - 6, hy + 4), (hx - 5, hy + 4)], MOUTH)
    if eyes == "open":
        s.rect(hx - 4, hy - 3, hx - 2, hy - 1, KIT_EYE)
        s.rect(hx - 4, hy - 3, hx - 2, hy - 3, KIT_EYEL)
        s.rect(hx - 3, hy - 2, hx - 3, hy - 1, PUPIL)
        s.set(hx - 4, hy - 3, GLINT)
    else:                                                  # closed ^ (the kiss)
        s.line([(hx - 4, hy - 1), (hx - 3, hy - 2), (hx - 2, hy - 1)], LID)
    s.set(hx + 1, hy + 3, SMUDGE)                          # some things don't wash off
    s.set(hx + 2, hy + 2, SMUDGE)
    # bandana at the throat, kerchief triangle hanging front
    s.rect(hx - 4, hy + 7, hx + 3, hy + 8, KIT_BAND[1])
    s.rect(hx + 1, hy + 8, hx + 3, hy + 8, KIT_BAND[2])
    s.tri((hx - 4, hy + 11), hy + 8, hx - 6, hx - 2, KIT_BAND, sh=0.14)


def _kitty_side_whiskers(s, hx, hy):
    """Profile whiskers off the white cheek, drawn post-outline."""
    for (x, y) in ((hx - 9, hy + 1), (hx - 10, hy + 2), (hx - 9, hy + 4)):
        s.set(x, y, WHISK)


def kitty_adult_side(s, bob=0):
    _kitty_side_core(s, bob=bob)
    s.despeckle(passes=1)
    s.outline(KITADULT_OUTS, OUT_DARK)
    _kitty_side_whiskers(s, 25, 21 + bob)


# ---- the bluff kiss (2026-07-17): a composed two-cat sheet, because two
# 48px bodies standing near each other never read as a kiss. Three 96x96
# frames (bluff_kiss_gen.png, 288x96 — scene/bluff.gd swaps it in over the
# hidden bodies, hframes=3): lean-in with the paw-hold, the KISS (muzzle
# contact, closed eyes, her paw on his chest, his tail curling up), and the
# after — both from BEHIND at the lip, her head on his shoulder, watching
# the sun lane. Feet baseline y=92 (the 48-cell contract + 48). ----------------------

COATR = BASIL["COATR"]
PANTR = BASIL["PANTR"]
GOGRIM = BASIL["GOGRIM"]
GOGLEN = BASIL["GOGLEN"]
KISS_OUTS = outs_for((FUR, OUT_DARK), (WHITE, OUT_LIGHT), (COATR, OUT_DARK),
                     (PANTR, OUT_DARK), (GOGRIM, OUT_DARK), (KIT_FUR, OUT_DARK),
                     (KIT_BAND, OUT_DARK), (APRON, OUT_DARK))


def _basil_profile(s, ox, oy, lean=0, kiss=False):
    """Adult-sheet Basil in RIGHT profile (coat, goggles, no gun), feet fill
    at 44+oy. `lean` tips the shoulders toward her; `kiss` closes the eyes,
    tips the chin up and raises the tail."""
    hx, hy = 23 + lean + ox, 18 + oy - (1 if kiss else 0)
    # tail: raised happy curl on the kiss, low sweep otherwise
    if kiss:
        s.capsule(16 + ox, 30 + oy, 14 + ox, 25 + oy, 1.7, 1.4, FUR, sh=0.10)
        s.capsule(14 + ox, 25 + oy, 15 + ox, 20 + oy, 1.4, 1.1, FUR, sh=0.13)
        s.set(15 + ox, 19 + oy, FUR[0])
    else:
        s.capsule(16 + ox, 30 + oy, 13 + ox, 28 + oy, 1.7, 1.4, FUR, sh=0.10)
        s.capsule(13 + ox, 28 + oy, 10 + ox, 26 + oy, 1.4, 1.1, FUR, sh=0.13)
        s.set(9 + ox, 25 + oy, FUR[0])
    for (fx, sh) in ((20, 0.16), (25, 0.0)):               # legs under the hem
        s.capsule(fx + ox, 33 + oy, fx + ox, 40 + oy, 2.1, 1.7, PANTR, sh=sh)
        s.ball(fx + 0.5 + ox, 42.6 + oy, 2.2, 1.7, WHITE, power=2.2,
               sh=sh * 0.4, wrap=0.10, curve=0.10)
    # the near-floor coat in profile (the adult sheet's flat-band recipe)
    top, hem = 22 + oy, 40 + oy
    h = hem - top
    for y in range(top, hem + 1):
        vy = (y - top) / h
        x_off = int(round(lean * (1.0 - vy)))
        x0 = int(round(17 - vy * 3.0)) + x_off + ox
        x1 = 29 + x_off + ox
        if y == top:
            x0 += 2
            x1 -= 1
        elif y == top + 1:
            x0 += 1
        fold = x0 + 3
        for x in range(x0, x1 + 1):
            if y >= hem - 1:
                c = COATR[3] if x >= x1 - 1 else COATR[2]
            elif x == x1:
                c = COATR[3] if y >= top + 2 else COATR[2]
            elif x == x1 - 1:
                c = COATR[2]
            elif x == fold and y >= top + 4:
                c = COATR[2]
            elif x <= x0 + 2:
                c = COATR[0]
            else:
                c = COATR[1]
            s.set(x, y, c)
    s.rect(16 + lean + ox, hem + 1, 27 + lean + ox, hem + 1, COATR[3])
    # head profile: short-nosed, big white cheek, goggles up
    s.tri((hx + 3, hy - 10), hy - 5, hx + 1, hx + 5, FUR, sh=0.30)
    s.tri((hx - 1, hy - 11), hy - 5, hx - 3, hx + 1, FUR)
    s.tri((hx - 1, hy - 9), hy - 6, hx - 2, hx, EARIN)
    s.ball(hx, hy, 6.8, 5.6, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.ball(hx + 4, hy + 2.5, 3.2, 2.7, FUR, power=2.0, wrap=0.30)
    s.ball(hx + 4.5, hy + 3.2, 3.2, 2.5, WHITE, power=2.0, wrap=0.10, curve=0.10)
    s.rect(hx + 6, hy + 2, hx + 7, hy + 2, NOSE)
    s.line([(hx + 5, hy + 4), (hx + 6, hy + 4)], MOUTH)
    if kiss:
        s.line([(hx + 2, hy - 2), (hx + 3, hy - 3), (hx + 4, hy - 2)], LID)
        s.set(hx + 1, hy + 1, BLUSH)
    else:
        _eye(s, hx + 2, hy - 3, EYE_Y, EYE_YL)
    s.rect(hx - 6, hy - 5, hx + 3, hy - 5, GOGRIM[2])      # goggle strap
    s.set(hx - 2, hy - 6, GOGRIM[1])
    s.ball(hx + 3, hy - 6.5, 2.3, 1.8, GOGRIM, power=2.0)
    s.blob(hx + 3, hy - 6.5, 1.3, 1.0, GOGLEN[1])
    s.set(hx + 2, hy - 7, GOGLEN[0])


def _basil_back(s, ox, oy, head_dx=0, tail_up=True):
    """Adult-sheet Basil from behind (the up-view recipe): dome + ear backs,
    goggle strap and cups over the crown, coat back, hanging sleeves, tail
    raised east — or resting on the ground west (`tail_up=False`, the
    after-kiss frame: her head occupies where the raised tail would go)."""
    hx, hy = 24 + ox + head_dx, 18 + oy
    s.tri((hx - 4, hy - 10), hy - 4, hx - 7, hx - 1, FUR)
    s.tri((hx + 4, hy - 10), hy - 4, hx + 1, hx + 7, FUR, sh=0.15)
    s.tri((hx - 4, hy - 8), hy - 5, hx - 6, hx - 2, FUR, sh=0.38)
    s.tri((hx + 4, hy - 8), hy - 5, hx + 2, hx + 6, FUR, sh=0.46)
    for (fx, sh) in ((21, 0.0), (27, 0.10)):               # trouser stubs + paws
        s.capsule(fx + ox, 33 + oy, fx + ox, 40 + oy, 2.2, 1.7, PANTR, sh=sh)
        s.ball(fx + ox, 42.6 + oy, 2.2, 1.7, WHITE, power=2.2, sh=sh * 0.5,
               wrap=0.10, curve=0.10)
    top, hem = 22 + oy, 40 + oy                            # coat back, flat bands
    cx = 24 + ox
    for y in range(top, hem + 1):
        vy = (y - top) / (hem - top)
        half = 5.6 + 2.0 * vy
        x0 = int(round(cx - half))
        x1 = int(round(cx + half))
        if y == top:
            x0 += 2
            x1 -= 2
        elif y == top + 1:
            x0 += 1
            x1 -= 1
        for x in range(x0, x1 + 1):
            if y >= hem - 1:
                c = COATR[3] if x >= x1 - 1 else COATR[2]
            elif x >= x1 - 1:
                c = COATR[2]
            elif x < cx:
                c = COATR[0]
            else:
                c = COATR[1]
            s.set(x, y, c)
    s.rect(cx - 5, hem + 1, cx + 5, hem + 1, COATR[3])
    s.rect(cx - 5, top, cx + 5, top + 1, COATR[1])         # collar band
    s.rect(cx - 4, top + 6, cx + 4, top + 6, COATR[2])     # back belt
    for y in range(top + 8, hem - 1):                      # vent seam
        s.set(cx, y, COATR[2])
    for (sx, hxx, sh) in ((cx - 6, cx - 8, 0.18), (cx + 6, cx + 8, 0.32)):
        s.capsule(sx, top + 1, hxx, top + 7, 1.9, 1.6, COATR, sh=sh)
        s.ball(hxx, top + 9, 1.8, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
    if tail_up:
        s.capsule(29 + ox, 31 + oy, 32 + ox, 27 + oy, 1.7, 1.4, FUR, sh=0.10)
        s.capsule(32 + ox, 27 + oy, 33 + ox, 23 + oy, 1.4, 1.1, FUR, sh=0.14)
        s.set(33 + ox, 22 + oy, FUR[0])
    else:
        s.capsule(19 + ox, 40 + oy, 14 + ox, 43 + oy, 1.6, 1.3, FUR, sh=0.10)
        s.set(13 + ox, 43 + oy, FUR[0])
    s.ball(hx, hy, 7.2, 6.0, FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(hx - 6, hy - 4, hx + 6, hy - 4, GOGRIM[2])      # strap + buckle
    s.rect(hx - 1, hy - 4, hx + 1, hy - 4, GOGRIM[1])
    s.ball(hx - 3, hy - 5.5, 2.0, 1.4, GOGRIM, power=2.0)
    s.ball(hx + 3, hy - 5.5, 2.0, 1.4, GOGRIM, power=2.0, sh=0.15)
    s.line([(hx - 2, hy + 5), (hx - 1, hy + 6), (hx, hy + 6),
            (hx + 1, hy + 6), (hx + 2, hy + 5)], FUR[3])


def kiss_lean(s):
    """Frame 0: turned to each other in profile, the paw-hold between them,
    muzzles a breath apart."""
    _basil_profile(s, ox=14, oy=48, lean=1)
    _kitty_side_core(s, ox=34, oy=48, lean=1, arm=False)
    # the paw-hold: his sleeve reaches east, her arm west, paws meeting
    s.capsule(37, 71, 43, 75, 1.8, 1.5, COATR, sh=0.24)
    s.ball(45, 76.5, 1.8, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.capsule(57, 79, 51, 77, 1.7, 1.5, KIT_FUR, sh=0.08)
    s.ball(48.5, 76.5, 1.7, 1.5, KIT_FUR, power=2.2, wrap=0.10, curve=0.10)
    s.despeckle(passes=1)
    s.outline(KISS_OUTS, OUT_DARK)
    for (x, y) in ((47, 67), (48, 66), (47, 71)):          # his whiskers
        s.set(x, y, WHISK)
    _kitty_side_whiskers(s, 58, 69)


def kiss_kiss(s):
    """Frame 1: THE KISS — chins tipped up, muzzles touching at the center,
    closed ^ eyes, her paw up on his chest, his tail curled high. The heart
    fx blooms above at runtime (prologue_fx cell 19)."""
    _basil_profile(s, ox=16, oy=48, lean=2, kiss=True)
    # bob=-2 tips her onto TIPTOE: body lifts, paws stay planted — the
    # 3px head-height difference closes and the muzzles actually meet
    _kitty_side_core(s, ox=32, oy=48, bob=-2, lean=2, eyes="closed", arm=False)
    s.set(54, 68, BLUSH)                                   # her blush
    # his paw finds her back; hers lands on his chest
    s.capsule(39, 71, 47, 76, 1.8, 1.5, COATR, sh=0.24)
    s.ball(56, 76, 1.8, 1.5, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.capsule(55, 78, 49, 73, 1.7, 1.5, KIT_FUR, sh=0.08)
    s.ball(47.5, 72, 1.7, 1.5, KIT_FUR, power=2.2, wrap=0.10, curve=0.10)
    s.despeckle(passes=1)
    s.outline(KISS_OUTS, OUT_DARK)
    for (x, y) in ((44, 62), (43, 61)):                    # whisker breaks
        s.set(x, y, WHISK)
    s.set(59, 63, WHISK)


def kiss_after(s):
    """Frame 2: the after — both from BEHIND at the lip, close, her head
    resting on his shoulder, tails curling toward each other. Held on the
    sun lane before the fade."""
    _basil_back(s, ox=17, oy=48, head_dx=1, tail_up=False)
    _kitty_back_core(s, ox=33, oy=48, head_dx=-4, head_dy=3)
    _kitty_tail_curl(s, 57, 48, 0, west=True)
    s.despeckle(passes=1)
    s.outline(KISS_OUTS, OUT_DARK)


# ---- Fuji, the librarian (the Ebb night, 2026-07-19) ---------------------------------------
# npc_fuji_gen.png on the NPC-kit contract (npc.gd builds SpriteFrames at
# runtime; spawn with frame_cols = 10):
#   cols 0-1  idle_down — planted / bob+step: the pair doubles as the 2-frame
#             walk (idle_down is the Theater helpers' single-facing fallback)
#   cols 2-3  act   — the WAND CAST: a slim BRASS wand raised mid-cast with a
#             tiny glass BEAD tip (brass-and-flask, never a fairy wand);
#             frame 3 (the bob cell) adds the cast flicker at the bead
#   cols 4-5  emote — STARTLED: ears pinned flat, shoulders hunched up, wide
#             eyes, startle ticks over the head
#   cols 6-7  back  — hooded robe from behind (npc.gd builds it frame_cols>=8)
#   cols 8-9  side  — profile at the counter, tome under her arm; stored
#             facing LEFT per the kit contract, play_side(true) flips her east
# Geometry is her CANONICAL player sheet's (assets/_gen_fuji_sprites.py: head
# cy=18, long robe 22..hem 40, feet fill y=44) — redrawn self-contained here
# because that generator writes fuji_gen.png at import (module-level build).

F_FUR, F_GING, F_CREAM = FUJI["FUR"], FUJI["GINGER"], FUJI["CREAM"]
F_ROBE, F_TRIM = FUJI["ROBE"], FUJI["TRIM"]
F_RIM, F_LENS, F_BOOK = FUJI["RIM"], FUJI["LENS"], FUJI["BOOK"]
F_EYE, F_EYEL = FUJI["EYE_G"], FUJI["EYE_GL"]
F_PUPIL, F_GLINT = FUJI["PUPIL"], FUJI["GLINT"]
F_NOSE, F_MOUTH = FUJI["NOSE"], FUJI["MOUTH"]
F_EARIN, F_EARIN_D = FUJI["EARIN"], FUJI["EARIN_D"]
F_WHISK = FUJI["WHISK"]
FUJI_OUTS = dict(FUJI["OUTS"])
F_OUT = FUJI["OUT_FALLBACK"]
FHEM = 40                                          # near-floor robe hem


def _fuji_eye(s, ex, ey, wide=False):
    """3x3 green-gold eye behind the lens; wide = the startled pinprick."""
    s.rect(ex, ey, ex + 2, ey + 2, F_EYE)
    s.rect(ex, ey, ex + 2, ey, F_EYEL)
    if wide:
        s.set(ex + 1, ey + 2, F_PUPIL)
    else:
        s.rect(ex + 1, ey + 1, ex + 1, ey + 2, F_PUPIL)


def _fuji_specs_down(s, hx, hy):
    """Round brass reading glasses ON the face — the eyes ARE the lenses."""
    for ex, sh in ((hx - 5, 0), (hx + 3, 1)):
        s.rect(ex, hy - 3, ex + 2, hy - 3, F_RIM[sh])       # top rim
        s.rect(ex, hy + 1, ex + 2, hy + 1, F_RIM[sh + 1])   # bottom rim
        for ry, rc in ((hy - 2, F_RIM[sh]), (hy - 1, F_RIM[sh + 1]),
                       (hy, F_RIM[sh + 1])):
            s.set(ex - 1, ry, rc)
            s.set(ex + 3, ry, rc)
        s.set(ex + 2, hy - 2, F_LENS[0])                    # glass shine
    s.rect(hx - 1, hy - 2, hx + 1, hy - 2, F_RIM[2])        # bridge


def fuji_head_down(s, dy=0, eyes="open", ears="up"):
    """Split tortie ears (left black / right ginger), placed rust patches,
    cream muzzle, green-gold eyes behind the brass specs."""
    hx, hy = CX, 18 + dy
    if ears == "up":
        s.tri((hx - 4, hy - 10), hy - 4, hx - 7, hx - 1, F_FUR)
        s.tri((hx + 4, hy - 10), hy - 4, hx + 1, hx + 7, F_GING, sh=0.15)
        s.tri((hx - 4, hy - 8), hy - 5, hx - 5, hx - 3, F_EARIN)
        s.tri((hx + 4, hy - 8), hy - 5, hx + 3, hx + 5, F_EARIN_D)
    else:                                          # pinned flat (startled)
        s.tri((hx - 8, hy - 3), hy, hx - 6, hx - 1, F_FUR)
        s.tri((hx + 8, hy - 3), hy, hx + 1, hx + 6, F_GING, sh=0.15)
    s.ball(hx, hy, 7.2, 6.0, F_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(hx + 2, hy - 4, hx + 5, hy - 3, F_GING[1])       # right brow patch
    s.set(hx + 6, hy - 2, F_GING[2])
    s.rect(hx - 6, hy + 1, hx - 5, hy + 2, F_GING[2])       # left cheek fleck
    s.ball(hx, hy + 4, 4.6, 2.9, F_CREAM, power=2.2, wrap=0.10, curve=0.10)
    s.rect(hx - 1, hy + 2, hx, hy + 2, F_NOSE)
    if eyes == "wide":                             # startled: little o mouth
        s.rect(hx - 1, hy + 4, hx, hy + 5, F_MOUTH)
        s.set(hx, hy + 4, MAW)
        _fuji_eye(s, hx - 5, hy - 2, wide=True)
        _fuji_eye(s, hx + 3, hy - 2, wide=True)
    else:
        s.line([(hx - 1, hy + 4), (hx, hy + 4)], F_MOUTH)
        _fuji_eye(s, hx - 5, hy - 2)
        _fuji_eye(s, hx + 3, hy - 2)
    _fuji_specs_down(s, hx, hy)


def fuji_whiskers_down(s, dy=0):
    """Post-outline cheek strokes (the whisker rule)."""
    for (x, y) in ((15, 21), (14, 21), (15, 23), (14, 24),
                   (33, 21), (34, 21), (33, 23), (34, 24)):
        s.set(x, y + dy, F_WHISK)


def fuji_legs_down(s, liftL=0, liftR=0):
    """Dark stubs + cream paws under the hem (feet fill y=44)."""
    for (lx, lift, sh) in ((21, liftL, 0.0), (27, liftR, 0.10)):
        fy = 42 - lift
        s.capsule(lx, 33, lx, fy - 2, 2.2, 1.7, F_FUR, sh=sh)
        s.ball(lx, fy + 0.6, 2.2, 1.7, F_CREAM, power=2.2, sh=sh * 0.5,
               wrap=0.10, curve=0.10)


def fuji_robe_down(s, dy=0, back=False):
    """The near-floor plum robe, flat CT bands: lit field west of center, mid
    field east, hard shade band screen-right, mustard trim stripe + placket.
    back=True swaps the placket/chest for the draped hood + vent seam."""
    top, hem = 22 + dy, FHEM + dy
    h = hem - top
    for y in range(top, hem + 1):
        vy = (y - top) / h
        half = 5.6 + 2.0 * vy
        x0, x1 = int(round(CX - half)), int(round(CX + half))
        if y == top:
            x0 += 2
            x1 -= 2
        elif y == top + 1:
            x0 += 1
            x1 -= 1
        for x in range(x0, x1 + 1):
            if y >= hem - 1:                       # hem band
                c = F_ROBE[3] if x >= x1 - 1 else F_ROBE[2]
            elif x >= x1 - 1:                      # shade band, screen-right
                c = F_ROBE[2]
            elif y == hem - 2:                     # mustard trim stripe
                c = F_TRIM[2]
            elif x < CX:                           # lit field
                c = F_ROBE[0]
            else:                                  # mid field
                c = F_ROBE[1]
            s.set(x, y, c)
    s.rect(CX - 5, hem + 1, CX + 5, hem + 1, F_ROBE[3])     # turn-under
    if back:
        s.tri((CX, top + 7), top, CX - 5, CX + 5, F_ROBE, sh=0.42)   # hood
        s.set(CX, top + 7, F_ROBE[3])                       # hood point
        s.rect(CX - 5, top, CX + 5, top, F_ROBE[3])         # hood roll
        for y in range(top + 9, hem - 2):                   # vent seam
            s.set(CX, y, F_ROBE[2])
        return
    for y in range(top + 4, hem - 2):                       # trim placket
        s.set(CX, y, F_TRIM[1])
    s.tri((CX, top), top + 3, CX - 2, CX + 2, F_CREAM)      # cream chest
    s.rect(CX - 1, top + 2, CX, top + 2, F_TRIM[0])         # throat clasp


def fuji_book_carry(s, dy=0):
    """The tome hugged to her chest, cover out, sleeves wrapping in."""
    y0, y1 = 24 + dy, 30 + dy
    for y in range(y0, y1 + 1):
        for x in range(21, 28):
            if y == y1:
                c = F_CREAM[2]                     # page block
            elif x >= 26:
                c = F_BOOK[2]                      # shade band
            elif x <= 22:
                c = F_BOOK[0]                      # lit field
            else:
                c = F_BOOK[1]
            s.set(x, y, c)
    s.rect(21, y0, 21, y1 - 1, F_BOOK[3])          # spine
    s.set(27, y0 + 3, F_TRIM[1])                   # brass clasp
    s.capsule(18, 23 + dy, 19.5, 26 + dy, 1.8, 1.5, F_ROBE, sh=0.18)
    s.capsule(30, 23 + dy, 28.5, 26 + dy, 1.8, 1.5, F_ROBE, sh=0.30)
    s.ball(19.5, 28 + dy, 1.6, 1.4, F_CREAM, power=2.2, wrap=0.10, curve=0.10)
    s.ball(28.5, 28 + dy, 1.6, 1.4, F_CREAM, power=2.2, sh=0.12, wrap=0.10,
           curve=0.10)


def fuji_tail_down(s, bob=0, sway=0):
    """Black tail curling east of the hem, RUST TIP — the tortie signature."""
    tx, ty = 30, 33 + bob
    s.capsule(tx, ty + 1, tx + 3, ty - 3, 1.7, 1.4, F_FUR, sh=0.08)
    s.capsule(tx + 3, ty - 3, tx + 4 + sway, ty - 7, 1.4, 1.1, F_FUR, sh=0.12)
    s.set(tx + 2, ty - 1, F_GING[2])                        # mid patch
    s.set(tx + 3 + sway, ty - 8, F_GING[1])                 # rust tip
    s.set(tx + 4 + sway, ty - 8, F_GING[1])


def _fuji_wand(s, bob=0, spark=False):
    """The slim BRASS wand off the raised paw, drawn POST-outline (the bindle
    lesson: the grip pixel overwrites the fist — pole through the paw). A 1px
    tip-to-grip shaft in her spectacle brass, a tiny glass BEAD at the tip."""
    for i, (x, y) in enumerate(((34, 12), (35, 11), (36, 10), (37, 9),
                                (38, 8))):
        s.set(x, y + bob, F_RIM[0] if i % 2 else F_RIM[1])
    s.set(39, 7 + bob, F_LENS[0])                  # the glass bead
    s.set(40, 6 + bob, F_GLINT)                    # bead shine
    if spark:                                      # cast flicker (frame 2)
        s.set(41, 4 + bob, MSPARK)
        s.set(38, 5 + bob, MSPARK_V)


def fuji_npc(s, mood="idle", bob=0, step=0):
    """Down-facing cells. mood: idle (tome hugged — the pair doubles as the
    walk; step=1 lifts the left paw), act (wand cast), emote (startled)."""
    fuji_tail_down(s, bob, 1 if (mood == "act" or step) else 0)
    fuji_legs_down(s, liftL=step)
    fuji_robe_down(s, bob)
    if mood == "act":
        # tome dropped to the off (west) arm's side; wand arm flung up east
        s.capsule(18, 23 + bob, 16, 28 + bob, 1.8, 1.6, F_ROBE, sh=0.18)
        s.ball(16, 30 + bob, 1.7, 1.5, F_CREAM, power=2.2, wrap=0.10,
               curve=0.10)
        s.capsule(30, 23 + bob, 33, 15 + bob, 1.8, 1.5, F_ROBE, sh=0.30)
        s.ball(33.5, 13.5 + bob, 1.6, 1.4, F_CREAM, power=2.2, wrap=0.10,
               curve=0.10)
        fuji_head_down(s, bob)
    elif mood == "emote":
        # STARTLED: shoulders hunched high, paws up at the chest, the head
        # sunk 1px into the collar, ears pinned, eyes wide
        s.capsule(19, 23 + bob, 18, 26 + bob, 1.9, 1.7, F_ROBE, sh=0.18)
        s.capsule(29, 23 + bob, 30, 26 + bob, 1.9, 1.7, F_ROBE, sh=0.30)
        s.ball(18, 27.5 + bob, 1.6, 1.4, F_CREAM, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(30, 27.5 + bob, 1.6, 1.4, F_CREAM, power=2.2, sh=0.12,
               wrap=0.10, curve=0.10)
        fuji_head_down(s, bob + 1, eyes="wide", ears="flat")
    else:
        fuji_book_carry(s, bob)
        fuji_head_down(s, bob)
    s.despeckle(passes=1)
    s.outline(FUJI_OUTS, F_OUT)
    fuji_whiskers_down(s, bob + (1 if mood == "emote" else 0))
    if mood == "act":
        _fuji_wand(s, bob, spark=(bob != 0))
    elif mood == "emote":
        for (x, y) in ((14, 7 + bob), (24, 4 + bob), (34, 7 + bob)):
            s.set(x, y, SPARK_D)                   # startle ticks, post-outline


def fuji_npc_back(s, bob=0):
    """From behind: hooded robe, crown rust patch, spectacle temple hooks,
    the hug's elbows poking past the robe, raised rust-tip tail."""
    fuji_legs_down(s)
    fuji_robe_down(s, bob, back=True)
    for (sx, dxx, sh) in ((18, -1.5, 0.20), (30, 1.5, 0.34)):   # hug elbows
        s.capsule(sx, 23 + bob, sx + dxx, 26.5 + bob, 1.8, 1.5, F_ROBE, sh=sh)
    s.capsule(29, 31 + bob, 32, 27 + bob, 1.7, 1.4, F_FUR, sh=0.10)   # tail
    s.capsule(32, 27 + bob, 32, 22 + bob, 1.4, 1.1, F_FUR, sh=0.14)
    s.set(32, 21 + bob, F_GING[1])                 # rust tip
    hy = 18 + bob
    s.tri((CX - 4, hy - 10), hy - 4, CX - 7, CX - 1, F_FUR)     # ear backs
    s.tri((CX + 4, hy - 10), hy - 4, CX + 1, CX + 7, F_GING, sh=0.15)
    s.tri((CX - 4, hy - 8), hy - 5, CX - 6, CX - 2, F_FUR, sh=0.38)
    s.tri((CX + 4, hy - 8), hy - 5, CX + 2, CX + 6, F_GING, sh=0.46)
    s.ball(CX, hy, 7.2, 6.0, F_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(CX - 5, hy - 3, CX - 2, hy - 1, F_GING[1])           # crown patch
    s.set(CX + 3, hy + 2, F_GING[2])
    s.set(CX - 6, hy - 1, F_RIM[2])                # temple hooks
    s.set(CX + 6, hy - 1, F_RIM[2])
    s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
            (CX + 1, hy + 6), (CX + 2, hy + 5)], F_FUR[3])      # neck part
    s.despeckle(passes=1)
    s.outline(FUJI_OUTS, F_OUT)


def _fuji_mirror(s):
    """Her side cells are authored right-facing; the kit stores left-facing
    (see _mirror_cell)."""
    _mirror_cell(s)


def fuji_robe_side(s, dy=0):
    """Robe in RIGHT-facing profile: straight dark front edge east, trim
    closure column inside it, lit band along the back, trailing fold."""
    top, hem = 22 + dy, FHEM + dy
    h = hem - top
    for y in range(top, hem + 1):
        vy = (y - top) / h
        x0, x1 = int(round(17 - vy * 3.0)), 29
        if y == top:
            x0 += 2
            x1 -= 1
        elif y == top + 1:
            x0 += 1
        fold = x0 + 3
        for x in range(x0, x1 + 1):
            if y >= hem - 1:                       # hem band
                c = F_ROBE[3] if x >= x1 - 1 else F_ROBE[2]
            elif x == x1:                          # dark front edge
                c = F_ROBE[3] if y >= top + 2 else F_ROBE[2]
            elif x == x1 - 1:                      # trim closure column
                c = F_TRIM[2] if y >= top + 3 else F_ROBE[2]
            elif y == hem - 2:                     # trim stripe
                c = F_TRIM[2]
            elif x == fold and y >= top + 4:       # trailing fold crease
                c = F_ROBE[2]
            elif x <= x0 + 2:                      # lit back
                c = F_ROBE[0]
            else:                                  # mid field
                c = F_ROBE[1]
            s.set(x, y, c)
    s.rect(16, hem + 1, 27, hem + 1, F_ROBE[3])    # turn-under


def fuji_head_side(s, dy=0):
    """RIGHT-facing profile head: near black ear tall, far ginger ear front,
    plump cream cheek, one lens with the temple arm running back."""
    hx, hy = 23, 18 + dy
    s.tri((hx + 3, hy - 10), hy - 5, hx + 1, hx + 5, F_GING, sh=0.30)  # far ear
    s.tri((hx - 1, hy - 11), hy - 5, hx - 3, hx + 1, F_FUR)     # near ear
    s.tri((hx - 1, hy - 9), hy - 6, hx - 2, hx, F_EARIN)
    s.ball(hx, hy, 6.8, 5.6, F_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.rect(hx - 4, hy - 3, hx - 2, hy - 1, F_GING[1])           # nape patch
    s.set(hx - 1, hy + 2, F_GING[2])                            # cheek fleck
    s.ball(hx + 4, hy + 2.5, 3.2, 2.7, F_FUR, power=2.0, wrap=0.30)
    s.ball(hx + 4.5, hy + 3.2, 3.2, 2.5, F_CREAM, power=2.0, wrap=0.10,
           curve=0.10)
    s.rect(hx + 6, hy + 2, hx + 7, hy + 2, F_NOSE)              # stub nose
    s.line([(hx + 5, hy + 4), (hx + 6, hy + 4)], F_MOUTH)
    _fuji_eye(s, hx + 2, hy - 3)
    s.rect(hx + 2, hy - 4, hx + 4, hy - 4, F_RIM[0])            # top rim
    s.rect(hx + 2, hy, hx + 4, hy, F_RIM[1])                    # bottom rim
    for ry, rc in ((hy - 3, F_RIM[0]), (hy - 2, F_RIM[1]), (hy - 1, F_RIM[1])):
        s.set(hx + 1, ry, rc)
        s.set(hx + 5, ry, rc)
    s.set(hx + 4, hy - 3, F_LENS[0])                            # glass shine
    s.rect(hx - 4, hy - 4, hx + 1, hy - 4, F_RIM[2])            # temple arm


def fuji_book_side(s, dy=0):
    """The tome under her near arm, edge-on: cream page stripe, sleeve over."""
    y = 28 + dy
    for x in range(20, 30):
        s.set(x, y - 1, F_BOOK[1])
        s.set(x, y, F_CREAM[1])                    # pages, edge-on
        s.set(x, y + 1, F_BOOK[2])
    s.rect(20, y - 1, 20, y + 1, F_BOOK[3])        # spine cap
    s.rect(29, y - 1, 29, y + 1, F_BOOK[3])        # fore-edge cap
    s.capsule(23, 23 + dy, 24.5, 27 + dy, 1.8, 1.5, F_ROBE, sh=0.24)
    s.ball(28, 30.5 + dy, 1.4, 1.2, F_CREAM, power=2.2, wrap=0.10, curve=0.10)


def fuji_npc_side(s, bob=0):
    """Profile standing at the counter, tome tucked under the near arm."""
    s.capsule(16, 30 + bob, 13, 28 + bob, 1.7, 1.4, F_FUR, sh=0.10)   # tail
    s.capsule(13, 28 + bob, 10, 26 + bob, 1.4, 1.1, F_FUR, sh=0.13)
    s.set(12, 27 + bob, F_GING[2])                 # mid patch
    s.set(9, 25 + bob, F_GING[1])                  # rust tip
    for (lx, sh) in ((20, 0.16), (25, 0.0)):       # legs: back then front
        s.capsule(lx, 33, lx, 40, 2.1, 1.7, F_FUR, sh=sh)
        s.ball(lx + 0.5, 42.6, 2.2, 1.7, F_CREAM, power=2.2, sh=sh * 0.4,
               wrap=0.10, curve=0.10)
    fuji_robe_side(s, bob)
    fuji_book_side(s, bob)
    fuji_head_side(s, bob)
    s.despeckle(passes=1)
    s.outline(FUJI_OUTS, F_OUT)
    for (x, y) in ((32, 19 + bob), (33, 19 + bob), (34, 20 + bob),
                   (32, 22 + bob), (33, 23 + bob)):
        s.set(x, y, F_WHISK)                       # profile whiskers
    _fuji_mirror(s)


# ---- the Lanternwood trio (the Ebb night, 2026-07-20) --------------------------------------
# Three winter villagers out in Lanternwood's snowy street the night the
# magic died (scene/lanternwood.gd spawns each at frame_cols = 6 — the plain
# [idle x2, act x2, emote x2] contract). Ebb-night cool cast on the Paper
# Girls law — pale blue-whites and steel indigos with violet-law darks, never
# gray mud — plus ONE warm accent each: Bramble's russet scarf, Alder's amber
# knit cap, Pip's own rust fur. Every held charm is DEAD on purpose: honest
# wood, cold stone, dark glass — no glow pixels anywhere on these sheets.

# 2026-07-29 less-kiddy pass. The old seed (228,232,250) sat at L=0.94, where
# the ramp's lit tone clamps to pure white and tones 0-1 collapse into each
# other: a flat cotton-wool rabbit with no form, and the pale end of the whole
# Lanternwood cast. HARE_FUR is now HAND-PINNED, because the derived version of
# a near-white blue seed comes back with a (104,74,228) core — a hot candy
# blue-violet, the same trap that makes BRASS[2..3] unusable. This walk is a
# cool blue-white ramp with real internal contrast and violet-slate darks:
# lower L, hue held, no beige/gray mud in it anywhere.
HARE_FUR = [(238, 244, 252, 255), (194, 206, 240, 255),
            (140, 148, 212, 255), (92, 92, 168, 255)]
HARE_IN = ramp((158, 138, 190), "violet", 4)       # cool violet inner ear
HARE_SCARF = ramp((184, 86, 46), "violet", 4)      # chunky russet knit — HER accent
HARE_EYE, HARE_EYEL = (146, 200, 236, 255), (198, 228, 248, 255)
HARE_OUTS = outs_for((HARE_FUR, OUT_LIGHT), (WHITE, OUT_LIGHT),
                     (HARE_IN, OUT_LIGHT), (HARE_SCARF, OUT_DARK))


def hare(s, mood="idle", bob=0, liftL=0, liftR=0):
    """Bramble, the flustered snow hare: pale blue-white fur, LONG upright
    ears running toward the cell top (art crests y=3 so the outline keeps
    1px inside), chunky russet scarf, big split feet. act = the dead
    warming-wand held UP TO one long ear — the ear folds down to meet it,
    listening, baffled (slim honest wood, clearly INERT). emote = both paws
    thrown up, the ears crossed back into an X of exasperation."""
    hy, by = 21 + bob, 35 + bob
    # -- ears first, behind the head ------------------------------------
    if mood == "emote":                             # crossed back: an X
        s.capsule(CX - 3, hy - 4, CX + 5, hy - 15, 1.9, 1.4, HARE_FUR, sh=0.04)
        s.capsule(CX + 3, hy - 4, CX - 5, hy - 15, 1.9, 1.4, HARE_FUR, sh=0.14)
    else:
        s.capsule(CX - 3, hy - 4, CX - 4, hy - 17, 1.9, 1.4, HARE_FUR, sh=0.04)
        s.capsule(CX - 3.5, hy - 9, CX - 4, hy - 15, 0.9, 0.7, HARE_IN)
        if mood == "act":                           # east ear leans to the wand
            s.capsule(CX + 3, hy - 4, CX + 8, hy - 8, 1.9, 1.4, HARE_FUR,
                      sh=0.14)
            s.capsule(CX + 4, hy - 6, CX + 7, hy - 8, 0.9, 0.7, HARE_IN,
                      sh=0.30)
        else:
            s.capsule(CX + 3, hy - 4, CX + 4, hy - 17, 1.9, 1.4, HARE_FUR, sh=0.14)
            s.capsule(CX + 3.5, hy - 9, CX + 4, hy - 15, 0.9, 0.7, HARE_IN,
                      sh=0.30)
    # -- feet / body / tail ---------------------------------------------
    for (fx_, lift, sh) in ((CX - 3, liftL, 0.0), (CX + 3, liftR, 0.10)):
        s.ball(fx_, 43 - lift, 2.7, 1.6, HARE_FUR, power=2.2, sh=sh, wrap=0.10,
               curve=0.10)                             # big hare feet
    s.ball(CX, by, 6.8, 6.4, HARE_FUR, power=2.2, wrap=0.28, curve=0.22)
    s.ball(CX, by + 1, 3.8, 3.4, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.ball(CX + 7.5, by + 3, 1.8, 1.6, WHITE, power=2.2, sh=0.10,
           wrap=0.10, curve=0.10)                   # snow-puff tail
    # -- arms per mood --------------------------------------------------
    if mood == "act":                               # east arm raises the wand
        s.capsule(CX - 6.5, by - 4, CX - 7.5, by + 1, 1.7, 1.5, HARE_FUR,
                  sh=0.06)
        s.ball(CX - 7.5, by + 2, 1.6, 1.4, WHITE, power=2.2, wrap=0.10,
               curve=0.10)
        s.capsule(CX + 6, by - 4, CX + 8, hy - 2, 1.7, 1.4, HARE_FUR, sh=0.16)
        s.ball(CX + 8, hy - 2, 1.7, 1.5, WHITE, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
    elif mood == "emote":                           # both paws thrown up
        s.capsule(CX - 5.5, by - 3, CX - 9, by - 12, 1.7, 1.4, HARE_FUR,
                  sh=0.06)
        s.capsule(CX + 5.5, by - 3, CX + 9, by - 12, 1.7, 1.4, HARE_FUR,
                  sh=0.16)
        s.ball(CX - 9, by - 13, 1.7, 1.5, WHITE, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 9, by - 13, 1.7, 1.5, WHITE, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
    else:
        s.capsule(CX - 6.5, by - 4, CX - 7.5, by + 1, 1.7, 1.5, HARE_FUR,
                  sh=0.06)
        s.capsule(CX + 6.5, by - 4, CX + 7.5, by + 1, 1.7, 1.5, HARE_FUR,
                  sh=0.16)
        s.ball(CX - 7.5, by + 2, 1.6, 1.4, WHITE, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 7.5, by + 2, 1.6, 1.4, WHITE, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
    # -- the chunky knitted scarf (flat bands + deliberate rib ticks) ---
    sy = hy + 7
    s.rect(CX - 5, sy, CX + 5, sy, HARE_SCARF[0])
    s.rect(CX - 5, sy + 1, CX + 5, sy + 1, HARE_SCARF[1])
    s.rect(CX - 5, sy + 2, CX + 5, sy + 2, HARE_SCARF[2])
    for rx in range(CX - 4, CX + 5, 2):
        s.set(rx, sy + 1, HARE_SCARF[2])            # knit ribs
    s.rect(CX + 2, sy + 3, CX + 4, sy + 8, HARE_SCARF[1])   # hanging end
    s.rect(CX + 4, sy + 3, CX + 4, sy + 8, HARE_SCARF[2])
    for fx_ in (CX + 2, CX + 4):                    # fringe
        s.set(fx_, sy + 9, HARE_SCARF[2])
    # -- head -----------------------------------------------------------
    s.ball(CX, hy, 6.8, 6.0, HARE_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.ball(CX, hy + 4, 4.4, 2.7, WHITE, power=2.2, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    ey = hy - 2
    if mood == "emote":                             # shut-flat + shouting
        _closed(s, CX - 5, ey, happy=False)
        _closed(s, CX + 3, ey, happy=False)
        s.rect(CX - 2, hy + 4, CX + 1, hy + 5, MAW)
    else:
        _eye(s, CX - 5, ey, HARE_EYE, HARE_EYEL)
        _eye(s, CX + 3, ey, HARE_EYE, HARE_EYEL)
        if mood == "act":                           # baffled little o
            s.rect(CX - 1, hy + 4, CX, hy + 5, MAW)
        else:
            s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    s.despeckle(passes=1)
    s.outline(HARE_OUTS, OUT_LIGHT)
    whiskers_kid_down(s, bob - 7)
    if mood == "act":                               # the INERT wand, post-outline
        for i, wy in enumerate(range(hy - 11, hy + 3)):     # (the grip law:
            s.set(CX + 8, wy, WOODF[1] if i % 2 else WOODF[2])  # pole through
        s.set(CX + 8, hy - 12, WOODF[3])            # the paw) — dead dark tip


def hare_back(s, bob=0, liftL=0, liftR=0):
    """Bramble from BEHIND (2026-07-29). Two reads and nothing else: the long
    ear BACKS (no violet inner — that lining only exists on the front of an
    ear) and the COTTONTAIL, a pale puff sitting low on the rump. She is an
    ADULT hare, so the skull stays small against a long trunk rather than the
    kid-cat's half-figure head. Her paws are WHITE on a near-white flank, so
    every one of them carries a shadow tint or it disappears."""
    hy, by = 21 + bob, 35 + bob
    s.capsule(CX - 3, hy - 4, CX - 4, hy - 17, 1.9, 1.4, HARE_FUR, sh=0.30)
    s.capsule(CX + 3, hy - 4, CX + 4, hy - 17, 1.9, 1.4, HARE_FUR, sh=0.38)
    for (fx_, lift, sh) in ((CX - 3, liftL, 0.16), (CX + 3, liftR, 0.26)):
        s.ball(fx_, 43 - lift, 2.7, 1.6, HARE_FUR, power=2.2, sh=sh, wrap=0.10,
               curve=0.10)
    s.ball(CX, by, 6.8, 6.4, HARE_FUR, power=2.2, wrap=0.28, curve=0.22)
    s.capsule(CX - 6.5, by - 4, CX - 7.5, by + 1, 1.7, 1.5, HARE_FUR, sh=0.16)
    s.capsule(CX + 6.5, by - 4, CX + 7.5, by + 1, 1.7, 1.5, HARE_FUR, sh=0.26)
    s.ball(CX - 7.5, by + 2, 1.6, 1.4, WHITE, power=2.2, sh=0.34, wrap=0.10,
           curve=0.10)                              # tinted, or it vanishes
    s.ball(CX + 7.5, by + 2, 1.6, 1.4, WHITE, power=2.2, sh=0.46, wrap=0.10,
           curve=0.10)
    s.ball(CX, by + 5, 2.8, 2.2, WHITE, power=2.0, sh=0.30, wrap=0.16,
           curve=0.12)                              # THE COTTONTAIL, low on
                                                    # the rump — mid-back it
                                                    # just read as a belly
    # the scarf from the nape: the band round, the end still hanging east
    sy = hy + 7
    s.rect(CX - 5, sy, CX + 5, sy, HARE_SCARF[1])
    s.rect(CX - 5, sy + 1, CX + 5, sy + 1, HARE_SCARF[2])
    s.rect(CX - 5, sy + 2, CX + 5, sy + 2, HARE_SCARF[3])
    for rx in range(CX - 4, CX + 5, 2):
        s.set(rx, sy + 1, HARE_SCARF[3])            # knit ribs
    s.rect(CX + 2, sy + 3, CX + 4, sy + 8, HARE_SCARF[2])
    s.rect(CX + 4, sy + 3, CX + 4, sy + 8, HARE_SCARF[3])
    for fx_ in (CX + 2, CX + 4):
        s.set(fx_, sy + 9, HARE_SCARF[3])
    s.ball(CX, hy, 6.8, 6.0, HARE_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
            (CX + 1, hy + 6), (CX + 2, hy + 5)], HARE_FUR[3])   # nape part
    s.despeckle(passes=1)
    s.outline(HARE_OUTS, OUT_LIGHT)


def hare_side(s, bob=0, fF=(0, 0), fB=(0, 0)):
    """Bramble in PROFILE, drawn facing RIGHT and mirrored last (the npc kit
    stores left-facing side cells). The near ear runs full height with its
    violet lining showing, the far one hangs back shaded; the long hare muzzle
    and the scarf's hanging end are the front read, the cottontail the rear."""
    hx, hy, by = 22, 21 + bob, 35 + bob
    s.capsule(hx + 2, hy - 4, hx + 4, hy - 16, 1.8, 1.3, HARE_FUR, sh=0.36)
    s.capsule(hx - 1, hy - 4, hx - 1, hy - 17, 1.9, 1.4, HARE_FUR, sh=0.04)
    s.capsule(hx - 1, hy - 9, hx - 1, hy - 15, 0.9, 0.7, HARE_IN)
    s.ball(15, by + 3, 2.6, 2.2, WHITE, power=2.0, sh=0.32, wrap=0.16,
           curve=0.12)                              # the cottontail, west
    for (base_x, (dx, lift), sh) in ((19, fB, 0.24), (26, fF, 0.0)):
        lx = base_x + dx
        s.capsule(lx, 39 + bob, lx, 42 - lift, 2.0, 1.7, HARE_FUR, sh=sh)
        s.ball(lx + 0.5, 43 - lift, 2.7, 1.6, HARE_FUR, power=2.2, sh=sh,
               wrap=0.10, curve=0.10)
    s.ball(22, by, 6.4, 6.2, HARE_FUR, power=2.2, wrap=0.28, curve=0.22)
    s.ball(25, by + 1, 3.0, 3.0, WHITE, power=2.2, sh=0.12, wrap=0.10,
           curve=0.10)                              # the bib, toward the front
    s.capsule(23, by - 4, 24.5, by + 1, 1.7, 1.5, HARE_FUR, sh=0.14)  # near arm
    s.ball(24.5, by + 2, 1.6, 1.4, WHITE, power=2.2, sh=0.30, wrap=0.10,
           curve=0.10)
    # the NECK — without it the scarf floated in the gap between skull and
    # trunk and came out an outlined box hanging in mid air
    s.capsule(22, hy + 3, 22, by - 4, 3.4, 3.8, HARE_FUR, sh=0.22)
    sy = hy + 6
    s.rect(hx - 4, sy, hx + 5, sy, HARE_SCARF[0])
    s.rect(hx - 4, sy + 1, hx + 5, sy + 1, HARE_SCARF[1])
    s.rect(hx - 4, sy + 2, hx + 5, sy + 2, HARE_SCARF[2])
    for rx in range(hx - 3, hx + 5, 2):
        s.set(rx, sy + 1, HARE_SCARF[2])
    s.rect(hx + 3, sy + 3, hx + 5, sy + 8, HARE_SCARF[1])
    s.rect(hx + 5, sy + 3, hx + 5, sy + 8, HARE_SCARF[2])
    for fx_ in (hx + 3, hx + 5):
        s.set(fx_, sy + 9, HARE_SCARF[2])
    s.ball(hx, hy, 6.4, 5.8, HARE_FUR, power=2.4, wrap=0.34, curve=0.30)
    # a SHORT rounded snout: run out as a long tapered capsule it read as a
    # duck's bill, which is the wrong animal and the wrong register
    s.ball(hx + 4.5, hy + 3.2, 3.6, 2.4, WHITE, power=2.0, wrap=0.12,
           curve=0.10)
    s.rect(hx + 8, hy + 2, hx + 8, hy + 3, NOSE)
    _eye(s, hx + 1, hy - 2, HARE_EYE, HARE_EYEL)
    s.line([(hx + 6, hy + 5), (hx + 7, hy + 5)], MOUTH)
    s.despeckle(passes=1)
    s.outline(HARE_OUTS, OUT_LIGHT)
    for (x, y) in ((hx + 9, hy + 1), (hx + 10, hy + 3)):
        s.set(x, y, WHISK)                  # post-outline: despeckle eats specks
    _mirror_cell(s)


# 2026-07-29 less-kiddy pass: fur and coat drop L and gain S with the spread
# up, so an old woodworker in a heavy winter coat has weight in him. BEAV_CAP is
# now HAND-PINNED — an amber seed's derived darks came back (225,15,28) and
# (179,4,101), fire-engine red and magenta, which is exactly the violet law's
# BRASS[2..3] trap and exactly the "very kiddy" failure mode. His muzzle drops
# off near-white (it was L=0.82, S=0.11 — mud) to a violet-grey with the flecks
# re-tuned darker, since the old flecks now matched the muzzle and vanished.
BEAV_FUR = ramp((138, 92, 74), "violet", 4, spread=1.1)     # riverbank brown
BEAV_COAT = ramp((74, 94, 152), "violet", 4, spread=1.15)   # steel-indigo coat
BEAV_CAP = [(238, 190, 120, 255), (222, 146, 54, 255),      # amber knit cap —
            (156, 86, 46, 255), (92, 50, 58, 255)]          # HIS accent
BEAV_TAIL = ramp((110, 80, 104), "violet", 4)      # violet-brown paddle tail
BEAV_MUZ = [(214, 208, 212, 255), (180, 172, 180, 255),     # old grey muzzle,
            (140, 128, 146, 255), (98, 86, 108, 255)]        # HAND-PINNED
BEAV_EYE = (58, 40, 48, 255)
GREYF = (110, 98, 132, 255)                        # the age flecks
BEAV_OUTS = outs_for((BEAV_FUR, OUT_DARK), (BEAV_COAT, OUT_DARK),
                     (BEAV_CAP, OUT_DARK), (BEAV_MUZ, OUT_LIGHT),
                     (BEAV_TAIL, OUT_DARK), (WHITE, OUT_LIGHT))


def beaver(s, mood="idle", bob=0, liftL=0, liftR=0):
    """Alder, the elderly beaver woodworker: heavy-set in a quilted steel-blue
    coat, small amber knit cap, grey-flecked muzzle, the broad flat tail
    poking out at the base. act = the dead charm-stone held out at arm's
    length, peering at it (a plain cold pebble). emote = the free paw
    scratching up under the cap, tail pressed flat, weary puzzlement."""
    hy, by = 21 + bob, 34 + bob
    # -- the paddle tail at the base ------------------------------------
    if mood == "emote":                             # pressed FLAT to the snow
        s.ball(CX + 9, 42.5, 4.8, 1.8, BEAV_TAIL, power=1.8, wrap=0.10,
               curve=0.10)
    else:
        s.capsule(CX + 6, 40 + bob, CX + 12, 42, 2.6, 2.2, BEAV_TAIL, sh=0.10)
    # -- feet / the heavy quilted body ----------------------------------
    for (fx_, lift, sh) in ((CX - 3, liftL, 0.0), (CX + 3, liftR, 0.10)):
        s.ball(fx_, 43 - lift, 2.2, 1.6, BEAV_FUR, power=2.2, sh=0.30 + sh,
               wrap=0.10, curve=0.10)
    s.ball(CX, by, 8.4, 7.4, BEAV_COAT, power=2.2, wrap=0.26, curve=0.20)
    # -- arms per mood --------------------------------------------------
    if mood == "act":                               # west arm OUT, full length
        s.capsule(CX - 7, by - 3, CX - 14, by - 4, 2.0, 1.6, BEAV_COAT,
                  sh=0.06)
        s.ball(CX - 15, by - 4, 1.9, 1.6, BEAV_FUR, power=2.2, wrap=0.10,
               curve=0.10)
        s.capsule(CX + 7.5, by - 4, CX + 8.5, by + 2, 2.0, 1.7, BEAV_COAT,
                  sh=0.16)
        s.ball(CX + 8.5, by + 3, 1.7, 1.5, BEAV_FUR, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
    elif mood == "emote":                           # east paw up under the cap
        s.capsule(CX - 7.5, by - 4, CX - 8.5, by + 2, 2.0, 1.7, BEAV_COAT,
                  sh=0.06)
        s.ball(CX - 8.5, by + 3, 1.7, 1.5, BEAV_FUR, power=2.2, wrap=0.10,
               curve=0.10)
        s.capsule(CX + 7.5, by - 4, CX + 8, hy - 3, 1.9, 1.5, BEAV_COAT,
                  sh=0.16)
        s.ball(CX + 8, hy - 4, 1.7, 1.5, BEAV_FUR, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
    else:
        s.capsule(CX - 7.5, by - 4, CX - 8.5, by + 2, 2.0, 1.7, BEAV_COAT,
                  sh=0.06)
        s.capsule(CX + 7.5, by - 4, CX + 8.5, by + 2, 2.0, 1.7, BEAV_COAT,
                  sh=0.16)
        s.ball(CX - 8.5, by + 3, 1.7, 1.5, BEAV_FUR, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 8.5, by + 3, 1.7, 1.5, BEAV_FUR, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
    # -- head + the small knit cap --------------------------------------
    for (ex, sh) in ((CX - 6, 0.0), (CX + 6, 0.14)):    # small round ears
        s.ball(ex, hy - 5, 1.8, 1.7, BEAV_FUR, power=2.0, sh=sh, wrap=0.20,
               curve=0.16)
    s.ball(CX, hy, 6.6, 5.8, BEAV_FUR, power=2.4, wrap=0.32, curve=0.28)
    capdx = 1 if mood == "emote" else 0             # scratch tilts the cap
    s.ball(CX + capdx, hy - 6, 5.2, 2.6, BEAV_CAP, power=2.0, wrap=0.16,
           curve=0.10)
    s.rect(CX - 5 + capdx, hy - 5, CX + 5 + capdx, hy - 4, BEAV_CAP[2])
    for rx in range(CX - 4 + capdx, CX + 5 + capdx, 2):
        s.set(rx, hy - 4, BEAV_CAP[3])              # knit rib ticks
    # grey-flecked muzzle, big nose, the two honest teeth
    s.ball(CX, hy + 4, 5.0, 3.0, BEAV_MUZ, power=2.0, wrap=0.10, curve=0.10)
    s.rect(CX - 1, hy + 1, CX + 1, hy + 2, NOSE)
    s.rect(CX - 1, hy + 6, CX - 1, hy + 7, WHITE[0])    # the two honest
    s.rect(CX, hy + 6, CX, hy + 7, WHITE[2])            # teeth, split-shaded
    for (gx, gy) in ((CX - 4, hy + 4), (CX + 4, hy + 5), (CX - 3, hy + 6)):
        s.set(gx, gy, GREYF)                        # the age flecks
    ey = hy - 1
    if mood == "emote":                             # weary shut lids
        _closed(s, CX - 5, ey - 1, happy=False)
        _closed(s, CX + 3, ey - 1, happy=False)
    else:
        for ex in (CX - 5, CX + 3):
            s.rect(ex, ey, ex + 1, ey + 1, BEAV_EYE)
            s.set(ex + 1, ey, GLINT)
        if mood == "act":                           # peering: brows knit down
            s.line([(CX - 5, ey - 1), (CX - 4, ey - 1)], BEAV_FUR[3])
            s.line([(CX + 3, ey - 1), (CX + 4, ey - 1)], BEAV_FUR[3])
    s.despeckle(passes=1)
    s.outline(BEAV_OUTS, OUT_DARK)
    s.crease([(CX + 8, 41), (CX + 9, 41), (CX + 10, 41), (CX + 8, 43),
              (CX + 10, 43)], BEAV_TAIL[3])         # the paddle crosshatch
    s.crease([(CX - 3, by - 3), (CX - 3, by), (CX - 3, by + 3),
              (CX + 3, by - 3), (CX + 3, by), (CX + 3, by + 3),
              (CX - 6, by + 1), (CX, by + 1), (CX + 6, by + 1)],
             BEAV_COAT[3])                          # quilt seams
    whiskers_kid_down(s, bob - 5)
    if mood == "act":                               # the cold pebble, seated
        s.rect(CX - 16, by - 7, CX - 15, by - 6, STEELF[2])     # on the paw
        s.set(CX - 15, by - 6, STEELF[3])
        s.set(CX - 16, by - 7, STEELF[1])           # one cold light catch


def beaver_back(s, bob=0, liftL=0, liftR=0):
    """Alder from BEHIND (2026-07-29): the PADDLE hangs straight down between
    his heels — side-on it points east, but a beaver walking away drags it, and
    it is the only silhouette that says beaver from this angle. The coat gets
    its centre seam and the knit cap's brim runs all the way round. Old bull of
    a body: the skull is small and set low on heavy shoulders, no kid dome."""
    hy, by = 21 + bob, 34 + bob
    # the paddle DRAGGED out east past the coat's edge — hung straight down it
    # sat entirely inside the coat's silhouette and read as a smudge of dirt
    s.capsule(CX + 3, 40 + bob, CX + 11, 43, 2.4, 2.4, BEAV_TAIL, sh=-0.06)
    for (fx_, lift, sh) in ((CX - 6, liftL, 0.30), (CX + 6, liftR, 0.40)):
        s.ball(fx_, 43 - lift, 2.2, 1.6, BEAV_FUR, power=2.2, sh=sh,
               wrap=0.10, curve=0.10)
    s.ball(CX, by, 8.4, 7.4, BEAV_COAT, power=2.2, wrap=0.26, curve=0.20)
    for y in range(by - 8, by + 8):
        s.set(CX, y, BEAV_COAT[3])                  # the centre seam
    s.rect(CX - 8, by + 5, CX + 8, by + 6, BEAV_COAT[3])        # the hem band
    s.capsule(CX - 7.5, by - 4, CX - 8.5, by + 2, 2.0, 1.7, BEAV_COAT, sh=0.16)
    s.capsule(CX + 7.5, by - 4, CX + 8.5, by + 2, 2.0, 1.7, BEAV_COAT, sh=0.26)
    s.ball(CX - 8.5, by + 3, 1.7, 1.5, BEAV_FUR, power=2.2, sh=0.16, wrap=0.10,
           curve=0.10)
    s.ball(CX + 8.5, by + 3, 1.7, 1.5, BEAV_FUR, power=2.2, sh=0.26, wrap=0.10,
           curve=0.10)
    for (ex, sh) in ((CX - 6, 0.26), (CX + 6, 0.34)):
        s.ball(ex, hy - 5, 1.8, 1.7, BEAV_FUR, power=2.0, sh=sh, wrap=0.20,
               curve=0.16)                          # small round ear backs
    s.ball(CX, hy, 6.6, 5.8, BEAV_FUR, power=2.4, wrap=0.32, curve=0.28)
    s.line([(CX - 2, hy + 4), (CX - 1, hy + 5), (CX, hy + 5),
            (CX + 1, hy + 5), (CX + 2, hy + 4)], BEAV_FUR[3])   # nape
    s.ball(CX, hy - 6, 5.2, 2.6, BEAV_CAP, power=2.0, wrap=0.16, curve=0.10)
    s.rect(CX - 5, hy - 5, CX + 5, hy - 4, BEAV_CAP[2])
    for rx in range(CX - 4, CX + 5, 2):
        s.set(rx, hy - 4, BEAV_CAP[3])              # knit rib ticks
    s.despeckle(passes=1)
    s.outline(BEAV_OUTS, OUT_DARK)
    s.crease([(CX + 6, 41), (CX + 8, 41), (CX + 10, 42), (CX + 6, 43),
              (CX + 8, 43)], BEAV_TAIL[3])          # the paddle crosshatch
    s.crease([(CX - 4, by - 3), (CX - 4, by), (CX - 4, by + 3),
              (CX + 4, by - 3), (CX + 4, by), (CX + 4, by + 3)],
             BEAV_COAT[3])                          # quilt seams


def beaver_side(s, bob=0, fF=(0, 0), fB=(0, 0)):
    """Alder in PROFILE, drawn facing RIGHT and mirrored last. The paddle
    sweeps back west at full width (side-on is the only view where it reads as
    a paddle and not a lump), the grey muzzle and the two honest teeth carry
    the front, and the amber cap sits over the brow."""
    hx, hy, by = 26, 21 + bob, 34 + bob
    s.capsule(18, 40 + bob, 9, 42, 2.2, 3.4, BEAV_TAIL, sh=0.14)
    for (base_x, (dx, lift), sh) in ((19, fB, 0.44), (26, fF, 0.30)):
        lx = base_x + dx
        s.ball(lx, 43 - lift, 2.2, 1.6, BEAV_FUR, power=2.2, sh=sh, wrap=0.10,
               curve=0.10)
    s.ball(23, by, 7.6, 7.4, BEAV_COAT, power=2.2, wrap=0.26, curve=0.20)
    s.rect(16, by + 5, 30, by + 6, BEAV_COAT[3])                # the hem band
    for y in range(by - 5, by + 5):                             # the front edge
        s.set(30, y, BEAV_COAT[3])
        s.set(29, y, BEAV_COAT[2])
    s.capsule(25, by - 4, 27, by + 2, 2.0, 1.7, BEAV_COAT, sh=0.10)  # near arm
    s.ball(27, by + 3, 1.7, 1.5, BEAV_FUR, power=2.2, wrap=0.10, curve=0.10)
    s.ball(hx, hy, 6.2, 5.6, BEAV_FUR, power=2.4, wrap=0.32, curve=0.28)
    # the ear rides BELOW the cap brim and BEHIND the skull line: tucked in at
    # hy-4 the knit swallowed it whole and the profile lost its only ear
    s.ball(hx - 7, hy - 1, 1.9, 1.8, BEAV_FUR, power=2.0, sh=0.28, wrap=0.20,
           curve=0.16)
    # a SHORT blunt muzzle — run out long and pale it read as an anteater
    s.capsule(hx + 1, hy + 3, hx + 5, hy + 4, 2.7, 2.1, BEAV_MUZ, sh=0.24)
    s.rect(hx + 7, hy + 2, hx + 7, hy + 3, NOSE)
    s.line([(hx + 3, hy + 5), (hx + 4, hy + 5), (hx + 5, hy + 5)], MOUTH)
    s.rect(hx + 4, hy + 6, hx + 4, hy + 7, WHITE[0])    # the two honest teeth
    s.rect(hx + 5, hy + 6, hx + 5, hy + 7, WHITE[2])
    for (gx, gy) in ((hx + 1, hy + 5), (hx + 3, hy + 3)):
        s.set(gx, gy, GREYF)                        # the age flecks
    s.ball(hx - 1, hy - 6, 5.2, 2.6, BEAV_CAP, power=2.0, wrap=0.16, curve=0.10)
    s.rect(hx - 6, hy - 5, hx + 4, hy - 4, BEAV_CAP[2])
    for rx in range(hx - 5, hx + 4, 2):
        s.set(rx, hy - 4, BEAV_CAP[3])
    s.rect(hx + 2, hy - 1, hx + 3, hy, BEAV_EYE)
    s.set(hx + 3, hy - 1, GLINT)
    s.despeckle(passes=1)
    s.outline(BEAV_OUTS, OUT_DARK)
    s.crease([(15, 40 + bob), (12, 41 + bob), (15, 43), (12, 43)],
             BEAV_TAIL[3])                          # the paddle crosshatch
    s.crease([(20, by - 3), (20, by), (20, by + 3),
              (25, by - 3), (25, by), (25, by + 3)], BEAV_COAT[3])
    for (x, y) in ((hx + 8, hy + 1), (hx + 9, hy + 4)):
        s.set(x, y, WHISK)                          # post-outline specks
    _mirror_cell(s)


# 2026-07-29 less-kiddy pass. BOTH of Pip's fur ramps are now HAND-PINNED, and
# they have to be: derived, FOX_CREAM's darks came back (246,141,139) and
# (249,80,166) — a warm pale seed taken the short way round to violet goes
# straight through HOT MAGENTA — and FOX_FUR's came back (194,18,46)/(149,7,94),
# which is what made his dark socks and the shadow side of his brush glow
# fire-engine red at sh=0.55. That is the exact "very kiddy" failure mode
# arrived at by obeying the palette code instead of the palette doctrine.
# Both walk to violet-BROWN instead: lower L, warmth held, no candy.
FOX_FUR = [(232, 158, 106, 255), (208, 102, 40, 255),       # rust — the kit's
           (146, 58, 44, 255), (86, 34, 58, 255)]           # own warmth
FOX_CREAM = [(248, 238, 214, 255), (226, 202, 158, 255),    # muzzle / chest /
             (170, 142, 126, 255), (112, 88, 102, 255)]     # tail-tip
FOX_KNIT = ramp((72, 128, 180), "violet", 4, spread=1.1)    # frost-blue knit
FOX_EYE, FOX_EYEL = (246, 204, 116, 255), (252, 232, 168, 255)
GLASSM = (214, 232, 242, 255)                      # the marble's cold glass
GLASSM_D = (36, 28, 52, 255)                       # ...and its DEAD dark heart
FOX_OUTS = outs_for((FOX_FUR, OUT_DARK), (FOX_CREAM, OUT_LIGHT),
                    (FOX_KNIT, OUT_DARK))


def foxkid(s, mood="idle", bob=0, liftL=0, liftR=0, tail_sway=0):
    """Pip, the fox kid — child proportions (shorter, bigger head, the mouse
    kid register): rust fur, cream muzzle and tail-tip, frost-blue bobble hat
    and mittens. act = shaking the little glow-marble up in both mittens (the
    glass is DARK inside — it died). emote = wide-eyed, mouth open, tail
    bristled: thrilled AND scared at once."""
    hy, by = 27 + bob, 37 + bob
    # -- the bushy tail (the fox signature) -----------------------------
    if mood == "emote":                             # bristled: fat + spiked
        s.capsule(CX + 5, 39 + bob, CX + 10, 29 + bob, 3.2, 2.6, FOX_FUR,
                  sh=0.10)
        for (tx, ty) in ((CX + 4, 34), (CX + 9, 38), (CX + 13, 33),
                         (CX + 7, 28)):
            s.tri((tx, ty + bob - 2), ty + bob, tx - 1, tx + 1, FOX_FUR[1])
        s.ball(CX + 10, 27 + bob, 2.2, 2.0, FOX_CREAM, power=2.2, wrap=0.10,
               curve=0.10)
    else:
        s.capsule(CX + 5, 39 + bob, CX + 9 + tail_sway, 31 + bob, 2.6, 2.2,
                  FOX_FUR, sh=0.10)
        s.ball(CX + 9 + tail_sway, 29.5 + bob, 2.0, 1.8, FOX_CREAM, power=2.2,
               wrap=0.10, curve=0.10)
    # -- legs (dark socks) / small body ---------------------------------
    for (lx, lift, sh) in ((CX - 3, liftL, 0.0), (CX + 3, liftR, 0.10)):
        s.capsule(lx, 39 + bob, lx, 42 - lift, 1.8, 1.5, FOX_FUR, sh=0.15 + sh)
        s.ball(lx, 42.8 - lift, 1.9, 1.4, FOX_FUR, power=2.2, sh=0.55,
               wrap=0.10, curve=0.10)
    s.ball(CX, by, 5.2, 4.6, FOX_FUR, power=2.2, wrap=0.30, curve=0.24)
    s.ball(CX, by + 1, 3.0, 2.6, FOX_CREAM, power=2.2, wrap=0.10, curve=0.10)
    # -- arms per mood (mittens are the paws) ---------------------------
    if mood == "act":                               # both up east, shaking
        s.capsule(CX - 4.5, by - 2, CX + 4, hy - 11, 1.5, 1.3, FOX_FUR,
                  sh=0.06)
        s.capsule(CX + 4.5, by - 2, CX + 7, hy - 11, 1.5, 1.3, FOX_FUR,
                  sh=0.16)
        s.ball(CX + 4, hy - 12, 1.7, 1.5, FOX_KNIT, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 7.5, hy - 12, 1.7, 1.5, FOX_KNIT, power=2.2, sh=0.12,
               wrap=0.10, curve=0.10)
    elif mood == "emote":                           # flung a little out
        s.capsule(CX - 4.5, by - 3, CX - 7, by - 7, 1.5, 1.3, FOX_FUR,
                  sh=0.06)
        s.capsule(CX + 4.5, by - 3, CX + 7, by - 7, 1.5, 1.3, FOX_FUR,
                  sh=0.16)
        s.ball(CX - 7.5, by - 8, 1.7, 1.5, FOX_KNIT, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 7.5, by - 8, 1.7, 1.5, FOX_KNIT, power=2.2, sh=0.12,
               wrap=0.10, curve=0.10)
    else:
        s.capsule(CX - 4.5, by - 3, CX - 5.5, by, 1.5, 1.3, FOX_FUR, sh=0.06)
        s.capsule(CX + 4.5, by - 3, CX + 5.5, by, 1.5, 1.3, FOX_FUR, sh=0.16)
        s.ball(CX - 5.5, by + 1.5, 1.6, 1.4, FOX_KNIT, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 5.5, by + 1.5, 1.6, 1.4, FOX_KNIT, power=2.2, sh=0.12,
               wrap=0.10, curve=0.10)
    # -- the big kid head + pointed ears + the bobble hat ---------------
    s.tri((CX - 6, hy - 12), hy - 4, CX - 9, CX - 3, FOX_FUR)
    s.tri((CX + 6, hy - 12), hy - 4, CX + 3, CX + 9, FOX_FUR, sh=0.14)
    s.rect(CX - 7, hy - 11, CX - 6, hy - 10, FOX_FUR[3])    # dark ear tips
    s.rect(CX + 6, hy - 11, CX + 7, hy - 10, FOX_FUR[3])
    s.ball(CX, hy, 6.2, 5.4, FOX_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.ball(CX - 4.5, hy + 3, 2.2, 1.8, FOX_CREAM, power=2.0, wrap=0.10,
           curve=0.10)                              # cheek ruffs
    s.ball(CX + 4.5, hy + 3, 2.2, 1.8, FOX_CREAM, power=2.0, sh=0.08,
           wrap=0.10, curve=0.10)
    s.ball(CX, hy + 3.6, 3.6, 2.4, FOX_CREAM, power=2.2, wrap=0.10,
           curve=0.10)
    s.rect(CX - 1, hy + 2, CX, hy + 2, NOSE)
    s.ball(CX, hy - 6, 5.6, 3.0, FOX_KNIT, power=2.0, wrap=0.16, curve=0.10)
    s.rect(CX - 5, hy - 4, CX + 5, hy - 3, FOX_KNIT[2])
    for rx in range(CX - 4, CX + 5, 2):
        s.set(rx, hy - 3, FOX_KNIT[3])              # rib ticks
    s.ball(CX, hy - 10, 1.9, 1.7, FOX_CREAM, power=2.2, wrap=0.10,
           curve=0.10)                              # the bobble
    ey = hy - 2
    if mood == "emote":                             # wide-eyed pinpricks
        for ex in (CX - 5, CX + 3):
            s.rect(ex, ey, ex + 2, ey + 2, FOX_EYE)
            s.rect(ex, ey, ex + 2, ey, FOX_EYEL)
            s.set(ex + 1, ey + 2, PUPIL)
            s.set(ex + 2, ey, GLINT)
        s.rect(CX - 2, hy + 4, CX + 1, hy + 5, MAW)
    else:
        _eye(s, CX - 5, ey, FOX_EYE, FOX_EYEL)
        _eye(s, CX + 3, ey, FOX_EYE, FOX_EYEL)
        if mood == "act":                           # rattling it — teeth grit
            s.rect(CX - 1, hy + 4, CX, hy + 5, MAW)
        else:
            s.line([(CX - 1, hy + 4), (CX, hy + 4)], MOUTH)
    s.despeckle(passes=1)
    s.outline(FOX_OUTS, OUT_DARK)
    if mood == "act":                               # the marble, post-outline:
        mx, my = CX + 6, hy - 16                    # cold glass, DARK heart
        for (px_, py_) in ((mx - 1, my), (mx + 1, my), (mx, my - 1),
                           (mx, my + 1)):
            s.set(px_, py_, GLASSM)
        s.set(mx, my, GLASSM_D)
        s.set(mx - 3, my - 2, GLASSM)               # shake ticks
        s.set(mx + 3, my - 2, GLASSM)
    elif mood == "emote":
        for (px_, py_) in ((CX - 9, hy - 9), (CX, hy - 14),
                           (CX + 9, hy - 9)):
            s.set(px_, py_, SPARK_D)                # thrilled-scared ticks


def foxkid_back(s, bob=0, liftL=0, liftR=0, tail_sway=0):
    """Pip from behind (2026-07-29): the bobble hat and the big cream-tipped
    TAIL are the whole silhouette, so the tail is drawn OVER his back — from
    behind it is the nearest thing to camera — sweeping up west with the cream
    tip clear of the shoulder line. Ear backs keep their dark tips; the hat's
    knit brim runs all the way round."""
    hy, by = 27 + bob, 37 + bob
    # -- legs (dark socks) / small body ---------------------------------
    for (lx, lift, sh) in ((CX - 3, liftL, 0.0), (CX + 3, liftR, 0.10)):
        s.capsule(lx, 39 + bob, lx, 42 - lift, 1.8, 1.5, FOX_FUR, sh=0.15 + sh)
        s.ball(lx, 42.8 - lift, 1.9, 1.4, FOX_FUR, power=2.2, sh=0.55,
               wrap=0.10, curve=0.10)
    s.ball(CX, by, 5.2, 4.6, FOX_FUR, power=2.2, wrap=0.30, curve=0.24)
    s.capsule(CX - 4.5, by - 3, CX - 5.5, by, 1.5, 1.3, FOX_FUR, sh=0.06)
    s.capsule(CX + 4.5, by - 3, CX + 5.5, by, 1.5, 1.3, FOX_FUR, sh=0.16)
    s.ball(CX - 5.5, by + 1.5, 1.6, 1.4, FOX_KNIT, power=2.2, wrap=0.10,
           curve=0.10)                              # mittens
    s.ball(CX + 5.5, by + 1.5, 1.6, 1.4, FOX_KNIT, power=2.2, sh=0.12,
           wrap=0.10, curve=0.10)
    # -- ear backs (dark tips, no inner) + the head ---------------------
    s.tri((CX - 6, hy - 12), hy - 4, CX - 9, CX - 3, FOX_FUR, sh=0.26)
    s.tri((CX + 6, hy - 12), hy - 4, CX + 3, CX + 9, FOX_FUR, sh=0.34)
    s.rect(CX - 7, hy - 11, CX - 6, hy - 10, FOX_FUR[3])
    s.rect(CX + 6, hy - 11, CX + 7, hy - 10, FOX_FUR[3])
    s.ball(CX, hy, 6.2, 5.4, FOX_FUR, power=2.4, wrap=0.34, curve=0.30)
    s.line([(CX - 2, hy + 4), (CX - 1, hy + 5), (CX, hy + 5),
            (CX + 1, hy + 5), (CX + 2, hy + 4)], FOX_FUR[3])    # nape part
    # -- the hat, brim all the way round --------------------------------
    s.ball(CX, hy - 6, 5.6, 3.0, FOX_KNIT, power=2.0, wrap=0.16, curve=0.10)
    s.rect(CX - 5, hy - 4, CX + 5, hy - 3, FOX_KNIT[2])
    for rx in range(CX - 4, CX + 5, 2):
        s.set(rx, hy - 3, FOX_KNIT[3])              # rib ticks
    s.ball(CX, hy - 10, 1.9, 1.7, FOX_CREAM, power=2.2, wrap=0.10,
           curve=0.10)                              # the bobble
    # -- THE TAIL, up the west flank, cream tip clear of the shoulder ----
    # (drawn over the body, since from behind the brush is the nearest thing to
    # camera — but only across the FLANK: a tail swept over the whole back left
    # him a red mass with a hat on it, no nape, no mittens, no read)
    s.capsule(CX - 3, 40 + bob, CX - 9 - tail_sway, 31 + bob, 2.7, 2.2,
              FOX_FUR, sh=0.10)
    s.ball(CX - 10 - tail_sway, 29 + bob, 2.2, 2.0, FOX_CREAM, power=2.2,
           wrap=0.10, curve=0.10)
    s.despeckle(passes=1)
    s.outline(FOX_OUTS, OUT_DARK)
    s.crease([(CX - 5, 37 + bob), (CX - 6, 35 + bob), (CX - 7, 33 + bob)],
             FOX_FUR[3])                            # fur ticks along the brush


def foxkid_side(s, bob=0, fF=(0, 0), fB=(0, 0), tail_sway=0):
    """Pip in profile, facing RIGHT before the mirror: the pointed fox muzzle
    out front under the bobble hat's brim, the brush swept back west with its
    cream tip, one mitten hanging."""
    hy, by = 27 + bob, 37 + bob
    # -- the brush swept back behind him. It has to TAPER hard: at an even
    # radius it read as a stick with a ball on the end, not a brush ------
    s.capsule(20, 40 + bob, 11 - tail_sway, 34 + bob, 3.4, 2.0, FOX_FUR,
              sh=0.10)
    s.ball(9.5 - tail_sway, 32.5 + bob, 2.1, 1.9, FOX_CREAM, power=2.2,
           wrap=0.10, curve=0.10)
    # -- legs / body ----------------------------------------------------
    for (base_x, (dx, lift), sh) in ((20, fB, 0.14), (26, fF, 0.0)):
        lx = base_x + dx
        s.capsule(lx, 39 + bob, lx, 42 - lift, 1.8, 1.5, FOX_FUR, sh=0.15 + sh)
        s.ball(lx + 0.5, 42.8 - lift, 1.9, 1.4, FOX_FUR, power=2.2, sh=0.55,
               wrap=0.10, curve=0.10)
    s.ball(23, by, 5.0, 4.6, FOX_FUR, power=2.2, wrap=0.30, curve=0.24)
    s.ball(25.5, by + 1, 2.4, 2.4, FOX_CREAM, power=2.2, wrap=0.10, curve=0.10)
    s.capsule(24, by - 3, 25.5, by, 1.5, 1.3, FOX_FUR, sh=0.10)   # near arm
    s.ball(25.5, by + 1.5, 1.6, 1.4, FOX_KNIT, power=2.2, wrap=0.10,
           curve=0.10)                              # the mitten
    # -- head: far ear peeking, near ear tall ---------------------------
    s.tri((26, hy - 11), hy - 4, 24, 29, FOX_FUR, sh=0.28)
    s.rect(27, hy - 10, 28, hy - 9, FOX_FUR[3])
    s.tri((21, hy - 12), hy - 4, 18, 23, FOX_FUR)
    s.rect(19, hy - 11, 20, hy - 10, FOX_FUR[3])
    s.ball(22, hy, 6.0, 5.2, FOX_FUR, power=2.4, wrap=0.34, curve=0.30)
    # the pointed muzzle: a taper out east, cream underside
    s.capsule(25, hy + 2, 30, hy + 3, 2.6, 1.5, FOX_FUR, sh=0.04)
    s.capsule(25, hy + 3.4, 29.5, hy + 3.8, 1.9, 1.1, FOX_CREAM, sh=-0.10)
    s.rect(30, hy + 2, 31, hy + 2, NOSE)
    s.ball(19.5, hy + 3, 2.2, 1.8, FOX_CREAM, power=2.0, wrap=0.10,
           curve=0.10)                              # the cheek ruff
    # -- the hat + bobble, brim riding the brow -------------------------
    s.ball(22, hy - 6, 5.4, 3.0, FOX_KNIT, power=2.0, wrap=0.16, curve=0.10)
    s.rect(17, hy - 4, 27, hy - 3, FOX_KNIT[2])
    for rx in range(18, 27, 2):
        s.set(rx, hy - 3, FOX_KNIT[3])
    s.ball(21, hy - 10, 1.9, 1.7, FOX_CREAM, power=2.2, wrap=0.10, curve=0.10)
    _eye(s, 24, hy - 2, FOX_EYE, FOX_EYEL)
    s.line([(28, hy + 4), (29, hy + 4)], MOUTH)
    s.despeckle(passes=1)
    s.outline(FOX_OUTS, OUT_DARK)
    s.crease([(17, 38 + bob), (15, 37 + bob), (13, 35 + bob)], FOX_FUR[3])
    for (x, y) in ((32, hy - 1), (33, hy), (32, hy + 5)):
        s.set(x, y, WHISK)                          # profile whiskers
    _mirror_cell(s)


# ---- MAYOR HOLLIS of Lanternwood (2026-07-29) ----------------------------------------------
# The town's mayor AND its clerk — an old elk, the biggest animal in Lanternwood,
# and the only one who answers the Ebb with paperwork. The design is three
# things and nothing else: the ANTLERS (broad, asymmetric, one tine snapped
# blunt), the CHAIN OF OFFICE (brass links to a flat pendant — it says mayor
# faster than any pose), and the half-moon SPECTACLES on their cord. Played
# completely straight: dignity, not whimsy. Cool browns under a heavy winter
# coat, one warm accent (the brass) per the Lanternwood cast law.

# 2026-07-29 less-kiddy pass: hide, coat and waistcoat all sat at S≈0.12-0.22 —
# naturalistic mud, the exact thing the palette doctrine bans as a field — so
# each drops L and commits to its hue with the spread up. ELK_MUZ and ELK_RUMP
# join ANTLER and LEDGER as HAND-PINNED, for the same reason those two already
# were: a pale warm seed's derived darks came back (214,139,136) and
# (208,86,146) — a PINK tuft on the back of a mayor — and dropping the muzzle's
# L far enough to lose the mud put the hue pull somewhere worse still, a
# saturated purple bruise across the face of the only adult in the scene who is
# supposed to read as dignity. Both walk cool-violet-GREY by hand instead.
ELK_FUR = ramp((140, 100, 82), "violet", 4, spread=1.1)     # cool elk hide
ELK_MUZ = [(208, 202, 202, 255), (176, 168, 172, 255),      # old bull's muzzle
           (138, 126, 138, 255), (96, 84, 100, 255)]         # (see below)
ELK_COAT = ramp((102, 70, 80), "violet", 4)        # thick cool-brown winter coat
ELK_VEST = ramp((70, 114, 88), "violet", 4, spread=1.15)    # pine-green waistcoat
ELK_RUMP = [(236, 228, 204, 255), (210, 196, 164, 255),     # the pale cervid
            (158, 144, 140, 255), (106, 94, 110, 255)]      # rump tuft
HOOF = ramp((92, 80, 100), "violet", 4)            # dark keratin
# BONE and PAPER are HAND-PINNED: ramp() takes a pale warm seed's darks the
# short way round the wheel toward violet, i.e. straight through RED (the same
# law that makes BRASS[2..3] unusable), and rust-red antlers on a rust-brown
# elk lose the whole silhouette. These go cool-violet instead, the honest way.
ANTLER = [(232, 218, 190, 255), (198, 178, 150, 255),
          (150, 130, 134, 255), (102, 86, 104, 255)]
LEDGER = [(240, 232, 210, 255), (220, 210, 190, 255),
          (166, 158, 166, 255), (114, 106, 126, 255)]
ELK_EYE = (48, 38, 52, 255)
ELK_NOSE = (74, 62, 82, 255)
CORD = (58, 50, 70, 255)                           # the spectacle cord
INK = (58, 48, 112, 255)                           # iron-gall ink, on the hoof
MAYOR_OUTS = outs_for((ELK_FUR, OUT_DARK), (ELK_COAT, OUT_DARK),
                      (ELK_MUZ, OUT_DARK), (ELK_VEST, OUT_DARK),
                      (ELK_RUMP, OUT_LIGHT), (ANTLER, OUT_DARK),
                      (HOOF, OUT_DARK), (LEDGER, OUT_DARK),
                      (BRASSF, OUT_DARK))


def _antler_rack(s, bx, by, d, broken=False):
    """One half-rack sweeping up and OUT from (bx, by). `d` = -1 west / +1 east.
    Beam plus a low brow tine and two risers — the candelabra read, which is
    the only antler that survives 48px. `broken` snaps the middle riser short
    and caps it with a pale break scar (the same tine every time, so the rack
    is reliably asymmetric).

    The rack is BROAD rather than tall on purpose — wapiti sweep back, and 10
    rows above the base is the ceiling: any taller and the fill reaches y=0 on
    a bob=-1 frame, where the outline pass has nowhere to put its edge. The
    callers pin `by` to an ABSOLUTE row for the same reason, so a chin-up or
    head-bowed pose moves the skull without dragging the rack off the cell."""
    # The beam sweeps OUT along a shallow diagonal and the tines rise VERTICALLY
    # off it, well apart — a riser running parallel to the beam merges with it
    # into one pale slab and the rack stops reading as tines at all.
    s.capsule(bx, by, bx + 10 * d, by - 5, 1.9, 1.2, ANTLER,
              sh=0.0 if d < 0 else 0.16)
    s.capsule(bx + d, by - 1, bx + 5 * d, by + 1, 1.4, 0.9, ANTLER,
              sh=0.10 if d < 0 else 0.24)                       # brow tine
    if broken:
        s.capsule(bx + 4 * d, by - 3, bx + 4 * d, by - 6, 1.3, 1.3, ANTLER,
                  sh=0.26)
        s.rect(bx + 4 * d - 1, by - 7, bx + 4 * d + 1, by - 7, ANTLER[3])
    else:
        s.capsule(bx + 4 * d, by - 3, bx + 4 * d, by - 9, 1.3, 0.9, ANTLER,
                  sh=0.06 if d < 0 else 0.22)
    s.capsule(bx + 10 * d, by - 5, bx + 10 * d, by - 10, 1.2, 0.9, ANTLER,
              sh=0.12 if d < 0 else 0.28)                       # the outer tine


def _mayor_chain(s, cy):
    """The chain of office: brass links down both shoulders to a flat pendant
    centred at (CX, cy). Alternating tones read as links at 1px; BRASSF[2..3]
    are unusable (the violet law turns brass darks to iron), so the shading is
    tones 0/1 only with a steel engraving on the plate."""
    for d in (-1, 1):
        for i, (lx, ly) in enumerate(((6, -8), (6, -7), (5, -6), (5, -5),
                                      (4, -4), (3, -3), (2, -2))):
            s.set(CX + lx * d, cy + ly, BRASSF[i % 2])
    s.rect(CX - 2, cy - 1, CX + 2, cy + 2, BRASSF[1])       # the pendant plate
    s.rect(CX - 2, cy - 1, CX + 2, cy - 1, BRASSF[0])
    s.set(CX, cy, STEELF[3])                                # engraved mark
    s.set(CX - 1, cy + 1, STEELF[3])
    s.set(CX + 1, cy + 1, STEELF[3])


def _mayor_specs(s, hy):
    """Half-moon spectacles low on the long muzzle — a straight top edge with a
    shallow arc under it, twice, bridged at the centre — and the cord looping
    back past the cheeks. Reuses the stork's RIMLESS glass."""
    s.rect(CX - 6, hy + 1, CX - 3, hy + 1, RIMLESS)         # straight top edges
    s.rect(CX + 2, hy + 1, CX + 5, hy + 1, RIMLESS)
    s.rect(CX - 1, hy + 1, CX, hy + 1, RIMLESS)             # the bridge
    for (lx, ly) in ((-6, 2), (-5, 3), (-4, 3), (-3, 2),
                     (2, 2), (3, 3), (4, 3), (5, 2)):       # the half-moon arcs
        s.set(CX + lx, hy + ly, RIMLESS)
    for (lx, ly) in ((-7, 1), (-8, 2), (-8, 4), (7, 1), (8, 2), (8, 4)):
        s.set(CX + lx, hy + ly, CORD)                       # the cord


def mayor(s, mood="idle", bob=0, liftL=0, liftR=0):
    """MAYOR HOLLIS, down view. mood: idle (hooves down, the ink-stained one
    east), act = WRITING (the ledger up in the off hoof, pencil at it, head
    bowed), emote = the civic gesture (one hoof raised as if calling a motion,
    chin up, eyes shut)."""
    write = mood == "act"
    call = mood == "emote"
    hy = 18 + bob + (2 if write else 0) - (2 if call else 0)
    by = 33 + bob
    ay = 14 + bob                                   # the rack's ABSOLUTE base row
    # -- the rack, drawn first so the skull sits over its bases ---------
    _antler_rack(s, CX - 4, ay, -1)
    _antler_rack(s, CX + 4, ay, 1, broken=True)
    # -- big leaf ears out to the sides --------------------------------
    s.capsule(CX - 6, hy - 2, CX - 11, hy, 2.3, 1.6, ELK_FUR, sh=0.06)
    s.capsule(CX + 6, hy - 2, CX + 11, hy, 2.3, 1.6, ELK_FUR, sh=0.22)
    # -- hooves under the coat hem ------------------------------------
    for (lx, lift) in ((CX - 4, liftL), (CX + 4, liftR)):
        s.ball(lx, 43 - lift, 2.3, 1.7, HOOF, power=2.2, wrap=0.10, curve=0.10)
    # -- the heavy coat -----------------------------------------------
    s.ball(CX, by, 9.0, 8.0, ELK_COAT, power=2.2, wrap=0.26, curve=0.20)
    for y in range(by - 9, by + 3):                 # the waistcoat, coat open
        for x in range(CX - 4, CX + 5):
            s.set(x, y, ELK_VEST[0] if x < CX else ELK_VEST[1])
    ln(s, CX - 7, by - 9, CX - 5, by + 2, ELK_COAT[3])      # lapels
    ln(s, CX + 7, by - 9, CX + 5, by + 2, ELK_COAT[3])
    s.rect(CX - 8, by + 6, CX + 8, by + 7, ELK_COAT[3])     # the hem band
    # -- forelegs per mood --------------------------------------------
    if write:
        # the ledger held against the chest in the off hoof, the pencil hoof
        # brought across to the page, the head bowed to the line
        s.capsule(CX - 8, by - 4, CX - 12, by - 1, 2.1, 1.7, ELK_COAT, sh=0.06)
        s.capsule(CX + 8, by - 5, CX + 2, by - 2, 2.1, 1.6, ELK_COAT, sh=0.16)
        s.rect(CX - 16, by - 8, CX - 5, by + 2, LEDGER[1])          # the page
        s.rect(CX - 16, by - 8, CX - 5, by - 8, LEDGER[0])
        s.rect(CX - 17, by - 8, CX - 16, by + 2, HOOF[1])           # board spine
        for ly in range(by - 6, by + 2, 2):
            s.rect(CX - 15, ly, CX - 8, ly, LEDGER[2])              # ruled lines
        s.ball(CX - 12, by - 1, 2.0, 1.7, ELK_FUR, power=2.2, wrap=0.10,
               curve=0.10)                          # the gripping hoof, OVER it
        s.ball(CX + 1, by - 2, 2.0, 1.7, ELK_FUR, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)               # the writing hoof
        s.set(CX, by - 2, INK)
        s.set(CX + 1, by - 1, INK)
    elif call:
        s.capsule(CX - 8, by - 5, CX - 9.5, by + 3, 2.1, 1.7, ELK_COAT, sh=0.06)
        s.ball(CX - 9.5, by + 4.5, 2.0, 1.7, ELK_FUR, power=2.2, wrap=0.10,
               curve=0.10)
        # the hoof thrown up and OUT east — the rack owns everything above the
        # shoulders, so the gesture travels sideways to clear it, and it stops
        # BELOW the ear line or it just reads as a third antler
        s.capsule(CX + 7, by - 5, CX + 13, by - 10, 2.1, 1.5, ELK_COAT, sh=0.16)
        s.ball(CX + 14.5, by - 12, 2.1, 1.8, ELK_FUR, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)               # the raised hoof
        s.set(CX + 14, by - 12, INK)
        s.set(CX + 15, by - 11, INK)
    else:
        s.capsule(CX - 8, by - 5, CX - 9.5, by + 3, 2.1, 1.7, ELK_COAT, sh=0.06)
        s.capsule(CX + 8, by - 5, CX + 9.5, by + 3, 2.1, 1.7, ELK_COAT, sh=0.16)
        s.ball(CX - 9.5, by + 4.5, 2.0, 1.7, ELK_FUR, power=2.2, wrap=0.10,
               curve=0.10)
        s.ball(CX + 9.5, by + 4.5, 2.0, 1.7, ELK_FUR, power=2.2, sh=0.10,
               wrap=0.10, curve=0.10)
        s.set(CX + 9, by + 4, INK)                  # the ink-stained hoof
        s.set(CX + 10, by + 5, INK)
    # -- the long grey-muzzled head -----------------------------------
    s.ball(CX, hy, 6.0, 5.6, ELK_FUR, power=2.4, wrap=0.32, curve=0.28)
    s.ball(CX, hy + 5.5, 4.2, 3.6, ELK_MUZ, power=2.2, sh=0.10, wrap=0.12,
           curve=0.10)
    s.rect(CX - 2, hy + 7, CX + 1, hy + 8, ELK_NOSE)
    for (gx, gy) in ((CX - 5, hy + 3), (CX + 4, hy + 4), (CX + 5, hy + 2)):
        s.set(gx, gy, ELK_MUZ[0])                   # grey creeping up the cheeks
    ey = hy - 3
    if call:                                        # eyes shut, mouth calling
        _closed(s, CX - 7, ey, happy=False)
        _closed(s, CX + 4, ey, happy=False)
        s.rect(CX - 1, hy + 9, CX + 1, hy + 10, MAW)
    elif write:                                     # downcast, reading his line
        s.rect(CX - 7, ey + 2, CX - 5, ey + 2, ELK_EYE)
        s.rect(CX + 5, ey + 2, CX + 7, ey + 2, ELK_EYE)
        s.rect(CX - 7, ey + 1, CX - 5, ey + 1, ELK_FUR[3])
        s.rect(CX + 5, ey + 1, CX + 7, ey + 1, ELK_FUR[3])
        s.line([(CX - 1, hy + 9), (CX, hy + 9)], MOUTH)
    else:
        for ex in (CX - 7, CX + 5):
            s.rect(ex, ey, ex + 2, ey + 2, ELK_EYE)
            s.set(ex + 2, ey, GLINT)
        s.line([(CX - 1, hy + 9), (CX, hy + 9)], MOUTH)
    if not write:                                   # heavy old-bull brows (ONE
        s.rect(CX - 8, ey - 1, CX - 5, ey - 1, ELK_FUR[3])      # row — two read
        s.rect(CX + 5, ey - 1, CX + 8, ey - 1, ELK_FUR[3])      # as a mask)
    _mayor_specs(s, hy)
    _mayor_chain(s, by - 1)
    s.despeckle(passes=1)
    s.outline(MAYOR_OUTS, OUT_DARK)
    s.crease([(CX - 6, by - 3), (CX - 6, by), (CX - 6, by + 3),
              (CX + 6, by - 3), (CX + 6, by), (CX + 6, by + 3)],
             ELK_COAT[3])                           # coat folds
    if write:                                       # the pencil, post-outline
        for i, (px_, py_) in enumerate(((CX - 1, by - 2), (CX - 2, by - 2),
                                        (CX - 3, by - 1), (CX - 4, by - 1),
                                        (CX - 5, by))):
            s.set(px_, py_, WOODF[1] if i % 2 else WOODF[2])
        s.set(CX - 6, by, OUT_DARK)                 # the graphite point


def mayor_back(s, bob=0, liftL=0, liftR=0):
    """From behind — the angle an antler rack is most legible, with nothing in
    front of it. The asymmetry mirrors (the snapped tine falls WEST here), the
    coat shows its centre seam and standing collar, the chain's back runs
    across the nape, and the pale cervid rump tuft pokes out of the vent."""
    hy, by = 18 + bob, 33 + bob
    _antler_rack(s, CX - 4, 14 + bob, -1, broken=True)
    _antler_rack(s, CX + 4, 14 + bob, 1)
    s.capsule(CX - 6, hy - 2, CX - 11, hy, 2.3, 1.6, ELK_FUR, sh=0.24)
    s.capsule(CX + 6, hy - 2, CX + 11, hy, 2.3, 1.6, ELK_FUR, sh=0.32)
    for (lx, lift) in ((CX - 4, liftL), (CX + 4, liftR)):
        s.ball(lx, 43 - lift, 2.3, 1.7, HOOF, power=2.2, wrap=0.10, curve=0.10)
    s.ball(CX, by, 9.0, 8.0, ELK_COAT, power=2.2, wrap=0.26, curve=0.20)
    for y in range(by - 8, by + 8):                 # the centre seam
        s.set(CX, y, ELK_COAT[3])
    s.rect(CX - 8, by + 6, CX + 8, by + 7, ELK_COAT[3])         # the hem band
    s.ball(CX, by - 9, 6.0, 2.0, ELK_COAT, power=2.0, wrap=0.16,
           curve=0.10)                              # the standing collar
    s.rect(CX - 6, by - 8, CX + 6, by - 8, ELK_COAT[3])
    s.capsule(CX - 8, by - 5, CX - 9.5, by + 3, 2.1, 1.7, ELK_COAT, sh=0.06)
    s.capsule(CX + 8, by - 5, CX + 9.5, by + 3, 2.1, 1.7, ELK_COAT, sh=0.16)
    s.ball(CX - 9.5, by + 4.5, 2.0, 1.7, ELK_FUR, power=2.2, wrap=0.10,
           curve=0.10)
    s.ball(CX + 9.5, by + 4.5, 2.0, 1.7, ELK_FUR, power=2.2, sh=0.10,
           wrap=0.10, curve=0.10)
    # the pale cervid rump tuft, sitting ON the coat over the vent slit
    s.rect(CX - 1, by + 3, CX + 1, by + 8, ELK_COAT[3])         # the vent
    s.ball(CX, by + 5, 2.5, 2.1, ELK_RUMP, power=2.0, wrap=0.14, curve=0.10)
    # the skull from behind, then the chain across the nape
    s.ball(CX, hy, 6.0, 5.6, ELK_FUR, power=2.4, wrap=0.32, curve=0.28)
    s.line([(CX - 2, hy + 5), (CX - 1, hy + 6), (CX, hy + 6),
            (CX + 1, hy + 6), (CX + 2, hy + 5)], ELK_FUR[3])    # nape part
    for i, lx in enumerate(range(CX - 5, CX + 6)):
        s.set(lx, by - 9, BRASSF[i % 2])
    s.set(CX - 7, hy + 3, CORD)                     # the spectacle cord, behind
    s.set(CX + 7, hy + 3, CORD)
    s.despeckle(passes=1)
    s.outline(MAYOR_OUTS, OUT_DARK)
    s.crease([(CX - 6, by - 3), (CX - 6, by), (CX - 6, by + 3),
              (CX + 6, by - 3), (CX + 6, by), (CX + 6, by + 3)],
             ELK_COAT[3])                           # coat folds


def mayor_side(s, bob=0, fF=(0, 0), fB=(0, 0)):
    """Profile, facing RIGHT before the mirror. The near rack sweeps back over
    the shoulders with the far rack shaded behind it, the long muzzle carries
    the half-moon specs, and the CHAIN survives the profile: links over the
    near shoulder to the pendant hanging clear on the chest's front edge."""
    hy, by = 21 + bob, 33 + bob
    hx = 26                                         # the head rides forward
    ay = 16 + bob                                   # the rack's absolute base row
    # -- the far rack, shaded right down, behind everything -------------
    s.capsule(hx - 4, ay + 1, hx - 13, ay - 3, 1.8, 1.1, ANTLER, sh=0.44)
    s.capsule(hx - 11, ay - 2, hx - 11, ay - 8, 1.2, 0.9, ANTLER, sh=0.48)
    # -- hooves, the coat, the near foreleg ----------------------------
    for (base_x, (dx, lift)) in ((21, fB), (27, fF)):
        s.ball(base_x + dx, 43 - lift, 2.3, 1.7, HOOF, power=2.2, wrap=0.10,
               curve=0.10)
    s.ball(23, by, 8.0, 8.0, ELK_COAT, power=2.2, wrap=0.26, curve=0.20)
    s.rect(16, by + 6, 30, by + 7, ELK_COAT[3])                 # the hem band
    for y in range(by - 6, by + 6):                             # the front edge
        s.set(30, y, ELK_COAT[3])
        s.set(29, y, ELK_COAT[2])
    s.ball(23, by - 8, 5.4, 2.0, ELK_COAT, power=2.0, wrap=0.16,
           curve=0.10)                              # the standing collar
    s.capsule(26, by - 4, 28, by + 3, 2.1, 1.7, ELK_COAT, sh=0.10)   # near leg
    s.ball(28, by + 4.5, 2.0, 1.7, ELK_FUR, power=2.2, wrap=0.10, curve=0.10)
    s.set(28, by + 4, INK)                          # the ink-stained hoof
    s.set(29, by + 5, INK)
    # -- the chain: over the near shoulder to the pendant on the chest --
    for i, (lx, ly) in enumerate(((21, -8), (23, -8), (25, -7), (26, -6),
                                  (27, -5), (28, -4), (29, -3))):
        s.set(lx, by + ly, BRASSF[i % 2])
    s.rect(27, by - 2, 30, by + 1, BRASSF[1])                   # the pendant
    s.rect(27, by - 2, 30, by - 2, BRASSF[0])
    s.set(28, by - 1, STEELF[3])
    s.set(29, by, STEELF[3])
    # -- the ear, swept back far enough to break the skull's silhouette
    # (tucked against the head it vanished into the fur entirely) -------
    s.capsule(hx - 3, hy, hx - 10, hy + 3, 2.2, 1.5, ELK_FUR, sh=0.30)
    s.ball(hx, hy, 5.8, 5.4, ELK_FUR, power=2.4, wrap=0.32, curve=0.28)
    s.capsule(hx + 2, hy + 3, hx + 8, hy + 4, 2.7, 2.1, ELK_MUZ, sh=0.20)
    s.rect(hx + 10, hy + 3, hx + 10, hy + 5, ELK_NOSE)
    s.set(hx + 9, hy + 6, ELK_MUZ[3])
    s.line([(hx + 6, hy + 6), (hx + 7, hy + 6)], MOUTH)
    # -- the near rack, full, sweeping BACK over the shoulders, tines up
    s.capsule(hx - 2, ay, hx - 12, ay - 5, 1.9, 1.2, ANTLER, sh=0.04)
    s.capsule(hx - 1, ay - 1, hx + 4, ay - 2, 1.4, 0.9, ANTLER, sh=0.14)
    s.capsule(hx - 7, ay - 3, hx - 7, ay - 10, 1.3, 0.9, ANTLER, sh=0.10)
    s.capsule(hx - 12, ay - 5, hx - 12, ay - 11, 1.2, 0.9, ANTLER, sh=0.18)
    # -- eye, brow, the half-moon low on the muzzle, the cord back -----
    s.rect(hx + 1, hy - 3, hx + 3, hy - 1, ELK_EYE)
    s.set(hx + 3, hy - 3, GLINT)
    s.rect(hx, hy - 5, hx + 4, hy - 5, ELK_FUR[3])
    s.rect(hx + 2, hy + 1, hx + 8, hy + 1, RIMLESS)             # half-moon lens
    for (lx, ly) in ((8, 2), (7, 3), (5, 3), (3, 3), (2, 2)):
        s.set(hx + lx, hy + ly, RIMLESS)
    for (lx, ly) in ((0, 0), (-2, 0), (-4, 1), (-6, 3)):
        s.set(hx + lx, hy + ly, CORD)
    s.despeckle(passes=1)
    s.outline(MAYOR_OUTS, OUT_DARK)
    s.crease([(19, by - 3), (19, by), (19, by + 3)], ELK_COAT[3])
    _mirror_cell(s)


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


# ---- the accident set-piece (Prologue B, 2026-07-15): side-view sheets -----------------
# One scene's worth of profile art for scene/accident.tscn: Kitty pedaling in
# on her bike (brace is the last frame before the cut to black), Schweinler's
# ATV-like machine, and the fallen bike + still Kitty for the aftermath.
# Flat bands, dusk-legible silhouettes; wheels sit on the feet baseline y=44.

WHEELR = ramp((74, 70, 98), "violet", 4)           # rubber, violet-shadowed
FRAMEB = ramp((196, 148, 84), "violet", 4)         # the bike's brass frame
ATVBODY = ramp((196, 116, 78), "violet", 4)        # riveted copper cowling
ATVIRON = ramp((96, 82, 108), "violet", 4)         # undercarriage iron


def _wheel(s, cx, cy, r, hub=True):
    s.ball(cx, cy, r, r, WHEELR, power=2.2, wrap=0.10, curve=0.10)
    s.ball(cx, cy, r - 2.4, r - 2.4, ATVIRON, power=2.0, wrap=0.05, curve=0.05)
    if hub:
        s.set(int(cx), int(cy), STEELF[0])


def kitty_bike(s, pose="pedal0"):
    """Kitty riding RIGHT on her brass-framed bicycle — CT-chunk chibi
    proportions to match her top-down sprite (head nearly half the figure,
    big lit eye, white muzzle, teal bandana). pedal0/pedal1 swap the crank;
    brace is the wide-eyed stiff-armed last frame before the cut."""
    brace = pose == "brace"
    _wheel(s, 13.0, 40.0, 4.2)
    _wheel(s, 34.0, 40.0, 4.2)
    # a compact diamond frame + fork + bars, thin brass capsules
    s.capsule(23, 42, 13, 40, 1.1, 1.1, FRAMEB, sh=0.10)      # chainstay
    s.capsule(13, 40, 18, 32, 1.1, 1.1, FRAMEB, sh=0.06)      # seat stay
    s.capsule(18, 32, 23, 42, 1.1, 1.1, FRAMEB, sh=0.10)      # seat tube
    s.capsule(23, 42, 31, 31, 1.1, 1.1, FRAMEB, sh=0.06)      # down tube
    s.capsule(18, 31, 30, 31, 1.1, 1.1, FRAMEB, sh=0.02)      # top tube
    s.capsule(31, 31, 34, 40, 1.1, 1.1, FRAMEB, sh=0.10)      # fork
    s.capsule(31, 31, 33, 27, 1.0, 1.0, FRAMEB, sh=0.02)      # stem
    s.rect(32, 26, 35, 27, ATVIRON[1])                        # grips
    s.rect(14, 29, 19, 30, WHEELR[2])                         # saddle
    # the crank + pedals
    px0, px1 = (26, 20) if pose != "pedal1" else (20, 26)
    if brace:
        s.rect(21, 43, 25, 44, ATVIRON[1])                    # both feet braced
    else:
        s.rect(px0 - 1, 43, px0 + 1, 44, ATVIRON[1])
        s.rect(px1 - 1, 39, px1 + 1, 40, ATVIRON[1])
    # ---- the rider, chibi: stubby legs, round body, BIG head
    if brace:
        s.capsule(17, 28, 21, 41, 1.8, 1.5, KIT_FUR, sh=0.10)
        s.capsule(18, 28, 25, 41, 1.8, 1.5, KIT_FUR, sh=0.16)
    else:
        s.capsule(17, 28, px1, 38, 1.8, 1.5, KIT_FUR, sh=0.10)
        s.capsule(18, 28, px0, 42, 1.8, 1.5, KIT_FUR, sh=0.16)
    s.capsule(13, 29, 8, 24, 1.4, 1.1, KIT_FUR, sh=0.10)      # tail streaming
    s.set(7, 23, KIT_FUR[0])
    s.ball(19.0, 26.0, 4.6, 4.0, KIT_FUR, power=2.2, wrap=0.28, curve=0.22)
    s.ball(21.0, 27.5, 2.6, 2.2, WHITE, power=2.2, wrap=0.08, curve=0.08)
    s.capsule(22, 24, 32, 28, 1.6, 1.4, KIT_FUR, sh=0.14)     # arm to the bars
    # the head: nearly half the figure, like every cast sheet
    hx, hy = 27.0, 14.0 - (1.0 if brace else 0.0)
    s.tri((int(hx) - 4, int(hy) - 9), int(hy) - 4, int(hx) - 7, int(hx) - 1, KIT_FUR)
    s.tri((int(hx) + 4, int(hy) - 9), int(hy) - 4, int(hx) + 1, int(hx) + 7,
          KIT_FUR, sh=0.12)
    s.tri((int(hx) + 4, int(hy) - 7), int(hy) - 5, int(hx) + 3, int(hx) + 5, EARIN_D)
    s.ball(hx, hy, 7.0, 6.4, KIT_FUR, power=2.4, wrap=0.30, curve=0.26)
    s.ball(hx + 4.6, hy + 2.6, 2.8, 2.2, WHITE, power=2.2, wrap=0.08, curve=0.08)
    s.set(int(hx) + 6, int(hy) + 1, NOSE)
    # bandana: brow band + the knot trailing (flying up on the brace)
    s.rect(int(hx) - 6, int(hy) - 5, int(hx) + 5, int(hy) - 4, KIT_BAND[1])
    s.rect(int(hx) - 6, int(hy) - 4, int(hx) + 5, int(hy) - 4, KIT_BAND[2])
    if brace:
        s.capsule(hx - 7, hy - 4, hx - 11, hy - 8, 1.3, 1.0, KIT_BAND, sh=0.14)
    else:
        s.capsule(hx - 7, hy - 4, hx - 12, hy - 2, 1.3, 1.0, KIT_BAND, sh=0.14)
    if brace:                                        # eye WIDE, mouth open
        s.rect(int(hx), int(hy) - 3, int(hx) + 3, int(hy), (255, 255, 255, 255))
        s.set(int(hx) + 2, int(hy) - 1, PUPIL)
        s.rect(int(hx) + 4, int(hy) + 4, int(hx) + 5, int(hy) + 5, MAW)
    else:                                            # the kid-sheet 3x3 eye
        s.rect(int(hx) + 1, int(hy) - 3, int(hx) + 3, int(hy) - 1, KIT_EYE)
        s.rect(int(hx) + 1, int(hy) - 3, int(hx) + 3, int(hy) - 3, KIT_EYEL)
        s.rect(int(hx) + 2, int(hy) - 2, int(hx) + 2, int(hy) - 1, PUPIL)
        s.set(int(hx) + 3, int(hy) - 3, GLINT)
        s.line([(int(hx) + 4, int(hy) + 4), (int(hx) + 5, int(hy) + 4)], MOUTH)
    s.despeckle(passes=1)
    s.outline(outs_for((KIT_FUR, OUT_DARK), (WHITE, OUT_LIGHT),
                       (KIT_BAND, OUT_DARK), (WHEELR, OUT_DARK),
                       (FRAMEB, OUT_DARK), (ATVIRON, OUT_DARK)), OUT_DARK)
    for (wx, wy) in ((int(hx) + 8, int(hy) + 1), (int(hx) + 7, int(hy) + 3)):
        s.set(wx, wy, WHISK)                         # cheek whiskers


def kitty_tumble(s):
    """Kitty thrown — a compact mid-air CURL the accident scene spins
    through its arc (the Sprite2D rotates; the pose only has to stay
    round): knees hugged, tail wrapped over, bandana knot streaming, eyes
    squeezed shut. Cartoon-stylized on purpose — the loop reads as motion,
    never as harm; she lands into the sleeping `down` frame."""
    # curled body under the big head
    s.ball(21.0, 29.0, 5.2, 4.6, KIT_FUR, power=2.2, wrap=0.26, curve=0.22)
    s.ball(22.5, 31.0, 2.8, 2.2, WHITE, power=2.2, wrap=0.08, curve=0.08)
    s.capsule(17, 32, 14, 28, 1.7, 1.4, KIT_FUR, sh=0.14)     # tucked legs
    s.capsule(25, 33, 28, 30, 1.7, 1.4, KIT_FUR, sh=0.10)
    s.capsule(14, 25, 19, 20, 1.3, 1.0, KIT_FUR, sh=0.12)     # tail wraps the curl
    s.set(20, 19, KIT_FUR[0])
    # the big head tipped INTO the roll
    hx, hy = 27.0, 20.0
    s.tri((int(hx) - 5, int(hy) - 9), int(hy) - 4, int(hx) - 8, int(hx) - 2, KIT_FUR)
    s.tri((int(hx) + 3, int(hy) - 9), int(hy) - 4, int(hx), int(hx) + 6,
          KIT_FUR, sh=0.12)
    s.ball(hx, hy, 7.0, 6.4, KIT_FUR, power=2.4, wrap=0.30, curve=0.26)
    s.ball(hx + 4.4, hy + 2.6, 2.8, 2.2, WHITE, power=2.2, wrap=0.08, curve=0.08)
    s.set(int(hx) + 6, int(hy) + 1, NOSE)
    # bandana band + the knot STREAMING with the spin
    s.rect(int(hx) - 6, int(hy) - 5, int(hx) + 5, int(hy) - 4, KIT_BAND[1])
    s.capsule(hx - 7, hy - 4, hx - 13, hy - 8, 1.3, 1.0, KIT_BAND, sh=0.14)
    # eyes squeezed shut, little o mouth
    s.line([(int(hx) + 1, int(hy) - 2), (int(hx) + 2, int(hy) - 3),
            (int(hx) + 3, int(hy) - 2)], MOUTH)
    s.set(int(hx) + 5, int(hy) + 4, MAW)
    s.despeckle(passes=1)
    s.outline(outs_for((KIT_FUR, OUT_DARK), (WHITE, OUT_LIGHT),
                       (KIT_BAND, OUT_DARK)), OUT_DARK)


def kitty_down(s):
    """Kitty still on the road (the aftermath) — lying on her side, eyes
    closed, bandana fanned out. Chibi head, soft and non-violent: a
    sleeping read."""
    s.ball(18.0, 40.5, 5.0, 3.4, KIT_FUR, power=2.2, wrap=0.24, curve=0.20)
    s.ball(20.0, 41.5, 2.6, 2.0, WHITE, power=2.2, wrap=0.08, curve=0.08)
    s.capsule(12, 42, 9, 44, 1.6, 1.3, KIT_FUR, sh=0.12)      # legs tucked
    s.capsule(11, 40, 6, 37, 1.3, 1.0, KIT_FUR, sh=0.12)      # tail
    s.set(5, 36, KIT_FUR[0])
    # the big head, resting on the road
    s.tri((26, 30), 34, 23, 29, KIT_FUR)                      # ear
    s.ball(29.0, 38.0, 6.4, 5.8, KIT_FUR, power=2.4, wrap=0.28, curve=0.24)
    s.ball(33.5, 40.0, 2.6, 2.0, WHITE, power=2.2, wrap=0.06, curve=0.06)
    s.set(35, 38, NOSE)
    s.rect(23, 34, 34, 35, KIT_BAND[1])                       # bandana band
    s.capsule(35, 35, 40, 33, 1.3, 1.0, KIT_BAND, sh=0.10)    # knot, fanned
    s.line([(29, 38), (31, 38)], MOUTH)                       # closed eye
    # an arm slack on the road
    s.capsule(22, 42, 29, 44, 1.5, 1.3, KIT_FUR, sh=0.14)
    s.ball(30.0, 44.0, 1.5, 1.3, WHITE, power=2.2, wrap=0.06, curve=0.06)
    s.despeckle(passes=1)
    s.outline(outs_for((KIT_FUR, OUT_DARK), (WHITE, OUT_LIGHT),
                       (KIT_BAND, OUT_DARK)), OUT_DARK)


def atv(s, pose="drive0"):
    """Schweinler's machine, barreling LEFT — the rider at the cast's chibi
    proportions (big pig head, proper snout, plum waistcoat). Fat wheels,
    riveted copper cowling, an exhaust stack coughing steam. swerve tips
    the whole rig; skid adds the dust of brakes losing the argument;
    `parked` is the machine ALONE, stack cold — the bragging beat before
    he climbs on (the 2026-07-16 setup rework)."""
    parked = pose == "parked"
    tilt = {"drive0": 0, "drive1": 0, "swerve": 1, "skid": 2, "parked": 0}[pose]
    bob = 1 if pose == "drive1" else 0
    _wheel(s, 11.0, 40.0 + tilt * 0.5, 5.5)
    _wheel(s, 37.0, 40.0 - tilt * 0.5, 5.5)
    # cowling: a fat copper wedge, nose down-left
    ny = 29 + bob + tilt
    s.capsule(12, ny + 5, 37, ny + 3 - tilt, 5.5, 6.0, ATVBODY, sh=0.08)
    s.rect(5, ny + 3 + tilt, 12, ny + 8 + tilt, ATVBODY[2])   # the scoop nose
    s.rect(5, ny + 3 + tilt, 12, ny + 3 + tilt, ATVBODY[1])
    # rivets along the cowl
    for rx in range(15, 36, 5):
        s.set(rx, ny + 6, SPARK_D)
    # exhaust stack (+ steam only once it's running)
    s.rect(39, ny - 6, 41, ny + 2, ATVIRON[2])
    s.rect(39, ny - 6, 41, ny - 6, ATVIRON[1])
    if not parked:
        puff = 0 if pose in ("drive0", "swerve") else 1
        s.set(41 + puff, ny - 9, SPARK)
        s.set(43, ny - 11 + puff, SPARK_D)
    # handlebar
    s.capsule(12, ny + 1, 9, ny - 5, 1.1, 1.0, ATVIRON, sh=0.06)
    s.rect(7, ny - 6, 10, ny - 5, ATVIRON[1])
    if parked:
        # the saddle sits empty; a proud little bow on the bars (it's NEW)
        s.rect(22, ny - 2, 29, ny, WHEELR[2])
        s.rect(8, ny - 8, 10, ny - 7, KERCH[1])
        s.set(9, ny - 6, KERCH[2])
    else:
        # ---- Schweinler, chibi: waistcoat body low, BIG head over the bars
        s.ball(25.0, ny - 3.0, 4.6, 4.0, VEST, power=2.2, wrap=0.24, curve=0.20)
        s.capsule(21, ny - 4, 10, ny - 4, 1.6, 1.4, PIG, sh=0.12)  # arm to the bars
        hx, hy = 19.0, ny - 13.0
        if pose in ("swerve", "skid"):
            hx -= 1.0
        s.tri((int(hx) - 4, int(hy) - 9), int(hy) - 4, int(hx) - 7, int(hx) - 1, PIG)
        s.tri((int(hx) + 4, int(hy) - 9), int(hy) - 4, int(hx) + 1, int(hx) + 7,
              PIG, sh=0.12)
        s.ball(hx, hy, 7.0, 6.3, PIG, power=2.4, wrap=0.30, curve=0.26)
        # the snout leads the way (he faces left)
        s.ball(hx - 5.4, hy + 1.8, 3.2, 2.6, SNOUT, power=2.2, wrap=0.08, curve=0.08)
        s.set(int(hx) - 6, int(hy) + 1, MAW)                      # nostrils
        s.set(int(hx) - 4, int(hy) + 1, MAW)
        if pose == "skid":                              # eye wide, mouth open
            s.rect(int(hx) - 4, int(hy) - 4, int(hx) - 1, int(hy) - 1,
                   (255, 255, 255, 255))
            s.set(int(hx) - 3, int(hy) - 2, PIG_EYE)
            s.rect(int(hx) - 6, int(hy) + 4, int(hx) - 5, int(hy) + 5, MAW)
        else:
            s.rect(int(hx) - 3, int(hy) - 3, int(hx) - 2, int(hy) - 2, PIG_EYE)
            s.set(int(hx) - 2, int(hy) - 3, GLINT)
    # motion lines / skid dust
    if pose == "swerve":
        for ly in (int(ny) - 2, int(ny) + 3, int(ny) + 8):
            s.rect(44, ly, 47, ly, SPARK_D)
    elif pose == "skid":
        for (dx, dy) in ((6, 44), (9, 46), (4, 46), (14, 45), (40, 45), (43, 44)):
            s.set(dx, dy, OUT_LIGHT)
    s.despeckle(passes=1)
    s.outline(outs_for((PIG, OUT_DARK), (SNOUT, OUT_DARK), (VEST, OUT_DARK),
                       (ATVBODY, OUT_DARK), (ATVIRON, OUT_DARK),
                       (KERCH, OUT_DARK), (WHEELR, OUT_DARK)), OUT_DARK)


def bike_down(s):
    """The fallen bicycle, on its side across the road — the front wheel
    still turning somewhere in the viewer's mind."""
    # rear wheel flat-ish (seen at a low tilt), front wheel up
    s.ball(14.0, 41.0, 6.5, 3.0, WHEELR, power=2.2, wrap=0.10, curve=0.10)
    s.ball(33.0, 36.0, 5.0, 5.0, WHEELR, power=2.2, wrap=0.10, curve=0.10)
    s.ball(33.0, 36.0, 2.8, 2.8, ATVIRON, power=2.0, wrap=0.05, curve=0.05)
    s.set(33, 36, STEELF[0])
    s.capsule(14, 41, 26, 38, 1.1, 1.1, FRAMEB, sh=0.10)      # bent frame
    s.capsule(26, 38, 33, 36, 1.1, 1.1, FRAMEB, sh=0.06)
    s.capsule(20, 40, 24, 34, 1.0, 1.0, FRAMEB, sh=0.04)      # seat tube up
    s.rect(21, 32, 25, 33, WHEELR[2])                         # saddle skyward
    s.rect(36, 33, 38, 34, ATVIRON[1])                        # a thrown grip
    s.despeckle(passes=1)
    s.outline(outs_for((WHEELR, OUT_DARK), (FRAMEB, OUT_DARK),
                       (ATVIRON, OUT_DARK)), OUT_DARK)


def fx_watch(s):
    """Basil's wrist-comm (the call beat): brass case, mint ward-glass."""
    s.rect(6, 0, 9, 2, KIT_BAND[2])                 # strap, teal
    s.rect(6, 13, 9, 15, KIT_BAND[2])
    s.rect(4, 3, 11, 12, BRASSF[2])                 # case
    s.rect(5, 4, 10, 11, BRASSF[1])
    s.rect(6, 5, 9, 10, (150, 240, 214, 255))       # the mint face
    s.rect(7, 6, 7, 8, (60, 140, 128, 255))         # hands
    s.rect(7, 8, 8, 8, (60, 140, 128, 255))
    s.set(5, 4, SPARK)
    s.outline(outs_for((BRASSF, OUT_DARK), (KIT_BAND, OUT_DARK)), OUT_DARK)


def fx_poof(s):
    """The impact flash — one toned beat, never a contact frame."""
    for (dx, dy) in ((0, -7), (0, 7), (-7, 0), (7, 0),
                     (-5, -5), (5, 5), (-5, 5), (5, -5)):
        s.line([(8, 8), (8 + dx, 8 + dy)], SPARK_D)
    s.rect(6, 6, 10, 10, SPARK)
    s.rect(7, 7, 9, 9, (255, 255, 255, 255))


def fx_lines(s):
    """Speed / swerve motion dashes."""
    s.rect(2, 4, 12, 4, SPARK_D)
    s.rect(4, 8, 14, 8, SPARK_D)
    s.rect(1, 12, 10, 12, SPARK_D)


HEART = (226, 76, 120, 255)                        # festival-magenta kin
HEART_L = (255, 150, 180, 255)


def fx_heart(s):
    """A blooming heart — the bluff kiss (frame 19)."""
    for (x0, x1, y) in ((4, 6, 3), (9, 11, 3), (3, 7, 4), (8, 12, 4),
                        (3, 12, 5), (3, 12, 6), (4, 11, 7), (5, 10, 8),
                        (6, 9, 9), (7, 8, 10)):
        s.rect(x0, y, x1, y, HEART)
    s.rect(4, 4, 5, 5, HEART_L)                    # lit lobe
    s.set(5, 4, (255, 255, 255, 255))              # glint
    s.outline({HEART: (120, 26, 60, 255), HEART_L: (120, 26, 60, 255)},
              (120, 26, 60, 255))


def fx_magic_spark(s, big):
    """A 4-point mote of raw magic (frames 20-21, the Ebb night: sparks
    streaming into the summit crystal; Fuji's wand casts). White-hot heart,
    mint-white body, violet fringe. big=False is the smaller/dimmer 2px-armed
    variant for trail/flicker alternation. Bare hand-set pixels like the
    sibling sparkle/zzz cells — no despeckle/outline pass."""
    c = 8
    if big:
        for d in range(1, 4):                      # mint cross arms
            for (x, y) in ((c, c - d), (c, c + d), (c - d, c), (c + d, c)):
                s.set(x, y, MSPARK)
        for (x, y) in ((c, c - 4), (c, c + 4), (c - 4, c), (c + 4, c)):
            s.set(x, y, MSPARK_V)                  # violet arm tips
        for (x, y) in ((c - 1, c - 1), (c + 1, c - 1),
                       (c - 1, c + 1), (c + 1, c + 1)):
            s.set(x, y, MSPARK)                    # core diamond
        for (x, y) in ((c - 2, c - 2), (c + 2, c - 2),
                       (c - 2, c + 2), (c + 2, c + 2)):
            s.set(x, y, MSPARK_V)                  # diagonal violet fringe
        s.set(c, c, MSPARK_W)                      # white-hot heart
    else:
        for d in (1, 2):                           # 2px arms, violet-tipped
            col = MSPARK if d == 1 else MSPARK_V
            for (x, y) in ((c, c - d), (c, c + d), (c - d, c), (c + d, c)):
                s.set(x, y, col)
        s.set(c, c, MSPARK)                        # dimmer: no pure white


def fx_burst(s, big):
    """The recital firework (frames 22-23): big=False the rising ember and
    its trailing sparks, big=True the burst ring.

    Drawn WHITE-HOT AND COLOURLESS on purpose. scene/hall.gd modulate-tints
    each instance to one of Alchemy's four compound tints — on the ORDINARY
    mix blend, NOT an additive one (cream at ~250 added onto the hall
    saturates every channel and all four colours arrive the same pale white,
    and which colour it is IS the beat; the bursts get their punch from the
    houselights going down around them instead). So this one pair of cells
    makes all four colours — the kid's first potion is the same
    green/blue/red/purple he'll be firing two decades later. Do NOT reuse the
    sparkle cells (2-3) for this: SPARK_D is warm gold, and gold multiplied
    by a blue tint is mud. Bare hand-set pixels like the sibling
    sparkle/magic-spark cells — an outline pass would fight the tint."""
    c = 8
    if big:
        for d in (5, 6):                           # the ring: axes...
            for (x, y) in ((c, c - d), (c, c + d), (c - d, c), (c + d, c)):
                s.set(x, y, BURST_C if d == 5 else BURST_D)
        for d in (3, 4):                           # ...and diagonals
            for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                s.set(c + sx * d, c + sy * d, BURST_C if d == 3 else BURST_D)
        for d in range(1, 3):                      # the collapsing arms
            for (x, y) in ((c, c - d), (c, c + d), (c - d, c), (c + d, c)):
                s.set(x, y, BURST_C)
        for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            s.set(c + sx, c + sy, BURST_W)         # core diamond
        s.set(c, c, BURST_W)
    else:
        for d in (1, 2):                           # a 4-point mote
            col = BURST_C if d == 1 else BURST_D
            for (x, y) in ((c, c - d), (c, c + d), (c - d, c), (c + d, c)):
                s.set(x, y, col)
        s.set(c, c, BURST_W)


FLASKG = ramp((176, 226, 234), "teal", 4)          # fx: pale reagent glass


def fx_beaker(s):
    """The recital potion (frame 24): a stoppered conical flask — brewed at
    the workbench, then pinned under the whirligig's pod as its payload.

    The fill is drawn in a LIGHT cream so downstairs_fest can modulate-cycle
    it through Alchemy's four tints while the stir meter fills (the player
    literally stirs the four sky colours in), and hall.gd can fade its alpha
    across the four bursts so the flask visibly empties."""
    s.rect(6, 2, 9, 3, BRASSF[2])                   # the stopper
    s.rect(6, 1, 9, 1, BRASSF[1])
    s.rect(7, 4, 8, 6, FLASKG[1])                   # the neck
    for (x0, x1, y) in ((6, 9, 7), (5, 10, 8), (5, 10, 9),
                        (4, 11, 10), (4, 11, 11), (4, 11, 12), (5, 10, 13)):
        s.rect(x0, y, x1, y, FLASKG[1])             # the cone
    for (x0, x1, y) in ((5, 10, 10), (5, 10, 11), (5, 10, 12), (6, 9, 13)):
        s.rect(x0, y, x1, y, BURST_C)               # the reagent, tintable
    s.set(5, 8, BURST_W)                            # glass glint
    s.despeckle(passes=1)
    s.outline(outs_for((FLASKG, OUT_DARK), (BRASSF, OUT_DARK)), OUT_DARK)


def accident_bg():
    """The dusk FOREST TRACK backdrop for scene/accident.tscn — one 384x216
    painting (a one-off set, not a tileset).

    REBUILT 2026-07-30: the first two cuts were a country ROAD — a painted
    centerline, a fence line, open hill country — and this kingdom has no
    roads. Carts and machines run on rutted tracks through the wood, which
    is also the honest reason the fastest machine in the kingdom kills
    somebody on it. The GEOMETRY is unchanged (the walkable band stays
    y 154-200, so accident.gd's lanes and every tween are untouched); the
    world around it is new: a two-rut cart track in a dusk wood, near trunks
    rising out of frame with the last of the sun burning between them, a
    canopy closing the top of the frame, leaf litter and fern on both
    verges. Duo-tone violet dusk with the amber sun as the only hot accent,
    per the palette law; hard bands everywhere, no dither."""
    W, H = 384, 216
    img = Img(W, H)
    horizon = 128                                   # the far tree line's foot
    path_top, path_bot = 154, 200                   # PINNED — the cast's lanes
    # (the vehicles' wheels ride ~14px above path_bot, so the 48px cast
    # fills the track — scene/accident.gd's LANE_* match this geometry)
    SKY_T = (44, 30, 74)
    SKY_M = (110, 52, 96)
    SKY_H = (214, 110, 88)
    AMBER = (244, 168, 92, 255)
    AMBER_H = (252, 204, 128, 255)
    STAR = (238, 222, 240, 255)
    FAR = (64, 42, 80, 255)                         # far wood, hazed by distance
    NEAR = (42, 28, 58, 255)                        # the mass behind the trunks
    CANOPY_L = (46, 30, 60, 255)                    # the leaf overhead, two layers
    CANOPY = (28, 18, 42, 255)
    TRUNK = (44, 30, 52, 255)
    TRUNK_M = (70, 46, 66, 255)                     # the one lit band of bark
    RIM = (156, 96, 82, 255)                        # the sun's edge-light, and it
    RIM_D = (94, 60, 72, 255)                       # falls off away from the sun
    ROOT = (76, 52, 62, 255)                        # root over dirt, not over sky
    # the ground gets LIGHTER as it comes forward — and the verge has to clear
    # TRUNK or the trunk feet vanish into it and leave their rim lines floating
    VERGE = (70, 48, 78, 255)                       # forest floor, both sides
    SCRUB = (52, 34, 62, 255)                       # bushes ON it — their own
    LITTER = (88, 60, 84, 255)                      # value, between wood and floor
    DRIFT = (128, 74, 64, 255)                      # fallen leaves — the hue break
    PATH = (90, 62, 68, 255)                        # packed DIRT — a pale value
    PATH_L = (118, 84, 82, 255)                     # here reads as paving stone
    PATH_D = (64, 44, 58, 255)
    RUT = (74, 52, 64, 255)
    DAPPLE = (192, 132, 96, 255)                    # what gets through the trunks
    FORE = (26, 16, 38, 255)                        # near undergrowth, near-black
    FLOWER = (150, 84, 128, 255)
    SUN = (292, 106)

    def lerp3(a, b, t):
        return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t),
                int(a[2] + (b[2] - a[2]) * t), 255)

    def meander(v, salt, amp):
        """A smooth 16-period wobble — every edge in a wood is a curve, and a
        ruler-straight one is what made the first cut read as pavement."""
        a = h2(v // 16, salt, 3) / 255.0
        b = h2(v // 16 + 1, salt, 3) / 255.0
        return int(round((a + (b - a) * ((v % 16) / 16.0)) * amp))

    def leaf(lx, ly, r, color):
        for y in range(-r, r + 1):                  # a leaf mass is a PATCH, never
            half = int((r * r - y * y) ** 0.5)      # a sloping LINE (the understory
            img.rect(lx - half, ly + y, lx + half, ly + y, color)   # law)

    # ---- sky: the same banded violet-to-rose dusk, seen in the gaps ------------
    for y in range(horizon):
        t = int(y / float(horizon) * 9) / 9.0       # hard 9-band gradient
        c = lerp3(SKY_T, SKY_M, t / 0.6) if t < 0.6 \
            else lerp3(SKY_M, SKY_H, (t - 0.6) / 0.4)
        img.rect(0, y, W - 1, y, c)
    # the low sun's haze, four hard rings, squashed (it spreads along the wood)
    for y in range(horizon):
        for x in range(W):
            dx, dy = x - SUN[0], (y - SUN[1]) * 1.4
            d = (dx * dx + dy * dy) ** 0.5
            if d < 100.0:
                img.mix(x, y, AMBER, (0.42, 0.28, 0.16, 0.07)[int(d / 25.0)])
    for (sx, sy) in ((22, 62), (66, 54), (128, 70), (176, 58), (94, 88),
                     (232, 66), (268, 52), (348, 60), (150, 96), (312, 78)):
        if ((sx - SUN[0]) ** 2 + (sy - SUN[1]) ** 2) ** 0.5 > 96.0:
            img.put(sx, sy, STAR)                   # first stars, clear of the haze
    for dy in range(-11, 12):                       # the sun itself, banded
        half = int((121 - dy * dy) ** 0.5)
        for dx in range(-half, half + 1):
            img.put(SUN[0] + dx, SUN[1] + dy, AMBER if dy > -5 else AMBER_H)

    def crown_line(salt, base, lo, hi, rlo, rhi, gap, color):
        """A silhouette band of overlapping crown lobes along `base` — the
        lobe arcs ARE the treeline, the same law the tileset's canopy uses."""
        top = [base] * W
        cx = -12
        while cx < W + 24:
            r = rlo + h2(cx, salt, 3) % (rhi - rlo + 1)
            rise = lo + h2(cx, salt, 5) % (hi - lo + 1)
            for x in range(cx - r, cx + r + 1):
                if 0 <= x < W:
                    u = (x - cx) / float(r)
                    top[x] = min(top[x], base - int((1.0 - u * u) ** 0.5 * rise))
            cx += max(7, r + gap - h2(cx, salt, 9) % 8)
        for x in range(W):
            img.rect(x, top[x], x, base, color)

    # ---- the wood, back to front ----------------------------------------------
    crown_line(1, horizon - 5, 12, 30, 13, 24, 10, FAR)
    crown_line(2, horizon, 7, 18, 10, 18, 8, NEAR)
    for (cx, ch, cw) in ((36, 36, 10), (188, 44, 12), (300, 32, 9), (352, 38, 11)):
        for i in range(ch):                         # conifers: TIERED, not cones
            half = max(1, int(cw * ((i + 1) / float(ch)) ** 0.8)
                       - (3 if i % 9 < 2 else 0))
            img.rect(cx - half, horizon - ch + i, cx + half, horizon - ch + i, NEAR)
    # the far verge: forest floor from the tree feet down to the track's lip.
    # Its top edge MEANDERS — a ruled line across the full width is a painted
    # backdrop the treeline is standing in front of.
    for x in range(W):
        img.rect(x, horizon - 7 + meander(x, 71, 8), x, path_top + 6, VERGE)

    # ---- the track: two ruts in packed dirt, both edges meandering -------------
    top_e = [path_top + meander(x, 11, 6) - 3 for x in range(W)]
    bot_e = [path_bot - meander(x, 23, 6) + 3 for x in range(W)]
    for x in range(W):
        img.rect(x, top_e[x], x, bot_e[x], PATH)
        img.put(x, top_e[x], PATH_L)                # the low sun grazes the far lip
        img.put(x, bot_e[x], PATH_D)
    for (ry, salt) in ((path_top + 15, 31), (path_top + 31, 37)):
        for x in range(W):                          # the ruts, fading in and out
            if h2(x // 7, salt, 2) % 7 == 0:
                continue
            y = ry + meander(x, salt, 4) - 2
            img.rect(x, y, x, y + 1, RUT)
            img.put(x, y + 2, PATH_L)               # the lit lower lip of a trench
    # The dirt has to be OVERGROWN at its edges or the meander alone reads as a
    # kerb — bare dirt between two clean lines is a paved lane whatever colour
    # it is, and the first rebuild's crossing roots only added cracks to it.
    for gx in range(0, W, 3):
        for (edge, sgn, salt) in ((top_e, 1, 51), (bot_e, -1, 53)):
            t = h2(gx, salt, 6) % 5
            if t:
                for i in range(t):                  # tufts breaking into the track
                    img.rect(gx, edge[gx] + sgn * i, gx + h2(gx, salt, 8) % 2,
                             edge[gx] + sgn * i, VERGE)
    for lx_ in range(5, W, 17):                     # leaf drift ON the track: the
        ly_ = top_e[lx_] + 4 + h2(lx_, 55, 7) % 38  # one thing dirt has and stone
        if ly_ < bot_e[lx_] - 1:                    # never does
            leaf(lx_, ly_, 1 + h2(lx_, 57, 4) % 2, DRIFT)
    for (dx_, dy_, dw, dh) in ((36, 172, 19, 5), (96, 187, 14, 4), (152, 165, 21, 5),
                               (228, 179, 16, 4), (278, 169, 23, 6), (332, 190, 15, 4)):
        for y in range(dy_ - dh, dy_ + dh + 1):     # dapple: what gets through
            for x in range(dx_ - dw, dx_ + dw + 1):
                u = ((x - dx_) / float(dw)) ** 2 + ((y - dy_) / float(dh)) ** 2
                lim = 1.0 - (h2(x // 3, dx_, 7) % 34) / 100.0   # a RAGGED pool of
                if u <= lim and 0 <= x < W and top_e[x] + 2 < y < bot_e[x] - 1:
                    img.mix(x, y, DAPPLE, 0.34 if u < lim * 0.45 else 0.17)
    for gx in range(3, W, 13):                      # grit and small stones
        gy = top_e[gx] + 5 + (gx * 7) % 34
        if gy < bot_e[gx] - 2:
            img.put(gx, gy, PATH_D)
            if gx % 39 == 3:
                img.rect(gx, gy - 1, gx + 1, gy, PATH_D)
                img.put(gx, gy - 2, PATH_L)

    # ---- the near trunks: the whole reason this reads as a wood ----------------
    for (tx, base, wt, wb, salt) in ((16, 145, 6, 9, 3), (58, 137, 4, 6, 5),
                                     (104, 142, 5, 7, 7), (152, 133, 3, 5, 11),
                                     (200, 144, 6, 8, 13), (244, 136, 4, 6, 17),
                                     (316, 146, 7, 10, 19), (366, 138, 5, 7, 23)):
        lit = 1 if tx < SUN[0] else -1              # every rim faces the sun
        # ...and falls off with distance from it, and BREAKS on the bark. An
        # unbroken 1px stripe of hot orange up a black trunk is a neon tube.
        rim_c = RIM if abs(tx - SUN[0]) < 150 else RIM_D
        bw = (h2(tx, salt, 1) % 7) - 3              # a trunk BOWS; a ruler is a post
        for i in range(7):                          # the root flare, drawn under
            e = (8 - i) // 2
            img.rect(tx - wb - e, base - i, tx + wb + e, base - i, TRUNK)
        for y in range(0, base + 1):
            t = y / float(base)
            half = int(round(wt + (wb - wt) * t))
            off = int(round(bw * (1.0 - (2.0 * t - 1.0) ** 2)))
            img.rect(tx + off - half, y, tx + off + half, y, TRUNK)
            m0, m1 = sorted((tx + off + lit * (half - 3), tx + off + lit * (half - 1)))
            img.rect(m0, y, m1, y, TRUNK_M)
            if h2(y // 4, salt, 21) % 4:
                img.put(tx + off + lit * half, y, rim_c)
        for k in range(3):                          # roots gripping the verge
            rl = 4 + h2(tx, k, 13) % 7
            sgn = -1 if k % 2 else 1
            x0, x1 = sorted((tx + sgn * wb, tx + sgn * (wb + rl)))
            img.rect(x0, base + 1 + k, x1, base + 1 + k, TRUNK)
        if h2(tx, salt, 2) % 2 == 0:                # a BARE LIMB on half of them
            sy = 56 + h2(tx, salt, 4) % 30          # — eight bare shafts running
            sd = 1 if h2(tx, salt, 6) % 2 else -1   # floor to canopy is a
            sl = 16 + h2(tx, salt, 8) % 7           # COLONNADE, not a wood.
            for s in range(sl):                     # No leaf clumps: a small dark
                by_ = sy - int(s * 0.62)            # ball on a thin stick reads
                th = 2 if s < sl * 0.35 else (1 if s < sl * 0.75 else 0)
                img.rect(tx + sd * (wt + s), by_, tx + sd * (wt + s),
                         by_ + th, TRUNK)           # as something FLYING, and
                for (at, tl) in ((sl // 2, 6), (sl * 3 // 4, 4)):
                    if s == at:                     # two twigs — a limb forks
                        for f in range(tl):
                            img.put(tx + sd * (wt + s + f * 2 // 3), by_ - 1 - f,
                                    TRUNK)

    # ---- the verge dressing, in FRONT of the trunk feet ------------------------
    def fern(fx, fy, fh, color):
        img.rect(fx, fy - fh, fx, fy, color)
        for i in range(1, fh, 2):
            w = 1 + (fh - i) // 3
            img.rect(fx - w, fy - i, fx - 1, fy - i, color)
            img.rect(fx + 1, fy - i, fx + w, fy - i, color)

    # scrub first: the mass that bridges the tree feet to the ground. Without
    # it the verge is a flat 26px stripe of one colour across the whole frame,
    # which is what the treeline is standing on and reads as a painted wall.
    for sx_ in range(-4, W + 12, 11):
        bx = sx_ + h2(sx_, 61, 3) % 9
        by = horizon + 2 + h2(sx_, 63, 5) % 9       # ON the verge. Straddling the
        r = 3 + h2(sx_, 65, 7) % 4                  # treeline's foot in the SAME
        leaf(bx, by, r, SCRUB)                      # value as the treeline made
        leaf(bx + r, by + 1, max(2, r - 2), SCRUB)  # lumps at an unreadable depth
        img.rect(bx, by - r, bx + r - 1, by - r, LITTER)   # a crown catching sky
    for (lx_, ly_, ll) in ((110, horizon + 19, 38), (294, horizon + 14, 24)):
        img.rect(lx_, ly_ - 5, lx_ + ll, ly_, TRUNK)         # fallen logs, the
        img.rect(lx_ + 1, ly_ - 6, lx_ + ll - 1, ly_ - 5, TRUNK_M)   # verge's
        img.rect(lx_ + 2, ly_ - 7, lx_ + ll - 3, ly_ - 7, LITTER)    # one big
        img.rect(lx_ - 3, ly_ - 4, lx_ - 1, ly_, TRUNK)      # shape, and it
        img.rect(lx_ + ll + 1, ly_ - 3, lx_ + ll + 2, ly_, TRUNK)    # has ends
        for k in range(3, ll - 2, 9):
            img.put(lx_ + k, ly_ - 4, LITTER)
    for vx in range(3, W, 6):
        vy = horizon + 6 + (h2(vx, 27, 4) % 18)
        kind = h2(vx, 29, 6) % 5
        if kind == 0:
            fern(vx, min(vy + 6, top_e[vx] - 1), 7 + h2(vx, 31, 8) % 6, SCRUB)
        elif kind == 1:                             # warm drift, the hue break
            leaf(vx, min(vy + 8, top_e[vx] - 2), 1 + h2(vx, 33, 2) % 2, DRIFT)
        elif kind == 2:
            img.rect(vx, vy, vx + 1 + h2(vx, 35, 3) % 3, vy, LITTER)
        elif kind == 3:
            leaf(vx, vy + 2, 2, SCRUB)

    # ---- the canopy closes the top of the frame -------------------------------
    def canopy(salt, rlo, rhi, dlo, dhi, gap, color):
        bot = [-1] * W
        cx = -14
        while cx < W + 24:
            r = rlo + h2(cx, salt, 3) % (rhi - rlo + 1)
            drop = dlo + h2(cx, salt, 5) % (dhi - dlo + 1)
            for x in range(cx - r, cx + r + 1):
                if 0 <= x < W:
                    u = (x - cx) / float(r)
                    bot[x] = max(bot[x], int((1.0 - u * u) ** 0.5 * drop))
            cx += max(8, r + gap - h2(cx, salt, 9) % 9)
        for x in range(W):
            img.rect(x, 0, x, bot[x], color)

    canopy(7, 16, 30, 26, 46, 6, CANOPY_L)
    canopy(8, 14, 26, 20, 38, 7, CANOPY)
    # one bough drooping into frame. The masses must OVERLAP into a single
    # ragged silhouette — spaced out along the limb they were beads on a wire.
    for s in range(96):
        x = 336 - s
        y = 26 + int(s * s / 260.0)                 # the droop, not a slope
        img.rect(x, y, x, y + 2 + s // 40, CANOPY)
    for (lx, ly, lr) in ((328, 29, 6), (317, 33, 7), (305, 38, 7), (293, 44, 6),
                         (281, 50, 6), (269, 55, 5), (257, 59, 4), (247, 61, 3)):
        leaf(lx, ly, lr, CANOPY)                    # overlapping, but a BOUGH —
                                                    # at r=10 it is a black slab

    # ---- the near undergrowth: a black silhouette band framing the bottom ------
    for x in range(W):
        img.rect(x, bot_e[x] + 1, x, H - 1, FORE)
    for ux in range(6, W, 11):
        fern(ux, bot_e[ux] + 3 + h2(ux, 39, 5) % 7, 7 + h2(ux, 41, 9) % 7, FORE)
    for fx_ in range(11, W, 46):                    # dusk flowers, sparse
        fy_ = bot_e[fx_] + 9 + (fx_ * 3) % 8
        img.put(fx_, fy_, FLOWER)
        img.put(fx_ + 1, fy_ + 1, FLOWER)
    img.save(os.path.join(HERE, "accident_bg.png"))


# ---- build all sheets -----------------------------------------------------------------------

# kid Basil: 6x6
kb = [[new() for _ in range(6)] for _ in range(6)]
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
# row 4 (2026-07-15): the fest sunrise wake-up — sleep / wake / sigh
kb_down(kb[4][0], eyes="blink", bob=1, tail_droop=1)   # sleep: relaxed closed lids
kb_down(kb[4][1], eyes="open", bob=-1)                 # wake: eyes wide, head lifted
kb_down(kb[4][2], eyes="sad", ears="droop", tail_droop=1)   # sigh: half-lids, ears down
for (bx, by) in ((CX + 9, 28), (CX + 11, 26), (CX + 12, 24)):
    kb[4][2].set(bx, by, WHISK)                        # the exhaled breath drifting off
# row 5 (2026-07-30): THE LADDER CLIMB, four frames in cols 0-3. The adult sheet
# and Fuji's grew this row when Alembic's great trees went in; the kid's predated
# it, so kid Basil kept falling back to walk_up on a rung (party_member.gd gates
# the clip on the SpriteFrames actually carrying it).
for i in range(4):
    kb_climb(kb[5][i], i)
write_cells(os.path.join(HERE, "kid_basil_gen.png"), kb, CELL)


def walk_rows(row_down, row_up, row_side):
    """Rows 1-3 of a WALKING villager sheet: walk_down / walk_up / walk_side,
    6 frames each, each row padded out to 10 cells (write_cells wants a square
    [rows][cols] grid, and row 0 is the 10-cell pose row).

    Every character drives the SAME proven stride tables kid Basil's playable
    sheet is cut from — a shuffle, not a churn: the stepping paw lifts 1px, a
    heel-up tap, and both paw tips stay visible under the hem for the whole
    cycle. f0 of the down and up rows is the planted neutral pose, so it comes
    out byte-identical to row-0 cells 0 and 6. NO hem sway in down/up — it is
    perpendicular to travel there and wags; the side row keeps its fore/aft
    scissor, which lies along the motion."""
    rows = []
    for fn in (row_down, row_up, row_side):
        cells = [new() for _ in range(10)]
        for i in range(6):
            fn(cells[i], i)
        rows.append(cells)
    return rows


# The CHILDREN grew cols 6-9 on 2026-07-29 — BACK x2 + SIDE x2 (npc.gd builds
# `back` at frame_cols >= 8 and `side` at >= 10; every existing 6-col spawn is
# untouched, and cells 0-5 of all four sheets are byte-identical to the shipped
# bytes). Before this they slid around front-facing: play_back()/play_side()
# were silent no-ops on a 6-col sheet, and Kitty in particular is staged
# turning and walking all over Prologue A.

# Sage: [idle, blink, cast x2, giggle x2, BACK x2, SIDE x2]
sg = [[new() for _ in range(10)]]
sage(sg[0][0])
sage(sg[0][1], eyes="blink")
sage(sg[0][2], arms="up", sparkle=True)
sage(sg[0][3], arms="up", bob=-1, sparkle=True)
sage(sg[0][4], eyes="happy", sway=2)
sage(sg[0][5], eyes="happy", bob=-1, sway=-2)
sage_back(sg[0][6])
sage_back(sg[0][7], bob=-1, sway=1)
sage_side(sg[0][8])
sage_side(sg[0][9], bob=-1)
write_cells(os.path.join(HERE, "npc_sage_gen.png"), sg, CELL)

# Schweinler: [idle x2, point x2, laugh x2, BACK x2, SIDE x2]
sw = [[new() for _ in range(10)]]
schweinler(sw[0][0])
schweinler(sw[0][1], bob=-1)
schweinler(sw[0][2], mood="point")
schweinler(sw[0][3], mood="point", bob=-1)
schweinler(sw[0][4], mood="laugh")
schweinler(sw[0][5], mood="laugh", bob=-2)
schweinler_back(sw[0][6])
schweinler_back(sw[0][7], bob=-1)
schweinler_side(sw[0][8])
schweinler_side(sw[0][9], bob=-1)
write_cells(os.path.join(HERE, "npc_schweinler_gen.png"), sw, CELL)

# Kitty: [idle, blink, tinker x2, beam x2, BACK x2, SIDE x2]
kt = [[new() for _ in range(10)]]
kitty(kt[0][0])
kitty(kt[0][1], eyes="blink")
kitty(kt[0][2], pose="tinker")
kitty(kt[0][3], pose="tinker", bob=-1)
kitty(kt[0][4], eyes="happy", pose="cheer", sway=2)
kitty(kt[0][5], eyes="happy", pose="cheer", bob=-1, sway=-2)
kitty_back(kt[0][6])
kitty_back(kt[0][7], bob=-1, sway=1)
kitty_side(kt[0][8])
kitty_side(kt[0][9], bob=-1)
write_cells(os.path.join(HERE, "npc_kitty_gen.png"), kt, CELL)

# villagers: [idle x2, act x2, laugh-emote x2] — 6 cols since 2026-07-17:
# the hall gallery must visibly LAUGH at the naming; on the old 4-col
# sheets play_emote() was a silent no-op (npc.gd only builds clips whose
# columns exist). Sheep + mouse (and badger below) carry BACK cells at
# cols 6-7 since 2026-07-18 — the restaged hall's tiered gallery sits with
# its backs to the camera (npc.gd builds `back` when frame_cols >= 8). The
# owl stays 6 cols: the Dean always faces the house.
vg = [[new() for _ in range(6)]]
owl(vg[0][0])
owl(vg[0][1], bob=-1)
owl(vg[0][2], mood="act")
owl(vg[0][3], mood="act", bob=-1)
owl(vg[0][4], mood="emote")
owl(vg[0][5], mood="emote", bob=-1)
write_cells(os.path.join(HERE, "npc_owl_gen.png"), vg, CELL)

for fname, fn in (("npc_sheep_gen.png", sheep), ("npc_mouse_gen.png", mouse)):
    vg = [[new() for _ in range(8)]]
    fn(vg[0][0])
    fn(vg[0][1], bob=-1)
    fn(vg[0][2], mood="act" if fn is not sheep else "talk")
    fn(vg[0][3], mood="act" if fn is not sheep else "talk", bob=-1)
    fn(vg[0][4], mood="emote")
    fn(vg[0][5], mood="emote", bob=-1)
    fn(vg[0][6], mood="back")
    fn(vg[0][7], mood="back", bob=-1)
    write_cells(os.path.join(HERE, fname), vg, CELL)

# the goose: [idle x2, honk x2, WADDLE x2, FLY x2] — the fest theft is a
# fly-by, so cells 6-7 are the airborne side profile (npc.gd never sees
# them: frame_cols stays 6 there; town_fest.gd appends its own "fly" clip)
gg = [[new() for _ in range(8)]]
goose(gg[0][0])
goose(gg[0][1], bob=-1)
goose(gg[0][2], mood="act")
goose(gg[0][3], mood="act", bob=-1)
goose(gg[0][4], mood="waddle", step=0)
goose(gg[0][5], mood="waddle", step=1)
goose(gg[0][6], mood="fly", step=0)
goose(gg[0][7], mood="fly", step=1)
write_cells(os.path.join(HERE, "npc_goose_gen.png"), gg, CELL)

# Mom: [idle x2, flour-dust act x2, warm emote x2, BACK x2, SIDE x2] + the
# three walk rows (2026-07-29)
mm = [[new() for _ in range(10)]]
mom(mm[0][0])
mom(mm[0][1], bob=-1)
mom(mm[0][2], mood="act")
mom(mm[0][3], mood="act", bob=-1)
mom(mm[0][4], mood="emote")
mom(mm[0][5], mood="emote", bob=-1)
mom_back(mm[0][6])
mom_back(mm[0][7], bob=-1)
mom_side(mm[0][8])
mom_side(mm[0][9], bob=-1)
mm += walk_rows(
    lambda c, i: mom(c, bob=walk_bob[i], liftL=walk_liftl[i], liftR=walk_liftr[i]),
    lambda c, i: mom_back(c, walk_bob[i], walk_liftl[i], walk_liftr[i]),
    lambda c, i: mom_side(c, walk_bob[i], side_fF[i], side_fB[i]))
write_cells(os.path.join(HERE, "npc_mom_gen.png"), mm, CELL)

# Kitty's mother: [idle x2, hands-to-cheeks gasp x2, accusing emote x2]
km = [[new() for _ in range(6)]]
kittymom(km[0][0])
kittymom(km[0][1], bob=-1)
kittymom(km[0][2], mood="act")
kittymom(km[0][3], mood="act", bob=-1)
kittymom(km[0][4], mood="emote")
kittymom(km[0][5], mood="emote", bob=-1)
write_cells(os.path.join(HERE, "npc_kittymom_gen.png"), km, CELL)

# Prologue B cast
# The two THESIS-DAY bystanders grew to the full 10-col + walking contract on
# 2026-07-30. They are the whole cast of the accident set-piece and both of its
# staged moves were theirs — Schweinler crossing to the machine and Ridley
# running to the wreck — and a pose-only sheet can only slide them there.
sa = [[new() for _ in range(10)]]
schweinler_adult(sa[0][0])
schweinler_adult(sa[0][1], bob=-1)
schweinler_adult(sa[0][2], mood="point")
schweinler_adult(sa[0][3], mood="point", bob=-1)
schweinler_adult(sa[0][4], mood="laugh")
schweinler_adult(sa[0][5], mood="laugh", bob=-2)
schweinler_adult_back(sa[0][6])
schweinler_adult_back(sa[0][7], bob=-1)
schweinler_adult_side(sa[0][8])
schweinler_adult_side(sa[0][9], bob=-1)
sa += walk_rows(
    lambda c, i: schweinler_adult(c, bob=walk_bob[i], liftL=walk_liftl[i],
                                  liftR=walk_liftr[i]),
    lambda c, i: schweinler_adult_back(c, walk_bob[i], walk_liftl[i],
                                       walk_liftr[i]),
    lambda c, i: schweinler_adult_side(c, walk_bob[i], side_fF[i], side_fB[i]))
write_cells(os.path.join(HERE, "npc_schweinler_adult_gen.png"), sa, CELL)

bd = [[new() for _ in range(10)]]
badger(bd[0][0])
badger(bd[0][1], bob=-1)
badger(bd[0][2], mood="act")
badger(bd[0][3], mood="act", bob=-1)
badger(bd[0][4], mood="emote")
badger(bd[0][5], mood="emote", bob=-2)
badger(bd[0][6], mood="back")
badger(bd[0][7], mood="back", bob=-1)
badger_side(bd[0][8])
badger_side(bd[0][9], bob=-1)
bd += walk_rows(
    lambda c, i: badger(c, bob=walk_bob[i], liftL=walk_liftl[i],
                        liftR=walk_liftr[i]),
    lambda c, i: badger(c, mood="back", bob=walk_bob[i], liftL=walk_liftl[i],
                        liftR=walk_liftr[i]),
    lambda c, i: badger_side(c, walk_bob[i], side_fF[i], side_fB[i]))
write_cells(os.path.join(HERE, "npc_badger_gen.png"), bd, CELL)

st = [[new() for _ in range(6)]]
stork(st[0][0])
stork(st[0][1], bob=-1)
stork(st[0][2], mood="act")
stork(st[0][3], mood="act", bob=-1)
stork(st[0][4], mood="emote")
stork(st[0][5], mood="emote", bob=-1)
write_cells(os.path.join(HERE, "npc_stork_gen.png"), st, CELL)

kb2 = [[new() for _ in range(6)]]
kitty_bed(kb2[0][0], "rest")
kitty_bed(kb2[0][1], "rest", bob=-1)
kitty_bed(kb2[0][2], "vacant")
kitty_bed(kb2[0][3], "vacant", bob=-1)
kitty_bed(kb2[0][4], "polite")
kitty_bed(kb2[0][5], "polite", bob=-1)
write_cells(os.path.join(HERE, "npc_kitty_bed_gen.png"), kb2, CELL)

# Mom in the sickbed (Prologue A0 "The Fever"): [rest x2, weak-awake act x2,
# warm emote x2] — the kitty_bed rig on the mom palette, scarf tied soft
mb = [[new() for _ in range(6)]]
mom_bed(mb[0][0], "rest")
mom_bed(mb[0][1], "rest", bob=-1)
mom_bed(mb[0][2], "act")
mom_bed(mb[0][3], "act", bob=-1)
mom_bed(mb[0][4], "emote")
mom_bed(mb[0][5], "emote", bob=-1)
write_cells(os.path.join(HERE, "npc_mom_bed_gen.png"), mb, CELL)

# College-age Kitty (the bluff romance + her fountain-rim stall):
# [idle x2, tinker x2, beam x2, BACK x2, SIDE x2] — the back/side pair is
# the bluff's from-behind staging (npc.gd cols 6-9; 6-col spawns unaffected)
ka = [[new() for _ in range(10)]]
kitty_adult(ka[0][0])
kitty_adult(ka[0][1], bob=-1)
kitty_adult(ka[0][2], mood="tinker")
kitty_adult(ka[0][3], mood="tinker", bob=-1)
kitty_adult(ka[0][4], mood="beam")
kitty_adult(ka[0][5], mood="beam", bob=-1)
kitty_adult_back(ka[0][6])
kitty_adult_back(ka[0][7], bob=-1)
kitty_adult_side(ka[0][8])
kitty_adult_side(ka[0][9], bob=-1)
write_cells(os.path.join(HERE, "npc_kitty_adult_gen.png"), ka, CELL)

# Fuji, the librarian (the Ebb night): [idle x2 (the pair doubles as the
# walk), WAND-CAST act x2, STARTLED emote x2, BACK x2, SIDE x2 (left profile
# — play_side(true) faces her east at the counter)] — spawn frame_cols = 10
fj = [[new() for _ in range(10)]]
fuji_npc(fj[0][0])
fuji_npc(fj[0][1], bob=-1, step=1)
fuji_npc(fj[0][2], mood="act")
fuji_npc(fj[0][3], mood="act", bob=-1)
fuji_npc(fj[0][4], mood="emote")
fuji_npc(fj[0][5], mood="emote", bob=-1)
fuji_npc_back(fj[0][6])
fuji_npc_back(fj[0][7], bob=-1)
fuji_npc_side(fj[0][8])
fuji_npc_side(fj[0][9], bob=-1)
write_cells(os.path.join(HERE, "npc_fuji_gen.png"), fj, CELL)

# the Lanternwood Ebb-night trio — all three grew to the full WALKING sheet on
# 2026-07-29 (row 0 the 10-cell pose row, rows 1-3 the walk): Lanternwood is
# where the game rests on solo Fuji, and villagers who slide face-on through a
# night everyone is out in the street read as furniture.
hr = [[new() for _ in range(10)]]
hare(hr[0][0])
hare(hr[0][1], bob=-1)
hare(hr[0][2], mood="act")
hare(hr[0][3], mood="act", bob=-1)
hare(hr[0][4], mood="emote")
hare(hr[0][5], mood="emote", bob=-1)
hare_back(hr[0][6])
hare_back(hr[0][7], bob=-1)
hare_side(hr[0][8])
hare_side(hr[0][9], bob=-1)
hr += walk_rows(
    lambda c, i: hare(c, bob=walk_bob[i], liftL=walk_liftl[i], liftR=walk_liftr[i]),
    lambda c, i: hare_back(c, walk_bob[i], walk_liftl[i], walk_liftr[i]),
    lambda c, i: hare_side(c, walk_bob[i], side_fF[i], side_fB[i]))
write_cells(os.path.join(HERE, "npc_hare_gen.png"), hr, CELL)

bv = [[new() for _ in range(10)]]
beaver(bv[0][0])
beaver(bv[0][1], bob=-1)
beaver(bv[0][2], mood="act")
beaver(bv[0][3], mood="act", bob=-1)
beaver(bv[0][4], mood="emote")
beaver(bv[0][5], mood="emote", bob=-1)
beaver_back(bv[0][6])
beaver_back(bv[0][7], bob=-1)
beaver_side(bv[0][8])
beaver_side(bv[0][9], bob=-1)
bv += walk_rows(
    lambda c, i: beaver(c, bob=walk_bob[i], liftL=walk_liftl[i], liftR=walk_liftr[i]),
    lambda c, i: beaver_back(c, walk_bob[i], walk_liftl[i], walk_liftr[i]),
    lambda c, i: beaver_side(c, walk_bob[i], side_fF[i], side_fB[i]))
write_cells(os.path.join(HERE, "npc_beaver_gen.png"), bv, CELL)

# Pip is a CHILD, so he grew the same cols 6-9 as the Prologue A kids
fk = [[new() for _ in range(10)]]
foxkid(fk[0][0])
foxkid(fk[0][1], bob=-1)
foxkid(fk[0][2], mood="act")
foxkid(fk[0][3], mood="act", bob=-1)
foxkid(fk[0][4], mood="emote")
foxkid(fk[0][5], mood="emote", bob=-1)
foxkid_back(fk[0][6])
foxkid_back(fk[0][7], bob=-1)
foxkid_side(fk[0][8])
foxkid_side(fk[0][9], bob=-1)
fk += walk_rows(
    lambda c, i: foxkid(c, bob=walk_bob[i], liftL=walk_liftl[i],
                        liftR=walk_liftr[i], tail_sway=walk_tail[i]),
    lambda c, i: foxkid_back(c, walk_bob[i], walk_liftl[i], walk_liftr[i],
                             walk_tail[i]),
    lambda c, i: foxkid_side(c, walk_bob[i], side_fF[i], side_fB[i],
                             walk_tail[i]))
write_cells(os.path.join(HERE, "npc_foxkid_gen.png"), fk, CELL)

# MAYOR HOLLIS of Lanternwood, 10 cols: [idle x2, WRITING act x2, the civic
# hoof emote x2, BACK x2 (the rack, unobstructed), SIDE x2]
my = [[new() for _ in range(10)]]
mayor(my[0][0])
mayor(my[0][1], bob=-1)
mayor(my[0][2], mood="act")
mayor(my[0][3], mood="act", bob=-1)
mayor(my[0][4], mood="emote")
mayor(my[0][5], mood="emote", bob=-1)
mayor_back(my[0][6])
mayor_back(my[0][7], bob=-1)
mayor_side(my[0][8])
mayor_side(my[0][9], bob=-1)
my += walk_rows(
    lambda c, i: mayor(c, bob=walk_bob[i], liftL=walk_liftl[i], liftR=walk_liftr[i]),
    lambda c, i: mayor_back(c, walk_bob[i], walk_liftl[i], walk_liftr[i]),
    lambda c, i: mayor_side(c, walk_bob[i], side_fF[i], side_fB[i]))
write_cells(os.path.join(HERE, "npc_mayor_gen.png"), my, CELL)

# the bluff kiss composition: three 96px frames (lean / KISS / the after)
kc = [[Sprite(96, grain=1, salt=13, jitter=0.0) for _ in range(3)]]
kiss_lean(kc[0][0])
kiss_kiss(kc[0][1])
kiss_after(kc[0][2])
write_cells(os.path.join(HERE, "bluff_kiss_gen.png"), kc, 96)

# fx strip — TWO 16-cell rows (256x32). Row 0 is frozen: cells 0-9 Prologue
# A's, 10-15 thesis day's — its bytes must never change (WorldFx callers
# address it by frame index; sheet_sprite infers vframes from the sheet, so
# row-0 indices survive the second row). Row 1: the accident set-piece
# (watch call, impact poof, motion lines) at cells 16+, the bluff kiss heart
# (19), the Ebb-night magic sparks (20 bright / 21 dim trail), and the
# recital's chemistry (22 firework mote / 23 burst / 24 the flask) — only
# APPEND here, NEVER widen a row. Cells 25-31 are FREE.
fx = [[Sprite(16, grain=1, salt=3, jitter=0.0) for _ in range(16)],
      [Sprite(16, grain=1, salt=3, jitter=0.0) for _ in range(16)]]
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
fx_watch(fx[1][0])                  # frame 16
fx_poof(fx[1][1])                   # frame 17
fx_lines(fx[1][2])                  # frame 18
fx_heart(fx[1][3])                  # frame 19 — the bluff kiss
fx_magic_spark(fx[1][4], True)      # frame 20 — the Ebb-night magic mote
fx_magic_spark(fx[1][5], False)     # frame 21 — dim 2px trail flicker
fx_burst(fx[1][6], False)           # frame 22 — firework mote / trail spark
fx_burst(fx[1][7], True)            # frame 23 — the burst ring
fx_beaker(fx[1][8])                 # frame 24 — the recital potion / payload
write_cells(os.path.join(HERE, "prologue_fx.png"), fx, 16)

# the accident set-piece: side-view sheets + the dusk forest-track backdrop
# (5 cols since 2026-07-17: `tumble` is the loop-and-land arc frame —
# accident.tscn's Kitty hframes must stay 5)
ak = [[new() for _ in range(5)]]
kitty_bike(ak[0][0], "pedal0")
kitty_bike(ak[0][1], "pedal1")
kitty_bike(ak[0][2], "brace")
kitty_down(ak[0][3])
kitty_tumble(ak[0][4])
write_cells(os.path.join(HERE, "accident_kitty_gen.png"), ak, CELL)

av = [[new() for _ in range(5)]]
for _i, _pose in enumerate(["drive0", "drive1", "swerve", "skid", "parked"]):
    atv(av[0][_i], _pose)
write_cells(os.path.join(HERE, "accident_atv_gen.png"), av, CELL)

bdn = [[new()]]
bike_down(bdn[0][0])
write_cells(os.path.join(HERE, "accident_bike_down_gen.png"), bdn, CELL)

accident_bg()

print("prologue cast written: kid_basil (6x6) + 19 NPC sheets + fx strip 16x2"
      " + the accident set + the bluff kiss (96px x3)")
