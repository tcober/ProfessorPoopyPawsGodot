# tools/ — probes and headless screenshots

**Load the `probes-and-shots` skill before running or writing anything here.** It carries
the probe inventory, `tools/shot.gd`'s args, and all the harness gotchas.

The standing rule: **verify the scene you changed, not the whole chapter.**
`prologue_probe.gd` takes minutes and is for handoff-chain changes and final checks only
— prefer the per-scene probe (`library_probe`, `recital_probe`, `fever_probe`,
`status_probe`, `rpg_probe`, `save_probe`, `defence_probe`, `party_probe`) or a `shot.gd` screenshot.

The four that cost the most debugging time:

1. **A `--script` probe must NOT name the `Player` class** — that drags `player.gd` into
   the tool's own compile, which happens BEFORE autoloads register, so its `Game.`
   references fail and poison the run. Duck-type it.
2. **Pin `Engine.max_fps = 60`.** An occluded macOS window runs uncapped (~2000fps), so
   frame budgets burn in real seconds while wall-clock cutscene timers don't advance any
   faster. An occluded window also stops drawing — `force_draw()` before `get_image()`.
3. **Synthesized presses exist only in the polled Input state, never as InputEvents** —
   any action you want testable must be polled.
4. **Stage a beat by NAME out of `scene/chapters.gd`** so a probe's flag ladder can't
   drift from the dev menu's. `shot.gd beat:<n>` does this in one arg, and is the only
   way to shoot beats needing `town_spawn` / `interior_spawn` / `library_phase`.

`godot --headless --import` is required after adding any script with a new `class_name`,
or headless runs report "base class not found".
