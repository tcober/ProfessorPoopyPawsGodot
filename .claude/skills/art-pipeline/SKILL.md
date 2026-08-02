---
name: art-pipeline
description: The procedural pixel-art pipeline — Python generators, the tile kit, palettes, sprite sheets, the slice/dedupe tileset build, animated water/lava, and the regen workflow. Load BEFORE writing or editing anything in assets/ (_gen_*.py, _tilekit.py, _palette.py, _sprites.py, _tiles.py, prop libraries), before adding a new scene's tileset, before touching a color ramp or a sprite sheet row, and whenever art renders scrambled, floats, seams, ghosts, or comes out the wrong color.
---

# Art pipeline

All art is drawn procedurally by stdlib-only Python. The AI-generated reference sheets
in `docs/reference/` are concept only — parked behind a `.gdignore` so Godot never
imports them. Never hand-edit a generated PNG; edit the generator and re-run it.

Full statement: **docs/DESIGN.md → "Art pipeline"**. Palette registry:
**docs/DESIGN.md → "Palette Registry"**.

## The regen workflow (in this order, every time)

```sh
python3 assets/_gen_tileset_<scene>.py   # or any other _gen_*.py
python3 assets/_check_art.py             # lint — fails the build on real errors
godot --headless --import                # REQUIRED
```

`--headless --import` is not optional. **Game runs never re-import**, so a regenerated
atlas renders scrambled until you do. The same rule applies after adding any script
with a NEW `class_name` — headless runs report "base class not found" otherwise.

## One scene pipeline, one map format

Every scene is TILED on the shared kit. A NEW scene = a map txt + a thin config.

- **`assets/maps/*.txt`** — the source of truth per map: a `legend` (char → terrain +
  walk/solid), named `anchor`s (spawns, exits), and the ASCII grid. Python paints from
  it; `scene/map_data.gd` builds collision and logic from the *same* file, so paint and
  physics cannot drift. **Keep `assets/_maps.py` and `scene/map_data.gd` parsers in
  sync.**
- **`assets/_core.py`** — canonical scale constants (`ZONE_TILE=16`, `ZONE_CELL=48`,
  `ZONE_FEET=44`, `OW_CELL=24`, `ICON=32`), `h2()` deterministic hash noise, `pick()`
  ramp dither, the `Img` canvas, the PNG writer.
- **`assets/_palette.py`** — the color script as data. `ramp(seed, shadow, tones)`
  derives N-tone material ramps (6 terrain / 4 sprite) from scene seeds, hue-shifting
  the dark end toward the scene's violet or teal bias. `SCENES` is the registry;
  per-scene `"ramps"` hold hand-tuned identity ramps for materials that can't be
  derived. `ACTORS` holds Basil / Schweinler / slime.
- **`assets/_tilekit.py`** (`TileScene`) — canvases, material ramps, footprint
  `place()` / `place_split()` / `place_each()`, glow, and the slice/dedupe `finish()`.
- **`assets/_tiles.py`** — slices composed canvases into a real TileSet (atlas +
  `.tres` + layout in `assets/tilesets/`).
- **`assets/_sprites.py`** — sprite/fx drawing primitives.
- `understory` carries six kinds — `roots` / `fern` / `shroom` / `log` / **`drift`** /
  **`sapling`**. `drift` is the important one and the common case: ferns, roots and
  saplings all come out of the leaf ramp, so a forest floor dressed only in those is
  green dressing on green ground, and warm fallen leaves are the only cheap thing that
  changes the field's HUE. Draw a leaf as a small SOLID patch with a lit edge, never as
  a sloping LINE — a line has direction and no area, and a floor of them reads as dead
  twigs. Stamp SEVERAL SALTED VARIANTS per kind: one litter cell is exactly one opaque
  atlas tile, so variants are nearly free, and one variant repeated three hundred times
  is wallpaper with a visible period.
