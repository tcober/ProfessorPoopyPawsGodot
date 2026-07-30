# ALEMBIC TOWN, REBUILT — the four-storey canopy village (2026-07-29)

A WORKING DOC, not the bible. `docs/DESIGN.md` stays the source of truth for what
the game is; this is the contract for one conversion, and it should be **deleted
and folded into DESIGN.md + the `map-authoring` skill when it lands.**

---

## STATUS — read this first

| | state |
| --- | --- |
| **v1: the 56×34 two-strata canopy town** | **SHIPPED AND GREEN.** Everything below is a rebuild of a town that already works — the whole probe suite passes on it today. Do not start the rebuild without a commit to fall back to. |
| this design (size, four storeys, trunk armature, legend) | **DONE — this document** |
| the anchor/consumer inventory the re-author must be authored against | **DONE — the APPENDIX at the end of this file.** Do not regenerate it; it also records two real v1 findings worth fixing first |
| the grids themselves | **NOT STARTED** |
| generators, scenes, probes | **NOT STARTED** |

**What v1 already gives you, and what the rebuild must not lose:** the strata kit
(`assert_strata` / `assert_span` / `assert_band_orientation` / `assert_stair` /
`assert_lift` / `assert_door_approach` / `assert_reachable`), `tree_edge` /
`tree_edge_return` / `tree_span_edge`, `tree_hut` (the Slitherbough/Endor building
— its four cues are non-negotiable, see DESIGN.md), the ported `_px_deck` plank
field, the hand-pinned `timber`/`THATCH`/`ROPE` ramps, the scripted dinghy lift,
`tools/lift_probe.gd`, `party_probe` phase 3, and `tools/zwalk.gd` (the z-order
walkaround). **None of that needs rewriting — only the grids do.**

**THE Z-ORDER WALKAROUND IS UNFINISHED.** `tools/zwalk.gd` runs and produces four
families of contact sheets (`pressed` / `notch` / `below` / `props`) derived from
the map. On v1 the `notch` family was eyeballed and is clean — bodies beside a band
step are correctly unmasked. The `pressed`, `below` and `props` families were
generated but **not fully reviewed**. Re-run it and review before trusting v1's
layering, and again after the rebuild:

```sh
/Applications/Godot.app/Contents/MacOS/Godot --path . \
    --script tools/zwalk.gd -- res://scene/alembic_town.tscn /tmp/z
```

---

## WHY A REBUILD, ONE VERSION IN

The 56×34 treehouse town shipped and every probe passes. It still reads as a
**raised boardwalk carrying huts**, not as a village in a forest canopy, and the
diagnosis is not a matter of taste:

- **13 of 34 rows are spent on stone** (the Academy, its forecourt, the cliff
  band). The canopy got seven rows and the floor eleven.
- **A cone needs height and a trunk needs run.** With one canopy tier there is
  nowhere for a trunk to *pass through* anything, so the whole town has ONE great
  tree in it and the boardwalk is the biggest mass on screen. In both references
  — FFXIV's Slitherbough and Endor — the **trunks are the biggest mass** and the
  buildings are subordinate, tucked between and around them.
- **One canopy tier cannot layer.** The references read as villages partly
  because you see platforms at several heights at once.

I had also told the user multi-level was unreachable. That was wrong, and the
error is worth recording because it is the same error twice: **three canopy tiers
is just three distinct stratum names with solid bands between them.**
`assert_strata` handles it unchanged, and a ladder linking two tiers still borders
exactly two strata. I said no because it did not fit in 34 rows — an argument
about the size I had accepted, not about the format.

**So the rule this rebuild is authored under: THE TREES ARE THE ARMATURE. Author
the trunks first and hang the town on them.** The previous pass authored a
boardwalk and then sprinkled trunks into the gaps, which is the inversion that
produced a high street.

---

## THE FOUR STOREYS

`stratum:` names, and every one of them is a genuine disjoint walkable region:

| stratum | what it is | rows |
| --- | --- | --- |
| `terrace` | the Academy's cut-stone forecourt — the establishment, above everything | 9–10 |
| `canopy_hi` | the HOMES, in the crowns. Basil's house is here. | 13–19 |
| `canopy_lo` | the PUBLIC town: both shops, the inn, the lift head, the boardwalk | 23–29 |
| `ground` | the forest floor: the square, the fountain, the clinic, the creek, the pond, the gate | 33–45 |

Face bands between them, all `stamp_columns` + `mask_band`:

| band | rows | run | pierced by |
| --- | --- | --- | --- |
| `C` the Academy's cliff | 11–12 | 2 | `S`, the grand stone stair (a `link`) |
| `y` the high fascia | 20–22 | 3 | `z`, rope ladders (a `link`) |
| `v` the low fascia | 30–32 | 3 | `z`, rope ladders (a `link`) |

**The stair is now a LINK, not ground.** It joins `terrace` to `canopy_hi`, which
is the one structural consequence of putting the homes above the shops: you reach
the Academy from the top of the town, not from the lane. Every beat this touches
is *better* for it — `town_thesis`'s morning dash becomes a paw-print run across
rope bridges and up a stair instead of a jog along a road.

**Row budget, 48 rows:**

```
 0- 8  THE ACADEMY (kK6, 14x9)             stone, art unchanged
 9-10  the forecourt                        stratum:terrace
11-12  C band + S stair                     the terrace's face
13-19  CANOPY HIGH — the homes              stratum:canopy_hi
20-22  y band (3) + z ladders               the high fascia
23-29  CANOPY LOW — the public town         stratum:canopy_lo
30-32  v band (3) + z ladders               the low fascia
33-45  THE FOREST FLOOR                     stratum:ground
46-47  the gate mouth                       (exit_south)
```

Seven deck rows per tier is not generosity: `assert_door_approach(rows=2)` wants
two clear rows under every door, a `tree_hut` footprint is 4–5 rows, and
`town_thesis`'s `plant` beat lands `home+(0,26)` and `home+(0,38)` two rows below
Basil's door. Shave a row and three shipped cutscenes end early against a wall.

---

## THE TRUNK ARMATURE — author this first

**Six great trees**, each a 3-column channel running from the forest floor up
through both boardwalks. One `tree_trunk(cells=17)` sprite per trunk — 48×272,
bottom-anchored at its foot — so a single continuous trunk passes *behind* both
decks and both fascias. That one sprite is the whole reference read.

The char stack in a trunk channel, north to south:

```
rows 13-17   a    solid   the crown, as leaf mass (renders the forest lobe lattice)
rows 18-19   Y    walk    canopy_hi — the high deck WRAPS the trunk (walk-behind)
rows 20-22   y    solid   the trunk through the high fascia
rows 23-27   J    walk    canopy_lo — the low deck wraps it (walk-behind)
rows 28-34   j    solid   the trunk through the low fascia AND its base on the floor
rows 35+          ground  the floor, with the buttress roots' contact shade
```

Why it sorts correctly with ONE sprite: y-sorted at the foot (row 34's south
edge), the trunk draws OVER every body north of it — on either deck, on either
crown — and UNDER every body south of it on the floor. That is every case a trunk
has, and it is why the alternating walk/solid pattern above is not a compromise:
**the bands alternate, so the trunk alternates.**

**AUTHORING RULE: a building never shares a trunk's columns.** The trunk sprite is
48px wide and y-sorted 500px down the map; anything in its columns north of it is
drawn over. Platforms go BETWEEN trunks, which is also exactly how both references
look.

Trunk channels, and the bays between them:

```
cols   3- 5   border / bough
cols   6- 8   T1
cols   9-15   bay A   (7)
cols  16-18   T2
cols  19-26   bay B   (8)
cols  27-29   T3
cols  30-37   bay C   (8)
cols  38-40   T4
cols  41-47   bay D   (7)
cols  48-50   T5
cols  51-57   bay E   (7)
cols  58-60   T6
cols  61-68   bay F   (8)
cols  69-71   border
```

---

## WHAT GOES WHERE

