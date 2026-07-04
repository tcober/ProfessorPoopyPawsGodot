# Agent Instructions — Professor Poopy Paws

This is a **Godot 4.6** (GDScript) top-down action-RPG. Any AI coding assistant working
in this repo should read the canonical design bible first:

➡️ **[docs/DESIGN.md](docs/DESIGN.md)** — story, themes, influences, asset specs, and
engine/architecture conventions (single source of truth).

Quick conventions: base resolution **384×216** (16:9, 5x → 1080p; 3x dev
window), **16×16** tiles, nearest
filtering; **component-based architecture** (`components/` reusable nodes, `entities/`
compose them, `resources/` for data, `scene/` for rooms, `assets/` for art). Player is
a `CharacterBody2D` with 8-way movement / 4-way facing; combat is `Area2D` Hitbox vs
Hurtbox → HealthComponent. Structure: a **Chrono Trigger / Sea of Stars overworld**
is the travel layer (24×24 chibi sprites, no map combat); **zones** play as an
ALttP-style top-down laser-gun shooter (48×48 field sprites) — two sprite scales,
16×16 tiles everywhere (TRUE SNES density, Chrono Trigger chunk; canonical Scale
Table in docs/DESIGN.md, constants in `assets/_core.py`, palettes in
`assets/_palette.py`). Magic is intentionally deferred (the world starts drained).
Art direction is influenced by **Final Fantasy VI, Chrono Trigger, Secret of Mana,
Sea of Stars, Adventure Time, and the Paper Girls comic** (see "Influences" in
docs/DESIGN.md).

Keep `docs/DESIGN.md` updated as the game grows.
