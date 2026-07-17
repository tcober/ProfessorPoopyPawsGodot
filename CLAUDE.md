# Professor Poopy Paws

> **Full design bible: [docs/DESIGN.md](docs/DESIGN.md)** — single source of truth for
> story, themes, influences, asset specs, and conventions. Keep it updated as the game
> grows. This file is a quick-reference for Claude Code.

A Zelda: ALttP–style action-RPG with deeper RPG systems, tonal blend of **Adventure
Time** and **Final Fantasy**, about a science cat branded "Professor Poopy Paws" who —
after public humiliation and losing his girlfriend to a machine accident that erased
her memory of him — becomes a hermit, until the world's magic drains away in a single
night (**the Ebb**, natural/ancient — a mystery, never villain-made) and Fuji, a
librarian stranger who unearthed his old thesis, pulls him back to restore the world's
magic and find love again, with her. (Full chapter structure — Prologue A "Sparkless",
Prologue B "Professor Poopy Paws", Act 1 "The Ebb", Act 2+ "Re-Enchantment", cast,
lore spine, pacing rules — in docs/DESIGN.md "Story".)

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
kit were deleted (git history keeps them; the story lives in docs/DESIGN.md
"Story", now a full chapter structure — and **nothing narrative is ever
recovered from git**: the 2026-07-12 build-fresh doctrine).
**PROLOGUE A "SPARKLESS" IS LIVE (2026-07-12):** the game now boots into
`scene/prologue_open.tscn` (title + era cards; ESC skips to the adult
sandbox) and plays the childhood chapter end-to-end — kid Basil (playable,
`entities/kid/`, no kit: walk/hop/interact only, the pre-Ebb world is SAFE)
alone on the roster, **opening AT HOME on a scripted SUNRISE** (the
2026-07-15 narrative pass): `scene/house_fest.tscn` (the loft, bright tint) —
asleep in bed (kid sheet row 4: sleep/wake/sigh, 6×5 now) → eyes open → pads
to the window → curtains slide apart (house.gd's Curtains+Glow idiom, Theater
instanced) → a sigh → control →
the stairs → `scene/downstairs_fest.tscn` where MOM's good-morning by the
hearth (`prologue_saw_mom`) unlocks the front door into the Founding
Festival in the bright-era town
(`scene/town_fest.tscn`, `maps/town_fest.txt` — a BYTE COPY of town.txt in
the `town_fest` palette: spring grass, cream plaster, festival magenta;
keep the two grids in lockstep; the fest Academy door is OPEN —
`town_academy(open_door=True)`, sealed bars stay drained-only), the
fountain-square teasing cutscene fired
by a PROXIMITY zone when Basil first walks by the square (Sage
floats three ribbons, kid Schweinler coins "Sparkless", and the GOOSE THEFT
plays out mid-cutscene: it snatches a ribbon, Sage yells, it bolts over the
bridge and HIDES behind the orchard TreeCrown — `goose_hide`+16px east, head
over the leaves; startling it returns the ribbon; goose_chase.gd retired
2026-07-15), the WANDER GATE
(talk to any 3 of the six talkables — sheep matron / owl scholar / the goose
/ mouse kid / Sage / Schweinler, every line stings — then "I want to go
home"), the BLESSING DOUBLE-BACK (2026-07-15: Mom stays home; the home-door
re-entry zone — armed only after the arrival body steps off it — leads back
to the fest downstairs where her hearth blessing sets `prologue_gate_open`;
the front door softlock-guards until then), the prologue meadow
(`scene/meadow_fest.tscn`, same meadow map +
anchors, no slimes) where Kitty Cool's whirligig fetch-quest (gear on the
beach / spring in the flowers / crank by the boulders) ends in the flight
finale and the **crank-up mash** minigame + montage cards.
**PROLOGUE B "PROFESSOR POOPY PAWS" IS LIVE (2026-07-12):**
A's montage swaps to `basil_student` (kit-less adult, no gun) and hands to
`scene/town_thesis.gd` — ONE scene, four `Game.town_thesis_phase` phases
tinted by a CanvasModulate (plant/night, Schweinler creeping the LANES —
walk_via dog-legs, never through the blocks → `house_thesis` wake-up →
dash/morning with hop-the-puddles + paw-print trail → `hall` the naming
before a JUDGING PANEL — 112px desk() on a one-row `J` footprint, Dean +
stork/badger/sheep at `judge_1..4`, gallery packed 3-per-bench `aud_1..12` →
call/dusk: the WATCH CALL (fx row 2 watch face over Basil) → black →
**`scene/accident.tscn`** (2026-07-15/16, the accident SHOWN with CAUSE: a
partyless side-view set-piece — Schweinler brags to Ridley over the parked
machine, mounts against his warning and instantly loses control as Kitty
rides in; dusk-road painting `accident_bg.png` (one NARROW lane the 48px
cast fills), CHIBI-proportioned profile sheets `accident_kitty_gen`
pedal×2/brace/down + `accident_atv_gen` drive×2/swerve/skid/parked +
`accident_bike_down_gen`; poof + white Flash + instant black at impact,
never a contact frame; owns `prologue_accident`) → `sickroom` the
verdict — THE DOCTOR'S OFFICE (rebuilt 2026-07-16 on the loft-diorama
recipe: 8-tile interior floating in void, every wall stretch occupied,
clinical pale-teal bedding, new `privacy_screen`/`drip_stand` props +
the doctor's desk() as y-sorted entities, kitty_bed redrawn at full chibi
scale with the brow bandage; canonically the EAST NEIGHBOR COTTAGE — the
town door banners name it in both eras; never move
bedside/kitty_bed/doctor_spot) →
fountain/dusk the
"selfish" beat → leaving/night → `house.tscn`). New interiors on the Room kit
(`scene/hall.*` + `maps/hall.txt` + `_gen_tileset_hall.py`; `scene/sickroom.*`
likewise), new reusable interior props (`chalkboard`/`lectern`/`bench` in
`_interior_props.py`), new cast in `_gen_prologue_sprites.py` (Mom, adult
Schweinler, badger, stork, Kitty-in-bed), `prologue_fx.png` now TWO 16-cell
rows (256×32 — row 0 frozen byte-identical, row 1 = watch/poof/motion-lines;
`WorldFx.sheet_sprite` infers vframes from sheet height so old frame indices
survive; NEVER widen a row).
**KITTY THREAD (2026-07-16):** the brass wrist-watch comm is HERS — canon
threaded through existing beats: the dusk call answers the bookend with
"never once failed - pick UP", the leaving cards close "He kept the
watch.", the sickroom verdict gains the hands-remember narrator beat (her
paws folding pleats while she talks), and the adult downstairs HEARTH
MANTEL carries the whirligig relic (`downstairs.gd` `WHIRL_*`: fx-sheet
droop/spin frames, hearth-draft stir every ~7s, plain `$World` sprite
keyed north of any body). SAME-DAY PLAYABLE PASS: the **WORKSHOP
INTERLUDE** (`scene/workshop_interlude.gd/.tscn` — downstairs map in a
honey-rose evening tint between A's montage and B; college Kitty
`npc_kitty_adult_gen` behind the KITCHEN TABLE — the **room-to-move
rule**: never park a solid NPC in a 1-cell corridor like the workbench's
E-row alley; gear/spring/crank fetch on the meadow pickup idiom — the
whirligig recipe on purpose — then the AWAITED talked-handler gift: the
watch fx's first blink, the front-row promise, outro cards → thesis day;
owns `prologue_watch_given` + `prologue_wpart_*`), the **plant phase went
SEMI-PLAYABLE** (opens at the Academy stair, walk home via doorstep
walk-gate, optional shuttered-stall line, then the bookend call — "that
watch keeps PERFECT time" — before Schweinler creeps), and **Kitty's
stall** (the fountain-rim `m` struct, located at runtime via bbox — no
map edit) is canonically hers: broken-axle cameo + banner during the
dash (why she misses the naming), shuttered-stall line before the dusk
call (why he phones, why she's on the road). Probe: 40 checks.
GOTCHA: an input-polling coroutine on `process_frame` must LEVEL-detect
(`is_action_pressed` + a latch), never `is_action_just_pressed` — the frame
signal can beat the same-frame press (killed the crank mash). Built on the
**narrative kit**:
`scene/dialog_box.gd/.tscn` (typewriter box, brass bevel, name plate, ▼
arrow, POLLED input, mixed-case text — lowercase glyphs shipped in
`assets/_pixfont.py`, lineHeight 9→10), `scene/theater.gd/.tscn` (awaitable
card/fade/say/walk/face/hop + lock_party via the "party" GROUP + **walk_gate**
(goal pos passed in; unlock → one-shot Area2D → await player → re-lock) — the
kit must never reference autoload identifiers, or --script probes poison its
compile), `entities/npcs/npc.gd/.tscn` (interact-to-talk, one-row 48px
sheets, SpriteFrames built at RUNTIME — a new villager is a PNG + exports),
`Game.flags` story flags, `Party.set_roster()` (typed
Array[StringName] — dynamic callers must pass a TYPED array). Cast sheets
from `assets/_gen_prologue_sprites.py`; probe:
`tools/prologue_probe.gd` (drives the whole chapter with synthesized
presses, asserts every flag; run it after touching story scenes).
**POLISH PASS (2026-07-12):** pacing is fixed with AGENCY, never cuts —
Prologue B hands control back FIVE times via `walk_gate` (lectern / hall
door / the pneumatic post — new fest anchor `post` / bedside / fountain;
`prologue_scolded` marks the fountain beat's end), no stretch runs ~45s
without movement. GATE GEOMETRY RULE (review pass): a walk-gate must be
UNAVOIDABLE for its objective — a point-rect is walkable around (hall
aisles, the fountain ring) and reads as a hang; use a full-width room band
(hall row 8, sickroom row 6) or the whole square zone (both town phases =
the fest cutscene's 96×96 fountain zone), then stage the last steps with
`walk_via` waypoints. Theater walks are straight NO-COLLISION tweens: any
scripted approach near the fountain must dog-leg the ring
(`_square_route`/`_post_route` in the town scenes). Runtime FX depth-sort
via **`scene/world_fx.gd`** — `decal()` (ground art: origin DECAL_BIAS=32px
north + child index 0 — the bias must exceed feet-offset 20 + half-cell 8
or a body standing ON the decal renders under it) / `airborne()` (origin
ground-anchored, art lifted by sprite `offset` only; tween the offset,
never the origin) — NEVER add FX to the scene root (paw prints died under
the floor to a z_index hack). The house_thesis bed spawn sits 4px north so
the quilt (origin 119) covers him. `bake_shadow(..., each=True)` for any
shared-char prop SET (the hall's four benches — a merged bbox smears the
band across the aisle). Refused exits need a wall: the gate-mouth road
runs to the map edge and collision only stamps grid cells
(`_wall_gate_mouth` in both town scenes). A talked-signal handler that
starts a dialog coroutine must AWAIT it before falling through to logic
that can start another (the Sage ribbon-return + want-home collision —
one advance press resumes BOTH pending say() awaits).
Invisible walls: the T3 coverage lint (a prop footprint cell stays solid
only if frame-0 art covers ≥20% of it — else retype to a walkable TWIN
char with the same terrain name: town `O/U/L`, hall `l`; paint stays
byte-identical) — but never open a walkable pocket inside a chase leash
(the goose wedged in the inn-nook lamp cell; reverted). Facades carry
`_eave_lift` TOP + SIDE mask bands (outer 6px columns; Academy included).
`tools/shot.gd` gained `phase:<name>` + `roster:<id>[:...]` +
`flag:<name>` + `pos:<x>:<y>` args, and both shot.gd and the probe pin
`Engine.max_fps = 60` (an OCCLUDED macOS window runs UNCAPPED ~2000fps —
frame budgets burn in real seconds while wall-clock cutscene timers don't
advance any faster; the 2026-07-16 harness gotcha).
The adult sandbox underneath is unchanged: `scene/house.tscn` — a small dense CT-bedroom diorama floating in void (10-tile-wide room
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
