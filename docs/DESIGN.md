# Professor Poopy Paws — Design Bible

> Canonical, tool-agnostic design doc. `CLAUDE.md` and `AGENTS.md` point here so any AI
> assistant (Claude Code, Cursor, Copilot, etc.) shares the same source of truth.

Tone is a blend of **Adventure Time** (whimsical, absurd, heartfelt) and **Final Fantasy** (earnest
stakes, party/progression depth, emotional arcs).

Structure in one line: **Chrono Trigger / Sea of Stars overworld for travel; zones
play as an ALttP-style top-down shooter (laser gun) — not turn-based.**

## Story Outline

- Protagonist: a brilliant **science cat** living in a magical world.
- Inciting humiliation: on the morning of an important lecture he oversleeps and rushes
  out. **Schweinler** — a smug pig, his academic rival and bully — has left a bag of
  poop outside his door; he steps in it. Mid-lecture Schweinler calls it out publicly
  and brands him **"Professor Poopy Paws"** — the name sticks and becomes the name of
  the game.
- Loss: later that same day, his girlfriend is hit by a car.
- Retreat: devastated, the cat becomes a reclusive hermit.
- Catalyzing event: all magic is removed/drained from the world.
- Call to adventure: Little brown librarian cat called Fuji who goes to the library to try and figure out how to bring magic back and reads an old paper by Basil and sets out to find him.
- Arc: through a series of adventures he restores the world's magic, saves the world,
  grows past his humiliation, and finds love again with Fuji.

## Themes

Humiliation → isolation → being seen by others → growth → redemption and renewed love.
Magic as a metaphor for hope/connection returning to the protagonist and the world.

## Influences

- **Adventure Time:** surreal biomes, oddball NPCs, comedic-but-sincere writing.
- **Final Fantasy:** progression systems, emotional storytelling, eventual party members
  (the sympathizers), set-piece dungeons.
- **Zelda: ALttP:** zone gameplay — top-down 4-directional action combat, dungeons,
  items as gating tools.
- **Chrono Trigger / Sea of Stars:** the **overworld** — a miniature painted continent
  walked by a tiny chibi travel sprite (~32 px tall on 32×32 terrain tiles) between
  full-scale places. Their turn-based combat is **not** adopted; zones stay an
  ALttP-style top-down shooter.
- **Secret of Mana:** the closest gameplay cousin — real-time top-down action combat
  inside a lush 16-bit JRPG shell. Reference for how zones should _feel_: saturated
  organic terrain, big readable sprites, action combat that stays friendly, whimsical
  enemies with personality, and the seamless flow between exploring and fighting.
- **Art direction** (canonical influence list): **Final Fantasy VI, Chrono Trigger,
  Secret of Mana, Sea of Stars, Adventure Time, and the Paper Girls comic.** Gameplay
  feels like Zelda, but the _look_ is richer 16-bit JRPG: **TRUE SNES density**
  (see Tech Conventions) — big deliberate CT-chunk pixels, ~24×13.5 tiles on
  screen, characters ~2 tiles tall like CT/SoM. FF6/CT field-sprite proportions
  (head/torso/legs roughly thirds), shading ramps and per-material outlines over flat
  fills, textured tiles, bitmap-font dialog boxes — with Adventure Time's whimsy in
  character/creature design and **Paper Girls' color law everywhere** (see "Palette
  Registry"): palettes stay MINIMAL and surreal — duo/tri-tone casts, one dominant
  hue field plus one hot accent, shadows hue-shift violet or teal (never neutral
  gray). Wood may be an honest warm brown (a material, not the field); the ban is
  on naturalistic beige/gray mud as a scene's whole field and on un-hue-shifted
  muddy darks.

**World genre: steampunk-inflected medieval fantasy.** The world is a
Zelda-ALttP-style kingdom — cottages, bluffs, stone-and-timber architecture, a
walkable overworld between named places — layered with an alchemical /
Victorian-inventor technology strand carried by Basil and his world's
trappings: gears, brass fittings, glass apparatus, lanterns, laser-gun
gadgetry, corkboard research. It's already in the lore's own naming (Alembic
Town — an alembic is distillation apparatus) and in Basil's design (goggles,
lab coat, beaker magazines). Future locations, NPCs and props should lean into
this pairing — brass-and-flask over chrome, candle-and-gear over circuitry —
never modern tech or generic-fantasy defaults.

