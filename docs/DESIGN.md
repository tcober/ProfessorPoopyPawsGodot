# Professor Poopy Paws — Design Bible

> Canonical, tool-agnostic design doc. `CLAUDE.md` and `AGENTS.md` point here so any AI
> assistant (Claude Code, Cursor, Copilot, etc.) shares the same source of truth.

Tone is a blend of **Adventure Time** (whimsical, absurd, heartfelt) and **Final Fantasy** (earnest
stakes, party/progression depth, emotional arcs).

Structure in one line: **Chrono Trigger / Sea of Stars overworld for travel; zones
play as an ALttP-style top-down shooter (laser gun) — not turn-based.**

## Story — Chapter Structure (canon, 2026-07-12)

Logline: a brilliant **science cat** in a world of casual magic — the one kid who
can't do any — is publicly branded **"Professor Poopy Paws"** on the day of his
thesis, loses his girlfriend to an accident that erases her memory of him, and
walks into the wilderness a hermit. Years later the world's magic drains away in
a single night (**the Ebb**), and a librarian stranger named **Fuji** finds the
one paper that reads like a map back — his — and goes looking for its author.
Together they restore the world's magic; along the way he grows past the name
and finds love again, with her.

### Lore spine

- **The Ebb** (the calamity, event): one night, with no warning and no author,
  magic ebbed out of the world like a tide going out — lights died, floating
  things fell mid-float, the Academy's wards went cold. It is **natural /
  ancient, NOT villain-made** — Schweinler is a personal rival only, never the
  world's villain. WHY the tide went out is the standing mystery of Act 2+
  (the network dying of age? never meant to be permanent? something below,
  drinking?) — deliberately unresolved for now; the mystery is the engine.
- **The Drain** (place): where the magic *went* — somewhere deep beneath the
  eastern wastes. The wastes themselves are the blight that spread outward
  from it after the Ebb.
- **The obelisk network**: the crystal obelisk + outcrops already on the
  overworld are ancient structures nobody living built, which once circulated
  magic through the world like a water table. Since the Ebb they stand dark.
  Restoring the world = probing and relighting the network, region by region.
- **Slimes are curdled magic**: feral residue pooling in the wild since the
  Ebb — every enemy ties to the mystery, and combat exists ONLY in the
  present-day chapters. The prologue world is SAFE (walk/hop/interact only).
- **Basil's thesis** — *On Re-Enchantment: Why Science Is Magic's Equal*:
  magic is not gone, it is merely sleeping; science can measure, carry, and
  rekindle it. Written as an academic argument and laughed off a stage; after
  the Ebb it reads as the only known map back. This is why Fuji seeks him.
- **The laser gun is hermit-built** — magic-free tech Basil invents alone in
  the wilderness. Nobody carries a gun in the prologue.

### Characters

**World rule — animal folk (2026-07-12):** the world is peopled by
anthropomorphic animals of MANY species, not just cats, and **a character's
personality matches its animal**: Schweinler the boorish pig, Basil and Fuji
the particular, curious cats, and townsfolk chosen species-first (a gentle
sheep matron, a know-it-all owl, a chaos goose...). New NPCs pick the animal
that IS the personality, Adventure Time style — never a generic villager.

- **Basil** — the science cat. Sparkless in a world of casual magic; got into
  the Academy on potion-craft (the one science that looks enough like magic);
  branded "Professor Poopy Paws" at his thesis; hermit for years **beneath the
  Elder Tree** on the riverbank, where he alone kept *measuring* the dead
  crystals of the nearby wastes. Comes back "for the science, not for the
  people" — the emotional runway of the whole game is closing that gap.
- **Fuji** — tortoiseshell librarian (current playable; see Asset Specs). The
  Academy's archivist, keeper of a library nobody visits. **A stranger to
  Basil's past** — she knows him only through the thesis she unearths after
  the Ebb. Pulls him back into the world; the slow-burn love of the story.
- **Sage** — Basil's little sister (herb-name family). Younger AND
  effortlessly gifted at magic as a kid — her teasing is sibling-thoughtless,
  not cruel. Present day: the Ebb took her whole identity; she scrapes by
  running THE CRACKED FLASK item shop selling *potions* — the sister who
  teased Basil for having no magic now survives on his kind of craft.
  Reconciliation is an Act 2 thread.
- **Kitty Cool** — the maker girl. Meets kid Basil in Whisker Meadow; her
  creed: "anyone can wiggle their fingers — try *making* something."
  Run down by the machine Schweinler was joyriding; lives, but her memories
  never return (the doctor's verdict stays honest — no miracle recovery).
  Present day: **largely left behind** — she lives in a distant town, hands
  still remembering what her mind lost, running a little handmade-goods shop.
  One optional quiet scene: Basil visits, she doesn't know him, he leaves
  without saying who he was. Closure, not reunion.
- **Schweinler** — the pig bully (sprites to be designed fresh; the deleted
  generator is not recovered). Rich family, all swagger. Kid bully → Academy rival who plants the bag and
  coins the name → the machine he was joyriding runs Kitty down (a rich kid's
  imported toy — machines exist in this world, but he did NOT cause the Ebb).
  Present day: recurring personal rival — he's weaseled into the Capital's
  court as the self-declared "Calamity Expert," obstructing and stealing
  credit. His arc ends personal-sized: the apology finally arrives and Basil
  finds he's already past it.
- **Minor cast**: the Dean (from the old intro), the doctor, the fountain
  classmate (unnamed, one scene), the Copper Kettle innkeeper (the town's
  memory — the one who recalls where Basil went), festival townsfolk, and
  Dr. Feathers the bird (kept — beloved wake-up gag).

### PROLOGUE A — "SPARKLESS" (kid Basil · Alembic Town, bright era)

1. **Festival morning — home start** *(playable from the first frame;
   reshaped 2026-07-12)*: kid Basil wakes in the loft bedroom on festival
   morning, walks downstairs, and says good morning to MOM by the hearth —
   her send-off is the front-door key. He steps out into the bright-era
   town himself: the Founding Festival, the Academy open and glowing, kids
   levitating ribbons in the fountain square.
2. **The teasing** *(proximity cutscene)*: the beat fires when Basil first
   walks BY the fountain square, not on scene entry. Basil can't raise a
   spark. Sage (younger, floating three ribbons at once) teases; kid
   Schweinler makes it public and mean.
3. **Wander gate — the pout** *(playable)*: the player is turned loose in the
   festival town. Townsfolk dialog is well-meaning but every line stings
   ("everyone blooms eventually, dear"). Talking to a few + reaching the south
   gate unlocks leaving — the game *teaches its own loop* (wander, talk, exits
   gated by story state).
4. **Whisker Meadow — Kitty** *(playable fetch-quest)*: pouting by the stream,
   Basil finds a girl cat wrestling with a hand-cranked whirligig. She doesn't
   care that he can't do magic. Find her three parts around the meadow (gear
   by the stream, spring in the flowers, crank by the cairn) — teaches
   interact/explore verbs, no combat. It flies. First friend.
5. **Montage cards**: seasons pass — building things together, the workshop
   corner in Basil's cottage, the first potion that actually fizzes. "YEARS
   LATER." They're dating; he got into the Academy on potion-craft.

### PROLOGUE B — "PROFESSOR POOPY PAWS" (college-age Basil · bright era)

Beats 1–5 re-tell the old five-part intro's gags, but **everything is built
fresh** — the deleted implementation and its art are not recovered (2026-07-12
decision: the old look is rejected wholesale); only the beats are canon:

1. **Night before** *(cutscene)*: Schweinler plants the bag outside the
   cottage door. ("A LITTLE 'CONGRATULATIONS' FOR MR.
   YOUNGEST-PROFESSOR-EVER.")
2. **8:57 AM** *(cutscene, the loft bedroom in bright dressing)*: Dr.
   Feathers, "FIVE MORE MINUTES", the clock, panic.
3. **SQUELCH.** *(cutscene, cottage door)*.
4. **The dash** *(playable)*: sprint through waking Alembic Town to the
   Academy on the cliff — hop-only obstacles (carts, puddles, a goose), a
   fading trail of brown paw prints behind him. The grand stair is the final
   climb.
5. **The lecture** *(cutscene, Academy hall interior — new scene)*: the
   re-enchantment thesis; Schweinler's "WHAT'S THAT SMELL?!"; the naming; the
   laughter. Cards: "THE NAME STUCK."
6. **The call** *(new beat)*: Basil, wrecked, sends word to Kitty by pneumatic
   post. Her reply arrives instantly: "ON MY WAY. PEDALING FAST. —K"
7. **The accident** *(cutscene, restrained — mostly offscreen)*: a machine
   roar, a crash sound over black, Schweinler's stunned "...I DIDN'T SEE
   HER." She lives. The doctor: her memories will never come back. She looks
   at Basil like a stranger.
8. **The fountain** *(cutscene, the existing fountain square at dusk)*: a
   classmate asks what's wrong; Basil confesses everything; "you're selfish —
   YOU weren't the one who got run over." The worst possible words at the
   worst possible moment.
9. **The leaving** *(playable, night)*: stick and knapsack. Walk out through
   the sleeping town — every NPC gone, windows dark — out the south gate into
   the dark overworld, walking east until the fade. Cards: "HE STOPPED GOING
   ANYWHERE AT ALL." / "YEARS LATER."

### ACT 1 — "THE EBB" (Fuji, present day — ends where the current build begins)

1. **Cold open** *(cutscene)*: the night of the Ebb — a soundless flash, the
   obelisk light dying, ribbons falling mid-float, the Academy going dark.
   Cards.
2. **The library** *(playable Fuji, new Academy-library interior)*: weeks
   later. Fuji hunts by candlelight for *anything* about magic leaving.
   **Research gate**: find the right stack (light exploration puzzle),
   unearth a dusty thesis — *On Re-Enchantment: Why Science Is Magic's
   Equal* — B. Basil. Marginal note: laughed out of the Academy.
3. **Wander gate — asking around** *(playable)*: nobody knows a "Basil."
   Everyone remembers "**Poopy Paws**" — the cruel name outlived the cat (the
   theme weaponized as a story gate: the player must ask about the *insult*
   to find the man). The Copper Kettle innkeeper: "went east, past the
   meadow, years back. Never came through again."
4. **The road east** *(playable)*: Fuji's overworld travel; **Whisker Meadow
   is her combat tutorial** — the meadow that was a childhood idyll in
   Prologue A now crawls with curdled-magic slimes (tome swing + darts taught
   here; same map, two eras, the loss made playable).
5. **The hermitage — the Elder Tree** *(new small zone: the riverbank under
   the giant tree, entered from its overworld landmark)*: a lean-to among the
   roots, corkboard research, crystal instruments — Basil has spent years
   *measuring* the dead crystals of the nearby wastes, the only person in the
   world with data on the Ebb. And a strange brass gun.
6. **The refusal → the party** *(cutscene + fight)*: he says no. She reads his
   own thesis back at him. A slime pack hits the camp — they fight side by
   side (**the 2-member party mechanic unlocks HERE, diegetically**). He
   comes back "for the science, not for the people."
7. **Return to Alembic Town**: the shuttered, drained town of the current
   build. Act 1 ends exactly where today's game boots — bedroom, downstairs,
   town, overworld, meadow.

### ACT 2+ — "RE-ENCHANTMENT" (the main game, sketched loose on purpose)

- **The mystery is the engine**: probe the obelisk network region by region —
  the Burrows (already anchored on the map), the Obelisk monument, the
  Capital, the Horn. Each expedition is a dungeon; each success relights a
  region (the glow-overlay pipeline literally exists for lights coming back
  on — restoration as a visible, palette-driven reward).
- **Schweinler recurs** at the Capital as the court's "Calamity Expert" —
  obstruction and stolen credit, escalating to a personal reckoning that
  lands as anticlimax-on-purpose: the apology arrives and Basil finds he's
  already past it.
- **Sage thread**: THE CRACKED FLASK, the drained sister, reconciliation.
- **Kitty side note**: one optional scene in a later town. Closure, not
  reunion.
- **Fuji romance**: slow burn in camp/inn beats across the acts; magic's
  return and "finds love again" land together — the metaphor made literal.
- **Party member 3** (future, "the sympathizers"): slot stays open; the
  roster architecture already supports it.

### Pacing rules

- **Never >90 seconds without control.** Every chapter alternates cutscene →
  playable gate. Time-skips are cards (the `card()` mechanism from the old
  cutscene kit), never montage cutscenes.
- **Wander gates over triggers**: progress unlocks by talking/finding (N
  townsfolk, a stack in the library, parts in the meadow) — the
  explore-talk-progress loop is taught from minute one.
- **Reprise staging**: the same three stages carry the whole story — Alembic
  Town (festival / thesis-day / drained), Whisker Meadow (Kitty / slimes),
  the Academy (glowing / barred / dark library). Two eras of one place beat
  many places seen once.
- **Combat debuts in Act 1** (Fuji in the meadow). The prologue's only action
  verbs are walk/hop/interact — the world before the Ebb was *safe*.

## Themes

Humiliation → isolation → being seen by others → growth → redemption and renewed love.
Magic as a metaphor for hope/connection returning to the protagonist and the world.
The insult outlives the man — "Poopy Paws" is remembered when "Basil" is
forgotten, and finding him means asking about the wound (Act 1's story gate).
Making-by-hand vs. wishing — Kitty's creed, Basil's science, Sage's inversion:
what is built endures what is granted.
The loss made playable — the same stages in two eras (festival town vs.
shuttered town, idyll meadow vs. slime meadow); the world before the Ebb was
safe, and the player feels the difference in the verbs.

## Influences

- **Adventure Time:** surreal biomes, oddball NPCs, comedic-but-sincere writing.
- **Final Fantasy:** progression systems, emotional storytelling, eventual party members
  (the sympathizers), set-piece dungeons.
- **Zelda: ALttP:** zone gameplay — top-down 4-directional action combat, dungeons,
  items as gating tools.
- **Chrono Trigger / Sea of Stars:** the **overworld** — a miniature tiled continent
  walked by a tiny chibi travel sprite (~16 px tall on 16×16 terrain tiles) between
  full-scale places, built the way CT built its own (a small reused tile vocabulary,
  autotile coasts and cliffs, towns as drawn clusters of roofs). Their turn-based
  combat is **not** adopted; zones stay an ALttP-style top-down shooter.
- **Secret of Mana:** the closest gameplay cousin — real-time top-down action combat
  inside a lush 16-bit JRPG shell. Reference for how zones should _feel_: saturated
  organic terrain, big readable sprites, action combat that stays friendly, whimsical
  enemies with personality, and the seamless flow between exploring and fighting.
- **Art direction** (canonical influence list): **Final Fantasy VI, Chrono Trigger,
  Secret of Mana, Sea of Stars, Adventure Time, and the Paper Girls comic.** Gameplay
  feels like Zelda, but the _look_ is richer 16-bit JRPG: **TRUE SNES density**
  (see Tech Conventions) — big deliberate CT-chunk pixels, ~24×13.5 tiles on
  screen, characters ~2 tiles tall like CT/SoM. FF6/CT field-sprite proportions
  (head/torso/legs roughly thirds), shading ramps and per-material outlines over flat
  fills, textured tiles, bitmap-font dialog boxes — with Adventure Time's whimsy in
  character/creature design and **Paper Girls' color law everywhere** (see "Palette
  Registry"): palettes stay MINIMAL and surreal — duo/tri-tone casts, one dominant
  hue field plus one hot accent, shadows hue-shift violet or teal (never neutral
  gray). Wood may be an honest warm brown (a material, not the field); the ban is
  on naturalistic beige/gray mud as a scene's whole field and on un-hue-shifted
  muddy darks.

**World genre: steampunk-inflected medieval fantasy.** The world is a
Zelda-ALttP-style kingdom — cottages, bluffs, stone-and-timber architecture, a
walkable overworld between named places — layered with an alchemical /
Victorian-inventor technology strand carried by Basil and his world's
trappings: gears, brass fittings, glass apparatus, lanterns, laser-gun
gadgetry, corkboard research. It's already in the lore's own naming (Alembic
Town — an alembic is distillation apparatus) and in Basil's design (goggles,
lab coat, beaker magazines). Future locations, NPCs and props should lean into
this pairing — brass-and-flask over chrome, candle-and-gear over circuitry —
never modern tech or generic-fantasy defaults.

## World Structure — Overworld + Zones

Two layers:

- **Overworld** (`scene/overworld.tscn`) — the travel layer: a Chrono Trigger /
  Sea of Stars–style miniature TILED continent (64×36 tiles, 1024×576 px,
  camera-clamped), stamped at runtime from a generated CT-style tileset
  (~210 unique tiles; coasts, riverbanks, cliff feet, canopy rims and road
  shoulders are neighbor-keyed autotile transitions that dedupe by
  construction) onto two TileMapLayers — under and over the chibi, so Basil
  passes behind the forest canopy rim. He walks it as a 24×24-cell chibi
  sprite (~16 px tall) over 16×16 terrain tiles; buildings are SQUAT (a
  cottage is 32 px, ~1.8× the figure) so the hero reads proportionally big,
  the CT area-map way. The 2026-07 darker pass replaced the candy-mint
  field with mossy emerald / deep ocean teal / violet-slate rock (the law
  holds: deep + saturated + hue-shifted, never gray).
  **No combat on the map.** Terrain gates travel — water, forest, mountains,
  rivers and buildings are solid; sand, grass, roads, bridges,
  hills and the wastes are walkable; bridges and roads open the routes. The
  eastern drained wastes render **hot violet-magenta** — the magic-drained
  premise carried by color.
- **Zones** — the full-scale scenes entered from the map, where the existing
  gameplay happens: 48×48-cell field sprites, SNES-Zelda ALttP-style movement, and
  the top-down laser-gun shooter combat.

**Location markers** (`Area2D`, `scene/overworld_location.gd`) carry
`id / display_name / target_scene / locked_text`. Walking onto one shows its name in
a banner label; unlocked markers fade out and enter their zone; locked ones show
flavor text instead. The **`Game` autoload** (`scene/game.gd`) remembers
`overworld_spawn`, so leaving a zone returns Basil to the marker he entered from.

**Towns are CT-faithful ICONS** (the 2026-07 icon pass): on the overworld a
town is ONE hand-drawn cluster composition — overlapping squat roofs at
staggered heights on an organic dirt apron, landmark silhouettes rising
behind — over solid cells, NOT walkable. Its one walkable gate-mouth `D` cell
carries the travel marker; stepping on it fades INTO the town's own walkable
zone scene, exactly how CT's overworld towns open into their village maps.

**Geography:** **ALEMBIC TOWN** as a DENSE cluster icon on the SW coast —
seven small overlapping cottage roofs (openings are dabs: a town read from
across the plain), the Academy's crenellated castle-keep at the back rank,
and the steamworks' riveted copper boiler venting a steam plume the whole
map can read, warm lit windows + rose window on the glow overlay, a
flask-sign gate — → ONE winding trail NE past Whisker Meadow (center-west),
over the rosewood bridge across the N→S river, petering out at the drained
wastes; mountain ridge + foothills N with the Burrows pass (cave anchor),
the **CAPITAL'S CASTLE** (`C` cells, 6×5) riding the west massif — pale
stone hold, blue cones, pennants, its own steaming flue — and the **HORN**
(`V`, 5×4), the one snowcapped summit breaking the ridge rhythm at the
massif's NW tip; the **ELDER TREE** (`g`, 4×6, ~5× the chibi) leaning over
the riverbank between trail and wastes — the plain's sense-of-scale anchor;
wastes E/SE with the **crystal OBELISK monument** (`O`, 3×4, at the obelisk
anchor) and 2×2 `K` crystal outcrops scattered around it; lone plains trees
+ flower patches scatter the grass; ocean frames everything. (The static
cloud-shadow overlay was cut 2026-07-06 — at CT zoom the soft dark ovals
read as smudges, not weather.) Region edges are drawn as 1-cell
stair-steps in the map txt ON PURPOSE — the autotile's 45° corner cuts
render them as continuous diagonal coasts/rims.

- **ALEMBIC TOWN** (`town` → `alembic_town.tscn`) — the icon's gate mouth;
  it opens into the walkable town at its south gate.
- **WHISKER MEADOW** (`meadow` → `meadow.tscn`) — the first field zone; the one
  playable combat zone today. A flower ring marks its road entrance.
- **THE BURROWS** (design only) — future dungeon; its pass and cave anchor
  already sit in the northern ridge.
- **THE DRAIN** (design only) — where the magic *went* when **the Ebb** took
  it: somewhere deep beneath the eastern wastes (see "Lore spine" in the Story
  chapter).

**Alembic Town, walkable** (`scene/alembic_town.tscn`, 56×34 tiles — rebuilt
from scratch 2026-07-11 as the Kakariko-style hub, LIVE in the flow) — the
village at zone scale (48px player), riding the SAME OverWorld tile driver
(tree borders = the forest class, lanes = the trail painter, fence class
yards, sea+beach pond, a river stream with one bridge cell), composed
DEPTH-FIRST: the barred **Academy crowns a north cliff terrace** on the
town's central axis (`school`, announce-only — "no magic has stirred here in
years"), a grand stone stair descending through the authored cliff-column
band (16×32 face columns, 3 salted variants stamped per column — the
meadow-boulder reuse pattern) to a lamp-flanked stair plaza; the **fountain
square** at the lane crossing (basin + brass alembic-bulb finial, trail ring
forking around it, the flask-stall on its rim); the **weapons shop** "THE
BRASS FANG" (`weapons`) and **item shop** "THE CRACKED FLASK" (`items`)
facing the market cross-lane — one shared shopfront builder, same salt, only
roof/sign/wares differ so their facade tiles dedupe; the two-story **inn**
"THE COPPER KETTLE" (`inn`) fronting the square SE by the stream bridge, lit
windows and a tankard sign (all three announce-only until shops earn
systems); **Basil's cottage** NW in its fenced yard with the open candle-lit
doorway (`home` → `downstairs.tscn` at the front door); the locked neighbor
cottages staggered SW (`cottage_w`/`cottage_e`) around the well and fenced
garden; the fenced NE orchard across the bridge; the SE pond; and six
walk-behind trees (canopy rows walk on the upper layer, trunk row solid).
Buildings are TWO map chars: solid facade rows + WALKABLE roof rows whose
art rides the upper tile layer, so the player walks behind rooflines,
CT-style. The south lane gap (`exit_south`) returns to the overworld at the
town icon. Spawns route through `Game.town_spawn` (read-and-clear; "" = the
south gate, `home` = below Basil's door — the downstairs front door now
opens HERE, not onto the overworld).

History: the 2026-07 town carve absorbed the old standalone "Basil's Bluff"
into Alembic Town and moved the town from its old NE-forest anchor onto the SW
coast; the proportion pass tore the rampart back out (the walled compound
dwarfed the chibi) in favor of an open on-map cluster; the icon pass then went
CT-faithful — the on-map cluster became a drawn icon and the open town moved
into its own walkable scene. The Burrows and the Drain stay design-only until
their zones exist.

The cracked/dead-tree/crystal **wastes biome** (east) visually encodes the
drained-magic premise — the blight that spread out of the Drain after **the
Ebb** (see the Story chapter's lore spine). New regions and zones unlock as the
story progresses; the gating tools are terrain plus story keys.

## Tech / Engine Conventions

- Engine: **Godot 4.6**, GDScript, GL Compatibility renderer.
- Base resolution: **384×216** (16:9 — canvas_items stretch, integer-scales 5x to
  1920×1080 / 10x to 4K so it fills a widescreen TV; the dev window runs 3x at
  1152×648; `snap_2d_transforms_to_pixel` on). Nearest filtering. No camera zoom
  anywhere — on-screen scale is purely sprite pixels vs. the viewport. (The
  2026-07 zoom-out from 320×180: same sprites, ~20% more world on screen, Basil
  reads ~15% of frame height instead of 18%.)
- **TRUE SNES DENSITY** (the 2026-07 CT-chunk restart): pixels are big and
  deliberate, Chrono Trigger scale — the earlier "SNES composition at 2x pixel
  density" was reversed because fine detail read as noise, not craft.
- **Scale Table** (canonical; mirrored by `assets/_core.py` constants — change them
  together):

  | Thing                            | Size                                                                                     |
  | -------------------------------- | ---------------------------------------------------------------------------------------- |
  | Viewport                         | 384×216 (16:9; 5x → 1920×1080)                                                           |
  | Terrain tile (zones + overworld) | **16×16** (`ZONE_TILE`/`OW_TILE`)                                                        |
  | Zone character cell (Basil)      | **48×48** (`ZONE_CELL`), figure ~33 px, feet y=44 (`ZONE_FEET`)                          |
  | Slime cell                       | 24×24                                                                                    |
  | Overworld chibi cell             | **24×24** (`OW_CELL`), ~16 px figure, feet y=21 (`OW_FEET`)                              |
  | Overworld landmark icon          | 32×32 (`ICON`)                                                                           |
  | Interior room map (house)        | 24×14 tiles = 384×224 (view clamps to 384×216; bottom void row is mostly offscreen)      |
  | HUD heart / ammo pip / font_size | 16 / 8 / 8                                                                               |
  | Gun muzzle offset (art contract) | 16 px from origin (`player.gd muzzle_offset`)                                            |

  This puts ~24×13.5 tiles on screen with characters ~2 tiles tall — the CT/Frog
  read where a character is a big chunky figure and every pixel is placed on
  purpose, with enough room around him for the world to breathe.

- Architecture: **component-based**. Reusable behavior lives in `components/` as nodes/
  resources (HealthComponent, HitboxComponent, HurtboxComponent, …). Entities in
  `entities/` compose these. Shared data (stats, items) as custom `Resource`s in
  `resources/`. Playable rooms/levels in `scene/`. Art/audio in `assets/`.
- Movement: `CharacterBody2D`, 8-way movement with 4-way facing (fires in the facing
  direction), ALttP-style.
- **Controls** (InputMap in `project.godot`; every action is POLLED — the shot.gd
  synthesized-press gotcha — so keyboard and gamepad share one code path). Gamepad
  bindings use Godot's generic SDL indices labeled here for the PS5 DualSense
  (2026-07-11); any XInput-style pad maps the same:

  | Action                                 | Keyboard      | Gamepad            |
  | -------------------------------------- | ------------- | ------------------ |
  | Move                                   | WASD / arrows | Left stick / D-pad |
  | Attack (Basil laser · Fuji tome)       | J / Space     | R2 or Square       |
  | Secondary (Basil reload · Fuji dart)   | R · L         | L2                 |
  | Hop                                    | K / Shift     | Cross              |
  | Interact                               | E             | Circle             |
  | Swap leader                            | Q / Tab       | Triangle or L1     |

  `reload` and `dart` are separate actions sharing the L2 event on purpose: only
  the **leader** polls their own secondary (`PartyMember._gather_intent`), so one
  physical button is contextual per character. The analog stick feeds the same
  `move_*` actions (0.2 deadzone) and the intent vector is normalized, so stick
  tilt never changes speed — same 8-way feel as keys.
- Combat: a **laser gun** with limited charges. Firing spawns a `LaserBolt` projectile
  (`Area2D`) that travels and damages the first `HurtboxComponent` it hits. Always-on
  `HitboxComponent`s (e.g. an enemy body) handle contact damage. All damage flows
  through `HealthComponent`. Single shot per `attack` press.
- **Ammo / beakers:** the gun holds `max_ammo` charges; each shot consumes one. **Beakers
  are magazines**: pickups (`entities/pickups/beaker.tscn`) pocket as spares (up to
  `max_beakers`; full paws leave the pickup in the world), and reloading — R/L, or pulling
  the trigger dry — plays the planted pour animation and empties one into the gun. The HUD
  shows hearts + an ammo-pip row.
- **Magic is deferred by design:** the world starts drained, so spell systems are
  introduced later as progression that mirrors the story. The laser gun is the
  early-game, magic-free weapon.

## Current Milestone — Prologue A + B + Combat Core

**Prologue B "Professor Poopy Paws" is LIVE (2026-07-12)** — the thesis-day
chapter, entered straight from A's "YEARS LATER." montage (roster swaps to
`basil_student`, a kit-less adult body on the existing player sheet — no gun;
the laser is still years off). The whole chapter, in flow order:
- **`scene/town_thesis.gd/.tscn`** — ONE scene on the festival town's map +
  tiles, FOUR flag-driven phases dressed only by a `Tint` CanvasModulate (the
  tint law: one painting, never a repaint), routed by
  `Game.town_thesis_phase`: **plant** (night — Schweinler creeps up and leaves
  the bag, "a little CONGRATULATIONS", → the wake-up), **dash** (morning — the
  SQUELCH, the **hop-the-puddles** run with a fading paw-print trail, reach the
  Academy → the hall), **call** (dusk — the pneumatic-post message to Kitty,
  then the machine roar / crash / "...I didn't see her" over black → the
  sickroom), **fountain→leaving** (dusk then night — the blunt badger
  classmate's "you're selfish, YOU weren't the one who got run over", the tint
  slides to night, Basil walks out the south gate → the closing cards →
  `house.tscn` with the adult roster `[basil, fuji]`).
- **`scene/house_thesis.gd/.tscn`** — the 8:57 wake-up, reusing the loft
  bedroom tileset/map/props with a dawn-dim CanvasModulate that snaps bright
  when Basil bolts up; Dr. Feathers the bird (fx) at the window, the panic,
  hop out of bed, the stair cuts to the dash.
- **`scene/hall.gd/.tscn`** + `maps/hall.txt` + `_gen_tileset_hall.py` — the
  Academy lecture hall on the interior Room kit (the `hall` palette: plum
  panelling / rose floor / chalk-mint; its mat key is now `wall`, not
  `timber`, since Room needs `wall`). New reusable interior props in
  `_interior_props.py`: **chalkboard** (corkboard skeleton + a
  `_pixfont`-stamped "RE-ENCHANTMENT" scrawl), **lectern** (desk y-sorted
  pattern), **bench** (workbench counter-walk — audience NPCs stand on the
  walkable top row so their legs tuck = the seated-gallery read). The Dean is
  **Professor Strix the owl** (the childhood note-taker, grown into the
  Academy); the naming plays out, the gallery chants, cards "THE NAME STUCK."
- **`scene/sickroom.gd/.tscn`** + `maps/sickroom.txt` +
  `_gen_tileset_sickroom.py` + the `sickroom` palette (pale lavender walls,
  one warm bedside lamp) — Kitty in the bed (the `npc_kitty_bed` sprite:
  rest/vacant/polite), Dr. Ciconia the stork doctor's permanent-amnesia
  verdict, Kitty's kind-stranger lines, Basil leaves without saying who he
  was.
- Sprites (all in `_gen_prologue_sprites.py`): Mom, adult Schweinler (plum
  waistcoat), the badger classmate, the stork doctor, Kitty-in-bed, plus the
  goose extended to a 6-col waddle. `prologue_fx.png` grew 10→16 cells (+ bag,
  paw-print, bird×2, puddle, zzz) — `meadow_fest.gd` slices it at hframes 16.
**Prologue A pacing pass (same day):** **Mom** is now load-bearing — three
stinging talks make Basil want to go home, and **her encouragement by the
cottage is the gate key** ("Sparks are common as dandelions. You take things
apart to see WHY. That's rarer."). Two minigames: the **goose ribbon chase**
(`entities/npcs/goose_chase.gd` — the goose stole Sage's ribbon; catch it
3× to earn a warmth beat that counts as a talk) and the **crank-up mash** at
the whirligig flight (mash E to fill a meter, the rotor spins up with it).
GOTCHA (2026-07-12): a coroutine polling input on `process_frame` must use
LEVEL-edge detection (`is_action_pressed` + a was-down latch), NOT
`is_action_just_pressed` — the frame signal can fire before the same-frame
press lands, so a just_pressed edge is missed every time (killed the crank
mash until fixed).

`tools/prologue_probe.gd` now drives the WHOLE A+B chapter and asserts every
scene transition + flag; run it after touching any story scene.

**Polish pass (2026-07-12, same day):** three player complaints fixed —
z-order, agency, invisible walls. The direction rule from the pass: **pacing
is fixed with AGENCY, never cuts** — every authored line and wait survived;
control was inserted BETWEEN beats.
- **Runtime FX now depth-sort** (`scene/world_fx.gd`, see the z-order
  doctrine): the thesis-day bag/puddles/paw-prints (the prints were
  invisible under the floor — the `z_index=-1` hack), the wake-up bird/Zs,
  the festival ribbons and meadow quest parts all moved from scene-root
  children into `$World` as decals (north-biased origin + child index 0)
  or airborne FX (ground-anchored origin, art lifted by sprite offset).
  The bed read fixed: Basil's bed spawn nudged 4px north so the quilt's
  y-sort origin (119) beats his (116) — head on the pillow, Zs floating
  OVER the quilt.
- **Prologue A opens AT HOME** (playable from the first frame):
  `scene/house_fest.tscn` (loft bedroom, bright tint) → the SW stairs →
  `scene/downstairs_fest.tscn` (Mom by the hearth; her good-morning sets
  `prologue_saw_mom` and unlocks the front door) → the festival town at the
  home door (`Game.town_spawn="home"`), FREE — the teasing cutscene fires
  from a proximity Area2D when Basil first walks by the fountain square.
- **`Theater.walk_gate(goal, size, relock)`**: the kit's mid-scene
  control hand-back — unlock, one-shot goal Area2D (the dash-goal idiom),
  await the player, optional re-lock. Group-based, position passed in (the
  no-autoloads rule). Prologue B now hands control back FIVE times inside
  its cutscene chain: the walk to the lectern (the Dean's welcome is the
  summons), the walk of shame out the hall door, the walk down the grand
  stair to the pneumatic post (new fest-map anchor `post`), the walk to
  Kitty's bedside, and the walk down to the fountain square — the old
  ~100-140s no-control stretch (hall → call → sickroom → fountain) now
  never runs ~45s without the player moving. `prologue_scolded` flags the
  fountain beat's end (the phase unlocks twice, so the probe needed a
  pollable state). **GATE GEOMETRY (the review pass):** a gate must be
  UNAVOIDABLE for its objective, or the beat soft-stalls with no re-prompt
  — a point-rect is walkable around (the hall's side aisles, the
  fountain's ring roads). The shapes that work: a FULL-WIDTH room band on
  an open row every route crosses (hall row 8, sickroom row 5), or the
  whole objective zone (both town phases gate on the fest cutscene's
  96×96 fountain-square zone). The last steps from wherever the gate
  fired are then staged with `walk_via` waypoints — and since theater
  walks are straight no-collision tweens, any staged path near the
  fountain dog-legs the road ring (`_square_route`/`_post_route`).
  Refused exits also need a physical stop: the gate-mouth road runs to
  the map edge and collision stamps only grid cells, so both town scenes
  wall the mouth just past the last row (`_wall_gate_mouth`).
- **Invisible walls + facades**: the silhouette-fit retypes and the T3
  coverage lint (see the doctrine), plus the `_eave_lift` SIDE bands — a
  body pressed on a building's west/east face no longer paints over the
  wall corner (the "standing on the roof" read; the Academy keep gained
  both bands). Fest-only anchor moves pulled Sage/Schweinler off the
  fountain ring's side lanes.
- **Harness**: `tools/shot.gd` grew `phase:<name>` (shoot any town_thesis
  dressing) and `roster:<id>[:<id>...]` (story scenes assume story
  rosters); the probe covers the home start, the Mom gate (door refuses
  before her), the proximity trigger, and every walk-gate — 33 checks.

### Prologue A "Sparkless" + the combat core (detail)

**The 2026-07 combat-first cut** pared the build to its core loop to hone the
battling and the look. Deleted (git history keeps the implementations, but per
the build-fresh doctrine NOTHING narrative is recovered): the title screen,
the old five-part intro, Schweinler's sprites, and the old cutscene/dialog
kit.

**Prologue A "Sparkless" is LIVE (2026-07-12)** — the game's first playable
minute is the story's first minute. Boot: `scene/prologue_open.tscn` (main
scene; title + era cards over black; ESC skips to the adult sandbox) → the
**festival town** (`scene/town_fest.tscn` on `maps/town_fest.txt` — a BYTE
COPY of town.txt tiled by `assets/_gen_tileset_town_fest.py` in the bright
`town_fest` palette, same builders + salts as the drained town so every lane
is recognizable across eras; the Academy rose window burns mint on the glow —
magic is ALIVE; keep the two grids in lockstep) where **kid Basil**
(`entities/kid/kid_basil.*` — a kit-less PartyMember, walk/hop/interact only;
the pre-Ebb world is SAFE) plays the fountain-square teasing beat (levitated
ribbon fx, Sage's three ribbons, kid Schweinler coining "Sparkless"), then
the **wander gate**: six talkable NPCs (Sage, Schweinler, sheep matron, owl
scholar, chaos goose, mouse kid — the animal-folk rule in action; every line
stings a little), any three talks open the south gate → the **prologue
meadow** (`scene/meadow_fest.tscn`, the same meadow map + quest anchors, no
slimes): meeting Kitty Cool, the whirligig fetch-quest (gear on the beach /
spring in the flowers / crank by the boulders — `prologue_fx.png` pickups
with sparkle loops), the flight finale, montage cards, hand-off to the adult
build (`Party.set_roster([basil, fuji])` → `house.tscn`, "YEARS LATER.").
Quest state lives in `Game.flags`, so leaving mid-quest keeps progress.
**`tools/prologue_probe.gd`** drives the whole chapter with synthesized
presses and asserts every flag flips in order — run it after touching story
scenes, like party_probe for the brains.

The **narrative kit** (built fresh 2026-07-12):

- `scene/dialog_box.gd/.tscn` — the typewriter box: bottom panel, brass
  bevel, auto-sizing name plate, blinking ▼ arrow, POLLED
  attack/interact/ui_accept (a press mid-type reveals the line), a 140ms
  swallow window so the press that opens a conversation can't skip line one.
  Mixed-case text: lowercase glyphs shipped in `assets/_pixfont.py` (same
  5×7 cells, per-char BMFont yoffset carries x-height/descenders, lineHeight
  9→10; `draw_text` still uppercases, so art stamps stay caps).
- `scene/theater.gd/.tscn` — the cutscene kit: awaitable
  black/clear/card/say/converse/wait + actor helpers walk/face/hop (drive
  anything exposing an AnimatedSprite2D `sprite` with walk_/idle_ clips —
  PartyMember and NPC both do) + lock/unlock_party via the **"party"
  group**. GOTCHA: the kit must reference NO autoload identifiers — a
  `--script` probe that compile-time-references game classes loads the chain
  before autoloads register and poisons the Theater script for the whole run
  (found by the prologue probe 2026-07-12).
- `entities/npcs/npc.gd/.tscn` — interact-to-talk: solid StaticBody2D at the
  party feet convention, TalkZone polls E, conversation runs through the
  scene's Theater (the "theater" group), `talked` signal feeds wander-gate
  counting. Sheets are ONE 48px row [idle0, idle1, act0, act1, emote0,
  emote1] (villagers stop at 4 cols) and SpriteFrames build at RUNTIME — a
  new villager is a PNG + exports, no .tres authoring.
- `Game.flags` (set-once story booleans, process-lifetime) +
  `Party.set_roster()` (typed Array[StringName]; dynamic callers through
  `root.get_node("Party")` must pass a TYPED array or the call errors).

Adult flow underneath (unchanged): **bedroom ↔ downstairs ↔ Alembic Town ↔
overworld ↔ Whisker Meadow**.
The adult loop opens in the loft bedroom; its stairs descend to the downstairs
great room, whose front door opens into walkable Alembic Town just below the
cottage door; the town's south gate leads out to the overworld at the town
icon (and stepping on the icon's mouth lands back at the town's south gate).
Basil's home door in town travels down into the downstairs.

- **House** (`scene/house.tscn`, main scene): Basil's LOFT bedroom as a TILED
  room (the CT-bedroom treatment) — a SMALL dense diorama floating in a huge
  black void (the room is only 10 tiles wide on the 24×14 map, ~7-tile side
  margins; dormer window bay jutting above the cornice; every wall stretch
  occupied: cork | window | shelf), warm brown plank walls over a teal weave
  floor.
  `assets/_gen_tileset_house.py` reads the feature chars in
  `assets/maps/house.txt` (window, bookshelf, corkboard, bed, desk, chair,
  rug, railing) and AUTHORS a real tile library: 16-periodic fabric
  painters (weave/planks) whose repeated cells are byte-identical and so
  collapse to single atlas tiles, whole-tile light variants for the dawn
  window's hard-edged pool (lit core / ordered-dither fringe / shadow band —
  never per-pixel gradients), and furniture painted once inside its map
  footprint as crisp multi-tile objects (blazing gold dawn glass, hot-magenta
  quilt, research desk with oil lamp + microscope, corkboard with red string).
  Visible tiles and collision are both built at runtime from the same map
  file. **Scene lighting** (runtime, over the tiles): a violet-biased
  `CanvasModulate` dims the whole room (Basil included, the CT interior
  read) — darker while the curtains are drawn; `house_glow.png` — a
  hard-banded ADDITIVE beam the generator aims from the map's window cells
  over the pool — draws UNDER entities (additive light over a sprite lifts
  its darks and reads as transparency; sprites stay crisp, like CT). The
  **curtain mechanic** (`house.gd`): the room wakes with the curtains drawn
  (`house_curtains.png` closed/half frames, flasks redrawn in front of the
  drapes, a hot sliver of dawn leaking between the panels); standing at the
  window (WindowZone) and pressing **interact (E)** slides them open/closed,
  tweening the beam and the dim with it. The south boundary is a **CT
  staircase in the south-west corner**:
  Basil passes the rail gap (balustrade + newel posts on the upper tile
  layer, so he walks BEHIND them) onto visible treads that descend south out
  of the room silhouette between dark jambs, each step darker until the void
  swallows it — landing in the downstairs at `stair_arrival`.
- **Downstairs** (`scene/downstairs.tscn`): the ground-floor **kitchen + lab
  great room** — the steampunk-medieval genre statement in one room, and the
  hub between bed and world. Twice the loft's width (a 20-tile room on the
  same 24×14 map, ~2-tile void margins, one fixed screen), same authored-tile
  pipeline (`assets/_gen_tileset_downstairs.py`, slate flagstone floor +
  shared house planks). KITCHEN west: stone hearth with a live hard-banded
  fire (the room's hot light source — whole lit-flag tiles + additive
  `downstairs_glow.png` drawn under entities; the fire itself is an ANIMATED
  overlay, `downstairs_fire.png`, 3 frames stepped by `downstairs.gd` over
  the cold baked firebox), and the sink counter under the kitchen window
  with the dish shelf above. STEAMPUNK LAB east: flask shelf, a copper pipe
  manifold on the
  wall feeding the **free-standing boiler** — an animated y-sorted World
  entity (`downstairs_boiler.png`, 4 frames from
  `_interior_props.boiler_frames`: gauge-needle wiggle, firebox flicker, a
  lazy steam leak), its collision still the map's solid `A` cells, its node
  placed at the player's feet convention (feet = node.y + 20) so y-sort
  agrees — and a workbench with a half-built gizmo. The loft staircase descends through a top-center
  alcove jutting above the cornice (treads brighten as they come down out of
  the dark); the south wall holds the **front door** — an open doorway
  spilling daylight, lintel on the upper layer (Basil ducks under it), stone
  stoop into the void. Exits: up the alcove → bedroom (`stair_top`); out the
  door → Alembic Town just below the cottage door (`Game.town_spawn =
  "home"`). Spawns route through `Game.interior_spawn` (read-and-clear;
  default = `front_door`, the town-entry landing).
