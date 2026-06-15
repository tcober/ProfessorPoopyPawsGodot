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
- Base resolution **320×180**, integer-scaled; **16×16** tiles; nearest filtering.
- **Component-based architecture:** reusable behavior as nodes/resources in
  `components/` (HealthComponent, HitboxComponent, HurtboxComponent). Entities in
  `entities/` compose them. Shared data as `Resource`s in `resources/`. Rooms/levels in
  `scene/`. Art/audio in `assets/`.
- Player: `CharacterBody2D`, 8-way movement, 4-way facing; sword swings in facing dir.
- Combat: `Area2D` Hitbox vs `Area2D` Hurtbox → HealthComponent.
- **Magic is deferred by design** (world starts drained); ranged/spell systems unlock
  later as story-driven progression.

## Current state
Vertical slice: 1 room, player walk + sword, 1 slime, heart HP HUD, placeholder art in
`assets/placeholder/`. Main scene: `scene/test_room.tscn`.
