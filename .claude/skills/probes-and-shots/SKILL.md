---
name: probes-and-shots
description: Verifying changes — tools/shot.gd for eyeballing a scene headlessly, the per-scene probe inventory and which one to run when, and the headless/harness gotchas (--headless --import, Engine.max_fps, polled input, --script class_name poisoning, occluded-window draw). Load BEFORE running or writing any tool in tools/, before verifying a scene or story change, and whenever a probe hangs, passes trivially, or behaves differently from the real game.
---

# Probes and screenshots

## The standing rule

**Verify the scene you changed — do not re-run the whole chapter probe.**

`tools/prologue_probe.gd` drives the entire chapter and takes minutes. It is for
handoff-chain changes and final checks, **not for every edit.** Prefer the per-scene
probe, or a `tools/shot.gd` screenshot.

## Probe inventory

| Probe | Checks | Covers |
| --- | --- | --- |
| `tools/prologue_probe.gd` | 56 | the whole Prologue A+B+Ebb chain — slow, handoff changes only |
| `tools/recital_probe.gd` | 13 | the recital chain's three legs, alone, in ~2min |
| `tools/library_probe.gd` | 28 | the library scene alone (ebb + research phases) |
| `tools/status_probe.gd` | 50 | statuses, mixing rules, loadout across a scene change |
| `tools/rpg_probe.gd` | 81 | sheets, stats, gear, satchel |
| `tools/save_probe.gd` | 31 | save/load round-trip |
| `tools/defence_probe.gd` | 32 | the kit→battle chain, and the south gate held during it |
| `tools/motion_probe.gd` | 47 | **THE MOTION + THE CROSSING** — Mayor Hollis as a three-state fixture, the beat's flags and party lock, idempotence, the pier refusing then casting off, the west-shingle landing. Its most valuable check is geometric: a mayor is a solid 12×8 body, so it BFSes the walkable graph with his cell removed and proves he cannot seal the pier, then walks a body down the harbour lane for real to prove the graph isn't lying |
| `tools/muzzle_probe.gd` | 30 | a projectile is never born inside a wall — both axes |
| `tools/ladder_probe.gd` | 17 | **THE ROPE-LADDER LANE** — the only join between Alembic's forest floor and a ring deck, and none of it visible to any art lint. That the lane beats a sideways press, that a diagonal climbs at FULL speed, that the hop is refused on the rungs, that the FUNNEL gets an off-centre walk-in through a mouth narrower than the ladder — and, the one a pin can plausibly break, that the climb still ENDS on the canopy going up and the ground coming down. A body held on the centre line of a ladder it cannot leave looks exactly like a body still climbing |
| `tools/town_probe.gd` | — | the home-arrival flow: boots the downstairs, walks out Basil's front door, prints where the party lands on the ring deck, then walks back in. Print-and-eyeball rather than checked — read the positions it prints |
| `tools/academy_probe.gd` | 12 | **THE ALEMBIC ACADEMY** — the precinct north of Alembic Town. The generator already asserts the composition on the walkable graph; this covers everything that needs a BODY: the round trip in both directions (the two halves are wired in different files), a 12×8 box actually fitting through the two-cell gate between the drum towers, every marker standing on walkable ground, and — the one that caught something — the spawn not sitting inside its own exit trigger, which reads exactly like a scene that failed to load |
| `tools/party_probe.gd` | — | brain moods, no in-view pops, settle distances, and **phase 3: the leash ACROSS A FASCIA** — the one genuinely new systems risk in a stacked map. It checks the follower's STRATUM, not the distance: the distance passes even when the follower is stuck directly below the leader against the boardwalk |
| `tools/overlay_probe.gd` | — | the paused-modal stack |
| `tools/status_shot.gd` | — | poses the status tells and the mixing bench for eyeballing |
| `tools/zwalk.gd` | — | **THE Z-ORDER WALKAROUND.** Derives every position in a scene where the layering doctrine can go wrong — pressed into a face band, in the NOTCH beside a band step, below a run's foot, around every Tier-3 prop — and tiles cropped frames into contact sheets. Add `lint` and it MEASURES instead: it recovers the body's visible silhouette at each spot (three captures, sprite hidden/shown/hidden, keeping pixels that changed in the middle frame AND agree in the outer two, which is what makes it immune to animated water and breathing windows) and asserts per family, exit 1 on any finding. It reads the props manifest for real art rects and sort keys, so legitimate walk-behind is not reported. Run it after ANY change to a map's bands, props or strata |
| `tools/pngcrop.py` | — | pulls named cells back out of a zwalk contact sheet at native scale, magnified, with the sheet's own labels as captions — for when a sheet shows an outlier and you need to judge eleven pixels of coat-tail. stdlib-only PNG read/write |

