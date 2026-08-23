class_name Combat
extends Object

## Turns a raw hit into a stat-adjusted one. Pure statics, no instances.
##
## THIS RUNS AT EXACTLY ONE PLACE: `HurtboxComponent.take_hit`. That is already
## the single chokepoint every hit in the game flows through — Fuji's tome and
## Basil's bolts and a slime's contact damage all arrive there — so scaling here
## covers every attacker and every target at once, including kit that does not
## exist yet. Scaling at each weapon instead would mean three call sites, would
## miss enemy contact damage entirely (enemies share HitboxComponent with the
## party), and would have to be revisited for every new weapon.
##
## THE UNIT SPLIT, and it is the reason there are two different formulas below:
## party HP is in HALF-HEARTS and always will be, because it is drawn as hearts
## and one damage has to stay legible as half a heart. Enemy HP is invisible. So
## the two directions get different resolutions on purpose —
##   party -> enemy  scales MULTIPLICATIVELY off MIG, against enemy HP that was
##                   rescaled x4 so a single point of MIG has somewhere to go;
##   enemy -> party  is a coarse flat SUBTRACTION off GRD, floored at 1, so
##                   guard shaves half-hearts slowly and can never reach zero.
## An untouchable party is a dead loop, hence the floor.

## outgoing = base * (1 + MIG/12). At MIG 0 this is exactly `base`, so an
## unlevelled party plays precisely as it did before this system existed.
const MIG_DIV := 12.0
## incoming = base - GRD/8, integer divide. Eight points of guard for one
## half-heart is deliberately slow.
const GRD_DIV := 8


## `source` is whoever swung: a PartyMember for melee (HitboxComponent passes its
## owner), or a projectile for ranged — projectiles carry a `shooter`, which is
## why this walks one hop. `target` is the hurtbox's owner.
static func resolve(damage: int, source: Node, target: Node) -> int:
	var probe: Node = target if is_instance_valid(target) else source
	var sheets := _sheets(probe)
	if sheets.is_empty():
		return damage                            # no RPG layer live: pass through
	var out := damage
	var atk := _sheet_of(sheets, source)
	if atk != null and not atk.neutral:
		out = roundi(out * (1.0 + float(atk.stat("mig")) / MIG_DIV))
	var def := _sheet_of(sheets, target)
	if def != null and not def.neutral:
		out = maxi(1, out - int(def.stat("grd") / float(GRD_DIV)))
	return maxi(0, out)


## The member id behind a node: the body itself, or the body that fired it.
## Duck-typed rather than type-checked so this file never has to `preload`
## PartyMember or any projectile — a `class_name` reference here would drag those
## scripts into the compile of every `--script` tool that touches a hurtbox.
static func member_id(n: Node) -> StringName:
	if not is_instance_valid(n):
		return &""
	if n.get("member_id") != null:
		return n.get("member_id")
	var shooter = n.get("shooter")
	if shooter is Node:
		return member_id(shooter)
	return &""


static func _sheet_of(sheets: Dictionary, n: Node) -> CharacterSheet:
	var id := member_id(n)
	if id == &"":
		return null
	return sheets.get(id)


## Reach the Game autoload through the tree rather than by name. Under a
## `--script` tool the autoloads are not registered, so a bare `Game.` reference
## would throw on the first hit and poison the run; an empty dictionary here just
## means "no stats yet", which is exactly right in that context.
static func _sheets(n: Node) -> Dictionary:
	if not is_instance_valid(n) or n.get_tree() == null:
		return {}
	var g := n.get_tree().root.get_node_or_null(^"Game")
	if g == null:
		return {}
	var s = g.get("sheets")
	return s if s is Dictionary else {}