- **`assets/_tree_props.py`** — the TREEHOUSE-TOWN kit (Alembic's canopy storey):
  `tree_hut` the bough hut, `tree_edge` / `tree_edge_return` the timber fascia,
  `tree_span_edge`, `tree_bridge`, `rope_ladder`, `tree_trunk`, `tree_canopy`, the
  `dinghy_lift_*` trio, `understory`. Every builder takes its material RAMPS as
  parameters — unlike `_town_props`, which closes over Alembic's own FOLIAGE/CEMENT.
  Two hand-pinned materials live here and have to: `ROPE` and `THATCH` both come out
  green under a teal scene bias and magenta under a violet one, so deriving them
  obeyed the palette code and broke the palette doctrine.
- **`assets/_academy_props.py`** — the ALEMBIC ACADEMY's own four pieces: the
  crenellated `academy_rampart` (a `stamp_columns` band whose merlons are phase-locked
  to the column's own x so a 50-cell wall is one continuous battlement and still dedupes
  to `len(sprites)` tiles), `academy_tower` (a drum tower whose ashlar courses BOW —
  drawn straight they flatten a cylinder into a panel with a curved outline),
  `academy_orrery` (three rings of DIFFERENT eccentricity; three concentric circles read
  as a target painted on a wall) and `academy_wing` (one builder, one salt, two crowns —
  observatory and still-house, so their facades dedupe). Everything else the precinct is
  built from is reused: the keep is `town_academy`, the terrace `town_cliff(wall=True)`,
  the flight `town_stairs`, and the two great trees flanking the keep are Alembic's own
  `great_trunk` / `great_crown`.
- Drivers: **`assets/_interior.py`** (+ `_interior_props.py`) for rooms;
  **`assets/_overworld_tiles.py`** (`OverWorld`) for the overworld map, Alembic Town,
  Whisker Meadow AND Lanternwood; prop libraries `_overworld_props.py`,
  `_town_props.py`, `_meadow_props.py`, `_propkit.py`.

`scene/tiled_map.gd` stamps the result onto TWO TileMapLayers — under and over entities.
`scene/painted_map.gd` builds the invisible collision layer at runtime from the same map
file. Reference implementations: `scene/house.tscn` (interior),
`scene/overworld.tscn` + `scene/alembic_town.tscn` (exterior), `scene/meadow.tscn`
(combat zone).

## Dedupe is the whole point

Cells must be **byte-identical BY CONSTRUCTION** so the slicer collapses them to a small
atlas — exactly how an SNES scene lives in VRAM. Current counts: house 60 tiles from 336
cells · overworld ~1170 from 7056 (~700 animated) · town ~190 from 1904 · meadow ~145
from 1152 · Lanternwood ~100 from 1232 · library ~55.

This is why **fabric texture must be tile-local** (`_grain_dither` / `_hatch`) and
**never keyed on absolute position**. Grass/forest carry a 32-periodic phase on interior
cells; variants only on interior cells.

**Standing rule (tile reusability):** shared builders + the SAME salt for sibling
buildings (the two shops dedupe because only roof/sign/wares differ), few repeating
variants for scenery, opaque un-outlined tiled props. Watch the `finish()` tile count —
a jump means something broke dedupe.

## Autotile transitions

Neighbor-keyed, pure functions of (terrain, per-class 8-neighbor masks, local pixel),
including **45° corner cuts**: a cell whose neighbor mask is one orthogonal pair renders
that corner cut along the tile diagonal. Every boundary is painted **one-sidedly by its
OWNER class** (water > waste > beach > road > forest > mountain), so 1-cell stair-steps
in the map txt chain into continuous diagonal coasts, rims and ridge edges.

Forest canopy and mountain massifs share one 16-periodic lobe lattice — crown-ball vs
stylized-peak shading — whose arcs also FORM each rim (`_arc_cell`: lobes whose disc
would cross an open boundary are rejected, bays render the neighbor's fabric, a 1px ring
outlines the silhouette, snow caps the massif's north-facing edge lobes).

Terrain classes: grass, forest, mountain, water/sea/river, beach, road, and the
2026-07-19 five-lands additions — **snow** (wind-scour drifts), **desert** (purple dune
sand), **basalt** (violet-charcoal crust), **lava** (solid, ANIMATED) and **pines**
(snow-dusted conifer mass on its own ramp). The `road_verge` knob is `"grass"` by
default, `"snow"` in Lanternwood.

**LAVA-RING LAW:** every lava cell's neighbors must be lava or basalt. Asserted at build.

## Animated water and lava

All sea/river/lava tiles cycle 4 Godot-native animation frames. Zero runtime code; scene
CanvasModulate tints ride on top.

- `OverWorld._lower_frames()` repaints only water/lava cells per frame on a clone of the
  finished canvas. **Frame 0 must reproduce the still canvas byte-identically** —
  asserted.
- `pack_tiles` lays each animated tile's 4 frames as contiguous same-row atlas cells,
  and the `.tres` declares durations on the **base cell ONLY** — frame cells never get
  `x:y/0 = 0`.
- **Every frame-dependent term must be periodic in `WATER_FRAMES`** or the loop seams:
  drifting crests 4px/16, river rows 2px/8, foam-churn salts and glint blinks period 4,
  molten channels crawl 4px/frame.
- Lava uses a **hand ramp** — incandescence cannot survive `ramp()`'s violet shadow law.
- The town fountain is a 4-frame `hframes` prop (`town_fountain(frames=4)`); pour
  columns live in the base silhouette so the baked outline never ghosts, and
  `_fountain_anim` only recolors. The towns' existing `_animated` scanners cycle it.

## Window breath (baked animation)

`_anim_building` knobs, all default-off so still bakes stay byte-identical:

- `windows=` — the **HEARTH BREATH** (`WIN_PULSE` / `_breathe`): a lit pane PULSES,
  never travels. Symmetric level curve over the whole sheet, every pane of a house IN
  PHASE, no wandering glint, two warm ladders + a two-ring bloom onto the logs.
  **Step 0 = the art as drawn**, which is what keeps the still bake identical.
  8-frame cabin sheets ≈ 1.4s per breath while smoke stays periodic in 4.
- `wood_flues=` — grey lazy woodsmoke.
- `_finish(pad=)` — smoke RISES into `SMOKE_PAD` sky rows padded atop the animated
  sheet (`_town_props._pad_top`). Bottom-anchored props extend up for free; without the
  pad, puffs clip flat at y=0.

## Sprite sheets

- Cast sheets come from `assets/_gen_prologue_sprites.py`, `_gen_basil_sprites.py`,
  `_gen_fuji_sprites.py`, `_gen_slime_sprites.py`, `_gen_overworld_actors.py`.
- **A sheet only ever APPENDS.** Adding a row is safe; renumbering existing cells breaks
  every scene that indexes them.
- **Sheet rows are a SpriteFrames contract** — the dev-menu beat table and every probe
  depend on them (see the **probes-and-shots** skill):
  - **kid Basil, 6×6** — row 4 is `sleep` / `wake` / `sigh` (kid-only); row 5 is the
    4-frame `climb_up`.
  - **adult Basil, 6×11** — row 8 is `look_watch` / `sit` / `bow_head` / `knapsack` + a
    2-frame trudge; row 9 is `knapsack_back` (the south-gate look-back), cols 1-2
    `defeat_walk` (the head-down hall walk of shame), cols 3-5 `knapsack_down` + the
    2-frame `knapsack_walk_down` (the gate exit walking INTO the camera — the old
    side-profile walk tweened south read as a sideways glide). Adult-only. Row 10 is
    the 4-frame `climb_up`. **Fuji's sheet is 6×11 with the same row 10.**
- **EVERY PLAYABLE SHEET OWES A `climb_up` ROW, and the missing one is silent.**
  Alembic's great trees are reached by rope ladder; `PartyMember` plays the clip by NAME
  (never through `_play_directional`) and forces the facing UP, gated on
  `sprite_frames.has_animation("climb_up")` — so a body without the row falls back to
  `walk_up` and reads as a cat SLIDING up the rungs, arms at its sides, with nothing in
  the log. Four frames, 8fps, back view ONLY (you always face a ladder — there is no
  side or down variant), contralateral: high paw with the opposite foot lifted, frames
  0/2 the reaches and 1/3 the passing positions. Cell 0 is deliberately not a planted
  neutral — there is no neutral on a ladder.
  - The row can be present in the PNG and still be dead: **`fuji_frames.tres` carried the
    four `atlas_climb_*` sub-resources with no animation entry referencing them** and
    nobody noticed, because the fallback is a plausible-looking walk. `_check_art.py`
    validates region geometry, not that a clip exists — if you add a row, add the clip
    and load the resource once to prove it.
  - **A KID'S ARMS SPLAY OUT WHERE AN ADULT'S CONVERGE.** The adult's forearms angle IN
    toward rungs narrower than his shoulders (splayed straight up reads as surrender).
    Copy that onto the chibi rig and the arms vanish: a kid's head is nearly as wide as
    his shoulders and swallows them. The kid's paws go to `CX ± 8`, just clear of the
    skull silhouette — the same place `kid_body_down(arms="up")` puts them. Foot lift is
    2px, not the adult's 5: the round tummy hangs lower than a coat hem and eats
    anything higher.
  - NPC cast sheets live in `_gen_prologue_sprites.py`: Mom, adult Schweinler, badger,
    stork, Kitty-in-bed, and Kitty's mother (`npc_kittymom_gen.png`). `npc_fuji_gen.png`
    is a 480×48 10-col sheet: idle / act (wand-cast) / emote (startled) / back / side.
  - Audience back cells: sheep / mouse / badger grew cols 6-7 (→384×48); owl and stork
    stay at 6.
- The knapsack is a true **BINDLE ON A STICK** — the earlier stickless bundle read as a
  lumpy raised ARM. The stick is ONE tip-to-grip line whose middle hides behind the huge
  head (the classic behind-the-head pass), with its front end redrawn OVER the fist
  (pole through the paw = the grip).
- `prologue_fx.png` is TWO 16-cell rows (256×32). Row 0 is frozen byte-identical. Row 1
  = watch/poof/motion-lines, the kiss HEART at 19, Ebb sparks at 20-21, the recital's
  chemistry at 22-24 (bursts drawn WHITE-HOT AND COLOURLESS so one pair of cells
  modulate-tints to all four compound colours), 25-31 free.
  **`WorldFx.sheet_sprite` infers vframes from sheet height, so old frame indices
  survive — but NEVER widen a row.**
- **NPC sheets: row 0 is the POSE row, rows 1-3 are an OPTIONAL WALK CYCLE**
  (2026-07-29). `frame_cols` gates optional facings on row 0 (`back`/`side` are built
  only when `frame_cols` >= 8/10). A new villager is a PNG + exports.
  - `row 0` idle_down×2 · act×2 · emote×2 · back×2 · side×2 (cols 0-9)
  - `row 1` walk_down ×6 · `row 2` walk_up ×6 · `row 3` walk_side ×6 (faces LEFT),
    cols 6-9 padded empty — so a walking villager is **480×192**.
  - Direction is the ROW, the cycle is the COLUMNS — the same contract the party sheets
    use, which is why the proven 6-frame stride tables get reused verbatim rather than
    re-timed.
  - `npc.gd` gates the walk clips on the sheet's real **HEIGHT**, deliberately not on
    `frame_cols`: a sheet that grows rows starts walking with **no scene edit at all**,
    so every staged `theater.walk` animates the moment its art lands. A 48px-tall sheet
    stays legal and stays a statue.
  - Walk clips run at their own `walk_fps` (~10). Sharing `idle_fps` (1.6) is what made
    a moving villager read as a sliding statue for the whole project up to here.
  - **`walk_down` f0 == row-0 col 0 and `walk_up` f0 == row-0 col 6** — the planted
    neutral contract, same as Basil's sheet, so a walk closes into its idle exactly.
  - **`walk_side` f0 does NOT match the col-8 idle-side, and cannot**: cols 8-9 were
    drawn at `(0,0)` offsets before the walk rows existed, while `side_fF[0]`/`side_fB[0]`
    are `(2,0)`/`(-1,0)`. Measured cost is 18-31 silhouette px — the REAR foot settling
    2px, with body, head and foot baseline identical. On a villager hopping one cell
    every ~3s that reads as a weight shift; on anything that stops and starts constantly
    it would not, so a future fast-moving NPC wants its cols 8-9 redrawn to walk f0.
  - Who has walk rows: **hare, beaver, foxkid, mayor, mom**, and since 2026-07-30
    **adult Schweinler and the badger**.
  - **A SIDE CELL MUST BE THE CHARACTER'S MARKINGS ROTATED, NOT THE ANIMAL'S.** The
    badger's front cell carries two VERTICAL face stripes flanking a white blaze, so
    his profile is ONE vertical band down the skull with the dark ear on top of it.
    Drawn as a real badger's horizontal nose-to-ear stripe he is a different species,
    and 2px of drift closes it over the crown and he reads as a hooded bird. The
    other half of the identity is PROPORTION — in his front cell the head is bigger
    than the trunk and the white belly covers most of the chest; invert either and
    it is some other stocky animal in his colours.
  - `_pig_curl` lays its dark edge only on EMPTY pixels, so a curly tail begun
    exactly on the body's rim loses its root to the outline pass and hangs in space
    (the shipped KID Schweinler side/back cells still do). Start it one px inside.
- **Never `play_emote` a back-turned head** — it flips to a front face.

## A PROP'S UNDERLAY IS THE GROUND IT MOVED TO (2026-07-30)

**This has now bitten twice in one day, both times when something CHANGED STOREY OR
SQUARE and its `TERRAIN_CLS` entry stayed where it was.** When you move a prop, move its
render class — the check is one line and the symptom never points at it.

- The **shops** kept `deck` after coming down off the canopy boardwalk, painting a
  five-cell **plank raft** on the forest floor (below).
- The **fountain** kept `grass` after moving into the paved festival square, punching a
  three-cell **green lawn** through the middle of the court.

**And a gap in Tier-1 art shows up as AUTOTILE, which reads as clipping.** The great
trees' shafts were blitted one row below the ring's whole 9-row block, so the block's
last two rows had no trunk art on them at all — the ring stops drawing after its fascia.
What filled the hole was the underlay doing its job: `ringedge` renders leaf, the ladder
beside it renders deck, so the pair drew a leaf-to-plank **transition** — a pale
hard-edged wedge either side of the rungs that looks exactly like a clipping bug. Three
fixes: start the shaft two rows up under the fascia that is meant to hide its top edge,
type the trunk's flanking cells as trunk so there is no class boundary there at all, and
widen the shaft to actually FILL its footprint (it was ~35px of bark in 64px, so the
outer third of each flanking cell showed underlay however you typed it).

## BAKED ORDER IS DEPTH — a trunk through a deck (2026-07-30)

The fix above filled those rows, and then the tree read as **CHOPPED OFF** instead: the
shaft was blitted *after* the ring, so 64px of bark with a dead-straight `edge()` outline
along its top landed two px below the fascia's hem. A trunk that visibly BEGINS at a
horizontal cut just under a platform is a post nailed to a saucer.

**Tier-1 has no sort key — the later blit wins — so on the baked layer the DRAW ORDER
*is* the depth order, and you have to choose it on purpose.** Shaft first, ring over it:
the straight edge is buried under opaque decking and the only line crossing the trunk is
the fascia's own hem, which is an **arc**. An arc crossing a cylinder is an overlap; a
straight line across it is a cut.

Order alone was not sufficient, and the reason is worth keeping: **bark under a platform
and bark in the open are the same six colours**, so the hem read as a change of material
rather than as something in front. `_alembic._shade_under` pulls the bark two ramp steps
down for 9px below the hem and one for the next 11, with the band's lower edge following
the fascia's own `sqrt(1 - t²)` — so what emerges is emerging out of shade. Two hard
bands, never a dither: bark is banded (`_BARK_BANDS`).

## A BUILDING'S UNDERLAY IS THE GROUND IT MOVED TO (2026-07-30)

Alembic's three shops read as *a flat tan box with a cone sitting on the middle of it*,
and the hut art was innocent. `tree_hut` is deliberately narrower than its footprint, and
`shoproof`/`shopbody` still rendered **`deck`** from the era when the shops stood on the
canopy boardwalk. On the forest floor that painted a five-cell **plank raft** under every
shop. **When a building moves storeys, its terrain's render class moves with it** — check
`RENDER_CLASS` in `_overworld_tiles.py`, not just the map.

**The raft was also silencing a lint.** The invisible-wall check only looks at solid cells
rendering as *open ground*; a `deck` underlay is "built", so it skipped them. The moment
the ground was honest, the check fired — the footprint was 5 cells for a 3-cell building.
**Match the footprint to the art**, in whichever direction is right: the shops were shrunk
to 3 first, and then the art was rebuilt and they went back to 5 (below).

## A BUILDING BELONGS TO ITS TOWN, NOT TO ITS PREVIOUS ADDRESS (2026-07-30)

The shops kept reading badly after the raft came out, and the answer was that the
BUILDING was wrong, not its ground. `tree_hut` — a cone of thatch over a barrel of withy
staves — is right in a bough and is a **tiki hut** on a forest floor: one flat tan value
from finial to porch, no wall material, gaps you see daylight through, and three cells
wide beside a five-cell cottage. It got called out twice before I stopped defending it.

`_town_props.town_shop` is now the town's own envelope (80×64 over 5×4 — the cottage's
exact footprint: leaf canopy, greeny cement, copper header and rain-barrel, vines) plus
the three things a house does not have. In order of weight:

1. **THE AWNING** (`_awning`) — the strongest "this is a shop" cue at 16px, because it is
   the only **cloth** on any building in the town; everything else is plaster, leaf,
   timber, copper. **Cream and one colour in 4px stripes** — a band in one colour is a
   banner whatever you do to its edge. The **scallops** are cut on the same 8px period as
   a stripe pair so each arc hangs off one cream and one coloured stripe. Then two rows
   of shade on the wall under it, which is what actually says the cloth stands PROUD;
   the first pass spent that budget on little iron stays and at this scale they read as
   violet scratches.
2. **THE DISPLAY WINDOW**, warm-lit and on the breath cycle, with the trade's goods in
   it — see the silhouette rule below.
3. **THE HANGING SIGN**: a **dark painted field in a timber frame**, never a bare plank.
   Drawn as bare `TIMBER` the board was a big mid-brown rectangle on a light cement wall
   — the loudest thing on the building — and the device, the only part that carries
   meaning, was a pale mark lost in the middle of it. Dark ground, one bright object.
   And the device is **never lettering**: there is no font at 16px.

`trade` (arms / tonics / inn) picks cloth colour, goods and device together, so three
shops off one builder are three shops and not three copies. `CLOTH` is hand-pinned
lit/mid/shade per trade — the `BRASSD` precedent, and for the same reason: `ramp()`'s
violet law would take the inn's amber straight to red.

### Small objects in a lit window are SILHOUETTES

Objects drawn in their own colours against warm glass came out as mud: a ten-pixel helm
in `IRON` is a grey blob and a ten-pixel flask in `MINT` is a green one, and neither
survives a 3× screenshot. **Backlit things are dark** — the same argument
`_hearth_window` already makes for keeping its mullions dark — so wares are `DOORDARK`
masses with one lit rim, and they read at native res because a silhouette is all shape
and has no detail to lose. Corollaries, both paid for:

- **Light the RIM, not the middle.** A dark disc with a lighter interior is a donut, not
  a shield. One lit arc on the upper-left edge and a small dark boss.
- **Mullions must not cross the goods.** Three mullions across 25px of glass sliced every
  object into two or three pieces — physically correct, visually a tangle. **One mullion,
  two panes, one object each**: the pane is the frame the silhouette needs.
- A **10px device** is a table, not a formula. The two things that make the Brass Fang a
  tooth and not a pennant are both local: the crown is widest **two rows down** and
  pinches back in above it, and the last three rows **curve**, so the point is offset
  from the root. A smooth `(1-u)^k` taper from the top row is a pennant, which is exactly
  what it shipped as first.

## ONLY 100px OF A BUILDING IS EVER SEEN (2026-07-30)

The camera is y-centred on the body over a 216-tall viewport, so it shows **108px above
the player**, and a player standing at a door is ~8px south of the building's base line.
**108 − 8 = 100.** Backing away does not help: the camera backs away with you. So on any
building in this game, art above `base_y − 100` is drawn for nobody.

**That is a rule about FURNITURE, not about SIZE.** The Academy keep was squashed until
its whole silhouette fit and it read as a cottage; restored to full height, with the
ridge running off the top of the frame, it reads as too big for the screen — which is
what you want out of a keep, and is how every great tree in this project already works.
What must live below the line is anything the player is meant to READ: the door, the
lit windows, a rose window, a bell, a balcony, **and every chimney cap** — a plume whose
flue is off screen is the phantom-smoke defect in the other direction. The keep's
chimneys became BREASTS running the full height of the facade for exactly that reason,
and they are worth more as depth than a ridge stack ever was.

Corollary for the old build it replaced: `town_academy`'s twin spires sat at y≈14-42 and
**were never once on screen**, which is a large part of why a building the overworld icon
promises as a castle keep read as "a flat wall with a garden on top."

## The menu of depth cues, in the order they pay (2026-07-30)

Both the Academy keep and its two wings were reported as "very flat", and the diagnosis
was the same for both: nothing overhung anything, so nothing cast a shadow on anything,
so there was no second surface for the eye to find. In descending order of how much each
buys at 384×216:

1. **A BAY STANDING PROUD** — a porch, a chimney breast, a projecting entrance — plus
   **the shadow it throws on the wall beside it** (LIGHT is NW, so the shadow goes east).
   One object demonstrably in front of another beats any amount of surface texture.
2. **A DEEP EAVE AND ITS SHADE BAND.** An eave that does not darken the wall under it is
   not an overhang, it is a line. `_academy_props._shade_band` pulls whatever is already
   drawn in a rect two steps down whichever of the known ramps it came from.
3. **PANELS, NOT A FABRIC.** Half-timbering (`_timber_wall`) turns one plane into a grid
   of small planes each with a lit top edge and a shadow under the rail above it. Braces
   spring **UP and OUT** from the foot of a post; drawn the other way they read as rope
   swags and the hall comes out with bunting on it.
4. **STEPPED BUTTRESSES at the corners** — they break the silhouette, so the building
   stops being a rectangle before you have read a single detail.
5. **HOODS AND SILLS** on every opening, so glass sits in a hole rather than on a surface.
6. A pitched roof with **verge boards, a ridge cap, and a dark butt line per shake
   course**, instead of a flat band.

## THREE WAYS TO SHIP NOTHING AT ALL (2026-07-30)

All three render, dedupe and pass every lint that was looking at the time. Two of them
put the user's ORIGINAL bug back while claiming to fix it.

- **`Sprite.rect` on an INVERTED range draws nothing, and says nothing.** The
  still-house's rebuilt flues were `_chimney(up, fx, 12, base - 12)` with `base = 22`,
  i.e. `y1 = 10 < y0 = 12`: **eight pixels** of rain cap, no shaft under it, while
  `_wing_anim` went on faithfully smoking from the same coordinate. That is smoke with
  no chimney — the exact complaint the change existed to fix. `_academy_props._flue`
  now asserts `y1 > y0`, because a flue is one of the few things in that file with a
  shape it MUST have.
- **A HIPPED ROOF LEAVES ITS FOOTPRINT'S BACK CORNERS EMPTY.** A trapezoid narrowing to
  a short ridge is the correct drawing of a hip and the wrong building: measured 0%, 0%,
  6% and 9% coverage across the wing block's top row, which is an **invisible wall** —
  a solid cell rendering plain grass beside walkable grass. A long hall's ridge runs the
  length of the building anyway, so drawing it as a **gable, full width, verge boards at
  each end** is both the fix and the better architecture.
- **A PLINTH RUN TO THE CANVAS EDGE WALKS OFF THE BUILDING.** The keep's art is 26 cells
  wide over 22 cells of collision; `_ashlar(sp, 0, …, W - 1, …)` laid 32px of dressed
  footing across open lawn at each end and stopped in a hard vertical cut. **Only the
  perforated crowns may use a sprite's overhang** — that is what an overhang is for.

**And the reason all three survived: the map was not in `_check_art.py`'s tables.** It
was added to `MAPS` and `PROPS` mid-pass and caught the roof one on the very first run;
it was still missing from `TILED` and `PLACEMENTS`, so "layout dims match the map",
"atlas refs in range" and ".tres declares every tile" — the three that catch a footprint
change that was not regenerated — were also dark. **A new map goes into all four tables
in the commit that creates it.**

## Two more silent traps (2026-07-30)

- **A LIT PANE WITH A 2-ON-2-OFF THROW BAND DOWN ITS WHOLE HEIGHT IS AN ORANGE
  BARCODE** — the most candy-coloured thing in a scene, and squarely in the "very kiddy"
  failure mode. Firelight falls off: confine the throw to the pane's **top third** the
  way `_tree_props._hearth_window` already does, and give the glass sparse dark leaded
  bars instead. `_breathe` matches `WARM`/`WARMD` by VALUE, so the hearth breath is
  unaffected either way.
- **`Sprite.tri` decides "ramp or flat colour" with `isinstance(x, list)`.** Hand it a
  hand-pinned ramp declared as a TUPLE of tuples and it stores the whole ramp as one
  pixel; the failure surfaces hundreds of lines away in the PNG writer as
  `TypeError: 'tuple' object cannot be interpreted as an integer`. Declare hand ramps as
  **lists**. (`ball`/`capsule` go through `tone()` and index fine either way, which is
  what makes this intermittent.)
- **A map that is not in `_check_art.py`'s `MAPS` table is not passing — it is ABSENT,
  and the summary still prints "all checks passed".** `assets/maps/academy.txt` — a
  64×48 map with six Tier-3 props — was never in it. Adding it found a real hole in the
  first run: the south border was open lawn from edge to edge and a body could walk off
  the bottom of the map. **Add a new map to `MAPS` and `PROPS` in the same commit that
  creates it.**

## A CANVAS IS SIZED TO ITS MASS, NEVER THE MASS TO ITS CANVAS (2026-08-02)

Every great tree in Alembic Town had a **FLAT TOP**. Reported as "the top of the trees
are cropped in a bunch of weird ways", and that is exactly what it was: `great_crown`'s
lobe tables were laid out against a 224×128 channel and spilled ~21px past the top, ~8
left, ~11 right and ~10 below — and **`Sprite.set` discards out-of-range pixels
silently**, so every one of those came back as a ruler-straight cut. Measured on the
shipped PNG: a **123px flat cut across the top of the dome**, 38 and 46px down the
sides, 84 across the hem. `edge()` cannot outline a silhouette with no empty pixel
beside it, so the cuts had no outline either — a tree in a box, dead centre of screen,
with forest still visible above the cut.

- **The generator knows its own extents, so it should allocate its own canvas.** Hoist
  the ellipse/limb tables above the `S(...)` call, take the union of their bounds, size
  the canvas to fit with a 2px margin (1 for `edge()`, 1 spare), and draw through a
  `PX()`/`PY()` pair that maps channel coordinates into the padded canvas. Nothing about
  the authored look changes — only the parts that were never being drawn appear.
- **Hand the pads back, because only the caller can place them.** `great_crown` returns
  `(sp, pad_x, pad_t, pad_b)`. `pad_x` must be the **max of the two sides, not one
  each**: `PropSpawner` centres a prop on its footprint's x, so an asymmetric canvas
  slides the whole crown sideways off its own trunk.
- **`anchor=top:` is SIGNED**, and a negative value is how art hangs above its footprint.
  `prop_spawner.gd` used `-1` as its "unset" sentinel and silently bottom-anchored
  anything negative; it carries an explicit `has_top` flag now. `_check_art.py` already
  handled a signed `top`.
- **ANCHOR A CROWN BY ITS HEM, NOT BY ITS HEAD.** The two vertical pads do not cost the
  same. Hung from the channel's top row (`top=-pad_t`) the whole mass drops by `pad_b`
  and the leaf hem swallows **the arch of the door in the trunk** — measured, and the
  door is the one thing on a great tree the player has to read. Hung by the hem
  (`top=-(pad_t + pad_b)`) everything from the deck down is pixel-for-pixel where it
  always was and the growth all goes UP into the dome, which is the half that was
  missing. Alembic's northernmost tree now runs off the top of the map, where
  `limit_top = 0` cuts it at the **screen** edge — which reads as scale, not as damage.
  That is the whole difference: a cut at the frame border is the Academy's own doctrine,
  a cut floating mid-picture is a bug.
- **The fix moves the wall up one level — check the caller's canvas too.** The Academy
  blits its crowns INTO `academy_keep`'s sprite, so widening the crown just moved the
  flat vertical cut onto the keep's own canvas edge, over open lawn. The keep now
  computes its crowns **first** (step 0), derives `PAD` from the margin they report, and
  every x in the builder is written `PAD + <building coordinate>` — so the building's
  own numbers stay the numbers they were designed as and only the canvas grows (416 →
  464 wide, still centred, so nothing moves in the world). `_keep_anim` became a
  **closure over `PAD`** for the same reason `_wing_anim` is one: a smoke plume that
  does not move with its chimney is this file's oldest bug.
- **Assert it, don't lint it.** A crown that overflows renders, dedupes and passes every
  check in `_check_art.py`. A border-pixel assert at the end of the builder is the
  cheap, local guard, and a lint over prop PNGs can't have it — buildings, curtains and
  trunk shafts legitimately run to their canvas edge, so the allowlist would be most of
  the file. The rule only binds art with an **organic silhouette**.

## Color law (the gotchas that cost real bugs)

- `ramp()` hue-shifts darks toward violet. That law turns an orange seed RED, so:
  **`BRASS[2..3]` are unusable** — brass is tones 0/1 only, darks are IRON. Anything
  incandescent (lava, fire) needs a hand-pinned ramp.
  - The exact values, so you stop re-deriving them: `BRASS` is `[(242,223,167),
    (240,188,98), (246,28,26), (216,0,109)]`. Tones 2 and 3 are **pure red** and
    **magenta**. `COPPER` is the same story from tone 3 down.
  - **Anything ROUND needs more than two tones, so use `BRASSD`** (`_tilekit.py`,
    hand-pinned warm darks — the SACKR precedent). Two tones are fine for a hinge or a
    stud; a shaded ball is not. Alembic's fountain finial is an alembic bulb and it
    spent its life as a **magenta blob on a stone plinth** for exactly this reason,
    in the middle of the square.
  - **It bit five more times in the Academy alone** (2026-07-30, all reported by the
    user as "the buildings look flat / that's red"): the observatory's dome (`COPPER`
    → a TAN AND RED MUSHROOM), the still-house's boiler (a wine barrel), the orrery's
    brass sun (`BRASS[2]` = pure red — a red bead), its founder's plate
    (`COPPER[3..4]` = red and magenta, the loudest thing in the court), and the keep's
    whole timber frame (`TIMBER[3..5]` are brick, plum, plum — a RED hall). Fixed with
    five hand-pinned ramps in `_academy_props.py`: `OAK` / `SHAKE` / `DAUB` / `VERDI` /
    `COPPERD`. **VERDI is the one to copy**: copper left out for two hundred years IS
    green, so the palette fix and the fiction were the same fix.
