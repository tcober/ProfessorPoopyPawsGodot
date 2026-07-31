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
| cutscenes, NPCs, phases, flags, walk-gates, doors, staging any character's lines | **`story-scenes`** |
| WORDING a line — read [docs/dialogue/](docs/dialogue/) first; `tools/dialogue.py` writes edits back | **`story-scenes`** |
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

**ALEMBIC TOWN — A FOREST-FLOOR VILLAGE WITH FOUR GREAT TREES (2026-07-30, rebuilt
twice).** One **80×56** grid. The town — the lane, the market square, three shops, the
clinic, the neighbour's cottage, the well, the stall, the fountain — is on the **forest
floor**. Four great trees stand along the clearing's north edge; each carries a round
**RING DECK** near its crown, a **door and a lit window cut into its trunk**, and a rope
ladder down. There is no elevation system: a storey is a flat walkable region *disjoint
in the grid*, and the whole "system" is the `stratum:` legend token plus
`_alembic.assert_all`.

**THE CANOPY IS NOT A FLOOR, IT IS FOUR ISLANDS — and that is the lesson, twice paid
for.** The version before this one made both canopy storeys continuous boardwalk from
edge to edge, and a town that is 100% floor renders as horizontal stripes of plank and
fascia: a lumber yard, or a fence. What makes Slitherbough and Endor read is the **VOID
between the platforms**. So each ring is a disc of decking with solid leaf all round it,
and the part that already looked like somewhere — the ground — is the town.

**A RING'S WALKABLE CELLS ARE THE ELLIPSE'S, DERIVED (2026-07-30).** `ring_cells`
rasterizes the same numbers `tree_ring` draws from and `_alembic.assert_all` checks the
grid against them. The hand-guessed mask before it made the disc's *widest* rows the
*narrowest* you could walk — a circle walked as a rectangle, with an invisible wall
following the rim. The test is the **body's 12×8 box at all four corners** against the
**rim board**, never a point and never a radius: the overhang is directional, so a cell
at `o=0.65` on the south rim has a foot off the platform while one at `o=0.88` on the
north arc is fine. A rim cell must render leaf, not deck, or the corners the curve
misses square the circle back off. **The rail is not decking** — its near arc is a
Tier-3 prop so you stand behind the handline; the far arc stays baked, behind you.

**THE TRUNK IS BLITTED BEFORE THE RING, AND THE SHOPS ARE NOT HUTS (2026-07-30).** Two
things the ring rebuild left behind, both fixed the same day it was reported. Tier-1 has
no sort key, so on the baked layer **draw order IS depth**: the shaft went down after the
ring and its dead-straight `edge()` top landed two px under the fascia, so every tree
visibly BEGAN at a horizontal cut — a post nailed to a saucer. Blitted first, the only
line crossing the trunk is the fascia's hem, which is an arc, and `_shade_under` lays the
deck's shadow on the bark below it. And the three shops were still `tree_hut`s: a cone of
thatch over a barrel of withy staves is right in a BOUGH and is a **tiki hut** on a
forest floor. They are `_town_props.town_shop` now — the cottage's own 80×64 envelope
over a 5×4 footprint, plus a striped **awning**, a warm **display window** with the
trade's goods silhouetted in it, and a **hanging device** on a dark board. **A building
belongs to the storey it stands on.**

**THE RING READS AS A CIRCLE FROM THREE THINGS, and it needs all three:** radial
planking (boards running out from the trunk like spokes — with normal east-west boards it
is a rectangular deck with rounded corners), a concentric rim board, and a fascia that is
a **crescent** (the vertical face hangs below the southern arc only, deepest at due
south, thinning to nothing at the poles; constant depth all round is a barrel). The
tree block is 12 cols × 9 rows and **its outer column each side is always solid** — a
ring's deck 4-adjacent to the forest floor fuses the two strata, silently. The ladder
runs down **inside** the trunk's four columns, or you can step sideways off rung eight
onto ground thirty feet below. Full doctrine in **DESIGN.md → "STACKED WALKABLE
STOREYS"** and the `map-authoring` skill.

Basil's house is UP one of those trees — his door → the lab → the bedroom — and the
hermit is the one cat in town who stopped coming down. The **north** mouth now goes
somewhere (below); the **east** one is authored for beat 5b and still walled.

