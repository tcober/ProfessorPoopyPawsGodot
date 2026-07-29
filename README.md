# Professor Poopy Paws

A Zelda: *A Link to the Past*–style action-RPG about a brilliant science cat who — after
a public humiliation, a devastating loss, and the draining of the world's magic — is
pulled out of hermithood to restore magic to the world and find love again.

Tonally it's Adventure Time at its most serious — the **Simon & Marcy** register, with a
little **Over the Garden Wall** — meets **Final Fantasy**: absurd on the surface, played
straight, and a lot sadder underneath than it first lets on.

Built in **Godot 4.6** (GDScript, GL Compatibility renderer) with an art style chasing
the 16-bit greats: Chrono Trigger's pixel density, Secret of Mana's lush action-RPG
feel, and Paper Girls' surreal duotone color scripting, all inside a
steampunk-inflected medieval fantasy world — brass and flasks, candles and gears.

> The full design bible lives in [docs/DESIGN.md](docs/DESIGN.md) — story, themes,
> influences, asset specs, and conventions. It's the single source of truth.

## The game right now

The game boots to a title screen (`NEW GAME` / `CONTINUE` / `QUIT`) and plays as a
continuous story from there.

**Prologue A — "The Whirligig."** Ten-year-old Basil wakes at sunrise, goes down to his
mother's hearth, and out into the Founding Festival, where everyone has a small cruelty
ready for the one kid in town who can't do magic. He builds a flying toy on a headland
with a girl named Kitty, has an idea about it, brews his first potion at his mother's
workbench, and flies the thing at the Academy recital with a flask pinned underneath —
which is how a boy with no magic talks his way into a school of it.

**Prologue B — "Professor Poopy Paws."** Years later, thesis day. It goes badly. The
chapter is the name he gets, the accident that takes Kitty's memory of him, and the walk
south out of town with everything he owns on a stick.

**The Ebb.** An earthquake. The mountain's summit turns to crystal and the world's magic
drains visibly into it, sparks streaming home from every horizon.

**Act 1.** The story picks up with **Fuji**, a Lanternwood librarian, whose wand stops
working the same night — and who finds, on her own shelf, an uncatalogued bundle of
string-tied paper with no accession stamp and *"Laughed out of the Academy"* written on
it in another hand. That's where the playable story currently rests.

Underneath the story is a full combat sandbox — reachable directly by pressing `0` (see
below) or by skipping the prologue with `ESC`:

- A **two-member party**: Basil leads, Fuji follows on AI, and `Q`/`Tab` swaps who you
  drive. The follower has a three-mood brain (follow / engage / return) with a leash and
  an off-screen catch-up teleport.
- **Basil** fires an instant laser with a hard recoil skid. Beakers are his magazines,
  and each one is a colour-coded **compound** — green base, blue frost, red flame,
  purple piercing plasma. `M` opens a **mixing bench** to fuse two spares into
  something better.
- **Fuji** swings a tome overhead and blows **sleep darts**. Sleep is a buildup, not a
  flag: dart an enemy enough and it drops, and a bigger enemy just takes more darts.
- **RPG systems**: levels, five stats, four equip slots, a satchel, and save/load.
- A **five-lands overworld** to travel — ocean-separated continents with a kingdom, a
  frozen north, a purple desert and a lava coast — plus the walkable towns of Alembic
  and Lanternwood, and Whisker Meadow, where the slimes are.

## Running it

Open the project in **Godot 4.6** and press Play, or from the repo root:

```sh
godot --path .
```

The dev window runs at 1152×648 (3× the base 384×216 resolution).

### Controls

Full gamepad support (bindings shown for a PS5 DualSense).

| Key | Pad | Action |
| --- | --- | --- |
| **WASD** / arrows | Left stick / D-pad | Move (8-way) |
| **J** / Space | Square / R2 | Attack — laser (Basil) / tome swing (Fuji) |
| **K** / Shift | Cross | Hop — air-steerable dodge |
| **L** | L2 | Blow-pipe dart (Fuji) |
| **R** | L2 | Reload (Basil) — `dart` and `reload` share L2, contextual on the leader |
| **E** | Circle | Interact / advance dialogue |
| **Q** / Tab | Triangle / L1 | Swap which party member you drive |
| **M** | Create | Mixing bench — fuse two beakers |
| **I** | Options | Party menu — roster, stats, gear, satchel, save |
| **0** | — | **Dev chapter selector** (debug builds): jump to any of 37 story beats |
| **ESC** | — | Skip the prologue to the combat sandbox |

## How it's built

- **Component-based architecture** — reusable behavior lives in
  [components/](components/) (health, hitbox, hurtbox, status); entities in
  [entities/](entities/) compose them; shared data are `Resource`s in
  [resources/](resources/); rooms and levels in [scene/](scene/).
- **One scene pipeline, one map format** — every scene (interiors, overworld, towns,
  meadow) is a plain-text tile map driven through a shared Python tile kit
  ([assets/_tilekit.py](assets/_tilekit.py)). The same map txt drives both the painted
  art and the runtime collision, so they can't drift. Move a feature character in the
  txt and it moves in-game. A new scene is a map txt plus a thin config script.
- **Procedurally authored pixel art** — all tilesets, sprites and FX are generated by
  stdlib-only Python in [assets/](assets/), then sliced and deduped into real Godot
  TileSets. Repeated cells are byte-identical *by construction*, so a whole scene
  collapses to a small atlas the way an SNES scene lives in VRAM. Two TileMapLayers
  (under/over entities) let bodies walk behind railings, lintels and rooflines.
- **Water, lava and lamplight animate with zero runtime code** — they're native
  4-frame TileSet animations, so every frame-dependent term is authored periodic.

### Regenerating art

```sh
python3 assets/_gen_tileset_overworld.py   # (or any other _gen_*.py)
python3 assets/_check_art.py               # lint — catches floating art, invisible walls
godot --headless --import                  # re-import — required, or atlases render scrambled
```

Scenes can be eyeballed without launching the game via `tools/shot.gd`, and each
subsystem has a headless probe in [tools/](tools/).

## Repo map

| Path | What's in it |
| --- | --- |
| [assets/](assets/) | Python art generators, tile kits, palettes, maps, generated atlases |
| [components/](components/) | Reusable gameplay components (health, hitbox, hurtbox, status) |
| [entities/](entities/) | Basil, Fuji, the party/AI layer, enemies, projectiles, pickups, NPCs |
| [resources/](resources/) | Compounds, alchemy rules, character sheets, stats, items |
| [scene/](scene/) | Rooms, cutscenes, overworld, towns, HUD, menus, autoloads, tile drivers |
| [docs/](docs/) | The design bible and planning docs |
| [tools/](tools/) | `shot.gd` screenshot tool and the per-subsystem probes |

## Working on it with an AI assistant

[CLAUDE.md](CLAUDE.md) is the short quick-reference — invariants and standing rules.
The subsystem depth lives in `.claude/skills/` (`art-pipeline`, `map-authoring`,
`combat-kits`, `party-ai`, `rpg-systems`, `story-scenes`, `world-and-zones`,
`probes-and-shots`), and `assets/`, `scene/`, `entities/` and `tools/` each carry a
short `CLAUDE.md` of their own. [AGENTS.md](AGENTS.md) points tool-agnostic assistants
at the same material — the skills are plain markdown and can just be read.