- **The 2026-08-01 sweep fixed the exterior half of this family**: `_town_props`'
    lamp cage, pipes (`_pv`/`_ph`), `_valve`, the stall glint and the cabin stoop
    lantern, plus `_overworld_props._chimney`, all moved to `BRASSD`/`COPPERD` —
    and **`COPPERD` now lives in `_tilekit` beside `BRASSD`** (promoted from
    `_academy_props`, which re-imports it; `_flue` is now just its inverted-rect
    assert plus a delegate to the fixed `_chimney`). Scenes pick the fixes up at
    their next regen — town/fest/academy/lanternwood are regenerated; **the
    overworld's landmark chimneys are not yet**. **The rule is still broken in
    ~20 places in `_interior_props.py`** (interiors were not in the sweep's
    scope): hooks, spouts and screw heads in `BRASS[2..3]` / `COPPER[3..5]` are
    still drawing red and magenta there — check before copying any brass idiom
    out of that file.
- Hand-pin anything the ramp would ruin (the bindle's warm burlap `SACKR` and wood
  `STICKR`).
- **A white paw on a white cheek vanishes** without a shadow tint.
- Palette doctrine: every scene is a MINIMAL duo/tri-tone cast — hue field + hot accent,
  violet/teal shadows. Wood may be honest warm brown. **Never a beige/gray mud field,
  never muddy un-hue-shifted darks.**
