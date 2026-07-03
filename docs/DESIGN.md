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
  feels like Zelda, but the _look_ is richer 16-bit JRPG: **SNES composition at 2x
  pixel density** — "Sea of Stars grain in an FF6 frame." The screen shows ~20x11
  tiles and characters stand ~2 tiles tall like CT/SoM, but every sprite carries
  double the pixel detail of its SNES ancestor. FF6/CT field-sprite proportions
  (head/torso/legs roughly thirds), shading ramps and per-material outlines over flat
  fills, textured tiles, bitmap-font dialog boxes — with Adventure Time's whimsy in
  character/creature design and **Paper Girls' color law everywhere** (see "Palette
  Registry"): every scene is one dominant hue field plus one hot accent, shadows
  hue-shift violet or teal, and neutral beige/brown/gray fields are forbidden.

## World Structure — Overworld + Zones

Two layers:

- **Overworld** (`scene/overworld.tscn`) — the travel layer: a Chrono Trigger /
  Sea of Stars–style miniature painted continent (64×36 tiles, 2048×1152 px,
  camera-clamped). Basil walks it as a 48×48-cell chibi sprite (~32 px tall) over
  32×32 terrain tiles. **No combat on the map.** Terrain gates travel — water,
  forest, mountains, rivers, cliffs and dead trees are solid; sand, grass, paths,
  bridges, forest edges, hills and the wastes are walkable; bridges and paths open
  the routes. The eastern drained wastes render **hot violet-magenta** — the
  magic-drained premise carried by color.
- **Zones** — the full-scale scenes entered from the map, where the existing
  gameplay happens: 96×96-cell field sprites, SNES-Zelda ALttP-style movement, and
  the top-down laser-gun shooter combat.

**Location markers** (`Area2D`, `scene/overworld_location.gd`) carry
`id / display_name / target_scene / locked_text`. Walking onto one shows its name in
a banner label; unlocked markers fade out and enter their zone; locked ones show
flavor text instead. The **`Game` autoload** (`scene/game.gd`) remembers
`overworld_spawn`, so leaving a zone returns Basil to the marker he entered from.

**Geography:** home bluff SW → path NE past Whisker Meadow (center-west) → bridge
over a N→S river → Alembic Town at the NE forest's edge; mountains + cave N; drained
wastes + obelisk E/SE; ocean frames everything.

- **BASIL'S BLUFF** (`home`, locked — "HOME. IT CAN WAIT.") — the hermit home Basil
  is leaving behind.
- **WHISKER MEADOW** (`meadow` → `test_room.tscn`) — the first field zone; the one
  playable zone today.
- **ALEMBIC TOWN** (`town`, locked — academy shut) — home of the Academy and the
  humiliation; future hub.
- **THE BURROWS** (`cave`, locked) — future dungeon.
- **THE DRAIN** (`obelisk`, locked) — drained-wastes story hook: where the magic
  went.

The cracked/dead-tree/crystal **wastes biome** (east) visually encodes the
drained-magic premise. New regions and zones unlock as the story progresses; the
gating tools are terrain plus story keys.

## Tech / Engine Conventions

- Engine: **Godot 4.6**, GDScript, GL Compatibility renderer.
- Base resolution: **640×360** (canvas_items stretch). Nearest filtering. No camera
  zoom anywhere — on-screen scale is purely sprite pixels vs. the viewport.
- **Scale Table** (canonical; mirrored by `assets/_artlib.py` constants — change them
  together):

  | Thing | Size |
  |---|---|
  | Viewport | 640×360 |
  | Terrain tile (zones + overworld) | **32×32** (`ZONE_TILE`/`OW_TILE`) |
  | Zone character cell (Basil, Schweinler) | **96×96** (`ZONE_CELL`), figure ~60–70 px, feet y=88 (`ZONE_FEET`) |
  | Slime cell | 48×48 |
  | Overworld chibi cell | **48×48** (`OW_CELL`), ~32 px figure, feet y=42 (`OW_FEET`) |
  | Overworld landmark icon | 64×64 (`ICON`) |
  | Full-screen backdrops (title, bedroom) | 640×360 |
  | HUD heart / ammo pip / font_size | 32 / 16 / 16 |
  | Gun muzzle offset (art contract) | 32 px from origin (`player.gd muzzle_offset`) |

  This puts ~20×11 tiles on screen with characters ~2 tiles tall — SNES composition —
  while the art carries 2x the pixel detail. All world speeds/offsets/collision
  shapes are 2x their pre-restart values (screen-relative feel is unchanged).
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
- **Ammo / beakers:** the gun holds `max_ammo` charges; each shot consumes one. **Beaker**
  pickups (`entities/pickups/beaker.tscn`) in the world refill ammo on walkover. The HUD
  shows hearts + an ammo-pip row.
