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
- Slimes: anim-synced hopping chase, splat death, 2 shots to kill (4 HP vs 2 dmg); each kill respawns one elsewhere in the meadow.
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

- **CT/SoS-style continent** (`scene/overworld.gd/.tscn`): 64×36 tiles
  (1024×576 px, camera-clamped), no combat on the map. Geography (reworked by
  the 2026-07 town carve, then re-proportioned the same month — the rampart
  came back out): Alembic Town as an OPEN CT-Truce cluster on the SW coast
  (squat cottages on dirt lanes, Basil's cottage = the `home` door-mouth
  marker, neighbor-cottage door markers, the Academy set apart, well/lamp/
  stall) → dirt road NE past Whisker Meadow → bridge over a N→S river →
  drained wastes + obelisk E/SE; mountains + cave N; ocean frame.
- Art (superseded twice: the Milestone-5 painting replaced the original
  tileset; the 2026-07 tiled-overworld conversion then replaced the painting
  with a real CT-autotile TileSet): now `assets/_gen_tileset_overworld.py` →
  `assets/tilesets/overworld_tiles.png/.tres` + `overworld_layout.txt` +
  `overworld_glow.png` (~210 unique tiles from `assets/maps/overworld.txt`;
  `_gen_scene_overworld.py` and the `overworld_ground/overlay.png` paintings
  are deleted), with `overworld_basil.png` (96×72, 24×24 chibi) and
  `overworld_icons.png` (160×32; only the meadow icon is still shown — drawn
  buildings replaced the rest). Terrain gating unchanged in spirit:
  sea/forest/mountain/river/buildings solid via the shared collision
  tileset; beach/grass/flowers/hills/roads/door-mouths/bridge/wastes walk.
- Travel sprite: `entities/player/overworld_player.gd/.tscn`
  (+ `overworld_basil_frames.tres`) — 8-way move, 4-way facing, ~90 px/s, no
  gun/hop/health.
- Location markers (`scene/overworld_location.gd`): id/display_name/target_scene/
  locked_text; banner label announces names, locked markers show flavor text,
  unlocked ones fade out and enter. Live set (2026-07 open-cluster town):
  BASIL'S COTTAGE (`home` door mouth → `downstairs.tscn`), WHISKER MEADOW →
  `meadow.tscn`, and announce-only A NEIGHBOR'S COTTAGE ×2 (`cottage_w`/
  `cottage_e`), ALEMBIC TOWN (commons) and THE ALEMBIC ACADEMY (barred).
- `scene/game.gd` autoload **Game** remembers `overworld_spawn` → leaving a zone
  returns Basil to that marker. Flow rewired: hall "...YEARS LATER." → overworld;
  title/intro ESC skips → overworld; meadow gains a south hedge-gap exit back to
  the map.

### Milestone 5 — Painted-scene art overhaul ✅ (2026-07-03)

Total from-scratch art rebuild — the tiled/RPG-maker look is gone. Every map is
now ONE composed painting (ground + overlay Sprite2Ds) generated from a shared
`assets/maps/*.txt` file; collision is an invisible TileMapLayer built at
runtime from the same file (`scene/painted_map.gd`), so paint and physics can't
drift. New foundation modules: `_core.py` / `_paint.py` (FBM fields, warped
SDF boundaries, spline trails, canopy masses, stamps) / `_sprites.py` (rigged
character kit) / `_maps.py`. All character/fx sheets rebuilt (Basil, slime,
Schweinler, chibi, icons, hearts/bolt/beaker), bedroom/hall/title recomposed,
native 10×16 font with true lowercase, surreal Paper Girls palette pushed
(emerald fields, indigo canopies, cyan water, violet cloud washes). Legacy
tilesets/generators deleted; `_artlib.py` shim remains only under
`_gen_intro_art.py` (house/school/small props — future prop pass).
Details: docs/DESIGN.md "Art pipeline".

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

## Verification (manual — it's a game; rewritten for the combat-first cut)

1. Run the main scene (`scene/house.tscn`, 384×216 integer-scaled): the loft
   bedroom renders; E at the window toggles the curtains (beam + dim tween).
2. SW stairs descend to the downstairs great room; hearth fire flickers, boiler
   shivers; the front door exits to the overworld INSIDE the open town cluster.
3. Overworld: WASD walks the chibi; each building's door mouth triggers — his
   own cottage re-enters the lab, the neighbor cottages / commons / Academy
   announce flavor banners; water/forest/mountains/buildings block walking;
   the dirt road leads NE, the bridge crosses the river.
4. Enter WHISKER MEADOW → slimes + HUD: camera clamps; slime contact damages +
   knockback; 2 bolts kill a slime and one respawns elsewhere; beaker refills
   (R / dry-trigger reload pours it). Exit the south hedge gap → back on the
   map at the meadow marker, landing in the flower ring.
5. `python3 assets/_check_art.py` green after any `assets/_gen_*.py` re-run.
6. No errors in the debugger output.