- **Additive vs MIX:** cream at ~250 added onto a saturated field saturates every
  channel and arrives white. The recital fireworks are MIX, not the additive magic-mote
  idiom, because *which colour it is* is the beat. Canvas MUL blend darkens through
  transparent texels — use MIX.
- **The glow overlay renders UNDER the y-sorted World**, so a building's light must land
  on the ground at its feet as ONE continuous wash — spaced per-aperture dabs scallop
  the ground into circles.
- The cloud-shadow shade overlay was **cut** — dark ovals read as smudges at CT zoom.

## Prop drawing gotchas

- Landmark props (`_overworld_props.py`) are one-off and never deduped, so they use full
  per-pixel Sprite shading: `tone()` lambert roofs, `_coursed_wall` masonry, `_hatch_px`
  linework, `cluster_shade` finishing.
- `_arch_rows` springs off the **CROWN, never the sill** — keyed to the sill, a tall
  window loses its whole head.
- A cupola is drawn **DOWN from the canvas top** — the pad rows belong to the smoke, so
  a finial at negative y clips.
- `bake_shadow(..., each=True)` for any shared-char prop SET — a merged bbox smears the
  band across the aisle (the hall's four benches).
- Drawing order matters: sleeve/paw first, stick last. A sleeve drawn after the stick
  covers it.
- A `Sprite2D`'s `offset` moves only its OWN texture — a pinned child stays planted
  while the parent's art climbs. Give both the same offset.
- `scale` multiplies a `Sprite2D`'s `offset` too — divide the lift by the scale.

## Where the art lints live

`python3 assets/_check_art.py` fails the build on: floating upper art, uncapped
walk-behind corridors, misplaced ridge cells, an empty upper layer, a bad prop manifest,
and the invisible-wall case. The rules it enforces are authoring rules — see the
**map-authoring** skill.

To eyeball a scene without launching the game, see the **probes-and-shots** skill
(`tools/shot.gd`).
