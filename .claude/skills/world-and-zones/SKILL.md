---
name: world-and-zones
description: The world layer — the five-lands tiled overworld, its markers and era twin, the walkable town zones (Alembic Town, Lanternwood), the combat zone (Whisker Meadow), interiors, and how travel between them works. Load BEFORE adding or moving a location marker, wiring a door or gate, adding a new zone or interior, editing the overworld map, or when travel lands the player in the wrong place.
---

# World and zones

Two scales, one tile pipeline:

- **Overworld** (`scene/overworld.tscn`) — a CT/SoS-style TILED travel map. 24×24 chibi
  travel scale (~16px figure), terrain-gated walking, **no map combat**.
- **Zones** — full-scale 48×48 gameplay. Combat zones (Whisker Meadow) and walkable
  town zones (Alembic Town, Lanternwood) both ride the same overworld tile driver.

Full statement: **docs/DESIGN.md → "World Structure — Overworld + Zones"**.

## The five lands (2026-07-19)

A **112×63 ocean-separated continent**. **There is NO walkable crossing between lands** —
the boat is future story.

| Land | Contents |
| --- | --- |
| **SW forest** | the playable core: Alembic Town icon, ONE winding trail NE past Whisker Meadow over the river bridge, and the **HOME TREE** (`g` trunk / `G` walk-behind canopy, 96×144, ~6× the chibi — only the trunk-core blocks) leaning over the SE coast: Basil's hermitage, arched lit door + round window + flue |
| **Central mountain** | the Kingdom — the Capital's pale-stone CASTLE (`C`), the snowcapped HORN (`V`), and **THE BIG MOUNTAIN** (`B`, 14×10): pre-Ebb a snow summit, post-Ebb the GIANT CRYSTAL, ablaze on the glow overlay |
| **NW ice/snow** | a pine-forested winter island (`i` snow, `P` pines) carrying **LANTERNWOOD** (`L` icon, `d` gate) — Fuji's hometown, visible but ocean-locked until the boat |
| **NE purple desert** (`b`) + **E/SE lava** (basalt `a`, animated lava `l`) | one eastern landmass split by a volcanic ridge |
| **Offshore** | mysterious islands, unreachable |

The old waste / obelisk / Burrows geography is **GONE**.

**Two eras, byte-locked.** `overworld_bright.txt/.tscn` is the pre-Ebb twin (snow summit,
mint glow) — staging, screenshots, and the Ebb scene only. `overworld.txt/.tscn` is the
post-Ebb default. **The grids are BYTE-LOCKED: edit one, edit the other in the same
commit.** Same pattern as `town.txt` ↔ `town_fest.txt`.

Lit windows, coals and the crystal ride the additive glow overlay. (The cloud-shadow
shade overlay was cut — dark ovals read as smudges at CT zoom.)

## Town icons

Towns on the overworld are **CT-faithful cluster ICONS** — one drawn composition of
overlapping roofs, solid except its gate-mouth `D` cell, which travels INTO the town's
walkable zone scene.

Region edges are drawn as **1-cell stair-steps in the map txt** — the autotile's 45°
corner cuts render them as continuous diagonals. (A region line is not a coast; don't
author it as one.)

## Travel plumbing

- `scene/overworld_location.gd` — the markers: `id` / `display_name` / `target_scene` /
  `locked_text`.
- `scene/game.gd` (autoload **`Game`**) remembers `overworld_spawn`, plus `town_spawn` /
  `interior_spawn`: the map anchor the next town or interior scene spawns at,
  **read-and-cleared** by the scene's `_ready`, so `""` means "its default entry".
- `scene/travel_scene.gd` — the shared travel/announce machinery for walkable zones.
- Leaving a zone returns to its overworld marker via `Game`.

**All the door gotchas — door-mouth arrivals, `_standing` suppression, `_deliver_standing`,
never sharing an anchor between travel and announce zones, flipping `target_scene` rather
than adding a second zone — are in the `story-scenes` skill.**

## Alembic Town (`scene/alembic_town.tscn`, 80×56)

The Kakariko-style hub, rebuilt from scratch 2026-07-11 and again 2026-07-30 as a
**forest-floor village with four great trees**: the town — lane, market square,
three shops, clinic, cottage, well, stall, fountain — is on the ground, and each
tree carries a round RING DECK near its crown with a door and a lit window in its
trunk, reached by a rope ladder. The canopy is four ISLANDS, not a floor: a town
that is 100% deck renders as stripes of plank and fascia. You walk a full circle
around each
one. Load **map-authoring** before touching the grid; the doctrine is in DESIGN.md
→ "STACKED WALKABLE STOREYS".

- **The Academy has LEFT this grid** (2026-07-30) — it is its own scene now, and what
  stays here is the way there: the **north lane** (`exit_north` → `academy.tscn`).
  Coming back sets `Game.town_spawn = "north"`, which lands you in this town's own lane
  rather than at the south gate.
- A **fountain square** at the lane crossing — trail ring forks around the basin + brass
  alembic finial; a flask stall on the rim. (The stall is generic scenery — the Kitty
  stall canon was CUT 2026-07-18; her wheel workshop is off-screen and never seen.)
