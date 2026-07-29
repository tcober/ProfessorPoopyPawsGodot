---
name: combat-kits
description: The combat layer — hitbox/hurtbox/health components, Basil's laser and the COMPOUND ammo/mixing system, Fuji's tome and sleep darts, status ailments (drowse/chill/burn), the ×4 damage rescale, and where MIG/GRD are applied. Load BEFORE touching anything in components/, entities/player/, entities/fuji/, entities/enemies/, entities/projectiles/, resources/compound.gd, resources/alchemy.gd, or scene/mix_menu.gd — and whenever damage, ammo, a status effect, or an enemy's HP is wrong.
---

# Combat kits

Combat is `Area2D` Hitbox vs `Area2D` Hurtbox → `HealthComponent`. `LaserBolt` is the
projectile. Kits live in the `PartyMember` subclasses behind `_process_kit`,
`_on_attack_intent` and `_on_secondary_intent` — see the **party-ai** skill for the
body/brain/Intent machinery underneath.

## The one chokepoint

Every hit flows through **`HurtboxComponent.take_hit(damage, source, effect := NO_EFFECT)`**.

- `effect` is a small Dictionary (`{"drowse":1}` / `{"chill":1}` / `{"burn":4}`). The
  const default avoids allocating per hit.
- **MIG and GRD are applied at exactly ONE place — `take_hit`.** That is deliberate: it
  covers enemy contact damage too. Projectiles carry `shooter`, so a dart inherits its
  firer's MIG.
- **The burn tick is the one exception** — it goes straight to `HealthComponent` on
  purpose, because the hurtbox's `invincible_time` would eat most of the ticks. It
  therefore ignores GRD. Documented, not an oversight.

## The ×4 rescale (2026-07-28)

Every party→enemy number and every enemy HP was multiplied by 4 — laser/tome 2→8, dart
1→4, burn tick 1→4, slime 4→16, big slime 10→40 — so **kill counts are unchanged** but
one point of MIG has somewhere to go.

**Enemy→party damage was NOT rescaled.** Party HP is drawn as hearts and must stay
legible in halves. Do not "fix" this asymmetry.

## COMPOUNDS — Basil's ammo types

A beaker is a colour-coded ammo TYPE (`resources/compound.gd`):

| Compound | Colour | Behaviour |
| --- | --- | --- |
| `base` | green | the original laser, dmg 2 (×4 = 8), ×6 |
| `frost` | blue | chill → brief freeze |
| `flame` | red | short-range sprayer + burn DoT |
| `plasma` | purple | dmg 4 (×4 = 16), PIERCES, ×3 |

**`M` opens the mixing bench** (`scene/mix_menu.gd`) to fuse two spares into one, under
three rules in `resources/alchemy.gd`:

1. same + same **CONCENTRATES**
2. green + anything **DILUTES** — green is the inert solvent, which is what keeps the
   common drop useful all game
3. red + blue = **purple**

Everything else is **refused with a reason, never silently eaten.**

**ONE bolt scene serves all four.** `bolt.apply_compound(c)` sets
damage/speed/lifetime/effect/pierce/tint the same way `direction` and `shooter` already
are. Do not fork the projectile.

**The loadout (`loaded`, `spares`, `ammo_left`) lives on `Game`**, because
`Party.spawn()` rebuilds every body at each door. `Game.reset_story()` blanks it, so a
backwards chapter jump can't carry plasma into a scene that predates the gun.

HUD tints the ammo pips to the loaded kind and each spare icon to its own — no new row,
no new art.

## STATUS AILMENTS

`components/status_component.gd`, composed onto enemies. Payload rides `take_hit`'s
`effect` dict (above).

**Fuji's darts are SLEEP darts, and sleep is a BUILDUP, not a flag.** Each dart adds
drowse; crossing `drowse_threshold` drops the target (still, and its contact hitbox
OFF). A sleeping target takes NORMAL damage and does **not** wake on being hit. A bigger
enemy just raises the threshold — hence `BigSlime` (`entities/enemies/big_slime.*`,
bruise-violet, 10 HP → 40, threshold 5, 30% of meadow respawns).

**Distinctness rule:** sleep is slow / long / total. Freeze is instant / partial /
short. Burn disables nothing. Keep them from converging.

### Three gotchas, all of which cost real bugs

1. **Buildup needs a GRACE WINDOW before decay resumes**, or the threshold lies — decay
   nibbles between the darts of a burst, and a "2 dart" enemy took 3.
2. **Disabling contact damage toggles the Hitbox's collision SHAPE, never
   `monitoring`.** Re-enabling `monitoring` does not re-scan an overlap that never
   ended, so an enemy woken while touching the player stays harmless forever.
3. **Burn ticks go straight to `HealthComponent`, never back through `take_hit`** — the
   hurtbox's `invincible_time` would eat most of them.

