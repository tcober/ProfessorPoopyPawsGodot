#!/usr/bin/env python3
"""Shared base of every TILED scene (interiors AND the overworld).

One module owns what _interior.py's Room and _overworld_tiles.py's OverWorld
would otherwise duplicate: the int-casting canvas, the shared material ramps
(one hardware store for the whole game), map-footprint geometry (bbox/px),
prop placement (place / place_upper / place_split with a baked contact
shadow), the additive glow writer, and finish() — the slice/dedupe/write
plumbing that turns the LOWER + UPPER compositions into one shared atlas,
a TileSet .tres and a layout file (see _tiles.py).

The disciplines this kit enforces (see DESIGN.md "Art pipeline"):
  * repeating art is a pure function of 16-periodic pixel coordinates (or,
    on the overworld, of the cell's neighbor configuration), so recurring
    cells are byte-identical and the slicer collapses them;
  * variety is whole-tile variants hash-placed per cell — never per-pixel
    noise, which makes every tile unique and kills the dedupe;
  * props stay strictly inside their map footprint.

Stdlib-only, deterministic. Used by _interior.py and _overworld_tiles.py.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _core import lerp, Img, ZONE_TILE, h2
from _maps import MapData
from _palette import SCENES, ramp
from _tiles import slice_atlas, pack_tiles, write_atlas, write_tileset_tres, \
    write_layout

T = ZONE_TILE
OUTDIR = os.path.join(HERE, "tilesets")

# ---- shared materials: one house, one hardware store -------------------------------
TIMBER = ramp((146, 94, 62), "violet", 6)     # furniture wood
BRASS = ramp((240, 188, 98), "violet", 4)
# BRASS WITH HONEST DARKS, hand-pinned — the SACKR precedent. `ramp()`'s violet
# shadow law swings a warm seed straight past brown, and on this one it overshoots
# into the paint: BRASS[2] and BRASS[3] resolve to (246,28,26) and (216,0,109), pure
# RED and MAGENTA. Two tones of brass is enough for a hinge or a stud, which is why
# the law in the art-pipeline skill says "brass is 0/1 only" — but anything ROUND
# needs a shading ramp, and the town fountain's alembic finial spent its life as a
# magenta blob on a stone plinth for exactly this reason. Use this for those.
BRASSD = ((242, 223, 167, 255), (240, 188, 98, 255),
          (186, 134, 62, 255), (132, 88, 44, 255))
STEEL = ramp((170, 168, 206), "violet", 4)
COPPER = ramp((198, 112, 72), "violet", 6)
IRON = ramp((104, 100, 124), "violet", 4)
STONER = ramp((144, 138, 170), "violet", 6)   # masonry
GLASS = (216, 226, 240, 255)
MINT = (132, 246, 152, 255)
VIOLETF = (188, 132, 232, 255)
PAPER = (240, 232, 226, 255)
PAPERD = (206, 196, 204, 255)
RED = (226, 62, 92, 255)
SPEC = (255, 255, 250, 255)
WATER = (150, 210, 214, 255)
STEAM = (226, 224, 240, 255)
VOID = (10, 8, 24, 255)
DROP1 = (22, 15, 42, 255)                     # darkness bands past a floor edge
DROP2 = (13, 10, 30, 255)
OUTLINE = (26, 17, 36, 255)                   # prop silhouette edge

# additive night-glow accents (shared by the overworld + town generators)
GLOW_WARM = (255, 200, 120)                   # lamp / window / coal light
GLOW_MINT = (150, 246, 190)                   # gauge / rose-window glow


# ---- the strata rule, as free functions ------------------------------------------------
# THE STRATA RULE LIVES OUT HERE, not only as a TileScene method, for one
# reason: the stratum is declared in the MAP TXT, so the rule can be re-run
# straight off the shipped artifact with no palette entry, no scene key, no
# generator and no atlas. That is what lets _check_art.py enforce it on every
# map in the game — including a HAND-EDIT of a map txt that was never
# regenerated, which is precisely the edit most likely to fuse two storeys.
# TileScene.assert_strata is a thin delegate so there is exactly one copy of it.

def strata_of(m):
    """(x, y) -> stratum, WALKABLE cells only. The one place the "a wall is not
    a storey" convention is spelled out."""
    return {(x, y): m.legend[m.at(x, y)]["stratum"]
            for y in range(m.rows_n) for x in range(m.cols)
            if not m.legend[m.at(x, y)]["solid"]}


def check_strata(m, name, link="link"):
    """The two strata rules over a MapData; raises AssertionError. See
    TileScene.assert_strata for what each one is for and why both are silent
    failures without it."""
    walk = strata_of(m)
    fused = []
    for (x, y), a in sorted(walk.items()):
        for n in ((x + 1, y), (x, y + 1)):             # visit each edge once
            b = walk.get(n)
            if b is None or b == a or link in (a, b):
                continue
            fused.append(f"({x},{y}) {a} | ({n[0]},{n[1]}) {b}")
    assert not fused, (
        f"{name}: THE STRATA FUSED at {len(fused)} edge(s) — two walkable cells "
        f"on different storeys are 4-adjacent and neither is a {link!r}, so the "
        f"upper one is now just a patch of the lower one: "
        + "; ".join(fused[:6]))
    todo = {c for c, s in walk.items() if s == link}
    while todo:
        comp = [todo.pop()]
        i = 0
        while i < len(comp):
            cx, cy = comp[i]
            i += 1
            for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if n in todo:
                    todo.remove(n)
                    comp.append(n)
        joins = {walk[n] for cx, cy in comp
                 for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1))
                 if walk.get(n, link) != link}
        assert len(joins) == 2, (
            f"{name}: the {link!r} at {sorted(comp)[0]} borders "
            f"{sorted(joins) or 'nothing'} — a link must join EXACTLY two strata "
            f"or it is a stair to nowhere")


def sprite_img(sp, w, h):
    """Crop a (square, sparse) prop Sprite to its w x h footprint as an Img —
    the emit_prop() input for props authored on the _propkit canvas."""
    img = Img(w, h)
    img.blit_cell(sp, 0, 0)
    return img


class Canvas(Img):
    """Scene canvas: int-casting put/rect."""

    def put(self, x, y, c):
        super().put(int(x), int(y), c)

    def rect(self, x0, y0, x1, y1, c):
        super().rect(int(x0), int(y0), int(x1), int(y1), c)