**`tools/party_probe.gd` must be re-run after anything that changes member movement
speed** — the brain hysteresis bands are tuned to 150px/s.

## `tools/shot.gd`

Eyeball any scene without launching the game. Args:

- `phase:<name>` — set a scene's phase router
- `roster:<id>[:<id>]` — stage the party
- `flag:<name>` — set a story flag
- `pos:<x>:<y>` — place the body
- **`beat:<n>`** — stage a whole beat from `scene/chapters.gd` in one arg. It can stand
  in for the scene path, and it is **the only way to shoot the beats needing
  `town_spawn` / `interior_spawn` / `library_phase`**, none of which has an arg of its
  own.

## Harness gotchas (each of these cost a real debugging session)

1. **`godot --headless --import` after every asset regen** — game runs never re-import,
   so a regenerated atlas renders scrambled. Also required after adding any script with
   a **new `class_name`**, or headless runs report "base class not found".

2. **An occluded macOS window stops drawing** — call `force_draw()` before
   `get_image()`.

3. **An occluded macOS window also runs UNCAPPED (~2000fps).** Frame budgets burn in
   real seconds while wall-clock cutscene timers don't advance any faster. Both
   `shot.gd` and the probes pin **`Engine.max_fps = 60`**. Keep that pin.

4. **Synthesized presses exist only in the polled Input state, never as InputEvents.**
   Any action you want testable must be **POLLED** (`Party` polls `swap_member` in
   `_process`).

4b. **NEVER MOVE A PARTY MEMBER BY ASSIGNING `velocity`.** It is a silent no-op: a
   `PartyMember` re-derives its velocity from an Intent EVERY physics frame
   (`_gather_intent()` reads the Input axes, `_process_move()` writes `velocity`), so
   an assignment made before `await physics_frame` is overwritten before
   `move_and_slide` ever sees it. `academy_probe` reported "moved 0 px" through a
   perfectly walkable gate, and `zwalk`'s NOTCH family spent its whole life seated in
   the middle of its cell instead of at the corner. Drive with **polled input**
   (`Input.action_press`), or with **geometry** — teleport a few px INTO the face and
   let depenetration seat the body flush, which is what zwalk does now.

5. **An input-polling coroutine on `process_frame` must LEVEL-detect**
   (`is_action_pressed` + a latch), never `is_action_just_pressed` — the frame signal can
   beat the same-frame press. This killed the crank mash.

6. **A `--script` probe must NOT name the `Player` class.** That drags `player.gd` into
   the tool's own compile, which happens BEFORE autoloads register, so its `Game.`
   references fail and poison the whole run. **Duck-type it instead.** The same rule is
   why `scene/theater.gd` never references autoload identifiers, and why
   `scene/chapters.gd` is deliberately `class_name`-free and autoload-free (so tools can
   `load()` it).

7. **A `_party_free` predicate must be gated on the scene you're waiting FOR**, or it
   passes trivially in the scene you just left.

8. **Dialog-invisible predicates are trivially true during an ENTRY_FADE wait** — poll
   real phase state, not the absence of a box.

9. **`_mash_until` advances dialog with ATTACK, and the press landing on the frame
   control returns is a REAL attack.** Fuji's tome swing lunges her out of the interact
   zone before the button fires. Probes teleport, settle, zero `velocity`, and re-park.