- **Overworld** (`overworld.tscn`): the CT/SoS TILED travel map (see "World
  Structure"). Two markers: the town icon's gate mouth (`town`, into the
  walkable town at its south gate) and Whisker Meadow (enters the combat
  zone). Cave and obelisk stay anchor-only landmarks in the terrain; their
  markers return with their zones.
- **Alembic Town, walkable** (`alembic_town.tscn`) — the Kakariko-style hub
  (see "World Structure" for the full composition): terrace Academy over the
  cliff-and-stair band, fountain square, the two shops + inn (announce-only
  facades), cottages, stream/bridge/pond, walk-behind trees; Basil's home
  door travels down to the downstairs; the south gate exits to the overworld.
- **Meadow — Whisker Meadow** (`scene/meadow.tscn`): 48×24-tile TILED zone on
  the shared overworld driver (forest treeline, sea pond + beach collar,
  road trail, boulder-prop outcrops + the trailhead cairn),
  4 slimes, beaker respawns, HUD; a south hedge-gap exit returns to the overworld
  at the meadow marker.

Feel: the bolt leaves the INSTANT the trigger is pulled (no wind-up — the shoot
anim starts on the muzzle frame), laser bolt (2 dmg; slimes have 4 HP → two
shots, and each kill respawns a slime elsewhere in the meadow), firing
**recoil-shoves**
Basil hard backward — the sheet's recoil frame leans him back, feet braced forward,
ears pinned, eyes squeezed in a wince, barrel kicked up; hop jumps straight up when
standing, leaps with held direction, and is **steerable mid-air** (SNES-Zelda style).

