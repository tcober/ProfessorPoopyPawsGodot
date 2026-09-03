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
7. **Byte-locked twins move together:** `town.txt` ↔ `town_fest.txt`, `canopy.txt` ↔
   `canopy_fest.txt`, `overworld.txt` ↔ `overworld_bright.txt`, `downstairs.txt` ↔
   `downstairs_bare.txt`. Edit one, edit the other in the same commit.
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

Built: **Prologue A0 "The Fever"** (2026-08-22, below) · Prologue A "The Whirligig"
(incl. the recital chain) · Prologue B "Professor
Poopy Paws" · the Ebb night · the library research gate (Act 1 beat 2) · **Act 1 beat 3
"THE KIT"** (`library_phase = "kit"` — `_kit_dose` / `_kit_wand` / `_kit_book`, gated in
`fuji.gd` on the real flags `fuji_dose_found` / `fuji_darts_made` / `fuji_tome_taken` →
`fuji_kit_made`, which is `Chapters.KIT_ARMED`) · THE DEFENCE OF LANTERNWOOD · **Act 1
beat 3b "THE MOTION"** and **the crossing** (below) · the combat core (compounds, status
ailments, the 2-member party) · the RPG layer (levels, gear, satchel, save/load) · the
five-lands overworld, Alembic Town, Lanternwood, Whisker Meadow.