## World Structure — Overworld + Zones

Two layers:

- **Overworld** (`scene/overworld.tscn`) — the travel layer: a Chrono Trigger /
  Sea of Stars–style miniature painted continent (64×36 tiles, 1024×576 px,
  camera-clamped). Basil walks it as a 24×24-cell chibi sprite (~16 px tall) over
  16×16 terrain tiles. **No combat on the map.** Terrain gates travel — water,
  forest, mountains, rivers, cliffs and dead trees are solid; sand, grass, paths,
  bridges, forest edges, hills and the wastes are walkable; bridges and paths open
  the routes. The eastern drained wastes render **hot violet-magenta** — the
  magic-drained premise carried by color.
- **Zones** — the full-scale scenes entered from the map, where the existing
  gameplay happens: 48×48-cell field sprites, SNES-Zelda ALttP-style movement, and
  the top-down laser-gun shooter combat.

**Location markers** (`Area2D`, `scene/overworld_location.gd`) carry
`id / display_name / target_scene / locked_text`. Walking onto one shows its name in
a banner label; unlocked markers fade out and enter their zone; locked ones show
flavor text instead. The **`Game` autoload** (`scene/game.gd`) remembers
`overworld_spawn`, so leaving a zone returns Basil to the marker he entered from.

**Geography:** home bluff SW → path NE past Whisker Meadow (center-west) → bridge
over a N→S river → Alembic Town at the NE forest's edge; mountains + cave N; drained
wastes + obelisk E/SE; ocean frames everything.

- **BASIL'S BLUFF** (`home` → `house.tscn`) — Basil's hermit home; the playable
  attic bedroom, and where the game boots.
- **WHISKER MEADOW** (`meadow` → `meadow.tscn`) — the first field zone; the one
  playable combat zone today.
- **ALEMBIC TOWN** (design only) — home of the Academy and the humiliation; future
  hub.
- **THE BURROWS** (design only) — future dungeon.
- **THE DRAIN** (design only) — drained-wastes story hook: where the magic went.

The three design-only locations lost their map markers in the 2026-07 combat-first
cut; their painted landmarks remain on the continent, and markers return when the
zones exist.

The cracked/dead-tree/crystal **wastes biome** (east) visually encodes the
drained-magic premise. New regions and zones unlock as the story progresses; the
gating tools are terrain plus story keys.

## Tech / Engine Conventions

- Engine: **Godot 4.6**, GDScript, GL Compatibility renderer.
- Base resolution: **384×216** (16:9 — canvas_items stretch, integer-scales 5x to
  1920×1080 / 10x to 4K so it fills a widescreen TV; the dev window runs 3x at
  1152×648; `snap_2d_transforms_to_pixel` on). Nearest filtering. No camera zoom
  anywhere — on-screen scale is purely sprite pixels vs. the viewport. (The
  2026-07 zoom-out from 320×180: same sprites, ~20% more world on screen, Basil
  reads ~15% of frame height instead of 18%.)
- **TRUE SNES DENSITY** (the 2026-07 CT-chunk restart): pixels are big and
  deliberate, Chrono Trigger scale — the earlier "SNES composition at 2x pixel
  density" was reversed because fine detail read as noise, not craft.
- **Scale Table** (canonical; mirrored by `assets/_core.py` constants — change them
  together):

  | Thing                            | Size                                                                                     |
  | -------------------------------- | ---------------------------------------------------------------------------------------- |
  | Viewport                         | 384×216 (16:9; 5x → 1920×1080)                                                           |
  | Terrain tile (zones + overworld) | **16×16** (`ZONE_TILE`/`OW_TILE`)                                                        |
  | Zone character cell (Basil)      | **48×48** (`ZONE_CELL`), figure ~33 px, feet y=44 (`ZONE_FEET`)                          |
  | Slime cell                       | 24×24                                                                                    |
  | Overworld chibi cell             | **24×24** (`OW_CELL`), ~16 px figure, feet y=21 (`OW_FEET`)                              |
  | Overworld landmark icon          | 32×32 (`ICON`)                                                                           |
  | Interior room map (house)        | 24×14 tiles = 384×224 (view clamps to 384×216; bottom void row is mostly offscreen)      |
  | HUD heart / ammo pip / font_size | 16 / 8 / 8                                                                               |
  | Gun muzzle offset (art contract) | 16 px from origin (`player.gd muzzle_offset`)                                            |

  This puts ~24×13.5 tiles on screen with characters ~2 tiles tall — the CT/Frog
  read where a character is a big chunky figure and every pixel is placed on
  purpose, with enough room around him for the world to breathe.

