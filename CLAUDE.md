# Professor Poopy Paws

A Zelda: ALttP–style action-RPG with deeper RPG systems, about a science cat branded
"Professor Poopy Paws" who — after public humiliation and losing his girlfriend to a
machine accident that erased her memory of him — becomes a hermit, until the world's
magic drains away in a single night (**the Ebb**) and Fuji, a librarian from snowbound
Lanternwood who unearthed his discarded thesis, pulls him back to restore the world's
magic and find love again, with her.

> **The design bible is [docs/DESIGN.md](docs/DESIGN.md)** — story, themes, lore spine,
> cast, influences, asset specs, and the full RPG systems design. It is the single
> source of truth for *what the game is*. **This file is the quick-reference for
> working in the repo**, and it deliberately stays short: the depth lives in the
> skills below and in DESIGN.md. Keep both updated as the game grows.

## Tone — the Simon & Marcy register

**Adventure Time at its most serious**: "I Remember You", Simon & Marcy, the Lich. A
bright surface stretched over an apocalypse nobody discusses. Jokes that land and then
leave a wound. **Over the Garden Wall** is the second touchstone — melancholy, folkloric,
funny without ever being cute. The other half of the blend is **Final Fantasy**: earnest,
operatic, sincere about big feelings.

**NOT the candy-kingdom register.** No random whimsy, no quirk for its own sake, no gag
that costs nothing. If a joke could be cut with no loss, it was the wrong joke. "Very
kiddy" is the failure mode, in writing and in art alike.

Absurd premises are played completely **straight** — the goose that stole the ribbon is
funny because nobody in the scene finds it funny. Register for Basil and Fuji: two
adults bad at this, funny far more often than tender.

## Tech invariants

- **Godot 4.6**, GDScript, GL Compatibility renderer.
- Base resolution **384×216** (16:9 — integer-scales 5× to 1080p; dev window 3× at
  1152×648); **16×16** tiles; **48×48** character cells (figure ~33px, feet y=44);
  nearest filtering, **no camera zoom**.
- **TRUE SNES density** — big deliberate pixels, Chrono Trigger scale: ~24×13.5 tiles
  visible, characters ~2 tiles tall. Canonical numbers live in the DESIGN.md Scale Table
  and `assets/_core.py`. **Never shrink Basil to fit more world on screen.**
- **Component-based architecture:** reusable behavior as nodes/resources in
  `components/`; entities in `entities/` compose them; shared data as `Resource`s in
  `resources/`; rooms and levels in `scene/`; art and audio in `assets/`.
- **Two sprite scales, one tile size:** 24×24 chibi on the overworld travel layer, 48×48
  in zones, 16×16 tiles everywhere.
- Art direction: **Final Fantasy VI, Chrono Trigger, Secret of Mana, Sea of Stars,
  Paper Girls** — CT-Frog proportions with flat hard-banded shading (no dither inside
  characters), SoM's lush action-RPG feel, Paper Girls' surreal duotone color scripting.
  Movement and perspective stay SNES-Zelda.
- **World genre: steampunk-inflected medieval fantasy** — brass-and-flask over chrome,
  candle-and-gear over circuitry. Never modern tech, never generic fantasy.

## Standing rules

These hold everywhere, in every session:

1. **Regenerate → lint → import.** `python3 assets/_gen_*.py` → `python3
   assets/_check_art.py` → `godot --headless --import`. Game runs never re-import.
2. **Verify the scene you changed, not the whole chapter.** Use the per-scene probe or
   `tools/shot.gd`; `tools/prologue_probe.gd` takes minutes and is for handoff-chain
   changes and final checks only.
3. **State that must survive a door lives on `Game`.** `Party.spawn()` rebuilds every
   body at every scene change — so the gun loadout, character sheets, inventory and
   flags all live on the autoload, never on the body.
4. **A save is exactly what `reset_story()` clears, plus roster and current scene.**
   Add a field to `Game` → add it to both, in the same commit.