- Weapons shop **"THE BRASS FANG"**, item shop **"THE CRACKED FLASK"** (adult Sage's,
  where Act 1 beat 4 happens) and the inn **"THE COPPER KETTLE"** — all three on the
  forest floor, 5×4 each, **ONE shared `_town_props.town_shop` builder** on the
  cottage's own envelope, with a `trade` (arms / tonics / inn) picking the awning's
  cloth colour, the wares in the display window and the device on the hanging board
  together. A trade is announced by its OBJECT painted on a swinging board, never by
  lettering: there is no font at 16px. (They were `tree_hut`s until 2026-07-30 and read
  as tiki huts — see the art-pipeline skill; a hut is a BOUGH building.)
- Locked cottages around the well + a fenced garden, a fenced NE orchard, six
  walk-behind trees.
- All shop / inn / cottage doors are **announce-only banners (caps-only font)**.
- Basil's `home` door → `downstairs` (`interior_spawn="front_door"`).
- The south gate (`exit_south`) → the tiled overworld.
- **The two era maps share a byte-locked GRID and NOT a byte-locked ANCHOR BLOCK.**
  `town_fest.txt` carries fifteen anchors `town.txt` does not — the festival square,
  the five NPCs, the goose and its hiding place, Sage's ribbons, Schweinler's
  four-corner creep route, Ridley's lane, the south-gate tableau. Emitting town.txt's
  anchors into both is what killed chapters A1-A13 and B3/B5/B11 in the 2026-07-30
  rebuild: every one of those scenes asserts on an unknown anchor before its first
  frame, so the break is total and invisible until you load the scene.
- The bright-era twin is `scene/town_fest.tscn` / `maps/town_fest.txt` — a **BYTE COPY**
  of `town.txt` in the `town_fest` palette (spring grass, cream plaster, festival
  magenta). **Keep the two grids in lockstep.** `town_fest.gd`'s own `School` marker
  still travels straight to `hall.tscn` for the recital — the prologue never comes out
  to the Academy precinct, so that shipped chapter is untouched by the new scene.

## The Alembic Academy (`scene/academy.tscn`, 64×48) — NEW 2026-07-30

The college, one lane north of the town. It used to be a 14×9 landmark on a cliff
terrace at the top of the town grid; given its own map it can be a **precinct you
approach along an axis, gate by gate**, which is the whole reason it moved. Full
composition in DESIGN.md → "THE ALEMBIC ACADEMY, walkable".

South to north: causeway → **the beck** (a stream on animated water — NOT a chasm) and
its four-cell bridge → outer ward → **THE RAMPART**, a crenellated curtain wall clear
across the map pierced by a gatehouse of two drum towers → **the inner court** with the
GREAT ORRERY standing on the axis (it blocks the straight line from gate to stair on
purpose) flanked by the observatory and the still-house → **the grand stair** → **THE
KEEP** (`town_academy`, rose window burning mint), with **two great trees flanking it
where a castle would put corner towers**.

- Everything is announce-only in the drained present. The great door is barred.
- **Paving only where the procession walks, lawn either side.** Paved edge to edge the
  court was 52×9 cells of one flat fabric — the "100% floor" failure the canopy town
  already taught, in a different material.
- Every piece standing on the paving carries its own terrain name rendering `road`
  (`courtlamp`, `rampart`, `gate`, `towerbody`, `orrery`, `orrerybase`) — see
  **map-authoring**: a terrain names the UNDERLAY, and reusing `lamp` here would punch
  grass squares through the court.
- `tools/academy_probe.gd` covers the round trip both ways, the gate's clearance for a
  real body, and the spawn not sitting inside its own exit trigger.

## Lanternwood (`scene/lanternwood.tscn`, 56×50)

Fuji's snow town, on the same `TravelScene` machinery. A **Narshe-style terraced**
town since the 2026-07-28 rebuild: five walkable levels, four cliff bands at three
heights, on the shipped terrace kit. **Two ways out, and they are not
interchangeable** — the south gate walks onto the island, and **THE PIER crosses the
ocean.**

### THE HARBOUR (2026-07-29) — the class choices are the design

The east end of LEVEL 1 is a cove: sea from col 46 to the map edge and from BAND D
past the south border, so the water leaves the frame on two sides and reads as ocean
rather than pond. Sea is solid, so **the cove seals the map border on its own** and
the enclosure lint still sees only the two gate-mouth cells.

