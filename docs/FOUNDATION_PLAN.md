# Foundation Plan — Professor Poopy Paws

> Running build plan + status log, kept in-repo so any AI tool can read it.
> Design details live in [DESIGN.md](DESIGN.md) — that file is the source of truth
> for story, art direction, and conventions; this one tracks what shipped and what's
> next.

## Shipped (as of 2026-07)

### Milestone 1 — Vertical slice ✅

- Component architecture (`components/`): HealthComponent, HitboxComponent,
  HurtboxComponent; entities compose them.
- Player: 8-way move / 4-way facing, laser gun (ammo + beaker refills, recoil
  shove on fire), hop (straight up standing, directional when moving, steerable
  mid-air), hearts + ammo-pip HUD.
- Slimes: anim-synced hopping chase, splat death, 3 shots to kill (6 HP vs 2 dmg).
- Tile-mapped rooms painted from ASCII maps (`TileMapLayer` + tileset physics).

### Milestone 2 — Opening sequence ✅

- Flow: **title → house cutscene → playable road (slime tutorial) → lecture-hall
  nickname scene → meadow**. ESC skips.
- Cutscene kit: `scene/cutscene.gd` (awaitable say/walk/hop/fade/card),
  `scene/dialog_box.tscn` (typewriter box), bitmap pixel font (`assets/font/`).
- Cast: **Schweinler** the pig (bully) with walk/point/laugh sheets.

### Milestone 3 — Art & resolution overhaul ✅

- Base resolution **640×360** (was 320×180): characters ~1/8 screen height →
  high-res pixel-art scale.
- All character art from **procedural hi-fi generators** (`assets/_gen_*.py`):
  4-tone dithered ramps, dome shading, per-material outlines, silhouette-breaking
  whiskers. Basil is modeled on the real cat and has happy/sad/hurt/blink
  expressions.
- Epic sunset title screen, lush meadow palette, detailed 2× props (readable
  chalkboard, mullioned windows, plank doors).

### Milestone 4 — Overworld travel layer ✅

- **CT/SoS-style painted continent** (`scene/overworld.gd/.tscn`): 64×36 tiles
  ASCII-painted (1024×576 px, camera-clamped), no combat on the map. Geography:
  home bluff SW → path NE past Whisker Meadow → bridge over a N→S river → Alembic
  Town at the NE forest's edge; mountains + cave N; drained wastes + obelisk E/SE;
  ocean frame.
- Art: `assets/_gen_overworld.py` (stdlib-only, same hi-fi procedural style) →
  `overworld_tiles.png` (128×48, 8×3 of 16×16 seamless terrain incl. the
  cracked/dead-tree/crystal wastes biome), `overworld_basil.png` (96×72, 24×24 chibi
  walk cycles), `overworld_icons.png` (160×32, five 32×32 landmark icons).
- `assets/overworld_tileset.tres`: water/forest/mountain/river/cliff/dead-tree tiles
  solid — terrain gates travel; sand/grass/path/bridge/forest-edge/hills/wastes walk.
- Travel sprite: `entities/player/overworld_player.gd/.tscn`
  (+ `overworld_basil_frames.tres`) — 8-way move, 4-way facing, ~90 px/s, no
  gun/hop/health.
- Location markers (`scene/overworld_location.gd`): id/display_name/target_scene/
  locked_text; banner label announces names, locked markers show flavor text,
  unlocked ones fade out and enter. Live set: BASIL'S BLUFF (locked, "HOME. IT CAN
  WAIT."), WHISKER MEADOW → `test_room.tscn`, ALEMBIC TOWN (locked, academy shut),
  THE BURROWS (locked), THE DRAIN (locked, where-the-magic-went hook).
- `scene/game.gd` autoload **Game** remembers `overworld_spawn` → leaving a zone
  returns Basil to that marker. Flow rewired: hall "...YEARS LATER." → overworld;
  title/intro ESC skips → overworld; meadow gains a south hedge-gap exit back to
  the map.

## Next milestone — candidates (pick when ready)

1. **Game over / respawn flow** — player death currently just freezes the cat.
2. **Audio** — footsteps, laser zap, slime splat, squelch, title theme. (Godot
   AudioStreamPlayer + generated or CC0 chiptune assets.)
3. **Alembic Town zone + sympathizer NPC #1** — unlock the town marker: first hub
   zone, dialog reuse from the cutscene kit, first party member per the story arc.
4. **The Burrows dungeon chain** — cave zone behind a light item: door transitions
   between authored rooms, keys/blocked doors, a miniboss.
5. **Wastes / obelisk story beat** — unlock THE DRAIN: the first
   where-the-magic-went reveal.
6. **Overworld polish** — region name popups, drifting cloud shadows, map sound.
7. **Save/continue** — skip intro automatically after first playthrough.
8. **Style upgrades** — port Schweinler-era props (house/school/hall) to the hi-fi
   renderer; ambient effects (CanvasModulate sunset pass, firefly particles).

## Verification (manual — it's a game)

1. Run main scene: title renders 640×360, integer-scaled, crisp; SPACE starts intro.
2. House scene: night drop-off plays; morning cards; Basil exits the doorway cleanly,
   SQUELCH, paw prints trail him off-screen.
3. Road: WASD/arrows move; J/Space fires (recoil shove); K hops (up in place,
   directional when moving, steerable); 3 bolts kill a slime; beaker refills; the
   Academy doors advance the story.
4. Hall: dialog advances on J/Space; Schweinler points/laughs; Basil's ears droop
   (sad face) under the crowd laugh; cards land on "...YEARS LATER." → overworld
   fade-in at Basil's Bluff.
5. Overworld: walk the path NE — banner names appear on markers; locked markers
   show flavor text; water/forest/mountains block walking; the bridge crosses the
   river.
6. Enter WHISKER MEADOW → meadow with slimes + HUD: camera clamps to the room;
   slime contact damages + knockback; heart HUD updates; beaker respawns away from
   hedges. Exit the south hedge gap → back on the map at the meadow marker.
7. ESC from title or road lands on the overworld.
8. No errors in the debugger output.