5. **Never add a narrator box** (`say("")`) to a story scene. A card may ONLY state how
   much time passed.
6. **Nothing narrative is ever recovered from git** — the build-fresh doctrine. Rebuild
   from DESIGN.md instead.
7. **Byte-locked twins move together:** `town.txt` ↔ `town_fest.txt`, `overworld.txt` ↔
   `overworld_bright.txt`. Edit one, edit the other in the same commit.
8. **The game must never be completable with either system alone.** Magic and science
   are non-overlapping by construction — only a spell revives or lights a room, only the
   gun answers the drowse-immune machines. Hold this every time a new enemy or gate is
   authored.
9. **A weapon never changes a KIT.** Gear grants stats and a name; who fights how is
   character, not equipment.
10. Prefer **one scene with N phases** over a new scene file (the phase-router idiom).

## Where the detail lives — load these skills

The subsystem depth was moved out of this file into skills, so it loads when it's
relevant instead of competing for attention every session. **Load the matching skill
before you start**, not after something breaks:

| Working on… | Load |
| --- | --- |
| anything in `assets/` — generators, tile kit, palettes, sprite sheets, animated water | **`art-pipeline`** |
| `assets/maps/*.txt`, props, cliffs/terraces, walk-behind, z-order, clipping/floating art | **`map-authoring`** |
| `components/`, `entities/player|fuji|enemies|projectiles`, ammo, status effects, damage | **`combat-kits`** |
| `scene/party.gd`, `entities/party/`, brains, follower behaviour, movement speed | **`party-ai`** |
| sheets, stats, gear, satchel, `party_menu`, `save_game`, `title` | **`rpg-systems`** |
| cutscenes, dialogue, NPCs, phases, flags, walk-gates, doors, any character's lines | **`story-scenes`** |
| the overworld, towns, zones, interiors, travel markers | **`world-and-zones`** |
| `tools/`, probes, screenshots, headless gotchas | **`probes-and-shots`** |

Subdirectories also carry their own short `CLAUDE.md` pointing at the same skills.

## Current state

The story is playable end-to-end from boot through the Ebb night, and **rests on
playable solo Fuji in Ebb-night Lanternwood**. `scene/title.tscn` is the boot scene;
`prologue_open`'s ESC skip jumps to the adult Basil sandbox (and sets `ebb_done`).

Built: Prologue A "The Whirligig" (incl. the recital chain) · Prologue B "Professor
Poopy Paws" · the Ebb night · the library research gate (Act 1 beat 2) · **Act 1 beat 3
"THE KIT"** (`library_phase = "kit"` — `_kit_dose` / `_kit_wand` / `_kit_book`, gated in
`fuji.gd` on the real flags `fuji_dose_found` / `fuji_darts_made` / `fuji_tome_taken` →
`fuji_kit_made`, which is `Chapters.KIT_ARMED`) · THE DEFENCE OF LANTERNWOOD · **Act 1
beat 3b "THE MOTION"** and **the crossing** (below) · the combat core (compounds, status
ailments, the 2-member party) · the RPG layer (levels, gear, satchel, save/load) · the
five-lands overworld, Alembic Town, Lanternwood, Whisker Meadow.

