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
  walked by a tiny chibi travel sprite (~16 px tall on 16×16 terrain tiles) between
  full-scale places. Their turn-based combat is **not** adopted; zones stay an
  ALttP-style top-down shooter.
- **Secret of Mana:** the closest gameplay cousin — real-time top-down action combat
  inside a lush 16-bit JRPG shell. Reference for how zones should _feel_: saturated
  organic terrain, big readable sprites, action combat that stays friendly, whimsical
  enemies with personality, and the seamless flow between exploring and fighting.
- **Art direction** (canonical influence list): **Final Fantasy VI, Chrono Trigger,
  Secret of Mana, Sea of Stars, Adventure Time, and the Paper Girls comic.** Gameplay
  feels like Zelda, but the _look_ is richer 16-bit JRPG — FF6/CT field-sprite
  proportions, SoM's lush saturated environments, shading ramps and rim light over
  flat fills, textured tiles, bitmap-font dialog boxes — with Adventure Time's whimsy
  in character/creature design and Paper Girls' bold graphic color scripting (dusk
  gradients, surreal duotone fields, violet-shifted shadows) for posters, title art,
  and mood lighting.

## World Structure — Overworld + Zones

Two layers:

- **Overworld** (`scene/overworld.tscn`) — the travel layer: a Chrono Trigger /
  Sea of Stars–style miniature painted continent (64×36 tiles, 1024×576 px,
  camera-clamped). Basil walks it as a 24×24-cell chibi sprite (~16 px tall) over
  16×16 terrain tiles. **No combat on the map.** Terrain gates travel — water,
  forest, mountains, rivers, cliffs and dead trees are solid; sand, grass, paths,
  bridges, forest edges, hills and the wastes are walkable; bridges and paths open
  the routes.
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
- Base resolution: **640×360**, integer-scaled. Tile size: **16×16**. Nearest filtering.
  Characters stay 48×48-cell sprites — at 640×360 they occupy ~1/8 of screen height,
  which is what gives the game its "high-resolution pixel art" scale (big world,
  small detailed characters) instead of a chunky retro look.
- **Two sprite scales:** zones use **48×48** field cells (above); the overworld uses
  **24×24** chibi travel cells (~16 px Basil). Tiles are **16×16** everywhere.
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
  travel-only `CharacterBody2D`: 8-way move, 4-way facing, ~90 px/s, no gun/hop/health
- `assets/overworld_tileset.tres` — water/forest/mountain/river/cliff/dead-tree tiles
  are solid (physics layer); sand/grass/path/bridge/forest-edge/hills/wastes walkable
- `assets/font/pixel_font.fnt/.png` — 5×7 bitmap font (`assets/font/_gen_font.py`,
  glyphs shared via `assets/_pixfont.py`)

### Art pipeline (generated placeholders that animate)

The AI-generated sheets (`assets/basil.png`, `assets/basil_sheet.png`) draw a slightly
different cat in every frame, so animations strobe; they are kept only as concept
reference (along with the old `_repack_basil.py` slicer and its `basil_packed.png`).
The live art is drawn procedurally — every frame from one parametric model — by three
stdlib-only scripts:

- `assets/_gen_basil_sprites.py` → `basil_gen.png` (288×336, 48×48 cells): Basil,
  modeled on the real cat — jet-black tuxedo, close-set yellow eyes with round
  pupils (stern by default, sweet ^ ^ on the idle blink), narrow white blaze into a
  plump muzzle, black nose smudge, whiskers breaking the silhouette, aviator goggles,
  straight-cut lab coat, white paws. **FF6/CT field-sprite proportions**: head /
  torso / legs each roughly a third of the figure, slim coat, small feet; walk
  cycles, shoot poses, hurt, and a full row 6
  of expressions: hurt ×2, blink, tail-flick, **happy** (open grin + blush) and
  **sad** (droopy ears, teary eyes, wobble frown) — exposed as `happy` / `sad`
  animations in `player_frames.tres` for cutscenes.
- `assets/_gen_slime_sprites.py` → `slime_gen.png` (144×96, 24×24 cells): bounce cycle
  (airborne on frames 2–4; `slime.gd` syncs movement speed to those frames so slimes
  hop instead of glide) + 4-frame splat death. Used by
  `entities/enemies/slime_frames.tres`.
- `assets/_gen_tileset.py` → `tileset_gen.png` (64×32, 16×16 tiles): grass/tufts/
  flowers/path/hedge/rock. Used by `assets/tileset.tres` (hedges collide).
