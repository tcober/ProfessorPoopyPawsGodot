# entities/ — bodies, kits, enemies, projectiles, NPCs

Load the skill that matches what you're touching:

- `player/`, `fuji/`, `enemies/`, `projectiles/`, `pickups/` → **`combat-kits`**
- `party/` (`party_member.gd`, `ai_brain.gd`, the per-character brains) → **`party-ai`**
- `npcs/` → **`story-scenes`**

The rules that bite here:

1. **Every hit flows through `HurtboxComponent.take_hit(damage, source, effect)`** — the
   one chokepoint, and the only place MIG and GRD are applied. The burn tick is the
   deliberate exception (it goes straight to `HealthComponent`, because i-frames would
   eat it) and therefore ignores GRD.
2. **A weapon never changes a KIT.** Basil shoots and Fuji swings a book because of who
   they are. Gear grants stats and a name.
3. **Fuji's kit is flag-gated** — in `fuji.gd::_start_book` / `_start_dart` **and** in
   `FujiBrain._combat`. Gating only the body makes a disarmed follower stand in a slime
   taking contact damage. Read the flag **per call**, never cached in `_ready`.
4. **Party numbers are ×4-rescaled; enemy→party damage is NOT.** Party HP is drawn as
   hearts and must stay legible in halves.
5. **SPD is frozen on purpose.** The brain hysteresis bands are tuned to 150px/s —
   anything that moves member speed must re-run `tools/party_probe.gd`.
6. **Disabling contact damage toggles the Hitbox's collision SHAPE, never
   `monitoring`** — re-enabling monitoring never re-scans an overlap that didn't end.
7. **A projectile is PLACED, never offset** — `PartyMember.place_muzzle`. The muzzle
   sits in front of the origin but the collision box sits at the feet, so near a wall
   the raw offset spawns the shot inside rock both along AND across the facing.
8. Hand-authored `.tscn` node exports need
   `node_paths=PackedStringArray("health_component")` on the node header, or the
   reference silently loads null.
