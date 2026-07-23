class_name BigSlime
extends Slime

## The heavy. Same gel, more of it: a bruise-violet slime half again the size
## of the common green one, and the reason the sleep mechanic is a BUILDUP
## rather than a flag — its StatusComponent raises drowse_threshold, so it
## simply takes more darts to put under. Slower, tougher, hits harder.
##
## Deliberately `extends Slime` and nothing more: meadow.gd's `child is Slime`
## checks, `_track_slime`, the death-respawn wiring and every party brain's
## "enemies" group targeting keep working untouched. All the difference lives
## in big_slime.tscn's exports — the tuning is data, not a second AI.
##
## Everything overridable is already an @export on Slime (speed, detect_range,
## knockback_speed/friction) or on its composed components (max_health,
## drowse_threshold, hitbox damage), so this script exists to name the type
## for `is BigSlime` checks and to carry the doc.