**PROLOGUE A0 "THE FEVER" (2026-08-22)** — the cold open, before the festival:
where the chemistry came from. Mom is ill, the doctor's mending "doesn't take
for long" ("Is there anything else?" / **"Not in my bag."**), and the boy who
can't cast goes and READS — the Academy reading room's search gate (the fancy
enchantment shelf must fail him TWICE before the plain still-room shelf gives
up half a page, which he COPIES, because he can't borrow it), then the simmer
at the family hearth (ONE colour warming cold→amber; the four reagents stay
A12's), one night's sleep for her, and the lab corner built by morning.
Three new maps: **`momroom`** (her bedroom behind the west-wall plank door,
the sickroom recipe played warm), **`academy_library`** (deliberately the
Lanternwood library's exact shape, 20 years early), and
**`downstairs_bare`** — a NEW BYTE-LOCKED TWIN of `downstairs.txt` (rule 7):
same grid + anchors, east corner bare (crates where the boiler will stand;
the flask shelf is already there as Mom's preserve shelf).
`scene/downstairs_fever.gd` picks which map it loads on
`prologue_remedy_made` — the corner getting built IS the beat. Both twins
carry **MOM'S DOOR** (`'` cells): walkable in bare, a closed plank door
forever in the built room. New sheet `npc_mom_bed_gen` (the kitty_bed rig on
the mom palette). Seven flags, `Chapters.FEVER_DONE`, carried by every
festival beat; `prologue_open` now hands to `house_fever.tscn`, and A0-8's
"TWO SUMMERS LATER." card lands on the untouched festival morning.
`tools/fever_probe.gd` (31 checks) covers the chapter and ends exactly where
`prologue_probe` begins. Full statement: DESIGN.md → PROLOGUE A0.

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

**THE 2026-08-01 SWEEP + THE CULTURE KIT.** A full bug sweep of Alembic Town and the
Academy, then a visual pass. The orphaned `assets/_culture_props.py` family (unwired
since the forest-floor rebuild) is LIVE again in both eras via the shared recipe: the
**notice board** and **messenger owl roost** on the plaza's north rim (`kK`/`cC`), and
six **hook lanterns** (`hH`) — one beside each great tree's ladder landing, two
flanking the south gate; candles are honest fire, so they burn drained. The exterior
red/magenta palette family was swept to `BRASSD`/`COPPERD` (now both in `_tilekit` —
lamp cages, pipes, valves, chimney flues, stall glint, cabin stoop; interiors still
pending, see the art-pipeline skill). Functional fixes: **raw exit zones now re-deliver
after banners and respect the entry lock** (`TravelScene._wire_exit`/`_exit_ok` — a
swallowed gate event used to leave the exit silently dead, and entering town holding
down bounced straight back out), fest/thesis wall all THREE mouths, A13's School
marker got a lane-wide shape and its banner says NORTH LANE (the stair is gone), the
Academy's border mouth is exactly its road, and ~86 stale canopy-era PNGs are deleted.

**THE LADDER IS A LANE, AND THE GOOSE GOES UP IT (2026-08-02).** Two consequences of
the forest-floor rebuild, both reported from play. **A rope ladder is now ONE LANE WIDE
and you are on it or off it** — `PartyMember._climb` pins the body to the run's own
centre line and takes only the SIGN of the vertical input (so a diagonal is simply
*up*), the hop is refused on the rungs, and `_funnel` reaches the lane one cell out
because the mouth is narrower than the ladder: the rungs sit inside the trunk's four
columns, so a 12px body only fits through the middle 20px and walking at a great tree
six pixels off centre used to stop you dead against bark. `AIBrain` gained the matching
rule — **a follower never stops on a `link` cell**, because the 34px follow band is
shorter than a ladder and it was settling a storey short, on the rungs. `tools/
ladder_probe.gd` holds all of it. And **the goose theft was restaged a third time**: the
2018-era fly-by came in from off-screen west and left over a river bridge this grid no
longer has, so the bird visibly BLINKED OUT one beat before it flew in (the flight
teleported it off-camera to start from) and Sage sent you over a bridge to an orchard
that was now lawn. It takes off from where it has been standing now — in frame, above
the dialog box, watched — and goes UP onto a neighbour's ring deck, which makes getting
the ribbon back a beat about the boy who can't do magic CLIMBING.

**THE GREAT HALL IS THE FF6 OPERA SHOT (2026-08-04, rebuilt from the ground up).**
`hall.tscn`'s room is 24×21, one screen wide, and **the only walkable ground is the
full-bleed STAGE and the pit strip at its foot — everything south is ambiance**: three
amphitheatre tiers of high-backed pews wall to wall, THIRTY live bobbing audience backs
nudged onto baked pew ARCS (`AUD_ARC` in hall.gd married to `HOUSE_ARC` in the gen), a
radial gloom rounding the corners, the runner falling to a door glint nobody walks to.
The proscenium's law came off the reference photo: **the opening is dark and the frame
is gold** — glittering midnight backdrop, gilt multi-order arch, mint rose window
(visible ONLY from the podium), two-layer velvet valance with a clock cartouche, gold
owls in lit niches, and 48px MASKING FLATS spanning both wings over solid `w` cells
(walk-behind lint 7 forbids hiding a controllable body; the flee TWEEN passes through
the velvet instead). **The FLOATING CANDLES are the room's magic** — Tier-3 hframes=4
tapers flickered by `_process`, excluded from the houselights snapshot, DOUSED in a
north-south wave for the recital's act (`_candle_douse` beside `_house_set(HOUSE_DOWN)`)
and relit at "Stop. STOP." Both walk-gates and both probes derive from the map and
survived unedited; the hall left `_check_art.py`'s `UPPER_REQUIRED` (no Tier-2 art
remains — everything over a body is y-sorted). Full statement in DESIGN.md → the
`scene/hall.gd` scene-inventory block.

**MUSIC + THE AUTUMN TITLE SCREEN (2026-08-22).** Four looping SNES-register tracks
out of `assets/_gen_music.py` — the art doctrine applied to audio: stdlib-only
synthesis of hand-written note tables, regenerate → lint-free → `--headless
--import`, loop-folded tails so the seam is inaudible. `scene/music.gd` (autoload
`Music`, LAST in the order, references no other autoload) picks the track by
polling the current scene's path: unmapped scenes keep what's playing (the SNES
door rule), `""` fades to silence (the accident, the Ebb quake, the cold-open
cards). And `scene/title.tscn` was rebuilt to the opening-screen sketch:
`assets/_gen_title_art.py` bakes the autumn corridor and the stacked cream title
(`title_bg.png`, registered in `_check_art`), adult Basil's real `walk_down` ambles
into the camera on the leaf carpet, falling leaves replaced the snow, and the menu
sits bottom-left. **SFX (2026-08-22):** `assets/_gen_sfx.py` + autoload `Sfx`
(just before Music) — `ui_*` verbs in the title screen and all three modals, a
door whump on every travel, and **Star-Fox talk blips**: three synthesized voice
timbres pitched per speaker (`sfx.gd VOICES`, unlisted names hash to a stable
pitch), one blip per third letter, punctuation silent; the dialog box looks Sfx
up by PATH (the kit rule). Full statement: DESIGN.md → "Music".

**THE TWO-SCENE SPLIT + PERMANENT DUSK (2026-08-23).** Alembic Town is TWO
SCENES now, per the owner's sketch: **THE FLOOR** (`alembic_town` + era twins,
`town.txt`/`town_fest.txt` rebuilt — no rings, the four trunks are bare shafts
baked from row 0 running off the frame top into leaf-gloom) and **THE BOUGHS**
(`alembic_canopy` / `canopy_fest` / `canopy_fever` / `canopy_thesis`, NEW
byte-locked pair `canopy.txt` ↔ `canopy_fest.txt`, 80×32: four ring decks at
one height joined by ROPE BRIDGES through `E` gate cells, a `tree_platform`
landing, and **THE DROP** — the void renders the town thirty feet down, roofs,
lane ribbons and amber window pinpricks, leaf-fringed at every boundary). The
four rope ladders are **CLIMB-THROUGH travel mouths** (floor `top1..top4` ↔
canopy `head1..head4`; `Game.town_spawn` carries "topN"/"headN" and the body
leaves climbing and arrives climbing — `TravelScene._wire_ladder_tops` /
`CanopyScene`). The town is in **PERMANENT DUSK**, diegetically (the crown
closed over the clearing a generation ago): dusk palettes both eras + `$Dusk`
CanvasModulate in the present pair, lamps + hook lanterns lit at noon, and
`components/fireflies.gd` — blinking chartreuse motes (the mint fx cells
tinted), at deck level AND below it on the boughs. The strata tokens left the
town grids (one storey per scene; AIBrain's never-stop rule keys on the
`ropeladder` TERRAIN now), DESIGN.md's old "REJECTED: a two-scene split"
bullet is formally repealed with each objection answered, and the beats were
restaged: the goose is TREED in canopy_fest (the theft exits up tree 3's
ladder line; the startle/ribbon play on the deck), the doorstep call +
Schweinler's creep live in canopy_thesis (the camera never saw the creep's
ground half anyway), the dash squelches on the deck and hands `dash` down the
ladder mid-run, the fever/fest home doors moved up tree 1 with the interiors
retargeted. Probes updated and green: ladder (cross-scene climb), town, fever
(33), prologue (65), recital, academy, party (phase 3 = the leash across the
boughs), save, zwalk lint ×2, `_check_art` incl. the new TWINS pair.

**THE 2026-08-22 CLUNK SWEEP.** Four fixes reported from play, one of them story-sized.
**THE AMBUSH (Act 1 beat 3 leg (a)) is BUILT** — it was the missing link: nothing in
play ever routed the library door to phase "kit", so the story dead-ended on the thesis.
Now `thesis_found` without `fuji_kit_made` puts two unkillable slimes in Lanternwood's
upper lane (anchors `ambush_e`/`ambush_w`), plays the failed reach once ("...I have a
stick. I am pointing a stick at you.", sets `fuji_chased`), and the arch routes "kit"
for exactly that window (`lanternwood.gd::_on_travel`); the kit-night speech skips on
re-entry. **The home door is a press, not a floor tile** — all three eras' zones hang
over the trunk face (24×8 at `home+(8,-8)`), because a zone on the ring deck's only
through-row yanked in anybody crossing their own deck; TravelScene resyncs stale
`_standing` latches at entry-lock end. **Schweinler CLIMBS now** — the creep's last leg
used to be one floor-to-deck diagonal tween (a pig levitating over the fascia); it walks
the lanes to the new `creep_foot` anchor, climbs the rungs' centre line both ways
(back-facing down, `turn=false`), and the bag sits at the deck lip (`BAG_OFF (8,16)`,
also the ladder head — the one cell Basil can't leave home without crossing), not on
the rungs. **The tree lanes** knit the four ladder feet into the road web (both town
twins, same commit) and the west cottage moved up beside the weapons shop under trees
1-2 — small homes below the tree houses; its old site is a flower garden. Plus the
editor-warning sweep (shadowed `show`/`skew` renamed, integer divisions made explicit,
`@warning_ignore` only in `tools/zwalk.gd` where int division is the intent).

Designed but NOT built — both live in Alembic Town, and the grids they were waiting on
have now settled: **Act 1 beat 4 — ASKING AROUND**, where the wander gate is not a crowd
but **adult Sage and Basil's mother**, and the rumour that he walked into the deep wood
is the direction as well as the dread; and **beat 5b — THE HOLLOWAY**, the sunken green
lane to the SE coast that was safe for four hundred years because the way-charms burned
along it, and is not any more. See DESIGN.md beats 4 / 5b.

Next, per DESIGN.md "Build order": **KO + FOCUS** → vestiges (gated to Act 2's first
obelisk) → the Return.

**Press `0` anywhere in a debug build** for the dev chapter selector — all 52 beats,
staged with roster/phase/spawn/flags. Adding a beat is one row in `scene/chapters.gd`.

## Commands

```sh
godot --path .                             # run (dev window 1152×648)
python3 assets/_gen_tileset_<scene>.py     # regenerate art
python3 assets/_check_art.py               # lint the output
godot --headless --import                  # REQUIRED after any regen or new class_name
godot --headless --script tools/shot.gd    # eyeball a scene (see probes-and-shots)
```