- `assets/_gen_overworld.py` → the CT/SoS overworld look — broccoli forest canopies,
  sparkle water, snow-capped ridges, cracked wastes — same procedural style (muted
  SNES palette, 4-tone ramps, hash-dithering, upper-left light). Three sheets:
  `overworld_tiles.png` (128×48, 8×3 of 16×16 seamless terrain — water, water
  sparkle, sand, grass, grass detail, scrub, path, bridge / forest A/B, forest edge,
  hills, mountain, mountain snow, river, cliff / cracked A/B, dead tree, crystal,
  +4 reserved grass variants; the cracked/dead/crystal tiles are the drained-wastes
  biome), `overworld_basil.png` (96×72, 4×3 of 24×24: chibi Basil — big head, tuxedo,
  goggles, lab coat — walk down/up/side ×4, side right-facing, flipped in code), and
  `overworld_icons.png` (160×32, five 32×32 landmark icons: HOME cottage, TOWN,
  MEADOW grove, CAVE mouth, OBELISK).
- `assets/_gen_schweinler_sprites.py` → `schweinler_gen.png`: Schweinler the pig
  (big snout, beady angry eyes, red neckerchief, curly tail, cloven trotters);
  walks + point_up + laugh_down. Compact upright FF6/CT figure, same
  scale/baseline as Basil.
- `assets/_gen_title.py` → `title_bg.png` + `leaf.png`: the autumn-poster title art.
- `assets/_gen_intro_art.py` → `assets/props/*`: house front, Academy front,
  poop bag (3 frames), paw print, hall floor/wall, chalkboard, podium, audience cats.
- `assets/font/_gen_font.py` → the BMFont bitmap font all Labels use.

Style: **FF6 / Chrono Trigger render, Paper Girls palette** — restrained
dithering, dark unified outlines, small expressive eyes, and taller field-sprite
proportions (movement/perspective stays SNES-Zelda; only the look is Square-style).
The **color script is surreal duotone**: every scene picks a dominant hue field plus
a hot accent (periwinkle + magenta, teal + peach), shadows hue-shift violet/teal,
glass and skies carry sunset gradients — never neutral beige/brown/gray fields.
Night scenes tint through a violet-magenta `CanvasModulate` (see `intro_house.gd`).
The Basil
and slime generators render every form as a shaded volume: 4-tone material ramps
(shadows hue-shift cool), light from the upper-left, ordered dithering between tone
bands (`_pick`), superellipse silhouettes (`oval`/`cloth` primitives), per-material
outline colors, and details that break the silhouette (whiskers, drawn after the
outline). Older generators (props) still use the simpler rim-light `shade()`
pass — upgrade them to the primitive-based renderer as they get screen time.

Re-run any script with `python3 <script>`; Godot reimports the PNG on editor focus.

## Asset Specs (sprite sheets to provide)

All PNG, transparent background, **0 padding/margin between cells**, nearest-neighbor
(no anti-aliased edges). Grid is **16×16**.

1. **Player — Professor Poopy Paws** _(highest priority)_ — **48×48 px** cells, **6
   columns**, one direction/action per row to match `player_frames.tres`:
   Walk Down (6) · Walk Up (6) · Walk Side (6, mirrored in code) · Shoot Down (4) ·
   Shoot Up (4) · Shoot Side (4) · Hurt (2) + idle-down blink + idle-side tail-flick.
   Full sheet **288×336**. The cat holds a **laser gun** in the shoot rows. See
   **`docs/SPRITE_PROMPT.md`** for the exact image-generation prompt, or use
   `assets/_gen_basil_sprites.py` (current art) as the layout reference.
2. **Slime / first enemy** — **24×24 px** cells. Walk Down/Up/Side (6 each, side
   mirrored) + 4-frame death. Sheet **144×96** (matches `slime_frames.tres`).
3. **Tileset** — **16×16** tiles in one sheet (~**128×128**, 8×8). Grass/floor, wall/cliff
   edges with a few corners, a path, one decorative tile. Wall tiles get collision.
4. **HUD hearts** — **16×16** heart, 3 frames in a horizontal strip:
   full | half | empty → **48×16**.
5. **Overworld terrain** — **16×16** seamless tiles, 8×3 sheet **128×48**: water,
   water sparkle, sand, grass, grass detail, scrub, path, bridge / forest A, forest
   B, forest edge, hills, mountain, mountain snow, river, cliff / cracked A, cracked
   B, dead tree, crystal (+4 reserved grass variants).
6. **Overworld Basil (travel chibi)** — **24×24** cells, 4×3 sheet **96×72**:
   walk down / up / side ×4 (side right-facing, flipped in code). Big head, tuxedo
   cat, goggles, lab coat — matches `overworld_basil_frames.tres`.
7. **Overworld landmark icons** — five **32×32** icons in a strip → **160×32**:
   HOME cottage, TOWN, MEADOW grove, CAVE mouth, OBELISK.

> Prefer a different layout (e.g. Aseprite export with tags)? Send it plus the frame
> tags and the slice will be re-sliced to match. The dimensions above are the defaults
> the code assumes.
