---
name: rpg-systems
description: The RPG layer — character sheets, the 5 stats and hand-authored growth tables, the 4 equip slots and item table, the satchel, the party menu, save/load, and the title screen. Also the DESIGNED-but-unbuilt vestige/Resonator ladder. Load BEFORE touching resources/character_sheet.gd, stat_block.gd, item.gd, items.gd, combat.gd, scene/party_menu.gd, scene/save_game.gd, scene/title.gd, or adding any field to the Game autoload.
---

# RPG systems

Built 2026-07-28. Full design: **docs/DESIGN.md → "RPG Systems"** (both ladders,
dispositions, the Return, what spells are allowed to be, build order).

## Where the files are

| File | What |
| --- | --- |
| `resources/character_sheet.gd` | level / EXP / 5 stats / 4 gear slots |
| `resources/stat_block.gd` | the growth TABLES + the EXP table |
| `resources/item.gd` | the item type |
| `resources/items.gd` | the item table and its **ONLY** factory |
| `resources/combat.gd` | damage math |
| `scene/party_menu.gd` | the three-pane menu |
| `scene/save_game.gd` | JSON save/load |
| `scene/title.gd` / `title.tscn` | **the boot scene** |

**Nothing calls `Item.new()` outside `resources/items.gd`.** Go through the factory.

## The five stats

**VIT · MIG · FOC · GRD · SPD.**

- Growth is a **hand-authored 20-row TABLE per character — never a curve.** Basil's
  MIG/FOC lead, Fuji's VIT/GRD lead, and **they must never converge.**
- **MIG and GRD are applied at exactly one place**, `HurtboxComponent.take_hit` — see
  the **combat-kits** skill for why, and for the burn-tick exception.
- **FOC is present but inert** until the magic layer exists.
- **SPD growth is ZERO at every level for both characters**, and only one relic grants
  any (`StatBlock.SPD_CLAMP` = +20% max). The AI brains' hysteresis bands are tuned to
  150px/s — **anything that moves member speed must re-run `tools/party_probe.gd`.** See
  the **party-ai** skill.

## Gear — four slots

**WEAPON / HEAD (hat) / BODY (shirt) / RELIC (charm).** This is an FFVI-shaped revision
of DESIGN.md's old "one socket is the whole equipment layer" rule. The VESTIGE socket is
a separate **5th** slot, still unbuilt.

**A weapon NEVER changes a KIT.** Basil shoots and Fuji swings a book because of who
they are; a weapon grants stats and a name. Otherwise combat branching ends up behind an
inventory screen.

## State lives on `Game`

`sheets`, `inventory`, `fuji_tome` — for the same reason the gun loadout does:
**`Party.spawn()` rebuilds every body at every door.** `Game.reset_story()` clears all
of it.

## The menu

**`scene/party_menu.gd`** is the **THIRD** `get_tree().paused` modal — it **must be in
`Overlay.MODALS`**. Opened with the `menu` action (I / gamepad START). Three panes:

1. roster
2. stats
3. gear + satchel + **SAVE**

The other two paused modals are `DevMenu` and `MixMenu`; modals refuse to open on top of
each other, so closing one can't unpause the tree under another.

## Save/load

**`scene/save_game.gd`** writes JSON to `user://save_1.json`.

> **A save is exactly what `reset_story()` clears, plus the roster and the current
> scene.**

Keeping that correspondence is the whole discipline — it is what stops a new `Game`
field from being silently lost. **Add a field to `Game`? Add it to `reset_story()` and
to the save in the same commit.**

A version-mismatched or unparseable save is **REFUSED whole, never half-applied.**

## The title screen

**`scene/title.tscn` is the boot scene.** NEW GAME / CONTINUE / QUIT, with **CONTINUE
first and pre-selected when a save exists** — a resting cursor on NEW GAME is how saves
get lost. Authored fresh per the build-fresh doctrine, with a code-drawn backdrop.

## Probes

- `tools/rpg_probe.gd` — 81 checks
- `tools/save_probe.gd` — 31 checks
- `tools/defence_probe.gd` — 30 checks, the kit→battle chain

## Ladder 2 — vestiges (DESIGNED, NOT BUILT)

Gated to Act 2's first obelisk. FFVI-magicite-shaped: named crystallized fragments of
the drained magic, read through Basil's **RESONATOR**, one socket per character
(Basil gets a locket, Fuji gets the book she chose in Act 1 beat 3), teaching spells
permanently at a per-vestige rate — so **who learns what is the player's choice.**

Two rules that constrain code before it is written:

- **Spells may never be recolored bolts** — compounds own projectiles. Only RESTORE /
  WARD / CONTROL (new status axes) / FIELD.
- **Every Remnant yields its vestige by EVERY path** — talked down or beaten, willing or
  refusing, no exceptions. Five vestiges gate the ending, so a missable one is an
  unwinnable save.

Build order: levels (**done**) → KO + FOCUS → vestiges → the Return.

Everything else about the vestige ladder — the Old Ones, dispositions, the Regent, the
Return, the funeral ending — is **story canon and lives in docs/DESIGN.md**, not here.