**THE FOREST FLOOR IS DRESSED (2026-07-30).** The understory pass used to fire only
where a trunk stood within three rows north of a cell, which is a band round each tree
and nothing else — the rest of an 80×56 clearing was a flat green LAWN with four trees
on it. Density is now a **gradient**: every cell is scored by its distance to the
nearest wild thing (forest wall, great tree, town tree) and the odds fall off with it,
so litter banks at the edges and wears away down the lane. What it is dressed WITH
matters more than how much — ferns, roots and saplings are all drawn from the leaf ramp,
so a floor dressed only in those is green dressing on green ground. `understory` gained
**`drift`** (warm fallen leaves out of the timber ramp), the only piece that changes the
field's HUE, and it is the common case at every distance. Several **salted variants per
kind**, because one litter cell is one opaque atlas tile and one variant repeated three
hundred times is wallpaper, not texture.

**THE ALEMBIC ACADEMY IS ITS OWN SCENE (2026-07-30)** — `scene/academy.tscn`, 64×48,
up the north lane, and back down again into the town's own lane
(`Game.town_spawn = "north"`). Composed depth-first on one axis: causeway → the beck and
its bridge → outer ward → the crenellated RAMPART and its two-tower gatehouse → the
inner court with the GREAT ORRERY standing in the middle of it → the grand stair → THE
KEEP.

**THE KEEP IS A TIMBER CASTLE-SCHOOL AND ITS CORNER TOWERS ARE THE TWO GREAT TREES
(2026-07-30 rework).** `_academy_props.academy_keep` replaced `town_academy` (retired —
no other caller): one 22×9 block, one 416×192 sprite, the hall's cedar-shake pitch
running out and dying INTO each trunk, a 48px iron-barred door under a porch bay, the
mint rose window in its gable, two masonry chimney breasts, timber galleries hooped
round both trunks and the **Academy bell** hung under the west one. It runs off the top
of the frame on purpose — **only 100px above a building's foot is ever on screen**, and
that is a rule about which FURNITURE must sit below the line, not about how big the
building may be. The two WINGS were redrawn for depth and their **phantom smoke fixed**
(`_wing_anim` gave flues to the observatory, which has no chimney). The court got weeds
and cracks in drifts, the beck reeds and a timber bridge. **Five hand-pinned ramps**
(`OAK`/`SHAKE`/`DAUB`/`VERDI`/`COPPERD`) — the violet shadow law was drawing the dome,
the boiler, the orrery's sun and plate and the whole timber frame RED. And
`assets/maps/academy.txt` **was never in any of `_check_art.py`'s four tables**: adding
it found the south border wide open and a hipped roof leaving the wings' back corners
art-free. A third silent failure needed measuring rather than linting — `Sprite.rect` on
an inverted range draws NOTHING, so the still-house's rebuilt flues were a rain cap with
no shaft and the smoke still rising off it. `_flue` asserts on that now.

Full statement in DESIGN.md → "THE ALEMBIC ACADEMY, walkable"; the art kit is
`assets/_academy_props.py` and the walk is covered by `tools/academy_probe.gd`.

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

python3 tools/dialogue.py export           # .gd -> docs/dialogue/*.md (the screenplay)
python3 tools/dialogue.py apply            # docs/dialogue/*.md -> .gd (your rewrites)
python3 tools/dialogue.py check            # neither side has drifted
python3 tools/dialogue_test.py             # the round-trip's own tests
```

## Writing dialogue: read the book, not the code

**[docs/dialogue/](docs/dialogue/) is every spoken line in the game as a screenplay** —
one file per scene, in story order, speaker in front of every line, `file:line`
beside it. It is GENERATED from the `.gd` files, which stay the source of truth,
but it is a two-way door: edit the words after `> `, run `python3
tools/dialogue.py apply`, and they land back in the scene.

Do that instead of grepping ~290 `theater.say()` call sites. **Re-export after any
`.gd` edit**, and `apply` before rearranging a beat — an unapplied edit lives only
in the `.md` and `export` overwrites it. Rewording is supported; adding, deleting
or reordering lines is a change to the SCENE and belongs in the `.gd`
(`close_dialog()` / `wait()` beats have to move with it).