**NPCs WALK NOW (2026-07-29).** A villager sheet's row 0 is unchanged, but **rows 1-3
are an optional walk cycle** — one direction per row, six cells each, side drawn LEFT,
so a walking villager is 480×192. The clips gate on the sheet's **height**, never on
`frame_cols`, so growing a sheet makes every staged `theater.walk` on that character
animate with no scene edit; `Theater._face_anim` now passes its `walk`/`idle` prefix
through to `NPC.face_dir(v, moving)`. `NPC` also gained an opt-in **wander** bounded by
an authored cell rect (`bind_map` + `wander_cells`), which freezes for dialogue, staged
tweens, cutscenes and anyone standing in the TalkZone, and refuses solid cells, cells
outside the box, walk-behind crowns and any cell a party body is on. Live on **Bramble /
Alder / Pip** in Ebb-night Lanternwood and on **Basil's mother**, who works the hearth
end of the kitchen and drops back into her `act` pose (`wander_rest`) every time she
stops. **Mayor Hollis got the walk art but does NOT wander** — `motion_probe` pins him
to his own step, and a body in the one-cell harbour lane is a wall. The same pass pulled
those five characters' seeds off the pastel register (lower L, saturation kept or
raised, five ramps hand-pinned where `ramp()`'s violet law was turning them candy).
`library_probe` carries the **roam-box lint**: block each roam cell in turn, and the
gate, the pier and the library must all stay reachable.

**THE MOTION + THE CROSSING (2026-07-29)** answer "why does she leave?" and close the
Act 1 boat hook. Lanternwood grew a **cove** on the east end of LEVEL 1 — a pier
(`dock` cells → render class `bridge`), the town's **steam launch** on `berth` cells
(→ render class `sea`, so the hull floats on animated water), and **THE MOOT HALL** on
a cabin's 5×4 footprint. **Mayor Hollis**, an old elk who is the town's clerk in the
same body, minutes the fight, moves that the town send somebody, **seconds himself**,
and gives her the launch — which still runs because it burns coal, paying off Alder's
shipped "honest oil, honest fire" line. Flags `mayor_briefed` / `boat_ready` →
stepping onto the pier casts off (`left_lanternwood`) and lands her on the overworld's
new `landing` marker, Forest Land's west shingle, five cells from Alembic Town.

**THE TREEHOUSE ALEMBIC (2026-07-29) — DONE.** Basil's origin town is a **two-strata
canopy town**: the forest floor, the plank boardwalk in the boughs above it, four rope
ladders, two rope spans and one scripted **dinghy lift**, all in the same 56×34 grid.
There is no elevation system — a storey is a flat walkable region *disjoint in the
grid*, and the whole "system" is the `stratum:` legend token plus the assert block at
the tail of each town generator. The doctrine (why the two alternatives were rejected,
the SPAN LAW, "the mask band IS the railing", the lift's solid shaft, and why a
treehouse village reads from `tree_hut`'s silhouette and nothing else) is in
**DESIGN.md → "STACKED WALKABLE STOREYS"** and the `map-authoring` skill.
Basil's house is UP: his door → the lab in the hollow → the bedroom in the fork, and
the hermit is the one cat in town who stopped coming down. The doctor's clinic and the
neighbour's cottage stay on the ground — you do not carry a cat who has been run over
up a rope ladder — and they keep Alembic's plaster-and-cement language, so the town
reads as an old ground village with a woven canopy grown over it.

Designed but NOT built — both live in Alembic Town, and the grids they were waiting on
have now settled: **Act 1 beat 4 — ASKING AROUND**, where the wander gate is not a crowd
but **adult Sage and Basil's mother**, and the rumour that he walked into the deep wood
is the direction as well as the dread; and **beat 5b — THE HOLLOWAY**, the sunken green
lane to the SE coast that was safe for four hundred years because the way-charms burned
along it, and is not any more. See DESIGN.md beats 4 / 5b.

Next, per DESIGN.md "Build order": **KO + FOCUS** → vestiges (gated to Act 2's first
obelisk) → the Return.

**Press `0` anywhere in a debug build** for the dev chapter selector — all 42 beats,
staged with roster/phase/spawn/flags. Adding a beat is one row in `scene/chapters.gd`.

## Commands

```sh
godot --path .                             # run (dev window 1152×648)
python3 assets/_gen_tileset_<scene>.py     # regenerate art
python3 assets/_check_art.py               # lint the output
godot --headless --import                  # REQUIRED after any regen or new class_name
godot --headless --script tools/shot.gd    # eyeball a scene (see probes-and-shots)
```
