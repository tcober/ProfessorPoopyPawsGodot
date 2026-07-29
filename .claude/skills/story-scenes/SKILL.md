---
name: story-scenes
description: The narrative kit and every story scene — Theater (cards/fades/say/walk/gates), the dialog box, NPCs, WorldFx depth-sorted effects, phase routers and story flags, plus the hard writing rules (no narrator boxes, cards state only time) and the scene-by-scene index of Prologue A, Prologue B and the Ebb night. Load BEFORE editing any cutscene or story scene in scene/, adding dialogue or an NPC, wiring a phase or flag, staging a walk-gate, or writing any character's lines.
---

# Story scenes

The story canon — what happens and why — lives in **docs/DESIGN.md → "Story"** (full
chapter structure, cast, lore spine, pacing rules). This skill is the *implementation*:
the kit, the rules, and where each beat lives.

**Nothing narrative is ever recovered from git** (the 2026-07-12 build-fresh doctrine).
If a scene was deleted, rebuild it fresh from DESIGN.md.

## The two hard writing rules

### 1. The NARRATION PURGE — never add a narrator box

Every `say("")` narrator box was cut chapter-wide (2026-07-18). Environment cues and
in-character dialogue carry those beats instead: the sky does the nightfall, the hop does
the squelch, Schweinler's own brag carries the engine catch, the door-bang is staged
bodies snapping round.

**Never add a `say("")` narrator box to a story scene.**

### 2. The CARD PURGE — a card may only state how much time passed

Legal: "THE NEXT MORNING." · "THREE SUMMERS LATER." · "THAT EVENING." · "YEARS LATER." ·
"SOME WEEKS LATER."

Cut, and never to be re-added: every commentary card — the summer-montage trio, the
watch/sunset pair, "He did not tell her who he was.", the leaving trio including "He kept
the watch.", "THE NAME STUCK."

The `prologue_open` title and era cards are the one exception and stay.

### Tone

See the tone rules in the root `CLAUDE.md`. Short version: **the Simon & Marcy
register.** Absurd played straight, comedy that leaves a wound, never the candy-kingdom
register. Every line in the fest square stings.

## The kit

| File | What it gives you |
| --- | --- |
| `scene/theater.gd/.tscn` | awaitable `card` / `fade` / `say` / `walk` / `walk_via` / `face` / `hop`, `lock_party` via the `party` GROUP, and **`walk_gate`** |
| `scene/dialog_box.gd/.tscn` | typewriter box, brass bevel, name plate, ▼ arrow, **POLLED** input, mixed-case text |
| `entities/npcs/npc.gd/.tscn` | interact-to-talk; one-row 48px sheets; SpriteFrames built at RUNTIME — a new villager is a PNG + exports |
| `scene/world_fx.gd` | depth-sorted runtime FX |
| `Game.flags` | story flags (`set_flag` is **one-way**) |
| `Party.set_roster()` | typed `Array[StringName]` |

**The kit must never reference autoload identifiers**, or `--script` probes poison their
own compile.

Lowercase glyphs ship in `assets/_pixfont.py` (lineHeight 9→10). UI chrome stays caps by
convention — **door banners are caps-only.**

### `walk_gate` and gate geometry

`walk_gate` takes the goal position, unlocks the party, arms a one-shot `Area2D`, awaits
the player, and re-locks.

**A walk-gate must be UNAVOIDABLE for its objective.** A point-rect is walkable *around*
(hall aisles, the fountain ring) and reads as a hang. Use:

- a full-width room band (hall row 8, sickroom row 6), or
- the whole square zone (both town phases use the fest cutscene's 96×96 fountain zone),

then stage the last steps with `walk_via` waypoints.

**Theater walks are straight NO-COLLISION tweens.** Any scripted approach near the
fountain must dog-leg the ring — `_square_route` / `_post_route` in the town scenes.

### Awaiting handlers

**A `talked` signal handler that starts a dialog coroutine must AWAIT it** before falling
through to logic that can start another. Otherwise one advance press resumes BOTH pending
`say()` awaits — the Sage ribbon-return / want-home collision.

### `WorldFx` — never add FX to the scene root

- **`decal()`** — ground art: origin `DECAL_BIAS = 32px` north + child index 0. The bias
  must exceed feet-offset 20 + half-cell 8, or a body standing ON the decal renders under
  it.
- **`airborne()`** — origin ground-anchored, art lifted by sprite `offset` only. **Tween
  the offset, never the origin.**
- Adding FX to the scene root is what killed the paw prints under the floor (and got
  "fixed" with a `z_index` hack — don't).
- `WorldFx.sheet_sprite` infers vframes from sheet height, so old frame indices survive.

### Pacing: agency vs automatic

Prologue B hands control back **four** times via `walk_gate` — the walk home, the hall
stage, the bluff lip, the bedside. But the hall walk-OUT and the steps/leaving ending are
**deliberately AUTOMATIC**: his body giving up IS those beats. Don't "fix" them into
gates.

## Doors, arrivals and travel

- **DOOR-MOUTH ARRIVALS:** leaving an interior lands the body **ON** the door
  marker/zone — feet on the lane under the arch. (The old tile-and-a-half drop read as
  appearing nowhere near the door.) `_standing` / `_home_armed` suppress the re-fire until
  the body steps off once; interior front-door spawns and exits x-center on the 2-cell
  door bbox.
- **`body_entered` fires ONCE per entry.** Any marker event `TravelScene` swallows — the
  entry lock, or `_busy` while a banner plays — is gone for good, and the marker sits
  dead until the body steps off and back on. A travel door that silently refuses reads as
  broken. Both swallow sites end in **`_deliver_standing()`**, which re-scans the
  overlaps and delivers what was missed; the `_standing` latch is what makes it safe to
  call at will.
- **Never share an anchor between a travel zone and an announce zone** — overlapping
  zones starve `_busy` into a softlock.
- **A door that must change from announce to travel FLIPS `target_scene` on the same
  `OverworldLocation`** — never a second zone on the anchor (the `_free_home_location`
  softlock).
- The `downstairs.txt` **`front_door` / `exit_door` split** is the pattern: the exit zone
  and the arrival cell can never overlap, so no `_standing` suppression is needed.
- **`_standing` suppression is load-bearing** wherever a door marker travels — without
  it, the body standing in the zone when the entry lock lifts walks straight back inside,
  forever.

## Phase routers

Several scenes are ONE scene with N phases, routed by a `Game` field and tinted by a
CanvasModulate. This is the standing idiom — prefer it to a new scene file.

| Router | Scene | Phases |
| --- | --- | --- |
| `Game.bluff_phase` | `scene/bluff.gd` | `meet` (day) · `romance` (sunset) · `call1` · `call2` |
| `Game.town_thesis_phase` | `scene/town_thesis.gd` | `plant`/night · `dash`/morning |
| `Game.hall_phase` | `scene/hall.gd` | `recital` (kid) · the naming (adult) |
| `Game.library_phase` | `scene/library.gd` | `ebb` · `research` · `kit` |
| flag-gated | `scene/downstairs_fest.gd` | the brew phase, gated on `prologue_whirligig_done and not prologue_potion_made` |

**`Game.library_phase == ""` still MEANS `"ebb"`** — it is the boot default a bare scene
load lands on. So the town door **always names its phase explicitly**, or walking in the
front door replays the cutscene. Any phase other than `""`/`"ebb"` skips the cutscene and
just opens the room.

`Game.reset_story()` clears flags **and blanks the routers first** — `set_flag` is
one-way, so a backwards jump would otherwise carry a later chapter's flags into an
earlier scene.

## Scene index

Flow: `prologue_open` → Prologue A → Prologue B → the Ebb night → **the story currently
rests on playable solo Fuji in Lanternwood.** The adult Basil sandbox is reached only via
`prologue_open`'s ESC skip (which also sets `ebb_done`).

### Prologue A — "The Whirligig" (kid Basil, bright era)

| Scene | Beat | Owns |
| --- | --- | --- |
| `scene/prologue_open.tscn` | title + era cards; ESC skips to the adult sandbox | — |
| `scene/house_fest.tscn` | scripted SUNRISE — asleep → eyes open → window → curtains → sigh → control | — |
| `scene/downstairs_fest.tscn` | Mom's good-morning by the hearth unlocks the front door | `prologue_saw_mom` |
| `scene/town_fest.tscn` | the Founding Festival; the fountain-square teasing cutscene; the WANDER GATE (talk to any 3 of six talkables, then "I want to go home"); the BLESSING DOUBLE-BACK | `prologue_gate_open` |
| `scene/bluff.tscn` phase `meet` | the whirligig quest: kid Kitty, the parts at the `part_*` anchors, the crank-up mash, the flight, then **THE IDEA** ("could it carry a flask?") | `prologue_part_*`, `prologue_whirligig_done` |
| `scene/downstairs_fest.tscn` (flag phase) | **THE BREW** — walk-gate on the workbench top `E`, then a STIR mash cycling the flask through the four `Alchemy` tints | `prologue_potion_made` |
| `scene/hall.tscn` phase `recital` | **THE RECITAL** — the flight with a flask pinned under the pod, four fireworks in the four COMPOUND colours | `prologue_recital` |

Then the card "THREE SUMMERS LATER." → the bluff's `romance` phase.

**The recital chain (2026-07-25)** pays off two shipped setups — Schweinler's fest-square
taunt and the Academy door's `locked_text` "RECITAL IN PROGRESS" — and answers *why the
Academy ever let him in*. Its deliberate inverse is Prologue B's naming in the same room:
the stage is a SEALED region, so the boy isn't ALLOWED on the platform and sets up on the
house floor with the faculty looking down. Strix says "It is POTIONS is what it is." and
the ten-year-old answers "...It's chemistry, sir." — the exact line the adult says at
that same podium. Once spent, the fest **south gate REFUSES** (it would re-enter bluff
`meet` with every part flag set and replay the finale) and the **Academy door goes live**.

### Prologue B — "Professor Poopy Paws" (college-age Basil)

| Scene | Beat | Owns |
| --- | --- | --- |
| `scene/bluff.tscn` phase `romance` | the watch gift EXPLODES on the handoff → gather → refit → first `look_watch` → **THE KISS** → the sun goes down while they watch | `prologue_wpart_*`, `prologue_watch_given`, `prologue_romance` |
| `scene/town_thesis.tscn` phase `plant` | the earned-it doorstep call ("potions" vs CHEMISTRY), then Schweinler creeping the LANES | — |
| `scene/house_thesis.tscn` | wake-up | — |
| `scene/town_thesis.tscn` phase `dash` | the step onto the bag is SHOWN, the SQUELCH, a clean run + paw-print trail | — |
| `scene/hall.tscn` | **THE NAMING** — a true proscenium; the laugh erupts and Basil starts the AUTOMATIC flee, swallowed behind the curtain leg after "But... I...", "'BUT'?! HA! HE SAID BUTT!" and a held `bow_head` | — |
| `scene/bluff.tscn` phase `call1` | Basil SITS on the lip; she calls ("I'm coming. Stay right there.") | — |
| `scene/accident.tscn` | the accident SHOWN with CAUSE — a partyless side-view set-piece; Schweinler brags, mounts against Ridley's warning, loses control as Kitty rides in | `prologue_accident` |
| `scene/bluff.tscn` phase `call2` | her watch calls his; RIDLEY's voice on it; ends on a REAL bolt back down the headland | — |
| `scene/sickroom.tscn` | **THE VERDICT** — magic mends anything but memory; ends on Kitty's mother banishing him ("LEAVE.") | — |
| clinic stoop | Ridley's blunt "perspective" speech and exit; Basil's one "..." + `bow_head`; night falls | — |
| south gate | the `knapsack` tableau, the `knapsack_back` LOOK-BACK ("I wish I could have been welcome here"), then the `knapsack_walk_down` trudge south **facing the camera** | — |

Then "YEARS LATER." → the Ebb.

### The Ebb night

| Scene | Beat | Owns |
| --- | --- | --- |
| `scene/ebb.tscn` | partyless cutscene over the big mountain: escalating quake, ONE white flash swaps bright for drained + crystal ignition on the same cut, 14 additive spark motes sucked home to the summit, held silence. Polled LEVEL-detect skip on accept/cancel/attack, armed after 1s | `ebb_done` |
| `scene/library.tscn` phase `ebb` | **FUJI'S FIRST APPEARANCE** — wand-made coffee whose sparks keep missing the kettle; **THE SYNC** (the third cast lands ON the quake and she's briefly certain she did it); the fourth cast makes NOTHING | — |
| `scene/lanternwood.tscn` | `_ebb_night_town()` — three villagers comparing charms that all died at once (Bramble / Alder / Pip). Talking to all three sets the gate | `asked_around` |
| `scene/library.tscn` phase `research` | **THE RESEARCH GATE** = Act 1 beat 2. The card "SOME WEEKS LATER.", then control straight back — a GATE, not a cutscene. The accession LEDGER vs the THREE STACKS; the twelfth spine is Basil's unbound, unstamped thesis | `ledger_read`, `thesis_found` |
| `scene/library.tscn` phase `kit` | **THE KIT** = Act 1 beat 3, the deliberate inverse of the recital chain (*idea → brew → it flies* becomes *ambush → improvise → the darts fly*). A 3-part wander gate on furniture that already exists: `_kit_dose` (shelf THREE, husbandry — how to put a large animal down to trim its hooves), `_kit_wand` (the dead wand bored out into the pipe), `_kit_book` (the book the player picks — stats identical, and it is her VESTIGE SOCKET VESSEL for the whole game). `_kit_check` sets the composite | `fuji_dose_found`, `fuji_darts_made`, `fuji_tome_taken` → `fuji_kit_made` |
| `scene/lanternwood.tscn` | **THE DEFENCE OF LANTERNWOOD** — the first real fight in the game, and Fuji's alone. Teaches the drowse setup properly: dart → dart → it drops → tome it | — |

**`ebb.tscn` needs no edit for the 2026-07-28 authorship revision** — it is staged from
the world's point of view, and the world is simply wrong about what it watched. The
visual is accurate and misunderstood.

**The library room is a cutscene that BECOMES playable.** Fuji acts the beat as an NPC
PUPPET over her own hidden body (her party sheet has no wand-cast pose), swapped on a
matching front-facing idle — never on the PROFILE, which would pop. At the hand-over the
puppet goes, the body takes its place, and control returns **where she stands**: no fade,
no card, nobody drags her out. She leaves by walking out her own door.

**The story STAYS WITH HER** from the library floor to the street — no card, because no
time passes.

## Scene lighting and time of day

The default is a **CanvasModulate tint** per phase — that is the "tint law", and it is
how `bluff`, `town_thesis`, `hall` and `lanternwood` all change hour.

**The bluff's nightfall idiom** (reusable; originally `town_thesis`'s) layers three
overlays over one warm painting:

- **`$Sky`** — an opaque baked band down to a horizon line at y=28, swapped per phase
  (`bluff_sky_day.png` / `bluff_sky_dusk.png`). Without it the sea ran to the frame top
  and read as a night sky.
- **`$Glow`** — additive: the setting sun + its glint lane. **Fading the glow IS the
  sunset.**
- **`$Stars`** — additive twinkles + moon + a silver moon-glint lane
  (`bluff_stars.png`), faded IN as night falls.

The three functions: **`_set_hour()`** snaps a phase's light; **`_fall_night()`** tweens
Dim + Glow + Stars in parallel (this is the awaitable on-screen nightfall);
**`_twinkle()`** alpha-pulses the star field. `romance` runs `_fall_night` twice to full
night after the kiss; `call2` opens late and AWAITS the fall before a single line.

**The one exception is THE HOUSELIGHTS** — see below. A CanvasModulate cannot do it.

## Two composed-scene gotchas worth remembering

- **`_laugh_bob` captures its rest `y` at call time**, and killing a looped tween mid-bob
  leaves the head sunk — so a SECOND bob set treats that as rest and the tier sinks.
  Reset `sprite.position.y` after every kill (`_kill_bobs`).
- **THE HOUSELIGHTS** are the one scene light that is NOT a CanvasModulate. A
  CanvasModulate multiplies the whole canvas, fireworks included, so it would darken the
  bursts by the same factor and buy nothing. `_house_take()` snapshots the room (both
  tile layers, the glow overlay, every prop/cast/player node in `$World`) and
  `_house_apply()` paints one interpolated colour across the lot — **one `tween_method`,
  not fifty tweeners.** Everything spawned afterwards — the rig, its pulsing payload,
  every burst and spark — is by construction outside the dim and burns full strength
  against it; *that*, not the blend mode, is where the brightness comes from. No line
  announces the lights going down (the narration purge).
  - Each burst `_house_wash()`es its own colour back over the walls and the eighteen
    backs on its **own** tween, so it can never kill and hang an awaited `_house_set`.
  - The ring grows via **`_burst_scale`** — and `scale` multiplies a `Sprite2D`'s
    `offset` too, so divide the lift by the scale or the ring flies 80px up the wall.
  - The flask's readability pulse is a LOOPED `modulate` tween that **must be killed
    before `_fireworks` drains its alpha**, or a=1 gets rewritten twice a second.
  - **`_set_rig_offset`** gives the whirligig and its pinned flask the *same* offset — a
    `Sprite2D`'s `offset` moves only its own texture, so a pinned child stays planted
    while the parent's art climbs. Flying by `position:y` instead would raise the y-sort
    key past the opaque apron entity and the whirligig would vanish behind it.