class TileScene:
    """One tiled scene: map + canvases + palette + placement + plumbing.

    A driver subclass (Room, OverWorld) adds its terrain painters; the
    generator config constructs it, paints terrain, places props from map
    feature bboxes, then finish()es. Everything positional derives from the
    map file — move a feature char and the scene follows.
    """

    def __init__(self, map_name, scene_key, fill=VOID):
        self.name = map_name
        self.m = MapData(os.path.join(HERE, "maps", map_name + ".txt"))
        self.W, self.H = self.m.cols * T, self.m.rows_n * T
        self.bg = Canvas(self.W, self.H, fill)
        self.ov = Canvas(self.W, self.H)
        self._props = []               # Tier-3 manifest rows (emit_prop)
        sc = SCENES[scene_key]
        self.scene = sc
        self.shadow = sc["shadow"]
        self.ACCENT = sc["accent"]
        self.mats = dict(sc.get("mats", {}))

    def mat(self, name, tones=6, spread=1.0, shadow=None):
        """Material ramp: the scene's hand ramp if it has one, else derived
        from the seed color."""
        hand = self.scene.get("ramps", {}).get(name)
        if hand:
            return list(hand)      # copy: callers must not mutate the registry
        return ramp(self.mats[name], shadow or self.shadow, tones, spread)

    # -- geometry ---------------------------------------------------------------------
    def bbox(self, chars):
        cs = [(x, y) for y in range(self.m.rows_n) for x in range(self.m.cols)
              if self.m.at(x, y) in chars]
        assert cs, f"no {chars!r} cells in {self.name}.txt"
        xs, ys = [c[0] for c in cs], [c[1] for c in cs]
        return (min(xs), min(ys), max(xs), max(ys))

    def px(self, bbox):
        """(X, Y, W, H) pixel rect of a tile bbox."""
        return (bbox[0] * T, bbox[1] * T,
                (bbox[2] - bbox[0] + 1) * T, (bbox[3] - bbox[1] + 1) * T)

    def comps(self, chars):
        """4-connected components of the chars' cells, each as a cell list
        (the place_each / emit_prop each=True idiom)."""
        m = self.m
        todo = {(x, y) for y in range(m.rows_n) for x in range(m.cols)
                if m.at(x, y) in chars}
        assert todo, f"no {chars!r} cells in {self.name}.txt"
        out = []
        while todo:
            comp = [todo.pop()]
            i = 0
            while i < len(comp):
                cx, cy = comp[i]
                i += 1
                for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if n in todo:
                        todo.remove(n)
                        comp.append(n)
            out.append(comp)
        return out

    def comp_bbox(self, comp):
        xs, ys = [c[0] for c in comp], [c[1] for c in comp]
        return (min(xs), min(ys), max(xs), max(ys))

    # -- prop placement -----------------------------------------------------------------
    def bake_shadow(self, chars, shadow_h, each=False):
        """Contact-shadow band across a footprint's bottom rows: darken the
        already-painted ground toward the scene's dark, whatever fabric is
        under it. (Room overrides this with its repaint-the-fabric version,
        which the interiors' whole-tile light dispatch depends on.)
        `each`: one band per connected component — a shared-char prop set
        (the hall's four benches) must NOT shade the combined bbox, which
        smears the band across the open cells between them."""
        boxes = [self.comp_bbox(c) for c in self.comps(chars)] if each \
                else [self.bbox(chars)]
        for box in boxes:
            X, Y, XW, YH = self.px(box)
            for y in range(Y + YH - shadow_h, Y + YH):
                for x in range(X + 1, X + XW - 1):
                    base = self.bg.get(x, y)
                    self.bg.put(x, y, lerp(base[:3], VOID[:3], 0.35) + (255,))

    # -- the TERRACE KIT (2026-07-28) ----------------------------------------------------
    # Verticality in this engine is AUTHORING, not a system: a terrace is two
    # flat walkable regions of the map separated by a band of solid cells
    # carrying opaque hand-drawn face art, pierced by a walkable stair gap.
    # Alembic's Academy terrace proved it; these three lift the idiom out of
    # that one generator so every zone can stack levels. (The travel overworld
    # is chibi and stays flat — see CHIBI_MAPS in _check_art.py.)

    def _col_runs(self, chars):
        """Every maximal VERTICAL run of `chars`, as (tx, top_ty, height)."""
        out = []
        for tx in range(self.m.cols):
            ty = 0
            while ty < self.m.rows_n:
                if self.m.at(tx, ty) in chars:
                    h = 0
                    while self.m.at(tx, ty + h) in chars:
                        h += 1
                    out.append((tx, ty, h))
                    ty += h
                else:
                    ty += 1
        return out

    def stamp_columns(self, chars, sprites, salt=51, run=2, ret=None):
        """Stamp one opaque face column per vertical run of `chars`, hash-picked
        from `sprites` — the cliff/chasm band. Blits straight onto the LOWER
        canvas over whatever fabric paint_terrain already put there, because a
        face is fully opaque and un-outlined: it dedupes no matter what the
        underlay's 32-phase is doing beneath it, and a per-column outline would
        print a seam every 16px.

        `ret` is an optional (west_cap, west_foot, east_cap, east_foot) set of
        town_cliff_return strips,
        blitted over the exposed side of every staircase STEP — see the note at
        the step loop below, and town_cliff_return for why a stepped band needs
        a corner to read as one wall.

        The `run` assert is the whole reason this is a shared primitive. The art
        is T*run tall and lands on the run's TOP cell, so an off-by-one run is a
        silent, ugly bug in BOTH directions and only one of them lints:
          - too TALL  -> the extra cells keep raw ground fabric, which trips the
                         invisible-wall lint (solid cell, walkable token).
          - too SHORT -> the art spills onto the WALKABLE cell below and the
                         player walks through a painted rock wall. NOTHING in
                         _check_art.py catches that. Hence the assert."""
        tops = {}                          # tx -> the run tops in that column
        for tx, ty, h in self._col_runs(chars):
            assert h == run, (
                f"{self.name}.txt: {chars!r} run at ({tx},{ty}) is {h} cells "
                f"tall, want exactly {run} — the face art is {T * run}px and "
                f"lands on the run's top cell")
            self.bg.blit_cell(sprites[h2(tx, ty, salt) % len(sprites)],
                              tx * T, ty * T)
            tops.setdefault(tx, []).append(ty)
        if ret is None:
            return
        # THE STEPS. Where a run's neighbour in the same band starts a row
        # LOWER, this column's face carries on past it and its side is exposed
        # to open ground — a straight vertical cut that reads as two unrelated
        # walls rather than one that steps down. Blit the return over that side.
        #
        # Matched on `ty + 1 in neighbour` rather than on the neighbour's
        # height, because ONE CHAR SERVES SEVERAL BANDS — Lanternwood spends
        # `C` on both the level-4 band and the gate band twenty rows away, and
        # comparing their tops finds an eighteen-row "step" that is really two
        # unrelated walls. A step is a neighbouring run exactly one row lower,
        # and no run of its own at this row.
        # A step exposes TWO legs and needs a band on both, or the corner is
        # only half closed: the HIGHER run's top row (the neighbour starts one
        # row lower) and the LOWER run's bottom row (the neighbour starts one
        # row higher, so its face ends a row short of this one's).
        w_cap, w_foot, e_cap, e_foot = ret
        for tx, tys in tops.items():
            for ty in tys:
                for dx, cap, foot in ((-1, w_cap, w_foot), (1, e_cap, e_foot)):
                    nb = tops.get(tx + dx, ())
                    if ty in nb:
                        continue                   # level: nothing exposed
                    if ty + 1 in nb:
                        self.bg.blit_cell(cap, tx * T, ty * T)
                        self._end_shade(tx, ty, dx)
                    elif ty - 1 in nb:
                        self.bg.blit_cell(foot, tx * T, (ty + run - 1) * T)
                        self._end_shade(tx, ty + run - 1, dx)

    def _shadeable(self, tx, ty):
        """May a contact shadow be painted onto this cell?

        NO for an ANIMATED cell, and the reason is the same one that gives the
        stream bridge its hand-drawn `bridge_fascia` instead of a mirrored mask
        band: sea, river and lava cells are repainted per frame from the finished
        canvas, and a shadow baked into frame 0 would survive in frame 0 alone —
        so the cell strobes. The driver catches it (`_lower_frames` asserts frame
        0 reproduces the still canvas byte for byte) but only at finish() time,
        with a message about purity that says nothing about which band did it.

        A base scene has nothing animated, so this defaults to yes; the OverWorld
        driver overrides it, because knowing which render class a cell is IS the
        driver's job and TileScene deliberately has no idea."""
        return True

    def _end_shade(self, tx, ty, dx, cols=3):
        """The shadow a wall END throws sideways onto the open ground beside it.

        From the terrace above, a step's exposed corner is the one place the
        wall's cap sits at the WALKER'S OWN feet level, so the eye follows the
        cap line straight past it and reads more ground — you walk into a wall
        that is not there to look at. A cast shadow is the cue that fixes it:
        nothing else in a flat top-down view says "something tall stands here"
        as cheaply. The band's own foot_shade only shades SOUTH, which is no
        help at a corner."""
        for i, a in enumerate((0.34, 0.20, 0.10)[:cols]):
            sx = tx * T - 1 - i if dx < 0 else (tx + 1) * T + i
            gx = sx // T
            ch = self.m.at(gx, ty)
            if ch is None or self.m.legend[ch]["solid"]:
                break                          # shading a wall, not the ground
            if not self._shadeable(gx, ty):
                break                          # ...or animated water (see above)
            for y in range(ty * T, ty * T + T):
                base = self.bg.get(sx, y)
                self.bg.put(sx, y, lerp(base[:3], VOID[:3], a) + (255,))

    def foot_shade(self, chars, rows=3):
        """Contact shadow on the ground at the FOOT of each stamped column run.

        Not bake_shadow: that works off a map-wide bbox, so a band spanning the
        map would smear its own bottom rows. And not _ground_overlays either —
        the driver's struct band excludes `snow` (so the overworld's ice land
        doesn't get shadow-crusted), which is exactly the class Lanternwood's
        terraces sit on, so without this every cliff floats."""
        fall = [(i, 0.32 - 0.11 * i) for i in range(rows)]
        for tx, ty, h in self._col_runs(chars):
            by = ty + h                                    # the cell below
            if self.m.at(tx, by) is None or self.m.at(tx, by) in chars:
                continue
            if not self._shadeable(tx, by):
                continue
            for dy, a in fall:
                for x in range(tx * T, tx * T + T):
                    base = self.bg.get(x, by * T + dy)
                    self.bg.put(x, by * T + dy,
                                lerp(base[:3], VOID[:3], a) + (255,))

    def mask_band(self, chars, band=12, run_min=2):
        """The TOP `band` px of every `chars` column run, re-emitted as a Tier-3
        Y-SORTED strip. This is the fix for "the player hangs off the edge of
        the cliff".

        THE ARITHMETIC, because the magic number 12 is not arbitrary. A body's
        CollisionShape2D hugs its FEET (12x8 centred at +6, so the box bottom is
        origin+10) while the ~22x38 figure's last row draws at origin+21.
        Pressed SOUTH into a solid cell, the box stops at the cell's top edge
        and ELEVEN px of sprite hangs past the physics boundary, over the face
        below. Re-drawing that face's own top 12px over the body swallows
        exactly that sliver — same paint, same coordinates, so it can never
        seam.

        IT USED TO BE UPPER-LAYER TILES, AND THAT WAS A BUG (2026-07-29). The
        upper layer draws over every body UNCONDITIONALLY, and the strip a body
        overhangs from the NORTH is the same strip a body JUMPING from the
        terrace below rises into: at rest a lower head tops out 2px under the
        band, and the hop lifts it 26. So hopping anywhere within ~1.5 tiles of
        a cliff sliced the top off your head. No band height fixes that — the
        two sprites want opposite answers from the same pixels — which is the
        whole reason the doctrine says depth belongs to Y-SORT and not to the
        static layers.

        THE KEY IS `run_top - 8`, and every one of those pixels is argued for.
        Three kinds of body meet a run's top row and they want three answers:

          - ON TOP, pressed south. Its box bottom stops at the run's top edge,
            so its origin is EXACTLY run_top-10 and no closer. Wants masking —
            this is the case the whole band exists for.
          - IN THE NOTCH beside the run. Every band staircases, so at each step
            the neighbouring column's ground runs one row FURTHER SOUTH and a
            body can stand level with the wall, at origin run_top-10..run_top+6.
            Wants NO masking: it is beside the drop, not on top of it, and
            masking it clips the character's FACE against the wall by its head.
          - ON THE TERRACE BELOW, hopping. Origin run_top+30 or more. Wants no
            masking (see above).

        run_top-8 is the only 2px of daylight between the first and the second,
        and it exists at all only because the on-top body cannot press past
        run_top-10. Anything keyed lower re-clips the overhang; anything keyed
        higher — the original run_top+band — clips a face at every corner.

        Legal only on a run >= `run_min` cells, and only with band <= 14. Runs
        whose north neighbour is itself solid are skipped: nobody can press
        them. Consecutive columns sharing a top row are emitted as ONE strip, so
        a staircased band costs a handful of sprites rather than one per column.

        CALL LAST — after stamp_columns / foot_shade / place / bake_shadow and
        before finish() — because the strip copies the FINISHED lower art."""
        m = self.m
        keep = []
        tops = {}
        for tx, ty, h in self._col_runs(chars):
            assert h >= run_min, (
                f"{self.name}.txt: {chars!r} run at ({tx},{ty}) is {h} cells "
                f"tall, want >= {run_min} — a south-pressed head reaches 18px "
                f"above a run's south edge and a 1-row band would eat it")
            assert band <= 14, f"{self.name}: mask band {band} > 14"
            north = m.at(tx, ty - 1)
            if north is None or m.legend[north]["solid"]:
                continue                           # nobody can press this run
            keep.append((ty, tx))
        for tx, ty, _h in self._col_runs(chars):
            tops.setdefault(tx, []).append(ty)
        segs = []                                  # (ty, tx0, cols)
        for ty, tx in sorted(keep):
            if segs and segs[-1][0] == ty and segs[-1][1] + segs[-1][2] == tx:
                segs[-1][2] += 1
            else:
                segs.append([ty, tx, 1])
        # A STRIP MUST OVERHANG ITS RUN BY A COLUMN wherever the neighbouring
        # run sits one row HIGHER. A body in the notch beside such a step stands
        # at the very edge of its own column, and the figure is 22px wide — a
        # third of it hangs into the next column, where this run's strip does
        # not reach and the neighbour's strip is 16px too high to help. The foot
        # and the coat-tail poke out over the wall, which is the exact artefact
        # the band exists to prevent, just moved sideways. The extra column
        # copies the FINISHED art at those coordinates, so it lands on the
        # neighbour's own face, same paint, same coords, no seam.
        for seg in segs:
            ty, tx, n = seg
            if ty - 1 in tops.get(tx - 1, ()):
                seg[1] -= 1
                seg[2] += 1
            if ty - 1 in tops.get(tx + n, ()):
                seg[2] += 1
        for i, (ty, tx, n) in enumerate(segs):
            img = Img(n * T, band)
            for y in range(band):
                for x in range(n * T):
                    img.put(x, y, self.bg.get(tx * T + x, ty * T + y))
            fname = f"{self.name}_mask{chars}{i}.png"
            img.save(os.path.join(OUTDIR, fname))
            self._props.append("mask %s %d %d %d"
                               % (fname, tx * T, ty * T, ty * T - 8))

    def upper_cell(self, tx, ty, sprite):
        """Blit one sprite onto the UPPER canvas at a single cell. The `chars`
        based place_upper() takes a whole feature bbox, which is no use when the
        target is one specific cell of a long run (a bridge's near rail sits on
        exactly one river cell, and the river's bbox is the whole stream)."""
        self.ov.blit_cell(sprite, tx * T, ty * T)

    def assert_reachable(self, *from_anchors, full=True):
        """BFS the walkable graph from every named anchor (default the single
        `player_start`); assert every anchor, every door cell and — with
        `full` — EVERY WALKABLE CELL OF EVERY STRATUM is reached.
        _check_art.py lints a great deal but NOT connectivity, so before
        terraces a stranded region was impossible and after them it is one
        mistyped band cell away — a town that ships, renders, lints clean, and
        cannot be walked.

        `full` is the strata half of that, and it catches the two failures the
        anchors-and-doors sweep structurally cannot. An anchor sweep only proves
        the places something was PLACED are reachable, so a stacked map's
        stranded platform — a canopy landing whose only ladder was mistyped, an
        orphaned pocket of forest floor walled in by fascia — passes silently
        precisely because nothing stands on it yet. That platform then ships,
        and the first thing to go on it is unreachable months later with no clue
        as to when it broke. All three shipped zone maps already satisfy it (the
        town, town_fest and Lanternwood each reach 100% of their walkable cells
        from `player_start`), which is what makes it safe as the default.

        Several starts, because on a stacked map a storey may legitimately be
        entered from ONE fixed place and nothing says that place is
        `player_start`. Pass every anchor a body can arrive on.

        `full=False` is for a map whose unreachable-on-foot ground is the point:
        the five-lands OVERWORLD is ocean-separated, so 1709 of its 2289
        walkable cells are correctly unreachable from the landing. (It does not
        call this at all today; the knob exists so it could.)"""
        names = from_anchors or ("player_start",)
        seen, todo = set(), []
        for name in names:
            start = self.m.anchors.get(name)
            assert start, f"{self.name}.txt: no anchor {name!r} to walk from"
            if tuple(start) not in seen:
                seen.add(tuple(start))
                todo.append(tuple(start))
        solid = self.m.solid_cells()
        while todo:
            cx, cy = todo.pop()
            for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if n in seen or self.m.at(*n) is None or n in solid:
                    continue
                seen.add(n)
                todo.append(n)
        want = {name: tuple(a) for name, a in self.m.anchors.items()}
        for x in range(self.m.cols):
            for y in range(self.m.rows_n):
                if self.m.legend[self.m.at(x, y)]["terrain"] == "door":
                    want[f"door@{x},{y}"] = (x, y)
        bad = sorted(k for k, c in want.items() if c not in seen)
        assert not bad, (
            f"{self.name}.txt: unreachable from {'+'.join(names)} -> "
            + ", ".join(f"{k}{want[k]}" for k in bad))
        if not full:
            return
        stranded = {}                          # stratum -> its stranded cells
        for y in range(self.m.rows_n):
            for x in range(self.m.cols):
                if (x, y) in solid or (x, y) in seen:
                    continue
                stranded.setdefault(self.m.stratum(x, y), []).append((x, y))
        assert not stranded, (
            f"{self.name}.txt: walkable ground unreachable from "
            f"{'+'.join(names)} — " + "; ".join(
                f"{len(cs)} {st!r} cell(s) from {sorted(cs)[0]}"
                for st, cs in sorted(stranded.items())))

    # -- THE STRATA KIT (2026-07-29) ------------------------------------------------------
    # A town with FOUR walkable storeys in one 72x48 grid — a forest floor, the low
    # boardwalk, the homes in the crowns, the Academy's stone terrace — needs no
    # elevation feature, for the same reason the terrace kit above needs none. It needs the
    # storeys to be DISJOINT IN THE GRID, because a cell is exactly one (x, y)
    # with one walk/solid bit: disjoint, and two storeys are unambiguous and "a
    # bridge over walkable ground" is unrepresentable rather than merely
    # discouraged. The `stratum:` legend token (assets/_maps.py) declares which
    # storey a char belongs to, and the asserts below are the whole system.
    #
    # THEY ARE THE SYSTEM BECAUSE EVERY FAILURE HERE IS SILENT. Fuse the canopy
    # to the floor with one mistyped cell and the boardwalk stops being a storey
    # and becomes a wooden patch of forest: it renders, it dedupes, every lint in
    # _check_art.py passes it, and it ships. Nothing else in this pipeline is
    # even looking — the invisible-wall lint reads tiles, the z-order lints read
    # the upper layer, and assert_reachable is HAPPIER with a fused canopy than
    # with a correct one.

    def assert_strata(self, link="link"):
        """THE ONE THAT MATTERS. Two rules over the walkable graph:

          1. THE STRATA MUST NOT FUSE. No two 4-adjacent walkable cells may
             declare different strata, unless one of them is a `link` — the rope
             ladder or the dinghy lift, the single char whose whole job is to
             touch two storeys at once. This is the rule the disjointness
             argument rests on, and violating it is the failure described in the
             section note above.
          2. NO STAIR TO NOWHERE. Every connected component of `link` cells must
             border walkable cells in EXACTLY TWO distinct non-link strata. ONE
             means a ladder that climbs to nothing — and worse, a hole punched
             through rule 1 in exchange for nothing. THREE means a junction
             where which storey a step leads to depends on the direction you
             leave it, which is not a thing a player can be taught.

        Strata default to `ground`, so a single-storey map satisfies both rules
        trivially and this is free to call on every map in the game.

        The body is the module-level check_strata() so _check_art.py can re-run
        the identical rule off a shipped map txt without building a scene."""
        check_strata(self.m, self.name + ".txt", link)

    def assert_band_orientation(self, band_chars, above, below):
        """Every `band_chars` face run must carry `above`-stratum walkable
        ground on its NORTH edge, and never on its south.

        A fascia is drawn to be seen from in front and from above: the opaque
        art lands on the run's TOP cell, the coping runs along its crest,
        `foot_shade` darkens the ground at its foot. Flip the band north for
        south and every one of those lands on the wrong side of it — and it
        renders perfectly, because no part of the paint path knows which way is
        up. Bury the same run one row INSIDE the canopy and it renders perfectly
        too, as a wall standing on the boardwalk with more boardwalk behind it.

        Both are one keystroke from correct and neither leaves a mark any other
        lint can see, which is the argument for checking the thing you actually
        meant: a fascia IS THE SOUTH EDGE OF A STOREY, and that sentence is
        testable."""
        m = self.m
        bad = []
        for tx, ty, h in self._col_runs(band_chars):
            n, s = m.stratum(tx, ty - 1), m.stratum(tx, ty + h)
            if n != above:
                bad.append(f"({tx},{ty}) north is {n or 'solid'}, want "
                           f"walkable {above!r} — the band is upside down")
            elif s == above:
                bad.append(f"({tx},{ty}) south is {above!r} as well — the band "
                           f"is buried inside its own storey")
            elif s is not None and s != below:
                bad.append(f"({tx},{ty}) south is {s!r}, want solid or {below!r}")
        assert not bad, (
            f"{self.name}.txt: {band_chars!r} band mis-oriented: "
            + "; ".join(bad[:6]))

    def assert_span(self, deck_chars="W", fascia="e", water="r"):
        """THE SPAN LAW. A span — a plank bridge from one platform to another
        across open air — is a run of walkable `deck_chars` cells and it is
        legal only when all three hold, per column:

          1. ITS SOUTH BOUNDARY IS A SOLID RUN OF >= 2 ROWS whose top row is a
             `fascia` char — or a single `water` cell, which is the shipped
             exception: Alembic's stream bridge takes a hand-drawn
             bridge_fascia() on the river cell south of the deck INSTEAD of a
             mirrored mask band, because river cells animate on 4 frames and a
             mirrored band would freeze half of every one of them.
          2. ITS NORTH BOUNDARY IS SOLID, or walkable on the span's own stratum
             (the platform it runs back onto).
          3. NO SPAN CELL IS 4-ADJACENT TO A WALKABLE CELL OF ANOTHER STRATUM.

        THE `>= 2` IN RULE 1 IS NOT AESTHETIC. DESIGN.md's z-order doctrine, in
        the mask-band paragraph: "NEVER band a 1-row-deep solid strip between
        two walkable rows — the corridor feet and the south head need the same
        12px and one of them always wears it (this killed the town-tree
        corridor)". A span's fascia is exactly that band. One row of solid
        between the deck above and whatever is walkable below, and there is no
        assignment of those twelve pixels that serves both bodies; two rows and
        the south head cannot reach the band at all.

        Rule 3 duplicates assert_strata, deliberately. assert_strata will indeed
        catch the same cell, and it will report it as an adjacency between two
        stratum names — true, and useless when you are staring at a bridge. This
        one says your bridge touches the forest floor, which is the sentence
        that tells you what to do. `link` is exempt from it for the same reason
        it is exempt there: a rope ladder is HOW you get onto a span."""
        m = self.m
        walk = strata_of(m)
        cells = [c for c, s in walk.items() if m.at(*c) in deck_chars]
        assert cells, f"no {deck_chars!r} span cells in {self.name}.txt"
        mine = {walk[c] for c in cells}
        assert len(mine) == 1, (
            f"{self.name}.txt: the {deck_chars!r} span spans strata {sorted(mine)} "
            f"— one span is one storey")
        mine = mine.pop()
        for tx, ty, h in self._col_runs(deck_chars):
            # (1) the south boundary
            sy = ty + h
            sch = m.at(tx, sy)
            if sch is not None and sch in water:
                pass                              # the bridge_fascia exception
            else:
                assert sch is not None and m.legend[sch]["solid"], (
                    f"{self.name}.txt: the span at ({tx},{ty}) has no fascia "
                    f"below it — ({tx},{sy}) is walkable, so the deck's south "
                    f"edge is open air with nothing drawn in it")
                assert sch in fascia, (
                    f"{self.name}.txt: the span at ({tx},{ty}) sits on {sch!r} "
                    f"at ({tx},{sy}), not a {fascia!r} fascia — a span's south "
                    f"row is the only face of it the player ever sees")
                depth = 0
                while (m.at(tx, sy + depth) is not None
                       and m.legend[m.at(tx, sy + depth)]["solid"]):
                    depth += 1
                assert depth >= 2, (
                    f"{self.name}.txt: the span at ({tx},{ty}) has a "
                    f"{depth}-row solid strip below it, want >= 2 — a 1-row "
                    f"band between two walkable rows is forbidden outright by "
                    f"the z-order doctrine (the corridor feet and the south "
                    f"head want the same 12px and one of them always wears it)")
            # (2) the north boundary
            nch = m.at(tx, ty - 1)
            assert nch is None or m.legend[nch]["solid"] \
                or m.stratum(tx, ty - 1) == mine, (
                f"{self.name}.txt: the span at ({tx},{ty}) runs north onto "
                f"{m.stratum(tx, ty - 1)!r} — a span lands on its own storey "
                f"or on solid, never on the ground below it")
        # (3) the one that gets its own sentence
        touch = []
        for (x, y) in sorted(cells):
            for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                s = walk.get(n)
                if s is not None and s not in (mine, "link"):
                    touch.append(f"({x},{y}) touches {s} at ({n[0]},{n[1]})")
        assert not touch, (
            f"{self.name}.txt: YOUR BRIDGE TOUCHES THE FOREST FLOOR — a span "
            f"cell is 4-adjacent to walkable ground on another storey, so the "
            f"player walks off the bridge onto the level below it: "
            + "; ".join(touch[:6]))

    def assert_stair(self, stair_char, band_char, cells):
        """Every `stair_char` flight is 2 cells wide, spans ALL `cells` rows of
        the `band_char` run it pierces, and has walkable ground directly north
        AND directly south of both its columns.

        Lanternwood documents every clause of this in prose in its map header,
        which is exactly as much protection as prose has ever given anything.
        Each clause is a failure that looks completely finished:
          * a flight one row SHORT of its band leaves a solid cell across the
            top of the stairs — a staircase you cannot use, under face art that
            looks entirely normal;
          * one row LONG spills the stair art out onto the terrace;
          * 1 cell wide is a flight a 22px-wide figure cannot enter squarely;
          * no landing north or south is only assert_reachable's problem when
            the storey beyond has no OTHER way in, and on a stacked map it
            usually does — so reachability shrugs and this fails loudly.

        The band run is matched by VERTICAL OVERLAP with the flight, never by
        column alone, for the reason stamp_columns gives: ONE CHAR SERVES
        SEVERAL BANDS (Lanternwood spends `C` on the level-4 band and the gate
        band twenty rows apart), and a per-column match would compare a flight
        against an unrelated wall."""
        for comp in self.comps(stair_char):
            x0, y0, x1, y1 = self.comp_bbox(comp)
            assert (x1 - x0, y1 - y0, len(comp)) == (1, cells - 1, 2 * cells), (
                f"{self.name}.txt: the {stair_char!r} flight at ({x0},{y0}) is "
                f"{x1 - x0 + 1}x{y1 - y0 + 1} ({len(comp)} cells), want a solid "
                f"2x{cells} block")
            runs = [(ty, h) for tx, ty, h in self._col_runs(band_char)
                    if tx in (x0 - 1, x1 + 1) and ty <= y1 and ty + h - 1 >= y0]
            assert runs, (
                f"{self.name}.txt: the {stair_char!r} flight at ({x0},{y0}) has "
                f"no {band_char!r} band beside it to pierce")
            bad = [r for r in runs if r != (y0, cells)]
            assert not bad, (
                f"{self.name}.txt: the {stair_char!r} flight at ({x0},{y0}) "
                f"spans rows {y0}..{y1} but the {band_char!r} band beside it "
                f"runs top={bad[0][0]} height={bad[0][1]} — a flight must span "
                f"ALL of its band's rows or it is a staircase into a wall")
            for cx in (x0, x1):
                for cy, side in ((y0 - 1, "north"), (y1 + 1, "south")):
                    ch = self.m.at(cx, cy)
                    assert ch is not None and not self.m.legend[ch]["solid"], (
                        f"{self.name}.txt: the {stair_char!r} flight at "
                        f"({x0},{y0}) has no landing to the {side} — "
                        f"({cx},{cy}) is {'off-map' if ch is None else 'solid'}")

    def assert_door_approach(self, rows=2, exempt=()):
        """Every `door`-terrain cell needs `rows` walkable cells DUE SOUTH of
        it, on the door's OWN stratum.

        Every door in this engine is approached from the south: the art is a
        south-facing arch, the door-mouth arrival convention puts the body in
        the mouth facing north, and several cutscenes walk to a door by adding a
        raw pixel offset to its anchor — `home + (0,26)`, `home + (0,38)`,
        `cottage_e + (4,14)`. Two clear rows is what all of those need, and a
        prop parked in the second one breaks them with no lint and no error: the
        walk simply ends early against the side of a market stall and the scene
        waits forever for a gate that will not fire.

        `on its own stratum` is the treehouse clause. A door in a canopy wall
        whose two clear rows are the forest floor two storeys down is not an
        approach, it is a drop.

        OPT-IN, because it is NOT free on the shipped maps and adopting it is
        per-map work: every interior room puts its exit door IN the south wall,
        so the wall itself is row +1 there and `rows` must be 0; and Alembic
        parks the market stall two cells south of the weapon shop's door and a
        tree two south of cottage_w's. `exempt` takes those cells while a map is
        being brought up to the rule."""
        m = self.m
        bad = []
        for y in range(m.rows_n):
            for x in range(m.cols):
                if m.legend[m.at(x, y)]["terrain"] != "door" or (x, y) in exempt:
                    continue
                mine = m.stratum(x, y)
                for d in range(1, rows + 1):
                    s = m.stratum(x, y + d)
                    if s == mine:
                        continue
                    bad.append(f"({x},{y}) blocked at ({x},{y + d})"
                               + (f" — {s!r}, not the door's {mine!r}"
                                  if s else " — solid"))
                    break
        assert not bad, (
            f"{self.name}.txt: door approaches blocked. Every door is entered "
            f"from the south and wants {rows} clear rows below it: "
            + "; ".join(bad[:6]))

    def assert_lift(self, head, shaft, drum_walk, drum_solid,
                    down="lift_down", up="lift_up", clear=2, canopy="canopy"):
        """THE ONE MACHINE. A scripted rope hoist joining the canopy to the floor
        in ONE 3-cell column: a walkable top landing (`head`), a SOLID shaft
        (`shaft`) carved out of the fascia band, and a crank drum at the bottom
        whose top row is the walkable plaza landing (`drum_walk`) over its solid
        works (`drum_solid`).

        THE SHAFT IS SOLID, AND THAT IS THE DESIGN. A cosmetic lift that is
        mechanically just another link needs a WALKABLE shaft — a hole punched
        through the fascia — and then you must answer what the floor of those
        cells is. There are no treads and there is no ground. The honest answer
        is nothing, and the player walks up a wall with a boat overhead: the
        chasm failure verbatim, because authoring an ABSENCE is the one thing
        this format is bad at. The mechanism IS the motion; there is nothing to
        draw in its place. So the two landings are walkable on their own strata,
        separated by a solid curtain, with ZERO adjacency between strata — which
        means assert_strata is satisfied with no link at all, and THE LIFT IS THE
        ONE PLACE THE TWO STOREYS ARE JOINED BY CODE RATHER THAN BY AUTHORING.
        That is the same thing a door is: a scripted crossing of a wall. It is
        right that the town's one machine is the one thing that isn't authoring.

        Seven clauses, and clause 6 is the one that earns its keep:

          1. all three pieces share one 3-cell column, north to south, contiguous;
          2. `head` walkable canopy, `shaft` solid and exactly the band's run
             rows, `drum_walk` walkable ground, `drum_solid` the bottom row only;
          3. >= 1 walkable cell EAST OR WEST of the drum's solid row, so a body
             can reach the crank — the lift is the only reason that landing
             exists and a landing you cannot stand beside is furniture;
          4. the cell due north of `head` is solid bough or trunk: the beam is
             lashed to SOMETHING. Hanging in bare sky reads as a mistake;
          5. the landing anchors are `clear` cells away from every other anchor,
             because two Area2Ds on one anchor is a documented softlock in this
             codebase (2026-07-18) and a lift is exactly where it would happen;
          6. THE HEAD LANDING IS REACHABLE WITH THE SHAFT TREATED AS IMPASSABLE.
             The no-softlock proof, at build time instead of by hope: if the only
             way onto the canopy were the ride itself, a player who rode up and
             then reloaded — or a scene that never wires the zones, which is
             every era but the present — is stranded up a tree;
          7. the car sheet's frame count is whole (checked by the caller).

        `canopy` names the stratum the head landing stands on. It is a PARAMETER
        and no longer the literal it used to be, because a town can have more than
        one canopy: the rebuilt Alembic has `canopy_hi` and `canopy_lo`, the lift
        serves the lower one, and a hardcoded "canopy" made clause 2 a check that
        could only ever fail."""
        m = self.m
        cols = None
        pieces = [("head", head), ("shaft", shaft),
                  ("drum crown", drum_walk), ("drum works", drum_solid)]
        rows = {}
        for label, ch in pieces:
            cs = [(x, y) for y in range(m.rows_n) for x in range(m.cols)
                  if m.at(x, y) == ch]
            assert cs, f"{self.name}.txt: no {ch!r} cells for the lift's {label}"
            xs = sorted({x for x, _ in cs})
            ys = sorted({y for _, y in cs})
            assert len(xs) == 3 and xs[2] - xs[0] == 2, (
                f"{self.name}.txt: the lift's {label} ({ch!r}) spans columns "
                f"{xs}, want exactly 3 contiguous")
            assert cols is None or xs == cols, (
                f"{self.name}.txt: the lift's {label} ({ch!r}) is in columns "
                f"{xs} but the pieces above it are in {cols} — the head, the car "
                f"and the drum share ONE column or the rope misses the boat")
            cols = xs
            assert len(cs) == 3 * len(ys) and ys[-1] - ys[0] == len(ys) - 1, (
                f"{self.name}.txt: the lift's {label} ({ch!r}) is not a clean "
                f"3 x {len(ys)} block")
            rows[label] = ys
        # (1) north to south, contiguous
        order = ["head", "shaft", "drum crown", "drum works"]
        for a, b in zip(order, order[1:]):
            assert rows[a][-1] + 1 == rows[b][0], (
                f"{self.name}.txt: the lift's {a} ends at row {rows[a][-1]} and "
                f"its {b} starts at row {rows[b][0]} — the column must be "
                f"unbroken north to south")
        # (2) the strata and the shaft's height
        for x in cols:
            assert m.stratum(x, rows["head"][0]) == canopy, (
                f"{self.name}.txt: the lift's head at ({x},{rows['head'][0]}) is "
                f"{m.stratum(x, rows['head'][0])!r}, not walkable {canopy!r}")
            for y in rows["shaft"]:
                assert m.legend[m.at(x, y)]["solid"], "the lift shaft must be solid"
            assert m.stratum(x, rows["drum crown"][0]) == "ground", (
                f"{self.name}.txt: the lift's drum crown at "
                f"({x},{rows['drum crown'][0]}) is not walkable ground")
        assert len(rows["drum works"]) == 1, \
            f"{self.name}.txt: the lift drum's solid works is ONE row"
        # (3) a body must be able to reach the crank
        beside = [(x, y) for y in rows["drum works"]
                  for x in (cols[0] - 1, cols[2] + 1)
                  if m.at(x, y) is not None and not m.legend[m.at(x, y)]["solid"]]
        assert beside, (
            f"{self.name}.txt: nothing walkable east or west of the lift drum's "
            f"works — nobody can reach the crank")
        # (4) the beam is lashed to something
        for x in cols:
            north = m.at(x, rows["head"][0] - 1)
            assert north is not None and m.legend[north]["terrain"] in (
                "bough", "greattrunk", "boughtop", "crown"), (
                f"{self.name}.txt: the lift's head beam at ({x},"
                f"{rows['head'][0]}) hangs off {north!r} — seize it to a bough "
                f"or a trunk or it reads as a mistake")
        # (5) the landing anchors, clear of everything else
        for name in (down, up):
            assert name in m.anchors, f"{self.name}.txt: no anchor {name!r}"
        for name in (down, up):
            ax, ay = m.anchors[name]
            for other, (ox, oy) in m.anchors.items():
                if other in (down, up):
                    continue
                assert max(abs(ax - ox), abs(ay - oy)) >= clear, (
                    f"{self.name}.txt: the lift anchor {name!r}({ax},{ay}) is "
                    f"{max(abs(ax - ox), abs(ay - oy))} cells from {other!r} — "
                    f"two zones on one anchor is a softlock, keep {clear}")
        assert m.stratum(*m.anchors[down]) == canopy, \
            f"{self.name}.txt: {down!r} must stand on {canopy!r}"
        assert m.stratum(*m.anchors[up]) == "ground", \
            f"{self.name}.txt: {up!r} must stand on the ground"
        # (6) THE NO-SOFTLOCK PROOF — reachable without the machine
        blocked = self.m.solid_cells() | {(x, y) for x in cols
                                          for y in rows["shaft"]}
        seen = {tuple(m.anchors["player_start"])}
        todo = [tuple(m.anchors["player_start"])]
        while todo:
            cx, cy = todo.pop()
            for n in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                if n in seen or m.at(*n) is None or n in blocked:
                    continue
                seen.add(n)
                todo.append(n)
        assert tuple(m.anchors[down]) in seen, (
            f"{self.name}.txt: the lift's top landing is reachable ONLY by the "
            f"lift. Ride up, reload, and you are stranded up a tree — and every "
            f"era but the present never wires the zones at all")

    _NPC_ANCHOR = ("_pos", "npc_")

    def assert_npc_room(self, extra=(), exempt=()):
        """Every anchor that looks like an NPC slot — `*_pos`, `npc_*`, plus
        anything named in `extra` — needs at least 3 walkable 4-neighbours.

        An NPC is a solid StaticBody2D carrying a 12x8 box inside a 16px cell,
        so a villager standing in a 1-cell corridor is not a squeeze, it is a
        WALL. The doctrine has said "never park a solid NPC in a 1-cell
        corridor" in prose ever since the goose wedged itself into the inn-nook
        lamp cell; three free neighbours is that sentence as arithmetic. Two is
        not enough: two lets a body past in one axis only, so a villager who
        happens to stand in the single gap in a hedge seals off a whole quarter
        of a town — and does it only when the mood machine walks him there, i.e.
        never while you are testing.

        `exempt` exists because a scripted NPC in a deliberately tight room is a
        real thing (downstairs' `kitty_pos` is in a 2-neighbour nook and she
        never moves)."""
        m = self.m
        bad = []
        for name, (x, y) in sorted(m.anchors.items()):
            if name in exempt:
                continue
            if not (name in extra or name.startswith(self._NPC_ANCHOR[1])
                    or name.endswith(self._NPC_ANCHOR[0])):
                continue
            free = [n for n in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                    if m.at(*n) is not None and not m.legend[m.at(*n)]["solid"]]
            if len(free) < 3:
                bad.append(f"{name}({x},{y}) has {len(free)}")
        assert not bad, (
            f"{self.name}.txt: no room to move — an NPC slot needs >= 3 "
            f"walkable neighbours or the villager standing on it is a wall: "
            + "; ".join(bad))

    def place(self, chars, sprite, shadow_h=0):
        """Blit a prop Sprite at its feature bbox; bake a contact-shadow band
        across the footprint's bottom rows first."""
        X, Y, XW, YH = self.px(self.bbox(chars))
        if shadow_h:
            self.bake_shadow(chars, shadow_h)
        self.bg.blit_cell(sprite, X, Y)

    def place_upper(self, chars, sprite):
        assert any(p for row in sprite.px for p in row), \
            f"upper sprite for {chars!r} is fully transparent (dead split)"
        X, Y, _, _ = self.px(self.bbox(chars))
        self.ov.blit_cell(sprite, X, Y)

    def place_split(self, chars, lower, upper, shadow_h=0):
        """A prop split across the layers (the bed_parts idiom generalized):
        `lower` bakes under entities, `upper` rides over them — bodies pass
        behind gate arches and lintels."""
        self.place(chars, lower, shadow_h)
        self.place_upper(chars, upper)

    def place_each(self, chars, sprite):
        """Blit one sprite per CONNECTED COMPONENT of the feature chars (two
        lamp posts share a char; each gets the same sprite, and identical
        cells dedupe to the same atlas tiles)."""
        for comp in self.comps(chars):
            self.bg.blit_cell(sprite, min(c[0] for c in comp) * T,
                              min(c[1] for c in comp) * T)

    def emit_prop(self, name, chars, img, fname=None, top=None, base_inset=0,
                  hframes=1, each=False):
        """A y-sorted WORLD prop (Tier 3): save its PNG beside the atlas and
        record a manifest row that scene/prop_spawner.gd spawns into the
        scene's y-sorted World at the chars' map bbox. For anything a body
        can stand both north and south of — the static layers can't sort it
        (see DESIGN.md "Z-order / layering doctrine").

        `top`: anchor the sprite's top at bbox_top + top px instead of its
        bottom at the bbox's south edge (the bed-cover crop case).
        `base_inset`: y-sort baseline pulled up from the south edge (a baked
        contact shadow's rows don't count as body).
        `each`: one sprite per connected component of the chars (the
        place_each idiom — several lamp posts share one char)."""
        self.bbox(chars)                   # assert the chars exist in the map
        fname = fname or f"{self.name}_{name.lower()}.png"
        img.save(os.path.join(OUTDIR, fname))
        opts = ([f"anchor=top:{int(top)}"] if top is not None else []) + \
               ([f"base_inset={int(base_inset)}"] if base_inset else []) + \
               ([f"hframes={hframes}"] if hframes > 1 else []) + \
               (["each"] if each else [])
        self._props.append(" ".join(["prop", name, chars, fname] + opts))

    # -- output --------------------------------------------------------------------------
    def write_overlay(self, suffix, draw_fn):
        """A full-map static overlay PNG beside the atlas (additive glow,
        multiply cloud-shade, ...) — scene .tscn picks the blend mode."""
        img = Img(self.W, self.H)
        draw_fn(img)
        img.save(os.path.join(OUTDIR, f"{self.name}_{suffix}.png"))

    def write_glow(self, draw_fn):
        self.write_overlay("glow", draw_fn)

    @staticmethod
    def glow_blob(img, cx, cy, r, color, a):
        """One radial dab on an additive glow overlay: alpha peaks at the
        center and falls to 0 at radius r."""
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                q = (dx * dx + dy * dy) / float(r * r)
                if q <= 1.0:
                    img.put(int(cx) + dx, int(cy) + dy,
                            color + (int(a * (1.0 - q)),))

    def _lower_frames(self):
        """Lower-canvas animation frames. Scenes with animated fabric
        (OverWorld's water) override; default is static — cells identical
        across every frame dedupe to plain static tiles either way."""
        return [self.bg]

    def finish(self):
        os.makedirs(OUTDIR, exist_ok=True)
        tiles, seen = [], {}
        _, lower = slice_atlas(self._lower_frames(), tiles, seen)
        _, upper = slice_atlas(self.ov, tiles, seen, skip_empty=True)
        cells, coords = pack_tiles(tiles)
        write_atlas(os.path.join(OUTDIR, f"{self.name}_tiles.png"), cells)
        write_tileset_tres(os.path.join(OUTDIR, f"{self.name}_tiles.tres"),
                           f"res://assets/tilesets/{self.name}_tiles.png", coords)
        write_layout(os.path.join(OUTDIR, f"{self.name}_layout.txt"),
                     {"lower": lower, "upper": upper}, coords,
                     f"from assets/maps/{self.name}.txt")
        if self._props:
            with open(os.path.join(OUTDIR, f"{self.name}_props.txt"), "w") as f:
                f.write(f"; y-sorted World props from assets/maps/"
                        f"{self.name}.txt — see scene/prop_spawner.gd\n")
                f.write("\n".join(self._props) + "\n")
        n_upper = sum(1 for row in upper for i in row if i is not None)
        print(f"{len(tiles)} unique tiles from {self.m.cols * self.m.rows_n} cells "
              f"({n_upper} upper-layer cells)")
        if "--preview" in sys.argv:
            out = sys.argv[sys.argv.index("--preview") + 1]
            for y in range(self.H):
                for x in range(self.W):
                    p = self.ov.get(x, y)
                    if p[3]:
                        self.bg.put(x, y, p)
            self.bg.save(out if os.path.isabs(out) else os.path.join(HERE, out))