All art is **generated, frame-consistent pixel art** (see "Art pipeline") so animations
actually cycle; hand-drawn sheets can still drop in later against "Asset Specs" below.

### Slice file map

- `components/health_component.gd`, `hitbox_component.gd`, `hurtbox_component.gd`
- `entities/player/player.gd` + `player.tscn` (+ `player_frames.tres`)
- `entities/enemies/slime.gd` + `slime.tscn` (+ `slime_frames.tres`)
- `entities/projectiles/laser_bolt.gd/.tscn`, `muzzle_flash.gd/.tscn`
- `entities/pickups/beaker.gd` + `beaker.tscn`
- `scene/hud.gd/.tscn`
- `scene/house.gd/.tscn` — the playable bedroom: tiled-interior reference
  implementation (Tiles → Collision → y-sorted World), visible tiles from the
  generated layout + collision from `assets/maps/house.txt`, south-door exit
- `scene/meadow.gd/.tscn` — the combat zone; the tiled combat-zone reference
  implementation (Tiles → Collision → y-sorted World → TilesUpper)
- `scene/map_data.gd` (map-file loader — keep in sync with `assets/_maps.py`) ·
  `scene/painted_map.gd` (stamps the invisible collision tiles at runtime) ·
  `scene/tiled_map.gd` (stamps visible tiles from a generated layout file)
