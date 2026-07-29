---
name: map-authoring
description: Authoring assets/maps/*.txt and placing props — the z-order doctrine and its three prop tiers, walk-behind corridors and ridge caps, mask bands, the terrace/cliff/chasm kit, walk-behind trees, invisible-wall and reachability lints. Load BEFORE editing any map txt, adding or moving a prop, building a cliff/terrace/bridge, making something walk-behind, or when a body clips, floats, walks on a wall, hits an invisible wall, or renders under something it should be in front of.
---

# Map authoring

A scene's layout lives in `assets/maps/<scene>.txt`: a `legend` (char → terrain +
walk/solid), named `anchor`s, and the ASCII grid. Move a feature char and it moves
in-game. The same file drives paint (Python) and collision (`scene/map_data.gd`), so
they cannot drift.

Full statement: **docs/DESIGN.md → "Z-order / layering doctrine"**.

## Z-order doctrine (lint-enforced)

Draw order is a fixed sandwich: **lower tiles → y-sorted `World` entities → upper
tiles.** Three tiers decide where a piece of art goes.

**Tier 1 — terrain, flat things, wall-flush props → lower layer.**

**Tier 2 — roofs, canopies, lintels → `place_split()`**, upper art ONLY above solid
cells (or door cells). Every walk-behind corridor is **capped by a solid `ridge` row**
(map digits, all named `ridge`, never a struct) so at most a head-peek crosses the
silhouette.

- The cap is **SCALE-GATED** (`CHIBI_MAPS` in `_check_art.py`): the overworld's ≤1-tile
  chibi can't out-peek a silhouette, so its covered cells need no cap — the Home Tree's
  whole crown is open walk-behind `G` cells, only the trunk solid.
- **Small-prop rule:** anything without 2 covered rows + a 2-row base (town trees) gets
  NO corridor — make it fully solid.

**Tier 3 — anything a body can stand BOTH north and south of → NEVER baked.**
Free-standing furniture, street lamps, the well, the stall, the fountain, and (since
2026-07-19) the town YARD FENCES. `emit_prop()` writes the PNG + a
`<scene>_props.txt` manifest row, and `scene/prop_spawner.gd` spawns it into `World` at
the feet convention (`node.y + 20`).

- Fences were the last baked standable: rails on the lower canvas drew UNDER a pressed
  body's sunk feet, reading as standing ON the fence. Now `town_fence(n)` run-length
  props — town `F` = the 3-cell gate runs via `each`, `G` = the 5-cell orchard run.
  Cells stay solid; the driver's fence class paints plain grass. **`each` requires
  identical components.**
- Counter-height pieces (desk / table / workbench) make their **TOP footprint row
  `walk`** so a body tucks in behind the tabletop.

## The depth mask — "the player hangs off the edge of the cliff"

A body's collision box hugs its FEET (12×8 at +6, box bottom = origin+10) while the
~22×38 figure draws to origin+21. So **pressed SOUTH into any solid cell, exactly 11px
of sprite hangs past the physics boundary.**

That is what `band=12` in `TileScene.mask_band()` covers — the number is derived, not
chosen. It re-draws the face's own top 12px over the body (same paint, same coords, so
it can never seam). **Legal only on runs ≥2 cells and band ≤14.**

**IT IS A TIER-3 Y-SORTED STRIP, AND MAKING IT UPPER-LAYER TILES WAS A BUG
(2026-07-29).** The upper layer draws over every body *unconditionally*, and **three**
different bodies meet a run's top row wanting three different answers:

| body | origin.y | wants |
| --- | --- | --- |
| ON TOP, pressed south | exactly `run_top-10`, and no closer | masked — the whole point |
| IN THE NOTCH beside the run | `run_top-10 … run_top+6` | NOT masked |
| ON THE TERRACE BELOW, hopping | `run_top+30` or more | NOT masked |

The notch exists because **every band staircases**, so at each step the neighbouring
column's ground runs one row further south and a body stands level with the wall. As
upper tiles all three were masked: hopping within ~1.5 tiles of a cliff sliced the top
off your head, and standing at a corner clipped the character's *face* against the wall
beside it. **No band height fixes either** — the sprites want opposite answers from the
same pixels.

Keyed as a World sprite it just sorts, and the key is **`run_top - 8`**: the only 2px of
daylight between the first row of that table and the second, and it exists at all only
because the on-top body cannot press past `run_top-10`. Anything lower re-clips the
overhang; anything higher clips a face at every corner. Consecutive columns sharing a
top row emit as one strip, so a staircased band costs a handful of sprites, not one per
column.

**A STRIP MUST ALSO OVERHANG ITS RUN BY ONE COLUMN wherever the neighbouring run sits a
row HIGHER.** The notch body stands at the very edge of its own column and the figure is
**22px wide**, so a third of it hangs into the next column — where this run's strip does
not reach and the neighbour's strip is 16px too high to help. Result: the foot and the
coat-tail poke out over the wall, the exact artefact the band exists to prevent, just
moved sideways. The extra column copies the FINISHED art at those coordinates, so it
lands on the neighbour's own face — same paint, same coords, no seam.

The lesson under all four of these: **a mask is not "the cells of the run".** It is
"wherever a 22×38 figure can overhang a drop", and that region is taller, wider and
sorted differently than the run itself.

This is the layering doctrine's own rule applied to itself: **depth belongs to y-sort,
never to the static layers.** The manifest carries them as `mask <png> <x> <y> <ysort>`
rows — explicit pixel rects, because a band's runs are not a feature bbox.

The town/building twin is `_town_props._eave_lift` (mirror the solid row's top 12px onto
upper), legal ONLY with a ≥2-row solid base below the corridor: building facades, the
home-tree trunk. Facades carry `_eave_lift` TOP + SIDE mask bands (outer 6px columns;
Academy included). Interior south walls carry `south_lift()` in `_interior.py` — the top
12px of body-pressable `#` south cells mirrored to upper, so nobody stands ON the bottom
wall.

**Adding a band to a map whose upper layer was empty ARMS three z-order lints.** Two
pass by construction (a banded cell is solid — `_check_art.py` has an explicit mask-band
exemption), but *"ridge cells under upper art"* scans the WHOLE map. That is why `^` in
both town maps was retyped from the vestigial `ridge` to `treecanopy` (byte-identical
paint).

**Exception:** Alembic's bridge gets a hand-drawn `bridge_fascia()` on the water cell
south of the deck INSTEAD of a mirrored band — river cells animate on 4 frames and a
mirrored band would freeze half the cell.

## The terrace kit — verticality is AUTHORING, not a system

There is no elevation feature and there does not need to be one. **A terrace is two flat
walkable regions separated by a band of SOLID cells wearing opaque hand-drawn face art,
pierced by a walkable stair gap.** Alembic's Academy terrace proved it; the idiom lives
in `assets/_tilekit.py`:

- **`stamp_columns(chars, sprites, run=N)`** — hash-picks a salted face variant per
  vertical run and **asserts the run height**. Art lands on a run's TOP cell, so a SHORT
  run paints a rock wall over the walkable cell below and **nothing else lints that**.
- **`foot_shade`** — the driver's struct shadow band skips `snow`, so a winter cliff
  would otherwise float.
- **`mask_band`** and **`assert_reachable`**.

`_gen_tileset_town.py` was refactored onto this kit and regenerates byte-identical —
that is the proof it is shared rather than forked.

- Cliff heights come in a family: `town_cliff(h=)` at 2/3/4 rows.
- **Bands must STAIRCASE across the map.** Uniform bands read as one cliff drawn twice,
  which is exactly how the first terraced Lanternwood failed.
- **DON'T AUTHOR A CHASM (2026-07-29).** The kit has one — `town_cliff(void=True)`
  crossed by a Tier-1 `town_trestle` — and Lanternwood shipped a rift on it and then
  removed it, after two passes at the face art failed to make it read. Both directions
  of ramp were tried: lit-at-the-top is plainly a wall, and dark-at-the-top with a lit
  far rim (`_rift_face`, briefly shipped) is *still* a wall, just a wall with an odd
  highlight. **A 2-row band of dark in flat top-down is a wall no matter what is painted
  on it**, and the trestle across it read as a wooden panel set into one — players
  called it a bug in the map, twice. Verticality here is authoring, and authoring an
  ABSENCE is the one thing it is bad at: a cliff is defined by the face you see, a hole
  by what you can't. If a terrace needs a feature, give it something POSITIVE — the east
  flank got the town skating rink (`frozen_pond(w=128, h=64, skated=True)`, flanked by
  lamps) and reads instantly. The builders stay in the kit; no map uses them.
- **LANTERNWOOD'S TERRACES ARE A BUILT WALL, NOT A CLIFF (2026-07-29,
  `town_cliff(wall=True)`).** Three passes, each a different wrong answer, and the
  sequence is the lesson: (1) fixing only the crest — a straight cap over a near-black
  turn-under — cured "the upper ground stops" but still read as an *edge*, not a *top*;
  (2) rustic coursed masonry on the face was wrong the other way, since heavy per-stone
  value variation reads as rubble; (3) what was wanted was **cast cement/cinderblock** —
  flat, with all the contrast in a regular 16×8 running-bond joint grid and none in
  per-stone value. Joints sit two steps down the ramp, never black, or the wall reads as
  a lattice. The crest is a **coping that stands proud and throws a shadow down the
  wall, under BROKEN snow**: without the overhang there is no top, and an unbroken white
  band along a terrace is a drift lying on the ground. Alembic does not pass the flag
  (pale grass, eroded read is right) and regenerates byte-identical — check that.
- **A STEPPED BAND NEEDS ITS CORNERS (2026-07-29, `town_cliff_return`, wired through
  `stamp_columns(ret=)`).** Bands must staircase — and at every step the higher run's
  face used to stop at a straight vertical cut against open snow, so the two runs read
  as two unrelated walls rather than one wall stepping down. Fix: a vertical band down
  the exposed side, carrying the coping AROUND the corner to meet the lower run's
  coping. **A step exposes TWO legs, not one** — the higher run's TOP row (`cap=True`,
  where the coping turns) and the lower run's BOTTOM row (`cap=False`: solid wall above
  it, so no coping and no snow, just the side face). Do both or the corner is half
  closed. Detect a step by `ty ± 1 in neighbour`, never by comparing heights: **one char
  serves several bands** (Lanternwood spends `C` on the level-4 band and the gate band
  twenty rows apart), and a height comparison finds an eighteen-row "step" between two
  unrelated walls.
- **A wall END throws a shadow SIDEWAYS (`TileScene._end_shade`).** At a step's exposed
  corner the wall's cap sits at the walker's own feet level, so the eye follows the cap
  line straight past it and reads more ground — you walk into a wall there is nothing to
  look at. A cast shadow on the open ground beside the end is the cue that fixes it;
  nothing else in a flat top-down view says "something tall stands here" as cheaply. The
  band's own `foot_shade` only shades SOUTH, which is no help at a corner.
- The bluff's north drop is the other answer: a 1-row authored cliff-LIP band (ragged
  sunlit brow + dark crevice line, three salted 16×16 variants).

## Walk-behind trees

Conifer footprints are no longer fully solid. **The case of the char means CROWN vs
TRUNK** — `Y`/`P` walkable boughs over `y`/`p` solid trunk, one Tier-3 prop spanning
both chars. Exactly the LAMP idiom (`L` mantle over `l` post). The crown sprite's y-sort
key already sits below a body standing in those cells, so walk-behind is free and needs
no code. It also turns a 4-row wall into a 1-row obstacle.

**The old alternate-the-case anti-merge trick is GONE with it** — two spruces authored
edge-to-edge now FUSE into one component and one stretched sprite. So
`_gen_tileset_lanternwood.py` asserts every component is a clean 2×4 with exactly its
bottom row solid.

## Walls, gates and reachability

- **Refused exits need a wall.** The gate-mouth road runs to the map edge and collision
  only stamps grid cells — `_wall_gate_mouth` in both town scenes and in
  `lanternwood.gd`.
- **AN EXIT MUST BE A PLACE YOU WALK INTO, NOT A SPOT YOU WANDER ONTO (2026-07-29).**
  Lanternwood's south lane used to run three cells past the stairs and stop in open snow
  with the exit trigger floating invisibly on it, so a fight in the lower street kept
  ending on the overworld by accident. The fix is three things together, and none of
  them alone is enough: a two-cell lane running OUT through a cut in the solid border
  (so the mouth is a chokepoint), a `town_gatepost` pier either side of it (walkable
  crown over solid base, the lamp idiom — it names the boundary without walling it),
  and the anchor moved INTO the mouth. Then the scene refuses the exit while a
  set-piece is live — out loud, via `theater.hint`, because a travel door that silently
  refuses reads as broken.
- **A 1-cell-thick forest/hedge line can't terminate in the open** — the lobe lattice
  rejects the tip into a grass bay. End it against another solid class, or use fence
  cells.
- **Never park a solid NPC in a 1-cell corridor** (the room-to-move rule).
- **Never open a walkable pocket inside a chase leash** — the goose wedged itself in the
  inn-nook lamp cell; reverted.
- Nothing walkable may hide behind a tall sheet (the 112px library backs onto pines).

## The lints (`python3 assets/_check_art.py`)

Fails the build on:

1. **Floating upper art** — solid-cell mask bands exempt.
2. **Uncapped walk-behind corridors** — waived on `CHIBI_MAPS`.
3. **Misplaced ridge cells** (ridge under upper art — scans the whole map).
4. **An empty upper layer.**
5. **A bad prop manifest.**
6. **The INVISIBLE-WALL lint** — a pressable solid cell whose tile dedupes to open
   ground. Tier-3 manifest chars are exempt: solid map cells under y-sorted sprites are
   fine.

**The T3 coverage rule:** a prop footprint cell stays solid only if frame-0 art covers
≥20% of it — otherwise retype it to a walkable TWIN char with the same terrain name
(town `O`/`U`/`L`, hall `l`). Paint stays byte-identical.

## Sibling map grids are byte-locked

Some maps exist as era pairs that must stay in lockstep, cell for cell:

- `town.txt` ↔ `town_fest.txt` (drained ↔ bright era; the fest copy only changes
  palette and the Academy door's `open_door=True`).
- `overworld.txt` ↔ `overworld_bright.txt`.

Edit one, edit the other in the same commit, or the eras silently diverge.
