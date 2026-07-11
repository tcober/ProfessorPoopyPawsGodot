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
- **Overworld layer:** CT/SoS-style TILED travel map (`scene/overworld.tscn`)
  between zones — 24×24 chibi travel scale (~16 px figure), terrain-gated
  walking, no map combat; towns are CT-faithful cluster ICONS (one drawn
  composition of overlapping roofs, solid except its gate-mouth `D` cell,
  which travels INTO the town's walkable zone scene). Region edges are drawn
  as 1-cell stair-steps in the map txt — the autotile's 45° corner cuts
  render them as continuous diagonals. Zones are the full-scale (48×48)
  shooter gameplay; walkable **Alembic Town** (`scene/alembic_town.tscn`) is
  a zone too, riding the same overworld tile driver.
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
OVERWORLD → Whisker Meadow — to hone the battling and the look. The
title screen, five-part intro, Schweinler's sprites, and the cutscene/dialog
kit were deleted (git history keeps them; the story stays in docs/DESIGN.md as
the plan). The game boots into Basil's loft bedroom (`scene/house.tscn`, main
scene) — a small dense CT-bedroom diorama floating in void (10-tile-wide room
on the 24×14 map), brown plank walls / teal weave / gold dawn window, E
toggles the curtains at the window; its SW staircase descends to the
**downstairs** (`scene/downstairs.tscn`) — the kitchen + steampunk-lab great
room (20-tile room, hearth fire = light source + glow, copper boiler,
workbench, alcove stairs back up) whose south front door opens onto the
**tiled overworld**, where Alembic Town is a CT-faithful cluster ICON on the
SW coast (one DENSE drawn composition — seven small overlapping roofs with
dab openings, the Academy castle-keep, the steamworks' riveted copper boiler
venting a steam plume; darker mossy-emerald 2026-07 palette) whose gate-mouth
`D` marker (`town`) goes straight back into the downstairs, with ONE winding
trail NE past Whisker Meadow (`scene/meadow.tscn` — slimes, beaker respawns,
HUD; marker `meadow`) over the river bridge to the wastes; steampunk-medieval
landmarks anchor the horizon — the Capital's pale-stone CASTLE on the north
massif (`C` cells) with the snowcapped HORN summit (`V`) at its NW tip, the
ELDER TREE (`g`, 64×96, ~5× the chibi) leaning over the riverbank, the
wastes' crystal OBELISK monument (`O`) + scattered 2×2 `K` crystal outcrops,
lit windows/coals/crystals on the glow overlay (the cloud-shadow shade
overlay was cut — dark ovals read as smudges at CT zoom); leaving a zone
returns to its marker via the
`Game` autoload. (A walkable zone-scale **Alembic
Town** — `scene/alembic_town.tscn`, 40×28 on the shared overworld driver,
walk-behind rooflines, `Game.town_spawn` routing — is built but PARKED:
unreferenced by the flow until the town earns its place.) **Current playable:
FUJI, the librarian cat** (`entities/fuji/` — swapped in for Basil 2026-07-07
to dial her look/feel; Basil's `entities/player/player.tscn` is parked, fully
working, one ext_resource repoint away; scene scripts are player-agnostic —
`DirectionalBody2D` + the `player` group — the Basil⇄Fuji switch groundwork).
Fuji: tortoiseshell (warm-black fur, PLACED rust patches, cream chin/chest/
paws, green-gold eyes), round brass reading glasses, plum scholar's robe,
tome hugged to her chest in the walk; walk/hop (Basil's air-steerable dodge) /
**tome swing** (attack — overhead slam, BookHitbox shape-toggled through the
strike/impact window, damage 2, forward lunge) / **blow-pipe darts** (`dart`
action, L — unlimited `blow_dart` projectiles, damage 1, leaves on the puff
frame at the 19px pipe-tip contract — Fuji's reed runs longer than Basil's
16px gun muzzle). Basil's kit (instant-fire laser, recoil
skid, beaker mags) lives on in player.gd/tscn; slimes explode in 2 book
swings or 2 laser shots and a replacement respawns elsewhere in the meadow.
GOTCHA fixed 2026-07-07: hand-authored .tscn node exports NEED
`node_paths=PackedStringArray("health_component")` on the node header or the
reference silently loads null (HurtboxComponent now also falls back to the
sibling HealthComponent in `_ready`).
**One scene pipeline, one map format:** every scene is TILED on the shared
**tile kit** `assets/_tilekit.py`
(`TileScene`: canvases, material ramps, footprint `place()`/`place_split`/
`place_each`, glow, the slice/dedupe `finish()`):
  the **interior kit** `assets/_interior.py` (16-periodic fabrics — plank
  walls with wainscot, weave/flag floors — whole-tile light dispatch,
  stair/rail/jamb cells, the `Room` driver) + `assets/_interior_props.py`
  (furniture authored on `_sprites.py`), and the **overworld kit**
  `assets/_overworld_tiles.py` (`OverWorld` driver, used by the overworld
  map, walkable Alembic Town AND Whisker Meadow: terrain fabrics — grass/forest
  carry a 32-periodic phase on interior cells — + neighbor-keyed CT autotile
  transitions with **45° corner cuts** — every boundary painted one-sidedly
  by its owner class, every cell a pure function of terrain + per-class
  8-neighbor masks, so diagonal coasts/cliffs/canopy rims dedupe; forest
  canopy AND mountain massifs share one 16-periodic lobe lattice —
  crown-ball vs stylized-peak shading — whose arcs also FORM each rim
  (`_arc_cell`: lobes whose disc would cross an open boundary are
  rejected, bays render the neighbor's fabric, a 1px ring outlines the
  silhouette, snow caps the massif's north-facing edge lobes); fabric
  texture = tile-local `_grain_dither`/`_hatch` — turf clumps + warm
  grass2 drift patches, strata-hatched peak faces, dithered boundary
  lips — NEVER keyed on absolute position; roads are wobbly segment-union
  trails keyed to shared edges; variants only on interior cells) + `assets/_overworld_props.py`
  (the landmark library — one-off, never deduped, so props use full
  per-pixel Sprite shading: tone() lambert roofs, `_coursed_wall` masonry,
  `_hatch_px` linework, cluster_shade finishing: town cluster ICON, the
  castle, the Horn peak, the Elder Tree, the obelisk + crystal outcrops,
  lone trees) + `assets/_town_props.py` (zone-scale facades: Basil's
  cottage, cottages, the Academy, well/lamp/stall) + `assets/_meadow_props.py`
  (the meadow's per-cell boulder domes + the trailhead cairn).
  A generator (`assets/_gen_tileset_house.py`, `_gen_tileset_downstairs.py`,
  `_gen_tileset_overworld.py`, `_gen_tileset_town.py`,
  `_gen_tileset_meadow.py`) is a thin config:
  palette + pools/terrain + `place()` props at map feature chars;
  `assets/_tiles.py` slices the composed canvases into a real TileSet (atlas
  + `.tres` + layout in `assets/tilesets/`; 60-88 tiles from 336 interior
  cells, ~580 from the overworld's 2304, ~255 from the town's 1120, ~145
  from the meadow's 1152) that
  `scene/tiled_map.gd` stamps onto TWO TileMapLayers — under and over
  entities, so bodies walk behind railings/lintels/ROOFLINES
  (`scene/house.tscn` = interior reference, `scene/overworld.tscn` +
  `scene/alembic_town.tscn` = exterior references, `scene/meadow.tscn` =
  combat-zone reference) — move a feature char in
  the map txt and it moves in-game. A NEW scene = map txt + thin config.
  Sprites/fx build on `assets/_sprites.py`; collision is always an
  invisible TileMapLayer built at runtime by `scene/painted_map.gd` from the same
  map file. Regenerate via `assets/_gen_*.py`, then
  `python3 assets/_check_art.py`; eyeball scenes with `tools/shot.gd` (see "Art
  pipeline" in docs/DESIGN.md).
