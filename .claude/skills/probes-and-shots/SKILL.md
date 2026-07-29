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
| `tools/muzzle_probe.gd` | 30 | a projectile is never born inside a wall — both axes |
| `tools/party_probe.gd` | — | brain moods, no in-view pops, settle distances |
| `tools/overlay_probe.gd` | — | the paused-modal stack |
| `tools/status_shot.gd` | — | poses the status tells and the mixing bench for eyeballing |

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
    lands OUTSIDE it. (That offset belongs to `town_thesis`'s separate dash GOAL area.)

11. **A walk-gate must be driven by teleporting to the anchor**, like every other gate —
    a mash alone just makes Fuji swing her tome in place.

12. **Stage a beat by NAME out of `scene/chapters.gd`** so a probe's flag ladder can't
    drift from the dev menu's.

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