- Architecture: **component-based**. Reusable behavior lives in `components/` as nodes/
  resources (HealthComponent, HitboxComponent, HurtboxComponent, …). Entities in
  `entities/` compose these. Shared data (stats, items) as custom `Resource`s in
  `resources/`. Playable rooms/levels in `scene/`. Art/audio in `assets/`.
- Movement: `CharacterBody2D`, 8-way movement with 4-way facing (fires in the facing
  direction), ALttP-style.
- Combat: a **laser gun** with limited charges. Firing spawns a `LaserBolt` projectile
  (`Area2D`) that travels and damages the first `HurtboxComponent` it hits. Always-on
  `HitboxComponent`s (e.g. an enemy body) handle contact damage. All damage flows
  through `HealthComponent`. Single shot per `attack` press.
- **Ammo / beakers:** the gun holds `max_ammo` charges; each shot consumes one. **Beakers
  are magazines**: pickups (`entities/pickups/beaker.tscn`) pocket as spares (up to
  `max_beakers`; full paws leave the pickup in the world), and reloading — R/L, or pulling
  the trigger dry — plays the planted pour animation and empties one into the gun. The HUD
  shows hearts + an ammo-pip row.
- **Magic is deferred by design:** the world starts drained, so spell systems are
  introduced later as progression that mirrors the story. The laser gun is the
  early-game, magic-free weapon.

## Current Milestone — Combat Core (house · overworld · meadow)

**The 2026-07 combat-first cut** pared the build to its core loop to hone the
battling and the look. Deleted (git history keeps the implementations; the story
sections above remain the plan): the title screen, the five-part intro (night
yard → bedroom wake-up → morning yard → playable road → lecture hall),
Schweinler's sprites, and the cutscene/dialog kit (`cutscene.gd`,
`dialog_box.gd/.tscn` — awaitable say/walk/fade/card helpers, typewriter box).

Flow: **bedroom ↔ downstairs ↔ overworld ↔ Whisker Meadow**. The game boots
into the loft bedroom; its stairs descend to the downstairs great room, whose
front door opens onto the overworld at the home marker (and entering from the
map lands back at that front door).

- **House** (`scene/house.tscn`, main scene): Basil's LOFT bedroom as a TILED
  room (the CT-bedroom treatment) — a SMALL dense diorama floating in a huge
  black void (the room is only 10 tiles wide on the 24×14 map, ~7-tile side
  margins; dormer window bay jutting above the cornice; every wall stretch
  occupied: cork | window | shelf), warm brown plank walls over a teal weave
  floor.
  `assets/_gen_tileset_house.py` reads the feature chars in
  `assets/maps/house.txt` (window, bookshelf, corkboard, bed, desk, chair,
  bucket, railing) and AUTHORS a real tile library: 16-periodic fabric
  painters (weave/planks) whose repeated cells are byte-identical and so
  collapse to single atlas tiles, whole-tile light variants for the dawn
  window's hard-edged pool (lit core / ordered-dither fringe / shadow band —
  never per-pixel gradients), and furniture painted once inside its map
  footprint as crisp multi-tile objects (blazing gold dawn glass, hot-magenta
  quilt, research desk with oil lamp + microscope, corkboard with red string).
  Visible tiles and collision are both built at runtime from the same map
  file. **Scene lighting** (runtime, over the tiles): a violet-biased
  `CanvasModulate` dims the whole room (Basil included, the CT interior
  read) — darker while the curtains are drawn; `house_glow.png` — a
  hard-banded ADDITIVE beam the generator aims from the map's window cells
  over the pool — draws UNDER entities (additive light over a sprite lifts
  its darks and reads as transparency; sprites stay crisp, like CT). The
  **curtain mechanic** (`house.gd`): the room wakes with the curtains drawn
  (`house_curtains.png` closed/half frames, flasks redrawn in front of the
  drapes, a hot sliver of dawn leaking between the panels); standing at the
  window (WindowZone) and pressing **interact (E)** slides them open/closed,
  tweening the beam and the dim with it. The south boundary is a **CT
  staircase in the south-west corner**:
  Basil passes the rail gap (balustrade + newel posts on the upper tile
  layer, so he walks BEHIND them) onto visible treads that descend south out
  of the room silhouette between dark jambs, each step darker until the void
  swallows it — landing in the downstairs at `stair_arrival`.