10. **A location zone is a 16×12 rect on its anchor**, so an `anchor + (0,40)` teleport
    lands OUTSIDE it. A probe that has to land on an area the SCENE builds in code must
    **read that geometry off the live scene**, never re-type the number — the dash goal
    in `town_thesis` moved from +40 to +24 in the Alembic rebuild, the probe kept its own
    copy of +40, and a body whose 12×8 collision box sits 10px below the rect never fires
    `body_entered`. Two checks went red and nothing in the log said why, because nothing
    had gone wrong: the beat was simply waiting for a body that was standing just south
    of the finish line. `town_thesis.DASH_GOAL_OFF` / `DASH_GOAL_SIZE` exist for exactly
    this, and reading a const off an instantiated scene is safe (gotcha 13 forbids
    `preload`ing the script, not touching the live node).

11. **A walk-gate must be driven by teleporting to the anchor**, like every other gate —
    a mash alone just makes Fuji swing her tome in place.

12. **Stage a beat by NAME out of `scene/chapters.gd`** so a probe's flag ladder can't
    drift from the dev menu's.

13. **NEVER `preload` a SCENE script in a probe — not even for its constants.** This is
    gotcha 6's nastier twin and the symptom points nowhere near the cause. `const OW :=
    preload("res://scene/overworld.gd")` compiles `overworld.gd` as part of the *tool's*
    compile, before autoloads register; its `Game.` / `Party.` references fail, the
    script is left broken, and `overworld.tscn` then instantiates its root as a
    **scriptless `Node2D`**. What you see is `Invalid access to property 'player' on a
    base object of type 'Node2D'` — from a scene that works perfectly in the game.
    Read its constants at RUNTIME instead:
    `(load("res://scene/overworld.gd") as GDScript).get_script_constant_map()`.

14. **A GDScript lambda captures by VALUE, so a `watch` closure that sets a plain `bool`
    is a check that SILENTLY PASSES FOREVER.** `var seen := false; var w := func():
    seen = true` assigns a copy. Two `motion_probe` checks — "was the party ever free
    mid-beat" and "did his slate come back out" — were dead this way and would never
    have failed. Use a one-element **Array** as the reference container. Any probe that
    asserts about frames *inside* a beat is exposed to this; grep your watches.

15. **`pos:x:y` HOLDS the body there for the whole `shot.gd` run**, re-teleporting every
    frame from frame 5. Leave a stale `pos:` on a shot of a different scene and you get a
    confident screenshot of the chibi standing in the open ocean, and will go looking for
    a travel bug that isn't there.

16. **A BigSlime needs a CLEAR cell, not merely a walkable one.** Its box is wider than a
    slime's, so on a terrace's last row — solid directly south — it depenetrates ~7px
    north and sits off its own anchor, failing "every enemy sits on its map anchor". When
    you move a spawn, check its NEIGHBOURS, not just its cell.

17. **Adding one NPC to a street breaks any probe that hardcodes the headcount.** Mayor
    Hollis made the Ebb-night street four people and `library_probe`'s `asked == 3` went
    red. Count from the scene (`folk.size()`), not from a literal.

## The dev chapter selector

**Press `0` ANYWHERE** — title, cutscene, mid-meadow — for a paused two-column menu of
all 39 story beats. Pick one and land in it with roster / phase / spawn / flags staged.

`scene/dev_menu.gd` (autoload `DevMenu`, third after `Game` / `Party`; overlay built in
code on CanvasLayer 100, `PROCESS_MODE_ALWAYS`, all-polled input, the whole thing behind
`OS.is_debug_build()`) reads the beat table in **`scene/chapters.gd`**.

**Adding a beat = one row in `chapters.gd`.**

Constraints the table encodes:

- **Roster is a SpriteFrames contract.** `sleep`/`wake`/`sigh` are kid-only;
  `sit`/`look_watch`/`bow_head`/`knapsack*`/`defeat_walk` are adult-only. The wrong body
  plays a beat as error spam and a frozen pose.
- **Never an EMPTY roster** — `party.gd` indexes `ids[0]`.
- **Never kid or student into the meadow** — no Brain node, no kit.
- Group headings clip to one column (~30 chars).
- **The toggle key is `0` only, NOT ESC.** Autoloads process before the current scene, so
  unpausing on ESC hands the same still-pressed ESC to `prologue_open`'s skip in that
  very frame.
- **`Game.reset_story()` clears flags and blanks the routers first**, because `set_flag`
  is one-way and a BACKWARDS jump would otherwise carry a later chapter's flags into an
  earlier scene.