- **Magic is deferred by design:** the world starts drained, so spell systems are
  introduced later as progression that mirrors the story. The laser gun is the
  early-game, magic-free weapon.

## Current Milestone — Vertical Slice + Opening

Flow: **title screen → intro (night yard → bedroom wake-up → morning yard → playable
road → lecture hall) → overworld → zones** (Whisker Meadow playable; the other four
places signposted).

- **Title** (`scene/title.tscn`, main scene): 640×360 Paper-Girls-style sunset — banded
  gradient sky, stars, a giant setting sun behind streaking clouds, mountain ridge,
  silhouetted autumn canopy, and Basil small on the glowing path. Falling leaves.
  Fire/accept starts the intro; ESC skips straight to the overworld.
- **Intro pt.1 — night yard** (`intro_house.tscn`): night — Schweinler sneaks up and
  plants the poop bag on Basil's doorstep, gloats, waddles off.
- **Intro pt.2 — bedroom** (`intro_bedroom.tscn`): morning — Chrono Trigger-style
  compact room floating on black. Basil asleep in bed (breathing loop), a songbird
  flaps onto the windowsill and chirps him awake; he bolts upright, close-up of the
  alarm clock frozen at **8:57** (alarm hand still at 8 — it never rang), and he
  tears out the south doorway over the doormat. Art from
  `assets/_gen_bedroom_art.py` (bedroom_bg / bed_basil / bird / nightstand /
  clock_face).
- **Intro pt.3 — morning yard** (`intro_house_morning.tscn`: instance of
  `intro_house.tscn` with `morning = true`): Basil bursts into the doorway, steps
  right in it (SQUELCH), sprints off leaving paw prints.
- **Intro pt.4 — road** (`intro_road.tscn`, _playable_): run the hedge-lined road to
  the Academy, two slimes to fight, a beaker, a fading poopy-paw-print trail, hint text.
  Reaching the Academy doors continues the story.
- **Intro pt.5 — hall** (`intro_hall.tscn`): the presentation, Schweinler's callout,
  the nickname. Title cards bridge to "…YEARS LATER." and the overworld.
- **Overworld** (`overworld.tscn`): the CT/SoS travel map (see "World Structure").
  Basil fades in at Basil's Bluff and walks the path NE; Whisker Meadow enters the
  meadow, the other markers announce themselves and show locked flavor text.
- **Meadow — Whisker Meadow** (`test_room.tscn`): 30×17-tile room, 3 slimes, beaker
  respawns, HUD; a south hedge-gap exit returns to the overworld at the meadow marker.

Feel: laser bolt (2 dmg; slimes have 6 HP → three shots), firing **recoil-shoves**
Basil hard backward — the sheet's recoil frame leans him back, feet braced forward,
ears pinned, eyes squeezed in a wince, barrel kicked up; hop jumps straight up when
standing, leaps with held direction, and is **steerable mid-air** (SNES-Zelda style).
Cutscenes are skippable with ESC.

All art is **generated, frame-consistent pixel art** (see "Art pipeline") so animations
actually cycle; hand-drawn sheets can still drop in later against "Asset Specs" below.

### Slice file map

- `components/health_component.gd`, `hitbox_component.gd`, `hurtbox_component.gd`
- `entities/player/player.gd` + `player.tscn` (+ `player_frames.tres`)
- `entities/enemies/slime.gd` + `slime.tscn` (+ `slime_frames.tres`)
- `entities/npcs/schweinler_frames.tres` (cutscene actor; sheet from
  `_gen_schweinler_sprites.py`)