- **Downstairs** (`scene/downstairs.tscn`): the ground-floor **kitchen + lab
  great room** — the steampunk-medieval genre statement in one room, and the
  hub between bed and world. Twice the loft's width (a 20-tile room on the
  same 24×14 map, ~2-tile void margins, one fixed screen), same authored-tile
  pipeline (`assets/_gen_tileset_downstairs.py`, slate flagstone floor +
  shared house planks). KITCHEN west: stone hearth with a live hard-banded
  fire (the room's hot light source — whole lit-flag tiles + additive
  `downstairs_glow.png` drawn under entities), counter with bread/bowl/
  bottle, brass-latched icebox. STEAMPUNK LAB east: flask shelf, riveted
  copper boiler (gauge, pipe to the cornice, glowing grate), workbench with
  a half-built gizmo. The loft staircase descends through a top-center
  alcove jutting above the cornice (treads brighten as they come down out of
  the dark); the south wall holds the **front door** — an open doorway
  spilling daylight, lintel on the upper layer (Basil ducks under it), stone
  stoop into the void. Exits: up the alcove → bedroom (`stair_top`); out the
  door → overworld home marker. Spawns route through `Game.interior_spawn`
  (read-and-clear; default = `front_door`, the overworld-entry landing).
- **Overworld** (`overworld.tscn`): the CT/SoS travel map (see "World Structure").
  Two live markers: Basil's Bluff enters the house at the downstairs front
  door, Whisker Meadow enters the
  combat zone. The continent still paints the future landmarks (town, cave,
  obelisk); their markers return when those zones exist.
- **Meadow — Whisker Meadow** (`scene/meadow.tscn`): 48×24-tile painted zone,
  4 slimes, beaker respawns, HUD; a south hedge-gap exit returns to the overworld
  at the meadow marker.

Feel: the bolt leaves the INSTANT the trigger is pulled (no wind-up — the shoot
anim starts on the muzzle frame), laser bolt (2 dmg; slimes have 4 HP → two
shots, and each kill respawns a slime elsewhere in the meadow), firing
**recoil-shoves**
Basil hard backward — the sheet's recoil frame leans him back, feet braced forward,
ears pinned, eyes squeezed in a wince, barrel kicked up; hop jumps straight up when
standing, leaps with held direction, and is **steerable mid-air** (SNES-Zelda style).

All art is **generated, frame-consistent pixel art** (see "Art pipeline") so animations
actually cycle; hand-drawn sheets can still drop in later against "Asset Specs" below.

### Slice file map

- `components/health_component.gd`, `hitbox_component.gd`, `hurtbox_component.gd`
- `entities/player/player.gd` + `player.tscn` (+ `player_frames.tres`)
- `entities/enemies/slime.gd` + `slime.tscn` (+ `slime_frames.tres`)
- `entities/projectiles/laser_bolt.gd/.tscn`, `muzzle_flash.gd/.tscn`
- `entities/pickups/beaker.gd` + `beaker.tscn`
- `scene/hud.gd/.tscn`
- `scene/house.gd/.tscn` — the playable bedroom: tiled-interior reference
  implementation (Tiles → Collision → y-sorted World), visible tiles from the
  generated layout + collision from `assets/maps/house.txt`, south-door exit
- `scene/meadow.gd/.tscn` — the combat zone; the painted-scene reference
  implementation (Ground → Collision → y-sorted World → Overlay)
- `scene/map_data.gd` (map-file loader — keep in sync with `assets/_maps.py`) ·
  `scene/painted_map.gd` (stamps the invisible collision tiles at runtime) ·
  `scene/tiled_map.gd` (stamps visible tiles from a generated layout file)
