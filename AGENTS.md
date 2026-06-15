# Agent Instructions — Professor Poopy Paws

This is a **Godot 4.6** (GDScript) top-down action-RPG. Any AI coding assistant working
in this repo should read the canonical design bible first:

➡️ **[docs/DESIGN.md](docs/DESIGN.md)** — story, themes, influences, asset specs, and
engine/architecture conventions (single source of truth).

Quick conventions: base resolution **320×180**, **16×16** tiles, nearest filtering;
**component-based architecture** (`components/` reusable nodes, `entities/` compose them,
`resources/` for data, `scene/` for rooms, `assets/` for art). Player is a
`CharacterBody2D` with 8-way movement / 4-way facing; combat is `Area2D` Hitbox vs
Hurtbox → HealthComponent. Magic is intentionally deferred (the world starts drained).

Keep `docs/DESIGN.md` updated as the game grows.