## Basil's kit (`entities/player/`)

Instant fire on the trigger, damage 2 (→8), hard recoil skid (~30px). Beakers are the
gun's magazines: pickups pocket as spares, reload (R, or a dry trigger) pours one in.

**A weapon NEVER changes a KIT.** Basil shoots and Fuji swings a book because of who
they are; a weapon grants stats and a name. Otherwise combat branching ends up behind an
inventory screen.

### The muzzle is PLACED, not offset — `PartyMember.place_muzzle` (2026-07-29)

A projectile is born `offset` px in FRONT of the body's ORIGIN, but the body's collision
box hugs its FEET (12×8 at +6, box top = origin+2). Near a wall that mismatch puts the
shot inside rock in **two independent ways**, and they need different answers:

1. **ALONG the facing.** The shot's collider reaches half its own length past the muzzle
   — 25px for the bolt (16 + 18/2) — while the body stops ~10px short of a north wall.
   Fired at the rock, the bolt is born well inside it and dies on its first physics step
   without moving. → ray the wall layer over the muzzle's reach, spawn at the last point
   that fits.
2. **ACROSS the facing.** Pressed north, the box top IS the wall's edge, so the ORIGIN
   sits **2px inside the solid cell** — and a bolt fired EAST is centred on that origin
   with its 6px-tall collider straddling the boundary. It dies having never left the
   barrel. The dead band is only ~5px of clearance, but that is exactly where you stand
   when you walk up to a wall. Pulling back along the facing does nothing here: the
   overlap is sideways. → test the shot's real shape at its real spawn transform and
   nudge it perpendicular (≤ `MUZZLE_NUDGE` = 6px) until it is clear.

**(2) escaped the first fix and its probe**, because the probe only ever fired north.
When a fix has an axis, test every axis.

Firing INTO a wall you are flush against still produces no shot — no free pixel exists,
in any direction. That is geometry, and `muzzle_probe` asserts it as a known limit.

Beware measuring this with "does the projectile survive N frames": `body_entered` is
flushed AFTER `_physics_process`, so a projectile born in rock always gets one step
either way. The discriminating assertion is an `intersect_shape` of the projectile's own
collider at its own spawn transform.

## Fuji's kit (`entities/fuji/`)

Tortoiseshell Lanternwood librarian. **Tome swing** attack — overhead slam, `BookHitbox`
shape-toggled through the strike/impact window, damage 2 (→8), forward lunge. **Blow-pipe
darts** (`dart` / L), unlimited, damage 1 (→4), leaving on the puff frame at the **19px
pipe-tip contract**.

### Fuji's kit is FLAG-GATED

She is a librarian and does not start armed — her tome and blow-pipe are MADE in Act 1
beat 3. Gated in:

- `fuji.gd::_start_book` / `_start_dart` (both the keyboard and AI paths funnel through
  those two), **and**
- **`FujiBrain._combat`** — gating only the body makes a disarmed follower walk into a
  slime and stand there taking contact damage.

**Read the flag PER CALL, never cached in `_ready`.**

The real flag names (set in `scene/library.gd`'s `kit` phase, **not** the design-doc
names): **`fuji_dose_found` · `fuji_darts_made` · `fuji_tome_taken` → `fuji_kit_made`**,
which is what `Chapters.KIT_ARMED` holds. `fuji.gd` reads `fuji_tome_taken` for the tome
and `fuji_darts_made` for the pipe.

**`Game.reset_story()` wipes flags, so EVERY beat and probe that expects to fight must
carry `Chapters.KIT_ARMED`.** That regression has to land in the same commit as any
change to the gate, or the meadow silently stops working.

## Enemies

Slimes explode in 2 book swings or 2 laser shots; a replacement respawns elsewhere in
the meadow. Live slimes are in the `enemies` group (left on death); brains target it.

Future: the Regent's machines are **drowse-IMMUNE** — the first enemies Fuji's sleep
setup can't solve, and the mechanical statement of the "never completable with either
system alone" thesis rule.

## Probes

- `tools/status_probe.gd` — 50 checks: statuses, mixing rules, the loadout surviving a
  scene change, `reset_story` clearing it.
- `tools/status_shot.gd` — poses the tells and the bench for eyeballing.
- `tools/defence_probe.gd` — 32 checks, the kit→battle chain (incl. the south gate
  refusing while the lanes are full, and opening once they are clear).
- `tools/muzzle_probe.gd` — 8 checks: a projectile is never born inside a wall. Run it
  after touching a muzzle offset, a projectile collision shape, or a body's box.

**PROBE GOTCHA:** a `--script` probe must NOT name the `Player` class. That drags
`player.gd` into the tool's own compile, which happens BEFORE autoloads register, so its
`Game.` references fail and poison the run. Duck-type it instead. See the
**probes-and-shots** skill.