- `scene/overworld.gd/.tscn` (64×36 painted continent) ·
  `scene/overworld_location.gd` (markers: id/display_name/target_scene/locked_text) ·
  `scene/game.gd` (autoload **Game** — remembers `overworld_spawn`, plus
  `interior_spawn`: the map anchor the next interior scene spawns at,
  read-and-cleared by the interior's `_ready` so "" = its default entry)
- `entities/player/overworld_player.gd/.tscn` (+ `overworld_basil_frames.tres`) —
  travel-only `CharacterBody2D`: 8-way move, 4-way facing, ~180 px/s, no gun/hop/health
- `assets/font/pixel_font.fnt/.png` — bitmap font all Labels use
  (`assets/font/_gen_font.py`, glyphs shared via `assets/_pixfont.py`)

### Art pipeline (generated, frame-consistent, palette-locked)

The AI-generated sheets (`assets/basil.png`, `assets/basil_sheet.png`) draw a slightly
different cat in every frame, so animations strobe; they are kept only as concept
reference. The live art is drawn procedurally by stdlib-only Python scripts.

**Two scene pipelines, one map format.** Exterior maps are PAINTED: one composed
ground painting plus one overlay painting, no per-tile texture anywhere, the
16px grid surviving only as collision/logic data. Interiors are TILED (the
2026-07 CT-bedroom pivot, house first; reworked 2026-07 from paint-then-slice
to AUTHORED tiles): the generator composes the room from 16-periodic fabric
functions + whole-tile light variants + footprint-bounded furniture painters,
so repeated cells are byte-identical BY CONSTRUCTION and the slicer collapses
them to a small atlas — one-off art (window, furniture) keeps unique tiles,
exactly how an SNES room lives in VRAM (the house: ~67 tiles from 336 cells).
Both pipelines are driven by the same `assets/maps/*.txt` file per scene.

- **`assets/maps/*.txt`** — the shared source of truth per map: a `legend`
  (char → terrain + walk/solid), named `anchor`s (spawns, exits), and the ASCII
  tile grid. Python paints from it; `scene/map_data.gd` builds collision and
  logic queries from the same file, so paint and physics cannot drift. Keep
  `assets/_maps.py` and `scene/map_data.gd` parsers in sync.
- **`assets/_core.py`** — canonical scale constants (`ZONE_TILE=16`,
  `ZONE_CELL=48`, `ZONE_FEET=44`, `OW_CELL=24`, `ICON=32` — the Scale Table above
  mirrors these), `h2()` deterministic hash noise, `pick()` ramp dither, `Img`
  canvas, PNG writer.
- **`assets/_paint.py`** — the scene-painting kit: `fbm()` scene-scale noise
  fields (texture never repeats on any tile rhythm), `sdf_from_mask()` blurred
  signed-distance fields whose warped zero-contours turn blocky tile regions into
  organic boundaries, `curve_field()` spline distance for genuinely curved trails
  (walkable-on-walkable paint is free of the grid entirely), `tone()`
  cluster-jittered ramp quantization (organic clumps, never checkerboard),
  `Painter` (per-map canvases, palette, memoized SDFs, scatter), `paint_canopy()`
  tree-mass walls, and stamps (flowers, tufts, pebbles, boulders, sparkles).
  **Tolerance rules baked in:** boundary warp ≤ 6px and solid paint may only
  overfill outward, so collision (full-square tiles on solid cells) never lets a
  body stand on water/canopy; canopy pixels deeper than `OVERLAY_DEPTH` (26px)
  into a solid region go to the overlay image (drawn above entities), the fringe
  stays on ground — sprites can't reach deeper than that, so occlusion can't go
  wrong.
- **`assets/_palette.py`** — the color script as data. `ramp(seed, shadow, tones)`
  derives N-tone material ramps (6 for painted terrain, 4 for sprites) from scene
  seeds, hue-shifting the dark end toward the scene's shadow bias (violet or
  teal). `SCENES` is the palette registry (below) — per-scene `"ramps"` entries
  hold hand-tuned identity ramps for materials that can't be derived (warm dirt:
  teal shadows turn it yellow-green, violet ones salmon); `ACTORS` holds the
  hand-tuned identity ramps for Basil / Schweinler / slime.
