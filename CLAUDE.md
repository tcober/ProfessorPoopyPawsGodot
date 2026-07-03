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
- Base resolution **640×360**, integer-scaled; **16×16** tiles; 48×48 character cells
  (small-on-screen = high-res pixel-art scale); nearest filtering.
- **Component-based architecture:** reusable behavior as nodes/resources in
  `components/` (HealthComponent, HitboxComponent, HurtboxComponent). Entities in
  `entities/` compose them. Shared data as `Resource`s in `resources/`. Rooms/levels in
  `scene/`. Art/audio in `assets/`.
- Player: `CharacterBody2D`, 8-way movement, 4-way facing; fires a laser gun in the
  facing direction (limited charges, beaker pickups refill).
- Combat: `Area2D` Hitbox vs `Area2D` Hurtbox → HealthComponent. `LaserBolt` projectile.
- **Overworld layer:** CT/SoS-style travel map (`scene/overworld.tscn`) between zones —
  24×24 chibi travel scale, terrain-gated walking, no map combat. Zones are the
  full-scale (48×48) shooter gameplay.
- **Magic is deferred by design** (world starts drained); ranged/spell systems unlock
  later as story-driven progression.
- **Art direction:** influenced by **Final Fantasy VI, Chrono Trigger, Secret of
  Mana, Sea of Stars, Adventure Time, and the Paper Girls comic** — FF6/CT sprite
  proportions, SoM's lush action-RPG feel, Paper Girls' surreal duotone color
  scripting; movement/perspective stays SNES-Zelda.

## Current state

Title screen → intro (night yard: Schweinler plants the poop bag → bedroom: bird
wakes Basil, clock close-up shows the alarm never rang → morning yard: he steps in
it → playable road with slimes → lecture-hall nickname scene) → OVERWORLD → Whisker
Meadow zone (the other four markers are locked with flavor text; leaving the meadow
returns to its marker via the `Game` autoload). Cutscene kit: `scene/cutscene.gd`
(awaitable say/walk/fade/card helpers, ESC skips) + `scene/dialog_box.tscn`
(typewriter box, bitmap pixel font in `assets/font/`). Player: walk/hop (straight up
when standing, air-steerable) / laser with recoil; slimes die in 3 shots. All art is
generated frame-consistent pixel art with a 16-bit shading pass — regenerate via
`assets/_gen_*.py` (see "Art pipeline" in docs/DESIGN.md). Main scene:
`scene/title.tscn`.
