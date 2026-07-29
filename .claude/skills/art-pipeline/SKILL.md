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
  - **kid Basil, 6×5** — row 4 is `sleep` / `wake` / `sigh`. Kid-only.
  - **adult Basil, 6×10** — row 8 is `look_watch` / `sit` / `bow_head` / `knapsack` + a
    2-frame trudge; row 9 is `knapsack_back` (the south-gate look-back), cols 1-2
    `defeat_walk` (the head-down hall walk of shame), cols 3-5 `knapsack_down` + the
    2-frame `knapsack_walk_down` (the gate exit walking INTO the camera — the old
    side-profile walk tweened south read as a sideways glide). Adult-only.
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
- NPC sheets are one-row 48px; `frame_cols` gates optional facings (`back`/`side` are
  built only when `frame_cols` >= 8/10). A new villager is a PNG + exports.
- **Never `play_emote` a back-turned head** — it flips to a front face.

## Color law (the gotchas that cost real bugs)

- `ramp()` hue-shifts darks toward violet. That law turns an orange seed RED, so:
  **`BRASS[2..3]` are unusable** — brass is tones 0/1 only, darks are IRON. Anything
  incandescent (lava, fire) needs a hand-pinned ramp.
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