- **`assets/_tiles.py`** — the tileset kit: `slice_atlas()` cuts full-room
  compositions on the 16px grid and dedupes identical cells into ONE shared
  atlas across TWO layers — a lower canvas (under entities) and a sparse
  upper canvas (over entities: railings, furniture tops, lintels — anything a
  body walks behind). Writers emit the packed atlas PNG, the TileSet `.tres`
  (visuals only — collision stays on the invisible collision layer) and the
  layered layout txt that `scene/tiled_map.gd` stamps at runtime.
  **The tiled READ is a discipline, not a file format:** repeating art must be
  a function of tile-local coordinates + a per-cell variant hash, and light/
  shade must be quantized PER TILE (whole lit tiles + ordered-dither fringe
  tiles, per-tile vignette/halo bands) — per-pixel gradients make every tile
  unique and dissolve the tile rhythm into a painting.
- **Godot side:** a painted map scene is `Ground` (Sprite2D, the painting) →
  `Collision` (invisible TileMapLayer, `assets/collision_tileset.tres` — one
  transparent full-square physics tile stamped on every solid cell by
  `scene/painted_map.gd`) → `World` (y-sorted entities) → `Overlay` (Sprite2D,
  above entities). A tiled interior is `Tiles` (TileMapLayer, under entities)
  → `Collision` → `World` → `TilesUpper` (TileMapLayer, OVER entities — the
  walk-behind layer), both stamped by `scene/tiled_map.gd` from the generated
  layout's `layer lower` / `layer upper` sections.
  Entity/exit positions come from map anchors where practical.
  `scene/meadow.tscn` is the painted reference; `scene/house.tscn` the tiled
  reference.
- **`assets/_sprites.py`** — the sprite construction kit: `Sprite` canvas with
  steer-lit `ball`/`capsule`/`panel` volumes, cluster-jittered tone selection,
  `cluster_shade`/`despeckle`/`outline`/`crease` finishing passes, and `Rig`
  (named anchors + per-frame offsets so cycles animate as one body).
  Generators (re-run any with `python3 <script>`; then let Godot reimport, or
  `godot --headless --path . --import`; **always run `python3 assets/_check_art.py`
  after regenerating** — it asserts map enclosure/anchors, painted-scene dims,
  overlay transparency, collision tileset shape, entity placements on walkable
  cells, sheet dims and `.tres` regions):

Painted scenes (ground + overlay from `assets/maps/*.txt`):

- `assets/_gen_scene_meadow.py` → `scenes/meadow_ground/overlay.png` (768×384,
  48×24 tiles): treeline border walls, cyan pond with waterline/foam/wet-sand
  collar, spline trail ending at a cairn, lavender boulders, hot-pink flower
  drifts, violet cloud washes. ~3s.
- `assets/_gen_scene_overworld.py` → `scenes/overworld_ground/overlay.png`
  (1024×576, 64×36): the CT/FF6 continent — deepwater→shallow sea with ripple
  bands + double foam arcs, smooth-contour beach, canopy forest masses, painted
  mountain ridge with snow caps, river + rosewood bridge, crack-web violet
  wastes with dead trees and glowing crystals, worn site pads under the five
  landmark anchors. ~5s.
- `assets/_gen_collision.py` → `collision_tile.png` (16×16 transparent) for the
  shared collision tileset.

Sprites and fx (on `_sprites.py`; sheet layouts frozen against the `.tres` files):

- `assets/_gen_basil_sprites.py` → `basil_gen.png` (288×384, 48×48, 6×8): Basil —
  jet-black tuxedo, stern yellow eyes (sweet ^ ^ blink), white blaze/muzzle/paws,
  close-set ears, big rimmed aviator goggles (amber glass) up on the forehead,
  lab coat worn LONG (hem y=35, flat CT bands — paw stubs peek under it, so the
  walk reads CT-Lucca style), laser gun. CT-Frog proportions (big head); walk/
  shoot ×3 facings (up-shot holds the gun skyward past his head, muzzle on the
  16px contract), hurt ×2, blink, tail-flick, happy, sad + a 4-frame reload
  (beaker of glow-juice poured into the gun's port — plays on reload: R/L or
  a dry trigger; beakers are carried as spare mags).
- `assets/_gen_slime_sprites.py` → `slime_gen.png` (144×96, 24×24, 6×4):
  squash-stretch bounce with conserved volume and a lagging gel nucleus
  (airborne frames 2–4 — `slime.gd` syncs speed to them) + 4-frame splat death.
- `assets/_gen_overworld_actors.py` → `overworld_basil.png` (96×72, 24×24,
  4×3 chibi) + `overworld_icons.png` (160×32, five 32×32 landmark vignettes).
