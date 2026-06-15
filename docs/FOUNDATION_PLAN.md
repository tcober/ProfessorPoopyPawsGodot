# Foundation Plan — Professor Poopy Paws

> The approved plan for the first build milestone, kept in-repo so any AI tool can read
> it. Design details live in [DESIGN.md](DESIGN.md).

## Goal
A **playable vertical slice**: one room where the science cat walks (8-way move, 4-way
facing), swings a sword, kills one slime, and has a heart-based HP bar — using
placeholder art so it runs immediately. Real sprite sheets drop in later against the
specs in [DESIGN.md](DESIGN.md#asset-specs-sprite-sheets-to-provide).

## Locked decisions
- First milestone: playable vertical slice (placeholder art).
- Resolution: **320×180**, 16px tiles (viewport changed from the original 318×216).
- Combat: **melee now**; magic/projectiles unlock later as story-driven progression.
- Art: placeholders now (`assets/placeholder/`), user supplies real sheets later.

## Build steps
1. **Docs** — `CLAUDE.md`, `AGENTS.md`, `docs/DESIGN.md`, this file. ✅
2. **Placeholder art** — generate `player_placeholder.png` (32×32),
   `slime_placeholder.png` (24×24), `hearts.png` (48×16) into `assets/placeholder/`.
3. **Project settings** — `project.godot`: viewport 320×180, `stretch/aspect=keep`,
   window override for a visible scale, main scene = `scene/test_room.tscn`.
4. **Components** (`components/`, reusable, story-agnostic):
   - `health_component.gd` (Node): `max_health`, `current_health`, `take_damage()`,
     signals `health_changed(current, max)` and `died`.
   - `hurtbox_component.gd` (Area2D): routes incoming hits to a HealthComponent.
   - `hitbox_component.gd` (Area2D): exported `damage`, enabled only during attack frames.
5. **Player** (`entities/player/`): `CharacterBody2D`, 8-way move, 4-way facing, enum
   state machine (MOVE/ATTACK/HURT), directional sword hitbox; composes the components.
6. **Enemy** (`entities/enemies/slime.*`): minimal chase AI, HealthComponent + Hurtbox,
   frees on `died`.
7. **HUD** (`scene/hud.*`): heart row bound to the player HealthComponent's
   `health_changed` signal.
8. **Test room** (`scene/test_room.*`): floor + wall colliders, player + slime, camera,
   HUD. Main scene.

## Verification (manual — it's a game)
1. Open in Godot 4.6, run main scene. Window renders 320×180 integer-scaled, crisp.
2. WASD/arrows move 8-way; facing snaps 4-way.
3. Attack (J / Space) swings and enables the directional hitbox.
4. Hitting the slime lowers its HP; enough hits frees it.
5. Slime contact damages the player; heart HUD updates via signal; death triggers.
6. No errors in the debugger output.
7. Asset swap-in (later): dropping a real sheet into the SpriteFrames needs no code
   changes to movement/combat.