- `scene/overworld.gd/.tscn` (64×36 TILED continent: layout-stamped Tiles/
  TilesUpper + additive glow + the town/meadow markers) ·
  `scene/alembic_town.gd/.tscn` (56×34 TILED walkable town: same
  stamp-and-anchor pattern with the full-scale party, door/announce markers
  + the south exit) ·
  `scene/overworld_location.gd` (markers: id/display_name/target_scene/locked_text) ·
  `scene/game.gd` (autoload **Game** — remembers `overworld_spawn`, plus
  `town_spawn`/`interior_spawn`: the map anchor the next town/interior scene
  spawns at, read-and-cleared by the scene's `_ready` so "" = its default entry)
- `entities/player/overworld_player.gd/.tscn` (+ `overworld_basil_frames.tres`) —
  travel-only `CharacterBody2D`: 8-way move, 4-way facing, 90 px/s, no gun/hop/health
- `assets/font/pixel_font.fnt/.png` — bitmap font all Labels use
  (`assets/font/_gen_font.py`, glyphs shared via `assets/_pixfont.py`;
  caps + LOWERCASE since 2026-07-12 — UI chrome stays caps by convention,
  mixed case belongs to the dialog system)
- **Prologue A slice (2026-07-12):** `scene/prologue_open.gd/.tscn` (boot
  cards) · `scene/town_fest.gd/.tscn` + `assets/maps/town_fest.txt` (the
  festival town: cutscene, cast, wander gate) · `scene/meadow_fest.gd/.tscn`
  (Kitty, the whirligig quest, the montage hand-off) ·
  `scene/dialog_box.gd/.tscn` + `scene/theater.gd/.tscn` (the narrative
  kit) · `entities/npcs/npc.gd/.tscn` (interact-to-talk) ·
  `entities/kid/kid_basil.gd/.tscn/_frames.tres` (the playable kid) ·
  `assets/_gen_prologue_sprites.py` (cast sheets + `prologue_fx.png`) ·
  `assets/_gen_tileset_town_fest.py` (bright-era town tiles) ·
  `tools/prologue_probe.gd` (the chapter's end-to-end regression probe)

### Art pipeline (generated, frame-consistent, palette-locked)

The AI-generated sheets (`assets/basil.png`, `assets/basil_sheet.png`) draw a slightly
different cat in every frame, so animations strobe; they are kept only as concept
reference. The live art is drawn procedurally by stdlib-only Python scripts.

**One scene pipeline, one map format.** Every scene is TILED (the interiors —
the 2026-07 CT-bedroom pivot — then, with the 2026-07 town carve, the
OVERWORLD and walkable ALEMBIC TOWN, and since the 2026-07 meadow conversion,
WHISKER MEADOW too — the painted pipeline is retired, git history keeps it):
the generator composes the
scene from 16-periodic fabric functions (grass/forest carry a 32-periodic
phase on interior cells) + whole-tile variants + footprint-bounded prop
painters — and, on the overworld driver, neighbor-keyed autotile transitions
that are pure functions of (terrain, per-class 8-neighbor masks, local pixel),
including **45° corner cuts**: a cell whose neighbor mask is one orthogonal
pair renders that corner cut along the tile diagonal, each boundary painted
one-sidedly by its OWNER class (water > waste > beach > road > forest >
mountain), so 1-cell stair-steps in the map txt chain into continuous
diagonal coasts, rims and ridge edges — so repeated cells are byte-identical
BY CONSTRUCTION and the slicer collapses them to a small atlas, exactly how
an SNES scene lives in VRAM (house: 60 tiles from 336 cells; overworld: ~260
from 2304; town: ~470 from 1904; meadow: ~145 from 1152). Every scene is
driven by its `assets/maps/*.txt` file.

- **`assets/maps/*.txt`** — the shared source of truth per map: a `legend`
  (char → terrain + walk/solid), named `anchor`s (spawns, exits), and the ASCII
  tile grid. Python paints from it; `scene/map_data.gd` builds collision and
  logic queries from the same file, so paint and physics cannot drift. Keep
  `assets/_maps.py` and `scene/map_data.gd` parsers in sync.
- **`assets/_core.py`** — canonical scale constants (`ZONE_TILE=16`,
  `ZONE_CELL=48`, `ZONE_FEET=44`, `OW_CELL=24`, `ICON=32` — the Scale Table above
  mirrors these), `h2()` deterministic hash noise, `pick()` ramp dither, `Img`
  canvas, PNG writer.
- **`assets/_palette.py`** — the color script as data. `ramp(seed, shadow, tones)`
  derives N-tone material ramps (6 for terrain, 4 for sprites) from scene
  seeds, hue-shifting the dark end toward the scene's shadow bias (violet or
  teal). `SCENES` is the palette registry (below) — per-scene `"ramps"` entries
  hold hand-tuned identity ramps for materials that can't be derived (warm dirt:
  teal shadows turn it yellow-green, violet ones salmon); `ACTORS` holds the
  hand-tuned identity ramps for Basil / Schweinler / slime.
- **`assets/_tiles.py`** — the tileset kit: `slice_atlas()` cuts full-room
  compositions on the 16px grid and dedupes identical cells into ONE shared
  atlas across TWO layers — a lower canvas (under entities) and a sparse
  upper canvas (over entities: railings, furniture tops, lintels — anything a
  body walks behind). Writers emit the packed atlas PNG, the TileSet `.tres`
  (visuals only — collision stays on the invisible collision layer) and the
  layered layout txt that `scene/tiled_map.gd` stamps at runtime.
  **The tiled READ is a discipline, not a file format:** repeating art must be
  a function of tile-local coordinates + a per-cell variant hash, and light/
  shade must be quantized PER TILE (whole lit tiles + ordered-dither fringe
  tiles, per-tile vignette/halo bands) — per-pixel gradients make every tile
  unique and dissolve the tile rhythm into a painting.
- **`assets/_tilekit.py`** — the shared base of every TILED scene:
  int-casting `Canvas`, the shared material ramps (one hardware store:
  TIMBER/BRASS/COPPER/STONER/...), and `TileScene` — map + LOWER/UPPER
  canvases + palette wiring, `bbox`/`px` footprint geometry,
  `place`/`place_upper`/`place_split`/`place_each` prop placement with baked
  contact shadows, `write_glow`, and `finish()` (the slice/dedupe/write).
  `Room` (interiors) and `OverWorld` (the continent) both subclass it.
- **`assets/_interior.py` + `assets/_interior_props.py`** — the interior kit,
  THE standard for every future interior room. `_interior.py` owns the
  interior skeleton (the 16-periodic terrain fabrics: `plank_px` walls with
  wainscot base row, `weave_px` / `flag_px` floors, per-cell painters with
  whole-tile light dispatch, stair/jamb/rail/drop/south cells, and the `Room`
  driver: `paint_terrain(rules)`, `place(char, prop, shadow_h)`).
  `_interior_props.py` is the furniture library — every prop a function
  returning a `_sprites.py` Sprite (jitter=0 hard CT bands;
  `ball`/`capsule`/`tri` volumes on round forms; outline/crease/specular
  finishing), blitted at its map footprint with a baked contact-shadow band.
  Windows and rugs are size-parameterized and shared across rooms. A NEW
  ROOM = a map txt + a ~100-line config (`assets/_gen_tileset_house.py` /
  `_gen_tileset_downstairs.py` are the two references) — pick the scene
  palette, declare light pools + odd cells, place props, `finish()`.