**canopy_hi — the homes (rows 13–19).** `tree_hut`s in the crowns, one per bay.
BASIL'S HOUSE in bay A (the west end, hardest to reach, first thing you see from
the gate looking up) — his door → `downstairs` → the lab in the hollow → the
bedroom in the fork, interiors untouched. Two or three neighbour huts in the other
bays so the tier is a street of homes and not one house.

**canopy_lo — the public town (rows 23–29).** THE BRASS FANG and THE CRACKED FLASK
(adult Sage's shop — Act 1 beat 4 happens in it), THE COPPER KETTLE, and the
DINGHY LIFT's top landing. This is where a player who climbs one ladder arrives,
so it carries every shopfront.

**ground — the forest floor (rows 33–45).** The fountain SQUARE (you arrive from
the gate, walk the root lane, and the whole town is over your head — the
establishing shot the conversion is for), THE DOCTOR'S OFFICE on its stoop with a
clear lane east (the clinic-steps ending), the neighbour's cottage, the well, the
creek and its footbridge, the orchard, the pond, and the lift's crank drum. Both
ground buildings keep Alembic's plaster-and-cement language: the old floor village
with a woven canopy grown over it.

**Vertical circulation.** Ways off every storey, ≥2 each:
- `terrace` — the S stair (and nothing else; it is a dead end by design)
- `canopy_hi` — two `z` ladders down to canopy_lo, at opposite ends
- `canopy_lo` — two `z` ladders down to the floor, plus the LIFT
- `ground` — the ladders, the lift, and the two exits

**Spans.** `W`/`e` rope bridges on canopy_lo across the creek's airspace, and
`R`/`E` on canopy_hi between crowns. Two-rows-deep, over a NAMED POSITIVE THING
(`a` bough, `j` trunk, `r` creek) — never an absence.

**The second exit.** Act 1 beat 5b (THE HOLLOWAY) leaves town to the SE, so the
floor gets an `exit_se` mouth as well as the south gate. Wiring it is beat 5b's
job; the mouth is authored now so that beat is not blocked on a third grid pass.

---

## THE NEW LEGEND — resolved

The shipped town spends **61** chars. The free pool is exactly
`E R Y c f g y` plus the digit `0` and punctuation — seven letters, which is
what the high tier needs, so nothing has to be re-typed except the strata.

**SOLID chars carry no stratum**, so every face, trunk and bough is shared
between tiers for free. Only WALKABLE chars need a name, which is why there are
three door chars and not one: a legend char carries exactly ONE stratum.

**NEW (7):**
```
legend Y deck       walk  stratum:canopy_hi   ; the HIGH boardwalk — the homes' tier
legend y deckedge   solid                     ; the HIGH fascia (run=3)
legend c crown      walk  stratum:canopy_hi   ; the high deck AROUND a great trunk
legend g boughtop   walk  stratum:canopy_hi   ; a walkable leaf mass, high tier
legend R plank      walk  stratum:canopy_hi   ; a high span
legend E plankedge  solid                     ; a high span's 1-row fascia
legend f door       walk  stratum:canopy_hi   ; a home's door
```

**RE-STRATUM'd (the v1 canopy becomes the LOW tier) — `canopy` → `canopy_lo`:**
`B` `V` `W` `A` `J` `M` `d`

**RE-STRATUM'd — `S` the grand stone stair becomes `stratum:link`:** it now joins
the terrace to `canopy_hi` rather than joining two patches of ground, so
`assert_strata`'s "a link borders EXACTLY TWO strata" starts governing it. That is
a gain: the stair was previously the one vertical connection in this town that
nothing checked.

**UNCHANGED:** every solid char (`a j v b e Q i C` and all the building triples),
both ladders (`z Z`, already `link`), and the whole floor set.

**THE TERRACE KEEPS THE `ground` STRATUM** rather than getting a name of its own,
and that is deliberate: `.` `,` `-` are spent on both the forecourt and the forest
floor, and one char carries one stratum. Two DISJOINT `ground` regions are legal —
`assert_strata` only forbids adjacency, `assert_reachable` reaches the forecourt
through the stair, and the stair still borders exactly two strata (`ground` and
`canopy_hi`). The only thing given up is that a stratum-aware query cannot tell the
forecourt from the floor, and nothing asks.

---

## WHAT THIS COSTS, AND WHY IT IS AFFORDABLE

**The events are already portable.** Phase 0 of the previous conversion
de-hardcoded every cutscene route: the creep, the goose theft, the clinic stoop,
the knapsack tableau, `_square_route` and `_locked_view` are all derived from
anchors and feature bboxes. The offsets that remain (`home+(0,26)`, `BAG_OFF`,
`cottage_e+(4,14)`, `school+(0,40)`) are RELATIVE, so they survive a move as long
as the walkable rows around each anchor hold — which is what
`assert_door_approach` enforces. `.tscn` marker positions are recomputed at load.

So the bill is: re-place ~35 anchors across two byte-locked files, extend three
generators, and re-run the suite. Not: rewrite the Prologue.

**The suite that has to go green again:** `_check_art.py`, then `town_probe`,
`recital_probe`, `party_probe` (incl. phase 3, the leash across a fascia),
`lift_probe`, `library_probe`, `defence_probe`, and `prologue_probe` LAST.
Then `tools/zwalk.gd` for the z-order walkaround on all four storeys.

## RISKS THIS INTRODUCES THAT v1 DID NOT HAVE

| # | risk | mitigation |
| --- | --- | --- |
| R1 | FOUR strata multiplies the fusion surface: every band now has two storeys to keep apart | `assert_strata` is unchanged and catches all of it; it is the reason this is authorable at all |
| R2 | the S stair becomes a `link`, so `assert_strata`'s "exactly two" now governs it | it borders `terrace` and `canopy_hi` only — assert it |
| R3 | a 272px trunk sprite y-sorted 500px down draws over anything in its columns | the authoring rule: no building shares a trunk channel. Assert it. |
| R4 | the terrace is reachable ONLY by the stair, so a mistyped stair strands the Academy | `assert_reachable(full=True)` from `exit_south` + `home` |
| R5 | `town_thesis`'s dash goal `school+(0,40)` now lands on the C band, and the dash route is canopy→terrace | verify the goal rect is enterable from the stair; re-shoot the beat |
| R6 | three ladders' worth of new `assert_stair` geometry, each needing level bands on BOTH sides | keep every ladder clear of a band STEP |
| R7 | 3456 cells and 4 fabrics — the atlas could balloon | the deck fabric is 4 tiles by construction; watch `finish()`'s count |
| R8 | the map grows, so `_locked_view` moves and the goose flight's off-camera proof changes | it is derived and it has a runtime assert; re-run `prologue_probe` |

---

# APPENDIX — THE CONSUMER CONTRACT

Generated 2026-07-29 by an exhaustive read-only sweep of `scene/`, `tools/`,
`assets/`, `entities/` and every `.tscn`. **This is the list the re-author must be
authored against**; a missed consumer is a silently broken cutscene. Line numbers
are as of v1.

## Anchors, and every offset added to them

Everything reads through `MapData.anchor_px(map, name)` = `cell * 16 + (8,8)`.

| anchor | consumers | offsets added |
| --- | --- | --- |
| `home` | `alembic_town.gd:56`, `town_fest.gd:89,176`, `town_thesis.gd:79,119,138,166,169,197,203`, `prologue_probe:205,358`, `party_probe:145` | **`+(0,12)` `+(0,22)` `+(0,26)` `+(0,38)=BAG_OFF`** — and `+(0,190)` in party_probe (deliberately the floor below the fascia, the cross-stratum leash test) |
| `school` | `town_fest.gd:131` (the SAME Location flipped live to travel), `town_thesis.gd:86,228`, `prologue_probe:287,386`, `recital_probe:149` | **`+(0,24)`** (plant spawn) and **`+(0,40)`** — a SEPARATE 48×16 dash-finish Area2D. Two disjoint trigger rects 40px apart on one anchor; both probes carry comments warning about it |
| `cottage_e` | `town_thesis.gd:81,287,292,302` | **`+(4,14)`** (Basil sits on the stoop), **`+(38,14)`** (Ridley's approach) |
| `exit_south` | all three scenes' `$ExitSouth`, `town_thesis.gd:141,181,370`, `town_fest.gd:157`, probes | x-only in `_wall_gate_mouth` and in the off-map trudge (`y` from `size_px`) |
| `goose_hide` | `town_fest.gd:301` | **`+(16,0)`** — the anchor is on the walkable bank, the goose tucks one east under the crown |
| `sage_pos` | `town_fest.gd:257,325` | three ribbon spots `(-14,-58) (12,-72) (-2,-86)`; the theft's snatch point derives from the lowest ribbon's stashed `rest` meta |
| `basil_mark` | `town_fest.gd:395`, `prologue_probe:173` | **`+(0,-16)`** in the probe |
| `lift_down`/`lift_up` | `alembic_town.gd:105-121,162`, `lift_probe:46`, and `assert_lift` reads `m.anchors[...]` directly | `assert_lift` requires `lift_down` on **canopy** and `lift_up` on **ground** — the names are from the RIDER's perspective, and inverting them is a copy-paste mistake the assert catches only at generator time |
| `creep_gate/cross/lane/head`, `lane_e`, `gate_inside`, `festival`, `player_start`, `weapons`, `items`, `inn`, `cottage_w`, `schw_pos`, `npc_*` | bare | — |

## Derived geometry (moves with the map for free)

`MapData.size_px` → camera clamps (self-adjusting), `_wall_gate_mouth`'s
`y = size_px.y + 4`, the trudge's `y = size_px.y + 16` with duration derived at
`TRUDGE_SPEED`; `_locked_view` (the goose's off-camera proof, with a RUNTIME
assert); `_square_route`'s dog-leg off `bbox_rect("oO")`; the fountain trigger's
position off the same bbox; the lift ride's anchor-to-anchor delta.

## Load-bearing literals — NOT derived, nothing lints them

- `RectangleShape2D_exit` **32×16** in all three town `.tscn`s — matches today's
  2-cell gate mouth exactly. **Nothing cross-checks an Area2D shape against the
  map's border gap.** Widen or narrow the mouth and this does not follow.
- `_wall_gate_mouth` rect **64×8**; the lift/home-door zones **24×16**; the
  fountain trigger **96×96** (position derived, size not); the dash goal **48×16**.
- `BAG_OFF (0,38)` and `TRUDGE_SPEED 18.5` are statements about this town's
  authored depth, written as constants.
- `town_fest.gd:43-53` — `BEAK_OFF`, `FLY_IN/OUT_CLEAR`, `FLY_IN/OUT_LIFT`: tuned
  against the town's width and the ribbons' height. A much narrower town trips the
  runtime off-camera assert; a much taller one degrades the swoop with no error.

## Two findings about v1 worth acting on

1. **`alembic_town.gd` never calls `_wall_gate_mouth()`** — `town_fest.gd`,
   `town_thesis.gd` and `lanternwood.gd` all do. Today the 32×16 exit trigger
   covers the whole 2-cell mouth so a body cannot slip past it, but the adult
   sandbox has no backstop and no refusal state, so a widened mouth in the rebuild
   walks the player straight off the collision grid into the void. Add the wall.
2. **`_check_art.py:254-257`'s comment is stale** — it claims town's upper layer
   is empty and the z-order lints short-circuit. The layer carries 9 cells (the
   span fascias + the creek under the hero span), so the support / corridor-cap /
   ridge-placement lints DO run on both town maps. The enforcement is right; the
   comment misleads. Fix the comment.

## Also true, and useful

- **No town NPC wanders.** `town_fest.gd` never calls `npc.bind_map()` or sets
  `wander_cells`, so `npc.gd::_can_stand` is dead for this scene — only Lanternwood
  wires villager wander. A re-author cannot break wandering villagers here.
- **`PLACEMENTS`' entity-on-walkable lint is vacuous for all three town scenes** —
  none has static `$World` children. It offers zero protection against a
  hand-placed node on a solid cell here.
- `assert_npc_room` only checks anchors matching `*_pos` / `npc_*`. Rename one out
  of that pattern and it is silently exempted from the room-to-move rule.