- `assets/_gen_fx.py` → `placeholder/`: ruby hearts 48×16, energy pips 16×8,
  laser bolt 26×8, muzzle flash 20×20, glass beaker 12×14, violet hop
  shadow 24×10.

Tiled interiors (atlas + TileSet + layout from `assets/maps/*.txt`):

- `assets/_gen_tileset_house.py` → `tilesets/house_tiles.png/.tres` +
  `tilesets/house_layout.txt`: the loft bedroom as an AUTHORED tile library —
  16-periodic fabric (warm brown plank walls, low-contrast teal basket-weave
  floor) that dedupes to single atlas tiles; whole-tile light variants (lit
  weave / dither fringe / shadow band) for the dawn window's hard pool;
  hash-placed whole-tile variety (worn floor cell, knotted plank cell — one
  atlas tile each); and furniture as footprint-bounded multi-tile objects
  (dormer gable + brass vent over the blazing quantized-dawn window with sun
  disc, skyline and flask-lined sill; corkboard obsession wall with red
  string; bookshelf with scroll + glow jar; bed with hot-magenta quilt; desk
  with oil lamp, microscope + book stack; chair; wash bucket; railed
  stairwell south whose balustrade rides the upper layer over steps sinking
  into dark). Every prop carries dark contact edges, 3-tone banding and
  single-pixel speculars; contact shadows are baked inside each footprint.
  Feature positions come from the map's feature chars — move the window in
  `maps/house.txt` and it moves in-game.
- `assets/_gen_tileset_downstairs.py` → `tilesets/downstairs_tiles.png/.tres` +
  `tilesets/downstairs_layout.txt` + `downstairs_glow.png`: the ground-floor
  great room on the same disciplines — slate flagstone fabric (16x8 running
  bond), shared house planks, whole-tile hearth light (lit flags + dither
  fringe + the additive glow overlay), and the furniture objects (stone
  hearth with hard-banded fire, counter, brass-latched icebox, flask shelf,
  riveted copper boiler with gauge + cornice pipe, workbench with half-built
  gizmo, alcove stair treads, open front doorway whose lintel rides the
  upper layer).
- `assets/font/_gen_font.py` → the BMFont all Labels use: the **native 5×7
  glyphs** from `assets/_pixfont.py` (caps/digits/punctuation) at size=8 —
  Labels use `font_size = 8`. UI text is uppercase; a lowercase set returns
  with the dialog system.
- Screenshot check: `Godot --path . --script tools/shot.gd --
res://scene/meadow.tscn /tmp/shot.png` (windowed; headless renders black).

Render style (CT-chunk): every form is a shaded volume — material ramps whose
shadows hue-shift cool, light from the upper-left. Sprites: 4-tone ramps with
**hard, flat band edges** (Sprite jitter=0 — no dither inside characters),
superellipse silhouettes, per-material 1px outlines, details that break the
silhouette (whiskers, drawn after the outline). Painted terrain: 6-tone ramps,
cluster-jittered tone quantization (organic 2px clumps, never checkerboard
fields), scene-wide light gradient + cloud shade, contact shadows grounding every
mass, and no texture element repeating on any visible 16px rhythm. Night scenes
tint through a violet-magenta `CanvasModulate` over the one daytime painting —
a single tint mechanism, never a night repaint.

### Palette Registry (the color script — `assets/_palette.py` SCENES)

Every scene keys into this table; new materials derive via
`ramp4(seed, SCENES[key]["shadow"])`. Keep every palette MINIMAL and surreal —
a duo/tri-tone cast per scene. Wood may be an honest warm brown (a material,
not the field); never a naturalistic beige/gray mud FIELD, and never
un-hue-shifted muddy darks — if a dark wants to be gray, it's lavender.
(Only `bedroom`, `downstairs`, `overworld`, and `meadow` are in the current build; the other
rows are the standing color script for scenes to come.)

