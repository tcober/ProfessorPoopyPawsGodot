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

## Alembic Town (`scene/alembic_town.tscn`, 56×34)

The Kakariko-style hub, rebuilt from scratch 2026-07-11.

- The barred **Academy** crowns a north cliff **terrace** on the central axis (authored
  16×32 cliff-face columns, 3 salted variants per column; a grand stone stair descends to
  a lamp-flanked plaza). See the **map-authoring** skill for the terrace kit.
- A **fountain square** at the lane crossing — trail ring forks around the basin + brass
  alembic finial; a flask stall on the rim. (The stall is generic scenery — the Kitty
  stall canon was CUT 2026-07-18; her wheel workshop is off-screen and never seen.)
- Weapons shop **"THE BRASS FANG"** + item shop **"THE CRACKED FLASK"** — **ONE shared
  `town_shop` builder, SAME salt**, so only roof/sign/wares differ and the facade tiles
  dedupe.
- The two-story inn **"THE COPPER KETTLE"** by the stream bridge (river + sea/beach pond
  classes at town scale).
- Locked cottages around the well + a fenced garden, a fenced NE orchard, six
  walk-behind trees.
- All shop / inn / cottage / school doors are **announce-only banners (caps-only font)**.
- Basil's `home` door → `downstairs` (`interior_spawn="front_door"`).
- The south gate (`exit_south`) → the tiled overworld.
- The bright-era twin is `scene/town_fest.tscn` / `maps/town_fest.txt` — a **BYTE COPY**
  of `town.txt` in the `town_fest` palette (spring grass, cream plaster, festival
  magenta). The fest Academy door is OPEN (`town_academy(open_door=True)`); the sealed
  bars stay drained-only. **Keep the two grids in lockstep.**

## Lanternwood (`scene/lanternwood.tscn`, 44×28)

Fuji's snow town, on the same `TravelScene` machinery.

- Log cabins as 8-frame Tier-3 sheets with softly pulsing fire-lit windows + woodsmoke,
  conifers, a frozen pond (**Tier-1 ice over WALKABLE pond cells — never sea/river, those
  animate**), `road_verge="snow"` lanes.
- Announce-only banners on FUJI'S FAMILY HOME + three cabins.
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
