# Professor Poopy Paws — Design Bible

> Canonical, tool-agnostic design doc. `CLAUDE.md` and `AGENTS.md` point here so any AI
> assistant (Claude Code, Cursor, Copilot, etc.) shares the same source of truth.

A Zelda: A Link to the Past–style action-RPG with deeper RPG systems. Tone is a blend
of **Adventure Time** (whimsical, absurd, heartfelt) and **Final Fantasy** (earnest
stakes, party/progression depth, emotional arcs).

## Story Outline
- Protagonist: a brilliant **science cat** living in a magical world.
- Inciting humiliation: on the morning of an important lecture he oversleeps and rushes
  out. A bully has left a bag of poop outside his door; he steps in it. Mid-lecture the
  bully calls it out publicly and brands him **"Professor Poopy Paws"** — the name sticks
  and becomes the name of the game.
- Loss: later that same day, his girlfriend is hit by a car.
- Retreat: devastated, the cat becomes a reclusive hermit.
- Catalyzing event: all magic is removed/drained from the world.
- Call to adventure: a handful of sympathizers who still remember and believe in him
  seek him out and pull him back into the world.
- Arc: through a series of adventures he restores the world's magic, saves the world,
  grows past his humiliation, and finds love again.

## Themes
Humiliation → isolation → being seen by others → growth → redemption and renewed love.
Magic as a metaphor for hope/connection returning to the protagonist and the world.

## Influences
- **Adventure Time:** surreal biomes, oddball NPCs, comedic-but-sincere writing.
- **Final Fantasy:** progression systems, emotional storytelling, eventual party members
  (the sympathizers), set-piece dungeons.
- **Zelda: ALttP:** top-down 4-directional action combat, dungeons, items as gating tools.

## Tech / Engine Conventions
- Engine: **Godot 4.6**, GDScript, GL Compatibility renderer.
- Base resolution: **320×180**, integer-scaled. Tile size: **16×16**. Nearest filtering.
- Architecture: **component-based**. Reusable behavior lives in `components/` as nodes/
  resources (HealthComponent, HitboxComponent, HurtboxComponent, …). Entities in
  `entities/` compose these. Shared data (stats, items) as custom `Resource`s in
  `resources/`. Playable rooms/levels in `scene/`. Art/audio in `assets/`.
- Movement: `CharacterBody2D`, 8-way movement with 4-way facing (sword swings in the
  facing direction), ALttP-style.
- Combat: `Area2D` Hitbox (attacker) vs `Area2D` Hurtbox (receiver) → HealthComponent.
- **Magic is deferred by design:** the world starts drained, so ranged/spell systems are
  introduced later as progression that mirrors the story.

## Current Milestone — Vertical Slice
One room: cat walks 8-way / faces 4-way, swings a sword, kills one slime, heart-based HP
HUD. Placeholder art (in `assets/placeholder/`) so it runs immediately; real sprite
sheets drop in later against the dimensions in "Asset Specs" below.

### Slice file map
- `components/health_component.gd`, `hitbox_component.gd`, `hurtbox_component.gd`
- `entities/player/player.gd` + `player.tscn`
- `entities/enemies/slime.gd` + `slime.tscn`
- `scene/hud.gd` + `hud.tscn`
- `scene/test_room.gd` + `test_room.tscn` (main scene)

## Asset Specs (sprite sheets to provide)
All PNG, transparent background, **0 padding/margin between cells**, nearest-neighbor
(no anti-aliased edges). Grid is **16×16**.

1. **Player — Professor Poopy Paws** *(highest priority)* — **32×32 px** cells (body
   ~16–22px; extra room for the sword arc / lab-coat flair). One direction per row:
   - Walk Down (6) · Walk Up (6) · Walk Side (6, side mirrored in code) ·
     Attack Down (4) · Attack Up (4) · Attack Side (4) · Hurt (1–2, optional).
   - Full sheet ≈ **192×224**. Fewer frames is fine — keep row-per-direction layout and
     tell me the frame counts.
2. **Slime / first enemy** — **24×24 px** cells. Walk Down/Up/Side (6 each, side
   mirrored), optional 2-frame death. Sheet ≈ **144×72**.
3. **Tileset** — **16×16** tiles in one sheet (~**128×128**, 8×8). Grass/floor, wall/cliff
   edges with a few corners, a path, one decorative tile. Wall tiles get collision.
4. **HUD hearts** — **16×16** heart, 3 frames in a horizontal strip:
   full | half | empty → **48×16**.

> Prefer a different layout (e.g. Aseprite export with tags)? Send it plus the frame
> tags and the slice will be re-sliced to match. The dimensions above are the defaults
> the code assumes.