- **`assets/_overworld_tiles.py` + `assets/_overworld_props.py`** — the
  overworld kit: the CT autotile look on the same bake→slice→dedupe path.
  `OverWorld(TileScene)` owns the terrain fabrics (sea/grass/hills/flowers/
  beach/forest-crowns/mountain-ridges/waste/road/bridge) and
  the neighbor-stamp transitions — every cell's art is a PURE function of
  (terrain class, per-class 8-neighbor masks via `edge_dist`, coast-distance
  band) + tile-local pixels, so coasts/foam, riverbanks, cliff faces,
  snowcapped back crests, crown-arc forest silhouettes and road shoulders
  all collapse into autotile families (the terrain painter sends nothing
  to the UPPER layer — no terrain pixel ever covers the chibi). Hash variants (sea sparkle, tufts, waste crystals/dead trees,
  crest snow, cave nicks) are allowed ONLY on family-interior cells (and
  never under a landmark's footprint) — the dedupe contract. Fabric texture
  rides two tile-local primitives (`_dither_i`/`_grain_dither`, the
  cluster-jittered Sprite.tone formula standalone, and `_hatch`, an ordered
  engraved-linework predicate — both keyed on tile-local/32-space coords
  ONLY, never absolute position): sparse turf clumps + broad warm-green
  drift patches (the second `grass2` ramp, dithered in at matched value —
  CT's two-green field) under the grass, painter-sorted scalloped crown
  ROWS in the forest (south crowns overlap north ones; lit caps, near-black
  under-rims — stacked canopy, not bubble wrap; lobe GEOMETRY is
  16-periodic, because edge cells render phase 0 and a 32-periodic lattice
  would chop lobes at every transition seam), the SAME lobe lattice shaded
  as stylized PEAKS on the mountains (`_rock_px`: hard two-face split —
  sunlit west, strata-hatched shadow east — under a bright ridge crest;
  snowy cells whiten the summit arcs), 2-tone `_lip_band` grades at every
  water/waste boundary, a creeping grass fringe on the beach seam. Forest
  AND mountain rims ride one mechanism (`_arc_cell`): a lobe instance is
  rejected if its disc would cross any open boundary, the surviving edge
  lobes' arcs form the outline, a 1px near-black ring seals it, and the
  bays render the neighbor's fabric — the silhouette follows the lobes,
  never the tile grid; narrow runs fall back to small strip lobes, and
  nothing goes to the upper layer. Mountains front the forest too
  (MOUNT_OWN), so canopy flows into the massif's bays.
  `_overworld_props.py` is the LANDMARK library — one-off compositions,
  never deduped, so they use full per-pixel `Sprite` shading (`tone()`
  lambert roofs/cylindrical towers via `_hip_roof`/`_coursed_wall`,
  `_hatch_px` shingle/strata linework on ABSOLUTE pixels — kept deliberately
  separate from the terrain `_hatch` — chimney cast shadows, window reveals
  + sky-catch streaks, `despeckle`+`cluster_shade` finishing): `town_cluster`
  (the 128×96 icon: dense mini-cottage ranks with dab openings, the Academy
  keep, `_boiler_house` steamworks + `_steam` plumes, well/awning, the gate),
  `castle` (a ~46×54 hold centered in the 96×80 footprint, nestled into
  the massif — pale STONER walls, slim towers, keep cone, tiny lit gate,
  steaming flue; elements stay SMALL so it reads distant, never a
  walk-up building scaled up),
  `mountain_peak` (80×64: the Horn — three shaded facets, snowcap with
  wind-torn fingers, crevasses), `giant_tree` (64×96: the Elder Tree —
  ball-lobed crown with seam shadows, bark-grooved trunk, root flare,
  surviving blooms), `obelisk` (48×64 faceted CRYSTAL obelisk — lit/deep
  facets on the CRYS ramp, rune score, crystal burst + floating shard),
  and `crystal_outcrop` (32×32 shard cluster, one per 2×2
  `K` block). Walkable-town facades live at zone scale in
  `assets/_town_props.py` (`town_home`, `town_cottage`, `town_academy`,
  `town_well`, `town_lamp`, `town_stall`); the meadow's per-cell boulder
  domes + trailhead cairn in `assets/_meadow_props.py`; the shared drawing
  primitives (`S`, `ln`, `edge`) live in `assets/_propkit.py`.
  A new overworld = the map txt + `assets/_gen_tileset_overworld.py`'s
  ~90-line config.
- **Godot side:** a scene is `Tiles` (TileMapLayer, under entities) →
  `Collision` (invisible TileMapLayer, `assets/collision_tileset.tres` — one
  transparent full-square physics tile stamped on every solid cell by
  `scene/painted_map.gd`) → entities → `TilesUpper` (TileMapLayer, OVER
  entities — the walk-behind layer), the visible layers stamped by
  `scene/tiled_map.gd` from the generated
  layout's `layer lower` / `layer upper` sections (interiors and combat zones
  put a y-sorted `World` between; the overworld's lone chibi needs none).
  Entity/exit positions come from map anchors where practical.
  `scene/house.tscn` is the tiled
  interior reference; `scene/overworld.tscn` the tiled exterior reference;
  `scene/meadow.tscn` the tiled combat-zone reference.
- **Z-order / layering doctrine (2026-07-11, lint-enforced).** Draw order is
  the fixed sandwich above — lower tiles always under every body, upper
  tiles always over, only `World` children y-sort against each other. There
  is NO per-tile depth (per-tile `y_sort_origin` was rejected: the dedupe
  atlas shares tiles between props at different heights). Every piece of art
  therefore belongs to one of THREE TIERS, chosen by one question — *can a
  body stand directly south of it and overlap it?*
  1. **Tier 1 — baked lower**: terrain, flat props, and wall-flush furniture
	 (a body can never get north of it, so always-under is always right).
  2. **Tier 2 — static split** (`place_split`: roof/canopy/lintel rows on
	 the upper canvas, base rows + contact shadow on the lower): tall props
	 whose over-art sits ONLY above solid cells or door cells. The top row
	 of every walk-behind corridor is a solid **`ridge`** cell (map digits,
	 all legend-named `ridge`, never a struct — a struct's shade band
	 peeks through the silhouette): a 33px body over 16px tiles covers its
	 feet row + the row above + ~5px more, so a ridge-capped corridor shows
	 at most a head-peek over the roofline (the CT "behind the house" read)
	 and never a full body "standing on the roof". The cap is SCALE-GATED:
	 a chibi map's figure (the overworld's 24x24 travel chibi, ~16px) fits
	 inside one tile and can't out-peek a silhouette, so covered walk-behind
	 cells there need no ridge cap — a whole crown may be open walk-behind
	 (`CHIBI_MAPS` in `_check_art.py` waives the cap lint; the Elder Tree's
	 entire crown is walkable `G` cells since 2026-07-11, only its trunk
	 blocks).
  3. **Tier 3 — y-sorted `World` entity**: free-standing props a body can
	 round (furniture, street lamps/well/stall/fountain, the animated
	 boiler). NEVER baked: the generator calls `TileScene.emit_prop()`
	 (PNG + a row in generated `tilesets/<scene>_props.txt`; `each` splits
	 one char into per-component sprites) and `scene/prop_spawner.gd`
	 spawns them into `World` — node origin on the feet line
	 (`base_y - 20`, matching `ZONE_FEET=44` in the 48px cell), art bottom
	 on the footprint's south edge (or `anchor=top:<px>` for crops like the
	 bed cover, `base_inset=<px>` to lift the baseline off a baked shadow).
	 Collision stays on the map's solid cells — spawned props are visual
	 only, and the spawner front-loads them in child order so bodies win
	 y-sort ties. **Counter-walk variant** (desk / table / workbench): a
	 counter-height Tier-3 prop makes its TOP footprint row `walk` and only
	 its bottom row `solid`, so a body steps onto the top row and tucks in
	 behind the y-sorted tabletop, legs hidden — the SoM shop-counter read.
	 **Runtime FX are Tier 3 too** (`scene/world_fx.gd`, 2026-07-12): a
	 sprite spawned by a script (paw prints, the squelch bag, puddle
	 splashes, quest-part icons, ribbons, sleeping Zs) joins `$World`, never
	 the scene root (a root child draws over the whole world; the old
	 `z_index=-1` paw-print hack buried them UNDER the floor tiles).
	 `WorldFx.decal()` is for GROUND art that must lose y-sort to EVERY
	 body that can overlap it: origin `DECAL_BIAS`=32px north of the visual
	 center (art offset south) AND `move_child(0)` so it also loses exact
	 ties to the front-loaded props. The bias arithmetic: bodies key at
	 feet−20, and the northmost overlapping body (feet on the decal's top
	 edge, center−8) keys at center−28 — a bias ≤28 lets a body standing ON
	 the decal render UNDER it (the original 8px draft did exactly that).
	 `WorldFx.airborne()` is for FLOATING art: origin ground-anchored on the
	 point it hovers over, art lifted by sprite `offset` only (the
	 theater.hop move-the-sprite rule), so world depth sorts by the ground
	 beneath — and bob/float tweens must animate `offset`, never `position`.
  **The mask band (pressed-body rule).** The collision box hugs the FEET,
  so a body pressed against a solid row sinks ~10px of sprite past the
  boundary in EITHER direction: pressed from the north, its feet + shadow
  leak ~14px over the lower-layer art of the row below (facade top);
  pressed from the south, its HEAD sinks ~10px into a solid row's top.
  `_town_props._eave_lift(lo, up, w, fy)` mirrors a solid row's top 12px
  onto the UPPER canvas (pixel-identical composite) to swallow the corridor
  sliver — legal ONLY when the nearest south-side walkable row is ≥2 rows
  below the band row, so no south head can reach it (buildings' 2-row
  facades, the elder tree's 3-row trunk block). NEVER band a 1-row-deep
  solid strip between two walkable rows — the corridor feet and the south
  head need the same 12px and one of them always wears it (this killed the
  town-tree corridor, below). The band is the only legal upper art on a
  body-adjacent solid row, and why the lint's support rule accepts upper
  cells that are themselves solid. **The SIDE band** (2026-07-12, the
  "standing on the roof corner" fix): a body pressed against a building's
  west/east face overlaps the wall edge at EVERY height, so
  `_eave_lift(..., h=h)` also mirrors the facade's outer 6px columns from
  the eave down to the footing — the pressed sliver is swallowed by the
  silhouette instead of painting over the plaster and roof-eave corner.
  Every town building carries both bands (the Academy keep was authored
  before the rule and gained them 2026-07-12).
  **The small-prop rule.** A walk-behind corridor needs ~2 covered rows
  above the corridor row AND a ≥2-row solid base below it. Props smaller
  than that (the 2x3 town trees: 2-row crown, 1-row trunk) get NO corridor
  — every cell solid, the ALttP small-tree standard. Their crown still
  rides the upper layer so a body passing east/west tucks its inner
  shoulder behind the silhouette, and a south-pressed body correctly draws
  over the trunk row's lower-layer art.
  **The silhouette-fit rule.** Solid must READ solid: a round prop over a
  square footprint leaves corner cells the art barely touches — a solid
  corner cell with no visible art is an invisible wall (hit on the elder
  tree's crown-top corners 2026-07-11). Shape the map chars to the
  silhouette (the elder's top canopy row is `.GG.`) and clip the prop's
  stray corner pixels one px past the cell boundary BEFORE `edge()` (the
  4-way outline dilates one pixel and must not spill into the walkable
  cell — the head-clearance lint catches spills). The collision box must
  also be FEET-ALIGNED like the zone bodies' — the overworld chibi's box
  was 3px below its `OW_FEET` baseline, which added a phantom margin to
  every south press (fixed 2026-07-11: `CollisionShape2D` at (0, -3) in
  both overworld_*.tscn bodies). The landmark footprints were audited
  2026-07-11: every art-free solid cell a body could press (town-icon
  spire gaps, the massif's east tip, the obelisk's NW corner, the elder
  trunk's bare west flank, the town's home/inn ridge corners) was retyped
  walkable, the town garden hedge spur became a fence run (a 1-cell-thick
  forest line can't terminate — the lobe lattice always rejects the tip
  cell into a grass bay), and the invisible-wall lint below keeps the
  class extinct. **Extended through Tier-3 footprints 2026-07-12:** the
  lint's Tier-3 exemption is now per CELL — a footprint cell keeps its
  solid map cell only where the prop's frame-0 art covers ≥20% of its
  16px square (measured floor: legit bases 25-46%, true walls 0%; the
  lint decodes the manifest PNGs and mirrors prop_spawner's placement
  math). Art-free cells are retyped to WALKABLE TWINS with the same
  terrain name so the paint stays byte-identical and only collision
  changes: `O`/`U`/`L` beside `o`/`u`/`l` in the town maps (the fountain's
  transparent top corners were the one true invisible wall; lamp heads
  and the well roof became walk-behinds — the twin chars stay in the
  manifest charsets so `bbox`/`each` grouping is unchanged), `l` beside
  `L` for the hall lectern's corners. One walk-behind was REVERTED to
  solid on gameplay grounds: the inn-nook lamp top at (43,24) opened a
  1-cell pocket inside the goose-chase leash and the fleeing goose
  wedged there (the catch loop stalled — walkable pockets next to chase
  AI are a trap; the town glow finder keys on lamp-component TOPS in
  either char, so the revert cost no pixels).
  `assets/_check_art.py` enforces the doctrine: upper art must rest on
  solid/upper/door cells or itself be a solid-cell mask band (no floating
  over walkable ground), walkable
  covered cells must have covered art due north (corridors capped —
  waived on `CHIBI_MAPS`),
  `ridge` cells must sit under upper art, the four upper layers must be
  non-empty, every props manifest must parse against its map and PNGs,
  and NO pressable solid cell may render as open ground (the
  invisible-wall lint: a solid cell 4-adjacent to walkable whose lower
  tile dedupes to one used on walkable ground, with no upper art, fails
  the build; Tier-3 manifest chars are exempt — their solid cells
  legitimately sit under y-sorted sprites).
  Generator-side, `place_upper` asserts a non-empty upper sprite (no dead
  splits).
- **`assets/_sprites.py`** — the sprite construction kit: `Sprite` canvas with
  steer-lit `ball`/`capsule`/`panel` volumes, cluster-jittered tone selection,
  `cluster_shade`/`despeckle`/`outline`/`crease` finishing passes, and `Rig`
  (named anchors + per-frame offsets so cycles animate as one body).
  Generators (re-run any with `python3 <script>`; then let Godot reimport, or
  `godot --headless --path . --import`; **always run `python3 assets/_check_art.py`
  after regenerating** — it asserts map enclosure/anchors, layout/atlas/.tres
  agreement, the z-order doctrine (upper-art support, capped walk-behind
  corridors, ridge placement, non-empty upper layers, props manifests),
  collision tileset shape, entity placements on walkable
  cells, sheet dims and `.tres` regions):

- `assets/_gen_collision.py` → `collision_tile.png` (16×16 transparent) for the
  shared collision tileset.

Tiled scenes (atlas + `.tres` + layout from `assets/maps/*.txt`):

- `assets/_gen_tileset_overworld.py` → `tilesets/overworld_tiles.png/.tres` +
  `overworld_layout.txt` + `overworld_glow.png`
  (64×36 map → ~575 unique tiles): the CT/FF6 continent as real tiles —
  shallow→deep sea with foam-arc autotile coasts and layered swells, sand
  with wet lips and a creeping grass fringe, canopy-crown forests
  (crown-arc silhouette rims, dark outline ring), peak-lobe massifs
  (lit/shadow faces, scalloped snow crests on north rims), river +
  rosewood bridge with
  rails, crack-web violet wastes with crystal / dead-tree variant tiles,
  the dirt trail (gentle edge-keyed wobble), and the landmark compositions:
  the Alembic Town cluster icon (dense roofs, Academy keep, steamworks
  plume), the Capital's castle + the Horn summit on the massif, the Elder
  Tree on the river plain, the wastes' obelisk monument + crystal outcrops
  (grass variants: tufts, boulders, mossy sinks, wild blooms). The glow PNG
  is the additive night-lights overlay (cottage candlelight, the rose
  window, firebox coals, the boiler gauge, castle windows + gate lamps,
  obelisk + outcrop + shard crystals). (If a darkening overlay ever comes
  back: Godot's canvas MUL blend darkens through transparent texels on
  Compatibility — use plain MIX alpha blending.) ~2s.
- `assets/_gen_tileset_meadow.py` → `tilesets/meadow_tiles.png/.tres` +
  `meadow_layout.txt` (48×24 map → ~145 unique tiles): Whisker Meadow as real
  tiles on the same driver — teal-indigo treeline border (crown-arc rims),
  the cyan pond with foam coasts + a wet-sand beach collar on its
  trail-facing shore, the wobbly dirt trail from the south gap to the
  flower-ringed trailhead cairn, per-cell squat boulder domes
  (`assets/_meadow_props.py`, three salted variants on the solid `r` cells —
  the `boulder` terrain renders grass underlay + a south contact band),
  hot-pink flower drifts; no glow overlay (daylight scene). ~2s.
- `assets/_gen_tileset_house.py`, `assets/_gen_tileset_downstairs.py` — the
  interiors (see the interior kit above).

Sprites and fx (on `_sprites.py`; sheet layouts frozen against the `.tres` files):

- `assets/_gen_basil_sprites.py` → `basil_gen.png` (288×384, 48×48, 6×8): Basil —
  jet-black tuxedo, stern yellow eyes (sweet ^ ^ blink), white blaze/muzzle/paws,
  close-set ears, big rimmed aviator goggles (amber glass) up on the forehead,
  lab coat worn LONG (hem y=35, flat CT bands — paw stubs peek under it, so the
  walk reads CT-Lucca style), laser gun. CT-Frog proportions (big head); walk/
  shoot ×3 facings (up-shot holds the gun skyward past his head, muzzle on the
  16px contract), hurt ×2, blink, tail-flick, happy, sad + a 4-frame reload
  (beaker of glow-juice poured into the gun's port — plays on reload: R/L or
  a dry trigger; beakers are carried as spare mags).
- `assets/_gen_slime_sprites.py` → `slime_gen.png` (144×96, 24×24, 6×4):
  squash-stretch bounce with conserved volume and a lagging gel nucleus
  (airborne frames 2–4 — `slime.gd` syncs speed to them) + 4-frame splat death.
- `assets/_gen_overworld_actors.py` → `overworld_basil.png` (96×72, 24×24,
  4×3 chibi) + `overworld_icons.png` (160×32, five 32×32 landmark vignettes).
- `assets/_gen_fx.py` → `placeholder/`: ruby hearts 48×16, energy pips 16×8,
  laser bolt 26×8, muzzle flash 20×20, glass beaker 12×14, violet hop
  shadow 24×10.

Tiled interiors (atlas + TileSet + layout from `assets/maps/*.txt`):

- `assets/_gen_tileset_house.py` → `tilesets/house_tiles.png/.tres` +
  `tilesets/house_layout.txt`: the loft bedroom as an AUTHORED tile library —
  16-periodic fabric (warm brown plank walls, low-contrast teal basket-weave
  floor) that dedupes to single atlas tiles; whole-tile light variants (lit
  weave / dither fringe / shadow band) for the dawn window's hard pool;
  hash-placed whole-tile variety (worn floor cell, knotted plank cell — one
  atlas tile each); and furniture as footprint-bounded multi-tile objects
  (dormer gable + brass vent over the blazing quantized-dawn window with sun
  disc, skyline and flask-lined sill; corkboard obsession wall with red
  string; bookshelf with scroll + glow jar; bed with hot-magenta quilt; desk
  with oil lamp, microscope + book stack — a WALK-BEHIND piece: the desk is a
  **y-sorted World entity** (`house_desk.png`) on a one-row solid footprint
  with a 2-row walkway behind it — behind it your legs hide under the desktop
  plane, in front you draw over it. (The static upper-TILE-layer trick is
  reserved for room-edge art like the rail/lintel: a 2-tile-tall body
  standing directly south clips its head behind static-over furniture —
  y-sort is unconditionally correct.) Chair; rug beside the bed; the BED is
  split for the FF/CT under-the-covers read (`_interior_props.bed_parts`):
  headboard/pillow bake under entities, the quilt+footboard cover is a
  y-sorted entity (`house_bed_cover.png`) — walk onto the bed's middle row
  and Basil slides under the quilt with only his head showing on the pillow;
  stand south of the bed and he draws over the covers. Railed
  stairwell south whose balustrade rides the upper layer over steps sinking
  into dark). Every prop carries dark contact edges, 3-tone banding and
  single-pixel speculars; contact shadows are baked inside each footprint.
  Feature positions come from the map's feature chars — move the window in
  `maps/house.txt` and it moves in-game.
- `assets/_gen_tileset_downstairs.py` → `tilesets/downstairs_tiles.png/.tres` +
  `tilesets/downstairs_layout.txt` + `downstairs_glow.png`: the ground-floor
  great room on the same disciplines — slate flagstone fabric (16x8 running
  bond), shared house planks, whole-tile hearth light (lit flags + dither
  fringe + the additive glow overlay), and the furniture objects (stone
  hearth with hard-banded fire, sink counter + dish shelf, flask shelf,
  wall pipe manifold + the free-standing animated boiler, workbench with
  half-built gizmo, alcove stair treads, open front doorway whose lintel
  rides the
  upper layer).
- `assets/font/_gen_font.py` → the BMFont all Labels use: the **native 5×7
  glyphs** from `assets/_pixfont.py` (caps/digits/punctuation) at size=8 —
  Labels use `font_size = 8`. UI text is uppercase; a lowercase set returns
  with the dialog system.
- Screenshot check: `Godot --path . --script tools/shot.gd --
res://scene/meadow.tscn /tmp/shot.png` (windowed; headless renders black).

Render style (CT-chunk): every form is a shaded volume — material ramps whose
shadows hue-shift cool, light from the upper-left. Sprites: 4-tone ramps with
**hard, flat band edges** (Sprite jitter=0 — no dither inside characters),
superellipse silhouettes, per-material 1px outlines, details that break the
silhouette (whiskers, drawn after the outline). Painted terrain: 6-tone ramps,
cluster-jittered tone quantization (organic 2px clumps, never checkerboard
fields), scene-wide light gradient + cloud shade, contact shadows grounding every
mass, and no texture element repeating on any visible 16px rhythm. Night scenes
tint through a violet-magenta `CanvasModulate` over the one daytime painting —
a single tint mechanism, never a night repaint.

### Palette Registry (the color script — `assets/_palette.py` SCENES)

Every scene keys into this table; new materials derive via
`ramp4(seed, SCENES[key]["shadow"])`. Keep every palette MINIMAL and surreal —
a duo/tri-tone cast per scene. Wood may be an honest warm brown (a material,
not the field); never a naturalistic beige/gray mud FIELD, and never
un-hue-shifted muddy darks — if a dark wants to be gray, it's lavender.
(`bedroom`, `downstairs`, `overworld`, `town`, `town_fest`, and `meadow` are
in the current build; the other rows are the standing color script for scenes
to come.)

| Scene key      | Dominant field                          | Hot accent                    | Shadow bias |
| -------------- | --------------------------------------- | ----------------------------- | ----------- |
| `title`        | indigo→magenta→gold posterized sunset   | leaf gold                     | violet      |
| `night_yard`   | periwinkle-violet night                 | amber lantern glow            | violet      |
| `bedroom`      | warm brown plank walls / teal weave floor | hot-magenta quilt, peach dawn | violet      |
| `downstairs`   | shared house timber / slate flag floor  | amber hearth fire, daylight door | violet   |
| `morning_yard` | peach plaster                           | magenta shingles, pink blooms | violet      |
| `road`         | minty teal + peach path                 | hot pink flowers              | teal        |
| `hall`         | plum panelling / rose floor             | chalk-mint board writing      | violet      |
| `overworld`    | deep ocean teal + mossy emerald land    | violet wastes + crystal       | teal        |
| `town`         | mossy lanes / dusky lavender plaster (drained era) | candle amber       | teal        |
| `town_fest`    | spring grass / cream plaster (festival era — Prologue A) | festival magenta + living mint glow | teal |
| `meadow`       | minty teal greens (mossy 2026-07 register) | candy hot-pink flowers     | teal        |

## Asset Specs (sprite sheets to provide)

All PNG, transparent background, **0 padding/margin between cells**, nearest-neighbor
(no anti-aliased edges). Grid is **16×16**. Style target: **Chrono Trigger's Frog
sheet** — big flat color regions, hard band edges, 1px outlines, every pixel
deliberate.

1. **Player — Professor Poopy Paws** _(highest priority)_ — **48×48 px** cells, **6
   columns**, one direction/action per row to match `player_frames.tres`:
   Walk Down (6) · Walk Up (6) · Walk Side (6, mirrored in code) · Shoot Down (4) ·
   Shoot Up (4) · Shoot Side (4) · Hurt (2) + idle-down blink + idle-side tail-flick
   - happy + sad · Reload (4, beaker pour). Full sheet **288×384**. Figure ~33 px
	 tall, feet baseline y=44, gun muzzle 16 px from cell center. The cat holds a
	 **laser gun** in the shoot rows (weapon-agnostic rows welcome — see "Future
	 Direction"). Use `assets/_gen_basil_sprites.py` (current art) as the layout
	 reference.
2. **Fuji — the librarian cat** _(current playable)_ — **48×48 px** cells, **6
   columns × 10 rows**, sheet **288×480**, matching `entities/fuji/fuji_frames.tres`:
   Walk Down/Up/Side (6 each) · Book Down/Up/Side (6 each: windup, peak, strike,
   IMPACT held, follow, recover-redraws-walk-f0) · Dart Down/Up/Side (4 each:
   raise, aim, PUFF, settle; cols 4-5 empty) · Hurt (2) + blink + tail-flick +
   happy + sad. Same figure/feet contracts as Basil, but her blow-pipe TIP
   sits at **19px** from cell center (`fuji.gd muzzle_offset` — the reed runs
   longer than Basil's 16px gun muzzle). Tortoiseshell —
   split ears (left black / right ginger), placed rust patches (never dithered),
   cream muzzle/chest/paws, green-gold eyes in round brass reading glasses, plum
   scholar's robe (mustard trim placket + hem stripe, hood on the back view),
   tome hugged to her chest in the walk. `assets/_gen_fuji_sprites.py`.
3. **Slime / first enemy** — **24×24 px** cells. Walk Down/Up/Side (6 each, side
   mirrored) + 4-frame death. Sheet **144×96** (matches `slime_frames.tres`).
4. **HUD hearts** — **16×16** heart, 3 frames in a horizontal strip:
   full | half | empty → **48×16**. Ammo pips: **8×8** ×2 → **16×8**.
5. **Overworld travel chibis** — **24×24** cells, 4×3 sheet **96×72** each:
   walk down / up / side ×4 (side right-facing, flipped in code), feet y=21.
   Basil (tuxedo, goggles, lab coat — `overworld_basil_frames.tres`) and Fuji
   (split tortie ears, spectacle glints, plum robe — `overworld_fuji_frames.tres`),
   both from `assets/_gen_overworld_actors.py`.
6. **Overworld landmark icons** — five **32×32** icons in a strip → **160×32**:
   HOME cottage, TOWN, MEADOW grove, CAVE mouth, OBELISK.

(Every scene's terrain is a generated tileset — see "Art pipeline".
Hand-drawn tiles would replace a
generated `tilesets/<name>_tiles.png` atlas in place. The landmark-icon strip
is now only used for the meadow marker — drawn buildings replaced the rest.)

> Prefer a different layout (e.g. Aseprite export with tags)? Send it plus the frame
> tags and the slice will be re-sliced to match. The dimensions above are the defaults
> the code assumes (and what `assets/_check_art.py` asserts).

## Future Direction — Combat & Party (recorded 2026-07, not yet in scope)

The target feel is **Secret of Mana, but snappier**: real-time top-down action that
stays friendly, with crisp fire/recover cadence, hit-pause, and readable knockback.

- **Weapon variety** — the laser gun is the first of several blaster-type weapons;
  each should differ in arc/range/rate/knockback the way SoM's weapon families did.
  The 48×48 cells and 4-frame shoot rows are sized so alternate weapons swap into
  the same animation contract (`shoot_down/up/side` + `muzzle_offset`).
- ~~**3-person party**~~ — **2-member slice BUILT (2026-07-10), SoM-style.**
  Basil is back as the default leader; **Fuji** (the librarian cat who pulls
  Basil back into the world) runs as the AI companion — and **Q/Tab swaps the
  lead** (camera + control hand off, the AI takes the other body). The
  architecture is roster-based, so the third sympathizer is additive:
  - `entities/party/party_member.gd` — `PartyMember` base (extends
	`DirectionalBody2D`): shared 8-way move, hop, knockback/hurt, can't-die
	refill. Each physics frame it fills an `Intent` (move/face vectors +
	attack/secondary/jump edges) from the keyboard when leading or from its
	`Brain` child when following — one movement/attack code path for both.
	Kits (Basil's gun states, Fuji's book/dart states) live in the subclasses
	behind `_process_kit` / `_on_attack_intent` / `_on_secondary_intent`.
  - `entities/party/ai_brain.gd` — `AIBrain` (a plain `Brain` node in each
	member scene), a three-mood machine: FOLLOW with hysteresis (stop 34px /
	resume 44px), catch-up sprint past 56px; ENGAGE acquires the nearest
	`enemies`-group node within 70px while ≤96px of the leader, then LATCHES
	the target and holds it to 140px (acquire/hold split — Basil's ~30px
	recoil skid crosses any single line every shot); RETURN once the leash
	breaks past 128px — run home to 48px ignoring enemies before re-engaging.
	Every boundary is a two-threshold band; single-threshold edges read as
	frame twitching (2026-07-10 fix). Attack cooldowns decay in the brain's
	own `_physics_process` (think() pauses during the member's kit/hurt
	states); brains reset on leader swap. The catch-up teleport fires only
	past 130px (kept ≤ the smallest view half-extent + margin so an
	off-screen-stuck follower always qualifies) AND off-screen (live camera
	check), landing a step behind the leader after a `test_move` sweep proves
	the step walkable (else on the leader) — never a visible pop, never an
	embed. `tools/party_probe.gd` is the behavioral regression probe (mood
	transitions, in-view pops, settle distances). Kit brains:
	`fuji_brain.gd` (close to swing range, tome slam), `basil_brain.gd`
	(sidle the shorter axis onto a cardinal — 4-way facing — fire in
	[36, 110]px, recoil kites him out, reload when dry, passive when out of
	beakers too; he restocks by walking over beaker pickups).
  - `scene/party.gd` — the `Party` autoload: roster `[basil, fuji]`,
	`leader_id` persists across scenes (HP does not, same as before),
	`spawn(world, pos)` replaces per-scene player instances, `place()`,
	`clamp_cameras()`, swap on `swap_member` (polled). Leadership = three
	things it applies together: `is_leader` on the body, sole membership of
	the **`player` group** (all door/exit/zone triggers still gate on it,
	untouched), and the live child `Camera2D` (`make_current` +
	`reset_smoothing` on swap). All members sit in the **`party` group**;
	slimes re-pick the nearest party member every frame and join/leave the
	**`enemies` group** for brain targeting.
  - HUD stacks one heart row per member (roster order, follower dimmed to
	55%); Basil's ammo pips/mags bind to him whether he leads or follows.
	The overworld stays ONE chibi — the leader's (frames swap on entry).
  Fuji's build notes (2026-07-07, look/feel dialed as solo playable):
  tortoiseshell (real-Fuji faithful: warm-black fur, placed rust patches,
  cream chin/chest/paws, green-gold eyes), round brass reading glasses, deep
  plum scholar's robe with mustard trim, hugging her clasped tome as she
  walks. Kit: **tome swing** (attack — two-paw overhead slam, BookHitbox
  opens through the strike/impact window, forward lunge) + **blow-pipe
  darts** (`dart` action, L — unlimited, the planted pose is the cost; dart
  leaves on the puff frame at the pipe-tip contract) + Basil's hop-dodge.
  `entities/fuji/` (fuji.gd/.tscn/frames), `entities/projectiles/blow_dart.*`,
  `assets/_gen_fuji_sprites.py` → `fuji_gen.png` (288×480, 6×10), chibi
  `overworld_fuji.png` in `_gen_overworld_actors.py`, `FUJI` palette dict.
  Remaining party ideas for later: member 3, real KO/downed state (both
  members currently refill on death), per-member AI stance settings
  (aggressive/defensive), SoM ring-menu flavor for swapping.
- **Magic returns late** — spell systems unlock as the story restores magic; the
  drained world is why early combat is all blasters.
- ~~**The downstairs**~~ — **BUILT (2026-07-04).** The kitchen + lab great
  room now sits between the loft and the overworld (see "House" above);
  leaving home routes bedroom → stairs → downstairs → front door → overworld.
  Remaining downstairs ideas for later: cooking/eating at the hearth,
  crafting at the workbench, the boiler as a story prop (the last machine
  still running on drained-world power).

## Future Direction — Story Build (recorded 2026-07-12, in progress)

The chapter structure in "Story" above is canon. **Build-fresh doctrine
(2026-07-12): nothing narrative is recovered from git** — the deleted intro,
cutscene kit, dialog box, and Schweinler sprites are rejected wholesale for
how they looked; the beats and gags stay canon, every implementation and
sprite is authored new on the current pipelines. Build order (user call:
**start the game from its first minute**), each a coherent slice:

1. ~~**Prologue A "Sparkless"**~~ — **DONE (2026-07-12).** See the Current
   Milestone section. Pacing pass added (Mom's blessing gate + goose-chase
   and crank-mash minigames).
2. ~~**Prologue B "Professor Poopy Paws"**~~ — **DONE (2026-07-12).** The
   whole thesis-day chapter: plant / wake-up / dash / hall-and-naming /
   call-and-accident / sickroom / fountain / leaving. See the Current
   Milestone section.
3. **Act 1 "The Ebb"** (next) — the Ebb cold-open, the Academy-library interior,
   drained-town wander gates, the meadow as Fuji's combat tutorial, the
   **Elder Tree hermitage** zone (the giant riverbank tree at zone scale —
   lean-to among the roots, corkboard research, the brass gun), the
   party-forming fight. Ends exactly where the combat sandbox boots.
4. **Act 2 expansion** (much later) — the overworld grows: more towns
   (Kitty's town), the walkable Capital, the Burrows and Drain dungeons,
   region-relight glow states.