| piece | chars | terrain → render class | why |
| --- | --- | --- | --- |
| the cove | `~` | `sea` → `sea` | animated, solid, shores against snow as an **ice-shelf lip** (`_lip_band`'s `"snow"` pair — already written) |
| the pier deck | `=` | `dock` → **`bridge`** | `bridge` ∈ `WATERC`, so **no coastline forms under the deck**; not in `_lower_frames`' animated set, so the deck is static over swelling water |
| the launch's berth | `b` | `berth` → **`sea`** | solid cells that paint as open water — a boat moored on painted planks reads as a boat in a car park |

Two things worth stealing next time a walkable edge meets water:

- **The pier is baked Tier-1 as ONE opaque `town_dock` blit** (the `town_trestle` /
  cliff-face idiom). Its rope rails sit on *walkable* cells, and upper-layer art over
  a walkable cell is exactly what the z-order doctrine forbids. Nothing autotiles it
  either — you walk along its length, so `_bridge_cell`'s N/S rails are wrong for it.
- **The launch moors DIRECTLY south of the deck, and that adjacency is load-bearing.**
  A body pressed into the deck's south row hangs ~11px of sprite over the cell below
  it; the hull, y-sorted south of the body, swallows it. **The mask-band problem
  answered by composition instead of by a mask** — no `bridge_fascia`, no
  `mask_band`, no upper-layer cell.

`town_moot_hall` sits on a cabin's 5×4 footprint (roof `vV` + a `D` one row south at
the x-centre), so it asks nothing new of the kit; the **bell-cote on its ridge** uses
the same `_snow_roof(ridge=)` trick that stands the library's lantern cupola.

**A SOLID NPC IN A ONE-CELL LANE IS A WALL, NOT A SQUEEZE.** Placing the moot hall
pinched LEVEL 1's east half to a single walkable row, and Mayor Hollis's 12×8 body in
a 16px cell sealed the pier off completely — the player could walk up to him and had
nowhere to go. The fix was to open a forecourt (delete the spruce east of the hall)
and move him onto it. Check every NPC anchor has room on more than one side.

### The rest of the town

- Log cabins as 8-frame Tier-3 sheets with softly pulsing fire-lit windows + woodsmoke,
  conifers, a frozen pond (**Tier-1 ice over WALKABLE pond cells — never sea/river, those
  animate**), `road_verge="snow"` lanes.
- Announce-only banners on FUJI'S FAMILY HOME, three cabins, and THE MOOT HALL.
- **THE PIER is a plain `Area2D` (`$DockZone`), NOT an `OverworldLocation`** — boarding
  is a staged beat, and `TravelScene._announce` would hold `_busy` across the whole
  cutscene. One zone on that anchor, one owner. (The doctrine's "never share an anchor"
  rule cuts both ways: sometimes the answer is not to use a Location at all.)
- **THE LIBRARY is the one door in town that TRAVELS** (`target_scene` →
  `scene/library.tscn`; `lanternwood.gd::_on_travel` names the phase) and the one
  building that isn't a cabin. `town_library()`, 144×112 over a 9×7 footprint: log walls
  on a coursed fieldstone plinth, a keystoned stone portal with a lit fanlight, four TALL
  ARCHED reading windows, a street-facing cross gable with a rose window, and the glazed
  **LANTERN CUPOLA** on the ridge — the town's name made a landmark. Seven apertures on
  the one hearth breath. It backs onto the north pines (nothing walkable hides behind a
  112px sheet) over a shoveled forecourt.
- The name is diegetic: honest flame owes magic nothing, which is why the Ebb-night tint
  is burned straight through by fire-lit windows and oil lanterns.

## Whisker Meadow (`scene/meadow.tscn`)

The combat zone and the tiled combat-zone reference implementation (Tiles → Collision →
y-sorted World → TilesUpper). Slimes, beaker respawns, HUD. Marker `meadow`.

Boulders are a **grass-underlay struct + a per-cell prop** — never the mountain class.
Trails are 1-wide and 4-connected. Props live in `assets/_meadow_props.py` (per-cell
boulder domes + the trailhead cairn).

**`scene/meadow.tscn` is NOT the same as the deleted `meadow_fest`** — the whirligig
quest moved onto the bluff. Keep the combat meadow.

## Interiors

`scene/house.tscn` is the interior reference implementation: a small dense CT-bedroom
diorama floating in void (a 10-tile-wide room on a 24×14 map), brown plank walls / teal
weave / gold dawn window; `E` toggles the curtains. Its SW staircase descends to
`scene/downstairs.tscn` — the kitchen + steampunk-lab great room (20-tile room, hearth
fire = light source + glow, copper boiler, workbench, alcove stairs back up) whose south
front door opens into Alembic Town.

The interior recipe: **8-tile-ish room floating in void, every wall stretch occupied.**
`scene/sickroom.tscn` and `scene/library.tscn` were both built on it —
the library was rebuilt 2026-07-25 from a 10-tile closet onto the 18-tile
downstairs-diorama frame, because a research puzzle needs somewhere to search.

Two interior lighting notes:

- **An 18-tile hall lit by one corner fire leaves the reading end unreadable** — the
  library has a second lit pool under the desk lamp. The aisles are MEANT to be dim.
- The `downstairs` hearth mantel carries the whirligig relic (`WHIRL_*`: fx-sheet
  droop/spin frames, a hearth-draft stir every ~7s, a plain `$World` sprite keyed north
  of any body).

**New free-standing interior prop rule:** a `stack()` (the library's bookshelves) is
32×48 on a 2×2 footprint, a y-sorted entity **NEVER baked** because a body walks both
sides of one — and it is one cell taller than its footprint, so whoever is in the aisle
behind it reads as a head above the books.

## Adding a new zone

A new scene = **a map txt + a thin generator config**. See the **art-pipeline** and
**map-authoring** skills.
