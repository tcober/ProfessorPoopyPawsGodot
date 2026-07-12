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
  Full gamepad (PS5 DualSense) bindings live alongside the keys in the InputMap —
  see the Controls table in DESIGN.md; `reload`+`dart` share L2 (leader-contextual).
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
ALEMBIC TOWN → OVERWORLD → Whisker Meadow — to hone the battling and the
look. The
title screen, five-part intro, Schweinler's sprites, and the cutscene/dialog
kit were deleted (git history keeps them; the story stays in docs/DESIGN.md as
the plan). The game boots into Basil's loft bedroom (`scene/house.tscn`, main
scene) — a small dense CT-bedroom diorama floating in void (10-tile-wide room
on the 24×14 map), brown plank walls / teal weave / gold dawn window, E
toggles the curtains at the window; its SW staircase descends to the
**downstairs** (`scene/downstairs.tscn`) — the kitchen + steampunk-lab great
room (20-tile room, hearth fire = light source + glow, copper boiler,
workbench, alcove stairs back up) whose south front door opens into walkable
**Alembic Town** (`scene/alembic_town.tscn`, 56×34 on the shared overworld
driver — rebuilt from scratch 2026-07-11 as the Kakariko-style hub, LIVE in
the flow): the barred Academy crowns a north cliff terrace on the central
axis (authored 16×32 cliff-face columns, 3 salted variants stamped per
column; a grand stone stair descends to a lamp-flanked plaza), a fountain
square at the lane crossing (trail ring forks around the basin + brass
alembic finial; flask stall on the rim), the weapons shop "THE BRASS FANG" +
item shop "THE CRACKED FLASK" (ONE shared `town_shop` builder, SAME salt —
only roof/sign/wares differ so facade tiles dedupe), the two-story inn "THE
COPPER KETTLE" by the stream bridge (river + sea/beach pond classes at town
scale), locked cottages around the well + fenced garden, a fenced NE orchard,
and six walk-behind trees (canopy rows walk on the upper layer, trunk row
solid + opaque — dedupe rule); all shop/inn/cottage/school doors are
announce-only banners (caps-only font!), Basil's `home` door → downstairs
(`interior_spawn="front_door"`), the south gate (`exit_south`) → the
**tiled overworld**, where Alembic Town is a CT-faithful cluster ICON on the
SW coast (one DENSE drawn composition — seven small overlapping roofs with
dab openings, the Academy castle-keep, the steamworks' riveted copper boiler
venting a steam plume; darker mossy-emerald 2026-07 palette) whose gate-mouth
`D` marker (`town`) opens back into the town's south gate, with ONE winding
trail NE past Whisker Meadow (`scene/meadow.tscn` — slimes, beaker respawns,
HUD; marker `meadow`) over the river bridge to the wastes; steampunk-medieval
landmarks anchor the horizon — the Capital's pale-stone CASTLE on the north
massif (`C` cells) with the snowcapped HORN summit (`V`) at its NW tip, the
ELDER TREE (`g`, 64×96, ~5× the chibi, whole crown walk-behind — only
the trunk blocks) leaning over the riverbank, the
wastes' crystal OBELISK monument (`O`) + scattered 2×2 `K` crystal outcrops,
lit windows/coals/crystals on the glow overlay (the cloud-shadow shade
overlay was cut — dark ovals read as smudges at CT zoom); leaving a zone
returns to its marker via the
`Game` autoload. **The PARTY
(2026-07-10, SoM-style 2-member slice):** Basil leads, Fuji runs AI-companion,
**Q/Tab swaps the lead** (`swap_member`; camera `make_current`+
`reset_smoothing`, HUD row dim, modulate blink). No scene instances a player
anymore — the **`Party` autoload** (`scene/party.gd`, registered after `Game`)
`spawn()`s the roster `[basil, fuji]` into each zone's `World` and scenes keep
the returned leader as `player`; `leader_id` persists across scenes (HP
doesn't, as before). Group contract: **`player` = current leader ONLY** (all
door/exit/zone triggers gate on it, unchanged), **`party` = all members**
(slimes re-pick the nearest every frame), **`enemies` = live slimes** (brains
target it; left on death). Bodies extend **`PartyMember`**
(`entities/party/party_member.gd`, extends `DirectionalBody2D`): shared move/
hop/knockback/hurt/can't-die, driven per-frame by an `Intent` (move/face +
attack/secondary/jump edges) filled from `Input` when leading or from the
scene's `Brain` node (**`AIBrain`**, `entities/party/ai_brain.gd`) when
following. The brain is a three-MOOD machine — FOLLOW (stop/resume hysteresis
34/44px, sprint >56px) / ENGAGE (acquire nearest enemy ≤70px while ≤96px of
the leader, then LATCH it and hold to 140px — Basil's ~30px recoil skid
crosses any single line every shot) / RETURN (leash breaks past 128px → run
home to 48px IGNORING enemies before re-engaging; every boundary is a
two-threshold band because lone edges read as twitching) — its cooldown
decays in the brain's own `_physics_process` (think() pauses during kit/hurt
states), brains reset on leader swap, and the catch-up teleport fires only
>130px (must stay ≤ min view half-extent + margin, or a stuck follower sits
invisible and never comes home) AND OFF-SCREEN (live camera's
`get_screen_center_position()` + `MapData.view_size()`), landing a step
behind the leader only after a `test_move` sweep proves the step walkable
(else on the leader). `tools/party_probe.gd` asserts all of this
headlessly-ish (windowed): mood-transition count, no in-view pops, settle
distances — run it after touching brain/member code. Kits stay in the
subclasses behind `_process_kit`/`_on_attack_intent`/`_on_secondary_intent`:
**Basil** (`entities/player/` — instant-fire laser damage 2, recoil skid,
beaker mags, reload ritual; `basil_brain.gd` sidles onto a cardinal — 4-way
facing — fires in [36,110]px, reloads when dry, restocks off beaker pickups)
and **Fuji** (`entities/fuji/` — tortoiseshell librarian: warm-black fur,
PLACED rust patches, cream chin/chest/paws, green-gold eyes, brass reading
glasses, plum robe, tome hugged in the walk; **tome swing** attack — overhead
slam, BookHitbox shape-toggled through the strike/impact window, damage 2,
forward lunge — and **blow-pipe darts**, `dart`/L, unlimited, damage 1,
leaves on the puff frame at the 19px pipe-tip contract; `fuji_brain.gd`
closes to swing range and slams). HUD: one heart row per member (follower
dimmed 55%) + Basil's ammo pips/mags wherever he sits in the party. The
overworld travels as ONE chibi — the leader's (frames swap on entry). Slimes
explode in 2 book swings or 2 laser shots and a replacement respawns
elsewhere in the meadow.
GOTCHA fixed 2026-07-07: hand-authored .tscn node exports NEED
`node_paths=PackedStringArray("health_component")` on the node header or the
reference silently loads null (HurtboxComponent now also falls back to the
sibling HealthComponent in `_ready`). GOTCHA 2026-07-10: a NEW `class_name`
script needs `--headless --import` before headless runs see it (same
never-reimports rule as assets); and `tools/shot.gd`'s synthesized presses
exist only in the polled Input state — never as InputEvents — so testable
actions must be POLLED (`Party` polls `swap_member` in `_process`).
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
  + `.tres` + layout in `assets/tilesets/`; 60-77 tiles from 336 interior
  cells, ~605 from the overworld's 2304, ~450 from the town's 1904, ~145
  from the meadow's 1152) that
  `scene/tiled_map.gd` stamps onto TWO TileMapLayers — under and over
  entities, so bodies walk behind railings/lintels/ROOFLINES
  (`scene/house.tscn` = interior reference, `scene/overworld.tscn` +
  `scene/alembic_town.tscn` = exterior references, `scene/meadow.tscn` =
  combat-zone reference) — move a feature char in
  the map txt and it moves in-game. A NEW scene = map txt + thin config.
  **Z-ORDER DOCTRINE (2026-07-11, lint-enforced — full statement in
  DESIGN.md "Z-order / layering doctrine"):** draw order is the fixed
  sandwich lower tiles → y-sorted `World` entities → upper tiles; three
  tiers decide where art goes. Tier 1 terrain/flat/wall-flush props → lower.
  Tier 2 roofs/canopies/lintels → `place_split`, upper art ONLY above solid
  cells (or door cells) — every walk-behind corridor is capped by a solid
  `ridge` row (map digits, all named `ridge`, never a struct) so at most
  a head-peek crosses the silhouette; the cap is SCALE-GATED (`CHIBI_MAPS`
  in `_check_art.py`): the overworld's ≤1-tile chibi can't out-peek a
  silhouette, so its covered cells need no cap — the Elder Tree's whole
  crown is open walk-behind `G` cells, only the trunk solid. Tier 3 = anything a body can stand
  BOTH north and south of (free-standing furniture, street lamps/well/
  stall/fountain) — NEVER baked: `emit_prop()` writes the PNG + a
  `<scene>_props.txt` manifest row and `scene/prop_spawner.gd` spawns it
  into `World` at the feet convention (`node.y + 20`); counter-height
  pieces (desk/table/workbench) make their TOP footprint row `walk` so a
  body tucks in behind the tabletop. The collision box hugs the feet, so a
  pressed body sinks ~10px of sprite past a solid boundary in EITHER
  direction: a corridor's south edge needs the MASK BAND
  (`_town_props._eave_lift`: mirror the solid row's top 12px onto upper),
  legal ONLY with a ≥2-row solid base below the corridor (building
  facades, the elder trunk) — never on a 1-row solid between walk rows (a
  south head sinks ~10px into it too). Small-prop rule: anything without
  2 covered rows + a 2-row base (town trees) gets NO corridor — fully
  solid. `_check_art.py`
  fails the build on floating upper art (solid-cell mask bands exempt),
  uncapped corridors (waived on `CHIBI_MAPS`), misplaced ridge cells, an
  empty upper layer, a bad manifest, or a pressable solid cell whose tile
  dedupes to open ground (the INVISIBLE-WALL lint; Tier-3 manifest chars
  exempt — solid map cells under y-sorted sprites are fine). A 1-cell-thick
  forest/hedge line can't terminate in the open (the lobe lattice rejects
  the tip into a grass bay) — end it against another solid class or use
  fence cells.
  Sprites/fx build on `assets/_sprites.py`; collision is always an
  invisible TileMapLayer built at runtime by `scene/painted_map.gd` from the same
  map file. Regenerate via `assets/_gen_*.py`, then
  `python3 assets/_check_art.py`; eyeball scenes with `tools/shot.gd` (see "Art
  pipeline" in docs/DESIGN.md).