| Scene key      | Dominant field                          | Hot accent                    | Shadow bias |
| -------------- | --------------------------------------- | ----------------------------- | ----------- |
| `title`        | indigo→magenta→gold posterized sunset   | leaf gold                     | violet      |
| `night_yard`   | periwinkle-violet night                 | amber lantern glow            | violet      |
| `bedroom`      | warm brown plank walls / teal weave floor | hot-magenta quilt, peach dawn | violet      |
| `downstairs`   | shared house timber / slate flag floor  | amber hearth fire, daylight door | violet   |
| `morning_yard` | peach plaster                           | magenta shingles, pink blooms | violet      |
| `road`         | minty teal + peach path                 | hot pink flowers              | teal        |
| `hall`         | plum panelling / rose floor             | chalk-mint board writing      | violet      |
| `overworld`    | teal sea + sage-teal land               | violet wastes + crystal       | teal        |
| `meadow`       | minty teal greens                       | candy hot-pink flowers        | teal        |

## Asset Specs (sprite sheets to provide)

All PNG, transparent background, **0 padding/margin between cells**, nearest-neighbor
(no anti-aliased edges). Grid is **16×16**. Style target: **Chrono Trigger's Frog
sheet** — big flat color regions, hard band edges, 1px outlines, every pixel
deliberate.

1. **Player — Professor Poopy Paws** _(highest priority)_ — **48×48 px** cells, **6
   columns**, one direction/action per row to match `player_frames.tres`:
   Walk Down (6) · Walk Up (6) · Walk Side (6, mirrored in code) · Shoot Down (4) ·
   Shoot Up (4) · Shoot Side (4) · Hurt (2) + idle-down blink + idle-side tail-flick
   - happy + sad · Reload (4, beaker pour). Full sheet **288×384**. Figure ~33 px
	 tall, feet baseline y=44, gun muzzle 16 px from cell center. The cat holds a
	 **laser gun** in the shoot rows (weapon-agnostic rows welcome — see "Future
	 Direction"). Use `assets/_gen_basil_sprites.py` (current art) as the layout
	 reference.
2. **Slime / first enemy** — **24×24 px** cells. Walk Down/Up/Side (6 each, side
   mirrored) + 4-frame death. Sheet **144×96** (matches `slime_frames.tres`).
3. **HUD hearts** — **16×16** heart, 3 frames in a horizontal strip:
   full | half | empty → **48×16**. Ammo pips: **8×8** ×2 → **16×8**.
4. **Overworld Basil (travel chibi)** — **24×24** cells, 4×3 sheet **96×72**:
   walk down / up / side ×4 (side right-facing, flipped in code). Big head, tuxedo
   cat, goggles, lab coat, feet y=21 — matches `overworld_basil_frames.tres`.
5. **Overworld landmark icons** — five **32×32** icons in a strip → **160×32**:
   HOME cottage, TOWN, MEADOW grove, CAVE mouth, OBELISK.

(Exterior terrain is painted whole-scene; interiors are generated tilesets —
see "Art pipeline". Hand-drawn interior tiles would replace a generated
`tilesets/<name>_tiles.png` atlas in place.)

> Prefer a different layout (e.g. Aseprite export with tags)? Send it plus the frame
> tags and the slice will be re-sliced to match. The dimensions above are the defaults
> the code assumes (and what `assets/_check_art.py` asserts).

## Future Direction — Combat & Party (recorded 2026-07, not yet in scope)

The target feel is **Secret of Mana, but snappier**: real-time top-down action that
stays friendly, with crisp fire/recover cadence, hit-pause, and readable knockback.

- **Weapon variety** — the laser gun is the first of several blaster-type weapons;
  each should differ in arc/range/rate/knockback the way SoM's weapon families did.
  The 48×48 cells and 4-frame shoot rows are sized so alternate weapons swap into
  the same animation contract (`shoot_down/up/side` + `muzzle_offset`).
- **3-person party** — the sympathizers (starting with **Fuji**, the librarian cat
  who pulls Basil back into the world) eventually join as party members, SoM-style:
  same 48 px sprite spec, composing the same Health/Hurtbox components, AI-followed
  with leader switching. Party UI stacks additional heart rows.
- **Magic returns late** — spell systems unlock as the story restores magic; the
  drained world is why early combat is all blasters.
- ~~**The downstairs**~~ — **BUILT (2026-07-04).** The kitchen + lab great
  room now sits between the loft and the overworld (see "House" above);
  leaving home routes bedroom → stairs → downstairs → front door → overworld.
  Remaining downstairs ideas for later: cooking/eating at the hearth,
  crafting at the workbench, the boiler as a story prop (the last machine
  still running on drained-world power).