- `entities/projectiles/laser_bolt.gd/.tscn`, `muzzle_flash.gd/.tscn`
- `entities/pickups/beaker.gd` + `beaker.tscn`
- `scene/hud.gd/.tscn` · `scene/dialog_box.gd/.tscn` (typewriter box, pixel font)
- `scene/cutscene.gd` — base class: awaitable `say/walk/hop/fade_in/fade_out/card`
  helpers + ESC skip. `intro_house.gd`/`intro_bedroom.gd`/`intro_hall.gd` extend it.
- `scene/title.gd/.tscn`, `intro_house` (+ `intro_house_morning.tscn` variant),
  `intro_bedroom`, `intro_road`, `intro_hall`
- `scene/test_room.gd` + `test_room.tscn` (paints an ASCII map onto a `TileMapLayer` —
  hedge tiles are solid via the tileset's physics layer; road scene uses the same trick)
- `scene/overworld.gd/.tscn` (64×36 ASCII-painted continent) ·
  `scene/overworld_location.gd` (markers: id/display_name/target_scene/locked_text) ·
  `scene/game.gd` (autoload **Game** — remembers `overworld_spawn`)
- `entities/player/overworld_player.gd/.tscn` (+ `overworld_basil_frames.tres`) —
  travel-only `CharacterBody2D`: 8-way move, 4-way facing, ~180 px/s, no gun/hop/health
- `assets/overworld_tileset.tres` — water/forest/mountain/river/cliff/dead-tree tiles
  are solid (physics layer); sand/grass/path/bridge/forest-edge/hills/wastes walkable
- `assets/font/pixel_font.fnt/.png` — 5×7 bitmap font (`assets/font/_gen_font.py`,
  glyphs shared via `assets/_pixfont.py`)

### Art pipeline (generated, frame-consistent, palette-locked)

The AI-generated sheets (`assets/basil.png`, `assets/basil_sheet.png`) draw a slightly
different cat in every frame, so animations strobe; they are kept only as concept
reference. The live art is drawn procedurally — every frame from one parametric
model — by stdlib-only Python scripts built on **two shared modules**:

- **`assets/_artlib.py`** — the rendering kit every generator imports: PNG writer,
  `h2()` deterministic value noise, `pick()` 4-tone ramp with ordered dither
  (`grain=2` dithers in 2×2 blocks so banding reads SNES-chunky at 2x density),
  `Cell` sprite canvas (superellipse `oval`, garment `cloth`, `tri`, per-material
  `outline()` pass) and dense `Img` canvas — plus the **canonical scale constants**
  (`ZONE_TILE=32`, `ZONE_CELL=96`, `ZONE_FEET=88`, `OW_CELL=48`, `ICON=64`) that the
  Scale Table above mirrors.
- **`assets/_palette.py`** — the color script as data. `ramp4(seed, shadow, spread)`
  derives every 4-tone material ramp from a scene seed, hue-shifting the dark end
  toward the scene's shadow bias (violet or teal) — sheets are palette-locked by
  construction. `SCENES` is the palette registry (below); `ACTORS` holds the
  hand-tuned identity ramps for Basil / Schweinler / slime, which travel across
  scenes (this ended Basil's old triplicated fur ramps).

Generators (re-run any with `python3 <script>`; then let Godot reimport, or
`godot --headless --path . --import`; **always run `python3 assets/_check_art.py`
after regenerating** — it asserts sheet dims, `.tres` regions, tile sizes and
physics polygons against `_artlib`'s constants):

- `assets/_gen_basil_sprites.py` → `basil_gen.png` (576×672, 96×96 cells): Basil,
  modeled on the real cat — jet-black tuxedo, close-set yellow eyes with round
  pupils (stern by default, sweet ^ ^ on the idle blink), narrow white blaze into a
  plump muzzle, black nose smudge, whiskers breaking the silhouette, aviator goggles,
  straight-cut lab coat, white paws. **FF6/CT field-sprite proportions**: head /
  torso / legs each roughly a third of the ~66 px figure; walk cycles, shoot poses,
  hurt, and a full row 6 of expressions: hurt ×2, blink, tail-flick, **happy** (open
  grin + blush) and **sad** (droopy ears, teary eyes, wobble frown) — exposed as
  `happy` / `sad` animations in `player_frames.tres` for cutscenes.
- `assets/_gen_slime_sprites.py` → `slime_gen.png` (288×192, 48×48 cells): bounce cycle
  (airborne on frames 2–4; `slime.gd` syncs movement speed to those frames so slimes
  hop instead of glide) + 4-frame splat death. Used by
  `entities/enemies/slime_frames.tres`.
- `assets/_gen_tileset.py` → `tileset_gen.png` (128×64, 32×32 tiles): grass/tufts/
  flowers/path/hedge/rock, ramps derived from `SCENES["meadow"]`. Used by
  `assets/tileset.tres` (hedges collide).
- `assets/_gen_overworld.py` → the CT/SoS overworld look — broccoli forest canopies,
  sparkle water, snow-capped ridges, **hot-violet cracked wastes** — 4-tone ramps
  from `SCENES["overworld"]`, hash-dithering, upper-left light. Three sheets:
  `overworld_tiles.png` (256×96, 8×3 of 32×32 seamless terrain — water, water
  sparkle, sand, grass, grass detail, scrub, path, bridge / forest A/B, forest edge,
  hills, mountain, mountain snow, river, cliff / cracked A/B, dead tree, crystal,
  +4 reserved grass variants; the cracked/dead/crystal tiles are the drained-wastes
  biome), `overworld_basil.png` (192×144, 4×3 of 48×48: chibi Basil — big head,
  tuxedo, goggles, lab coat — walk down/up/side ×4, side right-facing, flipped in
  code), and `overworld_icons.png` (320×64, five 64×64 landmark icons: HOME cottage,
  TOWN, MEADOW grove, CAVE mouth, OBELISK).
- `assets/_gen_schweinler_sprites.py` → `schweinler_gen.png` (384×384, 96×96 cells):
  Schweinler the pig (big snout, beady angry eyes, red neckerchief, curly tail,
  cloven trotters); walks + point_up + laugh_down. Deliberately stout and round —
  the comedy foil to Basil's lanky thirds — same scale/baseline (feet y=88) so he
  can walk into gameplay later.
- `assets/_gen_title.py` → `title_bg.png` (640×360) + `leaf.png` (10×10): the
  autumn-poster title art.
- `assets/_gen_intro_art.py` → `assets/props/*` at 2x: house front 768×256
  (door-centered; overflows the 640 stage for cinematic framing), Academy front
  896×320, poop bag 192×64, paw print 24×24, hall floor/wall 64×64, chalkboard
  448×144, podium 104×120, audience cats 320×80.
- `assets/_gen_bedroom_art.py` → bedroom stage: `bedroom_bg.png` 640×360 (CT room
  on black, interior (96,24)–(543,335), floor split y=168, bird perch (476,126)),
  `bed_basil.png` 448×160 (4× 112×160), `bird.png` 144×48, `nightstand.png` 52×68,
  `clock_face.png` 192×208.
- `assets/placeholder/_gen_placeholders.py` → combat/HUD support sprites,
  palette-locked to Basil's gun accents (bolt/flash/beaker fluid all laser-green):
  hearts 96×32, ammo pips 32×16, laser bolt 52×16, muzzle flash 40×40, beaker
  24×28, jump shadow 48×20.
- `assets/font/_gen_font.py` → the BMFont bitmap font all Labels use (5×7 glyphs;
  rendered at `font_size = 16` everywhere — a clean 2x integer scale; hand-author a
  10×14 font later only if the doubled glyphs wear thin).

Render style: every form is a shaded volume — 4-tone material ramps (shadows
hue-shift cool), light from the upper-left, ordered dithering between tone bands,
superellipse silhouettes, per-material outline colors, and details that break the
silhouette (whiskers, drawn after the outline). Night scenes tint through a
violet-magenta `CanvasModulate` (see `intro_house.gd`).

### Palette Registry (the color script — `assets/_palette.py` SCENES)

Every scene keys into this table; new materials derive via
`ramp4(seed, SCENES[key]["shadow"])`. Never introduce a neutral beige/brown/gray
field — if a surface wants to be brown, it's rosewood/plum; if gray, lavender.

| Scene key | Dominant field | Hot accent | Shadow bias |
|---|---|---|---|
| `title` | indigo→magenta→gold posterized sunset | leaf gold | violet |
| `night_yard` | periwinkle-violet night | amber lantern glow | violet |
| `bedroom` | periwinkle plaster / rosewood floor | hot-magenta quilt, peach dawn | violet |
| `morning_yard` | peach plaster | magenta shingles, pink blooms | violet |
| `road` | minty teal + peach path | hot pink flowers | teal |
| `hall` | plum panelling / rose floor | chalk-mint board writing | violet |
| `overworld` | teal sea + sage-teal land | violet wastes + crystal | teal |
| `meadow` | minty teal greens | candy hot-pink flowers | teal |

## Asset Specs (sprite sheets to provide)

All PNG, transparent background, **0 padding/margin between cells**, nearest-neighbor
(no anti-aliased edges). Grid is **32×32**.

1. **Player — Professor Poopy Paws** _(highest priority)_ — **96×96 px** cells, **6
   columns**, one direction/action per row to match `player_frames.tres`:
   Walk Down (6) · Walk Up (6) · Walk Side (6, mirrored in code) · Shoot Down (4) ·
   Shoot Up (4) · Shoot Side (4) · Hurt (2) + idle-down blink + idle-side tail-flick
   + happy + sad. Full sheet **576×672**. Figure ~60–70 px tall, feet baseline y=88,
   gun muzzle 32 px from cell center. The cat holds a **laser gun** in the shoot
   rows (weapon-agnostic rows welcome — see "Future Direction"). Use
   `assets/_gen_basil_sprites.py` (current art) as the layout reference.
2. **Slime / first enemy** — **48×48 px** cells. Walk Down/Up/Side (6 each, side
   mirrored) + 4-frame death. Sheet **288×192** (matches `slime_frames.tres`).
3. **Tileset** — **32×32** tiles, 4×2 sheet **128×64**: grass, grass+tufts,
   grass+flowers, dirt path / hedge A, hedge B, rock, reserved. Hedges get collision.
4. **HUD hearts** — **32×32** heart, 3 frames in a horizontal strip:
   full | half | empty → **96×32**. Ammo pips: **16×16** ×2 → **32×16**.
5. **Overworld terrain** — **32×32** seamless tiles, 8×3 sheet **256×96**: water,
   water sparkle, sand, grass, grass detail, scrub, path, bridge / forest A, forest
   B, forest edge, hills, mountain, mountain snow, river, cliff / cracked A, cracked
   B, dead tree, crystal (+4 reserved grass variants).
6. **Overworld Basil (travel chibi)** — **48×48** cells, 4×3 sheet **192×144**:
   walk down / up / side ×4 (side right-facing, flipped in code). Big head, tuxedo
   cat, goggles, lab coat, feet y=42 — matches `overworld_basil_frames.tres`.
7. **Overworld landmark icons** — five **64×64** icons in a strip → **320×64**:
   HOME cottage, TOWN, MEADOW grove, CAVE mouth, OBELISK.

> Prefer a different layout (e.g. Aseprite export with tags)? Send it plus the frame
> tags and the slice will be re-sliced to match. The dimensions above are the defaults
> the code assumes (and what `assets/_check_art.py` asserts).

## Future Direction — Combat & Party (recorded 2026-07, not yet in scope)

The target feel is **Secret of Mana, but snappier**: real-time top-down action that
stays friendly, with crisp fire/recover cadence, hit-pause, and readable knockback.

- **Weapon variety** — the laser gun is the first of several blaster-type weapons;
  each should differ in arc/range/rate/knockback the way SoM's weapon families did.
  The 96×96 cells and 4-frame shoot rows are sized so alternate weapons swap into
  the same animation contract (`shoot_down/up/side` + `muzzle_offset`).
- **3-person party** — the sympathizers (starting with **Fuji**, the librarian cat
  who pulls Basil back into the world) eventually join as party members, SoM-style:
  same 96 px sprite spec, composing the same Health/Hurtbox components, AI-followed
  with leader switching. Party UI stacks additional heart rows.
- **Magic returns late** — spell systems unlock as the story restores magic; the
  drained world is why early combat is all blasters.
