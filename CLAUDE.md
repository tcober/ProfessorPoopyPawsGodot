# Professor Poopy Paws

> **Full design bible: [docs/DESIGN.md](docs/DESIGN.md)** — single source of truth for
> story, themes, influences, asset specs, and conventions. Keep it updated as the game
> grows. This file is a quick-reference for Claude Code.

A Zelda: ALttP–style action-RPG with deeper RPG systems, tonal blend of **Adventure
Time** and **Final Fantasy**, about a science cat branded "Professor Poopy Paws" who —
after public humiliation and losing his girlfriend to a machine accident that erased
her memory of him — becomes a hermit, until the world's magic drains away in a single
night (**the Ebb**, natural/ancient — an EARTHQUAKE that crystallized the big
mountain's summit and visibly drank the world's magic into it; a mystery, never
villain-made) and Fuji, a
librarian stranger from snowbound Lanternwood who unearthed his old thesis, pulls
him back to restore the world's
magic and find love again, with her. (Full chapter structure — Prologue A "The Whirligig",
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
- **COMPOUNDS (2026-07-20):** a beaker is a colour-coded ammo TYPE
  (`resources/compound.gd`) — green `base` (the original laser, dmg 2 ×6) / blue
  `frost` (chill → brief freeze) / red `flame` (short-range sprayer + burn DoT) /
  purple `plasma` (dmg 4, PIERCES, ×3). `M` opens the **mixing bench**
  (`scene/mix_menu.gd`, 4th autoload) to fuse two spares into one under three rules
  in `resources/alchemy.gd`: same+same CONCENTRATES, green+anything DILUTES (green
  is the inert solvent — keeps the common drop useful all game), red+blue = purple;
  everything else is refused with a reason, never silently eaten. ONE bolt scene
  serves all four — `bolt.apply_compound(c)` sets damage/speed/lifetime/effect/
  pierce/tint the way `direction`/`shooter` already are. The loadout (`loaded`,
  `spares`, `ammo_left`) lives on **`Game`**, because `Party.spawn()` rebuilds every
  body at each door; `reset_story()` blanks it so a backwards chapter jump can't
  carry plasma into a scene that predates the gun. HUD tints the ammo pips to the
  loaded kind and each spare icon to its own — no new row, no new art.
- Combat: `Area2D` Hitbox vs `Area2D` Hurtbox → HealthComponent. `LaserBolt` projectile.
- **STATUS AILMENTS (2026-07-20):** `components/status_component.gd`, composed onto
  enemies. Payload rides the one chokepoint —
  `take_hit(damage, source, effect := NO_EFFECT)` with `effect` a small Dictionary
  (`{"drowse":1}`/`{"chill":1}`/`{"burn":4}`; the const default avoids allocating per
  hit). **Fuji's darts are SLEEP darts** and sleep is a BUILDUP, not a flag: each dart
  adds drowse, crossing `drowse_threshold` drops the target (still + contact hitbox
  OFF), it takes NORMAL damage and does NOT wake on being hit, and a bigger enemy just
  raises the threshold — hence `BigSlime` (`entities/enemies/big_slime.*`, bruise-violet,
  10 HP, threshold 5, 30% of meadow respawns). Distinctness rule: sleep is slow/long/
  total, freeze is instant/partial/short, burn disables nothing.
  GOTCHAS, all three already cost real bugs: (1) buildup needs a GRACE WINDOW before
  decay resumes or the threshold lies (decay nibbles between the darts of a burst — a
  "2 dart" enemy took 3); (2) disabling contact damage toggles the Hitbox's collision
  SHAPE, never `monitoring` — re-enabling monitoring does not re-scan an overlap that
  never ended, so an enemy woken while touching the player stays harmless forever;
  (3) burn ticks go straight to `HealthComponent`, never back through `take_hit`, or
  the hurtbox's `invincible_time` eats most of them.
  Probe: `tools/status_probe.gd` (50 checks — statuses, mixing rules, loadout survives
  a scene change, `reset_story` clears it); `tools/status_shot.gd` poses the tells and
  the bench for eyeballing. NOTE a `--script` probe must NOT name the `Player` class:
  that drags `player.gd` into the tool's own compile, which happens BEFORE autoloads
  register, so its `Game.` references fail and poison the run — duck-type it instead.
- **Overworld layer:** CT/SoS-style TILED travel map (`scene/overworld.tscn`)
  between zones — 24×24 chibi travel scale (~16 px figure), terrain-gated
  walking, no map combat; since 2026-07-19 the **FIVE LANDS**: a 112×63
  ocean-separated continent (NO walkable crossing between lands — the boat
  is future story), two eras on the fest byte-copy pattern
  (`overworld_bright.*` pre-Ebb / `overworld.*` post-Ebb default; grids
  BYTE-LOCKED). Towns are CT-faithful cluster ICONS (one drawn
  composition of overlapping roofs, solid except its gate-mouth `D` cell,
  which travels INTO the town's walkable zone scene). Region edges are drawn
  as 1-cell stair-steps in the map txt — the autotile's 45° corner cuts
  render them as continuous diagonals. Zones are the full-scale (48×48)
  shooter gameplay; walkable **Alembic Town** (`scene/alembic_town.tscn`)
  and **Lanternwood** (`scene/lanternwood.tscn`, Fuji's snow town) are
  zones too, riding the same overworld tile driver.
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
**PROLOGUE A "THE WHIRLIGIG" IS LIVE (2026-07-12; renamed 2026-07-18 —
the "Sparkless" nickname and all "spark" magic-talk were CUT as corny;
dialogue just says Basil can't do magic):** the game now boots into
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
by a PROXIMITY zone when Basil first walks by the square (2026-07-17
readability pass: Sage HAILS him — "BASIL! HEY! Over HERE!" — before the
scripted walk, her three ribbons float over HER OWN head, and the GOOSE
THEFT is a sneak FLY-BY (2026-07-18 — the announced waddle-in was cut):
no narration, a swoop in from off-screen west on the goose sheet's new
fly cells 6-7 (scene-local "fly" clip; npc.gd keeps `frame_cols=6`), the
lowest ribbon swapped to a carried goose-child at a mid-glide tween
callback — same fx cell stolen/carried, no mid-flight color swap — out
past the east edge, and only THEN Sage: "...did that goose just steal my
RIBBON!?"; it HIDES behind the orchard TreeCrown —
`goose_hide`+16px east, head over the leaves; startling it returns the
ribbon), the WANDER GATE
(talk to any 3 of the six talkables — sheep matron / owl scholar / the goose
/ mouse kid / Sage / Schweinler, every line stings — then "I want to go
home"), the BLESSING DOUBLE-BACK (2026-07-15: Mom stays home; the home-door
re-entry zone — armed only after the arrival body steps off it — leads back
to the fest downstairs where her hearth blessing sets `prologue_gate_open`;
the front door softlock-guards until then) → the south gate climbs
straight to **THE BLUFF** (2026-07-18: `meadow_fest` was DELETED — the
whirligig quest moved onto the headland; remember to keep
`scene/meadow.tscn`, the SEPARATE combat meadow): `scene/bluff.gd/.tscn`,
a headland scene (`maps/bluff.txt` + `_gen_tileset_bluff.py`, the `bluff`
sunset palette: gilded grass / evening indigo sea), staged FROM BEHIND
(the 2026-07-17 restage): the sea runs across the NORTH under a baked
**SKY BAND** (2026-07-18: opaque `$Sky` overlay art down to a horizon
line at y=28 — `bluff_sky_day.png` / `bluff_sky_dusk.png` swapped per
phase; the sea used to run to the frame top and read as a night sky),
the setting SUN + its glint lane live on the additive `$Glow`
(`bluff_glow.png` — fading the glow IS the sunset), and `$Stars`
(`bluff_stars.png`, additive twinkles + moon + a silver moon-glint lane)
fades IN as night falls: `_set_hour()` snaps a phase's light,
`_fall_night()` tweens Dim+Glow+Stars in parallel (the town_thesis
nightfall idiom), `_twinkle()` alpha-pulses the field. The drop is a
1-row authored cliff-LIP band, a WINDSWEPT TREE (Tier-3 prop on a solid
`t` cell) leans over the lip — the cast faces the water backs-to-camera
(player `idle_up`; Kitty's `back`/`side` cells, sheet cols 6-9 — npc.gd
builds them only when `frame_cols` >= 8/10) and turns to PROFILE for the
face-to-face lines — with FOUR `Game.bluff_phase` beats over one warm
painting — **meet** (DAY, kid roster: Prologue A's whirligig quest lives
here now — kid Kitty + the whirligig at `whirligig`, gear/spring/crank at
the `part_*` anchors, `prologue_part_*` flags, the crank-up mash minigame
(LEVEL-edge input — see the GOTCHA below) + flight finale + montage
cards, `prologue_whirligig_done`, then the scene RELOADS ITSELF as)
**romance** (sunset, `basil_student`: the watch gift EXPLODES on the
handoff, pieces fly to the SAME `part_*` anchors — the whirligig recipe
on purpose — the pickup gather, the AWAITED refit, Basil's first
`look_watch`, THE KISS — the composed two-cat sheet `bluff_kiss_gen.png`,
three 96px frames lean / KISS / after swapped in over the hidden bodies —
then the sun goes down WHILE THEY WATCH: `_fall_night` ×2 to full night
+ starfield + a held SILENT beat — owns
`prologue_wpart_*`/`prologue_watch_given`/`prologue_romance` → thesis
day), **call1** and **call2** (below; both calls sit beneath the tree,
call1 deepening dusk→late un-awaited under the talk, call2 opening late
and AWAITING the fall to full night on screen before one line — Basil's
"...Where is she?" — and ending on a REAL bolt back down the headland,
mid-run at the cut (the old beat played walk_side standing in place)).
**THE NARRATION PURGE (2026-07-18):** every `say("")` narrator box was
CUT chapter-wide — environment cues and in-character dialogue carry
those beats now (the sky does the nightfall, the hop does the squelch,
Schweinler's own brag carries the engine catch, Basil voices the
hands-remember beat, the door-bang is staged bodies snapping round).
Never add a narrator box to a story scene. The same-day CARD PURGE
extends the rule to the black-screen cards: a card may ONLY state how
much time passed ("THE NEXT MORNING.", "THREE SUMMERS LATER.", "THAT
EVENING." — which replaced "THE NAME STUCK.", "YEARS LATER.") — every
commentary card (the summer-montage trio, the watch/sunset pair, "He
did not tell her who he was.", the leaving trio incl. "He kept the
watch.") was CUT; the prologue_open title/era cards stay.
**PROLOGUE B "PROFESSOR POOPY PAWS" IS LIVE (2026-07-12):**
the bluff's cards hand to
`scene/town_thesis.gd` — ONE scene, three `Game.town_thesis_phase` phases
tinted by a CanvasModulate (plant/night: the earned-it doorstep call —
"potions" vs CHEMISTRY, never "youngest professor" (the 2026-07-17 theme
reframe) — then Schweinler creeping the LANES —
walk_via dog-legs, never through the blocks → `house_thesis` wake-up →
dash/morning — the step onto the bag is SHOWN (2026-07-18: door-mouth
spawn, the bag visible at `home + BAG_OFF` from frame one — the same
spot Schweinler drops it at night — a scripted bolt south ONTO it, the
SQUELCH, the bag fades) — then a clean run + paw-print trail (the puddle
hop was CUT 2026-07-17) → `hall` the naming — RESTAGED 2026-07-18 as a COLLEGE hall
(map 24×18; camera pans the 72px overflow): the whole north band is a
raised STAGE closed by the apron riser (`D` solid row + the full-width
`stage_front()` y-sorted entity — opaque across its footprint, the T3
coverage rule), reachable ONLY via its WEST WING, dressed since the
same-day curtain pass as a true proscenium: scalloped red VALANCE + slim
east drape baked Tier-1 into the front wall (`_stage_dressing()` — lower
layer can never occlude a tuck-row head) and the WEST CURTAIN LEG
(`curtain_leg()`, y-sorted T3 on its one solid `c` cell, origin y60
beats every stage body) — Basil spawns behind it
(stage right), the walk-in gate is the band across the stage rows just
west of the podium (the wing corridor makes it unavoidable), and the
flee is swallowed back behind the leg after one crushed "But... I...",
Schweinler's "'BUT'?! HA! HE SAID BUTT!" encore, and a held `bow_head` —
the walk-out itself is the SLOW `defeat_walk` trudge (20px/s, head on
his chest; a hand-rolled tween, theater.walk would override the clip)
whose last steps fade his modulate to 0 behind the leg, because the
~33px figure is WIDER than the 24px drape and a parked body leaves a
tail hanging past the fabric;
the podium (lectern, one-row `lLLl`
counter-walk footprint) front-CENTER, Basil presenting from the tuck row
BEHIND it, the JUDGING PANEL's 96px desk() stage-LEFT/east, Dean +
stork/badger/sheep at `judge_1..4`, Schweinler heckling from the east
aisle. The house is THREE TIERS of B/E benches — 18 audience
(`aud_1..18`, `frame_cols=8`) seated BACKS to the camera on new back
cells (sheep/mouse/badger sheets grew cols 6-7 = 384×48; owl/stork stay
6 — NEVER `play_emote` a back-turned head, it flips to a front face);
the laugh is a looped staggered `position:y` bob per head (`_laugh_bob`)
while only the front-facing panel + Dean emote, and Basil starts the
AUTOMATIC flee AS the laugh erupts (the chant plays over the walk) → bluff
**call1**/dusk: Basil SITS on the lip, SHE calls ("I'm coming. Stay right
there.") → **`scene/accident.tscn`** (the accident SHOWN with CAUSE: a
partyless side-view set-piece — Schweinler brags to Ridley over the parked
machine, mounts against his warning and instantly loses control as Kitty
rides in; dusk-road painting `accident_bg.png` (one NARROW lane the 48px
cast fills), CHIBI-proportioned profile sheets `accident_kitty_gen`
pedal×2/brace/down/TUMBLE (5 cols) + `accident_atv_gen`
drive×2/swerve/skid/parked + `accident_bike_down_gen`; impact reworked
2026-07-17 to the LOOP-AND-LAND: soft flash, the tumble curl spun TAU on
a parabolic arc, landing into the still `down` frame — never a held
contact frame; Ridley RUNS to the wreck under a tweened dusk Dim; owns
`prologue_accident`) → bluff **call2**/night: her watch calls his,
RIDLEY's voice on it → `sickroom` the
verdict — THE DOCTOR'S OFFICE (rebuilt 2026-07-16 on the loft-diorama
recipe: 8-tile interior floating in void, every wall stretch occupied,
clinical pale-teal bedding, new `privacy_screen`/`drip_stand` props +
the doctor's desk() as y-sorted entities, kitty_bed redrawn at full chibi
scale with the brow bandage; canonically the EAST NEIGHBOR COTTAGE — the
town door banners name it in both eras; never move
bedside/kitty_bed/doctor_spot; the verdict carries the WORLD-SPIRIT lore
2026-07-18 — magic mends anything but memory, a lost memory returns to
the spirit of the world and lives on out there, maybe surfacing elsewhere
someday — and ends on KITTY'S MOTHER bursting in from the door anchor,
`npc_kittymom_gen.png` the older-ginger matron w/ berry shawl + Kitty's
blue eyes, gasp `act` / accusing-point `emote`: Basil admits she was
riding to see him, the mother banishes him — "never near my daughter
again"; he tries "But - I -", she cuts him down with "LEAVE." and he
turns and walks himself out the door before the fade (2026-07-18: the
old accepting "...I understand." was cut) — the human rejection that
exiles him) →
steps/dusk (2026-07-17, replaces the fountain beat): out the doctor's
door onto the clinic stoop — `sit`, Ridley's blunt "perspective" speech
and exit, Basil's one "..." + `bow_head`, night falls → the scripted
leaving (RESTAGED 2026-07-18 to the SOUTH GATE): the `knapsack` tableau
on the central road, the `knapsack_back` LOOK-BACK at the town — "I wish
I could have been welcome here" — then a profile flash (the turn) into
the `knapsack_walk_down` trudge south out the gate mouth, FACING the
camera (2026-07-19 — the old side-profile walk tweened south read as a
sideways glide) → cards ("YEARS LATER.") → THE EBB NIGHT, below —
2026-07-19/20, the cards no longer hand to `house.tscn`). New interiors on the Room kit
(`scene/hall.*` + `maps/hall.txt` + `_gen_tileset_hall.py`; `scene/sickroom.*`
likewise), new reusable interior props (`chalkboard`/`lectern`/`bench` in
`_interior_props.py`), new cast in `_gen_prologue_sprites.py` (Mom, adult
Schweinler, badger, stork, Kitty-in-bed, Kitty's mother), `prologue_fx.png`
now TWO 16-cell
rows (256×32 — row 0 frozen byte-identical, row 1 = watch/poof/motion-lines
+ the kiss HEART at cell 19 + the Ebb magic sparks at 20-21 (bright/dim,
2026-07-19); `WorldFx.sheet_sprite` infers vframes from
sheet height so old frame indices survive; NEVER widen a row). Adult
Basil's sheet gained row 8 (2026-07-17, `basil_gen.png`; the tres
only APPENDS): `look_watch` (the raised-wrist call gesture that replaced
every floating watch fx) / `sit` / `bow_head` / `knapsack` + 2-frame
trudge — the knapsack is a true BINDLE ON A STICK since 2026-07-19 (the
2026-07-18 stickless bundle read as a lumpy raised ARM): hand-pinned
warm burlap `SACKR` + wood `STICKR` (ramp()'s violet law turned the
orange seed red, so both are hand-pinned), the stick ONE tip-to-grip
line whose middle hides behind the huge head (the classic
behind-the-head pass — bundle slung HIGH so the steep rear run reads
against the sky) and whose front end is redrawn OVER the fist (pole
through the paw = the grip; sleeve/paw first, stick last — a sleeve
drawn after the stick covers it, and a white paw on the white
cheek/coat vanishes without a sh tint) — and row 9 (sheet now 6×10):
`knapsack_back`, the south-gate look-back with the pack on his back +
the stick tip poking past the left ear, cols 1-2 (2026-07-18) the
`defeat_walk` pair — the knapsack stride empty-pawed with the head
bowed into the collar, ears back, eyes shut (the hall walk of shame) —
and cols 3-5 (2026-07-19) `knapsack_down` + the 2-frame
`knapsack_walk_down` trudge: the south-gate exit walking INTO the
camera, sad eyes + drooped ears, bindle over the screen-left shoulder.
**THE EBB NIGHT IS LIVE (2026-07-19/20; story canon REWRITE):** the Ebb is
an EARTHQUAKE — the big mountain's summit transforms into a GIANT GLOWING
CRYSTAL and the world's magic visibly drains INTO it, sparks streaming home
from every horizon (still natural/ancient/author-less, Schweinler never the
world's villain; "the Drain beneath the eastern wastes" canon is DEAD — the
summit crystal IS where the magic went, and WHY the mountain drank the
world stays the standing mystery). Flow: Prologue B's leaving cards →
`scene/ebb.tscn` (partyless cutscene over the big mountain: BOTH era
tilemaps stamped, deep-indigo night, escalating wall-clock quake, ONE white
flash swaps bright for drained + crystal ignition on the same cut, 14
additive spark motes sucked home to the summit, held silence; polled
LEVEL-detect skip on accept/cancel/attack, armed after 1s; sets
`ebb_done`) → `scene/library.tscn` phase "ebb" (the `Game.library_phase`
read-and-clear router): **FUJI'S FIRST APPEARANCE** — her Lanternwood
reading room at night (`maps/library.txt` + `_gen_tileset_library.py`, the
`library` palette), wand-made coffee whose sparks keep missing the kettle
(wild motes pop poof decals — the mess), the quake on her floor, "...That
was scary. ...Everything seems okay, though?", then the next wand flick
makes NOTHING — no spark at all — and **the story STAYS WITH HER**
(2026-07-20, NO card: no time passes between her floor and the street):
`Party.set_roster([&"fuji"], &"fuji")` + `Game.town_spawn="library"` →
`scene/lanternwood.tscn`, whose `_ebb_night_town()` (gated on `ebb_done`)
lands her a step south of her own library door under a deep night tint the
fire-lit windows and oil lanterns burn straight through — Lanternwood's
name made diegetic, honest flame owes magic nothing — with three
interact-to-talk villagers comparing charms that all died at once (Bramble
the snow hare / Alder the elderly beaver / Pip the fox kid; nobody blames
anybody — the Ebb has no author). **THE STORY RESTS HERE: playable solo
Fuji**; the adult Basil sandbox is reached only via prologue_open's ESC
skip, which also sets `ebb_done`. **FUJI CANON (2026-07-19):** she is the
LANTERNWOOD librarian — keeper of the little library in her snow town —
NEVER the Alembic Academy archivist (superseded); how his thesis reached a
Lanternwood shelf + how she crosses the ocean (the boat) are open Act 1
hooks. New art: `npc_fuji_gen.png` (480×48, 10-col NPC sheet: idle /
act=wand-cast / emote=startled / back / side) + the fx sparks above. New
Game state: `ebb_done` flag + `library_phase` router + the
`town_spawn="library"` route.
**KITTY THREAD (2026-07-16; the gift restaged onto the bluff 2026-07-17):**
the brass wrist-watch comm is HERS — canon threaded through the beats: the
bluff calls answer the doorstep bookend, the leaving cards close "He kept
the watch.", the sickroom verdict gains the hands-remember narrator beat
(her paws folding pleats while she talks), and the adult downstairs HEARTH
MANTEL carries the whirligig relic (`downstairs.gd` `WHIRL_*`: fx-sheet
droop/spin frames, hearth-draft stir every ~7s, plain `$World` sprite
keyed north of any body). The **room-to-move rule** stands: never park a
solid NPC in a 1-cell corridor. The **plant phase is SEMI-PLAYABLE**
(opens at the Academy stair, walk home via doorstep walk-gate, then the
bookend call — "that watch keeps PERFECT time" — before Schweinler
creeps). **The stall canon was CUT (2026-07-18):** the fountain-rim `m`
stall is generic scenery again; Kitty's wheel WORKSHOP is off-screen,
never seen — the busted-axle job there is why she misses the naming and
why she's on the dusk road, and the excuse is told ONLY in her call1
apology on the bluff. Probe: 46
checks (2026-07-20 — the tail asserts the Ebb → library → Lanternwood
chain, the solo-Fuji roster, and a peopled Ebb-night street). **DOOR-MOUTH ARRIVALS (2026-07-17):** leaving an interior lands
the body ON the door marker/zone (feet on the lane under the arch — the
old tile-and-a-half drop read as appearing nowhere near the door);
`_standing`/`_home_armed` suppress the re-fire until the body steps off
once, and interior front-door spawns/exits x-center on the 2-cell door
bbox. **Interior south walls carry a `south_lift()` mask band** (the
`_eave_lift` twin in `_interior.py`: top 12px of body-pressable `#` south
cells mirrored to the upper layer — no more standing ON the bottom wall);
town-building smoke RISES into `SMOKE_PAD` sky rows padded atop the
animated sheets (`_town_props._pad_top` — bottom-anchored props extend up
free; the old sideways puffs clipped flat at y=0).
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
**POLISH PASS (2026-07-12; reshaped 2026-07-17):** pacing is fixed with
AGENCY — Prologue B hands control back FOUR times via `walk_gate` (the
walk home / the hall stage / the bluff lip / the bedside;
`prologue_scolded` marks the steps beat's end) — but the hall walk-OUT
and the steps/leaving ending are deliberately AUTOMATIC (his body giving
up IS those beats). GATE GEOMETRY RULE (review pass): a walk-gate must be
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
**THE DEV CHAPTER SELECTOR (2026-07-20): press `0` ANYWHERE** — title,
cutscene, mid-meadow — for a paused two-column menu of all 32 story beats;
pick one and land in it with roster/phase/spawn/flags staged. `scene/dev_menu.gd`
(autoload `DevMenu`, third after Game/Party; overlay built in code on
CanvasLayer 100, `PROCESS_MODE_ALWAYS`, one of the project's only TWO
`get_tree().paused` uses — `MixMenu` is the other, and the two refuse to open
on top of each other so closing one can't unpause the tree under the other;
all-polled input; the whole thing behind `OS.is_debug_build()`) reads the
beat table in **`scene/chapters.gd`** — deliberately `class_name`-free and
autoload-free so `--script` tools can `load()` it, which is how `tools/shot.gd`
gained **`beat:<n>`** (stages a whole beat in one arg and can stand in for the
scene path — the only way to shoot the beats needing `town_spawn` /
`interior_spawn` / `library_phase`, none of which has an arg of its own).
`Game.reset_story()` clears flags + blanks the routers first, because
`set_flag` is one-way and a BACKWARDS jump would otherwise carry a later
chapter's flags into an earlier scene. Toggle key is `0` only, NOT ESC:
autoloads process before the current scene, so unpausing on ESC hands the same
still-pressed ESC to prologue_open's skip in that very frame. Gotchas the
table encodes: **roster is a SpriteFrames contract** (sleep/wake/sigh are
kid-only, sit/look_watch/bow_head/knapsack*/defeat_walk adult-only — the wrong
body plays a beat as error spam and a frozen pose); never an EMPTY roster
(`party.gd` indexes `ids[0]`); never kid/student into the meadow (no Brain
node, no kit); group headings clip to one column (~30 chars). Adding a beat =
one row in `chapters.gd`.
The adult sandbox underneath is unchanged (though the live story flow now
ends on Fuji in Lanternwood — the sandbox is entered via prologue_open's
ESC skip): `scene/house.tscn` — a small dense CT-bedroom diorama floating in void (10-tile-wide room
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
`D` marker (`town`) opens back into the town's south gate. Since 2026-07-19
the map is the **FIVE LANDS** (112×63, every landmass OCEAN-SEPARATED — no
walkable crossing, the boat is future story). SW FOREST LAND = the playable
core: the town icon, ONE winding
trail NE past Whisker Meadow (`scene/meadow.tscn` — slimes, beaker respawns,
HUD; marker `meadow`) over the river bridge, and the HOME TREE (`g` trunk /
`G` walk-behind canopy, 96×144, ~6× the chibi — only the trunk-core blocks)
leaning over the SE coast: Basil's hermitage, arched lit door + round
window + flue (interior future; renamed from the Elder Tree). CENTRAL
MOUNTAIN LAND = the Kingdom: the Capital's pale-stone CASTLE (`C`) on the
massif, the snowcapped HORN (`V`), and THE BIG MOUNTAIN (`B`, 14×10) —
pre-Ebb a snow summit, post-Ebb the GIANT CRYSTAL the magic drained into,
ablaze on the glow overlay. NW ICE/SNOW LAND = a pine-forested winter
island (`i` snow, `P` pines) carrying LANTERNWOOD (`L` cluster icon, `d`
gate → `scene/lanternwood.tscn`) — Fuji's hometown: visible but
ocean-locked until the boat; the zone itself is walkable — log cabins as
4-frame T3 sheets with fire-lit flickering windows + woodsmoke, conifers,
a frozen pond (Tier-1 ice over WALKABLE pond cells — never sea/river,
those animate), announce-only banners (THE LANTERNWOOD LIBRARY / FUJI'S
FAMILY HOME / three cabins), `road_verge="snow"` lanes. NE PURPLE DESERT
(`b`) + E/SE LAVA LAND (basalt `a`, ANIMATED lava pools `l` — the
LAVA-RING LAW: every lava cell's neighbors must be lava or basalt,
asserted at build) share one eastern landmass split by a volcanic ridge;
MYSTERIOUS ISLANDS offshore, unreachable. The old waste/obelisk/Burrows
geography is GONE. Two-era map: `overworld_bright.txt/.tscn` = the
byte-locked pre-Ebb twin (snow summit, mint glow; staging/screenshots +
the Ebb scene only). Lit windows/coals/crystal on the glow overlay (the
cloud-shadow shade
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
and **Fuji** (`entities/fuji/` — tortoiseshell Lanternwood librarian: warm-black fur,
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
  map, walkable Alembic Town, Whisker Meadow AND Lanternwood: terrain
  fabrics — grass/forest
  carry a 32-periodic phase on interior cells; the 2026-07-19 five-lands
  classes **snow** (wind-scour drifts), **desert** (purple dune sand),
  **basalt** (violet-charcoal crust), **lava** (solid, ANIMATED 4-frame —
  the sea/river cycle's mirror) and **pines** (snow-dusted conifer mass on
  its own ramp); the `road_verge` knob: "grass" default, "snow" in
  Lanternwood — + neighbor-keyed CT autotile
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
  `_hatch_px` linework, cluster_shade finishing: town + LANTERNWOOD
  cluster ICONs, the
  castle, the Horn peak, the HOME TREE, the `big_mountain`/`crystal_summit`
  era pair (224×160, same salt — byte-identical rock, only the summit
  differs), lone trees; obelisk + crystal outcrops stay in the library but
  are off-map since the five lands) + `assets/_town_props.py` (zone-scale
  facades: Basil's
  cottage, cottages, the Academy, well/lamp/stall — plus the 2026-07-19
  winter kit: `town_cabin` (log walls, snow gable, stone chimney,
  `wide=True` library-hall variant), `town_conifer` T3 trunk/crown pair,
  `frozen_pond`, `town_lamp(mantle=)`; `_anim_building` gained `windows=`
  (baked 4-frame warm flicker) + `wood_flues=` (grey lazy woodsmoke) +
  `_finish(pad=)`, all default-off — town/fest sheets proven
  byte-identical) + `assets/_meadow_props.py`
  (the meadow's per-cell boulder domes + the trailhead cairn).
  A generator (`assets/_gen_tileset_house.py`, `_gen_tileset_downstairs.py`,
  `_gen_tileset_overworld.py` + its byte-locked pre-Ebb twin
  `_gen_tileset_overworld_bright.py`, `_gen_tileset_town.py`,
  `_gen_tileset_meadow.py`, `_gen_tileset_lanternwood.py`,
  `_gen_tileset_library.py`) is a thin config:
  palette + pools/terrain + `place()` props at map feature chars;
  `assets/_tiles.py` slices the composed canvases into a real TileSet (atlas
  + `.tres` + layout in `assets/tilesets/`; 60-77 tiles from 336 interior
  cells, ~1170 from the five-lands overworld's 7056 (~700 of them animated
  water/lava), ~190
  from the town's 1904, ~144 from the meadow's 1152, ~100 from
  Lanternwood's 1232) that
  `scene/tiled_map.gd` stamps onto TWO TileMapLayers — under and over
  entities, so bodies walk behind railings/lintels/ROOFLINES
  (`scene/house.tscn` = interior reference, `scene/overworld.tscn` +
  `scene/alembic_town.tscn` = exterior references, `scene/meadow.tscn` =
  combat-zone reference) — move a feature char in
  the map txt and it moves in-game. A NEW scene = map txt + thin config.
  **ANIMATED WATER (2026-07-17, full statement in DESIGN.md "Art
  pipeline"; LAVA joined 2026-07-19):** all sea/river — and lava — tiles
  cycle 4 Godot-native animation frames
  (`OverWorld._lower_frames()` repaints only water/lava cells per frame on a
  clone of the finished canvas — frame-0 must reproduce it byte-identically,
  asserted; `pack_tiles` lays each animated tile's frames as 4 contiguous
  same-row atlas cells and the `.tres` declares durations on the base cell
  ONLY — frame cells never get `x:y/0 = 0`). Every frame-dependent term
  must be periodic in WATER_FRAMES (drifting crests 4px/16, river rows
  2px/8, foam-churn salts + glint blinks period 4, molten channels crawl
  4px/frame — lava's hand ramp because incandescence can't survive ramp()'s
  violet shadow law) so the loop is seamless;
  zero runtime code, scene CanvasModulate tints ride on top. The town
  fountain is a 4-frame `hframes` prop (`town_fountain(frames=4)` — pour
  columns live in the base silhouette so the baked outline never ghosts;
  `_fountain_anim` only recolors) cycled by the towns' existing
  `_animated` scanners.
  **Z-ORDER DOCTRINE (2026-07-11, lint-enforced — full statement in
  DESIGN.md "Z-order / layering doctrine"):** draw order is the fixed
  sandwich lower tiles → y-sorted `World` entities → upper tiles; three
  tiers decide where art goes. Tier 1 terrain/flat/wall-flush props → lower.
  Tier 2 roofs/canopies/lintels → `place_split`, upper art ONLY above solid
  cells (or door cells) — every walk-behind corridor is capped by a solid
  `ridge` row (map digits, all named `ridge`, never a struct) so at most
  a head-peek crosses the silhouette; the cap is SCALE-GATED (`CHIBI_MAPS`
  in `_check_art.py`): the overworld's ≤1-tile chibi can't out-peek a
  silhouette, so its covered cells need no cap — the Home Tree's whole
  crown is open walk-behind `G` cells, only the trunk solid. Tier 3 = anything a body can stand
  BOTH north and south of (free-standing furniture, street lamps/well/
  stall/fountain, and since 2026-07-19 the town YARD FENCES — the last
  baked standable: rails on the lower canvas drew UNDER a pressed body's
  sunk feet, reading as standing ON the fence; now `town_fence(n)`
  run-length props, town chars `F` = the 3-cell gate runs via `each`,
  `G` = the 5-cell orchard run, cells still solid, the driver's fence
  class paints plain grass) — NEVER baked: `emit_prop()` writes the PNG + a
  `<scene>_props.txt` manifest row and `scene/prop_spawner.gd` spawns it
  into `World` at the feet convention (`node.y + 20`); counter-height
  pieces (desk/table/workbench) make their TOP footprint row `walk` so a
  body tucks in behind the tabletop. The collision box hugs the feet, so a
  pressed body sinks ~10px of sprite past a solid boundary in EITHER
  direction: a corridor's south edge needs the MASK BAND
  (`_town_props._eave_lift`: mirror the solid row's top 12px onto upper),
  legal ONLY with a ≥2-row solid base below the corridor (building
  facades, the home-tree trunk) — never on a 1-row solid between walk rows (a
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
