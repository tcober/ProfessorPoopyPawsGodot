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
`fuji_kit_made`, which is `Chapters.KIT_ARMED`) · the combat core (compounds, status
ailments, the 2-member party) · the RPG layer (levels, gear, satchel, save/load) · the
five-lands overworld, Alembic Town, Lanternwood, Whisker Meadow.

In progress: **THE DEFENCE OF LANTERNWOOD** — Act 1 beat 3's fight, the first real one,
and Fuji's alone (`scene/lanternwood.gd`).

Next, per DESIGN.md "Build order": **KO + FOCUS** → vestiges (gated to Act 2's first
obelisk) → the Return.

**Press `0` anywhere in a debug build** for the dev chapter selector — all 39 beats,
staged with roster/phase/spawn/flags. Adding a beat is one row in `scene/chapters.gd`.

## Commands

```sh
godot --path .                             # run (dev window 1152×648)
python3 assets/_gen_tileset_<scene>.py     # regenerate art
python3 assets/_check_art.py               # lint the output
godot --headless --import                  # REQUIRED after any regen or new class_name
godot --headless --script tools/shot.gd    # eyeball a scene (see probes-and-shots)
```
