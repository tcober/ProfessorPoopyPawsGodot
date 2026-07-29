---
name: party-ai
description: The 2-member party slice — the Party autoload and spawn contract, PartyMember/Intent, the AIBrain mood machine (FOLLOW/ENGAGE/RETURN) and its tuned thresholds, leader swap, the leash teleport, and the node groups every trigger gates on. Load BEFORE touching scene/party.gd, entities/party/*, basil_brain.gd, fuji_brain.gd, any follower behaviour, member movement speed, or anything that reads the player/party/enemies groups.
---

# Party and AI

An SoM-style 2-member slice (2026-07-10). Basil leads, Fuji runs as AI companion;
**Q / Tab swaps the lead**.

## The spawn contract

**No scene instances a player anymore.** The **`Party` autoload** (`scene/party.gd`,
registered after `Game`) `spawn()`s the roster into each zone's `World`, and scenes keep
the returned leader as `player`.

- `leader_id` persists across scenes. HP does not.
- `Party.set_roster()` takes a **typed `Array[StringName]`** — dynamic callers must pass
  a typed array.
- **Never an EMPTY roster** — `party.gd` indexes `ids[0]`.
- **`Party.spawn()` rebuilds every body at every door.** This is *the* reason anything
  that must survive a scene change lives on **`Game`**, not on the body: the gun
  loadout, the character sheets, the inventory, `fuji_tome`.

## Node groups (every trigger gates on these)

| Group | Contents | Used by |
| --- | --- | --- |
| `player` | **the current leader ONLY** | all door / exit / zone triggers |
| `party` | all members | slimes re-pick the nearest every frame |
| `enemies` | live slimes | brains target it; members are left in it on death |

Changing what's in `player` breaks every travel trigger in the game.

## Bodies

Members extend **`PartyMember`** (`entities/party/party_member.gd`, which extends
`DirectionalBody2D`): shared move / hop / knockback / hurt / can't-die.

Each is driven per-frame by an **`Intent`** (move + face, plus attack / secondary / jump
edges), filled from `Input` when leading, or from the scene's `Brain` node when
following. Kits hang off `_process_kit` / `_on_attack_intent` / `_on_secondary_intent` —
see the **combat-kits** skill.

Leader swap: `swap_member` — camera `make_current` + `reset_smoothing`, HUD row dim,
modulate blink. **Brains reset on leader swap.**

HUD: one heart row per member (follower dimmed 55%) + Basil's ammo pips/mags wherever he
sits in the party.

## The brain — a three-MOOD machine

**`AIBrain`** (`entities/party/ai_brain.gd`). **Every boundary is a two-threshold band,
because lone edges read as twitching.**

- **FOLLOW** — stop/resume hysteresis **34 / 44px**, sprint past **56px**.
- **ENGAGE** — acquire the nearest enemy ≤**70px** while ≤**96px** of the leader, then
  **LATCH** it and hold to **140px**. (Basil's ~30px recoil skid crosses any single line
  every shot — that latch is why.)
- **RETURN** — the leash breaks past **128px** → run home to **48px** IGNORING enemies
  before re-engaging.

The cooldown decays in the brain's own `_physics_process`; `think()` pauses during
kit/hurt states.

### The catch-up teleport

Fires only **>130px AND OFF-SCREEN** (live camera's `get_screen_center_position()` +
`MapData.view_size()`), and lands a step behind the leader **only after a `test_move`
sweep proves the step walkable** — otherwise on the leader.

**The >130px threshold must stay ≤ min view half-extent + margin**, or a stuck follower
sits invisible and never comes home.

### Per-character brains

- `basil_brain.gd` — sidles onto a cardinal (4-way facing), fires in **[36, 110]px**,
  reloads when dry, restocks off beaker pickups.
- `fuji_brain.gd` — closes to swing range and slams. **`_combat` also carries the kit
  flag gate** (see **combat-kits**) — gating only the body makes a disarmed follower
  stand in a slime taking contact damage.

## SPD is frozen on purpose

**SPD growth is ZERO at every level for both characters**, and only one relic grants any
(`StatBlock.SPD_CLAMP` = +20% max).

**The hysteresis bands above are tuned to 150px/s.** Anything that moves member speed —
a stat, a relic, a status effect, a tweak to `PartyMember` — must re-run
`tools/party_probe.gd`.

## The overworld

The party travels as ONE chibi — the leader's. Frames swap on entry.
`entities/player/overworld_player.gd` is travel-only: 8-way move, 4-way facing, 90px/s,
no gun / hop / health.

## Probe

**`tools/party_probe.gd`** asserts all of this headlessly-ish (windowed): mood-transition
counts, no in-view pops, settle distances. **Run it after touching brain or member
code**, and always after anything that changes movement speed.
