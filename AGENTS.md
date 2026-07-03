# Agent Instructions — Professor Poopy Paws

This is a **Godot 4.6** (GDScript) top-down action-RPG. Any AI coding assistant working
in this repo should read the canonical design bible first:

➡️ **[docs/DESIGN.md](docs/DESIGN.md)** — story, themes, influences, asset specs, and
engine/architecture conventions (single source of truth).

Quick conventions: base resolution **640×360**, **32×32** tiles, nearest filtering;
**component-based architecture** (`components/` reusable nodes, `entities/` compose them,
`resources/` for data, `scene/` for rooms, `assets/` for art). Player is a
`CharacterBody2D` with 8-way movement / 4-way facing; combat is `Area2D` Hitbox vs
Hurtbox → HealthComponent. Structure: a **Chrono Trigger / Sea of Stars overworld**
is the travel layer (48×48 chibi sprites, no map combat); **zones** play as an
ALttP-style top-down laser-gun shooter (96×96 field sprites) — two sprite scales,
32×32 tiles everywhere (SNES composition at 2x pixel density; canonical Scale Table
in docs/DESIGN.md, constants in `assets/_artlib.py`, palettes in
`assets/_palette.py`). Magic is intentionally deferred (the world starts drained).
Art direction is influenced by **Final Fantasy VI, Chrono Trigger, Secret of Mana,
Sea of Stars, Adventure Time, and the Paper Girls comic** (see "Influences" in
docs/DESIGN.md).

Keep `docs/DESIGN.md` updated as the game grows.
