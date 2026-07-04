# Professor Poopy Paws

> **Full design bible: [docs/DESIGN.md](docs/DESIGN.md)** — single source of truth for
> story, themes, influences, asset specs, and conventions. Keep it updated as the game
> grows. This file is a quick-reference for Claude Code.

A Zelda: ALttP–style action-RPG with deeper RPG systems, tonal blend of **Adventure
Time** and **Final Fantasy**, about a science cat branded "Professor Poopy Paws" who —
after public humiliation, losing his girlfriend, and the world's magic being drained —
is pulled out of hermithood by sympathizers, restores the world's magic, and finds love
again. (Full story in docs/DESIGN.md.)

## Tech conventions (read before writing code)

- **Godot 4.6**, GDScript, GL Compatibility renderer.
- Base resolution **384×216** (16:9 — integer-scales 5x to 1080p; dev window 3x
  at 1152×648); **16×16** tiles; **48×48** character cells (figure ~33 px, feet
  y=44); nearest filtering, no camera zoom.
  **TRUE SNES density** (the 2026-07 CT-chunk restart — big deliberate pixels,
  Chrono Trigger scale): ~24×13.5 tiles visible, characters ~2 tiles tall.
  Canonical numbers live in the DESIGN.md Scale Table + `assets/_core.py`
  constants.
- **Component-based architecture:** reusable behavior as nodes/resources in
  `components/` (HealthComponent, HitboxComponent, HurtboxComponent). Entities in
  `entities/` compose them. Shared data as `Resource`s in `resources/`. Rooms/levels in
  `scene/`. Art/audio in `assets/`.
- Player: `CharacterBody2D`, 8-way movement, 4-way facing; fires a laser gun in the
  facing direction — instant on the trigger, hard recoil. Beakers are the gun's
  magazines: pickups pocket as spares, reload (R, or a dry trigger) pours one in.
- Combat: `Area2D` Hitbox vs `Area2D` Hurtbox → HealthComponent. `LaserBolt` projectile.
- **Overworld layer:** CT/SoS-style travel map (`scene/overworld.tscn`) between zones —
  24×24 chibi travel scale (~16 px figure), terrain-gated walking, no map combat.
  Zones are the full-scale (48×48) shooter gameplay.
- **Magic is deferred by design** (world starts drained); ranged/spell systems unlock
  later as story-driven progression.
- **Art direction:** influenced by **Final Fantasy VI, Chrono Trigger, Secret of
  Mana, Sea of Stars, Adventure Time, and the Paper Girls comic** — CT-Frog sprite
  proportions with **flat hard-banded shading** (no dither inside characters,
  every pixel deliberate), SoM's lush action-RPG feel, Paper Girls' surreal
  duotone color scripting (palette registry in `assets/_palette.py` — every scene
  = a MINIMAL duo/tri-tone cast: hue field + hot accent, violet/teal shadows;
  wood may be honest warm brown, but never a beige/gray mud field or muddy
  un-hue-shifted darks);
  movement/perspective stays SNES-Zelda. **World genre: steampunk-inflected
  medieval fantasy** — brass-and-flask over chrome, candle-and-gear over
  circuitry (see DESIGN.md "World genre").

## Current state

**Combat-first cut (2026-07):** the build is pared to its core loop — HOUSE →
OVERWORLD → Whisker Meadow — to hone the battling and the look. The title screen,
five-part intro, Schweinler's sprites, and the cutscene/dialog kit were deleted
(git history keeps them; the story stays in docs/DESIGN.md as the plan). The game
boots into Basil's loft bedroom (`scene/house.tscn`, main scene) — a small
dense CT-bedroom diorama floating in void (10-tile-wide room on the 24×14
map), brown plank walls / teal weave / gold dawn window, E toggles the
curtains at the window; its SW staircase descends to the **downstairs**
(`scene/downstairs.tscn`) — the kitchen + steampunk-lab great room (20-tile
room, hearth fire = light source + glow, copper boiler, workbench, alcove
stairs back up) whose south front door opens onto
the overworld, whose two markers are home (re-enters the house at the
downstairs front door) and
Whisker Meadow (`scene/meadow.tscn` — slimes, beaker respawns, HUD); leaving a
zone returns to its marker via the `Game` autoload. Player: walk/hop (straight up
when standing, air-steerable) / instant-fire laser whose recoil shoves him into
a barely-held skid / mag reloads (beakers = spare mags, R or dry trigger plays
the planted pour, RELOAD state + `reload` anim); slimes explode in 2 shots and
a replacement respawns elsewhere in the meadow.
**Two scene pipelines, one map format:** exteriors (meadow, overworld) are
painted — a single composed painting (ground + overlay Sprite2Ds) generated
from shared `assets/maps/*.txt` files on `assets/_core.py` + `assets/_paint.py`

- `assets/_palette.py` (`scene/meadow.tscn` = reference). Interiors are TILED
  (the 2026-07 CT-bedroom pivot): `assets/_gen_tileset_house.py` AUTHORS a tile
  library from `assets/maps/house.txt`'s feature chars — 16-periodic fabric
  painters (repeats are byte-identical, so they dedupe to single tiles),
  whole-tile light variants (lit / dither-fringe / shadow — never per-pixel
  gradients), furniture as footprint-bounded multi-tile objects — and
  `assets/_tiles.py` slices it into a real TileSet (atlas PNG + `.tres` +
  layout txt in `assets/tilesets/`, ~67 tiles from 336 cells) that
  `scene/tiled_map.gd` stamps onto TWO TileMapLayers — under and over
  entities, so bodies walk behind railings/furniture tops (`scene/house.tscn`
  = reference) — move a feature in the map txt and it moves in-game.
  Sprites/fx build on `assets/_sprites.py`; collision is always an
  invisible TileMapLayer built at runtime by `scene/painted_map.gd` from the same
  map file. Regenerate via `assets/_gen_*.py`, then
  `python3 assets/_check_art.py`; eyeball scenes with `tools/shot.gd` (see "Art
  pipeline" in docs/DESIGN.md).
